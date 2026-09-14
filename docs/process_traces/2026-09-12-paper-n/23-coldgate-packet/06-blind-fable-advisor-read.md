# Blind advisor read — `docs/paper/draft-v2-skeleton.md` (first contact)

Read cold on 2026-09-12 from the `JouleWise-wt-paper-n-cold` checkout. Only the
draft itself was read; no figures were opened, no registry, no repository
context. Quotes are verbatim from the draft; section numbers are the draft's.

## 1. What I understood the paper to claim

Written after the abstract and Section 1 only:

1. The student measures the energy of a language-model request on a Mac using
   macOS `powermetrics`, which reports one average power per roughly 100-ms
   record, and wants to split that energy between the prompt-processing phase
   and the token-generation phase.
2. Because a record can straddle the boundary between the two phases, where the
   boundary is placed in time moves energy from one phase to the other while the
   request total stays fixed; repeating the request does not cure this.
3. To size the allowed boundary movement, the method fires GPU pulses with
   time-stamped start/stop commands, fits their edges in the power trace,
   and adds a bound on how well the trace can be placed on the wall clock; the
   result is a permitted timing domain over which phase-energy statistics are
   recomputed, and the paper asks whether that recomputation at least doubles
   the false-difference floor a comparison must clear.
4. The evidence is a re-analysis of one historical pulse capture (all 59 fitted
   onsets late, 49 of 59 offsets early) and a count of how many sampler records
   overlap short prompt-processing phases (37 of 50 fail a three-record minimum
   for the 1.5B model; all 50 pass for 7B).
5. Everything is one M3 Max, one sampler configuration; whether the pulse-derived
   allowance applies to inference is untested; no model-versus-model energy
   result is claimed.

After reading the whole main text and appendix: the understanding survived,
but three things changed in my reading.

- The sensitivity ratio (R, and the comparative R_cm) is never computed on any
  measured inference data. Section 3 specifies it and demonstrates it on
  synthetic inputs only. I had read the abstract as promising at least one
  measured sensitivity number; there is none. The paper's measured content is
  Figure 2 (pulse lags) and the record-support counts.
- The false-difference floor, the A/B/B/A design, the whole-window allowance,
  reference runs, and the three estimands are described at length in Sections
  1–3 but are never exercised. They belong to an unperformed campaign.
- A large share of Section 2 is about file fingerprints, refusal reason names
  and code identifiers rather than about measurement. The measurement protocol
  itself is in Appendix A.3, and it is good.

## 2. Top asks before I would let this go to a venue

Priority order. None asks for new data collection.

**Ask 1 — Say up front that no sensitivity ratio is computed on measured data.**
Section: title and abstract. Quote: "*JouleWise: Timing Sensitivity of
Phase-Energy Assignments on Apple Silicon*" and "*sensitivity calculations over
the registered timing domain*". Category: claim overreach. Why: the title and
abstract lead a reader to expect a measured timing-sensitivity result; the
only R and R_cm values in the paper come from a synthetic five-number example
and a two-block test fixture. The reader discovers this only at the end of
Section 3 ("*no new component floor is published here*"). What would satisfy me:
one sentence in the abstract and one in Section 1, in this shape: "This paper
specifies the sensitivity calculation and demonstrates it on synthetic inputs;
it reports no sensitivity ratio on measured inference data." Retitling to
"A method for ..." would also be honest.

**Ask 2 — Rewrite the abstract as an abstract.**
Section: Abstract. Quote: "*macOS powermetrics is the power sampler used here.
Each sampling record reports average power between recorded start and end
times. A record can span two phases ...*". Category: presentation. Why: the
abstract is a glossary. It defines the sampler, the record, both phases,
fitted onsets and offsets, and the held-average reconstruction before it says
what was done or found; the conclusion then repeats it nearly verbatim. What
would satisfy me: at most 200 words in the order problem, method, what was
measured, what was found (the two counts), what it does not show; all
definitions move to Section 1. Delete the duplicated paragraph from the
conclusion.

**Ask 3 — Take code identifiers, hash names and internal decision IDs out of the main text.**
Section 2 ("Bracketed pulse-train algorithm"), Section 4. Quotes:
"*`validation_manifest_sha256` ... `instrument_calibration_invalid` in
`joulewise/reduce.py` ... `PLAN_HASH_MISMATCH` in
`joulewise/calibration_ledger.py` ... `ISSUED_ACCEPTANCE_REGISTRY` ...
`GENESIS_FIXTURE_ACCEPTANCE_SHA256`*"; "*whose energy values the repository
decision D-078 voids for energy-claim use*"; "*registry DX-001 binds
`round7/excursion-decomposition.json`; DX-003 binds this SVG; DX-010/011 bind
the two medians*". Category: presentation. Why: a reader who is not inside the
project cannot use any of these, and "D-078" is meaningless to them; the first
paragraph of Section 2 is about 450 words in one block and most of it is
integrity bookkeeping, not the measurement. What would satisfy me: Section 2
describes the physical procedure in the numbered form Appendix A.3.2 already
uses (stamp, spawn, wait for rollover, quiet, warm-ups, 59 pulses with the
gap rule, quiet, stop), with one sentence saying every input is fingerprinted
and mismatches refuse the capture; D-078 becomes its reason in plain words
(an earlier clock-anchor defect); registry and code locators go to Section 7
or Appendix A.

