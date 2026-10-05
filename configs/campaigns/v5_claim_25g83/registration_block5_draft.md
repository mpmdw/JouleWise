# Registration V5-CLAIM-25G83-B5: the first claim-bearing `_v5` windows (measurement block 5)

Status: **DRAFT UNSEALED, revision 2, 2026-10-05.** Written by an Opus 5.5 design seat for the lead on branch
`design/2026-10-05-v5-claim-block-draft` (revision 1 was `9900a047`, based on the block-4 design head `4fc184bd`).
Revision 2 answers three blind critiques (science, feasibility, replicability); the disposition of every critique
item is the last section of the companion analysis plan. This file authorizes no arm, no launch and no analysis.
It binds only when a cold gate (§0.1) seals it together with its companion analysis plan
`configs/campaigns/v5_claim_25g83/analysis_plan_block5_draft.md` (§13). A **FILL** is a value that must be tied to
authenticated bytes (§0.1) before the due point named in §14; it is never a default, and an arm with an unresolved
FILL due at or before that arm refuses. No claim-eligible `_v5` energy data exists at this writing, and none was
read (§16).

**The one change that cannot wait.** The three committed packs ask for a 30 s idle baseline. At that length every
member's sampler stream is shorter than the 60 s the clock-anchor method requires, so every member, and therefore
block 4's `s1` and every window here, would be refused with `clock_fit_span_insufficient` (§5.3). The packs, the
reference configurations and everything that pins their hashes must be regenerated before block 4 seals (§2.0,
§15 Q14). The same regeneration fixes GAMMA's duplicated interior reference (§3.1) and the in-chain verdict that
cannot see its bracket binding (§5.1).

## 0. Terms, built in the order they are used

### 0.1 People, seats and records

- **Ed** is the owner of the capstone project and of this machine. **The lead** is the orchestrating Opus 5.5
  session that dispatches seats, decides, records dissent and merges (D-186). A **seat** is one model session the
  lead dispatches with a written brief: Sol 6.1 (`gpt-6.1-sol`, high effort, the default implementation and review
  seat), Opus 5.5, or Fable 5.1. Ed asked on 2026-10-05 to use Fable less for now; seat choices that name Fable are
  marked as such (§15 Q6).
- **Consult.** One blind round from two seats (Sol 6.1 and Opus 5.5), each licensed to disagree; the lead decides
  and records dissent. **Cold gate.** An independent ruling on a named question by a **judge** seat with no prior
  involvement, checked by a **refuter**: a second independent seat, from a different model family where possible,
  whose job is to try to show the ruling wrong. A refuter's challenge that survives goes back to the judge once; a
  disagreement settles in one erratum, not a chain (orchestration doctrine, gate 2).
- **R3.** The standing route for a tooling fault: fix it in a reviewed, gated pull request, merge, then re-run the
  failed *desk* step on identical bytes. R3 never re-collects anything.
- **Authenticated.** A file is authenticated when it is read through the repository's authentication reader
  (`joulewise/authentication_io.py`), which refuses links and non-regular files and compares the bytes with a
  SHA-256 recorded beforehand in a committed file or a custody record. To **tie** a value to a file means to record
  the file's path and SHA-256 beside the value.
- **Custody.** A directory whose files are written once, never modified, and listed with their SHA-256s. **Restricted
  custody** is custody that only automation and the release event (§9.4) may read; nothing in it is printed,
  emailed or committed during the measurement block.
- **Courier record.** The driver's (§0.17) durable report of one attempt: a file on disk and an email to Ed, written
  when the attempt ends.

### 0.2 The machine and the sampler

The machine is one Apple M3 Max laptop (model identifier Mac15,9) running macOS build 25G83 on mains power.
Everything below happens on that one machine.

- **Sampler.** macOS `powermetrics`, asked for one **power record** every 100 ms. It never samples faster than
  asked; in block 3 a record actually spanned 127–130 ms (median 128.8 ms; scratch `b3_anchor.json`, §16). Each
  record states the average power over its own time span (its **support**) of the processor rails, CPU, GPU and
  ANE combined: `combined_power_w` in the parsed record (`joulewise/adapters/powermetrics.py:91`), carried as
  `power_w` in the reducer's trace.

### 0.3 A member, step by step

A **member** is one run of one inference request in its own process. Its steps, in order:

```
 prepare | idle baseline (idle admission; retry if refused) | warm-up | measured request | cleanup | reducer
          |<------------------------ sampler stream ----------------------------->|
 ...then, before the next member of the same stage starts: cooldown (§0.6)
```

- **Idle baseline.** The sampler records the idle machine for the configured `idle_seconds` (§0.13); idle
  admission judges it.
- **Warm-up.** One untimed generation of the same request (`warmup_runs: 1`), so the measured
  request does not pay first-call costs.
- **Measured request.** The request whose energy is reported; 11.1–23.6 s long in block 3 (`measured_run` stage of
  all 24 members; scratch `measured_run.txt`, §16).
- **Reducer.** The program (`joulewise/reduce.py`) that turns the raw power records and the event timestamps into
  the member's summary (`summary_metrics.json`).
- **Sampler stream.** One continuous `powermetrics` process that runs from the start of the idle baseline to the
  end of the measured request. An idle-admission retry stays inside the same stream (the second idle slice is
  taken from the running process, `powermetrics.py` `measure_idle`), so a retry lengthens the stream. The cooldown
  is outside it.
- **Bundle.** The member's immutable directory of raw files, events and summary.

### 0.4 Phases and phase energy

- **Phase.** A named, timestamped part of the measured request. **Prefill**: the model reads the whole prompt and
  computes the first output token; it ends at the first streamed token (`phase_boundary_method: first_token`).
  **Decode**: the model produces the remaining output tokens.
- **Phase energy.** Each power record contributes its power times the length of the overlap between its support
  and the phase (`reduce.py` `_integrate`). Records wholly inside count in full; a record that straddles a phase
  edge counts in proportion to its overlap; records outside count zero. No idle power is subtracted (**gross**
  energy).
  *Worked example (synthetic).* A phase runs from t = 10.00 s to t = 10.25 s. Record 1 covers 9.90–10.03 s at 20 W:
  overlap 0.03 s, 0.60 J. Record 2 covers 10.03–10.16 s at 30 W: overlap 0.13 s, 3.90 J. Record 3 covers
  10.16–10.29 s at 30 W: overlap 0.09 s, 2.70 J. Phase energy = 7.20 J.
- A phase needs at least 3 overlapping records or the reducer refuses it (`MIN_PHASE_SAMPLES = 3`,
  `reduce.py:116`; outcome `not_resolvable_sample_count`). Each phase also carries a **precheck**
  (`window_evidence_precheck`), a per-phase list of pass/fail tests on its timing evidence (record count, record
  regularity, clock bound against the phase length; full list in `joulewise/whole_window.py`
  `_METRIC_LOCAL_PRECHECK_REASONS`).

### 0.5 The two workloads

- **Decode workload.** The real prompt 0 of `real_prompts_v1`, rendered through the Qwen3 chat template with
  thinking off, which gives a 42-token prompt (the packs' condition family `prompt_tokens: 42`; decode prompt
  manifest SHA-256 `31301c9df7e1f79c027d05a8b8e6022bf4d14e22b9c7f77ce8431b0ac3256694`). Output is forced to exactly
  512 tokens: greedy decoding, end-of-sequence suppressed, `max_tokens` 512 (D-166 and its 2026-09-04 addendum).
  Because prefill computes the first output token, the decode phase spans the other 511 generation steps; the
  decode per-token value nevertheless divides by all 512 runtime-observed output tokens (D-179 per-token sibling;
  analysis plan §4).
- **p42.** The prefill phase of the decode workload: 42 prompt tokens, a few tens of milliseconds, shorter than one
  power record. Block 3's comparably short phases (`tokenize`, `generation_setup`) overlapped 1–2 records and failed
  their prechecks on all 24 members (scratch `b3_flags.out.txt`). The p42 cells are therefore registered as
  **expected unresolvable**; their refusal blocks nothing (analysis plan §2.2, §3).
