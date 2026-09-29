ADDENDUM: NTP-ENFORCE-DESIGN-01-A1 ISSUED

# Cold ruling NTP-ENFORCE-DESIGN-01-A1 — seat N1 may take a second fix round on defect F1, with a wider proof and fixed stop conditions

Judge: Claude Fable 5.1, cold seat, one foreground session, 2026-09-28, from 06:46 PDT, inside the 60 budgeted minutes.
Candidate judged: branch `feat/2026-09-28-ntp-n1`, commit `3ad82b43`; its base before fix round 1, commit `e7371399`. Both were copied with `git archive` into `/tmp/cg-ntpfix2-d528efb2/new` and `/old`. The candidate worktree was clean before and after, and its head did not move.

**Result in one paragraph** (every term is defined in §1). Defect D1 is real and it is the same defect as F1. I reproduced it four ways with the production process check, on both commits. Fix round 2 **may proceed**. The cure is not a better check of the chain's process group. It is a change in what is proved: from "the chain's group is empty" to "nothing that can write a recording is running on this machine", shown by three checks taken fresh each time (§4). I built that proof in a scratch copy and ran it: it withheld the query and ON in every failing case, left the clean path unchanged, and restored ON once the surviving process had ended. D2 is confirmed and its cure is confirmed with one amendment (§5). D3 and D4 are fixed in round 2 (§6). If D1's signature survives round 2, there is no round 3: the next spend is a design consult on who owns the capture processes (§7.4). Ruling sections §4.1, §4.3 and §4.5 are amended (§8). The owner has nothing to decide.

## 0. Contamination disclosure

1. **Put into my context by the session harness before the charge; opened by me: none.** The owner's global instruction file (a writing standard and a list of skill names). The project instruction file of my worktree (notes on the model bridge). The one-line index of the owner's memory store. Five commit subjects. The index carries owner directives on gates and on what bears on the truth of a number, and one status line that names this activation and says two earlier addenda ruled to proceed with network time ON. The commit subjects say the delta re-audit returned findings and that this gate was charged. I took the writing standard as form. I took no fact from the rest: every ruling below rests on a file I read or a command I ran.
2. **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file. The scratch copies contain some of these files because `git archive` copies the whole tree; I did not read them there either.
3. **Same model family.** I am Fable 5.1, as was the judge of the ruling in force. I did not sit on it.
4. **Read in full:** the ruling in force (record 21); the N1 brief (30); the execution lens (32); the fix-round-1 brief and report (34, 35); the delta re-audit and its brief (36); this gate's charge (37, identical to my prompt). **Read in part:** the contract lens (33), from the fifth item of its finding S2 to the end. **Not read:** the N1 report (31), the two design seats (11, 13).
5. **Auditor's scratch files read:** `probes_killpg.py`, `probes-killpg-new.log`, `off_failure_regression.py`, both `off-regression-*.log`, `recovery_descendant.py`. I wrote my own probes and did not run the auditor's.
6. **Executed:** read-only `git`, `grep`, `sed`; `git archive` into scratch; `/bin/ps` and `/usr/bin/pgrep` (they list processes and change nothing); my probes and two test modules under `/opt/homebrew/bin/python3 -B` with the required guard on `PYTHONPATH`. The guard is a small file that makes Python refuse to start any command whose text contains the battery probe's name. Every network-time command and every log query inside the probes was an injected stand-in, meaning a test function that answers in place of the real command. **Not executed:** `sudo`, `systemsetup`, `sntp`, `/usr/bin/log`, any capture, any power sampler, any battery read, any subagent, any background task. The guard logged the attempts it blocked, all from test fixtures; no battery probe started.
7. **Probe processes.** Twenty sleeping Python processes of 45 s each, and two chain stand-ins, started by my probes. Each was killed by the probe that started it. A search after the last probe found none left.
8. **Saved files seen:** the two preserved log files (the archived log of 2026-09-26/27 and `/tmp/cg-ntpd-d528efb2/q2_utc.txt`). I counted lines in them and used no value from them.
9. **Files.** I changed no repository file except this ruling. Scratch: `/tmp/cg-ntpfix2-d528efb2/`.

## 1. Words used

Each term is used below only in the sense given here. Terms of the ruling in force keep its meaning; the ones this addendum leans on are restated.

