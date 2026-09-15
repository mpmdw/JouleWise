# 10 — Cold Fable gate ruling, packet 25 (INSTALL-WINDOWS-MULTI-01), head `df86cee6`

Judge: Fable 5.1, fresh non-interactive session, foreground only, no subagents, 2026-09-15 08:44–09:05 PDT.

**Disclosure.** Auto-loaded by the harness before I read anything: `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, and the auto-memory index `MEMORY.md` (narrative pointers; set aside, none opened). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any memory file. Read for the kernel text only: `docs/process/state_kernel.json` (task `INSTALL-WINDOWS-MULTI-01` acceptance summary and goal).

**Validator.** Run 1 with the typoed charter sha `…a880…`: `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2. Run 2 with `…a870…`: `result: PASS`, rc=0, charter sha `099de884…c95d81`, packet sha `b204398d…261a`, all nine exhibit digests observed = expected. I judge on that PASS.

## Executed probes (this checkout, fake launchctl from `tests/test_install_night_agent.py` fixtures, `--launchctl-bin` stub, `HOME` under a tempdir; no real bootstrap, no `~/Library/LaunchAgents`, no `~/night-custody`)

| Probe | Result |
|---|---|
| P-F1a: spans `00:00–12:01, 12:01–24:00`, clock 12:00 → 12:01:01 at the dead-man `bootstrap` (after the `:343` check) | **rc=0, both labels loaded** (exhibit B F1 reproduced) |
| P-F1b: three spans, advance 12:00 → 12:02:01 crossing two boundaries | **rc=0, both loaded** |
| P-F1c (control): advance at the NIGHT bootstrap instead | rc=2 `install_span_closed; rolled back` — the `:343` check works; `:348` is the uncovered site |
| P-F3: stub sends `TERM` to the installer at the night bootstrap | **rc=143, night label still loaded, zero plists** (exhibit B F3 reproduced) |
| P-F2: prior dead-man plist mode 0444 → `PermissionError` in the second `render()` | **rc=1, night plist overwritten (not restored), one `/tmp/night-agent-install.*` leaked** (exhibit B F2 reproduced) |
| zsh 5.9 `set -e; trap … EXIT; f(){ false; }; f` | rc=1, trap NOT fired |
| zsh 5.9 `set -e; trap … EXIT; false` (top level) | trap fired |
| zsh 5.9 `f || exit 9` and TERM trap `exit 143` | EXIT trap fired in both |
| zsh 5.9 `{ f } always { … }` under errexit-in-function or under TERM | always-block NOT run in either |
| `launchd.plist(5)` `StartCalendarInterval` keys | `Minute (0-59)` at `:468`; no seconds key exists |

## Q1 — structure: **(c)**, a single commit gate at the only success exit. Mechanism choice, not a contract change.

Neither (a) nor (b). (a) adds a fifth point check and leaves the class open (the verification `print` calls after `:348` are already a sixth unguarded site). (b) needs a new constant (Q2) and still cannot guarantee anything by itself: a pre-sequence budget predicts, it does not observe, so a stalled `bootstrap` overruns it and (b) would need a post-mutation gate anyway.

The invariant the contract actually states (exhibit E: "refuses unless BOTH hold") is "every machine-state mutation completed while now < min(selected span close, install_close)". A clock read taken AFTER the last mutation that is still below both bounds proves that invariant for all prior mutations. So:

- Insert exactly one line after the verification block, before the success `print "validated pins…"` at `scripts/install_night_agent.sh:360`: `check_schedule close "$selected_span_close" || exit $?`. That is the commit gate; the success exit is unique and the gate guards it, which closes the call-site set by construction rather than by enumeration.
- The `initial` check stays (it selects the span and computes `selected_span_close`); the three existing `close` rechecks at `:336,:338,:343` may stay as early refusals or be deleted, they are no longer the safety mechanism.
- Teardown on gate failure is Q3's routine via the EXIT trap; no inline `bootout` at the gate.
- Contract: bounds, literals (`install_span_closed`), constants, and the fence are unchanged; this sits inside exhibit E's ruling. Not a contract change.
- Regression (RED at `df86cee6`, GREEN after): exhibit B's four F1 cases with the advance injected at the dead-man `bootstrap` (one boundary, two boundaries, plan-cutoff-first, selected-close-first) each end rc=2, `install_span_closed`, zero loaded labels, zero plists, zero backup dirs; plus advance to EXACTLY the close (kills the `>=`→`>` survivor from exhibit B F4). Mutation: deleting the gate line must turn all five RED.

