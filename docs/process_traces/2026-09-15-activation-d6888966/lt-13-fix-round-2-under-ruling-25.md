# lt-13 — Fix round 2, under cold-gate ruling 25 as amended

Written 09:08 PDT 2026-09-15 (clock read). Bookkeeping worktree fast-forwarded
to `origin/main` `e7950d20` to read the packet.

## What authorises this round

`25-coldgate-packet-install-windows/10-coldgate-fable-ruling.md` (cold Fable,
fresh session, at `df86cee6`), `12-opus-pairing-refuter-on-ruling-10.md` (Opus
contract lens, independent answers written BEFORE reading the ruling), and
`13-magistrate-synthesis-ruling-10-with-opus-amendments.md`, which adopts the
ruling with the Opus amendments and is authoritative. Verdicts converged on all
six questions; no overrule, no dissent.

The escalation trigger the lieutenant stopped on (lt-05) is satisfied, and the
synthesis says why in one clause: **the structure changes, not the call site.**
A fifth point check would have been round three; a postcondition is a different
mechanism.

Two facts from the ruling materially correct my hand-back:

1. **My "latent under the shipped whole-day default" framing was WRONG.** The
   cold judge's P-F3 produced class 2 (loaded job, no plist, fence blind) under
   the DEFAULT span; and the Opus refuter's CASE 2 shows class 1 crossing under
   the default too, because `check_schedule` tests
   `now >= install_close_epoch_s` in EVERY mode (`:186-188`) and
   `install_close_epoch` exists for every plan. So Q4 option (ii) — land with
   narrowed span lists refused — had no premise: the exit-0-both-loaded path is
   reachable on the shipped default. I recorded that option as available and it
   was not. Recorded as my error.
2. Q4 is **(i) close the blocker first**, and option (ii) would not have been a
   D-181 reinterpretation (a mechanism limit is a fact, not a rule) — but it
   would have left kernel clauses "accept a list of install spans" and "tests
   pin the span list" unmet, i.e. a different lane.

## What I dictated (brief `/tmp/magistrate-d6888966/brief-07-fix-round-2.md`)

ONE Astra xhigh seat, workspace-write, detached pid 15084, launched 09:08:06 in
the integration worktree at `df86cee6`. `WRITE_SCOPE` exactly
`["scripts/install_night_agent.sh","tests/test_install_night_agent.py","docs/phase_2/derivation_night_runbook.md"]`.

**FIX-A (Q1(c))** — one line, after the verification block ending `:358` and
before the success `print` at `:360`:
`check_schedule close "$selected_span_close" || exit $?`. The invariant is a
POSTCONDITION: the installer exits 0 only if a clock read taken after the LAST
mutation and its verification still satisfies both bounds, which proves the
bound for every prior mutation and closes the call-site set by construction. The
`initial` check stays (it emits `selected_span_close` as its eighth field); the
three existing `close` rechecks at `:336,:338,:343` may stay as early refusals
and stop being load-bearing; no inline `bootout` at the gate; no new constant,
literal or bound. Five regressions with the advance injected AT THE DEAD-MAN
BOOTSTRAP — one boundary, two boundaries, plan-cutoff-first,
selected-close-first, and exactly-at-close (which also kills the `>=`→`>`
survivor from lt-04 F4) — each rc=2, `install_span_closed`, zero loaded labels,
zero plists, zero backup dirs; deleting the gate line must turn all five RED.

**FIX-B (Q3 as amended)** — one idempotent `teardown` replacing
`rollback_install_files` at `:310-323`, with `trap teardown EXIT` the SOLE
invoker, every failure path an explicit `exit N`, both `render` calls becoming
`render … || exit 1` (measured: zsh 5.9 errexit from inside a function skips the
EXIT trap), the inline bootout rollbacks at `:344,:349,:355-356` deleted, no
`always` blocks (measured: not run in either failure mode), teardown never
bootstraps. **The Opus amendment is the load-bearing part:** after both
bootouts, RE-READ `launchctl print` for each label; if either is still loaded,
restore NOTHING and remove NOTHING including `$plist_backup`, print both labels
and the retained plist paths, and return a DISTINCT non-zero status; only when
both report not-loaded may restore / `rm -f` / `rm -rf "$plist_backup"` run.
Without it the teardown's own bootout failure produces exactly the state class 2
is about — the refuter executed it: exit 3, `loaded=['com.joulewise.night']`,
`plists=[]`, and a success-shaped "rolled back" message.

Nine-cell parametrised matrix: TERM/INT/HUP at the night bootstrap (143/130/129),
read-only prior dead-man plist (1), night bootstrap rc=1 (3), dead-man bootstrap
rc=1 (3), verification print rc=1 (3), commit-gate crossing (2) — each asserting
no `launchctl.log.<label>` marker for either label, every plist absent or
byte-equal to prior bytes, no leaked backup dir, and `installed_agent_fence()`
returning `None` or the prior plan without raising; **plus cell 9, the inverse**:
`bootout` rc=1 → non-zero exit AND both plists still PRESENT AND the fence still
SEES the plan. Mutation: reordering `rm` before `bootout` must turn the TERM cell
RED by asserting from the stub log that the two bootout lines are the last two
launchctl calls.

**FIX-C (Q6)** — exactly one runbook sentence appended at `:1297`: "Same-day
successors are a machinery capability; for the three FAIL-route registration
nights §3 item 3 still requires distinct calendar days." **§3 itself stays
byte-identical**, SHA-256 `71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`,
verified before and after. The §3 item-3 cross-reference the ruling drafted is a
SEPARATE Ed-visible lane (RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01) and was explicitly
withheld from this seat.

Q2 carried as a prohibition: no `MAX_INSTALL_DURATION_S`, no derived margin
feeding a refusal. Under Q1(c) the bound is OBSERVED, not predicted, so nothing
needs to carry it; the plan-side slack is already `INSTALL_CLOSE_MARGIN_S = 3600`
and the span-side slack is deliberately zero by D-180 cl.1.

Q5 (the acceptance-clause-(c) narrowing I ruled in lt-03) was AFFIRMED by both
seats; the kernel text is the magistrate's to record, not mine.

## Process observation carried from both seats, not mine to decide

The cold judge disclosed that the harness auto-loaded `~/.claude/CLAUDE.md` and
the worktree's tracked `CLAUDE.md` — both doctrine — before it read anything.
The Opus seat flags that this weakens rule 11's doctrine-free premise, since no
worktree choice removes the user-level file. Recorded in the synthesis for the
council's fresh-eyes sweep / Ed.
