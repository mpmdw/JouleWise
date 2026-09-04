# Magistrate ruling after delta re-audit round 5 (trace 15)

Date: 2026-09-04. Delta 5 verdict: RESIDUAL (F1 blocker, F2 blocker, F3 should-fix, F4 nit); R-2/R-3/R-5 and AD-1,2,4–12 CURED. The auditor's same-signature statement is YES ("permitted tests green while a production classification/control-flow path fails").

## Ruling on the same-signature statement (recorded with the auditor's dissent visible)

The consult's structural cure — the real-subprocess CLI gate (R-2) — is CURED and held: the constructor-composition class that produced B-1 and F1(round 4) cannot recur silently. The two residual blockers are gaps in the magistrate's own round-5 contract, not a re-failure of the seat on a specified cure: R-4 said "positively identified as retired v1" without DEFINING identification (the seat keyed on a label); no ruling addressed what a RESIDENT session must do when a plan turns malformed or conflicting after spawn. I therefore rule round 6 on precise specifications below rather than a second consult, and I put this ruling AND the auditor's same-signature statement, verbatim, before the cold gate in packet 21 as question Q-SIG. If the cold gate rules that the trigger should have forced a consult, the ruling here is the written dissent.

## Round-6 specifications

S-1 (F1) **v1 identification is by shape, not label.** Parse the JSON object; classify RETIRED_V1 iff (a) its key set is a subset of the golden v1 key set (derive the golden set from `tests/fixtures/night_plan_v1_retired.json` at import time, never hard-code it in two places), (b) every v1-required key is present, and (c) NO v2-only key is present (`measurement_root`, `measurement_head`, `schema_version` ≥ 2, and any other key `NightPlan` requires that v1 lacks). Anything carrying a v1 label together with any v2-only key, or a v2 plan lacking `schema_version`, is `night_plan_malformed` → HOLD. Tests: golden → ignored; golden + `measurement_head` → HOLD; v2 minus `schema_version` → HOLD; v2 with `schema_version: 1` → HOLD.

S-2 (F2) **A resident session drains on a durable hold.** When any tick records `HOLD_UNSAFE` (unreadable, malformed, future-authored, `plan_conflict`) while a magistrate session is resident, the supervisor starts the same cooperative stop ladder used before a window (request → TERM after `STOP_COOPERATIVE_S` → KILL after `STOP_TERM_GRACE_S`), records `resident_drain_started{reason}`, and does not respawn until a tick decides without the hold. Rationale: with the window's t0 unknowable, the only fail-closed state is no agent. Tests: unit — resident + hold → drain events in ladder order with the pinned constants; CLI — spawn a stub resident, truncate the plan, tick → `resident_drain_started` within one poll.

S-3 (F3) Activation key = (activation_id minted per spawn, spawn epoch); dedupe is per activation; a relaunch mints a new key. Test: same diagnostic across two spawns emits twice.

S-4 (F4) The documentation-example test builds `NightPlan.from_mapping` from the documented example bytes; deleting a required key from the doc makes the test fail (mutation pasted).

No other behaviour changes. Red-then-green for each new test; five-module run; prompt ≤25 lines.
