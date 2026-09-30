# FINAL PASS: MERGE

Cold Fable 5.1 on feat/2026-09-29-w1w2-set-aside head 2e805699 (lane CAP-W1W2-SET-ASIDE-01), against erratum E1 §3.2 and §4 step 3. Detached worktree at 2e805699; nothing edited, committed or pushed.

What I checked myself (not re-doing the two prior passes):
- Mechanism text: extracted the quoted string from the ruling file and compared to the code constant in Python: byte-equal. All 12 JSON rows carry it and each identifier is in the code table. No "diagnostic" / "never a member" label anywhere except the mandated "not a diagnostic" clause; grep of joulewise/, scripts/ and the three test files finds none.
- Registry: 23 rows, two decision IDs; sha256 equals the new pin 4a3d96da…effd; main's 11 rows (ba1ba3fc…) are the exact prefix; the 12 and the 11 are disjoint; parse_disposition_registry at the pin returns 23.
- Primary identity: tests/verify_w1w2_disposition_sources against the two harvest archives prints W1W2_PRIMARY_IDENTITIES=PASS valid=12 registry=12.
- Tests: the four required modules, 278 tests, OK (skipped=1); the live identity probe passes here.
- Prohibitions: scripts/ untouched (git diff --stat empty); _foreign_rows (issuer :1403) and the A-7 refusal unchanged; calibration_bracketing.py changed by comment only; old file digest a2620ba4… pinned nowhere in code, config or docs.

(1) Exactly §3.2? Yes: items 1–4 all present. Beyond §3.2: the module docstring drops "D-126" (necessary, two decisions now), and two verification scripts under tests/. Neither alters behaviour. Item 3 said "two comments"; one two-line block existed and nothing stale remains.

(2) Any number false, any W1/W2 row a member? No. No estimator, pinned file, member table or registered artifact changed; 7 generations load identical to main. Membership: the validator (bracketing :981–992) requires the declared decisions to equal decisions_disposing(prior_ids), so the E1 decision must be declared whenever the 12 sit in the prior set, and then any disposed content_id that is a member is refused. The issuer test shows the 12 excluded from a 24-member candidate and a thirteenth valid same-epoch row still refused.

(3) Reviewer's side effects:
 (a) W1/W2 sessions leave the battery-verdict set S via the existing rule at issuer :1360. No number depends on their verdicts because they are not members; it is how the D-126 rows already behave. Note for the cap transaction record only.
 (b) Issuer :2032 refuses a Revision 5 successor whose prior set lacks any of the 23. Fails closed; the ledger already carries the 12. Note only; the step 12 registration names them by identifier anyway.
 (c) Validator file bytes moved (comment). Step 12 already orders "if re-pinned, the validator digest then in force" after step 3 is on main; no existing pin breaks. Note only: take any validator digest at or after this merge.
None needs action before merge.

(4) Verdict: FINAL PASS: MERGE. Sequencing constraint carried from §4: this lands after step 1 (it does: 054511ef holds the loader/promotion module) and before step 12.
