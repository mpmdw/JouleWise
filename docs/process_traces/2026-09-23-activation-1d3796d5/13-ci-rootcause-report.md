```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "partial",
  "summary": "The CI failure is most likely a test-fixture readiness race: the deadline can send SIGTERM before the grandchild installs its ignore disposition.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "probable",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_run_night.WindowDeadlineTests.test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.007s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B - <<'PY'\nimport os, signal, subprocess, time\nfor name, recipe, wait_ready in [\n    ('term_before_trap', '/bin/sleep 2; trap \"\" TERM; print -r -- READY; exec /bin/sleep 25', False),\n    ('term_after_trap', 'trap \"\" TERM; print -r -- READY; exec /bin/sleep 25', True),\n]:\n    p = subprocess.Popen(['/bin/zsh', '-c', recipe], start_new_session=True, stdout=subprocess.PIPE, text=True)\n    try:\n        if wait_ready:\n            print(name, 'ready=', p.stdout.readline().strip(), flush=True)\n        else:\n            time.sleep(.2)\n        os.killpg(p.pid, signal.SIGTERM)\n        time.sleep(.1)\n        print(name, 'poll_after_TERM=', p.poll(), flush=True)\n    finally:\n        try: os.killpg(p.pid, signal.SIGKILL)\n        except ProcessLookupError: pass\n        p.wait(timeout=2)\n        p.stdout.close()\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "term_before_trap poll_after_TERM= -15",
          "term_after_trap ready= READY",
          "term_after_trap poll_after_TERM= None"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "term_after_trap poll_after_TERM= None"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 -B - <<'PY'\nimport importlib.util, signal\nfrom pathlib import Path\nfrom unittest import mock\nspec=importlib.util.spec_from_file_location('run_night_probe', Path('scripts/run_night.py'))\ndriver=importlib.util.module_from_spec(spec); spec.loader.exec_module(driver)\nclass Reaped:\n    pid=123456\n    def wait(self, timeout): return -signal.SIGTERM\nsent=[]\nanswers=[(False,['group member still visible'])]*19+[(True,[])]\nwith mock.patch.object(driver,'_signal_group',side_effect=lambda pgid,n:sent.append(n)), mock.patch.object(driver,'_group_census',side_effect=answers), mock.patch.object(driver,'GROUP_CENSUS_INTERVAL_S',0):\n    proven=driver._terminate_process_group(Reaped())\nprint('proven=',proven,'TERM_count=',sent.count(signal.SIGTERM),'KILL_count=',sent.count(signal.SIGKILL))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "proven= True TERM_count= 21 KILL_count= 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "proven= True TERM_count= 21 KILL_count= 0"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest $(head -n 33 /Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/11-ci-shard1-failing-module-order.txt) tests.test_run_night.WindowDeadlineTests.test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven > /tmp/joulewise-ci-shard1-prefix-target.log 2>&1; rc=$?; tail -n 35 /tmp/joulewise-ci-shard1-prefix-target.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The exact Ubuntu failure did not record whether the grandchild installed its trap or remained in the chain's process group. This Mac sandbox cannot run the named test because /usr/bin/pgrep cannot obtain a process list. The prefix replay was interrupted during an expensive test_p2038_production_path calculation before reaching the target.",
      "needs": "Land the proposed readiness check, then run the named test and failing shard on Ubuntu for Python 3.11 and 3.13; inspect the ready marker and group assertion if either fails."
    }
  ]
}
```

## Causal chain

The [test fixture](/Users/edr/code/wt-1d3796d5-consult/tests/test_run_night.py:3849) starts the grandchild in the background and immediately runs the night driver. Its two-second scaled deadline can fire before that grandchild executes `trap "" TERM`. The executed signal probe above shows the consequence: TERM before the trap exits with `-15`; TERM after readiness leaves the process running. On Linux, an ignored signal disposition also survives `execve`, so the later `exec /bin/sleep` is sound once the trap is installed. [Linux signal manual](https://man7.org/linux/man-pages/man7/signal.7.html)

The [termination path](/Users/edr/code/wt-1d3796d5-consult/scripts/run_night.py:445) repeats SIGTERM while censusing for five seconds and sends SIGKILL only if the group has not been proved absent. Executing that function with a census that becomes empty on its twentieth observation produced **21 TERMs, zero KILLs, and `proven=True`**, matching the CI signature. This supports a fixture race, though the missing CI readiness observation keeps the attribution *probable*.

## Remediation

Proposed **test-side** change: establish the trap before starting the test’s deadline, and check that the grandchild belongs to the group being tested. This preserves the SIGKILL assertion.

```diff
diff --git a/tests/test_run_night.py b/tests/test_run_night.py
@@
     def test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven(self) -> None:
         grandchild = self.root / "grandchild.pid"
+        ready = self.root / "grandchild.ready"
         self._arm(
-            "/bin/zsh -c 'trap \"\" TERM; exec /bin/sleep 25' &\n"
+            f"/bin/zsh -c 'trap \"\" TERM; : > {ready}; exec /bin/sleep 25' &\n"
             f"echo $! > {grandchild}\n/bin/sleep 20\n")
+        complete_start = self.driver._complete_chain_start
+
+        def complete_after_ready(descriptor, process, night_dir):
+            pgid = complete_start(descriptor, process, night_dir)
+            self._await(ready, timeout_s=10)
+            self._await(grandchild, timeout_s=10)
+            self.assertEqual(pgid, os.getpgid(int(grandchild.read_text().strip())))
+            return pgid
+
         sent, patch = self._signal_spy()
-        with patch:
+        with mock.patch.object(self.driver, "_complete_chain_start",
+                               side_effect=complete_after_ready), patch:
             exit_code = self.driver.run_night(self.plan_path)
```

Run the named test on both Ubuntu Python versions, then rerun the failing shard with its recorded module order under normal CI load. The test should reach its ready marker, confirm group membership, observe SIGKILL, and prove the grandchild gone. No repository file was changed in this session.

## Disproved alternatives

- **Missing `/bin/zsh`:** the [CI job](/Users/edr/code/wt-1d3796d5-consult/.github/workflows/ci.yml:161) installs it when needed and checks `test -x /bin/zsh` before running tests.
- **PR #394’s new gate branch:** the fixture is classified as `calibration`, so its new `quiet_predicate_evidence` corecaptured branch is not reached.
- **Failure to escalate while a member remains:** a separate executed census probe that kept reporting a survivor sent SIGKILL. The observed no-KILL path requires the census to report absence.

## Residual risk

The shard runner executes modules in one interpreter, but the local prefix replay did not reach the target; a leaked state or Linux-specific group-membership issue is therefore not fully excluded. The proposed group assertion makes the latter visible on CI. There is **no evidence of a new defect in real Mac night termination**: the driver escalates when its census continues to find the group; this failure concerns whether the test created the promised TERM-ignoring member before the deadline.