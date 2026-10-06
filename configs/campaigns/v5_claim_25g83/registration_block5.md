# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **DRAFT, NOT SEALED. Revision 4, 2026-10-06.** Written by Opus 5.5, as lane L6 of the gate-prune workflow
(revision 3, commit `71c91d74`) and then as the registration-sync side lane (revision 4), on branch
`design/2026-10-05-v5-claim-block-draft` (revision 2 is commit `bfd1ee8c`). This file authorizes no arm, no
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
`feat/2026-10-05-gate-prune`, commit `f8164893`). No threshold changed.

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

- **Idle baseline.** The sampler records the idle machine for the configuration's `idle_seconds`, 75 s in every
  `_v5` pack (PR #481): about 750 records, which at block 3's cadence spanned 97.7–100.3 s. **Idle admission** then
  tests whether the machine was quiet during that baseline (the tests are in §0.13).
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

- **Stage.** One ordered list of members that `scripts/run_campaign.py` runs together. Each stage starts with a
  180 s **settle**: the **chain** (the script that runs a window's stages in order, §0.17) sleeps so the machine
  returns to idle.
- **Cooldown.** Between members of a stage the runner waits until processor power has been steady for 30 s (judged
  in 5 s sub-windows, within 10%) and the OS thermal state is nominal, or until the 300 s **cap**. A member whose
  cooldown reached the cap is recorded as `cooldown_cap_hit`.

### 0.7 Packs, attempts, windows and the measurement block

- **Pack.** The frozen, hash-pinned set of stages, member configurations and plans for one window. Its **plan tree**
  (`plan_tree.json`) lists the stages in order (`stage_graph`), with each stage's inputs, command line and expected
  member count. Three packs exist, all with 75 s idle baselines (PR #481):
  **ALPHA** `configs/campaigns/d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA**
  `configs/campaigns/d117_floor_qwen3-8b_v5` (Qwen3-8B, 4-bit) and **GAMMA**
  `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models). Their plan-tree SHA-256s at the
  integration head `a0a4f5a7` are ALPHA `a0076ae7ed8dc89b81a5138ce35d38171946e5e8a30599202f7845e7bcb70938`, BETA
  `ebd8c160feda7698698eb28b48e18f9f3b3b7df9dacd1d4b7d70a09e49f73d6a`, GAMMA
  `7cdf1891ab8ddde7b2fcd882c211599bbf2205aeb08b30c9a9da92d749bf5b1e` (unchanged at the gate-prune integration head
  `f8164893`); the values in force are those in the sealed
  inventory at H_claim (§11), and GAMMA's changes once more before GAMMA-1 (§2, "Before GAMMA-1 arms").
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
  negative-control list; it is a name, not an abbreviation), then a **start triplet**, interior references, and an
  **end triplet**.
- **NEG-8 bound.** From the corpus members' gross energies (and separately their idle-subtracted energies), with s
  their sample standard deviation and t = t(0.975, n − 1): bound = max(mean of the largest 3 − mean of the smallest
  3, t × s × √(2/3)) (`whole_window.py` `build_neg8_drift_bound_artifact`).
- **NEG-8 screen.** The window passes when |mean(end triplet) − mean(start triplet)| ≤ that bound, for both the gross
  and the idle-subtracted energies. The
  **whole-window drift allowance** is max(largest spread among the start, interior and end means, the bound); each
  member carries half of it (`E_whole_window_drift_allowance_j`), so a contrast carries it once in total.
  *Worked example (synthetic).* A bound of 0.40 J; start mean 20.10 J, end mean 20.35 J: 0.25 ≤ 0.40 passes; with an
  interior mean of 19.90 J the spread is 0.45 J, so the allowance is 0.45 J and each member carries 0.225 J.
- The NEG-8 screen reads reference-workload energies, never a science member's energy.

### 0.13 Idle admission

Before each member's request, its idle baseline must pass (production policy
`configs/campaign_policies/quiet_mac_p2_production.json`, SHA-256
`b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`):

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
  Six are registered (§4.2): the clock stepping or drifting beyond budget; the battery charging or discharging; OS
  thermal pressure; a competing process above 5% of one core; too little free disk for the window; the sampler not
  sampling at its cadence.
