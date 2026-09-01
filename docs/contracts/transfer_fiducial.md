# TRANSFER-FIDUCIAL-01 inserted-gap diagnostic contract

Status: implemented but parked behind the D-167 `_v5` chain, including the
final `V5-NIGHTLY-G3-01` pass. Live execution is `[QUIET-MAC]`, meaning a
measurement window with no agent process competing for the machine. It is
lead/Ed-owned and must not occur while an agent session is active. This
protocol is diagnostic and non-claim-bearing: it can expose a timing problem,
but it mints no floor, licenses no scientific claim, and changes no `_v5`
artifact.

## Purpose and fixed v1 regime

The arm tests whether the existing powermetrics pulse timing bound transfers
to the prefill/decode load regime. V1 is one separately verdictable stratum:

- Qwen2.5-1.5B-Instruct-4bit, revision
  `8b403126fc14f14cfc99bb4cfa72ecbc129ea677`;
- M3 Max, MLX runtime, powermetrics telemetry, int4;
- 4,096 prompt tokens, 512 output tokens, one repetition;
- one 0.5 second inserted gap and ten planned runs;
- at least 0.8 seconds in each active window and 6.0 seconds of post-window
  sampling dwell (the fit requires at least 4.5 seconds after margins).

No 7B arm exists in v1 because no evidenced prompt sizing point establishes
its 0.8-second prefill minimum. The plan schema is stratum-shaped so a future
ruled arm can receive its own ten-run verdict; observations across strata are
never pooled.

## V2 Qwen3-small successor regime

`transfer_fiducial_v1/` is retained historical evidence. It is not the
workload for the `_v5` campaign. The successor generator at
`configs/diagnostics/transfer_fiducial_v2/generate_plan.py` creates one
separately verdictable Qwen3-small stratum (one fixed model and workload
group) only after it receives all three permanent inputs:

- the four-row G2-a summary emitted by
  `scripts/summarize_g2a_prefill_probe.py`;
- the successful G2-a selection record emitted by
  `scripts/select_g2a_prefill_length.py`; and
- the hash-bound G2-a prompt-pin file, a JSON file containing the exact prompt
  and its SHA-256 fingerprints, emitted by
  `scripts/issue_g2a_prefill_prompt_pin.py` for that record's selected rung.

The record selects one rung from 512, 1,024, 2,048, or 4,096 prompt tokens.
The record itself has no prompt text or token identifiers, so the generator
also requires the prompt pin. It hashes the exact summary bytes and requires
that value to equal the selection record's `summary_sha256`. It refuses a
missing, refused, malformed, or unauthenticated selection record, a rung
outside that four-value ladder, or any summary mismatch. It then requires the
pin's `g2a_record_sha256` and its `record_id` (`sha256:` followed by that
digest) to name the supplied selection bytes, and requires the recorded path
to match the supplied record. The generator's current check of
`generation_method` is a regex SHAPE check only: it requires the form
`N x 'repeated sentence' + 'closing sentence' under tokenizer
sha256:DIGEST`, but does not yet prove the ruling-39b construction. The
ruling-39b construction check lands in the post-probe-merge round. Finally,
the generator loads the model mirror named by
`configs/model_panels/qwen3_4bit.json` and passes `prompt_text` through the
same raw-text encode function used by the MLX runtime, with special tokens
enabled. The resulting integer token identifiers must exactly equal
`prompt_token_ids`. Thus separately self-hashed text and identifiers cannot
pose as one runtime workload.

The generator imports the Qwen3-small model identity from the `_v5` campaign
generator; this carries the model revision, tokenizer-file digest, and
chat-template digest instead of copying those values into a second source of
truth.

### Sequencing note

Pin-to-ladder binding from ruling 39b (the loader check that compares a pin
field by field with the selected ladder rung) lands in the post-probe-merge
round. This is a sequencing deferral, not a threat-model deferral: the 39b
loader is absent on this branch, no data exists, and the merge is held. The
ladder is the pre-registration record, so this binding check sits inside
D-161's fail-closed carve-out. Run-time re-tokenization remains because it is
the only fence across the two tokenizer loader paths: the issuer uses
`transformers.AutoTokenizer`, while the generator and runtime use
`mlx_lm.load`. The post-merge round's `WRITE_SCOPE` must include the plan
generator at `configs/diagnostics/transfer_fiducial_v2/generate_plan.py` and
`tests/test_transfer_fiducial_v2_plan.py`, because the 39b loader signature
changes.

