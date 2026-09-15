# 03b — Design consult, OPUS seat report (blind, read-only, worktree `3d5b7623`), received 06:14 PDT 2026-09-15

Verbatim final message of the Opus design seat on brief 02. Model output; the magistrate adjudicates in record 06.

---

# INSTALL-WINDOWS-MULTI-01 — Opus design seat (blind, read-only, worktree `3d5b7623`)

## The finding that should drive the design

The driver's "overruns the dead-man" refusal is **not** what blocks an any-clock-time t0. I ran the current arithmetic for a 13:20 t0:

```
$ python3 -c "... from scripts.run_night import _next_deadman_epoch, COURIER_DEADLINE_S ..."
t0 2026-09-16 13:20:00 / completion 15:55:00 / deadman 2026-09-17 07:00:00
gap_hours 15.08   refuses? False
```

A 13:20 plan **passes** `run_night.py:1470-1481` today. What breaks is everything downstream of `_next_deadman_epoch`: `magistrate_watchdog.py:736,749,782` keep the plan `armed` and its span `active` until next-07:00 + `COURIER_LOCK_FRESH_S`, so a 2.5 h afternoon window fences the magistrate for ~15 h and defers the dead-man courier by ~15 h. **The single load-bearing edit in this lane is making the dead-man epoch plan-derived rather than wall-clock-derived.** Everything else is ripple.

Second finding: **the install span does not exist in code at all today.** `grep -n "install span\|install_span" scripts/*.py scripts/*.sh` → no hits; only prose (`derivation_night_runbook.md:1248`, `NIGHT_HANDBACK.md:220`). `install_night_agent.sh` reads the clock only for plan staleness (`:109-115`); its one time-of-day rule is `hour == deadman_hour` (`:161-166`). So "never install after the span closes" is not being *relaxed* from one span to many — it is being **built for the first time**.

## Q1 — Where the span list lives

**A tracked module of defaults + an install-time argument. Not the plan, not the watchdog.**

New `joulewise/night_windows.py`:
```python
DEFAULT_INSTALL_SPANS = (("03:00", "06:30"), ("10:00", "12:00"), ("14:00", "17:00"))  # local wall clock, per-day recurring
def resolve_span(now_epoch_s) -> tuple[int, int] | None   # (open_epoch, close_epoch) of the span containing now
def spans_for_day(day: date) -> list[tuple[int,int]]
```
plus a `__main__` that prints the resolved close epoch (so zsh does no date math).

Deciding reason: the span is an **arm-time** property. No consumer at t0 needs it — not `night_gate` (its refusal list, `night_gate.py:59-74`, is all machine state), not the driver, not the watchdog's span logic. Put state where its only consumer is. Local wall-clock recurrence, not epochs, because Ed's text is "several bounded install spans per day" and DST-correct resolution belongs in one Python function, not in a hand-edited epoch table.

Spans must be non-overlapping, ordered, and close > open (validate at import; a same-day 23:00–01:00 wrap is refused rather than silently handled).

## Q2 — Dead-man per span: define it

"Per span" is the wrong axis; the brief's own framing should be rejected here (see disagreements). The dead-man is **per plan**:

```python
DEADMAN_MARGIN_S = 1800
def deadman_epoch(plan): return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S + DEADMAN_MARGIN_S
```
in `scripts/run_night.py`, replacing `DEADMAN_HOUR/MINUTE` (`:67-68`) and `_next_deadman_epoch` (`:958`). `magistrate_watchdog.py:47` already imports that symbol, so the watchdog follows for free; `gen_derivation_night.py:65-66,231-240` must stop duplicating and import it (that duplication is exactly the defect class this lane should close).

Which agent fires it: the same `com.joulewise.night.deadman` plist, but `@@HOUR@@/@@MINUTE@@` computed from `deadman_epoch(plan)` instead of from constants (`install_night_agent.sh:159-166,255`). **Add `@@MONTH@@/@@DAY@@` to `configs/launchd/com.joulewise.night.plist.template:23-29`** for both agents: `StartCalendarInterval` with Month+Day fires once a year instead of daily, which removes the "night agent re-fires tomorrow and is only stopped by the write-once record" hazard — a hazard that gets worse when windows are hours apart rather than days.

