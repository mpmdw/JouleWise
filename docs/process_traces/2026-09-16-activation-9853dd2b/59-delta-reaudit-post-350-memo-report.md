# Delta re-audit — post-#350 fix-forward + CUSTODY-PASS-MEMO-01 — Opus 5, read-only, 2026-09-17 09:30–10:00 PDT (30532437 vs c9589525)

Verbatim report:

# Delta re-audit — post-#350 fix-forward + CUSTODY-PASS-MEMO-01 (int/2026-09-17-post-350-memo @ 30532437)

Read-only. All work in `/tmp/reaudit-int4` (baselines) and `/tmp/reaudit-mut` (mutants). `/Users/edr/code/JouleWise-wt-int4-ref` verified clean at 30532437 at the end.

## Verdict: MERGEABLE-WITH-FIXES

One required suite is red at the integration head; the cure is a one-line README edit. The two branches' code and contract work is sound — every mutation the brief named was killed, and the memo's soundness properties hold under execution.

## Ranked findings

**1. BLOCKER (merge gate) — `tests.test_docs_freshness` is RED at 30532437.** `README.md:13` (added by 5857a838, inside the range) contains the literal `PR #350`, which `tests/test_docs_freshness.py:73` (`FORBIDDEN_VOLATILE_FACTS["pull-request literal"]`) bans in "current" sections.
`cd /tmp/reaudit-int4 && python3 -B -m unittest tests.test_docs_freshness` →
`FAIL: test_current_sections_do_not_copy_volatile_literals … Lists differ: [] != [('README', 'pull-request literal', 'PR #350')]` / `Ran 80 tests … FAILED (failures=1)`. Base `c9589525` README has no `PR #`, so this delta introduced it.
Same line is also stale at this head: "**Next:** halve the capture writer's custody passes (CUSTODY-PASS-MEMO-01)" — that lane is *in* this branch and the ruled constant is 3, not a halving.
Fix: drop "(PR #350)" and rewrite the Next clause to the post-merge state.

**2. SHOULD-FIX — the courier never reports `phase`.** `docs/process/NIGHT_COURIER_PROMPT.md:21-24` tells the courier to report "the exact calibration code, budget in seconds, elapsed time, and `existing_session`". The new abort document's distinguishing field is `phase: "abort"`, so an abort-step refusal is emailed in wording identical to a capture-step one — Ed cannot tell from the email that the slots completed and only the window-exhausted abort refused. The refusal *does* reach the courier (verified below), so this is presentation, not loss.
Fix: add `and the phase` to that sentence.

**3. NIT — kernel design summary contradicts the ruling.** `docs/process/state_kernel.json:1405` still reads "Lower WRITER_CUSTODY_PASSES from 4 to 2"; the ruling (and `status_note`, line 1421) is 3. Outside the object of study; `python3 scripts/gen_state.py --check` rc=0. Fix: amend the summary to 3.

**4. NIT — surviving mutant (not a defect).** Removing the pid-file wait from `test_probe_timeout_kills_reservation_and_descendant` survives 5/5 on this Mac (`Ran 1 test … OK` ×5). The load-bearing half of the cure is the `0.3 → 3.0 s` supervisor timeout: with the wait kept and the timeout reverted to 0.3 s the test fails 3/3 with the *named* assertion ("the stalled reservation never reached its own startup inside the probe deadline"), not a `FileNotFoundError`. So the wait does exactly what record 52 claims — it converts a slow-runner flake into a named failure — but it is unkilled locally by construction. No action.

**5. NIT — "3 with a repair" is pinned at the snapshot level only.** `test_a_repair_that_mutates_the_ledger_forces_one_honest_re_read` proves head-digest invalidation; nothing pins `custody_passes == 3` in a real writer receipt. Reasoned from code and confirmed safe (below). Optional: a receipt-level regression with a torn tail.

## Mutation table

