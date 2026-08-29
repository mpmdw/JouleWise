# D-162 G2 — real `_v4` shakedown operator runsheet

**Purpose.** Execute the claim family’s first consuming launch as a one-block,
non-claim shakedown on its own runs root, then replay S11 A1..A5 and all four
F-5 joins at the desk and prove that outcome-blind finalization refuses the
partial collection. This is the R-2 re-cut of `RUNSHEET.md`; none of the old
`_v9` diagnostic-family generation, admission, marker, or floor-supply steps
apply. No command in a live section may run while an agent session is active.

**Authority.** D-162 R-2/R-3 and the 2026-08-28 ARM-ABORT/B10/copy-safety
addendum (`proof-consult/04-MAGISTRATE-RULING.md:55-91`); estate-11 S11 A1..A5
(`../2026-08-27-t26/s11-collector-manifest-id/estate11-assertions.md:1-46`);
D-160 F-5, R-3′ and NR-14 (`../2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md:103-166`);
Phase G/H5/H5a/H6 and refusal handling
(`../2026-08-22-t20/real-transaction-runbook.md:1161-1210,1253-1517,1617-1675`);
and the calibration/reference/launch/verdict chain
(`../../phase_2/window_runbook.md:1372-1848`).

**PASS.** The ARM-ABORT rehearsal produces one GO arm receipt, later expires
as `readiness_record_expired`, and writes no bundle; the consuming shakedown
arm launches once; pre and post bracket slots finalize; exactly one complete
A/B/B/A block is collected; the bracket binding is built before the one
authoritative passed verdict row; the reusable G3 desk block reports
`PASS NR14-LAYOUT`, no FAIL, and either exercised `PASS S11-A4` or
`SKIP S11-A4 present_stages=0 assertion_not_exercised`;
and the scratch-copy refusal check observes exactly
`analysis_finalization_member_cover_mismatch`. Any retry, second verdict,
missing predecessor, unexpected refusal, CONTRACT mutation, or write beneath
the real custody by the refusal check is not PASS.

## BLOCKERS — resolve before any live command

1. **OWN-B1 — the current `run_campaign.py` parser cannot select one A/B/B/A
   block from a frozen five-block `_v4` stage.** Its collection parser accepts
   a positional `config_dir` and campaign controls, but has no block/member
   selector (`scripts/run_campaign.py:648-719`); discovery consumes the JSON
   members named by that directory and its complete order manifest
   (`:2968-3072`). A copied/subset directory would no longer be the stage path
   authenticated by the prospective manifest
   (`:1402-1481`). Therefore the required one-block collection command is not
   rendered. Cure with a governed, prospective-manifest-authenticated
   one-block stage or a parser/selection artifact that production membership
   authenticates; do not pass an invented flag. Note on the one flag whose
   name invites confusion: `--shakedown-gate production_uncertainty_v1`
   (`scripts/run_campaign.py:672`) is NOT a selector and has nothing to do
   with the B-3 shakedown window. It is the P2-038 per-bundle gate — after
   each successful bundle it runs strict validation, a scratch re-reduce,
   strict post-reduce validation, the production-uncertainty assertion and
   the backup command, and stops the campaign on the first
   `SHAKEDOWN_GATE_FAILED[...]` (`:1990-2262`, `:8422-8436`, `:8727-8739`).
   The flag requires `--backup` and refuses unless the invocation consists of
   exactly one single-repetition config (`scripts/run_campaign.py:8108-8117`),
   so it constrains an invocation to one bundle but cannot select that bundle
   from a larger frozen stage.

2. **B-SUPPLY — the named measurement checkout does not yet contain the real `_v4`
   supply.** The 2026-08-28 desk census found no
   `configs/campaigns/d117_{contrast,floor}_*_v4` directories and no real v4
   aggregate-floor artifact under
   `/Users/edr/JouleWise-measurement-20260813`. Do not substitute `_v3`, `_v9`,
   the historical `df-ph-decode-floor-mint1.json`, or guessed bytes. The live
   gate reopens only at a reviewed head containing all three real `_v4` packs,
   their real freeze/mint supply, and the exact aggregate floor path.

3. **B3 — the retained `preflight.sh` still admits only the old dedicated
   smoke checkout path.** It requires `$SMOKE_CHECKOUT` to equal
   `/Users/edr/JouleWise-smoke/checkout`
   (`preflight.sh:35-58`). D-162 names the established measurement checkout.
   Because the amendment was limited to B10 and all other preflight bytes had
   to remain unchanged, no invocation is rendered here. The lead must either
   rule that checkout as the G2 execution checkout or authorize a separate
   real-pack preflight re-cut.

