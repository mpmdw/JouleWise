# A210 LEAD-MARGIN-01 — fresh final-head review (Fable, row 10)

Head e05e497a, diff 69d668be..HEAD, scratch copy. `tests.test_run_night` + `tests.test_magistrate_watchdog`: 196 tests OK, 10 s.

## 1. Physics

Gates byte-unchanged: `git diff 69d668be..HEAD -- joulewise/night_gate.py` empty; `LOAD_MAX = 2.0` (night_gate.py:57), census `pgrep -lf "codex|claude|t3"` (:41), HID idle (:46–52, :1138–1151), boot clock (:55, :1257) untouched; run_night.py's only gate-adjacent edit is the constant (:75).

Load decay (5 s samples, e^(−5/60)): 120 s → 13.5 % of excess; 105 s effective (10 s poll slack + ~5 s signal/exit) → 17.4 %; 165 s (TERM honoured at t0−3) → 6.4 %. From load 6, base 0.5: 0.5+5.5×0.174 = **1.46 < 2.0**. Bound: KILL-only teardown clears t0 while excess ≤ ~8.6 (base 0.5) or ≤ ~5.7 (base 1.0); from load 12 it needs ~160 s. **2 min is sound as a floor provided TERM at t0−3 is the working teardown** — write the bound down (should-fix).

Backstop honest: live tree or load > 2.0 refuses at t0. But **A172 is unbuilt** (TASK_QUEUE.md:794 BLOCKED) and covers only non-physics aborts; a load/census refusal is physics → cold-gate path → human re-arm. No doc claims otherwise.

**BLOCKER-tier derivation gap (curable by amendment):** D-171(b) (decision_log.md:10990–11008) ratified 25/16/15 on a *physical* reason the seat never names: window_runbook.md:425–432 requires ≥ 10 min untouched idle before the first capture so idle-triggered daemons (XProtect) run before the window — "a 5-minute margin cannot buy 10 minutes of quiet". The letter still holds: d01 starts at t0+Δ+600 s (runbook :1124–1145, :1226–1244; `SETTLE_S=600`, night_chains/calibration_derivation_only.zsh:76), so quiet-to-d01 ≥ 120+10+600 ≈ 12.2 min ≥ 10 — but the margin against a late-starting scan drops from ~25 to ~12 min, and load is not rechecked per capture (thermal only). Reinterpreting a ratified physical reason needs a dated D-171(b) addendum from cold gate/Ed (rule 11), not silence.

## 2. Watchdog mechanics

Supervisor dead at t0−4: `standdown.request` exists from t0−5 (`_write_request` is write-once, watchdog :1729–1732). The next launchd tick (StartInterval 300, template :24) lands in (t0−4, t0+1]; it adopts and calls `supervisor.run()` (:2369), whose `_enforce_drain` sends TERM-then-KILL on phase KILL (:1875–1893). A post-t0 tick means a live tree at census → REFUSED, then killed. The old 300 s < 540 s recovery guarantee is gone; the limitation is stated operator-side (MAGISTRATE_WATCHDOG derivation paragraph, NIGHT_HANDBACK:151–159, runbook §1.3). Optional: StartInterval 300→60 restores the TERM guarantee cheaply (remote probe stays at :87's 300 s cadence).

## 3. Docs

Six docs clean of 85/25/16/15/nine-minute ladder text (remaining 3600/900/15-min hits are dead-man, courier lock, liveness). **Stale:** decision_log.md:10996, :11440, :11770 still say t0−25/−16/−15; state_kernel.json:5517 (historical, nit). Relaunch prompt: in two minutes the magistrate must commit/push worktrees, update the pointer, Gmail Ed, stop children, exit — feasible only at a slice boundary (prompt polls "before every new work slice"); mid-seat it will not see the request, so TERM at t0−3 is the real path and "courtesy" is the right word.

## 4. Tests

Pinned: constants (watchdog test :655–663; run_night :1434), fixed-epoch close 1799999580 = t0−420 (:1441–1444), ordering (:664–667), gaps ≥ 6 polls, 110/50 slack (:670–676), install_close < t0−REQUEST (:1437), late request buys no grace, term/kill epochs (:678–695), prompt string (:1990). Each fails on a plausible regression. **Nit:** `assertLess(min(gaps) - launchd_tick, 0)` (:677) pins the *weakness* as invariant; drop or invert. Missing: `KILL_LEAD_S + SETTLE_S ≥ 600` (the §1 idle rule).

## 5. Floor beyond 7 min

Nothing: install_close = t0−420 is minute-aligned given `t0 % 60 == 0` (run_night.py:1045); courier 300 s and DEADMAN_GRACE_S are post-window; notice has no minimum lead (install opens at notice send, NIGHT_HANDBACK:140), so Ed's veto window can shrink to seconds — his directive. Two lines worth adding to NIGHT_HANDBACK: an *interactive* arm (unowned session) is never TERM/KILLed, so the operator now has 5 min, not 25, to close every agent; the rehearsal arm at t0=now+8 leaves ~1 min before the cutoff (nit: +10).

## 6. Verdict

**LANDABLE with amendments** (pre-merge):
1. Add the idle-daemon mechanism to runbook §1.3 + MAGISTRATE_WATCHDOG with the quiet-to-d01 ≥ 12 min arithmetic, and a dated D-171(b) addendum ratified by cold gate/Ed. If the gate wants the old margin, 8/8/6/5 hits the row's stated ~10-min target.
2. Record the load bound (KILL-only clears t0 only for excess ≲ 6–8; TERM is the working teardown).
3. Decision-log addendum for :11440/:11770; fix test :677.
