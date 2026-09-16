SESSION_MODE: delegated
WRITE_SCOPE: ["joulewise/night_agent_install.py","tests/test_night_agent_install.py","docs/phase_2/derivation_night_runbook.md","docs/process/NIGHT_HANDBACK.md"]
BASE_HEAD: 0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa
BASELINE_MANIFEST: .codex-bridge/baselines/mag-r5b-txn-20260915-2010.json
BASELINE_DIGEST: sha256:3996d64d31f079118916f0ab7472557705ad3e3a8948b28873589533eb21c15c
LEASE_ID: lease-18fb1685c8174d8390f4284e2d27b640

# Fix round 5 — transactional night-agent installer (`feat/2026-09-15-install-windows-transactional` @ `0ba6ce54`)

You are the implementation seat for fix round 5 in worktree `/Users/edr/code/JouleWise-wt-iw-txn` (branch checked out, tree clean at BASE_HEAD). Edit ONLY the four WRITE_SCOPE paths. Do NOT commit (the magistrate commits by pathspec after reading your diff). Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`; never run a real `launchctl bootstrap`/`bootout`. Run single modules: `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_agent_install` (≈5 min) and `tests.test_install_night_agent`. Mutation probes go in a `cp -R` copy under `/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r5-mut`, never in the worktree.

Authority: record 34 (D1–D10) is NOT in this checkout (it lives on main); read it at `/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/authority/34-design-adjudication-transactional-installer.md` (a verbatim copy); the full counter-review lt-31 is beside it at `/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/authority/lt-31-opus-counter-review-transactional.md`. RULING (magistrate b0ae8462): those two copies are the authority for this seat; no other record is required. The findings below are the Opus counter-review (record lt-31, gate ledger row 6, verdict LANDABLE + AMEND) and are ADOPTED by the magistrate as dictated. Implement exactly these three, nothing else:

## F1 (must) — `.prior` validate() refusal: add the test and the must-die entry
Add ONE test cell to `tests/test_night_agent_install.py` asserting that an install with a pre-existing `<label>.plist.prior` sidecar refuses with exit 3 and the verbatim message `retained prior plist: <path>; re-run --uninstall`, WRITING NOTHING (no plist published, no launchctl verb invoked, sidecar bytes+mtime unchanged). Then prove it is a killer: in the mutation copy delete the three-line refusal at `joulewise/night_agent_install.py` (the `if self.sidecar(label).exists(): raise Refused(3, ...)` block in `Target.validate()`), run the module, paste the RED tail; restore, paste the GREEN tail. Where the file keeps the D10 must-die list (a comment/table in the test module or wherever the existing must-die set lives — locate it with grep for "must-die" / "must die"), add "delete the retained-prior refusal".

## F3 (must) — signals unmasked for a sliver at teardown entry
Cure exactly as lt-31 prescribes (3 lines, structural): block the signals INSIDE the handler before raising, and restore the mask captured at handler-install time rather than at unwind time:

    def _install_handlers(self):
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())   # read, don't change
        def raised(number, frame):
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)            # mask before unwinding
            raise Signalled(128 + number)
        ...

and `_unwind` restores `self.entry_mask` (SIG_SETMASK) instead of `old_mask`. TRAP (from lt-31): do not keep `old_mask = pthread_sigmask(SIG_BLOCK, SIGNALS)` at the top of `_unwind` and use it for restoration — after a handler-side block it captures the already-blocked set and leaves the signals blocked for in-process test callers. `_unwind` may still SIG_BLOCK SIGNALS as its first statement (idempotent) but must restore `entry_mask`. Keep the existing SIG_IGN drain of queued repetitions. Apply the same shape to the uninstall path if it shares `_install_handlers`/`_unwind` (it does: `uninstall()` calls `machine._install_handlers()`). Add ONE regression cell that pins the cure deterministically (no timing races): e.g. invoke the handler function directly (or deliver a signal to self via `os.kill(os.getpid(), SIGTERM)` while a fake adapter's bootstrap is executing) and assert (a) inside the raised `Signalled` path the three signals are in `pthread_sigmask(SIG_BLOCK, ())` before `_unwind` runs, and (b) after `run()` returns the process mask equals the entry mask and dispositions are restored. Prove it kills the reverted cure in the mutation copy; paste RED and GREEN tails. All existing repeat-signal tests must stay green.

## F2 (docs) — the `.prior` sidecar is NOT a resumable journal; fix the wording
Adopt lt-31's prose. In `docs/phase_2/derivation_night_runbook.md` (§1.3 sidecar description, the sentence calling sidecars "files holding the previous bytes for recovery", and the exit-4 / RETAINED recovery text) and in `docs/process/NIGHT_HANDBACK.md` (the sentence that repeats it), replace the "recovery" claim with, verbatim or minimally adapted to the sentence:
"`.prior` sidecars hold the bytes an install replaced. Nothing restores them automatically after the installer exits: a later install refuses while one is present, and `--uninstall` deletes both the plists and the sidecars. Copy a sidecar by hand if you need the old plist back."
Grep both docs for every remaining "recover"/"recovery"/"resum" near "sidecar" or ".prior" and make each consistent. Do not touch record 34 (the D5 rationale addendum is the magistrate's; out of scope).

## Report
claude-codex-report/v1 envelope (genre implementation, under 8192 bytes): per finding, the exact diff hunks' locations, the RED/GREEN mutation tails, the final full-module tails for both test modules (foreground), the list of changed paths, and anything you could not verify. Flag any place where lt-31's dictation conflicts with the code you find, instead of improvising.
