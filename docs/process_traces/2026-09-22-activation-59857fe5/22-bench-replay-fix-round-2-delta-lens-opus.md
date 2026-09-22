# BENCH-REPLAY-START-DRIFT-01 fix round 2 — delta re-audit (execution + contract, one lens)

Head `58a2e42b`, worktree `/Users/edr/code/JouleWise-wt-a267-review3`, tree clean before
and after. Four-module suite (`tests.test_uncertainty_evidence
tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign
tests.test_run_night`): **Ran 493 … OK** — see NIT 4 for a flake.

## Kill ledger (all executed at `58a2e42b`; each mutation reverted with `git checkout -- .`)

| # | mutation | test killed | message |
|---|---|---|---|
| 1 | `quiet_predicate_campaign.py:1366` → unconditional `REPLAY_REFUSAL_REASON` | `test_D1` | `'start_drift_abort: envelope 2' not found in 'replay_recorder'` |
| 2 | `:79-80` duplicate-marker guard removed | `test_D1`, **`test_R5`** | `'replay_recorder; replay_recorder' != 'replay_recorder'` |
| 3 | `bench_replay_start_drift.py:381` → `= escalate` | `test_D2` | `False is not true` |
| 4 | `:414-416` session clause dropped | `test_D2` | `'the session-level bar is exceeded too (max 0.900 s > 0.5 s on slots [4])' not found` |
| 5 | `:452-453` markdown line dropped | `test_D2` | `'Session bar exceeded (true whatever the status): True' not found` |
| 6 | `:404` `if False:` (drift-first branch forced) | `test_D3` | `False is not true : max <= 0.5 s NOT shown: over=[] …` |
| 7 | `:401` `if False:` (cap removed) | `test_D3`, `test_X2` | `'… and 21 more' not found`, `'… and 1 more' not found` |
| 8 | `ADMISSIBLE_SLOT` loses `interior_complete_support` | `test_X2`, `test_D3` | `Lists differ: … != … (8, 'interior_complete_support', False)` |

Command for each: `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest
tests.test_quiet_predicate_campaign.BenchReplayFailClosedTests` (Ran 17; OK when restored).
The seat's three kills reproduce; kills 2, 5 and 8 are mine.

## Required verifications

**(2) Both refusal sites vs. the environment site alone.** I spied on
`replay_refusal_error` across all 128 tests of the campaign module (`/tmp/a267r3/allsites.py`,
128 run, ok=True). Reaching lines, by test: `test_R5_…refuses_the_whole_night_at_the_summary`
→ **[1355, 1366]** (the ordinary bench night, both sites, args `None` then `'replay_recorder'`,
marker count 1); `test_L2_…wrote_no_session_still_refuses` → **[1366]** and
`test_D1` → **[1366]** with the abort text (environment site alone);
`test_R5_…no_recorder_kind_at_all` and `test_X3` → **[1355]**. Both dictated nights exist
as executed regressions, and kill 2 shows R5 is the one that pins the guard end-to-end.

**(3) Synthetic rows** (`/tmp/a267r3/synth.py`, independent of the test file, 12 admissible
rows): FAIL (`collector_exit=1` on slot 7) + session 0.9 on slot 4 → `session_bar_exceeded
True`, `escalate… False`, statement ends `; the session-level bar is exceeded too (max
0.900 s > 0.5 s on slots [4])`. Session-over alone → `ESCALATE`, both flags True. Both under
→ `PASS`, both False. Conforms.

**(4) Production identity for a real night.** Only `quiet_predicate_campaign.py:1355/:1366`
changed behaviourally; the *guards* on both are untouched by the delta. `:1355` needs
`report["status"] == REPLAY_NEVER_EVIDENCE`, set only when `replay_recorders` is non-empty
(`:1105-1121`, a `session.json` whose `power.recorder_kind` is not production); `:1366` needs
`REPLAY_ENV`. The 128-test spy above shows no real-night test reaches either. `ReplayRecorder`
is instantiated only under `REPLAY_ENV` (`sample_quiet_predicate_evidence.py:1681`), and
`bench_replay_start_drift.py` is not on the night path. **But the premise is incomplete:**
`MANIFEST_PATHS` (`campaign.py:82-85`) covers both `joulewise/quiet_predicate_campaign.py`
*and* `scripts/sample_quiet_predicate_evidence.py` (`HARNESS_PATHS[0]`), and the manifest
digests them at `:147`. So `a8656d4b` **and the docstring-only `58a2e42b`** each change the
sha256 a real night records; the two bench-script commits are fully inert. D-138 accounting
item, not a defect.

