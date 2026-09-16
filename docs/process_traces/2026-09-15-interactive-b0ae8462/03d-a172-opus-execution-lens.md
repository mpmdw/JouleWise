# a172-opus-exec — EXECUTION-LENS refutation of A172 ARM-RETRY-CLASS-01 (head 5ece8fb0)

Read-only on `/Users/edr/code/JouleWise-wt-a172`; every mutation ran in `…/seats/a172-opus-copy`
(restored: `sha256 8fa80203…` identical to the worktree, `git status` clean).

## Findings

**Blockers: none.** I drove `retry_allowed` through all ten required scenarios, 1000 fuzz cases and
11 mutations and could not produce a false ALLOW, an unhandled exception, or a denial that fails
Ed's no-artificial-scarcity directive.

**Should-fix 1 — `latest_abort_epoch_s` demands exact float equality, and the runbook does not say so.**
`joulewise/arm_retry.py:163` compares `notice["latest_abort_epoch_s"] != previous_abort` by value.
`docs/phase_2/derivation_night_runbook.md:1648` only tells the operator it is "the newest abort time".
Executed: abort at `1789466359.6`; an int-truncated (`1789466359`) or rounded (`1789466360`)
transcription both return `notice_abort_mismatch`. The magistrate records the abort in the *prior*
attempt's `outcome.json` and re-types it into `notice.json` a cycle later, so this is a live
transcription trap, not a theoretical one. Cost is bounded (re-run step 6 in place after correcting
the field — no new email, no new ordinal), so it is not a window-scarcity defect. Cure: one clause in
step 5 — "byte-equal to `attempts[-1].abort_epoch_s`, copied, never re-derived".

**Nit 1 — misleading reason ordering.** `arm_retry.py:160` (`notice_reused`) runs before the notice's
own well-formedness check at `:185`. An attempt that never sent mail (`message_id: ""`) plus a notice
with `message_id: ""` denies as `notice_reused` when `notice_not_current` is the true fault. Fails
closed; only the routing label is wrong.

**Nit 2 — a dominated bound.** `arm_retry.py:170`'s `now - authored <= max_age` upper half is
unreachable as the binding reason: `now < install_close = t0 - 4500` and `t0 <= authored + max_age`
together force `now - authored < max_age - 4500`. Executed sweep: ages M−4500…M all return
`install_closed`; only M+1 (where `t0 - authored` also fails) returns `plan_age`. Harmless fail-closed
redundancy, and the seat's own test documents the dominance honestly.

**Nit 3 — D-180's span ceiling is ~24 h, not ~48 h, when the first attempt sits near local midnight.**
With live `INSTALL_SPANS = (("00:00","24:00"),)`, origin 23:30 gives a next-span close only 24.5 h
later. This is D-180's shape retained verbatim by R1, not something A172 introduced, and
`install_close` (t0 − 1 h 25 m) and `PLAN_MAX_AGE_S` (36 h) bind long before it in every realistic
night. Midnight crossing itself is handled correctly — the caller resolves spans from the *origin*
attempt's day (runbook:1782–1786), so a 00:05 retry after a 23:30 abort is ALLOWED.

## 2. Denial-reason trace (all 19 strings; every one traces to a named bound)

`install_close_epoch` → `install_closed`. `PLAN_MAX_AGE_S` → `plan_age`. 60 s spacing →
`retry_spacing`. Per-attempt notice → `notice_reused`, `notice_not_current`, `notice_binding_mismatch`,
`notice_abort_mismatch`, `notice_timing`, `candidate_changed`, `invalid_head`,
`candidate_head_mismatch`. Cold-gate cause → `cold_gate_evidence`, `cold_gate_history`. Pre-existing
§0/veto checks, not new → `owner_no`, `prerequisites_not_clear`. D-180 ceiling (R1 keeps it) →
`outside_same_or_next_span`. Fail-closed evidence integrity, imposing no wait →
`malformed_evidence`, `invalid_history`, `invalid_spans`. **No reason traces to nothing, and only
`retry_spacing` requires waiting at all.**

