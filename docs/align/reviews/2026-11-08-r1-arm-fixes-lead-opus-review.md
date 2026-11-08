# R1 arm route, fix branch: lead's independent Opus executing review (item 219)

- **Target:** `lane/2026-11-08-r1-arm-fixes` @ `20e9edbc446a9f89a68badc1bd32bb0934cbb86d`.
  - Sol route `0b54827da`, magistrate review `5c0b79d31`, then the D2/D3/D5 fixes and runbook lines.
- **Reviewer:** laptop lead's Opus 5.5 seat (cross-family; Sol built the route and the fixes).
- **Where:** a detached worktree at `20e9edbc4` on the Air.
  - `TMPDIR=/private/tmp/r1armrev`, `JW_B5_SYNTHETIC_ONLY=1`, Python 3.13.18, one module per process.
- **Scope:** read nothing under custody, archive or restricted paths.

**VERDICT: ADMIT_WITH_FIXES. The one required fix is an arm instruction (N1), not a code change. Arm `20e9edbc4` itself; no descendant sha is needed.** No BLOCKER or HIGH.

## Executed

| Check | Result |
|---|---|
| `tests.align.test_r1_arm` | 9 tests OK. Both e2e cases ran, with their `R1_SYNTHETIC` lines. |
| `tests.align.test_r1_runtime` | 33 OK |
| `tests.align.test_v4_kit` | 116 OK |
| `tests.test_run_night` @ `20e9edbc4` | 318 run. One ERROR: `Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` (`SystemExit: 19`). No other failures. |
| `tests.test_run_night` @ `e901eb2a4` (base) | 318 run. The same single ERROR (`SystemExit: 19`), so it is pre-existing and not caused by this branch. |
| e2e normal, re-run alone | OK. exit 0, `r1_status` complete, power mode 0, host lock reacquired. The display journal reads `displaysleepnow` (flagged; synthetic pmset rc 7), then `dwell_start` and `dwell_end` 300 s apart. Both bookends are flagged `r1.bookend_failed` (rc 7) and do not veto. `meter_supervision.jsonl` is present. |
| e2e interrupt, re-run alone | OK. exit 130, `r1_status` aborted. A competing host-lock admission was blocked during High Power `[true]`. Mode was restored to 0, both power markers are gone, `chain.exited` is written, and child terminations are proven. |

## 1. D2 sizing: verified

`size --t0` (CLI) gives the following base terms:

| Term | Seconds |
|---|---:|
| `r1_retry_floor_s` | 96,427 |
| `hazard_arm_s` (`b5/plan.py:59`) | 3,300 |
| `bookends_s` | 3,600 |
| `close_s` | 1,200 |
| `harvest_s` | 600 |
| `display_dwell_s` | 300 |
| **Base** | **105,427** |

| t0 (PT) | Crossings in `[t0, end)` | `window_max_s` |
|---|---:|---:|
| Sun 11-08 01:04 (now + 15 min, tonight) | 1 (Sun 11:45) | 105,427 |
| Sun 11-08 08:00 | 2 (Sun, Mon) | 116,591 = 105,427 + 11,164 |
| Sun 11-08 13:30 | 1 (Mon) | 105,427 |
| Mon 11-09 08:00 / 13:30 | 2 / 1 | 116,591 / 105,427 |
| Sun 11-08 11:45 exactly | 2 (t0 inclusive) | 116,591 |

- **Fixed point.** `crossing_size` recounts local 11:45 instants in the half-open window until the size stops changing. Each added encounter (11,164 s) is shorter than any local day, so the count cannot run away. I checked each value above by hand against the end instant.
- **Plan acceptance.** I ran `prepare` for t0 at 08:00, 11:45, 13:30, 23:00 and Mon 01:30. Each plan is accepted by `NightPlan.from_mapping` and `run_night.schedule`. In every case `deadman_epoch` comes after `t0 + window_max_s + COURIER_DEADLINE_S`. A non-whole-minute t0 is refused (`PlanError`) before any custody is written.
- **Enforcement.** `run_night.py:1157` arms `_WindowDeadline` at `t0 + window_max_s + WINDOW_SHUTDOWN_GRACE_S (300)`.
- **Worst case with one crossing and no redo.** Every pre-R1 stage is at its cap:
  - hazard arm 3,300 s;
  - dwell 300 s plus about 5 s of interpreter start and pmset;
  - pre bookend 1,800 + 30 s grace;
  - R1 floor 96,427 s.

  That puts R1's end at t0 + 101,862 s, against a deadline of t0 + 105,727 s, which leaves **3,865 s of slack**. The post bookend (at most 1,830 s) also fits. The deadline cannot cut R1 short in this case.

## 2. D3: verified

- **Wrapper order:** digest gate, then `_display-dwell` (with `|| exit $?`), then the pre bookend, then R1, then the post bookend.
- **`display_dwell`:**
  - runs `/usr/bin/pmset displaysleepnow`;
  - records `exit_code`, with flag `r1.display_sleep_failed` on a nonzero rc or an `OSError`;
  - records `dwell_start`, sleeps 300 s, and records `dwell_end` in `night/r1_wrapper.jsonl`.
- **Tests:** rc 0, rc 7 and a missing pmset all get the full dwell and return 0. In the e2e run, the pre bookend saw `dwell_end` as the last record.

## 3. D5: verified

