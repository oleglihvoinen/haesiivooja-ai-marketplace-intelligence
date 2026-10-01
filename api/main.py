from __future__ import annotations

from pathlib import Path
from typing import Literal
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(
    title="HaeSiivooja Real-Time Marketplace Intelligence & AI Decision API",
    version="2.0.0",
)

ServiceId = Literal["home_cleaning", "deep_cleaning", "move_out_cleaning"]


class MatchRequest(BaseModel):
    city: str
    max_distance_km: float = Field(default=15, gt=0, le=50)
    max_price_cents: int | None = Field(default=None, gt=0)
    limit: int = Field(default=5, ge=1, le=20)


class ForecastRequest(BaseModel):
    city: str
    service_id: ServiceId
    date: str


class DecisionRequest(BaseModel):
    city: str
    service_id: ServiceId
    date: str


def _cleaners() -> pd.DataFrame:
    path = ROOT / "data" / "cleaner_features.csv"
    if not path.exists():
        raise HTTPException(503, "Run the data and feature pipelines first")
    return pd.read_csv(path)


def _forecast(city: str, service_id: str, date: str) -> float:
    artifact = ROOT / "artifacts" / "demand_forecast.joblib"
    if not artifact.exists():
        raise HTTPException(503, "Train the demand forecast first")
    bundle = joblib.load(artifact)
    dt = pd.Timestamp(date)
    row = pd.DataFrame([{
        "city": city,
        "service_id": service_id,
        "day_of_week": dt.dayofweek,
        "week_of_year": int(dt.isocalendar().week),
        "month": dt.month,
        "is_weekend": int(dt.dayofweek >= 5),
        "dow_sin": np.sin(2 * np.pi * dt.dayofweek / 7),
        "dow_cos": np.cos(2 * np.pi * dt.dayofweek / 7),
    }])
    return max(float(bundle["model"].predict(row[bundle["features"]])[0]), 0.0)


def _capacity_proxy(city: str) -> float:
    """
    Public-case approximation only.

    Production capacity must come from real-time cleaner availability,
    blocked time, confirmed bookings and service compatibility.
    """
    df = _cleaners()
    city_df = df[df.city == city].copy()
    if city_df.empty:
        return 0.0
    historical_minutes = pd.read_csv(ROOT / "data" / "bookings.csv")["duration_min"]
    median_booking_minutes = max(float(historical_minutes.median()), 60.0)
    daily_minutes = city_df["weekly_capacity_minutes"].sum() / 7.0
    return float(daily_minutes / median_booking_minutes)


def _decision_from_gap(gap: float) -> list[dict]:
    if gap <= 0:
        return [{
            "action": "no_capacity_intervention",
            "reason": "Estimated capacity covers forecast demand.",
            "human_approval_required": False,
        }]

    actions = [{
        "action": "availability_campaign",
        "reason": "Ask reliable cleaners to open additional availability.",
        "human_approval_required": True,
    }]
    if gap >= 5:
        actions.append({
            "action": "expand_matching_radius",
            "reason": "Evaluate nearby eligible cleaners outside the default radius.",
            "human_approval_required": True,
        })
    if gap >= 10:
        actions.append({
            "action": "incentive_simulation",
            "reason": "Simulate a temporary cleaner incentive before any financial action.",
            "human_approval_required": True,
        })
    return actions


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
    prediction = _forecast(req.city, req.service_id, req.date)
    return {
        "city": req.city,
        "service_id": req.service_id,
        "date": req.date,
        "predicted_bookings": round(prediction, 2),
    }


@app.post("/api/v1/marketplace-decision")
def marketplace_decision(req: DecisionRequest):
    predicted = _forecast(req.city, req.service_id, req.date)
    capacity = _capacity_proxy(req.city)
    gap = predicted - capacity
    return {
        "city": req.city,
        "service_id": req.service_id,
        "date": req.date,
        "predicted_bookings": round(predicted, 2),
        "estimated_capacity_bookings": round(capacity, 2),
        "supply_demand_gap": round(gap, 2),
        "recommended_actions": _decision_from_gap(gap),
        "decision_mode": "recommendation_only",
        "note": (
            "Public-case capacity is a proxy. Production decisions must use real-time "
            "availability, confirmed bookings, service compatibility and policy checks."
        ),
    }
