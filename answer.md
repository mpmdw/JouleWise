# ALIGN v4 Window 1 plan — handoff

Drafted [the executable plan](docs/align/WINDOW-1-PLAN.md) for the measurement
MacBook Pro: Qwen3.8-27B 8-bit now, Flash-Next later. The plan covers the
integrated kit requirements, headless R0, quiet R1, thermal/token controls,
Window 1 roster, fresh seed reservations, calibration contract, failure paths
and a ready-to-paste Next activation block. It preserves the original 30B
anchor bytes and keeps D checkpointing off for the series.

The plan is **not a built kit or live qualification**. It names the required
integration repairs before the headless magistrate can run. Window 1 remains
development/selection data; no v3 thresholds or sample counts transfer to D.
Source pins and file/line citations are in the plan's source table.

## Branch, files and commit

- New local branch: `lane/2026-11-05-align-v4-window1-plan`.
- Parent: `6eb1ff5be31bec330ae5af262c2b4c7601e7755e`, the checked-out
  council lane head (PR #656). No other lane was merged.
- Changed files: `docs/align/WINDOW-1-PLAN.md`, `answer.md`, and
  `docs/run_reports/2026-11-05-align-v4-window1-plan.md` only.
- Local commit message: `docs(align): draft v4 Window 1 plan and headless handoff`.
  The final response supplies the resulting commit SHA; `git log -1` on this
  branch identifies the commit containing this report. Nothing is pushed.
- No coordination state, code, tests, raw evidence or generated kit was edited.

## Inconsistencies and dispositions

The citations below use the plan's source keys, which resolve to immutable
commits plus repository paths/lines. These findings come from local Git
sources, not current online PR bodies or a hardware run.

| Finding | Plan disposition |
|---|---|
| **#661 vs #659 endpoint API:** R0 checks for/passes `reasoning_effort`; the current endpoint exposes `assistant_history` and `chat_template_kwargs`. The old readiness check rejects the current endpoint. [RB:40–47,88–95; XE:279–288] | Builder must adapt the R0 backend and merge the full production identity/rendering path before KIT_COMMIT admission. |
| **#661 vs fixed #658 SMC API:** #661 expects the old fitted-role proposal/coverage receipt; current #658's R0 is inventory-only with null selections and R1 owns classification. #666 already migrated to the fixed Sidecar. [RH:250–285; T:42–47,66–94,123–125; G:7–11,214–219] | Repair the R0 adapter and explicitly distinguish readability from final R1 sensor selection. Preserve journals and do not reintroduce retired hazard hooks. |
| **SMC duration/selection disagreement:** council's 60 s step and #658's current default cannot supply #661's old slow-fit rule. The later lead ruling in #661 uses 300/900/600 s and different fitted tau bars; final council R1 uses t63/rise/cooling tau. [RS:10–36; T:27–30,72–94,125; F:461–468] | Use the later 300/900/600 duration ruling for R0 capture; require lead admission of its adapter reconciliation. Use the real planning-turn council classifier for final R1 pins, not old R0 fit proposals. |
| **#661 offload prerequisite vs items 170/174:** R0 disk code requires matching offload receipts for pilots 8/9; later state says pilots 8–10 remain on disk. About 66 GB free also misses the 80 GB-plus-journal R0 bar. [RH:145–180; S:1049,1060,1068,1084] | No offload/deletion. Builder needs a retained-root receipt, and the lead needs a safe capacity remedy. The plan does not waive the free-space bar. |
| **#657 enablement vs Amendment 1:** the amendment conditionally enables checkpoints, while the updated implementation says enabling changes the schedule/trajectory of every hybrid turn. Supplied native success covers the pre-fix schedule; revised native qualification is still owed. [A:151–154; C:55–76,164–206] | Follow this brief's default-off requirement. Freeze explicit zero for D before R1/W1; retain omitted fields on legacy anchors. No mid-series enablement. |
| **#660 vs #666 deadman origin:** #660 describes episode-start time excluding prior warmup; #666's thermal path conservatively charges G0/G1/H against a deadline starting at G0 entry. [B:40–48; G:115–125] | Budget using the actual stricter thermal path and measured intercept/waits, not the illustrative transferred deadman. |
| **#659 legacy identity limits:** JSON cap-cut handling intentionally changes; frozen parser fixtures do not prove all actual anchor trajectories unchanged. D judge input has structured calls/separate reasoning, unlike raw legacy JSON history. [X:276–295] | Preserve anchor config bytes and require actual native replay identity; disclose family-dependent judge input. A failed bridge holds admission. |
| **#666 is not the full v4 kit/desk:** the ordinary v3 launcher never selects ThermalRegistry, window reference propagation is external, and the supplied thermal CLI leaves U4–U6 inconclusive. Several estimator conventions remain unregistered. [G:48–65,157–219] | Builder must deliver the integrated launcher, reference custody, full frozen-analysis desk, R1 driver and admitted estimator conventions. Do not treat synthetic library checks as those gates. |
| **Council D indices vs task's fresh-range requirement:** Amendment 1 uses D index 1 and held-out indices from 2, overlapping v3's index range. [A:90,106–109; S:1052] | Explicit plan choices: R0 91/92/95, R1 steps 94, D task development 101/93, calibration 201–242. Only old 30B anchors/contrast intentionally reuse old indices. |
| **Council target vs registration contract:** initial m≥20 is a pilot target; the registration floor remains m≥39 eligible benign per pair for D. [A:103–125; S:1099,1123; Q:45–57] | Initial D1–D3 schedules m=21/pair; predeclared D4–D6 extension schedules m=42/pair, only with registration-grade authorization. No FPR/power claim follows from either count alone. |
| **Extra-sentinel rule vs long-window cap:** an inconclusive U4/U5 calls for two extra sentinels. At guessed D costs, the derived maximum rises from 58,260 to 61,860 s, exceeding the allowed 59,520 s. [F:406–408; A:117] | Hold the next prepare for lead re-sizing with actual R1 costs. Never silently extend the maximum or drop calibration members after outcomes. |
| **Historical state pointers differ:** local origin/main stops at item 173; the supplied state lane contains 174. Older council/state wording requests offload or interactive-only R0, and earlier pointers propose another v3 window. [M; S:1043–1049,1079–1085] | Item 174 wins: pilot 10 last, retained roots, headless R0 only after the lead's concrete kit handoff. The paste block is conditional until filled/admitted. |
| **R1 duration is not a frozen window plan:** the amendment's 2.5–3 h estimate has no complete driver receipt. [A:204–220] | Explicit proposed reservation: core up to 10,800 s, one 4,995 s scaffold, derived maximum 33,540 s. Builder must prove the schedule fits before prepare; no runtime extension. |

## Verification performed here

No unittest, pytest, full suite, MLX execution, SMC capture, pipeline or real
measurement-data read was run. This is a documentation-only change; runtime
qualification would neither validate the prose nor be permitted in this
agent-active sandbox during the analysis job.

- `python3.13 -B -` with a stdlib-only inline document validator: **PASS**.
  Checked 187 keyed source citations against the exact local Git blobs and
  checked explicit file/line ranges. Checked Markdown fences/whitespace,
  window maxima/drop arithmetic, contrast ordinal sums, threshold ranks and
  seed reservations. No repository runtime module was imported.
- The same inline arithmetic/seed check independently derived 96 distinct
  reserved D episode seeds, with no collisions against the 92 v3 model/pair
  seeds at indices 1–46; fresh D indices also avoid that index range. It
  reproduced both historical contrast seeds. D index-101 witnesses:
  spam `10248134863903872330`, bank `9375716026310054484`.
- `git diff --check`: **PASS**; final staged check also required before commit.
- `git diff --exit-code 6eb1ff5be -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py`:
  **PASS**, protected coordination paths unchanged.
- Manual source/diff review: plan-only changes; original council files and
  all build lanes remain untouched. No fetch was attempted: all requested
  refs existed locally and the standing no-network rule controlled.

Native checks still owed by the lead are listed as future commands in the
plan: `NativeHistoryRenderingTests`, `test_thermal_mlx`, `test_smc_native`
and `test_r0_mlx_native`, separately on the pinned Metal-visible Mac with no
agent alive. These small native checks still do not replace real R0/R1.
Revised `test_cache_checkpoint_native` and its benchmark are needed before
any future enabled checkpoint cell, not to enable this series by default.

## Open questions and next exact step

No new model or precision decision is needed. Ed may still need to supply a
missing physical-setup receipt or capacity remedy; the later registration
extension needs his go. High Power/cooler testing is optional, with Automatic
as this headless plan's proposed default. Long D windows retain the council
default unless vetoed.

The **next exact step** is lead review of this draft and the listed integration
repairs, then a concrete KIT_COMMIT and launch/config/receipt paths. The lead
can then admit/paste the Next activation block. Do not execute this document
against measurement paths from the planning clone.

Uncertainty remains explicit: refs were not refreshed, actual model/host/disk
inventories and pilot-10 results were not inspected, the contrast's recorded
turn counts must still be supplied from authorized ALIGN custody, and all
durations/memory/thermal-slot values awaiting R0/R1 are provisional. The R1
reservation, fresh seed ranges, detailed calibration order and Automatic
default are draft plan choices for lead admission, not already-measured facts.
