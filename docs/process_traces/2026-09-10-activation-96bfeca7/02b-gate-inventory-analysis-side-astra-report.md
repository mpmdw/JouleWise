```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "Seat B inventory found one demonstrated arithmetic-scale refusal in D-165, no demonstrated microscopic measurement tolerance, and two capture-duration questions requiring lead/seat-A follow-up.",
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
        "row": "B1-D165-zero-point",
        "action": "needs_ruling",
        "wait_for": "Lead disposition of the registered D-124 provenance band and coordinated seat-A predicate",
        "collision_surface": "joulewise/dominance_closeout.py:963; joulewise/floor_extraction.py:590"
      },
      {
        "row": "B2-capture-duration",
        "action": "wait_for",
        "wait_for": "Seat A establishes the complete sampler span of prospective G2-a captures against the 60-second anchor requirement",
        "collision_surface": "joulewise/uncertainty_evidence.py:977 and capture configuration/controller"
      },
      {
        "row": "B3-idle-count",
        "action": "wait_for",
        "wait_for": "Seat A checks requested idle sample counts against the exact three-bandwidth predicate",
        "collision_surface": "joulewise/idle_dependence.py:267 and idle capture sizing"
      },
      {
        "row": "B4-preserved-gates",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "Lead may incorporate the KEEP inventory; no worker edits authorized"
      },
      {
        "row": "B5-deliberate-only",
        "action": "do_not_start",
        "wait_for": "THREAT-MODEL-PRUNE-01",
        "collision_surface": "Private in-process paper-custody construction guards"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "wc -l joulewise/whole_window.py joulewise/analysis_engine/*.py joulewise/uncertainty_evidence.py joulewise/dominance_closeout.py joulewise/idle_dependence.py joulewise/aggregate.py joulewise/salvage_dangler.py joulewise/cli.py joulewise/paper_*.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["   30674 total"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "30674 total"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -c 'import math; epoch=1789068000.0; print(\"epoch_ulp_s=\", math.ulp(epoch)); print(\"four_epoch_ulps_s=\", 4*math.ulp(epoch)); print(\"nanosecond_pad_changes_epoch=\", epoch+1e-9 != epoch); print(\"counter_gate_at_1J=\", 0.002+0.001*1.0); print(\"counter_gate_at_5J=\", 0.002+0.001*5.0); print(\"idle_n_min_at_100ms=\", 3*(math.floor(10.0/0.1)+1)); print(\"idle_n_min_at_115ms=\", 3*(math.floor(10.0/0.115)+1)); a1,b1,b2,a2=20000.1,20000.3,20000.0,20000.2; d=(b1+b2-a1-a2)/2; z=math.fsum([-0.5*a1,0.5*b1,0.5*b2,-0.5*a2]); s=0.5*math.fsum([a1,b1,b2,a2]); print(\"abba_sanity=\", {\"delta\":d,\"zero\":z,\"gap\":abs(d-z),\"old_accepts\":math.isclose(d,z,rel_tol=1e-9,abs_tol=1e-12),\"member_pad\":64*(math.ulp(1.0)/2)*s})'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "epoch_ulp_s= 2.384185791015625e-07",
          "four_epoch_ulps_s= 9.5367431640625e-07",
          "nanosecond_pad_changes_epoch= False",
          "counter_gate_at_1J= 0.003",
          "counter_gate_at_5J= 0.007",
          "idle_n_min_at_100ms= 303",
          "idle_n_min_at_115ms= 261",
          "abba_sanity= {'delta': 1.8189894035458565e-12, 'zero': 0.0, 'gap': 1.8189894035458565e-12, 'old_accepts': False, 'member_pad': 2.842192259322474e-10}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "old_accepts.*False.*member_pad.*2.842192259322474e-10"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-165 rejects a demonstrated disagreement between two arithmetic paths at large member-energy scale. The current tolerance is explicitly registered by D-124, and an upstream seat-A predicate duplicates it.",
      "needs": "Rule on the proposed member-scale identity tolerance before declaring this sweep closed."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests, imports of project code, live captures, or Git operations were run. The D-165 counterexample is sanity arithmetic, not an executed end-to-end fixture.",
      "needs": "Lead implements and runs defect-shaped regression if B1 is adopted."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git identity and dirty-state inventory were not obtained because this prompt prohibits all Git operations. Empty unowned_dirty means unexamined, not clean.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The current anchor requires a complete raw-record baseline of at least 60 seconds. Seat B did not establish that every prospective G2-a sampler lifetime supplies it; the 30-second idle configuration also needs checking against the exact three-bandwidth sample rule.",
      "needs": "Seat A verifies capture sizing without changing these registered evidence requirements merely to admit a short capture."
    },
    {
      "id": "F5",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The September 4 D-078/D-083 addenda supersede F+B as a joint clearable-effect description. The requested 1 J and 5 J figures are retained only as comparison scales.",
      "needs": "Use current separate-gate wording when filing the report."
    }
  ]
}
```

## A. Gate inventory

**Finding:** no inspected physical-reading comparison demonstrated the requested “microscopic measurement tolerance” defect. One **identity** comparison does have a demonstrated arithmetic-scale defect: D-165’s zero-point/ABBA-delta comparison. Its demonstrated counterexample uses approximately 20,000 J members; this is **not evidence of a real G2-a refusal**.

This is a logical-predicate inventory. Repeated implementations of the same predicate are cited together; schema field names and repeated propagation of another module’s refusal are not counted as new numeric gates. The unresolved cross-footprint dependencies below prevent certifying the whole claim path complete.

Paths below are relative to `joulewise/`. `AE/` means `analysis_engine/`.

**Scales and notation**

- **1 J** is the requested D-078 clause-11 attribution comparison scale; approximately **0.3 J** repeatability is not substituted for it.
- **5 J** is the requested historical planning comparison scale. Current D-078/D-083 addenda at `docs/decision_log.md:10942` and `:10965` explicitly make F+B non-gating. For symmetric intervals, the numerical conjunction is `|estimate| > max(F, h+B)`, alongside eligibility and multiplicity.
- Requested cadence is `max(1, round(1000/power_hz))` milliseconds: `adapters/powermetrics.py:1461`. The inspected `_v5` generator requests **10 Hz**, hence **100 ms**; protocol v3 also pins 100 ms. The fiducial contract describes observed cadence of approximately **115 ms** at `docs/contracts/powermetrics_fiducial.md:126`.
- Native plist timestamps are **whole-second quantized**, not nanosecond observations: `uncertainty_evidence.py:74`, `:909`; fiducial contract `:213`. Integer nanosecond storage does not improve that physical timestamp resolution.
- `J(x)` in the ratio column means **x / x÷5**, respectively relative to 1 J and 5 J. For example, `J(1e-12)` means `1e-12 / 2e-13`.
- `τ(r,a)` means `max(a, r × max(|left|, |right|))`, the `math.isclose` tolerance.
- **N/A** means **“n/a: not an energy.”** For J/token or J², dividing directly by 1 J would be dimensionally wrong.
- “Keep” on a diagnostic means retain its computation, **not** promote it into an acceptance gate.

