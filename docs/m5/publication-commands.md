# Proposed publication commands

These commands are a reviewed plan only. They have not been run. They require
an explicit publication approval and an approved commit-author email.

```bash
set -euo pipefail
export REPOSITORY_OWNER='jeshwinwilliam'
export REPOSITORY_NAME='kafka-consumer-crash-lab'
export RELEASE_TAG='v1.0.0'
export APPROVED_GIT_EMAIL='replace-with-owner-approved-email'

git config user.name 'Jeshwin William James'
git config user.email "$APPROVED_GIT_EMAIL"
git add LICENSE README.md PUBLICATION-BLOCKERS.md RELEASE-NOTES.md \
  EVIDENCE-INDEX.md docs/m5 release-tools scripts src sql pom.xml \
  compose.yaml compose.m4-fresh.yaml .gitattributes .gitignore
git commit -m 'Prepare Kafka crash lab v1.0.0'
git remote add origin "git@github.com:${REPOSITORY_OWNER}/${REPOSITORY_NAME}.git"
git push -u origin HEAD:main
git tag -a "$RELEASE_TAG" -m "Kafka consumer crash lab $RELEASE_TAG"
git push origin "$RELEASE_TAG"
```

After verifying the remote commit and tag, create a GitHub release for
`v1.0.0` and attach only the reviewed licensed source package, its SHA-256
sidecar, and the separately identified public-evidence derivative and sidecar.
Do not upload the private original archive, candidate-only review records, or
derivative working directories. MIT applies to this repository's code and
documentation; preserve third-party notices and licenses.