## Q2 — the bound: yes, exhibit E's rejection extends; nothing carries a predicted bound because under Q1(c) the bound is observed, not predicted.

`MAX_INSTALL_DURATION_S` is a ceiling constant of the same kind as the rejected `MAX_PLAN_SPAN_S`: an invented number that would become a timing rule D-181 cl.1 says does not exist. It is unnecessary. Plan-side slack already exists as `INSTALL_CLOSE_MARGIN_S = 3600` (`scripts/run_night.py:68`); span-side slack is deliberately zero by D-180 cl.1 ("never install after the span closes"), and the commit gate enforces exactly that. No measured duration and no derived margin are to be added.

## Q3 — cleanup: mechanism choice, but the ORDER is forced by the fence. Required shape follows.

Adjudication is not needed: exhibit E already adopted the installed-plist fence (`scripts/magistrate_watchdog.py:711-747` reads the two plists; job-loaded-with-no-plist is the one state the fence cannot see, which my P-F3 produced). Bootout-before-remove is therefore not a free choice; it is the only order whose interrupted half-state (files present, jobs gone) is the conservative one (FENCED/HOLD, exhibit B's E2 test already pins that a leftover file fences). Required shape, for a seat to implement without re-deciding:

1. One function `teardown` defined before any mutation. Body: `local result=$?`; if `result != 0`: `bootout gui/$uid/com.joulewise.night || true`, then `bootout gui/$uid/com.joulewise.night.deadman || true`, then for each plist restore the backup byte-for-byte if one exists else `rm -f`; in every case `rm -rf "$plist_backup"`; `return $result`. It never bootstraps. It must be idempotent (re-running it is a no-op).
2. `trap teardown EXIT` is the SOLE invoker. Every failure path after the backup is an explicit `exit N` (measured: explicit `exit` from a `||` list or from the `INT/TERM/HUP` traps fires EXIT). Delete the inline `bootout` rollbacks at `:344,:349,:355-356`; one entry only.
3. No function in the mutation region may be invoked bare under errexit (measured: errexit inside a function skips EXIT). Both `render …` calls become `render … || exit 1`; both remaining `check_schedule` calls keep `|| exit $?`. `always` blocks are not an acceptable substitute (measured: not run in either failure mode).
4. Regression that proves the invariant "a signalled or failed install never ends with a loaded job and no plist": one parametrised test over injections {TERM, INT, HUP at the night bootstrap; read-only prior dead-man plist (`PermissionError` in render); night bootstrap rc=1; dead-man bootstrap rc=1; verification `print` rc=1; Q1 commit-gate crossing}. For each: expected rc (143/130/129/1/3/3/3/2); NO `launchctl.log.<label>` marker for either label; each plist absent or byte-equal to its prior bytes; no `/tmp/night-agent-install.*`; and `wd.installed_agent_fence()` over the resulting directory returns `None` (or the prior plan when priors existed) without raising. Mutation: reordering `rm` before `bootout` in `teardown` must make the TERM case RED by asserting, from the stub log, that both `bootout` lines are the last two launchctl calls.

Residual, note only: a previously loaded dead-man booted out at `:337` is restored as a file but not re-loaded on failure. That half-state is the conservative one under the fence; do not "fix" it by bootstrapping inside cleanup.

## Q4 — landing: **(i)**. (ii) is not a D-181 reinterpretation, but it does not make the head safe and it does not land the lane.

Deciding fact: exhibit B's F3 is LIVE under the shipped default span `(("00:00","24:00"),)`. My P-F3 used the default span and produced a loaded night job with no plist, invisible to the fence. So (ii)'s premise ("latent under the default") is false for class 2. On D-181: cl.1 itself says what the machinery cannot yet do is "a mechanism limit, not a scientific one", so a test-pinned refusal of narrowed spans would be a mechanism limit, not a reinterpretation, and not Ed-only. But the kernel acceptance says "accept a list of install spans" and "tests pin the span list"; (ii) leaves both unmet, so it is not the lane landing, it is a different lane. Rule (i): fix round 2 is authorised UNDER this ruling as one seat implementing Q1(c) and Q3 exactly as written (the escalation trigger is satisfied: the structure changed, not the call site), then the delta auditor re-runs its isolated-reversion protocol on the two new regressions, then the twelve-row gate.

## Q5 — FIX-5: **AFFIRM**. The kernel acceptance text must be recorded as narrowed.

Whole-minute: `StartCalendarInterval` carries `Minute` and no seconds key (measured, man page `:468`); a fractional `t0` is undispatchable and exhibit D's executed case shows the consequence is a consumed pre-registered plan (write-once record). That is evidence-bearing, so D-161 keeps fail-closed here. Ambiguous minute: real launchd dispatch on a repeated local minute is unverified (exhibit C reason 1); either fold choice risks the same consumption; the cost is one local hour per year. This does not contradict D-181 cl.1: "any clock time" there is opposed to the fixed belt, and the narrowing adds no belt, cadence or gap. Not a contract change; it is the physical granularity made explicit. Text for the magistrate to record in `state_kernel.json` `INSTALL-WINDOWS-MULTI-01/acceptance/summary`: replace "the plan's t0 may be any clock time (launchd hour/minute derived from the plan, not a fixed belt)" with "the plan's t0 may be any clock time launchd can name: any whole minute (`t0_epoch_s % 60 == 0`) whose local wall-clock reading occurs exactly once (refusals `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`); launchd Month/Day/Hour/Minute derived from the plan, not a fixed belt"; and replace "the any-clock-time t0" with "the whole-minute unambiguous t0 (both refusals, an ordinary control, and a spring-gap control)". The goal sentence's "at any clock time" stays as Ed's words.

## Q6 — runbook §3 vs D-181: **(i)**, no conflict; the runbook must say so at two places.

Exhibit I line 143: "Three agent-free [QUIET-MAC] windows on distinct calendar days" is part of the registered sample. Exhibit H, D-181 cl.1, keeps "pre-registration before data" as a named soundness fence and says nothing ELSE about timing is a rule; the registered sample text is the fence, not "else". Ed's sentence that spacing "was never a scientific requirement" is recorded as forcing context, and D-181 names no lane amending rev1. So the machinery may install and arm several plans per day for everything not in that registered sample (rehearsals, the equivalence night, any non-registered window), while the three FAIL-route windows keep distinct calendar days until Ed issues a rev2 before the first FAIL-route capture (route (ii) is Ed's option, not a present requirement). Sentences for the magistrate to record:

- `docs/phase_2/derivation_night_runbook.md:2085-2086`, item 3 becomes: "**Distinct calendar days.** The registration (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143`) requires the three FAIL-route windows to fall on distinct calendar days. D-181 cl.1 and `INSTALL_SPANS` let the machinery install and arm several plans on one day; that capability does not apply to these three windows. A same-day FAIL-route successor is refused by this step, not by the installer, unless Ed amends the registration before the first FAIL-route capture."
- `docs/phase_2/derivation_night_runbook.md:1297`, append after "(a recurring local-time interval).": "Same-day successors are a machinery capability; for the three FAIL-route registration nights §3 item 3 still requires distinct calendar days."

## Severity summary

Blocker OPEN at `df86cee6` (Q1 class 1 reproduced twice; Q3 class 2 reproduced twice, one case live under the default span). No REFUSE on any question. Nothing above amends a rule; all text changes are for the magistrate to record. Probe files were written only under `/tmp/coldgate-iw/`; the checkout is untouched apart from this ruling.
