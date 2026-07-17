# Site drift report (D-068)

Refreshed: 2026-07-16, resumption + no-hardware batch session (PRs #67/#68/#69
merged: AXI-SA burst-decode contract, SITE-02 D1/D2 closure, SPLIT-AP freeze;
AXI-SB static-batch verdict `supported` with the Mac C5-2.2 leg mint staged on `impl/axi-sb` (pending merge); kernel/queue
closures; run report `2026-07-16-resumption-nohw-batch.md`). Automation
informs; Ed deploys.

Additional 2026-07-16 staleness on top of everything below: the generated
`run_state`, `task_queue` / `roadmap`, `record`, `research`, `risk_register`,
`council_log`, and `latest_run_report` pages now also predate today's AXI-SA/
SITE-02/SPLIT-AP landings, the AXI-SB `supported` verdict (+ its staged C5-2.2 Mac-leg mint, pending
merge), the R-016 body addendum, and this session's run report. SITE-02 also
changed `scripts/pack_capsule.py` discovery behavior (loud refusal, never
silent estimator fallback) — Ed's next manual deploy exercises the new
discovery path; the deploy command below is unchanged.

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
  harness-versus-benchmark split, or the D-070 five-axis Q4 stress-test
  agenda now present in their source documents.
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
