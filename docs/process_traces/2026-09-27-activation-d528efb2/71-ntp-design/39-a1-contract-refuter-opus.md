REFUTER: AGREE-WITH-D1

# Contract-lens refuter for cold gate NTP-ENFORCE-DESIGN-01-A1 (Opus 5.5)

Seat: Opus 5.5, contract lens, one foreground session, 2026-09-28. Paired with the cold Fable judge; written independently, without reading the judge's ruling (file 38).
Candidate: `/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2`, head `3ad82b43` (verified with `git rev-parse`), fix-round base `e7371399`.

## 0. Contamination disclosure

1. **Put into my context by the session harness before the task, not opened by me:** the owner's global instruction file (a writing standard and orchestration notes); the repository's `CLAUDE.md` (notes on the Codex bridge); the owner's private project notes `CLAUDE.local.md` (orchestration doctrine, including the rule "two consecutive rounds failing with the same signature: the next spend is a consult"); the one-line index of the owner's memory store (it carries directives on sensible gates, on "prevent bad science", and a status line naming this lane); five commit subjects. I took the writing standard as form. I took the escalation rule only because the charge restates it. No finding below rests on any other of these; each rests on a file I read or a command I ran, cited where used.
2. **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md` or `AGENTS.md` file, any memory file, any skill file, the Fable judge's ruling (38).
3. **Same model family** as the contract lens (33) of round 0, which was also an Opus seat. I did not write it.
4. **Read:** the charge (37); the ruling in force (21) §0–§10 except §7.1; the execution lens (32); the fix-round brief (34) and report (35); the N1 brief (30); the delta re-audit (36); the contract lens's nit list (33, N3–N7 only); the auditor's probe scripts `probes_killpg.py`, `recovery_descendant.py`, `off_failure_regression.py` and their logs in `/tmp/ntp-n1delta-d528efb2/`; candidate code cited below.
5. **Executed** (all in scratch `/tmp/opus-ntpA1-d528efb2/`, on a `git archive` copy of `3ad82b43` holding `joulewise/ scripts/ tests/ configs/`): three process probes with harmless Python sleepers that I killed myself (verified none remained); the auditor's D2 regression and one extension of it; the module test file `tests.test_network_time_window`. Every network-time command went through the test suite's injected fake runner; an audit hook refused any start of `sudo`, `systemsetup`, `powermetrics`, `ioreg`, `pmset`, `log` or `sntp`. Interpreter `/opt/homebrew/bin/python3 -B`, `PYTHONPATH` = the charge's guard directory. No real setting changed, no system-log query, no battery read, no capture, no repository file modified except this report.

## 1. Words used

| Term | Meaning here |
|---|---|
| **Driver** | `scripts/run_night.py`, the program that launches a night, sets network time OFF, starts the chain, watches it, then runs the query and sets network time ON. |
| **Chain** | The night's one child program (a `zsh` script) that takes the captures. For idle nights it `exec`s into the Python executor `joulewise/quiet_predicate_campaign.py`, so the executor *is* the chain's process. |
| **Capture** | One recording by the power sampler `powermetrics`, with its paired clock readings. |
| **Query** | The driver's one read of the `timed` log after the captures (the ruling's H6 query). |
| **OFF / ON** | The two `systemsetup -setusingnetworktime` commands. **Marker**: the restore-pending file `~/Library/Application Support/JouleWise/network-time-restore-pending.json`; it exists from just before OFF until ON succeeds. |
| **Recovery** | `recover_network_time()` in `joulewise/network_time_window.py`: run at the start of every driver run and twice in the **dead-man job** (the scheduled fallback that finishes a night whose driver died). It runs the query and ON for a night left with a marker. |
| **Process group** | A set of processes that the kernel signals together; its number is the **PGID**. A process normally inherits its parent's group. |
| **Session** | A set of process groups. `subprocess.Popen(..., start_new_session=True)` makes the child call `setsid()`: it becomes the first process of a *new session and a new group*. `os.setpgid(pid, pid)` moves a process into a new group inside the same session. Either way, signalling or probing the chain's group no longer reaches it. |
| **Orphan / adopted by launchd** | When a parent dies, its living children are re-parented to process 1 (`launchd` on macOS). Their parent link to the chain is then gone; their group number is unchanged. |
| **Group census** | The code's check that a group has no members: `_group_census` runs `/usr/bin/pgrep -lf -g <pgid> .`; `_probe_group_absent(pgid)` returns its "absent" answer (`run_night.py:3696`). |
| **Evidence journal** | `night/evidence_processes.jsonl`, written by the idle executor: one line per supervised child with its PGID (`quiet_predicate_campaign.py:1612`, `:213`). It is an existing durable **registry** (a list, kept on disk, of process identities the chain created). |
| **Capture identity** | What a process is, read from its command line: `/usr/bin/powermetrics`, the collector `scripts/sample_quiet_predicate_evidence.py collect`, the recorder `-m joulewise.quiet_predicate_campaign record`, the calibration writer `scripts/validate_powermetrics_fiducial.py`. |
| **Counterfactual input** | The input a regression test feeds that makes the old code do the wrong thing, here: a *real* live process in a *different* group from the chain. A test built on a mock of today's state, instead of that input, kills no defect. |
| **Red run** | The regression run on the pre-fix revision, failing *by assertion* (not by import error or incidental exception). |
| **Backstop** | `capture_verdict` step 4 (ruling §3.4): a capture counts as covered only by a valid query that started at least 1 s after the capture's last paired reading, on both clocks. |

## 2. What the ruling in force actually promises (charge Q1, contract part)

**The promise is about captures, not about process groups.** Ruling §4.3, row 4: "The chain's end cannot be proved → **neither query nor ON now.** A query beside a capture that may still be running would put the query's own work into the recording, and ON would invite a correction into it. The marker stays." Ruling §8, last row, names this row as the *only* defence against "the query's own work lands in a recording". The purpose clause defines the obligation: no query and no ON while any capture may still be recording.

**The ruling's own proof clause is narrower than its purpose.** §4.3's recovery paragraph says recovery acts when "the chain it names is proved gone (the file `chain.exited` exists, or the chain's process group is shown absent...)". Fix round 1 already went beyond that letter on one side (recovery now re-checks the group even when `chain.exited` exists, `network_time_window.py:354–363`, correctly, because the driver writes `chain.exited` itself). On the other side the letter is under-inclusive: "the chain's process group is shown absent" does not show that a capture has ended when the capture runs in another group. The fix brief (34) copied the narrow form ("termination must be PROVEN (process group gone)"), and the seat delivered exactly that. **So the candidate meets the letter of §4.3 and breaks its purpose.** D1 is inside the promise; the ruling's wording is part of the cause, and §4.3 needs a one-sentence amendment (§6 below) so round 2 is not briefed from the same narrow text.

**§4.5 already states the class for the chain's own query:** "after its children are proved gone, before its own ON". The ruling knew the chain has children; it did not carry "children" into the driver's and recovery's proof.

## 3. D1: real, same defect as F1, blocker (charge Q1)

### 3.1 Executed reproduction, with the real group census

The auditor's probes replaced the group census with `os.killpg(pgid, 0)` because `pgrep` could not list processes in its sandbox. I re-ran the scenario with the **production census itself** (`_group_census` → real `/usr/bin/pgrep`), on three exit routes. Each chain starts a harmless 45 s sleeper exactly as `quiet_predicate_campaign.py:1610–1612` starts a collector: `Popen(..., start_new_session=True)` then one journal line with its PGID. Script `/tmp/opus-ntpA1-d528efb2/probe_d1.py`, output `/tmp/opus-ntpA1-d528efb2/probe_d1.log`:

| Route | Driver result | Chain group absent (real pgrep) | Sleeper alive after | Its PGID / parent | Network-time calls | Marker after | Journal census of the sleeper's group |
|---|---|---|---|---|---|---|---|
| Chain exits normally | exit 0 (GO) | true | yes | own group 68312 / parent 1 (launchd) | OFF, query, **ON** | removed | **present** |
| Agent census aborts the chain (driver kills the chain's group) | exit 4 | true | yes | own group 68402 / parent 1 | OFF, query, **ON** | removed | **present** |
| Recovery with `chain.started` naming a gone group | `restored` | true | yes | own group 68557 | query, **ON** | removed | — |

All sleepers were killed with `SIGKILL` to their own group at the end of each case; a final process listing showed none left.

### 3.2 Why it is the same defect as F1

F1 (file 32): "the driver runs the query and ON while a surviving descendant of the capture may still run". Its reproduction used a same-group descendant; its suggested cure was "require whole-group absence". Round 1 implemented whole-group absence. D1 is the same effect (query and ON beside a live capture process) through the same decision point (the proof that the chain ended), reached by a descendant that left the group. **Same signature: yes.** Whether round 1 "failed" is fairer stated as: round 1 cured the instance F1 described and the brief prescribed; the class F1 belongs to was never stated to the seat. That distinction matters for what round 2 is told (§5), not for whether the escalation clock has started — it has.

### 3.3 D1 is slightly understated in reach (not in severity)

The re-audit showed the natural-exit route and recovery. The same one-group proof decides three more routes; all must be cured by one shared predicate, not route by route:

- **The census-abort route** (`run_night.py:964` → `_terminate_process_group`, `:495`) and **the deadline route** (`_WindowDeadline.fire`, `:786–793`, same function). Executed above for the census abort. Here the driver *kills* the chain, so the idle executor's own cleanup (`quiet_predicate_campaign.py:1768`) may never run; the orphans are then cleaned only by the courier's `_evidence_cleanup_error` (`run_night.py:1350`, reached at `:1426`), after query and ON.
- **The dead-man's own chain-exit proof**, `run_night.py:3524` (`os.killpg(pgid, 0)`) → `:3540` writes `chain.exited`. Same narrow proof, separate code.
- **Inside the chain, for seat N3:** the idle executor's `finally` restores ON at `quiet_predicate_campaign.py:1767` and only then reaps its children at `:1768`. That is D1's signature in N3's file. §4.5 requires the chain's query "after its children are proved gone, before its own ON", which forces the order cleanup → query → ON; N3's brief must say so explicitly, or N3 reproduces D1.

### 3.4 Severity: blocker is right, and the backstop does not change that

A fact the re-audit did not state: the **backstop** already keeps the *number* safe today. A capture still recording when the query starts has its last reading after the query's start, so no valid query covers it and its verdict is `network_time_unattested` (test `test_early_query_cannot_cover_capture`, `tests/test_network_time_window.py:112`, passed in my run: 40 of 41 tests pass; the one error is my scratch copy lacking `docs/`, where a real-log fixture lives). So D1 costs captures, not truth, *as long as no later valid query exists*. Today none can: recovery queries only when a night has no valid run, and the start claim is once-only. That condition is an incidental property, not a ruled invariant, and the ruling's §8 names §4.3 — not step 4 — as the defence. On the contract lens D1 stays a **blocker**; the backstop is the reason the stop condition in §7 may consider a fail-closed fallback instead of more rounds.

### 3.5 Reachability at this head

With `NETWORK_TIME_ENFORCED_KINDS` empty (`network_time_window.py:28`), the driver refuses every capture kind (`run_night.py:3234`), so no production capture chain can reach D1 at N1's merge. A plan of receipt class `REHEARSAL_STUB` skips that kind check (`:3147`, `:3228`) and runs whatever chain the plan names; whether the gate lets such a plan name a capturing chain I did not trace. **This does not defer D1:** the proof lives in `run_night.py`, which is in N1's scope only; N2 and N3 cannot change it (ruling §6.3), and the kinds are enrolled at their merges. The cure must land in N1.

## 4. The cure for D1 (charge Q2)

### 4.1 The class that must be closed

Every process that may still be recording a capture or producing its paired readings, at the moment of the query or ON, in the driver or in recovery. Its members, by how they escape the present proof:

| # | Escape | Production call site at `3ad82b43` |
|---|---|---|
| 1 | new session via `start_new_session=True` | `joulewise/quiet_predicate_campaign.py:1610` (`launch`; recorder at `:1633`, collectors at `:1662`), journaled at `:1612` |
| 2 | new session, grandchild, root-owned | `scripts/sample_quiet_predicate_evidence.py:760` (`PowerRecorder.start`: `sudo -n powermetrics`), journaled at `:762` |
| 3 | new group via `setpgid`, same session | `joulewise/sampler_teardown.py:164`, used by `joulewise/controller.py:821`/`:1666` (the measurement controller, the pack route of phase 2); **not** journaled in the evidence journal |
| 4 | orphaned to launchd when the chain dies | any of 1–3 on the census-abort, deadline or kill routes (executed: parent became 1, group unchanged) |
| 5 | same group as the chain | `run_night.py:881` (the chain), and the calibration sampler `scripts/validate_powermetrics_fiducial.py:1170`/`:1176` (no new group) — already covered by the group census |

Not chain descendants, listed so round 2 does not chase them: `run_night.py:1523` (courier, after the chain), `:2361` (bind launcher), `:3762` (`probe_night`), `:3880` (`_probe_cadence`, probe mode); `arm_readiness_evidence.py:655`, `arm_readiness_evidence_t0.py:457`; `magistrate_watchdog.py:480`, `:2503`. Not verified: whether `sudo` ever gives `powermetrics` a new session in the chain (sudo's `use_pty` applies only when a terminal is attached, and the chain has none); a capture-identity sweep (form c) makes the answer irrelevant.

### 4.2 The candidate forms, judged on the whole class

| Form | Closes | Leaves open | Verdict |
|---|---|---|---|
| (a) durable registry of every group the chain creates | 1, 2, 4 (the group number survives adoption; executed: the journal census showed the orphan **present** on both routes) | 3 (controller's sampler is not in this journal); any future spawn that forgets to register; a crash between `Popen` and the journal write (the F2 race again) | **necessary, not sufficient** |
| (b) the chain reaps its children and marks it before `chain.exited` | the cooperative, normal-exit route | 4 entirely: on the census-abort and deadline routes the driver kills the chain, so the chain cannot reap; also `chain.exited` is written by the driver, not the chain, and the chain script's bytes are pinned by the registration (ruling §4.1, X9) | **a fast path at most, never proof** |
| (c) process-table sweep | by *capture identity* (command line): 1–5 regardless of group, session, parent or owner. `ps -ax` lists every process; for root-owned ones it shows at least the executable path or name (checked on this machine: `/usr/libexec/logd`, `endpointsecurityd`), which is enough to match `powermetrics`; the Python collector, recorder and writer run as the user, so their full command lines are visible. By *ancestry*: fails on 4 (parent becomes launchd) | nothing in the class, if identity-based and fail-closed (a sweep that cannot list is "not proved") | **necessary; identity, not ancestry** |
| (d) move query and ON after the idle cleanup | the idle route's normal path | recovery; other kinds; and a cleanup that ends `cleanup_proven: false` must still block query and ON, which is (a) again | **an ordering, not a proof; right for N3's in-chain order (§3.3), not the driver's cure** |

### 4.3 What counts as proof (the contract)

**Capture quiescence is proved** only when, in one pass after the chain's direct child has exited or been killed, all of these hold, and each census that cannot answer counts as "not proved":

1. the chain's group is absent (the present check);
2. every group in the night's registry is absent — today the evidence journal read by `quiet_predicate_campaign.process_groups` (an unreadable journal is "not proved");
3. a sweep of the process table (`/bin/ps -axo pid,pgid,ppid,command`) finds no process with a capture identity and none whose group is in 1–2.

Put this in **one** predicate in `run_night.py` (for example `_capture_quiescent(night_dir, pgid) -> (bool, evidence)`), save its evidence in custody like `group_census`, and use it at every decision point:

- `run_night.py:1006` (normal exit);
- `_terminate_process_group`, `run_night.py:495–555`, before it returns proof (census abort `:964`, deadline `:793`);
- the dead-man's chain-exit proof, `run_night.py:3520–3540`;
- recovery, `network_time_window.py:363`: keep the module free of project imports by passing the predicate in, as `process_group_absent` is today, from `run_night.py:3005`, `:3458`, `:3545`.

No path may reach `run_window_query` or `set_network_time_on` from the driver's `finally` (`run_night.py:3316`) or from recovery unless this predicate returned true. "Not proved" keeps the marker (ruling §4.3 row 4). The machine-wide `powermetrics` rule can block a night when an unrelated `powermetrics` runs; that is the fail-closed direction, and during a quiet window such a process is itself contamination.

### 4.4 Regressions: real call paths and counterfactual inputs

Every one must run the production driver (`run_night.run_night`) or `recover_network_time`/`dead_man` with a **real** `Popen`, a **real** separately grouped sleeper and the **real** group census: the round-2 tests must remove the fixture patch that makes every group absent (`tests/test_run_night.py:413`) for these cases. Each asserts, at the moment the driver returns, that the sleeper is still alive (otherwise the test proves nothing), that neither the query nor ON was run, that the marker remains, and that the refusal is `night_chain_alive`. Each must go red by assertion on `3ad82b43`.

| Id | Route | Counterfactual input |
|---|---|---|
| R1 | normal exit | chain starts a sleeper with `start_new_session=True` and journals it (the `quiet_predicate_campaign.py:1610–1612` pattern), then exits |
| R2 | agent-census abort | same chain, lingering; running census reports an agent |
| R3 | deadline | same chain, lingering past a short deadline |
| R4 | orphan not in any registry | sleeper started with `setpgid` (the `sampler_teardown.py:164` pattern), not journaled, whose command line carries a capture identity. The identity list may be widened in the test to the sleeper's token; the process table must not be mocked |
| R5 | recovery, at driver start and in the dead-man | `chain.started` names a gone group; the journal names the sleeper's live group |
| R6 | the dead-man's own exit proof (`:3524`) | as R5, without `chain.exited` |
| R7 | positive control | as R1, sleeper killed before the chain exits: query and ON **do** run, marker removed |
| R8 | census failure | `pgrep`/`ps` made to fail: not proved |

## 5. D2's cure (charge Q3): confirmed, with three amendments

**Reproduced.** With OFF refused and the immediate ON failing, `chain.started` is left **empty** (0 bytes); the next recovery returns `marker_invalid`, does not retry ON, keeps the marker (`/tmp/opus-ntpA1-d528efb2/d2.log`). **Worse than stated:** the marker is one fixed file for all plans and the driver's recovery runs before the plan is even read (`run_night.py:3005`), and `marker_invalid` refuses the night (`:3021–3026`). I ran a following night: exit 3, reason `night_refused_network_time_marker_invalid`, marker still present (`/tmp/opus-ntpA1-d528efb2/d2_wedge.log`). So one OFF refusal plus one failed ON **refuses every later night of every plan and leaves network time OFF**, until a person deletes the file. That contradicts ruling §9 row 11 ("recover at the next driver start; do not block") and the §4.3 title. On the contract lens D2 is a must-fix in round 2, and I would grade it blocker; its science effect is fail-closed, so the grading does not change what round 2 does.

**Confirmed:** give the two OFF-refusal branches (`run_night.py:3266–3300`) an explicit, durable "Popen never ran" state that recovery and the dead-man understand, keep the immediate ON attempt, keep F2's refusal of unknown identities.

**Amendments:**
1. **Where and when:** write the state into `chain.started` through the claim descriptor, e.g. `{"pid": null, "pgid": null, "never_launched": "network_time_off_refused", "epoch_s": ...}`, **before** the immediate ON, inside its own `try` so that a failed write cannot skip ON (this keeps contract nit N4's point: nothing that can raise runs unguarded before ON). Written after ON, a crash between the two leaves the empty file and recreates the wedge.
2. **What recovery accepts:** that record alone, *without* requiring `chain.exited` (a crash may come before the exit record). An empty file, a file with a PID, or any other shape stays "not proved", as F2 requires. A text census like NR-6 pins that `never_launched` is written only by the two OFF-refusal branches, both of which return before `_run_chain_once`.
3. **The dead-man** (`run_night.py:3478–3494`) accepts the same record, so the crash-between case does not end in a `chain_alive` refusal.

Regressions: the auditor's `off_failure_regression.py` as a driver test (red on `3ad82b43`, green after); the same with a crash injected between the record and ON; a following night after the D2 state launches past recovery; F2's empty-file and unknown-PGID tests stay green.

## 6. D3 and D4 (charge Q4)

- **D3, fix in round 2.** `_DATA_CATEGORY` (`network_time_window.py:40`) contains a lazy `.+?` that lets the match restart at a second `timed[...]` inside the message. The witness is the proof that the log was not deleted, so its parser should read the category from its fixed position in the line with no lazy skip. The fix is one expression in a file already in scope. Regressions: the auditor's payload line (must not witness) and a real `data` line taken from the preserved log bytes (must witness).
- **D4, fix in round 2.** A test-only change: the ON mock at `tests/test_run_night.py:873` returns `{"exit_code": 0}`, so the F1 regression reaches its assertions on the old revision. The rules of evidence (ruling §3.6: a red run counts only if it fails by assertion) make this a correctness issue of the record, not style.

## 7. May round 2 proceed, and its stop conditions (charge Q5)

**Round 2 may proceed**, as the second and last fix round on F1, **only with a brief that states the class** (§4.1), the proof definition (§4.3), and the regressions (§4.4), and not "process group gone" again. Scope: N1's existing WRITE_SCOPE suffices (the predicate reads the evidence journal through `quiet_predicate_campaign.process_groups`, an import, not an edit). The in-chain order at `quiet_predicate_campaign.py:1767–1768` goes into N3's brief.

**Ruling text:** §4.3 should be amended by the judge before the brief is issued, replacing "the chain it names is proved gone (the file `chain.exited` exists, or the chain's process group is shown absent...)" with "capture quiescence is proved (§4.3 of addendum A1: the chain's group, every group in the night's registry, and every process with a capture identity are shown absent by a census that answered)", and adding the same condition to row 1 of the §4.3 table. §4.5 should state the in-chain order cleanup proved → query → ON → `pilot_summary`, which overrides §4.1's "the idle program's own OFF and ON stay as they are" for that order only. §8's last row should name the backstop (§3.4 step 4) as the second line of defence and the "no later valid query" condition it depends on.

**What the delta re-audit after round 2 must execute:** R1–R8 with the real census and real sleepers, killed afterward; each red on `3ad82b43` by assertion and green on the new head; the D2 set including the crash-between case and the following-night case; a text search showing no call to `run_window_query` or `set_network_time_on` in `run_night.py` or recovery that is not preceded by the predicate; the full scoped modules as in file 36.

**If D1's signature survives round 2** (any executed route on which the query or ON runs while a registered, capture-identity or chain-descended process is alive): **no round 3.** The next spend is a **consult** (the standing escalation rule), charged as a redesign question, not a fix: whether the driver should stop proving quiescence and instead never restore ON itself when a capture-kind chain ran, leaving ON to recovery at a later time when quiescence is simple to show, with the backstop as the guarantee for the number. The consult's answer goes to a **cold-gate addendum**, because it changes ruled text (§4.3). **Owner escalation is not needed** unless the answer changes a registration text (§7.1) or leaves nights refused for more than one scheduled window; in both cases the owner is informed with the arithmetic, per the ruling's own owner items.

## Summary

1. D1 is real and is F1's defect again: I reproduced it with the real process census on three routes (normal exit, agent-census abort, recovery), and the round-1 brief and ruling §4.3 both defined the proof as "the chain's process group is gone", which is narrower than the ruling's own purpose of "no query and no ON beside a running capture".
2. The cure that closes the whole class is one shared predicate: the chain's group gone, every group in the evidence journal gone, and no `powermetrics`, collector, recorder or calibration-writer process anywhere. Use it at the normal-exit, abort, deadline, dead-man and recovery decision points, and test each with a real separately grouped sleeper that goes red on `3ad82b43`. D2 is worse than filed (one OFF refusal plus a failed ON blocks every later night until a person deletes the marker) and is cured by a "never launched" record written before ON.
3. Round 2 may proceed once §4.3 is amended and the brief states the class. If the same signature survives, the next step is a consult leading to a cold-gate addendum, not a third round, and not the owner unless registration text or window cadence is at stake.