- **Hazard module.** Code (`joulewise/hazards/`, one module per hazard) that measures one physical quantity
  directly, keeps the raw bytes with their SHA-256, and returns **PASS**, **REFUSE** or **UNMEASURED** (the probe
  failed or timed out). A check that reads a proxy for a hazard (a settings string, a receipt, a setter's wording) is
  not a hazard module; doctrine requires measuring the quantity itself.
- **Arm.** The sequence the driver runs after t0 that decides whether this window's chain starts (§4.1). It returns
  **GO** only if every hazard verdict is PASS and the agent census (§4.5) is clean. UNMEASURED refuses, because an
  unread hazard may be present. Nothing else enters the decision.

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
  proven gone. It journals the clock anchor every 1 s and the frequency word every 5 s, the battery and thermal
  readings every 5 s, per-process CPU every 10 s and free disk every 60 s, one append-only file per hazard. Every
  reading carries three timestamps (wall time, the controller's `time.monotonic_ns()`, and CLOCK_MONOTONIC_RAW), so
  readings join member spans exactly.
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
of the processor package rails, never wall power or the whole machine.

What the paper prints, and from which artifact, is fixed in analysis plan §9; printing anything needs the placement
ruling of §14 Q4.

## 2. Preconditions

Each is evidenced by a path and SHA-256 before the point named.

**Before ALPHA-1 arms:**

1. H_claim is fixed: the commit carrying PR #483 (the `_v5` qualification-code integration) and lanes L1–L4, L7 and
   L8 of the gate-prune plan, merged under the merge gates. `FILL[H-CLAIM]`.
2. The #416 pre-arm triple audit has run once at H_claim and every verified BLOCKER is cleared (§9.1).
   `FILL[416-AUDIT-RECORD]`.
3. This file, the analysis plan, the flag catalog and the sealed inventory are sealed (§12). `FILL[B5-SEAL-RECORD]`.
4. The three idle-75 packs are at H_claim, and their files are in the sealed inventory.
5. The measurement checkout (the dedicated clone a window runs from) is fast-forwarded to H_claim with its Python
   environment relocked, and the ledger seed (§4.6 item 6) is installed at its default ledger path.
6. A mock-runtime dry render of all three packs' chains through the `HAZARD_PACK` driver has passed (every expected
   bundle present, return code 0, only physical seams stubbed), and a desk dry arm with agents alive has refused at
   the census before any action. `FILL[B5-DRY-RENDER-RECORD]`, `FILL[B5-DRY-ARM-RECORD]`.

**Before ALPHA-1's harvest:** the harvest program (lane L5) emits `member.whole_window_member_failure` for every member
the whole-window verdict fails (§6.3, §6.5; the integration head `f8164893` does not emit it yet), has passed its
Fable final pass, and is pinned by an addendum to the seal record (§11 item 4).

**Before GAMMA-1 arms:** GAMMA's three interior reference stages launch three distinct `run_id`s (lane L10). In the
current pack all three launch the same one-member input, and `run_campaign.py` skips a `run_id` whose complete bundle
already exists, so the second and third would be skipped. The fix changes GAMMA pack bytes only. If it lands before
the seal its bytes are sealed directly; otherwise a prospective cold erratum seals them before GAMMA-1 arms. Under
§7.5 it supersedes no completed ALPHA or BETA window, because neither executes GAMMA's files.

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
  **DISCHARGED**. (5) Keep network time ON while reading f each minute; switch OFF when |f| ≤ 3.0 ppm or 15 min after
  ON. OFF always runs, including on an exception or a SIGTERM or SIGHUP. (6) Write `night/g10.json` write-once.
- *Why it should discharge.* With network time OFF the wall clock's offset from a time server was about 1.15 s on
  2026-10-05 and grows about 0.3–0.5 s per day (gate-prune plan §4), so turning network time ON one night later
  corrects roughly 1.3–1.8 s, far above 5 ms.
- *Effect.* G10's result is a disclosed diagnostic (`g10.discharged`, `g10.not_discharged`, `g10.unmeasured`,
  `g10.interrupted`, `g10.error`). It touches no ALPHA-1 number, because each member carries its own anchor bound. A
  result other than DISCHARGED goes to one consult before BETA arms.