| Term | Meaning |
|---|---|
| **Process** | One running program. Each has a number, its **process identifier**, and a **parent**: the process that started it. |
| **Process group** | A set of processes that share one group number, so that one signal can be sent to all of them. A new process joins its parent's group unless it asks for its own. |
| **Separately grouped** | Of a child process: started with the option `start_new_session=True` (or the call `setpgid`), which puts it in a **new** group of its own. A signal or a check aimed at the parent's group no longer reaches it. |
| **Orphan** | A process whose parent has ended. The operating system then makes `launchd`, process number 1, its parent. From that moment nothing in the process table links the orphan to the program that started it. |
| **Capture** | One recording of the power sampler. |
| **Sampler** | The program that writes the recording. On this machine it is `/usr/bin/powermetrics`, started as `sudo -n /usr/bin/powermetrics …`. |
| **Collector**, **recorder** | In an idle night: the program that runs one capture and starts its sampler; and the program that logs which processes used the processor during the night. |
| **Capture writer** | In a calibration night: the program that runs one capture and starts its sampler (`scripts/validate_powermetrics_fiducial.py`). |
| **Capture process** | A sampler, a collector, a recorder or a capture writer. |
| **Driver** | `scripts/run_night.py`, the program that launches every night. |
| **Chain** | The one child program the driver starts, which takes the captures. |
| **OFF**, **ON** | The two commands that switch the macOS setting "set time automatically". While it is ON, the system corrects the clock. |
| **Query** | The driver's one reading of the clock daemon's log after the last capture. It costs about 2 s of processor work. |
| **Marker file** | The file the driver creates before OFF and removes after ON. While it exists, ON is still owed. |
| **Recovery** | The function `recover_network_time()`. It finishes the query and ON for a night whose driver did not. It runs at the start of every driver run and in the dead-man job. |
| **Dead-man job** | A second scheduled job that runs after a night's latest possible end and reports a night whose driver died. |
| **Start claim** | The file `chain.started`. The driver creates it empty, before OFF, so that a night can start only once. After it starts the chain it writes the chain's process and group numbers into it. |
| **Exit record** | The file `chain.exited`, which the driver writes when it holds the chain to have ended. |
| **Census** | One listing of the members of a process group, taken with `/usr/bin/pgrep -g`. An empty listing with exit status 1 is the only answer read as "the group is empty". |
| **Registry** | In an idle night: the file `<night>/evidence_processes.jsonl`, where the chain writes the group number of each child it starts, one line each. A child whose line is written is **journaled**. |
| **Witness** | A log line old enough to prove the log has not been deleted back to the period being judged (ruling in force, §5). It must be of the log category `data`. |
| **Pack route**, **phase 2** | The nights whose numbers will be reported as results, and the later seat that opens them. They stay closed under the ruling in force. |
| **Seat** | One delegated implementation or review session. **WRITE_SCOPE**: the exhaustive list of files a seat may change. **Sandbox**: the restricted environment a delegated seat runs in. |
| **Lens** | A review of a seat's work from one angle. The **execution lens** ran the code; the **contract lens** compared it with the ruling. The **delta re-audit** reviewed only what fix round 1 changed. |
| **Blocker** | A finding that must be repaired before the work may merge. |
| **Consult** | A session in which several seats each design an answer to one question, before any code is written. **Cold gate**: a ruling by a fresh judge with no knowledge of the running work, such as this one. |
| **Desk action** | Something a person does by hand at the machine, outside any night. |
| **Sweep** | One listing of every process on the machine with its command line, taken with `/bin/ps`. |
| **Signature (of a process)** | A piece of text in a process's command line that marks it as a capture process: the sampler's file name, or a path that belongs to the night. |
| **Verdict** | For one capture: `clean`, `network_time_slew_attested` or `network_time_unattested`, computed by `capture_verdict`. Only `clean` is accepted. |
| **Fix round** | One delegated session that repairs reviewed findings. |
| **Signature (of a defect)** | The observable behaviour by which a defect is recognised again after a repair. Defined for D1 in §3.4. |
| **Counterfactual input** | The input on which the unrepaired code fails and the repaired code passes. A test that does not use one proves nothing about the repair. |
| **Seam** | A function the tests can replace, so that a test never touches the real machine setting. |
| **F1, F2** | Blockers of the execution lens (record 32). F1: the driver runs the query and ON while a process started by the chain may still run. F2: the dead-man job treated a missing group number as proof that the chain had ended. |
| **D1 to D4** | The four findings of the delta re-audit (record 36). |

## 2. What I verified

### 2.1 Executed by me

All probes and logs are in `/tmp/cg-ntpfix2-d528efb2/`. "New" is `3ad82b43`, "old" is `e7371399`, "cure" is my scratch copy of new with the prototypes of §4 and §5.

