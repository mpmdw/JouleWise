# BLIND-DRY-RUN-SCOUT

Report-only scout, 2026-10-23 UTC. Repository: `mpmdw/JouleWise`.
Requested branch: `report/2026-10-22-blind-dry-run-scout`.
Main snapshot: `7c23ea4b71622f7a898617a66da48868e20562a3`.
No blinded archive, export, calibration capture, exclusion-code file, or numerical output was opened. No measurement or test was run. Only this report is in scope.

## Finding

Block 6 is collected and closed, but its analysis/release path is not ready. The critical path is:

**finish L9 joined acceptance and S11 records → pin/land L9 → block-5 blind dry run and recomputation → block-5 cold release and deterministic replay → finish/pin block-6 analysis additions and open slots → block-6 blind dry run over every session and independent recomputation → cold release record → identical-byte release replay.**

Block-6 synthetic implementation and record preparation can proceed alongside L9. Registration §12.2 permits blind analysis as sessions arrive, but §13 requires the released L9 program plus reviewed block-6 additions; block-5 release is an absolute prerequisite to opening block-6 numbers. Neither BYTES H nor another collection campaign is a science prerequisite to this release.

## Authority and snapshot

Read: `AGENTS.md`; Mission M0 in `docs/agent_playbook.md`; `docs/orchestration.md`; `AGENT_PLAN.md`; `RUN_STATE.md` (active stop card, current/workspace sections, items 53–65 and their next-action continuations); registered `docs/registrations/block6_replication_DRAFT.md`; block-5 registration/plan and seal record; targeted L9 rulings, source and branch reports.

`RUN_STATE.md` items 64–65, especially lines 237–248, supersede earlier “Mac is free” directions: Ed paused the whole workload and `ops/stop-pause` holds new arms. Cloud forward work remains authorized. The generated older queue/status prose does not override this explicit scout or the current pause. `TASK_QUEUE.md` returned empty content through the connector; no queue update was inferred or made.

The block-6 file is **REGISTERED 2026-10-17** despite “DRAFT” in its filename. The dated filled text governs stale “still open” language in S-5. All dates/statuses below are evidence snapshots, not claims about the Mac's present process state.

## Code, branches and PRs

| Component | Where the code/evidence lives | What it waits on |
|---|---|---|
| Block-6 collection/stage 1 | `integration/2026-10-14-b6-stage1` → `lane/2026-10-16-b6-round2`, draft **#499** → `lane/2026-10-17-b6-packs-registered`, draft **#502** | These are still open/unmerged. #499 targets the stage-1 branch; #502 targets round2. #502 explicitly says it must not merge before block-5 release (§7). |
| Frozen block-6 measurement code | S-1 pin `f31aca19f` on the registered-packs line; measurement checkout `/Users/edr/night-custody/measurement/JouleWise-measurement-20261018T0023Z-b6` | Collection is finished. Do not replace this pin with a newer analysis checkout or rewrite its harvests merely to land code. |
| Stage-2 blinding/export | `joulewise/b6/blinding.py`, `export_runs.py`; `scripts/b6_export_runs.py`, `b6_unblind.py` on #502 | Already built (item 54 corrects item 53). Export/factor removal is not the registered replication-analysis driver. |
| Block-6 analysis | `joulewise/b6/analysis_lane.py` on #502 | It remains a capability stub: `AnalysisLane.precision_reached(...)` returns `None`; no registered estimator entry point is connected there. A complete §13 driver, session index, independent comparison and release-record schema/CLI were not found on the cited line. Do not invent a runnable `b6_analyze.py` command. |
| L9 base analysis | `lane/2026-10-07-l9-analysis`, later `lane/2026-10-13-l9-s10` | Historical stages are not final ruling-build acceptance. |
| Current L9 ruling build | `lane/2026-10-20-l9-ruling-build`, draft **#513**; `.codex-report/l9-ruling-build.md`, newer `.codex-report/L9-1.md` | Complete current-source joined acceptance, S11, final CI/review/cold passes and merge ledger. Live #513 head observed: `92cdfd7502abed57dfd7bc7e4626ef14d4dbc28f`. |
| L9 CI integration | `ci/2026-10-21-l9`, draft **#517** (`82f1ddf4a`) | Contains the earlier `c11402cf6` build plus authentication-I/O census refresh and main. It is not final acceptance for newer #513 code. |
| L9 sensitivity fix | `lane/2026-10-21-l9-sensguard`; item 62 `a1e73a074`, newer report tip `e77ba9e42` | Reconciled into #513 according to L9-1; confirm final ancestry rather than cherry-pick it twice. Earlier 948-test green evidence is not J1–J6 acceptance. |
| Independent arithmetic | `lane/2026-10-14-independent-recompute`, `scripts/independent_recompute_b5.py` | Pin the reviewed version; run comparison in restricted custody. B6 needs its registered counting/pairing/rules and S-13 comparison, not an unmodified B5 `claim_usable` veto. |
| BYTES shared ancestry | B1 `lane/2026-10-20-bytes-integration` at `d924e7acf`; B2 `lane/2026-10-20-bytes-analysis-a8`; draft **#515** on `ci/2026-10-21-b2-nr1` (`de75fbabb`) | Item 60 holds landing: B2 would bring B1 and #499/#502 ancestry onto main. Lead must choose separate-ledger or combined landing, while respecting #502's block-5-release hold. A green B2 ledger does not clear the inherited B6 line. |

