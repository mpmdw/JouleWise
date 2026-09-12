# 12 — Opus pairing refuter (contract lens), ruling 50

Read-only in `wt-coldgate-a177` @ `74a547cd`.

**VERDICT: AMEND** — the oracle exemption is right; the warrant is overstated, the discharge rule certifies a dead assertion, and the ruled diff adds an unwitnessed term, relocates a surviving cut, and names a counterfactual that does not isolate.

## Q1 — reading or amendment?

**Excluding oracles follows** from Exhibit A: "A *clause* is one boolean term of a refusal condition"; (1) "named by a **test** whose counterfactual is refused by that clause ALONE"; A5 "running the **single test selected for each cut**." Test and cut are distinct roles, and an assertion refuses nothing.

**Including test mechanism does not.** `registry.adapter_type = ...`, the `patch.dict` scale patch and `bounded_captures.append(...)` refuse nothing, so under those same words they are neither clause nor fence. The texts reach neither side; keep audits 33/37's extension as practice, but "the texts already decide it" holds only for the exclusion.

**Dead-assertion counter-example.** The discharge rule ("first to fail on a named cut") is met by a cut of the test's own bookkeeping, so dead oracles pass. Instance: `test_controller.py:1688-1689`, `assertEqual(capture["timeout_s"], max(15.0, nominal_s*1.5+10.0))`. The left side is `self._capture_timeout_s(config, count)` (`:1651`); the right side rebuilds that same expression from the same inputs (`:1687` + `powermetrics.py:1469-1470`), so **no input can ever fail it**. Its only killer is Exhibit E clause 12 `record_timeout: report zero`, a cut of the one field only this oracle reads. Q1 keeps it; Q2 deletes it.

**Insert into the recorded sentence:** …naming one atomic cut **of production source or of a falsified input** on which that oracle first fails; **a cut of the test's own recording of a value only that oracle reads does not discharge it**, and an oracle whose two sides rebuild one production expression on identical inputs is dead and is deleted.

## Q2 — two diff defects, one bad counterfactual

Verified: formula `powermetrics.py:1468-1470`, used at `:1201`; both `max` operands pinned at `test_run_campaign.py:9636-9646`; `registry.adapter` at `:1710`. **No lane breach:** tests-only; floor→60.0 is in-memory.

1. **Unwitnessed new term.** `"config": config` adds a `record_config` cut nothing kills: a 40 Hz config recomputes `max(15, 94*0.025*1.5+10)=15.0`, and `56.4 > 15.0` still holds → survives; `interval_s` is recorded off the original config, so argv `-i` misses it. **Fix:** record `config` only and derive `interval_s` from `capture["config"]` via `_interval_ms` in the body.
2. **Relocated survivor.** Afterwards only the one-sided inequality reads `timeout_s`, so the cut `timeout_s = 0.0` survives: exempt oracle cut `stress_timeout_zero` becomes an unkilled *mechanism* cut — a round-four same-signature finding. **Fix:** rule that a direct call to the production function under test, on argv-witnessed inputs, is a **reference read**, not a mechanism term, discharged at `9636-9646`.
3. **Counterfactual wrong in one branch.** Strike "(or the offset from `10.0` to `50.0`)": at `count ≥ 96` (reachable; max 100), `n=4.8` → `57.6 > 57.2` → survives. Floor→60.0 is sound but zero-margin (at count 100, `60.0 > 60.0` fails only by strict `>`); use **floor→75.0**.

(ii) over (i)/(iii), and keeping the inequality, are correct.

## Q3

Defensible as split (`formula_floor` audits-33/37 class, R2 oracle-class), except that `stress_timeout_zero` is oracle-class only in the *current* shape; the ruled shape makes it mechanism-class, so restate post-fix.

## What I ran (read-only; `git status --short` clean before/after)

- `sed -n` `powermetrics.py` 1460-1475/1188-1205/1018-1036 → formula `:1468-1470`, use `:1201`, `count = max(3, ceil(min(5.0, baseline.duration_s)/interval_s))` ≤ 100
- `sed -n` `test_run_campaign.py` 9630-9650 (pins `17.5`/`15.0`), `test_idle_admission.py` 540-585 (`timeout == 17.5`), `test_controller.py` 1636-1725 (witness `:1641-1652`, mirror `:1688-1689`, inequality `:1690-1693`, `registry.adapter` `:1710`)
- `unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` → `Ran 1 test in 26.388s` `OK` rc 0 (unmodified)
- Arithmetic only, no cuts executed: `record_config` 40 Hz → 15.0; offset-50 survives at count ≥ 96; floor-60 margin 0.0; floor-75 margin ≥ 15 s
