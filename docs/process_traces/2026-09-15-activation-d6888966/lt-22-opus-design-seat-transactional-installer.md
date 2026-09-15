# lt-22 — Opus design seat: a transactional night-agent installer (contract / by-construction lens)

Written **11:52 PDT 2026-09-15** (clock read). Opus 5, blind — no other seat's output read. Checkout
`/Users/edr/code/JouleWise-wt-design-iw` at `073a9763`; bare line cites are that checkout. Read-only
except this file. Lens: for each element, the invariant it makes true *by construction* (the unsafe
state is unrepresentable) and what stays *enumerable* (true only because we checked a list).

## Q3 first — executed liveness evidence (mandatory), 11:48 PDT

```
$ launchctl print gui/501/com.joulewise.nonexistent.probe
exit=113 ; stdout empty
stderr: Bad request.
        Could not find service "com.joulewise.nonexistent.probe" in domain for user gui: 501

$ launchctl print gui/501/com.joulewise.magistrate      # loaded, state = not running
exit=0 ; stdout 66 lines, first `gui/501/com.joulewise.magistrate = {` ; stderr empty (0 bytes)
```

Predicate — the only liveness API in the design:

```
rc == 0                                            -> LOADED
rc == 113 AND stderr matches NOT_FOUND(label,uid)  -> ABSENT
anything else (any rc, timeout, OSError)           -> UNKNOWN
NOT_FOUND = 'Could not find service "<label>" in domain for user gui: <uid>'
```

rc 113 alone is **not** sufficient: the first stderr line is the generic `Bad request.`, so 113 is a
request-class code, not a label-specific one. `ABSENT` is the only constructor the deletion guard
accepts, so lt-21 F2 — `print … &&` reading any non-zero (stub 9) as "not loaded" at `:273`, `:335`,
`:338` — becomes unwritable. Enumerable residue: this rc/message signature is an empirical fact about
this macOS build, pinned by one test and re-probed on OS upgrade (the 25G83-epoch class). The adapter
must **capture** stderr; `2>/dev/null` today discards the evidence needed to classify.

**Fake launchctl.** The stub at `tests/test_install_night_agent.py:76-84`
(`[[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?`) emits only 0/1 and **cannot express UNKNOWN** — which is why
the suite never caught F2. Per label: marker present → rc 0 + a canned `gui/<uid>/<label> = {` block,
empty stderr; marker absent → rc 113 + the two verbatim stderr lines, label/uid substituted;
error-directive file → that rc with arbitrary stderr. Adversarial cells: rc 113 with a *different*
message ⇒ UNKNOWN; rc 9 with the exact not-found message ⇒ UNKNOWN; rc 0 with junk stderr ⇒ LOADED.
*Rejected:* a two-valued stub plus an "error mode" flag — models the bug, not the contract.

## Q1 — Shape: **(B)**, a Python transaction module; shell reduced to argv parsing

Four rounds, not four bugs but one topology: every invariant was enforced by inspecting call sites, and
the class reappeared at a **new site** each round — final bootstrap → `set -e`-skipped EXIT trap →
post-gate `rm -rf` at `:374` → `--uninstall` at `:267-272`. Enumeration cannot terminate against an
adversary that is "one more line". Four devices:

1. **Single mutation channel.** One `LaunchdTransaction`, exactly three mutators (`write_plist`,
   `bootstrap`, `bootout`); nothing else may touch `launch_dir` or call launchctl. The site set closes.
2. **The gate is a precondition of the mutator, not a statement between mutators.** `mutate(op)` = read
   clock → refuse if `now >= min(selected_span_close, install_close_epoch)` → execute → record.
   `commit()` is callable only from `VERIFIED`, re-reads the clock once, returns a `Committed` token;
   `main()` returns 0 **iff** it holds that token. → **I1 by construction**: exit 0 requires a clock read
   after the last mutation (`mutate` raises once COMMITTED).
3. **Teardown dispatches on transaction state, never on an exit code.** The shell branched on `$?`
   (`:312`), so any post-gate failure re-entered it — ruling 28 Q1b, a failed `/tmp` cleanup tearing down
   a verified arm. `__exit__` branches on `self.state`, monotone and set *before* any post-commit
   statement; the COMMITTED branch has no edge back to unwind and wraps cleanup in
   `except BaseException: warn`. → synthesis 28/13's POSITIVE RULE ("after the commit gate, no statement
   may fire teardown's failure branch") becomes structural instead of reviewed.
4. **Proof-carrying deletion.** `require_absent(label) -> Absent` raises on LOADED *and* UNKNOWN;
   `remove_plist(label, proof: Absent)` takes the token. → **I2 by construction**: no site can delete a
   plist without proving absence; unknown ⇒ loaded is a type fact, not a convention.

*Rejected: (A) keep zsh, fix the `loaded_state` predicate at the three sites.* It repairs the predicate,
not the topology, and zsh carries none of devices 2–4: `exit 0` is reachable from any line, there is no
token type, and errexit inside a function skips the EXIT trap (measured, ruling 25 probes). (A) makes I2
true *at three enumerated sites* and I1/I3 true nowhere — the guarantee shape that failed four times.
Also rejected: a post-hoc verifier subprocess — it observes the bad state but cannot undo it.

**Still enumerable under (B):** the managed label set (two constants); the ABSENT signature; SIGKILL
between `bootstrap` and the journal write (mitigated by ordering — plists written *before* bootstrap, so
the crash half-state is files-present = fence-visible); whether `bootout` is synchronous (a dying job
reads LOADED or UNKNOWN, both refuse — resolved conservatively, not eliminated).

## Q2 — The state machine

`PLANNED` → `PREPARED` → `FILES_WRITTEN` → `BOOTOUT_DONE` → `NIGHT_LOADED` → `BOTH_LOADED` →
`VERIFIED` → `COMMITTED`; terminal failures `UNWOUND`, `RETAINED`.

- `PLANNED` — plan/pin/preflight/write-once checks and occupancy; **no mutation, no `mkdir`** (preserves
  `:309`). Occupancy is `require_absent` on **both** labels (ruling 28 Q2; `:302-306`): UNKNOWN refuses
  (exit 3) rather than proceeding.
- `PREPARED` — journal under `TMPDIR`: per label, prior plist bytes (or "none") and prior liveness.
- `FILES_WRITTEN` … `VERIFIED` — one `mutate`/`verify` per edge, so the gate fires at every one; the
  "missed boundary at the final bootstrap" has nowhere to hide.
- `COMMITTED` — the single commit predicate, evaluated once.

**Single teardown** (`__exit__`, dispatching on state, signals masked throughout):

| state at failure | launchd left | files left | rc |
|---|---|---|---|
| PLANNED | untouched | untouched | 2 / 3 |
| PREPARED, FILES_WRITTEN | untouched (nothing bootstrapped) | priors restored byte-identical (`copy2`, mtime) | original |
| BOOTOUT_DONE … VERIFIED | bootout both, then `require_absent` both | priors restored | original |
| same, either label not ABSENT | left as found | **new plists, backup, journal all retained** | **4** |
| COMMITTED | both loaded | both new plists | 0 |

**I3 with a prior job loaded:** impossible. Occupancy refuses at PLANNED unless both labels prove
ABSENT, so at PREPARED no managed job is loaded and restoring *files* restores the exact prior state.
Ruling 25 Q3's residual ("a previously loaded dead-man is restored as a file but not re-loaded")
disappears by construction; teardown still never bootstraps.

**Signals.** INT/TERM/HUP raise `Signalled(rc)` (130/143/129) so the one teardown runs;
`pthread_sigmask(SIG_BLOCK, …)` covers the whole unwind — the Python form of ruling 28 Q4's
`trap '' INT TERM HUP` — and because handlers are installed *before* the journal exists it also closes
F4 (`:304-309`, INSTALLER-BACKUP-WINDOW-01) by construction. A SIGKILL mid-restore leaves the journal,
so restore is idempotent and resumable; even unresumed the half-state is files-present.

## Q4 — Migration

**Stale today; must land in this lane (I5).** `docs/phase_2/derivation_night_runbook.md:1408-1415`
documents `install_span_closed; rolled back com.joulewise.night before dead-man bootstrap`, `failed to
bootstrap com.joulewise.night.deadman; rolled back com.joulewise.night`, and `launch agent verification
failed; rolled back both agents`. **None of those strings exists in `scripts/install_night_agent.sh` at
`073a9763`** (`grep -n "rolled back"` → no match; ruling 25 Q3 step 2 deleted the inline rollbacks). Its
closing sentence — "Every unsuccessful exit after rendering also removes this attempt's plists and
restores prior bytes" — is **false** for the RETAINED branch. Replace that prose with the state table.

**Refusal strings surviving verbatim** (runbook `:1392-1402`; NIGHT_HANDBACK `:206-208`):
`install_span_closed`, `install_outside_span`, `plan_t0_in_the_past`, `night_agent_already_loaded`,
`plan_outside_custody_root`, `night_plan_malformed`, `plan_schedule_unrepresentable`,
`install_spans_unresolvable_on_day`, `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`; exit
codes 2/3; the summary fields (`now_epoch_s`, `t0_epoch_s`, `install_close_epoch_s`, `deadman_epoch_s`)
with local-ISO rendering. **New rows** (behaviour already in code, undocumented): the retained-state
message + **exit 4** (`:276`, `:342`), and `install_liveness_unknown` for UNKNOWN at occupancy.

**Callers.** `run_night.py schedule` unchanged; the module imports `schedule` / `install_close_epoch` /
`INSTALL_SPANS` directly rather than shelling out (`:153`), deleting the base64 marshalling (`:85-121`)
and `(@f)` splitting (`:293-301`). MIN_PYTHON (`:64-84`) **stays a subprocess** — its point is a
different interpreter. Courier prompt / NIGHT_HANDBACK: record that `--uninstall`, run after every
night, exits 4 and retains plists when a label is not provably ABSENT, and that re-running is safe.

**The twelve-row gate should require.** *Regression matrix as a product:* {8 states} × {op-nonzero, INT,
TERM, HUP, clock past selected_span_close, clock past install_close, liveness UNKNOWN, liveness
LOADED-after-bootout, restore I/O error}; each cell asserts the 4-tuple (rc; per-label liveness from the
stub log; per-plist bytes+mtime vs prior; `installed_agent_fence()` over the result) — never message
text alone. Unreachable cells are *declared* unreachable, so a refactor reaching one turns RED. *One
shared cell assertion*, the machine-checkable class-2 statement, impossible to omit per-cell: the fence
never returns `None` while the stub log says a label is loaded. *Must-die set:* removal of the signal
mask; removal of `require_absent` at any deletion site; ABSENT widened to `rc != 0`; rc 113 without the
stderr match; commit `<`→`<=`; `__exit__` dispatch replaced by an exit-code test; `copy2`→`copy`
(lt-21's near-miss: dropping `-p` survived 59 tests); the RETAINED `exit 4`; the render-only
no-launchctl guard; the COMMITTED `except BaseException`. Carry ruling 28 Q5's set forward; record
`trap - EXIT` (lt-21 F3, unkilled) as **retired by construction**, not killed. *Replay:* full unpiped
suite on the integration tree, plus an old→new mapping table (every FIX-1..10 assertion against its
matrix cell) so lt-15's "no case dropped" discipline is checkable. lt-90 rows 6, 7, 10, 11, 12 rerun on
the new head.

## Q5 — Scope

`scripts/install_magistrate_watchdog.sh` carries the **same class-2 defect, live today**: `:199-200`
(`bootout … || true`; `rm -f "$plist"`; `exit 0`) is byte-for-byte the shape ruling 28 Q2 just cured on
the night uninstall; `:184` removes the plist in `cleanup_failed_install` with no liveness check; `:306`
and `:311-315` bootout unverified.

**Recommendation: design for it now, land it later.** Parameterise the transaction by label set from the
first commit (no hard-coded pair inside the module), so A204 becomes a one-label caller with only new
tests and an unchanged module, landed as a **separate PR**. *Rejected:* fold A204 into the same PR —
this installer arms the magistrate that supervises the night, so a regression there blinds the
supervisor during exactly the window the lane protects, and one PR touching both installers makes a red
replay cell ambiguous as to its source.

**Shipped default span list: unchanged** — `INSTALL_SPANS = (("00:00","24:00"),)` (`run_night.py:69`).
*Rejected:* a narrowed default (e.g. the historical 03:00–06:30): D-181 cl.1 says nothing else about
timing is a rule, adjudication 06 ruled the whole-day default with population flagged to Ed, and cold
gate 25 Q4 established that a narrowed span is a *different* lane.

## Q6 — Preserve vs discard

**Preserve** — semantics, observable behaviour byte-identical wherever documented.
1. The single commit gate on `min(selected_span_close, install_close_epoch)` (ruling 25 Q1(c)) and
   synthesis 28/13's POSITIVE RULE — now structural rather than reviewed.
2. Verified bootout before any removal (ruling 25 Q3 as amended) → `require_absent` tokens.
3. The RETAINED branch verbatim: restore nothing, remove nothing (including the backup), name both
   labels and the retained plist paths, **exit 4** (`:275-278`, `:341-344`).
4. Render-only exemption (ruling 28 Q6.3) — never invokes launchctl, must **not** refuse loaded labels.
   **I4 by construction**: a `NullLaunchctl` adapter that raises on any call; never enters PREPARED.
5. Occupancy refusal on **both** labels, exit 3, message naming the label (`:302-306`).
6. One-pass template substitution (`:244-248`, re-audit 04 R1); the MIN_PYTHON subprocess (`:64-84`).
7. `cp -p` mtime preservation → `copy2` plus an explicit mtime assertion in the matrix.
8. Write-once record refusal (`:283-291`); read-only refusals before any `mkdir` (`:309`).
9. Every refusal string and exit code in the Q4 survivor list.

**Discard.** The `$?`/EXIT-trap machinery (`:320-356`) including `trap - EXIT` (`:330`); the three
`print … && loaded=1` idioms (`:273`, `:335`, `:338`); the base64/`(@f)` marshalling (`:85-121`,
`:293-301`); the stale runbook rollback prose (`:1408-1415`). FIX-1..10: keep every **assertion**,
discard the shell-specific scaffolding, ship the mapping table. Rename
`test_clock_advancing_during_backup_removal_preserves_verified_arm` to a `control_…` name — lt-21 showed
it survives edit 1's reversion because it *is* a control, and the name invites misreading it.
