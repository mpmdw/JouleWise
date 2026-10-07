# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **DRAFT, NOT SEALED. Revision 7, 2026-10-07.** Written by Opus 5.5, as lane L6 of the gate-prune workflow
(revision 3, commit `71c91d74`), then as the registration-sync side lane (revision 4, last commit `7261a585`), then
as the REG lane of gate-prune round 3 (revision 5, last commit `9d63b4df`), then as the REG sync to the frozen head
(revision 6, last commit `c6843537`), then as the REG sync to the audit fixes and the NEG-8 ruling (revision 7), on
branch `design/2026-10-05-v5-claim-block-draft` (revision 2 is commit `bfd1ee8c`). This file authorizes no arm, no
launch and no analysis. It binds only when one cold gate (§0.1, §12) seals it together with three companions in the
same directory:

- `analysis_plan_block5.md`, the **analysis plan**: what is computed from the collected bytes, and how;
- `flag_catalog.json`, the **flag catalog**: for every flag code, whether it removes a member from the claims,
  removes a whole window, or is only disclosed (§6);
- `sealed_inventory.json`, the **sealed inventory**: the SHA-256 of every file a window executes, at the commit the
  windows run (§11). At this writing it is a stub; it is filled at seal.

A **FILL**, written `FILL[NAME]`, is a value that must be tied to authenticated bytes before the point named in §13.
It is never a default. One FILL is a marker on values that are already written: `FILL[B5-FINAL-HASHES]` follows each
digest that was computed at the int5 head `d3c107f2f` (§2 item 1) and must be recomputed at the integration's final
head before the seal; a value so marked is correct for `d3c107f2f` and may change. No claim-eligible `_v5` energy
exists at this writing, and none was read (§16).

**What changed from revision 2.** On 2026-10-05 Ed ruled that arming refuses only on a physical hazard, measured
directly, and that every other check becomes a recorded flag (Ed: "this again feels like in ability to prune silly
gates that prevent data collection for the sake of semantics not science"). Revision 2 let a window start only
after a chain of receipts verified, and discarded a whole window when one member failed. Revision 3:

1. refuses a window before it starts only on a measured physical hazard (clock, battery, thermal pressure, a
   competing process, free disk, the sampler) or on the agent census (a check that no AI agent session is running
   on the machine), which doctrine keeps (§4);
2. turns every other check into a **flag**, a recorded fact that never stops collection; the sealed flag catalog
   decides which flags remove a member or a window from the claims (§6);
3. has the harvest (the desk program run after each window) always emit the numbers plus the flags. A window is
   **claim-usable** when no window-removing flag fired and each reported number still rests on at least 8 of its 10
   planned independent repeats and 8 of its 10 planned groups of four interleaved members (§0.8, §6.6). Each pack's
   analysed window is its first claim-usable attempt (§7.2);
4. folds block 4, the separate qualification window, into block 5: G10, a deliberate clock step that shows the
   clock check can see one, runs as a recorded diagnostic at the tail of the first ALPHA window (§3).

§15 maps each item of the approved implementation plan (`/Users/edr/night-archive/gate-prune/PLAN.md` §6, items
1–15) to the section that carries it.

**What changed in revision 4.** This revision brings the text into line with the integrated code (branch
`feat/2026-10-05-gate-prune`, commit `f8164893`). No threshold changed except by the timing ruling of item 6.

1. §5.3: each window starts with 12 reference runs, the NEG-8 corpus, from which a drift bound is derived (§0.12). A
   window in which only 10 or 11 of them succeeded no longer loses that bound: the harvest validates the bound
   against the members actually collected and re-screens the window against it (§14 Q1 closed).
2. §4.6 item 3: the pins that fix which model files and runtime versions may be measured live in
   `identity_pins.json` in this directory, not in the packs' plan trees.
3. §6.3, §6.5: the whole-window verdict (one pass/fail record over the whole window, §0.17) stays disclosed rather
   than window-removing, but each member it fails is now removed by a new member code,
   `member.whole_window_member_failure`. Without that code, revision 3 had dropped the check that the displays stayed
   asleep and the screensaver off through each request, which decision D-078 (item 4) installed after a screensaver
   contaminated captures in July 2026. Also, `calibration.ledger_snapshot_refused` now removes the window: the
   calibration bracket is judged from that same ledger, so the bracket check already fails with the same reasons.
4. §5.5: the sizing output is filled in, and revision 3's claim that a generous window deadline costs nothing is
   withdrawn. The supervising watchdog treats a window as running until its scheduled start plus that deadline, which
   is about 15 h after a normal chain ends (§14 Q8).
5. §1, §4.2, §5.6: the boundary label and the backup destinations are filled in. The backups sit on the same disk
   volume as the collected data, so the disk check at arm counts three copies of the window's bytes there, not one.
6. §0.3, §0.6, §0.13, §2, §4.6, §5.1, §5.5: the cold-judge timing ruling of 2026-10-06
   (`/Users/edr/night-archive/gate-prune/timing/RULING_fable_cooldown_2026-10-06.md`). The cooldown now starts the
   next member at the first 5 s reading at or below twice the previous member's idle baseline (was: 30 s within
   10%), under a new block-5 policy file; the idle baseline is 576 records, about 75 s (was 750 records, about
   98 s), with the admission tests unchanged; all eleven settles are 60 s (was 180 s); a battery-temperature
   diagnostic is added as a disclosed flag; and one 15-minute machinery smoke of the new cooldown is required before
   the seal. The packs, the identity pins and the sizing output were regenerated.

**What changed in revision 5.** This revision registers every decision of 2026-10-06 that changes collection or
claim use, checked against the integration head `b9d02700a` (branch `integrate/2026-10-06-gate-prune-3`, whole suite
green). A last code round (P3: lanes `lane/2026-10-06-p3-{harv,haz,drv,wd}`) is in flight; where this text describes
behaviour that only P3 installs, it says so, and the item is listed under §13 as a sync point to check before the
seal. Lane names (P2-…, P3-…, L10) and design-row ids in parentheses (PLAN2 row 8, core-prune A14, interface J1) are
citations for tracing a rule to the record that motivated it; no rule here depends on them for its meaning.

1. **Battery** (§0.17, §4.2, §6.4, §6.5, §9.2): the battery current is read from the SMC (the Mac's power
   controller) once a second instead of from the battery registry, which republishes only once a minute. The battery
   supplying part of the load while the adapter is connected and the battery is not charging ("assist") is now
   disclosed (`battery.assist`), not excluded; charging, loss of AC power and missing evidence still exclude. The same
   rule applies to calibration captures. The arm refusal is unchanged. The orchestrator's ruling of 2026-10-06
   (`/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`) and its reasons are in
   §9.2.
2. **Whole-machine meter** (§0.17, §1, §6.8; analysis plan §8.2): an inline USB-C power meter records the Mac's
   DC input at 50 samples per second. It is a recorded diagnostic with a pre-registered descriptive analysis. It never
   refuses, excludes or enters a claim number.
3. **Timing** (§3, §4.1–4.3, §5.1–5.5, §10): stand-down leads of 180, 90 and 60 s; operator countdowns of 0 s
   except at the post calibration (the fifth registered deviation); a contention dwell of 180 s instead of 600 s; a
   collection deadline that keeps the post calibration inside the 24 h calibration horizon; one retry of the NEG-8
   corpus; a 1,800 s cap per member; strict validation moved to the harvest; the calibration refit done once per
   window; the watchdog releasing a finished window at once; the sizing and the expected chain re-derived.
4. **Yield tripwire** (§5.7, §7.3): the driver counts collected bundles per stage and at the window's end, flags
   empty and short stages, and gives the window a yield status; a process rule stops a deterministic loss from
   repeating through back-to-back windows.
5. **Checks that now record instead of refusing** (§5.3, §6.10): the NEG-8 corpus drop rule (one closed list shared
   by the mint and the harvest), physical timestamps for the NEG-8 bound's age, the power-supply and OS-build
   strings disclosed, the cooldown fallback reference, and the controller, fiducial-writer and reservation records.
   Historical calibration custody is re-verified at the harvest, and a mismatch removes the window. The arm's one
   identity refusal, an OS build no acceptance judged, is registered (§4.7).
6. **GAMMA's interior references** (§0.7, §0.12, §2, §4.6, §5.1, §5.5): lane L10's erratum is applied.
7. **Era pins** (§11 item 5): two older documents' digests are records of their era; the block's live pins are the
   sealed inventory at H_claim.
8. **Catalog** (`flag_catalog.json`): `battery.assist` (DISCLOSE), `calibration.historical_custody_mismatch`
   (EXCLUDE_WINDOW) and `calibration.historical_custody_unmeasured` (DISCLOSE) are added; the battery notes follow
   the ruling.

**What changed in revision 6.** Revision 5 described several rules "as P3 will install them". The P3 round, lane
L10, a **refusal census** (a sweep that listed every place the code can refuse, stop or exclude, and turned each one
that was not physics or number protection into a flag) and an integrator's triage of what the census found have
since been merged into one **frozen head**: the commit the integration stopped changing so that the review gates
before the seal all judge the same bytes. It is commit `a434e363d96621318657418e60b8d14410079d82` (branch
`integrate/2026-10-06-gate-prune-4`; whole suite run at that commit, `/Users/edr/night-archive/gate-prune/
FROZEN_HEAD.md`), and it is the candidate for H_claim (§2 item 1). This revision reads that code and makes the text
say what it does. Where the code chose differently from revision 5, the text now follows the code; each such place
is listed here and in the sync record of §13. No registered threshold changed.

1. **Battery** (§4.2, §6.3, §6.4, §6.5, §9.2): assist is now **any** negative battery current read from the SMC,
   not only one below −200 mA; −200 mA is the threshold the assist report counts reads against. The
   charge-accumulator test keeps its own code, `battery.accumulator_excursion`. The assist report splits a member
   into the code's three phases: before the measured request, the request, after it. A calibration capture's assist
   is `calibration.capture_battery_assist`. A member's #421 pair (the battery registry read just before and just after
   its sampler stream) that failed on discharge alone is disclosed when the SMC reads cover the member. With SMC
   coverage, a hole of more than 120 s between registry reads of the charging and AC state makes the member
   `battery.unmeasured`.
2. **Desk order** (§2, §4.6 item 6): the **pin advance** (the pin-only commit that moves the repository's record of
   the calibration ledger's tip to this window's last entry) now comes **before** the harvest, not after it, because
   the program that writes the whole-window verdict at the desk reads the ledger through that committed record.
3. **Clock** (§4.2): a clock sample whose three reads took more than 250 µs is re-read up to five times and is
   otherwise unmeasured, never a step (`FILL[P3-CLOCK-SKEW-BOUND]` filled).
4. **Driver** (§0.17, §2, §5.4): the monitor and meter stop at least 5 s after the chain exits, after G10; the
   pre-launch lineage check records a mismatch (`records.lineage_prelaunch_mismatch`) and refuses only when the
   machine rebooted since the lineage was published.
5. **Records that no longer remove anything** (§6.3, §6.8, §6.10): `member.stderr_uncopied` is disclosed; an
   exception inside the member environment guard's collector is disclosed (`env.member_guard_flagged`, finding
   `collector_raised`); a historical calibration capture whose bytes changed removes the window only when this
   window's acceptance relies on it (`calibration.historical_custody_mismatch_unused` otherwise).
6. **A new window exclusion** (§6.5): `whole_window.member_failures_unreadable`, when a verdict that did not pass
   cannot name the members it failed.
7. **Which refusals may remain** (§6.11, new): every refusal left in the code is either physics or the protection
   of a number, and a test enforces the list.
8. **Fills** (§2 item 7, §2 item 8, §13): the cooldown smoke record, the P3 sync record and the sizing and pin
   digests at the frozen head.
9. **Smaller corrections:** the meter's restricted record is one file, `withheld/meter.json` (§5.8); G3 does not run
   on the floor packs (§2 item 7, §6.8); GAMMA's battery-assist line is adopted (§14 Q9 closed; analysis plan §8.1).

**What changed in revision 7.** After the frozen head, the pre-arm audits (§9.1) and a Fable cold pass found defects
that two fix lanes (`lane/2026-10-07-audit-fixes-1`, `01232742e`; `lane/2026-10-07-audit-fixes-2`, `0571cf8fd`) and
one ruling lane (`lane/2026-10-07-neg8-survivors`, `2011ec285`) repaired. All three are merged in the integration
branch `integrate/2026-10-07-int5`, whose head at this writing is `d3c107f2f` (`/Users/edr/code/JouleWise-wt-int5`).
This revision makes the text say what that code does. The finding labels in parentheses (A1, F3, N4, item 6) cite the
audit or cold-pass record a rule came from; no rule depends on them for its meaning.

1. **Lost NEG-8 references** (§0.12, §5.1, §5.3, §5.5, §5.7, §6.5; analysis plan §2.4). *Forcing problem:* the
   screen accepted exactly 3 start, 1 midpoint and 3 end references, so one start reference aborted by idle admission
   made the counts (2, 1, 3), which the screen called invalid, and the whole window was removed (Opus audit F1); and a
   reference whose request overlapped a competing process removed nothing, although its energy entered the screen and
   the allowance (Astra audit A1). A cold ruling of 2026-10-07 (`/Users/edr/night-archive/gate-prune/neg8-council/
   RULING.md`) replaced the exact-count rule: a lost reference is dropped, each reference stage gets one retry from
   pre-registered spare members, the screen runs on the survivors (at least 2 at each endpoint) against a bound sized
   to the surviving counts, and a corpus member with a physics exclusion is dropped from the bound. Two disclosed codes
   are added, `neg8.reference_lost` and `neg8.midpoint_lost`; the analysis plan makes the second claim-excluding for
   GAMMA's primary contrasts. The first fix lane's interim answer to A1, a window exclusion for any physics flag on a
   reference, is superseded by the ruling: its flag code was deleted from the harvest, both catalogs and the allowlist.
2. **An unread hazard probe at the arm** (§0.15, §4.1). UNMEASURED now refuses only for the instrument; for the
   other five hazards it is the disclosed flag `<module>.arm_unmeasured`, because the monitor measures those hazards
   over every member span anyway (audit A3).
3. **The agent census** (§4.5, §5.1, §5.7). A listed process counts only when its executable is an agent's, and the
   window's own process tree is ignored, so a run id containing "t3" no longer stops a window (Opus audit F3). In the
   window an unreadable census is disclosed and never stops the chain (audit A3).
4. **No code is permanently unclassified** (§6.2, §6.10). A flag line that fails validation is disclosed, with an
   exclusion beside it when the line could have been one (Opus audit F2).
5. **Smaller code changes:** the monitor's clock skew bound follows the plan's step threshold (§4.2); the monitor and
   the meter stay supervised during G10 (§5.4); an unusable pack inventory refuses before launch (§0.17, §6.11); the
   exclusion function resolves bundle ids (§0.16); the powermetrics digest is re-derived at harvest on the collection
   boot (§6.3, §6.10); a sign-inconsistent discharge accumulator under SMC coverage is disclosed (§6.4); operating-system
   metadata files are not source changes (§6.5); a post-run guard collector exception is disclosed on the verdict path
   only (§6.3, §6.10); two new runner record kinds and one new writer record kind (§6.10); the monitor's restarts and
   unverified orphans are written (§6.8); model identity can be superseded at harvest (§7.2).
6. **Re-derived artifacts** (§0.7, §4.2, §4.3, §4.6, §5.5). The spares change the plan trees, the identity pins (which
   record the plan-tree digests), the sizing output and each window's planned disk bytes. Each digest is given at
   `d3c107f2f` and marked `FILL[B5-FINAL-HASHES]`.
7. **Catalog** (`flag_catalog.json`): the fourteen codes above are added with the code's effects (§13).

## 0. Terms, built in the order they are used

### 0.1 People, seats and records

- **Ed** owns the capstone project and this machine. **The lead** is the orchestrating Opus 5.5 session: it
  dispatches seats, decides, records dissent and merges. A **seat** is one model session the lead dispatches with a
  written brief: Sol 6.1 (the default implementation and review seat), Opus 5.5, or Fable 5.1.
- **Consult.** One blind round from two seats, each licensed to disagree; the lead decides and records dissent.
- **Cold gate.** An independent ruling on a named question by a **judge** seat with no prior involvement, checked by
  a **refuter** seat whose job is to show the ruling wrong. A challenge that survives goes back to the judge once; a
  disagreement settles in one erratum, not a chain. A **cold erratum** is a change to a sealed document made this
  way; it is **prospective** when it is made before the bytes it governs exist.
- **R3.** The standing route for a tooling fault: fix it in a reviewed pull request, merge, then re-run the failed
  *desk* step (a step run after collection, at the desk) on identical bytes. R3 never re-collects anything.
- **Custody.** A directory whose files are written once, never modified, and listed with their SHA-256s.
  **Restricted custody** is custody that only automation may read until the **release event** (the recorded moment,
  after the block closes, from which energies may be read, §8); nothing in it is printed, emailed or committed
  during the measurement block.
- **To tie** a value to a file is to record the file's path and SHA-256 beside the value.
- **D-numbers** (D-078, D-179, …) are the project's numbered decision records in `docs/decision_log.md`; each is named here
  by what it fixed. **#416** and **#421** are Ed's numbered directives (the pre-arm audit, §9.1; battery float, §9.2).

### 0.2 The machine and the sampler

The machine is one Apple M3 Max laptop (model identifier Mac15,9) running macOS build 25G83 on a 140 W mains
adapter. Everything below happens on that one machine.

- **Sampler.** macOS `powermetrics`, asked for one **power record** every 100 ms. It never samples faster than
  asked; in block 3 a record actually spanned 127–130 ms (median 128.8 ms). Each record states the average power
  over its own time span (its **support**) of the processor rails, CPU, GPU and ANE combined (`combined_power_w`,
  `joulewise/adapters/powermetrics.py`).

### 0.3 A member, step by step

A **member** is one run of one inference request in its own process. Its steps, in order:

```
 prepare | idle baseline (idle admission; one retry if refused) | warm-up | measured request | cleanup | reducer
          |<--------------------------- sampler stream ------------------------------->|
 ...then, before the next member of the same stage starts: cooldown (§0.6)
```

