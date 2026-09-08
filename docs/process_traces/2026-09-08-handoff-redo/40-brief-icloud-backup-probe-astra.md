WRITE_SCOPE: ["scripts/paper_excursion_decomposition.py","tests/test_paper_round7_artifacts.py","tests/test_paper_excursion_decomposition.py"]

# Seat brief — ICLOUD-BACKUP-PROBE-01: a filesystem probe of an iCloud path can block the test suite forever (gpt-6-astra, medium)

Observed on this Mac today (two independent full-suite replays): `scripts/paper_excursion_decomposition.py` has
`BACKUP_ROOTS = ("/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup",)` (line ~83) and
iterates it (~line 122) with `os.path.isdir` / `listdir`. When iCloud is not responsive, that call blocks with zero
CPU indefinitely (a sampled child sat in `__opendir2 -> __open_nocancel` for 37 minutes; a 5 s alarm probe on the
path times out). `tests/test_paper_round7_artifacts.py` loads the script (importlib at ~line 62-64) and also runs it
as a subprocess (~line 606), so one unresponsive iCloud mount hangs a whole test shard.

Cure (implement all three):
1. The backup-root probe must be BOUNDED: probe each root in a helper that cannot block the caller longer than a
   small budget (e.g. run `os.path.isdir`/`os.listdir` in a daemon thread with a 2 s join, or a subprocess with a
   timeout), treating a timeout as "root unavailable" with a named, logged reason — never as an error that
   changes any computed number (an unavailable backup root must yield exactly the result an absent root yields
   today; confirm that from the code and say so).
2. An environment override `JOULEWISE_BACKUP_ROOTS` (os.pathsep-separated; empty string = no roots) so tests and
   replays can point the script at a scratch directory or disable the probe; the default stays the iCloud path.
3. Tests: every test that imports or runs the script sets the override to a scratch dir (fixture), plus a
   regression that makes the probe target a path whose `isdir` blocks (e.g. a FIFO-backed or a mocked
   `os.path.isdir` that sleeps 10 s) and asserts the helper returns within the budget with the "unavailable"
   outcome; and a regression that the override with an empty string yields zero roots.
Constraints: do not touch the iCloud path itself during tests (it may hang your run); do NOT run the
repository-wide suite; acceptance = the two test modules to a log with rc; no `git commit`; keep every existing
computed artifact byte-identical (if a golden/fixture check exists for this script's output, run it and report).
Header < 8192 bytes; genre implementation verdict keys; body = the counterfactual each regression kills,
fail-before/pass-after tails, rc.
