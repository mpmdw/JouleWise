```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"partial",
  "summary":"No cross-unit code defect found at merged 58edfa29; 131 focused tests passed. Historical-reference nit; G4 and CI verification remain environment-limited.",
  "workspace":{
    "base_requested":"58edfa29",
    "base_mode":"exact",
    "head_start":"58edfa29128ba4494dfae10457780ae030c72b06",
    "head_end":"58edfa29128ba4494dfae10457780ae030c72b06",
    "upstream_end":"2ac5ceabf1b1f315fb819daf5178ce0301df59a1",
    "branch":null
  },
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "findings":[
      {
        "id":"F1",
        "severity":"nit",
        "file":"docs/process/state_kernel.json",
        "line":47,
        "text":"Old browser alternation survives as dated defect evidence, not executable/current argv. Adjacent line 48 retains historical source coordinates. Preserve the record."
      }
    ]
  },
  "verification":[
    {
      "id":"V1","kind":"inspection",
      "cmd":"git diff --stat 4b9a3411..58edfa29","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" joulewise/arm_readiness_evidence_t0.py  |   8 +-"," tests/test_arm_readiness_evidence_t0.py | 193 +++++++++++++++++++++++++++++++-"," 2 files changed, 197 insertions(+), 4 deletions(-)"]},
      "expected":{"exit_code":0,"tail_regex":"2 files changed, 197 insertions\\(\\+\\), 4 deletions\\(-\\)"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k g1 -k g2 -k g3","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 13.670s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3","kind":"suite",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_integration tests.test_arm_readiness_registry tests.test_arm_readiness_schemas tests.test_night_gate","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 128 tests in 214.461s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"inspection",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V5","kind":"smoke",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import joulewise.arm_readiness_evidence_t0 as t0; print(t0._BROWSER_CENSUS_PATTERN, t0._MONITOR_CENSUS_PATTERN)'","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$) powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)"]},
      "expected":{"exit_code":0,"tail_regex":"^/Contents/MacOS/"}
    },
    {
      "id":"V6","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k g4","cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found","pgrep: Cannot get process list","Ran 1 test in 1.223s","","FAILED (failures=2)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V7","kind":"other",
      "cmd":"gh run list --repo mpmdw/JouleWise --branch main --commit 58edfa29128ba4494dfae10457780ae030c72b06 --json databaseId,headSha,name,status,conclusion,url","cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["error connecting to api.github.com","check your internet connection or https://githubstatus.com"]},
      "expected":{"exit_code":0,"tail_regex":"^\\["}
    },
    {
      "id":"V8","kind":"inspection",
      "cmd":"git status --short","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags":[
    {"id":"E1","kind":"environment","level":"nonblocking","text":"Both G4 subcases fail at tests/test_arm_readiness_evidence_t0.py:2693 solely because sandbox pgrep returns 3; matching assertions are not reached.","needs":"Lead reruns G4 with Darwin process-list access."},
    {"id":"E2","kind":"verification_gap","level":"nonblocking","text":"gh is installed but API connection failed; every main CI job status is unknown.","needs":"Lead retrieves the CI run and every job status for exact SHA 58edfa29."},
    {"id":"E3","kind":"baseline_drift","level":"nonblocking","text":"Local origin/main advanced concurrently from 58edfa29 to 2ac5ceab; detached review HEAD remained 58edfa29. No fetch performed.","needs":""}
  ]
}
```

## Findings

No blocker or should-fix code/config defect; no documentation quotes either complete old argv as current fact.

**F1 — nit:** `docs/process/state_kernel.json:47,48` contains historical defect evidence and source coordinates. Line 47 says the old alternation “matched five always-present Apple XPC services with no browser open.” It does not install that pattern.

Every hit from the five requested literal searches, grouped by classification:

- **Current code, compatible:** `joulewise/arm_readiness.py:1111,1174`; `joulewise/arm_readiness_evidence_t0.py:57,113,130,1724,1735,1958`. These define the new browser pattern, row/predicate mappings and shared derivation.
- **Current tests, compatible:** `tests/test_arm_readiness_evidence_t0.py:2538` pins the new browser argv; `tests/test_arm_readiness_registry.py:83` lists the required row.
- **Current config, compatible:** `configs/arm_readiness/d117_row_registry_v1.json:35,76,117,393,397`; `configs/arm_readiness/d117_row_registry_v2.json:493,572,613,654,930,934`. Row identifiers and applicability remain valid; no old patterns.
- **Current documentation, compatible:** `docs/phase_2/gamma_arm_readiness.md:69`, `beta_arm_readiness.md:63`, `alpha_arm_readiness.md:138`, `window_c_operator_checklist.md:201`, `window_runbook.md:37`. These state process-absence policy or pending evidence, not obsolete argv.
- **Historical — F1:** `docs/process/state_kernel.json:47,48`.
- **Acceptance requirement, not argv:** `docs/process/state_kernel.json:55`.

Exact searches for both complete old patterns returned **no hits**, rc 1. Searches covered all seven requested roots; excluded historical directories were not searched.

Additional consumer inspection confirmed unchanged `PROCESS_CENSUS` evidence/time-bound semantics and independent rehearsal/teardown censuses. Both scripts imported cleanly; identity assertions confirmed the same author function/module:

```text
desk/night imports: OK; shared T0 author
```

Caller locations: `scripts/author_arm_evidence_t0.py:17,43` and `scripts/run_night.py:43,1135`. The transaction-pack dispatch remains at `scripts/run_night.py:1498`. Both specified merge parents match. Final `git status --short` is empty.

## Residual risk

What the lead should double-check: rerun G4 with permitted process-list access and retrieve every CI job at **58edfa29**, not the subsequently advanced main. No live readiness authoring or quiet-machine measurement was performed; focused fixture tests do not establish that live gate.