| # | Probe | What it did | Result |
|---|---|---|---|
| E1 | `probe_d1.py`, control | Real driver. The chain starts a sleeping child **in its own group** and ends. Real census. | New: only OFF ran; marker file kept; no exit record. Old: OFF, query, ON. Fix round 1 repaired this case. |
| E2 | `probe_d1.py`, D1 at the driver | The same, but the child is **separately grouped**, started with the argument shape of the production call `quiet_predicate_campaign.py:1610`. | New and old alike: the census called the chain's group empty; **OFF, query, ON all ran**; the exit record was written; the marker file was removed; the child was alive, in group 65468, with parent 1. |
| E3 | `probe_d1.py`, D1 when the driver stops the chain | The production function `_terminate_process_group` on a chain that holds a separately grouped child and would have run for 60 s. | New and old: returned "termination proven" in 0.03 s and wrote the exit record; the child was alive. |
| E4 | `probe_d1.py`, D1 at recovery | Marker file and start claim of a chain that has ended; its separately grouped child alive. Real census. | New and old: `restored`; query and ON ran; marker file removed. |
| E5 | `probe_forms.py`, the registry | Production `append_event`, `process_groups`, `groups_absent` on a child journaled the way production journals it. | The registry named group 68318 and the census said "not empty". **The registry sees a journaled child.** |
| E6 | `probe_forms.py`, the registry's gap | The same child, with the journal line never written (the state after a kill between the two production lines 1610 and 1612). | The registry was empty and would have called everything gone. The child was alive. |
| E7 | `probe_forms.py`, the sweep | One `ps` listing of pid, parent, group, session and command. | 788 rows in 0.048 s. The orphan's parent was 1 and its group its own. **The session column read 0 on every row**, so macOS gives an unprivileged reader no session to follow. Ancestry did not reach the chain. A search of the command lines found both orphans. |
| E8 | `probe_forms.py`, the verdict function | A valid query that started at 10,620 s, and three captures. | Ended 10 s before the query: `clean`. Still running at the query: `network_time_unattested`. Ended 0.5 s before the query: `network_time_unattested`. |
| E9 | `probe_d2.py` | Real driver; OFF refused (wrong output) and, separately, the OFF receipt unsavable; the immediate ON fails; recovery later with ON working. | Old: `restored`, ON retried, marker file removed. New: `marker_invalid`, **no ON**, marker file kept, in both branches. Cure: `restored`, ON retried, marker file removed; the immediate ON attempt still ran. |
| E10 | `probe_d2.py`, F2 kept | An **empty** start claim with no exit record, and recovery told that every group is empty. | New and cure: no command ran and the marker file stayed. The label returned was `marker_invalid` (see §5). |
| E11 | `probe_d3.py` | Three lines of the `text` category whose message contains a second `timed[…]` token followed by the `data` category. | New: each served as witness and the verdict was `clean`. An anchored pattern (§6) matched none of them. On the two preserved real logs the anchored pattern, the candidate's pattern and an independent field-by-field parse agree: 2,040 of 2,040 and 90 of 90 `data` lines. |
| E12 | `probe_cure.py` | The §4 prototype against six chains. | See §4.5. |
| E13 | `tests.test_network_time_window`, `tests.test_run_night` | Both modules, on new and on cure, in my scratch copies under the guard. | New: 41 of 41; and 255 run with 20 failures and 12 errors. Cure: one failure more in the first module, 27 errors more in the second. See §9 for what these numbers can and cannot carry. |

### 2.2 Read by me, in the candidate

| # | Fact | Where |
|---|---|---|
| R1 | After the chain ends on its own, the driver checks one thing: the census of the chain's own group. | `scripts/run_night.py:1005–1012` |
| R2 | When the driver stops the chain itself, at an agent-census refusal or at the deadline, both paths end in one function, and its proof is the same census of the same one group. | `run_night.py:495–556`, called at `:964` and `:794` |
| R3 | Query and ON run whenever that one proof succeeded. | `run_night.py:3314–3334` |
| R4 | Recovery's proof is the same one group. | `joulewise/network_time_window.py:353–364` |
| R5 | The driver's own clean-up of an idle night's children runs later, inside the step that prepares the night's report. | `run_night.py:1350–1396`, called from `:1426`, reached through `_finish_reporting` (`:1842`), which runs after the block of R3 |
| R6 | The idle-night chain, when it ends in order, cleans up its children before it exits, **after** its own ON. | `quiet_predicate_campaign.py:1767` (ON), `:1768` (clean-up), `:1776` (summary) |
| R7 | The calibration capture writer starts its sampler without a new group, so that sampler stays in the chain's group. | `scripts/validate_powermetrics_fiducial.py:1170–1181` |
| R8 | The sampler's path is one constant; the idle night builds its sampler command from the same builder. | `joulewise/adapters/powermetrics.py:50`; `scripts/sample_quiet_predicate_evidence.py:214–219` |
| R9 | The driver's census of the agent sessions during the chain is a search for three names, every 30 s. It lists no other process. | `joulewise/night_gate.py:167`; `run_night.py:65` |
| R10 | The saved F1 test does not start a child. It replaces the group check with a stand-in that answers "not empty". | `tests/test_run_night.py:859–882` |

## 3. Ruling 1 — D1 is real, and it is F1

### 3.1 The call sites

The delta re-audit's statement about the production code is **correct**. In the capture code of an idle night, three kinds of process are started separately grouped, at two call sites:

| Call site | What it starts | Journaled in the registry? |
|---|---|---|
| `joulewise/quiet_predicate_campaign.py:1610`, the function `launch` inside `execute` | the recorder (called at `:1633`) and each collector (called at `:1662`) | yes, at `:1612`, two lines **after** the process exists |
| `scripts/sample_quiet_predicate_evidence.py:758–760`, `PowerRecorder.start` | the sampler, `sudo -n /usr/bin/powermetrics …` | yes, at `:762`, after an import at `:761` |

One more site changes a child's group on a capturing route: `joulewise/sampler_teardown.py:164` (`os.setpgid`), used by `joulewise/controller.py:1666`, which belongs to the pack route of phase 2.

The other uses of `start_new_session=True` in `joulewise/` and `scripts/` are not children of a chain. They are the driver's own children (`run_night.py:881` the chain itself, `:1523` the courier that sends the report, `:2361` the driver's supervised launcher, `:3762` and `:3880` two probes), the programs that gather evidence before a night is armed (`arm_readiness_evidence.py:655`, `arm_readiness_evidence_t0.py:457`) and a watchdog script (`scripts/magistrate_watchdog.py:480`). I placed each by the function it sits in and did not trace their callers.

### 3.2 The reproduction, with its numbers

Probe E2, candidate commit:

```
chain's group ........ 65460    census: empty
child ................ 65468    alive, group 65468, parent 1
commands the driver ran: off, query, on
exit record written: yes        marker file removed: yes        driver exit status: 0 (GO)
```

