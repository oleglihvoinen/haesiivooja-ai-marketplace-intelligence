import pandas as pd
from src.feature_pipeline import build_demand_features, build_cleaner_features

def test_demand_features_have_expected_columns():
    bookings = pd.DataFrame([
        {"booking_id":"b1","cleaner_id":"c1","city":"Helsinki","service_id":"home_cleaning","start_time":"2026-01-01T10:00:00Z","duration_min":120,"total_cents":5000,"status":"completed","rating_stars":5},
        {"booking_id":"b2","cleaner_id":"c1","city":"Helsinki","service_id":"home_cleaning","start_time":"2026-01-01T15:00:00Z","duration_min":90,"total_cents":4200,"status":"cancelled","rating_stars":None},
    ])
    out = build_demand_features(bookings)
    assert out.loc[0, "bookings"] == 2
    assert out.loc[0, "cancelled"] == 1
    assert "dow_sin" in out.columns

def test_cleaner_features_completion_rate():
    cleaners = pd.DataFrame([{
        "cleaner_id":"c1","city":"Helsinki","rating":4.8,
        "base_hourly_price_cents":3500,"reliability_score":0.96,
        "weekly_capacity_minutes":1800
    }])
    bookings = pd.DataFrame([
        {"booking_id":"b1","cleaner_id":"c1","status":"completed","rating_stars":5,"duration_min":120,"total_cents":5000},
        {"booking_id":"b2","cleaner_id":"c1","status":"cancelled","rating_stars":None,"duration_min":90,"total_cents":4200},
    ])
    out = build_cleaner_features(cleaners, bookings)
    assert out.loc[0, "completion_rate"] == 0.5
