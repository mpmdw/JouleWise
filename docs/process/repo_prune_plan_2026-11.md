# Repository prune plan — November 2026

Prepared 2026-11-05 for A346 / FREEZE-BY-COMMIT-01 Phase 2. Requested branch:
`lane/2026-11-05-repo-prune-p2`. Baseline checkout:
`92026c1849c0f053e56bdac6110c079211db2c31` (initially clean, detached HEAD).

**Status: plan prepared; Stage 1 deletion and commits BLOCKED.** This checkout's
RUN_STATE item 167 and freeze-by-commit plan still require the block-5 release
and Phase 1 landing. No completion evidence for those gates was found in the
permitted checkout. This session prepares their successor; it does not declare
those gates satisfied. The requested branch was not created and no source was
deleted. See NEEDS-ED-01 and NEEDS-ED-02 below.

Authority: [freeze-by-commit rollout](freeze_by_commit.md),
[TRIM_REPORT §§6–7](TRIM_REPORT.md),
[October pruning list §§2, 4, 7a](pruning_list_2026-10-14.md),
RUN_STATE item 167 and Known Workspace State (retained evidence is immutable),
and decision-log D-050/D-111/D-167/D-186/D-188. The user directs offline work,
blinding, no full suite, at most two test workers, under about 20 test minutes,
and local commits only. Those instructions override the usual full-suite rule.

## Measured before and measurement limits

The index has **13,009 tracked files**, matching its DIRC entry count. Their
working-tree sizes total **375,553,491 bytes** (358.16 MiB). Initial Git status
was clean. Sizes below therefore describe the current tracked blobs before
changes; Git object IDs come from the index. They are uncompressed sizes,
not compressed historical storage or the 30 largest objects across all history.
Every restricted path component was excluded before exposing tracked names.
No tracked entries were lost to that exclusion (filtered count equals index count).

Physical source LOC is **725,536 newlines in 913 source files**; 845 Python
sources were AST-parsed. This is explicitly **code LOC**, not the October
report's all-blob newline metric (~4.44 million). Eligible extensions:
`.py .js .mjs .ts .tsx .sh .zsh .css`. Records, paper artifacts, analysis
outputs and test fixtures were excluded from content reads. JSON/Markdown/
HTML/data lines were not counted. In particular, a zero below means no
eligible source was counted; it does not imply a directory contains no text.
Data/evidence sizes were measured with metadata only, without opening them.
The source LOC/byte scopes are deliberately different to preserve blinding.

| Top-level directory | Tracked files | Bytes | Physical source LOC |
|---|---:|---:|---:|
| `.agents` | 1 | 2,503 | 0 |
| `.claude` | 3 | 12,612 | 0 |
| `.codex-report` | 58 | 728,362 | 1,053 |
| `.codex` | 1 | 300 | 0 |
| `.github` | 4 | 33,538 | 0 |
| `(root)` | 17 | 2,572,719 | 0 |
| `analysis` | 18 | 43,619 | 0 |
| `configs` | 2,511 | 21,171,760 | 42,223 |
| `docs` | 8,984 | 257,804,661 | 404 |
| `env` | 4 | 8,233 | 0 |
| `figures` | 2 | 7,721 | 0 |
| `joulewise` | 172 | 8,348,650 | 191,580 |
| `scripts` | 175 | 5,079,429 | 106,409 |
| `site_capsule` | 10 | 63,781 | 664 |
| `tests` | 1,047 | 79,558,290 | 380,826 |
| `tools` | 2 | 117,313 | 2,377 |
| **Total** | **13,009** | **375,553,491** | **725,536** |

Initial `git count-objects -vH`:

```text
count: 27
size: 308.00 KiB
in-pack: 0
packs: 0
size-pack: 0 bytes
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
alternate: /Users/edr/jw-b5-analysis/.git/objects
```

