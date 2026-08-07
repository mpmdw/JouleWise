# Bibliography and novelty audit — draft-v1 (2026-08-07, Fable subagent, web-verified)

Closes round-1 flag G1. All 13 citation keys resolve to real, correctly
identified works. 12/13 characterizations verified accurate. ONE factual
error found (F-BIB-1 below). The §2 novelty claim STANDS as worded.

## Verdicts per key (full metadata in §2)

- **[MLPerfPower]** arXiv:2410.12032 (Tschand et al. 2024/25) — MOSTLY
  ACCURATE; "uncertainty at observed load", "invalid-sample accounting",
  and battery treatment trace to the SPEC Power and Performance
  Methodology, not the arXiv paper → split the citation (add SPEC ref).
- **[RAPLInAction]** Khan, Hirki, Niemi, Nurminen, Ou; ACM TOMPECS 3(2),
  2018, DOI 10.1145/3177754 — ACCURATE.
- **[JayOstapenco]** Jay, Ostapenco, Lefèvre, Trystram, Orgerie, Fichel;
  IEEE/ACM CCGrid 2023, HAL hal-04030223 — ACCURATE (six authors; get
  IEEE DOI).
- **[TokenPowerBench]** Niu et al.; AAAI-40 (2026) 40(38):32582–32590;
  arXiv:2512.03024 — ACCURATE incl. the negative claims; "phase-
  appropriate token denominators" not confirmed verbatim; CSL entry
  stale (says arXiv/2025 — update to AAAI record).
- **[MLENERGY]** Chung et al.; NeurIPS 2025 D&B Spotlight;
  arXiv:2505.06371 — ACCURATE (breadth citation).
- **[SiliconShowdown]** Javat, Kazakov; arXiv:2605.00519 (preprint) —
  ACCURATE.
- **[IntelligencePerWatt]** Saad-Falcon, Narayan, et al.;
  arXiv:2511.07885 (v4 May 2026, preprint) — ACCURATE.
- **[IllusionPowerCapping]** Ma, Afzal, Eitzinger, Wellein;
  arXiv:2605.11999 (preprint) — ACCURATE, best-verified key (every §8
  sub-claim confirmed verbatim).
- **[PairedMDE]** Zhuang, Li, Fan; arXiv:2605.28873 (preprint) —
  ACCURATE; note its domain is quantization ACCURACY benchmarking, not
  energy.
- **[RevisitingDisaggregationEnergy]** Li, Zhu, [Chen?], Lee, Nahrstedt;
  EuroMLSys '26 pp.397–406, DOI 10.1145/3805621.3807662;
  arXiv:2601.08833 — **F-BIB-1, INACCURATE in draft §8:** the draft
  attributes load/baseline/transfer dependence to the ENERGY outcome;
  the paper says the PERFORMANCE benefits depend on those, while
  disaggregation's energy is essentially unconditionally higher.
  `related_work_draft.md:31` has the correct wording. Author count
  discrepancy (4 on arXiv vs 5 in CSL/ACM) — confirm.
- **[DualScale]** Basit, Liu, Kong, Hu; arXiv:2602.18755 (preprint) —
  ACCURATE.
- **[PrimaCPP]** Li et al. (11 authors); ICLR 2026 poster (OpenReview
  h0LjpOG1jq); arXiv:2504.08791 — ACCURATE; appendix A.13 energy metric
  detail rests on the internal RPT-002 read (bench-verify before
  submission).
- **[SplitZip]** Guo, Joshi; arXiv:2605.01708 (preprint) — ACCURATE.

## Novelty claim (§2)

The three-leg conjunction (phase-resolved LLM energy on consumer
silicon + per-measurement error budget + powermetrics timing-attribution
validation) — **nothing found combines even two legs; no published
powermetrics validation study of any kind exists** through 2026-08.
Nearest neighbors, ranked: TokenPowerBench (AAAI-40, no error budget /
no validation), the apple-silicon-llm-bench "yardstick" GitHub artifact
(not a paper), Illusion of Power Capping (rigor neighbor, datacenter,
uncomposed error terms), ML.ENERGY's Mac blog + zeus-apple-silicon (no
phase split / uncertainty / validation). Optional defensive citations:
Apple vs. Oranges (arXiv:2502.05317 — powermetrics used-but-uncalibrated
in practice), energy-aware NAS benchmark guidelines (arXiv:2505.15631 —
counter-vs-meter discrepancies).

## Pre-submission double-checks (queued)

1. F-BIB-1 §8 sentence fix (this round). 2. TokenPowerBench CSL → AAAI.
3. Split [MLPerfPower]/SPEC. 4. Revisiting author list (Bo Chen?).
5. prima.cpp A.13 bench-verify. 6. JayOstapenco IEEE DOI + 6 authors.
7. Re-check the six arXiv-only preprints for venue acceptances before
submission. 8. Consider the defensive citations.
