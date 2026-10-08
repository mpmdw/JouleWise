```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "BLOCKERS FOUND: five delta findings; 109 focused tests and two pinned-estimator tests passed.",
  "workspace": {
    "base_requested": "43ac12d0ce554813278619b8e8e2331c9eb35be2",
    "base_mode": "exact",
    "head_start": "43ac12d0ce554813278619b8e8e2331c9eb35be2",
    "head_end": "43ac12d0ce554813278619b8e8e2331c9eb35be2",
    "upstream_end": "43ac12d0ce554813278619b8e8e2331c9eb35be2",
    "branch": "integrate/2026-10-07-int5"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "BLOCKERS FOUND",
    "audit_base": "a434e363d",
    "audit_paths": ["joulewise", "scripts", "configs"],
    "findings": [
      {"id":"A1","severity":"blocker","file":"joulewise/b5/harvest.py","line":4636,"summary":"Accepted survivor re-screen does not replace the bracket consumed for claim allowances.","evidence":"EXECUTED fixture probe; READ consumer integration"},
      {"id":"A2","severity":"blocker","file":"joulewise/b5/harvest.py","line":1635,"summary":"A wrong-model spare occupies an unpinned consistency group and generates no reference-loss flag.","evidence":"EXECUTED"},
      {"id":"A3","severity":"blocker","file":"joulewise/b5/harvest.py","line":4676,"summary":"Missing or unreadable source manifests erase known reference-loss mappings and preserve the stored passing screen.","evidence":"EXECUTED"},
      {"id":"A4","severity":"should_fix","file":"joulewise/agent_identity.py","line":118,"summary":"Interpreter option operands are mistaken for scripts, allowing a real agent hit to become a clean census.","evidence":"EXECUTED with injected kernel identity"},
      {"id":"A5","severity":"should_fix","file":"joulewise/b5/harvest.py","line":4857,"summary":"Unexcluded re-derivation fails on a strict-invalid reference before the valid survivor screen can run.","evidence":"EXECUTED fixture and strict-result probes"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection","cmd":"git rev-parse HEAD '@{u}'","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["43ac12d0ce554813278619b8e8e2331c9eb35be2","43ac12d0ce554813278619b8e8e2331c9eb35be2"]},
      "expected":{"exit_code":0,"tail_regex":"43ac12d0ce554813278619b8e8e2331c9eb35be2"}
    },
    {
      "id":"V2","kind":"inspection","cmd":"git status --porcelain=v1","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V3","kind":"suite","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_neg8_survivors tests.test_agent_identity.AgentIdentityTests.test_executable_identity_rules tests.test_agent_identity.AgentIdentityTests.test_an_agent_package_script_run_by_its_real_path_is_an_agent tests.test_agent_identity.AgentIdentityTests.test_an_undecidable_line_stays_a_hit tests.hazards.test_refusal_allowlist tests.flags.test_flags_exclusions","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"test","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_controller_hazard_flags.EnvironmentGuardTests.test_item6_only_the_post_run_collector_raising_is_disclosed_not_failed tests.test_controller_hazard_flags.EnvironmentGuardTests.test_item6_ruling_the_pinned_reducer_barrier_still_fails_a_collector_raised_post_run","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V5","kind":"smoke","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/deltasol/probe_delta.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["DELTA_PROBES_REPRODUCED"]},
      "expected":{"exit_code":0,"tail_regex":"DELTA_PROBES_REPRODUCED"}
    },
    {
      "id":"V6","kind":"lint","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[" \"unlisted\": [],"," \"stale\": [],"," \"miscounted\": [],"," \"guard_changed\": [],"," \"scope_gaps\": []","}"]},
      "expected":{"exit_code":0,"tail_regex":"\"scope_gaps\": \\[\\]"}
    },
    {
      "id":"V7","kind":"lint","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m joulewise.b5.reference_spares --check","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    },
    {
      "id":"V8","kind":"suite","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_neg8_survivors tests.test_agent_identity tests.test_harvest_b5_p2harv tests.test_harvest_b5_p3harv tests.test_b5_chain_prune2 tests.test_b5_driver_p2 tests.test_b5_driver_p3 tests.hazards.test_refusal_allowlist tests.flags.test_flags_exclusions","cwd":".",
      "observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V9","kind":"suite","cmd":"env TMPDIR=/private/tmp/deltasol PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_neg8_survivors tests.test_agent_identity tests.test_harvest_b5_p2harv tests.test_harvest_b5_p3harv tests.test_b5_chain_prune2 tests.hazards.test_refusal_allowlist tests.flags.test_flags_exclusions","cwd":".",
      "observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    }
  ],
  "flags": [
    {"id":"G1","kind":"verification_gap","level":"nonblocking","text":"Broader suites encountered failures/timeouts and were interrupted without complete failure summaries. Systemwide ps was denied; pgrep reported sysmond unavailable.","needs":"Repeat driver and process-budget checks in the lead's normal test environment."},
    {"id":"G2","kind":"residual_risk","level":"nonblocking","text":"Allowance consumption was probed with authentication checks stubbed. Survivor re-screen was probed with injected strict-validation and source-resolution results. These are fixture evidence, not live hardware validation.","needs":"Verify repairs through authenticated claim consumers before arming."},
    {"id":"G3","kind":"environment","level":"nonblocking","text":"Direct signals to orphaned test monitors were denied with EPERM. Runners were stopped; temporary monitors expired. Final kernel inspection found all tracked test children and test groups absent.","needs":""}
  ]
}
```

