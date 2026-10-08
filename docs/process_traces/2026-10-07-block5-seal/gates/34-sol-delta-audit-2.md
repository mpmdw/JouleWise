```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "BLOCKERS FOUND: A1-A5 triggers are fixed, but two allowance-routing failures and one census parsing defect remain; 302 tests completed with one skip.",
  "workspace": {
    "base_requested": "fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7",
    "base_mode": "exact",
    "head_start": "fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7",
    "head_end": "fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7",
    "upstream_end": "fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7",
    "branch": "integrate/2026-10-07-int5"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "BLOCKERS FOUND",
    "audit_base": "43ac12d0ce554813278619b8e8e2331c9eb35be2",
    "original_checks": [
      {"id":"A1","result":"FIXED","evidence":"EXECUTED: explicit harvest-archive consumption returns survivor allowance 0.638333333 J; remaining routing gaps are R2/R3."},
      {"id":"A2","result":"FIXED","evidence":"EXECUTED: wrong-model spare emits member-specific model.identity_mismatch; correctly pinned references remain."},
      {"id":"A3","result":"FIXED","evidence":"EXECUTED: absent manifests retain end-3 contention loss and emit neg8.screen_failed."},
      {"id":"A4","result":"FIXED","evidence":"EXECUTED: node --require preload followed by the Claude package script remains a census hit."},
      {"id":"A5","result":"FIXED","evidence":"EXECUTED: strict-invalid end reference is excluded; rescreen evaluates and passes at 3/1/2 with no problems."}
    ],
    "findings": [
      {"id":"R2","severity":"blocker","file":"joulewise/floor_extraction.py","line":2951,"summary":"Floor extraction cannot forward the harvest archive required by HAZARD allowance consumption.","evidence":"EXECUTED fixture; READ caller plumbing"},
      {"id":"R3","severity":"blocker","file":"joulewise/whole_window.py","line":7422,"summary":"Stored NEG-8 failure vetoes a passing survivor screen before the claim reads its harvested allowance.","evidence":"EXECUTED harvest recovery and real validator/consumer probes with disclosed fixture seams"},
      {"id":"R1","severity":"should_fix","file":"joulewise/agent_identity.py","line":173,"summary":"Prefix-based flag parsing still mistakes a valid Node option operand for the script and drops an agent-package launch.","evidence":"EXECUTED live Node fixture, kernel inspection and census integration"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection",
      "cmd":"git status --porcelain=v1; git rev-parse HEAD '@{u}'; git diff --exit-code",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7","fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7"]},
      "expected":{"exit_code":0,"tail_regex":"fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7"}
    },
    {
      "id":"V2","kind":"suite",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_neg8_survivors tests.test_agent_identity tests.test_authentication_io tests.hazards.test_refusal_allowlist tests.flags.test_flags_exclusions",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK (skipped=1)","KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]},
      "expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}
    },
    {
      "id":"V3","kind":"suite",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_hazard_whole_window_verdict tests.test_hazard_neg8_mint_verdicts tests.test_whole_window tests.test_whole_window_selection tests.test_floor_extraction.EvaluationBasisPlumbingTests tests.test_write_b5_identity_pins",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"smoke",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/deltasol2/probe_delta2.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["A1_A2_A3_A4_A5_FIXED"]},
      "expected":{"exit_code":0,"tail_regex":"A1_A2_A3_A4_A5_FIXED"}
    },
    {
      "id":"V5","kind":"smoke",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/deltasol2/probe_regressions.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["REGRESSIONS_REPRODUCED"]},
      "expected":{"exit_code":0,"tail_regex":"REGRESSIONS_REPRODUCED"}
    },
    {
      "id":"V6","kind":"smoke",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/deltasol2/probe_survivor_barrier.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["SURVIVOR_BARRIER_REPRODUCED"]},
      "expected":{"exit_code":0,"tail_regex":"SURVIVOR_BARRIER_REPRODUCED"}
    },
    {
      "id":"V7","kind":"smoke",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/deltasol2/probe_harvest_and_identity.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["HARVEST_AND_REFERENCE_CONTROLS_PASSED"]},
      "expected":{"exit_code":0,"tail_regex":"HARVEST_AND_REFERENCE_CONTROLS_PASSED"}
    },
    {
      "id":"V8","kind":"lint",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" \"unlisted\": [],"," \"stale\": [],"," \"miscounted\": [],"," \"guard_changed\": [],"," \"scope_gaps\": []","}"]},
      "expected":{"exit_code":0,"tail_regex":"\"scope_gaps\": \\[\\]"}
    },
    {
      "id":"V9","kind":"lint",
      "cmd":"env TMPDIR=/private/tmp/deltasol2 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m joulewise.b5.reference_spares --check",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": [
    {
      "id":"G1","kind":"verification_gap","level":"nonblocking",
      "text":"The live pgrep ancestor test was skipped: sandboxed /usr/bin/pgrep returned exit 3, Cannot get process list. Kernel inspection and matcher tests ran.",
      "needs":"Repeat the raw census ancestor test in the lead's normal environment."
    },
    {
      "id":"G2","kind":"residual_risk","level":"nonblocking",
      "text":"Allowance probes use controlled row/replay, hazard-detector, calibration/session or energy seams as documented in the temporary scripts; they are not complete authenticated claim or live hardware validation. All started probe/test processes finished or were killed and reaped.",
      "needs":"Verify the repaired claim paths end to end before arming."
    }
  ]
}
```

