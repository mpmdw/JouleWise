# RULES: every rule that gates, limits, schedules or delays work

Mythos 5.2 process audit, 2026-11-17. Companion files: `CUT.md`, `STRUCTURE.md`, `MIGRATION.md`.

## 0. Scope, sources and limits

**Sources and how they are cited.**

| Tag | File | Revision |
|---|---|---|
| `RS:n` | `RUN_STATE.md`, line n | `origin/main` at `2e07ef699` (item 416) |
| `RLD:n` | `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`, line n | `origin/audit/2026-11-10-fable` at `aeadb9122` (RL-177) |
| `MP:n` | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, line n | `origin/main` |
| `PL:n` | `docs/process/PIPELINE.md`, line n | `origin/main` |
| other `path:n` | as named | `origin/main` unless a ref is given |

**Classes.**
- **PHYSICS**: a physical limit: memory, thermals, power or meter capability, disk, or contention with a counted span or with the measurement itself.
- **VALIDITY**: protects the science and is needed for the paper: blinding, pre-registration, custody, measurement independence.
- **SAFETY**: prevents data loss or an irreversible mistake.
- **PACING**: everything else: calendar and count quotas, waits for a person or for the Air, review counts, ceremony, and rules whose trigger can no longer occur.

A rule can be in the right class and still be built far past its job. Those rows carry "over-built" and appear in `CUT.md` section 2.

**Limits of this inventory.**
- I read in full: the magistrate prompt, PIPELINE.md, items 346 to 348, 374 to 376, 384 to 388, 395, 396, 399, 402 to 416 of RUN_STATE, RL-149 §2.3, §2.4, §2.8 and §2.9, RL-155a, RL-171, RL-172 and RL-173, and the operational sections of RL-174 and RL-175. Three extraction passes (seats I briefed, working from the same revisions) read items 346, 372, 394, 397, 398 and 406 line by line, the code on main and on the measurement pins, and the review and merge documents. Their full tables are in `appendix/`; sections 3.3, 3.7 and 3.10 group them, and section 5 lists the cites I checked.
- The GPT 6.2 Astra drift register (`/Volumes/JW-EXT/scratch/astra-drift-audit/REGISTER.md`) lists 715 clauses at clause grain. This file is at rule grain: one row for a rule however many items repeat it. Section 5 maps the two. Rulings before RL-143 are covered only where a later ruling or a live item still cites them.
- Costs are from the record where the record shows them: launch and close times in the magistrate's items, and two earlier hour ledgers. "n.r." means the record does not show a cost. A cost is the time the rule was the binding reason, so costs of rules that bound together are shared and must not be added.
- No custody, energy, power, meter, transcript, slot, hazard, sealed or restricted file was opened. Receipt and leg values quoted below are the ones the magistrate printed in RUN_STATE.

---

## 1. Where the MBP hours went, 10 to 17 November

### 1.1 Sun 15 to Tue 17 November (72 h), from the magistrate's launch and close items

Every launch and close in this window has a magistrate item (RS:1047 to RS:8157). Closes are recorded to the second; most launches are, and five are given to the minute (marked "~" in the items), so each gap below is good to about two minutes.

| Use of the host | Hours | Share |
|---|---|---|
| Counted or product-bearing spans (dev-01-s04, hp-01 ×3, dev-02 ×2, dev-03 ×2, dev-04 ×2, F2 p01) | 26.4 | 37 % |
| F0 (ten runs of about 1 h 59 min; a diagnostic that "adopts nothing", RS:5813) | 19.8 | 27 % |
| Idle | 25.7 | 36 % |

The 25.7 idle hours by binding reason:

| Reason the host was idle | Gaps | Hours | Rule rows |
|---|---|---|---|
| F0 was the only eligible work and its 4 h spacing had not elapsed | Sun 15:15-17:17, Sun 19:16-21:18, Mon 13:34-15:34, Tue 08:22-10:25, Tue 12:24-14:29 | 10.2 | F0-06 |
| Evening tail: no F0 allowed (spacing, the 22:40 window end, the three-a-day cap) and the issued counted span could not start before 00:00 | Sun 23:18-00:00, Mon 20:14-00:00, Tue 21:06-00:00 | 7.4 | F0-06, F0-07, D-01 |
| F0 held by a prose hold while the lead packed the disk | Mon 15:34-18:15 | 2.7 | C-09 |
| The 30-minute wait for the Air's copy marker before the MBP made its own copy | four closes (Sun 12:43, Mon 03:06, Tue 02:51, Tue 05:51) | 2.2 | C-02 |
| Close to next launch when nothing else bound (Check by the magistrate, the lead issuing the next item, the 300 s or 1,200 s gap) | seven closes, 14 to 25 min each | 2.3 | M-08, I-01, F0-13 |
| Waiting for the lead's one-time waiver of the F0 cap | Tue 18:34-19:07 | 0.55 | F0-06 |
| 1,200 s gap after F0 before a counted span | Mon 07:32-07:52 | 0.33 | F0-13 |
| Disk floor (55 GiB against 60), cured by evicting uploaded archives | Mon 00:00-00:03 | 0.05 | X-03 |

Two things the idle figure does not show:

