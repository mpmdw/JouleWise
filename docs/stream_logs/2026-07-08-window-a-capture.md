### WAC-1 [5.5] [contract] Run-scoped environment snapshots

Decision: Capture `metadata.environment` per bundle at prepare end, immediately before the `idle_baseline` stage, with `capture_scope: "run"`, and expand it with nullable memory, display, power-adapter, uptime/boot, and clock-sync fields.

Alternatives: Keep the experiment-shared snapshot and add only experiment-level fields; capture at run start before adapter validation.

Why: Window A needs the environment that actually precedes each measured idle baseline. A run-start capture can drift before idle; a shared experiment capture loses per-repetition display, charger, load, and memory-pressure changes.

Evidence: `joulewise/controller.py` captures after runtime prepare and waits a recorded settle interval before idle sampling; `joulewise/environment.py` keeps every probe fail-soft with errors recorded under `metadata.environment.errors`.

Confidence: High.

Binds: Future captures may add fields, but per-run snapshots must remain outside the measured window and must not make host probe failures fail a run.

### WAC-2 [5.5] [contract] Experiment-level cooldown raw traces

Decision: Preserve cooldown sub-window readings as experiment-level raw JSONL artifacts referenced from manifest cooldown notes.

Alternatives: Write cooldown artifacts into the just-finished member bundle; write them into the next member bundle; store all readings inline in the manifest.

Why: The just-finished bundle is already finalized before cooldown starts, so modifying it would violate bundle immutability. Experiment-level raw artifacts keep cooldown evidence outside member measured windows, summaries, and strict member re-reduction.

Evidence: `joulewise/controller.py` writes `runs/experiments/raw/<experiment>__cooldown_after_<member>.jsonl` and records `raw_artifact` in the cooldown note.

Confidence: High.

Binds: Cooldown artifacts are experiment evidence, not member-bundle evidence; validators and reducers must not include them in request energy.

### WAC-3 [5.5] [contract] Inter-run gap handoff

Decision: Record `preceding_member_end_s`, `idle_start_s`, and `preceding_gap_s` under `metadata.extra`, and mirror member gaps in experiment manifests.

Alternatives: Record only a manifest field; record only controller log timestamps; infer gaps post hoc from bundle event files.

Why: The controller has the authoritative timestamp handoff and can compute the gap before writing metadata. Keeping it in member metadata makes each bundle self-describing for drift analysis while the manifest gives campaign-order access.

Evidence: `run_experiment` passes the previous member end timestamp into the next `run_benchmark`; `_stage_idle_baseline` computes the gap at idle start.

Confidence: High.

Binds: First repetitions use `null` for `preceding_gap_s`; later repetitions record the raw signed gap ending at post-settle idle start. Negative gaps are not clamped and set `clock_step_suspect: true`.

### WAC-4 [5.5] [contract] MLX phase and memory boundary markers

Decision: MLX emits generic, non-overlapping `tokenize` and `generation_setup` phase windows before `prefill`, and records memory snapshots at prepare end and cleanup start only.

Alternatives: Treat tokenization as part of prefill; add a single runtime-overhead phase; poll memory through decode.

Why: Tokenization happens inside the measured request before prefill, so it needs its own phase for honest request-energy decomposition. Memory polling inside decode would contaminate the measured loop; lifecycle-boundary snapshots provide fit/fail context without decode overhead. A `run_end` snapshot is inside the sampled window because it evaluates before the controller stamps `sampling_stopped_s`, so it contaminates every real MLX energy summary. `cleanup_start` is outside the sampled window, and MLX Metal peak memory is cumulative, so peak fidelity is preserved there.

Evidence: `joulewise/adapters/mlx_runtime.py` adds phase events and guarded RSS/MLX Metal memory snapshots; reducer tests verify new phase names are discovered generically.

Confidence: Medium-high.

Binds: Phase consumers must pair phase events by name, not by a fixed prefill/decode set. MLX memory APIs remain optional across versions. Do not restore an MLX `run_end` memory snapshot in `run_workload`.

### WAC-6 [5.5] [contract] Sudo-free display and clock probes

Decision: Use `ioreg -r -c IOMobileFramebuffer` for display presence/counts and `pgrep -x timed` for clock-sync process evidence. Do not parse `systemsetup` output in sudo-free captures.

Alternatives: Keep the fabricated `IODisplayConnect` fixture; parse `systemsetup` error banners; rely only on `system_profiler SPDisplaysDataType -json`.

Why: `IODisplayConnect` is absent on the target Apple Silicon/macOS stack, while `IOMobileFramebuffer` returns real data quickly without sudo. `systemsetup` requires admin privileges and can exit with an error banner unsuitable for NTP-state parsing. `pgrep timed` provides a limited but honest sudo-free signal.

Evidence: Live target verification showed `ioreg -r -c IOMobileFramebuffer` returning framebuffer entries in about 20 ms. In the current sandbox, `pgrep -x timed` is sudo-free but process-list access returns `returncode_3`; the capture records that as limited evidence instead of fabricating NTP state.

Confidence: Medium-high.

Binds: Display captures must record `status: "probe_unavailable"` with a reason when the framebuffer probe cannot produce entries. Clock captures use `status: "limited_without_admin"` and `timed_running` only; admin-only `systemsetup` state is intentionally absent.

### WAC-5 [5.5] [contract] Powermetrics sampler provenance

Decision: Record `metadata.device.powermetrics.samplers_requested` as the exact requested sampler string and `samplers_available` as either the requested sampler list confirmed by the capability preflight or `"probe-unavailable"`.

Alternatives: Add a separate sampler-listing powermetrics invocation; enable additional samplers for Window A.

Why: The requested-sampler capability probe is already required before powermetrics captures and does not change the sampler set. It distinguishes requested-and-confirmed from unavailable without adding new powermetrics overhead or permissions behavior.

Evidence: `joulewise/adapters/powermetrics.py` records sampler metadata during capability probing and leaves denied/unavailable probes fail-soft.

Confidence: Medium.

Binds: Do not widen `SAMPLERS` for Window A without a separate overhead smoke.
