```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: b-i and all five regression-redness claims pass, but b-ii remains fail-open because schema-valid measured-run telemetry and unclassified nested workload content can disagree with the admission event stream and still license.",
  "workspace": {
    "base_requested": "05d99b65c1954c845f483628754ec67aed8dc3fe",
    "base_mode": "exact",
    "head_start": "05d99b65c1954c845f483628754ec67aed8dc3fe",
    "head_end": "05d99b65c1954c845f483628754ec67aed8dc3fe",
    "upstream_end": null,
    "branch": "impl/met-dangler-disposition"
  },
  "pathspec": [],
  "unowned_dirty": [
    "D100-BRIEF.md"
  ],
  "verdict": {
    "overall": "fail",
    "blocker_present": true,
    "cold_gate_return_required": true,
    "escalation_trigger_dissent": "None. I read the binding trigger as fired by B3-R1.",
    "items": [
      {
        "id": "item_1",
        "result": "PASS",
        "detail": "Every discovered regular file is checked by path and streaming raw-byte containment; symlinks, non-regular nodes, duplicate inodes, and unreadable entries refuse."
      },
      {
        "id": "item_2",
        "result": "FAIL",
        "detail": "Exact inventory and the two named attacks close, but the per-file validators do not prove cross-surface admission-phase identity and retain unclassified nested-content paths."
      },
      {
        "id": "item_3",
        "result": "PASS",
        "detail": "All five new regressions would fail their assertRaises expectations against the pre-fix 5f8b4b8 implementation."
      },
      {
        "id": "item_4",
        "result": "PASS",
        "detail": "Exactly two files changed; exports and callers are unchanged, and behavior changes remain inside the salvage license inspectors."
      }
    ],
    "regressions_red_on_5f8b4b8": [
      {"name": "summary_metrics raw bytes", "result": "PASS"},
      {"name": "rich_telemetry raw bytes", "result": "PASS"},
      {"name": "renamed.json raw bytes", "result": "PASS"},
      {"name": "copied allowlisted telemetry", "result": "PASS"},
      {"name": "workload fields inside teardown bound", "result": "PASS"}
    ],
    "findings": [
      {
        "id": "B3-R1",
        "severity": "blocker",
        "title": "b-ii validation does not bind telemetry or nested content to the admission-only event account",
        "locations": [
          "joulewise/salvage_dangler.py:389",
          "joulewise/salvage_dangler.py:440",
          "joulewise/salvage_dangler.py:649",
          "joulewise/salvage_dangler.py:655",
          "joulewise/salvage_dangler.py:746"
        ],
        "scenario": "Place a valid rich_telemetry.jsonl captured during an earlier measured run under the allowlisted name while retaining the closed idle-abort events and idle power trace. Its rows have the same accepted schema, contain no phase or occurrence identity, and their older timestamps do not exceed failure+0.250 s. Alternatively, put workload output under an unrecognized nested key such as metadata.extra.model_output or failure-event metadata.model_output. Both shapes remain licensed."
      }
    ],
    "scope": {
      "result": "pass",
      "changed_paths": [
        "joulewise/salvage_dangler.py",
        "tests/test_salvage_dangler.py"
      ]
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show --no-ext-diff --no-renames --format=fuller 05d99b65c1954c845f483628754ec67aed8dc3fe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "refusal_path = refusal_root / f\"refusal-{index}.json\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "refusal_root"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git show --stat --oneline --decorate --no-renames 05d99b65c1954c845f483628754ec67aed8dc3fe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2 files changed, 536 insertions(+), 74 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2 files changed"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show 5f8b4b8655e442c3919e3d1f6d4a4cb5e376897b:joulewise/salvage_dangler.py; git show 5f8b4b8655e442c3919e3d1f6d4a4cb5e376897b:tests/test_salvage_dangler.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Pre-fix launcher parsing and telemetry/inventory logic inspected against each new regression."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "inspect_launcher_refusal"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": [
          "NOT RUN — prohibited by the lead's code-inspection-only ruling."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "B3-R1 is a false-license path within the repaired mechanism, firing the disposition note's binding cold-gate trigger.",
      "needs": "Return the branch to a cold gate; do not proceed to window-B re-evaluation."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests or mapping gates were executed by instruction; regression redness and containment were corroborated by code inspection only.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Literal byte containment cannot recognize transformed encodings such as JSON escapes, UTF-16, compression, or base64, but those are not realistic identity-bearing artifacts under the inspected corpus writer grammar.",
      "needs": ""
    }
  ]
}
```

## Findings

### B3-R1 — blocker (Item 2)

The exact inventory portion closes the named multiplicity attack: the actual path set must equal one of the derived closed sets, and byte-identical copies under separate allowlisted telemetry names void by digest at [salvage_dangler.py:500](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:500) and [salvage_dangler.py:535](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:535).

