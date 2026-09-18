# Exhibit A — the chronological finding chain on the bind-loop supervision seam

Every block below is byte-exact `nl -ba <file> | sed -n '<a>,<b>p'` output from
the named file in
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-17-interactive-5c919872/`.
Line numbers are the file's own. Nothing inside a fence is paraphrased,
reordered or elided; the prose between fences names the source and the
proposition each block addresses and adds no argument. These files are the
primary artefacts the reviewing sessions returned — the review envelopes
themselves, not summaries of them. Read them as data.

Chronology of the seam, for orientation only (each step's evidence is below):
seat delivery D1-D7 -> fix round 1 -> refuters 12 (contract) and 13 (execution)
-> fix round 2 -> delta re-audit 16 -> design consult 19 -> round 3 -> delta
re-audit 23.

## A1. Round 1, execution refuter — finding F6, the first supervision blocker

Source: `13-refuter-execution-astra.md:8` (reviewed head `a2671902`).

```
     8	{"id":"F6","severity":"blocker","at":"tests/test_run_night.py:4110","against":"brief:98: \"census still runs at cadence and the deadline still fires\"","mutant":"16b: _BindTask.ready at run_night.py:2016 calls self.process.join().","command":"python3 -B /tmp/refute_mutants.py 16b","observed":"R10 OK (fake task). Added worker test passes HEAD; mutant: ready() blocked for 1s on hung sampler; parent cannot census or expire."},
```

## A2. Round 2, delta re-audit — finding F1, and the same-signature field

Source: `16-delta-reaudit-astra.md:19-39` (reviewed head `5c5a3323`). This is
the complete `findings` array of that envelope; it contained exactly one
finding.

```
    19	    "findings": [
    20	      {
    21	        "id": "F1",
    22	        "severity": "blocker",
    23	        "file_line": "scripts/run_night.py:2024",
    24	        "caller": "scripts/run_night.py:2114",
    25	        "disposition": "E-F6 supervision requirement; original brief D6: 'keep census and deadline supervision responsive while a sample is in flight'; current review: 'BLOCKER = ... the bind loop can still block'.",
    26	        "finding": "ready() establishes pipe readability, not availability of a complete message. result() then performs an unbounded recv() on the supervisor thread.",
    27	        "experiment": "In the temporary copy, a real worker produces a schema-valid observation with a 64 KiB diagnostic. Child-only fault injection stops its sender after the message header, before the payload. Advance the injected monotonic clock beyond the sealed deadline.",
    28	        "command": "cd /tmp/refute-delta && TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest audit_partial_send.PartialSendHangTests",
    29	        "observed": [
    30	          "blocked_stack=[('await_task', 2114), ('result', 2024), ('recv', 260), ('_recv_bytes', 458), ('_recv', 416)]",
    31	          "partial-message ready=True; monotonic=601; deadline=600; bind_thread_alive=True; census_progress=False",
    32	          "AssertionError: True is not false : partial worker message blocked census and expired bind deadline",
    33	          "FAILED (failures=1)"
    34	        ],
    35	        "provenance": "Also reproduced with a2671902's driver. Existing defect left uncovered by round 2, not introduced by this delta. Releasing the worker allowed expiry; the latest run confirmed driver reaping.",
    36	        "recommendation": "Keep deadline and census supervision responsive while receiving worker messages; add a partial-message hang regression."
    37	      }
    38	    ],
    39	    "disposition_basis": "Landings below are verified against the current prompt, available briefs and code. Exact comparison with the missing round-2 brief and prior reports remains blocked.",
