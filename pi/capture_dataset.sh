#!/bin/bash
# Capture training images for one part from all four cameras, one orientation
# at a time.
#
# Usage:   pi/capture_dataset.sh <object_number> <good|bad> [start_orientation]
# Example: pi/capture_dataset.sh 5 bad
#
# Images are saved as
#   Obj<N>_<condition>/Obj<N>_<condition>_Or<orientation>_f<face>.jpg
# After each orientation you are asked whether to continue; answering yes
# increments the orientation number for the next set.
#
# Environment:
#   CAMERA_LENS  fixed lens position per camera (default "8 7 7 8", see cameras.sh)
#   FOCUS_STACK  capture a focus stack instead, e.g. "7 8 9 10 11 12"; files get
#                a _pos<lens> suffix, and matlab/select_best_focus.m keeps the sharpest
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cameras.sh"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <object_number> <good|bad> [start_orientation]"
    exit 1
fi
OBJ="$1"
COND="$2"
ORIENT="${3:-1}"
case "$COND" in
    good|bad) ;;
    *) echo "Condition must be 'good' or 'bad'"; exit 1 ;;
esac

FOCUS_STACK="${FOCUS_STACK:-}"
OUT_DIR="Obj${OBJ}_${COND}"
mkdir -p "$OUT_DIR"

while true; do
    echo "=== Obj${OBJ} ${COND}, orientation ${ORIENT} ==="
    for cam in 0 1 2 3; do
        select_camera "$cam"
        face=$((cam + 1))
        base="$OUT_DIR/Obj${OBJ}_${COND}_Or${ORIENT}_f${face}"
        if [ -n "$FOCUS_STACK" ]; then
            for lens in $FOCUS_STACK; do
                capture "${base}_pos${lens}.jpg" "$lens"
                echo "Face ${face}, lens position ${lens}"
            done
        else
            capture "${base}.jpg" "$(lens_for_camera "$cam")"
            echo "Face ${face}"
        fi
    done

    while true; do
        read -r -p "Turn the part and capture the next orientation? [y/n] " answer
        case "$answer" in
            [Yy]*) ORIENT=$((ORIENT + 1)); break ;;
            [Nn]*) echo "Images saved in $OUT_DIR"; exit 0 ;;
            *) echo "Please answer y or n." ;;
        esac
    done
done
