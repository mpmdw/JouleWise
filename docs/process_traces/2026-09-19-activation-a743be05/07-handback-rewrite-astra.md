```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Pilot handback rewritten.","workspace":{"base_requested":"010ff2e0","base_mode":"exact","head_start":"010ff2e0","head_end":"010ff2e0","upstream_end":"0959e613","branch":"docs/2026-09-19-handback-evidence-pilot"},"pathspec":["docs/process/NIGHT_HANDBACK.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[],"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Test timeout and ps denial; see notes.","needs":"Lead verification."},{"id":"F2","kind":"residual_risk","level":"nonblocking","text":"Absent citations and log-path discrepancy; see notes.","needs":"Lead review."}]}
```

## Change

Rewrote the three sections for `qpe01-pilot-n1-20260920`, including plan-relative timing, literal `<H>`, evidence outputs, PROVISIONAL status and lead-only block-two authority. Appended the n2 harvest addendum following the existing pattern.

Byte comparison confirmed all pre-existing history, other sections, the standing suffix within Next lane and both generated ARM-RETRY-POLICY blocks remain unchanged. Only the authorized file changed; no commits or pushes.

`git diff --stat`:

```text
 docs/process/NIGHT_HANDBACK.md | 304 ++++++++++++++++++-----------------------
 1 file changed, 132 insertions(+), 172 deletions(-)
```

Exact test commands, all from this worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_retry
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_magistrate_watchdog
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night
```

Module tails, respectively:

```text
Ran 32 tests in 0.324s

OK
```

```text
Ran 96 tests in 2.472s

OK
```

```text
Ran 73 tests in 0.635s

OK
```

```text
Ran 226 tests in 143.528s

FAILED (failures=1, skipped=9)
```

## Verification notes

**F1 — Verification incomplete.** The failing test was `tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`. Exact assertion at `tests/test_run_night.py:4458`:

```text
AssertionError: external watchdog (8 s): bind supervisor blocked in journal_block
```

An isolated replay reproduced it:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go
```

```text
Ran 1 test in 8.006s

FAILED (failures=1)
```

This fixture failure does not assert handback content. No test change was established as necessary; none was made.

The required final census command exited 2:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans
```

```text
{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}
```

`git diff --check` passed. The full suite was omitted for this docs-only change; all four requested modules ran.

## Residual risk

**F2 — Sentences requiring lead review:**

- The Ed-ruling sentence and consult-06 citation rely on the supplied brief: activation directory `2026-09-19-activation-a743be05` is absent here. The requested ruling path is preserved.
- “Driver log: `<custody_root>/night.log`” follows `scripts/run_night.py:198` and the previous handback. The brief instead grouped `night.log` under `night/`.

Next: lead reviews those two points, replays the failing fixture and orphan census in its permitted environment, then performs the final diff gate and pathspec commit.