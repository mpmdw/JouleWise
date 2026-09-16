SESSION_MODE: delegated
WRITE_SCOPE: ["joulewise/night_agent_install.py","tests/test_night_agent_install.py"]
BASE_HEAD: 0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa
BASELINE_MANIFEST: .codex-bridge/baselines/mag-r5c-txn-20260915-2040.json
BASELINE_DIGEST: sha256:6e465eb6c7e60fb1d82d1be570c51ad585ece49f3eebbec36579163dd059a6d8
LEASE_ID: lease-9594e55207044cd6b8412b8566a0126b

# Fix round 5, RESUMED for F3 only — transactional installer (worktree /Users/edr/code/JouleWise-wt-iw-txn)

RULING (magistrate b0ae8462, answering your flag F3): APPROVED as you recommended — initialize `self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())` in `Transaction.__init__` (a read of the current mask, no change), and RECAPTURE it in `_install_handlers()` exactly as dictated; `_unwind` restores `self.entry_mask` with SIG_SETMASK. No separate early-refusal branch. Do the same for the uninstall machine if it is a distinct class.

STATE: the worktree is DIRTY with the already-verified F1 (tests) and F2 (runbook + NIGHT_HANDBACK) edits from the previous session — the baseline manifest records them as baseline-dirty. Do NOT redo, revert, or touch them; the docs are outside your WRITE_SCOPE now. Implement F3 only, in the two WRITE_SCOPE files, then run the verification below. Do not commit.

## F3 (must) — signals unmasked for a sliver at teardown entry
Cure exactly as lt-31 prescribes (3 lines, structural): block the signals INSIDE the handler before raising, and restore the mask captured at handler-install time rather than at unwind time:

    def _install_handlers(self):
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())   # read, don't change
        def raised(number, frame):
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)            # mask before unwinding
            raise Signalled(128 + number)
        ...

and `_unwind` restores `self.entry_mask` (SIG_SETMASK) instead of `old_mask`. TRAP (from lt-31): do not keep `old_mask = pthread_sigmask(SIG_BLOCK, SIGNALS)` at the top of `_unwind` and use it for restoration — after a handler-side block it captures the already-blocked set and leaves the signals blocked for in-process test callers. `_unwind` may still SIG_BLOCK SIGNALS as its first statement (idempotent) but must restore `entry_mask`. Keep the existing SIG_IGN drain of queued repetitions. Apply the same shape to the uninstall path if it shares `_install_handlers`/`_unwind` (it does: `uninstall()` calls `machine._install_handlers()`). Add ONE regression cell that pins the cure deterministically (no timing races): e.g. invoke the handler function directly (or deliver a signal to self via `os.kill(os.getpid(), SIGTERM)` while a fake adapter's bootstrap is executing) and assert (a) inside the raised `Signalled` path the three signals are in `pthread_sigmask(SIG_BLOCK, ())` before `_unwind` runs, and (b) after `run()` returns the process mask equals the entry mask and dispositions are restored. Prove it kills the reverted cure in the mutation copy; paste RED and GREEN tails. All existing repeat-signal tests must stay green.


Verification: RED/GREEN mutation proof of the F3 regression cell in a fresh `cp -R` copy under /private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5c-mut (revert only the F3 production cure there); then both modules in the foreground in the worktree: `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install` and `tests.test_install_night_agent`. Also confirm by a direct probe that after a refusal BEFORE handler installation (e.g. the F1 retained-prior refusal) the process signal mask is unchanged and no AttributeError occurs. Report: claude-codex-report/v1 envelope (genre implementation, under 8192 bytes) with hunk locations, RED/GREEN tails, both module tails, and anything unverifiable.
