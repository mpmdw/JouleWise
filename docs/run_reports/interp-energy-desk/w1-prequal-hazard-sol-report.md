Fixed and committed locally:

- `dedf958eb` — production-derived clock budget, missing-field case, and regression tests.
- `ff85d6c70` — [run report](/Volumes/JW-EXT/jw-wt/sol-w1-prequal-hazard/docs/run_reports/2026-11-11-w1-prequal-hazard.md) with production-code citations and every before/after refusal.

Changed only `w1_prequal.py`, its tests, and the report. Production field access is correct. The 14-case CLI probe passes; all 13 original case records are byte-identical to baseline.

Verification: the new witness failed first, then both focused tests passed. All 10 updated `ArmCliTests` passed. **Both complete modules remain unverified**: PREQUAL was interrupted after 10 completed tests and watchdog after 21 to honor the approximate 20-minute budget. No completed test failed.

The lead’s next step is to run these separately to completion:

```sh
python3.13 -B -m unittest tests.align.test_w1_prequal
python3.13 -B -m unittest tests.align.test_v4_arm_watchdog_check
```

No contract questions remain. No native validation claimed. Working tree clean; nothing pushed.