- **Prefill workload.** A prompt of exactly L = 2048 tokens (token-ID hash
  `202e4913340b2bae39bf9a9d3a314f62bb5ff783fae483ad6a98507d071e1479`), 512 output tokens. Block 3 selected L
  (`selection.json`, SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`) as the shortest of
  512/1024/2048/4096 at which every small-model probe member's prefill overlapped at least five records. Five is a
  selection margin, not a second rule: the reducer's hard minimum is 3, and selecting at 5 leaves room for a run
  whose prefill catches fewer records than usual. At L = 2048, all six block-3 prefill phases (five small, one 8B)
  passed their prechecks (7 and 26 records); at p512, two small members failed with `cadence_ratio_below_threshold`.

### 0.6 Stages, settles and cooldowns

- **Stage.** One ordered list of members that `scripts/run_campaign.py` runs as a unit. Every stage starts with a
  180 s **settle**: the chain sleeps so the machine returns to idle (`docs/phase_2/window_runbook.md`
  `SETTLE_S=180`).
- **Cooldown.** Between members of a stage the runner waits until the processor power has been steady for 30 s
  (judged in 5 s sub-windows, within 10%) and the thermal state is nominal, or until the 300 s **cap**
  (`quiet_mac_p2_production.json` `cooldown`). A member whose cooldown reached the cap is flagged
  `cooldown_cap_hit` (`run_campaign.py`, around line 6718).

### 0.7 Packs, attempts, windows and the measurement block

- **Pack.** The frozen, hash-pinned set of stages, member configurations and plans for one window. Its **pack plan
  tree** (`plan_tree.json`) lists the stages in order (`stage_graph`) with their inputs and commands. A **freeze
  receipt** records the pack's digest (`joulewise.committed_pack_tree_sha256.v1`) at a commit; the plan tree points
  to it. Three packs exist, merged to main in PR #477 (`c88565c4`, pack commit `db41703c`): **ALPHA**
  `d117_floor_qwen3-1p7b_v5` (Qwen3-1.7B, 4-bit), **BETA** `d117_floor_qwen3-8b_v5` (Qwen3-8B, 4-bit) and **GAMMA**
  `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (both models). They must be regenerated before use (§2.0).
- **Attempt.** One arm-to-harvest occurrence of one pack, labelled `ALPHA-n`, `BETA-n` or `GAMMA-n`, n = 1, 2, …
  Its **attempt plan** is the driver's per-attempt plan file, with `plan_id` and `attempt_id = "<plan_id>/<n>"`
  (pack GO contract §8.2). A **window** is the stretch of machine time an attempt occupies, from T-0 (§0.17) to its
  harvest.
- **Measurement block.** A registered set of windows sealed under one registration. This file registers measurement
  block 5; block 4 is the qualification block (`configs/campaigns/v5_qualification_25g83/registration_block4_draft.md`).

### 0.8 Quads, contrasts and independence

- **A/B/B/A quad.** Four consecutive members in the order A1, B1, B2, A2. (The code and the manifests call this a
  "block": `block_ids`, `paired_block_incomplete`. This file says **quad** so that "block" means only a measurement
  block.) A and B are the quad's two **sides** (the code says "arms").
- **Contrast.** In GAMMA, side A is Qwen3-1.7B and side B is Qwen3-8B, with the same workload. A quad's difference
  is `d = (B1 + B2)/2 − (A1 + A2)/2`; the **contrast** is the mean of d over GAMMA's ten quads for one phase.
- **Null quad.** In ALPHA and BETA both sides are the *same* model and workload, so any apparent A-versus-B
  difference can only come from the instrument and the machine.
- **Why A/B/B/A.** A slow linear drift cancels inside a quad. *Worked example.* If every member reads δ more than
  the one before it, the members at positions 0, 1, 2, 3 carry 0, δ, 2δ, 3δ of drift; side A (positions 0 and 3)
  averages 1.5δ and side B (positions 1 and 2) averages 1.5δ, so d gains 0. A curved drift does not cancel: with
  drift k² at positions k = 0…3, side A averages 4.5 and side B 2.5.
- **Absolute repeat.** One member run on its own (not in a quad), ten in a row per workload.
- **Independence unit.** A group of members the statistics treat as one independent draw: each quad is one unit,
  and each absolute repeat is one unit. D-179 fixes 20 units per reported cell: 10 repeats plus 10 quads.
  Consecutive members do share slow drifts (temperature, background load), so independence between back-to-back
  units is a **modelling assumption**, not a measured fact. D-179 says so ("the protocol's dependence caveat
  persists"), and every reported interval carries that caveat (analysis plan §8).

### 0.9 Reported cells

A **reported cell** is one registered energy number per model and phase, computed over a fixed ordered list of
exactly 50 members (10 absolute repeats + the 40 members of 10 null quads): three per floor pack, six in all
(`d117-reported-mean-ph-{decode,prefill-p42,prefill-p2048}-{qwen3-1p7b,qwen3-8b}`). The four **paper cells** are
decode and prefill-p2048 for each model; the two p42 cells are computed if they can be and never printed (§0.5).

### 0.10 Floors

- **Detection floor.** The largest difference the instrument produces when nothing differs, estimated from a
  model's absolute repeats and null quads; hence the smallest real difference it can resolve. A contrast whose
  estimate does not exceed its floor is reported as `not_resolvable` (formulas: analysis plan §5). A **mint** is the
  authenticated issuance of the aggregate floor artifact (`joulewise.detection_floor_artifact.v2`).
- **Attribution floor.** A different quantity: D-078's estimate, about 1 J, of how much phase energy can be
  misattributed because phase edges are timed only to within the sampler's timing error. D-179 prints it beside each
  reported cell and never adds it into the cell's interval. Its exact value, source artifact and applicability to
  25G83 are `FILL[ATTRIBUTION-FLOOR-BINDING]` (§15 Q16).

### 0.11 Pulse calibration, acceptance and ledger

- **Pulse calibration.** A capture in which the GPU is driven through 59 commanded on/off pulses (3 warm-up pulses
  before them; `joulewise/powermetrics_fiducial.py` `PULSE_COUNT = 59`). For each pulse the estimator fits the
  power records as a baseline plus a rectangle whose start and end may be delayed from the commanded times, and
  returns the interval of delays consistent with the records. The **fiducial bound** `B_fiducial` is the largest
  absolute end of those intervals over all pulses: the largest timing error between commanded and observed edges.
  With 59 pulses it is a 95/95 bound on the calibration distribution (1 − 0.95⁵⁹ ≥ 0.95).
- **Pre** and **post** calibrations enclose a window; together they are its **bracket**.
- **Acceptance.** The issued file that judges brackets:
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256
  `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`, derived from 24 calibration captures. Its
  numbers: the **pre screen** `preflight_level_screen_s` = 0.036462861644980 s (the largest fiducial bound among
  the 24; a pre capture above it stops the chain before any member); the **bracket screen**
  `bracket_screen_s` = 0.014531 s (their range); the drift allowance is max(observed |post − pre|, bracket screen),
  which must not exceed `maximum_budgetable_drift_s` = 0.01550217418713139 s. The policy file's
  `calibration_bracket_max_drift_s` = 0.01 s is recorded in run metadata as
  `legacy_obsolete_not_an_acceptance_comparator` and is not applied (`calibration_bracketing.py:2225`).
- **Ledger.** The append-only record of every calibration capture. Its last entry is the **ledger tip**; the tip
  committed to the repository is the **ledger pin**. The acceptance was derived from the ledger up to sequence 376,
  its **cutoff**; brackets are judged against that cutoff while the live ledger keeps growing.
- **Bracket binding.** The file that ties the pre and post captures to one window's session
  (`bracket-binding.json`); the whole-window verdict must read it (§5.1).

### 0.12 Reference members and the NEG-8 drift check

- **Reference member.** A member of one fixed reference workload (Qwen2.5-1.5B, 1024-token prompt, 256 output
  tokens). Each window runs 12 at its start, the **NEG-8 bound corpus** (NEG-8 is an inherited label from the
  project's negative-control list; it is a name, not an abbreviation the reader needs), then a **start triplet**,
  interior references, and an **end triplet**.
- **NEG-8 bound.** From the 12 corpus members' gross energies (and separately their idle-subtracted energies), with
  s their sample standard deviation and t = t(0.975, 11): bound = max(mean of the largest 3 − mean of the smallest
  3, t × s × √(2/3)) (`whole_window.py` `build_neg8_drift_bound_artifact`, `replicated_endpoint_bound_j`).
- **NEG-8 screen.** The window passes when |mean(end triplet) − mean(start triplet)| ≤ that bound, per family. The
  **whole-window drift allowance** is max(largest spread among the start, interior and end means, the bound); each
  member carries half of it as `E_whole_window_drift_allowance_j` (`analysis_engine/inputs.py:3877`), so a contrast
  carries it once in total. The policy's `neg8_bracket` numbers (0.05 J, 0.25) are recorded but do not gate
  (`whole_window.py`, "neither numeric tolerance gates this amended estimand").
  *Worked example (synthetic).* Corpus spread gives a bound of 0.40 J; start mean 20.10 J, end mean 20.35 J: screen
  0.25 ≤ 0.40 passes; with an interior mean of 19.90 J the spread is 0.45 J, so the allowance is 0.45 J and each
  member carries 0.225 J.
- **The check reads energies.** The NEG-8 screen reads reference-workload energies, and idle admission and the
  bracket read power and timing. None reads a science member's energy (§6, §7.2).

### 0.13 Idle admission

Before each member's request, its idle baseline must pass two sets of tests (`quiet_mac_p2_production.json`,
SHA-256 `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`):

- **Environment guard:** on AC power, external power connected, displays asleep, screensaver not running, Low Power
  Mode off, thermal state nominal; an unknown critical value fails.
- **CPU criteria** (`idle_admission_extension.cpu_criteria`): over at least 30 CPU-telemetry samples
  (`min_samples`; a count of telemetry samples, not of 100 ms power records), the 95th
  percentile of the **CPU busy ratio** (the fraction of time the CPU cores were not idle) is at most 0.5, and the
  95th percentile of processor combined power is at most 1.0 W; missing telemetry fails. The AC adapter's
  reported wattage must be known and stay unchanged.

A refused baseline is retried once, immediately, in the same sampler stream (`retry_attempts: 1`, no backoff); a
second refusal aborts the member. In a claim window an aborted member aborts the whole window (§0.16, pack attempt
policy, zero replacements).

### 0.14 The clock anchor

- **The problem.** The sampler stamps each record with its own whole-second wall-clock label and an elapsed
  duration; phase edges are stamped on the machine's clocks. To place records against phase edges, the offset
  between the two time bases must be known.
- **The method** (`joulewise/uncertainty_evidence.py`, `powermetrics_native_second_rate_aware_set_membership_v1`):
  assume wall time is affine in monotonic time over the stream (one rate, no step). Each record's endpoint, found by
  adding up the elapsed durations, must fall inside its whole-second label, widened by 250 µs. The set of
  (offset, rate) pairs that satisfies every record at once is computed exactly. Its half-width at the first record
  is **h**.
  *Worked example (synthetic).* If the first record's endpoint is labelled second 100 and the cumulative endpoints
  of later records show that the second-100→101 rollover happened between cumulative times 0.712 s and 0.716 s, the
  first endpoint is pinned to within 0.002 s either side: h ≈ 2 ms (plus the 250 µs allowance).
- **Effective bound** = h + the change in (wall − monotonic) over the stream + 1 µs stamp resolution + 1 µs
  numeric padding. The middle term is about ρ × T, with T the stream length and ρ the relative rate of the two
  clocks; in block 3, ρ was 3.25–3.28 ppm (§5.3).
- **Limits.** A member is valid only if its stream's summed record time (`rate_fit_baseline_s`) is at least 60 s
  (`MIN_RATE_FIT_BASELINE_S`; otherwise `clock_fit_span_insufficient`) and its effective bound is at most 5 ms
  (`MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S`, the D-078 limit). The result is
  `uncertainty_evidence.clock_anchor.status`; `bounded` means both hold. The status is written into the bundle's
  metadata when the capture is finalized. Whether a non-`bounded` status fails the member at run time (and so
  aborts the window) or only at harvest is `FILL[ANCHOR-RUNTIME-EFFECT]`; either way the member is invalid (§6).

### 0.15 Network time OFF

The anchor's model excludes clock steps, and an automatic network-time correction is a clock step. A **network-time
OFF receipt** is a write-once record, written by the driver (`run_night.py` `_admit_network_time_off`), that the
command turning automatic network time off exited 0 with standard output `setUsingNetworkTime: Off` or `Network
Time is already off`. Network time stays off for the whole measurement block; nothing turns it on (D-186).

### 0.16 Battery float

The battery neither charges nor discharges: `ExternalConnected=Yes`, `IsCharging=No`, signed `InstantAmperage`
within ±200 mA, ioreg `UpdateTime` at most 180 s old (directive #421, block-4 §3 item 7; reader
`joulewise/battery_float.py`).

### 0.17 Driver, arming and launch

- **Driver.** `scripts/run_night.py`, the unattended program that arms, checks and launches a window.
- **T-0.** A window's scheduled start, at which machine-authored evidence of the clock, quietness and battery is
  captured.
- **Arm.** To install an attempt so the driver will run it at T-0. **ARM** is the authenticated readiness receipt
  the driver writes before T-0; **GO** (`joulewise.pack_night_go_receipt.v1`) is its permission receipt, written
  only after ARM verifies; the **launch** consumes the GO exactly once.
- **Arm notice.** The email to Ed before each arm; Ed's NO stops that arm.
- **Authorization record.** The record naming the pack, attempt, permitted chain, purpose and claim eligibility
  (D-176 §2). Claim windows use purpose `CAMPAIGN_TRANSACTION`, `claim_eligible=true` and the authority string
  exactly `V5-TRANSACTION-GO-01` (`joulewise/night_gate.py:1010` refuses any other).

### 0.18 Chain, dwell and window length

- **Chain.** The shell program the driver launches; it runs the pack's stages in order and writes
  `night/chain.started` when it begins.
- **Clean dwell.** After the OFF receipt the driver runs `scripts/prewindow_check.sh --wait`: every sample must pass
  the script's checks for 600 continuous seconds. They include: no listed background daemon (`XProtect`,
  `mds_stores`, `mdworker`, `mdbulkimport`, `backupd`, `photoanalysisd`, `softwareupdated`, `Spotlight`,
  `mediaanalysisd`) above 5% CPU; a 1-minute load average of at most 2.0; AC power; enough free disk; no stale runs
  root; no agent or measurement process. It gives up after 2700 s (`run_night.py` `_admit_derivation_clean_dwell`,
  `min(45 × 60, …)`).
  The chain starts only after a clean dwell.
- `NIGHT_PROGRAMMED_SPAN_S` is the sum of the chain's planned allowances; `WINDOW_MAX_S` is the hard cap after
  which the driver stops the chain (`run_night.py` `_WindowDeadline`). The **start budget** check refuses a chain
  that could not finish by the cap: the chain may start no later than `t0 + WINDOW_MAX_S − NIGHT_PROGRAMMED_SPAN_S`
  (`_derivation_start_budget`).

### 0.19 Whole-window verdict

One row, written after collection by `run_campaign.py --whole-window-verdict`, stating whether the window as a whole
passed: every member admitted; the AC adapter's wattage unchanged; the CPU criteria held; the NEG-8 screen passed;
and the bracket, read through its bracket binding, passed the acceptance (`joulewise/whole_window.py`).

### 0.20 Harvest, checker and earlier blocks

- **Harvest.** The desk program run after a window: it archives the window's bytes, authenticates them and writes
  one mechanical verdict (§7).
- **G3.** The read-only desk checker `scripts/check_window_provenance.py`, run on every claim window's bytes before
  the next arm (D-162, row V5-NIGHTLY-G3-01). Its assertions S11-A1…A5 check the window's lineage against the pack:
  collection join, campaign cooldown evidence, stage roster (S11-A4: the calibration, reference and science stages
  present and in order) and the prospective manifest. Its claim-window arguments are §6.
- **G2-a** was block 3, the prefill-length probe. **G2-b** is block 4's one-quad shakedown on the real GAMMA pack,
  **`s1`**: one consuming launch that collects a single A/B/B/A quad. **L10-A**, **L10-B** and **L10-C** are the
  three desk rehearsals of `docs/process/v5-l10-rehearsal-phase.md`: L10-A proves the desk path on `s1`'s bytes;
  L10-B runs floor extraction and a rehearsal mint on copies of ALPHA and BETA; L10-C runs finalization, the claim
  gate and the results fills on a copy of the complete corpus.

### 0.21 Commits

- **H.** An exact git commit. **H_claim** is the commit whose code runs every window of this block (§12).
- **Readiness and freeze refresh.** After a ledger-pin advance, block-4 record 47 requires the arm-readiness
  evidence and the next pack's freeze receipt to be re-authored at the new commit; the pack digest changes with
  them, and the next authorization must name the new digest (§3.3).

### 0.22 The claims ladder

`docs/contracts/claims_ladder.md` fixes how strong a sentence may be. **L1** (instrument result): on this exact
**stack** (machine, OS build, runtime, model, quantization, sampler) and **boundary** (what energy the sampler
covers, here `M3 Max / MLX / powermetrics` SoC rails), this quantity was observed. **L2** (comparative result): one
condition differed from another within one boundary, with intervals reported, interleaved order, and the effect
above the detection floor. L3 (a fitted model checked on held-out cells) and L4 (replicated across machines or
boundaries) are out of reach here. **Holm** is the correction that keeps the chance of any false positive across
the two contrasts at 5%.

## 1. Purpose, and what each window can support

Block 5 collects the three claim-bearing `_v5` windows. Their bytes are the only sources of the `_v5` numbers the
capstone paper can print: the reported phase energies (D-179), the detection floors (D-117/D-124), the dominance
ratios (D-165/D-168) and the two model contrasts (GAMMA's frozen prospective analysis manifest).

**Dominance ratios, defined here because the table uses them.** For each model, phase and floor form,
R = (detection floor with each member's energy free to move within its timing uncertainty) ÷ (the same floor with
every member at its point value) (analysis plan §6). R ≥ 2 means timing uncertainty at least doubles the floor.
R_cm is the comparative version replayed with an energy change of one shared sign across all quads. The
**contingent subtitle** is the "attribution-limited" paper subtitle D-165 licenses only when every required ratio
is at least 2. These ratios are point diagnostics with no interval.

| Window(s) | What it can support | Rung | Why not higher |
|---|---|---|---|
| ALPHA alone | Reported phase energy of Qwen3-1.7B for decode and prefill-p2048, each with its D-179 interval, runtime-observed J/token and the attribution floor beside it; the 1.7B floor cells. p42 is attempted and expected to refuse | L1 | One stack, one boundary, no comparison |
| BETA alone | The same for Qwen3-8B | L1 | Same |
| ALPHA beside BETA | Side-by-side L1 cells only, labelled as collected in separate windows in a fixed order | L1 | The claims ladder keeps forced order below L2; the two models were never interleaved |
| GAMMA with the ALPHA/BETA floors | Two primary contrasts (8B minus 1.7B phase energy, decode and prefill-p2048), Holm family of two, plus the registered descriptive ratio and per-token difference (analysis plan §7.3) | L2 if and only if the claim gate's `claim_ready_for_l2_l3` is true (analysis plan §7.2) | No held-out cells (L3) and no second machine (L4) |
| Floors + GAMMA | Dominance ratios R and R_cm; the dominance sentence and the contingent subtitle only if every required ratio is at least 2 | Disclosure (not a rung) | D-165 addendum: R_cm licenses no physical-common-time robustness claim |

Every phase-energy sentence carries the D-177 limitation (phase attribution was not characterized by a measured
instrument check). Nothing here supports a prompt-population claim (one fixed decode prompt), a claim outside
`M3 Max / MLX / powermetrics` (boundary label `FILL[BOUNDARY-LABEL]`), or a claim about prompt lengths other than
2048. That an 8B model uses more phase energy than a 1.7B model on the same work is expected; the informative
quantities are the magnitudes (the contrast in joules, the registered ratio and the per-token difference), and the
analysis plan registers each. What the paper prints, and from which artifact, is fixed in analysis plan §9; under
the current D-174 fallback no `_v5` result has a paper placement, so printing anything needs the placement ruling of
§15 Q5.

## 2. Preconditions

### 2.0 Before block 4 seals (block 4's `s1` runs the real GAMMA pack)

0. **Pack regeneration** `FILL[V5-PACK-REGEN-RECORD]`, merged under the normal gates, producing new ALPHA, BETA and
   GAMMA packs and new NEG-8 corpus and window-reference configurations in which:
   a. `idle_seconds` is the value `FILL[V5-IDLE-SECONDS]`, chosen inside the feasible band of §5.3 (about 50–56 s
      under the registered convention; 55 s recommended). Every artifact that pins the changed configuration hashes
      (order manifests, the settled NEG-8 corpus `neg8_reference_corpus/derivation/settled_corpus.json`, the
      extraction specs, GAMMA's prospective analysis manifest, the reported-energy registrations) is re-issued, and
      the regeneration record lists each with old and new SHA-256.
   b. GAMMA's three interior references (`gamma-reference-decode-midpoint`, `gamma-reference-arm-boundary`, which
      this file calls the **workload-switch reference**, and `gamma-reference-prefill-midpoint`) launch three
      distinct reference configurations with distinct `run_id`s. In the merged pack all three launch the same
      one-member input `midpoint_reference` (`run_id neg8-window-midpoint`), and `run_campaign.py` skips a `run_id`
      whose complete bundle already exists (around line 8665), so the second and third would be skipped or refused.
   c. Each pack's chain stage list ends at the post calibration and the completion lifecycle event. Bracket
      binding, the whole-window verdict and the two backups become named desk steps (§5.1), as in block 4 and the
      window runbook. The merged packs' in-chain verdict command carries no `--bracket-binding`, so it would write a
      failing authoritative row (`calibration_bracket_binding_missing`, `calibration_bracketing.py:2435`).
   d. GAMMA's plan tree uses the same schema as ALPHA and BETA (`input`, the non-collection `expected_count`
      values, and an `attempt_policy.policy` key), or the renderer and the claim harvest (§12.2) state and test how
      they read both schemas, against all three trees.
   e. The idle-admission retry follows the Q1 ruling (§15).
   Because these changes alter pack bytes, they precede block 4's seal; block 4's registration takes the
   regenerated GAMMA pack.

### 2.1 Before the first claim arm

All must hold, each evidenced by a path and SHA-256, before the first ALPHA attempt (`ALPHA-1`, §3.1) arms:

1. Block 4 qualified: `FILL[B4-STRUCTURAL-VERDICT]` and `FILL[B4-QUALIFICATION-VERDICT]` are both PASS on `s1` (or
   its allowed `s2`), harvested from authenticated archives.
2. The L10-A record is ratified (`proof_scope=L10_A_G2B_CONTRACT_PREFIX`: the desk proof, on `s1`'s bytes, that
   strict validation, reduction and the deliberately incomplete finalization behave exactly as registered; the
   finalization is incomplete on purpose because one quad cannot cover a ten-quad manifest):
   `FILL[L10-A-RATIFICATION-RECORD]`.
3. The liveness limitation Q110 is closed (the readiness evidence must be under 600 s old when it is judged; at
   least three real receipt bundles must all show that margin) or re-ruled by a cold gate before ALPHA:
   `FILL[Q110-CLOSURE]`.
4. H_claim is fixed and covered by block 4's qualification (§12): `FILL[H-CLAIM]`.
5. The launch-realization recheck (A6, PR #475: the check at launch that the bytes launched are the reviewed bytes)
   is present at H_claim: `FILL[A6-AT-H-CLAIM]`.
6. This registration and the analysis plan are sealed (§13): `FILL[B5-SEAL-RECORD]`.
7. The #416 pre-arm triple audit has run at H_claim and every verified BLOCKER is cleared (§10.1):
   `FILL[416-AUDIT-RECORD]`.
8. Every launch-path program a claim window executes is present at H_claim (§12.2), and the full-chain dry render
   of §12.3 has passed: `FILL[CLAIM-LAUNCH-CODE-AT-H]`, `FILL[CLAIM-DRY-RENDER-RECORD]`.
9. The task-queue row V5-TRANSACTION-GO-01 is discharged by an agent-run record under Ed's 2026-10-05 ruling that
   owner-reserved steps are agent-run (`FILL[V5-TRANSACTION-GO-01-DISCHARGE]`), and a `CAMPAIGN_TRANSACTION`
   authorization record with authority exactly `V5-TRANSACTION-GO-01` exists for the attempt (D-176 §2; D-171 §3):
   `FILL[AUTH-<label>]`, with `permitted_blocks` per `FILL[CAMPAIGN-PERMITTED-BLOCKS]`.
10. The step-6 confirmation record for the pack family (`d117_step6_confirmation_table_v5.json`) is in transaction
    custody: `FILL[STEP6-RECORD]`.
11. The analysis code of analysis plan §11 is merged and pinned, or the lead has recorded that it will be written
    blind before the release event (§15 Q10).

## 3. Attempts and schedule

### 3.1 Three windows, in a fixed order

| Label | Pack | Science members | Auxiliary members | Calibrations | Units it delivers |
|---|---|---:|---:|---:|---|
| `ALPHA-n` | ALPHA | 100: decode 10 absolute + 40 in 10 null quads; prefill-p2048 10 + 40 | 12 NEG-8 + 3 start + 1 midpoint + 3 end = 19 | 2 | 20 units for each 1.7B reported cell (decode and p42 share the same 50 members; p2048 has its own 50) |
| `BETA-n` | BETA | 100, same shape | 19 | 2 | 20 units for each 8B reported cell |
| `GAMMA-n` | GAMMA | 80: decode 10 quads (40) then prefill-p2048 10 quads (40) | 12 NEG-8 + 3 start + 3 interior (decode midpoint, workload switch, prefill midpoint; three distinct configs after §2.0 b) + 3 end = 21 | 2 | 10 quad differences for each of the two contrasts |

Each pack's stage order is its regenerated plan tree's `stage_graph` up to the post calibration (§2.0 c). All 20
units of a reported cell come from one window, and no member, quad or cell is ever pooled across attempts or
windows, topped up or replaced (D-078).

The order is ALPHA, then BETA, then GAMMA, and a window arms only after the previous one is PASS (§7). After a PASS,
that pack is never armed again in this measurement block, so no pack has two PASS attempts. The order is fixed in
advance so that no arming decision can depend on what an earlier window showed; it is the D-117 order, it puts the
floor windows (instrument characterization) before the contrast that consumes them, and it lets the L10-B
rehearsal (§3.3) test the floor path before GAMMA spends a window.

### 3.2 One floor window, drawn to time

```
  T-0  OFF                       chain start                                                   captures end
  |    |                              |                                                              |
  [T-0][OFF][dwell 600-2700 s][launch][set][pre][NEG8][start][D1][D2][D3][mid][P1][P2][P3][end][post][stop]
       |<----- >= 600 s (both clocks) ---->|
  ...then at the desk: [binding][verdict][backups][harvest][G3][pin advance + refresh] | next T-0
```

Every element: `T-0` = scheduled start and its machine-authored evidence; `OFF` = network-time OFF receipt; the
arrow = at least 600 s on both clocks from the OFF receipt to the first capture, the pre calibration (§4 item 7);
`dwell` = clean dwell (§0.18); `launch` = launch lifecycle up to `night/chain.started`, which marks **chain start**;
`set` = 180 s chain-owned settle; `pre`, `post` = pulse calibrations; `NEG8` = the 12-member bound corpus, then the
bound derivation; `start`, `mid`, `end` = reference stages of 3, 1 and 3 members; `D1` = 10 decode absolute
repeats; `D2`, `D3` = the two 20-member decode null-quad stages; `P1`–`P3` = the same for prefill-p2048;
**captures end** = the post calibration's sampler stops; `stop` = completion lifecycle event and terminal ledger
finalization. Each stage inside the chain also starts with its own 180 s settle, not drawn. GAMMA has the same frame
with its four 20-member contrast stages and three interior references in place of D1–D3, mid and P1–P3. Every
element after `stop` is a desk step (§3.3).

### 3.3 Desk steps after each window, in order

1. **Harvest opens** at the time `FILL[HARVEST-OPEN-RULE]` permits: either chain exit plus the driver's terminal
   courier record, if a cited code fact shows the driver holds nothing after it, or otherwise `t0 + WINDOW_MAX_S +
   300` (block-3 practice, `docs/process_traces/2026-10-03-design-block3/40-g2a-b3-arm-recipe.md:27`). §15 Q15.
2. **Bracket binding**, then the **whole-window verdict** with `--bracket-binding`, then the **two backups** (claim
   root to destination 1, bound root to destination 2): named desk CLIs `FILL[B5-DESK-BINDING-VERDICT-BACKUP-CLI]`,
   run before the harvest's verdict step, each writing exactly one authoritative output.
3. **Harvest** (§7) from the authenticated archive, then **G3** on the window's bytes (§6).
4. **Ledger-pin advance** from the harvest's terminal ledger (records-only commit, §12 class (i)), then the
   **readiness and freeze refresh** of every pack still to run (§0.21). The plan tree is pinned by its semantic
   content (everything except the freeze-receipt pointer, as record 47 allows); each authorization names the
   refreshed pack digest. A started attempt that ends RECOVER also opened a bracket session, so its re-arm also
   follows a pin advance and refresh.
5. **Disk ledger** update and any registered offload (§4 item 8).
6. After `BETA` PASS and before `GAMMA-1` arms: the **L10-B rehearsal** extraction and mint on a scratch copy of the
   ALPHA and BETA bytes, serializing only structure (§9). An L10-B refusal routes to its owner row; GAMMA arms only
   when the lead has classified the refusal (a cure that touches no collection code lets GAMMA proceed; one that
   touches collection code follows §7.4). Blocking (§15 Q12).
7. Attempt plan, authorization, arm notice and T-0 for the next window, after the load-average quiescence check of
   §4 item 11.

### 3.4 Expected duration and attempt budget

Design estimate (scratch `sizing_v2.json`, SHA-256
`6a82745f47b40c8aa1ea6aefe2c45c2d4cce2b7a7e65d114165057e64fae00de`, at 55 s idle; formulas in §5.2): expected chain
time 29,556 s (8.2 h) for ALPHA, 30,605 s (8.5 h) for BETA and 26,182 s (7.3 h) for GAMMA, 86,343 s (24.0 h) in all.
Each window adds its clean dwell (600–2700 s), and each desk gap holds the steps of §3.3: binding, verdict and
backups; strict re-reduction of about 119 bundles (block 3: at most 23.9 s each, about 48 min); the archive copy;
G3; the pin advance with its refresh; the upload of about 20 GiB if a backup goes to iCloud (§4 item 8); and, once,
L10-B.

- If the harvest may open at chain exit: about 24.0 h of chains + 3 × (0.2–0.75 h) of dwell + desk gaps of about
  2–4 h each ≈ **31–38 h** for an all-PASS measurement block.
- If the harvest opens only at `t0 + WINDOW_MAX_S + 300` with the cap-sized `WINDOW_MAX_S` of §5.2: about 81,300 +
  82,320 + 70,560 s ≈ 65.0 h of occupied windows + desk gaps ≈ **70–75 h**. This is why §15 Q15 matters.

**Attempt budget** `FILL[B5-ATTEMPT-BUDGET]`. Blocks 2 and 3 armed four windows: `w1` RECOVER-T (controller
refusal C-2, a code defect), `w2` RECOVER-E (two idle-admission refusals in a row), the first `b3w1` NULL (clean
dwell timed out: the load average crossed 2.0) and the re-armed `b3w1` the one usable window, after its harvest was
REFUSED once and cured by R3 (RUN_STATE entries of 2026-10-03 and 2026-10-04). Claim windows are 2–3 times longer
with about 5 times the members. With code defects cured, a first-attempt PASS probability of one third to one half
per pack is a planning figure, so 2–3 attempts per pack, 6–9 windows for the measurement block, and a time and disk
budget sized for that. The budget plans; it never caps (D-186).

## 4. Operating conditions and fixed inputs (checked by code at arm or T-0 unless marked)

1. **Machine.** As §0.2; AC, battery float, power mode `ac_high_power`, sampler interval 100 ms; no agent or operator
   process from T-0 to the chain's exit. The driver's census runs first and repeats every 30 s: a `pgrep` whose
   exact argv, copied from the driver's census code at H_claim, is `FILL[CENSUS-ARGV]` must exit exactly 1 with
   empty standard output. Driver standard input is `/dev/null`.
2. **Acceptance.** As §0.11, ledger cutoff 376. One acceptance for all three windows. If a prospective-rederivation
   trigger of the acceptance fires during the measurement block, no further window arms; the question goes to a
   cold gate (§15 Q13).
3. **Models.** `mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit` at the revisions, tokenizer bytes
   and file hashes of `configs/model_panels/qwen3_4bit.json` at H_claim.
4. **Packs.** The regenerated packs at H_claim, identified by `FILL[ALPHA-PACK-DIGEST-AND-FREEZE]`,
   `FILL[BETA-PACK-DIGEST-AND-FREEZE]`, `FILL[GAMMA-PACK-DIGEST-AND-FREEZE]`. For reference, the merged (to be
   superseded) plan trees at `db41703c` are ALPHA `e30fdf675e8b18e76142723c4f12baaf9366c0a74f37a5070e3e87d32eb2aefa`,
   BETA `c2c483525cde4d36e46bbd8f9edcf29be9b24bda212ed06d9eba086f297d64a7`, GAMMA
   `995c7ca548c718c96ef2b44b7efa37d356ba82619f391ac6abe2ecb636d0c730`. The pin bundle is block 4 §3 item 4's: prompt
   pin `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`, selection
   `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`, ladder
   `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
5. **Policy.** As §0.13 (SHA-256 `b0d7b228…5efd` in full: `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`),
   or its successor under the Q1 ruling.
6. **Ledger.** The measurement clone (the dedicated checkout a window runs from) restores its ledger byte-exact from
   the source whose ledger tip equals the committed ledger pin at the arm commit. For `ALPHA-1` that source is block
   4's final harvest terminal ledger, `FILL[LEDGER-SEED-AFTER-B4]`; for each later attempt it is the previous
   attempt's harvest `derived/terminal-ledger.jsonl`, whose tip the merged pin advance names.
7. **Network time.** OFF throughout (§0.15). Each attempt has its own fresh OFF receipt, at least 600 s before the
   first capture on both clocks; no reused receipt; no ON at any point. (Revision 1's "on its own boot" is
   withdrawn: no step reboots the machine between windows, and nothing requires it.)
8. **Disk** (a cumulative ledger, `FILL[DISK-LEDGER]`, checked at every arm). Facts (scratch `disk_record.txt`,
   SHA-256 `4dad5aa2e1c4d51d26a825bef004c3442543480d364081c5754e4ec0847e7a1b`): block 3's 24 member bundles occupy
   4.26 GiB (about 182 MiB each, each embedding a ~79 MiB copy of the pre-calibration capture); each of its two
   harvest archives is 4.6 GiB; the data volume had 181.7 GiB free on 2026-10-05. A `_v5` window writes about 119 ×
   182 MiB ≈ 21 GiB (GAMMA 101 × 182 MiB ≈ 18 GiB). Per window the copies are: the collected roots (1×), one backup
   copy split across the two destinations (1×, on this volume only if a destination is local), the harvest archive
   (1×, 2× after a REFUSED re-harvest unless the second is an APFS clone, `cp -c`, which shares storage), plus once
   the L10-B scratch copy of ALPHA and BETA (about 42 GiB) and the L10-C scratch copy. Kept on this volume, three or
   four copies of ALPHA and BETA exhaust the free space at about L10-B, before GAMMA. Registered rules:
   - archives and scratch copies are APFS clones of the collected roots wherever the tool allows;
   - backup destinations `FILL[BACKUP-DESTINATIONS]` are off this volume (an external disk, or iCloud Drive with
     the local copy evicted after upload verification);
   - the ledger names which copies may be deleted after a verified backup and when (`FILL[DISK-OFFLOAD-STEPS]`);
   - the arm refuses unless free space ≥ (this window's estimate × its on-volume copy count) +
     `FILL[DISK-MARGIN-GB]`, read from the ledger, and, if a destination is iCloud, the account's free quota covers
     the window;
   - if a destination uploads off-machine, the next T-0 is authored only after that upload has finished
     (`FILL[UPLOAD-QUIESCENCE-CHECK]`): upload work during the next clean dwell would make that window NULL.
9. **Battery (#421).** §10.2.
10. **Not checked by code: background work during a member's measured request.** Idle admission screens the idle
    baseline before each request; work that starts during the request is not screened. §8 registers how this is
    diagnosed and disclosed.
11. **Quiescence before T-0 is authored, and Spotlight.** The desk runs `scripts/prewindow_check.sh` (without
    `--wait`) before authoring T-0 and does not author it on a BLOCK line. The evidence, archive and backup roots
    are excluded from Spotlight indexing by a mechanism verified effective on 25G83 (`FILL[SPOTLIGHT-EXCLUSION]`);
    block 3's NULL record named `mds_stores` and `backupd`.

A change to any item after the seal requires a prospective cold erratum before the next arm (§11).

## 5. Window shape and sizing

### 5.1 Shape

Each chain runs its pack's stage graph through the post calibration (§2.0 c): chain-owned settle, pre calibration
and its screen (a pre fiducial bound above 0.036462861644980 s stops the chain before any member), the NEG-8 bound
corpus and bound derivation, the start triplet, the science stages with the pack's interior references in their
registered places, the end triplet, the post calibration, the completion lifecycle event and terminal ledger
finalization. Then, at the desk and in this order: bracket binding, the whole-window verdict reading that binding,
and the two backups (§3.3 step 2). Nothing is shortened, skipped, reordered or repeated at arm or at run time.
There is no quad limit: claim chains run every quad of their pack.

### 5.2 Sizing method

**One method for blocks 4 and 5.** The binding numbers are produced at H_claim by block 4's committed sizing adapter
(`configs/campaigns/v5_qualification_25g83/sizing_allowances.json` on `feat/2026-10-05-v5-qualification-code`,
source `tests/fixtures/v5_qualification/sizing_allowance_source.json` SHA-256
`b02aed6a1580592db2a9e845d843f7f68c57ac54e6fbac6b830eee29b5b6d33a`), extended to the claim rosters by
`FILL[SIZING-ADAPTER-CLI]` from a source file committed at H_claim. Its conventions: per-member allowances include a
cooldown at the 300 s policy cap and an idle-admission allowance covering the retry; fixed allowances of 360 s for
the launch and pack T-0, 770 s for the calibration pair and 300 s for terminal shutdown; 180 s settle per stage.
Binding, verdict and backups are desk steps and are not in the span. `FILL[B5-SPAN-AND-WINDOW-MAX]` holds the
literals it emits.

**Design estimate (this draft).** Scratch `size_block5_v2.py` (SHA-256
`ccf7e2159aa66aed546c9dce5d2960a4391216843ad1d7fdeae16ade2bf3841c`), output `sizing_v2.json` (above), reading
block-3 timing only. With I the regenerated idle time (55 s here) and k = 1.288 wall seconds per nominal idle second
(128.8 ms records for 100 ms requested):

- expected small-model member cycle = block-3 median start-to-start cycle (236.5 s) − k × (75 − I) = 210.7 s;
  8B cycle = that + 10.5 s (the 8B-minus-1.7B run-wall difference at p2048; an extrapolation, because block 3 never
  ran two 8B members in a row);
- cap-sized cycle = block-3 maximum cycle (274.9 s) − k × (75 − I) + 300 s (cooldown at its cap) + k × I (one
  retry) = 620.0 s small, 630.5 s 8B;
- expected chain time = fixed (360 + 180 + 770 + 60 bound derivation + 300) + stages × (180 + 39 + 62) + Σ member
  cycles, where 39 s and 62 s are block-3's largest stage head (stage start to first member) and tail;
- `WINDOW_MAX_S` = 60 × ceil((cap-sized span + 2700) / 60), with 2700 s the clean-dwell cap added once.

| Window | Members (small-like / 8B) | Expected chain time | Cap-sized span | `WINDOW_MAX_S` (cap-sized) |
|---|---:|---:|---:|---:|
| ALPHA | 119 / 0 | 29,556 s (8.2 h) | 78,261 s | 81,000 s (22.5 h) |
| BETA | 19 / 100 | 30,605 s (8.5 h) | 79,310 s | 82,020 s (22.8 h) |
| GAMMA | 61 / 40 | 26,182 s (7.3 h) | 67,521 s | 70,260 s (19.5 h) |

The cap-sized figure is a ceiling, not a forecast: it is what the window would need if every member's cooldown ran
to its cap and every admission needed its retry. A large `WINDOW_MAX_S` costs nothing if the harvest may open at
chain exit, and up to 14 h per window if it may not (§3.4, §15 Q15). The packs' own `runtime_budget` (22,704 s and
22,897 s, marked `planning_only`; GAMMA's is empty) is below even the expected chain time and must not set
`WINDOW_MAX_S`.

**Deadline stop.** A chain still running at `t0 + WINDOW_MAX_S` is stopped by the driver; the attempt is RECOVER
class T (recipe), never a partial PASS. The registered resizing rule applies without an erratum: the next attempt's
per-member allowance becomes the larger of the adapter's and the stopped attempt's largest observed member cycle
plus the adapter's margin, and `WINDOW_MAX_S` is re-derived by the formula above (member cycles are structural
timing, releasable under §9).

**8B cooldowns.** If 8B members systematically need the full 300 s cooldown, BETA's expected time grows by about
100 × (300 − ~60) s ≈ 6.7 h. `s1` gives the first B1→B2 (8B after 8B) and B2→A2 (1.7B after 8B) cooldown waits;
those waits and their results are classified as releasable structural timing (§9, §15 Q7). A cooldown that hits
its cap on a science member fails window validity (§6).

### 5.3 Sampler-stream length against the clock limits

A member's stream must be long enough for the anchor (summed record time ≥ 60 s, §0.14) and short enough for the
effective bound (≤ 5 ms). **Registered convention, one for blocks 4 and 5:** ρ = 8 ppm (above the network-time-OFF
rates on record: 7.24 and 7.60 ppm, `uncertainty_evidence.py:57-60`, and 7.78 ppm in the block-4 sizing source);
h = 3.598 ms, block 3's largest member anchor half-width (`g2a-large-p4096-r01/metadata.json`, SHA-256
`63bd62a1ca1652a0b9194885f75a4d59a8afde1b06d274dbfee21b6352d66c80`); T = idle-admission attempts + warm-up +
measured request, excluding the cooldown; the worst case is enforced at plan time, not only the observed case.

Block-3 facts (scratch `b3_anchor.json`, SHA-256 `2f6c92012f0bb011fbeec4da55b8efd0dd0d268e34dd6a432ffd9273d669d7a2`,
from all 24 members at 75 s idle): T (`rate_fit_baseline_s`) 111.8–128.5 s; ρ, measured as the
wall-minus-monotonic change over the stream divided by T, 3.248–3.279 ppm; largest effective bound 4.02 ms; records
127.0–129.9 ms. The non-idle part of the stream (warm-up and measured request) was 15.0 s at least (small model) and
26.9 s at most (8B at p2048).

- **Shortest stream** (no retry, records at the 100 ms floor): T_min = I + 10 s (taking 10 s, below block 3's 15.0
  s, as the floor for the shorter reference workload, `FILL[REF-STREAM-FLOOR]`). At the merged packs' I = 30 s,
  T_min = 40 s, and even at block 3's observed cadence a small member gives about 30 × 1.288 + 15 ≈ 54 s: below 60 s,
  so every member would be refused. G2-a hit the same limit and moved to 75 s (`scripts/generate_g2a_probe_inputs.py`
  around line 498: bundle `mtnull-o0512-b02-b2` gave 48.16 s at 30 s idle).
- **Longest stream** (8B at p2048, one immediate retry, observed cadence): T_max = 2 × 1.288 × I + 26.9 s. The
  convention allows T ≤ (5 − 3.598) ms ÷ 8 ppm = 175.3 s.
- **Calibration streams:** 196.8 s with anchor-only bound 1.832 ms (block-4 sizing source): 1.832 + 8 ppm × 196.8 s
  = 3.41 ms ≤ 5 ms.

| I (s) | T_min (s) | ≥ 60 s? | T_max, one retry (s) | Bound at 8 ppm (ms) | ≤ 5 ms? |
|---:|---:|---|---:|---:|---|
| 30 | 40.0 | no | 104.2 | 4.43 | yes |
| 50 | 60.0 | yes (no margin) | 155.7 | 4.84 | yes |
| 55 | 65.0 | yes | 168.6 | 4.95 | yes |
| 56 | 66.0 | yes | 171.2 | 4.97 | yes |
| 60 | 70.0 | yes | 181.5 | 5.05 | no |
| 75 | 85.0 | yes | 220.1 | 5.36 | no |

The feasible band under the convention is about 50–56 s; 55 s is recommended (`FILL[V5-IDLE-SECONDS]`). It leaves
no room for a retry wait inside the stream (§15 Q1). At block 3's observed ρ (3.28 ppm) the longest stream allowed
would be about 427 s; the live anchor check, not this table, decides each member. `FILL[LONGEST-STREAM-SIZING]` and
`FILL[SHORTEST-STREAM-SIZING]` re-bind h, ρ, cadence and the non-idle times from the regenerated packs' `s1`
streams before seal.

## 6. Validity

Each predicate below is evaluated by code; none reads a science member's energy except where marked.

- **Member.** Valid when:
  - its summary status is `succeeded`;
  - its bundle passes strict validation (`python -m joulewise validate-bundle --strict`, which re-reduces the raw
    evidence);
  - its clock anchor is `bounded`;
  - its runtime-observed token counts are present (`token_count_source: runtime_observed`) and equal the registered
    counts (42 or 2048 prompt tokens, 512 output tokens);
  - its #421 capture pair passes (§10.2);
  - its registered target phase passes its precheck: `phase.decode` for decode members, `phase.prefill` for
    p2048 members (`target_precheck_path`). One precheck test, `anchor_energy_envelope_exceeds_quarter_metric`,
    compares the anchor-shift energy envelope with a quarter of the member's own phase energy; it is the one place
    validity reads a science energy, as a pass/fail ratio computed by code and never released;
  - `measurement_quality.idle_window_suspect` is `false` (the GPU was idle during the idle baseline; the claim gate
    otherwise returns `idle_window_suspect`, `analysis_engine/inputs.py:3558`);
  - its cooldown did not hit the cap (`cooldown_cap_hit` not true) and its campaign cooldown evidence verifies
    (`analysis_engine/inputs.py:3547-3556`).
  The p42 phase is not a target phase; its refusal is a registered outcome, not a validity failure.
- **Window.** Valid when every member of every stage (science, NEG-8, references) is valid; the number of distinct
  reference bundles equals the registered count (19 or 21); both calibrations pass the acceptance's bracketing
  decision (`joulewise/calibration_bracketing.py`: each slot authenticated and tied to the window's session, the pre
  slot within the pre screen, the drift allowance within its ceiling, acceptance fresh); the bracket binding is
  written before exactly one authoritative whole-window verdict row and that row is `passed`; the NEG-8 bound was
  derived inside the window; the OFF receipt is admitted; the window battery verdict is `pass`; both backups
  verify; the launch lifecycle (start, settle, completion) is complete; and G3 passes. The ledger's
  `physical_ahead` terminal state (the window's ledger is ahead of the committed pin until the harvest advances it)
  is the expected hand-back boundary, not bracket evidence.
- **G3 on claim windows** `FILL[G3-CLAIM-ARGS]`: `scripts/check_window_provenance.py` with, for each pack, its pack
  root, runs roots and an explicit `--null-bound-stage` list naming every `_v5` calibration, reference and science
  stage. The default S11-A4 roster names the Qwen2.5 `_v1`–`_v3` packs, and an absent stage is a non-failing SKIP
  (lines 778-784); on a claim window S11-A4 must run with no SKIP. S11-A2 and S11-A5 read a prospective analysis
  manifest, which floor packs do not have; their claim-window form for ALPHA and BETA is part of the FILL.

Because a PASS window has every science member valid in this sense, the floor extractor's same-slot exclusion of a
cooldown-cap member (`joulewise/floor_extraction.py` header) and the claim gate's member-level `not_resolvable`
codes cannot be reached on a PASS window. If either is reached, it is a defect: the analysis stops and the step goes
to R3 (analysis plan §2.2).

## 7. Verdicts, stop and recovery rules

### 7.1 Four mechanical verdicts per attempt

The harvest (`FILL[CLAIM-HARVEST-CLI]`, from authenticated immutable archives only) writes one:

- **PASS:** the chain exited with its registered success code `FILL[CLAIM-CHAIN-SUCCESS-RC]` and §6's window
  validity holds.
- **RECOVER:** `night/chain.started` exists and the attempt is not PASS. The harvest names the cause code(s) and one
  cause class from the table below.
- **NULL:** `night/chain.started` is absent.
- **REFUSED:** the harvest program itself failed on bytes that are present. Cured by R3 and re-harvested from
  identical bytes into a distinct derived archive; never a science outcome.

| Event | Verdict and class |
|---|---|
| Night-gate refusal, OFF receipt failure, clean-dwell timeout, start budget exceeded, census not clean at T-0 | NULL |
| Code or recipe defect during the chain; chain stopped at `t0 + WINDOW_MAX_S`; a launch or desk CLI refusing correct input | RECOVER-T |
| Idle admission refused twice for one member; environment guard; cooldown cap hit on a science member; `idle_window_suspect` true; upload or other machine-state work; the §8 window trigger, if adopted | RECOVER-E |
| Pre screen exceeded; bracket failed the acceptance; clock anchor not `bounded`; target-phase precheck failed; NEG-8 screen failed; authentic battery non-pass | RECOVER-I |
| A required file missing or failing authentication after a complete collection, including a missing raw battery observation | RECOVER-C |
| The harvest program fails on present, authentic bytes | REFUSED |

An ambiguous class is ruled by the lead before any further arm, with the evidence recorded.

### 7.2 What happens next

| Outcome | Next step | If the same class occurs twice in a row for the same pack |
|---|---|---|
| PASS | Desk steps of §3.3, then the next window | — |
| NULL | Re-arm the same pack with a new attempt ordinal, plan, authorization and T-0 after the named cause is gone (D-182: a refusal before any capture licenses a new-plan successor) | The next step goes to a **consult**, not a third arm |
| RECOVER-E | A fresh complete attempt of the same pack (new ordinal, roots, bracket session, authorization, T-0) after the cause is named and, where possible, removed | **Consult**; it may authorize another unchanged attempt, a prospective change (cold erratum, §11) or END STATE |
| RECOVER-I | A fresh complete attempt after a named, removable cause is removed; with no removable cause named, the question goes to a **cold gate** | **Cold gate** |
| RECOVER-T | R3 cure. A cure touching no collection code: re-harvest or re-run the desk step on identical bytes. A cure touching collection code: §7.4. A deadline stop: the resizing rule of §5.2 | **Consult** on the defect class before the next spend |
| RECOVER-C | Restore custody byte-exact from the archive and re-harvest; a collection whose evidence is lost is RECOVER-T for the custody code | **Cold gate** |

"Twice in a row" counts consecutive attempts of the same pack with the same class. These are anti-spiral triggers
that say where the question goes; none is a cap on attempts (D-186). If a consult cannot settle the question, it
goes to a cold gate; a cold-gate refusal goes to Ed. Ed's NO stops any arm. Every attempt's bytes, verdict and cause
stay in custody and are disclosed (analysis plan §8); no member, quad or cell is pooled, topped up or replaced
across attempts (D-078).

**What a fresh attempt can and cannot select on.** A fresh attempt is a new complete window. Its acceptance reads
no science member's energy except the single pass/fail ratio named in §6; it does read reference-workload energies
(NEG-8 screen), power (idle admission, bracket) and timing. So re-attempting cannot select on the science outcome,
but every reported number is **conditional on a window that passed these quiet, timing and drift predicates**. The
analysis plan prints, beside every reported cell and contrast, the number of attempts of its pack and their cause
classes (analysis plan §8).

### 7.3 Systematic instrument trigger and END STATE

Counting across every started attempt under this registration: if at least five members have a recorded
clock-anchor status (excluding `not recorded`) and more than half of them are not `bounded`, the clock instrument
is failing and re-arming cannot cure it: the measurement block goes to **END STATE** at once. (Counted across
attempts because an attempt that aborts at its first unbounded member records at most one.) END STATE also follows a
cold-gate ruling to stop. At END STATE: no further window arms under this registration; Ed is emailed; the next step
is a design record naming the cause, with a consult and a cold gate. Windows that already PASSED keep their bytes,
and their L1 analysis is fixed now: analysis plan §2.3.

### 7.4 A defect found in the middle of the measurement block

**Collection code** is any file in the sealed inventory (§13) that executes during a window or changes how a
window's bytes are produced. GAMMA's contrasts are judged against floors minted from ALPHA and BETA, so all three
windows must share one acceptance, one macOS build and one collection head for the code they executed.

- A cure confined to collection code that no completed window executed (for example, GAMMA-only interior-reference
  stages that ALPHA and BETA never ran) does not supersede completed windows: §12 class (iv) records the changed
  paths, the diff-scoped #416 re-audit covers it, and the measurement block continues. The changed-path proof must
  show that no file executed by a completed window changed.
- A cure touching collection code that a completed window executed **supersedes the whole measurement block**: all
  completed windows are retained and disclosed structurally, their energies are never analysed (analysis plan
  §2.1), a new registration or a cold erratum to this one is written, block 4's coverage rule decides whether the
  new head needs a new qualification occurrence, and the block restarts at ALPHA.
- A defect in code that does not run during collection (harvest, extraction, mint, analysis) is cured by R3 and
  re-run on identical bytes; the block continues.

The full-chain dry render of §12.3 exists to find GAMMA-only defects before any claim window runs. §15 Q9.

## 8. Environmental diagnostic (Sol consult record 31 §5)

**The forcing problem.** Idle admission proves the machine was quiet in the idle baseline before each request. It
proves nothing about the request itself (§4 item 10). Block 3 could leave that unchecked because its output was a
record count; block 5 prints energies, and background work during a request adds energy that would be attributed to
the model. A macOS maintenance burst (Spotlight, media analysis) lasts minutes; block 2's `w2` lost a member to one
of about six minutes (archive `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2`,
`harvest.json` SHA-256 `e40583983c95ea2df0edff0854177a273cfac0c1fd3fbbe0a0fea10133fe756b`). A measured request
lasts 11.1–23.6 s (§0.3).

**What is registered now.**

1. The diagnostic is outcome-independent: it reads no science phase energy and is computed by code before any
   energy is released (§9).
2. Its result never removes a member from a reported cell or a contrast and never produces a reduced mean: D-179
   forbids any post-collection admission filter and any 49-member mean (`docs/contracts/paper_reported_energy.md`,
   "Membership, energy and uncertainty").
3. Existing per-member evidence is recorded and disclosed for every science member:
   `uncertainty_evidence.idle_drift.status`, `pre_idle_window_suspect` and `post_idle_window_suspect`. The last two
   describe the GPU state in the idle slices before and after the request, not the measured phase; they are
   registered as diagnostics, not as claims-ladder "suspect quality flags", with the waiver wording of analysis
   plan §8. `measurement_quality.idle_window_suspect`, which is a quality flag, is a validity predicate (§6).
4. A rejected design is on record: applying the production CPU criteria to each member's post-run idle sentinel
   flagged all 24 quiet block-3 members (`cpu_busy_ratio_p95_exceeded`; probe
   `/Users/edr/night-archive/ia-0a40/claim/scratch-block5-sizing/ed2_probe.py`, SHA-256
   `1e48e0677babd7fcb2926b747234a883ad377202d33ce020f39112ca0ba22b28`), because the member's own process is still
   tearing down. It cannot be the diagnostic.

**What must be fixed before seal (§15 Q2).** The member-level predicate `FILL[ED-PREDICATE]` and its disposition
`FILL[ED-DISPOSITION]`. The candidate with a physical basis is the QPE01 busy-core journal
(`docs/contracts/night_quiet_admission.md`; `joulewise/quiet_predicate_campaign.py`), which attributes CPU work to
each non-measurement process; it would have to run in the claim chain and therefore be at H and exercised on `s1`.
**Recommended disposition: a window-level trigger.** Its threshold is set from the predicate's false-flag rate p,
measured on clean block-3 members (diagnostic archive): the window is RECOVER-E when the number of flagged science
members exceeds the smallest k with P(Binomial(n, p) > k) < 0.05, n being the window's science members (100; 80
for GAMMA). The alternative,
report-only, cannot be given a magnitude assessment, because the only direct one (the mean without flagged members)
is the reduced mean D-179 forbids; report-only would disclose counts and positions only.

## 9. Blinding

1. **Before seal.** No claim-eligible `_v5` byte exists. Block 4 §10 already withholds `s1`'s energies, powers and
   per-member phase durations from everyone who designs or seals this plan. This draft's author read none of them
   (§16).
2. **During the measurement block.** From `ALPHA-1`'s launch until the block closes (GAMMA PASS, or END STATE),
   every harvest, G3 run, L10-B rehearsal, blind dry run (analysis plan §3), courier record, email and public
   summary releases **structure** only: verdicts, cause classes, counts of members and stages, paths, hashes,
   readiness facts, and timing facts that are not phase durations (member cycle and cooldown waits are
   releasable). **Restricted** (`FILL[B5-BLIND-CUSTODY-MAP]`), in addition to energies, powers, phase durations,
   floor values, reported means, dominance ratios and calibration numeric diagnostics:
   - any pass/fail or category derived from a science energy: floor-gate status, the dominance branch and each
     ratio's pass/fail, claim outcomes and ceilings, the `anchor_energy_envelope_exceeds_quarter_metric` result
     beyond the window's verdict;
   - any refusal or reason code that encodes a numeric comparison of a science quantity (for example
     `effect_not_above_floor`, `dominance_ratio_zero_denominator`, `deterministic_bound_obscures_direction`); such a
     refusal is released only as "an outcome-class refusal at step N".
   Automation may validate, reduce and evaluate predicates, but serializes only structure. Every recovery decision
   in §7 is therefore made without seeing a science outcome. The current driver excludes raw chain logs from durable
   courier records only for non-`CAMPAIGN_TRANSACTION` purposes (ruling 76 decision 9);
   `FILL[COURIER-BLINDNESS-CAMPAIGN]` extends that exclusion to claim windows (§12.2).
3. **Block 4's `s1` metrics** stay withheld until this measurement block closes, so that any erratum written during
   the block is written blind (§15 Q11). The `s1` timing facts named releasable in §5.2 are the exception.
4. **Unblinding.** After the block closes and after the blind dry run of analysis plan §3 has passed, the lead
   records a release event tying this file's and the analysis plan's sealed SHA-256s and the final harvest records
   (`FILL[B5-RELEASE-EVENT]`); the analysis then runs exactly as registered. Analyses not registered are labelled
   exploratory.

## 10. Directive gates

### 10.1 #416: pre-arm triple audit

Once, at H_claim, after this registration is sealed and before `ALPHA-1` arms: a fresh blind full-system audit
(adapters, calibration and issuance, night machinery, reduction, analysis and claims) by three independent model
families, findings cross-verified, BLOCKERs challenged by a refuter seat from a different family and cleared before
arm. Ed's directive names Astra 6 xhigh, Fable 5.1 and Opus 5.5 xhigh; the seat assignment under D-186 and Ed's
2026-10-05 wish to use Fable less is `FILL[416-SEATS]` (§15 Q6). It runs once per frozen code or protocol change,
never per window: a later change to collection code (§7.4) triggers a diff-scoped re-audit of that change, not a
full one. No audit work runs during a window.

### 10.2 #421: battery float, every window

At arm, immediately before the attempt plan is published to the measurement clone and installed with the driver,
and at T-0, a fresh authenticated raw `ioreg` observation read by `joulewise/battery_float.py` must pass §0.16's
predicate. Every capture (both calibrations and every member) has a raw pre/post `ioreg` pair outside its
clock-anchor stamps and sampler lifetime. The harvest computes the window battery verdict from raw bytes before any
energy is read; under block 4's A-R5b-1 reading that harvest verdict is final for the window. A missing or
unauthenticated observation is RECOVER-C; an authentic non-pass is RECOVER-I (§7.1). Paths:
`FILL[B5-BATTERY-EVIDENCE-MAP]`; block 4's disposition of its S3/S4 battery findings
`FILL[BATTERY-S3-S4-DISPOSITION]` carries over. Endpoint pairs cannot see an excursion wholly between two
observations; this limitation is disclosed.

### 10.3 Results and publication

Claim-bearing results are a cold-gate object (orchestration doctrine, gate 2): after the analysis runs, one judge
and one refuter re-derive every printed number from the preserved artifacts before any paper sentence is filled.

## 11. Changes after the seal

None to §§3–10 for an armed or completed attempt. A rule, threshold, roster, purpose, recovery or blinding change is
a prospective cold erratum (one judge, one refuter), settled in one erratum rather than a chain. The §5.2 resizing
rule is registered and needs no erratum. A fix that only makes code agree with this text goes through a gated R3
pull request whose final pass is the lead's measurement-code reviewer (`FILL[FINAL-PASS-SEAT]`); it never changes
collected bytes, and it follows §7.4 if it touches collection code.

## 12. Commit rule

1. **H_claim** is block 4's qualified commit H′ (H plus its record-47 terminal refresh), extended only by (i) merged
   ledger-pin advances from this block's harvests with their readiness and freeze refreshes, under block-4 record
   47's changed-path proof (the list of files a pin advance may change, checked against `git diff --name-only`);
   (ii) gated R3 fixes to code that does not run during collection; (iii) commits touching only `docs/`, `tests/`,
   `RUN_STATE.md` or `TASK_QUEUE.md` that leave every pinned executable, generated config and chain source
   unchanged; (iv) a §7.4 cure confined to collection code no completed window executed. Each extension carries a
   `git diff --name-only` map checked before the next arm.
2. **Claim launch code.** Claim windows execute code that `s1` did not. All of it must be at H before block 4's `s1`
   arms, so that `s1` qualifies it, or a cold gate must rule prospectively that `s1`'s coverage extends to it
   (`FILL[CLAIM-LAUNCH-CODE-AT-H]`, §15 Q3):
   - the `CAMPAIGN_TRANSACTION` attempt-plan writer;
   - a chain renderer that runs every stage of a full pack through the post calibration, including GAMMA's three
     interior references, and reads both plan-tree schemas if §2.0 d keeps two;
   - **a purpose-independent OFF-receipt admission, clean dwell and start-budget check for every `TRANSACTION_PACK`
     launch.** On main these run only for `DIAGNOSTIC_NO_PACK` (`run_night.py` around lines 3620-3634); the
     qualification branch adds them for `G2B_SHAKEDOWN` (around lines 3786-3793); the `CAMPAIGN_TRANSACTION` branch
     has only the OFF receipt at T-0. `s1` must run the same function the claim windows will run;
   - the desk binding, verdict and backup CLIs of §3.3;
   - the claim harvest, including the distinct-reference-bundle assertion of §6;
   - the claim-window courier exclusion (§9.2);
   - any §8 recorder.
3. **Full-chain dry render.** At H_claim, before `ALPHA-1` arms, all three chains are rendered and every stage is
   dry-run against its intended roots with no capture, as the runbook checklist requires
   (`FILL[CLAIM-DRY-RENDER-RECORD]`). This is the only exercise before GAMMA-1 of GAMMA stages 8–12 (`s1` runs only
   GAMMA's first science stage with `--max-blocks 1`).

## 13. Seal

A cold gate seals this file and the analysis plan together (`FILL[B5-SEAL-SEATS]`). The seal record
`FILL[B5-SEAL-RECORD]` pins, with SHA-256s at H_claim: both documents; H_claim; the three regenerated packs and
their freeze receipts; the pack regeneration record; the panel, policy, acceptance and pin bundle; the sizing
adapter source; the claim plan writer, chain renderer, `scripts/run_night.py`, `scripts/launch_window.py`,
`scripts/run_campaign.py`, `scripts/prewindow_check.sh`, `joulewise/controller.py`, `joulewise/night_gate.py`,
`joulewise/night_plan_writer.py`, `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence_t0.py`, the
calibration capture, ledger, bracketing, binding and battery readers, `joulewise/whole_window.py`,
`joulewise/uncertainty_evidence.py`, the strict validator and reducer, the desk binding, verdict and backup CLIs,
the claim harvest, `scripts/check_window_provenance.py` with its claim arguments, and the §8 producer; the analysis
programs named in analysis plan §11; and the two chain-source documents `docs/phase_2/window_runbook.md` and
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. Grouped entries are expanded file by file in
`FILL[B5-SEALED-FILE-INVENTORY]`.

## 14. Binding register

| Binding | FILL | Due |
|---|---|---|
| Pack regeneration | `V5-PACK-REGEN-RECORD`, `V5-IDLE-SECONDS` | Before block 4 seals |
| Block-4 verdicts | `B4-STRUCTURAL-VERDICT`, `B4-QUALIFICATION-VERDICT` | Seal |
| L10-A, Q110, A6 | `L10-A-RATIFICATION-RECORD`, `Q110-CLOSURE`, `A6-AT-H-CLAIM` | Before `ALPHA-1` arm |
| Commit and launch code | `H-CLAIM`, `CLAIM-LAUNCH-CODE-AT-H`, `CLAIM-DRY-RENDER-RECORD` | Code at H before block 4's `s1` arm; dry render before `ALPHA-1` |
| Packs | `ALPHA-PACK-DIGEST-AND-FREEZE`, `BETA-PACK-DIGEST-AND-FREEZE`, `GAMMA-PACK-DIGEST-AND-FREEZE` | Seal; refreshed after every pin advance |
| Ledger | `LEDGER-SEED-AFTER-B4`; per-attempt pin advance | `ALPHA-1` arm; each later arm |
| Authorization | `V5-TRANSACTION-GO-01-DISCHARGE`, `AUTH-<label>`, `CAMPAIGN-PERMITTED-BLOCKS`, `STEP6-RECORD` | Semantics at seal; record each arm |
| Sizing and clock | `SIZING-ADAPTER-CLI`, `B5-SPAN-AND-WINDOW-MAX`, `LONGEST-STREAM-SIZING`, `SHORTEST-STREAM-SIZING`, `REF-STREAM-FLOOR`, `ANCHOR-RUNTIME-EFFECT` | Seal |
| Harvest and desk | `HARVEST-OPEN-RULE`, `B5-DESK-BINDING-VERDICT-BACKUP-CLI`, `CLAIM-CHAIN-SUCCESS-RC`, `CLAIM-HARVEST-CLI`, `G3-CLAIM-ARGS` | Seal |
| Attempts | `B5-ATTEMPT-BUDGET` | Seal |
| Machine | `CENSUS-ARGV`, `SPOTLIGHT-EXCLUSION` | Seal |
| Disk | `DISK-LEDGER`, `DISK-MARGIN-GB`, `BACKUP-DESTINATIONS`, `DISK-OFFLOAD-STEPS`, `UPLOAD-QUIESCENCE-CHECK` | Seal; checked each arm |
| Environmental diagnostic | `ED-PREDICATE`, `ED-DISPOSITION` | Seal (exercised on block 4's `s1`) |
| Blinding | `B5-BLIND-CUSTODY-MAP`, `COURIER-BLINDNESS-CAMPAIGN`, `B5-RELEASE-EVENT` | Seal; release after the block closes and the blind dry run passes |
| Battery | `B5-BATTERY-EVIDENCE-MAP`, `BATTERY-S3-S4-DISPOSITION` | Seal; evidence each window |
| Audit, seats | `416-AUDIT-RECORD`, `416-SEATS`, `B5-SEAL-SEATS`, `FINAL-PASS-SEAT` | Seats at seal; audit before `ALPHA-1` |
| Boundary, attribution floor | `BOUNDARY-LABEL`, `ATTRIBUTION-FLOOR-BINDING` | Seal |
| Seal | `B5-SEAL-RECORD`, `B5-SEALED-FILE-INVENTORY` | Seal |

## 15. Open questions for the lead (each names where it goes)

- **Q14. Idle time and pack regeneration (decide before block 4 seals; lead, with a Sol 6.1 implementation seat).**
  The merged packs' 30 s idle voids every member (§5.3). Choose `V5-IDLE-SECONDS` in the 50–56 s band (55 s
  recommended) and commission the regeneration of §2.0 (idle time, GAMMA's distinct interior references, chains
  ending at the post calibration, one plan-tree schema, the Q1 retry). Changing the reference configurations may
  require re-deriving the settled NEG-8 corpus artifact if it pins their hashes; the regeneration record must say.
- **Q1. Admission bursts can end long windows (decide before block 4 seals; consult).** Block 2's `w2` (18:12–19:59
  UTC on 2026-10-03) and block 3's SELECT window (13:26–16:43 UTC on 2026-10-04) together ran 37 members' idle
  admissions over about 5.0 chain-hours: one member was lost to two refusals inside one burst of about six minutes,
  and one other admission needed its retry. A burst of about 360 s is longer than an admission and its immediate
  retry (2 × 1.288 × 55 ≈ 142 s at 55 s idle) and longer than a whole member cycle (about 211 s), so any burst during
  collection overlaps some admission completely and aborts the window. If bursts arrive at rate λ, a window of chain
  time t survives with probability e^(−λt). Counting one burst in 5.0 h: about 0.19 for an 8.2 h window. Counting
  the retried refusal as a second burst: about 0.04. At one burst per 24 h: about 0.71 per window and e^(−24.0/24) ≈
  0.37 for all three. The rate is poorly known. Options:
  (a) keep the policy and rely on §7.2's fresh attempts (plan for the §3.4 budget);
  (b) add a retry wait. Under the registered clock convention there is no room for a wait inside the stream at 55 s
      idle (§5.3); a wait is feasible only if the retry restarts the sampler stream (a code change), or if the lead
      rules that the observed ρ (3.28 ppm, longest stream about 427 s) replaces the 8 ppm convention for retried
      members, which would allow a wait of up to about 250 s;
  (c) re-cut each floor pack into two shorter windows (new packs, new freeze; the 20 units of a cell would then span
      two windows, which §3.1's one-window rule and D-078's no-pooling rule forbid without an erratum).
  First step: estimate the burst rate from every retained 25G83 record (block 2/3 members, QPE01 envelopes, D-079
  derivation windows). Any change to pack bytes rides the §2.0 regeneration.
- **Q15. When may the harvest open, and how is `WINDOW_MAX_S` sized? (lead, before seal).** If a cited code fact
  shows the driver holds nothing after chain exit and its terminal courier record, open the harvest then and size
  `WINDOW_MAX_S` at the cap (about 22.5 h; costs nothing). Otherwise either accept about 65 h of occupied windows or
  size from observed cycles (about 11–12 h, revision 1's figures) and rely on the §5.2 resizing rule if 8B cooldowns
  run long. Recommended: establish the early-open code fact.
- **Q2. Environmental diagnostic (§8; consult, before block 4 seals if a recorder is added).** Choose the predicate;
  the recommended disposition is the binomial window trigger; decide whether the QPE01 busy-core journal joins the
  claim chain and `s1`.
- **Q3. Claim launch code at H (before block 4's `s1` arms).** The items of §12.2, including the
  purpose-independent OFF, dwell and start-budget admission, do not exist yet for claim windows; without them at H,
  `s1` does not qualify the claim launch path.
- **Q4. Disk (lead).** Name off-volume backup destinations, the offload steps and the upload-quiescence check;
  confirm APFS clones for archives and scratch copies (§4 item 8).
- **Q5. Paper placement (cold gate, ideally before seal).** D-174's methods/diagnostic fallback places no `_v5`
  result, and D-179 ruling 7 keeps the reported-energy placement X5 `RETIRED_FALLBACK`. The comparison-placement
  proposal (X1–X22) is `PROPOSED_STOP_FILL`. Pre-registering what is printed needs an adoption ruling.
- **Q6. Seats (lead; Ed may veto).** Seal gate, #416 composition and the measurement-code final pass, given #416's
  named seats (Astra 6, Fable 5.1, Opus 5.5), D-186's Sol 6.1 default and Ed's 2026-10-05 "try using fable less for
  a bit". A proposal that honours both: #416 by Sol 6.1 xhigh, Astra 6 xhigh and Opus 5.5 xhigh (three model
  lines, no Fable); the seal gate judged by Opus 5.5 with a Sol 6.1 refuter; Fable kept for the results cold gate
  only.
- **Q7. Non-member stage timing (lead).** Confirm that `s1`'s non-member stage timestamps and its B1→B2 and B2→A2
  cooldown waits and results are structural (releasable) for sizing.
- **Q8. `permitted_blocks` for claim authorizations (lead).** The contract defines it only for G2-b (exactly 1).
  Proposed: the pack's full quad count (ALPHA and BETA 20 null quads, GAMMA 20 contrast quads), recorded but not
  enforced at run time, since claim chains run the whole pack.
- **Q9. §7.4 supersession (cold gate).** Confirm the narrowed rule: a cure confined to code no completed window
  executed keeps the completed windows; any other collection-code cure supersedes the block.
- **Q10. Analysis code timing (lead).** Production reported-energy issuance does not exist
  (`joulewise/paper_reported_energy.py:457`, "No production dispatch exists"), nor do the `_v5` pinset and input
  manifest, the mint-to-close-out adapter, the claim-verdict-to-results-fill adapter or the disclosure producer
  (`docs/process/v5-artifact-flow.md`). Preferred: merged and pinned before `ALPHA-1`; otherwise written blind
  before the release event, with the blind dry run of analysis plan §3 run before release either way.
- **Q11. Keep block 4's `s1` metrics withheld until block 5 closes (lead).** Recommended (§9.3).
- **Q12. L10-B between BETA and GAMMA (lead).** Proposed as blocking for `GAMMA-1` (§3.3 step 6).
- **Q13. Acceptance rederivation trigger mid-block (cold gate if it fires).** §4 item 2.
- **Q16. Attribution floor (lead, before seal).** D-078 derived the ~1 J attribution floor from corpora recorded
  before 25G83 and these packs. Bind the value and artifact, and rule whether it applies to 25G83 `_v5` or must be
  re-derived (`FILL[ATTRIBUTION-FLOOR-BINDING]`).

## 16. What the author read

Revision 1: from the block-3 SELECT archive (diagnostic, readable after block 3 by its §10): event timestamps and the
per-member and per-phase durations derived from them (for sizing), clock-anchor records, idle-admission attempt
counts and decisions, the CPU criteria's decisions on post-run idle sentinels (decisions only), the cluster-level
CPU idle-ratio field (reads 0 throughout, so it cannot serve as a diagnostic), bundle byte sizes, the selected
length, and the window chain log, which also prints the block-3 pre-calibration fiducial bound (seen; not used).
From block 2's `w2` archive: admission attempt counts and decisions and the chain log's stage times. The packs'
committed plan trees, including their `runtime_budget` planning figures.

Revision 2 (scratch `/Users/edr/night-archive/ia-0a40/claim/scratch-block5-rev/`): from the block-3 SELECT archive,
the clock-anchor fields of all 24 members (`b3_anchor.py` SHA-256
`5453c20456f6b18a0d78c341504466a9e345c8ec7aee460bc22bcb02015887a6`); structural quality flags, per-phase precheck
eligibility and reason codes, in-window record counts, and a zero-check of `interpolation_joint_edge_bound_j`
(`b3_flags.py` `4307b1826ab1cc744c8acead067a02a176fd619cbe1445561a10dad58d50079e`, output `b3_flags.out.txt`
`a0c2ad2733e388e357fb51248c8a6001e882f2d4dbab590c23d5c85363becd01`); `measured_run` stage durations
(`measured_run.txt` `c430142b8e524d21e984c1a7be334e0fefc2034109732b1248d57258fc56fcc2`); member event timelines
with energy fields filtered out; `du` and `df` (`disk_record.txt`). While locating the precheck structure the author
saw one block-3 member's decode precheck record (record count, cadence ratio, clock bound, a zero interpolation
bound and the phase duration); none of it is used. The issued acceptance file's derivation fields. Code and
contracts on `origin/main` at `c88565c4` and the block-4 branches. No energy or power value of any block was read,
nothing of block 4 exists yet, and no `_v5` claim byte exists.
