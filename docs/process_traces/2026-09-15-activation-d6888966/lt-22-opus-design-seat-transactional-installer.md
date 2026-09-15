# lt-22 — Opus design seat: a transactional night-agent installer (by-construction lens)

Written **11:52 PDT 2026-09-15** (clock read). Opus 5, blind. Tree
`/Users/edr/code/JouleWise-wt-design-iw` at `073a9763`; bare line cites are that checkout. Lens: what
each element makes true *by construction* (unsafe state unrepresentable) vs what stays *enumerable*.

## Q3 first — executed liveness evidence (mandatory), 11:48 PDT

```
$ launchctl print gui/501/com.joulewise.nonexistent.probe
exit=113 ; stdout empty
stderr: Bad request.
        Could not find service "com.joulewise.nonexistent.probe" in domain for user gui: 501

$ launchctl print gui/501/com.joulewise.magistrate      # loaded, state = not running
exit=0 ; stdout 66 lines, first `gui/501/com.joulewise.magistrate = {` ; stderr empty (0 bytes)
```

Predicate:

```
rc == 0                                            -> LOADED
rc == 113 AND stderr matches NOT_FOUND(label,uid)  -> ABSENT
anything else (any rc, timeout, OSError)           -> UNKNOWN
NOT_FOUND = 'Could not find service "<label>" in domain for user gui: <uid>'
```

rc 113 alone is **not** sufficient: the first stderr line is the generic `Bad request.`, so 113 is a
request-class, not a label-specific, code. `ABSENT` is the only constructor the deletion guard accepts,
so lt-21 F2 — `print … &&` reading any non-zero (stub 9) as "not loaded" at `:273`, `:335`, `:338` —
becomes unwritable. The signature is empirical, hence enumerable: pin it in one test, re-probe on OS
upgrade. The adapter must **capture** stderr; `2>/dev/null` discards what classifying needs.

**Fake launchctl.** The stub at `tests/test_install_night_agent.py:76-84`
(`[[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?`) emits only 0/1 and **cannot express UNKNOWN** — hence F2
went uncaught. Per label: marker present → rc 0 + a canned `gui/<uid>/<label> = {` block,
empty stderr; marker absent → rc 113 + the two stderr lines verbatim; an error-directive file → that rc
with arbitrary stderr. Adversarial cells: rc 113 with a *different* message, and rc 9 with the exact
not-found message, both ⇒ UNKNOWN. *Rejected:* a two-valued stub with an "error mode" flag — that models
the bug, not the contract.

## Q1 — Shape: **(B)**, a Python transaction module; shell reduced to argv parsing

Four rounds, not four bugs but one topology: each invariant was enforced by inspecting call sites, so
the class reappeared at a **new site** every round — final bootstrap → `set -e`-skipped EXIT trap →
post-gate `rm -rf` (`:374`) → `--uninstall` (`:267-272`). Enumeration cannot terminate against an
adversary that is "one more line". Four devices:

1. **Single mutation channel.** One `LaunchdTransaction`, three mutators (`write_plist`, `bootstrap`,
   `bootout`); nothing else touches `launch_dir` or launchctl.
2. **The gate is a precondition of the mutator, not a statement between mutators.** `mutate(op)` = read
   clock → refuse if `now >= min(selected_span_close, install_close_epoch)` → execute → record.
   `commit()` is callable only from `VERIFIED`, re-reads the clock once, returns a `Committed` token;
   `main()` returns 0 **iff** it holds that token. → **I1 by construction**: exit 0 needs a clock read
   after the last mutation (`mutate` raises once COMMITTED).
3. **Teardown dispatches on transaction state, never on an exit code.** The shell branched on `$?`
   (`:312`), so any post-gate failure re-entered it (ruling 28 Q1b: a failed `/tmp` cleanup tore down a
   verified arm). `__exit__` branches on `self.state` — monotone, set *before* any post-commit
   statement; the COMMITTED branch has no edge back to unwind and wraps cleanup in
   `except BaseException: warn`. → synthesis 28/13's POSITIVE RULE ("after the commit gate, no statement
   may fire teardown's failure branch") becomes structural, not reviewed.
4. **Proof-carrying deletion.** `require_absent(label) -> Absent` raises on LOADED *and* UNKNOWN;
   `remove_plist(label, proof: Absent)` takes the token. → **I2 by construction**: no site deletes a
   plist without proving absence; unknown ⇒ loaded is a type fact, not a convention.

*Rejected: (A) keep zsh, fix the `loaded_state` predicate at the three sites.* It repairs the predicate,
not the topology; zsh carries none of devices 2–4 (`exit 0` reachable from any line, no token type,
errexit in a function skips the EXIT trap — measured, ruling 25). (A) makes I2 true *at three named
sites* and I1/I3 nowhere.

**Still enumerable under (B):** the label set; the ABSENT signature; SIGKILL before the journal write
(ordering leaves the half-state files-present, fence-visible); `bootout` asynchrony (a dying job reads
LOADED or UNKNOWN; both refuse).

## Q2 — The state machine

`PLANNED` → `PREPARED` → `FILES_WRITTEN` → `BOOTOUT_DONE` → `NIGHT_LOADED` → `BOTH_LOADED` →
`VERIFIED` → `COMMITTED`; terminal failures `UNWOUND`, `RETAINED`.

- `PLANNED` — plan/pin/preflight/write-once checks and occupancy; **no mutation, no `mkdir`**
  (preserves `:309`). Occupancy is `require_absent` on **both** labels (ruling 28 Q2; `:302-306`):
  UNKNOWN refuses (exit 3).
- `PREPARED` — journal under `TMPDIR`: per label, prior plist bytes or none, and prior liveness.
- `FILES_WRITTEN` … `VERIFIED` — one `mutate`/`verify` per edge, so the gate fires at each; the missed
  boundary at the final bootstrap has nowhere to hide.

**Single teardown** (`__exit__`, dispatching on state; signals masked):

| state at failure | launchd left | files left | rc |
|---|---|---|---|
| PLANNED | untouched | untouched | 2 / 3 |
| PREPARED, FILES_WRITTEN | untouched | priors restored byte-identical (`copy2`) | orig |
| BOOTOUT_DONE … VERIFIED | bootout both, `require_absent` both | priors restored | orig |
| same, either label not ABSENT | as found | **new plists, backup, journal retained** | **4** |
| COMMITTED | both loaded | both new plists | 0 |

**I3 with a prior job loaded:** impossible. Occupancy refuses at PLANNED unless both labels prove
ABSENT, so at PREPARED no managed job is loaded and restoring *files* restores the prior state exactly.
Ruling 25 Q3's residual (a loaded dead-man restored as a file, not re-loaded) disappears.

**Signals.** INT/TERM/HUP raise `Signalled(rc)` (130/143/129) so the one teardown runs;
`pthread_sigmask(SIG_BLOCK, …)` covers the whole unwind (ruling 28 Q4's `trap '' INT TERM HUP`), and
since handlers install *before* the journal exists it also closes F4 (`:304-309`,
INSTALLER-BACKUP-WINDOW-01). SIGKILL mid-restore leaves the journal; restore is idempotent, and the
half-state is files-present.

## Q4 — Migration

**Stale today; must land in this lane (I5).** `docs/phase_2/derivation_night_runbook.md:1408-1415`
documents three `…; rolled back …` messages, but **no "rolled back" string exists in
`scripts/install_night_agent.sh` at `073a9763`** (grep → no match; ruling 25 Q3 step 2 deleted them).
Its closing claim that every unsuccessful post-render exit removes this attempt's plists and restores prior bytes is **false** for the RETAINED
branch; replace it with the state table, and document the retained message + **exit 4** (`:276`,
`:342`).

**Refusals surviving** (runbook `:1392-1402`; NIGHT_HANDBACK `:206-208`): install_span_closed,
install_outside_span, plan_t0_in_the_past, night_agent_already_loaded, plan_outside_custody_root,
night_plan_malformed, plan_schedule_unrepresentable, install_spans_unresolvable_on_day,
plan_t0_not_minute_aligned, plan_t0_ambiguous_local_time; exit codes 2/3; the summary fields
(now_epoch_s, t0_epoch_s, install_close_epoch_s, deadman_epoch_s) with local ISO times.

**Callers.** `run_night.py schedule` unchanged; the module imports `schedule`/`install_close_epoch`/
`INSTALL_SPANS` instead of shelling out (`:153`), deleting the base64 marshalling (`:85-121`) and `(@f)`
splitting (`:293-301`). MIN_PYTHON (`:64-84`) **stays a subprocess** (different interpreter). Courier
prompt / NIGHT_HANDBACK: `--uninstall` exits 4 and retains plists when a label is not provably ABSENT;
re-running is safe.

**The twelve-row gate should require.** *Matrix as a product:* {8 states} × {op-nonzero, INT, TERM,
HUP, clock past selected_span_close, clock past install_close, UNKNOWN, LOADED-after-bootout, restore
I/O error}; each cell asserts a 4-tuple (rc; per-label liveness from the stub log; per-plist
bytes+mtime vs prior; `installed_agent_fence()` over the result) — never message text alone.
Unreachable cells are *declared* unreachable, so a refactor reaching one turns RED. *Shared cell
assertion* (class 2, machine-checkable, impossible to omit): the fence never returns `None` while the
stub log says a label is loaded. *Must-die set:* the signal mask; `require_absent` at any deletion site; ABSENT widened to `rc != 0`; rc 113 without the stderr match;
commit `<`→`<=`; `__exit__` dispatch replaced by an exit-code test; `copy2`→`copy` (lt-21: dropping
`-p` survived 59 tests); RETAINED `exit 4`; the render-only guard; COMMITTED's
`except BaseException`. Carry ruling 28 Q5's set forward; record `trap - EXIT` (lt-21 F3, unkilled) as
**retired by construction**. *Replay:* full unpiped suite on the integration tree, plus an old→new
mapping table (each FIX-1..10 assertion against its cell) keeping lt-15's "no case dropped" rule
checkable; lt-90 rows 6/7/10/11/12 rerun.

## Q5 — Scope

`scripts/install_magistrate_watchdog.sh` carries the **same class-2 defect, live today**: `:199-200`
(`bootout … || true`; `rm -f "$plist"`; `exit 0`) is the shape ruling 28 Q2 just cured on the night
uninstall; `:184` removes the plist in `cleanup_failed_install` unchecked; `:306`, `:311-315` bootout
unverified.

**Design now, land later.** Parameterise the transaction by label set from commit one
(no hard-coded pair in the module), so A204 is a one-label caller with only new tests and an unchanged
module, landed as a **separate PR**. *Rejected:* folding A204 into the same PR — this installer arms the
magistrate supervising the night; a regression there blinds the supervisor during the very window the
lane protects.

**Shipped default span list: unchanged** — `INSTALL_SPANS = (("00:00","24:00"),)` (`run_night.py:69`).
*Rejected:* a narrowed default (e.g. the historical 03:00–06:30) — D-181 cl.1 (nothing else about
timing is a rule); adjudication 06 (whole-day default, population flagged to Ed); cold gate 25 Q4 (a
narrowed span is a *different* lane).

## Q6 — Preserve vs discard

**Preserve** — behaviour byte-identical where documented.
1. The single commit gate on `min(selected_span_close, install_close_epoch)` (ruling 25 Q1(c)) and
   synthesis 28/13's POSITIVE RULE — now structural rather than reviewed.
2. Verified bootout before removal (ruling 25 Q3 amended) → `require_absent` tokens.
3. The RETAINED branch verbatim: restore nothing, remove nothing (backup included), name both labels
   and the retained paths, **exit 4** (`:275-278`, `:341-344`).
4. Render-only exemption (ruling 28 Q6.3) — never invokes launchctl, must **not** refuse loaded labels.
   **I4 by construction**: a `NullLaunchctl` adapter raising on any call.
5. Occupancy refusal on **both** labels, exit 3, naming it (`:302-306`).
6. One-pass template substitution (`:244-248`, re-audit 04 R1); MIN_PYTHON subproc (`:64-84`); `cp -p`
   → `copy2` + mtime assertion; write-once refusal (`:283-291`); read-only refusals before `mkdir`
   (`:309`); every Q4 refusal string and code.

**Discard.** The `$?`/EXIT-trap machinery (`:320-356`) incl. `trap - EXIT` (`:330`); three
`print … && loaded=1` idioms (`:273`, `:335`, `:338`); the base64/`(@f)` marshalling (`:85-121`,
`:293-301`); the stale runbook rollback prose (`:1408-1415`). FIX-1..10: keep every **assertion**, drop
the shell scaffolding, ship the mapping table. Rename
`test_clock_advancing_during_backup_removal_preserves_verified_arm` to `control_…` (lt-21: it *is* a
control, hence survives edit 1's reversion).
