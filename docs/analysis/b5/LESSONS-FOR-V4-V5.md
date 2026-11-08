# Block 5 lessons for ALIGN v4, v5 and BYTES: use, reform, learn from

Written 2026-11-08 by an Opus 5.5 seat for the Block-5 lead (interactive session 1544c617). It answers Ed's question
of what Block 5 teaches the measurements not yet taken: ALIGN v4 (R1 is measuring, W1 is next), v5 and BYTES. The
companion results file is `docs/analysis/b5/RESULTS.md` (branch `analysis/2026-11-08-b5-results`).

## What this seat read, and what it could not read

**Read, Block 5 only, read-only.** Two directories:

- `/Users/edr/jw-b5-custody/dry-m/dry-run/`, giving these sources:
  - **DISC**: disclosures `77be1a3e…` and released text `1945410f…`;
  - **EXC**: exclusions `a9954365…`;
  - **gamma-verdict**: `finalized/inputs/3e0d1fcb…`;
  - the GAMMA ledger `49b2236d…`;
  - the supply census (file **names** only);
  - the per-member `rereduced/` window durations;
  - the gamma pack's order manifest.
- `/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z/`, giving **RC** (`recompute.json`) and **CMP**
  (`comparison.json`).

Repository sources were read as committed blobs. They are listed at the point of use.