## Findings

1. **R2 — blocker — HAZARD floors lose their allowance.** [floor_extraction.py:2951](/Users/edr/code/JouleWise-wt-int5/joulewise/floor_extraction.py:2951) calls `whole_window_drift_allowances` without an archive; `extract_cells` exposes no archive parameter. **Trigger:** a passing floor fixture evaluated as HAZARD. **Wrong output:** admitted count falls from `2` to `0`, floor becomes `null`, and `whole_window_drift_allowance_unrecorded` appears—even though explicit archive consumption returns `allowances`. **Minimal fix:** forward the archive through extraction and mint callers. **EXECUTED** with authentication barriers stubbed and HAZARD detection injected; missing plumbing confirmed by **READ**.

2. **R3 — blocker — Stored failure overrides survivor recovery.** [whole_window.py:7422](/Users/edr/code/JouleWise-wt-int5/joulewise/whole_window.py:7422) runs the original verdict refusal check before reading the harvested bracket; [line 6756](/Users/edr/code/JouleWise-wt-int5/joulewise/whole_window.py:6756) requires the stored screen to pass. **Trigger:** a contaminated end reference makes the stored screen fail, while dropping it produces passing survivors at `3/1/2`. The real harvest records `survivor_rescreen`, and its reader accepts that bracket. **Wrong output:** claim consumption returns `absent` with `whole_window_neg8_verdict_failed`; the harvest reader is called **zero times**. **Minimal fix:** authenticate the selected survivor screen in shared claim validation while retaining independent membership, provenance and physics checks. **EXECUTED** through harvest, validator and consumer functions with fixture seams; ordering confirmed by **READ**.

3. **R1 — should_fix — Another Node operand hides agents.** [agent_identity.py:173](/Users/edr/code/JouleWise-wt-int5/joulewise/agent_identity.py:173) treats every `--trace-*` option as operand-free. **Trigger:** `node --trace-require-module all …/@openai/codex/cli.js`, accepted by installed Node `v23.7.0`. **Wrong output:** `all` becomes the script; a live agent-package fixture is classified `not_agent`, and census integration returns clean exit `1`. **Minimal fix:** parse this operand and restrict operand-free recognition to known flags; unsupported forms should remain undecided. **EXECUTED** using actual Node and kernel argv inspection; child killed and reaped.

All original triggers were **FIXED**:

| Trigger | Executed result |
|---|---|
| A1 | Archive-aware consumer returns survivor allowance **0.638333333 J**. |
| A2 | Wrong-model spare receives member-specific identity loss. |
| A3 | Missing manifests preserve the known reference loss and fail the screen. |
| A4 | `--require preload` followed by Claude’s script remains a hit. |
| A5 | Strict-invalid reference is dropped; survivor screen passes at `3/1/2`. |

Allowance hash-replacement and arithmetic-mismatch controls passed. All six archived real-model reference identities recomputed to the sealed pin. No repository files changed.

## Residual risk

Raw `pgrep` ancestor coverage remains unverified because the sandbox denies process-list access. The 302-test focused runs completed with one skip. Probes establish function behavior under disclosed fixture seams; complete authenticated claim consumption and live hardware validation remain lead-owned checks before arming.