# MIGRATION: the order of work

Mythos 5.2 process audit, written Tue 17 Nov 2026, 21:45 PST. For the lead (Opus 5.5) to execute. Companion files: `RULES.md`, `CUT.md`, `STRUCTURE.md`. Ready files: `items/` (RUN_STATE item bodies and pointers) and `briefs/` (builder briefs).

## 0. Where things stand

| Fact | Source |
|---|---|
| F0 run 10 closed at 21:05:43. Nothing is armed | RS:1047 (item 416) |
| `dev-05-s01` arms from Wed 00:00:00 under item 393; `dev-05-s02` (item 394) follows; R1 is READY with effect from s02's launch record and takes its clean close, about Wed 08:15, for 28 to 33 h | RS:1047; RS:1753 (item 397) |
| Item 394 expires Wed 12:32:46 and its pin refuses 10:50 to 13:15, so its usable life is Wed 00:00 to 10:50. If it goes void, R1's READY record goes void with it | `appendix/item-gates.md`; RS:1759 |
| The copy is made by the MBP at once at each close "until R1 arms" | RS:1176 (item 409) |
| F0's item expires Sun 22 Nov 11:51. Its launch window is 02:35 to 22:40, set by the pinned bytes | RS:5813; RS:5837 |
| F2 pieces p02 to p04 and hp-02 exist as drafts and are not issued; p02 waits on piece 1's hand-read and "queue b" | RS:1114 (item 412); RS:3008 (item 384, item 3) |
| The freeze-2 packet is owed to Fable by Thu 08:00; qualification follows on three dates | RS:1857 (item 396); RLD:17576 |
| PRs #799, #800, #804, #807, #811 are open and unmerged; #795, #809, #812, #813 are open | `appendix/review-rules.md` |

**Where the host can still idle on pacing rules, from the next activation:**
1. After R1 closes (Thu evening): F0 is the only issued filler, with a 4 h spacing and a 22:40 cutoff.
2. If dev-05 slips by seven hours on Wed: item 394 dies of age inside its own date, R1's READY dies with it, and nothing but F0 is lawful until the lead re-issues.
3. If any arm refuses: a 20-minute wait for the lead's reply, then F0 only, with spacing.
4. After R1 arms, the copy reverts to "the lead copies; the MBP waits 30 minutes".
5. From Sun 22 Nov 11:51: no filler at all unless the lead has renewed item 346.

Step 1 closes all five.

---

## 1. Tonight

### Step 1. Post the PHYSICS-ONLY SCHEDULING item (before the 00:00 activation)

This is the step that stops calendar and pacing idling from the next activation. It changes no line of items 393, 394, 397 or 398 unless the chain slips.

```
cd <rs-main checkout, detached at origin/main>
python3 scripts/run_state_add.py add \
  --heading "Laptop lead (interactive, Opus 5.5), <date +'%Y-%m-%d %H:%M:%S PST'>: PHYSICS-ONLY SCHEDULING (standing; the process audit's ruling): F0 spacing and age expiry removed; nothing waits for a person, the Air or a count; the MBP copies at once, always; product fillers before F0; items 393, 394, 397 and 398 run as issued" \
  --body /Volumes/JW-EXT/scratch/mythos-process-audit/items/item-A-body.md \
  --pointer /Volumes/JW-EXT/scratch/mythos-process-audit/items/item-A-pointer.txt \
  --owner magistrate --status ISSUED \
  --supersedes 348 --supersedes 395 --supersedes 409 --supersedes 412 --supersedes 413 --supersedes 415 \
  --message "PHYSICS-ONLY SCHEDULING (standing): F0 spacing removed; no waits for people; copy at once" \
  --trailer "Co-Authored-By: <as usual>"
```

Notes for the lead:
- The heading is plain text; the tool adds the bold. Take the time from `date`.
- 348 and 395 are legacy items, so the tool records them only. 409, 412, 413 and 415 are typed; ISSUED to SUPERSEDED and CLOSED to SUPERSEDED are both legal transitions, so all six flags should be accepted. If the validator refuses one, drop that flag; the body names the items. Item 415's pointer is replaced by this item's as the current pointer.
- Item 346 is **not** superseded. It stays the F0 item with rules 4, 5 and its expiry removed by this item.
- Read the body once before posting. Point (e) is the only one that touches a counted item, and only if the 24 h line is the sole failing line.

