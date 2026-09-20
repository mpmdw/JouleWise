```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"NEEDS_RULING: verify.","workspace":{"base_requested":"7c377d72","base_mode":"exact","head_start":"7c377d72","head_end":"7c377d72","upstream_end":"4925d0e5","branch":"feat/2026-09-20-evidence-night-lifecycle"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md"],"unowned_dirty":[],"verdict":{"implementation":"partial","acceptance":"needs_ruling"},"verification":[],"flags":[{"id":"F1","kind":"lead_ruling","level":"blocking","text":"T3/step5 conflict.","needs":"Choose calendar evidence."},{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Full suite stopped; ps denied.","needs":"Lead replay."}]}
```

## Change

Implemented all four subcommands, offline tests, and contract documentation. Publication delegates probe/install to the existing installer, records attempts, and uses uninstall-first recovery with matching-byte restoration. No commits or out-of-scope repository changes.

**NEEDS_RULING — verification evidence source**

- **Question:** Does T3 require parsing calendars from `launchctl print` output, or is step 5’s LOADED check plus installed-plist calendar comparison authoritative?
- **Options:** Retain the implemented bench behavior; or add live-dump calendar parsing against a lead-approved output fixture.
- **Recommendation:** Retain step 5’s behavior. The existing `FakeLaunchctl` emits label/liveness output without calendars; the installer exposes typed liveness, without loaded-calendar verification.
- **Completed:** Pre-arm checks, publication/install/recovery, uninstall, and verification matching step 5.
- **Blocked:** Final `verify` acceptance and T3 interpretation. Resume with the chosen evidence contract.

## Verification notes

Commands and tails are supplied here to respect the 800-byte JSON-header limit. All commands ran from this worktree.

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night
Ran 43 tests in 124.877s
OK

PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_night.LifecycleTests
Ran 20 tests in 8.469s
OK

PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence tests.test_install_night_agent tests.test_arm_census tests.test_arm_retry
Ran 118 tests in 107.740s
OK
```

The 43-test run preceded the final recovery guard for an exception immediately after atomic publication. The subsequent 20-test run covered that guard and its new fault-injection test.

The composed test exercised the real shell installer with fake launchctl and a synthetic probe receipt. Its probe process census was injected because sandboxed `pgrep` cannot access sysmon. No live launchctl validation is claimed.

Canonical command:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests
```

Interrupted at the ruling gate, exit 130, terminal `KeyboardInterrupt`; no full-suite pass claimed.

Required orphan census returned exit 2:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans
{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}
```

`git diff --check` passed. HEAD stayed unchanged; upstream’s additional commit contains only brief 30.

## Residual risk

Notice transport, notice reading/veto integration, automated retry clearance, courier execution, and handbook replacement remain deferred. Courier availability is checked without invocation. Notice IDs are recorded verbatim without verification. Evidence remains PROVISIONAL; lead review and final verification remain outstanding.