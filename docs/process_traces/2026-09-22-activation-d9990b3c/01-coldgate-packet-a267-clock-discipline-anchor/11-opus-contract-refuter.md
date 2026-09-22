# Opus contract-lens refuter — A267 cold-gate packet (sealed, independent of the Fable ruling)

Claude Opus 5 (1M), read-only, 2026-09-22. I did not read or look for
`10-coldgate-fable-ruling.md`.

## 1. Auto-loaded files (disclosure)

My harness auto-loaded, before I saw the charge: `~/.claude/CLAUDE.md`,
`JouleWise/CLAUDE.md`, `JouleWise/CLAUDE.local.md`, and a memory index. Charter §4
forbids these to a cold judge; I am the refuter, so my requirement is model-family
diversity, not context-coldness — but the contamination is real. I opened no
memory-file body, no RUN_STATE, TASK_QUEUE, council log or run report, and took no
authority, severity or disposition from that text.

## 2. Digest verification

Method `shasum -a 256`, against the convening prompt (charter `099de884…c95d81`,
packet `0e3dfe79…7e6162`) and the packet's own manifest. Observed identical in every
case: charter and packet MATCH, exhibits A/B/B8/C/C-generator/D 6/6 MATCH,
`envelope-{02,07,08,11}/session.json` 4/4 MATCH against C1's list.

## 3. My independent answers (written before refuting the lead's)

- **Q1 — (c).** (a)'s toggle is necessary and D-127-chartered but yields an
  *asserted*, not *authenticated*, admission. My rule: (a) plus a post-window
  attestation from `timed`'s log refusing any envelope containing a
  `cmd,apply,src,adjtime` line; provenance records both.
- **Q2 — (c) as amended**, else (d). Parameterised caps with a v3.1 evidence
  identity is the right containment and the only option preserving review
  condition 5's negative control — but it needs an absolute drift backstop and a
  frozen identity→caps table emitted in the record.
- **Q3 — (a) as corrected** (three corrections below).
- **Q4 — correction right, enumeration incomplete** by consult R2 and R3.

## 4. Refutation results

### Q1 — environment control

**CONFIRMED: no network-time step in the evidence-night path.**
`git grep -l setusingnetworktime 9b6b3f0e` returns exactly six files: the four
T-0/arm-readiness modules, the sudoers file and the operator tool. Greps over
`quiet_predicate_campaign.py`, the chain zsh and `sample_quiet_predicate_evidence.py`
yield only the hard-coded `"network_time_provenance": None` at
`sample_quiet_predicate_evidence.py:750` and its reason at `:752`. The pilot's
`DIAGNOSTIC_NO_PACK` receipt class (A23) structurally excludes the T-0 pack path.
A9–A12/A24/A26 as described; A5, A6, A20, A21, A25 diff byte-identical against
`git show`. D-127 authority holds (B7 §1 verbatim; C2 shows the slice installed
`NOPASSWD`/`!requiretty`).

**MATERIAL — the option set omits the only available authentication.** C2 proves
the *read* form `-getusingnetworktime` is **not** in the slice and demands a
password, so the chain can never observe network-time state — only trust one set
command's stdout at t≈0. Consult I4 (B3) requires an "**authenticated**
network-time-OFF admission"; a t=0 receipt does not establish state across a 2.5 h
window (nothing would detect `timed` restarting or a profile re-enabling sync). The
packet itself ran the free, unprivileged check that closes this — exhibit D is
`log show --predicate 'process == "timed"'` — yet no option offers it. *Effect:* (a)
can be affirmed while I4 remains unsatisfied.

### Q2 — the two 5 ms caps

**CONFIRMED: both caps are absolute and duration-independent.**
`uncertainty_evidence.py:35`/`:41` are bare constants; the only comparisons are
`:407` (v2), `:1000` (v3 pre-fit), `:1225` (v3 post-fit) — scalar `>` with no
baseline term. `MIN_RATE_FIT_BASELINE_S` is a floor, not a scale.

