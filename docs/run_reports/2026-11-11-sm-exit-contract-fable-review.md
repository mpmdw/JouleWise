# Fable cold review: `sm-exit-contract` (audit section 8.2 items 6 and 9)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 03:35 PST. Reviewed head `a0edb4566`
(`feat/2026-11-11-sm-exit-contract`, base `origin/main` `41c7a1444`). Builder: Sol xhigh.

**Verdict: ADMIT.** One interface note (N-1) is deferred to the wave-2 watcher seat. Nothing blocks the merge.

## What I did

- Read the whole diff: `joulewise/exit_contract.py` (286 lines), `tests/test_exit_contract.py` (366 lines),
  one `CANONICAL.md` row, one inserted line in `scripts/test_timings.json`, two run reports.
- Ran `python3.13 -B -m unittest tests.test_exit_contract`: 26 tests, OK.
- Checked scope: no existing file under `joulewise/` or `scripts/` is edited, and no existing module imports the
  new one. The timings file gained one line and was not re-serialized.
- Spot-checked citations against the code: night driver 0/3/4/5/6 (`scripts/run_night.py`, both refs), the
  block-5 chain codes including the W1-only 13 (`joulewise/b5/chain.py:118` on the W1 line), R1 driver, R1 runtime
  (`EXIT_REFUSED, EXIT_FAILED = 2, 3`), PREQUAL (`EXIT = {"pass": 0, "fail": 1, "incomplete": 3}`), harvest
  2/4/6/0. All agree with the table.
- Mutation-tested the classifier and the parser. Ten mutants, ten killed:

| Mutant | Killed by |
|---|---|
| `type(returncode) is int` loosened to `isinstance` (bools and subclasses pass) | 20 failures |
| unverified contract allowed to classify | 1 |
| night driver 5 (`CHAIN_FAILED`) classed SUCCESS | 1 |
| signal range starts at 128 | 2 |
| `is_success` ignores `declared` | 1 |
| negative return codes allowed to match | 1 |
| plan contract without a declared 0 accepted | 1 |
| duplicate normalized plan keys accepted | 1 |
| dry-run 3 (`outcome_class`) classed SUCCESS | 1 |
| `as_outcome_map` serves an unverified contract | 1 |

## Findings

- **N-1 (interface, deferred).** `as_outcome_map` returns each tool's own word (`GO`, `completed`, `agree`).
  A consumer cannot tell from the word alone which codes are success. When `window_outcome` adopts a contract it
  should take the `Contract` (or a map to `ExitClass`), not this word map. Disposition: fixed where the first
  consumer is built, in the wave-2 seat `sm-air-watch`. Nothing consumes the map today.
- **N-2 (informational).** Harvest exit 0 is classed SUCCESS with the word `COLLECTED/NO_COLLECTION/NULL`, and
  the night driver's 0 is `GO`. Both notes say that the code proves process completion or admission only. That
  is the audit's point about these tools, stated as data. No change.
- **N-3 (informational).** The drift test checks citations whose files exist at `HEAD`. Citations into the W1
  line, the offload branch and the release-tools branch are checked by the seat once and by my spot checks; they
  start being drift-tested when those files reach `main`. The test already fails if a baseline file disappears.

## Not covered

- Python 3.11 was not run locally; CI runs it.
- No tool adopts the table. Adoption by bound writers is ruled out for the v4 series (RL-53, W-4).
