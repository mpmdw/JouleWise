# A267 fix round 1 — DELTA re-audit, EXECUTION lens (Opus)

Worktree `/Users/edr/code/JouleWise-wt-a267-review3`, detached at **62412ee6**,
tree clean before and after. Baseline of the three brief modules at the fix head:
`Ran 224 tests in 57.132s / OK` (exit 0). Same after every mutation was restored.
All findings below were produced by executing code, not by reading it.

## BLOCKER

**B1 — item 2 (05b S1): the header guard's premise is unevidenced, and on the
real pilot night it governs the MAJORITY of envelopes.**
`joulewise/quiet_predicate_campaign.py:443-457` asserts that `log show --style
syslog` "prints [the header] even when nothing matched the predicate", citing
exhibit D. Exhibit D is a *non-empty* query (178 entry lines), so it proves only
that a matching query emits the header. I measured the real corpus:

```
$ python3 -  # over tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt
entry lines: 178 span: 2026-09-22 02:28:08 -> 2026-09-22 04:07:36
per-602s-window counts (12 slots at 620 s pitch): [22, 0, 22, 0, 45, 0, 22, 0, 0, 67, 0, 0]
distinct minutes with entries: 6 of 100
```

`timed` logs in six bursts across 100 minutes. Laid over the v2 schedule,
**7 of 12 envelope windows contain zero matching entries** — and that is on a
night where network time was OFF, which is exactly why `timed` goes quiet.

Failure scenario: if `log show` emits nothing at all on a zero-match query, then
on a perfectly clean night 7–12 envelopes get `state="asserted"`, reason
`timed log query returned no header`, exclusion `network_time_unattested`, and
`retained` collapses toward 0. The night burns a ~3 h quiet window and yields no
claim-bearing envelope. No test in the delta can catch this: every fake supplies
the header (`tests/test_quiet_predicate_campaign.py:20` `TIMED_LOG_HEADER`, and
the executor harness default changed from `""` to that constant at line 453).
The `ZeroOutputGuardTests` "header only → authenticated" row is the fixture
pre-satisfying the assertion, not evidence about `logd`.

Cure (cheap, read-only, and mine to recommend not run — the brief forbids me real
`log`): before arming, the magistrate runs one
`/usr/bin/log show --info --debug --style syslog --predicate 'process ==
"no_such_process_zzz"' --start <t> --end <t+60>` and pins its first line into the
fixture as exhibit D2. If the header is absent on empty output, the guard must be
re-shaped (e.g. liveness via a second predicate, or `--style json` returning `[]`)
before it can ship; as written it would convert a clean night into a void one.

## SHOULD-FIX

**S1 — item 6: `record_attestation`'s other failure branch still returns a
claim-bearing state.** `quiet_predicate_campaign.py:686-690`: an unreadable or
malformed `session.json` returns `False` while leaving `attestation["state"]`
untouched. Executed:

```
F  returned=False state='authenticated' reason=None   # session.json = "{ truncated"
F2 returned=False state='authenticated'               # session.json absent
```
(`python3 -B /tmp/fp.py`, my own fakes.) `execute` then journals
`network_time_attestation: "authenticated"` into `evidence_envelopes.jsonl` for an
envelope whose record could not be read. `pilot_summary` happens to exclude it
earlier (`:852-857`, `incomplete_interior_support`), so no retained envelope is
admitted — but the night's audit journal asserts the one claim-bearing state on
zero evidence, which is the exact defect class item 2 was raised to close. One
line: set `asserted` / `session record unreadable` in that `except` too.

**S2 — item 6: the guard leaks `session.json.tmp`, and the test that would have
caught it cannot fail.** `:698-701` writes the temp file, then `os.replace`. When
`os.replace` is what fails, the temp file stays:

```
G returned=False state='asserted' leftover_tmp=['session.json.tmp']
```

