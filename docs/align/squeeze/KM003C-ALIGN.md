# KM003C capture on ALIGN v4 W1/D

2026-11-07. Branch `align/2026-11-07-km003c-align`, based on
`origin/lane/2026-11-07-w1-kit-r10`. **PROVISIONAL; synthetic verification only.**
Every DC result produced by this change is **SECONDARY / not yet registered**.
It changes no v4 rail estimator, exclusion, instrument check or alarm threshold.

Ed's RUN_STATE 210 / squeeze ruling places the KM003C between the wall brick
and MagSafe cable, covering power delivered by that supply to the Mac. This
is USB-C **DC input**, not AC wall energy. Battery assistance and charging can
separate DC input from total machine consumption.

## Wiring and supervision

The readiness audits found no direct reader launch in ALIGN. The indirect
HAZARD_PACK route in this checkout already has that launch:

1. `scripts/align_v4_session.py` delegates preparation to
   `align_pilot_session.py` and `bytes_h_session.py` with the v4 kit.
2. The Block plan writer renders the existing calibrated chain and a
   HAZARD_PACK `night_plan.json`. Its pack binds the v4 collection plan and
   the generated plan-tree hashes.
3. `scripts/run_night.py` dispatches HAZARD_PACK to
   `joulewise.b5.driver.run_hazard_night` with `production_seams`.
4. The production `meter_argv` launches the existing
   `scripts/km003c_monitor.py --out <custody>/hazards/meter/stream-NNN.jsonl`
   at plain QoS. `MonitorSupervisor(name='meter', restart_on_clean_exit=False)`
   starts it before the chain, hence before its first member's idle baseline.
5. The supervisor polls during the chain. Abnormal exits restart into a new
   create-once stream. A clean absent-meter exit is recorded once. After
   the chain is proven stopped, the existing post-chain hold precedes
   TERM/wait/census (and KILL escalation if needed). An unproven chain leaves
   the meter for the existing dead-man cleanup; that is not a proven stop.

No duplicate logger, USB decoder, clock fit, integration algorithm or parser
was added. The shared Block driver, reader, parser, harvest and `run_night`
are unchanged. The R1 rehearsal driver and R1 lane are unchanged.

The v4 generated collection plan now explicitly declares
`runtime_requirements.km003c`: enabled, existing reader and supervisor,
custody directory, whole-night scope and secondary label. `require_w1_ready`
checks the declaration before other readiness inputs; absent, disabled,
changed or unreadable declarations refuse with **RUN_STATE 210 / squeeze
ruling** in the message. Prepare checks generated-byte consistency; install
also calls `require_w1_ready`. The declaration is an admission contract for
the existing always-on HAZARD_PACK meter launch, not a second launcher or a
new shared-driver toggle. A future D kit must retain this contract and route.

Starting the child is not a claim of successful USB initialization. There is
no meter-readiness gate delaying the rail collection. Late initialization,
absence or insufficient coverage makes affected members' DC channel missing.

## Custody and desk layout

Paths below are relative to the supplied session/custody, not fixed machine
locations. No existing capture bytes are rewritten.

| Path | Owner / contents |
|---|---|
| `custody/hazards/meter/stream-NNN.jsonl` | Existing reader: header, raw sample batches, errors, closing trailer; one file per start |
| `custody/night/meter_supervision.jsonl` | Existing supervisor: starts, failures, exits, restart gaps, stop proof |
| `custody/night/meter.stdout.log`, `meter.stderr.log` | Existing child output |
| `custody/night/hazard_result.json` → `meter` | Existing supervisor summary and closing SHA-256 for each stream |
| `custody/night/result.json` → `artifacts` | Existing night publication hashes, including supervision journal / hazard result |
| Desk `PILOT.json` → `extra_checks.km003c` | New v4-only report: secondary label, source hashes, per-member integrals/flags and separate DC fits |

The ordinary v4 desk prints each member's status, gross integral, idle-subtracted
integral, DC residual and flags. The normal desk/harvest writes its report under
the existing output root; `desk --no-harvest` writes an inspection report. Use
only authorized ALIGN sessions, never a sealed Block-5 session. Existing
Block harvest continues to own archive creation and its own meter disclosures.
The new read-only addendum also accepts logical `.jsonl.zst` inputs through
the existing `desk_compress.read_bytes` seam.

Before using a stream, the addendum compares its decompressed/original-byte
SHA-256 with the Block driver's closing inventory. Missing/mismatched hashes
make that stream unusable. Recomputed source hashes are retained in the report.
No energy is added to the structure-only night result or courier.

