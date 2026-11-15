#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-$PWD/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  echo 'Project Python is missing. Create .venv and install requirements-modal.txt first.' >&2
  exit 1
fi
if [ -x "$PWD/.venv/bin/modal" ]; then
  MODAL_CLI="$PWD/.venv/bin/modal"
else
  MODAL_CLI="$(command -v modal || true)"
fi
if [ -z "$MODAL_CLI" ]; then
  echo 'Modal CLI is missing. Install requirements-modal.txt and try again.' >&2
  exit 1
fi
for file in demo/index.html demo/data.json demo/forecasts.csv demo/findings.md demo/README.md; do
  if [ ! -s "$file" ]; then
    echo "Missing public demo artifact: $file. Run ./reproduce.sh first." >&2
    exit 1
  fi
done
# Modal authenticates from MODAL_TOKEN_ID/MODAL_TOKEN_SECRET or its configured token file.
# No tokens are printed, bundled into the image, or sent to browser code.
mkdir -p logs
"$PYTHON" -B src/prepare_deploy.py
export GPU_VALUE_DEMO_DIR="$PWD/deliverables/deploy_demo"
"$PYTHON" -B src/with_env.py "$MODAL_CLI" deploy src/modal_jobs.py 2>&1 | tee logs/modal-deploy.log
printf '\nUse the exact public demo_site URL printed above. Verify it without cookies before sharing.\n'