- *Frequency redraw.* G10 leaves a new f. If the next arm's frequency gate refuses (§4.2), the desk redraws f before
  re-arming: network time ON; read f once a minute; OFF as soon as |f| ≤ 3.0 ppm or after 15 min; re-read f 10 min
  later; up to three cycles, then a consult. This loop reads only the frequency word, never an energy.

**a1 and a2 (the arm-then-abort controls) retire.** Their two physical questions are answered without a window:
does a refusal before launch leave nothing launched and nothing changed (the driver's tests inject each hazard
REFUSE and compare the ledger, `~/Library/LaunchAgents`, the custody roots and the network-time state before and
after; the desk dry arm of §2 item 6), and does arming run end to end on native output (every real arm writes
`hazards/arm.json`). The watchdog's stand-down (the supervising process asks every agent session to exit, then
terminates and kills any that remain, at t0 − 8, −6 and −5 min) is recorded live at ALPHA-1's arm.

**s1 (the one-quad qualification window) becomes ALPHA-1.** ALPHA-1 contains everything s1 had: pre calibration, the
NEG-8 corpus and bound, references, null quads and post calibration. s1's structural checks run at ALPHA-1's harvest
as disclosed diagnostics (`diagnostic.s1_structural`): strict validation, re-reduction and a deliberately incomplete
finalization; the p42 precheck counts; the longest and shortest stream sizes; stage timing outside members.

## 4. The arm: physical hazards, measured directly

### 4.1 Order

Everything below runs inside the launchd job after t0, so no person or agent session is present.

1. **Agent census** (§4.5).
2. **Instant reads:** battery, thermal, disk, and the clock's frequency gate.
3. **Network time OFF, as an action** (§4.4).
4. **Record-only collectors:** the executed-file inventory, the model-identity check, and the checkout identity,
   each in a subprocess with a timeout. Their findings are flags (§6); they never change the arm decision.
5. **Instrument cadence probe:** about 40 s.
6. **Dwell:** 600 to 2700 s, during which contention and clock linearity are measured.
7. **Final reads** of battery, thermal and the frequency word, and the agent census again; then GO; then the monitor
   starts; then the chain launches.

The chain therefore starts 11–47 min after t0. A refusal at any step ends the attempt as NULL (§7.1) with nothing
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
  consecutive samples is a `clock.step`; a change of f is `clock.frequency_changed`.
- *Replaces:* the 8 ppm sizing convention of revision 2 and the network-time OFF receipt's wording check. There is
  no resync at the arm: the wall clock's absolute offset enters no energy, because the anchor fit and every phase
  edge use relative times.

