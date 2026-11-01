#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.prepare_data
.venv/bin/python -m pytest -q
.venv/bin/python -m src.study --dataset adult --out results/study_adult.csv
echo "Setup done. Run: docker compose up --build"
