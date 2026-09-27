# Cold gate BFGS-SAMESIG-01: ruling

Judge: Claude Fable 5.1, cold seat. One foreground session, no subagents, no background tasks.
Charge: `70-consult-samesig/00-charge.md` @ `9a87b967`. Working tree: `a0e8e47f` (S2 head).
Session clock: 19:00 to 19:17 PDT, 2026-09-26 (first and last `date` calls of the session).

## 0. Contamination disclosure

I opened none of the forbidden files (RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, the decision log, memory bodies, skill files).

The harness put three things into my context before the charge, without my asking:

1. The owner's global instruction file. It holds a writing standard and a pointer to orchestration doctrine. It states no position on any question here.
2. This worktree's `CLAUDE.md`. It describes the Codex bridge only.
3. The index of the memory directory: one title line per memory. I read no memory body. Two title lines touch this ruling's subject and I name them so the magistrate can discount them:
   - a line saying that refusals aimed at an adversary who is the machine's own operator are over-engineering;
   - a line saying that gates must be sensible on science grounds.

Ruling Q-A1 reaches a conclusion that agrees with the first line. I therefore rest Q-A1 only on evidence executed in this session (§A1, probes P1 to P3) and on the code, so that the ruling stands if those lines are struck.

I edited no repository file. All four worktrees I touched were clean before and after (`git status --short` empty at `a0e8e47f`, `6c73caf4`, `b859317c`, and the S2 lane worktree at `a0e8e47f`). Scratch is under `/tmp/samesig/`.

## 1. Terms used in this ruling

Each term is given here once, from what is physically on disk, and is used only in this sense below.

