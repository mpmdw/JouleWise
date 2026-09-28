# Activation 77b1bee2 — 11:36 PDT 09-27 (Opus 5.5 magistrate)

1. **Launch** 11:36:14 (watchdog attempt 123; `last_exit_class` = `usage_exhausted`). Heartbeat written first (`resident_session.pid` 91957). `notice_pending` = [`transition-514-hold_census` at 09:00:33 PDT, "production census non-empty inside plan span"]. The census rows in `events.jsonl` show only W2's own driver (`run_night.py run --plan …/d079-epoch-25g83-derivation-w2-20260927/night_plan.json`, PID 90113), present from t0 until ≈11:06, when the census went empty and the watchdog moved HOLD_CENSUS → FENCED; benign. Night agents `com.joulewise.night` and `.deadman` are still loaded (W2 not yet harvested/uninstalled), so no git operation touches the canonical root. No standdown or STOP file. Directives unchanged (#422 #421 #417 and the standing set).
2. **Owner instruction (Gmail message `1a0e3f5f40b48642`, thread `1a0e25449a3aa211`, 10:42 PDT 09-27), verbatim**, replying to the W1 harvest email's quoted item 2 (the chain-log read before the battery-verdict commit):

   > You can override this, this is a remnant overengineered process to stop someone
   > altering the data which no one would really do, that's an earnest mistake not
   > someone trying to cheat the science

   **Applied:** the W1 ordering slip (3ba66eeb) is closed as accepted by Ed; it needs no further disclosure action beyond this record. Ed's text permits overriding that read-after-commit ordering; it does not require it, and this activation does not amend the runbook (rule 11: a process change goes to the cold gate or Ed). For the W2 harvest the documented order is followed anyway because it costs nothing. A runbook simplification lane, HARVEST-ORDER-SIMPLIFY-01, is registered for Ed/cold-gate ratification, citing this item.
3. **Launch email** accepted: Gmail `1a0e42883e977e7c`. `notice.ack` written. Ed's message `1a0e3f5f40b48642` marked read after item 2 was committed (`c57c8589`).
4. **W2 night outcome** (no measured value read). From `night.log` and `night/result.json`: the driver started at 09:00:01.79 PDT; gate verdict GO; chain digest verified. The result verdict was GO at 11:03:45, with `chain_exit_code` 0, `receipt_class` DIAGNOSTIC_NO_PACK, 248 censuses and 0 hits. The durable record was pushed to `night-results/d079-epoch-25g83-derivation-w2-20260927`. The courier sent Gmail `1a0e40aaa7d2cf5c` at 11:05:03. The harvest began at 11:38, after the 11:35 completion boundary.
5. **§2.1 preservation.** The custody root was copied byte-exact (`cp -Rp`; `diff -r` identical) to `~/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/`, with an lstat inventory (`lstat-inventory-ns.txt`, 11,266 rows, size, `mtime_ns` and mode taken from the original). The W2 clone's `runs/` (the ledger) was copied to `measurement-runs/`, also `diff -r` identical.
6. **Documented uninstall.** From the measurement root, `scripts/install_night_agent.sh --plan <NIGHT_ROOT>/night_plan.json --uninstall` returned rc 0 with empty output. Only `com.joulewise.magistrate` is loaded, and no `com.joulewise.night*` plist remains. Canonical `git pull --ff-only`: already current at `670756f3`.
7. **§2.0 + §2.2a, in order** (evidence in `10-w2-harvest/`). The inputs checked first: HEAD = H `a71a5e79`; `chain.zsh.sha256` OK; the plan's `custody_root` = NIGHT_ROOT; the pre-registration sha256 = `81b65f08…ddf1`.
   - (i) `terminal-pin` gives 276/`476e2ae8…9737`. `advance-head-pin` (operator `magistrate-77b1bee2`) ran as a dry run (rc 0) and then with `--execute` (rc 0), moving the pin from 226/`bd7aee7a…6693` to 276/`476e2ae8…9737`.
   - (iii) `battery-verdict` printed **`d079-epoch-25g83-derivation-w2-20260927: battery=pass`**, rc 0.
   - (iv) One commit, **`722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`** (parent `a71a5e79`), holds the pin and the verdict file. It is pushed as `harvest/2026-09-27-w2-pin-verdict`, and `git log --full-history` on the verdict path shows that one commit only.
   - (v) Harvest line: `d079-epoch-25g83-derivation-w2-20260927: battery=pass verdict_sha256=51f4961828a440cbab5c7cf504d7e4536b25243414441dab5fedfb6f28f946ec verdict_commit=722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`.
   - (vi) The cadence report returned rc 0: 12 captures, median native frame 128.47 ms, max 141.39 ms, median of capture medians 129.30 ms, **R5(n) CONTINUE** (the stop line is 150 ms). This is a disclosed diagnostic for a daytime window (arm-gate NIT-6).
   - (vii) `check --session-ids <W2>` alone returned rc 5. That is the expected mid-campaign A-7 blocker ("6 rows owned by …w1…"), not a fault. `check --session-ids <W1> --session-ids <W2>` (the flag repeats; a comma list is read as one absent id) returned **rc 0**. Each window shows `battery=pass recorded=pass`, `finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`, and prefix pending 0. **Registration admissible for prepare-candidate: yes.**
   - **Manual cross-check** (lane BATTERY-VALIDATOR-PROBE-ERROR-01): all 24 readings have `probe_error=false`, `passed=true`, `is_charging=false`, `external_connected=true` and `instant_amperage_ma=0`, with exit 0 and no timeout. Each raw ioreg's sha256 matches its recorded fingerprint. 0 failures.
   - (viii) The slot-disposition count was read only after (vii), from the dry run itself: 6 valid of 12.

   **W2 is ADMITTED.**