**(5) Tests passing for the wrong reason.** `test_X2`'s amendment moved only statement
fragments; kill 8 proves its untouched `slot_defects` assertion still kills an admissibility
regression. `test_D2`/`test_D3` counterfactuals are executed, not asserted. No vacuous pass
found.

## Findings

**SHOULD-FIX 1 — `bench_replay_start_drift.py:401-403`: the cap is keyed on slots, applied to
clauses, and delivers neither property on an ordinary shape.** `len(defect_slots) >
DEFECT_SLOT_CLAUSE_CAP` thresholds on *distinct slots* while the truncation takes
`clauses[:3]`. Executed (`/tmp/a267r3/synth.py`): three slots each failing all five
admissibility checks → 15 clauses, **971-character statement, uncapped** — longer than the
24-defect case the item was written for and than the 600 `test_D3` asserts. Four such slots →
capped, and all three surviving clauses name **slot 1**, so a `4/12 slots NOT admissible`
headline spells out one slot, defeating the stated reason for the cap ("the first defective
slots are what a reader acts on", `:316-319`). A feeder crash hitting the first slots is that
shape. Cure: take clauses for the first `CAP` *distinct* slots (or threshold on
`len(clauses)`); regression at three-slots-by-five-defects.

**NIT 1 — `quiet_predicate_campaign.py:79`: the guard is substring containment.** Executed:
`replay_refusal_error("pilot summary failed: 'replay_recorder_envelopes'")` returns the text
**without** the marker, because the key names `pilot_summary` itself writes
(`replay_recorder_envelopes`, `replay_recorder_reason`) contain `replay_recorder`, and the
`except` at `:1357` surfaces a `KeyError` verbatim. Fail-closed is unaffected
(`evidence_outcome.recorder_kind` is the run-side marker), only the text. Cure: `error ==
REPLAY_REFUSAL_REASON or error.endswith("; " + REPLAY_REFUSAL_REASON)`.

**NIT 2 — the seat's Observation (`:1357`) is real and matters little.** Reproduced
(`/tmp/a267r3/obs2.py`: pitch-603 abort night, `pilot_summary` writes then raises `KeyError`)
→ `error = "pilot summary failed: 'busy_core_seconds'; replay_recorder"`, abort text gone,
`envelope_journal[-1]["abort"] == "start_drift_abort"`. For the bench's diagnostic path it is
minor: the slot's `abort` key reaches the bench report at `:271` and the crash named in
`outcome_error` (`:594`) is the more proximate failure. Same defect class as item 1; a
one-line combine closes it.

**NIT 3 — `quiet_predicate_campaign.py:81-82`: no blank line between `replay_refusal_error`
and `HARNESS_PATHS` (E305).** Cosmetic only — no linter gates CI (`pyproject.toml` has no
flake8/ruff config; `.github/workflows` has no lint job).

**NIT 4 — one full-suite run in four FAILED (failures=1); the name was lost.** Runs 2–4 were
`Ran 493 … OK` (254 s, 251 s). The seat's "no wall-clock race fired" implies a known
wall-clock-sensitive test; I could not reproduce it in three repeats. Not attributable to the
delta — the bench-replay class ran clean 17/17 on ~12 invocations — but worth one more full
run before the merge wave.

**NIT 5 — `SCHEMA` stays `joulewise.bench_replay_start_drift.v1` while the verdict gained
`session_bar_exceeded`.** Additive; `markdown`'s `v.get(…, bool(v['session_slots_over_bar']))`
(`:453`) reads old reports; no doc pins the field list (grep of non-legacy `docs/` for
`escalate_chain_pass_session_fail` is empty). Recorded, not a defect.

## Verdict

**0 BLOCKER / 1 SHOULD-FIX / 5 NIT.** All four dictated items are implemented and pinned by
regressions that kill their counterfactuals; the three deviations are sound (the duplicate
guard is *required* by R5, executed; the `test_X2` edit moved cosmetic fragments only;
keeping `escalate_chain_pass_session_fail == (status == "ESCALATE")` was the brief's own
first option and the markdown now states that meaning on its face). Nothing blocks the merge
except the magistrate's own view of SHOULD-FIX 1.
