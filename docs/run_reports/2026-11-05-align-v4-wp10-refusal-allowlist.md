# WP10 CI repair: hazard refusal allowlist

Continued `lane/2026-11-05-magistrate-desk-fence` from clean head
`834feb229`, as explicitly requested. Fix commit: `3309d290d`
(`fix(hazards): census R0 desk handoff refusal sites`). Nothing pushed.
Read the supplied plan's rulings and WP10, repository intake/M0,
orchestration, D-172, the existing WP10 report and the headless runbook.
The user owns task selection here and prohibited coordination-state edits;
no kernel task was registered.

## Change and classification

Only `configs/gates/hazard_refusals.json` changes behavior of the CI census:

- Add `scripts/launch_align_r0.py` to scanned modules, closing the watchdog
  import gap. Also scan `scripts/run_align_r0_launchagent.sh`: the launcher
  constructs this dependency with `Path.with_name`, outside the scanner's
  literal-path dependency detection, but its exits belong to this lifecycle.
- Add 30 entries: 23 launcher, three watchdog and four shell entries. These
  represent 31 sites because shell `exit 2` occurs twice. Counts and guard
  digests come from the existing census, without changing the scanner.
- Refresh exactly four existing watchdog entries: `_launch_fence` FENCED
  (1 → 2), `_launch_fence` HOLD_UNSAFE (2, changed guard), `decide` FENCED
  (1 → 2), and `decide` HOLD_UNSAFE (8 → 9). Net additional covered sites: 34.
- Classify every new/changed entry INTERNAL with a specific `protects`
  explanation. The watchdog holds magistrate launch, not collection. The
  launcher and wrapper govern pre-arm R0 engineering work, outside registered
  windows; explanations identify operational catchers, ownership checks or
  shell cleanup. `pid_alive` uses signal zero, which stops no process.
  Runner TERM/KILL targets only the launcher-owned engineering runner.
- Reclassify the changed `_launch_fence` HOLD_UNSAFE entry from BASELINE to
  INTERNAL, as required for its changed guard. The frozen baseline is intact.

A structural before/after comparison confirmed that all unrelated entries,
all other config sections and `not_scanned` remain unchanged. No runtime or
test source changed. D-172's runtime-change/mutation requirement is not
triggered by this config-only repair; the requested entry-point tests ran.

## Verification

Test modules ran serially, using Python 3.13, synthetic fixtures only, and:

```sh
export HOME=/private/tmp/jwsol/v4-wp10d/tmp/home
export TMPDIR=/private/tmp/jwsol/v4-wp10d/tmp
export JW_B5_SYNTHETIC_ONLY=1
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=protocol.https.allow GIT_CONFIG_VALUE_0=never
export PYTHONPATH="$PWD"
```

| Exact command after those exports | Final result |
| --- | --- |
| `python3.13 -B -m unittest tests.hazards.test_refusal_allowlist` | 23 run: 22 passed, one skipped; 11.545 s |
| `python3.13 -B -m unittest tests.test_magistrate_desk_fence` | 34 passed; 17.026 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog` | 155 passed; 2.008 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_span` | 24 passed; 0.101 s |
| `python3.13 -B /private/tmp/jwsol/v4-wp10d/tmp/run_sandbox_module.py tests.test_magistrate_watchdog_yield` | 20 run: 17 passed, three failed; 35.937 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_cli` | Seven passed; 11.002 s |
| `python3.13 -B -m unittest tests.test_magistrate_watchdog_b6` | Nine passed; 0.050 s |
| `python3.13 -B /private/tmp/jwsol/v4-wp10d/tmp/run_sandbox_module.py tests.test_install_magistrate_watchdog` | Ten passed; 4.038 s |
| `python3.13 -B scripts/gen_state.py --check` | Exit 0; no writes |
| `python3.13 -m compileall -q joulewise tests` | Exit 0 |
| `git diff --check` | Pass |
| `git diff --exit-code 834feb229 -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | Empty |

Final unique-module total: **282 tests, 278 passed, three failed, one skipped**.
The skip is the existing design-catalog check: its referenced block-5 design
branch is absent from this clone. No fetch was attempted.

The initial allowlist baseline ran 23 tests in 16.027 s: 20 passed, the two
reported CI assertions failed, and one skipped. The first post-fix run was
22 passed/one skipped in 13.112 s; the final run above followed wording
clarifications in `protects` only. Including baseline and rerun, 328 test
executions took 110.846 s of reported unittest time, below the requested cap.

The temporary wrapper imports unchanged test modules. For the installer it
wraps `setUp` to replace only the noncanonical fixture script's absolute
canonical checkout with its existing synthetic `canonical-shadow` checkout.
Both compared checkouts remain distinct; the actual shell entry point and
assertions still run. This avoids resolving the real checkout outside the
blinding fence. For yield it retains direct `Popen` objects and supplements
the existing reaper by killing/waiting still-live owned children after its
normal cleanup. It does not change driver observation or assertions.
Both wrapped modules reported **zero directly tracked children still running**;
this makes no claim about unrelated processes or earlier sessions' children.
Logs and wrapper remain under `/private/tmp/jwsol/v4-wp10d/tmp/`.

## Remaining failures, uncertainty and handoff

The same three yield assertions already recorded in the incoming WP10 report
still fail, all in `DriverRecordsToWatchdogTests`:

- `test_a_chain_stop_is_released_on_the_driver_records`: expected 5, got 6.
- `test_a_live_process_naming_the_custody_holds_the_release`: expected
  HOLD_CENSUS, got FENCED.
- `test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery`:
  expected 5, got 6.

Their underlying cause is still unestablished. The prior report documents
the same failures against the original base watchdog and sandbox process-table
restrictions. This repair changes only census metadata and does not claim an
all-green watchdog suite or investigate an unrelated driver repair.

No full suite, network, block-5 analysis pipeline, real measurement-data
access, actual LaunchAgent installation, native Spotlight signal or MLX/Metal
test was run. All launch lifecycle evidence is synthetic. This repair adds
no MLX code; the integration lane's native MLX gates remain lead-owned.
The INTERNAL classification relies on the committed runbook's pre-arm,
R0-only lifecycle. Existing scanner vocabulary and its shell-guard limits
are unchanged. No new Ed or scientific-policy ruling was identified.

Lead next step: review the new entries and commits, rerun the seven watchdog
modules natively without the sandbox adapters (especially yield and installer),
then confirm CI before pushing. Existing native launchd self-unload,
Spotlight permission/recovery and agent-free R0 gates remain outstanding.
The requested `answer.md` is a separate handoff at
`/private/tmp/jwsol/v4-wp10d/tmp/answer.md`; the previously removed root file
is not reintroduced.
