# Executing review: ALIGN v4 R1 integration head (2026-11-06)

**Verdict: ADMIT_WITH_FIXES.** Two HIGH findings are fixed on the lane (`14f1dd875`, `b6a48037f`), each with a test that fails without its fix. One HIGH finding is still open: a crash or SIGKILL during the High Power leg leaves the host at powermode 2 for every night except the next R1 night. That can be handled by an operator runbook step for the rehearsal, but it needs a host-level fix before the D-series. Five MEDIUM findings are open. R1 still cannot run, because the WP15 runtime does not exist yet (see the run report's prerequisites).

Reviewer: Opus 5.5, executing review of `lane/2026-11-06-v4-r1-integrated@bb878f3b5` against `origin/lane/2026-11-05-align-pilot10-benign` (which contains the R0-merged kit `f3af22b94`). I did not write this code.

Read:
- `docs/run_reports/2026-11-06-align-v4-r1-integration.md`;
- the council `CHAIR.md` and `LEAD-RULINGS-1.md`, as carried on the lane;
- the full diff of `scripts/align_r1_rehearsal.py`, `scripts/night_chains/align_r1_rehearsal.zsh`, `joulewise/align/apple/{powermode,r1_runtime_contract,thermal_gates,workload}.py` and `scripts/align_v4_kit.py` (`require_ready`/L1);
- `scripts/run_night.py` group termination (`killpg` TERM → wait 30 s → KILL);
- `joulewise/environment.py` `_parse_pmset`.

Nothing restricted was opened, no weights were loaded and nothing ran on the measurement Mac. Every run used `/private/tmp/jwsol/venv-both/bin/python` under `nice -n 19 taskpolicy -b` with `TMPDIR=/private/tmp/jwwf-tmp`.

## What I executed

1. **The whole `tests/align` suite, one module per process:** all 105 modules rc=0, **Ran 1297 tests, OK (skipped=32)**, on bb878f3b5 (MoE calibration alone took 1,527 s). Three modules ran at a time. My two commits touch only the R1 driver, its chain, its tests and the contract doc. On `b6a48037f`, `test_r1_rehearsal` and `test_r1_runtime_contract` give Ran 40 tests, OK: 29 + 3 new + 8.
2. **WP22 synthetic W1 dry run** (`JW_WP22_FULL=1 -m unittest tests.align.test_v4_w1_synthetic`): on `b6a48037f`, **Ran 18 tests in 101.671 s, OK (expected failures=2)**. The two expected failures are the documented F2/F3 design divergences. The injected window behaves as the run report states (ordinal 8 g0_timeout failed, and the rest as designed).
3. **Real-process exit-path harness for the R1 chain** (scratch only, not committed).
   - Setup:
     - the real `align_r1_rehearsal.zsh` runs in its own session, as `run_night` starts it;
     - a fake narrow `sudo` on `PATH` (only `-n -l` and `-n /usr/bin/pmset -c powermode 0|2`) writes a state file;
     - the driver runs with only its read-only `pmset -g custom` query faked from that state file;
     - a fake WP15 runtime serves the test-suite `FakeWorld` payloads and can block in one kind;
     - signals go to the whole process group with `os.killpg`, as `run_night` sends them.
   - Results:

| Scenario | Chain rc | Final AC powermode | Marker left | r1_result status |
|---|---|---|---|---|
| normal completion | 0 | 0 | no | complete |
| one SIGTERM / SIGINT / SIGHUP during the B leg | 130 | 0 | no | aborted |
| **burst of SIGTERMs (0.4 s apart) during B, 1 s restore, on bb878f3b5** | **-15** | **2** | **yes** | **(no file)** |
| same burst after `14f1dd875` | 130 | 0 | no | aborted |
| SIGKILL of the group during B | -9 | 2 | yes | (no file) |
| … then the next R1 night (same MEASUREMENT_ROOT) | 0 | 0 | no | complete; startup restores ran before any runtime work |
| `run_night` TERM → 30 s → KILL with a restore that takes 40 s (artificial) | -9 | 2 | yes | (no file) |

4. **Adversarial evidence probes against the driver** (scratch):
   - P1 gated-run T_dead;
   - P2 load-journal length;
   - P3 L1 with a large tail;
   - P4 the generic environment gate on powermode 2.

   Results are below.
5. **Kit checks:**
   - `git diff origin/lane/2026-11-05-align-pilot10-benign HEAD -- configs/campaigns/align_pilot_v3` is empty.
   - `scripts/align_v4_kit.py --check` exits 1, blocked on the 13 named placeholders (WP11, WP18, R0, R1, WP15). It fails closed.

## Findings

### HIGH-1 (FIXED `14f1dd875`): a burst of signals left the host in High Power
- **Mechanism, driver.** `run()`'s handler raised `KeyboardInterrupt` on every signal. A second TERM or INT during teardown therefore interrupted both Python restore attempts (`__exit__` and `finally`), killing the restoring `sudo`.
- **Mechanism, chain.** The chain's `on_signal` ran `trap - EXIT HUP INT TERM`. The next TERM then killed the shell and its restoring `sudo` with the default action.
- **Evidence.** Harness row 3: rc -15, powermode 2, marker left and no `r1_result.json`. A second Ctrl-C from an operator, or any TERM burst, is enough.
- **Fix:**
  - The driver's handler is one-shot. It sets `SIG_IGN` for INT, TERM and HUP; the restoring `sudo` inherits that, and the old handlers return in `finally`.
  - `on_signal` uses `trap '' HUP INT TERM` (ignore) and keeps `trap - EXIT`.
- **Tests, both failing on bb878f3b5:**
  - `test_signal_burst_cannot_interrupt_the_automatic_restore` sends a second signal in-process during the restore.
  - `test_zsh_chain_signal_burst_still_restores_automatic` runs the real zsh chain with a fake `sudo` that signals the group mid-restore.

### HIGH-2 (FIXED `b6a48037f`): gated D runs' T_dead was taken on trust, so the duty bar could falsely pass
- **The gap.** Ruling 1(d)'s duty bar is G0 + G1 + H ≤ 40 % of T_dead. The driver used whatever `deadman.T_dead_s` each gated run reported.
- **Probe P1.** The three runs reported 900 s, 5,000 s and 1,451 s. The step-d slot was 1,451 s, and 5,000 s is past the workload's own 1800/1.13544 bound. R1 still exited 0 with `duty_bar.pass = true`.
- **Fix.** The deadman armed at G0 entry, and shared by G0, G1 and H, must be the one T_dead that R1 freezes. Each gated run is now checked against the step-d `slots.T_dead` as soon as it returns. R1 refuses at that run, fails fast and still restores powermode. The contract doc now states this.
- **Test.** `test_gated_d_runs_must_arm_the_step_d_t_dead` fails without the check.

### HIGH-3 (OPEN): after a crash, SIGKILL or power loss in the B leg, only the next *R1* night restores Automatic
- **What still works.**
  - The marker `$MEASUREMENT_ROOT/.align-r1-high-power` is written before `powermode 2`.
  - The chain restores unconditionally at startup (harness row 6).
  - `run_night`'s TERM → 30 s → KILL is safe in practice: the Python and zsh restores finish within the 30 s wait, before the KILL and before the group census re-signals.
- **The gap.** Nothing else on the host reads the marker (`grep` finds it only in the chain, the driver and their tests). `joulewise/environment.py::_parse_pmset` maps `powermode 2` to `low_power_mode: False` (probe P4), so a host left in High Power passes the generic physics gate for every other campaign. The marker also lives under ALIGN's measurement root, which other plans need not share.
- **ALIGN v4 itself is protected.** `arm_powermode_check` refuses a mismatch at W1/D arm, and the desk sets `instrument_ok` false per member (ruling 7).
- **Not fixed here.** The right fix is host-level and changes shared gate semantics, so it needs a lead decision. Either:
  - generalise POWERMODE-PREFLIGHT-RECORD-01, so that `run_night` admission refuses unless the AC `powermode` equals the plan's declared value (default 0); or
  - have `run_night` admission perform the narrow `sudo -n pmset -c powermode 0` restore when the marker exists.
- **Interim runbook for the rehearsal.** After any R1 night that did not write `r1_result.json` with `status: complete|refused|aborted`, run `pmset -g custom` and confirm `AC Power: powermode 0` before any other night is armed.

### MEDIUM-1 (OPEN): ruling 8's load journal is not checked for completeness
- **The gap.** `os_load_verdict` needs only a non-empty list.
- **Probe P2.** A one-sample `cpu_busy_cores: [3.9]` for every quiet segment, the 1,800 s soak included, is accepted with no redo. The 60 s-sustained rule is then vacuous.
- **Recommendation.** Require `len(cpu_busy_cores) ≥ 0.9 × (ended_ns − started_ns)/1e9 − 5`, and refuse otherwise.

### MEDIUM-2 (OPEN): L1 is not evaluated on the R1 record
- **The gap.** The driver records `max_r1_tail_s` but never prints the L1 T_dead or the member-fit worst case.
- **Probe P3.** With a 700 s tail, R1 exits 0 with slot T_dead 1,451 s, where I_D + 1.13544·T_dead + tail + 10 = 2,459 s, over the 1,800 s cap.
- **Why it matters even though the kit catches it.** The kit refuses such inputs (`require_ready` asserts L1 and the member fit). But the duty bar was then evaluated against a T_dead longer than the one W1 will use, which is optimistic once the tail exceeds 40 s.
- **Recommendation.** Print `l1_t_dead(I_D, max_tail)` and the worst case in r1_slots, and evaluate the 40 % share against min(armed, L1).

### MEDIUM-3 (OPEN): the kit does not bind r1_slots to R1 evidence
`require_ready` reads only `ac_powermode` and `max_r1_tail_s` from r1_slots. WP22's stand-in has no `slots` at all and passes. In particular, the kit:
- does not check the schema or `source` (a `--synthetic` r1_slots, `"R1 synthetic rehearsal"`, would admit);
- does not compare `inputs.R1.I_D` with `r1_slots.slots.I_D`;
- does not look at `duty_bar.pass`, `u5.verdict` or `high_power`.

A transcription error, or a failed duty bar without the ruling 1(e) fallback, is not caught mechanically. **Recommendation:** refuse a synthetic source; require equal I_D; require `duty_bar.pass` or a recorded lead fallback step.

### MEDIUM-4 (OPEN): ruling 4(b) battery outputs have no contract field
The run report lists the drain rate (%/h under D and under the 30B) and the charge-resume SoC as R1 outputs, but neither `KIND_FIELDS` nor r1_slots carries them. They may be recoverable afterwards from harvested hazard data, but nothing guarantees that. **Recommendation:** add `battery_drain_pct_per_h` to `step-30b`, `step-d` and the gated D kinds, and `charge_resume_soc_pct` (number or null) to `harvest`, and record both in r1_slots.

### MEDIUM-5 (OPEN): external-volume state is neither refused nor recorded in R1
- Ruling 20's "no external volume mounted" arm rule blocks W1, not R1, and nothing on this head checks `diskutil`.
- The borrowed SSD is planned to be on the MBP by day from 11-07, and `lane/2026-11-06-ssd-always-attached` drafts a default-off volume rule.
- An R1 soak or A-B-A with the SSD attached would freeze slots under a disk state W1 forbids.
- **Recommendation.** Record `diskutil list external physical` at t0, at the terminal record and in each quiet segment's census. Refuse a non-empty list unless the SSD amendment is adopted.

### LOW
1. The batch-window bound for A-B-A legs assumes 1,800 + 600 s. A leg with no decline (t = ∞) may run longer and reach 11:45-13:15. The runtime should declare its leg cap.
2. `t_decline_s: true` is accepted as 1 s, and `recovery_curve` rows are not shape-checked.
3. "A legs ∞, B finite" is reported as inconclusive. Ruling 16 reads as not-adopt. Both leave the series Automatic.
4. If R1 adopts High Power (`ac_powermode: 2`), no W1 chain yet sets 2 and restores it on exit. This fails closed (arm refuses on a mismatch). It is a W1 item.
5. In my first, accidentally unthrottled suite pass (about 100 modules at once), `test_endpoints` had 2 failures and `test_cache_checkpoint_probe` 1 error. Both pass at 3-way concurrency, so they are timing-sensitive under heavy load, not code defects.

## Checked and found sound
- The two-command sudo rule is verified with `sudo -n -l` in both the chain and the driver, before any runtime work. A failed proof of restore refuses with zero runtime calls.
- The marker is written before `pmset powermode 2`.
- The A-B-A sequence:
  - each leg's mode is read back from the exact AC `powermode` key;
  - every leg starts after a `g0-release-soak`, and a release that times out makes adoption inconclusive;
  - the ruling 16 thresholds hold (1.25×, 25 % A spread).
- The quiet/heavy redo logic (rulings 8 and 16):
  - a heavy redo always follows a release;
  - the soak redo is on slope and needs no release;
  - two redos, then R1 refuses;
  - the accepted attempt owns the canonical directory.
- U5 uses c = 1.0 and σ_pair = max(|ΔE|, 2.97 J), per L2.
- `workload.py` arms one `EpisodeDeadman` at G0 entry and passes it to G0, G1, the H holds (via the endpoint) and the tool calls.
- The contrast deadman is 1,086.30 s.
- The v3 kit bytes are unchanged, and `--check` fails closed.

## Commits on the lane from this review
- `14f1dd875` fix(align v4 R1): a signal burst can no longer interrupt the Automatic restore
- `b6a48037f` fix(align v4 R1): every gated D run must arm the step-d T_dead
- this review document
