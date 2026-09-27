# 06 — Screen diagnostics

Primary source: `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json` (sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`). Issuer implementation: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/scripts/issue_calibration_acceptance_generation.py` (sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`). Registration: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`).

```json
{
  "rule_outcomes": {
    "screen_challenge_member_count": 2,
    "screen_challenge_threshold_s": "0.032898493715362",
    "new_maximum_exceeds_prior_maximum_plus_range": false,
    "prior_maximum_plus_range_s": "0.04262208300415633",
    "quantized_range_s": "0.013701",
    "screen_floor_bound": false,
    "headroom_status": "positive_headroom"
  },
  "source_statistics": {
    "maximum_s": "0.03807857930294817",
    "maximum_member_id": "d079-epoch-25g83-derivation-w2-20260927-d10",
    "range_s": "0.013701485381050852",
    "prediction_99_two_draw_s": "0.01902064410651988"
  },
  "operatives": {
    "bracket_screen_s": "0.013701",
    "preflight_level_screen_s": "0.038078579302948",
    "maximum_budgetable_drift_s": "0.01902064410651988"
  },
  "predecessor_ceiling_s": "0.010164834757777545"
}
```

Members above the candidate’s prior screen threshold (`prior_screen_comparison.exceeds_prior_level_screen=true`):

- `d079-epoch-25g83-derivation-w1-20260927-d04`: B `0.03610911339816257` s.
- `d079-epoch-25g83-derivation-w2-20260927-d10`: B `0.03807857930294817` s.

S is `registered_generation_row.operatives.bracket_screen_s`; C is `registered_generation_row.operatives.maximum_budgetable_drift_s`. The candidate also records predecessor C and Q99 in the fields above.

### issue_calibration_acceptance_generation.py lines 1923–1935

Primary source: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/scripts/issue_calibration_acceptance_generation.py` (sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`). Verbatim:

```text
        raise PrepareRefusal(
            f"retained corpus n = {n} is below the required floor {minimum}; not issued"
        )

    challenged = [row for row in comparisons if row["exceeds_prior_level_screen"]]
    statistics = _corpus_statistics(members)
    if not revision_five and len(challenged) >= SCREEN_CHALLENGE_MEMBER_LIMIT:
        raise PrepareRefusal(
            f"screen challenge: {len(challenged)} retained members exceed "
            f"{level_screen_threshold}; not issued, Ed rules in writing"
        )

    degrees_of_freedom = n - 1
```

### issue_calibration_acceptance_generation.py lines 1955–1968

Primary source: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/scripts/issue_calibration_acceptance_generation.py` (sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`). Verbatim:

```text
    # The NAME is the pre-registered rule, not the arm of the `max` that won.
    screen_rule = SCREEN_RULE_FLOORED_RANGE_ENVELOPE
    predecessor_operatives = predecessor["decimal_derivation"]["ratified_operatives"]
    predecessor_ceiling = Decimal(predecessor_operatives["maximum_budgetable_drift_s"])
    ceiling = envelope_ceiling(predecessor_ceiling, Decimal(prediction_99))
    # D-125 / D-126 cl.3: the screen must sit STRICTLY below the ceiling, and
    # the refusal is never cured by lowering the screen (the floor binds it).
    if revision_five:
        ceiling = max(ceiling, screen)
    if not revision_five and not screen < ceiling:
        raise PrepareRefusal(
            "successor_screen_exceeds_budget_ceiling: screen "
            f"{screen} is not strictly below the budget ceiling {ceiling}; "
            "not issued, Ed rules in writing"
```

### issue_calibration_acceptance_generation.py lines 2211–2221

Primary source: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/scripts/issue_calibration_acceptance_generation.py` (sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`). Verbatim:

```text
                "excursion_member_count": excursion_count,
                "excursion_label": "excursion_limited" if excursion_count >= 2 else None,
            } if revision_five else {}),
            "screen_challenge_member_count": len(challenged),
            "screen_challenge_threshold_s": str(level_screen_threshold),
            "new_maximum_exceeds_prior_maximum_plus_range": (
                Decimal(statistics["maximum_s"]) > R6_MAXIMUM_PLUS_RANGE_S
            ),
            "prior_maximum_plus_range_s": str(R6_MAXIMUM_PLUS_RANGE_S),
        },
        "preregistration": {
```

### preregistration_d079_epoch_25g83_rev1.md lines 632–634

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Verbatim:

```text
The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch: on an identical instrument it would falsely refuse 16.3 % of the time. Count retained B > 0.075 s. Two or more mark the candidate `excursion_limited`, requiring the estimator lane before a phase-split claim. Any member B > 0.25 s refuses issuance with the `PLATEAU_INSET_S` mechanism named; 0.25 s is that protocol's plateau inset. No B value is excluded. S = max(corpus range quantized to 1e-6 s, 0.010818 s); C = max(predecessor C, successor Q99, S). If C = S, record `zero_headroom` and proceed with issuance; drift above S is refused by the operative bracket.

The physical barriers are pulse interiors, SNR, detection of all 59 pulses, edge coverage, anchor feasibility, pre/post brackets, settle and slot cadence, blindness, and verified Interactive launch context. Calendar-day spacing, n ≥ 19, the predecessor screen challenge, and strict S < C are not physical barriers for this epoch.
```

