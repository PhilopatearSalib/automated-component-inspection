import torch
import torchvision
from torchvision import transforms, datasets
from torch import nn, optim
import numpy as np
import random

# Set the seed value
seed_value = 1234

torch.manual_seed(seed_value)
np.random.seed(seed_value)
random.seed(seed_value)

if torch.cuda.is_available():
    torch.cuda.manual_seed(seed_value)
    torch.cuda.manual_seed_all(seed_value)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Check if a GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')

# Define the image size
image_size = 512

# Define the data transformations
data_transforms = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load the training and validation data
train_data = datasets.ImageFolder(root='train', transform=data_transforms)
val_data = datasets.ImageFolder(root='val', transform=data_transforms)

train_loader = torch.utils.data.DataLoader(train_data, batch_size=1, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_data, batch_size=16)

# Load the pre-trained ResNet-101 model
model = torchvision.models.resnet101(weights='DEFAULT')
model.avgpool = torch.nn.AdaptiveAvgPool2d((1, 1))
# Move the model to the GPU device
model = model.to(device)

# Freeze all layers except the last one
for param in model.parameters():
    param.requires_grad = True

# Replace the last layer with a binary classifier
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 16)

# Move the optimizer to the GPU device
optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)

# Define the loss function
criterion = nn.CrossEntropyLoss()

# Train the model
num_epochs = 500
patience = 10  # Number of epochs to wait for improvement before stopping
best_loss = np.inf  # Best loss value so far
epochs_no_improve = 0  # Number of epochs with no improvement

for epoch in range(num_epochs):
    running_loss = 0.0
    for inputs, labels in train_loader:
        # Move the inputs and labels to the GPU device
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        model.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Evaluate the model on the validation data
    correct = 0
    total = 0
    val_loss = 0.0
    with torch.no_grad():
        for inputs, labels in val_loader:
            # Move the inputs and labels to the GPU device
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    # Compute the average losses
    running_loss /= len(train_loader)
    val_loss /= len(val_loader)

    # Print the losses and accuracy
    print(f'Epoch: {epoch+1}/{num_epochs}, Training Loss: {running_loss:.3f}, Validation Loss: {val_loss:.3f}, Accuracy: {correct/total:.3f}')

    # Check for improvement
    if val_loss < best_loss:
        best_loss = val_loss
        epochs_no_improve = 0
    else:
        epochs_no_improve += 1
        if epochs_no_improve == patience:
            print('Early stopping!')
            break

# Save the trained model to a file named 'model.pth'
torch.save(model.state_dict(), 'TrainedModel.pth')

