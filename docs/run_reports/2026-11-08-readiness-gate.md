# Readiness gate — 2026-11-08

Implemented on `ops/2026-11-08-readiness-gate`, based on `origin/main`
`dcfa4c59351615cdf3879a0ef68c5800f56f53a7`. Local commit only; no push.
The final handoff names the commit containing this report.

## Delivered

- `configs/readiness/next_steps.json`: five ordered steps, shared defaults,
  branch/commit selection, live-command documentation, synthetic seam,
  kit fields/check command, rulings/receipts, offline PREQUAL and explicit
  default/opt-in test selectors. Unknown commands and rulings stay null/RED.
- `scripts/readiness_next2.py`: resolves only the first two named branches,
  optionally fetches in the workflow, uses detached temporary worktrees,
  runs synthetic commands with success-record assertions, kit checks,
  presence/binding checks, selected PREQUAL and fresh-process unittest
  selectors. Required skips, expected failures, zero tests, errors,
  refusals and timeouts are RED. JSON retains exact command/test evidence;
  Markdown summarizes each prerequisite and earliest MBP hour.
- `.github/workflows/readiness.yml`: advisory, visibly failing check every
  three hours and on lane/align/fix/main pushes; canonical gate/list from
  main; artifact and job-summary publication even on failure. No dependency
  installation or model downloads.
- `docs/ops/readiness-air.plist.md`: hourly Air-only launchd template,
  fixed `/private/tmp/joulewise-readiness/status.json`, offline cached refs.
- `docs/process/READINESS.md`: lead maintenance rule, RED/UNKNOWN scheduling
  hold, RED-within-24-hours alarm, provenance/freshness and native boundaries.
- `tests/test_readiness_next2.py`: 17 synthetic integration tests, including
  local-only git fetching, missing route files, opt-in skips, refusal
  records, PREQUAL subsets, budget expiry, pins, cleanup and alarm timing.
- `CANONICAL.md` points to the mechanism; `.gitignore` excludes its generated
  local status snapshots under `/tmp/readiness/`.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` were not edited. No kernel task was registered.

## Verification and actual catches

`python3.13 -B -m unittest tests.test_readiness_next2` — **17 PASS**, final
run 21.177 s. Earlier development runs caught a missing explicit
`unittest.mock` import; fixed. Total targeted testing remained well below
20 minutes; no full suite or pytest was run, per the blinded-job instruction.

`python3.13 -B scripts/readiness_next2.py --output tmp/readiness/status.json`
— **exit 1, RED**, `critical_path_alarm=true`. No network. Final status
generated at `2026-11-08T08:21:37.171567+00:00`, with a 1,200-second command
budget. JSON and Markdown are local generated outputs, intentionally ignored.

| Candidate | Result | Observed blockers |
|---|---|---|
| R1, `lane/2026-11-08-r1-arm` | RED, earliest hour 0 | No cached branch, hence `no arm route: checkout unavailable`; each remaining prerequisite UNKNOWN |
| R1-to-W1, `lane/2026-11-07-r1-kit-r0fill` at `d9d1098c619856d624214dc5fde14013aafc4312` | RED, earliest hour 18.7 | No agreed synthetic arm/launch chain; kit blocks on `R1.B_D`, `R1.I_D`, `R1.T_dead`, `R1.thermal_policy`; W1 plan/sizing/ruling missing; required tests below |

On the second candidate, `r0-config` and `d-pin-verifier` PREQUAL checks
passed; `kit` and `w1-plan` failed. The first exploratory run exposed a
reporting defect: a PREQUAL script exit 1 for one failed check incorrectly
colored passing siblings RED. Fixed and regression-tested; the final run
correctly preserves each passing row.

Required modules actually executed serially on the final candidate tree:

| Selector | Tests | Result | Seconds |
|---|---:|---|---:|
| `tests.align.test_v4_kit` | 116 | RED: 6 failures, 0 errors/skips | 21.395 |
| `tests.align.test_v4_w1_plan` | 12 | RED: 3 failures, 4 errors, 0 skips | 2.685 |
| `tests.align.test_v4_w1_synthetic.KitBridgeTests` | 4 | GREEN | 6.995 |
| `tests.align.test_v4_w1_synthetic`, `JW_WP22_FULL=1` | 18 | RED: 1 expected failure, **0 skips** | 122.118 |

The WP22 expected failure is
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`.
It is now visible despite unittest normally returning success for an
expected failure. The W1-plan errors report `members must be the registered
configs/campaigns/align_v4 roster`. These candidate-tree failures are handed
back to their owning lanes; this change does not repair or reinterpret them.

An earlier exploratory run used the older integrated tree `e901eb2a4`:
116 kit tests, 12 plan tests and 4 bridge tests passed, while the opt-in
18-test WP22 module exposed the same expected failure with zero skips.
The final manifest uses the R0-filled candidate named by RUN_STATE 218.
The exploratory `nice -n 19` request was refused by this sandbox; it did
not provide a lower-priority guarantee. The final run used plain Python.

Python AST parsing, effective five-step manifest/opt-in assertions, launchd
XML parsing and interval/output-path assertions, workflow schedule/branch/
artifact static assertions, and `git diff --check` passed. Hosted Actions,
remote fetch authentication and launchd installation were not executed.

## Boundaries, uncertainty and next exact step

No real measurement paths were opened, no block-5 analysis pipeline ran,
and no hardware measurement or model download was performed. Synthetic
GREEN grants no live or native qualification. Cached refs make no freshness
claim; the lead must match the reported SHA to the intended magistrate tree.
The manifest is trusted executable configuration, not an OS sandbox.

The exact agreed R1/W1/smoke/D1 launch commands and several ruling/receipt
paths do not yet exist in this clone. They were not invented. The shared
checks for later entries are provisional until their actual designs and
dependencies are pinned. R1's stage-specific kit `--check` interface is also
pending; requiring W1's future R1 outputs before R1 would create a circular
gate, so that missing interface is explicitly RED instead.

Next: the lead supplies the independently agreed route and commit, exact
live argv, real end-to-end synthetic seam/success assertion, stage-specific
kit check, and code-only ruling/receipt bindings in the manifest; repairs
the owning-lane failures; then re-runs the gate. Land the mechanism on main
and instantiate the template on the Air through the normal lead workflow.
No independent cross-family review was performed in this offline session;
merge and final route authority remain with the lead.

Native checks for the lead outside this sandbox: on an appropriate
non-measurement Metal host, run the candidate's
`python3.13 -B scripts/align_v4_prequal.py --offline --stage r1 --only stack,checkpoint-native --output <NEW_DIRECTORY>`
and require both selected rows to pass (exit 3 is expected for the subset).
Then run the agreed ≤45-minute native W1 smoke once its kit and exact argv
are published. This report supplies no substitute for that native result or
for the lead-controlled quiet-MBP gates.
