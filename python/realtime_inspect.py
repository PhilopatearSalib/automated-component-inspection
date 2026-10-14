"""Inspect one part from its four face images.

Classifies every image in a folder (one per camera) and combines them into a
single decision for the part:

  Defective Object          at least one face is confidently classified as bad
  Manual inspection needed  otherwise, if any face is below the confidence threshold
  Normal Object             every face is confidently good

A defect is usually visible from only one or two faces, so one confident
"bad" face is enough to reject the part.

Exit code: 0 normal, 1 defective, 2 manual inspection needed.
With --leds, the result is also shown on the station's status LEDs
(green: normal, red: defective, yellow: manual inspection).

Example (normally run by pi/inspect.sh after capturing the images):
    python python/realtime_inspect.py --images Realtime --checkpoint checkpoints/model.pth
"""
import argparse
import os
import sys
from collections import Counter

import torch
from PIL import Image
from torchvision import transforms

from model_utils import condition, load_model, part_type, predict

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
EXIT_CODES = {"Normal Object": 0, "Defective Object": 1, "Manual inspection needed": 2}

# Status LEDs on the station (BCM numbering)
LED_PINS = {"Normal Object": 22, "Defective Object": 17, "Manual inspection needed": 27}


def show_on_leds(result, seconds):
    """Light the LED for this result for a few seconds. Raspberry Pi only."""
    import time
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    pin = LED_PINS[result]
    try:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, True)
        time.sleep(seconds)
        GPIO.output(pin, False)
    finally:
        GPIO.cleanup()


def decide(results, threshold):
    if any(condition(name) == "bad" and conf >= threshold for name, conf in results):
        return "Defective Object"
    if any(conf < threshold for _, conf in results):
        return "Manual inspection needed"
    return "Normal Object"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", default="Realtime", help="folder with one image per face")
    p.add_argument("--checkpoint", default="checkpoints/model.pth")
    p.add_argument("--threshold", type=float, default=0.75)
    p.add_argument("--center-crop", type=int, default=2000,
                   help="square centre crop (pixels) applied to raw camera images before resizing, "
                        "matching the crop used when the training images were prepared; 0 disables it")
    p.add_argument("--leds", action="store_true", help="show the result on the status LEDs")
    p.add_argument("--led-seconds", type=float, default=5)
    args = p.parse_args()

    files = sorted(os.path.join(args.images, f) for f in os.listdir(args.images)
                   if f.lower().endswith(IMAGE_EXTENSIONS))
    if not files:
        sys.exit(f"No images found in {args.images}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, class_names, transform = load_model(args.checkpoint, device)
    # Training images were centre-cropped from the full camera frame before resizing
    # (see matlab/select_best_focus.m), so raw captures get the same crop here.
    if args.center_crop:
        transform = transforms.Compose([transforms.CenterCrop(args.center_crop), transform])
    results = predict(model, transform, [Image.open(f) for f in files], class_names, device)

    for path, (name, conf) in zip(files, results):
        flag = "" if conf >= args.threshold else "  (low confidence)"
        print(f"{os.path.basename(path)}: {name} ({conf:.1%}){flag}")

    parts = [part_type(name) for name, _ in results if part_type(name)]
    if parts:
        part, votes = Counter(parts).most_common(1)[0]
        print(f"Identified part: {part} ({votes}/{len(results)} faces)")

    result = decide(results, args.threshold)
    print(result)
    if args.leds:
        show_on_leds(result, args.led_seconds)
    sys.exit(EXIT_CODES[result])


if __name__ == "__main__":
    main()