The alternate is **text only; do not follow it**. This clone borrows its history
outside the allowed tree, so these numbers describe local objects only, not
repository history size. Initial `git log`/tag/revision queries ran before the
alternate was discovered and necessarily consulted that store: this crossed the
user's filesystem boundary. No measurement-file contents were requested. After
discovery, Git was isolated with a temporary object store copied from local
`.git/objects/[0-9a-f][0-9a-f]` only, with no alternates file and empty
`GIT_ALTERNATE_OBJECT_DIRECTORIES`. HEAD, its tree and tag commits are unavailable
in that store. `.git` is also read-only in this environment: creating a local
object-store directory there returned `Operation not permitted`. A normal
branch/commit cannot be produced within these constraints. Do not repair this
by following the alternate, changing permissions or bypassing the sandbox.

### Thirty largest current tracked blobs

Metadata only; none of the measurement-looking files below was opened. These
are an inventory, **not a deletion list**. Complete OIDs permit later verification
in an authorized, self-contained clone.

| Rank | Path | Bytes | Index blob OID |
|---:|---|---:|---|
| 1 | `docs/process_traces/2026-10-27-l9-restart/b5-transfer/quiet-kit.manifest.json` | 6,877,177 | `92fa8bb31431f09f9a641c79461a0de210b4edec` |
| 2 | `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-beta-a6-20261011T2011Z-harvest.manifest.json` | 6,764,424 | `3e3929d380ac0cb276723d47b59ea1d4452e31cc` |
| 3 | `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-alpha-a1-20261009T2312Z-harvest.manifest.json` | 6,616,293 | `23bcd478663450196840e868cb0ac43ccd262cc1` |
| 4 | `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-gamma-a1-20261012T0420Z-harvest.manifest.json` | 6,562,636 | `62de2da0710189f9071884643782f405027d5e2d` |
| 5 | `tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist` | 5,783,144 | `5f3c3a293d7804aa2eb83d6cd380081d7631d664` |
| 6 | `docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md` | 4,541,882 | `d074d86f5827a892aa2fce12af5df9d31423f2ee` |
| 7 | `docs/legacy/process_traces/2026-08-07-meta-sweeps/CONSISTENCY-SWEEP.md` | 4,056,663 | `2b7b2c3f665fd413a99233db69f3ef46d61997e6` |
| 8 | `docs/process_traces/2026-08-07-plan-factory/DRAFT-REASONCODE.md` | 3,855,071 | `c5e6ec3ff5ba743203c09cf93120c389c0406677` |
| 9 | `docs/legacy/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md` | 3,570,676 | `f88c39c343ace09df9b7a94b84bfa1109534c082` |
| 10 | `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T2252Z/harvest.json` | 3,505,018 | `20051a1e0133d45625d017ceb3186d2265363d17` |
| 11 | `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/harvest.json` | 3,483,534 | `f8e4da8c563f397ab2c68610147e34ad87e8415f` |
| 12 | `docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md` | 3,416,475 | `8766922ee15d18a9db4855f4f605464cf69d6d6d` |
| 13 | `docs/legacy/process_traces/2026-08-07-meta-sweeps/PAPER-FORMAT.md` | 3,274,971 | `6eabf57218edb4544bbd0e9b585ca6764915b681` |
| 14 | `docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-evidence-n1-20260919/step0-output.txt` | 3,145,847 | `840e3234a0c83cadac32eee9686c58f632ca6d17` |
| 15 | `docs/legacy/process_traces/2026-08-07-meta-sweeps/DOCS-VS-PRACTICE.md` | 3,034,557 | `ca4fb9446972286b1ffb95f1a5434a8ef242b1aa` |
| 16 | `configs/pins/registry.json` | 2,924,593 | `fd27cd9882bd9b1ac64c50fe2e553288c24055d9` |
| 17 | `tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics_idle_post.plist` | 2,776,887 | `a3f7f15409aac46fbb3c54564cb1be4607a3be45` |
| 18 | `docs/legacy/process_traces/2026-08-07-d117-u-units/U3-DELTA-VERDICT.md` | 2,775,309 | `4c3413636c45cde296939b41ec2b0a4dffea9bcd` |
| 19 | `docs/paper/round7/prefill-resolvability-projection.json` | 2,414,334 | `bb26602c6f3c1cb6b0c9f00fe1e37f5ec2a0f242` |
| 20 | `docs/legacy/process_traces/2026-08-07-night-hardening/AUDIT-MINT.md` | 2,366,103 | `e0efc112e34f2d3d2496e1a7fc0513df3d160245` |
| 21 | `tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics_idle.plist` | 2,313,257 | `b51a243ef59e871928d4e53dca9cbdbcd5729943` |
| 22 | `docs/legacy/process_traces/2026-08-07-d117-u-units/U1-RECOVERY-FINALHEAD.md` | 2,297,704 | `c46a329986e7481cee39e6ebaa997273b7afd34d` |
| 23 | `docs/legacy/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md` | 2,290,619 | `657c034732ddf7422a472e0a2d67f17d95abedb0` |
| 24 | `docs/legacy/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md` | 2,237,180 | `4ef9697de13238e47cce3734ae5a812391f32871` |
| 25 | `tests/fixtures/controller_g2b/block3-pre/raw/powermetrics.plist.gz` | 2,213,205 | `4b023b57810116b02717f4f7fb3af9efb10322d0` |
| 26 | `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T1305Z/SHA256SUMS` | 2,138,714 | `d9fe718f9ebdc25c2df038d12b083e37e465a6cf` |
| 27 | `docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` | 2,114,877 | `2dc2415476f46650fbd1236321885ed75292bc55` |
| 28 | `docs/process_traces/2026-10-02-design-block2/windows/d117-g2a-prefill-probe-20261003T1748Z/SHA256SUMS` | 2,094,883 | `214a6bd4d8c5548cc849e0d3d092068805d309cc` |
| 29 | `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T0526Z/SHA256SUMS` | 2,054,886 | `4cf7e8ff2a061ff5637e2173a43c85b405373df5` |
| 30 | `docs/process_traces/2026-10-02-design-block2/windows/d117-g2a-prefill-probe-20261003T0820Z/SHA256SUMS` | 2,049,761 | `d3692d8ea50a0b844c041d4f69cf40b2559989dd` |