V2 uses plan schema `joulewise.transfer_fiducial_plan.v2` and diagnostic kind
`transfer_fiducial_v2`; V1 retains its original schema and kind. V2 fixes 512
output tokens. It emits `plan.json` and exactly ten configuration
files named `tf-q3s-p<RUNG>-o512-rNN.json`. The plan records the selected
prompt's text digest and token-identifier digest, as well as the selection and
prompt-pin digests. A digest is a SHA-256 value: a 64-character fingerprint of
the exact bytes. `--check` regenerates into a temporary directory and refuses
if its plan or any of its ten configuration files differs byte-for-byte from
the committed set.

## Runtime boundary and zero-delta rule

`WorkloadProfile.transfer_fiducial_gap_s` is an additive, omission-serialized
optional in config schema `0.1`. Absence preserves normalized config bytes and
the legacy MLX event/call path. V1 accepts only finite value `0.5`, a
single-prompt workload, `repetitions == 1`, `output_tokens >= 1`, MLX runtime,
and powermetrics telemetry. Other runtimes refuse as `unsupported_workload`;
they never ignore the flag.

The measured boundary is
`boundary_semantics = first_yield_one_step_queued`. At the first `mlx_lm`
stream yield, one decode step is already queued. The flagged order is:

1. take `gap_start_stamp`;
2. emit `phase_end/prefill` and `fiducial_gap_start` at exactly that epoch;
3. call `mlx.core.synchronize()`;
4. call the injected clock's `sleep(0.5)` exactly once;
5. take `gap_end_stamp`;
6. emit `fiducial_gap_end` and `phase_start/decode` at exactly that epoch;
7. continue the unchanged generation loop.

The flagged outer `phase_start/prefill` and `phase_end/decode` events also
carry complete `clock_stamp` metadata. The gap lies in neither phase span.
Queued-work drain, sleep scheduling, and redispatch latency remain inside the
observed residual and are never subtracted. This is an inserted first-yield
transport fiducial, not a computation-exact natural phase boundary.

## Structural classification and claim lock

A bundle is transfer-diagnostic when either its config has a non-null
`transfer_fiducial_gap_s` or its events contain a `fiducial_gap_start` or
`fiducial_gap_end`. Config/event disagreement remains diagnostic and adds
`transfer_fiducial_class_inconsistent`. Every classified bundle receives the
LOCK reason `transfer_fiducial_claim_ineligible`; the inconsistency reason is
CONTRACT. A claim fence (a guard that prevents diagnostic evidence from
minting or supporting a claim) is active at each of the four consumers that
can mint or claim:

- `joulewise/analysis_engine/inputs.py:_read_bundle` labels classified input
  with the canonical refusal reason;
- `joulewise/floor_extraction.py:_evaluate_member` refuses a classified floor
  member;
- `scripts/mint_floor_artifact.py:_strict_bundle` refuses a classified bundle
  before minting; and
- `joulewise/whole_window.py:AuthenticatedConsumptionSession._prepare`
  refuses a whole-window set containing any classified bundle.

The reducer-layer defense-in-depth fence is deferred because the issued D079
calibration acceptance byte-hash-pins `joulewise/reduce.py`. Adding that fence
requires the governed post-V4 re-freeze of the D079 pin; issued pins must not
be hand-edited. Reduction therefore remains available so the diagnostic fit
can consume phase spans. The reducer's own outputs for a diagnostic bundle
are labelled non-claim-bearing by every downstream consumer listed above.
The diagnostic report keeps the bundle visible under the banner “DIAGNOSTIC
— non-claim-bearing (transfer fiducial).”

## Fit and statistic

The fitter re-anchors `raw/powermetrics.plist` from the bundle's stored clock
anchor and creates exactly two positive `CommandedPulse` values:

- `[phase_start/prefill, fiducial_gap_start]`;
- `[fiducial_gap_end, phase_end/decode]`.

Every endpoint uncertainty is `clock_stamp_half_width_s(stamp)`. The trace is
cropped at the last interval whose start is at or before
`prefill_start - FIT_HALF_RANGE_S`, retaining all later intervals. The fitter
then calls the imported, frozen
`powermetrics_fiducial.detect_pulses(intervals, pulses,
trace_anchor_bound_s=run_bound)` without changed constants or copied logic.

