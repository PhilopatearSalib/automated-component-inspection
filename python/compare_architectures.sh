#!/bin/bash
# Train and evaluate every ResNet depth on the same dataset split.
#
# Usage:   python/compare_architectures.sh [data_dir] [image_size]
# Example: python/compare_architectures.sh data 512
#
# Each run writes checkpoints/<arch>.pth and results/<arch>.txt.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="${1:-data}"
SIZE="${2:-512}"
mkdir -p checkpoints results

for arch in resnet18 resnet34 resnet50 resnet101 resnet152; do
    echo "=== $arch ==="
    python3 "$SCRIPT_DIR/train.py" --data "$DATA" --arch "$arch" --image-size "$SIZE" \
        --output "checkpoints/$arch.pth"
    python3 "$SCRIPT_DIR/evaluate.py" --data "$DATA/test" --checkpoint "checkpoints/$arch.pth" \
        | tee "results/$arch.txt"
done
