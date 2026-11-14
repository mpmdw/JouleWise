# PR #784 review record: README landing page

Date: 2026-11-14. Light-tier check failed honestly: the README restates Paper 1's released numbers and outcome sentences, so Impact line (vi) is Yes and the PR is full tier. Two reviews ran on head `a982d89c4`; all fixes were applied verbatim in the next commit.

## Dispositions (gate row 5)

| Source | Finding | Disposition |
|---|---|---|
| Row 1, F1 / row 4, F3 | Prefill floor printed 8.83 (absolute floor) instead of the 8.84 floor gate; intervals rounded inward | Fixed: Figure 5 and its alt print the paper's digits (146.63 [141.35, 151.91], 101.81 [95.80, 107.82], floor gates 10.18 and 8.84) |
| Row 1, F2 / row 4, F1, F5 | Dominance implied; detection-floor and dominance-ratio definitions stronger than the paper | Fixed with the research lead's wording: floors set by the clock-anchor bound, registered dominance test not met, no statement on the limiting source; definitions from §1.2 and §4.5–4.6 |
| Row 1, F3 / row 4, F6 | "about 45–49 ms" not in the paper | Fixed: removed |
| Row 1, F4 / row 4, F9 | BYTES commitment date not in the paper | Kept per the research lead (commitment exists, RUN_STATE item 291b, commit 569591e53); sentence tightened to "energy was unblinded" and the disclosed timing read added |
| Row 1, F5 / row 4, F1 | Derived "11–14 times" and "94–96 %" | Fixed: removed; replaced by the registered gate statement |
| Row 1, F6 | "not news" sentence not in the paper | Rejected per the research lead (row 4: "within the paper") |
| Row 1, F7 / row 4, F11 | "from the wall" conflicts with the DC-input boundary | Fixed: "It cannot edit the joules it drew." |
| Row 1, F8 / row 4, F11 | Tripwire "no outcome has been opened"; stale linked page | Sentence kept per the research lead; the linked page's stale lines are deferred to a follow-up correction of docs/research/energy-tripwire.html |
| Row 4, F2, F4, F7, F8, F10, F12, F13 and small fixes | Replication gloss; separate-sessions disclosure; Figure 6 steps; sealing sentence; card status; how-it-is-run paragraph; machines limit; powermetrics wording; Figure 4 alt | Fixed verbatim |

## Row 1: executing review (independent seat)

Gate-row-1 review of PR #784 (head a982d89), run 2026-11-14 11:43 PST (`date`).

**VERDICT: ADMIT WITH FIXES.** The headline numbers, the schematic labelling and the SVG safety all check out. The tripwire is not overstated. Four claims are not backed by the paper text, plus one 0.01 J mismatch and two doc-hygiene items. None is a safety issue.

## Findings

1. **MEDIUM, prefill floor "8.83" (README Figure 5 alt text; fig5 light and dark SVG text "floor 8.83"; task prompt).**
   - Paper Table 5, §6.5: "| prefill (2,048) | 5 of 10 | 101.81 | … | [95.80, 107.82] | 8.84 |". It repeats "floor gate of 8.84 J" in the result sentence and in "95.80 J against 8.84 J".
   - 8.83 is the primary block's *absolute* prefill floor, Table 6 ("Absolute floor, prefill (2,048) (J) | 8.83") and §6.8 "(10.18 and 8.83 J)". The contrast floor gate is 8.84. Decode's 10.18 is the same in both.
   - Fix: change "8.83" to "8.84" in the README alt text and in fig5 (the `build_readme_svgs.py` source and both SVGs).

