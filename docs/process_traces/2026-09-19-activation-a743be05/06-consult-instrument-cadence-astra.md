```json
{"schema":"claude-codex-report/v1","genre":"root_cause","status":"findings","completion":"complete","summary":"Longer native intervals confirmed; no frame loss; binary-versus-OS cause unresolved.","workspace":{"base_requested":"010ff2e0","base_mode":"exact","head_start":"010ff2e0","head_end":"010ff2e0","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"cause":"unresolved","remediation":"proposed"},"verification":[{"id":"V1","kind":"inspection","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw_cadence_ro.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["TOTAL 20605 SLOTS 24 RAW_CSV_1_TO_1_OK PARTIAL_TAILS 0"]},"expected":{"exit_code":0,"tail_regex":"RAW_CSV_1_TO_1_OK"}}],"flags":[]}
```

## Causal chain

1. **Confirmed, read-only:** 20,605 raw frames map one-to-one to each CSV rail; widths match elapsed_ns within 0.120 microseconds. Artifact hashes match local manifests; accumulated elapsed time matches native timestamp spans within one second.
2. **Probable:** coarse intervals remove plateau interiors; onset excursions need further explanation. Established evidence: `docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md`; `docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md` (FAIL).
3. **Unresolved:** nominal 100 ms timers plus late wakeups, sampler work or blocking all fit long elapsed_ns. Programmed timer changes are unproven.

Raw **ms: min/median/p95/max** (nearest-rank p95); N = frames/rows per rail:

|Slot|N1 N|Night 1|N2 N|Night 2|
|---|---:|---|---:|---|
|d01|871|110.4/244.3/274.0/284.5|862|110.5/247.6/274.6/419.1|
|d02|850|113.5/248.8/273.0/353.3|860|111.4/247.5/274.4/412.7|
|d03|851|110.9/249.2/274.1/284.4|874|112.0/245.0/274.2/281.7|
|d04|862|112.2/245.5/273.9/282.4|880|113.9/244.0/276.9/287.6|
|d05|855|113.4/247.7/274.2/299.1|860|114.2/249.9/274.5/284.9|
|d06|869|110.5/245.8/273.3/283.2|863|112.2/249.1/274.9/284.8|
|d07|855|112.7/249.7/274.8/309.4|862|112.0/247.3/272.8/345.4|
|d08|860|110.8/248.9/274.1/307.8|865|111.6/246.6/273.8/320.2|
|d09|862|110.9/247.1/273.6/290.2|843|114.9/250.5/274.7/399.3|
|d10|856|114.5/246.9/274.1/282.3|845|114.4/254.3/276.5/280.5|
|d11|862|113.5/248.1/274.1/281.4|846|111.1/251.5/276.1/358.7|
|d12|855|112.0/248.6/273.9/280.1|837|113.3/251.6/276.2/280.8|

Delivery jitter is unmeasured: CSV endpoints are reconstructed, not arrivals. Startup lag bounds (71–218 ms) are not steady jitter. This is not a fixed 250 ms clamp: 1,726 intervals are <150 ms. N1 d07/d10 endpoint gaps have the known unresolved-anchor artefact; use raw elapsed_ns.

## Remediation

**Q2 — proposed only.** Exact production command (`joulewise/adapters/powermetrics.py:1486`; `scripts/validate_powermetrics_fiducial.py:2276`):

```sh
sudo -n /usr/bin/powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o OUTPUT
```

Production is unbuffered file output, without hide flags; retain the file control.

Bench: `/bin/zsh /tmp/jw_cadence_bench.zsh`; [recipe](/tmp/jw_cadence_bench.zsh), [recorder](/tmp/jw_cadence_probe.py). Fixture-tested.

Matrix, 90 s/run: production 100/50/200; minimal `cpu_power,gpu_power` 100; production 100 + `--hide-cpu-duty-cycle`, each idle/one-core busy. Reverse ordering; repeat end baselines. Add file+hooks, stdout-direct, stdout+hooks versus file-direct. **15 runs, 35 min with settling**. If minimal helps, isolate ANE/thermal; confirm winner/baseline in both states (~10 min).