### Identity checks and arithmetic hygiene

| # | file:line | constant / expression | value | Quantity protected | Class | Ratio to 1 J / 5 J | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| I01 | whole_window.py:810,4386 | Stored calibration scalar versus authenticated scalar | abs 1e-9 s | Calibration provenance | identity | N/A | keep | Same calibration value, not pre/post calibration drift. |
| I02 | whole_window.py:823,4615 | `operative > minted + 1e-12` | 1e-12 s | Whether authenticated widening requires replay | identity | N/A | keep | Algebraic dominance dispatch; current path re-reduces instead of treating drift as noise. |
| I03 | whole_window.py:901 | Operative point equals minted point | Exact | Energy point under widened uncertainty | identity | J(0) | keep | Widening the domain must preserve the zero-shift observation. |
| I04 | whole_window.py:903 | Operative lower endpoint cannot increase | 1e-12 J | Envelope containment | identity | J(1e-12) | keep | Nested uncertainty domains, not two measurements. |
| I05 | whole_window.py:905 | Operative upper endpoint cannot decrease | 1e-12 J | Envelope containment | identity | J(1e-12) | keep | Same nested-domain invariant. |
| I06 | whole_window.py:907 | Operative half-width cannot decrease | 1e-12 J | Envelope containment | identity | J(1e-12) | keep | Recomputed conservative width; no instrument noise tolerance needed. |
| I07 | whole_window.py:3463 | Envelope point versus gross metric | τ(1e-9,1e-12) J | Same gross observation | identity | J(τ) | keep | Same bundle’s zero-shift energy. |
| I08 | whole_window.py:3531 | Stored versus fresh gross point/lower/upper | τ(1e-9,1e-9) J per field | Reducer replay | identity | J(τ) | keep | Same primary bytes and recorded reducer version. |
| I09 | whole_window.py:3540 | Stored versus fresh idle-subtracted point | τ(1e-9,1e-9) J | Reducer replay | identity | J(τ) | keep | Repeats the same reduction, not a second idle reading. |
| I10 | whole_window.py:4536 | Persisted endpoint maximum versus `max(pre,post)` | abs 1e-12 s | Bracket arithmetic | identity | N/A | keep | Recomputed maximum of the same endpoints. |
| I11 | whole_window.py:4542 | Decimal allowance string versus float projection | abs 1e-12 s | Allowance projection | identity | N/A | keep | One Decimal-produced value with two representations; D-124 audit explicitly covers it. |
| I12 | whole_window.py:4548 | Persisted operative bound versus endpoint + allowance | abs 1e-12 s | Once-composed bracket | identity | N/A | keep | Decimal-sum projection versus sum of projected operands; see C. |
| I13 | whole_window.py:4573 | Session operative bound versus expected operative | abs 1e-12 s | Authenticated consumption | identity | N/A | keep | Same governed bracket value. |
| I14 | whole_window.py:4608,4614 | Member operative matches session and is not below minted | abs 1e-12 s | Nonshrinking consumption bound | identity | N/A | keep | Alias agreement and arithmetic ordering. |
| I15 | whole_window.py:4634 | Recorded versus reconstructed half-width | abs 1e-12 J | Envelope serialization | identity | J(1e-12) | keep | Same `max(point−lower, upper−point, max_abs_delta)` calculation. |
| I16 | AE/inputs.py:1976 | Floor member metric versus strict summary | τ(1e-12,1e-12) J | Floor evidence linkage | identity | J(τ) | keep | Copied measurement value from the same strict source. |
| I17 | AE/inputs.py:3458 | `max_abs_delta` covers endpoint reach | abs 1e-12 J | Internal envelope consistency | identity | J(1e-12) | keep | Arithmetic undercoverage check, not another physical reading. |
| I18 | idle_dependence.py:333 | Baseline mean versus raw-derived mean | τ(1e-9,1e-12) W | Idle metadata identity | identity | N/A | keep | Same raw rails and version-selected estimator. |
| I19 | idle_dependence.py:333 | Baseline standard deviation versus raw-derived value | τ(1e-9,1e-12) W | Idle metadata identity | identity | N/A | keep | Same weighted variance helper and square root. |
| I20 | idle_dependence.py:333 | Baseline duration versus summed elapsed durations | τ(1e-9,1e-12) s | Idle metadata identity | identity | N/A | keep | Same native elapsed fields. |
| I21 | idle_dependence.py:332 | Baseline sample count versus raw count | Exact integer | Idle record census | identity | N/A | keep | Counts are discrete; noise cannot excuse a missing record. |
| I22 | dominance_closeout.py:898 | Shared bound versus authenticated operative bound | abs 1e-12 s; rel 0 | Replay provenance | identity | N/A | keep | D-124 explicitly establishes production single-sourcing. |
| I23 | dominance_closeout.py:963 | Zero-shift replay versus stored ABBA delta | τ(1e-9,1e-12) J | Arithmetic provenance | identity | J(τ) | **needs_ruling** | Different arithmetic paths; demonstrated false refusal at large member scale. B1 proposes re-set. |
| I24 | dominance_closeout.py:961 | Explicit zero point belongs to both sweeps | Exact | Sweep reference identity | identity | J(0) | keep | Builder inserts the very same zero-point value; D-124 forbids approximate identity substitution. |
| I25 | dominance_closeout.py:1848 | Sidecar delta versus sealed floor delta, `_close` | `min(max(1e-12,1e-12|x|),1e-6)` J | Copied block observation | identity | J(tolerance) | keep | Unlike I23, these are copies of the same block delta. |
| I26 | dominance_closeout.py:1109,1148,1357,2278 | Stored result/split versus fresh canonical result | Exact mappings | D-165 result replay | identity | J(0) for energy fields | keep | Calls the same production arithmetic; rejects stale or substituted results. |
| I27 | AE/artifact.py:689 | Repeat/metrology CI equals center ± critical×SE | τ(1e-12,1e-12) | Interval arithmetic | identity | J(τ), or N/A for ratios | keep | Same endpoint construction. |
| I28 | AE/artifact.py:702 | Decision interval equals metrology CI ± B | τ(1e-12,1e-12) | Single deterministic widening | identity | J(τ), or N/A | keep | Prevents changed signs or repeated widening. |
| I29 | AE/artifact.py:711 | `SE_total² = SE_repeat² + SE_metrology²` | τ(1e-12,1e-12) in squared units | Variance composition | identity | N/A | keep | `hypot` versus squared reconstruction; legitimate roundoff allowance. |
| I30 | AE/artifact.py:2085 | `SE_repeat = s_d/√n` | τ(1e-12,1e-12) | Repeat SE | identity | J(τ), or N/A | keep | Same formula and operands. |
| I31 | AE/artifact.py:2095 | Critical equals rounded Student-t quantile | abs 1e-12; rel 0 | Registered critical | identity | N/A | keep | Producer and validator both round the same quantile to three decimals. |
| I32 | AE/artifact.py:2158 | `SE_metrology²` versus sum of variance contributions | τ(1e-12,1e-12) in squared units | Metrology variance | identity | N/A | keep | Different summation/square-root paths, but same nonnegative terms. |
| I33 | AE/artifact.py:2193 | Deterministic total versus term sum | **default rel 1e-9**, abs 1e-12 | Total B | identity | J(τ), or N/A | keep | Important implicit default; producer uses `fsum`, validator uses `+=`. |
| I34 | AE/artifact.py:2360 | Resolution gate equals max(abs,cmp) | abs 1e-12; rel 0 | Floor selection | identity | J(1e-12) | keep | Same operands, exact maximum semantics. |
| I35 | AE/artifact.py:2506 | V3 active floor equals max(two arm gates) | abs 1e-12; rel 0 | Cross-stack floor composition | identity | J(1e-12) | keep | Registered max, not an additive physical allowance. |
| I36 | AE/artifact.py:2690 | Absolute floor equals resolution aggregate | abs 1e-12; rel 0 | Absolute floor aggregation | identity | J(1e-12), or N/A | keep | Max for absolute-energy path; sum for ratio path. |
| I37 | AE/artifact.py:2703 | Comparative floor equals resolution aggregate | abs 1e-12; rel 0 | Comparative floor aggregation | identity | J(1e-12), or N/A | keep | Same registered aggregation as producer. |
| I38 | AE/artifact.py:2716 | Active floor equals derived aggregate gate | abs 1e-12; rel 0 | Operative floor | identity | J(1e-12), or N/A | keep | Internal arithmetic cross-check. |
| I39 | AE/artifact.py:2730 | Active floor equals component maximum | abs 1e-12; rel 0 | Operative floor alias | identity | J(1e-12), or N/A | keep | Internal maximum identity. |
| I40 | AE/artifact.py:3269 | LOO CI midpoint versus estimate | τ(1e-12,1e-12) | LOO serialization | identity | J(τ), or N/A | keep | Inverts endpoint arithmetic; conditioning caveat in C/D. |
| I41 | AE/artifact.py:3297 | LOO p-value re-derived from CI width | τ(1e-12,1e-12) | LOO inference replay | identity | N/A | keep | Different arithmetic path; no demonstrated failure here. |
| I42 | AE/artifact.py:834,870 | Original p-value versus estimate/SE/df or TOST | τ(1e-12,1e-12) | Statistical-result identity | identity | N/A | keep | Same statistical function and inputs. |
| I43 | AE/artifact.py:730,3142,3156,3249 | Family/contrast/LOO adjusted p agreement | τ(1e-12,1e-12) | Multiplicity replay | identity | N/A | keep | Copied/recomputed probabilities, not measurement tolerances. |
| I44 | AE/artifact.py:2496,2638 | Arm/declared-cell floor versus resolved floor | τ(1e-12,1e-12) | Floor linkage | identity | J(τ), or N/A | keep | Same resolved source quantity. |
| I45 | AE/claim_side_bound.py:176 | Every copied numeric token equals source token | Exact numeral bytes | Claim-side provenance | identity | J(0), or N/A | keep | D-178 expressly distinguishes `4`, `4.0`, and `4e0`; no physical reading is compared. |
| I46 | AE/claim_side_bound.py:216 | Optional B/interval arithmetic diagnostic | τ(1e-12,1e-12) | Diagnostic arithmetic | identity | J(τ), or N/A | keep | **Not an acceptance gate**; contract explicitly says so. |
| I47 | paper_reported_energy.py:406 | Projection digest versus canonical recomputation | Exact | Reported mean and interval | identity | J(0) for energy fields | keep | D-179 pins the floating-point calculation, not merely algebraic equivalence. |
| I48 | cli.py:653,703 | Fresh versus stored summary | Exact parsed values | Versioned reducer replay | identity | J(0) for energy fields | keep | Frozen additive-absence exceptions are schema compatibility, not numeric tolerances. |
| I49 | cli.py:1310,1314 | Stored clock/sample-phase objects versus derivation | Exact | Timing evidence replay | identity | N/A | keep | Same stamps, raw records, method and fallback. |
| I50 | cli.py:1333 | Sampling marker aliases versus event timestamps | Exact | Event linkage | identity | N/A | keep | Same emitted timestamp, not independent clock observations. |
| I51 | cli.py:1445 | Top-level uncertainty scalar versus component | Exact | Evidence alias | identity | N/A | keep | Copied scalar must remain the same value. |
| I52 | cli.py:1406,1410,1414 | Idle drift/guard/scalar versus fresh derivation | Exact | Idle-bound replay | identity | N/A | keep | Same raw sentinels and guard provenance. |
| I53 | cli.py:1738,1744,1774,1781 | CSV timestamp/power/support versus raw-derived sample | Exact per field | Trace serialization | identity | N/A | keep | Serialized observations from the same parser; native resolution is irrelevant to copy equality. |
| I54 | cli.py:1622 | Rich telemetry versus raw reconstruction | Exact | Telemetry serialization | identity | N/A | keep | Same primary records. |
| I55 | AE/ratio.py:202,220 | Reused diagnostic source’s conversion factors | rel 0, abs 0 | Diagnostic disambiguation | identity | N/A | keep | Unequal token normalizations are kept condition-specific; this is not an energy refusal. |
| I56 | uncertainty_evidence.py:59,1017 | Float representation padding | 1e-6 s; four epoch ULPs checked | Outward timing coverage | identity | N/A | keep | Written derivation covers 9.5367e-7 s at current epoch; old 1e-9 defect already repaired. |
| I57 | dominance_closeout.py:594,541 | Extrema pad and directed rounding | `64u×S_env`, four `nextafter` steps | Arithmetic enclosure | identity | J(64u×S_env) | keep | Member-scale rounding, explicitly justified by D-124’s observed undercoverage defect. |