2. **MEDIUM, README omits that dominance was not established, and mixes up two ideas.**
   - README: "a **dominance ratio** (whether timing, rather than noise, sets that floor)" and "About 94–96 % of each interval's width is the deterministic timing bound … so this instrument's limit is phase-edge timing."
   - Paper abstract: "Timing movement did not at least double every detection floor (dominance branch B)." §6.4: "The registered statement that timing attribution dominates the detection floor … is not made; its opposite is not made either." §6.3: the clock-anchor timing bound "sets each of the four published floors … It is not the registered dominance statement".
   - The paper's definition is "how much timing uncertainty enlarges the detection floor". Its detection floor is "the largest difference the instrument produces when nothing differs". README says "smallest real difference the instrument can see".
   - A reader will infer dominance was shown. It was not.
   - Fix: say that the four published floors are set by the clock-anchor timing bound, and that the registered dominance statement (all twelve ratios at least 2) was not met (three of four shared-sign replays fall below 2). Align the detection-floor wording with the paper.

3. **MEDIUM, "about 45–49 ms in Block 5" (README, 59-pulse paragraph) is not in the paper.**
   - The paper's only ms figures are "b = 45.6 ms and s = 0.4 ms" (Appendix, line 2012) and "opening 40.0 ms, closing 30.0 ms … 54.531 ms" (line 2006), both labelled "Synthetic example". Per-session bounds are not printed. Table S5 gives the timing bounds in joules only (1.69, 2.31, 2.39 and 2.41 J).
   - Fig 2's "edge ±45 ms" is schematic and labelled as such, so it is acceptable, but it echoes the number.
   - The README says the paper "is the authority for every number here", which is false for this one.
   - Fix: source it to the Block 5 artifact or RESULTS.md and cite that, or drop the range. The paper states only that "59 commanded one-second matrix-multiplication pulses" are driven before and after each session, which is correct (§4.2, line 308).

4. **MEDIUM, BYTES "committed on 12 November 2026" (README) is not stated in the paper.**
   - Paper abstract: "the registration requires three straight lines fixed on three dense models to be committed before seven held-out models … are unblinded" (a requirement). §7.5 still has the placeholder `{{FILL: P1-BY-LINES | … the commitment date …}}`. Fact tag H02 reads "BYTES commitment is a requirement, not a completed step".
   - The only repo support I found is `docs/process_traces/2026-11-12-air-offline-handoff/bytes-commitment-draft.md`, which is a DRAFT order for the magistrate, with its time left as `<<HH:MM>>`. I did not verify that the commit was made.
   - "Seven held-out models remain sealed" is consistent with the paper (3 fit and 7 held-out: 4 dense and 3 MoE).
   - Fix: cite the commitment record (the `records/2026-11-bytes-stage1` receipt or RUN_STATE) next to the sentence, or phrase it as "committed per RUN_STATE item N". Do not claim the paper is the authority for it.

5. **LOW, derived ratios are not in the paper.**
   - "11–14 times their floors" (README: "detection floors"). Derived: decode 141.35/10.18 = 13.9 and 146.63/10.18 = 14.4; prefill 95.80/8.84 = 10.8 and 101.81/8.84 = 11.5. This is defensible, but it mixes near-end and point estimates, and the paper only says "the near end of the decision interval lies beyond the floor gate".
   - "94–96 %" derived from the intervals: the statistical part [146.44, 146.82] is 0.38 wide against a decision interval 10.56 wide (96.4 % timing). Prefill: 0.74 against 12.02 (93.9 %). The paper does not state a percentage.
   - Fix: add "(derived from Table 5)" to both.

6. **LOW, the README's "not news" sentence is not in the paper.** "the paper does not present it as news: the contrast is a known-direction test of the instrument." The paper only says "in the registered direction". Soften it to "registered direction", or drop "the paper does not present it as news".

7. **LOW, wall versus DC-input wording.** The tripwire motto "cannot edit the joules it drew from the wall" sits in a README whose Figure 1 says the wall AC is "not measured" (the meter is at the DC input). Fix: "from the charger" or "at the DC input".

