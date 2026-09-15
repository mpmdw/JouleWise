# lt-14 — Fix round 2: three NEEDS_RULINGs, all three the lead's defects

Written 09:35 PDT 2026-09-15 (clock read). The seat returned `NEEDS_RULING`
three times rather than guessing, and was right every time. All three defects
are in the LEAD'S DICTATION, not in cold-gate ruling 25's intent. Recorded
plainly because a lieutenant's dictation errors are exactly what a delegated
seat's early-return protocol exists to catch, and burying them would make the
next brief no better.

## Round 2a (pid 15084, 09:08:06 → 09:13, Astra xhigh)

Returned `blocked/partial` with FIX-C complete and FIX-A/FIX-B untouched.

### F1 — my mutation oracle was UNSATISFIABLE against the Opus amendment

Cold-gate step 4 requires the reorder mutation to be caught by asserting "both
`bootout` lines are the last two launchctl calls". The Opus amendment requires
`launchctl print` RE-READS after both bootouts. Both cannot hold: the prints are
necessarily the last calls. I carried both into one brief without noticing.

**Ruled: adopt the seat's formulation.** The final four launchctl calls are
`bootout <night>, bootout <deadman>, print <night>, print <deadman>` with no
later launchctl call, AND the stub asserts **both plists still exist at the
moment `bootout` is called**. The seat's version is STRONGER than the original
oracle: the original caught removal-before-bootout only in the TERM cell, the
stub assertion catches it in EVERY cell. Cell 9 (bootout rc=1 → both plists
present, fence still sees the plan) remains a second independent killer.

Executed outcome: reordering `rm` before the bootouts turned **all nine cells
and all 17 matrix variants RED**, each recording the stub violation `both plists
must exist at bootout`. The original oracle would have turned one cell RED.

### F2 — `return N` from an EXIT-trap function does not set the process status

Ruling 10 step 1 says teardown should "return a distinct non-zero status". On
zsh 5.9 that is not what `return` does. The seat measured it:

```
teardown 'return 4', original exit 3: observed rc=3
teardown 'exit 4',   original exit 3: observed rc=4
```

**Ruled: use `exit 4` in the retention branch.** The ruling's REQUIREMENT — "a
distinct non-zero status" — is preserved exactly; only the shell verb changes,
because the dictated verb could not deliver the required observable. The seat
verified no trap re-entry, exactly one retention diagnostic, no other cell
returning 4, and that replaying a completed teardown through another EXIT trap
returns 3, preserves restored bytes and adds no launchctl calls.

Both adopted in round 2b's brief with the reasoning stated, so the seat was not
asked to take the correction on trust.

## Round 2b (pid 17990, 09:15:49 → 09:33, Astra xhigh) — FIX-A and FIX-B landed `cb35e9aa`

Nine cells observed: 143 / 130 / 129 / 1 / 3 / 3 / 3 / 2, each with neither
loaded marker, plists absent or byte-equal to priors, no leaked backup, and
`installed_agent_fence()` returning `None` or the prior plan without raising;
cell 9 the inverse at rc 4 with both plists retained and the fence still seeing
the plan, including the variants where only ONE label remains loaded. Five FIX-A
cases RED (rc 0) before and GREEN (rc 2) after; deleting the gate line turns all
five plus cell 8's two variants RED. One existing assertion replaced under the
authorisation I granted (it asserted the deleted "rolled back" wording); AST
comparison confirms all 43 existing tests remain and no case was dropped.

### F3 — a REAL new defect the dictated shape introduced

**A failed `--render-only` run bootouts genuinely loaded labels.** The seat's
stub probe: both labels preloaded, second-render `PermissionError`, rc 1, both
bootouts and both prints executed, **both preloaded markers removed**.

`--render-only` promises to render and validate without touching launchd state,
and in that mode `launch_dir` is the render directory, not
`~/Library/LaunchAgents` — so the labels it unloads belong to somebody else's
install. On this machine that could silently DISARM an armed night. My
unconditional teardown caused it.

**Ruled: in `--render-only` mode `teardown` does FILE restore/removal only — no
`bootout`, no `print`, no launchctl invocation at all.** The safety invariant is
untouched, and the reason is recorded so it is not re-litigated: teardown exists
to prevent "a job loaded with no plist backing it"; `--render-only` never
bootstraps, so it cannot create that state, and the bootouts were pure side
effect that could only destroy state the run did not create. The retention
branch and its `exit 4` belong to the install path only.

Seat pid 32371 launched 09:34:58 (Astra high) with the F3 case defect-shaped
(both labels preloaded, render-only, `PermissionError` → rc 1, **both labels
still loaded**, **zero launchctl calls for the whole run**), a render-only
success control, an install-path guard re-running cells 1/8/9 to prove the
exemption did not leak (143 / 2 / 4 unchanged), and a mutation removing the
guard that must turn the F3 case RED.

## Assessment

Three rulings, three lead defects, zero seat drift. None of the three touched a
ruling invariant: F1 replaced an unsatisfiable oracle with a stronger one, F2
changed a shell verb to deliver the status the ruling required, F3 removed a
side effect the ruling never asked for. **All three are the lieutenant's to
reverse and the magistrate's to overrule**; none is a rule or doctrine change,
and each is a single guarded branch or assertion.

Per the direction, a same-signature delta finding would still mean STOP with no
round 3. These three are not that: they are dictation defects caught before the
delta, and the delta re-audit judges the result independently.
