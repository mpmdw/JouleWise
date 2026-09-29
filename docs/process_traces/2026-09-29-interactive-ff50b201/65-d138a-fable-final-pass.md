FINAL PASS: MERGE

Cold Fable 5.1 apex code-reading diff gate + overbuild/merge-ability prune (ledger rows 7, 8).
Head feat/2026-09-29-d138-loader-promotion e9827f33 (one commit on 9eab16f8). Detached worktree
/Users/edr/code/JouleWise-wt-d138afable-ff50b201; nothing edited, committed, pushed or merged.

Base check. `git diff --stat 9eab16f8 origin/main -- joulewise scripts tests configs` = tests/test_gen_state.py
only (+11/-2), disjoint from the seven files here; `git merge-tree --write-tree origin/main e9827f33` is clean.
Diff: joulewise/calibration_dispositions.py (new, 113 lines), calibration_bracketing.py (+31, four hunks),
issuer (-36/+9: constants moved, `_registered_dispositions` delegates), scripts/promote_calibration_candidate.py
(new, 233), three test files (+462). No configs/, pins, registry rows, generation rows, ACTIVE default or docs.
Issuer diff head vs source b953f4b0 confirms the R7 predecessor hunks (ANCHOR_V3_R7_* import, `requires r7
predecessor` equality, `--predecessor-acceptance` default) are NOT on this branch, as rulings 21/31 require.

Ran myself (python3 -B): dispositions + promote + bracketing + issuer + acc_25g83_rev5 + reissue = 287 tests OK
(1 skip). Loaded all 7 registry entries: all load, all import_only, none declares disposing_decision_ids, none
touches a D-126 content id, all os_build 25F84, ACTIVE = n17_r7. Registry at pin: 11 rows, one decision.

1. Shape for a second decision (CAP-W1W2-SET-ASIDE-01). Right shape, no redesign needed. DISPOSITION_DECISIONS
is a dict keyed by decision id with per-decision mechanism text and content-id set; the parser checks each row's
mechanism against ITS decision, `decisions_disposing` and `disposed_content_ids_for` union over decisions, and
the validator's declaration check (declared == sorted decisions whose rows touch the prior set) is exactly the
erratum's test 4. Issuer consumers (`_foreign_rows`, `_battery_computed_set`, `disposed_prior_ids`) are
membership-only and decision-agnostic, so the lane needs only: one table entry, 12 registry rows, one digest
re-pin, and the two comment rewordings the erratum already assigns to it ("diagnostics that can never be
members" at calibration_bracketing.py ~1040 docstring and ~2422). Nothing here that lane must undo.
Not premature: every hunk is exercised by a named test with a counterfactual. Missing: nothing required.
Nit: DISPOSITION_DECISION_ID and DISPOSITION_MECHANISM are imported into the issuer and unused (lines 114-115).

2. Stricter issuer parsing. `_registered_dispositions` runs only on the Revision 5 paths (check dry-run line
263 and prepare-candidate line 1791, both gated on target_epoch == REVISION_FIVE_EPOCH). On the pinned file the
new parser returns the identical 11-row dict (test d1; my script). The two new refusals (duplicate JSON key;
registry != code table under the production digest) can only fire on bytes that already fail the digest pin,
except a same-digest table drift in code, which is the repair's purpose. Refusal text changes slightly
("...invalid or duplicate row; not issued" replaces "...has an invalid or duplicate row"); nothing in tests or
contracts quotes the old text (git grep). Within the contract; no path running today changes result.

3. Promotion tool: KEEP. It is inert on main (no default output; --out/--check required; --issuance-text
required; nothing imports it; its output fails `load_calibration_acceptance_bound` and its id is not in the
registry, both asserted by test P1; --out refuses to overwrite different bytes). The owner's contract names it
explicitly and both cold rulings (A2 §3.5, E1 step 1 naming e9827f33) sequence it as step 1, with the
generalised tool a later lane whose regression is "given an r1 manifest, reproduce the r1 bytes byte for
byte"; the r1-shaped tool on main under test is that reference. Pruning would reopen a settled owner choice.
Follow-up (not a merge condition, light tier): the ruled issuance text and r1 bytes are not on main (only on
b953f4b0), so P1 now proves a synthetic round-trip, not reproduction of the ruled bytes (Opus nit confirmed).
When step 1's "filed in the record" commit lands the r1 bytes + 10-issuance-text.json, restore the digest
reproduction check against those record paths. Docstring "Promote the reviewed 25G83 candidate" is accurate.

4. Bearing on measured or published numbers: none. The validator block is dormant for all seven registered
files (import_only); the doubling exclusion set is empty for every artifact that declares no decision; the
issuer parse is identical on the pinned registry; no registered file judges 25G83, so every 25G83 bracket
still evaluates stale. No operative, screen, trigger or corpus output changes on main.

5. FINAL PASS: MERGE on e9827f33 as-is. Carry forward: (i) unused-import nit; (ii) P1 reproduction follow-up
after the record filing; (iii) the set-aside lane's comment rewording, already ruled in E1 §3.2 item 3.
