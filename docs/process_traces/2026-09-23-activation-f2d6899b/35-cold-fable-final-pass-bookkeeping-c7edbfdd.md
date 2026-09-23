# Cold final pass (Fable 5.1), gate-ledger row 7 — candidate c7edbfdd, branch docs/2026-09-23-f2d6899b (activation f2d6899b bookkeeping)

Worktree `/Users/edr/code/wt-f2d6899b-finalpass3`, HEAD `c7edbfdda865f26a1ae7c0048433a51f6ffab806`, clean. Session: one non-interactive session, every probe foreground, no subagents, nothing committed.

## 0. Contamination disclosure

Loaded by the harness before I acted: the user-level `/Users/edr/.claude/CLAUDE.md` (playbook names, the writing standard), the project `CLAUDE.md` at c7edbfdd (bridge policy), and the auto-memory index `MEMORY.md`. The index names activation 5fe5a59b, PR #392, lane A234+A212 and a "live F3 defect"; it says nothing about activation f2d6899b, PRs #393/#394 or lanes A277–A279. I opened no memory file body, no council log, no skill, and no RUN_STATE/TASK_QUEUE text beyond the diff hunks under review. Every claim below is checked against the diff, the records, `gh`, and the code on `origin/main` (`c741678b`).

## 1. Diff scope

`git diff --stat origin/main...c7edbfdd`: 37 files, +3,319/−131. Merge base is `c741678b` = current `origin/main`, so the branch is a clean addition on top of main. Files outside `docs/process_traces/`: `RUN_STATE.md` (+2), `TASK_QUEUE.md` (16 lines, generated rows), `docs/process/state_kernel.json`, `tests/test_gen_state.py`. No decision log, contract, skill, orchestration doc, or code file is touched.

## 2. Check (1): factual claims against primary evidence

Executed this session:

| Claim (RUN_STATE block / kernel) | Evidence | Result |
|---|---|---|
| PR #393 MERGED → `ea4995d5` (A234+A212) | `gh pr view 393 --json state,mergeCommit`: MERGED, `ea4995d5fce9…`, 2026-09-23T20:09:04Z; ancestor of origin/main and of c7edbfdd | TRUE |
| PR #394 MERGED → `c741678b` (A271) | `gh pr view 394`: MERGED, `c741678b47e8…`, 21:20:36Z; ancestor of both | TRUE |
| Release needs census AND `run_night.py` driver probe on the same tick; zero capture from custody on disk; symlink-safe; one-way latch keyed to result.json sha256 | Ruling 16 Q1 F1/F2/F3 text; record 25 §findings and VERDICT (34 adversarial inputs); `scripts/magistrate_watchdog.py:851 _zero_capture_disk_facts`, `:890` on origin/main | TRUE |
| Cold gate ruling 16 "design sound, one bounded round" | Record 16 Q1 RULING: "Sound in shape; one more bounded fix round is the right spend." | TRUE |
| Opus counter-review MERGEABLE; cold Fable final pass MERGE (A234) | Record 24 line 3 "Verdict: MERGEABLE… three deferrable nits"; record 25 VERDICT "MERGE." | TRUE |
| Full replay 6,940 tests, one load-sensitive flake in an untouched module | PR #393 body row 9: 6,940 tests, shard 3 failures=1, `test_run_night.BindSupervisionProcessTests.test_header_plus_one_byte_never_blocks_recv`, module untouched, rerun class 3/3 module 231/231 | TRUE |
| Post-merge hosted matrix SUCCESS (#393) | `gh run list --branch main`: ea4995d5 completed success | TRUE. (c741678b run was `in_progress` at probe time; the block does not claim success for #394.) |
| A271: t0 detection only, refuses above 2 spawns in 10 min, unmeasurable read = not_measured | `corecaptured_loop.py:12-13` WINDOW_S=600, SPAWNS_MAX=2; `night_gate.py:1521` "not_measured"; record 05 ruling (a); ruling 16 Q2(b) | TRUE |
| Arm check: one Wi-Fi cycle, 180 s recount, ≥1 new spawn → one `sudo -n` fseventsd restart then refuse; licensed only on a real arm, nothing loaded, every earlier row passing | `corecaptured_loop.py:14-16` WIFI_OFF_S=8, POST_TOGGLE_WAIT_S=180, POST_TOGGLE_SPAWNS_MIN=1; `evidence_night.py:925` `/usr/bin/sudo -n /usr/local/sbin/joulewise-restart-fseventsd`; `evidence_night.py:1096-1108` licensing guard (nothing_loaded, not rehearsal, all rows pass) | TRUE |
| Entry contract enumerates check's three machine moves; corecaptured row item 7 | `docs/contracts/evidence_night_entry.md:175, 283` on origin/main | TRUE |
| Cold final pass MERGE + delta pass MERGE; registration v4 deferred (record 32 §4 ACCEPT) | Record 32 §4 "ACCEPT the proposal in record 31", VERDICT "MERGE."; record 33 VERDICT present; record 31 is the lead's proposal | TRUE |
| Full replay 6,967/0 (A271) | PR #394 body row 9: 6,967 tests, 0 failures, 0 errors, rc 0 | TRUE |
| Kernel: A234/A212/A271 retired; A277/A278/A279 registered; 233 tasks | kernel `tasks` lacks the three ids, holds the three new ids; `len(tasks)`=233; test comment arithmetic 233−3+3=233 | TRUE |
| A277 goal: nothing writes `zero_capture_evidence`; `zero_capture_successor_allowed` rejects with `missing_zero_capture_evidence` | Ruling 16 Q1 "A finding for the lead" (rg at 4c76ab69; executed bare-row Decision); `arm_retry.py:205-206, 247, 269, 284` on origin/main | TRUE |
| A278: registration table `night_gate.py:55–75` digest-keyed; v3 sha `69321c69…` | `night_gate.py` lines 52–78 on origin/main: `QPE01_PILOT_REGISTRATION_PATH` v3, digest-keyed table with v1/v2 kept byte-identical | TRUE (line span is approximately right: the table spans ~52–78) |
| A278 status_note verbatim quote of record 32 §4 | Record 32 line 95 matches the quoted ruling text | TRUE |
| A279 goal and acceptance | PR #393 body row 9 (exact failure name and rerun counts) | TRUE |
| A276 note: next arm notice must append the corecaptured sentence until A276 lands | Record 32 §4 final sentence | TRUE |
| Records 01–33 present, "mostly verbatim seat and judge outputs" | 33 files; records 02/11/28 open with `claude-codex-report/v1` JSON envelopes; 16/25/32/33 are judge rulings | TRUE (spot-checked, not re-reviewed) |
| "Deferred nits are in records 24, 25, 32 and 33" | 24 §Nits; 25 §5 Should-fix; 32 §6 Should-fix; 33 §3 items 1–2 | TRUE |
| "4158e658 record 01 §4 queue" exists | `docs/process_traces/2026-09-23-activation-4158e658/01-activation-record.md` §4 "Not done this activation (next, after the night)" | TRUE |

Two claims did not verify cleanly:

**C1 (defect, must cure).** `tests/test_gen_state.py` line ~36 (diff line 3776) carries an unfilled placeholder: `A271 landed by PR #394, merge MERGE_SHA_A271.` The true merge commit is `c741678b`. The test passes because the line is a comment, but a bookkeeping PR whose purpose is to record merge SHAs must not ship a placeholder for one of them. The sibling comments for A234 and A212 correctly say `merge ea4995d5`.

**C2 (mis-attribution, should cure).** RUN_STATE block, successor action (2): "settle whether turning Wi-Fi on itself spawns corecaptured (Opus N-3; …)". Record 13 (the A271 Opus contract lens) N3 is a different point: "If arm-to-t0 < ~13 min, pre-toggle spawns remain inside t0's 10-min window and t0 refuses a machine the arm check just cured." Ruling 16 Q2 action 5 records that same N3 as a latent risk. No record in 01–33 and neither PR body contains the "Wi-Fi on itself spawns corecaptured" question (grep for "wi-fi on", "on itself", "power-on", "radio … spawn" across records 10–33 and PR #394 body: no hit). The question itself is sensible and the instruction to log the first live toggle is harmless, but the citation is wrong. PLAUSIBLE that it came from an unrecorded exchange; CONFIRMED that it is not record 13 N3.

NOT EXECUTED: the Gmail launch-email id `1a0cf447f67567e5` (not fetched); the "10:15 → ~14:45 PDT" session times beyond the commit timestamps (c7edbfdd 14:21:09 PDT, consistent); the hosted CI run on `c741678b` (in progress at probe time; the block makes no claim about it); re-review of the seat and judge records' content.

Pre-existing, not introduced by this diff: kernel `latest_report` still points at the 2026-09-22 harvest record (T38t). Out of scope for this verdict; noting it for the successor.

## 3. Check (2): registration only

Executed: `git diff --name-only origin/main...c7edbfdd` outside `docs/process_traces/` lists only RUN_STATE.md, TASK_QUEUE.md, state_kernel.json, tests/test_gen_state.py. No `docs/process/decision_log.md`, no contract, no skill, no orchestration doc. Grep of the added lines for ratif/amend/addendum/decision-log: hits are pointer uses only (D-182, D-183 named as the rules being followed; "registration by the magistrate, not a ruling" in a carried-forward authority label). The A278 status_note carries record 32 §4's ruling text verbatim; that is a record of a cold-pass ruling made at gate time, not a new ruling by this PR. The record 03 proposed decision-log addendum (named in the 5fe5a59b block) is not installed anywhere in the diff. PASS.

## 4. Check (3): mechanical gates

Executed in this worktree at c7edbfdd:

```
/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_state.py --check   → rc=0
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_gen_state.py tests/test_docs_freshness.py
  → 75 passed, 404 subtests passed in 2.13s
```

PASS.

## 5. Check (4): first-use test

**RUN_STATE block.** Read as the handoff a fresh supervisor must act on, the NEXT EXACT ACTION is executable: the queue pointer resolves, the two A277 cure options are spelled out in the lane, and the appended notice sentence is given verbatim. Terms used before or without a gloss, for a technical reader with no project grounding: "agent-free hold" and "agent census" (the deleted A234 kernel text used to gloss census; nothing in this block does), "tick" (the 300 s launchd interval; glossed in NIGHT_HANDBACK, not here), "latched one way", "custody", "arm check", "row" (in "every earlier row passing"), "registration" / "registration v4", "block two", "synthesis 35", "Full replay 6,967/0". None of these blocks the successor's replication, because each is either a pointer into a record that defines it or is a session-log shorthand the successor resolves from the kernel. Two are cheap to gloss and are offered as optional cures below (arm check; tick). The "corecaptured" gloss arrives in the notice sentence, after its first use in the #394 summary; acceptable in a log block, flagged for the explainer docs only.

**A277 ZERO-CAPTURE-EVIDENCE-WRITER-01.** "C5" (a receipt condition row id) is undefined in the goal and acceptance ("harvested zero_capture_evidence C5 block", "a bare C5 row never licenses"). It is defined by the code the goal names (`arm_retry.py:205-206, 267`: rows with `condition_id == "C5"` carrying `measured.zero_capture_evidence`), so an implementer who follows the pointer can replicate; a reader of the queue alone cannot. "Successor" (the one retry night D-182 allows after a zero-capture refusal) is glossed only by "the ~20-minute successor". "Reservation fact on disk" in the acceptance is not defined (the watchdog's `_zero_capture_disk_facts` names them: consumed marker, capture files, chain.started). Named optional cure below.

**A278 QPE01-REGISTRATION-V4-CORECAPTURED-01.** "Registration change", "block two", "pilot re-run" and "sealed-candidate consumers" are internal terms, but the status_note's verbatim ruling text glosses the digest-keyed table and why v3 bytes must not change, which is what an implementer needs. "Handback paragraph" resolves to `NIGHT_HANDBACK.md` via record 33. Replicable from the pointers. No blocking term.

**A279 BIND-SUPERVISION-RECV-STALL-FLAKE-01.** Self-contained: names the test, the error text, the replay shape (eight workers), the rerun counts, and the two exit conditions. No blocking term.

**A276 note.** One plain sentence with the notice text verbatim. PASS.

## 6. Cures

**Mandatory (C1).** In `tests/test_gen_state.py`, replace

```
    # 2026-09-23 activation f2d6899b: A271 landed by PR #394, merge MERGE_SHA_A271. Its t0 check is detection-only (lead ruling record 05, upheld by ruling 16 Q2); registration v4 recording is deferred per final pass record 32 §4.
```

with

```
    # 2026-09-23 activation f2d6899b: A271 landed by PR #394, merge c741678b. Its t0 check is detection-only (lead ruling record 05, upheld by ruling 16 Q2); registration v4 recording is deferred per final pass record 32 §4.
```

Re-run the two test modules after the edit (comment-only change; expected 75 passed).

**Should-fix (C2), RUN_STATE block, action (2).** Replace

```
(2) The first live arm-check Wi-Fi toggle, if one ever fires, must be logged to settle whether turning Wi-Fi on itself spawns corecaptured (Opus N-3; if it does, every toggle ends in a restart and a refusal).
```

with

```
(2) The first live arm-check Wi-Fi toggle, if one ever fires, must be logged to settle whether turning Wi-Fi on itself spawns corecaptured (an open question from this activation, not recorded in any lens; if it does, every toggle ends in a restart and a refusal). Separately, Opus N3 in record 13 stays a recorded latent risk: with an arm-to-t0 lead under about 13 minutes, pre-toggle spawns remain inside t0's 10-minute window and t0 refuses a machine the arm check just cured.
```

If the lead can name the real source of the Wi-Fi-on question, cite that instead of "not recorded in any lens".

**Optional first-use glosses (not blocking).**

- RUN_STATE block, first sentence of the #393 summary: replace "the watchdog releases the agent-free hold early. Release needs the agent census AND a `run_night.py` driver probe empty on the same tick" with "the watchdog releases the agent-free hold early (the hold keeps the headless lead agent off the machine for the night's whole planned span). Release needs the agent census (the scan for running AI-agent processes) AND a `run_night.py` driver probe both empty on the same tick (one 300 s watchdog wake-up)".
- RUN_STATE block, #394 summary: replace "The arm check makes one Wi-Fi cycle" with "The arm check (the checks that run before a night is installed) makes one Wi-Fi cycle".
- Kernel A277 goal, first sentence: replace "nothing writes the harvested zero_capture_evidence C5 block" with "nothing writes the harvested zero_capture_evidence block into the receipt's C5 row (C5 is the receipt condition row for the zero-capture refusal)". Acceptance: replace "any capture or reservation fact on disk blocks" with "any capture or reservation fact on disk (a consumed marker, a capture file under the chain's capture root, or a chain.started record) blocks". Regenerate TASK_QUEUE.md with `scripts/gen_state.py` after any kernel edit.

## VERDICT

**MERGE AFTER NAMED CURES.** Every load-bearing fact in the RUN_STATE block and the new and retired kernel entries is true against the PR states, the merge commits, the records and the code on `origin/main`; the diff is registration only, with no rule, decision or skill ratified or amended; `gen_state.py --check` is rc 0 and the two test modules pass (75 passed, 404 subtests). The one defect is the unfilled `MERGE_SHA_A271` placeholder in `tests/test_gen_state.py` (cure C1, exact text above), which a bookkeeping PR must not ship. The `Opus N-3` citation in the successor action is wrong (cure C2, should-fix). The first-use glosses are optional. Re-run the two test modules after C1; no other gate row is affected.
