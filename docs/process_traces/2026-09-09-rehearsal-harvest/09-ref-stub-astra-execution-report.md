```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No cure defect found; counterfactual confirmed, but file-backed suite verification is blocked by the read-only environment.",
  "workspace": {
    "base_requested": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "base_mode": "exact",
    "head_start": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "head_end": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 135 tests in 1.434s", "", "FAILED (errors=85)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 135 tests.*\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate.NightGateTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 52 tests in 0.574s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 52 tests.*\\s+OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff -w 83ab38ed..bb7090e2b8d4cfe30effbfb7e89cef802277d448 -- joulewise/night_gate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "+    else:",
          "         # The chain and sidecar are read as text by the injected adapter; UTF-8 is",
          "         # the ruled byte representation for hashing text observations.",
          "         try:"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "try:"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import subprocess, types, sys, unittest, io\nfrom pathlib import Path\nimport tests.test_night_gate as tests\nbase = subprocess.check_output([\"git\",\"show\",\"83ab38ed:joulewise/night_gate.py\"], text=True)\nhead = Path(\"joulewise/night_gate.py\").read_text()\nstart = \"# The chain and sidecar are read as text\"\nend = \"    rows[\\\"C5\\\"].status = \\\"PASS\\\"\"\nb = base[base.index(\"    \"+start):base.index(end, base.index(start))]\nh = head[head.index(\"        \"+start):head.index(end, head.index(start))]\nassert b == \"\".join(line[4:] if line.startswith(\"    \") else line for line in h.splitlines(keepends=True))\nprint(\"Non-stub block byte-identical after removing four-space indentation; zero tokens changed\")\nm = types.ModuleType(\"joulewise.ng_base_review\"); m.__package__=\"joulewise\"; sys.modules[m.__name__]=m\nexec(compile(base, \"83ab38ed:joulewise/night_gate.py\", \"exec\"), m.__dict__)\ntests.night_gate=m\nfor name in [\"test_rehearsal_stub_does_not_read_missing_chain_or_sidecar\",\"test_diagnostic_still_refuses_missing_chain_or_sidecar\"]:\n    log=io.StringIO(); result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.TestSuite([tests.NightGateTests(name)]))\n    print(log.getvalue()); print(\"rc=\"+str(0 if result.wasSuccessful() else 1))\n    assert result.wasSuccessful() == name.startswith(\"test_diagnostic\")\nprint(\"Counterfactual expectations PASS\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK", "", "rc=0", "Counterfactual expectations PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Counterfactual expectations PASS"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import io, unittest\nnames=[\"tests.test_night_plan_writer\",\"tests.test_install_night_agent\",\"tests.test_preflight\",\"tests.test_t0_rehearsal\",\"tests.test_arm_readiness_schemas\"]\nfor name in names:\n    log=io.StringIO()\n    r=unittest.TextTestRunner(stream=log).run(unittest.defaultTestLoader.loadTestsFromName(name))\n    print(name)\n    print(\"\\n\".join(log.getvalue().splitlines()[-4:]))\n    print(\"rc=\"+str(0 if r.wasSuccessful() else 1))\n    if r.errors: print(\"first_error=\"+r.errors[0][1].splitlines()[-1])'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "tests.test_arm_readiness_schemas",
          "----------------------------------------------------------------------",
          "Ran 50 tests in 0.100s",
          "",
          "FAILED (errors=6)",
          "rc=1",
          "first_error=FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-stub-astra']"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK\\s+rc=0"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check 83ab38ed..bb7090e2b8d4cfe30effbfb7e89cef802277d448",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The filesystem is read-only, including temporary directories. File-backed tests fail during fixture creation. Logs were captured in tool output or StringIO; a persistent log could not be written. No approval or sandbox bypass was attempted.",
      "needs": "Lead rerun V1 and the V5 modules with writable temporary storage, retaining logs and actual test return codes."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Review checkout is clean and detached at the exact requested head. Brief and seat report were absent here and read from /Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/.",
      "needs": ""
    }
  ]
}
```

## Findings

No blocker, should-fix, or nit identified in the cure. Execution acceptance remains incomplete because of F1.

Checks passed:

1. **Non-stub preservation.** `git diff -w` shows only the stub branch insertion. An independent string comparison confirmed the original block is byte-identical after removing four added indentation spaces: **zero tokens changed**. The unconditional reads remain at `joulewise/night_gate.py:1055–1056`; all sidecar checks remain at lines 1075–1106.