The run is inconclusive unless both active durations are at least 0.8 seconds,
the post-margin outside baseline is at least 4.5 seconds, all pulse edges have
coverage, both pulses are detected, the spurious plateau count is zero, and
all residual intervals are finite. The target edges are pulse 0 offset
(falling gap edge) and pulse 1 onset (rising gap edge); all other fit fields are
retained as nuisance diagnostics.

For each target edge:

```text
radius = max(abs(residual_lower_s), abs(residual_upper_s))
         + effective_clock_anchor_bound_s for that run
```

`residual_transfer_s` is the maximum over all 20 radii. Median and
nearest-rank p95 are diagnostic only and cannot decide the verdict.

## Calibration binding and verdict

The only comparison bound is
`<pulse-calibration-dir>/instrument_evidence.json#/b_fiducial_s`. The capture
records and verifies the evidence SHA-256, pulse protocol ID, estimator
revision, power policy, hardware model, OS build, and each run's attached
calibration identity. It also records the exact calibration path, capture
time/validation ID, `b_pulse_s`, estimator source SHA-256, config hashes,
bundle IDs, source commit, complete gap/boundary events and ClockStamps,
commanded and observed gap durations, anchors, constructed pulses, every fit
field, target radii, and pipeline caveat.

The only verdicts are:

- `supported`: every gate passes and `residual_transfer_s <= b_pulse_s`;
- `exceeds_bound`: every gate passes and the residual is larger;
- `inconclusive`: any planned run, binding, anchor, fit, or completeness gate
  fails.

`excess_s` is `max(0, residual_transfer_s - b_pulse_s)`. Failed runs are never
dropped and the pulse bound is never widened after observing the arm.

The bracket-calibration variant is not built. V1 binds one pulse calibration
directory named to the fit script, as ruled.

## Pre-data receipt

This section applies only to the explicit V2 plan. V1 keeps its original
library and command-line behavior and neither requires nor evaluates a
receipt. Before V2 run 1, the operator must issue a pre-data receipt with
`scripts/fit_transfer_fiducial.py --issue-receipt`. A receipt is an immutable
JSON record made before any of the ten diagnostic runs; it prevents selecting
a more convenient plan, program version, calibration, or decision rule after
seeing data. It records:

- the SHA-256 of the exact plan bytes and the exact bytes of every one of the
  ten named configuration files;
- the exact-byte SHA-256 value of `scripts/fit_transfer_fiducial.py` and a
  source inventory for the fit program;
- the calibration directory's absolute path, evidence-file SHA-256,
  validation identifier, and capture timestamp; and
- the exact rules used by the fitter: minimum prefill and decode duration,
  post-window sampling dwell, minimum post-margin baseline, the radius rule
  `radius = max(abs(residual_lower_s), abs(residual_upper_s)) +
  effective_clock_anchor_bound_s`, and `supported iff residual_transfer_s <=
  b_pulse_s`.

The source inventory is a fixed, hand-curated tuple of nine
repository-relative paths, each present because the fit runs its code:
`joulewise/transfer_fiducial.py` (the fit, the receipt, and the capture),
`joulewise/powermetrics_fiducial.py` (the pulse-edge estimator),
`joulewise/uncertainty_evidence.py` (the metrology standard-error term
`se_metrology`), `joulewise/clock.py` (`ClockStamp`, the shape every clock
stamp is parsed into), `joulewise/schemas.py` (`BenchmarkConfig`, the planned
configuration the capture binds each run to), `joulewise/validation.py`
(reason-name checks), `joulewise/adapters/powermetrics.py` (the power-sample
reader), `joulewise/bundle_read.py` (retained-bundle reading), and
`joulewise/authentication_io.py` (reading the evidence bytes the fit
consumes). `source_inventory` maps each path to the SHA-256 of its exact
bytes. `source_inventory_sha256` is the SHA-256 of the UTF-8 bytes of that
mapping rendered as JSON with keys sorted, compact separators `,` and `:`,
`ensure_ascii=false`, and no trailing newline.

