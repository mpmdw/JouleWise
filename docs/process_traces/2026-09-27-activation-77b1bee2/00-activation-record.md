# Activation 77b1bee2 — 11:36 PDT 09-27 (Opus 5.5 magistrate)

1. **Launch** 11:36:14 (watchdog attempt 123; `last_exit_class` = `usage_exhausted`). Heartbeat written first (`resident_session.pid` 91957). `notice_pending` = [`transition-514-hold_census` at 09:00:33 PDT, "production census non-empty inside plan span"]. The census rows in `events.jsonl` show only W2's own driver (`run_night.py run --plan …/d079-epoch-25g83-derivation-w2-20260927/night_plan.json`, PID 90113), present from t0 until ≈11:06, when the census went empty and the watchdog moved HOLD_CENSUS → FENCED; benign. Night agents `com.joulewise.night` and `.deadman` are still loaded (W2 not yet harvested/uninstalled), so no git operation touches the canonical root. No standdown or STOP file. Directives unchanged (#422 #421 #417 and the standing set).
2. **Owner instruction (Gmail message `1a0e3f5f40b48642`, thread `1a0e25449a3aa211`, 10:42 PDT 09-27), verbatim**, replying to the W1 harvest email's quoted item 2 (the chain-log read before the battery-verdict commit):

   > You can override this, this is a remnant overengineered process to stop someone
   > altering the data which no one would really do, that's an earnest mistake not
   > someone trying to cheat the science

   **Applied:** the W1 ordering slip (3ba66eeb) is closed as accepted by Ed; it needs no further disclosure action beyond this record. Ed's text permits overriding that read-after-commit ordering; it does not require it, and this activation does not amend the runbook (rule 11: a process change goes to the cold gate or Ed). For the W2 harvest the documented order is followed anyway because it costs nothing. A runbook simplification lane, HARVEST-ORDER-SIMPLIFY-01, is registered for Ed/cold-gate ratification, citing this item.
