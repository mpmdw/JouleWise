# Fable cold review: `w1-offload` (RL-53 W-5; audit Q10)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 04:45 PST. Reviewed head `1f45e511d`
(`ops/2026-11-11-w1-offload`, base the W1 line `b4a6c217f`). Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** One test is owed (O-1). The research lead's condition is met.

## The condition (RL-53 W-5): no change to when or whether a source is removed

- `scripts/offload_window.py` is not a bound file (not in `ARTIFACTS`, not in the receipt).
- The diff is 32 lines in three places: `_supervised` (exit code and `held_reason`), `_run_stages` (ask the Air
  before trusting a local receipt; always call `verify`), and `Gate.verify` (repair a missing queue entry).
  The `Offload` class, including `release`, every receipt check and the deletion and quarantine helpers, is
  untouched, as are `Gate.receipts`, `check_sealed` and `write_once`.
- The seat first committed a characterization test of 17 fixed states with "may delete: yes or no" from the
  base code, and it still passes unchanged after the fixes: only the two states with both verified receipts
  and a fresh re-hash delete, before and after.

## What I did

- Read the diff and the 17-state table.
- Ran `python3.13 -B -m unittest tests.test_offload_window` on the Air: 107 tests, OK.
- Mutation-tested six points: five killed, one survived (O-1).

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| O-1 | Medium | Surviving mutant: `stale_air_receipt` forced true. The local `receipt-air.json` is meant to be cleared only when the Air explicitly reports no receipt (`None`). No test covers the other case: the Air reports a receipt for a different manifest digest. There the local receipt must be kept, and the run must end in the existing mismatch refusal. | One test for that case: local receipt still present afterwards, exit is the integrity mismatch, nothing pushed over it. |
| O-2 | Low | Every run with a sealed manifest now asks the Air (`stat`) and calls `verify` even when already verified. That is the fix, and it costs one or two more calls per run. If the Air is unreachable the run now ends in the transport error earlier than before. | Say so in the module docstring's exit-code note. No behaviour change. |
| O-3 | Informational | A held release keeps exit 0, because the bound caller `scripts/align_v4_offloads.py` and the runbooks expect it; the hold is now visible as `held_reason` in the span, the journal and the activity record. | None. The Air-side watcher can alarm on `held_reason`; that belongs to the seat `sm-air-watch`. |

## Native check owed after install (remote)

On the Air store with a synthetic window: remove one queue entry by hand, run `verify`, and confirm the entry
is recreated and the second copy proceeds.
