FINAL PASS: PASS

No BLOCKER or MAJOR. The three named modules pass on the head (159 tests, 1 skipped), and every regression the new tests are meant to catch is killed.

**Answers to the five questions**

1. **Acceptance, ledger, pin.** The bracket is judged against the plan's acceptance. The harvest loads the default acceptance, refuses unless its file sha256 and id equal the plan's `active_acceptance` (`scripts/harvest_g2a_window.py:176-181`), and builds the third view on the same `ledger` and the same pin as the last custody view (`:187-189`). For the real windows, both b3w1 plans (0526Z, 1305Z) match this checkout's acceptance by sha and id; the seed is 392 and the cutoff is 376.
2. **Custody.** Nothing is weakened. The seed-head and terminal-head views and their refusals are unchanged (`:151-172`). A ledger whose cutoff entry differs gives `calibration_ledger_baseline_missing` in the third view, and the decision returns failed (`calibration_bracketing.py:2206-2220`). Rollback and truncation are still caught by the first view against the committed pin.
3. **Wrong pass or fail.** I found no path to a wrong pass. A third view with refusals cannot reach `passed`, since every path through `calibration_bracket_for_bundles` hits the early return at `:2206`. The union line at `:222` is a no-op when the view is valid. The loader fills sessions regardless of refusals, so open-session and no-session paths behave as before (`bracket_incomplete`). In the 1305Z measurement clone's ledger (402 receipts, parses clean), the cutoff digest sits at sequence 376, so a re-harvest should not hit baseline-missing; I did not replay full custody.
4. **Tests.** In-memory mutation of the harvest (`/tmp/df31-fable/mutate.py`, no worktree edits):

   | Mutation | Killed by |
   |---|---|
   | Seed-head baseline in third view | `test_finalized_session_after_acceptance_cutoff_uses_separate_bracket_view` |
   | Seed digest only | same |
   | Third view on committed pin | same (error) |
   | Sha check removed | `test_bracket_acceptance_file_sha_must_match_frozen_plan` |
   | Id check removed | `test_bracket_acceptance_id_must_match_frozen_plan` |
   | Union line removed, or weakened to `reasons or snap.refusal_reasons` | `test_bracket_view_refusals_survive_a_decision_that_drops_them` |
   | Binding built despite refusals | `test_bracket_view_refusals_are_unfiltered_recovery_causes` |
   | Third snapshot removed | three tests |
   | `acceptance is None` clause removed | survives (see finding 5) |

5. **Other defects.** None that makes a verdict wrong.

**Findings**

1. **MINOR, `scripts/harvest_g2a_window.py:187-189, 222`.** A non-baseline refusal in the third view (custody invalid, malformed) becomes a RECOVER cause, while the same refusal in the first two views is REFUSED. Because the third view reads the same ledger, pin and mode, such a reason can only mean the sources changed between replays. The verdict is never SELECT and the governed pin advance re-authenticates, so this is not a wrong pass. It is pinned as intended by `test_bracket_view_refusals_are_unfiltered_recovery_causes`. Evidence: code read.

2. **MINOR, `scripts/harvest_g2a_window.py:176-179` and `calibration_bracketing.py:2153`.** The decision reloads the default acceptance itself and does not receive the object the harvest bound, so the file is read three times. This is safe: the loader authenticates bytes against the code-pinned registry (`:1304-1313`), and a divergent cutoff fails closed as baseline-missing. Evidence: code read.

3. **NIT, `tests/test_harvest_g2a_window.py` (`test_finalized_session_after_acceptance_cutoff_uses_separate_bracket_view`).** This is the only test that runs the real decision, and it uses the genesis fixture (cutoff sequence 0). Its bracket ends failed on synthetic captures (`instrument_calibration_bracket_missing`, `capture_pipeline_superseded`). It does prove the baseline check is passed, but no test drives the real decision to `passed` through the harvest with a non-zero cutoff. Evidence: `/tmp/df31-fable/probe.py` output showing baseline 0, head 14, binding present, 24/24 members valid.

4. **NIT, `scripts/harvest_g2a_window.py:211-222`.** The union runs only for finalized sessions. An aborted or open session with a missing cutoff entry reports only `bracket_incomplete`. The verdict is RECOVER either way.

5. **NIT, `scripts/harvest_g2a_window.py:178`.** The surviving mutant is benign: without the `None` clause the harvest still ends REFUSED, with a different cause code (`archive_or_authentication_fault`).

6. **NIT, `scripts/harvest_g2a_window.py:176-181`.** The acceptance binding also refuses windows with no session or an open session, before session closure. This matches what `check_harvest_inputs` already enforces in the measurement clone (`generate_g2a_probe_inputs.py:1320`), so there is no new exposure when the harvest checkout and clone agree.

**The second commit's line (`:222`)** is correct. With zero valid members the decision returns only `instrument_calibration_bracket_missing` (`calibration_bracketing.py:2787-2797`); the union puts the snapshot's codes first and deduplicates, and cannot turn a pass into a fail.