- **Idle baseline.** The sampler records the idle machine for a fixed number of power records. The adapter sets
  that number from the configuration's `idle_seconds` as if a record arrived every 100 ms, the requested interval:
  records = ceil(`idle_seconds` / 0.1) (`joulewise/adapters/powermetrics.py` `_idle_count`). The sampler in fact
  delivers a record about every 130.5 ms (130.2–132.1 ms over block 3's 37 idle captures), so the record count, not
  the setting, fixes how long the baseline lasts. Every `_v5` pack sets `idle_seconds` 57.6: 576 records, which over
  those 37 captures would have spanned 75.0–75.9 s (median 75.2 s). 575 records would have fallen short of 75 s on
  11 of the 37. The packs set 75 s until the timing ruling of 2026-10-06 (§0.6); that gave 750 records spanning
  97.7–98.9 s. **Idle admission** then tests whether the machine was quiet during that baseline (the tests are in
  §0.13; they did not change). Replayed on the first 75 s of block 3's 37 captures, the unchanged tests changed one
  verdict, from pass to refuse: the 8B p4096 probe, a workload outside this registration (its CPU-busy 95th
  percentile rose from 0.469 to 0.576).
- **Warm-up.** One untimed generation of the same request, so the measured request does not pay first-call costs.
- **Measured request.** The request whose energy is reported: 11.1–23.6 s long in block 3.
- **Reducer.** `joulewise/reduce.py`, which turns the raw power records and the event timestamps into the member's
  summary (`summary_metrics.json`).
- **Sampler stream.** One continuous `powermetrics` process from the start of the idle baseline to the end of the
  measured request. An idle-admission retry stays inside the same stream, so a retry lengthens the stream. The
  cooldown is outside it.
- **Bundle.** The member's write-once directory of raw files, events and summary.

### 0.4 Phases and phase energy

- **Phase.** A named, timestamped part of the measured request. **Prefill**: the model reads the whole prompt and
  computes the first output token; it ends at the first streamed token. **Decode**: the model produces the remaining
  output tokens.
- **Phase energy.** Each power record contributes its power times the length of the overlap between its support and
  the phase (`reduce.py` `_integrate`). Records wholly inside count in full; a record that straddles a phase edge
  counts in proportion to its overlap; records outside count zero. No idle power is subtracted (**gross** energy).
  *Worked example (synthetic).* A phase runs from t = 10.00 s to t = 10.25 s. Record 1 covers 9.90–10.03 s at 20 W:
  overlap 0.03 s, 0.60 J. Record 2 covers 10.03–10.16 s at 30 W: overlap 0.13 s, 3.90 J. Record 3 covers
  10.16–10.29 s at 30 W: overlap 0.09 s, 2.70 J. Phase energy = 7.20 J.
- A phase needs at least 3 overlapping records or the reducer refuses it (`MIN_PHASE_SAMPLES = 3`). Each phase also
  carries a **precheck**: a per-phase list of pass/fail tests on its timing evidence (record count, record
  regularity, the clock bound of §0.14 against the phase length; full list in `joulewise/whole_window.py`
  `_METRIC_LOCAL_PRECHECK_REASONS`).

### 0.5 The two workloads

- **Decode workload.** Prompt 0 of `real_prompts_v1`, rendered through the Qwen3 chat template with thinking off: a
  42-token prompt (decode prompt manifest SHA-256 `31301c9df7e1f79c027d05a8b8e6022bf4d14e22b9c7f77ce8431b0ac3256694`).
  Output is forced to exactly 512 tokens (greedy, end-of-sequence suppressed). Prefill computes the first output
  token, so the decode phase spans the other 511 generation steps; the decode per-token value divides by all 512
  runtime-observed output tokens (D-179; analysis plan §4).
- **p42.** The prefill phase of the decode workload: 42 prompt tokens, a few tens of milliseconds, shorter than one
  power record. Block 3's comparably short phases failed their prechecks on all 24 members. The p42 cells are
  registered as **expected unresolvable**; their refusal blocks nothing.
- **Prefill workload.** A prompt of exactly L = 2048 tokens (token-ID hash
  `202e4913340b2bae39bf9a9d3a314f62bb5ff783fae483ad6a98507d071e1479`), 512 output tokens. Block 3 chose L as the
  shortest of 512/1024/2048/4096 at which every small-model probe member's prefill overlapped at least 5 records
  (`selection.json`, SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`).

### 0.6 Stages, settles and cooldowns

The values in this section follow the cold-judge ruling on block-5 per-member time of 2026-10-06
(`/Users/edr/night-archive/gate-prune/timing/RULING_fable_cooldown_2026-10-06.md`; its numbers are in
`judge/judge_checks.json` beside it).

- **Stage.** One ordered list of members that `scripts/run_campaign.py` runs together. Each stage starts with a
  60 s **settle**: the **chain** (the script that runs a window's stages in order, §0.17) sleeps so the machine
  returns to idle. The same 60 s settle precedes the pre calibration, so a window has eleven settles. The runbook's
  180 s (`docs/phase_2/window_runbook.md` `SETTLE_S=180`) still governs the older windows; the block-5 chain lists
  the difference among its deviations (`joulewise/b5/chain.py` `SETTLE_S`, `DEVIATIONS`). *Why 60 s:* processor
  power is back at idle within about 15 s of a decode ending (block 3's sentinel reading, 0.1 W at 9 s), each first
  member measures its own idle baseline, and the pre-calibration settle starts after a clean dwell of 633–1,477 s at
  the arm, so a longer wait has nothing left to recover from.
- **Cooldown.** Between members of a stage the runner reads the idle machine in 5 s readings: each reading is one
  short sampler capture (50 records requested, about 6.5 s of wall time) reduced to its mean processor power. It
  starts the next member at the first reading whose mean is at most twice the previous member's idle-baseline mean
  while the OS thermal state is nominal, or at the 300 s **cap**, whichever comes first. The first member of a stage
  has no previous member and no cooldown (`first_run_exempt`). A member whose cooldown reached the cap is recorded as
  `cooldown_cap_hit`. The policy file states the rule as `sustained_window_s` 5.0 (only the last 5 s of readings
  count, so one reading decides), `coverage_fraction` 0.8 (the readings must cover at least 4 of those 5 s),
  `tolerance_fraction` 1.0 (the bound is the previous baseline × (1 + 1.0)), `subwindow_s` 5.0, `cap_s` 300 and
  `require_thermal_nominal` true (`configs/campaign_policies/quiet_mac_p2_b5.json`, §0.13).
  *Worked example (synthetic).* The previous member's idle baseline averaged 0.037 W (block 3's median), so the
  bound is 0.074 W. The first reading averages 0.082 W: no start. The second averages 0.045 W with thermal state
  nominal: the next member starts, about 13 s after the cooldown began.
  *Why this rule, not block 3's.* Block 3 required 30 s of readings within 10% of the previous baseline. Its waits
  averaged 53.9 s over 26 cooldowns; the new rule would have averaged about 9.1 s. One wait, 114 s before w2
  member `g2a-small-p2048-r03` (readings of 0.822, 0.614 and 0.336 W after three readings of 0.034–0.064 W), was a
  background OS process (Apple Intelligence asset activity in the unified log), which then made that member's idle
  admission refuse it twice; the new rule would have started it at 8.6 s and admission would have refused it the
  same way. Over the 28 block-3 small members that had a cooldown, each member's gross energy minus its group mean
  did not move with the gap from the previous run's end (gaps 79–702 s; slope 0.003 J per 100 s, r = 0.027,
  residual SD 0.22 J on 60–125 J members). Neither rule measures temperature, so neither bears on heat carried from
  one 8B member to the next; that is measured by the reference members and the NEG-8 screen (§0.12) and by the
  diagnostic below.
- **Battery-temperature diagnostic** (recorded, never a refusal or an exclusion). At each cooldown release the
  runner reads the battery thermistor (`ioreg -rn AppleSmartBattery`, key `Temperature`, in hundredths of a degree
  Celsius; no privileges; outside the sampler stream) and writes it into the campaign manifest. At harvest, for each
  stage: the **rise** is the last reading minus the first, and the stage has a **plateau** when it has at least
  three readings and its last three lie within 0.5 K of each other (largest minus smallest ≤ 0.5 K). A stage whose
  rise exceeds 3 K with no plateau is flagged `thermal.stage_battery_rise`; a stage with a cooldown release whose
  temperature is missing or unreadable is flagged `thermal.battery_temperature_unmeasured`. A one-member stage has
  no cooldown and no reading. Both are DISCLOSE (§6.8) and are reported beside the window's NEG-8
  result. If the NEG-8 screen passes, the numbers stand and the kelvin figure sizes future gaps; if it fails, the
  window is already removed by `neg8.screen_failed`. *Worked example (synthetic).* Readings 30.1, 31.0, 31.9, 32.6,
  33.3 and 33.9 °C: rise 3.8 K; the last three span 1.3 K, so no plateau; the stage is flagged. The reading is
  taken by `scripts/run_campaign.py` (`_hazard_read_battery_temperature`, manifest key
  `battery_temperature_readings`) and judged by the harvest; both are at the frozen head `a434e363d`.

### 0.7 Packs, attempts, windows and the measurement block

- **Pack.** The frozen, hash-pinned set of stages, member configurations and plans for one window. Its **plan tree**
  (`plan_tree.json`) lists the stages in order (`stage_graph`), with each stage's inputs, command line and expected
  member count. Three packs exist, all with the duration-sized idle baseline of §0.3 (`idle_seconds` 57.6) and the
  block-5 policy of §0.13:
  **ALPHA** `configs/campaigns/d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA**
  `configs/campaigns/d117_floor_qwen3-8b_v5` (Qwen3-8B, 4-bit) and **GAMMA**
  `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models). Their plan-tree SHA-256s at the int5
  head `d3c107f2f`, after the NEG-8 lane added each reference stage's spare members (§0.12), are ALPHA
  `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a`, BETA
  `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` and GAMMA
  `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf` (`FILL[B5-FINAL-HASHES]`), computed by this
  author with `shasum -a 256` and equal to the `plan_tree.sha256` values the sizing output records (§5.5). Earlier
  values: at the frozen head `a434e363d`, ALPHA `5218c270…` and BETA `5bab773a…` (as the timing lane `f4cf9047` left
  them) and GAMMA `fb51b4aa…` (after lane L10 gave its interior references distinct run ids, branch
  `lane/2026-10-06-l10-gamma-refs`, commit `c6309e1a`; §2, "Before GAMMA-1 arms"); GAMMA `523864e2…` at the
  integration head `b9d02700a`, which did not carry L10; and `a0076ae7…`, `ebd8c160…` and `7cdf1891…` at the
  gate-prune integration head `f8164893`, before the timing lane. The values in force are those in the sealed
  inventory at H_claim (§11).
- **Attempt.** One arm-to-harvest occurrence of one pack, labelled `ALPHA-n`, `BETA-n` or `GAMMA-n`, n = 1, 2, …
- **Window.** The stretch of machine time an attempt occupies, from its scheduled start t0 (§0.17) to its chain's
  exit.
- **Measurement block.** A registered set of windows sealed under one registration. This file registers measurement
  block 5. Block 3 (2026-10-03/04) was the prefill-length probe; block 4, the planned qualification block, does not
  run (§3).

### 0.8 Quads, contrasts, units and strata

- **A/B/B/A quad.** Four consecutive members in the order A1, B1, B2, A2. (The code calls this a "block":
  `block_ids`, `paired_block_incomplete`. This file says **quad**, so that "block" means only a measurement block.)
  A and B are the quad's two **sides** (the code says "arms").
- **Why A/B/B/A.** A slow linear drift cancels inside a quad. *Worked example.* If every member reads δ more than the
  one before it, positions 0, 1, 2, 3 carry 0, δ, 2δ, 3δ of drift; side A (positions 0 and 3) averages 1.5δ and side
  B (positions 1 and 2) averages 1.5δ, so the A-versus-B difference gains 0. A curved drift does not cancel: with
  drift k² at positions k = 0…3, side A averages 4.5 and side B 2.5.
- **Null quad.** In ALPHA and BETA both sides are the *same* model and workload, so any A-versus-B difference can
  only come from the instrument and the machine.
- **Contrast.** In GAMMA, side A is Qwen3-1.7B and side B is Qwen3-8B on the same workload. A quad's difference is
  `d = (B1 + B2)/2 − (A1 + A2)/2`; the contrast is the mean of d over GAMMA's quads for one phase.
- **Absolute repeat.** One member run on its own (not in a quad); ten in a row per workload.
- **Unit.** A group of members the statistics treat as one independent draw: each absolute repeat is one unit, and
  each quad is one unit. A **stratum** is one kind of unit: the **repeat stratum** or the **quad stratum**. D-179
  fixes 20 units per reported cell: 10 repeats and 10 quads. Consecutive units share slow drifts (temperature,
  background load), so their independence is a **modelling assumption**, not a measured fact, and every reported
  interval carries that caveat.

### 0.9 Reported cells

A **reported cell** is one registered energy number per model and phase, computed from that model's 10 absolute
repeats and 10 null quads (50 members): three per floor pack, six in all
(`d117-reported-mean-ph-{decode,prefill-p42,prefill-p2048}-{qwen3-1p7b,qwen3-8b}`). Decode and p42 read the same 50
members (the decode stages); prefill-p2048 reads its own 50. The four **paper cells**, also called the **target
cells**, are decode and prefill-p2048 for each model; the two p42 cells are computed if they can be and never
printed. GAMMA's two contrasts are its target cells, each over 10 quads.

### 0.10 Floors

- **Detection floor.** The largest difference the instrument produces when nothing differs, estimated from a model's
  absolute repeats (the **absolute** form) or null quads (the **comparative** form); hence the smallest real
  difference it can resolve. A contrast whose estimate does not exceed its floor is reported as `not_resolvable`
  (formulas: analysis plan §5). A **mint** is the authenticated issuance of the aggregate floor artifact.
- **Attribution floor.** A different quantity: D-078's estimate, about 1 J, of how much phase energy can be
  misattributed because phase edges are timed only to within the sampler's timing error. It is printed beside each
  reported cell and never added into its interval. Its value and applicability to 25G83 are
  `FILL[ATTRIBUTION-FLOOR-BINDING]` (§14 Q5).

### 0.11 Pulse calibration, acceptance, ledger and bracket

- **Pulse calibration.** A capture in which the GPU is driven through 59 commanded on/off pulses. For each pulse the
  estimator fits the power records as a baseline plus a rectangle whose start and end may be delayed from the
  commanded times, and returns the interval of delays consistent with the records. The **fiducial bound** is the
  largest absolute end of those intervals over all pulses: the largest timing error between commanded and observed
  edges. With 59 pulses it is a 95/95 bound (1 − 0.95⁵⁹ ≥ 0.95).
- **Pre** and **post** calibrations enclose a window; together they are its **bracket**.
- **Acceptance.** The issued file that judges brackets:
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256
  `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`, derived from 24 captures. Its numbers: the **pre
  screen** 0.036462861644980 s (the largest fiducial bound among the 24; a pre capture above it stops the chain before
  any member); the **bracket screen** 0.014531 s (their range); the drift allowance max(observed |post − pre|,
  bracket screen) must not exceed 0.01550217418713139 s.
- **Ledger.** The append-only record of every calibration capture (`runs/calibration_observation_ledger.jsonl` in the
  measurement checkout). Its last entry is the **ledger tip**. The tip committed to the repository is the **ledger
  pin** (`configs/calibration/calibration_ledger_head.json`: sequence 402, head digest
  `3ce1676c530452df301e8f09d97905487b06b8ed8887d7c7a728a08fd5310c08`, block 3's final tip). The acceptance was derived
  from the ledger up to sequence 376, its **cutoff**; brackets are judged against that cutoff while the ledger grows.
- **Bracket session.** Before a window's pre calibration, the chain opens ("reserves") a session in the ledger naming
  the window's plan; the pre and post captures are recorded against it. The **bracket binding** is the file that ties
  the two captures to that session.

### 0.12 Reference members and the NEG-8 drift check

The rules of this section follow the cold ruling of 2026-10-07 on lost and contaminated references
(`/Users/edr/night-archive/gate-prune/neg8-council/RULING.md`), as the NEG-8 lane implemented it
(`lane/2026-10-07-neg8-survivors`, merged in the int5 head `d3c107f2f`). Where the code differs from the ruling's
wording, the text follows the code and says so.

- **Reference member.** A member of one fixed reference workload (Qwen2.5-1.5B, 1024-token prompt, 256 output
  tokens). Each window runs 12 at its start, the **NEG-8 corpus** (NEG-8 is an inherited label from the project's
  negative-control list; it is a name, not an abbreviation), then a **start triplet** (three reference members), one
  **midpoint reference**, and an **end triplet**. The midpoint reference runs at the boundary between the window's
  decode arm and its prefill arm, which is also its temporal midpoint: after science member 50 of 100 in ALPHA and
  BETA, after science member 40 of 80 in GAMMA. The start triplet, the midpoint reference and the end triplet are the
  window's three **reference stages**.
- **Spare members.** Each reference stage also lists **spares**: copies of the stage's first reference config, byte
  for byte except the run id, with the stage's role, run only by the retry below. There are three for each triplet
  (`neg8-window-start-spare-1` to `-3`, `neg8-window-end-spare-1` to `-3`) and one for the midpoint
  (`neg8-window-midpoint-spare-1`). They live in `configs/campaigns/window_reference_spares_v5/`: for each stage and
  each count k, a directory `<stage>_spares_<k>/` holds spares 1 to k and an order manifest listing exactly them.
  Each pack's plan tree pins every spare config and spare-set manifest by SHA-256 in the stage's `spare_retry` record
  (`joulewise/b5/reference_spares.py` writes and checks them).
- **Diagnostic interior reference (GAMMA only).** GAMMA also runs one reference in the middle of each arm, after
  science members 20 and 60. Each is the midpoint reference's config under its own run id
  (`gamma-interior-reference-decode-midpoint`, `gamma-interior-reference-prefill-midpoint`), with the role
  `window_interior_reference_diagnostic`. That role is not a NEG-8 role, so neither the NEG-8 screen nor the drift
  allowance below reads these two members; they are recorded as a measure of drift within each arm, and they have no
  spares. (The screen counts only members with the start, midpoint and end roles; "The screen on the survivors" below
  says how many of each it needs. A window with more than three start, more than one midpoint or more than three end
  references is a roster error and fails the screen.)
- **NEG-8 bound.** From the kept corpus members' gross energies (and separately their idle-subtracted energies), with
  n their count (10, 11 or 12; §5.3), s their sample standard deviation and t = t(0.975, n − 1). For an endpoint pair
  of n_s start references and n_e end references, let U_j be the mean of the corpus's j largest energies and L_j the
  mean of its j smallest. Then

      bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns), t × s × √(1/n_s + 1/n_e) ).

  The first term is the **envelope**: the widest gap that a start mean of n_s members and an end mean of n_e
  members could show if both were drawn from the corpus itself, so no screen statistic smaller than it is evidence
  of anything but repeatability. The second term is the 95% repeatability bound for a difference of two means of
  those sizes when nothing drifts (the corpus supplies the variance, so t keeps the corpus's n − 1 degrees of
  freedom). At the planned shape (3, 3) this is the former rule, max(U_3 − L_3, t × s × √(2/3)); at (1, 1) it is
  the legacy single-member bound max(U_1 − L_1, t × s × √2). At those two shapes the code reuses the terms stored in
  the bound artifact, so every bound minted before this rule replays to the same bytes; any other shape is computed
  from the artifact's corpus members (`whole_window.py` `build_neg8_drift_bound_artifact`,
  `neg8_family_endpoint_bound`, `neg8_count_adjusted_bound`, formula string `NEG8_COUNT_ADJUSTED_BOUND_FORMULA`).
- **NEG-8 screen.** The window passes when |mean of the end references that survive − mean of the start references
  that survive| ≤ bound(n_s, n_e), for both the gross and the idle-subtracted energies. A reference **survives** when
  it is not lost (the next item). The **whole-window drift allowance** is max(spread, bound(n_s, n_e)), where the
  spread is the largest minus the smallest of three values: the start mean, the midpoint reference's energy and the
  end mean (`whole_window.py`, `trajectory_excursion_max_j`); when the midpoint is lost, the spread is
  |end mean − start mean|. Each member carries half of the allowance (`E_whole_window_drift_allowance_j`), so a
  contrast carries it once in total. The allowance always uses the realised-count bound, on passing windows too, so a
  lost reference widens the uncertainty instead of hiding it.
- **Lost references.** A reference is **lost** when its bundle is absent, its summary status is not `succeeded`
  (which includes `member.admission_aborted` and `member.timeout`), it fails strict validation
  (`member.strict_validation_failed`), or any member-level physics exclusion of §6.4 fires on it
  (`contention.request_overlap`, `battery.member_span`, `battery.accumulator_excursion`, `thermal.os_level_nonzero`,
  `thermal.powermetrics_pressure_elevated`, `clock.step_overlap`). Two programs apply the test. The verdict writer
  drops a reference whose recorded status is not `succeeded` (`run_campaign.py` `_idle_admission_core_evaluation`);
  the harvest, which alone sees the monitor journals and runs strict validation, drops a reference that carries one
  of the flags above and re-runs the screen on what survives (`harvest.NEG8_REFERENCE_LOSS_CODES`, `_neg8_rescreen`,
  with `whole_window._derived_neg8_decision`'s `exclude_bundle_ids`). A lost reference's energy enters neither the
  screen nor the allowance, for either family. A reference whose physics is *unmeasured* (`contention.unmeasured`,
  `battery.unmeasured`, `clock.unmeasured`) is **kept**: unknown evidence never authorises an omission (the rule the
  mint applies to a corpus member, §5.3). The loss test never reads the reference's energy, so no reference can be
  dropped for its value. A lost reference's physics flags still apply to every science member and calibration they
  touch; losing the reference cures nothing else.
- **One retry, by spare slot.** When a reference stage ends with fewer succeeded members than it planned, the chain,
  before the next stage, counts the stage's members by their summary status alone and writes that count once to
  `neg8-spares-<stage id>.json` in the chain's transcript directory (a 300 s wall budget, §5.1). It then runs the
  spare set of size k = planned − succeeded (at most the stage's spares) once, into the stage's own runs root, after
  the ordinary 60 s settle and under the ordinary cooldown and admission procedure, provided the collection deadline
  allows 60 + 180 + 620 × k s (§5.1). The failed attempt's bundle is never moved, re-measured or replaced; both
  attempts stay in the roster, and the spare takes the slot's role (start, midpoint or end), so the screen reads it
  at that position. Each spare that left a bundle is flagged `member.retried` (DISCLOSE; observed: the stage, the
  slot, k, attempt 2). There is one retry per stage; a second loss at the same stage is evidence about the machine and
  is handled by the survivors rule. A retry is never run because a reference's energy is large, differs from its
  siblings or would fail the screen, and a loss found at harvest (contamination) is never repaired by a later
  reference. (`joulewise/b5/chain.py` `spare_retry_lines`, `SPARE_RETRY_HELPER`.) *Code differs from the ruling:*
  the ruling said "immediately"; the chain runs the spares after the ordinary 60 s settle that precedes every
  collection stage.
- **The screen on the survivors.** With n_s surviving start references and n_e surviving end references, the screen
  needs n_s ≥ 2 and n_e ≥ 2. With fewer at either endpoint, `neg8.screen_failed` removes the window with
  `observed.reason` `references_insufficient` and, in `observed.lost`, each lost reference's run id, slot and reason.
  Between two and three at each endpoint, the screen runs as above with bound(n_s, n_e). The midpoint is not required
  by the screen. The code names the shapes (`endpoint_protocol`): the planned (3, 1, 3) is
  `replicated_endpoints_with_midpoint`; any other shape with two or three references at each endpoint and zero or one
  at the midpoint is `replicated_endpoints`; more references than planned is `neg8_bracket_reference_invalid`.
- **A lost midpoint.** The window keeps its screen result, its allowance (computed as above with the two-value
  spread) and its numbers, and carries `neg8.midpoint_lost` (DISCLOSE). Because the midpoint is the only reference
  inside the window, its loss leaves any excursion that reverts by the end unmeasured, so the analysis plan (§2.4)
  lists `neg8.midpoint_lost` as a claim-excluding flag for the primary contrasts; the window still feeds descriptive
  numbers, sensitivity lines and the block's drift record. Once the block's midpoint record shows the midpoint never
  moved the spread beyond the bound, an erratum may downgrade the flag to disclose-only.
- **Disclosure.** A window whose screen ran on fewer than (3, 1, 3) references records `neg8.reference_lost`
  (DISCLOSE, window level). Its `observed` names each lost reference's run id, slot, reason, status and the outcome
  of its stage's retry (the spares measured and the spares that succeeded), the realised and planned counts, and the
  bound's formula; it also names the record that holds bound(n_s, n_e) and its two terms: the whole-window verdict,
  or `withheld/neg8-rescreen-bracket.json` when the harvest re-ran the screen. *Code differs from the ruling:* the
  flag itself carries no bound value, because a bound is computed from reference energies and flags are released
  as structure (§8). A loss that the retry restored (counts back at (3, 1, 3)) records no `neg8.reference_lost`; it
  is disclosed by the spare's `member.retried` and the lost member's own flag. `derived/neg8-screen.json` records the
  counts, the formula used and which bound was used.
- *Worked example (synthetic; recomputed by this author with the code's `neg8_count_adjusted_bound`).* Twelve corpus
  gross energies: 99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38 J;
  s = 0.2353 J, t(0.975, 11) = 2.201; U_3 = 100.3033, L_3 = 99.7100, U_2 = 100.3450, L_2 = 99.6650 J. Planned
  bound(3, 3) = max(0.5933, 2.201 × 0.2353 × √(2/3) = 0.4228) = 0.5933 J. Start triplet: r1 = 100.02 J, r2 aborted
  by idle admission (a failed bundle; corespotlightd at 0.54 CPU-s/s), r3 = 99.91 J. The chain runs one spare,
  `neg8-window-start-spare-1` = 99.95 J, flagged `member.retried`; start survivors [100.02, 99.91, 99.95], mean
  99.9600 J. Midpoint 100.20 J. End triplet [100.26, 100.19, 101.08] J; at harvest the third end member's request
  overlapped a contender (`contention.request_overlap`), so it is lost with no retry; end survivors
  [100.26, 100.19], mean 100.2250 J. Counts (3, 1, 2): bound(3, 2) = max(max(U_3 − L_2 = 0.6383, U_2 − L_3 =
  0.6350), 2.201 × 0.2353 × √(1/3 + 1/2) = 0.4727) = 0.6383 J. |100.2250 − 99.9600| = 0.2650 ≤ 0.6383: passes.
  Spread = max(99.96, 100.20, 100.225) − min(99.96, 100.20, 100.225) = 0.2650 J; allowance = max(0.2650, 0.6383) =
  0.6383 J; each member carries 0.3192 J. Had the contaminated end member been kept, the end mean would be
  100.5100 J, the screen statistic 0.5500 J (a near-failure caused by a contender, not by drift) and the spread
  0.5500 J. Had the midpoint also been lost, the spread would be |100.2250 − 99.9600| = 0.2650 J, the allowance
  unchanged at 0.6383 J, and the window would carry `neg8.midpoint_lost`. The idle-subtracted family subtracts one
  idle energy (here 36.00 J) from every corpus and reference energy, so its s, differences and decisions are the
  same. `neg8.reference_lost` names r2 (`member.admission_aborted`; its stage's spare
  `neg8-window-start-spare-1` measured and succeeded) and the third end member (`contention.request_overlap`; no
  spare, because the loss was found at harvest), counts (3, 1, 2), and `withheld/neg8-rescreen-bracket.json` as the
  record holding bound(3, 2) = 0.6383 J and its terms.
  *Second example (synthetic, every reference kept).* A bound of 0.40 J; start mean 20.10 J, end mean 20.35 J:
  0.25 ≤ 0.40 passes; with a midpoint reference of 19.90 J the spread is 20.35 − 19.90 = 0.45 J, so the allowance is
  0.45 J and each member carries 0.225 J. In GAMMA, a diagnostic interior reference of 19.70 J would change nothing:
  it is not one of the three values, so the spread stays 0.45 J.
- The NEG-8 screen reads reference-workload energies, never a science member's energy.

### 0.13 Idle admission

Before each member's request, its idle baseline must pass the block-5 policy
`configs/campaign_policies/quiet_mac_p2_b5.json`, SHA-256
`ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60`. It is the production policy
`configs/campaign_policies/quiet_mac_p2_production.json` (SHA-256
`b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`) with three cooldown fields changed (§0.6:
`sustained_window_s` 30 → 5, `tolerance_fraction` 0.1 → 1.0, `coverage_fraction` written out at its default 0.8)
and its `policy_id` set to `quiet-mac-p2-b5`. The admission tests below and the retry rule are byte-for-byte the
production policy's. The production file stays unchanged because the older packs and `scripts/run_campaign.py`'s
default still use it. The tests:

- an **environment guard**: AC power, external power connected, displays asleep, screensaver not running, Low Power
  Mode off, thermal state nominal;
- **CPU criteria**: over at least 30 CPU-telemetry samples, the 95th percentile of the CPU busy ratio (the fraction
  of time the cores were not idle) is at most 0.5, and the 95th percentile of processor power is at most 1.0 W.

A refused baseline is retried once, immediately, in the same sampler stream (`retry_attempts: 1`, no wait). A second
refusal aborts the member. In revision 2 an aborted member aborted the whole window; in revision 3 it removes only
that member's unit (§6.3).

### 0.14 The clock

- **The problem.** Each power record carries the sampler's own whole-second wall-clock label and an elapsed
  duration; phase edges are stamped on the machine's clocks. Placing records against phase edges needs the offset
  between the two time bases. An error of 5 ms in that placement moves at most 0.2 J per phase edge at 40 W, below
  the roughly 1 J attribution floor (§0.10); a larger error would move phase energy by more than the instrument can
  attribute.
- **Per-member anchor bound** (`joulewise/uncertainty_evidence.py`, unchanged). The method assumes wall time is
  affine in monotonic time over one sampler stream (one rate, no jump). Each record's endpoint, found by adding up
  the elapsed durations, must fall inside its whole-second label, widened by 250 µs; the set of (offset, rate) pairs
  that satisfies every record at once is computed exactly. Its half-width at the first record is **h**. The
  **effective bound** is h + the change in (wall − monotonic) over the stream + 2 µs of stamp resolution and
  padding. A member is **`bounded`** when its stream's summed record time is at least 60 s and its effective bound is
  at most 5 ms. This bound is authoritative for every member: not `bounded` removes the member (§6.3).
- **Clock anchor.** CLOCK_REALTIME (the wall clock) minus CLOCK_MONOTONIC_RAW (a hardware counter nothing adjusts),
  read in process. A step of the wall clock moves the anchor at once.
- **Frequency word f.** The kernel's stored rate correction for the wall clock, read without privileges by
  `ntp_adjtime` with `modes = 0` (`joulewise/kernel_clock.py`). With **network time** (automatic clock setting from a
  time server) OFF, nothing steps the clock, and the anchor drifts steadily at rate f. On 2026-10-05 f was
  −3.17 ppm, so the anchor moved about 0.27 s per day.
- **Residual.** The anchor's movement minus f × elapsed raw time. Steady drift leaves the residual flat; a step makes
  it jump.
- **Why f matters to the members.** The middle term of the effective bound grows with |f| × the stream's length. The
  longest stream any `_v5` member can have, **T_stream_max**, is 335 s: an 8B member with both idle-admission
  attempts, its warm-up, prefill, decode and guards (`configs/campaigns/v5_qualification_25g83/sizing_sources/
  sizing_source_v2.json`, SHA-256 `f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81`,
  `/derivations/stream_max`: max(15 + 265 + 10 + 2 + 5 + 17, 15 + 265 + 16 + 9 + 13 + 17, 240) = 335 s). The largest
  member half-width h in block 3 was 3.598 ms. The **frequency gate**, one of the checks run just before a window
  starts (the arm, §0.15 and §4.2), predicts the worst member's bound from these numbers before any member runs.

### 0.15 Hazards and the arm

- **Physical hazard.** A condition of the machine that would corrupt a measured energy if collection ran through it.
  Six are registered (§4.2): the clock stepping or drifting beyond budget; the machine off AC power or its battery
  charging (and, at the arm, any battery current while the machine is idle); OS thermal pressure; a competing process
  above 5% of one core; too little free disk for the window; the sampler not sampling at its cadence.
- **Hazard module.** Code (`joulewise/hazards/`, one module per hazard) that measures one physical quantity
  directly, keeps the raw bytes with their SHA-256, and returns **PASS**, **REFUSE** or **UNMEASURED** (the probe
  failed or timed out). A check that reads a proxy for a hazard (a settings string, a receipt, a setter's wording) is
  not a hazard module; doctrine requires measuring the quantity itself.
- **Arm.** The sequence the driver runs after t0 that decides whether this window's chain starts (§4.1). It returns
  **GO** only if no hazard verdict is REFUSE, the instrument's verdict is PASS, the agent census (§4.5) is clean, and
  the machine's OS build and model are ones the calibration acceptance has judged (§4.7). An UNMEASURED verdict
  refuses only for the instrument: a sampler that cannot start or sample is the hazard itself. For the other five
  hazards an UNMEASURED verdict is a failed probe, not a measured hazard, and the monitor measures each of them over
  every member span in the window (§0.17, §6.4); the driver records it in `hazards/arm.json` and as the disclosed
  flag `<module>.arm_unmeasured` (for example `contention.arm_unmeasured`) and the arm goes on (audit A3,
  `joulewise/hazards/arm.py`, `joulewise/b5/driver.py` `normalize_decision`). An arm that raised or timed out as a
  whole is still NULL, because the instrument is then unverified. Nothing else enters the decision. Which refusals the code may contain anywhere, at the arm or later, is fixed by
  one rule (physics or number integrity) that a test enforces (§6.11).

### 0.16 Flags, the catalog, exclusions and claim-usable

- **Flag.** One JSON line (schema `joulewise.flag.v1`) recording one fact: a **code** such as
  `battery.member_span`; a **scope** (window, stage, quad or member); a time interval on the machine's clocks; the
  observed and expected values; the evidence (path and SHA-256 of raw bytes); and a **blinding class**, STRUCTURE or
  RESTRICTED (RESTRICTED for anything computed from a science energy, §8). A flag never stops collection.
- **Flag catalog.** `flag_catalog.json` (schema `joulewise.flag_catalog.v1`), sealed with this file. It gives each
  code a family, a class (PHYSICS, NUMBER or REPRESENTATION, the classes of the gate inventory) and exactly one
  **effect**: **EXCLUDE_MEMBER** (the member is removed from every cell it feeds), **EXCLUDE_WINDOW** (the window is
  not claim-usable) or **DISCLOSE** (recorded and reported, removes nothing). The harvest looks effects up; it never
  decides them. A code the catalog does not list is **UNCLASSIFIED**: it blocks only the release event (§8) until it
  is classified blind (§7.2), and never blocks collection.
- **Exclusion function.** `joulewise/flags/exclusions.py` `compute(flags, roster, spans, catalog)`: a pure function
  from the flags, the planned roster of members and units, and the members' time spans to a document naming the
  excluded members, the kept units of each cell, and `claim_usable`. A member flag that names its member by bundle id
  instead of run id (the whole-window verdict names members by bundle id) is resolved through the roster's map from
  bundle id to run id; before that fix such an exclusion was silently dropped (Fable audit F9). It reads only each
  flag's code, scope, interval and id, never an energy, power or duration; its tests prove this by passing bundles whose energy fields raise when
  read. Identical inputs give byte-identical output.
- **Claim-usable.** A window is claim-usable when no EXCLUDE_WINDOW code fired and every target cell keeps at least
  8 of its 10 units in each stratum (§6.6).

### 0.17 Driver, chain, monitor and harvest

- **t0** is the planned start instant. The **launchd job**, the macOS scheduler entry installed for the window,
  starts the **driver** `scripts/run_night.py` at t0.
- **Window plan.** The per-attempt file written at the desk by `scripts/write_b5_window_plan.py` (receipt class
  `HAZARD_PACK`): plan id and attempt, the pack, the bracket session id, two freshly created runs roots (the
  **claim** root for science members and the **bound** root for NEG-8 and reference members), the thresholds of
  §4.3, the window's sizing (§5.5), and whether G10 runs at the tail (§3).
- **Chain.** The zsh script the driver launches; it runs the pack's stages in order and writes `night/chain.started`
  when it begins (§5.1).
- **Launch lineage.** A small file in each runs root, published by the driver before the chain starts, that ties
  every bundle to its plan, window and bracket session (`joulewise/window_lineage.py`, schema
  `joulewise.hazard_window_lineage.v1`). The measurement code reads it before writing a `_v5` bundle and refuses a
  member whose configuration bytes are not in the pack's committed inventory (§6.3). Just before launching the chain
  the driver reads each runs root's lineage back with the members' own reader (`_production_lineage_check`). Two
  findings refuse the window. (1) The machine has rebooted since the lineage was published
  (`night_refused_boot_changed`), because member stamps on the monotonic clocks of two different boots cannot be
  placed on one time axis. (2) The publication still fails after its one retry, 5 s later, because the pack's
  committed inventory is unusable (`night_refused_pack_inventory_unusable`, audit A5): no member's configuration bytes
  could then be checked against it, and every member would refuse itself. Everything else is recorded and the chain
  launches: a lineage file that is absent, unreadable, rejected by the members' reader, or naming another plan, window
  or bracket session is `records.lineage_prelaunch_mismatch` (DISCLOSE), and a publication that still fails after its
  retry for any other reason is `records.lineage_formality` (DISCLOSE). Both flags carry
  `observed.science_members_expected_to_refuse`: the runs roots whose lineage could not be read, where the members
  will refuse themselves. Members that cannot authenticate their lineage refuse themselves, and the yield counts
  (§5.7) show it.
- **Monitor.** `scripts/hazard_monitor.py`, a background process that runs from GO until the chain's processes are
  proven gone. It journals the clock anchor every 1 s and the frequency word every 5 s, the battery state (from the
  **registry**, the OS's record of the battery that `ioreg` prints) and the thermal level every 5 s, the battery
  current (from the **SMC**, the Mac's power-management controller; both sources are built in §4.2) every 1 s,
  per-process CPU every 10 s and free disk every 60 s, one append-only file per hazard. Every reading carries three
  timestamps (wall time, the controller's `time.monotonic_ns()`, and CLOCK_MONOTONIC_RAW), so readings join member
  spans exactly. The driver stops it no sooner than 5 s after the chain exits (`joulewise/b5/driver.py`
  `MONITOR_POST_CHAIN_HOLD_S` = 5.0, `hold_monitors_after_chain`), so that the 1 s battery reads cover the end of the
  post calibration (§6.5).
- **Meter.** `scripts/km003c_monitor.py`, a second background process, started and stopped with the monitor, that
  records the whole machine's DC input through an inline USB-C power meter (§5.8). It is a diagnostic: it never
  refuses, removes or enters a claim number. The driver runs it under its own supervisor (`MonitorSupervisor`, name
  `meter`), which restarts it after a crash but never after a clean exit, because the reader exits cleanly when no
  meter is attached.
- **Harvest.** `scripts/harvest_b5_window.py`, the desk program run after the chain exits. It archives the window,
  re-derives every number-protecting check from the preserved bytes, joins the monitor's journals to the member
  spans, writes every flag, and runs the exclusion function (§7.1).
- **Whole-window verdict.** One row, produced by the harvest with the production writer
  (`run_campaign.py --whole-window-verdict`), stating whether the window as a whole passed: every member admitted,
  the AC adapter's wattage unchanged, the CPU criteria held, the NEG-8 screen passed, and the bracket, read through
  its bracket binding, passed the acceptance (`joulewise/whole_window.py`). Its overall pass or fail removes nothing.
  Each of its parts acts through its own code: the NEG-8 screen and the bracket at window level, and each member's
  own failures at member level (§6.5).

### 0.18 Commits and the seal

- **H.** An exact git commit. **H_claim** is the commit whose code every block-5 window runs (§11).
- **Executed-file inventory.** At each arm the driver records the SHA-256 of every tracked file under `joulewise/`,
  `scripts/` and the window's pack, the chain bytes, the measurement checkout's HEAD and its `git status`. The harvest
  compares it with the sealed inventory (§11).
- **Pin-only commit.** A commit that changes only `configs/calibration/calibration_ledger_head.json`, the ledger pin,
  which is data. Such commits keep H_claim's code identity (§11).

### 0.19 The claims ladder

`docs/contracts/claims_ladder.md` fixes how strong a sentence may be. **L1** (instrument result): on this exact stack
(machine, OS build, runtime, model, quantization, sampler) and boundary (what energy the sampler covers, here
`M3 Max / MLX / powermetrics` SoC rails), this quantity was observed. **L2** (comparative result): one condition
differed from another within one boundary, with intervals reported, interleaved order, and the effect above the
detection floor. L3 and L4 (a fitted model checked on held-out cells; replication across machines) are out of reach.
**Holm** is the correction that keeps the chance of any false positive across the two contrasts at 5%.

## 1. Purpose, and what each window can support

Block 5 collects the three claim-bearing `_v5` windows. Their bytes are the only sources of the `_v5` numbers the
capstone paper can print: the reported phase energies (D-179), the detection floors (D-117/D-124), the dominance
ratios (D-165/D-168) and the two model contrasts (GAMMA's frozen prospective analysis manifest).

**Dominance ratios.** For each model, phase and floor form, R = (detection floor with each value free to move within
its timing uncertainty) ÷ (the same floor with every value at its point value) (analysis plan §6). R ≥ 2 means
timing uncertainty at least doubles the floor. The **contingent subtitle** is the "attribution-limited" paper
subtitle D-165 licenses only when every required ratio is at least 2.

| Window(s) | What it can support | Rung | Why not higher |
|---|---|---|---|
| ALPHA, its first claim-usable attempt | Reported phase energy of Qwen3-1.7B for decode and prefill-p2048, each with its interval, J/token, kept units and the attribution floor beside it; the 1.7B floor cells | L1 | One stack, one boundary, no comparison |
| BETA, the same | The same for Qwen3-8B | L1 | Same |
| ALPHA beside BETA | Side-by-side L1 cells only, labelled as collected in separate windows in a fixed order | L1 | Forced order stays below L2; the two models were never interleaved |
| GAMMA with the ALPHA and BETA floors | Two primary contrasts (8B minus 1.7B phase energy, decode and prefill-p2048), Holm family of two, plus the registered ratio and per-token difference (analysis plan §7.3) | L2 if and only if the claim gate's `claim_ready_for_l2_l3` is true (analysis plan §7.2) | No held-out cells, no second machine |
| Floors and GAMMA | Dominance ratios; the dominance sentence and the contingent subtitle only if every required ratio is at least 2 | Disclosure | D-165 addendum |

Every phase-energy sentence carries the D-177 limitation (phase attribution was not characterized by a measured
instrument check). Nothing here supports a prompt-population claim (one fixed decode prompt), a claim about prompt
lengths other than 2048, or a claim outside one measurement boundary. **Boundary label** (`BOUNDARY-LABEL`, filled
from committed bytes): `M3 Max / MLX / powermetrics SoC rails`, the claims ladder's form (§0.19). Every bundle records
the same boundary as `"boundary": "Apple SoC CPU + GPU + ANE package power"` with rails `cpu_power`, `gpu_power` and
`ane_power` (`joulewise/adapters/powermetrics.py`, `_base_device_metadata` and `RAIL_MANIFEST`). The identity pins
record it for each identity unit, that is, each model running one workload in one pack
(`stack_identity.measurement_boundary_label` in `identity_pins.json`, §4.6). The energy reported is therefore that
of the processor package rails, never wall power or the whole machine. The whole-machine meter of §5.8 measures a
wider boundary (the Mac's DC input); its numbers are a descriptive cross-check (analysis plan §8.2) and never a claim.

What the paper prints, and from which artifact, is fixed in analysis plan §9; printing anything needs the placement
ruling of §14 Q4.

## 2. Preconditions

Each is evidenced by a path and SHA-256 before the point named.

**Before ALPHA-1 arms:**

1. H_claim is fixed: the commit carrying PR #483 (the `_v5` qualification-code integration), lanes L1–L4, L7 and
   L8 of the gate-prune plan, the timing lane of 2026-10-06 (block-5 policy, idle records and settles; branch
   `lane/2026-10-06-timing-policy`), the core-prune lanes and gate-prune round 2 (integration head `b9d02700a`,
   branch `integrate/2026-10-06-gate-prune-3`), the P3 round (lanes `lane/2026-10-06-p3-{harv,haz,drv,wd}`) and
   lane L10, the two audit-fix lanes of 2026-10-07 and the NEG-8 survivors lane (revision 7 list), merged under the
   merge gates, with one consolidated Fable cold pass over the measurement code changed since `e6b6a0ce` (done at the
   frozen head `a434e363d`, `/Users/edr/night-archive/gate-prune/cold-pass/`) and a Fable delta cold pass over the
   measurement code changed from `a434e363d` to the final int5 head. `FILL[H-CLAIM]`. The candidate is the final head
   of `integrate/2026-10-07-int5`: `d3c107f2f` at this writing (`FILL[B5-FINAL-HASHES]`), which carries the frozen head
   `a434e363d96621318657418e60b8d14410079d82` (the refusal census and its triage, revision 6 list) and the three
   lanes of revision 7. It becomes H_claim only through the cold passes, the merge gates and the seal. If H_claim
   differs from the commit this text was synced to, the sync of item 8 is repeated on the difference.
2. The #416 pre-arm triple audit has run once at H_claim and every verified BLOCKER is cleared (§9.1).
   `FILL[416-AUDIT-RECORD]`.
3. This file, the analysis plan, the flag catalog and the sealed inventory are sealed (§12). `FILL[B5-SEAL-RECORD]`.
4. The three packs as the timing lane regenerated them, with GAMMA as lane L10 changed it and every reference stage
   carrying its spares (§0.7, §0.12), are at H_claim, and their files are in the sealed inventory. The spare configs
   and spare-set manifests, like the window references, sit outside the pack directories and are pinned by SHA-256 in
   each plan tree. Every window plan, and every plan-input file it is written from, uses
   the sealed threshold block of §4.3 (contention `clean_s` 180); any written before the seal is regenerated
   (`FILL[B5-PLANS-REGENERATED]`).
5. The measurement checkout (the dedicated clone a window runs from) is fast-forwarded to H_claim with its Python
   environment relocked, and the ledger seed (§4.6 item 6) is installed at its default ledger path.
6. A mock-runtime dry render of all three packs' chains through the `HAZARD_PACK` driver has passed (every expected
   bundle present, return code 0, only physical seams stubbed), and a desk dry arm with agents alive has refused at
   the census before any action. `FILL[B5-DRY-RENDER-RECORD]`, `FILL[B5-DRY-ARM-RECORD]`.
7. Before the seal, one machinery smoke of the block-5 cooldown policy has passed (timing ruling item 2): a
   dummy-label stage of three small members run under `quiet_mac_p2_b5.json` and harvested through the cooldown
   join, `campaign_cooldown_evidence` (the check that pairs each member with its cooldown record in the campaign
   manifest and verifies that record's raw trace). The ruling also named `scripts/check_window_provenance.py` (G3),
   but G3 does not apply to a floor pack: the harvest runs it only on a pack with an analysis manifest
   (`analysis_manifest_v3.json`, GAMMA's), and records `g3.not_applicable` (DISCLOSE) on ALPHA and BETA. So the smoke,
   an ALPHA stage, is judged on the cooldown join alone. It passes when every cooldown record verifies as `recovered`
   (or `first_run_exempt`) with a one-reading trace, and the join reports zero `campaign_cooldown_evidence_missing`
   and zero `cooldown_evidence_unverified`. It takes about 15 minutes. No thermal qualification run is required: the
   first BETA window measures 8B-after-8B carryover through its reference members (§0.12) and the
   battery-temperature diagnostic (§0.6).
   **`B5-COOLDOWN-SMOKE-RECORD`** (filled in revision 6; the record as written by the smoke's lead, with the four
   SHA-256s re-computed by this author from the files under `/Users/edr/night-archive/gate-prune/cooldown-smoke/
   run-4/`, where `night/` is `custody/night/` and `harvest.json` is `archive/harvest.json`): "Cooldown smoke run-4,
   2026-10-06 23:27–23:48 PDT, at head 3a9327e51c9d51ce5181f6db44983b6cf83a91df (integrate/2026-10-06-gate-prune-4;
   H_claim clone 3e2f67fb6). Plan REH-cdsmoke-alpha-20261007T0627Z, ALPHA pack, one stage of three small members
   (01_phase_decode_absolute r01–r03) under quiet_mac_p2_b5.json; other stages zero members. Rehearsal overrides:
   agent census (R1) and display (R4) only, arm dwell 60/120 s. Lineage published and verified without workaround;
   driver GO. Cooldown join (campaign_cooldown_evidence): r01 first_run_exempt, r02 recovered (waited 8.19 s), r03
   recovered (waited 8.20 s), all verified with one-reading traces; campaign_cooldown_evidence_missing 0,
   cooldown_evidence_unverified 0. PASS. Member r02 was refused by the real idle admission (CPU busy p95 0.634 and
   0.732 against 0.5; Spotlight indexing, corespotlightd 0.54 CPU-s/s), a physics refusal, not a cooldown fault.
   Evidence: night-archive/gate-prune/cooldown-smoke/run-4/cooldown-join-check.json sha256
   57ec28128a2915b2a0b73fb6a85d0f4f0fd4b9650791d6954fe5950d40a2be90; night/lineage.json sha256
   c35cb60a94333050cb2a0e8aa3a31aef79e09789f5bec15705947f7f5254faf4; night/result.json sha256
   b0863e43a4d0b90dc91fa7d92e5ef0943462c6f6227bf6ab483b67cd50a46619; harvest.json sha256
   b5015904eceddc640f28c4b088d77f8af455918d6bc882a11f4cba228a4482fa." The frozen head `a434e363d` carries the same
   driver code: between `3a9327e51` and `a434e363d` (`git diff --stat`, run by this author) only
   `joulewise/b5/harvest.py`, `joulewise/calibration_ledger.py`, `joulewise/controller.py` (the guard-collector and
   pack-root triage of §6.10), `joulewise/flags/catalog.py`, `joulewise/flags/core.py` and
   `configs/gates/hazard_refusals.json` changed under `joulewise/`, `scripts/` and `configs/`; the driver, the chain,
   the runner `scripts/run_campaign.py` and the cooldown join are byte-identical. From `a434e363d` to the int5 head
   `d3c107f2f` the driver, the chain and the runner did change (revision 7 list), but no added or removed line in
   `scripts/run_campaign.py`, `joulewise/controller.py` or `joulewise/b5/harvest.py` mentions the cooldown, and
   `configs/campaign_policies/` is unchanged (`git diff`, searched by this author), so the smoke's result carries
   over to that head.
8. The P3 sync points of §13 are each confirmed against the merged code, and this text is corrected where the code
   chose differently (a draft edit, before the seal). **`P3-SYNC-RECORD`** (filled in revision 6): confirmed against
   the frozen head `a434e363d`; the result of each sync point is the table in §13, and the catalog comparison there.
   Revision 7 repeats the sync for the code merged after `a434e363d` (the audit fixes and the NEG-8 lane), against
   the int5 head `d3c107f2f`, in a second table in §13 (`B5-REV7-SYNC`). Together they hold for H_claim only if
   H_claim is that head (item 1); otherwise the sync is repeated on the difference.

**Before ALPHA-1's harvest:** the harvest program (lane L5) has passed its Fable final pass and is pinned by an
addendum to the seal record (§11 item 4). Three requirements that revision 5 listed here are met at the frozen head
`a434e363d`:

- the harvest emits `member.whole_window_member_failure` for every member the whole-window verdict fails for one of
  the reasons of §6.3 (`harvest.whole_window_member_failures`), and `whole_window.member_failures_unreadable` when a
  verdict that did not pass cannot name its failed members (§6.5);
- the desk verdict's timeout is sized to the window: max(1,800 s, 90 s per claim-root bundle), with a 60 s
  heartbeat (`harvest.desk_verdict_timeout_s`; an ALPHA verdict needs about 3,700 s, and the old fixed 1,800 s would
  have lost it as `whole_window.verdict_absent`);
- the verdict writer never reads a stale ledger pin. *Forcing problem* (real-model rehearsal): the writer reads the
  calibration ledger through the committed pin, and the window's own post calibration has moved the ledger past the
  pin the window armed at, so a verdict written before the pin advance fails its bracket with
  `calibration_ledger_head_mismatch`, and its row stays in the append-only campaign log. *Mechanism:* the desk order
  is chain exit, then the pin advance, then the harvest (§4.6 item 6). Before starting the writer the harvest checks
  that the committed pin is this bracket session's terminal entry (`harvest._desk_pin_problem`); if it is not, it
  writes no verdict and records why (`whole_window.producer_failed`, `step` `head_pin`, with a reason such as
  `pin_behind`). The window then lacks a verdict (`whole_window.verdict_absent`, a harvest problem under §7.2); the
  cure is the advance and a re-harvest from the same bytes.

**Before GAMMA-1 arms:** GAMMA's three interior reference stages launch three distinct `run_id`s (lane L10, branch
`lane/2026-10-06-l10-gamma-refs`, commits `c6309e1a` and `7bfd7c2c`). Before L10 all three launched the same
one-member input, `window_references_v5/midpoint` (run id `neg8-window-midpoint`), and `run_campaign.py` skips a
`run_id` whose complete bundle already exists, so the second and third were never measured and the harvest removed
the window (`roster.duplicate_run_id`). Giving all three the midpoint role would instead fail the NEG-8 screen,
which accepts one midpoint (§0.12). So the arm boundary (stage `gamma-reference-arm-boundary`, after science member
40) keeps the shared midpoint reference and is GAMMA's one NEG-8 midpoint, and the two arm-midpoint stages run the
diagnostic interior references under `configs/campaigns/gamma_interior_references_v5/` (§0.12). GAMMA's plan tree
pins those two manifests and configs by SHA-256 as external inputs, as it pins the window references, and its
generator refuses if their bytes differ from the shared midpoint's in anything other than `run_id`. No science
config, calibration plan, analysis manifest or root order manifest changed; GAMMA still runs 80 science and 21
auxiliary members. Besides GAMMA's pack and the two new reference directories, the change touches only the retired
block-4 writer (`scripts/write_v5_qualification_plan.py`, which no block-5 window runs) and tests. L10 is merged in
the frozen head `a434e363d` (commit `7bfd7c2cf` is its ancestor), with the sizing output and identity pins re-derived
there (§4.6 item 3, §5.5), so its bytes are sealed directly with H_claim and no erratum is needed. Under §7.5 it
supersedes no completed ALPHA or BETA window, because neither executes GAMMA's files.

**Before the release event:** the analysis code (lane L9) is written blind, pinned by an addendum, and the blind dry
run of analysis plan §3.2 has completed.

**Deleted from revision 2, with the reason:**

- the block-4 verdicts and the L10-A ratification: block 4 does not run; ALPHA-1 carries its structural checks as
  disclosed diagnostics (§3);
- Q110 (the age of the readiness evidence): the readiness receipt no longer exists;
- A6 at H_claim (a launch-time recheck that the launched bytes are the reviewed bytes): replaced by the
  executed-file inventory and the model-identity check, both replayed at harvest (§6.5);
- V5-TRANSACTION-GO-01, the `CAMPAIGN_TRANSACTION` authorization records and the step-6 confirmation record: the
  receipt route they authorized (`TRANSACTION_PACK`: ARM, GO, `scripts/launch_window.py`) is retired for block 5
  (§11 item 3).

## 3. Block 4 folded into block 5

**G10, the clock positive control, at ALPHA-1's tail (agent-run).** Ed, 2026-10-05: "make it all agent run, don't
let old decisions stop progress on the paper. remember those are vestiges of weaker models, scaffolding i had to
build to corral weaker models working on this".

- *What it shows.* That the clock hazard's arm check can see a clock step at all. Without it, a clock module that
  always passed would look the same as a quiet clock.
- *When.* The driver runs `scripts/g10_clock_step_control.py` after the chain's process group is proven gone and
  before its terminal record, so no capture can be touched; the monitor and the meter stay supervised meanwhile (§5.4). The window plan of each attempt sets `g10: true` until a
  G10 record exists in this measurement block, and `false` after it. In practice this is ALPHA-1; if ALPHA-1 never
  starts its chain, or its chain is stopped by the agent census, the next attempt carries it.
- *Steps.* (1) Read f₀ and the anchor; check read-only that no capture process is alive (if one is, ON is skipped and
  the result is UNMEASURED). (2) `sudo -n systemsetup -setusingnetworktime on`; its output is recorded only.
  (3) Poll the anchor at 1 Hz for up to 300 s until the residual moves more than 5 ms. (4) Evaluate the clock
  module's own arm check (§4.2) on the before/after pair; a REFUSE whose measured residual exceeds 1 ms is
  **DISCHARGED**. (5) Keep network time ON while reading f each minute; switch OFF at the first read, at least 60 s
  after ON, at which the next arm's frequency gate (§4.2: 3.7 ms + (|f| + 0.25 ppm) × T_stream_max ≤ 5 ms) would pass,
  or 15 min after ON. (Revision 4's |f| ≤ 3.0 ppm target sat below this machine's own f of about −3.17 ppm, so it
  would always have run the full 15 min; each read still records whether |f| ≤ 3.0 ppm. PLAN2 item S7,
  `scripts/g10_clock_step_control.py` at `a434e363d`.) OFF always runs, including on an exception or a SIGTERM or
  SIGHUP. (6) Write `night/g10.json` write-once.
- *Why it should discharge.* With network time OFF the wall clock's offset from a time server was about 1.15 s on
  2026-10-05 and grows about 0.3–0.5 s per day (gate-prune plan §4), so turning network time ON one night later
  corrects roughly 1.3–1.8 s, far above 5 ms.
- *Effect.* G10's result is a disclosed diagnostic (`g10.discharged`, `g10.not_discharged`, `g10.unmeasured`,
  `g10.interrupted`, `g10.error`). It touches no ALPHA-1 number, because each member carries its own anchor bound. A
  result other than DISCHARGED goes to one consult before BETA arms.
- *Frequency redraw.* G10 leaves a new f. If the next arm's frequency gate refuses (§4.2), the desk redraws f before
  re-arming: network time ON; read f once a minute; OFF at the first read, at least 60 s after ON, at which the
  frequency gate passes, or after 15 min; re-read f 10 min later; up to three cycles, then a consult. This loop reads
  only the frequency word, never an energy.

**a1 and a2 (the arm-then-abort controls) retire.** Their two physical questions are answered without a window:
does a refusal before launch leave nothing launched and nothing changed (the driver's tests inject each hazard
REFUSE and compare the ledger, `~/Library/LaunchAgents`, the custody roots and the network-time state before and
after; the desk dry arm of §2 item 6), and does arming run end to end on native output (every real arm writes
`hazards/arm.json`). The watchdog's stand-down is recorded live at ALPHA-1's arm.

**Stand-down leads.** *Forcing problem:* the agent census at t0 (§4.5) refuses the window if any agent session is
alive, so every session must be gone by t0; but every second of agent-free idle before t0 is time the machine does
nothing, and the arm's own dwell measures contention after t0 anyway. The supervising watchdog (a scheduled job,
`scripts/magistrate_watchdog.py` at `a434e363d`, P2-WD, that starts and stops the agent sessions on this machine
around each window) therefore stops launching sessions and asks every agent
session to exit at t0 − 180 s, sends SIGTERM to any that remain at t0 − 90 s, and SIGKILL at t0 − 60 s (revision 4:
t0 − 8, −6 and −5 min, about 450 s of idle; now about 125 s). *Why these numbers:* real sessions took 20–31 s to
exit after the request (c1, c2 and the d117 magistrate events), so a request at t0 − 180 s leaves about 150 s of
margin, and the watchdog's 10 s poll gives 9 polls between request and SIGTERM and 3 between SIGTERM and SIGKILL. A
session that survives all three is refused by the t0 census, which stays the backstop.

**s1 (the one-quad qualification window) becomes ALPHA-1.** ALPHA-1 contains everything s1 had: pre calibration, the
NEG-8 corpus and bound, references, null quads and post calibration. s1's structural checks run at ALPHA-1's harvest
as disclosed diagnostics (`diagnostic.s1_structural`): strict validation, re-reduction and a deliberately incomplete
finalization; the p42 precheck counts; the longest and shortest stream sizes; stage timing outside members.

## 4. The arm: physical hazards, measured directly

### 4.1 Order

Everything below runs inside the launchd job after t0, so no person or agent session is present.

1. **Agent census** (§4.5).
2. **Instant reads:** battery, thermal, disk, and the clock's frequency gate; then the OS build and machine model
   against the acceptance's judged epochs (§4.7).
3. **Network time OFF, as an action** (§4.4).
4. **Record-only collectors:** the executed-file inventory, the model-identity check, and the checkout identity,
   each in a subprocess with a timeout. Their findings are flags (§6); they never change the arm decision.
5. **Instrument cadence probe:** about 40 s.
6. **Dwell:** 180 to 2700 s, during which contention and clock linearity are measured.
7. **Final reads** of battery, thermal and the frequency word, and the agent census again; then GO; then the monitor
   starts; then the chain launches.

The chain therefore starts about 4–47 min after t0: about 41 s of reads, collectors and cadence probe, then a dwell
of 180 s at the least and 2,700 s at the most (revision 4: 11–47 min, with a 600 s minimum dwell). A refusal at any
step ends the attempt as NULL (§7.1) with nothing launched. A refusal is a measured REFUSE, an UNMEASURED instrument,
an agent census that lists an agent process or cannot be read, or an OS build no acceptance judged. An UNMEASURED
clock, battery, thermal, contention or disk verdict is not a refusal: it is recorded under `unmeasured` in
`arm.json`, with its phase and reasons, and as `<module>.arm_unmeasured` (DISCLOSE), and the arm continues (§0.15).
A contention dwell in which every snapshot failed therefore runs to its 2,700 s cap and ends with
`contention.arm_unmeasured`, while a dwell that measured a contender still refuses. The arm writes
`<custody>/hazards/arm.json` write-once with every measurement, verdict and raw-byte digest.

### 4.2 The six hazards

**Clock.** *Forcing problem:* a clock step inside a member's stream breaks the anchor fit, and a large |f| makes
the longest streams exceed the 5 ms bound (§0.14).
- *Arm, all four must hold:* (i) the **frequency gate** 3.7 ms + (|f| + 0.25 ppm) × 335 s ≤ 5 ms, where 3.7 ms is
  block 3's largest half-width 3.6 ms plus a 0.1 ms placement margin and 0.25 ppm allows for the rate over a stream
  differing from the stored word (ruling 76 B.2, `docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md`);
  this holds for |f| ≤ 3.6306 ppm. *Worked example:* at
  f = −3.17 ppm the bound is 3.7 + 3.42 × 0.335 = 4.846 ms, PASS; at |f| = 3.7 ppm it is 3.7 + 3.95 × 0.335 =
  5.023 ms, REFUSE. (ii) Over the dwell, sampled at 1 Hz, the residual stays within ±1 ms of its start value.
  (iii) Each anchor read pair is taken within 1 ms. (iv) f is identical at dwell start, dwell end and GO; any change
  means something adjusted the clock.
- *In window:* the monitor journals the anchor at 1 Hz and f every 5 s. A residual move of more than 1 ms between
  consecutive samples is a `clock.step`; a change of f is `clock.frequency_changed`. Each anchor sample is three reads
  in a row, RAW, REALTIME, RAW; its **read skew** is the time between the two RAW reads. *Forcing problem:* in mock
  rehearsal round 3 a `ps` probe pre-empted the monitor between those reads, giving skews of 3.9–8.3 ms, and the
  residual computed from such a sample moved by more than 1 ms with no clock step, so the harvest recorded false
  `clock.step` and `clock.step_overlap` (finding R3-1). *Mechanism* (lane P3-HAZ, at `a434e363d`):
  **`P3-CLOCK-SKEW-BOUND`** (filled in revision 6) is a quarter of the step limit, 1 ms ÷ 4 = 250 µs
  (`joulewise/hazards/clock.py` `window_skew_max_ns`, `SKEW_DIVISOR_OF_STEP` = 4). The monitor takes the step limit
  from the window plan (`hazard_window.harvest_thresholds.clock_step_ns`, else `thresholds.clock.step_ns`), as the
  harvest does, so the two bounds stay equal if the limit is ever re-registered; a missing or unusable value keeps
  the module's 250 µs and never stops the monitor (cold pass N5, `joulewise/hazards/monitor.py` `build_config`). The
  monitor reads the anchor up to
  five times (`ANCHOR_TRIES` = 5) and keeps the first read whose skew is at most 250 µs; if all five exceed it, the
  sample has no anchor, its rejected reads are journaled, and the member join records `clock.unmeasured` (DISCLOSE,
  `observed.rule` `read_skew`). The harvest applies the same 250 µs bound to every journaled sample
  (`harvest._clock_point`): a sample above it is skipped, and the next good sample is compared with the last good one,
  so a step is never computed from a skewed sample. A real step moves every later sample, so a skipped sample cannot
  hide one. *Why a quarter:* the REALTIME read lies somewhere between the two RAW reads, so a skew of s can misplace
  one sample's residual by at most s; two consecutive samples misplaced in opposite directions by 250 µs each differ
  by 500 µs, still half the 1 ms that defines a step. (The arm's dwell samples are re-read the same way against the
  arm's own bound, `skew_max_ns` = 1 ms, rule iii above.)
- *Replaces:* the 8 ppm sizing convention of revision 2 and the network-time OFF receipt's wording check. There is
  no resync at the arm: the wall clock's absolute offset enters no energy, because the anchor fit and every phase
  edge use relative times.

**Battery** (directive #421; ruling of 2026-10-06, §9.2). *Forcing problem:* while the battery charges, the
battery heats and the machine draws more from the adapter than the work needs; with the adapter disconnected the
machine runs on battery under a different power policy. Either way the machine is not in the power state every
registered number assumes. A capture taken while charging was registered as confounded (`battery_float_confounded`;
decision log, amendment A-R5b of 2026-09-25). The rule is decided from instrument state alone, never from an
outcome.

- *Two sources.*
  - **State, from the registry.** `ioreg -r -c AppleSmartBattery` prints the OS's record of the battery; raw bytes
    are kept. It gives ExternalConnected (an adapter is supplying power), IsCharging, InstantAmperage (signed),
    Amperage, UpdateTime, Voltage and the `PowerTelemetryData` accumulators. The registry **publishes** a new set of
    values about once every 60 s (and on some events); between publications every value is frozen.
  - **Current, from the SMC.** The SMC (System Management Controller) is the chip that manages the Mac's power and
    exposes its sensor readings as four-letter **keys**, read in process without privileges
    (`joulewise/hazards/smc.py`). **B0AC** is the battery current in mA, signed, negative when the battery
    discharges into the machine; **B0AV** is the battery voltage in mV. The SMC refreshes them about once a second
    (largest gap 1.01 s over 580 s on 2026-10-06). Three more keys are recorded, not judged: PDTR (the DC input power
    from the adapter, W), PSTR (the system's total power, W) and PPBR (the SMC's own battery-power figure).
  - *Why the current comes from the SMC.* The registry's current is a snapshot, not an average. On 2026-10-06, at
    each of nine registry publications InstantAmperage equalled Amperage, and both equalled the last B0AC read before
    the publication (at one, −793 mA against a B0AC read of −727 mA taken 0.7 s earlier, within one SMC refresh), not
    the mean over the preceding interval. Between publications the registry misses discharge entirely: over the interval ending at
    UpdateTime 1791324894, B0AC read as low as −3,580 mA (mean −351 mA), and the registry published 0. A probe
    earlier that day saw −865 mA bursts during Qwen3-8B decode while every registry value read 0. So the registry
    now supplies only the state, and the SMC the current (`joulewise/hazards/battery.py`, and the harvest's own copy
    of the member rule, `harvest.battery_join`, at `a434e363d`).
  - *Validation of B0AC* (`/Users/edr/night-archive/wallmeter-probe/verify/b0ac_validation.md`, 2026-10-06 22:12Z).
    25 s idle, then 170 s of load (a 16-process CPU burner plus four Qwen3-8B generations; DC input peaked at
    135.7 W on the 140 W adapter, so the battery had to help), then 200 s of recovery. *Sign:* B0AC was negative
    exactly when PSTR exceeded PDTR, that is, when the machine drew more than the adapter supplied: at 126 of 536
    distinct SMC publications, all during the load; it read exactly 0 throughout the idle and the recovery.
    *Magnitude:* over the load, ∫ −B0AC × B0AV dt = 606.9 J against ∫ (PSTR − PDTR) dt = 595.4 J, 1.9% apart; on 20 s
    bins the slope of PSTR − PDTR on −B0AC × B0AV is 1.027 (r = 0.954). Single 1 s reads disagree (r = 0.32),
    because the SMC refreshes its keys out of phase with one another; time averages agree. *Charging direction:* not
    observed (the battery sat at its 80% charge limit). Positive B0AC is read as charging by the registry's
    convention: the archived charging capture shows InstantAmperage +1,716 mA with IsCharging Yes, and the registry
    current is B0AC's snapshot.
- *Arm:* ExternalConnected Yes; IsCharging No; |B0AC| ≤ 200 mA (|InstantAmperage| ≤ 200 mA when B0AC cannot be read,
  recorded as `battery.smc_unavailable`); the registry reading no older than 180 s. The arm runs on an idle machine,
  so battery current in either direction means the adapter is not supplying the machine, a real hazard; this refusal
  is unchanged by the ruling (§9.2).
- *In window:* the registry polled every 5 s, its raw bytes stored at every publication; the SMC read every 1 s.
  The member rule is §6.4: charging, loss of AC power and missing evidence remove the member; discharge with the
  adapter connected (**assist**) is disclosed.

**Thermal.** *Forcing problem:* under thermal pressure the processor throttles, which changes both power and
duration.
- *Measurement:* the OS thermal-pressure level, `notifyutil -g com.apple.system.thermalpressurelevel` (unprivileged,
  0 = nominal). `pmset -g therm` is recorded as a diagnostic only: on this Mac it prints only "No thermal warning
  level has been recorded", so a check built on it tests nothing.
- *Arm:* level 0. *In window:* level every 5 s; inside each member, powermetrics' own per-record thermal pressure.

**Contention.** *Forcing problem:* another process's CPU work during a request adds energy that would be attributed
to the model; idle admission screens only the idle baseline before the request. On 2026-09-22 a background indexer
(`fseventsd`) contaminated captures this way.
- *Measurement:* CPU-seconds per second of each process outside the measurement tree (the driver, the chain's
  process group, `sudo` and `powermetrics`, `caffeinate`, the monitor), computed from the difference of cumulative
  CPU time between two `ps` snapshots, not from the decaying `%CPU`. *Worked example:* a process whose cumulative
  CPU time goes from 12.40 s to 13.10 s across a 10 s interval used 0.07 CPU-s/s, above the 0.05 limit (5% of one
  core).
- *Arm (the dwell):* 30 s intervals; an interval is clean when no outside process exceeds 0.05 CPU-s/s. GO needs
  180 s (six intervals) of consecutive clean intervals; none within 2,700 s refuses. *Why 180 s, not revision 4's
  600 s* (PLAN2 finding t2-08; `joulewise/hazards/contention.py` `HAZARD_ARM_CLEAN_S` at `a434e363d`): no number
  depends on the dwell. Each member's idle admission screens its own baseline, the monitor checks contention every
  10 s through the window, and a persistent contender still fails the 0.05 limit in every interval and is refused at
  the cap. The dwell also carries the clock's linearity check, and 180 s still sees a step or a timed slew: a slew of
  500 ppm over 180 s moves the clock 90 ms, ninety times the 1 ms limit. Under revision 4 the dwell took 633–1,477 s;
  the change saves at least 420 s per window. (The legacy prewindow dwell, `prewindow.MIN_CLEAN_DWELL_S`, keeps its
  600 s; only the hazard arm changed.)
- *`kernel_task`.* An unprivileged `ps` never lists `kernel_task` (process id 0; checked 2026-10-05), so neither the
  dwell nor the window can judge it by name. Its work is inside the host's total busy time, which every interval
  journals (`host_busy_cpu_s_per_s`) and nothing judges: `aggregate_cpu_limit_s_per_s` is null (§4.3) until ALPHA-1's
  journal measures this Mac's idle total under a launchd job. (Revision 4 said the dwell included `kernel_task` and
  the window disclosed its share; neither could happen.)
- *In window:* every 10 s. The member rule is §6.4.

**Disk.** *Forcing problem:* a write failure mid-window loses bytes.
- *Measurement:* `statvfs` free bytes on the runs-root volume and each backup destination.
- *Arm:* on every volume, free ≥ planned bytes × the copies planned on that volume + 20 GiB. Planned bytes are
  182 MiB per member (block 3 measured) × (the window's members + the 7 spares its reference stages can add at most,
  §0.12; `joulewise/b5/plan.py`): 22.4 GiB for ALPHA and BETA (119 + 7 = 126 members), 19.2 GiB for GAMMA
  (101 + 7 = 108). The driver plans one copy in the claim runs root and one in each of the two backup destinations
  (§5.6); the bound runs root and the custody root need only the headroom (`joulewise/b5/driver.py`, disk targets).
  The harvest archive is an APFS clone (a copy that shares storage with its source until either is modified), so it
  adds no copy. Targets on one volume add their copies. The backup destinations are in iCloud Drive, whose local
  folder is on the same volume as the runs roots (one device number, read with `stat` on 2026-10-06). So three copies
  land on that volume: 3 × 22.39 + 20 = 87.2 GiB required for ALPHA and BETA, and 3 × 19.20 + 20 = 77.6 GiB for
  GAMMA, against 264 GiB free on 2026-10-05 (revision 6, before the spares: 83.5 and 73.9 GiB).
- *In window:* every 60 s; below 10 GiB the monitor journals `disk.low` and the driver stops the chain.

**Instrument.** *Forcing problem:* a sampler running slower than its cadence (as the launchd context did on
2026-09-19, at 244–250 ms per record) leaves phases without enough records.
- *Arm:* a 300-frame idle capture through the production adapter, inside the launchd job: exit 0, exactly 300
  frames within 55 s, median interval ≤ 150 ms, maximum ≤ 200 ms.
- *In window:* not polled; each member's own records are checked (§6.3), and the pre-calibration screen stops the
  chain before member 1 (§5.1).

### 4.3 Registered thresholds

The window plan copies this block verbatim into `hazard_window.thresholds`; the plan writer refuses a plan that
lacks a key a hazard module reads. The two **sized** keys (`disk.planned_bytes`, `clock.t_stream_max_s`) are replaced
by the window's own values (§5.5); the values shown are ALPHA's (`planned_bytes` = 126 × 182 MiB = 24,045,944,832
bytes, the window's 119 members plus its 7 spares, computed by this author; revision 6 showed 119 × 182 MiB).

```json
{
  "clock":      {"t_stream_max_s": 335, "h_ms": 3.7, "frequency_margin_ppm": 0.25, "limit_ms": 5.0,
                 "skew_max_ns": 1000000, "residual_max_ns": 1000000, "step_ns": 1000000},
  "battery":    {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120},
  "thermal":    {"max_level": 0, "max_gap_s": 15},
  "contention": {"cpu_limit_s_per_s": 0.05, "interval_s": 30, "clean_s": 180, "cap_s": 2700,
                 "window_interval_s": 10, "aggregate_cpu_limit_s_per_s": null},
  "disk":       {"planned_bytes": 24045944832, "headroom_bytes": 21474836480, "low_bytes": 10737418240},
  "instrument": {"frames": 300, "bound_s": 55.0, "median_ms_max": 150.0, "max_ms_max": 200.0}
}
```

`aggregate_cpu_limit_s_per_s: null` means the whole-machine CPU total is journaled at the dwell but not judged; only
the per-process limit decides.

`clean_s` is 180 in revision 5 (was 600). The hazard module's default is already 180 at `a434e363d`, but the arm
judges the value the window plan copied from this block (`joulewise/b5/driver.py` `_arm_thresholds`), and the plan
writer records any copied value that differs from a module default. So the change takes effect only in plans written
from this block after the seal: any window plan written earlier, and any plan-input file (the input from which the
plan writer copies this block) prepared earlier, carries 600 and must be regenerated (`FILL[B5-PLANS-REGENERATED]`,
§13).

### 4.4 Network time

- At every arm the driver runs `sudo -n systemsetup -setusingnetworktime off` as an action, whatever the current
  state, because running it removes the hazard. Its return code and output are recorded only (`network_time.off_output`,
  disclosed); nothing reads its wording. Whether the clock is in fact undisturbed is measured by the clock hazard
  (§4.2: the dwell residual and the f-equality checks).
- There is no settle wait after OFF and no ON at the arm. Network time is turned ON only by G10 at ALPHA-1's tail
  and by the desk frequency redraw (§3). Revision 2's "no ON at any point" is withdrawn.

### 4.5 Agent census

Kept by doctrine ("never start or continue a [QUIET-MAC] measurement while an agent session is active";
[QUIET-MAC] marks work run on the dedicated, quiet measurement Mac). The census probe
is `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'` (`joulewise/night_gate.py` `AGENT_CENSUS_ARGV`): it lists every
process whose command line contains one of the three strings anywhere. That list is a superset, so one matcher
(`joulewise/agent_identity.py`, used at every census site) decides each listed process by what the kernel says it
runs, never by its arguments. A listed process is an agent when its executable or process name starts with `claude`,
`codex`, `t3 code` or `t3code`, when its executable sits in a `claude/versions/<version>` or `codex/versions/<version>`
install, or when it is `node`, `bun` or `deno` running a script named `claude*` or `codex*`. A process in the
caller's own process tree (the driver or the arm and their descendants, or a process group led by one of them) is the
window itself and is ignored. A line is decided only when the live process's arguments, joined as `pgrep` joins
them, equal the listed text, which proves the line is that process and not a reused process id; a line that cannot be
decided stays a hit. Ignored lines are recorded with their process id, executable and reason. *Forcing problem*
(Opus audit F3): the window's own `python`, `zsh` and `run_campaign` processes carry paths such as
`…/b5-gamma-attempt3/custody`, which contains "t3", so the census refused the window for a string. The census is
clean when, after this matching, nothing remains (`pgrep` exit 1 with empty output, or every listed line ignored).
It runs first at the arm, again just before GO, and every 30 s in the window. At the arm, a census that lists an
agent process or cannot be read refuses. In the window, a census that lists an agent process stops the chain; the
window then has no post calibration, so it is not claim-usable (`calibration.no_bracket`). An in-window census that
cannot be read is `census.unmeasured` (DISCLOSE, with the count of consecutive unreadable censuses) and never stops
the chain (audit A3; the earlier stop after four consecutive unreadable censuses, `night_stopped_census_unmeasured`, PLAN2
row 7, is removed, and that code has no emitter). Seats exit before t0, and the watchdog fences the plan's span, so a stop
should not fire. Load average, process-name lists and the `corecaptured` spawn count, which revision 2 judged, are
recorded only.

### 4.6 Fixed inputs

1. **Machine:** §0.2; AC power, power mode `ac_high_power`, sampler interval 100 ms; driver standard input is
   `/dev/null`.
2. **Acceptance:** §0.11, ledger cutoff 376, one acceptance for all three windows. If a prospective re-derivation
   trigger of the acceptance fires during the block, no further window arms; the question goes to a cold gate.
3. **Models:** `mlx-community/Qwen3-1.7B-4bit` at revision `3b1b1768f8f8cf8351c712464f906e86c2b8269e` and
   `mlx-community/Qwen3-8B-4bit` at revision `545dc4251c05440727734bcd94334791f6ab0192`, with the tokenizer bytes the
   pack configs pin (panel `configs/model_panels/qwen3_4bit.json` at H_claim).
   **The identity pins are a file in this directory, not part of the plan trees.** Each pack's
   `identity_pin_projection` is `unprojected` and carries no pin. The pins are
   `configs/campaigns/v5_claim_25g83/identity_pins.json`, schema `joulewise.b5_identity_pins.v1`, sealed with this
   file (§12). An **identity unit** is one model running one workload in one pack. There are eight: `alpha` and
   `alpha/prefill_p2048` (ALPHA), `beta` and `beta/prefill_p2048` (BETA), and GAMMA's `A/decode`, `A/prefill_p2048`,
   `B/decode` and `B/prefill_p2048`. For each unit the file gives three digests:
   - the model artifact SHA-256 (Qwen3-1.7B `e1a4505d32a97bb080eac1d2046b6c99ef46f4483a4323484aaf9b4c546b7f4a`,
     Qwen3-8B `3e0fb77e7ce1ecb7ec844be3ef8856a23643e05317a55054a63d6af62252be31`);
   - the runtime identity SHA-256: the digest of the recorded stack (runtime and version, quantization, tokenizer,
     sampler and output policy, boundary), in the form the harvest recomputes from each bundle;
   - the configuration-set SHA-256: a digest over the scientific content of the unit's member configs.

   Once for the whole block, the file also gives the SHA-256 of the measurement interpreter's package versions,
   `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794`. That digest covers Python 3.13.1, mlx 0.31.2,
   mlx-lm 0.31.3, mlx-metal 0.31.2, numpy 2.5.1, safetensors 0.8.0, tokenizers 0.22.2 and transformers 5.12.1.
   `scripts/write_b5_identity_pins.py` generated the file from the packs' identity units and 24 block-3 reference
   bundles of the same two models, without loading a model. Its draft SHA-256 at the int5 head `d3c107f2f` is
   `f78a27f8c8c921e9b3de3403d6b56ea9da4cee92c23520e8ca24c666ecd95257` (`FILL[B5-FINAL-HASHES]`; computed by this
   author with `shasum -a 256`, and `scripts/write_b5_identity_pins.py --check` reproduced the file at that commit).
   The NEG-8 lane changed only the three packs' plan-tree digests in it (`git diff a434e363d d3c107f2f`). Earlier
   drafts: `ccce59f9…` at the frozen head `a434e363d`, after lane L10 (`c6309e1a`); `9c2ecd89…` after the timing
   lane `f4cf9047` and at the integration head `b9d02700a`; `039d3e3c…` at `f8164893`. Each change moved only the
   packs' plan-tree and config-inventory digests (L10's only GAMMA's plan-tree digest), never the model or runtime
   pins. The seal binds the bytes at H_claim.
   Two programs compare against these pins. At the arm, the driver passes the file to the model-identity collector
   (`--identity-pins`) when the measurement checkout holds it. At harvest, the harvest reads its archived copy. If
   either finds no pin to compare against, it records `model.identity_unpinned`, which removes the window (§6.5).
4. **Packs:** the three packs at H_claim (§0.7), with the pin bundle of the packs: prompt pin
   `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`, selection
   `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`, ladder
   `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
5. **Policy:** §0.13, `configs/campaign_policies/quiet_mac_p2_b5.json`,
   `ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60`.
6. **Ledger seed:** block 3's ledger at pin 402 (§0.11), installed at the measurement checkout's default ledger path,
   `<checkout>/runs/calibration_observation_ledger.jsonl`, because the controller's pre-calibration route reads that
   path; the plan writer refuses at the desk if the plan names another. Before each arm the desk runs the read-only
   ledger readiness check; a session left open by an abandoned attempt is closed with the existing abort plus a pin
   advance. For each later attempt the seed is the previous attempt's terminal ledger, whose tip the pin advance
   names. A pin advance is a pin-only commit made in the measurement checkout (H_claim plus pin-only commits, §0.18,
   §11), not a merged pull request: the merge path took 15–60 min per window for a one-file data change (PLAN2 X4).
   **The desk order is chain exit, pin advance, harvest, next arm** (`scripts/advance_b5_ledger_pin.py` at
   `a434e363d`; revision 5 had the advance after the harvest, which the code no longer allows). *Why this order:* the
   window's own post calibration finalizes its bracket session and moves the ledger past the pin the window armed at.
   The desk verdict writer and the next window's bracket reservation both read the ledger through the committed pin,
   so both refuse until the pin names this session's terminal entry (§2, "Before ALPHA-1's harvest"; the plan writer
   refuses the next plan at the desk for the same reason). The advance reads the session's terminal entry from the
   ledger, advances the pin through the guarded `advance-head-pin` path of `scripts/recover_calibration_ledger.py`,
   and makes a pin-only commit that it checks changes that one path alone. A window stopped before its post
   calibration leaves its session open: the desk aborts the session first, and the abort is then the terminal entry.
   The harvest still reads the live ledger and records how the committed pin relates to the window's terminal entry
   (`pin_relation`; `equal` when harvested in this order).

A change to any item after the seal needs a prospective cold erratum before the next arm (§10).

### 4.7 The one identity refusal at the arm: an OS build no acceptance judged

*What it checks* (core-prune row ARM-OS; `joulewise/hazards/arm.py` `identity_read`, `joulewise/b5/driver.py`
`_production_arm`, at `a434e363d`). Right after the instant reads, the arm reads `kern.osversion` (the OS build, for
example 25G83) and `hw.model` (Mac15,9) with `sysctl`, and compares the pair with the **judged epochs** of the
calibration acceptance: the (OS build, machine model) pairs the acceptance's captures were taken on, with any
continuation the ledger authenticates. A pair the acceptance never judged refuses the window (`refused_at:
"identity"`), before network time is touched. A read that fails is recorded and never refuses; if the judged epochs
cannot be loaded, the check is skipped.

*Why a refusal that is not a physical hazard.* Every timing bound in a window rests on the calibration acceptance
(§0.11), which was derived on one OS build. After an OS update the sampler, the scheduler and the timing estimator's
inputs may all differ, and the acceptance says nothing about them. The pre-calibration writer already refuses such a
window at the pre slot (its kept epoch check, `scripts/validate_powermetrics_fiducial.py`), after the whole dwell. This
check adds no new refusal outcome: it moves that same refusal before the dwell, reading the same judged epochs.
*Dissent recorded:* the Sol consult seat (core-prune DESIGN §7, R7) would record the identity at the arm and leave
the refusal to the writer, because doctrine lets only physics refuse. The orchestrator kept it: it changes when a
refusal happens, not whether. *Worked example (synthetic):* macOS updates overnight to build 25H12; the next arm reads
("25H12", "Mac15,9"), finds it among no judged epoch, and refuses in about a minute instead of after a dwell of
3–45 min and a pre calibration.

## 5. Window shape and sizing

### 5.1 The chain

The chain runs its pack's stage graph in block 3's order: the bracket reservation; a 60 s settle; the pre
calibration and its screen; the NEG-8 corpus and the bound derivation; the start triplet; the science stages with
the pack's interior references in their places (the midpoint reference in every pack; in GAMMA also the two
diagnostic interior references, §0.12); the end triplet; the post calibration and a record of the bracket
session's status. Each of the three reference stages (start triplet, midpoint, end triplet) is followed by its
spare-slot retry decision, which runs spares only when the stage lost members (§0.12). Every collection stage starts with its own 60 s settle (§0.6; block 3 used 180 s).

- **The only stops**, all before member 1 (about 13 min into the chain): a failed reservation (chain exit 10), a
  failed pre calibration capture (exit 11), and a pre fiducial bound above the pre screen 0.036462861644980 s
  (`instrument.precal_screen_failed`, exit 12). The driver records such a window as CHAIN_STOPPED, not GO (§5.7).
  Outside the chain, the driver stops it on `disk.low`, on a census that lists an agent process (§4.5; an unreadable
  census never stops it), when the monitor has written no
  battery or contention reading for about 10 min (`monitor.outage`, PLAN2 row 11), and at the window deadline
  (§5.5).
- Every other stage records its return code and the chain continues. A chain that reaches its end exits 0 whatever
  its stages returned; the flags, not the return code, decide claim use.
- **Operator countdowns: 0 s, except 20 s at the post calibration** (registered deviation 5, §10; P2-CHAIN,
  `joulewise/b5/chain.py` `COLLECTION_ARM_COUNTDOWN_S`, `CALIBRATION_ARM_COUNTDOWN_S`). Each pack stage passes
  `--arm-countdown-s 20`, a pause written for an operator to step away from the machine before collection. A window
  runs headless, and every collection stage and the pre calibration already follow a 60 s settle, so the pause waits
  for nothing: the chain passes 0 on the ten collection stages and the pre slot, saving 11 × 20 = 220 s per window.
  The post calibration keeps 20 s because no settle precedes it: it follows the last end-triplet member directly.
- **The window calibration verdict, computed once** (P2-CHAIN and P2-CTL, interface J1). *Forcing problem:* the
  timing estimator's fit of the pre calibration (the **refit**: re-running the pulse fit on the stored 90 MB raw
  capture) is a constant of the window, because its inputs are the same bytes for every member. Yet each member
  recomputed it three times, about 13.5–15 s each: in the child before the run, in the child's reduction, and in the
  parent's strict validation, 357 times per ALPHA window. *Mechanism:* right after the pre-calibration screen the
  chain runs the refit once (`scripts/b5_window_calibration_verdict.py`) and writes the create-once file
  `<claim runs root>/instrument_validation/window_calibration_verdict.json`, holding the SHA-256s of the calibration
  evidence, its manifest, the raw capture, its events and the estimator's code files, and the effective fiducial
  bound. A member uses it only when every digest equals that of its own installed copy and the bound is finite and at
  least the stored bound; otherwise it refits as before and records `calibration.refit_cache_miss` (DISCLOSE). It
  never refuses. The harvest never reads this file: it refits from the raw bytes itself. Saving: 1,654 s before the
  runs and 1,642 s in the reductions per ALPHA window (PLAN2 M1, M2), about 0.92 h.
- **Wall budgets on non-member stages** (PLAN2 row 8, `STAGE_WALL_BUDGET_S`): bracket reservation 900 s, pre
  calibration capture 1,800 s, window calibration verdict 600 s, the corpus-retry decision 300 s, each spare-retry
  decision 300 s (`neg8_spare_retry_decision`), the collected-corpus
  copy 1,800 s, the bound derivation 1,800 s, the session-status record 600 s, each chain flag record 120 s. On
  expiry the stage's process tree gets SIGTERM, then SIGKILL 30 s later, and the stage records return code 124; the
  chain continues as after any failure of that stage. The post calibration capture has no budget: it must be allowed
  to finish, or the window loses its bracket.
- **The collection deadline** (PLAN2 row 17; `chain.py` `CALIBRATION_HORIZON_S`, `HORIZON_*`). *Forcing problem:* a
  bracket is fresh for 24 h from the pre calibration capture, and the window's deadline (§5.5, 28.4 h for ALPHA) is
  longer. A chain that overran past 24 h would lose its bracket, and with it the whole window, not just a tail. The
  deadline cannot simply be lowered: it is the driver's kill time, and a kill loses the post calibration.
  *Mechanism:* a collection stage, the corpus retry, a spare retry and the bound derivation launch only when now +
  the stage's
  allowance ≤ pre-capture start + 86,400 s − 1,430 s. The 1,430 s reserve is a 60 s settle, the 770 s calibration
  pair allowance and 600 s of margin. A collection stage's allowance is 60 s settle + 180 s stage overhead + its
  members × 620 s (at least block 4's largest member allowance, 619 s); a spare retry's is 60 + 180 + k × 620 s for k
  spares. Once one stage is refused (return code 75),
  every later stage is skipped, the chain goes to the post capture, and `roster.horizon_truncated` (DISCLOSE) is
  recorded once; the units lost are then judged by the cell minimum like any other loss. *Worked example:* a
  20-member stage needs 60 + 180 + 20 × 620 = 12,640 s, so it launches only if it starts within 84,970 − 12,640 =
  72,330 s (20.1 h) of the pre capture. A normal ALPHA chain reaches its last stage 5–9 h after the pre capture
  (§5.5), so this fires only on a chain running more than twice its slowest expected length.
- **One retry of the NEG-8 corpus** (PLAN2 row 13; `chain.py` `NEG8_RETRY_MINIMUM`). *Forcing problem:* a corpus
  with fewer than 10 succeeded members cannot give a bound, so the window is lost about 1 h into the chain while the
  chain runs about 7 h more. *Mechanism:* when fewer than 10 of the 12 corpus members succeeded, the corpus stage runs
  once more into the same bound root, inside the collection deadline. The campaign runner skips a member whose bundle
  succeeded, refuses (never re-measures, never replaces) a member whose bundle exists and failed, and measures a
  member that has no bundle. So the retry recovers exactly the members refused before their bundle existed (a
  blocked cooldown, a lineage read failure), never a member that was measured and failed. Each member it measures is
  recorded `member.retried` (DISCLOSE). There is no drain (no early jump to the end references): a window whose corpus
  still has fewer than 10 is removed by `neg8.bound_not_derived` and collects the rest as data. *Worked example:*
  members 4, 5 and 6 are refused before their bundles exist and member 9 is aborted by idle admission (a failed
  bundle), so 8 of 12 succeeded. The retry measures 4, 5 and 6, each flagged `member.retried`, and leaves 9 alone. If
  all three succeed, 11 have succeeded and the bound is derived from those 11 (§5.3). The reference stages have
  their own retry instead, one spare-slot retry per reference stage (§0.12): because the runner never re-measures a
  failed bundle, the reference retry runs pre-registered spares under their own run ids, which also recovers a
  reference that was measured and failed.
- The bracket binding and the whole-window verdict are not chain stages. The harvest produces them at the desk with
  the production writers (`prepare_desk_verdict`). The backups are not chain stages either: they are a desk step after
  the harvest (§5.6).

### 5.2 A failed member costs only itself, and only up to 30 minutes

Every science and auxiliary stage in the committed packs passes `--max-failures 1`, so one admission abort today
drops the rest of a 20-member stage. The chain writer passes `--max-failures <the stage's expected member count>`
instead. This is a **registered deviation** from the pack bytes (§10). The plan trees' `attempt_policy`
(`abort_window_on_any_required_member_failure` in ALPHA and BETA, `abort_window_and_demote_to_non_claim_bearing` in
GAMMA) is read only by the retired freeze author (`arm_readiness_evidence.py`); it is superseded by the flag catalog
and disclosed, not regenerated.

**The member cap** (PLAN2 row 8; `scripts/run_campaign.py` `HAZARD_MEMBER_CAP_S` at `a434e363d`). *Forcing problem:*
no member had a wall-clock limit. A hung member held the chain until the window deadline, whose kill then lost the
post calibration and so the whole window, plus about 15 h of machine time; on 2026-09-16 a blocked file open held a
driver for 11 h. *Mechanism:* a member's child process gets 1,800 s. On expiry it gets SIGTERM, then SIGKILL 30 s
later, to its whole process tree; the runner proves no sampler process of that member is left, writes a `timeout`
row, records `member.timeout` (EXCLUDE_MEMBER) and goes on to the next member. After 2 consecutive timed-out members
the stage drains: only end references still run, then the post calibration. *Why 1,800 s:* the longest member the
sizing allows is an 8B member with both admission attempts and the cooldown at its cap, 619 s, plus 77 s of
bookkeeping; block 3's longest member cycle was 274.9 s. 1,800 s is 2.6 times the first, so it cuts only a member
that is not progressing.

**Strict validation moves to the harvest** (PLAN2 M3; P2-RC). In revision 4 the runner strictly validated each bundle
right after it was written: a fresh reduction including a third refit, about 28–30 s per member, all of which the
harvest repeats. Now the runner checks each bundle's structure only (files present and hashed, the config binding,
the prompt hash, the custody identity) and records `strict_validation: "deferred_to_harvest"`; the harvest runs the
full strict validation on every bundle, and a failure is `member.strict_validation_failed` (EXCLUDE_MEMBER) as
before. The runner's stage-end verdict row is labelled provisional, and its idle-admission summary
`deferred_to_desk`: nothing in block 5 reads it. Saving: about 3,475 s plus 655 s per ALPHA window.

### 5.3 The NEG-8 corpus may lose up to two members, for validity or for physics

A corpus member aborted by idle admission no longer aborts the window. **Registered rule:** the bound is derived
from the corpus members that were collected and succeeded, provided there are at least 10 of the 12
(`whole_window.NEG8_DRIFT_MINIMUM_N` = 10); t uses n − 1 degrees of freedom. With fewer than 10,
`neg8.bound_not_derived` removes the window.

*Why it matters.* At 1 abort in 37 members (the block 2 and 3 record), the chance that all 12 corpus members succeed
is (36/37)¹² ≈ 0.72. A rule that needed all 12 would lose about 28% of windows to the corpus alone.

*Implementation at `f8164893` (fix lane fx-harvest), with the protected core unchanged.* Three programs touch the
bound, in this order:

1. **The chain** derives the bound from a window-local copy of the corpus manifest that lists only the collected
   members that succeeded. It records that copy's path and SHA-256 in the driver's terminal record
   (`night/hazard_result.json`, `neg8_corpus.collected_manifest`).
2. **The production verdict writer**, which the harvest runs, reads the bound through the core's reader
   (`whole_window.load_neg8_drift_bound_artifact`, protected). That reader authenticates a bound only against the
   committed 12-member manifest. It therefore treats a 10- or 11-member bound as absent, and the stored NEG-8 screen
   fails with exactly two conditions, `neg8_drift_bound_underived` and its idle-subtracted twin.
3. **The harvest** decides both questions itself:
   - *Was the bound derived?* (`neg8_bound`) If the core reader accepts the bound, yes. Otherwise the harvest reads
     the custodied collected manifest and requires all of the following: its bytes hash to the recorded SHA-256; its
     header equals the committed manifest's; its members are committed members, each once, in committed order; there
     are at least 10 of them; and every member it leaves out did not succeed (a succeeded member left out would be a
     selected corpus). Then `whole_window.validate_neg8_drift_bound_artifact` checks the bound's arithmetic and corpus
     identity against those bytes. If both checks pass, the bound counts as derived from the collected subset.
     Otherwise `neg8.bound_not_derived` removes the window.
   - *Did the screen pass?* The harvest re-screens the window (`_neg8_rescreen`) in three cases: (a) the stored
     screen's only NEG-8 conditions are the two bound-underived ones and the bound was derived from the collected
     subset; (b) a reference the verdict names carries a loss flag that the stored bracket did not drop (§0.12, "Lost
     references"); (c) a corpus member was dropped for physics and the bound re-derived (below). It re-derives the
     NEG-8 bracket with the core's own evaluator (`whole_window._derived_neg8_decision`), over the reference bundles
     the verdict names, with the window's own validated bound (the physics-clean bound if there is one, else the
     collected-subset bound, else, in case (b) only, the stored bracket's), and with the bound's freshness judged at
     the verdict's completion time. Re-derived first without the harvest's losses, the bracket must have the stored
     bracket's endpoints and estimand; if it does not, these are not the bundles the verdict was written from, and
     nothing is evaluated. The decision is then the re-derivation that drops the lost references before aggregation.
     The re-screen alone decides: `neg8.screen_failed` is emitted unless the re-screen ran, passed and listed no
     condition. In case (a), any other NEG-8 condition leaves the screen failed; in every case, a re-screen that
     cannot run leaves it failed. The screen runs after the monitor joins (harvest steps `neg8_corpus_physics`, then
     `neg8_screen`), because the physics flags it reads come from them.

Structure (decisions, conditions, member counts, digests) goes to `derived/neg8-bound.json` and
`derived/neg8-screen.json`. The re-derived bracket holds reference-workload energies, so it goes to restricted custody
(`withheld/neg8-rescreen-bracket.json`). The stored verdict of such a window still reads "failed", which is
`whole_window.not_passed`, disclosed only (§6.5).

**Which corpus members the mint may leave out: one closed list.** *Forcing problem:* the bound may rest on 10 or 11
members, so something must decide which succeeded members are left out, and a loose rule would let a corpus be
*selected* (an inconvenient but valid member dropped). The NEG-8 mint (`whole_window.py`, at `a434e363d`) gives each
corpus member one of three verdicts:

- **keep:** it passes every per-member test the mint applies;
- **omit:** it fails a registered member-validity test that would also remove a science member. The reasons are a
  closed set, `whole_window.NEG8_MINT_DROP_REASONS`: `status_not_succeeded`, `not_current_strict_mint` (its summary
  was not produced by the current reducer from real, non-mock sampler records, so it cannot bear a strict claim),
  `custody_triangle_disagrees` (the three records that name the bundle's sampler, its config, metadata and summary,
  disagree about which sampler produced it),
  `precheck_ineligible` (the fresh re-reduction's gross or idle-subtracted precheck is not eligible) and
  `reduction_mismatch` (the fresh re-reduction differs from the stored summary). The bound is derived from the rest;
- **indeterminate:** the evaluation could not run or could not classify what it saw (a reducer exception, an absent
  or unknown precheck, a missing fresh number). The member is **kept**: unknown evidence never authorizes an omission.
  A kept member with no verified numbers cannot enter a bound, so the mint then refuses.

The mint refuses outright (no bound; `neg8.bound_not_derived`) on anything that is not evidence about one member's
number: an unauthenticated launch lineage, a member that is not the canonical condition, an unrecorded calibration
identity, a bundle inventory that cannot be sealed, kept members of more than one condition (no majority vote), of
more than one calibration identity or of two window lineages, or fewer than 10 kept members. The chain's corpus prune
asks the mint itself which members it drops (`whole_window.neg8_corpus_mint_drops`), so the chain's collected manifest
and the mint's input are the same bytes. The harvest accepts a left-out succeeded member only for one of the five
reasons, and records it `neg8.corpus_member_dropped` (DISCLOSE); any other left-out succeeded member makes a selected
corpus and `neg8.bound_not_derived`. The harvest's accepted reasons are the mint's own set, imported, not copied
(`harvest.py`: `from joulewise.whole_window import NEG8_MINT_DROP_REASONS as NEG8_ACCEPTED_DROP_REASONS`, at
`a434e363d`), so the two cannot drift. *Worked example:* member 7 succeeded, but its fresh re-reduction differs from
its stored summary (`reduction_mismatch`): it is omitted, the bound uses the other 11, and the harvest records
`neg8.corpus_member_dropped` for it. Had member 7's reducer raised instead, it would be indeterminate and kept, and
the mint would refuse.

**A fourth source of omission: physics, applied by the harvest** (NEG-8 ruling of 2026-10-07, decision 4; §0.12).
*Forcing problem:* a corpus member whose request overlapped a competing process measured the contender, not the
instrument. Kept, it inflates the corpus's standard deviation and its envelope, which widens the bound and the
allowance: a bias toward passing. The member-level physics codes of §6.4 are evaluated at harvest from the monitor
journals, which the chain's mint cannot see when it derives the bound. *Mechanism*
(`harvest.neg8_corpus_physics`, after the monitor joins): a corpus member of the validated bound on which a
member-level physics exclusion of §6.4 fires (`contention.request_overlap`, `battery.member_span`,
`battery.accumulator_excursion`, `thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`,
`clock.step_overlap`) is **omitted** from the bound, because its energy is an observation of the disturbance. A corpus
member whose physics is unmeasured is kept. The harvest records `neg8.corpus_member_dropped` for it
(`observed.source` `harvest_physics`, `observed.reason` the first of those codes that fired), writes the bound's own
manifest less those members to `derived/neg8-clean-corpus.json`, builds the bound from the clean members' recorded
points with the core's own builder, and validates its arithmetic and corpus identity against those bytes, as the
collected-subset path of item 3 does. A clean bound that validates goes to restricted custody
(`withheld/neg8-clean-bound.json`), the screen is re-run against it, and the record of the drop is
`derived/neg8-corpus-physics.json`. The minimum stays 10 kept members; fewer, or a clean bound that does not
validate, gives `neg8.bound_not_derived` (`observed.source` `corpus_physics`). The reference members and the corpus
therefore share one eligibility rule: the §6.4 physics codes drop a reference from the screen (§0.12) and a corpus
member from the bound. *Worked example (synthetic):* of 12 succeeded corpus members, member 3's request overlapped a
process at 0.09 CPU-s/s (`contention.request_overlap`): the bound is re-derived from the other 11 with t(0.975, 10),
and the screen is re-run against it. Had a second member also been flagged, the bound would rest on 10; had a third,
on 9, and the window would carry `neg8.bound_not_derived`.

**The bound's age is judged on physical times** (PLAN2 row 2, V1). *Forcing problem:* the bound is valid for 24 h,
and revision 4 judged its age at the desk clock of whoever wrote the verdict. A headless harvest of BETA would start
after the watchdog's hold, when BETA's bound was already 23.8–24.4 h old, and the window would be removed for good
(`validity_horizon_expired`). *Mechanism* (`whole_window.py` at `a434e363d`): the bound's derivation time is the end
of the latest kept corpus member's measured window, and its evaluation time is the end of the last end reference's
measured window, both read from the bundles. *Worked example:* the corpus's last member ends at 01:10 and the last end
reference at 08:40: the bound is 7.5 h old when used, whether the verdict is written at 09:00 or 40 h later. A corpus
none of whose kept members has a readable measured-window end has no physical derivation time; the mint then
refuses (`whole_window._hazard_bound_derived_at_s` raises, at `a434e363d`) instead of dating the bound by its own
clock, and the window gets `neg8.bound_not_derived`. Every real kept member passed a fresh reduction, which itself
refuses a bundle with no measured window, so this can happen only to a corrupted corpus.

**OS-build and power-supply strings are disclosed, not staleness triggers** (V2). The bound records the OS build and
a digest of the power-supply identity its corpus saw. A difference against the references used to mark the bound
stale and remove the window; both are labels (a string the OS prints, a hash of the adapter's description), not
measurements of the machine's state. On a block-5 window (the hazard route) a difference is now recorded in the verdict's
`disclosed_binding_changes`; a change of calibration identity stays a staleness trigger, because the bracket is
judged against that identity.

### 5.4 The window's tail

After the post calibration, in this order (`joulewise/b5/driver.py` `run_hazard_night`, at `d3c107f2f`): the chain
exits and the driver stamps that moment; the driver proves the chain's process group gone (a census of the group
with no signal, then the existing termination proof) and counts the window's yield (§5.7); G10 runs if the plan asks
and the chain exited by itself (§3), with the monitor and the meter still journaling; then the driver waits until at
least 5 s have passed since the chain exited (polling both supervisors meanwhile; after G10 that time has long
passed) and stops the monitor and the meter (§0.17); last, it writes its terminal record with the window's yield. If
the chain's exit could not be proven, the monitor and the meter are left running for the dead-man (the watchdog's
fallback stop). During G10 the driver keeps supervising (cold pass N7, `_run_g10`, `_wait_supervised`): it waits on
G10's process 5 s at a time (`G10_POLL_S`) under the same 1,500 s cap, and between waits runs the chain's supervision
pass, which restarts a monitor or meter that died, records `monitor.outage` and checks free disk, as during the
chain. A supervision pass that raises is recorded (`supervision_errors`); one that asks for a stop has already written
its flag, is recorded (`supervision_stop`) and ends supervision, while G10, a diagnostic, runs to its end. (Revision 6
said nothing restarted a dead monitor during G10: the driver then blocked for up to 1,500 s in one wait.) The
harvest may open as soon as the terminal record exists (§7.1), because the driver holds nothing after it.

**The dead-man never signals an unidentified process group** (audit-fix item 9; `driver.reap_orphan_monitor`). When
the watchdog's fallback stop finds a recorded monitor or meter process group, it signals it only if it can identify
the group's leader: either by the recorded start time and the identity reader, as before, or, without them, by `ps`
showing the recorded command line on a process that started between 5 s before and 1 s after the journal's start
stamp. Otherwise it leaves the group alone and writes `monitor.orphan_unverified` (DISCLOSE), because signalling an
unidentified group could hit an unrelated process that reused the id.

**The watchdog releases a finished window at once** (PLAN2 X1; `scripts/magistrate_watchdog.py` at `a434e363d`,
P2-WD). *Forcing problem:* in revision 4 the watchdog treated a window as running until t0 + `WINDOW_MAX_S` + 300 s
even after its chain had exited, and launched no headless session meanwhile, so the machine sat idle about 15 h after
every chain. *Mechanism:* the watchdog releases the window's hold, once and for good (a one-way latch keyed on the
plan id, the custody root and the SHA-256 of `result.json`), when it sees on one tick: `chain.started` and
`chain.exited`; the driver's terminal `result.json` with this plan's id and a finite end time no later than now;
`courier.sent`; and an empty agent census and no driver process. The same release applies to a NULL window and to a
CHAIN_STOPPED one. A driver that never wrote its first record is released through a create-once
`night/launch_abandoned.json`. A failed courier keeps the old dead-man timing. After the release, `WINDOW_MAX_S`
bounds only a hung chain or a dead driver.

### 5.5 Sizing

- **T_stream_max** = 335 s for every window (§0.14). The sizing output records each pack's own longest stream:
  ALPHA's is 314 s (its members are all 1.7B-class), and BETA's and GAMMA's are 335 s (their 8B members). It sets
  every pack's `T_stream_max_s` to the block's longest, 335 s, at which the frequency gate passes for
  |f| ≤ 3.6306 ppm.
- **Programmed span.** The programmed span is the chain's length if every member takes its longest allowed path. The
  rule keeps block 4's conventions and uses the chain at the int5 head `d3c107f2f` (`scripts/size_b5_window.py`, its
  `conventions` list):
  - span = (1 + collection stages) × 60 s settle + the collection stages' countdowns (0 s, §5.1) + the pre and post
    calibration pair (770 s) + the bound derivation (320 s) + the corpus prune (320 s) + the window calibration
    verdict (60 s) + the sum of member allowances + stage custody + the terminal shutdown (300 s) + one corpus retry
    + the reference spare retries;
  - a **member allowance** is load + warm-up + prefill + forced decode + the cooldown at its 300 s cap + both
    idle-admission attempts (275 s: two attempts of 110 s each plus guards, against an observed attempt maximum of
    103.6 s at the former 750 records). That is 595 s for a 1.7B member and 619 s for an 8B member. NEG-8 and
    reference members are charged as 1.7B members. These allowances come from block 4's committed source, which
    predates the 576-record idle baseline (§0.3); an attempt now takes about 83 s (75 s of capture plus block 3's 8 s
    of attempt overhead), so the allowance over-covers it and is kept;
  - **stage custody** (the bookkeeping time around members) is 180 s per collection stage, plus 77 s per member
    (45 s reduction, 32 s sampler start and wind-down), plus 2 × 240 s bracket-writer custody, 300 s reservation and
    120 s terminal custody;
  - **one corpus retry** (§5.1) is charged as one more corpus stage: 60 s settle + 180 s overhead + 12 × (595 + 45 +
    32) s = 8,304 s;
  - **the reference spare retries** (§0.12) are charged at their worst case, every spare run: for each reference
    stage, 60 s settle + 180 s overhead + its spares × 672 s (spares are reference members, charged as 1.7B members,
    595 + 77 s). That is 2,256 s for each triplet (3 spares) and 912 s for the midpoint (1 spare), 5,424 s (1.51 h)
    per window, the same in all three packs (`reference_spare_retry_s` in the sizing output);
  - the **bound derivation** is now charged 320 s, not block 4's 60 s: a real derivation re-reduces 12 bundles,
    about 270–320 s (PLAN2 §1.4 item 6; never measured live). The **corpus prune**, which asks the NEG-8 mint which
    corpus members it would drop (§5.3), reads the same 12 bundles and is charged the same. The **window calibration
    verdict** (§5.1) is charged 60 s for one refit of about 15 s.
