# Opus seat — record-and-poll redesign (blind three-seat consult, cold-gate 06 Q3)

**Verdict.** Ship record-and-poll, and go further: the handler records ONE int and touches nothing else — no
`pthread_sigmask` anywhere in the module. Delete `Signalled`-from-handler, `raised_once`, `resolved`, the outer
`except Signalled`, the `while True` loop, `entry_mask`. Q2 = **(a)**: the CLI never re-installs the originals. All
probes ran in the authorized copy under both `python3` 3.14.7 and `/usr/bin/python3` 3.9.6.

## Q1 — the code

```python
    def _install_handlers(self):                      # FIRST statement of run()/uninstall()
        # Single-threaded. Records one integer: never raises, never changes the mask, never calls
        # back. Not raising means PEP 475 auto-retries any syscall it interrupts (P5: SIGTERM 0.3 s
        # into a 1.2 s adapter call -> the call returns rc=0 and the signal is recorded).
        def record(number, frame):
            if self.signalled is None:                # first signal wins; repeats idempotent
                self.signalled = 128 + number
        for number in SIGNALS:
            self.handlers[number] = signal.getsignal(number)
            signal.signal(number, record)

    def _poll(self):
        if self.signalled is not None:
            raise Signalled(self.signalled)           # raised from ORDINARY code, inside the try

    def _enter(self, state):
        self._poll()                                  # every state boundary
        self.state = state

    def _commit(self):
        ...existing predicate...
        self._poll()                                  # THE LATCH — last statement before the assignment
        self.state = State.COMMITTED

    def _unwind(self):
        try:
            self._teardown()                          # NEVER polls: teardown must not abort
        except BaseException as exc:
            self.state, self.result = State.RETAINED, 1
            self._warn("teardown failed; retained: {}: {}".format(type(exc).__name__, exc))
        finally:
            for number in self.handlers:              # discards pending, ignores anything new
                signal.signal(number, signal.SIG_IGN)

    def restore_signals(self):                        # in-process callers only; the CLI never calls it
        for number, handler in self.handlers.items():
            signal.signal(number, handler)
```

`run()` keeps its inner try/except/`finally: self._unwind()` and `return self.result`; the outer `except Signalled`
(`:509-517`) is **deleted** — nothing asynchronous exists to catch. Polls: handlers first, `_enter` at every
boundary, plus an explicit `_poll()` before each `write_plist`, each `bootstrap`, the verify `print`, and in
`_commit`. `uninstall()` takes the same shape, **no mask calls**.

**Restoration order**: there is none to get wrong. Dispositions go `record → SIG_IGN`; neither can kill or raise,
so no instant needs a mask. Blocking is not just unnecessary but harmful: P5 shows a blocked mask is **inherited by
every launchctl child** (`child inherited blocked mask: [1, 2, 15]`) — today's handler makes the subprocess it is
about to spawn unkillable.

