# BFG-S S0 (helper and arm fence): cold Fable final pass (gate row 7, plus the row-10 fresh-eyes review of `b7df341b`)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single non-interactive foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-s0fp-f8d6cab1` at HEAD `b7df341beecf8d566905d68468d5aa2504a6423f` (`git rev-parse HEAD`; `git status --short` empty before and after; `git merge-base --is-ancestor 5d5a0b75 HEAD` true). Session 2026-09-26. Charge sha256 verified `3ec4fda7ac82cab1407b581066a60bbc8d1e53eb29e12e84dac2299ae6158242`. Only this file was written; scratch probes ran under `/tmp/fp/` and touched no repository file.

## 0. Contamination disclosure

Loaded by the harness without my choosing: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers, including loop-context checkpoint titles that name BFG-S S0 and commit hashes). A system reminder supplied the git status and five recent commit subjects. I opened no memory file body, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `CLAUDE.local.md`, no `AGENTS.md`, no decision log, and no process trace outside the paths the charge names.

Read by me: the charge; the erratum ruling (amendments 30, 31, 26, 32, 33, 34, T30-a…j); addendum 3 (amendment 29, T16, §4 class table); addendum 2 (amendments 20–28); Final texts v1.1 §4 in full; the round-3 fix contract and lead rulings 44; the two round-4 lenses (Astra `51`, Opus `52`); the round-4 seat report `41`; the full `git diff 5d5a0b75 b7df341b` (three modules, five test files); `joulewise/evidence_night.py:1339-1420, 1541-1560`; the collector's journal writes (`scripts/sample_quiet_predicate_evidence.py:1138-1208`) and the two event writers (`joulewise/bundle.py:985-1000`, `joulewise/quiet_predicate_campaign.py:203-207`) for one design probe. I did not read the round-3 lenses `10`/`11` beyond their S-1/S-2 restatement in the rulings.

## 1. Executed evidence (this session; every probe in the foreground)

