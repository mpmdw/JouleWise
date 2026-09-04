```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 10 cures M-A, M-C, H-2, and S-A, but the documented reaper cannot call setsid under interactive-zsh job control and step 0 cannot match two post-fix docs to the packet-21 exhibits.",
  "workspace": {
    "base_requested": "80741aad80618b96181265f7b75615d11cf5e782",
    "base_mode": "descendant",
    "head_start": "9b1424f5b4a895cfbb9d9353c4d336e679d5dd1b",
    "head_end": "9b1424f5b4a895cfbb9d9353c4d336e679d5dd1b",
    "upstream_end": "9b1424f5b4a895cfbb9d9353c4d336e679d5dd1b",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/28-delta-reaudit-round-10.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "line": "BLOCKED",
    "clauses": {
      "M-A": "CURED",
      "M-B": "NOT_CURED",
      "M-C": "CURED",
      "H-2": "CURED",
      "B-A": "NOT_CURED",
      "S-A/24a": "CURED",
      "D-172": "COMPLIANT_VACUOUS_NO_GOVERNED_CHANGED_LINES"
    },
    "same_signature": "YES: the permitted suite and source-extraction assertions are green while two unexecuted production checklist paths fail; the interactive-zsh reaper exits before its receipt and the literal packet-exhibit hash gate rejects two files changed by round 10 itself.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The background reaper is already a process-group leader, so os.setsid() exits EPERM before the kill ladder",
        "paths": ["docs/process/MAGISTRATE_WATCHDOG.md", "tests/test_magistrate_watchdog.py"]
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Step 0 requires byte identity to pre-round-10 packet exhibits for two files round 10 changed",
        "paths": ["docs/process/MAGISTRATE_WATCHDOG.md", "docs/process/NIGHT_HANDBACK.md", "tests/test_magistrate_watchdog.py"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog tests.test_night_gate tests.test_run_night tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 187 tests in 31.810s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 187 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli.MagistrateWatchdogCliTests.test_real_cli_consumes_production_plan_set_and_fails_closed tests.test_run_night.NightDriverTests.test_courier_body_reads_watchdog_age_and_last_decision_directly",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.720s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport tempfile,unittest\nfrom pathlib import Path\nfrom unittest import mock\nimport tests.test_install_magistrate_watchdog as i\nfrom tests.test_magistrate_watchdog import ContractTests\ns=i.SCRIPT_PATH.read_text(); n='    else\\n      rm -f \"$plist\"\\n    fi'; assert s.count(n)==1\nwith tempfile.TemporaryDirectory() as d:\n p=Path(d)/i.SCRIPT_PATH.name; p.write_text(s.replace(n,'    else\\n      : # M8\\n    fi')); p.chmod(0o755)\n with mock.patch.object(i,'SCRIPT_PATH',p): r=unittest.TextTestRunner().run(unittest.TestSuite([ContractTests('test_mutation_m8_failed_lock_seed_removes_new_plist')]))\nassert len(r.failures)==1 and not r.errors\nprint('M8 KILLED')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["AssertionError: True is not false : M8 survived: a failed first install left its new plist behind", "FAILED (failures=1)", "M8 KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "M8 survived[\\s\\S]*FAILED \\(failures=1\\)[\\s\\S]*M8 KILLED"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/bin/zsh -ic 'f=\"$(mktemp \"/tmp/setsid-control.XXXXXX\")\"; /usr/bin/nohup /usr/bin/python3 -c '\"'\"'import json,os; print(json.dumps({\"pid\":os.getpid(),\"pgrp\":os.getpgrp(),\"sid\":os.getsid(0)}),flush=True); os.setsid()'\"'\"' > \"$f\" 2>&1 & p=$!; wait \"$p\"; r=$?; /bin/cat \"$f\"; print \"child=$p rc=$r\"; exit \"$r\"'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["{\"pid\": 52524, \"pgrp\": 52524, \"sid\": 52519}", "PermissionError: [Errno 1] Operation not permitted", "child=52524 rc=1"]},
      "expected": {"exit_code": 0, "tail_regex": "pid.*pgrp.*sid[\\s\\S]*rc=0"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git show origin/feat/2026-09-04-packet-21:docs/process_traces/2026-09-02-hands-free-week/21-coldgate-packet-watchdog-v3.md | sed -n '153,156p'; shasum -a 256 scripts/magistrate_watchdog.py scripts/install_magistrate_watchdog.sh docs/process/MAGISTRATE_WATCHDOG.md docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/NIGHT_HANDBACK.md",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["8bae0beae9765f87f9df0f97b44200595d97bcdf23bc9e3f9c385d2e78c8b3aa  docs/process/MAGISTRATE_WATCHDOG.md", "ac51fd0832eb3a2c6772a66bb569a4b4045b390e5e339223b3df000cc914fb26  docs/process/MAGISTRATE_RELAUNCH_PROMPT.md", "78a7f943c2cfd2d7446ecd5c59b055627514dddc93938b8c455c1060a4a496e9  docs/process/NIGHT_HANDBACK.md"]},
      "expected": {"exit_code": 0, "tail_regex": "854cb273.*21-exhibits/MAGISTRATE_WATCHDOG.md[\\s\\S]*3af163be.*21-exhibits/NIGHT_HANDBACK.md[\\s\\S]*854cb273.*docs/process/MAGISTRATE_WATCHDOG.md[\\s\\S]*3af163be.*docs/process/NIGHT_HANDBACK.md"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --name-only HEAD^..HEAD -- scripts/magistrate_watchdog.py scripts/install_magistrate_watchdog.sh 'configs/launchd/*.template'; git diff -U0 HEAD^..HEAD -- scripts/magistrate_watchdog.py | rg 'SESSION_ARGV_AFTER_PROMPT' || true; git diff --check HEAD^..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No LaunchAgent was installed or loaded, no production custody was accessed, and no production process was signalled; all execution used temporary custody/shadows and a PTY interactive-zsh probe.",
      "needs": "After both blockers are cured, the lead still owns the installed handoff and launchd activation gates."
    }
  ]
}
```

