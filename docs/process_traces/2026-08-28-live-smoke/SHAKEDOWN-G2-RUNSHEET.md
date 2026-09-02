# D-162 G2-a / desk day / G2-b operator runsheet

**Purpose.** Split the ruled G2 proof across G2-a, one desk day, and G2-b.
G2-a brackets four prefill-resolvability probes before the `_v5` pack exists;
the desk day pins the selected prefill length and cuts the real pack; G2-b
executes the claim family’s first consuming launch as a one-block, non-claim
shakedown on its own runs root and proves exact finalizer refusal. No command
in a live section may run while an agent session is active.

G2 is **diagnostic and non-claim by construction**: `$RUNS_ROOT` is its own
shakedown root, never the campaign runs root, and no mint or claim artifact may
consume it. G2 PASS means exact refusal-set equality from
`--expect-finalize-refusal`; it does not mean that any downstream artifact was
produced or licensed. D-164 supersedes `_v4`: every collection path below is a
real Qwen3 `_v5` coordinate cut during the desk day. Publication-table
filenames retain their separately versioned `v4` wire names; they are not pack
generation labels.

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

## Amendment 2026-09-01 (ruling 97)

This amendment preserves the prior record while correcting the night commands
under ruling 97. Old lines 69--74 struck the aggregate-floor precondition:
the floor is minted inside the transaction, so no floor bytes can exist before
G2-b. Old lines 117--121's remaining ruling is resolved because the refusal
command is executable with its absent custody path. Old line 149's tree entry,
old line 212's `export AGGREGATE_FLOOR_ARTIFACT='NEEDS-RULING'`, and old lines
550, 591, and 593's floor-file check/copy/compare are removed so custody keeps
an empty floors directory. Old lines 178--180 used the errata
`qwen3_1p7b`, `qwen3_8b`, and `qwen3_1p7b_vs_8b`; the generator's hyphenated
ids are canonical. Old F2 text is amended with pre/post emptiness assertions,
a STOP for an attachment-missing observation, and ruling 97's member-cover
proof scope: bracket and ledger/head authentication are outside the finalizer
at that gate and are instead exercised by E1 on the night.

### Struck text (verbatim, from the pre-amendment record)

Old lines 69--74:

```text
   `configs/campaigns/d117_{contrast,floor}_*_v5` directories and no real v5
   aggregate-floor artifact under
   `/Users/edr/JouleWise-measurement-20260813`. Do not substitute `_v3`, `_v4`, `_v9`,
   the historical `df-ph-decode-floor-mint1.json`, or guessed bytes. The live
   gate reopens only at a reviewed head containing all three real `_v5` packs,
   their real freeze/mint supply, and the exact aggregate floor path.
```

Old lines 119--121:

```text
1. **Exact `_v5` floor artifact.** Name the real mint’s aggregate-floor path.
   Until supplied, finalizer/refusal commands below are templates with exact
   parser flags but are not executable.
```

Old line 149:

```text
│   ├── floors/                       # exact real-mint floor copy
```

Old lines 178--180:

```text
export PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_contrast_qwen3_1p7b_vs_8b_v5"
export FLOOR_15_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen3_1p7b_v5"
export FLOOR_7_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen3_8b_v5"
```

Old lines 211--212:

```text
# Lead supplies this from the real v5 mint transcript; never guess it.
export AGGREGATE_FLOOR_ARTIFACT='NEEDS-RULING'
```

Old line 540:

```text
path, unresolved floor path, or B10 refusal.
```

Old line 550:

```text
test -f "$AGGREGATE_FLOOR_ARTIFACT"
```

Old lines 576--577:

```text
floor, completed ledger, and adjacent head pin. Expected refusal: any recursive
diff or `cmp` mismatch. The prospective validator resolves every binding
```

Old line 591:

```text
/bin/cp -p "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json"
```

Old line 593:

```text
/usr/bin/cmp -s "$AGGREGATE_FLOOR_ARTIFACT" "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json"
```

## G2-b-only blockers — these do not gate G2-a

1. **OWN-B1 — RESOLVED by G2 ruling R-1.** The current `run_campaign.py` parser cannot select one A/B/B/A
   block from a frozen five-block successor stage.** Its collection parser accepts
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
   from a larger frozen stage. G2 therefore starts the authentic frozen stage
   and terminates that campaign process immediately after block 1's last
   member; Phase D gives the exact signal and post-signal on-disk assertions.

2. **B-SUPPLY — G2-b only: the named measurement checkout must contain the real `_v5`
   supply.** The 2026-08-28 desk census found no successor
   `configs/campaigns/d117_{contrast,floor}_*_v5` directories. Do not substitute
   `_v3`, `_v4`, `_v9`, the historical `df-ph-decode-floor-mint1.json`, or guessed
   bytes. The live gate reopens only at a reviewed head containing all three real
   `_v5` packs and their real freeze/mint supply. No aggregate floor is staged for
   G2-b (ruling 97 R-6a): it is minted inside the transaction from the ALPHA/BETA
   arms and cannot exist yet; the finalizer's member-cover gate
   (`joulewise/analysis_manifest_v3.py:3373`) refuses before the floor is first
   opened (`:3575`).

3. **B3 — RESOLVED by G2 ruling R-5.** `preflight.sh` takes the checkout as its
   one required argument. The documented and only accepted value for this G2
   run is `/Users/edr/JouleWise-measurement-20260813`.

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

5. **B2/B9 — both `_v5` arms and the consuming launch require the step-6
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

No G2-b command is authorized until B-SUPPLY and B2/B9 are cured at a newly
reviewed `_v5` head and B10 passes in the actual execution checkout. These
pack-existence gates do not apply to G2-a, which needs only the pinned Qwen3
models, the existing harness, its own diagnostic runs root, and calibration.

## Remaining ruling

1. **RESOLVED by ruling 97.** The finalizer/refusal commands are executable
   with the absent custody floor path; the member-cover gate refuses before it
   can be opened.

## Timeline

