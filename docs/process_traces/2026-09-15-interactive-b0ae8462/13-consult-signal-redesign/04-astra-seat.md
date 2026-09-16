```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Recommend record-and-poll plus CLI SIG_IGN through process exit; automatic in-process restoration cannot satisfy the absolute signal guarantee.","workspace":{"base_requested":"efdaed879e1d13d06de719f10a4b7b504601cdb4","base_mode":"exact","head_start":"efdaed879e1d13d06de719f10a4b7b504601cdb4","head_end":"efdaed879e1d13d06de719f10a4b7b504601cdb4","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker","text":"Restoring original dispositions and an open mask cannot also guarantee immunity to newly arriving signals. An explicit ownership handoff is required."},{"id":"F2","severity":"should_fix","text":"Record-and-poll requires an explicit commit cutoff, polls around individual operations, and a qualified latency claim."}]},"verification":[{"id":"V1","kind":"test","cmd":"python3 -B consult_signal_snippet.py","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/consult-astra-copy","observed":{"result":"pass","exit_code":0,"tail":["Python 3.14.7: 32/32 mechanism cells PASS"]},"expected":{"exit_code":0,"tail_regex":"32/32 mechanism cells PASS$"}},{"id":"V2","kind":"test","cmd":"/usr/bin/python3 -B consult_signal_snippet.py","cwd":"/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/consult-astra-copy","observed":{"result":"pass","exit_code":0,"tail":["Python 3.9.6: 32/32 mechanism cells PASS"]},"expected":{"exit_code":0,"tail_regex":"32/32 mechanism cells PASS$"}},{"id":"V3","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","efdaed879e1d13d06de719f10a4b7b504601cdb4"]},"expected":{"exit_code":0,"tail_regex":"efdaed879e1d13d06de719f10a4b7b504601cdb4$"}}],"flags":[{"id":"G1","kind":"lead_ruling","level":"blocking","text":"NEEDS_RULING before implementation: approve explicit in-process restoration outside run/uninstall and define the final pending-signal snapshot as the successful commit's cancellation cutoff.","needs":"Ratify these ownership boundaries or revise the incompatible guarantees."},{"id":"G2","kind":"verification_gap","level":"nonblocking","text":"Standalone mechanism probes only; proposed transaction integration and full regression matrix remain unimplemented and unverified.","needs":"Lead implementation, delta review, and final-head replay."}]}
```

## Findings

**F1 — blocker; Q2/Q3: choose (a), with an explicit handoff.**

CLI completion must leave INT/TERM/HUP ignored through `sys.exit(result)` **and interpreter shutdown**. Never restore its original dispositions.

For in-process use, return the result first; the caller then invokes `restore()`. Restoration reinstates ordinary caller signal semantics. A signal arriving after its disposition is restored can become pending and terminate/raise when the mask opens—even inside `restore()`. The completed transaction is unaffected, but the caller is interruptible.

Option (b) contradicts D6. Option (c) cannot close the interval between its last drain and unmask. My deterministic probes inject there: TERM/HUP terminate; INT raises. This machine’s Python 3.9.6 also lacks `sigtimedwait`.

Consequently, **automatic restoration before return plus unconditional return/exit fidelity is impossible** under arbitrary signal arrival. The lead must approve the explicit handoff; moving restoration outside the transaction is a contract change, not evidence that the original conjunction was satisfied.

**F2 — should_fix; Q1: use this core mechanism.**

