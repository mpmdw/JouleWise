"""Runtime-external controls, separate processes, no shell/weight loader/network.

The trusted caller supplies a spawn-picklable decoder factory. It must prepare
the frozen local model without fetching. Receipts never enter visible usage.
Work counts are exact; energy is unknown until a separate meter record is joined.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import multiprocessing
import re
import time
from typing import Any, Callable, Sequence

from .config import CONTROL_SCHEMA, seal
from .control import HiddenDecode


def cpu_work(units: int, seed: int) -> str:
    """One unit is one specified uint64 recurrence update, not a token or FLOP."""
    state = seed & ((1 << 64) - 1)
    for _ in range(units):
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
    return f"{state:016x}"


def _worker(connection: Any, config: dict[str, Any], factory: Any) -> None:
    work, control = None, None
    try:
        if config["kind"] == "side_generation":
            # Sham also prepares the model: no positive-only model-load cost.
            decoder = factory(config["seed"])
            control = HiddenDecode(seal({"schema": CONTROL_SCHEMA, "status": "DRAFT",
                "id": "external-side", "revision": 1, "decode_tokens": config["units"],
                "prompt_token_ids": config["prompt_token_ids"], "before_chat_call": 0,
                "max_context_tokens": config["max_context_tokens"]}), decoder,
                clock_domain="host-monotonic")
            control.execute()
            work = control.receipt()
        else:
            start = time.monotonic_ns()
            checksum = cpu_work(config["units"], config["seed"])
            work = {"status": "completed", "start_ns": start, "end_ns": time.monotonic_ns(),
                    "completed_work_units": config["units"], "work_unit": "uint64_lcg_update_v1",
                    "checksum": checksum, "H": 0, "completed_tokens": 0,
                    "prefill_tokens": 0, "output_token_ids": []}
        connection.send({"ok": True, "work": work})
    except BaseException as exc:
        connection.send({"ok": False, "work": control.receipt() if control else work,
                         "error_type": type(exc).__name__})
    finally:
        connection.close()


class ExternalWork:
    """Single-use, bounded, synchronous injection with mandatory child cleanup.

    before_chat runs before the selected visible request; tool runs before an
    existing task tool's implementation. Neither adds tools or grants the agent
    a subprocess capability. Timeout/load/partial failures never certify a dose.
    """

    def __init__(self, *, kind: str, units: int, seed: int, worker_identity: str,
                 decoder_factory: Callable | None = None,
                 prompt_token_ids: Sequence[int] = (1,), max_context_tokens: int = 4096,
                 placement: str = "before_chat", trigger_index: int = 0,
                 timeout_s: float = 30) -> None:
        if kind not in {"side_generation", "tool_cpu"} or placement not in {"before_chat", "tool"}:
            raise ValueError("unknown work kind or placement")
        if type(units) is not int or not 0 <= units <= (4096 if kind == "side_generation" else 10_000_000):
            raise ValueError("invalid work dose")
        if type(seed) is not int or not 0 <= seed < 2**64:
            raise ValueError("worker seed must be a uint64")
        if (type(trigger_index) is not int or not 0 <= trigger_index <= 127
                or not isinstance(worker_identity, str) or not worker_identity):
            raise ValueError("explicit worker identity and bounded trigger required")
        if (type(timeout_s) not in (int, float) or not 0 < timeout_s <= 3600):
            raise ValueError("finite child timeout in (0, 3600] required")
        ids = list(prompt_token_ids)
        if (not ids or any(type(t) is not int or t < 0 for t in ids)
                or type(max_context_tokens) is not int or not 1 <= max_context_tokens <= 40960
                or (kind == "side_generation" and len(ids) + max(0, units - 1) > max_context_tokens)):
            raise ValueError("invalid prompt or hidden context budget")
        factory_id = None
        if kind == "side_generation":
            if not callable(decoder_factory):
                raise ValueError("side generation requires a trusted decoder factory")
            factory_id = f"{decoder_factory.__module__}:{decoder_factory.__qualname__}"
            if "<locals>" in factory_id or "<lambda>" in factory_id:
                raise ValueError("decoder factory must be a module-level spawn-picklable callable")
        elif decoder_factory is not None:
            raise ValueError("CPU work has no decoder")
        self._config = seal({"schema": "joulewise.align.squeeze.external_work.v1",
            "kind": kind, "units": units, "seed": seed, "worker_identity": worker_identity,
            "decoder_factory": factory_id, "prompt_token_ids": ids,
            "max_context_tokens": max_context_tokens, "placement": placement,
            "trigger_index": trigger_index, "timeout_s": timeout_s})
        self._factory = decoder_factory
        self._receipt = {"schema": "joulewise.align.squeeze.external_truth.v1",
            "audience": "evaluator_only", "status": "not_triggered", "control": self.config,
            "clock_domain": "host-monotonic", "start_ns": None, "end_ns": None,
            "worker_pid": None, "work": None, "H": None, "energy_j": None,
            "unknown_work_on_failure": False}

    @property
    def config(self) -> dict[str, Any]:
        return deepcopy(self._config)

    @property
    def identity(self) -> str:
        return self._config["worker_identity"] + "/" + self._config["config_sha256"]

    @property
    def trigger_index(self) -> int:
        return self._config["trigger_index"]

    @property
    def placement(self) -> str:
        return self._config["placement"]

    def receipt(self) -> dict[str, Any]:
        return deepcopy(self._receipt)

    def execute(self) -> None:
        receipt = self._receipt
        if receipt["status"] != "not_triggered":
            raise RuntimeError("external work is single-use")
        receipt.update(status="running", start_ns=time.monotonic_ns())
        context = multiprocessing.get_context("spawn")  # no visible model/cache/RNG inherited
        reader, writer = context.Pipe(duplex=False)
        process = context.Process(target=_worker, args=(writer, self.config, self._factory))
        process.daemon = True
        try:
            process.start()
            receipt["worker_pid"] = process.pid
            writer.close()
            if not reader.poll(self._config["timeout_s"]):
                raise RuntimeError("external worker deadline exceeded")
            message = reader.recv()
            receipt["work"] = message["work"]
            process.join(timeout=1)
            if process.is_alive() or process.exitcode != 0 or not message["ok"]:
                raise RuntimeError("external worker failed: " + message.get("error_type", "exit/cleanup"))
            receipt.update(status="completed", H=message["work"]["H"])
        except BaseException as exc:
            receipt.update(status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                           unknown_work_on_failure=True, H=None, error_type=type(exc).__name__)
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise RuntimeError("external work not certified") from exc
        finally:
            if process.pid is not None:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=1)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1)
                if process.is_alive():
                    receipt.update(status="failed", H=None, unknown_work_on_failure=True)
                    raise RuntimeError("external worker cleanup failed")
                process.close()
            reader.close()
            writer.close()
            receipt["end_ns"] = time.monotonic_ns()


def account_meter(samples: Sequence[tuple[int, str]], *, start_ns: int, end_ns: int,
                  clock_domain: str, source: str, source_sha256: str,
                  uncertainty_j: str, max_gap_ns: int | None = None) -> dict[str, Any]:
    """Exact rational trapezoid arithmetic on explicitly supplied decimal watts.

    This is an integral of the whole host over the requested span, not causal
    hidden-work energy. Physical accuracy is limited by the meter, alignment,
    coverage and uncertainty. No interpolation/extrapolation across missing data
    is authorized beyond the caller's frozen max_gap_ns for measured samples.
    """
    if (type(start_ns) is not int or type(end_ns) is not int or not 0 <= start_ns < end_ns
            or not isinstance(clock_domain, str) or not clock_domain
            or source not in {"synthetic", "km003c"}
            or not isinstance(source_sha256, str) or re.fullmatch(r"[a-f0-9]{64}", source_sha256) is None):
        raise ValueError("valid span, domain and explicit source binding required")
    try:
        uncertainty = Fraction(uncertainty_j)
        points = [(t, Fraction(p)) for t, p in samples]
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("finite decimal power and uncertainty required") from exc
    if uncertainty < 0 or len(points) < 2 or any(type(t) is not int or t < 0 or p < 0 for t, p in points):
        raise ValueError("invalid power samples/uncertainty")
    if source == "km003c" and (uncertainty <= 0 or type(max_gap_ns) is not int or max_gap_ns <= 0):
        raise ValueError("measured DC requires positive uncertainty and frozen coverage gap")
    if max_gap_ns is not None and (type(max_gap_ns) is not int or max_gap_ns <= 0):
        raise ValueError("coverage gap must be a positive integer")
    if points[0][0] > start_ns or points[-1][0] < end_ns:
        raise ValueError("samples do not bracket the full span")
    energy = Fraction(0)
    for (t0, p0), (t1, p1) in zip(points, points[1:]):
        if t1 <= t0:
            raise ValueError("sample times must increase strictly")
        a, b = max(start_ns, t0), min(end_ns, t1)
        if a >= b:
            continue
        if max_gap_ns is not None and t1 - t0 > max_gap_ns:
            raise ValueError("meter coverage gap exceeds frozen limit")
        pa = p0 + (p1 - p0) * Fraction(a - t0, t1 - t0)
        pb = p0 + (p1 - p0) * Fraction(b - t0, t1 - t0)
        energy += (pa + pb) * Fraction(b - a, 2_000_000_000)
    return {"schema": "joulewise.align.squeeze.dc_integral.v1", "source": source,
            "channel": "km003c:dc_in", "source_sha256": source_sha256,
            "clock_domain": clock_domain, "start_ns": start_ns, "end_ns": end_ns,
            "dc_in_j": str(energy), "uncertainty_j": str(uncertainty),
            "uncertainty_kind": "additive_bound",
            "hidden_increment_j": None, "max_gap_ns": max_gap_ns}


def join_control_meter(receipt: dict[str, Any], meter: dict[str, Any], *,
                       transcript_sha256: str, v4_configuration_sha256: str) -> dict[str, Any]:
    """Evaluator-only join; verify containment, retain unknown/failed doses.

    This consumes already aligned meter arithmetic, not paths or raw files.
    Neither an integral nor the child's exact token receipt isolates hidden J.
    """
    for digest in (transcript_sha256, v4_configuration_sha256):
        if not isinstance(digest, str) or re.fullmatch(r"[a-f0-9]{64}", digest) is None:
            raise ValueError("transcript and v4 configuration digests required")
    if (receipt.get("schema") != "joulewise.align.squeeze.external_truth.v1"
            or meter.get("schema") != "joulewise.align.squeeze.dc_integral.v1"
            or receipt["clock_domain"] != meter["clock_domain"]
            or type(receipt["start_ns"]) is not int or type(receipt["end_ns"]) is not int
            or not meter["start_ns"] <= receipt["start_ns"] <= receipt["end_ns"] <= meter["end_ns"]):
        raise ValueError("aligned whole-member DC span must contain the full child lifecycle")
    return {"schema": "joulewise.align.squeeze.external_accounting.v1", "audience": "evaluator_only",
            "control": deepcopy(receipt), "meter": deepcopy(meter),
            "transcript_sha256": transcript_sha256, "v4_configuration_sha256": v4_configuration_sha256,
            "dose_certified": receipt["status"] == "completed" and not receipt["unknown_work_on_failure"],
            "hidden_energy_j": None}


def paired_increment(dose: dict[str, Any], sham: dict[str, Any]) -> dict[str, Any]:
    """Exact difference of matched DC integrals, with summed additive bounds.

    The observed difference includes startup, prefill, idle and noise. It is not
    exact causal hidden-work energy, and it is never a joule/token conversion.
    """
    if (not dose["dose_certified"] or not sham["dose_certified"]
            or dose["transcript_sha256"] != sham["transcript_sha256"]
            or dose["v4_configuration_sha256"] != sham["v4_configuration_sha256"]
            or dose["control"]["control"]["units"] <= 0 or sham["control"]["control"]["units"] != 0):
        raise ValueError("complete positive dose and matched sham with identical visible work required")
    config = lambda row: {k: v for k, v in row["control"]["control"].items() if k not in {"units", "config_sha256"}}
    if (config(dose) != config(sham) or dose["meter"]["source"] != sham["meter"]["source"]
            or any(row["meter"]["uncertainty_kind"] != "additive_bound" for row in (dose, sham))):
        raise ValueError("worker recipe and measurement kind must match")
    return {"schema": "joulewise.align.squeeze.paired_increment.v1", "audience": "evaluator_only",
            "source": dose["meter"]["source"],
            "observed_dc_difference_j": str(Fraction(dose["meter"]["dc_in_j"]) - Fraction(sham["meter"]["dc_in_j"])),
            "additive_bound_j": str(Fraction(dose["meter"]["uncertainty_j"]) + Fraction(sham["meter"]["uncertainty_j"])),
            "hidden_energy_j": None}
