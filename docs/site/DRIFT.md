# Site drift report (D-068)

Refreshed: 2026-07-17. Automation informs; Ed alone regenerates and deploys
the site.

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
