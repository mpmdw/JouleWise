# Cold gate QPE-SHAPE3-NIGHT-BLANK-01 ruling (Fable 5.1, cold judge): one unfinished collector and the night's numbers

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-qpe3cg-e6f06c96` at HEAD `a30385e8a2de978f274024efcbf3368217ad92e9` (`git rev-parse HEAD`; `git status --short` empty; `git diff --stat 1417c0c4 HEAD -- joulewise scripts configs` empty, so the code is main `1417c0c4`). Session 2026-09-26, 15:53–16:07 PDT (inside the 40-minute budget). Charge sha256 `0a0294b1…79ca`, identical in my tree and in the target worktree. Only this file was written to a repository; scratch probes live under `/tmp/qpe3cg/`. No `sudo`, no `launchctl`, no `powermetrics`, no live `ioreg`.

## 0. Contamination disclosure

Loaded by the harness without my choosing: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers with loop-context titles). A system reminder supplied the git status and five recent commit subjects. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `CLAUDE.local.md`, no `AGENTS.md`, no decision log, and no skill file.

Seen but not opened: a `git status` of the target worktree printed the file names `10-qpe-shape3/12-sol-execution-seat.md` (another seat's report on this same charge) and `20-bfgs-s1/11-seat-report-round1.manifest.jsonl`. I read neither. Nothing below rests on another seat's view.

Read by me: the charge; the addendum ruling in full (Final texts v1.1, of which text 6 is the text under review); the erratum ruling in full; the contract refuter's M1 (`11-opus-contract-refuter.md:107-122`) and its heading list. Code: `joulewise/quiet_predicate_campaign.py` (`cleanup_groups` `:261-312`, `record_attestation` head, `envelope_span_s`, `hard_exclusions`, `pilot_summary` `:1139-1420`, the executor loop `:1490-1700`), `scripts/sample_quiet_predicate_evidence.py` (`collect` `:1028-1209`, `summarize` `:1462-1564`, `main` `:1657-1696`), `joulewise/battery_float.py` (`authenticate_pair` `:858-952`, `authenticate_quiet_session` `:955-1023`, the constants at `:36-48`), `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`, and the fixture helpers in `tests/test_quiet_predicate_campaign.py` and `tests/test_battery_float.py`.

## 1. The words this ruling uses

Every term below is used later with exactly this meaning.

- **Envelope.** One 600 s capture. A night runs 12 of them, one every 620 s, after a 600 s settle (registered values, read from the protocol file). Inside each envelope the **interior** is the 480 s from second 60 to second 540; the energy integrated over the interior is the envelope's published number (`joules`).
- **Collector.** The process that records one envelope (`sample_quiet_predicate_evidence.py collect`). It writes `session.json` twice: a **first write** before any measurement (`:1084`), and a **final write** after all reduction (`:1208`). Only the final write carries the key `end_stamp` (the clock reading at the end of the capture).
- **Executor.** The parent process that launches each collector, waits for it, tears its process group down, and records one **entry** per envelope. The entry's `collector_exit` is the collector's exit code as the executor saw it, or 124 if the executor's wait ran out.
- **Battery read.** One run of `ioreg` on the battery. The **pre read** is taken at the start of the envelope and stored in the first write; the **post read** is taken at the end and stored only in the final write. A read is **at float** when the battery reports `IsCharging = No`, a current of at most 200 mA in magnitude, and a reading no older than 180 s (`battery_float.py:36-37`, `:269`, `:285`).
- **Verdict.** What the merged helper `authenticate_quiet_session` returns for one envelope. `pass`: both reads are present, authentic and at float. `battery_float_confounded`: at least one read was taken and shows the battery was not at float. `battery_float_evidence_missing`: no read shows a problem, but at least one read is absent or unusable.
- **Custody failure.** A recorded file no longer matches what was recorded about it (a raw `ioreg` file whose bytes do not hash to the digest stored beside the read, or a `session.json` that exists and does not parse). It is an exception, not a verdict: it propagates and no summary is written.
- **Blank the night.** Text 6's rule: the night's summary is written with its status set to the battery verdict, and every energy-derived field (the retained count, pairs, sizing, spreads, and each envelope's `joules`, `combined_joules`, `interior`) set to null.
- **Shapes (i), (ii), (iii).** The erratum's three classes of `session.json`. (i) refusal: no `end_stamp`, and `error_class` is `network_time_provenance`. (ii) completed: `end_stamp` present. (iii) anything else. In this ruling a shape-(iii) envelope is called an **unfinished envelope**: its collector made the first write and never made the final one.

## 2. Executed evidence (this session; every probe in the foreground)

Probes ran from the tree root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.`; scripts are `/tmp/qpe3cg/probe_{a,b,b_child,c,d,e}.py`.