4. **B10 — physical ledger/pin continuity is a hard gate on every fresh
   checkout.** `runs/calibration_observation_ledger.jsonl` must exist and the
   production `load_calibration_ledger_snapshot` result must be refusal-free
   against tracked `configs/calibration/calibration_ledger_head.json`; a
   missing physical ledger at pin sequence 76 refuses
   `calibration_ledger_missing`, and a proper prefix refuses
   `calibration_ledger_rollback`
   (`joulewise/calibration_ledger.py:1973-2050`). The added preflight leg uses
   that loader, not a byte hash or hand-written sequence comparison. It has
   been provisioned in the named measurement checkout, but any later failure
   is an ABORT, never a copy-from-an-unknown-source retry.

5. **B2/B9 — both `_v4` arms and the consuming launch require the step-6
   confirmation pair.** The real gamma pack is in the registry's
   `successor_pack_ids`, so `_gate_family_publication` engages for both the
   rehearsal arm and the consuming arm (`joulewise/arm_readiness.py:11721-11752`;
   arm call at `:8137-8142`). This is the real-pack re-cut of #225's B9
   disclosure: unlike the discarded diagnostic pack, this pack is supposed to
   traverse the publication gate; no admission exception is needed, and the
   estate-11 transaction has produced the marker. A missing out-of-band digest
   refuses `confirmation_missing` before table semantics are trusted
   (`:11376-11416`). `generate_arm_readiness.py arm` and `verify` accept only
   `--expected-confirmation-digest`; they resolve the table implicitly from
   `<window-custody-root>/family_publication/d117_step6_confirmation_table_v4.json`
   (`:8077-8087`; CLI forwarding `scripts/generate_arm_readiness.py:141-152`).
   `launch_window.py` accepts both the explicit table path and digest
   (`scripts/launch_window.py:38-60`). Phase A must therefore stage the marker,
   marker sidecar, table, and table sidecar at the implicit custody location,
   and the lead must carry `hC` from the real transaction's E3/E4 custody
   transcript as a frozen input, never recompute it from table bytes
   (`real-transaction-runbook.md:1746-1764`).

No live command below is authorized until OWN-B1, B-SUPPLY, B2/B9, and B3 are cured at a newly reviewed
head and B10 passes in the actual execution checkout.

## NEEDS-RULING

1. **NR-1 — one-block authenticated selection.** Exactly four options remain;
   this runsheet does not choose among them:
   (a) run the full frozen stage, which amends G2's literal “one block”;
   (b) terminate after block one, whose clean-close/campaign-manifest semantics
   are unruled and which leaves incomplete members/locks while aborting the
   strict chain before post bracket and lifecycle completion;
   (c) freeze a one-block stage/chain list into the real successor pack before
   its reviewed freeze, which changes pack bytes before estate 11; or
   (d) add an authenticated runtime selector, which is a production gate change
   outside D-162 R-3. The science-block command below is consequently a
   `BLOCKED-UNTIL-RULING` template, not an instruction.

2. **Ledger-pin changed-set disposition.** The post-bracket pin bump changes
   `configs/calibration/calibration_ledger_head.json`, but that path is outside
   the registry’s 112-entry `irrelevant_path_allowlist`; the allowlist occupies
   `configs/arm_readiness/d117_row_registry_v2.json:212-324` and the pinset
   builder consumes the loaded registry at
   `scripts/build_v4_histsem_pinset.py:259-271`. Rule whether the pin bump is a
   campaign-relevant changed path requiring a new readiness/freeze cycle, or
   whether an explicit registry amendment is required. Do not silently commit
   it as irrelevant.

3. **Exact v4 floor artifact and checkout preflight.** Name the real mint’s
   aggregate-floor path and rule the B3 checkout mismatch. Until both are
   supplied, finalizer/refusal commands below are templates with exact parser
   flags but are not executable.

## Timeline

| Phase | Activity | Desk | Quiet machine |
|---|---|---:|---:|
| A | supply, parser, ledger and no-agent preflight | 10 min | 0 |
| B | separate ARM-ABORT rehearsal and expiry | 2 min | 5–6 min |
| C | fresh T-0 chain and clean dwell | 2 min | ≥10 min |
| D | consuming arm, launch, pre bracket, one ABBA block, post bracket, close | — | measured plan |
| E | binding then verdict | 2–5 min | 0 |
| F | reusable G3 provenance check and scratch refusal | 3–5 min | 0 |
| G | ledger-pin ruling/commit handoff and preservation | 5 min | 0 |

The rehearsal arm must expire completely before Phase C begins. It must never
straddle, borrow, or shorten the later T-0 clean dwell.

## Tree and fixed variables

The finalizer authenticates custody containment lexically and rejects any
symlinked component between each root as spelled and the file beneath it
(`joulewise/analysis_manifest_v3.py:1479`, used at `:3282`), and the checker's
`NR14-LAYOUT` mirrors that rule. `/var` or `/tmp` can therefore be valid when
used consistently as the lexical root; real paths remain the safest advice.

