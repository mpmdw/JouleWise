# CUT: what to delete, what to replace, what to shrink

Mythos 5.2 process audit, 2026-11-17. Rule ids (F0-06, C-02, I-02 and so on) are the rows of `RULES.md`. Cut ids are `CUT-nn` for pacing rules and `O-nn` for over-built ones. `RS:n`, `RLD:n`, `MP:n` and `PL:n` are cited as defined in `RULES.md`.

## 0. How to read this

- **Section 1** lists every PACING rule and what happens to it. The lead can make all of these cuts without the research lead, under Ed's directive of 11-17 (RS:1065, item 415) and PIPELINE §5 ("Lead: everything else", PL:71). Where a cut rewrites words Fable wrote, it is marked **tell Fable**: she is told in the batch and the cut proceeds unless she objects.
- **Section 2** lists VALIDITY and SAFETY rules that are over-built for their job.
- **Section 3** is the one batch for Fable: the cuts that touch paper-bound validity, each as an exact question with a default.
- **Section 4** ranks the cuts by MBP hours a week.

"Hours a week" scales the 72-hour record of 15 to 17 November (`RULES.md` section 1.1) by 7/3 unless another basis is named. The figures overlap where two rules bound the same gap; section 4 says which.

---

## 1. PACING rules: delete or replace

### 1.1 The filler's pacing

| Cut | Rule | Action | Replacement | Who |
|---|---|---|---|---|
| CUT-01 | F0-06: 14,400 s between F0 t0s (RS:5836). The three-a-day cap is already revoked | **Delete** | Nothing. Each run has its own soak and gate. The reason given, "load without product" (RLD:17172), is an argument for a better filler (CUT-05), not for an empty host | Lead; tell Fable |
| CUT-02 | F0-05: the 20-minute wait for the lead's reply after a refusal (RS:5835). I-05: "any failed line ... nothing launches; a later t0 needs a new item" (RS:1895) | **Delete** the wait; **replace** the dead end | The refused entry is ineligible until its inputs change (`STRUCTURE.md` E6). The ladder continues at once. A lead reply is honoured at the next close | Lead |
| CUT-03 | F0-04: "once a session is READY nothing lower arms" when the session cannot arm (RS:5834) | **Replace** | A READY session has priority at a close where its arm succeeds. If its arm refuses, the refusal is recorded and mailed, and the ladder continues. Item 397 already says this for R1 (RS:1759, clause 6); make it the general rule | Lead; tell Fable (RLD:17288) |
| CUT-04 | F0-02: void on a W1-line merge and expiry 7 days after issue (RS:5828). F0-09: the restart hold (RS:5839) | **Delete** both | A filler entry is valid while its pin is on the admitted list. The restart hold is stale | Lead |
| CUT-05 | F0 as the default filler | **Replace** | A product ladder ahead of F0: single F2 legs as their own spans (Fable already sized one at about 1 h, RLD:17159), the remaining F2 pieces, hp-02 (RLD:17859-17860). F0 stays as the last rung until the R1 session has run, then see F-4 | Lead stocks the queue; F-4 for retiring F0 |
| CUT-06 | F0-11: the per-run Check item, mail and line-by-line comparison (RS:5841) | **Replace** | The close script writes one generated line. One mail a day summarises fillers. A changed verdict line is flagged by the script | Lead |
| CUT-07 | S-05: the pre-notice that holds fillers for up to 60 min (RS:1866) | **Replace** | A counted entry may carry `expected_ready_by`; the scheduler then picks a filler that ends before it. With one-hour fillers the worst inversion is under an hour | Lead; tell Fable (RLD:17723) |

### 1.2 Waiting for the Air or the lead

