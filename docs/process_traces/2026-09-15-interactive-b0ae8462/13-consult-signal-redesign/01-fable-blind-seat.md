# Blind Fable seat — record-and-poll for the transactional installer (`efdaed87`)

Probed under 3.14.7 and 3.9.6 (`consult-fable-copy/probe_rp.py`, `probe_exit.py`): record-only handler during `subprocess.run` (PEP 475 retry, poll raises 143); two back-to-back signals (first wins, no raise); SIG_IGN discards a self-kill; a process ignoring INT/TERM/HUP exits with its `sys.exit` code after a self-kill.

## Q1 — the mechanism

Principle: **no asynchronous exception, and no mask.** Every seam in A/B was a bytecode boundary where a raise could land; a handler that cannot raise has none, and 3.9-vs-3.14 eval-breaker placement stops mattering. The block in the consult's sketch buys nothing once the handler cannot raise (the disposition is always `record` or `SIG_IGN`, so delivery is harmless at every instruction) and it is what manufactured F1 (pending under the block, delivered at `SIG_SETMASK`). Drop it; D6's "masked for the whole unwind" becomes "uninterruptible by construction".

```python
SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)

class Signalled(BaseException):          # raised ONLY by Shield.poll, from ordinary code
    def __init__(self, code): self.code = code

class Shield:
    """Owns the three dispositions for one transaction. Never touches the mask."""
    def __init__(self):
        self.saved, self.signalled = {}, None
    def install(self):
        def record(number, frame):      # may run anywhere; never raises
            if self.signalled is None:
                self.signalled = 128 + number
        for number in SIGNALS:
            self.saved[number] = signal.getsignal(number)
            signal.signal(number, record)
    def poll(self):
        if self.signalled is not None:
            raise Signalled(self.signalled)
    def quiesce(self):
        """Result complete: discard anything deferred, ignore anything later."""
        for number in self.saved:
            signal.signal(number, signal.SIG_IGN)   # POSIX: discards pending instances
    def release(self):
        """In-process callers only. main() never calls it."""
        for number, handler in self.saved.items():
            signal.signal(number, handler)
        self.saved.clear()
```

Poll points — every state boundary and every mutation:

```python
def _enter(self, state):
    self.shield.poll()                  # signal since the last boundary → Signalled, rollback
    self.state = state
# run(): self.shield.poll() before EACH write_plist; bootstrap/print follow an _enter
def _commit(self):
    self.shield.poll()                  # the LAST poll; anything recorded after it is discarded
    now = self.clock()
    if now >= min(...): raise Refused(2, ...)
    self._enter(State.COMMITTED)        # _enter polls again first: same instant, harmless
```

Unwind and `run()`:

```python
def _unwind(self):                      # ordinary code; nothing in this frame can be interrupted
    try:
        self._teardown()
    except BaseException as exc:
        self.state, self.result = State.RETAINED, 1
        self._warn("teardown failed; retained: {}: {}".format(type(exc).__name__, exc))
    finally:
        self.shield.quiesce()           # dispositions → SIG_IGN; no mask call exists

def run(self):
    self.shield.install()               # at entry: nothing in run() ever sees a raising disposition
    try:
        ...body unchanged, with polls above...
        self._commit(); self._say(self.prepared.pins)   # BrokenPipe handling as today
    except Refused as exc:
        self.result = exc.code; self._warn(str(exc))
    except Signalled as exc:
        self.result = exc.code
    except BaseException as exc:
        self.result = 1; self._warn("{}: {}".format(type(exc).__name__, exc))
    finally:
        self._unwind()
    return self.result

def uninstall(adapter, stderr=None, shield=None):
    shield = shield or Shield(); shield.install()       # no polls: bootout→verify→delete is one step
    try:  ...today's body...
    except BaseException as exc: ...return 1
    finally: shield.quiesce()
```

`main()` unchanged: `sys.exit(main())`, no `release()`. `raised_once`, `resolved`, `entry_mask`, the outer `except Signalled`, the `while True` loop and the `KeyboardInterrupt` clause all go. Install at entry rather than STAGED (D5): closes the untested pre-STAGED escape where Ctrl-C lands in `except Refused`'s `_warn` under `default_int_handler`; SIGTERM during validate exits 143, state REFUSED, nothing written.

Seam closure: P1/P1b, entry, P2, P3, (b)–(d), (f)–(k): closed — no raise exists to land. F1/(e): closed for the CLI — after `quiesce()` the three are ignored until death; a deferred signal is discarded, a later one never delivered. A signal recorded after a refusal fixed `self.result` is discarded: the refusal code stands (both roll back identically; documented).