| Phase | Activity | Desk | Quiet machine |
|---|---|---:|---:|
| G2-a | brackets; diagnostic probes at 512/1024/2048/4096; G1 desk assertions | desk tail | first machine evening |
| Desk day | ruled prefill pin; `_v5` pack generation; estate 12 | reviewed desk work | 0 |
| G2-b A-C | real-pack supply, ARM-ABORT rehearsal, fresh T-0 and arm | 14 min | ≥15 min |
| G2-b D | one-block proof, post bracket, ratified physical-ahead STOP | — | measured plan |
| G2-b E-F | boundary-aware provenance and exact scratch finalizer refusal | 5–10 min | 0 |

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
│   ├── floors/                       # empty by ruling 97; no floor bytes are staged for G2-b
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
export REPO="$MEASUREMENT_CHECKOUT"
export PY=/Users/edr/code/JouleWise/.venv/bin/python
export PYTHONPATH="$MEASUREMENT_CHECKOUT"
export SHAKEDOWN_ROOT=/Users/edr/JouleWise-shakedown-g2/2026-08-29
export CUSTODY_ROOT="$SHAKEDOWN_ROOT/custody"
export WINDOW_CUSTODY_ROOT="$CUSTODY_ROOT"
export RUNS_ROOT="$CUSTODY_ROOT/runs"
export BOUND_RUNS_ROOT="$CUSTODY_ROOT/neg8-bound-runs"
export ANALYSIS_ROOT="$SHAKEDOWN_ROOT/analysis"
export CLAIMS_ROOT="$SHAKEDOWN_ROOT/claims"
export SCRATCH_ROOT="$SHAKEDOWN_ROOT/scratch"
export QUARANTINE_ROOT="$SHAKEDOWN_ROOT/quarantine"
export TRANSCRIPT_ROOT="$SHAKEDOWN_ROOT/transcript"
export WINDOW_PLAN_ROOT="$SHAKEDOWN_ROOT/window-plan"
export REHEARSAL_PLAN_ROOT="$SHAKEDOWN_ROOT/rehearsal-window-plan"
export PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
export FLOOR_15_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen3-1p7b_v5"
export FLOOR_7_PACK_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/d117_floor_qwen3-8b_v5"
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
export FROZEN_PLAN="$CUSTODY_ROOT/prospective/calibration_plan.json"
export REF_ROOT="$MEASUREMENT_CHECKOUT/configs/campaigns/window_references"
export CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
export BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
export NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"
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
export SETTLE_S=600
export PRE_CAL_FIDUCIAL_MAX_S=0.032898493715362
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

## G2-a — first machine evening, before the `_v5` pack

G2-a is diagnostic and non-claim. It has its own runs root and campaign log;
neither is a campaign input, a mint input, nor reusable in G2-b. The pack does
not exist yet and no G2-a gate may test `$PACK_ROOT`. Required supply is only
the pinned `mlx-community/Qwen3-1.7B-4bit` and
`mlx-community/Qwen3-8B-4bit` model pair plus the existing MLX/powermetrics
harness. The resolvability probes use the small pinned model; the large pin is
checked now so the pair cannot drift between evenings.

The probe sends raw prompt text with no chat template, so the model's thinking switch is never rendered; the panel file (whose thinking-off policy governs the decode arm the selected rung will feed) and the MLX runtime adapter are bound by file hash in the G2-a input inventory, and the adapter's greedy sampler is its fail-closed default.

```sh
export G2A_ROOT=/Users/edr/JouleWise-shakedown-g2/g2-a-20260830
export G2A_RUNS_ROOT="$G2A_ROOT/runs"
export G2A_TRANSCRIPT_ROOT="$G2A_ROOT/transcript"
export G2A_CONFIG_ROOT="$G2A_ROOT/prefill-probe-configs"
export G2A_LOG="$G2A_RUNS_ROOT/campaign_log.jsonl"
export G2A_OPERATOR_LOG_ROOT="$G2A_ROOT/operator-logs"
export G2A_QUARANTINE_ROOT="$G2A_ROOT/quarantine"
export G2A_WINDOW_PLAN_ROOT="$G2A_ROOT/window-plan"
export G2A_FROZEN_PLAN="$G2A_WINDOW_PLAN_ROOT/calibration_plan.json"
export G2A_IDENTITY_EPOCH_JSON="$G2A_WINDOW_PLAN_ROOT/identity-epoch.json"
export G2A_T1_BINDINGS_JSON="$G2A_WINDOW_PLAN_ROOT/t1-bindings.json"
export G2A_INPUT_INVENTORY="$G2A_WINDOW_PLAN_ROOT/g2a-input-inventory.json"
export G2A_PROMPT_LADDER="$G2A_WINDOW_PLAN_ROOT/prefill-prompt-ladder.json"
export G2A_SUMMARY="$G2A_WINDOW_PLAN_ROOT/d166-prefill-resolvability-summary.json"
export G2A_COUNTS_RECEIPT="$G2A_WINDOW_PLAN_ROOT/d166-prefill-counts-receipt.json"
export G2A_WINDOW_ID=d117-g2a-prefill-probe-20260830
export G2A_BRACKET_SESSION_ID=d117-g2a-prefill-probe-20260830-calibration
export G2A_PRE_ATTEMPT_ID=d117-g2a-prefill-probe-20260830-cal-pre
export G2A_POST_ATTEMPT_ID=d117-g2a-prefill-probe-20260830-cal-post
export G2A_EVIDENCE_ROOT_ID=evidence-d117-g2a-prefill-probe-20260830
/bin/mkdir -p "$G2A_RUNS_ROOT" "$G2A_TRANSCRIPT_ROOT"
test "$G2A_RUNS_ROOT" != "$RUNS_ROOT"
```