## Executed evidence

Scenarios (a)–(j), `python3 -B` in the copy:

```
(a) initial arm, no history                -> Decision(allowed=True,  reason='allowed')
(b) retry 61s after arm_idle_interactive   -> Decision(allowed=True,  reason='allowed')
(c) retry 59s after                        -> Decision(allowed=False, reason='retry_spacing')
(c') retry at exactly 60s                  -> Decision(allowed=True,  reason='allowed')
(d) 3rd arm after two retry-class aborts   -> Decision(allowed=True,  reason='allowed')
(e) after night_refused_not_quiet          -> Decision(allowed=False, reason='cold_gate_history')
(f) now = install_close-1 / +0 / +1        -> allowed / install_closed / install_closed
(g) t0-authored = M-1 / M / M+1            -> allowed / allowed / plan_age
(h) notice id reused from attempt 1        -> Decision(allowed=False, reason='notice_reused')
(h') whole earlier notice reused           -> Decision(allowed=False, reason='notice_not_current')
(i) owner NO present (recent or ancient)   -> Decision(allowed=False, reason='owner_no')
(j) every key dropped from plan(6)/notice(14)/attempt(8) -> False / malformed_evidence, 28/28
    plan-JSON key drops: plan_id, receipt_class, t0_epoch_s, authored_epoch_s, repo_head,
      measurement_head -> malformed_evidence; the 8 fields arm_retry never reads -> allowed
```

(j) honesty judgement: every denying field is one the headless magistrate can supply from its own
records — attempt epochs, cause, outcome, digest, message/thread ids, and the four freshly observed
booleans (`prerequisites_clear`, `veto_clear`, `blocking_causes`, `latest_no_epoch_s`) that it already
gathers from census/watchdog/Gmail. **No hidden human step.**

## 3. Fuzz

1000 perturbations (seeds 20260915 and 777777; types, signs, ordering, off-by-one epochs, container
shapes, cold-gate causes, id collisions):

```
fuzz n=500 raised=0 non-Decision=0 allowed=31 bad_allow=0   (seed 20260915)
fuzz n=500 raised=0 non-Decision=0 allowed=25 bad_allow=0   (seed 777777)
```

Never raised, always a `Decision`, never `allowed=True` with a cold-gate prior cause, a non-empty
`blocking_causes`, or a reused `message_id`. 17 of the 19 denial reasons were exercised by the fuzz
alone; `retry_spacing` and `outside_same_or_next_span` by the scenario and ceiling probes.

## 4. Tests and must-die set

`tests.test_arm_retry`: **Ran 21 tests … OK** (0.046 s). All five brief-required mutations plus six of
my own went RED, and the revert went GREEN:

```
M1 delete cold assignment (slot_refused)   FAILED (failures=2)
M2 flip arm_transport retry->cold_gate     FAILED (failures=22, errors=1)
M3 drop 60s spacing check                  FAILED (failures=1)
M4 drop plan-age check                     FAILED (failures=2)
M5 drop install_close check                FAILED (failures=5)
M6 drop notice_reused check                FAILED (failures=2)
M7 drop blocking_causes override           FAILED (failures=1)
M8 install_close off-by-one (>= -> >)      FAILED (failures=2)
M9 RETRY_INTERVAL_S 60 -> 1                FAILED (failures=2)
M10 drop cold_gate_history on prior cause  FAILED (failures=2)
M11 drop owner_no check                    FAILED (failures=4)
### REVERTED   Ran 21 tests in 0.046s   OK
```

## 5. Python 3.9

```
$ /usr/bin/python3 -B -c 'import joulewise.arm_retry …'
PY39 IMPORT OK 60 40
3.9.6 (default, May 22 2026, 11:13:45) [Clang 21.0.0 (clang-2100.1.1.101)]
```

## Verdict: **LANDABLE**

No blocker. Land as-is, or land with the one-clause runbook amendment in Should-fix 1 folded in; it
touches documentation only and needs no code change.
