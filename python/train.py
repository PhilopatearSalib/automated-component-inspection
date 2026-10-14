"""Fine-tune a ResNet classifier on the inspection dataset.

Dataset layout (torchvision ImageFolder):
    <data>/train/<class>/*.jpg
    <data>/val/<class>/*.jpg

Class folders follow the Obj<N>_good / Obj<N>_bad convention, so the model
learns which part it is looking at and whether it is defective. The number of
output classes is read from the folders: adding a new part only means adding
its two folders and retraining.

Example:
    python python/train.py --data data --arch resnet101 --image-size 512
"""
import argparse
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets

from model_utils import ARCHITECTURES, build_model, build_transform


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data", help="folder containing train/ and val/")
    p.add_argument("--arch", default="resnet101", choices=sorted(ARCHITECTURES))
    p.add_argument("--image-size", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=4,
                   help="4 by default, matching the four faces captured per part")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--momentum", type=float, default=0.9)
    p.add_argument("--epochs", type=int, default=500)
    p.add_argument("--patience", type=int, default=10,
                   help="epochs without validation-loss improvement before stopping")
    p.add_argument("--freeze-backbone", action="store_true",
                   help="train only the final layer (the original ResNet-18 baseline)")
    p.add_argument("--freeze-bn", action="store_true",
                   help="keep BatchNorm statistics fixed; use when GPU memory forces a small batch")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--output", default="checkpoints/model.pth")
    return p.parse_args()


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def set_train_mode(model, freeze_bn):
    """model.train() also switches BatchNorm back on, so re-freeze it if asked."""
    model.train()
    if freeze_bn:
        for m in model.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()


def run_epoch(model, loader, criterion, device, optimizer=None):
    """One pass over the loader. Trains when an optimizer is given, otherwise evaluates."""
    training = optimizer is not None
    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def main():
    args = parse_args()
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    transform = build_transform(args.image_size)
    train_data = datasets.ImageFolder(Path(args.data) / "train", transform=transform)
    val_data = datasets.ImageFolder(Path(args.data) / "val", transform=transform)
    if train_data.classes != val_data.classes:
        raise ValueError("train/ and val/ must contain the same class folders")
    class_names = train_data.classes
    print(f"{len(class_names)} classes | {len(train_data)} train / {len(val_data)} val images")

    generator = torch.Generator().manual_seed(args.seed)
    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, generator=generator)
    val_loader = DataLoader(val_data, batch_size=args.batch_size, num_workers=args.workers)

    model = build_model(args.arch, len(class_names))
    if args.freeze_backbone:
        for name, param in model.named_parameters():
            param.requires_grad = name.startswith("fc.")
    if args.freeze_bn:
        for m in model.modules():
            if isinstance(m, nn.BatchNorm2d):
                for param in m.parameters():
                    param.requires_grad = False
    model.to(device)  # after replacing fc, so the new layer is on the device too

    optimizer = optim.SGD([p for p in model.parameters() if p.requires_grad],
                          lr=args.lr, momentum=args.momentum)
    criterion = nn.CrossEntropyLoss()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    best_loss, epochs_no_improve = float("inf"), 0

    for epoch in range(1, args.epochs + 1):
        set_train_mode(model, args.freeze_bn)
        train_loss, train_acc = run_epoch(model, train_loader, criterion, device, optimizer)
        model.eval()
        val_loss, val_acc = run_epoch(model, val_loader, criterion, device)
        print(f"Epoch {epoch}/{args.epochs} | train loss {train_loss:.3f} acc {train_acc:.3f} "
              f"| val loss {val_loss:.3f} acc {val_acc:.3f}")

        if val_loss < best_loss:
            best_loss, epochs_no_improve = val_loss, 0
            torch.save({
                "arch": args.arch,
                "image_size": args.image_size,
                "class_names": class_names,
                "state_dict": model.state_dict(),
                "epoch": epoch,
                "val_loss": val_loss,
                "val_acc": val_acc,
            }, output)
            print(f"  new best model saved to {output}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"Early stopping: no improvement for {args.patience} epochs")
                break

    print(f"Best validation loss {best_loss:.3f}, checkpoint at {output}")


if __name__ == "__main__":
    main()
