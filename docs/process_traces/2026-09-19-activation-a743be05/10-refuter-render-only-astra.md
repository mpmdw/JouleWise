```json
{"schema":"claude-codex-report/v1","genre":"review","status":"blocked","completion":"partial","summary":"Behavioral mutants killed; one pre-existing sweep finding.","workspace":{"base_requested":"a997d30178fb2cb3239f83d779403660859c1146","base_mode":"exact","head_start":"a997d30178fb2cb3239f83d779403660859c1146","head_end":"a997d30178fb2cb3239f83d779403660859c1146","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix","file":"scripts/run_night.py:624"}]},"verification":[],"flags":[{"id":"R1","kind":"lead_ruling","level":"blocking","text":"04a is outside the allowed read boundary.","needs":"Permit its read or provide text."}]}
```

## Findings

**F1 — should_fix, pre-existing: foreign calibration artifacts affect evidence-night results.**  
[scripts/run_night.py:624](/Users/edr/code/JouleWise-wt-refute-renderonly/scripts/run_night.py:624), called unconditionally at line 3198, selects calibration-refusal interpretation from file existence. Installer admission at [night_agent_install.py:1129](/Users/edr/code/JouleWise-wt-refute-renderonly/joulewise/night_agent_install.py:1129) does not reject that artifact.

I placed `{}` in a valid evidence fixture’s `night/calibration-refusal.json`. Real `validate_install` accepted it; `_calibration_refusal(..., chain_exit_code=0)` returned a calibration refusal. This site also exists at `0959e613`.

Executed, exit **0**:

`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-refute-evidence-01/foreign_artifact.py`

Output tail:

```text
INSTALL_ACCEPTED_WITH_FOREIGN_CALIBRATION_ARTIFACT
SUCCESSFUL_EVIDENCE_CHAIN_WOULD_MAP_TO={"detail": "document_invalid", "evidence": {"error": "schema, plan_id, code, or exit_code mismatch", "path": "/private/tmp/jw-refute-evidence-01/round2/arm-fixture/custody/night/calibration-refusal.json", "payload": {}, "raw": "{}\n"}, "reason": "night_calibration_refused"}
```

Reject foreign artifacts during admission or make their interpretation depend on payload kind. Full night execution was not attempted.

**E1 — independently composed execution passed.**

Executed, exit **0**:

`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-refute-evidence-01/round2/arm.py`

This standalone script does not invoke the arm-sequence test or its fixture class. It authors a fresh v2 plan and executes byte-identical copies of the reviewed production files. [Exact subprocess commands, stdout JSON, stderr, and exit codes](/tmp/jw-refute-evidence-01/round2/arm-results.json).

| Operation | Exit/result |
|---|---|
| Fixture Git initialization, configuration, commit, HEAD lookup | All 0 |
| `gen_evidence_night.py --render-only` | 0 |
| Actual `install_night_agent.sh --plan STAGED --python PY --render-only DIR` | 0; three plists |
| `os.replace` publication | Completed; plan bytes unchanged |
| Actual shell render from published path | 0; three plists |
| `evidence_probe_bindings` | 0 |
| Real `run_night.probe_night` supervisor | 0 |
| `validate_probe_receipt` | 0 |
| `validate_install` | 0 |

Both renders printed `payload_kind="quiet_predicate_evidence"` and chain SHA `057357e729c148b6ff6e5768a867958aefd421c779e7681eb9dbde2e91dee2b6`. Their `input_digests` match the real bindings after replacing the staged plan-path key with the published key. Manifest and wrapper artifacts remained unchanged.

**Plists are not all byte-identical:** night and deadman match exactly. The probe plist changes `--plan`, pending-receipt path, and stdout/stderr paths from staging to custody. Exact differences are in [arm.log](/tmp/jw-refute-evidence-01/round2/arm.log).

The receipt reports supervisor PID **34048**, worker PGID **34060**, `outcome="ok"`, `verify_only=true`, `collect_started=false`, and `load_started=false`. Only `_probe_group_absent` was patched; supervisor, worker, verify-only chain, termination, and reaping executed. No night records were produced.

The initial standalone attempt omitted the runtime dependency `tests/fixtures/night_plan_v1_retired.json`. Both shell renders and `validate_install` exited **1**; generator, bindings, supervisor, and receipt validation exited **0**. Exact terminal error:

```text
RuntimeError: retired-v1 fixture is unavailable: [Errno 2] No such file or directory: '/private/tmp/jw-refute-evidence-01/arm-fixture/measurement/tests/fixtures/night_plan_v1_retired.json'
```

The successful repetition used a fresh fixture containing that dependency. [Initial results](/tmp/jw-refute-evidence-01/arm-results.json).

