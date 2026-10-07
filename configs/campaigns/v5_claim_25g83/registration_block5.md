# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **DRAFT, NOT SEALED. Revision 5, 2026-10-06.** Written by Opus 5.5, as lane L6 of the gate-prune workflow
(revision 3, commit `71c91d74`), then as the registration-sync side lane (revision 4, last commit `7261a585`), then
as the REG lane of gate-prune round 3 (revision 5), on branch `design/2026-10-05-v5-claim-block-draft` (revision 2
is commit `bfd1ee8c`). This file authorizes no arm, no
launch and no analysis. It binds only when one cold gate (§0.1, §12) seals it together with three companions in the
same directory:

- `analysis_plan_block5.md`, the **analysis plan**: what is computed from the collected bytes, and how;
- `flag_catalog.json`, the **flag catalog**: for every flag code, whether it removes a member from the claims,
  removes a whole window, or is only disclosed (§6);
- `sealed_inventory.json`, the **sealed inventory**: the SHA-256 of every file a window executes, at the commit the
  windows run (§11). At this writing it is a stub; it is filled at seal.

A **FILL**, written `FILL[NAME]`, is a value that must be tied to authenticated bytes before the point named in §13.
It is never a default. No claim-eligible `_v5` energy exists at this writing, and none was read (§16).

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
seal.

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
  `battery_temperature_readings`) and judged by the harvest; both are at `b9d02700a`.

### 0.7 Packs, attempts, windows and the measurement block

- **Pack.** The frozen, hash-pinned set of stages, member configurations and plans for one window. Its **plan tree**
  (`plan_tree.json`) lists the stages in order (`stage_graph`), with each stage's inputs, command line and expected
  member count. Three packs exist, all with the duration-sized idle baseline of §0.3 (`idle_seconds` 57.6) and the
  block-5 policy of §0.13:
  **ALPHA** `configs/campaigns/d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA**
  `configs/campaigns/d117_floor_qwen3-8b_v5` (Qwen3-8B, 4-bit) and **GAMMA**
  `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models). Their plan-tree SHA-256s after the
  timing lane regenerated them (branch `lane/2026-10-06-timing-policy`, commit `f4cf9047`) are ALPHA
  `5218c2709274765c706f38766ae68cce30892a673e9ae5cc290701362f615eb1` and BETA
  `5bab773a481e4a06fae564217b178d8e1d76a5334f99a3b264c1174db692a6e4`. GAMMA's, after lane L10 gave its interior
  references distinct run ids (branch `lane/2026-10-06-l10-gamma-refs`, commit `c6309e1a`; §2, "Before GAMMA-1
  arms"), is `fb51b4aa0c47fb36bbc838369fd6b5af0db4656becf01ebc5051c9794b8b8bc3` (`523864e2…` after the timing lane,
  and still at the integration head `b9d02700a`, which does not yet carry L10). (At the gate-prune integration head
  `f8164893`, before the timing lane, they were `a0076ae7…`, `ebd8c160…` and `7cdf1891…`.) The values in force are
  those in the sealed inventory at H_claim (§11).
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

- **Reference member.** A member of one fixed reference workload (Qwen2.5-1.5B, 1024-token prompt, 256 output
  tokens). Each window runs 12 at its start, the **NEG-8 corpus** (NEG-8 is an inherited label from the project's
  negative-control list; it is a name, not an abbreviation), then a **start triplet**, one **midpoint reference**,
  and an **end triplet**. The midpoint reference runs at the boundary between the window's decode arm and its
  prefill arm, which is also its temporal midpoint: after science member 50 of 100 in ALPHA and BETA, after science
  member 40 of 80 in GAMMA.
- **Diagnostic interior reference (GAMMA only).** GAMMA also runs one reference in the middle of each arm, after
  science members 20 and 60. Each is the midpoint reference's config under its own run id
  (`gamma-interior-reference-decode-midpoint`, `gamma-interior-reference-prefill-midpoint`), with the role
  `window_interior_reference_diagnostic`. That role is not a NEG-8 role, so neither the NEG-8 screen nor the drift
  allowance below reads these two members; they are recorded as a measure of drift within each arm. (The screen
  accepts exactly three start, one midpoint and three end references; a window with three midpoint-role references
  fails it.)
- **NEG-8 bound.** From the corpus members' gross energies (and separately their idle-subtracted energies), with s
  their sample standard deviation and t = t(0.975, n − 1): bound = max(mean of the largest 3 − mean of the smallest
  3, t × s × √(2/3)) (`whole_window.py` `build_neg8_drift_bound_artifact`).
- **NEG-8 screen.** The window passes when |mean(end triplet) − mean(start triplet)| ≤ that bound, for both the gross
  and the idle-subtracted energies. The
  **whole-window drift allowance** is max(spread, the bound), where the spread is the largest minus the smallest of
  three values: the start-triplet mean, the midpoint reference's energy and the end-triplet mean
  (`whole_window.py`, `trajectory_excursion_max_j`). Each member carries half of the allowance
  (`E_whole_window_drift_allowance_j`), so a contrast carries it once in total.
  *Worked example (synthetic).* A bound of 0.40 J; start mean 20.10 J, end mean 20.35 J: 0.25 ≤ 0.40 passes; with a
  midpoint reference of 19.90 J the spread is 20.35 − 19.90 = 0.45 J, so the allowance is 0.45 J and each member
  carries 0.225 J. In GAMMA, a diagnostic interior reference of 19.70 J would change nothing: it is not one of the
  three values, so the spread stays 0.45 J.
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
  **GO** only if every hazard verdict is PASS, the agent census (§4.5) is clean, and the machine's OS build and model
  are ones the calibration acceptance has judged (§4.7). UNMEASURED refuses, because an unread hazard may be present.
  Nothing else enters the decision.

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
  excluded members, the kept units of each cell, and `claim_usable`. It reads only each flag's code, scope, interval
  and id, never an energy, power or duration; its tests prove this by passing bundles whose energy fields raise when
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
  member whose configuration bytes are not in the pack's committed inventory (§6.3).
