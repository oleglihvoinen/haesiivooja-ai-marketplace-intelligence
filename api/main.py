from __future__ import annotations

from pathlib import Path
from typing import Literal
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="HaeSiivooja Marketplace Intelligence API", version="1.0.0")

class MatchRequest(BaseModel):
    city: str
    max_distance_km: float = Field(default=15, gt=0, le=50)
    max_price_cents: int | None = Field(default=None, gt=0)
    limit: int = Field(default=5, ge=1, le=20)

class ForecastRequest(BaseModel):
    city: str
    service_id: Literal["home_cleaning", "deep_cleaning", "move_out_cleaning"]
    date: str

def _cleaners() -> pd.DataFrame:
    path = ROOT / "data" / "cleaner_features.csv"
    if not path.exists():
        raise HTTPException(503, "Run the data and feature pipelines first")
    return pd.read_csv(path)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/match")
def match_cleaners(req: MatchRequest):
    artifact = ROOT / "artifacts" / "match_ranker.joblib"
    if not artifact.exists():
        raise HTTPException(503, "Train the match ranker first")
    bundle = joblib.load(artifact)
    df = _cleaners()
    df = df[df.city == req.city].copy()
    if req.max_price_cents:
        df = df[df.base_hourly_price_cents <= req.max_price_cents]
    if df.empty:
        return {"matches": []}

    # Deterministic public-case proxy. Production would use geospatial travel time.
    df["distance_km"] = 1.0 + (df.index.to_numpy() % max(int(req.max_distance_km), 1))
    df = df[df.distance_km <= req.max_distance_km]
    df["price_index"] = df.base_hourly_price_cents / df.base_hourly_price_cents.median()
    df["match_probability"] = bundle["model"].predict_proba(df[bundle["features"]])[:, 1]
    df["quality_guardrail"] = np.minimum(df.rating / 5.0, df.reliability_score)
    df["ranking_score"] = 0.8 * df.match_probability + 0.2 * df.quality_guardrail

    cols = [
        "cleaner_id", "city", "rating", "base_hourly_price_cents",
        "distance_km", "reliability_score", "completion_rate", "ranking_score"
    ]
    return {
        "matches": (
            df.sort_values("ranking_score", ascending=False)[cols]
              .head(req.limit).round(4).to_dict("records")
        )
    }

@app.post("/api/v1/demand-forecast")
def demand_forecast(req: ForecastRequest):
    artifact = ROOT / "artifacts" / "demand_forecast.joblib"
    if not artifact.exists():
        raise HTTPException(503, "Train the demand forecast first")
    bundle = joblib.load(artifact)
    date = pd.Timestamp(req.date)
    row = pd.DataFrame([{
        "city": req.city,
        "service_id": req.service_id,
        "day_of_week": date.dayofweek,
        "week_of_year": int(date.isocalendar().week),
        "month": date.month,
        "is_weekend": int(date.dayofweek >= 5),
        "dow_sin": np.sin(2 * np.pi * date.dayofweek / 7),
        "dow_cos": np.cos(2 * np.pi * date.dayofweek / 7),
    }])
    prediction = max(float(bundle["model"].predict(row[bundle["features"]])[0]), 0.0)
    return {
        "city": req.city,
        "service_id": req.service_id,
        "date": req.date,
        "predicted_bookings": round(prediction, 2),
    }