**CONFIRMED: C1's arithmetic and the timed-log correlation.** Re-derived 02/07/08/11
from the verified records: offset changes −0.406 / −22.322 / −4.503 / −1.507 ms;
baselines 592.1 / 590.6 / 592.4 / 592.3 s; rates −0.69 / −37.79 / −7.60 / −2.54 ppm
— all reproduce C1, and `H + span + stamp_resolution + padding` recomposes to the
recorded `effective_clock_anchor_bound_s` to all digits (08: 5.0768 ms). Envelope
07's wall window is 03:27:10–03:37:00, containing the 03:34:21 −20.278 ms slew; 08
runs 03:37:08–03:47:00 under `freq_scaled −498151/65536 = −7.601 ppm` and measures
−7.60 ppm; 11 (04:07–04:17) under −2.530 ppm measures −2.54 ppm.

**(iv) CONFIRMED that a step still refuses — for a reason the packet misses, and its
stated premise is FALSIFIED.** The five host stamps are not spread across the
capture: envelope 10's sit at t = 0.000, 0.810, 0.810, 590.914, 595.810 s — two
clusters. The stamp rows therefore carry *zero* information about *where* an
excursion occurred and cannot distinguish a step from a uniform rate.
Discrimination rests entirely on the native rows, which do carry the wall excursion
(`native_timestamp_ns` from the plist wall `timestamp`, A25). Envelope 02 shows how
tight that is: `rate_lower` 0.9999993074697832, `rate_upper` 0.9999993231523191 — a
0.0157 ppm window, i.e. ±9 µs of admissible drift over 590 s against a 250 µs
per-row allowance. A 16.6 ms kink cannot survive it, and envelopes 03 (−4.44 ms) and
04 (−1.33 ms) already refuse `affine_clock_fit_empty` — an empirical floor. **But
"~2000 native rows" is wrong:** `records_checked = 2535`,
`native_rollover_count = 591`; C1's 2038–2070 are *interior* counts.

**BLOCKER — no option carries an absolute backstop.** A sustained-rate limit is
unbounded in absolute drift: 25 ppm × 600 s = 15 ms, and under (b) the drift term
"passes into the bound uncapped". Materiality is computed at idle (0.3227 W →
7.2 mJ); the one loaded figure (22 ms at 40 W ≈ 0.9 J) never enters the option
evaluation. At 40 W a 15 ms admitted drift is ≈0.6 J — the *same order* as the
ratified ~1 J limit (B5), not two orders below — and this pilot precedes an
idle-load-idle bracket (A20 `block_two`).

**(v) "Q2(c) satisfies condition 7" — PARTLY FALSIFIED, in both directions.**
(1) The paraphrase is wrong *against the lead's own interest*: B1 condition 7 reads
"the **250 µs / ±50 ppm** constants stay frozen and may not widen after observed
failures without a new method identity" — two constants, neither a 5 ms cap. The
packet renders this "the frozen constants". Consult I3 (line 89, **omitted from
exhibit B**) agrees: "Recalibration of **50 ppm or 250 us** requires a new ruled
method identity." (2) (c) is nonetheless an evasion vector on a ground the packet
does not raise: the caps become a *caller* argument, and the bounded record — all 25
keys of the live envelope-02 record enumerated — emits `model_departure_allowance_s`
and `rate_limit_ppm` but **no span cap and no effective-bound cap**. Two records
under one "v3.1" identity could have been judged under different constants. (c)
satisfies condition 7 only if the identity→caps map is frozen *and* both caps are
emitted in the record.

