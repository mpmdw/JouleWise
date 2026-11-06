# WP8 cold review — PR #682 (lane/2026-11-05-align-v4-assembled @ cda5716a1)

Scope: B1/B2 XML tool-call parsing (xml_tool_calls.py, endpoint.py, generation.py),
B5/B6/B7 thermal gates + cache checkpointing (thermal.py, thermal_gates.py,
smc_reader.py, prompt_cache.py, budget.py, stop_precedence.py, workload.py,
diagnostics.py), and attribution.py. Reviewed from `git diff 83e2dac59..cda5716a1`
without reading the plan or earlier review files. Targeted tests run under
`nice -n 19 python3 -m unittest`: test_xml_tool_calls, test_attribution_holds,
test_stop_precedence — 29/29 pass with system python (no mlx locally, so the
native checkpoint path was traced, not executed).

No BLOCKER or HIGH found. The parser, hold/gate overlay in attribution, the
deadman, and the checkpoint prefill accounting trace correctly for well-formed
runs. Findings below are mostly "well-flagged but costly" behaviours and
fail-slow paths.

## Findings

### F1 — MEDIUM (confirmed by trace + probe): a refused XML call ends the episode as a normal return, invisible to the desk
- `joulewise/align/apple/xml_tool_calls.py:146-163, 240-252`; `joulewise/align/apple/workload.py:586-590` (`if not result.tool_calls: break`); no handling in `pilot_analysis.py` / `thermal_desk.py` (only `r0.py:275-276` counts `malformed_tool_call:`).
- Scenario: the model emits `<parameter=n>\n1.0\n</parameter>` for an `integer` parameter, a trailing sentence after `</tool_call>`, or a nested `<function>` word inside a string. Probe: all three return `()` with `malformed_tool_call:xml:...`. The workload then takes the no-tool-calls branch, `primary_stop` yields `episode_returned`, `main_score` is computed on a transcript with zero actions, and the member counts as a normal completed episode in the benign/sabotage pair. The flag is retained but no desk code excludes or even tabulates it.
- Fix: add an explicit stop (`episode.malformed_tool_call:{index}`) when the parse flags include `malformed_tool_call:`/`unsupported_tool_call_format`, rank it in `stop_precedence.primary_stop`, and add it to `pilot_analysis.episode_ineligibility_reasons` and `thermal_desk.calibration_exclusions`.

### F2 — MEDIUM (confirmed by trace): a dead SMC collector thread is detected only at cleanup; meanwhile every gate/hold waits its full cap
- `joulewise/align/apple/thermal.py:150-166` (`_loop` swallows the exception into `_error` and stops); `joulewise/align/apple/thermal_gates.py:431-483` (`wait` never inspects `sidecar._error`/`_stop`); error re-raised only in `Sidecar.stop()` (`thermal.py:191-192`) from `cleanup()`.
- Scenario: `_write` hits ENOSPC/OSError on the 1 Hz journal mid-episode (this project has already lost a run to ENOSPC). Rows stop, 60 s coverage → 0, `unobserved=True` for every subsequent G1/H. With `heavy=True`, `chunk_tokens=256`, `max_tokens=4096` that is up to 15 holds × `turn_cap_s` (≤300 s) per turn, 12 turns, no deadman in the current stage configs (`deadman_s: null`) — hours of wall time for a member that is already certain to be excluded (`thermal.state_unobserved`).
- Fix: at the top of each `wait()` loop iteration, `if self.sidecar._error is not None or self.sidecar._stop.is_set(): flag 'thermal.collector_failed'; reason='timeout'; break` (or raise so the member fails fast). Independently, once `thermal.state_unobserved` is set for the episode, stop scheduling further holds.

### F3 — LOW (confirmed by probe): untyped (Any) parameters lose their quotes and re-render differently, so the history prefix never matches the emitted text
- `xml_tool_calls.py:154-160` (JSON wins for untyped → `"quoted"` becomes `quoted`); `endpoint.py` `_render_xml_prompt` (`"arguments": json.loads(...)`) and the template's `args_value|string if string else tojson` (fixture `qwen38_chat_template.jinja:138`).
- Scenario: probe shows `{"a":"quoted"}` for an untyped `a` given `"quoted"`; the template renders `quoted` (no quotes). Nested objects go through `tojson` (default separators `, `/`: `) while the model emitted compact JSON. The re-rendered assistant turn therefore diverges from the cached token prefix on every such turn → trim/checkpoint-restore + re-prefill of the previous assistant turn and tool results (extra, correctly-labelled prefill energy; defeats the "keep emitted parameter order for cache reuse" intent in the parser comment). Also the model sees `quoted` where it wrote `"quoted"`.
- Fix: for untyped schemas keep the raw wire string when the decoded JSON is a `str`; consider rendering history arguments from the retained emitted text rather than re-serialising.

### F4 — LOW (confirmed by trace): the deadman does not cover the checkpoint prefill or cache reconcile
- `endpoint.py` `_StreamObservation.stream_generate` lines ~188-191 (`prefill_prompt(args[2])` runs before the guarded `while`); `reconcile_prompt` (cache `prepare`/`_restore`, second `_render_prompt`, `plan_checkpoint`) is called by the pinned core outside any `guard()`.
- Scenario: a Metal hang during the manual `self.model(mx.array([chunk]), cache=...)` chunk loop (`prompt_cache.py:175-181`) or during `_restore`'s `mx.eval` is exactly the kind of native stall the deadman exists for; it is only caught by the outer member cap.
- Fix: wrap `prefill_prompt(...)` and the `reconcile_prompt` body in `self.deadman.guard()` (no nesting occurs there — `guard()` refuses an already-armed ITIMER_REAL).

