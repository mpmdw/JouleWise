```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Fixed the four CI failures with archived-session-shaped fixtures and one INTERNAL refusal entry; all 82 requested tests pass.",
  "workspace": {
    "base_requested": "e31d5d871",
    "base_mode": "exact",
    "head_start": "e31d5d871e3c5c217bfbc69225e0cbed4cf5ac9e",
    "head_end": "e31d5d871e3c5c217bfbc69225e0cbed4cf5ac9e",
    "upstream_end": "e31d5d871e3c5c217bfbc69225e0cbed4cf5ac9e",
    "branch": "lane/2026-11-03-align-pilot4"
  },
  "pathspec": [
    ".codex-report/ALIGN-PILOT4-fix2.md",
    ".codex-report/verification/fix2-archive-shapes.json",
    ".codex-report/verification/fix2-baseline.log",
    ".codex-report/verification/fix2-pilot2-round1.log",
    ".codex-report/verification/fix2-pilot2.log",
    ".codex-report/verification/fix2-pilot4.log",
    ".codex-report/verification/fix2-refusal-census-after.json",
    ".codex-report/verification/fix2-refusal-census-before.json",
    ".codex-report/verification/fix2-refusal.log",
    ".codex-report/verification/fix2-session.log",
    "configs/gates/hazard_refusals.json",
    "tests/align/fixtures/pilot3_member_shape.json",
    "tests/align/test_pilot2.py",
    "tests/align/test_pilot2_round1.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot2 > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot2.log 2>&1\nresult=$?\ntail -25 /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot2.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...........",
          "----------------------------------------------------------------------",
          "Ran 11 tests in 2.973s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot2_round1 > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot2-round1.log 2>&1\nresult=$?\ntail -25 /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot2-round1.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..................",
          "----------------------------------------------------------------------",
          "Ran 18 tests in 1.896s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 18 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.align.test_pilot4 > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot4.log 2>&1\nresult=$?\ntail -25 /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-pilot4.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...............",
          "----------------------------------------------------------------------",
          "Ran 15 tests in 8.535s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_align_pilot_session > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-session.log 2>&1\nresult=$?\ntail -25 /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-session.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...............",
          "----------------------------------------------------------------------",
          "Ran 15 tests in 71.576s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.hazards.test_refusal_allowlist > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-refusal.log 2>&1\nresult=$?\ntail -25 /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-refusal.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......................",
          "----------------------------------------------------------------------",
          "Ran 23 tests in 13.693s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "TMPDIR=\"$(mktemp -d)\" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m tests.hazards.refusal_census > /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-refusal-census-after.json\nresult=$?\ncat /Users/edr/code/jw-wt/align-pilot4/.codex-report/verification/fix2-refusal-census-after.json\nexit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{",
          " \"unlisted\": [],",
          " \"stale\": [],",
          " \"miscounted\": [],",
          " \"guard_changed\": [],",
          " \"scope_gaps\": []",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"unlisted\": \\[\\],"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git -C /Users/edr/code/jw-wt/align-pilot4 diff --check",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "Initial baseline reproduction grouped two test modules under one fresh TMPDIR. Final acceptance ran each requested module separately with its own fresh TMPDIR.",
      "needs": ""
    }
  ]
}
```

## Change

1. **Interval clipping / active GPU weighting (V1).** Added monotonic episode start and turn stamps to the diagnostic fixture, plus an exact assertion relating its per-turn clock to the episode clock. Every archived pilot-2 episode (12/12) and pilot-3 episode (24/24) has `start_ns`, `end_ns`, and `turns`. Existing numerical expectations and tolerances are unchanged.
2. **Greedy sampling checks (V2).** Added the real greedy task seed (`1`) to the round-1 summary fixture. All 36 archived summaries and all 36 episodes carry seed `1`; no missing-seed production fallback is warranted by these archives. Updated the stale spread assertion to check pilot-4's empty sampled-replay spread for greedy members, while retaining the legacy thermal-ineligibility assertion through `instrument_checks`.
3. **Later-member readability / summary printing (V2).** Added `duration_s` consistent with the fixture's nanosecond interval, plus current-producer `configuration.sampler=None` and per-turn GPU clock fields. All 36 archived summaries contain duration. Older archived summaries omit configuration/per-turn clocks, but the current `episode_summary` explicitly produces them; the crash fixture mocks that current producer. The exception test still requires the first member to remain unreadable and the later member readable.
4. **Refusal census (V5, V6).** Ran the census and added only `MlxRuntimeAdapter._generate` / `ValueError|sampled generation requires`, count `1`, guard `ececd5bbf43ed1dc`, as `INTERNAL`. It is a programming-error guard for requesting sampled generation without a sampler policy and never fires on a physical condition. All existing entries and other allowlist metadata remain byte-semantically unchanged; the census has no unlisted, stale, miscounted, guard-changed, or scope-gap findings. No adapter edit was needed.
5. **Archived pilot-3 regression (V2).** Added a portable fixture projected from `PILOT.json` member `align-pilot-v2-episodes-a-e01`: its exact 46 summary keys, seed `1`, duration `97.959493084`, and the associated episode's real 12-turn timing. The test runs both `sampling_checks` and `telemetry_diagnostics`, supplies synthetic token IDs and one synthetic telemetry support, and compares seeds, IDs, and clock results exactly. It preserves the archived absence of pilot-4 configuration fields and adds no tolerance or bar. Fixture provenance points to the archive but the test reads only repository data.

Archive evidence: `verification/fix2-archive-shapes.json` records both roots, counts, missing-field counts, PILOT SHA-256 digests, and episode paths/digests. Pilot 2 is `/Users/edr/night-align/pilot-v1-20261102T183609Z` (12 members, 11–20 turns); pilot 3 is `/Users/edr/night-align/pilot-v2-20261103T035512Z` (24 members, 6–20 turns). All 36 member configs are greedy. Source files were read only.

### Decisions I made

- Follow the prompt's production-shape branch for all three failures: seed, duration, and turns are present throughout both archives. No production default, printed number, analysis policy, or calibrated file changed.
- Retain the greedy fixture's recorded task seed `1`, rather than replace a present archived seed with null.
- Keep the legacy thermal-spread check at `instrument_checks`; the pilot-4 desk's sampled-replay spread behavior is already asserted by the session tests and documented by the protocol.
- Classify only the mechanically reported sampler-policy guard as `INTERNAL`, per the supplied authority.

## Verification notes

The envelope contains the exact final replay commands and clean output tails: V1 11 tests, V2 18 tests, V3 15 tests, V4 15 tests, V5 23 tests; **82 total**. V6 is the clean post-change census; V7 is the clean whitespace check. Logs are under `verification/fix2-*`.

Initial reproduction in `verification/fix2-baseline.log` showed the three reported fixture errors (28 tests, three errors); `fix2-refusal-census-before.json` showed exactly the missing site. That initial reproduction grouped two modules under one fresh TMPDIR; each final acceptance module was subsequently run separately with its own fresh TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, and `/opt/homebrew/bin/python3.13`, from this worktree. Adding the missing fixture fields also exposed the stale greedy-spread assertion described above; the final V2 rerun passed after its correction.

Only the requested modules were run, per the task's explicit test restriction; the full suite and known pre-existing b6 class were not run. These are synthetic/fixture checks and archived-record inspection, with no live hardware validation. No model was loaded, no privileged collection was started, no active pilot root was accessed, and no Git write was performed. HEAD remains the requested revision. Lead next step: review this diff and commit the authorized changes.
