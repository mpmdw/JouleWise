# R1 follow-up night arm: notes for the orchestrator (2026-11-12, about 07:30 PST)

Sources read:
- RUN_STATE on `origin/main` `055c8fdfc`: items 286 back to 270, 263, 262, 261, 256, 255, 253, 251, 250 and 249.
- `RESEARCH-LEAD-DECISIONS.md` @ `cc8825611`: RL-59, 64, 72, 84, 89, 90, 91, 93, 94, 95 and 96.
- Presign `bb6394f2b`:
  - the kit and the driver;
  - the chain;
  - `powermode.py`;
  - `run_night._chain_environment`;
  - the contract doc;
  - the kit report;
  - the round-5 delta review;
  - `arm_routes.json`;
  - `w1_prequal.py`.
- The R1 lane `lane/2026-11-10-r1-g0-rop`: `r1_arm.py`, `arm_align_r1.py` and `r1_arm_runbook.md`.
- PRs #739 and #740.

Desk run on the Air, read-only, from a `git archive` of `bb6394f2b` in `tmp/tree-bb63`:
- `validate_sensor_ruling` passed: TV0h/Th0C, table sha `1fdd980c…eba3`;
- config sha `95825997…1dad`;
- `r0_picks` TV0h/Tf08;
- `g0_timeout_s` 1,200;
- `night_worst_case_s`: span 108,768, window 126,480, overhead 9,000, no-redo subtotal 58,711.9616 s.

I did not touch the MBP.

## Blockers

**B1 (TOP). No arm route for the follow-up night exists on the presign line.**
- `scripts/arm_align_r1.py` and `joulewise/align/r1_arm.py` exist only on the R1 lanes: `lane/2026-11-08-r1-arm`, `-arm-fixes` and `lane/2026-11-10-r1-g0-rop`.
  - Neither `0b54827da`, `20e9edbc4` nor `da3187e6e` is an ancestor of presign.
  - `configs/align/v4/arm_routes.json` at `bb6394f2b` declares the R1 route **pinned at `20e9edbc4`**, with "the route lives at this commit, not on the v4 branch". That is the 11-10 night's route.
- The kit says prepare "does not install or arm"; "the lead supplies the ordinary night-plan machine/custody fields through the existing arm procedure" (kit docstring; kit report items 23 and 46).
- `align_v4_session.py prepare` is W1-only, and `launch_align_r0.py` knows only the `r0` and `r1-smoke` kinds.
- The old route cannot be used as it stands:
  1. `r1_arm.wrapper_bytes` runs `"$PY" -B {measurement_root}/scripts/arm_align_r1.py _display-dwell` and `_bookend`, so the file must be in the measurement checkout. A presign checkout lacks it, and the wrapper would exit before the chain.
  2. Its sizing is the old R1's: `R1_RETRY_FLOOR_S` 100,627, base 109,627 s. RL-72 E2 needs `programmed_span_s` 108,768 and `window_max_s` 126,480.
     - The driver arms `_R1_WORK_DEADLINE` = driver start + 108,768 − 900.
     - The driver starts after hazard admission (≤3,300), the display dwell (300) and the pre bookend (≤1,800).
     - So a 109,627 s window can cut a long night short.
     - W1 PREQUAL's R1-plan check (`w1_prequal.py:1401-1404`) fails any R1 plan with span < 108,768 or window < 126,480.
  3. Overlaying untracked route files onto the night checkout is engineering around the problem, and the sizing would still be wrong.
- **Needed:** a port of the route onto presign. It needs:
  - `r1_arm.py` and `arm_align_r1.py`, the runbook and `test_r1_arm.py`;
  - the floor and window set to the follow-up's sizing: span 108,768, window 126,480, two encounters already inside it. Decide whether the wrapper bookends duplicate the "pre/post_bracket 1,800 each" already inside the 9,000 s overhead;
  - the `arm_routes.json` r1 entry re-pointed;
  - a cold review (Fable checks everything) and CI.
- Neither the route files nor the R1-lane `test_r1_arm.py` are condition-13. They do change the commit, so **a second Part A smoke at the final commit is then needed regardless of #739/#740**. Bundle them into one presign commit before about 13:00, smoke after 13:15, and arm by 19:26.
- The draft's arm block is written against the lane interface (`size`, `prepare`, `render`, `install`, `uninstall`) with `__ARM_ROUTE__` as a placeholder.

**B2. Once a plan is installed, the magistrate watchdog will likely hold `HOLD_UNSAFE`.**
- `origin/main`'s `joulewise/night_gate.py` has no `ac_powermode` handling (grep count 0). The canonical root runs main.
- Items 249 and 262 show the watchdog stranding on `extra ['ac_powermode']` in installed plists. The #707 fix is still open.
- Consequence: no magistrate spawns after the night, and the Air lead must unstrand remotely (as at 04:38 on 11-11).
- Optional mitigation in the port: omit `ac_powermode` from the plan. The presign `night_gate` treats it as optional, and absent means 0. That is a design call (Opus final, non-paper engineering).

