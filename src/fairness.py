import math


def compute_metrics(records, min_group=10, min_positive=5):
    groups = {"Female": [], "Male": []}
    for r in records:
        if r["sex"] in groups:
            groups[r["sex"]].append(r)
    out = {"n": sum(map(len, groups.values()))}
    for group, rows in groups.items():
        approvals = sum(int(r["prediction"]) for r in rows)
        positives = [r for r in rows if int(r["label"]) == 1]
        true_approvals = sum(int(r["prediction"]) for r in positives)
        out[group] = {"n": len(rows), "positive_n": len(positives),
                      "approval_rate": approvals / len(rows) if len(rows) >= min_group else None,
                      "tpr": true_approvals / len(positives) if len(positives) >= min_positive else None}
    def difference(metric):
        a = out["Male"][metric]
        b = out["Female"][metric]
        return round(a-b, 6) if a is not None and b is not None else None
    out["demographic_parity_gap"] = difference("approval_rate")
    out["equal_opportunity_gap"] = difference("tpr")
    return out


def alert_for_gap(gap, reference, threshold):
    if gap is None or reference is None:
        return False
    return abs(gap - reference) >= threshold
