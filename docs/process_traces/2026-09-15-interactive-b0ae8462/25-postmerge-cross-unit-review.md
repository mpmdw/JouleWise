```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three stale-reference findings; no stale executable installer caller found. All 336 tests passed across five individually run modules.",
  "workspace": {
    "base_requested": "4c84312651b1649dd858486a822d3e6d10e85974",
    "base_mode": "exact",
    "head_start": "4c84312651b1649dd858486a822d3e6d10e85974",
    "head_end": "4c84312651b1649dd858486a822d3e6d10e85974",
    "upstream_end": "d2cc8b5e314c2cd9277c0acff6d746ce96640e20",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "review_root": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/postmerge-copy",
    "baseline_digest_verified": true,
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "location": "docs/decision_log.md:11437",
        "title": "D-175 still requires a staged render that the installer now refuses",
        "detail": "The current REHEARSAL_STUB instructions require --render-only before os.replace publication. Prepared.admit requires the published custody_root/night_plan.json path, including in render-only mode (joulewise/night_agent_install.py:584,672). A valid staged REHEARSAL_STUB reproduced exit 2, plan_outside_custody_root, without rendering or invoking fake launchctl."
      },
      {
        "id": "R2",
        "severity": "nit",
        "location": "docs/process/state_kernel.json:3032",
        "title": "Queued follow-ups still target the retired shell implementation",
        "detail": "INSTALLER-BACKUP-WINDOW-01 prescribes moving an EXIT trap before mktemp and injecting a fake cp, but the wrapper now delegates to Python and backups are Target.stage sidecars. NIGHT-STREAM-PATHS-01 at line 3968 also assigns directory creation to obsolete shell line 125. Rebase these acceptance instructions onto the engine before assigning them. The merged INSTALL-WINDOWS-MULTI-01 row also remains queued at line 3015."
      },
      {
        "id": "R3",
        "severity": "nit",
        "location": "docs/phase_2/derivation_night_runbook.md:2555",
        "title": "The current source map points to a removed function",
        "detail": "The path-invariant row cites check_schedule in scripts/install_night_agent.sh. The check now lives in Prepared.admit in joulewise/night_agent_install.py:584. Separately, tests/test_run_night.py:1020 retains an obsolete fixed-07:00 explanatory comment; its executed test passes."
      }
    ],
    "reference_dispositions": [
      "scripts/install_night_agent.sh:88 and all direct references in tests/test_install_night_agent.py, tests/test_night_agent_install.py, and tests/test_run_night.py: consistent. No remaining executable caller passes --hour/--minute or parses the old rolled-back prose.",
      "scripts/run_night.py:954, scripts/gen_derivation_night.py:514, scripts/magistrate_watchdog.py:712, and configs/launchd/com.joulewise.night.plist.template:24: consistent plan-derived timing and installed-plan fencing.",
      "derivation_night_runbook.md:1618,1655,1668 and NIGHT_HANDBACK.md:203,400,425: consistent arguments, calendar checks, and exit-0-only uninstall recovery.",
      "NIGHT_COURIER_PROMPT.md:16,21 and MAGISTRATE_WATCHDOG.md:35,56: consistent results-branch naming, retained/UNKNOWN handling, and derived dead-man. MAGISTRATE_RELAUNCH_PROMPT.md has no obsolete installer flags or fixed-time requirement.",
      "docs/contracts/pack_night_go_receipt.md:26,995: plan-path contract remains consistent; lines 631/640 are dated implementation evidence.",
      "configs/calibration/preregistration_d079_epoch_25g83_rev1.md:112,121 retains historical fixed-07:00 and 03:00–06:30 prose. Preserve pinned registration bytes; current runbook timing supersedes it, with the old install-span comparison explicitly classified historical at runbook line 2543.",
      "Dated traces, run reports, historical handback entries, and archived/generated snapshots retain old commands and timing. These are historical, not current invocation templates. D-175's current summary is the actionable exception in R1.",
      "scripts/install_magistrate_watchdog.sh:313 emits rolled-back prose for its own separate installer; it does not consume night-installer output. Other rolled-back matches concern unrelated operations."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 101 tests in 18.892s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 101 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 52 tests in 63.828s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 52 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 50 tests in 995.180s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 50 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 93 tests in 2.588s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 93 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_derivation_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 40 tests in 38.389s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 40 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom dataclasses import replace\nimport json\nfrom tests.test_install_night_agent import InstallNightAgentTests\nfrom joulewise.night_gate import NightPlan\nfrom joulewise.night_plan_writer import write_night_plan\ncase = InstallNightAgentTests()\ncase.setUp()\ntry:\n    published = case._write_plan()\n    plan = replace(NightPlan.from_mapping(json.loads(published.read_text())), receipt_class='REHEARSAL_STUB', pack_night=None, registration_path=str(case.root / 'registration.json'))\n    staged = case.root / 'staged-night-plan.json'\n    write_night_plan(staged, plan)\n    published.unlink()\n    result = case._run(staged, render_only=True)\n    print('REHEARSAL_STUB staged render exit:', result.returncode)\n    print('plan_outside_custody_root:', 'plan_outside_custody_root' in result.stderr)\n    print('render directory exists:', case.rendered.exists())\n    print('fake launchctl called:', case.launch_log.exists())\n    assert result.returncode == 2 and 'plan_outside_custody_root' in result.stderr\n    assert not case.rendered.exists() and not case.launch_log.exists()\nfinally:\n    case.tearDown()\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REHEARSAL_STUB staged render exit: 2", "plan_outside_custody_root: True", "render directory exists: False", "fake launchctl called: False"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)staged render exit: 2.*fake launchctl called: False"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git --no-optional-locks -C /Users/edr/code/JouleWise-wt-postmerge status --short --branch; git -C /Users/edr/code/JouleWise-wt-postmerge rev-parse HEAD; git -C /Users/edr/code/JouleWise-wt-postmerge rev-parse origin/main; git --no-optional-locks status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "4c84312651b1649dd858486a822d3e6d10e85974", "d2cc8b5e314c2cd9277c0acff6d746ce96640e20", "## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)^## HEAD \\(no branch\\).*4c84312651b1649dd858486a822d3e6d10e85974.*## HEAD \\(no branch\\)"}
    }
  ],
  "flags": []
}
```

## Findings

- **R1 — should_fix:** Reconcile D-175’s pre-publication validation requirement with the new render-only behavior before the next stub arm. Preserve both staged validation and the real-install publication invariant.
- **R2 — nit:** Rebaseline the queued installer follow-ups against the Python engine.
- **R3 — nit:** Correct the removed-function pointer and fixed-time test comment.

No repository files changed. The next step is lead adjudication of R1, followed by reference/bookkeeping corrections.

## Residual risk

Validation used temporary fixtures and fake `launchctl`; no live launchd operation or full repository suite ran. This review covers requested commit `4c843126`; the later local `origin/main` revision was not reviewed.