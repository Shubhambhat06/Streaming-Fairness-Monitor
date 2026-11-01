import argparse
import csv
import hashlib
import json
import random
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/"
COLUMNS = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
           "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
           "hours_per_week", "native_country", "income"]


def download(out):
    out.mkdir(exist_ok=True, parents=True)
    for filename in ("adult.data", "adult.test"):
        path = out / filename
        if not path.exists():
            urllib.request.urlretrieve(BASE + filename, path)
    return out


def load_adult(folder):
    rows = []
    for name in ("adult.data", "adult.test"):
        with (folder / name).open(encoding="utf-8") as f:
            for line in f:
                values = [v.strip().rstrip(".") for v in line.split(",")]
                if len(values) == 15 and values[-1] in (">50K", "<=50K"):
                    rows.append(values)
    df = pd.DataFrame(rows, columns=COLUMNS).replace("?", "Unknown")
    for col in ("age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"):
        df[col] = pd.to_numeric(df[col])
    df["label"] = (df["income"] == ">50K").astype(int)
    return df


def build(seed=42, out=Path("data")):
    folder = download(out)
    df = load_adult(folder)
    rng = np.random.default_rng(seed)
    shuffled = df.iloc[rng.permutation(len(df))].reset_index(drop=True)
    cut = int(len(shuffled)*0.7)
    train, test = shuffled.iloc[:cut], shuffled.iloc[cut:]
    numeric = ["age", "education_num", "capital_gain", "capital_loss", "hours_per_week"]
    categoric = ["workclass", "education", "marital_status", "occupation", "relationship", "native_country"]
    transformer = ColumnTransformer([("numeric", StandardScaler(), numeric),
                                     ("categoric", OneHotEncoder(handle_unknown="ignore"), categoric)])
    model = Pipeline([("prep", transformer), ("classifier", LogisticRegression(max_iter=1000, random_state=seed))])
    model.fit(train[numeric+categoric], train["label"])
    preds = model.predict(test[numeric+categoric])
    events = pd.DataFrame({"id": [f"adult-{i}" for i in range(len(test))],
                           "sex": test["sex"].values, "label": test["label"].values,
                           "prediction": preds})
    events.to_csv(out / "events.csv", index=False)
    meta = {"dataset": "UCI Adult Income", "source": BASE, "seed": seed,
            "full_rows": len(df), "training_rows": len(train), "held_out_rows": len(test),
            "accuracy": round(float(accuracy_score(test["label"], preds)), 4),
            "sensitive_attribute_excluded_from_model": "sex", "note": "Income prediction is NOT a real loan decision."}
    (out / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", default="data")
    args=parser.parse_args()
    build(out=Path(args.output))
