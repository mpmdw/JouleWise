RULING: NTP-ENFORCE-DESIGN-01 ISSUED

# Cold ruling NTP-ENFORCE-DESIGN-01 — how "network time OFF" (H5) and the per-capture log check (H6) are enforced in code

Judge: Claude Fable 5.1, cold seat, one foreground session, 2026-09-28 04:03–04:21 PDT (18 of the 60 budgeted minutes).
Code read in the read-only checkout `/Users/edr/code/JouleWise-wt-ntpd-sol-d528efb2`, commit `d5f624b6`, working tree clean before and after.

Inputs, sha256 recomputed by me:

| Input | sha256 (first 16) |
|---|---|
| Design charge `00-design-charge.md` | `0cc40362a76562db` |
| Scout map `70-ntp-enforce-scout/report.md` | `9d9932a8c9d810d5` |
| Sol 6.0 design `11-sol.md` | `806d4ca10f6ada7d` |
| Opus 5.5 design `13-opus.md` | `a67ced149fcbe205` |
| This ruling's charge `20-coldgate-charge.md` (not opened; the charge reached me as the session's prompt) | `5242ee70c7f0f434` |

**Result in one paragraph** (the terms are defined in §1). The design is one set of records per night, written by the program that launches every night, and one function that every user of a recording must call before it may use that recording. The Opus seat's architecture is adopted with four changes of my own (§4.1, §4.3, §4.5, §6.7); the Sol seat's rule that every output names the records it relied on is adopted; the Opus seat's stricter period for the log query is adopted, which amends two sentences of addendum A3 (§5). The work is four delegated implementation sessions in a fixed order, and the first can start now. Nothing here touches the four files of code that compute a recording's timing uncertainty, or the module that holds back reportable results at this operating-system build.

## 0. Contamination disclosure

1. **Put into my context by the session harness before the charge; opened by me: none.** The owner's global instruction file (a writing standard and a list of skill names); the project instruction file of my worktree (notes on the model bridge); the one-line index of the owner's memory store; five commit subjects. The index carries owner directives on gates, on what bears on the truth of a number, and on threat models, and one status line saying the A2/A3 addenda ruled PROCEED with network time ON and that a D-138 seat was running. The commit subjects say the design seats are in and that a D-138 fix round landed. I took the writing standard as form. I took no fact from the rest: every ruling below rests on a file I read or a command I ran, cited where used.
2. **Not opened:** `RUN_STATE.md`, `TASK_QUEUE.md` (no row of it), any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file.
3. **Same model family.** I am Fable 5.1, as were the judges of addendum A3, of the cap council ruling and its addendum, and of the hold ruling. I sat on none of them.
4. **Read in full:** the charge, the scout map, both designs, addendum A3, the cap council ruling and its addendum A1, the hold ruling.
5. **Values seen:** the three operative numbers of the current calibration and several per-capture figures, as the rulings print them. I used them for nothing.
6. **Executed:** read-only `git`, `grep`, `sed`, `shasum`, `sysctl -n` (two keys); four queries of the system log with `/usr/bin/log show`; and one probe that **wrote four one-line messages to the system log** with `/usr/bin/logger` (tag `jwcgntpd`) to measure how soon a fresh line can be read back. The probe changes no setting. No `sudo`, no `systemsetup`, no capture, no power sampler, no battery read, no subagent, no background task.
7. **Files.** I changed no repository file except this ruling. Scratch: `/tmp/cg-ntpd-d528efb2/` (query outputs `q_local.txt`, `q_offset.txt`, `q2_local.txt`, `q2_utc.txt`, all four sha256 `cab261fdb369193a…`; probe outputs `lat_1.txt` to `lat_3.txt`).

## 1. Words used

Each term is used below only in the sense given here.

| Term | Meaning |
|---|---|
| **Capture** | One recording of the power sampler, about 198 s for a calibration capture and 600 s for an idle capture. |
| **Night** or **window** | One scheduled session of captures on a machine with no agent session running. The two words name the same thing; the code says "night". |
| **Slot** | One capture's scheduled place in a night. **Settle**: the quiet wait of 600 s between the last action on the machine and the first capture. |
| **Build** | The operating-system build string the machine reports (`sysctl -n kern.osversion`). This machine is at 25G83. |
| **Plan** | The frozen file that describes one night: its identifier, its start time, its chain, its custody. |
| **Driver** | The program `scripts/run_night.py`. It checks a night's plan, decides GO or refusal, starts the night's one child program and watches it. While the chain runs it repeats a check that no agent session is running (the **agent census**). |
| **Chain** | That child program: a shell script that takes the captures. |
| **Rehearsal** | A night that runs the driver's whole path with a stand-in chain and takes no capture. |
| **Go receipt** | For a pack, the record that authorises one window to start. |
| **Custody** | The directory tree where a night's records are kept and never rewritten. |
| **Receipt** | A saved record of one command: its arguments, exit status, exact output and the time it finished. |
| **Wall clock, monotonic clock** | The clock that tells the time of day, which software may move; and a counter of elapsed time that nothing moves. A **paired reading** is one reading of each, taken together. |
| **Boot identifier** | A string the system creates at each start-up (`sysctl -n kern.bootsessionuuid`). Two monotonic readings can be compared only if taken in the same boot. |
| **Network time** | The macOS setting "set time automatically". While ON, the time daemon **`timed`** corrects the wall clock. |
| **Marker** | A log line `timed` writes whenever it moves the clock. It contains `cmd,apply,src,`, `ntp_adjtime` or `settimeofday`. |
| **Lead** | The 180 s before a capture. A correction keeps moving the clock for a while after its marker, so a marker in the lead counts against the capture (A3 §4.5). |
| **Witness** | A log line old enough to prove the log has not been deleted back to the period being judged. Defined exactly in §5. |
| **Verdict** | For one capture, one of three strings: `clean`, `network_time_slew_attested` (a marker was found), `network_time_unattested` (cleanliness could not be shown). |
| **Member** | A capture whose timing-uncertainty number, B, enters a calibration. **Issuer**: the tool that selects members and writes the calibration file (`scripts/issue_calibration_acceptance_generation.py`). The calibration file is also called the **issued file**. |
| **Corpus** | The members' files as committed to the repository. The **corpus verifier** is the test script that re-derives the calibration from them. |
| **Clock-fit replay** | The issuer's re-computation, for each capture, of whether one straight line fits its paired readings. Today it is the only registered ground for excluding a capture. |
| **Standing rate, drift term** | The rate, in parts per million, at which the wall clock gains or loses against the monotonic clock; and how far "wall minus monotonic" moved during one capture. The drift term is part of B. |
| **Ledger** | The append-only list of calibration captures. Each row carries a **disposition**, the ledger's word on the capture: `valid` or a kind of invalid. A row is **finalized** when its disposition is written. |
| **Bracket, endpoint** | In a measurement window, the calibration capture before and the one after a measurement. Each is an endpoint. |
| **Claim-bearing** | Of a capture or window: its numbers will be reported as results. **Pack**: the frozen set of plans a claim-bearing window runs from. |
| **Harvest** | The step after the captures that reads them and writes the night's summary. |
| **Consumer** | Any function that turns a capture into a member, an endpoint, a counted idle observation or an input to a claim. |
| **Route** | Defined in §3.6, because the test depends on it. |
| **Registration** | The sealed document, written before captures are taken, that fixes which captures count and which are excluded. The **successor registration** is the one for the next calibration, which the cap council's plan has the owner approve before two new windows run; the present calibration is its **predecessor**. |
| **Estimator files** | The four files of code that turn a capture into B: `joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`. |
| **D-138** | The project's decision that a change to the four estimator files lands only together with a re-issued calibration. **The hold**: the rule, being installed by the D-138 transaction in `joulewise/claim_hold.py`, that nothing claim-bearing runs at build 25G83. |
| **Cap route** | The cap council's sixteen-step plan (its addendum A1 §5) that ends with the hold being lifted. Its conditions are cited here by their own labels: **C1–C9** (what the closing ruling must cite), **K3** (no correction in any acceptance capture), **R9** (the acceptance test on the two new windows), **R12** (a changed estimator file restarts the plan). |
| **Seat** | One delegated implementation session. **WRITE_SCOPE**: the exhaustive list of files a seat may change. |
| **Exclusive create** | Opening a file so that the call fails if the file already exists. It makes a record write-once. |

