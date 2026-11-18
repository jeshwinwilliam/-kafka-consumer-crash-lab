# Public evidence derivative guide

Use the local public-evidence derivative described in [EVIDENCE-INDEX.md](../../EVIDENCE-INDEX.md). It has its own archive checksum, transformed-file checksum inventory, transformation log, and validation report. It does not require access to the private upstream archive.

After extraction, verify `CHECKSUMS.sha256`, then inspect:

- `DERIVATIVE-VALIDATION.json` for campaign/fresh/coverage counts, mapped-path resolution, privacy scan, and result-preservation check.
- `DERIVATIVE-TRANSFORMATIONS.json` for every transformed, excluded, renamed-historical, and generated archive-relative file.
- `REVIEW_MAPPING.json` for working derivative archive-relative mappings.
- `HISTORICAL_PRIVATE_CHECKSUMS.sha256`, `HISTORICAL_REVIEW_MAPPING_REDACTED.json`, and `HISTORICAL_ARCHIVE_AUDIT_REDACTED.json` for labelled derivative copies of historical records.

The 90-record campaign index retains its mixed field schema: 50 records use `resultPath` and 40 use `evidencePath`. Resolve either through the derivative mapping; do not assume only one field exists.

Historical source/artifact hash values remain historical content. New derivative bytes are verified by the derivative `CHECKSUMS.sha256`; do not compare that file as if it were a historical build-artifact hash.
