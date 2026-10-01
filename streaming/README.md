# Real-Time Streaming Boundary

This directory documents the production CDC/event-streaming boundary for the HaeSiivooja decision platform.

The public repository does **not** connect to the production HaeSiivooja database. The connector configuration is an environment-neutral example showing how committed MySQL changes can be captured by Debezium and published to Kafka.

## Flow

`MySQL → Debezium CDC → Kafka → Bronze event history → Silver marketplace model`

The example connector includes only marketplace tables relevant to the case. Production deployment should use secrets management, least-privilege CDC credentials, TLS, schema compatibility controls, monitoring, dead-letter handling and environment-specific topic/configuration management.
