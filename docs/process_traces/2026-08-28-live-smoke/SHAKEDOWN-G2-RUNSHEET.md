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
authoritative passed verdict row; the reusable G3 desk block reports no FAIL;
and the scratch-copy refusal check observes exactly
`analysis_finalization_member_cover_mismatch`. Any retry, second verdict,
missing predecessor, unexpected refusal, CONTRACT mutation, or write beneath
the real custody by the refusal check is not PASS.

## BLOCKERS — resolve before any live command

1. **B1 — the current `run_campaign.py` parser cannot select one A/B/B/A
   block from a frozen five-block `_v4` stage.** Its collection parser accepts
   a positional `config_dir` and campaign controls, but has no block/member
   selector (`scripts/run_campaign.py:648-719`); discovery consumes the JSON
   members named by that directory and its complete order manifest
   (`:2968-3072`). A copied/subset directory would no longer be the stage path
   authenticated by the prospective manifest
   (`:1402-1481`). Therefore the required one-block collection command is not
   rendered. Cure with a governed, prospective-manifest-authenticated
   one-block stage or a parser/selection artifact that production membership
   authenticates; do not pass an invented flag.

2. **B2 — the named measurement checkout does not yet contain the real `_v4`
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

No live command below is authorized until B1–B3 are cured at a newly reviewed
head and B10 passes in the actual execution checkout.

## NEEDS-RULING

1. **One-block authenticated selection.** Choose between a frozen one-block
   stage emitted in the real pack and a production-authenticated selector.
   Recommendation: an outcome-blind selector bound into the pack/arm plan, so
   the shakedown stays on real bytes and the campaign manifest records the
   exact selected occurrence. This blocks the launch-chain rendering.

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
export PY=/Users/edr/code/JouleWise/.venv/bin/python
export PYTHONPATH="$MEASUREMENT_CHECKOUT"
export SHAKEDOWN_ROOT=/Users/edr/JouleWise-shakedown-g2/2026-08-29
export CUSTODY_ROOT="$SHAKEDOWN_ROOT/custody"
export RUNS_ROOT="$CUSTODY_ROOT/runs"
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
```

Do not run `preflight.sh` until B3 is ruled. Once ruled, execute its unchanged
checkout gates plus the new B10 production-loader gate; never cherry-pick only
the PASS text.

### A2 — stage exact pack copies in custody (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts: exact
prospective/tree/plan/floor copies and a pre-bracket ledger snapshot under
custody. Expected refusal: any `cmp` mismatch. These copies make the later
refusal mode copy-safe because every finalizer argument is beneath
`$CUSTODY_ROOT`.

```sh
/bin/mkdir -p "$CUSTODY_ROOT/prospective" "$CUSTODY_ROOT/calibration" \
  "$CUSTODY_ROOT/floors" "$RUNS_ROOT" "$ANALYSIS_ROOT" "$CLAIMS_ROOT" \
  "$SCRATCH_ROOT" "$TRANSCRIPT_ROOT" "$WINDOW_PLAN_ROOT" "$REHEARSAL_PLAN_ROOT"
/bin/cp -p "$PACK_ROOT/analysis_manifest_v3.json" "$CUSTODY_ROOT/prospective/analysis_manifest_v3.json"
/bin/cp -p "$PACK_ROOT/plan_tree.json" "$CUSTODY_ROOT/prospective/plan_tree.json"
/bin/cp -p "$PACK_ROOT/calibration_plan.json" "$CUSTODY_ROOT/prospective/calibration_plan.json"
/bin/cp -p "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v4-aggregate-floor.json"
/usr/bin/cmp -s "$PACK_ROOT/analysis_manifest_v3.json" "$CUSTODY_ROOT/prospective/analysis_manifest_v3.json"
/usr/bin/cmp -s "$PACK_ROOT/plan_tree.json" "$CUSTODY_ROOT/prospective/plan_tree.json"
/usr/bin/cmp -s "$PACK_ROOT/calibration_plan.json" "$CUSTODY_ROOT/prospective/calibration_plan.json"
/usr/bin/cmp -s "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v4-aggregate-floor.json"
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
  > "$TRANSCRIPT_ROOT/rehearsal-arm.json"
