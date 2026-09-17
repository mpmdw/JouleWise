# Cold-gate ruling 61 — NIGHT-STALL-WALLCLOCK-ABORT-01 (Fable 5.1, cold seat, 2026-09-17)

**Preconditions.** Checkout `5472ff53` (worktree). Auto-loaded before any action: `~/.claude/CLAUDE.md`, repo `CLAUDE.md`, memory index `MEMORY.md` (index lines only). Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, narrative state. Validator: typo charter sha → `REFUSE reason=charter_trusted_observed_mismatch rc=2`; correct sha `099de884…c95d81` + packet `b4ebbd6e…9ebc3` → `PASS rc=0`, six exhibit digests match the manifest. Exhibit D excerpts match the file at this head line for line. No subagents, no background jobs, one foreground probe (below), no launchctl, no custody roots touched.

**Executed probe (Q1/Q3).** `/tmp/cg61_probe.py`: Popen `/bin/zsh` with `start_new_session=True`; it spawned g1 = `zsh -c 'trap "" TERM; sleep 300'` (stays in the group) and g2 = python `os.setsid()` then sleep (leaves the group). `os.killpg(pgid, SIGTERM)` → direct child `wait()` returned exit −15 after **0.01 s**; `pgrep -lf -g <pgid> .` still listed g1. `killpg(SIGKILL)` → group census exit 1, empty. g2 survived both and is invisible to `pgrep -g`. Conclusion: `wait()` on the direct child proves nothing about any other group member, and a member that changed session is beyond both `killpg` and a group census.

**Where I disagree with the packet's framing:** (c) is presented as a live option; I reject it (Q1). The Q4 premise "a zero-capture t0 refusal … auto-retries" is not what this head encodes (Q4).

---

## Q1 — deadline placement and shutdown allowance

**Ruling: (d) + a separate 300 s driver constant.** (a) REJECT, (b) REJECT as written, (c) REJECT, (d) AFFIRM in the following shape. MATERIAL.

Deciding evidence (verified):
- The chain's acquisition steps are already fenced at the window end: reservation and every slot writer pass `--custody-deadline-epoch-s $(( WINDOW_END_EPOCH_S - 10 ))` (`scripts/night_chains/calibration_derivation_only.zsh:185`, `:248`), and no slot starts unless it fits (`:219–223`, `:231–235`). Only `abort_window_exhausted` (`:125–134`) carries **no** deadline or budget flag; `abort-session` accepts none (`scripts/recover_calibration_ledger.py:224–228`); `abort_calibration_session` takes `CalibrationWriterLease` and calls `calibration_session_status` with no `custody_deadline` (`joulewise/calibration_ledger.py:6121–6135`), so each `_custody_state` builds a fresh ambient budget (`:5501–5504`). Exhibit C F4's 12 × 120 s = 1440 s (≈ 1560 s with overhead) is confirmed by code.
- Nominal abort start: the loop checks `next_start + 480 > end` immediately after a slot ends, so the abort begins about 30 s before the window end in the common case, and later only if a writer overran its predictive 480 s budget (exhibit C §3: the budget gates starting, never kills).

Why each option falls:
- (a) kills a lawful abort on every night that reaches `window_exhausted` (the abort is normally still running at the window end), leaving the session open with a live lease each time.
- (b) reuses `COURIER_DEADLINE_S` (`scripts/run_night.py:64`, an R-7 delivery figure derived from `cold_start.json`) as a shutdown allowance. Same value, wrong owner: a future courier retune silently moves the kill point. The **value** 300 s is right; the **binding** is wrong.
- (c) sizes a driver constant to a chain pathology (per-slot unbounded budgets) and couples the driver to two chain knobs (`SLOT_COUNT`, `CUSTODY_BUDGET_S`). A 24-minute machine hold past the declared window is a mechanism defect being accommodated instead of cured. It is *not* acquisition grace (nothing new is acquired after the abort begins), but it is 24 minutes in which a stalled chain that never reached the abort is also left alive.

