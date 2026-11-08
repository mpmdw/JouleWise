# R1 arm route: agreement report (Opus build vs Sol build)

RUN_STATE item 220 asks for two independent builds of the R1 arm route, compared here before the lead rules.

| | Sol (seat R1-ARM-1, Sol 6.1 xhigh) | Opus (this lane, Opus 5.5) |
|---|---|---|
| branch @ sha | `lane/2026-11-08-r1-arm` @ `0b54827da` | `lane/2026-11-08-r1-arm-opus` @ `d5882a34e` (+ this report) |
| base | `d9d1098c6` | `d9d1098c6` |
| independence | Opus committed and pushed `d5882a34e` before fetching Sol's branch | same |
| R1 measurement code | unchanged | unchanged |

**The lead rules. Neither route is merged.** Opus has the final say under the window design council.

## 1. Route choice

- **Sol: (a), a HAZARD_PACK window around the unchanged R1 chain.**
  - `joulewise/align/r1_arm.py` writes a v5 hazard plan with `ac_powermode 0`.
  - It writes an *R1-only* "pack" in custody: `plan_tree.json` holds only a config inventory of the R1
    runtime config, `inputs.json` and the four templates, so lineage publication works.
  - The wrapper chain runs:
    1. a D-109 diagnostic fiducial bookend (pre);
    2. the R1 chain;
    3. a bookend (post);
    4. the R1 chain's exit code is returned.
  - The unchanged b5 driver supplies the census, the six-module hazard arm, lineage, inventory, the hazard
    monitor, the KM003C meter supervisor, keep-awake, the chain deadline, the terminal records and the
    program courier.
  - **No shared arming file changes.**
- **Opus: (b), a ruled, chain-bound `DIAGNOSTIC_NO_PACK` night.**
  - A registration (`configs/align/v4/r1_night_registration.json`) pins the R1 chain SHA-256 and the sizing
    constants, and is added to `RULED_REGISTRATIONS`.
  - A payload kind `align_v4_r1` makes C5 authenticate the R1 source against `measurement_head`.
  - The generated wrapper adds the KM003C meter, display sleep with a 300 s dwell, and a source re-check,
    then runs the R1 chain.
  - The installer and the `_probe-worker` never execute this chain.
  - **Four additive edits to arming code** (`night_kinds`, `night_gate`, `night_agent_install`,
    `run_night._probe_worker`), plus a dated amendment of the registration-table tripwire test.

## 2. Gates each route passes or bypasses