| Cut | Rule | Action | Replacement | Who |
|---|---|---|---|---|
| CUT-08 | C-02: the 30-minute wait for the Air's copy marker. C-03: copy owner by Air state (RS:5769, RS:1872) | **Delete** | The MBP copies at every close. The Air pulls later. Item 409 already does this "until R1 arms" (RS:1176); make it permanent | Lead |
| CUT-09 | A-04: handing the lead's work list to the MBP by RUN_STATE item each time the Air pauses; eight Air-state items on 11-17 | **Delete** | The Air's state changes nothing on the MBP. The lead's lanes live in `TASK_QUEUE.md` | Lead |
| CUT-10 | A-05: line 7, the watcher heartbeat as an arm gate (RLD:12653) | **Replace** | The alarm stays, off the arm path: the GitHub Actions watcher Fable already accepted (RLD:17468-17475, PR #805) plus the scheduler's own `QUEUE_EMPTY` and `HALTED` pages. No arm reads a heartbeat. This also wires the alarm of M-09 | Lead; tell Fable |
| CUT-11 | I-01: one RUN_STATE item per span, issued by the lead (RLD:12714). I-11: values typed in by hand. I-14: the 24-value arm record written twice. I-15: the ban on the pin's own `next` | **Replace** | A queue entry (`STRUCTURE.md` a.4) and a computed decision. RL-149 §2.8 already grants a standing queue with no per-span item (RLD:12641) and RL-172 (g) accepted it (RLD:17293) | Lead |
| CUT-12 | I-02: an item expires 24 h after issue (RLD:17483). I-03: at most three counted spans issued ahead (RLD:17479). I-06: a queue expires seven days after its commit (RLD:12647) | **Delete** all three | An entry is valid while its pin and kit hash are admitted and its window is open. These caps bounded how far a prose item could drift from the lead's attention; a hashed entry does not drift | Lead; tell Fable |
| CUT-13 | I-13: the drafting chain for each item (builder draft, Sol items review, Mythos delta seat, fill and issue) | **Delete** | Entries are data, validated by `mbp_sched.py validate` and the launcher's dry run | Lead |
| CUT-14 | H-05: span k's desk final before span k+2 arms, as an arm gate (RLD:12655) | **Replace** | The automatic desk runs in the close script. Its failure makes the same kit's later spans ineligible. A hand table is owed before a look reads the span, not before a later span arms | F-3 |
| CUT-15 | D-05: "a half-run block stops, and the lead issues the second span's item by hand" (RLD:17813) | **Replace** | The second half is a queue entry whose window is "the next date with no other qualification span" | Lead builds it; the dating rule is Fable's and is unchanged |
| CUT-16 | S-02: READY posted by a person when the remaining checklist lines are the magistrate's own observations | **Replace** | The lead commits the adoptions ahead; READY is derived when the native lines pass (RLD:17718 already recommends this delegation) | Lead |

### 1.3 Ceremony

| Cut | Rule | Action | Replacement | Who |
|---|---|---|---|---|
| CUT-17 | M-08: per launch, a pre-launch item, a trace file, three custody scripts and their outputs; per close, a Check item, a trace file, a script, an output, a mail | **Replace** | One generated record per launch and per close, written by the tick. The receipt and the launcher's JSON are the evidence. Mail to Ed only on a change of state he must know (MP:5 already says this) | Lead |
| CUT-18 | M-01: the magistrate resumes from RUN_STATE prose (MP:3). X-17: 105 shell blocks in RUN_STATE | **Replace** | The magistrate runs `mbp_sched.py tick` and does what it prints. The add tool refuses shell in an item | Lead |
| CUT-19 | I-10: eight test modules (201 tests) and a fresh worktree before every launch | **Delete** per launch | Once per pin per host, recorded. RL-149 §2.8 line 2 already says one result covers every span on those bytes (RLD:12645) | Lead |
| CUT-20 | F0-14: the eligibility check run twice. F0-01: the 17-hash table in prose. The checks repeated three times in one launch (expiry, close interval) | **Delete** | The launcher verifies its own frozen sources. The scheduler evaluates once, under the launch lock | Lead |
| CUT-21 | C-09: holds posted as prose and lifted by a second item (RS:3041, RS:3033) | **Replace** | A `maintenance` entry in the queue, so the work is scheduled and its cost is in the ledger | Lead |
| CUT-22 | G-05: one-time waivers | **Delete** | Retire or change the register row | Lead |
| CUT-23 | G-01: rules stated in items and amended by later items | **Replace** | The register (`STRUCTURE.md` b) | Lead; F-8 asks Fable to write clauses in the same form |
| CUT-24 | X-19: the state kernel (283 tasks, last updated 25 September) as a required CI drift check | **Retire** at the first retirement pass | Nothing reads it for work selection now. Not this week: it costs seconds and removing it touches the playbook | Lead |

### 1.4 Clock rules still in frozen code

| Cut | Rule | Action | When | Who |
|---|---|---|---|---|
| CUT-25 | F0-07 and X-01: the 02:35 to 22:40 launch window (the W1-line soak child) | **Delete in code** | In the W1-line PR that follows the slot session, as RL-171 already schedules (RLD:17126, RLD:17184). Until then it is what the bytes do, and fillers on the campaign pin, which have no evening bound, cover those hours | Lead; Brief E |
| CUT-26 | X-01: the 10:50 to 13:15 refusal and the `--batch-window` argument choice on the v1.1 pins (RLD:17101). I-12 | **Ends with the pins** | The qualification pin removes the midday band (RLD:17103). The scheduler asks the launcher's own `plan` (E5) and never re-derives a band | No action beyond not copying the band into new entries |

### 1.5 Review and merge

| Cut | Rule | Action | Replacement | Who |
|---|---|---|---|---|
| CUT-27 | R-04: paired Sol and Opus builds with an agreement report for every block or window design (RS:12916, RS:12914). R-05: two Sol xhigh seats for every v4 step | **Delete** | PIPELINE tiers. The independent recompute of claim numbers stays (PL:20-22) | Lead; tell Ed after (they were his rules of 11-07 and 11-08; PIPELINE, which he approved on 11-17, replaces them) |
| CUT-28 | R-06: the research lead cold-reviews everything | **Narrow** | She rules on what is paper-bound (PL:69), once, at the spec stage | Lead |
| CUT-29 | R-01: tier 2's scope, "arms, measures, offloads or deletes on the MBP" (PL:14) | **Narrow** | Tier 2 is four cases only (`STRUCTURE.md` c, change 1) | Lead |
| CUT-30 | The stack #800, #799, #807 and the contract #811 as a dependency of the arm path (X-16, C-11) | **Park #800, #799, #807 and #811. Reduce #804 to a copy-only tool and merge it at tier 1** | The magistrate runs `tick`; the close script copies; nothing deletes on the arm path. PIPELINE's own rule applies: #800's last four gates found 1, 1, 3 and 2 HIGH, which is not decaying, so it returns to spec (PL:47-52), and the spec it would return to is the set of rules this audit removes. See O-01 | Lead |
| CUT-31 | R-07: two tier systems, with the required gate-ledger check enforcing the older one (`Tier: full` or `light`, five rows, "any change to code or configs is FULL-TIER") | **Replace** | One system. The check reads PIPELINE's tier line: tier 0 needs CI; tier 1 needs CI and one review row; tier 2 needs the full ledger. Delete `docs/orchestration.md:247-268` and the template's `Tier:` line in the same PR | Lead |
| CUT-32 | R-02: "No fixed round caps" (`docs/orchestration.md:95-101`). R-08: the final-head rule "however small, no exceptions" (D-118 item 10). R-11: the charter's triggers "any second fix round" and "any proposed process rule" | **Delete** the older texts | PIPELINE's cap of three and its return to spec. Final-head review only for a commit that touches number-bearing code (`docs/orchestration.md:259-261` already says so). The registry notes that the hashed charter's trigger list is superseded; the judge's brief carries PL:74-76 | Lead |
| CUT-33 | R-09: a fresh cold seat for each review round | **Replace** | The seat that raised a finding reviews its fix. One fresh seat, once, at the end of a tier 2 review | Lead |
| CUT-34 | R-03: integration owner accepts, then lead accepts (PL:14, PL:54-62) | **Merge into one** | The lead is the integration owner unless the PR names another | Lead |
| CUT-35 | R-13: four records of one delegated run (D-064 manifest row, invocation-manifest row, ledger seat line, run report) | **Reduce to one** | The return envelope, kept by the launcher, is the record. The seat's ledger line is generated from it. The write-scope and envelope rules stay | Lead |
| CUT-36 | R-14: the bridge's `gpt-6.1-sol` allow-list. R-15: five intake read lists that predate PIPELINE; the playbook's 380 lines of retired missions | **Update** in one tier-0 PR | One intake list that names PIPELINE.md, RULES.json and QUEUE.json; the playbook's retired missions move to the archive | Lead |
| CUT-37 | I-07: a cold seat on every kit (RLD:12643) | **Narrow** | Only for a kit of a leg type not already ruled (RLD:12718-12720 already says a matching block "needs no ruling of its own") | Lead; tell Fable |
| CUT-38 | G-03: "no blind re-runs" as a wait on a ruling (RS:12913) | **Replace** | E6: a refused entry is ineligible until its inputs change; a tooling refusal retries once after the fix merges; the host moves on meanwhile | Lead |
| CUT-39 | R-12 in practice: rulings entering PRs mid-review | **Enforce** the freeze that PIPELINE already states (PL:40) | A ruling that lands during a build goes into the next spec version. F-8 asks Fable to batch rulings per phase | Lead; F-8 |

---

## 2. VALIDITY and SAFETY rules that are over-built

| Cut | Rule | What it protects | Why it is over-built | Proportionate form | Who |
|---|---|---|---|---|---|
| O-01 | C-11: the close as specified across #799, #800, #804 and #807: 12 span states, 15 durable artifacts, signed bundle commits, verdict refs, SSD receipts, retention holds, automatic retirement | The data, and the lead's ability to check a span | It automates deletion and a second desk for a campaign with about 30 spans left before the paper. Deleting is the only irreversible step, and the MBP had 268 GiB free on 11-17 (RS:1131) at about 5 GiB a span. The stack has been in review for three days without a merge | Copy at close with one tool. Never delete on the arm path. The lead packs and removes old spans by hand at a block boundary when free space nears the floor, as on 11-16 (RS:3033). Revisit automatic retirement after the paper | Lead |
| O-02 | C-01 and C-04: the verified off-host copy as a gate on the next arm, with a 90-minute poll that stops everything on a provider failure | One span of data against loss of the MBP during the next span | The original is retained. The exposure is hours. The cost is every close, and all measurement when the provider is slow | Copy is a debt: start at close, stop before the next soak, resume at the next close. Page at 2 h uncopied. Hold counted and v4 entries, not fillers, at 24 h uncopied | Lead; tell Fable (RLD:17458) |
| O-03 | F0-13: the fixed gaps after a close (300 s and 1,200 s) | The successor's start state | The successor's own soak and G0 gate set its start state (RLD:17154). No temperature or other quantity is named for the gap (RLD:17270) | "Close proven" and nothing else, or a named physical condition the scheduler can read | F-2 |
| O-04 | H-01: the hand-read of every new kit's first span | That new bytes measure correctly | A kit on an admitted pin is data, and the automatic desk has equalled the hand table on every span so far | Hand-read only the first span on a new runner pin | F-3 |
| O-05 | H-02: the L002 and L005 gates by hand. H-03: the Q1 print by hand and its record before span k+2 | That a consumer leg used the right reference | Both are fields of records the close already prints. RL-172 (c) set the condition for automating the print, three matching spans (RLD:17262), and it is met | Computed in the close script. A mismatch makes the kit's later spans ineligible | F-3 |
| O-06 | H-04: the sampled hand table as an arm gate | An independent check of the automatic table | A disagreement is a finding about the desk code, not about the host | Keep the sample. It is owed before a look, and a disagreement holds that kit only | F-3 |
| O-07 | I-04: "predecessor not clean: the item is void, never skipped", across blocks (RLD:17480) | That a fault is examined before more data is taken on it | Within a block the dependency is real. Across blocks it stops unrelated work for a person | A non-clean close holds its own block's later spans and raises the host checks. Other entries proceed once the host is proven clean | F-6 |
| O-08 | I-09 and X-10: named stops that halt the whole queue until a person writes a line (RLD:12515-12521) | Not building on a faulty span | Every stop holds every later span | Each stop holds the kit that raised it. Restore unproven, disk and instrument faults are host stops. The rest never hold a different entry | F-6 |
| O-09 | S-06: a native smoke after any code or config change (RS:12911) | A long session that cannot be redone | Measured bytes changed nine times in 50 hours and each change forced a smoke | A smoke only when the runner pin changes, and only ahead of a session longer than three hours. The counted pilot is the smoke for a campaign kit (RLD:12676 already) | Lead; tell Fable |
| O-10 | D-02: the day rules re-implemented in each item's shell (RS:2102, RS:2128, RS:2158) | D-01 | One rule, eleven hand-edited copies, each reviewed by a seat; `not_before` is unenforced in the pinned code (X-11) | One predicate (E2) that reads the kit's committed queue file | Lead |
| O-11 | X-03: five disk floors in five places, one of them in an untracked script (X-18) | Room for a span to finish | A span writes about 5 GiB; the floors range from 20 to 80 GB | Keep one stop with one value in the register. Evict uploaded archives automatically before paging. Put `measurement_mode.zsh` in the repository (Brief D) | Lead |
| O-12 | R-07 and R-10 for small changes: the full ledger and a CI run with a median of an hour and a 29 % failure rate, for every change to code or configs | Code that can change a number | Most changes cannot | Tier 0 and tier 1 as in CUT-31. A finding must cite a frozen acceptance scenario or carry a reproduction (`STRUCTURE.md` c, change 4) | Lead |
| O-13 | X-02 used for scheduling: worst-case bounds that are 2 to 2.5 times the real length | A bounded fence | The bound is right as a kill limit and wrong as a reservation | The scheduler reserves the worst case only against a counted entry's latest feasible start (E4), nowhere else | Lead |

---

## 3. The batch for Fable

One message. Each question has a default that takes effect if she does not object, except F-1 to F-4, which wait for her answer because they touch what the paper may say. Until she answers, the current rule stays as a predicate on the entries it names; none of these questions needs to idle the host in the meantime.

**Preface to send with it.** "Ed, 11-17: the only limits on how much the MBP measures are physical. A process audit classified every gate as PHYSICS, VALIDITY, SAFETY or PACING. The PACING ones are being removed by the lead. These eleven touch your rulings. For each: confirm, or state the physical quantity or the claim the rule protects so that the scheduler can test that condition and nothing wider."

| # | Rules | Exact question | Default if no objection |
|---|---|---|---|
| **F-1** | D-01 (RLD:17228-17233) | The date rules bind the counted entries they name. Confirm that they place no limit on any other work on the same date, that a block may start at any time on its date (there is nothing special about 00:00), and that the contention rule for fillers is "the block still fits in its date", worked back from the end of the date, not "the 00:00 arm is protected". Second: does independence need the local calendar date, or would "a block whose first t0 is at least N hours after the previous mixed block's close" serve for kits designed from now on? Give N or say the date stands | Date rules stay exactly as ruled for dev and qualification. Fillers and product work are unconstrained by date. The second part waits for an answer |
| **F-2** | F0-13 (RLD:17153-17155, RLD:17268-17272) | Every span begins with its own 1,800 s soak and a G0 gate. What physical quantity do the 300 s and 1,200 s gaps protect that the soak and gate do not? If one exists, name it and its threshold so the scheduler tests it. If none, the gap becomes "close proven" | Waits. Both gaps stay as timed predicates until answered |
| **F-3** | H-01 to H-05 (RLD:17253-17264, RLD:12655, RLD:17497) | (a) Accept the automatic Q1 print and the automatic L002/L005 read now, the three-span condition being met. (b) Move the hand table and desk-final from "before span k+2 arms" to "before a look reads span k". (c) Limit the class A hand-read to the first span on a new runner pin. A failure of the automatic desk still holds the same kit | Waits |
| **F-4** | F0-06, CUT-05 (RLD:14391, RLD:17172, RLD:17335) | F0 has returned the same verdict ten times. Its stated purpose is the bridge to the slot session (RS:5813, "Why F0 at this commit"). After R1 has run: (a) retire F0 as a standing filler, keeping one Part C per W1-line pin change; (b) accept single-leg F2 spans on the existing data-only kits, repeated across days, as the standing product filler (an instrument-stability series for the paper's validation section); (c) say what else produces evidence in an otherwise empty hour: extra same-size development-shaped legs, the dated transfer block of RL-172 (e), ctl-01 legs, Flash-Next on real weights now that the MBP has the disk (RLD:14394). The lead needs a ranked list it can queue without coming back | Until answered: product fillers that are already ruled (F2 pieces, hp-02) go ahead of F0, and F0 runs without spacing |
| **F-5** | C-01, C-04 (RLD:17458) | Tell: the off-host copy becomes a debt with a deadline (page at 2 h, hold counted work at 24 h) instead of a gate on the next arm. Originals are retained throughout. Objection? | Proceeds for entries issued from now on; items 393, 394 and R1 keep their copy gate as issued |
| **F-6** | I-02, I-03, I-04, I-06, I-09 (RLD:17479-17483, RLD:12647, RLD:12515-12521) | Tell: with hashed queue entries, the three-ahead cap, the 24 h item expiry and the seven-day queue expiry are dropped. A non-clean close and a named stop hold the kit that raised them, not the queue. Restore-unproven, disk and instrument faults remain host stops. Which named stop, if any, must still stop unrelated work, and what does it protect? | Proceeds |
| **F-7** | D-04 (RLD:17822) | Confirm the qualification batch rule is a predicate on qualification spans only, and that the 2 h 35 min it opens each date is to be filled (RLD:17825 says so). No change asked | Proceeds |
| **F-8** | G-01, G-02, R-12 | From RL-179 on: (a) end each ruling with a block "Register": for every operational clause, its class (PHYSICS, VALIDITY or SAFETY), the quantity or claim it protects, its scope, and when it ends. A clause without that block is commentary and is not executed. (b) Scheduling detail that protects no claim (spacing, gaps, issue caps, who posts a record) is the lead's to set. (c) A ruling that changes code already in review is applied at the next spec version (PL:40), not to the open PR; where possible, rulings for a phase arrive as one batch before its build starts | Proceeds |
| **F-9** | RLD:17080 (hp "worst case by 00:30", kept "so the lead is present to clear a restore unproven") | Tell: High Power spans launch at any hour. A restore that cannot be proven halts the host and pages. hp-01 restored in one attempt on all three spans (RS:7597, RS:7129, RS:6663) | Proceeds |
| **F-10** | F0-04, S-05 (RLD:17288, RLD:17723) | Tell: a READY session whose arm refuses releases the ladder at once. The pre-notice becomes a hint for choosing a short filler, not a hold | Proceeds |
| **F-11** | S-06, I-07 (RLD:12676, RLD:12643) | Tell: smokes only on a runner-pin change ahead of a session over three hours. Cold seats only on a kit of an unruled leg type | Proceeds |

---

## 4. Ranking by MBP hours a week

| Rank | Cut | Basis | MBP hours a week | Overlap and conditions |
|---|---|---|---|---|
| 1 | **CUT-05 with CUT-11 to CUT-13: a stocked product ladder in place of F0 as the default filler** | F0 took 19.8 h in 72 h while counted spans waited for their dates | **About 46**, converted from diagnostic to product-bearing | These hours are already occupied; the gain is evidence, not occupancy. Needs the F2 single-leg and hp-02 entries queued (MIGRATION step 2) |
| 2 | **CUT-01: F0 spacing** | 10.2 h binding in 72 h; the gap falls to the close gap | **About 20** | Fills with F0 until rank 1 is done |
| 3 | **Evening tails: CUT-01 plus fillers on the campaign pin, which has no 22:40 bound** | 7.4 h in 72 h | **About 17** | CUT-25 removes the F0 window itself after the slot session |
| 4 | **CUT-02, CUT-03, CUT-38: nothing waits for a person after a refusal** | 20.9 h on 11-10; 63.7 h across 11-08 to 11-10; none on 11-15 to 11-17 | **0 to 20** (one refusal a week, unnoticed for hours) | The R1 session arms Wed about 08:15; this is the exposure for the next 48 h |
| 5 | **O-09, CUT-29, CUT-37: smokes only on a pin change; kits as data** | 9.9 h of smokes and soaks in 96 h on 11-11 to 11-14 | **About 7 to 12** in a week with code churn; 0 in a week like 11-15 to 11-17 | Depends on one pin per phase (RLD:17327) |
| 6 | **D-04 filled: the qualification batch rule's 2 h 35 min a date** | RLD:17825 | **About 8** in the qualification week | No rule changes; needs a one-hour filler queued |
| 7 | **O-03: the fixed gap after a filler close** | About 15 min at each filler close; 13 in 72 h | **About 7** | Becomes the binding wait once rank 2 is cut. Waits for F-2 |
| 8 | **CUT-17, CUT-18, CUT-11: scripted close and no per-span item** | 2.3 h over seven closes in 72 h; the Mythos throughput seat measured 6.6 h a week at saturation | **About 5 to 7** | Full value needs `mbp_close.py` (Brief B) |
| 9 | **CUT-08: the copy at once, always** | 2.2 h over four closes in 72 h | **About 4 to 5** | Already in force until R1 arms (RS:1176); the cut makes it permanent |
| 10 | **CUT-14, O-04 to O-06, CUT-10: hand gates and the watcher off the arm path** | 2 h 13 min of counted work displaced on 11-16; dev-05's issue blocked on 11-17 morning | **About 3 to 5** of counted work brought forward | Waits for F-3 |
| 11 | **CUT-21: no prose holds** | 2.7 h on 11-16 | **About 3** in a week with a maintenance job | |
| 12 | **CUT-04, CUT-12: no expiry by age** | None observed. F0's item expires Sun 22 Nov 11:51. Item 394 has 10 h 50 min of usable life, and R1's READY record dies with it (RS:1759) | **0 to 24** at risk (one lost date and a day's delay to R1) | Covered tonight by point (e) of the first migration item |

Ranks 2, 3 and 7 share gaps: together they recover about 37 h a week of the 60 h a week (25.7 h in 72 h) the host idled. Rank 1 is separate: it changes what the occupied hours produce.

**What cutting MBP rules does not fix.** RL-171 says it and the record agrees: "the binding limit is READY work" (RLD:17068). The MBP was 37 % on evidence-bearing work in the last three days because nothing else evidence-bearing was eligible. The cuts in sections 1.2, 1.3 and 1.5 are aimed at that. They take the lead and its seats out of per-span items (169 items and 1.39 MB of text in eight days) and out of the #800 stack (60.5 h without a merge), so that the v4 kits, which are the demand that can fill the machine (RLD:17070), get built.
