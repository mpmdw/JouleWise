ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["docs/paper/results-fill-registry.md", "scripts/check_paper_round7_artifacts.py", "tests/test_paper_round7_artifacts.py", "docs/paper/round7/fill-checklist.md"]

# DX registry rows + round-7 artifact fence (ruling 168a)

Checkout: `/Users/edr/code/JouleWise-wt-dx` (branch `feat/2026-09-02-dx-registry`
at `a63d45bd`). Edit ONLY the four WRITE_SCOPE paths. Do not commit, stash,
checkout, or push. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`; named test modules only,
never canonical `unittest discover`. `docs/paper/draft-v1.md` is byte-frozen;
`scripts/check_paper_replay_fence.py` and `tests/test_paper_replay_fence.py`
are NOT in scope — read them as the pattern to mirror. Retained corpora under
`runs*/` are immutable (read-only for the replay half).

The ruling below is binding verbatim. Read first: the ruling, then the three
consult reports it synthesizes
(`scratchpad/out/168-sol-registry-consult.md`, `168-opus-…`, `168-fable-…`
— they contain the field-path and row-shape detail), then the registry's
own rules (`docs/paper/results-fill-registry.md:1-140`, the diagnostic-era
section `:540-722`) and `docs/paper/round7/fill-checklist.md`.

# Ruling 168a — registry door for the round-7 desk analyses

Magistrate: Fable, 2026-09-02 04:10. Three seats (Sol xhigh `out/168-sol-…`,
Opus `out/168-opus-…`, blind Fable `out/168-fable-…`) all returned OPTION A;
the magistrate's lean stands. Divergences synthesized below (not majority-voted).

R-168-1 (door). Every round-7 number enters the successor draft ONLY as
`[FILL:DX-nnn]` naming a row in `docs/paper/results-fill-registry.md`. The
rows live in a NEW subsection after DG-128, inside "Diagnostic-era value
custody": `#### Successor-draft desk analyses (round 7) — DX rows`. Prefix
`DX-`, never `DG-` (the DG census is closed against draft-v1's 101 sites).
DX rows carry values, never `[PENDING`, so the item-38 census greps are
unchanged.

R-168-2 (sources block, exact as the registry's `:548-567` style):
`XD` = docs/paper/round7/excursion-decomposition.json,
  sha256 21618026dfc677165b2a1acd511ff0d3130bd3837fa344c9ca9fbac95d7e058b (33,765 B),
  schema joulewise-excursion-decomposition/v1;
`XS` = scripts/paper_excursion_decomposition.py,
  sha256 8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b (49b258d2, #240);
`F4` = docs/paper/figures/fig4_edge_excursions.svg,
  sha256 6ac9d5c7a84ac1bb8d3c0da036449f77e0e5d2d36564dfc33a1c2812912782cf;
`AQ` = docs/paper/round7/anchor-correction-quantified.json,
  sha256 c09077149c66411d1873838de5c21aa1b7c97d8df24ea66a163d679cb31f50fc (54,280 B);
`AS` = scripts/paper_anchor_correction_quantified.py,
  sha256 41cbbf08176f9bfe1c6cfd526e1776f0324893c62f62cd76d1ff8128b8beb47f (0438566b, #242);
`R7F` = scripts/check_paper_round7_artifacts.py (new; R-168-5).
The implementation seat RECOMPUTES every digest and refuses to proceed on
any mismatch with the values above (they were computed by two seats
independently at a63d45bd).

R-168-3 (row ids, FIXED now so prose seats can cite them):
DX-001 XD artifact identity (digest row; no draft site);
DX-002 AQ artifact identity (digest row);
DX-003 F4 figure identity — binds F4 sha + XD sha + the FULL replay command
  including `--svg` (the JSON's own `replay_command` omits `--svg`; record
  that discrepancy in the row; no re-issue of XD in this round);
DX-010 onset best-fit lag median `XD#summary.onset_best_fit_lag.median_ms` = 13.0 → "+13.0 ms";
DX-011 offset best-fit lag median `…offset_best_fit_lag.median_ms` = −5.5 → "−5.5 ms";
DX-012 onset positive count 59 of 59 (`…onset_best_fit_lag` count fields — name the exact fields);
DX-013 offset negative count 49 of 59;
DX-014 onset MAD `…onset_best_fit_lag.median_absolute_deviation_ms` = 2.5 ms;
DX-015 offset MAD = 4.0 ms;
DX-016 bias share DERIVE: 13.0 / `XD#bound_terms.b_fiducial_ms` (30.067932) = 43.2 % (round 1);
DX-017 worst-pulse excess DERIVE: `onset_best_fit_lag.max_ms − median_ms` = 27.0 − 13.0 = 14.0 ms;
DX-020 `AQ#summary.population_size` = 15;
DX-021 `AQ#summary.v3_derived_count` = 12 / `v3_refused_count` = 3 (all `anchor_unresolved`);
DX-022 `AQ#summary.admissibility_flip_count` = 2 (both `refused_by_v3`);
DX-023 `AQ#summary.control_v2_reproduces_stored_count` = 14 of 15, failure `20260722T213749-563b9849`;
DX-024 `AQ#summary.delta_v3_vs_stored_absolute.median_ms` = 0.154318 → render per row rule;
DX-025 `…delta_v3_vs_stored_absolute.max_absolute_ms` = 1.090519;
DX-026 `…delta_v3_vs_stored_relative.max_absolute_pct` = 4.046812 → "4.05 %";
DX-027 `…delta_v3_vs_stored_relative.median_abs_pct` (exact field name per AQ) = 0.607832 → "0.61 %"
  (Sol F4: the MD's "well under half a percent" is WRONG against its own table; never copy it).
Each row: seven registry columns; fill rule MEASURED (DERIVE for 016/017);
supplier = field path + parent digest row; rendering rule explicit
(sign, decimals); Campaign/cell = "retained 20260722 capture / 59-pulse
calibration" (XD rows) or "15 retained instrument_validation captures, v2
era" (AQ rows). The seat verifies every value by reading the JSON; a value
above that the JSON does not carry is a REFUSAL, not an approximation.

R-168-4 (freeze label — Fable amendment adopted). `REPLAY_FENCED` is
reserved for RF (`check_paper_replay_fence.py`, Section 2 of draft-v1);
DX rows are NOT RF-fenced. Label: `DIAGNOSTIC_ERA / R7_FENCED; NOT
RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY`, with `R7_FENCED`
defined in the subsection header as "digest- and field-checked in CI by
R7F; byte-identical replay when the retained corpus is present".

R-168-5 (fence shape — Opus/Fable adopted over Sol's RF extension; RF and
its 43 stay untouched). New `scripts/check_paper_round7_artifacts.py` +
`tests/test_paper_round7_artifacts.py`, mirroring `test_paper_replay_fence.py`'s
two halves: DIGEST half (always on): sha256 of XD, AQ, F4, XS, AS equal the
registry-pinned values (parsed from the registry rows, not duplicated in
the test); every DX supplier field path resolves in its JSON; every
`[FILL:DX-nnn]` literal present in `docs/paper/draft-v2-skeleton.md` (if
any yet) equals the field value under the row's rendering rule; XD/AQ gate
booleans true (`calibration_gate.*_matches_exactly`,
`worked_capture_gate.matches_exactly`); F4 mark inversion per
`fig4-verification.md:41-43` for the 118 marks. REPLAY half
(`skipUnless` corpus present; exit 3 on absence — never a pass): re-run XS
and AS to TMPDIR and require byte identity with XD/AQ. Refusal tests:
altered literal, altered field, altered digest, missing JSON.

R-168-6 (prose standing — mandatory wherever a DX value is printed).
Opening sentence names the artifact class: "diagnostic-era instrument
statistics — a desk re-derivation (XS over XD; AS over AQ) over retained
captures whose energy values D-078 voids for claim use; they characterise
the timing calibration of the instrument and are not evidence for any
`_v5` result." Must also say: values were re-derived under the CURRENT
claim-bearing v3 anchor (`XD#anchor_method` = `powermetrics_native_second_rate_aware_set_membership_v1`)
and re-deriving a historical corpus under the current method does not make
it a supplier for a claim; one capture, 59/118 values, sample statistics
with no coverage/independence claim (keep skeleton:1137 verbatim); anchor
deltas are over the 12 captures v3 derived, with the 3 refusals and the 1
control failure in the same sentence; floor ratios NOT recomputed. The word
"repeatably" is DELETED everywhere it describes these numbers — print the
counts (DX-012/013) instead. D-119 wording on the figure caption.

R-168-7 (checklist). `docs/paper/round7/fill-checklist.md` is not parked;
its placement regex/expected-id list gains `DX`; the "43" census sentence
is left as RF's number with one added sentence naming R7F's separate
census. No other round-7 sheet is touched.

R-168-8 (sequencing). Registry + fence land as ONE branch/PR
(`feat/2026-09-02-dx-registry`) before any prose cites a DX row; the
WEAVE-EXCURSION / WEAVE-ANCHOR prose seat runs after paper-b (terra 165)
lands and cites the ids above; the R7F literal check then bites.

## Implementation notes

- Row values: READ every value from the JSON with python and paste the read
  value; if a named field does not exist under the name given in the ruling,
  find the exact field carrying that quantity, use its real path, and list
  the substitution in your report. If the quantity does not exist in the
  JSON at all, OMIT the row and report it — never approximate.
- The test parses the registry markdown to obtain the pinned digests and the
  DX row table (one parser, fail-closed on malformed rows), so the registry
  is the ONE home; the test file duplicates no digest.
- R7F CLI: `--literals-only` (digest half only) and default (both halves;
  exit 3 when the corpus is absent, printing which path). Print
  `R7F COMPARED n / MISMATCHES m` on the last line.
- Figure check: read `docs/paper/figures/fig4-verification.md:33-51` for the
  documented axis mapping and invert it for the 118 marks, comparing to XD's
  per-edge series with a tolerance you justify from the SVG's coordinate
  precision (state it in the test docstring).
- `fill-checklist.md`: minimal edit per R-168-7 only.

## Verification (executed; tails in report)

1. `python -m unittest tests.test_paper_round7_artifacts` → OK, count.
2. `python scripts/check_paper_round7_artifacts.py --literals-only` → last line.
3. `python scripts/check_paper_round7_artifacts.py` → either both halves
   pass or exit 3 naming the missing corpus path (report which).
4. Mutation: in a scratch copy of the registry change one hex digit of the
   XD digest → the test FAILS (tail); change `13.0` in a DX row → FAILS.
5. `python -m unittest tests.test_paper_replay_fence tests.test_docs_freshness` → still OK.
6. `git status --porcelain` shows only the four WRITE_SCOPE paths.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`), then
under 100 lines: the DX row table as landed (ids, values, field paths), any
field-name substitutions or omitted rows, digests recomputed (commands), the
mutation tails, test counts.
