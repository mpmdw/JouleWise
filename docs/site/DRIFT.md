# Site drift report (D-068)

Refreshed: 2026-08-01 (REPO AHEAD OF CAPSULE — claim-posture drift).
New since the 2026-07-31 refresh below (capsule still
`dep_2I04CG6tQ4t0mzY7` from `c3e2647`, 2026-07-25):

- (2026-08-01) Both metrology windows collected and salvage-closed:
  window A (`window_metrologyA_20260731`, linearity_ramp 40/40 complete)
  and window B (`window_metrologyB_20260801`, null o0128+o0512 complete,
  additivity 23/24 single-root, clean 2.25 ms bracket). BOTH
  whole-window verdicts FAILED as-issued on distinct machinery
  condition sets — the machinery adjudication COMPLETED as **D-100**
  (2026-08-01): window A is permanently non-claim-bearing (immutable
  calibration-identity error); window B's re-evaluation is licensed
  behind the queued repair. The corpora are banked and intact.
- (2026-08-01) New standing root doc `CLAIMS_STATUS.md` — the single
  home for claim validity state (valid / evidence-bearing / collected-
  blocked / do-not-quote). Any future site build should surface it.
- (2026-08-01) D-098/D-099 recorded: the salvage-close records, the
  clock-anchor knife-edge instrument finding (rate-aware anchor design
  queued; publishable metrology limitation), the bird-SIGSTOP window
  protocol, the TM-attribution false-proxy retirement, and the
  operator-streaming measurement hazard; C-039 addendum III (the
  in-window consult that refuted the lead's mechanism).
- (2026-08-01) Queue: `MET-WINDOW-C-01` (metrology remainder window)
  blocked on the D-100 repair (`MET-DANGLER-DISPOSITION-01`) + Ed §5A.
- (2026-08-01) D-101: the site gates nothing — the CI release-chain job
  is advisory, DRIFT refreshes are optional, and site budgets never
  reshape governed records.

Prior refresh (2026-07-31, REPO AHEAD OF CAPSULE — claim-posture drift).
The deployed capsule is still `dep_2I04CG6tQ4t0mzY7`, built from main
`c3e2647` (2026-07-25); no agent has deployed since, and none will
(D-068). Since that snapshot the repo gained front-facing state that the
live site does not show:

- D-078 clause 11 merged (`3055315`): attribution-limited floors are a
  LABELLED claim path, not a refusal, and every publishing artifact must
  carry the single-count statement (effective clearable effect = floor +
  claim-side bound).
- Windows C, D, a10, the 7B floor window, and the contrast window
  PASSED; window B failed on bracket drift and is preserved, not
  claim-bearing.
- The floor mint exists and has been exercised: PR #86 (CAL-REBRACKET),
  PR #87 (pre-mint schema hardening), and PR #88 (FIX-1..10 gauntlet +
  mint #1 `df-ph-decode-floor-mint1`, merged `da83337` 2026-07-30).
- A second claim-bearing window, `window_7bfloor_20260729` (Qwen2.5 7B
  decode floor), collected and PASSED on 2026-07-29.
- (2026-07-31) The Splitwise contrast window `window_contrast_20260730`
  collected and PASSED — 47 bundles, bracket drift 1.281 ms — with the
  7B−1.5B decode contrast at 146.730349 J (σ 0.241 J, n=10 blocks) as a
  DIAGNOSTIC only; the gated claim is UNGATED and blocked on
  `MANIFEST-CONTRAST-01`.
- (2026-07-31) D5-J, the structural cooldown-join redesign, merged via
  PR #89 under the D-093 cold-gate synthesis, which also added the
  standing raw-vs-validated supersession-record scan to every claim
  consumption.
- (2026-07-31) Decisions D-089 through D-093 and C-039 addendum II; the
  metrology pivot (D-091) is the project's new framing — the measurement
  instrument itself is the product; the paper outline v1 is archived at
  `docs/run_reports/2026-07-30-paper-outline-v1.md`.
- Decisions D-079 through D-088 and council entry C-039 (+ addendum).

**DISCHARGED 2026-07-31:** the prior refresh's deploy-blocking caveat —
`PROJECT_STATUS.md` stale since 2026-07-24 (`1af9f92`), still saying "the
first claim-grade floor is still ahead" — no longer holds. That page was
refreshed at `6ed1625` and now carries the mint, the passed windows, and
the metrology framing.

**New deploy-relevant caveat (2026-07-31):** `README.md`, the
front-facing landing text, still carried the pre-mint posture ("the next
step is one clean prospective quiet-machine window … first claim-grade
floors before the a8 re-verdict") until it was refreshed THIS session;
it is now current (mint #1, five passed windows, contrast collected,
metrology framing). Likewise, `PROJECT_STATUS.md`'s Update Ledger was 12
days behind — its newest row was 2026-07-19 — and was brought current
this session with the 07-22, 07-25, 07-29, 07-30, and 07-31 rows. Both
surfaces are deploy-ready as of this refresh. No other action is
recommended to an agent; Ed deploys.

Prior refresh: 2026-07-30 (the mint-era entry; its content is carried
forward and superseded by the 2026-07-31 entry above).

Prior refresh: 2026-07-25 (the then-CURRENT DEPLOYED BASELINE). Ed redeployed the
capsule from merged main `c3e2647` (plus the same-day bookkeeping
refresh: gauntlet run report, C-033, refreshed status surfaces, and the
council-log capsule redirect) as `dep_2I04CG6tQ4t0mzY7`; the capsule
configuration timestamp is 2026-07-25T02:44Z (the deployed page's own
copy of this stamp may read one deploy older — stamp-then-deploy
ordering artifact, not drift). This deployment
includes the repaired-instrument collection story, the ratified and
merged PR #85 SCREEN+BUDGET rules, the gauntlet report, and the
decision-log pagination/capsule repair. No deployment is outstanding:
all deploy recommendations below are retained as history and are now
fulfilled or retired.

Prior refresh: 2026-07-24 (COLLECTION ERA — repo far ahead of capsule).
Since the last deploy the repo gained: the merged repair PRs #79-#84,
two nights of collection (229 members, four bracketed windows), the
NEG-8 drift-gate redesign (debated, Ed-ratified, D-078 clauses 8-10),
a new plain-language PROJECT_STATUS collection-era section, the
2026-07-23 collection-arc run report, and council entries C-031/C-032.
Historical recommendation (fulfilled by the 2026-07-25 deployment):
deploy at the next natural point. Ed deployed before the first
claim-grade floor table because PR #85 and the capsule repair were
already complete.

Prior refresh: 2026-07-22 (INSTRUMENT REPAIR SIGNED OFF — the good-news
counterpart to the 07-19d alert below, which remains partly operative
until deploy). Repo truth now AHEAD of the live capsule: the D-078
instrument repair is complete and signed off (nine adversarial
confirmation rounds; PR #79 open for Ed's merge), PROJECT_STATUS
carries a new plain-language "REPAIR COMPLETE" advisor section (timing
fix with explicit ~27 ms error bar, calibration authentication,
fail-closed refusals, one honestly-registered limitation L1), and
RUN_STATE/the roadmap show Phase 0 complete with Phase 1 re-collection
next. The live capsule still shows the superseded 07-17 claim posture
AND none of the repair story. Deploy timing is Ed's call; note the
07-19d overstatement concern is best cured by deploying AFTER PR #79
merges so the capsule picks up the full corrected posture in one step.
Three-step: git pull; build_site + pack_capsule; npx lakebed deploy.
Automation informs; Ed deploys.

Prior refresh: 2026-07-20a (advisor-readability corrections — deploy
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

**HISTORICAL RECOMMENDATION (fulfilled by the 2026-07-25 deployment): fold
these changes into the next natural Ed-manual deploy.** The post-deploy delta adds
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
