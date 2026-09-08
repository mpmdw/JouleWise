```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Disposition B satisfies the requested matrices; 97 scoped tests pass, valid-lock behavior matches HEAD~1, and both mutations are caught.",
  "workspace": {
    "base_requested": "298da021637342986f8d57c4fa0e000921cb66ab",
    "base_mode": "exact",
    "head_start": "298da021637342986f8d57c4fa0e000921cb66ab",
    "head_end": "298da021637342986f8d57c4fa0e000921cb66ab",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 97 tests in 21.314s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 97 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/delta2_audit.py matrix events collision",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MATRIX_PASS 138 cases (69 decide; 69 exact documented block)",
          "EVENTS_PASS repeated refusals; HEAD~1 load/read/render/ack; relaunch retains notice; drain preserves record",
          "SAME_TOKEN_COLLISION: HOLD_UNSAFE corrupt_lock_resident_live: pid=100; lock retained through 3 ticks"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MATRIX_PASS 138[\\s\\S]*EVENTS_PASS[\\s\\S]*SAME_TOKEN_COLLISION: HOLD_UNSAFE"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/delta2_audit.py mutation parity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MUTATION_ABSENT_KILLED FAILED (failures=72, errors=12)",
          "MUTATION_TWIN_KILLED FAILED (failures=6)",
          "VALID_PARITY_PASS 42 differential cases; 94 unchanged preexisting tests pass"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATION_ABSENT_KILLED[\\s\\S]*MUTATION_TWIN_KILLED[\\s\\S]*VALID_PARITY_PASS 42"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nexec(open('/private/tmp/delta2_audit.py').read().split(\"if __name__=='__main__':\")[0])\nold=docblock(subprocess.check_output(['git','show','HEAD~1:docs/process/MAGISTRATE_WATCHDOG.md'],cwd=ROOT).decode())\nnew=docblock((ROOT/'docs/process/MAGISTRATE_WATCHDOG.md').read_text())\ncount=0\nfor record in (RECORD,{k:v for k,v in RECORD.items() if k!='activation_id'}):\n    for rows in ([],[ROW()],[ROW(start='different')],[ROW(command='<defunct>')],[ROW(200,command=TWIN)],[ROW(200,command='claude daemon run')],[ROW(200,command='claude bg-pty-host sock')],[ROW(200,command='claude --bg-spare sock')]):\n        outcomes=[]\n        for block in (old,new):\n            with tempfile.TemporaryDirectory() as td:\n                h=Harness(pathlib.Path(td),NOW); path=h.storage.root/'magistrate.lock';h.storage.atomic_json(path,record); error=None\n                with mock.patch.object(wd,'DEFAULT_CUSTODY_ROOT',path.parent),mock.patch.object(wd.RealProcessTable,'snapshot',return_value=rows),contextlib.redirect_stdout(io.StringIO()):\n                    try: exec(compile(block,'<step4-valid>','exec'),{})\n                    except SystemExit as e: error=str(e)\n                outcomes.append((error,path.exists()))\n        assert outcomes[0]==outcomes[1],outcomes\n        count+=1\nprint(f'VALID_DOCUMENT_PARITY_PASS {count} cases')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["VALID_DOCUMENT_PARITY_PASS 16 cases"]},
      "expected": {"exit_code": 0, "tail_regex": "VALID_DOCUMENT_PARITY_PASS 16 cases"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff HEAD~1 HEAD -- scripts/magistrate_watchdog.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A same-PID/same-lstart replacement remains held indefinitely while visible. Injection confirms this required conservative behavior; no live macOS collision or collision-frequency measurement was performed.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Repository remained clean and unchanged. Replay harness is /private/tmp/delta2_audit.py; mutation copies were temporary. The absent-record mutation bypassed its refusal by returning None: both matrix methods failed assertions, and the CLI method raised FileNotFoundError because the incorrectly removed lock was missing. The mutation runner's initial rejection of those expected test errors was corrected before V3.",
      "needs": ""
    }
  ]
}
```

## Residual risk

PID plus `lstart` is not a guaranteed unique identity. Apple’s `ps` formats the seconds component of process start time; XNU also maintains a separate process unique identifier. The injected collision therefore demonstrates possible relaunch starvation, but does not establish its practical frequency on this Mac. Holding the matching pair complies with the cold ruling. [Apple ps implementation](https://raw.githubusercontent.com/apple-oss-distributions/adv_cmds/main/ps/print.c), [Apple process identity implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_proc.c).

Compatibility was verified against HEAD~1’s existing readers. Actual launch-notice email delivery and live hardware behavior were not exercised.