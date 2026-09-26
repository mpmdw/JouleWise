# Cold gate BFGS-DESIGN-01, addendum 3 ruling (Fable 5.1, cold judge): custody of the quiet-envelope records

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-s0cg-fable-f8d6cab1` at HEAD `783a09bec56996f5cdeaa9d4c62c5d9e5246f0ed` (verified `git rev-parse HEAD`; `git status --short` empty). Session 2026-09-26. Charge sha256 verified `507446b9…13c7`. Only this file was written; scratch probes ran under `/tmp` through heredocs and left nothing behind.

## 0. Contamination disclosure

Loaded by the harness without my choosing: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers, including loop-context titles and checkpoint names). A system reminder supplied the git status and five recent commit subjects. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `CLAUDE.local.md`, no `AGENTS.md`, no decision log, and no process trace outside the two packet directories.

Read by me: the charge, Final texts v1.1 §4 (the authority), addendum 2 §5 amendments 20–28 and its §6 list, the round-3 fix contract, the delta charge, the Sol and Opus lenses, the Sol reproducer, and the code named under Executed evidence (`joulewise/battery_float.py`, the collector, `joulewise/quiet_predicate_campaign.py:1139-1260`, `joulewise/bundle_read.py` readers, `tests/test_battery_float.py` fixtures). I did not read the lead rulings 44 or the bundle-span gap-fill; nothing here depends on them.

## 1. Executed evidence (this session; every probe in the foreground)

| # | Probe | Result |
|---|---|---|
| E1 | Sol reproducer, `PYTHONPATH=. python3 10-sol-repro.py` from the tree root | `quiet: CustodyFailure -> battery_float_evidence_missing` / `bundle: CustodyFailure -> battery_float_evidence_missing` / `capture: CustodyFailure -> battery_float_evidence_missing` / `deleted rounds.jsonl: CustodyFailure -> pass`. **F1 and F2 reproduced.** |
| E2 | `RoundThreeAuthenticationTests().quiet(root)` (completed shape, the fixture default): journal absent; journal present and empty; journal empty **and** the pre raw file appended one byte with `session.json`'s `raw_stdout_sha256` rewritten to match | `pass` / `pass` / `pass`. The empty journal removes the only pre-finalization digest, so a raw rewritten together with the mutable `session.json` authenticates. **A third member of the class.** |
| E3 | Refusal shape (`quiet(root, refusal=True)`), `rounds.jsonl` deleted | `battery_float_evidence_missing ('quiet span unavailable',)` (amendment 21 as written; not `pass`). |
| E4 | `quiet(root, rounds=True)`, post raw deleted → then `session.json` deleted → then `session.json` a symlink to an intact copy outside the container → then `session.json` = `[]` | `CustodyFailure` → `evidence_missing` → `CustodyFailure` (symlink followed silently) → `evidence_missing`. |
| E5 | `BundleAuthenticationTests().bundle(root)`: baseline; `events.jsonl` with `[]` and `"x"` lines prepended; `events.jsonl` = `{`; `events.jsonl` deleted; events intact + post raw deleted; events `{` + post raw deleted; `metadata.json` deleted + post raw deleted | `pass` / **`pass`** (non-object lines silently skipped) / `evidence_missing` / `evidence_missing` / `CustodyFailure` / `CustodyFailure` / `evidence_missing`. |
| E6 | Collector `scripts/sample_quiet_predicate_evidence.py`, read | Refusal path: `write_json(session.json)` `:1081` then `(out/"rounds.jsonl").write_text("")` `:1082`. Capture path: `session["round_workers"].append(...)` `:1123` then journal `open("a")` `:1140` per completed round; `end_stamp` set in `finally` `:1163`; journal rewritten `open("w")` `:1205` (**creates the file even with zero rows**); final `session.json` write `:1208`. `round_workers` initialised `[]` in the session dict `:1064`. So on disk `end_stamp` present ⟹ `:1208` ran ⟹ `:1205` ran ⟹ the journal exists and its row count equals `len(round_workers)`. `write_json` `:142` is a plain `write_text` (not atomic). |
| E7 | `git log -S` on the collector | Both the finalization journal write and `round_workers` date from the harness's first commit `5a9dda37` (2026-09-18); every real envelope, the two pilot nights included, carries both. |
| E8 | `joulewise/quiet_predicate_campaign.py:1194-1223` | `pilot_summary` reads `session.json` and `rounds.jsonl` in one `try`; any `OSError`/`ValueError` appends `excluded + ["incomplete_interior_support"]` and `continue`s. That reason is byte-pinned in `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:24`. An unreadable envelope is therefore an **exclusion** today, before any battery authentication. |
| E9 | `joulewise/bundle_read.py:820-839, 280-330` | `_strict_json` raises `BundleReadError` for a missing, unreadable or non-JSON `metadata.json`; `events()` raises on a malformed or non-object line but treats a **missing** `events.jsonl` as `[]`. |
| E10 | `joulewise/calibration_bracketing.py:1700, 2236` | The `instrument_evidence.json` digest is compared with `observation.artifact_sha256` at both bracketing sites today, so text 10's digest-first order has a code home. |
| NOT EXECUTED | The five focused suites (301 tests, ~15 min) | Not rerun; both lenses report `OK` at `783a09be`. No live collector, controller, `ioreg` or `sudo` was run. |

## 2. Q1 (F2): the round journal

### Decision

A missing `rounds.jsonl` has three answers, one per shape, and the shape is decided from a readable `session.json` that carries a `battery_float` key:

| Shape | Definition (from `session.json`) | Missing journal | Present, empty |
|---|---|---|---|
| (i) refusal | `end_stamp` absent, `error_class == QUIET_REFUSAL_ERROR_CLASS` | **`CustodyUnreadable`** (the collector writes it at `:1082`, in the same breath as the record) | required; also `round_workers` must be `[]` |
| (ii) completed | `end_stamp` present | **`CustodyUnreadable`** (E6: `end_stamp` on disk proves `:1205` ran) | acceptable **iff** `len(round_workers) == 0`; otherwise `CustodyUnreadable` (E2 is the defect) |
| (iii) any other | neither | zero rows; verdict is `evidence_missing: quiet span unavailable` (amendment 21) and cannot be `pass` | zero rows, same verdict |

The rule that makes the table one sentence: **in shapes (i) and (ii) the journal's row count must equal `len(session["round_workers"])`**. The collector appends to both lists once per round (`:1123`, `:1140`) and rewrites the journal from the same `rows` list at finalization (`:1205`); the refusal path writes neither. A disagreement is evidence loss after the collector finished, which is custody, never a status. Shape (iii) is exempt because the capture path creates the journal only when the first round completes, so an envelope killed during round one legitimately has none; it is already `evidence_missing` at the span rung and blanks the night under text 6.

A present-but-empty journal for a completed envelope with recorded rounds is **not acceptable**: it silently removes the envelope's numbers and, as E2 shows, removes the only digest recorded before finalization, so a raw file and the mutable `session.json` rewritten together pass. With zero recorded rounds it is the collector's own legitimate output (a recorder that failed to start, a deadline already passed) and contributes no number.

### Amendment 30 (amends C1 "Missing: zero rows" and amendment 21's journal clause)

30. **Round journal presence and count.** In `authenticate_quiet_session`, once amendment 29 has admitted `session.json` as an object: if the object has no `battery_float` key, the verdict is text 2(a) `evidence_missing` and this amendment does not apply (text 6's historical population). Otherwise classify the shape as in the table above. In shapes (i) and (ii): `rounds.jsonl` must exist as a regular file (`lstat`, no symlink), else `CustodyUnreadable("round journal missing")`; `session["round_workers"]` must be a list, else `CustodyUnreadable("round count not recorded")`; and the number of rows must equal `len(round_workers)`, else `CustodyUnreadable("round journal holds <n> rows; session records <m> rounds")`. In shape (iii) a missing journal is zero rows. A present journal that cannot be read, or holds any non-empty line that is not a JSON object, is `CustodyUnreadable` in every shape (C1, unchanged). Every raise here precedes span derivation and `authenticate_pair`. Amendment 21's refusal-shape condition "and `rounds.jsonl` exists and contains no row" is superseded by the count rule (it is now implied); the refusal-shape end stays `start_stamp.monotonic_after_s`. Amendment 21's test "a refusal-shape envelope whose `rounds.jsonl` holds a row is `quiet span unavailable`" becomes "raises `CustodyUnreadable`". The per-row digest cross-check is unchanged and still runs on every row.

### Tests obliged (defect-shaped; production call site for all: `authenticate_quiet_session`, called by S2's `pilot_summary` and `summarize`, text 6)

- T30-a. The Sol F2 reproducer as a test: a row whose `raw.sha256` disagrees raises `CustodyFailure`; the same envelope with the journal **deleted** raises `CustodyUnreadable` matching `round journal missing`. RED today: `pass`.
- T30-b. Completed shape, `round_workers` of length 1, journal present and empty → `CustodyUnreadable` matching `holds 0 rows`. RED today: `pass` (E2). Variant: the pre raw appended one byte and `session.json`'s digest rewritten to match → still raises.
- T30-c. Completed shape, `round_workers == []`, journal empty, passing pair → `pass` (the legitimate zero-round completion).
- T30-d. Refusal shape, journal deleted → `CustodyUnreadable`. RED today: `quiet span unavailable` (E3).
- T30-e. Refusal shape with one row → `CustodyUnreadable` (replaces amendment 21's status expectation).
- T30-f. Shape (iii): no `end_stamp`, no `error_class`, journal absent → `evidence_missing` with reasons exactly `("quiet span unavailable",)`; the same with the post raw deleted → `CustodyFailure`.
- T30-g. Completed shape whose `session.json` lacks `battery_float`, journal absent → `evidence_missing` (historical population unchanged).
- T30-h. The fixture `RoundThreeAuthenticationTests.quiet` gains `round_workers` and writes the journal for the completed and refusal shapes, so every T15 fixture models the collector; the existing `rounds=True` flag becomes the default for the completed shape.

### Reasons

The magistrate's reading is accepted in full. `session.json` is rewritten after the fact by `record_attestation` (text 5 already forbids keying on its digest), so the journal rows are the only witness written before the envelope closed. C1's "missing means zero rows" was written for the refusal shape, which writes an empty file, and generalised by accident to the shape where absence is impossible without loss. The count rule costs one `len` and closes E2, which neither lens reported. Under D-161 an operator who rewrites `session.json`, the journal and the raw files consistently is out of scope; single-file loss or truncation is the class being closed.

## 3. Q2 (F1): the mandatory containers

### Decision

An **absent, unreadable, non-UTF-8, non-JSON, duplicate-key, symlinked or non-object** mandatory container is `CustodyUnreadable`, a refusal of the whole computation. A **readable object** whose `battery_float` key or pair fields are absent or malformed stays text 2(a) `evidence_missing`. The Opus reading ("text 2(a) already rules it") is rejected: text 2(a) enumerates faults *of a phase record inside a readable record*; it says nothing about a record that cannot be read, and C4 has already made one container malformation (a duplicate key) a custody raise, so leaving a truncated file as a status is incoherent on the candidate's own terms.

### Amendment 29 (amends text 2(a); resolves F1)

29. **Mandatory containers.** Each wrapper names its container: `session.json` (quiet), `metadata.json` (bundle), `instrument_evidence.json` (capture), and for kind bundle also `events.jsonl` (amendment 31). Before anything else the wrapper requires the container to be a regular file by `lstat` (no symlink), to read, to decode with the C4 `object_pairs_hook`, and to yield a JSON object; any failure raises `CustodyUnreadable("<file> unreadable: <reason>")` with reason one of `missing`, `not a regular file`, `symlink`, the `OSError` text, the decode error text, or `not a JSON object`. No reader in `battery_float.py` converts a read or decode failure into an empty value; the only admitted emptiness is a readable object lacking a key, which is text 2(a). The three `session = {}` / `metadata = {}` / `evidence = None` fallbacks are removed. Custody still raises before any status, and rung order (a)–(f) inside `authenticate_pair` is unchanged.

### Tests obliged (T16, a matrix; production call sites: `authenticate_quiet_session` ← S2 `pilot_summary`/`summarize` (text 6); `authenticate_bundle` ← S1 `BundleReader.metadata()` and `authenticate_window_members` (texts 8, 26); `authenticate_capture` ← S1 `_battery_exclusion_for_observation` (text 10) and the controller attachment (text 11))

- T16-a. For each kind, the Sol F1 shape: post raw deleted → `CustodyFailure`; then the container replaced by each of `{`, `[]`, `"x"`, a directory, a dangling symlink, a symlink to an intact copy outside the container, bytes `\xff\xfe`, and deletion → `CustodyUnreadable` matching `unreadable`. RED today for every cell: `evidence_missing` (E1, E4, E5).
- T16-b. For each kind, a readable object with no `battery_float` key → `evidence_missing` (unchanged); a readable object whose pre `raw_stdout_sha256` is not 64-hex → `evidence_missing: pre evidence missing: raw digest not recorded` (T2 order, unchanged).
- T16-c. Duplicate top-level key in each container → `CustodyUnreadable` (C4, unchanged, kept in the matrix so the matrix is the one place the container rules live).

### Consumers: exclusion versus refusal

- **Text 10 bracketing.** The predicate's first step is the ledger digest of `instrument_evidence.json` (E10 shows the comparison exists at both sites today), so a corrupted or missing file is `CustodyFailure` before `authenticate_capture` runs. With amendment 29 the wrapper raises as well, so the `continue` at text 10 can only ever be reached by a verdict computed from a readable object, that is by a genuine per-endpoint property (`confounded`, or the ruled historical/missing-key `evidence_missing`). S1's brief states that a **missing** evidence file is a digest disagreement (`CustodyFailure`), not a skipped comparison.
- **Text 6 quiet summary.** This is the consumer where the magistrate's concern is real today: E8 shows an unreadable `session.json` or an unreadable or **missing** `rounds.jsonl` is an `incomplete_interior_support` exclusion, before authentication, so deleting a confounded envelope's journal turns a blanked night into a night computed from the remaining envelopes. Amendment 32 closes it.
- **Texts 8, 12, 26.** `BundleReader.metadata()` already raises on an unreadable `metadata.json` (E9) and `authenticate_window_members` refuses the whole set on any non-pass, so bundles never excluded; amendment 29 aligns the wrapper with the reader.
- **Text 11.** Non-pass refuses the attachment; unchanged.

### Amendment 32 (amends text 6, sentence "Unreadable envelopes are excluded as today and yield no number"; binds S2, within its WRITE_SCOPE)

32. **Quiet-summary readability.** In `pilot_summary` and `summarize`, for every envelope directory the executor lists, `authenticate_quiet_session(out)` runs **before** the summary's own `session.json`/`rounds.jsonl` read and before the `incomplete_interior_support` `continue` (`quiet_predicate_campaign.py:1222`); a `CustodyFailure` (including `CustodyUnreadable`) propagates and no summary is written. `incomplete_interior_support` is therefore never applied to an envelope the wrapper refused; it remains available for a readable envelope whose interior support is short, and the registration digest `69321c69…` does not change (no reason added or removed). Text 6's remaining rules (authenticate before `all_rows.extend`, blank on non-pass, `CustodyFailure` propagates) are unchanged. T6 gains: (a) a night with one envelope whose `session.json` is `{` raises and writes no summary (RED today: excluded, summary written); (b) a night with one completed envelope whose `rounds.jsonl` is deleted raises (RED today: excluded); (c) the historical pilot fixture still re-summarizes as `evidence_missing`. If a real pilot-night envelope proves unreadable under (a) or (b), the raise is the correct record: its numbers were already excluded, and T6's "re-summarize as `evidence_missing`" row is read as "never a number".

## 4. Q3: the same-signature sweep

**Same signature: yes**, at the wrapper, with four members, two of which neither lens reported:

| Input | Absence or corruption | Today | Ruled |
|---|---|---|---|
| `session.json`, `metadata.json`, `instrument_evidence.json` | missing, truncated, non-object, symlink | `evidence_missing` (E1, E4) | `CustodyUnreadable` (amendment 29) |
| `rounds.jsonl` | missing on a completed or refusal envelope | `pass` / `quiet span unavailable` (E1, E3) | `CustodyUnreadable` (amendment 30) |
| `rounds.jsonl` | emptied on a completed envelope with rounds | `pass`, even with raw and session rewritten together (E2) | `CustodyUnreadable` (amendment 30) |
| `events.jsonl` | non-object lines | **silently skipped**, `pass` (E5) | `CustodyUnreadable` (amendment 31) |
| `events.jsonl` | missing or malformed | `bundle span unavailable` (E5) | `CustodyUnreadable` (amendment 31) |
| journal row `raw.sha256` | key absent, `raw` null or non-dict | `CustodyFailure` (code read; Opus C1 row) | unchanged, correct |
| raw ioreg files | missing, altered, symlinked | raise (C3, rung b) | unchanged, correct |
| spans, monotonic stamps | malformed, reversed, bool, float | statuses at rung (f), after custody (amendments 22, 23) | unchanged, correct: no custody is masked because rung (b) has already run |
| rung-(a) fault in the same phase as a tampered raw | e.g. `wall_time_s = "x"` | `evidence_missing` (ruled T2 order) | unchanged, noted below |

### Amendment 31 (Q3; `events.jsonl`)

31. **Bundle events.** In `authenticate_bundle`, `events.jsonl` is a mandatory container under amendment 29's file rule (missing, unreadable, symlinked → `CustodyUnreadable("events.jsonl unreadable: <reason>")`). Every non-blank line must decode with the C4 hook to a JSON object, else `CustodyUnreadable("events.jsonl line <n> unreadable: <reason>")`. Objects that decode but carry no `idle_baseline` start or `idle_drift_sentinel` completion, or a non-integer `monotonic_ns`, remain `bundle span unavailable` at rung (f). **S1 obligation (adopts Opus N-9):** `BundleReader` decides `not_reached` (texts 7, 8) only from an `events.jsonl` that `BundleReader.events()` parsed; any `BundleReadError` there propagates and is never read as "no `idle_baseline` start"; T8 gains that row. Tests (S0): E5's non-object-lines bundle raises (RED today: `pass`); `{` and a deleted file raise (RED today: `evidence_missing`); a well-formed file lacking the two stage events is `bundle span unavailable` (unchanged); the events file plus a deleted post raw still raises `CustodyFailure` from rung (b) (order unchanged, since amendment 29's raises are raises, not statuses).

### Not amended, with reasons

- **A rung-(a) fault inside a readable record beside a tampered raw** yields `evidence_missing`. This is text 2's ruled order, pinned by `test_structure_is_checked_before_raw_custody` and mirrored by frozen `validate_window`. Every consumer treats it as a refusal or a blank (texts 6, 8, 11, 12), and at text 10 the record edit moves the evidence digest, which raises first. I decline to reopen text 2's order for it.
- **`timed_out` absent** (Opus N-4), **`expected` key set** (N-5), **relative-import sweep** (N-3): not members of this class; the lead may take them in the next round without a ruling.

### The class, named once

Every member is the same idiom: `except (OSError, ValueError): x = <empty>` or `if path.exists(): … else: zero`. Amendment 29's sentence "no reader converts a read or decode failure into an empty value" is the rule; T16's matrix is its guard. A round-5 recurrence of this signature is a rule-11 trigger again and returns here.

## 5. Q4: S-1 and S-2 (confirmation)

- **S-1 confirmed.** Text 3 pins `sha256(inspect.getsource(fn))`, and `inspect.getsource` includes decorators, so hashing from the first decorator line is closer to the ruled text than the current `ast.get_source_segment` body, not further from it. A single binding per name and regeneration from the base file `5d5a0b75` only (the bench rule) conflict with nothing. The two pins that move (`AuthenticatedSlot`, `AuthenticatedVerdict`) move because the segment widens, not because bytes changed; the PR body says so.
- **S-2 confirmed.** Widening C8(ii) to `copy.replace`, `from copy import replace` and any `<expr>.__replace__(...)` extends text 4's guard; it removes nothing and adds no allowlist row (the Opus grep found none needed). `authenticate_bundle`'s own `dataclasses.replace` is inside `battery_float.py` and stays exempt.

## 6. Disposition

- **F1 (Sol): upheld as BLOCKER.** Closed by amendment 29 and T16.
- **F2 (Sol): upheld as BLOCKER.** Closed by amendment 30 and T30-a…h. Sol's proposed fix (bind presence to capture-shaped sessions) is adopted and sharpened to the row-count witness.
- **Opus "same signature: no": rejected.** Its matrix recorded the downgrade to a status and read text 2(a) as ruling it; text 2(a) does not reach an unreadable container, and E2 and E5 show two further members reaching `pass`.
- **Two new members (E2 empty journal, E5 non-object events): BLOCKER**, same class, closed by amendments 30 and 31.
- **Consumer-level member (E8 exclusion of unreadable envelopes): BLOCKER for S2**, closed by amendment 32; S0 is not the site.
- **Order for the lead.** One fix round implementing amendments 29–32 (S0 clauses) plus S-1 and S-2, within S0's existing WRITE_SCOPE (no path added; amendment 32's code lands in S2, amendment 31's reader clause in S1). Its lens pair carries the E1–E5 probes as a checklist and states the same-signature answer against the table in §4. Rule 11 is satisfied by this ruling; a further recurrence after that round returns to a cold gate, not to a round 5.

## 7. Plain summary for Ed (6 lines)

1. Both blockers are real and I reproduced them: corrupting the file that holds a battery record, or deleting the per-round journal, turns "the evidence has been tampered with" into "the evidence is missing" or even "pass".
2. I found two more of the same kind that neither reviewer caught: emptying the journal of a finished envelope lets a rewritten raw file pass, and junk lines in a bundle's event log are skipped in silence.
3. The rule is now one sentence: a file that should be there and cannot be read is a custody failure, full stop; only a file that reads cleanly and simply lacks the battery record is "evidence missing".
4. For the quiet-night journal, the collector itself tells us how many rounds it ran, so the journal must have exactly that many rows; a refused envelope has zero and an empty file, a finished one has one per round.
5. The night summary must run the battery check before it decides an envelope is "unreadable", otherwise deleting one bad envelope's journal quietly rescues the night.
6. The two guard improvements the magistrate proposed (decorator-inclusive pins, catching `copy.replace`) are fine and conflict with nothing.
