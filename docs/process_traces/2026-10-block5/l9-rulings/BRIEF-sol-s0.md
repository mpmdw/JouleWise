SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/__init__.py", "joulewise/b5_analysis/windows.py", "joulewise/b5_analysis/archive.py", "joulewise/b5_analysis/steps.py", "configs/analysis/b5/seal_pins.json", "tests/b5_analysis/__init__.py", "tests/b5_analysis/fixtures.py", "tests/b5_analysis/test_frozen_files.py", "tests/b5_analysis/test_windows.py", "tests/b5_analysis/test_attempt_record.py", "tests/b5_analysis/test_archive.py", "tests/b5_analysis/test_fixture_shapes.py", "tests/fixtures/b5_analysis/**", ".scratch-s0/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree.

# Build stage S0 of lane L9 (the block-5 analysis code): base readers, frozen-file guard, fixtures

You work in `/Users/edr/code/JouleWise-wt-l9`, branch `lane/2026-10-07-l9-analysis`, head `3a745e8dc` (main
`3c05b8076` with the pinned harvest program `b039c0257` merged in; clean tree; the merge is already done, do
not redo it). The design is one file outside the repository:
`/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md` (SHA-256 `3465acf9…2e7d`). **Read section 0
(terms), sections 3.1, 3.2, 3.3, 3.6 and 3.7, section 4.0 (layout), the head of section 5 and its part "S0",
and sections 6.1 to 6.3.** Those sections are your specification; this brief only orients you and adds four
constraints. Other stages (S1 to S11) are not yours: build nothing of theirs, and where S0's code needs a
type a later stage defines, leave the seam the design names.

## What S0 delivers (design section 5, "S0", is the authority)

1. `joulewise/b5_analysis/windows.py`: the window index, the attempt record reader (`open_attempt_record`,
   with its numbered checks) and `select_analysed_attempts` (section 3.2).
2. `joulewise/b5_analysis/archive.py`: the archive handle (`open_archive`, `output_bytes`, the census of files
   read; section 3.3) for the two archive shapes of section 3.6.
3. `joulewise/b5_analysis/steps.py`: the step record helpers and `classify_step4_exit`.
4. `configs/analysis/b5/seal_pins.json`: the digests and pins that
   `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` prints (its addenda 1 to 4), copied from that
   text, and a test that checks every value against the seal record's text.
5. `tests/b5_analysis/fixtures.py`: `build_window(pack, *, shape, variants)`, driving the real desk verdict
   writer and the in-tree harvest over mock-adapter bundles as `tests/test_harvest_b5_window.py`'s `Window`
   harness does, and the named fixtures of the design.
6. The tests and refusal paths the design lists under S0, each with the counterfactual it names.
   `test_frozen_files` fails when any file of the frozen table (design 6.2) differs from the digest the seal
   record or the sealed inventory gives.

## Four constraints the design does not state

- **Fixtures from other pins.** A `pin1`, `pin2` or `pin3` archive must be written by the program at that
  commit (`7e6158d6`, `224a264c5`, `0699abbb0`). Do not run `git worktree add` or `git checkout`: export the
  commit read-only with `git archive <commit> | tar -x -C .scratch-s0/<pin>/` and run the builder there with
  `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13`. Commit-ready output goes under
  `tests/fixtures/b5_analysis/<pin>/` with a `PROVENANCE.md` beside it giving the exact command and the commit.
  Keep fixtures small (mock-adapter bundles only). `.scratch-s0/` is scratch: say in your report what is in it;
  the lead deletes it.
- **Frozen files.** Do not edit any file of the frozen table in design 6.2, nor any existing test module, nor
  anything outside WRITE_SCOPE. If an existing test fails because of your change, report it; do not edit it.
- **Interpreter.** Use `/opt/homebrew/bin/python3.13` (not a virtual environment), `PYTHONDONTWRITEBYTECODE=1`,
  and a `TMPDIR` whose path contains neither "claude" nor "codex". Run your own test modules
  (`python3.13 -m unittest tests.b5_analysis.test_windows` and the others, from the repository root in the way
  the existing modules under `tests/` are run; check how `tests/hazards/` or `tests/flags/` modules are
  discovered and follow it) and the six harvest-lane modules the design names as S0's exit condition
  (`tests/test_harvest_b5_window.py`, `test_harvest_b5_sources.py`, `test_harvest_b5_trigger_scope.py`,
  `test_neg8_survivors.py`, `test_neg8_corpus_cap.py`, `test_harvest_b5_rehearsal_compare.py`). Do not run the
  whole suite; the lead runs it.
- **Design item O16.** Read `tests/hazards/refusal_census.py` and report which files and directories it scans,
  whether `joulewise/b5_analysis/` falls under it, and whether your new refusal codes need entries in
  `configs/gates/hazard_refusals.json` (do not edit that file; say exactly what the entries would be).

## Blinding (binding)

The measurement block is blinded until a recorded release event that has not happened. Do NOT open anything
under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`, `/Users/edr/night-g2a/`,
`/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root of the measurement clone under
`/Users/edr/night-custody/measurement/`, and run no program over them. Everything you build is exercised on
synthetic fixtures only. Your report carries no energy, power or duration of a real window.

## Where the design is wrong

Nothing in the design was executed; every statement about code is a reading. When the code contradicts the
design (a line number, a field that does not exist, a shape difference of section 3.6 that the fixtures do not
show), the code wins for facts and the sealed texts win for rules: build what is correct, and list every such
divergence in your report under "Design divergences" with file and line. If a divergence is a question of
what the rule is (not what the code does), do not guess: finish the independent work and return the question
(question, options, recommendation, blocked work).

## Report

Changed files; for each S0 test and refusal path of the design, the test's name and that it passes, and for
each named counterfactual, how you showed the test fails without the guard (mutation run, with its output);
the six harvest-lane modules' results; design divergences; O16; what is not done.
