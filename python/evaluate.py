"""Evaluate a trained checkpoint on the held-out test split.

Reports:
  * accuracy over all classes (part type + condition)
  * pass/fail accuracy (good vs bad, ignoring part type)
  * how many images fall below the confidence threshold and would be sent
    to manual inspection, and accuracy on the images decided automatically
  * per-class precision/recall and a confusion matrix

Example:
    python python/evaluate.py --data data/test --checkpoint checkpoints/model.pth
"""
import argparse
import csv

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model_utils import condition, load_model


def decision(class_name, confidence, threshold):
    if confidence < threshold:
        return "manual inspection"
    return "normal" if condition(class_name) == "good" else "defective"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data/test", help="test folder with one sub-folder per class")
    p.add_argument("--checkpoint", default="checkpoints/model.pth")
    p.add_argument("--threshold", type=float, default=0.75,
                   help="below this confidence a part is sent to manual inspection")
    p.add_argument("--center-crop", type=int, default=0,
                   help="centre-crop raw camera images before resizing (e.g. 2000 for images "
                        "captured on the station that were not prepared with select_best_focus)")
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--csv", help="optional path to write per-image predictions")
    p.add_argument("--verbose", action="store_true", help="print every prediction")
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, class_names, transform = load_model(args.checkpoint, device)

    if args.center_crop:
        transform = transforms.Compose([transforms.CenterCrop(args.center_crop), transform])
    test_data = datasets.ImageFolder(args.data, transform=transform)
    unknown = set(test_data.classes) - set(class_names)
    if unknown:
        raise ValueError(f"Test classes not seen in training: {sorted(unknown)}")
    # ImageFolder numbers only the folders present, so map labels to the model's class order.
    to_model_index = [class_names.index(c) for c in test_data.classes]
    loader = DataLoader(test_data, batch_size=args.batch_size, shuffle=False)

    y_true, y_pred, conf = [], [], []
    with torch.no_grad():
        for inputs, labels in loader:
            probs = torch.softmax(model(inputs.to(device)), dim=1)
            c, p = probs.max(dim=1)
            y_true += [to_model_index[i] for i in labels.tolist()]
            y_pred += p.tolist()
            conf += c.tolist()
    y_true, y_pred, conf = np.array(y_true), np.array(y_pred), np.array(conf)
    paths = [path for path, _ in test_data.samples]

    true_cond = np.array([condition(class_names[i]) for i in y_true])
    pred_cond = np.array([condition(class_names[i]) for i in y_pred])
    auto = conf >= args.threshold

    rows = []
    for path, t, p, c in zip(paths, y_true, y_pred, conf):
        rows.append([path, class_names[t], class_names[p], f"{c:.4f}",
                     decision(class_names[p], c, args.threshold)])
        if args.verbose:
            print(f"{path}: true {class_names[t]}, predicted {class_names[p]} ({c:.1%}) -> {rows[-1][-1]}")

    n = len(y_true)
    print(f"\nTest images: {n}")
    print(f"Accuracy, all classes:             {(y_true == y_pred).mean():.3f}")
    print(f"Pass/fail accuracy (good vs bad):  {(true_cond == pred_cond).mean():.3f}")
    print(f"Sent to manual inspection (< {args.threshold:.0%}): {(~auto).sum()} ({(~auto).mean():.1%})")
    if auto.any():
        print(f"Accuracy on automatic decisions:   {(y_true[auto] == y_pred[auto]).mean():.3f}")
        print(f"Pass/fail on automatic decisions:  {(true_cond[auto] == pred_cond[auto]).mean():.3f}")

    labels = sorted(set(y_true) | set(y_pred))
    names = [class_names[i] for i in labels]
    print("\n" + classification_report(y_true, y_pred, labels=labels, target_names=names, zero_division=0))
    print("Confusion matrix (rows = true, columns = predicted):")
    print("  " + ", ".join(names))
    print(confusion_matrix(y_true, y_pred, labels=labels))

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["image", "true", "predicted", "confidence", "decision"])
            writer.writerows(rows)
        print(f"\nPredictions written to {args.csv}")


if __name__ == "__main__":
    main()
