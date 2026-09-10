# 64 — Seat S5 fix-round-1 DELTA RE-AUDIT (execution lens)

Read-only on `/Users/edr/code/JouleWise-wt-s5-chain-watch` (`ae4a5ef9..8a9eec61`); scratch under `/tmp/s5-delta`, deleted after use. Canonical, the rehearsal checkout and `/Users/edr/night-custody` untouched; the chain was never run for real. Worktree `git status --porcelain -uall` empty at exit.

## Summary

1. **All six required fixes are present and behave as claimed.** `python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_docs_freshness` → `Ran 58 tests … OK`, `UNITTEST_RC=0`; `zsh -n scripts/night_chains/calibration_derivation_only.zsh` → `ZSH_N_RC=0`.
2. **F-2 is genuinely pinned.** In a scratch copy, deleting the post-wait guard (`:169-176`) gives `zsh -n` rc 0 and `Ran 10 tests … FAILED (failures=1)` — the single failure is `test_overrunning_capture_stops_the_next_slot_after_the_cadence_wait` (`['d01','d02'] != ['d01']`). Exactly the missing regression, no collateral.
3. **The fix round reproduced F-2's own signature once.** The `SETTLE_S >= 1` clause added for F-4 is killed by **no test**: deleting `|| SETTLE_S < 1` from `:76` leaves all 10 chain tests green (`SETTLE_GUARD_MUTANT_RC=0`). A guard added in the round whose purpose was "load-bearing guards must have a killing test."
4. **The reorder itself is correct and introduced no execution defect**, but it did not carry over G2-a's *other* pre-reservation step: `recover_calibration_ledger.py readiness --phase pre-reserve` (runsheet `:510-513`), a subcommand that exists today (`recover_calibration_ledger.py:165-174`), not S1/S2-pending.
5. Footprint is exactly the two files; nothing outside them; `test_docs_freshness` 31 tests rc 0. Verdict: **FIX** (two should-fixes, both small; no blocker).

## The six fixes, verified by execution

