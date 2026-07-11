# P2-041 Bounded Composition Fix Round (2026-07-10)

## Scope And Starting State

This run started from `impl/p2041` at WIP `[RED]` snapshot `d0bc777`.
The tree contains P2-041 branch work, main-post-PR-#48 content copied into the
tree without merge ancestry, and the Component C5
`window_evidence_precheck` rename. The preceding ultra-session result was
treated as uncorroborated. This run did not rebuild ancestry, commit, push,
open a PR, or run quiet-machine/hardware collection.

Fresh reproduction:

```text
python3 -m unittest tests.test_run_campaign
Ran 80 tests in 33.266s
FAILED (failures=6, errors=1)
```

The complete original output is retained outside the repository at
`/tmp/p2041-test_run_campaign-initial.txt` for this workspace session.

## Per-Failure Diagnosis

| Failure/error | Cause category | Root cause | Fix | File touched |
|---|---|---|---|---|
| `test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate` | stale test fixture/expectation | `write_strict_analysis_campaign` now defaults to the non-mock `wall_meter` backend for verifiable cooldown fixtures, but this test still expected the mock-backend reason. The runner correctly reported the unavailable wall-meter adapter. | Request `telemetry_backend="mock"` in this specifically mock-named test. | `tests/test_run_campaign.py` |
| `test_fake_cli_execution_logs_statuses_and_sequential_order` | stale fixture vs composed P2-042/P2-041 config-identity contract | The fake CLI rewrote experiment-member `workload_profile.repetitions` from the registered value `5` to `1`. P2-041 correctly classified those bundles with `config_manifest_mismatch`; alpha plus the intentionally failing beta reached `--max-failures 2`, so gamma was not invoked. | Preserve the source campaign repetition value in fake experiment-member configs. | `tests/test_run_campaign.py` |
| `test_fresh_experiment_run_then_second_invocation_skips` | stale fixture vs composed P2-042/P2-041 config-identity contract | All five fake member bundles recorded repetitions `1` instead of the registered `5`, so exit-zero execution failed closed on bundle/config identity. | Preserve the source repetition value in the fake CLI. | `tests/test_run_campaign.py` |
| `test_resume_after_partial_failure_sequence_skips_partial_on_second_run` | stale fixture vs composed P2-042/P2-041 config-identity contract | The first alpha experiment's fake members carried the same repetitions mismatch, so the runner correctly logged alpha as failed rather than ok/skipped. | Preserve the source repetition value in the fake CLI. | `tests/test_run_campaign.py` |
| `test_resume_skip_complete_experiment_records_member_counts` | stale fixture vs composed P2-042/P2-041 config-identity contract | The pre-existing experiment helper built members from `mock_local.json` instead of the registered campaign config, including repetitions `1` rather than `5`. | Make the helper accept the registered config path and retain its non-run-id fields. | `tests/test_run_campaign.py` |
| `test_sanitized_run_id_is_used_for_path_checks` | stale fixture vs P2-042 exact config identity | The fixture replaced raw config identity `Foo Bar` with its sanitized path component `foo-bar`. Real bundles retain `Foo Bar` in `config.json` while using directory `foo-bar`; the production exact-identity check correctly rejected the fixture. | Build the bundle from the registered source config and preserve the raw run ID when it sanitizes to the requested bundle path. | `tests/test_run_campaign.py` |
| `test_dry_run_plan_matches_real_mixed_state_actions` | stale fixture vs composed P2-042/P2-041 config-identity contract | Both pre-existing experiment fixtures were built from the wrong base config. The complete experiment therefore consumed one failure and the partial experiment consumed the second, so execution stopped before fresh and `order.log` did not exist. | Build both experiment fixtures from their registered config paths. | `tests/test_run_campaign.py` |

None of the seven failures exposed missing main-side P2-042 code after the
pre-union, and none required weakening or correcting the P2-041 production
verdict split. The fail-closed bundle/config binding was retained.

## Files Changed

- `tests/test_run_campaign.py`
- `RUN_STATE.md`
- `TASK_QUEUE.md`
- this report

No production source file changed in this bounded round.

## Verification

Focused module after the fix:

```text
Ran 80 tests in 35.072s

OK
```

Canonical suite:

```text
Ran 1020 tests in 62.462s

OK (skipped=12)
```

`git diff --check` also passed. The known
`test_telemetry_measure_idle_with_fake_nvidia_smi` machine-load flake did not
occur.

## Remaining Gate / Next Exact Step

The snapshot still lacks real merge ancestry for the pre-unioned main content.
The lead must rebuild P2-041 from `origin/main` (or otherwise recreate verified
ancestry), apply this bounded test-fixture diff with the P2-041 pathspecs, run
the full review stack, and rerun the focused and canonical suites before any
PR. This run found no unresolved main-vs-branch contract question within the
seven failures; it did not claim a complete review of the broader WIP tranche.
