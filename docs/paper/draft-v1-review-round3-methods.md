```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Methods audit found two claim-bearing uncertainty misstatements and four examiner-facing precision issues in draft Sections 3, 4, and 6.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "01420dab85158131da93594663f2de5dec45bb26",
    "head_end": "01420dab85158131da93594663f2de5dec45bb26",
    "upstream_end": null,
    "branch": "impl/paper-methods-audit"
  },
  "pathspec": [
    "docs/paper/draft-v1-review-round3-methods.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --no-index --check /dev/null docs/paper/draft-v1-review-round3-methods.md; rc=$?; if [ \"$rc\" -gt 1 ]; then exit \"$rc\"; fi; python3 - <<'PY'\nfrom pathlib import Path\nimport re\ns = Path('docs/paper/draft-v1-review-round3-methods.md').read_text()\nlevels = re.findall(r'^\\*\\*Severity: (BLOCKER|SHOULD-FIX|NIT)\\.\\*\\*', s, re.M)\nassert levels.count('BLOCKER') == 2\nassert levels.count('SHOULD-FIX') == 4\nassert levels.count('NIT') == 0\nfor token in ('## Coverage and verdict', '## Findings', '## Non-findings', '## Ordered fix list', '## Evidence and handoff'):\n    assert token in s\nprint('memo-structure: pass')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "memo-structure: pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "memo-structure: pass"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short && git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "?? docs/paper/draft-v1-review-round3-methods.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "docs/paper/draft-v1-review-round3-methods.md"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The lead should confirm that the two line-56 findings are applied as one atomic prose edit and should keep unmerged trust/recovery work described as unmerged.",
      "needs": "Lead contextual review before the later draft edit train lands."
    }
  ]
}
```

# Methods spec-fidelity audit memo — round 3

## Coverage and verdict

Audited `docs/paper/draft-v1.md` sentence-by-sentence across Section 3, lines 38–58; Section 4, lines 60–125; and Section 6, lines 153–172. The audit included prose, displayed equations, table cells, and completion-state tokens. Binding comparison sources were `docs/phase_2/floor_mint_contract.md`, `docs/phase_2/window_runbook.md`, `docs/phase_2/detection_floor.md`, decision-log entries D-078, D-083, D-085, D-116, D-117, D-119, D-121, D-122, D-123, and D-124, the issued D-079 artifact `configs/calibration/calibration_acceptance_d079_v2.json`, and the computation in `joulewise/detection_floor.py` (sources: the named documents and code; draft line locations from `docs/paper/draft-v1.md`).

**Verdict: REVISE. Finding count: 2 BLOCKER, 4 SHOULD-FIX, 0 NIT.** The floor formulas, interval-corner logic, cross-window maximum, attribution label, and separate two-gate claim rule are faithful. The blockers are narrower but claim-bearing: one sentence understates the calibration-drift allowance, and one defines idle subtraction with phase duration even though phase energy is gross-only (sources: issued D-079 artifact `decimal_derivation.ratified_operatives`; D-117 clause 1; `docs/phase_2/detection_floor.md` §§2–3 and §5 “NEG-8 SCREEN + BUDGET amendment”).

## Findings

### M01 — line 56 understates the never-zero calibration allowance

**Draft section and exact sentence:** §3, line 56: “A small repeatability-only excess over the screen is propagated into every floor and claim, while an identified systematic defect cannot be absorbed by that budget.”

**Binding conflict:** The issued acceptance artifact defines the calibration allowance as `max(observed_drift_s, bracket_screen_s)`, with an operative bound of `max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s`; it does not propagate only the amount above the screen. D-117 clause 1 restates the never-zero rule as `A_s = max(observed_drift_s, 0.010818)` for every successor mint. The preceding sentence in the draft states the full rule correctly, but this sentence then contracts it to “excess,” creating an internally inconsistent account of a claim-bearing bound (sources: `configs/calibration/calibration_acceptance_d079_v2.json`, `decimal_derivation.ratified_operatives.allowance_rule` and `.operative_bound_rule`; `docs/decision_log.md`, D-117 clause 1; D-079 clause 1).