| # | Probe | Result |
|---|---|---|
| E1 | `python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep` | `Ran 135 tests in 121.8s` / `OK` (the seat's 134 plus `b7df341b`'s encoding test). |
| E2 | `python3 -m unittest tests.test_evidence_night tests.test_night_kinds` | `Ran 181 tests in 377.4s` / `OK`. Together 316 tests, all green. |
| E3 | **Q2, recomputed independently** (`/tmp/fp/pins.py`): `git show 5d5a0b75:joulewise/battery_float.py` loaded as a module; the closure rebuilt from `FROZEN_ROOTS` over `Name` loads on base and on head; each member hashed under the test's own segment rule (roots by `inspect.getsource`, decorated members from the first decorator line, others by `ast.get_source_segment`) | Base closure = head closure = table keys, 39 members. For all 39: pin == sha256(base segment) **and** base segment == head segment byte for byte. **0 mismatches.** `CustodyFailure` is at its base bytes (`af27587c…`); `CustodyUnreadable` is a new subclass outside the closure. |
| E4 | **Q3 RED replay**: `git archive b7df341b` into `/tmp/fp/red`, `joulewise/battery_float.py` replaced by `c9081c6e`'s copy, then `test_t16_a_valid_json_in_another_encoding_refuses` | `FAILED (failures=6)`: all 3 kinds × utf-16/utf-32 fail on the old code, as the commit message claims. |
| E5 | **Q3 encoding matrix** (`/tmp/fp/probe.py`): each of the five files (`session.json`, `rounds.jsonl`, `metadata.json`, `events.jsonl`, `instrument_evidence.json`) re-encoded as utf-16 (BOM), utf-16-le (no BOM), utf-32, utf-8 with BOM, and utf-8 with one trailing latin-1 byte | 25/25 cells `CustodyUnreadable`. The line files refuse through `.decode("utf-8")` (BOM/latin-1) or through the per-line decode (utf-16-le's NULs). No file admits a non-UTF-8 body. |
| E6 | Sol reproducer `10-sol-repro.py` on the candidate | `quiet / bundle / capture: CustodyFailure -> CustodyUnreadable`; `deleted rounds.jsonl: CustodyFailure -> CustodyUnreadable`. F1 and F2 closed. |
| E7 | **P-A** as fixture: completed, `journal_rows: 1`, one agreeing row, `round_workers` of length 2, `error` set | `pass`, no raise. |
| E8 | **P-B, pre-only** (the collector's first write: no `end_stamp`, no `journal_rows`, `battery_float = {"pre": …}`), with the journal absent, empty, one provisional row, `{`, and `"  \n"` | Every variant `battery_float_evidence_missing ('post evidence missing: phase not recorded',)`, **no raise**; every variant with the pre raw deleted → `CustodyFailure` from rung (b). |
| E9 | P-B with the full pair and a provisional journal (the seat's T30-f) | `evidence_missing ('quiet span unavailable',)`. |
| E10 | Same-signature residuals: `battery_float: null` + journal deleted; historical (no key) + journal `{`; rung-(a) fault in the post phase beside a tampered post raw; the same beside a tampered **pre** raw; `events.jsonl` empty, then plus post raw deleted | `CustodyUnreadable(round journal missing)`; `evidence_missing` (ruled: historical); `evidence_missing: wall time not recorded` (ruled T2 order); **`CustodyFailure`** (the other phase's custody is not masked); `bundle span unavailable` then `CustodyFailure`. |
| E11 | D-161 residual (Opus O-1): completed envelope with `journal_rows := 0` and the journal emptied; completed envelope re-labelled as the refusal shape (drop `end_stamp`, set `error_class`) with the journal emptied | `pass` / `pass`. Reproduced; out of scope as the erratum states (§4 below). |
| E12 | Opus NIT-1: refusal envelope whose journal is `"  \n"` | `pass`. NIT-2: `session.json` = `"[" * 200000` → `RecursionError` escapes (a raise, not a status). |
| E13 | Container root passed through a symlink (`link -> envelope dir`) | `CustodyUnreadable("raw path traverses a symlink: …/link")` (design note D-1). |
| E14 | `str.splitlines()` versus `"\n"`: a journal row carrying a raw U+2028 inside a string value (`ensure_ascii=False`) | `CustodyUnreadable(… Unterminated string …)`; the same row escaped by default `json.dumps` → `pass`. Both producers use default `json.dumps` (ASCII output), so no honest row splits today (design note D-2). |
| E15 | The proposed fix-first test (`/tmp/fp/test_t30f_preonly.py`, §6) run against the unmodified candidate | `Ran 1 test` / `OK`. |
| E16 | `git diff --check 5d5a0b75 b7df341b` | clean. Diff touches exactly the eight WRITE_SCOPE paths. |
| NOT EXECUTED | Live `collect`, controller, `ioreg`, `sudo`, `launchctl` | Not run; P-A/P-B were fixture-shaped (the erratum's own P-A/P-B ran the real collector at `783a09be`; the on-disk shapes are as it recorded). The seat's V3 live-identity probe was not rerun. |

## 2. Q1: faithful and complete for S0's scope?

**Yes, with one test row short (T30-f's pre-only sub-row).** Every clause the rulings assign to S0 has a code home and a biting test:

| Text / amendment | Code | Test | State |
|---|---|---|---|
| Text 1 `PHASES`, sweep | `battery_float.py:34-35`; `test_battery_float_sweep.py` `_observe_phases` (aliased forms, C11) | `test_every_production_observe_phase_is_registered`, `test_aliased_out_of_set_phase_is_visible` | closed |
| Text 2 `PairVerdict`, `authenticate_pair`, rungs (a)–(f), custody raises before any status | `:759-895` | `PairAuthenticationTests` (one test per rung), `test_custody_raises_before_confounded_or_missing_status` | closed; E10 confirms the other-phase custody is never masked |
| Text 3 pins, `observe` golden | table `test_battery_float.py:29-71`, `S0FreezeTests` | `test_frozen_function_sources_match_base`, `test_observe_seven_old_phases_match_pre_s0_bytes` | closed (E3) |
| Text 4 guard: 7th row, `PairVerdict` call violation, wrappers call core only | `test_battery_float_consumers.py` | `test_the_allowlist_has_exactly_seven_rows`, `test_pair_verdict_calls_outside_module_are_flagged…`, `test_only_core_references_parser_and_wrappers_only_call_core` | closed |
| Text 15 fence (`battery_brackets`, no `skipped`, not in the exemption) + C5 + C6 | `night_kinds.py:41`; `evidence_night.py:1386-1395, 1544-1547` | T4 rows: `test_qpe_candidate_is_not_armable_before_s2`, `test_unknown_payload_kind_has_a_failed_battery_brackets_check`, `test_battery_brackets_has_no_skipped_state_or_exemption`, `test_missing_battery_brackets_attribute_records_normal_refusal`, `test_stale_check_without_battery_brackets_row_is_refused`; `test_battery_bracket_flags_are_a_pre_s2_arm_fence` | closed; `require_fresh_check` is the only `check.json` reader on the arm and notice paths (`:1558`, `:1724`), both pass through the new guard |
| Text 17 staleness pin | — | `test_future_update_time_*` at parse, pair and window level | closed |
| Amendments 20–25, 27 (T15) | `monotonic_ns_from_s`, `QUIET_REFUSAL_ERROR_CLASS`, span/stamp rungs, `bundle_sha256`, factories, capture identity | `RoundThreeAuthenticationTests` | closed |
| C1/C3/C4/C9 (journal parse, symlink raw, duplicate keys, exact-int exit code) | `_raw_bytes`, `_json_pairs`, rung (c) | the T15 tests named for each | closed |
| Amendment 29 (mandatory containers) | `_required_file`, `_required_object`; no empty fallback remains (verified by reading the diff) | T16-a (8 forms × 3 kinds), T16-b, T16-c, plus `b7df341b`'s encoding row | closed (E5) |
| Amendment 30 erratum (shape from the object alone; (i) zero rows; (ii) `journal_rows` witness; (iii) journal not opened; raises precede span and `authenticate_pair`) | `authenticate_quiet_session:954-1010` | T30-a, b, c, d, e, g, h, i, j | closed; `round_workers` is never consulted |
| T30-f | — | committed with a **full pair** in all three sub-rows | **open by one sub-row**: the erratum's second sub-row says "beside a pre record"; the pre-only shape is untested, though E8 shows it behaves |
| Amendment 31 S0 clauses (`events.jsonl` mandatory, object lines, well-formed-but-empty stays a status) | `authenticate_bundle:1027-1043` | `test_events_non_object_missing_and_malformed_refuse`, `test_missing_event_or_field_refuses_as_unavailable_span`, `test_custody_precedes_unavailable_span` | closed (E10) |
| S-1 (decorator-inclusive pins, single binding, base-only regeneration) | `_frozen_closure_issues` | decorator and nested-rebinding mutation tests | closed (E3) |
| S-2 (`copy.replace`, `__replace__`), C8 allowlist shrink-only, C10 baseline-green guards | `_Checker.visit_Call` | forgery self-tests, `test_replace_call_allowlist_is_exact…`, `test_new_replace_is_flagged_existing_one_is_allowed_and_stale_row_fails` | closed |

Honest-failure shapes: P-A passes (E7); P-B pre-only is a non-raising `evidence_missing` and still raises on raw loss (E8); the zero-round completion passes (T30-c). Same-signature class (addendum 3 §4): every member re-probed refuses as ruled; no reader in the S0 diff converts a read or decode failure into an empty value, and the only status-bearing "empty" is the ruled one (a well-formed `events.jsonl` with no stage events; E10).

## 3. Q2: frozen closure and pin table

**Byte-identical, and the table equals the base segments.** E3 recomputed both from `git show 5d5a0b75:joulewise/battery_float.py`, not from the branch head: 39 closure members, 39 pins equal to sha256 of the base segment under the test's own rule, 39 head segments equal to the base segments. The round-3 breach (`CustodyFailure` widened and self-pinned) is cured as `783a09be` states; the subclass `CustodyUnreadable` carries the string-detail raises and is itself outside the closure, so every consumer refusing on `CustodyFailure` refuses on it (`test_custody_unreadable_refuses_as_custody_failure`). The table comment carries the base-only regeneration rule.

## 4. Q3: the post-lens commit `b7df341b` (row 10)

**Correct and complete for R1.** The one production line changed is `_required_object`'s `json.loads(body.decode("utf-8"), …)` inside the existing `try`, whose `except (ValueError, UnicodeError)` already maps a `UnicodeDecodeError` to `CustodyUnreadable("<file> unreadable: …")`; the duplicate-key hook and the `CustodyFailure` pass-through are unchanged. All three containers go through `_required_object`, so one edit covers quiet, bundle and capture (E5: 15/15 container cells refuse). The test re-encodes an otherwise **passing** container, which is the shape Astra found (the earlier `\xff\xfe` cell was also malformed JSON and could not expose it); E4 shows it RED 6/6 on `c9081c6e`.

**Nothing else in S0 auto-detects an encoding.** The two line files were already strict: `rounds.jsonl` and `events.jsonl` are read as bytes and `.decode("utf-8")` before splitting (`:966`, `:1031`), and each line reaches `json.loads` as `str` (E5: 10/10 line-file cells refuse, including utf-16-le without a BOM, whose NUL bytes survive the decode and fail at the line parse). Raw `ioreg` files are hashed as bytes and handed to the frozen `parse`, which decodes matched lexemes as strict ASCII; its only lenient decode is `stderr` with `errors="replace"`, a display field that gates nothing. The `evidence_night.py` and `night_kinds.py` hunks read no files. A UTF-8 BOM is refused too (Python's `json.loads` rejects it on `str` input; E5).

## 5. Q4: the proposed dispositions

- **Astra R2 / Opus NIT-5: accepted, with the magistrate's reading made the ruled reading.** The erratum's shape-(iii) sentence is read as: *the verdict is `battery_float_evidence_missing`; when both phase records are present its single reason is `quiet span unavailable`; when a phase is absent, rung (a)'s reason stands, since the erratum keeps text 2's order (a)–(f) and rung (a) precedes the span rung.* Reasons: (1) the erratum itself says rung order is unchanged and that the span rung is amendment 21's, which applies "at the span rung only"; (2) Astra's normalization would post-process a verdict to replace a true reason (`post evidence missing: phase not recorded`) with a less informative one and would add a wrapper-level special case that S1/S2 would then have to mirror; (3) the status is identical and text 6 blanks either. The code stands. What does not stand is T30-f as committed: its three sub-rows all carry a full pair, so the honest P-B shape (pre record only) that the erratum names is not pinned. §6 supplies the row; E15 shows it passes on the candidate unchanged.
- **Opus NITs 1–4: deferral accepted.** None changes a number and each is a raise-or-pass on a shape no honest producer writes. Notes for the follow-up lane: NIT-1 (whitespace-only journal line skipped) departs from C1's "non-empty line" wording but loses no recorded byte, and the `journal_rows` count still binds real rows (E12); NIT-2's `RecursionError` is a raise that no consumer handler in the rulings catches (S2's `pilot_summary` catches `OSError`/`ValueError` only), so it refuses today, and mapping it to `CustodyUnreadable` is the tidy fix; NIT-3 (match-capture rebinding) is a fence backstop, not an S0 correctness gate; NIT-4 is label wording only.
- **The Opus residual: accepted.** E11 reproduces both consistent-edit shapes as `pass`. Both require editing `session.json`'s control fields together with the journal, which is the consistent multi-file rewrite the erratum places outside D-161's threat model. Single-file loss, truncation, emptying and re-encoding all refuse (E5, E6, T30-a/b/d/j).

## 6. Verdict: FIX-FIRST (test-only), then MERGE without a further lens round

One exact change, no production line moves, no pin moves:

Add to `tests/test_battery_float.py`, class `MandatoryContainerAndJournalTests`, after `test_t30_f_provisional_journal_is_not_input_but_raw_custody_remains`:

```python
    def test_t30_f_pre_only_first_write_is_not_custody(self):
        # P-B as the collector writes it: first-write session (no end_stamp,
        # no journal_rows), pre record only, provisional journal. Rung (a)
        # names the missing post; the provisional journal is not opened;
        # raw loss still raises from rung (b).
        for journal in (None, "", '{"raw":{"paths":[],"sha256":{}}}\n', "{"):
            with self.subTest(journal=journal), tempfile.TemporaryDirectory() as tmp:
                session, pair = self.quiet(tmp)
                del session["end_stamp"], session["journal_rows"]
                session["round_workers"] = []
                session["battery_float"] = {"pre": pair["pre"]}
                (Path(tmp) / "session.json").write_text(json.dumps(session))
                path = Path(tmp) / "rounds.jsonl"
                path.unlink()
                if journal is not None:
                    path.write_text(journal)
                verdict = battery_float.authenticate_quiet_session(tmp)
                self.assertEqual((verdict.status, verdict.reasons),
                                 ("battery_float_evidence_missing",
                                  ("post evidence missing: phase not recorded",)))
                (Path(tmp) / "raw/battery_float.pre.ioreg").unlink()
                with self.assertRaises(battery_float.CustodyFailure):
                    battery_float.authenticate_quiet_session(tmp)
```

E15 ran exactly this body against `b7df341b` and it passes. It is the erratum's T30-f second sub-row as written ("beside a pre record"), and it is the durable record of the §5 reading: S2's T6(e) (the P-B envelope through `pilot_summary` does not raise) depends on this helper behaviour. After the lead bench commit adds it and `tests.test_battery_float` is green, the candidate is **MERGE**. No refusal, no design stop.

Why not plain MERGE: this is the one T-row the rulings assign to S0 that the candidate does not carry, and the shape it pins is the honest kill-mid-envelope case whose false `CustodyFailure` was the erratum's R-2 blocker; five minutes of lead bench work pins it against regression while S1/S2 build on the helper. Why not a seat round: nothing in production changes and the assertion values are executed, not predicted.

## 7. Q5: design-level notes (none stops S0)

- **D-1. A container path that is itself a symlink refuses.** `_raw_bytes` `lstat`s the root before the components (E13: `CustodyUnreadable`). Production sites will pass the executor's real envelope directories and real bundle paths, so this is a raise on a shape that should not occur, never a status; S1/S2 briefs should say "pass the real directory, never a `latest` symlink". Tests under macOS `/var/folders` are unaffected because only the final component is inspected as the root.
- **D-2. `str.splitlines()` splits on Unicode line separators** (U+0085, U+2028, U+2029, form feed), not only `\n`. Both producers write default `json.dumps` (ASCII, separators escaped), so no honest row can contain one raw (E14, second line). If either producer ever switches to `ensure_ascii=False`, a row with a raw U+2028 inside a string would become a false `CustodyUnreadable`. The follow-up lane should split on `"\n"` only (a one-token change in two places); it is not a number-bearing defect today.
- **D-3. `authenticate_bundle` requires `events.jsonl` whether or not `metadata.json` carries `battery_float`.** This is consistent with text 8 only because state (ii) (key absent, historical set) never calls the helper; S1's `BundleReader.metadata()` and `authenticate_window_members` must keep that order, which amendment 26 already dictates. Stated here so S1's refuter checks it.
- **D-4. `end_stamp: null` (key present) classifies as completed**, so the journal and `journal_rows` are required and the span is unavailable; the outcome is a raise or a non-pass, never `pass`. The collector never writes a null `end_stamp`, so this is a correct fail-closed reading.
- **D-5. The arm fence is complete for S0's purpose.** `check()` records `battery_brackets` for every candidate that reaches the payload-kind block, fails closed on an unreadable kind, an unknown kind, or a kind row without the attribute, and `require_fresh_check` refuses a `check.json` without a passing row on both the publish-install and notice paths. A QPE candidate is not armable until S2 flips the flag in the same PR as the collector brackets (text 15).

## 8. Plain summary for Ed (5 lines)

1. The helper does what the rulings say: every file it depends on must be present and readable or the whole computation refuses; a file that reads cleanly but lacks the battery record is "evidence missing"; tampering with a raw reading is always a custody failure, never hidden behind another fault.
2. I recomputed the freeze fence from the main branch's own bytes: all 39 pinned pieces are unchanged, and the earlier breach is cured.
3. The last fix (UTF-16/UTF-32 files were being accepted) is right and complete; I re-checked all five files in five encodings and every one is refused.
4. One test is missing: the honest "collector killed after its first write" shape, which must not be called tampering. The code already handles it (I ran it); the lead should add the eight-line test, then merge.
5. The two small residuals (consistent multi-file rewrites by an operator; four wording-level nits) are correctly deferred, and nothing here should stop S1 and S2 from building on this.
