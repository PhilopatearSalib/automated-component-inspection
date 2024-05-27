import os
import torch
import torchvision
from torchvision import transforms, datasets
from torch import nn, optim
import torch.nn.functional as F

# Define the image size and data transformations
image_size = 512
data_transforms = transforms.Compose([
    transforms.CenterCrop(2000),
    transforms.Resize(1024),
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load the test data and create a data loader
#test_data = datasets.ImageFolder(root='Realtime_multi', transform=data_transforms)
test_data = datasets.ImageFolder(root='Extra_Realtime_multi', transform=data_transforms)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=4)

# Create a mapping from class indices to class names
idx_to_class = {v: k for k, v in test_data.class_to_idx.items()} 

# Load the pre-trained ResNet-101 model and replace the last layer with a binary classifier
model = torchvision.models.resnet101()
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 18)

# Load the trained model from the file named 'model.pth'
model.load_state_dict(torch.load('model_Aug_after3_norm_multi.pth'))

# Set the model to evaluation mode
model.eval()

# Evaluate the trained model on the test data
correct = 0
total = 0
excluded = 0

with torch.no_grad():
    for i, (inputs, labels) in enumerate(test_loader):
        outputs = model(inputs)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs.data, 1)
        
        for j in range(len(predicted)):
            file_name = test_loader.dataset.samples[i*len(predicted) + j][0]  # Get the file name
            if probabilities[j][predicted[j]].item() > 0.75:
                total += 1
                if predicted[j] == labels[j]:
                    print(f'Correct: {file_name}, Prediction: {idx_to_class[predicted[j].item()]} ({probabilities[j][predicted[j]].item():.2%}), Ground Truth: {idx_to_class[labels[j].item()]}')
                    correct += 1
                else:
                    print(f'Wrong: {file_name}, Prediction: {idx_to_class[predicted[j].item()]} ({probabilities[j][predicted[j]].item():.2%}), Ground Truth: {idx_to_class[labels[j].item()]}')
            else:
                excluded += 1
                print(f'Excluded: {file_name}, Prediction: {idx_to_class[predicted[j].item()]} ({probabilities[j][predicted[j]].item():.2%}), Ground Truth: {idx_to_class[labels[j].item()]}')

print(f'Accuracy on test data (for predictions with >75% confidence): {correct/total:.2%}') 
print(f'Percentage of excluded objects: {excluded/(total+excluded):.2%}')
