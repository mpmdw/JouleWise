# Activation 22784e38 — record 00

Magistrate activation `22784e38-8bb5-4497-a9f6-ab53e291ee58`, launched by the watchdog at 22:34:00 PDT 09-26 (Opus 5.5, attempt 109, supervisor PID 70177, session PID 70181). Predecessor 92472459 exited on purpose at about 22:30 so that a fresh supervisor could arm W1 (its record 00, item 36).

1. **Launch.**
   - Heartbeat written at epoch 1790487250.
   - Watchdog `notice_pending` = `[]`; no standdown request.
   - Gmail `from:claude2.glaring610@passmail.net is:unread` over all threads: **none**.
   - Open directives: #422, #421, #417, #416, #408, #405. None is new, and none stops W1.
   - No `com.joulewise.night*` label is loaded and no such plist is on disk.
   - Canonical is clean at `97082508` = `origin/main`.
   - Launch email accepted as Gmail `1a0e15bc811ddb3e`, then `notice.ack` was written.
   - Worktree `/Users/edr/code/JouleWise-wt-22784e38`, branch `docs/2026-09-26-22784e38` (from `origin/docs/2026-09-26-92472459` @ `c101f32c`).
2. **W1 arm attempt: prerequisites.**
   - Battery reads connected, not charging, InstantAmperage 0 mA, FullyCharged.
   - `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` sha256 = `81b65f08…ddf1` (matches the A-R5b pin).
   - No battery-log process, and no `ioreg`/`pmset` loop.
   - The arm scripts from `docs/2026-09-25-817355d2-w1arm` @ `c79816c9` were copied to `10-w1-arm/scripts/` in this worktree (untracked; see item 4). They were filled with H = `97082508f3648ff8575c94b0cdfcf657ba440142`, T0 = `1790494200` (00:30 PDT 09-27) and PREREG = `81b65f08…ddf1`.
3. **Step 0: PASS** (22:37:44 PDT).
   - Build 25G83; no night label or plist.
   - All six custody plans are TERMINAL.
   - The battery gate passed: ExternalConnected Yes, IsCharging No, signed current 0 mA, UpdateTime age 59 s. It created staging `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260927/` holding `battery-gate.txt`.
4. **Step 1: REFUSED**, `calibration_ledger_rollback`. The clone, the lock match and the ledger byte-copy all passed. Then `load_calibration_ledger_snapshot(..., verify_custody=True)` refused.
   - **Root cause (arm-script defect, not a code defect):** `arm-env.zsh` sets `LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl`.
   - The canonical ledger is the 76-row pre-n1 file (sha256 `aa806848…`).
   - The committed pin (`configs/calibration/calibration_ledger_head.json`, commit `1278b9f7`) is sequence 176, digest `0f7609ae…2512`. The n2 night wrote it.
   - The 176-row ledger lives at `/Users/edr/JouleWise-measurement-20260919-derivation-n2/runs/calibration_observation_ledger.jsonl`. Its sha256 is `95d152f0…5302`, equal to the n2 harvest record (`docs/process_traces/2026-09-19-activation-d0b83820/01-harvest-evidence/ledger-176-sha256.txt`).
   - The n2 arm pinned its source the same way (`LEDGER_SOURCE_EXPECTED_SHA256`).
   - The authenticator refused correctly; the gate worked.
5. **Bench fix DENIED by the auto-mode permission classifier** ("Security Test Removal").
   - The denied batch had two parts:
     1. Point `LEDGER_SOURCE` at the n2 ledger, add `LEDGER_SOURCE_EXPECTED_SHA256` plus a digest check in step 1.
     2. Move the refused partial clone `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1` to `~/night-archive/`.
   - A follow-up read-only `git status` in this worktree was then also denied.
   - Under the denial's terms the magistrate does not pursue that outcome by any route, including seats. **W1 is not armed this activation.** Ed is asked by email to rule on it.
   - Left on disk, untouched:
     - the partial clone above (step 1 requires the measurement root to be absent, so a re-arm must move it);
     - staging `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260927/` (step 0 requires it absent; a re-arm with a new t0 changes `NIGHT_DATE` only if the date changes, otherwise it must be moved);
     - the untracked `10-w1-arm/` directory in this worktree (filled scripts, `step0.out`, `step1.out`).