What the body says, in short (`items/item-A-body.md` is the text to post):

| Point | Change | Cuts |
|---|---|---|
| (a) | F0 spacing deleted; item 346 no longer expires by age; a moved W1-line head does not stop F0 at its pin | CUT-01, CUT-04 |
| (b) | No 20-minute wait after a refusal; the ladder continues; a READY session that cannot arm is not READY | CUT-02, CUT-03 |
| (c) | The MBP copies at once at every campaign close, permanently | CUT-08 |
| (d) | Product fillers (F2, hp-02) before F0; the magistrate may issue them from drafts with no date window and no age expiry | CUT-05, CUT-12 |
| (e) | dev-05 only, if the chain slips: expiry is the end of the date window | CUT-12 |
| (f) | No idle over 30 min without a physical reason; otherwise launch the lowest filler and mail the lead | the principle |
| (g) | One daily mail for fillers | CUT-06 |
| (h) | One line per record saying which points were used | |

### Step 2. Stock the ladder (lead, about an hour, tonight or Wed morning; the Air is resumed, RS:1186)

The hours this fills are Thu evening onward and the 2 h 35 min each qualification date leaves open (RLD:17825).

1. **Piece 1's hand-read.** Item 411 lists what is to be judged (L002's realized prefill of 284 against 256; L001's wall at 1.01 of budget), RS:1131. Record it on main. If it is not there when p02 is next, the magistrate does it under point (d).
2. **F2 queue b.** Commit it on the audit branch from the fixed drafts (`9ef385b9f`). In the same commit append the remaining F2 legs as one-leg and two-leg spans; Fable already allows this with no new kit (RLD:17160). A one-leg F2 span has a worst case of 5,850 s and takes about an hour (RLD:17159). These are the short fillers.
3. **hp-02.** Answer the two owner questions in its STATUS.md (`a32eb54ce`), commit its queue, and issue its three spans together (RLD:17859 allows that). It is outside every count and may fill any date (RLD:17860).
4. **Do not rebuild item 346.** Step 1 removed its age expiry. A new F0 pin, if one is wanted, comes with Brief E after R1.
5. **Do not issue anything past freeze 2 by hand.** Qualification's six items wait for the freeze-2 hash and Fable's answer as planned; when they are issued, issue them without the 24 h line and the three-ahead cap unless Fable has objected to F-6.

### Step 3. Send the Fable batch and post its item

Send `CUT.md` section 3 (the preface and the eleven-row table) with `RULES.md` attached as evidence, through the usual Fable dispatch. Ask for the answer as RL-179 with a Register block. Then:

```
python3 scripts/run_state_add.py add \
  --heading "Laptop lead (interactive, Opus 5.5), <date>: eleven process questions to the research lead as one batch (F-1 to F-11); F-5 to F-11 take effect Thu 19 Nov 20:00 unless RL-179 objects; nothing on the MBP waits" \
  --body /Volumes/JW-EXT/scratch/mythos-process-audit/items/item-C-body.md \
  --owner research_lead --status ISSUED --expires 2026-11-19T20:00:00-08:00 \
  --message "Fable batch F-1..F-11 sent"
```

This item carries no pointer block on purpose: `CURRENT.json` follows the highest pointer-bearing item (`docs/process/POINTER_RULE.md`), and that must stay the Step 1 item, whose owner is the magistrate. The Fable wait shows in `CURRENT.json` under `open_items` with its expiry.

---

## 2. This week, in order

### Step 4. Post the decision item and park the stack (Wed)

```
python3 scripts/run_state_add.py add \
  --heading "Laptop lead (interactive, Opus 5.5), <date>: process audit adopted: queue, register and scheduler replace standing and per-span items; #800, #799, #807 and #811 parked; #804 reduced to copy-only; PIPELINE narrowed" \
  --body /Volumes/JW-EXT/scratch/mythos-process-audit/items/item-B-body.md \
  --owner lead --status CLOSED \
  --message "process audit adopted; cluster parked"
```

