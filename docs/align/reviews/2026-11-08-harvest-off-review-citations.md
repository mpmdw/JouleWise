# Review citations: harvest-off commits b9fedca2a and c6ea47ebe (ALIGN v4, R17)

2026-11-08. This is a citation record for `configs/b6/executing_reviews.json`. It reviews nothing itself. It
names the reports that already exist, the range each one reviewed, and what each one says about these two
commits. Where a report does not reach a commit, it is not cited for it.

## The commits

| Commit | Change to a covered path |
|---|---|
| `b9fedca2a` (Opus build) | `joulewise/adapters/powermetrics.py` +40 (`document_memo`, a scoped in-run memo); `joulewise/b5/harvest.py` +5/-1 (`assess_member` opens the memo per member) |
| `c6ea47ebe` (merged build, R17) | `joulewise/b5/harvest.py` +78/-15 (`tree_inventory(workers)`, `io_workers`, `stage_observer`; post-window harvest only, no capture path) |

## Reports that cover both commits

Both commits are ancestors of the candidate `720398640` (`origin/align/2026-11-08-harvest-off-merged`) that
the two R17 review seats were given.

1. **Agreement report (two independent builds).** `docs/align/v4/HARVEST-OFF-AGREEMENT.md`, sha256
   `6b1e1bf68e49aaef4fd6d258dd7122356d5c9935a04ea961eaf57739f8614666`, with the merge record
   `docs/align/v4/HARVEST-OFF-MERGED.md`, sha256
   `c7762f88c79c3c62b7e267b8fad4568679d9041ddcc2adc4e177fc268e67eb54`. The Opus build
   (`HARVEST-OFF-opus.md`, `align/2026-11-08-harvest-off-opus`) and the Sol build were compared; `document_memo`
   is the Opus design and `tree_inventory(workers)` (decision D3) is the Sol design, adopted by the agreement.
   Cross-family, but the agreement is a design comparison, not an executing review.
2. **Sol 6.1 review, seat 1.** `docs/align/v4/harvest-off-review-sol1.md`, sha256
   `67131fc0f252b50f367cd8c4a1457792b0ed5b63171f912187965abbb730c5f4` (branch `harvest-off-review`
   @ `7046923ed`; committed into the lane at `6938c3733`). Candidate `720398640`. Verdict: HOLD for the
   production route, for custody and a finality bypass in `harvest_offload.py`, `align_v4_harvest_off.py` and
   `align_v4_next_arm_packet.py`. The report names no finding against the `powermetrics.py` or `harvest.py`
   hunks above. Those findings were fixed in later lane commits; the report is cited for its coverage of the
   candidate, not as an admission.
3. **Sol 6.1 review, seat 2.** Witness module `tests/align/test_harvest_off_review_sol2.py`, sha256
   `904ef300565a150b56e32b845f5633860cfe2f0dac8dd6351574777c6f1918bf` (branch
   `align/2026-11-08-harvest-off-review-sol2` @ `c15b59993`). The seat's run was cut off before it wrote a
   report (`HARVEST-OFF-MERGED.md`: "its red tests are its findings"). It contains the archive-equality
   witnesses over the harvest.

## Reports NOT cited for these commits

The delta (`f7eb244d0..6938c3733`), delta2 (`6938c3733..2cfafa198`) and confirmation
(`2cfafa198..d2e512a53`) seat reports review ranges that begin after both commits, so they are not cited here.
The harvest-off HOLD findings of those rounds, and the confirmation seat's open MEDIUM, are about
`harvest_offload.py` and the packet builder, not these hunks.

## Not covered

The merge commit `c84df94bf` into the v4 line (it combines this lane with the timing-receipts changes) has no
review of its own and has no row. The timing-receipts commits `3c9c47a4e` and `ed9fd3ca1` wait for the Opus
cold review of the fix delta.
