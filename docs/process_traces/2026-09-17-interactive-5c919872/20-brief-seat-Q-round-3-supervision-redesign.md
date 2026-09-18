SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/night_gate.py","joulewise/night_plan_writer.py","joulewise/arm_retry.py","joulewise/quiet_admission.py","scripts/run_night.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_night_plan_writer.py","tests/test_arm_retry.py","tests/test_run_night.py","tests/test_gen_derivation_night.py","tests/test_quiet_admission.py","tests/night_gate_fixtures/**","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md","docs/contracts/night_quiet_admission.md","docs/contracts/pack_night_go_receipt.md"]
BASE_HEAD: 5c5a3323
BASELINE_MANIFEST: .codex-bridge/baselines/mag-5c919872-gate-quiet-r3-2155.json
BASELINE_DIGEST: sha256:06ec851c177889fb9340627ae600abcc0cdd083e7f85a05cb6a8b087b589fbd9
LEASE_ID: lease-79c5a1766616453fb93e93b7cea20ffd

# Seat Q round 3 — bind-loop supervision REDESIGN per the adopted consult (not a patch)

Branch `feat/2026-09-17-night-gate-quiet-admission` in `/Users/edr/code/JouleWise-wt-gate-quiet`, head `5c5a3323`. Same rules: leave every change unstaged (the lead commits by pathspec), do NOT push, nothing outside WRITE_SCOPE, no `launchctl`, no `~/night-custody`, no network, no `sudo`. Do not end your turn before every item is done or a genuine early return is required.

Why a redesign: three consecutive reviews found the bind-loop supervision blockable on a different edge of the same seam (round 1: `join()`; round 2 fix: `poll(0)` readiness; delta re-audit `16-delta-reaudit-astra.md` F1: unbounded `recv()` after readiness, executed with a real worker that stops after the message header). The standing escalation rule sent the seam to a design consult; the consult's design is ADOPTED by the magistrate and is the authority for this round: read `/Users/edr/code/JouleWise/docs/process_traces/2026-09-17-interactive-5c919872/19-consult-bind-supervision-astra.md` first (read-only absolute path), then its cited lines in this worktree. Where this brief and the consult differ, this brief governs; where this brief is silent, the consult governs.

## The invariant you are implementing

No operation on the deadline-owning path (the tick loop that services the census cadence, the absolute bind deadline, job transport and cleanup) may wait for worker progress, EOF, filesystem completion, or child exit. Every operation that survives on that path carries a one-line bounded-work argument in a comment.

## Items

1. **Transport (`_BindTask`, `scripts/run_night.py` ~:1994–2040).** One dedicated pipe per job for EVERY bind job (census, static checks, hard checks, sampler): parent end set non-blocking; application protocol = 4-byte big-endian payload length + one JSON envelope `{job_id, ok, result | error}`; maximum payload 256 KiB including diagnostics — a length above the cap is rejected BEFORE allocation and is an ERROR; a worker whose serialization exceeds the cap sends a small error envelope instead. `advance()` performs a bounded number of raw `os.read()` calls with a fixed byte budget per tick; `EAGAIN` = pending; premature EOF = ERROR; decode only a complete buffered payload. `result()` returns cached data and performs NO I/O. Never use `Connection.recv`/`recv_bytes` on the parent side.

2. **Tick state machine (replaces `await_task()` and the nested census wait, ~:2090–2210).** Phases: static checks → pre-sample hard checks → sampling → post-sample hard checks → final checks → cleanup. Every tick, in this order and unconditionally: evaluate the absolute bind deadline (monotonic, converted once), service the census cadence (`CENSUS_INTERVAL_S`), advance every live job's transport by its byte budget, poll cleanup. A worker's state never decides whether those steps run. "Completed by the deadline" keeps its meaning; at the boundary no further bytes are awaited.

3. **Cancellation separate from reaping (~:2031).** At expiry: latch the refusal, send group termination immediately (`os.killpg`), then poll exit/reap without waiting (`waitpid(WNOHANG)`), returning only after direct children are reaped; remove the one-second synchronous join from the tick path. A complete valid frame IS publication: a worker that hangs after publishing never delays the decision; it is terminated with its group and reaped.

4. **Journal writer (~:2096, ~:2148, ~:2163).** One writer, in the parent process, on its own thread, fed immutable records through a bounded queue with NON-blocking submission; it owns append ordering, acknowledgements, and the incremental journal digest/line count; GO requires the acknowledgement of the final record; queue saturation or a write failure is terminal (no GO, timely termination) and is recorded in the receipt as `journal_failure: <reason>`; census appends move off the ticker too; `finish()` no longer re-reads the whole journal.

5. **Worker process.** Production workers are exec subprocesses: `sys.executable -m joulewise.quiet_admission --observation` (add a full-observation mode beside the compact smoke CLI at `joulewise/quiet_admission.py` ~:301) and a private dispatch for census/static/hard jobs beside the driver's existing private worker dispatch (~:2922); `start_new_session=True`, `close_fds=True`, the result descriptor via `pass_fds` and marked non-inheritable in the worker before it launches any tool; no `preexec_fn`; stderr redirected to a bounded file or drained boundedly — never an unread pipe. Injected callbacks for tests go through an explicit test-only dispatch hook, never through `fork`.

6. **Grace.** Per-sample local allowance = `sample_interval_s + 215` s (the seven tool timeouts in `joulewise/quiet_admission.py` ~:248 sum to 210 s beyond the interval, plus 5 s startup/serialization), always capped by the absolute bind deadline. It is an engineering supervision constant with that derivation in a comment, never a quietness threshold and never a deadline extension. Local expiry of one observation → ERROR sample (`night_probe_error` on that sample; binding continues if time remains); global bind expiry → `night_refused_bind_expired` with an interrupted ERROR sample recorded. Do not change the global-expiry code (ruled).

7. **Whole-round cost.** `observer_cpu_s` must cover the WHOLE production round: worker interpreter startup, the census/hard-check workers, transport and journal work — measured by the parent from `rusage` deltas (`RUSAGE_CHILDREN` + self) across the round, not inside `sample_interval()`. The smoke CLI prints it; the lead runs it natively.

8. **Regressions (real workers, fake clock, external watchdog).** Run the actual supervisor in a disposable test process under an external wall-clock watchdog; workers are real subprocesses that acknowledge reaching their fault point over a separate control channel BEFORE the test advances fake time; production readiness, transport and cleanup are never replaced by fakes. Implement the consult's table, one test per row: blocking `join()` (startup-hang and post-publication-hang variants); blocking `recv()` (valid header + one byte, then stall); partial message (EOF after partial header; EOF after partial body); pre-send hang (local timeout → ERROR; separate late-start case where absolute expiry wins); post-send hang (result consumed once without EOF; group terminated; child reaped); exit without result (ERROR, never quiet); oversized message (length above cap rejected before allocation; byte flood bounded per tick); slow write (header/body chunks released at controlled fake times; no early acceptance; census timely; deadline fixed); journal block (writer blocked on a FIFO/barrier: ticker continues, expiry kills workers, GO impossible); descriptor leak / descendant survival (worker spawns a grandchild then hangs or exits: the grandchild cannot hold the result descriptor, cancellation reaches the group, reaping asserted). Revise regression 10's early-start hang expectation to local-timeout `night_probe_error` and add the late-start hang where global expiry wins; adjust regression 8's hang subcases (`tests/test_run_night.py` ~:4062, ~:4134, ~:4164, ~:4258) accordingly and say why; keep regressions 1, 2, 5, 8's deadline invariants.

9. **Mutant evidence.** For each row of the table, build the mutant in a `/tmp` copy, run the named test, and paste the failing assertion or the watchdog result; a row without executed evidence is reported as NOT EXECUTED, never as killed.

10. **Docs.** `docs/contracts/night_quiet_admission.md`: a short "Supervision" subsection stating the invariant, the transport protocol, the grace derivation, and the two failure codes (local vs global), glossed at first use; keep the Terms section first.

## Verification you must run and paste

- The six modules: `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4`; no test may exceed 10 s except the pre-existing FIFO test at `tests/test_run_night.py` ~:2731.
- `PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?`; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?`.
- The mutant table (item 9).
- `git diff --stat` and `git status --short` (unstaged; nothing outside WRITE_SCOPE).

## Report

claude-codex-report/v1 envelope under 8000 bytes: per item what changed and which test proves it; the mutant table; the bounded-work argument list (one line per surviving operation on the deadline path); any early return. No commits.