The probe configs are ordinary harness configs, not a draft or subset pack. The
producer builds each raw prompt from one fixed seven-token sentence repeated a
whole-number number of times followed by that rung's fixed closing sentence;
it re-tokenizes the completed text and refuses unless its count is exact. The
last 8–11 tokens therefore differ between rungs, as each rung's
`generation_method` names; this is disclosed as a non-effect for this
length-only resolvability probe.
The panel thinking-off policy and the MLX greedy runtime are hash-bound—fixed
by exact file fingerprints—in the G2-a input inventory. Each config carries
the exact direct prompt text, which bypasses the chat template, and the output
budget. Each per-length small-model config carries AT LEAST FIVE members —
the ratified per-rung minimum
(`docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md`
A4); the selection rule requires the count floor in EVERY small-model member,
and a rung with fewer than five members cannot be selected. A parallel
per-length large-model config (any member count ≥1) is probed for the record
only and never gates. Hash and preserve every config before
the bracket opens. Capture pre and post slots through the governed calibration
writer, using the same D-079 screen as the generated chain. Between those
slots run every length, including the ratified 4096 fallback rung:

```sh
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" build-probes \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --small-members 5 --large-members 1
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" bind-window \
  --root "$G2A_ROOT" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY" --power-policy "$POWER_POLICY" \
  --window-id "$G2A_WINDOW_ID" --session-id "$G2A_BRACKET_SESSION_ID" \
  --evidence-root-id "$G2A_EVIDENCE_ROOT_ID"
```

<!-- BEGIN GENERATED: g2a-governed-bracket -->
<!-- GENERATED by scripts/gen_g2_phase_d.py from the pinned runbook reservation and foreground-chain helpers. -->
```zsh
set -euo pipefail

test -f "$G2A_FROZEN_PLAN"
test -f "$G2A_IDENTITY_EPOCH_JSON"
test -f "$G2A_T1_BINDINGS_JSON"
G2A_PLAN_ID="$(/usr/bin/jq -er '.plan_id' "$G2A_FROZEN_PLAN")"
G2A_PLAN_SHA256="$(/usr/bin/shasum -a 256 "$G2A_FROZEN_PLAN" | /usr/bin/awk '{print $1}')"
/bin/mkdir -p "$G2A_RUNS_ROOT/instrument_validation" "$G2A_OPERATOR_LOG_ROOT" "$G2A_TRANSCRIPT_ROOT" "$G2A_QUARANTINE_ROOT"

timestamp() {
  TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ'
}

settle() {
  /bin/sleep "$SETTLE_S"
}

quarantine_stale_lock() {
  local root="$1"
  local lock="$root/campaign.lock"
  [ ! -e "$lock" ] && return 0

  local pid
  pid="$(/usr/bin/sed -n 's/^pid=\([0-9][0-9]*\).*/\1/p' "$lock")"
  if [ -z "$pid" ]; then
    echo "Unreadable campaign lock: $lock" >&2
    return 1
  fi
  if /bin/kill -0 "$pid" 2>/dev/null; then
    echo "Live campaign PID $pid owns $lock" >&2
    return 1
  fi

  /bin/mv "$lock" \
    "$G2A_QUARANTINE_ROOT/$(basename "$root").campaign.lock.$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
}

calibrate_slot() {
  local slot="$1"
  local attempt_id="$2"
  "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
    --allow-live \
    --arm-countdown-s 20 \
    --sleep-display-before-capture \
    --output-root "$G2A_RUNS_ROOT/instrument_validation" \
    --ledger "$CALIBRATION_LEDGER" \
    --head-pin "$LEDGER_HEAD_PIN" \
    --session-id "$G2A_BRACKET_SESSION_ID" \
    --slot "$slot" \
    --attempt-id "$attempt_id" \
    --power-policy "$POWER_POLICY" \
    >> "$G2A_OPERATOR_LOG_ROOT/${slot}-calibration.log" 2>&1
  "$PY" "$REPO/scripts/recover_calibration_ledger.py" session-status \
    --session-id "$G2A_BRACKET_SESSION_ID" \
    --plan "$G2A_FROZEN_PLAN" |
    /usr/bin/jq -er --arg slot "$slot" '.slots[$slot].custody_locator'
}

# D-079 clause 3: pre-flight calibration screen. Refuses an out-of-family
# pre-calibration before any member is collected. Derived from the issued
# acceptance artifact d079_calibration_acceptance_v2_n17_r3 (sha 73f02263...).
# If a successor acceptance issues before arm, regenerate and re-hash this
# chain with it (freeze-plan Q4); bindings and derivation are in §5B.
PRE_CAL_FIDUCIAL_MAX_S=0.032898493715362

screen_pre_calibration() {
  local dir="$1"
  local b

  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' \
    "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    echo "pre-calibration has no fiducial bound: $dir" >&2
    return 1
  fi
  echo "$(timestamp) pre_calibration_fiducial_s=$b" \
    >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
  if (( b > PRE_CAL_FIDUCIAL_MAX_S )); then
    echo "pre-calibration fiducial $b exceeds D-079 screen $PRE_CAL_FIDUCIAL_MAX_S" >&2
    echo "$(timestamp) pre_calibration_screen=failed" \
      >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
    return 1
  fi
  echo "$(timestamp) pre_calibration_screen=passed" \
    >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage() {
  local root="$1"
  local log="$2"
  local config_dir="$3"
  local calibration_dir="$4"
  local label="$5"

  settle
  quarantine_stale_lock "$root"
  echo "$(timestamp) stage_start=$label" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"

  "$PY" "$REPO/scripts/run_campaign.py" "$config_dir" \
    --runs-dir "$root" \
    --log "$log" \
    --campaign-policy "$POLICY" \
    --instrument-calibration-dir "$calibration_dir" \
    --instrument-power-policy "$POWER_POLICY" \
    --arm-quiet-mode \
    --arm-countdown-s 20 \
    --max-failures 1

  echo "$(timestamp) stage_end=$label" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
}

# Authenticate every probe input before ledger readiness or reservation.
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" check \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY"

"$PY" "$REPO/scripts/recover_calibration_ledger.py" readiness \
  --phase pre-reserve \
  --session-id "$G2A_BRACKET_SESSION_ID" \
  --plan "$G2A_FROZEN_PLAN"

"$PY" "$REPO/scripts/reserve_calibration_window_bracket.py" \
  --ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$G2A_BRACKET_SESSION_ID" \
  --window-id "$G2A_WINDOW_ID" \
  --plan-id "$G2A_PLAN_ID" \
  --plan-sha256 "$G2A_PLAN_SHA256" \
  --plan "$G2A_FROZEN_PLAN" \
  --evidence-root-id "$G2A_EVIDENCE_ROOT_ID" \
  --runs-root "$G2A_RUNS_ROOT" \
  --pre-attempt-id "$G2A_PRE_ATTEMPT_ID" \
  --post-attempt-id "$G2A_POST_ATTEMPT_ID" \
  --pre-custody-locator "$G2A_RUNS_ROOT/instrument_validation/$G2A_PRE_ATTEMPT_ID" \
  --post-custody-locator "$G2A_RUNS_ROOT/instrument_validation/$G2A_POST_ATTEMPT_ID" \
  --identity-epoch-json "$G2A_IDENTITY_EPOCH_JSON" \
  --t1-bindings-json "$G2A_T1_BINDINGS_JSON" \
  --execute

cd "$REPO"
echo "$(timestamp) g2a_chain_start" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
# Runbook §5C/§6 settle: operator activity ends before the pre slot.
settle
G2A_PRE_CAL_CUSTODY="$(calibrate_slot pre "$G2A_PRE_ATTEMPT_ID")"
echo "$(timestamp) pre_calibration=$G2A_PRE_CAL_CUSTODY" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
screen_pre_calibration "$G2A_PRE_CAL_CUSTODY"

# G2-a-only delta: the diagnostic probe ladder is not a runbook science stage.
for role in small large; do
for length in 512 1024 2048 4096; do
  config_dir="$G2A_CONFIG_ROOT/$role-p$length"
  test -f "$config_dir/order_manifest.json"
  run_stage "$G2A_RUNS_ROOT" "$G2A_LOG" "$config_dir" \
    "$G2A_PRE_CAL_CUSTODY" "$role-p$length"
done
done

G2A_POST_CAL_CUSTODY="$(calibrate_slot post "$G2A_POST_ATTEMPT_ID")"
echo "$(timestamp) post_calibration=$G2A_POST_CAL_CUSTODY" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
# Ratified terminal boundary: preserve physical-ahead and its exact candidate.
"$PY" "$REPO/scripts/recover_calibration_ledger.py" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  session-status --session-id "$G2A_BRACKET_SESSION_ID" --plan "$G2A_FROZEN_PLAN" \
  > "$G2A_TRANSCRIPT_ROOT/g2a-post-bracket-terminal-boundary.json"
/usr/bin/jq -e '
  .session_state == "finalized"
  and .pin_relation == "physical_ahead"
  and .refusal_code == "calibration_ledger_head_mismatch"
  and .terminal_head_pin_candidate != null
' "$G2A_TRANSCRIPT_ROOT/g2a-post-bracket-terminal-boundary.json"
echo "$(timestamp) g2a_boundary_stopped=physical_ahead" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"
```
<!-- END GENERATED: g2a-governed-bracket -->