```text
/Users/edr/JouleWise-shakedown-g2/2026-08-29/
├── custody/
│   ├── prospective/                  # exact pack copies
│   ├── calibration/                  # exact completed ledger copy
│   ├── floors/                       # exact real-mint floor copy
│   └── runs/                         # RUNS_ROOT: non-claim, never campaign reuse
│       ├── bracket-binding.json      # built before verdict
│       ├── campaign_log.jsonl        # authoritative verdict row lives here
│       └── whole-window-verdict.json # copy of exact appended row
├── claims/                            # only analyze-claims outputs
├── scratch/                           # copy-safe refusal work; disposable
├── transcript/
├── window-plan/
└── rehearsal-window-plan/             # throwaway attempt/session ids
```

```sh
export MEASUREMENT_CHECKOUT=/Users/edr/JouleWise-measurement-20260813
export SMOKE_CHECKOUT=/Users/edr/JouleWise-smoke/checkout
export PY=/Users/edr/code/JouleWise/.venv/bin/python
export PYTHONPATH="$MEASUREMENT_CHECKOUT"
export SHAKEDOWN_ROOT=/Users/edr/JouleWise-shakedown-g2/2026-08-29
export CUSTODY_ROOT="$SHAKEDOWN_ROOT/custody"
export RUNS_ROOT="$CUSTODY_ROOT/runs"
export BOUND_RUNS_ROOT="$CUSTODY_ROOT/neg8-bound-runs"
export ANALYSIS_ROOT="$SHAKEDOWN_ROOT/analysis"
export CLAIMS_ROOT="$SHAKEDOWN_ROOT/claims"
export SCRATCH_ROOT="$SHAKEDOWN_ROOT/scratch"
export TRANSCRIPT_ROOT="$SHAKEDOWN_ROOT/transcript"
export WINDOW_PLAN_ROOT="$SHAKEDOWN_ROOT/window-plan"
export REHEARSAL_PLAN_ROOT="$SHAKEDOWN_ROOT/rehearsal-window-plan"
export PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4"
export FLOOR_15_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen25_1p5b_v4"
export FLOOR_7_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen25_7b_v4"
export POLICY="$MEASUREMENT_CHECKOUT/configs/campaign_policies/quiet_mac_p2_production.json"
export CALIBRATION_LEDGER="$MEASUREMENT_CHECKOUT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_CHECKOUT/configs/calibration/calibration_ledger_head.json"
export ARM_READINESS_CUSTODY_ROOT="$SHAKEDOWN_ROOT/arm-readiness"
export FAMILY_PUBLICATION_SOURCE_ROOT='LEAD-SUPPLIED-FROZEN-INPUT'
export FAMILY_PUBLICATION_ROOT="$ARM_READINESS_CUSTODY_ROOT/family_publication"
export FAMILY_PUBLICATION_MARKER="$FAMILY_PUBLICATION_ROOT/d117_family_publication_v4.json"
export STEP6_CONFIRMATION_TABLE="$FAMILY_PUBLICATION_ROOT/d117_step6_confirmation_table_v4.json"
# Lead carries hC from the real-transaction E4 custody transcript; never hash C here.
export EXPECTED_CONFIRMATION_DIGEST='LEAD-SUPPLIED-FROZEN-INPUT'
export BOUND_CONFIG_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/neg8_reference_corpus"
export BOUND_MANIFEST="$BOUND_CONFIG_ROOT/derivation/settled_corpus.json"
export REF_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/window_references"
export CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
export BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
export NEG8_DRIFT_BOUND="$RUNS_ROOT/neg8-drift-bound.json"
export FINALIZED_MANIFEST=''
export CHECK_FINALIZED_ARGS=''
export WINDOW_ID=d117-g2-shakedown-20260829
export BRACKET_SESSION_ID=d117-g2-shakedown-20260829-calibration
export PRE_ATTEMPT_ID=d117-g2-shakedown-20260829-cal-pre
export POST_ATTEMPT_ID=d117-g2-shakedown-20260829-cal-post
export REHEARSAL_WINDOW_ID=d117-g2-arm-abort-20260829
export REHEARSAL_SESSION_ID=d117-g2-arm-abort-throwaway-20260829
export REHEARSAL_PRE_ATTEMPT_ID=d117-g2-arm-abort-pre-throwaway-20260829
export REHEARSAL_POST_ATTEMPT_ID=d117-g2-arm-abort-post-throwaway-20260829
export POWER_POLICY=ac_high_power
export PLAN_ID="$(/usr/bin/jq -er '.plan.plan_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export PLAN_SHA256="$(/usr/bin/jq -er '.plan.sha256' "$PACK_ROOT/analysis_manifest_v3.json")"
export EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.evidence_root_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export PACK_MANIFEST_ID="$(/usr/bin/jq -er '.manifest_id' "$PACK_ROOT/analysis_manifest_v3.json")"
# Lead supplies this from the real v4 mint transcript; never guess it.
export AGGREGATE_FLOOR_ARTIFACT='NEEDS-RULING'
```

