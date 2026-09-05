```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT CURED: the named nested-module probe and D117 call site pass, but a basename collision still lets a nested support module bypass the recursive guard.",
  "workspace": {
    "base_requested": "355fa8431b1da14c0a5f8dc7bb382dd18c6f0351",
    "base_mode": "exact",
    "head_start": "355fa8431b1da14c0a5f8dc7bb382dd18c6f0351",
    "head_end": "355fa8431b1da14c0a5f8dc7bb382dd18c6f0351",
    "upstream_end": "7da20e28e795ac9aac41f774e4f5f7fa0ef29f5c",
    "branch": "feat/2026-09-04-fan-GIT-FIXTURE-MAINTENANCE-SWEEP-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GIT-FIXTURE-MAINTENANCE-SWEEP-01/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "result": "NOT CURED",
    "dispositions": [
      {
        "id": "GF-01",
        "status": "CURED",
        "text": "The PR #281 D117 fixture now calls tests.git_fixture.init_git_fixture, and runtime readback proves the exact four local maintenance/gc values survive."
      },
      {
        "id": "GF-02",
        "status": "NOT CURED",
        "text": "Recursive enumeration works for an ordinary nested support module, but basename-keyed exemptions let a nested support/git_fixture.py inherit the top-level helper exemption."
      }
    ],
    "regressed": [],
    "new_defects": [],
    "same_signature": "YES — GF-02 recurs at same-signature COUNT 2: a Python support module below tests/ can still contain direct git init without being reported.",
    "findings": [
      {
        "id": "GF-02",
        "severity": "blocker",
        "location": "tests/test_git_fixture_maintenance.py:99",
        "text": "ESTABLISHED_LOCAL_HELPERS is consulted with path.name. A nested support/git_fixture.py therefore inherits the canonical top-level exemption. With GIT_MAINTENANCE_CONTROLS = (), one direct git init, and a syntactic no-op hygiene loop, _git_init_violations returns {}. Key exemptions by tests-root-relative path (or exact resolved path) so only the established file can bypass the direct-init report.",
        "counterfactual": "The executed nested support/git_fixture.py probe expected {'support/git_fixture.py': (4,)} but printed {} and exited 1."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_git_fixture_maintenance tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 44 tests in 18.819s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'\nimport json, tempfile\nfrom pathlib import Path\nfrom tests.test_git_fixture_maintenance import _git_init_violations\nwith tempfile.TemporaryDirectory() as t:\n p=Path(t)/'tests/support/fixture_factory.py'; p.parent.mkdir(parents=True); p.write_text(\"import subprocess\\nsubprocess.run(('git', 'init'), check=True)\\n\", encoding='utf-8'); print(json.dumps(_git_init_violations(Path(t)/'tests'), sort_keys=True))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"support/fixture_factory.py\": [2]}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "support/fixture_factory.py.*2"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'\nimport json, subprocess, tempfile\nfrom pathlib import Path\nfrom tests.test_d117_contrast_v5_pack import D117ContrastV5PackTests\nkeys=('maintenance.auto','gc.auto','maintenance.autoDetach','gc.autoDetach')\nwith tempfile.TemporaryDirectory() as t:\n r=Path(t)/'repository'; r.mkdir(); D117ContrastV5PackTests().init_fixture_git(r); print(json.dumps({k:subprocess.run(('git','-C',str(r),'config','--local','--get',k),check=True,capture_output=True,text=True).stdout.strip() for k in keys},sort_keys=True))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"gc.auto\": \"0\", \"gc.autoDetach\": \"false\", \"maintenance.auto\": \"false\", \"maintenance.autoDetach\": \"false\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "gc.auto.*0.*maintenance.auto.*false"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'\nimport json, tempfile\nfrom pathlib import Path\nfrom tests.test_git_fixture_maintenance import _git_init_violations\nsource='import subprocess\\nGIT_MAINTENANCE_CONTROLS = ()\\ndef init_git_fixture(repository):\\n    subprocess.run((\"git\", \"init\"), check=True)\\n    for key, value in GIT_MAINTENANCE_CONTROLS:\\n        subprocess.run((\"git\", \"config\", \"--local\", key, value), check=True)\\n'\nwith tempfile.TemporaryDirectory() as t:\n root=Path(t)/'tests'; p=root/'support/git_fixture.py'; p.parent.mkdir(parents=True); p.write_text(source,encoding='utf-8'); v=_git_init_violations(root); print(json.dumps(v,sort_keys=True)); raise SystemExit(0 if v=={'support/git_fixture.py':(4,)} else 1)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "{}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "support/git_fixture.py.*4"
      }
    }
  ],
  "flags": []
}
```

## Findings

### GF-02 — blocker

`_git_init_violations` now recurses, and the required ordinary `support/fixture_factory.py` falsifier is reported at line 2. However, `_direct_git_init_lines` indexes `ESTABLISHED_LOCAL_HELPERS` by `path.name`. The executed `support/git_fixture.py` counterexample inherited the top-level helper exemption; with an empty controls tuple, direct `git init` was omitted and the probe failed with `{}`. GF-02 is therefore **NOT CURED**, not a new defect: **same-signature COUNT 2**.

GF-01 is **CURED**. Inspection of `git show HEAD` confirms that the D117 PR #281 site calls `init_git_fixture(root, "-q")`; temp-repository readback returned all four exact local values (`maintenance.auto=false`, `gc.auto=0`, and both auto-detach keys `false`). No regression was found in the mandated 44-test replay.

## Residual risk

The magistrate's separate 797-test replay was not repeated under the explicit preflight limit. No additional coverage limitation affects this blocker.