Record every authenticated overlap count and the complete four-row summary.
The summarizer reads `in_window_sample_count`, the number of power-sample
intervals that overlap the prefill phase, and records that field verbatim in
the counts receipt. Its four-row summary sets `all_small_count_ge_5` to true
only when every one of the small-model members at that rung has at least five
overlapping samples.
The selection rule is evaluated later at the desk; G2-a does not cut a pack:

```sh
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/summarize_g2a_prefill_probe.py" \
  --config-root "$G2A_CONFIG_ROOT" \
  --input-inventory "$G2A_INPUT_INVENTORY" \
  --runs-root "$G2A_RUNS_ROOT" \
  --counts-output "$G2A_COUNTS_RECEIPT" \
  --summary-output "$G2A_SUMMARY"
# Ratified gate: four rungs, >=5 small-model members each; the count floor is
# in_window_sample_count >= 5 per small member, NEVER count >= 8.
/usr/bin/jq -e 'length == 4 and map(.length) == [512,1024,2048,4096]
  and all(.small_members >= 5)' \
  "$G2A_SUMMARY"
```

After the post slot, record the terminal head candidate and stop with the
tracked pin unchanged. At the desk, run the G1 assertions (the estate-11
pre-shakedown checks in
`docs/process_traces/2026-08-27-t26/s11-collector-manifest-id/estate11-assertions.md`)
at the reviewed head. Also run W-11, the regenerated-manifest
finalize/claim-edge refusal check (`python3 -m unittest
tests.test_check_window_provenance`); D-157, the condition-family contract
mutation refusal (`docs/decision_log.md` D-157); and S11/F-5, the reusable
estate-11 and finalizer-layout checker in that same test module. Any red
assertion blocks the desk-day pin and `_v5` generation.

The preparation budget is approximately 2.5–3 hours against the available
2–4 hour evening: eight 600-second settles plus one pre-calibration settle are
about 90 minutes; 24 members at the historical approximately 148-second
cadence are about 59 minutes (the cadence is recorded by the `run_stage`
command above); and two 59-pulse calibrations fill the remaining time. This is
a planning disclosure, not a mechanical admission guard.

## Desk day — reviewed pin, pack generation, estate 12

Review G2-a’s physical-ahead candidate, run the runbook’s guarded
`advance-head-pin` with its exact sequence/digest and operator attestation,
commit the pin, and require a clean reviewed head. Apply the ruled shortest
qualifying-length selection to the four-row G2-a record (4096 remains evidence
and is the ruled collection length when no rung qualifies). Materialize and
hash the decision before any `_v5` input is authored:

```sh
export G2A_SELECTION_RECORD="$G2A_WINDOW_PLAN_ROOT/d166-prefill-selection.json"
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/select_g2a_prefill_length.py" \
  --summary "$G2A_SUMMARY" \
  --output "$G2A_SELECTION_RECORD"
export G2A_SELECTION_RECORD_SHA256="$(/usr/bin/shasum -a 256 \
  "$G2A_SELECTION_RECORD" | /usr/bin/awk '{print $1}')"
/usr/bin/printf '%s\n' "$G2A_SELECTION_RECORD_SHA256" \
  > "$G2A_SELECTION_RECORD.sha256"
/usr/bin/jq -e '
  (.status == "selected"
    and .selected_prefill_tokens == .collection_prefill_tokens)
  or (.status == "refused"
    and .selected_prefill_tokens == null
    and .collection_prefill_tokens == 4096
    and .refusal.fallback_action == "collect_at_4096")
' "$G2A_SELECTION_RECORD"
```

On `selected`, pin `selected_prefill_tokens`. On the ruled no-clear refusal,
pin `collection_prefill_tokens=4096` and carry the record’s split reporting:
counts below 3 retain `not_resolvable_sample_count`; resolvable counts 3–4 use
`below the pre-registered count floor of 5` and disclose the reducer result.
Issue the prompt pin only after that decision. The issuer writes one bundle in
`$G2A_WINDOW_PLAN_ROOT`: the pin plus verbatim copies of the selection record
and prompt ladder, with every copy's SHA-256 (a file fingerprint) in the pin.

```sh
export G2A_PROMPT_PIN="$G2A_WINDOW_PLAN_ROOT/prefill-prompt-pin.json"
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/issue_g2a_prefill_prompt_pin.py" \
  --selection-record "$G2A_SELECTION_RECORD" \
  --summary "$G2A_SUMMARY" \
  --prompt-ladder "$G2A_PROMPT_LADDER" \
  --input-inventory "$G2A_INPUT_INVENTORY" \
  --counts-receipt "$G2A_COUNTS_RECEIPT" \
  --ruling-trace "$REPO/docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md" \
  --output "$G2A_PROMPT_PIN"
/bin/mkdir -p "$REPO/configs/campaigns/d117_contrast_v5/prefill_pin"
/bin/cp "$G2A_PROMPT_PIN" "$G2A_SELECTION_RECORD" "$G2A_PROMPT_LADDER" \
  "$REPO/configs/campaigns/d117_contrast_v5/prefill_pin/"
```

`V5-DESK-DAY-01` is the desk-day queue row that consumes this copied bundle.
The existing Qwen3 `_v5` contrast generator is invoked exactly as follows:

```sh
export G2A_SELECTED_PREFILL_LENGTH="$(/usr/bin/jq -er \
  '.collection_prefill_tokens' "$G2A_SELECTION_RECORD")"
cd "$REPO"
PYTHONPATH="$REPO" "$PY" \
  configs/campaigns/d117_contrast_v5/generate_configs.py \
  --output-root "$REPO" \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$G2A_SELECTED_PREFILL_LENGTH" \
  --prefill-prompt-pin \
    configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json
```

This command emits the contrast pack. At this reviewed head there is no Qwen3
`_v5` `generate_configs.py` for either floor-pack root named at the top of this
runsheet, so the desk day must remain blocked rather than substituting either
retired Qwen2.5 floor generator or a non-executable invented command.
Then, after both floor-pack producers exist:

1. pin that selected prefill length in the `_v5` inputs;
2. generate all three real `_v5` packs and their exact freeze/mint supply; and
3. run estate 12 through reviewed freeze, re-attestation, and green receipts.

No G2-b T-0 receipt may predate this refreshed reviewed head.

## G2-b — evening before the transaction, real-pack one-block proof

The pack-existence gate begins here, and nowhere in G2-a. G2-b uses the real
estate-12 `_v5` pack, its own non-claim runs root, the one-block proof, the
ratified post-bracket physical-ahead boundary, and exact finalize-refusal
equality.

### Phase A — desk preflight

### A1 — fixed supply and checkout inspection (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <2 min. Expected artifact: transcript
only. Expected refusal: any absent pack/file, non-main head, dirty governed
path, or B10 refusal.

```sh
cd "$MEASUREMENT_CHECKOUT"
test "$(git branch --show-current)" = main
test -f "$PACK_ROOT/analysis_manifest_v3.json"
test -f "$PACK_ROOT/plan_tree.json"
test -f "$PACK_ROOT/calibration_plan.json"
test -f "$FLOOR_15_PACK_ROOT/plan_tree.json"
test -f "$FLOOR_7_PACK_ROOT/plan_tree.json"
test -f "$CALIBRATION_LEDGER"
test -f "$LEDGER_HEAD_PIN"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_family_publication_v4.json.sha256"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json"
test -f "$FAMILY_PUBLICATION_SOURCE_ROOT/d117_step6_confirmation_table_v4.json.sha256"
test "$EXPECTED_CONFIRMATION_DIGEST" != LEAD-SUPPLIED-FROZEN-INPUT
export PLAN_ID="$(/usr/bin/jq -er '.plan.plan_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export PLAN_SHA256="$(/usr/bin/jq -er '.plan.sha256' "$PACK_ROOT/analysis_manifest_v3.json")"
export EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.evidence_root_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export PACK_MANIFEST_ID="$(/usr/bin/jq -er '.manifest_id' "$PACK_ROOT/analysis_manifest_v3.json")"
```

Execute the required-argument preflight and preserve its complete output; never
cherry-pick only the PASS text:

```sh
"$MEASUREMENT_CHECKOUT/docs/process_traces/2026-08-28-live-smoke/preflight.sh" \
  /Users/edr/JouleWise-measurement-20260813
```

