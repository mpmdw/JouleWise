# Cold-gate packet — window B re-evaluation STOP (mechanically assembled, no magistrate lean)

Assembled 2026-08-03 night by the magistrate under the runbook's
deviation escape. This packet records facts only. Tracked per D-111.

## What ran

Command (lead-executed, main checkout at `7e3726a`; the D-100 repair,
D-108 close, and clause-(d) re-record are all landed; Stream B's D-109
implementation is NOT merged and not in this tree):

```
.venv/bin/python scripts/run_campaign.py --whole-window-verdict
  --runs-dir /Users/edr/code/JouleWise/runs_window_metrologyB_20260801
  --log .../runs_window_metrologyB_20260801/campaign_log.jsonl
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
  --neg8-drift-bound /Users/edr/code/JouleWise/runs_window_metrologyB_20260801_bound/neg8-drift-bound.json
  --consumption-semantics-id salvage_dangler_exclusion_v1
  --window-membership-binding ~/JouleWise-window-custody/window_metrologyB_20260801/membership-binding.json
  --salvage-closure ~/JouleWise-window-custody/window_metrologyB_20260801/salvage-closure.json
```

## Outcome (verbatim)

```
exit code 2
error: authenticated survivor consumption refused: clock_anchor_unresolved, environment_admission_missing
```

- NO new row was appended: campaign_log.jsonl remains 120 lines; tail
  row is the ORIGINAL 2026-08-01T14:19:10Z FAILED verdict, untouched.
- Refusal site: `scripts/run_campaign.py:5198` —
  `AuthenticatedConsumptionSession._prepare` over the INCLUDED
  survivors under `salvage_dangler_exclusion_v1`; `ready` was False
  with `refusal_reasons = [clock_anchor_unresolved,
  environment_admission_missing]`.
- `clock_anchor_unresolved` is NOT one of the five original window B
  failure conditions D-100 classified as pure cascade
  (membership_unresolved, environment_admission_missing,
  neg8_bracket_missing, neg8_bracket_reference_invalid,
  neg8_drift_bound_stale). `environment_admission_missing` IS one of
  them.

## License-condition state at the STOP (runbook conditions 1-8)

1-2. Contract + repair landed and audited (PR #94, PR #99). ✓
3. Clause-(d) re-record executed at merged HEAD 32d72fd, 3/3 licensed,
   digest-bound (`.desk/coldgate_d100_bii/d108-clause-d-rerecord.json`,
   copy to be tracked with this packet). ✓
4-5. Closure + membership-binding artifacts authored by a delegated
   session with every fact re-verified against primary bytes;
   dry-authorization PASSED (d093 [1,1,clean]; payload_attempt_count 3;
   operator deviation flagged). Installed unchanged to custody. ✓
6. D-093 raw-vs-validated scan clean 1/1. ✓
7. Frozen-corpus evidence recorded (210 member files + 4 bracket files,
   zero mismatches vs the original evaluation inputs;
   `~/JouleWise-window-custody/window_metrologyB_20260801/reeval-evidence.md`). ✓
8. Governed re-evaluation: REFUSED pre-verdict as above. ✗ → STOP.

## Possibly-related same-night observations (recorded, not argued)

Two current-HEAD extraction regenerations over OTHER (passed) windows
also refused under today's machinery where the July-28 pinned tool
accepted (Q1 replay lane, verification-only): a10 refused with
{adapter_continuity_evidence_missing, cpu_admission_core_missing,
whole_window_neg8_verdict_missing, admissible_set_uncertainty_dominates_
point_floor}; window_c refused with {admissible_set_uncertainty_
dominates_point_floor, whole_window_verdict_conflict}. A joint consult
ruled those "tightened-policy behavior, not corpus drift" FOR THE
VERIFICATION LANE (pinned replay licensed instead). Whether that
interpretation extends to a CLAIM-BEARING verdict run is exactly what
this gate must NOT assume.

## The question for the gate

Classify the survivor-consumption refusal:
(i) CORRECT machinery on real evidence state — window B's surviving
    bundles genuinely lack what salvage-semantics consumption requires
    (then: what, per bundle, and what does D-100's re-evaluation
    license mean now?);
(ii) a salvage-semantics DISPATCH defect — e.g. the session applying
    max-bracket-grade authentication requirements (calibration anchor
    resolution) to null/reference bundles that legitimately do not
    carry them (then: repair row, no reinterpretation of the verdict);
(iii) operator input error in the command above (then: name it).

Constraints binding the gate: the original FAILED verdict stands as
issued regardless (D-100); no reinterpretation of any stop signal;
window B re-evaluation remains blocked until this gate rules; the
magistrate's crude read-only probe (naive session construction,
policy=None, all-bundles set) FAILED to reproduce the refusal and is
recorded as non-evidence.

## Primary evidence pointers

- runs root + campaign log: `runs_window_metrologyB_20260801/` (frozen)
- custody: `~/JouleWise-window-custody/window_metrologyB_20260801/`
  (closure, binding, reeval-evidence, close-out)
- code: `scripts/run_campaign.py:5160-5210`,
  `joulewise/whole_window.py` (AuthenticatedConsumptionSession)
- rulings: D-100 (+ addendum), D-106, D-108, D-093; runbook
  `.desk/runway-20260801-artifacts/winB-reeval-runbook.md`