## Findings

1. **A1 — BLOCKER — Survivor allowance never reaches claims.** At [harvest.py:4636](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:4636), a passing survivor re-screen releases the window, but its bracket remains in `withheld/neg8-rescreen-bracket.json`. [whole_window.py:7287](/Users/edr/code/JouleWise-wt-int5/joulewise/whole_window.py:7287) still consumes the original campaign-log bracket. Trigger: one end reference receives a physics loss, leaving passing counts 3/1/2. **Wrong output:** the consumer returns **0.593333333 J**, versus the required survivor allowance **0.638333333 J**. Contaminated reference/corpus values can likewise remain in the consumed bracket. **Minimal fix:** authenticate and bind the harvested survivor bracket and clean bound to the selected claim basis, then route shared allowance consumers through it. **EXECUTED** with authentication stubbed; consumer disconnect confirmed by **READ**.

2. **A2 — BLOCKER — Wrong-model spare escapes N8 identity losses.** [harvest.py:1635](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:1635) puts spares in a separate `.spares` stage. The identity checker at [harvest.py:5599](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:5599) gives that auxiliary group no sealed model pin. Trigger: one original start reference fails and its successful spare records a different model hash. **Wrong output:** `model_identity()` emits no flags, so no N8 loss removes the spare’s energy. The probe used the actual ALPHA roster and correctly pinned science identities. **Minimal fix:** bind every reference and spare to the expected reference-workload model/runtime identity and emit member-specific mismatch losses. **EXECUTED.**

3. **A3 — BLOCKER — Missing manifests silently erase a known loss.** The fallback at [harvest.py:4676](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:4676) names references only from decodable campaign manifests. Trigger: source resolution fails, those manifests are absent/unreadable, and the roster’s known end reference carries `contention.request_overlap`. **Wrong output:** losses become `{}`; [harvest.py:4616](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:4616) keeps the original passing screen without emitting `neg8.screen_failed`. **Minimal fix:** retain reference names from the sealed roster, including measured spares, so known losses trigger re-screening; unauthenticated sources must never supply a passing result. **EXECUTED.**

4. **A4 — MAJOR — Node option operands hide real agents.** [agent_identity.py:118](/Users/edr/code/JouleWise-wt-int5/joulewise/agent_identity.py:118) skips option tokens and treats the first remaining token as the script. Trigger: `node --require /tmp/preload.cjs …/@anthropic-ai/claude-code/cli.js`. **Wrong output:** the preload file is classified as the script, the genuine Claude hit becomes `not_agent_executable`, and census integration converts it to clean exit 1. **Minimal fix:** parse interpreter option operands and script positions; retain unsupported launch forms as undecided. **EXECUTED** with injected kernel identity. Window-path controls were correctly ignored.

5. **A5 — MAJOR — Strict-invalid reference prevents valid survivor recovery.** [harvest.py:4857](/Users/edr/code/JouleWise-wt-int5/joulewise/b5/harvest.py:4857) first re-derives without exclusions. Trigger: one end reference has a readable succeeded summary but fails strict validation; two valid end references remain. **Wrong output:** `rederivation_failed:bundle_strict_invalid` prevents the exclusion pass and yields a failed window screen, although direct survivor evaluation passes at 3/1/2. The verdict writer also returns `neg8_bracket_reference_invalid` for this shape. **Minimal fix:** consistently drop structurally strict-invalid references before aggregation in writer and replay, while preserving survivor authentication. **EXECUTED** using fixtures and an injected strict result.

## Residual risk

Full authenticated claim consumption and raw systemwide census were not verified. Broader driver/process-budget suites were interrupted after failures and timeouts in the restricted environment. The focused 109-test suite and both pinned-estimator tests passed.