# CipherNest — Design Changes from Assignment 01

This log records every deviation from the architecture approved in
Assignment 01, as required by Assignment 02 (changes must be explained and
justified on camera in the Member 4 / Integration segment, and Member 1
should be able to speak to the architectural ones).

| # | Change | Reason | Why it still satisfies the approved design |
|---|--------|--------|----------------------------------------------|
| 1 | Dropped PostgreSQL; the flag-validator and platform now share a single SQLite database instead of a separate Postgres service. | One-day build window. A standalone Postgres service adds a connection-config/startup-ordering failure class with no marking benefit — the rubric asks for a flag validation *mechanism* (challenge ID, expected hash, submission, result, logging, basic rate limiting), not a specific database engine. | All required fields (challenge ID, expected SHA-256 hash, submitted flag, result, timestamp, basic logging/rate limiting) are still implemented, just on SQLite. The three-layer architecture (participant → control layer → challenge layer) is unchanged. |
| 2 | Dropped the separate "Logging Service" container; logs are written to stdout and read via `docker compose logs <service>`. | Same reason — a log-aggregation container (e.g. a Loki/Fluentd stack) is infrastructure the rubric does not require and that a one-day build cannot afford to debug. | Every service still produces timestamped logs that are inspectable and can be shown live during the demo (`docker compose logs -f`), satisfying "logging" as a security/observability control. |
| 3 | Flag-validator logic is implemented as routes inside the same Flask app as the platform, rather than as its own container/service. | Reduces the number of Dockerfiles, images, and inter-service network calls to debug under time pressure. | Functionally identical: flags are still validated server-side against stored hashes, never on the participant's machine, and the validation code is logically separated into its own module (`platform/app/validator.py`, added Phase 9) even though it runs in the same container. |

_(This file will be updated if further changes are made in later phases — e.g. any change to the CN05 network design if the FTP passive-port range causes problems.)_
