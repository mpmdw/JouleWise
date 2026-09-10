# 68 — Seat S5 fix-round-2 DELTA RE-AUDIT (execution lens)

Read-only on `/Users/edr/code/JouleWise-wt-s5-chain-watch` (`8a9eec61..d899886f`); scratch copy under `/tmp/s5-delta2`, deleted at exit. Canonical, the rehearsal checkout and `/Users/edr/night-custody` were not written to; the chain was never run for real. Worktree `git status --porcelain -uall` empty at exit, chain digest unchanged (`1a80cae4…79c181`).

## Summary

1. **All four required fixes (D-1, D-2, D-7, D-8) are present and each carries a killing mutation I reproduced independently.** `python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_docs_freshness` → `Ran 61 tests … OK`, `UNITTEST_RC=0`; `zsh -n scripts/night_chains/calibration_derivation_only.zsh` → `ZSH_N_RC=0`. The seat's mutation table reproduces exactly, one-to-one, with no collateral.
2. **The D-2 readiness step is correctly shaped against the real CLI.** `recover_calibration_ledger.py` declares `--ledger`/`--head-pin` on the top-level parser (`:120-128`) and `readiness --phase {pre-reserve,pre-slot,terminal}` as a subcommand (`:165-174`); I confirmed by execution that globals *after* the subcommand are rejected (`error: unrecognized arguments: --ledger …`, rc 2). The chain spells the accepted order. Runsheet parity holds and is stricter than G2-a: the runsheet's own readiness call (`:509-512`) passes no `--ledger`/`--head-pin` at all and relies on defaults; the chain passes the night's paths explicitly.
3. **Order verified by execution, not by reading the tests:** preflight → readiness → reservation → `session_open` → `chain_start` → ONE 600 s settle → captures at 120 s cadence fills. A readiness failure gives rc 3, `calls == [the readiness call]`, `log == []`.
4. **Two surviving mutants on the step added this round** — both about the *invocation shape* of the readiness call, not its existence or its refusal semantics (nits, see D-9/D-10). The code is correct as written; what is missing is a pin against a future edit.
5. Footprint is exactly the two files; `test_docs_freshness` 31 tests rc 0, no registry/EXPECTED_IDS/docs effect. **Verdict: CLEAN** (two nits, no blocker, no should-fix).

## Mutation battery (scratch copy; restored + digest-checked after each)

| probe | mutation | result | failing test |
|---|---|---|---|
| M1 | delete `\|\| SETTLE_S < 1` (`:76`) | `Ran 30 … FAILED (failures=1)` | `test_zero_settle_or_cadence_refuses_before_readiness_or_settle (knob='SETTLE_S')` |
| M2 | delete `\|\| SLOT_CADENCE_S < 1` (`:76`) | `Ran 30 … FAILED (failures=1)` | same test, `(knob='SLOT_CADENCE_S')` |
| M3 | delete the whole readiness block (`:129-139`) | `zsh -n` rc 0; `Ran 30 … FAILED (failures=7)` | `test_unready_ledger_refuses_before_any_reservation` (the semantically right kill) + 6 order/count tests |
| M4 | delete header `:18` (HAND-WRITTEN) | `FAILED (failures=1)` | `test_chain_header_pins_its_hand_written_and_unlanded_flag_warnings` |
| M5 | delete header `:19` (`gen_g2_phase_d.py;`) | `FAILED (failures=1)` | same |
| M6 | delete header `:25` (`--slot dNN` warning) | `FAILED (failures=1)` | same |
| M7 | delete header `:26` (`choices=("pre","post")` REJECTS) | `FAILED (failures=1)` | same |
| M8 | move readiness `--ledger`/`--head-pin` **after** `readiness` | `Ran 30 … OK` — **survives** | none (real CLI would exit 2) |
| M9 | delete readiness `--ledger`/`--head-pin` entirely | `Ran 30 … OK` — **survives** | none (readiness would authenticate `DEFAULT_LEDGER_PATH`) |
| M10 | delete header `:20` / `:27` (tail sentences of the two pinned warnings) | `Ran 30 … OK` — survives | none |

Each restoration verified by `shasum -a 256` back to `1a80cae4…79c181`.

Execution-observed order (harness driver, not a test assertion): `calls[0]` `recover_calibration_ledger.py` with `--ledger --head-pin readiness --phase pre-reserve --session-id --plan`; `calls[1]` `reserve_calibration_window_bracket.py`; then two `date`s, the single `sleep 600`, then the slot loop with `sleep 120` fills. Log order `session_open` → `chain_start …settle_s=600 slot_cadence_s=600 slot_capture_budget_s=480` → `settle_complete` → `slot_start slot=d01`. `fail_readiness` run: `rc=3`, `ncalls=1`, `log=[]`.

## Delta findings

