# Commit-boundary sequence diagrams

These diagrams reflect `CrashConsumer.run` and `DatabaseWork.begin`, not a generic delivery model. The consumer manually assigns partition `0`, disables auto-commit, seeks to the preinitialized committed offset, and processes at most one record.

## Database-first

```mermaid
sequenceDiagram
  participant K as Kafka record r
  participant C as CrashConsumer
  participant D as PostgreSQL
  C->>K: poll r at committed offset
  C->>D: BEGIN; UPDATE accounts +100
  D-->>C: work connection
  C->>D: COMMIT
  C->>C: DB_COMMITTED marker
  Note over C: after-db-commit barrier can pause here
  C->>K: commitSync(next offset)
  C->>C: OFFSET_COMMITTED marker
```

A kill at the barrier leaves balance `+100` durable and the group at the record offset; replay can apply again.

## Offset-first

```mermaid
sequenceDiagram
  participant K as Kafka record r
  participant C as CrashConsumer
  participant D as PostgreSQL
  C->>K: poll r
  C->>K: commitSync(next offset)
  C->>C: OFFSET_COMMITTED marker
  Note over C: after-offset-commit barrier can pause here
  C->>D: BEGIN; UPDATE accounts +100
  C->>D: COMMIT
  C->>C: DB_COMMITTED marker
```

A kill at this barrier advances the Kafka position before database work; bounded no-record observation is used after restart.

## Dedup database-first

```mermaid
sequenceDiagram
  participant K as Kafka record r
  participant C as CrashConsumer
  participant D as PostgreSQL
  C->>K: poll r
  C->>D: BEGIN; INSERT processed_events ON CONFLICT DO NOTHING RETURNING
  alt row inserted
    C->>D: UPDATE accounts +100
  else duplicate
    C->>D: compare persisted account and fixed amount=100
  end
  Note over C,D: before-db-commit barrier may pause
  C->>D: COMMIT
  C->>C: DB_COMMITTED marker
  Note over C: after-db-commit barrier may pause
  C->>K: commitSync(next offset)
  Note over C: after-both-commits barrier may pause
```

The content comparison rejects mismatched account/amount and unknown legacy content. It does not establish support for variable amounts: the implemented amount is fixed at `100`.
