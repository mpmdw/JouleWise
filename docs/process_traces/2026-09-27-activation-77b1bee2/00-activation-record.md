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
