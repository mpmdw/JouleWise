SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/b5_analysis/test_fixture_shapes.py", "tests/b5_analysis/fixtures_s1.py", "tests/b5_analysis/test_kept_units.py", ".scratch-migrate/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 75 minutes of wall time; write the report by minute 65 whatever is unfinished.** `tests.b5_analysis.test_fixture_shapes` takes about 25 minutes in full and `test_kept_units` about 4: run each in full once at the end, single tests before that.

# Lane L9: migrate three test files to stage S0's tightened readers

You work in `/Users/edr/code/JouleWise-wt-l9` (branch `lane/2026-10-07-l9-analysis`, head `83c1e0f1c`,
clean). A fix round tightened `joulewise/b5_analysis/{windows,archive}.py`: the index's pack label is bound
to the plan id and a pack table; a pack's attempts must be 1 to n; an attempt's authenticated documents must
agree with each other; `open_archive` accepts only a window that `select_analysed_attempts` produced. Three
test files still build synthetic windows the old way and now refuse early. That round's report says exactly
what each needs: read the section "NEEDS_SCOPE — preserved callers" of
`/Users/edr/night-archive/b5-consults/l9-rulings/s0/sol-s0fix-full-report.md`, and
`tests/b5_analysis/fixtures.py` for the helpers it added (`PACK_TABLE`, `selected_window`).

Rules:

- Production code is not yours: `joulewise/**` and `tests/b5_analysis/fixtures.py` are out of scope. If a
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

Report: per file, the tests changed and how; the final full results of both modules; anything that needs a
change outside your scope.
