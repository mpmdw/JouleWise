```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The July 29 numbers came from a pre-D-109 extraction; no recorded inputs make its default-acceptance bracket pass on current main, so the D-138 comparison has no qualifying baseline.",
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
    "category": "STOP",
    "qualifying_comparison": false,
    "recorded_absolute_floor_j": 6.294380135190098,
    "recorded_comparative_floor_j": 13.998036715259254,
    "main": {
      "acceptance": "d079_calibration_acceptance_v2_n17_r7",
      "freshness": "fresh",
      "reason": "instrument_calibration_bracket_missing",
      "numeric_result": null
    },
    "head": {
      "commit": "c81f65b8b703f348c0e2375407782028a5d3057b",
      "acceptance": "d079_calibration_acceptance_v2_n12_25g83_r1",
      "freshness": "stale",
      "stale_fields": ["os_build"],
      "reason": "calibration_acceptance_bound_stale",
      "numeric_result": null
    },
    "rows": [
      {
        "row": "D-138 merge",
        "action": "do_not_start",
        "reason": "The selected July replay refuses on main for a non-stale reason; it cannot establish the ruling's before-and-after condition."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["bd87d5c4a70405daa222e696ab16b61883299bddd55982c0b5efb9ae6719309a  /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^bd87d5c4a70405daa222e696ab16b61883299bddd55982c0b5efb9ae6719309a"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/bin/zsh /tmp/oldepoch-d528efb2/replay.sh /Users/edr/code/JouleWise-wt-oldepoch-main-d528efb2 /tmp/oldepoch2-d528efb2/main-bracket",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["stdout.txt: {\"status\": \"failed\", \"reasons\": [\"instrument_calibration_bracket_missing\"]}"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "instrument_calibration_bracket_missing"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/bin/zsh /tmp/oldepoch-d528efb2/replay.sh /Users/edr/code/JouleWise-wt-d138-suite-d528efb2 /tmp/oldepoch2-d528efb2/head-bracket",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["stdout.txt: {\"status\": \"failed\", \"reasons\": [\"calibration_acceptance_bound_stale\"]}"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "calibration_acceptance_bound_stale"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/oldepoch-d528efb2/compare.py /tmp/oldepoch2-d528efb2/main-bracket /tmp/oldepoch2-d528efb2/head-bracket",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["A refusal reasons: ['instrument_calibration_bracket_missing']", "B refusal reasons: ['calibration_acceptance_bound_stale']", "B acceptance freshness: stale"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "B acceptance freshness: stale"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The July pre/post calibrations are historical imports excluded from current claim-window candidate discovery. The main replay cannot produce a passing numeric baseline.",
      "needs": "Lead must resolve how to satisfy or disposition the mandatory old-epoch gate before merging D-138."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| D-138 merge | do_not_start | A qualifying old-epoch comparison or lead disposition of this unavailable baseline | None; both worktrees remain clean |

## Critical path

The recorded production sequence was the July whole-window verdict followed by `scripts/extract_detection_floors.py` at commit `969a4d6`, using the [57-member campaign basis](/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/campaign_log.jsonl:139), the [frozen extraction spec](/Users/edr/JouleWise-window-plans/window_7bfloor_20260729/extraction_spec.json), and `--evaluation-basis-sha256 3ff9128b170136c57eea1376e954d32736d82d319d0d82bd1b64a78e616f1173 --hash-bundles`. The July CLI had no `--consumption-semantics-id` option. The [custodied report](/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json) has the SHA-256 stated in the [close-out](/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md) and records **6.294380135190098 J absolute**, **13.998036715259254 J comparative**, and **192.38623252628366 J** for the ten-member absolute mean. R7 did not exist at that July commit, so this original analysis did not consult the default R7 acceptance.

For the closest current-code comparison, I replayed the production bracket evaluator on recorded member `sw7bfloor-df-ph-decode-abs-r01` with the authenticated 276-row ledger, then ran the identical command at the D-138 head. The commands are V2–V4 above; the outputs are in [/tmp/oldepoch2-d528efb2/main-bracket/bracket.json](/tmp/oldepoch2-d528efb2/main-bracket/bracket.json) and [/tmp/oldepoch2-d528efb2/head-bracket/bracket.json](/tmp/oldepoch2-d528efb2/head-bracket/bracket.json). Main finds R7 **fresh** but produces no number: `instrument_calibration_bracket_missing`. Head gives the expected **clean stale-calibration refusal** for `os_build`, also with no number.

The main refusal is inherent to these recorded inputs under current code. The July pre/post observations are ledger rows 58 and 60, both `historical-import-v1-finalization`; current `discover_calibration_candidates` excludes historical imports. All later finalized bracket-session observations in the 276-row ledger are 25G83. The 76-row archived ledger rolls back against the committed 276-row head pin. Thus no ledger found supplies eligible July endpoints for a passing default-acceptance replay on main. **STOP** is the ruling category for this attempted comparison because main refused for another reason; it is **not evidence of a changed July number**. A reduced extraction diagnostic was interrupted during prolonged strict bundle validation and is not used for the verdict.

An explicit-R7 route exists for later tooling: the D-138 head’s `epoch_equivalence_check.py --acceptance` defaults to the R7 path, and the generalized floor mint reads an acceptance path from its input manifest. I found no recorded July production step using an explicit R7 path.