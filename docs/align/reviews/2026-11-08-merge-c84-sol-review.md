# Review citation: merge c84df94bf (harvest-off lane into the v4 line)

2026-11-08. A citation record for `configs/b6/executing_reviews.json`; it reviews nothing itself.

- **Reviewed object:** merge `c84df94bfd38e7c29b083fe6629217eddaab94b3` (parents `94d3dcb3e` v4 line and
  `d5dc1198c` harvest-off), the five conflict resolutions in `scripts/align_pilot_session.py`,
  `scripts/align_v4_next_arm_packet.py`, `scripts/align_v4_series.py`, `scripts/align_v4_session.py` and
  `docs/align/pilot_protocol_v4.md`, and the 14 jointly changed paths.
- **Reviewer:** Sol 6.1, `docs/align/v4/MERGE-C84-REVIEW-sol.md`, sha256 `fdfef957a8307a9ec67db3b3ceb77392e9972f9e9fc7159b6c5e3e43a4e68ca5`, branch
  `align/2026-11-08-merge-c84-sol` @ `71a18a46b`, witnesses `tests/align/test_merge_c84_sol.py`.
- **Verdict: HOLD** on one reproduced defect (F1): R17 finality did not understand R22-1 disclosure-only records,
  so a valid contention-only desk could never be final. The review found the provisional-window adjustment
  (`has_final_sources()`) sound, and all 96 v4-only and 31 harvest-only changed paths byte-identical to their parent.
- **Repair:** commit `f455366162ffab6bcf7ecc4b5039f3b7d37f0c15` on `align/2026-11-08-v4-r11`: one disclosure-aware
  comparison (`v4_contention.recorded_exclusion_map`) shared by finality and `effective_desk`. The witness module is
  in unmodified and green (3 tests), with real-exclusion controls still refusing, plus
  `tests/align/test_final_disclosure_agreement.py` (6 tests). The repair was not itself re-reviewed.
