# Fresh-model repo review — cross-cutting seat (Opus 5)

**Date:** 2026-09-01. **Lens:** the seams between code, docs, process rulings,
and the paper, plus the newcomer's experience. **Mode:** read-only; no file
outside this one was modified, no measurement command run.

Terms I use below, glossed at first use so this page stands alone:

- **claim-bearing** — evidence the project's own rules allow to be quoted as a
  scientific result. Its opposite here is *diagnostic*: real measurements,
  retained and auditable, but barred from the paper's numbers.
- **the kernel** — `docs/process/state_kernel.json`, a generated JSON file the
  repo names as its authority for choosing what to work on next
  (`state_kernel.json` field `authority` = `AUTHORITATIVE_WORK_SELECTION_STATE`).
- **quiet-mac window / night** — a measurement session on Ed's M3 Max with all
  agent load off; the only way new energy data enters the project.
- **`_v4` / `_v5`** — successive *generations* of the frozen campaign plan.
  `_v4` was Qwen2.5 1.5B vs 7B and will never be collected; `_v5` is Qwen3
  1.7B vs 8B (decision D-164, `docs/decision_log.md:191`).
- **the falsifier / R** — the pre-registered pass-fail number for the paper's
  headline finding: R = corner-widened unguarded floor ÷ point unguarded floor,
  per component per cell, requiring R ≥ 2 (D-165, `docs/decision_log.md:192`).
- **fill session** — the future working session that replaces every `[PENDING]`
  in the frozen paper draft with an issued number.

---

## 1. VERDICT

Yes — this repository can produce a defensible capstone paper in ~10 days, and
the reason is narrow and real: the measurement method in `docs/paper/draft-v1.md`
§2 and Appendix A.3 is *already written to a replication standard* (A.3.3–A.3.7
specify the clock-anchor estimator and pulse fit precisely enough to rebuild
them from the text, with worked arithmetic at `draft-v1.md:549-557` and
`:638`), so what remains is filling numbers into a finished argument rather than
building one. The single biggest thing I would change is that **the two
documents an advisor is told to read first are both stale in ways that
contradict the current campaign** — `PROJECT_STATUS.md` (last substantive
commit `0a216b72`, 2026-08-17) contains zero mentions of `_v4` or `_v5`, and
`README.md:12-22` still describes the 2026-08-20 `_v4` freeze as the live
state — while the frozen paper draft still says Qwen2.5 and `_v4` throughout
(`draft-v1.md:260`; `_v4` ×8, `_v5` ×0). The single biggest thing I would
protect is the **refusal discipline**: the habit of printing a named reason and
stopping rather than producing a number (`draft-v1.md:214-236`, `:300`), which
is the paper's actual contribution and the thing that makes a small dataset
publishable. The adversarial worry — that this project documents instead of
measuring — is *half* true and I state the number plainly: the newest
measurement bundle on disk is `runs_window_metrologyB_20260801/` (2026-08-01),
so the machine has been idle for 31 days while 1,111 commits and 126 merges
landed; but that month bought two findings that would have sunk the paper (a
near-vacuous falsifier, D-165, and a prefill length chosen by extrapolation,
D-166), so the process is earning its keep — it just has no stopping rule.

---

## 2. NEWCOMER PATH

### What the advisor would read first, and what happens

`README.md` is the front door and its first 130 lines are the problem. The
opening glossary (`README.md:3-10`) is genuinely good — seven terms of art
defined before use. Then:

- **`README.md:12-22` ("**Status:**") is stale.** It says the successor
  campaign family "is frozen … and been merged to this main branch
  (2026-08-20)" and that "the readiness re-audit and the plan for that next
  family are in progress." That is the `_v4` state. D-164 (2026-08-28) replaced
  `_v4` with `_v5` and ruled `_v4` is never collected.