The inventory is *closed by execution*, meaning the following procedure
reproduces exactly these nine paths. A `joulewise/` module is executed by the
fit when, with every module under `joulewise/` except `joulewise/__main__.py`
already imported before tracing starts (so that no module body runs during
the trace and the result cannot depend on what the process imported earlier),
at least one function, method, lambda, or comprehension whose code object
names that module's file receives a call while the regression test (i) runs
`fit_run` on the synthetic fixture bundle `synthetic-transfer-r01` and (ii)
runs `build_capture` over the fixture plan with that fit and nine fixture
fits. The regression test is
`tests/test_transfer_fiducial.py::TransferFiducialTests::test_transfer_capture_records_estimator_revision_and_both_magnitudes`
(run with `python3 -m unittest
tests.test_transfer_fiducial.TransferFiducialTests.test_transfer_capture_records_estimator_revision_and_both_magnitudes`);
its tracer records a file on the first line event of such a code object,
which for ordinary in-file Python code is the same event as receiving a call. Code the interpreter cannot attribute to a file—dataclass-generated
methods, whose code objects report `<string>`—is invisible to this
measurement; a module whose only contribution is such code is listed by name
in `RECEIPT_TRACE_BLIND_MODULES` with its reason (`joulewise/clock.py`:
`ClockStamp`, constructed by `stamp_from_mapping`). The test asserts, in both
directions, `executed ∪ RECEIPT_TRACE_BLIND_MODULES == set(RECEIPT_SOURCE_MODULES)`:
nothing the fit runs escapes the receipt, and nothing the fit does not run is
frozen by it. It also asserts that every listed path exists, that no path is
duplicated, and that no trace-blind member is ever observed executing.
Without the pre-import step the same trace reports 22 files, because the lazy
imports inside `fit_run` execute the module bodies of fifteen import-closure
modules (mock adapters, `bundle.py`, ...) that the fit never calls; those
fifteen were frozen by an earlier revision of this inventory and are
deliberately excluded now.

Why a closed fence: without this inventory, an edit to
`uncertainty_evidence.py` on the day after the receipt is issued could change
`se_metrology` without changing the old receipt, so the receipt would no
longer identify the program that fit the data. Why not a wider one: freezing a
file the fit never runs lets an unrelated edit—a mock adapter, a bundle
writer—invalidate a receipt that is never reissued. The two largest members,
`bundle_read.py` and `adapters/powermetrics.py`, are frozen whole although the
fit executes a small fraction of each; an edit to either between receipt
issuance and the fit invalidates the receipt by design. Before any data
exists the operator re-issues the receipt from the edited tree; after data
there is no cure, and the fit refuses. The inventory fence closes before the
first receipt is issued, not before the first fit; receipt publication is
create-new and a receipt is not reissued after data.
At verification, a changed recorded hash refuses as
`pre_data_receipt_<repo-relative-path>_source_sha256_mismatch`, with the path
filled in literally.

The receipt file is canonical JSON: its keys are sorted, its indentation is
fixed, and it ends with exactly one newline. Issuance uses operating-system
create-new semantics, so an existing receipt refuses as
`pre_data_receipt_already_exists` instead of being overwritten. Issuance also
creates `<receipt>.sha256`, a sidecar (a separate small file) containing the
receipt file's exact-byte SHA-256 and one newline.

A receipt carrying the former schema version is refused by name as
`pre_data_receipt_schema_unsupported`, before the new closed key set is
compared.

At fit time the V2 fitter recomputes the sidecar binding and every recorded
input digest. It returns `inconclusive` with a named reason if the receipt is
absent, noncanonical, changed by even one byte, or differs in any pinned value;
if calibration was not captured before every run's prefill-start timestamp;
or if the plan's duration or dwell fields differ from the values the fitter
actually applies. It also checks each bundle's requested sampling dwell
against the plan. Thus the plan cannot merely state a duration or dwell that
the program ignores.

## Operation

