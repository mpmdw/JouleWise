```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Seat A source sweep found four proposed repairs spanning five numeric predicates, seven ruling items, and a definite epoch-arithmetic mismatch in provisional load-transition validation.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": null,
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "A-source-inventory",
        "action": "start_now",
        "detail": "Lead may consume this read-only source report."
      },
      {
        "row": "R1-R4",
        "action": "start_now",
        "detail": "Proposed repairs are reviewable below; no changes were applied."
      },
      {
        "row": "NR1-NR7",
        "action": "needs_ruling",
        "detail": "Resolve the identified contract, arithmetic-domain, and diagnostic-completeness choices."
      },
      {
        "row": "G2-a-number-consumption",
        "action": "wait_for",
        "detail": "Wait for integrated seat A/B adjudication and required refutation."
      },
      {
        "row": "live-capture",
        "action": "do_not_start",
        "detail": "This agent session is incompatible with QUIET-MAC acquisition."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 -c 'import math; t=1789000000.0; d=30.00000001; e=(t+d)-t; print(f\"ulp={math.ulp(t):.18g}; old={d <= e+1e-9}; proposed={d <= e+1e-6}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ulp=2.384185791015625e-07; old=False; proposed=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ulp=2\\.384185791015625e-07; old=False; proposed=True$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -c 'import math\nm=1789000000.0; s=m+0.1; e=m+0.2; produced=(s+e)/2-m; checked=((s-m)+(e-m))/2\nprint(\"producer_midpoint_s\",repr(produced),\"validator_midpoint_s\",repr(checked),\"delta_s\",repr(abs(produced-checked)),\"old_accept\",math.isclose(produced,checked,rel_tol=0,abs_tol=1e-12))\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "producer_midpoint_s 0.15000009536743164 validator_midpoint_s 0.1499999761581421 delta_s 1.1920928955078125e-07 old_accept False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "delta_s 1\\.1920928955078125e-07 old_accept False$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Seven dispositions require lead judgment; see NR1-NR7. Blocking applies to closing this sweep, not to the completed source inventory.",
      "needs": "Adjudicate NR1-NR7 with seat B and the required refuters."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Inspection and standalone arithmetic only. No repository tests, imports executing repository code, live acquisition, edits, or git commands were run. Workspace and dirty-state fields are uninspected, not claims of cleanliness.",
      "needs": "Lead applies and verifies any accepted repair."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The installed LaunchAgent, emitted night chain, and selected night plan were not supplied or authenticated. Source routing is established; deployment parity and instantiated night-window limits remain unverified.",
      "needs": "Compare the deployed plan/chain with the inspected generator before acquisition."
    }
  ]
}
```

## A. Gate inventory

This is a source inventory, not live hardware validation. Repeated calls to the same predicate appear together; schema versions, hash lengths, and diagnostic formatting widths are not measurement tolerances.

Paths below are relative to `joulewise/` unless prefixed `scripts/`, `configs/`, or `docs/`. **N** means **“n/a: not an energy.”** For a quantity \(x\) in joules, **R(x)** means its ratios to **1 J; 5 J**, respectively.

The requested **~1 J attribution scale** and **~5 J planning scale** come from D-078 clause 11 and D-083. However, the dated addenda at `docs/decision_log.md:10942` and `:10965` explicitly withdraw F+B as a guaranteed clearable-effect description: **F+B is non-gating planning information; floor and interval checks remain separate.** The ratios below do not introduce another acceptance gate.

Instrument facts:

- G2-a requests **10 Hz**, hence **100 ms nominal intervals**: `scripts/generate_g2a_probe_inputs.py:498`; adapter interval is `max(1, round(1000/power_hz))` milliseconds at `adapters/powermetrics.py:1461`.
- The fiducial also requests **100 ms**: `powermetrics_fiducial.py:66`.
- Native plist dates are **whole-second censored timestamps**, not 100 ms timestamps. Interval reconstruction uses the recorded integer `elapsed_ns`: `adapters/powermetrics.py:1769`, `docs/contracts/powermetrics_fiducial.md`, and `docs/contracts/run_bundle_layout.md:515`.
- The fiducial contract describes **~115 ms observed cadence**, so nominal 100 ms must not replace observed support widths.
- Controller timestamps are epoch binary64 values (`clock.py:55`). At contemporary epochs one representable step is **0.238418579 μs**. The existing anchor implementation already documents **1 μs padding for four epoch-scale roundings**, `uncertainty_evidence.py:45–59`. That is numerical representation allowance, not claimed instrument sensitivity.

### Identity checks

