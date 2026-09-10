```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two in-scope findings: an unconditional refusal-code claim and seven added tests that pass on the base. No footprint violation found; reduce.py is unchanged.",
  "workspace": {
    "base_requested": "078a13a4",
    "base_mode": "exact",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "reviewed_head": "92c3e15a7597f3f2e05cd6d8964f4f5f17c78679",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "class": 1,
        "path": "docs/contracts/measurement_methodology.md",
        "line": 75,
        "summary": "Malformed idle JSON raises a different refusal under active v2 authentication."
      },
      {
        "id": "R2",
        "severity": "nit",
        "class": 2,
        "path": "tests/test_gate_sensibility_rounding.py",
        "line": 99,
        "summary": "Three admission rejection tests and four cooldown rejection tests pass on unchanged pre-change production code."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gate_sensibility_rounding tests.test_generate_g2a_probe_inputs tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=26, skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import contextlib, pathlib, subprocess, types, unittest\nfrom unittest.mock import patch\np='\\''tests/test_gate_sensibility_rounding.py'\\''\nm=types.ModuleType('\\''candidate_tests'\\'')\nm.__file__=str(pathlib.Path(p).resolve())\nexec(compile(subprocess.check_output(['\\''git'\\'','\\''show'\\'','\\''92c3e15a:'\\''+p]),m.__file__,'\\''exec'\\''),m.__dict__)\nmemory={}\nreal_read=pathlib.Path.read_text\ndef write(path,value,*a,**k):\n    memory[path]=value\n    return len(value)\ndef read(path,*a,**k):\n    return memory[path] if path in memory else real_read(path,*a,**k)\nsuite=unittest.TestSuite(cls(name) for cls in [m.AdmissionRoundingTests,m.CooldownRoundingTests] for name in unittest.defaultTestLoader.getTestCaseNames(cls) if '\\''_refuses_'\\'' in name)\nwith patch('\\''tempfile.TemporaryDirectory'\\'',return_value=contextlib.nullcontext(str(pathlib.Path.cwd()/'\\''memory-only-fixture'\\''))),patch.object(pathlib.Path,'\\''write_text'\\'',write),patch.object(pathlib.Path,'\\''read_text'\\'',read):\n    r=unittest.TextTestRunner(verbosity=2).run(suite)\nraise SystemExit(not r.wasSuccessful())\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import pathlib, subprocess, types\nfrom unittest.mock import mock_open, patch\nfrom joulewise.authentication_io import V2AuthenticationReadSession, V2AuthenticationInputError\np='\\''joulewise/environment_admission.py'\\''\nm=types.ModuleType('\\''candidate_environment'\\'')\nm.__file__=str(pathlib.Path(p).resolve())\nexec(compile(subprocess.check_output(['\\''git'\\'','\\''show'\\'','\\''92c3e15a:'\\''+p]),m.__file__,'\\''exec'\\''),m.__dict__)\nwith patch('\\''pathlib.Path.read_text'\\'',return_value='\\''{\\n'\\''):\n    print('\\''ordinary parser:'\\'',m._attempt_capture_interval(pathlib.Path('\\''.'\\''),1))\nwith V2AuthenticationReadSession(), patch('\\''builtins.open'\\'',mock_open(read_data=b'\\''{\\n'\\'')):\n    try:\n        m._attempt_capture_interval(pathlib.Path('\\''.'\\''),1)\n    except V2AuthenticationInputError as e:\n        print('\\''v2 parser:'\\'',type(e).__name__,e.reason)\n        assert e.reason == '\\''v2_authentication_invalid_json'\\''\n    else:\n        raise AssertionError('\\''expected an authentication exception'\\'')\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ordinary parser: None",
          "v2 parser: V2AuthenticationInputError v2_authentication_invalid_json"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "v2 parser: V2AuthenticationInputError v2_authentication_invalid_json"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.abc, importlib.util, pathlib, subprocess, sys, unittest, io\nroot=pathlib.Path.cwd()\nchanged=subprocess.check_output(['\\''git'\\'','\\''diff'\\'','\\''--name-only'\\'','\\''078a13a4..92c3e15a'\\''],text=True).splitlines()\nsources={p[:-3].replace('\\''/'\\'','\\''.'\\''):subprocess.check_output(['\\''git'\\'','\\''show'\\'','\\''92c3e15a:'\\''+p]) for p in changed if p.endswith('\\''.py'\\'')}\nclass Loader(importlib.abc.MetaPathFinder, importlib.abc.Loader):\n    def find_spec(self, fullname, path=None, target=None):\n        if fullname in sources:\n            return importlib.util.spec_from_loader(fullname,self)\n    def create_module(self,spec): return None\n    def exec_module(self,module):\n        module.__file__=str(root/(module.__name__.replace('\\''.'\\'','\\''/'\\'')+'\\''.py'\\''))\n        exec(compile(sources[module.__name__],module.__file__,'\\''exec'\\''),module.__dict__)\nsys.meta_path.insert(0,Loader())\nsuite=unittest.defaultTestLoader.loadTestsFromNames(['\\''tests.test_gate_sensibility_rounding.CooldownRoundingTests'\\'','\\''tests.test_gate_sensibility_rounding.TransitionMidpointRoundingTests'\\''])\nr=unittest.TextTestRunner(verbosity=2).run(suite)\nraise SystemExit(not r.wasSuccessful())\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --exit-code 078a13a4..92c3e15a -- joulewise/reduce.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The workspace remained at the base as instructed. V1 ran 55 tests but encountered the absent new module and unavailable temporary directories. Loading candidate Python modules from Git produced 68 tests, rc 1, errors=34, skipped=1; all reported errors were temporary-directory failures. Docs-freshness file reads still used the base checkout. V4 independently passed all eight candidate cooldown/transition tests. V2 used memory-backed fixture I/O for admission; the four cooldown controls also passed separately without I/O mocks.",
      "needs": "Lead rerun the requested suite at 92c3e15a in an environment permitting temporary files."
    }
  ]
}
```

## Findings

**R1 — The malformed-telemetry refusal claim is not unconditional.**

Changed contract, `docs/contracts/measurement_methodology.md:75`:

> “when the attempt's telemetry file is absent, empty or unparsable, the attempt refuses with `environment_admission_missing`.”

At `92c3e15a`, `_attempt_capture_interval` calls `read_authentication_text(..., grammar="jsonl", ...)` and catches only:

```python
except (OSError, UnicodeDecodeError):
    return None
```

During active v2 authentication, `authentication_io.py` instead executes:

```python
raise V2AuthenticationInputError(
    "v2_authentication_invalid_json",
    ...
)
```

**Reproduction:** V3 supplies `b"{\n"` as the idle file. Ordinary parsing returns `None`; authenticated parsing raises `v2_authentication_invalid_json`. I also reproduced that exception through `current_environment_refusals` using the candidate admission fixture. Qualify the contract’s reason-code claim for this earlier authentication failure.

**R2 — Seven added tests pass before the fixes.**

V2 runs the candidate tests against production code at `078a13a4`: **7/7 pass**.

- All three `AdmissionRoundingTests.test_r1_refuses_*` methods.
- All four `CooldownRoundingTests.test_r3_refuses_*` methods.

These cover duration/endpoint excesses, span/coverage deficits, missing samples, and cap-first behavior. They are useful preserved-behavior controls, but individually are not defect-shaped regressions under the requested criterion. Retain them alongside the discriminating positive cases.