Completed collection prerequisites to retain in the ancestry/evidence map: **#500**, `fix/2026-10-16-watchdog-b6-bindings`, is merged to main (`ad31062e9`), gates `docs/process_traces/2026-10-17-magistrate-1a1261a5/pr500-gates.md`; **#501** fixed busy-only admission, idle-skip stage interpretation and smoke handling, merged into the round-2 line (`5b58cfa06`), gates `docs/process_traces/2026-10-17-magistrate-d34bf254/pr501-gates.md`. These are completed prerequisites, not new pending fixes. Registered acceptance/registration gate records are `docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-{fable,opus}.md` and `docs/process_traces/2026-10-17-magistrate-52d50d1f/reg-ruling-{fable,opus}.md`; preserve them with S-1 evidence.

#515's recorded integration size was 123 commits in item 60; live PR metadata now reports 137. This is branch movement, not permission to assume the old reviewed tree is current. BYTES B4 → B3 twin → B5 kit → item G is the subsequent BYTES merge path, **not** a block-6 science-release prerequisite. H PRs #516/#518 and the paused physical run do not hold block-6 analysis.

Relevant process records:
- `docs/process_traces/2026-10-20-magistrate-c634f6f3/RECORD.md` (item-53 counting defect).
- `2026-10-20-magistrate-4b350f47/L9-RULING.md` and `2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md`, under `docs/process_traces/`.
- `2026-10-21-magistrate-283e9802/RECORD.md`, `B2-NR1-COLD-DISPOSITION.md`; `2026-10-21-magistrate-c5a1d8fd/RECORD.md`; `2026-10-21-magistrate-a69c5394/RECORD.md`; `2026-10-21-magistrate-f1f6b9f1/RECORD.md`.
- External handoff `/Users/edr/night-archive/forward-20261021/STATE.md`; external L9 issue list `/Users/edr/night-archive/b5-consults/l9-rulings/OPEN-ISSUES-s4-s9.md`. These local papers were **not accessible/verified** by this scout.

## Exact dependency order and gates

### 1. Complete L9 on one identified final source

Reconcile main, #513, sensguard and #517's census change; preserve concurrent histories. L9-1 records integration `fc43ced491`, runtime baseline `ee98a1a8f`, sensguard `e77ba9e42`, concurrent lane `507bd16e2`, main `7c23ea4b7`. New main changed `joulewise/analysis_engine/distributions.py`, and S10 Git/fixture initialization changed, so prior-source acceptance is not final-source acceptance.

Required synthetic end-to-end checks: **J1–J6 and C5–C9**, through real programs and production-shaped full-size archives. C6/C7's removed/subsumed work is covered by the current chain sequence; do not manufacture extra commands for retired steps. Required modules:

