```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"C4 added; C1-C9 tested.","workspace":{"base_requested":"bd17126b","base_mode":"exact","head_start":"bd17126b","head_end":"bd17126b","upstream_end":"bd17126b","branch":"feat/2026-09-20-evidence-night-entry"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"Random t3 fixture collision; see notes.","needs":""}]}
```

## Change

Preserved the pre-existing C1–C3 and C5–C9 changes. Added only C4: the running checkout’s pre-clone age check, H’s binding authoring check using the stored authoring timestamp, two counterfactual tests, and contract documentation. No commits.

All test names below are in `tests.test_evidence_night`; class is `PrepareTests` unless specified.

| Closure | Test | Counterfactual at `bd17126b` → working tree |
|---|---|---|
| C1 — candidate identity | `test_same_day_distinct_roots_and_staging` | FAIL: identical date-only IDs → PASS: distinct IDs, results branches and admissible probe labels/plans |
| C2 — atomic publication | `test_cross_device_refused_before_clone` | FAIL: no refusal → PASS: different `st_dev` refuses before clone |
| C3 — sealed assertions | `test_sealed_candidate_checks_before_checkpoint`; `test_sealed_candidate_checks_on_resume` | Six failing subtests → all PASS for repaired-sidecar syntax corruption, manifest corruption and staged-plan literal |
| C4 — age at t0 | `test_t0_beyond_max_age_refused_before_clone`; `test_clone_authoring_max_age_binds_before_plan_write` | Both FAIL: no refusal → both PASS; no clone for `now + 130000`, no plan write under monkeypatched clone limit |
| C5 — orphan detection | `test_orphan_next_refused_before_resolution`; `test_orphan_custody_refused` | Both FAIL → both PASS, naming orphan and blocking default resolution |
| C6 — lock ordering/docs | `test_lock_precedes_first_staging_write`; contract inspection | FAIL: no refusal → PASS: contention refuses without candidate staging directory; refusal/reuse wording present |
| C7 — defects versus refusals | `test_unexpected_builder_is_error_exit_one` | ERROR: uncaught `RuntimeError` → PASS: exit 1, `ERROR:` and traceback |
| C8 — notice draft | `test_notice_bindings_and_spans`; same-day test | FAIL: missing source binding → PASS: digests, span triples, attempt count and prior candidates |
| C9 — recipe/identity/runway | `test_preclone_recipe_and_runway_warning`; `ArgumentsTests.test_real_lock_verifier_and_builder_recipe` | Recipe/warning test FAIL → PASS. Builder assertion PASS on both versions; it confirms existing correct arguments |

Counterfactual execution loaded the original module **in memory**, preserving working-tree bytes:

```python
baseline = types.ModuleType('joulewise.evidence_night')
source = subprocess.check_output(
    ['git', 'show', 'bd17126b:joulewise/evidence_night.py'], text=True)
exec(compile(source, 'bd17126b:joulewise/evidence_night.py', 'exec'),
     baseline.__dict__)
tests.entry = baseline
```

The 13 named tests above ran through `unittest` with the supplied interpreter and bytecode disabled. Exact tails:

```text
# Baseline module; exit 1
Ran 13 tests in 71.495s

FAILED (failures=15, errors=1)

# Working-tree module; exit 0
Ran 13 tests in 53.211s

OK
```

`git diff --check` passed. Requested `git diff --stat`:

```text
 docs/contracts/evidence_night_entry.md |  57 ++++++++--
 joulewise/evidence_night.py            | 178 +++++++++++++++++++++++-------
 tests/test_evidence_night.py           | 191 ++++++++++++++++++++++++++++++++-
 3 files changed, 374 insertions(+), 52 deletions(-)
```

## Verification notes

The full requested command ran **once**, exit 1:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night tests.test_evidence_arm_sequence tests.test_gen_evidence_night tests.test_night_plan_writer tests.test_install_night_agent
```

It encountered one random fixture-name collision, not a `pgrep` sandbox failure:

```text
ERROR: test_dirty_clone_interpreter_drift_and_unknown_remote_head
```

The generator refused because the generated directory `case-qa4uqbt3` contained the forbidden census substring `t3`.

```text
Ran 109 tests in 185.398s

FAILED (errors=1)
```

The affected test passed unchanged when rerun alone:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_evidence_night.PrepareTests.test_dirty_clone_interpreter_drift_and_unknown_remote_head
```

```text
Ran 1 test in 7.457s

OK
```

## Residual risk

The existing random fixture-name collision remains; the C4-only ruling did not authorize changing that fixture setup. Acceptance remains pending a clean full-suite result.

Next exact step: lead reviews the preserved three-file diff and reruns the full verification command above.