| # | file:line | Constant / expression | Value | Quantity protected | Class | Ratio | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| I01 | reduce.py:1400 | Artifact bound versus metadata bound | `abs Δ ≤ 1e-12 s` | Same copied fiducial scalar | identity | N | keep | No independent physical readings. |
| I02 | reduce.py:1472 | Residual extrema contained by declared B | `extrema ≤ B+1e-12 s` | Internal enclosure consistency | identity | N | keep | B must dominate its own stored residual rows. |
| I03 | reduce.py:1584; powermetrics_fiducial.py:1342 | Fresh fitted edge inside stored residual interval | `1e-12 s` versus **zero** slack | Replay consistency | identity | N | needs_ruling | Same raw bytes, potentially different estimator revision; two consumers also disagree on slack. NR1. |
| I04 | reduce.py:1847 | Authenticated override cannot narrow B | `override+1e-12 ≥ B` | Bracket maximum propagation | identity | N | keep | Copies/maxima of authenticated bounds, not noisy readings. |
| I05 | reduce.py:1928 | Stored versus raw-derived power | `1e-9·max(1,abs(P)) W` | Raw/CSV arithmetic agreement | identity | N | keep | Same rail data; alternate summation path justifies float fuzz. |
| I06 | reduce.py:1948 | Stored versus reconstructed support width | `1e-6 s` | Same elapsed interval | identity | N | keep | Different epoch anchors/subtractions; microsecond allowance covers current epoch rounding. |
| I07 | reduce.py:1955 | Relative sample spacing | `1e-6 s` | Same cumulative elapsed timeline | identity | N | keep | Uniform reanchoring changes rounding, not physical spacing. |
| I08 | bundle_read.py:2885 | Adjacent interval overlap allowance | `1e-6 s` | Normalized support continuity | identity | N | keep | Intended adjacent supports can differ through epoch arithmetic; a real cadence overlap remains rejected. |
| I09 | bundle_read.py:2861 | Per-rail sample timestamps | Exact equality | Rails from one plist record | identity | N | keep | Rails are not separately timed instruments. |
| I10 | bundle_read.py:2850 | Per-rail support tuples | Exact equality | Shared averaging support | identity | N | keep | Every rail repeats the same record support. |
| I11 | bundle_read.py:2828 | `interval_end_s == timestamp_s` | Exact equality | Endpoint-stamped representation | identity | N | keep | Two fields denote the same endpoint. |
| I12 | environment_admission.py:263 | Stored/fresh environment evaluation | Exact eligibility/findings/hash equality | Policy evaluation of same snapshot | identity | N | keep | Detects stale or mismatched evaluation. |
| I13 | window_duration_margins.py:745 | `_numbers_equal` | Absolute `1e-12` | Duration/count/cadence replay | identity | N | keep | Uses the reducer’s own window/count/gap helpers. |
| I14 | window_duration_margins.py:1089 | Recorded duration versus `end-start` | `1e-12 s` | Same phase-window subtraction | identity | N | keep | Producer stores the same endpoint subtraction. |
| I15 | window_duration_margins.py:1120 | Cell minima, ratios, count margins | Exact recomputation | Derived receipt statistics | identity | N | keep | Same member table and arithmetic. Negative margins are reportable. |
| I16 | load_transition_alignment.py:701 | Plateau threshold midpoint | `1e-12 W` | Same two plateau medians | identity | N | keep | Both sides use `(low+high)/2`. |
| I17 | load_transition_alignment.py:397,715 | Response-support midpoint | `1e-12 s` | Same interval midpoint | identity | N | re-set | **Different epoch-arithmetic paths demonstrably disagree by 0.119 μs. R4.** |
| I18 | load_transition_alignment.py:717 | Residual equals offset minus center | `1e-12 s` | Derived residual | identity | N | keep | Same subtraction, once I17 is repaired. |
| I19 | load_transition_alignment.py:720 | Per-transition endpoint maximum | `1e-12 s` | Same support-bound calculation | identity | N | keep | Same two endpoint offsets. |
| I20 | load_transition_alignment.py:748,753 | Direction summaries and centers | `1e-12` | Medians/maxima of stored transitions | identity | N | keep | No independent measurement comparison. |
| I21 | load_transition_alignment.py:764 | Overall conservative maximum | `1e-12 s` | Maximum across directions | identity | N | keep | Same maxima. |
| I22 | envelope_gate.py:514 | Permutation chi-square tie handling | `stat ≥ observed−1e-12` | Numerical equality of discrete statistics | identity | N | keep | Tie hygiene, not a physical tolerance; see C. |
| I23 | reduce.py:1506; calibration_bracketing.py:1200 | Declared versus authenticated capture time | `abs Δ ≤ 1 s` | Same capture-time declaration | identity | N | keep | Explicit contract allowance; does not authorize independent freshness origins. |
| I24 | powermetrics_fiducial.py:234 | Event timestamp versus ClockStamp epoch | `MAX_EVENT_CLOCK_SKEW_S=1 s` | Duplicate representations of event time | identity | N | keep | Authentication consistency, not a permitted 1 s phase-alignment error. |
| I25 | calibration_bracketing.py:622,659,664 | Decimal presentation/operative quantization | `1e-18`, `1e-6`, `1e-15 s` | Reproduction of issued derivation | identity | N | keep | **The 1e-15 is a decimal presentation quantum, not required measurement sensitivity.** |
| I26 | detection_floor.py:795,832 | Operative aliases and recorded allowance | `1e-12 s` | Same bound/allowance | identity | N | keep | Decimal-to-float aliases. |
| I27 | detection_floor.py:835 | `operative == endpoint+allowance` | `1e-12 s` | Once-composed bound | identity | N | keep | Decimal sum converted once versus binary64 addition; tolerance easily covers this scale. |
| I28 | floor_extraction.py:529,2647; detection_floor.py:1318; floor_mint_estimator.py:520 | Sweep/session bound equality | `1e-12 s` | Same authenticated operative B | identity | N | keep | No physical-reading comparison. |
| I29 | floor_extraction.py:2092 | Envelope point versus metric | `rel=1e-9, abs=1e-12 J` | Same point estimate | identity | R(`max(1e-12,1e-9·abs(E))`) | keep | Cross-field arithmetic consistency. |
| I30 | floor_extraction.py:590; detection_floor.py:1414 | Swept zero point versus ABBA delta | `rel=1e-9, abs=1e-12 J` | Equivalent contrast via different paths | identity | R(`max(1e-12,1e-9·abs(Δ))`) | needs_ruling | Near cancellation, error scales with member integrals, not the tiny contrast. NR2. |
| I31 | detection_floor.py:2222 and callers | `_close` | `min(max(1e-12,1e-12·abs(expected)),1e-6)` | Recomputed floor/statistic fields | identity | Energy fields: R(tolerance) | keep | Same inputs/formulas; 1 μJ is a ceiling on replay fuzz, not a measurement floor. |
| I32 | floor_mint_estimator.py:700 | Stored/recomputed common-mode widths | Exact `Decimal(str(...))` equality | Authenticated width reproduction | identity | `0;0` | keep | Same registered source computation; no noise allowance belongs here. |
| I33 | floor_mint_estimator.py:214; calibration_bracketing.py:670 | Allowance formula and embedding count | Exact max; count `1` | Prevent missing/double allowance | identity | N | keep | Arithmetic/pre-registration invariant. |
| I34 | night_gate.py:769 | ISO microsecond time versus epoch | `1e-6 s` | Same confirmation timestamp | identity | N | keep | Different serialization paths legitimately lose sub-microsecond digits. |
| I35 | bundle_read.py:1315,1517; detection_floor.py:3736,3814,3841; window_duration_margins.py:1093 | Counts, ordinals, ABBA positions, count margins | Exact counts; four ABBA members; `count−3` | Evidence structure | identity | N | keep | Counts are exact integers, not measurements needing jitter. |
| I36 | floor_extraction.py:308 | Structural shift-grid zero | Exactly one `+0.0` | Canonical zero-shift candidate | identity | N | keep | Builder identity; not a demand for a physically zero timing error. |

### Measurement thresholds and numerical boundary allowances

“Keep” here means sensible for the stated purpose. It does not claim that an operational screen proves universal transfer or statistical coverage.