**Battery** (directive #421). *Forcing problem:* a capture taken while the battery charges, or supplies part of the
load, is registered as confounded (`battery_float_confounded`; decision log, amendment A-R5b of 2026-09-25): the
machine is not in the one power state, everything from the adapter and the battery idle, that every registered
number assumes. The rule is decided from instrument state alone, never from an outcome.
- *Measurement:* `ioreg -r -c AppleSmartBattery`, raw bytes kept: ExternalConnected, IsCharging, InstantAmperage
  (signed), Amperage (the gauge's average), UpdateTime, Voltage, and the `PowerTelemetryData` accumulators. The gauge
  **publishes** a new reading once every 60 s.
- *Arm:* ExternalConnected Yes; IsCharging No; |InstantAmperage| ≤ 200 mA; the reading no older than 180 s.
- *In window:* polled every 5 s; raw bytes stored at every publication. The member rule is §6.4.

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
- *Arm (the dwell):* 30 s intervals; an interval is clean when no outside process exceeds 0.05 CPU-s/s, including
  `kernel_task`. GO needs 600 s of consecutive clean intervals; none within 2700 s refuses.
- *In window:* every 10 s. `kernel_task` is excluded in the window, because its time during a request is the
  workload's own driver and I/O work; its share is journaled and disclosed. The member rule is §6.4.

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
  "contention": {"cpu_limit_s_per_s": 0.05, "interval_s": 30, "clean_s": 600, "cap_s": 2700,
                 "window_interval_s": 10, "aggregate_cpu_limit_s_per_s": null},
  "disk":       {"planned_bytes": 22710059008, "headroom_bytes": 21474836480, "low_bytes": 10737418240},
  "instrument": {"frames": 300, "bound_s": 55.0, "median_ms_max": 150.0, "max_ms_max": 200.0}
}
```

`aggregate_cpu_limit_s_per_s: null` means the whole-machine CPU total is journaled at the dwell but not judged; only
the per-process limit decides.

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
   bundles of the same two models, without loading a model. Its draft SHA-256 at `f8164893` is
   `039d3e3c79d75a8bbf935d73bab3f94b0bf0ccf9ca3df5f199848f849dda9160`; the seal binds the bytes at H_claim.
   Two programs compare against these pins. At the arm, the driver passes the file to the model-identity collector
   (`--identity-pins`) when the measurement checkout holds it. At harvest, the harvest reads its archived copy. If
   either finds no pin to compare against, it records `model.identity_unpinned`, which removes the window (§6.5).
4. **Packs:** the three packs at H_claim (§0.7), with the pin bundle of the packs: prompt pin
   `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`, selection
   `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`, ladder
   `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
5. **Policy:** §0.13, `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`.
6. **Ledger seed:** block 3's ledger at pin 402 (§0.11), installed at the measurement checkout's default ledger
   path, `<checkout>/runs/calibration_observation_ledger.jsonl`, because the controller's pre-calibration route reads
   that path; the plan writer refuses at the desk if the plan names another. Before each arm the desk runs the
   read-only ledger readiness check; a session left open by an abandoned attempt is closed with the existing abort
   plus a committed pin advance. For each later attempt the seed is the previous attempt's harvested terminal ledger,
   whose tip the merged pin advance names.

A change to any item after the seal needs a prospective cold erratum before the next arm (§10).

## 5. Window shape and sizing

### 5.1 The chain

The chain runs its pack's stage graph in block 3's order: the bracket reservation; a 180 s settle; the pre
calibration and its screen; the NEG-8 corpus and the bound derivation; the start triplet; the science stages with
the pack's interior references in their places; the end triplet; the post calibration and a record of the bracket
session's status. Every collection stage starts with its own 180 s settle.

- **The only stops**, all before member 1 (about 15 min into the chain): a failed reservation, a failed pre
  calibration capture, and a pre fiducial bound above the pre screen 0.036462861644980 s
  (`instrument.precal_screen_failed`). Outside the chain, the driver stops it on `disk.low`, on a non-clean census
  and at the window deadline (§5.5).
- Every other stage records its return code and the chain continues. A chain that reaches its end exits 0 whatever
  its stages returned; the flags, not the return code, decide claim use.
- The bracket binding and the whole-window verdict are not chain stages. The harvest produces them at the desk with
  the production writers (`prepare_desk_verdict`). The backups are not chain stages either: they are a desk step after
  the harvest (§5.6).

### 5.2 A failed member costs only itself

Every science and auxiliary stage in the committed packs passes `--max-failures 1`, so one admission abort today
drops the rest of a 20-member stage. The chain writer passes `--max-failures <the stage's expected member count>`
instead. This is a **registered deviation** from the pack bytes (§10). The plan trees' `attempt_policy`
(`abort_window_on_any_required_member_failure` in ALPHA and BETA, `abort_window_and_demote_to_non_claim_bearing` in
GAMMA) is read only by the retired freeze author (`arm_readiness_evidence.py`); it is superseded by the flag catalog
and disclosed, not regenerated.

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
group with no signal, then the existing termination proof); the monitor stops; G10 runs if the plan asks (§3); the
driver writes its terminal record. The harvest may open as soon as that terminal record exists (§7.1), because the
driver holds nothing after it. The supervising watchdog does not yet release the window at that point (§5.5,
§14 Q8).

### 5.5 Sizing