The content closure is incomplete:

- Rich telemetry is validated only by field shape, scalar types, index order, and timestamp order at [salvage_dangler.py:389](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:389). It carries neither occurrence identity nor phase.
- Events are independently constrained to the idle-abort sequence at [salvage_dangler.py:664](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:664), but no relationship binds their account to telemetry.
- The only cross-surface temporal test is an upper bound, `telemetry_last - failure_timestamp <= 0.250`, at [salvage_dangler.py:746](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:746). Negative differences are accepted.

Concrete false-license scenario: substitute a valid `rich_telemetry.jsonl` from an earlier measured run. Its ordinary rows satisfy the admitted schema and have timestamps earlier than the failure; the valid idle `power_trace.csv` still determines the maximum timestamp. The event stream says idle abort, while telemetry contains measured-run samples, and authorization succeeds.

The “extra keys” attack also finds a gap. Top-level extra telemetry/event keys correctly void at lines 393–400 and 655–656. But event metadata is accepted as any mapping at lines 657–660, and `_contains_workload_evidence` is a spelling list at [salvage_dangler.py:440](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:440). A nested `model_output` field is unrecognized and passes. This violates “unclassifiable ⇒ void.”

Empty-row attack outcome: void, sound. Empty JSONL surfaces fail at lines 260–267; a header-only power trace fails at lines 599–605.

### Item 1 — PASS

Every regular file is scanned by both path and raw content. The scanner streams 1 MiB chunks with overlap, including identifiers split across chunk boundaries, at [salvage_dangler.py:564](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:564). Every discovered file reaches it at lines 883–918.

Attack outcomes:

- JSON escapes, UTF-16, compressed files, and base64 can theoretically represent the identifier without the literal ASCII substring. They therefore evade this predicate and remain readable rather than triggering the unreadable rule. This is a nonblocking, nit-level representation limitation, not a realistic corpus false-license path: inspected identity-bearing writers use ordinary ASCII JSON/path spellings, not those transformed formats.
- Root and nested symlinks void; traversal does not follow them. Ordinary directory cycles require a symlink and are therefore blocked. Non-symlink mount-cycle constructions are theoretical and outside the custody writer grammar.
- Unreadable directories, entries, and files void through the walk, `lstat`, and open error paths at lines 841–844, 865–914.
- Memory is bounded for file contents; the inode set grows with file count. Runtime is necessarily linear in all custody bytes and repeats for each launcher-refusal occurrence, but there is no superlinear content operation or silent truncation. No severity finding.

### Item 3 — PASS

All five tests are genuinely red against `5f8b4b8`:

1. `summary_metrics.json` raw bytes — PASS. The test at [test_salvage_dangler.py:403](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/tests/test_salvage_dangler.py:403) expects refusal. Pre-fix lines 528–539 parse only `config.json`, `metadata.json`, and `events.jsonl`, so the inspector licenses and the `assertRaises` fails.

2. `rich_telemetry.jsonl` raw bytes — PASS. The test at line 406 is skipped by the same pre-fix filename enumeration and is red.

3. `renamed.json` raw bytes — PASS. The test at line 409 is likewise skipped and red.

4. Copied allowlisted telemetry — PASS. The test at [test_salvage_dangler.py:240](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/tests/test_salvage_dangler.py:240) leaves two separately allowlisted names. Pre-fix lines 423–434 admit both and lines 280–297 check timestamps only, so no exception is raised.

5. Workload fields inside the teardown bound — PASS. The test at [test_salvage_dangler.py:258](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/tests/test_salvage_dangler.py:258) adds `phase`, `workload_result`, and `output_token_count`. Pre-fix telemetry parsing reads only `timestamp_s`; authorization succeeds and the `assertRaises` fails.

### Item 4 — PASS

`05d99b6` changes exactly `joulewise/salvage_dangler.py` and `tests/test_salvage_dangler.py`: 536 insertions and 74 deletions.

No export was added or removed; the public surface remains the inspector/authorization API at [salvage_dangler.py:1326](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbb164b5-3094-4877-a575-425599030f86/scratchpad/d100-worktree/joulewise/salvage_dangler.py:1326). Production callers continue through the existing salvage-only authorization branch. No non-salvage selection, mapping, claim, or mint path changed in this commit. No additional introduced defect was found beyond B3-R1’s incomplete closure.

Overall verdict: blocker present YES. B3-R1 triggers the binding cold-gate return. I record no dissent about that escalation trigger.

## Residual risk

Tests and mapping gates were not executed by instruction. The transformed-encoding limitation in b-i is theoretical under the current custody writer grammar; it does not mitigate or enlarge the B3 blocker.