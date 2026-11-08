# ALIGN v4 pre-W1 smoke kit (Opus build)

Authority: RUN_STATE 219 and 220 on `origin/main`. Ed's goal: "good quick smokes that test all the
likely flag/dangerous points before we commit to long blocks". A fault that a 30-45 minute check
can catch must never cost a 12 h W1/D window. Two such faults were found late on 2026-11-08:
- R1 had no arm route (item 218);
- the WP22 synthetic W1 dry run, which the protocol requires, had been red for two commits behind an
  opt-in environment flag (Opus cold review, HIGH-1).

This is the Opus half of a Sol/Opus pair (item 220). The Sol seat builds the same kit on
`align/2026-11-08-w1-smoke`. `W1-SMOKE-AGREEMENT.md` compares the two builds.

The kit has two parts:
- **Part A**, an Air-side PREQUAL extension (`scripts/align_v4_w1_prequal.py`). It runs before any
  MBP launch, takes about 40 s on the Air today, and about 4-6 min once WP22 is green.
- **Part B**, a native MBP smoke (`scripts/align_v4_w1_smoke.py`). The magistrate runs it in a gap
  between windows; it is budgeted at 45 min.

Both parts are synthetic or labelled `smoke`. Neither reads an outcome, a record or a restricted path.

## Part A: PREQUAL extension (Air)

```sh
# at the exact commit the MBP will run (clean checkout), on the Air
nice -n 15 python3.13 -B scripts/align_v4_w1_prequal.py --output /private/tmp/jw-w1pq/<commit>-w1 --next w1
# before R1: the same command with --next r1
```

- **Output:** one PASS/FAIL table on stdout, plus `prequal-w1.json` and `prequal-w1.md`.
- **Exit codes:** 0 PASS, 1 FAIL, 3 INCOMPLETE (`--only`), 2 usage.
- **How checks run:** each check is a probe in its own Python process, and probes run in parallel
  (`--jobs`, default 4). An exception counts as a FAIL. A probe that prints no result counts as a FAIL.
- **Host commands:** every pmset, ioreg, mount, diskutil, launchctl and installer call goes to
  `w1_prequal.FakeHost`. The meter is a stand-in program. Nothing touches hardware.
- **Gating:** each check gates a measurement, either `r1` or `w1`. A check *blocks* this arm when it
  gates the next measurement or an earlier one.
  - A FAIL in a check that gates a later measurement is still printed, as an early warning, but it does
    not change the exit code.
  - PENDING means "cannot be satisfied before that stage". At the check's own gate, PENDING becomes FAIL.
- **Waivers:** `--waive CHECK=RULING` records a lead waiver for a single check. The waiver goes into
  the report.