8. **LOW, stale linked page and "no outcome has been opened" (README, tripwire section).**
   - The linked `docs/research/energy-tripwire.html` reports pilot results ("Held-out one-turn omissions … were detected in the pilots", "In pilots 4–9, 2 of 26 untampered sabotage-task runs crossed the threshold"). It also says "Block 5 outcomes remain sealed until their registered release", but Block 5 was released on 8 November.
   - README's "no outcome has been opened" is true of v4 but reads as if no tripwire data exists.
   - Fix: say "no v4 (registered) outcome has been opened; earlier pilots are reported on that page", and refresh the page's Block 5 line.

## Checked and OK, with the paper line

- **Four phase energies and intervals.** README table, Figure 5 and the abstract match: 51.21 [48.92, 53.49], 26.25 [23.32, 29.19], 198.36 [195.23, 201.49], 128.28 [125.19, 131.38].
- **Contrasts.** Table 5 gives decode +146.63 [141.35, 151.91] with floor gate 10.18, and prefill +101.81 [95.80, 107.82]. Rounded, these match the README and Figure 5 (floor aside, see 1).
- **"6 of 10 / 5 of 10 quads".** §6.1: "keeping 6 of 10 for decode and 5 of 10 for 2,048-token prefill". The README says only L2, "direction supported".
- **Block 6 sentence.** Abstract: "each of the three replication contrast sessions gave the primary session's outcome word and sign". "Nine further sessions" is also in the abstract.
- **L1/L2 and one session per model.** The abstract has "from one session per model … each an instrument result (L1) whose phase attribution was not checked by an independent instrument". Table 5 shows L2 on both contrasts.
- **Release timing.** Figure 5 says "released 8 Nov 2026" (§5.6: "released on 8 November 2026 at 11:17 PST").
- **Session shape (Figure 3).** §4.1 and §5.3 give an 18-run reference corpus, a start triplet, a midpoint reference and an end triplet. Figure 3 is labelled "SCHEMATIC, WIDTHS NOT TO SCALE". I found no support in the paper for the "Settle 60 s" figure; that is minor.
- **Figures 2 and 4** are headed "SCHEMATIC", and Figure 7 is headed "REGISTERED DESIGN VALUES". No schematic is presented as a measured result. Figure 4's arithmetic is right: the linear case estimates 10.0 J and the curved case 8.0 J.
- **Meter.** §3.2 has "50 times a second", "DC input", and "descriptive cross-check … Part 1, primary boundary … Part 2". This matches the README.
- **"36–39 %".** Not present in the README or the figures.
- **Tripwire.** Neither the README nor the lines figure claims any tripwire or v4 result. The README says "no outcome has been opened"; see 8.

## SVG safety

All 18 files parse with `xml.etree`. None contains a script, `foreignObject`, `iframe`, `image`, `use`, an `on*` handler, an external href, an `@import` or a `url()` other than local references. The only `data:` content is `font/woff2`. The `http://www.w3.org/2000/svg` namespace is the only URL-like string.

## Docs tests (run from the tests dir)

Baseline, the tail of the output:
```
.......................
Ran 23 tests in 0.209s
OK
```

Mutation probe: I appended "Agents deploy the site." to README.md, ran the same command, then restored the file from a copy.
```
First extra element 0:
('README', 'Agents deploy the site.')
- []
+ [('README', 'Agents deploy the site.')]
Ran 23 tests in 0.189s
FAILED (failures=3)
```
The probe fails as it should. After the restore, `git status --short` and `git diff --stat` were both empty, so the checkout is clean. I did not commit or push anything.

Other paths: figure builder build_readme_svgs.py (lead's scratch directory). Full SVG text dump: svgscan.txt (lead's scratch directory).

## Row 4: cold final pass (research lead)

# Gate row 4 (cold final pass), PR #784 at `a982d89c4` — ruling of Sat 14 Nov 2026, 11:47 PST

**Verdict: ADMIT WITH FIXES.** The numbers in the gross-energy table and the estimates match the paper. Three places say more than the paper permits (F1, F3, F7) and must change before merge. The rest are small wording corrections. With all fixes applied verbatim and the SVGs regenerated, it merges without coming back to me.

