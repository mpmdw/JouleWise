# Handoff: v5-design-groundup-sol2

- Brief date: 2026-11-08
- Branch: `align/2026-11-08-v5design-groundup-sol2`
- Base: `32ba49285`

Deliverable: [ground-up v5 proposal](../v5-design/groundup-sol2.md)

## Built and recommended

Wrote a complete ground-up experiment proposal, not runnable measurement code or an installed registration. It includes model/configuration candidates, synthetic main/side task pairs, quantitative capability gates, shadow detector arms, bounded adaptive search, functional threat coverage, frontier monitor, runtime-external controls, meter/battery/tail requirements, estimands, rank thresholds, clustered-power calculations, blinding, sample sizes, Mac/replay costs, calendar, risk-retirement gates and a component-reuse map.

The central recommendation is a new calibration cohort and a strong software comparator including seeded rerun, trusted time and available process accounting. Primary candidate: Qwen3-30B-A3B-4bit, conditionally replaced or secondarily replicated by Qwen3.8-27B-4bit. Model selection and a new 900 s member envelope need lead approval and native qualification; this proposal does not amend the v4 production ruling.

Primary held-out design: 336 sabotage attempts and 280 honest trials over fourteen test windows, plus 56 controls and 56 sentinels. Calibration: 39 honest members per pair over seven sessions. Under the stated planning correlation/discordance assumptions, synthetic clustered-t power is about 85% for a 10-percentage-point escape-rate improvement. A 5-point improvement is poorly powered. The primary study reserves about 439 Mac-hours with contingency; a smaller second-model replication brings the reservation to about 577 h. Software rerun alone costs 75.4 h in the primary plan and is explicitly charged.

With 39 calibrators, two maximum-threshold channels give a marginal 5% union bound under exchangeability. A three-channel OR would give 7.5%. The proposal therefore calibrates a frozen software composite as one channel and guarded DC-in residual as the other; the equal-FPR software-only comparator uses rank 38 rather than rank 39. The document distinguishes this marginal guarantee from a high-confidence conditional FPR claim.

Subjective probability of a main-track-strength scientific result: about 30% (15–45% range), not an acceptance forecast. Equal-compute sabotage, weak actors and a software baseline that already catches hidden work can legitimately defeat the headline.

## Files and commit

Only these repository files were added:

- `docs/align/squeeze/v5-design/groundup-sol2.md`
- `docs/align/squeeze/fanout/v5-design-groundup-sol2.md`

Local commit subject: `docs(align): propose ground-up v5 squeeze experiment`. The commit ID is returned in the final handoff; it cannot be embedded in the same commit without changing that ID. No push requested or performed.

No changes to RUN_STATE.md, TASK_QUEUE.md, the state kernel, tests/test_gen_state.py, R1's lane or production code. The requested branch was already checked out and clean at intake. Explicit user scope took precedence over coordination-state close-out instructions. No other agent/seat was consulted, and no independent scientific review is claimed.

## Verification

All calculations used synthetic constants and Python's standard library. No network, model download/execution, hardware capture, real measurement read, Block-5 pipeline or full test suite was used. Total checks were well under one minute, excluding document reading/writing.

1. **Failing-first design counterexample:** in a temporary synthetic unittest module, ran:

   `V5_ARITHMETIC_CHANNELS=3 python3.13 -B -m unittest test_groundup_arithmetic`

   Result: six checks run; one expected failure, `0.075 not less than or equal to 0.05`. This rejects a naive three-channel m=39 FPR budget. It is a design check, not a failing production regression test.

2. **Chosen design:** same module, one process:

   `python3.13 -B -m unittest test_groundup_arithmetic`

   Result: **6/6 PASS**. Checks cover rank laws, the conditional-tolerance sample size, roster conservation, night envelope, planning power, and costs including software replay. Temporary module: `/private/tmp/v5design-groundup-sol2.dUG4BG/test_groundup_arithmetic.py`; the durable proposal contains independently executable arithmetic.

3. **Executed the proposal's Python appendix** directly from its sole Python fence:

   ```sh
   python3.13 -B - <<'PY'
   from pathlib import Path
   s = Path('docs/align/squeeze/v5-design/groundup-sol2.md').read_text()
   code = s.split('```python\n', 1)[1].split('\n```', 1)[0]
   exec(compile(code, '<groundup-sol2-arithmetic>', 'exec'), {})
   PY
   ```

   Result: PASS. IID sample-size approximations 43.17 / 149.13 / 463.08; effective n 198.82; primary cost 350.9 h; replication 110.9 h; reserve 577.25 h; synthetic Gaussian-window powers .849375 and .39505. These are planning calculations, not measured effects.

4. Checked new-document local links, fenced-code balance and whitespace; reviewed the final two-file diff. `git diff --check` passes. No production test module was touched, so production unit tests and compileall were unnecessary for this documentation-only change. The full suite was expressly forbidden by Ed's blinded-job constraints.

## Native / live checks still owned by the lead

All hardware behavior is **PROVISIONAL**. No MLX test ran in this sandbox. Outside this sandbox, in a clean agent-free slot where required, the lead must run native qualification for:

- Actual candidate-model artifact identity, MLX loading/memory, parser/template and reasoning-history preservation, 12-turn completion, cache/checkpoint exactness and per-turn reseed determinism.
- Seeded actor rerun using the actual invocation rather than a different benign prompt; trusted tool replay, process accounting and hidden side-generation/subprocess controls.
- Sustained throughput and the complete 900 s member, thermal release/hold behavior, battery float, meter cadence/gaps/clock bounds, 180 s recovery-tail closure, and uncertainty-guarded DC-in detection.
- Native software-replay throughput assumed to be 360 s/member; recost at the measured rate.

The exact native test-module names must come from the owning implementation branches; they are not visible on this branch, and I did not invent commands or inspect R1 to obtain them.

## Lead rulings assumed; unresolved questions

Assumed binding: Ed's in-path KM003C/whole-member authority; amended D-139 A1 for a sandboxed actor; off-box frontier API monitor; no v4 scoring before registration; at least 39 calibrators per pair plus held-out tests; runtime-external positive controls; escape per attempt as primary; synthetic-only/no-network/no-full-suite work in this clone.

New recommendations requiring adjudication, not assumptions: the primary model ladder, new synthetic task twins, 900 s thermal/member envelope, one frozen software composite plus energy, immutable API version, and a dedicated Mac allocation. Existing v4 calibration is intentionally not reused because the configuration and score differ.

**NEEDS_RULING — threat IDs only:**

- **Question:** What is the authoritative A0–A13 definition artifact, and how should its IDs map to the proposal's F0–F13 functional challenges?
- **Options considered:** guess existing ID meanings; inspect another seat's branch; or leave the crosswalk explicit and unresolved while completing the design.
- **Recommendation:** supply the owning threat-model artifact to the lead and perform an explicit crosswalk. I requested this source during the run; none was supplied before handoff.
- **Blocked work:** certification of A0–A13 coverage and registration of the final threat matrix. The proposal and local commit are complete. Existing IDs were not redefined.

Next exact step: lead resolves that crosswalk and approves a capability-and-cost development charter. Complete the small capability, real incremental-value and native-envelope gates before spending any new calibration seed. Do not start a quiet measurement from an active agent session.