**B3. `prepare` has never run natively.**
- Kit report, round 5: "No real weights or installed-stack qualification was attempted".
- Tonight's arm would be the first real `weight_digest_preflight` (full hashing of the 27B, 30B and NEG-8 roots) and `runtime_stack_preflight`.
- If either refuses at 19:00, the night is lost.
- Recommendation: a daytime dry run on the MBP, not at the fixed path. Use `--output /Users/edr/night-custody/magistrate/r1fu-prepare-dryrun-<ts>.json` at the current presign head, after the BYTES desk job and outside any smoke capture. It is read-only apart from that output file. It also measures `elapsed_s` per root, so the arm-time budget (I assumed 20 minutes) becomes a number.

**B4. PR #739 CI.**
- At head `2b2defd74` many test shards show FAILURE: shards 2, 3, 5, 6, 7, 8, 9 and 11, plus one gate-ledger.
- RL-91 and RL-96 let it ride only if it is "cold-reviewed and CI green by 12:00".
- If the reds are not inherited, the wrapper stays out, and the RL-91 "without the wrapper" reporting applies. #740's shards were still pending at about 07:10.

## D-7 and D-8 definitions (cited)

- **D-7 (MEDIUM, before the arm).** "A packet left at the fixed path by an earlier night is accepted if that night ran the same commit. Nothing binds the packet to this plan or to a date."
  - Source: `docs/run_reports/2026-11-11-r1-followup-kit-delta-coldreview.md`, Round 5 delta (Fable 5.2, 2026-11-11 15:20), the verdict bullets. Detail is under "D-2: … can a stale packet be picked up?". It is listed under "Owed before the arm" item 1.
  - The procedural fix is adopted in `docs/align/r1_runtime_contract.md` lines 25-37 ("Arm step for the packet (Fable kit delta review D-7, procedural route; no code change)"). It has three steps: delete the old packet, run prepare on the final commit and record its SHA-256 in the arm notice, then arm and compare the arm record's packet SHA-256.
  - It is procedural because the driver is a condition-13 file.
- **D-8 (LOW, test gap).** "No test stops the chain from honouring an inherited `ALIGN_R1_PREPARE_PACKET`."
  - Source: the same review, mutant R2d SURVIVED; "Owed before the arm" item 2: "the decoy-variable assertion. Test only."
  - **Already discharged at `bb6394f2b`.** `tests/align/test_r1_rehearsal.py` around line 79 ("D-8 (Fable kit delta review)") runs the chain with a decoy env var and asserts that the argv names the fixed packet path.
  - The chain line `ALIGN_R1_PREPARE_PACKET="$MEASUREMENT_ROOT/.align-r1-prepare.json"` is unconditional.
  - Remaining: confirm the test is green on the final head (it is in `tests.align.test_r1_rehearsal`).
- RL-89 ("D-7 and D-8, which are not mine") and the ruling file's `conditions[4]` both name them, so the lead must state them closed in the arm item. The draft does this.

## Night lock (answer to the specific question)

The arm/prepare path does **not** refuse on the stale `night.lock`.
- `powermode.HostLock` is an exclusive `fcntl.flock` on `/Users/Shared/JouleWise/host-power/night.lock`.
- `acquire()` opens the file `O_RDWR|O_CREAT` and rewrites the JSON as "the holder note is diagnostic only".
- A dead writer's file blocks nothing. Every smoke close since item 274 acquired the lock over a stale file and rewrote it (52565 → 50618 → 58535 → 77434).
- The only real failure modes are an open descriptor held by a live process, or a file edr cannot open (EACCES, the item-249 class).
- So the draft says: never delete it, since deleting a flocked inode splits the lock. Check only that the pid is dead, `lsof -t` is empty and the owner is edr.

## Assumptions I could not verify from the docs

1. **19:26 derivation.** RL-72 states only the limit. I infer 19:26 = 11:45 − the no-redo subtotal (58,711.96 s → 11:44:32 next day), which matches to the second. The design-round plan document itself is not in the repo.
2. **The measurement checkout.** I assume `$M` = `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2`, last at `da3187e6e` (item 256), with its `.venv`. The smokes used its interpreter.
   - The plan, `run_night` (`PY = measurement_root/.venv/bin/python`) and `prepare_checks` all need `.venv` in the measurement root, so the smoke worktree cannot serve.
   - Moving `$M` by fetch plus `switch --detach` follows item 256. I have not verified that `$M`'s current HEAD and status are clean.
3. **Arm-route interface and sizing:** see B1. I assumed the lane's CLI and `ARM_NOTICE_S` of 15 minutes, `plan_id` prefix `align-r1-` (`run_night._chain_outcome` and `plan_kind` depend on it), `HAZARD_PACK`, and installer cutoff t0 − 300 s.
4. **Network-time read.** `sudo -n systemsetup -getusingnetworktime` is assumed to be permitted and non-interactive. Earlier items report "Network time Off (read …)" without the command.
   - The frequency-word read uses `joulewise.kernel_clock.read_kernel_frequency` (`ntp_adjtime` modes 0, documented read-only).
   - The zero script path is from item 251.
