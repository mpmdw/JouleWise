# BFG-S S0 fix round 4: delta re-audit, CONTRACT lens (Opus 5.5)

**Verdict: PASS. 0 BLOCKER, 0 SHOULD-FIX, 5 NIT. Same signature: no.**

Candidate `c9081c6e` (parent `783a09be`), worktree `/Users/edr/code/JouleWise-wt-s0r4-opus-f8d6cab1`, detached, `git status --short` empty before and after. I edited no repository file. Every probe ran in the foreground, from scripts under `/tmp/opus52/`.

Authorities read in full: the charge `50-delta-r4-charge.md`, the brief `40-seat-brief-round4.txt`, the addendum-3 ruling `20-coldgate/10-coldgate-fable-ruling.md`, the erratum `20-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md`, the seat report `41-seat-report-round4.md`, and S-1/S-2 as written in `11-opus-contract-lens.md`. I read the Final texts v1.1 only as they are quoted by the rulings.

## 0. Executed evidence

| # | Probe | Result |
|---|---|---|
| X1 | `git diff --stat 783a09be HEAD` (no pathspec, so the whole tree) | 3 files: `joulewise/battery_float.py`, `tests/test_battery_float.py`, `tests/test_battery_float_consumers.py`. All three are in WRITE_SCOPE, and `tests/test_battery_float_sweep.py` is untouched. Nothing outside WRITE_SCOPE moved. `git merge-base 5d5a0b75 HEAD` = `5d5a0b75`. |
| X2 | `/tmp/opus52/fence.py`: loads `git show 5d5a0b75:joulewise/battery_float.py` as a module, rebuilds the closure from `FROZEN_ROOTS` on base and head, and hashes each member under the test's own segment rule | Base closure = head closure = the pin table keys, with 39 members. For all 39, the base segment equals the head segment, the decorator-inclusive full lines are identical, and the pin equals sha256(base segment). **0 mismatches.** Only `AuthenticatedSlot` and `AuthenticatedVerdict` differ from the old undecorated `ast.get_source_segment` hash, and the round-4 table diff moves exactly those two. |
| X3 | V1: `python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep` on the candidate | `Ran 134 tests in 148.356s` / `OK`. |
| X4 | RED replay: `git archive HEAD` extracted to `/tmp/opus52/red`, with `joulewise/battery_float.py` replaced by `783a09be`'s copy; then `MandatoryContainerAndJournalTests` plus the two edited T15 tests are run | `Ran 14 tests`, `FAILED (failures=37, errors=7)`. Every "RED today" cell fails: T30-a, T30-b (both variants), T30-d, T30-e, T30-f (provisional-row and `{` sub-rows), T30-i (four witness values), T30-j, T16-a (all 8 forms for each of 3 kinds, 24 cells), and the events test (7 bodies). T30-c, T30-g, T16-b and T16-c pass on the old code, as expected, since the ruling marks them unchanged. |
| X5 | `/tmp/opus52/probe.py`: a mutation matrix over 5 files × 6 mutations (delete, empty, truncate-half, symlink to an intact external copy, duplicate key, directory). It covers quiet in 4 shapes (completed, zero-round, refusal, iii), plus bundle and capture, and runs each cell with the post raw intact and with it deleted. | Full output in §2. In every custody-bearing cell the result is a raise. No cell with the raw deleted returns a status, except where the ruling places the file outside custody (shape iii). |
| X6 | `/tmp/opus52/probe2.py`: shape moves, `journal_rows` values, `end_stamp: null`, whitespace lines, row without `raw`, non-UTF-8 journal, FIFO journal | See §2 and the findings. |
| X7 | `/tmp/opus52/pab.py`: runs the **real** `collect()` with `FakeClock`, a network-time receipt and a scripted round runner, where round 1 writes both battery raws. P-A: round 2 leaves `sampler.json` = `{"marks": {"ps_start": 1.0`. P-B: round 2 raises `SystemExit`. Then `battery_float` is added to `session.json`, and `journal_rows = len(journal)` is added only where `end_stamp` exists (simulating amendment 33). | See §3. |
| X8 | `/tmp/opus52/hist.py`: `authenticate_quiet_session` from `783a09be` compared with head on historical envelopes (no `battery_float` key), 3 shapes × 5 journal states | See §3. |
| X9 | Live S-1 mutations applied to the `/tmp/opus52/red` copy of the head file, then `S0FreezeTests.test_frozen_function_sources_match_base` | See §5. |
| X10 | S-2 forms fed to `violations("scripts/x.py", …)`, plus a search over `joulewise/**` and `scripts/**` for `copy.replace\|from copy import\|__replace__` | See §5. |
| X11 | A 200 000-deep `[` written to `session.json`, `rounds.jsonl` and `events.jsonl` | `RecursionError` escapes in all three cases, and it is not a `CustodyFailure` (NIT-2). |
| NOT EXECUTED | V2/V3 and the live `pgrep`/`sysctl` probes | These belong to the execution lens. I also did not recompute the seat's pre-change RED run on its own tree; X4 is my independent replay of that run. |