| Module | Purpose / current evidence |
|---|---|
| `tests.b5_analysis.test_chain_fixture` | Real extraction/mint/finalization/claim chain (C5/C8/C9). Prior-source 32 tests passed; current-source rerun pending in L9-1. |
| `tests.b5_analysis.test_dry_run` | J1–J5, real source-cell census, limitations and validated fill boundary. Prior-source 62 tests: **2 failures, 1 error**, exit 1. |
| `tests.b5_analysis.test_release_equality` | J6 release after dry run and exact equality across two custody roots. Prior-source 12 tests: **2 failures**, exit 1. |
| `tests.b5_analysis.test_joined_probes` | Restored-unit real validator/tripwire and disclosure opener. Prior-source both methods failed. |
| `tests.test_authentication_io`, `tests.test_docs_freshness`, `tests.b5_analysis.test_sensitivity_guard`, `tests.b5_analysis.test_mint_kept_units`, `tests.b5_analysis.test_s10_chain_defects`, `tests.test_r4_acceptance_oracle` | Other six modules in current ten-module ledger have completed successfully; mint records one declared cache skip. The skipped chain-dependent check must have appropriate chain evidence; a skip alone is not execution. |

Actual unresolved failure: real driver stops at **9b**, exit 2, `unclassified_refusal`, restricted stderr `paper_custody_validator_refused`; steps 10/11 do not run. Failed dry-run methods are J3, J4 and `test_L9_real_chain_floor_inventory_sources_and_fill_boundary`. Both real J6 drivers stop at 9b and release refuses the incomplete-dry-record preflight. Reported nested validator reasons include `claim_verdicts_replay_refused` / `whole_window_verdict_provenance_invalid`; ownership remains unclassified. Cold exact-byte opener and preparation controls admit, but **do not replace failed full-driver acceptance**. An observer-free diagnostic reached step 11 with no completed outcome yet. New-source dry/probes/J6/chain results were still pending in the read report.

Finish/fix these blind, add defect-earning synthetic regressions where needed, then independent executing review, dispositions, applicable delta checks, whole suite on the current merged candidate, final-head CI, blind executing Fable and Opus cold passes, final diff/ledger read, and lead merge. Review/gates are tied to the actual final code, not old green tails. This report-only seat runs none of these tests.

### 2. Close S11 and block-5 analysis records before real dry run

Authorities: `configs/campaigns/v5_claim_25g83/registration_block5.md`; `analysis_plan_block5.md` §§2, 3, 11, 13; `docs/process_traces/2026-10-block5/l9-rulings/DECISIONS.md` §4; `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`.

Required records/inputs:
- Tracked `configs/analysis/b5/analysed_windows.json`: every attempt/history, selected attempt, archive/runs roots, authenticated governing harvest pin, no unresolved UNCLASSIFIED analysed attempt. It is **absent on inspected #513**; the directory contains `seal_pins.json` and `dry_run_refusal_classes.json`.
- First claim-usable block-5 attempt per pack, immutable: **ALPHA a1, BETA a6, GAMMA a1**. Retain all failed/superseded attempts as history; no re-selection by value.
- Authentic sealed pack/config/manifests, raw bundles, archives, exclusions, terminal-pinned archived calibration ledgers, bracket/NEG-8 survivor/allowance records, and all custody locators readable by automation. No evicted historical ledger-referenced capture may be silently treated as absent.
- External analysis custody root, complete immutable input census; final pinset and v2 mint input manifest; extraction reports, aggregate floor/replay sidecar; finalized GAMMA manifest; dominance close-out; claim verdict; each reported-cell issuance; disclosures and validated fill input.
- Seal-record **analysis addendum**: analysis commit/file digests; L9 rule and “(d)” dispositions; every remaining PLAN §13 FILL. The sealed plan is not casually rewritten.

