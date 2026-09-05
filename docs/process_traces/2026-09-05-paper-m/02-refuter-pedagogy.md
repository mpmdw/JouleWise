```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"NOT LANDABLE: incomplete numerical pedagogy, a wrong mechanism figure and orphaned campaign methods.","workspace":{"base_requested":"6145e832","base_mode":"exact","head_start":"6145e832b4291a07d72a4451dad9c2460f421939","head_end":"6145e832b4291a07d72a4451dad9c2460f421939","upstream_end":null,"branch":null},"pathspec":["docs/process_traces/2026-09-05-paper-m/02-refuter-pedagogy.md"],"unowned_dirty":[],"verdict":{"landability":"NOT LANDABLE","findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"blocker"},{"id":"F3","severity":"blocker"},{"id":"F4","severity":"blocker"},{"id":"F5","severity":"blocker"},{"id":"F6","severity":"blocker"},{"id":"F7","severity":"should_fix"},{"id":"F8","severity":"should_fix"},{"id":"F9","severity":"should_fix"},{"id":"F10","severity":"should_fix"},{"id":"F11","severity":"should_fix"},{"id":"F12","severity":"should_fix"},{"id":"F13","severity":"should_fix"},{"id":"F14","severity":"should_fix"},{"id":"F15","severity":"should_fix"},{"id":"F16","severity":"should_fix"},{"id":"F17","severity":"should_fix"},{"id":"F18","severity":"should_fix"},{"id":"F19","severity":"should_fix"},{"id":"F20","severity":"should_fix"},{"id":"F21","severity":"should_fix"},{"id":"F22","severity":"should_fix"},{"id":"F23","severity":"should_fix"},{"id":"F24","severity":"should_fix"},{"id":"F25","severity":"should_fix"},{"id":"F26","severity":"nit"}]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}}],"flags":[]}
```

## Findings

**NOT LANDABLE.** Draft lines at 6145e832 unless SVG named. Blind review. F1–F6: blocker; F7–F25: should_fix; F26: nit. The middle presumes an unperformed campaign. P1, n17 and the two-block quotient reproduce; fit/classification inputs are incomplete.

**F1; L203 / Figure 1 SVG L79.** Old artwork: “shift × power step ≈ 0.030 s × 33 W ≈ 1 J”. This uses the wrong power. Proposed: “Moving the boundary 0.010 s inside a 30-W record transfers 0.30 J between assigned phases.” Redraw the area; delete physical “wrong phase” claims. SVG L122–123: replace universal phase-power assertions with “Power levels are illustrative.”

**F2; L1378, L1519–1527, L1561–1613.** Old: “Everything below is stated as the code executes it.” Missing inputs: local records, command stamps and native clock labels; pulse 0 uses an earlier anchor. Proposed: “Table A3 supplies the current-anchor example's clock constraints, command stamps, local GPU records, predicted averages and losses.” Supply the table; printed fit outputs are insufficient.

**F3; L1011.** Old: “Two is less than the required three, so the phase was not resolvable.” Proposed: “Relative to epoch 1784978933 s, the phase [0.267684,0.3887181] overlaps records [0.1945653,0.3210495] and [0.3210495,0.434475] for 0.0533655 and 0.0676686 s: two records fail three.” Verified against retained r03 bytes. Add zero-overlap neighbors and a numeric three-overlap case; medians cannot recover geometry.

**F4; L348.** Old: “No such report is supplied in this submission.” Proposed: “The evidence tests clock placement and record support; the unperformed comparison protocol is documented separately.” **Cuts:** move §3 (326–498), campaign identities/census (150–190), claim machinery (803–907), operational fields (917–938), campaign dependence/custody extensions (1099–1187), and supply-chain rules (1288–1299) to that protocol. Keep §4 sensitivity arithmetic. Condense 1193–1236 and 1034–1041; exclude the editorial ledger (1731 onward).

**F5; L600–601.** Old: “Exact enumeration refuses above 16 independent units; it never substitutes an approximation.” Run-energy choices imply 2^(4n); block endpoints imply 2^n. Proposed: “First form each block's difference interval; enumerate its lower/upper endpoints across n blocks and maximize the comparative formula, which is convex in those differences.” Explain convexity; add a numeric example and diagram naming inputs, corners, statistics, maximum and refusal.

**F6; L1439.** Old: “A wall-clock excursion of less than 250 µs occurring between stamps is invisible to the arithmetic; it is excluded by the requirement that any capture whose numbers support a published claim runs with network time synchronisation off, which is a recorded admission condition, not something the estimator can verify.” Proposed: “Disabling network-time correction removes one adjustment source; constant clock rate between stamps remains an unverified assumption.”

**F7; L11–12.** Old: “Software can report one average power value over a span crossing the change from reading input to generating output tokens.” Proposed: “The sampler averages power while input reading changes to emitting tokens, pieces of generated text.”

**F8; L51–52.** Old: “It bounds neither physical phase energy under arbitrary within-record allocations nor inference transfer nor future-error coverage.” Proposed: “This range does not locate actual energy within records, establish pulse-to-model timing agreement, or guarantee how often future errors stay inside.”

**F9; L109–121.** Old table entries: “Absolute floor”; “Comparative floor”; “Science contrast”. Proposed introduction: “Repeat the same model to measure false differences; enlarge their spread into a threshold a model comparison must exceed.” Define these before the table.

