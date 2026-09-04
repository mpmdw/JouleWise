ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
EFFORT: xhigh
WRITE_SCOPE: []

# Refuter, EXECUTION + PHYSICS lens — DG-071/DG-075 statistics producer at `a3dadadd` (branch `feat/2026-09-02-paper-d`)

Checkout: `/Users/edr/code/JouleWise-wt-paper-d2` (detached at `a3dadadd`).
Read-only: write NOTHING under the checkout. `TMPDIR` = a subdirectory you
create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT run canonical
`python3 -m unittest discover`; you MAY run
`python -m unittest tests.test_issue_dg071_dg075_statistics` and any
one-off computation you write under TMPDIR.

The retained bundle is NOT in this worktree. Read it at the main checkout,
absolute path (read-only, never modify):
`/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
(expected SHA-256 `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`;
verify with `shasum -a 256` before using it).

## Files under review

- `scripts/issue_dg071_dg075_statistics.py` (producer)
- `tests/test_issue_dg071_dg075_statistics.py`
- `docs/paper/round7/dg071-dg075-statistics.{json,md}` (issued artifact)
- The ratification the producer implements:
  `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
- Registry rows DG-071 / DG-075 (`grep -n "DG-071\|DG-075" docs/paper/results-fill-registry.md`)
- Prior rounds (read for context, do not repeat their lens): contract-lens
  refuter luna 178
  `<scratchpad>/out/178-luna-paper-d-contract.md`
  and delta re-audit terra 185
  `<scratchpad>/out/185-terra-paper-d-delta.md`.

## Your lens: EXECUTION + PHYSICS (measurement-adjacent)

The contract lens already checked ratification text vs implementation vs
artifact. You check whether the NUMBERS are physically the right numbers and
whether the code computes what it says under real inputs. Answer each
question with evidence you executed (paste command + output tail); a claim
without an executed check is not a finding.

P1. **Record multiplicity.** The bundle has 1218 rows = 406 sampler
    records × 3 rails (`cpu_power`, `gpu_power`, `ane_power`; census with
    `awk -F, 'NR>1{print $4}' … | sort | uniq -c`). Each rail row of one
    sampler record carries the SAME `interval_start_s`/`interval_end_s`.
    DG-071 is issued with "Sample count 1218": every interval width is
    counted three times. Rule: (a) is the median/IQR over 1218 identical
    triples equal to the median/IQR over the 406 distinct widths (compute
    both; linear-interpolated quartiles CAN differ when a sample is
    tripled — show whether they do here, to the issued six decimals);
    (b) does the ratification's "every retained record" mean a CSV row or a
    sampler record, and does the paper sentence "sampling-record interval
    width" (draft line 256 — read the frozen draft
    `docs/paper/draft-v1.md` around that line, read-only) mean the same
    thing the artifact's "Retained record count: 1218" reports? If the
    reader would be misled, say what the artifact/registry row must say.
    Severity is yours to set; give the reasoning.

P2. **Quartile method.** `_quantile` at `:99-113` is a linear interpolation.
    State exactly which of the standard definitions it matches (Hyndman &
    Fan type — R's default type 7? numpy `linear`?) by executing numpy
    (`/Users/edr/code/JouleWise/.venv/bin/python -c "import numpy"`, if
    present; otherwise say so) on the 406-width sample and comparing to the
    producer's values to the issued six decimals. Does the ratification pin
    a method? If not, does the artifact DISCLOSE the method so a reader can
    replicate the numbers (Ed's replication bar)?

P3. **DG-075 vs DG-071 physics.** DG-075 = consecutive differences of the
    406 unique `timestamp_s`; DG-071 = `interval_end_s - interval_start_s`.
    In this bundle `interval_end_s == timestamp_s` and
    `interval_start_s == previous timestamp_s` for tiling records (check the
    first rows and the whole file: count rows where `interval_start_s` ≠
    the previous distinct timestamp). If the two statistics are the same
    sample shifted by one record, say so explicitly and say whether the
    Q1 difference (116.951942 vs 117.032051 ms) is entirely the one
    dropped record; if not, find what else differs.

P4. **Float and rounding.** Timestamps are ~1.78e9 s with ~1e-7 s
    resolution in the CSV; widths are ~0.12 s. Check that parsing with
    `float()` and subtracting does not lose resolution that matters at six
    rendered decimals of milliseconds (1e-9 s). The unrounded seconds in
    the Markdown are Python `repr` — confirm the JSON carries the same
    unrounded values and that `round(x*1000, 6)` is the only rounding.

P5. **Refusals bite at the production site.** For each `IssuanceRefused`
    name (`record_schema_mismatch`, `record_field_missing`,
    `record_field_invalid`, `timestamps_non_monotone`,
    `record_interval_not_positive`, `record_set_empty`,
    `insufficient_unique_timestamps`, and any others you find), name the
    test that exercises it through `main` and say whether a mutant that
    deletes the raise is killed by that test. Run the module's tests once
    (`Ran 8 tests` expected) and, for at most TWO refusals of your choice,
    apply the mutant in a copy under TMPDIR (`git clone --no-checkout`, or
    copy the two files) and show the test failing.

P6. **Anything else** the execution/physics lens finds: replay
    determinism across two runs (you may re-run the producer with
    `--repository-root /Users/edr/code/JouleWise --out <TMPDIR>/…` ONLY if
    it accepts an output path outside the repo — read `main` first and do
    not write under any checkout), the claim that the former
    "111.8–112.5 ms band is the bottom of the width distribution" (compute
    the minimum, 5th percentile and the count of widths below 112.5 ms),
    ordering assumptions.

## Report shape (protocol, mandatory)

Return the `claude-codex-report/v1` envelope FIRST (fenced ```json, nothing
before it). **The JSON envelope must be under 8192 bytes**: `verdict` =
`{"counts": {"blocker": n, "should_fix": n, "nit": n}, "findings": [{"id",
"severity", "title", "file", "line"}]}` only — ALL evidence, command
output, numbers and reasoning go in the Markdown body after the fence, not
in the envelope. `severity` ∈ {blocker, should_fix, nit}. Then a body with a
`VERDICT:` line (`CLEAN` or `BLOCKER n / SHOULD-FIX n / NIT n`), one section
per P1–P6 with executed evidence, and a final "What this review did NOT
check" section.
