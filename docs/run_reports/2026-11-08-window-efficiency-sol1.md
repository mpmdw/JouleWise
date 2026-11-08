# window-efficiency-sol1 handoff

Brief date: 2026-11-08. Branch: `perf/2026-11-08-window-efficiency-sol1`.
Independent design seat; no other window-efficiency seat branch read.

Delivered [WINDOW-EFFICIENCY-sol1.md](../perf/WINDOW-EFFICIENCY-sol1.md):
source-pinned W1, recurring D and R1 budgets; per-phase knowns/unknowns;
confound/evidence/alternative matrix; complete lean and aggressive F/C/T
allocations; and analyses of tonight's unchanged R1 records.

Mission M0: read root AGENTS/CLAUDE, playbook M0, source-of-truth map and report
conventions, stop-card (NONE), Current Project Status, Known Workspace State,
queue intake/current and Do-Not-Do-Yet pointers, orchestration role/write rules,
RUN_STATE items 160–213 and targeted decision authority. User's explicit task
selects this desk investigation and forbids coordination-state edits; no kernel
task registered. Checked branch/status and recent commits; tree initially clean
on the exact requested branch. No other writer was observed in this clone.

Read the requested kit sources through cached Git objects at `d600baba0`,
including R1 phase/runtime tables and R10's final cold-review corrections.
Read timing/calibration/validity sections across all eight cached v5-design
seat/judge documents and the later adopted agreement at `4526de7d5`.
Unblinded v3 evidence came from protocols/config sizing receipts, RUN_STATE
pilot summaries and targeted ALIGN run-report sections. Implementation reports
are not treated as native measurements. External source paths were text only.

Key findings:

* W1 is 18 members, 7.480 h programmed / 12.400 h maximum; no calibration m.
* D frame is 22 members but 18 D: 11.258 h programmed, 16.183 h planning
  reservation, 16.533 h authorized cap. Six of 22 are anchors/sentinels.
* R1 helper is 15.613 h with no redo, 17.113 h with one batch wait, and
  25.184 h with all R6-2 retries plus one wait. Physical calibration/harvest,
  ordinary redos, a second daily overlap, and the documented idle-bound caveat
  remain outside those headline helper cases.
* No evidence isolates the variance reduction purchased by D's gates yet.
  R0 long recovery cautions against unconditional short waits. V3 clock
  correlation is not causal proof; missing historical temperatures cannot be
  reconstructed by regression.
* Lean retains the physical experiment. Maximum-slot versus early-finish
  calendar savings must not be sold as physical acceleration. The aggressive
  option needs new thermal calibration and a native 1,200 s envelope; its
  qualification/fit costs erase most of a small campaign's throughput gain.
* R11 supersedes the older receipt-path contrast veto; current kit/protocol
  reconciliation is lead-owned. U3 and full Q6 fit/calibration/test roles are
  still registration work. The report proposes capacity, not new authority.

Only two documentation files changed: this report and the requested analysis.
RUN_STATE, TASK_QUEUE, state kernel, tests/test_gen_state.py, production code,
raw evidence, model files and registration artifacts were not changed.

No full suite, measurement pipeline, native MLX test, model download, live
instrument, analysis job/process census, network access or push was run.

Verification:

1. Executed the document's `WINDOW_EFFICIENCY_AUDIT` block with
   `python3 -B` using this exact file-only extraction. **PASS**: W1/D spans
   and reservations; R1 bound/retry arithmetic; both-pair calibration loss
   margins; complete campaign hours/days; slower-envelope sensitivities.

   ```sh
   python3 -B - <<'PY'
   from pathlib import Path
   p = Path('docs/perf/WINDOW-EFFICIENCY-sol1.md')
   s = p.read_text()
   code = s.split('```python\n# WINDOW_EFFICIENCY_AUDIT\n', 1)[1].split('\n```', 1)[0]
   exec(compile(code, str(p) + '::arithmetic_audit', 'exec'))
   PY
   ```

   Known subtotals: baseline 268.979712 h; lean 195.118045 h; max
   186.942212 h. Unknown C_R and retries remain additional. The initial
   audit failed on an incorrectly transcribed extra decimal in this author's
   expected deadman value; corrected to 1277.0379764672725 s and reran to
   PASS. This was an authored assertion error, not a repository test failure.

2. A separate `python3 -B` stdlib AST audit used the pinned K/RP source
   snapshots, extracting only the pure roster/deadman/phase/bound functions.
   Production imports were omitted; config/host-reading helpers were replaced
   by constants from committed `r1_runtime.json`. **PASS**: 18-member W1
   roster, 5/17 identity, ordinal 18 seed 93, nine L1 intercept/tail fits,
   actual 19-phase R1 table and all four helper totals, optional 4-bit
   +1,800 s increment. No production module or model path was opened by it.

3. Documentation structure/link/protected-path checks: **PASS** (balanced
   fences, consistent table columns, live local links, only the two named
   documentation additions, protected-path diff empty).
   `git diff --cached --check`: **PASS**, exit 0. No production
   code changed, so compileall/unittest/full-suite expansion was unnecessary;
   the full suite is explicitly prohibited by this brief.

Local commit: `docs(perf): audit v4 window budgets and cost lean and max designs`
on the requested branch; parent `4e7e878a1`. No push. The final response gives
the resulting commit ID. No independent fresh review or native validation is
claimed; the lead owns adoption/registration and final scientific review.

Open uncertainties: actual R1 timings/phase shares, D prefill and tails,
G0-after-30B behavior, calibration-score exchangeability, attrition and the
native ungated envelope. Cost totals expose unknown R1 scaffold/harvest as C_R;
they are not unconditional completion guarantees. No new decision-log ruling
was made. No code or MLX tests were added, so there is no new native test module
for the lead; any adoption still requires the existing native gate/hold/reset
qualifications and the report's explicitly new-policy qualification. Relevant
existing native modules on the kit lane include `tests.align.test_thermal_mlx`,
`tests.align.test_smc_native`, and
`tests.align.test_history_rendering.NativeHistoryRenderingTests`. The lead
must run applicable checks on the pinned native MLX/Metal environment with
agents stood down, after R1 and before adopting changed native behavior. These
tests do not replace B's new ungated multi-turn qualification or authorize
running anything during the armed R1.

Next exact step: the authorized custodian exports the report's timing-only R1
timeline/admission worksheet after R1 closes; the lead reconciles R10/R11 and
freezes the series plan before W1 registration. Do not change the armed R1.