**E2 — all seven requested behavioral mutations were KILLED.**

Executed mutation harness, exit **0**:

`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-refute-evidence-01/mutants.py`

Each targeted test subprocess used `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v TEST` in `/private/tmp/jw-refute-evidence-01/mutation-repo`. All seven unmodified baseline tests passed. Each behavioral mutant’s named test exited **1**.

For rows a–c and e, class prefix is `tests.test_night_agent_install.EvidenceRenderOnlyTests`.

| Mutant | Killing test | Failure tail |
|---|---|---|
| a: evidence falls through to legacy execution | `test_staged_and_published_render_hash_same_bytes_without_chain_execution` | `render-only executed the evidence chain` |
| b: ambiguous declaration falls through | `test_ambiguous_payload_refuses_before_legacy_inspection` | `Expected 'reservation_input_digests' to not have been called. Called 1 times.` |
| c: remove sealed-literal guard | `test_wrong_published_literal_refuses_before_plists` | `AssertionError: 0 != 2` |
| d: restore cwd-relative registration read | `tests.test_night_gate.EvidenceRegistrationTests.test_evidence_registration_is_relative_to_measurement_root_from_tmp` | `AssertionError: 'REFUSED' != 'GO'` |
| e: skip sidecar comparison | `test_wrong_chain_sidecar_refuses_render` | `AssertionError: 0 == 0` |
| f: execute calibration chain twice | `tests.test_install_night_agent.InstallNightAgentTests.test_calibration_render_executes_chain_exactly_once_in_argv_mode` | `AssertionError: 2 != 1` |
| f: reverse calibration JSON key order | `tests.test_install_night_agent.InstallNightAgentTests.test_calibration_render_input_digest_output_bytes_unchanged` | `First differing element 0:` / `FAILED (failures=1)` |

The key-order mutation was executed separately by:

`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-refute-evidence-01/keyorder.py`

Harness exit **0**, mutant test exit **1**. Removing `sort_keys` alone proved equivalent because `reservation_input_paths` already sorts paths; reversing the emitted order produced the actual behavioral mutation.

[Mutation results](/tmp/jw-refute-evidence-01/mutant-results.json), [key-order output](/tmp/jw-refute-evidence-01/keyorder.log).

**E3 — calibration success behavior preserved.**

The harness compared the baseline and current calibration success/fallback AST, accounting for the added exception wrapper:

```text
CALIBRATION_SUCCESS_AST_IDENTICAL=True
```

The golden stdout and exactly-once spy tests passed unmodified; the spy checks `NIGHT_RESERVATION_ARGV_ONLY=1`.

Executed in the disposable repository:

`/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_install_night_agent.InstallNightAgentTests`

Exit **0**:

```text
Ran 63 tests in 99.644s

OK
```

This includes the `/bin/true` fixtures.

**E4 — same-signature sweep completed within execution restrictions.**

Besides F1, no further calibration-artifact-existence dispatch reachable by evidence plans was found in the three requested files. Probe and receipt validation select payload kind; uninstall does not inspect calibration artifacts. Courier refusal inventory includes calibration documents but does not select a calibration execution path.

Executed `/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-refute-evidence-01/sweep.py`, exit **0**. Tail:

```text
refusal_inventory=["calibration-refusal.json"]
courier_argv_has_calibration_tokens=False
SWEEP exit=0; no collection or courier execution
```

**E5 — requested suite completed, exit 1; sole failure environmental.**

Executed with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp`:

`/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence tests.test_night_agent_install tests.test_gen_evidence_night tests.test_night_gate tests.test_install_night_agent`

Output was captured to [suite.log](/tmp/jw-refute-evidence-01/suite.log), then `tail -8` displayed while preserving the suite exit status:

```text
    self.assertIn("probe bootout absence unproven", str(caught.exception))
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'probe bootout absence unproven' not found in 'probe process census survivor or unknown:  sysmon request failed with error: sysmond service not found\npgrep: Cannot get process list\n'

----------------------------------------------------------------------
Ran 225 tests in 1035.633s

FAILED (failures=1)
```

Failure: `tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`.

## Residual risk

- **R1 — NEEDS_RULING:** the named 04a document resides in another worktree, conflicting with the explicit prohibition on touching other worktrees. The clarification remains unanswered. Options: permit reading that single file, or supply its contents. Recommend the single-file read exception. E1–E5 execution is complete; exact R1–R5/addendum adjudication remains blocked.
- The probe used the authorized census seam; its `cleanup_proven` value is fixture evidence, not live host-census validation. No live launchctl, collection, courier, or network operation was performed.
- All-three-plist byte identity does not hold. Lead should adjudicate the probe-plist difference against 04a.
- Worktree remains clean and detached at the requested head. All session writes are under `/tmp`.