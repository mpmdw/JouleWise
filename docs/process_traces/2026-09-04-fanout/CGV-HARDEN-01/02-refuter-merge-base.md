```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The refreshed mission-only delta is in scope, both claimed test modules pass, and nine behavior-specific mutations are killed; CGV-HARDEN-01 is LANDABLE.",
  "workspace": {
    "base_requested": "bffd467a1dbc4368c653ad9388fd02740da3c8aa",
    "base_mode": "exact",
    "head_start": "bffd467a1dbc4368c653ad9388fd02740da3c8aa",
    "head_end": "bffd467a1dbc4368c653ad9388fd02740da3c8aa",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-CGV-HARDEN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "set -eu\nbase=$(git merge-base origin/main HEAD)\nactual=$(git diff --name-only \"$base\"..HEAD)\nexpected='docs/designs/cgv_harden_01.md\ndocs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/01-sol-report.md\njoulewise/coldgate_receipt.py\ntests/test_coldgate_receipt.py'\n[ \"$actual\" = \"$expected\" ]\ngit diff --quiet \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md\nprintf 'scope: 4/4 allowed; protected state docs: clean\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scope: 4/4 allowed; protected state docs: clean"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^scope: 4/4 allowed; protected state docs: clean$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_coldgate_receipt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests in 0.010s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 7 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_gate_packet",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 28 tests in 2.349s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 28 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "set -eu\nprobe_root=/private/tmp/cgv-harden-01-refuter-v2\ncount=0\nfor mutant in m1_no_anchor_check m2_no_file_fsync m3_no_directory_fsync m4_replace_publication m5_no_atomic_visibility m6_no_name_slash_guard m7_wrong_digest m8_no_temp_cleanup m9_single_write; do\n  if (cd \"$probe_root/$mutant\" && PYTHONPATH=.:tests python3 -m unittest discover -s tests -p 'test_coldgate_receipt.py') >/dev/null 2>&1; then\n    printf 'survived: %s\\n' \"$mutant\"\n    exit 1\n  fi\n  count=$((count + 1))\ndone\nprintf 'mutation matrix: %s/9 killed\\n' \"$count\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "mutation matrix: 9/9 killed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^mutation matrix: 9/9 killed$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git ls-tree -r --name-only bffd467a1dbc4368c653ad9388fd02740da3c8aa -- docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/01-sol-report.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/01-sol-report\\.md$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The reviewed delta intentionally supplies only the receipt-persistence primitive; the magistrate ruled that the future convening runner will wire it when COLDGATE-HANDOFF-01 lands.",
      "needs": "At that later landing, pass the validator's exact stdout bytes into persist_validator_receipt and add a production-call-site regression."
    }
  ]
}
```

## Findings

None.

## Evidence

The review range was `git diff $(git merge-base origin/main HEAD)..HEAD`, whose
merge base was `b0ed6991c11f3a515ad293760c6dfc031adda8e1`. Its four paths exactly
match the implementation report's scope of record. `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`docs/decision_log.md` have no delta.

The magistrate ruling was applied as written: retain the persistence primitive
now and wire it into the convening runner when `COLDGATE-HANDOFF-01` lands. The
absence of a current call site is therefore not a blocker for this landing.

Both claimed modules passed: `tests.test_coldgate_receipt` ran 7 tests and
`tests.test_validate_gate_packet` ran 28 tests. The whole suite was not run,
per the runner's preflight rule. Repository search found no other Python module
importing the new module.

### Counterfactual execution matrix

All mutations were made only in isolated copies under
`/private/tmp/cgv-harden-01-refuter-v2`; the worktree implementation was not
modified.

| Behavior | Counterfactual input | Reversion/mutation | Killing assertion |
|---|---|---|---|
| Directory identity is checked before writing | Replace `receipts/` immediately after its fd is opened | Disable the first identity check while preserving the exception contract | Replacement test reaches its postcondition and finds `validation.json` in the opened tree |
| File durability precedes publication | Normal valid receipt | Remove file `fsync` | Success test observes only directory sync, not `[file, directory]` |
| Directory-sync failure is non-success | Inject `OSError` only for directory `fsync` | Remove directory `fsync` | Expected `ReceiptDurabilityUncertain` is not raised |
| Existing final entries are never overwritten | Pre-create a regular file, then a symlink, at the final name | Replace no-overwrite `link` with `replace` | Both collision subtests report no `ReceiptPublicationCollision` |
| Final name is absent during byte writes | Force one-byte writes of a multi-byte receipt | Publish the hard link before writing | The observer sees the final name during a write |
| Name stays one directory entry | Use `nested/receipt.json` | Remove the slash guard | The expected `ValueError` becomes a publication-path error |
| Returned digest binds stored bytes | Publish the normal valid receipt | Return an all-zero digest | Byte-exact success test detects the digest mismatch |
| Private temporary link is removed | Publish the normal valid receipt | Omit temporary-name unlink | Success test observes link count 2 instead of 1 |
| Short writes are completed | Make every `os.write` accept one byte | Replace `_write_all` with one `os.write` | Multi-write assertion observes only one write and fails |

No previous refuter verdict was present at the pinned head: the directory
contained only `01-sol-report.md`. Accordingly, there was no prior-round
non-staleness blocker to re-test. The mutation matrix directly checks the
spoofing/identity, occupied-name, durability, atomicity, and counterfactual
classes relevant to this mission.

## Residual risk

The production call-site behavior is not reviewable until the separately owned
convening runner lands. That later integration still needs to prove that exact
validator stdout bytes reach this primitive and that every publication
exception prevents runner success.
