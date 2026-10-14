"""Shared model helpers used by training, evaluation and deployment."""
import torch
from torch import nn
from torchvision import models, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

ARCHITECTURES = {
    "resnet18": models.resnet18,
    "resnet34": models.resnet34,
    "resnet50": models.resnet50,
    "resnet101": models.resnet101,
    "resnet152": models.resnet152,
}


def build_transform(image_size):
    """Resize to a square input and normalise with ImageNet statistics."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def build_model(arch, num_classes, pretrained=True):
    """ResNet backbone with a new fully connected layer sized to the dataset."""
    if arch not in ARCHITECTURES:
        raise ValueError(f"Unknown architecture '{arch}'. Choose from {sorted(ARCHITECTURES)}.")
    model = ARCHITECTURES[arch](weights="DEFAULT" if pretrained else None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def load_model(checkpoint_path, device="cpu"):
    """Load a checkpoint written by train.py.

    Returns (model, class_names, transform), with the model in eval mode.
    The class names travel with the checkpoint, so deployment code never has
    to hard-code them or the size of the final layer.
    """
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_names = checkpoint["class_names"]
    model = build_model(checkpoint["arch"], len(class_names), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device).eval()
    return model, class_names, build_transform(checkpoint["image_size"])


@torch.no_grad()
def predict(model, transform, images, class_names, device="cpu"):
    """Classify a list of PIL images. Returns [(class_name, confidence), ...]."""
    batch = torch.stack([transform(img.convert("RGB")) for img in images]).to(device)
    probs = torch.softmax(model(batch), dim=1)
    conf, idx = probs.max(dim=1)
    return [(class_names[i], c) for i, c in zip(idx.tolist(), conf.tolist())]


def condition(class_name):
    """'Obj5_bad' -> 'bad'. Also works for binary models with classes 'good' / 'bad'."""
    return class_name.rsplit("_", 1)[-1]


def part_type(class_name):
    """'Obj5_bad' -> 'Obj5', or None for binary 'good' / 'bad' classes."""
    return class_name.rsplit("_", 1)[0] if "_" in class_name else None
