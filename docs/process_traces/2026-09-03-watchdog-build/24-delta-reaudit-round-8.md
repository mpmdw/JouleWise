```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 8 cures C-1 through C-8, with one new should-fix installer rollback residual and one report-metadata nit.",
  "workspace": {
    "base_requested": "1b51fecfdae7246015ed9d981636e21939d760fc",
    "base_mode": "exact",
    "head_start": "a15cc15e7773a2d4a593cd1ad8814a9595b83d82",
    "head_end": "a15cc15e7773a2d4a593cd1ad8814a9595b83d82",
    "upstream_end": "a15cc15e7773a2d4a593cd1ad8814a9595b83d82",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/24-delta-reaudit-round-8.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "line": "RESIDUAL",
    "clauses": {
      "C-1": "CURED",
      "C-2": "CURED",
      "C-3": "CURED",
      "C-4": "CURED",
      "C-5": "CURED",
      "C-6": "CURED",
      "C-7": "CURED",
      "C-8": "CURED"
    },
    "same_signature": "YES for the broader production-control-flow signature: permitted tests are green while untested installer failure paths mis-handle prior/new state; NO for the specified C-1 through C-8 contracts.",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Installer rollback is not state-preserving outside the single tested lock-collision shape",
        "paths": ["scripts/install_magistrate_watchdog.sh", "tests/test_install_magistrate_watchdog.py"]
      },
      {
        "id": "F2",
        "severity": "nit",
        "title": "Trace 23 misstates the round-8 final Git head",
        "paths": ["docs/process_traces/2026-09-03-watchdog-build/23-sol-fix-round-8-report.md"]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog tests.test_night_gate tests.test_run_night tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 182 tests in 28.412s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 182 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["C-1 inline real-CLI harness: t0=1788550200; REQUEST=1788548880; TERM=1788549240; KILL=1788549300; latch@-10=KILL; replacement@-12=TERM+KILL"]},
      "expected": {"exit_code": 0, "tail_regex": "kill_no_later_than_t0_minus_15.*true.*kill_first_poll.*true.*term_first_poll.*true"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["C-2/C-8: noncanonical exit=3; plist=/Users/edr/code/JouleWise + /opt/homebrew/opt/python@3.14/bin/python3.14", "C-3: decision=LAUNCHING; event=backoff_reset_after_reboot"]},
      "expected": {"exit_code": 0, "tail_regex": "noncanonical_checkout[\\s\\S]*LAUNCHING[\\s\\S]*backoff_reset_after_reboot"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n 'SCRIPT_PATH\\.read_text|assertIn|assertNotIn' tests/test_install_magistrate_watchdog.py; if rg -n 'assertIn\\([^\\n]*(source|script)|assert[^\\n]*SCRIPT_PATH' tests/test_install_magistrate_watchdog.py; then exit 4; else echo 'NO_ASSERTION_OVER_INSTALLER_SOURCE'; fi; rg -n 'does not load before GUI login|no `state\\.json` write for more than 15 minutes|watchdog is dead|courier email for the next window|measurement_root=\"/private/tmp/|deliberately fake|Remove every `REHEARSAL_STUB`' docs/process/MAGISTRATE_WATCHDOG.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NO_ASSERTION_OVER_INSTALLER_SOURCE", "fake roots at MAGISTRATE_WATCHDOG.md:253,343"]},
      "expected": {"exit_code": 0, "tail_regex": "NO_ASSERTION_OVER_INSTALLER_SOURCE[\\s\\S]*/private/tmp/"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["pre-existing plist + lock collision: exit=1, plist absent, old lock preserved", "bootstrap failure after new seed: exit=3, plist absent, new lock remains"]},
      "expected": {"exit_code": 0, "tail_regex": "plist_exists_after.*false[\\s\\S]*lock_exists_after.*true"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check 1b51fecf..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied /bin/ps, so V2 retained the real CLI/parser/fork and real temporary resident signals but injected a deterministic PID/start process-table seam.",
      "needs": "Cold gate retains live process-table and loaded-LaunchAgent verification."
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "C-9 Gmail/courier send remains explicitly outside round 8.",
      "needs": "Carry C-9 to the cold-gate packet."
    }
  ]
}
```

