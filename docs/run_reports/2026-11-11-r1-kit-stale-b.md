# R1 stale expectations — Round 2 — 2026-11-11

Applied the six released STALE EXPECTATION updates and the RL-59 fixture
correction. All six refreshed tests pass. Five requested modules pass in
full; round 8 retains five baseline process-proof failures caused by
sandbox-denied process census. No production or condition-13 file changed.

Branch: `ops/2026-11-11-r1-kit-stale-b`, initially clean at
`0aa0143079062d4fcca984f2a0a5c369aa40fce8`
(`origin/ops/2026-11-11-w1-presign`). The launcher supplied the named branch
at the requested base. Local commit only; no push. Its hash is supplied in
the final handoff because this report is part of that commit.

## Authority and scope

Read the round-1 report from
`origin/ops/2026-11-11-r1-kit-stale:docs/run_reports/2026-11-11-r1-kit-stale.md`
first. The round-2 brief releases its six proposed changes after the lead's
R7-2 refusal fix in `0aa014307`. The ruling source is
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`,
RL-59 and RL-72. Every refreshed test and the fixture correction cite
introducing commit `a85ee8ec6` and quote the applicable ruling in a comment.

Only these repository files changed:

- `tests/align/test_r1_round7_science.py`: the five released round-7 expectations.
- `tests/align/test_r1_round8.py`: the released redo expectation and its class description.
- `tests/align/test_r1_rehearsal.py`: `FakeWorld.__call__` cap fields only.
- This explicitly requested replacement run report; the round-1 report is unchanged.

The brief owns task selection and the targeted-test exception to the normal
full-suite rule. No coordination state, task registration, production code,
contract, or condition-13 bytes changed. No agent was delegated work; the
launcher/orchestrator retains review, push, merge and hardware authority.

## Six changes and red → green

The method names below are unchanged. Baselines were run before changing
the corresponding module; final runs used the completed test/fixture diff.

| Item / test | Citation and retained coverage | Observed red → green |
| --- | --- | --- |
| 1. `test_the_r1_g0_timeout_is_one_runtime_config_constant` | `a85ee8ec6`, RL-59: “1,200 s stays, for every R1 gate.” Expanded the literal kind set to step-30B, every A-B-A leg and d-4bit. Kept the one-config constant and type/finite/range rejections; excluded the sensors-only helper. Separately asserted the exact step-only timeout-dispatch set and exclusion of gated D/X-G under RL-72 E3, “a timeout runs flagged: step kinds only.” | Extra kinds in the actual cap set → pass. |
| 2. `test_gate_policies_carry_the_timeout_only_for_its_kinds` | `a85ee8ec6`, RL-59: “1,200 s stays, for every R1 gate.” Expect 1,200 for the added model kinds, all three A-B-A legs included. Kept explicit gate-policy propagation/absence checks and a sensors-only helper witness at the default 600-second armed cap. | `1200 != None : step-30b` → pass. |
| 3. `test_step_d_and_the_designed_states_are_bounded_with_the_timeout` | `a85ee8ec6`, RL-59: “1,200 s stays, for every R1 gate.” Step-30B is 5,763.9952 s with the 1,200-second cap and 5,163.9952 s with a supplied 600-second cap. Kept the member overhead, step-D arithmetic and all three planning-state bounds. | `5763.9952 != 5163.9952` → pass. |
| 4. `test_registration_records_the_cap_and_every_g0_wait` | `a85ee8ec6`, RL-72 E3: “step-30b, the legs, step-D and the planning turns dispatch their turn after an observed timeout.” Require one timed-out step-D wait at cap/wait 1,200, its canonical directory, flag, candidate status and inadmissible B_D. RL-59: “The release against the soak before each leg is dropped; the leg's own gate is the settled start.” Require no G0-only retry or soak-release invocation. Keep the derived W1 cap, X-G wait, gated outcomes, contract fields and exact remaining G0 wait order. A CPU-busy step-30B attempt exercises preservation of its superseded G0 evidence before the accepted replacement. | `1 != 2` step-D waits → pass, including all later assertions. |
| 5. `test_night_worst_case_with_the_round8_bounds` | `a85ee8ec6`, RL-72 E2: “two load redos for the night, each a whole admission unit; `window_max_s` 126,480 s.” Assert every unit's names, order and independent literal bounds, including predecessor/step-D and each precool/planning pair. Assert subtotal 58,711.9616 s, largest unit 7,563.9952 s, blackout 5,400 s, encounter 12,963.9952 s, two redos/two encounters, floor 99,768 s, overhead 9,000 s, span 108,768 s and window 126,480 s. Keep the separate 1,200-second config check and absence checks for old summary, retry and release allowances. | `KeyError: 'g0_timeout_s'` in the obsolete summary shape → pass. |
| 6. `RedoReleaseBoundTests.test_a_heavy_redo_waits_with_the_release_preroll` | `a85ee8ec6`, RL-72 E2: “two load redos for the night, each a whole admission unit”. Expect actual OS-batch admission calls `[5763.9952, 5763.9952]`, two step invocations, no soak-release helper, one consumed load redo and the preserved rejected directory/attempt. The obsolete artificial 5,000-second override does not control the config-derived bound. Keep the standalone helper's `65 + 600` arithmetic. Existing follow-up tests still witness whole-pair redos and the shared quota. | `[5763.9952, 5763.9952] != [5000.0, 5665.0]` → pass. |

`FakeWorld` now emits `g0_timeout_s=1200.0` for step-30B, the A-B-A legs and
d-4bit, citing `a85ee8ec6` / RL-59's quoted cap sentence. The sensors-only
`g0-release-soak` helper keeps 600. This removes the fixture/production
mismatch; the refreshed registration test checks every emitted model gate
cap, and the full rehearsal module passes.

## Verification

Every module ran separately and sequentially with Python 3.13 and the
unmodified `tests/__init__.py` host guard. No full suite was run.

All commands below have the prefix `python3.13 -B -m unittest`:

| Module argument | Baseline | Final |
| --- | --- | --- |
| `tests.align.test_r1_round7_science` | 18 tests, 4 failures + 1 error, 1.853 s | **18 pass**, 2.245 s |
| `tests.align.test_r1_round8` | 21 tests, 6 failures, 68.813 s | **16 pass, 5 sandbox failures**, 70.720 s |
| `tests.align.test_r1_rehearsal` | Not rerun before the fixture edit | **77 pass**, 28.714 s |
| `tests.align.test_r1_followup` | Not rerun before edits | **12 pass**, 162.968 s |
| `tests.align.test_r1_round3` | Not rerun before edits | **8 pass**, 73.510 s |
| `tests.align.test_r1_round4` | Not rerun before edits | **10 pass**, 15.321 s |

The unchanged
`G0TimeoutTests.test_a_runtime_config_without_the_timeout_refuses_at_t0`
passed in both round-7 runs. AST/source comparison against `0aa014307`
confirms its method source is byte-identical and that exactly the six
released test methods plus `FakeWorld.__call__` changed. No test methods
were added or removed. The follow-up module also passes its every-file
byte comparison between the old and new default workload adapter bundles,
with its one-byte mutation witnesses intact. These are synthetic checks.

`git diff --check` passed. A repository diff against `0aa014307`, excluding
`tests/**` and this report, is empty: production/condition-13 and
coordination files remain unchanged.

Logs are local temporary files `/private/tmp/r1-kit-stale-b-<name>.log`,
where names are `round7-before`, `round8-before`, `round7-after`,
`round8-after`, `rehearsal-after`, `followup-after`, `round3-after`,
`round4-after`, and `process-diagnostic`. Total reported execution time
including baselines and the diagnostic: **429.552 s**, below 20 minutes.

## Sandbox failures and exact evidence

The five round-8 failures were present before these changes and remain
unchanged. No skips or weakened assertions were introduced.

The three `NightInterruptTests` methods
`test_sighup_while_the_chain_runs_stops_it_and_restores`,
`test_sigint_on_a_chain_that_ignores_term_is_killed_and_restored`, and
`test_sigterm_while_the_chain_runs_stops_it_and_restores` each fail the
`'"proven": true'` assertion. Their synthetic night logs contain this exact
census message:

```text
census_exit_3: sysmon request failed with error: sysmond service not found
pgrep: Cannot get process list
```

The other failures are:

- `R1InterruptTests.test_the_runtime_and_its_descendants_are_proven_gone_before_the_restore`:
  `AssertionError: [] is not true` at `self.assertTrue(at_restore)`.
- `TerminateTreeTests.test_an_orphan_holding_the_pipe_neither_hangs_nor_survives`:
  `AssertionError: False is not true` at `self.assertTrue(outcome["proven"])`.

A focused sequential rerun of just these last two tests, with in-memory
observers that forward the real `subprocess.run` and `_terminate` calls
unchanged, reproduced both failures (2 tests, 5.408 s). The observer recorded:

```text
PermissionError: [Errno 1] Operation not permitted: '/bin/ps'
```

Both termination proofs had `census_failed: true`, `proven: false`, and no
recorded descendants. The orphan case also had `pipes_held_open: true`.
This directly establishes the denied-census path for the two runtime
failures, rather than relying only on similarity to the night failures.
It does not establish how those native process tests behave outside the
sandbox. No permission escalation or sandbox bypass was attempted.

## Limits, read-scope caveat and handoff

No network, model download, real measurement pipeline, native MLX execution,
hardware validation, or real custody/measurement-file access was performed.
Only synthetic tests and repository code/documentation were used. No real
sealed-data or external study path was followed.

Read-scope caveat: the targeted RL-59 documentation excerpt included
surrounding retrospective prior-night narrative before reads were narrowed
to the applicable clauses. No underlying records were opened, and no
outcome inference was used for these changes. This caveat prevents treating
the session as having read only the ruling sentences.

No contract question remains open for this test refresh. The outstanding
verification gate is native process proof: the lead must rerun
`python3.13 -B -m unittest tests.align.test_r1_round8` in a permitted macOS
environment outside this sandbox, including the five named tests above.
No new MLX-specific test was added or changed, and this work provides no
native MLX evidence. The owning lane retains any required condition-13
smoke and hardware gates. The next exact step is the lead's final diff
review and native round-8 rerun, followed by the launcher's authorized push;
this seat does not push or merge.