- **`README.md:25-58` ("Current activity") is accurate.** I checked it against
  `RUN_STATE.md:13-26`: the merged `_v5` prep, the R ≥ 2 rule, the four-rung
  prompt-length sweep, the fill-registry re-issue, and the "≈ 2026-09-02/03"
  transaction all match. It was refreshed today (commit `3b3839c0`,
  2026-09-01 12:34). One nit: the section header says "last: 2026-09-01" while
  the paragraph inside says "(updated 2026-08-31)".
- So the reader meets a **contradiction eight lines apart** — a superseded
  status paragraph immediately above a correct one — with nothing marking which
  is which.

Then `README.md:59-180` ("Current State") is a 120-line archaeological deposit:
Phase 1/Phase 2 framing from July, the voided Qwen2.5 corpus, a table of three
VOIDED unmatched models, D-070/D-075 extension agendas, NVIDIA and Jetson
gating, AXI-SA/SB/SC verdicts. Every sentence is *true*; collectively they bury
the one fact the advisor needs, which is that **no claim-bearing number exists
yet** — a fact stated only in `CLAIMS_STATUS.md:88`: "§1 VALID — minted,
mainline, citable: **NONE at this checkpoint.**"

### Where they get lost

1. **Ten status-shaped files at the repository root.** `README.md`,
   `PROJECT_STATUS.md`, `RUN_STATE.md`, `STATUS.md`, `CLAIMS_STATUS.md`,
   `WINDOW_STATUS.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`, `FREEZE-FCM01.md`,
   `STOPPED-FCM01.md`, plus two stray tracked data artifacts
   (`df-ph-decode-floor-mint1.json`, `df-ph-decode-floor-mint1.single_count.txt`,
   last touched 2026-07-30, `f1885626`). Nothing tells a newcomer the ranking.
2. **`STATUS.md` is a trap.** It is 10 lines of stream-worker scratch — "# S14
   stream status", "PR #228 open", "Do NOT merge", and a path into a
   `/private/tmp` scratchpad. It was last written by commit `1f046cd9`, which is
   *the merge of #228*. A file named STATUS.md at the repo root tells the reader
   not to merge a PR that the same commit merged.
3. **`PROJECT_STATUS.md` is the designated advisor document and is two weeks
   and six binding decisions behind.** `README.md:249-251` says "**Advisor /
   high-level view:** `PROJECT_STATUS.md` is the standalone status, plan, and
   architecture document — start there." Its own header
   (`PROJECT_STATUS.md:3-6`) claims it works "without requiring any other
   file." It contains zero occurrences of `_v4` or `_v5`, still narrates the
   D-117 alpha/beta/gamma window plan, and at `:605-609` asserts "Window A's
   software gates are satisfied, its first floor corpus is published, and the
   window remains open" — a corpus `README.md:133` describes as "a permanently
   voided historical record under D-078."
4. **`RUN_STATE.md` is 5,845 lines.** `AGENTS.md:42-44` says to read its
   `ACTIVE_STOP_CARD` first, and `docs/orchestration.md:117` says that card
   sits "at the top of `RUN_STATE.md`". It is at `RUN_STATE.md:5037`. The
   top-of-file T-block summaries (T29, T28b, T28, T27c…) are excellent and are
   the real intake surface; the other 5,800 lines are session history that has
   never been rotated out.

### The one page that is missing

**A two-page "What this project measured, what it found, and what it cannot
say" for the advisor** — dated, superseding `PROJECT_STATUS.md`'s status half,
containing exactly: the one-sentence research question; the one-sentence answer
state ("no claim-bearing data yet; first claim-bearing night ≈ 2026-09-02/03");
the negative result that is already retained and real (37 of 50 prefill phases
unresolvable, `draft-v1.md:247`); the three diagnostic ratios that motivate the
whole paper (10.92, 5.92, 7.02 at `draft-v1.md:103`); the one honest
limitation (the pulse-to-inference transfer is assumed, not tested,
`draft-v1.md:294`); and the calendar. Everything else the advisor needs is
already in `draft-v1.md`. Rivoire will recognise the JouleSort boundary
discipline in `draft-v1.md:336` immediately; she should not have to excavate
`README.md:59-180` to get there.

