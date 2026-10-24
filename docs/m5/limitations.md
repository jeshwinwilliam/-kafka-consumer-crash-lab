# Limitations

- **Fixed amount:** all application updates use amount `100`. Identity checks compare the persisted fixed amount and account ID; this does not validate variable-amount semantics.
- **Manual partition assignment:** `CrashConsumer` assigns topic partition `0`. It is not a cooperative rebalance or multi-partition consumer study.
- **Bounded no-record observation:** cases 3 and 6 use a bounded empty-poll observation. It supports the stated run outcome, not an unbounded absence claim.
- **Dedup retention:** deleting a scoped dedup row in case 12 deliberately permits another application on replay. Retention policy is application-specific and is not solved by this lab.
- **Legacy rows:** rows with unknown account or amount content are explicitly rejected. No migration supplies missing historical identity content.
- **External effects:** the lab models a PostgreSQL account update. It does not provide exactly-once delivery for arbitrary external side effects.
- **Reproduction scope:** fresh reproduction uses new containers, volumes, endpoints, and source build on the same Mac. It is not cross-platform validation.
- **Kafka durability:** the original Kafka Compose service has no explicitly declared persistent volume. Its topic/offset survival depends on container lifecycle; this was not retroactively changed.
- **Historical provenance:** campaign-era `compose.m4-fresh.yaml` bytes are unavailable; the original temporary snapshot output was removed. Current corrected fresh configuration is not represented as a byte match to that historical Compose file.
- **Fresh 10–12:** historical fresh cases 10–12 are unverified-isolation because their controller hard-coded original Compose Docker commands. Corrected v2 replacements use explicit fresh endpoints/project and are separate executions.
- **Tests:** four passing test methods provide focused checks, including identity validation. They do not demonstrate exhaustive correctness.
