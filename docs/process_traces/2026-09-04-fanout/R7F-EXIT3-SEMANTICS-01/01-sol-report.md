```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The exit-3 row is design-blocked by two behaviours the governing cold gate explicitly left unruled; this report supplies a scoped design and exact implementation checklist without freezing an invented semantic.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 10 tests in 2.929s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --help | sed -n '/Exit codes:/,/Successful full replay/p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "a stop is reported as 3 with no ``MISMATCH`` line. Exit 3 also does not mean",
          "\"a file was absent\": a producer exits 3 when a required file is present but",
          "its bytes do not match the retained sha256. Successful full replay ends with"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "a producer exits 3 when a required file is present but\\nits bytes do not match the retained sha256"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'raise ArtifactsUnavailable|except ArtifactsUnavailable|return 3|events.jsonl does not match its retained sha256' scripts/check_paper_round7_artifacts.py scripts/paper_excursion_decomposition.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/paper_excursion_decomposition.py:170:        raise ArtifactsUnavailable(\"events.jsonl does not match its retained sha256\")",
          "scripts/paper_excursion_decomposition.py:800:    except ArtifactsUnavailable as exc:",
          "scripts/paper_excursion_decomposition.py:802:        return 3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "events.jsonl does not match its retained sha256[\\s\\S]*return 3"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The 2026-09-02 r7f-unavailable ruling explicitly did not decide whether comparisons collected before a producer exit 3 are retained or discarded, nor whether retained-sha256 drift is exit 2 or exit 3.",
      "needs": "Rule design option A, B, or C below; recommendation: A."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No counterfactual regression can be added honestly until the expected mixed-failure disposition and hash-drift exit code are ruled.",
      "needs": "After the ruling, implement the shared disposition definition and the listed defect-shaped regressions."
    }
  ]
}
```

## Change

No executable behaviour was changed. The kernel row has no dependency or hardware gate, but its authority deliberately deferred the two choices that define the requested behaviour. Selecting either choice here would be a new policy ruling, which this delegated implementation lane is not authorized to invent.

### Finding and decision table

| ID | Finding | Evidence | Decision |
| --- | --- | --- | --- |
| R1 | A mismatch found before the anchor-correction-summary producer stops is currently discarded. | `replay_half` builds a local comparison list, then raises `ArtifactsUnavailable`; `main` never receives that list. The governing ruling names this R-A3 and says it does not decide whether the comparisons should be kept. | NEEDS_RULING. |
| R2 | A present `events.jsonl` whose bytes differ from its retained SHA-256 digest (content fingerprint) currently becomes producer exit 3 and then driver exit 3. | `paper_excursion_decomposition.py` raises `ArtifactsUnavailable` for both absence and digest disagreement. The governing ruling names this R-A4 and says it does not decide whether the digest disagreement should instead be exit 2. | NEEDS_RULING. |
| R3 | A silent producer exit 3 is described as the corpus root, although the root may exist and is not the cause. | `_producer_unavailable_message` uses the resolved corpus root when producer output is empty. The cold gate documented this current fallback but did not decide whether it should exist. | Decide with R1/R2 because it is part of the same terminal-disposition grammar. |
| R4 | Current help text truthfully records current behaviour, but it is duplicated prose rather than the driver’s executable disposition definition. | The module docstring is passed to `argparse`; return codes and terminal tokens are separately hard-coded in `main`. | After ruling, make one typed disposition table drive both output and help text. |

### Scoped design

Forcing problem: one run can establish a byte mismatch and later discover that another replay input is unavailable. A single process exit code cannot erase either fact. The operator needs to know both what was established and whether the requested replay completed. Retained-byte drift is also evidence disagreement, not absence, so it needs a different producer classification from a missing path.

Option A — incomplete replay is the primary terminal disposition (recommended):

- Exit 0 means every requested comparison completed and agreed.
- Exit 2 means a completed comparison, producer integrity check, or producer execution definitively disagreed. A retained SHA-256 mismatch is exit 2.
- Exit 3 means the requested replay could not complete because required input was unavailable. Comparisons completed before the stop are printed and retained, but exit 3 remains primary because no complete replay verdict exists.
- A silent producer exit 3 is recorded as `source=excursion|anchor_summary; detail=no output`; it is never relabelled as the corpus root.

