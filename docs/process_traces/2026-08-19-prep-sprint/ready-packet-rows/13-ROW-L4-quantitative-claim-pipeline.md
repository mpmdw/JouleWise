# ROW L4-quantitative-claim-pipeline — QUANTITATIVE CLAIM PIPELINE (GATING)
Original verdict: NOT-READY (1 blocker / 2 should-fix / 1 nit / coverage 24/27)
Seat: `docs/process_traces/2026-08-15-readiness-council/seat-reports/L4-quantitative-claim-pipeline-report.md`
Row line in sealed packet: `sitting-packet-FINAL.md:31` — `| L4-quantitative-claim-pipeline | GATING | NOT_READY | 24/27 | 1 | 2 | 1 | 4 | 5 | 1 |`
Seat report sha (packet §1 index): `8f4434e3e3447de5`

**Assembly note on WHERE evidence lives (repeated per sub-row, but stated once here):**
worktree HEAD at assembly = `79a4cd0` on `impl/r2-s0-mint-resolver` (NOT `d10881b` — the brief's
pinned sha is an ancestor of this head; both are branch-only). `main == origin/main == 0099382`;
49 commits on HEAD not on origin/main; merge-base `311d8016`. Verified by `git rev-parse` /
`git merge-base --is-ancestor`.

---

## L4-B1 — Margin recorder cannot read the re-specced frozen floor-pack extraction specs

### (a) Original finding (VERBATIM)
> ### L4-quantitative-claim-pipeline B1: Margin recorder cannot read the re-specced frozen floor-pack extraction specs — ALPHA/BETA close-out halts deterministically at runbook section 11
> at: joulewise/window_duration_margins.py:897 (session) + :394 (spec read); cause joulewise/authentication_io.py:179,214; missing authorization mirror of scripts/mint_floor_artifact_generalized.py:1758-1759,3683
> scenario: A funded quiet window collects ALPHA cleanly; the operator runs the exact runbook section-11 command; the recorder opens its V2AuthenticationReadSession and reads the pack-pinned spec, which since the D-133 cl.4 re-spec carries estimator_registration in all comparative cells; the session's reserved-vocabulary rule refuses (executed: REFUSE authoritative_input_invalid, exit 2, no receipt); 'REFUSE stops close-out without writing a receipt' — backup/extraction never run under the mandated order, the window cannot be called claim-bearing, and the standing constraint 'collection close-out gates on the WO-COLLECTION-MARGIN-01 receipt' is unsatisfiable on every attempt. Only the mint authorizes governed-spec vocabulary (allow_governed_extraction_spec); the recorder never does. The committed census tests (tests/test_window_duration_margins.py:213,514) model 'real floor pack cell shapes' WITHOUT the estimator vocabulary, so the suite is green while the real seam is broken — the charter's producer-gap type specimen.

