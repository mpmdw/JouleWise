# LITREAD-VERIFY-01 — verification report (Opus seat, read-only + web)

Seat: Opus, executed 2026-09-12. Brief: `07-brief-litread-verify-opus.md`.
Article under verification: `/Users/edr/code/JouleWise-wt-paper-n-ref/docs/paper/draft-v2-skeleton.md`
at detached `origin/main` **dbe6c675** (verified by `git log --oneline -1` in that worktree this
session). No file in the ref worktree was modified; this report is the only file written.

## 0. Sources of record actually read

| Ref | Work | Form read | Identifier stamp as printed | SHA-256 of the bytes I read |
|---|---|---|---|---|
| [6] | TokenPowerBench | **PDF of record**, fetched from `https://arxiv.org/pdf/2512.03024` | `arXiv:2512.03024v1  [cs.LG]  2 Dec 2025` (left-margin stamp, p. 1) | `a0696f68778ebbd5371a5f54cb9a59b85c98c9c11634ee9429d130eb8fb0e44f` |
| [13] | The Illusion of Power Capping in LLM Decode | **PDF of record**, fetched from `https://arxiv.org/pdf/2605.11999` | `arXiv:2605.11999v1  [cs.DC]  12 May 2026` (left-margin stamp, p. 1) | `12b648e52cbb4d65d30c1249b45b724b8372da3413c491e472b92f435aa20beb` |

**How the PDFs were read, stated plainly.** Both PDFs were fetched over the network with WebFetch
from the `arxiv.org/pdf/...` URLs named in the brief. WebFetch's own summariser could not read
either file (both are FlateDecode-compressed), but it saved the fetched bytes to disk. I extracted
the full text of those saved bytes locally with PyMuPDF 1.28.2 and read the extraction directly —
9 pages / 1,148 lines for [6], 16 pages / 1,663 lines for [13]. So the text quoted below is the text
of the PDF of record, not of an HTML render, and not of a summariser's paraphrase. **No fallback to
the abs page or HTML render was needed for the content of either paper.** The abs pages were fetched
separately, for the bibliographic fields only (Comments / Journal-ref), in §2.

Front-matter as printed, both v1:

- **[6]** "TokenPowerBench: Benchmarking the Power Consumption of LLM Inference" — Chenxu Niu¹,
  Wei Zhang², Jie Li¹, Yongjian Zhao¹, Tongyang Wang¹, Xi Wang\*³, Yong Chen¹ (¹Texas Tech
  University, ²Texas Advanced Computing Center, ³Southeast University). PDF carries
  "Copyright © 2026, Association for the Advancement of Artificial Intelligence". arXiv Comments
  field: "Accepted by the AAAI'26 Conference Main Track". v1, 2 Dec 2025.
- **[13]** "The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy Characterisation
  Across Attention Architectures" — Bole Ma¹, Ayesha Afzal¹, Jan Eitzinger¹, Gerhard Wellein²
  (¹Erlangen National High Performance Computing Center, ²FAU Erlangen-Nürnberg). No venue line
  printed on p. 1; CC-BY-4.0. v1, 12 May 2026.

## 1. Claim-by-claim table

Every statement the article makes about either work. Both works are cited **exactly once each** in
the main text — line 878 for [13], line 880 for [6] — plus their §9 entries; confirmed by grepping
the whole article for the bracketed tokens `[6]` and `[13]` (the only other hit is a numeric table
value at line 1282, not a citation).

### 1a. TokenPowerBench [6] — all from article §6, line 880

