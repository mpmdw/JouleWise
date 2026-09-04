```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: all four prior defect signatures are cured, but exact interval ordering can be bypassed through binary-float aliasing of large JSON integers.",
  "workspace": {
    "base_requested": "ba73a35e",
    "base_mode": "exact",
    "head_start": "ba73a35ed54325197ab3da561e3f0ca209457ad1",
    "head_end": "ba73a35ed54325197ab3da561e3f0ca209457ad1",
    "upstream_end": "ba73a35ed54325197ab3da561e3f0ca209457ad1",
    "branch": "feat/2026-09-04-transfer-result-renderer"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-transfer-renderer/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "same_signature": {
      "result": "none",
      "decision": "No prior defect signature repeats, so the mandatory consult route is not triggered."
    },
    "dispositions": [
      {"id": "execution:F1/contract:CR-01", "result": "CURED"},
      {"id": "execution:F2/contract:CR-03", "result": "CURED"},
      {"id": "contract:CR-02", "result": "CURED"},
      {"id": "contract:CR-04", "result": "CURED"}
    ],
    "regressed": [],
    "findings": [
      {
        "id": "NEW-01",
        "severity": "should_fix",
        "file": "joulewise/results_fill_transfer.py",
        "line": 346,
        "title": "Exact interval ordering is weakened by binary-float coercion",
        "counterfactual": "A freshly reissued result with lower=9007199254740993 and upper=9007199254740992 validates and renders because both integers alias when converted to float."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.026s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_powermetrics_fiducial.ActiveCaptureMethodTests.test_capture_clock_dispatch_emits_active_schema_and_tracks_registry tests.test_powermetrics_fiducial.EvidenceTests.test_valid_evidence_carries_bindings_and_bound tests.test_powermetrics_fiducial.FrozenProtocolTests.test_estimator_byte_drift_refuses_acceptance_as_stale",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 0.505s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 3.099s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "sed -n '/^<!-- CF1 START -->$/,/^<!-- CF1 END -->$/p' docs/process_traces/2026-09-04-transfer-renderer/04-delta-reaudit-round-1.md | sed '1d;$d' | PYTHONDONTWRITEBYTECODE=1 python3 -",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CR01_nonselected_larger=STOP_FILL",
          "CR01_bundle_tie_loser=STOP_FILL",
          "CR01_edge_tie_loser=STOP_FILL",
          "CR02_revision=STOP_FILL",
          "CR02_digest=STOP_FILL",
          "CR03_false_complete=STOP_FILL",
          "CR03_truthful_9_18=accepted",
          "CR03_truthful_10_19=accepted",
          "CR04_registry=registered",
          "NEW_inverted_exact_interval=accepted",
          "fixtures_restored=true"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "CR01_nonselected_larger=STOP_FILL[\\s\\S]*NEW_inverted_exact_interval=accepted[\\s\\S]*fixtures_restored=true"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "shasum -a 256 joulewise/powermetrics_fiducial.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py"]},
      "expected": {"exit_code": 0, "tail_regex": "^386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "R3 remains fixture-only; the capture producer at d67ee56c is still unreviewed and no live value is issued.",
      "needs": "Keep producer acceptance as a separate gate."
    }
  ]
}
```

## Findings

### NEW-01 — should_fix — Exact interval ordering is weakened by binary-float coercion

`_validate_edge_record` checks `upper < lower` after converting both exact JSON
numbers to `float` (`joulewise/results_fill_transfer.py:343-347`). Distinct JSON
integers above 2^53 can therefore alias. A reissued projection with
`lower=9007199254740993`, `upper=9007199254740992`, and exactly replayed
composed/global bounds validated and rendered all nine `not_supported` sites,
despite the interval being inverted in exact arithmetic. Compare ordering with
`_decimal(upper) < _decimal(lower)`, as the surrounding replay and relation
checks already do, and add this mutation to the acceptance test.

### Prior finding dispositions

- **Execution F1 / Contract CR-01 — CURED.** Reissued nonselected-larger,
  later-bundle tie-loser, and rising-edge tie-loser mutations all returned
  nine-site `STOP_FILL`; missing/duplicate/swapped inventory cases are asserted
  by the passing renderer test.
