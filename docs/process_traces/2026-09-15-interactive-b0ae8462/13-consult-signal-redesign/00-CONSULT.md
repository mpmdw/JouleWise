# Blind three-seat redesign consult — signal handling in the transactional night-agent installer (`efdaed87`), convened 2026-09-15 22:58 PDT under cold-gate 06 Q3

You are ONE of three independent seats (Astra, Fable, Opus). You do not see the other seats' answers. Answer the questions below from the exhibits and the code; propose the design you would ship, with exact code for the core mechanism, and say what it costs.

## The situation
Six fix rounds have chased one defect class: an asynchronous `Signalled` raised from a Python signal handler escaping the transaction's teardown frame, or leaving the mask/dispositions wrong, in ever-narrower instruction windows. The cold gate (exhibit B, Q3) ruled: if any further signal-class defect appeared after round 6, NO round 7 — instead this consult on replacing raise-from-handler with RECORD-AND-POLL. The real-signal execution lens (exhibits A/A2) then found, under BOTH Python 3.14.7 and 3.9.6 (60/222 cells each): a signal that arrives while the three signals are blocked and AFTER its original disposition has been re-installed stays pending until the final `SIG_SETMASK(entry_mask)`, is then delivered with the ORIGINAL disposition, and terminates the process (SIGTERM/SIGHUP default) or raises `KeyboardInterrupt` (SIGINT) — AFTER the result was completed (refusal 3, COMMITTED 0, uninstall 0 all replaced). D6 (exhibit E) requires: a deferred signal never replaces a completed result; the unwind runs exactly once; exit codes are the documented ones.

## Invariants that must survive (exhibit E, D5–D7, and the runbook's outcome table)
- Exactly two exit-0 paths (uninstall verified; COMMITTED); refusal/rollback exit codes as documented; RETAINED 4/1.
- A signal DURING the transaction (before the commit gate) must produce a rollback with the documented code 143/130/129 — the install must remain interruptible by SIGTERM (launchd/operator kill) with cleanup.
- Teardown runs once; nothing escapes `run()`/`uninstall()`; in-process callers (the tests) get their mask and dispositions back; the CLI process exits with `self.result`.
- Single-threaded process; stdlib only; Python 3.9-compatible (`/usr/bin/python3` runs uninstall).

## Questions
Q1. Record-and-poll: the handler only `pthread_sigmask(SIG_BLOCK, SIGNALS)` + records `self.signalled = 128 + signum`; `run()` checks the flag at every state boundary and before every launchctl mutation, raising `Signalled` from ORDINARY code. Write the exact code for the handler, the poll point(s), `_unwind`, and the restoration order. Does it close EVERY seam in exhibits A/B, including the after-completion window? What is the signal latency bound (one adapter call + its timeout)?
Q2. The after-completion window (exhibit A F1): once the result is complete, what should happen to a signal that arrives during or after restoration? Options: (a) never re-install the original dispositions in the CLI path — keep SIG_IGN for the three signals from completion until `sys.exit(result)`, and expose an explicit `restore()` for in-process callers; (b) restore dispositions and accept that a post-completion signal may replace the exit code (document it); (c) restore under the block, then drain with `sigtimedwait`/`sigpending` (3.9 has `signal.sigpending`/`sigwait`) before opening the mask; (d) something better. Rule one with reasons; give the code.
Q3. Is there any remaining boundary under the design you propose where a pending or newly delivered signal can (i) skip teardown, (ii) leave the mask or a disposition altered for an in-process caller, or (iii) change a completed exit code? Enumerate honestly, including the instant between `sys.exit` and process death.
Q4. Tests: name the deterministic regression cells (inject via a fake adapter verb, a wrapper, or `os.kill` at a named seam; no timing races) that would pin your design, and the must-die set.
Q5. Cost: what does the night lose (interruptibility latency, complexity) and is it acceptable for an installer that runs for seconds?

Write ≤ 1200 words. Be concrete: code, not adjectives.