### Measurement and statistical decision thresholds

| # | file:line | constant / expression | value | Quantity protected | Class | Ratio to 1 J / 5 J | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| M01 | uncertainty_evidence.py:386,935 | Native power×duration versus energy counter | `0.002 + 0.001|E_record|` J | Agreement of differently quantized telemetry fields | measurement | J(tolerance); 0.003/0.0006 at E=1 J | keep | **Sensible:** mJ counters and mW power rounding; healthy discrepancy described as ~1e-4 J. |
| M02 | uncertainty_evidence.py:407,998 | Wall-minus-monotonic span | ≤0.005 s | Clock-model stability | measurement | N/A | keep | **Sensible:** D-078 hard ceiling retained by independent 2026-08-18 science review. |
| M03 | uncertainty_evidence.py:444,1152 | First-parse lag | 0–0.25 s | Causal endpoint placement | measurement | N/A | keep | **Sensible:** bounded sampler-delivery lag, not sub-resolution timing. |
| M04 | uncertainty_evidence.py:37,1090 | Native departure from affine clock | ≤0.000250 s | Registered clock-model residual | measurement | N/A | keep | **Sensible conditional model:** allowance charged in full; science review preserves it and network-time-OFF assumption. |
| M05 | uncertainty_evidence.py:1129 | Feasible clock-rate projection | Entirely within ±50 ppm | Clock-rate model | measurement | N/A | keep | **Sensible conditional model:** refuse rather than clip; changing it needs a new ruled method. |
| M06 | uncertainty_evidence.py:1225 | Effective local anchor bound | ≤0.005 s | Anchor identification | measurement | N/A | keep | **Sensible:** includes interval half-width, span, stamp resolution and numeric padding. |
| M07 | idle_dependence.py:269 | `p95(interval)/p05(interval)` | ≤1.25 | Applicability of lag-index HAC model | measurement | N/A | keep | **Sensible registered applicability rule:** frozen before outcomes; no resampling escape. |
| M08 | whole_window.py:1900 | Gross endpoint point drift ≤ derived bound | `max(range₃, t×s×√(2/3))`, or legacy two-point formula | Gross drift screen | measurement | J(derived bound) | keep | **Sensible:** empirically derived reference scatter; not old 0.05 J sidecar policy. |
| M09 | whole_window.py:1900,2047 | Idle-subtracted endpoint drift ≤ own derived bound | Same estimator on idle-subtracted reference points | Idle-subtracted drift screen | measurement | J(derived bound) | keep | **Sensible:** separate claim-family evidence, not gross-bound substitution. |
| M10 | AE/claims.py:343 | `abs(estimate) > floor` | Dynamic authenticated F | Resolvable contrast magnitude | measurement | J(F) | keep | **Sensible:** current D-083 floor gate; equality does not pass. |
| M11 | AE/claims.py:351 | Equivalence margin > floor | Dynamic preregistered margin/F | Resolvable equivalence question | measurement | J(margin), or N/A | keep | **Sensible:** a margin within the floor cannot support equivalence. |
| M12 | AE/claims.py:374 | Both metrology and decision intervals exclude zero | Strict endpoint exclusion | Directional support | measurement | Boundary 0/0; widths J(h), J(B) | keep | **Sensible:** interval uncertainty is already priced; an extra 1 J fuzz would alter inference. |
| M13 | AE/claims.py:363,254 | Both intervals strictly within ±margin | Preregistered margin | Equivalence support | measurement | J(margin), or N/A | keep | **Sensible:** registered TOST/interval rule. |
| M14 | AE/__init__.py:1127 | Interpolation bound < active floor | Dynamic F | Interpolation-dominated result | measurement | J(F) | keep | **Sensible registered refusal:** compares uncertainty to the operative resolution scale. |
| M15 | AE/__init__.py:1129 | Interpolation bound < half effect | `0.5×|estimate|` | Effect dominated by interpolation | measurement | J(0.5×|estimate|) | keep | **Sensible registered refusal:** relative to the claimed effect, not a microscopic constant. |
| M16 | dominance_closeout.py:537 | Ordinary/shared-sign diagnostic ratio | R ≥2.0 | Attribution-dominance wording | measurement | N/A | keep | **Sensible registered diagnostic:** exact equality passes; D-165 addendum preserves threshold but narrows interpretation. |