| # | file:line | Constant / expression | Value | Quantity protected | Class | Ratio | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| M01 | adapters/powermetrics.py:1461; powermetrics_fiducial.py:66 | Requested sampling interval | G2-a/fiducial `100 ms`; adapter minimum `1 ms` | Temporal support | measurement | N | keep | Nominal request; actual `elapsed_ns` controls integration. |
| M02 | adapters/powermetrics.py:70,1983 | Low GPU idle-ratio cutoff | `<0.80` | Idle GPU activity | measurement | N | keep | Coarse activity screen, not microscopic sensitivity. |
| M03 | adapters/powermetrics.py:71,1991 | Fraction of low-idle records | `≥0.40` | Persistent GPU activity | measurement | N | keep | Rejects sustained contamination rather than one sample. |
| M04 | adapters/powermetrics.py:72,1995 | GPU mean-frequency screen | `>800 MHz` | Elevated idle GPU state | measurement | N | keep | Coarse operational screen; provenance gap noted in D. |
| M05 | powermetrics_fiducial.py:62 | Warmup pulse count | `3` | Initialization effects | measurement | N | keep | Frozen protocol setting, not an acceptance epsilon. |
| M06 | powermetrics_fiducial.py:63 | Commanded pulse duration | `1 s` | Fit plateau and edges | measurement | N | keep | Roughly ten nominal intervals per pulse. |
| M07 | powermetrics_fiducial.py:64 | Pulse gap | `1.5+vanDerCorput₂(j) s` | Separation and sampling-phase diversity | measurement | N | keep | Contract explicitly avoids 10 Hz phase lock. |
| M08 | powermetrics_fiducial.py:65 | Baseline before/after train | `5 s` each | Background estimate | measurement | N | keep | Many sample intervals outside pulses. |
| M09 | powermetrics_fiducial.py:67–68 | Load shape | `4096×4096`, FP16 | Reproducible calibration stimulus | measurement | N | keep | Protocol setting; not an admissible-error threshold. |
| M10 | powermetrics_fiducial.py:71,768 | Minimum plateau over baseline | `10 W` | Detectable calibration stimulus | measurement | N | keep | At nominal cadence, 10 W corresponds to 1 J per record; ample stimulus. |
| M11 | powermetrics_fiducial.py:72,770 | Minimum robust SNR | `10` | Distinguishable pulse | measurement | N | keep | Strong signal requirement, explicitly frozen. |
| M12 | powermetrics_fiducial.py:733 | Robust sigma lower bound | `max(1.4826·MAD,0.001 W)` | Nondegenerate fit weighting | measurement | N | keep | 1 mW matches reported-power quantization scale; it does not assert 1 mW instrument accuracy. |
| M13 | powermetrics_fiducial.py:101,555 | Huber delta | `1.345` | Robust loss influence | measurement | N | keep | Frozen estimator parameter; not an energy gate. |
| M14 | powermetrics_fiducial.py:832 | Pulse versus flat-model loss | `best_loss < 0.5·flat_loss` | Pulse-model discrimination | measurement | N | keep | Material fit improvement; not a calibrated significance probability. |
| M15 | powermetrics_fiducial.py:857 | Accepted loss increment | `max(1,0.05·best_loss)` | Residual-region definition | measurement | N | keep | Frozen model-defined region; physical/coverage limitation must remain disclosed. |
| M16 | powermetrics_fiducial.py:73,785 | Fit search/coverage half-range | `0.75 s` | Complete edge search support | measurement | N | keep | Several sample intervals; missing support cannot be waived. |
| M17 | powermetrics_fiducial.py:74 | Coarse fit step | `5 ms` | Search discretization | measurement | N | keep | Numerical optimizer resolution, not required timestamp accuracy. |
| M18 | powermetrics_fiducial.py:75 | Fine fit step | `0.5 ms` | Search discretization | measurement | N | keep | Same distinction; accepted-region extents remain included. |
| M19 | powermetrics_fiducial.py:76,684 | Region-cell resolution | `0.1 ms` | Conservative projection termination | measurement | N | keep | Entire retained cell extents are included; finer resolution does not reject noisy readings. |
| M20 | powermetrics_fiducial.py:95,841 | Maximum fitted edge shift | Strictly `<0.50 s` | Validated fit domain | measurement | N | keep | Five nominal intervals; an outside-domain fit lacks calibration authority. |
| M21 | powermetrics_fiducial.py:97–98,418 | Authenticated pulse duration | `[0.8,1.2] s` | Actual executed pulse shape | measurement | N | keep | ±200 ms around 1 s is instrument-scale, not microscopic. |
| M22 | powermetrics_fiducial.py:99,430 | Gap-schedule error | `≤0.25 s` | Executed train spacing | measurement | N | keep | Approximately two actual cadence intervals. |
| M23 | powermetrics_fiducial.py:100,438 | Authenticated baseline minimum | `4.5 s` each side | Baseline coverage | measurement | N | keep | Allows 0.5 s below nominal protocol duration. |
| M24 | powermetrics_fiducial.py:102,754 | Plateau inset | `0.25 s` per edge | Exclude edge mixtures from plateau | measurement | N | keep | Multiple samples away from each command boundary. |
| M25 | powermetrics_fiducial.py:103,721 | Local pulse margin | `0.75 s` | Local fit and outside-baseline selection | measurement | N | keep | Same scale as fit domain. |
| M26 | powermetrics_fiducial.py:896 | Spurious plateau threshold | `baseline+max(5 W,5σ)` | Uncommanded load | measurement | N | keep | Large persistent excursion, not baseline noise. |
| M27 | adapters/powermetrics.py:1030 | Post-idle sentinel duration/count | `max(3 intervals,min(5 s,baseline))`; count ≥3 | Drift evidence availability | measurement | N | keep | Duration scales with cadence. |
| M28 | reduce.py:117,987 | Short-window cadence ratio | `T/local_gap ≥2` | Resolvable phase/item/block window | measurement | N | keep | Instrument-scale duration requirement. |
| M29 | reduce.py:118,987 | Request cadence ratio | `T/local_gap ≥4` | Resolvable request window | measurement | N | keep | Contract gives ~460 ms at ~115 ms cadence. |
| M30 | reduce.py:997; powermetrics_fiducial.py:1364 | Clock bound versus duration | `B≤0.25T`; `Tmin=max(4B,cadence requirement)` | Timing identifiability | measurement | N | keep | Bound scales with the measured window. |
| M31 | reduce.py:2360; floor_extraction.py:2126 | Anchor plus joint-edge energy width | `≤0.25·abs(E)`; E=0 requires zero width | Energy identifiability | measurement | `0.25abs(E);0.05abs(E)` for E in J | keep | Registered relative-resolution gate; distinct from ~1 J/~5 J reference scales. |
| M32 | calibration_bracketing.py:212 | Active bracket screen | `0.009724 s` | Calibration drift/allowance floor | measurement | N | needs_ruling | Physically derived, but unresolved D-125 lineage-floor conflict is already registered. NR3. |
| M33 | calibration_bracketing.py:215,1994 | Maximum budgetable drift | `0.010164834757777545 s` | Maximum admitted bracket change | measurement | N | keep | Active n=17 derivation; not the obsolete policy literal 0.010 s. |
| M34 | calibration_bracketing.py:213,1936; generated chain:453 | Preflight level screen | `0.032898493715362 s` | Out-of-family pre-calibration | measurement | N | keep | Issued D-079/D-102 derivation; long decimal spelling is not required sensitivity. |
| M35 | controller.py:2555 | Complete cooldown span | `30 s` | Sustained recovery | measurement | N | keep | Frozen policy, independent of coverage fraction. |
| M36 | controller.py:2552 | Cooldown coverage | `0.8×30=24 s` | Enough observed recovery data | measurement | N | keep | Explicitly accommodates probe gaps. |
| M37 | controller.py:2555–2556 | Completion/coverage slack | `1e-9 s` | Cooldown threshold boundary | measurement | N | re-set | Below epoch representation resolution; replace with bounded arithmetic allowance. R3. |
| M38 | environment_admission.py:180 | Baseline duration fits attempt | `duration≤end−start+1e-9 s` | Capture belongs to attempt | measurement | N | re-set | Elapsed-nanosecond sum versus rounded epoch difference can falsely disagree. R1. |
| M39 | environment_admission.py:186–187 | Capture endpoints fit attempt | `1e-9 s` slack | Causal capture containment | measurement | N | re-set | Nanosecond slack is ineffective at epoch scale. R1. |
| M40 | environment_admission.py:396 | Thermal-evidence continuity | Gap `≤1e-6 s` | Complete thermal observation span | measurement | N | keep | Numerical support continuity; do not replace with a cadence-sized gap allowance. |
| M41 | reduce.py:1986–1988 | Shifted trace covers both window edges | Zero explicit slack | Complete allocation domain | measurement | N | re-set | Inconsistent with preceding one-ULP tail admission; align endpoint arithmetic. R2. |
| M42 | night_gate.py:57,1206; scripts/prewindow_check.sh:35 | Load average | `≤2.0` | Quiet-machine readiness | measurement | N | keep | Coarse contamination screen; not an energy uncertainty estimate. |
| M43 | idle_admission.py:437; production policy | CPU busy p95 | `≤0.5` | Idle CPU contamination | measurement | N | keep | Contract records clean reference p95 0.211. |
| M44 | idle_admission.py:439; production policy | Combined-power p95 | `≤1 W` | Idle activity | measurement | N | keep | Contract records clean reference 0.143 W; not a 1 J limit. |
| M45 | detection_floor.py:4549 | Consumer mean-power envelope | Within calibrated min/max; zero extra tolerance | Transfer support | measurement | N | keep | Crossing a calibrated support limit is missing transfer evidence, not float identity. |
| M46 | detection_floor.py:4554 | Consumer duration envelope | Within calibrated min/max | Transfer support | measurement | N | keep | No independent authority to extrapolate duration. |
| M47 | detection_floor.py:4558 | Consumer p95 sample gap | `≤calibration maximum` | Cadence transfer | measurement | N | keep | Worse cadence requires evidence, not an arbitrary epsilon. |
| M48 | detection_floor.py:4562 | Consumer bracketing gap | `≤calibration maximum` | Edge-support transfer | measurement | N | keep | Same rationale. |
| M49 | detection_floor.py:4566 | Consumer cadence ratio | `≥calibration minimum` | Relative temporal resolution | measurement | N | keep | Same rationale. |
| M50 | detection_floor.py:4583 | Clock-bound transport maximum | `≤calibrated maximum` | Clock transfer | measurement | N | keep | Absent/larger bound remains unsupported. |
| M51 | detection_floor.py:4583 | Interpolation-bound transport maximum | `≤calibrated maximum J` | Reconstruction transfer | measurement | R(artifact maximum) | keep | Artifact-dependent bound; no universal numeric value. |
| M52 | detection_floor.py:4583 | Idle-drift-bound transport maximum | `≤calibrated maximum J` | Baseline transfer | measurement | R(artifact maximum) | keep | Artifact-dependent bound; do not invent a missing supplier. |
| M53 | load_transition_alignment.py:349,371 | Plateau ordering/response threshold | `0≤low<high`; response crosses midpoint | Transition detection | measurement | N | keep | Frozen descriptive response rule; no production calibration claim. |
| M54 | load_transition_alignment.py:367 | Adjacent normalized supports | No overlap, zero slack | Response-support chronology | measurement | N | needs_ruling | No production normalizer or live trace establishes whether exact adjacency is guaranteed. NR4. |
| M55 | envelope_gate.py:49,464 | Maximum non-EOS rate | `≤0.05` | Workload equivalence | measurement | N | keep | At n=8 this intentionally means zero non-EOS items. |
| M56 | envelope_gate.py:50,464 | Across-level non-EOS spread | `≤0.05` | Workload equivalence | measurement | N | keep | Discrete behavioral gate, not instrument noise. |
| M57 | envelope_gate.py:51,485 | Emitted-token mean spread | `≤1 token` | Workload equivalence | measurement | N | keep | Naturally count-scale tolerance. |
| M58 | envelope_gate.py:53,519 | Permutation p-value | `≥0.01` | Distribution homogeneity screen | measurement | N | keep | Statistical screen; 10,000 permutations resolve p in steps ~0.0001. |
| M59 | envelope_gate.py:54,574 | Global prompt-token range | `≤4 tokens` | Prompt equivalence | measurement | N | keep | Count-scale tolerance. |
| M60 | envelope_gate.py:55,575 | Level mean prompt-token spread | `≤2 tokens` | Prompt equivalence | measurement | N | keep | Count-scale tolerance. |
| M61 | envelope_gate.py:56,609 | E5 evaluability | `≥10` parsed items per class | Diagnostic sample size | measurement | N | keep | Explicitly advisory; with eight-item levels it is normally unevaluable and does not refuse. |
| M62 | detection_floor.py:1023; floor_extraction.py:2330 | Widened uncertainty exceeds point floor | Strict `>` | Attribution-limit label | measurement | R(data-dependent floors) | keep | Labels the widened-floor path; not itself a demand to eliminate attribution uncertainty. |

