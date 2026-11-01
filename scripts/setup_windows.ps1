$ErrorActionPreference = "Stop"
if (!(Get-Command py -ErrorAction SilentlyContinue)) { throw "Install Python 3.11 first" }
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.prepare_data
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.study --dataset adult --out results/study_adult.csv
Write-Host "Setup done. Run: docker compose up --build"
