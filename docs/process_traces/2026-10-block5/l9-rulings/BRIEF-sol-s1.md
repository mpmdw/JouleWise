SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/kept_units.py", "tests/b5_analysis/test_kept_units.py", "tests/b5_analysis/fixtures_s1.py", ".scratch-s1/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree.

# Build stage S1 of lane L9 (the block-5 analysis code): kept units

You work in `/Users/edr/code/JouleWise-wt-l9-s1`, a worktree cut from the lane branch after stage S0 was
committed (clean tree). The design is `/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`
(SHA-256 `3465acf9…2e7d`). Read its section 0 (terms), sections 3.1 to 3.4, 4.0 and 4.1, the head of section 5
and its part "S1". Read `docs/process_traces/2026-10-block5/l9-rulings/DECISIONS.md` and, in `RULING.md`
beside it, sections J3 and P9. (Those files are on the records branch; read them at
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/`.)

## What S1 delivers (design section 5, "S1", is the authority)

`joulewise/b5_analysis/kept_units.py`: `load_kept_units` and its record (`KeptUnits`, `CellKeptUnits`,
`to_record`, `removed_run_ids`) with the numbered checks of design 3.4, read through the S0 archive handle so
every byte is authenticated by its digest under `outputs`. The plan's named fixtures first (analysis plan
lines 753 to 757), then every refusal path the design lists under S1.

Two additions from the rulings:

1. **The J3 tripwire** (`RULING.md` J3 (b) items 1 to 3): a function that, given the kept units and a verdict
   row's `bundle_ids`, stops with `kept_member_outside_verdict_membership:<run_id>` when a member of a kept
   unit is not in the row. Build and test it here as a pure function; stage S3 calls it.
2. **What may leave the program** (`RULING.md` P9 (b) items 2 and 3): `to_record` is a restricted-custody
   record. Add `to_structure_record`, which returns only what P9 item 2 allows (per cell n_r and n_b, counts
   by family, counts by code only for codes whose catalog blinding is STRUCTURE, verdict words,
   `claim_usable`, digests), and a test that no member id, no RESTRICTED code name and no float appears in it.

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