- **Literal matches the file.** `prepare` on this worktree wrote `40a49bde4475c583719dc178d5f66963abe29918350b288a829c91bf54946be0` into `chain.zsh`. That equals `git show 20e9edbc4:scripts/night_chains/align_r1_rehearsal.zsh | shasum -a 256`.
- **Mismatch handling.** The test changes one byte after generation. The real zsh wrapper then exits 65. No sentinel helper runs, and no `r1_wrapper.jsonl`, bookend or `align-r1` output is created. An environment digest set to the mutated bytes does not override the literal.

## 4. Nothing frozen changed: verified

- **Measurement code, unchanged:** `git diff --stat e901eb2a4..20e9edbc4` is empty for:
  - `scripts/align_r1_rehearsal.py`, `scripts/night_chains/`, `scripts/run_night.py`;
  - `joulewise/night_gate.py`, `scripts/magistrate_watchdog.py`;
  - `joulewise/b5/`, `joulewise/hazards/`;
  - the installer (`.sh` and `.py`), `validate_powermetrics_fiducial.py` and `km003c_monitor.py`.
- **Changed by the route and its fixes:** `joulewise/align/r1_arm.py`, `scripts/arm_align_r1.py`, `tests/align/test_r1_arm.py`, the runbook, two `.codex-report` files and the magistrate review.
- **Also in the range, from the parents of the route (not on main):**
  - `5d9b66dd4` (R0 reasoning_effort fill, kit regenerated);
  - `d9d1098c6` (`r1_runtime.json` sensors TV0h/Tf08, fans F0Ac/F1Ac, r0 sha256; with matching test fixture edits).

  These are R0-result config fills, not code. Kit and runtime suites pass on them.

## 5. Arm safety: verified

- **Quiet guard, external-volume and display rules.** R1's driver is unchanged. Ruling-20 `ExternalVolumeWatch` is at `align_r1_rehearsal.py:1457`, and the R1 quiet segments and redos are unchanged. The hazard monitor only journals. The display rule is now enforced twice: the D3 dwell, and the bookend's `--sleep-display-before-capture`.
- **KM003C.** `production_seams.meter_argv` (`b5/driver.py:740`) starts `scripts/km003c_monitor.py --out <custody>/hazards/meter/...`. It runs until signalled and starts before the chain (`driver.py:2457`). It is a supervised diagnostic, and its absence is a flag, not a veto. The e2e run writes `meter_supervision.jsonl`.
- **Interrupt.** Automatic is restored and the host lock is released (e2e above). The wrapper's `trap 'exit 130'` starts no fresh bookend.
- **No double arm.** `prepare` refuses existing custody (`mkdir exist_ok=False`, tested). The installer refuses `night_agent_already_loaded`. `run_night` refuses `night_refused_agent_present`, and the R1 host lock blocks a second admission.
- **Install and uninstall,** run against this plan with a fake `launchctl` and `HOME`:
  - `--render-only` validated the pins (`repo_head` = `measurement_head` = `20e9edbc4`) and rendered the night, deadman and probe plists.
  - `--uninstall` booted out and verified both labels absent, then removed both plists. rc was 0, and it printed `--python ignored on uninstall`.
  - With an unknown launchctl result it failed closed (rc 4) and kept the plists.

## Findings

- **N1, MEDIUM, required arm instruction. The runbook fetches the wrong branch.**
  - The problem: runbook §1 fetches `refs/heads/lane/2026-11-08-r1-arm`. That branch is `5c0b79d31`, the unfixed route. Following the runbook literally would arm a head without D2/D3/D5: a 105,127 s fixed window, no dwell and no literal pin.
  - The instruction: item 225 must tell the magistrate to run `git -C "$M" fetch origin 20e9edbc446a9f89a68badc1bd32bb0934cbb86d`, or fetch the `-fixes` branch, then `switch --detach` to it. Before install, confirm two things:
    - `git -C "$M" rev-parse HEAD` = `20e9edbc4…`;
    - `night_plan.json` `repo_head`/`measurement_head` = `20e9edbc4…`.
  - No code change is needed. Correct the runbook text in a later commit.
- **N2, MEDIUM, known and disclosed.** There is no allowance for a ruling-8 load redo. One redo costs up to 6,429 s against the 3,865 s worst-case slack, so it fits only when the arm and bookends finish under their caps (as is usual). This meets item 216's floor; the magistrate review raised it earlier. If the deadline does fire, TERM restores Automatic.
- **N3, LOW. The D5 literal comes from whatever bytes the checkout holds at prepare, not from the committed blob.** A dirty checkout would be pinned as-is. The fix: `git status --short` must be clean before `prepare`, and the literal in `$S/chain.zsh` must equal `40a49bde…946be0`.
- **N4, LOW. A records fault in `_display-dwell` exits the wrapper before R1** (`|| exit $?`). Only an unhandled exception does this, such as a write failure on `night/` or a failed import. That is fail-closed, and R1 could not record its own output under those faults either.
- **N5, LOW, carried from the magistrate review.**
  - The bookends omit `--ledger`, so D-109 rows go to `$M/runs/calibration_observation_ledger.jsonl`. That file is gitignored, so neither the heads nor the pin is affected.
  - `uninstall` passes `--python`, which the installer ignores (confirmed).
- **Environment note.** This review ran on the Air, which has no live meter, pmset, launchctl or powermetrics. Hardware behaviour remains the magistrate's live check.