The two arms consume distinct ids. The rehearsal arm is the earlier,
non-consuming arm; its receipt becomes the predecessor/supersession link in
the family arm chain. The shakedown arm is therefore the family’s first
**consuming** arm and launches the B-3 non-claim window. Its bundle occurrences,
campaign manifests, and verdict remain isolated in `$RUNS_ROOT`; whole-window
membership is reconstructed from campaign records, not an arm roster
(`scripts/run_campaign.py:5534-5595`), and raw supersession visibility is read
from the run root’s campaign log (`joulewise/whole_window.py:2843-2908`). This
shakedown never counts as one of the published campaign’s claim occurrences.

## Phase A — desk preflight

### A1 — fixed supply and checkout inspection (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <2 min. Expected artifact: transcript
only. Expected refusal: any absent pack/file, non-main head, dirty governed
path, unresolved floor path, or B10 refusal.

```sh
cd "$MEASUREMENT_CHECKOUT"
test "$(git branch --show-current)" = main
test -f "$PACK_ROOT/analysis_manifest_v3.json"
test -f "$PACK_ROOT/plan_tree.json"
test -f "$PACK_ROOT/calibration_plan.json"
test -f "$FLOOR_15_PACK_ROOT/plan_tree.json"
test -f "$FLOOR_7_PACK_ROOT/plan_tree.json"
test -f "$AGGREGATE_FLOOR_ARTIFACT"
test -f "$CALIBRATION_LEDGER"
test -f "$LEDGER_HEAD_PIN"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json.sha256"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json.sha256"
test "$EXPECTED_CONFIRMATION_DIGEST" != LEAD-SUPPLIED-FROZEN-INPUT
```

Do not run `preflight.sh` until B3 is ruled. Once ruled, execute its unchanged
checkout gates plus the new B10 production-loader gate; never cherry-pick only
the PASS text.

### A2 — stage the complete finalizer input tree in custody (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <2 min before launch, then <1 min after
the post bracket. Expected artifacts: a byte-identical complete pack subtree,
floor, completed ledger, and adjacent head pin. Expected refusal: any recursive
diff or `cmp` mismatch. The prospective validator resolves every binding
relative to the manifest directory: calibration plan
(`analysis_manifest_v3.py:1945-1952`), root order manifest (`:1964-1971`), four
stage order manifests (`:1982-2008`), four condition-family definitions
(`:2030-2088`), every non-null prompt artifact (`:2330-2348`), and all 80 member
configs (`:2567-2574`). The finalizer runs that complete validator before its
member-cover check (`:3775-3784` before `:2970-2980`), so partial staging is a
staging defect, not a night result.

```sh
/bin/mkdir -p "$CUSTODY_ROOT/prospective" "$CUSTODY_ROOT/calibration" \
  "$CUSTODY_ROOT/floors" "$RUNS_ROOT" "$BOUND_RUNS_ROOT" "$ANALYSIS_ROOT" "$CLAIMS_ROOT" \
  "$SCRATCH_ROOT" "$TRANSCRIPT_ROOT" "$WINDOW_PLAN_ROOT" "$REHEARSAL_PLAN_ROOT"
/bin/cp -Rp "$PACK_ROOT/." "$CUSTODY_ROOT/prospective/"
/bin/cp -p "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v4-aggregate-floor.json"
/usr/bin/diff -r "$PACK_ROOT" "$CUSTODY_ROOT/prospective"
/usr/bin/cmp -s "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v4-aggregate-floor.json"
```

After D1 completes both bracket slots, complete the same staging unit before E1:

```sh
/bin/cp -p "$CALIBRATION_LEDGER" "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
/bin/cp -p "$LEDGER_HEAD_PIN" "$CUSTODY_ROOT/calibration/calibration_ledger_head.json"
/usr/bin/cmp -s "$CALIBRATION_LEDGER" "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
/usr/bin/cmp -s "$LEDGER_HEAD_PIN" "$CUSTODY_ROOT/calibration/calibration_ledger_head.json"
```

### A3 — stage the publication marker and confirmation pair (MAGISTRATE)

The source directory and `hC` are lead-produced frozen inputs from the real
transaction. Copy all four published bytes into the arm API's implicit custody
directory; do not rename, regenerate, or hash the table to obtain `hC`.

```sh
/bin/mkdir -p "$FAMILY_PUBLICATION_ROOT"
/bin/cp -p "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json" "$FAMILY_PUBLICATION_MARKER"
/bin/cp -p "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json.sha256" "$FAMILY_PUBLICATION_MARKER.sha256"
/bin/cp -p "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json" "$STEP6_CONFIRMATION_TABLE"
/bin/cp -p "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json.sha256" "$STEP6_CONFIRMATION_TABLE.sha256"
/usr/bin/cmp -s "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json" "$FAMILY_PUBLICATION_MARKER"
/usr/bin/cmp -s "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json.sha256" "$FAMILY_PUBLICATION_MARKER.sha256"
/usr/bin/cmp -s "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json" "$STEP6_CONFIRMATION_TABLE"
/usr/bin/cmp -s "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json.sha256" "$STEP6_CONFIRMATION_TABLE.sha256"
```