**F10; L213.** Old: “No uncommanded plateau may appear.” Proposed: “With 0-W idle power and σ=0.001 W, consecutive quiet 6-W and 7-W records fail the 5-W check.” Build max(5 W,5σ) and σ first; likewise give numeric predicates for “far enough,” “better,” and “accepted” before use.

**F11; L221–225.** Old: “A stage that passes is **admitted**, meaning allowed to begin its measured runs.” Proposed: “A stage is consecutive runs admitted when machine-state checks pass.” Move this before L221; gloss CPU/general-purpose processor and neural engine/specialized neural-network processor at L201.

**F12; L234–242 / Figure A2 SVG L157–158.** Old artwork: “It is bounded by the whole-window drift allowance, tracked by the reference runs above.” Proposed: “References measure change at selected times; their allowance cannot bound an arbitrary rise and fall between them.” Also repair “remains covered” at L234.

**F13; L350.** Old: “For workload response, an independent unit is one separately admitted bundle, not one sampler record within it.” Proposed: “Runs are the observations; admission does not establish the independence the statistical model assumes.” Also L543.

**F14; L458–459.** Old: “With fixed output levels, its slope is a fixed weighted sum, \(\hat\beta=\sum_i w_iE_i\), of the forty energies.” Proposed: “For output count x_i, w_i=(x_i−mean(x))/sum_k(x_k−mean(x))²; counts 1,2,3 give weights −0.5,0,+0.5 per token.” The printed intervals then yield 7–12 J/token.

**F15; L714.** Old: “A retained two-block fixture makes the replay checkable.” Block 2 allowances and scale M are supplied answers. Proposed: “The largest of eight cases uses (s,e1,e2)=(+1,−1,+1), giving differences 0.4278157324 and 1.1582423076 J and bound 8.8304376433 J.” Add eight rows, block 2 extrema/residuals, and a figure naming shifts, q, local widths, signs and maximum.

**F16; L871–872, L907.** Old: “Both intervals remain positive and the adjusted test passes, so the example supports the positive direction.” Test inputs are absent; Figure 3 omits Holm. Proposed: “Positive endpoints pass the sign check; Holm must pass separately.” Supply h=t×SE and test data; add Holm to Gate 2.

**F17; L932.** Old: “The refusal log is part of the result.” The list conflates invalid and below-floor evidence. Proposed: “Invalid evidence is refused; usable evidence below the floor receives a different outcome.” Figure 3: replace “no result of any kind” with “no authorized comparison result.”

**F18; L957–959.** Old: “The overlap count, record support, and the three-record minimum are the same test: count the sampling records with positive overlap, and calculate phase energy only when the count reaches the minimum.” Proposed: “Record support is a count; three is a chosen cutoff, not proof of adequate phase-energy precision.” Justify three.

**F19; L988–989.** Old: “An interquartile range (IQR) is the upper edge minus the lower edge of the middle half of sorted values; the width IQR was 5.9508 ms.” Proposed: “Using exact decimal timestamps, interpolate quartiles at (n−1)p, subtract, then round milliseconds to four decimals, ties to even.” Digits describe stored values, not physical resolution.

**F20; L1244.** Old: “JouleWise's distinct contribution is to calibrate runtime phase boundaries in the same measurement window, propagate their permitted positions through the energy integral, and make the resulting cell-specific resolution bound a claim gate (Sections 2, 3, and 5).” Proposed: “JouleWise fits GPU pulse edges and calculates phase-allocation sensitivity; transfer to inference is untested (Sections 2 and 4).”

**F21; L1360.** Old: “Re-derivation requires a full-history checkout at the released revision, Python 3.11 or later, and a copy of the evidence archive.” Proposed: “Historical replay needs unreleased raw data; synthetic replay uses pinned code.” Add the locator/revision; consolidate release-status repetitions.

**F22; L1437.** Old: “The third unknown, *A*, is expressed through this relation as described under "causal constraints."” Proposed: “Search for anchor A, offset α and rate β; eliminate α, then solve for A and β.” A is bounded, not uniquely expressed. Add numeric constraints and a polygon naming axes, lines, intersection, projections and empty-set refusal.

**F23; L1573.** Old: “Huber's loss is quadratic for small residuals and linear for large ones, so a single wild sample cannot dominate.” Linear growth remains unbounded. Proposed: “Linear growth reduces a large discrepancy's influence relative to squared error.” Add numeric prediction/loss examples and a figure naming commands, records, candidate edges, best pair, rectangles and projections.

**F24; L1597.** Old: “The algorithm computes a guaranteed *enclosure* of that region, not a sample of it, by interval branch-and-bound:” “Data cannot distinguish” overinterprets the tolerance. Proposed: “Split rectangles; reject those whose minimum score exceeds the cutoff: the surviving model-defined set is not a confidence region or physical-edge guarantee.”

**F25; L1623.** Old: “The anchor term is added because the whole trace was placed on the wall clock from a single point whose error is independent of, and additive to, the per-edge fit error.” Proposed: “Adding allowance magnitudes bounds their combined displacement without assuming independence.”

**F26; L970, L1727.** Old captions: “Figure 4. Phase–record overlap diagram.” / “Figure A2. One measurement window and the time-balanced A/B/B/A order.” Proposed: change embedded SVG titles from 5/2 to 4/A2.

## Residual risk

Tests: 11 and 10 passed sequentially. No discovery, hardware, agent launch, detector rerun or bibliography audit. SVG-source QA only. Next: lead adjudication, repairs, fresh review.
