# Design consult brief — a transactional night-agent installer (INSTALL-WINDOWS-MULTI-01 redesign; three seats, blind; assembled 2026-09-15 11:48 PDT)

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only design consult. Code checkout: `/Users/edr/code/JouleWise-wt-design-iw` (detached at the integration head `073a9763` of `int/2026-09-15-install-windows`). Never touch `/Users/edr/code/JouleWise` (frozen canonical root), `/Users/edr/night-custody`, `~/Library/LaunchAgents`, `/Users/edr/JouleWise-measurement-*`; never run `launchctl bootstrap`/`bootout`/`kickstart` against anything real (read-only `launchctl print gui/$UID/<nonexistent-label>` to learn the exit code is allowed and REQUESTED). No network. Temp under `/tmp`. Single test modules only. Ignore RUN_STATE.md, TASK_QUEUE.md and narrative state docs; the record set below is the evidence.

## Forcing problem (why the point-fix loop is over)

`scripts/install_night_agent.sh` installs two LaunchAgents (night + dead-man) for a pre-registered plan: render two plists → bootout priors → bootstrap night → bootstrap dead-man → verify → succeed; it also has `--uninstall` and `--render-only`. Its preconditions are time-varying (D-180/D-181: install only inside a listed local-time span and before `install_close_epoch = t0 − PLAN_LEAD_S − 3600`; refuse occupied labels) and every mutation is irreversible machine state read by a fence (`scripts/magistrate_watchdog.py` `installed_agent_fence` reads the two plist files to see an armed plan; a loaded job with no plist is invisible to it). Three dictated fix rounds under two cold gates (records `25-*/10`, `28-*/10` and their syntheses 13) each closed the visible sites; each delta audit found the class open one line further: (1) a missed boundary check at the final bootstrap; (2) cleanup that leaves a loaded job with no plist (EXIT trap skipped by `set -e` in a function; unconditional file removal after `bootout || true`); (3) a failable statement after the commit gate that tears down a verified install; (4) NOW: all three re-read sites use `launchctl print … && loaded=1`, so ANY non-zero exit (a query ERROR, stub exit 9) is read as "not loaded" and the plists are deleted under a still-loaded job (record `lt-21`, executed). The adopted stop condition (`28-*/13` §Q3) forbids round 4: the next spend is this consult.

## Invariants the design must make true BY CONSTRUCTION (not by enumeration)

- I1 (class 1): the installer never exits 0 with a label loaded unless a clock read taken AFTER the last launchd mutation is below `min(selected_span_close, install_close_epoch)`.
- I2 (class 2): no path ends with a label loaded and its plist absent; no path exits 0 while a label it attempted to bootout is still loaded; a failed or ambiguous liveness query is treated as LOADED (unknown ⇒ loaded), never as absent.
- I3: a failed or signalled install leaves either the prior state byte-identical (priors restored, prior jobs' loaded-ness as found) or a conservative half-state the fence can see (files present); never files-gone-jobs-loaded.
- I4: `--render-only` never invokes launchctl; `--uninstall` obeys I2.
- I5: no invented ceiling/duration constant (cold gate 25 Q2); bounds are observed, not predicted; existing constants (`INSTALL_CLOSE_MARGIN_S`, spans) unchanged; refusal reason strings already documented in the runbook (`docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`) preserved or the docs updated in the same lane.
- I6: testable end-to-end with the fake-launchctl pattern (`tests/test_install_night_agent.py`), including exit-code semantics of `launchctl print` (learn the real code for a missing service on this machine, read-only, and cite it), signals at every step, and clock advance at every step.

## Questions (answer each with a recommendation and a rejected alternative)

Q1 — Shape. (A) Keep the shell script and fix the liveness predicate (a `loaded_state` function returning loaded / absent / unknown from the exit code and output of `launchctl print`, unknown ⇒ loaded) at all three sites, plus whatever else you find; (B) a Python module (`joulewise/night_agent_install.py` or under `scripts/`) implementing a state machine with ONE commit point and ONE teardown, a `LaunchctlAdapter` whose every call returns an explicit outcome enum, the shell reduced to argument parsing and delegation; (C) other. Rule which and why, naming the invariant each alternative cannot guarantee by construction.
Q2 — The state machine (if B or C): states, transitions, the single commit predicate, the single teardown, what each failure/signal at each state leaves behind, and how I3 is met when a prior job was loaded before the install.
Q3 — Liveness semantics: the exact exit code and stderr of `launchctl print gui/$UID/<missing>` on this machine (read-only probe; cite verbatim) and the resulting three-valued predicate; how the fake launchctl in tests must model loaded/absent/unknown.
Q4 — Migration: what the runbook, NIGHT_HANDBACK, courier prompt and `scripts/run_night.py schedule` callers must change; which refusal strings survive; what the twelve-row gate should require of the landing (regression matrix; mutation must-die set; replay).
Q5 — Scope: does the same design cover `scripts/install_magistrate_watchdog.sh --uninstall` (lane A204) now or later; and the shipped default span list.
Q6 — Anything the three rounds got RIGHT that must be preserved verbatim (commit gate, verified bootout, render-only exemption, FIX-1..10 regressions) versus discarded.

## Report
Under 12 KB, in the claude-codex-report/v1 envelope where the seat is a Codex seat (genre `scout`), plain markdown otherwise. Executed evidence for Q3 is mandatory; everything else is design with cited lines from THIS checkout.
