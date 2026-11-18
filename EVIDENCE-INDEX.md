# Public evidence derivative index

## Review derivative

| Field | Value |
| --- | --- |
| Candidate-relative path | `evidence/public-derivatives/m4-public-evidence-derivative-20261118-r3.tar.gz` |
| Adjacent checksum file | `evidence/public-derivatives/m4-public-evidence-derivative-20261118-r3.tar.gz.sha256` |
| Derivative role | Privacy-reviewed derivative prepared for local review; not published |
| Mapping | `m4-public-evidence-derivative-20261118-r3/REVIEW_MAPPING.json` inside the archive |
| Validation | `m4-public-evidence-derivative-20261118-r3/DERIVATIVE-VALIDATION.json` inside the archive |
| Transformations | `m4-public-evidence-derivative-20261118-r3/DERIVATIVE-TRANSFORMATIONS.json` inside the archive |

Verify the derivative from a candidate checkout:

```bash
set -euo pipefail
export CHECKOUT_ROOT="$PWD"
export DERIVATIVE_ARCHIVE="$CHECKOUT_ROOT/evidence/public-derivatives/m4-public-evidence-derivative-20261118-r3.tar.gz"
(cd "$CHECKOUT_ROOT" && shasum -a 256 -c evidence/public-derivatives/m4-public-evidence-derivative-20261118-r3.tar.gz.sha256)
mkdir -p "$CHECKOUT_ROOT/derivative-extract"
tar -xzf "$DERIVATIVE_ARCHIVE" -C "$CHECKOUT_ROOT/derivative-extract"
export EVIDENCE_ROOT="$CHECKOUT_ROOT/derivative-extract/m4-public-evidence-derivative-20261118-r3"
(cd "$EVIDENCE_ROOT" && shasum -a 256 -c CHECKSUMS.sha256)
python3 -m json.tool "$EVIDENCE_ROOT/DERIVATIVE-VALIDATION.json"
```

## Evidence coverage preserved by the derivative

- Campaign: 90 records; cases 2–6 have 10 each and cases 8–9 have 20 each.
- Frozen coverage: seven records.
- Final fresh set: 14 executions, with historical fresh 10–12 retained as unverified-isolation and separately identified corrected replacements for cases 10–12.
- Historical source/artifact hashes are retained as historical values. Derivative file bytes use newly generated `CHECKSUMS.sha256` entries.

## Boundaries

This derivative preserves observations and historical status distinctions while replacing personal local-path/account metadata with neutral tokens. The private upstream review archive remains unchanged and is not required by this public-candidate reproduction path. The derivative itself remains local review material until licensing and final publication approval are complete.
