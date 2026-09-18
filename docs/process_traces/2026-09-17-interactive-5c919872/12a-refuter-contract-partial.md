```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Read-only contract review found one documentation defect; final test results and remaining verification were not collected before the immediate-report instruction.",
  "workspace": {
    "base_requested": "a2671902",
    "base_mode": "exact",
    "head_start": "a267190279afbb6660a5433f34a654ad36042eb5",
    "head_end": null,
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/contracts/night_quiet_admission.md",
        "line": 14,
        "summary": "The contract does not satisfy the required first-use glossary order.",
        "clause": "D7: \"Gloss every term at first use\"; review item 10 explicitly includes observer, bind window and sample interval.",
        "counterexample_command": "nl -ba docs/contracts/night_quiet_admission.md",
        "observed_output": "Line 14 uses \"including observer cost\" before observer is explained at lines 123–125. The policy example introduces bind_max_s and sample_interval_s at lines 57–58, and the following prose uses sample interval and bind allocation at lines 68–74; their definitions follow at lines 77–79.",
        "recommendation": "Move the observer and binding terminology definitions ahead of their first uses."
      }
    ],
    "clause_trace": [
      {
        "item": 1,
        "result": "Traced, no finding in inspected validation: exact seven-key policy, nonempty cutoff_authority, known policy only, finite numeric bounds, integer interval/count, bind capacity and total-window capacity. The computed 7980 s derivation minimum is enforced by generator build_spec and author_quiet_plan. Legacy dispatch changes are additive; evaluation was extracted into helpers."
      },
      {
        "item": 2,
        "result": "Traced, no finding in writer dispatch: quiet_admission must be explicitly present on NightPlan to emit v4; otherwise the added dataclass field is removed. New v4 authoring uses exclusive creation. Generator --check was not run, so byte-identical generated output is not independently verified."
      },
      {
        "item": 3,
        "result": "Traced, no semantic finding: bind deadline is min(t0+B,E-R), converted using the driver-entry wall/monotonic pair. Late entry consumes allowance. Existing completion, courier and dead-man derivations have no diff. Shutdown gains an explicit v4 monotonic argument anchored to driver entry; its E-plus-grace expression is preserved, although that call site is not textually unchanged."
      },
      {
        "item": 4,
        "result": "Traced static plan/window/age/head/chain/registration checks and dynamic census, screensaver, AC power, display parsing, thermal and boot/clock checks. CPU excess alone produces WAIT. V4 uses fresh dynamic census calls plus concurrent census supervision; the cached initial-census wrapper remains confined to the legacy branch. Exhaustive probe-error classification was not completed."
      },
      {
        "item": 5,
        "result": "Traced max(process_busy_cores,host_busy_cores), (pid,lstart) accounting, observer inclusion/labeling, second top sample, and diagnostic-only load handling. No name exemption appears in the inspected sampler. The requested repository-wide daemon-name grep remains unperformed."
      },
      {
        "item": 6,
        "result": "Traced, no finding in required receipt fields: literal false admission_is_capture_evidence, attribution or unavailable reason, journal digest/count and version dispatch. The receipt-contract diff contains exactly the two ruled sentences and their blank lines. Legacy byte-comparison regression was launched, but its completed result was not collected."
      },
      {
        "item": 7,
        "result": "Traced, no finding: bind_expired is in gate and driver registries, arm_retry.COLD_GATE_CODES and both generated policy copies. Legacy receipts explicitly exclude the new reason. Existing valid load/power/thermal refusals retain not_quiet."
      },
      {
        "item": 8,
        "result": "Traced, no finding in D-182 helper conditions: eligible terminal machine-state reason; matching plan identities; explicit no-start/no-reservation/no-session/no-writer/empty-inventory evidence; courier.sent and unused successor count; new id/digest; fresh notice; 60 s after terminal write; successor install close; inherited NO veto. Same-candidate history still requires identical digest. D-182 citations and ten-minute correction are present. Generated-copy byte equality was not independently verified."
      },
      {
        "item": 9,
        "result": "Inspected shared test policy uses busy_core_max=0.0 and TEST-ONLY-NOT-A-RULING; admitting values inspected are injected inside test methods. Documentation labels nonzero arithmetic examples as rejected calculations, not candidate cutoffs. Whole-diff numeric grep remains unperformed."
      },
      {
        "item": 10,
        "result": "F1. Otherwise traced the 480 s calculation, approximately 1 J/5 J bars, provisional status and ruling ownership. Timing example arithmetic is correct: 9600-187=9413 s; E=18:10, completion=18:15, dead-man=19:15."
      },
      {
        "item": 11,
        "result": "No measurement or claim constant change found in inspected implementation diffs. The pre-registration text was read, but a dedicated unchanged-file comparison and complete legacy-refusal verification remain outstanding; no final clean judgment is issued."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "a267190279afbb6660a5433f34a654ad36042eb5"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "a267190279afbb6660a5433f34a654ad36042eb5"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff a90ab4e8..a2671902 -- joulewise/night_gate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff a90ab4e8..a2671902 -- scripts/run_night.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_quiet_admission tests.test_night_gate tests.test_arm_retry",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V4 was launched and returned a running session, 97595. Progress included EEE, but no traceback, final count or exit status was collected. Its outcome is still pending in this report; not_run denotes unavailable completed verification, not that launch was skipped.",
      "needs": "Collect the pending test result and adjudicate any errors."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Immediate reporting interrupted verification. Generator --check, requested whole-diff greps, focused writer/generator/driver tests, exhaustive probe-error classification and final workspace check remain incomplete.",
      "needs": "Complete the enumerated checks before accepting a clean contract review."
    },
    {
      "id": "G3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Baseline file SHA-256 matched the supplied digest; initial worktree was clean at the requested detached HEAD. No files were modified, no live sampler or quiet-machine work was run, and no network or reverse consult was used.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — SHOULD-FIX:** [The admission contract](/Users/edr/code/JouleWise-wt-ref-contract/docs/contracts/night_quiet_admission.md:14) uses observer and binding terminology before defining it, contrary to the explicit first-use requirement.

## Residual risk

This is a partial review, not merge approval. The test command’s final result is still pending in this report. The lead should collect it and finish the checks listed in G2.