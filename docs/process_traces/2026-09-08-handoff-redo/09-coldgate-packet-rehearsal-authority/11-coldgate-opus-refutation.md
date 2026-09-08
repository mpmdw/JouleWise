# Opus contract-lens refutation — cold gate, rehearsal-arming authority (2026-09-08)

Read-only. All line numbers verified this session at working-tree HEAD (d8ad6c15).

## 1. The "already armed" carve-out has no counterpart in the code; a plan is armed the instant it is written

`plan_is_armed` (`scripts/magistrate_watchdog.py:740-750`) returns True as soon as
`authored_epoch_s <= now`, with no chain markers and no `night/courier.sent`, through
`_next_deadman_epoch(t0) + COURIER_LOCK_FRESH_S`. For the proposed plan (authored 2026-09-08,
t0 2026-09-09 02:56 PDT) that is True from the moment of the write, ~25.6 h before t0.
`decide()` then puts it in `armed` and writes `state["fenced_checkouts"]`
(`:1204-1205`); `MAGISTRATE_WATCHDOG.md:86` says the same ("every authored, not-completed v2
plan"). So the ruling's line "plans ... that are ALREADY ARMED" does not partition the world into
"new plan (allowed)" and "armed plan (barred)" — the new plan is armed at the next tick, and every
subsequent touch of it is barred by the ruling's own terms. That matters because the operational
record shows the last rehearsal REQUIRED exactly such a touch: `NIGHT_HANDBACK.md:27-32` records
`rehearsal-20260903` being RE-ARMED and re-pinned after a HEAD move, and
`MAGISTRATE_WATCHDOG.md:258` requires "re-arm after any relevant HEAD move." The ruling grants
one-shot authority with no repair path.

Command: `sed -n '740,760p;1200,1212p' scripts/magistrate_watchdog.py`

## 2. The arming write is watchdog input, and a bad write bricks the loop — no condition prevents it

`Storage.glob_plans` is `self.root.parent.glob("*/night_plan.json")`
(`scripts/magistrate_watchdog.py:258-259`). Custody root is `~/night-custody/magistrate/`, so a
plan written at `~/night-custody/rehearsal-20260909/night_plan.json` is inside the watchdog's own
glob at the next 300 s tick. `load_plans` is advertised as non-mutating (`:649-650`), but its
output drives three watchdog-owned effects:

- `state["fenced_checkouts"]` → the NEXT activation's `@@FENCED_CHECKOUTS@@` and prompt line 10
  (`:1204-1205`, `render_prompt` `:1290-1296`);
- `HOLD_UNSAFE` on `snapshot.errors` (unreadable/malformed) at `:1206-1207` and on
  `plan_conflicts` at `:1208-1210` — and per `MAGISTRATE_WATCHDOG.md:16`, "no later launch occurs
  until a fresh tick sees that plan hold clear";
- in a resident, `:1729-1745` sets `resident_hold_drain` and runs the irreversible
  9-min/TERM/1-min/KILL ladder on the arming session itself.

So one malformed-but-complete `night_plan.json` written by the resident causes the watchdog to
kill that session and then refuse to launch any successor — the total loss of the unattended loop,
recoverable only by Ed's hands, since removing the offending plan is "altering plans," barred by
line 19 under the ruling's own reading. This is precisely "a headless session moving the watchdog's
own state out from under the watchdog," the failure the packet names. None of the four conditions
mentions plan authorship, validation, atomicity, or a staging path outside the glob.

Answer to charge Q2: yes — the arming write reaches the watchdog through the plan's declared
`custody_root` (`plan_span_active` reads `Path(plan.custody_root)/"night"` chain markers,
`:721-737`), through the fence/deadline arithmetic, and through the drain ladder. None of the four
conditions binds `custody_root` to the plan directory, binds the installed LaunchAgent's
`--hour/--minute` to the plan's `t0`, or requires plan validation. (`install_night_agent.sh` checks
only that the hour is not the dead-man hour, `:108-109`; it never compares hour/minute to `t0`.)

## 3. `/private/tmp` is fine — exhibit E's objection is refuted

