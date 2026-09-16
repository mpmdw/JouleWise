# Cold-gate ruling — packet 06 (INSTALL-WINDOWS-MULTI-01 transactional, round 6)

Judge: Fable 5.1, cold single session, foreground only, no subagents, no background tasks. Checkout HEAD `ccce8a61b09a51d3a588d1a9b5f8d39f1f73ca8a` (verified `git rev-parse HEAD`). 2026-09-15.

**Disclosure.** Auto-loaded into context before I chose anything: `~/.claude/CLAUDE.md`, the repo `CLAUDE.md`, and the memory index `MEMORY.md` (pointer lines only). NOT read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any narrative state doc, any memory file body. No file modified except this ruling.

**Charter / packet verification (before the merits).** Method: `scripts/validate_gate_packet.py`. Run 1 with the convening prompt's first charter digest (`…75813a880ff…`): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2 with expected `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`: observed identical, `PASS`, rc 0; packet expected = observed `69ac0e9b…6d56d897b6c3e2a5ce`; exhibits A–E expected == observed digests. Judged on that basis.

**Packet hygiene.** Neutral and complete for Q2–Q5. One defect: Q1 is compound (same defect? / complete? / D6-consistent?) — answered in parts. Exhibit D cites authority files under `/private/tmp` that are not in this checkout; I used only the in-packet exhibit E for D1–D10.

## Q1 — F2: same defect as exhibit B F3; exhibit D's cure → AFFIRM (same defect), AMEND (cure incomplete; exact text below). Residual severity: MATERIAL.

Same defect: yes. Exhibit B F3 named "a sliver at teardown entry" and proposed the handler-side block; exhibit C's diff is exactly that; exhibit A F2 is the same seam one boundary earlier (the signal that lands before the handler has fired at all). Rule 11's trigger was correctly applied.

Executed probes (this checkout; fake adapter from `tests.test_night_agent_install.CapabilityTests`; one foreground process; `os.kill(getpid(), SIGTERM)` placed at a chosen seam via a wrapper; output verbatim):

```
P1  finally-before-block, refusal:   Signalled(143) ESCAPED run(); state=STAGED    result=3; mask_restored=False disp_restored=False
P1b finally-before-block, committed: Signalled(143) ESCAPED run(); state=COMMITTED result=1; mask_restored=False disp_restored=False
P2  except-Refused clause:           Signalled(143) ESCAPED run(); state=ROLLED_BACK result=3; mask_restored=True  disp_restored=True
P3  two distinct pending signals (HUP, TERM): the second handler fired AFTER the first had blocked all three (raised X: 15 at a later C call)
```

P1/P1b confirm exhibit A F2 on this head (teardown skipped, mask and dispositions left altered; `joulewise/night_agent_install.py:411-420`, `:482-483`). P2 and P3 are seams exhibit D does not name:

- **P2.** A signal landing inside an `except` clause of `run()` (`:473-481`; here during the `_warn` call). `_unwind` runs to completion in the `finally`, but the `Signalled` still escapes `run()`; `main()` (`:673`) catches only `Refused, OSError` → traceback, exit 1 instead of the refusal code; through the shell, an undocumented outcome. Teardown correct, mask restored: exit-code fidelity only.
- **P3 (mechanism).** `pthread_sigmask` stops kernel delivery; it does not clear a signal CPython has already tripped at C level. Two distinct signals tripped before the first Python handler runs → the second handler runs at the next check point although the mask is blocked → with the round-5 handler (`:352-354`) it raises inside the "masked" unwind: a teardown-skipped path inside the region D6 calls masked.
- **Entry seam.** Dictation (b)'s `for _ in range(2)` places a call (`range`) before the `try`, and a signal handled at `_unwind`'s function-entry check is raised before the loop's `try` exists. P1 is the deterministic equivalent (the raise precedes `_unwind`'s first statement).

**Ruling on exhibit D §F2:** (a), (c), (d) SOUND AS DICTATED. (b) AMENDED. (e) ADDED. Principle: the handler raises AT MOST ONCE per transaction, decided inside the handler; `run()` carries one outer catch for that single raise. Every seam then reduces to two cases, both handled.

Dictation text (replaces §F2 (b), adds (e); WRITE_SCOPE unchanged):

(b) `_install_handlers`: remove the recapture at `:351` (per (a)); the handler becomes

```python
def raised(number, frame):
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    if self.raised_once:
        return  # a second signal tripped before the block; the unwind owns the process
    self.raised_once = True
    raise Signalled(128 + number)
```

with `self.raised_once = False` and `self.resolved = False` in `__init__`. In `_unwind` the block becomes

```python
while True:
    try:
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        break
    except Signalled:
        continue  # the one raise landed here; the handler has already blocked the signals
```

(`while True`, not `range(2)`: no call precedes the `try`.) Comment in `_install_handlers`: "single-threaded process assumed: a helper thread would receive an unblocked signal and the Python handler would still run on the main thread."

(e) `run()`: the body's except clauses set `self.resolved = True` as their LAST statement, the try body sets it after the pins print, and one outer catch is added:

```python
def run(self):
    self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
    try:
        try:
            ...existing body...
            self.resolved = True
        except Refused as exc:
            self.result = exc.code; self._warn(str(exc)); self.resolved = True
        except Signalled as exc:
            self.result = exc.code; self.resolved = True
        except KeyboardInterrupt:
            self.result = 130; self.resolved = True
        except BaseException as exc:
            self.result = 1; self._warn("{}: {}".format(type(exc).__name__, exc)); self.resolved = True
        finally:
            self._unwind()
    except Signalled as exc:
        # The single handler raise landed outside the inner try: in an except clause above,
        # or at _unwind's entry. Signals are blocked and the handler cannot raise again, so
        # nothing below can be interrupted. _teardown is a no-op on a terminal state, so a
        # second _unwind is safe.
        if not self.resolved:
            self.result = exc.code
        self._unwind()
    return self.result
```