Post it after the Step 1 item (it has no pointer, so it does not move `CURRENT.json`). Then on GitHub (the lead; this audit made no PR edit): convert #800, #799, #807 and #811 to draft with one line, "Parked by RUN_STATE <n>; revisit after the paper", and stop their builders. Keep the branches. #794 and #812 (the qualification pin) are **not** parked: qualification needs that pin, and it is admitted by ruling as before. #805 (the watcher in GitHub Actions) continues at tier 1: it is the off-host alarm and gates nothing (CUT-10). #795 (the interim look's fit) is science on the critical path to freeze 2 and is untouched by this audit, except that the freeze rule now applies to it: the rulings already issued (through RL-177) are in its scope, and a later one goes to the next version unless Fable marks it as required for freeze 2.

### Step 5. Dispatch Brief A, the scheduler (Wed; tier 1)

`briefs/BRIEF-A-scheduler.md`. Before dispatch, commit `STRUCTURE.md` to the PR branch as `docs/process/mbp/DESIGN.md`. One Sol 6.2 xhigh builder; one cross-family review (Opus or Mythos, executing); merge on CI green with no VERIFIED HIGH. It launches nothing, so it cannot hurt a run.

After merge the lead fills `QUEUE.json` with the real entries: the F0 argv from item 346's Run block, the F2 and hp-02 spans from Step 2, and the qualification spans when their items exist, each with its `plan_argv` where the pinned launcher has one (`appendix/code-gates.md`, entry-point table: `cadence_legs_runner.py plan` for campaign spans, `arm_align_r1.py size` for R1; none for F0, which carries `launch_window_local` instead). Add the register rows for anything Fable keeps in RL-179.

### Step 6. Put `measurement_mode.zsh` in the repository (any gap; tier 1)

`briefs/BRIEF-D-measurement-mode.md`. The file is on the MBP, so the magistrate places it: in an activation with nothing armed it copies the installed script and its sha256 into a new branch and pushes. One line in a RUN_STATE item asks for that. No SSH.

### Step 7. Shadow (from Brief A's merge; about two days)

Each magistrate activation, before it acts on its item as now, runs:

```
python3 scripts/mbp_sched.py probe --out /tmp/facts.json --receipt-root /Users/edr/campaign-out --receipt-root /Users/edr/code/jw-wt --self-pid $PPID
python3 scripts/mbp_sched.py explain --facts /tmp/facts.json
```

and writes one line in its launch item: `SCHED: agree` or `SCHED: disagree (<its entry> vs <scheduler's entry>, <rule id>)`. The lead reads every disagreement the same day: either the queue data is wrong, the predicate is wrong, or the item was. **Cutover condition: ten consecutive closes with `agree`, at least two of them counted spans and at least one a filler chosen at night.**

### Step 8. Dispatch Brief B, the scripted close (after A merges; tier 1)

`briefs/BRIEF-B-close.md`. In shadow, the magistrate runs `mbp_close.py close --no-copy` after its own Check and compares the 12-line summary with its Check; differences go in the same `SCHED:` line.

### Step 9. Dispatch Brief C (C1 any time; C2 at cutover)

`briefs/BRIEF-C-runstate-prompt.md`. C1 archives the legacy region and stops items from holding programs. C2 changes line 3 of the magistrate prompt; the lead merges it when Step 7's condition holds. The first activation launched from a canonical root at or past that merge gets the new prompt (MP:10 says how the canonical root moves), and from then the magistrate runs `tick`.

### Step 10. PIPELINE and the tier check (one tier-0 PR by the lead, any time)

Edits, all in one PR:
- `docs/process/PIPELINE.md`: the eight changes in `STRUCTURE.md` section (c). Replace the tier 2 cell of the table at line 14 with the four cases. Add to §8's supersession list: `docs/orchestration.md:95-101` and `:247-268`; RUN_STATE items 220 and 221 rule 6; D-118 item 10's "however small".
- `scripts/check_gate_ledger.py` and `.github/pull_request_template.md`: accept `Tier 0`, `Tier 1`, `Tier 2` on line 1; require ledger rows by tier (0: CI only; 1: review row and CI; 2: all).
- `docs/orchestration.md`: delete the two superseded passages and point to PIPELINE.
- `AGENTS.md`, `CLAUDE.md`, `docs/agent_playbook.md`: one intake list that names PIPELINE.md, `docs/process/RULES.json` and `docs/process/mbp/QUEUE.json`; move the playbook's retired missions to `docs/archive/`.
- `docs/contracts/bridge_protocol.md`, `CLAUDE.md`, `.claude/skills/codex/SKILL.md`, `scripts/codex-mcp-server.mjs`: the model allow-list names the model actually in use.

