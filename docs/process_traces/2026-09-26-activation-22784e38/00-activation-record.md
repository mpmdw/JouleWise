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