## Phase B — first live step: ARM-ABORT REHEARSAL

### B1 — capture a separate throwaway T-0 set (ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: the governed prewindow dwell plus <2
min. Expected artifacts: the six ordered T-0 receipts, `arm-context.json`, and
`launch-manifest.json` beneath rehearsal readiness custody. Expected refusal:
`evidence_author_t0_capture_*`. Use exactly the 25 `WINDOW_ENV_KEYS` accepted at
`joulewise/arm_readiness_evidence_t0.py:63-91`; the rehearsal values must use
the throwaway window/session/attempt ids above. The environment authoring
command is intentionally not rendered: it is lead-produced frozen input and
B1/B3 must be cured before it can be made exact.

```sh
for step in clock-reference clock-disable quiet-mac-prep prewindow-check ledger-readiness ledger-reservation; do
  "$PY" scripts/capture_t0_step.py "$step" \
    --pack-root "$PACK_ROOT" \
    --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
    --window-plan-root "$REHEARSAL_PLAN_ROOT" \
    > "$TRANSCRIPT_ROOT/rehearsal-t0-$step.json" || exit 1
done
```

### B2 — arm once, never launch, then prove expiry (ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: arm <1 min, then wait beyond the governed
300 s budget. Expected artifacts: one arm receipt and sidecar; after the wait,
verification refuses `readiness_record_expired`; `$RUNS_ROOT` still contains no
bundle. The registry pins `arm_to_consume_budget_ns` to 300,000,000,000
(`configs/arm_readiness/d117_row_registry_v2.json:4`) and the arm proves all
four exact `t0.single_launch_capability.v1` facts:
`atomic_single_use_capability_available`, `attempt_ids_unused`,
`exact_launch_command_frozen`, and `session_id_unused`
(`joulewise/arm_readiness.py:980-984`).

```sh
export REHEARSAL_ARM_CONTEXT_JSON="$(/usr/bin/jq -c . "$ARM_READINESS_CUSTODY_ROOT/$(basename "$PACK_ROOT")/arm_readiness.t0.inputs/arm-context.json")"
"$PY" scripts/generate_arm_readiness.py arm \
  --pack-root "$PACK_ROOT" \
  --arm-context "$REHEARSAL_ARM_CONTEXT_JSON" \
  --window-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$TRANSCRIPT_ROOT/rehearsal-arm.json"
export REHEARSAL_ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$TRANSCRIPT_ROOT/rehearsal-arm.json")"
"$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$REHEARSAL_ARM_RECEIPT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$TRANSCRIPT_ROOT/rehearsal-arm-initial-verify.json"
# ED waits until the receipt's valid_until_monotonic_ns has passed; never start C1 early.
if "$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$REHEARSAL_ARM_RECEIPT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$TRANSCRIPT_ROOT/rehearsal-arm-expiry.json"; then exit 1; fi
test "$(/usr/bin/find "$RUNS_ROOT" -mindepth 1 -maxdepth 1 -type d | /usr/bin/wc -l | tr -d ' ')" = 0
```

Never call `launch_window.py` with the rehearsal receipt. Phase C starts only
after the expected expiry refusal is preserved and all rehearsal processes
have ended.

## Phase C — consuming shakedown T-0 and arm

### C1 — fresh six-step T-0 chain (ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: ≥10 min clean dwell. Expected artifacts:
a second, distinct six-receipt T-0 set, arm context, and launch manifest.
Expected refusal: any `evidence_author_t0_capture_*`; no retry. The lead-built
`$WINDOW_PLAN_ROOT/window.env` uses the real shakedown ids, not rehearsal ids.

```sh
for step in clock-reference clock-disable quiet-mac-prep prewindow-check ledger-readiness ledger-reservation; do
  "$PY" scripts/capture_t0_step.py "$step" \
    --pack-root "$PACK_ROOT" \
    --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
    --window-plan-root "$WINDOW_PLAN_ROOT" \
    > "$TRANSCRIPT_ROOT/shakedown-t0-$step.json" || exit 1
done
```

### C2 — author and verify the consuming arm (ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifact: one distinct
GO arm receipt, chained after the expired rehearsal receipt. Expected refusal:
any `readiness_*` NO_GO. The arm receipt id is recorded as the shakedown’s arm
coordinate; the later launch completion is its occurrence coordinate. H5 calls
the campaign complete only when the executed arm set equals the published plan
and names both the last consuming arm and consume completion
(`real-transaction-runbook.md:1253-1300`); this one-block non-claim run cannot
satisfy that full-campaign equality.