The index must authenticate each governing historical harvest program, rather than re-harvest everything with newest code: ALPHA a1 (`v5-b5-alpha-a1-20261009T2312Z`) uses `224a264c5` on `lane/2026-10-09-harvest-corpus-cap`; BETA a6 (`v5-b5-beta-a6-20261011T2011Z`) and GAMMA a1 (`v5-b5-gamma-a1-20261012T0420Z`) use `b039c0257` on `lane/2026-10-11-harvest-trigger-scope`. The intervening history uses `0699abbb0` on `lane/2026-10-10-harvest-screen-sources` where Seal Addenda 3/4 govern. No PR number is recorded for these pins in the inspected authority; do not invent one. Source records: `docs/process_traces/2026-10-block5/seal2-beta-a6-window.md`, `seal2-gamma-a1-window.md`, and seal-record Addenda 2–4. Preserve failed BETA attempts; prospective errata cannot rehabilitate earlier attempts for deciding evidence.

Before any number, L9 must check `excluded_reference_in_screen` (RUN_STATE item 33; `l9-rulings/RULING.md` J4). If it fires, only that window is re-harvested at a newly admitted pin after a cold gate; if it becomes not claim-usable, that pack has no analysed attempt and is **not re-armed**. Every consumer uses the window's own bracket timing bound and refuses a conflicting member bound (`DECISIONS.md` B1); a contrast's floor retains its producer window's drift allowance. None of these can be bypassed to make the joined run green.

All post-seal FILLs to disposition: `B5-ANALYSIS-CUSTODY-ROOT`, `B5-BLIND-DRY-RUN-RECORD`, `EXCLUSIONS-CONSUMER`, `L9-NEG8`, `REPORTED-ENERGY-ISSUER`, `FLOOR-EXTRACTION-KEPT-UNITS`, `GAMMA-MANIFEST-EXCLUSIONS-BINDING`, `V5-FINAL-PINSET`, `V5-V2-INPUT-MANIFEST`, `MINT-TO-CLOSEOUT-ADAPTER`, `CLAIM-VERDICT-TO-FILL-ADAPTER`, `DISCLOSURE-PRODUCER`, `DISCLOSURE-SITES`. PLAN lines 776–783 place their fills in the seal-record addendum.

PLAN §3.1 order is **1 strict validation → 2 restricted re-reduction → 3 kept units → 4 ALPHA/BETA extraction → 5 aggregate mint/replay → 8 GAMMA finalization → 6 dominance close-out → 9 claim gate → 10 per-cell issuer → 11 disclosures/fill**. The driver additionally records setup/adapter steps 0, 3b, 9b. Step 7 was removed. Step 6 is deliberately after 8, since it consumes the finalized manifest.

The ruled step-11 deviation ends at validated `results-fill-input.json`, with `results_rendering_not_run_no_block5_template`; it does not require inventing a Window-A-derived renderer before dry-run completion. A later Results renderer must preserve every row/status and pass the Results cold gate before paper use.

### 3. Block-5 blind dry run, recompute, release

Pin/land the accepted L9 program and complete S11. Run steps 1–11 on actual immutable bytes under automation, with every numerical output closed. Cure tooling refusals blind and restart in a fresh custody root. Registered scientific outcome refusals remain results; physics refusals are not “fixed” by changing tolerances or selecting other data.

Required: completed `<custody>/dry-run/B5-BLIND-DRY-RUN-RECORD.json`, restricted outputs under `dry-run/restricted/`, independent raw-record recompute and comparison evidence, and the analysis pin/addendum. The independent script must not use `--diagnostic-ignore-exclusions` for deciding evidence.

Then the lead assembles the cold release packet and records release in `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`, tying sealed registration/plan/catalog/errata digests to final harvest records. Its inspected “Release event” section still says **“Nothing is recorded here yet.”** Follow the user's cold-gate requirement; do not infer release from a successful synthetic test.

After the recorded event, run release mode on the same inputs, pin, index and custody root. Require every input/output digest equal to dry run, exactly. `release_digest_differs_from_dry_run` stops analysis. Expected record: `<custody>/release/B5-RELEASE-RECORD.json`. Establish the L9 release tag required by block-6 §13; no tag name is supplied in the governing text, so do not guess one.

