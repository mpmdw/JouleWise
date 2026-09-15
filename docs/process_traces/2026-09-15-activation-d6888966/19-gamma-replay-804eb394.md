# 19 — Replay at the merge candidate `804eb394` (row 9) and CI (row 11 first half) — 08:26 PDT (clock-read)

Tree `/Users/edr/code/JouleWise-wt-gamma-keys` @ `804eb394` (branch `fix/2026-09-15-gamma-root-keys` = `678d9bcc` +
merge of `origin/main` `ee6065f8`-era bookkeeping; clean before and after). Command (lead, unpiped to
`/tmp/magistrate-d6888966/gamma-replay-804eb394.txt`): `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py
--workers 4 --split`, launched 07:23:55 PDT, finished 08:22 PDT, `rc=1`. Exact shard summaries:

```
SHARD SUMMARY index=2/4 modules=61 tests=1311 failures=0 errors=0 skipped=77 result=PASS
```

## The one red module, diagnosed at the bench

Shard 1's twelve failures are the twelve subtests of ONE test,
`tests.test_magistrate_watchdog_cli.HandoffCliDefectTests.test_corrupt_lock_cli_refusal_survives_unreadable_state_and_repeated_hold`
(`MODULE FAIL tests.test_magistrate_watchdog_cli tests=6 failures=12`); every other module in all four shards passed.

Cause (reproduced with a 20-line script, record kept in this file): the watchdog discovers night plans with
`self.root.parent.glob("*/night_plan.json")` (`scripts/magistrate_watchdog.py:259`), i.e. in the PARENT of the custody
root. The test passes `--custody-root <TemporaryDirectory>`, whose parent is `/private/tmp`, so the tick found four
stale fixture plans left by earlier sessions and seats — `/private/tmp/install-windows-docs-synthetic/` (07:00 today, a
finished seat's synthetic plan), `interp-pin-fixture-31pn32dg/`, `joulewise-rehearsal-20260912-validate/`,
`night-pin-reaudit-i0ichlzc/` (all 09-11) — and went `HOLD_UNSAFE` with `night_plan_malformed …: plan authored_epoch_s
is in the future` (the harness clock is fixed at 2026-09-04) before the corrupt-lock branch could append its notice;
`notice_pending` stayed empty. Not this PR: the same module fails identically on clean `origin/main` `ee6065f8` at this
bench (`FAILED (failures=12)`) and passes on CI's clean runner. The live watchdog state was checked and is untouched
(`notice_pending []`, no `corrupt_lock` event, lock intact); the failure is confined to the temp harness root. The
`MAGISTRATE_WATCHDOG_CUSTODY_ROOT` variable this headless session inherits was ruled out (`env -u` fails the same way).

Cure at the bench (environment, not code): the four stale fixture directories were MOVED (not deleted) to
`/tmp/magistrate-d6888966/stale-tmp-plans/`; `/tmp/*/night_plan.json` now matches nothing. Module re-run at
`804eb394`, 08:25:23 PDT:

```
Ran 6 tests in 12.354s

OK
```

Replay verdict: PASS at `804eb394` (shards 2/3/4 PASS; shard 1's 51 other modules PASS; the one failing module PASS on
re-run after the environmental cause was removed). Lane to register: WATCHDOG-CLI-TEST-TMP-DISCOVERY-01 — the CLI test's
custody root must be nested one level below the temporary directory so discovery cannot see foreign `/tmp` plans.

## CI on the final head (row 11, first half)

run 34981396571 completed success head 804eb394 (`gate-ledger` advisory check red only while the ledger rows read NOT-RUN). The post-merge cross-unit
integration review follows the merge and is recorded separately.
