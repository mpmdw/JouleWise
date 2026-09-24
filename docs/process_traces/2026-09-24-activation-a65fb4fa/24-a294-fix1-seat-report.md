```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the A294+A295 gate fixes and documentation updates; final named acceptance passed.",
  "workspace": {
    "base_requested": "5ef72338",
    "base_mode": "exact",
    "head_start": "5ef72338b225281b951f4e3ccd8ca7a1675f21fb",
    "head_end": "5ef72338b225281b951f4e3ccd8ca7a1675f21fb",
    "upstream_end": null,
    "branch": "feat/2026-09-24-a294-t0-clean-tree"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py",
    "tests/test_night_kinds.py",
    "scripts/run_night.py",
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_gate tests.test_evidence_night tests.test_night_kinds tests.test_run_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 667 tests in 422.531s", "OK (skipped=9)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=9\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The journal_block watchdog test timed out in an intermediate suite run, as it had in the review baseline; it passed in the final run.",
      "needs": "Magistrate to retain the existing flaky-test observation during final review."
    }
  ]
}
```

## Change

- **P1–P2:** [night_gate.py:1272](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1272) disables fsmonitor in the exact status argv and cites the probe in C5. Regressions: `test_real_git_status_disables_fsmonitor_hook` and `test_clean_measurement_checkout_proceeds_with_porcelain_evidence` in [test_night_gate.py](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:859).
- **P3:** [run_night.py:358](/Users/edr/code/wt-a65fb4fa-a294/scripts/run_night.py:358) decodes timeout output as UTF-8 with replacement. `test_partial_output_timeout_keeps_status_refusal_evidence` [executes partial output and checks the refusal evidence](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:904).
- **P4–P5:** [arm_retry.py:42](/Users/edr/code/wt-a65fb4fa-a294/joulewise/arm_retry.py:42) has the exact requested description. Its copies in [NIGHT_HANDBACK.md:92](/Users/edr/code/wt-a65fb4fa-a294/docs/process/NIGHT_HANDBACK.md:92) and the [runbook:1885](/Users/edr/code/wt-a65fb4fa-a294/docs/phase_2/derivation_night_runbook.md:1885) were refreshed from `arm_retry.render_policy()`; `test_both_document_blocks_are_exact` checks that mechanism, and `test_stale_plan_operator_description_names_clone_cleanliness` pins the wording. The [runbook:770](/Users/edr/code/wt-a65fb4fa-a294/docs/phase_2/derivation_night_runbook.md:770) now gives both refusal codes and the re-cut remedy; `test_runbook_describes_t0_clone_status_and_recut_remedy` pins it in [test_arm_retry.py:148](/Users/edr/code/wt-a65fb4fa-a294/tests/test_arm_retry.py:148).
- **P6–P7:** `test_measurement_checkout_detail_shows_only_first_five_lines` [checks six lines](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:870). The [run_night fake:239](/Users/edr/code/wt-a65fb4fa-a294/tests/test_run_night.py:239) reads the current plan root and falls through to its results table for other roots; `test_status_fake_only_cleans_planned_measurement_root` pins that behavior.
- **P8–P9:** The T6 commit [uses signing and hook overrides under hostile global Git config](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_gate.py:944). The A295 clone setup [uses the overrides](/Users/edr/code/wt-a65fb4fa-a294/tests/test_night_kinds.py:415) and its commit uses the existing `commit_fixture` helper; `test_committed_window_mutant_refused_by_real_prepare` exercises that path. [night_gate.py:1277](/Users/edr/code/wt-a65fb4fa-a294/joulewise/night_gate.py:1277) records `null` on non-zero exit, caps measured lines at 50 with a truncation key only when needed, and joins the first five detail lines with `; `. Regressions: `test_measurement_checkout_status_exit_128_is_probe_error`, `test_measurement_checkout_porcelain_is_capped_at_fifty`, and the P6 detail test.

## Verification notes

The final named command passed: **667 tests, 9 skipped**. `git diff 5ef72338 --stat` lists only the nine `WRITE_SCOPE` paths; no commit was made. An intermediate run exposed plan-root mismatches in the tightened fake; those were fixed before the passing run. No failure was attributed to sandbox denial of `ps`.

## Residual risk

The magistrate should double-check the previously observed `journal_block` timeout, record NIT-1’s later-refusal evidence addition in the PR body, and retain the accepted NIT-5 companion-fixture note.