### Evidence and preregistration refusals

| # | file:line | constant / expression | value | Quantity protected | Class | Ratio to 1 J / 5 J | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| E01 | uncertainty_evidence.py:876,881 | Complete valid ordered clock stamps | Five named stamps | Clock evidence | evidence | N/A | keep | D-161: missing/invalid clock evidence cannot license an anchor. |
| E02 | uncertainty_evidence.py:890,909 | Exact native timing fields; whole-second labels | Positive integer elapsed ns; label mod 1e9 =0 | Native-time model | evidence | N/A | keep | Representation/schema requirement, not demand for nanosecond physical resolution. |
| E03 | uncertainty_evidence.py:942,952 | Native labels monotone; forward jump bounded | Jump ≤ elapsed interval +1 s | Native-clock continuity | evidence | N/A | keep | Accounts explicitly for whole-second censoring. |
| E04 | uncertainty_evidence.py:401,961,965 | Native rollover census | V2 ≥1; current V3 ≥2 | Identifiable anchor/rate evidence | evidence | N/A | keep | No zero-rollover inferred bound. |
| E05 | uncertainty_evidence.py:977 | Rate-fit raw baseline | ≥60 s | Rate identification | evidence | N/A | keep | Registered science-review requirement; capture supply still needs checking. |
| E06 | uncertainty_evidence.py:990 | Controller coverage spans raw baseline | coverage ≥ baseline | Clock/rate linkage | evidence | N/A | keep | Raw timing cannot extend beyond its supporting paired-clock observations. |
| E07 | uncertainty_evidence.py:1094,1099,1102 | Native/stamp/causal feasible sets nonempty | Exact rational feasibility | Clock-model consistency | evidence | N/A | keep | Uncertainty is inside constraints; no arbitrary solver epsilon is needed. |
| E08 | uncertainty_evidence.py:1122 | Feasible projection must not touch solver box | ±1000 ppm box | Identification rather than clipping | evidence | N/A | keep | Computational enclosing box is much wider than ±50 ppm physical domain. |
| E09 | uncertainty_evidence.py:925,929 | Delta aggregation and finite energy counter | `is_delta is True`; counter present | Native telemetry meaning | evidence | N/A | keep | Missing/different aggregation evidence cannot be interpreted as interval energy. |
| E10 | uncertainty_evidence.py:1302 | Claim-bearing capture method | V3 only; absent/superseded refuse | Current clock evidence | evidence | N/A | keep | Frozen replay readability is not prospective claim eligibility. |
| E11 | idle_dependence.py:264 | Raw idle sample minimum | n≥2 | Estimable sample variance | evidence | N/A | keep | Algebraic minimum; no physical noise threshold. |
| E12 | idle_dependence.py:266 | Three-bandwidth support | `L=floor(10/median Δt)`; `n≥3(L+1)` | HAC support | evidence | N/A | keep | Registered before outcomes; exact-count/configuration edge noted in D. |
| E13 | idle_dependence.py:198,211 | Backend policy and raw idle evidence | Frozen powermetrics policy; raw bytes required | Idle uncertainty provenance | evidence | N/A | keep | Other backends cannot inherit the method by analogy. |
| E14 | uncertainty_evidence.py:1389 | Pre/post idle sentinels | ≥3 samples each | Endpoint drift evidence | evidence | N/A | keep | Both endpoints need observations. |
| E15 | uncertainty_evidence.py:1394 | Contamination evidence known and clean | Both suspect flags false | Sentinel validity | evidence | N/A | keep | Unknown is not clean. |
| E16 | uncertainty_evidence.py:1401 | Calibration drift guard usable when supplied | Finite guard≥0; n=0 selects explicit interim mode | Drift allowance | evidence | N/A | keep | Interim status is retained; absent guard is not fabricated calibration. |
| E17 | uncertainty_evidence.py:1436 | Prediction-guard inputs | ≥2 bounds; positive t critical | Predictive drift guard | evidence | N/A | keep | Minimum variance information and valid prediction multiplier. |
| E18 | whole_window.py:1477 | NEG-8 reference corpus | n≥10 | Drift repeatability estimate | evidence | N/A | keep | Registered D-054-style reference design. |
| E19 | whole_window.py:1987 | NEG-8 endpoint census | Current 3/start, 1/mid, 3/end; legacy 1/0/1 | Drift trajectory | evidence | N/A | keep | Requires both claim families on the same registered protocol. |
| E20 | whole_window.py:1323,1341,1350 | NEG-8 freshness | max age exactly 86400 s; evaluation in [derived,expires] | Reference transfer validity | evidence | N/A | keep | Stale evidence is a D-161 preserved refusal. |
| E21 | whole_window.py:1360 | Freshness identity changes | Exact OS, supply and calibration binding | Reference applicability | evidence | N/A | keep | Same age does not cure changed instrument conditions. |
| E22 | whole_window.py:1498,1960 | Both family bounds valid and derived | Strictly positive bounds; validated artifact | Nonvanishing drift allowance | evidence | J(bound) | keep | Constant/unsupported reference evidence does not justify a zero uncertainty allowance. |
| E23 | whole_window.py:5670,5856 | Whole-window verdict coverage and semantic identity | Complete coverage; one operative identity | Window admission | evidence | N/A | keep | Missing, failed, conflicting or ambiguous admission cannot support a claim. |
| E24 | whole_window.py:4134,4310 | Re-derived admission/calibration/continuity core | All required component predicates pass | Physical collection validity | evidence | N/A | keep | Seat-A predicates are consumed, not replaced by a successful-looking stored flag. |
| E25 | AE/inputs.py:2752 | Bundle existence, strict validity and success | All required | Source observation | evidence | N/A | keep | D-161 preserves absent/invalid evidence refusal. |
| E26 | AE/inputs.py:3059 | Common authenticated launch lineage | One compatible lineage | Prospective execution linkage | evidence | N/A | keep | Avoids mixing measurements from different launches/plans. |
| E27 | AE/inputs.py:3493 | Per-metric evidence precheck | Eligible true; known empty refusal list | Metric-specific eligibility | evidence | N/A | keep | A request-level success cannot substitute for failed phase evidence. |
| E28 | AE/inputs.py:3535 | Campaign cooldown evidence | Verified; no cap hit | Pre-run recovery | evidence | N/A | keep | A local `cooldown_cap_hit=false` is not campaign proof. |
| E29 | AE/inputs.py:3556 | Idle-subtracted metric’s idle status | Known nonsuspect | Idle subtraction | evidence | N/A | keep | Applies to idle-subtracted request metrics, not gross phase metrics indiscriminately. |
| E30 | AE/inputs.py:3691 | Governed stochastic variance/covariance | Known nonnegative variance; governed method/scope | Statistical uncertainty | evidence | N/A | keep | Missing terms/covariance are not zero. |
| E31 | AE/inputs.py:3780 | Required current anchor envelope/scalar | Present, valid, current method | Claim-side anchor widening | evidence | J(recorded bound) | keep | Mandatory despite upstream timing eligibility. |
| E32 | AE/inputs.py:3830,3843 | Interpolation term coverage | Present for all required windows | Claim-side interpolation | evidence | J(recorded bound) | keep | No incomplete sum over only available windows. |
| E33 | AE/inputs.py:3836 | Idle drift term | Present finite nonnegative | Idle-subtracted claim bound | evidence | J(recorded bound) | keep | Gross and idle-subtracted paths retain their different requirements. |
| E34 | AE/inputs.py:3871 | Whole-window drift allowance | Finite >0 when required; half per arm | Window-wide uncertainty | evidence | J(allowance) | keep | Existing paired addition then includes the allowance exactly once. |
| E35 | AE/inputs.py:4258,4304,4462 | Floor usable, matching and unambiguous | One exact cell or one registered transport route | Same-estimand floor | evidence | J(selected F) | keep | Smoke, missing, stale, unbound or inapplicable floors refuse. |
| E36 | AE/__init__.py:727,729,731 | Complete planned paired design | ≥2 to estimate; all frozen planned blocks for confirmatory test | Sample-size integrity | evidence | N/A | keep | Descriptive estimability does not authorize incomplete fixed-n inference. |
| E37 | AE/__init__.py:760; AE/claims.py:401 | Outcome-dependent top-up | Any detected top-up demotes | Preregistration | evidence | N/A | keep | D-062/D-161; no later promotion from a favorable enlarged sample. |
| E38 | AE/multiplicity.py:25,110,154 | Frozen family and rejection threshold | Exactly m IDs; adjusted p≤registered α/q | False-positive control | evidence | N/A | keep | Missing hypotheses retain their denominator; thresholds are preregistered. |
| E39 | AE/sensitivity.py:62,125,132 | Randomization applicability and count | Frozen exchangeability; 6≤n≤20; deterministic rotation exempt | Design-respecting sensitivity | evidence | N/A | keep | Six allows a two-sided exact p below .05; twenty is a registered enumeration cap. |
| E40 | AE/__init__.py:1444; AE/artifact.py:2910 | LOO census | Complete planned n=3…10; one omission per block; >10 not required | Influence sensitivity | evidence | N/A | keep | Registered small-sample sensitivity policy, not a measurement-precision demand. |
| E41 | AE/claims.py:398,409 | Claim-ready ceiling | Current, confirmatory, eligible role/direction, no blocking sensitivity | L2/L3 permission | evidence | N/A | keep | Statistical outcome alone does not establish allowed claim scope. |
| E42 | AE/registry.py:425,431,441,447 | AP-SPEC frozen design | n≥2; Holm α=.05,m=2; 3 estimands,2 contrasts | Separate registered analysis route | evidence | N/A | keep | Sibling inspected; this is not a new G2-a acceptance rule. |
| E43 | paper_reported_energy.py:170 | Registration predates spec | Strict Git ancestry; both model proofs; original/current digest matches | Prospective reported-energy semantics | evidence | N/A | keep | D-179 preregistration refusal; no timestamp-only substitute. |
| E44 | paper_reported_energy.py:245,249,275,279,288 | Reported-energy membership census | 50 unique ordered members; 3 registered cells/model; 6 floor cells; 10 repeats+10 ABBA blocks | Fixed-universe mean | evidence | N/A | keep | D-179 forbids a post-hoc 49-member mean. |
| E45 | paper_reported_energy.py:369,373 | Every row valid with all bound kinds | Strict-valid; exactly 3 finite nonnegative kinds | Mean/interval uncertainty | evidence | J(B) | keep | Missing bound is not zero; prediction term is expressly excluded. |
| E46 | paper_reported_energy.py:301,323,376 | Runtime token denominator and scope | Positive observed count; all prefill surfaces agree; fixed tokenizer/policy | J/token sibling | evidence | N/A | keep | Refuses per-token output only; preserves energy mean. |
| E47 | paper_custody.py:672; paper_rendering.py:44 | Issuance and typed projection available | Registered production gate, authenticated/admitted input, grants, projection | Reported-number authority | evidence | N/A | keep | Reported-energy production gate remains absent; fixture arithmetic cannot issue. |
| E48 | AE/claim_side_bound.py:109,125,147 | Valid source join, units and anchor kind | Usable resolutions; injective estimand/cell join; anchor explicitly present | Correct deterministic B | evidence | N/A | keep | D-178 copy-only sidecar requires complete upstream authority. |
| E49 | salvage_dangler.py:810,811 | Telemetry interval contained in licensed abort | `[run_started, failure+0.250 s]`, with 1e-9 s code fuzz | Preworkload-abort evidence | evidence | N/A | keep | D-100 evidence containment; 136–171 ms observed flushes justify 250 ms. Padding caveat in D. |
| E50 | salvage_dangler.py:775,1079,1082,1253 | Salvage contains no measurand; closed failure census | Null measurands; 3 attempts; terminal index 2; one byte-derived signature | No outcome-selective salvage | evidence | N/A | keep | D-100/D-087 licensed historical branch, not ordinary measurement acceptance. |

