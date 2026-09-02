```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All accepted fixes, hashes, schema validation, launch-boundary review, and 35-test module pass; only the explicitly open title first-use FAIL remains.",
  "workspace": {
    "base_requested": "ec3794e9",
    "base_mode": "exact",
    "head_start": "ec3794e90d257aaeb039482a4305ad0ede9a1a45",
    "head_end": "ec3794e90d257aaeb039482a4305ad0ede9a1a45",
    "upstream_end": "a37b0b9f72928e345739c8ef88a28b4198dd1133",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F-163-6-TITLE",
        "severity": "should_fix",
        "doc_line": 1,
        "title": "Title first-use FAIL",
        "text": "The title uses identity-pin projection and receipt before their prose definitions at lines 9 and 41. R-163-6 explicitly left this title exception open."
      }
    ],
    "rulings": {
      "R-163-1": "pass",
      "R-163-2": "pass",
      "R-163-3": "pass",
      "R-163-4": "pass",
      "R-163-5": "pass",
      "R-163-6": "pass_except_title"
    },
    "hash_recompute": "pass",
    "pasteable_envelope": "pass",
    "launch_boundary": "pass",
    "test_delta": "pass"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "independent Python worked-example hash assertions",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["all worked-example hashes: PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^all worked-example hashes: PASS$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/identity-pin-delta-zfirHC PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 35 tests in 6.640s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 35 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check a37b0b9f ec3794e9 -- docs/contracts/identity_pin_projection.md tests/test_identity_pins.py",
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
      "id": "FL1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The prompt names joulewise/launch_window.py; that path is absent at this head. The actual executable is scripts/launch_window.py.",
      "needs": ""
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical unittest discover was not run because the task expressly prohibited it.",
      "needs": ""
    }
  ]
}
```

## Findings

- F-163-6-TITLE — SHOULD-FIX: line 1 is the sole mechanical first-use FAIL; all other terms are BUILT or GLOSSED.

- R-163-1: exact eight-key envelope, null pins/receipt, state rules, and supersession shape are present at `docs/contracts/identity_pin_projection.md:142-213`; the pasteable example validates.

- R-163-2: exact predicates at `docs/...:48-69` match `identity_pins.py:217-236` and prefix constants at `:158-163`.

- R-163-3: raw configs, normalized identity, eleven-field stack, projection input, and both model paths are present at `docs/...:545-670`. Independent recomputation matched every printed digest: raw `5bee…9805`/`bca6…00b0`, normalized `9536…c019`, stack `e2dc…4e36`, projection `6d3a…d1cd`, `TOY` `6361…fdfb`, `TOZ` `89da…14f`, plus both token hashes.

- R-163-4: test lines `569-597` compare exact GNU sidecar bytes and mutate the actual sidecar. `_load_frozen_receipt` reads and rejects that counterfactual at `identity_pins.py:1853-1883`.

- R-163-5: no launch-boundary test was added. The map row is at `docs/...:731`; the scheduled move is accurately stated at `:733-735`. `scripts/launch_window.py:239-264` authenticates, consumes, verifies, then calls `execve`; it contains no realization re-derivation.

- No normative contradiction found against `identity_pins.py`, `arm_readiness.py:5611-5708`, or `adapters/mlx_runtime.py:315-349,940-946,1109-1114`.

## Residual risk

No live MLX, hardware, or physical-energy validation was run. The launch-time recheck remains an explicitly scheduled follow-up.

DELTA NOT CLEAN