| Term | Meaning |
|---|---|
| Battery gate | The check that a laptop was on external power, not charging, with battery current at or under 200 mA, both just before and just after a measured span. Charging draws power that the energy instruments would book to the workload. |
| Battery reading | The captured text output of one `ioreg` call. It is stored as a file, `raw/battery_float.pre.ioreg` or `raw/battery_float.post.ioreg`. |
| Envelope | One directory written by one run of the collector (`scripts/sample_quiet_predicate_evidence.py::collect`). It holds `session.json` (the record: start and end stamps, the two battery readings' digests and stamps), `rounds.jsonl` (the journal: one line per measurement round), and `raw/` (captured command output). |
| Authenticator | `battery_float.authenticate_quiet_session(envelope_dir)`. It re-reads the envelope's files, recomputes the battery verdict from the raw readings, and returns a verdict whose status is `pass`, `battery_float_confounded` or `battery_float_evidence_missing`. |
| Custody failure | The authenticator, or a summary, raising `CustodyFailure` (or its subclass `CustodyUnreadable`) because recorded bytes are missing, unreadable, or do not hash to what the record says. It is an exception. It is never written into a summary as a status, and no summary is written when it is raised. |
| Summary | `summary.json`, written by `pilot_summary` (called by the night executor) or by `summarize` (called on a directory of envelopes). |
| Routing | The summary's per-envelope decision: keep the envelope's numbers, exclude the envelope with a reason, or blank the whole night under a battery status. |
| No-record carve-out | Amendment 32 item (1): an envelope whose collector exited non-zero and that holds no `session.json`, no `rounds.jsonl` and no `raw/round-*` directory is excluded with reason `collect_error` without authentication, because nothing was recorded whose custody could be lost. |
| Historical set | `configs/battery_float/historical_bundles.json`: 69 digests of measurement bundles recorded before the battery gate existed. A bundle with no battery readings is admitted with the label `unobserved_historical` only if its digest is in this set; otherwise the reader refuses it as `prospective bundle`. |
| Bundle | One directory holding one measurement run (`metadata.json`, `power_trace.csv`, and others). |
| Builder | `scripts/build_battery_float_historical_bundles.py`. It rebuilds the historical set from the repository at commit `1417c0c4` and prints what it found and did not include. |
| Mutant | A copy of the code with one condition deleted or changed, run against the tests. A mutant that passes every test shows that no test depends on that condition. |

## 2. Rulings at a glance

| Question | Ruling |
|---|---|
| Q-A1 | The A→B→A case is **outside** the threat the battery gate must close. No production process can produce it. The probe produced it only by replacing the authenticator function inside the summary's own process. |
| Q-A2 | **Option (a).** Keep the before/after comparison. Pin the journal comparison, the presence comparison and the no-third-read rule. Record the reading of amendment 32 item (2) and the residual. Amendments 44 and 45. `battery_float.py` stays byte-identical. Option (b) is specified in §A2.4 as the named cure if a reopening condition of amendment 45 is ever met. |
| Q-A3 | The revert of F7 is **upheld**. Amendment 46. |
| Q-B1 | Enumeration by text scan is **not** what decides the set, so F2 is not a structural defect of the set. A pattern fix is sufficient, with the scan's role stated. Amendment 47. |
| Q-B2 | **Yes, per entry, not per bundle.** The witness must fail when a cited entry's name is found on disk only on bundles with other bytes. It must not fail on a bundle that merely shares a name, because 177 honest bundles do. Amendment 48. |
| Q-B3 | **Confirmed.** Opus SF-1 to SF-3 and Sol F3 to F5 are test and label fixes with no change to any ruled text. Closure rows are in §B3. |

---

# Part A: S2

## A1. Q-A1: is A→B→A inside the threat?

### A1.1 What the case is

The summary does three things to an envelope, in this order, at `a0e8e47f` (`joulewise/quiet_predicate_campaign.py:1205-1217`, and the same shape at `scripts/sample_quiet_predicate_evidence.py:1507-1522`):

```
time ─────────────────────────────────────────────────────────────────▶

summary:   [read 1]        [ authenticator runs ]        [read 2]   [compare]  [route]
           b0, j0          reads session.json,            b1, j1    b0==b1 ?   from b0, j0
                           rounds.jsonl, two raw files              j0==j1 ?

file on    A ────────────▶ B ───────────────────────────▶ A
disk:      (non-passing)   (passing, present only          (non-passing,
                            while the authenticator         restored before
                            reads)                          read 2)
```

Every element, named:

- `read 1` and `read 2` are the summary's two reads of `session.json` (bytes `b0`, `b1`) and of `rounds.jsonl` (bytes `j0`, `j1`).
- `A` is a `session.json` whose battery pair does not pass. In the probe it is a record with its `post` reading removed.
- `B` is a `session.json` whose battery pair passes.
- `compare` raises a custody failure if `b0 != b1` or `j0 != j1`.
- `route` is the routing defined in §1.

In this sequence the authenticator returns `pass` for B, the comparison sees A equal to A, and routing proceeds from A under a `pass` verdict. The summary is written as a passing night.

### A1.2 Executed evidence

**P1. The charge's probe, re-run at the current head.**

```
$ cd /Users/edr/code/JouleWise-wt-samesig-92472459   # a0e8e47f
$ PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_s2_aba_probe.py
pilot_direct_status battery_float_evidence_missing
pilot_report SPREAD_RECORDED battery_rows 0 retained 12 summary True
summarize_direct_status battery_float_evidence_missing
summarize_report complete summary True source_status battery_float_evidence_missing
```

Reproduced. Both call sites write a passing summary.

**What the probe needed.** It calls `unittest.mock.patch.object(battery_float, 'authenticate_quiet_session', side_effect=transient_pass)`. The replacement function writes B, calls the real authenticator, and writes A back in a `finally` clause. So the probe needed three things at once:

1. code running **inside the summary's own Python process**, replacing the authenticator;
2. the passing bytes B in hand before the call;
3. write access to the envelope.

It did not use a second process or any timing. A party holding (1) does not need the file swap at all: it can replace the authenticator with a function that returns `pass`.

**P2. A plain write with no timing does the same thing** (`/tmp/samesig/static_forge_probe.py`, part 1). Same night, same non-passing envelope 5. One ordinary write of B, left in place, then the unpatched `pilot_summary`:

```
1a before_forge_status battery_float_evidence_missing
1b static_forge SPREAD_RECORDED battery_rows 0 retained 12 reauth pass
```

The authenticator recomputes the verdict from the raw readings, and checks them against digests that are stored in `session.json` itself. Nothing in the envelope is signed. So a writer who can write the envelope can write a complete passing envelope, and the authenticator accepts it. A→B→A gives that writer nothing B alone does not give, and leaves a worse trail: after A→B→A the files on disk contradict the summary, so re-running the summary exposes it.

**P3. A change that is not undone is caught** (same script, part 2). The wrapper writes B during the call and leaves it:

```
2 one_way CustodyUnreadable envelope-05: session.json changed during authentication summary False
```

### A1.3 Who could produce A→B→A on a real night

A→B→A needs a writer that **puts back bytes a file held earlier**. I checked every writer of the two files.

| Writer | Where | What it writes | Can it restore earlier bytes? |
|---|---|---|---|
| Collector, first write | `sample_quiet_predicate_evidence.py:1112` | `session.json` with the `pre` reading only | No. It is the first state. |
| Collector, round appends | `:1168` | one line appended to `rounds.jsonl` per round | No. The file only grows. |
| Collector, finalization | `:1235`, `:1237` | the journal rewritten whole, then `session.json` with `end_stamp`, `post`, `journal_rows` | No. It writes the last state once and returns. |
| Collector, refusal path | `:1109-1110` | a refusal `session.json`, then an empty `rounds.jsonl` | No. Written once. |
| Executor, `record_attestation` | `quiet_predicate_campaign.py:769`, called at `:1695` | `session.json` rewritten with an attestation added | No. It runs inside the envelope loop, after the collector exits and before `pilot_summary` (`:1776`). It adds a key. |
| Executor, `cleanup_record` | `:315`, called at `:1768` | kills leftover child processes | Writes no envelope file. |
| Authenticator | `battery_float.py:955-1023` | nothing | It only reads (`read_bytes`, and `os.open(..., O_RDONLY \| O_NOFOLLOW)`). |

No production writer restores earlier bytes. Each file moves through its states in one direction.

The one real-night hazard is a **straggler**: a collector that survived `cleanup_record` and is still writing while the summary runs. A straggler moves a file forward (A→B), never back. P3 shows that the comparison raises on that.

A file-sync service or a backup restore could in principle put an old file back. For that to pass the gate, the restore would have to land inside the authenticator's read of one envelope (1.7 ms measured, §A2.4), and the newer bytes would have to pass while the older ones did not. I rule this negligible. NOT EXECUTED: no test of a sync service.

### A1.4 Ruling

A→B→A is outside the threat. The gate exists to stop a number measured on a charging laptop from being published by a pipeline that is working as designed. It cannot, and does not claim to, resist a party who can write the evidence directory, because such a party can write passing evidence directly (P2). The before/after comparison closes the case that can occur on a real night (P3).

## A2. Q-A2: the binding

### A2.1 Ruling: option (a)

Reasons, in order of weight:

1. **It closes every case a real night can produce** (§A1.3, P3).
2. **Option (b) and option (c) defend against nothing that is not already open.** P2 passes under any binding, including a private snapshot and an authenticator that returns its bytes.
3. **Option (b) adds a way to be wrong.** The authenticator refuses a `session.json` that is a symbolic link (`battery_float.py:814`) and refuses a raw path that crosses one (`:842-849`). A copy by bytes follows the link and produces a regular file. Unless the copy step re-implements each of those checks, a custody failure at the source becomes a `pass` on the snapshot. That is the defect class "custody converted to a status", which this lane has spent two rounds closing.
4. **Option (c) changes a frozen, merged module** for no gain under reason 2.
5. **Cost.** Option (a) is test rows only. Option (b) is a third production round on both call sites, followed by another review round.

The same-signature rule asks whether a third round would hit the same defect again. Under option (a) it cannot, because the ruling moves the A→B→A case out of the defect set by stating the fact that closes it (amendment 45) and the conditions that reopen it.

### A2.2 Executed evidence for the unpinned conditions

I did not re-run the two lens mutants for the journal comparison. NOT EXECUTED by me: M4b and M4d (Opus), and the same mutant in Sol's V5. I rely on both lenses having run it independently with the same result (`Ran 194 tests … OK`, `Ran 101 tests … OK`, `Ran 36 tests … OK`). I read the code and confirm that no test in the diff appends to or deletes `rounds.jsonl` after authentication.

### A2.3 Exact text

**Amendment 44 (S2; replaces fix-contract item F4 as the ruled text; adds a reading to amendment 32 item (2) and to amendment 35 item 2; S2's existing scope).**

44. **The summary routes from bytes that it has shown unchanged across authentication.** In `pilot_summary` and in `summarize`, for every envelope that is not decided by amendment 32 item (1), in this order:

    (a) Read the bytes of `session.json` and of `rounds.jsonl`. Each result is either the file's bytes or "absent". Call the two results the *before pair*. This read decides nothing.

    (b) Call `battery_float.authenticate_quiet_session(<envelope directory>)`. A `CustodyFailure`, including `CustodyUnreadable`, propagates as amendment 32 rules.

    (c) Read both files again. Call the two results the *after pair*.

    (d) If any read in (a) or (c) failed for a reason other than absence, raise `CustodyUnreadable("<envelope name>: <file name> unreadable: <reason>")`. If the after pair differs from the before pair in either file, **by bytes or by presence**, raise `CustodyFailure` or a subclass of it (the code raises `CustodyUnreadable`, which stands), with the text `<envelope name>: session.json changed during authentication` or `<envelope name>: rounds.jsonl changed during authentication`. Both raises come before any routing. No summary is written.

    (e) Every later decision about that envelope, and every summary field taken from it, is computed from the verdict and from the before pair, parsed once. Neither function opens that envelope's `session.json` or `rounds.jsonl` a third time.

    **Reading of amendment 32 item (2).** Its words "runs before the summary's own `session.json`/`rounds.jsonl` read" mean: before any read whose content the summary acts on. The read in (a) is not such a read until (d) has shown its bytes equal to a read taken after the authenticator returned. Amendment 35 item 2 is met for the same reason: no decision to exclude, excuse, route or skip is taken before the call has returned. A later edit that moves the routing read after the call and drops (c) and (d) reopens round-1 finding B2 and is forbidden by this text.

**Amendment 45 (S2; records a residual; no code).**

45. **What the comparison proves, what it does not, and what closes the difference.**

    *Proved by amendment 44 (d):* each file held the same bytes before the authenticator started and after it returned.

    *Not proved:* that each file held those bytes at the instant the authenticator read it.

    *What closes the difference:* no production writer of `session.json` or `rounds.jsonl` ever writes bytes that the file held at an earlier time. The writers are the collector (first write, round appends, finalization, refusal path) and the executor's `record_attestation`. Each moves a file forward through its states and never back. Under that fact, equal before and after means unchanged in between.

    *Residual, accepted:* a writer that writes passing bytes and restores the earlier bytes while the authenticator runs. It is outside the battery gate's threat for two reasons. No production process does it. And any writer able to do it can write a complete passing envelope with one ordinary write, which no binding of the summary to the authenticator prevents, because the envelope's digests are stored in the envelope.

    *Reopening conditions.* This amendment is revisited by a cold gate if any of these becomes true:
    1. a change adds a writer of `session.json` or `rounds.jsonl` that can run while a summary runs and that can restore earlier bytes (a rollback, a retry that rewrites a first-write record, a sync step);
    2. a change makes a summary run while collectors are expected to be writing;
    3. envelope evidence becomes signed or is otherwise made unforgeable by a writer of the directory, so that the undone write becomes the cheapest remaining way to a false pass.

    If it is reopened, the cure is the private snapshot specified in ruling BFGS-SAMESIG-01 §A2.4, not a further comparison.

### A2.4 Option (b), specified for the record (not ruled in)

Recorded so that a reopening under amendment 45 does not start from nothing.

**What the authenticator reads** (`battery_float.py:955-1023`, traced by reading the code at `a0e8e47f`, which is byte-identical to base for this file):

| File | When it is read | How |
|---|---|---|
| `session.json` | always | `lstat`; refused if missing, a symbolic link, or not a regular file; then `read_bytes`; strict UTF-8; duplicate JSON keys refused |
| `rounds.jsonl` | only if the session has a `battery_float` key **and** is either completed (has `end_stamp`) or a refusal record | same checks as above |
| `raw/battery_float.pre.ioreg` | only if the stored `pre` record is well formed (phase, identity, path, digest, wall time) | `lstat` on the envelope directory, on `raw/`, and on the file, each refused if a symbolic link; `resolve()` must stay inside the envelope; opened `O_RDONLY \| O_NOFOLLOW`; a read error counts as "no bytes", which then fails the digest check as a custody failure |
| `raw/battery_float.post.ioreg` | same, for `post` | same |

It reads nothing else. A complete snapshot is these four files at most.

**Cost on a real envelope.** Measured on `…/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-01`:

```
snapshot_bytes 610198 seconds 0.0017 status battery_float_evidence_missing ('pre evidence missing: phase not recorded',)
```

`session.json` is 279,942 bytes and `rounds.jsonl` is 330,256 bytes. The whole envelope is 144,859,814 bytes, of which the snapshot copies 0.4 %. For a twelve-envelope night that is about 7.3 MB and 20 ms. NOT EXECUTED: a real envelope that carries the two battery readings. None exists yet, because S2 is what adds them. The fixture readings are a few kilobytes each.

**The condition that any snapshot must meet.** The copy step must apply, at the source, every file-type check in the table above and raise the authenticator's own exception class for each. Absent files must stay absent in the snapshot. Each of those is a test row with its own mutant.

### A2.5 Test rows for amendments 44 and 45

Every row goes through the real `pilot_summary` or the real `summarize`. Each wraps the real authenticator with a function that calls it and then acts on the envelope, as the two existing session-swap rows do.

| Row | Call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R44-1 | `pilot_summary` | after the authenticator returns `pass` for envelope 5, one line is appended to that envelope's `rounds.jsonl` | `CustodyFailure` matching `rounds\.jsonl changed during authentication`; no `summary.json` | the journal comparison deleted in `pilot_summary` (Opus M4b). Under it the summary is written. |
| R44-2 | `summarize` | the same, on the one fixture envelope | the same | the journal comparison deleted in `summarize` (Opus M4d) |
| R44-3 | `pilot_summary` | after the authenticator returns, `rounds.jsonl` is deleted | the same raise | the comparison applied only when both reads returned bytes (`if j1 is not None and j1 != j0`) |
| R44-4 | `summarize` | the same | the same | the same counterfactual in `summarize` |
| R44-5 | `pilot_summary` and `summarize` (two rows) | envelope starts non-passing (A); the wrapper writes passing bytes (B) **before** calling the real authenticator and leaves them | `CustodyFailure` matching `session\.json changed during authentication`; no `summary.json` | the session comparison deleted (Opus M4a, M4c). Under it a passing summary is written. Executed here as P3 for `pilot_summary`. |
| R44-6 | `pilot_summary` and `summarize` (two rows) | a clean passing night; a spy counts every open of each envelope's `session.json` and `rounds.jsonl` made by the call site while the authenticator is not running | exactly two opens of each file per envelope | routing that reads `session.json` a third time after the comparison (Opus M4e). Opus classed M4e as unkillable by a behaviour test. A read count kills it. |
| R44-7 | `execute` | the existing full-executor rows with the real `record_attestation` | no raise on an honest night | none added. Name the existing rows in the report. This row shows that amendment 44 (d) does not raise when nothing writes during the summary. |

Amendment 45 adds no row. A test asserting that the undone write passes would pin a non-defence.

## A3. Q-A3: the F7 revert

### A3.1 Ruling: upheld

### A3.2 Executed evidence

The same probe (`/tmp/bfgs_s2_f7_window.py`: the real `collect` on the refusal path with the session write made to fail, then the real `pilot_summary` with `collector_exit` 3), at both commits:

```
@ a0e8e47f (revert applied; session.json first)
collect OSError injected refusal session write failure
records session False journal None
pilot SPREAD_RECORDED

@ 6c73caf4 (F7; rounds.jsonl first)
collect OSError injected refusal session write failure
records session False journal b''
pilot CustodyUnreadable session.json unreadable: missing summary False
```

Under F7 an honest failed write (a full disk, for example) left an empty journal and no session record. The no-record carve-out requires that no `rounds.jsonl` exist, so it did not apply, and the whole night was lost to a custody failure. Under the reverted order the same failure leaves nothing, the carve-out applies, and the night is summarized with that one envelope excluded.

### A3.3 Why no order closes both windows

There are two files and no way to publish both in one step. Whichever is written first, a process killed between the two writes leaves one file without the other.

| Order | A **failed** first write leaves | A **kill between** the writes leaves |
|---|---|---|
| `session.json`, then `rounds.jsonl` (base, and now `a0e8e47f`) | nothing: carve-out applies | a refusal record with no journal: the authenticator raises `round journal missing` |
| `rounds.jsonl`, then `session.json` (F7) | an empty journal alone: custody failure | the same empty journal alone: custody failure |

The reverted order is better in the first column and equal in the second. Its kill window is also shorter: it spans one `write_text("")`, where F7's spanned the whole atomic session write (temporary file, `fsync`, rename).

The remaining window cannot be carved out. A refusal record with no journal is exactly what is left when someone deletes the journal of a complete refusal record. The authenticator raises `round journal missing` for it (`battery_float.py:968-969`; executed by the Opus delta's probe `f7probe_journal.py`, NOT re-run by me). Fix-contract item F3 row (i) rules the mirror state, a journal with no session record, a custody failure for the same reason. The window fails closed and it is rare: the refusal path finishes in seconds.

### A3.4 Exact text

**Amendment 46 (S2; withdraws fix-contract item F7; S2's existing scope).**

46. **Order of the two writes on the collector's refusal path.** On the path where `collect` refuses before capture, the collector writes `session.json` first and the empty `rounds.jsonl` second, as it did before S2. Fix-contract item F7 is withdrawn.

    Two consequences are recorded:

    (i) If the `session.json` write fails, neither file exists. Amendment 32 item (1) applies and the envelope is excluded `collect_error`.

    (ii) If the collector is killed after `session.json` exists and before `rounds.jsonl` exists, the envelope holds a refusal record with no journal. The authenticator raises `round journal missing` and no summary is written. This is accepted. It is not carved out, because the same files result from deleting the journal of a complete refusal record.

### A3.5 Test rows for amendment 46

| Row | Call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R46-1 | `collect` | the refusal path with the session write made to raise | the raise propagates; neither `session.json` nor `rounds.jsonl` exists | journal-first order. Exists at `a0e8e47f` as `test_refusal_session_write_failure_leaves_no_journal`. |
| R46-2 | `collect`, then `pilot_summary` | the directory R46-1 leaves, as envelope 5 of a twelve-envelope night, `collector_exit` 3 | a summary is written; envelope 5 is excluded with `collect_error` and `incomplete_interior_support`; no custody failure | journal-first order. Under it `pilot_summary` raises `CustodyUnreadable`. **Missing at `a0e8e47f`.** R46-1 alone does not pass its result through the reader, which is how F7's defect went unseen. Executed here as the probe in §A3.2. |
| R46-3 | `pilot_summary` | envelope 5 holds a complete refusal `session.json` and no `rounds.jsonl`, `collector_exit` 3 | `CustodyFailure` matching `round journal missing`; no `summary.json` | a carve-out widened to treat a session record with no journal as "no record". If an existing row already pins this, name it in the report and add none. |

---

# Part B: S1

## B1. Q-B1: is the text scan structurally unsound?

### B1.1 What the scan decides, and what it does not

The builder does two separate things.

1. **It writes the set.** An entry is written only for a digest that comes from one of three sources named in a constant, `INCLUDED_SOURCES` (`build_battery_float_historical_bundles.py:24-28`, used at `:187-200`): the detection-floor file, the RPT001 input manifest, and the tracked fixture bundles. The first two are JSON, parsed by key. The third is a directory walk that hashes committed bytes.
2. **It lists what it did not include.** It scans every tracked file for digests that sit near a key whose name looks like a bundle digest, and prints each one with a reason. It exits non-zero if a (key, schema) pair has no row in its classification table.

The text scanner that F2 faults feeds only the second. So the design the question proposes, "enumerate from a closed, declared list of citation sources", **is already what decides the set**. It was ruled as amendment 40's Inclusion paragraph and is implemented.

### B1.2 Executed evidence

**P4. The charge's probe, re-run at `b859317c`.**

```
$ cd /Users/edr/code/JouleWise-wt-s1cg-92472459
$ PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_text_candidate_probe.py
candidates []
build ([], [])
```

Reproduced. The cause is `TEXT_CANDIDATE` at `:33-35`, which names two literal keys, where amendment 40 rules "the same key pattern" as for JSON keys.

**P5. What the ruled pattern finds that the two literals miss** (`/tmp/samesig/pattern_probe.py`, over the tree at `1417c0c4`):

```
text_lines_hex_total 33506 non_utf8_files 40 unparseable_json 22
extra_candidates 3 distinct 3
extra 1 complete_bundle_sha256 docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md
extra 1 bundle_sha256_census docs/process_traces/2026-09-04-peer-audit/35-enclosure-refuter-execution.md
extra 1 bundle_sha256 docs/site/run_state.html
extra_in_set []
```

Three more quoted digests. None is a set entry. (Opus counted four with a different tokenizer. NOT EXECUTED: I did not reconcile the fourth.)

**P6. Which file types hold text candidates** (`/tmp/samesig/ext_probe.py`):

```
by_extension {'.md': 48, '.html': 1}
```

Every text candidate at base is in a documentation file. The one digest in a code file, `PINNED_BUNDLE_SHA256`, sits on the line after its name, so no line scan finds it. The builder finds it with a rule written for that file (`:162-165`), which amendment 41 already governs.

**P7. The forward check** at `b859317c`: `forward check: byte-identical entries=69`, with 119 listed lines.

### B1.3 Ruling

A pattern fix is sufficient, and the scan's role is now stated in the text so that the next review does not read a listing miss as a set miss.

Reasons:

1. **A scan miss cannot change the set.** It can only leave a quoted digest out of the printed list. P5 shows `extra_in_set []`.
2. **The two misses differ in kind.** Round 1 built the set from the wrong sources and omitted 50 real entries. F2 omits nothing from the set. The signature "set enumeration miss" recurred in name only.
3. **No scan of free text can be complete.** P6 shows a digest one line below its name. A text file holds 33,506 digest-shaped strings at base (P5), so listing all of them without a key is not a usable list either. The scan is an aid. The pattern-free check already exists: the reverse check compares every digest-shaped string in every tracked file against the digests of the bundles on disk.
4. **The miss that remains fails closed.** A digest quoted in text with no key on its line, for a bundle that is not on disk, goes unlisted. If that bundle ever appears, the reader refuses it as `prospective bundle` until a cold gate admits it.

### B1.4 Exact text

**Amendment 47 (S1; amends amendment 40, "Scan", second bullet; S1's existing scope: the builder and `tests/test_bundle_read.py`).**

47. **One key pattern for text, and what the scan is for.**

    *Role.* The contents of the historical set come only from the three sources in amendment 40's Inclusion table. The scan adds no entry and removes none. It produces the printed list of digests that were found and not included, and it stops the builder on a pair that it cannot classify. The scan is not evidence that the list is complete. The reverse check is.

    *Rule for text.* "Text" here means every tracked file that is not parsed as JSON or JSONL, and every `.json` or `.jsonl` file that fails to parse. For each line of text:
    - a *key token* is a maximal run of letters, digits and underscores that is not itself 64 hexadecimal characters and that matches the pattern used for JSON keys (the builder's constant `KEY`: the name contains `bundle` and one of `sha256`, `digest`, `tree`);
    - if the line holds at least one key token, every 64-hexadecimal string on the line is a candidate;
    - the candidate's key is the nearest key token before it on the line, or, if none comes before it, the first one after it.

    The two-literal pattern `TEXT_CANDIDATE` is removed. The rule for Markdown tables and the rule for `PINNED_BUNDLE_SHA256` (amendment 41) are unchanged.

    *Class of a text candidate.*
    - If the classification table has a row for its (key, file), it takes that row's class.
    - Otherwise, if the file's name ends in `.md`, `.html` or `.txt`, its class is `quoted`, and it is listed with the reason `quoted in text, not a citation source`. The table's two rows for schema `prose` are removed, since text has no producing code to cite.
    - Otherwise the builder exits non-zero with `unclassified candidate pair`, naming the key and the file. A digest under a bundle-named key in a file that is neither documentation nor parsed data may be a citation source that nobody has classified.

    *Skips are printed.* A file that is not valid UTF-8 is named on stderr as `skipped non-utf8 <name>`. A `.json` or `.jsonl` file that fails to parse is named, as today, and is then scanned as text.

    *Unchanged.* The set's 69 entries, its bytes, and `HISTORICAL_BUNDLE_SET_SHA256`. The forward check must print `byte-identical entries=69` before and after this amendment.

### B1.5 Test rows for amendment 47

Each row calls the production function `build(root, names)` on a temporary tree, as the charge's probe does.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R47-1 | `other.md` holding `bundle_tree_sha256: ` followed by 64 `a` characters | one listed candidate: key `bundle_tree_sha256`, class `quoted`, reason `quoted in text, not a citation source`; no entry | the code at `b859317c`, which returns `([], [])` (P4) |
| R47-2 | `other.md` holding the digest first and the key after it on the same line | one listed candidate with that key | a rule that accepts only a key before the digest |
| R47-3 | `other.toml` holding the line of R47-1, with no classification row | `ValueError` matching `unclassified candidate pair` | a rule that classes every text candidate `quoted` |
| R47-4 | `broken.json` that fails to parse and holds the line of R47-1 | one listed candidate, and the file named as unparseable | today's `continue` at `:135`, which skips the file |
| R47-5 | the real tree at `1417c0c4` | the forward check is byte-identical with 69 entries; the three files of P5 appear in the listed output | none for the first half (it pins "unchanged"); the second half is RED at `b859317c` |

## B2. Q-B2: the witness's semantics

### B2.1 Executed evidence

**P8. The charge's probe, re-run at `b859317c`.**

```
$ PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs_reverse_probe.py
reader_before unobserved_historical
reader_after battery_float_evidence_missing ('prospective bundle',)
witness_exit 0
witness_tail ['forward check: byte-identical entries=69', 'witness bundles=1']
```

Reproduced. The reader refuses the changed copy. The witness prints nothing about it and exits zero.

**The cause.** `witness()` at `:229-240` looks up each encountered bundle's digest in the set. Its only comparison of names runs **after** a digest hit (`:237`). A bundle whose bytes changed has a digest that hits nothing, so nothing is compared. Amendment 40 already rules: "A mismatch between an included entry and the recomputed digest of the bundle it names is a finding to return." As implemented that sentence can never fire, because a digest that hits cannot mismatch.

**P9. How often an honest bundle shares a name with a set entry and has other bytes** (`/tmp/samesig/namesake_probe.py` and `namesake2.py`, over `/Users/edr/code/JouleWise/runs*`, 1402 bundles, 7.5 s):

```
entries 69 distinct_run_ids 61 run_ids_shared_by_entries [eight ids, each held by one floor entry and one fixture entry]
bundles_seen 1402 seconds 7.5 {'match': 56, 'name_hit_digest_miss': 206}
entries_named_on_disk 65 entries_matched 56 entries_named_but_never_matched 9
by_source ('analysis/rpt001-v2/input_manifest.json', 'matched') 6
by_source ('df-ph-decode-floor-mint1.json', 'matched') 50
by_source ('tests', 'named_only') 9
by_source ('tests', 'not_on_disk') 4
honest_corpus distinct_namesake_bundles 177 citation_entries_named_only 0 => exit 0
```

**177 honest bundles** name a set entry whose digest they do not have. Counted per run root in a second pass:

```
namesake_root runs 51
namesake_root runs_window_a5_20260723 51
namesake_root runs_recal6_20260719 40
namesake_root runs_recal5_20260719 11
namesake_root runs_window_a7_20260723 10
namesake_root runs_window_c_20260726 8
namesake_root runs_window_a6_20260723 4
namesake_root runs_window_a4_20260722 1
namesake_root runs_window_d_20260726 1
namesake_total 177 roots 9
match_roots {'runs': 6, 'runs_window_a10_20260725': 10, 'runs_window_c_20260726': 40}
shared_ids 8 Counter({('df-ph-decode-floor-mint1.json', 'tests'): 8})
```

The same run ids were used again each time a campaign was collected again. The cited bundles are found intact in three roots (`match_roots`: 6 + 10 + 40 = 56).

Eight run ids are each held by two entries: one floor entry and one fixture entry, with different digests, because the fixture is a cut-down copy of the run. A bundle can therefore match one entry and be a namesake of the other. The 8 namesakes in `runs_window_c_20260726`, where 40 floor entries match, agree in count with that. NOT EXECUTED: I did not check those eight bundle by bundle.

So **a run id does not identify a bundle. Only a digest does.** A rule that fails on any bundle whose name hits and whose digest misses would raise 177 false findings on the honest corpus and would be switched off.

**P10. The per-entry rule on three cases** (`namesake2.py`), using a copy of `example-mac-mlx-local__r1`:

```
intact_copy_alone distinct_namesake_bundles 0 citation_entries_named_only 0 => exit 0
modified_copy_alone distinct_namesake_bundles 1 citation_entries_named_only 1 => exit 1
modified_copy_beside_original distinct_namesake_bundles 178 citation_entries_named_only 0 => exit 0
```

### B2.2 Ruling

Yes: the witness must compare by name when the digest misses. The unit of failure is the **set entry**, not the encountered bundle.

- An entry whose cited bytes are found on some encountered bundle is confirmed. Other bundles that share its name are printed and do not fail the run.
- An entry whose name is found but whose bytes are found nowhere under the given roots is a finding, and the witness exits non-zero. That is the state of the charge's probe (P8, and `modified_copy_alone` in P10).
- The nine fixture entries in that state on the honest corpus do not fail the run. A fixture entry's bytes are the committed files, which the builder hashes itself. The bundles on disk with the same run id are the full runs that the fixtures were cut from.

The witness still writes nothing and still decides nothing about the set.

### B2.3 Exact text

**Amendment 48 (S1; amends amendment 40, "Reverse check"; S1's existing scope: the builder and `tests/test_bundle_read.py`).**

48. **The reverse check compares by name as well as by digest, and reports per entry.**

    *Terms.* An *encountered bundle* is a directory under a witness root that holds `metadata.json`. It **names** a set entry when its directory name, or the `run_id` in its `metadata.json`, equals the entry's `run_id`. It **matches** the entry when its recomputed digest, of the entry's kind (complete or tree), equals the entry's digest.

    *Per entry.* For each of the set's entries the witness prints one line, `witness_entry <state> <kind> <run_id> <digest> <source>`, where the state is:
    - `matched`: at least one encountered bundle matches it;
    - `named_only`: no encountered bundle matches it, and at least one names it;
    - `absent`: no encountered bundle matches or names it.

    *Per bundle.* For each encountered bundle that names an entry and does not match it, the witness prints `witness namesake <kind> <bundle path> <run_id> expected=<entry digest> observed=<recomputed digest>`. These lines never change the exit status. The forcing fact: at `1417c0c4`, 177 bundles under `/Users/edr/code/JouleWise/runs*` name an entry that they do not match, because run ids were used again when campaigns were collected again. Where two entries hold one `run_id` (eight ids do), each entry is judged on its own, so one bundle may match one of them and be printed as a namesake of the other.

    *Exit status.* The witness exits non-zero if any entry whose source is `df-ph-decode-floor-mint1.json` or `analysis/rpt001-v2/input_manifest.json` is `named_only`. Such an entry's digest was computed from a bundle on disk, so this state means that the bundles carrying the cited name no longer hold the cited bytes. An entry whose source is a tracked fixture bundle is printed in whatever state it has and does not change the exit status, because the forward check hashes its committed bytes.

    *Scope of the result.* The states describe the roots that were given. The ruled invocation is over `/Users/edr/code/JouleWise/runs*`. Expected there at `1417c0c4`: 56 entries `matched` (50 floor, 6 RPT001), 9 fixture entries `named_only`, 4 fixture entries `absent`, 177 bundles on namesake lines, exit status zero.

    *Unchanged.* The witness writes nothing. It is a report and never an input to the set. The checks made on a digest hit (the entry's `run_id` equals the bundle's directory name; an included digest has a tracked citation) remain, as does the refusal on a hit in a file that is neither an included source nor prose.

### B2.4 Test rows for amendment 48

Each row calls the production function `witness(...)`, or `main` with `--witness`, on temporary roots holding copies of a tracked fixture bundle. Where a row needs an entry with a citation source, the test passes `witness` a row list with that one entry, and a tracked-file list in which that digest is cited.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R48-1 | one root holding an intact copy of the entry's bundle | `witness_entry matched …`; no namesake line; exit zero | none (it pins the honest case; RED at `b859317c` only for the new line) |
| R48-2 | the same copy with one byte appended to `power_trace.csv`, alone | `witness_entry named_only …`; one namesake line carrying both digests; exit non-zero | the code at `b859317c`, which exits zero (P8) |
| R48-3 | two roots: the changed copy and an intact copy | `witness_entry matched …`; one namesake line; exit zero | a per-bundle rule that fails on any namesake. P9 shows that rule fails 177 times on the honest corpus. |
| R48-4 | an entry whose source is a tracked fixture, with only a changed copy present | `witness_entry named_only …`; exit zero | a rule that fails on every `named_only` entry whatever its source |
| R48-5 | a bundle whose directory name differs from the entry's `run_id` and whose `metadata.json` `run_id` equals it, changed by one byte, alone | `named_only`; exit non-zero | a rule that compares directory names only |
| R48-6 | local corpus only (skipped when absent): the ruled invocation | the counts of amendment 48's "Scope of the result" | none; it pins the expected report |

## B3. Q-B3: the remaining findings

### B3.1 Ruling: confirmed

All six are fixes to tests or to a printed label. None needs a change to a ruled text. In each case the production behaviour that the text rules is either already correct (the pin is what is missing) or the text already says what the label should be.

### B3.2 Executed evidence

| Finding | What I ran | Result |
|---|---|---|
| Opus SF-1, Sol F3 | In a scratch copy of `b859317c`, deleted `and row["tree_identity"] == "joulewise.bundle-tree.nul-v1"` from `bundle_read.py:247`; ran `python3 -m unittest tests.test_bundle_read -k wrong_tree_identity` | `Ran 1 test in 0.015s  OK`. The mutant survives. Confirmed. |
| Opus SF-2 | In the same scratch copy, changed `except BundleReadError` at `bundle_read.py:488` to a clause that never matches; ran `tests.test_bundle_read tests.test_bfgs_window_consumers` | `Ran 110 tests … FAILED (failures=1, errors=1, skipped=1)`, **identical** to the unmutated scratch copy. The two failing tests need a git repository, which the scratch copy is not. The mutant adds no failure. Confirmed. |
| Sol F4 | Ran the builder's `main(['--check'])` from a copy in which the `PINNED_BUNDLE_SHA256` row's class is `complete` | `forward check: byte-identical entries=69`, `rc 0`. Confirmed. |
| Opus SF-3, Sol F5 | Read the stderr of the forward check (P7) | `listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d2…e213: source not named by amendment 40`, and the same for the other five. Amendment 40 rules that these are "listed as a duplicate". Confirmed. The cause is at `:202`: the reason is chosen while candidates are still arriving, and this file is visited before the input manifest. |

### B3.3 Closures for S1's next fix round (no amendment number)

| Finding | Ruled text it conforms to | Closure | Must fail (RED) under |
|---|---|---|---|
| Opus SF-1 = Sol F3 | amendment 39, test list | Split the test. The wrong-identity row gets a digest that is not already in the set. Add its twin: the same row with the right identity is accepted. The duplicate row stays as its own case. | the identity condition deleted at `bundle_read.py:247` |
| Opus SF-2 | amendment 37 ("never raises"), amendment 42 (a) | Two rows. Through `BundleReader`: a bundle with no battery key whose `config.json` is `[]` and whose `metadata.config_sha256` is bound to it raises `BatteryStatusRefusal` matching `prospective bundle \(config\.json does not re-validate`. Through `authenticate_window_members`: the same bundle as a window member gives `WindowBatteryRefusal`, not `CustodyUnreadable`. | the `except BundleReadError` clause at `:488` disabled |
| Opus SF-3 = Sol F5 | amendment 40 ("the second citation is listed as a duplicate") | Choose each listed reason after all inclusions are known. Add a builder row asserting that the six `artifact_manifest.json` digests carry `duplicate of included citation`. Run the forward check twice: set bytes and pin unchanged. | a candidate order in which `artifact_manifest.json` is visited before `input_manifest.json`, which is the order at `b859317c` |
| Sol F4 | amendment 41 | Assert that the digest `6945…06e9` is listed with class `file_digest` and its reason, and is not a set entry. | the row's class changed to `complete` |

Amendments 47 and 48 land in the same fix round. The round-2 seat now editing another worktree is not bound by this ruling until the magistrate issues its brief.

---

## 3. Kept intact

- **Custody is never a status.** Amendments 44 and 46 raise. Amendment 47 and 48 touch no reader. Row R46-3 pins the one place where a carve-out could have been widened.
- **Authentication precedes every exclusion decision.** Amendment 44's reading states why the read in (a) is not a decision. Amendment 32 item (1) remains the only exception.
- **`joulewise/battery_float.py` is byte-identical.** Option (c) is not ruled. Option (b) is recorded and not ruled in.
- **The historical set's 69 entries, bytes and pin are unchanged** by amendments 47 and 48.

## 4. Not executed

- The full S2 suites V1 and V2, and the full S1 suites. I ran targeted probes and targeted tests only.
- The two journal-comparison mutants (M4b, M4d). I rely on three independent lens runs.
- Any real envelope carrying the two battery readings. None exists before S2 lands.
- Any test of a file-sync or backup restore landing inside an authentication call.
- Opus's fourth extra quoted digest. I found three.
- The builder's own `--witness` over the full corpus. I ran my own per-entry probe over the same 1402 bundles with the builder's two digest functions.

## 5. Probes written in this session

| File | Purpose |
|---|---|
| `/tmp/samesig/static_forge_probe.py` | P2 and P3 |
| `/tmp/samesig/pattern_probe.py` | P5 |
| `/tmp/samesig/ext_probe.py` | P6 |
| `/tmp/samesig/namesake_probe.py`, `/tmp/samesig/namesake2.py` | P9 and P10 |
| `/tmp/samesig/s1/` | scratch copy of `b859317c` for the two reader mutants |
| `/tmp/samesig/builder_f4.py` | the builder with one class changed (Sol F4) |

## 6. Plain summary for Ed (5 lines)

1. **The file-swap trick in the night summary is not a real threat.** The summary reads an evidence folder, asks a checker (the "authenticator") whether the laptop was off-charge, and reads the folder again to confirm that nothing changed. A reviewer showed that swapping in good files only while the checker looks, then swapping the bad ones back, gets through. I ran it: it only works by replacing the checker inside the summary's own program, and anyone able to do that, or able to write the folder at all, can simply write good-looking files once. No normal program ever puts old bytes back.
2. **So the current check stays, with its untested halves now tested.** Four new rules ("amendments 44 to 46" in the project's numbering) keep the read-before and read-after comparison, require tests for the second file it compares, and write down exactly what is accepted as out of scope and what would reopen it. The checker's own code is not touched.
3. **The lead's bench change is upheld.** When the collector refuses to measure, it writes its record first and its empty log second, as it always did. The reverse order, tried in the last round, turned an ordinary failed write (a full disk) into the loss of a whole night. I reproduced both behaviours.
4. **The list of old measurements is complete and is not built by text search.** That list (69 runs recorded before the battery check existed) comes from three named files. The text search only prints digests that were seen and left out. It was too narrow, and widening it adds three printed lines and changes none of the 69 ("amendment 47").
5. **The cross-check against the disk must flag a changed run, judged per listed run and not per folder.** Today it stays silent if a listed run's files were altered. It must fail when a listed run's name is found only on altered copies. It must not fail merely because a folder shares a name, since 177 honest folders do: run names were used again each time a campaign was collected again ("amendment 48"). The six smaller review findings are test and label fixes with no rule change.
