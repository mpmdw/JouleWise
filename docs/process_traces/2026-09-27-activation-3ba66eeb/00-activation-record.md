# Activation 3ba66eeb — record 00

The magistrate was relaunched headless at 03:05:03 PDT on 2026-09-27 (Opus 5.5).
Frozen triple at launch: canonical only, `(__canonical_repo__, /Users/edr/code/JouleWise, null)`.
The predecessor's next action was record 22784e38 item 17, beginning with **harvest W1**.

1. **Launch.** Heartbeat written (pid 81133). Checks before the launch email:
   - Gmail `from:claude2.glaring610@passmail.net is:unread`: none.
   - Directives: six open (#422, #421, #417, #416, #408, #405), all previously seen; nothing new.
   - No standdown request and no STOP.
   
   The launch email was accepted as Gmail `1a0e25449a3aa211`, and `notice.ack` was written.
2. **Pending notice `transition-483-hold_census` (00:34:23 PDT) is benign.** Every non-empty census from 00:34 to 02:24 names exactly one process: W1's own driver, `run_night.py run --plan …w1-20260927/night_plan.json` (PID 79271). The watchdog held the magistrate out while the night ran, which is the intended behaviour. It returned to FENCED at 02:34:55 (census empty) and launched this activation at 03:05.
3. **Self-report 1 (git in canonical while armed).** At about 03:05:20, before reading the checkpoint's "never fetch in canonical while armed" lesson, the magistrate ran `git fetch -q origin` in `/Users/edr/code/JouleWise` while W1's agents were still loaded. Only remote-tracking refs moved; HEAD, index and worktree stayed at `97082508` and clean. This is the same fault activation 2d9ded9c self-reported. The durable cure is for the relaunch prompt or checkpoint to put the fetch prohibition before any command.
4. **Self-report 2 (read order).** Before reaching runbook §2.2a, the magistrate read `operator_logs/derivation-chain.log`, including its twelve `slot_end … disposition=` lines (6 valid, 6 non-valid). That read happened before the battery-float verdict was committed, which §2.2a step (viii) forbids. No measured value, ledger row or evidence file was opened.
   - **Effect:** none on the verdict. `battery-verdict` computes it mechanically from the raw `battery_float.{pre,post}.ioreg` bytes fingerprinted at capture, and the tool has no input for operator choice.
   - **Remaining duty:** disclose the ordering departure in the harvest notice and the PR body.
5. **W1 night outcome** (no measured value read). Read from `night.log` and `night/result.json`, which the runbook permits before step (iii):
   - driver started 00:30:00.75 PDT; gate verdict GO; chain digest verified;
   - result verdict GO at 02:33:42; `chain_exit_code` 0; `receipt_class` DIAGNOSTIC_NO_PACK; 248 censuses, 0 hits;
   - durable record pushed to `night-results/d079-epoch-25g83-derivation-w1-20260927` (`497b332b`);
   - courier attempt 1 sent at 02:34:46.
6. **Harvest §2.1 preservation.** The custody root was copied byte-exact to `~/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/` (`diff -r` identical, 1.2 G). An `lstat` inventory with sizes, `mtime_ns` and modes was written beside it: `lstat-inventory-ns.txt`, 11,263 rows.
7. **Documented uninstall after completion.** From the measurement root: `scripts/install_night_agent.sh --plan <NIGHT_ROOT>/night_plan.json --uninstall` returned rc 0 with empty output. Afterwards only `com.joulewise.magistrate` is loaded, and no `com.joulewise.night*` plist is on disk. Canonical `97082508` equals `origin/main`, so no fast-forward was needed.
8. **§2.0 coordinates rebuilt.**
   - `test HEAD = H`: OK. `chain.zsh.sha256 -c`: OK. The plan's `custody_root` equals `NIGHT_ROOT`.
   - Wrapper exports: `SESSION_ID=d079-epoch-25g83-derivation-w1-20260927`, `PLAN=<NIGHT_ROOT>/calibration_plan.json`, `EVIDENCE_ROOT_ID=evidence-<plan>`, `RUNS_ROOT=<NIGHT_ROOT>/runs`.
   - The first cadence-report call used the stale W1-arm README form. It refused with `calibration_ledger_head_mismatch` (pin 176, physical head 226), which is the runbook's `needs_pin_commit` row. The README HARVEST CHECK command is also stale: it lacks `--window` and `--preregistration-sha256`. Use the runbook §2.2a block instead.
9. **§2.2a executed in order**, in the measurement root. Evidence is in `10-w1-harvest/`.
   - (i) `terminal_head_pin_for_session` → sequence 226, digest `bd7aee7ab969e58d4c08992a3af0b0a1fed88cc9a911a65d1200ed0220a46693`. `advance-head-pin` (operator `magistrate-3ba66eeb`) ran as a dry run, rc 0, then with `--execute`, rc 0: pin 176/`0f7609ae…2512` → 226/`bd7aee7a…6693`.
   - (iii) `battery-verdict` → **`d079-epoch-25g83-derivation-w1-20260927: battery=pass`**, rc 0. The pre-registration file's sha256 equals `81b65f08…ddf1`.
   - (iv) One commit, `c5088b871dac4a3e75773f645c6293ffde1568b9`, containing the pin and `configs/calibration/battery_float_verdicts/<SESSION_ID>.json`. Pushed as `harvest/2026-09-27-w1-pin-verdict`.
   - (v) Harvest line: `d079-epoch-25g83-derivation-w1-20260927: battery=pass verdict_sha256=07bcc13b6f476c72280a74e21bfc2499b9085f5bf380cf891afa7f341fa535a2 verdict_commit=c5088b871dac4a3e75773f645c6293ffde1568b9`.
   - (vi) Cadence report, rc 0: 12 captures; median native frame 128.46 ms; max 141.64 ms; median of capture medians 128.80 ms; **R5(n) CONTINUE** (threshold 150 ms).
   - (vii) `check --session-ids`, rc 0. The epoch watch shows `os_build` MISMATCH (25F84 vs 25G83), which is expected for epoch 25G83; the powermetrics sha matches. Dry run: `battery=pass recorded=pass`; `kind=derivation state=finalized terminal=yes declared=12 filled=12 valid=6 excluded=none`; prefix pending 0; **registration admissible for prepare-candidate: yes**.
   
   **W1 is ADMITTED** (battery pass, cadence CONTINUE).
10. **Science note for W2 planning, not a gate.** The valid yield is 6/12 (50 %), below the pre-registration's projected valid rate near 30/38 (≈79 %). The rows were not opened. What the registration's stopping and replacement rules imply for W2 when the yield is this low is for the W2 planning step to read from the registration text itself.
11. **Merge path for the harvest commit.** TIER-01 (i)/(iii)/(v) make the pin and verdict FULL-TIER. The branch-protected `main` requires the gate ledger, so the commit lands by PR. It must merge with a **merge commit, never squash or rebase**. Correction per the Opus contract lens S1: the code check (`battery_float.py:599–606`, `git log --full-history --no-merges`) would also pass after a squash, but squash and rebase rewrite the SHA already published as `verdict_commit=c5088b87` in the harvest line. W2's arm needs this merged: W2's measurement head must carry pin 226.

12. **Harvest email** accepted as Gmail `1a0e259bfb22d25c` (thread `1a0e25449a3aa211`). It carried the harvest line, the 6/12 yield and the ordering departure. It did **not** carry arm-gate NIT-1 or NIT-6 (contract lens S2); the W2 arm notice text now carries both, plus NIT-3.
13. **PR #432** opened (FULL tier). Gate so far:
    - Row 1 + row 2 (execution lens): Sol 6.0 high, [11-sol-audit-report.md](20-harvest-gate/11-sol-audit-report.md), **AUDIT: PASS**. It re-derived the pin and the verdict byte-exact and read all 24 ioreg files: 0 mA in 23, −11 mA once (d10 post); all `probe_error=false`, `passed=true`. Its F1 and F2 are pre-existing gaps in frozen `battery_float.py`:
      - F1: `validate_window` ignores the recorded `probe_error` and `passed` fields, so a false pass is possible in principle;
      - F2: `compare_verdict` compares a field subset.
      
      Both go to a lane (BATTERY-VALIDATOR-PROBE-ERROR-01; F1 bears on verity per directive #421). **Until it lands, every harvest adds a manual check that all readings have `probe_error=false` and `passed=true`.**
    - Row 2 (contract lens) + row 6: Opus 5.5, [12-opus-contract-lens.md](20-harvest-gate/12-opus-contract-lens.md), **CONTRACT LENS: PASS**, with S1–S3 should-fix (merge-reason correction; notice NITs; W2 material), all actioned.
      
      Science C: the registration stops only on fewer than 6 valid of 12, so W1 counts with 6 members. Issuance needs n ≥ 12 across windows, and W3 is allowed only on count. At a 50 % yield, W1+W2 fall short about 39 % of the time. **Revision 5 is silent on n < 12 after W3.** That goes to Ed or a cold gate before W3 is needed (lane REV5-POST-W3-SHORTFALL-01).
    - Row 7: a cold Fable final pass was convened on `c5088b87` ([charge](20-harvest-gate/21-fable-finalpass-charge.md), committed at `59fd6fcd`).
    - Row 9: `scripts/shard_tests.py --workers 6` running on worktree `JouleWise-wt-harvest-w1-3ba66eeb` @ `c5088b87`, which equals the integration tree because the base is main.
14. **SWEEPCLASS: the rule-11 same-signature escalation → consult, not round three.** Two consecutive rounds each gave 0 BLOCKER and 5 SHOULD-FIX latent static-sweep evasion forms, with no current leak.
    - Consult [charge](30-sweepclass-samesig/00-consult-charge.md) at `7a341228`. Blind seats: Sol 6.0 high ([11](30-sweepclass-samesig/11-sol-consult.md)), Astra 6 high ([12](30-sweepclass-samesig/12-astra-consult.md)), Opus 5.5 ([13](30-sweepclass-samesig/13-opus-consult.md)).
    - **All three:** an exhaustive static guarantee is not closable, and this is the same signature. Close B-1 and B-5 as plausible accidents; record B-2 as a D-161 limitation.
    - Sol and Astra both found the sweep test **currently failing** at S1 head `315364b2` on an allowlist inventory mismatch. That blocks S1's merge; it is not a leak.
    - They split on B-3 and B-4. Opus adds the root cause: there is no gated `summary()` accessor.
    - The cold Fable judge was convened on the [cold-gate charge](30-sweepclass-samesig/20-coldgate-charge.md) at `6820fed0`, with a paired Opus refuter (Section A independent, Section B after the ruling).
15. **TEST-CENSUS-MULTILINE-ARGV-01**, bench fix on branch `test/2026-09-27-census-multiline-argv` (worktree `JouleWise-wt-census-3ba66eeb`). The scout's PID-only proposal would have deleted the per-hit text assertions (pattern match; no recorded service basename). The bench fix keeps them: `pgrep -f` supplies PIDs, then each hit's argv is read back with `ps -ww -o command= -p PID`.
    - Counterfactual, with a live decoy whose argv holds a newline (`scripts/run_campaign\nimport time\n`): the original test **errors=1** (tree `c5088b87`), the fixed test **OK**. The decoy was killed afterwards.
    - Light tier (test-only).
16. **W2 arm scripts** were derived from the W1 set at [40-w2-arm/scripts/](40-w2-arm/scripts/):
    - ids set to `w2`;
    - `__H__` and `__T0__` placeholders;
    - `LEDGER_SOURCE` = the W1 measurement root's 226-row ledger, with its expected sha256 `b03be938…c63f`;
    - the notice carries W1's harvest line, the NITs and the ordering departure.
    
    These were not executed. Registration spacing puts W2 t0 at 09:00 PDT or later.

17. **Harvest PR #432, row 7: the cold Fable 5.1 final pass ruled `VERDICT: MERGE`** ([22-fable-finalpass-ruling.md](20-harvest-gate/22-fable-finalpass-ruling.md)). It found 0 BLOCKER. Its SHOULD-FIX items:
    - S1: the gate is incomplete on GitHub (rows 9 and 11 are owed).
    - S2: merge with `gh pr merge 432 --merge`, and build W2 from a full clone.
    - S3: cross-check F1/F2 by hand at every remaining harvest of this epoch; the code change goes to its own lane.
    - S4: the notices carry the harvest line, both early touches, and d11's +9 mAh gauge re-estimate (0 mA). This is added to the W2 step-3 text.
    
    NITs N1–N5 (runbook §2.1 caveat; registration "pin-free" wording drift) are carried to lanes.
    
    **Rows 3, 4, 5, 8 and 10:** there was no fix round and no post-review commit. No reviewer (Sol AUDIT PASS, Opus CONTRACT LENS PASS, Fable MERGE) raised a finding against the commit's bytes; every SHOULD-FIX concerns notices, merge method, W2 material or a pre-existing frozen-file validator lane. The merge candidate is the reviewed commit `c5088b87`; it is two generated files, with nothing to prune.
18. **Census fix review:** Sol independent review `REVIEW: FAIL` on one finding ([copy](50-census/11-sol-review.md)). F1: an unrelated hit that exits between `pgrep` and `ps` skipped the basename check.
    - **Fixed at the bench** (`2b4f0a86` on `test/2026-09-27-census-multiline-argv`): a whole-output `pgrep -lf` recorded-service check that also covers continuation lines, at least as strong as the original per-line check. With the live newline decoy the test is OK.
    - **Bench slip:** `pkill -f 'scripts/run_campaign'` killed the background job whose own command line held that string, so the module run died (rc 144). Kill decoys by PID only. The full suite (row 9) was running at the time; any `run_campaign`-spawning test failure in its tail is suspect and gets a module rerun.

19. **Census lane: rule-11 same-signature consult.** The delta re-audit of `2b4f0a86` returned `REVIEW: FAIL` ([12-sol-delta.md](50-census/12-sol-delta.md)): a hit that exits between the `-f` and `-lf` snapshots still slips. That is the same signature as round 1 (an exit-between-snapshots window), so the next spend was a consult, not a third bench round.
    - Sol consult ([13-sol-consult.md](50-census/13-sol-consult.md)): **RECOMMEND c**. Deterministic negative decoys for all nine recorded service identities, checked in the same `pgrep -f` snapshot as the positives. The live-hit basename checks are dropped. Its stated trade: the nine recorded identities get deterministic coverage, and the incidental transient-hit check is given up.
    - Implemented at `3a346c46`. Focused test OK with a live newline decoy (killed by PID).
    - **Mutation:** with `watchdogd|` added to `_MONITOR_CENSUS_PATTERN`, the test FAILS on marker `/usr/libexec/watchdogd`. The mutation was reverted.
    - Final-head independent review `REVIEW: PASS` ([14-sol-final-review.md](50-census/14-sol-final-review.md)).

20. **The SWEEPCLASS-SAMESIG-01 cold ruling** ([21](30-sweepclass-samesig/21-coldgate-fable-ruling.md)) narrows the sweep's promise to accidental-edit coverage (amendment 61).
    - B-1 and B-5 are closed (62).
    - B-2 and B-3 are limitations. B-3 also gets lane BFGS-READER-ROOT-01 after S1.
    - B-4 gets a gated helper in `envelope_gate.py` (63), the only production change inside S1. The consensus inline edit was rejected by execution (Z8).
    - The inventory failure is fixed by the already-ruled detector replacement plus rule (d) 6 (64), not by key edits.
    - Fix round 3 is restated as §8.2 steps 1–12. The stop predicate is A1–A5 plus one refuter pass. Gated `summary()` becomes lane BFGS-GATED-SUMMARY-01, after S1, blocking nothing.
    
    **The paired Opus refuter** ([22](30-sweepclass-samesig/22-opus-paired-refuter.md)) raised F1, a BLOCKER tree finding (the cooldown anchor carries a pre-gate `idle_baseline` into later campaigns' admission reasons); SHOULD-FIX F2–F4; NITs F5–F6.
    
    **The S1 fix-round-3 seat** was launched on §8.2 steps 1–12 (Sol 6.0 xhigh; [brief](60-s1-fix3/10-fix-brief.txt) at `77d71d93`). It was told to return F1 with executed evidence and not to add F2/F4 rows.
21. **SAMESIG erratum ruling** ([31](30-sweepclass-samesig/31-coldgate-fable-erratum-ruling.md); [charge](30-sweepclass-samesig/30-erratum-charge.md) at `2daf10a8`).
    - **F1 is TRUE by execution** (E1–E3: a charging bundle's 9.99 W idle baseline becomes the stored anchor; the next campaign reads it and decides `recovered` or `cooldown_cap_hit` from it).
    - **It is pre-existing** (same on main; S1 changes no line of the route), so it does not block S1. It becomes lane **BFGS-COOLDOWN-ANCHOR-01**, which opens now and **must merge before the next scored campaign**. Until then the lead runs the read-only §4.6 anchor pre-check before every scored campaign. W2, a derivation window, is not a scored campaign.
    - F2–F6 are upheld as amendments 66–71. Test-only delta steps 13–19 go to the seat after steps 1–12.
    - **This erratum is not paired with a further refuter.** The ruled stop rule (61 (c)) prescribes exactly one refuter pass, on the final merge candidate, which will exercise amendments 61–71. Pairing each ruling is the mechanism that produced the same-signature spiral. This is a magistrate call, recorded here for Ed and the next cold gate.

22. **PR #432, row 9.** `scripts/shard_tests.py --workers 6` ran on `c5088b87`, which is the integration tree because the base is main `97082508`: 7,525 tests, 50 failures, 0 errors ([tail](20-harvest-gate/31-row9-fullsuite-tail.txt), [log](20-harvest-gate/31-row9-fullsuite.log.gz)).
    - **All 50 are one environmental cause:** the lead ran the suite with the canonical `.venv` interpreter, where `site.ENABLE_USER_SITE` is False. `battery_float_fixture.install_user_site_runner` therefore cannot load into child Pythons ("test interpreter must load the battery fixture in child Pythons"), and child processes read the real battery. The failing modules: `test_install_night_agent` 4, `test_run_night` 8, `test_evidence_night` 23, `test_night_kinds` 15.
    - **Rerun of exactly those four modules with `/opt/homebrew/bin/python3` (3.14.7, user site on): `Ran 483 tests … OK`** ([tail](20-harvest-gate/32-row9-rerun-4modules-python3-tail.txt)).
    - Hosted CI on `c5088b87` passes every test shard. **Row 9 PASS.** Lesson: run the suite with `python3`, never the venv interpreter.
    - The live battery gauge was checked meanwhile: `UpdateTime` age 46 s, connected, not charging, 0 mA. The fixture failure's "UpdateTime stale: 85815 s" is the test's fixed clock against real bytes.
    
    **Row 11:** hosted CI green on `c5088b87` (build, changes, fences, installed-wheel, quick, test 1–6, calibration-exclusive ×3). The post-merge cross-unit look follows the merge.
    
    **Row 12, magistrate terminal review of the exact candidate `c5088b87`:** two files, both generated by governed tools in the order §2.2a prescribes. The pin equals the ledger's terminal receipt (Sol, Opus and Fable each re-derived it). The verdict authenticates, and the single-commit rule holds. No reviewer raised a finding against the bytes. The merge method is a merge commit. **MERGE.**

23. **PR #432 MERGED** at 04:27 PDT as merge commit `a71a5e79` (`gh pr merge 432 --merge`). `gate-ledger` passed and the PR was CLEAN.
    - Canonical was fast-forwarded by `git pull --ff-only` after confirming that no `com.joulewise.night*` label is loaded and no such plist is on disk. It is now at `a71a5e79`, with pin 226.
    - `git log --full-history --no-merges` on the verdict path gives only `c5088b87`.
    - Supervisor staleness: the resident supervisor imports `night_gate.py`, which #432 does not change (NIGHT_HANDBACK §staleness), so no relaunch is needed.
24. **W2 arm, attempt 1** (t0 09:00 PDT 09-27, epoch 1790524800; H = `a71a5e79`). Scripts and outputs are in [40-w2-arm/](40-w2-arm/).
    - Prerequisites: no battery logger, no `ioreg`/`pmset` loop, no Wispr, no tty-attached interactive Claude or Codex.
    - **Step 0 OK** (04:27): battery 0 mA, gauge age 37 s.
    - **Step 1 OK**: full clone (not shallow); ledger byte-equal to W1's 226-row ledger `b03be938…`; head equals pin 226.
    - **Step 2 OK**: staged plan `0395a605…c0ce`, chain `e27978bd…`; three Interactive plists (night `1ed0240a…`, probe `da82415f…`, dead-man `9183da2e…`); epoch-watch rc 3/3 with `os_build` only and the sampler matching.
    - **Step 3 OK.** Census foreign PIDs are all this session's descendants: the S1 seat `codex_exec` 38918/38964 plus MCP servers.
    - **Cold Fable arm gate: ARM** ([06](40-w2-arm/50-armgate/06-armgate-fable-verdict.md); 0 BLOCKER, 0 MATERIAL, NIT 1–7). **Opus lens: ARM** ([07](40-w2-arm/50-armgate/07-armgate-opus-lens.md); NIT 1–5).
    - NIT-6 (daytime window): Ed was told in plain words (Gmail `1a0e2a740c6fa62e`), and W2's cadence report is owed as a disclosed diagnostic at harvest. NIT-7: the S1 seat must be gone before step 4's final census. The README is W1 text (NIT-1): harvest W2 by runbook §2.2a.
    - **Notice accepted**: Gmail `1a0e2a7251f65ea8` at 04:36:39 PDT (epoch 1790508999). `notice.json` filled and `notice-evidence.txt` written ([attempt-000001/](40-w2-arm/attempt-000001/)).
    - **Remaining:** re-check NO, directives and stop files → `step4-publish-install.zsh` (after the S1 seat ends, and no later than about 08:15) → `step5` → stop every child → exit before 08:52.

25. **PR #433 (census, light tier), rows 9, 11 and 12.**
    - Row 9: integration tree `a441703a` (main `a71a5e79` + `3a346c46`), `python3 scripts/shard_tests.py --workers 6`: **7,525 tests, 0 failures, 0 errors, 109 skipped; result PASS** ([tail](50-census/21-row9-fullsuite-a441703a-tail.txt), [log](50-census/21-row9-fullsuite-a441703a.log.gz)). This also re-confirms main after #432 under the correct interpreter.
    - Row 11: hosted CI green on `3a346c46` (every job except `gate-ledger`, which waits on these rows).
    - Row 12: magistrate terminal review of `3a346c46`. Test-only; the production census is untouched; the counterfactual and the `watchdogd` mutation were executed; the independent final review passed. **MERGE.** The merge lands before W2's publication, so no plan is armed at merge time. W2's H `a71a5e79` stays an ancestor of main.

26. **#433 MERGED** (`670756f3`, before W2's publication); canonical was fast-forwarded to `670756f3` while no plan was armed.
    - **S1 seat returned** at 05:54: `blocked`, `partial`, copied to [11-seat-report.md](60-s1-fix3/11-seat-report.md). Amendment 63(a) and the narrowed sweep are implemented and committed unchanged by the lead as `8953c7a5` on `feat/2026-09-26-bfgs-s1-bundles`.
    - It raised three NEEDS_RULING items:
      1. two watched reads that fit no class;
      2. 12 raw-capture members outside `RAW_CAPTURE_READERS`, 11 of kind energy with no preceding gate;
      3. the 64(b) conflict, which is exactly the cooldown-anchor route and is already ruled by the erratum's amendment 66.
27. **W2 ARMED.**
    - Pre-publication checks: NO channels (Gmail from Ed newer_than:1d holds only last night's W1 approvals), directives unchanged, no standdown or STOP file.
    - **Step 4 `STEP4 OK`**: second battery gate PASS (0 mA, age 1 s); `retry_allowed` allowed; **PUBLISHED 05:54:46 PDT** (epoch 1790513686.39). Live launchd probe OK: 300 frames in 40.2 s, median 131.1 ms, p95 135.2 ms, max 137.4 ms; cleanup proven; receipt v2 `c3cadff0…`; install done.
    - **Step 5 `STEP5 OK`**: night calendar 09-27 09:00, dead-man 12:35; installed plists equal the reviewed renders (night `1ed0240a…`, dead-man `9183da2e…`); chain OK. The install-time probe render is `418bbf2a…` against the staged `da82415f…`, as NIT-5 predicted.
    - **Frozen triple:** (`d079-epoch-25g83-derivation-w2-20260927`, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`, `a71a5e7999b5364e8477685b13c6a1e440fa7b27`). **The canonical root must not move until the W2 harvest and uninstall.**
    - Evidence is in [40-w2-arm/attempt-000001/](40-w2-arm/attempt-000001/) and `step4.out`/`step5.out`. The armed email to Ed was accepted as Gmail `1a0e2efcaf043edb`.
    - **Exit rule:** every child is stopped by about 08:20, and the magistrate exits before 08:52 (REQUEST, epoch 1790524320).

28. **Cold ruling S1-FIX3-RETURNS-01** ([21](60-s1-fix3/21-coldgate-fable-ruling.md); [charge](60-s1-fix3/20-coldgate-charge.md) at `ccf9aa9b`; judge tree `8953c7a5`). **No production code inside S1.**
    - The two salvage reads become `non_claim` (i) under a corrected clause (72).
    - Four raw-capture members get the new kind `validation` (73).
    - Three calibration readers are gated today and get the capture form of the gate (74).
    - Five ungated script functions go to the new lane **BFGS-RAWCAPTURE-01**, which opens at S1's merge and merges before the paper's timing numbers are frozen (75).
    - The 64(b) conflict is disposed by 66; the `evaluate_member` reason text is corrected (76).
    - The ordered seat list is steps 20–23 then 13–19, all test-only. Then one refuter pass on the merge candidate.
    
    **Seat round 3b** was launched at 06:18 ([brief](60-s1-fix3/30-seat-brief-round3b.txt) at `9b923643`; Sol xhigh; test files only; hard stop 08:00; codex timeout 6300 s). Its report goes to `/tmp/harvest-3ba66eeb/s1-fix3b-report.md`.

**Next exact action:** open the harvest PR (FULL tier) and run its gate: independent re-derivation audit, contract lens plus execution lens, Opus counter-review, cold Fable final pass, and a full suite on the integration tree. After the merge, plan W2 with t0 at least 6 h after W1's end, under NIGHT_HANDBACK.
