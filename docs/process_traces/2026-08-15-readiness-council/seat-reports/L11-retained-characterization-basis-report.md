# L11 — RETAINED CHARACTERIZATION BASIS (a9/a10 attribution-limit exhibit)

**Seat:** 11 (NON-GATING, publication-basis; charter amendment 13) — effort high
**Charter:** docs/process/instrument-readiness-audit-charter.md (v2 RATIFIED, read first; anti-ritual packet below)
**Audit baseline:** docs/process/audit-baseline-manifest.json — `head_commit ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`. Worktree HEAD at audit time: `8937dec` (three post-baseline commits: the manifest itself + two T7 checkpoint commits touching only README's activity blurb, RUN_STATE.md, and the manifest). I diffed `ac3fe1d..HEAD`: **no file in this seat's evidence universe changed** (docs/paper/, docs/decision_log.md, joulewise/, configs/floor_mint/ untouched; README's a9/a10 lines 58/136 unchanged). Baseline invalidation does not affect these results.
**Question for this seat:** is the characterization the paper leans on — the ±31 ms / ~33 W / ~1 J attribution-limit chain — exactly what the retained a9/a10 artifacts hold? Re-derive it from the retained bundles.

## Verdict: NOT-READY (publication basis) — 3 work orders

The quantitative chain **re-derives cleanly and the attribution-limited conclusion is robust** (every number reproduced below, several bit-for-bit). What fails the exactness bar is the paper's *framing* of the chain: the triple is presented as "the measured corpus figure" when it is a single-member maximum plus a derived quotient, the phase evidence is attributed to a window (a9) that holds no phase members, and the PASSED-verdict context survives only as prose. All three are cheap, wording/retention-level fixes; none is a blocker; none touches the launch GO (this seat is outside it).

## 1. Evidence universe (enumerated before findings) — 16 items

1. docs/paper/draft-v1.md a9/a10 attribution statements — 6 sites: L7 (abstract), L108, L112 (Fig 2 caption), L137, L234, L240
2. docs/paper/figures/README.md + fig1_boundary_attribution.svg (illustrative-values discipline)
3. README.md L58/L136 and CLAIMS_STATUS.md a10 references
4. docs/decision_log.md D-054 attribution-limited amendment (2026-07-25, ~L4671-4715) — the chain's home derivation
5. /Users/edr/code/JouleWise/runs_window_a10_20260725 — 30 phase-absolute science bundles (summaries, traces, events, calibration, raw plists)
6. same dir — 7 in-window reference bundles (neg8-window-start/mid/end)
7. /Users/edr/code/JouleWise/runs_window_a10_20260725_bound — 12 refcorpus bundles + neg8-drift-bound.json
8. runs_window_a10 instrument_validation — 3 captures (pre-cal, failed post-cal, post-cal retry)
9. /Users/edr/code/JouleWise/runs_window_a9_20260724 — 7 reference bundles + MANIFEST.sha256 (202 entries) + PRUNED.md
10. /Users/edr/code/JouleWise/runs_window_a9_20260724_bound — 12 refcorpus + neg8-drift-bound.json
11. ~/JouleWise-window-custody/window_a10_20260725 — CLOSE_OUT.md, detection-floor-extraction.json (mtime in-window 2026-07-25), 5 operator logs
12. ~/JouleWise-window-custody/window_a9_20260724 — 4 operator logs, quarantine (partially examined)
13. ~/JouleWise-window-plans/window_a10_20260725/extraction_spec.json + repo configs/floor_mint/a10_extraction_spec.json
14. joulewise/detection_floor.py — D-054 floor + dominance machinery (EXECUTED over retained data)
15. joulewise/whole_window.py — drift-bound/verdict machinery (surveyed)
16. iCloud archive mirrors (~/Library/Mobile Documents/.../JouleWise-backup/window_a10_20260725; a9 per PRUNED.md)

## 2. Coverage: 14 / 16

All 68 retained member-bundle summaries across items 5–10 were read and processed (30 science + 7 + 12 + 7 + 12). Items 12 and 16 partially examined (listed/surveyed, not deep-read). Unexecuted obligations, plainly: (a) exact trace re-integration for 29 of 30 science members (1 done bit-for-bit; the rest accepted from sha-verified summaries); (b) code audit of the reducer's envelope-v3 implementation (output re-derived numerically instead); (c) whole_window.py deep audit; (d) a9 custody operator logs; (e) campaign_log.jsonl / raw plists; (f) iCloud byte-parity.

## 3. The re-derived chain (positive probes, all executed)

**±31 ms.** Composed clock-anchor bound per member = fiducial + bundle-local + edge span. Retained pre-cal capture: `b_fiducial_s = 0.024879192` (log's 24.9 ms ✓). Member prefill-abs-r01: `anchor_bound_s = 0.0310738` = 24.879 + 6.195 ms (bundle-local + 0.12 ms edge span; log's 3.3–6.1 range ✓). **Corpus-wide (30 members): 25.62–31.07 ms, mean 27.3 ms — ±31 ms is the maximum, held by exactly one member.**

**~1 J.** Recorded prefill envelope for r01: `max_abs_delta_j = 1.0160 J`. I re-integrated the retained power_trace.csv (cpu+gpu+ane) over the events.jsonl phase window: prefill energy reproduces **bit-for-bit** (50.84663670868063 J); sweeping the boundary by ±b gives common-shift 0.961 J and independent-corner 1.029 J, **bracketing the recorded 1.016 J** (method: common shift + independent edge corners). Corpus-wide operative-phase envelopes: prefill cell 0.98–1.47 J, decode cell 0.75–1.13 J, short-prefill 0.57–0.92 J.

**~33 W.** No retained artifact records a 33 W step. 33 W = 1.016 J / 31.07 ms = 32.7 W — the envelope/bound quotient of that same single member. Corpus-wide quotients: ~21–58 W. r01's trace-measured prefill-vs-decode mean-power step is 18.6 W (45.6 → 27.0 W); at 100–310 ms scales the boundary step is 11–23 W. The dimensional story is right; the specific "33 W" is derived, not measured.

**Attribution-limited, not noise-limited.** Executed the project's own `absolute_false_effect_floor` + `admissible_set_uncertainty_dominates_point_floor` over the retained values: point floors **0.2888 / 0.4934 / 0.3113 J** — the D-054 log's "0.29–0.49 J on ~50 J points" reproduces exactly — and **dominance = True on all three cells** (corner-widened floors 3.153 / 2.922 / 2.184 J). Repeatability (stddev 0.12–0.21 J on ~50 J points) is indeed smaller than every member's envelope. Paper L108's comparative claim re-derives.

**Bracket-calibration context.** Post-cal retry `b = 0.025045995` (Δ +0.1668 ms = log's +0.167 ✓); the preserved failed attempt shows `all_pulses_detected: false` (deviation narrative ✓). Drift allowances in the retained bound artifact (0.6523/0.6579 J) match the close-out ✓. Custody: 30/30 science summary+config sha256 match the custody extraction; a9 MANIFEST re-hash 173/173 resident files clean, 28 missing = exactly the pruned plists.

**Whole-window PASSED (context).** No verdict artifact is retained anywhere findable — but the excursions re-derive exactly from retained references: a10 max pairwise excursion among start-mean/midpoint/end-mean = **0.5094 J in both families** (close-out: "0.509 J both families") vs allowances 0.652/0.658 J; a9: 0.310/0.305 J vs 0.624/0.609 J. Both pass.

## 4. Executed falsifiers (negative probes / READY-falsification)

- **F1 tamper:** flipped one digit in a scratchpad copy of a science summary → recorded sha no longer matches. Silent modification of the basis would be caught. (Outcome: detection works.)
- **F2a hardcoding check:** re-ran the floor machinery with envelope widths forced to zero → dominance flips to False and a 0.2888 J noise-only floor would publish. The attribution-limited conclusion is data-driven, not baked in. (Outcome: falsification attempt fails as it should.)
- **F2b bracket hold:** scaled widths by the post/pre fiducial ratio (×1.0067) → dominance still True (3.173 J vs 0.289 J gate). The unresolved max-bracket hold cannot overturn the characterization. (Outcome: robust.)
- **F3 corpus wording:** hunted a9 for any phase-absolute member → none exist (7 request-level refs, bounds 30.0–33.5 ms, + 12 refcorpus). (Outcome: finding SF2.)
- **F4 log detail:** scanned all 38 retained refs pairwise for the "0.007 J at three hours" pair → no unique match (best: 0.0013–0.0019 J gross at ~3.7 h). (Outcome: nit N2.)

## 5. Findings

**SF1 (should-fix) — draft-v1.md:108, :112 (also :7, :240).** "The measured corpus figure is ±31 ms across ~33 W" / "at corpus precision" overstates provenance: ±31 ms is the single widest member's composed bound (corpus 25.6–31.1 ms), ~33 W is that member's envelope/bound quotient (corpus quotients 21–58 W; r01's measured mean-power step 18.6 W), ~1 J is the low end of the prefill-cell envelopes (0.98–1.47 J). Failure scenario: a metrology referee asks which artifact records 33 W; none does. Fix: state ranges, or pin the triple to its defining member and derivation.

**SF2 (should-fix) — draft-v1.md:7, :108, :240.** The phase mis-attribution evidence is attributed to "the a9 and a10 windows"; a9 holds zero phase members. Failure scenario: reviewer requests a9 phase members; none exist (and a9's ±33.5 ms ref bounds would strain the ±31 ms headline if counted). Fix: a10's 30 phase-absolute members are the basis; a9 is reference/bracket context.

**SF3 (should-fix) — custody CLOSE_OUT.md / retained extraction.** The a9/a10 whole-window PASSED verdicts are prose-only; the retained extraction itself refuses `whole_window_neg8_verdict_missing`, and no verdict artifact exists locally, in custody, in-repo, or in the iCloud mirror. Mitigation shown above: excursions re-derive exactly from retained refs. Fix: commit that re-derivation beside the close-out (or recover the original artifacts), or strip PASSED context from consuming docs.

**N1 (nit) — a9 MANIFEST.sha256.** Lists `./backup.log`, neither resident nor covered by PRUNED.md's 28-plist enumeration (29 missing vs 28 authorized).

**N2 (nit) — decision_log.md D-054 entry.** "Settled pair 3 h apart, 0.007 J" not uniquely reproducible; "fiducial 24.9 ms (80–87%)" is actually 80–97% across members. Neither is paper-cited.

## 6. Work orders

WO-1 reword the triple as ranges or pin it (SF1); WO-2 fix the a9 attribution (SF2); WO-3 artifact-back the PASSED context (SF3); WO-4 optional N1/N2 bookkeeping.

## 7. Ed-qualification rows

None — this seat required no hardware, sudo, or live measurement; the entire chain re-derived at the desk from retained artifacts.

## 8. Exit state

Worktree left byte-identical: `git status --porcelain` empty at HEAD `8937dec`; all scratch work under the session scratchpad. Retained corpora at /Users/edr/code/JouleWise/runs_window_a9_20260724[,_bound] and runs_window_a10_20260725[,_bound] and ~/JouleWise-window-custody were read-only.