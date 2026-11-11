# Capstone talk, 30 November 2026: outline v2

**Title slide:** *Auditing AI Agents, Twice*
**Half A:** Automating research pipelines: how one undergraduate runs a preregistered hardware study with AI agents.
**Half B:** *Sabotage Leaves an Energy Signature: A Pilot Study of Physical Auditing for AI Agents.*

**Format.** 24 slides and about 23:40 of speaking: half A takes 11:00 and half B 10:55, with 0:30 for the title, 0:45 for the bridge and 0:30 for the close. Leave at least 1:20 for questions in a 25-minute slot. The three cuts at the end bring the talk to about 21:20.

**One-sentence thesis for the whole talk.** Both halves ask the same question: how do you trust work done by AI agents when you cannot watch every step? Half A answers it for our own agents with procedure (preregistration, blinding, independent recompute, cross-family review). Half B asks whether physics (a power meter the agent cannot edit) can answer it for AI agents in general.

**Evidence rules (binding on the slides, the notes and Q&A).**
- Every number on a slide has an ID: **H** for half A (ledger at the end of this file) and **E** for half B (the evidence ledger in [PAPER-OUTLINE.md](PAPER-OUTLINE.md), spot-checked again for v2; see the ledger note at the end). A number without an ID does not go on a slide.
- Block 5, BYTES held-out, v4 and Block 6 outcomes are sealed. No slide, note or Q&A answer states or hints at them. The talk may show the **status** of a gate (run, refused, pending) and the **exit-code class** of a release check, never a value.
  - **[Superseded 2026-11-10 for Block 5 only: research lead RL-10; `RUN_STATE.md` items 231 and 232.]** Block 5 was unsealed on 2026-11-08 with Ed's OK. Released Block 5 numbers may appear on a slide after RL-3's gate has passed (`docs/analysis/b5/RESULTS.md` on `main`, a cross-family re-derivation of each printed number, and the hand check for values the recompute does not cover), under the claim text of RL-4. Block 6, BYTES held-out and ALIGN v4 outcomes stay sealed, and the talk shows their gate status only. The talk's content and headline remain Ed's.
- Use "DC input", never "wall energy": the KM003C sits after the brick (item 210; AGREEMENT-FINAL authority table).
- In the pilots the scored channel is `powermetrics` GPU energy, which is host software. The external meter validates the instrument but is not yet the scored channel. Say so on slide B2.
- Gate status for slides B9 and A9 is frozen at the **22 November evidence freeze** (see PAPER-PLAN-v2.md). Fill the marked `[FREEZE]` cells from `RUN_STATE.md` on that date, and only from gate status.

---

## Slide 0 · Title (0:30)

- **Message:** Two halves, one theme: auditing AI agents.
- **Visual:** The title, and a two-panel strip: left, "agents auditing agents" (the lead/magistrate diagram as an icon); right, a laptop behind an inline USB-C meter.
- **Sources:** none (no numbers).
- **Speaker notes:**
  - "I'm an undergrad. This project ran on two laptops and a lot of AI agents. The first half is how that works and where it broke. The second half is the science it made possible."
  - Say up front that some results are still sealed and that you will say which.

---

# Half A · Automating research pipelines (11:00)

## A1 · The constraint (0:45)

- **Message:** A preregistered, blinded hardware study has far more procedure than one person can carry out by hand, so most of the procedure is run by agents.
- **Visual:** Four counters, each footnoted with its source and as-of commit: **7,905 commits on `main` since 2026-06-09 (H1); PRs numbered to #704 (H2); 212 numbered `RUN_STATE` items (H3); the decision log at D-190 (H4).**
- **Sources:** H1-H4.
- **Speaker notes:**
  - The commit count measures activity, not output. Do not present it as productivity.
  - The measurement machine is one 128 GB M3 Max MacBook Pro (`RUN_STATE.md` item 211, launch checks: Mac15,9). Analysis runs on an M4 Air.

## A2 · The architecture (1:30)

- **Message:** A laptop lead coordinates a headless "magistrate" on the measurement Mac through numbered `RUN_STATE` items. Sol/Codex workers and multi-agent workflows do the building and reviewing. Ed rules and handles the hardware.
- **Visual (figure FA1, new):** A box diagram.
  - **Ed:** email threads with the magistrate (his replies are copied verbatim into `RUN_STATE`), plus an interactive session with the lead.
  - **Laptop lead** (Claude Opus 5.5, M4 Air): rulings, kits, reviews, merges.
  - **`RUN_STATE.md` in git:** the only channel between the machines. Items run newest first; each one is either a kit delivery or a record.
  - **Magistrate** (Claude Opus 5.5, headless, MBP): a launchd watchdog ticks every 300 s and relaunches it (H5). It owns arming and re-running measurements (item 181).
  - **Workers:** local Sol 6.1 via `codex exec`, Codex Cloud tasks, and Claude workflows with seats (Opus/Fable).
  - **Instrument:** KM003C meter, `powermetrics`, SMC sensors.