### 4. Finish block-6 analysis and remaining registration slots

| Prerequisite | Waiting on / allowed work now |
|---|---|
| Item-53 counting defect | r2-GAMMA is registered **counting**, but old `exclusions.json` says `claim_usable:false` from the retired B5 `neg8.midpoint_lost_primary` rule. Build consumer taking loop acceptance as authority, or make the writer apply B6 §8.2 consistently. Synthetic regression now; automation-only validation against r2-GAMMA's real file before deciding dry run. Never open that restricted file in a seat. |
| **S-11**, longest non-claim smoke target-phase duration per pack/phase | Retrieve existing smoke records in automation; use longest if they differ. The M15 decode-only kit is not the registered source and supplies no required prefill smoke. Check existence first; if genuinely absent, new physical smoke needs Ed's pause lifted. |
| **S-9**, idle GPU/ANE exclusion | Derive per pack/phase `P* = F_min / (4 × T_phase)`, using registered `F_min = 1.9 J` and S-11. This is the registered quarter-floor interference budget, not a fitted pass bar. Compute at desk from preserved idle-baseline rails; round-1 `power.pstar_unsized` was a flag, not permission to omit analysis. |
| **S-14**, reviewed/pinned analysis commit | Released L9 tag plus B6 driver/additions: correct counting, per-session kept-unit computations, pairing, descriptive between-session mean/sample SD, side-by-side B5/B6 table, replication word, flagged-inclusive line. Full-size synthetic real chain, independent executing review/dispositions, blind executing Fable and Opus passes, then pin before real dry run. |
| S-14 associated obligations | S-8 outside-CPU labelled alternative: C, k, C−k×c_q and E_add per flagged run. The exclusion was not adopted for round 1; do not make it primary. Whole complete-cell issuer must equal `_project_cell` exactly; correct GAMMA estimator metadata (§9 lines 907–909). Remove any stored hidden export factor before printing; preserve raw exports/keys. |
| **S-15**, whole-machine phase definition | Commit the block-5 definition and its clock/alignment uncertainty; carry the same definition to B6. Request-level battery assist does not become a fabricated phase allocation; do not add GAMMA whole-machine phase numbers where §9 excludes them. |
| **S-16**, new/changed-rule replay counts | After B5 release, structurally replay every new/changed §8 rule on B5's usable sessions, print removals beside original rules. Rehearsal counts alone do not fill this slot. Deadline B6 release. |
| Independent recompute and comparator | Adapt/pin independent arithmetic to every B6 session, authoritative counting and pairing; compare run phases and all unrounded printed quantities under S-13, and retain per-comparison observed differences. Existing B5 script alone is not evidence this has happened. |

Other S-1…S-18 slots are filled/registered, not new science questions. In particular S-5's dated filled pin text supersedes its earlier “still open”; S-13 is already fixed. Do not reset settled bars.

Use loop acceptance/session history, not the archived B5-style `claim_usable` alone, to census attempts. Closed counting sets are A r1/r3/r4; B r1/r2/r3; G r1/r2/r3. **Also index noncounting A r2 and any other collected attempt revealed by the structural census**: §12.3 requires every B6 session, while item 59's “all nine” names only the counting set. Preserve reasons/history. §11.4 determines which noncounting sessions can enter the labelled flagged-inclusive line, retaining run exclusions: the session must be the registered experiment (no W1/W2/W3/S1 structural failure), each required stratum must retain at least five units (the registration's minimum for computability), and b_op plus drift must be defined (§11.4).

Pair by registered round/counting, never value: G r1→A r1/B r1; G r2→A r3/B r2; G r3→A r3/B r3. No B5-floor fallback is needed for these recorded sets. Run B5 PLAN steps per counting session, **no pooling across sessions**. §10 then summarizes B5 plus the three counting B6 sessions (four values per quantity) by mean/sample SD. §11.2 permits “replicated” only if every counting GAMMA outcome and dbar sign matches B5; B5 `not_estimable` permits no such word.

