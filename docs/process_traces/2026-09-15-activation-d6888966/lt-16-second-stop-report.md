# lt-16 — SECOND same-signature stop; no round 3 launched

Written 10:08 PDT 2026-09-15 (clock read). **Final int head: `9a7bacdf`** on
`int/2026-09-15-install-windows`, pushed.

## The direction, and what I did with it

The magistrate's resumption said: *"If the delta finds the same signature again,
STOP and report — no round 3."* The delta answered **YES** on both classes. I
stopped. No fix seat was launched after `lt-10`, and I did not adjudicate either
blocker downward.

I did four things after the stop, none of which is a fix round, and I name them
so the boundary is auditable:

1. **Bench-verified FIX-C myself**, closing a gap my own briefing created (the auditor could not see the ruling text). Verbatim sentence, once, at the dictated position, one-line runbook diff.
2. **Merged `origin/main` into the int branch** so the cold-gate packet and the lt-* records resolve inside the integration tree for the next auditor. `origin/main` had advanced to `dfb627c1` and carried CODE (the GAMMA root-keys fix, PR #339), not only bookkeeping — so the int head moved from `5649d494` to `9a7bacdf`.
3. **Re-ran the six lane modules after that merge** — `test_install_night_agent`, `test_run_night`, `test_magistrate_watchdog`, `test_night_gate`, `test_docs_freshness`, `test_gen_state`, each separately, **all OK** (lieutenant-run, 10:06 PDT).
4. Wrote `lt-15` and this record.

## Why I did NOT run rows 6, 9 and 10

The direction gates them on a clean delta. The delta is not clean, and the head
will change again once the blockers are ruled on, so a fresh Opus counter-review
and a ~55-minute full replay would both be spent on a head nobody will merge.
**Row 9's existing evidence is now STALE**: my replay (6094 tests PASS) was taken
at `df86cee6`, three commits and one main-merge ago. `lt-90`/`lt-91` are marked
accordingly.

## What the magistrate must rule on

### Blocker F1 — `install_night_agent.sh:372-374`, NEW this round, genuinely ours
The success path does work AFTER its own commit gate: gate at `:372`, success
`print` at `:373`, `rm -rf "$plist_backup" || exit 1` at `:374`. Two distinct
consequences:
- the auditor's: advancing the clock during that `rm` yields **rc=0 with both jobs loaded at close**;
- **mine, and I think the more serious**: that `|| exit 1` runs with `trap teardown EXIT` armed, so a failed temp-directory cleanup exits non-zero *after* "validated pins…" has printed, teardown sees a non-zero result, and **a correctly installed, verified night is bootouted and its plists removed**. A successful arm destroyed by a `/tmp` cleanup failure.

The obvious shapes are one line each — move the `rm` before the gate, or make it
non-fatal (`rm -rf "$plist_backup" || true`) and clear the trap on success —
**and that cheapness is precisely why I did not do it.** The rule exists for the
round where the fix looks like one line.

### Blocker F2 — `install_night_agent.sh:267-272`, PRE-EXISTING, out of this lane's scope
`--uninstall` swallows both bootout failures with `|| true`, removes both plists
unconditionally, and exits **0**. Executed: fake bootouts returning 1 with both
jobs loaded → **rc 0, both plists deleted, `installed_agent_fence()=None`** — a
loaded job with no plist, the fence blind, reported as success. Class 2 exactly,
at the one call site every brief in this lane excluded, that the original design
adjudication recorded as "unchanged", and that ruling 25's Q3 did not reach.
`--uninstall` runs in the real harvest flow after every night.

Its cure is the discipline this round already built and proved for `teardown`:
bootout, **re-read `launchctl print`**, and refuse to delete a plist under a
still-loaded job. The mechanism exists and is tested; it simply is not wired
into the uninstall path.

**Scoping question for the magistrate, which is yours and not mine:** F2 is a
pre-existing defect outside the lane's WRITE_SCOPE and outside ruling 25's
questions. Whether it (a) blocks this lane, (b) becomes its own registered lane,
or (c) is folded in under a scope expansion, is a decision about scope and
severity that rule 11 reserves from me. I record only that it is real, live, and
of the same class the lane exists to eliminate.

### Should-fix, both pre-existing
- **F3** (`:332-345`) a signal during plist restoration loses the un-restored prior bytes; reproduced at `df86cee6` too, jobs unloaded, so not fence-blinding.
- **F4** (`:304-309`) the backup `cp` precedes trap installation; that window is unguarded, but its state is conservative.

### Open verification gap
lt-04's 22-survivor mutation list was NOT re-run against this head — the
auditor could not see `lt-04` in its checkout (my briefing defect; since cured by
merging main into the int branch). Its own new sweep found **8 survivors in
`teardown`** and 3 in the production tail.

## Assessment I owe the magistrate

Fix round 2 did what ruling 25 asked, and the isolated reversions prove it: the
commit gate and the verified-bootout teardown are both real, both load-bearing,
and each fails correctly when only its own production change is removed. The
structure changed as intended.

What the round did not do is close the CLASS. Two sites remain: one the new
structure created three lines below itself, one the lane never had permission to
touch. That is the honest shape of the result, and it is the second consecutive
delta to answer the same-signature question YES on this installer — which is
itself the finding. My read, offered as input and not as a decision: the
installer is a shell script performing irreversible machine-state mutations with
time-varying preconditions and several exit paths, and each round makes it
locally correct while the next audit finds another path. Whether that warrants a
different shape for the whole script, or three more one-line guards, is above me.