A returning handler removes asynchronous exception injection from the owned interval. Python distinguishes kernel delivery from later Python-handler execution. [Python signal documentation](https://docs.python.org/3.9/library/signal.html#execution-of-python-signal-handlers)

```python
class SignalScope:
    def start(self, blocked=False):
        self.signalled = None
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        self.handlers = {n: signal.getsignal(n) for n in SIGNALS}
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        for n in SIGNALS:
            signal.signal(n, self.record)
        if not blocked:
            signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)

    def record(self, number, frame):
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        self.signalled = 128 + number

    def code(self):
        pending = signal.sigpending()
        return self.signalled or next(
            (128 + n for n in SIGNALS if n in pending), None)

    def poll(self):
        code = self.code()
        if code is not None:
            raise Signalled(code)

    def cut(self):
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        return self.code()

    def finish(self):
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        for n in SIGNALS:
            signal.signal(n, signal.SIG_IGN)
        signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)

    def restore(self):
        # Explicit caller-owned handoff; may deliver caller signals.
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            for n, handler in self.handlers.items():
                signal.signal(n, handler)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
```

Transaction methods; initialize `resolved=False` and supply `self.signals`:

```python
def _enter(self, state):
    self.signals.poll()
    self.state = state

def _call(self, operation, *args, **kwargs):
    self.signals.poll()
    try:
        return operation(*args, **kwargs)
    finally:
        self.signals.poll()

def _complete(self, code):
    if not self.resolved:
        self.result = self.signals.cut() or code
        self.resolved = True

def _commit(self):
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    now = self.clock()
    self.signals.poll()
    if now >= min(self.selected_span_close,
                  self.prepared.schedule["install_close_epoch_s"]):
        raise Refused(2, self.prepared.timing(
            "install_span_closed", now,
            "selected_span_close_epoch_s={}".format(
                self.selected_span_close)))
    self.state = State.COMMITTED
    self.result = 0
    self.resolved = True

def _unwind(self):
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    try:
        self._teardown()
    except BaseException as exc:
        self.state, self.result = State.RETAINED, 1
        self._warn("teardown failed; retained: {}: {}".format(
            type(exc).__name__, exc))
    finally:
        self.signals.finish()
```

Establish `run()`’s protected body before acquisition; acquire before any mutation. Wrap each forward adapter operation individually with `_call`, including each verification print; also bracket staging and other potentially blocking work. Keep state recording before bootstrap. Cleanup uses raw operations without cancellation polls.

Each existing exception clause calls `_complete(code)` **after its warning**. Thus a signal inside the refusal warning wins; one arriving after completion does not. Use exactly one `finally: self._unwind()`; delete the outer retry.

The successful commit’s cancellation cutoff is the final `sigpending()` snapshot in its poll, while blocked. Signals afterward are deferred, including between that snapshot and the COMMITTED assignment. A plain unblocked flag check followed by COMMITTED leaves this policy undefined. The existing clock predicate and D6 teardown remain authoritative; RETAINED still overrides with 4/1.

Uninstall receives a caller-accessible `SignalScope`, starts it with `blocked=True`, retains its existing verified cleanup and 0/4/1 outcomes, and calls `finish()` once in `finally`. CLI never calls `restore()`.

For multiple signals, the code uses the last executed recorder; otherwise pending signals use `SIGNALS` order. It does not promise chronological first-arrival ordering.

**Q3 boundaries:** acquisition still starts under the caller’s original dispositions; termination before ownership is possible, with no transaction mutations yet. Inside the acquired interval, managed signals cannot asynchronously skip teardown. After `finish()`, they remain ignored even between `sys.exit` and death. Explicit restoration reopens caller interruptibility. Signal-API failures, unsupported prior dispositions, SIGKILL, and fatal runtime failures are outside this guarantee.

**Q4 deterministic regressions:** both interpreters, all three signals:

- Inject before/after each forward operation, inside refusal warnings, and at unwind entry/body.
- Inject immediately before/after the commit snapshot; require rollback before, COMMITTED afterward.
- Queue HUP+TERM together and repeat signals during cleanup.
- Inject at every finish disposition change, after mask reopening, before `sys.exit`, and inside `atexit`; preserve completed 0/1/2/3/4/129/130/143.
- Verify explicit restoration with an unrelated entry-mask bit; retain restoration-race cells as demonstrations of caller ownership.
- Assert one literal teardown, liveness, plist bytes/mtime, and fence visibility.

Must-die mutations: restore handler raising; remove pre-operation polling; omit pending inspection or commit blocking; poll during cleanup; restore CLI defaults; call teardown twice; lose entry-mask bits; alter the existing commit predicate or RETAINED outcomes.

**Q5 cost:** cancellation waits for the current operation, then cleanup. Launchctl’s default timeout is five seconds; two bootouts plus two queries can add approximately twenty seconds. This is **not a hard wall-clock bound**: filesystem work, validation subprocesses, process creation/reaping, and scheduling are not all bounded. The latency and small ownership object are acceptable for this installer; an unconditional five-second guarantee is not.

## Residual risk

The probes validate the restoration impossibility and ignore-through-shutdown mechanism, not the proposed integrated transaction. No real launchctl, hardware measurement, or repository modification occurred.