- **T_stream_max** = 335 s for every window (§0.14). The sizing output records each pack's own longest stream:
  ALPHA's is 314 s (its members are all 1.7B-class), and BETA's and GAMMA's are 335 s (their 8B members). It sets
  every pack's `T_stream_max_s` to the block's longest, 335 s, at which the frequency gate passes for
  |f| ≤ 3.6306 ppm.
- **Programmed span.** The programmed span is the chain's length if every member takes its longest allowed path.
  The rule keeps block 4's conventions and uses block 5's chain:
  - span = (1 + collection stages) × 180 s settle + the stages' 20 s arm countdowns + the pre and post calibration
    pair (770 s) + the bound derivation (60 s) + the sum of member allowances + stage custody + the terminal shutdown
    (300 s);
  - a **member allowance** is load + warm-up + prefill + forced decode + the cooldown at its 300 s cap + both
    idle-admission attempts (275 s: two attempts of 110 s each plus guards, against an observed attempt maximum of
    103.6 s at 75 s idle). That is 595 s for a 1.7B member and 619 s for an 8B member. NEG-8 and reference members
    are charged as 1.7B members;
  - **stage custody** (the bookkeeping time around members) is 180 s per collection stage, plus 77 s per member
    (45 s reduction, 32 s sampler start and wind-down), plus 2 × 240 s bracket-writer custody, 300 s reservation and
    120 s terminal custody.
- **`WINDOW_MAX_S`**, the window's deadline measured from t0, = 60 × ceil((span + 3300 s) / 60). The 3300 s is the
  arm's allowance: the dwell cap of 2700 s plus the census, reads, network-time OFF, collectors and cadence probe.
- **`B5-SIZING-OUTPUTS`** (filled; draft values, re-derived and sealed at H_claim):
  `configs/campaigns/v5_claim_25g83/sizing_b5.json`, schema `joulewise.b5_sizing.v1`, SHA-256
  `9d16edfe6c7f508f5908d1222326df5acadf1610ac2a472cb069db33652bee1f` at `f8164893` (status `UNSEALED_DRAFT`).
  `scripts/size_b5_window.py` writes it from block 4's committed sizing source
  (`configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json`, SHA-256
  `f414301cd0328236f9309962b60ff4635026dac973ca3b0ce564b677c47baa81`) and from the packs' stage graphs, order
  manifests and configs. `--check` reproduces the file byte for byte. The program also refuses unless its
  arithmetic reproduces block 4's committed 22,494 s span and 25,800 s window. Each window plan reads
  `/packs/<label>/programmed_span_s` and `/packs/<label>/T_stream_max_s` from it. GAMMA's pack changes before GAMMA-1
  (§2), so GAMMA's row is re-derived then.

  | Pack | Members, 1.7B-class / 8B | Programmed span | `WINDOW_MAX_S` | Expected chain (below) |
  |---|---|---|---|---|
  | ALPHA | 119 / 0 | 85,978 s (23.9 h) | 89,280 s (24.8 h) | 32,264 s (9.0 h) |
  | BETA | 19 / 100 | 88,378 s (24.5 h) | 91,680 s (25.5 h) | 33,314 s (9.3 h) |
  | GAMMA | 61 / 40 | 74,842 s (20.8 h) | 78,180 s (21.7 h) | 28,427 s (7.9 h) |

- **Why the deadline is about 2.7 times the expected chain.** The rule charges every member, at once, both worst
  cases: the cooldown runs to its cap and idle admission needs its second attempt. *Worked decomposition, ALPHA:*
  119 members × 595 s = 70,805 s. Of that, 35,700 s is every member's cooldown at its 300 s cap and 32,725 s is
  every member's two admission attempts. Per-member custody adds 119 × 77 = 9,163 s. Settles, countdowns,
  calibration, derivation, stage custody and shutdown add the other 6,010 s, for a span of 85,978 s. Block 3 measured
  a start-to-start member cycle, which already includes cooldown and custody, with a median of 236.5 s and a maximum
  of 274.9 s. Each member here is charged 672 s (595 + 77).
- **Is that right? As a deadline, yes.** A chain stopped at its deadline loses its post calibration, and so the
  whole window. The deadline must therefore never cut a slow window that could still be claim-usable. A chain
  anywhere near this bound would have most members at the cooldown cap, and `member.cooldown_cap_hit` removes such
  members, so that window would fail the 8-of-10 minimum anyway. The generous size cannot cut a usable window and
  touches no number.
