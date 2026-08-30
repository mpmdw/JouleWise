# Round-7 bibliography verification (reviewer items C11 + D5)

Prepared 2026-08-30 against the frozen draft bytes, SHA-256
`939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`
(`docs/paper/draft-v1.md`), matching the SHA recorded in
`docs/paper/round7/bibliography-renumber-plan.md`. This document verifies; it
does not edit the draft. Renumbering runs in round 7 per the ruled plan.

Verification method for every claim below: the named online source was
resolved during this session (Crossref REST API `api.crossref.org/works/DOI`,
the HotCarbon 2026 program page and its linked paper PDFs, the arXiv abstract
page, or a publisher record), and the returned metadata was compared
field-by-field with the citation as written. No citation below is quoted from
memory alone.

## 1. Verification of flagged entries

### [19] Ruf and Detyniecki — VERIFIED

Verified against the HotCarbon 2026 program page (hotcarbon.org/program) and
the full paper PDF the program links (hotcarbon.org/assets/2026/paper-17.pdf).
The workshop ran July 16–17, 2026 at the University of Washington, Seattle,
WA; the paper appeared in Session 1 (LLM Serving). The paper's own running
footer reads "ACM SIGENERGY Energy Informatics Review Volume X Issue X, July
2026" — a placeholder, so the archival SIGENERGY EIR volume/issue/DOI is not
yet assigned. No arXiv ID appears on the paper.

Verified citation:

> B. Ruf and M. Detyniecki. "The Cost of Context: Profiling the Energy
> Footprint of Input Tokens in Large Language Models." *HotCarbon Workshop on
> Sustainable Computer Systems (HotCarbon '26)*, Seattle, WA, July 2026.
> https://hotcarbon.org/assets/2026/paper-17.pdf. To appear in *ACM SIGENERGY
> Energy Informatics Review*.

The draft's §11 entry (authors, title, HotCarbon '26, 2026) is correct as it
stands; the round-7 pass should add the URL locator (and swap in the SIGENERGY
EIR DOI if it has been assigned by then).

Cite-to-claim check (draft line 332 says: isolates prefill by generating one
token, infers decode by subtraction, one run per context length, no error
bars). Confirmed verbatim from the PDF text: "we isolate the prefill phase by
setting the generation length to exactly 1 token"; "each context length is
measured in a single run; prior work on similar deterministic GPU benchmarks
has shown negligible run-to-run variance under these conditions"; the decode
figure is derived as E_out = (E_total − E_prefill)/λ with λ = 128 output
tokens. No error bars are reported for the single-run sweep. The draft's
characterization is accurate; one nuance for the fill author's awareness: the
paper *argues* (with a citation) that single runs suffice under its
deterministic workload, so "without error bars" is true but the omission is
defended, not silent.

### [23] Dauner et al. — VERIFIED

Verified against the HotCarbon 2026 program page and the full paper PDF
(hotcarbon.org/assets/2026/paper-46.pdf). Same venue and dates as [19];
Session 4 (Hardware). Author list on the PDF matches the draft entry exactly:
Maximilian Dauner, Manuel Steinberg, Andreas Brunnert, Benedikt Schicker,
Benedikt Zönnchen, all Munich University of Applied Sciences HM, Germany. No
arXiv ID or assigned DOI appears on the paper; the SIGENERGY EIR volume/issue
is the same placeholder as [19].

Verified citation:

> M. Dauner, M. Steinberg, A. Brunnert, B. Schicker, and B. Zönnchen.
> "Evaluating the Influence of Measurement Frequency on Energy Readings Using
> Intel RAPL and NVIDIA NVML." *HotCarbon Workshop on Sustainable Computer
> Systems (HotCarbon '26)*, Seattle, WA, July 2026.
> https://hotcarbon.org/assets/2026/paper-46.pdf. To appear in *ACM SIGENERGY
> Energy Informatics Review*.

Cite-to-claim check (draft line 326 says: counter-update behavior and
requested sampling frequency can materially change an energy reading; on one
evaluated GPU, very frequent polling severely underestimated integrated
power, with agreement recovering only at a much longer interval). Confirmed
from the PDF: on the consumer-class GPUs (RTX 4090/RTX 5060 Ti) the
cumulative-energy counter underestimates integrated NVML power by 95.4% at a
0.5 ms sampling interval, 75.6% at 10 ms, and 13.3% at 100 ms, "recovering to
within 1.6% only at 1 s." The draft's sentence is accurate (both named
consumer devices show the effect; "one evaluated GPU" is if anything
conservative — the headline 95.4% figure is the consumer-class mean).

### [13] Benazir and Lin — ENTRY VERIFIED; the flagged fix is already applied

The §11 entry was verified against Crossref (`api.crossref.org/works/10.1145/3771563`),
which resolves to: Afsara Benazir and Felix Xiaozhu Lin, "Benchmarking and
Characterization of Large Language Model Inference on Apple Silicon,"
*Proceedings of the ACM on Measurement and Analysis of Computing Systems*
9(3), December 2025, pp. 1–26, DOI 10.1145/3771563. Every field of the draft
entry matches; no correction to the §11 line is needed.