## 2. What I verified

**Executed by me.**

| # | Fact | How | Result |
|---|---|---|---|
| X1 | `log show` accepts a start and end time with an explicit UTC offset, and honours the offset | The ruled query over the last 90 minutes, three ways: local time with no offset; the same instants written `…-0700`; the same instants written in UTC as `…+0000` | Exit 0 each time, 226 lines each, byte-identical output. Had the `+0000` form been read as local time it would have named a period in the future and returned the header alone. |
| X2 | The header line ends in spaces | `od -c` of the first line | `Timestamp`, 23 spaces, `(process)[PID]`, 4 spaces, newline. A comparison must strip trailing spaces, as the existing check does (`quiet_predicate_campaign.py:494–497`). |
| X3 | Some log lines have no timestamp of their own | Counted lines not starting with a date | 32 of 226. They continue the line above. |
| X4 | `timed` writes in three categories | Counted | 90 `[com.apple.timed:data]`, 52 `[com.apple.timed:text]`, 8 `[com.apple.timed:sntp]`. |
| X5 | How long `timed` is silent in the witness category, network time ON | Gaps between `data` lines | The three longest: 1,650 s, 1,156 s, 1,035 s. A3 found 1,881 s in 28.5 h. All are under 3,600 s. |
| X6 | Network time is ON on this machine now | Same output | 24 marker lines in 90 minutes. |
| X7 | A fresh log line can be read back at once | Wrote a line with `logger`, queried immediately; 3 trials | Found in 3 of 3, each under 1 s after writing. The line came from `logger`, not from `timed`. |
| X8 | Cost of the query | `time` | 2.0 s for 90 minutes of log. A3 measured 2.3 s for 3.5 h. |
| X9 | The registration pins the derivation chain's bytes | Searched the repository for the sha256 of each file the designs would edit | Only `scripts/night_chains/calibration_derivation_only.zsh` (`b5beea464d39…`) is pinned, in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. `run_night.py`, the issuer, the capture writer, `calibration_bracketing.py`, `quiet_predicate_campaign.py` and `build_bracket_binding.py` are pinned nowhere outside the process records. |
| X10 | Which files the D-138 branch changes | `git diff --name-only` of `feat/2026-09-27-d138-25g83-issuance` against its merge base | It changes `calibration_bracketing.py`, the issuer, the capture writer, `run_campaign.py`, `arm_readiness.py`, `tests/test_calibration_bracketing.py` and `tests/verify_calibration_acceptance_corpus.py`, among others. It does **not** change `run_night.py`, `night_gate.py`, `quiet_predicate_campaign.py`, `build_bracket_binding.py` or their tests. |

**Read by me** in the checkout, at the lines cited.

