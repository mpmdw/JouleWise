# lt-15 — Delta re-audit of fix round 2, and the SECOND same-signature stop

Fresh auditor, no part in writing the code. Astra `xhigh`, detached pid 37686,
launched 09:42:53, returned 10:03 (clock reads), worktree
`wt-ref-iw-execution` detached at `5649d494`. Brief
`/tmp/magistrate-d6888966/brief-10-delta2.md`; output
`/tmp/magistrate-d6888966/lt-10-delta2.md`.

## The two isolated reversions the magistrate required — BOTH behave correctly

| Reversion | Result |
|---|---|
| Revert ONLY the commit-gate line | **All five FIX-A cases RED** (one boundary, two boundaries, plan-cutoff-first, selected-close-first, exactly-at-close) |
| Revert ONLY the bootout-verification block | **Cell 9 RED with and without priors**, and the reverted code reproduces the original class-2 state exactly: `rc=3; both labels loaded; plists=[]; installed_agent_fence()=None` |

So the two new mechanisms are real and load-bearing: each regression genuinely
fails against its own production change removed. That was the single most
important thing to establish, and it holds.

Protected material also holds: §3 byte-identical at SHA-256
`71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`; only the
installer, its tests and the runbook changed; no new `max`/`min` and **no new
duration constant** (Q2 respected). The one authorised existing-test edit is
judged **stronger** than what it replaced (exact bootout/print sequence plus both
labels and both plists absent), with no case dropped and no other pre-existing
test, assertion or fixture touched.

## SAME-SIGNATURE STATEMENT — the auditor answers YES, on both classes

> "Class 1: another success path with mutation after the last clock read.
> Class 2: missed uninstall call site deletes plists while jobs remain loaded."

### F1 — blocker, NEW this round. `scripts/install_night_agent.sh:372-374`

The commit gate is at `:372`, the success `print` at `:373`, and
`rm -rf "$plist_backup" || exit 1` at **`:374` — after the gate**. The auditor's
reproduction wraps `rm` so it advances the controlled clock past the plan close
and then execs `/bin/rm`: **rc=0 with both jobs loaded at close.**

**The lieutenant read the code and finds a second, worse consequence the auditor
did not name.** That trailing `|| exit 1` runs with `trap teardown EXIT` still
armed. If the temp-directory cleanup fails for any reason, the script exits 1
*after having printed success*, teardown sees a non-zero result, bootouts BOTH
labels and restores or removes both plists — **a correctly installed, verified
night is torn down because a `/tmp` cleanup failed, with "validated pins…"
already on stdout.** Whatever one concludes about the clock-crossing framing,
the success path performing a failable operation after its own commit gate is
the defect, and it is this round's.

For the record, the lieutenant's read of the clock half specifically: the
backup directory lives under `TMPDIR` and its removal mutates no launchd state,
so "both jobs loaded, both plists present" at exit is the *intended* installed
state and the bound did hold at the last machine-state mutation. Whether that
makes F1 class 1 proper or a definitional question about "mutation" is for the
adjudicator; **the lieutenant does not adjudicate it downward**, and the
teardown consequence above is not definitional at all.

### F2 — blocker, PRE-EXISTING, at a call site this lane never touched. `:267-272`

```
"$launchctl_bin" bootout "gui/$uid/$night_label"    2>/dev/null || true
"$launchctl_bin" bootout "gui/$uid/$deadman_label"  2>/dev/null || true
rm -f "$night_plist" "$deadman_plist"
exit 0
```

`--uninstall` swallows both bootout failures with `|| true`, then removes both
plists unconditionally and **exits 0**. Executed by the auditor with fake
bootouts returning 1 and both jobs still loaded: ordinary uninstall, and
uninstall combined with render-only, both **return 0, delete both plists, and
yield `installed_agent_fence()=None`** — a loaded job, no plist, the fence blind,
and a success exit status. The lieutenant read `:267-272` and confirms the
control flow independently.

This is class 2 exactly, and it is not hypothetical: `--uninstall` runs in the
real harvest flow after every night. It is PRE-EXISTING — the original design
adjudication listed `--uninstall` as unchanged, every brief in this lane kept it
out of scope, and cold-gate ruling 25's Q3 addressed the install path's teardown
only. The verified-bootout discipline this round built for `teardown` is exactly
what `--uninstall` lacks.

### F3, F4 — should-fix, both PRE-EXISTING

- **F3** (`:332-345`): a signal DURING plist restoration leaves the first plist restored, the second at current bytes, and the backup gone — the un-restored prior bytes are lost. Reproduced at `df86cee6` as well, so not this round's. Both jobs were unloaded at this head, so the fence is not blinded.
- **F4** (`:304-309`): the backup `cp` runs BEFORE the INT/TERM/HUP traps are installed, so a signal in that window is unguarded (TERM=-15, INT=-2, HUP=1). Prior plists and the backup survive and no job is loaded, so the state is conservative.

### Mutation sweep of the new code

`teardown`: 50 mutations, 42 distinguished, **8 survivors**. Production tail: 24
mutations, 21 distinguished, **3 survivors**, all three caught by the function
probes. No new `max`/`min` and no duration constant exist in the diff.

## Verdicts, with the lieutenant's correction to one of them

| Item | Auditor | Lieutenant |
|---|---|---|
| FIX-A | not_closed (F1) | stands |
| FIX-B | not_closed (F2 at the uninstall site) | stands — but note F2 is pre-existing and out of this lane's dictated scope |
| FIX-C | "not_closed — cannot certify" | **CLOSED, lead-verified at the bench** |
| render-only exemption | closed | stands |

**FIX-C was a briefing defect of mine, not a code defect.** I pointed the auditor
at `…/25-coldgate-packet-install-windows/…` and at `lt-04`, which live on
`origin/main` and were NOT present in its checkout of the int branch (its flag
G1). It therefore could not compare the landed sentence with the ruling's text,
and for the same reason could not re-run lt-04's 22-survivor list. I closed the
first gap myself at the bench: the ruling's sentence is present **verbatim,
exactly once**, at the dictated position, and the round's entire runbook diff is
that one line. The second gap — re-running the previous 22 survivors against
this head — remains OPEN. I have since merged `origin/main` into the int branch
so the packet resolves for any future auditor.

Auditor flags G2 (three commits in the interval, not the four I stated — I
miscounted) and G3 (`ps` denied, so no process census) are both correct.
