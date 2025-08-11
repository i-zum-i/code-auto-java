#!/usr/bin/env bash
set -euo pipefail

echo "[worker] start"
python3 /home/app/app/worker.py
echo "[worker] done"