### A2 — stage the complete finalizer input tree in custody (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <2 min before launch, then <1 min after
the post bracket. Expected artifacts: a byte-identical complete pack subtree,
an empty floors directory, completed ledger, and adjacent head pin. Expected
refusal: any recursive diff or `cmp` mismatch. The prospective validator resolves every binding
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
/usr/bin/diff -r "$PACK_ROOT" "$CUSTODY_ROOT/prospective"
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
   the `_v5` supply must be cut before it can be made exact.

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
coordinate; the preserved terminal boundary is its G2-b occurrence coordinate. H5 calls
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
artifacts: launch consumption, start/settle lifecycle receipts, two
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
template, not a second operator invocation. The unchanged portions are
mechanically checked against the runbook chain: start lifecycle, settle, pre
bracket, D-079 screening, bound corpus and derivation on
`$BOUND_RUNS_ROOT`, stage-list semantics, start triplet, the ruled termination
inside the first before-midpoint stage, midpoint, end triplet, post bracket,
and the ratified stop boundary. The source anchors at this head are `window_runbook.md:1516`
(start), `:1541` (bound path), `:1636` (per-stage settle), `:1653`
(stage-list function), `:1663` (chain start), and `:1693-1727` (screen through
the source completion tail). `scripts/gen_g2_phase_d.py` emits this complete
region from those bytes and applies only the ruled G2-b one-block and stop
deltas; the test regenerates and byte-compares it. Every flag below was
confirmed from the current CLI `--help`.