---

## 3. WOULD CHANGE — ranked

### 1. Re-tense the frozen paper draft from `_v4`/Qwen2.5 to `_v5`/Qwen3 — before the data lands, not during the fill

**Observation.** `docs/paper/draft-v1.md` mentions `_v4` eight times and `_v5`
zero times. It says the demonstration "will compare 4-bit Qwen2.5 7B with 1.5B"
(`:260`), that "Nothing in the frozen `_v4` campaign tests that transfer"
(`:294`), "For each `_v4` prefill and decode cell" (`:356`), and the held title
block at `:2-7` is gated on "`_v4` ISSUES". D-164 (`docs/decision_log.md:191`)
repinned the pair to `mlx-community/Qwen3-1.7B-4bit` /
`mlx-community/Qwen3-8B-4bit` on 2026-08-28. Worse, §6's subsection "Why 256
prompt tokens were selected" (`:266-272`) derives 256 from Qwen2.5 128-token
history (5.809930 J → 11.619860 J), while D-166 as amended
(`docs/decision_log.md:193`) replaced that choice entirely with a *measured*
four-rung sweep over 512/1024/2048/4096
(`scripts/select_g2a_prefill_length.py:17`). That whole subsection now argues
for a number the ruling has retired.

**Why it matters for the paper.** These are not cosmetic. A reviewer who reads
§6 sees a prompt length justified by extrapolation from a model pair the study
no longer uses. The retensing sheets that would fix this exist
(`docs/paper/round7/retensing-plan.md`, `structural-edits.md`) but were **PARKED
on 2026-08-31** after a fresh adjudication seat returned NOT USABLE — 3
blockers, 13 should-fixes, 59/81 blocks passing
(`docs/process_traces/2026-08-31-registry-v5/12-PARK-DISPOSITION.md:1-8`). The
park hands that worklist to the fill session
(`12-PARK-DISPOSITION.md:10-28`), which is the single most time-pressured
session in the project.

**First step (≤1 day).** Do not reopen the parked adjudication. Instead, take
only the *mechanical* half: a scripted find-and-replace pass over `_v4`→`_v5`,
Qwen2.5→Qwen3 with the two model identities, plus deletion of §6's 256-token
subsection replaced by three sentences naming the G2-a selection rule and its
record hash. Adjudicate that diff with one fresh seat on the diff alone. Leave
the 3 pedagogy blockers to the fill session as ruled.

**Cost/risk.** Low cost. Risk: the park disposition says "No further pre-data
editing rounds"; this must be run as *executing D-164/D-166 into the draft*,
not as a new round, and the magistrate should say so in writing.

**Timing.** PRE-CAMPAIGN. Every hour of this done now is an hour not spent
during the fill.

---

### 2. Make the two advisor-facing pages true, and delete the decoys

**Observation.** `PROJECT_STATUS.md` last substantive commit `0a216b72`
(2026-08-17); zero `_v4`/`_v5` mentions; `:605-609` asserts a published,
open Window A. `README.md:12-22` is the 2026-08-20 `_v4` status. `STATUS.md` is
a merged-but-stale stream note. `WINDOW_STATUS.md` (last touched `1891ced8`,
2026-08-24) still narrates the `_v3`-lapsed / `_v4`-transaction hazard.
`CLAIMS_STATUS.md` (last touched `b7adb14d`, 2026-08-20) names the next
claim-state sequence as "Phase-2 re-freeze → re-audit → READY-candidate council
→ the alpha/beta/gamma windows" (`:56-58`) — which is not the sequence that
runs this week (G2-a → desk day → transaction → collection).