### Operator-mistake and numerical-domain guards

| # | file:line | constant / expression | value | Quantity protected | Class | Ratio to 1 J / 5 J | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| G01 | AE/estimators.py:167; AE/artifact.py:548; paper_reported_energy.py:95 | Finite numeric input, excluding bool | No NaN/Inf/bool/string | Valid arithmetic | mistake-guard | N/A | keep | Malformed input can arise accidentally; D-161 preserves refusal. |
| G02 | AE/estimators.py:176; whole_window.py:444; paper_reported_energy.py:373 | Bound/variance domains | ≥0 | Meaning of uncertainty | mistake-guard | 0/0 for J bounds | keep | Negative uncertainty is not instrument noise. |
| G03 | whole_window.py:1769,3464 | Gross reference envelope positive and ordered | `0<lower≤point≤upper` | Positive reference and relative-drift domain | mistake-guard | Boundary 0/0 | keep | Reference-domain guard; not a minimum 1 J measurement bar. |
| G04 | AE/artifact.py:563; AE/claim_side_bound.py:81 | Interval endpoints ordered | lower≤upper | Interval validity | mistake-guard | N/A | keep | Reversed bounds are invalid arithmetic. |
| G05 | AE/estimators.py:189; cli.py:1019,1026,1073,1088,1098,1150 | Token count domains and copies | Positive denominator/request; emitted≥0; exact row/event/ID counts | Discrete denominator integrity | mistake-guard | N/A | keep | Integer counts and fixed-budget completion require equality, not physical fuzz. |
| G06 | AE/estimators.py:304,524; AE/distributions.py:36 | Estimator sample/df domain | n≥2; integer df≥1 | Defined variance/t distribution | mistake-guard | N/A | keep | Mathematical domain guard, distinct from claim sample-size policy. |
| G07 | AE/estimators.py:360 | Covariance bound | `|cov|≤√(VaVb)+1e-12×max(1,√(VaVb))` | Positive-semidefinite covariance | mistake-guard | N/A: squared units | keep | Numerical matrix consistency; a 1 J tolerance would be dimensionally and statistically wrong. |
| G08 | AE/estimators.py:372 | Paired variance nonnegative | Floor tolerance `1e-12×max(1,Va+Vb)`; clamp accepted negative roundoff to 0 | Derived variance | mistake-guard | N/A | keep | Cancellation hygiene, not physical variability. |
| G09 | AE/estimators.py:700 | Ratio variance nonnegative | Same numeric expression, using unnormalized Va+Vb | Ratio variance | mistake-guard | N/A | keep | Not overly strict; dimensional scaling anomaly noted in D. |
| G10 | AE/distributions.py:21,83 | Incomplete-beta convergence | 3e-15 relative multiplicative change | Student-t probability accuracy | mistake-guard | N/A | keep | This apparent “1e-15” hit is solver convergence, not joule sensitivity. |
| G11 | AE/distributions.py:22,43 | Small denominator guard | 1e-300 | Avoid division overflow/underflow | mistake-guard | N/A | keep | Numerical algorithm constant. |
| G12 | AE/distributions.py:23,86 | Continued-fraction iteration ceiling | 10,000 | Finite solver completion | mistake-guard | N/A | keep | Nonconvergence refuses instead of emitting an unreliable p-value. |
| G13 | AE/distributions.py:140,151,154 | Quantile domain/bracketing/bisection | 0<p<1; finite bracket; ≤256 bisections | Student-t inversion | mistake-guard | N/A | keep | Numerical domain and representable convergence. |
| G14 | AE/distributions.py:177,210 | Exact sign-flip tie allowance | 1e-15 in input units; nonnegative | Extreme-count arithmetic | mistake-guard | J(1e-15) for J deltas; otherwise N/A | keep | Compares computed permutation statistics; not permission to demand 1e-15 J instrument resolution. |
| G15 | dominance_closeout.py:528,882 | Ratio denominator and corner census | denominator>0; 1≤blocks≤16 | Defined dominance ratio and exact enumeration | mistake-guard | N/A | keep | Zero denominator has explicit refusal; sixteen is the registered computational domain. |
| G16 | aggregate.py:266,441,474; AE/sensitivity.py:184 | Descriptive sample/outlier/influence flags | CI n≥2; minimum n=3; headline n=5; z>3.5 with scale .6745; LOO move>.25×MDE/F | Diagnostic interpretation | mistake-guard | N/A, except J(.25×MDE/F) | keep | Outliers remain in headline aggregate; magnitude-only LOO flag is nonblocking. |
| G17 | AE/registry.py:626,653; AE/artifact.py:2056; dominance_closeout.py:2128,2166 | Count/order aliases and closed census | 2n manifest entries; contiguous indices; df=n−1; 8 independent+4 comparative ratios | Correct assembly | mistake-guard | N/A | keep | Missing/duplicated/position-swapped rows are plausible operator mistakes. |
| G18 | AE/__init__.py:137; AE/artifact.py:582; paper_custody.py:1073 | Output separation, digest and role shapes | No input alias; SHA-256 64 hex; exact registered role census | Evidence preservation/linkage | mistake-guard | N/A | keep | Accidental overwrite or wrong-file assembly remains in D-161’s preserved class. |

