#!/bin/bash
# Capture one image from each camera and classify the part.
#
# Usage:   pi/inspect.sh [checkpoint] [extra realtime_inspect.py options]
# Example: pi/inspect.sh checkpoints/model.pth --leds
#
# Exit code: 0 normal, 1 defective, 2 manual inspection needed.
#
# Environment:
#   CAMERA_LENS  fixed lens position per camera (default "8 7 7 8", see cameras.sh);
#                use the same values as when the training images were captured
#   OUT_DIR      where the four images are written (default: Realtime)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cameras.sh"

CHECKPOINT="${1:-checkpoints/model.pth}"
shift || true
OUT_DIR="${OUT_DIR:-Realtime}"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/*.jpg
for cam in 0 1 2 3; do
    select_camera "$cam"
    capture "$OUT_DIR/face$((cam + 1)).jpg" "$(lens_for_camera "$cam")"
done

python3 "$SCRIPT_DIR/../python/realtime_inspect.py" --images "$OUT_DIR" --checkpoint "$CHECKPOINT" "$@"
