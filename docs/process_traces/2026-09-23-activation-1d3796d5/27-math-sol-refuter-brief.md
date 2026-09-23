ROLE: refuter seat (execution lens) for the JouleWise MATH importer. Break it; do not confirm it. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Detached worktree at candidate head 47ea644d (branch feat/2026-09-23-math-importer; base main 313efcca). Scratch only under $TMPDIR or /tmp; never write in the repo. Pinned source files (read-only): /Users/edr/jw_data/math-prm800k-7ecc7947/. Never run launchctl, sudo, networksetup; never load a model; never touch /Users/edr/night-custody.

1. SPEC: brief /Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/20-math-importer-seat-brief.md (C1-C8). Diff: `git diff 313efcca..HEAD`.

2. LENS: EXECUTION. (a) Mutation: in a /tmp copy, apply one mutant at a time to joulewise/benchmark_import_math.py and joulewise/suite.py and run `python3 -B -m unittest tests.test_benchmark_import_math tests.test_suite`: skip each receipt check; include one row of the duplicated id; drop the plain-comma exclusion; swap the pilot/test domain strings; drop subject interleaving; let a capped attempt with a parseable box score correct; drop the </think> requirement in thinking mode; compare floats instead of Fractions; take the first box instead of the last; each normalization step removed one at a time; collapse every min/max/comparison to each operand; serialize source_files when empty. Report killed/SURVIVED with the killing test. (b) Scorer fuzz: generate at least 200 response strings from each eligible reference (equivalent forms and near-miss wrong forms) and report any wrong-scored-correct case. (c) Recompute the population table and the three set hashes from the raw files with your own script. Named modules ONLY; NEVER run `unittest discover` or scripts/shard_tests.py.

3. OUTPUT: review-genre envelope, verdict = {counts, findings} only, JSON header under 8 KB; body carries the mutant table, the fuzz summary, the recomputation, and each finding with severity blocker/should_fix/nit and an executed counterexample. Timebox 45 minutes.
