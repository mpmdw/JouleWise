```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "FIX-1–5 implementation landed; two generator checks await the out-of-scope generated runsheet update.",
  "workspace": {
    "base_requested": "3d5b7623",
    "base_mode": "exact",
    "head_start": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "head_end": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "upstream_end": "1d39729c7f4b1dd7b732b9a92f76bad451cadea8",
    "branch": "feat/2026-09-15-install-windows-multi-01"
  },
  "pathspec": [
    "scripts/run_night.py",
    "scripts/gen_derivation_night.py",
    "scripts/magistrate_watchdog.py",
    "scripts/install_night_agent.sh",
    "configs/launchd/com.joulewise.night.plist.template",
    "tests/test_run_night.py",
    "tests/test_gen_derivation_night.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_install_night_agent.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 91 tests in 10.261s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_gen_derivation_night",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 30.177s", "FAILED (failures=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 89 tests in 2.124s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 33 tests in 25.349s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 59 tests in 0.553s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_install_night_agent.InstallNightAgentTests.test_installer_derives_calendar_fields_from_plan_without_hour_flags",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 1.801s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/install-windows-d172.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MUTATED_EXIT=1", "RESTORED_BYTE_IDENTICAL", "RESTORED_EXIT=0"]},
      "expected": {"exit_code": 0, "tail_regex": "RESTORED_EXIT=0"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check && /bin/zsh -n scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: required generator wording changes make the generated runsheet stale. Its two existing drift tests remain enforced; no out-of-scope file was modified.",
      "needs": "Have the docs seat apply the generated runsheet update, then rerun V2."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced concurrently; the worktree HEAD remained exactly at the requested base.",
      "needs": "Review integration against the lead's final base."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"],
    "reason": "FIX-2 changes generated explanatory text embedded in this document.",
    "blocked_work": "Passing test_the_region_carries_the_live_chain_digest and test_the_runsheet_region_matches_the_generator.",
    "minimal_change": "Apply the three-line generated-region replacement prepared at /tmp/install-windows-runsheet.patch; the docs seat may own this instead of expanding Seat A."
  }
}
```

## Change

- **FIX-1:** `scripts/run_night.py:67,954–1041,1540,1938` adds grace, install cutoff, validated recurring spans, DST resolution, calendar fields and `schedule`. Results use `plan_id` at `:570,578,591`. The overrun refusal remains reachable under an injected deadline; `dead_man()` behavior is unchanged.
- **FIX-2:** `scripts/gen_derivation_night.py:47,514,762` imports the driver’s function, checks the derived deadline and removes fixed-clock wording. Twelve-slot/window arithmetic is unchanged.
- **FIX-3:** `scripts/magistrate_watchdog.py:260,711,769,782,815,1444` reads installed plists through Storage, fences their active plans, holds unsafe on unreadable/malformed inputs, and uses derived deadlines throughout.
- **FIX-4:** `scripts/install_night_agent.sh:153,163,282,305` derives calendars, checks refusals before output creation, refuses occupied labels, and rechecks/rolls back at bootstrap. Template `:26–29` adds Month/Day for the night agent; the dead-man remains daily. **Dropped `--hour`/`--minute`.**
- **FIX-5:** Regressions are in `tests/test_run_night.py:1333–1433`, `tests/test_gen_derivation_night.py:390`, `tests/test_magistrate_watchdog.py:460–510`, and `tests/test_install_night_agent.py:195–281`. The gate registry test remains unchanged.

No commits, network operations, real agent bootstrap, or document edits.

## Verification notes

All five modules passed at baseline: driver 85, generator 40, watchdog 86, installer 25, gate 59. Final results are in the envelope. Intermediate failures from fixture adaptation and a schedule-key collision in the refusal-literal test were corrected.

D-172 mutated **template line 26**, `<key>Month</key>` → `<key>Year</key>`. V6 exercised real installer argv, real schedule subprocesses, rendering and fake launchctl; it failed with `FAILED (failures=1)`, exit 1. Byte-identical restoration passed, exit 0. Transcript: `/tmp/install-windows-d172.log`.

The only remaining failures are the two generated-document checks in F1. They were neither weakened nor skipped. Full-suite execution was omitted as instructed.

**Exact documentation replacements for the docs seat:**

- `MAGISTRATE_WATCHDOG.md:31`: replace the belt/minute sentence with: “`FENCED`: a discovered or installed plan’s active span forbids launch.”
- `:42`: “All plan arithmetic uses epoch seconds; recurring install spans and launchd calendar fields resolve local time.”
- `:48`: replace `_next_deadman_epoch(t0)` with `deadman_epoch(plan)`.
- `:52`: delete the fixed-interval sentence; retain the sentence about unsafe equality boundaries.
- `:54`: replace both fixed-fence sentences with: “An installed-plan fence also prevents adoption when that plan is absent from discovery; the short tick returns `FENCED` with `adopt=False` while its span remains active.”
- `derivation_night_runbook.md:1250–1263`: “Install both agents while inside a listed install span and strictly before `install_close_epoch = t0 − PLAN_LEAD_S − 3600`; obtain the spans, cutoff and derived dead-man from `run_night.py schedule --plan`.” Remove the day-before, 07:xx prohibition and proposed 06:05 cutoff.
- `:1411–1416`: “Check the night agent’s Month/Day/Hour/Minute against t0 and the dead-man’s daily Hour/Minute against the derived deadline.” Replace the `--hour 7` refusal explanation with the new timing, custody-location and occupied-label refusals.
- Remove `--hour`/`--minute` from install/uninstall examples at `:1389,1423` and corresponding command descriptions. Replace the fixed-deadline arithmetic at `:1150–1166,2113` with the derived epoch.
- Apply `/tmp/install-windows-runsheet.patch` for the generated text.

## Residual risk

**What the lead should double-check:** integrated docs and caller migration after dropping hour flags; launchd Month/Day behavior on 25G83; recovery grace against live courier evidence; results-branch consumers; and custom span boundaries during repeated/nonexistent DST minutes. These were not live hardware validations.