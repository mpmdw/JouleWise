```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "F-A through F-G and the in-scope portion of F-H are implemented; final closure requires the out-of-scope registry to repin AS and amend DX-003.",
  "workspace": {
    "base_requested": "3f1677b79b5ba17ec4ee8ef1db8d5df431e71cee",
    "base_mode": "exact",
    "head_start": "3f1677b79b5ba17ec4ee8ef1db8d5df431e71cee",
    "head_end": "3f1677b79b5ba17ec4ee8ef1db8d5df431e71cee",
    "upstream_end": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "branch": "feat/2026-09-02-dx-registry"
  },
  "pathspec": [
    "docs/paper/round7/fill-checklist.md",
    "scripts/check_paper_round7_artifacts.py",
    "scripts/paper_anchor_correction_quantified.py",
    "tests/test_paper_round7_artifacts.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 21 tests in 0.380s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests.test_every_governed_gate_names_a_registered_dx_row tests.test_paper_round7_artifacts.RegistryAndDigestTests.test_every_registry_marker_renders_from_its_supplier tests.test_paper_round7_artifacts.RegistryAndDigestTests.test_all_118_figure_marks_invert_to_xd",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.002s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -m py_compile scripts/check_paper_round7_artifacts.py scripts/paper_anchor_correction_quantified.py tests/test_paper_round7_artifacts.py\ngit diff --check",
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
      "kind": "inspection",
      "cmd": "git status --porcelain\ngit diff --stat\ngit diff --stat -- 'runs*' docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/round7/fill-checklist.md",
          " M scripts/check_paper_round7_artifacts.py",
          " M scripts/paper_anchor_correction_quantified.py",
          " M tests/test_paper_round7_artifacts.py",
          "4 files changed, 377 insertions(+), 67 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4 files changed"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": [
          "NOT RUN: authoritative AS digest pin is outside WRITE_SCOPE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "No out-of-scope write was made. The AS producer edit changes its registry-pinned SHA-256 from 41cbbf08176f9bfe1c6cfd526e1776f0324893c62f62cd76d1ff8128b8beb47f to e3e4355c8f388d5e60a4291f3aee4fbd4b4d45217f4156373d6e8dd398b9e693.",
      "needs": "Expand WRITE_SCOPE to docs/paper/results-fill-registry.md and repin the AS source definition."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The current DX-003 pinned replay command has no --repository-root flag, so dictated mutation M5 cannot be formed exactly without changing that row.",
      "needs": "Expand WRITE_SCOPE to docs/paper/results-fill-registry.md and add the repository-root argument to DX-003."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The requested eight-minute acceptance suite and final CLI smokes were preserved for one run after the authoritative registry is repaired.",
      "needs": "Resume after scope expansion, apply the two registry changes, then run acceptance once."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/paper/results-fill-registry.md"
    ],
    "reason": "Update the AS source SHA-256 required by F-C and add --repository-root to the DX-003 pinned command required for exact F-H/M5 closure.",
    "blocked_work": "Authoritative registry agreement, exact M5 mutation, and final acceptance verification.",
    "minimal_change": "Change only the AS source digest and the full replay command text in DX-003."
  }
}
```

## Change

Requested path: `docs/paper/results-fill-registry.md` with exact-match authority.

Completed: the artifact fence now has distinct success tokens, fail-closed unavailable output, portable corpus defaults, delimiter-safe literals, return-code-only producer classification, figure record guards, file-pin-only identity validation, count-aware renderers, governed gate metadata, and replay argv derived from the existing pin. AS now returns 3 only for `PopulationUnavailable`.

Blocked work: the registry must repin AS and add `--repository-root` to DX-003 before the authoritative suite can pass and M5 can be exercised exactly.

No `runs*` or `docs/paper/draft-v1.md` diff exists.

Mutation results:

- M1: KILLED by `test_absent_corpus_exits_three_and_names_path`.
- M2: KILLED by `test_bare_successor_literals_reject_ambiguous_continuations`—all three mutants failed.
- M3: KILLED by `test_as_filenotfounderror_is_a_producer_failure_not_unavailable`.
- M4: KILLED by `test_non_mapping_per_pulse_entry_is_refused_without_traceback`.
- M5: KILLED by `test_bad_repository_root_flag_in_pinned_command_fails_replay` using an injected misspelled flag; exact mutation against a correct baseline flag remains scope-blocked.

Opus 207 same-signature result: B1, B2, S3, N1, N2, N3, and N4 are killed in implementation and focused tests. N5 is implemented against the existing command but awaits the DX-003 registry amendment. S1 and S2 were excluded as ruled.

## Clause map

| Closure | Production site | Biting test | Counterfactual |
|---|---|---|---|
| F-A | `scripts/check_paper_round7_artifacts.py:840,860,869,874`; checklist `:25` | `tests/test_paper_round7_artifacts.py:515,539,576` | Unavailable prints `COMPARED`; literals-only shares the full token; census drifts |
| F-B | `scripts/check_paper_round7_artifacts.py:625-648` | `tests/test_paper_round7_artifacts.py:255,270,281` | `150`, `599`, and `%%%` continuations pass; legacy separator is stripped |
| F-C | `scripts/check_paper_round7_artifacts.py:780,807`; `scripts/paper_anchor_correction_quantified.py:717-723` | `tests/test_paper_round7_artifacts.py:332,361` | Output substring converts FileNotFoundError into corpus absence |
| F-D | `scripts/check_paper_round7_artifacts.py:582-597` | `tests/test_paper_round7_artifacts.py:316` | String `per_pulse` entry raises traceback/exit 1 |
| F-E | `scripts/check_paper_round7_artifacts.py:325-328,501-503` | `tests/test_paper_round7_artifacts.py:168,175,576` | Identity rows are tautologically rendered or census changes |
| F-F | `scripts/check_paper_round7_artifacts.py:456-483` | `tests/test_paper_round7_artifacts.py:288` | “both/all” remains hardcoded; failure count is unnamed |
| F-G | `scripts/check_paper_round7_artifacts.py:94-98,515-522` | `tests/test_paper_round7_artifacts.py:190` | Governed gate references a missing DX row |
| F-H | `scripts/check_paper_round7_artifacts.py:725-778` | `tests/test_paper_round7_artifacts.py:380` | Pinned command drift is bypassed by separately constructed argv |

## Verification notes

The canonical acceptance commands were not run because they would fail at the intentionally untouched AS registry pin before testing the completed behavior. The linked worktree also lacks the default-local retained corpus; a successful full replay will require the explicit retained corpus root after registry closure.

## Residual risk

DX-003 still lacks the authoritative `--repository-root` token required by the exact M5 wording.