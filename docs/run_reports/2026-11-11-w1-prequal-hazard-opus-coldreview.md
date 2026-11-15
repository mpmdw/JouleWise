# Cold review: `ops/2026-11-11-w1-prequal-hazard` @ `edbec60f7` (F-6)

Opus 5.5, interim lane lead, 2026-11-11. **Verdict: ADMIT.**

- Decision: `hazard_window` is a registered plan field (HAZARD_PACK plans; `joulewise/night_gate.py:456-462, 628`; built
  by `joulewise/b5/plan.py`), so the arm (`scripts/align_v4_session.py`, `c6d25d963`) is right and the PREQUAL control
  plan was wrong. Only the unbound harness `joulewise/align/w1_prequal.py` and its tests change.
- The control plan's `hazard_window` comes from the registered threshold assembler (`joulewise.b6.plan_inputs.thresholds`)
  with `T_stream_max_s` sized as the writer sizes it (max member_s); no hand-typed numbers.
- The control now runs the production plan check (`frequency_word_preflight`) up to the native reader, which the
  synthetic host stands in for; previously the whole preflight was faked.
- New failing-first case `plan-hazard-window-missing`: refuses with exactly
  `clock.frequency_plan_invalid: ValueError: plan clock budget unavailable: 'hazard_window'` and nothing else.
- The 13 original case records are byte-identical to before (seat).
- On the Air: `tests.align.test_w1_prequal` 42 tests, 40 pass, including all of ArmCliTests; the two failures
  (`MeterCrashRadiusTests.test_a_member_before_a_reader_crash_is_judged`,
  `MeterTests.test_meter_through_the_hazard_pack_driver_flags_the_member_it_lost`) are the pre-existing meter cases that
  need a quiet machine (lane PLAN section 11.4); the Air was at load 70-85. `tests.align.test_v4_arm_watchdog_check`:
  80 OK.