Shape of (d), exact:
1. `abort-session` gains `--custody-budget-s` (float, seconds); the chain passes `--custody-budget-s "${CUSTODY_BUDGET_S:-120}"` as its sibling calls do (no absolute deadline: `calibration_ledger.py:2093–2097` explains why the abort cannot take one). `abort_calibration_session` builds ONE `CustodyDeadline(budget_s, telemetry_stream=None)` and threads it into `calibration_session_status(custody_deadline=…)` (`:5541` already accepts it), so the whole status pass shares **120 s total**, not 120 s per slot. Worst-case abort ≈ 120 s + lease/repair overhead (seconds). NIT for the implementer: passing a deadline flips `calibration_session_status` to `mode="issuing"` (`:5546`); keep the abort's read mode explicit so the bytes read do not change.
2. Driver constant `WINDOW_SHUTDOWN_GRACE_S = 300` in `scripts/run_night.py` next to `COURIER_DEADLINE_S`, with the comment: `# Separate shutdown allowance for the chain's bounded end-of-window abort (one shared 120 s custody budget plus lease overhead); not derived from the courier deadline.` Deadline = `t0_epoch_s + window_max_s + WINDOW_SHUTDOWN_GRACE_S`, computed once from the wall clock when the chain starts and then tracked on `time.monotonic()`.
3. Arithmetic: deadline +300 s, termination ≤ 70 s (Q3), courier ≤ 300 s ⇒ ≤ 670 s after the window end; dead-man at +3900 s (`run_night.py:1076`) leaves ≥ 3230 s. `deadman_epoch`, `_completion_epoch_s` (`:1179–1180`) and the plan schema are untouched (`:466` comment: the v2 schema is exact; a plan field would be a contract change).
4. Lawful-abort regression margin: abort starting at the window end and taking its full 120 s budget finishes 180 s before the deadline.

Is +300 s "pre-termination grace that permits acquisition beyond the declared window"? **No.** Acquisition is fenced by the chain at end − 10 s (cited above); the grace covers only the closing abort, which acquires nothing. It is also the first hard bound on a capture writer that overruns its predictive budget.

**Class:** mechanism choice (a driver constant plus a CLI flag; no gate, census, plan or dead-man semantics change). The only text a contract-keeper should record: runbook note "end-of-window abort is bounded by one shared custody budget of 120 s; the driver terminates the chain 300 s after the exclusive window end."

## Q2 — independence from the census cadence

**Ruling: (iii) both.** MATERIAL.

Evidence: the loop sleeps ≤ 1 s (`run_night.py:623`) but two calls inside it can block without bound: (1) the probe runner's `subprocess.run(timeout=30)` (`:296–302`) — on `TimeoutExpired` the stdlib kills the child and then `wait()`s with **no** timeout, so a `pgrep` stuck in the kernel holds the loop; (2) `_append_census(census_path, …)` (`:587`) writes under the night dir, which lives under the custody root — a consent-blocked or hung volume stalls the driver by exactly the 2026-09-16 mechanism (exhibit F). A check that only runs between iterations therefore cannot be relied on.

Mechanism:
- (i) `deadline_monotonic` checked before the probe, after the probe, and after `_append_census`; sleep bound becomes `min(1.0, max(0.01, min(next_census − now, deadline − now)))` — never sleep past the deadline.
- (ii) a daemon `threading.Thread` (not `signal.alarm`: single slot, main-thread-only delivery, and useless if the main thread never returns from a syscall) that at the deadline performs the Q3 termination sequence itself and writes `chain.deadline` `{pgid, deadline_epoch_s, fired_epoch_s, proven}`. When the main loop resumes it sees `process.poll() is not None` plus the marker and reports `night_window_exceeded` (or `night_chain_alive`, Q3). The thread must not run the courier; the courier stays on the main path behind the existing "termination proven" condition (`:1928`).

Uncovered failure, stated: the driver process itself frozen (SIGSTOP, or every thread blocked while a C call holds the GIL), a group member the kernel will not reap because it is in an uninterruptible wait (SIGKILL is deferred until the syscall returns), or a member that left the session (probe g2: unreachable by `killpg` and invisible to `pgrep -g`). The custody worker is launched with `start_new_session=False` (`calibration_ledger.py:2191`), so it stays reachable; make that an asserted invariant in the regression, not a runtime assumption. Those residues belong to the dead-man (a separate launchd process at +3900 s), which already refuses `night_chain_alive` correctly. **Class:** mechanism choice.

## Q3 — proof of termination of the whole group

**Ruling: (i), strengthened; (ii) REJECT; the strengthened (i) is the better proof (iii).** MATERIAL — and it applies to today's census-abort path as much as to the new deadline: by the probe, `_terminate_process_group` (`run_night.py:390–416`) returns True the instant the direct child dies, with group members possibly alive; SIGKILL is only ever sent when the *direct child* ignores SIGTERM for 30 s.

Exact sequence: `killpg(SIGTERM)` → `wait(30)` on the direct child → `_probe_group_absent(pgid)` (exists at `:2069–2076`; exit 1 and empty stdout = absent; OSError/timeout = **not** absent) retried every 0.2 s up to 5 s → if not absent, `killpg(SIGKILL)` → `wait(30)` → group census retried up to 5 s. Proven ⇔ direct child reaped AND the group census returned empty. Bound: 30 + 5 + 30 + 5 = **70 s** worst case, 65 s in the normal escalation. On failure: `chain.unkilled` `{pgid, epoch_s, group_census: [...]}` as today, `termination_proven=False`, courier suppressed (`:1928`). (ii) is rejected because the worker keeps no pid file or progress record (`calibration_ledger.py:2188–2193`: two pipes, no on-disk record) and a group census is strictly stronger without asking the worker to cooperate.

