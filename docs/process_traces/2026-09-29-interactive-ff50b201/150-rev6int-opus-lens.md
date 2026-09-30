LENS: FINDINGS

Opus 5.5 read-only contract lens. Branch origin/feat/2026-09-30-revision6-integration @1b419f0e, worktree /Users/edr/code/JouleWise-wt-rev6lens-ff50b201. Probes: scratchpad/rev6lens/probe_replay.py plus inline python3 -B. Suites tests.test_acc_25g83_rev6, test_harvest_window, test_cap_replay_harness, test_issue_p8_pin_delta, test_acc_25g83_rev5, test_calibration_bracketing and test_prewindow_check all pass (OK, 1 skip). They pass only because of the mocks named in B1. No repo file modified.

WHAT MATCHES THE CONTRACT
(1) Cap and R6 match. powermetrics_fiducial.py:90 is 1_710_000, which is 10 x 170,965 rounded up (R3). R5 arithmetic: 104.85 s. The diff to that file is the cap line and its comment only (R1). The other three estimator files are unchanged. R6(i) is re-pinned (test_powermetrics_fiducial.py:577-579), R6(ii) is untouched, and R6(iii) is new; it prints elapsed time and does not assert it.
(2) P8 matches. The recursive diff from R7 to P8 is exactly acceptance_id, derivation_sha256, the powermetrics_fiducial.py pin and derivation_notes. The P8 pin equals the file on disk. `_valid_acceptance_bound` returns True for both P8 and R7, and the operatives are equal. All N-5 wiring is present (constants, registry row, generation row with its comment, ACTIVE/DEFAULT, EXPECTED, _issued_d079, schema_v2 enum, the moved test pins). The "stays on R7" items are held explicitly on R7. The recorded verifier shows the n17 statistics and CROSSCHECK=OK.
(3) The issuer's JSON policy matches. `REVISION_SIX_POLICY_SHA256` equals the canonical hash of the policy objects in 32-revision6-sealable-e1.md. Verified:
    - clause order 0-6;
    - T-count and T-members;
    - 3 counting windows, 1 battery replacement, 4 windows in all;
    - all eight stop predicates. STOP-R9-* are read on adverse windows; STOP-R9-RATIO covers out-of-range captures;
    - no session is allowed after a non-NEXT decision;
    - C = max(predecessor C, Q99, Q99_within, S), in both the issuer and the validator;
    - the Q99_within rule string is verbatim, with df = n-K and K = windows that contribute a member;
    - amendment-T timing;
    - B is read only after CLOSE_AND_DERIVE, with all sessions terminal and the R9 bytes committed at HEAD.
(5) The definition of "counted" is correct. Sealed §0 and §7 `definitions.counted_capture` both say: in a counting window, harness cells >= 1, and median frame from 100 ms to 150 ms inclusive. A1 R9 says the same. So the code's frame test is what the sealed text requires. "valid" is the ledger's valid count over counting windows, and harvest and issuer agree on it.
(6) The Revision 5 text is not edited. For Rev5 behaviour, see S6.

BLOCKER
B1. Harvest and issuer use different disposition words, so any real window with an invalid recorded capture is refused.
    - harvest_window.py:132 writes the harness word (cap_replay_harness.py:146,199: valid, invalid, clock_anchor_unresolved, detection_nonconvergent, not_replayed).
    - issue_calibration_acceptance_generation.py:1534 requires that word to equal the ledger's classification_disposition (valid, ordinary-invalid, systematic-invalid, unresolved).
    - Probe (revision_six_count_replay): ledger "ordinary-invalid" paired with R9 "invalid" is REFUSED. The same happens with "clock_anchor_unresolved". All-valid gives NEXT_WINDOW.
    - W1/W2 had many invalid captures, so the count-only dry run and prepare would refuse after most real windows.
    - The tests hide this. test_harvest_window.py:144-148 mocks the harness to return ledger words. tests/fixtures/epoch_bootstrap/revision6.py:79 builds R9 records from ledger dispositions. No test runs harvest into the issuer.
    - It fails closed and cannot produce a false number, but the Revision 6 count rule cannot run on real windows.