- **Sources:** `docs/process/MAGISTRATE_WATCHDOG.md` (300 s tick); `RUN_STATE.md` item 181 (magistrate owns measurement, Ed quoted); `CANONICAL.md` "Measurement windows"; H6 (activation count).
- **Speaker notes:**
  - "75 `RUN_STATE` items are magistrate activations: a fresh headless Claude session reads the file, does the next safe thing, writes a record and exits" (H6).
  - Division of labour, item 181: the lead originally orchestrated measurements, and Ed corrected it: "you should not be orchestrating the measurements, that responsibility should largely be in the hands of the magistrate".
  - Agents never share memory. Everything that matters is in git, which is why the record in this talk can be checked.

## A3 · One loop, end to end (1:00) · CUT CANDIDATE 1

- **Message:** A real four-hour loop on 7 November ran from a refusal, through a human question and a rule change, to a cross-family review, a merge and a relaunch.
- **Visual (figure FA2, new):** A timeline on 7 Nov PST:
  - 17:38, R0 re-run 9 is refused by WindowServer/ControlCenter;
  - 17:46, the magistrate mails Ed; 17:48, Ed replies ("spend a little time at least trying to figure out why this shit keeps happening");
  - 18:08, the magistrate finds the display has been on since 11-05 and puts it to sleep;
  - 18:28, Ed approves the amendments ("def make amendments..."); the lead is already building them as R0-L3 (#699, #700);
  - about 18:30, re-run 10 launches with the display off; 18:41, it is refused by `routined` during a macOS background-task wave;
  - 18:50, two reviewers of R0-L3 launch together (Fable cold pass, Opus executing review);
  - 19:35, both return ADMIT_WITH_FIXES, with 97 replayed checks and 0 failures (H15);
  - 21:33, merged; about 21:50, re-run 11 launches.
- **Sources:** `RUN_STATE.md` items 206, 207, 208, 209 and 211.
- **Speaker notes:**
  - Read Ed's line aloud; it gets a laugh and it is the turning point.
  - The reviewers replayed the real refusal rows of re-runs 8-10 through the new rule. They tested against data from the actual failures, not synthetic examples.

## A4 · Guardrail 1: decide before you look (0:50)

- **Message:** Rules are fixed before the data that could bias them exists, and every departure goes in a public log.
- **Visual:** Three dated examples, each with "ruled at" and "data existed?":
  - **R10** (W1 budget fallback): declared before any R1 number (item 203);
  - **Q6** (registration grade, m ≥ 39 per pair plus a held-out cohort): decided "before any alarm is read" (item 204);
  - **DLE-0 to DLE-4**, Block-5 deviation log entries, each signed: "The lead has seen no Block 5 energy or outcome value."
- **Sources:** `RUN_STATE.md` items 203 and 204; `docs/analysis/b5/DEVIATION-LOG.md` (signing statements).
- **Speaker notes:**
  - Ed delegated preregistration rulings to the lead. It rules blind, logs publicly and tells him after (DEVIATION-LOG signing statement; `docs/handoff/2026-11-07-account-retirement/RESUME.md`).
  - Preregistration is established practice (Nosek et al.); claim the discipline, not the invention.

## A5 · Guardrail 2: blinding, with structure-only probes (0:50)

- **Message:** Agents debug sealed data without seeing outcomes. They may read exit codes, counts, key names and status words; the probes refuse to print decimals.
- **Visual:** Two columns.
  - "Allowed": the exit code, `verdict.json` through a float-masking printer, counts and enum words.
  - "Never": energy values, intervals, outcome words of real contrasts.
  - Example: the D5 root cause, found blind. A campaign-level log row listing every bundle was counted as a member, so every calibration bundle appeared twice.
- **Sources:** `docs/handoff/2026-11-07-account-retirement/RESUME.md` (standing rules, D5 cause); `docs/analysis/b5/DEVIATION-LOG.md` DLE-3 signing statement and DLE-4.
- **Speaker notes:**
  - The rule is "rational, not absolutist": software structure is fine, and only outcome-bearing content is gated.
  - Unsealing needs Ed's explicit OK. No agent can unseal.

## A6 · Guardrail 3: independent recompute, release comparator, gate ledger (1:10)

- **Message:** A second program written separately must agree with the main analysis, leaf by leaf, within bars fixed blind, before anything is unsealed. That check found six real defects.
- **Visual (figure FA3):**
  - Stack: L9 heavy pipeline ⟷ standard-library recompute (shares no code) → comparator with bars fixed 2026-10-14 → `release_b5.py` prints agree/hold per family.
  - Side panel: **1,001 failing rows in 11 families → every row attributed to one of six defects, D1-D6, from structure alone → one cause left (D5, 108 rows) → fixed in r4 (H7).**
- **Sources:** `docs/analysis/b5/DEVIATION-LOG.md` DLE-0, DLE-1 and DLE-3; `docs/run_reports/2026-11-07-b5-release-hold-trace.md` §2 ("Every failing row maps to one of six defects"); `RESUME.md` (r3 held on D5 only; r4 = PR #697); H7.
- **Speaker notes:**
  - The defects were real but mundane: a wrong key name that printed null (D1), a baseline from the wrong attempt (D2), dropped and mis-binned members (D3, D4), a double-counted campaign row (D5), and an unconditional comparison (D6). Mundane bugs are the point: they are what silently corrupts papers. D1 was in the main pipeline; D2-D4 and D6 were in the recompute or the comparator. Two programs disagreeing is how each found the other's bugs.
  - CI enforces a five-row gate ledger in every PR body (`.github/workflows/gate-ledger.yml`, required on `main`). Number-bearing code needs two executing reviews from different model families, launched together (`docs/process/gate_policy.md` rule 3).
  - `[FREEZE]` Status of the r4 release check: report only "agree", "hold" or "pending", plus whether Ed has given the unseal OK. No values.

## A7 · Win: 37 h to 1 h 40 min, proven equivalent blind (0:40) · CUT CANDIDATE 2

- **Message:** Ed treats a multi-day analysis as a bug. The rewrite was accepted only after a blinded comparator showed result-equivalence.
- **Visual (figure FA4):** Two bars, **about 37 h (r1 reference, dry-k) vs 1 h 40 min (r3, dry-l)**. A footnote gives the like-for-like pair: **27.1 h vs 1 h 46 min**, with the earlier machine more loaded (H8).
- **Sources:** `RUN_STATE.md` item 197 and item 165; `RESUME.md`; DEVIATION-LOG DLE-3 §3 (equivalence evidence).
- **Speaker notes:**
  - Do not claim the whole factor is the rewrite: item 165 says E's machine was more loaded.
  - Equivalence was shown twice, in two separate checks: the r2 rewrite against r1 on real data under the blinded D-188 comparator, and r3's speed work against r2 on the full synthetic chain (1,540 of 1,543 custody files identical; the other 3 are timing logs).
  - Lesson: the fast recompute sat unused for three weeks because nobody could see it was current, so `CANONICAL.md` now names the one current tool per job.

## A8 · Guardrail 4: cross-family review and agreement reports (1:10)

- **Message:** Claude and Sol seats review each other's work, and findings are weighted by agreement across families, not by a vote count. This caught a real overclaim.
- **Visual (figure FA5):**
  - An excerpt of the AGREEMENT-FINAL matrix: tracks × seats (Fable, Opus, Sol-1, Sol-2), with labels HC/HR/M/U.
  - Callout: Claude's squeeze design said its sample was "well powered" at 0.989/0.999. A Sol reviewer recomputed the power at a true catch rate of 0.7 as **0.118/0.255**, and the claim was rejected (H9).
- **Sources:** `docs/align/squeeze/AGREEMENT-FINAL.md` on `origin/align/2026-11-07-squeeze-agreement-final` ("Counting and confidence"; "Rejected sufficiency claims"); `RUN_STATE.md` item 212 (lead ruling R11 adopts HC/HR); H9 and H10.
- **Speaker notes:**
  - Scale: one day of research audits (7 Nov) used about 150 model agents (H10, reconstructed). Say "about 150".
  - The other direction also happens: the Opus cross-review corrected an earlier agreement report that undercounted a Sol finding (R15: "earlier AGREEMENT's 1/4 is wrong").
  - The point is not that the models are good reviewers. It is that the two families make *different* mistakes.

## A9 · Failure 1: the "quiet machine" that never was (1:10)

- **Message:** A guard written for the strictest case stopped the readiness check eleven times. Seven of those stops were ordinary macOS housekeeping, until the rule was made proportionate.
- **Visual (figure FA6):**
  - A strip of R0 attempts from 11-06 08:05 to 11-07 18:41 PST, each labelled by cause.
  - Seven contention refusals: photoanalysisd, Spotlight `mdworker`, the softwareupdated scan, the midnight `/tmp` cleaner, trustkit, WindowServer + ControlCenter (display on since 11-05), and `routined` during a background-task wave.
  - Four other stops: the launcher, a model load, a harness prompt, and sensor selection.
  - Annotation: the limit was **0.05 CPU-s/s for any single process over 30 s**, while **macOS starts about 650 background tasks per hour** on an idle Mac (H11).
- **Sources:** `RUN_STATE.md` items 177-211 (per-attempt causes); item 206 (survey: 594-685 per hour); item 207 (diagnosis); `docs/research-audits/2026-11-07/proportionality.md` (PR #695: the top over-engineering item); `docs/process/R0_HEADLESS_LAUNCH.md` (R0-L3: display sleep plus a 300 s dwell, flag instead of fail).
- **Speaker notes:**
  - Lesson 1: the agents dutifully hunted daemons one at a time. The process itself was the bug. It took Ed's "why is our quiet machine never quiet" and an audit asking what the rule protected (no reported number) to change it.
  - Lesson 2: the display had been left on since 11-05. That was a physical-world fact, and no agent asked about it until the seventh refusal.
  - The brief said "nine refusals". The record shows **7 contention refusals among 11 unsuccessful attempts** (H11), so use those numbers.
  - `[FREEZE]` R0 re-run 11 (launched about 21:50 PST 11-07 under R0-L3): its pass, fail or flag status at the freeze.

## A10 · Failure 2: when agreement is wrong, and when the guardrails bite (1:10)

- **Message:** Model reviewers can repeat one another's false premise, and safety classifiers sometimes stop the pipeline. A human with the hardware in front of him corrected the premise.
- **Visual:** Two panels.
  - **Left, the meter-path mistake.** Several model documents said the KM003C meter was not in the v4 power path, and cross-reviews repeated it rather than catching it: the literature audit, the Claude reviewer-2 synthesis, and Opus cross-reviews of Sol's work. Ed: "the usb c power meter is between the magsafe cord and the wallbrick, so it does catch all power going from wall to machine through magsafe" (H12).
  - **Right, classifier stops (H13):** the lead's `kill` of a stray process, refused; `launchctl bootstrap` of a measurement loop, refused; a push to `main`, blocked; running upstream code, blocked; one Opus research seat stopped mid-task.
- **Sources:** `RUN_STATE.md` item 210 (Ed verbatim; "Review findings that say the KM003C is not in the v4 path are refuted"); AGREEMENT-FINAL authority table (refuted passages: LIT H3, C-V §3.2, XO-D "What all four missed" #1, XO-V #5); `RUN_STATE.md` items 42, 44 and 102; `RESUME.md` (upstream code); PR #703 body (Opus seat stopped).
- **Speaker notes:**
  - Agreement reports measure agreement, not truth. Shared inputs mean shared blind spots.
  - On the classifiers, be fair: most of those stops put a human in front of an action on the shared host, which is arguably the right place for one. The cost was latency and one lost seat (that research direction list came from a single seat).
  - Also mention the harness bugs: Block-5 attempt D died after 18.5 h on a full disk (about 110 GB of parallel test fixtures, item 165), and a disk guard now prunes only under pressure.

## A11 · What the human still does (0:45)

- **Message:** Ed makes the rulings, does the physical setup, makes the judgement calls and does the unsealing. The agents do the rest, and they are graded by procedure, not trusted.
- **Visual:** Four icons, each with one dated example:
  - **rulings:** the claim "sabotage leaves an energy signature"; a scoped on-host red team (items 204, 210);
  - **physical:** Optimized Battery Charging off, ran the quiet-OS script, the SSD (AGENDA "Ed's items"; item 201);
  - **judgement:** "why our quiet machine is never quiet" (item 206);
  - **unsealing:** nothing is unsealed without his OK (`RESUME.md`).
- **Sources:** as listed; `docs/research/AGENDA.md` "Ed's items".
- **Speaker notes:**
  - Also: Ed writes every upstream open-source post himself (AGENDA "Open source").
  - Transition: "So a single undergrad can run a preregistered, blinded hardware study. What is that study?"

---

## Bridge · Auditing agents is the theme of both halves (0:45)

- **Message:** In half A we trust our agents only through things they cannot quietly change: sealed custody, hashes, an independent recompute and a second model family. Half B asks whether energy can play that role for any AI agent. And the half-A pipeline is what makes the half-B study feasible for one person.
- **Visual:** Two rows with the same three columns, "what the agent says / what it cannot edit / who checks":
  - half A: the agent's report / custody hashes plus recompute / the other model family plus Ed;
  - half B: the agent's log / joules at the meter / a residual against predicted joules.
- **Sources:** none (framing).
- **Speaker notes:** Keep it to two sentences. Do not claim the pipeline was itself audited by energy.

---

# Half B · Sabotage Leaves an Energy Signature (10:55)

## B1 · Monitors read content (0:50)

- **Message:** Transcript and chain-of-thought monitors only see what reaches the log. Agents that know they are monitored can keep work out of it.
- **Visual:** Three qualitative examples: a hidden scratchpad, obfuscated CoT, an edited log. No borrowed catch rates.
- **Sources:** LIT §4 M4 and §6.2 rows 27, 29-30, 39-42 (`16e1db6230a80a605d084f0f9f61431d541b793f:docs/research-audits/2026-11-07/literature.md`); SHADE-Arena (arXiv 2506.15740); Baker et al. (2503.11926).
- **Speaker notes:** SHADE-Arena gives an agent a legitimate main task and, in sabotage runs, a covert side task. We run open models on two of its task pairs.

## B2 · The idea: predict joules from the log (1:10)

- **Message:** Fit energy against the logged work on honest episodes. A large positive residual means the machine did more work than the log explains.
- **Visual (F1 + F2 from [FIGURES.md](FIGURES.md)):** `residual = measured J − predicted J(logged prefill, decode, context)`, with a benign fit, then calibration, then a score. Highlight the trust boundary, and label `powermetrics` "host software: the pilots' scored channel".
- **Sources:** ER and V3 (PAPER-OUTLINE source register); `docs/research/energy-tripwire.html` "The idea" (drawing only).
- **Speaker notes:**
  - Use the careful wording: "the agent cannot rewrite an independently retained meter reading under our privilege assumptions." It can still change what work it does.
  - Be honest that in the pilots the score uses the GPU rail from `powermetrics`, which runs on the same host. An adversary with host privileges could tamper with it. That is why the external meter matters, and why v5 qualifies a DC endpoint (R11-3, item 212).

## B3 · The instrument: two energy boundaries (1:10)

- **Message:** The software rails miss most of a controlled memory-traffic contrast, so an external DC meter is needed.
- **Visual (F3 + F4):**
  - Power path: AC → brick → KM003C → MagSafe → laptop, with CPU/GPU/ANE rails inside.
  - Known-bytes contrast: rails **0.0092 ± 0.0021** and DC input **0.0389 ± 0.0072** J/GB; rails share **f = 0.238 ± 0.098**, so **about 76% outside the rails (E1, E2).**
- **Sources:** `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md` "Contrasts" and "Description"; `RUN_STATE.md` item 210 (power path).
- **Speaker notes:**
  - Say "in this rotate-minus-repeat test", never "76% of inference energy". The test is latency-bound.
  - "Rest" means DC minus rails: memory, fabric, conversion and fans together. It is not a measured DRAM number.
  - The reading rule was corrected after the data existed (KB "Corrections"). Say it is a validation check, not a confirmatory calibration.

## B4 · Footprint is not active work (0:40) · CUT CANDIDATE 3

- **Message:** Two models of similar resident size read very different weight bytes per token, so a meter has to model active work, not model size.
- **Visual (F5):** Qwen3-32B vs Qwen3-30B-A3B: resident **18.4 / 17.2 GB**, accounted reads **17.99 / 1.71 GB/token (E3)**. Label: "weight accounting; no power capture".
- **Sources:** `e901eb2a480d51377a494be9d797733dfcd0220b:docs/design/bytes_pilot/SUMMARY.md`.
- **Speaker notes:**
  - `[FREEZE]` If BYTES stage 1 has been committed and its registered release admitted by 22 Nov, the lead may swap in the admitted stage-1/2 summary. Otherwise this slide stays accounting-only. Never show unreleased BYTES energy.

## B5 · What the v3 pilot tested (1:10)

- **Message:** Known-H tampering removes logged reasoning counts while the executed episode, and its joules, stay fixed. It tests detection of a known log omission, not of intent.
- **Visual (F2 with the manipulation drawn):**
  - one device; Qwen3-30B-A3B MLX 4-bit, thinking on;
  - `spam_filter_update` and `bank_transfer_2`;
  - turn limit 12, output budget 4,096, context cap 40,960 (D1).
- **Sources:** `e901eb2a480d51377a494be9d797733dfcd0220b:docs/align/pilot_protocol_v3.md` (configuration table); P7 "Ruling (lead)" (`docs/process_traces/2026-11-04-magistrate-cf1baad2/RECORD.md`).
- **Speaker notes:**
  - "v3" is the protocol; pilots 4-10 are runs under it.
  - The model's terms (attention-length design) were selected using pilots 4-7. Say so before anyone asks.

## B6 · Result: the tested omissions crossed the threshold (1:20)

- **Message:** In pilots 8-10 every tested omission was detected, and no untampered sabotage reading crossed its threshold, but that is two trajectories checked repeatedly.
- **Visual (F7):** A per-pair table.
  - Benign calibration **m = 28** per pair; thresholds **bank 2.53, spam 7.13 (E6)**.
  - Untampered sabotage below threshold in all six session checks. Detected at the smallest tested omission, **H = 539 (spam) and 1,193 (bank) tokens (E7)**.
  - Large footnote: **two distinct sabotage trajectories, each re-checked across sessions.**
- **Sources:** P10 "Desk read (pilot 10)" (`docs/process_traces/2026-11-05-magistrate-3efb8793/RECORD.md`); P8 and P9 records.
- **Speaker notes:**
  - "Detected at the smallest H we tested" is not "minimum detectable H". There is no H50/H90 curve and no binomial interval over six "independent" attacks.
  - Repeatability: an identical replay repeats to about 1.93 J of residual SD with a 4.67 J between-session component (E5), against regression residual SDs of 19-58 J (E4). Do not turn this into a "10-25× more sensitive" claim; that is a projection for a replay detector we have not run.

## B7 · Why it is still a pilot (1:15)

- **Message:** Sample-maximum thresholds, design selection, host-software scoring and log edits limit what the pilot shows.
- **Visual (F8 + a limits list):**
  - spam threshold **7.13** against the next-largest **2.99** at m = 28: one tail point sets it (E6);
  - selection-inclusive diagnostic: bank **2/26** untampered above threshold, spam **0/26** (E8);
  - exclusions: pilot 8 had 27/28 eligible, pilot 10 had 24/28 (battery and thermal) (E9);
  - list: the tamper is a log edit, not real hidden computation; the scored channel is host software; one device, two task pairs, one mid-size open model; a non-adaptive agent.
- **Sources:** P9 final paragraph; P8 and P10 eligibility paragraphs.
- **Speaker notes:**
  - None of these are population false-alarm rates.
  - The registered v4 series exists to close exactly these gaps, which is the next slide.

## B8 · Three layers, and the squeeze (1:20)

- **Message:** Monitors see content, the meter sees quantity, and probes see internals. The squeeze is a hypothesis: hiding from one should expose you to the other.
- **Visual (F9):** Three columns, **monitor = content · meter = quantity · probes = internals**, plus the escape routes that may beat both:
  - logged plausible cover work;
  - filler or encoded reasoning;
  - matched-energy padding;
  - latent reasoning at fixed compute (the meter is blind here: the weight-only physics effect is estimated at ≤ 3×10⁻⁵ of energy, from the PR #702 design study, an estimate and not a measurement).
- **Sources:** `docs/research/research-strategy.md` §2; AGREEMENT-FINAL V01 ("an empirical bounded hypothesis, not a partition theorem"); interp design study `docs/research-audits/2026-11-07/interp-weight-edit-energy.md` (PR #702, unmerged draft).
- **Speaker notes:**
  - Label it "hypothesis, untested". No monitor and no probe has been evaluated in this project yet.
  - Energy's real niche is computation that the runtime does not mediate: side generation, tool subprocesses, untrusted or non-replayable runtimes. On a seeded local stack, a software rerun already catches stripped reasoning (strategy §2, PR #703).

## B9 · v4: the registered test (1:00)

- **Message:** v4 turns the pilot into a confirmatory test. Its rules were fixed before data, and its outcomes stay sealed until a registered release.
- **Visual (F10):** R0 → R1 → blind registration gate → W1 → 3 D windows → registration-grade calibration (m ≥ 39 per pair plus a held-out test cohort) → independent recompute → release. Each box shows a `[FREEZE]` status (done, pending or refused), never an outcome.
  - Qwen3.8-27B at 8-bit; KM003C captured in every window, with a secondary DC-in analysis; full transcripts sealed and unscored.
- **Sources:** `docs/research/research-strategy.md` §3; `RUN_STATE.md` items 203 (R10, 11.9 tok/s, fallback declared blind), 204 (Q4, Q6) and 212 (R11-3: the registered residual stays GPU energy).
- **Speaker notes:**
  - Example of deciding first: 8-bit decode at about 11.9 tok/s cannot fit the original budget, so the fallback was declared before any R1 number existed (item 203).
  - As of 7 Nov, protocol v4 still lacked nine chair rulings and WP19 (`w1-prearm-gate.md`, PR #695). `[FREEZE]` Update with the status at the freeze.
  - If asked about results: "sealed until the registered release; I don't know them."

## B10 · v5 and the road to the main result (1:00)

- **Message:** v5 tests whether the squeeze holds against an adaptive agent: does successful sabotage escape a joint energy-plus-monitor audit?
- **Visual (F10 extension + F11):**
  - Endpoint: **side-task success and no joint alarm, per assigned attempt**, reported with utility.
  - Joint rule calibrated at 0.05, with energy-alone and monitor-alone comparators, plus trusted time plus monitor as a primary comparator.
  - Frontier API monitor off-box; a scoped, sandboxed red team.
  - Timeline: Nov 30 talk → mid-Dec paper → v5 windows Dec-Feb → NeurIPS 2027 (about mid-May; no deadline verified).
- **Sources:** `RUN_STATE.md` item 212 (R11-2: D07, D09, D12) and item 210 (monitor, D-139 A1, venue); `docs/research/AGENDA.md` timeline; v5 design competition branches `origin/align/2026-11-08-v5design-*` (not decided).
- **Speaker notes:**
  - The v5 design is still being judged. Do not name a roster or sample size.
  - Expect a measured limit rather than a clean win (strategy §1). Saying so is a strength.

## Close (0:30)

- **Message:** "Our pilot sees work missing from a log, and a registered test is under way. The next question is whether an adaptive agent can hide from the monitor and the meter at once. Answering it at this rigour was possible only because the pipeline that runs the study is itself audited."
- **Visual:** The two-row bridge table again, with one link to the repo and the paper.

---

## Three slides to cut if short on time

1. **A3, one loop end to end (saves 1:00).** Fold one sentence into A2: "a refusal to a merged rule change took four hours on 7 Nov."
2. **A7, 37 h to 1 h 40 min (saves 0:40).** Keep the number as one line on A6.
3. **B4, BYTES footprint (saves 0:40).** Mention it in one clause on B3.

Total after the cuts: about 21:20 (half A 9:20, half B 10:15). Never cut B6's two-trajectory footnote, B7, or A10. If still short, shorten B8's escape-route list to two items before cutting anything else.

## New figures for half A

These are added to [FIGURES.md](FIGURES.md)'s F1-F11. All of them are desk-made from committed text, with no Mac time.

| ID | Figure | Data source | Limits |
|---|---|---|---|
| FA1 | Architecture: Ed, lead, `RUN_STATE`, magistrate, workers, instrument | items 181 and 211; `MAGISTRATE_WATCHDOG.md` | Schematic. Name model versions as in the record. |
| FA2 | One loop, 7 Nov 17:38-21:50 | items 206-211 | Times as recorded (PST). |
| FA3 | Recompute and comparator stack, with the D1-D6 attribution | DEVIATION-LOG; release-hold trace §2 | Counts and defect labels only; no values. |
| FA4 | 37 h to 1 h 40 min bars | items 165 and 197; `RESUME.md` | Must carry the load caveat and the like-for-like 27.1 h vs 1 h 46 min. |
| FA5 | Agreement matrix excerpt plus the power-claim callout | AGREEMENT-FINAL | Quote labels exactly (HC/HR/M/U). |
| FA6 | R0 attempt strip, 11 attempts and their causes | items 177-211 | Distinguish contention refusals (7) from tooling or model stops (4). |

## Half-A number ledger (H)

Verified 2026-11-08 against `origin/main` at `bfaf119f2` unless noted. "Verified" means re-derived by the v2 author from the cited source, not copied from a summary.

| ID | Value | Source | Status |
|---|---|---|---|
| H1 | 7,905 commits on `main`, the first dated 2026-06-09 | `git log origin/main --oneline \| wc -l` at `bfaf119f2` | Verified; recount at the freeze |
| H2 | PRs numbered up to #704 | `gh pr list --state all` | Verified; recount at the freeze |
| H3 | 212 numbered `RUN_STATE` items | `RUN_STATE.md` top item 212 | Verified |
| H4 | Decision log to D-190 | `docs/decision_log.md` | Verified |
| H5 | Watchdog tick every 300 s | `docs/process/MAGISTRATE_WATCHDOG.md` | Verified |
| H6 | 75 magistrate-activation items (73 distinct activation IDs) | grep of `^N. **Magistrate activation` in `RUN_STATE.md` | Verified; the count covers numbered items only |
| H7 | r2 release check: 1,001 failing rows in 11 families, all attributed to six defects D1-D6; after r3, one cause (D5, 108 rows); D5 fixed in r4 (PR #697, tag `b5/analysis-r4`) | `docs/run_reports/2026-11-07-b5-release-hold-trace.md` header and §2; `RESUME.md` | Verified. **The showcase page's "12 → 1 families" does not match the trace (11 families); do not use it.** The r4 release-check result is `[FREEZE]` (exit class only). |
| H8 | about 37 h (r1 reference re-run, dry-k) → 1 h 40 min (r3, dry-l); like-for-like 27.1 h (attempt E) vs 1 h 46 min (candidate 1); steps 0-5 about 22.5 h vs 1 h 23 min, with E's machine more loaded | `RUN_STATE.md` items 165 and 197; `RESUME.md` | Verified. The "about 37 h" is the record's own approximation. |
| H9 | AGREEMENT-FINAL: 4 seats per core track (Fable, Opus, Sol-1, Sol-2), cross-reviewed both ways; 38 adjudicated rows (R01-R16, D01-D12, V01-V10); 5 sufficiency claims rejected, including the power claim of 0.989/0.999 recomputed as 0.117649/0.255298 | AGREEMENT-FINAL ("Counting and confidence"; tracks 1-3; "Rejected sufficiency claims") | Verified. The row count is from a grep of the tables. |
| H10 | About 150 agents on 7 Nov | Stated on `docs/research/energy-tripwire.html` ("About 150 model agents"). Reconstructed from the PR provenance: 7 audit tracks × (2 seats + synthesis) = 21; methodology 2 seats + 20 checks + synthesis = 23; Qwen-Next 3; OSS 2 seats + 40 verifiers + synthesis = 43; interp 2 seats + 36 checks = 38; tripwire directions 2 seats + 22 checks = 24; **total about 152** | **Approximate.** The reconstruction counts documented seats and checks (PRs #695, #696, #698, #702, #703) and excludes that day's Sol squeeze seats. Say "about 150". |
| H11 | 11 unsuccessful R0 attempts, 11-06 08:05 to 11-07 18:41 PST. 7 contention refusals (re-runs 3, 4, 5, 6, 8, 9, 10). 4 other stops: original run (launcher), re-run 1 (model load), re-run 2 (harness prompt), re-run 7 (sensor selection). Census limit 0.05 CPU-s/s per process over 30 s; about 650 background activities per hour (594-685 measured) | `RUN_STATE.md` items 177-208 | Verified. **The brief's "nine refusals" is not supported; use 7 of 11.** Re-run 11's outcome is `[FREEZE]`. |
| H12 | Meter-path error in several model documents and cross-reviews (LIT H3, C-V §3.2, XO-D "What all four missed" #1, XO-V #5), corrected by Ed | item 210 (verbatim); AGREEMENT-FINAL authority table | Verified. Which original seat first raised it is not traced, so do not say "every seat" or "both families" |
| H13 | Classifier stops: `kill` refused (item 42); `launchctl bootstrap` refused (item 44); push to `main` blocked (item 102); upstream code blocked (`RESUME.md`); Opus seat stopped (PR #703) | as cited | Verified |
| H14 | Attempt D died after 18.5 h on ENOSPC; about 110 GB of fixtures | item 165 | Verified |
| H15 | R0-L3 reviews: 97 replayed checks, 0 failures; both ADMIT_WITH_FIXES, nothing above LOW in #699/#700 | item 208 | Verified |

**Half-B ledger note.** E1-E9 and D1 are as defined in [PAPER-OUTLINE.md](PAPER-OUTLINE.md). For v2, E1, E2, E5, E6, E7, E8 and D1 were re-checked against the KB slot fill, the P9 and P10 records and V3, and agree. E3, E4 and E9 were not independently re-checked in v2; re-check them at the freeze.