## Findings

F1 — should_fix — `cleanup_failed_install` removes the destination plist whenever this attempt wrote it, without preserving prior bytes, and it never removes a lock successfully seeded by this attempt if `bootstrap`/`print` later fails. Executed counterfactuals against the behavioral shadow: (a) pre-existing plist + pre-existing lock → exit 1, old lock preserved, plist deleted; a re-install can therefore remove a working reboot-persistent configuration; (b) fresh install + stubbed bootstrap failure → exit 3, plist removed, newly seeded `magistrate.lock` remains; the next install collides until manual cleanup. Preserve/restore a prior plist and remove only an exact lock created by the failing attempt on downstream failure.

F2 — nit — trace 23 says both baseline and final HEAD are `1b51fecf`; the actual final head is `a15cc15e`. Counterfactual: a reviewer replaying the report's stated base/final pair obtains an empty diff and loses the round evidence.

Clause ledger (trace 22 → trace 21/16 source):

- C-1 (B-1 + A-1) **CURED**. Real CLI/parser/fork with a clock seam and temporary TERM-ignoring resident produced `t0=1788550200`: drain start/REQUEST `1788548880` (t0−22), TERM `1788549240` (t0−16), KILL `1788549300` (t0−15). A live-supervisor latch at t0−10 KILLed on its first poll. A dead-supervisor replacement tick at t0−12 emitted TERM and KILL at `1788549480`.
- C-2 (B-2) **CURED**. A real installer copied to a temporary Git repo refused before writing, rc 3 with `noncanonical_checkout`. Render-only in temp HOME produced WorkingDirectory `/Users/edr/code/JouleWise` and script argument `/Users/edr/code/JouleWise/scripts/magistrate_watchdog.py`.
- C-3 (B-3) **CURED**. A persisted foreign boot id plus far-future monotonic and wall deadlines returned `LAUNCHING` under `tick(..., dry_run=True)` and appended `backoff_reset_after_reboot{stored_boot_id:"foreign-boot-id",observed_boot_id:"current-boot-id"}` at epoch `1788548400`.
- C-4 (B-4, S-2) **CURED as ruled**. The real zsh subprocess module is green, parses plist/lock bytes, records stub launchctl argv, and proves the specified failed-lock-seed rollback. Grep found no assertion over installer source; its source read is used only to construct the executable canonical shadow. F1 is beyond that one ruled rollback shape.
- C-5 (S-1) **CURED** by C-1's replacement tick: phase comes from wall time, not tick count; TERM was immediate at t0−12.
- C-6 (S-3) **CURED**. Doc line 61 states the GUI-login limit, accepted logged-in-week posture, >15-minute `state.json` death threshold, and next-window courier report; the executable contract test passed.
- C-7 (S-4) **CURED**. Doc line 222 states fake-root/non-reuse/removal semantics; both writer-round-tripped examples use distinct `/private/tmp/...` roots (lines 253, 343).
- C-8 (S-5) **CURED**. The rendered first argument is the test interpreter `/opt/homebrew/opt/python@3.14/bin/python3.14`, not `/usr/bin/env` or `/usr/bin/python3`.

Same-signature statement: **YES**, narrowly for the broader signature “permitted tests green while an untested production control-flow path fails”: V1 is green while F1's two installer failure paths mis-rollback. **NO** for the specified C-1 through C-8 contracts; each has independent executed evidence above.

Verdict line: **RESIDUAL**.

## Residual risk

No real LaunchAgent was installed or loaded and no production process was signalled. The sandbox denied `/bin/ps`; V2 therefore injected only the process-table seam while exercising the real CLI/parser/fork, state transitions, deadline code, and signals against temporary residents. The cold gate still owns live `ps`, launchctl, first installed tick, twin-kill, and C-9 Gmail/courier evidence. Only the six preflight-authorized modules were run; no broader discovery was attempted.