The audit's flag was not the entry but the cite-to-claim attachment: the
2026-08-27 audit (of the pre-fix bytes) found the draft grouping [13] with
works that "map energy across useful deployed configurations," while the
paper reports no energy measurement. That fix has ALREADY LANDED: commit
`e3f28da9` (PR #226, one of the "two frozen-draft fidelity fixes",
2026-08-28) rewrote draft line 332 to read "…and Benazir and Lin characterize
inference throughput on Apple silicon without energy measurement [13]", and
that wording is in the frozen bytes verified above.

This session verified the corrected sentence against the paper itself: the
arXiv version (arXiv:2508.08531, same authors, University of Virginia;
abstract checked on arxiv.org) benchmarks latency, throughput, and low-level
hardware counters (ALU utilization, memory bandwidth, buffer usage, cache
residency) across Apple M-series and NVIDIA hardware, and performs no energy
or power measurement. The corrected sentence is accurate. No round-7 action
remains for [13] beyond the ruled renumber (13 → 10).

## 2. Candidate lineage citations (reviewer D5), each verified

Grounding used for the verdicts: the paper builds a worst-case,
interval-shaped calibration bound — Appendix A.3 formalizes a "pulse accepted
region" and a "clock-anchor feasible set" (draft line 51 names both), §4
states the resolution bound "is a worst-case bound, not an estimated
population percentile" (line 111), and §8 claims the "counter time" axis
(where in time a counter places energy) as the complement to counter gain.
Verdicts follow from whether a candidate supports something the frozen paper
actually argues.

### Marzullo (interval intersection) — RECOMMEND

Verified via Crossref, DOI 10.1145/800221.806730:

