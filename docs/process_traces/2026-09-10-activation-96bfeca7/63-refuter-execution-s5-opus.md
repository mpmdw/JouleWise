# 62 — Seat S5 EXECUTION-lens refuter report

Read-only on `/Users/edr/code/JouleWise-wt-s5-chain-watch` (`ae4a5ef9`); no repo writes, scratch only under `/tmp/s5-refute`. Canonical, the rehearsal checkout and `/Users/edr/night-custody` untouched; the chain was never run for real.

## Summary (5 lines)

1. Everything the seat claims to have executed reproduces: 25 tests rc 0, `zsh -n` rc 0, live `check` rc 3 naming `os_build 25F84` vs `25G83`, and the `SLOT_CAPTURE_BUDGET_S=0` mutation kills exactly the three named tests.
2. One **blocker**: the chain settles *before* the reservation, inverting the pinned G2-a chain (which reserves, then settles, with the comment "operator activity ends before the pre slot") and breaking R-c's own sentence "one 600 s settle after the last operator action". The seat's O-1 spotted the symptom but filed it as an open science question, not a spec deviation.
3. The seat's headline fix is half-pinned: removing the **post-wait** completability guard leaves all 8 chain tests green, yet I built the counterfactual (700 s capture, 1700 s window) where its absence runs d02 to 300 s past the window end. The harness already takes `capture=`; the missing regression is two lines.
4. Report item O-4's remedy is wrong: passing `--ledger/--head-pin` from a worktree does **not** work (`calibration_ledger_head_uncommitted`, rc 3) because `REPO_ROOT` is hardcoded with no `--repo-root` flag; and `runs/` is gitignored, so no clone ever has the ledger — the watch is canonical-only.
5. Footprint is exactly the three files, no untracked residue, no hidden behaviour in `check` (verified read-only). Verdict: **MERGEABLE AFTER FIXES**.

## Findings

