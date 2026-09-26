```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The dry-run bound authenticates unnamed computed records but omits raw replay; a single verified-verdict seam and shared epoch assessment remove the duplicate gate.",
  "workspace": {
    "base_requested": "3e984ecc",
    "base_mode": "exact",
    "head_start": "3e984ecc3b598506c12d652e391b85c6c3c22dd8",
    "head_end": "3e984ecc3b598506c12d652e391b85c6c3c22dd8",
    "upstream_end": "7f007c597535468bf5f05136fd42c15df632fb75",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "Verified verdict seam and immutable result",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "joulewise/battery_float.py; production consumers"
      },
      {
        "row": "One epoch assessment for issuer and dry run",
        "action": "wait_for",
        "wait_for": "Verified verdict seam",
        "collision_surface": "scripts/issue_calibration_acceptance_generation.py"
      },
      {
        "row": "Mutation regressions and AST boundary test",
        "action": "wait_for",
        "wait_for": "Both shared functions",
        "collision_surface": "tests/"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n 'battery_float\\.(load_committed_verdict|validate_window|compare_verdict)|^[[:space:]]*(window|result) = validate_window\\(' --glob '*.py' joulewise scripts tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/issue_calibration_acceptance_generation.py:358:            record = battery_float.load_committed_verdict(",
          "scripts/issue_calibration_acceptance_generation.py:1602:            difference = battery_float.compare_verdict(record, recomputed)",
          "joulewise/battery_float.py:514:    window = validate_window(session)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "joulewise/battery_float.py:514:"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport ast\nfrom pathlib import Path\npaths = [Path('scripts/issue_calibration_acceptance_generation.py'), Path('scripts/calibration_cadence_report.py')]\nfor path in paths:\n    tree = ast.parse(path.read_text())\n    hits = []\n    for node in ast.walk(tree):\n        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'battery_float' and node.func.attr in {'load_committed_verdict', 'validate_window', 'compare_verdict'}:\n            hits.append((node.lineno, node.func.attr))\n    print(f'{path}: {hits}')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/issue_calibration_acceptance_generation.py: [(358, 'load_committed_verdict'), (1602, 'compare_verdict'), (1586, 'validate_window'), (1593, 'load_committed_verdict'), (243, 'validate_window'), (250, 'load_committed_verdict'), (263, 'compare_verdict')]",
          "scripts/calibration_cadence_report.py: [(93, 'compare_verdict'), (81, 'validate_window'), (85, 'load_committed_verdict')]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scripts/calibration_cadence_report.py:"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A Python AST boundary test prevents ordinary direct calls; dynamic reflection could still bypass it and needs review discipline.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

| Row | Action | Wait for | Collision surface |
|---|---|---|---|
| Verified verdict seam | Start now | — | `battery_float.py`, then consumers |
| Shared epoch assessment | Wait | Verified seam | Issuer and dry-run logic |
| Regressions and AST guard | Wait | Both shared functions | Tests |

## Critical path

**Put the complete per-window operation in [battery_float.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/joulewise/battery_float.py:543):**

```python
def authenticate_committed_verdict(
    repo_root: Path | str,
    session_id: str,
    *,
    session: Any,
    preregistration_sha256: str,
) -> VerifiedBatteryVerdict: ...
```

It must require a nonempty, valid registration digest; call `load_committed_verdict` **first**; then call `validate_window` on raw bytes; then require `compare_verdict(record, recomputed) is None`. It returns only a frozen `VerifiedBatteryVerdict` containing `session_id`, recorded `status`, an immutable tuple of frozen slot records, `file_sha256`, and `commit`. There is no return path for an unauthenticated record. Keep `verdict_record()`’s direct `validate_window` call at line 514: it is the **producer**, not a committed-verdict consumer.

Use one `BatteryVerdictRefusal(RuntimeError)` with `code`, `session_id`, and `detail`; preserve the underlying exception as `__cause__`. Specify these exact messages:

| Code | Message |
|---|---|
| `invalid_request` | `battery-float verification for <id> requires a valid preregistration_sha256` |
| `missing_record` | `battery-float harvest verdict missing or uncommitted for <id>: <NoRecord.reason>` |
| `custody_failure` | `battery-float custody failure for <id>: <CustodyFailure.detail>` |
| `disagreement` | `battery-float harvest verdict for <id> cannot be re-established from raw bytes (<difference>)` |

The issuer can append its existing `; not issued` wording. The dry run must turn **every** refusal into exit 5 and an admissibility blocker. It must not print a recomputed battery label when the committed record is absent: the current named path computes and prints that label before authentication.

**Share the epoch decision as well as the window check.** Add one `assess_battery_epoch(snapshot, registration_ids, repo_root, preregistration_sha256, target_epoch, dispositions) -> BatteryEpochAssessment` in the issuer module. It calls `_battery_computed_set` once, authenticates *every eligible member* through the new seam, and returns frozen `verdicts` and `non_pass_ids`. Keep the contract’s existing scope and exemptions for set S. Authenticate named terminal sessions before the exemption scan so the current no-member-evidence-before-verdict gate remains intact. Both `registration_dry_run` and `_prepare_candidate` consume this assessment; neither repeats a verdict loop or derives its own non-pass count. The dry run renders counts and blockers from it; the issuer applies its declared-confounded exact-set check to it.

Call-site changes at 3e984ecc:

- [Issuer script](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:181): replace the named loop’s primitive calls at **243, 250, 263** and the separate bound’s record-only call at **358** with the assessment. Remove `_dry_run_epoch_bound`’s second verdict implementation at **332–373**. Replace `_prepare_candidate`’s loop at **1573–1612** with the same assessment; retain the exact-set and replacement policy at **1613–1640**.
- [Cadence report](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/calibration_cadence_report.py:60): replace primitive calls at **81, 85, 93** with one seam call; derive `diagnostic_only` from its recorded status.
- [Battery verdict producer](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-sol/scripts/issue_calibration_acceptance_generation.py:1450): retain `verdict_record`; it creates the record before commit.

**Tests that distinguish all three rounds:** use a committed W1, W1-prime, W2 fixture with only W1-prime and W2 named. First make W1 a committed non-pass: `check` must exit 5 for omission, while prepare refuses. Then remove W1’s record and, separately, bind it to a different registration digest: both commands must refuse for missing authentication. Finally keep W1’s committed record but delete or alter W1 raw battery bytes: `check` must exit 5 for custody failure and prepare must refuse, with no exclusion or omission verdict substituted. Add a committed, structurally valid record whose status or compared digest disagrees with intact raw bytes; this specifically proves the compare step runs for an **unnamed** session. Repeat the custody and disagreement cases for a named session and the cadence report. Existing tests cover parts of rounds 1 and 2; the unnamed replay and disagreement cases are the missing discriminators.

Add an AST test over **all production Python files** under `joulewise/` and `scripts/` that forbids calls or direct imports of `load_committed_verdict`, `validate_window`, and `compare_verdict` outside `battery_float.py`. Resolve import aliases; exempt the producer call inside `verdict_record`. Assert the new seam contains the three primitive calls. The executed AST prototype found **10 direct production call sites** on this head, so that guard would fail before the refactor and pass only after consumers migrate.

The grep found no other production primitive callers. Its remaining hits are direct unit-test calls in `test_battery_float.py`, `test_validate_powermetrics_fiducial_derivation_only.py`, and one issuer test; those test the primitives themselves. `issue_epoch_continuation.py` is not a primitive caller and currently refuses Revision-5 sessions before member evidence at lines 81–88.