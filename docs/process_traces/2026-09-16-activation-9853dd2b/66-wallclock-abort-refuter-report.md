# NIGHT-STALL-WALLCLOCK-ABORT-01 refuter — Opus 5, read-only, both lenses + eleven mutations, 2026-09-17 12:05–12:30 PDT (a4d530cd vs 5472ff53)

Verbatim report:

# Refuter report — NIGHT-STALL-WALLCLOCK-ABORT-01 (a4d530cd vs 5472ff53), Opus 5, read-only, both lenses

**Verdict: MERGEABLE-WITH-FIXES.** No blocker. Every property P1–P6 traced and executed; two ordered clauses are correct in code but have NO regression (mutants survive 135 tests) — both fixes are test-only and bench-sized. Nothing edited: `git status --short` empty in both `JouleWise-wt-a221-ref` and canonical `JouleWise`; all experiments in `/tmp/refute-a221` (probe files deleted after use).

## Suites / checks (at a4d530cd, this session)
`tests.test_run_night` 135 OK · `test_night_gate` 59 OK · `test_arm_retry` 27 OK · `test_calibration_ledger_custody` 62 OK · `test_custody_mode_inventory` 7 OK · `test_docs_freshness` 31 OK · extra (touched files) `test_issue_calibration_acceptance_generation` 114 OK · `test_gen_derivation_night` 40 OK · `zsh -n` chain rc 0 · `gen_derivation_night.py --check` `PASS` · `shasum -a 256` chain = `b5beea46…ead6fb` (matches both re-pinned doc sites).

