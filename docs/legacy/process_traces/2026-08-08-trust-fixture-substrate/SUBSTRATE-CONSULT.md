# Storage-substrate ruling

Adopt a **digest-pinned, losslessly compressed GitHub Release asset, hydrated by one required CI job and cached only as an optimization**.

Keep in Git:

- The issued D-079 acceptance artifact, 76-receipt ledger prefix, and head pin.
- The ledger-derived `custody_store/manifest.json` census.
- A small transport descriptor containing release tag, asset name, archive SHA-256, format, expected file count, logical bytes, and manifest SHA-256.
- Hydration/validation tooling and the small strict/synthetic fixtures.

Keep out of Git:

- All 38 content directories and their 190 governed files, packaged byte-for-byte as one `tar.zst`.

The archive is a delivery replica, never an authority. The issued ledger remains senior.

## Why this preserves the contract

The current fixture verifies cleanly:

- HEAD: `1cae2bcf6e4d92691a2f1370516b6a926a007352`
- 76 receipts, 38 finalized observations, 38 unique content IDs.
- 190/190 governed files match the ledger’s SHA-256 maps.
- Head: sequence 76, digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`.
- Store manifest SHA-256: `dc90e366235343abeca97f7fc16b6cb5d257cb4a9c9a17d6042b12a4dec49370`.
- Raw plists: 3,314,405,206 bytes total—3.087 GiB—with each file 82.4–83.7 MiB.
- All 38 are distinct Git blobs. Their present compressed Git-object footprint is about 141.7 MiB, so the premise needs one correction: the network/`.git` tax is compressed, not 3.1 GiB. The working-tree and CI-checkout expansion is still 3.3 GB per job.

There is **no relocation table**. CI supplies:

```text
--calibration-custody-store $RUNNER_TEMP/d117-v2-custody-store
```

Production resolution remains exactly:

```text
ROOT/<receipt.content_id>/<governed-artifact>
```

No locator mapping, no fallback, no partial mode. The historical absolute locator remains authenticated inside its receipt but does not select storage.

The transport descriptor must not contain per-receipt destination paths. Suggested fields are:

```text
schema_version
fixture_id
release_tag
asset_name
archive_format
archive_sha256
logical_file_count = 191        # 190 governed members + store manifest
logical_bytes
custody_manifest_sha256
```

The census remains the current strict manifest: sorted 38 content IDs, each with exactly five artifact hashes, plus ledger schema/head. At runtime the loader derives that entire object again from the authenticated ledger and requires exact equality; it never trusts the committed census or archive descriptor to supply identities.

## Exact publication and branch-rewrite mechanics

1. Build the archive from the currently verified store, with sorted paths, normalized metadata, regular files/directories only, and lossless zstd compression. The current Git compression numbers imply a roughly 0.15–0.17 GiB asset, safely below GitHub’s 2 GiB per-asset limit. GitHub states release assets have no aggregate-size or bandwidth quota. [GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)

2. Create the release as a draft, targeting a **blob-free main commit—never `1cae2bc`**. Upload the archive, download it afresh, verify its archive SHA, safely extract it, and rerun the 190/190 ledger census and production loader.

3. Publish only after that verification. Enable release immutability if the repository’s plan supports it; otherwise archive and member digests still make replacement an availability failure, not a successful substitution. [GitHub immutable releases](https://docs.github.com/en/enterprise-cloud%40latest/code-security/concepts/supply-chain-security/immutable-releases)

4. In this branch, preserve `custody_store/manifest.json` but stage deletion of the exact 38 ledger-derived content directories. Add the descriptor, hydration tool, ignore rules, and dedicated workflow.

5. **Rewrite `1cae2bc`, not merely add a later deletion commit.** It is the only commit anywhere in current branch history that introduced these raw paths, and its parent is `97fd4c1`. Amend or replace that checkpoint commit after staging the external-substrate form. A later deletion would leave all blobs in main’s ancestry.

6. Force-push only with an exact lease against old remote head:

```text
refs/heads/impl/d117-postcollection-trust:
1cae2bcf6e4d92691a2f1370516b6a926a007352
```

Keep any safety tag/bundle local and never tag the release at the old commit. Verify afterward that the raw paths occur in no commit reachable from the rewritten remote branch.

7. Integrate current `main` only after the rewrite. Then run the entire D-118/D-121 gate on the new final candidate. No review evidence from the old SHA transfers across the rewrite.

This must occur before merge. Rewriting shared `main` afterward is mechanically imaginable but operationally unacceptable; deleting the files at main’s tip would not remove the clone history.

## Binding CI story

Add one required check named, for example, `d117-production-proof`:

1. Ordinary source checkout—no large payload.
2. Restore the compressed archive from Actions cache using an exact archive-digest key and no broad restore prefix.
3. On cache miss, download the release asset. For a private repository, use the job’s repository-scoped token.
4. Verify archive SHA-256 before extraction.
5. Reject unsafe archive entries, then extract under `$RUNNER_TEMP`.
6. Verify the external manifest is byte-identical to the committed census.
7. Authenticate the issued ledger and perform the full 190-member per-file census.
8. Execute, without patches:
   - the authentic production CLI mint;
   - production-open/registry bidirectional equality;
   - the coordinated-attack regression and masking-removal variants;
   - no-output and refusal-stage assertions.
9. Treat missing asset, network failure, cache corruption, absent members, or a skipped full-fixture test as a hard failure.

Cache only the compressed archive, not the expanded 3.3 GB tree. GitHub caches are immutable per key, but still must be rehashed; the default repository cache allowance is 10 GB and unused entries may be evicted after seven days. [Actions cache behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)

Normal 3.11/3.14 shards may label the full-fixture test unavailable and skip it, because the dedicated required job executes it. They must not report such a skip as production-proof evidence.

For gate compatibility:

- D-118 item 9: the lead’s exact integration-tree replay must run the full-fidelity proof with Ed’s local custody or the same hydrated archive—no skip.
- D-118 item 11: the final head’s required `d117-production-proof` CI check must be green.
- D-121 item 12: the magistrate reviews that exact head only after both proofs and all other items finish.

Therefore, a regression that CI never executes is not acceptable here. A required exact-head local run could logically be binding, but a merely skipped CI test hollows out the portable no-substitution claim. Under this substrate both local and CI execute it.

## Required refusal behavior

The hydrator must refuse:

- Archive SHA mismatch.
- Absolute, `..`, duplicate, or unexpected archive paths.
- Symlinks, hardlinks, devices, sockets, FIFOs, or other non-regular entries.
- Missing or extra packaged members.
- Manifest bytes differing from the committed census.

The production loader must refuse in the existing custody-invalid domain:

- Noncanonical/duplicate-key/nonfinite store manifest.
- Manifest inequality with the ledger-derived projection.
- Wrong ledger schema, sequence, or head digest.
- Null or duplicate content identity.
- Anything other than the exact five-artifact hash vector.
- Missing content directory or governed artifact.
- Symlink, non-regular file, path escape, or digest mismatch.
- Any mixture of store and legacy resolution.
- Any fallback to the receipt’s historical locator.

As already ruled, extra filesystem entries are ignored and unregistered by the production loader; the archive packager may be stricter and forbid them.

The proof must additionally fail if observed opens and authentication-registry records are unequal in either direction.

## Rejected alternatives

| Option | Verdict | Why it loses |
|---|---|---|
| Git LFS for 38 plists | Reject | Authenticity survives, but LFS stores/downloads the full 3.087 GiB. Free/Pro includes 10 GiB monthly storage and bandwidth; three full downloads consume about 9.26 GiB, and GitHub Actions downloads charge the repository owner’s LFS bandwidth. Current published overage rates are $0.07/GiB-month storage and $0.0875/GiB egress. It also requires Git LFS locally and explicit selective CI fetching; checkout defaults to pointer files. [LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs), [checkout LFS default](https://github.com/actions/checkout/blob/main/action.yml) |
| Local custody only, CI skip | Reject | It can support a lead-local gate, but it makes CI green compatible with never exercising the decisive proof. That is the wrong failure boundary for this branch. |
| Fetchable archive with hard-failing CI | Adopt | Preserves exact bytes, removes clone tax, compresses extremely well, has no LFS quota, and keeps one operational path. |
| Generated at test time | Kill | Powermetrics captures are physical observations. No deterministic generator can reproduce their exact bytes and ledger hashes. Lossless decompression can, but that is storage—not generation. |
| Keep regular Git as-is | Reject | Current workflows create eight full-history test checkouts plus build and site checkouts. Every one expands the 3.3 GB tree even though only one proof needs it. GitHub warns above 50 MiB per object, blocks at 100 MiB, and recommends keeping repositories small. [GitHub large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), [repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits) |
| One production member in Git, 37 external | Reject | It retains a >50 MiB warning, does not establish the 38-member proof, and saves no full-proof fetch. The existing small strict seed and synthetic custody fixtures are better fast-test assets. |
| LFS with selective checkout/cache | Runner-up only | It avoids eight smudges if carefully configured, but still adds LFS tooling and meters raw-byte fetches. A compressed release asset is smaller and simpler. |
| Separate data Git repo/submodule | Reject | It merely relocates regular-Git history and adds submodule lifecycle friction without improving authenticity over the pinned archive. |

Keeping the corpus in regular Git would be defensible if JouleWise were primarily a dataset repository whose central promise was offline-clone completeness. It is a capstone code/methodology repository with one specialized proof consumer, so that trade is not justified.

## Authority conflict to record

The issued artifact and adopted R2 ruling are fully compatible with this design: they mandate exact bytes, content-ID resolution, and ledger-derived verification—not regular-Git storage.

The round-2 implementation prompt literally says “assemble the checked-in fixture.” The recommended substrate supersedes only that placement adjective: the logical fixture remains the same 38-directory store, but is hydrated rather than Git-tracked. The magistrate should record this narrow amendment before implementation resumes. No issued byte, receipt, digest, or no-substitution requirement changes.

Checks performed: clean `1cae2bc` status and history/path audit; current CI checkout census; 38-file size and Git-object measurements; production ledger/store load valid at 76 receipts/38 observations; 190/190 SHA census; issued artifact and store-manifest SHA recomputation; D-118/D-121, R2 ruling, and round-2 contract review; official GitHub limits/billing/cache/release review; no files changed and no test suite run.