## 1. Closure table

| Item | State | Evidence |
|---|---|---|
| **Amendment 29** (mandatory containers) | **CLOSED** | `_required_file` does an `lstat` and then refuses missing, symlink and non-regular files. `_required_object` decodes with the C4 hook and requires a dict, and every failure is `CustodyUnreadable("<file> unreadable: <reason>")`. The three fallbacks `session = {}`, `metadata = {}` and `evidence = None` are gone, verified by reading the diff. The container is read before anything else in all three wrappers, and `authenticate_pair` is untouched in round 4. X5 shows every container mutation raising, with and without raw loss. |
| T16-a | CLOSED | `test_t16_a_…`: 3 kinds × 8 forms. Each cell first asserts `CustodyFailure` with the post raw deleted, then `CustodyUnreadable` matching `unreadable`. All 24 cells are RED on the old code (X4). |
| T16-b | CLOSED | A readable object with no `battery_float` gives `evidence_missing`, and a bad pre digest gives `pre evidence missing: raw digest not recorded`, for all 3 kinds. |
| T16-c | CLOSED | A duplicate top-level key raises `CustodyUnreadable` matching `duplicate JSON key same in <file>`, for all 3 kinds. |
| **Amendment 30 (erratum)** | **CLOSED** (with NIT-1, NIT-4 and NIT-5 on wording) | The shape comes from the object alone. `completed = "end_stamp" in session` is key presence; the collector's first write has no `end_stamp` key (`scripts/sample_quiet_predicate_evidence.py:1054-1065`), so presence is the right test. Refusal = `end_stamp` absent and `error_class == QUIET_REFUSAL_ERROR_CLASS`. The journal is read only when `battery_float` is present and the shape is (i) or (ii). In shape (i), any rows raise with the text `refusal envelope records none`. In shape (ii), `type(count) is not int or count < 0` raises `round count not recorded`, and a length disagreement raises `holds <n> rows; session records <m>`. `round_workers` is never consulted (grep: no occurrence in `battery_float.py`). The per-row cross-check is gated on the same condition, so shape (iii) is neither opened, counted nor cross-checked. All raises come before span derivation and `authenticate_pair`. The refusal span end is `start_stamp.monotonic_after_s`. |
| T30-a | CLOSED | `test_t30_a_…`: a mismatching row raises `CustodyFailure`; with the journal deleted it raises `round journal missing`. RED on the old code. |
| T30-b | CLOSED | Both variants raise `holds 0 rows; session records 1`, including the one where the pre raw is appended and the `session.json` digest is rewritten. RED on the old code. See Observation O-1 for the limit on this closure. |
| T30-c | CLOSED | `journal_rows: 0` with an empty journal gives `pass`. |
| T30-d | CLOSED | A refusal envelope with the journal deleted raises `round journal missing`. RED on the old code. |
| T30-e | CLOSED | `test_quiet_refusal_span_and_missing_capture_span`: a refusal envelope with one row raises `refusal envelope records none`. The old status expectation is replaced, and the test is RED on the old code. |
| T30-f | CLOSED (NIT-5) | Three sub-rows: absent, one provisional row, and `{`. Each gives `("battery_float_evidence_missing", ("quiet span unavailable",))`, and each raises `CustodyFailure` once the pre raw is deleted. The provisional and `{` sub-rows are RED on the old code. |
| T30-g | CLOSED | A completed envelope without `battery_float` and with no journal gives `evidence_missing`. |
| T30-h | CLOSED | The fixture now defaults to `rounds=True`, sets `journal_rows`, writes the journal for completed and refusal envelopes, and carries `round_workers`. |
| T30-i | CLOSED | `journal_rows` absent, `True`, `"1"` or `-1` each raise `round count not recorded` (RED on the old code). The P-A fixture (1 row, `journal_rows: 1`, `round_workers` of length 2) gives `pass`. X6 adds `False`, `1.0`, `None`, `[1]` and `{}`, which all raise, and `10**30`, which raises the count disagreement. |
| T30-j | CLOSED | Two rows, one of them mismatching, raise `CustodyFailure`. Truncating to one row raises `holds 1 rows; session records 2`. RED on the old code. |
| **Amendment 31 (S0 clauses)** | **CLOSED** | `events.jsonl` goes through `_required_file`, so missing, symlinked, directory and unreadable files raise `events.jsonl unreadable: …`. Non-UTF-8 content raises the same way. Each non-blank line must be a JSON object, or it raises `events.jsonl line <n> unreadable: …`. A well-formed file without the two stage events is still `bundle span unavailable` (`test_missing_event_or_field_refuses_as_unavailable_span`). An events file plus a deleted post raw still raises from rung (b) (`test_custody_precedes_unavailable_span`, and X5 `bundle events.jsonl empty rawloss=1`). The S1 clause is not implemented in S0, which is correct: `bundle_read.py` is untouched. |
| **S-1** | **CLOSED** (NIT-3 residual) | Decorated members are hashed from the first decorator line, and roots keep `inspect.getsource`. A single-binding count is added, a runtime digest check is added, the table is regenerated from base (X2), and only the two decorated pins move. Both mutation self-tests are present. Applied to the live file, the decorator and nested-`def` mutations turn the pin test RED (X9). |
| **S-2** | **CLOSED** | `copy.replace` is flagged however it is imported: `import copy`, `import copy as cp`, `from copy import replace [as r]`, and imports inside a function. `<expr>.__replace__(...)` is flagged, including `type(v).__replace__(v, …)`. `copy.deepcopy` stays clean. `REPLACE_CALL_ALLOWLIST` is unchanged in the diff, and the search finds only two `from copy import deepcopy` lines, so no allowlist row is needed (X10). |

