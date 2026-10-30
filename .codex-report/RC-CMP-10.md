STATUS: BLOCKED in progress (milestone 2 of 3: fixes pushed; probes and the final report pending)

# RC-CMP-10 (in progress)

- Merged origin/main into the lane (ab4029f7b; no conflicts).
- Fixes for FS1-FS4, OPUS F1-F2, FABLE F1-F4 and the literal pins are in scripts/compare_b5_recompute.py, with
  tests/independent_recompute/test_rc_cmp10.py (new) and the fixture/test updates listed in the final report.
- Suite before this commit: 393 tests, 4 subtests failing in one generic-deletion case (nested-locator order in the
  test harness), fixed in this commit; the final suite run and the probe reruns follow.
