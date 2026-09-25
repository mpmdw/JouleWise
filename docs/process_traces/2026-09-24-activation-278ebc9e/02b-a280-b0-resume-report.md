```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "B0 routing is implemented and the requested tests pass in the worktree, but the sandbox prevents staging and committing it.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "74b4dc65c9bb0f2bdf8289157b374747fc9b47d5",
    "head_end": "74b4dc65c9bb0f2bdf8289157b374747fc9b47d5",
    "upstream_end": "74b4dc65c9bb0f2bdf8289157b374747fc9b47d5",
    "branch": "feat/2026-09-24-a280-b0-kind-dispatch"
  },
  "pathspec": [
    "joulewise/evidence_night.py",
    "joulewise/night_gate.py",
    "joulewise/night_kinds.py",
    "joulewise/zero_capture_facts.py",
    "scripts/gen_evidence_night.py",
    "scripts/run_night.py",
    "tests/test_evidence_night.py",
    "tests/test_kind_dispatch_literals.py",
    "tests/test_night_kinds.py"
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
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_gen_evidence_night tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_zero_capture_facts tests.test_kind_dispatch_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 598 tests in 1271.187s", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check 2ea6a7ec HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2-worktree",
      "kind": "lint",
      "cmd": "git diff --check 2ea6a7ec",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_third_row_notice_text_and_corecaptured_flag",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: '(TEST; DIAGNOSTIC_NO_PACK)' not found",
          "Ran 1 test in 9.347s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3-restored",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_third_row_notice_text_and_corecaptured_flag tests.test_kind_dispatch_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 9.371s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "commit",
      "kind": "other",
      "cmd": "git add joulewise/evidence_night.py joulewise/night_gate.py joulewise/night_kinds.py joulewise/zero_capture_facts.py scripts/gen_evidence_night.py scripts/run_night.py tests/test_evidence_night.py tests/test_night_kinds.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/wt-7370d0fb-a280b0/index.lock': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The linked worktree stores its Git index outside the writable sandbox; git add was denied. No commit was made.",
      "needs": "Lead must commit this exact worktree diff in a Git-writable context, or resume the seat in a worktree with writable Git metadata."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V1 and V3 passed or killed their mutant against the completed working tree, while V2 at HEAD checks only WIP commit 74b4dc65. Final-head V1–V3 cannot be claimed without a commit.",
      "needs": "After committing, replay V1–V3 and git diff --check 2ea6a7ec HEAD at the new final head."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide canonical suite was not run; the brief's 598-test V1 suite passed.",
      "needs": "Lead may run the canonical suite during final verification."
    }
  ]
}
```

## Change

**R1 audit of `74b4dc65`:**

| Brief item | WIP finding and completion |
|---|---|
| 1(a) | The draft routed the listed evidence sites through a row, but could accept a wrapper kind that disagreed with its bound chain source and surfaced some unreadable kinds without a typed refusal. The worktree now checks the source declaration and refuses unreadable kinds. It adds no bare `state["kind"]` authority. |
| 1(b) | The draft selected notice clauses and subject text from the row and gated the corecaptured sentence. The unchanged golden notice passes. |
| 1(c) | The draft selected manifest, executor, and wrapper literals, but chose the first row when two rows named one chain source. That ambiguity now refuses. The idle wrapper golden passes. |
| 1(d) | The draft’s unrestricted missing-chain idle fallback was a second kind authority. Cleanup also trusted C5 without comparing a present wrapper, and calibration lost historical artifact names. The worktree uses a validated C5 receipt when a delivered wrapper is missing, compares C5 with a present wrapper, and keeps the calibration inventory explicit in its row. Malformed-plan reporting retains the historical idle inventory. |
| 1(e) | The draft changed C5 routing without adding B2’s registration payload-kind comparison. A row missing its wrapper prefix could raise an untyped error; it now refuses through C5. |
| 1(f) | The draft added a test-only third row and literal scan, but had a stale refusal expectation, line-number-bound allowlist entries, no duplicate-hit check, and no mutation evidence. These are corrected. Unknown-kind admission remains refused. |

No scored row, scored manifest, armable kind, or registration digest was added. `test_base_archive_byte_goldens` and `test_refusal_parity` passed without editing their expected bytes.