### 5. Block-6 blind dry run and cold release

Before the real blind run: S-9/S-11/S-14/S-15 filled; accepted/pinned driver/index/comparator; full synthetic stage chain and review/cold records; immutable archives/raw inputs/loop acceptance and harvest census; external restricted custody; all referenced capture locators readable. S-16 additionally closes before release.

Automation may open restricted inputs; no seat may. Block-6 §12 restricts energies, powers, phase durations, floors, ratios/means/dbar/signs/outcomes, calibration numbers, science-derived pass/fail, and `derived/flags.jsonl`, `derived/exclusions.json`, `derived/window_flags.json` (the three restricted code-bearing files). Human-readable records contain only structure: statuses, permitted verdict/counting, redacted counts, kept counts, digests, drift verdict, hazards, non-phase timing. Restrict logs/stderr too; “no numbers in stdout” alone is insufficient.

Complete **every collected session** with no tooling refusal. Retain content-addressed input/output census, readable blind-run record and restricted outputs; do not manufacture a B6 record filename/schema from the B5 name. Build and pin those contracts first.

Independent agreement under **S-13**:
- Each run phase energy: **1 mJ**. Registered derivation: rehearsal overlap sum reproduced 154/154 energies within 7×10⁻¹⁵ J; 1 ns at 42 W gives 4.2×10⁻⁸ J, while a 1 ms shift gives 0.047 J and a dropped record gives 3.4–5.5 J. Thus the fixed bar separates rounding from the targeted defects.
- Every printed quantity, compared **unrounded**: **half a unit of its last printed digit**, derived from that quantity's declared printed precision.
- Print observed difference alongside the fixed bar; never use observed agreement to choose the bar. For other two-program comparisons, the task's rule applies: above 10⁶×float noise and below 1% of smallest printed half-width, otherwise 10⁻⁶ relative; exact identity where that is the property. This does not replace the explicitly registered S-13 release bars.

Release prerequisites, all affirmative: B6 closed; B5 release event exists; every-session B6 blind run completed without tooling refusal; S-13 comparison passed; remaining slots/records complete; cold gate under this user's instruction. Dated B6 release record binds **registration, flag catalog and every harvest record digest**, analysis pin, blind record/recompute evidence and the gate disposition. Then rerun identical bytes at the pinned program; every output digest must equal blind run exactly. A science outcome is recorded, not optimized away; a determinism defect blocks release output use.

## Commands for subsequent authorized seats/lead

These are recipes, **not commands executed by this scout**. Placeholders must be filled from the authenticated index/records, not guessed. No new PR/merge/measurement is authorized for this report seat.

Read-only branch/status reconciliation:

```sh
git -C /workspace/JouleWise fetch origin main
git -C /workspace/JouleWise status --short --branch
git -C /workspace/JouleWise show origin/lane/2026-10-20-l9-ruling-build:.codex-report/L9-1.md
git -C /workspace/JouleWise log --oneline --graph origin/main..origin/lane/2026-10-20-l9-ruling-build
git -C /workspace/JouleWise merge-base --is-ancestor origin/lane/2026-10-21-l9-sensguard origin/lane/2026-10-20-l9-ruling-build
git -C /workspace/JouleWise diff --name-status origin/main...origin/lane/2026-10-17-b6-packs-registered
```

Fetch each named non-main ref explicitly first if absent locally; a fetch of main alone need not install it. Read metadata and code only; no broad search over `runs/`, `derived/`, exports or custody.

Synthetic module process example (repeat separately per named module; existing private TMPDIR **per process**; keep outputs until recorded):

```sh
jw_module=tests.b5_analysis.test_chain_fixture
jw_tmp=$(mktemp -d /workspace/jw-synthetic-chain.XXXXXX)
JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 \
JW_B5_S10_CHAIN_CACHE=/workspace/jw-synthetic-chain-cache \
TMPDIR="$jw_tmp" PYTHONDONTWRITEBYTECODE=1 \
python3.13 -B -m unittest "$jw_module"
```

