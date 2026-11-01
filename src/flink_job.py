import json
import os
import time
from pathlib import Path
from pyflink.common import Types, Time
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import ProcessAllWindowFunction
from pyflink.datastream.window import SlidingProcessingTimeWindows
from src.fairness import compute_metrics, alert_for_gap


class FairnessWindow(ProcessAllWindowFunction):
    def process(self, context, elements):
        records = list(elements)
        metrics = compute_metrics(records, min_group=int(os.getenv("MIN_GROUP", "10")),
                                  min_positive=int(os.getenv("MIN_POSITIVE", "5")))
        metrics["observed_at"] = time.time()
        metrics["window_seconds"] = int(os.getenv("WINDOW_SECONDS", "20"))
        metrics["slide_seconds"] = int(os.getenv("SLIDE_SECONDS", "5"))
        metrics["phase_drift_fraction"] = sum(r["phase"] == "drift" for r in records) / len(records) if records else 0
        for name, key in (("dp", "demographic_parity_gap"), ("eo", "equal_opportunity_gap")):
            reference = float(os.getenv("REFERENCE_DP" if name == "dp" else "REFERENCE_EO", "0"))
            metrics[f"{name}_alert"] = alert_for_gap(metrics[key], reference, float(os.getenv("ALERT_THRESHOLD", "0.12")))
        yield json.dumps(metrics)


def parse(line):
    return json.loads(line)


def save(line):
    path = Path(os.getenv("RESULTS_PATH", "/opt/project/results/live.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf8") as out:
        out.write(line + "\n")
    return line


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    window = int(os.getenv("WINDOW_SECONDS", "20"))
    slide = int(os.getenv("SLIDE_SECONDS", "5"))
    if not (window >= slide > 0):
        raise ValueError("Window must be >= slide > 0")
    source = env.socket_text_stream(os.getenv("REPLAY_HOST", "replayer"), 9999, "\n")
    source.map(parse, output_type=Types.PICKLED_BYTE_ARRAY()) \
        .window_all(SlidingProcessingTimeWindows.of(Time.seconds(window), Time.seconds(slide))) \
        .process(FairnessWindow(), output_type=Types.STRING()) \
        .map(save, output_type=Types.STRING()).print()
    env.execute("Streaming Fairness Monitor")


if __name__ == "__main__":
    main()
