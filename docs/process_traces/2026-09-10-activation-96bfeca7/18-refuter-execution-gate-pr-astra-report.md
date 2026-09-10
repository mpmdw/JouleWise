```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "One should_fix endpoint-mutation coverage gap; temporary-storage restrictions block full suite and producer check; repository unchanged.",
  "workspace": {
    "base_requested": "078a13a461abd124c29796798da5107fe00190a6",
    "base_mode": "exact",
    "head_start": "8da99190c67127eb632452444c58977d7279b247",
    "head_end": "8da99190c67127eb632452444c58977d7279b247",
    "upstream_end": "57da1d3031388750dade45ca5ca6d703244dcf88",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "path": "tests/test_gate_sensibility_rounding.py",
        "line": 104,
        "summary": "Capture-endpoint REFUSE coverage survives widening only the two endpoint allowances from 1 us to 1 ms.",
        "reproduction": "V5",
        "recommendation": "Add left/right 10 us capture-containment refusal cases; preserve the duration-excess and missing-sample tests."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail\nPYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gate_sensibility_rounding tests.test_environment_admission tests.test_controller tests.test_load_transition_alignment tests.test_generate_g2a_probe_inputs tests.test_reduce -v 2>&1 | tail -40",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-gate']"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gate_sensibility_rounding.CooldownRoundingTests tests.test_gate_sensibility_rounding.TransitionMidpointRoundingTests -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import tempfile\nimport unittest\nfrom unittest.mock import patch\n# Avoid only the import-time writable-temp probe; the selected test does read-only hashing.\nwith patch.object(tempfile, '\\''gettempdir'\\'', return_value='\\''/tmp'\\''):\n    from tests.test_reduce import D078R01RegressionTests\nresult = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([\n    D078R01RegressionTests('\\''test_d138_reduce_source_bytes_remain_at_issued_pin'\\'')\n]))\nraise SystemExit(not result.wasSuccessful())\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --stat && git diff --cached --stat && git diff --exit-code 078a13a4..8da99190 -- joulewise/reduce.py && git rev-parse HEAD && git rev-parse refs/remotes/origin/main && git diff --name-only 078a13a4..8da99190",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["scripts/generate_g2a_probe_inputs.py", "tests/test_gate_sensibility_rounding.py", "tests/test_generate_g2a_probe_inputs.py"]
      },
      "expected": {"exit_code": 0, "tail_regex": "tests/test_generate_g2a_probe_inputs.py"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import contextlib,io,unittest\nfrom pathlib import Path\nfrom unittest.mock import patch\nfrom joulewise import environment_admission as e\nfrom tests import test_gate_sensibility_rounding as t\ns=Path(e.__file__).read_text()\nfor old,new in [(\"attempt_start_s - ADMISSION_TIME_ROUNDING_S\",\"attempt_start_s - 1e-3\"),(\"attempt_end_s + ADMISSION_TIME_ROUNDING_S\",\"attempt_end_s + 1e-3\")]:\n    assert s.count(old)==1\n    s=s.replace(old,new)\nexec(compile(s,e.__file__,\"exec\"),vars(e))\ndata=[]\nwith patch.object(t.tempfile,\"TemporaryDirectory\",lambda:contextlib.nullcontext(\"/__memory__\")),patch.object(Path,\"write_text\",lambda p,s:data.append(s)),patch.object(e,\"read_authentication_text\",lambda *a,**k:data[-1]):\n    r=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromModule(t))\n    for shift in (-1e-5,1e-5):\n        print(\"capture_shift\",shift,\"refusals\",t.AdmissionRoundingTests()._refusals(capture_shift_s=shift))\nraise SystemExit(not r.wasSuccessful())\n'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["OK", "capture_shift -1e-05 refusals ()", "capture_shift 1e-05 refusals ()"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_generate_g2a_probe_inputs.GenerateG2AProbeInputsTests.test_check_is_read_only tests.test_generate_g2a_probe_inputs.GenerateG2AProbeInputsTests.test_idle_capture_alone_clears_rate_fit_span_and_idle_count_gates -v",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (errors=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "set -o pipefail\nPYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness -v 2>&1 | tail -25",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (errors=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The read-only runner has no usable temporary directory. V1 stopped during import; V6 failed in setup; V7 had 28 passes and three temporary-directory errors. The known controller failure was not reached or reproduced on main.",
      "needs": "Lead reruns the requested suite and baseline comparison, producer build/bind/check tests, and remaining docs tests in a runner with writable temporary storage; repository WRITE_SCOPE can remain empty."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "R1 mutation runs replaced temporary-file transport with memory while retaining JSONL parsing and admission predicates. R3/R4 used production functions compiled in memory. These are supplemental tests, not full filesystem/authentication coverage. The D-138 test only mocked the import-time tempfile.gettempdir probe.",
      "needs": "Confirm the same R1 mutation results using real temporary files."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The supplied backup path lacked seat A's report; its committed worktree copy was read. The sizing report was read at the supplied backup path. Twenty-four historical G2-a fixture configs still have 30 s idle at 20 Hz and matching inventory hashes; no claim that all committed 30 s pins are absent is made.",
      "needs": "Regenerate and rebind prospective 75 s inputs before arming; preserve historical fixtures and evidence."
    }
  ]
}
```

## Findings

