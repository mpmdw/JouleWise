# BFG-S S2, cold Fable final pass (gate row 7; row 10 for the post-lens commits)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold seat. One foreground session, no subagents, no background tasks.
Working tree: `/Users/edr/code/JouleWise-wt-s2fp-92472459` at `d3f904d682f2c7f0f33c8fe7c98ad483c2c8ff64` (`git rev-parse HEAD`; `git status --short` empty at start and after every probe).
Charge: committed at `c4b4c750` on `docs/2026-09-26-92472459` (verified with `git log` in the bookkeeping worktree).
Session clock: about 19:50 to 20:35 PDT, 2026-09-26 (last `date` call before this file: 20:30:26).

## Verdict: MERGE

**Condition, not a finding:** the full-suite replay of the integration tree `11c2f89d` (candidate plus main `97a48451`) must be green. I did not run it and I did not inspect that tree.

No BLOCKER. No SHOULD-FIX. Three NITs, none of which needs to land before the merge (§6).

## 0. Contamination disclosure

Put in my context by the harness, without my asking:

1. The owner's global instruction file (a writing standard and a pointer to orchestration doctrine). I followed the writing standard for the form of this file. It states no position on any question here.
2. This worktree's `CLAUDE.md` (the Codex bridge description only).
3. The index of the memory directory: one title line per memory. I opened no memory body. Title lines that touch this review's subject, named so they can be discounted: a line that anything bearing on whether a number is true is mandatory and that the battery gate applies every window; a line that gates must be sensible on science grounds; a line that refusals aimed at the machine's own operator are over-engineering; a line that documentation and test-only changes get a light gate. My acceptance of the two residuals in §5 agrees in direction with the third line, so I rest it only on the ruled texts that accept them by name (cited there).
4. The git status and the five most recent commit subjects.

I did not open `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE.local.md`, `AGENTS.md`, the decision log, or any skill file. I wrote no memory.