**Why it matters.** The advisor meeting is ~1 week after the transaction. These
five files are what she sees if she opens the repo. A capstone defended against
its own stale status pages is a bad afternoon.

**First step (≤1 day).** (a) Replace `README.md:12-22` with two sentences
pointing at the Current-activity block. (b) Delete `STATUS.md` and the two
stray `df-ph-decode-floor-mint1.*` root artifacts. (c) Add a dated
`SUPERSEDED — see RUN_STATE T29` banner to `WINDOW_STATUS.md` and
`CLAIMS_STATUS.md` rather than rewriting them. (d) Write the missing advisor
page (§2 above) and repoint `README.md:249-251` at it.

**Cost/risk.** Half a day. Risk: `tests/test_docs_freshness.py:209-212` will
fail on any edit that removes the pinned `PROJECT_STATUS.md` sentences — see
SEAM 4; that test must be amended in the same commit.

**Timing.** PRE-CAMPAIGN (b, c cost minutes); the advisor page can be
POST-CAMPAIGN if it must be, but not post-meeting.

---

### 3. Reconcile the kernel with the night that is about to happen

**Observation.** `docs/process/state_kernel.json` declares itself
`AUTHORITATIVE_WORK_SELECTION_STATE`, is stamped `updated: 2026-08-28`, and
carries one active global gate, `WINDOW-COUNCIL-GATE`, whose summary reads: "No
quiet-mac task may start or resume after the 2026-08-15 NOT-READY verdict."
Its 13 `quiet_mac` tasks are `D117-W-ALPHA`, `D117-W-BETA`, `D117-W-GAMMA`,
`MET-WINDOW-C-01`, `P2-010`, `P2-012`, `P2-019`, `P2-020`, `P2-046B`,
`P2-047B`, `PIPELINE-SMOKE-LIVE-01`, `T3-CHAR-PAIR-01`, `TRANSFER-FIDUCIAL-01`
— all `_v3`/Qwen2.5-era. The string `Qwen3` does not appear in the kernel at
all, and neither does `G2-a`. Meanwhile `RUN_STATE.md:25-26` says "NEXT MACHINE
STEP unchanged: G2-a evening → desk day → transaction ≈ 09-02/03."

**Why it matters.** The gate's own clearance rule is recorded (D-149,
`docs/decision_log.md:172`, clause 1: a standing READY-candidate council verdict
clears it). If the imminent night runs with no kernel row and the gate still
showing NOT-READY, then either the kernel is not authoritative — in which case
the repo's stated work-selection mechanism is decorative — or the night is
being selected around its own gate. For a paper whose contribution is
*refusing to proceed when a gate fails*, that is the worst possible internal
inconsistency to have on the record.

**First step (≤1 day).** Add the G2-a row (and the `_v5` transaction row) to the
kernel with lane `quiet_mac`, and either record the `WINDOW-COUNCIL-GATE`
clearance receipt per D-149 or amend the gate text to say what it now fences.
Regenerate; the kernel is generated, so this is a source-side edit plus
`scripts/gen_state.py`.

**Cost/risk.** Hours. Risk of doing nothing: an auditor (or Rivoire) finds the
project's own gate open at the moment of first claim collection.

**Timing.** PRE-CAMPAIGN — specifically, before G2-a.

---

### 4. Close the loop on the falsifier: name who computes R, and when