| guarantee | Sol (HAZARD_PACK) | Opus (DIAGNOSTIC_NO_PACK) |
|---|---|---|
| agent census at t0 and in-chain | yes (hazard census plus in-chain census) | yes (initial, C3, in-chain every 30 s) |
| quiet guard before start | hazard arm: contention dwell, thermal, battery, clock, disk, instrument; "physics refuses, the rest is a flag" | network time OFF + 600 s settle; `prewindow_check --wait` (600 s clean, ≤ 5 %/process, load ≤ 2, 45 min cap); C3 (HID setting, AC, battery float, display setting, load ≤ 2, thermal) |
| contention during R1 | R1 ruling 8 journal (redo or refuse) **plus the hazard monitor's continuous journal** | R1 ruling 8 journal only |
| display asleep (R0-L3) | **not explicit**: the fiducial bookend sleeps the display before its own capture; no dwell before R1; the runbook does not ask for display sleep | wrapper `pmset displaysleepnow` + 300 s dwell before R1, recorded; runbook step 7 |
| external volume | R1 driver ruling 20 census (unchanged); hazard disk module watches custody | R1 driver ruling 20 census (unchanged) |
| KM003C | **the b5 driver's meter supervisor** (`km003c_monitor.py`, restarts, flags). This is literally the shared launcher. | the same program and stream layout, run by the wrapper inside the chain's process group (restart after a crash; stop file at the end) |
| disk | **arm disk module (20 GiB headroom) plus a 10 GiB live floor that stops the night**; `planned_bytes` 0 is flagged as unsized | **none**: the runbook asks for a manual `df` check of ≥ 80 GB |
| keep-awake | **caffeinate assertion (`sleep_guard`)** | none: the runbook asks for AC `sleep 0` |
| instrument | hazard instrument module (powermetrics cadence) at arm | none at arm (the installer probe is skipped); a broken powermetrics fails R1's first model segment |
| chain identity | sidecar mismatch is **only a flag**; R1 source recorded in the executed inventory, not checked at t0 | C5: wrapper vs sidecar, R1 source vs the committed blob and the pinned digest; C1: the registration binds that digest; the wrapper re-checks at launch (exit 65) |
| measurement checkout at t0 | heads checked by the installer at install; not re-checked at t0 | C5: HEAD = `measurement_head`, clean porcelain, root under `night-custody/measurement` |
| registration authority | none needed (HAZARD_PACK) | **a new `RULED_REGISTRATIONS` entry, which needs the lead's ruling** |
| AC powermode | plan 0 admission; R1 holds its own host lock | identical |
| deadline | `_WindowDeadline` (t0 + W + 300 s), proven group stop | identical |
| meter or monitor on interrupt | the existing hazard interrupt path can leave the monitor and meter alive until the dead-man (Sol F3) | the meter is in the chain group and dies with it |
| desk control before t0 | `run_night --dry-arm` works (census + hazard arm) | `write_align_r1_night.py check` (static C1/C5 with real probes) |
| calibration scaffold | **two diagnostic D-109 fiducial bookends** (r1_runtime_contract: "the meter calibration itself belongs to the R1 night plan's scaffold") | none (only R1's own calibration-pre/post host snapshots) |
| courier | `b6_courier.sh` (file-only, no agent) | runbook now passes `--courier-bin b6_courier.sh` (amended after comparison) |
| network time | OFF at arm, not restored | OFF at admission, not restored; runbook step 8 restores it |
| hazard clock threshold | changed to the ALIGN pilot / b6 S-7 hold, with `T_stream_max_s` = 5,764 s (longest segment); otherwise every R1 would refuse | n/a (C4 boot/epoch only) |

## 3. Sizing

Both routes follow items 215/216. R1 can redo, so the **96,427 s floor** applies in both. Sol's F3
("unsized") is about **disk** `planned_bytes`, not `window_max_s`.

| term | Sol | Opus |
|---|---|---|
| R1 redo floor (one 11,164 s batch encounter) | 96,427 | 96,427 |
| arm / admission | 3,300 (`T0_STAGE_CAP_S`) | 3,000 (OFF settle + ≤ 2,700 s clean dwell) |
| bookends | 2 × 1,800 | — |
| bookend / segment close | 2 × 600 | 120 (close) |
| harvest | 600 | 1,800 |
| display dwell + meter | — | 330 |
| R1 calibration-pre/post | — | 600 |
| **window_max_s** | **105,127** (fixed) | **102,300**, or 113,460 when t0 is about 07:20-11:45 PT |
| extra 11:45 crossings | **not counted** | +11,164 s per extra local 11:45 in the window |

**Finding (Sol, HIGH for sizing).** A 105,127 s window (29.2 h) reaches two local 11:45s whenever t0 falls
between about 06:33 and 11:45 PT. Item 216 says "11,164 s per segment that can touch 11:45-13:15". Sol's
runbook derives t0 as "now + about 8 min", so an arm in that band would be under-sized by up to 11,164 s.
Opus's generator adds the term and iterates it to a fixed point.

## 4. Test coverage, re-executed on the laptop (python3.13, one module per process)

| module | at `d9d1098c6` | Opus branch | Sol branch |
|---|---|---|---|
| `tests.align.test_r1_arm_route` (Opus) | n/a | **14/14 OK** (59 s) | n/a |
| `tests.align.test_r1_arm` (Sol) | n/a | n/a | **4/4 OK** (22 s; `JW_B5_SYNTHETIC_ONLY=1`) |
| `tests.align.test_v4_kit` | 6 fail (expected, item 218) | 116 OK | 116 OK (Sol's report) |
| `tests.align.test_r1_runtime` | 2 fail (expected) | 33 OK | 33 OK (Sol's report) |
| `tests.align.test_r1_rehearsal` | — | OK | OK (Sol's report) |
| `tests.align.test_r1_runtime_contract` | — | OK | unchanged |
| `tests.test_night_gate` | — | 112 OK (tripwire repinned with a dated note) | unchanged |
| `tests.test_night_kinds` | — | OK | unchanged |
| `tests.test_digest_pin_census` | — | OK | unchanged |
| `tests.test_night_agent_install`, `tests.test_evidence_night` | — | see §6 | unchanged |
| `tests.test_run_night` (318) | **2 F + 1 E** | **1 F + 1 E** (a subset of base) | Sol's sandbox: 3 F + 2 E |

**F1 (`tests.test_run_night`).**
- `Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` errors at the base
  `d9d1098c6` too. It is pre-existing, from the R8-1/D8-1 re-raise, and neither route causes it.
- `BindSupervisionProcessTests.test_startup_hang_is_nonblocking` and
  `test_blocked_journal_never_blocks_deadline_or_grants_go` are wall-clock fixtures. They failed at base and
  were flaky on Opus while two 318-test modules ran in parallel.
- Sol's two other failures, `HazardPackPrimitiveTests` natural-exit census and supervision stop, plus the
  dead-man monitor, pass at base on the Air. They come from Sol's sandbox denying `ps` (Sol F2), not from
  the route. Sol's shared files are byte-identical to the base.
- The `origin/main` run is in §6.

**What each e2e makes real.**

| layer | Sol e2e | Opus e2e |
|---|---|---|
| run_night | real (HAZARD branch) | real (DIAGNOSTIC branch) |
| gate | hazard arm faked (`FakeArm`) | night_gate C1-C5 real, on `ProbeSource` probes; the derivation admission (OFF + dwell + start conditions) uses the existing stub |
| lineage publication | real | n/a |
| wrapper and R1 chain | real | real |
| R1 driver | real | real; FakeWorld only at sudo/pmset/mount, through `r1_arm_bootstrap.py` |
| runtime | an executable fake runtime | **the real WP15 runtime on the synthetic backend** |
| KM003C | meter argv exits 0 at once | synthetic streaming meter, stopped by its stop file |
| interrupt case | yes (TERM during the B leg: lock blocked, then Automatic and the lock restored) | no (the deadline and interrupt machinery is unchanged run_night code) |
| negative gate cases | — | changed registration → C1; changed R1 source → C5; chain never claimed |
| watchdog / dead-man second day | yes (real plists → watchdog reader; early dead-man stands down) | code-checked only (runbook §2) |

## 5. Every behavioural difference, with a recommendation

| # | difference | recommendation | reason |
|---|---|---|---|
| D1 | plan class: HAZARD_PACK (Sol) vs ruled DIAGNOSTIC_NO_PACK (Opus) | **Sol's HAZARD_PACK** | No arming code changes and no new `RULED_REGISTRATIONS` authority. It carries the physical modules R1 lacks in Opus's route (disk floor, keep-awake, continuous monitor, instrument), the driver-supervised meter and `--dry-arm`. Opus's route is stronger on custody (D5, D6) but weaker on physics, which matters more for a 28-29 h unattended night. |
| D2 | sizing: no crossing term (Sol) vs crossing term (Opus) | **adopt Opus's term in Sol's route**, or constrain t0 to outside 06:33-11:45 PT | item 216 |
| D3 | display: implicit (Sol) vs `displaysleepnow` + 300 s dwell (Opus) | **add to Sol's wrapper** (before the pre bookend) and to its runbook: the magistrate sleeps the display before exit | R0-L3 / items 206 and 209: display-on bursts refuse quiet gates; the R0 re-run 11 pass depended on it |
| D4 | bookends: two D-109 diagnostic fiducial captures (Sol) vs none (Opus) | **keep Sol's**, recorded as diagnostic (exit ≠ 0 → `r1.bookend_failed`, never a veto) | the contract names the calibration scaffold as the plan's; it costs about 1 h of window, already sized |
| D5 | R1 chain identity at launch: flag only (Sol) vs fail-closed (Opus) | **add Opus's wrapper source re-check to Sol's wrapper**: pin the R1 chain SHA-256 as a literal and exit 65 on mismatch before any work | "R1 measurement code must NOT change". The HAZARD doctrine makes a sidecar mismatch only a flag; R1 is a one-off night where running drifted R1 code would waste 29 h |
| D6 | measurement HEAD at t0: install-time only (Sol) vs t0 (Opus) | accept Sol's; runbook: no `git` operation in `$M` between install and t0 | the installer checks both heads, and the magistrate exits right after install |
| D7 | meter on interrupt: may outlive the chain until the dead-man (Sol) vs dies with the chain (Opus) | accept Sol's (existing shared behaviour, disclosed); the next activation checks for a stray `km003c_monitor.py`/`hazard_monitor.py` | not R1-specific; fixing it touches the b5 driver |
| D8 | disk: arm module + live floor, `planned_bytes` 0 (Sol) vs none (Opus) | **Sol's**; magistrate also records `df` at arm | the 20 GiB headroom and 10 GiB live floor remain the protection; R1's footprint is unmeasured |
| D9 | hazard clock threshold set to the ALIGN pilot S-7 hold, T_stream 5,764 s (Sol) | **accept**: an existing registered rule, not a new tolerance; the B5 3.7 ms hold would refuse every R1 | Sol's test pins zero drift passing and 1 ppm failing |
| D10 | R1-only "pack" (inventory-only `plan_tree.json`) in custody (Sol) | **accept**, labelled non-claim | lineage needs an inventory; R1 has no W1 members; the yield plan errors into a note (`driver.py:2520`), never a stop |
| D11 | admission quiet guard: hazard contention dwell (Sol) vs 600 s `prewindow_check` + C3 load/battery float (Opus) | Sol's (part of D1) | both are existing, ruled admissions; the hazard arm is what W1 will use, so R1 also rehearses W1's arm |
| D12 | courier: `b6_courier.sh` (Sol) vs default `claude` (Opus, before amendment) | **Sol's**; Opus's runbook amended | no agent on the MBP after the chain |
| D13 | network time left OFF after the night (both) | **add to Sol's runbook**: `sudo -n systemsetup -setusingnetworktime on` at the next activation | 29 h with no NTP is harmless for R1; W1's arm sets it again anyway |
| D14 | snapshot test repin: both repin the same 8 tests to the post-R0 state and keep each refusal on an emptied copy | either; take Sol's (it lands with the route) | equivalent |
| D15 | item 202 (4): both read the same code: load > 0.5 core for 60 s → redo (≤ 2), then R1 refuses; only 11:45-13:15 is avoided | **agree** | Sol adds trustkit xx:31 and XProtect about 05:40 to the job list; Opus recommends t0 13:20-14:00 PT |

**Recommendation to the lead.** Arm R1 on **Sol's route (`0b54827da`)** after three small changes, all in
`joulewise/align/r1_arm.py` or its runbook, none in arming code:
1. **D2**: the per-crossing sizing term, or a t0 constraint.
2. **D3**: `pmset displaysleepnow` + 300 s dwell in the wrapper before the pre bookend, plus a runbook line.
3. **D5**: a fail-closed R1 chain-digest check in the wrapper.

Also add D13 and D6 to its runbook. Opus's branch then stays unmerged. Its `write_align_r1_night.py size`
can serve as the sizing calculator until the D2 port lands.

Since these changes touch the route that arms, they need a quick independent re-execution of
`tests.align.test_r1_arm`: the Opus executing review under item 219.

## 6. Open checks at the time of writing

- `tests.test_run_night` on `origin/main`: see the lead's run log. The Opus run was still going when this
  report was committed.
- `tests.test_night_agent_install` and `tests.test_evidence_night` on the Opus branch: still running at
  commit time; results follow in the hand-back.
