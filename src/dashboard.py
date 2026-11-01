import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Streaming Fairness Monitor", layout="wide")
st.title("Streaming Fairness Monitor")
st.caption("Simulated lending: UCI Adult income labels are used as proxy outcomes, not real loan approval data.")
path = Path(os.getenv("RESULTS_PATH", "results/live.jsonl"))
refresh = st.sidebar.button("Refresh data")
threshold = st.sidebar.slider("Reference deviation alert threshold", 0.01, 0.40, 0.12, 0.01)
if not path.exists():
    st.info("No Flink output yet. Start Docker Compose or run the replay pipeline.")
    st.stop()
rows=[]
for line in path.read_text(encoding="utf8").splitlines():
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        continue
if not rows:
    st.info("Waiting for completed sliding windows")
    st.stop()
df=pd.json_normalize(rows)
df["window_time"]=pd.to_datetime(df["observed_at"],unit="s")
latest=df.iloc[-1]
cols=st.columns(4)
cols[0].metric("Rows in latest window", int(latest["n"]))
cols[1].metric("Demographic parity gap", "N/A" if pd.isna(latest["demographic_parity_gap"]) else f"{latest['demographic_parity_gap']:+.3f}")
cols[2].metric("Equal opportunity gap", "N/A" if pd.isna(latest["equal_opportunity_gap"]) else f"{latest['equal_opportunity_gap']:+.3f}")
cols[3].metric("Flink alerts", int(df[["dp_alert","eo_alert"]].fillna(False).any(axis=1).sum()))
for col, title in (("demographic_parity_gap", "Demographic parity (Male − Female)"),
                   ("equal_opportunity_gap", "Equal opportunity (Male − Female)")):
    plot=px.line(df,x="window_time",y=col,markers=True,title=title)
    plot.add_hline(y=0,line_dash="dot")
    st.plotly_chart(plot,use_container_width=True)
st.subheader("Live alerts")
alerts=df[df[["dp_alert","eo_alert"]].fillna(False).any(axis=1)]
st.dataframe(alerts[["window_time","demographic_parity_gap","equal_opportunity_gap","dp_alert","eo_alert"]].tail(30).iloc[::-1],use_container_width=True)
st.caption("Flink alerts use baseline reference values from the Docker configuration; the slider is for display guidance only, not a live Flink threshold change.")
st.subheader("Recent windows")
st.dataframe(df.tail(20).iloc[::-1],use_container_width=True)