D6 consistency (exhibit E): COMMITTED still exits 0 because `_teardown`'s COMMITTED branch (`:377-382`) assigns 0 after any signal code; RETAINED still exits 4/1 (`:395`, `:406`); a refusal whose except clause was interrupted exits with the signal's documented code (130/143/129) — the signal arrived BEFORE the result was completed, so "a deferred signal never replaces a completed result" holds, and no traceback/exit-1 path remains. Swallowing the sliver `Signalled` inside `_unwind` is consistent with D6 for the same reason.

Regressions: keep D's (i)–(iv); add (v) signal inside the `except Refused` clause (a `_warn` wrapper that kills before delegating, as P2) → `run()` RETURNS 143, state ROLLED_BACK, mask restored, no traceback; (vi) two distinct signals pending at `_unwind` entry (block HUP+TERM in the test, `os.kill` both, unblock inside the seam) → `run()` returns, teardown ran once, mask restored; (vii) the P1 shape (kill in a wrapper around `_unwind`) → refusal code, and 0 on COMMITTED, mask restored. Must-die: revert the `raised_once` guard → (vi) RED; revert (e) → (v)/(vii) RED.

## Q2 — F1 → BLOCKER; exhibit D §F1 cure SOUND AS DICTATED, with one addition.

Verified by reading: `scripts/install_night_agent.sh:20` stores an empty value; `:79-81` forwards `--render-only` only when non-empty; so `--render-only ""` execs a real install and `--uninstall --render-only ""` real bootouts (consistent with exhibit A V4's tail; not re-run). BLOCKER: `--render-only "$dir"` with an unset variable is an ordinary operator error and it mutates launchd during what the operator believes is a dry run — D7/I4 isolation broken by argv shape, the exact class the ruled design made unrepresentable. Module side: `--render-only ""` reaches argparse `type=Path` (`:651`) as `Path("")` == `Path(".")` → a RenderTarget in the CWD (the repo root after the shell's `cd`): not a launchd mutation, but a silent write into the checkout; refuse with a custom argparse type raising `ArgumentTypeError` on empty → `UsageParser.error` → exit 2. Addition to the shell cure: `[[ -n "$2" ]] || usage` in every valued case with the usage line naming the option, and forward `--render-only` by a `render_given` flag, never by `-n "$render_only"`. Tests as dictated (exit 2, usage line, empty fake-launchctl call log, nothing written).

## Q3 — Round 6 justified as the LAST same-shape round; STOP CONDITION.

Charter §9: rounds 5 and 6 are two consecutive rounds on one signature. Round 6 is licensed only because it is dictated, in-scope, and — with the Q1 amendment — complete; the dictated (b) alone would fail its own delta re-audit on P2/P3, which would be the third failure. STOP CONDITION: if the delta re-audit of round 6 finds ANY further signal-class defect (teardown skipped, mask left blocked, or a handler raise escaping `run()`/`uninstall()`), there is NO round 7. Instead: a blind three-seat redesign consult on ONE question — replace raise-from-handler with record-and-poll: the handler only blocks and sets `self.signalled = 128 + number`; `run()` reads the flag at each state boundary before each mutation and in `_commit`, raising `Signalled` from ordinary code. No asynchronous exception exists, so no seam exists; the cost is signal latency bounded by one adapter call and its timeout. Until that lands the branch does not merge, and D6's "masked for the whole unwind" is recorded as a named limitation, not as met.

## Q4 — F3: fold into round 6 as dictated. AFFIRM exhibit D §F3.

The docs must describe the mechanism that lands: a registered lane would ship a runbook promising a pre-bootstrap check and a cleanup guarantee the code does not have (`night_agent_install.py:377-382` warns and returns 0). Seat already holds both docs in scope; zero code risk. NIT severity, in-round.

## Q5 — Landability: NOT YET; one more independent lens required.

Both round 5 and round 6 are reasoned cures for microsecond seams, and exhibit A's own G1 flag records no live probe. Require one fresh execution-lens seat (Astra or Opus, read-only on the module, tests in a copy) that drives REAL signals deterministically at every seam in Q1 (i)–(vii) plus `uninstall()` (c), under BOTH `python3` 3.14.7 (the venv path) and `/usr/bin/python3` 3.9.6 (the uninstall interpreter; eval-breaker placement differs between 3.9 and 3.11+, so the seam tests must pass on both), and runs the F1 shell cells against the fake launchctl. Clean delta re-audit (as the packet lists it) + that seat green + the lead's full-suite replay at the final head → LANDABLE. No further contract lens.

**Severities:** F1 BLOCKER; F2 with the P2/P3/entry seams MATERIAL; F3 NIT.

**Disagreements with the lead's labeled disposition:** (1) exhibit D §F2 is incomplete — AMEND, not confirm; (2) `range(2)` → `while True`; (3) landability requires the execution seat. Concur: F1 blocker, F2 MUST in this round, F3 in-round.

**Not executed:** the non-deterministic function-entry race itself (P1 is its deterministic equivalent); exhibit A's shell probe V4 (verified by reading `:20`, `:79-81`). Charter §5: this ruling is sealed unseen by the refuter.
