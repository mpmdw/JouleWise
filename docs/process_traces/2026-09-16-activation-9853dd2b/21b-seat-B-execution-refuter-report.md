```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Three blockers and one should-fix reproduced; four mutants killed; real census verification remains environment-blocked.",
  "workspace": {
    "base_requested": "d1aadecccb397cdd5040cb252908c80290177def",
    "base_mode": "exact",
    "head_start": "d1aadecccb397cdd5040cb252908c80290177def",
    "head_end": "d1aadecccb397cdd5040cb252908c80290177def",
    "upstream_end": "68fa9a9cf89c88e64588f8d3d7eee7508158b45e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "joulewise/night_agent_install.py:689",
        "title": "Receipt admission does not bind reservation input-file contents",
        "clause": "“a changed interpreter or input invalidates it”",
        "counterexample": "V4 input_binding: create a matching receipt, then independently replace identity.json, t1.json, or frozen-plan.json with {\"changed_after_probe\":true}; invoke the real installer through fake launchctl.",
        "observed": "Each installation exited 0 with empty stderr and bootstrapped both night jobs. The bindings cover wrapper/code/ledger bytes but omit these reservation inputs."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "joulewise/night_agent_install.py:719",
        "title": "The explicitly requested mtime-stale receipt is admitted",
        "clause": "“stale (mtime older than the bound) ... → exit 2 naming the field”",
        "counterexample": "V2 admission-stale_mtime: os.utime(receipt, (time.time()-21601,)*2), retaining fresh JSON timestamps, then invoke the real installer.",
        "observed": "Exit 0, empty stderr, both night jobs bootstrapped. By contrast, finished_epoch_s older than 21600 seconds correctly exited 2: probe receipt finished_epoch_s stale or invalid (maximum age 21600 s)."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "file": "scripts/run_night.py:1825",
        "title": "A calibration document changes the established census-abort result",
        "clause": "“No change to gate or census semantics.”",
        "counterexample": "V5/V6: reservation writes a valid refusal document, then remains alive; the fake census reports '20 claude', causing the real driver to SIGTERM the chain. Repeat without the document and against base 3015cb39.",
        "observed": "Head with document: exit 3, REFUSED, aborted_reason=night_calibration_refused. Head without document and base with/without document: exit 4, ABORTED, aborted_reason=night_aborted_agent_present. All chain_exit_code values were -15. Both causes remain in separate head refusal files, but the existing result/exit semantics changed."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "scripts/run_night.py:2045",
        "title": "Direct probe timeout excludes synchronous binding reads",
        "clause": "“outcome: timeout within --timeout-s”",
        "counterexample": "V4 fifo: replace the fixture ledger with a FIFO having no writer, then run the real probe with --timeout-s 0.3.",
        "observed": "Still blocked after 7.005 seconds; no receipt and reservation never started. The harness killed the driver, exit -9. probe_bindings reads the ledger at night_agent_install.py:681 before the timed communicate call. The temporary LaunchAgent wrapper supplies a separate outer bound, limiting severity."
      }
    ],
    "coverage": {
      "a": "285 focused tests completed: OK (skipped=3). All three skipped bodies were subsequently forced to run and failed because process census is unavailable.",
      "b": "Real driver main(['run',...]) and real chain exercised valid, mismatched, and absent documents. Valid: REFUSED, night_calibration_refused, chain_exit_code=2, exact calibration_ledger_custody_timeout code and 14-key evidence, document inventoried. Mismatch: document_invalid. No document: GO and driver exit 5. A separate real courier runner launched a local executable stub, created courier.sent, and copied result/refusal records into the fixture results directory; two Git publication calls were faked.",
      "c": "Real chain verify-only returned 0 with its JSON receipt and 2 for refusal. Budget 0.75 and window-end-minus-10 deadline reached the reservation. No capture sentinel, chain.started, or operator-log directory.",
      "d": "All requested receipt fields appeared. With unavailable pgrep, success/refused/hung cases conservatively returned exit 2, outcome=refused, refusal_code=probe_process_survived. Hung case completed in 5.994 seconds with timeout 0.3 plus cleanup; both recorded child PIDs were absent via kill(pid,0). Successful production census behavior is unverified.",
      "e": "Missing receipt, stale JSON timestamp, non-ok outcome, changed driver sha, chain sha, code_digests, and ledger head each refused with exit 2 naming the field. Matching receipt installed. Fake launchctl showed probe bootstrap, probe bootout, absence query, then production bootstraps. That cleanup census was mocked. Mtime-only staleness failed as F2.",
      "f": "Two-writer regression passed. Three writers produced refusal.json, refusal-01.json, refusal-02.json with intact causes and all paths inventoried. Existing sequence files were preserved and skipped; the suite explicitly covers pre-existing refusal-01.json.",
      "g": "Four one-line mutants killed: removed plan-id check; replaced exclusive allocation with overwrite; omitted verified_bootout; ignored chain_python comparison.",
      "h": "zsh syntax passed. Real render-only with a v2 fixture exited 0 and made zero launchctl calls.",
      "provenance": "Fixtures only; no hardware validation, network, real launchctl, commits, or original-worktree edits."
    },
    "probe_plist_ProgramArguments": [
      "/opt/homebrew/opt/python@3.14/bin/python3.14",
      "/private/tmp/refute-B-exec/scripts/run_night.py",
      "probe",
      "--plan",
      "/private/tmp/tmpl2oqg4rl/custody/night_plan.json",
      "--receipt",
      "/private/tmp/tmpl2oqg4rl/custody/night_probe_receipt.pending.json",
      "--timeout-s",
      "600"
    ],
    "mutation_outputs": {
      "plan_id": "AssertionError: 'document_invalid' != 'calibration_ledger_custody_timeout'",
      "overwrite": "FileNotFoundError for night/refusal-01.json",
      "bootout": "AssertionError: 'bootout gui/501/com.joulewise.night-probe.probe-fixture' not found",
      "chain_python": "field='chain_python': AssertionError: 2 != 0"
    },
    "evidence": "Replay scripts remain in /tmp/refute-B-exec/. Full outputs are /tmp/refute-B-exec-{suite,probes,courier,extra,census,census-base,mutations,unskipped-replay}.log; mutant copies and individual logs also remain under /tmp."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v tests.test_run_night tests.test_night_gate tests.test_night_agent_install tests.test_install_night_agent > /tmp/refute-B-exec-suite.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 285 tests in 1057.336s", "", "OK (skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_exec.py transport chain probe admission collision render > /tmp/refute-B-exec-probes.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "fail", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_courier.py > /tmp/refute-B-exec-courier.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_extra.py launchd input_binding fifo > /tmp/refute-B-exec-extra.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "fail", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_census.py > /tmp/refute-B-exec-census.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "fail", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_census_base.py > /tmp/refute-B-exec-census-base.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_mutations.py > /tmp/refute-B-exec-mutations.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B refute_unskipped.py > /tmp/refute-B-exec-unskipped-replay.log 2>&1",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 3 tests in 17.858s", "", "FAILED (failures=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "lint",
      "cmd": "zsh -n scripts/night_chains/calibration_derivation_only.zsh",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": "/tmp/refute-B-exec",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "^\\[\\]$"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "blocking",
      "text": "/usr/bin/pgrep -lf -g 999999 . exited 3: sysmond service not found; Cannot get process list. The three probe tests skipped normally and failed when forced to run. The final orphan census also could not acquire ps data. No census-capable execution was claimed.",
      "needs": "Lead: adjudicate F1-F4 and rerun the three NightProbeTests plus orphan census on a census-capable runner before acceptance."
    }
  ]
}
```