- **What it costs: withdrawn claim.** Revision 3 said a large `WINDOW_MAX_S` costs nothing because the harvest opens
  at chain exit. The code says otherwise. The supervising watchdog (`scripts/magistrate_watchdog.py`,
  `plan_span_active`) treats a window's plan as active until t0 + `WINDOW_MAX_S` + 300 s, even after `chain.exited`
  exists. While any plan is active it launches no **headless agent session**, meaning a model session that the
  watchdog starts with no person present, which is how unattended work resumes after a window. The watchdog records
  this hold as `FENCED`. The dead-man job, the second scheduled job that cleans up if the driver dies, is timed from
  the same instant. ALPHA's chain normally ends 9.2–9.8 h after t0 (an 11–47 min arm plus a 9.0 h chain), but the
  fence holds until 24.9 h after t0. That leaves about 15 h in which the machine is idle and no headless session may
  run the harvest or arm BETA. Across the three windows, that is about 44 h.
- **Fix (code, before ALPHA-1; §14 Q8).** End a collected window's span at the driver's terminal evidence:
  `chain.exited`, the driver's terminal `result.json`, `courier.sent` (the marker that the driver's structure-only
  notice went out), and no driver process alive. The watchdog already releases a delivered refusal that captured
  nothing on the same kind of evidence: the terminal `result.json`, `courier.sent`, and an empty census and driver
  probe. After the fix, `WINDOW_MAX_S` bounds only a hung chain or a dead driver, and the size
  above costs only the time to notice one. Shrinking the size is not proposed: it would save hang-detection time
  only, and every cut would risk stopping a usable window.
- **Expected chain time** (planning only; it gates nothing). From block 3 at 75 s idle: median start-to-start member
  cycle 236.5 s, plus 10.5 s for an 8B member; per collection stage 180 s settle + 39 s head + 62 s tail; fixed
  180 s settle + 770 s calibration pair + 60 s bound derivation + 300 s terminal (scratch `sizing_v2.json`, SHA-256
  `6a82745f47b40c8aa1ea6aefe2c45c2d4cce2b7a7e65d114165057e64fae00de`). Each pack has 10 collection stages.
  - ALPHA: 1,310 + 10 × 281 + 119 × 236.5 = 32,264 s ≈ 9.0 h.
  - BETA: 1,310 + 2,810 + 19 × 236.5 + 100 × 247.0 = 33,314 s ≈ 9.3 h.
  - GAMMA: 1,310 + 2,810 + 61 × 236.5 + 40 × 247.0 = 28,427 s ≈ 7.9 h.
  Each window adds its 11–47 min arm. (The gate-prune plan's 9.1, 9.4 and 8.0 h include a 360 s launch allowance that
  is no longer inside the chain.)
- **Deadline stop.** A chain still running at t0 + `WINDOW_MAX_S` is stopped by the driver; the window then has no
  post calibration, so it is not claim-usable (`calibration.no_bracket`). The next attempt's per-member allowance
  becomes the larger of the sizing output's and the stopped attempt's largest observed member cycle, plus the sizing
  margin, and `WINDOW_MAX_S` is re-derived by the rule above without an erratum (member cycles are structural timing,
  releasable under §8).
- **Block duration.** Assume every window is claim-usable on its first attempt. If the watchdog releases each window
  at its chain's exit (the fix above), the block takes about 35–45 h, including desk gaps and any frequency redraw
  before BETA. With the watchdog as it is at `f8164893`, each window holds headless work off until
  t0 + `WINDOW_MAX_S` + 300 s. That is 89,580 + 91,980 + 78,480 s ≈ 72 h for the three windows, before desk gaps.

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
| PHYSICS_IN_SPAN | §6.4 | EXCLUDE_MEMBER |
| ROSTER | §6.7 | EXCLUDE_MEMBER (window-level roster failures: EXCLUDE_WINDOW) |
| RECORDS | receipts, lineage formalities, attempt history, pin ledger, provenance digests, naming, notices, missing journals | DISCLOSE (one exception: source bytes changed during the harvest, EXCLUDE_WINDOW) |
| DIAGNOSTIC | network-time output, clock steps and frequency changes outside any span, `kernel_task` share, G10, s1-structural checks | DISCLOSE |

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
- its #421 per-capture battery pair is present and fails (`battery.capture_pair_failed`);
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

