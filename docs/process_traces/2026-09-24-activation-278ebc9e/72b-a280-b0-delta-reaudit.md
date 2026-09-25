```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Named cure witnesses and unchanged goldens pass, but two blockers and two should-fix gaps remain.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "A1": "FAIL: original witnesses satisfy their rulings, but expanded probes show C1 and C2 remain incomplete.",
    "A2": "FAIL: unauthenticated wrapper selection remains. No additional defect unique to the fix-round delta was established.",
    "A3": "FAIL: unreadable wrappers still alter cleanup and refusal behavior; malformed preparation kinds escape as TypeError.",
    "A4": "PASS: both tests pass; their complete function sources and GOLDENS values are unchanged from base.",
    "cures": {
      "C1": "PARTIAL: w1 reporting bytes match base; Sol F1 is cured; F1 and F4 below remain.",
      "C2": "PARTIAL: w2 accepts all four cases at base and head; F2 and F3 below remain.",
      "C3": "PASS: evidence_night.py:241 validates NightPlan; malformed [] gives the base Refused text.",
      "C4": "PASS: test_night_kinds.py:558 kills M3; the pre-fix mutant survives.",
      "C5": "PASS: gen_evidence_night.py:20 preserves malformed-plan and receipt-class refusal ordering.",
      "C6": "PASS: symbolic KIND scan, ImportError handling, and removal of repeated reporting kind reads verified."
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/run_night.py:1009",
        "witness": "With a non-UTF-8 wrapper and a C5 receipt encoded as UTF-8 BOM or UTF-16, the real receipt validator returns []. Base cleanup writes the refused outcome and calls write_refusal once. Head skips both and returns 'evidence outcome/cleanup unavailable: ValueError: night payload kind unavailable'.",
        "cure": "Reuse the already validated C5 receipt, or parse its bytes consistently with _evidence_cleanup_error. Preserve base repair behavior without introducing another kind authority."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "location": "joulewise/evidence_night.py:249; joulewise/evidence_night.py:689",
        "witness": "Intact sealing passes at base, pre-fix and head. Missing, non-UTF-8, ambiguous and declaration-stripped wrappers give 'sealed candidate failed wrapper sidecar' at base but new kind-related texts at head. A changed bound source gives 'dirty clone' at base versus 'candidate chain source differs from sealed binding' at head.",
        "cure": "Preserve the established shared validation order and refusal texts before new kind/source checks; retain authenticated row selection and fail-closed dispatch."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "location": "joulewise/evidence_night.py:639",
        "witness": "For an otherwise complete idle preparation with kind=[] or kind={}, base raises Refused('candidate is not a completed, owned preparation'); head raises uncaught TypeError during NIGHT_KINDS.get.",
        "cure": "Validate the kind field's type before lookup and retain the historical typed refusal."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "location": "scripts/run_night.py:1019",
        "witness": "_custody_row accepts a bare wrapper without any sidecar, source binding or C5 receipt: a declarationless file returns calibration and an idle export returns quiet_predicate_evidence. This private dispatch helper does not establish the claimed authenticated identity. No public cleanup bypass was demonstrated; that caller separately validates C5.",
        "cure": "Require authenticated wrapper identity or a validated C5 receipt before returning a dispatch row; otherwise refuse typed. Keep reporting row-neutral."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/278ebc9e/b0audit/harness:. TMPDIR=/tmp/278ebc9e/b0audit python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_gen_evidence_night tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_zero_capture_facts tests.test_kind_dispatch_literals",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["Ran 603 tests in 1648.844s","FAILED (failures=3, errors=1, skipped=9)"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "sh /tmp/278ebc9e/b0audit/witnesses.sh",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["head F1:","F1 missing_no_C5: ValueError night payload kind unavailable","F1 wrapper_vs_C5: ValueError night payload kind differs from authenticated receipt","F1 cleanup: night payload kind differs from authenticated receipt outcome_exists= False refusal_calls= 0"]},
      "expected": {"exit_code":0,"tail_regex":"outcome_exists= False refusal_calls= 0"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "sh /tmp/278ebc9e/b0audit/delta_probes.sh",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["head source_drift Refused candidate chain source differs from sealed binding","head unauthenticated_wrapper no sidecar/source/C5: calibration","head unauthenticated_wrapper idle no sidecar/source/C5: quiet_predicate_evidence","reporting: courier argv, artifact inventory and copied bytes BASE=HEAD for 4 kind failures; zero kind reads"]},
      "expected": {"exit_code":0,"tail_regex":"zero kind reads"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "sh /tmp/278ebc9e/b0audit/mutation.sh",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 9.804s","FAILED (failures=1)"]},
      "expected": {"exit_code":0,"tail_regex":"FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/278ebc9e/b0audit/harness:. TMPDIR=/tmp/278ebc9e/b0audit python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_base_archive_byte_goldens tests.test_night_kinds.NightKindTests.test_refusal_parity",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 2 tests in 26.567s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -B /tmp/278ebc9e/b0audit/unchanged.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["test_base_archive_byte_goldens: source UNCHANGED","test_refusal_parity: source UNCHANGED","GOLDENS: expected bytes UNCHANGED"]},
      "expected": {"exit_code":0,"tail_regex":"GOLDENS: expected bytes UNCHANGED"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check 2ea6a7ec bee658c5acc4dd860a382317c40ec4421587a13a",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":[]},
      "expected": {"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/278ebc9e/b0audit/harness:. TMPDIR=/tmp/278ebc9e/b0audit python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go tests.test_run_night.NightDriverTests.test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap tests.test_run_night.NightDriverTests.test_preflight_emits_json_without_running_or_creating_custody",
      "cwd": "/tmp/278ebc9e/b0audit/base_checkout",
      "observed": {"result":"fail","exit_code":1,"tail":["Ran 3 tests in 10.816s","FAILED (failures=3)"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/278ebc9e/b0audit/harness:. TMPDIR=/tmp/278ebc9e/b0audit python3 -B -m unittest tests.test_evidence_night.LifecycleCompositionTests.test_prepare_check_real_installer_fake_launchctl_verify_and_uninstall",
      "cwd": "/tmp/278ebc9e/b0audit/base_checkout",
      "observed": {"result":"fail","exit_code":1,"tail":["Ran 1 test in 19.842s","FAILED (errors=1)"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "All four V1 failures reproduce at exact base 2ea6a7ec: two driver_python mismatches, a Python executable-path assertion, and the journal_block 8-second watchdog. The watchdog also fails on isolated head replay. V1 is not green.",
      "needs": "Lead must resolve the baseline verification environment and rerun the final suite gate."
    }
  ]
}
```

