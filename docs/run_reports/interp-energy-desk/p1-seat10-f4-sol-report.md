Committed locally as `060bd10e5` on `docs/2026-11-11-paper1-f4`. Working tree is clean; nothing pushed.

- Restored all four definition groups verbatim, updated eight headings, and cut the duplicate §3.4 label.
- Changed only `paper1.md`, the outline map, fill index and [run report](/Volumes/JW-EXT/jw-wt/sol-p1-seat10-f4/docs/run_reports/2026-11-11-p1-seat10-f4.md).
- Identity checks against `62a87aaad` passed with only mapped differences. Fill index: `234 213 217 173`.
- `python3.13 -B -m unittest tests.test_paper_build`: OK, 5 tests, 2 skipped.
- Markdown lint on all four files and `git diff --check`: passed.

§1.2 and §8 remain unchanged. The disclosure clause is recorded as owed because the required sentence is absent. No blockers remain; HTML rendering is unverified because the optional parser is missing. No full suite, network or measurement-data access was used.