**Battery.** The publications **in force** for a span are the last publication at or before its start, every
publication inside it, and the first publication at or after its end.
- `battery.member_span`: any in-force publication has |InstantAmperage| > 200 mA, |Amperage| > 200 mA, IsCharging
  Yes or ExternalConnected No; or any 5 s poll inside the span reads IsCharging Yes or ExternalConnected No.
- `battery.accumulator_excursion`: for an interval between two consecutive publications that overlaps the span, an
  accumulator implies a mean battery power above 200 mA × the publication's voltage over its counted ticks. **Units
  (lane L1, 2026-10-05, on 66 archived publications and a live read):** each `Accumulated*` field adds its
  instantaneous value in mW once per tick (about 1.01 s), each `*AccumulatorCount` counts ticks, and battery power is
  split by sign into a charge accumulator (`AccumulatedBatteryPower` / `BatteryPowerAccumulatorCount`) and a
  discharge accumulator (`AccumulatedBatteryDischarge` / `BatteryDischargeAccumulatorCount`); the split was proven by
  an exact identity on all 65 intervals. So Δ(accumulated) ÷ Δ(count) is the mean power in mW over the ticks on which
  that sign occurred, and the registered scale is 0.001 W per unit. *Positive control:* between the 2026-09-25 20:47
  and 2026-10-01 06:17 publications the discharge accumulator gained 15,043 ticks at a mean of −5,415 mW; the gauge
  reading inside that interval was −447 mA at 12,180 mV = −5,444 mW; they agree within 0.6%.
- *Worked example (synthetic):* a span runs from 1,000 s to 1,240 s; publications at 950, 1,010, 1,070, 1,130, 1,190
  and 1,250 s are all in force. If the 1,250 s publication reads InstantAmperage −447 mA, the member is flagged even
  if the discharge began after the span ended: the rule is conservative and can also flag a neighbouring member. If
  between 1,190 s and 1,250 s the discharge accumulator gained 40 ticks totalling −216,000 mW·ticks, its mean is
  −5,400 mW, above 200 mA × 12.18 V = 2,436 mW, and the member is flagged.
- `battery.unmeasured`: no publication was observed for more than 120 s overlapping the span, or an in-force
  publication lacks a needed field.