## Findings

| ID | Severity | Witness and cure |
|---|---|---|
| F1 | **BLOCKER** | [Receipt re-read](/Users/edr/code/wt-278ebc9e-b0audit/scripts/run_night.py:1009) loses an already validated BOM/UTF-16 C5 receipt and skips idle cleanup repair. Reuse the validated receipt or parse bytes consistently. |
| F2 | **BLOCKER** | [Sealing](/Users/edr/code/wt-278ebc9e-b0audit/joulewise/evidence_night.py:249) still changes historical idle refusal texts; the source check also precedes `dirty clone`. Preserve existing validation order and texts. |
| F3 | should_fix | [Candidate lookup](/Users/edr/code/wt-278ebc9e-b0audit/joulewise/evidence_night.py:639) crashes on list/object kinds. Type-check before lookup and return the historical `Refused`. |
| F4 | should_fix | [_custody_row](/Users/edr/code/wt-278ebc9e-b0audit/scripts/run_night.py:1019) still accepts unauthenticated wrapper contents as dispatch identity. Require wrapper authentication or validated C5. |

These are surviving B0 defects. No additional defect unique to `7647bb2e..bee658c5` was established.

| Check | Verdict |
|---|---|
| A1 | **FAIL:** named witnesses are cured, but C1/C2 remain incomplete. C3–C6 pass. |
| A2 | **FAIL:** remaining authority gap F4; reporting parity probes pass. |
| A3 | **FAIL:** cleanup/refusal changes and untyped malformed-kind failures remain. |
| A4 | **PASS:** both tests green; expected bytes and complete test functions unchanged. |

Executed witness excerpts:

```text
w1 ambiguous: BYTE_IDENTICAL
w1 nonutf8: BYTE_IDENTICAL
w1 unknown: BYTE_IDENTICAL
w1 cal: BYTE_IDENTICAL

base intact candidate_state ACCEPTED
head intact candidate_state ACCEPTED
base clone_archived candidate_state ACCEPTED
head clone_archived candidate_state ACCEPTED
base chain_removed candidate_state ACCEPTED
head chain_removed candidate_state ACCEPTED
base chain_tampered candidate_state ACCEPTED
head chain_tampered candidate_state ACCEPTED

F1 missing_no_C5: ValueError night payload kind unavailable
F1 wrapper_vs_C5: ValueError night payload kind differs from authenticated receipt

M3 pre_fix: OK
AssertionError: True is not false
Ran 1 test in 9.804s
FAILED (failures=1)
```

Sol F2 returned `Refused sealed candidate failed plan` at both base and head. C5 matched at both:

```text
wrong_class GenerationRefusal evidence requires v2 DIAGNOSTIC_NO_PACK
malformed PlanError plan must be an object
```

M3’s failure is the expected mutant kill at `scan_complete`. Its comparison uses the pre-fix third-row test, which does not exist at base.

## Residual risk

The 603-test suite is **not green**; all four failures reproduce at base, as recorded in R1. The full repository discovery suite was not run. Temporary-file creation was redirected into the authorized scratch directory; the checkout remains unchanged and clean.