**Not read.** The process names behind each contention flag live only in the Block 5 harvest archives, under
`~/night-archive/harvest-v5-b5-*` (`derived/flags.jsonl` and the monitor's `contention.jsonl`). This seat's brief
and `RUN_STATE.md` item 231 keep every `night-*` path sealed, so they were not opened. §1 therefore names culprits by
time, rate and schedule, not by process. It ships a tested extractor that fills in the names in one authorized run
(§1.4).

**Arithmetic.** Numbers marked **(derived)** are this seat's own computations from the sources named. Everything else
is copied from a registered or recompute output. No energy value enters §1 or the corpus.

---

## 0. The answer in one page

1. **Contention is a steady background hazard, not one culprit.** Fitted per second of request:
   - **λ = 0.0121 per s** (95% profile CI 0.0072-0.0187), about one qualifying burst per 83 s of request time, judged
     at the B5 bar (an outside process above 0.05 CPU-s/s in a 10 s interval);
   - the rate is the same for 1.7B (0.0119) and 8B (0.0121);
   - the count is steady across all 9 collected B5 attempts, at every time of day.

   Two loss units line up with the known launchd schedule: trustkit at about 17:31 and the softwareupdated scan at
   about 23:09. The rest do not. Scheduling arms around the schedule removes at most about 2 of 17 science flags.
2. **Exposure fully explains the 8B skew.**
   - The fitted hazard predicts **76.7%** of contention flags on the 8B arm (derived: (6.77+9.82)/21.63 s). Observed:
     **76.5%** (13/17) pooled and 5/6 in GAMMA.
   - Quad loss predicted from member hazards: 0.37 (decode) and 0.43 (prefill). Observed: 0.40 and 0.50.
   - The registration planned on 1 member in 37 (2.7%), which implies about 10% quad loss.
3. **Under B5's bar, every v4 member would be lost.**
   - A v4 D member's active span is about 830 s. Under the same rule, P(flagged) is **> 0.997**.
   - v4's kit has **no** member-level host-contention exclusion. It flags only (§2.3), so the projected loss from
     this hazard is about **0** and the fixed-8 calibration is safe from it: P(≥ 39 eligible per pair, both pairs)
     ≥ 0.998 for any iid member loss up to 15%.
   - The real calibration risk is **whole-window loss**. P(success) is **0.87** if each C window has a 1-in-8 chance
     of being barred, and **0.59** at 1 in 4 (with 5% iid member loss).
   - BETA needed 6 attempts, 5 of which were unusable.
4. **τ (between-window shock).** Read from the registered cross-window check:
   - **τ ≈ 0.24 J pooled**, which is **0.13% of the cell** (relative);
   - the upper cell is 8B decode at **0.41 J (0.21%), equal to 1.30 s_r**;
   - χ²(4) = 30 under τ = 0, so the within-window intervals do understate between-window variation.

   In B3's units, τ/s_r depends on v4's own benign residual SD (§3.3). In v5, ρ is a rescue-probability ICC, not an
   energy ICC, so B5 cannot set ρ̂. v5 lands at **baseline (28 windows)** whenever r̂ and m̂ are both ≤ 0.02 (§3.4).
5. **D is 81% clock anchor, and the anchor is not the member's ≤ 5 ms bound.**
   - The anchor term is the window's operative fiducial bound **b_op = 47.97 ms**, which is the larger bracket end
     (33.44 ms) plus a 14.53 ms screen allowance, summed linearly over both arms.
   - Timing receipts would shrink D by **0**: they stamp session boundaries, not powermetrics samples.
   - Better fiducial anchoring would shrink D by **24-72%**. A governed common-mode contrast bound would shrink it by
     **73-81%** (§4).
6. **Comparator.** Six concrete rules for v4's comparator and `release_v4` (§5). The main ones: an empty family is
   a HOLD unless it was declared expected-empty, and every registered sensitivity line must compute on a fixture
   before data.

**Must land before W1 registration** (ranked list in §6):

- (a) state in the v4 registration that in-window contention is DISCLOSE-only, with an energy-scaled exclusion if
  any, and bound `contention.unmeasured`;
- (b) the lead rules on whole-window-loss risk for the fixed-8 calibration;
- (c) a balance check by condition with an exposure-adjusted expectation;
- (d) the comparator and release rules of §5.

---

## 1. Contention forensics (45% of quads lost against about 2.7% planned)

### 1.1 What was lost, and when

**Sources.** Every lost unit, with codes, stage, within-stage index, request duration and an estimated local time
window, is in `docs/ops/guard-replay-corpus/b5/b5-loss-timeline.json`.

**How times were estimated.**

- Stage start comes from the campaign-manifest timestamp in the supply census. Stage end is the next campaign's start.
- Members are spaced uniformly within a stage, 144-179 s apart.
- Error is about ±2.5 min for a named member. ALPHA and BETA quad lines do not name the triggering member, so for
  them the error is the quad's span of about 10 min.
- Times are PDT, since Block 5 ran before the DST change.

**Request spans** (rereduced `window_evidence_precheck.gross_request.window_duration_s`, means):

| Arm and workload | Request span |
|---|---|
| 1.7B decode | 2.08 s |
| 1.7B prefill p2048 | 2.96 s |
| 8B decode | 6.77 s |
| 8B prefill p2048 | 9.82 s |
| Qwen2.5-1.5B NEG-8 reference | about 1.6 s (12-13 power records at about 7.6 Hz; RC `members.*.n_overlap.request`) |

**`contention.request_overlap` science units** (one contended member per unit; DISC flag counts match unit counts,
except BETA, which has 14 flags on 13 units):

| Window (local day) | Unit and trigger | Arm | Estimated time (PDT) |
|---|---|---|---|
| ALPHA (Fri 10-09) | prefill abs r08 | 1.7B prefill | 20:06-20:08 |
| ALPHA | prefill abba b07 | 1.7B prefill | 21:11-21:21 |
| ALPHA | prefill abba b10 | 1.7B prefill | 21:40-21:50 |
| BETA (Sun 10-11) | decode abs r03, r06, r10 | 8B decode | 14:33-14:35, 14:40-14:43, 14:50-14:53 |
| BETA | decode abba b10 | 8B decode | 16:25-16:35 |
| BETA | prefill abba b03 | 8B prefill | **17:31-17:41** |
| BETA | prefill abba b07, b08, b09 | 8B prefill | 18:14-18:49 (three consecutive quads) |
| GAMMA (Sun-Mon 10-11/12) | decode b01-b1 | 8B decode | 22:34-22:36 |
| GAMMA | decode b05-b1 | 8B decode | **23:15-23:17** |
| GAMMA | prefill b04-a1 | 1.7B prefill | 00:49-00:52 |
| GAMMA | prefill b06-b2, b09-b1, b10-b1 | 8B prefill | 01:18-01:21, 01:46-01:48, 01:56-01:58 |

**Reference and corpus contention losses** (DISC `reference_lost`, `corpus_physics_drop`):

- ALPHA: end r2, about 21:52.
- BETA: 5 of 18 corpus members.
- GAMMA: corpus r05 (about 21:41) and r16 (about 22:16), start r2 (about 22:25) and end r1 (about 02:04).

**The CPU-s/s, start and duration of each overlap are not in the permitted read.** They come from the extractor's
`culprits-b5.md` (§1.4).

**Arm dwell context** (DISC `arm_hazards`): the largest outside process at arm was 0.0063-0.0100 CPU-s/s, and host
busy time was 0.046-0.054 CPU-s/s. Every window armed clean, and contention started after arm.

### 1.2 Patterns

**(a) A constant per-second hazard explains the science losses** (derived; `docs/analysis/b5/lessons-derivations/hazard.py`, binomial MLE on
280 exposed science members with a 1 − exp(−λ(T + c)) law):

- **Fit.** The best offset is **c = 0 s**, giving **λ = 0.01206 per s (95% CI 0.0072-0.0187)**, log L −60.30. A
  10 s interval-alignment offset fits worse (log L −61.95).
- **By model.** 1.7B 0.0119 per s (4 flags in 343 member-s) and 8B 0.0121 per s (13 in 1,128). The hazard is the
  same, so the skew is exposure.
- **By window.** ALPHA 0.0123, BETA 0.0103, GAMMA 0.0155 per s. The confidence intervals overlap.
- **Predicted against observed:**

  | Arm | Predicted | Observed |
  |---|---|---|
  | 1.7B decode | 2.5% | 0/68 |
  | 1.7B prefill | 3.5% | 4/68 |
  | 8B decode | 7.8% | 6/68 |
  | 8B prefill | 11.2% | 7/68 |

**(b) It is not a time-of-day schedule.** The family count `PHYSICS_IN_SPAN` (contention plus span-unknown) is
steady across all collected attempts (DISC `attempt_history`):

- ALPHA attempts: 18, 8 and 6.
- BETA attempts: 13, 12, 12, 14 and 17.
- GAMMA: 14.

These attempts started between 00:39 and 22:15 local, on five days. Only two units line up with the known launchd
schedule (`RUN_STATE.md` item 205, observed in November; the 4-hourly phase may have differed in October):

- BETA prefill b03 at 17:31-17:41 matches trustkit's `com.apple.trustkit.signatures` at about 17:31.
- GAMMA decode b05 at 23:15 matches the softwareupdated scan at about 23:09.

No unit lines up with the 00:00 `/tmp` cleaner. Three GAMMA units fall at 01:18-01:58, and trustkit's 01:31 run lies
between them, not on them.

**(c) References and the corpus are lost far more often than their 1.6 s span predicts.**

- Observed: **10 of 77 (13%)**. The per-second fit predicts 1.9%, and P(≥ 10) is 2 × 10⁻⁶ (derived).
- They run at the window edges. The 18-member corpus runs in the first hour after arm.
- BETA's losses include 5 corpus members and decode-absolute r03, r06 and r10, all in its first stage, within 25 min of
  stage start. Its corpus position is not derivable from the permitted read.
- Readings that fit: a post-arm or post-launch settling burst, since the arm needs only 180 s clean; or a request span
  for references that is wider than the 1.6 s measured run. The extractor's `request_s` settles which one.

**(d) Stage starts.**

- The first quad of every GAMMA stage was lost, and two of those four were host-busy events:
  - decode b01-b1, contention;
  - prefill b01-b1 and b01-a2, idle-admission aborts.
- BETA lost decode b01 and prefill r01, the first unit of each stage, to admission aborts.
- **Admission aborts are host-busy losses too.** Idle admission refuses when CPU busy p95 exceeds 0.5. The B5
  rehearsal's abort was Spotlight's corespotlightd at 0.54 CPU-s/s (registration_block5.md:1886).
- Counting aborts, GAMMA lost 11 of 80 contrast members (13.75%).

**(e) Host state during Block 5, from the repository record.** During Block 5 (10-09 to 10-12):

- mediaanalysisd was **not** yet held: SIGSTOP began 10-17 (`RUN_STATE.md` item 188);
- photoanalysisd was not held either: SIGSTOP began 11-06;
- the displays were asleep, because the campaign environment requires it.

So Photos/media analysis was live, and at about 190 photoanalysisd restarts a day, with a burst of about 0.6 CPU-s
each, it alone crosses 0.05 CPU-s/s in a 10 s interval. It is the leading single-process hypothesis. Next come the
dasd background-task waves (about 650 starts an hour on this idle Mac; item 206), Spotlight
(mdworker_shared/corespotlightd; item 189, rehearsal) and fseventsd (the registration's original forcing case).

### 1.3 Culprits and fixes the magistrate can apply on the MBP

The order is by expected share under the hypotheses above. The process attribution is a hypothesis until §1.4 runs.

| # | Suspected source | Evidence in B5 | Fix on the MBP | Already handled? |
|---|---|---|---|---|
| 1 | photoanalysisd / mediaanalysisd (Photos library analysis) | Live during B5; respawn bursts of about 0.6 CPU-s, about 190 a day (item 188) | Keep both SIGSTOPped (`/Users/edr/night-custody/magistrate/photoanalysisd-stopped`). To make it permanent, Ed opens Photos and turns off library analysis or the iCloud Photos sync, or uses `launchctl disable gui/501/com.apple.photoanalysisd` if SIP allows it | Yes since 11-06 (SIGSTOP), but survives no reboot. Add a check of the STOP state to PREQUAL |
| 2 | dasd background waves (routined, coreduetd, contacts, ids, osanalytics, Safari SafeBrowsing) | Item 208: refused R0 at 0.052; about 650 an hour | Ed's call: System Settings → Privacy → Location Services → System Services → Significant Locations off (routined); Analytics & Improvements sharing off (osanalytics); Siri & Suggestions off (duetexpertd/suggestd); quit Safari | **No.** Only flagged (R0-L3) |
| 3 | Spotlight (mds_stores, mdworker_shared, corespotlightd) | Item 189 refusal; rehearsal abort at 0.54 CPU-s/s | `sudo mdutil -a -i off`, and SIGSTOP corespotlightd and spotlightknowledged for the window, as the R0 launcher does | Partly. The R0 launcher stops them; confirm the v4 window path does too |
| 4 | softwareupdated scan, about 05:09/11:09/17:09/23:09 | GAMMA b05 at 23:15; R0 at 0.25-0.29 core (item 218) | `sudo softwareupdate --schedule off`, and `defaults write /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled -bool false` (needs sudo, so Ed's OK) | **No.** Scheduled around and flagged |
| 5 | frauddefensed trustkit, 4-hourly at about xx:31 | BETA b03 at 17:31 | Cannot be disabled. Arm-time avoidance for its own segment only | Schedule known (item 205) |
| 6 | Display / WindowServer / ControlCenter location indicator | Not seen in B5, because displays were asleep | `pmset displaysleepnow` plus a 300 s dwell; Ed's call on the Location Services client (WirelessDiagnostics) | Yes (#700, R1 D3, R16 P2) |
| 7 | `/tmp` cleaner at 00:00 (find, fseventsd) | No B5 unit at 00:00 | Keep `/private/tmp` small | Yes (item 206) |
| 8 | Post-arm and stage-start settling | §1.2 (c) and (d) | **Prospective design** (BYTES, later blocks): repeat the 180 s clean contention dwell at every stage launch, not only at arm. Place the NEG-8 corpus after a warm-up member rather than first | No |
| 9 | iCloud (bird, cloudd), Time Machine | Not identifiable without names | Ed's call: pause iCloud Drive; `tmutil disable` if auto-backup is on | Unknown. Check `tmutil destinationinfo` |

**The structural fix outranks daemon hunting** (Ed's proportionality ruling; item 207).

- The registered load-correlated sensitivity line restores the contention-removed quads (RC
  `disclosures.load_sensitivity`; uncompared, and not a registered L9 number):
  - decode moves **+0.17 J** (146.80 against 146.63);
  - prefill moves **−0.15 J** (101.66 against 101.81).
- The floors are 10.2 J and 8.8 J. The 0.05 CPU-s/s rule therefore removed 45% of quads to guard against effects
  about 1/60 of the floor.
- **Recommendation for every prospective registration (BYTES, later blocks):** keep `contention.request_overlap` as
  DISCLOSE. Exclude only above an **energy-scaled** bar, for example outside CPU-seconds inside the span ×
  P_core_W ≥ 10% of the cell's registered floor. Prove the bar on this corpus by replay, per R18, before it gates.

### 1.4 Guard-replay corpus export (R18)

`docs/ops/guard-replay-corpus/b5/` holds two things.

**`extract_b5_guard_corpus.py`** reads, in each harvest root, only the monitor's 10 s intervals, the request spans,
the roster and the flag offenders. It keeps the process and timing allowlist of `joulewise/guard_replay_corpus.py`,
and writes two outputs:

- a `joulewise.guard_replay.corpus.v1` corpus: about 300 member runs, each with its real `request` span and ±60 s of
  `contention_interval` frames, plus 3 whole-window runs of about 4.5-5 h;
- `culprits-b5.{json,md}`: the table §1.1 lacks, giving process, CPU-s/s, start in UTC and local time, episode
  duration and a census by local hour.

It was tested on a synthetic harvest built from the committed FakeMac journal:

- it produced the `fseventsd` 0.90 CPU-s/s culprit row with a 20 s episode;
- a planted energy field did not leak;
- the output passed `guard_replay.validate`;
- the real `contention_request` adapter returned PASS and REFUSE on the clean and overlapped members.

**`b5-loss-timeline.json`** is everything the permitted read supports. It is a label and timing skeleton, and it
cannot be replayed.

**Owed.** The lead or magistrate, with Block 5 archive access, runs the extractor once (README command, about a
minute), commits the outputs and pastes `culprits-b5.md` into §1.1. Member labels are the B5 predicate's own verdict.
They are circular for that predicate and valid for evaluating **other** candidates: ruling 8, a 30 s interval, or the
energy-scaled bar. The window runs are unlabelled host traces for the shadow-mode bound.

---

## 2. Exclusion versus condition

### 2.1 Did exposure drive the 8B-skewed losses?

**Yes.** The per-second hazard is equal on the two arms: 1.7B 0.0119 per s, CI 0.0037-0.0276; 8B 0.0121 per s, CI
0.0067-0.0200. The predicted 8B share of contention flags is 76.7%; observed is 13/17 (76.5%) pooled and 5/6 in GAMMA.
Admission aborts were balanced in GAMMA (2 on 8B, 2 on 1.7B) and are not exposure-driven.

Whole-quad removal (§6.6) keeps the comparison symmetric. The kept quads still under-represent stage starts (§1.2 d).

### 2.2 Loss probability per member-second

| Loss route | Model |
|---|---|
| Contention at the B5 bar | P(flag) = 1 − exp(−λT), λ = 0.0121 per s of request (CI 0.0072-0.0187) |
| Admission abort (per member, not per second) | GAMMA 4/80 = 5%, BETA 3/100, ALPHA 2/100 |
| Anchor not bounded | 1/80 GAMMA, 1/100 BETA |

Quad-loss planning formula (derived):

> P(quad lost) = 1 − exp(−2λ(T_A + T_B)) × (1 − p_abort)⁴ × (1 − p_anchor)⁴

| GAMMA contrast | Predicted quad loss | Observed |
|---|---|---|
| Decode | 0.37 | 0.40 |
| Prefill | 0.43 | 0.50 |

The registration's 1/37 implies about 0.10 per quad.

### 2.3 v4 projection: benign versus sabotage

Sources: `docs/align/pilot_protocol_v4.md` on `align/2026-11-08-v4-r11` and `series_manifest.json` on
`align/2026-11-08-dct-series-merged`.

**The v4 D member.**

- Benign and sabotage D members have the **same** 1,800 s allowance. Every D member is sized at the largest W1 D
  `member_s`.
- The episode is (1,800 − 516.575) / 1.13544 = **1,130 s**, which includes 300 s idle, leaving about **830 s active**
  (PP4:84, 193-197; pilot_protocol_v3.md:169).
- Up to 12 turns of 4,096 output tokens.

| Episode span | P(flagged at the B5 bar, λ = 0.0121 per s) |
|---|---|
| 830 s (benign = sabotage allowance) | **0.99996** (CI ≥ 0.9975) |
| 300 s | 0.973 |
| 60 s | 0.515 |
| 10 s | 0.114 |

**Under B5's rule, v4 would exclude every D member and end `insufficient_calibration` with certainty.**

**v4's actual rule.**

- No member-level host-contention exclusion exists in the v4 kit. A search of `joulewise/align`,
  `configs/campaigns/align_v4` and `pilot_protocol_v4.md` on `v4-r11` finds only the R0/SMC ruling-8 redo and flag.
- The ruling-8 redo (≥ 0.5 core for ≥ 60 s) applies to R1 segments and R0 SMC only (PP4:1106;
  `docs/align/r0/R0-L3-contention-rule.md`).
- The member exclusions are X1-X8 (thermal, PM, identity, OOM, deadman) and battery B (PP4:491-498, 637-649).
- So **the projected v4 member loss from this hazard is about 0, for benign and sabotage alike.** Contention flags
  will sit on nearly 100% of members. A flag that marks every member carries no information, so the flag must record
  the offender's CPU-seconds, not only its presence (§6, item 1).

### 2.4 Probability that the fixed-8 calibration reaches ≥ 39 eligible per pair

The design is 8 C windows × 7 benign per pair = 56, with ≥ 39 needed per pair, no replacements and no extension
(SM `calibration`; PP4:950-956). Results from the derived binomial and simulation (`lessons-derivations/v4proj.py`):

| iid member loss p (no window loss) | P(both pairs ≥ 39) |
|---|---|
| ≤ 0.10 | 1.000 |
| 0.1375 (GAMMA's member rate) | 0.999 |
| 0.20 | 0.957 |
| 0.25 | 0.739 |
| 0.30 | 0.346 |
| ≈ 1 (B5 rule applied to v4) | 0.000 |

| Whole-window loss w per C window, with p | P(success) |
|---|---|
| w = 1/8, p = 0.05 | **0.87** |
| w = 1/8, p = 0.10 | 0.76 |
| w = 1/4, p = 0.05 | **0.59** |
| w = 1/4, p = 0 | 0.68 |

Losing three windows (21 per pair) fails outright: 56 − 21 = 35 < 39.

A captured-but-barred window (U1-U3) counts toward the 8 and its benign members do not enter m (RUN_STATE item 226).
B5's attempt history is a warning: BETA needed **6 attempts, 5 unusable** (NEG8, CALIBRATION, ROSTER,
`cell.below_minimum`). Each would have been a counted, lost window under v4's rule.

### 2.5 Prospective mitigations (before W1 registration)

1. **A quiet-Mac fix will not save a 0.05 bar** over 830 s episodes: even λ/10 gives P(flag) = 0.63. Keep v4's
   flag-only rule and write it into the registration explicitly (§6, item 1).
2. **Member-level rather than quad-level loss.** v4 is already member-level. For ABBA designs (BYTES, later blocks),
   whole-quad removal multiplied 11 member losses into 36 lost bundles. Two options:
   - register a blind, end-of-stage **replacement quad** for each quad lost to a PHYSICS or abort code, capped at 2
     per stage and pre-declared;
   - or print the half-quad (AB or BA) sensitivity.
3. **More windows.** The quantity to buy down is whole-window loss, not member loss (§2.4). Two ways to do it:
   - register a structural-failure extension: one C9, allowed only when a C window is barred for a U1-U3 or
     zero-member-eligibility cause, decided blind before any test window opens;
   - or accept P ≈ 0.6-0.9 and disclose it. R15 currently forbids extension, so this is a lead ruling.
4. **A balance check by condition** (benign against sabotage, and per pair). Print exclusions and contention flags
   per member-second by condition, with the exposure-adjusted expectation from this λ. Sabotage episodes may run
   longer inside the same allowance, so any exposure-linked exclusion (battery accumulator excursion, X2 thermal
   hold, X7 deadman) would remove them unevenly. This is item 232's new tracked metric.

---

## 3. Window-to-window variation (τ)

### 3.1 Estimate

Source: RC `disclosures.cross_window`. F is the separate-window reported cell (ALPHA or BETA); G is GAMMA's per-arm
estimate of the same quantity. se_F comes from RC `reported_cells.*.interval.variance`; se_G = h_G / t(n−1). The
estimator is a method-of-moments τ² = δ² − se_F² − se_G² (derived).

| Cell | δ = G − F | z | τ | τ relative to cell | τ / s_r |
|---|---|---|---|---|---|
| 1.7B decode (51.2 J) | +0.104 J | +1.85 | 0.088 J | 0.17% | 0.35 |
| 1.7B prefill (26.3 J) | −0.041 J | −0.62 | 0 | 0 | 0 |
| **8B decode (198.4 J)** | **−0.422 J** | **−4.63** | **0.412 J** | **0.21%** | **1.30** |
| 8B prefill (128.3 J) | −0.261 J | −2.19 | 0.232 J | 0.18% | 0.73 |
| Pooled (mean τ²) | — | χ²(4) = 30.0 | **0.24 J** | **0.13%** | about 0.75 |

**On a contrast.**

- Building the contrast across windows (BETA − ALPHA) gives decode 147.155 J, against GAMMA's within-window
  146.629 J: **0.53 J apart, 7 GAMMA se**. For prefill the gap is 0.22 J.
- If the shock is common to both arms inside a window, τ_contrast ≈ 0.36 J per window (derived), and it cancels in
  every within-window contrast. This is why GAMMA, not ALPHA versus BETA, is the claim.
- The two 8B cells moved together by about −0.2% between BETA (Sunday afternoon) and GAMMA (Sunday night). A
  multiplicative window shock fits. A thermal or ambient leakage reading is plausible but untested.

### 3.2 What to use

- **For energy level comparisons across windows:** a multiplicative shock of **0.13% pooled, 0.21% as stress**. It
  should be reported beside every cross-window number.
- **For within-window contrasts:** about 0. Use the GAMMA design.

### 3.3 Into the v4 B3 simulation

B3 (`docs/align/v4/b3-sim/B3-SIM-sol{1,2}.md`) puts τ in units of s_r, the within-window **benign residual SD of the
v4 score**. It tests τ ∈ {0, 0.25, 0.5}, with 0.5 as the headline stress. B5's s_r is a repeat SD of a fixed prompt
(0.16-0.30% of the cell). v4's s_r is the residual of agentic episodes, which have varying trajectories and is likely
several percent. The conversion:

- τ_v4 / s_r,v4 ≈ 0.0021 / (s_r,v4 as a fraction of mean energy);
- so if v4's benign residual SD is at least 0.84% of episode energy, τ ≤ 0.25 s_r;
- at 0.42% or more, τ ≤ 0.5 s_r, so B3's stress setting covers it.

**Action.** When W1 or C1 gives the first benign residual SD, compute this ratio and record which B3 row applies.
Until then, B3's τ = 0.5 s_r stress is conservative unless v4 residuals are tighter than 0.42%. That would be
surprising for agentic episodes. One caution: the A4 fit is per window × pair, which absorbs a window's level shock
inside C. A **T** window gets a fresh shock relative to thresholds carried from C. That is B3's exact model, so the
mapping holds.

### 3.4 Into the v5 power simulation

v5's ρ (`docs/align/squeeze/v5-design/RULING-DRAFT.md` §4e, revision 7, `ruling_power_sim.py`) is the **rescue
intraclass correlation**: a Gamma(mean 1) window multiplier on a per-attempt rescue probability. It is dimensionless,
has no energy scale, and B5 does not measure it. B5's energy ICC would be τ²/(τ² + s_r²) = 0.36 pooled and 0.63 for 8B
decode, but it is the wrong quantity and must not be entered as ρ̂.

The sizing rule decides from G12's r̂ and m̂:

- **r̂ ≤ 0.02 and m̂ ≤ 0.02:** 28 windows, **baseline**, whatever ρ̂ is.
- **Otherwise:** the frozen sim reruns at (r̂, m̂, ρ̂), with ρ̂ = 0.30 if the development ICC exceeds 0.15. It lands at
  +8 windows (intermediate law, 36) or +24 (stress, 52).

The one B5 lesson that does transfer: **window clustering is real on this Mac.** χ²(4) = 30 at τ = 0. A development
ICC above 0.15 is therefore plausible, so plan the reserve for the stress branch.

### 3.5 BYTES

Any BYTES number compared across sessions or windows should carry a ±0.13% window term (0.21% as stress) on gross
rail energy. Within-window contrasts do not need it.

---

## 4. Timing bound D: decomposition and levers

### 4.1 Decomposition

Source: RC `contrasts.*.D_terms_j` and `members.GAMMA.*.a_bop_j`, plus `windows.GAMMA`.

| | Decode | Prefill |
|---|---|---|
| D | 5.084 J | 5.633 J |
| Clock-anchor term | 4.111 J (81%) | 4.660 J (83%) |
| = mean anchor bound, 1.7B arm | 1.855 J | 2.389 J |
| + mean anchor bound, 8B arm | 2.255 J | 2.271 J |
| Interpolation | 0 | 0 |
| NEG-8 drift allowance | 0.974 J (19%) | 0.974 J (17%) |

**How the arms combine.** The contrast adds the two arms' bounds **linearly**: per block bound_A + bound_B, then the
mean over blocks (`analysis_engine/estimators.py` lines 76-90 and 414-447). This was reproduced exactly (derived:
1.8555 + 2.2551 = 4.1106).

**Which anchor dominates.** It is **not** the member's registered clock anchor (§0.14, effective bound ≤ 5 ms; the
largest in GAMMA was 4.27 ms, DISC `anchor_bound`; member m_s 0.6-4.3 ms). It is the window's operative fiducial
bound:

- **b_op = 47.97 ms** = max(b_pre 28.37, b_post 33.44 ms) + the operative bracket screen 14.53 ms
  (gamma-verdict `operative_bracket_screen_decimal_s` 0.014531);
- this is the powermetrics sample-stamp to monotonic offset bracketed by the pre and post calibration pulses.

**The member bound scales with b.** The ratio a_bpre/a_bop is 0.57-0.60, against b_pre/b_op = 0.591. The method is
`common_trace_shift_plus_independent_edge_corners_v3` (`joulewise/reduce.py` around lines 2064-2146), which shifts
each phase edge independently by up to ±b. Edge power is about 20-25 W for 1.7B decode, so the bound is about
(P_start + P_end) × b ≈ 2 J.

### 4.2 Levers and their size (derived, assuming the bound is linear in b)

| Lever | Anchor term (decode / prefill) | D (decode / prefill) | Change |
|---|---|---|---|
| Today | 4.11 / 4.66 | 5.08 / 5.63 | — |
| **Timing receipts** (`perf/2026-11-08-timing-receipts`) | unchanged | unchanged | **0%**. They stamp run_night, arm, dispatch and controller boundaries in monotonic/wall. No powermetrics sample stamp, no `stamp_mapping`, no fiducial |
| Remove the 14.53 ms screen (a mid-window calibration bracket, so the operative bound is the measured bracket end) | 2.86 / 3.25 | 3.84 / 4.22 | −24% / −25% |
| Per-member or denser-pulse fiducial at about 5 ms (the member anchor class) | 0.43 / 0.49 | 1.40 / 1.46 | **−72% / −74%** |
| **Governed common-mode `contrast_bound`** (the estimators.py hook): if the bracketed offset is one shared shift for both arms of a quad, the contrast moves by about the difference of the arm bounds | 0.40 / 0.12 | 1.37 / 1.09 | **−73% / −81%** |
| Both of the last two | about 0.04 / 0.01 | about 1.0 / 1.0 | −80% / −82%; then the NEG-8 allowance dominates |

**The common-mode lever is not licensed by B5's data.** It needs a registered argument, plus a test, that the
fiducial offset is shared within a quad and is not independent per edge. Registration §0.10 treats the edge part as
independent. The D-165 common-mode ratios R_cm (1.70-2.77, three below 2) were computed for floors and do not settle
it.

**After the anchor, the NEG-8 drift allowance is next** (0.97 J; corpus s 0.347 J, t 2.201, 12 members). The corpus
is the member class contention hits hardest (§1.2 c). Fixing reference and corpus contention (stage-settling dwell,
corpus after warm-up) both stabilizes and shrinks it.

**For v4.** A21 uses production `stamp_mapping`, and A3 sets half-widths to zero with attribution bounds print-only.
D does not gate v4. The lesson applies to any rails-energy claim in BYTES and later blocks: the anchor bound decides
the decision interval (94-96% of its width; RESULTS.md §1) and the published floors (`attribution_limited`, source
`E_clock_anchor_shift_bound_j`). A tighter fiducial would lower the 10.2 J and 8.8 J floors in proportion.

---

## 5. Comparator coverage: rules for the v4 comparator and `release_v4`

### 5.1 What B5 showed

- **`window_edge_s` compared 0 rows and the release still said "agree across 24 families"** (CMP; comparator
  stdout).
  - The emptiness was structural: every whole-machine window used `controller_stamps` and compared exactly under
    `count` (`scripts/compare_b5_recompute.py` around line 3640).
  - Nothing declared that ahead of time, so an empty family looked the same as a mapping bug.
- **Seven registered disclosure families were never recomputed** (DLE-1). There were also 403 uncovered numeric
  leaves.
- **A registered sensitivity line could not be computed in L9.** The load-correlated line failed with
  `member_code_on_kept_unit`. The recompute's value exists and is exempt from comparison.
- **Collection-time judgments were taken from storage**: flags, anchors and calibration fits. Nobody re-detected
  contention from raw journals.
- **The p-value bar (1e-6 absolute) could not separate 1e-11 from 1e-15.**

### 5.2 Rules

**R-C1. Empty family = HOLD.**

- Every declared comparator family carries `min_rows` (default 1) or `expected_empty: {reason, predicate}`. The
  predicate is evaluated on structure only, for example "no member has `window_basis == legacy_wall`".
- A family with 0 rows and no satisfied `expected_empty` holds the release (exit 1).
- The verdict prints "N families compared, E expected-empty, 0 unexplained-empty", never "agree across N".

**R-C2. Frozen row-count manifest.**

- Before any data, `release_v4` derives from the roster and series manifest, blind, the expected row count per family
  (for example per window × pair × member × channel).
- Actual counts outside [expected − declared exclusions, expected] hold the release.
- This catches an empty family and also a silently partial one.

**R-C3. Every registered output family is classified** as `recomputed+compared`, `integrity_only` (digest only, with
a named deviation) or `exempt` (with a ruling id).

- The renderer refuses to print a number from an `integrity_only` or exempt leaf unless a hand-check receipt (item
  83 ruling 3) is bound to that leaf's key path.
- The uncovered-leaf count must be 0 for every leaf the paper prints.

**R-C4. Every sensitivity line computes on a fixture before data.**

- Every registered sensitivity and robustness line (for v4: the U5 descriptive, the R20 sentinels, the LOTO/full-fit
  variants, assist-disclosed lines) must compute on a synthetic fixture that exercises its hard case. B5's hard case
  was a member code on a kept unit.
- A line that returns uncomputable on real data, where the fixture said computable, is a HOLD.
- Where the engine and the recompute both produce the line, it is **compared**, never exempt.

**R-C5. Re-derive eligibility from raw journals.**

- The v4 recompute re-derives member eligibility (X1-X8, battery B, the contention flag's CPU-seconds) from the raw
  journals, independently of the engine's stored flags.
- The comparator compares the eligibility vector member by member.
- The counted m per pair is a release-gating family, and its mismatch is a REFUSE. It decides `calibration_stop`.

**R-C6. Bars matched to scale.**

- p-values and tail probabilities use a log-relative bar (for example |log10 p₁ − log10 p₂| ≤ 1e-6), or are compared
  through their compared inputs (t, df), with the absolute bar kept only for p > 1e-3.
- v4 rank thresholds (order-statistic picks) are compared **exactly** by member id and rank, not numerically.

The exit contract stays as in B5 (refused 2 > hold 1 > agree 0; R21).

---

## 6. Ranked recommendations

**Before W1 registration (v4 is unregistered, so these go into the registration text).**

1. **Write the in-window contention rule explicitly.**
   - `contention.request_overlap` is DISCLOSE-only for D, anchor and sentinel members. Never adopt B5's 0.05 / 10 s
     exclusion, which projects to about 100% loss and certain `insufficient_calibration` (§2.3).
   - Record each member's outside CPU-seconds inside its span and the top offenders, so the flag carries a magnitude.
   - Bound `contention.unmeasured`: if any catalog makes it EXCLUDE_MEMBER, a monitor hole anywhere in an 830 s
     episode is far likelier than in a 10 s request. Require a gap above 60 s, or downgrade it to DISCLOSE plus a
     U1-style per-window cap.
2. **Rule on whole-window loss for the fixed-8 calibration.** P(success) is 0.87 at 1-in-8 and 0.59 at 1-in-4 barred
   windows (§2.4). Options:
   - (a) a pre-declared structural-failure C9, triggered blind;
   - (b) accept the risk and disclose it;
   - (c) tighten what can bar a window. A U1-U3 fail is window loss.
3. **Balance check by condition** as a registered descriptive: exclusions and flags per member-second, benign against
   sabotage and per pair, against the exposure-adjusted expectation (§2.5 item 4).
4. **Comparator and release rules R-C1 to R-C6** in the v4 comparator and `release_v4` before the synthetic
   full-series rehearsal (R21 next step).
5. **τ for B3:** record τ_rel = 0.13% (stress 0.21%) and the conversion rule of §3.3, to be applied when the first
   benign residual SD exists.

**Before the W1 arm (magistrate; no registration text needed; sudo or settings items need Ed's OK).**

6. Host hygiene, in order:
   - keep photoanalysisd and mediaanalysisd STOPped, with a PREQUAL check;
   - `softwareupdate --schedule off`;
   - `mdutil -a -i off`, plus corespotlightd and spotlightknowledged STOPped on the v4 window path;
   - Significant Locations, Analytics sharing and Siri Suggestions off;
   - check Time Machine and iCloud.

   These reduce the flag rate. Under v4's flag-only rule they are not needed for eligibility.
7. **Run `extract_b5_guard_corpus.py`** on the three B5 harvest archives (authorized reader), commit the corpus and
   culprit table, and replay ruling 8 and any energy-scaled candidate against it (R18 shadow mode).

**For BYTES and later blocks (prospective registrations only; Block 5 and anything sealed are unchanged).**

8. **Energy-scaled contention exclusion** in place of the 0.05 CPU-s/s bar (§1.3), proven by replay.
9. **Plan sizes with the measured hazards** (§2.2 formula, λ = 0.012 per s, aborts 2-5% per member), not 1/37.
   Pre-declare blind replacement quads at stage end.
10. **A stage-launch contention dwell** of 180 s at every stage start, and the NEG-8 corpus after a warm-up member.
11. **Timing anchor:** a per-member or denser-pulse fiducial, plus removing the screen allowance through a mid-window
    bracket, gives D −24% to −72%. Then decide whether to register a governed common-mode `contrast_bound` (up to
    −81%) with its own validation test. Timing receipts do not help here.
12. **Report cross-window numbers with the 0.13% / 0.21% window term.** Keep every confirmatory contrast within one
    window.

**Learn from (process).**

- The registration's loss assumption (1/37) was the single most consequential planning number. It came from one
  measured cause.
- Next time, estimate member loss from a pilot window under the exact production hazard rules, per member-second and
  per cause, before freezing a cell minimum.