- **Counted spans that were issued and ready sat behind the calendar for 32.5 h.** dev-02-s03 (issued Sun 15:42, ran Mon 00:02), dev-04-s01 (ready from dev-03-s02's close at Mon 11:16, ran Tue 00:00) and dev-05-s01 (issued Tue 12:32, arms Wed 00:00) each waited for their t0-date (row D-01). In those hours the host ran F0 for about 16 h, F2 for 1.75 h and idled for about 15 h. The date rule is a validity rule; the waste is that nothing with a product was eligible to fill the hours.
- **One priority inversion.** F0 run 4 launched Mon 05:32:36. The dev-03 pilot's hand-read was signed at 05:38:41. The counted remainder then waited for F0 and its gap until 07:51:38: 2 h 13 min of counted work displaced by a diagnostic (rows H-01, F0-10).

### 1.2 Wed 11 to Sat 14 November (96 h), from the Mythos throughput ledger

`/Volumes/JW-EXT/scratch/mythos-throughput/ledger.out` (86 intervals; 66 h with both ends recorded).

| Bucket | Hours | Rule rows |
|---|---|---|
| Any capture running | 39.7 | |
| of which counted campaign legs | 2.4 | |
| of which rehearsal sessions that gave no slots | 21.8 | (an engineering failure, not a rule) |
| of which smokes forced by a change to measured bytes, with their soaks | 9.9 | S-06 |
| Waiting on builds, kit checks and reviews | 18.6 | R-01 to R-09, R-12, I-07, I-13 |
| Waiting on CI or a merge | 7.4 | R-10 |
| Waiting on a research-lead ruling or Ed | 5.4 | G-02 |
| Waiting on the lead to issue or re-issue an item | 5.5 | I-01 |
| Clock rules (11:45-13:15 window, 13:20 earliest start, calendar day) | 4.9 | X-01, D-01 |
| Close interval and poll latency | 3.4 | F0-13, M-08 |
| Other compute on the MBP (BYTES twin, fixtures, custody copy) | 11.0 | A-03 |

### 1.3 Tue 10 November (24 h), from items 249 to 262

R1 had refused at 01:17 on 8 November and nobody was told for 60 h (`/Volumes/JW-EXT/scratch/throughput-plan/REPORT.md`). On the 10th: stranded until 13:21 (RS:12295); re-armed, refused at 13:49 and unnoticed until 17:30 (RS:12278); re-armed 17:26, refused 19:05 (RS:12249); a fix, a research-lead review and a re-arm at 20:53 (RS:12171). About 20.9 h idle, 3.1 h measuring. No rule caused the refusals; the cost came from nobody being told and from each re-arm waiting for a person (rows G-03, I-05, M-09).

### 1.4 The eight days together

| | Hours | Share of 192 h |
|---|---|---|
| Idle or waiting | about 92 | 48 % |
| Counted or product-bearing capture | about 29 | 15 % |
| F0 and other diagnostics, smokes, rehearsals that gave no slots, other compute | about 71 | 37 % |

The first three days and the last three have different causes. Through the 14th the host waited for people and reviews. From the 15th the queue ran by itself, and the host waited for pacing rules on its only filler and for the calendar.

---

## 2. Where the lead and agent hours went

The record does not log lead or seat hours. It does give volumes and elapsed times, from RUN_STATE, the scratch volume and the PR history (`appendix/review-rules.md`, Part 2).

| Indicator, 10 to 17 November | Value | Source |
|---|---|---|
| RUN_STATE items written | 169 (91 by the lead, 78 by the magistrate), 1.39 MB of text | RS:1047 to RS:12330 |
| Size of one counted-span item | 49 to 65 KB. Item 394 is 532 lines, 444 of them shell, with 93 distinct gates | RS:1889-2420; `appendix/item-gates.md` |
| What RL-149 specified for a per-span item | "the ten-line template" | RLD:12714 |
| Research-lead rulings | RL-143 to RL-177 in five days (13 to 17 November), about 8,200 lines | RLD:10150-18375 |
| Agent seat directories created on the Air's SSD | at least 128 in six days (33 on the 14th, 34 on the 15th, 32 on the 17th); cloud seats are not counted | `/Volumes/JW-EXT/scratch`, directory names only |
| PRs opened or merged | 94: 66 merged, 23 open, 5 closed | GitHub |
| Open to merge, for PRs that merged | median 2.2 h; 90th percentile 12.7 h; longest 24.5 h; none states more than 3 rounds | GitHub |
| Longest stretch with no merge | 60.5 h (15 Nov 12:06 UTC to 18 Nov 00:35 UTC), with nine PRs opened in it and eight still open | GitHub |
| Open PRs now | 56, of which 49 drafts; median age 10 days | GitHub |
| The queue-controller stack | #800 on #799 on #794 on #788 on #775: none merged, none targets main. #800 has been open 68 h, through 7 gates and rounds to 10; its last four gates found 1, 1, 3 and 2 HIGH. #795 (the interim look's fit): 72 h, 60 commits, round 10 | PR bodies |
| A pull-request CI run that finishes | median 61.7 min, 90th percentile 120.9 min; 29 % fail; 109 of 198 runs were cancelled by a newer push | last 300 `ci` runs |
| Direct pushes to main against PR merges | 196 to 47 since 10 November; almost all the pushes are RUN_STATE records | `git log --first-parent` |

**Reading.** Work that fits in one PR merges in a couple of hours. The lead's and the seats' time went to two things that do not converge: (1) the per-span items, each a hand-edited program of about 450 lines that a builder drafts, a Sol seat reviews and a Mythos seat re-checks; and (2) the five-deep stack under #800, where every round goes to a fresh reader, rulings add scope mid-review, and one PR's refusal holds its neighbours. Both exist to enforce the rules in section 3. The first disappears when gates are functions (`STRUCTURE.md` a). The second disappears when the rules it compiles are cut (`CUT.md` CUT-30).

---

## 3. The inventory

Columns: **Id**; **Source**; **Rule** (what it says); **Blocks**; **Stated reason**; **Class**; **Cost 11-10..11-17** (MBP hours; lead or agent time where the record shows it).

### 3.1 The standing filler, F0 (RUN_STATE item 346)

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| F0-01 | RS:5827 | F0 runs only at commit `b2e01464d`; the magistrate re-checks a 17-hash table, the tree, the Mac-check line and, once per host, six test modules | F0 after any merge to the W1 line | The pin is the registered Part C path (RL-165 §3) | VALIDITY, over-built: the launcher verifies its own frozen sources (`verify_r1_executed_sources`); the prose table duplicates it | Lead re-pinned and re-issued the item twice on 11-15; MBP n.r. |
| F0-02 | RS:5828 | The item is void when the W1-line head moves and expires 7 days after issue; the lead re-issues it | All F0 from Sun 22 Nov 11:51 unless the lead renews (RS:1597, item 402 §6) | "This item names a sha, so it is re-issued there" | PACING (expiry by age; needs a person) | None yet. It is the next scheduled filler outage |
| F0-03 | RS:5829-5833 | F0 launches only on one of three triggers; NO_STAGED means no staged item can launch within 2 h 30 min of a close; F0 is the last rung | F0 while a staged item might become launchable within 2 h 30 min | Order of the ladder (RL-165 §1-§4) | PHYSICS (contention with a counted span), crude: a fixed look-ahead in place of a computed fit | n.r. |
| F0-04 | RS:5834; RLD:17288 | From the record that a v4 session is READY, nothing of lower priority arms, F0 included | Every filler once R1 is READY, including when R1 cannot arm | The session takes the next clean close (RL-172 (f)) | PACING as written: a priority rule with no release when the session's arm refuses | 0 in the window (READY takes effect at dev-05-s02's launch). A refused session with nothing else allowed to run is how the host stood idle for 63.7 h on 11-08 to 11-10 |
| F0-05 | RS:5835 | After a refused arm: mail the lead, wait 20 min for a reply; an unclear reply means no launch in this activation | F0 for 20 min or more after any refusal | The lead may be clearing the refusal | PACING (waits for a person) | 0 (no refusal 11-15 to 11-17) |
| F0-06 | RS:5836; RLD:14391; RLD:17172; RLD:17335 | F0 t0s at least 14,400 s apart, and at most three in a calendar day (the cap was revoked by item 415, RS:1065; the spacing stands "until the process audit rules") | F0, which is 2 h long, for 2 h after every F0 | "More than three a day is load without product" (RLD:17172) | PACING | 10.2 h as the binding reason, plus a share of the 7.4 h of evening tails, plus 0.55 h waiting for a waiver |
| F0-07 | RS:5837; RLD:17102; RLD:17126 | F0 launches only between 02:35:00 and 22:40:00: the pinned `soak_child` refuses a soak whose span would meet 02:00-02:35 | F0 for 3 h 55 min every night | The macOS daily batch (about 02:08). RL-171 calls the window "no longer a rule; what the bytes still do" (RLD:17081) | PACING in frozen code (a clock blackout already disowned) | A share of the 7.4 h of tails: 0.7 h Sun, 1.3 h Mon, 1.3 h Tue after 22:40 |
| F0-08 | RS:5838 | Launch + 12,180 s + 1,200 s must be at or before the latest legal t0 of every staged counted span due that day | F0 near a counted span's deadline | "It never costs a counted span its day" | PHYSICS (contention with a counted span). Keep the purpose; compute it from the latest feasible start (Astra finding 4) | 0 |
| F0-09 | RS:5839; RLD:17311 | No F0 after 12:00 on the restart day until the lead records the restart | F0 on that day | The restart re-phases the OS batch (RL-172 (h)) | PACING, stale: the restart was never made and RL-173 E parks it until Ed is at the machine (RLD:17498) | 0 |
| F0-10 | RS:5840 | A running F0 is never aborted; a counted span cleared meanwhile arms 20 min after F0 closes | A counted span for up to 2 h 20 min | Aborting leaves host state unknown | SAFETY (keep "never abort"). The cost comes from the filler being 2 h long | 2 h 13 min of counted work displaced on Mon 16 |
| F0-11 | RS:5841 | After each run: a Check item, mail to Ed and the lead, a line-by-line comparison with the previous run; any differing line goes to the research lead | Magistrate time at every F0 close | The lead reads each verdict under RL-164 §3 | PACING (ceremony). Ten runs gave ten identical verdicts (RS:1047, RS:1544, RS:2954 and earlier) | About 10 to 20 min of magistrate time per run; ten mails to Ed |
| F0-12 | RS:5813; RS:5872 | One run per activation; the launch is the magistrate's last action; no agent, SSH or other job until the fence is gone | Everything else on the host during a run | An agent beside the measurement contaminates it | PHYSICS | Necessary |
| F0-13 | RS:5874; RLD:17153-17155; RLD:17268-17272 | After the latest close of anything: wait at least 300 s if it was a campaign span, 1,200 s if it was F0, F2, a session or W1 | Every launch | The successor needs a settled start; RL-172 (d) keeps 20 min because "nothing on record tests a 2 min gap, and 0.3 °C has no basis" (RLD:17270) | Claimed PHYSICS with no measured quantity, over-built: every span starts with its own 1,800 s soak and G0 gate (RLD:17154); Astra's finding 9 shows elapsed cooling does not explain the one F0 excursion (RLD:17841) | About 15 min at each of 13 filler closes, 3 h, mostly inside F0-06's waits |
| F0-14 | RS:5875 | The complete eligibility check runs twice, in "Start and check" and again in "Run" | Seconds | State may change between the two | SAFETY, over-built | Seconds; it doubles the shell |
| F0-15 | RS:5813 (Conditions, Blinding) | From the verdict file print only `evaluation`, N_chunk and T_dead; open no bundle, transcript, energy or meter file | Reading outcomes | Blinding | VALIDITY | Necessary |
| F0-16 | RS:5813 (Conditions) | A High Power marker present, an unproven restore or an unproven process group holds F0 | F0 | Host state is unknown | SAFETY | Necessary |