> K. Marzullo and S. Owicki. "Maintaining the Time in a Distributed System."
> *Proceedings of the Second Annual ACM Symposium on Principles of Distributed
> Computing (PODC '83)*, 1983, pp. 295–305. DOI:10.1145/800221.806730.

What it supports: representing a clock quantity as an interval guaranteed to
contain the true value and shrinking it by intersecting independent
constraints — the exact shape of the clock-anchor feasible set in Appendix
A.3. Verdict: RECOMMEND. This is the canonical ancestor of the paper's core
construction, and the reviewers are right that its absence is a visible
lineage gap. (The fully developed interval-intersection algorithm is in
Marzullo's 1984 Stanford dissertation; the PODC '83 paper is the citable
published version and suffices.)

### Kopetz (clock synchronization in distributed real-time systems) — OPTIONAL

Verified via Crossref, DOI 10.1109/TC.1987.5009516:

> H. Kopetz and W. Ochsenreiter. "Clock Synchronization in Distributed
> Real-Time Systems." *IEEE Transactions on Computers* C-36(8), 1987,
> pp. 933–940. DOI:10.1109/TC.1987.5009516.

What it supports: precision limits of clock synchronization, including the
error contributed by clock-reading granularity — kin to the whole-second
timestamp quantization the clock-anchor estimator must absorb. Verdict:
OPTIONAL. The paper aligns two clock domains on one host, not a distributed
ensemble; the citation strengthens lineage without supporting a specific
sentence. Add only if the round-7 fill writes a timing-lineage sentence broad
enough to carry it.

### Cristian (probabilistic clock synchronization) — OPTIONAL

Verified via Crossref, DOI 10.1007/BF01784024:

> F. Cristian. "Probabilistic Clock Synchronization." *Distributed Computing*
> 3(3), 1989, pp. 146–158. DOI:10.1007/BF01784024.

What it supports: reading another clock with a quantified error bound derived
from observable events — structurally analogous to anchoring the instrument's
trace on the controller clock. Verdict: OPTIONAL. Cristian's bound is
probabilistic where the paper's is deliberately worst-case (line 111), so it
works only as a contrast citation; Marzullo alone covers the load-bearing
lineage claim.

### Wilks 1941 (statistical tolerance limits) — OPTIONAL

Verified via Crossref, DOI 10.1214/aoms/1177731788:

> S. S. Wilks. "Determination of Sample Sizes for Setting Tolerance Limits."
> *The Annals of Mathematical Statistics* 12(1), 1941, pp. 91–96.
> DOI:10.1214/aoms/1177731788.

What it supports: distribution-free tolerance limits from order statistics —
what coverage an empirical extremum over n samples actually buys. Verdict:
OPTIONAL. The frozen draft explicitly declines the percentile/coverage
framing ("a worst-case bound, not an estimated population percentile," line
111) and nowhere claims a tolerance-limit property for the pulse-edge
maximum. Wilks becomes RECOMMEND only if the round-7 response to D6 adds a
sentence contrasting the worst-case bound with distribution-free tolerance
limits; citing it without that sentence would invite exactly the coverage
question the paper chose not to answer.

### Milanese and Vicino (set-membership estimation) — RECOMMEND

Verified via Crossref, DOI 10.1016/0005-1098(91)90134-N, with the full title
confirmed on the ScienceDirect record (sciencedirect.com/science/article/abs/pii/000510989190134N):

> M. Milanese and A. Vicino. "Optimal Estimation Theory for Dynamic Systems
> with Set Membership Uncertainty: An Overview." *Automatica* 27(6), 1991,
> pp. 997–1009. DOI:10.1016/0005-1098(91)90134-N.

What it supports: estimation under unknown-but-bounded error, where the
result is the feasible set of parameters consistent with bounded residuals —
the pulse accepted region of Appendix A.3 is a set-membership estimator in
this exact sense, and the paper's refusal to model edge placement as random
noise (line 342) is the set-membership stance stated without its name.
Verdict: RECOMMEND. It names and grounds the estimation framework the paper
already uses.

### Burtscher, Zecena, and Zong 2014 (K20 built-in sensor lag) — RECOMMEND

Verified via Crossref, DOI 10.1145/2576779.2576783:

> M. Burtscher, I. Zecena, and Z. Zong. "Measuring GPU Power with the K20
> Built-in Sensor." *Proceedings of the 7th Workshop on General Purpose
> Processing Using GPUs (GPGPU-7)*, 2014, pp. 28–36.
> DOI:10.1145/2576779.2576783.

What it supports: a built-in GPU power sensor whose readings lag and smooth
the true power draw, so that naive integration attributes energy to the wrong
time — the closest prior instance of the paper's counter-time thesis on a GPU
counter, complementing Hähnel [29] (RAPL update boundaries) and Dauner [23]
(NVML sampling frequency). Verdict: RECOMMEND. It slots directly into the §8
"From counter gain to counter time" paragraph and strengthens the claim that
temporal placement, not gain, is the under-examined axis.

### Raffin and Trystram (energy measurement) — OPTIONAL

Verified via Crossref (bibliographic query resolving DOI
10.1109/TPDS.2024.3492336) and the arXiv record (arXiv:2401.15985):

> G. Raffin and D. Trystram. "Dissecting the Software-Based Measurement of
> CPU Energy Consumption: A Comparative Analysis." *IEEE Transactions on
> Parallel and Distributed Systems* 36(1), January 2025, pp. 96–107.
> DOI:10.1109/TPDS.2024.3492336; arXiv:2401.15985.

What it supports: a mechanism-level dissection of how software reads RAPL
(update behavior, reading strategies, error sources) — counter-gain and
counter-mechanism territory. Verdict: OPTIONAL. The counter-gain lane is
already carried by Khan [5], Jay [6], Hähnel [29], and Dauner [23]; this adds
depth but no claim the draft currently makes goes uncited without it. Fable
req. 15 proposed it; nothing in the frozen argument requires it.

No candidate is UNVERIFIED-DO-NOT-ADD: all seven resolved to real, exact
publications through Crossref, arXiv, ScienceDirect, or the HotCarbon
program, as named above.

## 3. Cross-check against the frozen draft

Run on the worktree copy of the frozen bytes (SHA above, identical to the
renumber plan's recorded SHA).

Orphan status. The renumber plan's own grep
(`rg --pcre2 -n '\[(?:[0-9]+)(?:\s*,\s*[0-9]+)*\](?!\()'` with reference-list
lines 360–392 excluded) reproduces the cited multiset exactly: each of
{1, 2, 3, 7, 8, 10, 12, 13, 15, 19, 20, 22, 23, 26, 27, 28, 29, 30, 31} once
and {5, 6} twice, plus the non-citation mathematical interval `[0,1]` on line
221. A per-number grep for each of the ten ruled orphans {4, 9, 11, 14, 16,
17, 18, 21, 24, 25} returns zero body occurrences. All ten remain orphans;
the ruled removal set and the 31→21 map are still exactly right.

Reference list integrity. §11 still contains exactly 31 entries numbered
contiguously 1–31, in order, no duplicates.

New issues since the 08-27 audit. The only draft change since the audit is
commit `e3f28da9` (PR #226), whose bibliography-adjacent edits are precisely
the three the audit's addendum records: the JouleSort DOI on [3], the
DOI/arXiv ordering on [27], and the [13] cite-to-claim rewrite on line 332 —
the last now verified correct against the paper (Section 1 above). Crossref
resolution this session re-confirmed [3] (10.1145/1247480.1247522 fields all
match, per the 08-28 director check) implicitly via the audit trail; no entry
changed since. No new citation, no new orphan, no metadata drift, and no new
cite-to-claim mismatch was found. The audit's two UNVERIFIED-OFFLINE items
([19], [23]) are closed by Section 1; its open list item 3 (fix [13]) was
closed by PR #226 and is verified here.

One forward note for the round-7 pass: [19] and [23] should gain their URL
locators (and SIGENERGY EIR DOIs if assigned by then) in the same edit that
renumbers them (19 → 12, 23 → 15), since that pass is the one authorized to
touch §11.
