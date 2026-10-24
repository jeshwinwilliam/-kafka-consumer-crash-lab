# Evidence guide

## Start with the supplemental archive

The review archive bundled with this local candidate is
`evidence/m4-supplemental-review-corrected.tar.gz`; its adjacent `.sha256` file
records the archive digest. Verify it without changing the archive bytes:

```bash
# Run from the candidate root.
(cd evidence && shasum -a 256 -c m4-supplemental-review-corrected.tar.gz.sha256)
mkdir -p /tmp/kafka-crash-lab-evidence-review
tar -xzf evidence/m4-supplemental-review-corrected.tar.gz \
  -C /tmp/kafka-crash-lab-evidence-review
cd /tmp/kafka-crash-lab-evidence-review/supplemental-review-corrected
shasum -a 256 -c CHECKSUMS.sha256
python3 -m json.tool ARCHIVE_AUDIT.json
```

The archive retains historical absolute local paths. It is included in this
candidate only for review; `PUBLICATION-BLOCKERS.md` explains why it must not
be uploaded publicly as-is.

`REVIEW_MAPPING.json` is the authoritative archive-relative mapping. It maps every required campaign, frozen-coverage, fresh, normalized-contention, and provenance item. `GAP_REPORT.json` states what cannot be reconstructed from the archive.

## Campaign-index erratum

The immutable `campaign/campaign-index.json` contains **90** records:

- **50** records use `resultPath`.
- **40** records use `evidencePath`.

A reviewer must resolve whichever field exists; no record should be assumed to use `resultPath`. The campaign index remains unchanged. The supplemental mapping resolves the actual directory for both field forms and checks for `result.json` plus a trial manifest (`m4-trial-manifest.json` or `manifest.json`).

## Source and build identity

`campaign/frozen-source-manifest.json` records the campaign Java executable, Maven/Python versions, images, and full hashes. The campaign used Java 21.0.12.1, Maven 3.9.15, Kafka image digest `sha256:5cc2…772e0e`, and PostgreSQL image digest `sha256:3645…3826`.

`provenance/clean-snapshot-build.log` and `provenance/snapshot-artifact-hashes.sha256` preserve historical build provenance. `provenance/rebuilt-frozen-source-20261017b/` preserves a separately identified Java 21 rebuild. It is evidence of a new build of matching source where documented, not proof of the historical temporary build’s exact artifact files.

The corrected fresh 10–12 controller records its classpath and artifact-hash-file digest in each `fresh/corrected-v2/*/result.json`. It is separately identified from campaign execution.

## Representative evidence locations

- Crash/replay and SIGKILL cases: `campaign/trials/` entries mapped from cases 2–6; case 5 is identified in `ARCHIVE_AUDIT.json`.
- Concurrency: `fresh/normalized-contention/case8/` and `case9/` contain distinct manifest, `stdout.ndjson`, `stderr.log`, and `exit-status.txt` files.
- Corrected missing-account/replay evidence: `fresh/corrected-v2/` case 10–12 result directories.
- Frozen coverage: `coverage/`.

The archive audit validates files and counts. Assertions remain tied to snapshots, raw logs, process exits, group descriptions, and observer output rather than pass labels alone.