### Evidence and pre-registration refusals

| # | file:line | Constant / expression | Value | Quantity protected | Class | Ratio | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| E01 | adapters/powermetrics.py:59 | Readiness deadline | `15 s`; poll `0.05 s` | Sampler actually started | evidence | N | keep | Missing sampler evidence, not sensitivity. |
| E02 | adapters/powermetrics.py:66; scripts/validate_powermetrics_fiducial.py:1055 | Native rollover deadline | `15 s` | Causal timestamp anchoring | evidence | N | keep | Far larger than native one-second rollover. |
| E03 | adapters/powermetrics.py:624 | Post-marker drain deadline | `anchor_lag+2/f+0.25 s`; lag capped at `5 s`; poll `0.05 s` | Right-edge support | evidence | N | keep | Cadence-sized drain plus bounded host margin; unresolved tail still refuses. |
| E04 | adapters/powermetrics.py:1468 | Bounded-capture timeout | `max(15,1.5·nominal+10) s` | Complete bounded capture | evidence | N | keep | Substantial operational headroom. |
| E05 | reduce.py:2952,3521 | Measured-window sample minimum | `2` | Integrable trace | evidence | N | keep | No energy from an insufficient trace basis. |
| E06 | powermetrics_fiducial.py:725 | Outside-baseline intervals | At least `3` | Median/MAD basis | evidence | N | keep | Missing estimator input. |
| E07 | powermetrics_fiducial.py:59–61; reduce.py:1430 | Complete pulse census | `59` current; `40` historical v1/v2 | Calibration evidence | evidence | N | keep | Current 59 count has the documented finite-sample 95/95 rationale. |
| E08 | powermetrics_fiducial.py:104,1016 | Spurious plateaus | `0`; detection requires `2` consecutive records | Uncommanded calibration activity | evidence | N | keep | Prevents contaminated pulse evidence. |
| E09 | powermetrics_fiducial.py:88,536 | Projection work budget | `165,000` cells total | Complete accepted region | evidence | N | keep | D-143: observed maximum 137,189; 20.3% headroom. Partial regions never license B. |
| E10 | powermetrics_fiducial.py:92,543 | Projection wall deadline | `120 s` | Host-pathology containment | evidence | N | keep | Supplementary resource limit; wall-trigger diagnostics are not reproducible measurements. |
| E11 | reduce.py:1265–1591 | Missing/invalid raw, stamps, calibration, pulses | Any failure | Authenticated bounded anchor | evidence | N | keep | Explicit D-161 physics/evidence class. |
| E12 | powermetrics_fiducial.py:58; calibration_bracketing.py:1860 | Calibration freshness and causal endpoints | `86,400 s`; pre≤start, post≥end | Transfer horizon | evidence | N | keep | Contract T2; both collection endpoints matter. |
| E13 | environment_admission.py:22,157 | Admission-to-window gap | `≤600 s`; admission cannot follow start | Fresh environment observation | evidence | N | keep | Stale/causally reversed admission is not acceptable evidence. |
| E14 | environment_admission.py:30,201,409 | Environment predicates and before/after observations | All required known/pass | Uncontaminated capture | evidence | N | keep | Display, screensaver, thermal, policy, and CPU evidence fail closed. |
| E15 | idle_admission.py:433 | CPU-admission minimum sample count | `30` | Stable idle quantiles | evidence | N | keep | Approximately three nominal seconds; production idle capture is 30 s. |
| E16 | reduce.py:971,2914; window_duration_margins.py:600 | Positive measured/phase duration | `T>0` | Defined integration interval | evidence | N | keep | Zero or reversed windows are not readings. |
| E17 | reduce.py:116,979 | Phase sample minimum | `3` overlapping intervals | Phase evidence | evidence | N | keep | Separate from G2-a’s prospective five-interval margin. |
| E18 | reduce.py:1000–1025; floor_extraction.py:2085 | Missing interpolation, required drift, idle baseline, or anchor envelope | Any required term absent | Complete uncertainty basis | evidence | N | keep | D-161; never replace missing evidence with zero. |
| E19 | calibration_bracketing.py:1497 | Authenticated ledger/snapshot/cutoff | Matching baseline; issued head sequence `>0` | Calibration provenance | evidence | N | keep | Missing/incorrect source universe. |
| E20 | calibration_bracketing.py:1530,1763 | Identity epoch or protocol/estimator changes | Exact match required | Stationarity and issued method | evidence | N | keep | Pre-registration/transfer evidence, not a deliberate-only guard. |
| E21 | calibration_bracketing.py:1756,1809 | Corpus-doubling trigger | Current `17→34`; old `19→38` | Acceptance rederivation | evidence | N | keep | Registered prospective trigger; old generations retain their own counts. |
| E22 | calibration_bracketing.py:1822 | New valid observation expands corpus range | Any value outside issued min/max | Screen freshness | evidence | N | keep | Deliberately a rederivation trigger, not a measurement-resolution epsilon. |
| E23 | calibration_bracketing.py:1826 | New systematic-invalid observation | Any qualifying observation | Screen validity | evidence | N | keep | Challenges the evidence supporting the preflight screen. |
| E24 | detection_floor.py:816; floor_mint_estimator.py:214 | Positive allowance embedded once | Allowance `>0`, embedding count `1` | Nondeleted calibration allowance | evidence | N | keep | Frozen causal composition. |
| E25 | floor_extraction.py:2306,2740; detection_floor.py:866 | Minimum inputs for sample SD | `2` members/blocks | Defined floor estimator | evidence | N | keep | Mathematical minimum, not claim-ready minimum. |
| E26 | detection_floor.py:121–122,847,4167 | Claim guard/minimum n | `n≥5`; `g=max(1,sqrt(9/(n−1)))`; g=1 at n≥10 | Small-sample operational guard | evidence | R(g·floor) | keep | C-028 accepted operational factor, explicitly not a coverage guarantee. |
| E27 | detection_floor.py:123,1069; floor_extraction.py:2318,2751 | Exact-corner enumeration limit | `n≤16` when widths require enumeration | Exact widened-floor calculation | evidence | N | keep | Computational completeness; >16 cannot silently use a partial maximum. |
| E28 | detection_floor.py:4149; floor_extraction.py:184 | Missing absolute/comparative floor, invalid source, stale/not-ready cells | Required suppliers present and eligible | Claim-floor basis | evidence | N | keep | D-161 evidence refusal. |
| E29 | floor_extraction.py:169,2074 | Cooldown-cap disposition | Exclude affected same slot; remaining n gates apply | Clean acquisition population | evidence | N | keep | Existing evidence-based exclusion, not outcome-dependent tuning. |
| E30 | floor_mint_estimator.py:247–289 | Unfrozen/missing/pending estimator registration | Exact preregistered authorized path | Analysis choice | evidence | N | keep | D-161 pre-registration class. |
| E31 | detection_floor.py:742–746; floor_extraction.py:384 | Shared-edge noncollapse | Outward-rounded `start+B < end−B` | Valid separable domain | evidence | N | keep | Mathematical domain proof; allowing collapse changes the estimator. |
| E32 | night_gate.py:58,991–998 | Plan age | Not future; age `≤36 h` | Fresh unattended instructions | evidence | N | keep | Operational freshness, separate from 24 h calibration transfer. |
| E33 | night_gate.py:934,977,1288 | Launch window / ARM validity | Plan’s `[t0,t0+window_max_s]`; monotonic time `<valid_until` | Current authorization | evidence | N | keep | Instantiated limits require the selected plan; not supplied here. |
| E34 | night_gate.py:42,1035; scripts/run_night.py:465 | Agent census | Zero matches; failed observation refuses | Agent-free capture | evidence | N | keep | D-161 physical contamination class. |
| E35 | night_gate.py:1141 | Screensaver preference | `idleTime == 0` | Avoid screensaver activity | evidence | N | keep | Configuration value, **not** measured HID-idle duration. |
| E36 | night_gate.py:1237 | CPU speed limit | Every reported limit exactly `100` | No thermal throttling | evidence | N | keep | Discrete OS status; not a 100%-accurate physical reading. |
| E37 | scripts/generate_g2a_probe_inputs.py:313; scripts/select_g2a_prefill_length.py:18 | Small-model members per rung | At least `5` | Prospective resolvability evidence | evidence | N | keep | Ratified A4 minimum. |
| E38 | scripts/select_g2a_prefill_length.py:19,76; scripts/summarize_g2a_prefill_probe.py:527 | Small-member overlap count | Every member `≥5` | Margin over reducer minimum 3 | evidence | N | keep | **Five, never eight.** Count concerns overlapping intervals, not five full intervals of duration. |
| E39 | scripts/summarize_g2a_prefill_probe.py:20; scripts/gen_g2_phase_d.py:52 | Large-model evidence completeness | At least `1` per rung | Diagnostic record | evidence | N | needs_ruling | Completeness can stop a chain described as non-gating for the large model. NR5. |
| E40 | scripts/gen_g2_phase_d.py:55; scripts/select_g2a_prefill_length.py:17 | Prompt ladder and realized counts | Exactly `512,1024,2048,4096` | Prospective input identity | evidence | N | keep | Exact token counts are operator/pre-registration facts. |
| E41 | scripts/gen_g2_phase_d.py:239–284 | Calibration bracket structure | One pre and one post governed slot | Causal bracket | evidence | N | keep | Missing endpoint remains missing evidence. |
| E42 | load_transition_alignment.py:186,201,243,353 | Transition evidence counts | Plateau ≥2/state; target persistence ≥2; ≥3 total samples; 4 transitions/direction in manifest | Descriptive alignment basis | evidence | N | keep | Frozen eight-transition design. |
| E43 | load_transition_alignment.py:24–27; window_duration_margins.py:568 | Provisional status / raw replay / unique phase | No physical promotion; one phase window; authentic raw support | Proper evidence scope | evidence | N | keep | Fixture or unadjudicated alignment never becomes production calibration. |
| E44 | bundle_read.py:2823,2939; adapters/powermetrics.py:2037 | Finite/nonnegative power, positive widths/weights, ordered events; weighted variance q<1 | Domain checks | Valid trace arithmetic | evidence | N | keep | Invalid representation is not instrument noise. |
| E45 | scripts/prewindow_check.sh:34–38,189 | Readiness dwell and contamination sampling | Clean `600 s`; poll `30 s`; named process CPU `≤5%`; default timeout `45 min` | Settled machine | evidence | N | keep | Motivated by observed idle-triggered daemon contamination. |
| E46 | generated runsheet:1596,404 | G2-a stage settle | **`600 s`** | End operator/background activity before stages | evidence | N | keep | Actual emitted G2-a variable is 600 s; generic runbook prose says 180 s. |
| E47 | scripts/run_night.py:49,465 | During-chain census cadence | `30 s` | Detect newly active agents | evidence | N | keep | Operational observation cadence; not continuous-proof coverage. |
| E48 | scripts/run_night.py:48; measurement_liveness.py:55; scripts/validate_powermetrics_fiducial.py:131 | Probe/termination bounds | Probe `30 s`; identity `2 s`; sampler termination `10 s` | Avoid treating failed observation/teardown as success | evidence | N | keep | Resource/liveness guards, not metrology thresholds. |
| E49 | detection_floor.py:4540,4573 | Unknown transport terms or absent maxima | Any required term unknown | Transfer evidence | evidence | N | keep | Do not substitute permissive defaults. |
| E50 | envelope_gate.py:48; expected level constants | Envelope population | Eight distinct non-sentinel items at each L01/L08/L64 | Workload comparison basis | evidence | N | keep | Frozen workload design; unrelated to G2-a overlap count. |

