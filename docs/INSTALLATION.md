# Complete installation, run, and GitHub upload

## 1. Requirements

- Windows 10/11 + WSL2, or macOS/Linux
- Python **3.11** added to PATH (`py -3.11 --version` on Windows)
- Docker Desktop with Linux containers (verify `docker compose version`)
- Git (`git --version`)
- Internet during initial UCI download and Docker image build
- Recommended 6–8 GB RAM available to Docker

## 2. Extract and open

Unzip the project into a short path such as `C:\streaming-fairness-monitor`, then right-click in the folder and choose **Open in Terminal**. Your working directory must contain `docker-compose.yml`.

## 3. Python setup and actual Adult dataset

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.prepare_data
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.study --dataset adult --out results/study_adult.csv
```

Mac/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.prepare_data
.venv/bin/python -m pytest -q
.venv/bin/python -m src.study --dataset adult --out results/study_adult.csv
```

You should now have `data/events.csv`, `data/metadata.json`, and `results/study_adult.csv`. If UCI download fails, check internet access and use the official UCI page to obtain `adult.data` and `adult.test`, then place those two files inside `data/` before rerunning prepare_data.

## 4. Start the real Flink streaming monitor

```powershell
docker compose up --build
```

First build downloads multiple container images and PyFlink wheels. Keep the terminal open. Dashboard: `http://localhost:8501`. Flink job manager: `http://localhost:8081`. The source process begins to transmit after the Flink job connects. Refresh the Streamlit page manually to see new windows. Terminal logs can be inspected using:

```powershell
docker compose logs -f jobsubmit
docker compose logs -f replayer
```

## 5. Review notebook and report

```powershell
.\.venv\Scripts\python.exe -m jupyter notebook notebooks/results.ipynb
```

Run all notebook cells; they read pilot CSV and optional Adult CSV. See the report in `report/technical_report.pdf`.

## 6. Put it on GitHub

Create an empty GitHub repository called `streaming-fairness-monitor` (do not add an extra README on the website), then run in the project directory:

```powershell
git init
git add .
git commit -m "Add streaming fairness monitor project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streaming-fairness-monitor.git
git push -u origin main
```

Replace `YOUR_USERNAME`. GitHub may require browser sign-in or a token; it no longer accepts a normal account password for Git operations. Keep raw Adult files and saved model files out of the repository (see `.gitignore`).

## 7. Troubleshooting

- `docker is not recognized`: install Docker Desktop and restart the terminal.
- `Cannot connect to Docker daemon`: start Docker Desktop and wait until it reports that the engine is running.
- `No module named sklearn`: rerun pip installation using the **same** `.venv` interpreter.
- `No events.csv`: run `python -m src.prepare_data` successfully **before** Docker.
- Dashboard empty: inspect jobsubmit logs and wait for Flink windows to close; the dashboard does not automatically refresh.
- Build fails with Python/pip conflict: check `docker compose build --no-cache` logs and verify the selected base image/tag is available. Docker and package versions may change.
- Port 8081 or 8501 in use: stop the conflicting service or edit published port in `docker-compose.yml`.
- To rerun: `docker compose down`; delete `results/live.jsonl`; `docker compose up --build`.
- `python -m src.study` from inside `src/` fails: return to repository root first.

## 8. Demo checklist

Show that the Flink job is visible, dashboard lines move after refresh, a biased late phase is injected by the replayer, alerts are surfaced, the study CSV/figure compare sizes, and notebook and data card explain the limits.
