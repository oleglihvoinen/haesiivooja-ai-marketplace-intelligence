# Real-Time Architecture

## Objective

Turn live HaeSiivooja marketplace activity into governed data, predictions and controlled operational recommendations while preserving a clear boundary between **AI recommendation** and **business action authorization**.

## Closed-loop design

**Observe → Predict → Recommend → Approve → Act → Measure → Improve**

1. **SaaS event capture** — bookings, searches, cleaner availability, service changes, ratings and payment outcomes originate in the web, Android and iOS product.
2. **Operational system of record** — MySQL remains authoritative for transactional state.
3. **CDC and streaming** — Debezium captures committed database changes and publishes versioned event streams to Kafka.
4. **Bronze history** — append-only event history preserves source changes and replay capability.
5. **Silver marketplace model** — events are cleaned, deduplicated and mapped into canonical booking, cleaner, service, availability and outcome entities.
6. **Gold metrics & features** — governed business metrics and reusable ML features are produced from the conformed model.
7. **ML models** — demand forecasting, cleaner ranking and future anomaly models consume governed features rather than raw production tables.
8. **Semantic & governance layer** — definitions such as Booking GMV, Cancellation Rate and Supply Utilization remain consistent across BI, APIs and AI.
9. **AI decision service** — forecast and supply signals are translated into explainable recommendations.
10. **Policy and human approval** — interventions are checked against business rules and approval requirements before execution.
11. **Action APIs** — approved campaigns, notifications, matching changes or other operational actions are invoked through explicit APIs.
12. **Outcome feedback** — conversions, availability responses, completed work, cancellations and quality outcomes return as events for evaluation.

## Current public implementation

The repository implements the synthetic data pipeline, feature engineering, forecasting, ranking, semantic contracts, prediction APIs and a recommendation-only marketplace decision endpoint.

The public decision endpoint estimates capacity with a reproducible proxy. It is intentionally not presented as production capacity planning: a deployed system must use real-time cleaner availability, blocked periods, confirmed bookings, service compatibility and travel constraints.

## Streaming boundary

The `streaming/` directory contains a Debezium MySQL connector example. The `events/` directory contains a versioned booking-event schema.

A production deployment should also add:

- schema compatibility enforcement
- dead-letter handling
- idempotent downstream processing
- Kafka consumer lag monitoring
- replay/runbook procedures
- secrets management
- environment-specific connector deployment

## Data-platform mapping

The logical Bronze/Silver/Gold boundaries are platform-independent.

### Snowflake/dbt
Kafka or Snowflake ingestion → RAW/Bronze → dbt staging/conformed Silver → Gold marts/features → semantic metrics.

### Microsoft Fabric
Kafka/Eventstream or Data Factory → OneLake/Lakehouse Bronze → PySpark/Delta Silver → governed Gold → Power BI / APIs / AI.

## Decision governance

High-impact actions must not be triggered simply because a model score crosses a threshold. The decision boundary should evaluate:

- action type and financial impact
- forecast/model confidence
- supply-demand gap
- cleaner/customer impact
- business rules
- rate/frequency limits
- required human approval
- audit metadata and provenance

The public implementation returns recommendations and approval flags; it does not execute campaigns or financial incentives autonomously.

## Observability

Production controls should cover data freshness, schema drift, event lag, data-quality failures, feature freshness, model drift, API latency, recommendation volume, approval rate and measured outcome.

## Privacy

The public implementation contains no real customer names, exact addresses, emails, phone numbers, Stripe identifiers or payment methods. Production analytics should use pseudonymous identifiers, isolate PII, enforce retention policies and support GDPR access/deletion workflows.