<!-- BEGIN GENERATED: g2-phase-d-governed-chain -->
<!-- GENERATED by scripts/gen_g2_phase_d.py from the pinned runbook chain. -->
```zsh
#!/bin/zsh
set -euo pipefail

WINDOW_PLAN_ROOT="$1"
source "$WINDOW_PLAN_ROOT/window.env"
: "${ARM_RECEIPT:?E-10 export step must export ARM_RECEIPT}"
: "${LAUNCH_MANIFEST:?E-10 export step must export LAUNCH_MANIFEST}"

REPO=/Users/edr/JouleWise-measurement-20260813
PY="$REPO/.venv/bin/python"

# First executable action: consume the inherited one-use FD and mint start
# custody. Direct shell invocation has no FD 198 and refuses
# launch_handoff_invalid before settle or collection.
#
# INCOMPLETE, BY DECISION: this call performs the full consumption replay, so
# it also needs --step6-confirmation-table and --expected-confirmation-digest
# and refuses without them. It cannot inherit them from E-10's command line
# (execve hands this process the manifest's argv, not E-10's), and window.env
# cannot hold them (exact-key allowlist). The exported environment DOES cross
# execve and is the one remaining candidate channel. See the OPEN DEFECT note
# above this chain; choosing the confirmation-pair supply line is a magistrate
# ruling, not something to improvise at the bench.
"$PY" "$REPO/scripts/launch_window.py" \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --lifecycle-event start \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"

POLICY="$REPO/configs/campaign_policies/quiet_mac_p2_production.json"
REF_ROOT="$REPO/configs/campaigns/window_references"
BOUND_CONFIG_ROOT="$REPO/configs/campaigns/neg8_reference_corpus"
BOUND_MANIFEST="$BOUND_CONFIG_ROOT/derivation/settled_corpus.json"
CLAIM_LOG="$RUNS_ROOT/campaign_log.jsonl"
BOUND_LOG="$BOUND_RUNS_ROOT/campaign_log.jsonl"
NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"
OPERATOR_LOG_ROOT="$WINDOW_CUSTODY_ROOT/operator_logs"

mkdir -p \
  "$RUNS_ROOT/instrument_validation" \
  "$BOUND_RUNS_ROOT" \
  "$WINDOW_CUSTODY_ROOT" \
  "$OPERATOR_LOG_ROOT" \
  "$QUARANTINE_ROOT"

timestamp() {
  TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ'
}

settle() {
  /bin/sleep "$SETTLE_S"
}

quarantine_stale_lock() {
  local root="$1"
  local lock="$root/campaign.lock"
  [ ! -e "$lock" ] && return 0

  local pid
  pid="$(/usr/bin/sed -n 's/^pid=\([0-9][0-9]*\).*/\1/p' "$lock")"
  if [ -z "$pid" ]; then
    echo "Unreadable campaign lock: $lock" >&2
    return 1
  fi
  if /bin/kill -0 "$pid" 2>/dev/null; then
    echo "Live campaign PID $pid owns $lock" >&2
    return 1
  fi

  /bin/mv "$lock" \
    "$QUARANTINE_ROOT/$(basename "$root").campaign.lock.$(TZ=UTC date '+%Y%m%dT%H%M%SZ')"
}

calibrate_slot() {
  local slot="$1"
  local attempt_id="$2"
  "$PY" "$REPO/scripts/validate_powermetrics_fiducial.py" \
    --allow-live \
    --arm-countdown-s 20 \
    --sleep-display-before-capture \
    --output-root "$RUNS_ROOT/instrument_validation" \
    --ledger "$CALIBRATION_LEDGER" \
    --head-pin "$LEDGER_HEAD_PIN" \
    --session-id "$BRACKET_SESSION_ID" \
    --slot "$slot" \
    --attempt-id "$attempt_id" \
    --power-policy "$POWER_POLICY" \
    >> "$OPERATOR_LOG_ROOT/${slot}-calibration.log" 2>&1
  "$PY" "$REPO/scripts/recover_calibration_ledger.py" session-status \
    --session-id "$BRACKET_SESSION_ID" \
    --plan "$FROZEN_PLAN" |
    /usr/bin/jq -er --arg slot "$slot" '.slots[$slot].custody_locator'
}

# D-079 clause 3: pre-flight calibration screen. Refuses an out-of-family
# pre-calibration before any member is collected. Derived from the issued
# acceptance artifact d079_calibration_acceptance_v2_n17_r3 (sha 73f02263...).
# If a successor acceptance issues before arm, regenerate and re-hash this
# chain with it (freeze-plan Q4); bindings and derivation are in §5B.
PRE_CAL_FIDUCIAL_MAX_S=0.032898493715362

screen_pre_calibration() {
  local dir="$1"
  local b

  b="$(/usr/bin/jq -r '.b_fiducial_s // empty' \
    "$dir/instrument_evidence.json")"
  if [ -z "$b" ]; then
    echo "pre-calibration has no fiducial bound: $dir" >&2
    return 1
  fi
  echo "$(timestamp) pre_calibration_fiducial_s=$b" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
  if (( b > PRE_CAL_FIDUCIAL_MAX_S )); then
    echo "pre-calibration fiducial $b exceeds D-079 screen $PRE_CAL_FIDUCIAL_MAX_S" >&2
    echo "$(timestamp) pre_calibration_screen=failed" \
      >> "$OPERATOR_LOG_ROOT/window-chain.log"
    return 1
  fi
  echo "$(timestamp) pre_calibration_screen=passed" \
    >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage() {
  local root="$1"
  local log="$2"
  local config_dir="$3"
  local calibration_dir="$4"
  local label="$5"

  settle
  quarantine_stale_lock "$root"
  echo "$(timestamp) stage_start=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"

  "$PY" "$REPO/scripts/run_campaign.py" "$config_dir" \
    --runs-dir "$root" \
    --log "$log" \
    --campaign-policy "$POLICY" \
    --instrument-calibration-dir "$calibration_dir" \
    --instrument-power-policy "$POWER_POLICY" \
    --arm-quiet-mode \
    --arm-countdown-s 20 \
    --max-failures 1

  echo "$(timestamp) stage_end=$label" >> "$OPERATOR_LOG_ROOT/window-chain.log"
}

run_stage_list() {
  local list="$1"
  local stage
  while IFS= read -r stage; do
    [ -z "$stage" ] && continue
    [[ "$stage" = \#* ]] && continue
    run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REPO/$stage" "$PRE_CAL_CUSTODY" "$stage"
  done < "$list"
}

cd "$REPO"
echo "$(timestamp) chain_start" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# Final settle is chain-owned (D-117 §5C): operator activity ends at launch,
# and §1's post-activity settle happens here, before the pre-calibration.
settle
# No confirmation pair here, and none at completion below, even once the open
# defect above is ruled. Settle and completion do replay the consumed arm --
# every lifecycle event does -- but they replay it with arm semantics switched
# off (replay_arm_semantics=False), and the table check lives inside those
# semantics. Only the start event runs the full replay that reaches it. Their
# omission is deliberate, not an oversight.
"$PY" "$REPO/scripts/launch_window.py" \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --lifecycle-event settle
# Settle publishes BOTH fixed locators, each with its GNU SHA-256 sidecar:
#   $RUNS_ROOT/.joulewise-launch-lineage.json
#   $BOUND_RUNS_ROOT/.joulewise-launch-lineage.json
# Publication is canonical, no-clobber, file-fsynced, and directory-fsynced.
# Any primary/sidecar/root failure burns this attempt and set -e stops here,
# before pre-calibration or collection; never repair a partial publication.
echo "$(timestamp) launch_settle_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"

PRE_CAL_CUSTODY="$(calibrate_slot pre "$PRE_ATTEMPT_ID")"
echo "$(timestamp) pre_calibration=$PRE_CAL_CUSTODY" >> "$OPERATOR_LOG_ROOT/window-chain.log"

# Abort before member 1 if the pre-calibration is out of family (§5B).
screen_pre_calibration "$PRE_CAL_CUSTODY"

# The reference corpus and bound are minted inside this same quiet window.
run_stage "$BOUND_RUNS_ROOT" "$BOUND_LOG" "$BOUND_CONFIG_ROOT" "$PRE_CAL_CUSTODY" \
  neg8-bound-corpus

"$PY" "$REPO/scripts/run_campaign.py" \
  --derive-neg8-drift-bound "$BOUND_MANIFEST" \
  --neg8-drift-bound-output "$NEG8_DRIFT_BOUND" \
  --runs-dir "$BOUND_RUNS_ROOT" \
  >> "$OPERATOR_LOG_ROOT/bound-mint.log" 2>&1
echo "$(timestamp) neg8_bound=$NEG8_DRIFT_BOUND" >> "$OPERATOR_LOG_ROOT/window-chain.log"

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/start_triplet" "$PRE_CAL_CUSTODY" \
  start-reference-triplet

# G2-b delta: stop the authentic first stage after block 1, then preserve
# the governed chain's post-science bracket path.  The second-terminal
# signal card below supplies SIGINT immediately after b01 A2 succeeds.
set +e
run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"
SCIENCE_RC=$?
set -e
test "$SCIENCE_RC" = 130

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/midpoint" "$PRE_CAL_CUSTODY" \
  midpoint-reference

# G2-b deliberately collects no after-midpoint science stage.

run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REF_ROOT/end_triplet" "$PRE_CAL_CUSTODY" \
  end-reference-triplet

POST_CAL_CUSTODY="$(calibrate_slot post "$POST_ATTEMPT_ID")"
echo "$(timestamp) post_calibration=$POST_CAL_CUSTODY" >> "$OPERATOR_LOG_ROOT/window-chain.log"
# R-6 ratified boundary: post finalization emitted the physical terminal
# candidate.  Record it and STOP; do not advance the tracked pin and do
# not emit launch completion during this night.
"$PY" "$REPO/scripts/recover_calibration_ledger.py" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  session-status --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN" \
  > "$TRANSCRIPT_ROOT/post-bracket-terminal-boundary.json"
/usr/bin/jq -e '
  .session_state == "finalized"
  and .pin_relation == "physical_ahead"
  and .refusal_code == "calibration_ledger_head_mismatch"
  and .terminal_head_pin_candidate != null
' "$TRANSCRIPT_ROOT/post-bracket-terminal-boundary.json"
echo "$(timestamp) g2_boundary_stopped=physical_ahead" >> "$OPERATOR_LOG_ROOT/window-chain.log"
```
<!-- END GENERATED: g2-phase-d-governed-chain -->

**TERMINATE HERE — second local terminal, after block 1 A2 succeeds:**

```sh
SCIENCE_PID="$(/usr/bin/sed -n 's/^pid=\([0-9][0-9]*\).*/\1/p' "$RUNS_ROOT/campaign.lock")"
test -n "$SCIENCE_PID"
/bin/kill -INT "$SCIENCE_PID"
```