These commands are parked until D-167's `_v5` chain and
`V5-NIGHTLY-G3-01` have passed. The complete readiness and idle procedure is
[window runbook §5](../phase_2/window_runbook.md#5-machine-and-operator-preflight):
connect the approved charger and cable, record the power policy, stop noisy
background work, prove `sudo -n powermetrics` works, complete the clock steps,
leave the machine untouched for the required idle period, use fresh output
roots, confirm backup capacity, and close every agent and browser-automation
session. “Network-time custody” means recording the prior automatic-time
state, disabling automatic adjustment for the window, retaining the clock
evidence, and restoring the prior state only after close-out; the exact Ed-only
commands and evidence requirements are in
[window runbook §5A](../phase_2/window_runbook.md#5a-pre-window-clock-stabilization-administrator-step-ed-performs-it).
“Verification” below means the V2 fitter exits zero and its capture has no
unexpected reason; “backup” means `scripts/backup_runs.sh` exits zero while
the source run root remains unchanged, as built in
[window runbook §11](../phase_2/window_runbook.md#11-record-duration-margins-back-up-then-extract-in-the-same-custody-session).

The two G2-a producer programs named below are owned by the parallel G2-a
producer stream. Their ruled command shapes come from producer designs 2–3 in
`docs/process_traces/2026-09-01-fresh-model-review/16-sol-g2a-executability-scout.md`
and ruling 16b. `--summary`, `--selection-record`,
`--prefill-prompt-pin`, `--output-root`, `--check`, `--allow-live`,
`--arm-countdown-s`, `--sleep-display-before-capture`,
`--power-policy`, `--runs-dir`, `--instrument-calibration-dir`,
`--instrument-power-policy`, `--post-window-sampling-dwell-s`,
`--issue-receipt`, `--receipt`, and `--output` were verified against this
repository's argument parsers. The producer flags `--config-root`,
`--input-inventory`, `--runs-root`, `--counts-output`, and `--summary-output`
of `scripts/summarize_g2a_prefill_probe.py`, plus `--selection-record`,
`--summary`, `--prompt-ladder`, `--ruling-trace`, and `--output` of
`scripts/issue_g2a_prefill_prompt_pin.py`, were verified against `feat/2026-09-01-g2a-probe` @ `82e7519d`; absent from this branch until that branch merges.

```sh
JW_REPO=/Users/edr/code/JouleWise
JW_PY=/Users/edr/code/JouleWise/.venv/bin/python
TF_ROOT=/Users/edr/JouleWise-transfer-fiducial-v2
TF_CAL_ROOT="$TF_ROOT/instrument_validation"
TF_RUNS_ROOT="$TF_ROOT/runs"
TF_BACKUP_DEST=/absolute/existing/backup/destination
POWER_POLICY=ac_high_power
G2A_CONFIG_ROOT=/absolute/path/to/g2a-probe-config-root
G2A_WINDOW_PLAN_ROOT=/absolute/path/to/g2a-window-plan-root
G2A_RUNS_ROOT=/absolute/path/to/g2a-runs-root
G2A_SUMMARY="$G2A_WINDOW_PLAN_ROOT/g2a-prefill-summary.json"
G2A_COUNTS="$G2A_WINDOW_PLAN_ROOT/g2a-prefill-counts.jsonl"
G2A_SELECTION_RECORD="$G2A_WINDOW_PLAN_ROOT/g2a-selected-prefill-length.json"
G2A_PROMPT_LADDER="$G2A_WINDOW_PLAN_ROOT/prefill-prompt-ladder.json"
G2A_PREFILL_PROMPT_PIN="$G2A_WINDOW_PLAN_ROOT/g2a-selected-prefill-prompt-pin.json"

cd "$JW_REPO"

# Build the four-row summary from authenticated probe inputs and run bundles.
PYTHONPATH="$JW_REPO" "$JW_PY" scripts/summarize_g2a_prefill_probe.py \
  --config-root "$G2A_CONFIG_ROOT" \
  --input-inventory "$G2A_WINDOW_PLAN_ROOT/g2a-input-inventory.json" \
  --runs-root "$G2A_RUNS_ROOT" \
  --counts-output "$G2A_COUNTS" \
  --summary-output "$G2A_SUMMARY"

PYTHONPATH="$JW_REPO" "$JW_PY" scripts/select_g2a_prefill_length.py \
  --summary "$G2A_SUMMARY" \
  --output "$G2A_SELECTION_RECORD"

# Bind the selected record, its exact summary, and the selected ladder prompt.
PYTHONPATH="$JW_REPO" "$JW_PY" scripts/issue_g2a_prefill_prompt_pin.py \
  --selection-record "$G2A_SELECTION_RECORD" \
  --summary "$G2A_SUMMARY" \
  --prompt-ladder "$G2A_PROMPT_LADDER" \
  --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md \
  --output "$G2A_PREFILL_PROMPT_PIN"

# The generator authenticates all three permanent inputs and re-tokenizes the
# prompt through the model mirror that the runtime will use.
"$JW_PY" configs/diagnostics/transfer_fiducial_v2/generate_plan.py \
  --summary "$G2A_SUMMARY" \
  --selection-record "$G2A_SELECTION_RECORD" \
  --prefill-prompt-pin "$G2A_PREFILL_PROMPT_PIN" \
  --output-root "$JW_REPO"

"$JW_PY" configs/diagnostics/transfer_fiducial_v2/generate_plan.py \
  --summary "$G2A_SUMMARY" \
  --selection-record "$G2A_SELECTION_RECORD" \
  --prefill-prompt-pin "$G2A_PREFILL_PROMPT_PIN" \
  --output-root "$JW_REPO" \
  --check

# Read the rung only after the two generator checks above accepted the record.
G2A_RUNG="$("$JW_PY" -c 'import json, sys; print(json.load(open(sys.argv[1]))["selected_prefill_tokens"])' "$G2A_SELECTION_RECORD")"

bash scripts/quiet_mac_prep.sh

"$JW_PY" scripts/validate_powermetrics_fiducial.py \
  --allow-live \
  --arm-countdown-s 20 \
  --sleep-display-before-capture \
  --output-root "$TF_CAL_ROOT" \
  --power-policy "$POWER_POLICY"

# Select exactly one valid calibration, in sorted path order, or stop.
TF_CAL_DIR="$($JW_PY - "$TF_CAL_ROOT" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
valid = []
for evidence_path in sorted(root.glob("*/instrument_evidence.json")):
    evidence = json.loads(evidence_path.read_bytes())
    if evidence.get("status") == "valid" and evidence.get("reasons") in ([], None):
        valid.append(evidence_path.parent.resolve())
if len(valid) != 1:
    raise SystemExit(f"expected exactly one valid calibration, found {len(valid)}")
print(valid[0])
PY
)" || exit 1

# Issue this receipt after calibration and before the first diagnostic bundle.
"$JW_PY" scripts/fit_transfer_fiducial.py \
  --plan configs/diagnostics/transfer_fiducial_v2/plan.json \
  --pulse-calibration-dir "$TF_CAL_DIR" \
  --issue-receipt \
  --receipt "$TF_ROOT/pre_data_receipt.json"

for TF_RUN in {01,02,03,04,05,06,07,08,09,10}
do
  TF_CONFIG="configs/diagnostics/transfer_fiducial_v2/tf-q3s-p${G2A_RUNG}-o512-r${TF_RUN}.json"
  "$JW_PY" -m joulewise run "$TF_CONFIG" \
    --runs-dir "$TF_RUNS_ROOT" \
    --instrument-calibration-dir "$TF_CAL_DIR" \
    --instrument-power-policy "$POWER_POLICY" \
    --post-window-sampling-dwell-s 6.0 || exit 1
done

"$JW_PY" scripts/fit_transfer_fiducial.py \
  --plan configs/diagnostics/transfer_fiducial_v2/plan.json \
  --runs-root "$TF_RUNS_ROOT" \
  --pulse-calibration-dir "$TF_CAL_DIR" \
  --receipt "$TF_ROOT/pre_data_receipt.json" \
  --output "$TF_ROOT/transfer_fiducial_capture.json"

# Verify that the fit reached one of the two conclusive diagnostic outcomes.
"$JW_PY" - "$TF_ROOT/transfer_fiducial_capture.json" <<'PY'
import json
import pathlib
import sys

capture = json.loads(pathlib.Path(sys.argv[1]).read_bytes())
if capture.get("verdict") not in {"supported", "exceeds_bound"}:
    raise SystemExit(f"transfer fit is not conclusive: {capture.get('reasons')}")
if capture.get("reasons") != []:
    raise SystemExit(f"transfer fit has refusal reasons: {capture.get('reasons')}")
print(capture["verdict"])
PY

bash scripts/backup_runs.sh "$TF_RUNS_ROOT" "$TF_BACKUP_DEST"

# Restore the pre-window automatic-time state only after fit and backup pass.
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
```

Review the capture without promoting its diagnostic verdict into any claim or
floor artifact. Preserve the receipt, its `.sha256` sidecar, the capture, the
backup log, and the recorded network-time off/on timestamps together.
