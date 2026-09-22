# Cold-gate packet — the A267 + A269 merge transaction: a second fix round on two already-ruled defects (item 2's header guard and item 1's attestation bound), the ratification of one seat deviation, and the single D-138 atomic re-freeze that lands the feature branch and the re-issued D-079 acceptance together or not at all (charter §3 triggers: a second fix round on the same defect; an irreversible action — a merge and the measurement-window commitment that follows it)

Assembled 2026-09-22 by a packet-assembly agent under the resident magistrate's dictation (activation 59857fe5). Mechanically assembled: exhibit A is verbatim `git show <rev>:<path>` output located by `ast` spans or by printed anchor strings (generator in this directory); exhibit B is verbatim anchor-located extracts of the controlling rulings, the decision log and the fix-round brief, each carrying the five fields the charter requires of a bounded excerpt (generator in this directory); exhibit C is generator output executed at assembly time over the repository's own objects — the estimator-pin digests, the acceptance artifacts' derivation-digest recomputation through the production helper, the header guard evaluated on three saved log bodies, and the path-overlap check — with the expensive runs (test suites, corpus replay, quick tier, corpus verify) quoted verbatim from the magistrate's record and labelled with the step that executed them, never re-run; exhibits D1, D2 and D3 are byte-identical copies of the two delta-review lenses and the implementation seat's report, and are LABELLED ARGUMENT, not evidence. The assembler wrote only this file and the three generators, and decided nothing: where a dictated fact did not match the primary evidence, the packet follows the evidence and the divergence is named in the facts below.

**A naming collision the judge must hold.** The magistrate's record calls two saved `log show` captures "exhibit D2" and "exhibit D3". This packet's exhibits D1/D2/D3 are the contract lens, the execution lens and the seat report. The two saved captures are cited here only by their tracked repository paths, `docs/process_traces/2026-09-22-activation-59857fe5/07c-exhibit-D2-timed-log-0210-0435-syslog.txt` and `…/07c-exhibit-D3-timed-log-zero-match-syslog.txt`, and their digests are printed in exhibit C3.

## What happened

