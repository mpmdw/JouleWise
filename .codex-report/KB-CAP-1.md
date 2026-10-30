# KB-CAP-1

## 1. Design before implementation

Authority: magistrate activation 4e748ac1, 2026-10-30. M0: no active stop card;
explicit bounded user direction selects this AGENT task over the generated queue.
The exhaustive write scope supersedes kernel/run-state bookkeeping. No hardware,
MLX import, BYTES data, ledger or blinding keys will be used on this seat.

Vehicle: the existing HAZARD_PACK night driver, installer, hazard arm, agent census,
network-time OFF, instrument checks and meter supervision. A new
`joulewise/bytes_stream_capture.py` stage uses
`PowermetricsTelemetryAdapter.start_sampling/stop_sampling_with_evidence`, never a
second capture launcher. The graph is reservation, pre calibration,
`bytes_stream_capture`, post calibration. The existing calibration tools operate
on a fresh test-only ledger with a genesis pin; no claim ledger is copied. The
bookend calibration captures are additional instrument checks, not a split of
the one continuous test capture. The driver starts the one meter stream; harvest
rejects multiple streams instead of fitting restarts separately.

Before editing existing files, the stage dispatch/registry files in scope are:
`joulewise/b5/chain.py` (tool/kind dispatch, graph validation and renderer);
`tests/hazards/refusal_allowlist.json` and `tests/hazards/refusal_census.py`
(refusal inventory, if the chain change changes its census);
`tests/test_battery_float_sweep.py` (READERS classification, if new code names a
bound lexeme). The import-fence lists are inspected, and extended only if the new
entry requires it. No estimator, calibration implementation, reader or registered
BYTES config is edited. A separate prepare writer in the new stage module avoids
changing the claim-only assumptions of `joulewise/b5/plan.py`.

Planned artifacts: `configs/campaigns/bytes_stream_test/` owns the fixed non-claim
plan tree, generator, telemetry-only config, README and genesis pin;
`scripts/bytes_stream_harvest.py` produces INPUT.json from an immutable archive;
`tests/test_bytes_stream_capture.py` and `tests/test_bytes_stream_harvest.py`
exercise the new paths. The existing probe is imported without changing its
scan/read functions.

Rule-derived numbers (no new acceptance threshold):
- §1: “run the probe at --bytes 2^k for k = 14 to 35 ... three calls per size,
  repeats chosen so each call lasts about 2 s”. Preserve planning pilots and the
  three scan calls separately; stop on allocation failure, never retry acceptance.
- §1: “N = floor(T_call / t_dispatch)”, S “2 × 500 s”, cache arms “2 × 250 s”.
- §2: “--idle-s 57.6” and “Settle gap 3 s”; these are passed literally to stream.
- §1: planned measured time is 3573.6 s (2500 + 16×57.6 + 24×3 + 8×10).
  Scan planning is 22×3×2 s plus measured planning/allocation overhead. Runtime
  allowances must record their terms, including the existing calibration-tool
  allowances, rather than introduce a hidden timeout.

Decisions I made: retain the existing bookend calibration lifecycle; use fresh
non-claim roots named runs_bytes_stream_test and runs_bytes_stream_test_bound;
keep the continuous scan capture but never use its energy to select sizes/counts;
retain native idle rows without trimming; retain missing prerequisites as null
with archive diagnostics so the unchanged reader gives a reasoned result.
The reader owns every classification and any τ-based idle trimming.

Mac lifecycle and exact commands, field-source map, executed evidence and final
CI states will be completed below after implementation and verification.
