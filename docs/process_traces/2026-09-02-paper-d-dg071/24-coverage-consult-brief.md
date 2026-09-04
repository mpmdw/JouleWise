ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
EFFORT: xhigh
WRITE_SCOPE: []

# CONSULT (escalation trigger, rule 11) — systematic mutation coverage of the DG-071/DG-075 producer's reported fields

Checkout: `/Users/edr/code/JouleWise-wt-paper-d2` (detached at `8ab397b5`).
Read-only: write NOTHING under the checkout. `TMPDIR` = a subdirectory you
create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT run canonical
`python3 -m unittest discover`; you MAY run
`python -m unittest tests.test_issue_dg071_dg075_statistics` (23 tests) and
mutant copies under TMPDIR. The retained bundle (read-only) is at
`/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`.

## Why you are being consulted (the trigger, not a fix request)

`scripts/issue_dg071_dg075_statistics.py` issues
`docs/paper/round7/dg071-dg075-statistics.{json,md}`. Its test module has 23
tests, 16 of them one-refusal-one-test through `main`, two dictated mutants
killed. Two consecutive review rounds then each found two SURVIVING mutants
that change a PUBLISHED value:

- delta 2 (terra, `docs/process_traces/2026-09-02-paper-d-dg071/20-terra-248-delta-2.md`
  §D7): `ROUND_HALF_EVEN → ROUND_HALF_UP` survived; dropping the
  `len(starts) != 1` guard survived. Both were patched at the bench with two
  hand-added fixtures (`21-delta-2-disposition.md`).
- counter-review (Opus, `<scratchpad>/out/249-opus-paper-d-counter.md` —
  read finding C-1 and §5): rendering IQR as `render_ms(Q3) − render_ms(Q1)`
  instead of `render_ms(Q3 − Q1)` survived (issues `5.9507` for `5.9508`);
  changing `sum(gap != 0)` to `sum(gap > TILING_TOLERANCE_S)` survived
  (issues `tiling_gap_nonzero_boundaries: 0` for `100`).

Same signature twice: a reported field with no test that pins its value on
an input where the wrong computation differs. Under the standing escalation
rule the next spend is this consult, not a third pair of fixtures.

## Questions — answer each with a recommendation, its reasoning, and what it would NOT catch

Q1. **Coverage shape.** The magistrate's candidate: ONE synthetic "golden"
    bundle fixture engineered so that every reported field takes a value a
    plausible wrong computation would change — nonzero tiling gaps of
    several sizes (some below and some at the tolerance), quartiles that
    require interpolation with a non-trivial weight, an IQR whose 4-decimal
    rendering differs from the difference of the rendered quartiles, an ms
    rendering that sits on an exact half, ≥ 3 rails with realistic epoch
    magnitudes — plus a test that asserts the ENTIRE `build_payload` output
    (minus `producer.git_commit`/`script_sha256`) against a hand-derived
    golden dict, so any field drift fails. Is that the right shape? Where is
    it weak (a golden dict that is derived by running the producer once is
    worthless — how do you make the hand-derivation credible and short)?
    Alternatives you may argue for: property-based/differential test against
    an independent 20-line reference implementation on random bundles
    (Decimal, type 7); a per-field census test that walks
    `build_payload`'s keys and fails on any key without an explicit
    assertion somewhere in the module; a mutation-score harness (the repo has
    `scripts/mutation_kill*`? — check `ls scripts | grep -i mut` and say what
    exists) run as a test gate. Recommend ONE primary shape and say whether a
    second is worth its maintenance.
Q2. **Enumerate the mutant classes** that the recommended shape kills and,
    explicitly, the ones it does not (e.g. message-text mutants, refusal
    ordering, `argparse` defaults). For each not-killed class, say whether it
    can change a published digit.
Q3. **Build the golden bundle on paper** (in your report, not in the
    checkout): the CSV rows (≤ 8 records), the hand-derived values for every
    reported field, shown step by step so the magistrate can check them
    without running code. Then run your own reference computation under
    TMPDIR to confirm your hand-derivation, and run the CURRENT producer on
    the fixture (`--bundle <TMPDIR>/golden.csv` with the pins patched the way
    the existing tests do it, or via `issue_artifacts`) to show which fields
    it currently gets right. Paste both.
Q4. **Which of the four surviving mutants** (two from terra 248, two from
    Opus 249) does your fixture kill, shown by running the 23 tests + your
    proposed test against copies under TMPDIR carrying each mutant? (You may
    write the proposed test file under TMPDIR and run it with `-m unittest`
    from a scratch clone; you may NOT edit the checkout.)
Q5. **Process.** Is the same-signature reading correct (two rounds, same
    defect class)? Would you have escalated to a cold gate rather than a
    consult, and why or why not? One paragraph, plain words.

## Report shape (protocol, mandatory)

Return the `claude-codex-report/v1` envelope FIRST (fenced ```json, nothing
before it, UNDER 8192 BYTES): `verdict` = `{"recommendation": "<one line>",
"counts": {"blocker": n, "should_fix": n, "nit": n}, "findings": []}` only —
all reasoning, tables, CSV rows, derivations and command output in the
Markdown body after the fence. Body sections Q1–Q5, then "What this consult
did NOT check".