### Deliberate-only candidates: listed, not adjudicated

| # | file:line | constant / expression | value | Quantity protected | Class | Ratio to 1 J / 5 J | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| D01 | paper_custody.py:134 | Refuse direct construction of verified capability objects | Unconditional outside mint | In-process construction authority | deliberate-guard | N/A | needs_ruling | Candidate for THREAT-MODEL-PRUNE-01; no disposition in this sweep. |
| D02 | paper_custody.py:168,176,192 | Private closure token identity | Exact object identity | In-process capability manufacture | deliberate-guard | N/A | needs_ruling | Candidate in-process adversary defense; distinct fixture/production type and evidence checks still protect mistakes. |

## B. RE-SET list

### B1 — D-165 zero-point identity band: proposed, requires ruling

**Priority:** the only demonstrated re-set candidate in this seat. **Low established likelihood of refusing a real G2-a number:** the demonstrated operands are approximately 20,000 J each. No live or fixture-level G2-a reproduction was run.

**Current guard:** `dominance_closeout.py:963` compares:

```python
math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12)
```

These are the same intended estimand but **different arithmetic paths**:

- Stored delta uses `(B1+B2−A1−A2)/2`, `detection_floor.py:1449`.
- Zero-shift replay uses weighted `math.fsum` of re-integrated member energies, `floor_extraction.py:2534`.
- D-124 already acknowledges real nonzero divergence and charges `abs(zero_point−delta)` into the shared bound. Its provenance guard is expressly **not load-bearing for soundness**: `docs/decision_log.md:8114–8138`.

