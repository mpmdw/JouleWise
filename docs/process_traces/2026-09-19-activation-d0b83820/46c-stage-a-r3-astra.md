```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented ruling 46b within six-file scope; 88 focused tests and 12 mutation checks pass; canonical suite encountered sandbox restrictions.",
  "workspace": {
    "base_requested": "8c7f7d9f",
    "base_mode": "exact",
    "head_start": "8c7f7d9f6c7a7c9e032f63a8aef9834dff56438f",
    "head_end": "8c7f7d9f6c7a7c9e032f63a8aef9834dff56438f",
    "upstream_end": "8c7f7d9f6c7a7c9e032f63a8aef9834dff56438f",
    "branch": "feat/2026-09-19-stage-a-evidence-executor"
  },
  "pathspec": [
    "joulewise/quiet_predicate_campaign.py",
    "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json",
    "configs/campaigns/quiet_predicate_evidence_01/README.md",
    "tests/test_quiet_predicate_campaign.py",
    "joulewise/night_gate.py",
    "tests/test_night_gate.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_quiet_predicate_campaign tests.test_night_gate tests.test_gen_evidence_night > /tmp/stagea-r3-final-focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-r3-mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS: 12 one-site mutants rejected"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS: 12 one-site mutants rejected"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests > /tmp/stagea-r3-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible."]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g3_browser_and_monitor_probes_gate_the_row tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused > /tmp/stagea-r3-suite-failures.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": [" 6 files changed, 245 insertions(+), 36 deletions(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "6 files changed"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Canonical discovery encountered two failing subtests in the existing real-pgrep census test. Focused reproduction confirms exit 3: sysmond service not found; Cannot get process list. Neighboring tests pass. The remaining canonical run was interrupted after confirming this restriction; interpreter shutdown also reported unavailable Metal access. No full-suite pass is claimed.",
      "needs": "Lead reruns canonical verification in an environment supporting the existing process-census tests."
    }
  ]
}
```

## Change

Implemented fixed disjoint pairing, four-pair minimum, sample SD, and the upper-90% chi-square construction using stdlib numerical inversion. Sizing uses that bound, preserves the three-pair floor, and reports “no cutoff qualifies” above 24 pairs.

Overlapping differences and single-envelope values remain diagnostics, including spread, drift, and named large differences. Protocol and README state the assumptions; the registration digest is updated.

All changes remain uncommitted. No scope expansion was needed.

## Clause map

References below use ruling `46b-ruling-stage-a-seat-r3.md`, lines 7–11. Production abbreviations: **C** = `joulewise/quiet_predicate_campaign.py`; **P** = `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json`. Test references **T** = `tests/test_quiet_predicate_campaign.py`.

| Ruling clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| L7: “Pairs `(e1,e2), (e3,e4)`” | C:332 | T:49 `test_disjoint_pairs_drop_exactly_one_original_pair_for_each_exclusion` | Anchor pairs on even indices. |
| L7: “BOTH envelopes are retained” | C:330 | T:49, same test | Remove retained-pair filtering. |
| L7: “never re-formed across a gap” | C:325 | T:60–62, same test | Pair neighboring retained entries across missing e3. |
| L7: second-minus-first difference | C:329 | T:57, same test | Reverse subtraction. |
| L7: “minimum retained pairs 4” | C:333 | T:64 `test_four_pairs_minimum_even_when_eight_envelopes_survive` | Require five pairs. |
| L7: “INCONCLUSIVE, no top-up” | C:343, C:363 | T:64, same test | Emit success or enable top-up with insufficient pairs. |
| L8: “sample SD” | C:334 | T:95 `test_overlapping_and_single_values_are_diagnostics_never_sizing` | Use population SD. |
| L8: “df = n − 1” | C:335 | T:79 `test_chi_square_quantiles_and_n_six_n_four_factors` | Use df = n. |
| L8: lower-tail 0.10 quantile; factors 1.762 / 2.266 | C:256, C:336 | T:79, same test | Change quantile probability or confidence factor. |
| L8: upper bound scales sample SD | C:337 | T:95, diagnostic-only test | Use point SD directly. |
| L8: overlapping and single values “as diagnostics” | C:337, C:345 | T:95, diagnostic-only test | Size from either diagnostic series. Both mutants were rejected. |
| L8: spread, drift, named large pairs | C:340, C:346, C:351 | T:95, diagnostic-only test | Omit overlapping spread, zero drift, or suppress large-pair names. |
| L8: normality assumption in memo | C:369 | T:46, exercised by summary tests | Remove the normality statement. |
| L8: documented normality assumption | README:56; P:39 | T:126 `test_frozen_protocol_and_size_use_upper_bound_not_sd` | Remove the stated assumption. |
| L9: sizing formula, δ = 1 J, floor 3 | C:263–266 | T:115 `test_summary_sizing_floor_and_stop_above_24_pairs`; T:126 | Change floor, multiplier, or default δ. |
| L9: stop only above 24 | C:277 | T:115, same test | Change `> 24` to `>= 24`. |
| L7–9: preregistered pairing and constants | P:28–52 | T:126, frozen-protocol test | Change minimum, pairing rule, probability, factors, or sizing constants. |
| L11: protocol digest binding | `joulewise/night_gate.py:46` | `tests/test_night_gate.py:1280` `test_protocol_digest_and_source_are_the_ruled_files` | Leave the old digest or remove its table entry. |

## Verification notes

The requested bench passes **88 tests**. Twelve one-site mutants were rejected.

Canonical verification remains incomplete because the sandbox prevents the existing real-process census test from reading the process list. The lead’s next step is final diff review and canonical verification in the appropriate environment. No live measurement was performed.