| id | severity | file:line | claim | reproduction |
|---|---|---|---|---|
| F-1 | **blocker** | `scripts/night_chains/calibration_derivation_only.zsh:105-124` | Settle precedes the reservation; G2-a reserves then settles. d01 alone is preceded by a ledger-writing Python process instead of idle, and 600 s of window burn before any input authentication. | `sed -n '512,536p' docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (reserve 514-530 → `g2a_chain_start` 533 → `settle` 535 → capture 536) vs chain 105-124 |
| F-2 | should_fix | same, `:142-147` | The post-wait completability guard is load-bearing but **no test kills it**; the report's "two defect-shaped regressions" is one. | `/tmp/s5-refute/probe.py` and `drive.py` below; MUTANT-B rc 0 across 8 tests |
| F-3 | should_fix | same, `:36-72` | No `test -f` on `$PLAN`, `$IDENTITY_EPOCH_JSON`, `$T1_BINDINGS_JSON`; only integer knobs are validated, contradicting the chain's own comment at `:60-61`. G2-a guards these at `:392-394` before the settle. | read; `scripts/reserve_calibration_window_bracket.py:106-116` is the refusal that would fire 600 s late |
| F-4 | should_fix | same, `:54-58`, `:101,106` | `SETTLE_S`/`SLOT_CADENCE_S`/`SLOT_CAPTURE_BUDGET_S` are env-overridable and only `settle_s` reaches the operator log. `CHAIN_SHA256` in the pre-registration therefore does not pin the protocol actually run. `SETTLE_S=0` also passes the `<->` guard while `SLOT_CADENCE_S` is `≥1`-guarded. | read `:62-72`; log assertions in `test_operator_log_records_each_lifecycle_transition` |
| F-5 | should_fix | `/tmp/magistrate-96bfeca7/reports/61-s5-opus-report.md` O-4; `scripts/issue_calibration_acceptance_generation.py:20,98` | O-4's remedy ("pass `--ledger/--head-pin` explicitly") fails: out-of-repo paths yield `calibration_ledger_head_uncommitted`. And `runs/` is in `.gitignore:8`, so "a clone that has `runs/`" does not exist. | `OUTREPO_RC=3` below |
| F-6 | should_fix | chain `:18-24` | The "UNLANDED SURFACE" header omits the writer's slot-name generalization; `--slot d01` is rejected today (`BRACKET_SESSION_SLOTS = ("pre","post")`, `joulewise/calibration_ledger.py:66`). | `WRITER_SLOT_RC=2` below |
| F-7 | nit | chain `:75` | Bare PATH-resolved `mkdir -p`; G2-a uses `/bin/mkdir -p` (runsheet `:397`). Contradicts report claim 4. | `grep -n mkdir` on both |
| F-8 | nit | new dir `scripts/night_chains/` | R-d row S5 says "in the G2-a chain's home"; the G2-a chain is a *generated region* rendered by `scripts/gen_g2_phase_d.py`. Nothing re-renders or diffs the derivation chain when the runbook helpers change. | `git ls-tree 7c4366ec scripts/` shows no `night_chains` |
| F-9 | nit | chain `:167-169` | No `ERR`/`EXIT` trap: a failed capture ends the operator log at `slot_start` with no terminal line (rc 7). G2-a has no trap either, so parity holds. | `test_slot_count_override_and_writer_error_stop` |
| F-10 | nit | chain `:134,146` | `window_exhausted` exits 0; the driver cannot distinguish a truncated night from a complete one by rc. | read |
| F-11 | nit | `issue_calibration_acceptance_generation.py:94,111` | `WATCH_FIELDS[:2]` / `[2:]` positionally couples field order to its source (acceptance vs ledger T1); no regression pins the order. | read |
| C-1..C-9 | cleared | — | see "Cleared" | — |

## Per-item detail with verbatim rcs

**(1) Suites.** From the worktree root:

```
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation -v
Ran 25 tests in 27.069s   OK        UNITTEST_RC=0
$ zsh -n scripts/night_chains/calibration_derivation_only.zsh    ZSH_N_RC=0
$ python3 -m unittest tests.test_docs_freshness
Ran 31 tests in 0.724s    OK        DOCS_RC=0
```
`ls -l`: mode `755`. The live probe test ran (not skipped): `test_live_probes_report_this_machine_against_the_active_epoch ... ok`.

**(2) `check` live.** Reproduces the seat's block exactly:

```
os_build             25F84  25G83   MISMATCH
hardware_model       Mac15,9 Mac15,9 match
powermetrics_sha256  unavailable  b762e5bf…21330c5  MISMATCH
mlx_version          unavailable  unavailable       MISMATCH
ledger: calibration_ledger_missing, calibration_ledger_rollback
mismatched fields: os_build, powermetrics_sha256, mlx_version      CHECK_RC=3
```
The observed sha equals the sha the R-c pre-registration names in force. Exit codes: `CHECK_RC=3`, `PREP_RC=64` ("not implemented: waits for seat S3's…"), and a fourth undocumented code — argparse `NOSUB_RC=2` / `BOGUS_RC=2` (cleared: standard, fail-closed).

*Read-only:* `check` calls only `load_calibration_acceptance_bound`, `load_calibration_ledger_snapshot(mode="read_replay")`, `observe_machine`, `print`. I grepped the loader's 220-line body for `write|open(|mkdir|unlink|replace|rename|journal|touch` — no hits; `mode` only classifies custody. `powermetrics` is hashed, never executed (`:43,54`). `sys.dont_write_bytecode=True` precedes the `joulewise` imports. `git status --short` after the live run: clean. `test_equal_epoch_and_t1_admit_without_writes` additionally asserts byte-identity and no new files.

*Sources:* ACTIVE acceptance via `DEFAULT_ACCEPTANCE_BOUND_PATH` → `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`, `ACTIVE_ACCEPTANCE_ID = d079_calibration_acceptance_v2_n17_r6` (`:88,136`); T1 half from `snapshot.receipts[-1]["t1_bindings"]` with no older-row substitution (`:106-111`). MLX is read as `mlx.core.__version__`, byte-parity with the writer (`validate_powermetrics_fiducial.py:1722,1742`).

*O-4.* `DEFAULT_HEAD_PIN_PATH` is **tracked** (`configs/calibration/…`); only the ledger lives under gitignored `runs/`. So a fresh clone always refuses with `calibration_ledger_missing` regardless of epoch. Redirecting to another checkout does not help:

```
$ … check --ledger /tmp/…/calibration_observation_ledger.jsonl --head-pin /tmp/…/head.json
ledger: calibration_ledger_head_uncommitted                        OUTREPO_RC=3
```
because `_committed_pin_bytes` requires the pin to be relative to the hardcoded `REPO_ROOT` (`calibration_ledger.py:1156-1160`; `issuer:20,98`). **It fails closed with a named reason — good — but the report's O-4 sentence would mislead whoever drafts the step-0 proposal.** Correct statement: the watch's T1 half works only from canonical; adding `--repo-root` would be the general fix.

**(3) Chain, by reading + harness.** Confirmed present: one 600 s settle then 600 s start-to-start cadence anchored to `slot_start` (`:162`), never compressed; budget checked before the cadence wait (`:131`) and again after (`:143`); `abort-session --reason window_exhausted` once (`:90-99`); `set -euo pipefail` (`:31`); `PY/SLEEP/DATE` absolute and injectable (`:50-52`); `--ledger/--head-pin` explicit on all three calls, with recover's globals correctly **before** the subcommand (verified against `recover_calibration_ledger.py:120-129, 206-211`); no probes/pack/Git/claim output (static test + my own grep); operator log lines at every transition.

*Mandated mutation (budget → 0), scratch copy:*
```
CONTROL_RC=0 (8/8 OK)
MUTANT_RC=1  FAILED (failures=3):
  test_first_slot_that_cannot_finish_aborts_with_no_capture
  test_slot_that_cannot_finish_is_never_started
  test_window_exhausted_refuses_next_slot_and_aborts_once
```
Exactly the three the report names. Claim upheld.

*My additional mutation (F-2), post-wait guard deleted:* `zsh -n` rc 0, `MUTANTB_RC=0` — **all 8 tests green**. The guard is nonetheless load-bearing; with a capture that overruns the cadence the stale `next_start` admits a slot the fresh clock must refuse:

```
CONTROL(HEAD)  rc=0 captures=['d01']         capture_end_times=[1300]        window_end=1700
MUTANT-B       rc=0 captures=['d01','d02']   capture_end_times=[1300, 2000]  window_end=1700
```
MUTANT-B runs d02 to 300 s past the agent-free end — the exact failure the seat's blocker-1 fix exists to prevent. `run_chain(end=1700, capture=700)` is the missing regression; no existing test passes `capture` other than 480.

**(4) Flag inventory.**

| target | flags the chain passes | in tree today? |
|---|---|---|
| `reserve_calibration_window_bracket.py` | `--ledger --head-pin --session-id --window-id --plan-id --plan-sha256 --plan --evidence-root-id --runs-root --identity-epoch-json --t1-bindings-json --execute` | **exist** (`:58-90`) |
| ″ | `--session-kind derivation`, `--slot-count N` | **pending S1/S2** (absent; V5/R-d) |
| ″ | `"$@"` forwarding the per-slot bindings | **pending S2** — today the CLI demands four required scalars `--pre-attempt-id --post-attempt-id --pre-custody-locator --post-custody-locator` (`:71-74`); addendum 11 N2 turns them into a list |
| `validate_powermetrics_fiducial.py` | `--allow-live --ledger --head-pin --session-id --slot --attempt-id --output-root --power-policy` | **exist** (`:1526,1546,1547,1586,1590,1595,1542,1599`) |
| ″ | `--derivation-only` | **pending S1** (absent) |
| ″ | `--slot d01` | **pending S2** — flag exists but `choices=("pre","post")`: `WRITER_SLOT_RC=2`, `error: argument --slot: invalid choice: 'd01'`. **Not named in the chain's unlanded-surface header** (F-6) |
| `recover_calibration_ledger.py` | globals `--ledger --head-pin`, then `abort-session --session-id --plan --reason` | **all exist**, ordering correct (`:120-129,206-211`) |

Report item O-3 is accurate as written; O-2 (`--arm-countdown-s`, `--sleep-display-before-capture` deliberately absent) is unresolvable at this seat and correctly deferred to S1 — both flags do exist today (`:1531,1537`), so the choice is real, not forced.

**(5) Footprint / hidden behaviour.** `git diff --name-status 7c4366ec..HEAD` = exactly the three added files; `git status --porcelain -uall` empty. No repo-wide registry (docs-freshness, EXPECTED_IDS) needs the new files — `test_docs_freshness` rc 0. `MAGISTRATE_WATCHDOG.md` untouched, per A-8. No `NEEDS_SCOPE` overreach found. One benign global side effect: importing the module for tests sets `sys.dont_write_bytecode` process-wide (precedent: `reserve_calibration_window_bracket.py:18`) — cleared. `importlib.import_module("mlx.core")` initialises the MLX/Metal runtime as a side effect of an otherwise inert watch; unavailable on this machine today, and identical to the writer's own read — cleared, but do not run the watch inside a live window.

**Cleared (C-1..C-9):** cadence arithmetic (settle 600, then eleven 120 s remainders; captures at 600…7200); single settle (static count); executable bit; abort fires once; `PLAN_SHA256` taken from env is *cross-checked* against the plan bytes by the reserve script (`PLAN_HASH_MISMATCH`, `:106-116`) — stricter than G2-a's shasum-from-file; `mismatched_fields` unknown-vs-unknown refusal; historical-acceptance and missing-`identity_epoch` refusals; the two carried mutation-kill tests; read-only-ness.

## Verdict

**MERGEABLE AFTER FIXES** — as a skeleton, in a linked worktree, with these before the integration replay:

1. **F-1 (blocker):** move the reservation (and the F-3 preflight) *before* the settle, matching G2-a; then delete report O-1 as resolved rather than leaving it open.
2. **F-2:** add `run_chain(end=1700, capture=700)` as the post-wait-guard regression.
3. **F-3:** `test -f` on `$PLAN`, `$IDENTITY_EPOCH_JSON`, `$T1_BINDINGS_JSON` before any window time is spent.
4. **F-4:** log `slot_cadence_s` and `slot_capture_budget_s` at `chain_start`; guard `SETTLE_S ≥ 1`.
5. **F-5:** correct O-4 in the report before its sentence reaches the step-0 text for Ed.
6. **F-6:** add the writer's `--slot` slot-name generalization to the unlanded-surface header.

F-7..F-11 are nits; F-8 is worth a decision (register the chain with `gen_g2_phase_d.py` or accept the drift explicitly).