```sh
export ARM_CONTEXT_JSON="$(/usr/bin/jq -c . "$ARM_READINESS_CUSTODY_ROOT/$(basename "$PACK_ROOT")/arm_readiness.t0.inputs/arm-context.json")"
"$PY" scripts/generate_arm_readiness.py arm \
  --pack-root "$PACK_ROOT" --arm-context "$ARM_CONTEXT_JSON" \
  --window-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$TRANSCRIPT_ROOT/shakedown-arm.json"
export ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$TRANSCRIPT_ROOT/shakedown-arm.json")"
"$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$ARM_RECEIPT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$TRANSCRIPT_ROOT/shakedown-arm-verify.json"
export LAUNCH_MANIFEST="$ARM_READINESS_CUSTODY_ROOT/$(basename "$PACK_ROOT")/arm_readiness.t0.inputs/launch-manifest.json"
```

## Phase D — one physical launch and close

### D1 — launch the frozen chain exactly once (ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: consumes the live plan. Expected
artifacts: launch consumption, start/settle/completion lifecycle receipts, two
calibration slots, and four science bundles. Expected refusal:
`launch_consumption_*`, `launch_handoff_invalid`, any calibration refusal, or
any collection nonzero. The current launcher flags are exact
(`scripts/launch_window.py:38-60`).

```sh
"$PY" scripts/launch_window.py \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"
```

The launcher invokes the frozen chain; the following is its governed command
template, not a second operator invocation. It follows the runbook's exact
order: start lifecycle, settle, pre bracket, bound corpus and derivation, start
triplet, before-midpoint science, midpoint, after-midpoint science, end triplet,
post bracket, completion (`window_runbook.md:1663-1727`). Every flag below was
confirmed from the current CLI `--help`.

```sh
"$PY" scripts/launch_window.py \
  --pack-root "$PACK_ROOT" --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" --lifecycle-event start \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"

SLOT=pre ATTEMPT_ID="$PRE_ATTEMPT_ID" \
"$PY" scripts/validate_powermetrics_fiducial.py --allow-live \
  --arm-countdown-s 20 --sleep-display-before-capture \
  --output-root "$RUNS_ROOT/instrument_validation" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$BRACKET_SESSION_ID" --slot pre --attempt-id "$PRE_ATTEMPT_ID" \
  --power-policy "$POWER_POLICY"

"$PY" scripts/run_campaign.py "$BOUND_CONFIG_ROOT" \
  --runs-dir "$BOUND_RUNS_ROOT" --log "$BOUND_LOG" \
  --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1
"$PY" scripts/run_campaign.py \
  --derive-neg8-drift-bound "$BOUND_MANIFEST" \
  --neg8-drift-bound-output "$NEG8_DRIFT_BOUND" \
  --runs-dir "$BOUND_RUNS_ROOT"

"$PY" scripts/run_campaign.py "$REF_ROOT/start_triplet" \
  --runs-dir "$RUNS_ROOT" --log "$CLAIM_LOG" --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1

# BLOCKED-UNTIL-RULING NR-1 — TEMPLATE ONLY; option (a) would run all five blocks.
"$PY" scripts/run_campaign.py "$PACK_ROOT/01_decode_contrast_blocks_01_05" \
  --runs-dir "$RUNS_ROOT" --log "$CLAIM_LOG" --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1

"$PY" scripts/run_campaign.py "$REF_ROOT/midpoint" \
  --runs-dir "$RUNS_ROOT" --log "$CLAIM_LOG" --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1
"$PY" scripts/run_campaign.py "$REF_ROOT/end_triplet" \
  --runs-dir "$RUNS_ROOT" --log "$CLAIM_LOG" --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1

SLOT=post ATTEMPT_ID="$POST_ATTEMPT_ID" \
"$PY" scripts/validate_powermetrics_fiducial.py --allow-live \
  --arm-countdown-s 20 --sleep-display-before-capture \
  --output-root "$RUNS_ROOT/instrument_validation" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$BRACKET_SESSION_ID" --slot post --attempt-id "$POST_ATTEMPT_ID" \
  --power-policy "$POWER_POLICY"
"$PY" scripts/launch_window.py \
  --pack-root "$PACK_ROOT" --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" --lifecycle-event completion \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"
```

## Phase E — postcollection binding before verdict

### E1 — build the binding from the completed staged ledger pair (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts: the completed
ledger and adjacent head already byte-verified by A2, plus
`$RUNS_ROOT/bracket-binding.json`. Expected refusal:
`bracket_binding_session_not_finalized`, endpoint invalid, ledger rollback, or
runs-root identity mismatch. The builder precedes the verdict by R-3′/H5a and
accepts the exact flags at `scripts/build_bracket_binding.py:383-413`.