- **`WINDOW_MAX_S`**, the window's deadline measured from t0, = 60 × ceil((span + 3,300 s) / 60). The 3,300 s is the
  arm's allowance: the dwell cap of 2,700 s plus the census, reads, network-time OFF, collectors and cadence probe.
- **`B5-SIZING-OUTPUTS`** (draft values at the int5 head `d3c107f2f`; sealed at H_claim):
  `configs/campaigns/v5_claim_25g83/sizing_b5.json`, schema `joulewise.b5_sizing.v1`, SHA-256
  `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa` at `d3c107f2f` (`FILL[B5-FINAL-HASHES]`; status
  `UNSEALED_DRAFT`; computed by this author with `shasum -a 256`, and `scripts/size_b5_window.py --check` reproduced
  it byte for byte at that commit). Earlier drafts: `f114f9b9…` at the frozen head `a434e363d`, before the spares;
  `a5c6ec05…` at `b9d02700a`; `7c53ebc8…` on lane L10's branch with the older sizer; `b31a27b5…` after the timing lane
  `f4cf9047`; `9d16edfe…` at `f8164893`. The value in force is the one sealed at H_claim. `scripts/size_b5_window.py` writes it from block 4's committed sizing source
  (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, SHA-256
  `f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81`) and from the packs' stage graphs, order
  manifests and configs. `--check` reproduces the file byte for byte. The program also refuses unless its arithmetic
  reproduces block 4's committed 22,494 s span and 25,800 s window. Block 4's source names four GAMMA configs to fix
  which model is 1.7B-class and which 8B; the timing lane's regeneration changed their bytes (their `idle_seconds` and
  plan tag), so the program reads them at the bytes GAMMA's plan tree now records and lists them under
  `class_map.superseded_block4_configs`; bytes recorded by neither still refuse. Each window plan reads
  `/packs/<label>/programmed_span_s` and `/packs/<label>/T_stream_max_s` from it. Lane L10 changes only GAMMA's
  plan-tree digest and the two diagnostic stages' order-manifest paths and digests; the members per class (61 / 40),
  the programmed span and `WINDOW_MAX_S` do not change, because each diagnostic stage is still one auxiliary member
  of the reference class.

  | Pack | Members, 1.7B-class / 8B | Programmed span | `WINDOW_MAX_S` | Expected chain, block-3 basis | Expected chain, projected |
  |---|---|---|---|---|---|
  | ALPHA | 119 / 0 | 98,826 s (27.5 h) | 102,180 s (28.4 h) | 31,584 s (8.8 h) | 19,460 s (5.4 h) |
  | BETA | 19 / 100 | 101,226 s (28.1 h) | 104,580 s (29.05 h) | 32,634 s (9.1 h) | 20,510 s (5.7 h) |
  | GAMMA | 61 / 40 | 87,690 s (24.4 h) | 91,020 s (25.3 h) | 27,747 s (7.7 h) | 17,426 s (4.8 h) |

  The programmed spans and `WINDOW_MAX_S` are read from the sizing output at `d3c107f2f` (`FILL[B5-FINAL-HASHES]`);
  each span is revision 6's plus the 5,424 s of spare retries (93,402, 95,802 and 82,266 s at `a434e363d`). The
  members column counts the planned roster, without spares; the expected-chain columns assume no spare runs.

