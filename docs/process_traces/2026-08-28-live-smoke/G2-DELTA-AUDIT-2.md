```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DO-NOT-MERGE: G2-a lacks an executable calibration bracket, desk selection is not deterministically materialized, and H-3's required add/delete real-path regression coverage does not reach F5-1..4.",
  "workspace": {
    "base_requested": "9a088906bd16902ca528f9fed13c18008e5fda80",
    "base_mode": "exact",
    "head_start": "1cb5b470c35f5ef467dcb80263698b65077ceeba",
    "head_end": "1cb5b470c35f5ef467dcb80263698b65077ceeba",
    "upstream_end": "62be575169e485ee255acea4b6f5adac6ba8a8a9",
    "branch": "feat/window-provenance-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO-NOT-MERGE",
    "items": {
      "1_generated_region": {
        "verdict": "PASS",
        "detail": "Both settle mutations go red. The generator validates exact runbook content, extracts between unique content anchors, and the runsheet has one marker-delimited region whose bytes match regeneration."
      },
      "2_h2_boundary": {
        "verdict": "PASS",
        "detail": "The night chain stops after the post bracket with physical_ahead/mismatch/candidate asserted, emits no completion or pin advance, and the sole advance is the later reviewed desk cycle. F5-2/F5-3 inspect the preserved boundary record; premature-exact and missing-candidate regressions are present."
      },
      "3_h3_exact_sets": {
        "verdict": "FAIL",
        "detail": "Exact-set calls exist at S11-A2 and F5-1..4, but the required add/delete real-path regression matrix is incomplete: membership mutations fail at A2 and skip every F5 assertion; the delete-set case is mocked, while the real deletion test exercises missing bundle bytes instead."
      },
      "4_ratified_arithmetic": {
        "verdict": "FAIL",
        "detail": "The per-row/per-rung jq expressions match count>=5 and exclude large rows from gating, but no executable shortest-qualifying selection or zero-qualifying 4096/refusal branch is emitted. HEAD also still contains the superseded D-166 row; origin/main contains the amendment."
      },
      "5_h4_sequence": {
        "verdict": "FAIL",
        "detail": "Pack gating is confined to G2-b and estate 12 precedes it, but G2-a consumes an undefined G2A_PRE_CAL_CUSTODY and provides no governed pre/post bracket or terminal-candidate producer. The desk selection is prose-only."
      },
      "6_cross_damage": {
        "verdict": "PASS",
        "detail": "The assertion roster, frozen authenticated-order roster, TERMINATE-HERE signal card, exact finalizer refusal, and required preflight checkout argument remain installed."
      }
    },
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "G2-a consumes calibration custody that the runsheet never produces",
        "locations": [
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:245",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:267",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:314"
        ],
        "refutation": "Search the complete runsheet for G2A_PRE_CAL_CUSTODY and G2A post-calibration production. The only executable occurrence is the run_campaign consumer at line 267; there is no reservation plan, bracket session, pre-slot producer, post-slot producer, or candidate-capture command."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "The ratified four-row record never deterministically produces the desk selection",
        "locations": [
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:296",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:309",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:324",
          "tests/test_check_window_provenance.py:532"
        ],
        "refutation": "Supply four rows with small_members=5 and varying all_small_count_ge_5 values. The only jq -e command passes member cardinality, but no command filters qualifying rows, selects the shortest length, emits/pins that result, or implements the no-clear 4096 pre-registration-refusal branch. The test checks only literal substrings."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "title": "H-3's add/delete regression requirement is not demonstrated for F5-1..4 through the real path",
        "locations": [
          "tests/test_check_window_provenance.py:590",
          "tests/test_check_window_provenance.py:629",
          "tests/test_check_window_provenance.py:647",
          "tests/test_check_window_provenance.py:621",
          "scripts/check_window_provenance.py:793",
          "scripts/check_window_provenance.py:820",
          "scripts/check_window_provenance.py:892",
          "scripts/check_window_provenance.py:931"
        ],
        "refutation": "The add-one real-path test fails S11-A2; the downstream F5 assertions are then explicitly skipped. The missing-set test patches campaign_cooldown_evidence, while the real deletion test fails the separate summary_metrics existence check. No add/delete membership test independently reaches F5-1, F5-2, F5-3, or F5-4."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generated Phase D matches pinned runbook bytes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated Phase D matches pinned runbook bytes"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<in-memory runbook and runsheet settle-mutation check using scripts.gen_g2_phase_d>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "runbook_mutation_red=True runsheet_mutation_red=True markers=1/1 source_anchors=1/1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "runbook_mutation_red=True runsheet_mutation_red=True markers=1/1 source_anchors=1/1"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check HEAD^ HEAD",
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
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast; from pathlib import Path; paths=[Path(\"scripts/gen_g2_phase_d.py\"),Path(\"scripts/check_window_provenance.py\"),Path(\"tests/test_check_window_provenance.py\")]; [ast.parse(p.read_text(), filename=str(p)) for p in paths]; print(\"AST OK:\", \", \".join(map(str,paths)))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AST OK: scripts/gen_g2_phase_d.py, scripts/check_window_provenance.py, tests/test_check_window_provenance.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^AST OK:"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests[\\s\\S]*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox exposes no writable temporary directory, so the focused unittest module could not import/run; mutation and static checks did run.",
      "needs": "Rerun the focused module and canonical suite in writable CI or the lead bench."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD's docs/decision_log.md:193 still carries the discarded three-rung margin>=5 D-166 row and the ratification file is absent from HEAD. origin/main at 62be575 contains the amended row/file; changed-path intersection is empty, so an ordinary merge should supply them without conflict.",
      "needs": "Gate the final merge result against origin/main rather than treating the PR head alone as the authority-complete tree."
    }
  ]
}
```

## Findings

- **B1 — blocker:** [SHAKEDOWN-G2-RUNSHEET.md:267](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:267) consumes `$G2A_PRE_CAL_CUSTODY`, but the runsheet never creates it. The promised G2-a pre/post bracket and terminal candidate are prose only. Therefore the four-row prerequisite cannot be produced by this runsheet.

- **B2 — blocker:** [SHAKEDOWN-G2-RUNSHEET.md:296](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:296) correctly computes the ratified fields, but [the desk step](/Users/edr/code/JouleWise-wt-g1/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:324) never executes the shortest-clearing selection or the no-clear 4096/refusal branch. The test at [test_check_window_provenance.py:532](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:532) only checks strings, so wrong or absent selection behavior remains green.

- **B3 — blocker:** The exact-set implementation is present, but the required regression proof is not. The real add-one test at [test_check_window_provenance.py:647](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:647) fails A2, after which [all F5 checks are skipped](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:621). The delete-set case at [line 590](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:590) mocks the join; the real deletion at [line 629](/Users/edr/code/JouleWise-wt-g1/tests/test_check_window_provenance.py:629) exercises missing bundle bytes, not set deletion.

## Residual risk

The focused and canonical suites still need a writable lead/CI rerun. Also verify the final merge tree includes `origin/main`’s amended D-166 row and ratification custody; the PR head alone retains the superseded binding text.