**Verdict: reject the candidate as a complete liveness fix.** Atomic publication solves partial visibility; it does not make filesystem operations time-bounded. I recommend a bounded, explicitly nonblocking byte transport and a supervisor that never performs journal I/O.

Verified at detached HEAD `5c5a3323`, with a clean worktree. The named `13-refuter-execution-astra.md` and `16-delta-reaudit-astra.md` are absent here; their execution findings are supplied evidence, not independently reproduced. No files were written or tests run.

**Why the file proposal is insufficient**

Same-filesystem `os.replace()` is atomic. For APFS publication, serialize fully, flush and close the temporary file, then rename it within the same directory; never modify the published inode afterward. Atomic naming and crash durability are separate properties. None of this gives `stat()`, `open()`, or `read()` a completion deadline. A size cap bounds bytes, not elapsed time. [Python filesystem documentation](https://docs.python.org/3/library/os.html#os.replace)

This is already a concrete repository concern: binding appends through `_write_all()`, which calls `fsync()`, and the chain regression explicitly exercises a custody-volume write blocking deadline supervision. [scripts/run_night.py:2154](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2154), [scripts/run_night.py:164](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:164), [tests/test_run_night.py:3835](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:3835)

Also, `_BindTask` transports **census, static-check, hard-check, and sampler results**. Replacing only the sampler handoff leaves the same blocking `recv()` reachable through other jobs. [scripts/run_night.py:2022](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2022), [scripts/run_night.py:2090](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2090), [scripts/run_night.py:2131](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2131), [scripts/run_night.py:2197](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2197)

**Smallest sound design I would authorize**

1. **Replace `_BindTask`’s transport for every job.** Use one dedicated pipe with the parent descriptor explicitly nonblocking. Define a small application protocol: four-byte payload length, then one JSON envelope containing job identity, success/error, and typed result. Proposed maximum: **256 KiB**, including diagnostics. Reject oversized lengths before allocating; emit a small error envelope if worker serialization exceeds the cap.

   Each `advance()` performs a bounded number of raw `os.read()` calls and consumes at most a fixed byte budget. `EAGAIN` means pending; premature EOF means ERROR. Decode only a complete buffered payload. `result()` returns cached data and performs **no I/O**. Never substitute `Connection.recv_bytes(maxlength)`: that also waits for a complete message. Change site: [scripts/run_night.py:1994](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:1994). [Python Connection documentation](https://docs.python.org/3/library/multiprocessing.html#connection-objects)

2. **Use one explicit state machine.** Replace `await_task()` and its nested census wait with phases for static checks, pre-sample checks, sampling, post-sample checks, final checks, and cleanup. Every tick evaluates the absolute deadline, services census cadence, advances bounded job transport, and polls cleanup. A worker’s state never determines whether those steps execute. Preserve “completed by the deadline” semantics, but never wait for additional bytes at the boundary. Change sites: [scripts/run_night.py:2090](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2090), [scripts/run_night.py:2105](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2105), [scripts/run_night.py:2201](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2201).

3. **Separate cancellation from reaping.** At expiry, latch refusal and send group termination immediately. Poll exit/reaping without waiting; return only after the direct children are reaped. Remove the one-second synchronous join from tick-path cleanup. A complete valid frame is publication: a post-publication hang must not require waiting for EOF or voluntary exit. Terminate remaining group members and reap. Change site: [scripts/run_night.py:2031](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2031).

4. **Keep one journal writer in the parent process, outside the ticking thread.** Give it immutable records through a bounded queue using nonblocking submission. It owns append ordering, acknowledgments, and incremental digest/count. GO requires acknowledgment of the final record. Queue saturation or write failure is terminal; a stuck writer cannot delay cancellation. Move census appends off the ticker too. Avoid rereading the entire journal in `finish()`. Change sites: [scripts/run_night.py:2096](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2096), [scripts/run_night.py:2148](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2148), [scripts/run_night.py:2163](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2163).

   Persistent storage failure cannot simultaneously guarantee durable ERROR evidence. It can—and must—still guarantee no GO and timely termination.

5. **Prefer a lightweight exec subprocess for production.** Both `multiprocessing.Process` and `subprocess` provide real process boundaries; the advantage is explicit startup and descriptor ownership, not “realness.” Use `sys.executable`, `start_new_session=True`, `close_fds=True`, a dedicated `pass_fds` result descriptor, and no `preexec_fn`. Close unused ends immediately; mark the result descriptor non-inheritable inside the worker before launching tools. Redirect or boundedly drain stderr—never leave an unread diagnostic pipe.

   This also avoids retaining explicit macOS `fork` alongside a new journal thread. The current fork choice exists to preserve injected callbacks; Python documents macOS fork hazards. [scripts/run_night.py:1997](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:1997), [Python process documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods), [subprocess documentation](https://docs.python.org/3/library/subprocess.html#subprocess.Popen)

   Add a full-observation worker mode beside the existing compact smoke CLI; add private census/static/hard worker dispatch beside the driver’s existing private worker dispatch. [joulewise/quiet_admission.py:301](/Users/edr/code/JouleWise-wt-ref-delta/joulewise/quiet_admission.py:301), [scripts/run_night.py:2922](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2922)

**Grace and cost**

I would initially use **interval + 215 seconds**, capped by the absolute bind deadline: seven existing command allowances contribute 210 seconds beyond the sampling interval, plus a proposed five-second startup/serialization allowance. This is conservative, not measured latency evidence. A five-second *total* grace would silently impose a much tighter whole-job limit than the existing command bounds. The seven calls and their bounds are visible in [joulewise/quiet_admission.py:248](/Users/edr/code/JouleWise-wt-ref-delta/joulewise/quiet_admission.py:248).

Keep that allowance an engineering supervision constant, never a quietness threshold or deadline extension. Measure before tightening it.

The cost gate must measure the **whole production round**, including interpreter startup, independent census/hard checks, transport and journal work. The existing `observer_cpu_s` starts inside `sample_interval()` and ends before return, so it cannot establish that total. [joulewise/quiet_admission.py:243](/Users/edr/code/JouleWise-wt-ref-delta/joulewise/quiet_admission.py:243), [joulewise/quiet_admission.py:285](/Users/edr/code/JouleWise-wt-ref-delta/joulewise/quiet_admission.py:285). I cannot certify the 0.2–0.3 cpu-s target from this read-only review.

**Mutant-kill plan**

Run the actual supervisor in a disposable test process with an external wall-clock watchdog. Use real workers and separate control-channel acknowledgments proving each worker reached its fault point **before advancing fake time**. Otherwise the fake clock can outrun process startup. Never replace production readiness, transport, or cleanup with fake implementations.

| Mutant / fault | Real-worker test | Required assertion |
|---|---|---|
| Blocking `join()` in readiness/result/cleanup | Worker acknowledges startup, then hangs; repeat after full publication | Watchdog remains untriggered; census ticks continue; cancellation happens at the prescribed fake time |
| Blocking `recv()` | Worker writes a valid length header and one byte, then stalls | No whole-message receive; ticks continue |
| Partial message | EOF after partial header and, separately, partial body | Immediate `night_probe_error`; one ERROR attempt; no GO |
| Pre-send hang | Worker acknowledges fault point, emits nothing | Local timeout produces ERROR; separate late-start case proves absolute bind expiry |
| Post-send hang | Complete valid frame, worker remains alive | Result consumed once without EOF; group terminated and direct child reaped |
| Exit without file/result | Worker exits without publishing any frame | ERROR, never quiet |
| Oversized file/message | File transport is eliminated; publish length exceeding cap, then flood bytes | Reject before oversized allocation; bounded work per tick |
| Slow write | Release individual header/body chunks at controlled fake times | No early acceptance; census remains timely; fixed deadline never resets |
| Journal block | Block real writer on a FIFO/barrier | Ticker continues; expiry kills workers; GO remains impossible |
| Descriptor leak / descendant survival | Worker starts a child and exits or hangs | Child cannot retain result transport; cancellation reaches the group; reaping assertion passes |

These kill specified mutants, not every imaginable blocking implementation. Execute each mutation and retain its failing assertion/watchdog result.

Keep regressions 1, 2, 5 and 8’s deadline invariants. Revise regression 10’s early-start hang expectation to local-timeout `night_probe_error`; add a late-start hang where global expiry wins. Regression 8’s hang-based subcases likewise need adjustment because they currently expect the hang to survive until 600 seconds. [tests/test_run_night.py:4062](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:4062), [tests/test_run_night.py:4134](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:4134), [tests/test_run_night.py:4164](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:4164), [tests/test_run_night.py:4258](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:4258).

**Same-signature rule:** Review the entire deadline-owning call graph against one invariant: no operation on that path may wait for worker progress, EOF, filesystem completion, or child exit. Every surviving operation needs an explicit bounded-work argument. Tests must cross the production boundary and establish the adversarial state before asserting responsiveness. Native tool assumptions need a separate actual-command smoke with preserved output; injected parsers cannot validate command syntax or real output conventions.

**Authority:** Transport, process choice, supervision grace, and journal sequencing are magistrate mechanisms under ruling §12, explicitly including “sampler supervision”; synthesis Q10 preserves that allocation. [ruling:84](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/10-coldgate-fable-ruling.md:84), [synthesis:18](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md:18).

One distinction needs preserving: local observation failure is `night_probe_error`; global bind expiry remains `night_refused_bind_expired`, with an interrupted ERROR sample. Changing global expiry to probe error would contradict the explicit ruled code and needs a ruling. [synthesis:25](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md:25). Separately, the repeated-signature escalation already returns the **merge question** to a cold gate; mechanism discretion does not remove that process obligation. [docs/orchestration.md:64](/Users/edr/code/JouleWise-wt-ref-delta/docs/orchestration.md:64)