Use an appropriate existing interpreter (Homebrew path below is the Mac command). Record source SHA, exact unittest tail and process exit. Do not share TMPDIRs or run the broad suite from this report seat. CI supplies whole-suite evidence on the final merged candidate; do not mistake an import or supervisor exit for a test pass.

Real B5 commands from `scripts/run_b5_analysis.py` (clean pinned analysis checkout; all actual outputs restricted):

```sh
/opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py \
  --mode blind-dry-run --index configs/analysis/b5/analysed_windows.json \
  --custody <fresh-outside-repository-custody-root>
```

After the cold release record only:

```sh
/opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py \
  --mode release --index configs/analysis/b5/analysed_windows.json \
  --custody <the-same-custody-root>
```

Use a non-symlink, whitespace-free custody path (`/private/tmp`, not macOS `/tmp`, if that location is chosen). A failed/repaired blind run needs a **new** custody root. Driver order: 0,1,2,3,3b,4,5,8,6,9,9b,10,11. Exit 0 means complete, 3 an outcome-class stop, 2 otherwise. The readable record and step classifications decide what completed; no tooling refusal is waived.

Independent B5 raw arithmetic, at its separately pinned code, under automation/restricted logs:

```sh
python3.13 -B scripts/independent_recompute_b5.py \
  --alpha <indexed-alpha-archive> --beta <indexed-beta-archive> \
  --gamma <indexed-gamma-archive> --out <restricted-recompute-json>
```

If authenticated index locators require them, the actual CLI supports `--alpha-exclusions` / `--beta-exclusions` / `--gamma-exclusions`, `--claim-runs-alpha` (and beta/gamma) and `--bound-runs-alpha` (and beta/gamma). No diagnostic-ignore-exclusions override for release. The comparison record is separate evidence; script completion is not agreement.

Pre-real-run Mac custody availability check from RUN_STATE item 34: `find <ledger-iCloud-locator> -type f -flags +dataless` must identify no evicted referenced file; `df -g /Users/edr` at slice boundaries. This is availability checking, not permission for a seat to read capture contents. Linux Cloud cannot establish those Mac facts.

There is **no verified runnable B6 §13 blind/release/recompute command** on the inspected code line. Implement/pin it and record its exact invocation at S-14. `scripts/b6_unblind.py --export <csv> --key-dir <keys> --out <csv>` only divides stored factors; it is not a release gate and must not be used to open numbers now. `scripts/b6_replay_acceptance.py` builds a non-claim replay with defaults/protected-path refusals; it is not the deciding B6 analysis. `scripts/release_check.py` is packaging tooling, not scientific release.

## Agent-doable now, and Ed boundary

**Now in cloud, with separate implementation write scopes:** inspect/join existing L9 results rather than repeat successful diagnostics; cure current joined failures blind; finish synthetic tests; build B6 counting/driver/pairing/recompute/records; prepare authenticated index/census and registration/addendum/review packets without displaying restricted data; review branch ancestry and prepare merge order. An agent can retrieve smoke records and run blind automation on an authorized data host when all required custody and program gates exist. This scout does none of that out-of-scope writing/running.

**Lead-owned:** final source/gate adjudication, six-key merge readiness, #515 topology choice, merges, release-tag choice, real-data execution/custody, release record and cold-gate execution. No PR is opened or merged by this seat.

**Needs Ed:** lifting `ops/stop-pause` before any new physical smoke/capture/window; missing physical access or evidence that needs recollection; a surviving cold-pass refusal requiring a choice about counted data or a printed number. Routine branch landing topology, missing code and record preparation need no invented science ruling. No new campaign is justified merely because analysis is blocked. No email or other message is sent by this scout.

## Decisions I made

