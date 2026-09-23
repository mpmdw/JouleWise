# 03 — Opus delta lens: ruling 21 C3 driver amendment

Lens: Opus 5, read-only, 2026-09-23 PDT. Worktree `JouleWise-wt-c3-a022aecc`,
head `b647fda3` (2 commits on `91f80870`); tree clean but for this file. No
bench, sudo, launchctl, Codex or subagents. Authority: cold ruling 21,
`docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md`
(§Q1, §Q2 block, §Q3 C3).

## Contract ledger — clause by clause

Unqualified `:NNN` paths below are `scripts/bench_replay_start_drift.py`.

| Ruled clause | Implemented at | Verdict |
| --- | --- | --- |
| (1) 12 of 12 slots at the merged head | `:503,506,538` (`len(rows) == protocol["envelopes"]`, `missing`); head/clean-tree pinned out of band `:153-160`, printed `:650-651` | PASS |
| (2) `collector_exit == 0`, `cleanup_proven`, attestation ∈ {authenticated, slew_attested} | `ADMISSIBLE_SLOT` `:349`, `BENCH_ATTESTATION_STATES` `:374`, applied `:512-520` | PASS |
| (3) every CHAIN-level `start_drift_s` ≤ 0.5 s, `max ≤ 0.5 s` stated | `START_DRIFT_BAR_S = 0.5` `:114`; `over` `:507-508` strict `>`, so `== 0.5` passes; max stated on PASS `:570-571` and on FAIL `:600-604,619-621` | PASS |
| (4) fidelity table + tally; one ADMITTING slot voids; refusing admissible | `fidelity()` `:407-442`; admitting also recorded as a defect `:530-536`; leading FAIL clause `:606-611`; rendered `:698-716` | PASS |
| (5) floor of ≥1 slot `bounded` with `interior_complete_support` | `floor_slots` `:524-526`, `floor_met` `:528`, FAIL lead `:612-615`, rendered `:687-689` | PASS |
| (6) max `tail_s` + 2.3 s < the 20 s gap, with figures | `tail_budget()` `:446-472`; gap **derived** `pitch − envelope` `:458` (620−600, not a literal); `WORST_SKIPPED_TAIL_S = 2.3` `:385`; strict `<` `:462` | PASS |
| Session figure reported, assessed only vs the night's 2 s rule | `SESSION_BAR_S = 2.0` `:125`; `session_over` `:509-510`; reported `:652-654` | PASS (see MATERIAL 1) |
| ESCALATE preserved for session over the rule | `:552`; statement `:580-584`; rc 3 `:909` | PASS — executed below |
| Smoke exemptions exactly (4) and (5) | `:526-528`; (1)(2)(3)(6) and the attestation states still bind — executed, `tests/test_bench_replay_start_drift.py:282-327` | PASS |
| `RULED_ADMISSIBILITY_TEXT` byte-faithful to the ruling's block | `:392-405` | PASS — byte-equal (979 chars) once the closing sentence is removed; executed below |
| Old X1 (0.5 s session bar) survives? | `0.5` in session context only in comments `:117`, the quoted rule `:403`, rendered prose `:732`, and one explicit-argument counterfactual `tests/test_bench_replay_start_drift.py:279` | NO — struck |
| Old X2 (`bounded` on every slot) survives? | `ADMISSIBLE_SLOT` `:349` holds only the two ruled fields | NO — struck |
| `ARCHIVED_V31_BOUNDED` = F9 constant | `:377`; A269 record 01 step 10 reads "bounded {02, 05, 06, 08, 09, 11, 12}" — I opened that line | PASS; a module constant, never read from the run it judges |
| 2.3 s worst skipped tail = ruled figure | `:385`; ruling §Q4/F8 `end-postparse` max 2.291 s, rounded up | PASS |

**Omission of the ruling's closing sentence** ("Driver output: status FAIL,
statement quoted verbatim above, retained as issued") — the seat's call is
RIGHT: that sentence names artifact 24's own pre-amendment output, and stamping
it on every future artifact would assert `status FAIL` on a PASS run. Its
substance is discharged by `markdown():664` printing the driver's own `status`
and `statement` verbatim, and the omission is disclosed at
`.../a022aecc/02-c3-replay-driver-amendment-seat-report.md:228-235`. It is
still a deviation from a block the ruling called "exact text", so it belongs in
the PR body too (MATERIAL 2).

## Execution ledger