6. **Owner email: the W1 block** (Gmail `1a0e16172f3388bf`). It asks Ed for "YES ledger fix" (approve (a) + (b) of item 5, optionally with an allow rule), or for (b) done by hand. **Fallback lane: the SWEEPCLASS erratum cold gate was convened** (charge [20-coldgate-sweep-erratum/00-charge.md](20-coldgate-sweep-erratum/00-charge.md), commit `405199bd`, sha256 prefix `683a014c`).
   - The cold Fable judge runs in `JouleWise-wt-s1swcg-92472459` @ `cbfa9dc3`, pinned for the session. Script: `~/.claude/jobs/22784e38/tmp/convene-coldgate-swerr.sh`.
   - The paired Opus contract refuter runs in parallel (Section A independent; Section B after the ruling).
   - Astra is not seated: this is a design-closure erratum on test-code amendments, with no new science. The same omission was recorded for SAMESIG.
7. **Owner instruction (Ed, Gmail message `1a0e163a9a06c137`, thread `1a0e16172f3388bf`, 22:43:13 PDT 09-26), verbatim above the quoted text:**

   > Explicit "YES ledger fix" . A and b approved.

   Applied: (a) `LEDGER_SOURCE` → the n2 ledger with `LEDGER_SOURCE_EXPECTED_SHA256 = 95d152f0…5302` plus a digest check in step 1; (b) the refused partial clone moves to `~/night-archive/`. The W1 steps are then re-run from step 0.
8. **W1 re-run after Ed's approval.**
   - (b) done: the refused clone was moved to `~/night-archive/w1-step1-refused-clone-22784e38`.
   - (a) done: `arm-env.zsh` `LEDGER_SOURCE` → the n2 ledger plus `LEDGER_SOURCE_EXPECTED_SHA256`; `step1-clone.zsh` gains the digest check.
   - **Step 1: PASS**: the digest check passed, the byte copy passed, and `authenticated head-equals-pin 176 0f7609ae…2512`; tree clean.
   - **Step 2: STOPPED** at its epoch-watch expectation line. Every check before it passed: clone = H and clean; A-R5b, frozen plan and both template digests exact; 0 placeholders; A-R5b heading ×1; `check_rc=3 prereg_rc=3`; `pre-registered powermetrics sha256 b762e5bf…: match`.
   - The script requires `mismatched fields: os_build, powermetrics_sha256`, but the watch now reports `mismatched fields: os_build` only.
   - **Cause:** `scripts/issue_calibration_acceptance_generation.py` (lines ≈410–416) takes the expected `powermetrics_sha256`/`mlx_version` from the ledger's **last row's T1 bindings**. The script's expectation was written against the stale 76-row ledger, whose last row is 25F84 with sampler `d1dccad0…`. The correct 176-row ledger ends on n2 (25G83), whose sampler is `b762e5bf…`, equal to today's `/usr/bin/powermetrics` sha256. So the one remaining mismatch is the old r7 acceptance's `os_build` 25F84, which is the explained mismatch the runbook (§0.3) expects.
