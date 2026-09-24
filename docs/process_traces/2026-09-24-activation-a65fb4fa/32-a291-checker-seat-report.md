```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the independent A291 roster checker and hand-built contract witnesses; the requested test module passes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "d917bf77a9ff01aa35165be911045d66a3220409",
    "head_end": "d917bf77a9ff01aa35165be911045d66a3220409",
    "upstream_end": null,
    "branch": "feat/2026-09-24-a291-packer-recut"
  },
  "pathspec": [
    "tests/scored_roster_checker.py",
    "tests/test_scored_roster_checker.py"
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
      "cmd": "python3 -B -m unittest tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 4.068s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests in .*s\\s+OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Section 6 leaves the invalid-input dict shape of check_executed unspecified; the checker returns {'violations': list[Violation]}.",
      "needs": "Magistrate confirm the shape before the packer seat uses it."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The exact R1 case-2 observation order is rejected by the later FT-14 rule.",
      "needs": "Magistrate confirm that the historical probe should remain an INV-47 rejection witness."
    }
  ]
}
```

## Change

Added the stdlib-only [checker](/Users/edr/code/wt-a65fb4fa-a291/tests/scored_roster_checker.py) and [hand-built tests](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_roster_checker.py). The checker reconstructs the root from pack-time placements, re-derives decisions and placement targets from observations, and compares each event digest and the final roster bit-exactly. It imports no JouleWise implementation modules. No commit was made.

**Row coverage.** Test aliases: A = `test_base_and_row_inventory`; B = `test_registration_rows`; C = `test_root_mutation_rows`; D = `test_event_mutation_rows`; E = `test_split_and_completed_single_rows`; F = `test_INV_31_innocent_initial_reschedule`; G = `test_executed_values_INV_26_INV_45`; H = `test_refuter_R1_cases_1_and_2`; I = `test_refuter_R2_four_envelopes`. Each reject test asserts the listed row ID. G checks ruled value changes for recorded-value rows.

| Row | Checker function | Accept test | Reject or value-boundary test |
|---|---|---|---|
| INV-01 | `_static_checks` | A | C |
| INV-02 | `_static_checks` | A | C |
| INV-03 | `_schema`, `_static_checks` | A | C |
| INV-04 | `check_registration`, `_static_checks` | A | B, C |
| INV-05 | `_static_checks` | A | B |
| INV-06 | `check_registration` | A | B |
| INV-07 | `_check_predictions`, `_static_checks` | A | C |
| INV-08 | `_static_checks` | A | C |
| INV-09 | `check_registration` | A | B |
| INV-10 | `_static_checks` | A | C |
| INV-11 | `_static_checks` | A | C |
| INV-12 | `_static_checks` | A | C |
| INV-14 | `_static_checks` | A | C |
| INV-15 | `_static_checks` | A | C |
| INV-16 | `_static_checks` | A | C |
| INV-17 | `_static_checks` | A | C |
| INV-18 | `_event_checks`, `check_transition` | D | D |
| INV-19 | `_event_checks` | E | E |
| INV-20 | `_static_checks` | A | C |
| INV-21 | `_static_checks`, `_event_checks` | A | C |
| INV-22 | `_static_checks`, `_event_checks` | D | D |
| INV-23 | `_static_checks` | E | E |
| INV-24 | `_static_checks` | A | C |
| INV-25 | `_derived`, `_static_checks` | A | C |
| INV-26 | `check_executed` | G | G, value boundary |
| INV-27 | `_derived`, `_static_checks` | A | C |
| INV-28 | `_static_checks` | A | B |
| INV-29 | `_types`, `_event_checks` | D | D |
| INV-30 | `_event_checks`, `_apply` | D | D |
| INV-31 | `_event_checks`, `_apply` | F | F |
| INV-32 | `_event_checks`, `_apply` | E | E |
| INV-33/43 | `_event_checks`, `_apply` | E | E |
| INV-34 | `_event_checks`, `_eligible` | F | D, F |
| INV-35 | `_event_checks` | I | D, I |
| INV-36 | `_static_checks`, `_event_checks` | D | D |
| INV-37 | `_static_checks`, `_event_checks` | A | C |
| INV-38 | `_root_from_final`, `_event_checks` | D | D |
| INV-41 | `_static_checks` | A | C |
| INV-45 | `check_executed` | G | G, value boundary |
| INV-46 | `_event_checks`, `check_executed` | D | D |
| INV-47 | `_event_checks` | H | D, H |
| INV-48 | `_event_checks` | D | D |
| INV-49 | `_derived`, `_static_checks` | A | C |
| INV-50 | `_static_checks` | A | C |
| INV-51 | `check_registration` | A | B |
| INV-52 | `_types` | A | C |

`NOT_CHECKABLE` contains INV-13 (moved to A292), INV-39 (requires the future packer for re-pack equality), INV-40 (seal call placement is source structure), and INV-44 (constant and literal scan needs implementation source). INV-50’s insertion-order permutation clause also needs the packer; its roster-order predicate is checked. The test parses INV IDs from 02d at runtime and asserts the inventory equals `ROWS ∪ NOT_CHECKABLE`.

## Verification notes

`python3 -B -m unittest tests.test_scored_roster_checker` passed: **12 tests, OK**. The named fixtures include R1 cases 1 and 2, R2’s four-envelope 3+3+2+2 reschedule sequence, P5b/P5c, and the PC reported empty loaded envelope. `git status --porcelain` shows only the two `WRITE_SCOPE` files.

## Residual risk

**CONTRACT GAPS:** (1) Root envelope cutoff is inferred from initial placements and the idle slot. (2) A single roster cannot prove that an earlier event or placement was removed; `check_transition` compares the before/after pair. (3) INV-26 and INV-45 specify recorded executed values, so tests assert value boundaries rather than refusal. (4) Invalid `check_executed` input returns a `violations` dict entry. (5) Registered root `claim_ready: false` is accepted at pack exit but rejected on descendant entry, following INV-05’s entry wording. (6) The exact historical R1 case-2 order is rejected under the later FT-14 rule. No discrepancy was found between 02d and the binding ruled texts.

The magistrate should double-check gaps 4 and 6, the root cutoff inference, and the packer-owned INV-39/40/44 and INV-50 permutation witnesses.