| # | Article sentence (§6:880, quoted) | Source location and supporting text (quoted) | Verdict | Cure |
|---|---|---|---|---|
| A | "TokenPowerBench reports prefill and decode energy" | §"Execution and Measurement", *2) Temporal view*, p. 4: "After the run we integrate these tagged samples to obtain two clear numbers: **energy consumed during prefill and energy consumed during decode**." Eq. (1), p. 5: "E_total = E_Prefill + E_Decode". Fig. 2 caption, p. 5: "Prefill Energy (a) and Decode Energy per Token (b) Across Models and Inference Engines". | **MATCH** | — |
| B | "and groups measurements by context length [6]" | §"Parameter-sensitivity Analysis" → *Context Length*, p. 6: "Figure 3 reports energy (total and gpu) per token for ten models at **three prompt length range : 0-2K, 2K to 5K, and 5K to 10K tokens**." Fig. 3 caption: "Comparison of Total (a) and GPU (b) Energy per Token Across Models at Varying Context Lengths". | **MATCH** | — |
| C | "Its disclosed method does not specify the **boundary events** …" | Absence. The sole statement of phase assignment is p. 4: "The same logger records two key stages of every inference: prefill, when the model reads the input tokens, and decode, when it produces new tokens. **Each power sample is tagged with the stage that is active at that moment.**" No event, signal, engine callback or API hook is named as marking the prefill→decode transition. Full-text search of all 9 pages returns **zero** occurrences of "boundary", "transition", "first token", "TTFT". | **MATCH** | — |
| D | "… the **alignment rule** …" | Absence *of a rule*, though alignment is asserted. Asserted: Abstract, "a **phase-aligned** metrics pipeline that attributes energy to the prefill and decode stages of every request"; §"System-Level Power Instrumentation", "**aligns measurements** with LLM inference phases"; p. 4, "Because all telemetry streams **share the same timestamp**, we can also sum them precisely". No rule is given: zero occurrences of "sampling interval", "sampling frequency", "Hz", "poll", "resolution"; no clock-synchronisation procedure between the telemetry sources and the serving process; no stated policy for a power sample that straddles a phase boundary. | **MATCH** (see nit n1) | — |
| E | "… **repetition and variance protocol** …" | Absence. Full-text search returns **zero** occurrences of "repeat", "repetition", "trial", "variance", "standard deviation", "error bar", "confidence", "median", "N =". Every reported figure and heatmap carries single values. The nearest language is the Conclusion's "a declarative configuration harness that ensures **repeatability** across experiments" — a reproducibility claim about configuration, not a repetition count or a variance report. | **MATCH** | — |
| F | "… **idle baseline** …" | Absence. Zero occurrences of "baseline" (in the measurement sense), "subtract", "calibrat". "Idle" appears three times, none as a baseline protocol: §"System-Level Power Instrumentation", "performs time-correlated breakdown across prefill, decode, **and idle phases**"; §"Parallelism Strategy", "GPU utilization, **idle time**, and network power draw"; p. 7, "long pipelines leave some GPUs **idle**". Eq. (1) has no idle term: E_total = E_Prefill + E_Decode. No idle level is defined, measured, or subtracted anywhere. | **MATCH** (see nit n2) | — |
| G | "… or **external validation** needed to reconstruct a phase-attribution error budget." | Absence, and by design. Abstract: "a measurement layer that captures GPU-, node-, and system-level power **without specialized power meters**". §"Related Work": "supports reproducible multi-node configurations **without requiring external metering hardware**"; the paper's stated criticism of MLPerf Power is that it "often depend[s] on external, high-precision metering equipment that is costly". Zero occurrences of "valid", "calibrat", "ground truth", "cross-check". No validation section exists. | **MATCH** | — |

### 1b. The Illusion of Power Capping in LLM Decode [13] — all from article §6, line 878