## 2. Same-signature statement

**Same signature: no.** No input S0 reads converts a read or decode failure into an empty value, or a custody failure into a status or `pass`, outside what the rulings expressly place outside custody. The one literal instance, whitespace-only journal lines (NIT-1), carries no recorded bytes, so no evidence can be lost through it.

The X5 matrix, as `result (raw intact) / result (post raw deleted)`. U means `CustodyUnreadable`, CF means `CustodyFailure`.

| File | Shape | delete | empty | truncate | symlink | dup key | directory |
|---|---|---|---|---|---|---|---|
| `session.json` | completed / zero-round / refusal / iii | U / U | U / U | U / U | U / U | U / U | U / U |
| `rounds.jsonl` | completed | U missing | U `holds 0 rows; session records 1` | U line 1 | U | U dup | U |
| `rounds.jsonl` | zero-round, refusal | U missing | pass / CF (no-op: the honest file is already empty) | pass / CF (no-op) | U | U | U |
| `rounds.jsonl` | iii | status / CF | status / CF | status / CF | status / CF | status / CF | status / CF (ruled: not an input) |
| `metadata.json` | bundle | U / U | U / U | U / U | U / U | U / U | U / U |
| `events.jsonl` | bundle | U / U | `bundle span unavailable` / CF (O-2) | U line 2 | U / U | U / U | U / U |
| `instrument_evidence.json` | capture | U / U | U / U | U / U | U / U | U / U | U / U |

