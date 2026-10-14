"""Offline augmentation with OpenCV.

Writes transformed copies next to each original as <name>_<transform>.<ext>.
Run it on the TRAINING split only, after splitting, so that copies of the same
image never end up in both training and test data.

Example:
    python python/augment_images.py data/train/Obj3_bad
    python python/augment_images.py data/train/Obj3_bad --transforms flip_horizontal rotate_180
"""
import argparse
import os

import cv2
import numpy as np

SHARPEN_KERNEL = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

TRANSFORMS = {
    "flip_horizontal": lambda img: cv2.flip(img, 1),
    "flip_vertical": lambda img: cv2.flip(img, 0),
    "rotate_90": lambda img: cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
    "rotate_180": lambda img: cv2.rotate(img, cv2.ROTATE_180),
    "rotate_270": lambda img: cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
    "brightness_increase": lambda img: cv2.convertScaleAbs(img, alpha=1.5, beta=0),
    "brightness_decrease": lambda img: cv2.convertScaleAbs(img, alpha=0.5, beta=0),
    "sharpen": lambda img: cv2.filter2D(img, -1, SHARPEN_KERNEL),
    "blur": lambda img: cv2.GaussianBlur(img, (5, 5), 0),
    "add_noise": lambda img: (img + np.random.normal(0, 10, img.shape)).clip(0, 255).astype(np.uint8),
}
DEFAULT_TRANSFORMS = list(TRANSFORMS)


def _resize_back(img, out):
    return cv2.resize(out, (img.shape[1], img.shape[0]))


def _center_mask(img):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (img.shape[1] // 2, img.shape[0] // 2), min(img.shape[:2]) // 3, 255, -1)
    return cv2.bitwise_and(img, img, mask=mask)


# Also tried during development, not used for the final model. Available on request.
TRANSFORMS.update({
    "contrast_increase": lambda img: cv2.convertScaleAbs(img, alpha=1, beta=50),
    "contrast_decrease": lambda img: cv2.convertScaleAbs(img, alpha=1, beta=-50),
    "crop_center": lambda img: _resize_back(img, img[img.shape[0] // 4:img.shape[0] * 3 // 4,
                                                     img.shape[1] // 4:img.shape[1] * 3 // 4]),
    "scale_up": lambda img: _resize_back(img, cv2.resize(img, None, fx=1.5, fy=1.5)),
    "scale_down": lambda img: _resize_back(img, cv2.resize(img, None, fx=0.5, fy=0.5)),
    "skew_left": lambda img: cv2.warpAffine(img, np.float32([[1, -0.5, 0], [0, 1, 0]]),
                                            (img.shape[1], img.shape[0])),
    "skew_right": lambda img: cv2.warpAffine(img, np.float32([[1, 0.5, 0], [0, 1, 0]]),
                                             (img.shape[1], img.shape[0])),
    "mask_circle": _center_mask,
})

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", help="folder of images to augment (in place)")
    p.add_argument("--transforms", nargs="+", choices=sorted(TRANSFORMS), default=DEFAULT_TRANSFORMS,
                   help="which transforms to apply (default: the set used for the final model)")
    p.add_argument("--seed", type=int, default=0, help="seed for the noise transform")
    args = p.parse_args()
    np.random.seed(args.seed)

    # List files before writing anything, so new copies are not augmented again.
    files = sorted(f for f in os.listdir(args.folder)
                   if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS)
    written = 0
    for filename in files:
        path = os.path.join(args.folder, filename)
        img = cv2.imread(path)
        if img is None:
            print(f"Skipping unreadable image: {path}")
            continue
        base, ext = os.path.splitext(path)
        for name in args.transforms:
            out_path = f"{base}_{name}{ext}"
            if cv2.imwrite(out_path, TRANSFORMS[name](img)):
                written += 1
            else:
                print(f"Could not write {out_path}")
    print(f"Augmented {len(files)} images -> {written} new files in {args.folder}")


if __name__ == "__main__":
    main()