Lane A267 (clock-discipline anchor v3.1 and the network-time attestation) and lane A269 (the harness's 7.6–10.2 s per-envelope start drift) were both ruled by cold gates — A267 by rulings 10 and 14 under activation d9990b3c, A269 by ruling 10 under activation e4b4ead6. Their implementations share one branch, `feat/2026-09-22-a267-clock-anchor-v3_1`, whose head is **`489b0953`** (base `447fd6bf`, 21 commits). A delta re-audit of fix round 1 ran two lenses over it: a contract lens (exhibit D1, Fable, read-only) returning 0 blockers / 5 should-fix / 6 nits, and an execution lens (exhibit D2, Opus, mutation licence on its own copy) returning 1 blocker / 7 should-fix / 4 nits.

**The blocker, confirmed at the bench.** Brief 06 item 2 (exhibit B6) ordered a guard that refuses to call an envelope `authenticated` unless the `log show` body carries the query's column header. The seat built the guard's constant from the only log artifact in the repository, `tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt`, whose first line is `'Timestamp               Ty Process[PID:TID]'` — the **`--style compact`** header. The argv ruled by A267 ruling 14 R4 (exhibit B2) uses **`--style syslog`**, whose header is `'Timestamp                       (process)[PID]    '`. Exhibit C3 executes `timed_log_has_header` as it stands at `489b0953` over three bodies: `True` on the compact fixture, **`False` on the live syslog capture (191 lines) and `False` on the live zero-match syslog capture (one line, 51 bytes)**. Every envelope of a real night would therefore become `asserted` with exclusion `network_time_unattested`, and the night would retain nothing. Exhibit C3 also shows the header is the *only* style-dependent part: the fixture and the live syslog capture are both 191 lines and both yield `timed_log_marker_lines` = 30.

**The should-fix that reopens a dictated shape.** Item 1 (exhibit B6) dictated the attestation query's timeout as `max(5, slot_pitch_s − envelope_s − 5)` = 15 s under registration v2, where the slot pitch is 620 s and the capture 600 s, leaving a 20 s inter-slot gap. Exhibit A shows the module already spends that same reserve twice: `cleanup_budget_s` returns `max(1, gap − CLEANUP_BUDGET_RESERVE_S)` = 15 s and its comment says the 5 s it holds back is "a reserve that the attestation's `log show` fits in", while `attestation_timeout_s` returns `max(ATTESTATION_TIMEOUT_FLOOR_S, gap − CLEANUP_BUDGET_RESERVE_S)` = 15 s. Two bounds, each claiming 15 s of the same 20 s gap.

**The D-138 transaction.** D-138 (exhibit B1) makes any change to one of four governed estimator files deliberately stale the issued D-079 calibration acceptance, and forbids re-keying the tests that detect that staleness. The A267 deriver change moves one of the four, `joulewise/uncertainty_evidence.py`. A successor acceptance, r7, was prepared by hand on `scratch/r7-dryrun-e4b4ead6` (head `e52c7fbc`, base `447fd6bf`). Exhibit A's recursive field diff shows r7 differs from r6 in exactly **3 of 428 leaf fields** — `acceptance_id`, `derivation_sha256`, and the one estimator pin — with nothing added and nothing removed. Exhibit C1 shows the four governed files at the final feature head `489b0953` hash exactly to r7's pins, and that only the `uncertainty_evidence.py` pin moved between r6 and r7. Exhibit C2 recomputes each artifact's `derivation_sha256` through the production helper `calibration_bracketing._canonical_sha256` over every key but that one: both MATCH. Exhibit C5 shows r7's registry pin equals the digest of r7's own bytes. Exhibit C4 shows the feature branch's 9 changed paths and the scratch branch's 10 changed paths have an **empty** intersection.

**Divergences between the dictation and the evidence, named.** (i) The lead's brief describes the scratch delta as "5 commits"; exhibit A prints `commit count: 4`. (ii) The lead's dependent-pin list names five code/config files "and four test modules"; exhibit A's `--stat` shows ten paths, the tenth being `tests/verify_calibration_acceptance_corpus.py` (+3 lines), unnamed in the dictation. (iii) The record describes the zero-match capture as "50 bytes"; the saved file is 51 bytes (exhibit C3) — the header line is 50 characters and the file carries a trailing newline. (iv) The lead's Q3 disposition speaks of updating "the two test pins"; the assembler finds four assertions plus one harness argument inside a single test, enumerated under Q3 below. (v) Exhibit D1 §S1's failure arithmetic does not reproduce from its own inputs: a 10.23 s finalisation tail plus a 9 s query is 19.23 s, which fits inside the 20 s gap, so it produces no drift at all; on the numbers A269 ruling 10 Q1 accepts (exhibit B3), the drift exceeds the 2 s abort only when tail + query exceeds 22 s, i.e. for a query of roughly 11.8–15 s rather than the lens's "~8–15 s". The *direction* of the lens's finding is unaffected — a 15 s bound can breach the gap and a 5 s bound cannot — but the judge should not adopt the lens's band as verified. This is assembler arithmetic over the numbers in exhibits B3 and D1; nothing was re-measured.

The lead's labelled dispositions (argument, not evidence): Q1 option (a); Q2 option (a); Q3 option (b); Q4 affirm as-implemented; Q5 adopt all as dictated; Q6 the corpus stands; Q7 yes with the standard no-objection window.

## Q1 — The D-138 atomic re-freeze transaction: what shape may it take, is r7 as prepared admissible as the issued acceptance, and what must the lead re-execute at the final head

**Facts.** D-138 (exhibit B1) orders that a branch changing a governed estimator input "merge[s] ONLY inside the atomic Phase-2 successor re-freeze transaction that re-issues the acceptance artifact and every dependent pin", that follow-on work touching the same pinned files rides the same branch, and that "tests may re-key only private synthetic fixtures". The r7 delta is a pure pin delta (exhibit A's field diff: 3 of 428 leaves), its pins match the final head's bytes (C1), its derivation digest is self-consistent (C2), its registry pin matches its own bytes (C5), and it touches no path the feature branch touches (C4). Neutrality of the science was checked by the magistrate and is quoted, not re-run: the corpus verify script prints the identical five statistics and `PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK` for r6 and r7 (C6, record step 9); the six D-138-affected calibration modules ran `Ran 349 tests in 546.361s OK (skipped=5)` on the scratch branch (C6, step 11); the quick tier ran `modules=153 excluded=92 failures=0 seconds=72.139 result=PASS` at `e52c7fbc` (C6, step 12); the 38-member corpus replay returned `EQUAL 38, DIFF 0, NOT_EXECUTED 0` at `62412ee6` (C6, step 18), and `62412ee6..489b0953` is a docstring-only diff, printed in full in C6. **Contrary evidence, included:** the magistrate's own seven-module exit-contract run at `62412ee6` returned `Ran 616 tests in 884.637s FAILED (failures=1)` (C6, step 22). The failing test exercises three files the fix round does not touch, and both the test alone and its whole module alone re-ran green; the record classifies it a contention flake, which is argument the judge may weigh, not a verified fact.

**Options.** (a) Rebase the scratch delta onto the FINAL feature head after fix round 2, open ONE pull request from that branch, and merge it with a single merge commit — feature and r7 land together or neither lands. (b) Squash the whole thing into one commit before merging. (c) Two pull requests, feature first and r7 second — which D-138 as written rejects, since main would then carry a window in which the issued acceptance is stale.

**Lead's disposition (argument, not evidence): (a).** Reasons offered: the atomicity D-138 demands is a property of the merge, not of the commit count, and one merge commit gives it while preserving the per-item commit trail the C-028 gauntlet reads; (b) destroys that trail for no atomicity gain; (c) is the shape D-138 exists to forbid.

**Deliver.** The ruled transaction shape; whether r7 as prepared (exhibit A's field diff, C1, C2, C5) is admissible as the *issued* acceptance or needs anything further; and the exact pre-merge proof set the lead must RE-EXECUTE at the final rebased head. The lead proposes that set as: (i) the 38-member corpus replay, `EQUAL 38 / DIFF 0 / NOT_EXECUTED 0`, with the member ids in the pull-request ledger as ruling 14 R3(b) requires (exhibit B2); (ii) the corpus verify script on r6 and r7 showing identical statistics and `PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK`; (iii) the derivation-digest recomputation MATCH for r7; (iv) the four governed estimator digests against the head's bytes; (v) the quick tier green; (vi) the six D-138 calibration modules and the seven brief-06 exit-contract modules green; (vii) the twelve-row gate ledger in the pull-request body.

## Q2 — Item 2's header guard: the guard text, the fixture set, and the regressions

**Facts.** The guard at `489b0953` is `TIMED_LOG_HEADER_FIELDS = ("Timestamp", "Process")` with `timed_log_has_header` testing that both substrings appear in the body's first line (exhibit A, `joulewise/quiet_predicate_campaign.py:443-456`). The comment above it asserts that `log show --style syslog` prints `Timestamp ... Ty Process[PID:TID]` — which is the compact header, not the syslog one. Exhibit C3, executing that exact code over three bodies: compact fixture `True`; live syslog capture `False`; live zero-match syslog capture `False`. Marker parity: fixture and live syslog capture are both 191 lines with 30 marker lines each; the zero-match capture is one line with 0. The zero-match capture settles the premise the execution lens could not settle from the repository alone: a query that matched nothing still prints the header.

**Options.** (a) Pin the exact syslog header line as a frozen constant — `TIMED_LOG_SYSLOG_HEADER = "Timestamp                       (process)[PID]"`, guard = the body's first line, right-stripped, equals that constant — add the two live captures as tracked fixtures, run the twelve ruling-14-R3 regressions over the syslog fixture as well as the compact one, and add a regression that the guard accepts both live captures' first lines and rejects the empty body, an HTML error page, a headerless entry line and the COMPACT header. (b) A style-agnostic rule: the first line starts with `"Timestamp"`. (c) Change the ruled argv to `--style compact` so the fixture matches.

**Lead's disposition (argument, not evidence): (a).** Reasons offered: (b) would accept any body whose first line begins with the word, including a compact-style body produced by an argv nobody ruled, and the defect being cured is precisely a mismatch between the guard's constant and the ruled argv's output — a guard that cannot tell the two styles apart cannot detect that mismatch recurring; (c) amends a ruled argv for a fixture's convenience.

**Evidence for the proposed guard, executed.** Exhibit C3b evaluates the proposed rule over eight bodies: `True` on the live syslog capture and on the zero-match capture; `False` on the compact fixture, the empty body, an HTML error page, a bare newline, a headerless entry line taken mechanically as the live capture's second line, and the compact header alone.

**Deliver.** The ruled guard text (exact constant and comparison), the ruled fixture set, and the regressions with their counterfactuals — or a different guard, with the executed evidence you accept for it.

## Q3 — Item 1's attestation bound

**Facts.** Exhibit A prints both budgets at `489b0953`: `attestation_timeout_s(protocol) = max(ATTESTATION_TIMEOUT_FLOOR_S, gap − CLEANUP_BUDGET_RESERVE_S)`, and `cleanup_budget_s(protocol) = max(1, gap − CLEANUP_BUDGET_RESERVE_S)`, where `gap = slot_pitch_s − envelope_s` = 20 s under registration v2. Both return 15 s. The comment block above `CLEANUP_BUDGET_RESERVE_S` states that the teardown's budget is the gap minus a reserve the attestation's query fits into, "so a teardown can never eat the attestation's time or run into the next spawn" — a claim the 15 s bound contradicts. A269 ruling 10 Q1 (exhibit B3) accepts as its own arithmetic a worst observed finalisation tail of 10.23 s and a worst attestation of 1.45 s, 11.7 s inside the 20 s gap, and Q3 of that ruling pins an in-chain abort at `start_drift_abort_s` = 2 s that refuses the whole night at the first slot whose start drift exceeds it (exhibit B4). Exhibit D1 §S1 argues the 15 s bound can therefore convert a recoverable one-envelope loss into a refused night; the assembler's note (v) above bounds where that is true: tail + query must exceed 22 s.

**Options.** (a) Keep 15 s and rewrite the `CLEANUP_BUDGET_RESERVE_S` comment so the module stops asserting a reserve it does not hold. (b) `max(ATTESTATION_TIMEOUT_FLOOR_S, gap − cleanup_budget_s(protocol))`, which is 5 s under v2 (20 − 15, floored at 5) and 5 s at a 700 s pitch (100 − 95), with the comments made consistent. (c) Another number, with its derivation.

**Lead's disposition (argument, not evidence): (b).** Reasons offered: the reserve the module already documents is 5 s and was sized against a measured query cost of 0.70–1.45 s; deriving the attestation's bound FROM the teardown's budget makes the two sum to the gap by construction instead of by coincidence; and of the two fail-closed outcomes, losing one envelope's claim-bearing state is strictly cheaper than refusing a ~3 h measurement window.

**The pins option (b) moves, enumerated at `489b0953`** (all inside `tests/test_quiet_predicate_campaign.py`, one test, `test_the_bound_is_the_registrations_gap_and_a_timeout_keeps_the_schedule`, lines 1257–1278): line 1259 `attestation_timeout_s(PROTOCOL) == 15`; line 1262 `attestation_timeout_s({**PROTOCOL, 'slot_pitch_s': 700}) == 95`; line 1267's harness argument `attest_burn=15`; line 1269 `[kwargs["timeout"] …] == [15] * 12`; line 1274 `[row["network_time_attestation_wall_s"] …] == [15] * 12`. Line 1260's `SCALED` assertion pins the floor and is unchanged by (b). The lead's dictation says "the two test pins"; the count above is what the file holds.

**Deliver.** The ruled bound (exact expression), the pins to move, and whether the `CLEANUP_BUDGET_RESERVE_S` comment must be rewritten under whichever option you rule.

## Q4 — Ratify seat deviation D1: the two window keys

**Facts.** A269 ruling 10 Q4(i) (exhibit B4) rules `window_epoch_s` to be the epoch/monotonic union window — `start = min(sampling_started.epoch_s, sampling_stopped.epoch_s − span) − 1`, `end = max(…) + 1` — and orders `"window_method": "epoch_monotonic_union_v1"` recorded beside it. Brief 06 item 14 (exhibit B6) reads "`attestation.window_epoch_s` records the whole-second values actually passed to `--start/--end` alongside the float union window (`window_argv_epoch_s`)", which assigns the two meanings the other way round. The seat implemented the ruling's meaning: `window_epoch_s` unchanged, and a NEW key `window_argv_epoch_s` carrying the whole-second epochs parsed back out of the argv strings (exhibit A, `timed_log_window_epoch_s` and `attest_network_time`). Exhibit D1 holds the deviation correct and notes two ruled regressions pin `window_epoch_s` to `attestation_window(stamps)`; exhibit D2 §N4 calls it "a rename of a ruled field [that] needs ratification, not a report footnote". Exhibit D1 §N3 separately observes that `window_argv_epoch_s` is set only on the success path while `window_epoch_s` is initialised to `None` in the record skeleton, so a blocked or window-unavailable record lacks the key instead of carrying `null`.

**Lead's disposition (argument, not evidence): AFFIRM as implemented**, and rule additionally that `window_argv_epoch_s` is initialised to `null` beside `window_epoch_s` in the record skeleton, so every attestation record carries both keys on every path.

**Deliver.** AFFIRM or amend, with exact text for any amendment; and AFFIRM or reject the null-initialisation.

## Q5 — Fix round 2 contents: the remaining findings from the two delta lenses

**Facts and the lead's proposed disposition for each (argument, not evidence — the lead adopts all as dictated items).**

1. **Execution lens S1.** `record_attestation`'s first `except (OSError, ValueError)` (exhibit A, `quiet_predicate_campaign.py:688-692`) returns `False` with `attestation["state"]` untouched, so an envelope whose `session.json` could not be read is journalled `authenticated` — the one claim-bearing state — on zero evidence. Lead: set `asserted` with reason `session record unreadable` in that branch too.
2. **Execution lens S2, identical to contract lens N5.** When `os.replace` fails, the temporary file survives (exhibit A, `:700-713`), and it is a *complete* session record carrying the pre-downgrade `authenticated` state. The existing assertion that no `.tmp` survives sits on the read-only-directory test, where no temporary can ever be created, so it is vacuous. Lead: `temporary.unlink(missing_ok=True)` in the `except`, and move the `.tmp` assertion onto the `os.replace` variant.
3. **Contract lens N1.** The item-3 truth table's third axis is the cause of refusal, not the final record's `cleanup_proven` flag, which the harness asserts `True` on every row; so deleting `and cleanup["cleanup_proven"]` from the return-code expression (exhibit A, `execute` return-code tail) has no row that catches it. Lead: add `cleanup_proven` as a real axis.
4. **Contract lens N4.** A receipt write that fails inside the restore is swallowed by `except Exception: pass` (exhibit A, `restore_network_time:411-412`) while the outcome document still says `network_time_restored: true`. Lead: print a reason line with `flush=True`.
5. **Contract lens N3, identical to execution lens N3.** `timed_log_window_epoch_s` parses a naive local timestamp, which resolves an ambiguous daylight-saving fall-back hour to its first occurrence. Lead: one docstring sentence; no code change.
6. **Execution lens N1.** `attest_network_time`'s `timeout` parameter defaults to the 5 s floor (exhibit A, `:604`), so a future caller that forgets it gets a silent bound. Lead: make it keyword-only with no default.
7. **Contract lens N2 and execution lens N2** (the timeout reason literal carrying the number of seconds; the item-1 test being half source-grep and half stub). Lead: accepted as-is, no change.

**Deliver.** AFFIRM, amend or reject each of the seven; and name any regression you require beyond those proposed below.

## Q6 — Packet hygiene for the already-sealed A267 gate

**Facts.** Ruling 14 R3 (exhibit B2) requires, as in-repo regression 8, replaying all twelve archived envelopes and asserting exact record equality, and requires regression 12 to find ten marker matches over exhibit D. Exhibit D — the fixture — was captured in `--style compact` while the ruled argv is `--style syslog`. Exhibit C3 shows the two styles agree on everything the regressions read: both bodies are 191 lines and both yield `timed_log_marker_lines` = 30; only the first line differs.

**Lead's disposition (argument, not evidence).** The twelve-envelope regression corpus stands on that parity, and gains the live syslog capture as a production-format twin under Q2, so that a future style mismatch is caught by a fixture rather than by a lens.

**Deliver.** AFFIRM, or state the correction required — including whether any already-sealed A267 finding must be re-opened because its evidence was captured in the wrong style.

## Q7 — Post-merge: may the next pilot night be armed

**Facts.** A269 ruling 10 Q3 (exhibit B4) replaced ruling 14 R6's precondition. Its replacement text is quoted in full in exhibit B4; it requires, in order, that lane A269 has landed cure Q1(c) under registration v2; that **a daytime bench replay — real `execute` and real collector with an injected recorder replaying an archived plist, no sudo, no measurement, never labelled R6 evidence — shows chain-level `start_drift_s` ≤ 0.5 s on every slot**; and only then that the re-run night is itself the live check, refusing at the first envelope whose chain-level start drift exceeds 2 s. A269 ruling 10 Q2 (exhibit B3b) additionally states that both A267 Part 3 and A269 must be merged before any arm, and that a pinned exclusion list omitting reasons the code emits "is an incomplete registration and must never exist on main".

**Lead's disposition (argument, not evidence): yes** — NIGHT_HANDBACK (notify, then arm) may proceed for the next pilot night under registration v2 immediately after the transaction merges and the tracked entry point's dry check passes, with the standard no-objection window.

**The gap the assembler flags.** The lead's formulation names "the tracked entry point's dry check". The ruled text names a specific daytime bench replay with a ≤ 0.5 s per-slot bar. Whether the entry point's dry check is that replay is not established by any evidence in this packet.

**Deliver.** AFFIRM, or name the extra precondition — in particular, whether the ≤ 0.5 s bench replay must be executed and recorded by name before the arm, and what artifact evidences it.

## Regressions

Each regression below names the counterfactual that must FAIL at `489b0953` and the production call site it exercises. The judge adopts, amends or replaces them.

**For Q2 (header guard).**
- R2.1 — `timed_log_has_header` accepts the live syslog capture's body. Counterfactual: at `489b0953` it returns `False` (exhibit C3). Call site: `attest_network_time`'s header branch, which sets `asserted` / `timed log query returned no header` (exhibit A).
- R2.2 — the zero-match live capture (header only, no entries) yields `authenticated` with `matched_lines` 0 end-to-end. Counterfactual: at `489b0953` it yields `asserted` (exhibit C3). Call site: `attest_network_time` → `record_attestation` → `execute`'s journal append.
- R2.3 — the guard REJECTS the compact-style header line. Counterfactual: at `489b0953` it returns `True` (exhibit C3b), so the assertion fails. This is the defect-shaped kill: it pins that the constant is the *ruled argv's* header, not any header.
- R2.4 — the empty body, an HTML error page, a bare newline and a headerless entry line are all rejected under the new constant. Counterfactual: deleting the guard's call from `attest_network_time` turns these rows red.
- R2.5 — the twelve ruling-14-R3 envelope regressions and regression 12's marker count run over the syslog fixture as well as the compact one, with identical outcomes. Counterfactual: substituting the syslog body at `489b0953` turns every envelope `asserted`.

**For Q3 (attestation bound).**
- R3.1 — `attestation_timeout_s(PROTOCOL) == 5` under registration v2. Counterfactual: 15 at `489b0953` (exhibit A). Call site: `execute` passes `timeout=attestation_timeout_s(protocol)` to `attest_network_time`.
- R3.2 — `attestation_timeout_s({**PROTOCOL, 'slot_pitch_s': 700}) == 5`. Counterfactual: 95 at `489b0953`.
- R3.3 — the invariant `attestation_timeout_s(p) + cleanup_budget_s(p) <= p["slot_pitch_s"] − p["envelope_s"]` holds for v2, for the scaled protocol and for a 700 s pitch. Counterfactual: 15 + 15 = 30 > 20 at `489b0953`. This is the defect-shaped regression — it is the two budgets claiming the same seconds, stated as an executable assertion.
- R3.4 — a night in which every query burns its whole bound still spawns all twelve slots at `600 + 620·i` with `|start_drift_s| ≤ 0.02`, and journals the new bound on all twelve entries. Counterfactual: the same test with the 15 s pins at `489b0953`.

**For Q5 (fix-round-2 items).**
- R5.1 (item 1) — an envelope whose `session.json` is absent or malformed is journalled `asserted` with reason `session record unreadable`. Counterfactual: at `489b0953` the state stays `authenticated` (exhibit A, `:691-692`; executed in exhibit D2 §S1). Call site: `record_attestation`, called from `execute`'s inter-slot section.
- R5.2 (item 2) — with `os.replace` patched to raise, no `*.tmp` survives in the envelope directory and the state is `asserted`. Counterfactual: at `489b0953` a complete `session.json.tmp` carrying `authenticated` survives (exhibit D2 §S2). The assertion must sit on the `os.replace` variant, not on the read-only-directory variant where no temporary can exist.
- R5.3 (item 3) — the truth table gains a row with a complete outcome and `cleanup_proven` `False`, returning 2. Counterfactual: deleting `and cleanup["cleanup_proven"]` from `execute`'s return-code expression leaves the table at `489b0953` green.
- R5.4 (item 4) — a restore whose receipt write raises prints a reason line on stdout. Counterfactual: at `489b0953` `except Exception: pass` prints nothing.
- R5.5 (item 6) — `attest_network_time(out)` called without a timeout raises `TypeError`. Counterfactual: at `489b0953` it silently binds the 5 s floor.
- Item 5 (the daylight-saving docstring) and item 7 carry no regression by the lead's proposal; the judge may require one.

## Constraints on the judge

Read-only. Nothing is armed. Do NOT modify any file, and do NOT run `systemsetup`, `sudo`, `powermetrics`, or the real `/usr/bin/log` in any form. No suite-wide runs; at most ONE run of the single module `tests.test_quiet_predicate_campaign`. Probes allowed: `git -C <worktree> show <rev>:<path>`, `git diff`, `git log`, `grep`/`rg`, `sed -n`, `shasum`, and `python3` over the two saved log captures and the fixture. Re-running the three generators in this directory is allowed and encouraged.

Your worktree is a fresh detached checkout of the bookkeeping head, so: every path in this packet is relative to the repository root, and every revision is named explicitly. The feature head `489b0953` and the scratch head `e52c7fbc` are NOT checked out in your worktree; read them with `git show <rev>:<path>`, which works because the objects are in the shared repository. The fixture `tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt` exists only at `489b0953`. The two saved log captures are tracked at the bookkeeping head and exist on disk in your worktree.

Revisions: main `c8812172`; feature branch base `447fd6bf`; feature head `489b0953` (`feat/2026-09-22-a267-clock-anchor-v3_1`); fix-round head before the docstring rewrap `62412ee6`; r7 scratch head `e52c7fbc` (`scratch/r7-dryrun-e4b4ead6`).

Exhibits D1, D2 and D3 are LABELLED ARGUMENT: two review lenses and one implementation seat's self-report. They are included complete and unedited so their reasoning can be checked, not adopted. The lead's dispositions throughout are argument, not evidence.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
cc052495ce3b7a3e884affb353252aad840f247f9c8a2ee1477be60d31c692de  exhibit-A-code-at-revisions.md
d9f5a21b746c749c551f4c3ea9b813141e687f6ca3d151c544c9d74f17985ddf  exhibit-A-generator.py
3be21d9356e6e9010fc54755803245e6b05b262588cc7b2b8330cf74094214c1  exhibit-B-authorities.md
d24548ea838e1b072f61e41a606c0a215fac9bb116966b8e7fdfea3f2724273c  exhibit-B-generator.py
2a9dbfdf7804888d0ca671186c10995a4cdb2acf4ea533c80976ff2611d4dae5  exhibit-C-executed-evidence.md
894cf3141f1cbdb625b1d07fb79f413586aaa89ab9c8d1476f83a3c17e9c841a  exhibit-C-generator.py
9a164e9354421a101bc6a46b067fa24380a8c35e3430276eae7a300af410fc75  exhibit-D1-contract-lens-fable.md
fb7021ae481c25787d26c62fcaf86be42648bd1a4c16ca9c65776aee68a55195  exhibit-D2-execution-lens-opus.md
8dd71162fb41a81f12d7e74bfd1c782301ea1317c7863d9121efb41e4eb27cc0  exhibit-D3-seat-report.md
```