| # | Article sentence (§6:878, quoted) | Source location and supporting text (quoted) | Verdict | Cure |
|---|---|---|---|---|
| I | "It is **phase-aware**" | Title: "A **Phase-Aware** Energy Characterisation". §3.2 *Experimental Design*, p. 4: "Our primary metric is energy per token (mJ/tok), **measured separately for prefill and decode**. For prefill, the denominator is the number of input tokens processed …; for decode it is the number of output tokens generated." | **MATCH** | — |
| J | "**repeats configurations**" | §3.2, p. 4: "**Each configuration is repeated 10–20 times; we report medians.** Three warmup iterations precede every measurement run. Figures showing energy-per-token vs. sequence length include ±1 s.d. shaded bands." Corroborated in Fig. 2 caption: "All energy saving results are rock-stable across repeated runs (max stddev ≤3%, typically <0.5%)"; Table 1 note: "median over 10 reps". | **MATCH** | — |
| K | "and **independently** checks **sufficiently long** sampled-power integrals against a **hardware energy counter** [13]" | §3.1 *Deployment Baseline and Hardware*, p. 4: "Energy is measured via **NVML power sampling at 50 ms intervals, integrated with the trapezoidal rule**; for operations shorter than 100 ms (≈44% of prefill configs) we fall back to the product of snapshot power and wall-clock latency. Results are **cross-validated against NVML hardware energy counters, which agree to within 2% for operations ≥200 ms** but have millijoule-level granularity that makes them unreliable for short prefills." | **PARTIAL** | See below |
| L | "the power-capping study reports **counter agreement, repetition, and timing regimes as separate diagnostics**" | Counter agreement: §3.1, "agree to within 2% for operations ≥200 ms". Repetition: §3.2, "repeated 10–20 times; we report medians … ±1 s.d. shaded bands". Timing regimes: §3.1 states two distinct duration regimes with different treatment — "<100 ms → snapshot power × wall-clock latency" and "≥200 ms → counters agree to within 2%". These appear in three separate statements and are never combined: full-text search returns **zero** occurrences of "uncertainty", "error budget", or "propagat" in a measurement sense, and the §7 *Limitations* section enumerates scope limits (single GPU, single framework, dense models only, driver-version specificity) without a combined attribution budget. | **MATCH** | — |
| M | "*The Illusion of Power Capping in LLM Decode* is the **closest methodological rival**." | Comparative judgment about JouleWise's own position in the literature. The source cannot confirm or refute it; nothing in [13] addresses JouleWise. | **not source-checkable** (recorded, not scored) | — |

