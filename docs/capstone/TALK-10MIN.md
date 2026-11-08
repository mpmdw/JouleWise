# Capstone talk, 30 November 2026: 10-minute version

**Title:** *Sabotage Leaves an Energy Signature: A Pilot Study of Physical Auditing for AI Agents*

**Format.** 11 slides, about 9:40 of speaking, which leaves 20 s of slack in a 10-minute slot. This is half B of [TALK-OUTLINE-v2.md](TALK-OUTLINE-v2.md). B4 is folded into slide 4 as one clause, B9 and B10 are merged, and half A is reduced to one slide (10). The readable page is [TALK-10MIN.html](TALK-10MIN.html).

**Evidence rules (unchanged from v2).**
- Every number has an E ID from the ledger in [PAPER-OUTLINE.md](PAPER-OUTLINE.md). A number without an ID does not go on a slide.
- Block 5, BYTES held-out, v4 and Block 6 outcomes are sealed. Show gate **status** only, never a value.
- Say "DC input", never "wall energy". The KM003C sits after the brick and before MagSafe.
- In the pilots the scored channel is `powermetrics` GPU energy, which is host software. Say so on slide 3.
- `[FREEZE]` cells are filled from `RUN_STATE.md` gate status on 22 November (see [PAPER-PLAN-v2.md](PAPER-PLAN-v2.md)).

| # | Slide | Time | Running |
|---|---|---|---|
| 1 | Title | 0:20 | 0:20 |
| 2 | Monitors read content | 0:50 | 1:10 |
| 3 | The idea: predict joules from the log | 1:00 | 2:10 |
| 4 | The instrument | 1:00 | 3:10 |
| 5 | What the pilot tested | 0:50 | 4:00 |
| 6 | Result | 1:15 | 5:15 |
| 7 | Why it is still a pilot | 1:05 | 6:20 |
| 8 | Three layers and the squeeze | 1:00 | 7:20 |
| 9 | v4 and v5 | 1:15 | 8:35 |
| 10 | How one person ran this | 0:35 | 9:10 |
| 11 | Close | 0:30 | 9:40 |

**If you are running long:** drop slide 10 and keep its last sentence in the close (saves 0:35). Then shorten slide 8's escape routes to two. Never cut slide 6's two-trajectory footnote or slide 7.

---

## 1 · Title (0:20)

- **On the slide:** the title, your name, and a photo or drawing of the laptop with the inline USB-C meter.
- **Say:** "I'm an undergrad. This is a pilot study on one laptop with a power meter in its charging cable. Some results are still sealed, and I'll say which."

## 2 · Monitors read content (0:50) · from B1

- **Message:** Transcript and chain-of-thought monitors only see what reaches the log. Agents that know they are monitored can keep work out of it.
- **On the slide:** three qualitative examples: a hidden scratchpad, obfuscated reasoning, an edited log. No borrowed catch rates.
- **Say:** SHADE-Arena gives an agent a legitimate main task and, in sabotage runs, a covert side task. We run open models on two of its task pairs.
- **Sources:** SHADE-Arena (arXiv 2506.15740); Baker et al. (2503.11926); LIT §4 M4.

## 3 · The idea: predict joules from the log (1:00) · from B2

- **Message:** Fit energy against the logged work on honest episodes. A large positive residual means the machine did more work than the log explains.
- **On the slide:** `residual = measured J − predicted J(logged prefill, decode, context)`, then benign fit → calibration → score (F1, F2). Label `powermetrics` "host software: the pilots' scored channel".
- **Say:**
  - "The agent cannot rewrite an independently retained meter reading under our privilege assumptions. It can still change what work it does."
  - "In the pilots the score uses the GPU rail from `powermetrics`, which runs on the same host. That is why the external meter matters."

## 4 · The instrument (1:00) · from B3, with B4 as one clause

- **Message:** The software rails miss most of a controlled memory-traffic contrast, so an external DC meter is needed.
- **On the slide:** the power path AC → brick → KM003C → MagSafe → laptop (F3). The contrast: rails **0.0092 ± 0.0021** J/GB, DC input **0.0389 ± 0.0072** J/GB, rails share **f = 0.238 ± 0.098**, so **about 76 % outside the rails** (E1, E2).
- **Say:**
  - "In this rotate-minus-repeat test", never "76 % of inference energy".
  - "Rest" is DC minus rails: memory, fabric, conversion and fans together. It is not a DRAM measurement.
  - One clause from B4: "and the meter has to model active work, not model size: two models of similar size differ about tenfold in weight bytes read per token" (E3, accounting only).
  - The reading rule was corrected after the data existed. Call it a validation check.

## 5 · What the pilot tested (0:50) · from B5

- **Message:** Known-H tampering removes logged reasoning counts while the executed episode, and its joules, stay fixed. It tests detection of a known log omission, not of intent.
- **On the slide:** Qwen3-30B-A3B MLX 4-bit, thinking on; `spam_filter_update` and `bank_transfer_2`; turn limit 12, output budget 4,096, context cap 40,960.
- **Say:** the model's terms were selected using pilots 4-7. Say so before anyone asks.

