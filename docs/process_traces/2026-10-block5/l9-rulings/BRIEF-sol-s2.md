SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/bracket.py", "tests/b5_analysis/test_bracket.py", "tests/b5_analysis/fixtures_s2.py", ".scratch-s2/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree.

# Build stage S2 of lane L9 (the block-5 analysis code): the window bracket evaluation (L9-BRACKET, part 1)

You work in `/Users/edr/code/JouleWise-wt-l9-s2`, a worktree cut from the lane branch after stage S0 was
committed (head `88a3303ac`, clean tree). A second seat is closing S0 in another worktree at the same time: it may change `archive.py`'s handling of an unclean harvest checkout and the fixtures' capture bounds, nothing else; build on S0's functions as they are at your head. **You have 85 minutes of wall time; write the report by minute 75 whatever is unfinished, and list what is unfinished.** Building a synthetic window takes minutes: build each fixture once per test module (module-level cache), never per test. The design is `/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`
(SHA-256 `3465acf9…2e7d`). Read its section 0 (terms), sections 3.3, 3.6, 4.0 and 4.13, the head of section 5
and its part "S2". Read `docs/process_traces/2026-10-block5/trigger-erratum/ERRATUM.md` items 10, 11 and 14
(the admitted rule this stage implements). Read
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/DECISIONS.md` and, in
`RULING.md` beside it, sections J6 (b) (the definitions of b_op, B_max and b_sens only; the sensitivity pass
itself is stage S9) and J7 whole.

## What S2 delivers (design section 5, "S2", is the authority)

`joulewise/b5_analysis/bracket.py`: `ledger_prefix`, `evaluate_window_bracket`,
`require_ledger_copies_are_prefixes`, B_max and b_sens, with the tests and refusal paths the design lists
under S2. The evaluation calls the in-tree `joulewise/calibration_bracketing.py` (the pinned harvest's file,
frozen) with `trigger_scope="window_evidence"` for a window Erratum 3 governs and `"sealed"` otherwise.

Three additions from the rulings:

1. **J7 replaces the design's reading of the ledger copy's digest.** Build `RULING.md` J7 (b) items 1 to 5
   exactly, with its refusal names (`ledger_copy_digest_mismatch`, `ledger_prefix_not_at_terminal_pin`,
   `ledger_copy_not_prefix_of_live`, `ledger_copies_disagree_below_T`) and a test for each. The SHA-256 of
   `sources/SHA256SUMS` is returned for the caller's input census.
2. **The operative bound has one owner** (`DECISIONS.md` B1): the evaluation's result exposes
   `b_fiducial_s` as the window's operative bound, and this module exports the one function later stages call
   to compare a member's recorded operative bound with it
   (`require_member_bound_is_window_bracket(provenance, window_bracket)` →
   `operative_bound_not_the_window_bracket` when the bound is absent or different). Test it with a fixture
   whose post-capture bound differs from its pre-capture bound; the mutations that must fail are the
   pre-capture bound substituted and another window's bound substituted. If the S0 fixtures do not yet have
   distinct pre and post bounds, build the variant in `fixtures_s2.py` and say so.
3. **O6 is not yours** (finalization, stage S5), but B_max must be computed from ledger rows only: add a test
   that B_max is unchanged when every historical capture file is made unreadable.

## Constraints

- **Authority.** The design is your specification; `DECISIONS.md` wins where it differs from the design; a
  cold ruling (`RULING.md` as amended by `ERRATUM-RULING.md`) wins over both. Nothing in the design was
  executed: when the code contradicts it, the code wins for facts and the sealed texts and rulings win for
  rules. List every divergence in your report under "Design divergences" with file and line. If a divergence
  is a question of what the rule is, do not guess: finish the independent work and return the question
  (question, options, recommendation, blocked work).
- **Frozen files.** Edit nothing outside WRITE_SCOPE: no file of the frozen table in design 6.2, no existing
  test module, no file of stage S0 (`windows.py`, `archive.py`, `steps.py`, `fixtures.py`). A fixture variant
  you need goes in your own `tests/b5_analysis/fixtures_<stage>.py`, built on the S0 builder. If S0 code is
  wrong or lacks a seam you need, report it with the exact change you would make; do not make it.
- **Refusal paths.** Every refusal path the design lists gets a test, and for each named counterfactual you
  show the test fails without the guard (a mutation run, with its output, in your report).
- **Interpreter.** `/opt/homebrew/bin/python3.13` (not a virtual environment), `PYTHONDONTWRITEBYTECODE=1`,
  a `TMPDIR` whose path contains neither "claude" nor "codex". Run your own modules and the existing
  `tests/b5_analysis/` modules. Do not run the whole suite; the lead runs it.
- **Blinding (binding).** The measurement block is blinded until a recorded release event that has not
  happened. Do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root of the measurement
  clone under `/Users/edr/night-custody/measurement/`, and run no program over them. Everything you build is
  exercised on synthetic fixtures only. Your report carries no energy, power or duration of a real window.

## Report

Changed files; for each test and refusal path of the design, the test name and that it passes; each
counterfactual with its mutation output; design divergences; what is not done.