- **Why the deadline is about three times the expected chain.** The rule charges every member, at once, both worst
  cases: the cooldown runs to its cap and idle admission needs its second attempt; and it charges a corpus retry and
  seven spares that most windows never run. *Worked decomposition, ALPHA:* 119 members × 595 s = 70,805 s, of which
  35,700 s is every member's cooldown at its 300 s cap and 32,725 s is every member's two admission attempts.
  Per-member custody adds 119 × 77 = 9,163 s; the corpus retry 8,304 s; the spare retries 5,424 s; settles,
  calibration, derivation, prune, the window calibration verdict, stage custody and shutdown the other 5,130 s; span
  98,826 s. Block 3 measured a start-to-start member
  cycle, cooldown and custody included, with a median of 236.5 s and a maximum of 274.9 s; each member here is
  charged 672 s (595 + 77).
- **Is that right? As a deadline, yes.** A chain stopped at its deadline loses its post calibration, and so the
  whole window. The deadline must therefore never cut a slow window that could still be claim-usable. A chain
  anywhere near this bound would have most members at the cooldown cap, and `member.cooldown_cap_hit` removes such
  members, so that window would fail the 8-of-10 minimum anyway. The deadline now exceeds the 24 h calibration
  horizon; the collection deadline (§5.1) keeps the post calibration inside the horizon, so a slow chain is truncated
  to a usable tail rather than killed. Since the watchdog releases a finished window at once (§5.4), the generous
  size costs only the time to notice a hung chain or a dead driver.