| fix | site (chain file:line) | evidence |
|---|---|---|
| F-1 order | `:127` `preflight_inputs` → `:129-144` reserve → `:145` `session_open` → `:146-147` `chain_start` → `:152` `settle` → `:156+` captures; order comment `:122-126` cites `SHAKEDOWN-G2-RUNSHEET.md:509-536` | matches the runsheet I read (`reserve :514-530` → `g2a_chain_start :533` → `settle :535` → `calibrate_slot :536`). Pinned: test `:373-375` asserts the reserve call is `calls[0]` and precedes the 600 s sleep in call order |
| F-2 regression | test `:434-451`, `run_chain(end=1700, capture=700)` | mutation above: uniquely killed |
| F-3 preflight | `:108-120`, `exit 66`, before reservation and settle | `test_missing_file_input_refuses_before_reservation_or_settle` ok; the stub records `date`/`sleep`/`python3`, and it asserts `calls == []` **and** `log == []` — so a refused preflight provably spends no window time and writes no ledger row |
| F-4 knobs | `:146-147` `chain_start … settle_s=$SETTLE_S slot_cadence_s=$SLOT_CADENCE_S slot_capture_budget_s=$SLOT_CAPTURE_BUDGET_S` (quoted `\`-newline elides correctly; log test pins the exact rendered string) | `test_operator_log_records_each_lifecycle_transition` ok |
| F-4 `SETTLE_S ≥ 1` | `:76` `if (( SLOT_COUNT < 1 \|\| SLOT_CADENCE_S < 1 \|\| SETTLE_S < 1 ))` | present, **unpinned** — see D-1 |
| F-6 header | `:25-27` (`--slot dNN`, `choices=("pre","post")` rejects d01..dNN) and `:18-20` (HAND-WRITTEN, not a `gen_g2_phase_d.py` region) | read; unpinned by any test (D-8) |

Single settle intact: `grep -nx settle` → one hit, `:152`; the static assertion `code.count("\nsettle\n") == 1` still holds. The mandated budget→0 mutation now kills **5** tests (was 3): the three refuter 63 named plus the new F-2 test and the log test — kill strength went up, not down.

## Delta findings

| id | severity | file:line | claim | reproduction |
|---|---|---|---|---|
| D-1 | should_fix | chain `:76`; tests `:474-480` | The `SETTLE_S < 1` clause added this round has no killing test. `test_invalid_slot_count_refuses_before_settle_or_reservation` varies only `slots`; `run_chain` has no knob passthrough for `SETTLE_S`/`SLOT_CADENCE_S`. **Same signature as F-2**, recurring inside the fix round for F-2. | scratch copy with `\|\| SETTLE_S < 1` deleted: `Ran 10 tests … OK`, `SETTLE_GUARD_MUTANT_RC=0`. Cure: add a knob kwarg to `run_chain` and drive `SETTLE_S="0"` / `SLOT_CADENCE_S="0"` asserting rc 64, `calls == []`, `log == []` |
| D-2 | should_fix | chain `:127-129` vs runsheet `:510-513` | The reorder adopted G2-a's reserve-then-settle order but not its *other* pre-reservation gate: `recover_calibration_ledger.py readiness --phase pre-reserve --session-id --plan`. That subcommand is landed today (`recover_calibration_ledger.py:165-174`, `:385-431`) and authenticates plan bytes/`plan_id`, committed-pin state and ledger readiness before a row is written. The derivation chain's authentication is `test -f` only. **Not a blocker:** the reserve script itself fails closed at the same point in the timeline (before the settle), so the loss is early-warning diagnostics, not admission safety. G2-a's *other* pre-step, `generate_g2a_probe_inputs.py check`, has no derivation analogue (no probe ladder) and must not be added — `test_chain_source_carries_no_pack_probe_or_git_step` forbids the literal string. | read both; `zsh -n` unaffected |
| D-3 | nit | chain `:113-114` | Preflight `test -f`s `$CALIBRATION_LEDGER`, which is stricter than the library: `joulewise/calibration_ledger.py:2019-2022` explicitly admits an absent ledger under `genesis_development_bootstrap` (genesis pin, no bytes). F-3 asked only for `$PLAN`/`$IDENTITY_EPOCH_JSON`/`$T1_BINDINGS_JSON`. No operational impact — the real night runs from canonical where the ledger exists (136 KB) — but the chain now refuses a state the ledger layer permits. | read |
| D-4 | nit | chain `:129-152` | Reorder consequence worth one line in the integration-replay notes: the ledger session is now **open across the 600 s settle**. A kill during the settle (driver hard deadline, laptop event) leaves an open session with zero captures needing S2 desk recovery; the old order left no ledger row at all. G2-a carries the identical exposure, so this is accepted parity, not a defect. | read |
| D-5 | nit | chain `:145-147` | No operator-log line exists before the first machine action any more. A preflight (66) or reservation failure now leaves `derivation-chain.log` absent/empty — a failed night has zero operator-log evidence it ran. Matches G2-a (`g2a_chain_start` after reserve), and the F-4 knob line has to sit after the reserve to stay in log order, so it is a genuine trade, not an oversight. | `test_missing_file_input…` asserts `log == []` — i.e. the emptiness is pinned as intended |
| D-6 | nit | chain `:82` vs `:127` | `/bin/mkdir -p` still runs before `preflight_inputs`, so an exit-66 refusal creates `$WINDOW_CUSTODY_ROOT/operator_logs` and `$RUNS_ROOT/instrument_validation`. Ledger untouched (verified), directories are gitignored; pre-existing, now reachable on the new 66 path. | read |
| D-7 | nit | `61-s5-opus-report.md:207-215` | The withdrawn O-4 sentence ("must pass `--ledger`/`--head-pin` explicitly") still stands **verbatim** in the Open-items section with no inline marker; the withdrawal lives 90 lines later at `:297-308`. F-5's stated risk was precisely that this sentence reaches the step-0 text for Ed, and a reader harvesting the open-items list still meets the wrong version. Cure: one inline `SUPERSEDED — see F-5` on the O-4 bullet. | `grep` over `:184-216` for `SUPERSEDED\|CORRECTED\|see F-5` → no match |
| D-8 | nit | chain `:18-20`, `:25-27` | Both header fixes are unpinned; `test_chain_source_carries_no_pack_probe_or_git_step` asserts only the SKELETON line. A future edit can silently drop the `--slot` warning that is the reason no slot may run yet. | read |

## Behaviour outside the two files

None. `git diff --name-status ae4a5ef9..HEAD` = exactly `scripts/night_chains/calibration_derivation_only.zsh` and `tests/test_issue_calibration_acceptance_generation.py`; `scripts/issue_calibration_acceptance_generation.py` unchanged this round, as the seat states. No registry/EXPECTED_IDS/docs-freshness effect (31 tests rc 0). No `MAGISTRATE_WATCHDOG.md` touch. Worktree clean; no untracked residue.

## Same-signature statement vs refuter 63

Refuter 63's F-2 signature is *"a load-bearing guard exists and no test kills it."* The round cured F-2 itself (verified by mutation) and **reintroduced the same signature once**, at the `SETTLE_S ≥ 1` guard it added in the same round (D-1). That is one recurrence, not two consecutive rounds failing with the same signature, so the standing escalation trigger is **not** met — but the class is live and the next round's brief should require a named killing mutation for every guard clause it adds. No other refuter-63 finding regressed; F-1's blocker is resolved at the source rather than restated as an open question, and the mandated budget-0 mutation kill grew from 3 tests to 5.

## Verdict

**FIX** — no blocker; two should-fixes before the integration replay:

1. **D-1:** pin the `SETTLE_S ≥ 1` clause (and, free of charge, `SLOT_CADENCE_S ≥ 1`) with a rc-64 / `calls == []` / `log == []` regression driven through a `run_chain` knob kwarg.
2. **D-2:** decide G2-a parity on `recover_calibration_ledger.py readiness --phase pre-reserve` — add it before the reservation, or record in the header why the derivation night's `test -f` preflight plus the reserve script's own fail-closed refusals are the whole authentication.

D-3..D-8 are nits; D-4 and D-7 are the two worth carrying into the integration-replay notes verbatim.
