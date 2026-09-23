```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed Z1–Z7 within scope; the four named acceptance modules pass.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "descendant",
    "head_start": "6d1e004ffe24e49c61f5415860cffa50212cf850",
    "head_end": "6d1e004ffe24e49c61f5415860cffa50212cf850",
    "upstream_end": null,
    "branch": "feat/2026-09-23-a277-successor-facts"
  },
  "pathspec": [
    "joulewise/zero_capture_facts.py",
    "joulewise/arm_retry.py",
    "joulewise/evidence_night.py",
    "tests/test_zero_capture_facts.py",
    "tests/test_arm_retry.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_evidence_night.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/contracts/night_quiet_admission.md"
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
      "cmd": "python3 -B -m unittest tests.test_zero_capture_facts tests.test_arm_retry tests.test_evidence_night tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 310 tests in 861.861s", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 310 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_zero_capture_facts tests.test_arm_retry tests.test_evidence_night tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 310 tests in 376.338s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 310 tests in .*\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Real launchctl publication was not exercised under the hard fence; the production claim gate was inspected and the rehearsal path was tested.",
      "needs": "Magistrate review of the production publication branch."
    }
  ]
}
```

## Change

- **Z1:** Removed the ledger-session field and read from [zero_capture_facts.py](/Users/edr/code/wt-1d3796d5-a277/joulewise/zero_capture_facts.py:79) and its successor check in [arm_retry.py](/Users/edr/code/wt-1d3796d5-a277/joulewise/arm_retry.py:250). The code comment at line 109 and [contract](/Users/edr/code/wt-1d3796d5-a277/docs/contracts/night_quiet_admission.md:305) cite the driver ordering: `run_night.py:536` creates `chain.started` before the chain starts at `:3170`; ledger sessions are appended inside the chain.
- **Z2:** [Watchdog parity tests](/Users/edr/code/wt-1d3796d5-a277/tests/test_magistrate_watchdog.py:228) pin the base fixture decisions. The [contract](/Users/edr/code/wt-1d3796d5-a277/docs/contracts/night_quiet_admission.md:309) states the deliberate stricter case: any symlink inside custody prevents early release, including an unrelated one. The one-way release record remains unchanged.
- **Z3:** [Custody tests](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2728) now say “while release is recorded” and show the missing-root refusal ends when the key is forgotten. The same operator-action sentence appears byte-identically in [NIGHT_HANDBACK.md](/Users/edr/code/wt-1d3796d5-a277/docs/process/NIGHT_HANDBACK.md:141) and the [runbook](/Users/edr/code/wt-1d3796d5-a277/docs/phase_2/derivation_night_runbook.md:1939).
- **Z4:** [Claim creation](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:884) now fsyncs a temporary file, links it to the exclusive final name, then removes the temporary file. The [reader](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:766) ignores dot-files and still refuses malformed final claims.
- **Z5:** [Publication](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:1655) creates a claim only for a real publication; the [rehearsal regression](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2597) checks that fake launchctl leaves no claim.
- **Z6:** The [released-key check](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:831) compares resolved parent paths while retaining detection of a symlinked custody root. The [path-spelling regression](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2741) covers it.
- **Z7:** The [contract](/Users/edr/code/wt-1d3796d5-a277/docs/contracts/night_quiet_admission.md:305) glosses “latched” and “bare C5 receipt row” at first use, limits the claim to the predecessor’s completion time, and explains the cost of re-preparing changed bytes after failed publication.

## Verification notes

The first acceptance run found two incorrect uses of the test helper and one real regression in the resolved-path check. Those were corrected; the identical named command then passed **310 tests**. The two policy blocks also matched `render_policy()` byte for byte.

The base column below is derived from the `313efcca` predicate and its fixture expectations; the new column was exercised by the parity test. “Release” means the delivered-refusal predicate releases the hold.

| Fixture | `313efcca` | `6d1e004f` | New |
|---|---|---|---|
| Clean calibration | Release | Release | Release |
| Clean evidence | Release | Release | Release |
| Nested custody reservation | Refuse | Refuse | Refuse |
| Runs-root reservation | Refuse | Refuse | Refuse |
| Calibration capture | Refuse | Refuse | Refuse |
| Evidence capture | Refuse | Refuse | Refuse |
| Broken capture symlink | Refuse | Refuse | Refuse |
| Nonempty envelope index | Refuse | Refuse | Refuse |
| Empty envelope index | Release | Release | Release |
| `chain.started` | Refuse | Refuse | Refuse |
| Missing chain | Refuse | Refuse | Refuse |
| Ambiguous payload kind | Refuse | Refuse | Refuse |
| Unrelated symlink inside custody | Release | Refuse | Refuse |
| Torn, unrelated shared-ledger line | Release | Refuse | Release |

Behavior-changing regression counterfactuals against `6d1e004f`:

| Test | Counterfactual at `6d1e004f` | New result |
|---|---|---|
| [Shared-ledger facts](/Users/edr/code/wt-1d3796d5-a277/tests/test_zero_capture_facts.py:54) and [watchdog release](/Users/edr/code/wt-1d3796d5-a277/tests/test_magistrate_watchdog.py:293) | Torn unrelated line blocks a clean fact scan and early release | Pass |
| [Claim scratch and metadata](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2752) | A crash-left temporary file or `.DS_Store` blocks the check | Pass; malformed final claim still refuses |
| [Rehearsal claim](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2597) | Fake launchctl creates the claim | Pass; no claim created |
| [Resolved release key](/Users/edr/code/wt-1d3796d5-a277/tests/test_evidence_night.py:2741) | Differently spelled parent skips the missing-custody refusal | Pass; refusal detected |

The parity test, stricter-symlink test, and renamed custody tests characterize behavior already present at `6d1e004f`; they are intentionally not claimed as failing-baseline regressions.

## Residual risk

The magistrate should double-check the `if not fake` production branch immediately before publication, the link collision behavior under a concurrent final claim, and the driver-ordering citation. Real publication and live watchdog execution were excluded by the hard fences. The successor-cannot-license-again rule and courier format pin remain with their recorded out-of-scope lanes.