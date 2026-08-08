# Fixture-substrate ruling (magistrate, 2026-08-08 afternoon)

**Question** (opened by the T0 final checkpoint, `18d007a`): storage
substrate for `tests/fixtures/d117_v2_production/custody_store/` — 38
content-ID directories, 190 governed files, raw plists totaling
3,314,405,206 bytes (~3.087 GiB; ~142 MiB compressed as git objects) —
committed on `impl/d117-postcollection-trust` @ `1cae2bc` and pushed
with GitHub size warnings. Ruling required BEFORE more fixture work or
any PR.

**Consult**: Sol xhigh, read-only, one round
(`SUBSTRATE-CONSULT-PROMPT.md` → `SUBSTRATE-CONSULT.md`, both in this
directory). The consult verified the fixture against the issued ledger
before recommending (76 receipts, 38 observations, 190/190 SHA census,
head digest `08456d50…`, store-manifest SHA `dc90e366…`).

**RULING — ADOPTED IN FULL, one narrow amendment:**

Substrate = **digest-pinned, losslessly compressed (`tar.zst`) GitHub
Release asset, hydrated by one required CI job
(`d117-production-proof`), cached only as an optimization.** In git:
the issued artifacts, the ledger-derived `custody_store/manifest.json`
census, a transport descriptor (release tag, asset name, archive
sha256, format, file count = 191, logical bytes, manifest sha256), the
hydration/packaging tooling, and the small strict/synthetic fixtures.
Out of git: the 38 content directories, packaged byte-for-byte. The
archive is a delivery replica, never an authority — the issued ledger
remains senior; the loader re-derives the census from the authenticated
ledger and requires exact equality. Hydrator and loader refusal
contracts, the CI job's nine steps, and the D-118/D-121 gate mapping
are as written in the consult (§Binding CI story, §Required refusal
behavior). Repo verified PUBLIC (asset downloads unauthenticated,
unmetered); zstd present.

Rejected: git-as-is (3.3 GB × 8 full-history CI checkouts per run,
permanent clone tax), LFS (meters raw 3.087 GiB per fetch; tooling
friction), local-custody-with-CI-skip (CI green would be compatible
with never running the decisive proof — wrong failure boundary),
generated-at-test-time (physical captures; killed), one-member-in-git,
data submodule. Full table in the consult.

**Narrow amendment to the round-2 contract** (recorded per the
consult's authority-conflict note): step 4's "assemble the CHECKED-IN
fixture" is amended to "assemble the HYDRATED fixture" — the logical
fixture remains the same 38-directory store with identical bytes,
digests, and no-substitution requirements; only the storage placement
changes (git-ignored working data + release asset instead of
git-tracked). No issued byte, receipt, digest, or refusal requirement
changes. Ruling precedence: substrate ruling > round-2 prompt wording.

**History rewrite (executed by the magistrate, this session):**
`1cae2bc` is the only commit in branch history introducing the raw
paths (parent `97fd4c1`). It is amended to exclude the 38 content
directories (census manifest stays tracked; ignore rule added), then
force-pushed with an exact lease against `1cae2bc`. Sequencing chosen:
rewrite FIRST, then round 2b resumes on the clean head (the consult's
tooling-first ordering reaches the same end state; rewrite-first takes
the blobs off the remote before any further work and guarantees no
later commit carries them). Gate consequence (consult §mechanics 7):
NO review evidence from any pre-rewrite SHA transfers; the full
D-118/D-121 gate runs on the final rewritten candidate.

**Reversibility custody** (the banked checkpoint `1cae2bc` was Ed's
stop-order bank; it is preserved, not destroyed): local safety tag
`safety/trust-1cae2bc-prerewrite` + git bundle at
`~/JouleWise-window-custody/trust-prerewrite-20260808/` (branch objects
vs main). The fixture bytes themselves remain independently custodied
in the issued evidence roots and Ed's custody backups; the store is
reconstructible from the ledger + those roots, and verifies via the
committed census. Old→new hash mapping recorded in this directory
after the rewrite (`REWRITE-RECORD.md`). Historical documents naming
`1cae2bc` (RUN_STATE checkpoint, C-051, the T0 run report) are
correct-as-written history and are NOT rewritten; this ruling is the
pointer.

**Release publication order**: draft release targeting a blob-free main
commit → upload → fresh download → archive-SHA + 190/190 census
verification → publish (immutability if plan supports); executed by the
magistrate (network + gh are outside Sol's sandbox) after round 2b
lands the governed packager. CI's required job will only go green once
the release exists — expected red until then.

Surfaced for Ed's morning review as a reversible item (the force-push
is lease-guarded and bundle-backed; overriding this ruling =
restore-from-bundle + force-push back).