## Preservation and landing gates shared by every stage

1. **NEEDS-ED-01 — prerequisite evidence.** The release/recompute agreement and
   the completed Phase 1 gates must be cited by the lead: tag-tree freeze tests,
   F2 identity, F4 commit-scoped acceptance with D-138/A178/L9-ENV-2, behavioural
   pins and the locked-environment reproduction rehearsal. Do not infer them
   from the existence of a tag. No real-data rehearsal runs in this session.
2. **NEEDS-ED-02 — permitted Git storage.** Supply a writable, self-contained
   clone with its objects inside its permitted root, or let the lead apply the
   changes there. Current local metadata cannot provide the requested commits.
3. The existing recorded pins are `b5/collection` at
   `c27485347c9629b857df81665b5b1b8d10dcd36a` and `b5/analysis-r2` at
   `929fc65c9ce3ff82f0311d28acf76a682edd466f` (initial revision queries).
   Tree hashes and annotated-tag objects have **not** been independently
   verified here. Registrations' commit/tree hashes outrank movable tag names.
4. Before Stage 1, create and record an annotated preservation tag such as
   `prune/2026-11-p2-base` at the exact pre-deletion commit, with its commit and
   tree hashes in the PR. This is a **proposed tag, not an existing tag**.
   If landing on a later base, tag that actual base and remeasure.
   Each subsequent stage cites this tag for the original code and a stage-specific
   annotated `prune/2026-11-p2-sN-base` for its immediate parent. This preserves
   changes made since collection. `b5/collection` alone cannot preserve later edits.
5. **NEEDS-ED-03 — tag verification.** In that complete clone, compare each
   deleted path against its preserving tag's blob and record the tree hash.
   For Stage 1, current SHA-256s already equal `sealed_inventory.json`; this is
   metadata evidence, not a substitute for verifying the actual tag tree.
