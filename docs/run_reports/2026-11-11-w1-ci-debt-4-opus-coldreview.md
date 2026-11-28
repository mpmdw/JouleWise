# Cold review: `ops/2026-11-11-w1-ci-debt-4` @ `2025c52c1` (rounds 1 and 2)

Opus 5.5, interim lane lead, 2026-11-11. **Verdict: ADMIT (test-tree only); three production items parked.**

- Scope: 34 test/fixture files under `tests/` and the report; no file under `joulewise/`, `scripts/` or `configs/`
  changed (checked with `git diff --stat`). The lead's template-cache fix `cb7d0af08` is cherry-picked unchanged.
- Spot-checked for loosening: `test_magistrate_watchdog_cli` (`HOLD_LOCK`, `HOLD_PLAN_MALFORMED`, the admitted split
  holds of `21029737a`, all other assertions kept); `test_battery_float_consumers` (an exact-site exception for two
  `snapshot['parse']` reads in `watchdog_acceptance`, with a new negative test that the same text elsewhere, and a
  `getattr(battery_float, ...)`, still trips); `test_lane_adapters` (native courier test kept on Darwin; its fixture
  supplies the authenticated delivery receipt that `c80d4d638`/`454d78142` made mandatory); the thermal-sidecar
  re-pin (the seat reproduced old and new bytes at the named admitted commits: driver at `b4a6c217f`, harvest at
  `2127e00bd`, matching `e01743ae4`'s audit).
- Not green locally: several whole-repo scans and the full Cartesian terminal grid hit the seat's caps. CI on #734 is
  the evidence.

## Production items, parked (not changed)

1. **P1** `configs/b6/executing_reviews.json` lacks executing-review rows for the eight admitted W1 commits
   (`19a862dc8`, `2127e00bd`, `454d78142`, `5bb152acc`, `5dc2d4b48`, `b4a6c217f`, `c6d25d963`, `ebe3d56a7`);
   `tests.b6.test_audit_record_fixes` stays red. Needs authentic rows; never invented.
2. **P2** `configs/gates/hazard_refusals.json`: 45 unlisted sites, 15 stale, 2 counts, 2 guard digests, 11 scope gaps
   against the admitted source; `tests.hazards.test_refusal_allowlist` stays red. A registration/ruling change.
3. **P3** `joulewise/t0_rehearsal.py:670` qualification registry lacks the NTP getter (`scripts/run_night.py:4479`)
   and terminal-delivery Git calls; `tests.test_v5_block4_x12b` stays red. A bound production edit.