**Demonstrated counterexample, sanity arithmetic only**

```text
A1=20000.1, B1=20000.3, B2=20000.0, A2=20000.2 J
sequential delta = 1.8189894035458565e-12 J
weighted fsum   = 0.0 J
current guard   = refuses
```

These binary64 operands are identical on both sides; the discrepancy is arithmetic, not telemetry noise.

**Proposed value**

Preserve the existing tolerance and add a member-scale arithmetic allowance:

```text
τ_new = max(
    1e-12 J,
    1e-9 × max(|zero_point|, |delta|),
    64u × S
)
u = 2^-53
S = max(1 J, member_envelope_integral_sum_j, |delta|, |zero_point|,
        every absolute onset/offset sweep value)
```

This uses the **existing D-124 member-integrand scale and `64u` allowance**, rather than inventing a measurement tolerance from 1 J. At the counterexample scale, the pad is `2.842192259322474e-10 J`: approximately `2.84e-10` of 1 J and `5.68e-11` of 5 J.

The proposed band must remain coupled to the existing **once-only outward charge of `|zero_point−delta|`**. Do not delete that term.

**Diff-shaped proposal; not applied**

```diff
--- a/joulewise/dominance_closeout.py
+++ b/joulewise/dominance_closeout.py
@@
-        if not math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12):
+        provenance_scale_j = max(
+            1.0,
+            float(block["member_envelope_integral_sum_j"]),
+            abs(delta),
+            abs(zero_point),
+            *(abs(value) for value in onset),
+            *(abs(value) for value in offset),
+        )
+        provenance_abs_tol_j = max(
+            1e-12,
+            64.0 * (math.ulp(1.0) / 2.0) * provenance_scale_j,
+        )
+        if not math.isclose(
+            zero_point, delta,
+            rel_tol=1e-9, abs_tol=provenance_abs_tol_j,
+        ):
             raise ValueError(_COMMON_MODE_ZERO_POINT_DIVERGENCE)
```

This does **not** complete the repair alone. Seat A owns the upstream duplicate at `floor_extraction.py:590`; leaving it unchanged would refuse the candidate before the D-165 replay consumer is reached. Prefer one shared predicate after lead approval.

**Defect-shaped regression**

1. Construct a block from the four stated member energies using the actual registered delta and zero-shift builder paths. Add another ordinary valid block so the point-floor denominator is nonzero. Supply valid windows, authenticated shared bound and complete sweeps.
2. **Admit counterfactual:** same member energies, differing only because of the two legitimate arithmetic paths. Assert old predicate refuses; proposed predicate admits; `|z−delta|` remains included in the shared width.
3. **Refuse counterfactual:** change the block delta by **1e-6 J**, leaving the authentic zero point and member-scale envelope unchanged. Assert the proposed provenance predicate still refuses. This is over three orders of magnitude beyond the illustrated new pad.
4. Exercise both extraction and replay consumers. A replay-only passing test would miss the earlier refusal.

These tests were **specified, not executed**.

**Contract changes required**

- Amend the sentence in `docs/contracts/d165_dominance_closeout.md:193` requiring agreement “inside the registered provenance tolerance” to name the scale-aware formula and its arithmetic-only role.
- Add a dated correction to `docs/decision_log.md:8130`, whose existing sentence explicitly registers `rel_tol=1e-9, abs_tol=1e-12`.
- Preserve the D-124 statements about exact zero-point membership, single-sourced bracket bounds and once-only discrepancy charging.

**No measurement-tolerance re-set is justified by this result.** Replacing these identity bands with 1 J, a sampling interval’s energy, or calibration width would hide incorrect recomputation.

## C. KEEP summary

The table contains **143 logical rows**:

| Class | Rows | KEEP | Other disposition |
|---|---:|---:|---|
| identity | 57 | 56 | I23 needs ruling on proposed re-set |
| measurement | 16 | 16 | None demonstrated microscopic |
| evidence | 50 | 50 | Capture-supply verification remains open |
| mistake-guard | 18 | 18 | Includes explicitly non-gating diagnostics |
| deliberate-guard | 2 | 0 | Deferred to THREAT-MODEL-PRUNE-01 |

**Identity rows whose arithmetic paths differ**

- **I23, D-165 zero-point versus delta:** demonstrated scale defect; B1.
- **I11–I12, Decimal bracket projections:** Decimal arithmetic versus binary64 projection/addition. D-124’s input-surface audit at `decision_log.md:8148` explicitly states the production-constructor assumption. Keep the 1e-12 s band; this is not calibration disagreement.
- **I29, total SE:** producer uses `hypot`; validator squares and adds. Existing tolerance is roundoff hygiene.
- **I32, metrology variance:** producer uses `fsum` and square root; validator accumulates terms and squares the stored SE. No false refusal demonstrated.
- **I33, deterministic total:** producer uses `fsum`; validator uses ordinary accumulation, with an implicit **1e-9 relative** tolerance. No microscopic refusal demonstrated.
- **I40–I41, LOO midpoint/p-value:** validator reconstructs center and SE from rounded interval endpoints. This is not the original arithmetic path. No current-scale failure demonstrated; an ill-conditioned endpoint inversion deserves a targeted numerical test, not an instrument-sized p-value tolerance.
- **I04–I06, widened versus minted envelopes:** these are different uncertainty-domain evaluations, not literal replay equality. Their ordering is an exact mathematical containment requirement. The small slack accommodates arithmetic; physical calibration width is already in the widened domain.