`install_night_agent.sh:57-70` requires `measurement_root` absolute and whitespace-free, plan not
future-authored, not older than 36 h; `:80-94` requires `git -C "$repo" rev-parse HEAD == repo_head`
and `git -C "$measurement_root" rev-parse HEAD == measurement_head`. A real detached checkout of
`ae8f074f` under `/private/tmp` satisfies all of them. Nothing forbids `/private/tmp`; the opposite
— `MAGISTRATE_WATCHDOG.md:258` explicitly blesses `/private/tmp/...` roots for rehearsal stubs
(with "must never be reused by a real plan" and "Remove every `REHEARSAL_STUB` plan root before
arming any real plan"), and `:262,289,379` use them in the bench fixtures. Exhibit E:9 ("the night
installer requires a real measurement checkout") is correct about the requirement and wrong about
the conclusion: a real checkout at a `/private/tmp` path meets it. Note `/private/tmp` (not `/tmp`)
is required for `_canonical_measurement_root`'s `resolve()` (`:761-762`) to round-trip; the packet
has this right. Verified absent today: `ls -d /private/tmp/joulewise-rehearsal-20260909-checkout`
→ No such file.

## 4. Arm-then-exit is mechanically compatible, but condition (4) decays in ≤300 s

t0 = 02:56 PDT gives REQUEST at 02:31, TERM 02:40, KILL 02:41 (`REQUEST/TERM/KILL_LEAD_S`,
`:67-70`; `standdown_phase` `:822-830`) — all strictly before the belt `[02:45, 03:30)`
(`local_fixed_fence` `:702-712`), and `decide()` evaluates `active_plans` before `fixed`
(`:1224-1247`), so the plan branch governs the span and the belt only backstops afterwards. That
ladder is coherent. What is NOT coherent is treating line 12 as a safety condition here: after the
arming session exits, the very next tick sees no active span (t0−25 min is 25 h away), stop CLEAR,
no fixed fence, no owner → `LAUNCHING` (`:1256-1265`). The watchdog immediately spawns a fresh
headless magistrate that lives all day with the plan armed. Condition (4) ("no arming while any
other agent session is alive") therefore guarantees nothing past the instant of the write; the real
protection is the plan-span ladder, not condition (4).

## 5. Strongest reasons each way

- **OVERTURN:** the write lands inside the watchdog's own plan glob
  (`scripts/magistrate_watchdog.py:258-259`) and a malformed one kills the resident and permanently
  holds launches (`:1729-1745`, `:1206-1210`, `docs/process/MAGISTRATE_WATCHDOG.md:16`) — the exact
  fail-closed brick line 19 exists to prevent, and the ruling adds no condition against it.
- **UPHOLD:** `docs/process/MAGISTRATE_WATCHDOG.md:86` — "Arming also obligates the session to end
  its loop and exit by the request deadline" — is the design doc's own statement that the
  watchdog-relaunched session is the arming party; with prompt line 12 (`exhibit-A:12`) and line 13,
  reading line 19 to bar arming makes three prompt lines dead text.

## Recommendation

**AMEND.** Keep the ruling's holding; replace its condition list with:

> provided: (1) `NIGHT_HANDBACK.md` is re-dated with the real pins of the plan's checkout and
> committed before the arm email; (2) the plan is authored ONLY by
> `joulewise.night_plan_writer.write_night_plan`, written first to a staging path that is NOT
> matched by `~/night-custody/*/night_plan.json`, validated there by
> `scripts/install_night_agent.sh --render-only` run FROM the plan's `measurement_root` at its
> `measurement_head`, and only then moved atomically (`os.replace`) into its plan directory;
> (3) the plan's `custody_root` equals its plan directory, contains no existing night record, and
> the two night agents are installed from that same checkout with `--hour/--minute` equal to the
> plan's `t0` in local time; (4) the arm email names `t0`, `measurement_root`, `measurement_head`,
> receipt class `REHEARSAL_STUB` and the courier deadline, and precedes arming; (5) no arming while
> any other agent session is alive, and the session re-runs the census immediately before the move
> in (2); (6) the session retains authority to re-arm or REMOVE this same `REHEARSAL_STUB` plan it
> authored — and only that plan — under conditions (1)-(5); every other plan, night record, lock,
> request, event, and `state.json` remains barred by line 19.
