# PR #800 round 9 controller repairs

The user selected the four cold-review findings ahead of the ordinary [AGENT] queue. Mission M0 found no active stop card and clean branches at PR #799 `69931e529` and PR #800 `9dc15c473`. The refusal is recorded in `COLD-REVIEW.md` from the round 9 review directory. RL-172(c)(g) and RL-173 A and E govern this work. No phase exit-checklist item closed.

PR #799 was repaired and pushed first at `28ceeaba9`. PR #800 was rebased onto it using the established linear stack. Both sides' handoff entries were preserved in the rebase. The original controller implementation and affected test file were byte-identical to the rebased versions before the regressions were added.

| Finding | Repair and regression |
| --- | --- |
| F1 | Gate the ledger's latest declared hand-armed predecessor on its own identity-matched receipt and source-bound copy marker. The missing-receipt, wrong campaign directory and newer unrelated receipt cases exercise the real census in `Gate6Controller`. |
| F2 | Require a valid standing fence at child entry, verify that exact record under the transfer lock, and require the transferred launch record at bootstrap. `ArmChildRealPin` exercises the frozen launcher and a fake launchctl. `ArmChild` covers loss before the locked read, replacement after that read, loss before bootstrap, and expiry. |
| F3 | Inspect the ordered restore and feed-close records. `Gate6Controller.test_duplicate_prior_restore_stages_hold_despite_successful_last_stage` covers both a failed stage followed by success and two successful duplicates. |
| F4 | Inherit the checked signed-history enumeration and `SignedTransport.test_failed_history_listing_refuses_signed_desk_final` from PR #799. |

Each finding's regression failed on the original implementation. All 21 focused controller and arm-child checks pass. The guarded cadence run excludes the 12 cases in `test_launch_cadence_span.py` that signal live fixture processes. The user narrowed the run to cadence. The final suite result and workflow runs are tracked on [PR #800](https://github.com/mpmdw/JouleWise/pull/800). The fixture-orphan census could not observe the process table because the environment denied `ps`.

Fresh admission and live gates remain lead-owned.
