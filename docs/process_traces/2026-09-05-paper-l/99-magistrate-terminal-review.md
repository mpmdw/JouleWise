# Paper-L — magistrate terminal review (apex read)

Read: Appendix A.7 Figure A1 caption in full (every visual element named: R1–R10 rectangles, blue/orange
membership, purple window segment and dashed edges, axes; the [8, 10] J and [8.8, 9.2] J arithmetic is
replicable from the caption's words alone, which delta 02 re-derived independently), the Introduction citation
sentence, the PE-01 registry row (DERIVE, pinned producer digest and size, unique appendix marker, SYNTHETIC
placement), the registry-integration merges (paper-K rows kept; enclosure row added; D-166 rows kept), and the
seat/delta reports 01–05 (delta 05 CLEAN: checker validates the pin; renderer refuses to render PE-01 into
Results; 107 tests; corrupt pins rejected; mutation killed).

Design-level questions. (1) Is the enclosure delivered as ruling 43 Q-17-1 requires — a pinned desk script, one
DERIVE row, appendix figure, reported and never composed into any bound? Yes; the figure says SYNTHETIC on its
face and the caption states the diagnostic scope. (2) Does the production path now know the row? Yes: the
round-7 checker validates PE-01's digest and placement and the Results renderer treats DERIVE rows as
non-Results (StopFill known, never rendered). (3) Frozen bytes: joulewise/, goldens and contracts byte-identical
to main (enclosure branch invariant carried over). (4) Registry conflicts with paper-K were authored, not
side-picked (K's OB/TR/OR rows kept; D-166's more specific rows kept). (5) Overbuild: none.

Residual carried: draft line ~1738 (ledger vocabulary "timing error common to") is a physical-timing survivor
found by the D-165 census; it is a paper-side one-row cure queued for the next paper round.

Verdict: LANDABLE, stacked on paper-K (#288). Full-suite replay on the merged head before merge.

## Addendum 2026-09-05 — post-review commits through 3f391094 (magistrate, this session)

Read and bench-verified: the merges of origin/main (paper-K, seam, F+B context), the D-166 identity-set
regression diagnosis (astra chose to keep the intended singleton A/decode identity and repair the synthetic
fixture; report 06), the Opus delta (report 07: option (b) confirmed, S1 coverage loss), and the singleton
production-path test (report 08). At my bench: FrozenConsumerIdentitySetTests 14 OK, test_analysis_inputs 20
OK, test_d117_contrast_v5_pack 44 OK. CI green at 3f391094; full replay recorded in file 07. Merge candidate:
3f391094 plus this record. Verdict: LANDABLE.