- **Expected chain time** (planning only; it gates nothing). Two figures:
  - *Block-3 basis* (measured, an upper planning figure). Block 3's median start-to-start member cycle at 750 idle
    records, 236.5 s, plus 10.5 s for an 8B member; per collection stage 60 s settle + 39 s head + 62 s tail (block-3
    maxima); fixed 60 s pre-calibration settle + 770 s calibration pair + 320 s bound derivation + 320 s corpus prune
    + 60 s window calibration verdict + 300 s terminal = 1,830 s (scratch `sizing_v2.json`, SHA-256
    `6a82745f47b40c8aa1ea6aefe2c45c2d4cce2b7a7e65d114165057e64fae00de`). Each pack has 10 collection stages.
    - ALPHA: 1,830 + 10 × 161 + 119 × 236.5 = 31,584 s ≈ 8.8 h.
    - BETA: 1,830 + 1,610 + 19 × 236.5 + 100 × 247.0 = 32,634 s ≈ 9.1 h.
    - GAMMA: 1,830 + 1,610 + 61 × 236.5 + 40 × 247.0 = 27,747 s ≈ 7.7 h.
  - *Projected* (not measured; built from the measured block-3 mean cycle and the savings of the changes now in the
    code). Block 3's mean start-to-start cycle was 257.1 s (PLAN2 §1.1). Per member, subtract 22.9 s for the
    576-record idle baseline (2,725 s over 119 members, timing ruling), 41.0 s for the 2× cooldown rule (mean wait
    53.9 → 9.1 s over 109 cooldowns, 4,883 s over 119 members, timing ruling) and 56.9 s for the refit done once and
    strict validation moved to the harvest (1,654 + 1,642 + 3,475 s over 119 members, PLAN2 M1–M3): 136.3 s for a
    1.7B member, 146.8 s for an 8B member. Per collection stage subtract the 20 s countdown (assuming, as PLAN2's
    budget does, that it ran inside the 39 s head): 141 s. The stage-end verdict saving (PLAN2 S4, about 655 s per
    window) is not subtracted, because the 62 s tail is not decomposed.
    - ALPHA: 1,830 + 10 × 141 + 119 × 136.3 = 19,460 s ≈ 5.4 h.
    - BETA: 1,830 + 1,410 + 19 × 136.3 + 100 × 146.8 = 20,510 s ≈ 5.7 h.
    - GAMMA: 1,830 + 1,410 + 61 × 136.3 + 40 × 146.8 = 17,426 s ≈ 4.8 h.
  ALPHA-1 measures which figure is right. Each window adds its 4–47 min arm. Below about 119 s from one decode's end
  to the next idle capture, recovery is untested (archived gaps 119–740 s); ALPHA-1 records idle medians and cooldown
  waits against block 3's 30.6 mW reference as a diagnostic (PLAN2 §1.4 item 4).
- **Deadline stop.** A chain still running at t0 + `WINDOW_MAX_S` is stopped by the driver; the window then has no
  post calibration, so it is not claim-usable (`calibration.no_bracket`). The next attempt's per-member allowance
  becomes the larger of the sizing output's and the stopped attempt's largest observed member cycle, plus the sizing
  margin, and `WINDOW_MAX_S` is re-derived by the rule above without an erratum (member cycles are structural timing,
  releasable under §8).
- **Block duration.** Assume every window is claim-usable on its first attempt. With the watchdog releasing each
  window at its terminal record (§5.4), one window to the next is the window plus about 0.6–1.6 h: the driver's tail
  and courier about 0.1 h, a watchdog tick of up to 5 min, the pin advance and the next plan a few minutes, the
  harvest 0.5–1.5 h, and the 180 s stand-down lead (PLAN2 §1.3). Adding three arms of 4–47 min, the three windows
  take about 18–23 h at the projected chains (15.9 h of chain) and about 28–33 h at the block-3 basis (25.6 h of
  chain), before any re-arm or frequency redraw. (Revision 4, with the
  fence held to t0 + `WINDOW_MAX_S` + 300 s, gave about 71 h before desk gaps.)

### 5.6 Disk between windows

The harvest archive is an APFS clone of the collected roots where the tool allows (it shares storage until
modified).

**`BACKUP-DESTINATIONS`** (filled from committed code and the runbook):

- *Where they are named.* Each attempt's window plan names two destinations, `claim_backup_destination` and
  `bound_backup_destination`, as absolute paths (`joulewise/b5/plan.py`).
- *What is checked.* At the arm, the disk hazard requires room for one planned copy on each destination's volume
  (`joulewise/b5/driver.py`, disk targets). In the window only the volumes the chain writes to are watched, so a full
  backup volume never stops a chain.
- *Where they point.* By the window runbook's convention (`docs/phase_2/window_runbook.md`, `CLAIM_BACKUP_DEST` and
  `BOUND_BACKUP_DEST`) they are `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/<window>/claim` and
  `…/bound` in iCloud Drive. iCloud Drive's local folder is on the runs volume, which is why the arm counts three
  copies there (§4.2).
- *Who copies.* The copy itself is a desk step after the harvest (`scripts/backup_runs.sh`, the packs' `backup`
  stages, which the chain does not render). No block-5 program runs it at this writing; the lead runs it.

The disk hazard re-measures free space at every arm, so no separate disk ledger is kept.

### 5.7 Yield: counting what was collected

*Forcing problem.* Several causes make every member of a window refuse before its bundle exists: about 15 window-level
checks are repeated by each member, so one deterministic failure among them loses all of them. In revision 4 such a
window ended with 0 of 119 bundles, chain exit 0 and verdict GO. A stage's return code of 1 cannot tell one lost
member from twenty (a healthy ALPHA shows about 2.6 stages with a nonzero code), the cause sat only in logs the
courier does not send, and chain stops at exit 10, 11 or 12 also said GO. With windows back to back, a deterministic
cause would repeat in every window, at 1.5–3 h of chain each, until someone read a harvest.

The **yield** is counts only: members planned, logged, succeeded, and bundles present. It is never an energy, a
power or a duration, so it is releasable structure under §8 item 2. It never stops collection, and it costs under
50 ms of reads per stage boundary. (PLAN2 §2.2; `joulewise/b5/driver.py` and the harvest at `a434e363d`.)

- **Yield plan.** Before the chain starts, the driver lists, for each collection stage: its id and position, its
  runs root, its run ids (less any run id an earlier stage already launched into the same root), the number planned,
  and **min_valid**, the fewest succeeded members that still leave the stage able to do its job:
  - the NEG-8 corpus stage: 10 (the bound's minimum, §5.3; a minimum of 12 would raise a false alarm in about 28% of
    windows);
  - start and end triplets: 2 of 3; midpoint: 0 of 1 (the screen's minimum, §0.12; `driver.REFERENCE_ENDPOINT_MIN_VALID`,
    `REFERENCE_MIDPOINT_MIN_VALID`). The driver does not count spares: its yield plan lists only the planned
    members, so a stage whose loss a spare restored still shows that loss in the driver's counts;
  - science stages: ⌈planned × 8 / 10⌉, the stage's share of the 8-of-10 cell minimum (§6.6): 16 of a 20-member quad
    stage, 8 of a 10-member absolute stage. If each member is lost independently with probability 1/37, these trip
    by chance with probability 1.6 × 10⁻⁴ and 2.1 × 10⁻³, so a trip means a systematic cause.

  It is written once to `night/yield_plan.json`, outside the plan's `hazard_window` block.
- **Counting in the window.** After each stage's journal line, at the start of the next settle (never during an idle
  capture), the driver checks each planned bundle directory: present, and summary status succeeded. Raw-byte
  validity stays with the harvest. It writes one line to `night/stage_yield.jsonl` with the stage's status: **ZERO**
  (none of the planned members present), **LOW** (succeeded below min_valid) or **OK**. ZERO and LOW record
  `yield.stage_zero` or `yield.stage_low` and write `night/yield_alert-<position>.json` once.
