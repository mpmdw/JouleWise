```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"Eight closures implemented; C4 needs a source-order ruling.","workspace":{"base_requested":"bd17126b","base_mode":"exact","head_start":"bd17126b","head_end":"bd17126b","upstream_end":"bd17126b","branch":"feat/2026-09-20-evidence-night-entry"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"partial","acceptance":"needs_ruling"},"verification":[],"flags":[{"id":"F1","kind":"lead_ruling","level":"blocking","text":"C4: clone import required before clone exists.","needs":"Rule on pre-clone constant source."}]}
```

## Change

Implemented C1–C3 and C5–C9 within WRITE_SCOPE. No commits. Tests used a local bare repository.

**NEEDS_RULING — C4:** A fresh preparation cannot import `PLAN_MAX_AGE_S` from its clone while refusing before creating that clone. Options considered:

- **Recommended:** import the entry checkout’s constant for the pre-clone check, then repeat the authoring check using the clone’s constant.
- Revise the before-clone requirement to allow obtaining H’s constant first.

C4 implementation and its counterfactual test remain blocked. Independent authorized work is complete. The next step is the lead’s ruling on that constant source.

All test names below are in `tests.test_evidence_night.PrepareTests`.

| Closure / production site | Test | Counterfactual at `bd17126b` → modified code |
|---|---|---|
| C1 — `locations` | `test_same_day_distinct_roots_and_staging` | FAIL: identical plan IDs → PASS; also checks branch names, probe labels, and `NightPlan` |
| C2 — selection filesystem check | `test_cross_device_refused_before_clone` | FAIL: no refusal → PASS |
| C3 — `sealed_candidate` | `test_sealed_candidate_checks_before_checkpoint`, `test_sealed_candidate_checks_on_resume` | Six subtest failures for syntax, manifest, and published-path corruption → PASS |
| C4 — not implemented | Blocked pending ruling | Not run |
| C5 — `prior_records` | `test_orphan_next_refused_before_resolution`, `test_orphan_custody_refused` | Two failures: resolution attempted / orphan accepted → PASS |
| C6 — `staging_lock`, documentation | `test_lock_precedes_first_staging_write` | FAIL: no concurrency refusal → PASS |
| C7 — `Refused`, `main` | `test_unexpected_builder_is_error_exit_one` | ERROR: uncaught `RuntimeError` → PASS |
| C8 — `notice`, attempt state | `test_notice_bindings_and_spans`; same-day test above | FAIL: missing chain-source details → PASS |
| C9 — interpreter and clone recipe | `test_preclone_recipe_and_runway_warning` | FAIL: missing warning → PASS; verifies version/fetch ordering and identity reuse |
| C9 — builder arguments | `ArgumentsTests.test_real_lock_verifier_and_builder_recipe` | Literal constraint/editable arguments verified; recipe already existed |

Requested verification:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night tests.test_evidence_arm_sequence tests.test_gen_evidence_night tests.test_night_plan_writer tests.test_install_night_agent
```

```text
Ran 107 tests in 183.661s

OK
```

The final composition test, rerun after restoring its original chain-invocation guard:

```text
Ran 1 test in 6.968s

OK
```

`git diff --check` passed. `git diff --stat`:

```text
 docs/contracts/evidence_night_entry.md |  47 +++++++---
 joulewise/evidence_night.py            | 161 ++++++++++++++++++++++++++-------
 tests/test_evidence_night.py           | 154 ++++++++++++++++++++++++++++++-
 3 files changed, 313 insertions(+), 49 deletions(-)
```

## Verification notes

Counterfactuals loaded `git show bd17126b:joulewise/evidence_night.py` into the imported module’s namespace with `exec(compile(...), entry.__dict__)`, then ran the new tests. Working files were not swapped.

C1–C3, C5, C7 baseline replay, exit 1:

```text
Ran 7 tests in 46.253s

FAILED (failures=10, errors=1)
```

C6, C8, C9 baseline replay, exit 1:

```text
Ran 3 tests in 14.634s

FAILED (failures=3)
```

For C3, baseline manifest/path corruptions reached installer validation after the wrapper checkpoint; syntax corruption was accepted. All three corruptions were accepted on completed resume after updating recorded digests. The new tests reject them at the requested sealed-candidate boundary.

No `pgrep` sandbox failure occurred. Logs: [requested suite](/tmp/evidence-night-verification.log), [primary counterfactuals](/tmp/evidence-night-counterfactual.log), [remaining counterfactuals](/tmp/evidence-night-counterfactual-nits.log).

## Residual risk

C4’s stale-at-t0 prevention remains open pending the ruling above. Offline verification establishes composition only; live evidence remains PROVISIONAL.