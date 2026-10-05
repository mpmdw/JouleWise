# Block-4 lane X7 (Sol 6.1 xhigh): the attempt-history chain (X6 F5) and NULL-reservation recovery (memo 1.11)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x7 (branch `lane/2026-10-05-b4-x7` at bda1c180 = PR #483 head with origin/main merged). Scratch /tmp/dd5-x7/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics or Metal. Never touch the four pinned estimator files.

## Lead ruling on X6 F5 (binding)

The threat model is honest mistakes and hallucinated records, not forgery (D-161). Under that threat model, the attempt history of a block is proven complete by two checks together:

1. **Mandatory create-once pointer.** Every `s1` authorization and plan (every fresh attempt: a NULL re-arm, the one admission re-arm, and the `s2`) carries a required field `previous_attempt` that is either the literal `{"none": true}` (the block's first attempt only) or `{"path": <absolute harvest.json path>, "sha256": <hex>}` naming the immediately preceding attempt's harvest. The plan writer requires it (no default), writes it into the authorization and the plan, and the authorization stays create-once. Omission refuses.
2. **Completeness census.** The block-4 harvesters walk the chain from the current attempt back to `none`, authenticating each link by sha256. Then they enumerate every attempt harvest of this block under the block's harvest archive root (the registered archive layout; find it in the code and registration draft) and refuse unless the set of harvests found equals the set on the chain exactly: no fork (two attempts naming the same predecessor), no orphan, no second `none`.

From the walked chain, the harvester enforces the registration's counts: at most one guard-attested admission-abort re-arm per block (addendum B item 4: authenticated guard observation and abort reason, no other RECOVER cause present on that attempt); a second admission abort returns the same-refusal-twice outcome; at most one `s2`, and only after an `s1` RECOVER from a named tooling defect; NULL re-arms are allowed and spend neither allowance. The aborted attempt's bytes are never pooled with the fresh attempt.

Then implement X6 F5 itself in `scripts/harvest_v5_g2b_window.py` (around line 697) and `scripts/harvest_v5_qualification.py`: the one admission-abort re-arm as above, with a fresh `s1` written without END STATE and without spending `s2`.

## Memo 1.11 (`~/night-archive/ia-0a40/MEMO.md` lines 243-261)

- Add an `s2` occurrence to the plan writer. It is written as `s1` plus a required `previous_attempt` pointer to the RECOVER `s1` harvest, and the writer checks the predecessor's verdict and named tooling defect.
- Add a NULL-only reservation restore: `scripts/restore_v5_null_reservation.py`. It copies the attempt's ledger to custody (create-once). It refuses unless the dropped tail is exactly one bracket-session-open row written by that attempt's T-0 reservation, and unless the attempt's harvest is NULL with no `chain.started`. Then it restores the seed bytes with the pin unchanged and writes an authenticated restore record that the next attempt's writer and harvester verify. Read the ledger code (`joulewise/` calibration ledger, `scripts/reserve_calibration_window_bracket.py`) for the row schema; do not change the ledger format.

## Tests

Add `tests/test_v5_block4_x7.py`. Kill-tests: missing pointer; wrong sha256; fork; orphan harvest in the archive; second `none`; a second admission abort; an admission abort with another RECOVER cause; a second `s2`; an `s2` after a physics RECOVER; NULL restore with a two-row tail; NULL restore after `chain.started`. Positive paths: first attempt; NULL → fresh `s1`; admission abort → fresh `s1`; tooling RECOVER → `s2`. Run focused tests: `tests.test_v5_block4_x7 tests.test_v5_qualification_plan tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_x6 tests.test_v5_block4_replay tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout`. Use the shared git fixture helper for any git initialisation (`tests/test_git_fixture_maintenance.py` checks this). If a registry or lint test needs a registration for new code (read-replay allowlist, authentication IO surface, battery consumer list), register it honestly and say so.

Finish in this turn; FLAG what you cannot close.

WRITE_SCOPE: ["scripts/write_v5_qualification_plan.py", "scripts/harvest_v5_g2b_window.py", "scripts/harvest_v5_qualification.py", "scripts/restore_v5_null_reservation.py", "joulewise/v5_qualification.py", "tests/test_v5_block4_x7.py", "tests/test_v5_qualification_plan.py", "tests/test_harvest_v5_g2b_window.py", "tests/test_harvest_v5_qualification.py", "tests/test_v5_s1_qualification.py", "tests/fixtures/v5_qualification/**", "tests/fixtures/v5_qualification_harvest/**", "tests/fixtures/custody_read_replay_allowlist.json", "tests/test_authentication_io.py"]
