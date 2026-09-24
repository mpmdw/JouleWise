ROLE: implementation seat for JouleWise lane A295 (KIND-TABLE-WINDOW-MUTANT-TEST-01). Test-only lane. Execution seat and design peer; the magistrate reviews. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["tests/test_night_kinds.py"]

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a295, branch test/2026-09-24-a295-window-mutant at origin/main bd80d169. Do not commit. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise (the canonical checkout). Authority: docs/process_traces/2026-09-23-activation-d8cc9c0a/43-a280-pra-fable-final-pass.md §Q2 F1 (read it first: the executed committed-mutant probe and its exact fixture shape) and TASK_QUEUE.md row A295.

1. PROBLEM. A cold final pass proved, with a temporary committed mutant, that a night-kind table row with the wrong measurement window (window_max_s=8999 instead of the frozen-protocol 9000) cannot arm an idle night through the real prepare path. That probe is not a repository test. The existing test near tests/test_night_kinds.py:343 patches the table in-process; it does not commit a mutant into the base archive the real prepare path reads.

2. CLAUSES:
   C1. Add one named test (for example `test_committed_window_mutant_refused_by_real_prepare`) that, in a hermetic bare-clone test root built exactly the way the module's existing fixtures build theirs (census-clean temp root, never-run `claude` courier stub on PATH, `tests.git_fixture.init_git_fixture` for any git init; reuse the module helpers, do not duplicate them): commits a `joulewise/night_kinds.py` whose idle row has `window_max_s=8999`, `update-ref`s main to that commit, calls the REAL prepare path with that head, and asserts the frozen-protocol refusal (assert the refusal class and the stable part of its message exactly as record 43 reports it).
   C2. A companion assertion or test shows the same fixture with the unmodified row (9000) is NOT refused for the window reason, so the test is not vacuous.
   C3. Guard-deletion proof: temporarily remove the production refusal guard in your sandbox copy, show the new test fails, restore it (report the file:line of the guard; do not leave it edited, it is outside WRITE_SCOPE).

3. ACCEPTANCE: `python3 -B -m unittest tests.test_night_kinds tests.test_git_fixture_maintenance`. NEVER `unittest discover` or scripts/shard_tests.py. `git diff bd80d169 --stat` lists only tests/test_night_kinds.py. End your turn only after the named acceptance has run.

4. EVIDENCE DEMANDED (markdown body): C1-C3 mapped to test names and file:line; the guard-deletion result; the test command with its result tail; "what the magistrate should double-check". Implementation-genre verdict keys only; JSON header under 8 KB.
