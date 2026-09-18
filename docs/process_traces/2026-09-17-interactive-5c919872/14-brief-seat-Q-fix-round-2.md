SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/night_gate.py","joulewise/night_plan_writer.py","joulewise/arm_retry.py","joulewise/quiet_admission.py","scripts/run_night.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_night_plan_writer.py","tests/test_arm_retry.py","tests/test_run_night.py","tests/test_gen_derivation_night.py","tests/test_quiet_admission.py","tests/night_gate_fixtures/**","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md","docs/contracts/night_quiet_admission.md","docs/contracts/pack_night_go_receipt.md"]
BASE_HEAD: 649eefd2
BASELINE_MANIFEST: .codex-bridge/baselines/mag-5c919872-gate-quiet-fix2-2120.json
BASELINE_DIGEST: sha256:f216315722282936e68d4420dfecee37b86e52494222150cd026ce7a20c15ba7
LEASE_ID: lease-79c5a1766616453fb93e93b7cea20ffd

# Seat Q fix round 2 — refuter findings (contract lens F1–F3, execution lens below)

Branch `feat/2026-09-17-night-gate-quiet-admission` in `/Users/edr/code/JouleWise-wt-gate-quiet`, head `649eefd2` (your fix round 1 `a2671902` plus two lead bench commits: `536fd4db` widens the `top` percentage tolerance to 1.0 because `top` rounds user/sys/idle independently — live lines 100.26 and 99.98 — and `649eefd2` adds the regression that kills the strict mutant; read both with `git show`). Same rules as before: leave every change unstaged (the lead commits by pathspec), do NOT push, nothing outside WRITE_SCOPE, no `launchctl`, no `~/night-custody`, no network, no `sudo`. Do not end your turn before every item is done or a genuine early return is required.

The two refuter reports are tracked at `docs/process_traces/2026-09-17-interactive-5c919872/12-refuter-contract-astra.md` and `13-refuter-execution-astra.md` (read-only, absolute path under `/Users/edr/code/JouleWise/` if your worktree predates them). Each finding below is dispositioned by the lead; apply exactly what the disposition says.

## Contract lens

**C-F3 (BLOCKER, `scripts/run_night.py` ~:126, the write-once record set).** The `quiet_samples.jsonl` entry was added unconditionally to `_WRITE_ONCE_RECORDS`, so an existing v2 plan whose night directory happens to contain that file is refused as a rerun before its legacy evaluator runs (refuter counterexample: valid v2 plan, `quiet_admission=None`, the journal the only existing artifact → head driver exits 3 `rerun_refusal quiet_samples.jsonl`; base guard `None`). Disposition: FIX. The journal joins the write-once set for v4 plans only; the v2 record set is byte-identical to `a90ab4e8` (assert the legacy tuple equals the base tuple in a regression, and add the refuter's counterexample as a regression: a v2 plan with a pre-existing `quiet_samples.jsonl` proceeds to the legacy evaluator).

**C-F2 (SHOULD-FIX, `joulewise/night_gate.py` ~:1392).** In the v4 dynamic hard checks a FAILED boot-identity command (`sysctl -n kern.bootsessionuuid`, exit 2) is classified as `night_refused_boot_clock` ("not a canonical UUID") instead of `night_probe_error`; the other five injected probe failures already return `night_probe_error`. Disposition: FIX in the v4 path only — a non-zero exit or empty stdout from the boot probe is `night_probe_error` (terminal, never quiet); a well-formed but DIFFERENT boot id stays `night_refused_boot_clock`; the legacy v2 path is untouched (regression for all three cases, plus the assertion that the v2 evaluator's behaviour on the same injected failure is unchanged from base).

**C-F1 (SHOULD-FIX, `docs/contracts/night_quiet_admission.md`).** First-use defects: "observer cost" at line 14 before observer is defined at 124; `sample_interval_s` at 58 and "sample interval" at 68 before the definition at 78–79; `consecutive_quiet_samples` at 59 before 82–83; `bind_max_s` at 57 and "bind allocation" at 73 before "bind window" at 77; "GO" at 9 before 153; "t0" at 50 before 184. Disposition: FIX by restructuring, not by footnotes — put a short "Terms" section immediately after the opening paragraph that builds, in this order, t0, GO, the bind window and its allocation, the sample interval, consecutive quiet samples, busy-core equivalents, the observer, terminal vs WAIT, attribution, cutoff authority; then make sure no term appears above that section except in the title. Re-run the refuter's check yourself (`nl -ba` and the first occurrence of each term) and paste the line numbers of definition vs first use for all ten terms.

## Execution lens

Report `13-refuter-execution-astra.md` (313 head tests pass; 35 mutant variants; replay patches under `/tmp/refute-evidence/ID.{diff,json}` may still exist). Two real defects and five test-strength gaps; every one is dispositioned FIX.

**E-F6 (BLOCKER, real defect, `scripts/run_night.py` ~:2016 `_BindTask.ready`).** `ready()` calls `self.process.join()`, so a hung sampler blocks the parent: no census, no expiry (mutant 16b; the refuter's added worker test shows `ready()` blocking 1 s on a hung sampler; the prescribed regression 10 passes with a fake task and therefore proves nothing about the real task). Disposition: `ready()` must be non-blocking (`join(0)`/`is_alive()` or a poll on the result pipe with zero timeout); the bind loop's census and deadline checks run on every tick regardless of the sampler's state; on deadline expiry the parent terminates and reaps a still-running sampler. Regression: a REAL `_BindTask` wrapping a worker that sleeps forever; assert `ready()` returns within 50 ms, that a census probe injected during the hang is evaluated, and that the deadline fires and the worker is reaped (no zombie); this test must fail against the `join()` mutant.

**E-F7 (SHOULD-FIX, real defect + broken test, `scripts/gen_derivation_night.py` and `tests/test_gen_derivation_night.py` ~:1105).** The named regression crashes (`AttributeError: 'NoneType' object has no attribute 'lower'`) and with complete fixtures `GenerationRefusal` is NOT raised for `post_bind_budget_s` 7979 or `window_max_s = bind + runway − 1` (mutants 21a/21b survive). Disposition: make `build_spec` (and the authoring path) refuse both cases with `GenerationRefusal`, the 7980 computed from the schedule constants, and fix the test so both refusals are asserted with complete fixtures; paste the two failing assertions against the pre-fix copy.

**E-F1 (test strength, `tests/test_quiet_admission.py` ~:27).** Omitting `mds_stores` alone from the aggregate survives regressions 3 and 6 (only the `fseventsd` case is exercised). Disposition: parametrise the name-exemption regression over every daemon named in the consult (`fseventsd`, `mdworker_shared`, `mds`, `mds_stores`, `mediaanalysisd`, `deleted_helper`, `cloudd`, `bird`, `softwareupdated`, `backupd`) and over an arbitrary name, asserting each contributes exactly its delta to the aggregate.

**E-F2 (test strength, ~:30).** Reading the decaying `%CPU` column instead of interval deltas survives regression 4. Disposition: add the refuter's counterexample to regression 4: a process with `%CPU` 90 in the snapshot but zero cumulative delta contributes 0 busy-cores (quiet), and a process with `%CPU` 0 but a large delta contributes its delta (busy).

**E-F3 (test strength, ~:33).** Parser identity by pid alone survives regression 6 (the test exercises the accounting layer, not `parse_ps`). Disposition: extend regression 6 to the parser: two `ps` snapshots where the same pid appears with a different `lstart` in the second must yield two identities and no delta between them; assert on `parse_ps` output directly.

**E-F4 (test strength, `tests/test_run_night.py` ~:4077).** Regression 8 does not kill "deadline reset each sample" (05) or "plan t0 reset to GO" (13); the driver integration test kills 13 (`10440.0 != 9900`). Disposition: make regression 8 assert the four derived instants (forced shutdown, completion, courier boundary, dead-man) and the bind deadline as exact numbers computed from the fixture's t0 for GO at t0+0 and t0+540, and assert the bind deadline is unchanged after three samples; both mutants must fail it.

**E-F5 (test strength, `tests/test_arm_retry.py` ~:453).** Regression 9 does not exercise predecessor-digest reuse (15c/15d); other tests kill them (`'allowed' != 'predecessor_rearm'`, `'candidate_changed'`). Disposition: fold both digest cases into regression 9 so the named test kills them.

Also from the refuter's inspection: mutants 05 and 14 were "killed" only by the 10 s external watchdog on the late-driver/rollback companions, not by an assertion; make those two companions assert a `night_refused_bind_expired` result within the fake clock (no real waiting) so they fail by assertion.

## Verification you must run and paste

- `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4`.
- `PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?`; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?`.
- For C-F3 and C-F2: run each new regression against the current head with the fix reverted in a `/tmp` copy and paste the failing assertion.
- The ten-term table for C-F1.
- `git diff --stat` and `git status --short` (unstaged; nothing outside WRITE_SCOPE).

## Report

claude-codex-report/v1 envelope under 8000 bytes: per finding what changed and the test that proves it, the counterfactual assertions, the ten-term table, any early return. No commits.