- **Execution F2 / Contract CR-03 — CURED.** A false complete 10/20 refusal
  returned `STOP_FILL`; truthful 9/18 run and 10/19 edge shortfalls rendered.
- **Contract CR-02 — CURED.** Freshly reissued estimator revision and digest
  changes returned `STOP_FILL`; the fixed digest matches the producer bytes.
- **Contract CR-04 — CURED.** The registry now names the exact ordered four-code
  enum and reason-to-field semantics consumed by the validator.
- **REGRESSED:** none.

**Same-signature decision:** no prior defect signature repeats. `NEW-01` is a
distinct exact-number validation defect, so no consult is routed.

<!-- CF1 START -->
import copy, hashlib, json
from pathlib import Path
from tests.test_results_fill_transfer import _all_stop, _render, _reissue

root = Path("tests/fixtures/results_fill_transfer")
paths = sorted(root.glob("*.json"))
before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
s = json.loads((root / "supported.json").read_text())
n = json.loads((root / "not_evaluated.json").read_text())
state = lambda v: "STOP_FILL" if _all_stop(_render(_reissue(v))) else "accepted"
checks = []

v = copy.deepcopy(s)
v["edge_records"][-1].update(fitted_residual_interval_s={"lower": -.498, "upper": .1}, composed_absolute_residual_bound_s=.5)
checks.append(("CR01_nonselected_larger", state(v), "STOP_FILL"))
for label, index in (("CR01_bundle_tie_loser", 18), ("CR01_edge_tie_loser", 7)):
    v = copy.deepcopy(s)
    v["edge_records"][index].update(fitted_residual_interval_s={"lower": -.02, "upper": .018}, effective_clock_anchor_bound_s=.002, composed_absolute_residual_bound_s=.022)
    v["largest_inserted_gap_edge"] = copy.deepcopy(v["edge_records"][index])
    checks.append((label, state(v), "STOP_FILL"))
for label, field, replacement in (("CR02_revision", "estimator_revision", "arbitrary_changed_estimator.v99"), ("CR02_digest", "estimator_source_sha256", "0" * 64)):
    v = copy.deepcopy(s)
    v["source_capture"][field] = replacement
    checks.append((label, state(v), "STOP_FILL"))
v = copy.deepcopy(s)
v.update(largest_composed_edge_residual_bound_s=None, largest_inserted_gap_edge=None, support_outcome="not_evaluated", reason_codes=["run_census_incomplete"])
checks.append(("CR03_false_complete", state(v), "STOP_FILL"))
checks.append(("CR03_truthful_9_18", state(n), "accepted"))
v = copy.deepcopy(s)
v["edge_records"].pop()
v["census"]["observed_edge_count"] = 19
v.update(largest_composed_edge_residual_bound_s=None, largest_inserted_gap_edge=None, support_outcome="not_evaluated", reason_codes=["edge_census_incomplete"])
checks.append(("CR03_truthful_10_19", state(v), "accepted"))
registry = " ".join(Path("docs/paper/results-fill-registry.md").read_text().split())
registered = all(x in registry for x in ("source_capture_refused", "run_census_incomplete", "edge_census_incomplete", "pulse_derived_timing_bound_unavailable", "present iff"))
checks.append(("CR04_registry", "registered" if registered else "missing", "registered"))
v = copy.deepcopy(s)
v["edge_records"][-1].update(fitted_residual_interval_s={"lower": 9007199254740993, "upper": 9007199254740992}, effective_clock_anchor_bound_s=0, composed_absolute_residual_bound_s=9007199254740993)
v["largest_inserted_gap_edge"] = copy.deepcopy(v["edge_records"][-1])
v["largest_composed_edge_residual_bound_s"] = 9007199254740993
v["support_outcome"] = "not_supported"
checks.append(("NEW_inverted_exact_interval", state(v), "accepted"))
for label, actual, expected in checks:
    print(f"{label}={actual}")
    assert actual == expected, label
after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
print("fixtures_restored=" + str(before == after).lower())
assert before == after
<!-- CF1 END -->

## Residual risk

The R3 path remains fixture-only; the unreviewed capture producer at `d67ee56c`
was not executed. The canonical suite was intentionally excluded by the
prompt's preflight rule; only the renderer test, three named producer/validator
tests, and two registry modules ran.