### 3.2 Close, copy, offload and retention

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| C-01 | RLD:17153; RLD:17458; RS:5779 | A hash-verified off-host copy of the last campaign close must exist before the next arm; "a failed or unverified offload holds the next arm. F0 does not run past it either" | Every launch after a campaign close | The data must exist off the MBP | SAFETY, over-built as a gate: the original stays on the MBP (C-07), so the exposure is one span of data for the minutes of an upload | About 5 min per close when the MBP copies at once (RS:5765: 13:12:48 to 13:14:28 plus upload confirmation) |
| C-02 | RS:5769 (item 348); RS:1872 (item 395 A) | With the Air "resumed", the lead copies; the MBP falls back only 30 min after the close | Every launch after a campaign close for up to 30 min | Ed, 11-15: the MBP should take over Air jobs only when the Air is away | PACING (waits for the Air). Suspended "until R1 arms" by item 409 (RS:1176) | 2.2 h over four closes |
| C-03 | RS:1872 | The copy owner at each close is chosen from the latest lead record of the Air's state (paused or resumed) | The close, on reading several items in order | Removes the 30-min wait when the Air is known to be away | PACING (state kept in prose; eight Air-state items on 11-17: RS:3008, 2965, 2963, 1597, 1595, 1575, 1186, 1176) | Lead and magistrate reading time; n.r. |
| C-04 | RS:5809; RS:5779 (pointer) | Poll the provider every 2 min for up to 90 min; if the upload cannot be confirmed write no marker, run nothing else, mail Ed and the lead | All measurement while the cloud provider is slow or down | An unconfirmed copy is not a copy | SAFETY, over-built: a provider outage stops the instrument | 0 so far; unbounded when it happens. 136 uploads timed out on the Air on 11-17 (RS:3017) |
| C-05 | RLD:17450 | A second copy of the encryption key exists off the MBP | Counting the offload at all, after 24 h | The cloud copy is useless if the MBP dies with the only key | SAFETY | Necessary; one-time |
| C-06 | RLD:17452 | The upload ends before the next soak starts; a sync daemon is the kind of program quiet is defined against | The next soak | Network and disk activity beside a measurement | PHYSICS (contention) | Necessary |
| C-07 | RLD:17456; RS:1859; RS:1628 | The MBP keeps its originals until a second verified location holds them; no step may pack, move or delete a dev-01 to dev-05 output until the lead records "interim look complete" | Deleting | The interim look reads the raw directories | SAFETY and VALIDITY | Necessary |
| C-08 | RLD:17621 | Each arm reads that no iCloud transfer is pending under the JouleWise folders | The arm | A pending transfer will run during the span | PHYSICS (contention) | Seconds |
| C-09 | RS:3041 (item 374); RS:3033 (item 376) | No F0 from Mon 13:42 until the lead records "offload window closed" or 23:30 | F0 for the length of the lead's disk packing | The packer is a heavy process | PHYSICS (contention) for the 4 h 14 min the packer ran; the form, a prose hold lifted by a second item, is PACING | 2.7 h beyond the spacing wait. The magistrate found the hold at its pre-launch re-read (RS:3039) |
| C-10 | RLD:17612 | From the freeze-2 commit to qual-03's close nobody changes a host hygiene setting | Host-setting changes | Qualification, ctl-01 and W1 run on one host state | VALIDITY | Necessary |
| C-11 | contract §1.2, `/Volumes/JW-EXT/scratch/mythos-cluster-contract/CONTRACT.md:51-66` | A span passes through 12 states and 15 durable artifacts (signed bundle commit, verdict ref, wrapped key, SSD receipt, retirement record, retention holds) before its raw directory may go | Merging #799, #800, #804, #807 | Each artifact answers a review finding | SAFETY, over-built for the job of "copy it, keep the original" | Four PRs unmerged; #800 at round 10 |

### 3.3 Counted spans: issuing, and the gates inside one item

