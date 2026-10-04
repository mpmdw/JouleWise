# Consult brief: block 2 (G2-a prefill probe) stopped after w2 RECOVER — what next? (registration §7)

Seat: blind consult seat (one of two: Sol 6.1 and Opus 5.5; you do not see the other seat's answer).
Read-only. You have explicit licence to disagree with anything below, including the framing.

## Situation (read the files; do not trust this summary)

- Registration (sealed): `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md`.
  §7: "If the recovery window also ends RECOVER, the block stops and the question goes to a
  consult (Sol 6.1 plus Opus, blind), then to the orchestrator's ruling." That is this consult.
- w1 (plan `d117-g2a-prefill-probe-20261003T0820Z`): chain crashed at the first member on a code
  defect (controller refused the pre-bracket capture); RECOVER with capture_made true; fixed by
  PR #461. Records: `docs/process_traces/2026-10-03-activation-a7a0ed6a/`,
  `docs/process_traces/2026-10-03-activation-adaebcc6/`.
- w2 (plan `d117-g2a-prefill-probe-20261003T1748Z`, the one recovery window): the chain ran
  small-p512 and small-p1024 (5 members each) and small-p2048 r01, r02; r03 failed in stage
  `idle_baseline` ("idle environment admission failed after one retry", both attempts failed only
  on `cpu_busy_ratio_p95_exceeded`, 1.0 and 0.896 vs limit 0.5), `--max-failures 1` stopped the
  campaign, chain exit 1; nothing after ran (no p4096, no large stages, no post bracket).
  Diagnosis (Sonnet, read-only, ≈85 % confidence on the process): macOS background maintenance
  scheduled by `dasd` 4 s before r03 (`mediaanalysisd.photos.maintenance`,
  `duetexpertd.anchormodeldataharvesting`); E-cluster CPU 0 ≈85 % busy across both attempts;
  attempt 2 starts ≈0.5 s after attempt 1, so the retry cannot outwait a multi-minute burst.
  Record: `docs/process_traces/2026-10-03-activation-5bffbeaf/00-session-record.md`.
- w2 harvest first REFUSED on a tooling fault (summary provenance compared raw vs runner-normalized
  config bytes), fixed by PR #463; re-harvest verdict and cause codes:
  re-harvest at main `28b78580` into `~/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2/harvest.json` (sha256 `e40583983c95ea2df0edff0854177a273cfac0c1fd3fbbe0a0fea10133fe756b`): verdict RECOVER, cause codes `bracket_incomplete`, `chain_nonzero_or_missing_exit`, `rung_valid_small_members_shortfall`, capture_made true; members 12/24 valid; every valid member's `clock_anchor_status` is `bounded`, the 12 others ran nothing (`not recorded`). You may read `harvest.json` (it holds no overlap count) and the night logs under `/Users/edr/night-custody/d117-g2a-prefill-probe-20261003T1748Z/`; nothing under `derived/` except `bracket.json` and `network-time.json`.

## Blindness (registration §10) — binding on you

Do NOT open any per-member overlap count, any row of either window's summary
(`summary*.json`, counts receipt), selection output, energy, fiducial bound or drift value.
You may read cause codes, `clock_anchor_status`, admission/idle-baseline logs, chain logs,
code, and the records named above. Your recommendation must not depend on what the partial data
would have selected.

## Questions

1. **Next step for the prefill-length question.** Options include (not exhaustive): (a) a new
   sealed block (block 3) with the same window shape, re-registered, after removing the cause;
   (b) the D-166 fallback (collect `_v5` prefill at 4096) without a completed probe; (c) anything
   else you judge better. For each option say what the registration/D-166 text permits, what a
   cold gate would need to seal, and the cost in windows (each window ≈5.5 h wall).
2. **The removable cause.** Is the idle-admission failure a machine state removable by re-arming,
   a design flaw in the admission retry (back-to-back retry cannot outwait a maintenance burst),
   or both? Name the smallest change that removes it without weakening the quiet-machine bar:
   e.g. a bounded wait-and-retry before the idle baseline, a pre-window check that macOS
   maintenance (`dasd` activities) is not due, or disabling the specific maintenance
   (Photos analysis, Spotlight knowledge) for the window. Give file:line for where it lives.
   Note: Ed's rule — before building enforcement, ask whether one setting or command removes the
   hazard.
3. **`--max-failures 1` per stage.** One failed member stops the whole chain. Is that the right
   design for a diagnostic probe, given §7 forbids re-collection inside a window? Would a design
   where a member failing *before any capture* (idle admission) gets a bounded in-window retry
   violate D-078 "never re-collected"? Argue from the text.
4. Anything in the w1/w2 records that suggests a systematic, non-removable cause (registration §7
   example: most clock anchors not `bounded`).

## Output

A single markdown answer: a recommendation (one option, with the reasons), the cause ruling,
the smallest concrete change list with file:line, and dissent/risks. ≤ 900 words. Do not edit
any file. Cite file:line for every factual claim about code.
