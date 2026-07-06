"""Deterministic mock telemetry adapter (decisions D-002, D-018, D-019).

Power is piecewise-constant per lifecycle stage (idle 5.0 W, warmup 6.0 W,
measured 7.5 W) so the reducer's trapezoidal integration has a closed-form
expectation (D-019). ``WARMUP_POWER_W`` is declared for trace-extension use;
sampling only covers the measured window. All timestamps come from the
injected :class:`joulewise.clock.Clock`. Where real backends spawn a
file-writing sampler subprocess (D-002), the mock simply synthesizes samples
between ``start_sampling`` and ``stop_sampling``. The rail manifest in
``device_metadata`` names exactly the rails that sum to the backend's
canonical ``power_w`` (D-018): the single rail ``mock``.

Fault-injection conventions (internal convention per the Phase 2 plan, Slice
2B; revisit if configs need first-class fault injection):

- ``hardware_target.notes == "telemetry-denied"`` makes
  :meth:`MockTelemetryAdapter.start_sampling` return a structured
  ``permission_denied`` failure, so the controller's ``FailureReason ->
  RunStatus`` mapping (D-012, status ``failed``) can be tested end-to-end.
- The companion runtime convention (``model.name == "mock-unsupported"`` =>
  ``did_not_fit``) is documented in :mod:`joulewise.adapters.mock_runtime`.
"""

from __future__ import annotations

import json

from joulewise.bundle import write_raw_artifact
from joulewise.clock import Clock
from joulewise.interfaces import AdapterResult, PowerSample, RunContext, ThermalState
from joulewise.schemas import BenchmarkConfig, FailureReason, IdleBaseline, TelemetryBackend

#: hardware_target.notes value that triggers the permission_denied fault
#: injection (see module docstring).
TELEMETRY_DENIED_NOTE = "telemetry-denied"

#: Piecewise-constant power levels per lifecycle stage (D-019).
IDLE_POWER_W = 5.0
WARMUP_POWER_W = 6.0
MEASURED_POWER_W = 7.5

#: The single mock rail; sums to the canonical power_w by itself (D-018).
RAIL_NAME = "mock"

#: Raw-evidence file the mock writes under ``RunContext.raw_dir`` (D-002/D-024):
#: the mock analogue of a real sampler's native output (e.g. the powermetrics
#: plist), preserved verbatim so the raw-evidence seam is exercised on every
#: mock run.
RAW_SAMPLES_NAME = "mock_samples.json"


class MockTelemetryAdapter:
    """Deterministic, clock-driven implementation of ``TelemetryAdapter``."""

    name = "mock"

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._sampling_start_s: float | None = None

    def device_metadata(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> dict:
        return {
            "device": config.hardware_target.id,
            "telemetry": "mock",
            "rail_manifest": [RAIL_NAME],
        }

    def measure_idle(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> IdleBaseline:
        duration_s = config.sampling.idle_seconds
        self._clock.sleep(duration_s)
        return IdleBaseline(
            power_w_mean=IDLE_POWER_W,
            power_w_stddev=0.0,
            duration_s=duration_s,
            sample_count=max(2, int(duration_s * config.sampling.power_hz)),
            telemetry_backend=TelemetryBackend.MOCK,
        )

    def start_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> AdapterResult:
        if config.hardware_target.notes == TELEMETRY_DENIED_NOTE:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.PERMISSION_DENIED,
                message=(
                    "mock fault injection: hardware_target.notes == "
                    "'telemetry-denied' simulates a telemetry permission "
                    "failure (permission_denied); internal convention "
                    "documented in joulewise.adapters.mock_telemetry"
                ),
            )
        start = self._clock.now()
        self._sampling_start_s = start
        return AdapterResult(ok=True, metadata={"start_timestamp_s": start})

    def stop_sampling(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> list[PowerSample]:
        if self._sampling_start_s is None:
            return []
        start = self._sampling_start_s
        self._sampling_start_s = None
        end = self._clock.now()

        samples: list[PowerSample] = []
        k = 0
        while True:
            timestamp_s = start + k / config.sampling.power_hz
            if timestamp_s >= end:
                break
            samples.append(self._sample(timestamp_s))
            k += 1
        # A final sample at exactly t = end guarantees >= 2 samples for any
        # nonzero window, keeping trapezoidal integration well-defined.
        samples.append(self._sample(end))
        # D-002 via D-024: preserve the sampler's native output verbatim under
        # raw/, through the validated no-overwrite helper (adapters must not
        # write raw/ paths directly). Out-of-run invocations (context None,
        # e.g. the cooldown gate) produce no raw output.
        if context is not None:
            write_raw_artifact(
                context,
                RAW_SAMPLES_NAME,
                json.dumps(
                    [
                        {
                            "timestamp_s": sample.timestamp_s,
                            "power_w": sample.power_w,
                            "source": sample.source,
                            "rail": sample.rail,
                        }
                        for sample in samples
                    ],
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
            )
        return samples

    def thermal_state(
        self, config: BenchmarkConfig, context: RunContext | None = None
    ) -> ThermalState:
        return ThermalState(
            timestamp_s=self._clock.now(),
            temperature_c=42.0,
            thermal_pressure="nominal",
        )

    @staticmethod
    def _sample(timestamp_s: float) -> PowerSample:
        return PowerSample(
            timestamp_s=timestamp_s,
            power_w=MEASURED_POWER_W,
            source="mock",
            rail=RAIL_NAME,
        )