9. **Expectation change DENIED** by the auto-mode classifier ("Security Test Removal"). The change was: replace the two `os_build, powermetrics_sha256` expectation lines with `os_build`, plus an explicit `powermetrics_sha256 … b762e5bf… b762e5bf… match` row. Running step 2 with it was denied; Ed approved (a) and (b) only. The edit was reverted: `step2-desk.zsh` is byte-identical to `c79816c9`. Nothing past step 2 ran: no `NIGHT_ROOT`, no plan, no notice. Ed is asked by email.
10. **Owner instruction (Ed, Gmail message `1a0e16a14d318643`, thread `1a0e16172f3388bf`, 22:50:14 PDT 09-26), a reply to the (c) ask, verbatim above the quoted text:**

    > Yes, explicit permission to do whatever you need to do to arm W1, replace old
    > stuff, override old rules, anything you need to do as long as the science is
    > sound. Even grant you permission to update the necessary config files or
    > whatever, just solve this yourself

    **The magistrate reads it as:**
    - (c) is approved;
    - so is any further arm-script correction needed to arm W1, as long as it leaves every science-bearing gate in place: the battery gate at step 0 and immediately before publication, ledger authentication, the digest pins, the epoch watch, the census, a cold Fable pass on the staged plan, and the arm notice with Ed's NO window.

    Process-rule, decision-log and skill-doctrine changes stay with the cold gate or Ed (magistrate charter), and none is needed for this arm. Each correction is recorded here with its cause.
11. **(c) applied under item 10's licence; step 2 re-run.** It passed the epoch watch (`mismatched fields: os_build`, sampler `b762e5bf… match`), the digests, the frozen-plan copy, identity-epoch and T1 JSON, the staged plan (`/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260927/night_plan.json`), and wrapper generation and verification (chain sha256 `ccaeac64…b956`). Preflight OK ×2. Validated pins: repo_head = measurement_head = `97082508`.
    - **It stopped at the render-only assertion.** The script expects exactly the night and dead-man plists, but the installer's render mode has also emitted `com.joulewise.night-probe.<PLAN_ID>` since `d1aadecc` (`night_agent_install.py` `main()`: `target.labels += (probe_label(...),)`). All three render `ProcessType=Interactive`: night `d082e61c…`, probe `562e4341…`, dead-man `f2074d38…`. Step 3 has the same two-label set.
12. **(d) DENIED by the classifier**, despite item 10's licence: widen the step-2 and step-3 render label sets to require the probe plist too (equally strict: exact set, Interactive, digest recorded). The magistrate does not pursue it. It will ask Ed for (d) together with anything else a read-only Sol dry-scan of steps 2–5 finds (`40-w1-script-scan/`), in one batch.
13. **Read-only Sol dry-scan of steps 2–5** ([40-w1-script-scan/11-scan-report.md](40-w1-script-scan/11-scan-report.md)).
    - F1/F2 = (d), confirmed.
    - F3: step 3's notice header names the retired `claude.ai.copper531` address.
    - F4 (make `arm_census` final output blocking) and F5 (block on any open directive) are **rejected by the magistrate**:
      - F4 would count the live magistrate as foreign at publication; the production t0 census (`arm_readiness_evidence_t0`/`night_gate`) is the fail-closed gate.
      - F5 would block on the six benign open directives; the README makes directive review a lead act.
    - No other stale flag, key or receipt field was found. The scan notes step 2 cannot be re-run over an existing staged plan.
    - Ed was asked for "(d) probe plist in the render sets, (e) the address fix, (f) move tonight's partial W1 outputs (staged plan, rendered-agents, the `NIGHT_ROOT` folder) to `~/night-archive/` and re-run step 2" (Gmail `1a0e1735d1f7d166`).
14. **Owner instruction (Ed, Gmail message `1a0e17772e3044ca`, thread `1a0e16172f3388bf`, 23:04:50 PDT 09-26), verbatim above the quoted text:**

    > YES def the email change is superfluous, both are aliases to my real mailbox, so send to whichever, I'll get all the emails, as long as you can manage replies

    Applied: (d) and (f). (e) is not applied: Ed calls it superfluous, and the notice is sent by hand to `claude2.glaring610@passmail.net`, where replies are searched. **Correction to the 23:00 email:** it said the installer's probe render dates from "a July change". `d1aadecc` is dated 2026-09-17.