**MATERIAL — two omitted authorities.** Pro-lead: consult FLAG1 (lines 203-204, and
line 31) frames the alternative as "…or **explicitly overturn the 5 ms rule**", so
the consult expressly contemplated overturning the span rule as a legitimate
explicit path. Anti-(b): review condition 5 preserves negative control b10cb348
(span 6.40 ms) **permanently**; whether it still refuses under a 25 ppm rate rule
depends on its stamp baseline, which the packet does not supply (NOT EXECUTED;
corpus outside my read set). (c) is safe here — an argument for (c) over (b) the
packet never makes.

### Q3 — the 1 µs span-mismatch tolerance

**(vi) CONFIRMED to the ulp.** Every observed mismatch is an *exact integer
multiple* of `ulp(epoch) = 2.384185791015625e-07 s`: envelope 02 = +4 ulp, 05 = −5,
06 = +11, 11 = −17, 12 = 0 — necessarily representation error in the epoch-scale
supports built by `align_frames` (`start_s = end - elapsed_s`, A25);
`ulp(480.0) = 5.68e-14` rules out the interior scale.

**FALSIFIED: "the anchor's integer bound".** No integer-nanosecond field exists. The
record's endpoint is `first_sample_end_point_epoch_s = 1790069829.8024597` — a
float64 of ulp 238 ns, produced at A5 by `float((anchor_lower_ns + anchor_upper_ns)
/ (2 * ns_per_second))`, a Fraction midpoint that need not even be an integer ns.
(a)'s *mechanism* still works (round the emitted endpoint once to integer ns, then
accumulate `elapsed_ns` as ints) and stays inside
`align_frames`/`overlap`/`integrate` — but the provenance must be re-drafted or a
seat will hunt a field that does not exist.

**MATERIAL — there are TWO 1 µs gates; the options address one.** `integrate` sets
`span_mismatch` on `> 1e-6` (A6), and `reduce_interior` *independently* requires
`abs(rail_coverage_s[rail] - duration) <= 1e-6` for both `rail_sum_w` and
`combined_w` (A6). I verified both fire on the same envelopes: 05 (−5 ulp), 06
(+11), 11 (−17) fail the rail check too. Q3(b) ("set **the** tolerance") and Q3(c)
(1 ms absolute), as drafted, move only `span_mismatch` and would leave 05/06/11
`partial` — the options would not achieve their stated purpose. Only (a) fixes both.

**MATERIAL — "vacuous" is wrong.** Under integer arithmetic the comparison becomes
an exact *gap* detector: a genuinely missing frame still mismatches. Calling it
vacuous invites deleting a live fail-closed gate.

### Q4 — regression specification

**CONFIRMED: B8's acceptance sentence is wrong.** Envelope 07's 22.36 ms excursion
contains the logged −20.278 ms `adjtime` and is non-affine; it refuses under every
option offered. Envelope 08 (`effective_clock_anchor_bound_exceeded`, H 0.532 ms,
span 4.542 ms, −7.60 ppm) is the correct bounded-with-drift-priced replay, and its
reaching the *post*-fit gate proves its fit succeeded.

**BLOCKER — two ratified bars missing.** Consult **R3** (line 111) requires kill
tests that "independently exercise **>5 ms offset span** … and **effective bound
>5 ms**"; **R2** (line 107) requires, on any deriver change, "zero new refusals"
across all 34 resolvable corpus members, point shift ≤1 ms, bound delta within
±0.25 ms. Neither is in exhibit B or Q4's list of six. Under Q2(c) the default path
is meant to be untouched — R2 is the executable proof of exactly that, and R3 proves
the v3 kill tests (A16, A17) still bind after parameterisation.

## 5. Findings, tiered