| # | Mutant | Result | Killed by (observed) |
|---|---|---|---|
| M1 | drop `clear_custody_memo()` in `_release_writer_lease` (`validate_powermetrics_fiducial.py:1464`) | **KILLED** | `test_releasing_the_writer_lease_clears_the_allowance_it_holds` — `AssertionError: ('aaa…', frozenset({…})) is not None` |
| M8 | drop `self.clear_custody_memo()` in `next_operation` (`calibration_ledger.py:2041`) | **KILLED** | `test_a_new_operation_starts_disarmed_and_uncounted` — `AssertionError: True is not false` |
| MP | `WRITER_CUSTODY_PASSES = 2` | **KILLED ×2** | `…constant_matches_the_memoized_writer` (`3 != 2`) and the boundary case `test_probe_receipt_gates_writer_passes_and_zero_observations (custody_elapsed_s=26.693…)` — `Refused not raised` |
| MA | abort-session refusal back to plain `emit_refusal` | **KILLED ×2** | `NightBudgetAbortPathTests.test_blocked_abort_publishes_the_typed_refusal_document` and `NightDriverTests.test_real_abort_command_refusal_reaches_the_driver_as_refused` — both `FileNotFoundError: …calibration-refusal.json` |
| MI | old interpreter stimulus (plain copy, no appended byte) | **KILLED** | `test_install_recomputes_code_ledger_and_interpreter_bindings (field='chain_python')` — `AssertionError: '87d4df…' == '87d4df…'` |
| MW | drop the pid-file wait | **SURVIVED** 5/5 | see finding 4 |
| MT | probe timeout back to 0.3 s | **KILLED** 3/3 | named assertion above |

**Why the new interpreter stimulus is platform-independent (one sentence):** `interpreter_identity` (`night_agent_install.py:694-707`) runs the target interpreter and has it report `sha256(Path(sys.executable).read_bytes())`, so appending a byte moves a *content*-bound field on every platform, whereas the old plain copy moved only `path` — which CPython resolves differently for a symlinked interpreter on macOS and Linux, and left `sha256` identical (proved by MI).

## Traced, no finding

- **Append after a stale memo — none exists.** Instrumented `bounded_custody_reasons` and ran a real two-slot derivation capture: per writer pid exactly `pass=1 armed=False`, `pass=2 armed=True`, `MEMO-HIT`, `MEMO-HIT` — four sweeps, two reads, one allowance. No fifth entry: `claim_bracket_session_slot`, `append_pending_receipt` (no custody pass in its body, `calibration_ledger.py:6180+`) and the finalize allowance perform no whole-corpus pass, so no append is guarded by a memoized result.
- **Worst case is 3, and the gate is not loosened in seconds.** `_begin_once` orders readiness (sweep 3) → `_validate_slot` (sweep 4) → `claim_bracket_session_slot` (the append), so nothing appends between sweeps 3 and 4; a mutating repair costs exactly one re-read. `120/(3×1.5) = 26.67 s` admits the *same* 80 s of worst-case preparation as the old `120/(4×1.5) = 20 s` × 4 passes.
- **Memo key can't go stale.** `bounded_custody_reasons` has exactly one caller (`calibration_ledger.py:2654`), and `custody_deadline.ledger_head_sha256 = physical_digest` is set at `:2642` in the same load, immediately before it. Structural refusals (`custody_backup_roots_disabled`) run *before* the memo consult.
- **`phase="abort"` is accepted.** No phase enumeration anywhere: `_calibration_refusal` (`run_night.py:516-535`) validates schema, `plan_id`, non-empty `code`, and `exit_code == 2 == chain_exit_code` only. All 76 `RefusalCode`s have `process_exit == 2`, so no code can trip the exit-code check. `abort-session` has no early `emit_refusal` path, so every refusal from it takes the new document route; `set -euo pipefail` in the chain makes a failing `abort_window_exhausted` exit 2 before its `exit 0`. The document lands in `refusal_documents` (`_refusal_paths`, `:262`) and `run_courier` is asserted called once.
- **F4/S7 seam.** The merged runbook (`derivation_night_runbook.md:1353-1363`) says exit-2-with-document → `REFUSED`/`night_calibration_refused` and exit-2-without → verdict `GO` with `chain_exit_code` 2; both match `run_night.py:1879-1912` and the pinned `test_calibration_exit_two_without_document_keeps_chain_failure`.
- **Shared seams are consistent.** `3` / `T ≤ 26.67 s` appear uniformly in the contract, runbook (§1.2 and :1978) and handback; no stale `4` / `20 s` outside process traces. Both usage strings list exactly the flags `main` accepts and the shell forwards. The "seven variables" row matches `_chain_environment` (7 keys). The pre-settle sentence matches the chain (`--pre-reserve-strict`, no separate readiness command).

## Suites (all at 30532437, `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest …`)

`test_calibration_ledger_custody` 60 OK · `test_validate_powermetrics_fiducial_derivation_only` 23 OK (289.9 s) · `test_run_night` 129 OK · `test_install_night_agent` 61 OK · `test_arm_retry` + `test_authentication_io` + `test_docs_freshness` 80, **1 failure** (finding 1). `zsh -n` OK on the chain and the installer. `gen_state.py --check` rc=0; `gen_derivation_night.py --check` → `PASS generated derivation-night wrapper region matches`, rc=0.
