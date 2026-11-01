# Data card and educational model card

## Data source
UCI Adult / Census Income, Becker & Kohavi (1996), https://doi.org/10.24432/C5XW20, **CC BY 4.0**. Original dataset: 48,842 records, 14 features, 1994 US Census-derived records. Binary target is annual income above USD 50,000; this is **not a loan repayment or loan approval label**. Dataset files are fetched by `src.prepare_data` and not bundled.

## Processing and split
All original train/test files are joined, stripped, and seeded-shuffled (seed 42). 70% used for training, 30% held out for replay. Some predictor fields may contain `Unknown`. The real feature `sex` is retained **for group audit only** and excluded from model features. Model uses standardized numeric predictors, one-hot categorical predictors and scikit-learn logistic regression. Features including relationship and marital status can act as sensitive proxies; removing sex does **not** guarantee fairness. `data/metadata.json` records the measured held-out classification accuracy after setup.

## Simulation
Held-out income classification predictions are treated only as a **fictional approval proxy**. Events receive new sequence-based replay ordering and wall-clock timestamps. During the second part, up to 80% of Female positive predictions are deliberately set to negative in the live stream (75% in the offline study). This controlled shift is artificial and not evidence of observed bias in a financial institution.

## Protected attributes and limitations
Sex is recorded as Male/Female from the data source; representation of gender identity is inadequate. Historical census context, selection bias, missing fields, intersectional effects, and correlated predictors limit generalizability. Sensitive data must not be used to infer or identify individuals. Never use this educational classifier to make actual lending decisions.

## Risk and evaluation
Check DP and EO gaps with minimum supports, baseline calibration, false-alarm rates, and delay. A gap is an operational signal requiring investigation, not a legal conclusion. The benchmark lacks transaction ground truth, causal counterfactuals, and institutional review. In real systems, assess privacy, data retention, model drift, subgroup coverage, sample uncertainty, consent, and regulatory obligations.

## Attribution
Becker, B. and Kohavi, R. (1996). Adult [Dataset]. UCI Machine Learning Repository. CC BY 4.0. https://archive.ics.uci.edu/dataset/2/adult . Changes: preprocessing, train/test reshuffle, proxy model, injected drift, synthetic timestamps.
