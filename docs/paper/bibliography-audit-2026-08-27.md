# Bibliography audit — draft-v1 (2026-08-27)

> **Director disposition (Fable, 2026-08-28) — read before the tables.** The Sol
> seat below removed the ten uncited entries ([4], [9], [11], [14], [16], [17],
> [18], [21], [24], [25]) from §11. That removal was **NOT applied** to the
> branch: it leaves a numbered reference list with ten gaps, and closing the
> gaps means renumbering body citations, which the round-6 freeze forbids. The
> ten entries therefore still stand in §11 and every "removed as uncited" status
> in the tables below should be read as "uncited; removal proposed, pending a
> magistrate ruling" (options: keep as-is, remove with gaps, or renumber at
> round 7 alongside the fills). The two edits that WERE applied to §11 are the
> JouleSort DOI on [3] (`10.1145/1247480.1247522`) and the DOI/arXiv ordering on
> [27]. Online verification by the director via api.crossref.org on
> 2026-08-28: DOIs for [3], [27], [29] Hähnel, [30] Georges, and [31] Mytkowicz
> each resolve to the stated title, first author, venue, and year. [19] and
> [23] (HotCarbon '26) remain UNVERIFIED (no DOI in the entries).

## Method and scope

This was an offline audit. No network lookup or DOI resolver was used. I read the
whole draft, the 2026-08-07 audit, related_work_draft.md, the local source
reports they point to, and ruling item 57. VERIFIED-OFFLINE therefore means
that the metadata and locator are syntactically valid and plausible from those
local records and stable bibliographic knowledge; it does not mean that a
publisher endpoint was resolved during this run. UNVERIFIED-OFFLINE marks
metadata or a locator I cannot independently vouch for without an online check.

The mechanical citation pattern was
\[(\d+(?:\s*(?:,|[-–—])\s*\d+)*)\]; comma lists and inclusive ranges were
expanded. The scan domain was Sections 1–10 plus Appendix A, excluding Section
11 itself. The raw regex also found [0,1] on draft line 221; inspection
classified it as a mathematical interval inside \(...\), not a citation.
There were no numeric citation ranges or lists, and Appendix A contained no
numeric citations. Reference entries were extracted with ^(\d+)\.\s+ between
the Section 11 and Appendix A headings.

DOIs were checked against ^10\.\d{4,9}/\S+$, arXiv identifiers against
^\d{4}\.\d{4,5}$, and URLs for an https:// scheme and nonempty host/path.
All supplied locators passed their applicable syntax check. Plausibility was
then judged offline; no DOI was invented.

## Used/present matrix

Initial counts were 21 unique used keys, 31 present entries, 0 used-but-missing,
and 10 present-but-orphan. After the authorized cleanup the counts are 21, 21,
0, and 0. There were no duplicate or out-of-order entry numbers before or after.
Removing true orphans while preserving every cited number leaves intentional
numbering gaps at 4, 9, 11, 14, 16–18, 21, and 24–25; closing them would require
renumbering frozen body citations and was not done.

| Key | Draft citation line(s) | Occurrences | Initially present | Final present |
|---:|---|---:|---|---|
| 1 | 338 | 1 | yes | yes |
| 2 | 338 | 1 | yes | yes |
| 3 | 336 | 1 | yes | yes |
| 5 | 324 | 2 | yes | yes |
| 6 | 324 | 2 | yes | yes |
| 7 | 332 | 1 | yes | yes |
| 8 | 332 | 1 | yes | yes |
| 10 | 344 | 1 | yes | yes |
| 12 | 344 | 1 | yes | yes |
| 13 | 332 | 1 | yes | yes |
| 15 | 338 | 1 | yes | yes |
| 19 | 332 | 1 | yes | yes |
| 20 | 330 | 1 | yes | yes |
| 22 | 332 | 1 | yes | yes |
| 23 | 326 | 1 | yes | yes |
| 26 | 342 | 1 | yes | yes |
| 27 | 344 | 1 | yes | yes |
| 28 | 344 | 1 | yes | yes |
| 29 | 326 | 1 | yes | yes |
| 30 | 340 | 1 | yes | yes |
| 31 | 340 | 1 | yes | yes |

Initial orphan entries 4, 9, 11, 14, 16, 17, 18, 21, 24, and 25 had no
numeric citation anywhere in the scan domain and were removed. No missing key,
duplicate number, descending number, or pre-cleanup numbering gap was found.

## Per-entry metadata and offline verification

The table inventories all 31 entries present at audit intake, including entries
removed as orphans. “As cited” preserves et al. where the draft did not list
every author.

| Key | Authors | Title | Venue and year | DOI, URL, or persistent identifier | Status / before → after |
|---:|---|---|---|---|---|
| 1 | A. Tschand et al. | MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from μWatts to MWatts for Sustainable AI | HPCA, 2025 | DOI 10.1109/HPCA61900.2025.00092; arXiv 2410.12032 | VERIFIED-OFFLINE |
| 2 | Standard Performance Evaluation Corporation | Power and Performance Benchmark Methodology, V2.3 | SPECpower Committee, n.d. | https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf | VERIFIED-OFFLINE |
| 3 | S. Rivoire; M. A. Shah; P. Ranganathan; C. Kozyrakis | JouleSort: A Balanced Energy-Efficiency Benchmark | ACM SIGMOD, 2007 | DOI 10.1145/1247480.1247522 | FIXED — no locator → known DOI added |
| 4 | D. Economou; S. Rivoire; C. Kozyrakis; P. Ranganathan | Full-System Power Analysis and Modeling for Server Environments | MoBS, 2006 | none supplied | FIXED — present → removed as uncited |
| 5 | K. N. Khan; M. Hirki; T. Niemi; J. K. Nurminen; Z. Ou | RAPL in Action: Experiences in Using RAPL for Power Measurements | ACM TOMPECS 3(2), 2018 | DOI 10.1145/3177754 | VERIFIED-OFFLINE |
| 6 | M. Jay; V. Ostapenco; L. Lefèvre; D. Trystram; A.-C. Orgerie; B. Fichel | An Experimental Comparison of Software-Based Power Meters: Focus on CPU and GPU | IEEE/ACM CCGrid, 2023 | DOI 10.1109/CCGrid57682.2023.00020; HAL hal-04030223 | VERIFIED-OFFLINE |
| 7 | C. Niu; W. Zhang; J. Li; Y. Zhao; T. Wang; X. Wang; Y. Chen | TokenPowerBench: Benchmarking the Power Consumption of LLM Inference | AAAI 40(38), 2026 | arXiv 2512.03024 | VERIFIED-OFFLINE |
| 8 | J.-W. Chung et al. | The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization | NeurIPS Datasets and Benchmarks, 2025 | arXiv 2505.06371 | VERIFIED-OFFLINE |
| 9 | P. Hübner; A. Hu; I. Peng; S. Markidis | Apple vs. Oranges: Evaluating the Apple Silicon M-Series SoCs for HPC Performance and Efficiency | IEEE IPDPSW, 2025 | DOI 10.1109/IPDPSW66978.2025.00013 | FIXED — present → removed as uncited |
| 10 | Z. Li et al. | Prima.cpp: Fast 30-70B LLM Inference on Heterogeneous and Low-Resource Home Clusters | ICLR, 2026 | arXiv 2504.08791 | VERIFIED-OFFLINE |
| 11 | D. Pham; K. Katevas; A. Shahin Shamsabadi; H. Haddadi | AgentStop: Terminating Local AI Agents Early to Save Energy in Consumer Devices | ACM CAIS, 2026 | DOI 10.1145/3786335.3813163; arXiv 2605.15206 | FIXED — present → removed as uncited |
| 12 | O. Basit; Y. Liu; Z. J. Kong; Y. C. Hu | DualScale: Energy-Efficient Disaggregated LLM Serving via Phase-Aware Placement and DVFS | arXiv preprint, 2026 | arXiv 2602.18755 | VERIFIED-OFFLINE |
| 13 | A. Benazir; F. X. Lin | Benchmarking and Characterization of Large Language Model Inference on Apple Silicon | ACM POMACS 9(3), 2025 | DOI 10.1145/3771563 | VERIFIED-OFFLINE; cite-to-claim concern below |
| 14 | N. Kocher; C. Wassermann; L. Hennig; J. Seng; H. Hoos; K. Kersting; M. Lindauer; M. Müller | Guidelines for the Quality Assessment of Energy-Aware NAS Benchmarks | Castanet workshop at CCGrid, 2025 | DOI 10.1109/CCGridW65158.2025.00017 | FIXED — present → removed as uncited |
| 15 | K.-D. Lange | Identifying Shades of Green: The SPECpower Benchmarks | IEEE Computer 42(3), 2009 | DOI 10.1109/MC.2009.84 | VERIFIED-OFFLINE |
| 16 | M. Poess; R. O. Nambiar; K. Vaid; J. M. Stephens; K. Huppler; E. Haines | Energy Benchmarks: A Detailed Analysis | e-Energy, 2010 | DOI 10.1145/1791314.1791336 | FIXED — present → removed as uncited |
| 17 | W. Feng; K. W. Cameron | The Green500 List: Encouraging Sustainable Supercomputing | IEEE Computer 40(12), 2007 | DOI 10.1109/MC.2007.445 | FIXED — present → removed as uncited |
| 18 | S. Rivoire; P. Ranganathan; C. Kozyrakis | A Comparison of High-Level Full-System Power Models | USENIX HotPower, 2008 | none supplied | FIXED — present → removed as uncited |
| 19 | B. Ruf; M. Detyniecki | The Cost of Context: Profiling the Energy Footprint of Input Tokens in Large Language Models | HotCarbon, 2026 | none supplied | UNVERIFIED-OFFLINE |
| 20 | B. Ma; A. Afzal; J. Eitzinger; G. Wellein | The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy Characterisation Across Attention Architectures | arXiv preprint, 2026 | arXiv 2605.11999 | VERIFIED-OFFLINE |
| 21 | A. Javat; A. Kazakov | Silicon Showdown: Performance, Efficiency, and Ecosystem Barriers in Consumer-Grade LLM Inference | arXiv preprint, 2026 | arXiv 2605.00519 | FIXED — present → removed as uncited |
| 22 | J. Saad-Falcon; A. Narayan; et al. | Intelligence per Watt: Measuring Intelligence Efficiency of Local AI | arXiv preprint, 2025 | arXiv 2511.07885 | VERIFIED-OFFLINE |
| 23 | M. Dauner; M. Steinberg; A. Brunnert; B. Schicker; B. Zönnchen | Evaluating the Influence of Measurement Frequency on Energy Readings Using Intel RAPL and NVIDIA NVML | HotCarbon, 2026 | none supplied | UNVERIFIED-OFFLINE |
| 24 | Q. Cao; A. Balasubramanian; N. Balasubramanian | Towards Accurate and Reliable Energy Measurement of NLP Models | SustaiNLP at EMNLP, 2020 | DOI 10.18653/v1/2020.sustainlp-1.19 | FIXED — present → removed as uncited |
| 25 | D. Panigrahy; A. Tyagi | The Energy Blind Spot: NVIDIA's Flagship Edge AI Hardware Cannot Support Process-Level Energy Attribution | LOCO, 2026 | arXiv 2605.27599 | FIXED — present → removed as uncited |
| 26 | Z. Zhuang; Y. Li; Z. Fan | Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bit Quantization Benchmarks, with a Pilot Audit | arXiv preprint, 2026 | arXiv 2605.28873 | VERIFIED-OFFLINE |
| 27 | J. Li; Y. Zhu; B. Chen; E. K. Lee; K. Nahrstedt | Revisiting Disaggregated Large Language Model Serving for Performance and Energy Implications | EuroMLSys, 2026 | DOI 10.1145/3805621.3807662; arXiv 2601.08833 | FIXED — arXiv; DOI → consistent DOI; arXiv order |
| 28 | Y. Guo; S. Joshi | SplitZip: Ultra Fast Lossless KV Compression for Disaggregated LLM Serving | arXiv preprint, 2026 | arXiv 2605.01708 | VERIFIED-OFFLINE |
| 29 | M. Hähnel; B. Döbel; M. Völp; H. Härtig | Measuring energy consumption for short code paths using RAPL | ACM SIGMETRICS Performance Evaluation Review 40(3), 2012 | DOI 10.1145/2425248.2425252 | VERIFIED-OFFLINE |
| 30 | A. Georges; D. Buytaert; L. Eeckhout | Statistically Rigorous Java Performance Evaluation | OOPSLA, 2007 | DOI 10.1145/1297027.1297033 | VERIFIED-OFFLINE |
| 31 | T. Mytkowicz; A. Diwan; M. Hauswirth; P. F. Sweeney | Producing Wrong Data Without Doing Anything Obviously Wrong! | ASPLOS XIV, 2009 | DOI 10.1145/1508244.1508275 | VERIFIED-OFFLINE |

## Cite-to-claim fit

- Concern — [13], draft line 332. The sentence groups Benazir and Lin
  with works that “map energy across useful deployed configurations.” The local
  2026-08-10 paper-session report says this Apple-silicon characterization
  reports no energy. The citation therefore appears mis-attached to the energy
  claim. The body is frozen, so this audit reports rather than edits it.
- Offline confidence gaps, not established misattachments — [19] and [23].
  The detailed [19] claim (one-token prefill isolation, decode by subtraction,
  one run per context length, no error bars) and [23] claim (polling-frequency
  dependence and the severe-underestimate example) are plausible and match
  local notes, but I cannot independently vouch for them offline.
- No other cite-to-claim mismatch was found in the 23 numeric citation
  occurrences. That is an offline judgment, not a fresh source-resolution pass.

## Director online-resolution list

1. Resolve an official proceedings page, DOI/URL, author/title metadata, and
   the method claims for [19].
2. Resolve HotCarbon acceptance/proceedings metadata and an official DOI/URL
   for [23], then confirm the polling-frequency claim against the paper.
3. At the next body-authorized paper round, correct or replace [13] at line 332;
   no body edit is authorized in this bibliography unit.

## Required ruling checks

- [29] Hähnel is present and cited; title, 2012 venue, and DOI
  10.1145/2425248.2425252 are plausible and syntactically valid offline.
- [30] Georges is present and cited with DOI 10.1145/1297027.1297033.
- [31] Mytkowicz is present and cited with DOI 10.1145/1508244.1508275.
- Case-insensitive whole-draft search found no Hackenberg entry, citation, or
  prose mention.
