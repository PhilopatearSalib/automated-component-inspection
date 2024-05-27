import os
from PIL import Image
import torch
import torchvision
from torchvision import transforms
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import RPi.GPIO as GPIO
from time import sleep

# Define the image size and data transformations
image_size = 512
data_transforms = transforms.Compose([
    transforms.CenterCrop(2000),
    transforms.Resize(1024),
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Use Broadcom SOC channel numbering 
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin where the LEDs are connected
RedLED_Pin = 17
GreenLED_Pin = 22
YellowLED_Pin = 27

# Set up the GPIO pins as an output
GPIO.setup(RedLED_Pin, GPIO.OUT)
GPIO.setup(GreenLED_Pin, GPIO.OUT)
GPIO.setup(YellowLED_Pin, GPIO.OUT)


# Load the pre-trained ResNet-101 model and replace the last layer with a binary classifier
model = torchvision.models.resnet101()
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 16)

# Load the trained model from the file named 'model.pth'
model.load_state_dict(torch.load('TrainedModel.pth',map_location=torch.device('cpu')))


# Get a list of all image files in the test directory
image_dir = 'Realtime'
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')]

# Define class names
class_names = ["Obj10_bad", "Obj10_good", "Obj1_bad", "Obj1_good", "Obj2_bad", "Obj2_good", "Obj4_bad", "Obj4_good", "Obj5_bad", "Obj5_good", "Obj6_bad", "Obj6_good", "Obj7_bad", "Obj7_good", "Obj9_bad", "Obj9_good"]

defective = False 
inspection_needed = False


# Define a custom dataset
class CustomDataset(Dataset):
    def __init__(self, image_files, transform=None):
        self.image_files = image_files
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_file = self.image_files[idx]
        image = Image.open(image_file)
        if self.transform:
            image = self.transform(image)
        return image, image_file

# Create a DataLoader
dataset = CustomDataset(image_files, transform=data_transforms)
dataloader = DataLoader(dataset, batch_size=4, shuffle=False)

# Set the model to evaluation mode
model.eval()

# Evaluate the trained model on the test data
with torch.no_grad():
    for images, image_files in dataloader:
        # Make sure we're using a GPU if it's available
        if torch.cuda.is_available():
            images = images.cuda()
            model = model.cuda()
        # Get the model's predictions
        outputs = model(images)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        _, predicted = torch.max(outputs.data, 1)
        # Print the prediction
        for i in range(len(predicted)):
            prediction = class_names[predicted[i].item()]
            if "good" in prediction:
                print(f'File: {image_files[i]}, Prediction: {prediction} (good) ({probabilities[i][predicted[i].item()].item():.2%})')
            else:
                print(f'File: {image_files[i]}, Prediction: {prediction} (bad) ({probabilities[i][predicted[i].item()].item():.2%})')
                defective = True
            # Check if the probability is less than 75%
            if probabilities[i][predicted[i].item()].item() < 0.75:
                inspection_needed = True

if defective:
    print('Defective')
	# Set the GPIO pin to output mode
    GPIO.output(RedLED_Pin, True)
    # Keep the pin on for 5 seconds
    sleep(5)
    # Set the GPIO pin false    
    GPIO.output(RedLED_Pin, False)
	
else:
    print('Normal')
    # Set the GPIO pin true
    GPIO.output(GreenLED_Pin, True)
    # Keep the pin on for 5 seconds
    sleep(5)
	# Set the GPIO pin false
    GPIO.output(GreenLED_Pin, False)

if inspection_needed:
    print('Further Inspection Needed.')
    # Set the GPIO pin true
    GPIO.output(YellowLED_Pin, True)
	# Keep the pin on for 5 seconds
    sleep(5)
    # Set the GPIO pin false
    GPIO.output(YellowLED_Pin, False)

# Clean up GPIO to ensure we reset the pin's state
GPIO.cleanup()