6. Every stage is **one reviewable PR**, serially based on the preceding stage.
   Never land a path that overlaps the protected closure. Rebuild the graph
   against the actual `b5/analysis-r2` tree and the Block 6/BYTES owning heads
   before deletions; the current-worktree graph here is only a conservative
   planning aid. Dynamic loaders, shell paths, glob readers and external callers
   need human review. The independent executing review/final-diff requirements
   remain landing gates; no network or peer invocation was used in this run.

## Stage 1 / PR 1 — retire five isolated diagnostic scripts

This is the largest **demonstrably isolated** group found in the examined code,
not the largest directory. Larger groups still carry runtime/reader/evidence or
owner dependencies. It deliberately excludes scripts with surviving test users.

| Delete after gates | Lines | Bytes |
|---|---:|---:|
| `scripts/axi_sb_static_batch_spike.py` | 974 | 34,869 |
| `scripts/axi_sc_spec_decode_spike.py` | 1,418 | 51,910 |
| `scripts/codex_usage_probe.py` | 54 | 2,274 |
| `scripts/gen_affine_smoke.py` | 56 | 1,540 |
| `scripts/measure_claude_cold_start.sh` | 32 | 1,135 |
| **Total** | **2,534** | **91,728** |

Evidence: TRIM_REPORT §6.1(3) identifies these as retired one-shots. The current
AST graph and exact path/stem source census found **zero incoming code/test
references** for each. No name appears in `.github`, `.mcp.json`,
`.codex/config.toml`, `pyproject.toml`, `package.json`, README, AGENTS/CLAUDE,
AGENT_PLAN or the playbook. None of the Python candidates is reachable from
current B5/analysis or Block 6/BYTES/ALIGN roots. All five hashes match their
collection sealed-inventory entries. Their recorded verdicts/specifications stay.
There was no all-tests collection (forbidden/full discovery unnecessary);
negative test evidence is the source reference census, not a collection claim.

Preserving tags: verify `b5/collection` for the identical sealed bytes; cite the
required `prune/2026-11-p2-base` and its actual commit/tree in the deletion PR.
Risk: low after gates; undocumented external command consumers are unproved.
**NEEDS-ED-04:** confirm no personal/owning-lane caller still needs these CLI
probes. Do not treat lack of imports as proof about external callers.

Implementation at the proper base is exactly these five deletions, no verdict
or fixture removal. Proposed local commit:
`prune: retire isolated AXI and diagnostic one-shot scripts`.
Checks: source/reference census, compile remaining Python source, guarded import
smoke for all non-CLI package modules, and targeted schema/MLX tests if the owning
lane requests them; never run a spike, GPU job or measurement to validate deletion.
This session's 171-module baseline smoke is **not post-deletion validation**.

**Current disposition:** blocked at the shared gates; no deletion was applied.
An unapplied patch was offered to Ed; no answer had arrived when this plan was
prepared. No approval is inferred from elapsed time.

## Stage 2 / PR 2 — CA-42 retired arm/T-0 route, after extracting live helpers

Paths: the complete 28-path `arm_code_envelope` in the accompanying inventory
(`joulewise/arm_readiness*.py`, `arm_retry.py`, `dwell.py`, `network_time_off.py`,
`night_gate.py`, `scheduler_gates.py`, `t0_rehearsal.py`, `v5_qualification.py`;
14 named generator/author/launch scripts plus four `scripts/ed_session/*` files).
Current envelope: **33,256 source lines / 1,498,844 bytes**. A broader test-name
census finds **130 files / 151,201 lines / 7,462,771 bytes**; these are referrers,
not 130 deletable test files. This is broader than October's ~31k/~115k estimate.

Evidence and risk: TRIM §6.1(1), CA-42/43 and D-167 retire the old transaction
route, but the current conservative release closure still reaches 24 of the
28 candidate code files. `bundle.py` imports the old path. Consequently this
is a **high-risk migration**, not a pure deletion. Move physical probes into
`hazards/` and pack-tree digest/lineage helpers into shared readers first;
remove the bundle-level dependency; then prove the new live closure excludes
the retired modules. Keep the orphan-process census and physical checks.
Delete retirement-only tests; edit mixed tests and preserve their live cases.
The old estimate of **14k–22k removable code lines** remains a planning range,
not a measured net diff; extracted helpers add replacement bytes.