### Operator-mistake guards

| # | file:line | Constant / expression | Value | Quantity protected | Class | Ratio | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| O01 | bundle_read.py:996,1123,2492; night_gate.py:270,310 | Numeric domain of counts/indices/plans | Integer, finite, nonnegative or positive as specified | Valid input structure | mistake-guard | N | keep | Catches ordinary malformed configs/records. |
| O02 | detection_floor.py:136,3008 | `_MAX_FLOOR_J` | `floor <1,000,000 J` | Magnitude sanity | mistake-guard | `1,000,000;200,000` | needs_ruling | No traced physical bound or decision for this universal ceiling. NR6. |
| O03 | scripts/gen_g2_phase_d.py:26,130,174 | Source-anchor/fence positions | Exact line/byte pins; five expected shell ranges | Correct generated chain | mistake-guard | N | keep | Prevents accidental source extraction drift; no measurement significance. |
| O04 | generated runsheet:503; scripts/run_campaign.py:8055 | Campaign failure cap | `--max-failures 1` | Avoid uncontrolled retries | mistake-guard | N | needs_ruling | With `set -e`, a large-probe failure can prevent post calibration. NR7. |
| O05 | adapters/powermetrics.py:928; scripts/run_night.py:1425 | Existing custody/attempt/lock refusal | Zero conflicting writers or prior one-shot records | Preserve evidence and avoid duplicate capture | mistake-guard | N | keep | Accidental reruns/collisions are in D-161’s retained threat model. |
| O06 | scripts/gen_g2_phase_d.py:64; night_gate.py:1060; floor_mint_estimator.py:175 | Input/chain/config/acceptance pin equality | Exact hashes and identities | Execute intended reviewed inputs | mistake-guard | N | keep | A wrong file/version is an operator mistake; hashes are not solely adversarial defenses. |
| O07 | scripts/validate_powermetrics_fiducial.py:1769; adapters/powermetrics.py:1465 | Countdown/count configuration | Countdown ≥0; idle count ≥1; live chain countdown 20 s, display wait 5 s | Valid arming/capture setup | mistake-guard | N | keep | Operational parameter validation. |
| O08 | scripts/prewindow_check.sh:145 | Disk headroom | At least `20 GB` | Complete on-disk capture | mistake-guard | N | keep | Script documents several-GB windows; ample storage margin. |

