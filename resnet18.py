import torch
import torchvision
from torchvision import transforms, datasets
from torch import nn, optim

# Check if a GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# Define the image size
image_size = 256

# Define the data transformations
data_transforms = transforms.Compose([
    transforms.Resize(image_size),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load the training and validation data
train_data = datasets.ImageFolder(root='Dataset/train', transform=data_transforms)
val_data = datasets.ImageFolder(root='Dataset/val', transform=data_transforms)

train_loader = torch.utils.data.DataLoader(train_data, batch_size=4, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_data, batch_size=4)

# Load the pre-trained ResNet-18 model
model = torchvision.models.resnet18(weights=True)

# Move the model to the GPU device
model = model.to(device)

# Freeze all layers except the last one
for param in model.parameters():
    param.requires_grad = False

# Replace the last layer with a binary classifier
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)

# Move the optimizer to the GPU device
optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)

# Define the loss function
criterion = nn.CrossEntropyLoss()

# Train the model
num_epochs = 50

for epoch in range(num_epochs):
    running_loss = 0.0
    for inputs, labels in train_loader:
        # Move the inputs and labels to the GPU device
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Evaluate the model on the validation data
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            # Move the inputs and labels to the GPU device
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f'Epoch: {epoch+1}/{num_epochs}, Loss: {running_loss/len(train_loader)}, Accuracy: {correct/total}')


# Save the trained model to a file named 'model.pth'
torch.save(model.state_dict(), 'model.pth')