8. **Science consequence.** W1 and W2 together hold **12 valid** derivation captures. That is the n ≥ 12 the registration needs for issuance, so on count W3 is not needed, and REV5-POST-W3-SHORTFALL-01 is moot unless issuance is blocked for another reason. Directive #416 is now live: a blind full-system audit by three model families (Astra xhigh, Fable, Opus xhigh) must come after W1/W2 pass and before any claim-bearing run. Ed must be pinged to close interactive sessions before any t0. The next science steps are `prepare-candidate`/issuance under Revision 5 and the #416 audit. Their order and gates are for the next slice to read from the registration and the directive.
9. **Correction to item 8 (directive #416 trigger).** In #416 as amended, the audit trigger is "CLAIM-RUN WORK COMPLETE", which means W1/W2 are **issued** and the headline pipeline is frozen. It is not triggered merely by W1/W2 passing. So the order is:
   1. The harvest PR merges.
   2. `prepare-candidate` runs under Revision 5, then the cold science gate, then the D-138 issuance transaction. The runbook's §4 text is the three-night FAIL route, so the Revision 5 flag set comes from the registration text; the contract lens was asked about it.
   3. The headline pipeline freezes, after S1–S4 and BFGS-COOLDOWN-ANCHOR-01.
   4. The #416 audit follows, and its auditors re-derive W1/W2 from the raw bundles.
   5. Only then does a claim-bearing run happen.
10. **Harvest PR #434 gate, first two lenses.**
    - **Row 1 + row 2 (execution lens):** Sol 6.0 high, [11-sol-audit-report.md](20-harvest-gate/11-sol-audit-report.md). **AUDIT: PASS**, with 0 findings.
      - It confirmed rows 227–276 are all W2 and rows 1–226 are byte-identical to W1's ledger.
      - The pin and the verdict re-derive byte-exact.
      - It read all 24 raw ioreg files: 0 mA, not charging, external power connected.
      - Its one residual risk is already disclosed by A-R5b: a charging excursion that falls entirely between the two endpoint readings of a slot cannot be seen.
    - **Row 2 (contract lens) + row 6:** Opus 5.5, [12-opus-contract-lens.md](20-harvest-gate/12-opus-contract-lens.md). **CONTRACT LENS: PASS**, with 0 BLOCKER. Dispositions:
      - **S1** (merge commit only): adopted. The merge uses `gh pr merge 434 --merge`.
      - **S2** (harvest notice content): the notice had already gone out, as Gmail `1a0e42d7ad74be5f`, carrying both battery lines. A **correction was sent as Gmail `1a0e43cab8a8ea93`**. It says W3 is *not permitted* (prereg: permitted only if fewer than 12 valid after W2; the issuer refuses it, `issue_…py:1838`), that n = 12 has zero margin, that the yield was 50 % against ≈79 % assumed, and that there is no top-up.
      - **Item 8 is corrected:** "W3 not needed" should read **"W3 not permitted"**. REV5-POST-W3-SHORTFALL-01 is **not moot**: it governs what happens if `prepare-candidate` refuses after W2, and that goes to Ed or a cold gate **before** `prepare-candidate` runs.
      - **S3** (`prepare-candidate` preconditions): these are carried into the issuance lane brief. Record the five checks no tool performs (6 h spacing, Interactive launch context, MLX 0.31.2 on every row, estimator code unchanged, Revision 3 chain digest). Use an estimator-unchanged head. Name W1 and then W2, with no confounded session and with `--d125-ruling`. Keep both custody roots in place.
      - **NITs:** the cross-check script is now kept as `10-w2-harvest/manual-battery-crosscheck.py`. Item 7's "(i)" label for the pin advance is the runbook's own (i), "§2.0 done / ledger at head-equals-pin", which is where the pin advance sits, as at W1. The probe-plist render/install digest pattern and the runbook's missing merge-commit-only rule go to the lane list (HARVEST-RUNBOOK-MERGE-METHOD-01, PROBE-PLIST-DIGEST-PATTERN-01).
11. **PR #434 row 7: the cold Fable 5.1 final pass ruled `VERDICT: MERGE`** ([22-fable-finalpass-ruling.md](20-harvest-gate/22-fable-finalpass-ruling.md); convened 11:5x from worktree `JouleWise-wt-harvest-fp-77b1bee2` @ `722f7bd1`, rc 0). It found 0 BLOCKER. SHOULD-FIX items and their dispositions:
    - **S1** (merge commit only; the ledger rows were PENDING): the merge uses `--merge`, and the PR body is updated before the merge.
    - **S2a:** the first owner notice put issuance after the #416 audit. That is wrong: the #416 trigger is W1/W2 *issued* plus the headline pipeline frozen (item 9). A correction goes out in the next email.
    - **S2b:** #416 clause 3 says W1/W2 are re-run if the audit finds a derivation defect. Revision 5 has no window left, so a re-run would need a new registration. Ed has not been told this; he is told in the same email.
    - **S3:** before `prepare-candidate`, a **refusal statement**: what happens if issuance refuses after W2. This is REV5-POST-W3-SHORTFALL-01 in light form, ruling §4.4. It goes to Ed or a cold gate together with the contract lens's S3 list (ruling §4.5 names who settles each item).
    - **S4 (new): the battery gauge's capacity figures stepped +12 mAh between d05 post (gauge time 09:52:45) and d06 pre (09:59:45).** `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` and `NominalChargeCapacity` each rose by 12. Voltage held at 12890 mV, and instantaneous and charging current were 0 at both readings. **Executed follow-up (the judge's NOT EXECUTED item):** `pmset -g log` for 2026-09-27 has **no charge, battery or AC-source event anywhere in the day**. Between 09:40 and 10:09 it shows only routine assertion summaries, cloudd network tasks, and one powerd darkwake inactivity-model query at 09:59:59 ([pmset-log-0940-1009.txt](10-w2-harvest/pmset-log-0940-1009.txt)). This is consistent with a gauge re-estimate, not charging. The registered verdict is defined on the endpoint readings and stands either way; the step is disclosed to Ed.
    - **NITs** (six): these are listed in the ruling and go to the lane list with the contract-lens NITs.
