```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Implemented","workspace":{"base_requested":"cea87cca","base_mode":"exact","head_start":"cea87cca","head_end":"cea87cca","upstream_end":"0982f7e","branch":"feat/2026-09-20-evidence-night-entry"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"See notes.","needs":""}]}
```

## Change

Implemented slice A: tracked `prepare`, checkpointed selection, detached clone, locked-venv recipe, clone-local authoring/generation, real installer render-only, schedule, frozen digests and notice draft.

Completed resumes preserve sealed bytes, mtimes and authoring time. Drift, foreign paths, symlinks, dirty checkouts and uncheckpointed outputs refuse reuse.

Ruling 22a is implemented: custody contains the wrapper, both sidecars and manifest; `night_plan.json` remains in staging.

Implementation choices:

- Retained date-only plan IDs; measurement, staging and custody names include time, epoch and full H.
- Offline composition injects the venv builder and lock verifier. Production exposes no bypass switch.
- Interrupted steps with conflicting uncheckpointed output refuse safely and preserve it.

No executor changes, network, mail, live launchctl, collection, commits or pushes occurred.

## Verification notes

**Final focused regression: exit 0.**

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night tests.test_evidence_arm_sequence tests.test_gen_evidence_night tests.test_night_plan_writer > /tmp/evidence-entry-focused-final.log 2>&1
```

```text
Ran 33 tests in 45.789s

OK
```

Coverage includes local bare-repository cloning, real generator and installer rendering, pinned defaults, same-day collisions, interruption/resume, preserved bytes/mtimes, every sealed-output drift check, refusals and forbidden-command argv checks.

**Delegated touched suite: exit 1.**

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier touched --since cea87cca5a68f6144abf9ef41a83179b0cfea670 > /tmp/evidence-entry-quick-suite.log 2>&1
```

```text
QUICK SUMMARY tier=touched modules=169 excluded=76 failures=3 seconds=931.499 result=FAIL
```

Three existing modules failed; isolated replays reproduced each failure group:

- `test_axi_controller_events`: two failures, “campaign start identity unavailable”; returned 2 instead of expected 1.
- `test_run_night`: bind-supervision `journal_block` exceeded its eight-second watchdog.
- `test_night_agent_install`: expected bootout-cleanup diagnostic was displaced by unavailable process census: `sysmond service not found` / `pgrep: Cannot get process list`.

Replay commands:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --module tests.test_axi_controller_events
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_agent_install.LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted
```

```text
SHARD SUMMARY index=1/1 modules=1 tests=7 failures=2 errors=0 skipped=0 result=FAIL

Ran 1 test in 8.007s
FAILED (failures=1)

Ran 1 test in 0.595s
FAILED (failures=1)
```

F1: No fresh production dependency installation was attempted under the no-network constraint. The real venv recipe and exact-lock comparison have unit coverage; composition uses the permitted interpreter-symlink seam. Full canonical-suite and live verification remain lead-owned under `docs/orchestration.md`. No out-of-scope repairs were made.

## Residual risk

Slice B retains the lifecycle façade, handbook/runbook checklist replacement and pre-arm discovery/census/ancestry/supervisor checks. Notice transport, acceptance/veto handling, publication, probe/install/verification and recovery remain deferred.

Next exact step: lead reviews the three-file diff and adjudicates the reproduced broader-suite failures before acceptance. Fixture success establishes composition only; live evidence remains PROVISIONAL.