| # | Probe | Observed |
|---|---|---|
| P-A | **Today's `pilot_summary`** on a 12-envelope night (fixture helpers of `tests/test_quiet_predicate_campaign.py`), envelope 5 replaced by a first-write `session.json` (no `end_stamp`, no `interior`, no `whole_envelope_observer_cpu_s`, `power: null`) with `collector_exit: 124`. Three journal variants. | Journal holding **one provisional row**: **`ValueError: envelope 5: whole_envelope_observer_cpu_s or envelope span missing; absent evidence is never a pass`**, `summary.json` **not written**. Journal **absent**: summary written, `retained 11`, `retained_pairs 5`, envelope 5 `excluded ['collect_error', 'incomplete_interior_support']`, `joules None`. Journal **truncated mid-line**: same as absent. Control night (12 completed): `retained 12`, pairs 6. |
| P-B | **The real `collect`** in a child process behind the same SIGTERM handler `main()` installs (`:1675-1677`), injected round runner that stalls in round 2, injected recorder whose `finish()` takes 0.4 s. The parent waits, books 124 on `TimeoutExpired`, then tears down three ways. | **One SIGTERM:** `end_stamp` present, `error 'KeyboardInterrupt: collector termination requested'`, process exit 1, two journal rows: shape (ii). **SIGTERM on every 50 ms sweep, as `cleanup_groups` does (`:267-304`):** `end_stamp` **absent**, `error` null, `whole_envelope_observer_cpu_s` absent, process exit −2, two provisional rows: **shape (iii)**. **SIGKILL:** `end_stamp` absent, exit −9, one provisional row: shape (iii). |
| P-C | **The merged helper** on the bytes a killed S2-era collector leaves (a first-write session whose `battery_float` holds the pre read only), 11 cases, each run through a reference copy of text 6 as it stands and of amendment 35 below. Fixture reads: `tests/fixtures/battery_float/float.ioreg`, `charging-synthetic-from-real.ioreg`. | K1–K3 (pre at float; journal provisional / truncated / absent; exit 124 / −9 / −2): verdict `battery_float_evidence_missing`, reasons exactly `('post evidence missing: phase not recorded',)`. K4 (pre **charging**): `battery_float_confounded`, reasons `('pre IsCharging is not No', 'pre InstantAmperage exceeds 200 mA', 'post evidence missing: phase not recorded')`. K5 (pre raw file deleted): **raises `CustodyFailure`**. K6 (pre probe exit 2): `evidence_missing`. K7, K8 (K1's bytes with `collector_exit` 0, or the key absent): `evidence_missing`. K9 (completed, both reads at float, exit 124): `pass`. K10 (completed, post charging, exit 1): `confounded`. K11 (completed, post absent, exit 0): `evidence_missing`. |
| P-D | Custody and carve-out edges through the same reference. | `session.json` = `{` with exit 124: `CustodyUnreadable`. `session.json` deleted beside a provisional journal, exit 124: `CustodyUnreadable … missing`. Only `raw/battery_float.pre.ioreg` on disk, exit 1: excluded without authentication (amendment 32 step 1). Same, exit 0: `CustodyUnreadable`. Pre digest rewritten to disagree with the raw bytes: `CustodyFailure`. Pre charging **and** raw deleted: `CustodyFailure` (custody before status). Pre stale by more than 180 s: `evidence_missing`. Refusal shape (i) holding a pre read only, exit 3: `evidence_missing`. |
| P-E | **Registered minimums on the existing exclusion path.** Today's `pilot_summary` on 12-envelope nights whose unfinished envelopes have no journal (the path amendment 35 item 4 routes every excused envelope through), exit code 1. | Envelope 5: `retained 11`, pairs 5, `observer_support_s 6600.0` (11 × 600 s: the floor leaves the envelope out). Envelopes 5 and 6: retained 10, pairs 5. Envelopes 5 and 7: retained 10, pairs 4, spread bound still computed. Envelopes 1, 3, 5, 7, 9: retained 7, pairs 1, status `INCONCLUSIVE`, spread bound `None`. |
| S1 | Source, executor `:1566-1568`, `:1573-1574`, `:1552-1558` | The wait is `envelope_s + 30` = 630 s and books 124. The next envelope is scheduled 620 s after this one's scheduled start, and a start more than `start_drift_abort_s` = 2 s late ends the night as refused. |
| S2 | Source, collector `:1084`, `:1087`, `:1148-1165`, `:1166-1208`; `main` `:1683-1696` | First write precedes the `try`. `end_stamp` is set in memory at `:1163` inside `finally`; the `finally`'s own handler catches `Exception` only (`:1154`), so a `KeyboardInterrupt` arriving there escapes. `:1166-1207` (interior reduction, per-row integration, hashing, `json.dumps(..., allow_nan=False)`) sits between `finally` and the final write with no handler. `main` returns 0 only after `collect` returned, and `collect` returns only after `:1208`. |
| S3 | Registration | `sha256(pilot_protocol_v3.json)` = `69321c69…3616`, equal to `night_gate.QPE01_PILOT_REGISTRATION_SHA256`. Its `exclusions` list holds both `collect_error` and `incomplete_interior_support`. Its observer-floor statistic is defined "over all readable envelopes". |
| S4 | `grep` for callers of the harness `summarize` under `joulewise/`, `scripts/`, `scripts/night_chains/` | Only `main()`'s `summarize` subcommand (`:1692`). No chain, executor or harvest step calls it. |
| NOT EXECUTED | | The real executor loop (needs the night's privileged steps); the 630 s against 620 s consequence in §3 F5 is arithmetic on S1, not a run. S2's implementation (not written): the amendment-35 column of P-C is a reference function in `/tmp`, not repository code. The battery's own update cadence (how often `UpdateTime` advances) was not measured. No focused test suite was rerun. |

## 3. The magistrate's bench facts, checked

- **F1 CONFIRMED** (S1; the `except` is at `:1567-1568`). Addition the charge does not carry: the collector converts SIGTERM into `KeyboardInterrupt`, so a single SIGTERM lets it finish and write shape (ii). The executor's teardown signals the group again on every 50 ms sweep, and the second signal lands inside the collector's finalization, which does not survive it (P-B). The production teardown therefore does leave the unfinished shape, as F1 says, for that reason.
- **F2 FALSE for the common case** (P-A). Today one unfinished envelope costs only its own admission **only if the collector died before its first round was journaled**. Once one provisional row exists (30 s into a 600 s envelope), today's `pilot_summary` raises at the observer-floor step (`:1325-1327`) and writes no summary; the executor then books the night refused (`:1685-1686`). The "night proceeds" baseline that the charge weighs text 6 against exists today only for kills in the first 30 s.
- **F3 CONFIRMED** (S2, P-B). Addition: a collector can also leave this shape with **no kill at all**, by raising anywhere in `:1166-1207`; `main` then exits 1 or 2.
- **F4 CONFIRMED as to status, NOT as to reason** (P-C K1). The status is `battery_float_evidence_missing`. The reason is `post evidence missing: phase not recorded`, not `quiet span unavailable`: the helper adds the span reason only when both reads produced stamps (`battery_float.py:934-941`), and a killed collector has no post read. Tests must key on the status, never on the span string.
- **F5 (new, from S1; arithmetic, NOT EXECUTED).** A collector that reaches the 630 s timeout on any envelope except the twelfth has already made the next envelope at least 630 − 620 = 10 s late, five times the 2 s abort bar, so the registered start-drift abort ends the night as refused whatever the battery rule says. The timeout is therefore not where amendment 35 saves nights. It saves them where a collector **exits non-zero on time** (a raise in the final reduction, a signal from outside the chain) and on **envelope 12**.

## 4. Rulings

### Q1. Unfinished envelope with a non-zero `collector_exit`: AMEND

An unfinished envelope whose executor entry records a non-zero exit, and whose verdict is `battery_float_evidence_missing`, is excluded from the night and the night proceeds. Its verdict stays on the record in `battery_float_envelopes`.

**The forcing problem.** Text 6 blanks on any verdict other than `pass`. A killed collector can never reach `pass`, because the post read lives only in the final write it never made (P-C K1–K3). So under text 6 the battery rule, which exists to catch a battery that was charging, voids a night on which no read showed charging and every published number has its own pair of passing reads.

**Worked example.** A night is 600 s of settle plus 12 × 620 s = 8040 s, 2 h 14 min. The registration forbids topping up from another night. Collector 5 raises during its final reduction and exits 1. Under text 6: 0 of 12 envelopes yield a number. Under amendment 35: envelope 5 yields none, its registered pair partner 6 loses its pair (pairs are the fixed couples (1,2), (3,4), …, never re-paired), and the night keeps 11 retained envelopes and 5 pairs against registered minimums of 8 and 4 (P-A, absent-journal variant, shows exactly 11 and 5 on the existing exclusion path).

**Could a published number be wrong?** Each candidate route was checked:

1. *The unfinished envelope's own energy.* It has none: `interior` is computed at `:1176`, after the point where the collector died, and amendment 35 sets the three energy fields to null regardless.
2. *Another envelope's energy.* Each retained envelope is bracketed by its own pre and post read and must pass on them. The missing post read of envelope 5 would have been taken about 20 s before envelope 6's pre read; envelope 6's own pre read is the later and nearer observation of the same battery, so nothing about envelope 6 is known less well. Toward envelope 4, envelope 5's pre read is present and was evaluated.
3. *The observer floor* (the apparatus's CPU cost in cores, a stop-rule input). The unfinished envelope recorded neither its CPU total nor its end stamp, so the registered per-envelope statistic is undefined for it, and the registration defines the campaign value "over all readable envelopes" (S3). Omitting it is the registered computation. Today's code already omits the same physical event when the journal is absent.

**Why not KEEP.** Text 6's own justification for blanking rather than excluding is that the registration has no battery exclusion reason. That argument does not reach this envelope: it is already excluded, under a registered reason, by a witness independent of the battery (the executor's exit code). The erratum's class rule ("honest collector failure … never costs more than its own envelope's admission") then applies without strain, and the asymmetry the erratum flagged (a collector that died before its first write is excluded; one that died a second later voids the night) disappears.

**Limitation to carry into the record.** `collect_error` is keyed on an exit code, so a collector that crashes *because of what it measured* (for example a non-finite value refused by `allow_nan=False`) removes an envelope by its content. That is a property of the registered exclusion, not of the battery gate, and amendment 35 neither creates nor cures it. It is why the amendment requires the exit code on the summary row and a sentence in `summary.md`: every such envelope is named, none disappears.

### Q2. A pre read that shows charging still blanks the night; only absent evidence is excused

**Ruling.** The excuse covers the verdict `battery_float_evidence_missing` and nothing else. `battery_float_confounded` on an unfinished envelope blanks the night exactly as text 6 says (P-C K4).

**The science.** A missing post read is an observation that was never made. A pre read that shows charging is an observation that was made, and the collector's later death does not make the battery's state at that instant less true. The night's numbers are pooled, and that read sits between two envelopes that do publish:

```
night clock (s)   0    60            540  600 620  680                        1240 1300          1780 1840
                  |     |             |    |   |    |                           |    |             |    |
envelope 4        pre4  [== interior 4 ==] post4
envelope 5                                     pre5 [== interior 5 ==  X
envelope 6                                                                      pre6 [== interior 6 ==] post6
```

Every element, named: `pre4`, `post4`, `pre5`, `pre6`, `post6` are battery reads (there is no `post5`); each `[== interior N ==]` is the 480 s span whose energy is envelope N's published number; `X` is the instant collector 5 died; the numbers on the top line are seconds since envelope 4's scheduled start (envelope 5 starts at 620, envelope 6 at 1240).

The gate accepts a battery reading up to 180 s old. `post4`, taken near second 600, may therefore rest on a reading from second 420 onward, which is inside interior 4 (60 to 540). If charging began at second 500, `post4` can pass on a reading from second 430 and the first read to show the charging is `pre5` at second 620. In that case the only evidence that interior 4 was contaminated is the pre read of the envelope that was later killed. Excusing it would publish envelope 4's number over positive evidence against it. How often the battery refreshes its reading was not measured here (NOT EXECUTED); the 180 s bound is the gate's own and is enough for the ruling.

A pre read that failed or is stale is absence, not evidence, and is excused with the rest (P-C K6, P-D stale case).

### Q3. Custody: CONFIRMED, and fixed by order

`authenticate_quiet_session` runs on every envelope that has any recorded output **before** the summary looks at the exit code or the shape for the purpose of excusing. Executed: an unfinished envelope with exit 124 whose pre raw file is deleted raises `CustodyFailure` (K5); with the pre read charging and the raw deleted, still `CustodyFailure` (custody precedes status); with the digest rewritten, `CustodyFailure`; with `session.json` unparseable or deleted beside a journal, `CustodyUnreadable` (P-D). The excuse is decided from the returned verdict, so an implementation that follows the order cannot swallow a raise. The one path that skips authentication is amendment 32's step (1), unchanged: nothing recorded, so nothing whose custody could be lost.

### Q4. Unfinished envelope with `collector_exit == 0`: cannot occur honestly; text 6 applies

Exit 0 is returned only after `collect` returned, and `collect` returns only after the final write (S2), which carries `end_stamp`; with amendment 34's atomic writes the file on disk is then the final one. The executor's later annotation rewrites the same object and keeps the key. In P-B no teardown produced exit 0 (1, −2, −9). So this combination means the record and the executor disagree. It is not excused: the verdict is `evidence_missing` and the night is blanked under text 6 (K7), with the exit code shown on the row. The same holds when `collector_exit` is absent from the entry (K8; today's code reads an absent key as 0, `:1150`) or is not an integer. I do not add a new raise: the helper has no digest that proves a loss here, and blanking already lets no number out.

### Q5. `summarize`: KEEP text 6

`summarize` has no executor entry, so it has no witness that the collector failed, and it has no exclusion list to book an exclusion under. An unfinished session is a non-pass and `summarize` raises, naming the session directory. The cost is not a night: `summarize` is an offline tool that reads a directory someone chose, nothing calls it from the chain (S4), rerunning it destroys nothing, and the night's numbers come from `pilot_summary`. If a claim-bearing use of `summarize` ever needs to continue past an unfinished session, that is a separate ruled change.

### Q6. Tests: see §6.

## 5. Amendment 35 (final text; S2's brief quotes this verbatim)

35. **An unfinished collector costs its own envelope, not the night (amends text 6 and amendment 32; S2; `pilot_summary` only).**

    *Definitions.* An envelope is **unfinished** when its `session.json`, as admitted by `authenticate_quiet_session`, has no `end_stamp` key and its `error_class` is not `battery_float.QUIET_REFUSAL_ERROR_CLASS`. An entry carries the **executor witness** when its `collector_exit` is an `int` that is not a `bool` and is not 0.

    *Rule.* In `pilot_summary` (`quiet_predicate_campaign.py:1139`), for every entry the executor lists, in this order:

    1. Amendment 32 step (1) is unchanged: executor witness, and no `session.json`, no `rounds.jsonl` (both by `lstat`) and no `raw/round-*` directory → excluded `collect_error`, no authentication.
    2. Otherwise `authenticate_quiet_session(out)` runs first. A `CustodyFailure` (including `CustodyUnreadable`) propagates and no summary is written. Nothing in this amendment catches, converts or postpones it, and no test of the exit code or of the shape may precede this call.
    3. Verdict `pass`: the envelope is summarized as today.
    4. **Excused**, only when all three hold: the envelope is unfinished; the entry carries the executor witness; the verdict's status is `battery_float_evidence_missing`. Then:
       - the envelope does not set the night's status and blanks nothing;
       - it is appended to `values` through the existing unreadable-envelope path (`:1221-1224`): `excluded` is the reasons already booked from the entry (`collect_error` from `:1150`, and `cleanup_unproven` or the non-observer reason where they apply) plus `incomplete_interior_support`; `error` is `collector did not finish: no end_stamp, collector_exit <code>`; `joules`, `combined_joules` and `interior` are `None`;
       - its `rounds.jsonl` is not read by the summary: no row of it enters `all_rows`, `hard_exclusions`, the row/session identity check, `clean_busy` or the observer floor, and because `error` is set the floor's `readable` filter (`:1321`) leaves the envelope out, which is the registered statistic ("over all readable envelopes");
       - the summary's own read of `session.json` and the replay-recorder check (`:1216-1220`) run as today.
    5. Every other non-pass follows text 6 unchanged and blanks the night. This includes: `battery_float_confounded` on an unfinished envelope (a pre read that shows charging); an unfinished envelope whose `collector_exit` is 0, absent or not an integer; and any non-pass on a completed or refusal-shape envelope whatever its exit code.

    *Record.* The report always carries `battery_float_envelopes`, one row per envelope whose verdict is not `pass`, holding `index`, `status`, `reasons`, the raw digests, `collector_exit`, and `disposition`, which is `excluded_collect_error` for an excused envelope and `blanks_night` otherwise. When at least one envelope is excused, `summary.md` says so in one sentence giving each index and exit code. No exclusion reason is added or removed; the registration digest `69321c69…` does not change.

    *`summarize`.* Unchanged from text 6 and amendment 32: it has no executor entry, so nothing is excused; an unfinished session is a non-pass and `summarize` raises, naming the session directory and the verdict's status and reasons.

    *Supersession.* Amendment 32's test (e) ("… its verdict is `evidence_missing` and the night follows text 6") is replaced by T6-f below. Amendment 30's phrase "the single reason `quiet span unavailable`" describes a fixture holding both reads; a killed collector's verdict carries `post evidence missing: phase not recorded`, and no S2 code or test may key on either string.

## 6. T6 rows for S2 (defect-shaped)

Production call site for every row except T6-m: `pilot_summary` → `authenticate_quiet_session`. Fixture night for every row: 12 envelopes, 11 completed with a passing pair and an interior energy, envelope 5 the counterfactual. "Naive" means text 6 implemented as it stands (blank on any non-pass).

| Row | Counterfactual input (envelope 5) | Expected | RED against |
|---|---|---|---|
| T6-f | First-write `session.json` with a passing pre read and no post; one provisional row (`raw.sha256 == {}`); `collector_exit: 124` | Summary written; status is not a battery status; `retained == 11`, `retained_pairs == 5`; envelope 5 `excluded ⊇ {collect_error, incomplete_interior_support}`, `joules is None`; one `battery_float_envelopes` row, `evidence_missing`, `excluded_collect_error` | Naive: night blanked. Also RED against an excuse that still reads the journal: `ValueError … whole_envelope_observer_cpu_s or envelope span missing` (P-A) |
| T6-g | T6-f with the pre raw from `charging-synthetic-from-real.ioreg` | Night blanked, status `BATTERY_FLOAT_CONFOUNDED`, disposition `blanks_night` | An excuse keyed on shape and exit code without the status test: night proceeds |
| T6-h | T6-f with `raw/battery_float.pre.ioreg` deleted; and T6-g with it deleted | `CustodyFailure` raised; no `summary.json` | An implementation that tests the exit code or shape before calling the helper: excluded, summary written |
| T6-i | T6-f's bytes with `collector_exit` 0; key absent; `True`; `"124"` | Night blanked, `BATTERY_FLOAT_EVIDENCE_MISSING`, row shows the exit code | An excuse keyed on shape alone, or on `!= 0` without the type test (`True != 0`, `"124" != 0`) |
| T6-j | Completed envelope (`end_stamp`, `journal_rows: 1`, agreeing row), post read charging, `collector_exit: 1`; variant with the post probe failed | Night blanked (`CONFOUNDED`; variant `EVIDENCE_MISSING`) | An excuse keyed on the exit code alone |
| T6-k | Refusal shape (`error_class: network_time_provenance`, empty journal) holding a pre read only, `collector_exit: 3` | Night blanked, `EVIDENCE_MISSING` | An excuse keyed on "no `end_stamp`" without the `error_class` test |
| T6-l | T6-f with the journal absent; with the journal `{"round": 1, "ra` | Same as T6-f | An implementation that parses the journal before deciding |
| T6-m | Call site `summarize` → `authenticate_quiet_session`. A directory with one completed passing session and one session with T6-f's bytes; variant with the pre raw deleted | Raises, naming the unfinished session; no summary files. Variant: `CustodyFailure` | The excuse ported into `summarize`: summary returned |
| T6-n | Envelope 5's bytes produced by the **real** `collect` in a child process (injected round runner that stalls, injected battery runner), torn down with SIGTERM on every 50 ms sweep as `cleanup_groups` does; the exit code the parent records goes into the entry | As T6-f; additionally the child's `session.json` has no `end_stamp` and its exit code is not 0 | Hand-written fixture bytes that drift from the collector's real output (P-B is the model) |
| T6-o | Three nights: envelopes 5 and 6 as T6-f (one registered pair); 5 and 7 (two pairs); 1, 3, 5, 7, 9 | 5 and 6: `retained == 10`, `retained_pairs == 5`. 5 and 7: `retained == 10`, `retained_pairs == 4`, spread still computed. Five excused: `retained == 7`, `retained_pairs == 1`, status `INCONCLUSIVE` by the registered minimums, not a battery status (counts executed in P-E) | An excuse that bypasses the registered minimums, or that re-pairs a survivor with a neighbour |

## 7. Disposition and flags

- **Q1 AMEND** (amendment 35). **Q2** confounded still blanks; only `evidence_missing` is excused. **Q3** custody confirmed and fixed by order. **Q4** cannot occur honestly; text 6 applies. **Q5** KEEP for `summarize`. **Q6** rows T6-f to T6-o.
- **Flag 1 (bench fact F2 is wrong).** The magistrate's baseline should be corrected wherever it is recorded: today an unfinished envelope with one journaled round raises in `pilot_summary` and the night is booked refused (P-A). Amendment 35 item 4 removes that raise for excused envelopes by routing them through the path the floor already skips; S2 must not "fix" it by supplying a span or CPU total the collector never recorded.
- **Flag 2 (F5, cost weighting).** For envelopes 1 to 11 a timeout already ends the night through the registered start-drift abort. If the magistrate wants a stalled sampler to cost one envelope rather than the night, the change is in the executor's wait and teardown timing, not in the battery rule. Not ruled here.
- **Flag 3 (not ruled, outside the charge).** A completed envelope whose post probe failed blanks the night under text 6 even though nothing showed charging. There is no registered exclusion to book it under, so the cure is the separate registration item text 6 already names.
- **Flag 4 (test fixtures).** Rows read back from `evidence_envelopes.jsonl` can include the executor's abort row, which has no `collector_exit` and no directory. The executor never passes that row to `pilot_summary` (`:1553` writes it to the file only), but a re-summarization that feeds the file's rows in would raise under amendment 32 step (2). Filter rows carrying `abort` in any such fixture.

## 8. Plain summary for Ed (5 lines)

1. A night is twelve 10-minute recordings; each one reads the battery at its start and end, and the current rule throws away the whole night's energy numbers if any recording lacks a clean pair of reads. A recording whose process died can never have its end read, so one crash voided 2 h 14 min of otherwise good data.
2. I ruled that such a recording is dropped on its own (under the already-registered "collector error" reason) and the night keeps its other eleven, because no published number depends on the dead recording and every surviving recording still has its own passing pair.
3. Two things still void the night: a start read that actually shows the battery charging (it is real evidence about the neighbouring recordings, whatever happened afterwards), and any sign that a recorded file was altered or lost, which is checked before anything can be dropped.
4. Testing turned up two facts the question did not have. Today's code already fails the whole night on a crashed recording for an unrelated reason (a missing CPU figure), and a recording that overruns its time limit ends the night anyway through a separate lateness rule, so the saving is for crashes, not for stalls.
5. The standalone offline summary tool keeps the strict rule, since it has no independent record that a crash happened; ten test cases are specified, each built to fail against a specific wrong implementation.