This keeps exit 2 and exit 3 disjoint: disagreement versus incomplete evidence. It also preserves every known mismatch without implying that a partial replay is a complete mismatch verdict.

Option B — any established mismatch has precedence: classify retained-hash drift as exit 2; if a later input is unavailable, print both facts but return 2. This makes “any mismatch returns 2” literal, but automation can no longer infer from the process status that the replay was incomplete.

Option C — ratify current behaviour: producer exit 3 always becomes driver exit 3, earlier replay comparisons are discarded, and silent output falls back to the corpus root. This is the smallest diff, but it preserves the recorded diagnostic-destruction defect and permits `UNAVAILABLE` to mean that present bytes changed.

Recommended shared implementation after Option A is ruled:

- Add an enumerated disposition definition—a closed list of allowed outcomes—containing the exit code, stable terminal token, and help sentence for `agreement`, `mismatch`, and `replay_incomplete`.
- Make the driver’s finalizer return the code and print the token from that definition. Generate the `--help` exit-code paragraph from the same definition; remove the duplicated hand-written mapping from the module docstring.
- Replace the exception-only replay return with a result that carries completed comparisons plus an optional stop record (`source`, `reason`, `detail`). This prevents a later stop from destroying earlier evidence.
- Split the excursion producer’s missing-input exception from its integrity-mismatch exception. Missing paths remain exit 3; present bytes that disagree with their retained digest exit 2.
- Require producer exit 3 to carry a diagnostic. If it is silent, the driver emits the explicit `no output` detail rather than guessing a path.

Worked example: the excursion producer completes but its regenerated Figure 4 bytes differ from the registered figure; the anchor-correction-summary population directory is then absent. Under Option A the driver prints the figure `MISMATCH`, prints `R7F REPLAY INCOMPLETE: source=anchor_summary; detail=...`, and exits 3. The log preserves the established mismatch while the exit code accurately states that the overall replay did not complete. Separately, if `events.jsonl` is present but fails its retained digest, the excursion producer and driver exit 2 and print a mismatch disposition, not an unavailable disposition.

Exact post-ruling checklist:

1. Record the selected option in the lead-owned decision log and point the kernel row to that ruling; do not edit either authority file from this branch.
2. Implement the shared typed disposition definition in `scripts/check_paper_round7_artifacts.py` and derive both the finalizer and `--help` semantics from it.
3. For Option A, carry completed comparisons through a replay stop and split missing-input from integrity-mismatch exceptions in `scripts/paper_excursion_decomposition.py`.
4. Add a defect-shaped mixed-failure regression: regenerate mismatching edge-excursion data or Figure 4, then make the anchor-correction-summary population unavailable; assert the mismatch is printed, the incomplete terminal token is last, and the return code is 3.
5. Add a defect-shaped present-byte-drift regression: mutate `events.jsonl` behind its retained digest and assert producer and driver return 2 with a mismatch disposition.
6. Add a table-consistency regression that iterates every disposition, invokes the driver finalizer, and asserts its return code, terminal token, and rendered help sentence come from the same row. Deleting the shared finalizer or restoring a literal return code must fail this test.
7. Add a silent-exit-3 regression that asserts `source=excursion` or `source=anchor_summary` plus `detail=no output`, never the corpus root.
8. Run only the focused producer tests and the non-retained-corpus classes in `tests.test_paper_round7_artifacts`; the magistrate separately owns any retained-corpus replay.

Requested lead ruling: choose A, B, or C. Recommendation: A, because it distinguishes “disagreement established” from “replay incomplete” while retaining both facts in a mixed failure.

## Verification notes

The focused non-corpus classes pass. The live help output and source-site inspection confirm the blocked semantics: replay exit 3 preempts and hides earlier mismatches, while a present-file digest disagreement routes through `ArtifactsUnavailable` to exit 3. The repository-wide suite and retained-corpus replay were not run, as required by the preflight rule. Because executable semantics remain unruled, no counterfactual test was added; adding one now would make an unauthorized option normative.

## Residual risk

Until the ruling lands, current behaviour remains fail-closed but diagnostically lossy: a later producer exit 3 can hide an earlier byte mismatch, and a present-byte digest disagreement is labelled unavailable. Neither route can produce a false pass.