2. **Receipt compatibility.** `validate_receipt` at `joulewise/night_gate.py:1416` checks:
   > `if not isinstance(item.get("measured"), Mapping):`

   It does not constrain measured keys or their value types. The new stub test at `tests/test_night_gate.py:431` passes, including JSON round-trip validation, null digests, substitution marker, PASS status, and null basis.

   Downstream inspection found:
   - `scripts/run_night.py:510` hashes artifacts; line 576 copies them into night-results without parsing measured fields.
   - `scripts/run_night.py:1208` reads **C4** boot identity; line 1228 copies measured mappings for pack GO receipts.
   - `joulewise/arm_readiness.py:2850` likewise requires only a measured mapping in its separate pack GO parser.
   - `docs/process/NIGHT_COURIER_PROMPT.md:10` directs receipt reading and reporting verdict/refusal information, without imposing C5 digest types.

3. **No residual stub chain reader found.**
   - `scripts/install_night_agent.sh:45–98`: parses the plan and checks checkout pins; does not read either chain file.
   - `joulewise/night_plan_writer.py:32`: validates through `NightPlan.from_mapping`; `joulewise/night_gate.py:290–291` requires chain-path text, not readable files.
   - `docs/process_traces/2026-08-28-live-smoke/preflight.sh:39–69`: checks schema, checkout pin, and interpreter; no plan-chain reader. The built-in stub does not invoke this preflight.
   - `scripts/run_night.py:1572–1575`: substitutes `/dev/null` and `"sleep 2; echo REHEARSAL"`; filesystem chain checks are confined to its `else`.
   - `joulewise/night_gate.py:776–777`: additional chain reads belong to pack evaluation, dispatched only for `TRANSACTION_PACK` at line 1124.
   - `docs/process/NIGHT_HANDBACK.md:57` explicitly describes the built-in stub. Standing rules at line 113 onward require writer/schema/pins, not stub chain files.

4. **Logging.** `scripts/run_night.py:1518–1523` retains exactly `night gate verdict=<verdict>` for non-refused receipts. Refused details use:
   > `" ".join(str(refusal.get("detail", "")).splitlines())[:200]`

   `_refusal_from_object` is defined at line 168, before use. Independent in-memory execution of the unchanged production logging statements passed GO, REHEARSAL_ONLY, and multiline REFUSED cases.

   New driver tests at `tests/test_run_night.py:292`, `:313`, and `:321` call the real driver through `_run_night` at line 262 and inspect the actual log file. They do not mock the modified logging statements. Their execution here was blocked during temporary fixture creation.

5. **Counterfactual independently confirmed.** Loaded baseline gate code into an alternate in-memory module and ran the current two tests against it:
   > `AssertionError: 'REHEARSAL_ONLY' != 'REFUSED'`  
   > `Refusal(reason='night_probe_error', detail="FileNotFoundError: [Errno 2] No such file or directory: '/custody/chain.zsh'"`

   Stub test: `FAILED (failures=1)`, rc 1. Diagnostic test: `OK`, rc 0. Counterfactual harness: rc 0.

6. **Exit-code observation, without judgment.** `scripts/run_night.py:1672–1675` explicitly pairs:
   > `verdict = "REHEARSAL_ONLY"`  
   > `base_exit_code = EXIT_REFUSED`

   This predates the cure. Existing `test_rehearsal_census_hits_are_observed_without_killing_the_stub` at `tests/test_run_night.py:1112` asserts EXIT_REFUSED and result verdict REHEARSAL_ONLY at lines 1125–1126; the same assertions occur on `83ab38ed` at lines 1080–1081. That existing case has an agent-refused gate receipt; the newly added test pins the green REHEARSAL_ONLY receipt case.

Additional attempted module tails, each test rc 1:

| Module | Tail |
|---|---|
| `test_night_plan_writer` | `Ran 8 tests` / `FAILED (errors=8)` |
| `test_install_night_agent` | `Ran 13 tests` / `FAILED (errors=13)` |
| `test_preflight` | `Ran 9 tests` / `FAILED (errors=9)` |
| `test_t0_rehearsal` | `Ran 32 tests` / `FAILED (errors=35)` |
| `test_arm_readiness_schemas` | `Ran 50 tests` / `FAILED (errors=6)` |

The capture harness itself returned 0; this is **not** a suite pass. First errors reported unavailable temporary storage.

## Residual risk

No live stub arm, launchd execution, courier delivery, or results publication was performed. Next step: lead reruns the blocked file-backed modules with writable temporary storage and retains their logs before final verification.