12. **Cold gate REV5-REFUSAL-BRANCH-01** (Fable 5.1, 12:10–12:19; [charge](40-refusal-branch/20-coldgate-charge.md), [ruling](40-refusal-branch/21-coldgate-fable-ruling.md)): **RULING: RATIFY-AMENDED**. Owner points (a)–(c) are approved and amended into a ten-item statement (§5). A cold gate suffices, because the statement only restricts.
    - **Paired Opus 5.5 refuter** ([22-opus-refuter.md](40-refusal-branch/22-opus-refuter.md)): **REFUTER: CONCUR**, with 0 BLOCKER and SF-1–SF-3 plus N-a–N-d.
    - **SF-1: `prepare-candidate` will certainly refuse on its first run, before any B value is read.** Every W1/W2 `custody_locator` is `/Users/edr/night-custody/…/runs/instrument_validation/<attempt>`, which lies outside every git checkout. `_select_members` → `_repo_relative_custody` (`issue_calibration_acceptance_generation.py:896–912`, called at :1244) raises "custody … lies outside the repository, so no repo-relative source_directory exists". The refuter ran the issuer's own function on both prefixes, and both refused. The dry run does not mirror this check ("List B, not mirrored").
      - The cure is a code change with a design decision: how do issued members stay verifiable when `tests/verify_calibration_acceptance_corpus.py` joins `repo_root / source_directory`?
      - Moving, copying or re-rooting the custody tree, or creating a git repository above it, is never a cure.
      - SF-1 also changes the ruling's "if no ruling is given, terminal" to "held until ruled".
    - SF-2 fixes the `--d125-ruling` text (the 2026-09-25 D-125 addendum) and the run checkout (the W2 measurement root at `722f7bd1`).
    - SF-3: the claim that the tool enforces (b) holds only against unnamed rows; the issuer should refuse a registration that names a disposed session.
    - **Adjudication:** the refuter's amendments change the ratified text, so they go to a **cold addendum** (Fable) rather than the magistrate. The statement is recorded only after that addendum.
    - **New lane ISSUANCE-CUSTODY-OUTSIDE-REPO-01** (science-bearing issuer code, full tier). A design scout starts now. The design consult and the fix must land, blind to B values, before `prepare-candidate` first runs.
