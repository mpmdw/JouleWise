SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/night_gate.py","joulewise/night_plan_writer.py","joulewise/arm_retry.py","joulewise/quiet_admission.py","scripts/run_night.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_night_plan_writer.py","tests/test_arm_retry.py","tests/test_run_night.py","tests/test_gen_derivation_night.py","tests/test_quiet_admission.py","tests/night_gate_fixtures/**","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md","docs/contracts/night_quiet_admission.md"]
BASE_HEAD: a90ab4e8
BASELINE_MANIFEST: .codex-bridge/baselines/mag-5c919872-gate-quiet-1935.json
BASELINE_DIGEST: sha256:3d093f902554c16beaffda1acff085ac24579d7328f44980bfb8ef38dd2565f3
LEASE_ID: lease-79c5a1766616453fb93e93b7cea20ffd

# Seat Q — NIGHT-GATE-QUIET-ADMISSION-01: poll-until-quiet bind window + interval CPU quiet predicate (plan v4, receipt v3), driver timing, retry-policy reconciliation

Worktree `/Users/edr/code/JouleWise-wt-gate-quiet`, branch `feat/2026-09-17-night-gate-quiet-admission` at `a90ab4e8` (origin/main). Commit on this branch as you go (one commit per stage below, imperative subjects). Do NOT push. Never touch `/Users/edr/code/JouleWise` (the canonical root), any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`, or `launchctl`. No network. Do not edit RUN_STATE.md, TASK_QUEUE.md, `configs/calibration/preregistration_*`, `scripts/magistrate_watchdog.py`, or anything outside WRITE_SCOPE; if another path must change, finish everything else, commit, and stop with a NEEDS_SCOPE early return naming the path and why. Do not end your turn before every stage is done or an early return is required; "still working" is not a report.

Run tests as `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest <module>`; the quick tier is `python3 scripts/quick_suite.py --tier quick --workers 4` (about 60 s). The canonical full suite is the lead's to run.

## The forcing problem (executed evidence; read the two records first)

Four consecutive unattended measurement nights produced zero data. Read `docs/process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md` (findings 1–2 at the end) and the design consult `docs/process_traces/2026-09-17-interactive-45a0774c/01-gate-redesign-consult.md` (gpt-6-astra xhigh, read-only; its verdicts and section 2 are the adopted design unless this brief says otherwise). Short form: on 2026-09-17 the gate refused at t0 15:30:01 with `load_1m` 3.66 against the fixed `LOAD_MAX = 2.0` (`joulewise/night_gate.py:57`) while the agent census was EMPTY; the load came from a Spotlight/`mediaanalysisd` burst. Three hours later the load was 1.3–1.5 (the gate would have PASSED) while `fseventsd` alone burned 85–100 % of a core continuously. The 1-minute load average therefore refuses a clean machine and admits a contaminated one. One M3 Max performance core fully busy is on the order of 5 W, i.e. roughly 300 J over a 60 s capture slot against the ~5 J claim-side tolerance of each floor; the physical quantity that matters is busy CPU time during the interval, not run-queue length.

Today the gate (`evaluate_night`, `joulewise/night_gate.py:947`) runs its machine-quiet predicates ONCE at t0 and returns `Refusal("night_refused_not_quiet", …)` on the first failure (sites at lines ~1170, ~1190, ~1214, ~1247); the driver (`scripts/run_night.py`, `evaluate_night` calls at :2052 and :2064) writes `refusal.json` + `result.json` and exits 3. There is no waiting and no re-sampling. Verify every line number you rely on by reading it; the numbers above were checked against `a90ab4e8` on 2026-09-17.

## Standing rulings that bind you (do not reinterpret)

- Sensible gates (Ed, 2026-09-10): every tolerance is sized to the instrument (attribution limit ~1 J; claim-side ~5 J per floor). No microscopic gates. Physics and evidence refusals stay.
- Quiet windows any time (Ed, 2026-09-08 / D-181): "quiet" is a census-clean machine state, not a time of day; no artificial scarcity; every frequency bound must be scientific.
- Threat-model prune D-161: the only adversary is the operator; fail-closed only for physics, evidence and pre-registration.
- Pre-registration: sealed plan bytes are digest-bound. A plan-schema change must not alter the semantics of any existing sealed plan. Existing `joulewise.night_plan.v2` plans and the transaction-pack v3 shape keep their exact current validation and their exact current one-shot admission semantics.
- Rule 11: the numeric thresholds below (bind budget, interval, consecutive count, busy-core cutoff) are PROVISIONAL policy parameters carried in the sealed plan and ruled on by a cold gate that is being convened in parallel. Build the mechanism so the values are plan data, not code constants; do not invent a default that admits a night. The magistrate owns factoring, journal representation and sequencing; you own neither thresholds nor process rules.

## Adopted design (implement exactly; deviations are NEEDS_RULING early returns)

### D1 Plan schema v4 with `quiet_admission`

New schema id `joulewise.night_plan.v4` (v3 is occupied by the transaction pack; see `joulewise/night_gate.py:22` and the exact-key validation at :213). A v4 plan carries every v2 field plus:

```json
"quiet_admission": {
  "policy_id": "cpu_interval_v1",
  "bind_max_s": 600,
  "sample_interval_s": 30,
  "consecutive_quiet_samples": 2,
  "busy_core_max": 0.05,
  "post_bind_budget_s": 9000
}
```

`NightPlan.from_mapping` (`:197`) dispatches on the schema id: v2 → legacy dataclass with `quiet_admission = None`; v4 → the block is REQUIRED, every key required, exact key set, all numbers finite and positive, `consecutive_quiet_samples ≥ 1`, `bind_max_s ≥ sample_interval_s × consecutive_quiet_samples`, `window_max_s ≥ bind_max_s + post_bind_budget_s`. `policy_id` must be exactly `cpu_interval_v1` (an unknown policy is a validation refusal, never a fallback). No environment override of any of these values. `joulewise/night_plan_writer.py:18` `night_plan_mapping` becomes version-aware: it writes v4 only when the caller passes a `quiet_admission` mapping and never migrates or rewrites an existing plan. The generator `scripts/gen_derivation_night.py` (`build_spec` ~:462; schedule constants ~:86, ~:124, ~:511) gains an explicit `--quiet-admission-json PATH` (or equivalent explicit flag set; document it) that produces v4 plans; with no flag it still produces byte-identical v2 output (prove with the existing `--check` and a test).

The value 0.05 above is a PLACEHOLDER for tests and docs. Do not describe it as validated anywhere. In `docs/contracts/night_quiet_admission.md` (new, see D7) say plainly that the cutoff is provisional pending cold-gate proposition 4 and the evidence lane.

### D2 The quiet policy `cpu_interval_v1` (new module `joulewise/quiet_admission.py`)

A pure function core plus an injected sampler, so tests never need a live machine.

- Observation = two snapshots separated by `sample_interval_s`. Each snapshot: (i) per-process `(pid, start_identity, command, cumulative_cpu_seconds)` from `ps -Ao pid,lstart,time,comm` (or `etimes`+`cputime`; pick what parses robustly and say why) — identity is `(pid, lstart)` so PID reuse cannot alias; (ii) host busy fraction from `top -l 2 -s <interval> -n 0` using ONLY the second sample's `CPU usage:` line (Apple's `top` says the first sample is invalid) — or, if you can get `host_statistics` idle/busy ticks without a C extension, that; say which; (iii) `sysctl -n vm.loadavg` and `sysctl -n hw.logicalcpu` as DIAGNOSTIC fields only.
- Per-interval metrics: `process_busy_cores = Σ Δcpu_seconds / interval_s` over every process present in either snapshot (a process that exited mid-interval contributes its last-seen delta if measurable, otherwise is listed under `unaccounted`); `host_busy_cores = logical_cpu × (1 − idle_fraction)`; `busy_cores = max(process_busy_cores, host_busy_cores)` (so kernel and unattributed time count). `top_consumers` = the ten largest Δcpu processes with `(pid, command, busy_cores)`; the observer (this interpreter and its children) is INCLUDED, labelled `observer: true`, never subtracted.
- Interval verdict: `quiet` iff `busy_cores ≤ busy_core_max`. No per-daemon allow or deny list; no name-based exemption anywhere.
- Admission: GO on the first run of `consecutive_quiet_samples` consecutive quiet intervals; a busy interval resets the run to zero. Load average never authorises or vetoes admission.
- Every interval is appended as one JSON line to `quiet_samples.jsonl` in the night's artifact directory (fields: sample index, wall + monotonic start/end, boot identity, raw `ps`/`top` text digests (sha256) and parsed metrics, `top_consumers`, hard-predicate results (D3), the WAIT/quiet/error decision). The file is append-only, never truncated, and is listed by `_artifact_list` (`scripts/run_night.py` ~:945) so the courier ships it.

### D3 Terminal versus WAIT during the bind window

Terminal at any sample (immediate refusal with the existing codes, no waiting to "collect attribution"): agent census hit (`night_refused_agent_present`), AC power, the screensaver-configuration probe (the brief calls it HID; keep its current semantics — it reads configuration, not live inactivity), thermal speed limit (keep the current semantics: output without a `CPU_Speed_Limit` line passes), boot/clock checks, malformed required observations, plan/registration/digest failures. Only excess CPU is a WAIT. All dynamic hard predicates are re-evaluated on EVERY sample and once more immediately before GO. Census continues at its existing cadence (`CENSUS_INTERVAL_S = 30`, `scripts/run_night.py:63`) throughout binding; a census hit refuses even if the CPU run had already reached the required length. A probe error during binding is recorded on the sample and is terminal (`night_probe_error`), never silently "quiet".

### D4 Timing (the acquisition end never moves)

With `E = t0 + window_max_s`, `B = bind_max_s`, `R = post_bind_budget_s`: binding ends at `bind_deadline = min(t0 + B, E − R)`; every qualifying sample and the final hard checks must complete by then. A driver that starts late CONSUMES the bind allowance (the deadline is absolute, converted once to a monotonic deadline at driver start; a wall-clock change never extends it). Bind-window expiry with no GO → `Refusal("night_refused_not_quiet", …)` carrying the count of samples, the last busy-core value, the top consumers of the last sample, and the digest and line count of `quiet_samples.jsonl`. On GO the chain starts immediately; the reservation, settle and slots run under the UNCHANGED `E`, `E + COURIER_DEADLINE_S` completion and courier boundary, the unchanged forced-shutdown trigger and the unchanged dead-man derivation (read `scripts/run_night.py` ~:841, ~:1399, ~:1506, ~:1549 before touching anything; nothing derived from `E` may change). For v2 plans the driver's behaviour is byte-for-byte unchanged (one shot at t0).

The generator's `--quiet-admission-json` path must validate `window_max_s ≥ bind_max_s + post_bind_budget_s` with `post_bind_budget_s` at least the existing derivation runway (today's 9000 s allocation: 600 s settle + 12 slots at 600 s start-to-start + the pre-settle allowance — read the constants and state the sum in the docs); a v4 derivation night therefore has `window_max_s = 9600` when `bind_max_s = 600`.

### D5 Receipt v3

New receipt schema `joulewise.unattended_night_receipt.v3` for v4 plans (v2 receipts unchanged and still validated at `:1373`). Adds: `quiet_admission` (policy id and the plan's parameter values), `bind_deadline_epoch_s`, `go_epoch_s` (null on refusal), `samples_total`, `samples_quiet_run_at_go`, `quiet_samples_sha256`, `quiet_samples_lines`, `top_consumers_at_decision`, `load_avg_diagnostic`. Every GO and every refusal carries attribution (`top_consumers_at_decision`) or an explicit `attribution_unavailable: <reason>`. Never emit an intermediate `refusal.json` for a WAIT.

### D6 Driver orchestration (`scripts/run_night.py` ~:316 subprocess helper, ~:1961 onward, :2052/:2064 call sites)

Split `evaluate_night` into (i) static checks (plan, registration, digests, install identity), (ii) dynamic hard checks (D3), (iii) interval admission (D2), keeping the legacy one-shot path for v2 plans as a thin composition of (i)+(ii)+the existing load predicate. The bind loop runs in the driver with the sampler supervised under the bind deadline: the existing 30 s subprocess timeout at ~:316 cannot wrap a 30–60 s sampler — give the sampler its own bounded supervision, keep census and deadline supervision responsive while a sample is in flight (a hung `top` must not block the census or the expiry), and kill/reap a sampler that overruns.

### D7 Retry-policy reconciliation (`joulewise/arm_retry.py`, `docs/process/NIGHT_HANDBACK.md` R1 ~:134, `docs/phase_2/derivation_night_runbook.md` pre-settle prose ~:1200)

`COLD_GATE_CODES["night_refused_not_quiet"]` (`:29`) currently reads "Machine quietness failed; load, power and thermal thresholds stay fixed." Change the text to describe the bind-window semantics (load is diagnostic; CPU cutoff is a sealed plan parameter). Add a separately evidenced zero-capture successor route: `classify_abort` (`:88`) keeps its classes; a NEW helper (name it; e.g. `zero_capture_successor_allowed(result, receipt, delivery)`) returns allowed only when (1) the terminal refusal is one of `night_refused_not_quiet` / `night_refused_agent_present` / the HID-idle and boot-clock codes, (2) there is positive evidence of no start claim, no reservation and no capture (`chain.started` absent, no session id, `runs/instrument_validation` empty per the receipt), and (3) the delivery handoff (`courier.sent`) is complete. `retry_allowed` (`:99`) is unchanged for same-plan attempts; the successor route is a NEW plan (new id, fresh notice, ≥ 60 s spacing, fresh install close), never a re-arm, and the existing same-digest history check must reject a new-plan successor masquerading as a same-candidate attempt. `render_policy` (`:195`) and both generated policy copies must show the new text; fix the stale "85 minutes" prose at `NIGHT_HANDBACK.md:59` to the ten-minute derivation the code uses (`INSTALL_CLOSE_MARGIN_S = 2 × 60` + the 8-minute request lead; read `scripts/run_night.py:90` and `install_close_epoch` ~:1410). R1's new sentence: binding observations inside the window are not retries; a terminal zero-capture machine-state refusal permits ONE new-plan successor under the conditions above.

New contract doc `docs/contracts/night_quiet_admission.md`: written for a reader who has never seen the project. Gloss every term at first use (bind window, sample interval, busy-core equivalent, consecutive quiet samples, terminal vs WAIT, attribution). Give the 2026-09-17 worked example with its real numbers (load 3.66 refused a clean machine; load 1.3–1.5 would have admitted a core-burning daemon; 5 W × 60 s = 300 J vs 5 J). Give the timing derivation with a concrete v4 plan (t0, B = 600, R = 9000, E = t0 + 9600, GO at t0 + 187 s → what remains). State what is provisional and who rules it. A reader must be able to rebuild the mechanism from the text alone.

## Regressions (defect-shaped; each must FAIL on `a90ab4e8` semantics and pass with the fix; say which you confirmed failing and how)

Use injected samplers and a fake clock; never sleep for real interval lengths in tests.

1. `test_bind_go_on_second_consecutive_quiet_sample_at_k`: busy, busy, quiet, busy, quiet, quiet → GO after sample 6; kills first-pass GO, non-consecutive GO, polling-after-GO.
2. `test_bind_expiry_refuses_with_every_sample_recorded`: all busy → refusal at the deadline, `quiet_samples.jsonl` has N lines and the receipt's digest/count match; no intermediate `refusal.json`; kills last-sample-only journals, deadline reset, late GO after expiry.
3. `test_low_load_busy_daemon_never_admits`: load 1.2 with one process at 0.9 core → WAIT every sample; kills load-controls-admission, any name exemption, wrong core normalisation.
4. `test_finished_burst_admits_despite_high_load`: load 3.7, interval busy 0.02 core → quiet; kills a retained load veto and stale `%CPU` use.
5. `test_census_hit_during_bind_is_terminal_agent_present`: census hit on sample 3 while CPU quiet → `night_refused_agent_present` immediately; kills reuse of the initial census, waiting for the agent to leave.
6. `test_cpu_aggregate_identity_and_observer_accounting`: ten small processes each 0.02 core → busy 0.2 (aggregate, not per-process cap); PID reused with a new `lstart` is a new identity; an exited process's delta is not lost; the observer is present in `top_consumers` with `observer: true` and counted.
7. `test_v2_plan_bytes_and_semantics_unchanged`: a committed v2 plan fixture validates identically, `night_plan_mapping` output is byte-identical, evaluation is one shot at t0 with the load predicate; a v4 plan with a missing key, an unknown policy id, or `window_max_s < bind_max_s + post_bind_budget_s` is refused at validation; transaction-pack v3 tests unchanged.
8. `test_late_go_preserves_absolute_deadlines`: GO at t0 + 540 s leaves `E`, completion, courier and dead-man exactly as for GO at t0; a driver starting at t0 + 300 s has only 300 s of bind left; a wall-clock rollback during binding does not extend the deadline.
9. `test_zero_capture_successor_requires_delivery_and_no_start`: refusal receipt alone → not allowed; refusal + `courier.sent` + no start evidence → allowed as a NEW plan; a started or reserved night → not allowed; the successor cannot reuse the predecessor's digest as a same-candidate attempt.
10. `test_sampler_hang_cannot_block_census_or_expiry`: a sampler that never returns → census still runs at cadence and the deadline still fires; a malformed sampler output is a probe error, never quiet.
11. Generator: `--check` byte-identical without the flag; with `--quiet-admission-json` the v4 plan validates and the runsheet states the bind allocation.

## Verification you must run and paste

- `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -5` (rc and counts).
- `python3 scripts/quick_suite.py --tier quick --workers 4 2>&1 | tail -5`.
- `python3 -m compileall -q scripts joulewise; echo rc=$?`.
- `python3 scripts/gen_derivation_night.py --check; echo rc=$?`.
- A LIVE sampler smoke on this machine (read-only, no arming): run the `cpu_interval_v1` sampler once for one 30 s interval from the worktree and paste the parsed metrics line (busy_cores, host_busy_cores, top three consumers, load diagnostic). This is evidence for the cold gate, not a test.
- The counterfactual for regressions 3 and 4: show each failing against the legacy one-shot path (call the legacy evaluation with the same injected observations) and paste the failing assertion.
- `git log --oneline a90ab4e8..HEAD` and `git status --short` (clean apart from committed work; nothing outside WRITE_SCOPE).

## Rules

- No arming, no `launchctl`, no `~/night-custody`, no `[QUIET-MAC]` work, no network, no `sudo`.
- Do not change any measurement, instrument or claim constant; do not touch `NIGHT_DRIVER_REASON_CODES` except to add what D5/D7 require, and say what you added.
- If a clause of `docs/contracts/pack_night_go_receipt.md` or the pre-registration pins a shape you would need to change, finish the code and stop with NEEDS_RULING quoting the clause.
- Final message: the claude-codex-report/v1 envelope (the --genre implementation contract), UNDER 8000 BYTES — changed files, commits, test tails, the live sampler line, the counterfactual evidence, and any early return. Long output belongs in commit messages, not the envelope.