Reason on unproven termination at the deadline: **keep `night_chain_alive`**, with evidence `{"trigger": "night_window_exceeded", "deadline_epoch_s": …, "pgid": …, "group_census": [...]}`. Rationale: `night_chain_alive` is registered as "the existing chain has not been proved ended" (`joulewise/night_gate.py:88`, `joulewise/arm_retry.py:46`), the census-abort path already uses it for exactly this state (`run_night.py:603`), and the dead-man will re-derive the same state at +3900 s; a third code would split one machine state across two names. The courier is suppressed in this case by the acceptance itself, so "window exceeded AND not proven dead" is read from `refusal.json` evidence and `chain.deadline`, not from a courier line. **Class:** mechanism choice.

## Q4 — class of `night_window_exceeded`

**Ruling: COLD.** Deciding consideration: retry is granted only to causes that establish the machine did nothing (all four `RETRY_CAUSES`, `arm_retry.py:21–27`, are arm-time/pre-publication; the policy text at `:208` keeps "every capture, clock, custody, ledger or pre-registration guard" cold). A window overrun by construction cannot establish that: the chain passed or stalled inside the reservation, intent may be written (exhibit B), the session may be open under a live lease. Note for the record: at this head even the production t0 census refusal `night_refused_agent_present` is COLD ("including a receipt at t0", `arm_retry.py:30`); the auto-retry Ed granted lives in `arm_idle_interactive`, an arm-time cause. The packet's analogy therefore does not hold in this checkout.

Exact text. `night_gate.py` registry line: `"night_window_exceeded",  # driver wall-clock deadline: chain terminated after the exclusive window end plus shutdown grace`. `arm_retry.py` COLD_GATE_CODES entry: `"night_window_exceeded": "The chain ran past the exclusive window end and was terminated by the driver; reservation or capture intent may have been written and the session may need desk recovery; never an auto-retry cause."` Regenerate the embedded ARM-RETRY-POLICY v1 block (`:196–212`) so `tests/test_arm_retry.py:96–99` parity holds. Courier detail string: `"chain terminated at the wall-clock deadline (window end + 300 s); process-group termination proven"`. **Class:** mechanism (registry addition under the existing A172 rule; no rule text changes).

## Q5 — landing

**Ruling: (i) implement now, then re-plan.** Risk of (ii), which decides it: the custody cures bound one stall class; the writer's capture budget is predictive only (`zsh:217–223`), the abort path is unbounded per slot today (Q1), and any non-custody stall has exactly one terminator, a person entering the census (exhibit F: 11 h 07 m). With Ed remote, (ii) risks a repeat of the 09-16 shape on the very next night. Risk of (i): Opus-only seats touch the driver's termination path without Codex refuters until 09-19; mitigate with the four regressions below and a lead read of the full diff (~150 driver lines, ~25 CLI/ledger lines). Required regressions: (1) chain that sleeps past the deadline with a `start_new_session=False` grandchild → both gone, `night_window_exceeded`, courier ran; (2) grandchild that ignores SIGTERM → SIGKILL escalation, proven; (3) stubbed census refusing to empty → `chain.unkilled`, `night_chain_alive`, courier suppressed; (4) chain whose abort starts at the window end and takes 120 s → not interrupted, exit 0, verdict from the chain; plus (5) FIFO-blocked `manifest.json` during `abort-session` → typed refusal within ~120 s total, not 1440 s.

## Severity summary
- MATERIAL: existing helper proves only the direct child (probe; fixes today's census-abort path too).
- MATERIAL: driver loop can block inside a probe wait or a custody-root write; deadline needs an independent thread.
- MATERIAL: abort path holds the lease for up to ~26 min with per-slot budgets; bound to one shared budget.
- NIT: threading a deadline changes the abort's custody read mode unless made explicit.
- NIT (packet hygiene): Q4 premise about t0-refusal auto-retry contradicts `arm_retry.py:30` at this head.

Verdicts: Q1 (d)+constant AFFIRM, (a)(b)(c) REJECT · Q2 (iii) AFFIRM · Q3 (i)-strengthened AFFIRM, (ii) REJECT, reason `night_chain_alive` · Q4 COLD AFFIRM · Q5 (i) AFFIRM. No REFUSE.