**Severity: BLOCKER.** This wording can lead a reader or later editor to subtract the screen and understate the bound.

**Minimal corrected wording proposal:** “For ordinary repeatability scatter, the full allowance—the larger of the observed bracket difference and the derived screen—is propagated into every floor and claim; an identified systematic defect cannot be absorbed by that budget.”

### M02 — line 56 calls the pre-flight comparator a fitted lag

**Draft section and exact sentence:** §3, line 56: “It rejects a calibration whose fitted lag is outside the previously characterized family, such as a graphics-processor frequency ramp that the pulse model could mistake for a timing shift.”

**Binding conflict or understatement:** The pre-flight screen compares the calibration artifact’s composite fiducial timing bound, `b_fiducial_s`, with the issued level threshold. It is not a screen on one fitted lag. D-079 explains that the anomalous onset residual contributes to the failure, while the comparator remains the complete fiducial bound; the run-book likewise directs the operator and chain to read `b_fiducial_s` (sources: `docs/decision_log.md`, D-079 clauses 2–3; `docs/phase_2/window_runbook.md` §5B “The screen”; `configs/calibration/calibration_acceptance_d079_v2.json`, `decimal_derivation.rounding.preflight_level_screen`).

**Severity: SHOULD-FIX.** An examiner following the method cannot reproduce the screen from “fitted lag.”

**Minimal corrected wording proposal:** “It rejects a calibration whose composite fiducial timing bound lies outside the previously characterized family, such as when a graphics-processor frequency ramp is absorbed by the pulse model as apparent edge displacement.”

### M03 — line 58 overstates what constrains load-regime transfer

**Draft section and exact sentence:** §3, line 58: “The in-session bracket, empirical floor probes in Section 6, and stack-specific labels constrain that assumption; only an external meter could additionally validate the absolute whole-system scale.”

**Binding conflict or understatement:** D-078 registers transfer from graphics-processor calibration pulses under light central-processor load to sustained mixed-load inference as an assumption. The in-session bracket establishes temporal consistency of that calibration identity, and floor probes can test the operational false-effect behavior of the named stack, but neither independently validates the load-regime transfer assumption. The external-meter boundary is separate again: it can validate whole-system totals, not phase attribution by itself (sources: `docs/decision_log.md`, D-078 clause 7b(2), transfer assumption T3; `docs/phase_2/detection_floor.md` §4 “Telemetry Trust Hierarchy” and “Wall-Meter Runbook”; `docs/phase_2/window_runbook.md` opening definitions and §8).

**Severity: SHOULD-FIX.** “Constrain” can be read as empirical validation of the registered transfer assumption.

**Minimal corrected wording proposal:** “The in-session bracket checks calibration consistency, empirical floor probes test operational false effects on the named stack, and stack-specific labels limit the scope of the conclusion; none independently validates transfer of the timing bound to sustained mixed-load inference. An external meter could additionally validate whole-system totals, but not phase attribution by itself.”

### M04 — line 62 opens a window-class vocabulary that the code closes

**Draft section and exact token:** §4, line 62: “phase or other interval type”.

**Binding conflict or understatement:** The implemented floor metric/window validator admits only `request` and `phase`, and the public metric catalog contains request metrics plus named `phase_energy_j.*` metrics. The ratified floor-mint contract likewise requires a shared closed metric/window-class validator; item, level, and other arbitrary interval types are not open members of the current artifact vocabulary (sources: `joulewise/detection_floor.py`, `FLOOR_METRIC_CATALOG` and `validate_floor_metric_window_class`; `docs/phase_2/floor_mint_contract.md`, Implementation Order W8).

**Severity: SHOULD-FIX.** The present phrase implies a broader implemented artifact domain than exists.