Read by me: the six governing texts in the charge (the SAMESIG erratum in full; its base ruling not opened, since the erratum's §8 restates amendments 44 to 46 in full); the seat brief and both fix contracts; both round-1 lenses, both delta-1 reports, the fix-2 seat report and the delta-2 report. I did not read the round-1 or fix-1 seat reports.

## 1. Terms used in this file

| Term | Meaning |
|---|---|
| Envelope | One directory written by one run of the collector: `session.json` (the record), `rounds.jsonl` (the journal, one line per measurement round), `raw/` (captured command output). A night is 12 envelopes. |
| Collector | `scripts/sample_quiet_predicate_evidence.py::collect`. |
| Executor | `joulewise/quiet_predicate_campaign.py::execute`. It launches one collector per envelope, records the collector's exit code in its own entry (124 when its wait ran out), then calls the summary. |
| Battery read | One `ioreg` call on the battery, stored as a record plus the raw output. The pre read is taken at the envelope's start, the post read at its end. |
| At float | External power connected, not charging, battery current at most 200 mA, and the battery gauge's own reading at most 180 s old. |
| Verdict | What `battery_float.authenticate_quiet_session` returns: `pass`, `battery_float_confounded` (a read was judged and shows the battery was not at float), or `battery_float_evidence_missing` (a read is absent or could not be judged). |
| Custody failure | The exception `CustodyFailure` (or its subclass `CustodyUnreadable`): recorded bytes are missing, unreadable, or do not hash to what the record says. It is never a status. No summary is written when it is raised. |
| Blanked night | A summary that is written with its status set to the battery verdict and every energy-derived field set to null. |
| Excused envelope | An envelope whose collector died before its final write, dropped on its own (`collect_error`) without blanking the night. Requires all four: no `end_stamp`; the record is exactly what a collector's first write holds; the executor saw a non-zero integer exit; the verdict is `evidence_missing`. |
| No-record carve-out | An envelope whose collector exited non-zero and left no `session.json`, no `rounds.jsonl` and no `raw/round-*` directory. Excluded `collect_error` without authentication, because nothing was recorded. |

## 2. Executed evidence (this session, every probe in the foreground)

All probes ran from the tree root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.`. Scratch is under `/tmp/s2fp/`. No `sudo`, no `launchctl`, no `powermetrics`. I ran the read-only battery `ioreg` command six times to time it (E4).

| # | Probe | Observed |
|---|---|---|
| E1 | Scope and frozen paths: `git diff --name-only 1417c0c4 d3f904d6`; `git diff --stat` over `battery_float.py`, `evidence_night.py`, `night_gate.py`, `configs`, `scripts/night_chains`; `shasum -a 256` | Exactly the eight S2 write-scope paths changed. The excluded paths show no diff. Registration `pilot_protocol_v3.json` = `69321c69…3616`. `battery_float.py` = `4b4d7bb2…e7e5`, the value the SAMESIG erratum records for the base. |
| E2 | **Hermeticity.** A `sitecustomize` in `/tmp/s2fp/site` that logs every un-injected battery `ioreg` call and makes it fail, then `python3 -m unittest tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign tests.test_night_kinds tests.test_battery_float_sweep` | `Ran 327 tests in 323.457s`, `FAILED (failures=1)`. The one failure is `test_real_collect_no_power_reaps_all_recorded_workers`, tripped by my probe's own log file (the test asserts that nothing is written outside the output directory). Run without the probe, it passes (`Ran 2 tests … OK`, together with the historical-night row). 34 un-injected `ioreg` calls were logged, from 9 pre-existing collector tests. **No test outcome depends on the battery state of the machine that runs it.** |
| E3 | The historical pilot nights: `test_t6_historical_pilot_nights_re_summarize_as_evidence_missing`, verbose | `ok`, not skipped: the two archives are on this machine. Both re-summarize as `BATTERY_FLOAT_EVIDENCE_MISSING`. |
| E4 | Cost of the new reads: `/usr/bin/time -p /usr/sbin/ioreg -r -c AppleSmartBattery` five times; one `battery_float.observe` through its default runner; the registration's limits | 0.02 to 0.09 s per call; `observe` 0.027 s, `passed True`. Registration: `start_drift_max_s` 10, `start_drift_abort_s` 2, envelope 600 s, pitch 620 s. The pre read moves the collector's start by about 0.03 s against a 10 s limit. |
| E5 | **End-to-end, `/tmp/s2fp/probe_e2e.py`.** Envelope 5 of a 12-envelope night is written by the **real** `collect` (real `Clock`, injected battery runner carrying the float or charging fixture with `UpdateTime` set to now), then passed through the **real** `record_attestation` as the executor does, then the **real** `pilot_summary`. Ten cases, table below. | Every case matches the ruled outcome. |
| E6 | `/tmp/s2fp/probe_sum.py`, first part: the real `summarize` on a directory of three real-collector envelopes (two completed, one refusal, all at float) | Returned; `summary.json` written. |
| E7 | The same script, second part: a blanked night (envelope 5 post read charging), then a recursive scan of `summary.json` for any number under a key matching `joule`, `energy`, `_j`, `delta`, `s_upper`, `pair_sd`, `interior`, `retained`, `sizing`, `block_two` | Status `BATTERY_FLOAT_CONFOUNDED`; **0 surviving numbers**. |
| E8 | Focused rows: `WriteSiteInventoryTests`, `BatteryFloatSummaryTests`, `BatteryFloatExecuteTests`, `BatteryFloatInterruptedCollectorTests`, `BatteryCollectorTests`, the text-15 fence row in `test_evidence_night`, `tests.test_battery_float_sweep` | `Ran 57 tests in 20.486s`, `OK`. This includes T6-n (the real collector killed in a child process by the real `cleanup_groups`), X-1, R44-1 to R44-6, R45-1 to R45-4, R46-1 to R46-3, and the N-1 row. |
| E9 | **Five mutants of my own**, `/tmp/s2fp/mutate.py`, each one text replaced in a `git archive` copy, run against the two summary test classes (29 tests) | All five KILLED, table below. |
| E10 | Other readers of envelope files: content search over `joulewise/` and `scripts/` for the two file names, the envelope directory pattern and `summary.json` | Four files: the two S2 modules, `battery_float.py`, and `scripts/bench_replay_start_drift.py`. The last reads `power.anchor`, `power.replay` and the summary's status fields for a bench report. It reads no energy. |

### E5, case by case

"Exit" is the code placed in the executor's entry. Eleven other envelopes are passing fixtures with energies 1 to 12 J.

| Case | Envelope 5 | Verdict | `pilot_summary` | Intended? |
|---|---|---|---|---|
| C1 | Honest refusal (no network-time control record), both reads at float, exit 3 | `pass` | Summary written, `SPREAD_RECORDED`, retained 11, pairs 5. Envelope 5: `collect_error`, `incomplete_interior_support`, error `collector refused before capture: network_time_provenance, collector_exit 3`. `summary.md` names it. | Yes (amendment 35 item 3(b)) |
| C2 | Honest completed capture, both at float, exit 0 | `pass` | Summary written, no battery row. Envelope 5 summarized as any envelope (excluded here only for my probe's missing census and power rows). | Yes |
| C3 | Completed, **post read charging** | `confounded` | Blanked, `BATTERY_FLOAT_CONFOUNDED`; no `joules` anywhere; `s_upper` null; disposition `blanks_night` | Yes (text 6) |
| C3b | Completed, **pre read charging** | `confounded` | The same | Yes |
| C4 | Refusal record with a charging pre read, exit 3 | `confounded` | Blanked, `CONFOUNDED`; row routed with `collector record has no end_stamp` | Yes (item 5) |
| C5 | Collector raised before any write; directory holds only `raw/`; exit 1. `record_attestation` returned `False` and **created no file**. | not run | Summary written, retained 11; error `collector left no record, collector_exit 1` | Yes (no-record carve-out) |
| C6 | Collector died in round 2: first-write record, provisional journal, an unbound post raw file; exit 124; then the attestation rewrite | `evidence_missing` | Summary written, retained 11, pairs 5; disposition `excluded_collect_error`; `summary.md` names it | Yes (item 4). The attestation rewrite does not disturb the first-write test. |
| C6b | C6's bytes, exit 0 | `evidence_missing` | Blanked, `BATTERY_FLOAT_EVIDENCE_MISSING` | Yes (item 5: exit 0 is not excused) |
| C7 | Completed, post probe timed out | `evidence_missing` | Blanked, `EVIDENCE_MISSING` | Yes (ruled; QPE erratum Flag 3) |
| C8 | Completed, pre probe timed out | `evidence_missing` | Blanked, `EVIDENCE_MISSING` | Yes |

In C3, C3b, C4, C6, C6b, C7 and C8 the real `summarize` raised `ValueError` naming `envelope-05` and the verdict, and wrote no summary, as amendment 35 rules. (In C1, C2 and C5 my mixed night's fixture envelopes lack the collector's schema key, so `summarize` stopped on that; E6 is the clean positive case.)

### E9, mutants

| Mutant | Result | Killed by |
|---|---|---|
| Blanking leaves the per-envelope `joules` in place | KILLED, 8 failures | T6-g/h/i, the historical row, others |
| Refusal route taken without requiring `pass` | KILLED | T6-j/k |
| Excuse without the executor's exit code | KILLED, 5 failures | T6-g/h/i |
| Excuse on any non-pass status (would excuse a charging pre read) | KILLED | T6-g/h/i |
| A completed envelope's non-pass not booked (night not blanked) | KILLED, 7 failures | T6-j/k, confounded-precedence row, both historical rows |

### Not executed

- The integration tree `11c2f89d` and its full-suite replay.
- The whole of `tests.test_evidence_night` (I ran its one S2 fence row), and the V2 and V3 suites. The lead's bench reports V1 493 OK at `d3f904d6`; my 327 + 57 runs overlap it but are not that run.
- The real `execute` end to end. It needs the night's privileged steps. I read it (`:1600-1832`) and relied on the mocked executor rows inside E2.
- A real `SIGKILL` in my own probe. C6 uses `SystemExit` from the round runner, which reaches the same bytes; the real kill is T6-n, which passed in E8.
- Any envelope from a real night that carries the two battery reads. None exists before S2 merges.
- The write-site inventory's counterfactuals on the real tree. I ran the four R45 rows, which apply them to temporary copies.

## 3. Answers

### Q1. Faithful and complete for S2's scope? **Yes.**

Read against the texts, line by line in the candidate:

| Text | Where | Finding |
|---|---|---|
| Text 5, amendment 20: one pair per envelope; pre after the `session` dict and before `envelope_cpu_start`; post on both return paths before the last record write; the collector's own clock through `monotonic_ns_from_s`; a failed probe is recorded and the collector continues; no new exit path | `sample_quiet_predicate_evidence.py:1081-1092, 1108, 1194` | Exact. C7 and C8 show a failed probe leaves a completed envelope. |
| Amendment 33: `journal_rows = len(rows)` immediately before the final journal write, only in the final record | `:1234` | Exact. C1 and C6 records carry no `journal_rows`. |
| Amendment 34: atomic record and final-journal writes; appends stay appends | `:142-159, 1235`; append at `:1168` unchanged | Exact. |
| Amendment 32 and 35 item 1: the carve-out, by `lstat` | `quiet_predicate_campaign.py:1190-1204` | Exact. C5. |
| Amendment 44: read, authenticate, read again, compare by bytes and by presence, route only from the first read | `:1205-1217, 1229-1231, 1281-1283`; `summarize` `:1507-1529` | Exact. |
| Amendment 35 items 3 to 6 and the record | `:1257-1279, 1412, 1501-1522` | Exact. C1, C4, C6, C6b. |
| Text 6 blanking, confounded first | `:1484-1500` | Exact. E7. |
| X-1: custody printed with `flush=True`, bare `raise`, guard not widened | `:1787-1789` | Exact. |
| Amendment 46: refusal path writes the record, then the journal | `:1109-1110` | Exact. |
| Text 15: the fence flip | `night_kinds.py:66` | Exact. |

Every T-row the rulings assign to S2 has a test through the named call site; the Opus clause table (round 1) and the two deltas enumerate them, and I found no row they missed. E9 shows the rows I care most about have teeth.

### Q2. Can an honest night be refused, blanked or mis-recorded beyond what the rulings intend? **I found no such path.**

Checked by execution: the refusal path (C1), a kill mid-envelope (C6, and T6-n with a real kill), a crash before any write (C5), the attestation rewrite on a completed, a refusal and a first-write record (C1, C2, C6: each still authenticates the same way afterwards), and the two historical nights (E3, `BATTERY_FLOAT_EVIDENCE_MISSING`, intended).

Checked by reading: `record_attestation` on a missing record returns without creating a file, so it cannot defeat the carve-out (confirmed in C5). The replay recorder: a record whose `power.recorder_kind` is not `powermetrics` still refuses the night at the executor (`:1780`), and first-write and refusal records carry `power: null`, so a production night cannot enter that refusal.

Two honest-night costs exist and both are ruled, not defects:
- A completed envelope whose post probe fails blanks the night (C7; QPE erratum Flag 3).
- A kill that lands between the refusal path's two consecutive file writes reads as custody (amendment 46 (ii)).

A hung probe (the 10 s timeout) costs nothing extra: it is a failed probe, so the night is blanked by the ruled text whatever the schedule then does.

### Q3. Can a charging-confounded or custody-failed envelope reach a number or a non-blanked summary? **No path found.**

- Confounded on a completed record, either read: blanked, zero surviving numbers (C3, C3b, E7).
- Confounded on a refusal or unfinished record: blanked (C4; mutant 4 in E9 proves the excuse cannot swallow a charging pre read).
- Custody: every raise of the authenticator and of the two comparisons precedes routing, and `execute` re-raises it without writing an outcome (X-1 rows in E8).
- `summarize` raises on any non-pass and has no excuse (T6-m; C3 to C8).
- No other production reader takes energy from an envelope (E10).

The accepted residuals stay as the rulings state them: a writer that changes a file and changes it back during authentication (amendment 45), and a completed record stripped of `end_stamp`, `post` and `journal_rows` together, which is byte-identical in form to an honest first-write record (amendment 35, rationale (iii)). In the second case the envelope is excluded and yields no number.

### Q4. Row 10: the bench commits and fix 2

- **`4ea4b26b`** (one assertion in `tests/test_battery_float_sweep.py`): correct. It admits exactly `quiet_pre` and `quiet_post` beside the seven original phases. At integration with S1 the line must become `set(battery_float.PHASES)`; that is recorded in the charge and I confirm it.
- **`a0e8e47f`** (revert of F7): correct, and the right call. Two lines swapped in production; the test now asserts that a failed record write leaves neither file. Amendment 46 ratifies the order. R46-2 shows the consequence through `pilot_summary` (the carve-out applies).
- **`d3f904d6`** (fix 2): `git diff --name-status a0e8e47f d3f904d6` lists the two test files only. The rows exist and pass (E8). The inventory test lists seven rows and nine sites, matching amendment 45's table.

### Q5. Dispositions

| Disposition | Ruling |
|---|---|
| Round-1 Sol B1, no change | **ACCEPT.** Amendment 35's rationale (iii) accepts it by name. The envelope is excluded either way and publishes nothing. |
| Sol B2 to the SAMESIG consult, amendments 44 and 45 | **ACCEPT.** Implemented exactly; the premise has a dying test. |
| **Opus N-1** | **ACCEPT: fail closed is correct.** Reasons below. |
| Fix-2 coverage pins baseline-green | **ACCEPT.** A row that pins behaviour already correct cannot be red at the base; its teeth are shown by its counterfactual, and the deltas and E9 show them. |
| N-3 to N-5 closed; D-3 recorded by amendment 44 | **ACCEPT.** |

**N-1, ruled.** The case: a record that has `end_stamp` (the collector finished), has no `battery_float` key (it predates S2), and whose `rounds.jsonl` is missing. The candidate raises `CustodyUnreadable("rounds.jsonl unreadable: …")` and writes no summary.

1. *No number depends on the choice.* A record with no battery key is `evidence_missing`, so the night is blanked under text 6 in any case. The choice is between a blanked summary and no summary.
2. *The newer text decides it.* Text 6's sentence "unreadable envelopes are excluded as today" is the older one. Amendment 32 (erratum) closes with: "If a real pilot-night envelope proves unreadable under (a) or (b), the raise is the correct record", where (b) is a completed envelope whose journal is deleted. The same ruling's class rule says that loss after the collector finished is custody, and it keeps `incomplete_interior_support` only for a readable envelope with short support or a provisional journal.
3. *It costs no existing night.* Both archived pilot nights re-summarize without a raise (E3).
4. *The honest unfinished case is untouched.* A historical record with no `end_stamp` is routed without its journal being read, so a killed historical collector is not turned into custody.

## 4. Q6. Should anything stop S2 merging before S1? **No.**

- A quiet-predicate night uses the collector, the executor and the summary only. Nothing in S1 (bundles and their consumers) is on its path.
- Text 15 rules that the fence opens with S2. The fence row passes with the flag on and refuses with it patched off (E8).
- The only shared file is the sweep test; S1 rebases and the assertion becomes `set(battery_float.PHASES)`.
- The new reads cost about 0.03 s each (E4), against a 10 s start-drift limit and a 20 s gap between envelopes.

One thing to carry into the first real night, as a note and not a condition: that night is the first time a real envelope carries the pair. If a completed envelope's probe fails, the whole night is blanked by rule. That is the ruled behaviour, and text 5 already says any softer rule waits until one real night has run under S2.

## 5. Residuals I accept, with the text that accepts each

| Residual | Accepted by |
|---|---|
| A file changed and changed back during authentication | Amendment 45, with its write-site inventory and reopening conditions |
| A completed record stripped of three fields reads as a first-write record | Amendment 35, rationale (iii) |
| A kill between the refusal path's two writes reads as custody | Amendment 46 (ii) and (iii) |
| One failed probe on a completed envelope blanks the night | Text 6; QPE erratum Flag 3 |

## 6. NITs (none blocks the merge; each is a follow-up)

1. **Nine pre-existing collector tests run the real `ioreg`.** They call `collect` with no `battery_runner`, so each makes two real probes (34 calls logged in E2). Outcomes do not depend on the result, so nothing is wrong today. Follow-up: give the shared test helper a default injected runner, so the suite never touches the host battery.
2. **Three custody texts do not name the envelope.** `quiet_predicate_campaign.py:1233`, `:1235` and `:1285` raise `session.json unreadable after authentication: …`, `session.json is not an object after authentication` and `rounds.jsonl unreadable: …` with no envelope name, while the comparison raises at `:1213-1217` do carry it. With twelve envelopes, the X-1 line then does not say which one. The third wording is dictated by fix item F8 and pinned by a test, so changing it is a small ruled follow-up, not a bench edit.
3. **A stale sentence in the bench replay tool.** `scripts/bench_replay_start_drift.py` (docstring `:28-34`, report text `:778`) says a bench replay's summary status is `REPLAY_NEVER_EVIDENCE`. After S2, a bench replay run while the battery is charging carries a battery status in the summary, and the executor still refuses it as a replay. The file is outside S2's write scope.

## 7. Plain summary for Ed (5 lines)

1. **MERGE**, provided the full-suite replay of the merged tree is green; I did not run that replay.
2. I drove one envelope of a twelve-envelope night through the real collector, the real clock-attestation rewrite and the real night summary in ten situations. Every honest case (a collector that declined to start, one that was killed, one that crashed before writing anything) cost only its own envelope, and every charging or failed battery reading blanked the whole night with no energy number left in the file.
3. I broke the summary code five different ways in a scratch copy; the tests caught all five.
4. On the one question I was asked to rule: an old finished recording whose journal file has gone missing stops the summary with an error instead of being skipped. That is correct. No number depends on it, the newer ruling says so in words, and both archived pilot nights still summarize.
5. Three small follow-ups, none urgent: some older tests still call the real battery command, three error messages do not say which envelope they mean, and one sentence in the bench replay tool is out of date.