That leftover is a *complete* session record carrying the attestation with its
pre-downgrade `authenticated` state — a file on disk that reads like the record of
account and is not. `SessionRewriteFailureTests.test_a_read_only_envelope…`
(tests:1441) asserts `assertFalse(list(out.glob("*.tmp")))`, but with the directory
at `0o500` `write_text` fails at `open()`, so no temp file can ever exist there:
the assertion is vacuous. The real leak path
(`test_a_night_whose_annotations_cannot_land_still_finishes`, which patches
`os.replace` and therefore leaves 12 stray `.tmp` files) asserts nothing about it.
Cure: `temporary.unlink(missing_ok=True)` in the `except`, and move the `.tmp`
assertion onto the `os.replace` variant.

## NIT

**N1 — item 1: `attest_network_time`'s default `timeout=ATTESTATION_TIMEOUT_FLOOR_S`
(`:604`)** silently gives 5 s to any future caller that forgets the kwarg. Only
`execute:1106` passes a real bound today (verified exhaustively by grep: one
production call site). A required keyword-only argument would make the omission
loud.

**N2 — item 1 test is half source-text, half fake.**
`AttestationBudgetTests.test_the_bound_is…` (tests:1256) asserts
`assertNotIn("timeout=300", source)` — a grep, not behaviour — and its
end-to-end half runs with `attest_burn`, which replaces `attest_network_time`
with a canned `asserted` dict, so the night-level path never executes the real
timeout branch. The load-bearing part (`[kwargs["timeout"]…] == [15]*12`) is
genuine, and the unit half does execute a real timeout (I timed it at 0.507 s,
and reproduced it at 0.31 s with my own 0.3 s bound), so the bound is proven.

**N3 — item 14: `timed_log_window_epoch_s` (`:459`) is DST-ambiguous.**
`strptime(...).timestamp()` resolves an ambiguous local time as `fold=0`; the
argv strings come from `datetime.fromtimestamp`, which may be `fold=1`. On the
1 Nov 2026 fall-back the recorded `window_argv_epoch_s` can be 3600 s away from
what `log show` will read — and the underlying `timed_log_argv` ambiguity is
pre-existing, not introduced here. Nights run 02:17. Worth a registry note.

**N4 — deviation D1 (item 14) is a genuine reading conflict for the magistrate.**
The brief assigns the whole-second values to `window_epoch_s` and the float union
window to `window_argv_epoch_s`; the seat did the reverse. The seat's reasoning
(the key named "argv" should hold the argv's values; two ruled regressions pin
`window_epoch_s` to `attestation_window(stamps)`) is sound, but it is a rename of
a ruled field and needs ratification, not a report footnote.

**N5 — item 5, D4 confirmed benign.** A read-only night directory and an absent
night directory both return the correct exit-code verdict without raising and
without touching the record. Nothing escapes the `finally`.

## Requirement (4): byte invariance on a no-failure night — PASS

I ran the frozen executor to completion at 62412ee6 and again with all five files
checked out at c5f4f9c6 (same fake commands, same `timed_log` header), dumping
`evidence_outcome.json`, `summary.json`, `evidence_envelopes.jsonl` and all twelve
`session.json`, then diffed them structurally (`/tmp/bytes_probe.py`).
**`evidence_outcome.json`: zero differences.** The only differences anywhere are
the two additive keys the brief names — `network_time_attestation_wall_s` on each
of the twelve journal entries (and its pass-through into `summary.envelopes[*]`)
and `window_argv_epoch_s` on each of the twelve session attestations — plus
`summary.whole_campaign_observer_cpu_s` (0.00955 → 0.01163), which is the real
measured CPU of the test process and varies run to run, not a delta effect.
Retained counts, joules, exclusions, `log_sha256`, `window_epoch_s` all identical.

## Kill ledger

All seven mutations applied to the worktree, run, then
`git checkout -- .` / `git reset --hard HEAD`; tree verified clean after each.
Harness: `/tmp/mut.py <item>`; runner
`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest <class>`.