```sh
"$PY" scripts/build_bracket_binding.py \
  --custody-root "$CUSTODY_ROOT" \
  --session-id "$BRACKET_SESSION_ID" \
  --window-id "$WINDOW_ID" \
  --plan-id "$PLAN_ID" \
  --plan-sha256 "$PLAN_SHA256" \
  --frozen-plan "$CUSTODY_ROOT/prospective/calibration_plan.json" \
  --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --runs-root "$RUNS_ROOT" \
  --calibration-ledger "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl" \
  --head-pin "$CUSTODY_ROOT/calibration/calibration_ledger_head.json" \
  --output "$RUNS_ROOT/bracket-binding.json" \
  > "$TRANSCRIPT_ROOT/bracket-binding.json"
```

### E2 — append and publish one whole-window verdict (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts: one
authoritative row appended to `$RUNS_ROOT/campaign_log.jsonl` and its exact
copy at `$RUNS_ROOT/whole-window-verdict.json`, both beneath the runs root as
NR-14 requires. Expected refusal: bracket binding invalid/missing, window
membership unresolved, or any whole-window condition. `run_campaign.py` has no
`--calibration-ledger` or `--head-pin`; it reads the code-owned default paths,
so B10 must already pass. Do not invent those flags. The producer loads the
derived NEG-8 bound and reconstructs the reference membership at
`scripts/run_campaign.py:6149-6165`; without the governed corpus/bound and
start/midpoint/end references the production-policy verdict is `failed`, its
endpoint protocol is `invalid`, and the conditions include
`neg8_bracket_missing`, `neg8_bracket_reference_invalid`,
`neg8_drift_bound_underived`, and
`neg8_idle_sub_drift_bound_underived`.

```sh
"$PY" scripts/run_campaign.py --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" \
  --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy "$POLICY" \
  --neg8-drift-bound "$RUNS_ROOT/neg8-drift-bound.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --whole-window-verdict-output "$RUNS_ROOT/whole-window-verdict.json" \
  > "$TRANSCRIPT_ROOT/whole-window-verdict.stdout" \
  2> "$TRANSCRIPT_ROOT/whole-window-verdict.stderr"
/usr/bin/jq -e '.status == "passed"' "$RUNS_ROOT/whole-window-verdict.json"
```

## Phase F — G2 desk checks

### F1 — run the reusable G3 provenance block (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifact: transcript
with PASS/SKIP lines and no FAIL. Expected refusal: any S11/F-5 failure. Execute
the reusable block below with `FINALIZED_MANIFEST` unset; do not duplicate its
command here.

