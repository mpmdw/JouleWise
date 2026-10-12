SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/b5_analysis/fixtures.py", "tests/b5_analysis/test_fixture_shapes.py", "tests/fixtures/b5_analysis/**", ".scratch-fixtures/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 75 minutes of wall time; write the report by minute 65 whatever is unfinished.**

# Lane L9: the committed synthetic windows must load in several processes at once, and on Linux

You work in `/Users/edr/code/JouleWise-wt-l9-s3b` (branch `lane/2026-10-12-l9-fixtures-c`, cut from the S3
head `9f2a7e27b`, clean). `tests/b5_analysis/fixtures.py` loads committed synthetic windows
(`tests/fixtures/b5_analysis/pin2/` and `pin4/`, `archive.tar.xz` each) by restoring them at the absolute
paths they were built at, `/private/tmp/b5-s0-*`, because the archived records name those paths. Two
defects, both seen by the lead:

1. **Concurrency.** The whole suite runs six shard processes at once on one machine. Four modules failed at
   fixture load with `ValueError: synthetic original fixture root unavailable`
   (`tests.b5_analysis.test_fixture_shapes`, `test_tripwires`, `test_context`, `test_bracket`; logs
   `/Users/edr/night-archive/b5-consults/l9-rulings/suite-s3/shard{1..6}.log`): two processes want the same
   root, and the loader refuses a root it does not own.
2. **Linux.** CI runs on `ubuntu-latest`, where `/private/tmp` does not exist.

Required outcome: any number of processes may load the same window at the same time, on macOS and on Linux,
with no fixed absolute path on the machine, no workflow change, and no weaker test. Choose the mechanism
after reading how the paths are used (which archived records name the absolute root, and which readers
compare or open those paths): the preferred one is to restore each window under a fresh per-process temporary
directory and rewrite, in the restored copy only, exactly the records that name the old root, re-binding
every digest that covers a rewritten file in the same way the builder binds them (the committed archives stay
byte-identical; only the in-memory or on-disk restored copy changes). If a rewritten record is itself covered
by a digest the tests must treat as the pinned program's own output (so that rewriting it would make a test
about the pinned program vacuous), do not rewrite that record: say which records those are, and use for them
the fallback of an inter-process lock on a shared root, with the root taken from `tempfile.gettempdir()`
rather than `/private/tmp`... but only if the archived absolute paths permit it; if neither works, report
exactly why. Whatever you choose:

- `test_fixture_shapes.py` keeps every assertion about what the pinned program wrote; add a test that two
  processes started together each load `BETA_STD` and `GAMMA_STD`, read a record, and exit 0, and a test
  that loading works when `/private/tmp` is not writable or absent (simulate by pointing the loader's base at
  a fresh temporary directory; do not touch the real `/private/tmp`).
- No production file changes (`joulewise/**`, `scripts/**`, `configs/**` are out of scope), no other test
  module changes; if another fixtures module (`fixtures_s1.py`, `fixtures_s2.py`, `fixtures_s3.py`,
  `fixtures_s3b.py`) or a test must change because it hard-codes the old root, do not edit it: list the file,
  the line and the exact change.
- At the end run, **all at once as six parallel processes**, `tests.b5_analysis.test_fixture_shapes`,
  `test_tripwires`, `test_context`, `test_bracket`, `test_kept_units` and `test_validator_context`
  (`PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest <module>` from the repository root,
  each in the background of one shell command that waits for all six and prints each result). All must pass.
  This shell-level parallel run is the one exception to "no background task".
- Blinding (binding): do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root under
  `/Users/edr/night-custody/measurement/`. Synthetic fixtures only.

Report: the mechanism in five lines; which records name the old root and how each is handled; the parallel
run's six results; anything that must change outside your scope.
