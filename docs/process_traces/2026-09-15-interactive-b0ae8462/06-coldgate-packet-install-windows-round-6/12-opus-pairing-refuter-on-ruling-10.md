# Cold-gate 06 — Opus pairing refuter (contract lens), packet 06 at `ccce8a61`

Charter digest observed `sha256 099de884…c95d81` via `shasum -a 256 docs/process/coldgate_charter.md`; matches the packet pin. I do not decide; I attempt falsification.

## Q1 — F2 is the same defect; the dictated cure is INCOMPLETE. AMEND.

Same defect as exhibit B F3: yes — both are "a handler-raised `Signalled` escapes the teardown frame". Three residuals survive exhibit D §F2.

**(1) The retry is nested one frame too deep.** Dictation (b) puts `for _ in range(2): try: pthread_sigmask(SIG_BLOCK, SIGNALS)` inside `_unwind`. Executed `dis` of that exact body (Python 3.9.6): `0 LOAD_GLOBAL range / 2 LOAD_CONST / 4 CALL_FUNCTION / 6 GET_ITER / 8 FOR_ITER / 10 STORE_FAST / 12 SETUP_FINALLY`. Six boundaries — plus the lookup, call and prologue of `self._unwind()` at :484 — precede the try. A handler firing there raises `Signalled` from inside `run()`'s `finally`: `_teardown` (:413) never runs and the mask stays blocked. That is exactly the round-5 defect, narrower by ~8 bytecodes.

**(2) A `Signalled` still escapes `run()` even when teardown does run.** Executed probe (`sigprobe.py`: structural replica with cure (b) applied, real `SIGTERM` via `os.kill(os.getpid(), …)` at the except-clause seam): `seam=except-body rc=None escaped=Signalled torn_down=True mask_leaked=[] disp_leaked=[]`. The `finally` fires, so teardown and mask are fine, but `return self.result` (:485) is skipped and the caller gets a `BaseException`, not the exit code — a D6 violation ("exit with the original code", exhibit E :68–:72) untested by the dictation.

**(3) Dictation (d) restores in the wrong order.** Current :416–:420 is `SIG_IGN` all → `SIG_SETMASK(entry_mask)` → re-install originals; (d) keeps it. Between the unblock at :418 and the last `signal.signal` at :420 the mask is open while dispositions are half-restored, so a signal delivered there runs a restored original (e.g. `default_int_handler` → `KeyboardInterrupt`) out of `_unwind`, escaping the `finally`. Same hole in `uninstall` at :513–:515.

Swallowing the sliver is D6-consistent **provided** it happens in a frame that still reaches `_teardown` and returns the original code; D6's "runs once; a repeated signal does not restart it" (E:73) already holds because `_teardown`'s state dispatch (:377/:383/:385) matches none of `SUCCESS/REFUSED/ROLLED_BACK/RETAINED`, so a second `_unwind` cannot re-tear-down. Amended text:

> (b-amended) Leave `_unwind`'s first call unguarded; guard the whole frame instead. Rename today's `run()` body to `_run_guarded()` (unchanged, including its `finally: self._unwind()`), and write:
> ```python
> def run(self):
>     self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
>     try:
>         return self._run_guarded()
>     except Signalled:
>         # Handler blocked INT/TERM/HUP before raising: uninterruptible here;
>         # a second _unwind is a no-op by _teardown's state dispatch.
>         self._unwind()
>         return self.result
> ```
> (d-amended) In `_unwind` and in `uninstall`'s `finally`, restore dispositions BEFORE the mask: `SIG_IGN` all (discards pending) → re-install the saved dispositions → `SIG_SETMASK(entry_mask)` LAST.

With (c) as dictated (block before `_install_handlers`), `uninstall` needs no outer guard: nothing can raise before the block.

## Q2 — BLOCKER; cure shape right, dictation text needs two corrections.

Executed probe of :15–:24 and :78–:89 copied verbatim: `--render-only ""` → `RECONSTRUCTED ARGV: --plan … --launchctl-bin launchctl --python DERIVED` (real install); `--uninstall --render-only ""` → real uninstall argv, so `main()`'s mutual-exclusion refusal (:655) is never reached. BLOCKER, confirmed.

Corrections: (i) "preserved verbatim" must not be read as dropping `${plan:A}`/`${render_only:A}`; :74 makes absolutization contractual. Dictate: *"track presence with a per-option `_given` flag (the existing `python_given` idiom at :11/:32/:84) and drive :78–:89 off the FLAG, never off emptiness: `if (( render_only_given )); then set -- "$@" --render-only "${render_only:A}"; fi`. 'Verbatim' means option presence and count, not the literal string."* (ii) The module-side guard as written will not fire: `--render-only` is `type=Path` (:662) and `Path("")` is `PosixPath('.')`. Dictate: *"change `--render-only` to `type=str`, refuse `if args.render_only == "": raise Refused(2, "--render-only requires a non-empty directory")` before `Target.for_mode`, then convert to `Path`."*

## Q3 — Round 6 authorized; stop condition.

Justified under charter §9 (dictated cures; my (b-amended) is a frame rename, not new mechanism). **Stop condition I would accept:** if the delta re-audit finds ANY further signal-class defect — teardown skipped, mask or disposition leak, or any exception escaping `run()`/`uninstall()` — there is NO round 7. The lane descopes: delete raise-from-handler entirely (block INT/TERM/HUP from `_install_handlers` through the end of `_unwind`, no Python-level handler, no `Signalled`), making the class unreachable at the cost of a non-interruptible install (bounded by the adapter timeouts and the install span); "interruptible install" becomes a separate lane.

## Q4 — Fold, with one added sentence.

Both are mechanical text fixes in WRITE_SCOPE; fold. But the runbook :1438 fix must not hide the behaviour: :377–:382 warns and exits 0, and the retained `.prior` makes the NEXT install refuse at :128–:129. Dictate: *"…if removal fails the installer prints `warning: prior sidecars not removed: <exc>` and still exits 0; the retained sidecar makes the next install refuse with exit 3 `retained prior plist: <path>; re-run --uninstall` — clear it before the next arm."* With that sentence, no lane.

## Q5 — Yes: one more execution lens before merge.

Rounds 5 and 6 were both reasoned statically and each missed a boundary. Require a seat driving REAL signals at five seams — (a) after the last mutating verb inside `run()`'s try, (b) in an `except` body, (c) at `_unwind` entry before `SETUP_FINALLY`, (d) in `uninstall` between block and try, (e) inside the disposition-restore loop — asserting per seam: teardown ran, exit code equals the original, `pthread_sigmask(SIG_BLOCK, ())` equals the invocation mask, `getsignal()` equals the pre-run disposition, nothing escapes `run()`/`uninstall()`. Landable once that lens is green, not before.
