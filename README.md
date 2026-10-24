# Kafka crash-window laboratory

> **Local public-release candidate, not published.** This candidate packages the
> reviewed lab source and an unchanged evidence archive for review only. It has
> no public repository, release, or immutable public URL yet. See
> `PUBLICATION-BLOCKERS.md` before any upload.

This educational lab makes Kafka consumer/database crash windows observable. It uses a single manually assigned Kafka partition, PostgreSQL, explicit consumer-group offsets, and a fixed credit amount of `100`.

The tested campaign runtime was Homebrew OpenJDK **21.0.12.1**. Do not substitute a newer JDK with `--release 21`: the consumer and controller processes must execute on Java 21.

## Prerequisites

- Docker Desktop with `docker compose`
- Homebrew `openjdk@21` and Maven 3.9.x
- Python 3 for the standard-library controllers; Python 3.14.4 is the recorded campaign runtime, not an asserted minimum supported version
- Local ports `9092`, `5433` for the original environment; `19092`, `15433` for the fresh environment

Select Java 21 in every shell that builds or launches Java:

```bash
export JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
java -version
javac -version
mvn -version
```

All three version commands should identify Java 21.

## Service setup, schema, build, and test

`DedupPostgresTest` calls `DatabaseWork.open()` and therefore requires PostgreSQL and the lab schema. Start and inspect services **before** testing.

```bash
# Inspect first; do not recreate existing containers or data.
docker compose -f compose.yaml config
docker compose -f compose.yaml ps
docker compose -f compose.yaml up -d --wait --wait-timeout 180
```

The original Compose file does not mount initialization SQL. For a deliberately new original-environment database, initialize its schema before tests:

```bash
docker compose -f compose.yaml exec -T postgres \
  psql -U crashlab -d crashlab < sql/000_base_schema.sql
docker compose -f compose.yaml exec -T postgres \
  psql -U crashlab -d crashlab < sql/001_processed_events_identity.sql
```

Do not apply those files blindly to an existing database; inspect its schema and data first. With PostgreSQL available and schema initialized, build, test, and create the runtime dependency classpath:

```bash
JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home" \
PATH="$JAVA_HOME/bin:$PATH" \
mvn clean test dependency:copy-dependencies -DincludeScope=runtime
```

The current-root controller classpath is `target/classes:target/dependency/*`. The frozen M4 evidence records four passing test methods; that is useful regression coverage, not exhaustive correctness proof.

## Original environment

The commands above establish the original environment: Kafka at `localhost:9092` and PostgreSQL at `localhost:5433`. Java defaults to those endpoints when `CRASHLAB_KAFKA_BOOTSTRAP` and `CRASHLAB_JDBC_URL` are unset.

## Individual scenarios

With Java 21 selected and the original environment running:

```bash
python3 scripts/run_m2.py 1a  # database-first baseline
python3 scripts/run_m2.py 1b  # offset-first baseline
python3 scripts/run_m2.py 1c  # dedup database-first baseline
python3 scripts/run_m2.py 2   # db-first, post-DB-commit crash
python3 scripts/run_m2.py 3   # offset-first, post-offset-commit crash
python3 scripts/run_m2.py 4   # dedup, post-DB-commit crash
python3 scripts/run_m2.py 5   # dedup, pre-DB-commit crash
python3 scripts/run_m2.py 6   # dedup, post-both-commits crash
python3 scripts/run_m3_case7.py
java -cp 'target/classes:target/dependency/*' com.jeshwin.crashlab.M3ConcurrencyHarness commit manual-case8
java -cp 'target/classes:target/dependency/*' com.jeshwin.crashlab.M3ConcurrencyHarness rollback manual-case9
python3 scripts/run_m3_remaining.py 10
python3 scripts/run_m3_remaining.py 11
python3 scripts/run_m3_remaining.py 12
```

`run_m3_remaining.py` is historical and hard-codes `compose.yaml`; it is valid only for the original environment. For isolated fresh replacements of cases 10–12, use the versioned controller in [docs/m5/reproduction.md](docs/m5/reproduction.md).

Most controllers write a unique directory under `results/`. Direct `M3ConcurrencyHarness` invocations only emit NDJSON to stdout: give every run a unique ID and capture stdout, stderr, and exit status explicitly, for example `run_id=manual-case8-$(date +%Y%m%dT%H%M%S); java -cp 'target/classes:target/dependency/*' com.jeshwin.crashlab.M3ConcurrencyHarness commit "$run_id" > "results/$run_id.stdout.ndjson" 2> "results/$run_id.stderr.log"; printf '%s\n' "$?" > "results/$run_id.exit-status.txt"`. Preserve failed or invalid outputs too.

## Documentation and reviewed evidence

- [Reproduction guide](docs/m5/reproduction.md)
- [Commit-boundary diagrams](docs/m5/commit-boundaries.md)
- [Results matrix](docs/m5/results-matrix.md)
- [Evidence guide](docs/m5/evidence-guide.md)
- [Limitations](docs/m5/limitations.md)
- [Editorial handoff](docs/m5/editorial-handoff.md)
- [Evidence index](EVIDENCE-INDEX.md)
- [Local release notes](RELEASE-NOTES.md)
- [Publication blockers](PUBLICATION-BLOCKERS.md)

The reviewed supplemental archive is intentionally stored at
`evidence/m4-supplemental-review-corrected.tar.gz`. Its SHA-256 is recorded in
the adjacent `.sha256` file and in `EVIDENCE-INDEX.md`. It is preserved
byte-for-byte for review and is **not** ready for public upload until the
privacy blockers are resolved.
