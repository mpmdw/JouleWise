FINAL PASS: MERGE

Cold Fable 5.1, P8 registration gate + merge final pass. Branch origin/feat/2026-09-30-revision6-integration @ 9f654a86 (merge-base = main 0009b976), detached worktree /Users/edr/code/JouleWise-wt-rev6fable-ff50b201. No loop context opened; no repo edits; python3 -B, TMPDIR=/private/tmp/jw-tests; no sudo/systemsetup/powermetrics/launchctl.

## 1. P8 registration: science-neutral, cap value exact
- Recursive diff R7 -> P8 (my own walker): /acceptance_id, /derivation_sha256, the one rotated pin (powermetrics_fiducial.py 386e8254 -> bcdfeec0), and derivation_notes (predecessor block, generation, reissue_delta, cap_change, measurement_licence). Members (17), statistics, identity_epoch, ledger_cutoff, prior_observation_set, decimal_derivation byte-equal. Other three pins unchanged from main (numstat empty); working-tree shasums equal P8's four pins and the pre-registration freeze.
- P8 file sha256 52e3d18a... equals the registry constant; `_valid_acceptance_bound` True for P8 and R7; ACTIVE = r8; R7 still registered and loads. Recorded issuance: delta report PROCEED, changed_pin_count 1, n17 statistics, CROSSCHECK=OK.
- N-1 re-run by me for members 1 (e941c821, window a) and 13 (a64711b7, the a9 archive-only member, now local and hash-authenticated a22005ea...): derived lexeme EQUAL to R7's and P8's member table, 59/59, admissible, cells 122,859 / 120,643 under the 1,710,000 cap. Record shows 17/17 EQUAL (N-1) and 38/38 (N-2).
- Cap: recomputed from 140-cap-rule/10-replay/replay.jsonl (100 rows, 0 failed, all SIZING, no B or bound key, max elapsed 18.9 s): 73 rows with a need (65 sizing + 8 check), N_max = 170,965 (w1-d03, sizing set A1), check-set max 132,137 < N_max; 10 x 170,965 = 1,709,650 -> next 10,000 = **1,710,000** = DETECTION_PROJECTION_CELL_BUDGET; R5 45 + 1,710,000 x 35 us = 104.85 s <= 120 s. Pre-registration (4d03d848, before the recorded replay) and run-info agree. 8 captures exceed the old cap = the 8 W1/W2 stops.

## 2. False-number / B-leak / admission paths: none found
- Harvest replays every capture in REPORT mode with compare_stored_bound=False (harness decodes "BLIND": b_fiducial_s never decoded, _stored_reproduced never called); R9 carries cells/frame/ratio/ledger disposition only. Wall-deadline replays retried x3 then refused, never a finding (R8(c)).
- Issuer: `revision_six_count_replay` requires every session terminal, uses ledger words + authenticated stored anchor outcome + R9 blind fields; `_prepare_candidate` refuses unless the decision is CLOSE_AND_DERIVE and the campaign R9 record is committed (line 2573-2576) BEFORE `_select_members` reads any member B (line 2716). Predecessor must be P8 by id, derivation digest and pins equal to the sealed declaration; policy digest REVISION_SIX_POLICY_SHA256 pinned; C = max(pred, Q99, Q99_within, S) in issuer (2793) and validator (df = n-K, sqrt(2), recomputed and compared in `_valid_acceptance_bound`). Counted = cells >= 1 and 100 <= frame <= 150 in a battery-pass window, as sealed.
- Cap change is the cap line + a two-line comment in the one pinned file (R1); literal R6 test asserts 1_710_000.

## 3. Revision 5 intact
Real W1/W2 prepare (night-custody ledger, 12 valid rows) through main's issuer with main's ACTIVE (R7) versus the branch issuer UNPATCHED (ACTIVE = P8): exit 0 both, **byte-identical** (sha 5d185cde...), n=12, revision 5, predecessor R7. The branch names R7 explicitly for Revision 5 (issuer :2615), not ACTIVE.

## 4. Tests
Focused modules (rev6, harvest, cap harness, P8 pin delta, rev5, bracketing, prewindow, fiducial, run_night, gen_derivation_night, epoch_continuation, capture_pipeline_era, issuer): 805 tests, OK (1 skipped), 707 s, rc=0.

## 5. Prune / fix before or right after merge (none blocks; none weakens a check)
1. `scripts/p8_evidence/full-suite.stdout.txt` (1.24 MB, 9,395 lines) and the other *.stdout.txt logs belong in the record directory (E1 §3.1 "in the record"), not under scripts/; keep n1.json, n2.json, r7_corpus_baseline.json, pin-classification.json, issuance.stdout.txt and the two scripts in the repo. Drop or relocate n2-first-attempt.* likewise.
2. Rule name: code comment, 20-value.md and P8's cap_change note say CAP-RULE-25G83-1; A1 §4.3 says CAP-RULE-25G83-2 "replaces -1 entirely". Value unaffected. Fix the comment/record now; P8's note is a digest-bearing field, so either re-run scripts/issue_p8_pin_delta.py (and move the constants) before merge, or record the misnomer in the record directory and leave P8 as issued. Lead's call.
3. Before the SEAL (step 12), not before this merge: prewindow_check.sh changed (check 8 now matches executable names via `ps -A -o comm=`; `--timeout-s` added; digest now d8458eea...). Sealable-e1 §6.2(g) and its JSON still describe "anywhere in a ps aux line" and argv `--wait` alone; the seal must pin the new digest and re-describe check 8 and the driver's `--wait --timeout-s` argv in the same edit (E1 §5 note 2 anticipated this).
4. Nit: `check` without --preregistration on an r6-named session runs the ordinary dry run, which parses member evidence (anchor keys only, no B value used or printed). Make it refuse or route to revision_six_dry_run.
5. Nit: issuer accepts any truthy `ledger_reason` for no-recording slots rather than the ledger's word.

Not executed: full suite, any live window, iCloud fetch, the derivation driver. Values of the 17 members were seen while checking N-1 and are not used in any ruling.
