#!/bin/bash
# Show a short live preview from each camera in turn, for aligning the part
# and checking that all four cameras respond.
#
# Environment: PREVIEW_MS  preview length per camera in milliseconds (default 5000)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cameras.sh"

for cam in 0 1 2 3; do
    echo "Camera $cam (face $((cam + 1)))"
    select_camera "$cam"
    libcamera-hello -t "${PREVIEW_MS:-5000}"
done