## 6 · Result: the tested omissions crossed the threshold (1:15) · from B6

- **Message:** In pilots 8-10 every tested omission was detected, and no untampered sabotage reading crossed its threshold. That is two trajectories checked repeatedly.
- **On the slide:** per-pair table. Benign calibration **m = 28** per pair; thresholds **bank 2.53, spam 7.13** (E6). Untampered sabotage below threshold in all six checks; detected at the smallest tested omission, **H = 539 (spam) and 1,193 (bank) tokens** (E7). Large footnote: **two distinct sabotage trajectories, each re-checked across sessions.**
- **Say:**
  - "Detected at the smallest H we tested" is not a minimum detectable H. There is no detection curve and no interval over six independent attacks.
  - An identical replay repeats to about 1.93 J of residual SD (E5), against regression residual SDs of 19-58 J (E4). Do not turn this into a sensitivity multiple.

## 7 · Why it is still a pilot (1:05) · from B7

- **Message:** Sample-maximum thresholds, design selection, host-software scoring and log edits limit what the pilot shows.
- **On the slide:**
  - spam threshold **7.13** against the next-largest **2.99**: one tail point sets it (E6);
  - selection-inclusive diagnostic: bank **2/26** untampered above threshold, spam **0/26** (E8);
  - exclusions: pilot 8 had 27/28 eligible, pilot 10 had 24/28 (E9);
  - the tamper is a log edit, not real hidden computation; the scored channel is host software; one device, two task pairs, one model; a non-adaptive agent.
- **Say:** none of these are population false-alarm rates. v4 exists to close these gaps.

## 8 · Three layers and the squeeze (1:00) · from B8

- **Message:** Monitors see content, the meter sees quantity, probes see internals. The squeeze is a hypothesis: hiding from one should expose you to another.
- **On the slide:** three columns (monitor = content, meter = quantity, probes = internals) and the escape routes: logged cover work, filler or encoded reasoning, matched-energy padding, and latent reasoning at fixed compute, where the meter is blind (weight-only physics effect estimated at ≤ 3×10⁻⁵ of energy, a design estimate, not a measurement).
- **Say:** "Hypothesis, untested." Energy's niche is computation the runtime does not mediate: side generation, tool subprocesses, runtimes the auditor cannot trust or re-run.

## 9 · v4 and v5 (1:15) · from B9 + B10

- **Message:** v4 turns the pilot into a registered test with rules fixed before data. v5 asks whether successful sabotage can escape a joint energy-plus-monitor audit by an adaptive agent.
- **On the slide:**
  - v4: R0 → R1 → blind registration gate → W1 → three D windows → calibration (m ≥ 39 per pair plus a held-out test cohort) → independent recompute → release. Each box shows `[FREEZE]` status, never an outcome. Qwen3.8-27B 8-bit; KM003C in every window; full transcripts sealed and unscored.
  - v5 endpoint: **side-task success and no joint alarm, per attempt**, with utility; joint rule calibrated at 0.05 against energy-alone, monitor-alone and time-plus-monitor comparators; frontier API monitor off-box.
  - Timeline: talk Nov 30 → paper mid-December → v5 windows December-February → NeurIPS 2027.
- **Say:**
  - Example of deciding first: 8-bit decode at about 11.9 tok/s could not fit the original budget, so the fallback was declared before any R1 number existed.
  - If asked about results: "sealed until the registered release; I don't know them."
  - The v5 design is still being judged. Do not name a roster or sample size. Expect a measured limit rather than a clean win.

## 10 · How one person ran this (0:35) · half A in one slide

- **Message:** A preregistered, blinded hardware study has more procedure than one person can do by hand, so AI agents run it, and agents are trusted only through what they cannot quietly change.
- **On the slide:** a small diagram: me → lead agent → magistrate on the measurement Mac → workers; sealed custody, an independent recompute, review by a second model family.
- **Say:** "The pipeline that runs the study is itself audited, the same way the study audits agents." No commit counts; they measure activity, not output.

## 11 · Close (0:30)

- **Say:** "Our pilot sees work missing from a log, and a registered test is under way. The next question is whether an adaptive agent can hide from the monitor and the meter at once."
- **On the slide:** the repo link and the paper title.

---

## Likely questions

- **"Can't the agent just pad the log to match the energy?"** Yes, that is one of the escape routes on slide 8. Padding has to be logged work, which the monitor reads. That trade is what v5 tests.
- **"Why not just re-run the episode?"** On a seeded local stack a rerun already catches stripped reasoning. Energy matters where you cannot re-run: untrusted runtimes, tool subprocesses, hardware you don't control.
- **"Is 76 % of the energy outside the rails?"** Only in this memory-traffic contrast. It says the rails are incomplete, not what share of inference they miss.
- **"Isn't `powermetrics` controlled by the same host?"** Yes. That is the pilots' main limit, and why every v4 window captures the KM003C and v5 qualifies a DC-input endpoint.
- **"What did v4 find?"** Sealed until the registered release.