Latency: one adapter call + its 5 s timeout; during validate, the preflight subprocess (terminal Ctrl-C reaches the child too); during teardown, not honoured (≤ 4 launchctl calls ≈ 20 s worst).

## Q2 — after completion: rule (a), amended: no mask, no drain

(c) is a TOCTOU: `sigpending` and `SIG_SETMASK` are two syscalls; a signal between them runs the original disposition. (b) makes exit 143 lie ("rolled back") while both jobs are loaded — the handback would retire a live night. (a) is the only option under which a completed result cannot be replaced, and its window is flush + finalisation, milliseconds. Code: `quiesce()`/`release()` above. Behavioural change: Ctrl-C after COMMITTED gives exit 0 and the pins, not 130.

## Q3 — remaining boundaries, honestly

1. **SIGKILL/SIGQUIT**: no teardown; the `.prior` sidecars make the next install refuse (exit 3) — unchanged, by design.
2. **Stalled stdout after COMMITTED**: `_say` blocks on a full pipe with TERM ignored; only SIGKILL frees it (today the raise freed it, losing the pins). Handback pipes drain.
3. **Between `sys.exit` and death**: the three are ignored, the code cannot change; SIGKILL → 137, which never claims rollback.
4. **In-process callers**: SIG_IGN from `quiesce()` until `release()` (test base class releases in `tearDown`); after `release()` a signal runs the caller's own disposition, the result already returned. The mask is never touched: (ii)'s mask clause is impossible.
5. **Commit race**: a signal between `_commit`'s poll and COMMITTED is discarded; one bytecode earlier it rolls back. Both documented.
6. **Caller-blocked pending signal at entry**: never delivered to us, survives `release()` untouched.
7. **Threads**: none; a helper thread's delivery would still only record.

## Q4 — deterministic cells (both interpreters × {INT,TERM,HUP}; fake-adapter hook `kill_in(verb, label)` does `os.kill(getpid(), sig)` inside the verb)

1. `write_plist`(night) → caught before the deadman write → ROLLED_BACK, rc 143/130/129, priors byte+mtime restored, fence `None`.
2. `bootstrap`(night) → `_enter(DEADMAN_LOADED)` → `verified_bootout` both → ROLLED_BACK.
3. last verification `print` → `_commit` polls → rollback from VERIFIED.
4. `clock` hook (after `_commit`'s poll) → COMMITTED, rc 0, pins printed.
5. stdout wrapper during the pins print → rc 0.
6. `_warn` inside `except Refused` (P2) → refusal code, ROLLED_BACK, one teardown.
7. `bootout` during teardown; wrapper at `_unwind`'s first statement → rc = original code, `_teardown` called exactly once (G1 resolved).
8. TERM then HUP in one hook → 143, one teardown.
9. wrapper around each `signal.signal` call of `quiesce` (F1 shape) → rc unchanged; after `release()`, `getsignal` == originals.
10. child-process CLI cell: wrapper kills after `run()` returns, before `sys.exit` → child status 0 (COMMITTED) / 3 (refusal), never −15.
11. uninstall: kill in `bootout`, `print`, `remove_plist` → rc 0, plists gone; `shield` passed by the test, released.
12. kill in the validate callable → rc signal, state REFUSED, nothing written, no launchctl call.
13. `pthread_sigmask(SIG_BLOCK, ())` equals entry in every cell; `release()` twice is a no-op.

Must-die: handler raises → 6/7/8 RED; delete any one poll → its cell RED (each poll has exactly one cell only it catches); delete `quiesce` → 9/10 RED; `main()` calls `release()` → 10 RED; add any `pthread_sigmask` call → 13 RED (pin the absence: `grep -c pthread_sigmask == 0`); `_commit` polls after the clock read → 4 RED; install at STAGED → 12 RED.

## Q5 — cost

Latency rises from "next bytecode" to "next poll": ≤ 5 s in a launchctl call, the preflight's runtime during validate, ~20 s worst in teardown. Invisible for an installer that runs seconds inside a multi-hour window; the night gains a handler that cannot escape, a restore order that cannot be wrong, and ~40 fewer lines (two flags, the outer catch, the retry loop, every mask call). Document: post-COMMITTED signals ignored (exit 0 stands); Ctrl-C during validate costs the preflight's runtime. Acceptable. I would not keep the mask even as belt-and-braces: it is the one mechanism in six rounds that ever manufactured a window.