- Brief battery assist below the limit is disclosed, not excluded (`battery.accumulator_activity`): every archived
  calibration capture shows 7–32 discharge ticks at −122 to −151 mW while InstantAmperage read 0.

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
- `calibration.capture_invalid`, `calibration.capture_battery_pair_failed` (a calibration captured while the
  battery was not floating), `calibration.bracket_acceptance_failed` (evaluated with the acceptance's ledger-cutoff
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
offset; `kernel_task`'s CPU share and monitor probes falling inside phases; a missing #421 per-capture pair
(`battery.capture_pair_missing_covered` when the continuous journal covers the span; `battery.capture_pair_missing`
otherwise, beside the `battery.unmeasured` that then removes the member); `battery.accumulator_unavailable` (the
accumulator rule could not run on an interval; the publication rule still applies); clock steps and frequency
changes outside any span; `disk.low` (its effect arrives through `calibration.no_bracket`); the desk's ledger
readiness checks before an arm (`calibration.ledger_not_ready`, `calibration.ledger_readiness_unmeasured`); the G10
result; the s1-structural diagnostics.

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

### 9.2 #421: battery float

Checked at the arm (§4.2) and journaled continuously in the window (§6.4). Every capture's raw pre/post `ioreg` pair
is kept as data and authenticated at harvest; a pair that fails removes its member (or, for a calibration, the
window), and a missing pair is disclosed. **Limitation, measured:** the gauge publishes InstantAmperage once every
60 s. An excursion shorter than that is seen through the averaged Amperage and the 1 s accumulators (§6.4); the
in-force rule over-excludes rather than under-excludes. This replaces revision 2's "endpoint pairs cannot see an
excursion" limitation.

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
| Sizing | `B5-SIZING-OUTPUTS`: filled in revision 4 with draft values (§5.5); re-derived and pinned at H_claim | Seal |
| Disk | `BACKUP-DESTINATIONS`: filled in revision 4 (§5.6) | Seal |
| Identity pins | `identity_pins.json` (§4.6 item 3): draft at `f8164893`; pinned at H_claim | Seal |
| Blinding | `B5-BLIND-CUSTODY-MAP`, `B5-RELEASE-EVENT` | Map at seal; release after the block closes |
| Boundary | `BOUNDARY-LABEL`: filled in revision 4 (§1) | Seal |
| Attribution floor | `ATTRIBUTION-FLOOR-BINDING` | Seal |
| Seal | `B5-SEAL-RECORD` | Seal |

Still open after revision 4: `H-CLAIM`, `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS`, `B5-SEAL-RECORD`,
`B5-DRY-RENDER-RECORD`, `B5-DRY-ARM-RECORD`, `B5-BLIND-CUSTODY-MAP`, `B5-RELEASE-EVENT` and
`ATTRIBUTION-FLOOR-BINDING`. None can be filled from committed bytes: each names a commit, a record or a ruling that
does not exist yet.

Removed from revision 2 because the mechanism they bound is retired or now measured: `V5-PACK-REGEN-RECORD` and
`V5-IDLE-SECONDS` (done, PR #481), `B4-*`, `L10-A-RATIFICATION-RECORD`, `Q110-CLOSURE`, `A6-AT-H-CLAIM`,
`V5-TRANSACTION-GO-01-DISCHARGE`, `AUTH-<label>`, `CAMPAIGN-PERMITTED-BLOCKS`, `STEP6-RECORD`, `CENSUS-ARGV` (§4.5),
`ANCHOR-RUNTIME-EFFECT` (either way the member is removed), `HARVEST-OPEN-RULE` (§5.4), `CLAIM-CHAIN-SUCCESS-RC`
(§7.1), `CLAIM-HARVEST-CLI` (`scripts/harvest_b5_window.py`), `G3-CLAIM-ARGS` (the harvest runs G3 on GAMMA; floor
packs have no analysis manifest), `ED-PREDICATE` and `ED-DISPOSITION` (§6.4 contention), `SPOTLIGHT-EXCLUSION` and
the disk ledger FILLs (measured by the contention and disk hazards), `B5-ATTEMPT-BUDGET` (attempts are planned, never
capped), `LONGEST-STREAM-SIZING`, `SHORTEST-STREAM-SIZING`, `REF-STREAM-FLOOR` (T_stream_max is committed; the 75 s
idle gives at least 97.5 s of idle stream, above the 60 s minimum), `COURIER-BLINDNESS-CAMPAIGN` (§8 item 2), and the
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
- **Q6. The sensitivity line (seal gate).** Analysis plan §8 proposes a labelled line over all members removed only
  by physics-in-span codes, to expose the bias that such exclusions can introduce (battery assist, thermal pressure
  and contention plausibly correlate with load, most of all on 8B prefill-p2048 members). Adopt or strike.
- **Q7. Ed's hardware setting (optional).** A fixed 80% charge limit with Optimized Battery Charging off avoids arms
  refused because the OS chose to charge.
- **Q8. The watchdog holds each window open until its deadline (lead; code lane before ALPHA-1).** §5.5 gives the
  arithmetic. `plan_span_active` in `scripts/magistrate_watchdog.py` keeps a collected window's plan active until
  t0 + `WINDOW_MAX_S` + 300 s even after `chain.exited`, so about 15 h of each window passes with no headless session
  able to harvest or arm. Fix: release a collected window's span on the driver's terminal evidence (`chain.exited`,
  the terminal `result.json`, `courier.sent`, and no driver process alive). The watchdog already releases a delivered
  refusal that captured nothing on the same kind of evidence. The change touches no number. It should land before
  the seal, so that H_claim carries it.

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