This PR changes the required check, so it is tier 1 under the new table: one cross-family review.

### Step 11. Reduce #804 to a copy-only tool (tier 1)

One builder on #804's branch: delete the `close` verb and its script entry (the path that ends in removing the span directory, `joulewise/span_offload.py:1657-1713` and `scripts/close_offload.py` at #804's head, per the cluster contract's finding D13), delete anything that removes or rewrites an original, retarget to main, drop the dependency on #811. Keep `offload`, the marker and its re-check. `mbp_close.py` then names it in `--copy-config`. Until it merges, the copy command is item 347's steps as a script file in the custody root.

### Step 12. After R1 closes: Brief E, or nothing

If RL-179 keeps F0: `briefs/BRIEF-E-w1-window.md` removes the 22:40 window on the W1 line together with #809's evaluator fix, as RL-171 scheduled. If RL-179 retires F0 (F-4): merge #809's evaluator fix alone for the record and drop the F0 entry from the queue.

### Step 13. First retirement pass (at qual-03's close)

Run `mbp_sched.py report --since 2026-11-18`. For each register row: hours of WAIT and times fired. Retire what never fired. In the same pass: mark the Astra register's 28 STALE and 51 SUPERSEDED-BUT-STILL-CITED clauses retired (they are in the archived legacy file by then, so this is one line in the register's header), and retire the state-kernel CI check (CUT-24).

### Not on this list

- **A LaunchAgent that runs `tick` without a model.** It is the end state (`STRUCTURE.md` a.6) and it is tier 2. Build it only if, after cutover, the ledger shows the magistrate's wake and decision time is still a material share of each close. With a scripted close it may not be.
- **Automatic retirement of raw spans.** After the paper.

---

## 3. What the magistrate does, by phase

| Phase | Reads | Does | Writes |
|---|---|---|---|
| Tonight to Brief A's merge | Items as now, plus the Step 1 item | Launches as now, with points (a) to (h). Never idles over 30 min without a physical reason | Items as now, plus one line naming the points used |
| Shadow | The same, plus `explain` | The same; acts on the items; reports agree or disagree | One `SCHED:` line per launch |
| After cutover | `tick`'s output | Runs the printed argv as its last action; on HALT or QUEUE_EMPTY mails the lead and Ed | Nothing by hand: the close script and the tick write the records |

At no phase does the magistrate decide a science question, change a pin, or delete data.

---

## 4. Builder briefs

| Brief | PR | Tier | Depends on | File |
|---|---|---|---|---|
| A | `mbp_sched.py`, `QUEUE.json`, `RULES.json`, CI check | 1 | nothing | `briefs/BRIEF-A-scheduler.md` |
| B | `mbp_close.py`, `tick` | 1 | A | `briefs/BRIEF-B-close.md` |
| C1 | Archive legacy RUN_STATE; add-tool limits | 0 | nothing | `briefs/BRIEF-C-runstate-prompt.md` |
| C2 | Magistrate prompt line 3 | 1 | A, B, shadow passed | same file |
| D | `measurement_mode.zsh` tracked, with a hash check | 1 | the magistrate's copy | `briefs/BRIEF-D-measurement-mode.md` |
| E | W1 line: remove the F0 soak child's clock refusal, with #809 | 2 | R1 closed; RL-179 keeps F0 | `briefs/BRIEF-E-w1-window.md` |

Each brief is self-contained and names its exhaustive write scope. The lead adds the `BRIDGE_TASK_V1` header at dispatch. Steps 10 and 11 are small enough to brief in a paragraph each; their text above is the brief.

---

## 5. What goes to Fable

One batch, `CUT.md` section 3:
- **Wait for her:** F-1 (date rules bind only the entries they name; hours-apart instead of calendar dates for later kits), F-2 (what the close gaps protect), F-3 (hand gates and desk-final move to "before a look"), F-4 (F0 retires as a filler after R1; a ranked list of product fillers).
- **Proceed unless she objects by Thu 19 Nov 20:00:** F-5 to F-11.
- **Format request:** RL-179 ends with a Register block; scheduling detail that protects no claim is the lead's; rulings for a phase arrive as one batch before its build (F-8).

Nothing in the batch changes a registered estimator, an inclusion rule, a date already run, or a pin.

---

## 6. Should the tooling be rewritten in another language? No

The brief allows a rewrite only if the repository shows it pays for itself before the mid-December paper. It shows the opposite.