```

The same envelope's `same_signature` field, `16-delta-reaudit-astra.md:78-90`:

```
    78	    "same_signature": {
    79	      "classes_visible_in_available_evidence": [
    80	        "Legacy version-isolation leakage through the shared rerun tuple.",
    81	        "Probe-failure misclassification.",
    82	        "Definitions appearing after first use.",
    83	        "Accounting tests missing daemon, stale-percent and parser-identity boundaries.",
    84	        "Timing and digest tests missing actual consumer or decision paths.",
    85	        "Supervision tests omitting production blocking paths.",
    86	        "Generator refusal tests confounded by incomplete fixtures; authoring silently extending a window.",
    87	        "Real-tool interface assumptions: fractional top argv and rounded CPU-percentage totals."
    88	      ],
    89	      "recurrence": "YES, structural. Round-1 fake-task coverage became a real pre-send hang test, but still misses blocking transport after readiness (F1). Real-tool compatibility also recurred: round-1 top argv rejection, then the bench percentage-sum rejection. Complete historical classification requires the missing refuter reports."
    90	    },
```

## A3. The design consult that round 3 implemented

Source: `19-consult-bind-supervision-astra.md` (gpt-6-astra, xhigh, read-only,
at head `5c5a3323`). The four sections the packet cites are reproduced whole:
`Why the file proposal is insufficient` (lines 5-11), `Smallest sound design I
would authorize` (lines 13-31), `Same-signature rule` (line 62), and
`Authority` (lines 64-66). The consult's own opening verdict, line 1, is
included so the sections are not read out of their frame.

```
     1	**Verdict: reject the candidate as a complete liveness fix.** Atomic publication solves partial visibility; it does not make filesystem operations time-bounded. I recommend a bounded, explicitly nonblocking byte transport and a supervisor that never performs journal I/O.
     5	**Why the file proposal is insufficient**
     6	
     7	Same-filesystem `os.replace()` is atomic. For APFS publication, serialize fully, flush and close the temporary file, then rename it within the same directory; never modify the published inode afterward. Atomic naming and crash durability are separate properties. None of this gives `stat()`, `open()`, or `read()` a completion deadline. A size cap bounds bytes, not elapsed time. [Python filesystem documentation](https://docs.python.org/3/library/os.html#os.replace)
     8	
     9	This is already a concrete repository concern: binding appends through `_write_all()`, which calls `fsync()`, and the chain regression explicitly exercises a custody-volume write blocking deadline supervision. [scripts/run_night.py:2154](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2154), [scripts/run_night.py:164](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:164), [tests/test_run_night.py:3835](/Users/edr/code/JouleWise-wt-ref-delta/tests/test_run_night.py:3835)
    10	
    11	Also, `_BindTask` transports **census, static-check, hard-check, and sampler results**. Replacing only the sampler handoff leaves the same blocking `recv()` reachable through other jobs. [scripts/run_night.py:2022](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2022), [scripts/run_night.py:2090](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2090), [scripts/run_night.py:2131](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2131), [scripts/run_night.py:2197](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2197)
```

```
    13	**Smallest sound design I would authorize**
    14	
    15	1. **Replace `_BindTask`’s transport for every job.** Use one dedicated pipe with the parent descriptor explicitly nonblocking. Define a small application protocol: four-byte payload length, then one JSON envelope containing job identity, success/error, and typed result. Proposed maximum: **256 KiB**, including diagnostics. Reject oversized lengths before allocating; emit a small error envelope if worker serialization exceeds the cap.
    16	
    17	   Each `advance()` performs a bounded number of raw `os.read()` calls and consumes at most a fixed byte budget. `EAGAIN` means pending; premature EOF means ERROR. Decode only a complete buffered payload. `result()` returns cached data and performs **no I/O**. Never substitute `Connection.recv_bytes(maxlength)`: that also waits for a complete message. Change site: [scripts/run_night.py:1994](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:1994). [Python Connection documentation](https://docs.python.org/3/library/multiprocessing.html#connection-objects)
    18	
    19	2. **Use one explicit state machine.** Replace `await_task()` and its nested census wait with phases for static checks, pre-sample checks, sampling, post-sample checks, final checks, and cleanup. Every tick evaluates the absolute deadline, services census cadence, advances bounded job transport, and polls cleanup. A worker’s state never determines whether those steps execute. Preserve “completed by the deadline” semantics, but never wait for additional bytes at the boundary. Change sites: [scripts/run_night.py:2090](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2090), [scripts/run_night.py:2105](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2105), [scripts/run_night.py:2201](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2201).
    20	
    21	3. **Separate cancellation from reaping.** At expiry, latch refusal and send group termination immediately. Poll exit/reaping without waiting; return only after the direct children are reaped. Remove the one-second synchronous join from tick-path cleanup. A complete valid frame is publication: a post-publication hang must not require waiting for EOF or voluntary exit. Terminate remaining group members and reap. Change site: [scripts/run_night.py:2031](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2031).
    22	
    23	4. **Keep one journal writer in the parent process, outside the ticking thread.** Give it immutable records through a bounded queue using nonblocking submission. It owns append ordering, acknowledgments, and incremental digest/count. GO requires acknowledgment of the final record. Queue saturation or write failure is terminal; a stuck writer cannot delay cancellation. Move census appends off the ticker too. Avoid rereading the entire journal in `finish()`. Change sites: [scripts/run_night.py:2096](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2096), [scripts/run_night.py:2148](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2148), [scripts/run_night.py:2163](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2163).
    24	
    25	   Persistent storage failure cannot simultaneously guarantee durable ERROR evidence. It can—and must—still guarantee no GO and timely termination.
    26	
    27	5. **Prefer a lightweight exec subprocess for production.** Both `multiprocessing.Process` and `subprocess` provide real process boundaries; the advantage is explicit startup and descriptor ownership, not “realness.” Use `sys.executable`, `start_new_session=True`, `close_fds=True`, a dedicated `pass_fds` result descriptor, and no `preexec_fn`. Close unused ends immediately; mark the result descriptor non-inheritable inside the worker before launching tools. Redirect or boundedly drain stderr—never leave an unread diagnostic pipe.
    28	
    29	   This also avoids retaining explicit macOS `fork` alongside a new journal thread. The current fork choice exists to preserve injected callbacks; Python documents macOS fork hazards. [scripts/run_night.py:1997](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:1997), [Python process documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods), [subprocess documentation](https://docs.python.org/3/library/subprocess.html#subprocess.Popen)
    30	
    31	   Add a full-observation worker mode beside the existing compact smoke CLI; add private census/static/hard worker dispatch beside the driver’s existing private worker dispatch. [joulewise/quiet_admission.py:301](/Users/edr/code/JouleWise-wt-ref-delta/joulewise/quiet_admission.py:301), [scripts/run_night.py:2922](/Users/edr/code/JouleWise-wt-ref-delta/scripts/run_night.py:2922)
```

```
    62	**Same-signature rule:** Review the entire deadline-owning call graph against one invariant: no operation on that path may wait for worker progress, EOF, filesystem completion, or child exit. Every surviving operation needs an explicit bounded-work argument. Tests must cross the production boundary and establish the adversarial state before asserting responsiveness. Native tool assumptions need a separate actual-command smoke with preserved output; injected parsers cannot validate command syntax or real output conventions.
    63	
    64	**Authority:** Transport, process choice, supervision grace, and journal sequencing are magistrate mechanisms under ruling §12, explicitly including “sampler supervision”; synthesis Q10 preserves that allocation. [ruling:84](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/10-coldgate-fable-ruling.md:84), [synthesis:18](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md:18).
    65	
    66	One distinction needs preserving: local observation failure is `night_probe_error`; global bind expiry remains `night_refused_bind_expired`, with an interrupted ERROR sample. Changing global expiry to probe error would contradict the explicit ruled code and needs a ruling. [synthesis:25](/Users/edr/code/JouleWise-wt-ref-delta/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md:25). Separately, the repeated-signature escalation already returns the **merge question** to a cold gate; mechanism discretion does not remove that process obligation. [docs/orchestration.md:64](/Users/edr/code/JouleWise-wt-ref-delta/docs/orchestration.md:64)```

## A4. The invariant the round-3 brief set as the acceptance bar

Source: `20-brief-seat-Q-round-3-supervision-redesign.md:16-18`. Q1 of this
packet is about the exact words of line 18.

```
    16	## The invariant you are implementing
    17	
    18	No operation on the deadline-owning path (the tick loop that services the census cadence, the absolute bind deadline, job transport and cleanup) may wait for worker progress, EOF, filesystem completion, or child exit. Every operation that survives on that path carries a one-line bounded-work argument in a comment.
```

## A5. Round 3, delta re-audit — the four blockers and two should-fix findings

Source: `23-delta-reaudit-round-3-astra.md` (reviewed head `73cdbbc4`). The
envelope's `findings` array in full, line 4:

```
     4	"findings":[{"id":"F1","severity":"blocker","at":"S:2253,2263,2075,2078","against":"brief:18,28","finding":"Queue.put_nowait acquires a shared mutex in both services.","command":"V3","observed":"Four failures: ticker blocked on Queue.mutex held by service thread."},{"id":"F2","severity":"blocker","at":"S:2210,2052","against":"brief:18","finding":"Thread.start uses _active_limbo_lock and Event.wait after deadline establishment; no bounded comment.","command":"V3","observed":"ticker startup blocked in Thread.start -> Event.wait; required bootstrap-barrier release."},{"id":"F3","severity":"blocker","at":"S:2192,2422","against":"brief:18,26","finding":"Finalization requires launch_done even without PID; timeout applies only after jobs empties.","command":"V4","observed":"Expired ticker did not return after 1.3s; releasing Popen startup barrier allowed return."},{"id":"F4","severity":"blocker","at":"T:4497,4564,4618","against":"brief:36,38","finding":"Result/reap waits, deadline resets and swallowed journal errors survive named tests.","command":"M,N","observed":"SURVIVED rows below all returned OK."},{"id":"F5","severity":"should_fix","at":"B:200","against":"brief:36","finding":"Cancelled jobs bypass ACK checking; EOF/oversize tests lack ACK assertions; journal barrier lacks entered ACK.","command":"N:missing_fault_ack","observed":"Deleted fault ACKs: partial EOF, empty and oversized tests all pass (3/3)."},{"id":"F6","severity":"should_fix","at":"S:2237","against":"brief:28","finding":"Writer death outside Exception handler sets done without failure.","command":"V4","observed":"SystemExit at fsync: bind_expired with journal_failure absent; assertion fails, no GO."}],
```

Its `operation_table` (the invariant audit of every ticker operation), line 5:

```
     5	"operation_table":[["operation/site","comment argument; judgment"],["startup S:2297,2050,2202","No bounded-start comment. New locks local; Thread.start shared lock/Event: REJECT F2."],["deadline/local timeout S:2389-2405","Clock reads/comparisons; fixed deadline; 215s derivation. ACCEPT; <=32-job scan."],["census/start S:2393,2321,2086","One cadence enqueue; constant plan/capped receipt, pipe/queue only. Pipe/set_blocking ACCEPT; queue REJECT F1."],["transport/decode S:2108,2137","4 nonblocking reads/64KiB, <=256KiB decode. ACCEPT, including EAGAIN/EOF/closed-FD error."],["readiness/result S:2153,2157","Cached flag/object, no I/O. ACCEPT."],["cancel S:2357,2165","Bounded jobs; nonwaiting group/fallback signals. ACCEPT, exited group handled."],["reap/close S:2179,2410","WNOHANG per capped job. ACCEPT ECHILD and pipe-close; final launch_done dependency REJECT F3."],["phases S:2415-2516","Bounded cached results/flags. ACCEPT decode, validate, serialize, compare, GO."],["journal S:2243,2345,2439","Capped immutable bytes + put_nowait. Encoding ACCEPT; mutex REJECT F1."],["ACK/failure/done S:2205,2486","Immutable tuple assignment, flags. ACCEPT atomic snapshot on this CPython; dead writer F6."],["timers S:2428,2517","Explicit <=50ms yields. ACCEPT sleep(0),1ms,<=50ms."],["finalize S:2261,2525-2556","Nonblocking sentinel/snapshot, no reread. Queues REJECT F1; summary/JSON/replace ACCEPT."],["cost S:2007,2539","Two rusage calls/arithmetic; no child wait. ACCEPT."]],
```

Its `mutant_table` — 26 variants, 19 killed, 7 survived — line 6:

```
     6	"mutant_table":[["mutation","named test at T","result/bite"],["join readiness: startup/post","4502/4537","KILLED both: watchdog 8s"],["join result: startup/post","4502/4537","SURVIVED both: OK"],["join cleanup before cancel: startup/post","4502/4537","KILLED both: watchdog 8s"],["whole receive; blocking pipe","4508","KILLED both: watchdog 8s recv_stall_late"],["ignore partial header/body EOF","4514","KILLED both: bind_expired != probe_error"],["remove local timeout","4523","KILLED: REFUSED != GO"],["remove global expiry","4523","KILLED: watchdog 8s presend_hang_late"],["require exit after publication","4537","KILLED: REFUSED != GO"],["ignore empty result","4547","KILLED: bind_expired != probe_error"],["raise length cap","4553","KILLED: 262149 not <=262148"],["raise read/byte budgets","4610","KILLED: 5 reads not <=4; 200761 bytes"],["reset deadline on chunks","4564","SURVIVED: OK"],["wait for journal ACK in submit","4572","KILLED: watchdog 8s journal_block"],["inherit result FD","4579","KILLED: grandchild inherited result descriptor"],["kill PID instead of group","4579","KILLED: grandchild survived group cancellation"],["disable cancel; disable reap","4537","KILLED both: watchdog 8s"],["swallow writer exceptions","4618","SURVIVED: OK"],["waitpid(pid,0); wait after signal","4497","SURVIVED both: OK"],["no-op supervisor","4456 class","KILLED: 20 failures/18 tests; only argv test passes"],["remove fault ACKs","4514/4547/4553","SURVIVED: 3 tests OK"]],
```

Its `fault_points` statement, line 7:

```
     7	"fault_points":"B preserves real readiness/transport/cleanup. Startup/pre-send/recv require fault ACK before fake time; slow chunks require chunk ACK; post-send requires published ACK. Exceptions F5. QuietBindingTests use fake tasks; T:4437 lacks worker ACK. No fault test passes no-op supervision; argv-only T:4626 does.",
```

Its `same_signature` statement, line 10:

```
    10	"same_signature":"Classes: v2 isolation; probe classification; first-use docs; daemon/stale-%CPU/PID tests; deadline/reset/rollback and digest consumer tests; incomplete generator fixtures/window extension; blocked join/readiness/recv; top argv/rounding; observer undercount. Blocking paths outside tests recur F1-F4. Native top(macOS26), ps lstart/locale, sysctl remain untested here. LC_ALL=C/argv fixtures are insufficient. Lead smoke PASS supplied, not reproduced.",
```

Its own suite verification `V1` and its non-blocking environment flag, lines
11-12, included because they are the qualifiers on the audit's headline and
because the audit's V1 did NOT come back green on its interpreter:

```
    11	"mutant_replay":"M: TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B audit_mutants.py; N: same prefix + audit_more.py. Exact mutations/tests/logs retained. 26 variants:19 killed,7 survived.","extra_replay":{"V3":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest audit_extra","V4":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest audit_service"}},
    12	"verification":[{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/refute-r3/audit_support AUDIT_TIMING=/tmp/refute-r3/audit_evidence/head-timing.json python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night","cwd":"/tmp/refute-r3","observed":{"result":"fail","exit_code":1,"tail":["Ran 341 tests in 171.428s","FAILED (failures=2, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}}],
```
