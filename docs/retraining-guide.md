# Retraining guide

How to capture images of a new part and retrain the classifier. The model recognises a fixed set of parts and their defects, so a new part, or a new kind of defect on an existing part, needs a retraining run.

## 1. Capture images

Place the part in the centre of the camera station in the standard position, and check it with `pi/preview_cameras.sh`. Then run:

```bash
pi/capture_dataset.sh <object_number> good   # or bad
```

Each capture takes one image from each of the four cameras, so a single capture covers four faces. Each camera uses its own fixed lens position, set by `CAMERA_LENS` (default `"8 7 7 8"` for faces 1 to 4). Keep these the same for training captures and for inspection. To capture a focus stack per face instead, set `FOCUS_STACK="7 8 9 10 11 12"`.

Capture both conditions:

- **Good parts:** non-defective examples.
- **Bad parts:** defective examples, positioned so the defect faces at least one camera.

Capture as many orientations as practical. After each capture, confirm to continue, turn the part, and capture again; the orientation number increments automatically. More orientations make the model more robust.

Aim for a similar number of good and bad images. Augmentation helps close remaining gaps.

### Naming convention

```
Obj<object>_<condition>_Or<orientation>_f<face>.jpg
```

| Field | Meaning |
|---|---|
| `object` | Part number, unique per part type |
| `condition` | `good` or `bad` |
| `orientation` | Increments with each capture |
| `face` | Camera number, 1 to 4 |

Example: `Obj5_good_Or3_f2.jpg` is part 5, non-defective, third orientation, camera 2. Focus-stack captures add `_pos<lens>`.

The script writes each class to its own folder, `Obj<N>_good` or `Obj<N>_bad`. Copy these into `raw/` on the training machine.

## 2. Prepare the dataset

1. Run `select_best_focus` to crop and resize each image, keeping the sharpest frame when focus stacks were captured.
2. Review each `Obj<N>_bad` folder and move images with no visible damage into `Obj<N>_good`.
3. Run `split_dataset` to split every class 70/20/10 into `data/train`, `data/val` and `data/test`.
4. Run `augment_images` on the training folders of any under-represented classes.

`matlab/run_pipeline.m` shows the full sequence.

## 3. Train

```bash
python python/train.py --data data --output checkpoints/<model_name>.pth
```

No code edits are needed. The output layer is sized from the number of class folders, and the class names are saved in the checkpoint. The checkpoint saved is the one with the lowest validation loss.

The default batch size is 4, one part's four faces, as in the thesis. With batches this small, `--freeze-bn` keeps BatchNorm statistics stable and can make training smoother.

## 4. Evaluate

```bash
python python/evaluate.py --data data/test --checkpoint checkpoints/<model_name>.pth --csv predictions.csv
```

Check the pass/fail accuracy, the share of images sent to manual inspection, and the confusion matrix for parts that get confused with each other.

## 5. Deploy

Copy the checkpoint to the Raspberry Pi and run:

```bash
pi/inspect.sh checkpoints/<model_name>.pth --leds
```

The class names and input size travel with the checkpoint, so no script needs editing when parts are added. To use the model from other code, `python/model_utils.py` provides `load_model` and `predict`:

```python
from PIL import Image
from model_utils import load_model, predict

model, class_names, transform = load_model("checkpoints/<model_name>.pth")
results = predict(model, transform, [Image.open(p) for p in face_images], class_names)
# [(class_name, confidence), ...]
```
