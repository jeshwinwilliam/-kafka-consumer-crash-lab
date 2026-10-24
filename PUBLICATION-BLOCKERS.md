# Publication Blockers

Do not create a remote repository, release, archive upload, website link, or
deployment until every blocker below is resolved.

1. **No immutable public source reference exists.** The original lab directory
   is not a Git repository. Create and review a clean local source commit, then
   create a public remote and release tag only after approval.
2. **No license has been selected.** The original lab has no license or notice
   file. Choose a license before public distribution.
3. **The preserved evidence archive is not public-safe as-is.** Its mapping and
   historical records include absolute local paths such as
   `/Users/<local-account>/kafka-crash-lab/...`. Preserve the original bytes and
   checksum, but conduct a privacy review before releasing an explicitly named
   derivative with a new checksum and change record.
4. **No public URLs exist yet.** Repository, immutable commit/release,
   reproduction guide, evidence index, archive, and checksum URLs must all be
   verified after publication and before the website article is enabled.
5. **Runtime reproduction has not been executed from this candidate.** Static
   layout checks are complete; Maven, Docker Compose, and controller execution
   would create new build or run artifacts and require explicit approval.

The website's default production build must continue to exclude the article
and homepage card while these blockers remain open.