The expected state when the signal completes is exact: the four block-1 bundle
directories named by the SHA-bound index-1 stage order manifest each contain
`summary_metrics.json`; no other frozen science-member directory exists;
`campaign.lock` is absent because Python unwound through its `finally`; the
partial campaign manifest retains the four completed members; and no midpoint,
post-calibration, completion, binding, verdict, finalized manifest, or claim
artifact exists yet. The primary chain checks `SCIENCE_RC=130`, then continues
with midpoint, end reference, and the post bracket. It then records the
physical-ahead terminal candidate and STOPS: no launch completion, pin advance,
binding, verdict, finalize attempt, or claim occurs in the night chain. Any
fifth science bundle, partial bundle, retained lock, different rc, absent
member, missing candidate, or non-mismatch boundary record is ABORT.

## G2-b desk reviewed-refresh after the boundary

The preserved boundary record must show `session_state=finalized`,
`pin_relation=physical_ahead`,
`refusal_code=calibration_ledger_head_mismatch`, and a non-null
`terminal_head_pin_candidate`. Review that candidate, then use the existing
guarded desk advance; never edit the pin by hand:

```sh
export TERMINAL_BOUNDARY_RECORD="$TRANSCRIPT_ROOT/post-bracket-terminal-boundary.json"
export CANDIDATE_SEQUENCE="$(/usr/bin/jq -er '.terminal_head_pin_candidate.sequence' "$TERMINAL_BOUNDARY_RECORD")"
export CANDIDATE_DIGEST="$(/usr/bin/jq -er '.terminal_head_pin_candidate.head_digest' "$TERMINAL_BOUNDARY_RECORD")"
"$PY" scripts/recover_calibration_ledger.py \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  advance-head-pin --session-id "$BRACKET_SESSION_ID" \
  --expected-sequence "$CANDIDATE_SEQUENCE" \
  --expected-digest "$CANDIDATE_DIGEST" \
  --operator-identity "$OPERATOR_IDENTITY" \
  --attestation-reason "reviewed exact G2-b terminal candidate" --execute
```

The lead reviews and commits that pin, requires a clean reviewed head,
regenerates readiness evidence, re-freezes, and re-attests. Restage the now
exact ledger/pin pair into custody and repeat all A2 byte comparisons before
continuing. No later arm may consume the pre-refresh freeze.

## Phase E — postcollection binding before verdict

### E1 — build the binding from the completed staged ledger pair (MAGISTRATE)

CWD: `$MEASUREMENT_CHECKOUT`. Timing: <1 min. Expected artifacts: the completed
ledger and refreshed adjacent head re-staged and byte-verified after the desk
cycle, plus
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

The PASS line carries no information about the floor; this pre-assertion is
the transcript's proof that no floor bytes were staged.

```sh
if test -d "$CUSTODY_ROOT/floors" \
   && test ! -e "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json" \
   && test -z "$(/bin/ls -A "$CUSTODY_ROOT/floors")"; then
  echo "FLOORS-EMPTY OK"
else
  echo "STOP: floors/ missing or non-empty: $(/bin/ls -lA "$CUSTODY_ROOT/floors" 2>&1)"; false
fi
```

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
  --aggregate-floor-artifact "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json" \
  --output-dir "$CUSTODY_ROOT"
```

The PASS line carries no information about the floor; this post-assertion is
the transcript's proof that no floor bytes were staged.

```sh
if test -d "$CUSTODY_ROOT/floors" \
   && test ! -e "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json" \
   && test -z "$(/bin/ls -A "$CUSTODY_ROOT/floors")"; then
  echo "FLOORS-EMPTY OK"
else
  echo "STOP: floors/ missing or non-empty: $(/bin/ls -lA "$CUSTODY_ROOT/floors" 2>&1)"; false
fi
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

An observed singleton of `analysis_finalization_attachment_missing` is a STOP
and a ruling, never "stage a floor and rerun". The member-cover singleton
proves prospective-manifest validation, verdict schema/status/basis, and the
present members' config/metadata/summary hashes and identity paths; it does not
prove bracket-byte or ledger-head authentication. The finalizer's bracket and
ledger legs (`joulewise/analysis_manifest_v3.py:3380-3487`) run after member
cover and are validated on the night by the reusable G3 provenance block
(`check_window_provenance.py --bracket-binding … --calibration-ledger …
--head-pin …`, executed at F1), outside the finalizer.

`analyze-claims` is copy-safe with respect to the source trees: it reads the
manifest/runs/floor inputs and writes only `--output`
(`joulewise/cli.py:2003-2019`). Finalize is not copy-safe, hence the mandatory
scratch copy above. A G2 partial collection must not be finalized in real
custody and must not produce a claim artifact.

## Phase G — post-run record and preservation

The superseded in-night pin-advance section is deleted. The only pin advance
is the ratified desk reviewed-refresh cycle between the recorded boundary and
Phase E; Phase G never advances or edits the pin.

### G1 — post-run assertions (MAGISTRATE)

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

Return: reviewed head, both arm receipt ids and dispositions, terminal boundary
record, bracket session/pre/post ids, ledger pre/post pin coordinates,
exact runs root, bundle roster, campaign-manifest roster, binding/verdict
digests, G3 transcript, exact observed refusal set, dirty-tree roster, and all
blocker and remaining-ruling dispositions. Do not finalize, claim, commit, push, seal,
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
CHECK_BOUNDARY_ARGS=(--terminal-boundary-record "$TERMINAL_BOUNDARY_RECORD")
if [ -n "${FINALIZED_MANIFEST:-}" ]; then
  CHECK_FINALIZED_ARGS=(--finalized-manifest "$FINALIZED_MANIFEST")
  CHECK_BOUNDARY_ARGS=()
fi
"$PY" scripts/check_window_provenance.py \
  --runs-root "$RUNS_ROOT" \
  --pack-root "$PACK_ROOT" \
  --custody-root "$CUSTODY_ROOT" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  "${CHECK_BOUNDARY_ARGS[@]}" \
  "${CHECK_FINALIZED_ARGS[@]}" \
  > "$TRANSCRIPT_ROOT/window-provenance.txt"
/bin/cat "$TRANSCRIPT_ROOT/window-provenance.txt"
```
