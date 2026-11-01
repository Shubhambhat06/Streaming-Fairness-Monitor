# 3-minute class demo script

**0:00–0:30** Introduce the fairness monitor and clarify that UCI Adult income classification stands in for fictional loan approval, not real loan data.

**0:30–1:00** Show GitHub README and architecture diagram. Explain source → PyFlink 20-second sliding processing-time windows every 5 seconds → JSONL → Streamlit.

**1:00–1:45** Open `http://localhost:8081` and show the Flink job; open `http://localhost:8501`, press Refresh, and explain male-minus-female demographic parity and equal opportunity gaps.

**1:45–2:15** Show replay logs and later drift phase. Refresh dashboard to discuss alarm behavior. Explain the fixed zero-gap production demo alert reference and why calibration matters.

**2:15–2:45** Open `results/study_synthetic.csv` or notebook. Compare sizes 200, 500, 1000, 2000 events, discussing false alarms and delay. Note that this study is an offline event-count analogue, not seconds-based Flink measurements.

**2:45–3:00** Point to tests, model/data card, limitations, and reproducible setup. End by noting socket and file sinks are demo-only, not transactional production infrastructure.