No inspected guard could confidently be classified as **deliberate-only** without also defending an ordinary wrong-file, duplicate-run, post-hoc-choice, or missing-evidence mistake. Accordingly, this report does not invent a D-161 retirement. Candidate custody simplifications belong to THREAT-MODEL-PRUNE-01.

## B. RE-SET proposals, ranked by G2-a relevance

These are proposals only. Arithmetic witnesses were executed; repository regressions were not.

### R1 — Admission timing allowance: 1 ns → 1 μs

**Rows:** M38–M39. Highest direct relevance: these checks can invalidate otherwise usable captured members during strict reduction.

The producer sums native elapsed intervals for `baseline.duration_s`, while the controller records separately rounded epoch endpoints (`adapters/powermetrics.py:334`; `controller.py:1113`). The comparison therefore combines different numerical representations.

At epoch 1,789,000,000 s:

- One ULP is 0.238418579 μs.
- Four ULPs are 0.953674316 μs.
- **1 μs** matches the already documented representation allowance in `uncertainty_evidence.py:45–59`.
- At an illustrative 10 W, 1 μs is **0.00001 J**, ratios **0.00001; 0.000002** to the requested scales. Actual energy exposure is \(P_{\max}·10^{-6}\) J.
- This does **not** authorize a missing 100–115 ms sample.

```diff
--- a/joulewise/environment_admission.py
+++ b/joulewise/environment_admission.py
@@
 MAX_ADMISSION_GAP_S = 600.0
+# Covers four contemporary epoch-binary64 roundings, not missing samples.
+ADMISSION_TIME_ROUNDING_S = 1e-6
@@
-                or baseline_duration_s > attempt_end_s - attempt_start_s + 1e-9
+                or baseline_duration_s > attempt_end_s - attempt_start_s + ADMISSION_TIME_ROUNDING_S
@@
-                capture[0] < attempt_start_s - 1e-9
-                or capture[1] > attempt_end_s + 1e-9
+                capture[0] < attempt_start_s - ADMISSION_TIME_ROUNDING_S
+                or capture[1] > attempt_end_s + ADMISSION_TIME_ROUNDING_S
```

**Defect-shaped regression:**

1. Otherwise valid admission: start `1789000000.0`, true interval sum `30.00000001`, stored end `float(start+duration)`. Stored epoch subtraction yields `30.0`; current duration gate rejects the 10 ns discrepancy. Proposed gate admits.
2. Endpoint variants one epoch ULP outside the reconstructed attempt boundary pass the numerical containment check.
3. A baseline exceeding the attempt by **10 μs**, or a capture endpoint outside it by **one actual sample interval**, still refuses.
4. Preserve unrelated failures: missing timestamps, nonpositive elapsed intervals, absent thermal coverage, and stale admission remain refused.

**Contract amendment:** In `docs/contracts/measurement_methodology.md`, environment admission, specify that numerical containment allows at most 1 μs of epoch-representation discrepancy, without crediting unobserved time. Retain the positive-duration and causal-containment requirements.

For epochs outside the currently documented ULP range, use a checked ULP-derived allowance rather than silently assuming this fixed number remains sufficient.

### R2 — Make later trace coverage agree with the existing endpoint-ULP rule

**Row:** M41. Direct strict-reducer relevance, but requires a near-boundary tail.

The preceding gate at `reduce.py:1888` deliberately accepts one endpoint ULP below `fsum(window.end,B)`. `_anchor_coverage_ok` then uses subtraction and zero slack, so the same accepted tail can fail later.

Executed witness:

```text
window.end = 1789000000.0001
B          = 0.009724
tail       = 1789000000.0098236
```

The tail is one ULP below the rounded required endpoint. The earlier tail gate accepts it; `tail-B < window.end` is true by one ULP.

Use the same endpoint comparison at both edges:

```diff
--- a/joulewise/reduce.py
+++ b/joulewise/reduce.py
@@
         for window in windows:
-            if trace_start_s + bound_s > window.start_s:
+            required_start_s = math.fsum((window.start_s, -bound_s))
+            required_end_s = math.fsum((window.end_s, bound_s))
+            if trace_start_s > required_start_s + math.ulp(required_start_s):
                 return False
-            if trace_end_s - bound_s < window.end_s:
+            if trace_end_s < required_end_s - math.ulp(required_end_s):
                 return False
```

**Allowance:** One endpoint ULP, currently **0.238418579 μs**. At 10 W: **2.38418579×10⁻⁶ J**, ratios **2.38418579×10⁻⁶; 4.76837158×10⁻⁷**.

**Defect-shaped regression:**

- The witness above passes both coverage gates after repair.
- A tail **two representable endpoint steps** below the required endpoint still fails.
- A complete missing sample still fails.
- Exercise the symmetric left-edge boundary.

**Contract amendment:** In `docs/contracts/run_bundle_layout.md`, the sentence requiring edge coverage under every admissible shift should state that endpoint coverage uses the same one-ULP arithmetic allowance throughout the current reducer. It must not imply permission to extrapolate a missing interval.

### R3 — Cooldown completion: replace sub-ULP slack with an arithmetic error allowance

**Row:** M37. Lower likelihood than R1: a boundary miss normally causes another probe rather than immediate loss, but can affect cap-adjacent release.

For span completion, use **1 μs**. Coverage is a sum of endpoint differences; its allowance should account for the number of retained contributions rather than assuming a single subtraction.

```diff
--- a/joulewise/controller.py
+++ b/joulewise/controller.py
@@
         weighted_sum = 0.0
         coverage_s = 0.0
+        coverage_rounding_s = 0.0
@@
             overlap_s = max(0.0, evidence_end - clipped_start)
             weighted_sum += overlap_s * value
             coverage_s += overlap_s
+            if overlap_s > 0.0:
+                coverage_rounding_s += (
+                    math.ulp(evidence_end) + math.ulp(clipped_start)
+                )
@@
-        span_complete = window_span_s + 1e-9 >= selected.sustained_window_s
-        coverage_complete = coverage_s + 1e-9 >= required_coverage_s
+        span_complete = window_span_s + 1e-6 >= selected.sustained_window_s
+        coverage_slack_s = max(
+            1e-6, coverage_rounding_s + math.ulp(coverage_s)
+        )
+        coverage_complete = coverage_s + coverage_slack_s >= required_coverage_s
```

