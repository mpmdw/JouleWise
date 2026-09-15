# 10 — Cold Fable gate ruling, packet 28 (INSTALL-WINDOWS-MULTI-01 round 3), head `9a7bacdf`

Judge: Fable 5.1, fresh non-interactive session, foreground only, no subagents, 2026-09-15 (clock not read; ~35 min).

**Disclosure.** Auto-loaded before I read anything: `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, the auto-memory index `MEMORY.md` (pointers only; none opened). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any memory file, any narrative doc. Read: packet, charter, exhibits A–H, `scripts/install_night_agent.sh` (whole), `tests/test_install_night_agent.py` `:60-200,:755-1044`, `scripts/magistrate_watchdog.py` via `installed_agent_fence` in the probes only.

**Validator.** Run 1 (charter sha `…a880…`): `REFUSE`, `charter_trusted_observed_mismatch`, rc=2. Run 2 (`…a870…`): `PASS`, rc=0, charter observed `099de884…c95d81`, packet `6e0514da…4b35`, all eight exhibit digests observed = expected. Method: `scripts/validate_gate_packet.py`. I judge on that PASS. `git rev-parse HEAD` = `9a7bacdf25c2…`.

## Executed probes (fake launchctl and a fake `rm` on the fixture PATH; `HOME` under a tempdir; no real bootstrap; nothing under `~/Library/LaunchAgents` or `~/night-custody`; files only under `/tmp/coldgate-iw2/`)

| Probe | Result |
|---|---|
| Q1b: priors present; the first `rm -rf <backup>` after the gate (`:374`) exits 1 | **rc=1; "validated pins…" on stdout; both labels booted out; prior plists restored; fence = prior plan.** A verified install torn down. |
| Q1a: spans `00:00–12:01, 12:01–24:00`; clock +3600 s during the `:374` `rm` | rc=0; both loaded; both plists present; no backup dir. |
| Q2a: `--uninstall`, both bootouts exit 1, both jobs loaded | **rc=0; plists=[]; both still loaded; `installed_agent_fence()=None`.** F2 reproduced. |
| Q2b: next install, night label stuck loaded, no plists | rc=3 `night_agent_already_loaded` (`:294`); refusal. |
| Q2c: next install, ONLY dead-man stuck; stub where bootstrap of a loaded label fails (real launchd shape, not executed against launchd) | rc=4 (teardown retained branch); dead-man still loaded; both NEW plists retained; fence sees the new plan. |
| Q2c': same, stub where bootstrap of a loaded label succeeds | **rc=0; both loaded; both plists** — the `:294` guard checks the night label only. |
| zsh 5.9 EXIT-trap function `return 4` after `exit 3` | rc=3 |
| zsh 5.9 EXIT-trap function `exit 4` after `exit 3` (with and without `trap - EXIT`) | rc=4, trap body ran once |

## Q1 — F1: option (a), plus the definition. Not a new class; not a same-signature class-1 finding.

Definition ruled: the class-1 invariant covers machine state the fence and launchd read — the two loaded jobs and the two plist files. A clock read after the LAST such mutation that satisfies both bounds is the commit; removal of a `TMPDIR` backup directory is not a mutation of that state. So Q1a (rc=0, both loaded, both plists, no backup) is the intended installed state, and the auditor's clock-half of F1 is definitional, not class 1. The lieutenant's stop was procedurally right (exhibit A said YES); on the merits the delta's class-1 YES does not hold.

The real defect is Q1b: a failable statement after the commit gate whose failure re-enters `teardown` and destroys a verified arm (`:374` with `trap teardown EXIT` still armed at `:342`, `teardown` `:312` takes any non-zero result). That is incomplete application of ruling 10 Q3 step 1 (exhibit E: "in every case `rm -rf "$plist_backup"`" belongs in `teardown`). Option (a). Dictation:

1. Delete `scripts/install_night_agent.sh:374` (`rm -rf "$plist_backup" || exit 1`). The success `print` at `:373` is the last statement.
2. Replace `:312` (`(( result != 0 )) || return 0`) with:
   ```
   if (( result == 0 )); then
     rm -rf "$plist_backup" 2>/dev/null || print "warning: backup directory not removed: $plist_backup" >&2
     return 0
   fi
   ```
   On success `teardown` removes the backup, never calls launchctl, never changes the exit status.
3. Regressions (RED at `9a7bacdf`, GREEN after), fake `rm` on the fixture PATH exactly as my probes: (i) backup removal fails after the gate → rc=0, both loaded, both plists present, one warning line on stderr, no launchctl call after the two verification `print`s; (ii) clock advance during backup removal → rc=0, both loaded, both plists, no backup dir. Mutation: restoring `:374` must turn (i) RED; deleting the new `rm` must turn `test_success_removes_backup_without_teardown` RED (it asserts the backup is gone, `:1037`).

Residual, NIT, no action: a `print` to a closed stdout at `:373` would kill the shell with SIGPIPE (no EXIT trap), leaving rc=141 with both loaded and both plists present. The fence sees the plan; the caller sees failure and the next install is refused at `:294`.

## Q2 — F2: option (i), scope expansion, one dictated block; not a contract change to exhibit H.

Deciding evidence: Q2a executed on this checkout; `:269-272` swallows both bootouts, deletes both plists unconditionally, exits 0. `--uninstall` runs after every night; the state it produces is the one the fence cannot see (exhibit E Q3). The cure is the discipline already built and tested at `:318-330`. Exhibit H's "`--uninstall` unchanged" sat in the label-collision row: it decided fixed labels plus refuse-if-loaded, not that uninstall may never be touched. Adding verified bootout alters no H decision; the magistrate records it as a scope expansion of this lane's WRITE_SCOPE (same three files).

Dictation, replacing `:269-272`:
```
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  "$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  uninstall_loaded=()
  for label in "$night_label" "$deadman_label"; do
    "$launchctl_bin" print "gui/$uid/$label" >/dev/null 2>&1 && uninstall_loaded+=("$label")
  done
  if (( ${#uninstall_loaded[@]} )); then
    print "uninstall: still loaded after bootout: ${uninstall_loaded[*]}; retained plists: $night_plist $deadman_plist" >&2
    exit 4
  fi
  rm -f "$night_plist" "$deadman_plist"
  exit 0
```
Regression mirroring cell 9: stub bootout rc=1 leaving the marker → rc=4, both plists still present, fence still sees the plan, the last four launchctl calls are bootout/bootout/print/print; plus the one-label variants; plus the existing `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl` amended from 4 calls to 4 bootout/print pairs = 4 lines still (its stub already answers `print` from the marker; assert the two prints follow the two bootouts). Mutation: deleting the `exit 4` line must turn the new cell RED.

Stuck-job answer (the packet's sub-question): a stuck NIGHT job refuses the next install (Q2b, exit 3). A stuck DEAD-MAN job is NOT refused by `:294`; under real launchd the second bootstrap of a loaded label fails and the run ends in the retained branch (Q2c, rc=4, conservative, fence sees the new plan); under a permissive launchd it double-arms (Q2c'). Real-launchd bootstrap behaviour was NOT EXECUTED (forbidden). Dictate one line so the refusal does not depend on launchd: at `:294` check both labels — replace the condition with `[[ -z "$render_only" ]] && { "$launchctl_bin" print "gui/$uid/$night_label" >/dev/null 2>&1 || "$launchctl_bin" print "gui/$uid/$deadman_label" >/dev/null 2>&1; }` and name the loaded label in the message. Regression: dead-man-only preloaded → rc=3, zero bootstraps. Note this changes the ordinary path's bootout at `:356`: a prior dead-man that is loaded now refuses instead of being quietly booted out; that is the FIX-4 occupied-label rule applied evenly and it is what the uninstall path guarantees is empty after every night.

## Q3 — round 3: AUTHORISED with justification; stop condition stated.

Charter §9 justification: the two consecutive YES answers are not the same failure twice. Round 2's mechanisms are real (exhibit A reversions). F1's clock half is definitional (Q1); its rm half is a new, different-class residue three lines below round 2's own change; F2 is a site every brief excluded. Neither says "the fix did not take". Round 3 = four dictated edits, no new structure: Q1 (delete `:374`, success branch in `teardown`), Q2 (uninstall verified bootout; `:294` both labels), Q4 F3 (one line). One seat, WRITE_SCOPE the same three files, regressions as dictated, then delta 3 with the isolated-reversion protocol AND the still-open re-run of lt-04's 22-survivor list (exhibit A) at the round-3 head.

Stop condition: if delta 3 reports ANY class-1 or class-2 site on the install or uninstall path at the round-3 head, there is no round 4. The lane does not land with a live class-1/2 site as a "registered lane" (that is the defect the lane exists to remove). The next spend is a redesign consult (three seats, Astra + Opus + blind Fable) on a transactional installer: one Python state machine with a single commit and a single teardown, the shell script reduced to argument parsing. The magistrate decides to stop and convene, records it, and informs Ed in the PR body; Ed is not blocked and may override. Should-fix residue whose failure state is conservative (F4 shape) may land as registered lanes.

## Q4 — F3 fold into round 3; F4 register.

F3 (`:332-338`): a TERM/INT/HUP during restoration runs the `exit 143` trap mid-loop; the backup survives (the `rm -rf` at `:339` is not reached) but the second plist stays at current bytes and the next uninstall deletes it — prior bytes lost. Closure shape, one line at the top of `teardown` after `local result=$?`: `trap '' INT TERM HUP`. Regression: stub sends TERM from the first restore `cp` (fake `cp` on PATH) → both priors byte-identical, no backup dir, rc unchanged from the cell's expected code. F4 (`:304-309`): the unguarded window leaves prior plists intact, no job loaded, one leaked backup dir. Conservative; the cure is a reorder of the trap block above `mktemp` with `plist_backup=""` initialised so `:314` returns early. Register as its own NIT lane (INSTALLER-BACKUP-WINDOW-01); not this round.

## Q5 — REFUSE (packet defect).

Exhibit A names counts only (8 `teardown`, 3 production-tail survivors) and no survivor. I cannot rule which must die without the list. Minimum cure: the packet carries the auditor's survivor list from `lt-10-delta2.md` verbatim (mutation, line, cell outcomes). Non-binding note for that packet: any survivor that removes `trap - EXIT` (`:316`), the `exit 4` (`:329`), either `print` re-read (`:321,:324`), the `-p` on `cp` (`:334`), or the `[[ -z "$render_only" ]]` guard (`:317`) must die before landing; survivors changing only the `:328` diagnostic wording are text-only.

## Q6 — the three round-2 rulings.

1. Oracle: **AFFIRM.** The stub asserts both plists exist at every bootout (`tests/test_install_night_agent.py:849-853`) and `_assert_teardown` pins the final four calls (`:882-887`); stronger than the TERM-only oracle.
2. `exit 4`: **AFFIRM.** Measured above: `return 4` leaves rc=3, `exit 4` gives rc=4, trap body runs once with or without `trap - EXIT`. Ruling 10's requirement was the observable status; the verb change delivers it.
3. Render-only: **AFFIRM** the contract (render-only never invokes launchctl, `:317`; teardown does file restore/removal only). The installer must NOT refuse render-only when a label is loaded: render-only writes to its own directory, never bootstraps, cannot create the fence-blind state, and the check itself would be a launchctl call the contract forbids. Validating the next plan while a night is armed is the lane's purpose.

## Packet hygiene

One defect: Q5 unnamed survivors (REFUSED above). The packet's "same-signature YES again" framing is carried neutrally with both halves of F1; I disagree with the class-1 half on the merits and say so in Q1.

## Severity summary

BLOCKER open at `9a7bacdf`: Q1b (verified install torn down on backup-removal failure) and Q2a (uninstall exits 0 with jobs loaded and plists deleted), both executed. MATERIAL: `:294` night-only check (Q2c'). NIT: F4; SIGPIPE residual. REFUSE: Q5 only. No rule, decision-log, or doctrine text amended; all text above is for the magistrate to record. Probe files under `/tmp/coldgate-iw2/`; one retained backup dir from probe Q2c removed by me; the checkout is untouched apart from this ruling.
