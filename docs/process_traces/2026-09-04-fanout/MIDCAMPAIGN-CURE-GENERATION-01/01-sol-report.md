```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The transaction record now carries the complete mid-campaign cure boundary with a mutation-proven regression; the current paper draft remains unchanged under the prompt's explicit ownership fence.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-MIDCAMPAIGN-CURE-GENERATION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-08-22-t20/real-transaction-runbook.md",
    "docs/process_traces/2026-09-04-fanout/MIDCAMPAIGN-CURE-GENERATION-01/01-sol-report.md",
    "tests/test_midcampaign_cure_generation_docs.py"
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
      "cmd": "python3 -m unittest -v tests.test_midcampaign_cure_generation_docs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.000s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport os\nimport subprocess\nimport sys\nimport tempfile\nsource = Path('docs/process_traces/2026-08-22-t20/real-transaction-runbook.md').read_text(encoding='utf-8')\nstart = source.index('### The mid-campaign cure boundary (D-153 W5)')\nend = source.index('**H1\\'s continuation clause', start)\nmutant = source[:start] + source[end:]\nwith tempfile.TemporaryDirectory(prefix='midcampaign-cure-mutant-') as directory:\n    path = Path(directory) / 'real-transaction-runbook.md'\n    path.write_text(mutant, encoding='utf-8')\n    environment = os.environ.copy()\n    environment['MIDCAMPAIGN_CURE_TRANSACTION_RECORD'] = str(path)\n    completed = subprocess.run([sys.executable, '-m', 'unittest', 'tests.test_midcampaign_cure_generation_docs'], cwd='.', env=environment, text=True, capture_output=True, check=False)\n    if completed.returncode == 0:\n        raise SystemExit('counterfactual unexpectedly passed')\n    print(f'MUTANT_EXIT={completed.returncode}')\n    print('COUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTANT_EXIT=1",
          "COUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTANT_EXIT=1\\nCOUNTERFACTUAL_PASS: removing the D-153 section makes the focused module fail"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "if rg -n 'mid-campaign|new family generation|already-running (foreground chain|campaign)' docs/paper/draft-v2-skeleton.md; then exit 1; fi; printf '%s\\n' 'PAPER_LIMITATION_ABSENT: draft-v2-skeleton.md has no D-153 interruption limitation'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PAPER_LIMITATION_ABSENT: draft-v2-skeleton.md has no D-153 interruption limitation"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PAPER_LIMITATION_ABSENT: draft-v2-skeleton.md has no D-153 interruption limitation"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Acceptance requires the paper's limitations to carry the interruption condition, but the prompt expressly forbids editing docs/paper/draft-v2-skeleton.md, the current paper draft and canonical reader-facing limitations section.",
      "needs": "The paper owner must either apply the proposed paragraph to draft-v2-skeleton.md or designate another canonical reader-facing paper artifact; then add a focused counterfactual guard for that artifact."
    }
  ]
}
```

## Change

The `_v4` transaction record now defines a **non-configuration cure** as a
repair to measurement code, policy, or another frozen artifact, rather than a
choice already permitted by the frozen plan. It states the registered rule in
full: while a campaign is in progress, no ALPHA, BETA, or GAMMA path can inject
such a repair into the foreground chain; cured work requires a new family
generation, meaning a newly emitted and frozen set of campaign packs.

The focused test checks both the definition and the all-profile rule. Its
counterfactual run removes only the new section from a temporary copy; the
module then exits unsuccessfully, so deleting the implementation is detected.

| Finding | Decision | State |
|---|---|---|
| The transaction record previously named the rule only as a close-session action and an abort note; it did not spell out that the rule applies equally to ALPHA, BETA, and GAMMA. | Add one glossary-first operational section beside the existing close-session action. | Implemented and tested. |
| The current paper's `Further limitations` section has no conditional statement for an interrupted campaign. | Preserve the paper branch's ownership fence and supply exact insertion text below. | **NEEDS_RULING — paper-owner action required.** |
| The kernel, generated queue, run-state file, decision log, and frozen paper draft were explicitly lead-owned in this task. | Leave them byte-unchanged and report the required follow-up. | Preserved. |

**NEEDS_RULING — paper carriage.** Recommended placement: the current paper's
`Further limitations` subsection, immediately before `Future work`. Proposed
reader-facing paragraph:

> If the measurement campaign is interrupted because a repair requires a
> change to measurement code, policy, or another artifact frozen with the
> campaign, that repair cannot be inserted into the campaign already in
> progress. The interrupted campaign remains preserved, and measurements using
> the repair require a newly generated and frozen campaign family. This
> limitation applies to every registered campaign profile.

Exact completion checklist for the paper owner:

- Apply the paragraph to `docs/paper/draft-v2-skeleton.md` at the placement
  above, or rule a different canonical reader-facing paper home.
- Add a focused test that extracts `Further limitations` and fails if the
  interruption condition or the new-family consequence is removed.
- Run that focused paper test and the existing paper first-use ledger test if
  the insertion introduces any newly governed term.
- After both acceptance clauses are present, update the magistrate-owned kernel
  row and generated projections; this session did not edit them.

## Verification notes

The repository-wide test suite was not run, as the preflight rule forbade it.
Only the new focused module and its temporary-file mutation were executed. The
paper inspection is intentionally green when it proves the limitation is still
absent; it records the ownership blocker rather than acceptance.

## Residual risk

The kernel row is not ready to close until the reader-facing paper carries the
conditional interruption limitation. The operator-facing half is complete;
the paper-facing half is not.