- **Repeated refusals.** The driver reads the campaign log as it grows. Three consecutive members that ended without a
  bundle for one shared cause (the member's last error line with its digits replaced by `#`, or else its exit code)
  record `stage.members_refused_pre_bundle_identical`, once per cause.
- **Stall.** No new bundle directory and no new stage journal line for 3,600 s records `yield.stage_stalled`, once.
- **No process is started for any of this in the window.** A network call would sit inside a settle, the idle
  stretch the next member's cooldown and baseline read. (Revision 6 also cited the agent census, which then matched
  "t3", "claude" or "codex" anywhere in a command line; it now ignores the window's own processes, §4.5.) The watchdog, a scheduled job and not an agent,
  picks the alert files up on its own tick (`scripts/magistrate_watchdog.py` `queue_yield_alerts`, lane P3-WD, at
  `a434e363d`): for a window from t0 − 180 s until its dead-man deadline, each `night/yield_alert-*.json` is queued
  once as a notice for Ed (`notice_pending`, kind `yield_alert`, with the file's SHA-256). A file it cannot read is
  recorded as an event, and a file over 64 KiB is queued unread. Reading an alert never changes a fence, a release or
  a launch. The notice reaches Ed when the watchdog next launches a headless lead session (the **magistrate**), which
  comes soon after the window ends because the watchdog releases a finished window at once (§5.4); a true mid-window
  email would need a network process inside the window.
- **Terminal record.** After the chain's process group is proven gone, the driver writes the window's yield into
  `night/hazard_result.json`: planned, logged, succeeded, failed, bundles present, the per-stage rows, and the
  **yield status**: **EMPTY** (no bundle present at all), **LOW** (some stage below its min_valid), **FULL** (every
  planned member succeeded), **PARTIAL** (otherwise), or **UNKNOWN** (the count failed or nothing was planned; it
  changes nothing else). The verdict stays GO for a collected window, because it describes the arm; an EMPTY window
  exits 5. A chain stopped at exit 10, 11 or 12 gets the verdict **CHAIN_STOPPED**, never REFUSED (which would have
  held the watchdog longer). A failed post calibration and a failed bound derivation are recorded as their own faults.
  EMPTY, LOW and CHAIN_STOPPED send a fault email to Ed (a change of state). The courier's notice leads with
  "collected X of Y planned members"; it never carries durations, member identities or error texts.
- **At the harvest.** `harvest.json` and `derived/window_flags.json` carry planned, present, raw-valid (a stream of at
  least 1 MiB and no missing files) and succeeded, overall and per stage; a spare counts as planned only when the
  retry ran it (its bundle exists), and an unrun spare is never `member.bytes_missing`. The command prints members =
  raw-valid / planned and the window-removing reasons, and exits 6 when a COLLECTED window has nothing present
  (`collection.zero_yield`). `collection.failure_histogram` groups every error line of the operator logs by its
  digit-redacted text (full texts to `withheld/`). A disagreement with the window's own `stage_yield.jsonl` records
  `yield.harvest_disagrees_with_window`. A window with no collection stage row at all is harvested as
  **NO_COLLECTION**, with `chain.stopped_before_collection`, every collector still run (§7.1).

Every yield code is DISCLOSE (§6.8): `cell.below_minimum` and `neg8.bound_not_derived` already remove a window where
it matters; the yield exists to say so early and to stop a repeat (§7.3). *Worked example (synthetic).* An ALPHA
window ends with stage rows corpus 12/12, start triplet 3/3, the first decode quad stage 0/20 (ZERO), the rest full.
The terminal status is LOW (a stage below its min_valid of 16); Ed gets a fault email that leads "collected 99 of 119
planned members"; the harvest later removes the window by `cell.below_minimum`, and the orchestrator does not arm the
next window on the same code until the cause is fixed (§7.3).

### 5.8 The whole-machine meter (a recorded diagnostic)

*Forcing problem.* Every registered number is a processor-rail energy (§1): the CPU, GPU and ANE package as the
sampler reports it. A reader will ask what share of the machine's energy that is, and whether the rail estimate moves
with the machine's energy from member to member. The sampler cannot answer: it sees only the rails. An independent
instrument at the machine's power input can, without touching any claim.

*Boundary.* Every element of the path, from the wall to the rails:

```
 mains AC --> [adapter, 140 W] --USB-C cable, 28 V--> [KM003C meter] --USB-C--> [Mac DC input]
               AC-to-DC loss here:                    Vbus and Ibus,               |
               NOT measured                           50 samples/s                 +--> processor rails, CPU+GPU+ANE
                                                                                   |    (powermetrics: the claim boundary)
                                                                                   +--> rest of the machine (memory,
                                                                                   |    storage, fans, display asleep)
                                [battery] <--- B0AC x B0AV, SMC, 1 read/s -------->+
```

- *mains AC* and the *adapter*: the 140 W charger; its conversion loss happens before the meter and is not measured;
- *USB-C cable, 28 V*: the adapter and the Mac agree to 28 V under USB Power Delivery's extended power range;
- *KM003C meter*: an inline USB-C power meter (POWER-Z KM003C) in that cable, reporting the bus voltage (Vbus) and
  current (Ibus) 50 times a second;
- *Mac DC input*: the meter measures what enters the Mac; the Mac's own reading of the same quantity is the SMC key
  PDTR (§4.2);
- *battery*: when it assists, it supplies the machine beside the DC input, and the meter cannot see that energy; the
  battery term −B0AC × B0AV (SMC, once a second) adds it back;
- *processor rails* inside the machine are the claim boundary; the *rest of the machine* is everything else the
  DC input feeds.

So the meter's boundary is **whole-machine DC input plus the battery term**, not wall AC: the charger's loss is
excluded.

*The reader.* `scripts/km003c_monitor.py` (at `a434e363d`) polls the meter every 200 ms at ordinary scheduling
priority (the probe rejected background priority) and reads B0AC, B0AV, PDTR, PSTR and PPBR from the SMC at every
poll. It writes one create-once stream file per start, `<custody>/hazards/meter/stream-NNN.jsonl`: a header (status
`streaming` or `absent`), one line per poll, error lines, and a trailer. The header and trailer each carry a pair of
clock readings (CLOCK_MONOTONIC_RAW and `time.monotonic_ns`), so the stream can be placed on the members' clock. When
no meter is attached it writes an `absent` header and exits 0, and the driver does not restart it. Its cost: 0.302
CPU-s over a 120 s live run, 0.25% of one core. It runs outside the chain's process tree, so the contention monitor
counts it, at about 0.0025 CPU-s/s, one twentieth of the 0.05 limit; its own energy is on the rails like the
monitor's and is disclosed with it (analysis plan §8.1).

*Quantities* (`joulewise/external/km003c_parse.py` and the harvest's `meter_joins`, at `a434e363d`), for each member
over one window, its measured request (the harvest's request span, `sampling_started` to `sampling_stopped`). Revision
5 also named each phase; the code computes the request only, so phase-level figures are not produced in block 5:

- **ΔE_rail**: the rail energy above the member's idle baseline, the bundle's `idle_subtracted_energy_j` as the
  harvest re-derives it from the raw records;
- **ΔE_machine** = [E_meter(window) − P_meter(baseline) × T] + [E_battery(window) − P_battery(baseline) × T], where
  T is the window's length, E(window) is the mean of the samples inside the window times T, P(baseline) is the mean
  over the member's idle-baseline stage, the meter power is Vbus × Ibus and the battery power is −B0AC × B0AV at each
  SMC read. When no SMC read falls in the window or the baseline, the battery term is marked unavailable and
  ΔE_machine is the meter term alone;
- **ρ** = ΔE_rail ÷ ΔE_machine, the rails' share of the machine's extra energy; undefined when ΔE_machine ≤ 0.

The meter's timestamps are CLOCK_MONOTONIC_RAW; member spans are in `time.monotonic_ns`. The two differ by a constant
except across a system sleep, taken from the stream's own clock pairs (rejected if its start and end pairs disagree
by more than 1 ms) or, failing that, from the monitor's clock journal line nearest the span.

*Worked example (synthetic).* A member's idle baseline reads a meter mean of 9.0 W and a battery power of 0 W. Its
measured request lasts 20.0 s with a meter mean of 52.0 W and a battery mean of 1.5 W (assist). The meter term is
52.0 × 20 − 9.0 × 20 = 860 J; the battery term is 1.5 × 20 − 0 = 30 J; ΔE_machine = 890 J. With ΔE_rail = 712 J,
ρ = 712 ÷ 890 = 0.80, inside the hard band of analysis plan §8.2 (0 < 0.80 ≤ 1, and 890 − 712 = 178 J ≥ 0). Without
the battery term ρ would read 712 ÷ 860 = 0.83: leaving the battery out overstates the rails' share whenever the
battery helps.

*How well it reads* (all on 2026-10-06). At the desk, 120 s idle: 0 dropped and 0 duplicated samples, largest
clock-fit residual 10.0 ms (the parser fits the meter's sample clock to the host's clock from the poll times; the
residual is how late a batch arrived beyond that fit), median PDTR/meter ratio 0.992, Vbus 27.44–27.50 V, no flag.
The probe's 300 s run: largest residual 16.8 ms; PDTR/meter median 0.986. Under the B0AC validation load (§4.2), on
20 s bins: PDTR = 0.955 × meter + 2.3 W (r = 0.9975), median per-second ratio 0.987; and PSTR = 0.959 × (meter +
battery power) + 2.1 W (r = 0.993), so the system's total is accounted for by the DC input plus the battery term. The
probe could not test ρ itself: on the loaded desk machine background work moved the baseline and gave negative ρ. So
the central band for ρ is set by the first clean window (analysis plan §8.2).

*Flags* (all DISCLOSE; their observed fields hold counts, mA, V, milliseconds and the PDTR/meter ratio, never an
energy, so they are structure):

| Code | Fires when |
|---|---|
| `meter.absent` | the stream header says `absent`, the stream has no samples, or no stream file exists |
| `meter.drops_excess` | dropped samples ÷ (kept + dropped) > 0.5% |
| `meter.duplicates` | the meter re-delivered samples that the parser dropped (count > 0) |
| `meter.clock_fit_residual` | the largest clock-fit residual > 2 sample periods (40 ms at 50 samples/s), or no fit |
| `meter.pdtr_gain_out_of_band` | the median over 1 s bins of mean PDTR ÷ mean meter power is outside 0.95–1.02, or cannot be computed |
| `meter.battery_activity` | a B0AC read inside a member window is nonzero (either direction) |
| `meter.vbus_out_of_contract` | a sample's Vbus is outside 26.6–29.4 V (28 V ± 5%) |

*What it can never do.* The meter never refuses an arm or a window, never removes a member, and never enters a
claim-bearing number. ΔE_rail, ΔE_machine and ρ are energies and an energy ratio: they go to restricted custody in
one file per window, `withheld/meter.json` (one row per member, with the stream used, the clock-offset source and
whether the battery term was available), until the release event, like every other energy (§8). No file is written
when the window has no meter stream; `meter.absent` records that. `meter.battery_activity` is a member-level flag;
the other `meter.*` flags are window-level. The driver's supervision of the reader (§0.17) adds one more DISCLOSE
code, `meter.supervision_fault`: the reader could not be started; it crashed within 30 s of its start five times in a
row (it is still restarted, every 30 s instead of every 1 s); the supervisor failed to record an event; or the
reader could not be proven stopped (`joulewise/b5/driver.py`, `MONITOR_BACKOFF_AFTER` = 5, `MONITOR_RAPID_EXIT_S` = 30,
`MONITOR_RESTART_BACKOFF_S` = 30).

## 6. Flags and exclusions

### 6.1 Where flags come from

All flag files are append-only, with an fsync per line.

| Stage | File | Writer |
|---|---|---|
| Desk, before an arm (never during a dwell or a window) | `<custody>/flags/desk.jsonl` | the record-only collectors run by the lead; a window-removing flag here means the cause is fixed before scheduling; the driver never reads these flags |
| Arm | `<custody>/hazards/arm.json` (verdicts and measurements); `<custody>/flags/arm.jsonl` (collectors) | the hazard arm; the collectors |
| Window | `<custody>/hazards/monitor/{clock,battery,thermal,contention,disk}.jsonl` plus raw bytes; `<custody>/hazards/meter/stream-*.jsonl` (§5.8); the driver's flags, `night/stage_yield.jsonl` and `night/yield_alert-*.json` (§5.7) | the monitor; the meter reader; the driver |
| Harvest | `derived/flags.jsonl` (every flag, de-duplicated); `derived/window_flags.json` (summary); `derived/exclusions.json`; numbers under restricted custody `withheld/` | the harvest |

### 6.2 The catalog

`flag_catalog.json` is normative; this section states its rules in words. Its `rules.cell_unit_minimum` is 8.

*No code stays unclassified for good* (audit-fix 2, Opus audit F2). Revision 6 kept two codes deliberately out of the
catalog so that they would always block the release event. But the loader also refused any catalog that classified
them, so the registered cure for an UNCLASSIFIED code (a cold erratum classifying it, §7.2) could never be applied,
and one torn flag line left its attempt blocked for ever. Now:

- `records.malformed_flag` (a flag line that failed validation: torn, not JSON, or not a valid flag record) is
  DISCLOSE. Because the line may have carried an exclusion, the harvest reads what the line still shows of its code,
  whole or as the prefix it was torn inside, and lists every catalog code it could have been. If any of those is an
  EXCLUDE_WINDOW code, it adds `records.malformed_flag_exclusion_possible` (EXCLUDE_WINDOW). Otherwise, if any is an
  EXCLUDE_MEMBER code and the line still shows a run id, it adds `records.malformed_flag_member_exclusion_possible`
  (EXCLUDE_MEMBER) on that member. A line that shows no code, or a possible member code but no run id, is disclosed
  only: the rule excludes on what the line shows, never on what it might have said (`harvest._malformed_flag_line`).
  *Worked example (synthetic):* a line torn after `{"code": "calibration.capt` could have been
  `calibration.capture_invalid` (EXCLUDE_WINDOW) among seven candidates, so the window is removed; a line that still
  shows a member's run id and is torn inside `"code": "member.tok` could only have been `member.token_count_mismatch`
  (EXCLUDE_MEMBER), so that member is removed (both candidate lists computed by this author from the catalog).
- `collector.unmeasured` (a collector the flag package does not know how to class) is still absent from the catalog,
  so it blocks the release event until a cold erratum classifies it, which the loader now accepts.

| Family | What it covers | Effect |
|---|---|---|
| PACK_IDENTITY, CODE_IDENTITY, MODEL_IDENTITY | the pack, the executed code or the model differs from what was sealed, or could not be compared | EXCLUDE_WINDOW (one member whose model identity cannot be derived from its own metadata: EXCLUDE_MEMBER) |
| CALIBRATION | the bracket is missing, invalid, unbound or fails the acceptance, the ledger it is judged from fails its own integrity checks, a capture saw charging or AC loss, or an earlier capture the acceptance relies on changed | EXCLUDE_WINDOW (DISCLOSE: the desk's ledger-readiness checks before an arm; battery assist during a capture; a changed capture the acceptance does not rely on; a historical file that could not be read; the writers' records of §6.10) |
| NEG8 | the bound was not derived, the screen failed, the verdict holding the screen is absent, or a verdict that did not pass cannot name its failed members | EXCLUDE_WINDOW (DISCLOSE: the aggregate verdict codes of §6.5, a corpus member dropped for a registered reason or for physics, lost references and a lost midpoint (§0.12; the analysis plan makes a lost midpoint claim-excluding for the primary contrasts), and the verdict producer's own records) |
| INSTRUMENT | the pre-calibration screen failed | EXCLUDE_WINDOW (a member that could not read the sampler binary's digest: EXCLUDE_MEMBER, §6.3, unless the harvest re-derived it: DISCLOSE) |
| CLOCK_SYSTEMATIC | a step during a calibration capture; most recorded anchors not `bounded` | EXCLUDE_WINDOW |
| MEMBER_VALIDITY | §6.3 | EXCLUDE_MEMBER |
| PHYSICS_IN_SPAN | §6.4 (battery assist is DIAGNOSTIC, not this family) | EXCLUDE_MEMBER |
| ROSTER | §6.7 | EXCLUDE_MEMBER (window-level roster failures: EXCLUDE_WINDOW; the chain's roster records, such as a retried member or a horizon-truncated tail, §5.1: DISCLOSE) |
| RECORDS | receipts, lineage formalities and the driver's pre-launch lineage check, attempt history, pin ledger, provenance digests, naming, notices, missing journals, a member's error output not copied, malformed and rebuilt flag lines, unreadable operator logs | DISCLOSE (three exceptions: source bytes changed during the harvest, EXCLUDE_WINDOW; a malformed flag line that could have been a window exclusion, EXCLUDE_WINDOW, or a member exclusion naming a readable member, EXCLUDE_MEMBER) |
| DIAGNOSTIC | network-time output, clock steps and frequency changes outside any span, G10, s1-structural checks, the battery-temperature rise across a stage (§0.6), battery assist (§6.4), the whole-machine meter (§5.8), the yield counts (§5.7), an unread hazard probe at the arm (§4.1), monitor restarts and orphans left unsignalled (§5.4, §6.8) | DISCLOSE |

### 6.3 Member exclusions: validity

A member is removed from every cell it feeds when any of these is flagged:

- its status is not `succeeded` (`member.status_not_succeeded`), or idle admission refused it after its retry
  (`member.admission_aborted`);
- its bundle fails strict validation, which re-reduces the raw evidence (`member.strict_validation_failed`); its
  re-reduction is not byte-identical to the stored summary (`member.reduction_mismatch`); or a required file is
  missing, unreadable or present twice (`member.bytes_missing`, `member.unreadable`, `member.bytes_ambiguous`);
- its clock anchor is not `bounded` (`member.anchor_not_bounded`), or the harvest's recomputed status differs from
  the recorded one (`member.anchor_recompute_mismatch`);
- its runtime-observed token counts differ from the registered counts (42 or 2048 prompt tokens, 512 output tokens)
  (`member.token_count_mismatch`);
- its target phase (`phase.decode` for decode members, `phase.prefill` for p2048 members) fails its precheck
  (`member.target_phase_precheck_failed`), including the one precheck test that reads a science energy,
  `anchor_energy_envelope_exceeds_quarter_metric` (`member.anchor_energy_envelope_exceeded`, blinding RESTRICTED). The
  p42 phase is not a target phase;
- the GPU was not idle during its idle baseline (`member.idle_window_suspect`); its cooldown hit the cap
  (`member.cooldown_cap_hit`); or its campaign cooldown evidence does not verify (`member.cooldown_evidence_unverified`);
- its configuration bytes are not in the pack's committed inventory (`member.config_not_in_inventory`; the lineage
  check refuses such a member at write time, so normally its bundle is simply absent);
- its model identity cannot be derived from its metadata (`model.identity_underivable`);
- its #421 per-capture battery pair (the registry read just before and just after its sampler stream, kept as raw
  bytes) is present and failed (`battery.capture_pair_failed`). One failure is disclosed instead: when the pair failed
  on its endpoint current alone (the pair rule tests the unsigned |InstantAmperage| > 200 mA), every failed endpoint
  reads a negative InstantAmperage from its own raw bytes, the SMC reads cover the member (§6.4), and the member's
  battery join found none of `battery.member_span`, `battery.accumulator_excursion` and `battery.unmeasured`, the
  failure was discharge, and `battery.capture_pair_assist` (DISCLOSE) replaces the exclusion and names it
  (`harvest._pair_assist`). Without SMC coverage the exclusion stands, because the journal then cannot show the span
  free of charging;
- the whole-window verdict lists it among its per-member failures (`member_failures` in the verdict row) for a reason
  that no other member code carries (`member.whole_window_member_failure`). Those reasons are:
  - its environment evidence is missing or failed (`environment_admission_missing`, `environment_admission_failed`);
  - its CPU-idle criteria do not replay from its own telemetry (the `cpu_*` reasons and
    `processor_combined_power_w_p95_exceeded`), or its GPU idle admission does not (`gpu_idle_admission_*`);
  - its idle-admission attempt cannot be paired with the telemetry it was judged on
    (`idle_admission_attempt_ledger_invalid`).

  The verdict's other two per-member reasons already have their own codes. In-window thermal pressure is
  `thermal.powermetrics_pressure_elevated` (§6.4), and an invalid bundle is `member.strict_validation_failed` and its
  kin. Leaving those two out keeps each exclusion in one family, which the sensitivity line of analysis plan §8
  relies on.

  *Why this rule is needed.* Its environment evidence includes the post-run observation that the displays stayed
  asleep and the screensaver stayed off through the request. That observation is how decision D-078 (item 4) closed
  the screensaver contamination class of July 2026, and no other code measures it. The verdict as a whole is only
  disclosed (§6.5), so without this member rule a member whose display woke during its request would be kept.
  *Code state:* the harvest emits it at `a434e363d` (`harvest.whole_window_member_failures`), one flag per listed
  member with its reasons, whether or not the verdict authenticates. When a verdict that did not pass has no
  `member_failures` list, or one its own validator rejects, no member can be named, and the window is removed
  instead (`whole_window.member_failures_unreadable`, §6.5).
  *One case moved* (audit-fix item 6 and the orchestrator's ruling on it, 2026-10-07): a post-run guard observation
  whose collector raised an exception (every reading null, `collector_error` set; §6.10) is no longer missing
  environment evidence to the verdict, so the verdict does not list the member for it. The member is still removed,
  by `member.target_phase_precheck_failed`: the pinned reducer's environment barrier, which the ruling left
  unchanged, marks such a record `environment_admission_failed` on the member's target prechecks, because an
  unmeasured post-run environment cannot show the member clean.

Codes added since revision 4 that remove a member (catalog effect EXCLUDE_MEMBER; their writers are in §6.10):

- `member.timeout`: the member's child was stopped at the 1,800 s cap (§5.2);
- `env.member_quiet_state_violated`: during the member a display was awake, the screensaver ran, or Low Power Mode
  was on (measured states);
- `member.idle_admission_telemetry_missing`: idle admission passed every test it could evaluate, but its CPU
  telemetry was missing or too short, so the idle window's quietness is unmeasured;
- `instrument.binary_identity_unmeasured`: the member could not read the SHA-256 of the `powermetrics` binary it ran
  (a different digest still refuses the member before it runs). The harvest supersedes it when it can re-derive the
  digest (cold pass N1, Fable audit F10; `harvest` step `binary_identity`): the binary is a system file that changes
  only across a reboot, so when the member's collection boot (`extra.launch_lineage.collection_boot_session_id`) is
  the harvest's own boot and the SHA-256 of the executable the member recorded (`device.powermetrics.executable_path`,
  `/usr/bin/powermetrics` by default) equals the calibrated digest (`instrument_calibration.bindings.powermetrics_sha256`),
  the flag is moved whole into `instrument.binary_identity_rederived` (DISCLOSE) and the member is kept. A different
  digest, another or an unknown boot, or an unreadable executable keeps the exclusion.

Revision 5 also listed `member.stderr_uncopied` here. It is now DISCLOSE (orchestrator, 2026-10-06, at `a434e363d`):
it records that the copy of a member's error output into the stage log failed, which is a record not written, not
a measured fault. A flag the member printed there behind the unwritten-flag marker (§6.10) is still recovered,
because the harvest also scans the member's own error-output file (`operator-logs/member-stderr/`).

### 6.4 Member exclusions: physics in the member's span

A member's **span** is the earliest-to-latest hull of two time ranges, in the controller's `time.monotonic_ns()`
domain: its sampler stream (the `pre_spawn` to `post_parse` clock stamps, or the sampling markers when those are
missing) and the controller's battery span (from the start of the idle baseline to the end of the **idle drift
sentinel**, the short idle reading the controller takes right after the request). The hull over-covers rather than
under-covers. The member's **request span** is `sampling_started` to `sampling_stopped`: the measured request
(`harvest.member_spans`, at `a434e363d`). A member whose span cannot be placed is removed (`member.span_unknown`),
because the rules below cannot be applied to it.

**Battery** (ruling of 2026-10-06, §9.2; sources and validation in §4.2). The harvest's join decides
(`joulewise/b5/harvest.py` `battery_join`, `_battery_assist`, `accumulator_member_flags`, at `a434e363d`). Terms used
below:

- The registry publications **in force** for a span are the last publication at or before its start, every
  publication inside it, and the first publication at or after its end. SMC reads in force are chosen the same way.
- An SMC read is **good** when B0AC is an integer with no read error, and **fresh** when its five recorded keys
  (B0AC, B0AV, PDTR, PSTR, PPBR) differ from the previous good read's: a frozen SMC repeats its block, and repeats
  are not new measurements. The SMC **covers** a span when good, fresh reads are no more than 5 s apart across it
  (`battery.SMC_MAX_GAP_S`). When it does not, the registry's InstantAmperage and Amperage at the in-force
  publications stand in for B0AC in the current rules below, and `battery.smc_unavailable` (DISCLOSE) records the
  fallback.
- Each good read **holds** its value from its own time until the next good read, never longer than 5 s. A read
  belongs to a stretch of time when its hold overlaps that stretch for a positive time, so the read in force at a
  stretch's start belongs to it, and a read taken at or after its end belongs to what follows.
- **Assist**: the battery discharging into the machine while the adapter is connected and the battery is not
  charging. It is **any** negative B0AC read (ruling item 1) on a span with no read of charging or AC loss. −200 mA
  is not part of the definition; it is the threshold the assist report counts reads against.

Rules:

- `battery.member_span` (EXCLUDE_MEMBER) fires on any of:
  1. *charging current:* a good B0AC read in force above +200 mA; without SMC coverage, InstantAmperage or Amperage
     above +200 mA at an in-force publication;
  2. *charging or AC lost:* IsCharging Yes or ExternalConnected No at any in-force publication, or at any good 5 s
     registry poll inside the span.
- `battery.accumulator_excursion` (EXCLUDE_MEMBER): over an interval between two consecutive in-force publications,
  the charge accumulator implies a mean charging power above 200 mA × the publication's voltage (units below); or,
  without SMC coverage, the discharge accumulator's mean is **positive** and beyond that limit. The discharge
  accumulator sums discharging ticks only, so a positive mean is inconsistent evidence, not discharge, and without
  SMC coverage it keeps the exclusion (`observed.sign_inconsistent`). With SMC coverage the same reading is
  `battery.accumulator_unavailable` (DISCLOSE; cold pass N4): the 1 s SMC reads measure the current directly and
  remove the member for any charging read (`battery.member_span`), so a 60 s registry record that disagrees with
  itself adds no evidence of a hazard. The harvest and the hazard module's copy of the rule (`hazards/battery.py`,
  where the same case was `battery.member_span`) changed together, and a parity test holds them equal. A negative
  discharge mean beyond the limit is assist evidence, below.
- `battery.unmeasured` (EXCLUDE_MEMBER), the missing-evidence predicate: the charging and AC state over the span is
  unknown, so the member cannot be kept. Only the registry reads that state; the SMC current says nothing about it.
  - *With SMC coverage:* no registry publication in force at or before the span's start; an in-force publication
    that lacks IsCharging or ExternalConnected; or a **state hole**: more than 120 s between consecutive good
    registry reads that carry both state fields, among the last such read at or before the span's start, every one
    inside and the first at or after its end. With no read before the start, the stretch from the start to the first
    read counts; with no read after the end, the stretch from the last read to the end counts (the monitor may have
    stopped after the span; while it runs, its 5 s poll writes a line on any state change).
    *Worked example (synthetic):* span 100–130 s. State reads at 0 s and 62 s and none after: the stretches are
    62 s and 130 − 62 = 68 s, both at most 120 s, so the state counts as measured. State read only at 0 s: the
    stretch from 0 s to the span's end is 130 s, more than 120 s, so the member is `battery.unmeasured`.
  - *Without SMC coverage* (unchanged from revision 4): no registry publication for more than 120 s overlapping the
    span, or an in-force publication lacking a state or current field.
- `battery.assist` and `battery.assist_outside_request` (both DISCLOSE). Computed only when no read in the span
  showed charging or AC loss. The member's span is split into **phases**: with a request span inside it,
  `pre_request` (from the span's start to the request: the idle baseline and the warm-up), `request`, and
  `post_request` (from the request's end: the idle drift sentinel); without one, the whole span is one phase,
  `span`. For each phase the flag records: the SMC reads that belong to it (`smc_reads_in_force`), how many are
  negative (`smc_reads_negative`) and how many are below −200 mA (`smc_reads_below`), the minimum B0AC, the held
  time below −200 mA (`smc_duration_below_s`), and, without SMC coverage only, the in-force publications taken before
  the phase ends whose InstantAmperage or Amperage is negative (`registry_publications_negative`); also the
  discharge-accumulator intervals beyond the limit that overlap the phase (`accumulator_intervals_over_limit`). A
  phase is **assisted** when any of these counts is nonzero. The member carries `battery.assist`, the marker the
  sensitivity line uses (analysis plan §8.1), when the deciding phase (`request`, or `span`) has a negative SMC read,
  or, without SMC coverage only, any of the other evidence; it carries `battery.assist_outside_request` when only
  other phases were assisted, which decides nothing (ruling item 5). With SMC coverage the 1 s reads locate the
  discharge, so an accumulator interval (about 60 s long) that overlaps the request without a negative read in it
  is reported in that phase and does not decide. The discharged energy of each phase, the sum over its negative
  reads of held time (clipped to the phase) × (−B0AC × B0AV), goes to restricted custody
  (`withheld/battery-assist.json`) with the other machine energies (§8); the counts, minimum and durations are
  structure. Battery energy is never added to or subtracted from a rail energy. A member that is also
  `battery.unmeasured` because a publication in force did not read the state keeps its disclosure, marked
  `observed.state_unread`.
- `battery.accumulator_activity` (DISCLOSE): an accumulator sign with at least one tick on an in-force interval and
  a mean at or below the limit. Every archived calibration capture shows 7–32 discharge ticks at −122 to −151 mW
  while InstantAmperage read 0.
- `battery.accumulator_unavailable` (DISCLOSE): the accumulator rule could not run on an interval (a field not read
  at both publications, a counter that went backward, or no voltage); also, with SMC coverage, a gap of more than
  120 s between registry publications, over which only the accumulator test goes unevaluated, and a sign-inconsistent
  discharge accumulator (above).

*Accumulator units* (lane L1, 2026-10-05, on 66 archived publications and a live read): each `Accumulated*` field
adds its instantaneous value in mW once per tick (about 1.01 s), each `*AccumulatorCount` counts ticks, and battery
power is split by sign into a charge accumulator (`AccumulatedBatteryPower` / `BatteryPowerAccumulatorCount`) and a
discharge accumulator (`AccumulatedBatteryDischarge` / `BatteryDischargeAccumulatorCount`); the split was proven by
an exact identity on all 65 intervals. So Δ(accumulated) ÷ Δ(count) is the mean power in mW over the ticks on which
that sign occurred, and the registered scale is 0.001 W per unit. *Positive control:* between the 2026-09-25 20:47
and 2026-10-01 06:17 publications the discharge accumulator gained 15,043 ticks at a mean of −5,415 mW; the registry
reading inside that interval was −447 mA at 12,180 mV = −5,444 mW; they agree within 0.6%.

*Worked example (synthetic).* A member's measured request runs from 0 to 5 s, with good, fresh B0AC reads at 0, 1, 2,
3 and 4 s of −865, −1,200, −400, −150 and 0 mA, the next read at 5 s, B0AV 12,180 mV, and ExternalConnected Yes and
IsCharging No throughout. Each read holds 1 s inside the request; the read at 5 s belongs to `post_request`. In the
`request` phase: 5 reads belong, 4 are negative, 3 are below −200 mA, the minimum is −1,200 mA, and 3 s are held
below −200 mA. The discharged powers are 10.54, 14.62, 4.87 and 1.83 W, so the discharged energy is
(0.865 + 1.200 + 0.400 + 0.150) A × 12.18 V × 1 s = 31.85 J (to `withheld/`). The member is kept and carries
`battery.assist`; the −150 mA read alone would have made it so. Had the only negative read fallen in the warm-up, the
member would carry `battery.assist_outside_request` and stay in both lines of the sensitivity pair. Had one read in
force been +450 mA, or one registry poll in the span read IsCharging Yes, the member would be removed by
`battery.member_span`, and no assist would be computed. If between two in-force publications the charge accumulator
gained 40 ticks totalling +216,000 mW·ticks, its mean is +5,400 mW, above 200 mA × 12.18 V = 2,436 mW, and the member
is removed by `battery.accumulator_excursion`. The same numbers with a negative sign on the discharge accumulator
remove nothing: with SMC coverage the interval is reported in each phase it overlaps, and only a negative 1 s read in
the request decides the marker.

**Thermal.** `thermal.os_level_nonzero`: any in-force 5 s sample of the OS level is nonzero (in force as for the
battery). `thermal.powermetrics_pressure_elevated`: the member's own records show thermal pressure
(`environment_admission.thermal_pressure_elevated_in_window`, unchanged). A gap in the OS-level samples
(`thermal.unmeasured`) is disclosed only, because the member's own records still carry thermal pressure.

**Contention.** `contention.request_overlap`: an outside process (not `kernel_task`) exceeds 0.05 CPU-s/s in a
10 s interval that overlaps the member's request (request start to request end). `contention.unmeasured`: part of the
request is covered by no interval. This replaces revision 2's environmental-diagnostic trigger with a member rule.

**Clock.** `clock.step_overlap`: a `clock.step` falls inside the span. A gap in the 1 Hz journal (`clock.unmeasured`)
is disclosed only, because the member's own anchor bound stays authoritative and is computed from its own records.

**Instrument.** `instrument.insufficient_in_window_samples` and `instrument.cadence_ratio_below_threshold`: the
member's own records are too few or too slow for its target phase.

### 6.5 Window exclusions

The window is not claim-usable when any of these fired:

- `pack.identity_mismatch`: the pack's plan tree, any configuration, the prompt pin, the extraction spec, or a NEG-8
  or reference manifest differs from its digest in the sealed inventory or the plan tree's own pins, recomputed at
  harvest from preserved bytes; also `lineage.plan_tree_digest_differs`.
- `code.executed_differs_from_sealed`: the executed-file inventory differs from the sealed inventory; or the chain
  bytes differ from their sidecar; or the measurement checkout's HEAD is neither H_claim nor H_claim plus pin-only
  commits; or it has tracked edits, or untracked files under the executed roots (Python could import them).
- `model.identity_mismatch` (the model, tokenizer or runtime realized at the arm or recorded in any bundle differs
  from the pins of `identity_pins.json`, §4.6 item 3), `model.identity_inconsistent_in_window` (two identities within
  one identity unit), and `model.identity_unpinned` (no pin to compare against, which happens when the measurement
  checkout lacks `identity_pins.json`).
- `*.identity_unmeasured` for pack, code or model: a number-protecting identity check could not run. This is a
  harvest problem first (§7.2).
- `calibration.capture_invalid`, `calibration.capture_battery_pair_failed` (a calibration capture's #421 pair failed,
  other than on discharge alone with the journal confirming it, below), `calibration.bracket_acceptance_failed`
  (evaluated with the acceptance's ledger-cutoff baseline), `calibration.acceptance_mismatch` (the acceptance bytes
  differ from the plan tree's pin), `calibration.session_not_bound` (the bracket session names another plan, window or
  runs root), `calibration.binding_failed`, and `calibration.no_bracket` (including a chain stopped before its post
  calibration by `disk.low`, the census or the deadline).
- `calibration.ledger_snapshot_refused`: the calibration ledger, read up to this window's terminal entry, fails its
  own integrity checks. That means a missing or malformed ledger, a broken digest chain, or the acceptance's cutoff
  entry (sequence 376 with its recorded head digest) not found in the chain. The bracket's captures and the
  acceptance's screens are authenticated through this ledger. The bracket evaluation reads the same snapshot and
  refuses with the same reasons, so `calibration.bracket_acceptance_failed` fires as well. Classing this code as
  window-removing therefore costs no extra window, and it keeps the window removed even if that propagation changed.
- `calibration.capture_battery_span` and `calibration.capture_battery_unmeasured`: the battery rule of §6.4 applied
  to each calibration capture's span, as to a member's (`harvest._capture_battery_joins`, at `a434e363d`). A capture
  has no request inside it, so its whole span is one deciding phase. `battery.member_span` or
  `battery.accumulator_excursion` over the span gives `calibration.capture_battery_span`. A capture whose #421 pair
  did not pass and whose span the journal cannot stand in for gives `calibration.capture_battery_unmeasured`: no
  capture span, no battery journal, a join that could not run, or `battery.unmeasured` over the span. (A capture
  whose pair passed is not removed for a gap in the journal.) Discharge alone is disclosed:
  `calibration.capture_battery_assist` (DISCLOSE), with the capture's discharged energy in
  `withheld/battery-assist.json`. A capture pair that failed on its endpoint current alone, with every failed endpoint
  reading a negative InstantAmperage from its raw bytes, an SMC-covered span and none of the three excluding battery
  codes, is `calibration.capture_battery_pair_assist` (DISCLOSE) in place of `calibration.capture_battery_pair_failed`
  (the member rule of §6.3, applied to a capture). *Forcing problem for the 1 s reads* (mock rehearsal round 3,
  finding R3-5): when this join read the registry, the monitor stopped right after the chain exited, before the
  registry's next publication, so the post capture's last in-force publication never existed and every window got
  `calibration.capture_battery_unmeasured`. *Mechanism at `a434e363d`:* the join judges the current on the 1 s SMC
  reads, the state-hole rule of §6.4 measures the trailing stretch only to the span's end, and the driver stops the
  monitor no sooner than 5 s after the chain exits (§0.17).
- `calibration.historical_custody_mismatch`: a file of an earlier calibration capture that this window's acceptance
  relies on, re-hashed by the harvest, differs from the SHA-256 its ledger entry recorded (§6.10). A changed capture
  the acceptance does not rely on is `calibration.historical_custody_mismatch_unused` (DISCLOSE).
- `clock.step_overlap_calibration`: a clock step inside a calibration capture.
- `neg8.bound_not_derived` (§5.3) and `neg8.screen_failed`; also `whole_window.verdict_absent`, because the NEG-8
  screen's result is held in the whole-window verdict. The screen runs on the surviving references (§0.12, "The
  screen on the survivors"): a lost reference never removes the window by itself; fewer than two survivors at an
  endpoint does (`observed.reason` `references_insufficient`). Lost references and a lost midpoint are disclosed
  (`neg8.reference_lost`, `neg8.midpoint_lost`); a corpus member dropped for physics is disclosed
  (`neg8.corpus_member_dropped`, §5.3).
- `whole_window.member_failures_unreadable` (NEG8, NUMBER; orchestrator item P4, at `a434e363d`): the whole-window
  verdict did not pass, and its `member_failures` list is absent or rejected by the verdict's own validator
  (`whole_window._validated_member_failures`). Then no failed member can be named, so
  `member.whole_window_member_failure` (§6.3) cannot remove the members the verdict failed, and keeping every member
  would keep numbers the verdict rejected. A verdict that passed, or a well-formed list (an empty one included), does
  not emit it. An absent verdict file is `whole_window.verdict_absent` instead, and an unparseable one is
  `neg8.screen_failed` (the screen it holds cannot be read) with `whole_window.verdict_unauthenticated`; both remove the
  window already.
- `instrument.precal_screen_failed`.
- `clock.systematic`: at least 5 members of the window have a recorded anchor status and more than half of them are
  not `bounded`.
- `cell.below_minimum` (§6.6) and `roster.no_science_bundles`.
- `records.source_changed_during_harvest`: bytes the harvest reads changed while it read them. Operating-system
  metadata files that no reducer, validator or harvest step reads (`.DS_Store`, `.localized` and AppleDouble `._*`
  files, which Finder writes when a person browses a runs root) are ignored by all three of its comparisons (Opus
  audit F7); any other added, removed or changed file still fires it.

**Two aggregate codes are disclosed, not window-removing:** `whole_window.not_passed` (the stored whole-window verdict
did not pass) and `g3.recompute_failed` (check F5-2 of G3, the desk provenance checker
`scripts/check_window_provenance.py`, which independently recomputes that verdict, did not find a clean pass). The
verdict passes only if every member passed, so both codes fire when a single member failed admission or its
environment guard. Making them window-removing would restore "one aborted member voids the window", which Ed's
2026-10-05 ruling removed. The verdict's checks are not lost: each part acts at its own level through its own code.

- *The NEG-8 screen* (window level): `neg8.screen_failed`. The harvest emits it from the verdict's NEG-8 bracket:
  a decision other than passed, or any NEG-8 condition (`neg8_gross_point_drift_exceeded`,
  `neg8_idle_sub_point_drift_exceeded`, `neg8_bracket_missing`, `neg8_bracket_reference_invalid`,
  `neg8_drift_bound_stale`, the bound-underived conditions). The exceptions are the harvest's re-screens of §5.3
  (the collected-subset bound, a reference lost at harvest, a corpus member dropped for physics), whose result
  decides alone. `neg8_bracket_reference_invalid` now means fewer than two survivors at an endpoint or more references
  than planned (§0.12).
- *The calibration bracket* (window level): `calibration.bracket_acceptance_failed`, which the harvest evaluates
  itself.
- *Each member's own failures* (member level): `member.whole_window_member_failure` (§6.3), which removes only the
  members the verdict names. In-window thermal pressure and an invalid bundle are carried by their existing member
  codes.
- *The AC adapter's wattage continuity* is disclosed only. The battery rule (§6.4) measures directly whether the
  battery supplied any of the load, which is the way a weaker or reconnected adapter could change a measurement.

### 6.6 Cells, units and the minimum

This amends D-179 ruling 1 and D-078's no-reduced-mean text, as Ed's 2026-10-05 ruling requires (§10).

- **Which units a flag removes.** A removed repeat member removes that repeat. A removed quad member removes its
  whole quad, so the A, B, B, A drift cancellation is kept. In GAMMA a quad with any removed member is dropped from
  its contrast.
- **Minimum.** Every target cell keeps at least 8 of its 10 units in each stratum: floor cells in both the repeat and
  the quad stratum, GAMMA's contrasts in the quad stratum. Otherwise `cell.below_minimum` removes the window. The p42
  cells are not target cells.
- **What the reduced cell computes.** The stratified mean, variance and half-width of analysis plan §4, which equal
  D-179's when all 20 units are kept; floors with the small-sample guard of analysis plan §5; contrasts over the kept
  quads (analysis plan §7).
- **Why 8.** At 8 units per stratum the reported-cell half-width grows by at most (2.365 / 2.262) × √(10/8) − 1 ≈
  17%, and floors use the existing guard g(8) = 1.134.
- **Planning figure.** If each member is aborted by idle admission independently with probability 1/37 (blocks 2
  and 3), a floor window keeps both target cells at or above the minimum with probability about 0.85 (a repeat is
  lost with probability 0.027 and a quad with 0.104), against (36/37)¹¹⁹ ≈ 0.04 under revision 2's rule that any
  aborted member aborts the window. Bursts that hit consecutive members make losses cluster within a quad, which this
  figure ignores.
- **Disclosed beside every cell:** the kept units n_r and n_b, the exclusions by family and their positions in the
  window, and the attempts of the pack with their causes (analysis plan §8).

### 6.7 Roster

A bundle that is not in the plan's roster (`roster.not_in_plan`), not bound to this attempt (`roster.foreign_attempt`),
or created before `chain.started` (`roster.before_chain_started`) is ignored, not used; a roster member left without
an admissible bundle is `member.bytes_missing`.

A bundle whose recorded `run_id` (in `metadata.json`) differs from its directory (`roster.run_id_mismatch`) is
removed. The harvest places a bundle in a cell, a unit and a quad position by its directory name. Each planned member
has its own config, which carries its `run_id`, so a bundle filed under another member's directory already fails the
config check (`member.config_not_in_inventory`). This code covers the remaining case: a bundle whose own records
disagree about which member it is. A kept member must have one identity in every record a later program may key on,
or the same energy could be counted under two units or in the wrong quad position. The catalog classes it NUMBER for
that reason, and since audit-fix item 7 the emitter and the test fixture do too (revision 6 recorded the emitter's
REPRESENTATION as a restatement). It costs one unit and should never fire.

### 6.8 Disclosed only

All REPRESENTATION flags: receipts, lineage formalities other than the configuration bytes (`lineage.*` except the
plan-tree digest), attempt history, the pin ledger, provenance digests, naming, notices, missing or malformed
monitor journals, missing arm or terminal records, collector failures; the OFF action's output and the time-server
offset; monitor probes falling inside phases; a missing #421 per-capture pair
(`battery.capture_pair_missing_covered` when the continuous journal covers the span; `battery.capture_pair_missing`
otherwise, beside the `battery.unmeasured` that then removes the member); `battery.accumulator_unavailable` (the
accumulator rule could not run on an interval; the publication rule still applies); clock steps and frequency
changes outside any span; `disk.low` (its effect arrives through `calibration.no_bracket`); the desk's ledger
readiness checks before an arm (`calibration.ledger_not_ready`, `calibration.ledger_readiness_unmeasured`); the G10
result; the s1-structural diagnostics; the battery-temperature diagnostic of §0.6 (`thermal.stage_battery_rise`,
`thermal.battery_temperature_unmeasured`), reported beside the window's NEG-8 result; battery assist
(`battery.assist`, `battery.assist_outside_request`, §6.4; `calibration.capture_battery_assist`, §6.5), the #421
pairs that failed on discharge alone (`battery.capture_pair_assist`, §6.3; `calibration.capture_battery_pair_assist`,
§6.5) and the SMC fallback (`battery.smc_unavailable`); clock samples too skewed to use (`clock.unmeasured`,
`read_skew`, §4.2); the whole-machine meter's flags (`meter.*`, §5.8); the yield flags (§5.7); G3 not applying to a
floor pack (`g3.not_applicable`); the driver's pre-launch lineage check (`records.lineage_prelaunch_mismatch`,
§0.17); a member's error output not copied into the stage log (`member.stderr_uncopied`, §6.3); a changed historical
capture the acceptance does not rely on, and a historical file that could not be read
(`calibration.historical_custody_mismatch_unused`, `calibration.historical_custody_unmeasured`, §6.10); an arm
probe of the clock, battery, thermal, contention or disk hazard that returned UNMEASURED (`<module>.arm_unmeasured`,
§4.1); an in-window census that could not be read (`census.unmeasured`, §4.5); a re-derived powermetrics digest
(`instrument.binary_identity_rederived`, §6.3); lost NEG-8 references, a lost midpoint and a corpus member dropped for
physics (`neg8.reference_lost`, `neg8.midpoint_lost`, `neg8.corpus_member_dropped`, §0.12, §5.3; the analysis plan
makes `neg8.midpoint_lost` claim-excluding for the primary contrasts, §2.4 there); a flag line that failed validation,
a writer's stand-in line rebuilt into its flag, and an operator log that could not be read (`records.malformed_flag`,
`records.flag_unbuilt`, `records.operator_log_unreadable`, §6.2, §6.10); a monitor restart (`monitor.restarted`) and a
recorded monitor or meter group the dead-man left unsignalled (`monitor.orphan_unverified`, §5.4); and the records of
§6.10.

`contention.kernel_task_share` stays in the catalog but cannot fire today: an unprivileged `ps` never lists
`kernel_task` (process id 0; checked 2026-10-05), so neither the arm nor the monitor sees its CPU time by name. Its
work is inside the host's total busy time, which the monitor journals every 10 s and nothing judges in the window
(§4.2, Contention). It is to be removed in the prune after block 5 (orchestrator ruling of 2026-10-06).
`monitor.restarted` is now written (audit-fix item 8): the hazard monitor's supervisor calls the driver on each
restart, and the driver writes one window flag with the restart's process id, start count and previous exit, its
interval the gap between the old monitor's death and the new one's start. The gap also shows as the modules'
unmeasured flags over the member spans it touched, and a monitor that keeps dying reaches the flags as
`monitor.crash_loop` and `monitor.outage` (§5.1). (At `a434e363d` no production path wrote it.) The meter's restarts
stay `meter.supervision_fault` (§5.8).

### 6.9 Harvest thresholds

The harvest reads its own copy of the in-window thresholds. The window plan carries this block as well; its values
are the same physical limits as §4.3 under the harvest's names.

```json
{
  "battery_limit_ma": 200,
  "battery_unmeasured_gap_s": 120.0,
  "battery_accumulator_watts_per_unit": 0.001,
  "thermal_unmeasured_gap_s": 15.0,
  "contention_cpu_s_per_s": 0.05,
  "clock_step_ns": 1000000,
  "clock_unmeasured_gap_s": 3.0,
  "disk_low_bytes": 10737418240,
  "clock_systematic_min_recorded": 5
}
```

### 6.10 Checks the writers record instead of refusing

Ed's ruling of 2026-10-05 (§0, revision 3) turned every check that is not a physical hazard into a flag. Inside the
protected measurement code (the controller, the campaign runner, the calibration writer and the bracket reservation)
that was done by the core-prune lanes (`/Users/edr/night-archive/gate-prune/core-prune/DESIGN.md` §3) and the round-2
lanes, and finished by the refusal census and its triage, all at `a434e363d`. Each row below says what used to
refuse, what is recorded now, and what still decides the claim. A refusal that protects integrity stays a refusal;
those are named, and §6.11 says how the whole list is enforced.

**The controller, once per member** (`joulewise/controller.py`):

| What used to refuse the member | Recorded now | What decides the claim |
|---|---|---|
| the pre-slot calibration's #421 battery pair did not pass (A1) | `calibration.capture_battery_pair_unverified` (DISCLOSE) | the harvest re-derives the pair from the same bytes (`calibration.capture_battery_pair_failed`) and joins the battery journal over the capture (§6.5) |
| `git` or the ledger's shape could not be read per member (A5) | `records.pin_ledger` (DISCLOSE) | the harvest's ledger integrity check (`calibration.ledger_snapshot_refused`, EXCLUDE_WINDOW) |
| the pack's directory was not at `<repo>/configs/campaigns/<pack>`, so the repository could not be found from the path (refusal census) | the repository is found with one `git` lookup and `records.pin_ledger` (DISCLOSE, `kind` `pack_root_layout`) is recorded | the session, slot, plan, custody and digest checks that bind the member to the ledger still refuse |
| the member's environment guard failed (A11) | a measured quiet-state violation (display awake, screensaver, Low Power Mode): `env.member_quiet_state_violated` (EXCLUDE_MEMBER); an unknown field, or AC or thermal failures that the hazard journals measure directly: `env.member_guard_flagged` (DISCLOSE) | the reducer's environment barrier is unchanged, so a member whose own environment evaluation failed is still removed through `member.target_phase_precheck_failed` |
| the guard's observation collector raised an exception (refusal-census triage c; `controller._hazard_guard_observation`) | that one observation is recorded as unmeasured (every reading null, `collector_error` naming the exception) and the member runs; the finding `collector_raised` is added to `env.member_guard_flagged` (DISCLOSE), at idle admission and, since audit-fix item 6, after the run (phase `post_run`) | the other observations' readings still apply. A post-run observation recorded this way is no longer missing evidence to the whole-window verdict (`environment_admission.post_run_observation_collector_raised`, read only on the verdict path by the orchestrator's ruling), but the pinned reducer's environment barrier still marks it `environment_admission_failed` on the member's target prechecks, so the member is removed by `member.target_phase_precheck_failed` (§6.3): an unmeasured post-run environment cannot show the member clean |
| the power-policy label or the runtime power observation differed from the calibration's (A14) | `calibration.power_policy_unverified` (DISCLOSE) | a label is not a measurement; the battery and thermal hazards measure the power state |
| the `powermetrics` binary's digest could not be read (A14) | `instrument.binary_identity_unmeasured` (EXCLUDE_MEMBER), superseded by `instrument.binary_identity_rederived` (DISCLOSE) when the harvest, on the member's collection boot, hashes the recorded executable and finds the calibrated digest (§6.3) | a present, different digest still refuses (the binary must be the calibrated one) |
| sampler or runtime processes survived the member's teardown (A17) | `teardown.survivors` (DISCLOSE) | the next members' contention is measured directly (`contention.request_overlap`) |
| idle admission's telemetry was missing or short (A18) | `member.idle_admission_telemetry_missing` (EXCLUDE_MEMBER) | a failed threshold (CPU busy, power, GPU) still retries and aborts as before |
| the window calibration verdict did not match (J1, §5.1) | `calibration.refit_cache_miss` (DISCLOSE); the member refits | the harvest's own refit from the raw bytes |
| the auxiliary-config comparison raised an exception | `records.auxiliary_match_raised` (DISCLOSE), with the exception text | the pack-identity check at harvest |

**The campaign runner, once per stage or member** (`scripts/run_campaign.py`): a member whose child left no readable
metadata (A4), a stale `campaign.lock` reclaimed under a directory lock after proving its owner dead (A9, V3), the
campaign-log identity check (A13), a failed record write before or inside the member loop (A16), and a failed stage
verdict (A20) are each `campaign.runner_record_flagged` (DISCLOSE) with a `kind`; a lock owned by a live process, or
any lock-ownership error, still ends the stage. Two kinds were added by the Opus audit (F4, 2026-10-07). The runner
publishes each running campaign in an **active-campaign registry** (`joulewise/measurement_liveness.py`
`publish_campaign`: its process id and start time, so that a later campaign can tell a live owner from a dead one);
when the `ps` identity probe returns UNKNOWN, the entry is published with no start time and the stage runs, recorded as
`kind: registry_start_time_unavailable` (it used to end the stage). An empty or unparseable `campaign.lock` (a lock
file whose writer died before writing it) is reclaimed only when three facts are proven: the file is at least 30 s
old, `lsof` shows no process holding it open (its content can be written only through its creator's open file, so
with no holder nothing can complete it), and no active-campaign entry naming the runs root belongs to a live process
or one whose state is unknown; it is then reclaimed under the existing directory lock and recorded as
`kind: torn_lock_cleared` with that evidence. Any probe that fails keeps the lock. A stage environment preflight that raised or did not admit (A10) is
`env.stage_preflight_not_admitted` (DISCLOSE); its members carry the failed evaluation, which the reducer's barrier
judges. A cooldown whose result is unknown (A2, A19) is `cooldown.result_unknown` (DISCLOSE) and the member runs; its
claim status is `member.cooldown_evidence_unverified` (EXCLUDE_MEMBER) unless the cooldown was measured.

**The cooldown fallback reference** (PLAN2 s2-05). *Forcing problem:* a cooldown is judged against the previous
member's idle baseline (§0.6). When none is eligible (the stage's first measured member after a refused one, or a
reference that failed its own quiet checks), revision 4's runner either blocked the next member or ran it with an
unknown cooldown, which the harvest then removes. *Mechanism:* the runner measures the cooldown anyway, against the
first reference available in this order: the last eligible idle baseline of this session; else an eligible frozen
anchor anywhere in the window, the NEG-8 start reference first; else a **self-referenced** test that needs no outside
reference: two adjacent windows of max(the policy's window, 30 s), each with the policy's coverage, the newest
window's mean power the reference, and the window before it within min(the policy's tolerance, 10%) of it, with
thermal state nominal and the policy's 300 s cap. The self-referenced test never runs looser than the cooldown-v2
defaults (30 s, 10%), because without an idle level a 5 s window cannot tell a slow decay from a plateau. The result
is an ordinary cooldown record with its raw trace, verified at harvest like any other, and
`campaign.runner_record_flagged` (`kind: cooldown_fallback_reference`, DISCLOSE) names the reference used.
*Worked example (synthetic):* no eligible baseline exists; the newest 30 s window averages 0.040 W and the one before
it 0.043 W, 7.5% apart, at most 10%: the next member starts. Had the earlier window averaged 0.050 W (25% apart),
power would still be falling and the test would keep waiting, up to 300 s.

**The calibration writer and the bracket reservation** (`scripts/validate_powermetrics_fiducial.py`,
`scripts/reserve_calibration_window_bracket.py`, `joulewise/calibration_ledger.py`). Every row is
`calibration.writer_record_flagged` (DISCLOSE) with the `kind` named:

- `desk_identity_differs` (A6-R1): the reservation now measures the OS build, the machine model and the T1 bindings
  (the digest of the sampler binary and the MLX version a capture is bound to) itself, instead of copying a
  prediction typed at the desk, and records any difference. The writer's own comparison of two
  measurements stays a refusal: within one boot minutes apart, a difference is a real identity change.
- `historical_custody_unverified` (A6-R2/R3): the writer and the reservation skip the committed-pin check and the
  re-hash of every historical calibration file. *Forcing problem:* the reservation re-verified 190 historical files,
  3.33 GB, in iCloud Drive with optimize-storage on, under a 120 s budget; an evicted file would time out and stop the
  chain at exit 10 with nothing collected (PLAN2 row 4; other files in the same backup tree were already evicted). This window's own capture files are still verified at
  finalization, under their own deadline.
- `head_pin_stale` (PLAN2 row 4): the committed ledger pin lags the ledger's physical tail. The reservation appends
  the session to the physical tail and records how the pin relates to it, instead of refusing; a stale pin is cured by
  the next pin-only commit (§4.6 item 6).
- `session_custody_unverified`: the writer's check of this session's own custody could not complete inside its
  deadline; a session-custody worker still running past it refuses (`session_custody_worker_not_quiescent`).
- `display_sleep_action_failed` (A7): `pmset displaysleepnow` failed; the capture's own fit and the pre screen judge
  any effect.
- `binding_read_substituted` (A8): the sampler's header lacked the machine model or OS build, and the values the
  writer read at its start were used.
- `desk_identity_unreadable` (audit A6, 2026-10-07): on the `HAZARD_PACK` path a desk identity file the reservation
  reads was missing or malformed. The reservation used to exit 2 (`calibration_reservation_json_invalid`) and the
  chain stopped at the reservation before any measurement; now it measures the identity itself with an empty desk
  fallback (power policy: the desk epoch's, else the desk T1's, else the plan's `ac_high_power`) and records the
  file, path and reason. A live read that fails with no desk fallback still refuses.

The executed estimator code differing from the acceptance's (A15) is not a record: it is
`code.executed_differs_from_sealed` (EXCLUDE_WINDOW). The ledger's integrity refusals stay: a malformed ledger, a
broken hash chain, a rollback, an identity conflict, a held lease, an unfinished recovery.

**Historical custody is re-verified at the harvest, once** (`calibration_ledger.historical_custody_report`, lane
P2-VPF; called by `harvest._Harvest.historical_custody`, at `a434e363d`; the report goes to
`derived/historical-custody.json`). Because the slots skip the historical re-hash, the harvest re-hashes every
historical calibration file the archived ledger records, once per window, against the SHA-256 in its ledger entry.
This window's own bracket session is left out, because its files are verified at finalization. Each ledger row gets
one outcome: **changed** (a present file's bytes differ from its recorded digest, or a row that was not abandoned
records no file hashes), **unreadable** (a present file could not be read), **absent** (a file is missing, for
example evicted from local iCloud storage, while its present siblings match), **absent_or_unreachable** (the capture
directory is missing, or did not answer a 2 s probe), or **verified**. A digest mismatch is never downgraded to an
absence.

*Which captures the window relies on* (refusal-census triage d, 2026-10-07). *Forcing problem:* the first version of
this pass removed the window for a changed file in any earlier capture, including another window's bracket, which no
number of this window uses, so the removal protected no number of the window it removed. *Mechanism:* the
harvest reads the window's acceptance (§0.11) and takes the attempt ids of the captures it was derived from (its
`derivation_corpus` members, which set the pre screen and the bracket screen) and of the captures it judged before
issuance (its `prior_observation_set`). On the real acceptance these are all 110 governed rows up to sequence 376
(as the integrator's triage reports, `FROZEN_HEAD.md`). Then:

- **changed, and relied on:** `calibration.historical_custody_mismatch` (EXCLUDE_WINDOW, `observed.scope`
  `acceptance_relied`). The acceptance's screens are numbers computed from those captures; changed bytes mean the
  evidence the screens rest on is not the evidence that was judged. If the acceptance cannot be read, nothing can be
  scoped, and every changed row counts (`observed.scope` `acceptance_unreadable`).
- **changed, not relied on:** `calibration.historical_custody_mismatch_unused` (DISCLOSE; `observed.attempt_ids`
  names the captures). Both codes can fire in one pass.
- **no row changed, but some row is unreadable, absent or unreachable, the ledger could not be read, or no row was
  verified:** `calibration.historical_custody_unmeasured` (DISCLOSE; `observed.evicted` counts the evicted files). A
  file that cannot be read is not evidence of a change, and the ledger's hash chain and pin are still checked. Its
  class is NUMBER, as the emitter gives it (revision 5 had restated it as REPRESENTATION); only its effect is
  DISCLOSE.

*Worked example (synthetic):* of 190 historical files, 189 re-hash to their recorded digests and one cannot be read
because iCloud evicted it: the window is kept, `calibration.historical_custody_unmeasured` lists it. Had that file
read back with a different digest, the window would be removed if the file belongs to a capture in the acceptance's
derivation corpus or prior observations, and kept with `calibration.historical_custody_mismatch_unused` if it belongs
to, say, an earlier window's bracket.

**Recovering flags a writer could not write** (core-prune N8). A core writer that cannot write its flag file prints
the whole flag behind a fixed marker (`JOULEWISE_UNWRITTEN_FLAG `) on its error output. The harvest scans the stage
logs (`operator-logs/*.log`), each member's own error-output file (`operator-logs/member-stderr/*.stderr`), the planned
operator-log root and the desk transcript for the marker, and absorbs each flag as if written
(`harvest._unwritten_core_flags`, at `d3c107f2f`). Three outcomes (audit-fix 2, Opus audit F2): a writer's designed
stand-in line (`{code, level, run_id, [observed,] unbuilt}`, printed by `joulewise.flags.core.emit` or the chain's
flag writer when the flag could not be built or written) is rebuilt as the flag it names, so that flag's catalog
effect applies and no exclusion is lost, and `records.flag_unbuilt` (DISCLOSE) records the rebuild (a stage or quad
fact, or a member fact with no run id, is applied to the whole window); any other marker line that is not a valid
flag is `records.malformed_flag` under the rule of §6.2; and a log or log directory that cannot be read is
`records.operator_log_unreadable` (DISCLOSE). Revision 6's "never classified, so it blocks the release event" is
withdrawn: none of these blocks the release event.

### 6.11 Which refusals remain, and how that is enforced

*The rule* (Ed, 2026-10-05; `CLAUDE.local.md`, "Physics refuses; everything else is a flag"): a refusal, a stop or
an exclusion is allowed for exactly two reasons. **PHYSICS**: a physical hazard, measured directly, would corrupt the
energy (§4.2, §6.4). **NUMBER_INTEGRITY**: a number would be wrong or could not be attributed to what it claims to
measure (an identity, a calibration, a screen, a roster position). Anything else (a receipt's wording, a record's
format, a missing log) is a flag that removes nothing.

*How the code enforces it* (refusal census, lane `6fab71954`, merged at `a434e363d`, kept current by every lane
since). The file `configs/gates/hazard_refusals.json` (schema `joulewise.hazard_refusals.v1`) lists every **refusal
site**: each place in the 93 files it scans (91 Python files the hazard path imports or runs, `scripts/backup_runs.sh`,
and the runbook
whose shell functions the chain copies) where the code raises or asserts, exits nonzero, returns a nonzero code or a
blocking status, writes a refusal reason, kills a process, or (in the chain's shell text) stops the chain. Each site
carries a **category**:

| Category | Meaning (the file's own definition) | Entries | Sites |
|---|---|---|---|
| PHYSICS | refuses on a measured physical hazard; names the quantity | 30 | 31 |
| NUMBER_INTEGRITY | refuses because a number would be wrong or unattributable; names the number | 34 | 57 |
| INTERNAL | never stops collection or excludes a window (for example an import-time constant check); names why | 91 | 117 |
| BASELINE | present at the sweep base `e6b6a0ce` and unchanged; not individually reviewed; frozen | 2,594 | 3,664 |
| DEFERRED_REPRESENTATION | a representation refusal another lane is converting | 0 | 0 |

(Counts computed by this author from the file at the int5 head `d3c107f2f`: entries are list items, sites the sum of
their `count` fields; 2,749 entries and 3,869 sites in all. At `a434e363d` they were 27/28, 33/56, 90/116 and
2,598/3,668, 2,748 entries and 3,868 sites. Comparing the two files entry by entry: three BASELINE entries were
reviewed into PHYSICS (the arm's dwell refusal, its instrument refusal and the driver's GO-without-PASS reason, §4.1);
two entries were removed (the in-window census stop on unreadable censuses, PHYSICS, §4.5, and the raise on an
unknown registry start identity, BASELINE, §6.10); and three were added: the refusal of an unusable pack inventory,
`night_refused_pack_inventory_unusable`, NUMBER_INTEGRITY (§0.17), the 1,500 s cap on G10's supervised wait, PHYSICS
(a hung process, §5.4), and the spare-retry helper's exit on an unknown mode, INTERNAL.) The file
also lists every flag code the catalogs mark EXCLUDE_WINDOW (33 codes: 29 NUMBER_INTEGRITY, 4 PHYSICS, none BASELINE;
`whole_window.verdict_absent` was relabelled from BASELINE to NUMBER_INTEGRITY) or EXCLUDE_MEMBER (40 codes: 20
NUMBER_INTEGRITY, 16 PHYSICS, 4 BASELINE), each with the quantity or number it protects. The 33 include
`g3.recompute_failed`, which the test fixture still marks EXCLUDE_WINDOW (§6.5, §13).

The test `tests/hazards/test_refusal_allowlist.py` scans those modules' syntax trees on every run and fails when:
a refusal site appears that the file does not list, or a listed site changes its count or its guarding conditions;
a non-BASELINE entry does not say in at least 30 characters what it protects; a BASELINE entry is new, moved,
re-guarded or more frequent than in the frozen list `tests/hazards/refusal_baseline_frozen.txt` (whose own SHA-256
the test pins), so BASELINE can only shrink; a module the hazard path imports is neither scanned nor listed as
deliberately unscanned; or an excluding catalog code is missing from the file, carries another category, or is
BASELINE outside six named codes (`calibration.ledger_snapshot_refused`, `whole_window.verdict_absent`,
`member.admission_aborted`, `member.cooldown_evidence_unverified`, `member.strict_validation_failed`,
`member.target_phase_precheck_failed`). So a new refusal cannot enter the hazard path without being classed PHYSICS
or NUMBER_INTEGRITY (or INTERNAL, which by definition stops nothing) and saying what it protects.

*What the scan does not see* (its own docstring): a bare `return False` from an admission predicate, a `continue`
that skips a member, and a new call to an existing raising function. Those are checked by hand in review
(`/Users/edr/night-archive/gate-prune/REVIEW_BRIEF_RULE.md`).

*Seal-time item, closed in revision 7.* The test reads this directory's `flag_catalog.json` once it is in the code
tree, and a test added by audit-fix item 7 already reads it from this design branch. Revision 6 found that the file
did not list `roster.run_id_mismatch`, which this catalog marks EXCLUDE_MEMBER (§6.7). The file now lists it as a
NUMBER_INTEGRITY member exclusion ("the member's records disagree about which member it is"), and every excluding
code of this catalog, including the two malformed-flag exclusions of §6.2, is listed (checked by this author against
revision 7's catalog).

## 7. Verdicts, re-arming and END STATE

### 7.1 Four verdicts per attempt

The harvest opens when the driver's terminal record exists (§5.4), works from an archive copy of the window, and
writes one verdict:

- **COLLECTED:** `night/chain.started` exists. The numbers (into restricted custody) and the flags are emitted
  whatever the flags say, and the exclusion function computes `claim_usable`.
- **NULL:** no chain start: the arm refused, or the driver failed before the chain. `claim_usable` is false.
- **NO_COLLECTION:** the chain started but no collection stage ran (for example a stop at exit 10, 11 or 12):
  every collector still runs, `chain.stopped_before_collection` is recorded, and `claim_usable` is false.
- **HARVEST_FAULT:** the harvest program failed on bytes that are present. Cured by R3 and re-harvested from
  identical bytes into a distinct derived directory; never a science outcome.

### 7.2 What happens next

- **The analysed window of each pack is its first claim-usable attempt** in arm order. All of a model's cells come
  from that one window, so attempts are never mixed: no member, quad or cell is pooled, topped up or replaced across
  attempts (D-078).
- A pack is re-armed, with a new attempt number, plan, fresh roots and bracket session, until it has a claim-usable
  attempt; then the next pack in the fixed order ALPHA, BETA, GAMMA arms. A pack is never armed again after a
  claim-usable attempt. The scheduler reads only `claim_usable`, never an energy.
- **Harvest problems first.** When an attempt's only window-removing codes are `*.identity_unmeasured`,
  `whole_window.verdict_absent` or `records.source_changed_during_harvest` (checks that did not run, or ran on moving
  bytes), the cause is the harvest, not the window: R3 and re-harvest on identical bytes before deciding whether to
  re-arm. *Supersession* (PLAN2 row 12): when an arm collector recorded `pack.identity_unmeasured` or
  `code.identity_unmeasured` because it errored or timed out, and the harvest itself re-derived every check that
  collector performs (pack: the pins, the config run ids and the registered digests; checkout: HEAD, tracked edits
  and untracked files under the executed roots; executed code: the executed inventory and the chain sidecar), the
  harvest's own result stands and the arm's flag is moved, whole, into `records.identity_unmeasured_superseded`
  (DISCLOSE). Without this, a collector that errors deterministically would remove every re-armed window. Model
  identity is superseded the same way since Opus audit F5: the arm's model-identity collector has a 55 s budget,
  and a slow one left `model.identity_unmeasured`, which removed the window. Every member's metadata carries the
  content hash of the model tree its own process loaded and its runtime stack, and the harvest compares them with the
  pins (`harvest.model_identity`). When the harvest read the pins and compared the identity of every succeeded science
  member (at least one) with a pin, its own result (a mismatch, or clean) stands and the arm's flag moves into
  `records.identity_unmeasured_superseded`; a science member whose identity cannot be derived keeps the arm's flag
  (`IDENTITY_SUPERSESSION_CHECKS` `model_identity`: `pins`, `members_compared`). Revision 6 said model identity was
  never superseded because the harvest does not re-hash the model files; it still does not, but each member's own
  recorded hash is the evidence the comparison needs.
- **UNCLASSIFIED codes** block only the release event. For scheduling, an attempt with an unclassified code but no
  classified window-removing code counts as claim-usable. The code is classified blind (from its definition and
  emitter, reading no energy) by a cold erratum to the catalog before the release event. If that makes the attempt
  not claim-usable, its pack is re-armed after the packs already scheduled, and the changed order is disclosed.
- **NULL:** re-arm after the named hazard is gone (a contention dwell timeout: identify the process; charging: wait
  for float; the frequency gate: the desk redraw of §3; disk: offload).
- Ed's NO, on the arm notice before each arm, stops that arm.

### 7.3 Anti-spiral routing

Each attempt that is not claim-usable has a **cause key**: the hazard modules that refused (NULL), or the families of
its window-removing codes, or, for `cell.below_minimum`, the families of the member exclusions that removed the
units. When two consecutive attempts of the same pack share a cause key family, the next spend goes to a consult, not
a third arm; the consult may authorize another unchanged attempt, a prospective change (cold erratum), or END STATE.
A consult that cannot settle goes to a cold gate; a cold-gate refusal goes to Ed. None of these is a cap on attempts.

**Process rule for empty and short windows** (PLAN2 §2.2 H; not code). The orchestrator does not arm window N + 1 on
unchanged code when window N's yield status (§5.7) is EMPTY, or LOW with one shared pre-bundle cause
(`stage.members_refused_pre_bundle_identical`, or every lost member of the short stages sharing one cause in the
harvest's `collection.failure_histogram`). It fixes the cause first, by the R3 route. *Why:* a deterministic refusal
repeats identically in every window; under back-to-back cadence each repeat costs a whole arm and chain and teaches
nothing new.

### 7.4 END STATE

Counting across every started attempt of this measurement block: if at least 5 members have a recorded anchor status
and more than half of them are not `bounded`, the clock instrument is failing and re-arming cannot cure it; the
measurement block goes to **END STATE** at once. (A single window meeting the same rule is already `clock.systematic`,
§6.5.) END STATE also follows a cold-gate ruling to stop. At END STATE no further window arms, Ed is emailed, and the
next step is a design record naming the cause, with a consult and a cold gate. Claim-usable windows keep their bytes;
their analysis is fixed in analysis plan §2.3.

### 7.5 A defect found in the middle of the block

**Collection code** is any file in the sealed inventory that executes during a window or changes how a window's bytes
are produced. GAMMA's contrasts are judged against floors from ALPHA and BETA, so all three windows must share one
acceptance, one macOS build and one collection head for the code they executed.

- A cure confined to collection code that no completed window executed (for example GAMMA-only stages) does not
  supersede completed windows; the changed-path map must show that no file executed by a completed window changed,
  and a diff-scoped #416 re-audit covers the change.
- A cure touching collection code that a completed window executed **supersedes the whole block**: completed windows
  are retained and disclosed structurally, their energies are never analysed, a new registration or a cold erratum is
  written, and the block restarts at ALPHA.
- A defect in code that does not run during collection (harvest, extraction, mint, analysis) is cured by R3 and re-run
  on identical bytes; the block continues.
- **Fresh-stream admission retry** (lane L11: restarting the sampler stream for the retry, so a wait between attempts
  fits the clock budget) is an option after ALPHA-1 if its admission aborts cost a cell. It changes collection code,
  so it needs a prospective cold erratum and follows this section.

### 7.6 What re-arming can and cannot select on

`claim_usable` reads no science member's energy except the single pass/fail precheck ratio of §6.3, which is
RESTRICTED. It does read reference-workload energies (the NEG-8 screen), power (idle admission, the bracket), timing,
and the physical hazards. So re-arming cannot select on the science outcome, but every reported number is
**conditional on a window that passed these quiet, timing and drift predicates**, and the analysis plan prints,
beside every reported cell and contrast, the number of attempts of its pack and their causes.

## 8. Blinding

1. **Before seal.** No claim-eligible `_v5` byte exists. This draft's author read none (§16).
2. **During the block.** From ALPHA-1's arm until the block closes (every pack claim-usable, or END STATE), every
   harvest, courier record, email and public summary releases **structure** only: verdicts, `claim_usable`, flag
   counts by code and family, kept-unit counts, paths, hashes, hazard measurements, and timing that is not a phase
   duration (member cycles and cooldown waits are releasable). **Restricted:** energies, powers, phase durations,
   floor values, reported means, dominance ratios, calibration numeric diagnostics, any pass/fail derived from a
   science energy, and every flag whose `blinding` is RESTRICTED. A member removed by a RESTRICTED code is released as
   "removed (restricted code)", without the code. The driver's courier for `HAZARD_PACK` sends structure only: no
   chain or campaign logs, no runs-root files. `FILL[B5-BLIND-CUSTODY-MAP]` lists the restricted paths.
3. **Unblinding.** After the block closes and the blind dry run of analysis plan §3.2 has completed, the lead records
   a **release event** tying the sealed SHA-256s of this file, the analysis plan and the catalog to the final harvest
   records (`FILL[B5-RELEASE-EVENT]`); the analysis then runs exactly as registered. Analyses not registered are
   labelled exploratory.

## 9. Directive gates

### 9.1 #416: pre-arm triple audit

Once at H_claim, after the seal and before ALPHA-1 arms: a blind full-system audit by three independent model
families, findings cross-verified, BLOCKERs challenged by a refuter from another family and cleared before arm.
Seats: `FILL[416-SEATS]`. It runs once per frozen code or protocol change, never per window; a later change to
collection code (§7.5) triggers a diff-scoped re-audit of that change. No audit work runs during a window.

### 9.2 #421: battery float, and the battery-assist ruling of 2026-10-06

**What #421 asked for.** Ed's directive #421 (2026-09-25) made the battery's state mandatory evidence for every
capture: a number taken while the battery was charging, or while the machine was not drawing everything from the
adapter, should not stand unexamined. Its motivating hazards were two. *Charging heat:* a change of the battery's
charge limit from 80% to 100% would start a long charge, warming the battery and adding load beside the workload.
*An incomplete wall reading:* a wall or USB-C meter on the adapter does not see energy the battery supplies, so the
machine's total energy cannot be read from the adapter side alone while the battery helps.

**What changed, and why.** Until 2026-10-06 any discharge above 200 mA in a member's span removed the member. Two
measurements on 2026-10-06 showed that this rule had been reading a 60 s snapshot (§4.2) and that the battery
assists under heavy load on the 140 W adapter: B0AC was nonzero in 126 of 170 s under an 8B-plus-CPU-burner load,
down to −5,331 mA. Under the old rule switched to the 1 s SMC reads, the heaviest members, most of all 8B
prefill-p2048, would be removed in numbers. Ed, 2026-10-06: "'under the existing rule' - should not preclude you from
sensible changes - if the science is improved by a new rule make a new rule or remove the old one - obviously this
needs to be durably remedied" (doctrine item 7 in the ruling). Two blind council seats (Opus 5.5 and Sol 6.1 xhigh)
agreed; the orchestrator ruled
(`/Users/edr/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md`):

1. *The rail number does not depend on the source.* The processor rails are regulated downstream of the supply, so
   the rail energy the sampler reports is the same whether the adapter or the battery delivered it.
2. *Excluding assisted members would bias the result.* Assist happens when the load is highest, so removing those
   members selects members by load and pulls the kept means down, most of all for 8B.
3. *The evidence on hand is benign.* Qwen3-8B decode ran at 69.1–72.6 tokens/s under up to −5.3 A of assist against
   68.9–71.1 tokens/s without it. (The −865 mA reading of the earlier probe was at model load, not during decode.)
4. *#421's two hazards stay covered.* Charging (current above +200 mA, IsCharging, the charge accumulator) and loss
   of AC power still remove the member (§6.4), and the arm still refuses any battery current at idle (§4.2). The
   wall-reading gap is closed by adding the battery term explicitly to the whole-machine energy (§5.8).

So discharge with the adapter connected is disclosed (`battery.assist`), with its counts, minimum, duration and
discharged energy per phase, and every reported cell is printed both with and without the members that carry it
(analysis plan §8.1); neither value is chosen after the fact. The same disposition applies to calibration captures,
to the #421 endpoint pairs and to the accumulator bounds (§6.3, §6.5): a discharge-only failure is disclosed; charging
or AC loss keeps its exclusion. At `a434e363d` no rule removes a member or a window for discharge as such. One case
keeps a pair exclusion: a #421 pair that failed on discharge alone is disclosed only when the SMC reads cover the
span, because only then can the journal show that the span held no charging; without SMC coverage the pair's
exclusion stands, as missing evidence, not as discharge.

**What would reopen the ruling** (by erratum to an exclusion scoped to the affected phase): power-mode or power-limit
transitions that reproducibly accompany assist; lower rail power, frequency or tokens per second in assisted seconds
against matched unassisted seconds; or a battery-temperature rise concentrated in assisted stages (§0.6). GAMMA's 8B
members and the battery-temperature diagnostic are where this is watched. No qualification run is required before
the seal, because the rule does not depend on how often assist occurs.

**Records kept.** Every capture's raw pre/post `ioreg` pair is kept as data and authenticated at harvest; a missing
pair is disclosed. The registry's 60 s snapshot limitation of revision 4 no longer limits the current rule, which
reads the SMC once a second; the registry still supplies the charging and AC state, polled every 5 s.

## 10. Changes after the seal, and registered deviations

None to §§3–9 for an armed or completed attempt. A rule, threshold, catalog effect, roster or blinding change is a
prospective cold erratum (one judge, one refuter), settled in one erratum. The §5.5 resizing rule and the §3
frequency redraw need no erratum. A review finding that concerns only how something is recorded (receipts, naming,
schema formality) is dispositioned "flag, not refuse" and never sent to a fix round.

**Registered deviations from committed bytes, made prospectively here:**

1. The chain passes `--max-failures <expected_count>` in place of the packs' literal `1` (§5.2).
2. The plan trees' `attempt_policy` is superseded by the flag catalog (§5.2).
3. The NEG-8 bound may be derived from 10 or 11 corpus members (§5.3).
4. Analysis: D-179 ruling 1 ("no member is excluded after collection"; no reduced mean) and D-078's no-reduced-mean
   text are amended by §6.6 and analysis plan §2.2 and §4, as Ed's 2026-10-05 ruling requires; GAMMA's prospective
   manifest's fixed n = 10 quads becomes "at least 8 kept quads" (analysis plan §7).
5. The chain passes `--arm-countdown-s 0` on every collection stage and on the pre calibration slot in place of the
   packs' literal 20; the post calibration slot keeps 20 s (§5.1).

The chain's other changes of round 2 (the 60 s settles, the window calibration verdict, the wall budgets, the
collection deadline, the corpus retry) and the spare-slot retry of revision 7 are not deviations from pack bytes: they
are the chain's own steps, listed in `joulewise/b5/chain.py` `DEVIATIONS` and registered in §5.1, §0.6 and §0.12. The
spare members themselves are committed bytes that each pack's plan tree pins (§0.12).

## 11. Commit rule and the sealed inventory

1. **H_claim** is the commit of §2 item 1. It is extended only by (i) pin-only commits from this block's pin advances
   (§4.6 item 6),
   shown by a `git diff --name-only` map against H_claim that names only `configs/calibration/calibration_ledger_head.json`;
   (ii) gated R3 fixes to code that does not run during collection; (iii) commits touching only `docs/`, `tests/`,
   `RUN_STATE.md` or `TASK_QUEUE.md`; (iv) a §7.5 cure confined to collection code no completed window executed.
   Each extension carries its changed-path map, checked before the next arm.
2. **The sealed inventory** (`sealed_inventory.json`) lists, at H_claim, the SHA-256 of every tracked file under
   `joulewise/`, `scripts/` and the three pack directories, and names H_claim as its `head`. It does not list the
   ledger pin (data). It covers the hazard path: `joulewise/hazards/*`, `joulewise/b5/{driver,plan,chain}.py`,
   `joulewise/window_lineage.py`, `joulewise/flags/*`, `scripts/run_night.py`, `scripts/hazard_monitor.py`,
   `scripts/write_b5_window_plan.py`, `scripts/run_campaign.py` and the measurement core, and this directory's
   `flag_catalog.json`. This directory's `identity_pins.json` and `sizing_b5.json` are pinned by the seal record
   (§12). A window's executed-file inventory covers `joulewise/`, `scripts/` and only its own pack, so
   the comparison is made over the sealed entries under those roots (§14 Q2).
3. **Retired, not deleted.** The `TRANSACTION_PACK` route (ARM, GO, consumption and lifecycle in
   `joulewise/arm_readiness.py`, except the lineage helpers the hazard lineage dispatches through;
   `arm_readiness_evidence.py`, `arm_readiness_evidence_t0.py`; `scripts/capture_t0_step.py`,
   `author_arm_evidence_t0.py`, `author_arm_readiness_evidence.py`, `generate_arm_readiness.py`,
   `launch_window.py`; the network-time OFF receipt admission and `joulewise/dwell.py`) and the block-4 machinery stay
   in the tree with their tests green. Block 5 never runs them, and an import-graph test proves the hazard path cannot
   reach them. Their deletion is proposed to Ed after GAMMA's harvest under the pruning rule.
4. **Written blind, pinned before use.** The harvest program (L5) is pinned by an addendum to the seal record before
   ALPHA-1's harvest; the analysis code (L9) before the release event (analysis plan §11). Each addendum names the
   files and their SHA-256s and is written by a seat that has read no claim-window energy.
5. **Records of their era are not live pins.** Two older documents carry digests of files as they were when the
   documents were written: revision 6 of the calibration preregistration
   (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, sealed 2026-09-30 at `46643f1d`) records
   `pins.validator_sha256` (`3dc75857…`), the calibration writer that produced block 1's derivation captures; and
   block 4's sizing source (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, `head`
   `bda1c180`) records the production files it sized from. Those files have changed since, as the gate-prune lanes
   required, so the digests no longer match today's tree, and they are not meant to: they say what ran then. The
   digest census (`scripts/digest_pin_census.py`, `ERA_RECORDS`) resolves each such digest against the file at the
   document's declared commit with `git show`, and the documents are not edited. Revision 6's
   `estimator_code_sha256` pins stay live, because the acceptance re-derives them. **The live pins of block 5 are the
   sealed inventory at H_claim** (item 2): a window is judged against the files H_claim holds, never against an era
   record.

## 12. Seal

One cold gate seals this file, the analysis plan, the flag catalog and the sealed inventory together: a Fable 5.1
judge and one Opus 5.5 refuter (`FILL[B5-SEAL-SEATS]` records the seats used). The seal record `FILL[B5-SEAL-RECORD]`
pins, with SHA-256s at H_claim: the four documents; H_claim; the three packs' plan trees; the panel, policy,
acceptance and pin bundle; the sizing output `sizing_b5.json` (§5.5) and the identity pins `identity_pins.json`
(§4.6 item 3); and the chain-source document
`docs/phase_2/window_runbook.md` (the chain embeds its pre-calibration screen). The gate rules in particular on the
cell rule of §6.6, the catalog's effects (especially the two disclosed aggregate codes of §6.5), and the proposed
sensitivity line of analysis plan §8.

## 13. Binding register

| Binding | FILL | Due |
|---|---|---|
| Commit | `H-CLAIM` | Seal |
| Sealed inventory | `sealed_inventory.json` filled at H_claim | Seal |
| Dry render, dry arm | `B5-DRY-RENDER-RECORD`, `B5-DRY-ARM-RECORD` | Before ALPHA-1 arms |
| Audit, seats | `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS` | Seats at seal; audit before ALPHA-1 |
| Sizing | `B5-SIZING-OUTPUTS`: draft values at the int5 head `d3c107f2f` (§5.5), spares included; pinned at H_claim | Seal |
| Cooldown smoke | `B5-COOLDOWN-SMOKE-RECORD` (§2 item 7): filled in revision 6 | Seal |
| Plans | `B5-PLANS-REGENERATED`: every window plan and plan-input file written from the sealed §4.3 block (contention `clean_s` 180) | Before ALPHA-1 arms |
| P3 sync | `P3-SYNC-RECORD` (§2 item 8), with `P3-BATTERY-CODES` (§6.4, and the table below) and `P3-CLOCK-SKEW-BOUND` (§4.2): filled in revision 6 against `a434e363d`; the revision 7 sync record below covers the code merged since, against `d3c107f2f` | Seal |
| Final hashes | `B5-FINAL-HASHES`: every digest computed at `d3c107f2f` and so marked (§0.7 plan trees, §2 item 1 candidate head, §4.6 item 3 identity pins, §5.5 sizing output) is recomputed at the integration's final head (`/Users/edr/night-archive/gate-prune/FROZEN_HEAD_2.md` when it exists) | Seal |
| Refusal allowlist | `roster.run_id_mismatch` listed under the member exclusions of `configs/gates/hazard_refusals.json` (§6.11): done at `d3c107f2f` (audit-fix item 7) | Seal |
| Disk | `BACKUP-DESTINATIONS`: filled in revision 4 (§5.6) | Seal |
| Identity pins | `identity_pins.json` (§4.6 item 3): draft at `d3c107f2f`, spares included; pinned at H_claim | Seal |
| Blinding | `B5-BLIND-CUSTODY-MAP`, `B5-RELEASE-EVENT` | Map at seal; release after the block closes |
| Boundary | `BOUNDARY-LABEL`: filled in revision 4 (§1) | Seal |
| Attribution floor | `ATTRIBUTION-FLOOR-BINDING` | Seal |
| Seal | `B5-SEAL-RECORD` | Seal |

Still open after revision 7: `H-CLAIM` (the candidate is the final int5 head, `d3c107f2f` at this writing, §2 item 1),
`B5-FINAL-HASHES`, `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS`, `B5-SEAL-RECORD`, `B5-DRY-RENDER-RECORD`,
`B5-DRY-ARM-RECORD`, `B5-BLIND-CUSTODY-MAP`, `B5-RELEASE-EVENT`, `ATTRIBUTION-FLOOR-BINDING`, `B5-PLANS-REGENERATED`,
and the sealed inventory itself. None can be filled from committed bytes: each names a commit, a record, a ruling or
a regeneration that does not exist yet (`B5-FINAL-HASHES` waits for the integration's final head).
`B5-SIZING-OUTPUTS` and the identity pins hold draft values. Filled in revision 6: `B5-COOLDOWN-SMOKE-RECORD`,
`P3-SYNC-RECORD`, `P3-BATTERY-CODES`, `P3-CLOCK-SKEW-BOUND`. Closed in revision 7: the refusal-allowlist item.

**P3 sync record** (`P3-SYNC-RECORD`, revision 6). Revision 5 described the behaviour below from the rulings, before
the code had it. Each row was read in the frozen head `a434e363d` (`/Users/edr/code/JouleWise-wt-int4`); the last
column says whether the code matched revision 5's text or the text was changed to match the code.

| Sync point | Code at `a434e363d` | Text |
|---|---|---|
| battery member rule on SMC 1 s reads, assist disclosed, the codes for each predicate (`P3-BATTERY-CODES`) | `harvest.battery_join`, `_battery_assist`, `accumulator_member_flags`. The codes: `battery.member_span` (a charging current; charging or AC lost), `battery.accumulator_excursion` (the charge accumulator; a sign-inconsistent discharge accumulator), `battery.unmeasured` (missing state evidence, including the 120 s state hole under SMC coverage), `battery.smc_unavailable`, `battery.assist` and `battery.assist_outside_request` (any negative read; −200 mA is the report's threshold), `battery.accumulator_activity`, `battery.accumulator_unavailable` | changed: §6.4 rewritten (any negative read; the code's three phases; the excursion code; the state hole; the energy as held time × power) |
| capture battery join on SMC reads; assist for captures and #421 pairs | `harvest._capture_battery_joins`, `_pair_assist`: `calibration.capture_battery_span`, `_unmeasured`, `_assist`, `_pair_assist`; `battery.capture_pair_assist` | changed: §6.3, §6.5 (capture assist has its own code; pair assist needs SMC coverage) |
| monitor and meter stopped no sooner than 5 s after the chain exits | `driver.MONITOR_POST_CHAIN_HOLD_S` = 5.0, `hold_monitors_after_chain`, after G10 | changed: §5.4 order (G10 before the stop) |
| clock samples with a large read skew re-read, then unmeasured, never a step (`P3-CLOCK-SKEW-BOUND`) | `clock.window_skew_max_ns` = step ÷ 4 = 250 µs, `ANCHOR_TRIES` = 5; harvest `_clock_point` applies the same bound | filled: §4.2 |
| meter driver wiring and harvest hook; restricted record; `meter.*` flags | `MonitorSupervisor` named `meter`, no restart on a clean exit; `meter.supervision_fault`; `harvest.meter_joins` | changed: §5.8 (one file `withheld/meter.json`; the request window only, no phases) |
| historical custody re-verified at harvest; the unmeasured code's name | `harvest.historical_custody`; scoped to the acceptance's captures (triage d) | changed: §6.10 (scope; `_mismatch_unused`; class NUMBER) |
| harvest drop reasons imported from the mint's set | imported from `whole_window.NEG8_MINT_DROP_REASONS` | matched: §5.3 |
| terminal ledger pin handed to the desk verdict | the committed pin must already be this session's terminal entry (`harvest._desk_pin_problem`), so the desk order is chain exit, pin advance, harvest | changed: §2, §4.6 item 6 (pin advance before the harvest) |
| member error-output files scanned for unwritten flags | `harvest._unwritten_core_flags` scans `operator-logs/member-stderr/` | matched: §6.10 |
| yield alerts queued by the watchdog | `magistrate_watchdog.queue_yield_alerts` | matched: §5.7 |
| `member.whole_window_member_failure` emitted | `harvest.whole_window_member_failures`; plus `whole_window.member_failures_unreadable` (P4) | matched: §6.3; new code in §6.5 |

**Catalog comparison** (revision 6). A script read, from `a434e363d`, every code named by the harvest's `CODES`
table, `joulewise.flags.catalog.DRAFT_CODES`, `joulewise.flags.core.CORE_FLAG_CODES`, `km003c_parse.CODES`,
`window_lineage.FINDING_CODES` and the literal codes of `joulewise/hazards/monitor.py`, plus the test fixture catalog
`tests/fixtures/b5_harvest/flag_catalog.json`, and compared each with this directory's catalog (family, class,
effect, blinding), then loaded the catalog with `joulewise.flags.catalog.load_catalog`. Before revision 6 (catalog at
commit `f3473b7a`): every emitted code was present, and one disagreement was not documented,
`calibration.historical_custody_unmeasured` classed REPRESENTATION here and NUMBER in the code. After: 178 codes,
none missing, none extra, the two never-classified codes absent, and four documented disagreements only:
`roster.run_id_mismatch` restated NUMBER and EXCLUDE_MEMBER here (§6.7) against the emitter's REPRESENTATION and the
fixture's DISCLOSE, and `g3.recompute_failed`, which the fixture keeps at its earlier effect EXCLUDE_WINDOW
(`tests/fixtures/b5_harvest/README.md`) against DISCLOSE here (§6.5).

**Revision 7 sync record** (`B5-REV7-SYNC`). The source list of required changes was the integration's REG list
(`/Users/edr/night-archive/gate-prune/REG_PENDING.md`: fix lane 2, fix lane 1, the NEG-8 lane) and the NEG-8 ruling.
Each row was read in the int5 head `d3c107f2f` (a read-only shared clone at `/private/tmp/regsync2/repo`, detached at
that commit); the last column says where the text changed, or that it already matched.

| Sync point | Code at `d3c107f2f` | Text |
|---|---|---|
| NEG-8 screen on the survivors; count-adjusted bound | `whole_window.evaluate_neg8_point_drift` (endpoint counts 2–3, midpoint 0–1, protocols `replicated_endpoints_with_midpoint` and `replicated_endpoints`), `neg8_count_adjusted_bound`, `neg8_family_endpoint_bound`; the verdict writer drops status losses (`run_campaign._idle_admission_core_evaluation`); the harvest drops flag losses and discloses (`neg8_screen`, `_neg8_rescreen`, `_neg8_disclose`) | changed: §0.12 (the ruling's text, adapted where the code differs: the retry runs after the 60 s settle; the flag names the record holding the bound instead of carrying it; `neg8.reference_lost` only below (3, 1, 3)), §5.3, §6.5 |
| spare-slot retry | `chain.spare_retry_lines`, `SPARE_RETRY_HELPER`, wall budget `neg8_spare_retry_decision` 300 s, horizon allowance 60 + 180 + 620 × k s; spares in `configs/campaigns/window_reference_spares_v5/`, pinned by each reference stage's `spare_retry` record | changed: §0.12, §5.1, §10 |
| corpus members dropped for physics | `harvest.neg8_corpus_physics` (`derived/neg8-clean-corpus.json`, `withheld/neg8-clean-bound.json`, `derived/neg8-corpus-physics.json`) | changed: §5.3 |
| yield minimums of the reference stages | `driver.REFERENCE_ENDPOINT_MIN_VALID` = 2, `REFERENCE_MIDPOINT_MIN_VALID` = 0; the harvest counts a spare only when it ran | changed: §5.7 |
| sizing and disk for the spares | `size_b5_window` `reference_spare_retry_s` = 5,424 s per pack; `plan.py` planned bytes include the 7 spares | changed: §4.2, §4.3, §5.5 |
| UNMEASURED at the arm | `hazards/arm.py`, `driver.normalize_decision`; `<module>.arm_unmeasured` | changed: §0.15, §4.1 |
| agent census | `agent_identity.filter_census` at every census site; in-window `census.unmeasured` never stops | changed: §4.5, §5.1, §5.7 |
| lineage publication | `driver.run_hazard_night`: `night_refused_pack_inventory_unusable`; `observed.science_members_expected_to_refuse` | changed: §0.17, §6.11 |
| desk identity files at the reservation | `reserve_calibration_window_bracket._hazard_desk_object`, kind `desk_identity_unreadable` | changed: §6.10 |
| malformed and unbuilt flag lines | `harvest._malformed_flag_line`, `_rebuild_unbuilt_flag`, `_unwritten_core_flags`; `NEVER_CLASSIFIED_CODES` empty | changed: §6.2, §6.10 |
| registry start time; torn lock | `measurement_liveness.publish_campaign`; runner kinds `registry_start_time_unavailable`, `torn_lock_cleared` | changed: §6.10 |
| powermetrics digest | harvest step `binary_identity`, `instrument.binary_identity_rederived` | changed: §6.3, §6.10 |
| monitor restarts; orphan groups | `MonitorSupervisor` `on_restart` writes `monitor.restarted`; `reap_orphan_monitor` writes `monitor.orphan_unverified` | changed: §5.4, §6.8 |
| sign-inconsistent discharge accumulator | `harvest.accumulator_member_flags(smc_covered=…)` and `hazards/battery.py`, in parity | changed: §6.4 |
| monitor skew bound | `hazards/monitor.build_config(clock_step_ns)` from the plan | changed: §4.2 |
| post-run guard collector exception | `environment_admission.post_run_observation_collector_raised`, read on the verdict path only (`e0a71cc2f`); the reducer unchanged | changed: §6.3, §6.10 |
| G10 | `driver._run_g10`, `_wait_supervised`, `G10_POLL_S` = 5 under the 1,500 s cap | changed: §3, §5.4 |
| desk pin order | `harvest._desk_pin_problem` kept; `whole_window.verdict_absent` relabelled NUMBER_INTEGRITY in the allowlist | matched: §2; changed: §6.11 |
| model identity supersession | `IDENTITY_SUPERSESSION_CHECKS["model_identity"]` = {`pins`, `members_compared`} | changed: §7.2 |
| OS metadata files in sources | the three source comparisons ignore `.DS_Store`, `.localized`, `._*` | changed: §6.5 |
| member flags scoped by bundle id | `exclusions.compute` resolves bundle ids through the roster | changed: §0.16 |
| `roster.run_id_mismatch` in the allowlist | listed, NUMBER_INTEGRITY; emitter and fixture NUMBER and EXCLUDE_MEMBER | changed: §6.7, §6.11 |

**Catalog comparison** (revision 7). The same script as revision 6, adapted to import the int5 head
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/0a4039c8-3a55-4151-82ba-e66d8a0e9397/scratchpad/regsync7/check_catalog.py`),
read every code named by those tables at `d3c107f2f`, compared each with this directory's catalog, checked that
the superseded A1 window-exclusion code appears in none of them, and loaded the catalog with `load_catalog`. Before revision 7
(catalog at `c6843537`, 178 codes): 14 codes the code emits were missing (the five `*.arm_unmeasured`,
`monitor.orphan_unverified`, `records.malformed_flag`, the two malformed-flag exclusions, `records.flag_unbuilt`,
`records.operator_log_unreadable`, `instrument.binary_identity_rederived`, `neg8.reference_lost`,
`neg8.midpoint_lost`), and the same 14 were in the test fixture but not here; 28 open disagreements in all. After: 192
codes, none missing, none extra, `collector.unmeasured` deliberately absent (§6.2), `load_catalog` OK, and one
documented disagreement only: `g3.recompute_failed`, which the fixture keeps at its earlier effect EXCLUDE_WINDOW
(`tests/fixtures/b5_harvest/README.md`) against DISCLOSE here (§6.5). The `roster.run_id_mismatch` restatement of
revision 6 is gone, because the emitter and the fixture now agree with the catalog.

Removed from revision 2 because the mechanism they bound is retired or now measured: `V5-PACK-REGEN-RECORD` and
`V5-IDLE-SECONDS` (done, PR #481), `B4-*`, `L10-A-RATIFICATION-RECORD`, `Q110-CLOSURE`, `A6-AT-H-CLAIM`,
`V5-TRANSACTION-GO-01-DISCHARGE`, `AUTH-<label>`, `CAMPAIGN-PERMITTED-BLOCKS`, `STEP6-RECORD`, `CENSUS-ARGV` (§4.5),
`ANCHOR-RUNTIME-EFFECT` (either way the member is removed), `HARVEST-OPEN-RULE` (§5.4), `CLAIM-CHAIN-SUCCESS-RC`
(§7.1), `CLAIM-HARVEST-CLI` (`scripts/harvest_b5_window.py`), `G3-CLAIM-ARGS` (the harvest runs G3 on GAMMA; floor
packs have no analysis manifest), `ED-PREDICATE` and `ED-DISPOSITION` (§6.4 contention), `SPOTLIGHT-EXCLUSION` and
the disk ledger FILLs (measured by the contention and disk hazards), `B5-ATTEMPT-BUDGET` (attempts are planned, never
capped), `LONGEST-STREAM-SIZING`, `SHORTEST-STREAM-SIZING`, `REF-STREAM-FLOOR` (T_stream_max is committed; the
576 idle records give about 75 s of idle stream at the observed cadence, and at least 57.6 s even if every record
took only the requested 100 ms; every member then adds its warm-up and request, at least 117 more records in block 3,
so each stream exceeds the 60 s minimum of the clock fit), `COURIER-BLINDNESS-CAMPAIGN` (§8 item 2), and the
battery evidence map (§9.2).

## 14. Open questions (each names where it goes)

- **Q1. NEG-8 corpus of 10 or 11. Closed in revision 4.** It was settled by the harvest-side derivation from
  custodied bytes, with the core untouched (fix lane fx-harvest, §5.3).
- **Q2. Sealed-inventory comparison scope. Closed in revision 4.** At `f8164893` the arm's executed-code collector
  (`joulewise/flags/collect.py`, `_window_scope`) and the harvest (`code_identity`) count missing and added files only
  under the window's own roots, so the other two packs' sealed files are not read as missing.
- **Q3. Contention false flags (after ALPHA-1; cold erratum if needed).** "Any outside process above 5% of one core"
  has never been applied to every process on this Mac during a window. If ALPHA-1's flag rate costs cells, a
  prospective erratum retunes the predicate from flag rates, which are structure, not energies. A repeat goes to a
  consult (§7.3).
- **Q4. Paper placement (cold gate, ideally before seal).** D-174's fallback places no `_v5` result; printing needs an
  adoption ruling.
- **Q5. Attribution floor (lead, before seal).** Bind the ~1 J value and artifact, and rule whether D-078's derivation
  applies on 25G83.
- **Q6. The sensitivity line (seal gate).** Analysis plan §8.1 proposes a labelled line over all members removed
  only by physics-in-span codes, to expose the bias that such exclusions can introduce (thermal pressure and
  contention plausibly correlate with load, most of all on 8B prefill-p2048 members). Adopt or strike. Battery assist
  no longer belongs here: it is disclosed, and its own two-way line is registered (§9.2, analysis plan §8.1).
- **Q7. Ed's hardware setting (optional).** A fixed 80% charge limit with Optimized Battery Charging off avoids arms
  refused because the OS chose to charge.
- **Q8. The watchdog held each window open until its deadline. Closed in revision 5.** The watchdog now releases a
  finished window on its terminal evidence (§5.4; P2-WD, at `a434e363d`).
- **Q9. The battery-assist line for GAMMA's contrasts. Closed in revision 6: adopted.** The ruling of 2026-10-06
  prints every reported cell with and without assisted members (analysis plan §8.1). GAMMA's contrasts are not
  reported cells (§0.9), and 8B members, one side of every quad, are the ones that assist most. The orchestrator
  ruled on revision 5's open points (2026-10-06, `/Users/edr/night-archive/gate-prune/INTEGRATION_TODO.md`): GAMMA's
  contrasts get the line too, because 8B is where assist occurs. Analysis plan §8.1 now prints each contrast's
  estimate also without the quads that hold an assist member. The line is descriptive and gates nothing; the seal
  gate may still strike it.
- **Q10. Whole-machine meter, central band (none; recorded).** The band for ρ is set by the first clean window
  (analysis plan §8.2). If no window of the block is clean, no band is set, and the cross-check reports only the hard
  plausibility band and the spreads. Nothing waits on this.
- **Q11. A GAMMA attempt whose midpoint was lost (orchestrator before the seal; the seal gate rules).** The NEG-8
  ruling makes `neg8.midpoint_lost` DISCLOSE in the catalog and claim-excluding for the primary contrasts in the
  analysis plan (§0.12; analysis plan §2.4). The scheduler reads only `claim_usable` (§7.2), so a GAMMA attempt that
  is claim-usable but lost its midpoint ends the block's GAMMA arms, and the paper then has no claim-bearing contrast.
  The ruling did not say whether such an attempt should instead count as not claim-usable for GAMMA's scheduling, so
  that GAMMA is re-armed. Either answer reads no energy. The midpoint is lost when it and its one spare both fail at
  run time, which at the recorded 1-in-37 loss rate is about (1/37)² ≈ 0.07% of windows, or when a physics flag found
  at harvest contaminates it (no spare runs then), for which the block has no rate yet. Until ruled, the text above
  stands: GAMMA is not re-armed.

## 15. Where each gate-prune change lives

| Plan §6 item | Change | Here |
|---|---|---|
| 1 | Network time OFF as an action; no wording check; ONs only at G10 and the redraw | §4.4, §3 |
| 2 | Clock gate 3.7 ms + (\|f\| + 0.25 ppm) × 335 s ≤ 5 ms; dwell linearity ±1 ms; 1 ms step; per-member 5 ms bound authoritative | §0.14, §4.2, §6.4 |
| 3 | Idle admission unchanged; `member.admission_aborted` removes the member; stage continues; L11 option | §0.13, §6.3, §5.2, §7.5 |
| 4 | Battery: arm check, 5 s journal, 60 s publication, in-force rule, accumulator rule with units, unmeasured, pairs as data, measured limitation (revision 5: current from the SMC at 1 s; assist disclosed, §9.2) | §4.2, §6.4, §9.2 |
| 5 | Census kept; contention measured directly; load average and name lists recorded only | §4.5, §4.2, §6.4 |
| 6 | Disk arm rule and in-window stop; dwell replaces `prewindow_check.sh` | §4.2, §4.1 |
| 7 | Thermal (OS level and powermetrics); instrument cadence probe | §4.2, §6.4 |
| 8 | Ledger seed at pin 402 at the default path; readiness and abort before each arm | §4.6 item 6 |
| 9 | Validity becomes the catalog; COLLECTED, NULL, HARVEST_FAULT; re-arm until claim-usable; anti-spiral by family; END STATE from flags; §7.4 kept | §6, §7 |
| 10 | Preconditions deleted and kept | §2 |
| 11 | Harvest at chain exit; next arm reads only `claim_usable`; block time recomputed | §5.4, §7.2, §5.5 |
| 12 | Blinding unchanged; flag `blinding` governs release; courier structure only | §8 |
| 13 | H_claim, sealed inventory, pin-only commits, L5 and L9 pinned by addenda | §11 |
| 14 | `attempt_policy` superseded; `--max-failures` override as a registered deviation | §5.2, §10 |
| 15 | Analysis plan amendments | analysis plan §1, §2.2, §4, §5, §7, §8, §11 |

## 16. What the author read

For revision 3: Ed's ruling in `CLAUDE.local.md`; the gate-prune plan and its inventory
(`/Users/edr/night-archive/gate-prune/`); the code of lanes L1–L5 and L8 in their worktrees (hazard modules and
thresholds, the driver, plan writer and chain writer, the hazard lineage, the flag package and its draft catalog, the
harvest's code table, G10); at the integration head `a0a4f5a7`: the packs' plan trees (stage graphs, attempt
policies, identity pins, idle seconds), the production policy, the acceptance and ledger pin digests, the committed
sizing source, `kernel_clock.py`, `whole_window.py`'s verdict conditions, `check_window_provenance.py`'s F5-2 check,
the floor functions and the t table (to compute the synthetic worked examples of the analysis plan); and the
pre-mortem memo `/Users/edr/night-archive/ia-0a40/MEMO.md`. No energy or power value of any block was read, and no
`_v5` claim byte exists. Revision 2's reading record and its disposition of three blind critiques are in commit
`bfd1ee8c` (this file's §16 and the analysis plan's §14 there).

For revision 4, the author read the code at the gate-prune integration head `f8164893`
(`/Users/edr/code/JouleWise-wt-gp-int`):
- the harvest's code table, NEG-8 bound check, re-screen, calibration, roster, member and model-identity steps;
- the flag catalog loader and the harvest's test catalog;
- the battery, thermal, clock and contention span joins, and the disk targets;
- the model-identity collector and `identity_pins.json`;
- `scripts/size_b5_window.py`, `sizing_b5.json` (re-derived with `--check`) and block 4's sizing source;
- the plan writer's inputs, the driver's deadline, and the watchdog's plan-span rule;
- the whole-window verdict writer's per-member failure reasons and `joulewise/environment_admission.py`;
- the ledger snapshot loader and the bracket evaluation's use of it;
- the boundary fields of the powermetrics adapter, the floor packs' extraction specs, decision D-078 item 4, and
  the backup convention of `docs/phase_2/window_runbook.md`.

The author also read the block-3 timing summary that §5.5 cites (scratch `sizing_v2.json`, member-cycle timing
only). The catalog was validated with `joulewise.flags.catalog.load_catalog`. No energy or power value was read.

For the timing edits of revision 4 (item 6 of "What changed in revision 4"), the author read the cold-judge ruling
and the two council reports it judged (`/Users/edr/night-archive/gate-prune/timing/`: the ruling, `council-sol.md`,
`council-opus/council_opus_summary.json`, `timing_analysis.json`); the adapter's record-count rule
(`powermetrics.py` `_idle_count`), the controller's cooldown release loop, the clock fit's 60 s minimum
(`uncertainty_evidence.py` `MIN_RATE_FIT_BASELINE_S`) and the idle trace's three-bandwidth rule
(`idle_dependence.py`); and, from block 3's 37 idle captures, the record durations only, to choose 576 records.
The block-3 power figures quoted in §0.3 and §0.6 are the ruling's and the councils' (block 3 is not a claim
window). No `_v5` claim byte exists.

For revision 5, the author read: the orchestrator's integration list (`/Users/edr/night-archive/gate-prune/
INTEGRATION_TODO.md`); PLAN2 (`prune2/PLAN2.md`, §2.2 and §3.1) and the round-2 lane results (`prune2/P2_RESULTS.md`);
the timing ruling; the battery-assist ruling, the B0AC validation and the meter wiring note
(`/Users/edr/night-archive/wallmeter-probe/`); lane L10's registration erratum; the core-prune design
(`core-prune/DESIGN.md` §3, §5, §7); and the P3 lane briefs. At the integration head `b9d02700a`
(`/Users/edr/code/JouleWise-wt-int3`) it read: the battery hazard module's SMC sources and arm rule; the harvest's
battery member rule, capture join, code table, threshold parser, desk-verdict timeout, identity supersession and
yield summary; `whole_window.py`'s NEG-8 drop verdicts, physical freshness times and disclosed binding changes; the
runner's member cap, strict-validation deferral, cooldown fallback and thermistor reading; the chain's deviations,
wall budgets, collection deadline and corpus retry; the driver's yield plan, counting and terminal verdicts; the
watchdog's leads and release; the contention module's dwell; G10's settle; the arm's identity read; the reservation's
and writer's record kinds; `km003c_parse.py`; `sizing_b5.json` (its totals and conventions) and the scratch sizing
source of §5.5; and the digest census's era records. It compared every code the harvest, the draft vocabulary and
the core table name with the catalog (§13 lists the one code the catalog has and the harvest does not yet emit). No
energy or power value of any window was read; the power figures quoted are the validation runs' and the rulings'.

For revision 6, the author read: the integration list's REG items and the frozen-head record
(`/Users/edr/night-archive/gate-prune/INTEGRATION_TODO.md`, `FROZEN_HEAD.md`); the battery-assist ruling, the meter
wiring note, the timing ruling and lane L10's erratum (all already applied in revision 5, re-checked); the cooldown
smoke's run-4 directory (the join-check record, and the SHA-256 of the four evidence files, computed). At the frozen
head `a434e363d` (`/Users/edr/code/JouleWise-wt-int4`, read only) it read, directly or through three read-only
investigation seats whose citations it spot-checked: the harvest's battery join, assist rule, accumulator rule,
capture join and pair replacement, member spans, meter join, historical custody pass, desk-pin guard and verdict
handling, unwritten-flag scan, drop-reason import and G3 condition; `joulewise/hazards/battery.py` and `clock.py`;
the driver's lineage check, monitor and meter supervision and tail order; the watchdog's leads and yield-alert reader;
`scripts/advance_b5_ledger_pin.py`; the controller's guard-collector wrapper; `whole_window.py`'s change since
`b9d02700a`; the chain's constants; the refusal allowlist and its test (counts recomputed); `sizing_b5.json`
(re-derived with `--check`) and `identity_pins.json` (hashed); and `git diff --stat` between `3a9327e51` and
`a434e363d` and between `b9d02700a` and `a434e363d`. It compared the catalog with the code by script (§13). No energy
or power value of any window was read.

For revision 7, the author read: the integration's REG list (`/Users/edr/night-archive/gate-prune/REG_PENDING.md`)
and the relevant entries of `INTEGRATION_TODO.md`; the NEG-8 cold ruling (`neg8-council/RULING.md`); and, at the int5
head `d3c107f2f` (read through a shared clone at `/private/tmp/regsync2/repo`, detached at that commit; the
integration worktree was not touched): the commit messages and diffs of the two audit-fix lanes and the NEG-8 lane
since `a434e363d`; `whole_window.py`'s survivor evaluator and count-adjusted bound; the verdict writer's status
losses; the harvest's NEG-8 screen, re-screen, disclosure, corpus physics drop, malformed-flag rule, unbuilt-flag
rebuild, binary-identity step, accumulator rule and identity supersession; the chain's spare-retry lines and helper;
the driver's reference minimums, census, G10 wait, lineage refusal and orphan reaping; `agent_identity.py`; the arm's
census and UNMEASURED handling; the reservation's desk-file reader; the plan writer's planned bytes; the sizer; the
spare directory's README; the allowlist file and its test. Every number written in this revision was read from a
file or computed by the author: the plan-tree, sizing and identity-pin digests with `shasum -a 256` (and
`size_b5_window.py --check`, `write_b5_identity_pins.py --check` and `reference_spares --check`, all exit 0 at
`d3c107f2f`); the spans and deadlines from `sizing_b5.json`; the planned disk bytes and their GiB from 182 MiB × the
member counts; the allowlist counts and the entry-by-entry difference from `hazard_refusals.json` at both commits;
the §0.12 worked example with the code's own `neg8_count_adjusted_bound` and `student_t_critical_95`; the §6.2
candidate lists from the catalog; and the catalog comparison by script (§13). No energy or power value of any window
was read.
