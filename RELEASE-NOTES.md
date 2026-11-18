# Local Release Candidate Notes

**Status:** Prepared for local review on 2026-10-24. This is not a public
release, remote repository, tag, upload, or deployment.

## Proposed public identity (unpublished)

- Repository name: `kafka-consumer-crash-lab`
- First public release tag: `v1.0.0`
- Evidence asset role: local public-evidence derivative prepared for review;
  publication remains pending approval.
- Proposed URLs: `<unpublished>` until a repository and release are created.
- License: MIT for this repository's code and documentation only; third-party
  licenses/notices remain in force.

## Candidate contents

- Actual Java 21 Maven source, JUnit tests, SQL migrations, Docker Compose
  configurations, and Python standard-library controllers.
- The current documentation set under `docs/m5/`.
- The separately identified public-evidence derivative and its new checksum.
  The private upstream review archive remains outside the public-source package.
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

## Proposed publication commands (do not run without explicit approval)

The proposed owner is `jeshwinwilliam`, repository name is
`kafka-consumer-crash-lab`, and initial release is `v1.0.0`. After a reviewed
local commit exists and publication is explicitly approved, create the remote,
push the selected commit, tag it, and attach the licensed source package using
the owner-approved Git identity. These actions remain intentionally unexecuted.