- **Monitor.** `scripts/hazard_monitor.py`, a background process that runs from GO until the chain's processes are
  proven gone. It journals the clock anchor every 1 s and the frequency word every 5 s, the battery state (from the
  **registry**, the OS's record of the battery that `ioreg` prints) and the thermal level every 5 s, the battery
  current (from the **SMC**, the Mac's power-management controller; both sources are built in §4.2) every 1 s,
  per-process CPU every 10 s and free disk every 60 s, one append-only file per hazard. Every reading carries three
  timestamps (wall time, the controller's `time.monotonic_ns()`, and CLOCK_MONOTONIC_RAW), so readings join member
  spans exactly. The driver stops it no sooner than 5 s after the chain exits, so that the 1 s battery reads cover
  the end of the post calibration (§6.5; P3-DRV, a sync point of §13).
- **Meter.** `scripts/km003c_monitor.py`, a second background process, started and stopped with the monitor, that
  records the whole machine's DC input through an inline USB-C power meter (§5.8). It is a diagnostic: it never
  refuses, removes or enters a claim number (P3-DRV wires it into the driver; §13).
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
   L8 of the gate-prune plan, and the timing lane of 2026-10-06 (block-5 policy, idle records and settles; branch
   `lane/2026-10-06-timing-policy`), merged under the merge gates. `FILL[H-CLAIM]`.
2. The #416 pre-arm triple audit has run once at H_claim and every verified BLOCKER is cleared (§9.1).
   `FILL[416-AUDIT-RECORD]`.
3. This file, the analysis plan, the flag catalog and the sealed inventory are sealed (§12). `FILL[B5-SEAL-RECORD]`.
4. The three packs as the timing lane regenerated them (§0.7) are at H_claim, and their files are in the sealed
   inventory.
5. The measurement checkout (the dedicated clone a window runs from) is fast-forwarded to H_claim with its Python
   environment relocked, and the ledger seed (§4.6 item 6) is installed at its default ledger path.
6. A mock-runtime dry render of all three packs' chains through the `HAZARD_PACK` driver has passed (every expected
   bundle present, return code 0, only physical seams stubbed), and a desk dry arm with agents alive has refused at
   the census before any action. `FILL[B5-DRY-RENDER-RECORD]`, `FILL[B5-DRY-ARM-RECORD]`.
7. Before the seal, one machinery smoke of the block-5 cooldown policy has passed (timing ruling item 2): a
   dummy-label stage of three small members run under `quiet_mac_p2_b5.json` and harvested through
   `campaign_cooldown_evidence` and `scripts/check_window_provenance.py`. It passes when every cooldown record
   verifies as `recovered` (or `first_run_exempt`) with a one-reading trace, and the join reports zero
   `campaign_cooldown_evidence_missing` and zero `cooldown_evidence_unverified`. It takes about 15 minutes. No
   thermal qualification run is required: the first BETA window measures 8B-after-8B carryover through its
   reference members (§0.12) and the battery-temperature diagnostic (§0.6). `FILL[B5-COOLDOWN-SMOKE-RECORD]`.

**Before ALPHA-1's harvest:** the harvest program (lane L5) emits `member.whole_window_member_failure` for every member
the whole-window verdict fails (§6.3, §6.5; the integration head `f8164893` does not emit it yet), has passed its
Fable final pass, and is pinned by an addendum to the seal record (§11 item 4).

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
block-4 writer (`scripts/write_v5_qualification_plan.py`, which no block-5 window runs) and tests. L10 is not in
the integration head `b9d02700a`; it merges into the next integration (with the sizing and identity pins re-derived
there by the current sizer and `repin.py`). If it lands before the seal its bytes are sealed directly; otherwise a
prospective cold erratum seals them before GAMMA-1 arms. Under §7.5 it supersedes no completed ALPHA or BETA
window, because neither executes GAMMA's files.

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
  before its terminal record, so no capture can be touched. The window plan of each attempt sets `g10: true` until a
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
  `scripts/g10_clock_step_control.py` at `b9d02700a`.) OFF always runs, including on an exception or a SIGTERM or
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
nothing, and the arm's own dwell measures contention after t0 anyway. The supervising watchdog
(`scripts/magistrate_watchdog.py` at `b9d02700a`, P2-WD) therefore stops launching sessions and asks every agent
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
step ends the attempt as NULL (§7.1) with nothing
launched. The arm writes `<custody>/hazards/arm.json` write-once with every measurement, verdict and raw-byte digest.

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
  consecutive samples is a `clock.step`; a change of f is `clock.frequency_changed`. Each anchor sample is three
  reads in a row, RAW, REALTIME, RAW; its **read skew** is the time between the two RAW reads. *Forcing problem:* in
  mock rehearsal round 3 a `ps` probe pre-empted the monitor between those reads, giving skews of 3.9–8.3 ms, and the
  residual computed from such a sample moved by more than 1 ms with no clock step, so the harvest recorded false
  `clock.step` and `clock.step_overlap` (finding R3-1). P3 (lane P3-HAZ) re-reads a sample whose skew exceeds a bound
  well under the 1 ms step limit, up to a fixed number of tries, and then records the sample as unmeasured
  (`clock.unmeasured`, DISCLOSE), never as a step (`FILL[P3-CLOCK-SKEW-BOUND]`, §13). A real step moves every later
  sample, so a skipped sample cannot hide one.
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
    now supplies only the state, and the SMC the current (`joulewise/hazards/battery.py` at `b9d02700a`).
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
  600 s* (PLAN2 finding t2-08; `joulewise/hazards/contention.py` `HAZARD_ARM_CLEAN_S` at `b9d02700a`): no number
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
  182 MiB per member (block 3 measured) × the window's members: 21.2 GiB for ALPHA and BETA (119 members), 17.9 GiB
  for GAMMA (101). The driver plans one copy in the claim runs root and one in each of the two backup destinations
  (§5.6); the bound runs root and the custody root need only the headroom (`joulewise/b5/driver.py`, disk targets).
  The harvest archive is an APFS clone (a copy that shares storage with its source until either is modified), so it
  adds no copy. Targets on one volume add their copies. The backup destinations are in iCloud Drive, whose local
  folder is on the same volume as the runs roots (one device number, read with `stat` on 2026-10-06). So three copies
  land on that volume: 3 × 21.15 + 20 = 83.5 GiB required for ALPHA and BETA, and 3 × 17.95 + 20 = 73.9 GiB for
  GAMMA, against 264 GiB free on 2026-10-05.
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
by the window's own values (§5.5); the values shown are ALPHA's.

```json
{
  "clock":      {"t_stream_max_s": 335, "h_ms": 3.7, "frequency_margin_ppm": 0.25, "limit_ms": 5.0,
                 "skew_max_ns": 1000000, "residual_max_ns": 1000000, "step_ns": 1000000},
  "battery":    {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120},
  "thermal":    {"max_level": 0, "max_gap_s": 15},
  "contention": {"cpu_limit_s_per_s": 0.05, "interval_s": 30, "clean_s": 180, "cap_s": 2700,
                 "window_interval_s": 10, "aggregate_cpu_limit_s_per_s": null},
  "disk":       {"planned_bytes": 22710059008, "headroom_bytes": 21474836480, "low_bytes": 10737418240},
  "instrument": {"frames": 300, "bound_s": 55.0, "median_ms_max": 150.0, "max_ms_max": 200.0}
}
```

`aggregate_cpu_limit_s_per_s: null` means the whole-machine CPU total is journaled at the dwell but not judged; only
the per-process limit decides.

`clean_s` is 180 in revision 5 (was 600). The hazard module's default is already 180 at `b9d02700a`, but the arm
judges the value the window plan copied from this block (`joulewise/b5/driver.py` `_arm_thresholds`), and the plan
writer records any copied value that differs from a module default. So the change takes effect only in plans written
from this block after the seal: any window plan or plan-input template written earlier carries 600 and must be
regenerated (`FILL[B5-PLANS-REGENERATED]`, §13).

### 4.4 Network time

- At every arm the driver runs `sudo -n systemsetup -setusingnetworktime off` as an action, whatever the current
  state, because running it removes the hazard. Its return code and output are recorded only (`network_time.off_output`,
  disclosed); nothing reads its wording. Whether the clock is in fact undisturbed is measured by the clock hazard
  (§4.2: the dwell residual and the f-equality checks).
- There is no settle wait after OFF and no ON at the arm. Network time is turned ON only by G10 at ALPHA-1's tail
  and by the desk frequency redraw (§3). Revision 2's "no ON at any point" is withdrawn.

### 4.5 Agent census

Kept by doctrine ("never start or continue a [QUIET-MAC] measurement while an agent session is active";
[QUIET-MAC] marks work run on the dedicated, quiet measurement Mac). The census
is `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'` (`joulewise/night_gate.py` `AGENT_CENSUS_ARGV`); it is clean when it
exits 1 with empty output. It runs first at the arm, again just before GO, and every 30 s in the window. In the
window a non-clean census stops the chain; the window then has no post calibration, so it is not claim-usable
(`calibration.no_bracket`). Seats exit before t0, and the watchdog fences the plan's span, so this should not fire.
Load average, process-name lists and the `corecaptured` spawn count, which revision 2 judged, are recorded only.

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
   bundles of the same two models, without loading a model. Its draft SHA-256 after lane L10 (`c6309e1a`) is
   `ccce59f908ddefd881ac0d8ba9b510e7de9e54adced1ae77d9353da398999c32` (`9c2ecd89…` after the timing lane
   `f4cf9047` and still at the integration head `b9d02700a`; `039d3e3c…` at `f8164893`; each change moved only the
   packs' plan-tree and config-inventory digests, L10's only GAMMA's plan-tree digest, never the model or runtime
   pins); the seal binds the bytes at H_claim.
   Two programs compare against these pins. At the arm, the driver passes the file to the model-identity collector
   (`--identity-pins`) when the measurement checkout holds it. At harvest, the harvest reads its archived copy. If
   either finds no pin to compare against, it records `model.identity_unpinned`, which removes the window (§6.5).
4. **Packs:** the three packs at H_claim (§0.7), with the pin bundle of the packs: prompt pin
   `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`, selection
   `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`, ladder
   `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
5. **Policy:** §0.13, `configs/campaign_policies/quiet_mac_p2_b5.json`,
   `ba0f7b7f1538fe87f6281362efbba4b05f7dff74b4bfd78e84c98b9e8859bc60`.
6. **Ledger seed:** block 3's ledger at pin 402 (§0.11), installed at the measurement checkout's default ledger
   path, `<checkout>/runs/calibration_observation_ledger.jsonl`, because the controller's pre-calibration route reads
   that path; the plan writer refuses at the desk if the plan names another. Before each arm the desk runs the
   read-only ledger readiness check; a session left open by an abandoned attempt is closed with the existing abort
   plus a pin advance. For each later attempt the seed is the previous attempt's harvested terminal ledger, whose tip
   the pin advance names. A pin advance is a pin-only commit made in the measurement checkout (H_claim plus pin-only
   commits, §0.18, §11), not a merged pull request: the merge path took 15–60 min per window for a one-file data
   change (PLAN2 X4). The order stays harvest, then pin advance, then the next arm, because the harvest reads the live
   ledger and an append before it would drop the harvested window from it.

A change to any item after the seal needs a prospective cold erratum before the next arm (§10).

## 5. Window shape and sizing

### 5.1 The chain

The chain runs its pack's stage graph in block 3's order: the bracket reservation; a 60 s settle; the pre
calibration and its screen; the NEG-8 corpus and the bound derivation; the start triplet; the science stages with
the pack's interior references in their places (the midpoint reference in every pack; in GAMMA also the two
diagnostic interior references, §0.12); the end triplet; the post calibration and a record of the bracket
session's status. Every collection stage starts with its own 60 s settle (§0.6; block 3 used 180 s).

- **The only stops**, all before member 1 (about 13 min into the chain): a failed reservation (chain exit 10), a
  failed pre calibration capture (exit 11), and a pre fiducial bound above the pre screen 0.036462861644980 s
  (`instrument.precal_screen_failed`, exit 12). The driver records such a window as CHAIN_STOPPED, not GO (§5.7).
  Outside the chain, the driver stops it on `disk.low`, on a non-clean census, when the monitor has written no
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
  calibration capture 1,800 s, window calibration verdict 600 s, the corpus-retry decision 300 s, the collected-corpus
  copy 1,800 s, the bound derivation 1,800 s, the session-status record 600 s, each chain flag record 120 s. On
  expiry the stage's process tree gets SIGTERM, then SIGKILL 30 s later, and the stage records return code 124; the
  chain continues as after any failure of that stage. The post calibration capture has no budget: it must be allowed
  to finish, or the window loses its bracket.
- **The collection deadline** (PLAN2 row 17; `chain.py` `CALIBRATION_HORIZON_S`, `HORIZON_*`). *Forcing problem:* a
  bracket is fresh for 24 h from the pre calibration capture, and the window's deadline (§5.5, 26.9 h for ALPHA) is
  longer. A chain that overran past 24 h would lose its bracket, and with it the whole window, not just a tail. The
  deadline cannot simply be lowered: it is the driver's kill time, and a kill loses the post calibration.
  *Mechanism:* a collection stage, the corpus retry and the bound derivation launch only when now + the stage's
  allowance ≤ pre-capture start + 86,400 s − 1,430 s. The 1,430 s reserve is a 60 s settle, the 770 s calibration
  pair allowance and 600 s of margin. A collection stage's allowance is 60 s settle + 180 s stage overhead + its
  members × 620 s (at least block 4's largest member allowance, 619 s). Once one stage is refused (return code 75),
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
  all three succeed, 11 have succeeded and the bound is derived from those 11 (§5.3).
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

**The member cap** (PLAN2 row 8; `scripts/run_campaign.py` `HAZARD_MEMBER_CAP_S` at `b9d02700a`). *Forcing problem:*
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

### 5.3 The NEG-8 corpus may lose up to two members

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
   - *Did the screen pass?* When the stored screen's only NEG-8 conditions are the two bound-underived ones and the
     bound was derived from the collected subset, the harvest re-screens the window (`_neg8_rescreen`). It
     re-derives the NEG-8 bracket with the core's own evaluator (`whole_window._derived_neg8_decision`), over the
     reference bundles the verdict names, with the validated bound in place of the absent one, and with the bound's
     freshness judged at the verdict's completion time. The re-derived bracket must have the stored bracket's
     endpoints and estimand; if it does not, these are not the bundles the verdict was written from, and nothing is
     evaluated. The re-screen alone then decides: `neg8.screen_failed` is emitted unless the re-screen ran, passed
     and listed no condition. Any other NEG-8 condition, or a re-screen that cannot run, leaves the screen failed.

Structure (decisions, conditions, member counts, digests) goes to `derived/neg8-bound.json` and
`derived/neg8-screen.json`. The re-derived bracket holds reference-workload energies, so it goes to restricted custody
(`withheld/neg8-rescreen-bracket.json`). The stored verdict of such a window still reads "failed", which is
`whole_window.not_passed`, disclosed only (§6.5).

### 5.4 The window's tail

After the post calibration: the chain exits; the driver proves the chain's process group gone (a census of the
group with no signal, then the existing termination proof); the monitor and the meter stop, no sooner than 5 s after
the chain exited (§0.17); G10 runs if the plan asks (§3); the driver writes its terminal record with the window's
yield (§5.7). The harvest may open as soon as that terminal record exists (§7.1), because the driver holds nothing
after it.

**The watchdog releases a finished window at once** (PLAN2 X1; `scripts/magistrate_watchdog.py` at `b9d02700a`,
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
  rule keeps block 4's conventions and uses the chain at `b9d02700a` (`scripts/size_b5_window.py`, its
  `conventions` list):
  - span = (1 + collection stages) × 60 s settle + the collection stages' countdowns (0 s, §5.1) + the pre and post
    calibration pair (770 s) + the bound derivation (320 s) + the corpus prune (320 s) + the window calibration
    verdict (60 s) + the sum of member allowances + stage custody + the terminal shutdown (300 s) + one corpus retry;
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
  - the **bound derivation** is now charged 320 s, not block 4's 60 s: a real derivation re-reduces 12 bundles,
    about 270–320 s (PLAN2 §1.4 item 6; never measured live). The **corpus prune**, which asks the NEG-8 mint which
    corpus members it would drop (§5.3), reads the same 12 bundles and is charged the same. The **window calibration
    verdict** (§5.1) is charged 60 s for one refit of about 15 s.
- **`WINDOW_MAX_S`**, the window's deadline measured from t0, = 60 × ceil((span + 3,300 s) / 60). The 3,300 s is the
  arm's allowance: the dwell cap of 2,700 s plus the census, reads, network-time OFF, collectors and cadence probe.
- **`B5-SIZING-OUTPUTS`** (draft values at the integration head `b9d02700a`; re-derived and sealed at H_claim):
  `configs/campaigns/v5_claim_25g83/sizing_b5.json`, schema `joulewise.b5_sizing.v1`, SHA-256
  `a5c6ec05c8cd0df84b7ee2c8e21709d17a96f87a5de5cfdbf711087e2944ca52` at `b9d02700a` (status `UNSEALED_DRAFT`;
  `7c53ebc8…` on lane L10's branch with the older sizer, `b31a27b5…` after the timing lane `f4cf9047`, `9d16edfe…` at
  `f8164893`). The next integration merges L10 and re-derives it with the current sizer; the value in force is the
  one sealed at H_claim. `scripts/size_b5_window.py` writes it from block 4's committed sizing source
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
  | ALPHA | 119 / 0 | 93,402 s (25.9 h) | 96,720 s (26.9 h) | 31,584 s (8.8 h) | 19,460 s (5.4 h) |
  | BETA | 19 / 100 | 95,802 s (26.6 h) | 99,120 s (27.5 h) | 32,634 s (9.1 h) | 20,510 s (5.7 h) |
  | GAMMA | 61 / 40 | 82,266 s (22.9 h) | 85,620 s (23.8 h) | 27,747 s (7.7 h) | 17,426 s (4.8 h) |

- **Why the deadline is about three times the expected chain.** The rule charges every member, at once, both worst
  cases: the cooldown runs to its cap and idle admission needs its second attempt; and it charges a corpus retry that
  most windows never run. *Worked decomposition, ALPHA:* 119 members × 595 s = 70,805 s, of which 35,700 s is every
  member's cooldown at its 300 s cap and 32,725 s is every member's two admission attempts. Per-member custody adds
  119 × 77 = 9,163 s; the corpus retry 8,304 s; settles, calibration, derivation, prune, the window calibration
  verdict, stage custody and shutdown the other 5,130 s; span 93,402 s. Block 3 measured a start-to-start member
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
  and courier about 0.1 h, a watchdog tick of up to 5 min, the harvest 0.5–1.5 h, the pin-only commit and the next
  plan a few minutes, and the 180 s stand-down lead (PLAN2 §1.3). Adding three arms of 4–47 min, the three windows
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

*The reader.* `scripts/km003c_monitor.py` (at `b9d02700a`) polls the meter every 200 ms at ordinary scheduling
priority (the probe rejected background priority) and reads B0AC, B0AV, PDTR, PSTR and PPBR from the SMC at every
poll. It writes one create-once stream file per start, `<custody>/hazards/meter/stream-NNN.jsonl`: a header (status
`streaming` or `absent`), one line per poll, error lines, and a trailer. The header and trailer each carry a pair of
clock readings (CLOCK_MONOTONIC_RAW and `time.monotonic_ns`), so the stream can be placed on the members' clock. When
no meter is attached it writes an `absent` header and exits 0, and the driver does not restart it. Its cost: 0.302
CPU-s over a 120 s live run, 0.25% of one core. It runs outside the chain's process tree, so the contention monitor
counts it, at about 0.0025 CPU-s/s, one twentieth of the 0.05 limit; its own energy is on the rails like the
monitor's and is disclosed with it (analysis plan §8.1).

*Quantities* (`joulewise/external/km003c_parse.py`, at `b9d02700a`), for each member and each analysed window (the
member's measured request, and each phase where the bundle records phase boundaries):

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
claim-bearing number. ΔE_rail, ΔE_machine and ρ are energies and an energy ratio: they go to restricted custody
(`withheld/meter/<run_id>.json`) until the release event, like every other energy (§8). The driver wiring (start,
stop, the supervisor's name, no restart after `absent`) is P3-DRV's and the harvest hook is P3-HARV's; both are sync
points (§13).

## 6. Flags and exclusions

### 6.1 Where flags come from

All flag files are append-only, with an fsync per line.

| Stage | File | Writer |
|---|---|---|
| Desk, before an arm (never during a dwell or a window) | `<custody>/flags/desk.jsonl` | the record-only collectors run by the lead; a window-removing flag here means the cause is fixed before scheduling; the driver never reads these flags |
| Arm | `<custody>/hazards/arm.json` (verdicts and measurements); `<custody>/flags/arm.jsonl` (collectors) | the hazard arm; the collectors |
| Window | `<custody>/hazards/monitor/{clock,battery,thermal,contention,disk}.jsonl` plus raw bytes; the driver's flags | the monitor; the driver |
| Harvest | `derived/flags.jsonl` (every flag, de-duplicated); `derived/window_flags.json` (summary); `derived/exclusions.json`; numbers under restricted custody `withheld/` | the harvest |

### 6.2 The catalog

`flag_catalog.json` is normative; this section states its rules in words. Its `rules.cell_unit_minimum` is 8. Two
codes, `records.malformed_flag` (a flag line that failed validation, so its exclusion may be lost) and
`collector.unmeasured` (a collector the flag package does not know), are deliberately absent from the catalog: they
are always UNCLASSIFIED, so they always block the release event until a person reads them.

| Family | What it covers | Effect |
|---|---|---|
| PACK_IDENTITY, CODE_IDENTITY, MODEL_IDENTITY | the pack, the executed code or the model differs from what was sealed, or could not be compared | EXCLUDE_WINDOW (one member whose model identity cannot be derived from its own metadata: EXCLUDE_MEMBER) |
| CALIBRATION | the bracket is missing, invalid, unbound or fails the acceptance, or the ledger it is judged from fails its own integrity checks | EXCLUDE_WINDOW (the desk's ledger-readiness checks before an arm: DISCLOSE) |
| NEG8 | the bound was not derived, the screen failed, or the verdict holding the screen is absent | EXCLUDE_WINDOW (aggregate verdict codes: DISCLOSE, §6.5) |
| INSTRUMENT | the pre-calibration screen failed | EXCLUDE_WINDOW |
| CLOCK_SYSTEMATIC | a step during a calibration capture; most recorded anchors not `bounded` | EXCLUDE_WINDOW |
| MEMBER_VALIDITY | §6.3 | EXCLUDE_MEMBER |
| PHYSICS_IN_SPAN | §6.4 (battery assist is DIAGNOSTIC, not this family) | EXCLUDE_MEMBER |
| ROSTER | §6.7 | EXCLUDE_MEMBER (window-level roster failures: EXCLUDE_WINDOW) |
| RECORDS | receipts, lineage formalities, attempt history, pin ledger, provenance digests, naming, notices, missing journals | DISCLOSE (one exception: source bytes changed during the harvest, EXCLUDE_WINDOW) |
| DIAGNOSTIC | network-time output, clock steps and frequency changes outside any span, G10, s1-structural checks, the battery-temperature rise across a stage (§0.6), battery assist (§6.4), the whole-machine meter (§5.8), the yield counts (§5.7) | DISCLOSE |

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
  bytes) is present and shows charging or AC lost (`battery.capture_pair_failed`); a pair that fails only on
  discharge current is disclosed as `battery.assist` (§6.4; P3 sync point, §13);
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

### 6.4 Member exclusions: physics in the member's span

A member's **span** is its sampler stream, from the `start_sampling` stamp to the stop stamp, in the controller's
`time.monotonic_ns()` domain. A member whose span cannot be placed is removed (`member.span_unknown`), because the
rules below cannot be applied to it.

**Battery** (ruling of 2026-10-06, §9.2; sources and validation in §4.2). Terms used below:

- The registry publications **in force** for a span are the last publication at or before its start, every
  publication inside it, and the first publication at or after its end.
- An SMC read is **good** when B0AC is an integer with no read error, and **fresh** when its five recorded keys
  (B0AC, B0AV, PDTR, PSTR, PPBR) differ from the previous good read's: a frozen SMC repeats its block, and repeats
  are not new measurements. The SMC **covers** a span when good, fresh reads are no more than 5 s apart across it
  (`battery.SMC_MAX_GAP_S`). When it does not, the registry's InstantAmperage and Amperage at the in-force
  publications stand in for B0AC in every rule below, and `battery.smc_unavailable` (DISCLOSE) records the fallback.
- **Assist**: the battery discharging into the machine while the adapter is connected and the battery is not
  charging: a B0AC read below −200 mA with ExternalConnected Yes and IsCharging No.

Rules:

- `battery.member_span` (EXCLUDE_MEMBER) fires on any of:
  1. *charging current:* a B0AC read inside the span above +200 mA;
  2. *charging or AC lost:* IsCharging Yes or ExternalConnected No at any in-force publication or any 5 s registry
     poll inside the span;
  3. *charging energy:* over an interval between two consecutive in-force publications, the charge accumulator
     implies a mean charging power above 200 mA × the publication's voltage (units below).
- `battery.unmeasured` (EXCLUDE_MEMBER), the missing-evidence predicate, unchanged: no registry publication was
  observed for more than 120 s overlapping the span, or an in-force publication lacks a needed field. Without the
  registry the state (charging, AC connected) is unknown, so the member cannot be kept.
- `battery.assist` (DISCLOSE): assist inside the member. For each phase of the member, prepare (before the sampler
  starts), idle baseline, warm-up and measured request, the flag records the number of reads below −200 mA, the
  minimum B0AC, the sampled duration below −200 mA (each read counts for the time until the next read) and the
  discharged energy, ∫ max(0, −B0AC × B0AV) dt (the mean of max(0, −B0AC × B0AV) over the phase's reads times the
  phase's length, the rule the meter uses, §5.8). The counts, minimum and duration are structure; the energy goes to
  restricted custody (`withheld/`) with the other machine energies (§8). Battery energy is never added to or
  subtracted from a rail energy. A discharge accumulator above 200 mA × V on an interval overlapping the span is also
  recorded here. Reads in prepare, idle baseline and warm-up are reported separately and decide nothing; the
  battery-assist sensitivity line (analysis plan §8.1) marks a member only by reads in its measured request.
- `battery.accumulator_activity` (DISCLOSE): an accumulator mean that is nonzero but at or below the limit. Every
  archived calibration capture shows 7–32 discharge ticks at −122 to −151 mW while InstantAmperage read 0.

*Code state.* At `b9d02700a` the harvest still judges the current on the registry publications and removes a member
on |InstantAmperage| or |Amperage| above 200 mA in either direction, and `battery.accumulator_excursion`
(EXCLUDE_MEMBER) fires on either accumulator sign. P3 (lanes P3-HARV and P3-HAZ) moves the harvest and the hazard
module to the SMC reads and to the rule above: discharge becomes `battery.assist`; the charge-accumulator test stays
excluding, under `battery.member_span` or `battery.accumulator_excursion` restricted to the charge sign
(`FILL[P3-BATTERY-CODES]`, §13).

*Accumulator units* (lane L1, 2026-10-05, on 66 archived publications and a live read): each `Accumulated*` field
adds its instantaneous value in mW once per tick (about 1.01 s), each `*AccumulatorCount` counts ticks, and battery
power is split by sign into a charge accumulator (`AccumulatedBatteryPower` / `BatteryPowerAccumulatorCount`) and a
discharge accumulator (`AccumulatedBatteryDischarge` / `BatteryDischargeAccumulatorCount`); the split was proven by
an exact identity on all 65 intervals. So Δ(accumulated) ÷ Δ(count) is the mean power in mW over the ticks on which
that sign occurred, and the registered scale is 0.001 W per unit. *Positive control:* between the 2026-09-25 20:47
and 2026-10-01 06:17 publications the discharge accumulator gained 15,043 ticks at a mean of −5,415 mW; the registry
reading inside that interval was −447 mA at 12,180 mV = −5,444 mW; they agree within 0.6%.

*Worked example (synthetic).* A member's measured request runs 5 s, with B0AC reads one second apart of −865,
−1,200, −400, −150 and 0 mA, B0AV 12,180 mV, ExternalConnected Yes and IsCharging No throughout. Three reads are below
−200 mA; the minimum is −1,200 mA; the sampled duration below −200 mA is 3 s. The discharged powers are 10.54, 14.62,
4.87, 1.83 and 0 W (the −150 mA read counts toward the energy, not toward the count); their mean, 6.37 W, times 5 s
is 31.85 J of discharged energy. The member is kept and carries `battery.assist`. Had one read been +450 mA, or one
registry poll in the span read IsCharging Yes, the member would be removed by `battery.member_span`. If between two
in-force publications the charge accumulator gained 40 ticks totalling +216,000 mW·ticks, its mean is +5,400 mW,
above 200 mA × 12.18 V = 2,436 mW, and the member is removed; the same numbers on the discharge accumulator give
`battery.assist` only.

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
- `calibration.capture_invalid`, `calibration.capture_battery_pair_failed` (a calibration capture's #421 pair
  shows charging or AC lost), `calibration.bracket_acceptance_failed` (evaluated with the acceptance's ledger-cutoff
  baseline), `calibration.acceptance_mismatch` (the acceptance bytes differ from the plan tree's pin),
  `calibration.session_not_bound` (the bracket session names another plan, window or runs root),
  `calibration.binding_failed`, and `calibration.no_bracket` (including a chain stopped before its post calibration
  by `disk.low`, the census or the deadline).
- `calibration.ledger_snapshot_refused`: the calibration ledger, read up to this window's terminal entry, fails its
  own integrity checks. That means a missing or malformed ledger, a broken digest chain, or the acceptance's cutoff
  entry (sequence 376 with its recorded head digest) not found in the chain. The bracket's captures and the
  acceptance's screens are authenticated through this ledger. The bracket evaluation reads the same snapshot and
  refuses with the same reasons, so `calibration.bracket_acceptance_failed` fires as well. Classing this code as
  window-removing therefore costs no extra window, and it keeps the window removed even if that propagation changed.
- `calibration.capture_battery_span` and `calibration.capture_battery_unmeasured`: the battery rule of §6.4 applied
  to each calibration capture's span, as to a member's. Charging, AC lost or the charge accumulator above the limit
  gives `calibration.capture_battery_span`; a capture whose #421 pair did not pass and whose span the journal cannot
  stand in for (no span, no battery journal, or the §6.4 missing-evidence predicate) gives
  `calibration.capture_battery_unmeasured`. A capture with only discharge is disclosed (`battery.assist`, window
  scope). *Forcing problem for the 1 s reads:* at `b9d02700a` this join reads the registry, and the monitor stops
  right after the chain exits, before the registry's next publication; so the post capture's last in-force
  publication never exists and every window would get `calibration.capture_battery_unmeasured` (mock rehearsal
  round 3, finding R3-5). P3 makes the join read the 1 s SMC reads and stops the monitor no sooner than 5 s after the
  chain exits (§0.17; sync point, §13).
- `calibration.historical_custody_mismatch`: a file of an earlier calibration capture, re-hashed by the harvest,
  differs from the SHA-256 its ledger entry recorded (§6.10).
- `clock.step_overlap_calibration`: a clock step inside a calibration capture.
- `neg8.bound_not_derived` (§5.3) and `neg8.screen_failed`; also `whole_window.verdict_absent`, because the NEG-8
  screen's result is held in the whole-window verdict.
- `instrument.precal_screen_failed`.
- `clock.systematic`: at least 5 members of the window have a recorded anchor status and more than half of them are
  not `bounded`.
- `cell.below_minimum` (§6.6) and `roster.no_science_bundles`.
- `records.source_changed_during_harvest`: bytes the harvest reads changed while it read them.

**Two aggregate codes are disclosed, not window-removing:** `whole_window.not_passed` (the stored whole-window verdict
did not pass) and `g3.recompute_failed` (check F5-2 of G3, the desk provenance checker
`scripts/check_window_provenance.py`, which independently recomputes that verdict, did not find a clean pass). The
verdict passes only if every member passed, so both codes fire when a single member failed admission or its
environment guard. Making them window-removing would restore "one aborted member voids the window", which Ed's
2026-10-05 ruling removed. The verdict's checks are not lost: each part acts at its own level through its own code.

- *The NEG-8 screen* (window level): `neg8.screen_failed`. The harvest emits it from the verdict's NEG-8 bracket:
  a decision other than passed, or any NEG-8 condition (`neg8_gross_point_drift_exceeded`,
  `neg8_idle_sub_point_drift_exceeded`, `neg8_bracket_missing`, `neg8_bracket_reference_invalid`,
  `neg8_drift_bound_stale`, the bound-underived conditions). The one exception is the collected-subset re-screen of
  §5.3, which decides when the bound's absence was the only problem.
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
or the same energy could be counted under two units or in the wrong quad position. The emitter classes this code
REPRESENTATION; the catalog restates it as NUMBER for that reason. It costs one unit and should never fire.

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
(`battery.assist`, §6.4) and the SMC fallback (`battery.smc_unavailable`); the whole-machine meter's flags
(`meter.*`, §5.8); the yield flags (§5.7); and the records of §6.10.

`contention.kernel_task_share` stays in the catalog but cannot fire today: an unprivileged `ps` never lists
`kernel_task` (process id 0; checked 2026-10-05), so neither the arm nor the monitor sees its CPU time by name. Its
work is inside the host's total busy time, which the monitor journals every 10 s and nothing judges in the window
(§4.2, Contention).

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

## 7. Verdicts, re-arming and END STATE

### 7.1 Three verdicts per attempt

The harvest opens when the driver's terminal record exists (§5.4), works from an archive copy of the window, and
writes one verdict:

- **COLLECTED:** `night/chain.started` exists. The numbers (into restricted custody) and the flags are emitted
  whatever the flags say, and the exclusion function computes `claim_usable`.
- **NULL:** no chain start: the arm refused, or the driver failed before the chain. `claim_usable` is false.
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
  re-arm.
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
or AC loss keeps its exclusion. No discharge exclusion remains anywhere once P3 lands (§13).

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
collection deadline, the corpus retry) are not deviations from pack bytes: they are the chain's own steps, listed in
`joulewise/b5/chain.py` `DEVIATIONS` and registered in §5.1 and §0.6.

## 11. Commit rule and the sealed inventory

1. **H_claim** is the commit of §2 item 1. It is extended only by (i) pin-only commits from this block's harvests,
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
| Sizing | `B5-SIZING-OUTPUTS`: filled in revision 4 with draft values, re-derived after the timing lane (§5.5); pinned at H_claim | Seal |
| Cooldown smoke | `B5-COOLDOWN-SMOKE-RECORD` (§2 item 7) | Seal |
| Disk | `BACKUP-DESTINATIONS`: filled in revision 4 (§5.6) | Seal |
| Identity pins | `identity_pins.json` (§4.6 item 3): draft after the timing lane; pinned at H_claim | Seal |
| Blinding | `B5-BLIND-CUSTODY-MAP`, `B5-RELEASE-EVENT` | Map at seal; release after the block closes |
| Boundary | `BOUNDARY-LABEL`: filled in revision 4 (§1) | Seal |
| Attribution floor | `ATTRIBUTION-FLOOR-BINDING` | Seal |
| Seal | `B5-SEAL-RECORD` | Seal |

Still open after revision 4: `H-CLAIM`, `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS`, `B5-SEAL-RECORD`,
`B5-COOLDOWN-SMOKE-RECORD`, `B5-DRY-RENDER-RECORD`, `B5-DRY-ARM-RECORD`, `B5-BLIND-CUSTODY-MAP`,
`B5-RELEASE-EVENT` and `ATTRIBUTION-FLOOR-BINDING`. None can be filled from committed bytes: each names a commit, a
record or a ruling that does not exist yet.

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
  finished window on its terminal evidence (§5.4; P2-WD at `b9d02700a`).
- **Q9. The battery-assist line for GAMMA's contrasts (seal gate).** The ruling of 2026-10-06 prints every reported
  cell with and without assisted members (analysis plan §8.1). GAMMA's contrasts are not reported cells (§0.9), and
  8B members, one side of every quad, are the ones that assist most. Should each contrast's estimate also be printed
  without the quads that hold an assist member? Adopt (the line is descriptive and gates nothing) or strike.
- **Q10. Whole-machine meter, central band (none; recorded).** The band for ρ is set by the first clean window
  (analysis plan §8.2). If no window of the block is clean, no band is set, and the cross-check reports only the hard
  plausibility band and the spreads. Nothing waits on this.

## 15. Where each gate-prune change lives

| Plan §6 item | Change | Here |
|---|---|---|
| 1 | Network time OFF as an action; no wording check; ONs only at G10 and the redraw | §4.4, §3 |
| 2 | Clock gate 3.7 ms + (\|f\| + 0.25 ppm) × 335 s ≤ 5 ms; dwell linearity ±1 ms; 1 ms step; per-member 5 ms bound authoritative | §0.14, §4.2, §6.4 |
| 3 | Idle admission unchanged; `member.admission_aborted` removes the member; stage continues; L11 option | §0.13, §6.3, §5.2, §7.5 |
| 4 | Battery: arm check, 5 s journal, 60 s publication, in-force rule, accumulator rule with units, unmeasured, pairs as data, measured limitation | §4.2, §6.4, §9.2 |
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
