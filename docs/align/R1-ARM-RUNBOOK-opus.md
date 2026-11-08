# ALIGN v4 R1 arm runbook (Opus build)

Branch `lane/2026-11-08-r1-arm-opus`, from `d9d1098c6`. This is one of two independent
builds (RUN_STATE item 220). **Do not arm from this runbook until a lead ruling item names
this route and its sha.** The comparison with the Sol build is `docs/align/R1-ARM-AGREEMENT.md`.

## 1. The route and why it is the smallest correct one

R1 runs as a **`DIAGNOSTIC_NO_PACK` night under the unchanged `run_night` driver**, with:

- a **ruled, chain-bound registration**, `configs/align/v4/r1_night_registration.json`
  (`night_gate.RULED_REGISTRATIONS`, `binds_chain: true`). It pins the R1 chain's SHA-256
  and the window sizing constants;
- a **payload kind** `align_v4_r1` (`joulewise/night_kinds.py`). It makes C5 authenticate
  the R1 chain source against the committed blob at `measurement_head` and against the
  wrapper's pinned digest. It also makes C1 demand the chain-bound registration;
- a **generated wrapper** (`scripts/write_align_r1_night.py`). It adds the KM003C meter, display
  sleep and a 300 s dwell, then runs `scripts/night_chains/align_r1_rehearsal.zsh` unchanged as a
  child and returns its exit code.

No R1 measurement code changed (`scripts/align_r1_rehearsal.py`, the R1 chain,
`joulewise/align/apple/r1_runtime*.py` are byte-identical to `lane/2026-11-06-v4-r1-integrated`).
Arming code changed in three places, each additive:

| file | change |
|---|---|
| `joulewise/night_kinds.py` | new row `align_v4_r1` |
| `joulewise/night_gate.py` | one new `RULED_REGISTRATIONS` entry (and its digest constant) |
| `joulewise/night_agent_install.py` | an `align_v4_r1` chain is never probed or executed at install (the HAZARD_PACK rule) |
| `scripts/run_night.py` | `_probe-worker` refuses an `align_v4_r1` chain (never executes it) |

The other routes were rejected:
- **HAZARD_PACK** needs a v5 pack: a plan tree whose stage graph starts with the bracket
  reservation and pre/post calibration captures, a config inventory for lineage, and members
  for the yield plan. The R1 chain is none of these. Wrapping it means building a fake pack or
  changing the b5 chain renderer and driver.
- **An R0-style launcher** (`launch_align_r0.py`) caps the desk at 12 h and has no meter, no
  `run_night` deadline, census or custody. Each of those would have to be rebuilt.

### Arm-time guarantees, and where each comes from

| guarantee | enforced by | weakened? |
|---|---|---|
| agent census | `run_night` initial census, gate C3, then the in-chain census every 30 s with abort | no (unchanged) |
| quiet guard / contention before start | network time OFF + 600 s settle, overlapped with `prewindow_check.sh --wait`: 600 s continuous clean, ≤ 5 % CPU per contaminating process, load ≤ 2.0, 45 min cap; C3 load ≤ 2.0 and thermal | no (calibration-night admission, unchanged) |
| contention during R1 | R1's own ruling 8 journal: redo a quiet segment on > 0.5 core for 60 s, at most 2 redos | no (R1 code) |
| display | wrapper `pmset displaysleepnow`, then a 300 s dwell (R0-L3), recorded; C3 reads `displaysleep`; the magistrate also sleeps the display before exit | added |
| external volume | R1 driver ruling 20 census at t0, before every runtime call and before r1_slots; refusal exit 3 | no (R1 code) |
| KM003C | wrapper runs `scripts/km003c_monitor.py` (the program the HAZARD_PACK driver supervises) into `<custody>/hazards/meter/stream-NNN.jsonl`. A clean exit (absent meter, or stopped) is final; a crash restarts after 30 s. It is stopped by a stop file after R1 | added; record-only, as in HAZARD_PACK |
| AC powermode | `run_night` admission at plan 0 (restores an R1 marker first); R1's own guard and host lock for its A-B-A legs; R1 chain EXIT trap | no (unchanged) |
| custody | write-once night records, C5 clean checkout at `measurement_head`, C1 ruled registration, wrapper sidecar, R1 source digest (gate and wrapper) | no |
| deadline watchdog | `_WindowDeadline`: TERM, then KILL of the chain group at `t0 + window_max_s + 300 s`, proven gone; launchd dead-man; magistrate watchdog plan span | no (unchanged) |
| finalize | R1 `harvest` segment; wrapper stops the meter; `run_night` result, artifacts, courier | no |

