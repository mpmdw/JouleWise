# W1 reliability and watchdog integration — 2026-11-10

Branch: `align/2026-11-10-w1-integration`, starting at claim-B/RL-28 base
`7770d6a4fbf40c4bb2b0595e9e9388d44da6a96d`. Local commits only; no push.

## Authority and intake

The explicit integration brief and Fable's final Rounds 6–7 check select this
bounded AGENT task over the general queue. Mission M0 read the active stop
card, status/workspace/restart pointers, queue and Do-Not-Do-Yet sections,
playbook, source map, orchestration, CLAUDE conventions, and targeted D-009 /
D-050 authority. No active stop card existed; the initial tree was clean on
the requested branch. No agent delegation or model consult was used.

The brief overrides the ordinary coordination and full-suite checklist.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`tests/test_gen_state.py` are preserved; no kernel task is registered.
No real custody or restricted directory, measurement data, external home
directory, model weights, host power/clock setter, or live measurement was
accessed. Local Git object reads and synthetic temporary Git remotes only;
validation constrains Git transport to `file`. No network or full suite.

## Integration

1. Merged admitted reliability head `e2fca009641c377d2da1d347c204082c184a6dba`
   with `git merge --no-ff --no-commit`, then committed as `978cbea59`.
   All three shared files auto-merged cleanly and were inspected:
   `scripts/align_v4_next_arm_packet.py` retains claim-B `build_packet` rules
   and the digest-bound `courier_delivery` fallback in `terminal_release_check`;
   `docs/align/v4/DEVIATIONS.md` retains the B/V4/RL16/U5 rows and adds the
   distinct D-01/RL-26 row; `tests/align/test_v4_series.py` retains claim-B
   manifest/packet tests and the real-writer frequency-preflight replay.
   Both packet modules passed before this merge commit (15 and 46 tests).

2. Ported admitted watchdog head
   `6e0647a61353f559ada9e4763ecee76f6e8112ec` by per-path **three-way merge**,
   using common ancestor `d842f697f37a95a439dbb89927185b4b6e4fb1ea`, the W1
   merge tree, and the admitted incoming blobs. This avoids merging unrelated
   branch history. Scratch ancestor/ours/theirs blobs and merge output are in
   `/private/tmp/w1-integration-validation/merge/`; the reproducible port
   driver is `/private/tmp/w1-integration-validation/port_watchdog.py`.
   No watchdog file was replaced by a two-way copy.

   The one watchdog conflict is resolved by appending `[*boundaries, event]`
   and then checkpointing status. `night_gate.py` had the expected two-hunk
   conflict in the preview; the W1 file is retained byte-for-byte. AST comparison
   confirms `_restore_abandoned_high_power` is unchanged, including
   `powermode.restore_owed` / `deps.power_runner`. The
   `mark_production_entry("magistrate_watchdog")` main guard is retained.

3. Retained desk fencing and ported the self-contained, stdlib-only
   `scripts/launch_align_r0.py` plus `scripts/run_align_r0_launchagent.sh`,
   its runtime wrapper. The existing fail-closed desk-fence and launch-boundary
   checks remain useful even when the W1 plan is absent. The launcher requires
   an explicitly supplied measurement checkout/runner; no R0 runner, weights,
   environment, or measurement execution is added or invoked here.

4. Preserved W1 timing receipts for the watchdog's new named holds by including
   `UNSAFE_STATES` in `_hold_boundaries`' hold vocabulary. Merely retaining the
   old `HOLD_UNSAFE` spelling would lose start boundaries for the newly named
   holds. The new integration witness checks real receipt start/end rows are
   appended before status checkpointing. Its other witness calls the real
   CLI parser/main with `--dry-run`, synthetic dependencies, no writes, and
   no fork. The literal import command succeeds:
   `python3.13 -B -c "import scripts.magistrate_watchdog"`.

