# Cold gate BFGS-SAMESIG-01, erratum: ruling

Judge: Claude Fable 5.1, cold seat. One foreground session, no subagents, no background tasks.
Charge: `70-consult-samesig/30-erratum/00-charge.md` @ `10e3a0d2`. Working tree: `a0e8e47f` (S2 head).
Session clock: 19:35 to 19:50 PDT, 2026-09-26 (first `date` call 19:35:17; last before this file 19:45:22).

## 0. Contamination disclosure

I opened none of the forbidden files (RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, the decision log, memory bodies, skill files).

Four things reached my context without my asking, or as a side effect:

1. **The owner's global instruction file**, put there by the harness. It holds a writing standard and a pointer to orchestration doctrine. It states no position on any finding here. I followed its writing standard for the form of this document.
2. **This worktree's `CLAUDE.md`**, put there by the harness. It describes the Codex bridge only.
3. **The index of the memory directory**, put there by the harness: one title line per memory. I read no memory body. Three title lines touch this ruling's subject, and I name them so the magistrate can discount them:
   - a line saying that refusals aimed at an adversary who is the machine's own operator are over-engineering;
   - a line saying that gates must be sensible on science grounds;
   - a line saying that documentation and test-only changes get a light gate.

   My ruling on SF-B1 declines the refuter's "every new member needs a cold gate" and rules a lighter consequence. That agrees in direction with the second and third lines. I therefore rest it only on evidence executed here (§3.2: three of the refuter's five members write neither file, and its rule stays green on the change it is meant to catch).
4. **Four line numbers of `TASK_QUEUE.md`.** A content search over the worktree for the two file names matched that file. The search tool printed the line numbers and omitted the line text. I read none of its content.

I read, as the charge requires: the original charge, the ruling under review (`21-coldgate-fable-ruling.md`), the refuter's report (`11-opus-contract-refuter.md`), and the refuter's scratch scripts under `/tmp/opsg/`.

I did **not** read amendments 32, 35, 40 or 41 in their home rulings. Where the restated amendments cite them, the cited words are the ones quoted in the ruling under review.

**A worktree moved under me.** The S1 worktree `/Users/edr/code/JouleWise-wt-s1cg-92472459` was at `b859317c` when I started. Its reflog shows another session checked out `21213be7` at 19:43:04. I ran no git command that writes. One of my probes (E6) had by then run against the moved tree. I exported `b859317c` with `git archive` to `/tmp/samesig-err/s1-b859317c` and re-ran **every** S1 probe there. All results below are from that export. The files those probes import do not differ between the two commits.

I edited no repository file. `git status --short` was empty in the S2 and S1 worktrees at my last check. The bookkeeping worktree showed two untracked files of another session's S1 lens run, not mine. Scratch is under `/tmp/samesig-err/`.

## 1. Terms used in this ruling

Each term is given once, from what is physically on disk or in the code, and is used only in this sense below.

| Term | Meaning |
|---|---|
| Battery gate | The check that a laptop was on external power, not charging, with battery current at or under 200 mA, both just before and just after a measured span. Charging draws power that the energy instruments would book to the workload. |
| Battery reading | The captured output of one `ioreg` call, stored as `raw/battery_float.pre.ioreg` or `raw/battery_float.post.ioreg`. |
| Envelope | One directory written by one run of the collector. It holds `session.json` (the record), `rounds.jsonl` (the journal: one line per measurement round) and `raw/` (captured command output). |
| Collector | `scripts/sample_quiet_predicate_evidence.py::collect`. It writes one envelope. |
| Refusal path | The branch of the collector taken when it cannot establish that network time was off. It measures nothing, writes a refusal record and an empty journal, and returns. |
| Executor | `joulewise/quiet_predicate_campaign.py::execute`. It starts one collector per envelope, waits for it for at most the envelope's length plus 30 s, kills what is left, and then calls the summary. |
| Authenticator | `battery_float.authenticate_quiet_session(envelope_dir)`. It re-reads the envelope's files, recomputes the battery verdict from the raw readings, and returns a verdict whose status is `pass`, `battery_float_confounded` or `battery_float_evidence_missing`. |
| Custody failure | The authenticator, or a summary, raising `CustodyFailure` (or its subclass `CustodyUnreadable`) because recorded bytes are missing, unreadable, or do not hash to what the record says. It is an exception. It is never written into a summary as a status, and no summary is written when it is raised. |
| Summary | `summary.json`, written by `pilot_summary` (called by the executor) or by `summarize` (called on a directory of envelopes). |
| Routing | The summary's per-envelope decision: keep the envelope's numbers, exclude the envelope with a reason, or blank the whole night under a battery status. |
| No-record carve-out | Amendment 32 item (1): an envelope whose collector exited non-zero and that holds no `session.json`, no `rounds.jsonl` and no `raw/round-*` directory is excluded with reason `collect_error` without authentication, because nothing was recorded whose custody could be lost. |
| Write call | A call in Python source whose name is on the list in amendment 45 (for example `write_text`, `os.replace`, `open` with mode `w`). |
| Path name | A variable that holds a path to `session.json` or `rounds.jsonl`. Defined exactly in amendment 45. |
| Write site | A write call whose receiver or arguments reach one of the two files. Defined exactly in amendment 45. |
| Sweep | A test that parses source files without running them, lists every write site, and compares the list with an expected list. |
| Shape of a path | Which one of five things the path is: absent, a symbolic link, a directory, another non-regular entry, or a regular file. |
| Historical set | `configs/battery_float/historical_bundles.json`: 69 digests of measurement bundles recorded before the battery gate existed. |
| Bundle | One directory holding one measurement run (`metadata.json`, `power_trace.csv`, and others). |
| Entry | One row of the historical set: a digest, its kind (`complete` or `tree`), a `run_id`, and the file that cites it (its source). |
| Builder | `scripts/build_battery_float_historical_bundles.py`. It rebuilds the historical set and prints what it found and did not include. |
| Witness | The builder's `--witness` mode. It walks directories of bundles on disk, recomputes each bundle's two digests, and reports how they relate to the set. It writes nothing. |
| Mutant, counterfactual | A copy of the code with one condition changed, run against a test. A test "must fail under" a counterfactual when it would pass on the correct code and fail on the changed code. |

## 2. Rulings at a glance

