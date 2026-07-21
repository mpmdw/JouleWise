# Site drift report (D-068)

Refreshed: 2026-07-20a (advisor-readability corrections — deploy
priority remains raised). Responding to the professor's direct
feedback: the Status page's audit update is rewritten in plain
language (two-clocks explanation; explicit "nothing measured negative";
short-workload resolution limit stated as a design fact, not a
workaround), a dedicated plain-English explainer ships at
docs/advisor_briefs/2026-07-20-timing-defect-explainer.md, and the
run-report banner phrasing that invited a "-8 J" misreading is
corrected. The deployed capsule still shows the pre-audit claim
posture AND the jargon-heavy update; deploying picks up both fixes.
Standing rule adopted: advisor-facing surfaces use plain language with
defined terms. Three-step: git pull; build_site + pack_capsule; npx
lakebed deploy. Automation informs; Ed deploys.

Prior refresh: 2026-07-19d (SOUNDNESS AUDIT — deploy priority raised). The
live capsule now shows SUPERSEDED claim posture: the deployed Status
page presents the 07-17 floor table uncaveated and the night's corpus
as claim-ready. Repo truth: D-078 soundness gate — a trace-time-anchor
defect makes all existing powermetrics point energies non-attributable
as recorded; the floor table is caveated pending re-adjudication; the
288-bundle corpus is instrument evidence only
(docs/reviews/2026-07-19-measurement-soundness-audit.md). PROJECT_STATUS
carries the superseding update + audit ledger row; RUN_STATE carries the
gate; the Status page split (2026-07-19c note below) is also undeployed.
Because the deployed page overstates claim status, Ed may want to
deploy sooner than usual. Three-step: git pull; build_site +
pack_capsule; npx lakebed deploy. Automation informs; Ed deploys.

Prior refresh: 2026-07-19c (extended clean-provenance window + status-page
split). The live capsule is now BEHIND the repo in two ways: (1)
PROJECT_STATUS gained the night's UPDATE (288 strict-valid,
claim-eligible bundles across runs_recal3/4/5/6; n=10 suite-ABBA cell
complete; provenance gate CLOSED; extraction + P2-037 sole remaining
gates) plus a new dated ledger row; (2) the Status page is now SPLIT at
the tracked `<!-- ADVISOR-PAGE-END -->` marker into professor-facing
project_status.html (~12.2 KB shard, was AT the 30 KB cap) and
project_status_full.html (~21.0 KB shard, cross-linked, no new nav
tab), so the deployed single Status page no longer matches the build
output and the A42 capacity pressure on this page is resolved. Site
parser/capacity tests green (20/20; full suite 1760 OK). Ed's
three-step publishes it: git pull; build_site + pack_capsule; npx
lakebed deploy. Automation informs; Ed deploys. Prior note follows.

Prior refresh: 2026-07-19b (DEPLOY-READY, review-corrected: a three-lens Sol
review corrected two over-promoted claims (floor statistic, -15%
comparison) and surfaced the source-provenance claim gate before
publication; the Status page and baked latest run report carry the
corrected numbers. The planned "Recal Update" tab was REMOVED pre-merge:
the verbatim page costs ~33 KB against ~7 KB of D-076 capsule headroom
(991,722 / 1,000,000 measured as shipped) — the update brief ships as a
self-contained repo artifact docs/advisor_briefs/
2026-07-19-recalibration-update.html instead, and the A42 capacity
right-sizing decision is now formally due. Original note follows,
superseded where it mentions the tab.)

Prior refresh: 2026-07-19 (Ed-requested regeneration carrying the
2026-07-19 re-calibration update — new "Recal Update" top-nav tab
(advisor_update.html, verbatim advisor brief supplement), PROJECT_STATUS
re-calibration section + ledger rows, run_state/latest-report refresh.
All values in the update are labeled preliminary lead-side readout;
verified extraction + P2-037 gate promotion. Site parser/capacity tests
green (project_status.html trimmed to fit its 30,000-byte shard budget —
page is AT capacity; A42 right-sizing decision is nearing due).
Ed's three-step publishes it: git pull; build_site + pack_capsule;
npx lakebed deploy. Automation informs; Ed deploys.)

## Deployed baseline

Ed completed the manual Lakebed deployment represented by commit `b641f26`
(`Site: Ed's manual deploy artifacts`). The deployed site was **CURRENT at
that snapshot**: it included the Window-A floors, advisor-brief-aligned
reader pages, README-first structure, and the interactive Learn guide. This
supersedes the earlier report that described the 2026-07-13 capsule as stale
and awaiting deployment.

## What now postdates that deployment

- The extension-axis roadmap was re-persisted with its real synthesis after a
  forced-report placeholder was caught (`f656c90`), and the lead-run
  DSpark/DFlash feasibility trace landed (`1644663`). The smoke established
  native MLX execution plus per-round acceptance observability; it was not an
  energy measurement or claim.
- D-075 and its research-bank/registry fold-in landed (`4d20aad`):
  DSpark/DFlash candidate riders, on-device quantized-KV work, a named hybrid
  pair, and attached cache/context/kernel/backend provenance riders. These are
  floor-gated agenda entries capped by their existing claim ceilings, not new
  promoted results.
- The retained exploratory inputs landed (`c6cf3e5`), followed by the current
  re-wrap draft: nine strict-valid, collection-usable but claim-evidence-
  flagged OLMoE/Qwen observations and their bundle-cited extraction. The
  reader-facing observations are explicitly exploratory and the model/config
  points are unmatched.
- Consequently, the deployed `readme`, `project_status`, `research`,
  `decision_log`, and `latest_run_report` views predate the corresponding
  source updates. Other deployed pages remain current as of `b641f26` unless
  their own sources changed after that commit.

**RECOMMENDATION: fold these changes into the next natural Ed-manual deploy;
a separate near-term redeploy is not warranted.** The post-deploy delta adds
an explicitly exploratory observation block, feasibility evidence, and
research-agenda bookkeeping; it does not change a promoted claim, close a live
gate, or alter the published floor table. If an advisor review will rely on
the new D-075 agenda or exploratory block before that natural deploy, Ed can
choose to deploy immediately before the review.

The ED-MANUAL-ONLY command remains:

```bash
python3 scripts/build_site.py && python3 scripts/pack_capsule.py &&
(cd site_capsule && npx lakebed deploy)
```

No agent runs that command. The on-site drift banner continues to self-report
staleness between Ed's manual deployments.