**Minimal corrected wording proposal:** Replace “phase or other interval type” with “request or phase interval type”.

### M05 — line 98 uses phase duration to define a request-only idle subtraction

**Draft section and exact sentence:** §4, line 98: “Gross energy and idle-subtracted energy are treated as separate claim families; idle-subtracted energy is gross energy minus the measured idle mean power multiplied by the phase duration.”

**Binding conflict:** Idle-subtracted energy is a request-window metric. The reducer computes `idle_subtracted = gross - idle_mean * duration` using the measured request-window duration, while phase energy is gross-only until a phase-idle model exists. The floor catalog reinforces the separation by listing `idle_subtracted_energy_j` as a request metric and `phase_energy_j.*` as distinct phase metrics (sources: `docs/phase_2/detection_floor.md` §2 “Metric And Window-Class Notes” and §3 “Idle-Subtracted Request Propagation”; `joulewise/detection_floor.py`, `FLOOR_METRIC_CATALOG` and `validate_floor_metric_window_class`).

**Severity: BLOCKER.** This is a dimensional formula attached to the wrong measurement window and could change reported energy.

**Minimal corrected wording proposal:** “Gross energy and idle-subtracted energy are separate whole-window claim families. For a request, idle-subtracted energy is gross request energy minus the measured idle mean power multiplied by the measured request-window duration; phase energy remains gross-only because no phase-idle model is defined.”

### M06 — line 159 calls a same-instrument slope a known-effect standard

**Draft section and exact sentence:** §6, line 159: “Energy would respond proportionally over the tested dynamic range, and the fitted per-token slope could serve as the known-effect standard for floor probes on this stack.”

**Binding conflict or understatement:** A slope estimated from the same unbridged software counter is an internal, model-based target, not an independently known energy input. The measurement design may use larger signals prospectively, but D-122 labels its analogous longer-prompt value as a projection rather than demonstrated evidence, D-123 freezes the measurand and procedure rather than the number, and D-119 requires the weaker truthful wording when evidence does not warrant the stronger claim. Without an external boundary bridge, the platform counter remains uncalibrated for absolute system-energy gain (sources: `docs/decision_log.md`, D-119 conservative-language rule, D-122 “Evidence basis,” and D-123 clauses 1–2; `docs/phase_2/detection_floor.md` §4 “Telemetry Trust Hierarchy” and “Wall-Meter Runbook”; D-078 clause 10 “NO INVENTED PHYSICS”).

**Severity: SHOULD-FIX.** The proposed experiment can test internal decision behavior, but “known-effect standard” makes that test sound independently calibrated.

**Minimal corrected wording proposal:** “If the fit is adequate, its internally estimated per-token slope will define model-based target sizes for floor probes on this stack; those probes test the method’s operational decision boundary, not an independently known energy input or the counter’s absolute gain.”

## Non-findings

The following spec-critical statements were checked and are correct; the later edit train should not re-litigate them.

