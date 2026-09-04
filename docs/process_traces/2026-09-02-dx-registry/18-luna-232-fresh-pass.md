```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round-7 delta is contract-correct and environment-independent; one latent TMPDIR dependency remains in the sibling gate-ledger test.",
  "workspace": {
    "base_requested": "8efbb200",
    "base_mode": "exact",
    "head_start": "c8ea9e95f517d7f204ec3277cc5a8000afebaced",
    "head_end": "c8ea9e95f517d7f204ec3277cc5a8000afebaced",
    "upstream_end": null,
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "SHOULD-FIX 1",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:33",
        "title": "Sibling test hard-requires TMPDIR",
        "counterfactual": "env -u TMPDIR causes setUpClass to raise KeyError before any tests run.",
        "observed": "Ran 0 tests; FAILED (errors=1); KeyError: 'TMPDIR'.",
        "scope": "Sibling latent defect; not introduced by c8ea9e95."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 43 tests in 0.802s", "OK", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests.*OK.*EXIT=0"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env -u TMPDIR python3 -m unittest tests.test_paper_round7_artifacts.RegistryAndDigestTests tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 43 tests in 0.787s", "OK", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests.*OK.*EXIT=0"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["R7F PLACED 0/16", "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16.*R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0.*EXIT=0"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "env -u TMPDIR python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["R7F PLACED 0/16", "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16.*R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0.*EXIT=0"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.114s", "OK", "EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK.*EXIT=0"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --exit-code c8ea9e95 -- tests/test_paper_round7_artifacts.py; git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DIFF_EXIT=0", "STATUS_EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DIFF_EXIT=0.*STATUS_EXIT=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sibling test_check_gate_ledger.py uses os.environ[\"TMPDIR\"] directly and fails when TMPDIR is unset.",
      "needs": "Use tempfile.gettempdir() fallback in the sibling test."
    }
  ]
}
```

## Findings

F1 — SHOULD-FIX, sibling latent defect: `tests/test_check_gate_ledger.py:33` hard-requires `TMPDIR`. The sibling suite passes with the exported TMPDIR but fails under `env -u TMPDIR` before running tests. Its path assertion at line 362 has no symlink hazard because the checker echoes `args.repo_root` without resolving it.

No blocker or nit findings apply to the c8ea9e95 delta.

## Contract

The fence resolves `args.corpus_root` at `scripts/check_paper_round7_artifacts.py:978`, constructs required paths from that resolved root, and raises `ArtifactsUnavailable(str(path))` at lines 865–867. Therefore the output line names the resolved file actually tried.

The test-side `.resolve()` at `tests/test_paper_round7_artifacts.py:811` is the correct fix. Printing `args.corpus_root` instead would report the input spelling rather than the path used for the filesystem attempt, violating the fence contract.

The ruling’s P3 requirement is: `per_pulse[0].onset_best_fit_lag_ms: "16.0"` must exit 2 and name `figure onset mark 0` plus `expected number, found str`. Neither corpus-path spelling choice affects that typed-scalar regression.

## Census

All other `SCRATCH_PARENT` users in `tests/test_paper_round7_artifacts.py` were checked. The tests at lines 423, 498, 520, 541, 562, 597, 621, 646, 670, 693, 736, 759, and 777 create scratch paths, but none compares `str(path)` with fence stdout/stderr. They assert fixed diagnostic text or pass paths only as CLI arguments; no equivalent symlink hazard is latent.

## Executed evidence

Counterfactual probe after removing `.resolve()`:

- Exported scratchpad TMPDIR: `InvocationTests`, 2 tests, `OK`, exit 0.
- `env -u TMPDIR`: one expected failure; fence emitted `/private/tmp/...`, while the unresolved test expected `/tmp/...`; exit 1.
- The original `.resolve()` was restored. `git diff --exit-code c8ea9e95 -- tests/test_paper_round7_artifacts.py` returned 0.

Sibling check:

```text
python3 -m unittest tests.test_check_gate_ledger
Ran 31 tests ... OK
EXIT=0

env -u TMPDIR python3 -m unittest tests.test_check_gate_ledger
Ran 0 tests ... FAILED (errors=1)
KeyError: 'TMPDIR'
EXIT=1
```

VERDICT: SHOULD-FIX 1

`git status --porcelain`

(empty)