**Observation.** The paper's headline test is R ≥ 2 per component per cell
(D-165, `docs/decision_log.md:192`; `draft-v1.md:185` describes the falsifier
as testing "that exact per-component linear corner maximum against the guarded
point-only value"). The criterion is minted into the campaign pack —
`configs/campaigns/d117_contrast_v5/generate_configs.py:496-599`, with
`DOMINANCE_THRESHOLD = 2.0` at `:497` and `dominance_criterion` injected at
`:587` — and golden-tested at `tests/test_d117_contrast_v5_pack.py:63,88`. But
**`dominance_criterion` has zero occurrences under `joulewise/` and zero under
`scripts/`** (verified by `grep -rn`). The analysis engine still evaluates the
*old*, D-165-declared-near-vacuous predicate
`admissible_set_uncertainty_dominates_point_floor`
(`joulewise/detection_floor.py:806`, consumed at `:848`, `:3296`, and
`joulewise/floor_extraction.py:89`).

This is not a hidden hole — `docs/paper/results-fill-registry.md:235-255` marks
R and R_cm as `DERIVE` (fill-time derivations from the emitted
`corner_widened_unguarded_floor_j` / `unguarded_floor_j` fields at
`joulewise/floor_extraction.py:1386,1531`), and the renderer that would perform
them is a registered but unbuilt row: `RENDERER-V5-SUCCESSOR-01`, "Lead-owned,
post-G2-a (41 keys unresolved until the selection record)"
(`docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:68`), with
`docs/paper/round7/fill-checklist.md:7-9` stating the current
`scripts/render_results_fills.py` "is not fill authority for renamed rows and
must fail closed."

**Why it matters.** The single number the paper's conclusion turns on will be
computed, for the first time ever, by a program that does not yet exist,
during the fill session, under deadline. Every other number in the paper has a
replay fence (`scripts/check_paper_replay_fence.py`, 43/43 at
`draft-v1.md:77,82`); this one has a queue row.

**First step (≤1 day).** Build the R and R_cm derivation *now* against the
existing fill-rehearsal fixtures (`docs/paper/fill-rehearsal/` already contains
`dominance-reproduced-*` and `dominance-not-reproduced-*` floor and extraction
JSONs — both branches of the outcome). It needs no `_v5` data: it needs the two
already-emitted floor fields and the registered replay rule. Ship it with the
two rehearsal fixtures as red/green tests.

**Cost/risk.** One Sol day. Risk of deferring: if R comes out < 2 on real data,
the paper's headline withdraws — and Ed will want to know that on collection
night, not during the fill.

**Timing.** PRE-CAMPAIGN. This is the highest-value pre-campaign engineering
item in the repo.

---

### 5. Fill the two `[PENDING]`s that are already derivable at the desk

**Observation.** `draft-v1.md:256` — inside the paper's one *already-retained*
result, the short-prefill negative — carries two holes: "for this bundle it is
[PENDING] (DIAGNOSTIC-ERA VALUE: sampling-record interval width for
`p2015-df-ph-decode-abs-r03`)" and the matching median record spacing. The
surrounding paragraph exists specifically to teach the reader not to confuse
record *width* with record *spacing*, then declines to state either.

**Why it matters.** This is the paper's strongest currently-defensible passage
— a real negative result, 37 of 50, from retained data. Leaving two numbers
blank in a pedagogical passage whose whole point is those two numbers is the
first-use failure the writing standard exists to prevent. Neither depends on
`_v5`.

**First step (≤1 day).** Derive both from the retained bundle and add them
under the existing replay fence so they are mechanically checked like the other
43 values.

**Cost/risk.** Hours. No risk.

**Timing.** PRE-CAMPAIGN.

---

### 6. Turn on branch protection

**Observation.** Continuous integration is genuinely strong: `.github/workflows/ci.yml:3-6`
triggers on every push to `main` and every pull request; the four ordinary
shards plus two exclusive jobs run the complete discovered module set on Python
3.11 and 3.14, and `tests/test_shard_tests.py:57,64-66` proves the shard
partition equals `unittest discover -s tests` with no duplicates — so a module
cannot silently fall out. 19 of the last 20 `main` runs are green; all recent
failures are on feature branches. **But `gh api
repos/:owner/:repo/branches/main/protection` returns `404 Branch not
protected`.** No check is required at the merge button.

**Why it matters.** The project grants agent-side self-merge under a review
gate. The one mechanical backstop that does not depend on an agent remembering
the gate is not switched on. Given 126 merges since 2026-08-01, the exposure is
real even though the record is clean.

**First step (≤1 day).** Require the `test` matrix and the two exclusive jobs
on `main`. Ten minutes of settings.

**Cost/risk.** Trivial cost; the only risk is a slower merge when CI is slow
(runs range 17 m–1 h 33 m).

**Timing.** PRE-CAMPAIGN.

---

### 7. Put the actual operating model into a tracked file, and rotate `RUN_STATE.md`

**Observation.** `docs/orchestration.md` is described at `:5-6` as "the single
in-repo description of that process." Its worked example is the 2026-07-07/08
session (`:292-308`); its topology history stops at C-010, 2026-07-08
(`:279-283`). The magistrate / lieutenant / cold-gate topology that has
governed since 2026-07-27 — and that appears 201 times in
`docs/decision_log.md` — appears in `docs/orchestration.md` exactly once, as
the word "lieutenant" inside a D-129 amendment note at `:38`. The governing
text lives only in `CLAUDE.local.md`, which is untracked and private.
Separately, `RUN_STATE.md` is 5,845 lines with its `ACTIVE_STOP_CARD` at
`:5037` while `docs/orchestration.md:117` says that card is "at the top."

**Why it matters.** Two things a capstone can be asked to defend are *how the
work was produced* and *whether that process is reconstructible*. The in-repo
answer is a month and a half out of date. This is also a mundane operational
risk: an agent following `AGENTS.md:42` looks for the stop card at the top and
finds T-blocks.

**First step (≤1 day).** Add one tracked section to `docs/orchestration.md`
describing the current three-seat topology and its mandatory escalation
triggers (a summary, not a copy of Ed's private notes), and move the stop card
to the top of `RUN_STATE.md` with everything before T25 archived to
`docs/run_reports/`.

**Cost/risk.** Half a day, delegable. Risk: none, if the private/tracked split
is respected.

**Timing.** POST-CAMPAIGN for the orchestration section; the stop-card move is
PRE-CAMPAIGN and takes minutes.

---

## 4. WOULD KEEP — five things a newcomer would simplify away and must not

1. **The refusal machinery, all of it.** `draft-v1.md:214-236` and `:300`: a
   `REFUSED` comparison is the paper's result, not its failure. This is what
   makes a one-machine, small-n study publishable, and it is exactly what an
   efficiency-minded reviewer would call over-engineering. Note that D-161
   (`docs/decision_log.md:188`) already pruned the *wrong* kind of fail-closed
   — operator-only custody policing — while keeping physics, evidence and
   pre-registration fail-closed. That line is correctly drawn; do not move it
   again.

2. **Appendix A.3.** Fifty pages of algorithm specified to the constant, with
   worked arithmetic (`draft-v1.md:549-557`), the model condition stated
   because the containment claim depends on it (`:480`), and an explicit note
   that the printed endpoints will not reproduce the printed sum (`:557`).
   This is the single most defensible artifact in the repository and the thing
   a metrologist will respect. A reviewer will tell you to cut it; put it in a
   supplement, do not delete it.

3. **The replay fence.** `scripts/check_paper_replay_fence.py` re-derives 43
   fenced literals from primary bytes and fails closed on a reworded anchor or
   dropped row (`draft-v1.md:77`, `:82`). Most papers have no mechanism that
   catches a number drifting away from its evidence. Extend it (item 4 above);
   never relax it.

4. **The sharded-but-complete CI partition.** `tests/test_shard_tests.py:57,64-66`
   asserts the union of shards equals the discovery set. Sharded suites almost
   always leak modules; this one provably cannot. Also keep the 21
   structurally-blocked tests being *counted* rather than deleted
   (`tests/test_s0_blocked_enumeration.py:82-88` pins the census at exactly 21,
   all `STRUCTURAL-BLOCKED`) — a known, counted skip is honest; a deleted test
   is not.

5. **The glossary-before-use habit.** `README.md:3-10`, `PROJECT_STATUS.md:8-15`,
   `CLAIMS_STATUS.md:20-28`, `WINDOW_STATUS.md:18-25`, and
   `docs/research_question_coverage-2026-08-28.md:7-9` each define their terms
   of art before using them. It reads as repetitive; it is why an outsider can
   read any one of these cold. Keep it even when consolidating files.

---

## 5. SEAMS — flagged, not fixed

**SEAM 1 — the paper describes a campaign that will never run.** Draft says
`_v4`, Qwen2.5 7B vs 1.5B, 256-token prefill (`draft-v1.md:260`, `:266-272`,
`:294`, `:356`, and the held title block `:2-7`). Rulings say `_v5`, Qwen3 8B vs
1.7B (`docs/decision_log.md:191`), prefill selected from the 512/1024/2048/4096
ladder (`docs/decision_log.md:193`;
`scripts/select_g2a_prefill_length.py:17`). The retensing sheets that would fix
this are PARKED (`docs/process_traces/2026-08-31-registry-v5/12-PARK-DISPOSITION.md`).
Severity: highest. This is the seam most likely to reach the advisor.

**SEAM 2 — the falsifier's gate is registered but has no reader.**
`dominance_criterion` and `attribution_dominance_ratio.v1` exist only in
`configs/campaigns/d117_contrast_v5/generate_configs.py:496,514,587` and its
golden test; zero hits under `joulewise/` or `scripts/`. Production analysis
still runs the superseded near-vacuous predicate
(`joulewise/detection_floor.py:806`, consumed at `:848`, `:3296`,
`joulewise/floor_extraction.py:89`). The derivation is *registered* as fill-time
`DERIVE` (`docs/paper/results-fill-registry.md:235-255`) and the renderer is a
queued unbuilt row (`docs/process_traces/2026-08-27-t26/WAVE-ROWS.md:68`), so
this is a schedule seam rather than a soundness hole — but see SEAM 3.

**SEAM 3 — the RQ coverage map cites the old predicate as the new one's
implementation.** `docs/research_question_coverage-2026-08-28.md:61` describes
the D-165 ratio falsifier and then cites, as its "implementation:"
`joulewise/detection_floor.py:689-718` and `:735-841`. Those line ranges are
`_floor_estimate` and the corner-max helper feeding
`admissible_set_uncertainty_dominates_point_floor` — the predicate D-165
replaced *because it was near-vacuous*. A reader checking the RQ map's citation
would conclude the falsifier is implemented in production code. It is not.

**SEAM 4 — a CI test pins a sentence the decision log has superseded three
times.** `tests/test_docs_freshness.py:210` requires the exact string `"Window
A's software gates are\nsatisfied"` in `PROJECT_STATUS.md`'s current section.
That sentence continues (`PROJECT_STATUS.md:605-606`): "…its first floor corpus
is published, and the window remains open." But `README.md:133` calls that
corpus "a permanently voided historical record under D-078"; D-110 made mint #1
retroactively non-claim-bearing (`CLAIMS_STATUS.md:88-92`); and D-117 retired
the whole Window-A path. The test now actively prevents removing a claim the
project has withdrawn.

**SEAM 5 — the kernel fences a night that RUN_STATE schedules.** `state_kernel.json`
(`updated: 2026-08-28`, `authority: AUTHORITATIVE_WORK_SELECTION_STATE`) holds
`WINDOW-COUNCIL-GATE` active over all `quiet_mac` selection, with no G2-a row
and no `Qwen3` string anywhere in the file; `RUN_STATE.md:25-26` schedules the
G2-a evening for tonight-ish.

**SEAM 6 — `STATUS.md` forbids the merge that wrote it.** `STATUS.md:2-3` says
"PR #228 open" and "Do NOT merge"; its last commit is `1f046cd9`, the merge of
#228.

**SEAM 7 — the paper's "first plotted measured data" is not in the paper.**
`README.md:39-41` describes the 118-excursion decomposition as "the paper's
first plotted measured data" and `docs/paper/figures/fig4_edge_excursions.svg`
exists (2026-08-30, PR #240). `docs/paper/draft-v1.md` contains no reference to
Figure 4. Correct under the freeze — but the README states as landed something
the frozen draft does not yet carry.

**SEAM 8 — the "decisive production proof" has been unrunnable for two weeks.**
`.github/workflows/d117-production-proof.yml:4-13` is `workflow_dispatch` only,
with a header recording that automatic triggering was deferred 2026-08-16 on
fixture drift (`AttributeError: scripts.mint_floor_artifact has no
STACK_IDENTITY_DOMAIN`); the last green run is the 2026-08-11 dispatch.
`TASK_QUEUE.md:139` records the deferral, and A62 `WO-PROOF-RUNNABILITY-REPAIR`
remains open (`TASK_QUEUE.md:644`, `:773`). The proof that discharged D-130
cannot currently be re-run at `main`.

**SEAM 9 — scheduling data drifted past its own provenance claim.**
`scripts/test_timings.json` measures 140 modules; discovery now finds 168, so
28 modules take the 29.834 s fallback weight, and the file's own text claiming
"140 of the 141 currently discovered modules are measured" is false by 27. The
two exclusive-job asserts (`ci.yml:130-133`, `:196-204`) compare the file with
itself, so nothing fails. Low severity; noted because it is the same
decided-≠-done shape as SEAM 2.

**SEAM 10 — the in-repo process description is not the process.**
`docs/orchestration.md` says it is "the single in-repo description" (`:5-6`) and
stops at 2026-07-08 topology; the governing magistrate/lieutenant/cold-gate
model appears 201 times in `docs/decision_log.md` and once, glancingly, in
`docs/orchestration.md:38`.

---

## 6. OPEN QUESTIONS FOR THE OWNER

1. **Is the fill session allowed to be two sessions?** The park disposition
   loads the fill session with 3 blockers + 13 should-fixes + a lint gap
   (`12-PARK-DISPOSITION.md:10-28`) *before* any number is inserted, and item 1
   above adds a retensing pass. If the answer is "no, one session," I would drop
   items 1 and 5 from pre-campaign and accept a rougher draft; if "yes," the
   mechanical retensing should land this week. **This changes the ranking of
   items 1 and 5.**

2. **Must R be computed by a program before collection night, or is a
   spreadsheet acceptable for the first look?** If Ed wants to know on the night
   whether the headline survives, item 4 is mandatory pre-campaign. If the first
   look can wait for the renderer, item 4 drops to third. **This is the single
   biggest scheduling fork I found.**

3. **What clears `WINDOW-COUNCIL-GATE` for `_v5`?** D-149
   (`docs/decision_log.md:172`) names a standing READY-candidate council verdict
   as the clearance. Has one been recorded for the Qwen3 pack, or is the gate
   understood as fencing only the retired `_v3` rows? The answer decides whether
   item 3 is a five-minute kernel edit or a required council.

4. **Is `PROJECT_STATUS.md` still the advisor's document, or has the paper draft
   replaced it?** If Rivoire now reads `draft-v1.md` directly, the right move is
   to demote `PROJECT_STATUS.md` to an internal archive and write the short
   advisor page; if she still monitors via `PROJECT_STATUS.md`, it needs a real
   rewrite, which is a day, not an hour.

5. **What is the stopping rule for pre-registration rounds?** D-165 and D-166
   were both genuine saves found by cold gates in the last week. They were also
   both new preconditions on a night that has now not happened for 31 days
   (last data: `runs_window_metrologyB_20260801/`). If a cold gate on 2026-09-02
   produces a D-167 with a new precondition, does the night still run? I would
   want that answered *before* G2-a rather than at 22:00 that evening.