Not carried over (stated, not hidden):
- **The installer's launchd probe.** It is skipped for this kind, as for HAZARD_PACK. The probe
  executes the chain in verify-only mode and binds the calibration ledger, which R1 does not use.
  Executing this chain would start R1. Its powermetrics cadence check is therefore not run. A broken
  powermetrics fails R1's first model segment, and R1 refuses (exit 3).
- **The QPE-only predicates.** The non-observer interval and the corecaptured predicate are not
  turned on for this kind.

## 2. Sizing: `window_max_s`

**R1 can redo** (ruling 8 load redos, the R6-2 G0 retries), so **the item 216 redo floor applies:
96,427 s**, and not item 215's 67,371 s.

The route adds its own bracket, close and harvest allowances. They are pinned in the registration:

| term | s |
|---|---|
| R1 redo floor (items 215/216; one 11,164 s batch encounter included) | 96,427 |
| admission before the chain (OFF settle overlapped by the ≤ 2,700 s clean dwell, gate probes) | 3,000 |
| display dwell | 300 |
| meter start and stop | 30 |
| R1 calibration-pre and -post brackets (`night_worst_case_s` bounds them at 0) | 600 |
| R1 harvest (SHA-256 of the R1 output) | 1,800 |
| close (R1 teardown, Automatic restore, child proofs) | 120 |
| **total, rounded up to a minute** | **102,300 (28.42 h)** |

