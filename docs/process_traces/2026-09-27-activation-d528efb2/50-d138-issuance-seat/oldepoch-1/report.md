```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Pinned-main replay of a recorded 25F84 member refused for a non-stale reason; D-138 must stop under the cold-gate rule.",
  "workspace": {
    "base_requested": "e7c8bcc6",
    "base_mode": "exact",
    "head_start": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "head_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "measurement": "sw7bfloor-df-ph-decode-abs-r01 in the passed 2026-07-29 Qwen2.5 7B decode-floor window",
    "main": {
      "exit_code": 1,
      "acceptance_id": "d079_calibration_acceptance_v2_n17_r7",
      "acceptance_freshness": "fresh",
      "bracket_status": "failed",
      "refusal": "instrument_calibration_bracket_missing"
    },
    "rows": [
      {
        "row": "D-138 merge",
        "action": "do_not_start",
        "reason": "The main-side refusal is not a stale-calibration refusal."
      },
      {
        "row": "Head replay",
        "action": "start_now",
        "reason": "Runner and comparator are ready for diagnostic comparison."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/bin/zsh /tmp/oldepoch-d528efb2/replay.sh /Users/edr/code/JouleWise-wt-oldepoch-main-d528efb2 /tmp/oldepoch-d528efb2/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["{\"status\": \"failed\", \"reasons\": [\"instrument_calibration_bracket_missing\"]}"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "instrument_calibration_bracket_missing"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/oldepoch-d528efb2/compare.py /tmp/oldepoch-d528efb2/main /tmp/oldepoch-d528efb2/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL CONTENT IDENTICAL"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ALL CONTENT IDENTICAL"
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
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The selected production bracket analysis refuses on main for instrument_calibration_bracket_missing, while R7 itself authenticates as fresh. This is outside the ruling's proceed conditions.",
      "needs": "Do not merge D-138. Resolve the old-epoch analysis route or select and replay another recorded analysis that meets the ruling before proceeding."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full 57-member governed floor extraction was interrupted after prolonged raw-plist revalidation; the completed replay evaluates the production bracket component for one recorded member.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| D-138 merge | do_not_start | A qualifying old-epoch replay under ruling §10 item 2 | None; repository unchanged |
| Head diagnostic | start_now | D-138 head worktree path | Read-only custody; output must be a new `/tmp` directory |

The chosen member belongs to a passed, claim-bearing 25F84 window whose [close-out record](/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md) reports two governed decode-floor values. The replay calls the production bracket evaluator used by that analysis. It reads the recorded member and the pinned 276-row ledger, including the old-epoch observations. It writes only under `/tmp`.

Run the head side, then compare:

```sh
/bin/zsh /tmp/oldepoch-d528efb2/replay.sh <D-138-head-worktree> /tmp/oldepoch-d528efb2/head
/opt/homebrew/bin/python3 -B /tmp/oldepoch-d528efb2/compare.py /tmp/oldepoch-d528efb2/main /tmp/oldepoch-d528efb2/head
```

[Main outputs](/tmp/oldepoch-d528efb2/main/output-sha256.txt) record every primary output digest. `bracket.json` is `32562d34a87888022cd5dc5f256d81bafed9d987fefee8549762299d42a4da4c`; the hash manifest itself is `63df61200c4dd16430f84752dee162f08b81fb17064568072e61a876be829376`. Stdout contains the refusal, stderr is empty, and exit status is 1. The [runner](/tmp/oldepoch-d528efb2/replay.sh), [bracket replay](/tmp/oldepoch-d528efb2/bracket_replay.py), and [comparator](/tmp/oldepoch-d528efb2/compare.py) are ready.

## Critical path

The main-side `instrument_calibration_bracket_missing` refusal already triggers the ruling’s **stop** condition. A head-side result can diagnose the change, but cannot turn this main-side replay into a qualifying proceed result.