| # | Fact | Where |
|---|---|---|
| R1 | Every governed night, of any kind, is started by the driver in one function, `_run_chain_once`. The driver's three other launches of a chain are probes that set `NIGHT_VERIFY_ONLY` and take no capture. | `run_night.py:856–880`, `:3217`, `:3700–3714`, `:3833–3838` |
| R2 | The derivation chain reserves its ledger session, then waits 600 s, then starts the first capture. It contains no network-time command. | `calibration_derivation_only.zsh:187–219`, `:251–262` |
| R3 | The capture writer finalizes each row during its slot, and the chain continues on exit status 0 or 1. | chain `:244–279` |
| R4 | The writer takes five paired readings named `pre_spawn`, `first_parse`, `sampling_started`, `sampling_stopped`, `post_parse`, with Python's `time.time()` and `time.monotonic()`, and hands them to the evidence. | `validate_powermetrics_fiducial.py:2391`, `:2490`, `:2506–2513`; `clock.py:57–62`; `uncertainty_evidence.py:111–117` |
| R5 | The existing OFF command helper stamps both clocks **after** the command returns, with the same two Python clocks. | `quiet_predicate_campaign.py:348–354` |
| R6 | The idle-night program harvests **inside the chain**: its `finally` block restores network time ON, then calls `pilot_summary`. | `quiet_predicate_campaign.py:1764–1775` |
| R7 | Its per-capture query accepts a header with no rows as clean. | `:756–765` |
| R8 | Its timestamp reader throws the UTC offset away. | `:535–556` |
| R9 | The issuer selects every row whose disposition is `valid` and excludes only for a reason in a one-entry set. | issuer `:1255–1323`; `calibration_bracketing.py:293` |
| R10 | The issued file's validator requires each exclusion entry to have exactly four keys, one of them `reason`. | `calibration_bracketing.py:996–1011` |
| R11 | Bracket building accepts endpoints whose disposition is `valid`, from the ledger alone. | `calibration_bracketing.py:1302–1381`; `build_bracket_binding.py:250–258` |
| R12 | The driver installs no signal handler of its own. Python's default on a termination signal ends the process without running `finally` blocks. | search of `run_night.py` for `signal.signal`: none |
| R13 | The dead-man job (a second scheduled job that runs after a night's latest possible end, to report a night whose driver died) returns early in two cases: the report was already sent, or it fired too soon. | `run_night.py:3361–3373` |
| R14 | The expected OFF output is one constant, with its newline: `"setUsingNetworkTime: Off\n"`. | `arm_readiness.py:104` |
| R15 | The driver's refusal reasons are a registered set in `night_gate.py`, and the same strings appear in `arm_retry.py` and three test files. | `night_gate.py:231–240`; repository search |

## 3. Ruling 1 — the architecture

### 3.1 The forcing problem

A3 requires that a capture taken while the clock was being corrected, or whose log cannot show that it was not, never becomes a member, an endpoint or a claim input. The check that decides this can only run **after the window**, because its witness and its markers are read from the log once the last capture has ended. But the capture writer has already written `valid` into the ledger during each slot (R3), and the ledger is append-only. So at the moment the check runs, every capture is already `valid` on the record, and every consumer today trusts that word (R9, R11).

Two ways out were on the table. A **pending-to-final ledger** would make the writer record "pending" and a later step record the final word. That changes the ledger's life cycle, which three places in `calibration_bracketing.py` must agree on exactly (Opus seat, its §1; not re-read by me). The other way leaves the ledger alone and makes every consumer ask a second question. All three designs chose the second. **I rule the second.**

### 3.2 The design in one picture

```
  BEFORE THE NIGHT            DURING                      AFTER THE LAST CAPTURE
  driver                      chain                       driver
  ┌─────────────────┐   ┌──────────────────────┐   ┌─────────────────────────────┐
  │ marker created  │   │ settle, captures     │   │ [Q] query the timed log     │
  │ [OFF] command   │──>│ each writes its own  │──>│     save raw output + record│
  │ receipt saved   │   │ evidence, hashed     │   │ [ON] command, receipt saved │
  └─────────────────┘   └──────────────────────┘   │ marker removed              │
          │                       │                └─────────────────────────────┘
          v                       v                               │
     h5-off.json          capture evidence                h6-query-N.txt
                          (paired readings)               h6-window-N.json, h5-on.json
          │                       │                               │
          └───────────────────────┴───────────────┬───────────────┘
                                                  v
                       capture_verdict(window records, capture bounds)
                                                  │
              ┌──────────────┬────────────────────┼─────────────────────┐
              v              v                    v                     v
          [C1] issuer   [C2] idle harvest   [C3] bracket build    [C4] claim
          member?       counted?            and evaluation        evaluation
```

Every element named:

- **marker**: the restore-pending file of §4.3. It exists from just before OFF until the ON receipt is written.
- **[OFF]**, **[ON]**: the two `systemsetup` commands of H5. **[Q]**: the window query of H6.
- **h5-off.json, h5-on.json**: the two receipts. **h6-query-N.txt**: the raw bytes the query printed. **h6-window-N.json**: the record about that query. N counts query runs from 1.
- **capture evidence**: the file each capture writes about itself, whose sha256 the ledger row records. It holds the capture's paired readings (R4).
- **capture_verdict**: one function, in one new module, with no side effect. It is the only place a verdict is computed.
- **[C1]–[C4]**: the four kinds of consumer. Each calls the function and refuses anything but `clean`.

### 3.3 Where the verdict is produced, stored and consumed

**Produced: at the moment of use, never earlier.** The window records hold facts (what was run, what it printed, when). They hold **no verdict**. A consumer computes the verdict itself from those facts and from the capture's own evidence. This is the Opus seat's central idea and I adopt it, for the reason the hold ruling gave for its own design: a decision taken at the moment of use from bytes whose digests are checked cannot be overtaken by a stale or borrowed answer.

**A missing record gives `network_time_unattested`.** This one rule replaces the roster the Sol seat and the scout proposed. No list of captures has to be complete, because a capture that no record covers is refused, not passed. A capture taken by hand, outside the driver, has no record and is refused.

**Stored: in the consumer's output, with digests.** This is the Sol seat's point and I adopt it. Whatever a consumer writes (the calibration file, the bracket binding, the idle summary) names the sha256 of each window record it used and the verdict it computed for each capture. A reader can recompute every verdict from the saved bytes.

**The window records.** Directory `<custody root>/night/network_time/`. Every file is written once, by exclusive create.

| File | Content |
|---|---|
| `h5-off.json` | Arguments, exit status, exact output, wall time and monotonic time read after the command returned, boot identifier, plan identifier. |
| `h6-query-N.txt` | The query's full output, byte for byte. |
| `h6-window-N.json` | Arguments; exit status; sha256 of the raw file; the start and end of the query as numbers and as the strings passed; the time the query started and ended on both clocks; boot identifier; sha256 of `h5-off.json`; who ran it (`driver`, `chain`, or `recovery`). On a timeout or a failure to run: the error, and no raw file. |
| `h5-on.json` | As `h5-off.json`, for the ON command. |

The record holds no parsed witness and no parsed markers. They are re-read from the raw bytes each time, so a parser defect fixed later corrects every later verdict without touching custody.

### 3.4 The verdict function

`capture_verdict(window_dir, first, last) -> (verdict, detail)`, in `joulewise/network_time_window.py`. `first` and `last` are the capture's earliest and latest paired readings. For a calibration capture those are `pre_spawn` and `post_parse` (R4); for an idle capture, `sampling_started` and `sampling_stopped`, the pair the existing per-capture check uses.

A **run** is one `h6-window-N.json` with its raw file. A run is **authentic** if the raw file's sha256 equals the recorded one and the recorded `h5-off.json` digest equals that file's. A run is **valid** if it is authentic and all of these hold:

| # | Condition | Catches |
|---|---|---|
| a | exit status 0 | a failed query |
| b | the first line, trailing spaces stripped, is the syslog column header | output of another command or style |
| c | the arguments equal the ruled command, with its start at or before OFF − 3,600 s | a query over the wrong period |
| d | every line of the output is either a line with a timestamp that parses, offset included, or a continuation line that follows one | a timestamp the code cannot place |
| e | a witness is present (§5) | a deleted log |
| f | the run's boot identifier equals the OFF receipt's | a restart in between |

The capture is judged in this order:

1. **Marker.** If any *authentic* run, valid or not, holds a marker whose time lies from `first` − 180 s to `last` + 1 s, the verdict is `network_time_slew_attested`. Each end of that interval is taken from both clocks and the wider reading used (the rule of `quiet_predicate_campaign.py:610–635`, which the new module restates and a test compares against the original). A marker on a continuation line takes the time of the line it continues. A marker is positive evidence that the OFF control failed, so it needs no witness and it takes precedence.
2. **OFF receipt.** `h5-off.json` must exist, show the exact arguments, exit status 0 and the exact output of R14. Else `network_time_unattested`, detail `off_not_proved`.
3. **The 600 s.** `first` must be at least 600 s after the OFF receipt on the wall clock **and** on the monotonic clock. Else unattested, detail `off_lead_short`.
4. **A valid run that covers this capture.** At least one valid run must have started at least 1 s after `last`, on both clocks. Else unattested, detail `no_valid_query`.
5. Otherwise `clean`.

`detail` is for the reader. Only the three verdict strings are ever used as exclusion reasons, because the two failing ones are the registered vocabulary (A3 §4.5; `quiet_predicate_campaign.py:55–56`).

### 3.5 Worked example

Figures patterned on the schedule of the first calibration window of 2026-09-27; they illustrate, they are not a record.

| Moment | Event |
|---|---|
| 00:12:40 | `timed` writes a `[com.apple.timed:data]` line (network time still ON) |
| 00:29:50 | driver runs OFF; exit 0; output exact; receipt stamped 00:29:50 |
| 00:29:52–00:30:05 | chain reserves its ledger session |
| 00:30:05–00:40:05 | the 600 s settle |
| 00:40:08 | capture 1, earliest paired reading |
| 02:30:09–02:33:26 | capture 12 |
| 02:34:10 | chain exits |
| 02:34:12 | driver runs the query, from 23:29:50 (OFF − 3,600 s) to 02:34:13 |
| 02:34:15 | driver runs ON; receipt saved; marker removed |

Capture 1: 00:40:08 − 00:29:50 = 618 s, at least 600 on both clocks. The witness at 00:12:40 is older than OFF. The query started after capture 1 ended. No marker lies between 00:37:08 and the capture's end + 1 s. Verdict: `clean`.

Change one thing at a time:

- The line at 00:12:40 is absent and the oldest `data` line is at 00:35:00. No witness (it is not older than OFF). All 12 captures: `network_time_unattested`. Under A3's text this line would have served, being older than 00:37:08.
- A marker at 00:37:09 (179 s before capture 1). Capture 1: `network_time_slew_attested`. The other eleven: `clean`.
- The driver is killed at 01:15. No query, no ON. The marker file remains. The dead-man job later finds it, proves the chain gone, runs the query and ON (§4.3). If the witness is still in the log, the captures taken before 01:15 are `clean`.

### 3.6 The "no route" property and the test that proves it

A **route** is a sequence of calls into unmodified production code, given a capture at a build where the check is required (§3.7) whose verdict is not `clean`, that ends in any of:

1. a calibration file that lists the capture as a member;
2. a bracket binding that names it as an endpoint, or a bracket evaluated `passed` on it;
3. an idle summary that counts it without one of the two exclusion strings;
4. a claim evaluation that reads it.

**The property rests on three things**, and the test file checks each.

| Id | Test | What it shows |
|---|---|---|
| **NR-1** | One synthetic window with three ledger-`valid` captures: one clean, one with a marker 179 s before it, one with no window record at all. The three are driven through every production consumer of the phase (§6.1): the real function, no stand-in for the verdict function. Required: the first is admitted; the second is refused with `network_time_slew_attested`; the third with `network_time_unattested`. | No consumer of the phase admits. |
| **NR-2** | The same inputs with the records made clean: everything is admitted. | The refusals of NR-1 come from this check and nothing else. |
| **NR-3** | A census (a test that lists every place in production code that touches a protected thing and fails when the list changes). By text search over every `.py` file under `joulewise/` and `scripts/`: (i) files that compare a disposition with the string `valid`; (ii) files that call the consumer entry points (`_select_members`, `discover_calibration_candidates`, `build_calibration_bracket_binding`, `evaluate_calibration_bracket`, `pilot_summary`); (iii) files that call `capture_verdict`. Each list equals a literal list in the test, every entry with a one-line purpose and its phase. | A new consumer cannot appear without review. |
| **NR-4** | A capture at an invented future build with no record is refused. | The default is "required". |
| **NR-5** | If the hold's table no longer holds `25G83` while the set of enforced night kinds (§4.4) lacks `pack`, the test fails. | The hold cannot be lifted before phase 2 lands. |
| **NR-6** | In `run_night.py`, by text: the places that start a process from `plan.chain_path`. Allowed: `_run_chain_once`, and three that set `NIGHT_VERIFY_ONLY` or `NIGHT_RESERVATION_ARGV_ONLY`. | No second capturing launch. |

**Rules of evidence for these tests**, taken from the hold ruling and binding here. A failing run counts only if it fails **by assertion**; an import error is not a failure of the thing tested. For each consumer, the record shows the test going red when that consumer's one check is deleted. Two planted routes are shown to turn NR-3 red and are then removed: a new script that reads a ledger row's disposition, and an alias import of `build_calibration_bracket_binding`.

**What the census cannot see:** a name assembled at run time. It bounds drift and honest mistakes. NR-1 is the proof; NR-3 is the alarm.

### 3.7 Which captures the check applies to

`attestation_required(os_build, session_id)` in the new module returns true unless a **closed list** covers the capture:

- the operating-system builds that precede 25G83, written out as literal strings (the seat takes them from the registered calibration files, and a test checks the list equals the registered builds other than 25G83);
- the two session identifiers of the calibration windows of 2026-09-27, which their sealed registration governs (A3 §4.5, "Scope");
- for idle nights, the plan identifiers of the nights already in custody on the day the idle consumer merges. These stay subject to their own per-capture query.

An unknown build, an unknown session, an unreadable value: required.

## 4. Ruling 2 — the H5 life cycle

### 4.1 Who sets OFF, and when

**The driver, on every route, immediately before it starts the chain.** Precisely: after every check that can refuse a night without touching the machine (plan, gate verdict, chain digest, the pack's go receipt, the once-only start claim), and before the chain's process is created. Everything from the OFF command onward runs inside one `try`/`finally`.

The Opus seat placed OFF earlier, as the driver's first action. I place it later for one reason: every refusal before OFF then leaves the machine untouched and needs no restore. The 600 s are not at risk, because they are proved per capture (§3.4 step 3) and not assumed from the placement.

The chain does not change (X9 shows its bytes are pinned by the registration; A3 §4.4 allows "setting the state from the arming session, outside the capture chain"). The reservation stays the last action before the settle, so the registration's sentence "one 600 s settle after the last operator action" stays true.

The idle-night program's own OFF and ON, and the OFF check in the pack's arm step, stay as they are. Setting OFF twice is harmless. **The driver's receipt is the receipt of record.**

If the OFF command does not exit 0 with the exact output, or cannot be run: the receipt is saved first, ON is attempted and its receipt saved, and the night is refused before any chain runs, with a new registered reason `night_refused_network_time_off_unproved`. A test shows the night launching when that refusal is deleted, which is condition C9 of the cap addendum.

### 4.2 How the 600 s are proved

By subtraction at the moment of use: the capture's earliest paired reading minus the OFF receipt, on the wall clock and on the monotonic clock. Both must be at least 600 s. Three facts make the subtraction sound.

- The receipt is stamped after the command returns (R5), so the true OFF moment is earlier and the proved interval is a lower bound.
- Receipt and capture use the same two Python clocks (R4, R5). The new module must call `time.time()` and `time.monotonic()` and no other clock; a test pins this.
- Same boot: the OFF receipt and a valid query carry the same boot identifier (§3.4 f). A capture whose wall time lies between them was taken in that boot.

If the machine slept between OFF and the capture, the monotonic clock stood still while the wall clock ran. The monotonic difference is then short and the capture is refused. That is the safe direction.

### 4.3 How ON is restored on every exit path

| Exit path | What restores ON |
|---|---|
| Chain ends normally, or with a non-zero status | the `finally`: query, then ON, then remove the marker |
| The driver's own deadline or agent census stops the chain | the same; both return through `_run_chain_once` (read at `:880–960`; not traced to the end by me) |
| An exception in the driver after OFF | the same |
| The chain's end cannot be proved | **neither query nor ON now.** A query beside a capture that may still be running would put the query's own work into the recording, and ON would invite a correction into it. The marker stays. |
| The driver is terminated by a signal, or killed, or the machine loses power | nothing at that moment (R12). The marker stays. |

**The marker** is one file at a fixed place that does not depend on any plan, outside every repository and every custody tree, on the system volume: `~/Library/Application Support/JouleWise/network-time-restore-pending.json`, named by one constant in the new module. It is created by exclusive create **before** the OFF command runs, and holds the night's custody path and plan identifier. It is removed only after `h5-on.json` is written.

**Recovery** is one function, `recover_network_time()`, called in two places: as the first action of the dead-man job, before both of its early returns (R13); and at the start of every driver run, before its own OFF. It acts only when the marker exists **and** the chain it names is proved gone (the file `chain.exited` exists, or the chain's process group is shown absent, as the dead-man job already does at `:3390–3425`). It then runs the query if that night has no valid run, runs ON, saves the receipt in that night's custody and removes the marker. If the chain cannot be proved gone, recovery does nothing and a driver run refuses its own night.

The restore never raises. A failed ON is reported in the night's result and changes no verdict, which is the idle-night program's existing rule (`quiet_predicate_campaign.py:394–469`). Success of ON is exit status 0; its output is saved and compared with nothing until the bench check of §7.2 has observed it.

**No new signal handler in the driver.** It would change how the driver stops its chain, which this ruling does not examine. The marker covers a signal, a kill and a power loss alike.

### 4.4 Night kinds not yet covered refuse to launch

The new module holds one constant, `NETWORK_TIME_ENFORCED_KINDS`. It is **empty** when the first seat merges. A kind enters it in the same merge that lands that kind's consumer. The driver refuses any night whose kind is not in it, with a second new reason `night_refused_network_time_route_unenforced`. A rehearsal that takes no capture is not refused; it runs the same OFF, query and ON, so the path is rehearsed.

This is how "in force before the next window of any kind" is met: by refusal, until the code exists.

### 4.5 Where harvest happens inside the chain

**Neither design saw this.** The idle-night program writes its summary inside the chain (R6), before the driver's query can exist. So for that route the chain itself must run a query: after its children are proved gone, before its own ON and before `pilot_summary`, by calling the new module's `run_window_query(night_dir, who="chain")`. It uses the driver's `h5-off.json`, which exists before the chain starts. The driver still runs its own query after the chain, so the behaviour of the driver is the same for every kind; the night then has two runs, which §3.4 handles. An idle night run by hand has no driver receipt, and its captures are `network_time_unattested`.

The phase-2 scout (§6.4) must answer the same question for the pack's chain.

## 5. Ruling 3 — the query window. A3's text is amended.

**A3 as written.** The query starts 3,600 s before the first capture's first reading and ends 1 s after the last capture's last reading. The witness is a `[com.apple.timed:data]` line older than the first capture's first reading minus 180 s.

**Ruled.** The query starts **3,600 s before the OFF receipt's wall time** and ends at **the moment the query is run**, rounded up to the next whole second. The witness is a `[com.apple.timed:data]` line **older than the OFF receipt's wall time**. Start and end are passed with their explicit UTC offset (X1).

```
        W          OFF              capture 1        ...        capture n       Q
        |           |              |=========|                 |=========|      |
        |           |<-- >= 600 s ->|
        |                     |<-L->|                     |<-L->|
  S |<-- 3,600 s -->|
  S |<----------------------- range of the window query ---------------------->| E
```

`W` is the witness, `OFF` the moment of the OFF receipt, `L` the 180 s lead, `Q` the moment the query runs, `S` and `E` the start and end of the query's range. `|=========|` is one capture. The one change from A3's drawing: `S` and `W` are measured from `OFF`, and `E` sits at `Q`.

**Why this is safe: it can only refuse more.** OFF is at least 600 s before every capture, so:

- a line older than OFF is older than any capture's first reading minus 600 s, hence older than first reading minus 180 s. Every witness under the new rule is a witness under A3's.
- the new range begins no later than A3's and ends no earlier. Every line A3's query would return, the new query returns.
- the marker search for each capture is unchanged.

So a capture `clean` under the new rule is `clean` under A3's text, on the same log. The reverse does not hold, as the second row of §3.5 shows.

**Why it is worth changing a ruled text.**

1. *The query no longer depends on knowing the captures.* Under A3 the driver would have to find the first and last capture of the night and read their clocks before it could ask the log anything. Those live in different places on each route, and the first slot of a night may have been refused and written nothing. Under the new rule the driver needs two things it already holds: its own OFF receipt and the present time. One query serves every capture of the night, and any later capture can be judged against it.
2. *The witness falls where `timed` is most talkative.* Before OFF, network time is normally ON, and `timed` then writes a `data` line at least every 1,881 s on record (X5, A3). The new rule gives the witness a full 3,600 s there. A3's rule gave it 3,420 s, part of it after OFF.
3. *Cost.* A longer range: about 2 s more work at most (X8).

**What does not change:** the command, its flags, the predicate, the category of the witness, the three marker strings, the 180 s lead, the 1 s tail, the two exclusion strings, the rule that one marker of any size excludes, and A3's seven tests. Each of the seven keeps its expected result under the new rule: the line "100 s before the first capture" lies after OFF and is no witness.

**Tests added because of the change**, without which nothing shows that the tightening was implemented:

| Input | Expected | Catches |
|---|---|---|
| The only `data` line before the captures is 300 s before the first capture, after OFF | all unattested | A3's looser witness left in the code |
| A query whose start is 3,600 s before the first capture and not before OFF | run not valid (condition c) | A3's start left in the code |
| A query that started before a capture's last reading + 1 s | that capture unattested | a query run early |

**Standing.** This changes two sentences of A3 §4.5, and the registration text of §7.1 carries the new wording. The owner may overrule it; the fallback is A3's text with a roster of captures sealed by the driver at query time, which the Opus seat named.

**The cap addendum's K3** says "300 s". It points to A2's H6 for the interval, and A3 replaced that H6 in full, so K3 is read with 180 s and with this section's witness. The lead corrects the citation in the next cap record.

## 6. Ruling 4 — files, seats, order

### 6.1 Phases and consumers

| Phase | Night kinds it opens | Consumers it covers |
|---|---|---|
| **1a** | none (the driver refuses all) | none; it builds the module and the driver's life cycle |
| **1b** | `calibration` | [C1] the issuer's member selection (`_select_members`, and the second site at issuer `:306–320`); the issued file's validator; the corpus verifier |
| **1c** | `quiet_predicate_evidence` | [C2] `pilot_summary` |
| **2** | `pack` | [C3] `build_calibration_bracket_binding`, its validator, `evaluate_calibration_bracket`, `scripts/build_bracket_binding.py`; [C4] the pack's claim evaluation; `scripts/launch_window.py`; the manual campaign |

Brackets are in phase 2 because they exist only in measurement windows, and at 25G83 the hold already stops every bracket from passing.

### 6.2 What each consumer does

**[C1] Issuer.** For every `valid` row of the registration's sessions, `capture_verdict` is computed **before** the clock-fit replay. A capture that is not `clean` becomes a named exclusion whose `reason` is the verdict string, even if the replay would also have excluded it. Reason for the order: this check reads the instrument's state and no outcome of the capture, so deciding it first keeps the exclusion independent of outcome. The two strings join `REGISTERED_CORPUS_EXCLUSION_REASONS`. The exclusion entry keeps its four keys (R10).

The issuer takes one window-record directory per session by a required argument. A missing argument refuses the run (an operator's mistake). A directory whose records give no valid run excludes the captures (A3's rule).

The issued file gains, for generations at builds where the check is required, a block `network_time` with: for each session, the sha256 of each window record used; for each member, its state (`off`), its verdict (`clean`) and its session. The validator refuses such a file when a member lacks a clean entry. The window records are copied into the committed corpus beside the members, and the corpus verifier recomputes every verdict from those bytes.

**H7 in the issuer.** Each member's state is recorded. A member set that mixes ON-state and OFF-state members is refused. No pooling rule exists, so none is implemented; adding one later is a reviewed change with its registration.

**[C2] Idle harvest.** A capture is counted only if its own immediate query found it clean **and** `capture_verdict` is `clean`. The immediate query stays byte for byte as approved.

**[C3], [C4].** Designed after the phase-2 scout (§6.4), on this architecture.

### 6.3 Seats and WRITE_SCOPEs

Each list is exhaustive. A seat that finds a needed change outside its list stops and reports the path.

**Seat N1 — module and driver. Starts now**, in a linked worktree from main. Its files are disjoint from the D-138 branch (X10).

```
joulewise/network_time_window.py      (new; imports nothing from the project)
tests/test_network_time_window.py     (new)
scripts/run_night.py
tests/test_run_night.py
joulewise/night_gate.py               (the two new refusal reasons only)
tests/test_night_gate.py
joulewise/arm_retry.py                (classification of the two new reasons only)
tests/test_arm_retry.py
```

Contents of the module: the two commands and their receipts; the query and its records; the parser (offset kept, continuation lines, refusal on a line it cannot place); `capture_verdict`; `attestation_required`; the marker and `recover_network_time`; `NETWORK_TIME_ENFORCED_KINDS`, empty; a report command (§6.5). Every call to the operating system goes through a runner the tests replace; no test touches a machine setting.

**Seat N2 — calibration consumer. Starts after the D-138 transaction has merged**, on a base that holds N1.

```
scripts/issue_calibration_acceptance_generation.py
tests/test_issue_calibration_acceptance_generation.py
joulewise/calibration_bracketing.py   (the exclusion-reason set and the issued-file
                                       validator's network-time block; nothing else)
tests/test_calibration_bracketing.py
tests/verify_calibration_acceptance_corpus.py
tests/test_network_time_routes.py     (new: NR-1 to NR-6 for phase 1b)
```

**Seat N3 — idle consumer. May run beside N2**, on a base that holds N1.

```
joulewise/quiet_predicate_campaign.py
tests/test_quiet_predicate_campaign.py
tests/test_network_time_routes_evidence.py   (new: NR-1, NR-2 for phase 1c)
```

**Seat N4 — phase 2.** Scope fixed by the lead after the scout of §6.4.

**Lead-owned, not in any seat's scope:**
- the one-line additions to `NETWORK_TIME_ENFORCED_KINDS`, made in the merge of N2, of N3 and of N4;
- the three documents that list driver refusal reasons (`docs/contracts/pack_night_go_receipt.md`, `docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`);
- the registration texts of §7.1.

**Never in scope:** the four estimator files; `joulewise/claim_hold.py`; the derivation chain and its generator; the capture writer.

### 6.4 Before seat N4

The Sol seat's blocker F2 stands for phase 2: the script that produces a pack's chain, and the code that harvests a pack's window, are not identified. I found the chain's log name in `scripts/gen_g2_phase_d.py` and its digest checked in `night_gate.py:1033–1038`, and did not trace further. A short read-only scout answers three questions before N4 is scoped: which file produces the pack's chain; where a pack's captures are harvested, inside or outside the chain (§4.5); and which of the four readers the Sol seat listed (`run_campaign.py:4977`, `whole_window.py:602`, `analysis_manifest_v3.py:3652`, `mint_floor_artifact_generalized.py:2261`) read a capture and which only read a bracket's result.

### 6.5 The report command and the cap's step 11

`python3 -B -m joulewise.network_time_window report` has two modes.

- `--h6`: for each capture of a window, its verdict and detail. It reads the paired readings of each capture's evidence and nothing else, and **prints no B**. This is the "H6 log check per capture" of the cap addendum's step 11, which runs before any B is read. A `network_time_slew_attested` capture is printed first and flagged, because under K3 one such capture returns the clock question to council.
- `--h7`: for each capture, its state, its standing rate and its drift term (A3 §4.6). The drift term is part of B, so this mode is run only after the acceptance record of the cap's rule R9 is committed.

### 6.6 Order, against D-138 and the cap route

Step numbers are those of the cap addendum A1 §5.

| Order | What | Depends on |
|---|---|---|
| 1 | D-138 issuance transaction merges (cap step 1) | its own gates; unchanged by this ruling |
| 1, in parallel | **Seat N1** | nothing |
| 2 | N1 reviewed and merged. No night of any kind can launch through the driver from this merge until a consumer lands. | N1 |
| 3 | **Lead's bench checks** (§7.2) | N1 merged; no window armed |
| 4 | **Seats N2 and N3** | D-138 merged (N2); N1 merged (both) |
| 5 | N2 merged with `calibration` enforced. **Cap step 2 is discharged** when 2, 3 and 5 are done. | |
| 6 | N3 merged with `quiet_predicate_evidence` enforced; idle nights may run again | N3; the amendment of §7.1 item 2 |
| 7 | Cap steps 3–9 (name and freeze the estimator files, replay, review, merge the cap transaction) | unaffected: no estimator file is touched, so the cap rule's restart (R12) is not triggered |
| 8 | Cap step 10: the successor registration is sealed with H5–H7 in it, and the two windows run | 5 |
| 9 | Cap step 11 after each window: the cell report, then `report --h6`, then the acceptance test | |
| 10 | Scout, then **seat N4**, merged with `pack` enforced | before cap step 16 |
| 11 | Cap step 16: the closing ruling cites C1–C9 **and NT-C1** | 10 |

**NT-C1**, a condition of this ruling that the closing ruling must cite beside the cap's nine: phase 2 is merged, `pack` is in the enforced set, and NR-1 to NR-6 pass for phase 2 with their red runs on record.

N2 must merge before cap step 10, because a later change to the derivation path re-runs both windows (cap step 15).

### 6.7 Composition with the hold

The hold and this check are **two independent refusals**. A capture must pass both.

- `joulewise/claim_hold.py` is not edited, and the hold's key stays the build. The Opus seat's guard inside the hold's module is not adopted; NR-5 and NT-C1 carry the same dependency without touching it.
- Each is tested with the other switched off: with the hold's table emptied in memory, a capture that is not `clean` is still refused; with clean records, a capture at a held build is still refused by the hold.
- In phase 2 the check in `evaluate_calibration_bracket` is a second statement at the top level of the function, after the hold's. The hold's census requires the hold's statement to stay where it is; N4 keeps that census green.

## 7. Ruling 5 — the owner's items and the lead's bench checks

### 7.1 For the owner

**1. H5–H7 go into the successor registration**, which the owner already approves at cap step 10. No separate amendment is needed for calibration windows: A3 requires the conditions in "the registration the window runs under", and the next window that takes calibration captures runs under the successor. Both seats agree. Draft text, each condition written to be read alone:

> **H5. Network time OFF.** "Network time" is the macOS setting "set time automatically"; while it is ON the time daemon `timed` moves the machine's clock. Before every window the launching program sets it OFF with `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`. The window starts only if that command exits 0 and prints exactly `setUsingNetworkTime: Off`. The command's arguments, exit status, exact output, the time on the wall clock and on the monotonic clock, and the boot identifier are saved. A capture counts only if its earliest clock reading is at least 600 s after that receipt on both clocks, in the same boot. After the last capture network time is set ON and that receipt is saved.
>
> **H6. Every capture is attested from the `timed` log.** The system deletes log lines oldest first, and a query over a deleted period looks exactly like a period without corrections. After the last capture the launching program runs `/usr/bin/log show --info --debug --style syslog --predicate 'process == "timed"' --start S --end E`, where S is 3,600 s before the H5 receipt and E is the moment the query runs, and saves the full output and its sha256. The query is **valid** only if it exits 0, its first line is the syslog column header, every line can be placed in time, and the output holds a **witness**: a line in the category `[com.apple.timed:data]` older than the H5 receipt. A **marker** is a line containing `cmd,apply,src,`, `ntp_adjtime` or `settimeofday`; `timed` writes one whenever it moves the clock. A capture with a marker between 180 s before its earliest clock reading and 1 s after its latest is recorded `network_time_slew_attested`. A capture for which no valid query exists that was run after the capture ended, or whose H5 condition is not met, is recorded `network_time_unattested`. A capture with either record is excluded from the corpus by that named mechanism, which is decided from the instrument's state alone and before the clock-fit replay.
>
> **H7. States are not mixed.** Every member's network-time state is recorded. All members of this corpus are taken with network time OFF. The 12 members of the predecessor were taken with it ON and are not members of this corpus. For every capture of the first OFF window the standing rate and the drift term are recorded, and their comparison with the 12 predecessor members is reported with the first claim-bearing results.

**2. The idle nights' registration.** Its two exclusion strings stay. Their meaning widens: a capture is excluded also when the window check fails. That is a stricter exclusion, decided from instrument state. It needs a dated note in that registration before N3 merges. Whether the owner signs such notes is the project's practice, which I did not read.

**3. Optional.** The owner may overrule §5 and keep A3's query window.

**4. Nothing administrative.** The passwordless command is installed (cap addendum A1 §2, S1; not re-checked by me, since the check uses `sudo`).

### 7.2 For the lead: live checks on the bench

All with no window armed and no capture running. They switch network time, so each session ends with ON and its receipt.

| # | Check | Pass | Sizes what |
|---|---|---|---|
| B1 | The real OFF and ON commands through `sudo -n`, using the new module | OFF: exit 0, output byte-equal to R14's constant. ON: exit 0; its exact output is recorded | H5; the ON comparator |
| B2 | A3's seventh test: the new code's query over a period older than the log | every capture `network_time_unattested` | H6 against a real deleted log |
| B3 | The query with explicit offsets, repeated on the bench | identical to the local-time form (as X1) | §5 |
| B4 | Does switching OFF, or ON, write a marker, and how long after? | recorded either way | confirms both switches lie outside every capture and lead |
| B5 | While OFF for one hour: does `timed` write `[com.apple.timed:data]` lines, and how often? | recorded | whether a window that follows a night left OFF can find its witness |
| B6 | With network time ON: the delay between a `timed` line's own timestamp and the first query that returns it | recorded; if above 1 s, the lead raises the "1 s after the capture ended" of §3.4 step 4 by a reviewed change | the query's earliest safe moment (X7 used `logger`) |
| B7 | Kill the driver after OFF on a throwaway plan; let the dead-man job run | ON receipt written in that night's custody; marker removed | §4.3 |
| B8 | One rehearsal night through the real driver | the four records exist and `report --h6` reads them | the whole path, no capture |

## 8. Ruling 6 — how the attestation could lie, and the refusal for each

| Risk | What would go wrong | What the design does |
|---|---|---|
| The log was deleted | an empty answer read as "no correction" | no witness older than OFF: run not valid: all unattested |
| The query ran late (after a crash) | the same | the same; a late run is valid only if the witness survived |
| The query ran early | a marker written after the query is missed | §3.4 step 4: the capture is unattested |
| A timestamp's offset is dropped or misread | a marker placed an hour away from where it happened | offsets are parsed; a line that cannot be placed makes the run not valid. The existing reader (R8) is not reused. |
| A clock change across the end of daylight saving | one wall-clock hour happens twice | all arithmetic is on seconds since the epoch, from explicit offsets, in the arguments and in the lines |
| A marker on a continuation line | missed or unplaced | it takes its parent's time; a continuation line with no parent makes the run not valid |
| The witness comes from a kind of line kept longer than markers | false proof of coverage | only `[com.apple.timed:data]` counts (A3) |
| OFF was reported but did not take effect | captures taken under corrections | markers appear; the captures are slew-attested; K3 returns the question to council |
| OFF was set less than 600 s before a capture | a slew still fading | §3.4 step 3 |
| The machine restarted or slept | monotonic readings not comparable | boot identifiers differ: unattested. Sleep shortens the monotonic interval: refused. |
| The header or the command drifts with a system update | output of a different shape parsed as clean | conditions b and c |
| A record is damaged | a verdict from altered bytes | digests are checked at every use |
| A capture taken outside the driver | no record at all | unattested |
| Two query runs disagree | which to believe | a marker in any authentic run excludes; cleanliness needs one valid run |
| A consumer added later forgets the check | a route | NR-3 fails |
| The query's own work lands in a recording | energy nobody can attribute | no query while the chain's end is unproved (§4.3) |

**Not refusable by this design, stated plainly.** A future system build that corrects the clock without writing any of the three marker strings would pass H6. The clock fit and the H7 comparison are the only backstops. Deliberate forgery of records by the operator is outside what this check defends against.

## 9. Ruling 7 — every seat disagreement, resolved

| # | Question | Scout | Sol | Opus | Ruling | Why |
|---|---|---|---|---|---|---|
| 1 | Artifact and admission checks, or a pending-to-final ledger | artifact | artifact | artifact | **artifact** | §3.1 |
| 2 | Who produces the records | the chains and the arming step, per route | a "window supervisor" | the driver | **the driver**, plus the chain where harvest is inside the chain | R1: one launch point for all kinds. §4.5 for the exception. |
| 3 | Are verdicts stored in the window record | yes, per capture | yes, with a full roster | no; computed at use | **no** | §3.3: a missing record refuses, so no roster can be incomplete |
| 4 | Do outputs bind the records' digests | yes | yes, at every boundary | yes | **yes** | §3.3 |
| 5 | The query window | A3 | A3 | from OFF | **from OFF** | §5 |
| 6 | Edit the derivation chain, its generator, the capture writer | yes | yes | no | **no** | X9: the chain is pinned by the registration; the writer is also being edited by D-138; nothing requires either |
| 7 | The capture writer checks an OFF receipt before capturing | yes | silent | no | **no** | the 600 s are proved at use; a second check adds a dependency and no safety |
| 8 | Where OFF is placed | before the settle, in the chain | the same | the driver's first action | **the driver, just before the chain starts** | §4.1 |
| 9 | One seat or several | five steps | one seat, 13 production files | two phases | **four seats** | X10: half the files collide with D-138, half do not |
| 10 | The pack route | map it during implementation | a blocker for the whole scope | phase 2 behind a refusal | **phase 2 behind a refusal**; Sol's blocker binds phase 2 only | §4.4, §6.4 |
| 11 | A failed or missing restore | recover in a supervisor | recover, and block the next arm | never raises; changes no verdict | **recover at the next driver start; do not block** | the next night's validity rests on its own receipt and its own witness, and both refuse if the machine's state is wrong |
| 12 | Tie to the hold | — | independent refusals | a guard inside the hold's module | **independent**; NR-5 and NT-C1 | §6.7 |
| 13 | Where the exemption list lives | — | — | `calibration_bracketing.py` | **the new module** | it keeps the list beside the rule and out of the file D-138 is rewriting |
| 14 | Markers counted as lines or as grouped events | lines | lines | lines | **lines** | A3's rule is any marker line |
| 15 | The test of the no-route property | refusal tests | a census of consumers | a driven test, plus a census as alarm | **both**, with the hold ruling's rules of evidence | §3.6 |
| 16 | A window crossing the end of daylight saving | refuse ambiguous times | refuse | refuse the window if offsets cannot be passed | **handled by offsets; nothing refused for that alone** | X1 |
| 17 | The vocabulary entry `scheduler_c4_network_time_on` | do not wire it alone | — | the same | **left unwired** | a reason with no check behind it would be decoration |

## 10. Left unchecked, stated plainly

- **NOT EXECUTED:** any part of the design. §3 to §6 are a specification. I built no prototype.
- **NOT EXECUTED:** the OFF and ON commands, and the check that the passwordless rule is installed. My session may not use `sudo`.
- **NOT READ from a real capture:** the place of the paired readings inside a calibration capture's evidence file. No such file is tracked in the checkout. R4 is read from the code that writes them. Seat N1 confirms the path on one bundle of 2026-09-27, reading the clock readings only.
- **NOT TRACED:** that every stop of the chain by the driver returns through `_run_chain_once` to the `finally` (§4.3, second row). If one does not, the marker still covers it.
- **NOT READ:** `joulewise/arm_retry.py`. Whether its table must classify the two new reasons is for seat N1 to establish; if it need not, those two files leave the scope unchanged.
- **NOT VERIFIED:** the four claim readers the Sol seat cites, and the Opus seat's three-site statement about the ledger's endpoint set. Neither bears on phase 1.
- **NOT ESTABLISHED:** whether `timed` writes `data` lines while network time is OFF (B5), and whether the switches write markers (B4). The design refuses safely either way.
- **ONE MACHINE, ONE MORNING:** X1 to X8.
- **ASSUMED from the file names** in `configs/calibration/battery_float_verdicts/`: the two session identifiers of §3.7. The seat takes them from the registration.

## Summary

1. The program that launches every night sets network time OFF, saves the receipt, queries the clock log after the last capture and sets it back ON; a leftover marker file makes the next run or the dead-man job finish the job after a crash. Every user of a capture recomputes the verdict itself from those saved bytes, and a capture with no record is refused.
2. The log query now starts one hour before OFF and its witness must be older than OFF. This is stricter than addendum A3 and changes two of its sentences; the owner may overrule it. H5 to H7 go into the successor registration the owner already signs.
3. Four seats in order: module and driver now; the calibration and idle-night consumers after D-138 merges; brackets and packs later, behind a refusal and a new closing condition. Until a kind's consumer lands, nights of that kind refuse to launch.
