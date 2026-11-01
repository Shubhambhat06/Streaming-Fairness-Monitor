import argparse
import csv
import json
import random
from pathlib import Path
from src.fairness import compute_metrics, alert_for_gap


def synthetic_events(n=8000, seed=42, drift_start=4000):
    rng = random.Random(seed)
    events=[]
    for i in range(n):
        sex = "Male" if rng.random() < .5 else "Female"
        label = int(rng.random() < .42)
        probability = .78 if label else .19
        prediction = int(rng.random() < probability)
        if i >= drift_start and sex == "Female" and prediction and rng.random() < .75:
            prediction=0
        events.append({"sex":sex,"label":label,"prediction":prediction,"phase":"drift" if i>=drift_start else "baseline"})
    return events


def evaluate(events, size, slide=100, threshold=.13, min_group=10, min_positive=5, drift_start=None):
    if drift_start is None:
        drift_start = len(events)//2
    raw=[]
    for end in range(size,len(events)+1,slide):
        m=compute_metrics(events[end-size:end],min_group,min_positive)
        raw.append((end,m))
    baseline=[m for end,m in raw if end<=drift_start]
    reference={k:sum(m[k] for m in baseline if m[k] is not None)/max(1,sum(m[k] is not None for m in baseline))
               for k in ("demographic_parity_gap","equal_opportunity_gap")}
    outputs=[]
    for end,m in raw:
        alarm=any(alert_for_gap(m[k],reference[k],threshold) for k in reference)
        outputs.append({"end":end,"alarm":alarm,"drift":end>drift_start,"metrics":m})
    early=[r for r in outputs if not r["drift"]]
    late=[r for r in outputs if r["drift"]]
    first=next((r["end"] for r in late if r["alarm"]),None)
    return {"window_events":size,"slide_events":slide,"threshold":threshold,
            "baseline_windows":len(early),"drift_windows":len(late),
            "false_alarms":sum(r["alarm"] for r in early),
            "false_alarm_rate":round(sum(r["alarm"] for r in early)/len(early),4) if early else None,
            "detection_delay_events":first-drift_start if first is not None else None,
            "detection_rate":round(sum(r["alarm"] for r in late)/len(late),4) if late else None,
            "baseline_dp_reference":round(reference["demographic_parity_gap"],4),
            "baseline_eo_reference":round(reference["equal_opportunity_gap"],4)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",choices=["synthetic","adult"],default="synthetic")
    ap.add_argument("--file",default="data/events.csv")
    ap.add_argument("--out",default="results/study_synthetic.csv")
    ap.add_argument("--seed",type=int,default=42)
    args=ap.parse_args()
    if args.dataset=="adult":
        with open(args.file,newline="",encoding="utf8") as f:
            raw=[{**r,"label":int(r["label"]),"prediction":int(r["prediction"])} for r in csv.DictReader(f)]
        if not raw:
            raise ValueError("Empty Adult events file")
        rng=random.Random(args.seed)
        drift_start=len(raw)//2
        for i,r in enumerate(raw):
            if i>=drift_start and r["sex"]=="Female" and r["prediction"] and rng.random()<.75:
                r["prediction"]=0
    else:
        raw=synthetic_events(seed=args.seed)
        drift_start=len(raw)//2
    values=[evaluate(raw,n,slide=100,drift_start=drift_start) for n in (200,500,1000,2000)]
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=values[0].keys());writer.writeheader();writer.writerows(values)
    out.with_suffix(".json").write_text(json.dumps({"source":args.dataset,"seed":args.seed,"rows":len(raw),"drift_start":drift_start,"results":values},indent=2))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(7,4))
        ax.plot([v["window_events"] for v in values],[v["false_alarm_rate"] for v in values],marker="o",label="False alarm rate")
        ax.set(xlabel="Window size (events)",ylabel="Fraction of baseline windows flagged",title="Window size versus false alarms")
        fig.tight_layout();fig.savefig(out.with_suffix(".png"),dpi=140);plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(values,indent=2))


if __name__=="__main__":
    main()
