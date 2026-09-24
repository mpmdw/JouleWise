# Q2 — B1 wall meter by phase and bit-width

## Review text

Record 02 §3, “Proposed scientific questions,” B1 asks, “Is `powermetrics` biased by phase or by quantization?” It calls for a wall/powermetrics ratio for compute-bound prefill and bandwidth-bound decode across bit-widths, with an IOReport counter; it hypothesizes a larger decode ratio (docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:138-144). Its original “buy the meter” step in “Suggested order” is stale: the same record's §2 bench check says the KM003C was connected and reading on 09-23 (same file:18-20,166).

## Existing authority and collision

- D-091 is the adopted metrology-first paper pivot; D-092 ratified a wall-meter check but reflects its older no-hardware state (docs/decision_log.md:135-136). The Q6 boundary-sensitivity research row names the P1-003 wall-meter prerequisite and forbids a wall/rail conclusion flip without a paired plan, though the 09-04 capstone coverage cuts Q6 (docs/research_question_registry.md:51; docs/research_question_coverage-2026-09-04.md:49).
- E214, WALL-METER-GAIN-01, is the current phase-gate lane for calibrating software-counter gain (TASK_QUEUE.md:935). B1's phase × bit-width scientific comparison is wider than that named gain check. The powermetrics rail manifest is CPU, GPU and ANE (joulewise/adapters/powermetrics.py:50-58), so the ratio crosses measurement boundaries and must label them.
- D-166's current _v5 decode workload uses pinned thinking-off 512-token Qwen3 runs; the existing admitted Qwen3 panel is 4-bit for both sizes (docs/decision_log.md:10755-10762; configs/model_panels/qwen3_4bit.json:5-16,38-49). A bit-width factor requires other pinned weight artifacts and a new registration.

## Tooling and timing

- The archived local tool is /Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py, with meter_paired.txt and protocol-research material beside it. The probe documents vendor bulk VID/PID and prints epoch time plus V, A and watts; the archived output shows repeated samples about 0.5 s apart (archive/km003c_probe.py:2-14,120-133; archive/meter_paired.txt:1-6, using the absolute archive root above). The tool is archived, not a repository measurement adapter. A repository search returned no KM003C path in joulewise/, scripts/, configs/ or tests/; the command and empty tail are in 06.
- The MLX runtime already emits prefill start, first-token prefill end/decode start, decode end, and per-token timestamps (joulewise/adapters/mlx_runtime.py:740-755,774-835,880-890). Phase alignment to KM003C samples needs a shared clock/anchor, meter latency and interval semantics, and sustained phase segments; these are requirements inferred from the recorded epoch samples and event stamps, not validated behavior.
- The archived probe is a readout demonstration, not calibration evidence. The review's note that a 1 Hz meter suffices for long steady decode is a design assertion (§6 B1); the archive shows a configurable interval but does not establish meter accuracy (record 02:140-144; archive/km003c_probe.py:13,131-134).

## Change surface and schedule facts

A governed B1 result would add a repository meter adapter or imported immutable meter log, calibration and alignment evidence, phase/bit-width registrations, paired run manifests, reduction and uncertainty code, and paper-boundary labels: several files and at least a design, bench and cold review session (estimate from docs/orchestration.md:84-99 and docs/research_question_registry.md:51). It could satisfy part of E214 and supply an accuracy result while A3 or MATH runs; true simultaneity with another quiet measurement needs an authorized integrated night and matching registration, because the current night driver owns an exclusive window (scripts/run_night.py:684-685). The current Q2 quiet gate remains the first ready _v5 collection task (RUN_STATE.md:5394-5404).