1. Followed the current user's **release cold-gate requirement**. B6 registration §12.3 lines 1164–1166 says “no separate cold gate,” with two executing code cold passes at merge; B5 historical prose has the same prune. I retain those merge passes and add the requested release gate. This is a stricter process instruction, not a change to arithmetic or counted data; no scientific NEEDS_RULING is created.
2. “Every block-6 session” (§12.3) includes collected noncounting attempts; item 59's “all nine” is shorthand for the counting set. The registered flagged-inclusive eligibility rules decide their analysis treatment.
3. Chose the item-53 consumer route as the least invasive implementation recommendation; it still needs real-file automated regression. I did not rule a different counting set or alter a writer/record.
4. Treated newer L9-1 as the acceptance-status update to older RUN_STATE handoffs, while preserving its failed completed tests. Diagnostic admissions and in-progress drivers are not green acceptance.
5. Did not request scope expansion: no outside file must change to complete this scout. All listed implementation/addendum/index changes are follow-up work under other scopes.
6. Added no test for a read-only documentary scout. Test commands above are future recipes; no synthetic or real-data acceptance is claimed here.

## Open questions / verification limits

- Does the final integrated L9 dry/probes/J6/chain run complete, and what leaf condition explains the prior warm 9b refusal? Pending execution evidence, not a science ruling.
- Are all S-11 smoke records and every Mac ledger locator locally available? Cloud metadata cannot prove this.
- What exact B6 driver/index/release-record contract and analysis tag will S-14 pin? Missing implementation/evidence, not permission to improvise commands.
- No numerical NEEDS_RULING identified by this scout. B6 §12.4 permits no change to registered arithmetic after data exist; a permitted blind §8 rule correction needs a dated §17 entry checked by an executing refuter, applies to every session, and retains the original-rule result beside the correction. A proposed change to selection/arithmetic must use the registered cold process and print original/alternative where required.

## Work performed and exact command/tool outcomes

Two independent read-only agents audited (a) registration/gates and (b) branch/L9/B5 dependencies; the primary scout checked governing passages, source CLIs and live PR metadata and adjudicated their findings. No subagent wrote a file or ran a test.

Managed environment remained pending/offline while the report was prepared. `wait_for_environment` was requested for the selected environment. The attempted local command was exactly `pwd`; it did not launch and returned:

```text
No usable execution environment is available. Wait for an environment to become available before using this tool.
```

Therefore the requested local `git -C /workspace/JouleWise fetch origin main && git -C /workspace/JouleWise checkout -B report/2026-10-22-blind-dry-run-scout origin/main` and shell/git diff checks could not run at that point. Connected GitHub reads supplied the evidence. `tools/cloud/seat_setup.sh` on base main returned:

```text
GitHub API error 404: {"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/contents#get-repository-content","status":"404"}
```

Thus the conditional seat-setup script is absent on this base snapshot. Runtime skill/network readiness was inspected without printing credentials. No test tail exists: **tests not run (report-only; no modules touched)**. Source/report integrity was checked using in-memory content validation and GitHub readback; final publication outcome is recorded below.

Publication method: connected GitHub tools, creating only the requested report branch from the stated main SHA and committing only this report. Local shell/Git execution remained unavailable; no branch other than the report branch is written. The readback and scope comparison are recorded in the close-out below.

### Close-out verification

- First report commit/push through `github.create_file`: `ade1eb489316cee1ca68029727229127858086c6`. Exact tool result: `{"commit_sha":"ade1eb489316cee1ca68029727229127858086c6"}`.
- GitHub readback matched the complete submitted text exactly; report blob `44d9d0b8f954e8b44fc7adf3c27d0dcd556246e2`.
- GitHub compare against base `7c23ea4b71622f7a898617a66da48868e20562a3`: `status=ahead`, `ahead_by=1`, `behind_by=0`; exactly one added path, `.codex-report/BLIND-DRY-RUN-SCOUT.md`, no other file. Commit parent equals the requested main snapshot.
- Final documentary pass added the completed #500/#501 gate references, historical B5 harvest pins, excluded-reference cold re-harvest contingency and exact restricted filenames. In-memory final checks: terminal newline, no trailing whitespace/NUL, balanced code fences; PASS.
- This close-out is committed directly to the same report branch through `github.update_file` (a normal new commit, no force update). Final content and one-path scope are read back before handoff. No local checkout/setup/test/diff success is claimed; the cloud execution environment never became usable during this scout.