**R1 — should_fix: endpoint refusal tests do not constrain the new numerical allowance.** Widening only the two capture-containment comparisons to 1 ms leaves all 12 new tests green. That mutant admits both ±10 μs capture shifts; the actual branch refuses both. The existing ±100 ms cases cannot detect this widening. Reproduce with **V5** above. Add ±10 μs endpoint cases, preferably mutation-checking each comparison independently. This is a coverage defect; the branch’s production comparisons behaved correctly.

Disposition of the five requested items:

1. **Suite: blocked, not cleared.** The pipeline returned **1**, with `pipefail` enabled, during import because no temporary directory was writable. I cannot confirm the known controller failure is the only failure or reproduce its baseline behavior. **No finding on R2 preservation:** `reduce.py` is byte-identical to `078a13a4`, and the actual D-138 pin test passed with the narrowly described import accommodation.

2. **Mutation execution: R1 finding above; no finding on R3/R4 within executed coverage.** All substitutions were in memory.

   | Mutation | Observed regression |
   |---|---|
   | R1 allowance reverted to `1e-9` | Both ADMIT tests failed: interval-sum rounding and either capture endpoint |
   | R3 production hunk reverted | Both ADMIT tests failed: span rounding and summed coverage rounding |
   | R4 production hunk reverted | Epoch-marker ADMIT test errored with eight `offset_s does not equal support midpoint` refusals; REFUSE fixture construction also errored |
   | R1 shared allowance → `1e-3` | Ten-microsecond duration-excess REFUSE test failed |
   | R3 new allowances → `1e-3` | Ten-microsecond span and coverage REFUSE tests failed |
   | R1 endpoint comparisons alone → `1e-3` | **Survived: all 12 tests passed** |
   | R4 midpoint identity tolerance → `1e-3` | One-microsecond offset-mutation REFUSE test failed |

   R4 introduces **no new allowance**: it aligns arithmetic order. Widening its existing `1e-12` identity tolerance ×1000 to `1e-9` leaves the 1 μs refusal intact, as expected. After restoring the in-memory functions, all 12 supplemental tests passed. The eight R3/R4 tests also passed without filesystem substitutions. Both repository diff statistics remained empty.

3. **Same-signature sweep: no finding.** No remaining `1e-9`/`1e-12` epoch-containment or cooldown-completion comparison was found in the three repaired modules. Both cooldown callers use `cooldown_gate`. Current admission consumers in `reduce.py`, `floor_extraction.py`, `whole_window.py`, and `scripts/run_campaign.py` dispatch to `current_environment_refusals`. Remaining tight comparisons concern copied bounds, derived offsets/residuals, or energy/power identities; the deliberately deferred reducer coverage predicate remains unchanged.

4. **Idle sizing: no production finding from inspection and direct execution; checker completion blocked.** Calling `_config_for` for all 24 members produced schema-valid configurations with **75 s idle and 10 Hz**, satisfying the new sizing bounds. V6 could not reach build/bind/check because setup requires temporary storage.

   The literal “no committed artifact pins 30 s” assertion is **false**: 24 configs under `tests/fixtures/g2a/pin/config-root/` contain **30 s at 20 Hz**, and all 24 hashes match their committed inventory. These are existing pin-consumer fixtures, not prospective outputs from the changed producer. Historical campaign configs also retain 30 s. No 30-second requirement was found in the G2 runsheet or applicable contract text.

   Arithmetic:
   - Additional records: `24 × (75−30) / 0.1 = 10,800`.
   - Additional capture time at 115 ms: `10,800 × 0.115 = 1,242 s = 20.7 min`.
   - Allocated chain end: `02:56 + 13,500 s = 06:41`.
   - Courier allocation end: `06:41 + 300 s = 06:46 < 07:00`, with **840 s** remaining.

   This clears the strict inequality **with 13,500 s as the total chain budget**. Adding 1,242 s on top of that allocation would end at **07:06:42** and fail.

5. **Contract text: no finding.** Both new methodology sentences are reconstructible with their surrounding definitions:

   > Numerical containment of each positive-duration baseline and its capture within the admission attempt allows at most 1 μs of epoch-representation discrepancy and never credits unobserved time.

   This specifies the duration and endpoint allowance while preserving positive-duration requirements.

   > Numerical completion allows 1 μs for span and, for coverage, the greater of 1 μs and the summed endpoint ULPs of positive overlap contributions plus one coverage-sum ULP; neither credits unobserved time.

   This specifies `max(1e-6, Σ endpoint ULPs + ulp(coverage_sum))` for coverage and `1e-6` for span.

   The additional load-transition clarification is also reconstructible:

   > Let `a_i = S_i,start - M_i` and `b_i = S_i,end - M_i`. The frozen artifact arithmetic is implemented by forming the endpoint offsets `a_i`, `b_i` first and then taking their midpoint:

   No document-byte pin was found by path/reference inspection or searches for either document’s base/head SHA-256 in configs, tests, scripts, and production modules. `test_docs_freshness` does not pin these sentences: **28 tests passed; three errored solely on unavailable temporary storage**.

## Residual risk

Full filesystem-backed verification remains outstanding. The next exact step is to rerun **V1 and V6** with writable temporary storage, establish the controller failure against the exact base, and confirm the endpoint mutation finding without the supplemental memory transport. No files were changed, no commits were made, and no live capture was started.