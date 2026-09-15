# lt-18 — Round 3, dictated verbatim from cold-gate ruling 28

Written 10:36 PDT 2026-09-15 (clock read). Bookkeeping worktree fast-forwarded
to `origin/main` `63db085b` to read packet 28.

## Authority

`28-coldgate-packet-install-windows-round-3/10-coldgate-fable-ruling.md` (cold
Fable, fresh session, at `9a7bacdf`, validator PASS on the corrected charter
sha), `12-opus-pairing-refuter-on-ruling-10.md` (Opus, independent answers
written first), and `13-magistrate-synthesis-…md`, which is authoritative.
Convergent on all six questions; no overrule, no dissent.

## What the gate found that changes my own hand-back

**My class-1 report was half wrong, and the ruling says so on the merits.** The
class-1 invariant is defined to cover *machine state the fence and launchd read*
— the two loaded jobs and the two plist files. Removal of a `TMPDIR` backup
directory is not that state, so the auditor's clock-half of F1 (rc=0, both
loaded, both plists, no backup dir) is the INTENDED installed state and is
definitional, not class 1. My stop was procedurally right — exhibit A said YES
and the rule is judgment-free — but the delta's class-1 YES does not hold.

**The half I flagged myself is the real defect, and the gate reproduced it:**
with priors present and the post-gate `rm -rf` exiting 1, the result is rc=1,
"validated pins…" already on stdout, both labels booted out, prior plists
restored, fence showing the prior plan. A verified arm destroyed by a `/tmp`
cleanup failure. The ruling classifies it as incomplete application of ruling
10's own Q3 step 1, which had put `rm -rf "$plist_backup"` inside `teardown`
"in every case" — round 2 left a copy outside it.

**F2 is confirmed on the merits and the scope question is answered:** exhibit H's
"`--uninstall` unchanged" sat in the label-collision row and decided fixed labels
plus refuse-if-loaded — not that uninstall may never be touched. The magistrate
records a WRITE_SCOPE expansion over the same three files. Executed at this head:
uninstall with both bootouts failing gives rc=0, both plists deleted, both jobs
loaded, fence `None`.

**A material finding neither I nor the delta had:** `:294` checks the NIGHT label
only. With only the dead-man stuck loaded, a permissive launchd double-arms
(the gate's probe Q2c' — rc=0, both loaded, both plists). Real-launchd bootstrap
behaviour was not executed, which is exactly why the ruling dictates a one-line
both-label check rather than relying on launchd to fail.

## The positive rule (Opus amendment, adopted)

> **After the commit gate, no statement may fire `teardown`'s failure branch.**

The Opus seat's reasoning is the one that matters for this lane: ruling the
DEFINITION without stating a positive rule "closes a SITE and leaves the class
enumerable — this lane's exact failure mode." It goes verbatim into the
docstring of the regression that pins it.

## Dictated to one Astra xhigh seat (pid 80476, 10:36:27), brief `/tmp/magistrate-d6888966/brief-11-round-3.md`

1. **EDIT 1 (Q1)** — delete `:374`; replace the `:312` guard with the success branch that removes the backup, warns on failure, `return 0`, never calls launchctl, never changes the status. Regressions (i) post-gate backup-removal failure → rc 0, both loaded, both plists, exactly one warning line, no launchctl call after the two verification prints; (ii) clock advance during removal → rc 0, both loaded, both plists, no backup dir. Mutations: restoring `:374` turns (i) RED; deleting the new `rm` turns `test_success_removes_backup_without_teardown` RED.
2. **EDIT 2 (Q2)** — the uninstall block verbatim (bootout both, re-read `print` both, retain and `exit 4` if either is loaded, else `rm -f` both and `exit 0`), plus `:294` checking BOTH labels with the loaded label named. Regressions: cell-9 mirror at rc 4 with both plists retained, the fence still seeing the plan, and the last four launchctl calls `bootout/bootout/print/print`; the one-label variants; dead-man-only preloaded on install → rc 3, ZERO bootstraps; `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl` amended to bootout/print pairs. Mutation: deleting `exit 4` turns the new cell RED.
3. **EDIT 3 (Q4-F3)** — `trap '' INT TERM HUP` as the first line of `teardown` after `local result=$?`. Regression: TERM from the first restore `cp` → both priors byte-identical, no backup dir, rc unchanged from the cell's expected code.

**Named in the brief so the seat cannot "fix" it the wrong way:** the tracked
assertion at `tests/test_install_night_agent.py:216`
(`assertEqual(3, … "print ")`) legitimately becomes **4**, because edit 2B adds a
second occupancy print. The Opus seat predicted the seat would otherwise
"fix" the assertion; the brief instructs the opposite in those words. It also
carries the Opus clearance that the dictated `for … && arr+=()` block does not
trip `set -e` on zsh 5.9, so the seat does not restructure it.

Explicitly withheld: the render-only contract (which must NOT refuse loaded
labels — validating the next plan while a night is armed is the lane's purpose),
`:304-309` (registered as INSTALLER-BACKUP-WINDOW-01), and any new structure.

## Carried forward, NOT actioned — for the magistrate

The Opus refuter records a MATERIAL addition the packet does not carry:
**`scripts/install_magistrate_watchdog.sh:199-201` has the same shape** —
`bootout … || true`, `rm -f "$plist"`, `print "uninstalled"`, `exit 0` — for the
magistrate's own agent, and "whatever lane takes F2 must cover BOTH installers
or the class closes half-way" (read, not probed). The adopted synthesis does not
put it in round 3 and my direction says nothing else is in scope, so the seat
was explicitly forbidden to touch it. **It needs a lane.**

## The stop condition I am now under (judgment-free, adopted verbatim)

Delta 3 answers same-signature YES if, **as an executed case at the round-3
head**, either:
- **class 1** — the installer exits 0 with either label loaded while a clock read taken after the commit gate is at or past `min(selected_span_close, install_close_epoch)`; or
- **class 2** — any path in `scripts/install_night_agent.sh` ends with a label loaded and its plist absent, **or** exits 0 while a label it attempted to bootout is still loaded.

On YES there is no round 4: I launch no fix seat and hand back; the magistrate
convenes the redesign consult (three seats on a transactional installer — one
Python state machine with a single commit and a single teardown, the shell
reduced to argument parsing) and emails Ed. **The count is per CLASS, not per
site.** The decider is the magistrate, not me.