## Findings

F1 — blocker — The exact heredoc bytes at `docs/process/MAGISTRATE_WATCHDOG.md:134-222` succeed only in the test's non-job-control `subprocess.run` launch (`tests/test_magistrate_watchdog.py:1460-1472`). Under the documented Terminal-hosted interactive-zsh `nohup ... &` command, zsh makes the Python job its process-group leader (`pid == pgrp`); POSIX forbids a process-group leader from calling `setsid()`. The exact snippet exited 1 at line 2 with `PermissionError: [Errno 1] Operation not permitted`, before any signal or receipt. The handoff therefore cannot complete. Cure with a launch shape that forks before `setsid()` (or an equivalent proven mechanism) and execute the whole documented shell command under PTY job control in the test.

F2 — blocker — Step 0 (`docs/process/MAGISTRATE_WATCHDOG.md:92`) says to stop unless all five final files equal their packet exhibits. Packet 21 pins `MAGISTRATE_WATCHDOG.md` to `854cb273...` and `NIGHT_HANDBACK.md` to `3af163be...`; round 10 necessarily changed them to `8bae0bea...` and `78a7f943...`. The other three match. The string/order assertion at `tests/test_magistrate_watchdog.py:1486-1510` does not execute the digest gate, so the checklist is guaranteed to stop before install. Name an authoritative post-round-10 manifest (or obtain a ruling that narrows/replaces the packet-exhibit comparison) and test the actual five-file comparison.

M-A is independently cured: isolated real `tick` CLI probes for M1 and M9 each returned `HOLD_UNSAFE`, named the malformed path, and created no `attempts/`. M-C is cured: the temp-only M8 mutation failed the new named test. H-2 is cured: a stale `state.json` rendered age `901.250` and decision `HOLD_UNSAFE`, and `scripts.magistrate_watchdog` never entered `sys.modules`. S-A/24a matches the round-9 licence. D-172 is prospectively compliant but vacuous: round 10 changes zero lines in its four governed surfaces; trace 27 records M1/M9 RED evidence, and V3 supplies the requested independent M8 kill.

Same-signature statement: **YES**. The broader delta-8 signature recurs twice: permitted tests are green while unexecuted production checklist paths fail.

Verdict line: **BLOCKED**.

## Residual risk

The review did not install/load a LaunchAgent, touch default custody, launch an agent, send email, or signal a production process. Installed handoff and launchd activation remain lead-owned gates after F1 and F2 are cured.