Shape moves and witness values (X6):

- **Removing `end_stamp` from a completed envelope** gives shape (iii): `evidence_missing ('quiet span unavailable',)`. With the post raw deleted it raises CF. The same holds with the journal also deleted. The erratum's R-2 names this as the ruled residual, and it is non-pass.
- **Removing `error_class` from a refusal envelope** gives shape (iii) with the same result, and the same with the journal deleted.
- **`end_stamp: null`** (key present) is treated as completed. The journal is then required (deleting it raises `round journal missing`), and the span is unavailable, so the result is non-pass.
- **`battery_float: null`** (key present) leaves the journal rules applying: deleting the journal raises.
- **`journal_rows`** set to bool, string, negative, float, `None`, a list or a dict raises `round count not recorded`. A wrong integer raises the count disagreement.
- **A row with no `raw` key** raises CF. **A non-UTF-8 journal** raises `round journal unreadable: 'utf-8' codec …`. **A FIFO journal** raises `not a regular file`.

Observations for the magistrate. These are ruled residuals, not findings.

- **O-1. The T30-b closure holds only while `session.json`'s control fields are intact.** Take a completed envelope, drop `end_stamp`, set `error_class: "network_time_provenance"` and empty the journal: the result is **`pass`** (X6). Setting `journal_rows: 0` and emptying the journal also gives `pass`. Both are edits to `session.json` beyond the raw digest. The erratum's R-1 paragraph puts consistent rewrites of `session.json` and the journal out of scope under D-161, so this is not a finding. It does mean the ruling's E2 variant is closed against journal-only loss, not against an actor who already edits `session.json`. This matters only if the threat model is ever widened.
- **O-2. `events.jsonl` emptied, or truncated at a line boundary**, gives `bundle span unavailable`, which is non-pass. Amendment 31's third sentence keeps "objects that decode but carry no stage events" as a status, and an empty file has no non-blank line to fail. With the post raw deleted, rung (b) still raises.

## 3. The honest-failure side

- **P-A (real collector, X7).** On disk: `end_stamp` present, `error = JSONDecodeError: Expecting ',' delimiter…`, `round_workers` = 2, journal rows = 1. Row 1 carries digests for `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`. With `battery_float` added and `journal_rows: 1` simulated, the result is **`pass`, with no raise**. As the collector writes it today, without `journal_rows` or `battery_float`, the result is `evidence_missing` (historical); amendment 33 is S2's job. The fixture form, T30-i part 2, also gives `pass`.
- **P-B (real collector, X7).** On disk: no `end_stamp`, `round_workers` = 0, and one provisional row. The results:
  - With the full pair added, the result is `evidence_missing ('quiet span unavailable',)`.
  - With the journal absent, empty or `{`, the result is the same, with no raise in any case.
  - With the pre raw deleted, it raises CF.
  - With a **pre-only** record (the text-5 first write), the result is `evidence_missing ('post evidence missing: phase not recorded',)`. It does not raise, and the variants with the journal absent, empty or `{` give the same result (NIT-5).