## Mutation table (11 probes, one line reverted each, in the /tmp copy)
| # | mutation (file:line) | result | observed |
|---|---|---|---|
|M1|watchdog thread never started (`run_night.py:697`)|KILLED|`refusal.json never appeared within 30.0 s`|
|M2|firing skips the refusal document (`:770-774`)|KILLED|2 failures + 2 errors (`6 != 5`; document missing)|
|M3|census retry does not re-signal (`:437`)|**SURVIVED**|`tests.test_run_night` 135 OK|
|M4|rc≠0 read as absent (`:2419`)|**SURVIVED**|`tests.test_run_night` 135 OK|
|M5|only the explicit `killpg(SIGKILL)` → SIGTERM (`:495`)|SURVIVED|see F3 (redundant with M3's re-signal)|
|M5′|whole phase-two escalation → SIGTERM (`:494-501`)|KILLED|`AssertionError: 4 != 6`|
|M6|abort reads every declared slot (`calibration_ledger.py:6215`)|KILLED|rc 2 timeout on `session-abort-pre`; `1 != 2` worker pids|
|M7|budget threaded as an absolute deadline (`:6202`)|KILLED|`calibration_window_exhausted` + 3 errors|
|M8|`WINDOW_SHUTDOWN_GRACE_S = 60` (`run_night.py:70`)|KILLED|2 failures (constant + ownership comment)|
|M9|reason code removed from `COLD_GATE_CODES` (`arm_retry.py:53`)|KILLED|`test_every_cold_assignment_is_explicit`, `test_both_document_blocks_are_exact`|
|M11|resuming loop always re-writes (`run_night.py:2218`)|KILLED|`['refusal.json','refusal-01.json']`|

## Findings (ranked)
**F1 SHOULD-FIX — the rc-2 census discipline has no regression.** `scripts/run_night.py:2419` (`if result.returncode == 1 and not lines`). Clause: P2 / ruling Q3 + amendment 4 ("rc 2 = malformed = not absent"). M4 (`== 1` → `!= 0`) survives all 135 driver tests; no test anywhere references `_group_census`/`_probe_group_absent`. The code IS correct — live probe: `_group_census` returned `(False, ['census_exit_2: usage: pgrep …'])` for a malformed arg, `(False, ['census_failed: TimeoutExpired…'])`, `(False, ['census_failed: PermissionError…'])`, `(False, ['6622 /bin/sleep 5'])` live, `(True, [])` empty. Fix: one unit test over those five cases.

**F2 SHOULD-FIX — the re-signal on each census retry has no regression.** `run_night.py:437` inside `_prove_group_absent`. Clause: magistrate amendment 4 / brief C. M3 (delete the `_signal_group` line) survives all 135 tests. Fix: assert `killpg` call count > 1 per phase using the fixture's existing `_signal_spy`.

**F3 NIT — the explicit SIGKILL send is redundant.** `run_night.py:495`; M5 survives because `observe(signal.SIGKILL)` re-sends SIGKILL inside `_prove_group_absent`. Doubly covered, not a defect; it is why the single-line mutant lived and M5′ died.

**F4 NIT — `custody_mode="read_replay"` is inert on the bounded path.** `calibration_ledger.py:6210`; M10 (delete it) survives `NightBudgetAbortPathTests` and `test_custody_mode_inventory`. Mechanism: with a `CustodyDeadline` present, `_custody_state` (`:5504-5517`) uses `mode` nowhere — it hardcodes `_custody_probe_paths(path, mode="issuing")` at `:5508` and reads `str(path)` through `_bounded_custody_request`; `mode` only reaches `probe_custody` in the unbounded branch (`:5518-5521`). The ruling's mode-flip NIT is satisfied in form and the bytes genuinely do not change — but the guard would only bite if that branch ever honoured `mode` (pre-existing; `load_…_snapshot` runs `verify_custody=False`).

**F5 NIT — "one *shared* custody budget" survives the amendment that removed the sharing.** Runbook §1.2 required sentence and `run_night.py:66-68`. Under amendment A there is one read, so nothing is shared. Fix: "one 120 s custody budget for the abort's single custody read".

**F6 NIT — the 300 s sizing rationale is in no landed text, and its residual is unstated.** The docs justify 300 s only as "120 s of abort … covered"; the magistrate's amendment 2 rationale (the writer-overrun tail) appears nowhere, so a reader cannot derive 300 rather than 130. Residual, arithmetically: the chain starts a slot only if `next_start + 480 ≤ END` and the 480 s capture budget is predictive (never kills), so a writer that overruns by >180 s has its lawful closing abort interrupted at +300 s. Severity is limited by a fact worth recording: `CalibrationWriterLease` is a kernel `flock` (`calibration_ledger.py:3623-3628`), released when the process dies — so the harm is an OPEN session (desk-recoverable; the next arm refuses) and not a stuck `LIVE_WRITER_CONTENTION` lease. One sentence in §1.2 closes it.

**F7 NIT (first-use/replication) — "re-signalled" is unglossed.** `NIGHT_HANDBACK.md:569`. Why a census re-sends the signal (a member forked by a survivor after the first signal inherits the pgid unsignalled) exists only in the code docstring. One clause in the table row.

**F8 NIT (observed; ruling-sanctioned residue).** Real-process probe: a grandchild calling `setsid` survives; the night reports `ABORTED` / `night_window_exceeded`, `proven: true`, no `chain.unkilled`, courier ran, escapee alive. Honest against the claim actually published (both docs say "a `pgrep -g` census of its **group** came back empty") and explicitly out of scope per Q2/Q3; the production invariant (`start_new_session=False`, asserted in the regression) means no chain member escapes. Correction for the record: the ruling's "those residues belong to the dead-man" does not hold once the courier delivered — the dead-man stands down on `courier.sent`, so nothing would report an escaped member.

**F9 NIT.** Deterministic race probe: with the chain already exited 0 at the deadline instant, `fire()` records `chain.exited` `exit_code: 0` (the chain's own code), writes exactly ONE document, is idempotent (`first is second`), and `cancel()` hands back the same outcome — but the verdict is the deadline's (`ABORTED`), not `GO`. Zero-width in practice (a lawful chain closes ≥110 s early), fail-safe direction, and the artifact shows 0.

## Traced, no finding
**P1.** Proven by real process: with the main loop blocked 40.15 s inside `agent_census`, the chain's group was gone **2.17 s after the hang began**; reason `night_window_exceeded`, `proven: true`. Blocked-`_append_census` FIFO case green. `fire()` orders termination BEFORE the document write, so a hung custody volume still loses the machine hold, not just the report. No courier call inside `fire()` (only `_finish_reporting` calls `run_courier`); M1/M2/M11 killed.
**P2.** Sequence at `run_night.py:487-508` matches the ordered shape; proven ⇔ `reaped and absent`; measured phase bound 5.06 s (overshoot 0.06 s), so ≤70.12 s worst case against 230 s of slack. Unproven path: `night_chain_alive` + `evidence.trigger night_window_exceeded` + `chain.unkilled.group_census` + `EXIT_COURIER_FAILED` with `run_courier` not called. Both real paths use the strengthened helper (`:730`, `:899`); the courier retry site (`:1275`) is `prove_group_absent=False` with the stated reason, and its behaviour is byte-for-byte the old contract.
**P3.** `custody_state_scope="next_slot"`: `assertFalse(marker.exists())` proves a blocked non-next slot's barrier is never entered; the 12-slow-slot test proves exactly one worker pid, all paths under `session-abort-d02`. `"not_inspected"` is never consumed — the only readers are `slots[next_slot]` under `next_slot is not None` (`:5639-5649`, `:6235-6239`); snapshot load is `verify_custody=False`; the abort's returned mapping does not embed `slots`, so no new string reaches stdout. Budget validated (nan/inf/≤0) BEFORE the lease; the CLI refusal document reports the flag's seconds with the marker as fallback. M6/M7 killed.
**P4.** Five sites present; `test_both_document_blocks_are_exact` green and killed by M9.
**P5.** `120 ≤ 300 − 70` asserted with the real constants; lawful-abort regression green; M8 killed.
**P6.** Plan schema untouched (dataclass-field assertion), `_completion_epoch_s`/`deadman_epoch` identities asserted, `_probe_group_absent` delegates with identical truth value so `_stop_probe_group` is unchanged, `CENSUS_INTERVAL_S`/`PROBE_TIMEOUT_S` unchanged, gate registries gained exactly one code.
**Docs vs code, every number:** `CUSTODY_BUDGET_S` 120 (`zsh:80`), `SLOT_COUNT` 12 (`:85`), `window end − 10` (`:192`, `:255`), `WRITER_CUSTODY_PASSES 3 × 1.5 → 26.67 s` (`night_agent_install.py:680-686`, `:834`), 300/70/300/3900, 670, 3230 — all correct; `night_window_expired` and `night_chain_digest_mismatch` are real gate codes; prereg rev1 pins `b8bf5b0a` exactly once, matching a4d530cd's corrected paragraph; no stale `1440`/`1560`/"26 min" text survives.