The full line-by-line table is `appendix/item-gates.md`. It finds **93 distinct gates in item 394** (dev-05-s02), 63 in item 406 (F2 piece 1), 54 in item 346 (F0), 27 in item 397 (R1 READY) and 33 in item 398 (the slot session): 270 rows. In item 394, 41 gates end in STOP, WAIT or VOID; 39 are shell that reads host state, 9 are shell that tests a value the magistrate typed in, 30 are prose only, and 10 involve the pinned code. Across the five items, 44 rows are shell tests of a hand-typed value. The rows below group them.

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| I-01 | RLD:12714; RS:1889-2420 | One RUN_STATE item per span, issued by the lead. RL-149 specified "the ten-line template"; item 394 is 532 lines with 444 lines of shell | A span until a person fills and issues its item | RL-149 §2.9 item 6.6 | PACING | 5.5 h of MBP wait on issue and re-issue on 11-11 to 11-14; a builder, a Sol review and a Mythos delta seat per item (I-13) |
| I-02 | RLD:17483; RS:2016-2022 | An item expires 24 h after issue. The check runs three times in one launch (RS:2181, 2256, 2263) | A ready span whose date window is still open | RL-173 D.5, "the interim until #800 is admitted" (RS:1899) | PACING (expiry by age). For item 394: issued Tue 12:32:46, window opens Wed 00:00, the pin refuses 10:50 to 13:15, the item dies Wed 12:32:46. Its usable life is 10 h 50 min. Item 397 makes R1's READY record void if 394 goes void (RS:1759) | 0 so far. One slip of seven hours on Wed loses dev-05's date and R1's READY together |
| I-03 | RLD:17479; RS:1899 | At most three counted spans issued ahead, plus the standing F0 | Stocking the queue; the lead must be present daily | RL-173 D.1 | PACING | dev-05 could not be issued on 11-17 morning with the Air paused (RS:3000) |
| I-04 | RLD:17480; RS:2023-2084 | Each item names its predecessor. No receipt yet: WAIT. A predecessor that did not close clean, had two legs over 1.5 times budget, or three contaminated redos: this item is VOID "and is not skipped" | The next span after any non-clean close, until the lead writes a new item | RL-173 D.2 | VALIDITY inside a block (the next span builds on this one). PACING across blocks | 0 (every span closed clean) |
| I-05 | RS:1895; RS:2413 | "Any failed line of Start and check, any launch refusal ...: NOTHING of this item launches; a later t0 needs a new item. Do not retry, do not extend." After a span that ended badly "nothing relaunches, nothing is re-run, nothing else is queued; mail the lead" | Everything after any failed check, until a person acts | None stated | PACING (waits for a person). The close-interval check is a STOP in one place and a WAIT in another in the same item (RS:2167, RS:2257) | 0 observed; this is the stranding shape of 11-08 to 11-10 |
| I-06 | RLD:12647; K11:`queue.py:252-254` | A queue expires seven days after its commit and is extended only by appending | Spans left in an old queue | RL-149 §2.8 line 3 | PACING (expiry by age). The hash pin and append-only rule are VALIDITY and stay | 0 |
| I-07 | RLD:12643; RS:1903 | Line 1: a cold seat that did not write the kit has checked it, with no open finding | A kit until a seat is run | The kit matches the ruling | VALIDITY for a new leg type; over-built for a kit of a ruled type (RLD:12718) | One Mythos seat per kit (dev-04/05: Sat 14 Nov, RS:1903) |
| I-08 | RLD:12645; RS:1921 | Line 2: the kit validates at its frozen commit and that commit's full suite is green; "one result covers every span on those bytes" | A kit | The bytes are tested | VALIDITY. In practice the suite on the campaign pin was red (9 of 12 shards) and was accepted because the red set equalled the base's (RS:1921, RL-165 §5) | Lead time arguing red-set equality; n.r. |
| I-09 | RLD:12515-12521; K11:`stops.py:27-77` | Named stops "stop the next arm". REFUSAL, restore unproven, disk and watcher down are cleared by the lead "with a line in RUN_STATE"; INSTRUMENT_FAULT and any change to host state by the research lead; LEG_OVERTIME by the lead | The whole campaign queue until a person writes a line | RL-149 §2.4 | Restore unproven: SAFETY. Disk, instrument: PHYSICS. CONTAMINATED_REDOS: VALIDITY. Watcher down: PACING. All are over-scoped: each holds every later span, not the kit that raised it | 0 on 11-15 to 11-17 |
| I-10 | RS:1930; RS:1933-1938 | Before every launch: eight test modules (201 tests) run one at a time in a fresh worktree; two fetches; a new detached worktree per span | A few minutes a launch | None stated | VALIDITY, over-built: I-08 says one result covers the bytes, and the runner re-verifies the freeze itself (X-12) | Minutes a launch |
| I-11 | RS:1940-1947; RS:2241-2259 | Seven values typed in by the magistrate at each launch (among them the prior close epoch, the kind of the last close, "host restore OK", "session READY"); item 406 has 28, item 346 has 15 | Nothing; the gates then test what was typed | Sol review findings P1-1 and P1-2 | PACING (ceremony) with a SAFETY cost: 9 of item 394's shell gates test a hand-typed value | Magistrate time; the risk of a wrong fill |
| I-12 | RS:2158-2170; RS:2264-2265; RLD:17101; RLD:17222 | The `--batch-window` argument is chosen by clock band (`02:00-02:35` from 02:35 to 10:50 and 13:15 to 18:33; `13:14-13:15` otherwise) and must still fit at Run | The launch if the clock leaves the band between check and run | Steers around X-01 in the frozen pin | PACING (a workaround for a clock rule in frozen code) | Seconds; one more way to void an item |
| I-13 | RS:1889 (heading); RS:1903 | The drafting chain for each item: a builder drafts, a Sol items review finds P1s, a Mythos delta seat checks, the lead or the magistrate fills and issues | A span until the chain finishes | Each stage caught real faults in the shell (for example the checklist-order fault in six qualification drafts, Astra window-schedule finding 2) | PACING (review count). The faults are in the per-item shell the chain exists to check | 11 campaign items of 49 to 65 KB in three days; 128 or more seat directories in six days |
| I-14 | RS:2276; RS:2402-2411 | The arm record: 24 named values written twice (in the RUN_STATE item and a custody file). The Check report: nine groups, by mail and as an item | The next launch for the time it takes | Evidence | PACING (ceremony); see M-08 | Inside M-08's 14 to 25 min |
| I-15 | RS:1910; RS:1924 | "Do not run `cadence_queue.py next` or `checklist`": `not_before` and the k+2 rule are not enforced in code at the pin, so the item's shell carries them | Use of the decision library that exists at the pin | Mythos dev-04/05 finding F4 | PACING (historical): a decision function was built, frozen with gaps, then forbidden | Lead and seat time re-implementing it as shell per item |
| I-16 | RS:1908; RS:2258-2261 | The R1 reservation: if a v4 session is READY this span cedes | A counted span once R1 is READY | RL-172 (f) | VALIDITY (priority of a registered session). See F0-04 for the case where the session cannot arm | 0 |

### 3.4 The day design and qualification

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| D-01 | RLD:17228-17233; RLD:12479 | The unit of independence is the calendar day, the local date of a span's t0. No date holds more than 12 mixed-size development legs or 24 development legs; qualification dates are disjoint from development dates; a span that misses its date is re-dated by the lead and never doubles up | A counted span until its date begins; a second mixed block on a date | "Every leave-one-out error is leave-one-day-out. More blocks in a day never make more days" | VALIDITY (measurement independence), paper-bound | 32.5 h in which issued counted spans waited for their date. The ruling accepted this because "the machine has nothing else READY on those days" (RLD:17229) |
| D-02 | RS:2102; RS:2128; RS:2158 | Each counted item's shell counts the day's legs from receipts and stops on an unreadable receipt; it carries its own launch bands (earliest and latest epoch, and "none 10:50:01-13:14:59") | The arm | D-01, enforced "until the queue enforces dates" (RLD:17239) | VALIDITY, implemented as per-item shell | Lead and seat time per item (section 3.3) |
| D-03 | RLD:17576 | Qualification runs on three t0-dates, one block each; at most two blocks and 24 legs on a date, block starts 10 h apart | Qualification pace | Fewer than three pair-days prints `not_evaluable` | VALIDITY, paper-bound | Future: three dates |
| D-04 | RLD:17822; RLD:17825 | A qualification span does not arm while the predicted OS batch lies between its soak end and its expected close; it arms at the predicted batch start plus 27 min | Qualification spans for about 2 h 35 min a date | Each ratio has three pairs and none is re-run to mend one; "it matches the v4 population" | VALIDITY, paper-bound. A clock rule read from the boot time. Its hours are to be filled, not waited (RLD:17825) | Future: 2 h 35 min a date unless a filler runs |
| D-05 | RLD:17807-17813 | A half-run qualification block: the missing span runs on the next date with no other qualification span; until the items builder changes, "a half-run block stops, and the lead issues the second span's item by hand. The magistrate does not improvise it" | The second half of a block until the lead acts | The date plan is keyed by block, not span | VALIDITY for the dating; PACING for the wait on the lead | Future |
| D-06 | RLD:12659 | No qualification span before the freeze-2 coefficient hash is on main | Qualification | The fit is frozen before the data that tests it | VALIDITY (prereg) | Necessary |
| D-07 | RLD:17715 | No READY record takes effect between the first and second span of a block | A v4 session for one span, about 3.4 h | A block is not split across dates | VALIDITY (follows D-01) | Necessary while D-01 stands |

