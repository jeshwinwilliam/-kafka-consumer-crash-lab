# Publication Blockers

Do not create a remote repository, release, archive upload, website link, or
deployment until every blocker below is resolved.

1. **No immutable public source reference exists.** The original lab directory
   is not a Git repository. Create and review a clean local source commit, then
   create a public remote and release tag only after approval.
2. **MIT is selected for this repository's code and documentation.** `LICENSE`
   records Copyright (c) 2026 Jeshwin William James. Preserve third-party
   notices and licenses; this selection does not apply to dependencies, Docker
   images, the website, EffectGuard, or other projects.
3. **The derivative is review-ready, not approved for publication.** Its
   transformation log, mapping, checksums, and validation report require final
   privacy review. The private upstream archive remains unchanged and excluded
   from the public-source package.
4. **No public URLs exist yet.** Repository, immutable commit/release,
   reproduction guide, evidence index, archive, and checksum URLs must all be
   verified after publication and before the website article is enabled.
5. **Runtime reproduction has not been executed from this candidate.** Static
   layout checks are complete; Maven, Docker Compose, and controller execution
   would create new build or run artifacts and require explicit approval.

The website's default production build must continue to exclude the article
and homepage card while these blockers remain open.
