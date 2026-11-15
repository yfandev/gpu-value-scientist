#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
PYTHON="${PYTHON:-$PWD/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then echo 'Create .venv and pip install -r requirements.txt first.' >&2; exit 1; fi
mkdir -p logs
PYTHON="$PYTHON" bash data/pack/gpu-price-pack-v0.1.1-handover/starter/run_demo.sh data/pack/gpu-price-pack-v0.1.1-handover results/quickstart 2026-10-24 > logs/quickstart.log 2>&1
"$PYTHON" -B src/evidence.py "$@"
"$PYTHON" -B src/pipeline.py "$@"
