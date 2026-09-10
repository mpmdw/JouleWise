```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three documentation findings; arithmetic, test-file structure, reference census, and range scope are clean.",
  "workspace": {
    "base_requested": "8da99190",
    "base_mode": "informational",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "reviewed_range": "8da99190..58d4696b",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/contracts/measurement_methodology.md",
        "line": 308,
        "summary": "The unconditional 10 microsecond coverage-deficit refusal claim exceeds what the predicate guarantees."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "docs/contracts/measurement_methodology.md",
        "line": 307,
        "summary": "Evidence end and clipped start are named but not defined, so the paragraph does not meet the requested replication and first-use bar."
      },
      {
        "id": "F3",
        "severity": "nit",
        "path": "docs/contracts/measurement_methodology.md",
        "line": 74,
        "summary": "The admission paragraph incorrectly describes both containment comparisons as comparisons between epoch timestamps."
      }
    ],
    "item_checks": {
      "1": "F1-F3. The coverage allowance's summation structure otherwise matches the code, and ULP is expanded at first use.",
      "2": "No finding: ceil(75/0.1)=750; 750*0.115=86.25 seconds; MIN_RATE_FIT_BASELINE_S=60; 75 seconds gives 25 percent margin; 750 exceeds 303.",
      "3": "No finding: 13 test methods, no unused imports, obsolete class/imports removed, shifts are -1e-5 and +1e-5 seconds, and the expected tuple exactly matches the production refusal string.",
      "4": "No finding: the requested path census found site rendering/source-stamp references and fixture references, with no pinned digest or numeric line reference. The 28 read-only docs-freshness tests passed.",
      "5": "No finding: only the three requested files changed; 32 insertions and 28 deletions."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 8da99190..58d4696b; git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "3 files changed, 32 insertions(+), 28 deletions(-)",
          "## HEAD (no branch)",
          "078a13a461abd124c29796798da5107fe00190a6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "078a13a461abd124c29796798da5107fe00190a6"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import ast, json, pathlib, subprocess, types\nimport joulewise.controller as c\nfrom joulewise.clock import FakeClock\nfrom joulewise.schemas import BenchmarkConfig, CooldownPolicy, IdleBaseline, TelemetryBackend\nsrc=subprocess.check_output(['git','show','58d4696b:joulewise/controller.py'],text=True,stderr=subprocess.DEVNULL)\nnode=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=='cooldown_gate')\nexec(compile(ast.Module(body=[node],type_ignores=[]),'<58d4696b cooldown_gate>','exec'),c.__dict__)\nclock=FakeClock(1789000000.)\nconfig=BenchmarkConfig.from_mapping(json.loads(pathlib.Path('configs/examples/mock_local.json').read_text()))\nreference=IdleBaseline(5.,0.,30.,30,TelemetryBackend.POWERMETRICS)\nclass Telemetry:\n    def measure_idle(self, config):\n        clock.sleep(.75)\n        return IdleBaseline(5.,0.,.6-1e-5/40,6,TelemetryBackend.POWERMETRICS)\n    def thermal_state(self, config): return types.SimpleNamespace(thermal_pressure='nominal')\nr=c.cooldown_gate(Telemetry(),reference,config,clock,policy=CooldownPolicy.from_mapping({'subwindow_s':.75}))\nprint(r['result'],r['window_span_s'],r['window_coverage_s'],(24-r['window_coverage_s'])*1e6)\nassert r['result']=='recovered' and 24-r['window_coverage_s']>1e-5\n\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "recovered 30.0 23.99998664855957 13.3514404296875"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "recovered 30\\.0 23\\.99998664855957 13\\.3514404296875"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import ast, subprocess; s=subprocess.check_output(['git','show','58d4696b:tests/test_gate_sensibility_rounding.py'],text=True); t=ast.parse(s); names={a.asname or a.name.split('.')[0] for n in ast.walk(t) if isinstance(n,(ast.Import,ast.ImportFrom)) and getattr(n,'module',None)!='__future__' for a in n.names}; used={n.id for n in ast.walk(t) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}; print('tests',sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(t))); print('unused',sorted(names-used))\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests 13", "unused []"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests 13\\nunused \\[\\]"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Five admission tests and three docs-freshness tests require temporary filesystem writes and were not executed under the read-only sandbox. Eight rounding tests and 28 docs-freshness tests passed. The canonical suite was not run.",
      "needs": "Lead should run both complete focused modules at 58d4696b in a writable test environment."
    }
  ]
}
```

## Findings

**F1 — should_fix: qualify the 10 μs refusal claim.**  
At `58d4696b`, methodology lines 308–309 promise refusal for a 10 μs coverage deficit without limiting the policy or contribution count. V2 reproduces recovery with a valid `subwindow_s=0.75` policy, 40 positive contributions, and **13.3514404296875 μs missing coverage**. The summed endpoint allowance grows with the number of contributions; it has no fixed 10 μs ceiling. Qualify the example to its tested configuration or remove the categorical coverage claim. The span claim remains supported.

**F2 — should_fix: define the endpoint terms.**  
Methodology lines 305–308 define ULP but leave “evidence end” and “clipped start” undefined. Reproduce by comparing:

```sh
git show 58d4696b:docs/contracts/measurement_methodology.md | sed -n '294,309p'
git show 58d4696b:joulewise/controller.py | sed -n '2497,2531p'
```

The reader needs the code’s definitions: evidence end is the post-capture time; evidence start is bounded by capture start; clipped start is `max(evidence_start, window_cutoff)`. Only strictly positive overlaps contribute endpoint ULPs. The stated sum otherwise correctly includes **both endpoint ULPs per contribution, then one coverage-sum ULP**, with a 1 μs minimum.

**F3 — nit: distinguish duration and timestamp comparisons.**  
Methodology lines 74–76 say both comparisons are between epoch timestamps and describe both as sampler sums against endpoint differences. Reproduce with:

```sh
git show 58d4696b:joulewise/environment_admission.py | sed -n '175,192p'
```

The first comparison is **baseline duration versus attempt duration**; the capture checks compare **epoch endpoints**. Separate those explanations.

Items **2, 3, 4, and 5: no finding**, as detailed in the envelope. Exact range statistics:

```text
 docs/contracts/measurement_methodology.md | 25 ++++++++++++++++++-------
 scripts/generate_g2a_probe_inputs.py      |  8 +++++---
 tests/test_gate_sensibility_rounding.py   | 27 +++++++++------------------
 3 files changed, 32 insertions(+), 28 deletions(-)
```

## Residual risk

Execution coverage is limited as recorded in R1. Revision-sensitive production modules and rounding tests were loaded from Git into memory; docs-freshness checks used in-memory overlays for the changed contracts. No files were changed, and no live hardware validation was performed.