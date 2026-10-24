# Results matrix

This matrix summarizes evidence categories; it does not replace the linked raw records. “Initial” refers to one early isolated execution. “Coverage” is the separate seven-run frozen-source set. “Fresh” is a same-Mac independently named Compose environment. Campaign counts are new M4 trials only.

| Case | Expected observation | Initial evidence | M4 campaign | Frozen coverage | Fresh evidence / disposition |
|---|---|---:|---:|---:|---|
| 1A | db-first baseline: balance 0→100; offset advances | yes | — | yes | retained historical fresh |
| 1B | offset-first baseline: balance 0→100; offset advances | yes | — | yes | retained historical fresh |
| 1C | dedup-db-first baseline: balance 0→100; dedup row; offset advances | yes | — | yes | retained historical fresh |
| 2 | db-first post-DB-commit crash: replay applies again | yes | 10 pass | — | retained historical fresh |
| 3 | offset-first post-offset crash: no DB work after restart | yes | 10 pass | — | retained historical fresh |
| 4 | dedup post-DB-commit crash: replay is skipped | yes | 10 pass | — | retained historical fresh |
| 5 | dedup pre-DB-commit crash: rollback then one application | yes | 10 pass | — | retained historical fresh; campaign case-5 raw kill/rollback evidence retained |
| 6 | dedup post-both-commit crash: bounded no-record observation | yes | 10 pass | — | retained historical fresh |
| 7 | same event at two offsets: one application | yes | — | yes | retained historical fresh |
| 8 | overlapping duplicate commit: first applies, second skips | yes | 20 pass | — | normalized fresh case-8 raw contention record retained |
| 9 | overlapping duplicate rollback: second applies | yes | 20 pass | — | normalized fresh case-9 raw contention record retained |
| 10 | absent account: rollback, no dedup, unchanged observed offset | yes | — | yes | earlier fresh run **unverified-isolation**; corrected fresh v2 pass |
| 11 | two event IDs: balance 200, two scoped dedup rows, offset beyond both | yes | — | yes | earlier fresh run **unverified-isolation**; corrected fresh v2 pass |
| 12 | remove this run’s dedup row then replay: 100→200 | yes | — | yes | earlier fresh run **unverified-isolation**; corrected fresh v2 pass |

The campaign has 90 records: cases 2–6 have 10 each; cases 8–9 have 20 each. Counts are repeatability observations on one frozen implementation, not statistical proof.

The corrected fresh v2 replacement records are:

- `m4-fresh-corrected-v2-case10-3f540cdebbb9`
- `m4-fresh-corrected-v2-case11-2b996f4628f5`
- `m4-fresh-corrected-v2-case12-943aca3e6259`

The 14-execution final fresh set is composed of retained historical cases 1A–9 and these three replacements. The three older fresh 10–12 directories are preserved as historical but excluded from fresh-isolation claims.