SHOULD-FIX
S1. A slot with no recording is refused. harvest_window.py:120 writes cells, ratio and frame as null. The issuer at :1540 refuses with "R9 cells malformed" (probe P4). Sealed §4 says such a slot is listed with its ledger reason, not counted, and fires no stop. Harvest also writes no ledger-reason field.
S2. Null sessions have no producer. Harvest refuses a refused start record (:311) and a window with no finalized slot (:170), and nothing ever writes `abort_reason`. The issuer needs a harvest record and an R9 record for every session. Clause 0 and STOP-NULL-REPEAT therefore work only in the fixture, and a real null session makes the campaign unissuable.
S3. A replay's wall-deadline stop becomes a capture finding. This contradicts R8(c): "In a replay, a stop on the wall deadline is a failed replay ... repeated ... never a finding". Harvest copies the replay's trigger (:126) and ignores `replay_failed` (harness :206), with no repeat. The issuer then fires STOP-R9-DEADLINE with campaign_void=True (probe P5). A busy harvest machine could void a campaign wrongly.
S4. Start condition (b) is not evidenced. run_night.py:3105 points `b_blind_checks` at the same prior-session manifest as (a). That manifest has no count-rule decision; its prior timestamps come from operator arguments (gen_derivation_night.py). For Revision 6, harvest prints COUNTS_ONLY on a CELL, DEADLINE or RATIO stop (:384). Result: window k+1 can be armed and run after a STOP. Only issuance catches it (§6.2(b) is violated at start).
S5. Clean-dwell order and argv differ from the sealed text.
    - The dwell runs after the night gate's t0 checks, inside the OFF settle (run_night.py:3488). §6.2(g) says "Before t0". So the thermal (d) and battery (e) gate evidence can be about 45 min older than chain start.
    - The argv adds `--timeout-s <=2700` (:3222); the registered argv is `scripts/prewindow_check.sh --wait` with a 45-min default. This only shortens the timeout, but the pinned script gained an option.
S6. Revision 6 mode is chosen by an operator-chosen ID prefix (issuer :481, :2437), and the generator does not enforce the r6 pattern. At the same time the Revision 5 predecessor gate moved from R7 to ACTIVE, which is now P8 (:2502).
    - Effect: sessions opened after the pin but named without "r6" would take the Rev5 path with P8 accepted. That path has no R9 check, no start-condition checks and no Q99_within in C.
    - I did not run this route end to end.
    - The Rev5 test patches ACTIVE back to R7 (test_acc_25g83_rev5.py setUp), so production Rev5 behaviour is not what is tested.
S7. The single R9 record that sealed §4 requires is not produced. §4 asks for one committed file with verdicts on the five clauses and the digests of the harness and of the cap-rule text; §5 adds the clock-movement refusals listed by slot. Only the per-window r9_window.json exists, and it has no cap-rule-text digest. The pins cap_rule_text, roster, chain and validator are only format-checked (issuer :1159). The interface itself says the sealed text wins.

NITS
N1. Rule name. Code, the value record and P8's cap_change note say CAP-RULE-25G83-1. Rev6 §0/§5, A1, E1 §3.4 and the harness docstring say -2.
N2. E1 step 9 puts the P8 script in the record directory. It lives in scripts/issue_p8_pin_delta.py and scripts/p8_evidence/.
N3. calibration_bracketing.py:1121 imports a scripts module lazily, and an ImportError is not caught. It fails closed (crash).
N4. Harvest copies boot_id from the start record, so a reboot before chain exit cannot be seen. The timing is report-only.
N5. A null session requires state=="aborted" (:1514); the sealed text says "terminal". This is stricter and fails closed.

(7) Could a measured or published number be false? No path found that issues a wrong number on the Revision 6 route: every mismatch above refuses. Two exceptions:
    - S3 can void a campaign wrongly.
    - S6 is the one plausible route to a successor issued without the R9, start-condition and Q99_within gates. I did not execute it.
