# 61 — Opus counter-review of PR #338 (gate row 6, contract lens; candidate 8afd6ade, the pre-fix head; delivered 2026-09-14 ~17:07 PDT)

Verbatim final report of the Opus 5 subagent (read-only git object reads; scratch under /tmp).

---

## Counter-review — PR #338 (D-181), candidate `8afd6ade` — contract lens

**VERDICT: AMEND** — fidelity to directive #337 is high and restraint holds (no rule text, doctrine or prior decision-log entry is amended; record 55 is byte-identical to the live issue). Two should-fix precision defects and one PR-body gap; no blockers.

### Restraint / fidelity baseline (no finding)
- `docs/process_traces/2026-09-13-activation-24b9d3dd/55-ed-directive-337-verbatim.md:7-27` is **byte-for-byte identical** to `gh issue view 337 --json body` fetched live this session (2955 bytes both, `IDENTICAL`).
- `docs/decision_log.md` diff is a **pure 54-line insertion**; D-180's text (`11738-11781`) is untouched. No `docs/process/*.md`, runbook, skill or watchdog file is in the diff. The fourth D-180 lane (`REMOTE-CONTROL-BETWEEN-WINDOWS-01`) is byte-identical to base — correct, #337 names only three.
- Shape matches D-180 exactly: `## D-NNN: … (Ed, date)`, `**Status:**` with verbatim pointer + "decided ≠ done" + "Forcing problem:", bolded numbered clauses each naming its lane, trailing "…recorded with the rulings" paragraph (`Housekeeping` ↔ D-180's `Standing direction`).
- Clause-by-clause substance vs record 55: ruling 1 keeps every fence verbatim in list form; ruling 2 adds only "No lane: this clause changes no text" (restraint, not rule); ruling 3 adds only the factual "(lane `ed_external`)". Nothing normative is added.
- **"Forcing problem" is factual and smuggles no rule.** `RUN_STATE.md:23` (T38q third addendum) confirms both halves: the 09-13 plan root was *"the refused 09-13 plan root"* and *"the census never cleared … through the 06:05 cutoff"* on 09-14 morning, with the successor prepared for *the next* night (`n1-20260916`). The trailing "Ed rules that the spacing was never a scientific requirement" restates ruling 1, sourced.
- **"This supersedes the D-180 sequencing note 'after G2-a instrument validation' on those three rows"** (`docs/decision_log.md:11813`) is a faithful and *scoped* consequence: "top of the queue … immediately after tonight's harvest" and "after G2-a instrument validation" cannot both hold, and the supersession is asserted inside D-181, not written into D-180.
- Gate rows as recorded match the repo: `.github/pull_request_template.md:15` "Apex Fable code-reading diff gate … never skipped or downgraded"; `:20` "Magistrate terminal review … (final head sha); not delegable". No contradiction.

### Findings

**1. should-fix — "so the kernel enforces the order" overstates what the kernel enforces.**
`docs/decision_log.md:11814-11816`: *"the other two are blocked on their predecessor by a hard start dependency and take rank 0 in the bookkeeping that closes it, so the kernel enforces the order."*
The kernel enforces only the **negative** half (a successor cannot start first). It does not enforce that the successor becomes the next head — that depends on a future manual rank edit the sentence itself discloses. Simulated on the candidate kernel (delete `INSTALL-WINDOWS-MULTI-01`, flip its dep to `satisfied`, unblock `ARM-RETRY-CLASS-01`):
```
after INSTALL closes, selectable: ['ED-DATES-01', 'V5-G2A-PREFILL-PROBE-01', 'WO-LAUNCH-BINDING']
```
`ARM-RETRY-CLASS-01` sits at rank 172; `_selectable_in_lane` (`scripts/gen_state.py:500-505`) returns the lowest-rank ready task, so `WO-LAUNCH-BINDING` (rank 1) becomes the agent head, not the promoted successor. Given this repo's own "ruled-not-installed" history, a binding entry should not claim mechanical enforcement it does not have.
*Closure:* replace "so the kernel enforces the order" with "so the kernel refuses a successor before its predecessor closes; the head position is carried by the rank edit in that closing bookkeeping."

**2. should-fix — "immediately after tonight's harvest and the §2.5 outcome action" is encoded only in prose; the lane is selectable now.**
`docs/process/state_kernel.json` gives `INSTALL-WINDOWS-MULTI-01` `rank 0`, `status "queued"`, no start dependency. Computed against the candidate kernel:
```
selectable: ['ED-DATES-01', 'INSTALL-WINDOWS-MULTI-01', 'V5-G2A-PREFILL-PROBE-01']
INSTALL-WINDOWS-MULTI-01 agent rank 0 queued p1_phase_gate
```
i.e. the machine-readable source of truth says an activation may start this lane **before** the 09-15 harvest, which the directive conditions it on. The start condition lives only in `status_note` prose, and `RUN_STATE.md` is declared "Source of truth for work selection: state kernel".
The repo's idiom for exactly this is a hard start **event** dependency, and it is live, not theoretical:
- `NIGHT-REHEARSAL-01` carries `('start','hard','satisfied','REHEARSAL-20260911-HARVESTED')` and `('start','hard','satisfied','POST-WATCHDOG-REHEARSAL-20260909')` — harvest events flipped on completion;
- the sibling D-180 lane `REMOTE-CONTROL-BETWEEN-WINDOWS-01` encodes its own "sequenced after" as `('start','hard','pending','G2A-FIRST-WINDOW-01')`;
- `DOC-010`'s two hard start events are protected by an explicit invariant (`scripts/gen_state.py:409-419`), and `AUD-WO-033` is the `scope:"close"` variant.
*Trade-off named honestly:* invariant 3 (`scripts/gen_state.py:387-396`) would then force `status:"blocked"`, so the agent head would read `WO-LAUNCH-BINDING` until the event flips — which is the truthful state for the next ~12 h, and would also make the three test pins in finding 4 unnecessary until then.
*Closure:* add `{kind:"event", scope:"start", strength:"hard", state:"pending", target:"N1-20260915-HARVESTED-AND-2.5-ACTION"}` to `INSTALL-WINDOWS-MULTI-01` (status → `blocked`), or strike "immediately after tonight's harvest" from the entry as a mechanically-unbacked condition. I would require one or the other, not both.

**3. nit — insertion point re-parents a pre-existing H3 and breaks the log's chronological append.**
D-181 is inserted at `docs/decision_log.md:11783`, ahead of `### D-124 dated addendum — 2026-09-13` (`:11837`, the file's last heading). Two consequences: a 2026-09-14 entry now precedes a 2026-09-13 addendum at the tail, and the D-124 addendum — the log's only `###` heading, every other addendum being `## D-NNN dated addendum` — now nests under "Windows run whenever the machine is quiet" instead of under D-180. The H3 anomaly predates this PR; appending D-181 at end-of-file would preserve chronology and leave it where it was. Not load-bearing.

**4. nit — the three `tests/test_gen_state.py` pins are the minimum and the comments are accurate, with one asymmetry.**
Edits at `:1299-1301`, `:1352-1353`, `:1513-1514` are the only test changes in the diff; each carries a dated `D-181 cl.1` comment, and `:1300`'s claim "ahead of `WO-LAUNCH-BINDING` (rank 1)" is exactly right. `grep -rn WO-LAUNCH-BINDING tests scripts` returns only these two comments plus the unrelated retired-head list at `:184`, so no fourth site was missed. Bench-verified on a `git archive` copy of the candidate: `scripts/gen_state.py --check` rc 0, `44 passed, 21 subtests passed`.

**5. nit — `ARM-CENSUS-IDLE-INTERACTIVE-01`'s status note drops the supersession sentence its two siblings carry.**
`INSTALL-WINDOWS-MULTI-01` ("Supersedes the D-180 sequencing note 'after G2-a instrument validation'") and `ARM-RETRY-CLASS-01` ("Supersedes the D-180 sequencing note") both record it; the third row's note stops at "…takes the agent lane's rank 0 in that bookkeeping." The authority pointer covers it, so this is cosmetic consistency only.

**6. nit / observation — the promotion is invisible where a restarting agent looks first.**
The agent lane has eight `active` tasks, so `render_run_state` takes the CONTINUE branch (`scripts/gen_state.py:586-591`) and never emits a READY head; `RUN_STATE.md` §Restart `### [AGENT]` shows eight CONTINUE rows and no mention of `INSTALL-WINDOWS-MULTI-01`. The promotion is visible only in `TASK_QUEUE.md` (row `A0`). This is pre-existing generator behaviour, not a defect of this PR, but it means "top of the queue" is not what a restart reads. Worth one sentence in the merge bookkeeping.

**7. should-fix (PR-level, not diff) — PR #338's body carries no twelve-row gate ledger.**
`gh pr view 338 --json body` returns Summary / Evidence / Residual risk only, with *"Gate ledger to follow before merge."* This is precisely the defect Ed flags on PR #330 in the same directive (record 55:25, *"its body still lacks the gate ledger"*), and `.github/pull_request_template.md:3` makes the advisory `gate-ledger` check report it as a defect. Everything else the body asserts is corroborated: 174 kernel rows before and after (verified), `--check` rc 0, 44 tests OK, three test sites, clause-2 changes no text, no production code in the diff. One loose phrase: "status notes naming the start condition" is true of `INSTALL-WINDOWS-MULTI-01` only; the other two name their predecessor, not the harvest.

*Closure for the PR:* fix findings 1 and 2 (one sentence + one dependency edge), fill the ledger, and the entry is a faithful, restrained recording of #337.

### Commands run (read-only; worktree never mutated)
```
git -C /Users/edr/code/JouleWise-wt-bk-24b9d3dd show 8afd6ade --stat          → 6 files, +139 −34
git -C … diff --word-diff=plain -U0 6d2d62d8 8afd6ade -- TASK_QUEUE.md RUN_STATE.md
git -C … show 8afd6ade:docs/decision_log.md | sed -n 11738,11840p
git -C … archive 8afd6ade | tar -x -C /tmp/d181/repo2          (201M, no repo write)
.venv/bin/python3 scripts/gen_state.py --check                  → CHECK_EXIT=0
.venv/bin/python3 -m pytest tests/test_gen_state.py -q          → 44 passed, 21 subtests passed in 3.26s
.venv/bin/python3 -c "... selectable_task_ids(k) ..."           → ['ED-DATES-01','INSTALL-WINDOWS-MULTI-01','V5-G2A-PREFILL-PROBE-01']
.venv/bin/python3 -c "... simulate INSTALL closed ..."          → ['ED-DATES-01','V5-G2A-PREFILL-PROBE-01','WO-LAUNCH-BINDING']
gh issue view 337 --repo mpmdw/JouleWise --json body  vs record 55 → issue 2955 / record 2955, IDENTICAL
gh pr view 338 --repo mpmdw/JouleWise --json body,title,state    → OPEN, no gate-ledger table
```