**Ask 4 — Acknowledge that the noise scale hit its floor, and what that does to the accepted region.**
Section: Appendix A.3.5 and Table A3. Quote: "*the idle GPU channel reads
0.0 W throughout the baseline set, so b = 0.0 W, the MAD is 0, and the floor
engages: σ = 0.001 W*"; then Table A3 shows plateau records at 41.08 W against
a predicted 42.55 W with Huber loss 1975, and a quiet record at 0.041 W with
loss 54.7. Category: metrology. Why: the standardised residuals on the plateau
are about 1500σ. σ is not measuring the instrument's noise; it is a 1-mW
constant, and the accepted region (all edge pairs within 5% of the best loss)
is therefore a tolerance around a number with no statistical scale behind it.
That region's width is the calibration bound, so the headline 30-ms bound is
partly a product of two constants (1 mW and 5%). The paper does say the region
is "*not a confidence region*", but does not say that the noise scale was
degenerate on the capture used. What would satisfy me: two sentences in A.3.5,
and one in Section 5: on this capture σ was at its floor; the plateau scatter
is about ±1.5 W around the fitted amplitude, roughly 1500 times σ; the accepted
region is a tolerance set whose width depends on the 5% and 1-mW constants, and
those constants have not been varied.

**Ask 5 — Interpret the systematic lag, and say why it is bounded rather than corrected.**
Section 4 ("Historical current-method edge result") and Figure 2. Quote: "*The
59 onset lags are all positive; 49 of 59 offset lags are negative ... Their
medians ... are +13.0 ms and −5.5 ms.*" Category: metrology. Why: 59 of 59 in
one direction is a bias, not scatter. The method then folds the largest
excursion into a symmetric ±b domain. A metrologist reads this and asks:
is this the GPU taking ~13 ms to start after the command (a command-path
latency that inference would also have), or the sampler stamping its windows
late (an instrument offset)? Either way, a known bias is normally subtracted
and the residual bounded; bounding the bias symmetrically is conservative on
one side and may be non-covering on the other. What would satisfy me: a short
paragraph in Section 5 stating the physical interpretation the student
favours, stating that no correction is applied and why, and stating the
consequence: the ±b domain includes the bias, so the timing envelope is wider
in the direction the bias does not go.

**Ask 6 — Put the record-support result next to the timing bound, in joules or as a fraction.**
Section 4 ("Record support in two historical model stacks"). Quote: "*Median
prefill duration was 0.2815 s for 7B versus 0.1365 s for 1.5B*"; "*Record
support is a count; three is a chosen cutoff, not proof of adequate
phase-energy precision.*" Category: missing. Why: the two results of the paper
are never connected. With a window bound of about 39 ms (the Section 2 worked
example, b = 38.724 ms), each edge of a 136-ms phase may move by up to 39 ms,
so up to 57% of the phase's duration is reassignable under the paper's own
domain; for the 281-ms 7B phase it is about 28%. That is the sentence a reader
needs to judge what "passed the three-record minimum" is worth, and the paper's
own r08 example (a passing case whose three overlaps are 14 ms, 115 ms and
7.6 ms) shows that passing can still mean one record carries almost all the
energy. What would satisfy me: one sentence after the medians giving those
fractions (arithmetic from numbers already in the paper), and one sentence
stating that the three-record minimum guards only against a split supported by
two straddling averages, not against a timing envelope comparable to the phase
energy.

**Ask 7 — Print timing numbers at instrument precision in the main text.**
Sections 2, 4, 5. Quotes: "*t_{0.995,16}=2.92078162242509999197*";
"*10.164834757777545 ms*"; "*The retained diagnostic capture's pulse-derived
limit was 0.030067931757111657 s*"; "*0.0000010000000000000002*". Category:
presentation / metrology. Why: seventeen significant figures on a bound from a
100-ms sampler tells a reader the author does not distinguish stored digits
from measured precision, and it makes the text hard to read. The appendix can
keep full binary64 strings for replay. What would satisfy me: main text to
0.1 ms (30.1 ms, 10.2 ms, 1.1 ms), a footnote or appendix sentence saying full
digits are retained for byte-exact replay, and the 1-µs resolution written as
1 µs.