The driver asked "is group 65460 empty?". It was. The child had never been in it. The same happened when the driver stopped the chain (E3) and in recovery (E4).

### 3.3 When this happens on a real night

Not on a night that ends in order: the idle-night chain kills and checks its children before it exits (R6), and the calibration sampler never leaves the chain's group (R7). It happens when the chain does **not** end in order:

- the driver stops the chain at its deadline or because an agent session appeared. It asks the chain's group to end, waits up to 30 s and checks for up to 5 s more, then kills (`run_night.py:85–87`, `:534–548`). The chain's own clean-up has a budget of 30 s (`quiet_predicate_campaign.py:323`) and runs after the chain's own ON command, so the kill can land in the middle of it;
- the chain crashes or is killed by anything else;
- the chain's clean-up ends unproved, for instance because the sampler runs as root and the chain's signal is refused.

In each case a collector and its sampler can run on for up to one capture, 600 s, while the driver queries the log and turns network time ON.

### 3.4 Same defect, and its signature

F1's sentence was: "the driver runs the query and ON while a surviving descendant of the capture may still run". D1 is that sentence with the survivor in another group. The code path is the same (`_run_chain_once`, then the block of R3); the violated rule is the same (ruling §4.3, fourth row); only the survivor's group number differs. **The next fix round is the second on F1.**

**D1's signature**, for every later audit: *the query or ON is run, by the driver or by recovery, while a process that can write a recording is alive.*

### 3.5 What D1 can and cannot damage

This sizes the defect, and it matters for §7.4.

- **It cannot make a spoiled capture `clean`.** A capture counts only if a valid query started at least 1 s after the capture's last clock reading (ruling §3.4 step 4). A capture that was still running when the query ran has its last reading after the query's start, so its verdict is `network_time_unattested` (E8). If a later query covers it, that query's log holds the correction ON caused, and the verdict is `network_time_slew_attested`.
- **It does make the record false.** The exit record and the removed marker file both say the night's processes ended. They had not.
- **It lets the next night start beside the last night's sampler.** With the marker file gone, the next driver run finds nothing pending. Whether another check of the next night would notice a running sampler I did not read (§9).

So D1 is a blocker because it breaks a ruled rule and the truth of the record, not because a wrong number can already reach a result.

## 4. Ruling 2 — the cure's shape for D1

### 4.1 The forcing problem

The driver must know that nothing can still write into a recording before it spends 2 s of processor work on the query and before it lets the system correct the clock. Fix round 1 answered a narrower question, "is the chain's group empty?", and a capture process can leave that group in one line of code. Any proof that starts from *who started the process* has the same weakness, for two reasons I executed:

1. **An orphan cannot be traced.** Once its parent ends, its parent is `launchd` (E2, E7). On macOS the process table shows an unprivileged reader no session either (E7: 0 on all 788 rows).
2. **A list written by the capture code has a gap.** The process exists before its line is written (E6), and a program the capture code starts, such as `sudo`, may create groups the capture code never sees.

So the proof must not depend on where a process came from. It must ask what the machine is running **now**.

### 4.2 What counts as proof

**Ruled.** "No capture process can still be running" is proved when all three checks below succeed. Each is taken fresh at the moment of use, each only reads, and a check that cannot answer (time-out, error, a row it cannot parse) counts as **not proved**. A saved answer, such as the exit record or a clean-up record, is never the proof.

| Check | Question | How | Catches |
|---|---|---|---|
| **P1** | Is the chain's own group empty? | the existing census | a child that stayed in the group (fix round 1) |
| **P2** | Is every group in the night's registry empty? | the registry's group numbers, then one census of all of them. Skipped when the night has no registry file. A registry that cannot be read: not proved. | a journaled child in its own group |
| **P3** | Does any process on the machine carry a capture signature? | one sweep. A process matches when its command line has a word whose last path component is a sampler's file name (a closed list in one constant; today `powermetrics`), or contains one of the night's three paths: the measurement root, the custody root, the chain's path, each both as written in the plan and with links resolved. The sweeping process, its ancestors and its own listing child are left out. | every sampler whoever started it; an unjournaled or orphaned collector or capture writer |