For six retained contributions, the conservative endpoint allowance is about **2.86 μs** at contemporary epochs. This remains millions of times smaller than the 24-second coverage requirement. It is an arithmetic bound, not a cadence-sized relaxation.

**Defect-shaped regression:**

- A span represented as `29.99999976158142` s satisfies the repaired 30 s boundary; current 1 ns slack rejects it.
- Construct six nominal four-second coverage contributions with an aggregate inward endpoint-rounding discrepancy; a deficit within the calculated allowance passes.
- A **10 μs** deficit with only six contributions still fails; a missing sample certainly fails.
- **Recovery first achieved at or after 300 s remains `cap_hit`.** Do not move or soften the deadline.

**Contract amendment:** Amend the complete-span/80%-coverage sentence in `docs/contracts/measurement_methodology.md:285` to distinguish numerical rounding allowance from observed coverage. Preserve the 30 s, 80%, power, thermal, and cap-first semantics.

### R4 — Repair the load-transition midpoint arithmetic, retain its tight identity check

**Row:** I17. Definite defect, but **not a current G2-a acceptance path**.

Current producer:

```python
(response_start_s + response_end_s) / 2 - marker_s
```

Current validator:

```python
((response_start_s - marker_s) + (response_end_s - marker_s)) / 2
```

These are mathematically equal but numerically different. The executed example in V2 differs by **1.1920928955×10⁻⁷ s**, over 100,000 times the validator’s 1e-12 allowance.

The preferable repair is to give producer and validator the same arithmetic path:

```diff
--- a/joulewise/load_transition_alignment.py
+++ b/joulewise/load_transition_alignment.py
@@
-    offset_s = (response_start_s + response_end_s) / 2.0 - marker_s
+    offset_s = (support_start_offset_s + support_end_offset_s) / 2.0
```

**Proposed tolerance:** Keep **1e-12 s** after aligning the arithmetic. This becomes an honest identity check. No physical tolerance increase is needed.

**Defect-shaped regression:**

- An otherwise valid eight-transition observation set with epoch-sized markers and a response support at marker+0.1 to marker+0.2 s must emit an artifact accepted by its validator.
- Mutating only an emitted `offset_s` by **1 μs**, while preserving its support endpoints, must still fail.
- Validate residuals and direction centers too; they must derive from the corrected offsets.

**Contract amendment:** `docs/contracts/load_transition_alignment.md` already defines `offset=(a+b)/2`. Add that the implementation first forms the endpoint offsets `a,b`, then takes their midpoint. The manifest phrase `response_sample_midpoint_s-marker_epoch_s` needs review as mathematically equivalent wording; preserve frozen historical bytes.

## C. KEEP summary and arithmetic-path qualifications

The table contains **156 predicate/parameter rows**:

| Class | Total | Keep | Re-set | Needs ruling |
|---|---:|---:|---:|---:|
| identity | 36 | 33 | 1 | 2 |
| measurement | 62 | 56 | 4 | 2 |
| evidence | 50 | 49 | 0 | 1 |
| mistake-guard | 8 | 6 | 0 | 2 |
| deliberate-guard | 0 | 0 | 0 | 0 |
| **Total** | **156** | **144** | **5** | **7** |

The five re-set rows form four repair proposals because R1 covers two predicates.

Identity checks whose sides are **not literally the same arithmetic path**:

- **I03:** Same primary bytes can be processed by different estimator revisions. A widened fresh bound is already accepted; fitted-edge containment remains a separate compatibility question.
- **I05:** Rail aggregation versus raw combined-power construction. The relative tolerance covers arithmetic order, not independent sensors.
- **I06–I08:** Different anchors and epoch subtraction/cumulative addition. Existing 1 μs allowance is appropriate at the documented epoch scale.
- **I17:** Different midpoint/epoch subtraction order. Demonstrated defect; align arithmetic.
- **I22:** Different discrete contingency tables can produce mathematically tied chi-square values. The subtraction of 1e-12 makes the permutation comparison include numerical ties. It does not demand picounit instrument precision.
- **I23–I24:** Duplicate event-time representations/authentication paths. Their broad one-second limit must not be confused with the much tighter physical anchor bound.
- **I25:** Decimal high-precision recomputation followed by specified presentation rounding.
- **I26–I27:** Decimal values converted to binary64 and recomposed. At the tens-of-milliseconds bound scale, 1e-12 s comfortably exceeds the conversion/addition error.
- **I30:** Direct ABBA arithmetic versus zero-shift integration/contrast construction. Cancellation makes a contrast-relative tolerance suspect; see NR2.
- **I34:** ISO microsecond serialization versus epoch binary64.

The enormous ratio between instrument uncertainty and an identity epsilon is **not itself a defect**. In particular, do not expand I01, I04, I28, I29, I31, or I32 to 0.1–1 J merely because the instrument is attribution-limited.

## D. Anomalies, reachability, and boundaries

1. **A real arithmetic mismatch exists outside G2-a:** load-transition midpoint production/validation, R4. The fixture-oriented epoch scale can hide it.

2. **The source already contains the precedent needed for R1/R3.** `uncertainty_evidence.py:45–59` explicitly explains why predecessor 1 ns padding was insufficient and why 1 μs covers four contemporary epoch roundings. This is not a proposal to improve the physical instrument.

3. **Calibration documentation still quotes obsolete 10 ms production drift.** `docs/contracts/powermetrics_fiducial.md`, “Claim-bearing calibration bracket,” and `docs/contracts/run_bundle_layout.md:637` say production tolerance 0.010 s. Current `calibration_bracketing.py:1520` explicitly labels that policy field `legacy_obsolete_not_an_acceptance_comparator`. Active acceptance uses:
   - screen **9.724 ms**;
   - maximum budgetable drift **10.164834758 ms**;
   - preflight level **32.898493715 ms**;
   - allowance **max(observed drift, screen)**, added once.

   The excess budget **0.440834758 ms** is the difference between screen and maximum, not an additional independent refusal.

4. **D-125 lineage-floor conflict remains live.** The current queue’s `S9-05-CAL-SCREEN-FLOOR-RULING-01` records the conflict between a predecessor 10.818 ms lower bound and the active 9.724 ms screen. This scout must not silently resolve it.

5. **Long decimals are being conflated with sensitivity in the motivating concern.** Calibration code’s **1e-18 presentation quantum** and **1e-15 preflight-screen quantum** authenticate a derivation. Neither asks the instrument to distinguish femtoseconds. Changing their spelling alone would break issued identities without fixing metrology.

6. **G2-a is diagnostic, but uses production acquisition guards.** Source chain:
   ```text
   LaunchAgent template
     → scripts/run_night.py
     → night_gate.evaluate and agent/quiet/plan checks
     → authenticated emitted zsh chain
     → input-inventory check and ledger readiness/reservation
     → settle
     → governed pre-calibration writer and preflight screen
     → eight stages: small/large × four prompt lengths
     → run_campaign → controller/admission → powermetrics → bundle reduction/finalization
     → governed post-calibration
     → terminal physical-ahead record
     → G2-a count summarizer
   ```
   The lead-owned selector runs later. Neither G2-a results nor alignment fixtures thereby become claim-bearing floors.

7. **Actual emitted settle is 600 s.** The generator includes runsheet lines 1534–1598, where `SETTLE_S=600`. The generic runbook describes 180-second stage settles. This changes duration, not numeric admission sensitivity; deployment should follow the emitted bytes.