See [G3 — nightly desk check (reusable)](#g3--nightly-desk-check-reusable).

### F2 — prove exact finalizer refusal on a scratch custody copy (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected output:
`PASS FINALIZE-REFUSAL observed={analysis_finalization_member_cover_mismatch}`.
Expected refusal mismatch: nonzero with observed/expected sets named. The
finalizer itself exposes one `AnalysisManifestFinalizationError.reason_code`
per call (`scripts/finalize_analysis_manifest.py:42-56`); the checker compares
that observable singleton exactly. It copies custody below `$SCRATCH_ROOT`
before calling the finalizer, because finalization writes the finalized
manifest append-only into its custody output
(`joulewise/analysis_manifest_v3.py:3738-3816`).

```sh
"$PY" scripts/check_window_provenance.py --expect-finalize-refusal \
  --scratch-dir "$SCRATCH_ROOT" \
  --prospective-manifest "$CUSTODY_ROOT/prospective/analysis_manifest_v3.json" \
  --plan-tree "$CUSTODY_ROOT/prospective/plan_tree.json" \
  --custody-root "$CUSTODY_ROOT" \
  --runs-root "$RUNS_ROOT" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --calibration-ledger "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl" \
  --aggregate-floor-artifact "$CUSTODY_ROOT/floors/d117-v4-aggregate-floor.json" \
  --output-dir "$CUSTODY_ROOT"
```

The default expected set is reachable **only** from A2's complete staged pack
subtree and completed adjacent ledger/head pair. If the stage directories or
any other manifest-relative binding are absent, the observed singleton is
`analysis_finalization_prospective_invalid`; that is a custody staging error,
not a night result, and it must remain nonzero because it differs from the
default. With complete staging, the default expected set is derived from the real finalizer’s passed-verdict
member-cover gate, not from the analysis engine’s later claim counts: a
one-block basis does not cover all 80 frozen members and refuses
`analysis_finalization_member_cover_mismatch`
(`joulewise/analysis_manifest_v3.py:2970-2980`). It never reaches
`insufficient_complete_blocks` / `fixed_n_plan_incomplete`, which belong to the
claim engine (`joulewise/analysis_engine/__init__.py:690-700`).

`analyze-claims` is copy-safe with respect to the source trees: it reads the
manifest/runs/floor inputs and writes only `--output`
(`joulewise/cli.py:2003-2019`). Finalize is not copy-safe, hence the mandatory
scratch copy above. A G2 partial collection must not be finalized in real
custody and must not produce a claim artifact.

## Phase G — pin bump, post-run record, and preservation

### G1 — classify the tracked pin advance (NEEDS-RULING; ED PROMPT)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <2 min. Expected artifact: diff showing
the new ledger head after the two bracket receipts. Expected refusal: unchanged
pin, ledger loader refusal, or any changed path not explained by the window.

```sh
git diff -- configs/calibration/calibration_ledger_head.json
git status --short --branch
```

Do not commit until the allowlist ruling above is recorded. If authorized, the
named step is **“commit the shakedown calibration-ledger head-pin advance”**;
only Ed/lead may commit. The physical JSONL remains untracked run state and is
preserved with custody evidence; the tracked pin is the reviewed code change.

### G2 — post-run assertions (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts: final tree
census and immutable transcript. Expected refusal: any extra bundle, second
verdict, scratch residue inside custody, or modified pack byte.

```sh
test "$(/usr/bin/jq -r 'select(.record_type=="idle_admission_whole_window_verdict") | .record_type' "$RUNS_ROOT/campaign_log.jsonl" | /usr/bin/wc -l | tr -d ' ')" = 1
/usr/bin/find "$RUNS_ROOT" -mindepth 1 -maxdepth 2 -print | /usr/bin/sort > "$TRANSCRIPT_ROOT/runs-tree.txt"
/usr/bin/find "$CUSTODY_ROOT" -type f -print0 | /usr/bin/xargs -0 shasum -a 256 > "$TRANSCRIPT_ROOT/custody-sha256.txt"
git status --short --branch > "$TRANSCRIPT_ROOT/git-status.txt"
```

## ABORT — any refusal, no retry

On any nonzero exit, exception, unexpected PASS/FAIL set, missing artifact,
extra bundle, second verdict, expired consuming arm, or process-census failure:

1. stop the chain; do not issue another arm, session id, attempt id, bracket,
   bundle, binding, or verdict;
2. preserve the publication marker/table and sidecars, both arm receipts, all
   T-0 receipts, every launch lifecycle receipt, bound-corpus bundles and bound,
   start/midpoint/end reference bundles, partial science bundles, campaign
   manifests/logs, ledger and head pin, pre/post calibration custody,
   binding/verdict if present, stdout/stderr, and `git status`;
3. write the refusal JSON/stdout/stderr under `$TRANSCRIPT_ROOT/refusals/` and
   record its SHA-256 in the operator handoff;
4. label the run `ABORTED_NON_CLAIM_BEARING`; never move its bundles into a
   campaign runs root and never describe fixture/mock evidence as hardware
   validation;
5. return the exact blocker/refusal to Ed. A new attempt requires new ruled ids
   and a fresh run, not a retry in this root.

## Post-run handoff

Return: reviewed head, both arm receipt ids and dispositions, consuming launch
completion id, bracket session/pre/post ids, ledger pre/post pin coordinates,
exact runs root, bundle roster, campaign-manifest roster, binding/verdict
digests, G3 transcript, exact observed refusal set, dirty-tree roster, and all
BLOCKER/NEEDS-RULING dispositions. Do not finalize, claim, commit, push, seal,
or delete as part of this runsheet.

### G3 — nightly desk check (reusable)

Set `$RUNS_ROOT` to that night’s exact runs root. The pack/custody/binding/
verdict/ledger variables must name artifacts for that same window. For G2,
leave `FINALIZED_MANIFEST` empty; after a full campaign finalizes, set it so
S11-A2 selects `lineage.collection_manifest_id`. The roster defaults to S11
A4's committed calibration/reference/floor/metrology list. It may instead be
passed explicitly from the frozen `before_midpoint_stages.txt` and
`after_midpoint_stages.txt` files; the checker does not derive those lists.
When none of the configured stages is present it prints exactly
`SKIP S11-A4 present_stages=0 assertion_not_exercised`, never a vacuous PASS;
SKIP does not change the exit status. Stage matching uses the campaign
manifest's `config_dir`, written by `new_campaign_provenance`
(`run_campaign.py:3436-3452`, caller `:8223-8229`).

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected output:
`PASS NR14-LAYOUT`, one PASS/FAIL line per exercised assertion, the S11-A4
PASS-or-SKIP result above, and `SUMMARY ... fail=0`. Expected
refusal: any FAIL or exception gives nonzero; the checker writes nothing.

```sh
CHECK_FINALIZED_ARGS=()
if [ -n "${FINALIZED_MANIFEST:-}" ]; then
  CHECK_FINALIZED_ARGS=(--finalized-manifest "$FINALIZED_MANIFEST")
fi
"$PY" scripts/check_window_provenance.py \
  --runs-root "$RUNS_ROOT" \
  --pack-root "$PACK_ROOT" \
  --custody-root "$CUSTODY_ROOT" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  "${CHECK_FINALIZED_ARGS[@]}" \
  > "$TRANSCRIPT_ROOT/window-provenance.txt"
/bin/cat "$TRANSCRIPT_ROOT/window-provenance.txt"
```
