# Site drift report (D-068)

Refreshed: 2026-07-15, audit close-out session. Automation informs; Ed
deploys.

Live capsule state (last deploy 2026-07-13, `7d3ea57`-era snapshot at
854,349 B): STALE against this branch.

Stale sections needing regeneration at Ed's next manual deploy:

- Every generated page is behind the audit fix wave (44+ commits):
  `run_state`, `task_queue` (route now aliases Roadmap per the capsule
  page-set change), `decision_log` (D-066..D-070 + amendments),
  `council_log` (C-033), `risk_register` (R-018), `orchestration`
  (spend guardrails), `project_status`, `readme`, `record`,
  `measurement_methodology` (WO-005/WO-006 contract lines).
- `docs/site/*.html` in this branch were regenerated 2026-07-15
  (deterministic double-build verified) — the deploy step is:
  `python3 scripts/build_site.py && python3 scripts/pack_capsule.py &&
  (cd site_capsule && npx lakebed deploy)` — ED-MANUAL ONLY (D-068).
- Estimated artifact at last local pack: 879,212 B (64.5 KB headroom
  under the conservative budget).

The on-site drift banner continues to self-report staleness to readers.