Record raw frames/elapsed_ns/native dates, independent wall/monotonic arrivals, adapter readiness/parse stamps, exits, CPU/busy cores, identities, power/thermal state and census. Summarise intervals/arrivals/parser lag as min/median/p95/max, startup separately. Relative lag drift is `Δarrival−elapsed`; absolute latency needs an anchor endpoint interval. Whole-second dates are insufficient. Nominal polling: reader 5 ms, adapter 50 ms; wakeup delays unbounded. Hooks add work.

Rules: sampler/hide-dependent raw improvement implicates collection/output work; isolate ANE/thermal. Short native intervals with burst arrivals imply delivery jitter; long intervals in direct file/stdout put delay upstream. Hook-only slowdown implicates observer/readiness; frame mismatch implicates parsing. Constant `elapsed−requested` across 50/100/200 supports overhead; constant elapsed supports a floor/coalescing hypothesis. Idle/busy reversal shows state dependence, not uniquely scheduling.

Compare a compatible retained signed old binary on this OS (`--binary "$OLD_PM"`), matched settings/reversed order; never replace the system binary. Same-binary approved OS boots test OS/runtime; 2×2 binary/OS tests interaction. Missing counterfactuals leave attribution unresolved; scheduler claims also need wakeup/blocking evidence.

Controlled runs: **[QUIET-MAC]**, including synthetic busy. Agent-live timing smoke could be **[DIAGNOSTIC]** scientifically, but requires a prospective lane ruling and cannot supply idle/power evidence. Offline: [AGENT]; alternate boot: [ED-EXTERNAL].

Pilot `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json` supplies raw cadence/busy-core covariates for free; these nights already answer Q1. Add offline distributions/correlations. Collect arrival stamps/contrasts separately; new observers would change the frozen pilot.

**Q3 — cold-gate candidates.** Restored ~120 ms cadence needs shared argv/identity pins; rail/schema checks (never invent ANE zeros); readiness/idle-count/duration review; clock/pulse/energy replay; focused+canonical tests; agent-free phase-varied pulse validation. Acceptance remains stale until authorised continuation/successor issuance.

Otherwise trial **2 s pulses**, retain 59 pulses and phase-varying gaps. With maximum admitted interval h, `L−2m ≥ (k+1)h` guarantees k full cells under continuous coverage. For m=.25, observed h≈.42, L=2 permits two; validate future tails. Change protocol/hash, duration authentication (now .8–1.2 s), budgets and thermal validation.

Interior evidence, SNR/detectability, edge coverage, clock feasibility and residual-plus-anchor accounting are **evidence-bound principles: keep**. The .25 s margin is empirical transient separation: retain initially; revise only with ramp evidence, not to admit otherwise empty cells.

Level **.03289849 s** and bracket **.009724 s** are **r6 maximum/range, not physics limits**. Keep historical equivalence: FAIL stands. Permanent successor ceilings are unjustified. Prospectively derive new level/range/prediction allowances from a fixed corpus; neither scale by 250/120 nor fit these failures. Propagate uncertainty into floors/claims.

**Q4.** Tonight: review probe, then agent-free attribution/reversal (~45 min). Desk implementation/cold-gate work: ~2–6 h; OS crossovers may add more. Quiet pulse/clock validation: 30–60 min. Freeze membership/exclusions/sample size/stopping, then resume derivation; three 12-slot nights, if retained, cost ~2.2 h each. Do not mix failed old-protocol nights into the revised corpus.

## Disproved alternatives

Alternate-frame loss and delivery-only delay contradict raw parity/elapsed_ns. Anchoring cannot alter raw cadence. R6 acceptance already re-derived its corpus under anchor-v3 (`calibration_acceptance_d079_v2_n17_r6.json`); stored v1/v3 labels are not an estimator comparison.

## Residual risk

Read-only; no instrument/network/repository writes or canonical-root Git. Clean at 010ff2e0. R6: 14 raw members checked, three unavailable. File/stdout fixtures: `FIXTURE_12_FRAME_PARITY_OK`; syntax passed. No live validation.

Paper: disclose OS/binary/MLX identities, requested/realised cadence, FAIL (11/24 valid), exclusions and separate protocols/epochs; binary causation is unproven. D-078's 2026-09-04 addendum limits the historical ~1 J claim: retain interval-overlap allocation and both uncertainty roles, not a universal accuracy guarantee.