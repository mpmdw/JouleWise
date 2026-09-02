ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/issue_dg071_dg075_statistics.py", "tests/test_issue_dg071_dg075_statistics.py"]

# Paper seat D — the producer that ISSUES the DG-071 / DG-075 statistics

Checkout: `/Users/edr/code/JouleWise-wt-paper-d` (branch
`feat/2026-09-02-paper-d` at `a63d45bd`, clean). Two new files only.
Do not commit, stash, checkout, or push. Everything under `runs*/` is
retained evidence: READ-ONLY. `TMPDIR` = a subdirectory you create under
`<scratchpad>/`.
Python: `/Users/edr/code/JouleWise/.venv/bin/python`. Named test modules
only; never canonical `unittest discover`.

## Problem

`docs/paper/results-fill-registry.md` rows DG-071 and DG-075 (`:640-648`)
are `STOP_FILL` / `VALUE_UNISSUED`: the statistics were RATIFIED
(`docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
— read it in full; it is the specification) but no producer issues them, and
the registry forbids a desk-computed value. Read also
`docs/paper/round7/fill-checklist.md:236-250` and `:356-371` (open gap 5),
the registry's definition of "issued" and "supplier" (`fill-checklist.md:15-22`),
and — as the pattern to imitate — `scripts/paper_excursion_decomposition.py`
and `scripts/paper_anchor_correction_quantified.py` (how they locate the
retained bundle, hash-pin their inputs, write a JSON+MD pair, and are
replay-fenced), plus `scripts/check_paper_replay_fence.py`.

## Deliverable

`scripts/issue_dg071_dg075_statistics.py`: over the hash-pinned cited R03P
bundle named by the ratification, compute (a) DG-071: median and IQR of
`interval_end_s - interval_start_s` over the sampling records, (b) DG-075:
median and IQR of consecutive unique `timestamp_s` differences — EXACTLY as
the ratification defines them (quote its defining sentences in the module
docstring; if the ratification leaves any convention open — endpoint
inclusion, merged intervals, unit, rounding — STOP and report `NEEDS_RULING`
with the exact ambiguity rather than choosing). Output: a JSON artifact
carrying the input bundle path + sha256, the record count, both statistics,
the script's own sha256, the git commit, and the registry row ids; plus a
companion Markdown rendering. Deterministic: two runs produce byte-identical
JSON. Refuse (non-zero exit, named reason) if the bundle path, its sha256,
or its record schema differs from the pinned expectation. Do NOT edit the
registry; the magistrate registers the issued artifact.

`tests/test_issue_dg071_dg075_statistics.py`: synthetic fixture bundle with
hand-computable records (e.g. five records → median/IQR you can state by
hand in the test), byte-identical re-run, and one refusal per guarded
precondition (wrong sha, missing field, non-monotone timestamps). Also run
the script ONCE for real over the pinned bundle with `--out` under your
TMPDIR and report the two statistics and the artifact sha256 — the
magistrate will re-run it.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`), then
under 70 lines: the ratification sentences you implemented (quoted), the
real-run values, the test tails, and any `NEEDS_RULING`.

## Ruling R-167-1 (magistrate, 2026-09-02) — resolves the NEEDS_RULING of the first seat

The ratification left the IQR estimator and the issued-value rounding open.
Ruling: use the convention the two landed round-7 producers already use, so
every round-7 desk statistic in the paper is computed one way:

- median = `statistics.median(ordered)`;
- Q1 / Q3 = the linear-interpolated quantile of the sorted sample exactly as
  defined by `_quantile` in `scripts/paper_excursion_decomposition.py:246-259`
  (position = fraction × (n−1), linear interpolation between neighbours;
  n = 1 returns the single value; empty sample raises) — copy that function
  verbatim into your module with a comment citing its origin; do not import
  it (the paper scripts are standalone by convention);
- IQR = Q3 − Q1;
- unit: the JSON carries BOTH the unrounded seconds values (`*_s`, raw
  float repr) and the millisecond renderings rounded to `MS_DECIMALS = 6`
  as in `scripts/paper_excursion_decomposition.py:90`; the Markdown
  companion prints milliseconds at 6 decimals. Rounding is a rendering
  convention; the unrounded seconds are the issued values of record.
- "consecutive unique `timestamp_s`": sort the distinct `timestamp_s`
  values ascending, take first differences; duplicates collapse to one
  value before differencing (so a duplicated stamp contributes no zero
  spacing). Record the count of distinct stamps and the count of
  duplicates dropped in the JSON.
- "every retained record": all records of the cited R03P bundle file, no
  filtering; a record missing either field is a refusal, not a skip.

No other convention is open. Proceed to implement, test, and run once.
