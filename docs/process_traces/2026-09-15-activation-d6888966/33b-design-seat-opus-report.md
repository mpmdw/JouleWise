# lt-22 — Opus design seat: a transactional night-agent installer (contract / by-construction lens)

Written **11:52 PDT 2026-09-15** (clock read). Seat: Opus 5, blind (no other seat's output read).
Checkout `/Users/edr/code/JouleWise-wt-design-iw` detached at `073a9763`. Read-only except this file.
Line cites are that checkout unless marked.

**Lens statement.** For each element I name the invariant it makes true *by construction* (the unsafe
state is unrepresentable) and what stays *enumerable* (true only because we checked a list).

---

## Q3 first — executed liveness evidence (mandatory)

Probes run on this machine, read-only, 11:48 PDT:

```
$ launchctl print gui/501/com.joulewise.nonexistent.probe
exit=113
stdout: (empty)
stderr: Bad request.
        Could not find service "com.joulewise.nonexistent.probe" in domain for user gui: 501

$ launchctl print gui/501/com.joulewise.magistrate        # loaded (state = not running)
exit=0
stdout: 66 lines, first line `gui/501/com.joulewise.magistrate = {`
stderr: (empty, 0 bytes)
```

**Three-valued predicate** (the only liveness API in the design):

```
rc == 0                                        -> LOADED
rc == 113 AND stderr matches NOT_FOUND(label,uid) -> ABSENT
everything else (any rc, timeout, OSError)     -> UNKNOWN
NOT_FOUND = 'Could not find service "<label>" in domain for user gui: <uid>'
```

rc 113 alone is **not** sufficient: the first stderr line is the generic `Bad request.`, so 113 is a
request-class code, not a label-specific one. The conjunction is deliberate. By construction: `ABSENT`
is the only constructor accepted by the deletion guard (below), so the lt-21 F2 defect — `print … &&`
reading *any* non-zero (stub 9) as "not loaded" at `install_night_agent.sh:273`, `:335`, `:338` —
cannot be written. Enumerable residue, stated plainly: the rc/message signature is an empirical fact
about this macOS build; it is pinned by one test and must be re-probed on OS upgrade (the same class
as the 25G83 acceptance epoch). The adapter must also **capture** stderr — today `2>/dev/null` throws
away the evidence needed to classify.

**Fake launchctl.** The current stub (`tests/test_install_night_agent.py:76-84`,
`[[ -f "$LAUNCH_LOG.${2:t}" ]]; exit $?`) emits only 0/1 and **cannot express UNKNOWN** — that is why
six rounds of tests never caught F2. Replacement, per label: marker present → rc 0 + a canned
`gui/<uid>/<label> = {` block + empty stderr; marker absent → rc 113 + the two verbatim stderr lines
with label/uid substituted; an error-directive file → that rc with arbitrary stderr. Adversarial cells
that must exist: rc 113 with a *different* message ⇒ UNKNOWN; rc 9 carrying the exact not-found
message ⇒ UNKNOWN; rc 0 with junk stderr ⇒ LOADED.

*Rejected:* keep a two-valued stub and add an "error mode" flag. Rejected — a boolean stub can model
the bug but not the contract; the test must be able to express every (rc, stderr) pair the adapter
classifies, or the classifier is untested at its only interesting boundary.

---

## Q1 — Shape: **(B)**, a Python transaction module; shell reduced to argv parsing

The four rounds did not fail on four bugs; they failed on one topology. Each invariant was enforced by
*inspecting call sites* — and the class reappeared at a **new site** every round (final bootstrap →
`set -e`-skipped EXIT trap → post-gate `rm -rf` at `:374` → `--uninstall` at `:267-272`). Enumeration
cannot terminate against an adversary that is "one more line".

Three devices, each killing one class by construction:

1. **Single mutation channel.** One `LaunchdTransaction` with exactly three mutators
   (`write_plist`, `bootstrap`, `bootout`); nothing else in the module may touch `launch_dir` or call
   launchctl. "Another call site" stops existing. → makes the *site set* closed (precondition of I1/I2).
2. **The gate is a precondition of the mutator, not a statement between mutators.**
   `mutate(op)` = read clock → refuse if `now >= min(selected_span_close, install_close_epoch)` →
   execute → record. `commit()` is callable only from `VERIFIED`, re-reads the clock once, and returns
   a `Committed` token. `main()` returns 0 **iff** it holds that token. → **I1 by construction**: exit 0
   requires a clock read after the last mutation (`mutate` raises once COMMITTED).
3. **Teardown dispatches on transaction state, never on an exit code.** The shell's `teardown` branched
   on `$?` (`:312`), so *any* post-gate failure re-entered it — the ruling-28 Q1b defect where a failed
   `/tmp` cleanup tears down a verified arm. In the module `__exit__` selects its branch from
   `self.state`, which is monotone and set **before** any post-commit statement; the COMMITTED branch
   has no edge back to the unwind branch and wraps cleanup in `except BaseException: warn`.
   → this is synthesis 28/13's POSITIVE RULE ("after the commit gate, no statement may fire teardown's
   failure branch") made structural instead of reviewed.
4. **Proof-carrying deletion.** `require_absent(label) -> Absent` raises on LOADED *and* UNKNOWN;
   `remove_plist(label, proof: Absent)` takes the token. → **I2 by construction**: no call site can
   delete a plist without having proved absence; unknown ⇒ loaded is a type fact, not a convention.

*Rejected: (A) keep zsh, fix the `loaded_state` predicate at the three sites.* It repairs the predicate
but not the topology, and zsh cannot carry devices 2–4: `exit 0` is reachable from any line, there is no
token type, and errexit-inside-a-function skips the EXIT trap (measured, ruling 25 probes). (A) can
make I2 true *at the three enumerated sites* and cannot make I1 or I3 true at all — the same guarantee
shape that has now failed four times. Also rejected: a post-hoc verifier subprocess — it can observe the
bad state but cannot undo it, and its own failure re-opens the class.

**Still enumerable under (B), stated honestly:** the managed label set (two constants); the ABSENT
signature (Q3); a SIGKILL between `bootstrap` and the journal write (mitigated by ordering — write
plists *then* bootstrap, so the crash half-state is files-present = fence-visible = conservative);
whether `bootout` is synchronous (a job still dying reads LOADED/UNKNOWN, both of which refuse — the
race is resolved conservatively, not eliminated).

---

## Q2 — The state machine

States, in order: `PLANNED` → `PREPARED` → `FILES_WRITTEN` → `BOOTOUT_DONE` → `NIGHT_LOADED` →
`BOTH_LOADED` → `VERIFIED` → `COMMITTED`; terminal failures `UNWOUND` and `RETAINED`.

- `PLANNED` — plan/pin/preflight/write-once-record checks and the occupancy refusal done; **no mutation,
  no `mkdir`** (preserves `:309`'s ordering). The occupancy check is `require_absent` on **both** labels
  (ruling 28 Q2; code `:302-306`): an UNKNOWN here refuses (exit 3) rather than proceeding.
- `PREPARED` — journal created under `TMPDIR`: per label, prior plist bytes (or "none") + prior liveness.
- `FILES_WRITTEN` → `BOOTOUT_DONE` → `NIGHT_LOADED` → `BOTH_LOADED` → `VERIFIED` — each edge is one
  `mutate`/`verify`, so the gate fires at every one; the "missed boundary at the final bootstrap" has no
  place to hide.
- `COMMITTED` — single commit predicate, evaluated once.

**Single teardown** (`__exit__`, dispatching on state, signals masked throughout):

| state at failure | launchd left | files left | rc |
|---|---|---|---|
| PLANNED | untouched | untouched | 2 / 3 |
| PREPARED, FILES_WRITTEN | untouched (nothing bootstrapped) | priors restored byte-identical (`copy2`, mtime) | original |
| BOOTOUT_DONE … VERIFIED | bootout both, then `require_absent` both | priors restored | original |
| — same, but either label not ABSENT | left as found | **new plists retained, backup and journal retained** | **4** |
| COMMITTED | both loaded | both new plists | 0 |

**I3 when a prior job was loaded.** It cannot be: the occupancy rule refuses at PLANNED unless both
labels prove ABSENT. So at PREPARED no managed job is loaded, and restoring *files* restores the exact
prior state — the ruling-25 Q3 residual ("a previously loaded dead-man is restored as a file but not
re-loaded") **disappears by construction**, and teardown still never bootstraps.

**Signals.** INT/TERM/HUP handlers raise `Signalled(rc)` (130/143/129), so the one teardown runs;
`signal.pthread_sigmask(SIG_BLOCK, …)` covers the whole unwind — the Python form of the `trap '' INT
TERM HUP` folded by ruling 28 Q4, and because handlers are installed *before* the journal is created it
also closes F4 (`:304-309`, INSTALLER-BACKUP-WINDOW-01) by construction. A SIGKILL mid-restore leaves the
journal, so restore is idempotent and resumable; even unresumed, the half-state is files-present.

---

## Q4 — Migration

**Stale today, must land in the same lane (I5).** `docs/phase_2/derivation_night_runbook.md:1408-1415`
documents `install_span_closed; rolled back com.joulewise.night before dead-man bootstrap`,
`failed to bootstrap com.joulewise.night.deadman; rolled back com.joulewise.night`, and
`launch agent verification failed; rolled back both agents`. **None of those strings exists in
`scripts/install_night_agent.sh` at `073a9763`** (`grep -n "rolled back"` → no match; ruling 25 Q3 step 2
deleted the inline rollbacks). The block's closing sentence — "Every unsuccessful exit after rendering
also removes this attempt's plists and restores prior bytes" — is now **false** for the RETAINED branch,
which deliberately keeps them. Replace that prose with the state table above.

**Refusal strings that survive verbatim** (runbook `:1392-1402`; NIGHT_HANDBACK `:206-208`):
`install_span_closed`, `install_outside_span`, `plan_t0_in_the_past`, `night_agent_already_loaded`,
`plan_outside_custody_root`, `night_plan_malformed`, `plan_schedule_unrepresentable`,
`install_spans_unresolvable_on_day`, `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`;
exit codes 2/3; the summary field set (`now_epoch_s`, `t0_epoch_s`, `install_close_epoch_s`,
`deadman_epoch_s`) and its local-ISO rendering. **New rows to document** (behaviour already in code,
undocumented): the retained-state message + **exit 4** (`:276`, `:342`), and one
`install_liveness_unknown` reason for an UNKNOWN at the occupancy check.

**Callers.** `run_night.py schedule` is unchanged; the module imports `schedule` / `install_close_epoch`
/ `INSTALL_SPANS` directly instead of shelling out (`:153`), which deletes the base64 marshalling at
`:85-121` and the `(@f)` splitting at `:293-301`. The MIN_PYTHON check (`:64-84`) **stays a subprocess** —
its whole point is a different interpreter. Courier prompt / NIGHT_HANDBACK: state that `--uninstall`
(run after every night) exits 4 and retains plists when a label is not provably ABSENT, and that re-running
it is safe (idempotent).

**What the twelve-row gate should require.**
- *Regression matrix as a product, not a list:* {8 states} × {op-nonzero, INT, TERM, HUP, clock past
  selected_span_close, clock past install_close, liveness UNKNOWN, liveness LOADED-after-bootout,
  restore I/O error}. Every cell asserts the 4-tuple (rc; per-label liveness from the stub log; per-plist
  bytes+mtime vs prior; `installed_agent_fence()` over the resulting dir) — never message text alone.
  Structurally unreachable cells are declared unreachable, so a future refactor that reaches one turns RED.
- *One shared cell assertion* (the machine-checkable class-2 statement, impossible to omit per-cell):
  the fence never returns `None` while the stub log says a label is loaded.
- *Mutation must-die set:* removal of the signal mask; removal of `require_absent` at any deletion site;
  `ABSENT` widened to `rc != 0`; `rc == 113` accepted without the stderr match; commit `<` → `<=`;
  `__exit__` dispatch replaced by an exit-code test; `copy2` → `copy` (lt-21's near-miss: dropping `-p`
  survived 59 tests); the RETAINED `exit 4`; the render-only no-launchctl guard; the COMMITTED branch's
  `except BaseException`. Carry ruling 28 Q5's set forward; record `trap - EXIT` (lt-21 F3, unkilled) as
  **retired by construction**, not as killed — it has no Python analogue.
- *Replay:* full unpiped suite on the integration tree; plus the old→new mapping table (every FIX-1..10
  assertion named against its matrix cell) so the lt-15 "no case dropped" discipline is checkable.
- Rows 6, 7, 10, 11, 12 are OPEN in lt-90 and must run on the post-consult head.

---

## Q5 — Scope

`scripts/install_magistrate_watchdog.sh` carries the **same class-2 defect, live today**: `:199-200`
(`bootout … || true`; `rm -f "$plist"`; `exit 0`) is byte-for-byte the shape ruling 28 Q2 just cured on
the night uninstall; `:184` removes the plist in `cleanup_failed_install` with no liveness check; `:306`
and `:311-315` bootout unverified.

**Recommendation: design for it now, land it later.** Parameterise the transaction by label set from the
first commit (no hard-coded pair inside the module), so A204 becomes a one-label caller with only new
tests and an unchanged module — then land A204 as a **separate PR** after the night installer.
*Rejected:* fold A204 into the same PR. Rejected because this installer arms the magistrate that
supervises the night: a regression there blinds the supervisor during exactly the window the lane exists
to protect, and one PR touching both installers makes a red replay cell ambiguous as to which installer
produced it.

**Shipped default span list: unchanged** — `INSTALL_SPANS = (("00:00","24:00"),)` (`run_night.py:69`).
*Rejected:* ship a narrowed default (e.g. the historical 03:00–06:30). D-181 cl.1 says nothing else about
timing is a rule; adjudication 06 already ruled the whole-day default with population flagged to Ed; and
cold gate 25 Q4 established a narrowed span is a *different* lane. I5 forbids inventing it here.

---

## Q6 — Preserve vs discard

**Preserve (semantics; observable behaviour byte-identical where documented).**
1. The single commit gate on `min(selected_span_close, install_close_epoch)` (ruling 25 Q1(c)) and
   synthesis 28/13's POSITIVE RULE — now structural rather than reviewed.
2. Verified bootout before any removal (ruling 25 Q3 as amended) → `require_absent` tokens.
3. The RETAINED branch verbatim in behaviour: restore nothing, remove nothing (including the backup),
   name both labels and the retained plist paths, **exit 4** (`:275-278`, `:341-344`).
4. Render-only exemption (ruling 28 Q6.3): never invokes launchctl and must **not** refuse loaded labels.
   **I4 by construction**: render-only builds the transaction with a `NullLaunchctl` adapter that raises
   on any call and never enters PREPARED.
5. Occupancy refusal on **both** labels, exit 3, message naming the label (`:302-306`).
6. One-pass template substitution (`:244-248`, re-audit 04 R1) and the MIN_PYTHON subprocess (`:64-84`) —
   independent defect cures, unrelated to the transaction.
7. `cp -p` mtime preservation → `copy2` plus an explicit mtime assertion in the matrix.
8. Write-once record refusal (`:283-291`); all read-only refusals before any `mkdir` (`:309`).
9. Every refusal string and exit code in Q4's survivor list.

**Discard.** The whole `$?`/EXIT-trap machinery (`:320-356`) including `trap - EXIT` (`:330`); the three
`print … && loaded=1` idioms (`:273`, `:335`, `:338`); the base64/`(@f)` marshalling (`:85-121`,
`:293-301`); the stale runbook rollback prose (`:1408-1415`). FIX-1..10: keep every **assertion**, discard
the shell-specific scaffolding, and ship the mapping table. Rename
`test_clock_advancing_during_backup_removal_preserves_verified_arm` to a `control_…` name — lt-21 showed
it survives edit 1's reversion because it *is* a control, and the name invites misreading it as a
regression.
