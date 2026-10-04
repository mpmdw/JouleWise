# R3 fix seat: G2-a harvest builds the bracket ledger view from the wrong baseline (b3w1 RECOVER)

Repository worktree: /Users/edr/code/JouleWise-wt-df31-fix (branch fix/2026-10-04-g2a-b3w1-bracket-baseline, based on main a6c7f9cf). Commit your work on this branch. Do not push; the lead pushes.

## The fault
Block-3 window `b3w1` (plan `d117-g2a-prefill-probe-20261004T1305Z`) ran with chain exit 0, and its bracket session finalized. This is the first G2-a window whose session reached `finalized`; block 2's windows all stopped at `bracket_incomplete`. `scripts/harvest_g2a_window.py` returned verdict RECOVER, and its only cause code is `calibration_ledger_baseline_missing`. That code comes from `joulewise/calibration_bracketing.py` around lines 2208-2220. The bracket decision requires `ledger_snapshot.baseline_sequence/baseline_digest` to equal the acceptance artifact's `ledger_cutoff`. The acceptance in force, `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, has cutoff sequence 376.

The harvest builds both of its snapshots (lines ~150-167) with `baseline_sequence/baseline_digest` = the frozen calibration plan's `calibration_ledger.head_sequence/head_digest`, which is the window's seed head (392). It then passes that snapshot to `brackets.build_calibration_bracket_binding` and `brackets.calibration_bracket_for_bundles` (lines ~187-197). Every other bracket or ledger caller instead uses the acceptance cutoff as the baseline: `joulewise/whole_window.py:507-522`, `scripts/run_campaign.py:~4819-4834`, and the G2-a input generator's own `_authenticate_ledger_and_acceptance` (`scripts/generate_g2a_probe_inputs.py:~677-690`). The registration (`configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md` §6) says the brackets pass "when the existing bracketing decision (`joulewise/calibration_bracketing.py`, against the acceptance in force) admits both". So the harvest disagrees with the registration, and registration §11 lets an ordinary gated PR fix it.

## What to do
1. In `scripts/harvest_g2a_window.py`, keep the existing seed-head authentication. The first snapshot against the committed pin, with the frozen seed head as baseline, and the terminal-head scratch-pin authentication are real custody checks; do not weaken them. Then build the ledger view used for the bracket (session lookup, `build_calibration_bracket_binding`, `calibration_bracket_for_bundles`) with baseline = the `ledger_cutoff` of the acceptance artifact the bracket decision itself uses. `calibration_bracket_for_bundles` is called without `acceptance_bound`, so that artifact is `load_calibration_acceptance_bound()`. Use the same pin, path and mode as the snapshot it replaces.
2. Bind the acceptance. Refuse (a `HarvestRefusal` with a new, specific code) unless the acceptance the bracket uses is the one the window was planned under. Its sha256 must equal the frozen `calibration_plan.json` `active_acceptance.sha256`, using the same sha function the generator used to write that field (find it; do not guess), and its id must equal `active_acceptance.acceptance_id`. If the generator or harvest inputs check already enforces this, cite where and do not duplicate it.
3. If the bracket-view snapshot has any `refusal_reasons`, keep today's behaviour: let the bracket decision return them as RECOVER causes. Do not convert them to REFUSED, and do not filter them.
4. Read `_prior_set_matches_import_cutoff_prefix` and anything else downstream of the baseline check in `calibration_bracket_for_bundles`. Find out whether a ledger whose head is past the cutoff (here 402 > 376, with the window's own bracket session appended) is meant to pass those checks, as it does on the Revision 6 path. If some later check would also wrongly refuse a G2-a window for a tooling reason, report it with file:line, and fix it only if the fix lies within the write scope below.
5. Tests in `tests/test_harvest_g2a_window.py`:
   - a regression in which the fixture ledger's seed head is past the acceptance cutoff and the bracket session is finalized. It must reach the bracket decision without `calibration_ledger_baseline_missing`. Build the ledger the way existing fixtures do; if no fixture can finalize a session, say so and add the narrowest one that can;
   - a negative test: an acceptance whose sha differs from `active_acceptance.sha256` refuses with the new code;
   - all existing tests in the file still pass.

   Run that file plus `tests/test_calibration_bracketing.py` and `tests/test_generate_g2a_probe_inputs.py` (if present). If you add or change any file the custody replay reads, update `tests/fixtures/custody_read_replay_allowlist.json` as commit 9e2b1004 did, and run its consuming test.
6. **Real-data bracket replay (mandatory; this is how we avoid a serial RECOVER).**
   - Copy what the bracket decision reads, read-only from the sources, into `/tmp/g2a-b3w1-replay-df31/`. The archive is `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/` (its `g2a-root/` and `physical-ledger/`), the live tree is `/Users/edr/night-g2a/d117-g2a-prefill-probe-20261004T1305Z/`, and the measurement clone is `/Users/edr/night-custody/measurement/JouleWise-measurement-20261004T1305Z-g2a-b3w1`.
   - Run, with this branch's code, ONLY the bracket path: snapshot, then binding, then `calibration_bracket_for_bundles`.
   - **Blindness (registration §10):** report ONLY the returned `status` string and the reason-code tuple. Do NOT print, log or report the assessment's numeric fields (drift, fiducial, window times), any member count, `counts.json`, `summary.json`, or a selection. Do not run the summarizer or the selector.
   - If the reasons are another tooling refusal of the same kind (a provenance, binding or authentication code), diagnose it and fix it within scope. If the status is `passed`, or a failure that is a measured outcome (drift over the allowance, acceptance stale by age), that is correct behaviour: report the code and change nothing.
   - NEVER write under `/Users/edr/night-g2a`, `/Users/edr/night-custody`, or `/Users/edr/night-archive`.

## Write scope (exhaustive)
WRITE_SCOPE: ["scripts/harvest_g2a_window.py", "tests/test_harvest_g2a_window.py", "tests/fixtures/custody_read_replay_allowlist.json"]
Scratch outside the repository: the lead authorizes writes under /tmp/g2a-b3w1-replay-df31/ for the replay copy only (not a repository write).
Do not touch `joulewise/` package code, other scripts, configs, registrations, or the calibration ledger. If the right fix needs one of those, stop and report why.

## Report
End with: the files changed; the commit sha; test commands with pass counts; the replay command and its status and reason codes only; and any finding outside scope (file:line).
