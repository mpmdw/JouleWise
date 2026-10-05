# Block-4 lane X12a round 2 (Sol 6.1 xhigh): executing-review findings D2, D4, D5 and C2 (addendum F item 10)

Worktree: /Users/edr/code/JouleWise-wt-dd5-x12a (branch `lane/2026-10-05-b4-x12a`; round 1 committed). Scratch /tmp/dd5-x12a/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal. Never touch the four pinned estimator files.

The executing review at 6796b8e0 (`/Users/edr/night-archive/desk-day-v5/sol-intrev2.md`; reproducers under `/tmp/dd5-intrev2/`) found the following. Each must be fixed, with a regression test that fails at your round-1 head and passes after.

- **D2** (`joulewise/v5_qualification.py:~170`): an admission abort is re-armable only if no other RECOVER cause is present in the attempt. Successful members must face the normal physics assessment, including clock-anchor status. One successful member with an unbounded clock, followed by an admission abort, is RECOVER with the physics cause. It is not re-armable and goes to END STATE per registration §7. Reuse the existing assessment; do not write a second one.
- **D4** (`scripts/harvest_v5_g2b_window.py:~506`): an observation-producer fault never enters the structural cause set (ruling 76 decision 5; registration §6, "a producer fault cannot ... turn the structural verdict into RECOVER"). It belongs to the qualification verdict only. Test: an admission abort plus an observer write fault stays a re-armable admission abort structurally.
- **D5** (`joulewise/v5_qualification.py:~308`): two consecutive attempts that end NULL with the same refusal code set send the next spend to the consult. The writer refuses a third attempt (`same_refusal_twice`) and names the codes. A different code on the second NULL does not trigger this. The comparison uses the nearest attempts, consistent with the nearest-non-NULL rule from round 1. Here both records are NULL, so compare the two NULL records directly.
- **C2**: a regression test that a single-row substitution in the stage list is refused by the digest guard. The existing test changes a duplicated row and does not kill the digest-guard deletion mutant. See `/tmp/dd5-intrev2/` for the scratch test that does.

Run the round-1 module list plus your new tests. Finish in this turn.

WRITE_SCOPE: ["joulewise/v5_qualification.py", "scripts/harvest_v5_g2b_window.py", "scripts/harvest_v5_qualification.py", "scripts/write_v5_qualification_plan.py", "tests/test_v5_block4_x12a.py", "tests/test_v5_block4_x7.py", "tests/test_harvest_v5_g2b_window.py", "tests/test_launch_window.py", "tests/fixtures/v5_qualification/**", "tests/fixtures/v5_qualification_harvest/**"]
