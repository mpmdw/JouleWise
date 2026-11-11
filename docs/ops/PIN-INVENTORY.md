# Pin inventory for the release-day prune

**Offline planning snapshot, not retention or release authorization.** This
revision applies Opus's ADMIT_WITH_FIXES review. Recorded main is
`c07b388e90d9f085e6428a1e0d96b0361ff417f0`; no fetch or server verification was
performed. The original plan used `4e7e878a1` and a narrower census; its counts
and per-citation tag proposals are superseded by this revision.

Authority: [freeze-by-commit F1–F7](../process/freeze_by_commit.md),
[decision log D-188–D-190](../decision_log.md#d-188-block-5-analysis-rewrite-under-result-equivalence-engineering-window-fresh-analysis-start-ed-2026-11-02),
[previous prune](../run_reports/2026-11-06-repo-prune.md), the cold review at
`origin/ops/2026-11-08-prune-plan-opus-review:docs/ops/prune-plan-opus-review.md`,
and the present PI brief. Full SHA/tree and registered digests remain authority;
tags retain objects and provide discovery. Existing tags never move.

## Tables and reproducible refresh

- [TAGS-TO-CREATE.tsv](TAGS-TO-CREATE.tsv): **33 named anchors** (12 existing names to
  verify/reuse, 21 proposed tags). No duplicate `pin/b5-analysis-r*` or
  `pin/bytes-collection-*` tags and no `*-cited-<hex>` tag factory. The archive
  row is corrected to recorded main. Refresh it to freshly fetched release-day
  main and date the name at creation; never move a created tag.
- [TAG-REVIEW-EVIDENCE.tsv](TAG-REVIEW-EVIDENCE.tsv): one row per named tag with
  locally observed tag-object ID (or NOT_CREATED) and tree. PR number, required
  checks, exact-SHA conclusions and server JSON are **PENDING**. This offline
  task cannot invent those results. Complete and archive them before use.
- [PIN-COMMITS.tsv](PIN-COMMITS.tsv): resolved source citations, coverage class,
  sampled locations (up to 3 per identity) and complete location counts.
  MAIN/TAG means locally observed reachability, **not** server protection.
  HOLD-BUNDLE-ONLY/PR-BUNDLE-ONLY stays on HOLD until its entire retiring tip is
  protected; UNRETAINED blocks deletion pending recovery/disposition.
- [PIN-UNRESOLVED.tsv](PIN-UNRESOLVED.tsv): unresolved textual hex candidates,
  including dates, external model revisions and synthetic hashes. Not all are
  repository commits. Numeric-only strings that resolve to no object are counted
  in `CENSUS.json` rather than expanding this table with fixture decimal values.
  Numeric-only candidates require quoting or commit/SHA/head/revision/pin
  context, so decimal fixture values do not accidentally become commit pins.
  Resolvable numeric-only commit prefixes in that context are retained. An owner must distinguish
  actual missing pins, including any contextual numeric-only reference.
- [SOURCE-DIGESTS.tsv](SOURCE-DIGESTS.tsv): SHA-256 source literals in
  `joulewise/`, `scripts/`, **and `tools/`**, across the scanned tips. Tests/configs
  retain their existing digest registry; this table does not replace it.
- [BRANCH-TRIAGE.tsv](BRANCH-TRIAGE.tsv): exact locally recorded origin tips.
  Only unchanged original merged candidates remain candidates; new/moved refs
  default HOLD. The release operator can reduce this set, never infer approval
  from the disposition label.
- `CENSUS-SCOPE.tsv` / `CENSUS.json`: exact scanned refs/commits and scope
  metadata. `BRANCH-NAME-CONSUMERS.tsv`: grep hits requiring owner dispositions.

Committed tooling: `scripts/ops/prune_inventory.py`, `prune_verify.py`,
`prune_branch_names.py`, and one-command `prune_refresh.py`. All are offline
source/Git readers. They do not fetch, create tags, remove refs, touch weights,
or follow absolute data paths found in text. Main's **entire eligible tracked source
text** is scanned; each HOLD tip contributes changed/new blobs, with unchanged
blobs covered by main's scan. Git symlinks and submodules are not followed;
`restricted`, `night-custody` and `night-archive` components and fixture data
payloads are excluded before blob reads. Under `tests/fixtures/`, only source
(`.py/.sh/.js/.mjs`) and documentation (`.md/.rst`) are eligible, and raw/custody
subtrees remain excluded. All code/config/docs/registration sources remain in scope.
These fixture-payload exclusions do not remove retention: main history and whole HOLD
tips remain in the complete mirror/bundle. Text is UTF-8 without NULs. Full SHA-256 literals are not misclassified
as abbreviated Git commits. Source locations include exact containing tips.

Run the refresh command in [PRUNE-PLAN step 1](PRUNE-PLAN.md#1-fresh-census-receipt-identities-and-review-evidence),
review its output diff, and commit the approved refreshed tables before execution.
The census is a **coverage check**, not an assertion that every citation is a
scientific dependency. Freshness requires the later fetch, including PR heads.

## Named scientific anchors

Full targets are in the 33-row manifest. The source map below explains their
roles; it does not replace the hashed registrations or imply live validation.

| Anchor group / tag(s) | Source authority and identity | Status after B5 release |
|---|---|---|
| `pin/b5-seal1-claim`, `pin/b5-seal1-record`, `b5/collection`, `pin/b5-seal2-record` | `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`; first claim `a64000884`, second claim `c27485347` and original sealed inventory | Retain original seals/inputs; never repin their digests |
| `pin/b5-harvest-1` through `-4` | `configs/analysis/b5/seal_pins.json`; `7e6158d66`, `224a264c5`, `0699abbb0`, `b039c0257` | Historical replay, both errata and per-harvest file identities |
| `pin/b5-corpus18-text-gate` | **`8ce450ad55949e9e30fd21261b4b0eb687e1915a`**, corpus-18 erratum TEXT-GATE on `seal/2026-10-09-corpus18-text` | Added missed provenance anchor |
| `pin/b5-hclaim-ci` | **`9271df94f0e5bac1d4dfd9c0122c73b90e6cef20`**, H_claim-tree CI record on `lane/2026-10-07-ci-lock-inode-candidate` | Added missed CI provenance anchor; later archive actual check JSON |
| `pin/b5-accepted-analysis` | `tests/b5_analysis/test_frozen_files.py`; `b13a510dc`; ruled rebind `13af1baa8` is a separate source citation | Preserve original/rebound identities separately |
| Existing `b5/analysis`, `b5/analysis-r1`, `b5/analysis-r1-9bfix-ref`, `-r2`, `-r3`, `-r4` | Existing annotated tags; D-188/D-189 and `docs/analysis/b5/DEVIATION-LOG.md` | Reuse unchanged; r1 and the 9b reference remain oracle history |
| B6 `pin/b6-registration`, `pin/b6-machine-test`, `b6/collection`, `pin/b6-acceptance`, `pin/b6-kit`, `pin/b6-ledger-final` | `docs/registrations/block6_freeze_by_commit_addendum.md`; actual collection `f31aca19f`; kit `1c1bc3204`; final ledger `20c881075` | B6 remains live; early UNRECORDED text is superseded by appended records |
| BYTES `pin/bytes-registration`, `pin/bytes-pass2-lane`, existing `bytes/collection-n1`–`n4`, `pin/bytes-ledger-final` | `docs/registrations/bytes_freeze_by_commit_addendum.md`; pass-2 tree `ee4ce93fc`; final ledger `1aca17e27` | BYTES remains live; preserve registered analysis/manifest bytes on pass-2 lane |
| `pin/align-v4-measurement-snapshot`, `pin/align-v4-r1-integration-snapshot` | Measurement snapshot `9c40e4e5d`, R1 integration `e901eb2a4`; lane identity/plan/registration files | **PROVISIONAL_PENDING_LIVE_GATES**, not a registered live validation |
| `archive/process-traces-before-release-prune-<release-date>` | Freshly fetched pre-prune main; includes original/last-change seal record `3ac9623da`/`4c34132bc` | Named once at creation; preserve main history and existing prior archive promise |

The following are **required release inputs**, not fabricated executable TSV
rows today. For each role record the receipt field, full commit/tree, exact
retaining tag/tag-object ID, receipt digest, PR and exact-SHA required-check
results. Reuse an existing tag if it already names that exact role's commit.

| Release role | Required source |
|---|---|
| Analysis | Accepted receipt `analysis_commit` / explicit pinned commit |
| Equivalence oracle, including D-189 reference | Receipt's oracle binding; retain both r1 and 9b-fixed reference where used |
| Independent comparator checkout | Receipt's comparator binding; #704 `bea480f296e5c7bc77ad1684936f2b257801f597` if used before merge |
| Independent recompute checkout | Receipt's recompute checkout commit/tree |
| Release checkout | Receipt `release_checkout.commit` and tree from `release_b5.py` |
| Final B5 ledger | Magistrate-recovered full SHA beginning `4cb222a19`; server branch `records/b5-ledger-final` and tag `pin/b5-ledger-final` |

A release analysis tag alone covers none of the other roles by implication.
Add distinct named tags only where existing protected refs do not retain the
required identity. About 30 anchors is proportional guidance, not a hard cap
that permits dropping a required receipt identity.

## HOLD-lane gaps closed by the expanded scope

Opus found the following missed groups. They are now mandatory scope inputs,
not approvals to retire the branches. Preserve the whole tip as
`archive/branch/<name>` at eventual retirement, including cited commits plus
uncited work. Do not substitute per-citation tags for that tip.

| HOLD group | Pins highlighted by review / retention requirement |
|---|---|
| ALIGN v4 R1/R11 | 11 citations; R0 NLL config pin **`62bc719f73da4874bb9fd1a2d5c0ee2d1d8f0881`**, `configs/align/v4/r0_nll_reference.json`, `lane/2026-11-06-r0-d-nll-diagnosis` |
| qwen4_exp canonical + MBP-live | 7 citations; Sol port **`28d1534496b582aaeeb8bd533127fb682d381516`**, twin **`ad56248a5be7b12755cc0102df3db746a55d6600`**; all canonical/MBP-live tips remain HOLD |
| BYTES stage-1 (#701) | 11 citations; scan both `lane/2026-11-07-bytes-stage1` and `-run` tips |
| #704 comparator | 3 citations; include comparator checkout `bea480f29` and any subsequent exact receipt binding |
| `research/2026-11-07-audit-burn` | 24 citations; whole tip remains HOLD |
| Deeper `docs/**` and `tools/**` | 38 previously uncovered off-main doc citations, including the two new B5 anchors above; tools includes the independent B5 comparator |

These are review counts, not independently asserted current census totals. The
full refreshed tables and source scope give the current locally resolvable set.

## Unfetched and missing history

| Citation | Current classification and gate |
|---|---|
| `498ad1d0` (`RUN_STATE.md:2861`) | **Exists on GitHub per Opus**, full ID starts `498ad1d0c0f9`; not present in this clone. Later fetch PR heads and resolve; do not call it nonexistent or recover it by reading a measurement checkout |
| `4cb222a19` (`RUN_STATE.md:54`) | B5 final ledger is MBP-only; **mandatory magistrate recovery to server and both bundles before any MBP cleanup** |
| `050aaad13` (`RUN_STATE.md:949`) | Historical rehearsal; recover or owner-disposition |
| `6bcd90a3` (`RUN_STATE.md:2873`) | Historical quiet-gate lead commit; recover or owner-disposition |
| `9a6f8880` (`RUN_STATE.md:3278`) | Historical clone mint head; recover or owner-disposition |

Absent or abbreviated names are not executable tag targets. A passing topology
check for resolvable commits does not prove complete provenance retention.

## Digest and history-reader protection

`configs/pins/registry.json` remains the existing literal authority for tests and
configs: pack/config bytes, calibration acceptance/estimator, issued artifacts,
sealed registrations, historical pins, evidence and synthetic fixture families.
Preserve every original digest; do not repin changed bytes to make pruning pass.
The source-digest TSV supplements this scope and records source blobs; external
model revisions/digests are metadata, never weight-download instructions.

Retain old-format readers, independent recompute/comparator/twins and main's
history. File-prune PRs must also migrate `HEAD:<path>` and `git log -S` consumers:
`paper_custody.py`, `paper_reported_energy.py`, `evidence_night.py`,
`refresh_receipt_histsem_pinset.py`, `build_v4_histsem_pinset.py`,
`harvest_window.py`, `flags/collect.py`, `digest_pin_census.py`,
`arm_readiness.py`, identity pins and generalized mint. History retention alone
does not make a missing HEAD path readable.

Local tags cannot protect an alternate owner's GC. The complete protection
procedure is [PRUNE-PLAN](PRUNE-PLAN.md): Ed's one server tag ruleset, explicit
tag push and `ls-remote` comparison, full mirror + PR heads + `bundle --all`,
two durable independent copies (never the borrowed SSD), isolated restores,
whole-tip tags on later unmerged retirement, and owner-only disk gates.
