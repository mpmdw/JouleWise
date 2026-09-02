ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
EFFORT: xhigh
WRITE_SCOPE: ["scripts/issue_dg071_dg075_statistics.py", "tests/test_issue_dg071_dg075_statistics.py"]

# Fix round 2 — DG-071/DG-075 producer: population, exact arithmetic, method disclosure, tiling (ruled addendum 2026-09-02)

Checkout: `/Users/edr/code/JouleWise-wt-paper-d` (branch
`feat/2026-09-02-paper-d`; a linked worktree — you cannot commit, the
magistrate commits). Edit ONLY the two WRITE_SCOPE files. `TMPDIR` = a
subdirectory you create under
`<scratchpad>/`.
Python `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT run canonical
`python3 -m unittest discover`; run only
`python -m unittest tests.test_issue_dg071_dg075_statistics`. Do NOT write
under `docs/` (the artifact is re-issued by the magistrate at the bench after
your landing); you MAY run the producer with `--out <TMPDIR>/…` to see what
it would issue — the pinned bundle path is absolute and readable, never
modify it.

## Authority (read first, in this order)

1. The ruled conventions — the dated addendum at the END of
   `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`
   ("## Addendum 2026-09-02"). Its four numbered items are the contract; the
   producer's docstring cites THAT addendum path and no longer cites
   "R-167-1" anywhere (delete both mentions).
2. The findings you are curing, with their executed evidence:
   `docs/process_traces/2026-09-02-paper-d-dg071/12-sol-245-physics-refute.md`
   (B-1, SF-1, SF-2, SF-3) and `13-opus-246-physics-refute.md` (B-1, S-1,
   S-2, S-3, S-4, N-1). The blind seat's operative text in
   `15-blind-fable-seat-ruling.md` §Q2–Q4 is adopted verbatim by the addendum.

## Closure shapes (dictated; deviate only with a stated reason in the report)

C1. **Population.** `_read_records` (or a successor) groups rows by
    `timestamp_s` literal; a sampler record = one group. REFUSE
    `record_rail_set_mismatch` unless every group has exactly the rails
    `{"cpu_power","gpu_power","ane_power"}` (one row each) with
    byte-identical `interval_start_s` and `interval_end_s` literals across
    the three rows. Refuse `records_not_contiguous` if rows of one
    timestamp are interleaved with another's. Widths: ONE per record. JSON
    reports `sampler_record_count` (406), `rail_row_count` (1218),
    `rails` (the sorted three names); the words "duplicate timestamps" are
    gone (they were the other two rails).
C2. **Exact arithmetic.** Parse `timestamp_s`, `interval_start_s`,
    `interval_end_s` with `decimal.Decimal(literal)` (after the existing
    emptiness/finite checks — `Decimal` refuses `nan`/`inf` via
    `is_finite()`); never through `float`. Quantile: h = (n−1)·p exactly in
    Decimal, interpolate exactly; median = quantile(0.5); IQR = Q3 − Q1
    exact. Values of record: exact decimal seconds as JSON STRINGS
    (`str(Decimal)`, normalised so no exponent notation appears — use
    `format(d, 'f')`). Renderings: `*_ms` = (value × 1000).quantize(
    Decimal("0.0001"), ROUND_HALF_EVEN), ALSO written as JSON strings.
    Remove `MS_DECIMALS = 6`; the constant becomes `MS_RENDER_QUANTUM =
    Decimal("0.0001")`. Bump `SCHEMA_VERSION` to `…v2`.
C3. **Method disclosure.** The JSON carries a `method` object and the
    Markdown a "Method" section stating, in words a reader can replicate
    from: the population rule (C1), the exact-decimal arithmetic, the
    quantile formula (h = (n−1)·p, linear interpolation between the two
    neighbouring order statistics; Hyndman–Fan type 7 as a
    cross-reference), median = p 0.5 quantile (mean of the two middle values
    for even n), IQR exact before rendering, the four-decimal
    round-half-even rendering, and the sentence: "A float64 replication
    (numpy `linear`, R type 7) is guaranteed to agree only to three
    decimals because a float64 at 1.78e9 s has spacing 2.4e-7 s, coarser
    than the file's 1e-7 s literals; the digits characterise the retained
    bytes, not the sampler's physical timing resolution." Include the worked
    example: median 120.9186 ms exact vs 120.9185 ms float64.
C4. **Tiling verification (DG-075).** After grouping, verify for every
    record `interval_end_s` literal == `timestamp_s` literal, and for every
    boundary k ≥ 2, |Decimal(interval_start_s(k)) − Decimal(timestamp_s(k−1))|
    ≤ Decimal("0.000001"). REFUSE `records_do_not_tile` otherwise. JSON
    reports `max_tiling_gap_s` (exact string) and
    `tiling_gap_nonzero_boundaries` (expected 100). DG-075 sample = the
    405 consecutive differences of the sorted DISTINCT timestamp literals
    (Decimal); the Markdown carries the dependence sentence from the
    addendum item 4 ("DG-075 is the DG-071 distribution minus the first
    record …").
C5. **Refusals bite at `main`.** Every `IssuanceRefused` name in the module
    has ONE test that drives `main([...])` with a fixture engineered for
    that refusal and asserts exit 2 plus the refusal name on stderr. For
    each, the test's docstring names the counterfactual input. Then, in
    your report, list every refusal name with its test name, and show (in
    a copy under TMPDIR, never in the checkout) that deleting the
    `record_interval_not_positive` raise AND deleting the
    `record_rail_set_mismatch` raise each make exactly their named test
    fail. The two existing fixtures with the wrong shape (single-rail rows)
    are rewritten to three-rail records.
C6. **Precision regression.** A fixture whose two middle width literals
    have an exact mean that differs from their float64 mean at the fourth
    millisecond decimal; assert the exact rendering. (The real bundle's
    middle values are `0.1209148` and `0.1209224` s — build a small
    fixture around such a pair at epoch magnitude ~1.78e9 s and show the
    float64 path would print the other digit.)
C7. **Byte-identical replay** of the producer over the real bundle twice
    into TMPDIR; paste the two sha256s and the rendered table. The expected
    renderings (from the addendum's executed evidence): DG-071 n = 406,
    Q1 116.9720, median 120.9186, Q3 122.9227, IQR 5.9508; DG-075 n = 405,
    Q1 117.0321, median 120.9224, Q3 122.9270, IQR 5.8949. If yours differ,
    STOP and report the difference as a finding — do not tune.

Keep the producer standalone (no imports from other paper scripts), keep
the existing pin/sha/path refusals, keep `argparse` shape (`--repository-root`,
`--out`). Line count matters less than legibility: a reader must be able to
replicate the statistic from the docstring alone.

## Report (protocol, mandatory)

`claude-codex-report/v1` envelope first (fenced ```json, nothing before
it, UNDER 8192 BYTES — `verdict` = counts + the C1–C7 closure list with
`done|deviated|blocked` only; all evidence in the Markdown body). Body:
per-closure evidence (commands + output tails), the refusal↔test table
(C5) with the two mutant runs, the C7 replay block, then a `git diff --stat`
and anything the next reviewer must know.
