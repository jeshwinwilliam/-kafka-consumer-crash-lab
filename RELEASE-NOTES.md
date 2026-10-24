# Local Release Candidate Notes

**Status:** Prepared for local review on 2026-10-24. This is not a public
release, remote repository, tag, upload, or deployment.

## Proposed public identity (unpublished)

- Repository name: `kafka-consumer-crash-lab`
- First public release tag: `v1.0.0`
- Evidence asset role: reviewed supplemental archive plus a separately approved
  public-safe derivative, if required by privacy review.
- Proposed URLs: `<unpublished>` until a repository and release are created.

## Candidate contents

- Actual Java 21 Maven source, JUnit tests, SQL migrations, Docker Compose
  configurations, and Python standard-library controllers.
- The current documentation set under `docs/m5/`.
- The exact reviewed archive
  `m4-supplemental-review-corrected.tar.gz` and its existing SHA-256 file.
- Candidate-only release review metadata under the repository root and
  `review/`.

## Source and execution identity

The current source matches the archive's `source/frozen-snapshot` for the
reviewed source set. The only source-tree differences identified during review
were the later corrected controller `scripts/run_m4_fresh_10_12_v2.py` and a
generated Python cache directory. The evidence archive remains unchanged and
retains its own campaign, source, build, and execution identity records.

## Deliberate exclusions

- `target/` build output (approximately 22 MB).
- The original `results/` tree (approximately 214 MB), including raw and
  superseded material. The reviewed archive is included instead as a single
  immutable review asset.
- Python caches and `.DS_Store` files.
- EffectGuard, Paper #3, website files, credentials, and unrelated projects.

See `review/PACKAGING-CHANGES.md` and `review/SECURITY-EXCLUSIONS.md` for
details.