Each additional local 11:45 inside `[t0, t0 + window_max_s]` adds 11,164 s (item 216: "11,164 s per
segment that can touch 11:45-13:15"). The generator iterates this to a fixed point:
- a t0 between about 07:20 and 11:45 PT reaches two 11:45s, which gives 113,460 s;
- any other t0 gives 102,300 s.

`NIGHT_PROGRAMMED_SPAN_S = window_max_s − 3,000`. So run_night refuses to start the chain later than
t0 + 3,000 s, and R1 always has its full allowance.

Print the sizing for a candidate t0:

    python3 -B scripts/write_align_r1_night.py size --t0 2026-11-08T13:30

**Recommended t0: 13:20-14:00 PT.**
- The first quiet segments then run in the afternoon and evening.
- The single batch-window encounter falls near the end, next day.
- The night ends about 17:50-18:30 PT the next day.

Avoid a t0 between 07:20 and 11:45 PT. It costs 3.1 h.

Notes:
- The launchd dead-man plist carries only Hour and Minute. Its first firing, about 5.4 h after t0, stands
  down ("dead-man fired before the night's completion epoch"). Its next-day firing is the real one.
- `PLAN_MAX_AGE_S` (36 h) is checked at t0 only.

## 3. Magistrate commands (MBP)

Placeholders: `$SHA` is the ruled sha; `$MROOT` is a fresh measurement checkout that **must be under
`/Users/edr/night-custody/measurement/`** (gate C5 rule for plans authored after the custody cutoff);
`$CUSTODY` is a new empty custody root, for example `/Users/edr/night-custody/align-r1-<date>/custody`.

1. **Measurement checkout.** Make it clean, at `$SHA`, with the pinned venv at `$MROOT/.venv`, as for R0
   and W1. Then:

       git -C "$MROOT" rev-parse HEAD      # = $SHA
       git -C "$MROOT" status --porcelain  # empty

2. **Host prerequisites** (each one is also enforced at t0):
   - On AC, with the battery at float. The installer and C3 refuse otherwise.
   - Screensaver `idleTime` 0 (C3 HID).
   - These four `sudo -n` rules exist:
     - `pmset -c powermode 0`
     - `pmset -c powermode 2`
     - `systemsetup -setusingnetworktime off`
     - `systemsetup -setusingnetworktime on`
   - `pmset -g custom` AC `powermode` reads 0.
   - **No external volume:** `/sbin/mount | /usr/bin/grep -v ' on / \| on /System' ` lists no `/Volumes/*`
     disk, and the SSD stays unplugged for the whole night.
   - `launchctl print gui/$(id -u)/com.joulewise.night` must say the service is absent.

3. **Write the plan.** Run this from the measurement checkout, so `repo_head` = `measurement_head`:

       "$MROOT/.venv/bin/python" -B "$MROOT/scripts/write_align_r1_night.py" write \
         --measurement-root "$MROOT" --custody-root "$CUSTODY" --t0 2026-11-08T13:30

   Keep the printed `plan.sha256`, `window_max_s` and `plan_id`.

4. **Desk check** (the static gates with the real probes at t0; launches nothing):

       "$MROOT/.venv/bin/python" -B "$MROOT/scripts/write_align_r1_night.py" check --plan "$CUSTODY/night_plan.json"

   It must print `"verdict": "STATIC_PASS"` with C1 and C5 PASS.

5. **Arm notice to Ed, before install.** Mail it on the R1 thread. It must say:
   - R1 arms on route `<route>` @ `$SHA` (lead ruling item N);
   - t0 (PT) and `window_max_s`, and the latest end, which is t0 + window_max_s + 300 s;
   - the MBP stays agent-free until then;
   - the SSD and any external disk stay unplugged;
   - the display is asleep;
   - Ed should not wake or touch the MBP until the end time. Waking the display restarts WindowServer bursts:
     these can fail the t0 clean dwell, and during R1 they can trigger load redos.

6. **Install** (the shared installer; no probe for this kind):

       "$MROOT/scripts/install_night_agent.sh" --plan "$CUSTODY/night_plan.json" \
         --python "$MROOT/.venv/bin/python"

   It must print the two plist paths.

7. **Display asleep, then exit before t0.**

       pmset displaysleepnow

   Then end the magistrate session and every agent child. Install closes at t0 − 10 min, so allow at least
   20 min between install and t0. The initial census at t0 refuses on any `claude` or `codex` process, and
   the in-chain census aborts on one for the whole night. The watchdog's plan span keeps the magistrate down
   until the dead-man epoch.

8. **After the night** (next activation):
   - `pmset -g custom` must read powermode 0.
   - Re-enable network time: `sudo -n /usr/sbin/systemsetup -setusingnetworktime on`. run_night's
     calibration admission set it OFF and nothing restores it.
   - Read `night/result.json`, `night/align-r1/r1_result.json`, `night/r1_wrapper.jsonl` and
     `hazards/meter/`.
   - Commit the R1 record (item 185 pattern), mail Ed, and hand item 202 (5)-(7) to the lead.

## 4. Refusals and what to do

| where | code or symptom | do |
|---|---|---|
| `write` | registration "not a ruled, armable registration" | wrong checkout or edited registration; use `$SHA` |
| `write` | chain "not the bytes the registration binds" | R1 chain drifted; stop and escalate (the chain is frozen) |
| `write` | custody not empty / t0 past / not minute | a new custody root; a t0 on a whole minute ≥ 20 min ahead |
| `check` / t0 | `night_plan_stale` | checkout dirty or HEAD ≠ plan; recreate the checkout, rewrite the plan |
| `check` / t0 | `measurement_root_outside_custody` | move the checkout under `/Users/edr/night-custody/measurement/` |
| `check` / t0 | `night_chain_digest_mismatch` | wrapper, sidecar or R1 source changed; rewrite in a new custody; escalate if the R1 source changed |
| `check` / t0 | `night_refused_registration` | registration bytes differ from the ruled digest; use `$SHA` |
| install | battery not at float | wait for float on AC; never bypass |
| install | existing night records / launchd already holds the job | do not arm over another night; new custody, or wait for the other night |
| t0 | census refusal (agent present) | the magistrate did not exit; re-arm with a new custody and t0 |
| t0 | `night_refused_ac_powermode` | the host was not at 0, or the marker restore failed; check `pmset -g custom`; escalate if a restore fails |
| t0 | `night_probe_error` "clean dwell refused/timed out" | no 600 s clean stretch inside 45 min; item 194 (3): identify the source in `night/clean_dwell.output.txt`; re-arm after it, or mail Ed if unscheduled |
| t0 | `night_refused_hid_idle` / `night_refused_not_quiet` (ac, display, load, thermal) / `night_refused_battery_float` | fix that host condition; re-arm with a new custody |
| t0 | `night_window_expired` | launchd fired late (sleep or reboot); re-arm |
| night | `ABORTED night_aborted_agent_present` | an agent started during R1; the chain was stopped and R1 restored Automatic; re-arm later |
| night | `night_window_exceeded` | R1 overran the sized window; R1 is cut (item 202: accepted); report the segment it reached |
| night | verdict GO, exit 5, chain exit 3 | the R1 driver refused (sudo rule, external volume, segment contaminated after 2 redos, contract violation); read `align-r1/r1_result.json` `error`; Automatic was restored by R1 |
| night | chain exit 65 | the wrapper found the R1 source changed between gate and launch; escalate |
| any | NEEDS_RULING (data that counts would change) | a RUN_STATE item to the lead; Ed only if the lead is silent |

## 5. Item 202 (4), answered from the code

**Question:** how is a scheduled macOS job that fires mid-night handled in an R1 segment?
- the softwareupdated scan (about 23:09, 05:09, 11:09)
- the 00:00 `/tmp` cleaner
- XProtect
- the 12:53 maintenance

**In a quiet segment:**
- These are the idle soak, step-30b, step-d, the three planning-turn states and the three A-B-A legs.
- The runtime journals `cpu_busy_cores` once a second: summed %CPU of every process outside its own
  tree (`QUIET_FIELDS`).
- The driver's `os_load_verdict` sets `redo` only for > 0.5 core (`CPU_BUSY_CORES_LIMIT`) for ≥ 60
  consecutive seconds (`CPU_BUSY_SUSTAINED_S`).
- A shorter or smaller burst is **recorded only**. For scale, R0 re-run 11 saw the softwareupdated scan at
  0.25-0.29 core, which is below the bar.
- A sustained one rejects that attempt: it is renamed `.rejectedN` and the segment is redone.
  - A heavy segment's redo starts only after a `g0-release-soak` release.
  - There are at most `MAX_SEGMENT_REDOS` = 2 redos.
  - A third contaminated attempt **refuses R1**: "segment still contaminated after 2 redos", exit 3. The
    night ends there, and Automatic is restored.
- So the answer is **dwell-and-redo, then night refusal**. It is never a segment marked INCONCLUSIVE.
  INCONCLUSIVE is only for a G0 timeout (R6-2).

**Avoided by schedule:** only 11:45-13:15 local (ruling 8, `wait_outside_os_batch`). It covers the 12:53
maintenance.
- A quiet segment whose bound would overlap that window waits until 13:15.
- The 11:09 scan is not covered.

**In the other segments** (X-G, the gated D runs, d-4bit, the harvest): there is no load journal and no
redo. A burst there is unmeasured contention inside the member's own records.

**At admission:** a job firing in the 45 min before the chain starts delays the start: the clean dwell needs
600 s continuous below 5 % per process. If no such stretch comes within the cap, the night refuses.

**Advice:** start at 13:20-14:00 PT. Then:
- the first quiet segments (the soak, 30B, A-B-A) run in the afternoon and evening, clear of the 23:09
  scan for several hours;
- the 00:00 and 05:09 events can still meet a later quiet segment, and the R1 driver redoes it.

No pre-arm mail to the lead is needed: the handling is a redo, not a night refusal, unless the job is
sustained across three attempts of one segment.

## 6. Verification on this branch

`tests/align/test_r1_arm_route.py` runs the real `run_night` and the real gate on a generated plan, launches
the real wrapper and the unchanged R1 chain, driver and runtime (synthetic backend, `FakeWorld` sudo/pmset
boundary through `tests/align/r1_arm_bootstrap.py`), and checks:
- GO;
- r1_result `complete`;
- the C1 digest and the C5 kind and source;
- display sleep before R1;
- a meter stream with header and trailer, stopped by its stop file;
- Automatic at the end.

Negative cases check:
- a changed registration refuses at C1;
- a changed R1 source refuses at C5;
- in both, the chain is not claimed.

Run: `python3.13 -B -m unittest tests.align.test_r1_arm_route`.