- **Shape (iii) journal absent, empty or `{`.** Each gives `battery_float_evidence_missing: quiet span unavailable` with a full pair (X5, X7, T30-f).
- **Historical population (X8).** For the intact, absent, empty and mismatching-row journal states, in each of the 3 shapes, head and `783a09be` give the same result: `evidence_missing` with both `phase not recorded` reasons. **One change:** a historical envelope whose journal is `{` used to raise `round journal unreadable` and now gives `evidence_missing`. The erratum rules exactly this: "if the object has no `battery_float` key, the verdict is text 2(a) `evidence_missing` and this amendment does not apply". A historical envelope records no battery digest, so no custody is at stake, and text 6 already treats it as "never a number". **No honest shape now raises.**

## 4. Freeze fence

This is verified independently (X2). Every `FROZEN_ROOTS` closure member, 39 in all, is byte-identical to `git show 5d5a0b75:joulewise/battery_float.py` under both the test's segment rule and a decorator-inclusive full-line rule. Every pin equals sha256 of the base segment. The table comment carries the "regenerate from the BASE file" rule. `CustodyFailure` is still pinned at `af27587c` (base bytes). `CustodyUnreadable` is a subclass whose `__init__(detail)` sets `failures = []` and does not widen the base. The round-4 diff does not touch `authenticate_pair` (rungs (a)–(f)).

## 5. Guards

- **S-1, live file mutations (X9).** Control: OK. `frozen=False` on `AuthenticatedVerdict`: **FAILED** (`source pin changed` and `runtime pin changed`). An appended `if True: def _is_sha256`: **FAILED** (`2 module-level bindings`). Rebinding by a `for` target, a walrus or `LIMIT_MA += 1`: **FAILED** (binding count). Rebinding `_is_sha256` by a match capture: **FAILED** (runtime pin). A match capture rebinding the constant `_SHA256`: **OK**. That is the NIT-3 evasion.
- **S-2 (X10).** Every ruled form is flagged. `from copy import *`, `getattr(copy, "replace")` and `operator.methodcaller("__replace__", …)` are not flagged. These are the same forms that were already unguarded for `dataclasses` (prior lens N-2), and they fall outside S-2's ruled text, so they are not findings.

## 6. Findings

### NIT-1: whitespace-only journal lines are silently skipped, and a pre-existing C1 assertion was weakened

**Where.** In `authenticate_quiet_session`'s journal loop, the check is `if not line.strip(): continue`.

**Ruled text.** Erratum amendment 30, shapes (i)/(ii): a journal "that holds any **non-empty** line that is not a JSON object is `CustodyUnreadable("round journal unreadable: <reason>")` (C1)". Amendment 31 says "non-blank" for events, so the two rules differ on purpose.

**Executed.**
- A refusal envelope whose journal is `"  \n"` gives **`pass`**.
- A completed envelope with its one real row plus a `"   \n"` line gives `pass` (X6).
- Round 3 (`if line:`) raised `round journal unreadable` on both.
- Round 4 changed the existing assertion in `test_round_journal_mismatch_and_malformed_both_raise` from `"round journal unreadable"` to `"holds 0 rows"` (see the `git diff 783a09be HEAD -- tests/test_battery_float.py` hunk at about line 370).

**Why only a NIT.** A whitespace line carries no recorded bytes, and the `journal_rows` count still binds real rows, so nothing can be lost through it. It is still a literal departure from C1, and it weakens a test the seat did not own.

