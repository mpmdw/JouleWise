# lt-31 — Opus counter-review (gate ledger row 6), transactional night-agent installer

Fresh seat, read-only. Opened Tue Sep 15 19:30:28 PDT 2026, closed 19:47:54 PDT (clock-read `date`).
Target: `feat/2026-09-15-install-windows-transactional` @ `0ba6ce54`, worktree `/Users/edr/code/JouleWise-wt-iw-txn`.
Diff `073a9763...0ba6ce54`. Authority read first: `34-design-adjudication-transactional-installer.md` (D1–D10).
I wrote none of this code and none of its reviews. Lens: design questions the refuters did not ask.

**Verdict: LANDABLE with one AMEND (F1, a one-test addition) — no FIX-FIRST finding.**

Executed evidence (this session, on this head):
- `python3 -B -m unittest tests.test_night_agent_install` → Ran 35 tests, OK (268s).
- `python3 -B -m unittest tests.test_install_night_agent` → Ran 47 tests, OK (28s).
- Mutation probe in a `cp -R` copy at `/tmp/iw-mut` (canonical untouched): see F1.

## F1 — SHOULD-FIX (amend). The `.prior` validate() refusal is a live mutation survivor.

`Target.validate()` (`joulewise/night_agent_install.py:133-135`) refuses exit 3 with
`retained prior plist: <path>; re-run --uninstall`. That refusal is a documented row of the runbook
refusal table (`docs/phase_2/derivation_night_runbook.md:1414`). **No test covers it**:
`grep -rn "re-run --uninstall\|retained prior plist" tests/` returns nothing. Probe: deleted those
three lines in `/tmp/iw-mut`; `tests.test_night_agent_install` Ran 35 OK (351s) and
`tests.test_install_night_agent` Ran 47 OK (40s). 82 tests, both green, mutant alive.

This is the one leg of the sidecar lifecycle (Q2) with zero enforcement, and it is the leg that stops
a second install from clobbering an interrupted transaction's journal. It is also absent from D10's
must-die set — an omission in the dictation, not seat disobedience.

Amend: add one cell asserting that an install with a pre-existing `<label>.plist.prior` refuses with
exit 3 and the verbatim string, writing nothing; and add "delete the retained-prior refusal" to the
D10 must-die set. Cheaper than a delegated contract (rule 9 bench threshold) — bench work.

## F2 — RULING WANTED. The `.prior` sidecar is not a resumable journal; D5's rationale says it is.

D5 rejected 33b's TMPDIR journal partly because "the `.prior` sidecar is resumable (33b's
SIGKILL-mid-restore concern) without it." As implemented it is not. `restore_prior` (`:162-176`) reads
only `self.priors`, populated by `stage()` in the *same process*. No code path ever reads a sidecar
left by a dead process: `validate()` refuses on its presence, and `uninstall()` calls
`discard_priors()` (`:502`), deleting it. So after a SIGKILL the prior bytes are operator-readable
evidence, never automatically restored.

The shipped behaviour is right and matches D7 ("uninstall discards"). Only the recorded *reason* and
the docs' wording overclaim. The runbook calls sidecars "files holding the previous bytes for
recovery" (`:1435`) and the handback repeats it; under the writing standard's first-use test,
"recovery" there names a mechanism that does not exist. Suggested amend text, runbook §1.3 and
NIGHT_HANDBACK: *"`.prior` sidecars hold the bytes an install replaced. Nothing restores them
automatically after the installer exits: a later install refuses while one is present, and
`--uninstall` deletes both the plists and the sidecars. Copy a sidecar by hand if you need the old
plist back."* Magistrate's call on whether to also correct D5's rationale by dated addendum.

## F3 — SHOULD-FIX (not a blocker). Signals are unmasked for a sliver at teardown entry.

D6: "Signals masked (`pthread_sigmask` SIG_BLOCK) for the whole unwind (rule 28 Q4-F3)." The mask is
taken as the *first statement of* `_unwind` (`:409`), reached from `run()`'s `finally` (`:480-481`).
Between the first `Signalled` propagating and that call returning, the three signals are still
deliverable; a second one raises `Signalled` inside `_unwind`, which escapes `run()` (its `finally` is
already executing) and escapes `main()` (which catches only `Refused, OSError`) — traceback, exit 1,
**teardown never runs**: plists published, jobs possibly loaded, sidecars retained. The existing
repeat-signal tests (`test_repeated_signals_during_restore`,
`test_uninstall_masks_repeated_signals_through_absence_and_deletion`) exercise the masked region, not
this sliver. Same sliver in `uninstall()` (`:491-492`) but harmless there: nothing has mutated yet and
`except BaseException` returns 1.