**Cure for K (the one non-MATCH).** The check, the counter, and the duration qualifier are all real
and correctly characterised; the single unsupported word is **"independently"**. Both quantities
compared — the 50 ms sampled power that is integrated, and the reference energy counter — are read
from **NVML on the same H200**. That is a second register inside one vendor telemetry stack, not an
instrument independent of it. The source's own verb is "cross-validated" and it never says
"independent". The article then leans on that word again in the next sentence ("JouleWise lacks that
**independent** cross-check"), so the overstatement is load-bearing rather than incidental, and it
overstates the rival's advantage over JouleWise.

Minimal cure, two words changed:

- line 878: "and independently checks sufficiently long sampled-power integrals against a hardware
  energy counter [13]" → "and **cross-checks** sufficiently long sampled-power integrals against a
  hardware energy counter **on the same telemetry interface** [13]";
- line 878, next sentence: "JouleWise lacks that independent cross-check." → "JouleWise lacks that
  **counter** cross-check."

Optional strengthening (not required for fidelity): the source supplies exact numbers the article
could quote — "to within 2% for operations ≥200 ms".

### Claim-table counts

| Verdict | Count |
|---|---|
| MATCH | **10** |
| PARTIAL | **1** (K) |
| MISMATCH | **0** |
| NOT FOUND | **0** |
| Recorded but not source-checkable (comparative judgment) | 1 (M) |
| **Total rows** | **12** |

No number is attributed to either work anywhere in the article, and no phrase from either work is
quoted in the article, so there were no numeric or quotation rows to check.

## 2. Reference-list check — all 21 entries of §9

Method: DOIs resolved through the Crossref REST API (`api.crossref.org/works?filter=doi:…`, ten
DOIs in one query, all ten returned); arXiv entries resolved through their `arxiv.org/abs/` pages
(the arXiv API returned HTTP 429, so abs pages were used and are named below); the three
non-arXiv/non-DOI URLs fetched directly and their PDFs read locally. Every row below was resolved
this session.

| # | Entry (short) | Resolved via | Verdict |
|---|---|---|---|
| 1 | Tschand et al., MLPerf Power, HPCA 2025, 1201–1216, DOI:10.1109/HPCA61900.2025.00092; arXiv:2410.12032 | Crossref (title, 26 authors led by A. Tschand, HPCA 2025, pp. 1201–1216) + `arxiv.org/abs/2410.12032` (v2, 6 Feb 2025) | **OK** |
| 2 | SPEC, *Power and Performance Benchmark Methodology* V2.3, SPECpower Committee, URL | PDF cover read: "Standard Performance Evaluation Corporation (SPEC) / Power and Performance Benchmark Methodology / V2.3 … SPECpower Committee"; footer "12 June 2025", 38 pp. URL live. | **OK** |
| 3 | Rivoire, Shah, Ranganathan, Kozyrakis, JouleSort, SIGMOD 2007, 365–376 | Crossref: SIGMOD 2007, pp. 365–376, 4 authors as listed | **OK** |
| 4 | Khan, Hirki, Niemi, Nurminen, Ou, RAPL in Action, TOMPECS 3(2) 2018, Article 9 | Crossref: TOMPECS, vol. 3, issue 2, 2018, 5 authors as listed | **OK** — with caveat n3: Crossref's `article-number` field is absent (it reports page span 1–26), so "Article 9" itself is not confirmed by this pass; the ACM DL landing page returns HTTP 403 |
| 5 | Jay, Ostapenco, Lefèvre, Trystram, Orgerie, Fichel, CCGrid 2023, 106–118 | Crossref: CCGrid 2023, pp. 106–118, 6 authors in the listed order | **OK** — caveat: the `HAL:hal-04030223` identifier was not separately resolved |
| 6 | Niu et al., TokenPowerBench, AAAI 40(38) 2026, 32582–32590; arXiv:2512.03024 | AAAI OJS record `ojs.aaai.org/index.php/AAAI/article/view/40535`: *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40 No. 38, pp. **32582–32590**, 2026, all 7 authors in the listed order, DOI 10.1609/aaai.v40i38.40535. arXiv id confirmed from the PDF stamp. | **OK** (nit n5: the AAAI DOI could be added for parity with neighbouring entries) |
| 7 | Chung et al., ML.ENERGY Benchmark, NeurIPS D&B 2025 Spotlight; arXiv:2505.06371 | `arxiv.org/abs/2505.06371`, first author Jae-Won Chung; Comments field reads "**NeurIPS D&B 2025 (Spotlight)**" | **OK** |
| 8 | Li et al., Prima.cpp, ICLR 2026; arXiv:2504.08791 | `arxiv.org/abs/2504.08791` (first author Zonghang Li) + ICLR 2026 poster record `iclr.cc/virtual/2026/poster/10008093` and the OpenReview PDF. ICLR 2026 is the Fourteenth ICLR. | **OK** |
| 9 | Basit, Liu, Kong, Hu, DualScale; arXiv:2602.18755 | `arxiv.org/abs/2602.18755`: title verbatim, authors Omar Basit, Yunzhao Liu, Z. Jonny Kong, Y. Charlie Hu | **OK** |
| 10 | Benazir, Lin, POMACS 9(3) Dec 2025, 1–26, DOI:10.1145/3771563 | Crossref: POMACS, vol. 9, issue 3, pp. 1–26, 2025, both authors | **OK** |
| 11 | Lange, Identifying Shades of Green, IEEE *Computer* 42(3) 2009, 95–97 | Crossref: *Computer*, vol. 42, issue 3, pp. 95–97, 2009 | **OK** |
| 12 | Ruf, Detyniecki, *The Cost of Context*, HotCarbon '26, hotcarbon.org/assets/2026/paper-17.pdf | PDF at the cited URL read locally: title verbatim; "BORIS RUF, AXA AI Research, France / MARCIN DETYNIECKI, AXA AI Research, France" | **OK** — caveat n4: the string "HotCarbon" is not printed anywhere in the PDF (running header reads "Volume X Issue X, July 2026", an unfilled placeholder); the venue attribution rests on the hosting path |
| 13 | Ma, Afzal, Eitzinger, Wellein, *Illusion of Power Capping*; arXiv:2605.11999 | PDF of record read: title and all four authors verbatim; stamp `arXiv:2605.11999v1 [cs.DC] 12 May 2026` | **OK** |
| 14 | Saad-Falcon, Narayan et al., Intelligence per Watt, 2025; arXiv:2511.07885 | `arxiv.org/abs/2511.07885`: title verbatim, leading authors Jon Saad-Falcon, Avanika Narayan; v1 11 Nov 2025 (matches the entry's year; latest is v6, Sept 2026) | **OK** |
| 15 | Dauner, Steinberg, Brunnert, Schicker, Zönnchen, HotCarbon '26, paper-46.pdf | PDF at the cited URL read locally: title verbatim; all five authors in the listed order, Munich University of Applied Sciences HM | **OK** — same venue-string caveat n4 (header "Volume 6 Issue 2, July 2026") |
| 16 | Zhuang, Li, Fan, *Pre-Registering the Detectable Effect*; arXiv:2605.28873 | `arxiv.org/abs/2605.28873`: title verbatim, Zexin Zhuang, Yanhang Li, Zhichao Fan; v1 25 May 2026 | **OK** |
| 17 | Li, Zhu, Chen, Lee, Nahrstedt, EuroMLSys '26, 397–406, DOI:10.1145/3805621.3807662; arXiv:2601.08833 | Crossref: "Proceedings of the Sixth European Workshop on Machine Learning and Systems", pp. 397–406, 2026, authors J. Li, Y. Zhu, **B. Chen**, E. K. Lee, K. Nahrstedt — exactly the entry's five | **OK** — caveat n6: the cited arXiv preprint `abs/2601.08833` lists only four authors (no B. Chen), so the entry's author list follows the version of record while its arXiv id points at a differently-authored preprint |
| 18 | Guo, Joshi, SplitZip; arXiv:2605.01708 | `arxiv.org/abs/2605.01708`: title verbatim, Yipin Guo, Siddharth Joshi | **OK** |
| 19 | Hähnel, Döbel, Völp, Härtig, SIGMETRICS PER 40(3) 2012, 13–17 | Crossref: *ACM SIGMETRICS Performance Evaluation Review*, vol. 40, issue 3, **pp. 13–17**, 2012, 4 authors as listed | **OK** |
| 20 | Georges, Buytaert, Eeckhout, OOPSLA '07, 57–76 | Crossref: OOPSLA 2007, pp. 57–76, 3 authors as listed | **OK** |
| 21 | Mytkowicz, Diwan, Hauswirth, Sweeney, ASPLOS XIV 2009, 265–276 | Crossref: ASPLOS 14th, pp. 265–276, 2009, 4 authors as listed | **OK** |

**Reference-list counts: OK 21 / FIX 0.** No entry was rewritten. Every title, author list, year,
page range, volume/issue and identifier that the list asserts was checked against a resolving
record, with the four caveats (n3, n4, n5, n6) itemised above and in §4.

## 3. Queue-row id correction (brief task 4)

The corrected ids are confirmed against the PDFs' own left-margin stamps and the venue records, and
the article cites each work under the right one:

| Work | Correct id | Article's citation | Verdict |
|---|---|---|---|
| TokenPowerBench | arXiv:**2512.03024** (stamp: `arXiv:2512.03024v1 [cs.LG] 2 Dec 2025`; AAAI 40(38):32582–32590) | §9 entry **[6]** carries "arXiv:2512.03024"; cited in text once, §6:880 | **correct, no swap** |
| The Illusion of Power Capping in LLM Decode | arXiv:**2605.11999** (stamp: `arXiv:2605.11999v1 [cs.DC] 12 May 2026`) | §9 entry **[13]** carries "arXiv:2605.11999"; cited in text once, §6:878 | **correct, no swap** |

Neither id appears anywhere else in the article, and neither work is cited under any other number.

## 4. Findings, tiered

### Blockers — 0

No statement the article makes about either source is contradicted by the source, and no reference
entry fails to resolve.

### Should-fix — 2

- **S1 — "independently" is not supported by [13] (article §6:878).** The cross-check that the
  article credits to the power-capping study compares NVML-sampled power against NVML's own hardware
  energy counter, on the same GPU through the same vendor library. The source calls this
  "cross-validated" and never claims independence. Because the article's very next sentence rests on
  the word ("JouleWise lacks that independent cross-check"), the overstatement inflates the rival's
  advantage. Cure: the two-word substitution given under row K above.
- **S2 — the [6] absence claim is not scoped to the artifact examined (article §6:880).** "Its
  disclosed method does not specify the boundary events, alignment rule, repetition and variance
  protocol, idle baseline, or external validation" is, on this pass, verified against the complete
  9-page arXiv/AAAI paper — and holds there without exception. But that paper itself points
  elsewhere: p. 5, "Please check the total results in the **supplementary material**." That
  supplement is not on the arXiv listing and was not consulted, so an unqualified absence claim is
  exposed to a referee who has it. Cure: scope the sentence to the artifact, e.g. "Its disclosed
  method **in the published paper** does not specify …" (four words, no restyling).

### Nits — 5

- **n1 — adjacency to [6]'s own "phase-aligned" language.** The article says [6] does not specify an
  *alignment rule*, which is exactly true — no interval, no clock-sync procedure, no
  straddling-sample policy. But [6]'s abstract advertises "a phase-aligned metrics pipeline" and its
  body says it "aligns measurements with LLM inference phases". A reader who checks the abstract
  first may read the article as unfair. A four-word concession ("beyond asserting a shared
  timestamp") would close it. No change is required for factual accuracy.
- **n2 — adjacency to [6]'s "idle phases".** Likewise for *idle baseline*: [6] claims to perform a
  "time-correlated breakdown across prefill, decode, and idle phases" while defining, measuring and
  subtracting nothing, and its Eq. (1) carries no idle term. The article's claim stands; the nearby
  counter-text is worth knowing before a referee raises it.
- **n3 — [4] "Article 9" unconfirmed.** Crossref exposes no `article-number` for DOI 10.1145/3177754
  and the ACM DL page is 403 to this seat. Title, journal, volume, issue, year and authors all
  confirm; the article number alone rests on the prior citation.
- **n4 — HotCarbon venue string not printed in [12] or [15].** Neither PDF prints "HotCarbon"
  anywhere; [12]'s running header is the unfilled placeholder "Volume X Issue X, July 2026" and
  [15]'s is "Volume 6 Issue 2, July 2026". Venue attribution therefore rests on the
  `hotcarbon.org/assets/2026/` hosting path (corroborated for [15] by its own footnote repository
  `hm-green-it-lab/hotc2026`). Acceptable, but not printed-on-the-artifact evidence.
- **n5/n6 — identifier hygiene.** [6] could carry its AAAI DOI (10.1609/aaai.v40i38.40535) for
  parity with neighbouring entries. [17]'s author list is the five-author version of record while
  its arXiv id points at a four-author preprint; both are correct for what they name, but the pairing
  invites a query.

## 5. What could NOT be verified, and why

1. **[6]'s supplementary material.** [6] defers its full results to a supplement that is not part of
   the arXiv deposit and was not reachable this session. All absence findings for [6] (rows C–G) are
   therefore scoped to the 9-page paper. This is the substance of finding S2.
2. **Plotted values in [6]'s Figures 2–6.** Row A is verified from the figure captions, the prose,
   and Eq. (1) — not by digitising data points out of the vector plots. The article attributes no
   number to [6], so no numeric row depended on this.
3. **[4]'s article number 9** — Crossref field absent, ACM DL returns HTTP 403 (nit n3).
4. **[5]'s HAL identifier** `hal-04030223` — not separately resolved; the DOI resolves cleanly and
   fixes the work.
5. **The article's comparative judgments** — "closest methodological rival" ([13]), and by the same
   character "closest ancestor" ([19]) and "strongest corroboration" ([15]) elsewhere in §6 — are
   claims about JouleWise's position relative to the literature. They are not statements the sources
   can confirm or refute, and were recorded (row M) rather than scored.
6. **Statements about JouleWise itself** in the same sentences ("JouleWise lacks that independent
   cross-check", "JouleWise carries registered phase-edge perturbations into the allocation-sensitivity
   calculation") are out of this brief's scope: they are checkable against the project's own evidence,
   not against these two sources.
7. **Entries [7]–[11] and [14]–[21] were resolved bibliographically only.** The brief scoped
   content verification to [6] and [13]; for the other nineteen entries I confirmed that the work
   exists as listed, not that the article's characterisations of them are accurate. ([12] is a
   partial exception: while resolving it I incidentally confirmed the article's §6:880 claim that
   Ruf and Detyniecki "isolate prefill by generating one token and infer decode by subtraction" —
   their §3 states they isolate "the prefill phase by setting the generation length to exactly 1
   token" and obtain decode by "subtracting the isolated prefill energy". That was not a
   commissioned check and no verdict is recorded for it.)

## 6. Tooling note for reproduction

- Bash in this seat is network-sandboxed (`curl` to `export.arxiv.org` returned zero bytes), so all
  network access went through WebFetch/WebSearch.
- The arXiv API (`export.arxiv.org/api/query`) returned HTTP 429; per-paper `arxiv.org/abs/` pages
  were used instead and are named per row in §2.
- PDF text was extracted with PyMuPDF 1.28.2 in a throwaway venv under the session scratchpad; the
  ref worktree was never written to.