**Read.** `README.md`, `build_readme_svgs.py`, `paper1.md` (abstract, §1.2–1.4, §3.1–3.2, §4.2–4.8, §5.1–5.7, §6.2–6.5, §6.7–6.8, §7.1–7.2, §7.5, §8.1–8.2, §9, §11), the visible text of `energy-tripwire.html`, `docs/analysis/b5/RESULTS.md` and `RUN_STATE.md` on main, and RL-27, RL-52 and RL-147 in my log. Released results only; nothing sealed was opened. I wrote nothing.

README strings below are quoted as continuous text; some wrap across lines in the file.

## Blocking fixes

**F1. README lines 73–75: the L2 sentence and the "94–96 %" sentence.**
- The conclusion "so this instrument's limit is phase-edge timing" contradicts the paper. Dominance branch B was selected, and §11 says "we make no statement about which source limits these measurements".
- "94–96 %" is the share of D in the decision half-width, but D is not only timing: it includes the drift allowance. `RESULTS.md` line 112 puts the clock-anchor term at 81–83 % of D. The value is also the kind RL-52 item 5 dropped from the paper (unregistered, derived, no ledger row).
- "about 11–14 times" is likewise derived and ambiguous (`RESULTS.md` gives 13.9 and 10.9 for the interval's near end; the estimate over the floor gate gives 14.4 and 11.5).

Old:
> Both contrasts are **direction supported** at claim level L2, about 11–14 times their detection floors. About 94–96 % of each interval's width is the deterministic timing bound, not run-to-run scatter, so this instrument's limit is phase-edge timing.

New:
> Both contrasts are **direction supported** and reach claim level L2 under the registered gate: each estimate exceeds its floor gate (146.63 J against 10.18 J for decode, 101.81 J against 8.84 J for prefill). All four published detection floors are set by the clock-anchor timing bound, not by run-to-run repeatability. The registered test for the stronger statement, that timing attribution dominates the detection floor, was not met (three of the twelve dominance ratios are below 2), so the paper makes no statement about which source limits these measurements.

**F2. README lines 76–77: the replication sentence.** It is correct; add the registered gloss from §6.8.

Old:
> **The registered replication (Block 6, nine further sessions) gave the same outcome word and sign in each of its three contrast sessions.**

New:
> **The registered replication (Block 6, nine further sessions) gave the same outcome word and sign in each of its three contrast sessions.** "Replicated" is the registered word for that agreement; it is not a new test and carries no new interval.

**F3. Figure 5: floor and interval digits.**
- As a limit the prefill floor gate prints 8.84 (Tables 3 and 5 and the result sentence round floors up). 8.83 is Table 6's to-nearest form.
- The intervals [141.4, 151.9] and [95.8, 107.8] are narrower than the paper's [141.35, 151.91] and [95.80, 107.82]; the paper rounds interval ends outward. Print the paper's digits.
- The axis label should say "gross".

`build_readme_svgs.py`, then regenerate both themes:
- Lines 423–424, old: `"Figure 5: Block 5 contrasts drawn to scale. Decode +146.6 J [141.4, 151.9] against a floor " "of 10.18 J; prefill +101.8 J [95.8, 107.8] against a floor of 8.83 J; both direction supported"`
  new: `"Figure 5: Block 5 contrasts drawn to scale. Decode +146.63 J [141.35, 151.91] against a floor gate " "of 10.18 J; prefill +101.81 J [95.80, 107.82] against a floor gate of 8.84 J; both direction supported"`
- Line 439, old: `"extra energy per request, Qwen3-8B minus Qwen3-1.7B (processor rails)"`
  new: `"gross phase energy per request, Qwen3-8B minus Qwen3-1.7B (processor rails)"`
- Line 441, old: `10.18, 146.6, 141.4, 151.9,` → new: `10.18, 146.63, 141.35, 151.91,`
- Line 442, old: `8.83, 101.8, 95.8, 107.8,` → new: `8.84, 101.81, 95.80, 107.82,`
- Line 447, old: `f"floor {floor}"` → new: `f"floor gate {floor:.2f}"`
- Line 451, old: `f"+{est} [{lo}, {hi}]"` → new: `f"+{est:.2f} [{lo:.2f}, {hi:.2f}]"`

README line 70 alt, old:
> Figure 5: decode contrast +146.6 J [141.4, 151.9] against a floor of 10.18 J; prefill contrast +101.8 J [95.8, 107.8] against a floor of 8.83 J

New:
> Figure 5: decode contrast +146.63 J [141.35, 151.91] against a floor gate of 10.18 J; prefill contrast +101.81 J [95.80, 107.82] against a floor gate of 8.84 J

**F4. README line 84: the table qualifier.** The numbers and the L1 wording match Table 2 and the abstract. Add the registered "separate windows" disclosure, because two rows side by side invite a subtraction.

Old:
> One session per model, instrument results (L1); phase attribution was not checked by an independent instrument.

New:
> One session per model, instrument results (L1); phase attribution was not checked by an independent instrument. The two models were measured in separate sessions in a fixed order, so the rows are not differenced into a comparison; the contrasts above come from their own interleaved session.

**F5. README lines 23–24: two definitions stronger than §1.2 and §4.5–4.6.**

Old:
> a **detection floor** (the smallest real difference the instrument can see) and a **dominance ratio** (whether timing, rather than noise, sets that floor)

New:
> a **detection floor** (the largest difference the instrument produces when nothing differs, and so the smallest the registered analysis will call resolved in one session) and a **dominance ratio** (the factor by which timing uncertainty enlarges that floor)

**F6. README line 48: "(about 45–49 ms in Block 5)".** The paper does not print it (`P1-M-ACCEPT` is unfilled; the only 45.6 ms is a synthetic example), and I could not trace it to a released row in `RESULTS.md`. The README says the paper is the authority for every number.

Old: `sets the session's timing bound (about 45–49 ms in Block 5).` → New: `sets the session's timing bound.`

**F7. Figure 6 steps 3–5 (build script lines 463–465).**
- Step 3 says the analysis is pinned "before it sees the data". §5.5 says the opposite of what a reader would infer: analysis versions r1–r4 changed after collection, blind.
- Step 4 says "every registered quantity". §5.7 says core arithmetic, with seven disclosure families not recomputed.
- Step 5's "only match or field names, never values" is not in the paper.

Old 3: `("3", "Pin the analysis", "The analysis program is pinned to a tagged commit before it sees the data."),`
New 3: `("3", "Analyse blind", "The analysis runs end to end over the real archives in a blind dry run; only structure is exposed."),`

Old 4: `"A separately written program recomputes every registered quantity."`
New 4: `"A separately written program recomputes the core arithmetic from the raw power records."`

Old 5: `("5", "Blinded comparison", "A comparator reports only “match” or field names, never values."),`
New 5: `("5", "Compare under fixed bars", "The two computations are compared family by family, under tolerances fixed blind before release."),`

README line 91 alt, old: `collect blind, pin the analysis, recompute independently, blinded comparison, unseal` → new: `collect blind, analyse blind, recompute independently, compare under fixed bars, unseal`

**F8. README line 94: sealing sentence.** §5.5 is explicit that later changes "cannot be hidden by saying that the estimators were unchanged".

Old:
> The counting rules, exclusions, estimators and even the result sentences were sealed before the first session armed.

New:
> The counting rules, exclusions, estimators and the fixed outcome sentences were registered and sealed before the first session armed. Later errata, blind rulings and analysis-code changes are dated and disclosed in the paper (Section 5.5).

**F9. BYTES status, README lines 102–103.** The stage-1 commitment exists (RUN_STATE item 291b: commit `569591e53`, pushed 2026-11-12T20:00:59Z, "no held-out operation of any kind"), so the sentence may stand under RL-147 §4 item 4. Tighten "analysed" and carry the disclosed departure from §8.2 item 2.

Old:
> before any held-out model was analysed. The seven held-out models remain sealed.

New:
> before any held-out model's energy was unblinded. The seven held-out models remain sealed. One held-out model's timing had been read before the commitment; the paper discloses it.

Figure 7 is accepted as is: I recomputed three points from Table 7 and they match, and "registered design values" is right.

**F10. Research-lines card and its alt.** "Replicated" is a registered word for the two contrasts only. §6.8 reports that the 8B floors differed between blocks by 1.69–3.23 J.
- Build script line 236, old: `"Released · replicated"` → new: `"Released · contrasts replicated"`
- README line 10 alt, old: `phase energy (released and replicated)` → new: `phase energy (released; both contrasts replicated)`
- "Lines committed · held-out sealed" and "Registration · calibration": accepted.

**F11. Tripwire, README line 112.** No v4 outcome is implied by the section or the card; "no outcome has been opened" stands. One fix: the meter is at the DC input, and Figure 1 on the same page says the wall is not measured.

Old: `*An agent can edit its own logs. It cannot edit the joules it drew from the wall.*` → New: `*An agent can edit its own logs. It cannot edit the joules it drew.*`

**F12. "How the research is run", README lines 121–125.** "Every change" and "every unseal" are not in §8. §8.2 item 4 limits executing review to number-bearing code from 27 October, and §8.1 gives the researcher's role in other words.

Old:
> A headless **magistrate** on the measurement Mac does one step at a time and exits before any capture, because no AI process may run while power is measured.

New:
> A headless **magistrate** on the measurement Mac does one step at a time and exits before any capture: a live AI agent process on that machine is a registered hazard that refuses the arm.

Old:
> Every change gets an executing cold review that reruns the code, and independent re-implementations check the analyses. Ed keeps scope, authorship and every unseal.

New:
> Since 27 October 2026, code that can compute, select or exclude a published number is reviewed by two sessions from different model families that execute and mutate it, and separately written code recomputes the core arithmetic. Ed sets the research direction, the methodological requirements and the process policy, and is the escalation point for changes to what is measured or claimed.

**F13. "What this does not claim", README line 129.** Accepted, with one sentence added because the page now says "replicated".

Old:
> Nothing here is a statement about other prompts, models, machines or boundaries.

New:
> The replication is across sessions and days on the same machine, not across machines. Nothing here is a statement about other prompts, models, machines or boundaries.

## Small fixes (same commit)

- **Hero, build script line 219.** §3.1: 100 ms is the requested interval and records arrive more slowly. Old: `"Instrument: macOS powermetrics, 100 ms records"` → new: `"Instrument: macOS powermetrics, records requested every 100 ms"`
- **README line 63 alt.** Old: `Figure 4: linear drift cancels in the quad, curved drift leaves a 2 J error` → new: `Figure 4 (schematic): linear drift cancels in the quad, curved drift leaves a 2 J error in this example`

## Accepted without change

- Figures 2, 3 and 4 carry "schematic" in the plate, and none presents a synthetic value as a measurement.
- Figure 1 and the boundary sentence (line 31–32) match §3.1–3.2.
- The splitting paragraph, the quad paragraph, and "not news … known-direction test of the instrument" are within the paper.
- The gross-energy table values match Table 2 digit for digit.

## After applying

1. Regenerate all SVGs and look at Figure 5 and the first card: the longer labels may collide.
2. Grep the regenerated SVGs and README for `8.83`, `141.4`, `94–96`, `11–14`, `from the wall`, `every registered quantity`: expect none.

## Not in this PR

`docs/research/energy-tripwire.html` is not in the diff. It also says "from the wall" and its 7 November roadmap statuses are stale. It implies no v4 outcome and its pilot figures carry their caveats, so the link may stand; correct the page in a follow-up.
