# HaeSiivooja AI Marketplace Intelligence Platform

A full-stack **AI + data engineering case** built around the operating model of a two-sided cleaning-services SaaS marketplace. The platform turns booking, availability, service, pricing and quality signals into demand forecasts, cleaner-ranking decisions and governed marketplace metrics.

> The domain model is based on HaeSiivooja marketplace flows. The public implementation uses **synthetic/anonymized data** and contains no customer PII, exact addresses, Stripe identifiers or payment credentials.

![HaeSiivooja AI Marketplace Intelligence architecture](docs/architecture-v2.png)

## Summary

Marketplace products have a difficult data problem: demand changes by time and location, supply is constrained by individual availability, and the best match is not simply the cheapest provider. A useful AI system therefore has to combine **transactional data engineering, temporal features, marketplace metrics, predictive models, ranking logic, operational APIs and governance**.

This case implements that end-to-end pattern.

## Business capabilities

- forecast booking demand by city, service and date
- rank eligible cleaners using quality, reliability, distance, price and utilization signals
- expose AI decisions through FastAPI
- publish governed marketplace metrics such as GMV, cancellation rate and supply utilization
- preserve a clear boundary between operational SaaS data, analytical features and decision services
- demonstrate a privacy-safe path from a real product domain to public AI engineering work

## Architecture

**HaeSiivooja web/mobile SaaS** → bookings / availability / services / ratings / payment outcomes → analytical event history → standardized marketplace entities → Gold metrics & feature tables → **Demand Forecast + Cleaner Ranker** → FastAPI → customer/cleaner experiences + operations.

A production cloud implementation can map the same logical design to **MySQL CDC → Debezium/Kafka → Snowflake/dbt** or **Microsoft Fabric / OneLake / Lakehouse**.

## Real HaeSiivooja domain alignment

The source product already contains the business concepts required for this platform: cleaners, bookings, recurring/blocked availability, services, apartment size, locations, ratings, pricing/duration, booking status and Stripe-connected payment flows. The public dataset generator reproduces these analytical shapes without exposing production records.

## Data products

### Marketplace demand feature table
Daily city/service grain with booking volume, completed/cancelled counts, booked minutes, GMV proxy, calendar features and cancellation rate.

### Cleaner feature table
Per-cleaner quality and capacity signals: rating, reliability, completion rate, booked minutes, utilization proxy, price and historical marketplace value.

### Governed metric contracts
Machine-readable definitions for Booking GMV, Completed Bookings, Cancellation Rate and Supply Utilization.

## AI models

### Demand forecasting
A gradient-boosted regression pipeline predicts booking demand by city, service and calendar context. The training workflow uses a chronological holdout rather than a random split.

### Marketplace match ranking
A gradient-boosted classifier produces a match probability from distance, relative price, rating, reliability, completion rate and utilization. A separate quality guardrail contributes to the final ranking score.

The public ranking labels are synthetic, so model metrics demonstrate the engineering workflow rather than real HaeSiivooja marketplace performance.

## Decision API

- `GET /health`
- `POST /api/v1/demand-forecast`
- `POST /api/v1/match`

The API layer keeps models behind stable service contracts suitable for integration into web/mobile SaaS experiences.

## Privacy & governance

- no real names, emails, phone numbers or addresses
- no Stripe customer/payment/account identifiers
- synthetic cleaner and booking IDs
- city-level location only
- metric definitions have explicit ownership
- production architecture should separate PII from analytical identifiers and enforce GDPR retention/access policies

## Run locally

```bash
python -m pip install -r requirements.txt
make all
uvicorn api.main:app --reload
```

**Technologies:** Python · Pandas · scikit-learn · FastAPI · Pydantic · feature engineering · demand forecasting · ranking · semantic metrics · marketplace analytics · CI/CD · MySQL CDC/Kafka/Snowflake/Fabric-ready architecture