## Per-member availability

`joulewise.align.apple.km003c` reuses Block harvest's `member_spans` and
`idle_baseline_span`. Member time includes idle baseline, sampler hull and
controller tail, rather than just the agent episode. It maps monotonic spans
to RAW using the existing parser's start/end clock pairs. A missing or
inconsistent pair has no guessed wall-time fallback.

A single aligned stream must cover the entire member and its idle baseline.
Streams across a restart are never spliced. One missing device-counter sample
inside that member hull is enough for `meter.member_gap`, even if the whole
stream's dropout fraction is below Block's disclosure threshold. USB/protocol
errors during the member, unknown-time parse errors, unresolved clock fit,
partial coverage, missing baseline/bundle, absent streams and hash failures
all produce explicit per-member flags and null DC energy/residual fields.
Gaps outside a member do not remove its DC channel. Existing parser disclosures
(including battery activity, gain unconfirmed and voltage) remain visible;
not every disclosure is a missing-channel condition.

The addendum never writes `excluded`, never adds a DC instrument check, and
never modifies a rail summary. Meter parsing/desk failures are themselves
reported as missing DC, including the exception type. “Powermetrics
admissibility unchanged” means existing rail criteria still apply; it does
not admit a member that already failed those criteria.

## Print-only residual convention

- `dc_in_energy_j`: existing parser's mean-power integral over the whole member.
- `episode_dc_in_energy_j`: separate integral over the episode alone.
- `baseline_w`: DC mean over that member's recorded idle baseline.
- `dc_in_delta_j`: whole-member DC integral minus `baseline_w * member_seconds`.
- `predicted_j`: `energy_residual.predict_episode` using a separately fitted DC
  `EnergyModel`, never the GPU-rail coefficients.
- `dc_in_residual_j`: `dc_in_delta_j - predicted_j`.

The fit uses the same five-term API and feature order as rails: intercept,
prefill, decode, context×decode and context×prefill. Logged reasoning counts
remain logged. Turn training energies use DC above the same baseline over
the union of each logged turn and its logged tool intervals. Unowned member
time (including warmup and thermal waits) remains in the measured total.
Training is separated by model, task pair and recorded serving configuration;
only unique benign trajectories with existing rail admission train the model.
Replays do not add training trajectories. Too few/unsupported fit rows give a
null residual and explicit fit status/flags.

This is exploratory equal-weight fitting through the existing API, using
zero in its training-weight slot and the explicit
`diagnostic_equal_weights` uncertainty kind. That slot is **not** a physical
zero-error assertion. Models and predictions are in sample. No standardized
score, conformal threshold, p-value, MDE, OR alarm or registration claim is
issued; `score` remains null.

## Open questions and lead verification

1. Confirm on the measurement MBP that the existing HAZARD_PACK route actually
   starts the reader before the first baseline, streams continuously through
   the last member, then records a proven stop and matching custody hashes.
   Confirm libusb, USB permissions and the actual hookup. The fake-process
   test uses a synthetic process census because sandbox process enumeration
   is denied; it is not native stop/census evidence.
2. Freeze the squeeze channel definition and baseline: current per-member
   idle subtraction is diagnostic only. The design synthesis proposes a
   window-level idle reference. Whole-member versus episode scope, warmup,
   gates and tail charging need the lead's registration decision.
3. Qualify DC against PDTR in-window and specify battery correction/availability
   using the existing `delta_machine_energy` API before calling it machine
   energy. The present output intentionally reports DC input; battery activity
   remains a disclosure, with no invented correction when missing.
4. Specify meter uncertainty, DC calibration folds and the held-out threshold
   procedure before using standardized residuals or a squeeze detector. No
   datasheet accuracy, physical fit uncertainty or rail-to-DC conversion was
   assumed here.
5. Confirm each future D kit retains the v4 declaration, HAZARD_PACK route and
   desk addendum. This branch implements the W1/D path available on the R10
   base; it does not invent or arm a future D-series roster.

Native verification must run in a clean lead-controlled quiet session after
agents exit. No live USB, powermetrics, SMC or MLX validation was performed.
No model download or Block-5 analysis/data access is part of this change.

Design sources read as repository objects:
`origin/align/2026-11-07-v4-{squeeze-design,reviewer2,v4-registration}`,
`docs/align/squeeze/<track>.md`. This implementation follows the task's
secondary/print-only instruction; it does not adopt the audits' proposed
primary-channel or preregistration changes.
