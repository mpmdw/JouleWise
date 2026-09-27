```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented C1–C3 within the scoped issuer and test files; one live OS-probe test remains blocked by sandboxed sysctl.",
  "workspace": {
    "base_requested": "c84b1dc2fbb52f2296e9cce0b52afe9be5de5d5b",
    "base_mode": "exact",
    "head_start": "c84b1dc2fbb52f2296e9cce0b52afe9be5de5d5b",
    "head_end": "c84b1dc2fbb52f2296e9cce0b52afe9be5de5d5b",
    "upstream_end": null,
    "branch": "fix/2026-09-27-issuer-corpus-root"
  },
  "pathspec": [
    "scripts/issue_calibration_acceptance_generation.py",
    "tests/test_issuer_corpus_root.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_issuer_corpus_root",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 21.370s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 15 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: None is not an instance of <class 'str'>", "Ran 156 tests in 335.188s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 156 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_reissue_calibration_acceptance",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 0.151s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 93 tests in 0.698s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 93 tests.*OK \\(skipped=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-fix1-77b1bee2/mutation_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["test_verifier_refuses_duplicate_id_and_source: M7 drop member uniqueness: RED"]},
      "expected": {"exit_code": 0, "tail_regex": "M7 drop member uniqueness: RED"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/corpus-fix1-77b1bee2 /opt/homebrew/bin/python3 /tmp/corpus-fix1-77b1bee2/r8_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R8 projected triples=24; intended accepted=24; /Users/edr refused=24/24; W1 night refused=24/24; / refused=24/24"]},
      "expected": {"exit_code": 0, "tail_regex": "intended accepted=24.*W1 night refused=24/24"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "other",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["sysctl: sysctl fmt -1 1024 1: Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The issuer suite's sole failure is its live OS-probe test; sandboxed sysctl returns Operation not permitted.",
      "needs": "Lead reruns the issuer suite where sysctl is permitted."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unittest discovery suite was not run; the four directed suites and focused mutation probes were run.",
      "needs": "Lead runs the canonical suite at its final verification gate."
    }
  ]
}
```

## Change

- **C1:** [The issuer](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/scripts/issue_calibration_acceptance_generation.py:926) now requires exactly `<session_id>/runs/instrument_validation/<attempt_id>`. Verification checks that shape against the session in the prior-set row. [Tests](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/tests/test_issuer_corpus_root.py:228) cover the nested-root ambiguity, three- and five-part paths, and a wrong middle part. The path-string-only R8 probe accepted 24/24 under the intended root and refused 24/24 under each wrong root.
- **C2:** [Revision 5 and same-ledger tests](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/tests/test_issuer_corpus_root.py:123) cover checkout-owned ledger, pin, verdicts, and Git; the battery-root mutation refuses. The flag comparison preserves member IDs and order, `derivation_input_sha256`, and ledger cutoff; after normalizing only source paths, the custody note, and `derivation_sha256`, the artifacts match.
- **C3:** [The pre-pass and verifier](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1271) refuse duplicate valid attempt IDs and duplicate member IDs or source directories. Tests cover missing primary files and prior-row session mismatch. The tests use `tempfile`, and `--repo-root` help identifies the run checkout. `_repo_relative_custody` and no-flag behavior were left unchanged. The fixture builder needed no edit.

## Verification notes

| New test | Named cut | Result |
|---|---|---|
| Revision 5 checkout authentication | M1: route battery authentication to corpus root | RED |
| Same-ledger equivalence | M2: use repo-relative naming despite flag | RED |
| Exact four-part naming | M3: restore the old two-or-more-part rule | RED |
| Duplicate valid attempt | M4: remove the pre-pass duplicate guard | RED |
| Missing primary and prior session | M5: take session identity from stored path | RED |
| Stored-path shape | M6: restore permissive naming and verification shapes | RED |
| Duplicate member ID and source | M7: remove member uniqueness | RED |

The issuer suite ran 156 tests; its only failure was the live OS probe. `sysctl -n kern.osversion` separately returned “Operation not permitted.”

## Residual risk

The lead needs to rerun the issuer and canonical suites where the live OS probe is permitted. No commit was made.