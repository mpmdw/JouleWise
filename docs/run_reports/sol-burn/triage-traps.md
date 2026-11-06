# Triage of sol/burn-traps (lead-side verification, 2026-11-06)

The citations and numbers check out (21,215 s -> 5,872 s; 82 refits 594/941 s; recompute
first commit ab14e02d8 2026-10-14; zero non-test invocation sites on main). But all
three traps are ALREADY HANDLED on lane/2026-11-06-b5-lean-release (d8c17dff4,
docs/analysis/b5/DEVIATION-LOG.md):
- Trap 1 (recompute unused) and trap 3 (release replay): DLE-1 replaces the release
  replay with scripts/release_b5.py (digest re-verify + independent recompute +
  comparator). DLE-2 makes the recompute the production path from block 6 on.
- Trap 2 (harvest re-reduction vs L9 steps 1-2): this is DLE-3, which the lead explicitly
  declined, because the heavy pipeline is now an off-critical-path audit.
The scope covered only block 5, so this audit adds nothing new. Hunt for traps elsewhere.

## New trap found outside block 5 (local Sol 6.1 second opinion, verified by the lead)
- STALE: `python3 -m unittest discover -s tests` is the "canonical suite" in AGENTS.md:109-110,
  RUN_STATE.md:7486 (Start Here step 8) and README.md:194. It runs sequentially, about 3.2 h of
  recorded module weight outside block 5. Evidence that it costs time: the cloud Sol r0rev and
  w1rev runs both stopped it after more than 25 minutes in test_moe_calibration.
- BETTER: `scripts/shard_tests.py --workers N [--split]` (--help works; CI ci.yml:190-198
  already uses its discovery and timing map). Caveat: plain --workers does not enforce the
  timing map's exclusive_modules, which CI handles separately. The routing doc should say so.