`plan_overruns_deadman` (code registered at `night_gate.py:91`) becomes vacuous under the derived dead-man. Do not delete the code — re-point it: refuse when `window_max_s + COURIER_DEADLINE_S + DEADMAN_MARGIN_S > MAX_PLAN_SPAN_S` (name the ceiling; today's armed night is 9000+300+1800 = 11100 s). That keeps "a plan cannot be unboundedly long" after the 07:00 wall is gone, keeps the registered code non-dead, and costs no schema change.

"Never install after the span closes", mechanically: `install_night_agent.sh` gains `--install-span-close EPOCH` (required unless `--uninstall`/`--render-only`) and refuses with exit 2 when `now >= close` **or** `now < open`. Integer comparison in zsh; the epochs come from `joulewise.night_windows`. Refusal text names the span and the resolved epochs. The driver must **not** re-check at launch (it has no span in hand, and a stale span check at t0 would be a new refusal path for no gain).

New fence the brief does not ask for and should have: refuse the install when `plan.t0_epoch_s - PLAN_LEAD_S < now + 600`. With day-before installs this was impossible; with same-day spans, arming 5 minutes before t0 gives the watchdog no time to stand a magistrate down. Call it `install_too_close_to_t0`.

## Q3 — What replaces `local_fixed_fence`

Delete `belt_02:45_03:30` and `deadman_minute_07:00` (`magistrate_watchdog.py:702-714`). The dead-man minute is already covered: `plan_span_active` (`:720-733`) runs to `deadman + COURIER_LOCK_FRESH_S` whenever a plan is discoverable.

The belt's unique value is precisely the case the brief names: **a plan authored but not yet discoverable** (`glob_plans` = `self.root.parent.glob("*/night_plan.json")`, `:258-259`; the runbook publishes the plan only *after* the notice, §1.4). Replace the time-of-day proxy with an explicit declaration: the arming activation writes `<watchdog root>/arming.json` `{plan_id, open_epoch_s, close_epoch_s}` at the start of its desk block; the watchdog returns `Decision("FENCED", f"arming_declared:{plan_id}")` while `open <= now < close`, refuses a declaration longer than a hard TTL (`ARMING_MAX_S`, 8 h), and ignores an expired one. Absent file ⇒ no fence (fail-open is right: absence means nobody is arming; fail-closed on a stale file would fence the magistrate forever). Insert at `:1410`, keeping the current order — plan span first, declaration second, at the existing `if fixed is not None` site (`:1440-1441`).

## Q4 — What blocks two windows on one day

| Blocker | Evidence | Minimal change |
|---|---|---|
| Results-branch + dir name | `run_night.py:549 _night_date`, used at `:574,582,595` — two windows on one day collide | key on `plan.plan_id` (already unique, already date-carrying) |
| `plan_is_armed` / `plan_span_active` | `:736,749` next-07:00 tail → 15 h of false "armed" | follows automatically from Q2 |
| `plan_conflicts` | `:782` same tail in `left_end` | follows from Q2. Note same-`measurement_root` pairs are exempt (`:779-780`), so two sequential same-root windows already produce no conflict |
| `fenced_checkout_rows` | `:796-807` — one row per plan, no collision | none |
| Custody/night root | `<night-custody>/<plan_id>` | none; runbook names the id convention (`…-n2-<date>`) |
| Installer | labels are fixed (`:222-223`) and existing night records refuse re-install (`:245-252`) | none — sequential arm is what D-181 asks for. Do **not** make labels per-plan: `--uninstall` finds agents by those two labels |
| Handback page | one file, rewritten per plan (`NIGHT_HANDBACK.md:220,238`) | move to `docs/process/night_handbacks/<plan_id>.md`, keep `NIGHT_HANDBACK.md` as index + procedure |

## Q5 — Schema

**No schema bump. Stay at v2/v3 as they are.** Deciding reason: every new quantity is derivable from keys the plan already has (`t0_epoch_s`, `window_max_s`), and the one genuinely new datum (the install span) has no t0-time consumer.

The cost of the alternative is concrete and avoidable: `night_gate.py:216` builds an exact key set, `:212-233` raises `night_plan_malformed` on any extra key; `PLAN_SCHEMA=v2` and `PACK_PLAN_SCHEMA=v3` (`:23-26`) are **class labels, not a ladder**, so "bump packless to v3" collides with the pack schema and a real bump means v4 for both classes, plus `night_plan_writer.py:19-34`, `install_night_agent.sh` v2/v3 tests (`tests/test_install_night_agent.py:387,400,473`), and the relaunch-prompt sentence "only under a v2 plan". Buy none of that for a field the gate never reads.

## Q6 — Regressions (count-free names)

- `test_default_install_spans_are_ordered_disjoint_and_local` — span list shape + a DST day.
- `test_resolve_span_returns_none_between_spans`.
- `test_deadman_epoch_is_derived_from_t0_window_and_courier_deadline` — asserts the margin, not a clock hour.
- `test_afternoon_t0_deadman_is_hours_not_next_morning` — the 13:20 case above; pins `deadman - completion == DEADMAN_MARGIN_S`.
- `test_afternoon_plan_passes_driver_gate_and_span_closes_same_day` — driver GO + `plan_span_active` False at `deadman + COURIER_LOCK_FRESH_S + 1`.
- `test_watchdog_is_not_fenced_at_0300_without_a_discoverable_plan` — belt removal.
- `test_watchdog_is_fenced_by_a_fresh_arming_declaration_and_not_by_a_stale_one`.
- `test_install_refuses_after_span_close_and_before_span_open` (shell-level, mirroring `tests/test_install_night_agent.py` style).
- `test_install_refuses_when_t0_is_inside_the_standdown_lead`.
- `test_deadman_plist_calendar_interval_matches_the_derived_epoch` — including Month/Day.
- `test_two_plans_on_one_day_use_distinct_roots_branches_and_no_conflict` — `_night_date`→plan_id plus `plan_conflicts == []`.
- `test_gen_derivation_night_imports_the_single_deadman_home` — asserts no second constant (`gen_derivation_night.py:65-66` today).

Existing tests to retire/rewrite, named so nobody is surprised: `tests/test_run_night.py:766,886,1618,1631-1632,1740,1775`; `tests/test_gen_derivation_night.py:397`; `tests/test_magistrate_watchdog.py:443,451,459-469`.

## Q7 — Docs

- `derivation_night_runbook.md:1248` §1.3: retitle "Install spans and the exit boundary"; replace "on the calendar day BEFORE t0, between 03:00 and 06:30" with "inside any span printed by `python3 -m joulewise.night_windows`, on any day, provided t0 − 25 min is at least 10 minutes away"; delete "never install in the 07:xx hour" and the `t0 + window_max_s + 300 < 07:00` arithmetic; replace with the derived dead-man line. Fix the collateral mentions at `:1145` and `:2273,2293`. Resolve the `[UNVERIFIED]` 06:05 cutoff block by restating it as "the span's close minus the block's duration".
- `NIGHT_HANDBACK.md:126-132,220,238-252`: Timeline paragraph names **every span of the install day** and the plan's own span; delete "t0 sits inside the fixed 02:45–03:30 belt, which is correct for a night"; notice text gains "install spans today: …; this plan was installed in the HH:MM–HH:MM span" and the derived dead-man local time. Procedure (email-then-arm, NO overrides) unchanged in substance.
- `MAGISTRATE_WATCHDOG.md:31,42,52-54`: belt/dead-man-minute rows → the arming-declaration row and the plan-derived span.
- `MAGISTRATE_RELAUNCH_PROMPT.md`: keep "v2 plan" verbatim (no bump); add the arming-declaration line.

## Q8 — Do not change

Census and its argv (`night_gate.py:43`), `LOAD_MAX`, `PLAN_MAX_AGE_S`; `PLAN_LEAD_S`/`REQUEST_LEAD_S`/`TERM_LEAD_S`/`KILL_LEAD_S` (`:724,822-830`) — they are measured from t0 and are already clock-free; `COURIER_DEADLINE_S` and `COURIER_BACKOFF_S` (R-7-derived from `cold_start.json`); `window_max_s` arithmetic and the twelve-slot minimum in `gen_derivation_night.py:520-527`; every `NIGHT_GATE_REASON_CODES` entry; the write-once record set (`run_night.py:80-89`); the twelve-row gate; email-then-arm ordering. Reason: each of these is bound to physics, evidence or owner authority — none of them encodes a time of day.

## What the lead should double-check

1. **launchd Month/Day semantics on 25G83** — a missed once-a-year calendar interval (machine asleep/off at the moment) must still fire at wake. Verify with a render + `launchctl print` at the bench before trusting single-shot plists; if it does not, keep daily Hour/Minute and rely on the write-once record.
2. **`DEADMAN_MARGIN_S = 1800` is my number, not a measured one.** It must exceed the worst observed courier retry envelope; `COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)` = 900 s (`run_night.py:57-60`), so 1800 has ~2x headroom — confirm against a real harvest's `courier.json` timestamps.
3. **The frozen clone currently on disk** carries a plan authored under the old arithmetic; confirm no armed plan exists before landing (this session's record says NOTHING ARMED) and that no `night-results/<YYYYMMDD>` branch consumer outside `run_night.py` reads that name (I grepped only `scripts/`).
4. Whether `arming.json` belongs in the watchdog root (writable by the arming activation) without violating `Storage._write_path`'s refusal (`magistrate_watchdog.py:245-249`) — the watchdog only reads it, but confirm the path is inside `root`.

## Where I disagree with the brief

- **"Dead-man per span" is the wrong unit.** A span is a window for *installing*; a dead-man is a bound on *a night that has started*. One plan installed in one span has one dead-man; a span with no install has nothing to stand down. Q2's framing invites a per-span timer that would fire with no plan to reference. The rule Ed states ("never install after the span closes") is an **installer refusal**, not a dead-man, and I have implemented it as one.
- **Q1's premise that the span list might live in the plan or the watchdog** should be rejected: it would force a schema bump (Q5) for a field with no t0-time reader, and would give the watchdog a second, redundant time-of-day fence just as we are removing the first.
- **The brief under-weights the watchdog** and over-weights the driver refusal. Q2 asks "what margin?" as the interesting question; the measured fact above is that the driver already passes a 13:20 t0 and the watchdog silently fences for 15 h. A seat briefed on the brief's ordering could land a green lane that still cannot run two windows in a day.
- **A missing fence**: any-clock-time t0 makes "install 5 minutes before t0" newly reachable, which the day-before rule made structurally impossible. `install_too_close_to_t0` is not in the kernel acceptance and should be added to it.