5. **`sudo -n -l /bin/kill -KILL 1`** as an argv-shape listing: this is standard `sudo -l command` semantics (list, do not run). That the MBP sudoers rule is literally `/bin/kill` with any arguments is unverified. RL-96 only says "must be permitted".
6. **`prepare` duration.** I assumed 20 minutes; unmeasured (B3).
7. **D-7 step 3 timing.** The driver writes `prepare_packet.sha256` only in `r1_result.json` at its terminal write. So the binding comparison happens after the night, and the draft adds an immediate re-hash before exit. A mismatch found after the night voids the night ("a refused arm"). Confirm that this reading of "after the arm" is acceptable.
8. **The Tf08 release value.** Item 286 says the G0 release record holds only fast and slow. I assumed Tf08 at release can be read from the sidecar journal (`record_keys`); RL-90 requires it printed.
9. **The `night-results/<plan_id>` ref.** I assumed it is still pushed by the courier for this route (item 253 precedent), and that the Air watcher's early-refusal alarm can key on it.
10. **Commits from the magistrate.** I assumed the magistrate commits its arm trace from the canonical root, not `$M`. No git is allowed in `$M` after install.
11. **TMPDIR.** The rule "export TMPDIR=/Volumes/JW-EXT/scratch/arm-r1fu/tmp" was applied to my own commands on the Air. The draft's MBP commands do not set it, because that path does not exist on the MBP.

## Open questions for the orchestrator

1. **B1 route:** port the R1 arm route to presign with RL-72 E2 sizing (Sol build, Fable cold review, CI) and bundle it with #739/#740 into one commit for a single second Part A smoke after 13:15? Or another route? Without this, nothing can arm tonight.
2. **The bookends.** Does the ported wrapper keep the two D-109 bookends and the 300 s display dwell outside the 108,768 s span (window 126,480 still covers them: about 116k worst case)? Or are they the "pre/post_bracket" already counted in the 9,000 s overhead, in which case drop them?
3. **The `ac_powermode` key (B2).** Omit it from the plan so main's watchdog can read it, or accept a stranded watchdog and an Air-side unstrand after the night?
4. **A daytime prepare dry run (B3)** on the MBP after the BYTES desk job: authorize it?
5. **The #739 CI reds (B4).** Inherited or new? This decides whether the wrapper (and the `sudo -n -l /bin/kill` check) is in.
6. **Network time after the night.** The draft says leave it OFF, because W1 follows. Runbook §4 says ON, then zero before the next arm. Confirm.

## Update 07:07 PST: orchestrator decisions applied

- **B1 is closed by the port.**
  - `fix/2026-11-12-r1fu-arm-route` @ `683dfe654`, three commits: the verbatim lane copy `b5b76b597`, the fail-first tests `ec09bf83c`, then the fix. It is pushed; no PR has been opened.
  - Sizing: the route takes the driver's span from `night_worst_case_s` and refuses anything but 108,768 s. The base is 117,768 s. `window_max_s` is 126,480 s for every t0.
- **Bookends (Q2) are not ambiguous.**
  - The 9,000 s overhead is the driver's OWN segments:
    - `pre_calibration_bracket` and `post_calibration_bracket` (`r1_phase_table.py:51,69`; kinds `calibration-pre`/`-post`), 1,800 s each in `align_r1_rehearsal.phase_bound` and `_run`;
    - close 900;
    - harvest 4,500.
  - `night_worst_case_s` excludes them from the admission units and adds them as overhead.
  - The wrapper's D-109 bookends (`validate_powermetrics_fiducial.py`, `r1_arm.bookend`) and the 300 s dwell run outside the driver in `r1_arm.wrapper_bytes`. They are extra, and the window covers them. The 11-10 night ran both: `bookends/*.json` plus the driver's `pre_calibration_bracket`, item 253.
- **`ac_powermode` (Q3) is dropped from the plan.**
  - Absent means 0 (`night_gate.py:446-449`). Admission still runs at Automatic: the e2e night.log shows "ac powermode admitted: expected 0 observed 0".
  - The R1 driver's `PowerModeGuard` owns the A-B-A and series transitions and the restore (`r1_runtime_contract.md`, host-level admission).
  - Checked: main's `NightPlan.from_mapping` accepts the ported plan, and with the key it raises "plan keys are not exact … extra 'ac_powermode'". So B2 is resolved.
- **Hazard allowlist / host-command guard:** both modules pass without new rows. The new modules are not in either scan scope. A reviewer may want a `not_scanned` row for `r1_arm.py`, but it was not needed for green, and changing `hazard_refusals.json` touches pinned registry text.
- **Condition 13:** untouched. None of the ten `R1_EXECUTED_SOURCES` is in the diff. The arm route was not condition 13 for the first night either.
- **Note for the reviewer:** `tests/align/test_w1_prequal.py::RouteTests.test_r1_route_is_pinned_at_its_armed_commit` still passes, but its name now describes the old pin.
