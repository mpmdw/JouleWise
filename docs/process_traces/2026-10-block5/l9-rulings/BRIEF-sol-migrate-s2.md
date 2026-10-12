SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/b5_analysis/fixtures_s2.py", "tests/b5_analysis/test_bracket.py", "joulewise/b5_analysis/bracket.py", ".scratch-migrate/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 75 minutes of wall time; write the report by minute 65 whatever is unfinished.** `tests.b5_analysis.test_bracket` takes about 8 minutes in full: run it in full once at the end, single tests before that. Do not run `test_fixture_shapes` or `test_kept_units` (another seat is migrating them in another worktree).

# Lane L9: migrate stage S2 to to stage S0's tightened readers

You work in `/Users/edr/code/JouleWise-wt-l9-s2` (branch `lane/2026-10-12-l9-s2`, which now contains the lane head `83c1e0f1c`,
clean). A fix round tightened `joulewise/b5_analysis/{windows,archive}.py`: the index's pack label is bound
to the plan id and a pack table; a pack's attempts must be 1 to n; an attempt's authenticated documents must
agree with each other; `open_archive` accepts only a window that `select_analysed_attempts` produced. Stage S2's two test files (`fixtures_s2.py`, `test_bracket.py`) were written before that round and may build
synthetic windows the old way. The same section describes the pattern for three other files: read the section "NEEDS_SCOPE — preserved callers" of
`/Users/edr/night-archive/b5-consults/l9-rulings/s0/sol-s0fix-full-report.md`, and
`tests/b5_analysis/fixtures.py` for the helpers it added (`PACK_TABLE`, `selected_window`).

Rules:

- `joulewise/b5_analysis/bracket.py` is in scope only for a call that must pass the new reader arguments (for
  example `pack_table`) through; no check in it may be weakened or removed. Everything else under `joulewise/**`
  and `tests/b5_analysis/fixtures.py` are out of scope. If a
  test cannot be migrated without changing them, do not weaken the test: report the exact change needed.
- Every existing test keeps its meaning. A test whose input is now refused earlier by a new guard either
  (a) builds a coherent input that reaches the guard it was written for, or (b) if no coherent input can
  reach that guard any more, is kept as a test of the downstream guard through a deliberate, named test
  double at that guard, with a comment saying which upstream guard makes it unreachable. Never delete a test,
  and never change an expected refusal code to make a test pass without saying so in the report.
- For each test you change, the report says: what changed, and whether the guard it covers is still killed
  by removing it (re-run the mutation for at least every test of kind (b)).
- Interpreter `/opt/homebrew/bin/python3.13`, `PYTHONDONTWRITEBYTECODE=1`, a `TMPDIR` without "claude" or
  "codex" in its path.
- Blinding (binding): do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root under
  `/Users/edr/night-custody/measurement/`. Synthetic fixtures only.

Report: per file, the tests changed and how; the final full result of `tests.b5_analysis.test_bracket` (first run it once as it stands to see what fails); anything that needs a
change outside your scope.