**Ask 8 — Either explain what R_cm answers that R does not, or move it to the appendix.**
Section 3 ("Combining shared movements and local widths"). Quote: "*Retaining
the same sign for the scalar q_j allowances does not preserve or replay one
physical time shift; their extrema can arise at different timing coordinates*"
and, in Section 5, "*a sensitivity calculation with no proof that its limit
covers the effect of the same timing shift in every block*". Category: unclear
/ redundant. Why: about two pages of the main text (the q_j and ℓ_j
construction, the outward-rounding paragraph with p = 64·ulp·M, Table 4, and
Figure A4) build a quantity the paper itself says does not mean the thing it
looks like it means. I could not state in one sentence what physical question
R_cm answers. What would satisfy me: one plain sentence at the top of the
subsection of the form "R asks how much the bound grows when every run's
edges move independently; R_cm asks how much it grows when ... ", and the
floating-point padding paragraph and Table 4 moved to the appendix. If that
sentence cannot be written, drop R_cm from the main text.

**Ask 9 — Delete or demote the machinery that is defined but never used.**
Sections 1–2. Quotes: the three-estimand table ("*Same-model repeats | Absolute
floor*" ...), "*The cell's resolution bound—the detection floor in the
advisor's terminology—is a registered operational resolution guard ... the
artifacts call the final gate value after those safeguards the cell floor*",
"*whole-window allowance*", "*reference-trajectory excursion*", "*issued
repeatability bound*", "*energy family*", "*stage*", "*admitted*", "*entry
check*". Category: redundant. Why: none of these produces a number in this
paper, and three names (resolution bound, detection floor, cell floor) are
given for one idea. Every defined-but-unused term costs the reader and makes
the paper look like it reports a campaign it did not run. What would satisfy
me: one paragraph in Section 5 (Future work) naming the planned comparison and
pointing to the protocol document; the terms above deleted from Sections 1–3,
and a single name kept for the floor.

**Ask 10 — State in Section 1 that the measured results cannot be re-derived from the released materials.**
Section 7 and A.1. Quote: "*an outside reader cannot presently repeat the
complete historical raw-byte analysis from the repository alone*"; "*Complete
historical replay is not presently open to independent re-reduction from Git
alone.*" Category: missing (in the right place). Why: for a methods paper
whose only measured numbers come from unreleased bytes, this is a first-page
limitation, not a Section 7 note; a reviewer who finds it on page 20 will
feel misled. What would satisfy me: one sentence in Section 1's "deliberately
narrow" paragraph and one in the limitations, saying plainly that the raw
captures are retained but not released, and that the synthetic examples are
the only fully reproducible part.

**Ask 11 — Move the synthetic enclosure example out of the introduction.**
Section 1. Quote: "*In a synthetic enclosure diagnostic, a 0.9-s window
crossing ten 100-ms records that each report 10 W is assigned 9 J. Its ±10-ms
two-edge timing envelope is [8.8, 9.2] J, while ... the nonnegative
partial-record enclosure [8, 10] J ... it is reported, never composed into any
bound.*" Category: unclear. Why: the numbers arrive before the reader has been
shown what clipping a record is (Section 3 does that well with the 30-W
example), and "composed into any bound" refers to a construction that has not
been introduced. What would satisfy me: move this paragraph to the start of
Section 3 directly after the 1.20 J / 1.80 J example, and replace "never
composed into any bound" with "it is shown for contrast and is not added to
any result in this paper".

**Ask 12 — Justify the 17-capture spread rule as an instrument statement, not a t-table exercise.**
Section 2. Quote: "*Student-t is a small-sample bell curve whose 99% quantile
... sets the maximum permitted pre/post difference ... the two-draw rule ...
gives 10.164835 ms*" and "*The minimum prevents two numerically matching
captures from erasing the finite change allowance*". Category: metrology.
Why: the 17 captures are from one machine over four days; the rule treats them
as 17 independent draws of the capture bound and then uses their spread as a
drift-detection threshold. The reader is told the arithmetic in full but not
what physical change the rule is meant to catch or why 17 captures over four
days characterise it. What would satisfy me: two sentences: what a pre/post
difference above 10 ms would physically indicate (a change in the sampler's
edge response across the window), and that the threshold is conditional on
the retained corpus being representative, which has not been tested.

## 3. Three things that are strong and must not be lost

1. The forcing problem is stated with numbers, in one breath. Section 2:
   "*Moving a boundary 0.010 s inside a 30-W record transfers 0.30 J between
   assigned phases under the held-average reconstruction. The request total
   does not change: energy removed from one phase is added to the other.
   Repetition can reduce random scatter, but it cannot remove this systematic
   reassignment.*" That is the whole paper in three sentences, and it is the
   right observation: a software counter's timing, not its gain, is what
   limits a phase split. The related-work framing ("*opens the complementary
   time axis*") is the correct positioning against RAPL-in-Action and Jay et
   al., and the Hähnel et al. lineage is exactly the right ancestor.

2. Appendix A.3.2–A.3.3 is replicable and honest about its own bound. The
   capture procedure is a numbered protocol with the gap rule fully specified
   ("*gap(k) = 1.5 + vdC₂(k)*" with the first five values printed), and the
   clock anchor is built as set membership with all constraints written down,
   refused rather than clipped ("*The rate is refused, never clipped*"), and
   the bound decomposed into four named terms with a worked capture: "*H
   prices where record 0's end sits ... span prices within-capture
   wall-versus-elapsed drift ... r_max ... 10⁻⁶ s prices binary64
   representation error*". The paragraph explaining why the printed endpoints
   do not close to the printed H is the kind of thing that builds a reader's
   trust.

3. The refusals, and the repeated refusal to over-claim. "*A matching refusal
   is a reproduced result, not a failed replication*" (A.5); "*this value is an
   observed sample maximum, not a bound covering 95% of future edge errors with
   95% confidence*" (A.3.6); "*Alignment, not width alone, therefore denies the
   third overlap*" with the r03/r08 record table showing exactly why a 121-ms
   phase can fail against 121-ms records (Section 4). Keep every one of these.
   The r03/r08 table in particular is the best piece of evidence-writing in the
   draft: a reader can check every number against the sentence above it.

## 4. Could I replicate the method from the text?

**Section 2, calibration.** From Section 2 alone: no. The first point I would
have to guess is the scoring rule: "*scores the difference between predicted
and observed power with a rule that limits the influence of one large
discrepancy*" does not name or define the loss, and "*encloses every pair
close enough to that fit*" does not say how close. From Section 2 plus
Appendix A.3: yes, to the level of rebuilding the anchor estimator, the pulse
fit, the accepted-region search and the bound composition. The first genuine
guess in the appendix is A.3.2 step 7: how the 1-s pulse is driven and
terminated (a loop of 4096×4096 matmuls with a fence "*repeated*" until what
condition, and whether the off-stamp is taken after the last fence returns or
after a monotonic deadline). The second is the median convention for an even
number of baseline intervals in A.3.5 (A.3.6 states it for the 118 excursions;
A.3.5 does not).

**Section 3, sensitivity calculation.** The point-only bounds U_abs,point and
U_cmp,point: yes; the formulas and the 8–12 J worked example are enough. The
corner enumeration and R: yes, with one guess: the "*permitted timing domain*"
through which each edge moves is never written as an interval in Section 3; I
assumed each phase start and end may move independently anywhere in [−b, +b]
with b the operative timing bound of Section 2. If that is wrong, R changes.
R_cm: no. The first point where I must guess is ℓ_j: "*moving only that
member's remaining local clock and edge uncertainty*" — the paper never says
what that quantity is, what domain it ranges over, or how it differs from b.
The second is why the admitted difference δ_j and the zero-shift recomputation
z_j can differ at all (in the fixture they are equal), which is needed to
reproduce q_j in general.

## 5. One paragraph I would write for the student

You have found a real problem and stated it better than most published work
does: with a software counter that averages over 100 ms, where you draw the
line between prefill and decode moves tenths of a joule around, and no amount
of repetition fixes that. The pulse calibration and the clock anchor in the
appendix are careful, replicable work, and your habit of saying exactly what a
number does not show is the right instinct — keep it. The draft's problem is
that it reads as though you are afraid of it. The abstract is a glossary, the
second section is half integrity bookkeeping, and about a third of the main
text defines a comparison campaign the paper does not run. Your two measured
results — the instrument reports GPU work starting about 13 ms late and ending
about 5 ms early, and short prefill phases on the 1.5B model mostly fail to
touch three records — deserve to be stated plainly on the first page,
connected to each other (a 39-ms timing allowance is more than half of a
136-ms phase), and then defended. Cut what is not exercised, print timing
numbers at the precision the instrument has, say on page one that no
sensitivity ratio is computed on measured data and that the raw captures are
not yet released, and explain the one metrological soft spot honestly: the
noise scale in your pulse fit sat at its 1-mW floor, so the accepted region is
a tolerance set built from two constants, not from measured noise. Do those
things and this is a solid methods paper that a metrologist will respect,
because it will be saying only what it can show.
