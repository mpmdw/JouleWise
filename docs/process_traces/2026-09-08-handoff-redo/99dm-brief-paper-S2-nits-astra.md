WRITE_SCOPE: ["docs/contracts/paper_supply_custody.md","joulewise/paper_rendering.py","joulewise/paper_reported_energy.py","docs/contracts/paper_reported_energy.md","tests/test_paper_rendering.py","tests/test_paper_reported_energy.py"]

# Paper S2 — closing nits from the Opus delta (gpt-6-astra, medium, genre implementation)
Head e5eb5b8d on feat/2026-09-08-paper-S2. The Opus delta at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dl-delta-paper-S2-fix-opus-review.md passed
F1–F12 and named N1–N5. Cure N1, N2, N4, N5 exactly (N3 is magistrate-owned):
N1 (should-fix) docs/contracts/paper_supply_custody.md ~:411–412: amend the exhaustive sentence to "Every custody-seam
   and renderer-guard failure is `PaperCustodyRefusal` with a code from the closed `paper_custody_*` set; a
   reported-energy renderer body may additionally raise the closed `paper_reported_energy_*` vocabulary of D-179, also
   with empty `rendered_output`." (verify the surrounding paragraph still reads true).
N2 joulewise/paper_rendering.py ~:36–46: give `_field` a sentinel default and raise
   `paper_reported_energy_projection_mismatch` (add the code to the closed vocabulary + contract table) when a
   non-None projection lacks `cells` — never StopIteration; regression.
N4 docs/contracts/paper_reported_energy.md ~:34–36: drop the lane-local commit pin (or mark it informative) and WIRE
   the ordering-fence call at gate registration in paper_reported_energy.py so "the gate must call this check" is code,
   not prose; regression that registration without the fence check refuses.
N5 joulewise/paper_reported_energy.py ~:302–306: move the `prompt <= 0` check above the agreement check so a
   nonpositive denominator refuses `_denominator_invalid` as the contract :117–118 states; regression.
Acceptance (rc-gated to a log): tests.test_paper_reported_energy tests.test_paper_rendering tests.test_paper_custody
tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report before/after per item.