export REHEARSAL_ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$TRANSCRIPT_ROOT/rehearsal-arm.json")"
"$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$REHEARSAL_ARM_RECEIPT" \
  > "$TRANSCRIPT_ROOT/rehearsal-arm-initial-verify.json"
# ED waits until the receipt's valid_until_monotonic_ns has passed; never start C1 early.
if "$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$REHEARSAL_ARM_RECEIPT" \
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
  > "$TRANSCRIPT_ROOT/shakedown-arm.json"
export ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$TRANSCRIPT_ROOT/shakedown-arm.json")"
"$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$ARM_RECEIPT" \
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
  --launch-manifest "$LAUNCH_MANIFEST"
```

The frozen chain invoked by D1, never by hand, has this strict order:

1. `launch_window.py --lifecycle-event start`;
2. pre bracket via the exact command below;
3. the governed B1 cure’s one A/B/B/A block via `run_campaign.py`;
4. post bracket via the same exact command with `post` ids;
5. `launch_window.py --lifecycle-event completion`.

The bracket command accepted by the current parser is:

```sh
"$PY" scripts/validate_powermetrics_fiducial.py --allow-live \
  --arm-countdown-s 20 --sleep-display-before-capture \
  --output-root "$RUNS_ROOT/instrument_validation" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$BRACKET_SESSION_ID" --slot "$SLOT" --attempt-id "$ATTEMPT_ID" \
  --power-policy "$POWER_POLICY"
```

`SLOT/PRE_ATTEMPT_ID` are used before the block and
`SLOT/POST_ATTEMPT_ID` after it. The required one-block collection command is
not rendered while B1 is open. The full-stage form below is shown only to name
the flags the current parser actually accepts; **DO NOT EXECUTE IT**, because
it would collect five blocks rather than one:

```sh
# NOT EXECUTABLE FOR G2 WHILE B1 IS OPEN
"$PY" scripts/run_campaign.py "$PACK_ROOT/01_decode_contrast_blocks_01_05" \
  --runs-dir "$RUNS_ROOT" --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$RUNS_ROOT/instrument_validation/$PRE_ATTEMPT_ID" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1
```

## Phase E — postcollection binding before verdict

### E1 — copy the completed ledger and build the binding (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts:
`$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl` and
`$RUNS_ROOT/bracket-binding.json`. Expected refusal:
`bracket_binding_session_not_finalized`, endpoint invalid, ledger rollback, or
runs-root identity mismatch. The builder precedes the verdict by R-3′/H5a and
accepts the exact flags at `scripts/build_bracket_binding.py:383-413`.

```sh
/bin/cp -p "$CALIBRATION_LEDGER" "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
"$PY" scripts/build_bracket_binding.py \
  --custody-root "$CUSTODY_ROOT" \
  --session-id "$BRACKET_SESSION_ID" \
  --window-id "$WINDOW_ID" \
  --plan-id "$PLAN_ID" \
  --plan-sha256 "$PLAN_SHA256" \
  --frozen-plan "$CUSTODY_ROOT/prospective/calibration_plan.json" \
  --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --runs-root "$RUNS_ROOT" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
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
so B10 must already pass. Do not invent those flags.

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

The default expected set is derived from the real finalizer’s passed-verdict
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
2. preserve the arm receipt, all T-0 receipts, launch lifecycle, partial bundle
   directories, campaign manifests/log, ledger and head pin, calibration
   custody, binding/verdict if present, stdout/stderr, and `git status`;
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
S11-A2 selects `lineage.collection_manifest_id`. Stages absent from a nightly
root print `SKIP S11-A4 <stage> absent`; SKIP never changes the exit status.

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected output: one PASS/FAIL
line per assertion, optional S11-A4 SKIPs, and `SUMMARY ... fail=0`. Expected
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
