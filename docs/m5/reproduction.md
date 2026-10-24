# Reproduction guide

## Prerequisites and order

Use a shell with Java 21 selected. Python controllers use only the Python standard library (`datetime`, `hashlib`, `json`, `os`, `pathlib`, `subprocess`, `sys`, `uuid`, and related standard modules). Python 3.14.4 is recorded in the campaign manifest; this guide does not claim Python 3.14 as a minimum supported version.

`DedupPostgresTest` requires a live PostgreSQL database with the lab schema. Start services and initialize schema before running Maven tests.

## Original environment

The original project is named `kafka-crash-lab` by `compose.yaml`. Its host endpoints are Kafka `localhost:9092` and PostgreSQL `localhost:5433`. Java defaults to these endpoints through `LabConfig`; leave `CRASHLAB_KAFKA_BOOTSTRAP` and `CRASHLAB_JDBC_URL` unset when intentionally operating on the original environment.

```bash
docker compose -f compose.yaml config
docker compose -f compose.yaml ps
docker compose -f compose.yaml up -d --wait --wait-timeout 180
# Only for a deliberately new original-environment database:
docker compose -f compose.yaml exec -T postgres psql -U crashlab -d crashlab < sql/000_base_schema.sql
docker compose -f compose.yaml exec -T postgres psql -U crashlab -d crashlab < sql/001_processed_events_identity.sql
export JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
mvn clean test dependency:copy-dependencies -DincludeScope=runtime
```

Use `docker compose -f compose.yaml exec -T ...` for inspections. Do not use `down -v`, `prune`, or broad cleanup commands when preserving historical lab data.

## Isolated fresh environment

The fresh configuration is intentionally separate. It uses project `kafka-crash-lab-m4fresh`, container DNS `kafka:9092` for the internal listener, host Kafka `localhost:19092` for Java clients, and PostgreSQL `localhost:15433`.

```bash
export M4_KAFKA_PORT=19092
export M4_POSTGRES_PORT=15433
export CRASHLAB_KAFKA_BOOTSTRAP=localhost:19092
export CRASHLAB_JDBC_URL='jdbc:postgresql://localhost:15433/crashlab?connectTimeout=10&socketTimeout=10'
docker compose -p kafka-crash-lab-m4fresh -f compose.m4-fresh.yaml config
docker compose -p kafka-crash-lab-m4fresh -f compose.m4-fresh.yaml up -d --wait --wait-timeout 180
docker compose -p kafka-crash-lab-m4fresh -f compose.m4-fresh.yaml ps
```

`compose.m4-fresh.yaml` configures Kafka 4.1.2 with `INTERNAL://kafka:9092`, `EXTERNAL://localhost:19092`, and the separate KRaft `CONTROLLER://kafka:9093`. Its health check uses `kafka:9092`; host-side Java uses `localhost:19092`. The fresh PostgreSQL service initializes from the two SQL files only when its fresh named volume is first created.

## Reconstructing the corrected 10–12 build layout

`run_m4_fresh_10_12_v2.py` is intentionally historical-controller-compatible and hard-codes this relative build location:

```text
results/m4/rebuilt-frozen-source-20261017b/source/target/classes
results/m4/rebuilt-frozen-source-20261017b/source/target/dependency/*
```

From a new checkout, obtain the reviewed M4 supplemental archive, verify its checksum, extract it, and copy its preserved rebuilt-source directory into that exact layout. The archive-relative source is `provenance/rebuilt-frozen-source-20261017b/`.

```bash
# Run from the candidate root. The bundled archive is review-only and must be
# verified before use.
export M4_ARCHIVE="$PWD/evidence/m4-supplemental-review-corrected.tar.gz"
(cd evidence && shasum -a 256 -c m4-supplemental-review-corrected.tar.gz.sha256)
tar -xzf "$M4_ARCHIVE"
mkdir -p results/m4
cp -R supplemental-review-corrected/provenance/rebuilt-frozen-source-20261017b \
  results/m4/rebuilt-frozen-source-20261017b
export BUILD="$PWD/results/m4/rebuilt-frozen-source-20261017b/source"
export JAVA_HOME="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
cd "$BUILD"
# Fresh environment variables remain exported from the preceding section.
mvn clean test dependency:copy-dependencies -DincludeScope=runtime | tee ../new-reproduction-build.log
find target/classes target/dependency -type f -print0 | sort -z | xargs -0 shasum -a 256 > ../new-reproduction-artifact-hashes.sha256
cd -
```

Record the source/archive checksum and the new artifact-hash file. This is a **new reproduction build** of the preserved source layout. It is not the removed original temporary snapshot output and must not be presented as historical artifacts. The preserved `build.log`, `environment.txt`, and `artifact-hashes.sha256` remain comparison evidence only.

## Complete fresh-suite sequence

With the fresh services running, variables exported, and `BUILD` prepared as above, use the snapshot build classpath for fresh cases 1A–9. These scripts inherit `CRASHLAB_KAFKA_BOOTSTRAP` and `CRASHLAB_JDBC_URL`.

```bash
# 1A–6; create the parent because the preserved scripts use mkdir() without parents=True.
mkdir -p "$BUILD/results"
python3 "$BUILD/scripts/run_m2.py" 1a
python3 "$BUILD/scripts/run_m2.py" 1b
python3 "$BUILD/scripts/run_m2.py" 1c
python3 "$BUILD/scripts/run_m2.py" 2
python3 "$BUILD/scripts/run_m2.py" 3
python3 "$BUILD/scripts/run_m2.py" 4
python3 "$BUILD/scripts/run_m2.py" 5
python3 "$BUILD/scripts/run_m2.py" 6
# Case 7
python3 "$BUILD/scripts/run_m3_case7.py"
# Cases 8–9: capture direct harness output and exit status.
export CP="$BUILD/target/classes:$BUILD/target/dependency/*"
for mode_case in 'commit 8' 'rollback 9'; do
  set -- $mode_case; mode=$1; n=$2; run_id="fresh-case${n}-$(date +%Y%m%dT%H%M%S)"
  "$JAVA_HOME/bin/java" -cp "$CP" com.jeshwin.crashlab.M3ConcurrencyHarness "$mode" "$run_id" > "$BUILD/results/$run_id.stdout.ndjson" 2> "$BUILD/results/$run_id.stderr.log"
  printf '%s\n' "$?" > "$BUILD/results/$run_id.exit-status.txt"
done
# Corrected replacements 10–12; this controller must run from checkout root.
cd /path/to/new-checkout
python3 scripts/run_m4_fresh_10_12_v2.py 10
python3 scripts/run_m4_fresh_10_12_v2.py 11
python3 scripts/run_m4_fresh_10_12_v2.py 12
```

The final three commands deliberately use the separately identified v2 controller and its hard-coded `BUILD` layout. Do not redirect or modify the historical `run_m3_remaining.py`; it hard-codes the original Compose file and remains unsuitable for fresh-isolation claims.

## Evidence and scoped cleanup

Inspect rather than delete historical evidence:

```bash
find results/m4/fresh-corrected-v2 -name result.json -print
python3 -m json.tool results/m4/supplemental-review-corrected/ARCHIVE_AUDIT.json
```

Case 12 intentionally deletes only its own `processed_events` row and resets only its own consumer group/topic partition before replay. The fresh controller records the affected-row result and reset command. Stop the fresh services without deleting their volume only when their evidence is already captured:

```bash
docker compose -p kafka-crash-lab-m4fresh -f compose.m4-fresh.yaml stop
```
