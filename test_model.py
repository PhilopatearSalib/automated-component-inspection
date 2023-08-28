import torch
import torchvision
from torchvision import transforms, datasets
from torch import nn, optim

# Define the image size and data transformations
image_size = 256
data_transforms = transforms.Compose([
    transforms.Resize(image_size),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load the test data and create a data loader
test_data = datasets.ImageFolder(root='test', transform=data_transforms)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=4)

# Load the pre-trained ResNet-18 model and replace the last layer with a binary classifier
model = torchvision.models.resnet18(weights='DEFAULT')
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)

# Load the trained model from the file named 'model.pth'
model.load_state_dict(torch.load('model.pth'))

# Evaluate the trained model on the test data
correct = 0
total = 0

with torch.no_grad():
    for inputs, labels in test_loader:
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        for i in range(len(predicted)):
            print(f'Image: {test_data.imgs[total-len(predicted)+i][0]}, Predicted: {"good" if predicted[i] == 1 else "bad"}')

print(f'Accuracy on test data: {correct/total}')