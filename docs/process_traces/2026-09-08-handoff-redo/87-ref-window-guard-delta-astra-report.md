```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two blockers remain: command mentions cause false refusals, and the global unittest exclusion hides a valid live driver.",
  "workspace": {
    "base_requested": "a37de2ec31d32be02cec0fa5c3ffd9bde6c5da83",
    "base_mode": "exact",
    "head_start": "b5786cea113f8aa08a75cbbd14cd89275b16d236",
    "head_end": "b5786cea113f8aa08a75cbbd14cd89275b16d236",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 2, "should_fix": 0, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/window_status.sh",
        "line": 65,
        "summary": "Whole-command matching still treats file mentions as execution; whitespace truncation also defeats the codex exemption.",
        "command": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\ns=Path('scripts/window_status.sh').read_text().split(\"$(awk '\\n\",1)[1].split(\"\\n' <<<\",1)[0]\nfor c in ['20 1 /Applications/Codex App/bin/codex exec \"scripts/run_night.py run\"','20 1 less scripts/run_night.py','20 1 python3 scripts/run_night.py run --plan /tmp/my unittest plan.json']:\n print(c, '=>', subprocess.check_output(['awk',s],input=c+'\\n',text=True).strip())\nPY",
        "observed": "Codex under a spaced executable path and less both classify as live. Full-script fixtures also refuse vim and git grep scripts/run_night.py: rc=1, wrote=False.",
        "expected": "Non-measurement processes classify as clear and permit status writing."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "scripts/window_status.sh",
        "line": 70,
        "summary": "The global unittest exclusion suppresses a live run_night driver when its plan path contains that whitespace-delimited word.",
        "command": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\ns=Path('scripts/window_status.sh').read_text().split(\"$(awk '\\n\",1)[1].split(\"\\n' <<<\",1)[0]\nfor c in ['20 1 /Applications/Codex App/bin/codex exec \"scripts/run_night.py run\"','20 1 less scripts/run_night.py','20 1 python3 scripts/run_night.py run --plan /tmp/my unittest plan.json']:\n print(c, '=>', subprocess.check_output(['awk',s],input=c+'\\n',text=True).strip())\nPY",
        "observed": "The driver classifies as clear. Full-script injected census including its custom zsh chain and sleep child returns rc=0, wrote=True.",
        "expected": "A live driver with a valid spaced plan path refuses before writing."
      }
    ],
    "probe_matrix": {
      "cases": 26,
      "matched_expectations": 21,
      "mismatches": [
        "editor",
        "less",
        "git_grep_path",
        "codex_spaced_path",
        "night_unittest_plan"
      ],
      "confirmed": [
        "Rebuilt G2-a driver/custom-chain/sleep census refuses.",
        "PyPy, spaced interpreter/script/chain paths, Python --, env, venv, module and historical window-chain shapes refuse.",
        "Garbage, empty, header-only and all-malformed censuses refuse.",
        "A census containing only the guard's ps row passes.",
        "Ordinary codex prompt, git grep run_night.py, unittest, grep, dry-run and shell-echo exclusions pass.",
        "All five new regression methods fail against HEAD~1.",
        "Removing run_night detection and census validation separately kills the named regressions."
      ]
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 3.893s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom pathlib import Path\nfrom tests.test_window_status_guard import WindowStatusGuardTests as T\nfor argv in ['vim scripts/run_night.py','less scripts/run_night.py','git grep scripts/run_night.py','/Applications/Codex App/bin/codex exec \"scripts/run_night.py run\"','python3 scripts/run_night.py run --plan /tmp/my unittest plan.json']:\n t=T(); t.setUp()\n try:\n  t.census.write_text('20 1 '+argv+'\\n'); s=Path(t.temporary.name)/'freeze'; s.touch(); r=t._run_status(s)\n  print(repr(argv), 'rc='+str(r.returncode), 'wrote='+str((t.repository/'WINDOW_STATUS.md').exists()))\n finally: t.doCleanups()\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "'vim scripts/run_night.py' rc=1 wrote=False",
          "'less scripts/run_night.py' rc=1 wrote=False",
          "'git grep scripts/run_night.py' rc=1 wrote=False",
          "'/Applications/Codex App/bin/codex exec \"scripts/run_night.py run\"' rc=1 wrote=False",
          "'python3 scripts/run_night.py run --plan /tmp/my unittest plan.json' rc=0 wrote=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "plan.json' rc=1 wrote=False"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport io, subprocess, unittest\nfrom unittest.mock import patch\nimport tests.test_window_status_guard as m\noriginal=m.SCRIPT.read_text()\nbase=subprocess.check_output(['git','show','HEAD~1:scripts/window_status.sh'],text=True)\nlines=original.splitlines(keepends=True)\nno_night=''.join(lines[:73]+lines[78:])\nno_validation=''.join(lines[:55]+lines[59:]).replace('if (invalid || !rows) print \"invalid\"\\n    else if (live)', 'if (live)')\nnames=['test_run_night_custom_chain_refuses','test_paths_with_spaces_refuse','test_python_option_separator_refuses','test_garbage_census_refuses','test_empty_census_refuses']\nreal_run=subprocess.run\nfor label,source,selected in [('baseline',base,names),('drop_run_night',no_night,names[:1]),('drop_row_validation',no_validation,names[3:])]:\n def run(args,*a,**kw):\n  if len(args)>1 and args[0]=='/bin/bash' and args[1]==str(m.SCRIPT):\n   args=('/bin/bash','-s','--',*args[2:]); kw['input']=source\n  return real_run(args,*a,**kw)\n for name in selected:\n  out=io.StringIO()\n  with patch.object(m.subprocess,'run',run):\n   result=unittest.TextTestRunner(stream=out).run(unittest.TestSuite([m.WindowStatusGuardTests(name)]))\n  print(label,name,'KILLED' if not result.wasSuccessful() else 'SURVIVED',f'failures={len(result.failures)} errors={len(result.errors)}')\n  for _,trace in result.failures: print(trace.strip().splitlines()[-1])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "drop_run_night test_run_night_custom_chain_refuses KILLED failures=2 errors=0",
          "AssertionError: 0 != 1 :",
          "AssertionError: 0 != 1 :",
          "drop_row_validation test_garbage_census_refuses KILLED failures=1 errors=0",
          "AssertionError: 0 != 1 :",
          "drop_row_validation test_empty_census_refuses KILLED failures=1 errors=0",
          "AssertionError: 0 != 1 :"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "KILLED failures=[12] errors=0"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["b5786cea113f8aa08a75cbbd14cd89275b16d236"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^b5786cea113f8aa08a75cbbd14cd89275b16d236$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — blocker:** `scripts/window_status.sh:65–74` still confuses mentions with execution. Plain `codex exec … "scripts/run_night.py …"` passes, but a Codex executable beneath a directory containing spaces loses its exemption and refuses. `vim`, `less`, and `git grep scripts/run_night.py` also falsely refuse. Fixing this requires identifying the actual entry point rather than extending the executable exclusion list.

**F2 — blocker:** `scripts/window_status.sh:70` exempts any command containing the word `unittest`. A legitimate flattened command for `--plan "/tmp/my unittest plan.json"` therefore bypasses detection. Its arbitrary chain and sleep child do not restore refusal because the skipped driver never enters `night[]`.

## Residual risk

All measurement evidence here uses injected censuses; no live collection was started. The prior report was read from the main checkout because it is absent from this worktree.

PID/PPID validation rejects malformed records but does not establish census completeness: a lone valid `ps` row permits writing. Repository files and HEAD remained unchanged.