8. **Large-model “non-gating” has a control-flow qualification.** Both roles use `set -e` and `--max-failures 1`; a large-probe failure can stop before post-calibration. The summarizer also requires large-member completeness. NR5/NR7 distinguish scientific selection from operational stopping.

9. **Transport envelopes are hard evidence-domain boundaries.** Their zero extra tolerance compares different physical collections. That does not automatically make them “microscopic”: relaxing an empirical min/max envelope invents transfer authority. Actual artifact values were not supplied, so M45–M52 correctly remain artifact-dependent rather than filled with invented numbers.

10. **Parameters without a traced quantitative physical derivation:** `_MAX_FLOOR_J=1e6`; the GPU 0.80/0.40/800 MHz screens; Huber 1.345, half-flat-loss screen, and `max(1,0.05·loss)` region increment; projection search step choices. Most are frozen estimator/operational definitions with clear roles, but their exact values should not be presented as independently calibrated confidence guarantees. `_MAX_FLOOR_J` needs a disposition.

11. **The detector budget was previously a genuinely silly operational gate—and was repaired.** D-143 records that the old 100,000-cell cap rejected all examined real corpus-grade fits. Current **165,000** is based on **34 complete convergences**, max **137,189**. The older D-078 body still narrates 100,000; use its dated successor.

12. **Non-gates must remain non-gates:** 64u energy enclosures and four-ULP outward rounding in `detection_floor.py:1236` are conservative arithmetic padding; window-duration receipt margins can be negative; E5 is advisory; attribution-limited classification preserves the widened-floor path. None should become a new acceptance test.

13. **Seat B handoff, without adjudicating its implementations:**
   - `uncertainty_evidence.py:35–41`: wall/monotonic span, parse lag, affine residual, rate deviation, baseline, rollover and effective-anchor caps.
   - `uncertainty_evidence.py:59,65–66`: numerical padding and raw energy/power consistency tolerances.
   - `aggregate.py:78`: Student-t critical values used by floor computation.
   - `whole_window.py:5670`: whole-window refusal dispatch.
   - `floor_extraction.py:58–70`: calls into `analysis_engine.inputs` prechecks and deterministic bounds.
   - `floor_extraction.py:99,470`: shared-width composition delegated to `dominance_closeout`.
   - `reduce.py:65–69`: idle-dependence calculation.
   - Production policy’s **0.05 J / 0.25 NEG-8 literals** reach the whole-window chain; seat B must distinguish obsolete/default literals from governed derived bounds. The 0.05 J literal alone has ratios **0.05;0.01**, but is not enough to establish the operative bound.

14. **Read limitations:** Every assigned source module and named contract was accessible. An initially guessed G2 runsheet path did not exist; the generator’s actual runsheet path was subsequently read. An unmatched exploratory `common_mode*.py` glob was replaced by the actual import pointer to `dominance_closeout`. No inaccessible assigned source remained. Installed LaunchAgent/plan/chain parity was not inspected; the report does not certify those external bytes.

## E. NEEDS_RULING items

### NR1 — What replay difference is allowed across fiducial estimator revisions?

- **Question:** Must a newly fitted point always remain in an old declared residual interval, and should the two consumers use identical slack?
- **Options:** Preserve point-containment exactly; align both to numerical ULP hygiene; define an explicit revision-compatible enclosure rule.
- **Recommendation:** Align consumer behavior and retain exact/ULP identity semantics for the same estimator. Require a versioned rule before admitting a fit moved by a changed estimator. Do **not** substitute one cadence or 1 J of tolerance.
- **Blocked work:** Definitive keep/re-set disposition for I03.

### NR2 — What numerical domain should govern zero-point/ABBA agreement?

- **Question:** Is `1e-9·abs(contrast)` an honest replay bound when large member energies nearly cancel?
- **Options:** Keep the current band; use a forward-error bound based on member integral magnitudes; unify the arithmetic paths.
- **Recommendation:** Prefer shared arithmetic; otherwise derive the comparison from the existing **64u·S** enclosure machinery and its actual operation count. Preserve separately charged zero-center divergence. Seat B owns the shared composition judgment.
- **Blocked work:** Definitive disposition and defect regression for I30.

### NR3 — Which calibration screen lineage rule governs this generation?

- **Question:** Does D-125’s 10.818 ms inherited floor still bind the active n=17 screen?
- **Options:** Retain 9.724 ms through an explicit superseding ruling; enforce a lineage-monotone floor and reissue dependents.
- **Recommendation:** Resolve through the existing `S9-05-CAL-SCREEN-FLOOR-RULING-01`; do not make a local numeric edit during this sweep.
- **Blocked work:** Declaring M32 fully justified under both code and governing policy.

### NR4 — How are real load-transition supports normalized?

- **Question:** Will the future real-Mac normalizer copy shared endpoints exactly, or independently derive them using epoch arithmetic?
- **Options:** Require canonical shared endpoints; admit a proved rounding allowance; allow physical overlaps under a different model.
- **Recommendation:** Canonical shared supports, with at most a justified numerical allowance. Do not permit cadence-sized overlap without changing the model.
- **Blocked work:** Final disposition of M54 before P2-046B; does not block G2-a itself.

### NR5 — Does non-gating large-model evidence have to be complete?

- **Question:** Can small-model G2-a selection proceed when a large-model diagnostic rung is absent or failed?
- **Options:** Require complete diagnostics; allow explicit unavailable large rows while retaining all small evidence.
- **Recommendation:** Allow typed diagnostic unavailability for selection, subject to NR7’s acquisition-integrity distinction. Never manufacture counts.
- **Blocked work:** Summarizer/completeness semantics for E39.

### NR6 — What authorizes the universal 1 MJ floor ceiling?

- **Question:** Is it a registered supported-domain limit or an arbitrary sanity guard?
- **Options:** Document a supported window/power domain; replace with a derived domain bound; remove the finite ceiling while retaining finite/nonnegative checks.
- **Recommendation:** Use a documented domain bound if one exists; otherwise avoid treating 1 MJ as physics. Low immediate G2-a priority.
- **Blocked work:** Keep/removal disposition for O02.

### NR7 — Should a failed large diagnostic prevent post-calibration?

- **Question:** Does “large probes never gate” permit continuing the bracket after a large diagnostic’s failure?
- **Options:** Abort on every stage failure; continue only for explicitly non-contaminating diagnostic failure classes; always continue.
- **Recommendation:** Preserve abort for contamination, missing sampler/custody, and uncertain machine state. Consider typed continuation for safe diagnostic-only failure, retaining failure evidence and collecting post-calibration. Never unconditional `|| true`.
- **Blocked work:** Exact chain change and regression for O04.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| R1 admission rounding | start_now | Lead accepts proposal | `environment_admission.py`, admission contracts/tests |
| R2 coverage consistency | start_now | Coordinate with seat B’s anchor findings | `reduce.py`, coverage tests |
| R3 cooldown rounding | start_now | Lead accepts bounded arithmetic rule | `controller.py`, cooldown contracts/tests |
| R4 midpoint arithmetic | start_now | Historical-artifact disposition if any exist | `load_transition_alignment.py`, alignment tests |
| NR1–NR7 | needs_ruling | Lead adjudication | Estimator, screen lineage, diagnostic semantics |
| First G2-a number consumption | wait_for | Integrated sweep and required refuters | Claim/input-consumption boundary |
| Live acquisition | do_not_start | Clean lead-controlled QUIET-MAC session | Machine state |

## Critical path

R1–R3 and the G2-a-relevant rulings feed the integrated sweep before number consumption. R4 is independently repairable and must precede real load-transition use. Accepted source changes that participate in authenticated estimator or chain hashes require the lead to refresh their governed dependent artifacts before deployment.