The proof may be repeated for up to 5 s (the driver's existing bound `GROUP_CENSUS_WINDOW_S`) to let a process that is already ending finish. After that it is not proved.

**When it is not proved:** no query, no ON, the marker file stays, and the night's result carries the registered reason `night_chain_alive` with the evidence: which check failed and, for P3, the process numbers and command lines found. The driver's exit status is the refusal status. In my prototype the driver still returned GO (E12), which a reader of the exit status would take for a finished night; the seat must not copy that.

### 4.3 The picture

```
  chain ended, or the driver stopped it
                 |
                 v
   [K]  kill the registered groups          (idle nights only; the clean-up the
                 |                           driver already owns, moved earlier)
                 v
   [P1] chain's group empty? ------------ no --------+
                 | yes                                |
                 v                                    |
   [P2] every registered group empty? --- no --------+
                 | yes, or no registry                |
                 v                                    |
   [P3] sweep: no sampler name,                       |
        no path of this night? ---------- no --------+
                 | yes                                v
                 v                         [U] NOT PROVED: no query, no ON,
   [Q] query --> [ON] --> [M] marker           marker file stays, result says
                          file removed         night_chain_alive
                                                      |
                                                      v
                                           [R] recovery, at the next driver run or
                                               in the dead-man job, asks P1, P2, P3
                                               again, fresh
```

Every element named:

- **[K]**: the driver's existing call of `cleanup_record` for an idle night (`run_night.py:1376–1377`), which signals and then checks the groups in the registry. It moves from the report step to here. It is the only step that signals anything, and it signals only groups the chain itself wrote down.
- **[P1], [P2], [P3]**: the three checks of §4.2.
- **[Q], [ON], [M]**: the query, the ON command and the removal of the marker file, as in the ruling in force.
- **[U]**: the refusal of §4.2.
- **[R]**: recovery. It has no memory of the driver's run. It reads the night's paths from the marker file.

### 4.4 Each candidate form, judged on the whole class

"The class" is: every way a capture process can be alive when the query or ON runs.

| Form | Closes the class? | Why |
|---|---|---|
| **(a)** a registry of every group the chain creates | **No, alone.** Adopted as P2. | It sees only what cooperating code wrote down. E6 shows the gap between the process and its line. The calibration and pack routes have no registry. A group made by `sudo` is never written. |
| **(b)** the chain reaps its children and leaves a durable note before it ends | **No.** Not required of N1. | A chain that is killed writes no note, and that is exactly the case of §3.3. The note is the chain's own claim, not the driver's observation. The calibration chain's bytes are pinned by its registration and may not be edited; the idle-night program belongs to seat N3. |
| **(c)** a sweep of the process table | **Yes, for recordings**, when it matches by signature. Adopted as P3. | Ancestry fails for orphans (E7). A match on the sampler's name does not depend on who started the sampler, in which group, journaled or not. Every recording on this machine is written by that one program (R8). |
| **(d)** moving the query and ON after the idle night's clean-up | **No, alone.** Adopted as [K]. | It covers one route and only journaled groups. Its use is to end stragglers under the identity the chain recorded, so that the same driver run can finish the query and ON. |
| **Ruled** | **[K], then P1 and P2 and P3.** | P3 closes the class. P1 and P2 name the survivor precisely when they catch it. [K] keeps an unattended night from waiting for the dead-man job. |

**Considered and refused:** a list the driver itself keeps by sweeping the process table every few seconds while the chain runs. It would catch a child before it becomes an orphan. It would also add a process listing every few seconds inside every capture (R9 shows the driver runs nothing of that kind today), and this gate did not examine what that does to a recording.

**What the proof does not show, stated plainly.**

- A descendant that carries no signature. My probe's plain sleeper, started separately grouped and unjournaled, passed the proof (E12, last row). It is not a capture process: it names no sampler and no file of the night. The proof is "no recording can be in progress", not "no descendant exists".
- A sampler added later under another name. `joulewise/adapters/nvidia_smi.py` exists for another machine. The list of sampler names is one constant, and a test pins it to the sampler adapters' executables.
- A process that hides its command line on purpose. Out of scope, as deliberate forgery is in the ruling in force (§8, last paragraph).

### 4.5 The prototype, executed

Scratch copy `cure`, probe `probe_cure.py`. The stand-in for the sampler was a sleeping script whose file name was put on the sampler list for the test (`cgprobe-sampler`); I started no process named after the real sampler.

| Chain | New (`3ad82b43`) | Cure |
|---|---|---|
| no children (control) | off, query, on | off, query, on |
| collector stand-in under the measurement root, journaled | off, query, on; child alive | **off only**; marker file kept |
| the same, unjournaled | off, query, on; child alive | **off only**; marker file kept |
| sampler-name stand-in outside every path of the night, unjournaled | off, query, on; child alive | **off only**; marker file kept |
| then recovery while the child lives | `nothing_pending` (the marker file was already gone) | `chain_unproved`; no command |
| then recovery after the child ended | — | `restored`; query, on; one ON receipt; marker file removed |
| plain sleeper, no signature | off, query, on | off, query, on (the stated limit) |

### 4.6 Call sites that must change

| # | Where (candidate line numbers) | Change |
|---|---|---|
| C1 | `scripts/run_night.py`, a new function beside `_probe_group_absent` (`:3696`) | The proof of §4.2. It returns the answer and the evidence. Its process listing goes through a seam, as `_probe_group_absent` does. My prototype called `subprocess.run` directly and broke 27 existing tests that replace `subprocess.Popen` (E13); the seat must not repeat that. |
| C2 | `run_night.py:3314–3334`, the block after the chain | The condition becomes "the chain's end is proved **and** the proof of C1 holds". When the start claim records a failed launch, no process was created and the proof is not needed. When C1 fails: the refusal of §4.2. |
| C3 | the same place, before C1 | [K], for nights that have a registry, under the conditions `_evidence_cleanup_error` already applies (`:1365–1374`). The later call at `:1426` stays and finds the saved record. [K] may itself end unproved, for instance when a sampler runs as root and refuses the signal. The proof then fails and the refusal of §4.2 follows. |
| C4 | `run_night.py:3005`, `:3458`, `:3545`, the three calls of recovery | Pass the proof to recovery as an injected function. |
| C5 | `joulewise/network_time_window.py:341–395`, `recover_network_time` | For a known group number: act only when the injected proof holds. Without an injected proof: `chain_unproved`. The module still imports nothing from the project. |
| C6 | `network_time_window.py:96–108`, the marker file's creation, and the driver's OFF call at `run_night.py:3266` | The marker file also holds the night's three paths, written before OFF. A marker file without them (none can exist from a real night, since no night has launched under this code) is judged with P1, P2 and the sampler names. |
| C7 | `run_night.py:1005–1012` and `:495–556` | **Unchanged.** "The chain's end is proved" keeps its meaning, and the exit record keeps its meaning, because the report step and the dead-man job read them. The new proof gates only the query and ON. |

All of these are inside the files fix round 1 was allowed to change.

### 4.7 The counterfactual inputs the regressions must use

Rules for all of them:

- Each test starts a **real process** through the **production call path**: `run_night`, then `_run_chain_once` with its real `Popen`, a real chain script, and a real child started with `start_new_session=True`. The census and the sweep are real. A stand-in that answers "not empty" (R10) is a picture of today's finding and is not accepted for any row below.
- Each test asserts that the survivor is **alive**, and for the orphan rows that its parent is 1, **at the moment it asserts** what the driver did. Otherwise a slow machine turns the test into a control.
- Each test fails **by assertion** on `3ad82b43`. An error raised for another reason is not a failure of the thing tested.
- A host that cannot list processes must make these tests **fail or report "not run"**. It must not skip them silently. The lead runs them outside the sandbox.
- No test starts a process whose file name is the real sampler's. The name list is tested in two other ways (rows T3 and T10).

| # | Counterfactual input | Production call site | Expected after the cure |
|---|---|---|---|
| T1 | chain ends; child separately grouped, **journaled** with the production `append_event` into `$NIGHT_DIR/evidence_processes.jsonl`, running a script under the measurement root | `run_night` → C2 | only OFF ran; marker file kept; `night_chain_alive`; refusal exit status |
| T2 | the same, **unjournaled** (the state between lines 1610 and 1612) | the same | the same |
| T3 | child separately grouped, unjournaled, **outside every path of the night**, whose file name is on the sampler list (a neutral name added for the test) | the same | the same |
| T4 | the driver **stops** a running chain (agent census refusal, and again at the deadline) while a separately grouped child lives | `_run_chain_once` → `_terminate_process_group` → C2 | no query, no ON |
| T5 | marker file and start claim of an ended chain, separately grouped child alive; then the child ends | `recover_network_time` from `run_night` (`:3005`) | first `chain_unproved` and no command; then `restored`, one ON receipt, marker file removed |
| T6 | the same state | `dead_man` (`:3458`, `:3545`) | no ON while the child lives |
| T7 | the sweep cannot answer: time-out, non-zero exit, a row that does not parse | C1 | not proved |
| T8 | the driver's own command line contains a path of the night, on an otherwise clean machine | C1 | proved; the driver does not find itself |
| T9 | control: a chain with no children | `run_night` | off, query, on, on both commits |
| T10 | by text, no process: the command line the production builder `power_argv()` returns is matched by the production matcher with the production list; and the production list equals the file name of `adapters/powermetrics.py:50` | C1 | matched |

**Red by deletion**, each shown in the round's report: with P3 deleted, T2 and T3 go red; with P2 deleted, a journaled child **without** any signature goes red; with P1 deleted, the same-group case of fix round 1 goes red; with C5 deleted, T5 goes red.

## 5. Ruling 3 — D2's cure. Confirmed, with one amendment.

**The defect, executed (E9).** When OFF is refused, the driver closes the start claim **empty**. If the immediate ON also fails, the marker file stays, as it should. Recovery then tries to read the empty start claim, fails, and answers `marker_invalid`. It never retries ON, and every later driver run refuses its night with `night_refused_network_time_marker_invalid` until a person removes the marker file. The likeliest cause of a refused OFF is a broken password-free rule for `sudo`, and that breaks the immediate ON too. So this is the expected course of the most plausible failure, not a corner.

**Confirmed.** Both branches that refuse after OFF (`run_night.py:3268–3284` and `:3285–3301`) write a complete start claim that says the chain's launch was never attempted, and only then the exit record:

```json
{"pid": null, "pgid": null, "epoch_s": 1790603668.27,
 "popen_attempted": false,
 "launch_error": "never_launched: network_time_off_unproved"}
```

`launch_error` is kept because the dead-man job's existing test for a failed launch reads it (`run_night.py:3506–3510`). The order of fix round 1 stays: the immediate ON attempt first, then the claim, then the exit record.

Recovery treats a night as **never launched** only when all of these hold: the start claim is an object; its `pid` and `pgid` are both null; it has `popen_attempted` false or a non-empty `launch_error`; and the exit record has `launch_failed` true. Everything else with an unknown group number stays `chain_unproved`. That is F2's refusal, unchanged (E10).

Executed on the prototype (E9): recovery answered `restored`, retried ON and removed the marker file, in both branches; the immediate ON attempt still ran in the driver.

**Amendment: the label.** An empty or unreadable **start claim** must return `chain_unproved`, not `marker_invalid`. `marker_invalid` means the marker file itself cannot be read. Today the two are confused because one catch-all at `network_time_window.py:394` turns every error into `marker_invalid` (E10). The confusion sends a person to repair the wrong file.

**Left as a registered limit, not for round 2.** If the driver is killed in the instant between starting the chain and writing its numbers into the start claim, the claim stays empty for ever and recovery can never act. F2 requires exactly that. Clearing it is a desk action: confirm by hand that no capture process runs, set network time ON, remove the marker file. The lead writes that step into the night hand-back document.

**Regressions.** Through the real driver with injected commands and a spawn that raises if called: (i) OFF returns wrong output, the immediate ON fails, a later recovery with ON working answers `restored`; (ii) the same with the OFF receipt unsavable; (iii) an empty start claim with no exit record: no ON; (iv) an empty start claim **with** an exit record that says `launch_failed`: no ON, because the claim itself says nothing. Rows (i) and (ii) fail by assertion on `3ad82b43`.

## 6. Ruling 4 — D3 and D4: both in round 2

**D3.** Fixed in round 2. It is small, the file is already open, and it is the second time this finding survives (the contract lens's N1), so deferring it would invite a third.

The pattern at `network_time_window.py:40` allows any text before `timed[…]`, so the search can begin again inside the message. The category must be read **by position**: timestamp with offset, then at most one host word, then `timed[number]`, then the category. A pattern that does this, tested in E11:

```
^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+[+-]\d\d:?\d\d\s+(?:\S+\s+)?timed\[\d+\]:?\s+\[com\.apple\.timed:data\](?:\s|$)
```

It rejected all three attack lines and matched the same 2,040 and 90 real `data` lines as the candidate's pattern. The seat may use it or a field-by-field parse. Regression: the three lines of `probe_d3.py`, each expected `network_time_unattested`; and the two real-log counts, unchanged.

**D4.** Fixed in round 2, as part of T1. The saved F1 test (R10) is replaced by T1, which starts a real child. Wherever a test stands in for the ON command, the stand-in returns a receipt of the shape the driver reads (`{"exit_code": 0}`), so that the old commit fails by assertion and not by a type error.

## 7. Ruling 5 — fix round 2 may proceed

### 7.1 Decision

**PROCEED.** One round, one seat, in the candidate worktree, on top of `3ad82b43`.

### 7.2 Scope and the seat's stop conditions

WRITE_SCOPE is the nine files of fix round 1, unchanged: `joulewise/network_time_window.py`, `scripts/run_night.py`, `joulewise/night_gate.py`, `joulewise/arm_retry.py` and their four test files, and `tests/test_launch_window.py`. No new refusal reason is needed.

The brief carries §4.2, §4.6, §4.7, §5 and §6 of this addendum word for word. The seat **stops and reports** instead of going on if any of these occurs:

1. the cure needs a change outside the nine files;
2. the cure needs any process listing, signal or log query **while a capture may be running**;
3. an existing test must be weakened or deleted to pass, other than the saved F1 test that T1 replaces;
4. a regression of §4.7 cannot be made to fail by assertion on `3ad82b43`;
5. the seat finds a fourth way for a capture process to be alive that P1, P2 and P3 do not see. That is a finding for the lead. The seat does not design a fourth check.

### 7.3 What the delta re-audit after round 2 must execute

The auditor is a fresh seat that wrote no part of the fix. It needs a host where `ps` and `pgrep` can list processes. The auditor of fix round 1 reported that its sandbox could not, and used a substitute for the census; no substitute exists for P3. If the auditor cannot list processes, the lead runs rows 1 to 3 below outside the sandbox and gives the auditor the logs.

| # | Must execute | Pass |
|---|---|---|
| 1 | My probes against the new head: `probe_d1.py`, `probe_cure.py`, `probe_d2.py`, `probe_d3.py`, from `/tmp/cg-ntpfix2-d528efb2/`, copied into the record before that directory is lost | every D1 row: only OFF ran and the marker file is kept; D2: `restored` with ON retried; D3: three times `network_time_unattested`; the clean control: off, query, on |
| 2 | Every regression of §4.7 and §5 on `3ad82b43` and on the new head | fails by assertion on the old, passes on the new; T9 passes on both |
| 3 | The four deletions of §4.7, and the deletion of the D2 claim record | each turns its named test red by assertion |
| 4 | **A hunt of its own**, at least these four, each with a real process: a child that forks twice and lets the middle process end; a child that calls `setsid` some seconds after it starts; a child that starts a further child **after** the chain has ended; a separately grouped child that itself starts a separately grouped child | for each, either the proof refuses, or the survivor carries no capture signature and the report says so |
| 5 | Every other finding marked fixed in record 36 | still fixed: the 42 tests of fix round 1 pass on the new head |
| 6 | The modules in scope, run whole, in a real checkout outside the sandbox | no failure that is absent on `3ad82b43` in the same environment |
| 7 | A statement, for D1 and for the contract lens's N1: does the signature survive in any form? | stated yes or no, with the executed case |

### 7.4 If D1's signature survives again

**Test.** D1 has survived if the re-audit executes any case in which the query or ON runs, in the driver or in recovery, while a process is alive that names a sampler or a path of the night. A surviving process with no capture signature is the stated limit of §4.4 and is not D1. A defect of another kind that round 2 introduces, as round 1 introduced D2, is a new finding: it gets one fix round of its own with no cold gate.

**Then.** No round 3. N1 does not merge. The next spend is a **design consult**, convened as the project's own rules for consults require, followed by a cold gate. Its charge: *who owns the capture processes?* A second failure would show that a proof taken from outside, at one moment, cannot be made whole, and that the driver must instead be the only program that starts a sampler, or must hold each sampler through a supervisor of its own. That is a redesign of process custody, and it reaches into the capture code that N1 may not touch.

**Not an owner escalation.** Nothing here needs hardware, `sudo`, money or a change to a sealed registration. The owner receives one plain notice of the outcome.

**Why a consult is the proportionate step and not an emergency.** By §3.5, D1 cannot by itself turn a spoiled capture into a `clean` one, and while N1 is unmerged no night launches under this code. Nothing is at risk while the consult runs except time.

### 7.5 Owed by the lead, outside the seat's scope

1. Copy my probes and their logs into the record directory (row 1 of §7.3).
2. Write the desk action of §5 into the night hand-back document.
3. Give seat N3 the amendments of §8, and add `joulewise/network_time_window.py` to its WRITE_SCOPE (the still open item N5 of the contract lens).
4. Give the phase-2 scout one more question: on the pack route, which program starts the sampler, and in which group (`sampler_teardown.py:164`).

## 8. Amendments to the ruling in force

| Section | Text in force | Amended text | Why |
|---|---|---|---|
| **§4.3**, table, fourth row | "The chain's end cannot be proved" | "The end of every capture process cannot be proved." What restores ON stays the same: neither query nor ON now; the marker file stays. | The chain's end is one process group. A recording can outlive it (E2 to E4). |
| **§4.3**, the marker file | "holds the night's custody path and plan identifier" | It also holds the night's measurement root and the chain's path. | Recovery runs with no plan loaded and needs the night's paths for P3. |
| **§4.3**, recovery | "It acts only when the marker exists **and** the chain it names is proved gone (the file `chain.exited` exists, or the chain's process group is shown absent…)" | "It acts only when the marker file exists **and** the proof of addendum A1 §4.2 holds at that moment, or the start claim records that the chain was never launched (A1 §5). The exit record is a record and never a proof." | Fix round 1 already stopped trusting the exit record alone. This makes the ruling say so, and widens the proof. |
| **§4.5** | the chain runs its query "after its children are proved gone, before its own ON and before `pilot_summary`" | The order inside the chain is stated in full: clean-up of its children, **proved**; then its query; then its own ON; then `pilot_summary`. If the clean-up is not proved, the chain runs neither its query nor its ON and leaves both to the driver and to recovery. | Today's code runs the chain's ON **first** (R6: line 1767 before 1768). That is D1's signature inside the chain. It is seat N3's file. |
| **§4.1**, fourth paragraph | "The idle-night program's own OFF and ON … stay as they are." | "The idle-night program's own OFF stays as it is. Its own ON moves after its proved clean-up (§4.5 as amended)." | The same. |

Not amended: §3 (the verdict function and its records), §5 (the query window), §6 (seats and order, except N3's scope in §7.5), §7, §8. E8 confirms that the verdict function already refuses a capture the query overlapped.

## 9. Left unchecked, stated plainly

- **NOT EXECUTED on a real night path:** any real sampler, any real `sudo`. Whether `sudo` on this machine puts its command into a new group or session I could not test. P3 does not depend on the answer; P1 and P2 do.
- **NOT EXECUTED:** the full driver path with a real census refusal or a real deadline (T4). I called the function both paths end in (E3).
- **THE PROTOTYPE IS NOT AN IMPLEMENTATION.** It has no seam, no refusal record and no retry bound, and it returns GO where §4.2 demands a refusal. It shows that the shape works, not that any code is ready.
- **THE SUITE NUMBERS OF E13 CARRY LITTLE.** My copies are `git archive` trees with no repository around them, and the guard blocks every command whose text contains the battery probe's name. The candidate itself showed 20 failures and 12 errors there. I compared the two runs by kind of error: the prototype's 27 added errors are of two kinds, both caused by its direct call past the tests' stand-in for `Popen`; the 20 failures are the same in both runs. Row 6 of §7.3 exists because of this.
- **NOT READ:** whether any check of the *next* night would notice a sampler left over from the last one (§3.5, third point).
- **NOT READ:** the pack route's chain and its sampler's group (§7.5 item 4). The pack route stays closed until phase 2.
- **NOT READ:** the N1 report (31) and the two design seats.
- **ONE MACHINE, ONE MORNING:** the 0.048 s for a sweep of 788 processes, and the session column that reads 0.
- **THE PATH SIGNATURES CAN MATCH TOO MUCH.** A shell, an editor or an agent session whose command line names the measurement root will hold back the query and ON. That is the safe direction, and the refusal names the process so that a person can end it. A machine in that state is not quiet in any case.

## Summary

1. D1 is real and is F1 again: the driver and recovery check only the chain's own process group, and the idle night's collector, recorder and sampler each run in a group of their own, so the query and ON ran beside a live child in all four of my reproductions. It cannot turn a spoiled capture into a clean one, but it makes the record false.
2. Fix round 2 may proceed in the same nine files. The proof becomes "nothing that can write a recording is running": the chain's group empty, every journaled group empty, and no process on the machine naming the sampler or a path of the night. D2 gets an explicit "never launched" start claim; D3 and D4 are fixed in the same round.
3. If the query or ON still runs beside a live capture process after round 2, there is no round 3: a design consult decides who owns the capture processes, then a cold gate rules on it. The owner has nothing to decide.