5. Retained `scripts/post_window_unstrand.sh` as an explicit operator recovery
   tool, along with its synthetic tests. It is not run against any real plan.
   The full final review is copied byte-for-byte from the allowed
   `/private/tmp/jwsol/briefs/rel-fable-review-final.md` into
   `docs/run_reports/2026-11-10-w1-reliability-fable-review.md` (578 lines).

## Registration work reserved for the research lead

No integration edit is made to registration code or the receipt template.
The reliability merge inherits only their already-ratified RL-26 C-helper
binding. They remain byte-identical to admitted reliability head `e2fca0096`.

After ratification, add these paths to `_NAMED_ARTIFACTS` in
`joulewise/align/apple/v4_registration.py` (thereby to `ARTIFACTS`, strict
by default), and add matching `null` entries to `artifacts` in
`configs/campaigns/align_v4/registration/registration_receipt.json`:

- `scripts/watchdog_status.py`
- `scripts/launch_align_r0.py`
- `scripts/run_align_r0_launchagent.sh`
- `scripts/post_window_unstrand.sh`

The first two are the exact missing imports reported by static closure.
All four occur in the regenerated dynamic trace's conservative traced set.
The third is the retained launcher's executed shell dependency: its path is
computed with `Path(__file__).with_name(...)`, which the static walk cannot
discover. The fourth is retained for operator recovery and also appears in
the registered trace. Bind all four before claiming closure completeness.
No amendment/allowlist exception is requested. The already-bound
`configs/launchd/com.joulewise.magistrate.plist.template` changes to carry the
required stable `MAGISTRATE_WATCHDOG_STATUS_HOST`; re-registration must bind
those bytes, the integrated watchdog, deviations, and regenerated trace.

## Trace and verification

Registered generator command (exit 0, 372.813 s):

```sh
python3.13 -B scripts/align_v4_dynamic_trace.py --out /private/tmp/w1-integration-validation/dynamic_closure_trace.json
```

Copied its output unchanged to `docs/align/v4/dynamic_closure_trace.json`.
All nine scenarios pass, **416 tests**. Against the reliability merge's
trace: `executed` grows **186 → 190**, adding exactly the four paths listed
above; no path is removed. The same additions appear in `opened` and
`child_process_paths`, and `not_bound` changes from empty to those four.
Scenario records/counts and `not_strict: []` are unchanged. This conservative
trace includes child script opens; it is not proof that an operator recovery
or measurement route ran.

The generator exercises the complete modules `tests.align.test_v4_series`
(16), `tests.align.test_v4_replacement_windows` (20), and
`tests.align.test_v4_next_arm_packet` (46) within its registered scenario
suites. These integrated-tree runs are reused rather than repeated.

Other commands are `python3.13 -B -m unittest <target>`. The validation runner
uses `JW_B5_SYNTHETIC_ONLY=1 PYTHONNOUSERSITE=1 GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_GLOBAL=/dev/null GIT_ALLOW_PROTOCOL=file`; all test remotes are
temporary local repositories. Final results:

| Target | Result |
|---|---|
| `tests.test_watchdog_reliability` | 45 passed |
| `tests.test_magistrate_watchdog_v5` | 4 passed |
| `tests.test_magistrate_watchdog` | 158 passed, including W1 abandoned-launch power restore |
| `tests.test_install_magistrate_watchdog` | 12 passed |
| `tests.align.test_v4_executed_closure` | 4 run, 1 failure: exactly the two new Python imports are unbound |
| `tests.align.test_v4_dynamic_closure` | 10 run, 1 failure: exactly the four newly traced paths are unbound |
| `tests.align.test_v4_registration` | 22 passed |
| `tests.align.test_v4_claim_b_packet` | 15 passed before port; 15 passed on the integrated tree |
| `tests.align.test_v4_test_reserves` | 2 passed |
| `tests.test_w1_reliability` | 11 passed |
| `tests.test_w1_reliability_r2` | 18 passed |
| `tests.test_w1_reliability_r3` | 14 passed |
| `tests.test_w1_reliability_r4` | 42 passed |
| `tests.test_w1_reliability_r5` | 7 passed |
| `tests.test_w1_reliability_r6` | 3 passed |
| `tests.test_w1_reliability_r7` | 10 passed |
| `tests.align.test_w1_smoke` | 28 passed; synthetic in-process CLI-only warnings expected |
| `tests.test_w1_integration` | 2 passed: receipt/checkpoint ordering and CLI `--dry-run` with no writes/fork |
| `tests.test_magistrate_desk_fence` | Final full module: 42 passed |
| `tests.test_post_window_unstrand` | 24 run, 2 platform skips, otherwise passed |