| id | severity | site | claim | reproduction |
|---|---|---|---|---|
| D-9 | nit | chain `:132-139`; tests `:366-390` | The readiness call's **global-before-subcommand ordering is unpinned**, and it is the one property that would kill the night at the real CLI. M8 keeps all 30 tests green while the real script exits 2. The seat's own report (`:205-207`) calls this ordering out as load-bearing prose ("the chain now spells that ordering correctly") without a test behind it. Cure is one static assertion in the existing header test: the source contains `--ledger …\n    --head-pin …\n    readiness` in that order. Not a defect in shipped behaviour — the code is right today. | M8 above; real-CLI rc 2 recorded |
| D-10 | nit | chain `:133-134` | The readiness call's explicit `--ledger`/`--head-pin` are unpinned (M9). Deleting them silently retargets the early-warning check at `DEFAULT_LEDGER_PATH` (`joulewise/calibration_ledger.py:95`, `<repo>/runs/calibration_observation_ledger.jsonl`) instead of the night's declared `$CALIBRATION_LEDGER` — a check that passes or fails on the wrong artifact. Note this is *stricter* than G2-a, which omits them; the chain's form is the better one and deserves the pin. Same one-assertion cure as D-9. | M9 above |
| D-11 | nit | chain `:20`, `:27` | The header test pins the first two lines of each warning; the tail sentences survive deletion (M10) — including `"no slot of this chain runs until it lands"`, arguably the operative clause of the `--slot dNN` warning. D-8's stated cure (pin the two warnings) is met to the letter; the residue is one substring-length choice. | M10 |
| D-12 | nit | `61-s5-opus-report.md:207-215` | D-7 is satisfied exactly as specified — the inline `SUPERSEDED — see Fix round 1 F-5` now heads the O-4 bullet (`:207`) and the standing-items line (`:329`), so a reader meets the marker before the stale text. The withdrawn sentence itself ("anyone running the watch from a worktree must pass `--ledger`/`--head-pin` explicitly", `:213-214`) still stands verbatim, unstruck, inside the bullet body. Harvest risk is mitigated, not removed. | `grep`/read of `:204-216`, `:326-332` |

D-3…D-6 were correctly left as integration-replay notes with no code change; I re-read `preflight_inputs` (`:108-120`) and confirm the round-2 note reframing D-3 ("presence-only, NOT an authentication") is accurate against `joulewise/calibration_ledger.py`.

## Did round 2 add a guard or step without a killing test? (the recurring class)

**No — for every guard clause.** Both positivity disjuncts (M1, M2) and the readiness step's existence and refusal semantics (M3) are individually killed, and both header pins (M4–M7) are killed. The seat's blanket claim ("every guard clause added this round carries a named killing mutation") holds under independent mutation.

The residual (D-9, D-10) is a **different, weaker class**: an added *step* whose argument shape — as opposed to its presence, position and failure behaviour — has no pin, because the test harness stubs `python3` and therefore cannot see argparse's real acceptance rules. The seat did pin part of that shape (`readiness`, `--phase pre-reserve`); it stopped short of the global-position and global-presence properties.

## Behaviour outside the two files; footprint

None. `git diff --name-status 8a9eec61..HEAD` = exactly `scripts/night_chains/calibration_derivation_only.zsh` and `tests/test_issue_calibration_acceptance_generation.py`; `scripts/issue_calibration_acceptance_generation.py` untouched this round, as the seat states. No `MAGISTRATE_WATCHDOG.md`, registry, EXPECTED_IDS or docs effect (`test_docs_freshness` 31 tests rc 0). Disclosure: my scratch copy carried the worktree's `.git` pointer file, so the single `git status` I ran inside `/tmp/s5-delta2` resolved back to the linked worktree (read-only, reported clean); every mutation was a file-level edit in `/tmp` and was never staged, committed or visible to git. Scratch removed.

## Same-signature statement vs deltas 63 and 67

Delta 63's signature was *"a load-bearing guard exists and no test kills it"* (F-2). Delta 67 found that signature **recurring once inside the round that cured it** (D-1, the `SETTLE_S ≥ 1` clause). Round 2 closes it for every instance named, verified by mutation, and does **not** reintroduce it: no guard clause added this round survives deletion. The standing escalation trigger (two consecutive rounds failing with the same signature) is therefore **NOT met** — round 2 is the round that broke the streak, not extended it. D-9/D-10 are a distinct and materially weaker class (stub-invisible invocation shape), they concern code that is correct as shipped, and the integration replay — which runs against the real CLI — is a genuine second net under them.

## Verdict

**CLEAN.**

No blocker, no should-fix. D-9 and D-10 are a single one-assertion bench fix (smaller than the contract needed to delegate it) that the lead may fold in without another seat round; D-11 and D-12 are recorded for the integration-replay note set alongside D-3…D-6.