| item | mutation | red tail | green tail |
| --- | --- | --- | --- |
| 2 (required) | delete the `elif not timed_log_has_header(...)` branch (campaign:661-662) | `AssertionError: 'authenticated' != 'asserted'` — `Ran 5 tests in 1.626s / FAILED (failures=2)` | `Ran 5 tests in 1.643s / OK` |
| 3 (required) | restore `if not network_time_restored: return 3` ahead of the base code (campaign:1158) | `AssertionError: 3 != 2 : refused (two cleanup_unproven), restore failed` — `Ran 5 tests in 0.299s / FAILED (failures=2)` | `Ran 5 tests in 0.302s / OK` |
| 5 (required) | `if isinstance(control, dict)` → coerce non-dict to a fresh record and always rewrite the main file (campaign:388) | `- "stdout": "setUsingNetworkTime: On\n" … - "schema": "joulewise.network_time_control.v1"` — `Ran 7 tests in 0.264s / FAILED (failures=7)` | `Ran 7 tests in 0.260s / OK` |
| 9 (required) | rail comparator `== duration_ns` → `abs(...) <= 1000` (sampler:437) | `AssertionError: True is not false` — `Ran 4 tests in 8.056s / FAILED (failures=1)` | `Ran 4 tests in 7.981s / OK` |
| 12 (required) | `reduce_interior` re-rounds through float seconds before `integrate` (sampler:436) | `AssertionError: 12344999936 != 12345000000` — `Ran 6 tests in 7.865s / FAILED (failures=1)` | `Ran 2 tests in 0.000s / OK` |
| 6 (mine) | drop the `try/except OSError` around the `session.json` rewrite (campaign:698) | `AssertionError: 2 != 0` — `Ran 6 tests in 0.231s / FAILED (failures=1, errors=1)` | `Ran 6 tests in 0.244s / OK` |
| 4 (mine) | drop the `try/except` around `off = set_network_time("off")` (campaign:332) | `AssertionError: 'network time OFF not established' not found in "TimeoutExpired: Command '[…]' timed out after 0.5 seconds"` — `Ran 5 tests in 0.736s / FAILED (failures=1)` | `Ran 5 tests in 0.742s / OK` |

Note on item 4: the mutation shows the pre-fix code already refused with rc 2 (the
executor's except tuple caught `TimeoutExpired` directly), so the delta's real gain
is the receipt — which the regression does assert.

## Failure-path exercises (items 1, 4, 5, 6) — my own fakes, all documented states met

| path | executed result |
| --- | --- |
| item 1, real `sh` fake `log` sleeping 5 s, `timeout=0.3` | returned in 0.31 s, `state=asserted`, `reason='timed log query timed out after 0.3 s'`, no `timed-log.txt` written, window keys present |
| item 1, `log` exiting 7 | `state=asserted`, `reason='timed log query exited 7'` |
| item 4, `SUDO` pointed at a missing binary (`FileNotFoundError`, not a timeout) | raises `ValueError: network time OFF not established: FileNotFoundError: …`; control record on disk with `off.error`, `exit_code=None`, `stdout=None`, both clocks set |
| item 5, night dir `0o500` (neither file writable) | verdict `True` / `False` tracking the toggle's exit code, no raise, original `[]` bytes intact, no sibling |
| item 5, night dir absent entirely | verdict `True`, no raise |
| item 6, malformed / absent `session.json` | `False`, state left `authenticated` → **S1** |
| item 6, `os.replace` raising after a successful temp write | `False`, state `asserted`, `session.json.tmp` left behind → **S2** |

## Verdict

All seven kills reproduce; the no-failure night's byte output is unchanged beyond
the two named additive keys; every failure path reached its documented state
except S1/S2. The one thing that should stop this arming as-is is **B1** — not a
logic defect but a factual premise about `log show` that the repo's own corpus
shows governs 7 of 12 envelopes and that no artifact establishes. One read-only
command settles it.