- **Fresh 59-pulse bracketing and its epistemic label (§3 lines 50–52): CORRECT.** Protocol v3 uses 59 pulses, a deterministic varied-gap schedule, independently fitted start/stop behavior, and a 95/95 nonparametric calibration statement that becomes deterministic for claims only under registered transfer assumptions (sources: `docs/decision_log.md`, D-078 clause 7b(1)–(3) and round-8 follow-up; `docs/phase_2/window_runbook.md` §§3, 5B, and 8).
- **Three-term edge attribution and exact four-corner evaluation (§3 line 54): CORRECT.** The repaired path combines member-local anchor uncertainty, fiducial edge uncertainty, and wall-versus-monotonic span, then evaluates independent start/stop edge corners while scanning the common shift (sources: `docs/decision_log.md`, D-078 second amendment clause 1 and third-amendment follow-ups; `docs/phase_2/detection_floor.md` §5 “Governed max-bracket consumption”).
- **The first and most detailed calibration-allowance sentence (§3 line 56): CORRECT apart from M01’s later shorthand.** The draft correctly gives the derived bracket screen, the never-zero maximum rule, non-budgetability of systematic defects, governed wider-bound re-reduction, and cause-removal-only retry semantics (sources: issued D-079 artifact `decimal_derivation.ratified_operatives`; `docs/decision_log.md`, D-079 clauses 1–3 and D-117 clause 1; `docs/phase_2/window_runbook.md` §§5B, 8, and 10).
- **Absolute and ABBA point-floor equations (§4 lines 66–88): CORRECT.** The formulas, ABBA sign convention, Student-t prediction term, small-sample guard, and smoke-only treatment below five independent bundles or blocks match the implementation (sources: `joulewise/detection_floor.py`, `_floor_estimate`, `small_sample_guard_factor`, `absolute_false_effect_floor`, `comparative_false_effect_floor`, and `abba_delta`; `docs/phase_2/detection_floor.md` §1 “Floor Artifact Semantics”).
- **Joint-corner widening and rejection of root-sum-square treatment (§4 lines 92–94): CORRECT for the landed implementation.** The code maximizes the complete floor over joint admissible-set corners and retains the point-only calculation as a non-publishing diagnostic when attribution dominates (sources: `joulewise/detection_floor.py`, `_corner_maximized_unguarded_floor`, `_apply_admissible_set_guard`, and `_point_floor_diagnostic`; `docs/decision_log.md`, D-078 clause 11).
- **D-124 does not yet invalidate the preceding non-finding.** D-124 promotes the two-shared-edge common-mode estimator only as a registered candidate until its implementation and pre-registration gates land; on failure, contrasts revert to the current worst-case default. The draft’s worst-case account therefore describes the landed code, not the unlanded candidate (source: `docs/decision_log.md`, D-124 “What is promoted,” “Registration conditions,” and “Sequencing”).
- **Three-start/one-midpoint/three-end drift construction, separate families, and no invented duration scaling (§4 lines 98–105): CORRECT except for M05’s idle-subtraction duration.** The allowance is the maximum of the observed trajectory excursion and the derived family-specific repeatability bound, remains nonzero, and is not scaled by an unsupported drift law (sources: `docs/phase_2/detection_floor.md` §5 “NEG-8 SCREEN + BUDGET amendment”; `docs/phase_2/window_runbook.md` §§2–3 and 9; D-078 clause 10 addendum).
- **Per-component single addition and cell maximum (§4 lines 107–113): CORRECT.** Each component adds its authenticated allowance once, cross-window components retain separate bases and allowances, and `floor_gate_j` is the maximum of the final absolute and comparative components, never their sum (sources: `docs/phase_2/floor_mint_contract.md` W3 rules 1–8; `joulewise/detection_floor.py`, `_add_whole_window_drift_allowance` and `build_floor_cell`; D-083).
- **Attribution-limited publication and separate claim gates (§4 lines 117–125): CORRECT.** The label is available only when attribution dominance is the sole condition and an exact corner-widened floor exists; the point diagnostic cannot publish; floor clearance and interval-supported direction remain separate gates; floor plus claim-side bound is a disclosure and sizing quantity, not a summed acceptance test (sources: `docs/phase_2/detection_floor.md` §1 “Floor Artifact Semantics” and §5 “Extraction hygiene”; `docs/decision_log.md`, D-078 clause 11 and D-083).
- **Prospective characterization status (§6 lines 155–172): CORRECT as a completion-state boundary.** Every result remains explicitly pending, failed historical fragments are not promoted, whole-system validation remains conditional on an external meter, and conclusions remain stack-specific (sources: `docs/decision_log.md`, D-117 clauses 2 and 4 and D-119; `docs/phase_2/detection_floor.md` §4; `docs/phase_2/window_runbook.md` §§11–12).
- **Issued D-079 anchor: CORRECTLY available, but not fresh science.** D-116 records the artifact as issued and claim-eligible, and the checked artifact’s role/status agree. D-117 then supersedes historical re-minting: the historical corpus establishes the rule, while fresh live brackets must govern all prospective claim-bearing science (sources: `docs/decision_log.md`, D-116 “What was written” and D-117 clauses 1–2; `configs/calibration/calibration_acceptance_d079_v2.json`, `artifact_role`, `issuance`, and `ledger_cutoff`).