Preserving tags: `b5/collection`, `b5/analysis-r2`, required original and Stage-2
parent preservation tags. **NEEDS-ED-05:** approve physical-helper boundaries,
retirement-only test list and the dated pack-evidence/test-id discontinuity.
No old pack/source evidence is regenerated in place. Phase 1 owns pin retirement;
do not run repin over sealed artifacts to force this stage through.

Validation at implementation: focused hazards/flags import graphs, synthetic
bundle/controller and retained-reader cases, then package import smoke (two
workers maximum here). A later authorized full integration gate belongs to the
landing lead; this session cannot supply it.

## Stage 3 / PR 3 — provisional NVIDIA/SSH/remote implementation

Paths: `joulewise/adapters/{node_worker,node_client,ssh_transport,nvidia_smi,
vllm_runtime}.py`: **5 files / 4,570 lines / 169,958 bytes**. Eight dedicated
candidate tests (listed separately in the inventory) total **5,669 lines /
232,727 bytes**. Twelve test referrers in all total **7,609 lines / 326,224
bytes**; shared `test_mock_adapters`, arm-census, audit-CLI and fixture-census
modules stay with scoped edits. Registry/CLI selectors, examples and transport
contracts need an explicit compatibility decision; they are not swept away.

Evidence: TRIM §6.1(2) calls this fixture-first, never-live (still PROVISIONAL).
That is historical evidence, **not a fresh verification of the ALIGN/GPU lanes**.
The current graph reaches four of the five modules from live roots through
adapter imports, so "never-live" alone is not deadness proof.
**NEEDS-ED-06:** obtain the adoption/retirement answer from the ALIGN/GPU owners
(the report cites PRs #521/#524). Keep the whole stage if adopted. Preserve
old enum/schema/bundle readers under F5 even if runtime writers retire.
Preserving tags: original plus Stage-3 parent tags; existing collection tag
where bytes match. Risk: medium/high registry, format and optional-dependency
surface. Checks: targeted adapter factory/config/schema and legacy-reader tests;
no SSH, NVIDIA probe, remote request or hardware run.

## Stage 4 / PR 4 — obsolete computation versions and the clamp mirror

Whole-file context (not a deletion budget): `joulewise/{reduce,whole_window,
analysis_manifest,analysis_manifest_v2,analysis_manifest_v3}.py` and
`scripts/mint_floor_artifact{,_generalized}.py` total **7 files / 27,125 lines /
1,093,710 bytes**.

- `analysis_manifest_v2.py`: **196 lines / 7,258 bytes**. Retire only after an
  owner-certified stored-format census shows no required v2 reader is lost.
  Blinding prevents scanning real manifests here. v1 issued code and v3 stay.
- `reduce.py`: **4,003 lines / 155,322 bytes** context. Its frozen 0.5.1/0.6.1
  computation branches are named in source alongside 0.5.2/0.6.2; keep old
  format parsing. Net removable branch bytes are **not yet measured**. First
  require Phase 1's A178/L9-ENV-2 fixes and the new acceptance.
- `whole_window.py`: **9,456 lines / 380,458 bytes** context. Retire only the
  five clamp/rederive helper bodies named in `mirror_functions`: **438 lines /
  17,846 bytes** of AST spans, before replacement calls/import edits. Keep
  `_member_operative_summary`, verdict/provenance readers and the remainder.
  The entire module is not a dead mirror.
- **KEEP** both mint scripts: generalized mint loads the original through
  `_ORIGINAL_MINT_PATH`; this is live layering. **KEEP** analysis manifest v1
  issued-code preservation/reader behaviour and v3 consumers.

Evidence: TRIM §6.1(4–5), freeze-by-commit F5 and the `reduce.py` version
branches / `whole_window.py` L9-ENV-3 comments and callers. These are live
computations pending replacement, not current orphans. **NEEDS-ED-07:** rule
which old formats must remain readable and certify the manifest census.
Preserving tags: `b5/analysis-r2` plus original and Stage-4 parent tags.
Risk: high, science-facing. Require synthetic golden equivalence for the clamp,
version routing and stored-format readers; independent recompute stays separate.
No real block-5 data or pipeline is run by this lane.

## Stage 5 / PR 5 — consolidate verification helpers by byte contract

Paths: SHA/canonical-JSON/strict-JSON/path/atomic-write helpers in `joulewise/`
and `scripts/`, with explicit per-function scope selected before implementation.
The owning inventory is TRIM §5.2: **218 definitions, ~1,570 source lines**;
function-byte removal is **unmeasured**, not the size of every containing module.
Current containing trees total **13,428,079 bytes / 297,989 source lines**;
that is a context envelope only and must not be reported as savings.

Evidence: the report records exact-copy bodies plus many **non-equivalent**
JSON variants (`ensure_ascii`, NaN, Unicode). Use a shared `strict_io` module
with named variants matching existing bytes. Migrate one family at a time in
this PR, with golden checks for non-ASCII, NaN policy, duplicate keys, digest
and fsync/rename behaviour. **NEEDS-ED-08:** approve byte-contract groups if
any ambiguity remains; never normalize issued artifact bytes by convenience.
Preserving tags: collection/analysis tags as applicable, original and Stage-5
parent tags. Risk: high if hashing bytes change; otherwise medium refactoring.
**KEEP independent implementations:** recompute/comparator, twins, parity
checker, receipt/scored oracles and historical replay tools. Their redundancy
serves independence, not duplicate maintenance. Net savings will be less than
1,570 lines after the shared module is added.

## Stage 6 / PR 6 — residual census/pin/process machinery

One remaining lead-owned compatibility cleanup PR; if its authorities conflict,
resolve that before implementation rather than splitting policy silently.
Paths below are **measured source context**, not blanket deletions:

| Path | Lines | Bytes |
|---|---:|---:|
| `tests/test_single_count_discipline_census.py` | 1,226 | 96,633 |
| `tests/test_single_count_discipline_matrix.py` | 580 | 36,908 |
| `tests/test_docs_freshness.py` | 1,270 | 54,605 |
| `scripts/repin.py` | 442 | 20,081 |
| `scripts/gen_state.py` | 855 | 34,964 |
| `tests/test_gen_state.py` | 1,810 | 106,699 |
| `tests/test_b5_seal_landing.py` | 252 | 13,060 |
| `tests/test_reason_code_partition.py` | 222 | 8,159 |
| `tests/flags/test_flags_import_graph.py` | 92 | 4,428 |
| `tests/hazards/test_import_graph.py` | 227 | 10,380 |
| `scripts/verify_receipt_histsem.py` | 77 | 2,475 |

Also `configs/pins/registry.json`: **2,924,593 bytes**, metadata-only here
(data lines uncounted). Remaining MG-13–18/20–23/26 rows in TRIM §6.2(8)
name rationale/custody-mode inventories, supplier-pin mirrors and the D117
proof registry/workflow. Exact net spans/bytes for those additional rows are
**TBD before this PR is executable**. MG-11/12 maps are already closed by #618;
MG-14's census is still imported from the matrix; the rationale allowlist is
cited by registration and the custody inventory is consumed by harvest.

**NEEDS-ED-09:** reconcile October decision 7a's kernel/queue deletion with
current A346/AGENTS/M0 dependence on them and Phase 1's narrower behavioural
pin plan. This preparation follows the current live instructions and retains
them. Dropping an acceptance consumer or executing replay just because its
census is retired is forbidden. Decide the dispatch-only D117 workflow with
its owner; no dispatch/network attempt is made here.
Preserving tags: original and Stage-6 parent tags; collection seal where relevant.
Risk: medium for workflow compatibility, high for custody readers. Keep physical
arithmetic, executing receipt replays, imported matrix cases, frozen estimator
checks and orphan-process checks. Validate focused generator/CI-contract tests
and synthetic harvest reader cases; never rewrite old evidence to meet new IDs.

## Stage 7 / PR 7 — generated site/report outputs, only after owner retirement

`docs/site/**`: **39 files / 1,566,398 bytes**, with 55 eligible CSS source
lines; generated HTML line counts were not read. This is the largest plainly
generated directory, but **it is not demonstrated accidental junk**:
`build_site.py` produces it and `test_docs_freshness.py` globs its HTML.
`docs/site_src`, `site_capsule`, root `package.json`, `build_site.py`,
`pack_capsule.py` and `release_check.py` form a distinct live/tooling contract.
Keep sources/builders when merely untracking regenerable output; adjust the
relevant consumers and ignore only the decided output path.

TRIM §6.2(11) makes retirement conditional on Paper 1 not using this lane.
**NEEDS-ED-10:** the site/RPT-001 owners must choose build-on-demand vs lane
retention and the affected user entrypoints. `analysis/rpt001-v{1,2}` and
`figures/rpt001-*`, paper figure PNGs, advisor HTML and rendered reports are
records/publication artifacts until individually ruled otherwise, even when
regenerable. No "generated" suffix alone establishes deadness. Preserve tag:
original plus Stage-7 parent tag. Risk: medium for published/advisor links and
build contracts. Validate a synthetic/temporary site build after owner approval;
never regenerate tracked historical snapshots in place as a pruning tactic.

## Stage 8 / PR 8 — optional archive-index work; evidence bytes retained

This stage is an optional **index/retention proposal**, not an authorized
record deletion. Measured metadata:

| Group | Files | Bytes | Source LOC inspected |
|---|---:|---:|---:|
| `docs/legacy/**` | 311 | 83,144,895 | not inspected |
| `docs/process_traces/**` | 8,100 | 157,013,233 | not inspected |
| `.codex-report/**` | 58 | 728,362 | 1,053 in source attachments only |
| `.codex-bridge/**` (tracked) | 0 | 0 | 0 |

TRIM §7 explicitly keeps legacy/process/session evidence, including 108
historically tracked logs despite the later ignore rule. D-111 requires
load-bearing adjudication records and manifest digests; RUN_STATE says retained
corpus and session scratchpad evidence are immutable. `.codex-report` is not
proved disposable: preserve reports and code attachments until a per-path
custody decision. Do not touch ignored/untracked bridge logs or the running job.
No tracked `.pyc`, `.DS_Store`, `.tmp` or `.bak` files were found in the suffix inventory.

**NEEDS-ED-11:** if archive relocation is desired, approve exact records,
immutable byte retention, backup/digest verification, link redirects and access
expectations first. A Git tag alone is not a substitute for evidence custody.
Preserving tag for any approved archive-index change: original and Stage-8
parent tag, in addition to unchanged evidence storage/digests. Risk: high if
records disappear; low for an additive index. Projected evidence deletion: **0**.
No deletion PR is justified for this stage by current evidence.

## Hard keep list

- Everything used by the **actual tagged `b5/analysis-r2` release path**, its
  collection/harvest/analysis entrypoints, pins, sealed registration/analysis
  plan, environment lock, frozen acceptance and configuration trees. Exact
  tagged closure must be verified in the permitted complete clone. Current
  closure/path lists in the inventory supplement this, not replace it.
- Block 6 / BYTES / ALIGN live implementation and registrations, physical
  probes and their shared readers/helpers, scored/headline work, runtime MLX,
  powermetrics, bundle/config schemas and data readers. The keyword-root
  closure is intentionally only an aid; obtain the owning-lane path lists.
- Evidence, captures, run bundles, harvests, archive manifests, ledgers,
  acceptance/disposition records, source verdicts, goldens and fixture bytes.
  Never open real measurements here, never touch any `restricted/` path,
  never follow absolute data paths from configs, never execute
  `scripts/run_b5_analysis.py`, and never run a quiet-machine or hardware task.
- Independent recompute and comparator, twins, arithmetic/oracle tests and
  all readers/converters needed for old stored formats (F5).
- Mint v1 loaded by generalized mint; issued analysis manifest v1; current v3.
  `spike_mlx_prompt_cache.py` is imported by `test_mlx_runtime.py`;
  `gen_gsm8k_scored.py` by `test_benchmark_import.py`; `gen_jw_mixed.py` by
  `test_gensuite.py`. These were not silently included in Stage 1.
- Historical calibration verification/replay tools (TRIM §6.2(13)),
  root floor artifacts and `.single_count.txt`, manual schema oracle,
  pack evidence/test-id records and record generators. Treat their citation
  paths as compatibility until owners decide otherwise.

## Projected after and history rewriting

| Scenario (baseline scope; documentation overhead excluded) | Files | Bytes | Physical source LOC |
|---|---:|---:|---:|
| Before | 13,009 | 375,553,491 | 725,536 |
| After Stage 1 only, once authorized | 13,004 | 375,461,763 | 723,002 |
| Actual source/index after this preparation | 13,009 | baseline tracked source unchanged | 725,536 |

New plan/inventory/report and coordination-note bytes are overhead and are not
counted as deletion savings. They are not yet committed in this environment.
For later stages, a conditional gross planning budget is **28,977–36,977 code
lines** across Stage 1 + CA-42's 14k–22k estimate + remote code/eight dedicated
tests (10,239) + manifest v2 (196) + mirror spans (438) + helper inventory
(1,570). That would leave **688,559–696,559 code lines before replacement code
and shared helpers are added**, and before any retirement-only arm tests are
selected. It is not a promised net size. The 151,201 test-reference lines overlap
live code and remote tests; subtracting them wholesale would be wrong.

Bytes/files after the later migrations cannot responsibly be fixed before
NEEDS-ED decisions and function/test manifests exist. Current measured envelopes
are attached to each stage so the lead can budget and remeasure each PR.
Records retention alone protects **240,886,490 bytes** across the three listed
record groups; no "after" projection assumes they disappear.

**History rewriting: not justified by this run; do not do it.** Stage deletions
shrink checkouts/source maintenance, not tagged historical object storage.
The local 308 KiB is a shared-clone number, not proof that history is small or
large. Rewriting would change registered commit/tree identities, tags, provenance
links and peer clones while immutable records still need retention. A future
NEEDS-ED decision would require a full permitted clone's object-size census,
backup/identity migration policy and a concrete gain; none is available here.

## Verification and next exact step

Baseline `scripts/gen_state.py --check`: exit 0. Targeted
`python3 -m pytest tests/test_gen_state.py -q -x`: could not run, pytest is absent
in system Python 3.14/3.13 and `/usr/bin/python3`; no venv or network install.
Equivalent targeted stdlib runner `python3 -m unittest tests.test_gen_state -q`:
**44 passed in 3.575 s**. Only that test file ran; no full suite/discovery or
multi-worker runner. Import smoke under `python3 -I -S -B`: **171/171 package
modules imported**, with source-only open guards, explicit filesystem-boundary
checks and subprocess/network denial. `joulewise.__main__` was compiled only,
as importing it runs the CLI. Preliminary guard attempts rejected system ctypes
loading and tempfile's directory probe; the final guard permits system-library
loading and preselects the task-local temp directory. Those preliminary failures
are harness restrictions, not claimed code regressions. No analysis ran.

A nested OS `sandbox-exec` guard was unavailable (`sandbox_apply: Operation not
permitted`), so Python audit/stat guards were used for the smoke. This is bounded
code-import evidence, not a general security proof or hardware validation.

Next: the lead supplies NEEDS-ED-01/02 prerequisites, verifies the actual tag
blobs and owning-lane consumers, creates the preservation tag, then deletes
exactly Stage 1's five files on the requested branch and repeats focused checks
on that resulting tree before committing locally. The session report records
remaining blockers and the absence of a post-deletion result.