| Check | Gates | What it runs | PASS means |
|---|---|---|---|
| `arm-cli` | w1 | `align_v4_session.py install --help`, and `install` with no arm evidence. Then the production `main(['install', ...])` with every required flag, against a fake host, in 11 cases. | Every required flag is present and enforced by argparse. The control case admits and calls the installer exactly once. The 10 fault cases each refuse with their documented reason before the installer. The faults are: triage packet missing, edited or pre-R12; top-up missing, stale (31 min) or future-dated; OBC unattested; a disk image mounted; battery charging; powermode mismatch. |
| `triage-staleness` | w1 | `next_arm_triage` on a well-formed packet from an earlier window | A stale packet is refused. |
| `calibration-stop` | w1 | `calibration_stop` over the planned C1-C8 series (7 benign per pair per window). Also the zero-capture, provisional, insufficient and ninth-window cases, and the predicate inside the triage for W1, C1, test-early, C9 and T1 arms. | Every case gives its registered decision. |
| `cal-escalation-exit` | w1 | A lead-ruling row after `escalate_to_lead` | The next arm can proceed (no permanent deadlock). |
| `kit-ready` | w1 | `align_v4_kit.py --check` on a clean clone of the candidate | Exit 0. Pending placeholders count as PENDING; drift or a crash is a FAIL. |
| `receipt` | w1 | Validator self-test on the candidate: an exact receipt is admitted; a digest mismatch and a working-bytes drift are refused. Then `require_registration` on the committed receipt. | The committed receipt validates. |
| `r1-w1-chain` | w1 | `R1-TO-W1-CHAIN.md` steps 1-6 as CLIs on a synthetic lane-shaped R1 record (no bundle key, X-G and per-turn counts stripped): exporter, `backfill-x-g`, `backfill-turn-counts`, `derive-contrast`, `decide`, then `kit.require_ready` and `kit --check` with the record installed | Every step exits 0. `derive-contrast` equals the kit's re-derivation. The kit binds the backfilled record. |
| `km003c-launch` | r1 | The real HAZARD_PACK driver (shared `tests/test_b5_driver.Harness`) with a live stand-in meter, clean and with the reader SIGKILLed mid-chain. Then `km003c.session_report` on synthetic members, the production meter argv, and `require_enabled` on the W1 plan. | The meter starts with the window, is SIGTERM-stopped and proven gone, and its streams are hashed in custody. A killed reader restarts into `stream-002`. The member that straddles the kill reads DC `missing` with `meter.*` flags. Members in an intact stream read `available`. Rail admission is unchanged. |
| `km003c-crash-radius` | w1 | As above, with a member that ended *before* the kill | That member keeps its DC (the protocol's per-member promise). |
| `w1-window-max` | w1 | The W1 template filled at the planning worst case (anchor 783 s, D 1,800 s, G 1,150 s, S 850 s), checked by the validator, `plan_inputs.window_max_s` (the value prepare and the plan writer use) and the b5 formula. Also L1 member fit, the 1,800 s cap, and a scan of every `EXECUTED_CLOSURE` module for an unprogrammed wait (`wait_outside_os_batch`, the R1 fault class). Then the committed `w1_plan.json`, once it exists. | The three paths agree (span 26,927 s, `window_max_s` 44,640 s ≤ 44,640). The caps hold. No unplanned wait exists. |
| `wp22-dry-run` | w1 | `JW_WP22_FULL=1 python -m unittest tests.align.test_v4_w1_synthetic` (all 18 members, injected and clean windows), plus the cold review's minimal witness (`--inject none --members 5`) | Both are green. This is the check that would have caught HIGH-1. |
| `smoke-kit` | w1 | Part B pre-qualified off the MBP. Runs the production `measurement_view` on a clean clone plus `reduce_view` plus `chain.stage_plan`. Then every Part B arm-fault expectation against the production arm CLI with a fake host and a past-t0 plan. | The reduction keeps the two smoke members, and the manifests and tree sha are re-pinned. Each smoke fault's documented refusal (needle) is what production returns, except the receipt mismatch, which can only run natively. |
| `arm-route` | r1 | `configs/align/v4/arm_routes.json` for `--next`: every step's files exist, every step's entry point answers (`--help` or usage), and run_night knows the receipt class | The route is declared and every step answers. A missing route FAILs and names item 218. |

### Result at `align/2026-11-08-v4-r11` @ `05b6d04cb` (Air, 2026-11-08; fake host, no hardware)

Both gate runs took 20-40 s with 6 jobs.

| Check | `--next r1` | `--next w1` | Finding |
|---|---|---|---|
| arm-cli | PASS (not blocking) | PASS | |
| triage-staleness | FAIL (not blocking) | **FAIL** | **G1.** The packet names `previous_window` but binds no record sha or commit, so a stale but well-formed packet admits. Fix: add `previous_record_sha256` (or commit) to the packet schema and check it against the committed record at arm. |
| calibration-stop | PASS | PASS | The planned roster tolerates the loss of two whole windows (6 × 7 = 42 ≥ 39). Losing three is `insufficient_calibration`. |
| cal-escalation-exit | FAIL (not blocking) | **FAIL** | Cold review MED-2(a) is still open: after `escalate_to_lead` no row records a ruling, so the series deadlocks. |
| kit-ready | PENDING | **FAIL** | R0 effort and the R1 values are placeholders on this branch. The R0 fill (`5d9b66dd4`) is on `lane/2026-11-07-r1-kit-r0fill`, not here. |
| receipt | PENDING | **FAIL** | Four bound artifacts do not exist yet: `r1_soak_reference.json`, `u3_bar.json`, `w1_plan.json`, `wp19_receipt.json`. `validate_u3` also refuses unconditionally (R11/R03), so no W1 can register until the U3 derivation lands. |
| r1-w1-chain | FAIL (not blocking) | **FAIL** | **G2.** Steps 1-5 and `require_ready` pass. But `R1-TO-W1-CHAIN.md` step 6 runs `kit --check` straight after installing `r1_slots.json`, and the kit then reports drift (`stages/episodes-a/order_manifest.json`). The runbook is missing an `align_v4_kit.py` regeneration step. After regeneration the refusal is only the pending placeholders. |
| km003c-launch | PASS | PASS | |
| km003c-crash-radius | FAIL (not blocking) | **FAIL** | **G3.** A SIGKILLed or crashed reader leaves its stream without a trailer. `raw_offset_ns` is then None for the *whole* stream, so every member recorded earlier in that stream also loses DC (`meter.clock_unresolved`), not only the interrupted member. `km003c_parse.raw_offset_ns` documents a fallback to the monitor-journal offset that `km003c.capture_member` does not implement. |
| w1-window-max | PASS | **FAIL** (PENDING at gate) | The sizing paths agree. The R1-filled `w1_plan.json` is not committed yet. |
| wp22-dry-run | FAIL (not blocking) | **FAIL** | Cold review HIGH-1 is unchanged at `05b6d04cb`: the witness raises `R11 contrast_fit/contrast_g0_cap_s must bind`, and the full module gives `FAILED (errors=2)`. |
| smoke-kit | PASS | PASS | |
| arm-route | **FAIL** | PASS | No R1 route is declared (item 218). The W1 route is declared and every step answers. |

`--next r1` exits 1, on `arm-route` alone. `--next w1` exits 1 on nine blocking checks. G1-G3 are new
findings from this kit. MED-2(a), HIGH-1, the pending R0/R1 inputs and the U3 stop were already known.

## Part B: native MBP smoke

**When to run it.** Run it on the MBP only, in a gap between windows. Run it before the first long
window after any code change, and in particular before W1. It needs a W1-ready kit, because it runs
the production prepare. It is never run during a window: the guards refuse if a night job is loaded,
the host night lock is held or `run_night.py` is running.

**Label.** The smoke is non-registrable and labelled `smoke`. Its session and plan ids start with
`align-v4-smoke-`. The reduced tree carries `smoke_label.registrable: false`. Its custody lives under
the smoke directory. It is never pooled, analysed, pushed or cited, and nothing from it enters the
series manifest.

### Commands

```sh
# Air: the PREQUAL at the MBP's measurement commit must PASS with --next w1 (copy the json to the MBP)
python3.13 -B scripts/align_v4_w1_prequal.py --output /private/tmp/jw-w1pq/<commit>-w1 --next w1

# MBP, magistrate, in a gap. The packet, disk config, OBC and top-up values are the ones planned for the W1 arm.
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py run --detach \
  --measurement-root $M --smoke-dir <smoke-root>/align-v4-smoke-<utc> \
  --prequal-report <copied prequal-w1.json> --next-arm-triage <w1 packet.json> \
  --w1-disk-config <R0 desk config with W1 offloads> --obc-off-attested-by <name> \
  --topup-completed-at <ISO with offset> --topup-source <name/log>
# check that <smoke-dir>/smoke-log.jsonl shows guards and prepare passing, then exit the agent session
# within about 4 min (the smoke window's agent census at t0 must see no agent)

# next activation: the PASS/FAIL table (exit 0 only on PASS)
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py parse <smoke-dir> --json <smoke-dir>/report.json
$M/.venv/bin/python -B scripts/align_v4_w1_smoke.py faults     # the arm fault catalogue
```

- `<smoke-root>` must not be under `~`. Use the run root the magistrate uses for windows.
- `--detach` re-runs the command in a new session, so the runner is not an agent process.
- The runner's own polling is a stat call every 5 s, far below the 0.05 CPU-s/s contention limit.

### Sequence and expected outcomes

| # | Step | Production code exercised | Expected |
|---|---|---|---|
| 1 | `guards` | `launchctl print`, `pgrep -f run_night.py`, host night lock, git HEAD and dirtiness, Air report | The night job is absent (exit 113), no run_night process is running, the lock is free, the checkout is clean, and the PREQUAL report is PASS with `next=w1` at this HEAD. Otherwise the smoke aborts (exit 2) before touching anything. |
| 2 | `prepare` | `align_v4_session.prepare`: the kit W1-ready check, models present, disk snapshot, `desk_identity.collect`, the plan writer. One seam: `bytes_h_session.measurement_view` is wrapped so that the session-local view's pack is reduced by `reduce_view` (`joulewise.b6.smoke.reduce_tree` plus a manifest re-pin). | `STAGED`. The session id is `align-v4-smoke-…`. The kept members are `neg8-window-start-r1` (a 1.5B NEG-8 reference) and `align-pilot-v3-episodes-a-e01` (W1 ordinal 1, 30B anchor). The kit directory and the checkout are unchanged. |
| 3 | `arm-fault:*` (7 attempts) | `align_v4_session.py install` (the production CLI) on a disposable session copy: fresh custody and a plan copy whose t0 is 10 min in the past, so `h.install` can never call the installer, even if an arm admits | See the fault table below. Each attempt is torn down. |
| 4 | `arm-main` | `align_v4_session.py install` on the smoke session: the arm checks, the triage, the W1 disk gate, `install_night_agent.sh`, launchd | Exit 0, and the night job is installed for t0 (lead 420 s, `configs/b6/loop.json`). If the fault attempts used up the lead (t0 within 240 s), the runner stages a fresh session first (`prepare-again`). |
| 5a | `meter-kill` | At the NEG-8 reference's bundle + 90 s, `pkill -KILL -f scripts/km003c_monitor.py`. The Block driver restarts the meter. | That member's DC is `missing` with `meter.*` flags. The meter restarts into `stream-002`. |
| 5b | `cpu-contender` | At the anchor's bundle + 390 s (300 s idle plus 90 s), `/usr/bin/yes` runs for 45 s in its own session, out of tree, then is terminated | The anchor carries `contention.request_overlap` (from `monitor.member_findings` over the hazard journals). Its DC stays `available`, recorded in the restarted stream. |
| 6 | `terminal` | `night/result.json`; then `launchctl print` must report the job gone (B1 latch) | Both happen before the budget runs out. |
| 7 | `finalize` | A sha256 inventory of the smoke custody (`finalize.json`). It is never pushed. | Non-empty inventory. |
| 8 | `r1-w1-chain` | The PREQUAL `r1-w1-chain` probe, run with the MBP's `.venv` | The status the probe gives (today: FAIL on G2, until the runbook is fixed). |

**Arm faults.** These are safe and software-only. Each one is its own production arm attempt.

| Fault | Injection | Expected (needle) | Teardown |
|---|---|---|---|
| `arm-control` | none | The arm admits, the W1 disk gate passes, then `plan t0 has passed` | none |
| `triage-edited` | `capture_faults` set to `fail` | `triage capture_faults failed` | none |
| `triage-stale` | A pre-R12 packet (no schema, no `full_desk_gate`) | `missing or wrong schema` | none |
| `receipt-digest-mismatch` | A disposable `git clone --shared` of `$M` at HEAD with one byte appended to a receipt-bound `.md`; the session points at the clone | `digest drift`, refused before the arm (the kit check) | The clone is removed |
| `disk-image-mounted` | `hdiutil create` of a 2 MB HFS+ image and `hdiutil attach -nobrowse -readonly` at `/Volumes/JWSMOKE` | `external_volume_mounted:` | `hdiutil detach` (`-force` if needed). The row FAILs if the volume is still mounted. |
| `topup-missing` | `--topup-completed-at missing` | `completed top-up evidence missing` | none |
| `topup-omitted` | The flag left out | argparse usage error naming `--topup-completed-at` | none |

- **Already pre-qualified on the Air.** The `smoke-kit` PREQUAL check runs six of these against the
  production arm with a fake host and gets the expected outcome for each. Only the receipt fault needs
  the MBP and a signed receipt.
- **A stale but well-formed packet is not injected.** No code path refuses one (G1). Injecting it would
  only show a known gap.
- **High Power.** Under an adopted High Power series, each fault attempt also runs the production
  High Power enter-and-restore path, and every refused arm restores Automatic.

### Parser rows (`parse`)

The parser emits one row per check below. Overall PASS requires every row to PASS.

- `labelled-non-registrable`
- `gap-guards`
- `prepare-reduced`
- each `arm-fault:*`
- `arm-main`
- `terminal-marker`
- `finalize`
- `km003c-reader`: the meter restarted at least once, its streams are hashed and present, and its stop is proven
- `meter-kill-flags-member`
- `cpu-contender-flagged`
- `w1-member-dc-available`
- `r1-w1-chain-native`
- `wall-time`: at most `budget_s` = 2,700 s

### Wall time (budget 45 min)

| Phase | Estimate | Basis |
|---|---|---|
| Guards and prepare | 3 min | The kit check is about 10 s. The measurement view and the plan writer are seconds. `desk_identity.collect` is one venv script. |
| 7 arm-fault attempts | 3 min | About 15 s each (the kit check dominates), plus about 1 min for the receipt clone |
| Wait to t0 | about 1-2 min | 420 s lead from prepare |
| Driver arm dwell | about 3-5 min | 180 s clean contention, plus quiet admission |
| Bracket reservation and pre-calibration | about 4 min | Not measured; the first run times it |
| NEG-8 reference (1.5B) | about 2 min | Idle 57.6 s plus a short request |
| W1 anchor (30B) | about 13 min | Planning member_s 783 s |
| Post-calibration, verdict, backup | about 5 min | Not measured |
| Finalize and native chain | about 1 min | |
| **Total** | **about 36-41 min** | `wall-time` FAILs above 45 min. If the first run is over budget, drop `align-v4-reference-start` from `keep`. That saves about 2 min but moves the meter kill onto the anchor and loses the clean-DC row. |

### Verified here vs on the first native run

**Verified on the Air** (tests: `tests/align/test_w1_smoke.py`, `tests/align/test_w1_prequal.py`, one module
per process):
- the runner end to end on a fake MBP: every step, the fault judgement, re-staging when t0 is too
  close, guard aborts, a disk image left mounted, an over-budget run, a refused main arm, and missing
  member flags;
- the reducer on the real production measurement view;
- the fault expectations against the production arm;
- the parser over a synthetic custody, through the production KM003C and contention readers.

**Native assumptions the first run checks.** If any of them fails, the corresponding row FAILs.
- The plan writer accepts the reduced view pack, whose external manifests are re-pinned.
- The chain's `run_campaign` honours the pack-local truncated order manifests.
- The contender and meter-kill offsets land inside the intended request.
- The calibration-capture durations fit the budget.

## Recommendation to the lead

- **Before R1:** run Part A with `--next r1` at the R1 measurement commit. Today it blocks only on
  `arm-route`, which is the item 218 fault. The ruled R1 route adds its entry to `arm_routes.json`.
- **Before W1:**
  - Part A with `--next w1` must PASS. That needs HIGH-1 fixed, MED-2(a) fixed or waived, and G1, G2
    and G3 fixed or waived by a lead ruling.
  - Then the magistrate runs Part B in the gap after R1 closes and registration is signed, and before
    the W1 arm. This is a ≤45 min smoke.