| Command | Result |
| --- | --- |
| `python3 -B -m unittest tests.test_bench_replay_start_drift tests.test_quiet_predicate_campaign` (with `PYTHONDONTWRITEBYTECODE=1`) | **135 tests, OK** |
| `verdict()` re-run on `.../59857fe5/24-bench-replay.json` (rows + protocol as tracked) | **PASS**. Statement byte-identical to the seat report `:105`: chain max 0.352 s ≤ 0.5 s over 12/12; 10/12 match, admitting 0, refusing 2; floor `[2, 5, 6, 11, 12]`; 8.410 + 2.3 = 10.710 s < 20 s; session max 0.608 s ≤ 2.0 s. Every figure equals ruling §Q4's own. |
| Byte-compare `RULED_ADMISSIBILITY_TEXT` vs the ruling's `> Admissibility…` line, closing sentence stripped | **EQUAL** (979 chars both sides) |
| CF1 — slot 1 (archive unresolved) forced `bounded` | **FAIL**, leads "anchor fidelity VOIDS the run: slots [1] … ADMITTING-direction mismatch"; names the slot; tally 9/12 |
| CF2 — every slot unresolved, `interior_complete_support` False | **FAIL**, leads "no slot is 'bounded' with complete interior support…", and still states the chain figures are under the bar |
| CF3 — slot 1 session 2.1 s | **ESCALATE**, "a split verdict is ESCALATED to the magistrate, never passed"; rc map `:909` gives 3 |
| CF4 (as the brief specified it) — slot 8 `bounded` + slot 2 unresolved | **PASS**, correctly. The brief's premise is wrong: slot 8 IS archived-bounded, so slot 8 going `bounded` is a *match*, not admitting. Not a driver defect. |
| CF4b (the intended test, reconstructed) — slot 1 `bounded` (admitting) **and** slot 2 unresolved (refusing) | **FAIL** — "anchor fidelity VOIDS the run: slots [1] …; 8/12 match; admitting-direction 1; refusing-direction 3". One admitting slot voids even beside a refusing one. Kill confirmed. |
| `markdown()` once on the JSON | Fidelity table (12 rows: `anchor_detail`, archived class, direction), "Tally: 10/12 match; admitting-direction 0; refusing-direction 2.", the tail line with all three figures, the floor line, the ruled block as a blockquote, and `refusing-direction slots [8, 9] (admissible, reported)` stated, not buried. |

## Findings

**BLOCKER:** none.

**MATERIAL 1 — the 2 s session rule is a hardcoded constant, not the
registration field it was made into.** `:125` pins `SESSION_BAR_S = 2.0`, while
the protocol dict `verdict()` already receives carries `start_drift_abort_s: 2`
(copied into the report at `:846`; A269 ruling 10 A2 made it a registration
field precisely so it is not restated). The two agree today, so there is no
behavioural defect — but a registration that later moves the abort threshold
leaves the bench silently judging against a stale 2.0. One-line cure: a
`protocol.get("start_drift_abort_s", SESSION_BAR_S)` default in the signature
at `:475-477`.

**MATERIAL 2 — the ruled "exact text" is quoted with a deliberate omission and
nothing mechanically pins it.** `RULED_ADMISSIBILITY_TEXT` (`:392-405`) is
byte-faithful today — I executed the comparison — but the only test over it
(`tests/test_bench_replay_start_drift.py:329-352`) asserts one substring,
`"{02,05,06,08,09,11,12}"`. A later edit to that string drifts the driver's
stamped rule away from the ruling with the suite still green. Cure: assert the
constant against the ruling file's own `> Admissibility` line with the closing
sentence stripped — the comparison I ran, ~6 lines — which also makes the
omission self-documenting.

**NIT 1 — `SMOKE_EXEMPT_FIELDS` (`:350`) no longer gates anything**: it is
referenced only by the report key at `:634`, while the exemption is three
`if smoke` branches at `:526-528`. Adding a field to the tuple would do
nothing. Say so, or derive the branches from it.

**NIT 2 — `refusing` is emptied under `--smoke`** (`:527`), though it is a
report line, not a rule; `fidelity_applied: False` already marks it non-binding.

**NIT 3 — comment/code mismatch:**
`tests/test_bench_replay_start_drift.py:311-313` says "under the FULL protocol"
but passes `SMOKE_PROTOCOL` with `smoke=False`. Assertion right, sentence wrong.

**NIT 4 (pre-existing) — `--expect-sha` is optional** (`:159`): clause (1)'s
"at the merged head" binds only when the operator supplies it.

## Same-signature statement

**No defect class from the seat's earlier rounds survives.** X1 (0.5 s session
bar) and X2 (`bounded` + `interior_complete_support` on EVERY slot) are both
gone from executable code — `:125` is 2.0, `:349` holds only the two ruled
fields — surviving only as named history in comments plus one
explicit-argument counterfactual test. Every earlier lens cure still executes
and is covered by a test I ran: the third status ESCALATE (17b B1) at `:552`;
`session_bar_exceeded` independent of `status` (delta lens SHOULD-FIX 2) at
`:557`; leading-defect FAIL statement and `DEFECT_SLOT_CLAUSE_CAP` (delta lens
NIT 1) at `:586-598`; the `slew_attested`/`asserted` split (17b S3) at `:374`.
What X2 was for — proof the finalisation tail ran at this head — is now carried
by rules (4) and (5), and CF2 shows a tail that never ran anywhere still fails.
The two attempts this lane has failed on (feeder causality, then the
admissibility convention) have distinct signatures; no structural-failure
trigger is engaged.

## Verdict

**MERGEABLE.** The six ruled clauses are implemented exactly — no more, no
less: (1)–(3) unchanged in substance, (4) and (5) added as run-level rules in
place of the struck per-slot X2, (6) added with the gap *derived* from the
protocol rather than hardcoded, and the session figure demoted to a reported
quantity assessed against the night's own 2 s rule. Condition C3's required
demonstration is real and reproducible: I re-ran `verdict()` on
`24-bench-replay.json` myself and got PASS with a statement byte-identical to
the seat's, every figure matching ruling §Q4's independently-computed ones, and
135 tests green. The three kill counterfactuals the seat claimed all fire, and
the one it did not try — an admitting slot beside a refusing one — FAILs as the
ruling requires (the brief's own version of it was mis-specified: slot 8 is
archived-bounded and cannot be the admitting side). The verbatim-text omission
is the right call, correctly reasoned and disclosed. Nothing found is
merge-blocking; MATERIAL 1 and 2 are two short hardening lines to land in this
PR if cheap or as a named follow-up if not, and MATERIAL 2's omission must
appear in the PR body, not only in the seat report.
