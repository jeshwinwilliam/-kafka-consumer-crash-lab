# Editorial handoff

This note maps bounded educational claims to inspectable implementation and evidence. It is not article copy and does not claim general exactly-once processing.

| Proposed claim | Code to inspect | Evidence to cite | Editorial boundary |
|---|---|---|---|
| A DB commit before an offset commit can replay a durable update after a kill | `CrashConsumer`, `DatabaseWork`, db-first diagram | campaign case 2 and its snapshots/logs | State this as the lab’s single-record PostgreSQL observation. |
| An offset commit before DB work can skip DB processing after a kill | `CrashConsumer` offset-first branch | campaign case 3 and bounded no-record evidence | Do not call bounded observation permanent proof. |
| A dedup row can prevent a replayed update when retained | `DatabaseWork.begin` dedup branch | cases 4, 6, 7, 8 | Retention determines the scope of this result. |
| A pre-commit failure rolls back dedup and account update | `DatabaseWork.begin` catch/rollback; consumer barrier | campaign case 5 raw process/snapshot evidence | Distinguish transaction rollback from external-effect rollback. |
| Duplicate races were observed at the database | `M3ConcurrencyHarness` | case 8/9 raw observer output and PID/blocker fields | Require `pg_blocking_pids(B)` containing A before release. |
| Mismatched identity content is rejected | `DatabaseWork.begin`, `DedupPostgresTest` | test report and source | Fixed amount=100 only; do not generalize to arbitrary payload schemas. |
| Isolated same-Mac reproduction exists | `compose.m4-fresh.yaml`, `LabConfig`, corrected v2 controller | fresh case records and Compose identities | Do not describe it as cross-platform or independent third-party validation. |

Before publication, editorial review should inspect the supplemental archive checksum, `REVIEW_MAPPING.json`, `ARCHIVE_AUDIT.json`, and `GAP_REPORT.json`. Keep the stated provenance limitations in any prose using M4 results.