**Fix.** In the journal loop, use `if not line: continue` (restoring round 3's predicate). Restore the `"round journal unreadable"` assertion for `"  \n"`, and add a refusal-shape `"  \n"` row expecting `CustodyUnreadable`. Leave the events loop at `.strip()`.

### NIT-2: a decode `RecursionError` escapes as a non-`CustodyFailure`

**Where.** `_required_object`, and the line loops for `rounds.jsonl` and `events.jsonl`.

**Executed (X11).** A 200 000-deep `[` in any of the three files raises `RecursionError`, which is neither a `CustodyFailure` nor a `ValueError`.

**Why only a NIT.** It is a raise, never a status, and no honest producer writes such a file. But amendment 29 says "any failure raises `CustodyUnreadable`", and a consumer with a broad `except Exception` exclusion handler would treat it as an exclusion.

**Fix.** Use `except (ValueError, UnicodeError, RecursionError)` in `_required_object`, and `except (ValueError, RecursionError)` in both line loops. Add one T16-a form: `"[" * 200000`.

### NIT-3: the S-1 single-binding count misses match-capture patterns

**Where.** In `_frozen_closure_issues.ModuleBindings`, the counted forms are `Name(Store)`, `def`/`class`, imports and `global`. `ast.MatchAs.name`, `ast.MatchStar.name` and `ast.MatchMapping.rest` are plain strings, not `Name` nodes, so they are never counted.

**Executed (X9).** Append `match re.compile(r'.*'):\n    case _SHA256:\n        pass` to the file. The pin test stays **OK**, while `battery_float._is_sha256("zz")` is now `True`. For functions, the runtime pin catches the same trick, but no runtime check covers non-function constants. A `globals()[...] =` write also stays green; that is dynamic and outside the ruled AST rule.

**Why only a NIT.** The form is contrived, and the fence is a backstop for later PRs, not an S0 correctness gate.

**Fix.** In `ModuleBindings`, add `visit_MatchAs`, `visit_MatchStar` and `visit_MatchMapping`, each counting its `name`/`rest` when not `None` and then calling `generic_visit`. Add a mutation self-test using the `_SHA256` match capture. Optionally, for `Assign` members, add a runtime value check against the evaluated base segment (for example `_SHA256.pattern`, and `LIMIT_MA == 200`).

### NIT-4: a non-regular or symlinked journal gives a different label from the one ruled

**Ruled text.** Erratum amendment 30: "`rounds.jsonl` must exist as a regular file (`lstat`, no symlink), else `CustodyUnreadable("round journal missing")`".

**Executed (X5).** A symlinked journal raises `round journal unreadable: rounds.jsonl unreadable: symlink`, and a directory raises `… not a regular file`. Both are `CustodyUnreadable`, and the pre-existing `test_unreadable_round_journal_refuses` expects the "unreadable" label.

**Fix.** Either map the symlink and non-regular cases to `"round journal missing"` and update `test_unreadable_round_journal_refuses`, or record in the PR body that the label follows the older test. The class is correct either way, so this is wording only.

### NIT-5: T30-f and the shape-(iii) single-reason sentence, for a pre-only record

**Ruled text.** Erratum amendment 30, shape (iii): "The verdict is `battery_float_evidence_missing` with the single reason `quiet span unavailable`". T30-f says "one provisional row … beside a pre record".

**Executed (X7).** The real P-B shape with a **pre-only** `battery_float` (the text-5 first write) gives `('post evidence missing: phase not recorded',)`. It does not raise, even with the journal absent, empty or `{`. The single reason cannot hold here, because rung (a) comes before the span rung (T2 order, which the brief keeps untouched). The seat's T30-f uses a full pair, which does give the single reason.

**Fix.**
1. Add a pre-only sub-row to T30-f that asserts no raise and `status == "battery_float_evidence_missing"`, without an exact-reasons check. This covers the realistic kill-mid-envelope shape.
2. Flag the erratum sentence for the magistrate. It should read "…`quiet span unavailable` when both phases are recorded; otherwise the rung-(a) reason". This is a text clarification, and no code change is needed.

## 7. Seat-report cross-check

The seat's claims hold under my replay:
- V1 passes: 134 tests, OK (X3).
- 39 frozen members are unchanged, and only 2 pins move (X2).
- The listed cases were RED before the change (X4 reproduces them independently: 37 failures and 7 errors, against the seat's 32 and 6; the difference comes from the extra T15 edits I included).
- "Same signature: no" is upheld, with NIT-1 as its only literal exception.

The seat's P-D note (F2) belongs to S2 (amendment 32) and is correctly left open for that lane.
