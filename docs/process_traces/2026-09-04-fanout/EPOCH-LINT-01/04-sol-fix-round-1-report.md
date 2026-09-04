```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured refuter blockers B1-B5 with the ruled runsheet census and authenticated overlay, exact token/commit/symbol checks, and passing focused regressions and replays.",
  "workspace": {
    "base_requested": "e0371ab3c823141bf310e8a0fc62191ef40dfac8",
    "base_mode": "exact",
    "head_start": "e0371ab3c823141bf310e8a0fc62191ef40dfac8",
    "head_end": "e0371ab3c823141bf310e8a0fc62191ef40dfac8",
    "upstream_end": "36e7d539c795cf8a60f2bace8d640ff81499c336",
    "branch": "feat/2026-09-04-fan-EPOCH-LINT-01"
  },
  "pathspec": [
    "configs/process/epoch_lint_b1_join_replay.json",
    "configs/process/epoch_lint_f0_f3_replay.json",
    "configs/process/epoch_lint_post_cure_replay.json",
    "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md",
    "docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/04-sol-fix-round-1-report.md",
    "scripts/lint_runsheet_epoch.py",
    "tests/test_lint_runsheet_epoch.py"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_lint_runsheet_epoch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 3.799s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 15 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "set -euo pipefail; for cfg in configs/process/epoch_lint_f0_f3_replay.json configs/process/epoch_lint_b1_join_replay.json; do out_file=$(mktemp); set +e; python3 scripts/lint_runsheet_epoch.py \"$cfg\" > \"$out_file\"; replay_rc=$?; set -e; jq -c '{status,mode,finding_count,kinds:[.findings[].kind],detail:(.findings[0].detail // null)}' \"$out_file\"; test \"$replay_rc\" -eq 1; done",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"REFUSE\",\"mode\":\"historical_replay\",\"finding_count\":3,\"kinds\":[\"symbol_existence\",\"contract_required_cli_inputs\",\"file_line_coordinates\"],\"detail\":\"symbol 'test_successor_pinset_is_byte_pinned_at_fixation' is absent from tests/test_receipt_histsem.py\"}", "{\"status\":\"REFUSE\",\"mode\":\"historical_replay\",\"finding_count\":1,\"kinds\":[\"file_line_coordinates\"],\"detail\":\"cites scripts/generate_arm_readiness.py:28-186; definitions span 28-192\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "REFUSE.*finding_count.*3.*REFUSE.*28-186.*28-192"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/lint_runsheet_epoch.py configs/process/epoch_lint_post_cure_replay.json | jq -c '{status,mode,finding_count,check_count}'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"PASS\",\"mode\":\"historical_replay\",\"finding_count\":0,\"check_count\":3}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS.*finding_count.*0.*check_count.*3"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp.phYQAKwDHU/repo/scripts/lint_runsheet_epoch.py /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp.phYQAKwDHU/stage/contract.json --repository /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp.phYQAKwDHU/repo | jq -c '{status,mode,finding_count,check_count,overlay_file_count}'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"status\":\"PASS\",\"mode\":\"ratification\",\"finding_count\":0,\"check_count\":3,\"overlay_file_count\":1}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS.*ratification.*finding_count.*0.*check_count.*3.*overlay_file_count.*1"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 -m py_compile scripts/lint_runsheet_epoch.py tests/test_lint_runsheet_epoch.py && git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The no-commit instruction required the full runsheet ratification smoke to use an isolated temporary commit; the wired procedure reruns at the final exact landing head.",
      "needs": "Lead final-head ratification and ordinary merge gate."
    }
  ]
}
```

## Change

The resumed round installs the scope-granted S-0 declarations and ratification wire. Every one of 49 executable zsh blocks now begins with an inline declaration; the three dependency obligations live beside the owning line-audit, post-mint freeze, and fixation-test blocks. Before later gates, the runsheet builds a post-image from the reviewed fixation delta, seals its base/result bytes and named base, runs the checker, and retains the generated contract plus `003a-epoch-lint-ratification.json`. The stale executed CLI range is recut from `28-192` to `28-199` at the current named head.

| Finding | Cure | Production and regression |
|---|---|---|
| B1 | Complete inline block census, exact ratification invocation, named-base byte-authenticated overlay, occupied-root refusal | `s0-runsheet-r4.md:829,889,1148,2881,4188`; `lint_runsheet_epoch.py:267,417,558`; `test_lint_runsheet_epoch.py:341,349,364,380,395` |
| B2 | Tokenized logical-command prefixes and exact option tokens; comments and echo text cannot discharge an invocation | `lint_runsheet_epoch.py:278`; `test_lint_runsheet_epoch.py:202` |
| B3 | Only a full lowercase 40-hex object ID resolving to itself is accepted | `lint_runsheet_epoch.py:71`; `test_lint_runsheet_epoch.py:239` |
| B4 | Whole-symbol starts include the earliest decorator | `lint_runsheet_epoch.py:382`; `test_lint_runsheet_epoch.py:244` |
| B5 | Module/class `Assign` and `AnnAssign` nodes are resolvable constants | `lint_runsheet_epoch.py:117`; `test_lint_runsheet_epoch.py:269` |

Magistrate-owned completion row, to apply after the final-head gate:

`| EPOCH-LINT-01 | P2 Next Slice | 2026-09-04 | Build the mechanical three-kind runsheet epoch lint ordered by D-153 synthesis R-5 | COMPLETE: exact historical replays reproduce the F0-F3 symbol/input failures and B1 coordinate drift; the S-0 runsheet carries a complete inline block census, authenticated named-base fixation overlay, exact ratification wire, and clean three-kind transcript. Evidence: docs/process_traces/2026-09-04-fanout/EPOCH-LINT-01/04-sol-fix-round-1-report.md. |`

## Clause map

| Ruling clause (`01-magistrate-rulings.md:11`) | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| “Inline obligation declarations in the runsheet” | `s0-runsheet-r4.md:675-4255`; checks at `:1148`, `:2881`, `:4188` | `test_lint_runsheet_epoch.py:380` | Remove any declaration or the exact wire; census parsing fails. |
| “authenticated patch overlay on a named base” | `lint_runsheet_epoch.py:417`; runtime construction `s0-runsheet-r4.md:844-883` | `test_lint_runsheet_epoch.py:341,395` | Change content without resealing, change/reseal the base, or preoccupy the staging root; each refuses. |

## Verification notes

The whole suite was not run, per the explicit preflight rule. `rg` found no Python importer beyond the focused test module. V4 copied the scoped landing into an isolated clone and committed only there (`6d7abdf5d098b681e9a33beb7ecc5554695fe9c9`) so the exact-revision contract could exercise the real 49-block runsheet without violating the no-commit instruction.

## Residual risk

The magistrate must retire the kernel task and add the completion row after the final-head ratification reruns on the committed landing object.
