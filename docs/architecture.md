# Architecture

## Business objective

Turn marketplace activity into operational intelligence that improves the balance between customer demand and cleaner supply while providing a governed foundation for AI-assisted marketplace operations.

## End-to-end design

**Transactional web/mobile SaaS** → booking/payment/availability signals → analytical event history → standardized marketplace entities → **Gold marketplace metrics & feature tables** → demand forecasting + cleaner ranking → FastAPI decision services → customer/cleaner applications and operations.

For cloud deployment, the same boundaries map cleanly to **MySQL CDC → Debezium/Kafka → Snowflake/dbt** or **Microsoft Fabric / OneLake / Lakehouse**. The public project remains locally reproducible and requires no production credentials.

## Data engineering layer

The transactional system remains the system of record. Analytical pipelines produce privacy-safe identifiers, temporal booking features, cleaner capacity/quality features and governed marketplace aggregates. Production ingestion would be incremental and idempotent, with event offsets or watermarks tracked explicitly.

## AI services

### Demand forecasting
Forecast daily booking demand by city and service. Operational uses include cleaner acquisition, availability nudges, campaign timing and capacity planning.

### Cleaner ranking
Rank already-eligible cleaners using relative price, distance/travel proxy, customer rating, reliability, historical completion and utilization. Availability and service compatibility remain hard constraints outside model ranking.

## Governance

Metrics such as Booking GMV, Completed Bookings, Cancellation Rate and Supply Utilization have explicit definitions and owners. This provides a stable semantic boundary for dashboards and future AI/data-agent tooling.

## Privacy

The public implementation contains no real customer identities, exact addresses, emails, phone numbers, Stripe identifiers or payment methods. Synthetic IDs and city-level geography are sufficient to demonstrate the architecture. A production implementation should isolate PII, minimize analytical exposure, define retention rules and enforce GDPR access controls.
