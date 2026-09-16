# 03 — Adoption (magistrate b0ae8462, 2026-09-15 23:10 PDT)

Two of three seats (Fable blind, Opus) converged independently on the same design, each with executed probes under
Python 3.14.7 and 3.9.6: a handler that only RECORDS one integer (never raises, never touches the mask), ordinary-code
polls at every state boundary and before every mutation with the last poll as the commit latch, no `pthread_sigmask`
anywhere, `SIG_IGN` for the three signals from the end of teardown until process death (the CLI never re-installs the
originals; in-process callers call an explicit restore), and `_teardown` never polls. Both refuted the drain
alternative (`sigpending`+`sigwait` is two instructions with a gap; `sigtimedwait` does not exist on macOS). Opus adds
a physical finding: the round-5/6 `SIG_BLOCK` in the handler is INHERITED by every launchctl child spawned afterwards,
making the subprocess unkillable — the mask was harmful, not merely unnecessary. Ed's guidance (23:15) applied: this
is a nearly-done design converging under executed evidence, so implementation proceeded as round 8 without waiting.

ADOPTED: the Fable seat's Q1/Q2 code and Q4 cells as the round-8 dictation (already launched), PLUS the Opus seat's
extras for round 8b or the delta: install the handlers in `main()` before `parse_args` (shrinks the pre-handler window
to interpreter startup and covers `validate_install`); the CLI cell asserting `returncode >= 0`; the PEP 475 cell (a
signal 0.3 s into a 1.2 s adapter call returns the Outcome, recorded, next poll rolls back); the child-mask cell
(launchctl children inherit an empty mask); the seam × signal product with `getsignal is SIG_IGN` ×3 and
`teardown_calls == 1`; must-die items (1)–(8). Delta 6's F1 (outer catch overwrote completed codes) is moot under the
design; its F2 (runbook outcome row for teardown failure) is in round 8's scope. The Astra seat's answer is folded in
when it lands.
