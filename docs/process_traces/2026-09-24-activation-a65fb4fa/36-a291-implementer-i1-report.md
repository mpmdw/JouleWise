```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented A291 registration, scored packing, replay and executed status; acceptance passes with one demonstrated checker disagreement.",
  "workspace": {
    "base_requested": "b8962fd0",
    "base_mode": "exact",
    "head_start": "b8962fd0d35ec83d382984354674d63300cf1c12",
    "head_end": "b8962fd0d35ec83d382984354674d63300cf1c12",
    "upstream_end": null,
    "branch": "feat/2026-09-24-a291-packer-recut"
  },
  "pathspec": [
    "joulewise/scored_registration.py",
    "joulewise/scored_packer.py",
    "tests/test_scored_registration.py",
    "tests/test_scored_packer.py",
    "tests/test_scored_packer_stress.py"
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
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 45 tests in 107.166s",
          "OK",
          "STRESS seeds=(291013,) registrations=300 calls=4263 rosters_checked=4563 violations=0 edges={'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1027, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in .*s[\\s\\S]*OK[\\s\\S]*violations=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "?? joulewise/scored_packer.py",
          "?? joulewise/scored_registration.py",
          "?? tests/test_scored_packer.py",
          "?? tests/test_scored_packer_stress.py",
          "?? tests/test_scored_registration.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^(\\?\\? (joulewise/scored_(packer|registration)\\.py|tests/test_scored_(packer|packer_stress|registration)\\.py)\\n?)+$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The independent checker's executed-status helper counts a voided first attempt when that block ID has a later live placement. A valid-roster counterexample is recorded in the tests; the checker was not edited.",
      "needs": "Magistrate to review the counterexample and route any checker correction outside this write scope."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The AP-5M equality anchor for CARRIED constants remains pending under 31 X-8; this stage pins the 02d values.",
      "needs": "Apply the adopted AP-5M equality witness when lane A282 lands."
    }
  ]
}
```

## Change

[scored_registration.py](/Users/edr/code/wt-a65fb4fa-a291/joulewise/scored_registration.py:1) now accepts the exact 29-key registration, preserves canonical numeric values, exposes defensive copies, and raises typed refusals. [scored_packer.py](/Users/edr/code/wt-a65fb4fa-a291/joulewise/scored_packer.py:1) implements deterministic role-ordered packing, the eleven overrun edges, derived fields, sealing, event replay, and executed status. No commit was made.

The section and invariant map below uses **R** for [registration tests](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_registration.py:1), **P** for [packer tests](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer.py:1), and **S** for the [seeded stress test](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer_stress.py:1). S passes every produced roster to the independent checker.

| 02d section | Implementation and witness |
|---|---|
| §0 conventions | Registration and packer canonical JSON helpers; R canonical identity test. |
| §1 constants and derivations | Registration module constants and derived properties; `_roles`, `_derived`; R and P constant tests. |
| §2 data contract and digests | `Registration.from_mapping`, `_predictions`, `_structure`, `_seal`; R and P domain, type, and digest refusals. |
| §3 pack, requeue, replay | `pack`, `_eligible`, `requeue_overrun`, `_replay_roster`, `verify_executed_roster`; P’s named P/E1–E11/R tests and S. |
| §4 executed values | `executed_status`; P’s reduce-entry and checker-counterexample tests. |
| §5 invariant matrix | Row map below; P refusal tests and S checker calls. |
| §6 checker interface | P and S call the independent checker without modifying it. |
| §7 CONSUMED/CARRIED | Registration retains the exact fields and constants; R and P validate their pinned values and consumers. |
| §8 later-lane rules | No A292 or A293 implementation was started. |
| §9 coverage | Named P/E1–E11/R tests and S exercise the I1 paths. |
| §10 residual rulings | Role and list ordering, float summation, cell keys, and typed codes appear in the implementation and P tests. |
| §11 change log | Historical contract description; no separate runtime behavior. |

| INV rows | Implementing functions; principal tests |
|---|---|
| 01, 02, 03, 04, 05 | `_seal`, `_structure`; P typed seal refusals, R identity, S. |
| 06, 07, 08, 09 | `Registration.from_mapping`, `_predictions`, `_structure`; R typed refusals, P pack refusals. |
| 10, 11, 12 | `pack`, `requeue_overrun`, `_structure`; P split path, S checker. |
| 13 | Moved to A292 by 02d; no I1 implementation. |
| 14, 15, 16, 17 | `pack`, `_structure`; P typed static refusals, S checker. |
| 18, 19 | `_structure`, `_eligible`, `requeue_overrun`; P event-target refusal, S checker. |
| 20, 21, 22, 23, 24 | `pack`, `_structure`, `_eligible`, `requeue_overrun`; P capacity/static refusals and E1/E4, S checker. |
| 25, 26 | `pack`, `_seal`, `executed_status`; P root and reduce-entry tests, S checker. |
| 27, 28 | `_derived`, `_seal`; P drift refusal, S checker. |
| 29, 30, 31, 32 | `_observations`, `_eligible`, `requeue_overrun`; P report refusals and E1/E2/E4, S checker. |
| 33/43, 34 | `requeue_overrun`, `_eligible`; P E6–E9, S checker. |
| 35, 36, 37 | `_structure`, `requeue_overrun`; P culprit/reschedule typed refusals and terminal paths, S checker. |
| 38, 39 | `_digest`, `_seal`, `_replay_roster`; P earlier-event tamper and re-pack refusal tests. |
| 40, 44 | `_seal` call placement and registration constants; P AST and literal-scan tests. |
| 41, 45, 46 | `pack`, `executed_status`, `_observations`, `verify_executed_roster`; P root/reduce-entry tests, S checker. |
| 47, 48, 49 | `_observations`, `_structure`, `_derived`, `_seal`; P order, elapsed, and stale-derived refusals. |
| 50, 51, 52 | `_roles`, `pack`, `Registration.from_mapping`, `_structure`; P insertion-order permutation and typed refusals, R domain tests. |

## Verification notes

The exact acceptance command in V1 passed. The stress run used seed `291013`, covered short last blocks, odd and even envelope counts, both idle-slot cases, and tight capacity. It completed **300 registrations, 4,263 requeue calls, 4,563 checker-clean rosters, and zero violations** in the 107-second suite run.

| Path | Hits | Path | Hits |
|---|---:|---|---:|
| P pack | 300 | R verify and executed status | 300 each |
| E1 initial→whole_block | 262 | E2 initial→reschedule | 1,027 |
| E3 initial→unattributed | 186 | E4 whole_block→single_problem | 224 |
| E5 whole_block→unattributed | 38 | E6 single_problem→single_retry | 260 |
| E7 single_problem→reschedule | 74 | E8 single_retry→ceiling_violation | 223 |
| E9 single_retry→reschedule | 37 | E10 single_problem→unattributed | 76 |
| E11 single_retry→unattributed | 37 | | |

**Checker disagreement, with counterexample:** P’s `test_checker_executed_voided_attempt_counterexample` builds a valid, checker-clean roster in which `large:decode:2:0` is rescheduled. Its attempt 0 window is captured, but its live attempt is omitted. FT-11 excludes attempt 0, so `executed_status` reports `spread_exceeded["large:2"] == true`. The checker’s `check_executed` reports `false`: it selects the first placement for a live block ID. The checker file was left untouched.

## Residual risk

The magistrate should double-check the checker counterexample, the `_seal(..., finalize=True)` output convention and bounded trusted-roster cache, and the PROVISIONAL reduce-entry witnesses when A292 supplies the real reducer entry. The AP-5M constant equality witness remains tied to A282’s adopted text.