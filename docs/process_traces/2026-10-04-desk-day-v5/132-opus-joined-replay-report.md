JOINED REPLAY: FINDINGS

# Block-4 joined producer-to-harvest replay on a frozen throwaway clone (addendum C item 6)

- Seat: headless Claude Opus 5.5, 2026-10-05, 12:04–13:20 PDT.
- HEAD: `6796b8e033b8515e12b8c1e6a8da3b94014f7266` (PR #483 integration head).
- Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python`.
- Clones (all under `/tmp/dd5-joined/`, local only, never pushed): `repo` (primary Step 1), `landed` (Step 1 rerun with the new test in the frozen head), `base` (unfrozen HEAD), `frozen-suite`, `tests-clone`, `landed-tests`, `sacrificial`, `landed-sacrificial`.
- Custody mirror: `custody/` next to this report (`primary/` = clone `repo`, `landed/` = clone `landed`, `probe/` = the scripts used).

## Words used below

- **Seam**: a place where the code touches the physical machine (a privileged command, a sensor read, the network clock, a real clock). The brief authorises replacing exactly eight: sudo/systemsetup, the powermetrics sampler, model inference, ioreg battery reads, the HID idle read, the sntp collector, wall/monotonic clocks, and launchctl. Everything else must run for real.
- **FLAG**: a stop. The real code reached something that is neither real-runnable at a desk nor one of the eight seams, so the step stops there and the report names the file and line. It is never stubbed.
- **T-0 stage**: the six native capture steps that run before an ARM: `clock-reference`, `clock-disable`, `quiet-mac-prep`, `prewindow-check`, `ledger-readiness`, `ledger-reservation` (`scripts/capture_t0_step.py`).
- **ARM-only path**: `check_v5_arm_abort.py arm --context <plan>` → `scripts/run_night.py:arm_only`. It runs the T-0 stage, the A196 evidence author and the real ARM issuer, but never launches.
- **Changed set**: the files changed between the freeze head and the reviewed HEAD. If any of them is in the r1 dependency set, the frozen evidence no longer applies and every writer and ARM refuses (`joulewise/arm_readiness.py:5168`).

## Bottom line

1. **Step 1 PASSES at this head.** In both clones the generator `--check`s pass (clone-proof2's G1 is cured here), the U11 projection passes, the pre-author suite passes (203 OK, 1 skipped), 11 evidence kinds are authored per pack, and the sacrificial and primary `freeze-0004` PASS for all three packs.
2. **The joined chain cannot complete at a desk without breaking the rules, so no gate and no verdict was reached.** The real chain runs these steps:
   - the a1 writer (STAGED on frozen GAMMA);
   - the dry-run rehearsal (PASS);
   - the ARM-only path into the native T-0 stage;
   - `clock-reference` and `clock-disable`, captured through the sntp and systemsetup seams.

   It then stops at **F1**: `quiet-mac-prep` runs `scripts/quiet_mac_prep.sh`, whose osascript, pmset, defaults and ps/pgrep commands are not among the eight seams. Every later leg depends on a1's ARM PASS/GO: the a1 expiry, a2, G10, s1, the closeout and both harvests.
3. **Two further stops sit behind F1**, independent of each other:
   - F2 to F4 are more unlisted physical probes, in the T-0 dwell, the A196 author and the s1 night gate. The s1 chain also launches as a real process group.
   - F5 is an authority stop. Even with every seam admitted, the ARM's family-publication gate needs a PUBLISHED d117-v5 marker confirmed with Ed's out-of-band digest hC (clone-proof2 G2), and a desk cannot hold that.
4. **One real defect outside the replay (D1).** `tests/test_v5_pack_regen.py` fails on all three packs as soon as they are frozen. CI will be red at the freeze commit unless that test changes with it.
5. **One landing-order requirement (P1).** The replay test must already be in the head that gets frozen. Committed after the freeze, it puts itself in the changed set, and every writer and ARM refuses.
6. **The new test file** (`test_v5_block4_replay.py`, sha256 `4759da19…ab25ad`) implements all six joined chains. They run the real prefix and assert that exact stop, then skip with the FLAG text. The file passes in all three states: unfrozen HEAD (6 skipped at the freeze FLAG), the landed frozen clone (7 skipped at F1), and frozen-then-committed (8 skipped at the changed-set FLAG).

## Step table

Notation:
- **1.7B** = `d117_floor_qwen3-1p7b_v5`, **8B** = `d117_floor_qwen3-8b_v5`, **GAMMA** = `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`.
- `<p>` = `configs/campaigns/<pack>`.
- The machine-readable logs are `custody/primary/steps.tsv` and `custody/landed/steps.tsv`.

### Step 1, primary clone `repo` (follows clone-proof2 "Exact commands", steps 1–4)

| Step | Command | rc | Outcome | Expected? |
|---|---|---|---|---|
| 0 | `git clone --no-local …/JouleWise repo`; `checkout --detach 6796b8e0`; `update-ref refs/remotes/origin/main 6796b8e0` | 0 | HEAD = origin/main = `6796b8e0` locally | yes |
| 1 | `derive_estate_anchors.py <clone> --output custody/estate-anchor-map.json` | 0 | map written | yes |
| 1b | 3 source generators `--check` (floors `--prefill-prompt-pin`; contrast with panel/models/workload/length/pin) and 3 emitted `<p>/generate_configs.py --check` | 0 ×7 | all clean: **clone-proof2 G1 is cured at this head** | yes |
| 2 | `project_identity_pins.py freeze <clone>/<p>`, one commit per pack | 0 ×3 | PASS, mutated, `[]`. projection-0001: 1.7B `331fc1e9…`, 8B `fbb61c40…`, GAMMA `7b04ef79…`. Commits `430eec3b`, `05709e2c`, `95e0e524` (= EVIDENCE_DERIVATION_HEAD). origin/main moved there locally | yes |
| 3 | pre-author suite in `tests-clone` at `95e0e524`: 4 modules whole, `test_receipt_histsem` per class, RefreshLane per method in 5 groups (15 jobs) | 0 ×15 | **203 OK, 1 skipped** (= clone-proof2) | yes |
| 3c | `author_arm_readiness_evidence.py --pack-root <clone>/<p> --measurement-checkout <clone>` | 0 ×3 | PASS, 11 kinds each (ACCEPTANCE_OWNER … THREE_WINDOW_REGRESSION) | yes |
| 3d | evidence commit; origin/main moved there | 0 | EVIDENCE_COMMIT `52b9f3b2fff926b3a7c04bec5aa4476601eca7ed` | yes |
| 4s | `sacrificial` clone at `52b9f3b2`: `generate_arm_readiness.py freeze --pack-root … --predecessor-pack-root <v3 pred>` | 0 ×3 | PASS ×3 (the slot is spent; the clone is left dirty as the witness) | yes |
| 4p | the same freeze in the primary clone, then commit; origin/main moved there | 0 ×3, 0 | PASS, mutated, `[]`. freeze-0004: 1.7B `a846e35f…`, 8B `0d8d20e8…`, GAMMA `386a99fb…`. FREEZE_COMMIT `c0a65624d22dbc4e149abf160697310396363593`. GAMMA `plan_tree` now pins `arm_readiness.freeze.receipts/freeze-0004.json` | yes |
| 4r | DESK DIAGNOSTIC empty commit carrying `JouleWise-Terminal-Review{,-Tree-Oid,-Pack-Sha256}` trailers; local main and origin/main moved to it | 0 | `bd756b91d9453f849f6479a3423fe883a288fa4d`. `reviewed_main`: clean, exact_match. **Not Ed's or the lead's review: a desk input that exists only in this clone** | yes (desk input) |
| 5–6 | successor pinset, family marker, arm (clone-proof2 steps 5–6) | — | **not run.** The joined chain needs them (F5), but it stops earlier at F1, and step 6 needs Ed's hC, which a desk cannot have | see F5 |

### Step 1 rerun in landed order, clone `landed` (the test file is committed BEFORE the freeze, as it will be on the integration branch)

| Step | Command | rc | Outcome | Expected? |
|---|---|---|---|---|
| L0 | clone at `6796b8e0`; commit the new `tests/test_v5_block4_replay.py` | 0 | LANDED_HEAD `8a90fb26b7bf09012c5dc0cde73790424b98a490` | yes |
| L1–L4 | the same commands as steps 1–4 above (`custody/probe/landed.zsh`) | 0 throughout | generator checks ×7 OK; projection ×3 PASS (EVIDENCE_DERIVATION_HEAD `fc61e3be`); pre-author suite **203 OK, 1 skipped**; authoring ×3 PASS; EVIDENCE_COMMIT `3d8a7958`; sacrificial ×3 PASS; freeze ×3 PASS (freeze-0004: 1.7B `65d077af…`, 8B `f13b268b…`, GAMMA `a6b9e339…`); FREEZE_COMMIT `59ba1542`; desk-review commit `77c3b5c0bc71553bd4a842899c09f4982070482e` | yes |
| L-arm | the real `ar.generate_arm_receipt` on frozen GAMMA (`custody/probe/arm_inventory_landed.py`) | — | governed **REFUSE / NO_GO**. 14 PASS (every FREEZE_AND_ARM row), 16 REFUSE (all ARM_ONLY: 2 clock rows, 12 `t0.*`, `desk.terminal_review`, `desk.under_lease_rehearsal`), 5 N/A. The same 12 codes as clone-proof2's armpre, including `readiness_r1_family_publication` | yes |

### Step 2, the joined replay

| Step | Command | rc | Outcome | Expected? |
|---|---|---|---|---|
| J1 | `writer.write_qualification("a1", inputs, <custody>/plan.json)` with a distinct fresh arm-context root, `window/window.env` (25 keys) and `window/window-chain.zsh` rendered with the arm context | — | **STAGED**: `ARM_ONLY_NO_LAUNCH`, freeze locator = GAMMA freeze-0004, kernel-frequency margin 1.216 ms | yes |
| J2 | `ar.generate_dry_run_receipt(GAMMA, <a1 custody>, "a1", <synthetic>)` (row `desk.under_lease_rehearsal`) | — | **PASS**, `[]` (the real reservation CLI and ledger lifecycle, on a synthetic ledger) | yes |
| J3 | `check_v5_arm_abort.main(record.recipe.arm_argv[2:])` = `arm --context <plan>` → `run_night.arm_only` | 2 | `{"status":"REFUSED","reason_code":"arm_abort_control_invalid"}`. The native T-0 stage ran in-process (see "Process boundary" below). `clock-reference` and `clock-disable` were captured through the seams (3 × sntp collector, 1 × sudo/systemsetup OFF), together with `network_time_off.json` and `launch-manifest.json`. Then `quiet-mac-prep` → **F1**; `t0-capture.stdout.json` = REFUSE with detail = the F1 text. No `arm-*.json`, no `arm-only.json`. The absence census is all True: no consumption, no `launch.pending`, no `chain.started`, empty runs roots | **NO → F1** |
| J4… | a1 `observe`/`finish` (expiry), a2, G10 `run` with preflight, the s1 writer (`previous_attempt: none`), the s1 driver under the observation producer, `v5_s1_desk_closeout.py`, the qualification assembly with `harvest_v5_qualification.py`, `harvest_v5_g2b_window.py`, `restore_v5_null_reservation.py` | — | **not reached**: every one needs a1's ARM PASS/GO | — |

### Test runs of the delivered file

| Run | State | Command | rc | Outcome |
|---|---|---|---|---|
| T4 | `base` (HEAD, unfrozen) | `python -m unittest tests.test_v5_block4_replay` | 0 | 14 run, OK, 6 skipped: the joined cases, at the freeze FLAG `joulewise/arm_readiness.py:7621` |
| 06 | `landed` (frozen, landed order); final file run from outside with `PYTHONPATH=<landed>`, so the checkout stays clean | `python -m unittest -v test_v5_block4_replay` | 0 | 14 run, OK, 7 skipped (6 joined at **F1**, plus the superseded unfrozen-writer case). `test_real_arm_issuer_also_stops_before_authorizing` passes on its frozen branch |
| 05 | `landed`, in place (the committed copy; differs from the final file only in the changed-set handling, a path `resolve()` and one unused import) | `python -m unittest -v tests.test_v5_block4_replay` | 0 | 14 run, OK, 7 skipped, the same as run 06 |
| T3b | `repo` (test committed after the freeze, `2e4d1d30`); final file from outside (run before the last edit, which removed one unused `import os`) | `…CommittedGammaJoinedReplayTests` | 0 | 10 run, OK, 8 skipped at the changed-set FLAG `joulewise/arm_readiness.py:5168` (**P1**) |
| FS | `frozen-suite` (= `repo` at `bd756b91`): the other 17 `tests/test_v5_*.py` and `tests/test_harvest_v5_*.py` modules | per module | 0 ×16, 1 ×1 | 16 modules OK. `test_v5_pack_regen` FAILED (3 failures) → **D1** |

## Per variant: gates and verdicts reached

Each joined case runs its own complete chain (about 40–60 s each) and reaches the same last step.

| Test | Variant | Real steps reached | Gates (G1, G3, G5, G8, G9) | Verdicts |
|---|---|---|---|---|
| `test_joined_success_qualification_and_structural_pass` | success | J1 STAGED, J2 PASS, J3: T-0 steps 1–2 captured, stop at F1 | none reached | none |
| `test_joined_observation_exception_preserves_chain_rc_and_structural_verdict` | an observation producer raises | the same | none | none (the injection point is after `chain.started`; not reached) |
| `test_joined_launch_crash_recovers_no_science` | launch tooling crash → `recover_no_science` | the same | none | none |
| `test_joined_agent_capture_is_live_gate_fail_end_state` | an agent in the capture census | the same | none | none |
| `test_joined_null_s1_restore_then_fresh_s1_history_and_census` (new) | NULL s1 → NULL restore → fresh s1 | the same | none | none |
| `test_joined_admission_abort_then_fresh_s1_allowance_spent` (new) | admission abort → fresh s1 → allowance spent; a second abort refuses as the same refusal twice | the same | none | none |

Seams used at runtime: the sntp collector (3 legs) and sudo/systemsetup (OFF). The other six authorised seams were never reached. Real clocks were used and nothing was mocked for them.

**Process boundary (not a seam).** `run_night._capture_qualification_t0` runs `<repo>/.venv/bin/python scripts/capture_t0_step.py sequence …` through `t0_rehearsal.observed_run`. The test replaces only that process launch. It runs the same `capture_t0_step.main` with the identical argv in-process, and it runs `collect_clock_reference.main` the same way. Those two modules' physical commands then pass through `PhysicalSeams.execute`. Any command that is not an authorised seam raises before it executes.

## Findings

### F1 (FLAG, unlisted physical seam): the native T-0 step `quiet-mac-prep`. This blocks a1, and therefore the whole chain.

- **Where.**
  - `scripts/capture_t0_step.py:491` runs `/bin/bash scripts/quiet_mac_prep.sh`, as the third of six steps, under `run_night.arm_only` → `_capture_qualification_t0` (`scripts/run_night.py:3725-3780`).
  - The script's physical commands that are not among the eight seams:
    - `pmset -g batt` (`:13-14`);
    - `osascript`, which lists and **quits every foreground app** (`:17-27`);
    - `ps -Aro` (`:34`);
    - the `pgrep` census (`:38-44`);
    - `defaults -currentHost read com.apple.screensaver` (`:66-67`);
    - `pmset displaysleepnow` and `pmset -g systemstate` (`:92-94`).
  - Its `sudo -n powermetrics` (`:47`) and HID-idle `ioreg` (`:74`) are listed seams. The script as a whole is not.
- **Reproducer.** In a frozen clone with the test in the frozen head (as `/tmp/dd5-joined/landed`), run:

  ```
  TMPDIR=/tmp/dd5-joined/tmp python -m unittest -v tests.test_v5_block4_replay.CommittedGammaJoinedReplayTests.test_joined_success_qualification_and_structural_pass
  ```

  Expected result: `skipped "FLAG scripts/capture_t0_step.py:491 …"`. The test asserts:
  - the exact seam call sequence;
  - the two captures;
  - `t0-capture.stdout.json` REFUSE with the FLAG detail;
  - no ARM, `arm-only` or launch artefact.
- **Safety note.** My first probe called `run_night.arm_only` without the interception. It reached `subprocess.run([<clone>/.venv/bin/python, scripts/capture_t0_step.py, …])` and failed with `FileNotFoundError`, because the throwaway clone has no `.venv`. Nothing executed, so no sudo or systemsetup ran. Every later run had the interception installed first. In a checkout that does have `.venv`, an un-intercepted desk call to the ARM-only path would run the real `sudo -n systemsetup` (by design: it is the production path).

### F2 (FLAG, unlisted physical seam): the native T-0 step `prewindow-check`, next after F1

- **Where.**
  - `scripts/capture_t0_step.py:492-493` runs `joulewise/prewindow.py --t0-wait --timeout-min 45 --window <profile>`.
  - Its probes: `ps` CPU census (`joulewise/prewindow.py:57`), `uptime` (`:66`), `pmset -g batt` (`:73`), `ps -A -o comm=` (`:100`).
  - The ≥ 600 s continuous dwell (`scripts/capture_t0_step.py:865-871`) is a clock seam and is admissible.
- **Not reached at runtime** (F1 is earlier). The test's dispatcher already maps this argv to the F2 FLAG.

### F3 (FLAG, unlisted physical seam): the A196 author's fresh probes, which run inside the ARM-only path after the T-0 stage

- **Where** (`author_arm_readiness_evidence_t0`, called from `scripts/run_night.py:_author_pack_arm`), unlisted:
  - `pgrep` maintenance census (`joulewise/arm_readiness_evidence_t0.py:1391-1396`);
  - `ps` CPU samples (`:1407`);
  - `pmset -g therm` (`:1453`);
  - `pgrep` keep-awake, agent, browser and monitor censuses (`:1821-1824`);
  - `pmset -g batt` and `pmset -g custom` (`:1934-1935`);
  - `system_profiler SPPowerDataType -json` (`:1936-1940`).
- Listed and admissible: sntp R1 (`:1158`), `sudo -n powermetrics -i 200 -n 1` (`:1899-1903`), ioreg battery (`:1958`).
- **Code reading, not executed.**

### F4 (FLAG, unlisted physical seams plus a process boundary): the s1 driver

- **Where.**
  - The night gate's probes (`joulewise/night_gate.py:178-192`): `pmset -g`, `pmset -g batt` and `pmset -g therm`, `sysctl -n vm.loadavg`, the `pgrep -lf` agent census, and `defaults read … idleTime` (named HID idle).
  - The chain is launched as a real process group through `t0_rehearsal.observed_popen` (`scripts/run_night.py:1000`). Inside it, `run_campaign` performs model inference and runs the powermetrics sampler in child processes. Those two are listed seams, but they have no in-process injection point there. Replacing `run_campaign` or the interpreter would stub non-physical semantics. The s1 driver also repeats F1/F2 in its own native T-0 stage.
- **Code reading, not executed.**
- By code reading, the G10 helper (`scripts/ed_session/capture_t0_anchor_positive_control.py`) needs only listed seams: the sntp collector through `collect_clock_reference`, and systemsetup on/off. It needs a2's T-0 inputs first.

### F5 (FLAG, authority, not a seam): the ARM family-publication gate. Steps 5–6 are needed but cannot be satisfied at a desk.

- **Where.**
  - `joulewise/arm_readiness.py:12875-12904` (`_gate_family_publication`).
  - GAMMA is in the registry's successor roster, so with no marker the ARM refuses at `:12896` (`marker_absent`).
  - With a marker, it requires `verify_family_publication_marker(phase="pre-arm")` to be gate-admissible: a PUBLISHED marker (`:11806`), the step-6 confirmation table, and Ed's out-of-band digest hC.
- **Observed.** The real ARM at the landed frozen head carries `readiness_r1_family_publication` (step L-arm).
- **Why it cannot be cleared at a desk.** A desk proof cannot hold hC. Rendering and self-confirming a step-6 table would fabricate Ed's confirmation (clone-proof2 G2). The schema-only confirmation table the committed test already uses (`tests/test_family_marker.confirmation()`) does not confirm a real marker.
- **Steps 5–6.**
  - What the joined replay needs: 5a (successor pinset), 5d (the family marker, promoted to PUBLISHED), and 6 (arm with the promoted table and hC).
  - Why they were not run: F1 stops the chain first, and step 6 cannot be authorised at a desk.

### D1 (real defect, test code): `tests/test_v5_pack_regen.py` fails once the `_v5` packs are frozen, so CI goes red at the freeze commit

- **Where.**
  - `tests/test_v5_pack_regen.py:24-36` (`test_generators_emit_75_second_idle_from_issued_pin`) always passes `--no-preserve-current-frozen-bytes`.
  - Once a pack is frozen, the generators correctly refuse: "the current frozen identity requires preserve mode". The guard is at:
    - `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:337-342`;
    - `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:342`;
    - `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py:313-318`.
  - The production guard is right; the test is wrong.
- **Reproducer.**
  - `cd /tmp/dd5-joined/frozen-suite && python -m unittest tests.test_v5_pack_regen` → `FAILED (failures=3)`, one per pack, "generation failed: the current frozen identity requires preserve mode".
  - The same command at `6796b8e0` (`/tmp/dd5-joined/base`) → OK.
  - Minimal form: `python -B <p>/generate_configs.py --prefill-prompt-pin configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json --no-preserve-current-frozen-bytes --output-root <tmp>` in any frozen clone.
- **Not fixed** (outside the brief's scope). Suggested route: when the target status is FROZEN, check the 75 s idle from preserve-mode output or from the committed members, and land that with the freeze.

### D2 (test defect, fixed in the delivered file): the committed replay test's preparation cases break once GAMMA is frozen

- What breaks:
  - `test_complete_pack_bytes_roster_and_reviewed_chain_are_real` requires byte equality with `PACK_SOURCE_COMMIT`. The freeze legitimately re-pins `plan_tree.{json,sha256}` and adds 37 receipt files.
  - `inputs()` reuses the plan custody as the arm-context custody. Once the freeze refusal no longer comes first, the real writer refuses at `arm_context.custody_roots_overlap` (`scripts/write_v5_qualification_plan.py:626-628`).
  - The real ARM issuer returns a governed NO_GO receipt instead of raising.
- Reproducer: the original file at the frozen `repo` head gives `FAILED (failures=6, errors=3)` (first run this seat).
- The delivered file handles each case explicitly:
  - a subset check that leaves out exactly the two re-pinned files;
  - a skip for the superseded unfrozen-writer case;
  - frozen-branch assertions on the real NO_GO receipt.

### P1 (procedure): the replay test must be in the frozen head

- Commit `tests/test_v5_block4_replay.py` after the freeze, and the real writer and ARM both refuse: `reviewed HEAD changed relevant path(s): ['tests/test_v5_block4_replay.py']` (`joulewise/arm_readiness.py:5168`; writer path `scripts/write_v5_qualification_plan.py:506`).
- Reproducer: `/tmp/dd5-joined/repo` at `2e4d1d30`.
- The delivered file turns this into a FLAG skip. Land the test on the integration branch **before** the claim-head freeze. The `landed` clone shows that order working end to end.

### Desk inputs that stand in for authority (disclosed; never launch authority)

- The terminal-review trailer commits `bd756b91` and `77c3b5c0`. They exist only in the throwaway clones.
- The schema-only step-6 confirmation table and transcript, from the committed test's own pattern.
- `window.env`, written as `scripts/ed_session/build_rehearsal_env.sh` would author it.
- Fresh empty claim, bound, quarantine and custody roots.

## Final test file

- Path: `/Users/edr/night-archive/desk-day-v5/joined-replay/test_v5_block4_replay.py`.
- sha256: `4759da1984d57e494b3d475a64df0651773a1e407eb90deabe42709841ab25ad`.
- Target: `tests/test_v5_block4_replay.py` on the integration branch.
- Contents:
  - `PHYSICAL_SEAMS` and `PhysicalSeams`: one labelled branch per seam. Any other command raises `UnlistedPhysicalSeam` before it executes, carrying a FLAG computed from the live source line.
  - `JoinedDesk`: the desk inputs for one occurrence.
  - `CommittedGammaJoinedReplayTests.joined_chain(variant)`.
  - The four original joined tests plus the two new variants.
- Behaviour in each state:
  - **Unfrozen**: skips at the freeze FLAG, as before.
  - **Frozen, test in the frozen head**: runs J1–J3 and asserts the F1 stop exactly.
  - **Frozen before the test landed**: skips at the P1 FLAG.
  - **If the ARM-only path ever returns PASS**: the test fails with "implement the a1 expiry, a2, G10 and s1 legs; do not keep this stop", so the stop cannot silently become stale.
- Runtime: about 7 min for the module in a frozen clone (6 chains at roughly 40–60 s each, plus the started-occurrence controls). About 45 s unfrozen.

## Exact next step

1. **Lead decision on F1–F4.** Either admit the extra physical seams as listed above (osascript, pmset, defaults, ps/pgrep/uptime census, sysctl loadavg, system_profiler), or give the T-0 stage and the driver a supported injection point for them.
2. **Lead decision on F5.** Decide what desk-only authority a replay may hold for the family-publication gate: for example, a reviewed desk-replay rule for a self-rendered step-6 table, kept separate from Ed's hC. Without such a rule, no desk replay can get an ARM PASS/GO for a registry-installed `_v5` pack.
3. **Land D1's test fix together with the freeze**, and land this test file before the freeze (P1).
4. **Then rerun.** Use the `landed` recipe (`custody/probe/landed.zsh`) and extend `joined_chain` past J3: a1 `observe`/`finish` → a2 → G10 → s1 → closeout → both harvests. Then implement each variant's injection at its real seam.

## Safety

- No sudo, launchctl, powermetrics or systemsetup ran.
- No window was armed or launched, and no launch capability was consumed: every ARM result in this seat is a REFUSE/NO_GO receipt or an early refusal.
- Nothing was pushed, and there was no fetch in `/Users/edr/code/JouleWise`.
- Writes stayed in `/tmp/dd5-joined/` and this directory.
- No measured energy or power value is printed or recorded.
- No detached job remains running.
