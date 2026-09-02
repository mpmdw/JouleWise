# Delta re-audit 2 — magistrate disposition (2026-09-02)

Seat: terra xhigh, execution lens (`20-terra-248-delta-2.md`, brief
`19-delta-2-brief.md`), detached worktree at `8096cb80`. Wrapper status:
`semantic_status=findings completion=complete run_status=OK
scope_action=passed rc=0`; envelope 3557 bytes.

Verdict: SHOULD-FIX 2 / NIT 1 — no blocker. D2 replicated all eight values of
record (exact seconds and 4-decimal ms) byte-for-byte with the seat's own
Decimal/type-7 code; D9 reproduced the DG-071 median and IQR strings from the
Markdown `## Method` alone (24-line script, no extra sentence needed) — the
replication bar is met.

## Dispositions

- **SF-EXEC-01** (mutant `ROUND_HALF_EVEN → ROUND_HALF_UP` survived the 22
  tests). FIXED at the bench (smaller than a delegation contract): new
  `test_millisecond_rendering_ties_round_half_even_through_main` — two
  two-record fixtures of identical width `0.00123445 s` (→ `1.2344`, where
  half-up prints `1.2345`) and `0.00123455 s` (→ `1.2346`), driven through
  `main`, asserting DG-071 and DG-075 `median_ms`.
- **SF-EXEC-02** (mutant dropping `len(starts) != 1` survived). FIXED at the
  bench: `different-start` fixture added to
  `test_record_rail_set_mismatch_refusal_reaches_main` (gpu row
  `interval_start_s` = `9.0000001`, siblings `9`).
- **NIT-EXEC-01** (file 18's carried scenario — numerically-equal distinct
  timestamp literals — cannot issue: the positive-width construction refuses
  `records_do_not_tile`, the tiled construction refuses
  `record_interval_not_positive`). ACCEPTED as a correction of the trace;
  no producer change. File 18 stands as written with this file as its
  correction (custodied rulings are corrected by dated addendum, not
  rewritten).

Producer unchanged; `docs/paper/round7/dg071-dg075-statistics.{json,md}` at
`8096cb80` therefore remain the issued artifact (`script_sha256` unchanged —
checked below).

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-paper-d
$ TMPDIR=<scratchpad>/tmpbench /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics
Ran 23 tests in 0.167s

OK
exit=0
$ # mutant copies under <scratchpad>/mut-{base,halfup,starts} (two files each, git init + commit so git_commit resolves)
$ # halfup: sed 's/rounding=ROUND_HALF_EVEN/rounding=ROUND_HALF_UP/' (+ import); starts: delete the line "        or len(starts) != 1"
== base
Ran 23 tests in 0.194s
OK
== halfup
FAIL: test_millisecond_rendering_ties_round_half_even_through_main (…)
Ran 23 tests in 0.183s
FAILED (failures=1)
== starts
FAIL: test_record_rail_set_mismatch_refusal_reaches_main (…)
Ran 23 tests in 0.214s
FAILED (failures=1)
exit=1
```