Citation: `sitting-packet-FINAL.md` §3 heading "L4-quantitative-claim-pipeline B1" (lines 69-71);
seat report `seat-reports/L4-quantitative-claim-pipeline-report.md` §5 BLOCKER 1 + §4 probe F4;
refuter verdicts `refuter-outputs/refuter-verdicts.md` — "ECF-contract … All four CONFIRMED
(L10-B1 consumption edge, L4-B1 margin recorder, …)" and "ECF-execution … V3 margin recorder
REFUSE authoritative_input_invalid (forbidden key 'estimator_registration' at pack-pinned
spec.cells[1])". CONFIRMED by two distinct lenses; no downgrade in `council-verdict.md`
Disposition 4 (struck findings are L8-B4, WO-L2-4, F4's timing premise — L4-B1 is not among them).

### (b) What changed since 2026-08-15
- **`00ec3b7`** — "WO-MARGIN-RECORDER-AUTHZ: narrow governed-vocabulary grant for the
  plan-tree-pinned floor spec (#151)", 2026-08-15. **WHERE: merged to main** (`git merge-base
  --is-ancestor 00ec3b7 origin/main` → YES; also ancestor of HEAD). Diff = 2 files:
  `joulewise/window_duration_margins.py` (+68/-24 region) and
  `tests/test_window_duration_margins.py` (477 lines changed).
- What the code actually does (verified by reading `git show 00ec3b7 -- joulewise/window_duration_margins.py`):
  1. `_pack_inventory` now takes the live `V2AuthenticationReadSession` and calls
     `authentication.allow_governed_extraction_spec(registry_path)` on **only** the floor-pack
     branch (the plan-tree-pinned `extraction_spec` path) — current head
     `joulewise/window_duration_margins.py:428`. The GAMMA analysis-manifest branch is never
     granted. This is the narrow-grant contract the adoption ruling required (decision log
     `docs/decision_log.md:9381` "WO-MARGIN-RECORDER-AUTHZ contract ADOPTED").
  2. A **resolution-invariance guard** precedes the grant: the pack-declared path must resolve to
     itself and no component from the repository root down may be a symlink, else
     `_refuse("authoritative_input_invalid", "governed extraction-spec path is not
     resolution-invariant (symlinked component)")`.
  3. Grant failure is normalized: `except (ValueError, RuntimeError)` →
     `authoritative_input_invalid`.
  4. F-5 fix: `_json_object` now wraps `read_authentication_input` in try/except so a raw
     `V2AuthenticationInputError` can no longer escape `_pack_inventory` on a non-adversarial path.
  5. The floor/GAMMA branch selection was made explicitly exclusive
     (`floor_pack_selected == gamma_pack_selected` → `registered_cell_inventory_invalid`) and the
     `registry_sha != expected_sha` pin check duplicated into both branches.
- **Executed positive verification by this assembler** (read-only, at HEAD `79a4cd0`, python3
  in-process call of `joulewise.window_duration_margins._pack_inventory` inside a real
  `V2AuthenticationReadSession`, against the REAL committed pack bytes):
  - `configs/campaigns/d117_floor_qwen25_1p5b_v1` (identity
    `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1`) → **OK**, tree_sha `3e725c047c98…`,
    registry_sha `d98ae4deb787…`, 3 registered comparative cells.
  - `configs/campaigns/d117_floor_qwen25_1p5b_v3` → **OK**, tree_sha `2b3fefc8e04c…`, 3 cells.
  - `configs/campaigns/d117_floor_qwen25_7b_v3` → **OK**, tree_sha `7f4de9d0ef3c…`, 3 cells.
  - GAMMA branch also exercised: `d117_contrast_..._v1` and `_v3` → **OK**, 2 cells each.
  The `REFUSE authoritative_input_invalid — forbidden key 'estimator_registration'` refusal the
  seat and both ECF refuters reproduced **no longer fires** on the real frozen bytes, on either
  the audited `_v1` family or the new `_v3` family.
- **Not verified by this assembler:** end-to-end `scripts/record_window_duration_margins.py`
  reaching `RECEIPT_STATUS=PASS` — that needs a real runs root with the registered members
  (the seat's own probe stopped at `member_missing`). The PASS claim rests on the PR #151 commit
  message ("recorder now PASSes on the re-specced frozen pack") and the recorder-race composed
  verdict §5, not on an assembler-executed run.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED (with a named residual — see L4-B1-RESIDUAL).** The seat is
adjudicating whether an in-process `_pack_inventory` success on real frozen bytes, plus a
main-merged narrow grant that never touches the GAMMA path, discharges a blocker whose original
failure was "close-out halts deterministically" — or whether it needs the CLI-level
`RECEIPT_STATUS=PASS` proof over a real member corpus (which is exactly ED-L10-1, still open).

### (d) Skeptical probes
1. Re-run the assembler's probe yourself at HEAD and demand the *CLI* result, not the library
   result: `.venv/bin/python scripts/record_window_duration_margins.py --repository-root . --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v3 --runs-root <real corpus> --receipt-root <tmp> --pack-identity plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`. Without a real
   runs root it stops at `member_missing`; that is *not* proof of PASS.
2. `grep -n "estimator_registration" tests/test_window_duration_margins.py` — the blocker's
   root cause was a fixture that omitted the estimator vocabulary. Confirm the committed census
   regression now reads the **REAL frozen spec bytes** (WO-L4-1 required this), not a repaired
   synthetic fixture.
3. The adoption ruling's clause 1 says "never granted the other floor pack's spec". Confirm the
   grant is per-path and that a session which inventories two packs in sequence cannot accumulate
   two grants: read `joulewise/authentication_io.py:349-363`
   (`_governed_spec_vocabulary_identities` is a *set* on the session).
4. `git log --since=2026-08-14 --oneline -- joulewise/window_duration_margins.py` returns exactly
   one commit (`00ec3b7`). Ask whether one commit, merged the same day as the council, has had a
   delta re-audit at any later head — the file's callers (`_v3` pack family, launch-lineage
   markers from `b9c7d0a`) changed after it.
5. Charter final-head invalidation: `git diff --stat 8937dec..HEAD` over the L4 scope files is
   **900 files / 134,721 insertions**. Ask whether L4-B1's cure was ever re-verified at the
   current head rather than at `00ec3b7`.

---

## L4-B1-RESIDUAL — recorder check-to-grant TOCTOU: cure RETIRED BY APPETITE, not by code

### (a) Original finding (VERBATIM — this is a POST-verdict finding, not a 2026-08-15 finding)
Raised during the WO-MARGIN-RECORDER-AUTHZ gauntlet, ruled at a rule-11 cold gate. Verbatim from
`docs/decision_log.md:9510` ff, heading "RECORDER CHECK-TO-GRANT RACE — registered limitation +
WO-RECORDER-GRANT-IDENTITY queued (magistrate, 2026-08-15; rule-11 cold gate, composed verdict)":
> **REGISTERED LIMITATION (L1 shape):** the margin recorder's governed-vocabulary grant
> (window_duration_margins.py) is subject to a check-to-grant TOCTOU: a concurrent local process
> with repository write access can, mid-run, alias the selected floor-spec path so
> allow_governed_extraction_spec registers the OTHER floor pack's identity (executed:
> 10/400 and 7/1200 uninstrumented iterations; a swap-and-revert yields a SILENT success with an
> attacker-chosen identity granted). **RECEIPT INTEGRITY IS INTACT:** every post-grant read in the
> recorder is hash-pinned (expected_sha / member_config_sha256), so a stolen exemption cannot alter
> a receipt today — the harm is a contract-boundary violation (clause 1's "never granted the other
> floor pack's spec") and a forensic refusal-code downgrade, not a receipt forgery.

Citation: `docs/decision_log.md:9510-9550`; gate record (the ONE home)
`docs/process_traces/2026-08-15-recorder-race-coldgate/` — `packet.md`, `assemble.py`
(non-author assembly), `coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`,
`composed-verdict.md`. Custody commits `8b6c872` (packet), `8c7843a` (adjudicator ruling),
`5cdec0c` (composed verdict) — **all merged to main.**

### (b) What changed since 2026-08-15
- **Composed verdict** (`composed-verdict.md:12-50`, merged to main at `5cdec0c`): the seats split
  — the cold adjudicator ruled the race out-of-model and regraded should-fix; the Opus contract
  refuter ruled the contract SILENT, not exclusionary, and fired the F-9 standing escalation
  trigger. The magistrate ruled the refuter CONTROLS: **"the concurrent unprivileged local writer
  is NOT ruled out of the instrument's threat model"**, and "the real cure is a clause-2
  amendment" (stop `allow_governed_extraction_spec` re-resolving its argument) queued as
  **WO-RECORDER-GRANT-IDENTITY**, with its own future rule-11 cold gate.
- **Design consult delivered:** `docs/process_traces/2026-08-16-grant-identity-consult/`
  (`README.md`, `consult-prompt.md`, `consult.md`), custody commit **`2adac50` — merged to main.**
  Recommendation: `allow_governed_extraction_spec(*, verified_identity: str)` accepted VERBATIM,
  callee performs lexical validation only. Naive fd-stat and `(st_dev, st_ino)` formulations
  **REJECTED on executed REPLAY E hardlink-restoration evidence**. Sequencing: "the cold gate +
  implementation WAIT for Ed's batched risk-appetite session".
- **RETIRED WITHOUT IMPLEMENTATION.** `docs/decision_log.md:10049-10056`, D-139 clause A1
  (Ed, 2026-08-17, packet `docs/process/ed-batch-packet.md`): "**A1 — In-process adversary RULED
  OUT OF MODEL (registered limitation, family-wide).** Ed: 'no adversarial programs affecting the
  measurement can be assumed.' Consequences, effective immediately: (1) WO-RECORDER-GRANT-IDENTITY
  is RETIRED to the registered check-to-grant limitation — no implementation, no cold gate (the
  design consult remains custodied at docs/process_traces/2026-08-16-grant-identity-consult/
  should the appetite ever change)". D-139 index row at `docs/decision_log.md:164`. **WHERE:
  merged to main.**
- **Code state at HEAD:** `joulewise/authentication_io.py:352` still reads
  `identity = str(Path(path).resolve(strict=False))` — the re-resolution the composed verdict
  named as the root cause is unchanged. The only mitigation shipped is the caller-side
  resolution-invariance guard in `00ec3b7` (which the composed verdict §1 explicitly declined to
  call a closure: "NO caller-side 'closure' is licensed").
- **PROPAGATION NOT FOUND.** The registered limitation states a **bounding workflow rule**: "the
  recorder runs single-operator with no concurrent repo-writing process during a close-out; this
  is documented in the runbook §11 close-out preamble (propagation owed with the WO)". Searched
  `docs/phase_2/window_runbook.md` for `concurrent` / `single-operator` / `repo-writing` /
  `no other process`: the ONLY hit is line 887, which is the **T-0 trusted-operator** paragraph,
  a different limitation. **§11 (lines 1729-1745) carries no such preamble.** The WO that owed the
  propagation was retired; the propagation appears to have been retired with it.

### (c) Candidate disposition for the seat
**SUPERSEDED-BY-RULING (with an unpropagated bounding rule).** The seat is adjudicating whether a
cure retired by *risk appetite* (D-139 A1) rather than by code leaves the L4 seam sound — and,
separately, whether the registered limitation's own mitigating workflow rule can be considered in
force when it was never written into the runbook it names.

### (d) Skeptical probes
1. `grep -n "concurrent\|single-operator\|repo-writing" docs/phase_2/window_runbook.md` — verify
   the assembler's claim that §11 has no concurrency preamble. If confirmed: the registered
   limitation is mitigated by a rule that exists only in the decision log.
2. Ask whether D-139 A1's scope ("no adversarial programs affecting the measurement") actually
   covers this race. The composed verdict's harm was a **contract-boundary violation and forensic
   refusal-code downgrade**, not measurement corruption — is that inside or outside A1's words?
3. The magistrate's own ruling (composed verdict §2) declined to buy a merge by declaring the
   writer out of model, citing three precedents that graded this class blocker-and-fix. Ed then
   declared it out of model two days later. Ask what evidence changed between 08-15 and 08-17 —
   or whether only the seat did.
4. Non-adversarial reachability: the race needs a concurrent repo writer. A *Claude/Codex agent
   session* is a concurrent repo writer. Ask whether the standing prohibition
   ("never start or continue a `[QUIET-MAC]` measurement while an agent session is active",
   `CLAUDE.md`) is machine-enforced anywhere in the close-out path, or is operator discipline.
5. Read `docs/process_traces/2026-08-15-recorder-race-coldgate/coldgate-opus-refuter-findings.md`
   F-10 (post-grant grant-delta verification). It was DEFERRED into WO-RECORDER-GRANT-IDENTITY.
   That WO is retired — confirm F-10 was not silently dropped with it.

---

## L4-SF-1 — GAMMA contrast both-gates consumption route is unbuilt

### (a) Original finding (VERBATIM)
> - [should_fix] [L4] GAMMA contrast both-gates consumption route is unbuilt: prospective manifest refused by the loader, sole frozen-v3 builder hard-pinned to the splitwise campaign

Citation: `sitting-packet-FINAL.md` §4 line 152 (titles-only region). Full text, seat report
`seat-reports/L4-quantitative-claim-pipeline-report.md` §5 SHOULD-FIX 2 (VERBATIM):
> **SHOULD-FIX 2 — GAMMA both-gates consumption route unbuilt.** load_manifest (inputs.py:554-569) refuses the prospective schema (correct, fail-closed — executed); the only frozen-v3 builder (analysis_manifest_v3.py:34,48,441-447) is hard-pinned to the splitwise campaign (ROOT_ORDER_SHA256, swdec-contrast run-id grammar, 40 entries) while the frozen GAMMA pack has 80 d117c15v7-* rows; zero production code references the GAMMA grammar; the prospective manifest's only production consumer is the margin recorder. The funded p256 contrast — the purpose of the 1.869502 J re-spec — cannot mechanically reach evaluate_claim post-window, and the in-span re-run decision for GAMMA cannot be made on claim outcomes. Satisfies the council disjunction's fail-closed arm; the missing piece is hereby named per the charter's "what exactly is missing".

Note: this is the same seam as blocker **L10-B1**; both were CONFIRMED by both ECF lenses
(`refuter-outputs/refuter-verdicts.md`, ECF-contract and ECF-execution sections). The L10 row
carries the full repair analysis; only the L4-specific residue is stated here.

### (b) What changed since 2026-08-15
- **`d54db78`** — "Merge pull request #155 from mpmdw/impl/wo-consumption-edge —
  WO-CONSUMPTION-EDGE: prospective validator, outcome-blind finalizer, finalized-v3 consumption
  edge", 2026-08-16. **WHERE: merged to main.** 9 files, +6162/-65:
  `joulewise/analysis_manifest_v3.py` +3226, `joulewise/analysis_engine/inputs.py` +308,
  `analysis_engine/artifact.py` +190, `analysis_engine/__init__.py` +128,
  `scripts/finalize_analysis_manifest.py` +87 (new), 3 test modules +2215.
- The splitwise hard-pin is **still present** but is now confined to the *historical* v3 path:
  `joulewise/analysis_manifest_v3.py:33` `PLAN_ID = "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b"`,
  `:48 ROOT_ORDER_SHA256`, `:63` `swdec-contrast-b…` run-id regex, `:585,:713` `design_id:
  splitwise_decode_cross_model_abba_v1`. The **new** prospective/finalized functions
  (`_validate_prospective_analysis_manifest_v3_unchecked:1885`,
  `validate_prospective_analysis_manifest_v3:2777`, `build_prospective_…:2831`,
  `finalize_prospective_…:3722`, `validate_finalized_…:4062`) are design-agnostic: they take the
  `design` block from the manifest.
- `joulewise/analysis_engine/inputs.py:604` now emits the **registered** refusal
  `analysis_manifest_prospective_not_consumable: frozen prospective manifests must pass the
  outcome-blind finalizer` instead of the seat's observed
  `unsupported analysis manifest schema_version`. Finalized artifacts route to
  `validate_finalized_analysis_manifest_v3` (`inputs.py:593`).
- Refusal vocabulary registered as a D-078 amendment in the same PR (33 new spellings across
  prospective / finalization / consumer tiers) — `docs/decision_log.md`, "D-078 amendment —
  2026-08-15: analysis-manifest consumption-edge refusal registry". **Merged to main.**
- **BUT the route does not yet reach the real GAMMA pack.** Executed by this assembler at HEAD:
  `validate_prospective_analysis_manifest_v3(json(configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json), manifest_dir=…, plan_tree_path=…/plan_tree.json)`
  returns **4 refusals** on the FROZEN `_v3` (freeze-0003) pack:
  - `analysis_prospective_schema_invalid` — "manifest: missing key(s): design, families,
    finalization_contract, freeze_status, frozen_semantics_sha256, manifest_id, replacement_policy"
  - `analysis_prospective_unknown_key` — "manifest: unrecognized key(s): draft_status,
    postcollection_attachments"
  - `analysis_prospective_unresolved_slot` — "manifest contains an EMPTY/TODO placeholder"
  - `analysis_prospective_not_frozen` — "manifest.freeze_status must be 'frozen'"
  Identical 4-refusal result on the `_v1` pack. `grep -rl frozen_semantics_sha256 configs/ tests/ docs/`
  finds the field **only** in `tests/test_analysis_manifest_v3.py` and
  `docs/process_traces/2026-08-15-consumption-edge-consult/consult.md` — **no committed pack
  manifest carries the schema the shipped validator requires.**
- D-139 A2 (`docs/decision_log.md:10063` ff, merged to main) supplied the missing science:
  Holm α=0.05, m=2 (decode + prefill_p256), two-sided; dedicated p256 floor artifact. It states
  "These values enter the gamma prospective manifest's **families** block at the production
  freeze." The `_v3` contrast manifest's top-level keys are
  `['schema_version','draft_status','plan','evidence_root_id','root_order_manifest','stage_manifests','condition_families','contrasts','postcollection_attachments']` — **no `families` block.**

### (c) Candidate disposition for the seat
**STILL-OPEN (code landed; the packs are not yet on the schema).** The seat is adjudicating
whether a merged, design-agnostic prospective/finalized lifecycle counts as the GAMMA route
existing, when the three frozen production packs — including the `_v3` family frozen in *this*
transaction — refuse the shipped validator on four counts and carry no families block.

### (d) Skeptical probes
1. Reproduce the 4 refusals yourself against `d117_contrast_qwen25_1p5b_vs_7b_v3`. Then ask what
   produces a compliant manifest: is `build_prospective_analysis_manifest_v3` wired to any
   generator (`configs/campaigns/d117_*_v3/generate_configs.py`), or must the packs be re-frozen
   a fourth time?
2. D-140 is cited in the runsheet as "all pack bytes are immutable after mint". If the packs must
   gain `families` / `freeze_status` / `frozen_semantics_sha256` blocks, that is a byte change to
   frozen packs. Ask which ruling licenses it and at which freeze generation (`freeze-0004`?).
3. `grep -n "prospective\|finaliz\|analysis_manifest" docs/process/phase2-transaction-runsheet.md`
   → **zero hits.** The Phase-2 transaction runsheet does not schedule the manifest re-authoring
   at all. Ask who owns it and where it is tracked.
4. `grep -n "finalize_analysis_manifest\|analyze-claims" docs/phase_2/window_runbook.md` → **zero
   hits.** The finalizer has no operator step in the runbook. A window can be spent and closed out
   with no documented path to a consumable manifest.
5. Check whether the historical splitwise-pinned `validate_analysis_manifest_v3` is still
   reachable from `load_manifest` (`inputs.py`, the `ANALYSIS_MANIFEST_V3_SCHEMA` branch) and
   whether any D-117 artifact could land on that branch by mistake.

---

## L4-SF-2 — Margin-receipt consumption never mechanically binds to the FROZEN pack

### (a) Original finding (VERBATIM)
> - [should_fix] [L4] Margin-receipt consumption never mechanically binds to the FROZEN pack: a repinned truncated pack yields a plausible PASS and the receipt validator accepts a truncated sha-repaired receipt

Citation: `sitting-packet-FINAL.md` §4 line 153. Full text, seat report §5 SHOULD-FIX 3 (VERBATIM):
> **SHOULD-FIX 3 — margin receipt is never mechanically bound to the FROZEN pack at consumption.** Executed F3-B/C: repinned truncated pack → plausible PASS; truncated sha-repaired receipt → validator accepts. Close-out records path+SHA only (runbook:1449-1473,1536); no step compares receipt.pack_tree_sha256 to the frozen pack's committed plan_tree.sha256. A tired operator pointing --pack-root at a stale copy (the registered F-C/F-F ambiguity family) gets a plausible PASS bound to the wrong census.

Seat work order: **WO-L4-3** — "one mechanical close-out line: receipt.pack_tree_sha256 must equal
the frozen pack's committed plan_tree.sha256; record the comparison in §12."

### (b) What changed since 2026-08-15
**NO-REPAIR-FOUND.** What was searched, at HEAD `79a4cd0`:
- `git log --since=2026-08-14 --oneline -- joulewise/window_duration_margins.py` → exactly one
  commit, `00ec3b7` (the authz grant). Its diff adds no comparison against a committed pack digest;
  the `registry_sha != expected_sha` check it duplicates into both branches was **already present**
  before the PR (it was moved out of the shared tail, not added) — and it binds the spec bytes to
  the *supplied* plan tree, which is exactly the re-pinned-doctored-pack case F3-B defeats.
- `grep -n "freeze\|committed_pack_tree\|pack_tree_sha256" joulewise/window_duration_margins.py`
  → `pack_tree_sha256` appears only as a receipt field (`:51` schema key, `:997` emission,
  `:1043` validator key). No freeze-receipt or committed-digest comparison anywhere in the module.
- `validate_window_duration_margins_receipt` (`joulewise/window_duration_margins.py:1032`) takes
  a receipt *Mapping* and nothing else — structurally it cannot compare against the frozen pack.
  It re-derives internal consistency only, exactly as F3-C described.
- Runbook §12 close-out list (`docs/phase_2/window_runbook.md:1795-1832`) still records
  "the comparative-cell window-duration-margin receipt path and SHA-256, recorded separately from
  bound-mint, backup, and extraction outputs" — **no comparison line.** WO-L4-3 is not implemented
  in the runbook.
- No TASK_QUEUE / `docs/process/state_kernel.json` row named WO-L4-3 or equivalent was found.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a should-fix whose one-line remedy (a §12 digest
comparison) was specified by the seat, ratified into the work-order program
(`council-verdict.md` "should-fix batch"), and does not appear anywhere at the current head.

### (d) Skeptical probes
1. `sed -n '1795,1832p' docs/phase_2/window_runbook.md` and look for any line comparing the
   receipt's `pack_tree_sha256` to `PACK_ROOT/plan_tree.sha256`. Assembler found none.
2. Re-run the seat's F3-B attack at HEAD: copy a frozen pack, truncate its census, re-pin
   `plan_tree.sha256` and the downstream extraction-spec sha consistently, point `--pack-root` at
   the copy, and see whether a PASS receipt is produced. The `00ec3b7` symlink guard does not
   address this (it guards aliasing, not a legitimately-repinned separate tree).
3. Ask whether the `_v3` family's **freeze receipts** (`arm_readiness.freeze.receipts/freeze-0003.json`,
   present in all three packs) create a binding the recorder could cheaply consume — and if so,
   why the recorder still does not read them.
4. Note the operator-trap amplification: `WINDOW_ID` in the runbook `window.env` example is
   `…-v2` (line 190) while the frozen family in this transaction is `_v3`. A `--pack-root` /
   `--pack-identity` mismatch of exactly the F-C/F-F ambiguity family is now *encouraged* by the
   frozen example.

---

## L4-NIT-1 — validate_floor_artifact's recomputation tolerance accepts a one-ULP-understated floor

### (a) Original finding (VERBATIM)
> - [nit] [L4] validate_floor_artifact's recomputation tolerance accepts a one-ULP-understated floor; tamper-evidence rides on byte custody, not numeric revalidation

Citation: `sitting-packet-FINAL.md` §4 line 154. Full text, seat report §5 NIT 4 (VERBATIM):
> **NIT 4 — validate_floor_artifact numeric tolerance passes a one-ULP-understated floor** (detection_floor.py:2021); enforcement rides on the mint's exact-Decimal gates and claim-side file_sha256 binding (artifact.py:943). Executed on the committed mint1 artifact. Defense-in-depth posture is sound; record it so no one cites the validator alone as tamper-proofing.

Seat work order: **WO-L4-4 (record-only)** — "document the _close-tolerance/byte-custody posture;
any future floor-artifact consumer must bind file_sha256 or use exact-Decimal equality."

### (b) What changed since 2026-08-15
**NO-REPAIR-FOUND (and none was ordered — WO-L4-4 is record-only).** Verified at HEAD:
- The tolerance is unchanged. `joulewise/detection_floor.py:2040-2047`:
  `delta = abs(actual - expected)`; `relative_limit = max(1e-12, 1e-12 * abs(expected))`;
  `return delta <= min(relative_limit, _MAX_RECOMPUTATION_ABS_DELTA_J)` with
  `_MAX_RECOMPUTATION_ABS_DELTA_J = 1e-6` at `:123`.
- `git log --oneline -S"def _close(" -- joulewise/detection_floor.py` → one commit, `8384287`
  ("P2-039: detection-floor calculator, artifact emit/validate, transport refusal (new files
  only)"). The function has never been touched since introduction.
- `validate_floor_artifact` moved from the seat's cited `:2021` to **`joulewise/detection_floor.py:4146`**
  (file grew by 76 lines net since baseline; the tolerance helper stayed at `:2040`).
- `detection_floor.py` did change since the council: `b9c7d0a` (WO-LAUNCH-BINDING stage 3,
  **merged to main**) and `cef3306` (S0 kernel generation-resolved mint policy, **branch-only**
  on `impl/r2-s0-mint-resolver`). Neither touches `_close` or the tolerance.
- No record-only documentation of the posture was found: `grep` for the posture in
  `docs/decision_log.md` / `docs/limitations`-style surfaces produced no matching entry.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND (record-only WO undischarged).** The seat is adjudicating whether an
undischarged record-only work order matters at a READY-candidate sitting, given that
`detection_floor.py` has since gained a new branch-only mint-policy generation layer (`cef3306`)
whose consumers were not audited by L4.

### (d) Skeptical probes
1. Confirm the tolerance value yourself: `sed -n '2040,2048p' joulewise/detection_floor.py`.
2. `cef3306` is **branch-only** and adds "generation-resolved mint policy (D-147 S2/S4); genesis
   digest rename; schema generation conditionals" to `detection_floor.py`. Ask whether any new
   generation-resolved path consumes a floor value through `_close` rather than exact Decimal.
3. Ask where the record-only posture note was supposed to land, and check it is there. If it is
   nowhere, the nit's only remedy is undischarged.

---

## L4-COVERAGE — 24/27 examined at working depth

### (a) Original finding (VERBATIM)
Seat report §2 (VERBATIM):
> **24 / 27 examined at working depth.** Full read: items 4, 7, 8, 9, 16, plus targeted reads of 2, 5, 11, 12, 13, 14, 15 at every line my probes and findings depend on; executed verification of every frozen artifact (17–24) against the baseline manifest; suites executed for every code item. Partial (disclosed, not silently skipped): item 1 and 14 interiors covered by suite + seam checks only (deep line-read unexecuted, listed in §6); the decisive full-fixture proof (network-gated) unexecuted.

Post-verdict adjudication: `council-verdict.md` VERDICT §2 —
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every
> seat's evidence universe was self-nominated, and the one denominator adversarially tested fell.
> Closing all listed work orders does not entitle READY; the READY-candidate re-audit must
> re-enumerate every universe independently and run the adversarial coverage attack as a standing
> packet element.

L4 was NOT tagged UNVERIFIED on coverage (only L2 was — `sitting-packet-FINAL.md:30-31`,
`council-verdict.md` VERDICT). But L4's 27-item denominator was **self-nominated and never
adversarially attacked**, and L2's was the one that fell when attacked.

### (b) What changed since 2026-08-15
- **The adversarial coverage re-enumeration has NOT been run.** It sits in Phase 3:
  `council-verdict.md` "**Phase 3:** baseline-manifest SUPERSESSION (with the ruled fields) +
  focused re-audit of pack/custody-bearing seats (L1, L5, L7 minimum) + adversarial coverage
  re-enumeration of all universes"; still forward-looking in
  `docs/process/phase2-transaction-runsheet.md:115` ("Phase-3 focused re-audit (adversarial
  coverage re-enumeration) → READY-candidate council") and `RUN_STATE.md:450,604`.
- **The denominator is materially stale.** `git diff --stat 8937dec..HEAD` restricted to L4-scope
  paths (`joulewise/analysis_manifest_v3.py`, `joulewise/analysis_engine/`,
  `joulewise/window_duration_margins.py`, `joulewise/detection_floor.py`,
  `joulewise/floor_extraction.py`, `scripts/extract_detection_floors.py`,
  `scripts/mint_floor_artifact_generalized.py`, `scripts/finalize_analysis_manifest.py`,
  `docs/phase_2/window_runbook.md`, `configs/campaigns/`) = **900 files changed, 134,721
  insertions, 422 deletions.** Notably: `analysis_manifest_v3.py` +3226 (a whole new lifecycle),
  `analysis_engine/inputs.py` +403, `analysis_engine/artifact.py` +190,
  `scripts/finalize_analysis_manifest.py` +87 (new file, item never in the universe),
  two entire new pack families (`_v2`, `_v3`), runbook +505.
- **Charter final-head invalidation applies:**
  `docs/process/instrument-readiness-audit-charter.md:79-91` — "final-head invalidation — any repo
  change after the baseline manifest voids affected lens results." The baseline manifest pins
  `ac3fe1d`; the effective audit baseline was `8937dec`; HEAD is `79a4cd0`.
- Baseline-manifest SUPERSESSION (Phase 3, with `pack_digest_algorithm` + chain-template note +
  paths for all bindings, per `council-verdict.md` "Manifest conditions at supersession") has not
  been executed — no successor manifest found.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a self-nominated 27-item denominator, never adversarially
attacked, against a scope that has since taken 134k insertions including a complete new
claim-consumption lifecycle — with the charter's final-head invalidation clause unexercised and the
baseline manifest not superseded.

### (d) Skeptical probes
1. Run the adversarial coverage attack the council ordered as a **standing packet element**:
   independently enumerate the L4 universe at HEAD and compare with the seat's 27 items. Predict
   at minimum the addition of `scripts/finalize_analysis_manifest.py`, the prospective/finalized
   halves of `analysis_manifest_v3.py`, and the `_v3` pack family's three
   `analysis_manifest_v3.json` / `plan_tree.json` / freeze receipts.
2. `git diff --stat ac3fe1d..HEAD -- joulewise/ scripts/` and ask which of the seat's *executed*
   suite results (the 13 modules, 442+ tests) were re-run at HEAD. None are recorded in this packet.
3. Ask whether the baseline-manifest supersession is a precondition to this sitting. The charter
   calls the manifest immutable and the verdict words future changes as SUPERSESSION
   (`council-verdict.md` Disposition 1) — if no successor manifest exists, what binds the current
   head?
4. `docs/process/audit-baseline-manifest.json:20` at HEAD still reads
   `"head_commit": "ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b"` (assembler-verified). The baseline
   manifest has NOT been superseded. Ask what document, if any, binds the head this sitting audits.

---

## L4-UNEXECUTED / ED-QUAL-L4-1 — the decisive full-fixture production proof

### (a) Original finding (VERBATIM)
Unexecuted obligation, `sitting-packet-FINAL.md` §6 line 241:
> - [L4] The decisive full-fixture production proof (scripts/replay_d117_decisive.sh; test_coordinated_report_and_pin_change_refuses_against_floor_evidence and the split-partition test, the 2 skips in my mint suite run) — requires network download of the custody-store release asset and ~3h35m; not executable in this no-network sandbox.

Paired ED row, `sitting-packet-FINAL.md` §5 line 191:
> - [L4] ED-QUAL-L4-1 (network capability, not hardware/sudo — emitted so it is not silently skipped): execute scripts/replay_d117_decisive.sh at the audited head in any tap block with network — anonymous release download, digest gate, governed hydration, census byte-compare, then the single decisive no-skip mint test (~3h35m on the M3 Max). Stable evidence; closes the two skipped decisive tests and the full-fixture leg of the mint's exact-equality proof.

Charter constraint: `docs/process/instrument-readiness-audit-charter.md:70-78` — ED-QUALIFICATION
rows are "performed BEFORE the sitting… stable evidence cannot be deferred. **Only T0 rows may
remain open at the sitting.**"

### (b) What changed since 2026-08-15
- **CLOSED — executed by Ed, 2026-08-17 ~22:05 PT.**
  `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:189-196`: "## ED-QUAL-L4-1
  CLOSED (2026-08-17 ~22:05 PT) — DECISIVE REPLAY: OK — full chain (download, digest, hydration,
  census byte-compare, decisive no-skip mint test) 13,180s at the repaired head (724ea28-era fix
  present). Log: ed-qual custody decisive-replay.log."
- `docs/run_reports/2026-08-18-t10-session.md:108` (results table): "**ED-QUAL-L4-1 decisive
  replay** | **`DECISIVE REPLAY: OK`** — full chain (download, digest, hydration, census
  byte-compare, decisive no-skip mint), 23 proof selections, **13,180.653 s** total |
  `decisive-replay.log`". Custody root `~/JouleWise-window-custody/ed-qual-20260817/` — **off-repo,
  Ed-held; the log itself is not in the repository.**
- Also recorded in `docs/process/ed-morning-packet-2026-08-18.md:119`: "ED-QUAL-L4-1 decisive
  replay: **DECISIVE REPLAY: OK** (3h40m, full …)".
- **Three attempts; two aborts were themselves catches.** `docs/run_reports/2026-08-18-t10-session.md`
  §2 "Three defects flushed by the operator run — fixed on main":
  - **`724ea28`** "decisive-test repair: import STACK_IDENTITY_DOMAIN from its post-#131 home" —
    "`mint1.STACK_IDENTITY_DOMAIN` was removed by #131 and re-introduced stale by the `add914a`
    resynthesis; **the decisive leg is CI-excluded, so only the operator replay could hit it**".
    **WHERE: merged to main** (verified `git merge-base --is-ancestor 724ea28 origin/main` → YES).
  - `d873f77` (bash 3.2 empty-array under `set -u`) and `e5dc38a` (blanket `sudo -n /usr/bin/true`
    probe vs command-scoped NOPASSWD) — both **merged to main**.
- Regression registered: `tests/test_decisive_reference_resolution.py:7` — "2026-08-17:
  mint1.STACK_IDENTITY_DOMAIN drift from #131 hit ED-QUAL-L4-1".
- The other four L4 unexecuted obligations (`sitting-packet-FINAL.md` §6 lines 240, 242, 243, 244)
  — full canonical suite on both interpreters at the baseline head, deep line-audit of
  `reduce.py`/`whole_window.py` interiors, the end-to-end sacrificial lifecycle (seat 10), and
  MET-VERDICT-ADJ-01 re-adjudication — have **no closure record found**.

### (c) Candidate disposition for the seat
**ED-ROW — CLOSED WITH EVIDENCE (evidence is off-repo).** The seat is adjudicating whether an
Ed-held `decisive-replay.log` under `~/JouleWise-window-custody/ed-qual-20260817/`, reported in two
in-repo documents but not committed, satisfies the charter's "closed with evidence" bar — and
whether a replay executed at a `724ea28`-era head still qualifies at HEAD `79a4cd0`, which is
~40 commits later.

### (d) Skeptical probes
1. Ask Ed (or the magistrate) to produce `~/JouleWise-window-custody/ed-qual-20260817/decisive-replay.log`
   at the sitting, and check its final line reads `DECISIVE REPLAY: OK` with the 13,180.653 s total
   and 23 proof selections. Nothing in the repository proves this; two prose records do.
2. `scripts/replay_d117_decisive.sh` exists at HEAD (2143 bytes). Ask what head the replay actually
   pinned and whether the mint fixtures it downloads changed after `724ea28` — `cef3306` (S0 kernel:
   generation-resolved mint policy, **branch-only**) touches `detection_floor.py` mint policy after
   the replay ran.
3. The decisive leg is **CI-excluded** by its own record. Ask what standing mechanism catches a
   second drift of the same class before the next window — a 3h40m operator-only test is not a
   regression net.
4. Charter: "Only T0 rows may remain open at the sitting." ED-L10-1 (the a9/a10 desk replay) and
   the dress rehearsal are ED-QUALIFICATION rows still open (see the L10 row). Ask whether L4 can
   be graded while a sibling stable row that would exercise L4's own §11 seam is unclosed.
5. Ask for the status of L4's four other unexecuted obligations, especially the full canonical
   suite on **both** interpreters at the current head — the seat ran 13 modules on 3.13 and 2 on
   3.11 at the baseline and explicitly disclaimed the rest.

---

## ROW-LEVEL OPEN ITEMS
- **L4-SF-2 (margin-receipt ↔ frozen-pack binding, WO-L4-3): NO REPAIR EXISTS.** No code, no
  runbook §12 line, no queue row. The seat's F3-B (re-pinned truncated pack → plausible PASS) and
  F3-C (validator accepts truncated sha-repaired receipt) attacks should both still succeed at HEAD.
- **L4-NIT-1 (WO-L4-4, record-only): undischarged.** `_close`'s tolerance is byte-for-byte
  unchanged since `8384287`, and no posture documentation was found.
- **The recorder check-to-grant race is closed by APPETITE, not by code.** `authentication_io.py:352`
  still re-resolves. The registered limitation's own **bounding workflow rule** ("single-operator,
  no concurrent repo-writing process during close-out; documented in the runbook §11 close-out
  preamble") is **NOT in the runbook** — the propagation was owed with WO-RECORDER-GRANT-IDENTITY
  and appears to have been retired with it. F-10 (post-grant grant-delta verification) was deferred
  into the same retired WO and may have been dropped silently.
- **L4-SF-1 / GAMMA route: code merged, packs non-conformant.** All three committed
  `analysis_manifest_v3.json` files (including the `_v3` freeze-0003 family) produce 4 refusals
  from the shipped `validate_prospective_analysis_manifest_v3`, and none carries the `families`
  block D-139 A2 requires. **No runsheet, runbook, or queue row schedules the re-authoring.**
- **L4-B1's cure has no CLI-level PASS proof.** Assembler verified `_pack_inventory` succeeds
  in-process on real frozen bytes; `RECEIPT_STATUS=PASS` over a real member corpus is asserted only
  in the PR #151 commit message and the composed verdict. The proof is ED-L10-1, still open.
- **Coverage denominator (24/27) is self-nominated, never attacked, and stale by 134,721
  insertions.** The council-ordered adversarial coverage re-enumeration (Phase 3) has not run, and
  the baseline manifest has not been superseded — so the charter's final-head-invalidation clause
  is live and unexercised for this row.
- **Four of L4's five unexecuted obligations have no closure record** (both-interpreter canonical
  suite, `reduce.py`/`whole_window.py` deep line-audit, the seat-10 end-to-end lifecycle,
  MET-VERDICT-ADJ-01). Only ED-QUAL-L4-1 closed.
- **Assembler could not verify** the ED-QUAL-L4-1 evidence itself: `decisive-replay.log` is
  Ed-held off-repo at `~/JouleWise-window-custody/ed-qual-20260817/` and is not in this worktree.