| Finding | Ruling | Text change |
|---|---|---|
| SF-B1 | **UPHELD, with the pin changed.** The premise of amendment 45 needs a test. The refuter's function-level set is not that test: it stays green on a rollback added inside the collector, and three of its five members write neither file. Ruled instead: an inventory of write **sites**. | Amendment 45 gains a *Write-site inventory* paragraph, a *What the inventory does not see* paragraph, and rows R45-1 to R45-4. |
| NIT-B1 | **UPHELD.** The record of the snapshot cure names one copy, the shape-preserving one, and two mandatory counterfactual rows. I add one clause the refuter's text lacks: what a failed read does. | §A2.4's last paragraph is replaced. Its content is folded into amendment 45 (*Cure if reopened*) so that the amendment is self-contained. Rows R45-S1 and R45-S2, owed only if the cure is adopted. |
| NIT-B2 | **UPHELD, both halves.** As ruled, amendment 48 contradicts itself on a renamed intact bundle: its terms call the entry `matched`, and its kept check stops the witness. | Amendment 48 *Terms* and *Unchanged* are amended. Rows R48-7 to R48-9. |
| NIT-B3 | **UPHELD, with the wording corrected.** The fact is right: a kill before the record is written falls in the no-record carve-out. The refuter's sentence is not: the post battery reading is not "the one blocking step", and it cannot block for longer than 10 s. | Amendment 46 gains consequence (iii). No new row. |
| J-1 (judge's own) | The refuter's reconciliation of two namesake counts (177 and 169) is wrong, and amendment 48's expected result confuses printed lines with bundles. | Amendment 48 *Scope of the result*: `206 namesake lines, naming 177 distinct bundles`. |

Amendments 44 and 47 are untouched by any finding and are restated verbatim in §8.

---

## 3. SF-B1: a test for the premise of amendment 45

### 3.1 What is asked

Amendment 45 accepts that the summary's before/after comparison cannot see a file that was changed and changed back. It closes that gap with one fact: **no production code ever writes bytes that `session.json` or `rounds.jsonl` held earlier.** The refuter's point is that nothing fails when a later change makes that fact false. That is correct, and it is the same kind of defect that convened this consult: a condition that the text relies on and that no test reads.

### 3.2 Executed evidence

**E1. The refuter's sweep, rebuilt independently** (`/tmp/samesig-err/inventory.py`, over `joulewise/` and `scripts/` at `a0e8e47f`). Rule: a function whose body holds the string `"session.json"` or `"rounds.jsonl"` and any write call.

```
coarse_functions 5
  joulewise/quiet_predicate_campaign.py attest_network_time
  joulewise/quiet_predicate_campaign.py pilot_summary
  joulewise/quiet_predicate_campaign.py record_attestation
  scripts/sample_quiet_predicate_evidence.py collect
  scripts/sample_quiet_predicate_evidence.py summarize
```

Reproduced: exactly five. I read the three that the refuter says only read the two files, and confirm it: `attest_network_time` writes the timed-log file, `pilot_summary` writes `summary.json` and `summary.md`, `summarize` writes `summary.json`.

**E2. The write-site sweep** (`/tmp/samesig-err/inventory2.py`; the rule is given in full in amendment 45, §8). At `a0e8e47f`:

```
write_sites 9 distinct_rows 7
  joulewise/quiet_predicate_campaign.py::record_attestation replace session.json x1
  joulewise/quiet_predicate_campaign.py::record_attestation unlink session.json x1
  joulewise/quiet_predicate_campaign.py::record_attestation write_text session.json x1
  scripts/sample_quiet_predicate_evidence.py::collect atomic_write_text rounds.jsonl x1
  scripts/sample_quiet_predicate_evidence.py::collect open rounds.jsonl x1
  scripts/sample_quiet_predicate_evidence.py::collect write_json session.json x3
  scripts/sample_quiet_predicate_evidence.py::collect write_text rounds.jsonl x1
```

Two functions, nine sites. These are the writers in the table of the ruling under review (§A1.3), found mechanically. At the base commit `1417c0c4` the same sweep prints six rows (`collect open rounds.jsonl x2`, no `atomic_write_text`), so the list does move when the writers change: S2 replaced one journal write.

**E3. Five counterfactual trees**, each a copy of the two directories with one addition, swept by both rules:

| Tree | Addition | Refuter's function set | Write-site list |
|---|---|---|---|
| cf1 | a new function `rollback_session` that calls `(out / "session.json").write_text(body)` (the refuter's own counterfactual) | 6, **RED** | 10 sites, **RED** |
| cf2 | inside `collect`, after the final record is written: `write_json(out / "session.json", first_record)`, a rollback to the first record | 5, **green** | `write_json session.json x4`, **RED** |
| cf3 | `SESSION_NAME = "session.json"` at module level, and a new function writing `out / SESSION_NAME` | 5, **green** | 10 sites, **RED** |
| cf4 | a new function that calls `shutil.rmtree(out)` then `shutil.copytree(backup, out)`: a whole-directory restore that names neither file | 5, green | 9 sites, green |
| cf5 | a new function writing `out / f"{which}.json"`: a name computed at run time | 5, green | 9 sites, green |

cf2 is the decisive row. Reopening condition 1 of amendment 45 names "a retry that rewrites a first-write record". Such a retry would be written inside `collect`, which is already a member of the refuter's set, so the refuter's test would stay green on the very change it exists to catch.

cf4 and cf5 pass both rules. No source sweep can see a writer that does not name the file. I state that in the text as a named limit, not leave it implied.

**E4. No other place writes the two files.** A search of every tracked `.py`, `.sh` and `.mjs` file outside `tests/` and `docs/` for the two names as string constants finds four files: `joulewise/battery_float.py` (the authenticator, reads only), `joulewise/quiet_predicate_campaign.py`, `scripts/sample_quiet_predicate_evidence.py`, and `scripts/bench_replay_start_drift.py` (reads an archived record). The two modules that own envelopes contain no `shutil.rmtree`, `shutil.copytree` or `shutil.move` at `a0e8e47f`; their only `os.replace` calls are the two atomic-write helpers.

### 3.3 Ruling

**UPHELD.** The premise gets a test. The test is the write-site inventory, not the function set, for three executed reasons:

1. The function set misses a new write inside an existing member (cf2).
2. Three of its five members write neither file (E1). A pin that holds non-writers goes red when someone adds another reader that writes a report, and each such red would cost a cold gate under the refuter's text.
3. It misses a writer that reaches the file through a constant (cf3).

**The consequence of a red test is also changed.** The refuter's text sends every new member to a cold gate. Reopening condition 1 is narrower than "a new writer exists": it asks whether the writer can run while a summary runs **and** can restore earlier bytes. A new site that adds a key to a finished record, as `record_attestation` does, meets neither. So a red test forces the two questions to be answered in writing, and a cold gate is owed only when an answer is yes or cannot be shown. The exact rule is in amendment 45.

**Not ruled: a run-time test that the honest writers never repeat a state.** It would pin what the existing nine sites write. A change that makes an existing site write older bytes without adding a site is not a plausible edit, and the row would need a hook on every write, including the append. NOT EXECUTED; recorded so that it is not mistaken for an oversight.

### 3.4 Text change

Amendment 45 gains the paragraphs *Write-site inventory*, *When the inventory changes* and *What the inventory does not see*, and rows R45-1 to R45-4. The sentence "Amendment 45 adds no row" in §A2.5 of the ruling under review is withdrawn. Full text in §8.

---

## 4. NIT-B1: the record of the snapshot cure

### 4.1 What is asked

The ruling under review did not adopt the private snapshot (option (b)). It recorded it in §A2.4 as the cure to use if amendment 45 is ever reopened. The last paragraph of that record says the copy step must "apply, at the source, every file-type check" of the authenticator. The refuter shows a simpler copy that applies no check at all and is exact, and two ways a copy can turn a custody failure into `pass`.

### 4.2 Executed evidence

I re-ran the refuter's three harnesses at `a0e8e47f`, with the code imported from my own working tree. Each compares the authenticator's outcome on an envelope with its outcome on a copy of that envelope, over 57 envelopes: 36 archived real ones, 9 built by the real collector or the summary tests' fixtures, and 12 with deliberately wrong shapes (symbolic links, a directory in place of a file, missing files, a duplicate JSON key).

| Copy | Result | The differences |
|---|---|---|
| **Shape-preserving** (`/tmp/opsg/snapshot_proto.py`): each path keeps its shape; a regular file is opened with `O_NOFOLLOW` and copied by bytes | `TOTAL 57 SAME 57 DIFF 0` | none: verdict, reasons, digests, exception class and text all equal |
| **Link-following** (`/tmp/opsg/naive_proto.py`): `is_file()` then `read_bytes()` | `TOTAL 57 SAME 52 DIFF 5` | all five turn `CustodyUnreadable` into `pass`: symbolic link at `session.json`, at `rounds.jsonl`, at the pre reading, at `raw/`, at the envelope directory |
| **Refuse-on-shape** (`/tmp/opsg/s2b`): raises on any symbolic link or non-regular entry among the envelope directory, `raw/` and the four files | `TOTAL 57 SAME 50 DIFF 7` | six replace one custody raise with another; one turns `battery_float_evidence_missing` into a raise (a first-record envelope whose journal is a symbolic link, which the authenticator never opens). None is laxer. |

Copy time was 0.3 to 0.7 ms on the collector-built envelopes (about 47 KB copied).

**The absent-file case** (`/tmp/samesig-err/absent_and_kill.py`, my own probe): a refusal envelope built by the real collector, then its journal deleted.

```
E3 refusal_intact ('verdict', 'pass', ())
E3 journal_deleted direct ('raise', 'CustodyUnreadable', 'round journal missing')
E3 journal_deleted via absent_as_empty copy ('verdict', 'pass', ())
```

A copy that creates a missing journal as an empty file turns the custody failure into `pass`. Reproduced.

### 4.3 Ruling

**UPHELD**, with two changes to the refuter's replacement text.

1. **One copy is named, not two.** The refuter's text permits either the shape-preserving copy or the refuse-on-shape copy. The record should hand a later round one design. I name the shape-preserving copy: it is the only one measured identical on all 57, and it duplicates none of the authenticator's checks, so it cannot drift from them. The refuse-on-shape copy is recorded as measured never laxer and is not the named cure.
2. **A failed read is ruled.** The refuter's text does not say what the copy does when a regular file cannot be read (permission denied, I/O error). The prototype raises `RuntimeError` in one such case. Ruled: any failure other than absence raises `CustodyUnreadable`, as amendment 44 (d) already rules for the summary's own reads.

### 4.4 Text change

The last paragraph of §A2.4 of the ruling under review ("The condition that any snapshot must meet…") is replaced by the *Cure if reopened* paragraph of amendment 45 in §8. The rest of §A2.4 (what the authenticator reads; the measured cost) stands.

---

## 5. NIT-B2: how the witness names a bundle

### 5.1 What is asked

Amendment 48 says a bundle on disk *names* an entry when its directory name, or the `run_id` inside its `metadata.json`, equals the entry's `run_id`. Two things are left open. What if `metadata.json` cannot be read? And the amendment keeps an older check, made when a bundle's digest is found in the set, that compares the entry's `run_id` with the **directory name only**.

### 5.2 Executed evidence

All on the export of `b859317c`.

**E4. How the 1402 bundles under `/Users/edr/code/JouleWise/runs*` are named** (`/tmp/samesig-err/names.py`):

```
bundles 1402 {'run_id_equals_directory': 1401, 'run_id_differs_from_directory': 1}
differs …/runs_window_a5_quarantine/p2015-neg8-reference-end_attempt1_20260723T1220Z metadata_run_id p2015-neg8-reference-end
  directory_name_is_entry False metadata_run_id_is_entry False complete_in_set False tree_in_set False
digest_hits_checked 56 metadata_run_id_differs_from_entry 0
```

Reproduced: every `metadata.json` parses and has a string `run_id`; one bundle is stored under a directory name with a suffix. That bundle is not in the set by either name or either digest, so neither open point fires today.

**E4a to E4e. The witness on copies of one cited bundle** (`/tmp/samesig-err/witness_cases.py`; the bundle is `example-mac-mlx-local__r1`, a `tree` entry cited by `analysis/rpt001-v2/input_manifest.json`):

```
E4a intact copy                       witness returns; prints 'witness included tree …'
E4b renamed intact copy               digests equal to E4a; metadata run_id example-mac-mlx-local__r1
                                      witness raises ValueError: included digest run_id mismatch
E4c metadata.json unparseable         both digests still computed, both miss; witness returns, prints nothing about it
E4d run_id is the number 7            the same
E4e run_id edited to 'other'          both digests change
```

E4b is the contradiction. The copy's bytes are the cited bytes and its `metadata.json` carries the entry's `run_id`. Under amendment 48's own terms it names and matches the entry, so the entry's state is `matched`. Under the kept check the witness stops with an error.

E4e shows that both digests cover `metadata.json`. So when a digest is found in the set, the `run_id` inside the bundle is the one in the cited bytes. Accepting it as a name therefore cannot pass a bundle that the directory-name check was right to stop. The case that check exists for is an entry whose `run_id` label does not belong to its bytes. There, neither name equals the label, and the check still raises.

E4c and E4d show that the digests are computed from file bytes and do not need `metadata.json` to parse. So "the recomputed digest" is always defined, and only the naming needs a rule.

### 5.3 Ruling

**UPHELD, both halves**, in the refuter's sense. I restructure the wording so that a bundle has a set of *names* and both the naming rule and the digest-hit check use that one set.

A bundle whose directory was renamed **and** whose `metadata.json` cannot be read carries no name that ties it to an entry. If it is the only copy, the entry is `absent` and the witness exits zero. That is accepted: nothing on disk says the bundle is the cited one, and the reader refuses it in any case (it has no battery readings and its digest is not in the set).

### 5.4 Text change

Amendment 48 *Terms* and *Unchanged* are amended, and rows R48-7 to R48-9 are added. Full text in §8.

---

## 6. NIT-B3: where a kill can land on the refusal path

### 6.1 Executed evidence

**Read at `a0e8e47f`** (`scripts/sample_quiet_predicate_evidence.py:1043-1112`). The refusal path runs these steps in this order:

```
metadata commands        three subprocess calls, each with timeout 5 s          (:1055-1057, :200)
network-time receipt     one file read                                           (:1070)
pre battery reading      one ioreg call, timeout 10 s (PROBE_TIMEOUT_S), then
                         raw/battery_float.pre.ioreg is written                  (:1092)
refusal decided                                                                  (:1101)
post battery reading     one ioreg call, timeout 10 s, then
                         raw/battery_float.post.ioreg is written                 (:1108)
session.json written     temporary file, fsync, rename                           (:1109)
rounds.jsonl written     empty                                                   (:1110)
```

Lines 1109 and 1110 are consecutive statements. Every step that waits on another process comes before line 1109, and each has its own time limit. A battery reading that times out does not hang: `observe` catches the timeout and returns a record that says so (`battery_float.py:342-343`).

**E5. Death inside the post battery reading** (`/tmp/samesig-err/absent_and_kill.py`; the real collector, with the second `ioreg` call made to raise an exception that nothing catches, then the real `pilot_summary` on a twelve-envelope night):

```
E5 left_on_disk ['raw', 'raw/battery_float.pre.ioreg']
E5 pilot collector_exit 124 SPREAD_RECORDED summary True envelope5 (['collect_error', 'incomplete_interior_support'], 'collector left no record, collector_exit 124')
E5 pilot collector_exit -9  SPREAD_RECORDED summary True envelope5 (the same)
```

The carve-out applies. 124 is the code the executor records when its wait times out.

**E5b. Death between the two writes** (the same, with the journal write made to raise):

```
E5b left_on_disk ['raw', 'raw/battery_float.post.ioreg', 'raw/battery_float.pre.ioreg', 'session.json']
E5b pilot CustodyUnreadable round journal missing summary False
```

This is consequence (ii) of amendment 46, as ruled.

### 6.2 Ruling

**UPHELD, with the wording corrected.** The refuter's sentence calls the post battery reading "the one blocking step on this path". Three kinds of step wait on another process, not one, and the post reading is bounded at 10 s, so it cannot itself hold the collector until the executor's kill. What is true, and what I rule as the recorded fact, is the order: every bounded wait comes before the record is written, and nothing separates the two writes.

No new test row. The order is fixed by construction: the refusal record contains the post reading, so the reading must come before the write. A change that wrote a record first and rewrote it after the reading would add a write site, and row R45-1 goes red on that.

### 6.3 Text change

Amendment 46 gains consequence (iii). Full text in §8.

---

## 7. J-1: a correction of my own to amendment 48's expected result

The refuter counted 169 bundles that share a name with an entry and have other bytes. The ruling under review counted 177. The refuter explains the difference by the ruling also naming bundles by their `metadata.json` `run_id`. **That explanation is wrong.** E4 shows one bundle in 1402 whose two names differ, and it names no entry.

**E6** (`/tmp/samesig-err/per_entry.py`, on the export of `b859317c`):

```
entries 69 bundles 1402 metadata_unreadable 0 naming_an_entry 225
entry_state ('df-ph-decode-floor-mint1.json', 'matched') 50
entry_state ('input_manifest.json', 'matched') 6
entry_state ('fixture', 'named_only') 9
entry_state ('fixture', 'absent') 4
namesake_lines 206 distinct_namesake_bundles 177
name_an_entry_and_match_no_entry 169 match_one_entry_and_namesake_of_another 8
```

The difference is the eight `run_id`s that two entries share (one detection-floor entry and one fixture entry each). Eight bundles match the floor entry and are namesakes of the fixture entry. Counted per bundle against any entry they are hits (169 misses). Counted per entry, as amendment 48 rules, they are namesakes (177).

This also exposes an ambiguity in amendment 48's expected result, "177 bundles on namesake lines". The witness prints one namesake line per (bundle, entry) pair. A bundle that names two entries and matches neither prints two lines. The corpus gives **206 lines naming 177 distinct bundles**. Row R48-6 pins these counts, so the text must say which is which. Amendment 48 *Scope of the result* is corrected in §8.

---

## 8. Amendments 44 to 48 as they stand

These five texts replace the texts of the same numbers in `21-coldgate-fable-ruling.md`. The next S2 brief quotes 44, 45 and 46. The next S1 brief quotes 47 and 48. Amendments 44 and 47 are word for word as first ruled.

Texts cited and not restated here: amendment 32 item (1) is the no-record carve-out of §1. Amendment 32 item (2) says that authentication "runs before the summary's own `session.json`/`rounds.jsonl` read". Amendment 35 item 2 says that no decision to exclude, excuse, route or skip is taken before the authenticator has returned. Amendment 40 is the rule that enumerates the historical set (its *Inclusion* table names the three sources; its *Scan* lists digests found and not included; its *Reverse check* is the witness). Amendment 41 is the rule for the code constant `PINNED_BUNDLE_SHA256`.

### Amendment 44 (S2; replaces fix-contract item F4 as the ruled text; adds a reading to amendment 32 item (2) and to amendment 35 item 2; S2's existing scope). Unchanged.

44. **The summary routes from bytes that it has shown unchanged across authentication.** In `pilot_summary` and in `summarize`, for every envelope that is not decided by amendment 32 item (1), in this order:

    (a) Read the bytes of `session.json` and of `rounds.jsonl`. Each result is either the file's bytes or "absent". Call the two results the *before pair*. This read decides nothing.

    (b) Call `battery_float.authenticate_quiet_session(<envelope directory>)`. A `CustodyFailure`, including `CustodyUnreadable`, propagates as amendment 32 rules.

    (c) Read both files again. Call the two results the *after pair*.

    (d) If any read in (a) or (c) failed for a reason other than absence, raise `CustodyUnreadable("<envelope name>: <file name> unreadable: <reason>")`. If the after pair differs from the before pair in either file, **by bytes or by presence**, raise `CustodyFailure` or a subclass of it (the code raises `CustodyUnreadable`, which stands), with the text `<envelope name>: session.json changed during authentication` or `<envelope name>: rounds.jsonl changed during authentication`. Both raises come before any routing. No summary is written.

    (e) Every later decision about that envelope, and every summary field taken from it, is computed from the verdict and from the before pair, parsed once. Neither function opens that envelope's `session.json` or `rounds.jsonl` a third time.

    **Reading of amendment 32 item (2).** Its words "runs before the summary's own `session.json`/`rounds.jsonl` read" mean: before any read whose content the summary acts on. The read in (a) is not such a read until (d) has shown its bytes equal to a read taken after the authenticator returned. Amendment 35 item 2 is met for the same reason: no decision to exclude, excuse, route or skip is taken before the call has returned. A later edit that moves the routing read after the call and drops (c) and (d) reopens round-1 finding B2 and is forbidden by this text.

**Test rows for amendment 44.** Every row goes through the real `pilot_summary` or the real `summarize`. Each wraps the real authenticator with a function that calls it and then acts on the envelope, as the two existing session-swap rows do.

| Row | Call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R44-1 | `pilot_summary` | after the authenticator returns `pass` for envelope 5, one line is appended to that envelope's `rounds.jsonl` | `CustodyFailure` matching `rounds\.jsonl changed during authentication`; no `summary.json` | the journal comparison deleted in `pilot_summary`. Under it the summary is written. |
| R44-2 | `summarize` | the same, on the one fixture envelope | the same | the journal comparison deleted in `summarize` |
| R44-3 | `pilot_summary` | after the authenticator returns, `rounds.jsonl` is deleted | the same raise | the comparison applied only when both reads returned bytes (`if j1 is not None and j1 != j0`) |
| R44-4 | `summarize` | the same | the same | the same counterfactual in `summarize` |
| R44-5 | `pilot_summary` and `summarize` (two rows) | the envelope starts with a battery pair that does not pass; the wrapper writes a passing `session.json` **before** calling the real authenticator and leaves it | `CustodyFailure` matching `session\.json changed during authentication`; no `summary.json` | the session comparison deleted. Under it a passing summary is written. |
| R44-6 | `pilot_summary` and `summarize` (two rows) | a clean passing night; a spy counts every open of each envelope's `session.json` and `rounds.jsonl` made by the call site while the authenticator is not running | exactly two opens of each file per envelope | routing that reads `session.json` a third time after the comparison |
| R44-7 | `execute` | the existing full-executor rows with the real `record_attestation` | no raise on an honest night | none added. Name the existing rows in the report. This row shows that amendment 44 (d) does not raise when nothing writes during the summary. |

Executed by the refuter and relied on here: with both journal comparisons deleted, the two S2 test files give `295 passed`. NOT re-run by me. Rows R44-1 to R44-4 are therefore necessary.

### Amendment 45 (S2; records a residual and pins its premise; test code only, in `tests/test_quiet_predicate_campaign.py`). Amended by SF-B1 and NIT-B1.

45. **What the comparison proves, what it does not, what closes the difference, and the test that watches it.**

    *Proved by amendment 44 (d):* each file held the same bytes before the authenticator started and after it returned.

    *Not proved:* that each file held those bytes at the instant the authenticator read it.

    *What closes the difference (the premise):* no production writer of `session.json` or `rounds.jsonl` ever writes bytes that the file held at an earlier time. The writers are the collector (first record, one appended line per round, final journal and final record, and on the refusal path one record and one empty journal) and the executor's `record_attestation` (the finished record rewritten once with one key added). Each moves a file forward through its states and never back. Under that fact, equal before and after means unchanged in between.

    *Write-site inventory (the test that watches the premise).* A test parses, without running them, every `*.py` file under `joulewise/` and `scripts/`, and lists every place that can write one of the two files. It is built from four definitions.

    - *Target.* One of the two strings `session.json` and `rounds.jsonl`. An expression *holds* a target when it contains a string constant that is exactly that string. A longer string that merely contains it (an error message, for example) does not count.
    - *Path-building expression.* An expression made only of: variable names, attribute accesses, constants, f-strings, tuples, lists, the operators `/` and `+`, and calls named `Path`, `PurePath`, `with_name`, `with_suffix`, `resolve`, `absolute`, `joinpath`, `str` or `join`. An expression that calls anything else is not path-building. The forcing case: `session_bytes = snapshot(out / "session.json")` holds a target, but `snapshot` reads the file, so `session_bytes` is data and not a path.
    - *Path name.* A variable is a path name for a target when an assignment, or the variable part of a `for` clause, binds it from a path-building expression that holds the target or contains a path name for it. Assignments at module level are learned first and hold in every function of that module. Assignments inside a function hold in that function only; a nested function is its own function. Learning repeats until it finds no new path name.
    - *Write call.* A call whose name is one of `write_text`, `write_bytes`, `write_json`, `atomic_write_text`, `replace`, `rename`, `move`, `copy`, `copy2`, `copyfile`, `copytree`, `unlink`, `rmtree`, `truncate`, `touch`, `symlink_to`, `hardlink_to`, `symlink`, `link`; or a call named `open` that has a mode argument containing `w`, `a`, `x` or `+`. The name is the last part of the call (`os.replace` and `path.replace` are both `replace`). `write_json` and `atomic_write_text` are this project's own helpers, which write the path handed to them.

    A *write site* is a write call whose receiver or arguments hold a target or contain a path name for it. It is recorded as the row (file, function, call name, target), with the number of such calls. A nested function is written `outer.inner`. Calls outside any function are recorded under `<module>`. Line numbers are not recorded, so that unrelated edits do not move the list.

    Worked example, from `record_attestation`:

    ```
    path = out / "session.json"                      path-building, holds the target:   `path` is a path name
    raw = path.read_bytes()                          read_bytes is not a path call:      `raw` is data
    temporary = path.with_name(path.name + ".tmp")   path-building from a path name:     `temporary` is a path name
    temporary.write_text(...)                        write call on a path name:          site (write_text, session.json)
    os.replace(temporary, path)                      write call, arguments are path names: site (replace, session.json)
    temporary.unlink(missing_ok=True)                write call on a path name:          site (unlink, session.json)
    ```

    The test asserts that the rows are exactly these seven, nine sites in all, as they are at `a0e8e47f`:

    | File | Function | Call | Target | Count | What the site does |
    |---|---|---|---|---|---|
    | `joulewise/quiet_predicate_campaign.py` | `record_attestation` | `write_text` | `session.json` | 1 | writes the temporary file `session.json.tmp` |
    | the same | `record_attestation` | `replace` | `session.json` | 1 | renames the temporary file over `session.json` |
    | the same | `record_attestation` | `unlink` | `session.json` | 1 | removes a temporary file left by a failed rename |
    | `scripts/sample_quiet_predicate_evidence.py` | `collect` | `write_json` | `session.json` | 3 | the refusal record, the first record, the final record |
    | the same | `collect` | `write_text` | `rounds.jsonl` | 1 | the empty journal on the refusal path |
    | the same | `collect` | `open` | `rounds.jsonl` | 1 | appends one line per round |
    | the same | `collect` | `atomic_write_text` | `rounds.jsonl` | 1 | the final journal |

    *When the inventory changes.* A change that adds, removes or recounts a row turns the test red. The expected rows may be edited only in the commit that makes the change, and that commit's message answers two questions for every added or recounted row, with the evidence for each answer:
    1. Can this site run while a summary of the same envelope runs?
    2. Can this site write bytes that the file held at an earlier time?

    If both answers are no, the rows are edited and the review of that change checks the two answers. If either answer is yes, or cannot be shown, reopening condition 1 below is met and a cold gate is convened before the change is merged. A change that adds a helper which writes a path handed to it adds that helper's name to the write-call list in the same commit.

    *What the inventory does not see.* It reads source text, so it cannot see: a writer that names neither file (a copy or restore of a whole directory); a file name computed at run time; a path received as a function argument by a helper that is not on the write-call list; a writer outside `joulewise/` and `scripts/`, or not written in Python. For these the reopening conditions remain the rule, and the review of any change to envelope handling applies them by reading. At `a0e8e47f` the two modules that own envelopes contain no whole-directory copy, move or removal.

    *Residual, accepted:* a writer that writes passing bytes and restores the earlier bytes while the authenticator runs. It is outside the battery gate's threat for two reasons. No production process does it. And any writer able to do it can write a complete passing envelope with one ordinary write, which no binding of the summary to the authenticator prevents, because the envelope's digests are stored in the envelope.

    *Reopening conditions.* This amendment is revisited by a cold gate if any of these becomes true:
    1. a change adds a writer of `session.json` or `rounds.jsonl` that can run while a summary runs and that can restore earlier bytes (a rollback, a retry that rewrites a first-write record, a sync step);
    2. a change makes a summary run while collectors are expected to be writing;
    3. envelope evidence becomes signed or is otherwise made unforgeable by a writer of the directory, so that the undone write becomes the cheapest remaining way to a false pass.

    *Cure if reopened: one private snapshot.* The cure is not a further comparison. The summary copies the files that the authenticator can read into a fresh private directory, calls `authenticate_quiet_session` on the copy, and routes from the copy's bytes. `battery_float.py` is not changed. The files are at most four: `session.json`, `rounds.jsonl`, `raw/battery_float.pre.ioreg`, `raw/battery_float.post.ioreg`. The authenticator can read no other, because it refuses a stored raw path other than those two.

    The copy must never make a path more readable than it is at the source. It therefore **keeps the shape of every path** among the envelope directory, `raw/` and the four files:
    - a path that is absent at the source is absent in the copy, and is never created empty;
    - a symbolic link at the source is a symbolic link in the copy, which the authenticator then refuses; the copy never follows it;
    - a directory, or any other entry that is not a regular file, is an entry of that kind in the copy;
    - a regular file is opened with `O_NOFOLLOW`, confirmed regular by `fstat` on the open descriptor, and copied by bytes;
    - a read that fails for any reason other than absence raises `CustodyUnreadable("<envelope name>: <path> unreadable: <reason>")`.

    The copy applies none of the authenticator's checks itself. The authenticator applies them to the copy. Measured at `a0e8e47f` on 57 envelopes (36 archived, 9 built by the collector or the test fixtures, 12 with wrong shapes): 57 outcomes identical to authenticating the source, 0.3 to 0.7 ms per collector-built envelope. A copy that instead raises on every symbolic link or non-regular entry was measured never laxer (50 identical, 6 with one custody raise in place of another, 1 with a raise in place of `battery_float_evidence_missing`); it is not the named cure, because it changes one outcome and repeats checks that the authenticator owns.

**Test rows for amendment 45.** R45-1 to R45-4 are owed in S2's next round. The sweep is a function of a directory, so that R45-2 to R45-4 can run it on a temporary copy of the two directories with text appended.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R45-1 | the repository's own `joulewise/` and `scripts/` | exactly the seven rows and counts above | any of the three additions of R45-2 to R45-4 made to the real tree |
| R45-2 | a copy, with a new function appended to the collector's module that calls `(out / "session.json").write_text(body)` | the sweep returns the seven rows plus `(scripts/sample_quiet_predicate_evidence.py, <that function>, write_text, session.json) x1` | a sweep with `write_text` removed from the write-call list |
| R45-3 | a copy, with `write_json(out / "session.json", first_record)` added inside `collect` after the final record is written | the row `collect write_json session.json` has count 4 | a sweep that records functions and not sites (the refuter's rule). Executed: it reports the same five functions before and after. |
| R45-4 | a copy, with `SESSION_NAME = "session.json"` at module level and a new function that writes `out / SESSION_NAME` | the sweep returns the seven rows plus that function's row | a sweep that learns path names inside functions only |

Owed **only if the snapshot cure is adopted**, and mandatory then. Each goes through the real `pilot_summary` and the real `summarize`:

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R45-S1 | five envelopes, each a passing envelope with one path replaced by a symbolic link to its own former content: `session.json`, `rounds.jsonl`, the pre reading, `raw/`, the envelope directory | `CustodyUnreadable` for each; no `summary.json` | a copy that follows links (`is_file()` then `read_bytes()`). Executed: it gives `pass` on all five. |
| R45-S2 | a refusal envelope built by the real collector, with `rounds.jsonl` deleted | `CustodyUnreadable` matching `round journal missing`; no `summary.json` | a copy that creates an absent file empty. Executed: it gives `pass`. |

A test asserting that the undone write passes is still not added. It would pin a non-defence.

### Amendment 46 (S2; withdraws fix-contract item F7; S2's existing scope). Amended by NIT-B3.

46. **Order of the two writes on the collector's refusal path.** On the path where `collect` refuses before capture, the collector writes `session.json` first and the empty `rounds.jsonl` second, as it did before S2. Fix-contract item F7 (which reversed the order) is withdrawn.

    Three consequences are recorded:

    (i) If the `session.json` write fails, neither file exists. Amendment 32 item (1) applies and the envelope is excluded `collect_error`.

    (ii) If the collector is killed after `session.json` exists and before `rounds.jsonl` exists, the envelope holds a refusal record with no journal. The authenticator raises `round journal missing` and no summary is written. This is accepted. It is not carved out, because the same files result from deleting the journal of a complete refusal record.

    (iii) Where a kill can land. On this path, every step that waits on another process runs before the `session.json` write, and each has its own time limit: the three metadata commands (5 s each) and the pre and post battery readings (10 s each). A battery reading that times out returns a record saying so; it does not hang. The two writes are consecutive statements with nothing between them. So a collector killed while it waits, by the executor or by anything else, has not yet written a record. It leaves at most `raw/` and the battery readings, which is the no-record case of amendment 32 item (1), and the night is summarized with that envelope excluded. The window of (ii) can be entered only by a kill that lands between two consecutive file writes. This consequence adds no rule and no row: the order is fixed by the record containing the post reading, and a record written before that reading and rewritten after it would be a new write site, which row R45-1 detects.

**Test rows for amendment 46.**

| Row | Call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R46-1 | `collect` | the refusal path with the session write made to raise | the raise propagates; neither `session.json` nor `rounds.jsonl` exists | journal-first order. Exists at `a0e8e47f` as `test_refusal_session_write_failure_leaves_no_journal`. |
| R46-2 | `collect`, then `pilot_summary` | the directory R46-1 leaves, as envelope 5 of a twelve-envelope night, `collector_exit` 3 | a summary is written; envelope 5 is excluded with `collect_error` and `incomplete_interior_support`; no custody failure | journal-first order. Under it `pilot_summary` raises `CustodyUnreadable`. **Missing at `a0e8e47f`.** |
| R46-3 | `pilot_summary` | envelope 5 holds a complete refusal `session.json` and no `rounds.jsonl`, `collector_exit` 3 | `CustodyFailure` matching `round journal missing`; no `summary.json` | a carve-out widened to treat a session record with no journal as "no record". If an existing row already pins this, name it in the report and add none. Executed here as E5b. |

### Amendment 47 (S1; amends amendment 40, "Scan", second bullet; S1's existing scope: the builder and `tests/test_bundle_read.py`). Unchanged.

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

**Test rows for amendment 47.** Each row calls the production function `build(root, names)` on a temporary tree.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R47-1 | `other.md` holding `bundle_tree_sha256: ` followed by 64 `a` characters | one listed candidate: key `bundle_tree_sha256`, class `quoted`, reason `quoted in text, not a citation source`; no entry | the code at `b859317c`, which returns `([], [])` |
| R47-2 | `other.md` holding the digest first and the key after it on the same line | one listed candidate with that key | a rule that accepts only a key before the digest |
| R47-3 | `other.toml` holding the line of R47-1, with no classification row | `ValueError` matching `unclassified candidate pair` | a rule that classes every text candidate `quoted` |
| R47-4 | `broken.json` that fails to parse and holds the line of R47-1 | one listed candidate, and the file named as unparseable | today's `continue`, which skips the file |
| R47-5 | the real tree at `1417c0c4` | the forward check is byte-identical with 69 entries; the three documentation files that quote a digest under a wider key appear in the listed output | none for the first half (it pins "unchanged"); the second half is RED at `b859317c` |

Executed by the refuter and relied on here: the ruled rule, run over the base tree, finds text candidates only in `.md` (48) and `.html` (1) files, so the `unclassified candidate pair` exit cannot fire at `1417c0c4`. NOT re-run by me.

### Amendment 48 (S1; amends amendment 40, "Reverse check"; S1's existing scope: the builder and `tests/test_bundle_read.py`). Amended by NIT-B2 and J-1.

48. **The reverse check compares by name as well as by digest, and reports per entry.**

    *Terms.* An *encountered bundle* is a directory under a witness root that holds `metadata.json`. Its *names* are its directory name and, when its `metadata.json` parses as a JSON object with a string `run_id`, that `run_id`. When `metadata.json` does not parse, or holds no string `run_id`, the bundle's only name is its directory name, and the witness prints `witness metadata_unreadable <bundle path>`. That line never changes the exit status. The bundle **names** a set entry when one of its names equals the entry's `run_id`. It **matches** the entry when its recomputed digest, of the entry's kind (complete or tree), equals the entry's digest. Both digests are computed from the bundle's files as bytes, so they are computed whether or not `metadata.json` parses.

    *Per entry.* For each of the set's entries the witness prints one line, `witness_entry <state> <kind> <run_id> <digest> <source>`, where the state is:
    - `matched`: at least one encountered bundle matches it;
    - `named_only`: no encountered bundle matches it, and at least one names it;
    - `absent`: no encountered bundle matches or names it.

    *Per bundle.* For each pair of an encountered bundle and an entry that the bundle names and does not match, the witness prints `witness namesake <kind> <bundle path> <run_id> expected=<entry digest> observed=<recomputed digest>`. These lines never change the exit status. The forcing fact: at `1417c0c4`, 177 bundles under `/Users/edr/code/JouleWise/runs*` name an entry that they do not match, because run ids were used again when campaigns were collected again. Where two entries hold one `run_id` (eight ids do: one detection-floor entry and one fixture entry each), each entry is judged on its own, so one bundle may match one of them and be printed as a namesake of the other, and a bundle that matches neither is printed twice.

    *Exit status.* The witness exits non-zero if any entry whose source is `df-ph-decode-floor-mint1.json` or `analysis/rpt001-v2/input_manifest.json` is `named_only`. Such an entry's digest was computed from a bundle on disk, so this state means that the bundles carrying the cited name no longer hold the cited bytes. An entry whose source is a tracked fixture bundle is printed in whatever state it has and does not change the exit status, because the forward check hashes its committed bytes.

    *Scope of the result.* The states describe the roots that were given. The ruled invocation is over `/Users/edr/code/JouleWise/runs*`. Expected there at `1417c0c4`, over 1402 encountered bundles: 56 entries `matched` (50 floor, 6 RPT001), 9 fixture entries `named_only`, 4 fixture entries `absent`; 206 namesake lines, naming 177 distinct bundles; no `witness metadata_unreadable` line; exit status zero.

    *The checks made on a digest hit.* When an encountered bundle's digest is an entry's digest, two existing checks remain. The first is amended: the witness raises `included digest run_id mismatch` unless **one of the bundle's names** equals the entry's `run_id` (before this amendment: unless the directory name equals it). The forcing case: an intact copy of a cited bundle stored under a directory name with a suffix. Its bytes are the cited bytes and its `metadata.json` carries the entry's `run_id`, so by the terms above it names and matches the entry; the old check stopped the witness on it. One bundle in the corpus is stored that way (`runs_window_a5_quarantine/p2015-neg8-reference-end_attempt1_20260723T1220Z`, whose `run_id` is `p2015-neg8-reference-end`); it is not a set entry. Both digests cover `metadata.json`, so on a digest hit the `run_id` inside the bundle is the one in the cited bytes. The check still raises in the case it exists for, an entry whose `run_id` does not belong to its bytes, because then no name of the bundle equals it. The second check is unchanged: an included digest must have a tracked citation.

    *Unchanged.* The witness writes nothing. It is a report and never an input to the set. The refusal on a digest hit in a file that is neither an included source nor prose remains.

**Test rows for amendment 48.** Each row calls the production function `witness(...)`, or `main` with `--witness`, on temporary roots holding copies of a tracked fixture bundle. Where a row needs an entry with a citation source, the test passes `witness` a row list with that one entry, and a tracked-file list in which that digest is cited.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R48-1 | one root holding an intact copy of the entry's bundle | `witness_entry matched …`; no namesake line; exit zero | none (it pins the honest case; RED at `b859317c` only for the new line) |
| R48-2 | the same copy with one byte appended to `power_trace.csv`, alone | `witness_entry named_only …`; one namesake line carrying both digests; exit non-zero | the code at `b859317c`, which exits zero |
| R48-3 | two roots: the changed copy and an intact copy | `witness_entry matched …`; one namesake line; exit zero | a per-bundle rule that fails on any namesake. It fails 177 times on the honest corpus. |
| R48-4 | an entry whose source is a tracked fixture, with only a changed copy present | `witness_entry named_only …`; exit zero | a rule that fails on every `named_only` entry whatever its source |
| R48-5 | a bundle whose directory name differs from the entry's `run_id` and whose `metadata.json` `run_id` equals it, changed by one byte, alone | `named_only`; exit non-zero | a rule that compares directory names only |
| R48-6 | local corpus only (skipped when absent): the ruled invocation | the counts of *Scope of the result* | none; it pins the expected report |
| R48-7 | an **intact** copy of the entry's bundle under a directory named `<run_id>_attempt1`, alone | `witness_entry matched …`; no namesake line; no raise; exit zero | the code at `b859317c`, which raises `included digest run_id mismatch` (executed, E4b) |
| R48-8 | a copy under the entry's `run_id` as directory name, with `metadata.json` replaced by `{not json`, alone; and the same with `run_id` set to the number 7 (two rows) | `witness metadata_unreadable <path>`; `witness_entry named_only …`; one namesake line; exit non-zero | a rule that skips a bundle whose `metadata.json` cannot be read. Under it the entry is `absent` and the exit is zero. |
| R48-9 | an intact copy under its own name, and a row list whose one entry carries that copy's digest with `run_id` `some-other-run` | `ValueError` matching `included digest run_id mismatch` | the name check on a digest hit deleted. If an existing row already pins this, name it in the report and add none. |

---

## 9. Kept intact

- **Custody is never a status.** No ruling here adds a status or an exclusion. Amendment 45's cure paragraph and rows R45-S1 and R45-S2 exist to stop a copy from turning a custody failure into `pass`. Amendment 46 (iii) widens no carve-out: it records which existing case a kill falls in. Amendment 48 touches no reader.
- **Authentication precedes every exclusion decision.** Amendment 44 is unchanged. Amendment 32 item (1) remains the only exception.
- **`joulewise/battery_float.py` is byte-identical.** Its SHA-256 at `a0e8e47f` equals its SHA-256 at the base `1417c0c4` (`4b4d7bb2…e5e7`, executed). Nothing ruled here touches it. The inventory of amendment 45 is test code.
- **The historical set's 69 entries, bytes and pin are unchanged.**

## 10. Not executed

- The full S2 and S1 test suites. I ran probes only.
- The refuter's mutant run with both journal comparisons deleted (`295 passed`), and its run of amendment 47's rule over the base tree. I rely on its report for both and say so at the rows.
- The builder's own `--witness` over the full corpus (72 s per the refuter). I ran my per-entry probe over the same 1402 bundles with the builder's two digest functions.
- Any real envelope that carries the two battery readings. None exists before S2 lands; the 36 archived envelopes are all without them.
- The inventory as a test inside the repository's test runner. I ran it as a script on the real tree and on five modified copies.
- A run-time check that the honest writers never repeat a state (§3.3).
- Amendments 32, 35, 40 and 41 in their home rulings: not read.

## 11. Probes written in this session

| File | Purpose |
|---|---|
| `/tmp/samesig-err/inventory.py` | E1: the refuter's function-level rule, rebuilt |
| `/tmp/samesig-err/inventory2.py` | E2, E3: the write-site sweep of amendment 45 |
| `/tmp/samesig-err/cf0` to `cf5`, `base` | copies of `joulewise/` and `scripts/`: unmodified, the five counterfactuals, and the base commit |
| `/tmp/samesig-err/absent_and_kill.py` | the absent-file case (§4.2), E5, E5b |
| `/tmp/samesig-err/names.py` | E4 |
| `/tmp/samesig-err/witness_cases.py` | E4a to E4e |
| `/tmp/samesig-err/per_entry.py` | E6 |
| `/tmp/samesig-err/s1-b859317c/` | `git archive` export of the S1 commit, used for every S1 probe |

Re-run from the refuter's scratch, with code imported from my working tree: `/tmp/opsg/diff_harness.py`, `/tmp/opsg/diff_naive.py`, and `/tmp/opsg/diff_s2b.py` (the last imports the refuter's prototype tree `/tmp/opsg/s2b`).

## 12. Plain summary for Ed (5 lines)

1. **All four of the second reviewer's points are upheld, two of them with the proposed fix changed; none alters what the first ruling decided.** The first ruling kept the night summary's safeguard (read the evidence files, run the battery checker, read them again, stop if anything changed) and accepted that it cannot see a file changed and changed back, because no program of ours ever puts old bytes back.
2. **That "no program puts old bytes back" now has a test ("amendment 45", the rule that records this accepted gap).** The test reads the source code and lists every place that can write the two evidence files: nine places in two functions today. The reviewer's version listed functions, and I showed it stays silent if someone adds a rollback inside the collector, which is the exact change it is meant to catch; mine lists the write locations and catches it. It cannot see code that copies a whole folder without naming the files, and the rule says so.
3. **If that gap ever has to be closed, the recorded cure is to check a private copy of the files, and the copy must not tidy anything up.** I reproduced that a copy which follows shortcuts (symbolic links) turns five "evidence is broken" errors into a pass, and that a copy which creates a missing file as empty does the same. Both now have mandatory tests, owed only if the cure is adopted.
4. **The cross-check of old measurement folders against the list of 69 old runs gets two small repairs ("amendment 48", the rule for that cross-check).** It now says what to do with a folder whose description file is unreadable (use the folder name, print a note), and it no longer stops with an error on an intact folder that was merely renamed. I also corrected an expected count: 177 folders share a name with a listed run, printed as 206 lines.
5. **A note added to the rule on write order ("amendment 46") records where an interrupted collector lands.** Everything that can wait on another program runs before the first record is written, so a collector killed while waiting leaves no record and only that one envelope is dropped, not the night; I ran both that case and the rare in-between case. Separately: another session moved the S1 code folder to a newer commit while I worked, so I re-ran every S1 check on a clean export of the commit under review.