The apparently alarming constants `3e-15`, `1e-300`, and `1e-12` in distribution/variance calculations are **not instrument sensitivity requirements**.

## D. Anomalies and coverage limitations

1. **The brief’s F+B language is superseded.** Current decisions preserve both floor and claim-side roles but reject F+B as a necessary or sufficient acceptance bar. The report uses 5 J only as the requested comparison scale. No new additive cutoff should be installed.

2. **Potential G2-a capture-supply mismatch: 60-second raw baseline.**  
   `uncertainty_evidence.py:977` measures the accumulated raw intervals **excluding record zero**, not phase duration. Its ≥60 s gate is justified by the registered rate model. I did not establish that every prospective short G2-a capture supplies this lifetime. Seat A must check the complete sampler lifecycle; relaxing the fit requirement is not the first remedy.

3. **Idle sizing is stricter than the phrase “30 seconds” suggests.**  
   `idle_dependence.py:267` requires `n≥3(L+1)`. At exactly 100 ms, L=100 and the minimum is **303**, so 300 perfect 100 ms observations fail. At 115 ms, L=86 and the minimum is **261**, so 300 pass. The inspected `_v5` generator records `idle_seconds=30.0`. This is a capture-sizing compatibility question, not proof that the frozen HAC threshold should change.

4. **Salvage’s 1e-9 s padding is ineffective at current POSIX epochs.**  
   At the checked epoch, one ULP is `2.384185791015625e-7 s`; adding 1e-9 changes nothing. However, `salvage_dangler.py:810–811` implements **registered evidence containment**, not equality of two physical readings. I found no healthy-boundary reproducer proving the containment decision wrong. Keep the 250 ms domain; do not enlarge it to a sampling interval or native one-second label resolution without tracing the actual timestamp construction.

5. **Ratio variance tolerance uses an unnormalized scale.**  
   `AE/estimators.py:700` tests a `(J/token)²` contribution using a tolerance scaled by unnormalized J² variances. This is potentially **too permissive**, not the requested microscopic refusal defect. The earlier covariance guard constrains admissible inputs. Do not silently revise it under a “loosen tolerance” patch.

6. **Two apparent “gates” do not gate acceptance.**
   - `AE/claim_side_bound.py:207` diagnostics cannot grant or refuse issuance.
   - `AE/ratio.py:202,220` exact factor comparison prevents collapsing differently normalized diagnostics; it does not reject the energy result.
   - `aggregate.py:474` outlier detection retains all headline points.
   - `AE/sensitivity.py:184` magnitude-only influence is nonblocking.
   - `whole_window.py:2173` explicitly preserves legacy `max_abs_delta_j`/`max_rel_delta` fields as **non-gating**. The old 0.05 J example must not be mistaken for the current NEG-8 screen.

7. **Reported-energy production is not yet reachable.**  
   `paper_custody.py:653–660` registers D-165 and claim-evidence gates, not reported-energy production. `paper_reported_energy.py:413` is fixture projection. `paper_rendering.py:44` requires an issued projection. Consequently, this inspection cannot certify an end-to-end production reported-number path that has not been installed.

8. **Cross-footprint handoffs inspected only to resolve dependencies**
   - `floor_extraction.py:590`: upstream duplicate of B1.
   - `floor_extraction.py:2380,2534`: zero-shift arithmetic source.
   - `detection_floor.py:1449`: sequential ABBA arithmetic source.
   - `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:592`: sampling request.
   - Adapter cadence and fiducial contract: expressly requested instrument facts.
   
   Seat A retains ownership of their complete inventories and any changes.

9. **The assignment contains a contradictory sentence:** “If a hit is in seat B’s footprint, list the file:line under D and move on.” Read literally, it would prevent the requested seat-B table. I followed the explicit footprint and deliverable, and used D for anomalies and cross-footprint handoffs.

10. **Access and verification limits:** no targeted file failed to open. Large initial search outputs were truncated; consequential comparisons were reopened in bounded excerpts. No Git state, production supply, full test suite, project-code execution or live hardware was verified. Exact dirty-state and baseline identity remain unknown. This report does not claim a syntactic census of every schema-key refusal or successful production issuance.

## E. NEEDS_RULING

### R1 — D-165 arithmetic provenance tolerance

- **Question:** Should the registered contrast-scaled provenance band gain the member-scale arithmetic allowance in B1?
- **Options:** retain the present domain with a documented large-energy limitation; adopt the proposed shared predicate in extraction and replay; or require a production-scale counterexample before changing the registration.
- **Recommendation:** adopt the bounded member-scale identity repair, subject to a lead check that the inherited `64u×S` allowance covers both registered paths. Preserve exact zero-point membership and discrepancy charging.
- **Blocked work:** closing I23 and implementing/verifying a consistent repair across the two seats. No write-scope expansion is requested for this read-only scout.

### R2 — Capture duration and idle sizing

- **Question:** Do prospective G2-a captures provide the raw ≥60 s rate-fit baseline and enough idle samples under the exact HAC rule?
- **Options:** demonstrate current sizing already satisfies both; prospectively lengthen the supporting capture; or commission a newly ruled estimator if shorter support is essential.
- **Recommendation:** have seat A establish the lifecycle and sizing first. Preserve the current physical/evidence gates while doing so.
- **Blocked work:** certifying that these justified gates will accept correctly configured G2-a captures.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Incorporate KEEP inventory | start_now | None | Lead-owned report |
| D-165 provenance repair | needs_ruling | R1 | `dominance_closeout.py:963`, seat-A `floor_extraction.py:590`, D-124/D-165 text |
| G2-a capture sizing check | wait_for | Seat A’s complete sampler-lifetime inspection | Adapter/controller/configuration and `uncertainty_evidence.py:977` |
| Idle support sizing check | wait_for | Seat A’s idle-count derivation | Capture configuration and `idle_dependence.py:267` |
| Deliberate-only guards | do_not_start | THREAT-MODEL-PRUNE-01 | Private paper-custody construction machinery |
| Production reported number | wait_for | Registered issuing supplier and sweep closeout | Paper custody/energy projection |

## Critical path

Seat-A capture-supply checks and the R1 disposition precede declaring GATE-SENSIBILITY-SWEEP-01 satisfied. If B1 is adopted, extraction and replay must change together before the regression can establish that the original false refusal is removed. Production reported-energy issuance remains a separate outstanding dependency.