**Seams closed?** The async-raise class (A/B seams a, b, c, d, f, g, i; ruling 10's P1–P3) is closed by construction:
no exception originates in a handler, so no frame is entered non-locally. Seam (e) / exhibit A **F1 is NOT closed by
record-and-poll** — it is a restoration defect, closed by Q2(a). Seam matrix (`p7_cell.py`: structural replica of the
state machine, `os.kill` at 19 named seams × 3 signals, one subprocess per cell): **57/57 on 3.14.7, 57/57 on
3.9.6** — pre-latch seams roll back 143/130/129 with `teardowns=1`, `loaded=[] published=False`; post-latch exit 0;
dispositions `SIG_IGN`; mask `[]`.

**Latency bound** = the in-flight adapter call: `LaunchctlAdapter.timeout = 5 s` (`:200`), or `validate_install`'s
longest subprocess.

## Q2 — after completion: rule **(a)**, refute (c)

P3, four modes, identical on both interpreters: **(a)** `SIG_IGN`, never restore, 3× SIGTERM → survives, **rc 7**;
**(b)** restore originals then SIGTERM → **143, result replaced** (A F1 reproduced); **(c)** restore + `while
sigpending() & S: sigwait(S)` then SIGTERM after the last check → **143 — the drain does not close it**; (d) drain
with nothing arriving after → rc 7.

(c) is round seven in costume: `sigpending()` and `SIG_SETMASK` are two instructions and mode (c) is the gap between
them. `signal.sigtimedwait`/`sigwaitinfo` **do not exist on macOS** (P1, both interpreters), so the only drain is
`sigpending`+`sigwait` — and a wrong `sigpending` read makes `sigwait` block forever, a hung installer. `SIG_IGN`
already discards what a drain would consume ((d) vs (a)), so (c) buys a hang risk and closes nothing. **(a)**: the
three signals stay `SIG_IGN` until the process dies. P4: `os.kill` ×3 pre-exit, ×3 inside `atexit`, ×3 inside a
`__del__` running during interpreter finalization — all survive, `sys.exit(3)` yields **rc 3** on both. CPython's
`_PySignal_Fini` resets only *Python-callable* handlers to `SIG_DFL`; `SIG_IGN` is preserved, and P4 confirms it at
the latest point reachable from Python.

In-process callers get an explicit `restore_signals()` (P8: dispositions identical to the originals, mask unchanged,
first of three signals recorded = 143). The restoration window still exists *inside that method* — but it now sits
after the caller holds its result, where signal policy is the caller's business, not a completed exit code's.

## Q3 — remaining boundaries, honestly

1. **Before `_install_handlers`** — startup, imports, `argparse`, `Target.for_mode`. Default dispositions: SIGTERM
   kills with 143 (the `pre_handlers` cells die by signal). Nothing has mutated and the kernel's code equals the
   documented one. Shrinkable to interpreter startup by installing in `main()` before `parse_args`; I recommend that,
   and it closes the multi-second `validate_install` window too.
2. **The latch instant.** A signal between `_commit`'s poll and `state = COMMITTED` commits. A decision, not a
   defect: jobs are loaded and verified, so exit 0 is truthful, and D6 forbids replacing a completed result.
3. **During `_teardown`** — no polls by design, so a signal is recorded and discarded: SIGTERM cannot interrupt a
   rollback. Intended; document it.
4. **`restore_signals()`** (in-process only): a signal between the `SIG_IGN` pass and the re-install is *lost*, not
   mis-delivered. Signal-injecting tests must call it in `addCleanup`.
5. **Between `sys.exit(result)` and process death**: INT/TERM/HUP cannot alter the code (P4). Signals *outside*
   `SIGNALS` can (SIGQUIT 131, SIGABRT), and shutdown can still turn a final flush failure into 120 — mitigated for
   the committed print by the `devnull` `dup2` (`:483-488`), unhandled on the *warning* path. Separate lane.
6. **SIGKILL/SIGSTOP** anywhere — uncatchable; `.prior` sidecars remain the recovery mechanism (D5).
7. **Threads**: a helper thread would break the `self.signalled` single-writer assumption; the comment states it.

## Q4 — deterministic cells

Injection: a fake-adapter verb (`write_plist`/`bootstrap`/`print`/`bootout`) and a `_poll`/`_enter` wrapper calling
`os.kill(os.getpid(), sig)` at a **named seam** before returning — synchronous, no race.

- **Product (the pin):** {before `_install_handlers`, VALIDATED, ADMITTED, STAGED, before `write_plist` 1/2,
  PUBLISHED, before/after `bootstrap` 1/2, before/after verify, `_commit` pre-latch, post-latch, post-pins-print,
  `_teardown` body, `_teardown` bootout, after the `SIG_IGN` pass, after `run()` returns} × {INT 130, TERM 143,
  HUP 129}. Each cell asserts the existing 4-tuple (rc; liveness; plist bytes+mtime; fence) **plus** `getsignal(n) is
  SIG_IGN` ×3, mask == entry mask, `teardown_calls == 1`. Pre-latch ⇒ rollback with the signal code; post-latch ⇒ 0.
- **CLI cells** (subprocess, both interpreters, fake `launchctl`): `returncode >= 0` — not killed by a signal — and
  the documented code. This is the cell that fails today.
- **Two distinct signals** at one seam: `signalled == 143`, one rollback. **Signal during an adapter call**: a
  forked helper kills 0.3 s into a 1.2 s verb; the call returns its `Outcome`, no `InterruptedError`, the next poll
  rolls back. **`uninstall()`** under `/usr/bin/python3`: before each `bootout`, between bootout and
  `require_absent`, before each `remove_plist`, in the `finally`. **In-process**: `restore_signals()` returns the
  exact pre-run dispositions and mask.

**Must-die:** (1) handler raises instead of records → escape + EINTR cells RED; (2) drop `if self.signalled is None`
→ two-signal cell RED; (3) CLI re-installs originals → after-completion CLI cells RED (process dies 143); (4) any
`_poll()` deleted → its seam commits a mutation it should roll back; (5) latch poll moved after the assignment or
before the predicate → latch cells RED; (6) `_poll` added inside `_teardown` → teardown-abort cell RED; (7) `_poll`
raises `Refused` → exit-code cells RED; (8) re-introduce `SIG_BLOCK` in the handler → child-mask cell RED.

## Q5 — cost

A SIGTERM is honoured at the next poll — worst case one 5 s adapter timeout, typically microseconds, on an installer
whose span is seconds; SIGKILL stays immediate. Complexity: **negative** — the design deletes `raised_once`,
`resolved`, the outer `except`, the retry loop, both `SIG_IGN`→restore→`SETMASK` dances, `entry_mask` and every
`pthread_sigmask` call, for a 4-line handler, a 3-line poll and a 2-line `finally`. The reviewable claim becomes one
grep-checkable sentence: *no exception in this module originates in a signal handler, and the three signals are
ignored from teardown to process death.* Accept.
