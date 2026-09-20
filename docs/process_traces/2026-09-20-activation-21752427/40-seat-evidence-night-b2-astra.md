```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"B2 implemented; NEEDS_RULING on test timeout.","workspace":{"base_requested":"ff623dc8","base_mode":"exact","head_start":"ff623dc8","head_end":"ff623dc8","upstream_end":"3c454c1b","branch":"feat/2026-09-20-evidence-night-b2"},"pathspec":["joulewise/evidence_night.py","tests/test_evidence_night.py","docs/contracts/evidence_night_entry.md","docs/process/NIGHT_HANDBACK.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"needs_ruling"},"verification":[],"flags":[{"id":"F1","kind":"verification_gap","level":"blocking","text":"Bind-supervision timeout; see notes.","needs":"Lead ruling"}]}
```

## Change

Implemented all requested B2 code and documentation:

- `notice` validates sealed state and fresh check evidence, refreshes the draft, prints it, and writes `lifecycle/notice-draft.txt`.
- `veto` records owner directives, standdown, STOP, and manual mailbox-NO relay evidence. Failures refuse; every channel is observed.
- Publication additionally requires fresh, clear, preparation-bound veto evidence.
- Successful installation records the recursive custody baseline; `verify` reports additions, removals, and metadata changes.
- Handbook adds the command sequence and record-17 fallback.

No commits, network requests, mail, live launchctl, or measurements occurred.

**Argv/stdin inventory:** Every call below retains clone cwd.

| Clone-side operation | Arguments following `P -B -c CODE` | stdin |
|---|---|---|
| Plan authoring | None | Preparation JSON |
| Census observation/classification | None | Request/observation JSON |
| Retry routing | None | Records JSON |
| Interpreter identity | None | None |
| Sealed checks, plan-age validation, both schedule calls | Plan path | None |
| Job discovery | Launchctl executable | None |
| Installed-job verification | Plan, launchctl executable, render directory, interpreter | None |

Tests spy on `input=` and argv; a real clone-side census round-trip also passes a 300 KB record.

**Verification evidence:** Commands ran from the supplied cwd. Set:

```sh
P313=/Users/edr/code/JouleWise/.venv/bin/python
P311=/opt/homebrew/bin/python3.11
```

| Replay command | Exit | Exact result tail |
|---|---:|---|
| `PYTHONDONTWRITEBYTECODE=1 "$P313" -B -m unittest tests.test_evidence_night` | 0 | `Ran 78 tests in 231.256s` / `OK` |
| `PYTHONDONTWRITEBYTECODE=1 "$P311" -B -m unittest tests.test_evidence_night` | 0 | `Ran 78 tests in 214.061s` / `OK` |
| `git diff --check` | 0 | Empty |

The final three added/extended tests were replayed separately on both interpreters:

```sh
PYTHONDONTWRITEBYTECODE=1 "$P313" -B -m unittest \
  tests.test_evidence_night.LifecycleTests.test_census_and_retry_json_travel_on_stdin \
  tests.test_evidence_night.LifecycleTests.test_veto_cli_refusal_and_json_output \
  tests.test_evidence_night.PrepareTests.test_real_composition_idempotence_and_never_invokes
```

Exit 0: `Ran 3 tests in 9.902s` / `OK`. Same command with `"$P311"`: exit 0, `Ran 3 tests in 8.902s` / `OK`.

Pre-change baseline: 69 tests, `OK`.

Protected handbook regions remain byte-identical to HEAD. MD5s:

- Ten concatenated `Executed` blocks: `8b4a3a006e214855be93c5282a695b5a`
- ARM-RETRY-POLICY: `b9c2bda9817c14cf81a6412820385246`

## Verification notes

This requested related-suite command exited 1:

```sh
PYTHONDONTWRITEBYTECODE=1 "$P313" -B -m unittest \
  tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_night_gate \
  tests.test_magistrate_watchdog tests.test_run_night
```

Tail: `Ran 432 tests in 158.705s` / `FAILED (failures=1, skipped=9)`.

Sole failure:

```text
tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go
AssertionError: external watchdog (8 s): bind supervisor blocked in journal_block
```

It reproduced without concurrent suites:

```sh
PYTHONDONTWRITEBYTECODE=1 "$P313" -B -m unittest \
  tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go
```

Exit 1: `Ran 1 test in 8.007s` / `FAILED (failures=1)`.

The test, subprocess fixture, and driver have no working-tree changes. That suggests independence from B2 but does not establish the cause. Verification followed the brief’s specified modules rather than full discovery.

**NEEDS_RULING:** Should this unchanged-path timeout receive a separate investigation, or may B2 proceed with the failure explicitly carried?

- **Options:** investigate separately before acceptance; or accept B2’s focused evidence with a recorded verification gap.
- **Recommendation:** separate investigation; preserve this bounded patch.
- **Completed:** all requested implementation and authorized checks.
- **Blocked:** acceptance pending disposition of the reproducible timeout.

## Residual risk

Fixture evidence remains PROVISIONAL. First live use and final verification remain lead-owned.