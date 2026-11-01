from src.fairness import compute_metrics, alert_for_gap
from src.study import synthetic_events, evaluate


def test_exact_gaps():
    x=([{"sex":"Male","label":1,"prediction":1}]*10+
       [{"sex":"Female","label":1,"prediction":0}]*10)
    m=compute_metrics(x)
    assert m["demographic_parity_gap"]==1
    assert m["equal_opportunity_gap"]==1


def test_small_support_suppressed():
    m=compute_metrics([{"sex":"Male","label":0,"prediction":1}])
    assert m["demographic_parity_gap"] is None
    assert m["equal_opportunity_gap"] is None


def test_alert_reference():
    assert alert_for_gap(.35,.10,.2)
    assert not alert_for_gap(.12,.10,.2)
    assert not alert_for_gap(None,.10,.2)


def test_deterministic_study():
    events=synthetic_events()
    a=evaluate(events,500)
    b=evaluate(events,500)
    assert a==b
    assert a["baseline_windows"]>0