**BLOCKER 1 (Q2)** no absolute drift backstop in any option — §4.Q2.
**BLOCKER 2 (Q4)** consult R2 and R3 omitted from exhibit and enumeration.
**BLOCKER 3 (Q2/Q3)** the ruled options cannot restore this night, and the packet
does not say so: Q2(c)+Q3(a) recovers {02,05,06,08,09,11,12} = 7, then the frozen
protocol's own `start_drift_max_s: 10` (A20) removes 06 (10.18 s) and 09 (10.06 s)
→ **5 retained, 1 disjoint pair** against registered minimums of **8 and 4**. Every
envelope of the night sits at 78–102% of the drift budget.
**MATERIAL 4 (Q1)** no option authenticates the OFF state; exhibit D's own method is
never offered. **5 (Q2)** the record emits no cap fields, detaching the v3.1 identity
from its constants. **6 (Q3)** (b)/(c) address one of two 1 µs gates. **7 (Q3)** (a)'s
"integer bound" does not exist and "vacuous" is wrong. **8 (Q2)** FLAG1 (pro-lead)
and review condition 5 (anti-(b)) omitted.
**NIT 9** C1's span column uses a midpoint, not the gated outer bracket (0.5–1.2 µs
low). **10** "~2000 native rows" is the interior count (2535 records / 591
rollovers). **11** C1's `per-envelope start drift s: [None × 12]` is a generator
artefact. **12** `min_l_infinity_residual_upper_bound_s = 1.49e-11 s` — seven orders
below the 250 µs allowance, strong *pro-lead* evidence — omitted.

## 6. Hygiene defects and effect per question

The packet is **substantially honest and mechanically assembled**: the code exhibits
diff byte-identical against `git show`; exhibit B1 is the **complete 129-line** cold
review, untruncated — the controlling authority handed over whole, not excerpted; C1
reproduced on re-derivation; the generator reads only primary records. No
fabrication found. The defects are of omission and drafting and are **not
one-directional** — several (condition 7's paraphrase, I3, FLAG1, the residual
figure) weaken the lead's own case, reading as good faith, not steering.

- **Q1:** C2's own implication (no read form ⇒ no authentication) not drawn →
  affirming (a) leaves consult I4 unsatisfied.
- **Q2:** compound question (fuses "are the caps wrong?" with "what replaces them?"
  and never asks what absolute drift a replacement admits); asymmetric
  quantification (idle only); condition 7 paraphrased off its named constants; I3,
  FLAG1 and condition 5 omitted.
- **Q3:** the gate is misidentified (one of two comparisons) and (a)'s input
  provenance is unsupported → (b) and (c) cannot deliver their stated effect.
- **Q4:** consult R2 and R3 omitted from exhibit and enumeration.
- **Q2/Q3 jointly — the most consequential omission.** C1 discloses the raw numbers,
  but the prose names only envelopes 03 and 06 as `start_drift` while C1's own
  exclusion list shows **03, 06 and 09**. Envelope 09 is one of the two envelopes the
  entire cap argument exists to recover, so the omission is directly load-bearing.

## 7. Verdict on the lead's labeled disposition

I concur on **direction** and dissent on **sufficiency**. Q1(a) is correctly
authorised by D-127 §1/§3 (B6, B7) and the slice is installed (C2), but it yields an
asserted rather than authenticated admission and does not discharge consult I4
without the `timed`-log attestation; I would rule Q1(c) with that mechanism named.
Q2(c) is the right containment and the only option protecting review condition 5's
negative control, and the packet *understates* its own authority — but (c) is not
rulable as drafted: no absolute drift backstop, and the caps detach from the
identity because the record emits no cap fields. Q3(a) is right and its float64
diagnosis is confirmed to the ulp, but its stated input does not exist, "vacuous" is
wrong, and Q3 as posed addresses only one of two 1 µs gates. Q4's correction of B8
is right and necessary; its enumeration is short by consult R2 and R3. Above all I
dissent from the implicit premise that the caps and the tolerance are what stand
between this pilot and eight retained envelopes: on the packet's own primary
evidence the best case under the lead's full disposition is **5 retained and 1 pair
against 8 and 4**, because `start_drift` independently removes envelopes 03, 06 and
09. A ruling that does not also name the start-drift mechanism licenses a re-run
that fails again for a cause already visible in this night's data.
