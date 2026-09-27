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
11. **Merge path for the harvest commit.** TIER-01 (i)/(iii)/(v) make the pin and verdict FULL-TIER. The branch-protected `main` requires the gate ledger, so the commit lands by PR. It must merge with a **merge commit, never squash or rebase**, because the verdict-file rule requires exactly one commit that adds the path. W2's arm needs this merged: W2's measurement head must carry pin 226.

**Next exact action:** open the harvest PR (FULL tier) and run its gate: independent re-derivation audit, contract lens plus execution lens, Opus counter-review, cold Fable final pass, and a full suite on the integration tree. After the merge, plan W2 with t0 at least 6 h after W1's end, under NIGHT_HANDBACK.
