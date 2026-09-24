```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No behavioral difference was observed beyond the ruled manifest delta; two review findings remain.",
  "workspace": {
    "base_requested": "cdc05e9b",
    "base_mode": "exact",
    "head_start": "702afd8d80a440d8a549dea1a3fff87fe8c9fa0b",
    "head_end": "702afd8d80a440d8a549dea1a3fff87fe8c9fa0b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 2, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "summary": "K3 golden test misses plan-prefix and root-suffix behavior and skips candidate-head sealing."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "In-scope single-kind literals remain outside the table."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-review.icxY9B/compare.py",
      "cwd": "/tmp/a280-review.icxY9B/head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: eight artifacts; sole manifest entry night_kinds.py; only downstream digest substitutions",
          "PASS: 15 direct parity cases"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: 15 direct parity cases"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-review.icxY9B/mutate.py",
      "cwd": "/tmp/a280-review.icxY9B/head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["13 single-field mutants classified; prefix and suffix survived K3 and gate tests"]
      },
      "expected": {"exit_code": 0, "tail_regex": "mutant"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_base_archive_byte_goldens tests.test_night_kinds.NightKindTests.test_refusal_parity tests.test_night_kinds.NightKindTests.test_rows_and_unknown_kind tests.test_night_gate",
      "cwd": "/tmp/a280-review.icxY9B/head",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 89 tests in 1.200s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night.LifecycleTests.test_the_arm_check_spends_the_predicate_only_on_an_evidence_chain tests.test_evidence_night.LifecycleTests.test_an_unreadable_payload_kind_fails_the_arm_check_closed tests.test_night_gate.EvidenceRegistrationTests.test_the_non_observer_predicate_is_spent_only_on_an_evidence_night tests.test_night_gate.EvidenceRegistrationTests.test_payload_ambiguity_and_unknown_literal_refuse",
      "cwd": "/tmp/a280-review.icxY9B/base and /tmp/a280-review.icxY9B/head",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 3.171s", "OK", "Ran 4 tests in 3.169s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/a280-review.icxY9B/import_probe.py <module>",
      "cwd": "/tmp/a280-review.icxY9B/base and /tmp/a280-review.icxY9B/head",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["All four modules imported fresh in both archives; no non-code file opens or process launches."]},
      "expected": {"exit_code": 0, "tail_regex": "\"result\": \"ok\""}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The full prepare composition test exercised prepare successfully in both archives but its original runs failed during temporary Git-directory cleanup. Reruns with only TemporaryDirectory.cleanup disabled passed one test in each archive.",
      "needs": ""
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The long importer list was not rerun because a heavy test run was already active; this review used targeted classes and probes.",
      "needs": ""
    }
  ]
}
```

## (a) Behavior parity

The same fixture and refusal inputs ran from separate `/tmp` archives of `cdc05e9b` and `702afd8d`. The head test copy was adjusted **only under `/tmp`** to obtain the base archive and use identical fixture paths.

| Path | Observed base versus candidate |
|---|---|
| Plan authoring and locations | Fixed plan bytes and `locations()` output matched. The real `prepare` composition test passed in both archives when temporary-directory cleanup was disabled. |
| Generator, manifest, notice | Eight artifacts compared. The manifest gained exactly `joulewise/night_kinds.py`; existing entries were equal. Only the manifest digest and downstream wrapper digest changed. Plan and both notice variants were byte identical. |
| `sealed_candidate` | Candidate-head sealing passed against a committed `/tmp` measurement copy. |
| Refusals | Unknown kind, calibration at the idle entry point, wrong plan prefix, wrong protocol path, window 8999, alternate chain, and mismatched source digests produced matching exception types/messages or refusal reasons. |
| Gate and arm scope | Idle reached the source authentication and non-observer observation; calibration skipped them. Duplicate, unknown, and ledger-coexport payloads refused identically. Four focused arm/gate tests passed in both archives. |

The direct parity probe compared 15 result groups with no difference. The base manifest digest was `3f6b0039…5330f9bb`; the candidate digest was `ff865fe5…d37f995`.

## (b) Mutation sensitivity

Each mutation changed one idle-row field in a `/tmp` copy. “Gate” is the named `tests.test_night_gate` module, whose unmutated baseline passed 86 tests.

| Idle-row mutation | K3 golden | Gate |
|---|---|---|
| Plan prefix; root suffix | Survived; survived | Survived; survived |
| Chain path; protocol path; window | Killed all three | Killed all three |
| Chain authentication; chain-bound registration; arm/t0 corecaptured; arm/t0 non-observer flags | Survived all four | Killed all four |
| Four notice text fields | Killed all four | Survived all four |

The separate `test_rows_and_unknown_kind` killed both prefix and suffix mutants.

## (c) Remaining literals

| Site | Assessment |
|---|---|
| [quiet_predicate_campaign.py:168](/Users/edr/code/wt-d8cc9c0a-a280a-review/joulewise/quiet_predicate_campaign.py:168) | `verify_manifest` still compares the probed kind with the literal `"quiet_predicate_evidence"`. |
| [gen_evidence_night.py:34](/Users/edr/code/wt-d8cc9c0a-a280a-review/scripts/gen_evidence_night.py:34) and [line 44](/Users/edr/code/wt-d8cc9c0a-a280a-review/scripts/gen_evidence_night.py:44) | The calibration-chain basename remains a literal in refusal filters. |
| Other matched kind strings | Table lookups, public compatibility names, comments, and refusal text; no further behavioral selector found. |

## (d) Imports

| Fresh import in each archive | Cycle | Non-code read, Git call, or subprocess at import |
|---|---|---|
| `joulewise.evidence_night` | None | None |
| `joulewise.night_gate` | None | None |
| `joulewise.quiet_predicate_campaign` | None | None |
| `scripts.gen_evidence_night` | None | None |

## Findings

- **F1 — should_fix:** K3 builds its plan directly with a hard-coded ID at [test_night_kinds.py:84](/Users/edr/code/wt-d8cc9c0a-a280a-review/tests/test_night_kinds.py:84), so it does not test `prepare`’s prefix or root suffix. It also invokes `sealed_candidate` only when the table is absent, at [line 113](/Users/edr/code/wt-d8cc9c0a-a280a-review/tests/test_night_kinds.py:113). Executed counterexample: `python3 -B /tmp/a280-review.icxY9B/mutate.py` changed each field separately; K3 and all 86 gate tests still reported `OK` for both. The row-constant test catches them, but K3 does not prove those authoring bytes.

- **F2 — should_fix:** The literals in table (c) remain in the four-file refactor scope. The clause is K1–K2’s requirement that per-kind facts and single-kind selectors read the table; the exact sites are [quiet_predicate_campaign.py:168](/Users/edr/code/wt-d8cc9c0a-a280a-review/joulewise/quiet_predicate_campaign.py:168) and [gen_evidence_night.py:34](/Users/edr/code/wt-d8cc9c0a-a280a-review/scripts/gen_evidence_night.py:34). No current-idle behavior difference was observed.

## Residual risk

This was a targeted execution review. The long importer test list and live hardware gates were outside this run. The repository worktree remained clean and unchanged.