### F5 — LOW (confirmed by trace): G0 silently times out at 600 s per member when no powermetrics status source is bound
- `thermal_gates.py:453-459` (G0 requires `status.os_level == 0 and pm_state == 'Nominal'`), `:331-341` (`_status` returns `{}` with no reader and no `align_thermal_status.json`), `cli.py:344-350` (registry bound only through `joulewise run`).
- Scenario: any launcher that reaches `run_benchmark` without `registry_for_config` (or a config whose `thermal.sensors` is not a dict) gets a `ThermalSession` whose status is always `{}`; every G0 waits the full 600 s and flags `thermal.start_gate_timeout`; every member is then excluded by the desk. Correctly flagged, but a whole window is lost before anyone looks.
- Fix: at G0 entry, if the first sampled row has no `status.pm_observed_ns`/`os_level`, flag `thermal.status_source_missing` and fail the member immediately.

### F6 — LOW (confirmed by trace): after a G0 timeout/unobserved outcome, the episode reference is taken from the latest (hot) sample
- `thermal_gates.py:495-499` (`values = release or latest`; `episode_reference = release_values`).
- Scenario: G0 times out at 600 s with the slow sensor still 4 °C above reference; `episode_reference` becomes that hot sample, so G1/H bands are satisfied immediately and the desk's `member_record` marks those releases `journal_verified` (it checks `gate['reference'] == g0['release']`, which holds). The member is excluded via `thermal.start_gate_timeout`, so no silent inclusion, but the per-gate evidence looks clean.
- Fix: set `episode_reference = None` unless `reason == 'released'`; G1/H then report `unobserved` honestly.

### F7 — LOW (confirmed by reading): counterbalancing now keys on the full `thermal` policy including `window_reference`, which puts the capture member in its own cell and orders it last
- `joulewise/align/apple/campaign.py:26-30, 38-45` (`**spec.execution_policy_projection()` in the cell key; unmatched cells appended after all pairs).
- Scenario: a kit that calls `generate_campaign(..., counterbalance=True)` with WP15 roles would run every `consume` member before the `capture` member; each would be refused with `thermal.window_reference_missing`. Not exercised by `scripts/align_v4_kit.py` (it writes its own `order_manifest.json`), so no current impact — a latent trap in a shared function.
- Fix: strip `window_reference` from the counterbalance key, or assert the capture member is first when thermal roles are present.

### F8 — LOW (plausible): attribution raises on any malformed thermal custody instead of excluding the member
- `joulewise/align/attribution.py:623-655` (`raise ValueError` for ordering/containment violations); consumed unguarded by `thermal_desk.member_record` (`thermal_desk.py:177`).
- Scenario: for well-formed runs the invariants hold (holds start ≥256 tokens into decode; G1 sits in the gap after tools; G0 ends before `start`). But a single corrupted interval in one bundle makes `attribute_episode` raise and the window desk abort for every member rather than reporting one excluded member.
- Fix: in the desk, catch `ValueError` from `attribute_episode` and emit `thermal.custody_invalid` as an exclusion for that member.

## Checked and found correct (for the record)
- Hold/gate overlay: holds are carved from the owning turn's decode; G1 from gaps; G0 must end ≤ `episode.start_ns`; segment sums tile the total (tests pass). `thermal_desk` and `energy_residual` only sum `turn is not None`, so `hold`/`gate` kinds are excluded from owned energy as intended.
- `split_decode_events` boundaries use strict `<` in the pinned reducer's overlap check, so equal-timestamp decode/hold boundaries are not flagged; the workload's `events.sort` is stable.
- `_StreamObservation`: hold entry is stamped after `drain_decode` (drain GPU work charged to decode), resume stamped right before `next(stream)`; a deferred hold is always resumed+persisted exactly once on every exit path; `count % chunk_tokens` guarded by `chunk_tokens ≥ 256` validation; no hold at the last token.
- Deadman: `DeadmanExpired` is a `BaseException`, timer disarmed before handler restoration, nested arming refused; controller runs `run_workload` on the main thread; no other SIGALRM user in the measurement process.
- Checkpoint prefill: runs inside the pinned prefill window with the full delta counted as prefill tokens; chunk loop mirrors mlx-lm `generate_step` (`mx.eval([c.state ...])`, `clear_cache`); `plan_checkpoint` guarantees `0 ≤ count < len(delta)`; restored ArraysCache is deep-copied per restore so checkpoints are reusable. Native 4/4 gate recorded on mlx 0.31.2.
- XML parser: `<tool_call>` inside an unclosed or closed thought stays hidden (probe); `</think>` inside a parameter string survives (probe); empty string parameter round-trips; `Optional[str]` `null` vs `"null"` disambiguated as documented; template `\n` framing matches `removeprefix/removesuffix`.
- `qwen38_config.json` fixture is `model_type qwen3_5/qwen3_5_text`, so both `XML_MODEL_FAMILIES` and `hybrid_checkpoint_policy` cover it; `validate_model_family` accepts the dotted label.
- Controller stage order is prepare → idle_baseline → warmup → measured, so `capture_reference` at warmup entry really sees the last 60 s of idle (sidecar starts before model load).
