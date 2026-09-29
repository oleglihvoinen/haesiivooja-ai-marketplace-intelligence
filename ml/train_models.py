from __future__ import annotations

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(7)

def train_demand() -> None:
    df = pd.read_csv(ROOT / "data" / "demand_features.csv", parse_dates=["date"]).sort_values("date")
    cutoff = df["date"].quantile(0.8)
    train, test = df[df.date <= cutoff], df[df.date > cutoff]
    features = ["city", "service_id", "day_of_week", "week_of_year", "month", "is_weekend", "dow_sin", "dow_cos"]
    categorical = ["city", "service_id"]
    numeric = [x for x in features if x not in categorical]
    pipe = Pipeline([
        ("prep", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
            ("num", "passthrough", numeric),
        ])),
        ("model", HistGradientBoostingRegressor(max_depth=6, learning_rate=0.06, random_state=42)),
    ])
    pipe.fit(train[features], train["bookings"])
    pred = pipe.predict(test[features])
    mae = float(mean_absolute_error(test["bookings"], pred))
    joblib.dump({"model": pipe, "features": features}, ROOT / "artifacts" / "demand_forecast.joblib")
    (ROOT / "artifacts" / "demand_metrics.json").write_text(json.dumps({"mae": round(mae, 4), "cutoff": str(cutoff.date())}, indent=2))

def train_ranker() -> None:
    cleaners = pd.read_csv(ROOT / "data" / "cleaner_features.csv")
    n = 24000
    sampled = cleaners.sample(n=n, replace=True, random_state=7).reset_index(drop=True)
    sampled["distance_km"] = np.clip(RNG.gamma(2.0, 3.0, n), 0.2, 35)
    sampled["price_index"] = sampled["base_hourly_price_cents"] / sampled["base_hourly_price_cents"].median()
    score = (
        1.8 * sampled["reliability_score"] + 0.45 * sampled["rating"]
        + 1.2 * sampled["completion_rate"] - 0.10 * sampled["distance_km"]
        - 0.55 * sampled["price_index"] - 0.65 * sampled["utilization_proxy"]
        + RNG.normal(0, 0.7, n)
    )
    sampled["accepted_completed"] = (score >= np.quantile(score, 0.47)).astype(int)
    split = int(n * 0.8)
    train, test = sampled.iloc[:split], sampled.iloc[split:]
    features = ["distance_km", "price_index", "rating", "reliability_score", "completion_rate", "utilization_proxy"]
    model = HistGradientBoostingClassifier(max_depth=5, learning_rate=0.07, random_state=42)
    model.fit(train[features], train["accepted_completed"])
    auc = float(roc_auc_score(test["accepted_completed"], model.predict_proba(test[features])[:, 1]))
    joblib.dump({"model": model, "features": features}, ROOT / "artifacts" / "match_ranker.joblib")
    (ROOT / "artifacts" / "match_metrics.json").write_text(json.dumps({"roc_auc": round(auc, 4)}, indent=2))

if __name__ == "__main__":
    (ROOT / "artifacts").mkdir(exist_ok=True)
    train_demand()
    train_ranker()
    print("Models trained")