The imported desk-fence test initially expected `HOLD_UNSAFE` from public
`decide`; updated that stale expectation to `HOLD_DESK_FENCE`. The raw
`_launch_fence` helper still expects `HOLD_UNSAFE`. Final full-module rerun
passes. Four short checks inadvertently overlapped in the first orchestration
batch; all four were rerun serially. Subsequent module invocations were
serial, as were the generator's scenarios. Recorded test/generator elapsed
time, including retries and the initial packet checks: **1,144.501 s
(19m04.5s)**. No further test expansion or full-suite run.

Additional checks: literal watchdog import exit 0; AST parsing of all 36
changed Python files passes; `bash -n` passes for both new shell helpers;
`zsh -n scripts/install_magistrate_watchdog.sh` passes; staged
`git diff --check` passes. Protected coordination files match the initial
base exactly; registration code/template match admitted reliability head
`e2fca0096` exactly. The copied Fable review SHA-256 is
`a78951aeb5ce876a92dc79c619300208b805e821272982952194b2db27783bb9`.

Required fixture census:
`python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` returned
**2**, `PermissionError: [Errno 1] Operation not permitted: 'ps'`.
This is an unavailable observation, not a clean census. No bypass or process
signal was attempted; the lead must repeat it outside this sandbox.

## Files and local commits

- `978cbea59` — merge admitted reliability (47 changed paths inherited from
  the admitted branch; see `git diff --name-only 7770d6a4f 978cbea59`).
- `21029737a` — watchdog integration, trace and complete Fable review (19 paths).
- This report is committed separately after recording the above checks.

The watchdog commit changes the six operational scripts (`magistrate_watchdog.py`,
`watchdog_status.py`, `launch_align_r0.py`, `run_align_r0_launchagent.sh`,
`install_magistrate_watchdog.sh`, `post_window_unstrand.sh`), the magistrate
plist template, the seven watchdog/integration/unstrand test modules listed
above, `docs/process/MAGISTRATE_WATCHDOG.md`,
`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`,
`docs/process/R0_HEADLESS_LAUNCH.md`, the dynamic trace, and the final review.
No advisor-visible state, coordination state, registration amendment, receipt
signature, or installed service is changed by the port.

## Remaining gates and limits

This tree is **not ready to arm** while the new dependencies are unbound.
The lead must ratify the registration edits, apply them, repeat closure checks,
and issue STRICT registration at the final admitted head.

The supplied review's native checks (§7, D6, R6, S5) still apply. In particular:
close/uninstall the old night before moving installed code; provision and
record the helper build/binary and authenticated sudo query/setter rules;
verify frequency and power restore paths, launch-abandoned handling, USB
re-enumeration/restarts and liveness stops; prove launchd delivery, no watchdog
push during an armed span, and post-span freshness/alarm behavior. W-01/W-02
remain open until native launchd status push and the Air scheduler/notifier
are demonstrated. The `courier_delivery` window-record exporter remains owed.

No MLX or native hardware claim is made. The lead must run the review's
real-process test outside this sandbox:
`python3.13 -B -m unittest tests.test_b5_driver.LaunchTests.test_chain_digest_mismatch_is_a_flag_and_the_chain_runs`,
then native PREQUAL/W1 smoke and the final registration/arm checks.