**Site map.** Lines are `2ea6a7ec → working tree`. Test keys: **T3** = `test_unhandled_third_row_routes_or_refuses_across_shared_entries`; **N** = `test_third_row_notice_text_and_corecaptured_flag`; **G** = `test_third_row_generator_selects_manifest_executor_and_literals`; **Gate** = `test_gate_refuses_evidence_row_without_wrapper_literals`; **Cal** = `test_calibration_keeps_legacy_artifact_and_courier_inventory`; **Gold** = `test_base_archive_byte_goldens`; **Lit** = `test_only_reviewed_idle_literals_remain_in_shared_dispatch`. All are in `tests/test_night_kinds.py` except **Lit**, which is in `tests/test_kind_dispatch_literals.py`.

| Site | Base → worktree file:line | Test |
|---|---|---|
| `locations` | `evidence_night.py:158 → :158` | T3 |
| `prior_records` | `evidence_night.py:219 → :219` | T3 |
| `sealed_candidate`, including H-side selection | `evidence_night.py:241 → :241` | T3, Gold |
| `notice_subject` | `evidence_night.py:296 → :337` | N, V3 |
| `render_notice` row/protocol selection | `evidence_night.py:300 → :342` | N, Gold |
| Idle-only notice clauses | `evidence_night.py:323 → :376` | N, Gold |
| Corecaptured sentence flag | `evidence_night.py:340 → :380` | N, Gold |
| H-side census snippet | `evidence_night.py:1026 → :1080` | T3 |
| `notice_unused` | `evidence_night.py:1658 → :1711` | T3 |
| `prepare` | `evidence_night.py:371 → :413` | T3, Gold |
| `candidate_state` | `evidence_night.py:586 → :633` | T3, `test_refusal_parity` |
| `sealed_state` | `evidence_night.py:612 → :663` | T3 |
| Candidate kind binding | `evidence_night.py:1064 → :308, :1112` | T3, N |
| Row fields | `night_kinds.py:24, :49 → :24, :48` | T3, Cal |
| Wrapper generator | `gen_evidence_night.py:20, :55 → :20, :60` | G, Gold, `test_generator_refuses_two_rows_for_one_chain_source` |
| Gate C5 routing | `night_gate.py:1388 → :1391` | T3, Gate |
| Installer receipt routing | `night_agent_install.py:793 → :793` | T3 |
| Installer binding and evidence receipt | `night_agent_install.py:887, :925 → :892, :936` | T3, V1 installer tests |
| Installer render inspection | `night_agent_install.py:1164 → :1180` | T3 |
| Driver kind source and inventory | `run_night.py:1029 → :1005, :1032` | T3, Cal |
| Durable artifact path | `run_night.py:1095 → :1089, :1132` | Cal, V1 driver tests |
| Courier prompt routing | `run_night.py:1218 → :1223` | T3, Cal |
| Cleanup routing | `run_night.py:1324 → :1355` | T3, `test_evidence_identity_dispatches_cleanup_without_reading_wrapper` |
| Malformed-plan result inventory | `run_night.py:1602 → :1609` | `test_empty_non_json_and_missing_plans_refuse_and_attempt_courier` |
| Driver probe dispatch | `run_night.py:3690 → :3721` | T3 |
| Zero-capture facts | `zero_capture_facts.py:99 → :80, :102` | T3, V1 zero-capture tests |
| Shared-source literal guard | new `test_kind_dispatch_literals.py:52` | Lit |

## Verification notes

V3 temporarily replaced the notice subject’s row label with `kind_row(KIND).notice_subject_label`. The third-row notice test failed on the resulting idle `EVIDENCE` subject. The original file was restored; the focused test and literal guard then passed. Both diff checks returned exit 0.

The first V1 run exposed malformed-plan reporting and missing-wrapper cleanup regressions. Those were fixed; the exact V1 replay then passed all 598 tests. A separate 8-second supervision timeout on the first run passed on focused rerun and did not recur in V1.

## Residual risk

**NEEDS_SCOPE / environment handoff:** `git add` cannot create the linked worktree’s index lock under `/Users/edr/code/JouleWise/.git/worktrees/...` in this sandbox. The nine session-modified paths remain unstaged. The lead’s next exact step is to commit the worktree diff on top of `74b4dc65` in a Git-writable context, then rerun V1–V3 and `git diff --check 2ea6a7ec HEAD` at that commit.