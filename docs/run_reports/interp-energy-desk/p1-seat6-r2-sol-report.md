Applied R-1–R-4 and both prior-report fixes on `p1-seat6-r2`. FACT comments retained.

Changed eight files: manuscript, two builders, their generated outputs, two prior reports, and the [round-2 report](/Volumes/JW-EXT/jw-wt/sol-p1-seat6-r2/docs/run_reports/2026-11-10-p1-seat6-r2.md).

Local commits:

- `811a05b69` — corrections
- `9fba30947` — verification and handoff

Verification:

- `python3.13 -B -m unittest tests.test_paper_build`: passed; 5 tests, 2 optional renderer skips.
- Both generators completed and reproduce byte-identical output.
- `fill_index.md` changes exactly one line.
- Markdown lint and `git diff --check` passed.

Working tree clean; nothing pushed this round. No blockers. Rendering/visual QA remains unverified; R-5 stays with seat 9. Ready for research-lead review.