| Evidence | Value | Source |
|---|---|---|
| Python under `scripts/` and `joulewise/` on main | 310,996 lines in 364 files | `appendix/code-gates.md`, Part 2 |
| The same on the W1 line and on the campaign pin | 350,680 and 352,105 lines | same |
| All tracked Python on main | 763,220 lines, of which tests 394,584 | same |
| Test functions | 13,060 on main; 15,046 on the W1 line | same |
| What the MBP runs | Commits pinned by hash and admitted by ruling: campaign pins `b4b6aeb19`, `dd206025a`, `2d347f721`; the W1 line at `b2e01464d`. A change to a measured path needs a re-pin, a smoke and a Part C carry (RLD:12676; RL-172b, RL-172c) | `RULES.md` X-12, S-06 |
| Calendar left | About four weeks: the slot session, freeze 2, three qualification dates, W1 and the C and T windows | `RULES.md` section 3.4, 3.5 |

- **The measurement plane cannot be rewritten in the time.** It is about 350,000 lines whose bytes are part of the registration. A port would void every pin, and each new pin costs MBP hours in smokes before it measures anything. The record already shows what byte churn costs: nine changes in 50 hours and 9.9 hours of smokes (`RULES.md` S-06).
- **The control plane is not slow because of its language.** The hours went to prose executed by a model, to shell re-pasted per item, and to rules with no physical reason. The replacement is, by my estimate, about 1,000 lines of stdlib Python in two new files and one edited tool (Briefs A, B, C) reading two JSON files. Another language would add a toolchain to the measurement Mac and change nothing about those causes.
- **What does pay for itself:** deleting. Parking the #800 stack removes about 29,000 added lines from review (#800: 10,989; #799: 7,155; #807: 7,646; #811: 3,166). Archiving the legacy RUN_STATE removes about 20,000 lines from what the magistrate loads.

---

## 7. Risks, and what bounds each

| Risk | Bound |
|---|---|
| The Step 1 item is misread and a counted span is touched | The item says three times that 393, 394, 397 and 398 run as issued; point (e) applies only when the age line is the sole failing line; every other gate in those items is untouched |
| F0 back to back all night is "load without product" | True (RLD:17172), which is why Step 2 puts F2 and hp-02 ahead of it, and F-4 asks to retire it. An empty host produces less |
| A filler delays a counted span | Rule 7 stays. Fillers of one hour replace fillers of two. `expected_ready_by` picks the short one |
| The copy as a debt loses data | Applies only to entries issued from now on; originals are never deleted on the arm path; page at 2 h; counted work holds at 24 h |
| The scheduler disagrees with a ruling | It is read-only until ten consecutive agreements in shadow; a disagreement is a finding about the queue data or the predicate, fixed before cutover |
| Fable objects to a "proceeds" item | Each is a register row or a queue field; reverting one is a one-line commit. None changes data already taken |
| Parking #800 loses work | The branches stay. What is parked is review effort, not code. `mbp_sched.py` implements the part of #800 that survives the cuts (date rules, fit, priority) in a form that is read-only first |
| The lead is away | That is the case this structure is for: no step on the measurement path names the lead |

**Rollback.** Step 1 is one item; a later item that supersedes it restores the old text. Briefs A, B and D add files and change no behaviour until C2. C2 is one line of the prompt.

---

## 8. What Ed is told (one plain mail, after Step 1)

Subject: Process audit done: pacing rules removed from the Mac tonight

- The audit you asked for is finished. It classified every rule that can hold the Mac: 118 rules, of which 39 are pure pacing and another 11 have a pacing part.
- In the last three days the Mac was idle 26 of 72 hours and spent 20 more on a diagnostic run that produces nothing. The causes were a 4-hour spacing rule on that diagnostic, waiting for calendar dates with nothing else ready, and waiting for the Air.
- Tonight: the spacing rule is gone, the Mac no longer waits for a person or the Air for anything, and useful filler runs go ahead of the diagnostic.
- This week: the rules become a short data file and one small program decides what runs next, so a rule without a physical or scientific reason cannot exist. The queue-controller PRs that were stuck at round 10 are parked; they were encoding the rules we removed.
- Four questions went to Fable because they touch the paper. None of them holds the Mac while she answers.
- Nothing needed from you.
- Details: RUN_STATE <n>.
