```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 11 items traced: one blocker changes the v2 rerun guard; two should-fix findings concern boot-probe classification and first-use definitions.",
  "workspace": {
    "base_requested": "a2671902",
    "base_mode": "exact",
    "head_start": "a267190279afbb6660a5433f34a654ad36042eb5",
    "head_end": "a267190279afbb6660a5433f34a654ad36042eb5",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F3",
        "severity": "blocker",
        "file": "scripts/run_night.py",
        "line": 126,
        "summary": "The v4 journal becomes a rerun blocker for existing v2 plans.",
        "clause": "Seat brief, standing pre-registration ruling: existing v2 plans keep \"their exact current one-shot admission semantics\".",
        "counterexample_input": "Valid v2 make_plan(), quiet_admission=None; mock filesystem existence so quiet_samples.jsonl is the only existing night artifact. Compare the base/head _WRITE_ONCE_RECORDS and _existing_record, then invoke the head run_night with injected probes and mocked artifact writes.",
        "observed_output": "Base guard: None. Head guard: /fixture-v2/night/quiet_samples.jsonl. Head driver: v2 quiet_admission None exit 3 rerun_refusal quiet_samples.jsonl.",
        "impact": "The shared guard now refuses this v2 invocation before its legacy evaluator runs. The added journal entry is unconditional.",
        "recommendation": "Apply the quiet_samples.jsonl rerun guard only to v4 plans, preserving the legacy record set."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/night_gate.py",
        "line": 1392,
        "summary": "V4 hard checks misclassify a failed boot-identity command as a boot-clock predicate refusal.",
        "clause": "D3: \"A probe error during binding is recorded on the sample and is terminal (`night_probe_error`), never silently \\\"quiet\\\".\"",
        "counterexample_input": "Build a v4 plan from make_plan(window_max_s=9600, quiet_admission=POLICY), obtain its static receipt with FakeProbeSource, then inject BOOT_SESSION_ARGV ProbeResult(exit_code=2, stdout='', stderr='fixture probe failure') and call evaluate_dynamic_hard.",
        "observed_output": "/usr/sbin/sysctl -n kern.bootsessionuuid => night_refused_boot_clock 'kern.bootsessionuuid is not a canonical UUID'",
        "impact": "The new v4 caller inherits the legacy clock check's command-failure classification. It remains terminal, but uses the wrong required reason; the other five injected failed hard probes returned night_probe_error.",
        "recommendation": "Distinguish failed boot observations in the v4 path while preserving legacy v2 handling."
      },
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/contracts/night_quiet_admission.md",
        "line": 14,
        "summary": "Required terminology is used before its first-use definition.",
        "clause": "D7: \"Gloss every term at first use\"; review item 10 explicitly includes observer, bind window, sample interval and consecutive quiet samples.",
        "counterexample_command": "nl -ba docs/contracts/night_quiet_admission.md",
        "observed_output": "observer cost appears at 14, but observer is defined at 124; sample_interval_s appears at 58 and sample interval at 68, before its definition at 78–79; consecutive_quiet_samples appears at 59 before its definition at 82–83; bind_max_s appears at 57 and bind allocation at 73, before bind window is defined at 77. GO appears at 9 before permission to start at 153; t0 appears at 50 before scheduled start at 184.",
        "recommendation": "Move the relevant definitions before these first uses. cutoff_authority is already explained when introduced at 17–18."
      }
    ],
    "clause_trace": [
      {
        "item": 1,
        "result": "traced, no finding in plan validation: exact seven policy keys; nonempty authority; known policy only; finite positive durations/count, nonnegative cutoff sentinel, integer-valued positive interval, integer count >=1, bind >= interval*count and window >= bind+runway. Generator derives the 7980 s minimum from constants. No environment override. Legacy parser branches remain equivalent; driver compatibility finding F3 is separate."
      },
      {
        "item": 2,
        "result": "traced, no finding: writer emits v4 only with explicit NightPlan.quiet_admission; otherwise removes the added dataclass field. Explicit generator authoring exclusively creates a new id/output. V2 fixture bytes and one-shot semantics tests pass; generator --check passes."
      },
      {
        "item": 3,
        "result": "traced, no finding: min(t0+B,E-R) converts once using driver-entry clocks; late starts consume B. Completion, dead-man, install-close and chain-environment functions are AST-identical. Existing E-based expressions remain unchanged. The added v4 shutdown argument anchors the same E+300 trigger to entry monotonic time, independent of GO."
      },
      {
        "item": 4,
        "result": "traced, finding F2. Static plan/window/age/head/chain/registration failures are terminal. Dynamic census hits, nonzero screensaver configuration, AC loss, thermal restriction, boot changes and clock rollback are terminal; malformed required observations are terminal. Display configuration is parsed without a new threshold; absent thermal-limit lines still pass. CPU excess alone yields WAIT. Census is fresh before/after intervals and before GO, with concurrent 30 s supervision; initial-census replay remains legacy-only."
      },
      {
        "item": 5,
        "result": "traced, no finding: busy=max(process,host), identity=(pid,lstart), union accounting and unaccounted exits, observer included/labeled without subtraction, second top sample only. Whole-diff grep found no added production daemon references or name exemptions. Load values/errors are diagnostic only."
      },
      {
        "item": 6,
        "result": "traced, no finding: v3 requires policy, deadlines/GO fields, sample counts, journal digest/count, attribution or unavailable reason, load diagnostic and literal admission_is_capture_evidence=false. Versioned validation preserves legacy reason membership and receipt shape. Base/head receipt-byte regression passes. Pack receipt contract contains exactly the two verbatim ruled insertions, with no removals or other additions."
      },
      {
        "item": 7,
        "result": "traced, no finding: bind_expired is registered in gate/driver registries, arm_retry, generated policy copies and handback table. Legacy receipt validation excludes it. Valid v2 load and non-CPU power/thermal failures retain not_quiet; bind expiry uses the distinct code."
      },
      {
        "item": 8,
        "result": "traced, no finding: D-182 route checks matching terminal machine-state refusal, explicit no-start/no-reservation/no-session/no-writer/empty-inventory evidence, courier.sent, unused successor count, new id/digest, fresh notice, >=60 s after terminal write, successor install close and inherited NO veto. retry_allowed/classify_abort are AST-identical. Changed digest is rejected in same-candidate history. Both generated copies equal render_policy; D-182/R1 and ten-minute corrections are present."
      },
      {
        "item": 9,
        "result": "traced, no finding: whole-diff grep with AST test-body exclusion found only numeric busy_core_max=0.0 outside test bodies, in the contract example and shared test policy; both carry TEST-ONLY-NOT-A-RULING. Nonzero GO thresholds are injected inside tests. Document arithmetic examples are explicitly rejected calculations, as fix item 1 requires."
      },
      {
        "item": 10,
        "result": "traced, finding F1. Otherwise the document builds accounting, supervision, journal/receipt and successor mechanisms. It uses 480 s, approximately 1 J/5 J bars, identifies provisional parameters and ruling ownership, and computes timing correctly: 9600-187=9413 s; E=18:10, completion=18:15, dead-man=19:15."
      },
      {
        "item": 11,
        "result": "traced, findings F3 and F2. No measurement/instrument/claim constant changed: existing module-constant changes are confined to reason registries, retry descriptions and the journal record guard. Pre-registration and chain files have no diff. Pinned receipt-contract changes are exactly the ruled exception."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "set -o pipefail; TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 313 tests in 2.739s", "", "FAILED (errors=194, skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_quiet_admission tests.test_night_gate.QuietGatePhaseTests tests.test_arm_retry.ZeroCaptureSuccessorTests tests.test_arm_retry.ArmRetryTests.test_both_document_blocks_are_exact tests.test_arm_retry.ArmRetryTests.test_every_cold_assignment_is_explicit",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 18 tests in 0.084s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_plan_writer.QuietPlanVersionTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.007s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated derivation-night wrapper region matches"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet a90ab4e8..a2671902 -- configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "blocking",
      "text": "The earlier test session was gone; the full six-module rerun completed. Diagnostic collection classified all 194 errors: 183 FileNotFoundError for no usable temporary directory and 11 PermissionError creating /tmp directories; zero assertion failures, nine skips. This is not a green suite.",
      "needs": "Lead must rerun the six-module suite where temporary fixture writes are permitted."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live sampler or hardware validation was performed. Baseline digest matched; final HEAD and clean worktree were unchanged. No writes, network, reverse consult, arming or quiet-machine work.",
      "needs": ""
    }
  ]
}
```