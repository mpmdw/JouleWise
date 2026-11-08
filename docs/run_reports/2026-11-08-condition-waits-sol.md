# Condition waits — Sol handoff, 2026-11-08

## Result

Wrote `docs/align/v4/CONDITION-WAITS-sol.md`: independent Sol proposal,
not an adopted registration, implementation or native qualification.
It inventories recurring and R0/R1 waits with file:line sources; distinguishes
fixed observations, conditional releases and ceilings; specifies proposed
signals/bands/stability/floors/caps/failure outcomes; separates registration
changes from engineering; and supplies a maximum-two-hour native diagnostic.

The primary opportunity is joint, freshly measured between-window state and
shared display/quiet observation. G0/G1/H and campaign cooldown already
early-exit. Retain the 300 s member idle and all observation/calibration tails
for v4. The chosen B5-derived sidecar's 5 s / 100% cooldown is distinguished
from D-077's generic 30 s / 10% default. The short post-idle sentinel is
distinguished from the 300 s pre-idle baseline.

No saving is established. Conditional hot-tail arithmetic spans slowdown to
about eight minutes saved; ten to twenty minutes requires an already-cool
machine. Shared dwell can remove at most three additional minutes only if
it was actually serial, without double-counting cooling. The 54 min gross
D-window idle opportunity remains deferred, as already ruled.

## Scope and source custody

- Started clean at `05b6d04cb`, with the task's branch already created and
  checked out: `align/2026-11-08-condition-waits-sol`, tracking
  `origin/align/2026-11-08-v4-r11`. Used that new task branch; no base movement.
- Read AGENTS/CLAUDE, targeted intake/queue sections, Mission M0,
  orchestration, D-077 and owning thermal/protocol rulings. No active stop
  card. The explicit task is the intake authority; no kernel task registered.
- Used only local repository/Git objects, including the permitted shared
  object store, and explicit committed timing/thermal/context sources.
  Historical absolute record locators were text only. No real restricted or
  external measurement path was followed, no Block-5 pipeline ran, no network,
  model loading/download, live sampling or machine/job manipulation occurred.
- The independent Opus condition-waits build was not read. No consult or
  subagent was launched; agreement and final design authority remain with
  the lead. The earlier cited Opus engineering review was read as requested.
- Only two documentation files changed. RUN_STATE.md, TASK_QUEUE.md,
  docs/process/state_kernel.json and tests/test_gen_state.py were preserved
  under the user's explicit coordination-state prohibition. No decision-log
  ruling or advisor-visible project state was changed.

## Verification

Commands executed serially for the test modules, with no native MLX tests:

| Command / check | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_cadence` | 16 passed, 0.004 s; synthetic triage/fixed-eight predicate coverage. |
| `python3.13 -B -m unittest tests.align.test_thermal_gate` | 44 passed, 32.198 s; fake SMC, clocks and native-stream seams. Not hardware validation. |
| One-off Python citation-bounds check against named allowed Git blobs | 51 explicit file:line citations exist and are within file bounds. This is a location check, not independent scientific review. |
| One-off timing projection from three explicit pilot `arm_decision.json` blobs | Monotonic whole-arm durations 276.580233 / 306.510938 / 276.620115 s; source commits and field lines recorded in the design. No energy/residual/score field used. |
| `git diff --check` and staged equivalent | Passed. Final scope/diff review: this design and this report only. |

No code/script added, so no new synthetic test suite was needed. The full
suite and compileall were not run: docs-only task, explicit full-suite
prohibition and a long analysis job on this host. Targeted unittest time was
about 32.2 s. No native measurement claim follows from these checks.

## Open questions and next step

1. Lead compares this build with Opus's independent build, resolves the
   admission/overlap policy and decides whether to spend the proposed native
   gap before W1 registration. This report grants no arm authority.
2. R1-final thermometry and contemporaneous fan/package-power references may
   be unavailable; R11's TV0h/Tf08 remain PROVISIONAL. R1's initial soak also
   predates final power-mode adoption, so it cannot automatically supply the
   proposed Q in a different mode. R11 journals are only digest-pinned
   off-repo here, so exact joint time-to-band was not computed.
3. Two synthetic native recovery curves can validate instrumentation and
   refute a bad release rule; they cannot prove D-load/residual equivalence
   or establish a recovery-tail quantile. If load-transfer evidence or any
   bound channel is missing before registration, keep the incumbent waits.
4. Lead/magistrate native work remains: the ≤2 h diagnostic with agents and
   competing work absent, SMC/fan/power/display freshness and units, observer
   overhead and final-read disturbances. If gate code changes later, also
   run native MLX hold-drain/resume and token/cache identity checks outside
   this sandbox. The separate paired idle-shortening study is deferred.

Local commit: the commit containing this report is the handoff commit
(`git log -1` on the task branch). No push requested or performed.