### Decode-only versus gamma-arm staleness

The known stale decode-only wording does **not** occur inside the audited line ranges. It appears immediately afterward in draft §7: line 180 says the registered model-size contrast is token-generation only; lines 184 and 186 continue to treat the longer-prompt prefill arm as an optional alternative. D-122 supersedes that state by putting a prospectively frozen 256-token prefill ABBA arm on gamma. This memo records the location only and deliberately supplies no §7, §9, or §13 edit proposal because those sections belong to other lanes (sources: `docs/paper/draft-v1.md` lines 180, 184, and 186; `docs/decision_log.md`, D-122 consequences 1 and 4).

### Unmerged-branch boundary

No finding above treats unmerged work as landed. Current restart authority identifies post-collection trust work on `impl/d117-postcollection-trust` and append-recovery/arming work on `impl/d117-ledger-recovery` as unmerged. Statements that the future prospective chain has completed those stronger trust or crash-recovery mechanics depend on those branches; the audited Sections 3, 4, and 6 state measurement requirements and calculations and do not claim that either branch has landed (source: `RUN_STATE.md`, T1 final checkpoint “SUCCESSOR ORDER,” items 1–2). D-124’s estimator is likewise only a registered candidate, as noted above (source: `docs/decision_log.md`, D-124).

## Ordered fix list

Apply top-to-bottom. M01 and M02 share line 56 and should be applied as one atomic paragraph edit before moving to later lines.

| Draft line | Finding | Severity | Exact target | Minimal edit |
|---:|---|---|---|---|
| 56 | M01 + M02 | BLOCKER + SHOULD-FIX | “A small repeatability-only excess…” and “whose fitted lag…” | Replace “excess” with the full maximum allowance rule and name the screened quantity as the composite fiducial timing bound. |
| 58 | M03 | SHOULD-FIX | “constrain that assumption” | Separate within-session consistency and operational floor probes from independent validation of load-regime transfer. |
| 62 | M04 | SHOULD-FIX | “phase or other interval type” | Use the implemented closed classes: “request or phase interval type.” |
| 98 | M05 | BLOCKER | “multiplied by the phase duration” | Define request idle subtraction with request-window duration and state that phase energy remains gross-only. |
| 159 | M06 | SHOULD-FIX | “known-effect standard” | Call the fitted slope an internal, model-based target and deny independent gain calibration. |

Sources for every row are the corresponding finding’s binding-source paragraph above; draft line numbers are from the audited `docs/paper/draft-v1.md` head.

## Evidence and handoff

- **Coverage:** complete for draft lines 38–58, 60–125, and 153–172; no sentence, formula, table cell, or placeholder in those ranges was skipped (source: line-numbered inspection of `docs/paper/draft-v1.md`).
- **Counts:** 2 BLOCKER, 4 SHOULD-FIX, 0 NIT (source: findings M01–M06 in this memo).
- **Deviations:** none. Only this memo was written; `docs/paper/draft-v1.md` and every other repository path remained read-only (source: final `git status --short` and `git diff --name-only` verification recorded in the report envelope).
- **Lead double-check:** apply the two line-56 fixes atomically; preserve the distinction between the issued historical acceptance rule and fresh prospective science; do not import the unmerged trust/recovery implementation state; and let the owning §7 lane repair the D-122 gamma-arm staleness (sources: issued D-079 artifact; D-117 clauses 1–2; D-122; `RUN_STATE.md` T1 final checkpoint).
