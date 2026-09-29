from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def build_demand_features(bookings: pd.DataFrame) -> pd.DataFrame:
    df = bookings.copy()
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True, format="mixed")
    df["date"] = df["start_time"].dt.floor("D")
    daily = (
        df.groupby(["date", "city", "service_id"], as_index=False)
          .agg(
              bookings=("booking_id", "count"),
              completed=("status", lambda s: int((s == "completed").sum())),
              cancelled=("status", lambda s: int((s == "cancelled").sum())),
              booked_minutes=("duration_min", "sum"),
              gross_value_cents=("total_cents", "sum"),
          )
    )
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["week_of_year"] = daily["date"].dt.isocalendar().week.astype(int)
    daily["month"] = daily["date"].dt.month
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)
    daily["dow_sin"] = np.sin(2 * np.pi * daily["day_of_week"] / 7)
    daily["dow_cos"] = np.cos(2 * np.pi * daily["day_of_week"] / 7)
    daily["cancellation_rate"] = daily["cancelled"] / daily["bookings"].clip(lower=1)
    return daily.sort_values(["date", "city", "service_id"]).reset_index(drop=True)

def build_cleaner_features(cleaners: pd.DataFrame, bookings: pd.DataFrame) -> pd.DataFrame:
    stats = (
        bookings.groupby("cleaner_id", as_index=False)
        .agg(
            jobs=("booking_id", "count"),
            completed_jobs=("status", lambda s: int((s == "completed").sum())),
            avg_customer_rating=("rating_stars", "mean"),
            booked_minutes=("duration_min", "sum"),
            gross_value_cents=("total_cents", "sum"),
        )
    )
    out = cleaners.merge(stats, on="cleaner_id", how="left").fillna({
        "jobs": 0, "completed_jobs": 0, "avg_customer_rating": 0,
        "booked_minutes": 0, "gross_value_cents": 0,
    })
    out["completion_rate"] = out["completed_jobs"] / out["jobs"].clip(lower=1)
    out["utilization_proxy"] = (out["booked_minutes"] / (34 * out["weekly_capacity_minutes"])).clip(0, 1)
    return out

def main() -> None:
    bookings = pd.read_csv(ROOT / "data" / "bookings.csv")
    cleaners = pd.read_csv(ROOT / "data" / "cleaners.csv")
    build_demand_features(bookings).to_csv(ROOT / "data" / "demand_features.csv", index=False)
    build_cleaner_features(cleaners, bookings).to_csv(ROOT / "data" / "cleaner_features.csv", index=False)
    print("Feature tables built")

if __name__ == "__main__":
    main()
