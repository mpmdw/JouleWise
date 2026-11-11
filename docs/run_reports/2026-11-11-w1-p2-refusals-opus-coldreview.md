# Cold review: `ops/2026-11-11-w1-p2-refusals` @ `787df335f` (P2, groups A and B applied; C proposed)

Independent Opus subagent, read-only, 2026-11-11. **Verdict: ADMIT** (two advisories, no fixes).

- `tests.hazards.test_refusal_allowlist` on the branch: 2 failures whose residue is exactly the C frontier: 3 unlisted
  keys (C01 `driver._run_hazard_night_body <reraise>`, C02 `_decide FENCED`, C03 `_decide HOLD_UNSAFE`), 2 counts
  (C04, C05), 2 guard changes (C06, C07), 11 scope edges (C08-C18). No stale entries; the BASELINE/frozen test passes.
- Added entries (42): about 20 read in depth at the presign tree. A03 `joulewise/b5/driver.py refuse|meter` (PHYSICS)
  is the two pre-chain meter refusals (live probe, first valid batch); later outages only flag; consistent with
  `refuse|monitor` precedent (caveat: the probe's broad `except` turns a software error into a refusal, as the existing
  `refuse|arm` does). Run-night, courier, dead-man and watchdog entries accurate; commits confirmed with `git log -S`.
- Removed entries (15): all renames or extractions (`decide`->`_decide` 21029737a, `arm_only`->`_arm_only_admission`
  3c9c47a4e, `dead_man`->`_dead_man` 19a862dc8, `main`->`_run` c6ea47ebe); each replacement re-listed with identical
  guard and count, except B05 FENCED, which correctly stays C02.
- 13 entries move from BASELINE to INTERNAL on rename: mechanical, because the baseline digest hashes the function name
  and a renamed key cannot stay BASELINE. **Advisory (lead acknowledges):** their new protection texts are the first
  individual review of these sites; read and found accurate.
- No existing entry's count, guard or category changed; the scan section is untouched; nothing added to BASELINE.
- Advisory: A01's protection text names only the `align_v4_session.prepare` caller; `w1_smoke.py:965` also calls it and
  catches the error.

The 18 C items are proposed diffs in `docs/run_reports/2026-11-11-w1-p2-refusals.md`, for the research lead.