Width is microseconds and needs an adversarial `kill` loop (a human double Ctrl-C lands tens of ms
later, safely inside the mask), so this is not a merge blocker. Structural cure, ~3 lines: block inside
the handler itself, and restore the mask captured at install time rather than at unwind time —

    def _install_handlers(self):
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())   # read, don't change
        def raised(number, frame):
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)            # mask before unwinding
            raise Signalled(128 + number)

with `_unwind` restoring `self.entry_mask` at `:415`. Note the trap: naively keeping
`old_mask = pthread_sigmask(SIG_BLOCK, SIGNALS)` at `:409` *after* a handler-side block would capture
the already-blocked set and leave the signals blocked for in-process test callers.

## D1–D8 faithfulness (Q1): implemented, with four deviations, all defensible

- **D1** ✓ engine stdlib-only at import; driver/gate imports are inside `validate_install` (`:584,:621`).
  Deviation: the shell does more than "argv + MIN_PYTHON + exec" — it also derives
  `measurement_root/.venv/bin/python` via `python3 -B -S` (`scripts/install_night_agent.sh:36-44`).
  Unavoidable (the interpreter must be chosen before `exec`), read-only, parity with `073a9763`. Not a defect.
- **D2** ✓ `LaunchctlAdapter.print` (`:227-236`) is exactly the dictated three-valued predicate, and
  matches the signature as a whole stderr **line** (`splitlines()`), which is stricter than substring.
- **D3** ✓ `Absent` is unconstructible outside `require_absent` (`_PROOF_KEY`, `:87-89`), and
  `_authorize` (`:148-156`) additionally binds target identity, label **and generation** — a bootstrap
  or bootout invalidates every outstanding proof (`:206,:210`). Stronger than dictated; improvement.
  Deviation: `write_plist` overwrites a plist with no proof (`:244-260`) — covered by ruling R2
  ("publication is not deletion") plus ADMITTED's absence check on both labels. Ruled, not a gap.
- **D4** deviation of letter: five `Target` methods touch `launch_dir` besides the three launchctl
  mutators (`stage`, `_temporary`, `remove_plist`, `restore_prior`, `discard_priors`). The invariant
  that matters — every *deletion or restoration* of a plist carries a current proof — holds; only
  `discard_priors` deletes unproofed, and sidecars are not plists and are invisible to
  `installed_agent_fence` (`scripts/magistrate_watchdog.py:726-728` reads `<label>.plist` only).
  A refinement of D4, not a violation; worth recording so a future reader is not misled by "nothing
  else touches launch_dir."
- **D5** ✓ all 9 states + 4 terminals; handlers installed *before* `STAGED` (`:442-444`); each
  bootstrap recorded *before* invocation (`:453-454`). Deviation: `Prepared.admit()` runs twice —
  `validate_install:632` on real `time.time()`, then authoritatively at `:440` on the injected clock.
  D5 permits the early read-only refusal; the wart is that the early one ignores the test clock. Low.
  Deviation: `custody_night.mkdir` (`:445`) runs under `--render-only` too, creating
  `<custody_root>/night` during a dry run — exact parity with baseline `install_night_agent.sh:310`,
  so not a regression; no doc claims render-only writes nothing. Low.
- **D6** ✓ one `finally`, positive dispatch on `state` (not on exception), `BrokenPipeError` lands in
  the success branch (`:462-469`), pending repeats drained via `SIG_IGN` before unblocking
  (`:413-415`) so a deferred signal cannot replace a completed result. Except F3.
  Extension beyond D6's three branches: restore-failure → `RETAINED` with **exit 1** (`:404-406`).
  Correctly documented as the runbook's fourth outcome row, so exit 4 no longer means "state is
  RETAINED" but "cleanup could not prove both labels absent". Consistent; improvement.
- **D7** ✓ `uninstall` 0/4, idempotent (`test_uninstall_is_rerunnable`), `NullAdapter` raises on every
  verb, render/uninstall refused at `main:652` before any adapter is constructed.
- **D8** ✓ no constant restated (`grep INSTALL_SPANS|INSTALL_CLOSE_MARGIN|PLAN_LEAD_S|00:00|24:00` →
  no hits); label set parameterised and the A204 one-label path already pinned
  (`test_one_label_verified_bootout_is_supported:1181`).

