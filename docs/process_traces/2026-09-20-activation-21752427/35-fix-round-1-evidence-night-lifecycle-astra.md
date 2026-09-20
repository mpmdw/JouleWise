```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"B1-B12 implemented; requested verification passes.","workspace":{"base_requested":"b678b1dc","base_mode":"exact","head_start":"b678b1dc","head_end":"b678b1dc","upstream_end":"b678b1dc","branch":"feat/2026-09-20-evidence-night-lifecycle"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"Canonical suite interrupted after sandbox identity failures.","needs":"Lead rerun where process identity probes are permitted."}]}
```

## Change

Implemented all twelve dictated closures, including foreign-job preservation, atomic lifecycle journals, clone-owned census classification, notice reuse refusal, rehearsal provenance, shared locking, and freshness checks. No repository commits, real launchctl operations, mail, or network operations.

Counterfactual tests loaded the `b678b1dc` module in memory without changing checkouts. Methods below belong to `LifecycleTests` unless qualified.

| Closure | Test methods | `b678b1dc` | Patched |
|---|---|---|---|
| B1 | `test_b1_check_rejects_foreign_jobs_plists_and_unknown`; `test_b1_rechecks_before_publication`; `test_b1_foreign_jobs_preserved_after_installer_refusal` | FAIL ×3 | PASS ×3 |
| B2 | `test_b2_malformed_uninstall_has_no_mutation` | FAIL | PASS |
| B3 | `test_b3_unresolved_raw_pid_reobserved_once` | FAIL | PASS |
| B4 | `PrepareTests.test_b4_prepare_check_prepare` | FAIL | PASS |
| B5 | `test_b5_atomic_json_preserves_previous_record_on_failure`; `test_b5_publishing_journal_precedes_plan_move` | FAIL ×2 | PASS ×2 |
| B6 | `test_b6_clone_old_census_literal_is_reported`; `test_b6_classification_runs_inside_clone` | FAIL ×2 | PASS ×2 |
| B7 | `test_b7_notice_reuse_across_same_day_candidates` | FAIL | PASS |
| B8 | `test_b8_fake_check_cannot_authorize_real_arm`; `test_b8_verify_records_launchctl_provenance` | FAIL ×2 | PASS ×2 |
| B9 | `test_b9_second_publication_is_refusal_not_error` | FAIL | PASS |
| B10 | `test_b10_prepare_lock_excludes_lifecycle` | FAIL | PASS |
| B11 | `test_b11_check_age_bound_and_cause_recorded` | FAIL | PASS |
| B12 | `test_b12_retained_plan_must_be_regular` | FAIL | PASS |

Requested verification:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night tests.test_evidence_arm_sequence tests.test_install_night_agent tests.test_arm_census tests.test_arm_retry
```

```text
Ran 180 tests in 278.936s

OK
```

Counterfactual replay:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/b1-counterfactual.py
```

```text
17 closure tests: 17 FAIL->PASS; 0 mismatches
```

`git diff --check` passed. `git diff --stat`:

```text
 docs/contracts/evidence_night_entry.md |  94 ++++++---
 joulewise/evidence_night.py            | 287 +++++++++++++++++++++------
 tests/test_evidence_night.py           | 343 ++++++++++++++++++++++++++++++---
 3 files changed, 617 insertions(+), 107 deletions(-)
```

## Verification notes

The additional canonical run (`python -B -m unittest discover -s tests`) was interrupted with exit 130 after four reproducible process-identity failures. This sandbox rejects `ps`; unchanged campaign code consequently reports `campaign start identity unavailable`. Shutdown also reported unavailable Metal access.

Isolated reproduction, using the prescribed interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_axi_controller_events tests.test_axi_mock_spec
```

```text
Ran 18 tests in 3.357s

FAILED (failures=4)
```

Those test modules, `scripts/run_campaign.py`, and `joulewise/measurement_liveness.py` are unchanged from `b678b1dc`. [Diagnostic tracebacks](/private/tmp/b1-campaign-diagnostic.log) and [counterfactual evidence](/private/tmp/b1-counterfactual.log) are retained.

## Residual risk

The step-5 filename/size/mtime baseline is explicitly deferred to B2, as authorized. Hardware evidence remains PROVISIONAL.

Next: lead reviews the three-file diff and reruns the canonical suite where process-identity probes are permitted.