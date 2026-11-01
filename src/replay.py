import argparse
import csv
import json
import os
import random
import socket
import time
from pathlib import Path


def load_rows(path):
    with open(path, newline="", encoding="utf8") as f:
        return list(csv.DictReader(f))


def stream_rows(rows, rate, drift_at, seed):
    rng = random.Random(seed)
    for i, row in enumerate(rows):
        record = {"id": row["id"], "sex": row["sex"], "label": int(row["label"]),
                  "prediction": int(row["prediction"]), "sequence": i,
                  "phase": "drift" if i >= drift_at else "baseline", "event_time": time.time()}
        if i >= drift_at and record["sex"] == "Female" and record["prediction"] == 1 and rng.random() < 0.80:
            record["prediction"] = 0
        yield record
        if rate > 0:
            time.sleep(1.0 / rate)


def serve(host, port, rows, rate, drift_fraction, seed, loops):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        print(f"Listening on {host}:{port}; rows={len(rows)}", flush=True)
        conn, address = sock.accept()
        with conn:
            print(f"Connected: {address}", flush=True)
            total = len(rows)*loops
            stream = (rows[i % len(rows)] for i in range(total))
            for record in stream_rows(list(stream), rate, int(total*drift_fraction), seed):
                try:
                    conn.sendall((json.dumps(record)+"\n").encode("utf8"))
                except (BrokenPipeError, ConnectionResetError):
                    break
        print("Replay finished", flush=True)


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--file", default="data/events.csv")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=9999)
    ap.add_argument("--rate", type=float, default=50)
    ap.add_argument("--drift-fraction", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--loops", type=int, default=2)
    a=ap.parse_args()
    serve(a.host,a.port,load_rows(a.file),a.rate,a.drift_fraction,a.seed,a.loops)
