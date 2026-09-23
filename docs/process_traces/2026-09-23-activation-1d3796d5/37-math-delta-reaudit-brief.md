ROLE: delta re-audit seat for the JouleWise MATH importer fix round 1. Fix rounds introduce defects; find them. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Detached worktree at candidate head ed1c8205 (branch feat/2026-09-23-math-importer). Delta under audit: `git diff 47ea644d..ed1c8205`; lane base main 313efcca. Pinned source files (read-only): /Users/edr/jw_data/math-prm800k-7ecc7947/. Scratch only under $TMPDIR or /tmp. Never run launchctl, sudo, networksetup; never load a model; never touch /Users/edr/night-custody.

1. The fix contract is /Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/32-math-fix1-seat-brief.md (Y1-Y10); the findings it closes are 28-math-sol-refuter.md and 29-math-opus-contract-lens.md; the seat's report is 33-math-fix1-seat-report.md (same directory).

2. QUESTIONS (executed evidence each): (a) Is each Y1-Y10 closed at the production call site? (b) Y2: prove with your own scorer-only change that the eligible population and all three set hashes do not move; and prove the reference parser and the response scorer agree on every eligible reference (4,040/4,040). (c) Y5: can the new denials make a CORRECT response score incorrect for any eligible reference (e.g. a reference that itself carries \% or a unit word)? Run all 4,040 references through the scorer with their own reference text as the response. (d) Recompute the three new set hashes independently. (e) SAME-SIGNATURE STATEMENT (mandatory): is any finding the same defect class as a round-1 finding (unauthenticated receipt; scorer/eligibility coupling; prompt-shape laxity; surviving scorer mutant)? yes/no per class. (f) 5 mutants of your own on the delta. Named modules ONLY: `python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite`; NEVER `unittest discover` or scripts/shard_tests.py.

3. OUTPUT: review-genre envelope, verdict = {counts, findings} only, JSON header under 8 KB; body with each answer, the same-signature statement and findings (blocker/should_fix/nit) with executed counterexamples. Timebox 40 minutes.
