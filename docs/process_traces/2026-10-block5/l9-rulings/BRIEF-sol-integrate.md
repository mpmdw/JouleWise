SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["configs/gates/hazard_refusals.json", "tests/test_battery_float_sweep.py", "configs/pins/**", ".scratch-integrate/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 60 minutes of wall time; write the report by minute 50 whatever is unfinished.** Run only the three test modules named below (each takes seconds), not the whole suite.

# Lane L9: three whole-suite failures that the lane's base merge caused

You work in `/Users/edr/code/JouleWise-wt-l9` (branch `lane/2026-10-07-l9-analysis`, head `b857cef2f`, clean).
The lane's first commit merged the pinned harvest program (`b039c0257`, an unmerged harvest lane) into main's
tree, on the lead's decision: collection of the measurement block is closed, the measurement clone and the
harvest desk root are separate checkouts that this lane never touches, and the analysis must call code that
exists only on the harvest lane. The lead ran the whole suite on the lane (logs:
`/Users/edr/night-archive/b5-consults/l9-rulings/suite/shard{1..6}.log`). Three failures are consequences of
that merge and of the new package `joulewise/b5_analysis/`. Fix each at its cause; do not silence a check.

1. `tests.hazards.test_refusal_allowlist` (`shard5.log`): two unlisted refusal sites in
   `joulewise/calibration_bracketing.py` (`ValueError|invalid calibration trigger_scope`, in
   `evaluate_calibration_bracket` and `calibration_bracket_for_bundles`). They arrived with the harvest lane.
   Add their entries to `configs/gates/hazard_refusals.json` in the file's own format, classified by what the
   site is (an argument check of a desk program, not a physical hazard): read how comparable argument checks
   are classified there and in `tests/hazards/refusal_census.py`, and follow that. Run
   `python -m tests.hazards.refusal_census` as the test's message says.
2. `tests.test_battery_float_sweep` (`shard2.log`): `joulewise/b5_analysis/bracket.py` matches the test's
   pattern for a reader of the battery-evidence lexeme and is not in the `READERS` table of the test. Read
   what the table classifies and what its second test (`READERS.items()` loop) then requires of each class;
   read what `bracket.py` actually does with that lexeme; add the correct classification. If `bracket.py`
   does not in fact read battery evidence and only matches the pattern, say so and classify it as the table
   classifies such a file, never by loosening the pattern.
3. `tests.test_repin` `RealTreeTests.test_committed_registry_kind_p_rows_are_current` (`shard2.log`): the pin
   registry `configs/pins/registry.json` has a row saying that
   `configs/campaigns/v5_claim_25g83/sealed_inventory.json` carries the current digest of
   `joulewise/whole_window.py`; on this lane that file is the pinned harvest program's version, so the row is
   stale. **The sealed inventory is a sealed document and is never edited**: it records the bytes every
   measurement window executed, at the seal's claim commit, and stays true. Read `scripts/repin.py` and its
   census (`tests/test_repin.py` shows an "era" mechanism for a pointer that names bytes at a declared commit
   and no longer names the current ones) and record this row, and the rows of the other files the merge
   changed if they are in the same state (`joulewise/b5/harvest.py`, `joulewise/calibration_bracketing.py`
   and any other file the base merge touched: `git diff --stat 3c05b8076 3a745e8dc`), the way the registry
   records a pointer bound to a past commit. Later stages of this lane will edit `joulewise/whole_window.py`
   again and other files under `joulewise/` and `scripts/` that the sealed inventory lists: say in your
   report whether your change makes every sealed-inventory row era-bound once (preferred, if the mechanism
   allows it and it is the truthful description: the inventory is by definition a record at the claim
   commit), or whether each later edit will need its own registry row change, and what that change is.
   If the truthful fix needs a file outside your scope (for example a change to `scripts/repin.py`), do not
   make it: finish items 1 and 2 and return the question with your recommendation.

Constraints: edit nothing outside WRITE_SCOPE; in particular not `sealed_inventory.json`, nothing under
`joulewise/` or `scripts/`. Interpreter `/opt/homebrew/bin/python3.13`, `PYTHONDONTWRITEBYTECODE=1`, a `TMPDIR`
without "claude" or "codex" in its path; run `tests.hazards.test_refusal_allowlist`,
`tests.test_battery_float_sweep` and `tests.test_repin` the way CI does (`scripts/shard_tests.py` shows how
modules under `tests/` are imported). Blinding (binding): do NOT open anything under
`/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`, `/Users/edr/night-g2a/`,
`/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root under `/Users/edr/night-custody/measurement/`.

Report: per item, the cause in one sentence, the change, the module's result; for item 3 the answer about
later edits.