### 3.5 v4 sessions (R1 slot session, W1, C and T windows)

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| S-01 | MP:11; MP:13 | A session is armed only through its registered arming procedure, which sends Ed the arm notice before the night agents are installed; Ed's NO overrides | Arming a session | Owner veto on a registered, claim-bearing session | VALIDITY (registered route) | About 15 min a session |
| S-02 | RLD:17718; RLD:17707 | READY is the lead's record, valid 72 h; it may be delegated to the interim lead once three native lines pass | A session until a person posts READY | READY is a priority record | VALIDITY for the checklist behind it; PACING for the wait when the checklist lines are the magistrate's own observations | n.r. |
| S-03 | RLD:17124 | The R1 driver keeps its registered 02:00-02:35 hold | At most 70 min in a 28 h session | It is a registered R1 procedure and sizes `window_max_s` | VALIDITY (prereg) | Inside the session |
| S-04 | RS:1861; RLD:17851 | The counted Part C gets a G1 re-read before R1 installs | R1 | The evaluator never counted G1 records | VALIDITY | One read; done (RS:1623) |
| S-05 | RS:1866; RLD:17723-17727 | A lead record "PRE-NOTICE until <time>" (at most 30 min, renewable once) holds F0, F2 and hp-02 | Fillers for up to 60 min | Avoids the Mon 16 inversion | PACING (the host is held empty for a person's estimate) | 0 so far |
| S-06 | RLD:12676-12681; RS:12911 | A native smoke before every long block after any code or config change; the counted pilot serves for campaign bytes | A session after any change to measured bytes | A session that cannot be redone must not fail on a tooling fault | SAFETY. Over-built when applied to kit data or to bytes off the measured path | 9.9 h of smokes and soaks on 11-11 to 11-14; measured bytes changed 9 times in 50 h |

### 3.6 Hand gates and the desk

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| H-01 | RLD:17260; RLD:12676-12679 | The lead hand-reads the first span of every new kit (the class A smoke) beside the automatic desk before the rest of the kit is issued | The rest of a block until a person signs | The smoke proves the kit's bytes | VALIDITY, over-built: a kit on an admitted pin is data | 28 min on Mon 16 (close 05:10:07, signed 05:38:41) and the 2 h 13 min inversion |
| H-02 | RLD:17261 | The L002 and L005 consumer gates are read by hand | The next span | The first consumer leg must release against the span reference | VALIDITY, mechanical: the value is a field of the leg record the Check already prints (RS:3025) | Inside the Check |
| H-03 | RLD:17262; RLD:17497 | RL-158 Q1's reference print is made by hand on every v1.1 span, and span k's Q1 record must exist before span k+2 arms. It may become automatic once it has matched the hand print on three spans | Span k+2 | The reference source must be the one the runner verified | VALIDITY. The condition for automation is met: the automatic desk equalled the hand table on every value for dev-04-s01 and dev-04-s02 (RS:3000, "0 of 114 differ") and the dev-03 and dev-01 spans before them | A local Sol desk seat (7 min) plus the magistrate's re-execution per span (RS:3000) |
| H-04 | RLD:17264 | A sampled hand table (one span in four by seed, and always after a redo, exclusion or schema change); a disagreement holds the next arm | The next arm on a disagreement | An independent check of the automatic table | VALIDITY as a check; PACING as an arm gate | n.r. |
| H-05 | RLD:12655; RLD:17253-17257 | Span k's desk is final before span k+2 arms | Span k+2 | Bounds the desk debt | PACING as an arm gate: it protects the lead's review queue. The validity need is that a span is checked before a look reads it | dev-05 could not be issued on 11-17 morning until the MBP built both dev-04 desks (RS:3000) |
| H-06 | RLD:17872 | Hand-reads use the MBP's own raw directory, not a pushed projection | Where the hand-read runs | A projection could hide a field | VALIDITY | n.r. |

### 3.7 Gates enforced in code and config

The full table is `appendix/code-gates.md`: 171 rows with `ref:path:line`, of which 143 are in tracked code on refs in use. This section groups them. Refs: `K11` is the campaign pin `2d347f721`; `W1` is the W1 line at `b2e01464d` (F0, Part C, R1); `CTL` is the unmerged controller, PR #800 at `ce5097e95`. **`origin/main` holds no measurement code**: main and the W1 line are about 1,600 commits apart on each side, so every launch runs from a pinned worktree.

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| X-01 | K11:`joulewise/cadence/legs.py:305-323, 350-358`; K11:`scripts/align_r1_rehearsal.py:64`; K11:`scripts/cadence_legs_runner.py:400-402, 480-482`; W1:`scripts/run_align_r1_smoke.py:308-327`; W1:`scripts/align_r1_rehearsal.py:1033-1050, 1134`; W1:`joulewise/align/r1_arm.py:96-99` | Clock blackouts for the macOS daily batch. A campaign launch is refused when its worst case meets the window passed in `--batch-window`, when its fence would end after 01:50, and for any t0 from 10:50 to 13:15 (the campaign pin still carries the old 11:45-13:15 constant). A soak waits out a window and no leg starts in one. The F0 soak child refuses a soak start in (22:50:40, 02:35:00), after launch. The R1 driver waits out 02:00-02:35 and allows two encounters | Launches by time of day | "Three days of dasd logs put the daily batch at about 02:08" (W1 code comment); RL-149 §2.9 item 4 (RLD:12682) | PACING in frozen code: a clock stands in for a load that the per-leg detector (X-09) already measures. RL-171 disowned it (RLD:17081). The constant has five homes across refs | 4.9 h on 11-11 to 11-14; the F0 window's share of the evening tails; the `--batch-window` argument choice at every campaign launch |
| X-02 | K11:`legs.py:351-352`; W1:`scripts/launch_align_r0.py:24-27, 45-86`; K11:`cadence_legs_runner.py:466-473` | A launch is refused if its worst case exceeds the 12 h desk ceiling, or if the deadline cannot fit the worst case plus reserves (12,180 s for F0) | Long spans; any launch near a deadline | "A cap stops a unit slip or a typo from fencing the magistrate for days" | SAFETY (a bounded fence). Worst cases are 2 to 2.5 times the real length (RLD:17064), so anything scheduled on them over-reserves. RL-171 §6.3 already says the worst case is the kill bound and "no longer gates a launch" (RLD:17166) | n.r. |
| X-03 | K11 kits `min_gb` 40; W1:`joulewise/align/r0_host.py:381` (80 GB); main:`scripts/prewindow_check.sh:152` (20 GB); `measurement_mode.zsh` (60 GiB, untracked); the desk launcher only reports | Free-disk floors: five values in five places | The arm | Room for the run | PHYSICS, inconsistent | 3 min on Mon 16 (RS:4669) |
| X-04 | K11:`joulewise/cadence/kit.py:474-479`; K11:`scripts/run_align_r1_smoke.py:165-173`; W1:`joulewise/night_gate.py:219-220` | No `claude` or `codex` process outside the runner's own tree, at the arm and during the span; no stray monitor; no night label loaded | A run beside an agent | Contamination | PHYSICS | Necessary |
| X-05 | K11:`kit.py:466-485`; K11:`cadence_legs_runner.py:445-457`; W1:`launch_align_r0.py:194-201` | AC power, power mode 0, network time off, frequency word 0, no High Power marker, meter ready | The arm | The measurement condition | PHYSICS | Necessary |
| X-06 | K11:`cadence_legs_runner.py:458-459`; W1:`launch_align_r0.py:228-233` | Sleep the display, then dwell 300 s before the first checked segment | 5 min a span | Menu-bar redraws wake WindowServer and trip the census | PHYSICS | 5 min a span, by design |
| X-07 | W1:`scripts/align_r1_rehearsal.py:981-994`; K11:`run_align_r1_smoke.py:330-332` | A 1,800 s soak whose last 1,200 s must settle (slope at most 0.2 °C/min) and be quiet | 30 min a span | The thermal start state | PHYSICS | 30 min a span, by design |
| X-08 | K11:`joulewise/align/apple/cadence_leg.py:95-97`; K11:`joulewise/align/apple/r1_runtime.py:86`; K11:`cadence_legs_runner.py:142-170` | The G0 thermal gate must release within 1,200 s; member cap 1,800 s; leg process cap 2,700 s | A leg | Inclusion and kill bounds; "re-deriving it mid-campaign would change the population" (RLD:17164) | PHYSICS and VALIDITY | Necessary |
| X-09 | K11:`cadence_legs_runner.py:412-424`; W1:`align_r1_rehearsal.py:813-822, 907-913` | Rule 5: outside load above 0.5 core for 60 s redoes the leg, at most twice a span; an incomplete load journal refuses | A contaminated leg | This is what "quiet" means (RLD:17063) | PHYSICS and VALIDITY | One redo of about 21 min on most nights (RS:4667, RS:3025) |
| X-10 | K11:`joulewise/cadence/stops.py:27-77`; K11:`joulewise/cadence/queue.py:196-203, 269-270` | Named stops halt the queue: INSTRUMENT_FAULT, CONTAMINATED_REDOS (3), LEG_OVERTIME (two legs over 1.5 times budget), REFUSAL; a bad-terminal span stops the chain | Everything after the span | RL-149 §2.4 (RLD:12515) | Mixed; see I-09 | 0 on 11-15 to 11-17 (every span closed clean) |
| X-11 | K11:`queue.py:99-100, 134-137, 252-254, 277-282` | In the pinned queue code: queue expiry; the k+2 desk rule (`WAIT_AIR`); `not_before` is checked for format only and never enforced | The queue | "A queue is finite" | PACING (expiry, k+2). The pin's `cadence_queue.py next` exists, and the items forbid using it "to grant authority" (RS:1467) | n.r. |
| X-12 | K11:`cadence_legs_runner.py:251-265`; K11:`kit.py:457-465`; K11:`legs.py:426-433` | The runner re-verifies the frozen commit and every frozen path hash. A leg is admitted only if complete, G0 released, decode cap reached, power mode right, not contaminated | A run on changed bytes; an inadmissible leg | Pre-registration; RL-149 §2.4 | VALIDITY | Necessary |
| X-13 | K11:`scripts/launch_cadence_span.py:137-155, 219`; W1:`launch_align_r0.py:177-191, 358-362` | One desk fence at a time; the LaunchAgent must claim it within 30 s; the magistrate must exit within 180 s of the handoff | A second run; an agent that lingers | One host; no agent at capture | PHYSICS and SAFETY | Necessary |
| X-14 | W1:`configs/launchd/com.joulewise.magistrate.plist.template:26-29`; W1:`scripts/magistrate_watchdog.py:104-108, 1322-1342, 1958-1999, 2036-2090, 2332-2354` | Watchdog: wake tick every 300 s; one magistrate at a time; a plan or desk fence holds the magistrate until the span ends; a stand-down ladder; relaunch backoff of 2 min to 2 h after failures | The magistrate | No agent at capture; no crash loop | PHYSICS and SAFETY | 3.0 min of wake latency a close (Mythos ledger) |
| X-15 | W1:`r1_arm.py:33-45, 81-99, 125-126`; W1:`joulewise/align/apple/v4_cadence.py:263-275` | R1: t0 at least 15 min ahead (the notice); the registered span of 102,168 s; calibration is exactly 8 admitted windows | The session | Registered values | VALIDITY (prereg) | Necessary |
| X-16 | CTL:`joulewise/cadence/standing.py:50-70, 87-190, 454, 816-819, 940-986, 1495-1527`; CTL:`scripts/cadence_controller.py:103-125` | The unmerged controller encodes 92 named reasons (66 halt, 19 wait): queue TTL, the 24 h watcher, F0 spacing and the three-a-day cap (still `F0_MAX_PER_DATE = 3`), the 2 h 30 min horizon, k+2 desk and Q1 debts, the gaps, a 120 s midnight margin, a hard-coded calendar instant for the key copy | Would block as the items do now | Each cites the ruling it implements | PACING, about to be compiled in; see `CUT.md` CUT-30 | PR #800: 10 review rounds |
| X-17 | main:`RUN_STATE.md`, 105 fenced `sh` or `zsh` blocks; RS:1276-1288; RS:1396-1445 | The only executable form on main of item expiry, the watcher check, the close interval, the F2 priority gate, F0 spacing and the launch band is shell pasted into items | The arm | "The interim until #800 is admitted" (RS:1899) | PACING (the program lives in the log) | Section 3.3 |
| X-18 | In no commit reachable from any fetched ref. Path on the MBP: `/Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh`; 40 mentions in RUN_STATE | `measurement_mode.zsh verify` runs at every arm and close and supplies the 60 GiB floor and the process-census lines | The arm | Host readback | PHYSICS. Also a SAFETY gap: a gate that runs at every arm is not under version control or review | n.r. |
| X-19 | main:`.github/workflows/ci.yml:121-122`; main:`docs/process/state_kernel.json` | CI fails if generated views of the state kernel drift. The kernel holds 283 tasks (192 queued) and was last updated 2026-09-25 | Merges | It is "AUTHORITATIVE_WORK_SELECTION_STATE" | PACING (historical): seven weeks stale, still a required check | Seconds a run; a false source of truth |

### 3.8 The Air, the lead and holds

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| A-01 | RS:2979 (item 388) | The MBP never stops for the Air: seven fallbacks, one per Air-dependent step | Nothing; it removes blocks | Ed, 11-17 | Not a gate. It exists because seven gates named the Air | n.a. |
| A-02 | RS:3043; lead note `no-ssh-without-check-item` | No lead SSH or job on the MBP until the armed span's Check item is on main | Lead work on the MBP | A second process contaminates the run (two slips, 11-15 and 11-16) | PHYSICS (contention) | Necessary |
| A-03 | RLD:17330; RS:1598 | The MBP runs measurement only; agent or code work only in gaps of 2 h or more with nothing armed | Lead and seat work on the MBP | Quiet | PHYSICS (contention). The "2 h" is arbitrary; at saturation there are no such gaps, which is the intent | 11.0 h of other compute on the MBP on 11-11 to 11-14, before the rule |
| A-04 | RS:1597 (item 402); RS:3008 (item 384) | When the Air pauses, the lead's whole work list is handed to the MBP's interim lead as a RUN_STATE item, and taken back when it resumes | Nothing directly | Ed paused the Air four times on 11-17 | PACING (ceremony): eight items in one day | Lead time; n.r. |
| A-05 | RS:2991 (item 387); RLD:12653; RLD:17474 | Line 7: a results watcher observation under 24 h old is required at each arm (a flag, not a stop, while the Air is paused) | Issuing dev-05 on 11-17 until Ed was asked (RS:3000) | Someone is told when results land or a span is silent | PACING as an arm gate: "it guards no physical hazard and no measurement" (RS:2992). The alarm itself is worth having | F0 ran in place of counted work that morning; a question went to Ed |

### 3.9 The magistrate prompt and per-run ceremony

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| M-01 | MP:3 | Resume from the top pointer in RUN_STATE and the state file it names | Nothing; it makes RUN_STATE prose the program | Durable state | PACING (historical design) | Every activation loads and interprets items of 50 KB |
| M-02 | MP:5; MP:25 | Before every work slice search Gmail for Ed's unread mail and list open `directive` issues | Seconds | Owner instructions | Owner channel | Necessary |
| M-03 | MP:10 | Move the canonical root only when no plan is armed and no night agent is loaded | Git moves while armed | A moved root invalidates an armed plan | SAFETY | Necessary |
| M-04 | MP:14 | Never start or continue `[QUIET-MAC]` work while an agent session is alive | Measurement beside an agent | Contamination | PHYSICS | Necessary |
| M-05 | MP:17 | Stand-down: request at t0−180 s, SIGTERM at t0−90 s, SIGKILL at t0−60 s | The magistrate near a t0 | No agent alive at capture | PHYSICS | Necessary |
| M-06 | MP:20 | The magistrate does not ratify or amend a process rule | Rule changes by the magistrate | Authority | Authority | Necessary |
| M-07 | MP:22 | RUN_STATE items are written only with `run_state_add.py` | Hand edits | Six duplicate item numbers | SAFETY (record integrity) | Necessary |
| M-08 | RS:1085 (item 414); RS:1200 (item 407); RS:1047 (item 416) | Per launch: a pre-launch RUN_STATE item, a process-trace file, custody copies of `inputs.sh`, `startcheck.sh`, `launch.sh` and their outputs. Per close: a Check item, a trace file, custody copies of the check script and output, a mail | The next launch for the length of the Check | Evidence | PACING (ceremony). The receipt, the runner's step list and the launcher's JSON already are the evidence | Close to next launch is 14 to 25 min when nothing else binds, against a 5 min floor: about 2.3 h over seven closes; Mythos measured 8.1 min of Check plus 3.0 min of wake per close on 11-14 |
| M-09 | RLD:12667 | Alarms: "refused or stranded noticed" within 10 min; "MBP unarmed with no job queued" within 30 min, also on `DESIGN_QUEUE_LOW` | Nothing; it is the anti-idle alarm | RL-127 term 6 | The right rule. Not wired: `DESIGN_QUEUE_LOW` appears twice in RUN_STATE, and the host idled 25.7 h in three days without an alarm | The absence cost the 25.7 h |

### 3.10 Review, merge and hand-off

The full table is `appendix/review-rules.md`: 222 rule rows from 29 sources on main (39 from `docs/orchestration.md`, 25 from the bridge contract, 21 from PIPELINE.md), with 19 contradictions between rules that are both in force, and the PR timings. This section groups them.

**What the PR record shows (10 to 17 November, 94 PRs).** 66 merged, with a median of 2.2 h from open to merge and a 90th percentile of 12.7 h. The PRs that merge, merge fast. The delay is in the ones that do not: from 15 Nov 12:06 UTC to 18 Nov 00:35 UTC nothing merged for 60.5 h while nine PRs were opened, eight of them still open. 56 PRs are open, 49 of them drafts, with a median age of ten days. PR #800 is the top of a five-deep stack (#800 on #799 on #794 on #788 on #775), none merged and none targeting main.

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| R-01 | PL:10-18 | Three tiers. Tier 2 is "code that arms, measures, offloads or deletes on the MBP; anything touching blinding, custody or prereg; code that computes, selects or excludes a claim number" | A tier 2 merge until spec, freeze, review and two accepts | Ed approved it on 11-17 and asked that it stay small | VALIDITY and SAFETY for the cases that can change a number or destroy data; over-built in scope: it sweeps in copy tools, desk transport and the queue | The cluster below |
| R-02 | PL:42-52; `docs/orchestration.md:95-101` | PIPELINE: at most three review rounds at tier 2, then return to spec, "there is no round 4". Orchestration, still on main: "No fixed round caps" (from D-132 and D-186) | Nothing consistently | Each cites an incident | The cap is the right rule. The older text contradicts it and PIPELINE's supersession list (PL:111-123) does not name it | #800: gates 1 to 7 and rounds to 10. #795: 60 commits, round 10 |
| R-03 | PL:54-62; `docs/orchestration.md:270-273` | A cluster of PRs gets an integration owner, a shared contract suite and an acceptance line; a member PR merges only after it | Every member PR | Integration seams had no owner | PACING (a second accept). `tests/contracts/` does not exist on main; #811, which adds it, has 1 scenario passing and 74 expected failures | Five PRs wait on #811's review |
| R-04 | RS:12916 (item 220); RS:12914 | Sol and Opus each build every block or window design, arm routes included, then an agreement report, then a lead ruling. "Cross-family review alone is not enough" | Every design until two builds agree | Ed, 11-08, after R1 had no arm route | PACING (review count). Never withdrawn; PIPELINE does not name it | Two builds per design; n.r. |
| R-05 | lead note `main-goal-v4-squeeze` (Ed, 11-07) | Every v4 step gets at least two Sol xhigh seats and an agreement report | v4 steps | Auditing v4 is the main goal | PACING (review count) | n.r. |
| R-06 | lead note `fable-research-lead` (Ed, 11-10); PL:69 | The research lead reviews everything (a cold-review gate). PIPELINE: only what is paper-bound | Merges that wait on a ruling | Final say on the paper | VALIDITY for what is paper-bound; PACING beyond it | Rulings arriving mid-review added scope to six PRs (R-12) |
| R-07 | `.github/workflows/gate-ledger.yml:4-35`; `scripts/check_gate_ledger.py:192-199`; `docs/orchestration.md:247-268`; `.github/pull_request_template.md:1` | A required check on main: the PR body must carry `Tier: full` or `light`, five ledger rows with RUN evidence (independent executing review, whole suite on the merged tree, CI green on the final head, a cold final pass for measurement code, every finding dispositioned) and six Impact lines. "Any change to code or configs is FULL-TIER." "Every fresh PR is red by construction" | Every merge to main | D-118, D-170: three PRs merged after an incomplete gate | VALIDITY for claim code. PACING for the rest, and it contradicts R-01: two tier systems are live, and PIPELINE's "only a VERIFIED HIGH blocks" (PL:33) against "every finding dispositioned". PRs opened on 11-17 carry both forms | Ledger row 1 is NOT-RUN on all eight open cluster PRs that carry a ledger; a builder cannot fill it |
| R-08 | `docs/decision_log.md:8122-8124` (D-118 item 10); `docs/orchestration.md:211-212, 259-261` | The final-head rule in four versions, from "any commit after the last review round gets one more fresh-eyes pass, however small, no exceptions" to "only a commit that touches number-bearing code" | A merge after any late commit | Late commits had slipped past review | VALIDITY in the narrow form; PACING in "however small" | Each fix round invites a fresh pass, which opens the next round |
| R-09 | `docs/orchestration.md:64-68`; practice on #800 gates 5 to 7 and #795 rounds 7 to 10 | Each review round goes to a fresh ("cold") seat | Convergence | Independence | PACING: a fresh reader finds a different set each time. #800's gate 1 found 16 HIGH between two seats; gates 3 to 7 each found one or two new HIGH after the previous set was fixed; then a new auditor found more at round 10 | #800 and #799: 68 h open. #795: 72 h |
| R-10 | `.github/workflows/ci.yml:148-200`; CI run history | The required `ci` check: 6 shards of 4 workers. Over the last 300 runs, a pull-request run that finishes takes a median of 61.7 min (90th percentile 120.9 min), 29 % of those fail, and 109 of 198 were cancelled by a newer push | Every merge | Tests | VALIDITY (tests) at a high price per attempt | 7.4 h of MBP wait on CI on 11-11 to 11-14. The campaign pin's suite is red and is accepted by matching its red set to the base's (RS:1921) |
| R-11 | `docs/process/coldgate_charter.md:29-36`; PL:74-76 | The charter's five mandatory triggers for a cold gate include "any second fix round on the same defect", "any proposed process rule" and any turn that ends waiting. PIPELINE allows four other triggers. The charter is hashed, so its bytes are unchanged and every judge is still handed the old list | Process changes and second fix rounds, if read literally | D-era incidents | PACING (historical), contradicted | n.r. |
| R-12 | PL:40; PR bodies of #795, #799, #800, #804, #807, #812, #813 | The freeze rule says a ruling that lands mid-build goes into the next spec version. In practice RL-173 entered #799 and #800 at round 4, RL-174 entered #795, #804 and #807, RL-175 entered #795 and #812, and RL-176 and RL-177 opened #813 with five items marked NEEDS_RULING | Convergence | Rulings are final on paper-bound matters | The freeze rule is right and was not applied. Six rulings in four days each reopened reviewed code | The 60.5 h with no merge |
| R-13 | `docs/contracts/bridge_protocol.md:28-52, 167-171`; `docs/decision_log.md:2863-2871, 3466-3518` (D-050, D-064); `docs/orchestration.md:381-388`; PL:91; `AGENTS.md:126-130` | Each delegated run needs: a 13-field task header, a return envelope, a D-064 manifest row per invocation, an invocation-manifest row with 13 minimum fields, a seat line in the allocation ledger, and for a substantial run a dated run report and RUN_STATE update | Every seat | "Run-report summaries had collapsed roughly one hundred invocations into zero auditable rows" | SAFETY for the write-scope and envelope (they stop out-of-scope edits). PACING for four records of one invocation | Lead time on 128 or more seats in six days; n.r. |
| R-14 | `docs/contracts/bridge_protocol.md:822-838`; `CLAUDE.md:14, 24`; PL:86-87; MP:21 | The tracked bridge permits only `gpt-6.1-sol`. The routing table and the magistrate prompt name `gpt-6.2-sol` and `gpt-6.2-astra` | A 6.2 seat through the tracked route | The adapter's allow-list | PACING (stale). 6.2 seats run through an untracked wrapper; the MBP's own launcher refused a 6.2 override on 11-17 and ran 6.1 (RS:1200) | n.r. |
| R-15 | `AGENTS.md:40-53`; `docs/agent_playbook.md:39-78`; `CLAUDE.md:89-91` | Every session reads AGENTS.md, CANONICAL.md, the top RUN_STATE item, CURRENT.json, POINTER_RULE.md and Mission M0 of the playbook, and orchestration.md before delegating. None of the five intake lists mentions PIPELINE.md. About 380 of the playbook's 474 lines are missions marked "Do Not Select" | Start of every session | Durable intake | PACING (historical) | Reading time per session; rules read from superseded files |
| R-16 | `AGENTS.md:83-84`; `docs/orchestration.md:242-246`; `docs/process/model_allocation_ledger.md:312-321` | The lead never delegates final verification | A merge | "Every hardware/integration bug to date was caught only by lead-side live verification" | VALIDITY | Necessary |
| R-17 | RS:12909-12910 (item 221 rules 1 and 2) | The next two MBP steps show green on an automated end-to-end readiness check; a new guard is replayed against recorded traces before it may refuse a run | A guard or step that has not been checked | Four R0 refusals from over-strict guards | SAFETY (it protects MBP hours). The right rules; the record does not show them running for the campaign items | n.a. |
| R-18 | practice; RLD (admissions "gate row 4 passes (ADMIT)" in RL-153, RL-159, RL-168, RL-170, RL-172b, RL-172c) | Measurement code is admitted by a research-lead ruling on a pin, not by a merge to main. The campaign runner (#775), kit v1.1 (#788), the hp path (#789) and the qualification pin (#794) are open drafts whose commits the MBP already runs | Nothing; it makes "merged" the wrong test for measurement code | Pins are frozen by commit | VALIDITY (pin by hash). It means tiers and ledgers on main do not govern what the MBP runs | n.a. |

### 3.11 Rule governance

| Id | Source | Rule | Blocks | Stated reason | Class | Cost |
|---|---|---|---|---|---|---|
| G-01 | RS:1 (header); RLD (every ruling's "Amends" list) | Rules are stated in items and rulings and amended by later items and rulings; nothing is deleted | Nothing directly | History | PACING (historical). The Astra register found 715 clauses in force-or-cited, 51 superseded but still cited, 28 stale, 12 duplicate, 7 contradicted | Every reader re-derives what is in force |
| G-02 | lead notes `fable-research-lead`, `window-design-council`; PL:69 | The research lead has the final say on anything paper-bound | Changes to paper-bound rules | Ed, 11-10 | VALIDITY (authority) | 5.4 h of MBP wait on rulings on 11-11 to 11-14. The rulings also carry scheduling detail that is not paper-bound (F0 spacing, close gaps, issue caps) |
| G-03 | RS:12913 (item 221 rule 5) | No blind re-runs: after a refusal the next attempt needs a fix verified on the refusal's own trace, or a ruling | Every retry | Four R0 refusals from over-strict guards | SAFETY in intent; PACING in effect, because the host waits with the entry | Part of the 20.9 h on 11-10 |
| G-04 | PL:98-109 | Every standing rule has a register row with a `review_by` date; a retirement pass every 14 days | Nothing yet | Ed approved it on 11-17 | The right rule. Not built: no `docs/process/RULES.md` exists on main | n.a. |
| G-05 | RS:1114 (item 412) | A rule that idles the host is waived once by a lead item | Nothing | Fills one gap | PACING. Ed, 11-17: remove the rule, never waive once | 33 min for the waiver to be written and picked up |

---

## 4. Counts

118 rule rows in section 3.

| Class (primary) | Rows | Note |
|---|---|---|
| PACING | 39 | Another 11 rows are a VALIDITY or SAFETY rule with a pacing part (for example "valid inside a block, pacing across blocks") |
| VALIDITY | 34 | 6 of them are marked over-built or mechanical |
| PHYSICS (alone or leading) | 21 | One of these is "claimed PHYSICS with no measured quantity" (F0-13) |
| SAFETY (alone or leading) | 15 | 4 are marked over-built |
| Mixed (I-09, the named stops) | 1 | One row holding a SAFETY, two PHYSICS, a VALIDITY and a PACING stop, all over-scoped |
| Not a gate, or the right rule but not built or wired | 8 | A-01, M-02, M-06, M-09, G-04, R-02 (the cap), R-12 (the freeze), R-17 |

23 rows are marked "Necessary": they are what the measurement physically needs or what the registration fixes, and none of them idled the host in the record.

By family:

| Family | Rows | PACING, whole or part | Where the cost fell |
|---|---|---|---|
| F0, the filler (3.1) | 16 | 7 | 10.2 h + 7.4 h + 0.55 h of idle in 72 h |
| Close, copy, offload (3.2) | 11 | 3 | 2.2 h + 2.7 h of idle in 72 h; four unmerged PRs |
| Issuing and item gates (3.3) | 16 | 12 | 5.5 h of MBP wait on 11-11 to 11-14; most of the lead's and seats' item work |
| Day design and qualification (3.4) | 7 | 1 | 32.5 h of ready counted work waiting for its date; no idle if a product filler exists |
| v4 sessions (3.5) | 6 | 2 | 9.9 h of smokes on 11-11 to 11-14 |
| Hand gates and desk (3.6) | 6 | 2 | 2 h 13 min of counted work displaced; dev-05's issue blocked one morning |
| Code and config (3.7) | 19 | 5 | 4.9 h on 11-11 to 11-14; the F0 window's share of the tails |
| Air, lead, holds (3.8) | 5 | 2 | Eight hand-off items in a day |
| Magistrate prompt and ceremony (3.9) | 9 | 2 | 2.3 h of close-to-launch time in 72 h |
| Review and merge (3.10) | 18 | 11 | 18.6 h + 7.4 h of MBP wait on 11-11 to 11-14; 60.5 h with no merge |
| Governance (3.11) | 5 | 3 | Every reader re-derives what is in force |

---

## 5. Coverage, and how this maps to the earlier register

**Three grains, one inventory.**

| Grain | Where | Rows |
|---|---|---|
| Rule (this file, section 3) | One row per rule, however many places repeat it | 118 |
| Gate as written or coded (`appendix/`) | `item-gates.md`: every gate in items 346, 394, 397, 398 and 406. `code-gates.md`: every gate in code on the refs in use. `review-rules.md`: every review, merge and hand-off rule on main | 270 + 171 + 222 |
| Clause (`/Volumes/JW-EXT/scratch/astra-drift-audit/REGISTER.md`) | Every standing clause in RUN_STATE through item 396 and the rulings through RL-175, with a status | 715 |

**Mapping the Astra register's statuses to this file's classes.** The register answers "is this clause in force". This file answers "what kind of reason does it have". They compose:

| Register status | Count | Treatment here |
|---|---|---|
| STALE (trigger can no longer occur) | 28 | PACING (historical). Retire at the first retirement pass without further review |
| SUPERSEDED-BUT-STILL-CITED | 51 | PACING (historical). Retire and fix the citers |
| DUPLICATE | 12 | Merge into the surviving row |
| CONTRADICTED | 7 | The lead rules; this file's class for the surviving side decides who owns it |
| LIVE | 617 | Each falls under one of the 118 rows above. The register's sections map as: "MBP dispatch, custody and host rules" to 3.1, 3.2, 3.8 and 3.9; "Research rulings that govern current scheduling and release" to 3.3 to 3.6; "Research rulings through RL-170" to 3.4 to 3.7 where still operative, otherwise to the register's own row; "Installed process contracts" to 3.10 and 3.11 |

Line numbers in the register's RUN_STATE cites are from an older revision (item 396). Items 397 to 416 were inserted above them, so each cite at or below the newest-first region is about 1,914 lines lower in the revision cited here (for example the register's `RUN_STATE.md:3918` for item 346 rule 7 is RS:5838). Its cites into the rulings file are unchanged, because that file only grows at the end.

**What this inventory does not cover.**
- Rulings RL-1 to RL-142, except where a later ruling or a live item cites them. Most concern Block 5, Block 6 and BYTES, which are released or closed. The Astra register's section "Research rulings through RL-170" lists those still cited.
- `docs/decision_log.md` beyond the D-entries the process files cite (D-050, D-064, D-072, D-118, D-132, D-170, D-183, D-184, D-186).
- `docs/council_log.md`, the run reports, and the untracked tools `codex-run-v3` and `measurement_mode.zsh`.
- The registered analysis rules (estimators, inclusion at a look, release). They are VALIDITY by construction and none of them gates the MBP.
- The v4 session's internal procedure (the D-7 packet, the 60-key check, the seal). Section 3.5 lists what gates the session's start; `appendix/item-gates.md` lists the gates in items 397 and 398.

**Checks made on the three extraction passes.** I compared a sample of their line cites with the files: for `item-gates.md`, RS:1759, 1899, 1903, 1910, 1921, 1924, 1930, 2167, 2181, 2256, 2257 and 2263; for `code-gates.md`, RS:1276, 1284, 1396, 1413, 1440, 1467 and 1899. All matched. I did not re-read the code on the pins myself; the `ref:path:line` cites in section 3.7 are the pass's. The class in every row of section 3 is mine; the passes' own class guesses in the appendix files are theirs and differ in places (the code pass calls worst-case-fit checks PACING; I call the desk ceiling SAFETY).
