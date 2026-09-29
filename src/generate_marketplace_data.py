from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data"
RNG = np.random.default_rng(42)

CITIES = ["Helsinki", "Espoo", "Vantaa", "Järvenpää", "Kerava"]
SERVICES = ["home_cleaning", "deep_cleaning", "move_out_cleaning"]
APARTMENT_SIZES = ["1-2_rooms", "3_rooms", "4_plus_rooms"]

def main(n_bookings: int = 12000, n_cleaners: int = 180) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cleaners = pd.DataFrame({
        "cleaner_id": [f"cln_{i:04d}" for i in range(1, n_cleaners + 1)],
        "city": RNG.choice(CITIES, n_cleaners, p=[0.38, 0.24, 0.20, 0.10, 0.08]),
        "rating": np.clip(RNG.normal(4.55, 0.28, n_cleaners), 3.2, 5.0).round(2),
        "base_hourly_price_cents": RNG.integers(2800, 5200, n_cleaners),
        "reliability_score": np.clip(RNG.normal(0.92, 0.06, n_cleaners), 0.65, 0.999).round(3),
        "weekly_capacity_minutes": RNG.integers(900, 2400, n_cleaners),
    })

    start = pd.Timestamp("2026-01-01", tz="Europe/Helsinki")
    created = start + pd.to_timedelta(RNG.integers(0, 240 * 24 * 60, n_bookings), unit="m")
    lead_hours = np.clip(RNG.gamma(2.2, 28, n_bookings), 2, 24 * 21)
    scheduled = created + pd.to_timedelta(lead_hours, unit="h")
    city = RNG.choice(CITIES, n_bookings, p=[0.40, 0.25, 0.19, 0.09, 0.07])
    service = RNG.choice(SERVICES, n_bookings, p=[0.72, 0.17, 0.11])
    apartment = RNG.choice(APARTMENT_SIZES, n_bookings, p=[0.44, 0.33, 0.23])
    duration = np.select(
        [apartment == "1-2_rooms", apartment == "3_rooms"],
        [RNG.integers(90, 181, n_bookings), RNG.integers(150, 241, n_bookings)],
        default=RNG.integers(210, 361, n_bookings),
    )
    cleaner_idx = RNG.integers(0, n_cleaners, n_bookings)
    cleaner_id = cleaners.iloc[cleaner_idx]["cleaner_id"].to_numpy()
    cleaner_price = cleaners.iloc[cleaner_idx]["base_hourly_price_cents"].to_numpy()
    cleaner_rating = cleaners.iloc[cleaner_idx]["rating"].to_numpy()
    reliability = cleaners.iloc[cleaner_idx]["reliability_score"].to_numpy()

    addon_cents = RNG.choice([0, 500, 900, 1200, 1800], n_bookings, p=[0.55, 0.16, 0.12, 0.10, 0.07])
    subtotal = np.rint(cleaner_price * (duration / 60.0)).astype(int) + addon_cents
    total = np.rint(subtotal * 1.255).astype(int) + 250

    weekend = scheduled.dayofweek >= 5
    evening = scheduled.hour >= 16
    cancel_logit = -2.6 + 0.45 * weekend + 0.3 * evening + 0.7 * (lead_hours > 168) - 1.3 * (reliability - 0.8)
    cancel_prob = 1 / (1 + np.exp(-cancel_logit))
    cancelled = RNG.random(n_bookings) < cancel_prob
    status = np.where(cancelled, "cancelled", "completed")
    rating = np.where(status == "completed", np.clip(np.rint(RNG.normal(cleaner_rating, 0.55)), 1, 5), np.nan)

    bookings = pd.DataFrame({
        "booking_id": [f"bkg_{i:06d}" for i in range(1, n_bookings + 1)],
        "cleaner_id": cleaner_id,
        "city": city,
        "service_id": service,
        "apartment_size_id": apartment,
        "created_at": created.astype(str),
        "start_time": scheduled.astype(str),
        "duration_min": duration.astype(int),
        "total_cents": total.astype(int),
        "status": status,
        "rating_stars": rating,
    })
    cleaners.to_csv(OUT / "cleaners.csv", index=False)
    bookings.to_csv(OUT / "bookings.csv", index=False)
    print(f"Wrote {len(cleaners)} cleaners and {len(bookings)} synthetic bookings")

if __name__ == "__main__":
    main()
