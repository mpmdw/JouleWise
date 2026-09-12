```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two should-fix findings: active restart framing still claims a byte freeze, and rendered-signature comparison admits a meaningful default-value bypass.",
  "workspace": {
    "base_requested": "c2f81d4",
    "base_mode": "exact",
    "head_start": "4c0897a39a89542e4d01f2822a681c6610f4d139",
    "head_end": "4c0897a39a89542e4d01f2822a681c6610f4d139",
    "upstream_end": "4c0897a39a89542e4d01f2822a681c6610f4d139",
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Active restart instructions retain the rejected byte-frozen mint-core framing",
        "location": "RUN_STATE.md:49"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Stringified signature comparison can accept a behavior-changing default",
        "location": "scripts/mint_floor_artifact_generalized.py:469"
      }
    ],
    "audit_answers": {
      "A1": "Partially fails because RUN_STATE.md:49 and :56 retain binding byte-frozen/frozen-expectation framing. The amended code otherwise matches the live D-109 signature; the literal pin exists; the parity test retains read_bytes equality; and the snapshot regression uses assertIs at both authentication seams and rebinding with one loader call.",
      "A2": "No. Keyword-only changes and ordinary default changes alter the rendered signature, but a custom default whose repr is 'None' passes while changing the required load behavior.",
      "A3": "Pass. A fresh automatic merge of c2f81d4 and bd83f83 produced tree f591fc61f6a1a6e2ccdd8108986857289cfaca3a, exactly equal to 341055e's recorded tree; remerge diff was empty.",
      "A4": "Pass. A mutation adding a second snapshot-loader call was detected as Called 2 times. Different-but-equal objects would fail because the sentinel is object() and every consumer assertion uses assertIs."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp python3 -B -m unittest tests.test_mint_floor_artifact_generalized tests.test_mint_floor_artifact",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 53 tests in 0.809s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 53 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "set -eu\naudit_tmp=$(mktemp -d /tmp/calbracket-audit.XXXXXX)\ngit clone --quiet --no-hardlinks . \"$audit_tmp/repo\"\ncd \"$audit_tmp/repo\"\nmerge_tree=$(git merge-tree --write-tree c2f81d4 bd83f83)\nrecorded_tree=$(git rev-parse '341055e^{tree}')\nprintf '%s\\n' \"merge-tree=$merge_tree\" \"recorded-tree=$recorded_tree\"\ntest \"$merge_tree\" = \"$recorded_tree\"\ngit show --remerge-diff --format= 341055e",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "merge-tree=f591fc61f6a1a6e2ccdd8108986857289cfaca3a",
          "recorded-tree=f591fc61f6a1a6e2ccdd8108986857289cfaca3a"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "merge-tree=(f591fc61f6a1a6e2ccdd8108986857289cfaca3a)[\\s\\S]*recorded-tree=\\1"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=/tmp python3 -B - <<'PY'\nimport inspect\nfrom scripts import mint_floor_artifact_generalized as generalized\ncore = generalized._fresh_original_core()\nclass FauxNone:\n    def __repr__(self): return 'None'\nfaux_none = FauxNone()\ncore.mint_floor_artifact.__kwdefaults__['calibration_ledger_snapshot'] = faux_none\nprint(f\"rendered-signature-equal={str(inspect.signature(core.mint_floor_artifact)) == generalized._CORE_SIGNATURES['mint_floor_artifact']}\")\ngeneralized._assert_core_interface(core)\nactual = inspect.signature(core.mint_floor_artifact).parameters['calibration_ledger_snapshot'].default\nprint(f'guard-passed-with-non-None-default={actual is faux_none}')\nprint(f'default-is-None={actual is None}')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "rendered-signature-equal=True",
          "guard-passed-with-non-None-default=True",
          "default-is-None=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rendered-signature-equal=True[\\s\\S]*guard-passed-with-non-None-default=True[\\s\\S]*default-is-None=False"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=. TMPDIR=/tmp python3 -B /tmp/calbracket_snapshot_mutation_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "mutation detected: second loader call produced the expected test failure"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "mutation detected: second loader call produced the expected test failure"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n -i \"byte[- ]frozen|frozen expectation\" RUN_STATE.md scripts/mint_floor_artifact_generalized.py tests/test_mint_floor_artifact_generalized.py tests/test_mint_floor_artifact.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RUN_STATE.md:49:   `scripts/mint_floor_artifact_generalized.py` holds a BYTE-FROZEN",
          "RUN_STATE.md:56:   Recommended shape is in the finding — update the frozen expectation"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RUN_STATE.md:49:[\\s\\S]*RUN_STATE.md:56:"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check 341055e..4c0897a && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/cal-bracket-d079...origin/impl/cal-bracket-d079"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/cal-bracket-d079"
      }
    }
  ],
  "flags": []
}
```

## Findings

F1 — should_fix — [RUN_STATE.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/RUN_STATE.md:49)

The active successor script still says the generalized tool holds a “BYTE-FROZEN” interface and instructs the successor to update a “frozen expectation” at line 56. This is current restart authority, not preserved historical evidence. A successor following it could incorrectly treat the selected signature pin as a core-byte freeze or revive historical-byte identity as the oracle, contrary to the adopted review-pinned-interface framing and D-110.

F2 — should_fix — [mint_floor_artifact_generalized.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/scripts/mint_floor_artifact_generalized.py:469)

`str(inspect.signature(...))` is not airtight for meaningful default changes. I replaced the ledger parameter’s keyword default with a non-`None` object whose `repr()` returns `None`. The rendered signature remained exactly equal to the pin and `_assert_core_interface` passed. At invocation, however, `mint_floor_artifact.py:1959` sees the default is not `None` and skips the mandatory ledger-snapshot load.

Compare parameter structure directly and identity-check security-relevant sentinel defaults—particularly `calibration_ledger_snapshot.default is None`—rather than trusting their rendered representation. `__signature__` spoofing is a related residual property of the current approach.

Checks performed: exact replay commands and results are recorded in V1–V6 above.

## Residual risk

The full repository suite and an issued-ledger governed re-mint were not run. The latter remains correctly gated by D-110; the authorized focused modules covered all three amendment files.