13. **ISSUANCE-CUSTODY-OUTSIDE-REPO-01 scout** (Sol 6.0 xhigh, outcome-blind; [brief](50-custody-outside-repo/01-scout-brief.txt), [report](50-custody-outside-repo/11-sol-scout-report.md)).
    - **The refusal is certain.** The issuer's `_repo_relative_custody` was run on all 24 W1/W2 locators and refused on all 24.
    - **It was latent in the plan.** The runbook puts night custody at `/Users/edr/night-custody/<PLAN_ID>` and forbids moving it. The issuer test `test_custody_outside_the_repository_refuses` asserts the refusal, and r6/r7 used gitignored in-repo `runs_window_*` paths.
    - **The other non-mirrored checks pass value-blind:**
      - the r7 predecessor pin matches;
      - the registration pins are well formed;
      - two nights with W1 then W2 is permitted, and the 12-slot count holds;
      - W1 futility is passed at 6.
      Only the plateau inset (value-dependent) is left unprobed.
    - **Designs:**
      - **A (recommended):** an artifact-level, generation-specific logical `source_root` descriptor plus a `--custody-root` flag. Members stay relative and contained. The verifier and reissue take a caller-supplied archive location, the validator accepts only the declared descriptor, and r6/r7 repo-root resolution is kept.
      - **B:** per-night logical roots.
      - Neither design moves, copies or symlinks custody, and neither lets a choice depend on values.
    - **Next:** the design ruling (who rules is the addendum's Q4), then implementation under the full gate, then `prepare-candidate`.
14. **Cold addendum REV5-REFUSAL-BRANCH-01-A1** (Fable 5.1, 12:25–12:34; [charge](40-refusal-branch/30-addendum/20-addendum-charge.md), [ruling](40-refusal-branch/30-addendum/21-addendum-ruling.md)): **ADDENDUM: FINAL STATEMENT ISSUED**.
    - It verified SF-1 by execution: the refusal is certain.
    - It adopted all seven refuter items, adding J-1 (the override window ends at the first value-dependent result) and J-2 (the custody fault is not a #416 clause-3 finding).
    - **BLOCKER B1:** the issuance step must not run until the custody repair lands.
    - **Who rules the repair:** the four-model council (D-184) designs it; a fresh cold gate, shown no B value, rules on the final diff. The owner is not required. Constraints R1–R9 are in statement item 6(d).
    - **S1 done:** the statement is recorded verbatim at [60-prepare-record/00-refusal-branch-final-statement.md](60-prepare-record/00-refusal-branch-final-statement.md) (`b2eae0ab`), sha256 `8717e33c27f069e3889d8f3d6095d76adbdd6ad9b012482e0cad3a936bb339a6`.
    - **S1/S2 email to Ed:** Gmail `1a0e45d2f203a0cb`.
    - **Still owed before the issuance step:** S4 (check Ed's replies immediately before) and S5 (re-run the dry run at the run's commit).
    - **Council seats** (all blind, on [20-consult-charge.md](50-custody-outside-repo/20-consult-charge.md)): Sol 6.0 xhigh (scout, recommends A), Astra 6 high, Opus 5.5 and Fable 5.1 (cold `claude -p`), all running.
15. **Custody-repair council closed: design C adopted** ([synthesis](50-custody-outside-repo/30-lead-synthesis.md)).
    - Fable 5.1 (cold) and Opus 5.5 both recommended C. Sol recommended A and Astra recommended B; both dissents are recorded.
    - C is a change to the issuer only. It adds `--corpus-root`, and a naming function that ties the first part of each stored path to the session id and the last part to the capture id. It adds a read-only `verify-members` command and a fixed-text `member_custody` note. The validator, loader, verifier, reissue tool and `configs/` are untouched.
    - Astra's path-hardening is folded in. Five lanes are registered (synthesis ruling 5).
    - The implementation seat (Sol 6.0 xhigh) was launched on branch `fix/2026-09-27-issuer-corpus-root`, worktree `JouleWise-wt-corpus-root-77b1bee2`, [brief](50-custody-outside-repo/40-impl-brief.txt).
16. **PR #434 row 9.** `python3 scripts/shard_tests.py --workers 6` ran on the integration tree `2a4416c4` (the merge of `722f7bd1` into origin/main `670756f3`, worktree `JouleWise-wt-harvest-integ-77b1bee2`, `/opt/homebrew/bin/python3`). **7,525 tests, 0 failures, 0 errors, 109 skipped; result PASS; rc 0** ([tail](20-harvest-gate/31-row9-fullsuite-tail.txt), [log](20-harvest-gate/31-row9-fullsuite.log.gz)). The run took about 68 minutes, contending with the concurrent S1 V1/V2 seat.
17. **PR #434 MERGED** at 12:52 PDT with a merge commit, `b69c39eb`. All checks were green, including the gate ledger. Canonical was fast-forwarded to `b69c39eb`, and the verdict path's only non-merge commit is `722f7bd1`.
18. **S1 ruling §7 steps 2–3: `S1 STEPS 2-3: GREEN+RED AS RULED`** (Sol 6.0 high; [brief](30-s1-steps23/01-seat-brief.txt), [report](30-s1-steps23/11-seat-report.md)). The seat edited nothing and HEAD stayed at `204424e6`, clean.
    - Green on the tree: the test method (1 test, 333 s), V1 (477 OK), V2 (343 OK), and B1 and B2 (`byte-identical entries=69`).
    - On `git archive` copies of the real committed test (the unmutated control copy is GREEN, 423 s):
      - mutant (a), both guards removed: RED, 17 failures, "SalvageAuthorizationError not raised";
      - mutant (b), guard A removed: RED, 17 failures, "failed attempt contains measurand bytes" did not match "unknown non-null …";
      - mutant (c), guard B removed: RED, 17 failures, "not raised".
    - **Next for S1:** ONE refuter pass on the merge candidate, then the S1 merge gate (full tier), on an integration tree with main `b69c39eb`.
19. **S1 merge candidate.** `origin/main` was merged into `feat/2026-09-26-bfgs-s1-bundles`, giving `4aefdd12`. Its tree `6e0dfda7` is identical to the integration tree. The ONE refuter pass (Sol 6.0 xhigh) was launched on it under 61 (c)/66 plus the three reading tasks ([brief](35-s1-refuter/01-refuter-brief.txt)).
20. **Bookkeeping.**
    - RUN_STATE top block `a609bf65`.
    - A lanes seat (Sol high, [brief](70-lanes-brief.txt)) registered A316–A329, 14 lanes: 263 + 14 = 277. `gen_state --check` passes, `tests.test_gen_state` is OK (44 tests), commit `f25bae33`.
    - **PR #435** is open from `docs/2026-09-26-22784e38` @ `f25bae33`, light tier.
    - **Row 1:** Sol high, **AUDIT: PASS** with 0 findings ([brief](80-pr435-audit-brief.txt), [report](81-pr435-audit-report.md)).
    - **Row 9** is running on worktree `JouleWise-wt-bk435-row9-77b1bee2` @ `f25bae33`, which contains main `b69c39eb`.
    - Further records of this activation go on branch `docs/2026-09-27-77b1bee2` (worktree `JouleWise-wt-bk-77b1bee2`), so #435's head stays fixed.
21. **S1 one refuter pass** (Sol 6.0 xhigh, [report](35-s1-refuter/11-refuter-report.md)): **`S1 REFUTER: A3 FAILS`**.
    - A1, A2 (119 keys, no false class or kind), A5 and all three reading tasks hold. No class (4) form was found.
    - **Two BLOCKERs of class (1), A3:**
      - **F1:** the cooldown-anchor route. It exists on main too, but S1 added lines in `evaluate_member` and `campaign_cooldown_before_member`, so the refuter says 66 (a) row 1c cannot exempt it.
      - **F2:** reduction does not recheck an attached calibration capture's own battery pair. The bound still flows to whole-window preparation, and S1 changed that function.
    - **Rule 11 is mandatory:** deciding whether the prior ruling's row-1c exemption applies is a reinterpretation of a verdict, and the magistrate may not adjudicate blocker severity downward. **Cold gate S1-A3-ROUTE-01** (Fable, [charge](35-s1-refuter/20-coldgate/20-coldgate-charge.md)) and a paired Opus refuter were convened. S1 is not on the issuance path; the custody repair continues in parallel.
22. **Custody repair implemented** (Sol 6.0 xhigh; [report](50-custody-outside-repo/41-impl-seat-report.md)). The lead committed it unchanged as `cc8346c2`, merged main to give **`c84b1dc2`**, and pushed `fix/2026-09-27-issuer-corpus-root`.
    - **What changed:** the issuer only, plus the fixture builder and a new `tests/test_issuer_corpus_root.py` (8 tests). `_repo_relative_custody` is byte-identical.
    - **Mutation cuts:** 11 named cuts, all RED.
    - **R8 probe:** all 24 real locators map to `<session>/runs/instrument_validation/<attempt>`. `/Users/edr` and the W1 night directory as roots refuse 24/24.
    - **R6:** all seven `calibration_acceptance_*.json` are byte-identical, and so are the four estimator-code files.
    - **The seat's one suite failure** is the sandbox denying `sysctl`. The lead is re-running the issuer, reissue and bracketing suites outside the sandbox.
    - **Lenses launched on `c84b1dc2`:** Sol xhigh (execution, rows 1 and 2) and Opus 5.5 (contract, rows 2 and 6), [brief](50-custody-outside-repo/50-lens-brief.txt). Next come the fresh cold gate on the final diff (row 7 and statement item 6(c)) and row 9.
23. **Custody repair, lead verification outside the sandbox** on `c84b1dc2`, run with `/opt/homebrew/bin/python3 -m unittest tests.test_issuer_corpus_root tests.test_issue_calibration_acceptance_generation tests.test_reissue_calibration_acceptance tests.test_calibration_bracketing`: **Ran 263 tests, OK (skipped=1), rc 0** ([tail](50-custody-outside-repo/42-lead-verify-tail.txt)). This includes the live `sysctl` OS probe that the sandbox had denied.
24. **Cold gate S1-A3-ROUTE-01** (Fable 5.1, 13:07–13:22; [ruling](35-s1-refuter/20-coldgate/21-coldgate-fable-ruling.md)): **RULING: S1 MERGE NOT BLOCKED.**
    - **F1** (cooldown anchor) and **F2** (capture pair not rechecked at reduction) both reproduce identically on main `b69c39eb`.
    - S1's only lines inside the route functions are gate-exception handlers that re-raise, and the window gate itself. They narrow the route: with a planted custody failure, main passes 9.99 W on while the candidate raises.
    - **Amendment 77** replaces test (iii) of 66 (a) with a checkable list. Every changed line in a route function is quoted, and only two closed forms count as off-route.
    - **Amendment 78:** F2's item of BFGS-RAWCAPTURE-01 must merge before any whole-window verdict computed after S1 is used for a paper number. Until then a read-only capture pre-check stands in.
    - "Land the lane first" is circular, because both fixes call gates that only S1 provides.
    - **Question 4:** this is not the SWEEPCLASS class. But F1 has now been to three gates with no new fact, and F1, F2 and the salvage licence share one shape (a verdict fed by sources that are not window members). The ruling lists five items for one consult on the two lanes.
    - The paired Opus refuter is pending. The lead's **A4** (V1, V2, builder ×2 on `4aefdd12`) is running.
25. **Custody repair lenses on `c84b1dc2`.**
    - **Opus 5.5 contract lens** ([52](50-custody-outside-repo/52-opus-contract-lens.md)): **LENS: PASS**.
      - Design C is exact with no scope creep, and output without the flag is byte-identical to base.
      - The flag changes only `member_custody` and `derivation_sha256`.
      - It passed the lens's own 23 + 16 adversarial inputs, and R8 was re-run: 24 accepted, and five wrong roots each refused 24/24.
      - **S1:** guard F2 is untested on the Revision-5 path. Plus 8 NITs.
    - **Sol 6.0 xhigh execution lens** ([51](50-custody-outside-repo/51-sol-execution-lens.md)): **LENS: FAIL**, with **F1 BLOCKER**: a nested capture `P/s/s/runs/instrument_validation/s-d01` is accepted under both `P` and `P/s`, so the stored name is ambiguous. The real 24 locators are unaffected.
    - **Lead ruling on F1:** require exactly `<session_id>/runs/instrument_validation/<attempt_id>`. This is the fixed middle part of Fable consult §4.1's diagram, and it makes the root unique. It is a design-C closure, not a new design.
    - **Fix round 1** (Sol xhigh, [brief](50-custody-outside-repo/60-fix1-brief.txt)) covers C1 (exact shape), C2 (a Revision-5 guard-F2 test plus a flag-equivalence test) and C3 (the nits). A delta re-audit follows, then the fresh cold gate on the final diff.
26. **Paired Opus refuter on S1-A3-ROUTE-01** ([22](35-s1-refuter/20-coldgate/22-opus-refuter.md)): **REFUTER: CONCUR**, 0 BLOCKER.
    - Section A independently found the same four answers:
      - S1's only lines in the route functions are the two `except GATE_EXCEPTIONS: raise` handlers.
      - F1 reproduces on main.
      - F2 is pre-existing and *worse* on main: main's own production fixture has no capture battery pair.
      - This is not the SWEEPCLASS signature.
    - **Five SHOULD-FIX items are against the amendment texts:**
      1. 77 (a) form 1 is too broad: argument-building lines that narrow the member filter would still count as off-route.
      2. 77 (a) has no refusal-only form.
      3. F2's test (i) was relaxed without saying so.
      4. 77 (b) has no channel to correct a false premise.
      5. The 78 (b) pre-check script exits 1 on the historical exemption.
    - **Disposition:** the S1 merge stands unblocked. The five items go to a cold erratum, **combined into S1's cold Fable final pass** (row 7), which rules on them before 77 binds a later pass.
    - **Outside the charge:** the 69-entry historical pin list has no `202609` bundles, so how W1/W2 bundles are admitted after S1 must be confirmed. W1/W2 are calibration captures, not scored bundles; this goes to the final pass as a question.
27. **S1 merge gate in progress on `4aefdd12`.**
    - **Lead A4:** V2 Ran 343 OK (778 s); B1 and B2 both `byte-identical entries=69`, rc 0 ([tails](35-s1-refuter/)). V1 is still running.
    - The Opus 5.5 counter-review (rows 2 and 6) was launched.
28. **Custody fix round 1** ([report](50-custody-outside-repo/61-fix1-seat-report.md)) was committed unchanged as **`f783a3fd`**.
    - It adds C1 (exact 4-part shape in both the naming function and `verify-members`), C2 (a Revision-5 guard-F2 test and a flag-equivalence test) and C3 (nits).
    - 15 new tests OK; mutation cuts RED; R8 24/24 accepted, with wrong roots refused 24/24.
    - The seat's only failure is the sandboxed `sysctl`. The lead is re-running outside the sandbox.
    - **Delta re-audit** (rule 9): Astra 6 high (cross-family), [brief](50-custody-outside-repo/62-delta-brief.txt).
29. **Custody repair after fix round 1** (`f783a3fd`).
    - **Lead verification** outside the sandbox: 270 tests OK ([tail](50-custody-outside-repo/63-fix1-lead-verify-tail.txt)).
    - **Astra 6 high delta re-audit: DELTA: PASS, 0 findings** ([64](50-custody-outside-repo/64-astra-delta-report.md)):
      - C1–C3 are exact, and C1 holds in both functions against 10 adversarial shapes.
      - The real ledger has 12 valid rows and 12 ordinary-invalid rows, with 0 duplicate valid attempt ids.
      - Three cuts ran and all went RED.
      - The Sol F1 class is closed (rule 11: no same signature).
    - **Cold gate CUSTODY-REPAIR-FINAL-01** (Fable, [charge](50-custody-outside-repo/70-coldgate-final-diff-charge.md)) was convened on `f783a3fd`. It serves as gate row 7 and as statement item 6(c).
30. **Cold gate CUSTODY-REPAIR-FINAL-01** (Fable 5.1, ≈13:45–14:00; [ruling](50-custody-outside-repo/71-coldgate-final-diff-ruling.md)): **VERDICT: MERGE; ITEM 6(c): TOOL REPAIR.**
    - **Evidence:** the judge re-ran 270 tests, ran R8 24/24 on the real paths, and tried 47 hostile inputs; nothing broke. The lead's F1 exact-shape ruling is within design C. The prepare argument is fixed as `--corpus-root /Users/edr/night-custody`, with `--repo-root` omitted.
    - **Conditions before the prepare step** (none blocks the merge):
      - **S1:** the default `--predecessor-acceptance` is an absolute path, and it would be stored in `derivation_notes.predecessor.relative_path` (base behaviour; R4 says no absolute path is stored). This needs a value-blind ruling now. The judge recommends that the owner permit passing the relative r7 path.
      - **S2:** lane ISSUANCE-ARCHIVE-PACKET-01 must key the archive layout on **session id**, not plan id, because W1 and W2 share one plan id.
      - **S3:** the R7/R9 disclosures go into the PR and the prepare record.
      - **S4:** the run checkout is still at `722f7bd1`. Advance it after the merge and recheck the item 2(d) digests.
    - The ruling's §8 lists 11 value-blind prepare checks.
    - **Row 9** is running on `f783a3fd`, which contains main `b69c39eb`.
31. **PR #435 gate complete.** Row 9 ran `python3 scripts/shard_tests.py --workers 6` on `f25bae33`, which contains main `b69c39eb`: **7,525 tests, 0 failures, 0 errors, PASS** ([tail](82-pr435-row9-tail.txt)). Hosted CI is green on `f25bae33`, apart from the ledger check awaiting this evidence. **Row 12**, magistrate terminal review of `f25bae33`: docs, state and the test count only; the audit passed; the full suite is green. MERGE.
32. **PR #435 MERGED** as `daaff807` (merge commit, light tier), and canonical was fast-forwarded. **S1 A4 complete on `4aefdd12`:** V1 (tail in [40-a4-v1-tail.txt](35-s1-refuter/40-a4-v1-tail.txt)), V2 343 OK, B1 and B2 `byte-identical entries=69`.
33. **Correction to item 32: A4 is NOT complete.** V1 on `4aefdd12` ran 477 tests with **FAILED (failures=1), rc 1** (5,510 s under contention).
    - **The failing test:** `tests.test_bundle_read.StrictAccessorTests.test_historical_set_bytes_and_protected_base_paths_are_pinned`. It runs `git diff --exit-code 1417c0c4 -- <protected>`, and `<protected>` includes the whole of `configs/calibration`.
    - **Why it fails:** main's W1 and W2 harvests (#432 and #434) added `configs/calibration/battery_float_verdicts/*.json` and moved `calibration_ledger_head.json`. Those are legitimate harvest-written state, and the fence was written before them.
    - **Consequence:** this is a merge conflict of meaning between S1's fence and main. It **blocks S1's merge**, and as written it would fail after every future harvest.
    - Awaiting the Opus counter-review (its Q3 asks exactly this) before a dictated test-only fix and an S1 final pass that also ratifies the fence change.
34. **Opus 5.5 counter-review of S1 `4aefdd12`** ([30](35-s1-refuter/30-opus-counter-review.md)): **COUNTER-REVIEW: FAIL**, on **B-1** only (the same fence failure as item 33).
    - **What holds:**
      - scope is exact: 27 files, the same set as the fix-3 WRITE_SCOPE, and no unruled production change;
      - the fences hold;
      - the merge is mechanically clean;
      - all 12 post-cutoff valid observations and all 24 W1/W2 captures pass.
    - **SHOULD-FIX:**
      - S-1: the PR description obligations;
      - S-2: the 78 (b) pre-check script;
      - S-3: `test_raw_capture_lane_files_match_main` has the same latent flaw, pinned to `97082508`.
    - **NIT N-1:** constant 176 is read as the S1 branch base, which is the stricter reading.
35. **B-1 bench fix, test-only, 1 line.** The fence now diffs S1's own commits, `1417c0c4 204424e6` (option (a)). Committed as **`c7593edb`** on `feat/2026-09-26-bfgs-s1-bundles` and pushed.
    - GREEN on the head.
    - **RED under the counterfactual** in which the compared commit touches `configs/calibration` (main `b69c39eb`): FAILED (failures=1).
    - `git diff --quiet 1417c0c4 204424e6 -- configs/calibration` gives rc 0.
    - `tests.test_bundle_read` ran **118 OK**, after clearing a stale `__pycache__`.
    - **Lesson (self-report):** the counterfactual was run by swapping the test file in place. The swapped file had the same size and the same second's mtime, so Python kept the counterfactual bytecode and the first module re-run showed a false RED. Run counterfactuals on a copy, or clear `__pycache__`.
    - The S1 cold final pass (row 7) ratifies B-1 (a), rules S-3, and gives the 77/78 erratum ([charge](35-s1-refuter/50-fable-finalpass-charge.md), updated to `c7593edb`).
36. **Custody repair, rows 9 and 11 prep.**
    - **Row 9:** `python3 scripts/shard_tests.py --workers 6` on `f783a3fd` gave **7,540 tests, 0 failures, 0 errors, PASS** ([tail](50-custody-outside-repo/72-row9-tail.txt)).
    - **Main moved after that run.** Main moved from `b69c39eb` to `daaff807` (#435), touching only README, RUN_STATE, TASK_QUEUE and `tests/test_gen_state.py`.
    - **Integration tree `06ecc12c`** (`f783a3fd` merged with `origin/main`): `tests.test_gen_state` plus `tests.test_issuer_corpus_root` ran 59 OK; `gen_state --check` rc 0.
37. **PR #436** (custody repair) was opened from `f783a3fd` with the full ledger. The gate-ledger check passes; hosted tests are queued.
38. **S1 cold Fable final pass** ([51](35-s1-refuter/51-fable-finalpass-ruling.md)): **VERDICT: MERGE `c7593edb`.**
    - **B-1 fix RATIFIED** (§3.1). It is GREEN on the candidate and RED when S1's head is swapped for scratch commits touching a calibration file, `reduce.py` or main's harvest state.
    - **S-3 is NOT fixed the same way** (§3.2). The tripwire text goes into lane BFGS-RAWCAPTURE-01's brief.
    - **Erratum E1:** all five refuter items are adopted (items 1 and 2 amended), with a replacement 78 (b) pre-check script (§4).
    - **§5:** after the merge, the battery gate refuses all 57 on-disk `runs_window_7bfloor_20260729` bundles as `prospective bundle`, as ruled (amendment 40 erratum; lane HISTORICAL-BATTERY-STATE-01).
    - **Merge conditions:**
      1. merge commit only;
      2. the PR description carries text 15 verbatim, the registry refresh list, both lanes with their orders and pre-checks, 77/78 as replaced by E1, the reading of the constants, and the 7bfloor sentence;
      3. the tripwire text goes into the BFGS-RAWCAPTURE-01 brief;
      4. **one full V1 + V2 + builder run on main after the merge.**
    - Row 9 is running on the S1 integration tree `42e2af3e` (`c7593edb` merged with main `daaff807`). An Opus writer is drafting the PR description from the rulings (dictated fills).
39. **Cold gate PREDECESSOR-PATH-01** (Fable 5.1, ≈16:10–16:20; [charge](60-prepare-record/10-predecessor-path-charge.md), [ruling](60-prepare-record/11-predecessor-path-ruling.md)): **RULING: (b).**
    - The prepare step passes `--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, relative, from the run checkout.
    - A synthetic trial showed that only the stored path string and the whole-file digest differ, and every substitution of different content was refused.
    - This is recorded as a **disclosed amendment made before any measured value was read**. Ed's reply (asked as Gmail `1a0e4ac6d73738a2`; none yet) takes precedence if it arrives before the prepare step.
    - The final pass's §4.6 N-1 rewording of "land the lane first" is noted against item 24's wording ("gates that only S1 provides").
40. **PR #436 MERGED** at 16:23 PDT as `e7c8bcc6` (merge commit). All hosted checks were green. Canonical was fast-forwarded.
41. **Prepare step: done, one run, a candidate was written.**
    - **Before the run:** the owner was told under C4 (Gmail `1a0e52ead28598fe`). The run checkout was advanced from `722f7bd1` to `e7c8bcc6`. All value-blind pre-checks passed ([20-prechecks](60-prepare-record/20-prechecks/00-prechecks.md)).
    - **The run** (16:25:42–16:26:39): rc 0, **candidate `dbad7cc7…b5b2`, n = 12, NOT ISSUED** ([30-run1](60-prepare-record/30-run1/00-run1-record.md)).
    - **After the run:** 12/12 `verify-members` PASS; no absolute string; the predecessor note is relative; the custody tree is byte-identical before and after (R3).
    - **Rule outcomes:** S = 0.013701 s; level screen 0.038079 s; positive headroom; excursion members 0; **2 screen-challenge members above r6's 0.0329 s**; new maximum not above the prior maximum plus range.
42. **Cold science gate (runbook §4.3, adapted to two windows)** under the four-model shape:
    - Sol 6.0 high mechanically assembles the packet on side branch `docs/2026-09-27-77b1bee2-packet` ([brief](70-science-gate/01-packet-brief.txt)).
    - Astra 6 xhigh independently re-derives every operative from the raw members ([brief](70-science-gate/02-rederivation-brief.txt)).
    - Next: a cold Fable 5.1 science judge with a paired Opus refuter. **The D-138 issuance transaction is out of scope for this turn** (runbook §4.4).
43. **Science-gate inputs are complete.**
    - **Packet:** Sol-assembled, all 8 items, byte-checked ([packet](70-science-gate/packet/00-index.md), side-branch commit `f1f6b3a5`, merged).
    - **Astra 6 xhigh independent re-derivation: REDERIVATION: MATCH**, 0 findings ([12](70-science-gate/12-astra-rederivation-report.md)):
      - it used 90-digit Decimal arithmetic and its own Student-t inversion;
      - the 12 members are exactly the valid captures;
      - the digests match custody, ledger and candidate;
      - all 276 receipts and 48 battery observations authenticate.
    - **The cold Fable science judge** (SCI-25G83-CANDIDATE-01, [charge](70-science-gate/20-science-gate-charge.md)) and a **paired Opus refuter** were convened at ≈16:35.
44. **S1 row 9 FAILED. S1 is NOT mergeable despite the final pass's MERGE.**
    - **The run:** `python3 scripts/shard_tests.py --workers 6` on the S1 integration tree `42e2af3e` (`c7593edb` merged with main `daaff807`): **7,647 tests, 115 failures, 418 errors, all 6 shards FAIL** ([tail](35-s1-refuter/60-row9-tail.txt), [log](35-s1-refuter/60-row9-integration-FAIL.log.gz)).
    - **Attribution:** `tests.test_phase_share` and `tests.test_audit_amplification` give FAILED (failures=4, errors=3) on S1 `c7593edb` alone, and OK on main `e7c8bcc6`. **The regression is S1's own.**
    - **Dominant signatures:**
      - `battery_float_evidence_missing` (S1's gate refuses fixtures that carry no battery evidence);
      - `stale supply-map receipt digest` (d165_closeout, reported_energy_parents);
      - `RunStatus.FAILED`;
      - missing `order_manifest.json` fallback warnings turned into failures.
    - **Root of the miss:** every S1 round and every S1 gate ran only the targeted V1/V2 suites. No full suite ran on any S1 head until this row 9. The final pass listed "full V1 in one run" as not executed, and inferred the rest was green.
    - **The gate worked:** row 9 caught what the lenses did not.
    - **Next:** a classification scout (Sol high) over all 533 failures, then a consult on the fix shape. The options are fixture battery evidence, the historical-exemption scope, or gate placement. S1 is off the issuance critical path. No fix round runs before the scout.
45. **S1 regression scout** (Sol 6.0 high; [brief](35-s1-refuter/61-regression-scout-brief.txt), [report](35-s1-refuter/62-regression-scout-report.md), inventory `62-regression-inventory.jsonl`).
    - **Coverage:** 533 outcomes across 478 test ids and 42 modules, in 11 groups. Every group's representative fails on S1 and passes on main.
    - **Fixture/test scope, (a):** G1 and G3–G8 plus G10. These are synthetic fixtures that lack battery pairs, digest-bound config/metadata, resolvable custody, or an injected battery runner.
    - **G2 (42 F / 56 E) needs a ruling:** mock (`not_applicable`) members now refuse at window scope, including campaign completion. Preserving successful non-claim mock workflows would need a separately ruled production path; passing `not_applicable` would weaken the gate.
    - **G9 (23 F) needs authority:** stale paper supply-map receipt digests (`d165_closeout`, `reported_energy_parents`, `whole_window_verdict`), because S1 changed pinned sources. The repin reaches `configs/paper_supply/` outside S1's ruled scope.
    - **G11 (36):** secondary; these need a re-run after the other closures.
    - **No group** is a historical-set exemption.
    - **Why no gate caught it:** V1/V2 selected none of the 42 legacy modules.
    - **Next (not this slice):** a consult with a cold ruling on G2 (the mock-workflow contract) and G9 (repin authority and order). Then a fixture-repair round under an enforced WRITE_SCOPE, then a delta re-audit, then row 9 again. **This is a new lesson for every lane: full tier requires a full-suite row 9 on EVERY fix head before the final pass, never targeted suites alone.** It is registered for the council (not ratified here).
46. **Cold science gate SCI-25G83-CANDIDATE-01** (Fable 5.1, ≈16:35–16:53; [ruling](70-science-gate/21-science-gate-ruling.md)): **VERDICT: PROCEED TO ISSUANCE** (to the D-138 transaction, which has its own gate).
    - **What holds:**
      - Membership is exact.
      - S, C, the level screen and headroom all reproduce.
      - The sealed Revision 5 text removes the screen-challenge veto (three places are quoted), and it was sealed before W1.
      - No retained value shows an artifact. W2 running higher than W1 is not a real effect (permutation p = 0.19).
      - **No mark applies:** neither `excursion_limited` nor `zero_headroom`.
    - **New findings:**
      - **8 of the 12 exclusions came from the estimator's 165,000-cell work cap**, which was sized for ≈120 ms frames; this epoch runs at 128–130 ms. The cap selected on cadence (r = +0.82), not on B (r = −0.05, p = 0.44).
      - **3 exclusions came from wall-clock steps** of 52.0, 35.9 and 5.8 ms (`wall_minus_monotonic_span_exceeded`). They were excluded as ordinary-invalid under the judge's structural reading (§2.4), which matches statement item 4(iii). **The strict reading would refuse issuance. The owner may overrule**, and that would be recorded as made after the outcome was known.
    - **Mandatory disclosures D1–D6** (§7) travel with the D-138 record and the paper.
    - **Recommendations (§8):**
      - **Re-size the cap** before measurement windows run at scale; about one bracket in four would complete as things stand. Re-sizing changes a pinned estimator file, which stales the calibration and forces a re-issue. The council should rule *first* on which captures a re-issue may contain; the judge's view is the same 12.
      - **Find what steps the wall clock.**
      - **Packet erratum** on item 04.
    - The paired Opus refuter is pending. **D-138 is not started in this turn** (runbook §4.4).
47. **Paired Opus refuter on the science gate** ([22](70-science-gate/22-opus-refuter.md)): **REFUTER: CONCUR**, 0 BLOCKER. It independently replicated all 12 member B values, the 20 cell counts, the 8 diagnostic B values and the clock-step spans. Its SF-1 to SF-3 went to the **cold addendum SCI-25G83-CANDIDATE-01-A1** (Fable, [31](70-science-gate/31-addendum-ruling.md)), which ruled **ADDENDUM: ISSUED**, adopting all of them:
    - **SF-1:** the 165,000-cell cap is **not** a derivation-code defect under statement item 7(b). It was registered on 2026-08-15, frozen on 08-18 and pinned before capture. Re-runs at caps of 165k, 206k and 5M give the stored B to the last digit.
    - **SF-2:** D-138 issues with the four estimator files **byte-for-byte as run** (binding text B1–B4 in the ruling). Four unmerged branches touch pinned files (three named by the refuter, plus `impl/p2041`). A cap re-size is a separate, later transaction, after the council rules on re-issue membership and on a sizing rule that uses no B value.
    - **SF-3, a HOLD on claim-bearing windows at 25G83:** before any claim-bearing window is armed, one of two things must be true.
      - The cap is re-sized by a rule written in advance, with at least 24 non-claim captures showing none stopping on the cap.
      - Or the cap stays, under a registered plan that records every abandoned bracket and compares its energy with completed ones.
      The clock-step exclusions fall under the same hold.
    - N-1 to N-4 adopted.
    - **Next (a new activation or turn; runbook §4.4):** the D-138 issuing transaction, with its own gate, carrying D1–D6 and A1's binding text.
48. **Lanes registered** (second seat): CALIB-ISSUE-25G83-D138-01, ESTIMATOR-CELL-CAP-RESIZE-01, WALLCLOCK-STEP-SOURCE-01 and S1-REGRESSION-01, so 277 + 4 = 281. ISSUANCE-ARCHIVE-PACKET-01 is corrected to a session-id layout. Commit `4ae6de80`, merged.
49. **S1-REGRESSION-01 consult:**
    - **Seats:** Sol xhigh ([11](36-s1-regression-consult/11-sol-consult.md)), Astra high ([12](36-s1-regression-consult/12-astra-consult.md)) and Opus ([13](36-s1-regression-consult/13-opus-consult.md)). All three say HOLD, and they split on G2.
    - **The cold Fable ruling** ([21](36-s1-regression-consult/21-coldgate-fable-ruling.md)): **RULING: S1-REGRESSION-01 ISSUED.** The earlier S1 MERGE verdict is **void**. S1 is repaired on its own branch, with the production diff kept whole.
      - **G2, rule 12a:** a keyword `admit_mock_window`, strict by default, passed by exactly two non-claim flows (campaign completion and the experiment manifest aggregate). Every claim-writing call site is unchanged. The text and 10 defect-shaped tests are in §3.
      - **G7:** a production regression Astra found and the ruling confirmed. The battery classifier reads the original custody locator, so custody replayed from a backup root raises `CustodyFailure`. **Text 10a** routes it through the mode-aware resolver.
      - **G9:** the roles are synthetic `test_fixture_non_issuing` fixtures. The lead repins three roles' digests at the bench as the last commit in S1's PR, and the delta refuter recomputes them. `tests/fixtures/paper_custody/repin.py` must **not** be run, because it deletes the `qwen3-8b` pending role.
      - **Scope:** granted by exact path (39 test files, 2 new helpers, `configs/paper_supply/supply_map.json`). The three §E test files are granted only with byte-identical assertions. `receipt_corpus.py`, the repin helper and the historical set are refused.
      - **Plan:**
        1. a reference run on main;
        2. a production seat and a fixture-helper seat, in parallel;
        3. four repair seats;
        4. the lead's eight checks, including an assertion census and planted defects;
        5. the repin;
        6. the full suite.
      - **Standing rule within this lane:** no refuter, cold gate or final pass is charged without a full-suite record on the exact head merged with the day's main. Skips are compared by test id.
    - The paired Opus refuter is pending.
50. **Paired Opus refuter on S1-REGRESSION-01** ([22](36-s1-regression-consult/22-opus-refuter.md)): **REFUTER: CONCUR**, 0 BLOCKER. The keyword design of 12a is better than the seat's own. The grant covers every failing non-G9 module. Four SHOULD-FIX items **amend the ruling** and so go to a **cold addendum before any repair seat is briefed**:
    - **SF-1:** ban a battery pair on a mock-config fixture. Check 2 gains this, helper H refuses it with a counterfactual self-test, and the reader-side admission goes to a lane.
    - **SF-2:** rule `run_campaign.py:7848`, the AXI completion gate. Either add it to 12a (c) with a T12a-8 AXI row, or record why it is claim-bearing.
    - **SF-3:** 12a (d) is already met. `claim_readiness_for` returns `ready_for_analysis` for mock campaigns, per main's documented contract. The refuter prefers (a): keep main's semantics, since the loader stays strict.
    - **SF-4:** add a fence limiting the repair diff's test paths, because check 7's commit-to-commit fence cannot see the repair.
    - Plus three NITs.
51. **Wrap-up.** This activation stops here, so that **D-138 runs in a fresh turn** (runbook §4.4). No Codex seat, `claude -p` judge or subagent of this activation is still running; each finished and was harvested. The durable pointer is the RUN_STATE top block on `docs/2026-09-27-77b1bee2`.
