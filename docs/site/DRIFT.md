# Site drift report (D-068)

Refreshed: 2026-07-17 (SITE SOURCE READY FOR ED'S DEPLOY: PR #75 merged —
README-first structure with measurements last + the new interactive Learn
guide on /research; capsule verified 905,568 B conservative estimate /
876 KB Lakebed-validator-measured, under cap with headroom restored. One
manual deploy publishes: floors + Window A state, advisor-brief-aligned
numbers, Learn section, all of this week's landings. Deploy command
unchanged (below). Automation informs; Ed deploys.)

Additional 2026-07-17 staleness on top of everything below: the deployed site
predates P2-038's merged-main production-shaped pass, the Window-A floor corpus
(222 distinct strict-valid, collection-usable but claim-evidence-flagged
bundles), the independently verified request/phase/suite floor table, the
AXI-SC `unsupported_for_joulewise` verdict, and the shipped advisor brief at
`docs/advisor_briefs/2026-07-17-window-a-brief.html`. It also predates the
current `README.md`, `PROJECT_STATUS.md`, and draft overnight run report.

Live capsule state (last deploy 2026-07-13, `7d3ea57`-era snapshot at
854,349 B): STALE against this branch.

Stale sections needing regeneration at Ed's next manual deploy:

- Every current site page is stale against the source and audit wave. The full
  page set is: `index`, `status`, `roadmap`, `record`, `results`, `process`,
  `research`, `library`, `readme`, `project_status`, `agent_plan`, `run_state`,
  `task_queue`, `risk_register`, `adapter_contracts`,
  `measurement_methodology`, `claims_ladder`, `orchestration`, `decision_log`,
  `council_log`, `milestones`, and `latest_run_report`.
- The generated `index` and `results` pages specifically still contain both
  confirmed reader-facing defects: they conflate the benchmark with the
  measurement harness, and they use idle-subtracted energy to rank
  configurations. Ed's regeneration must replace both defects with the D-067
  gross-headline / named-boundary rule and the D-069 terminology split.
- The generated `project_status`, `status`, and `readme` pages do not yet
  contain the D-067 gross-headline / named-boundary wording, the D-069
  harness-versus-benchmark split, the D-070 five-axis Q4 stress-test agenda,
  P2-038 closure, or the published Window-A floor/caveat summary now present in
  their source documents.
- The generated `results` and `latest_run_report` pages do not include the
  verified floor values or their evidence ceiling: strict-valid and
  collection-usable does not mean claim-ready; P2-037 adjudication remains
  pending, short prefill is smoke-only, optional long-request floors were not
  run, and ABBA tails carry drift/ordering caveats.
- The current capsule has no page for the shipped Window-A advisor brief. Ed's
  next manual publication decision must either add it deliberately or leave it
  repository-only; this drift report does not prescribe a new site route.
- The generated `research` page does not yet reflect the D-067
  C-023-IDLE-STATIONARITY framing note or the aligned C5-1.1/static-batching
  bank text. Generated library/provenance surfaces likewise predate these
  source edits.
- The generated `run_state`, `task_queue` / `roadmap`, `decision_log`,
  `council_log`, `risk_register`, `orchestration`, `record`, and
  `measurement_methodology` pages still predate their named audit-wave source
  updates; the remaining pages in the full set above inherit the same stale
  snapshot and provenance stamps.
- The ED-MANUAL-ONLY regeneration and deploy command is:
  `python3 scripts/build_site.py && python3 scripts/pack_capsule.py &&
  (cd site_capsule && npx lakebed deploy)` — ED-MANUAL ONLY (D-068).

The on-site drift banner continues to self-report staleness to readers.