## Q2 sidecar lifecycle — closed

Created at STAGED only when a plist exists (`:137-145`); removed on COMMITTED (`:316-319`) and on
ROLLED_BACK (`:310`); retained on both RETAINED flavours (asserted bytes+mtime at
`tests/test_night_agent_install.py:726-730`); refused at `validate()` (F1, untested); discarded by
`uninstall` (`:502`). "Uninstall discards rather than restores priors" is correct and is what the
handback describes — but see F2 on the word "recovery".

## Q3 exit-0 paths — exactly two, and pinned

`uninstall`'s `return 0` (`:503`) and the single `self.result = 0` inside the `COMMITTED` branch of
`_teardown` (`:379`). Verified independently by grep and by
`test_zero_exit_routes_require_commit_or_verified_uninstall`, which re-derives both from the module's
own AST and asserts the zero assignment is inside `if self.state is State.COMMITTED`. `--help` is
disabled (`add_help=False`) and argparse errors exit 2. I1 holds.

## Q5 uninstall under system Python — yes, two independent pins

`scripts/install_night_agent.sh:30` forces `python="/usr/bin/python3"` and skips the whole MIN_PYTHON
block for uninstall. Behavioural pin: `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl`
runs the shell from a driver tree containing only the shell, the template and `joulewise/` — **no
`scripts/run_night.py`, no `.venv`** — and expects rc 0. Module pin:
`test_system_python_uninstall_exec_with_stripped_environment` execs
`/usr/bin/python3 -B -S -m joulewise.night_agent_install --uninstall` with `env={HOME,PATH,TMPDIR}` only.
Nit: neither pins the literal `/usr/bin/python3`, so a mutation to a bare `python3` would survive; not
worth a round.

## Q6 docs vs code — consistent

Every string in the new runbook §1.3 outcome table, §1.4, NIGHT_HANDBACK and the courier prompt was
grepped against the module: `install_span_closed`, `install_outside_span`, `plan_t0_in_the_past`,
`night_agent_already_loaded … state=unknown rc= stderr=`, `plan_outside_custody_root`,
`liveness_unknown: <label> rc= stderr=`, `failed to bootstrap`, `launch agent verification failed`,
`teardown: … retained plists:`, `uninstall: still loaded after bootout: …`,
`restore failed; retained prior sidecars: …`, `retained prior plist: …; re-run --uninstall`,
`unsupported plist destination: …`, `--render-only directory must differ from launch_dir`. All present
with matching exit codes (0 / 143,130,129,1,2,3 / 4 / 1). The dead "rolled back …" prose is gone from
all three docs (the one surviving hit, runbook `:449`, is an unrelated OS rollback). §1.4's recovery
block is now `&&`-chained and gated on uninstall exit 0, as D9 required. The four-outcome table with
the "span closes between the two bootstraps" worked example is the best pedagogy in this diff.

## Q7 overbuilt / missing

Nothing overbuilt. `Outcome.__bool__` raising, the `_PROOF_KEY`/`_TARGET_KEY` sentinels and the
generation counter each pay for themselves as mutation barriers. The `RenderTarget`/`LaunchdTarget`
subclasses are empty marker types but are load-bearing under `type(...) is` checks — keep.

**fsync gap: accepted limitation, not a defect.** No `fsync` on the published plist, the sidecar, or
`launch_dir` (`grep fsync` → none). The `.prior` file needs none, because F2 establishes it is never
read across process death. The published plist is exposed only to power loss between `os.replace` and
the APFS flush; launchd's loaded state does not survive a reboot either, so the post-crash recovery is
the documented §1.4 uninstall-and-re-arm in both cases. Recording it as a limitation is right; closing
it would add `os.fsync` on two file descriptors plus a directory fd for no reachable benefit.

**Operational coupling worth one runbook line (low):** `--plan` is required and must exist even for
`--uninstall` (`main:654`), so removing the night root makes uninstall impossible. This is parity with
`073a9763` and the handback already says "Do NOT remove the clone or the night root", so it is covered
— but the *reason* is not stated there. Optional.

## Merge-ability

Land after F1's one test. F2 is a docs/record amend that may land in the same PR or as a dated
addendum. F3 is a real hole in a stated invariant and should be booked, but it does not gate this
merge; if it is deferred, book it as a named limitation rather than letting D6's "masked for the whole
unwind" stand unqualified. A204 stays a separate PR per D8.
