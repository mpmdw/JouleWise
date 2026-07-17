from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "axi_sb_static_batch_spike.py"
SPEC = importlib.util.spec_from_file_location("axi_sb_static_batch_spike", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
spike = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = spike
SPEC.loader.exec_module(spike)


def request_row(request_id: str, runtime_uid: int) -> dict[str, object]:
    return {
        "request_id": request_id,
        "runtime_uid": runtime_uid,
        "output_token_count": 2,
        "output_token_ids": [10, 11],
        "token_timestamps_s": [1.0, 2.0],
        "stop_reason": "length",
        "terminal_timestamp_s": 2.0,
        "phase_hooks": {
            "prefill_started": True,
            "prefill_ended": True,
            "decode_started": True,
            "decode_ended": True,
        },
    }


def supported_observation() -> dict[str, object]:
    return {
        "runtime_available": True,
        "requested_batch_size": 2,
        "configured_batch_size": 2,
        "realized_batch_size": 2,
        "insert_call_count": 1,
        "runtime_uids": [0, 1],
        "model_calls": [{"batch_dimension": 2}],
        "observed_hooks": sorted(spike.REQUIRED_HOOKS | {"prompt_response"}),
        "requests": [request_row("axi-sb-000", 0), request_row("axi-sb-001", 1)],
    }


def supported_evidence_rows() -> list[dict[str, object]]:
    observation = supported_observation()
    rows: list[dict[str, object]] = [
        {"event": "batch_observation", **observation}
    ]
    for request in observation["requests"]:
        identity = {
            "request_id": request["request_id"],
            "runtime_uid": request["runtime_uid"],
        }
        rows.extend(
            [
                {"event": "request_submitted", **identity},
                {"event": "request_admitted", **identity},
                {"event": "generation_response", **identity},
                {"event": "request_terminal", **request},
            ]
        )
    rows.append(
        {
            "event": "probe_outcome",
            "verdict": "supported",
            "reason": None,
            "stage": "complete",
        }
    )
    return rows


def controller_rows(
    worker_rows: list[dict[str, object]], requested_batch_size: int
) -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory() as temporary:
        model = Path(temporary)
        (model / "config.json").write_text("{}\n", encoding="utf-8")
        args = SimpleNamespace(
            model=str(model),
            batch_size=requested_batch_size,
            max_tokens=2,
            timeout_seconds=1.0,
        )
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="\n".join(json.dumps(row) for row in worker_rows) + "\n",
            stderr="",
        )
        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
        stream = io.StringIO()
        with patch.object(
            spike,
            "_distribution_record",
            side_effect=lambda name: {
                "name": name,
                "version": versions[name],
                "package_root": f"/fake/{name}",
            },
        ), patch.object(spike.subprocess, "run", return_value=completed):
            spike.controller(args, spike.Emitter(stream))
    return [json.loads(line) for line in stream.getvalue().splitlines()]


class StaticBatchSpikeTests(unittest.TestCase):
    def test_import_is_mlx_free(self) -> None:
        self.assertNotIn("mlx", spike.__dict__)
        self.assertNotIn("mlx_lm", spike.__dict__)

    def test_supported_requires_true_batch_and_full_observability(self) -> None:
        self.assertEqual(
            spike.classify_observation(supported_observation()),
            {"verdict": "supported", "reason": None},
        )

    def test_singleton_loop_is_not_native_batch_execution(self) -> None:
        observation = supported_observation()
        observation["insert_call_count"] = 2
        observation["model_calls"] = [
            {"batch_dimension": 1},
            {"batch_dimension": 1},
        ]
        self.assertEqual(
            spike.classify_observation(observation),
            {
                "verdict": "unsupported_for_joulewise",
                "reason": "native_batch_execution",
            },
        )

    def test_missing_request_timestamp_is_event_observability_failure(self) -> None:
        observation = supported_observation()
        observation["requests"][0]["token_timestamps_s"] = [1.0]
        self.assertEqual(
            spike.classify_observation(observation),
            {
                "verdict": "unsupported_for_joulewise",
                "reason": "event_observability",
            },
        )

    def test_missing_per_request_phase_hooks_is_event_observability_failure(self) -> None:
        observation = supported_observation()
        observation["requests"][1]["phase_hooks"] = {}
        self.assertEqual(
            spike.classify_observation(observation),
            {
                "verdict": "unsupported_for_joulewise",
                "reason": "event_observability",
            },
        )

    def test_runtime_unavailable_is_preserved(self) -> None:
        self.assertEqual(
            spike.classify_observation(
                {
                    "runtime_available": False,
                    "runtime_unavailable_reason": "metal_unavailable",
                }
            ),
            {"verdict": "runtime_unavailable", "reason": "metal_unavailable"},
        )

    def test_worker_parser_separates_non_json_output(self) -> None:
        rows, malformed = spike.parse_worker_lines(
            '{"event":"metal_probe","metal_available":true}\nwarning text\n'
        )
        self.assertEqual(rows, [{"event": "metal_probe", "metal_available": True}])
        self.assertEqual(malformed, ["warning text"])

    def test_pin_mismatch_is_structured_jsonl(self) -> None:
        stream = io.StringIO()
        emitter = spike.Emitter(stream)
        args = SimpleNamespace(
            model=spike.DEFAULT_MODEL,
            batch_size=2,
            max_tokens=2,
            timeout_seconds=1.0,
        )
        with patch.object(
            spike,
            "_distribution_record",
            side_effect=lambda name: {"name": name, "version": None, "package_root": None},
        ):
            self.assertEqual(spike.controller(args, emitter), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertTrue(all(row["schema"] == spike.SCHEMA for row in rows))
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "pin_mismatch")

    def test_missing_model_is_structured_runtime_unavailable(self) -> None:
        stream = io.StringIO()
        args = SimpleNamespace(
            model="/definitely/missing/axi-sb-model",
            batch_size=2,
            max_tokens=2,
            timeout_seconds=1.0,
        )
        versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
        with patch.object(
            spike,
            "_distribution_record",
            side_effect=lambda name: {
                "name": name,
                "version": versions[name],
                "package_root": f"/fake/{name}",
            },
        ), patch.object(spike.subprocess, "run") as run:
            self.assertEqual(spike.controller(args, spike.Emitter(stream)), 0)
        run.assert_not_called()
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "model_artifact_missing")

    def test_worker_timeout_is_structured_runtime_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            model = Path(temporary)
            (model / "config.json").write_text("{}\n", encoding="utf-8")
            args = SimpleNamespace(
                model=str(model),
                batch_size=2,
                max_tokens=2,
                timeout_seconds=1.0,
            )
            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
            stream = io.StringIO()
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(
                spike.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired([], 1.0, output=b"partial"),
            ):
                self.assertEqual(spike.controller(args, spike.Emitter(stream)), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "probe_timeout")

    def test_controller_rejects_supported_without_batch_observation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            model = Path(temporary)
            (model / "config.json").write_text("{}\n", encoding="utf-8")
            args = SimpleNamespace(
                model=str(model),
                batch_size=2,
                max_tokens=2,
                timeout_seconds=1.0,
            )
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=(
                    '{"event":"metal_probe","metal_available":true}\n'
                    '{"event":"probe_outcome","verdict":"supported",'
                    '"reason":null,"stage":"complete"}\n'
                ),
                stderr="",
            )
            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
            stream = io.StringIO()
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(spike.subprocess, "run", return_value=completed):
                self.assertEqual(spike.controller(args, spike.Emitter(stream)), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["event"], "probe_outcome")
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "native_batch_execution")
        self.assertTrue(rows[-1]["evidence_verdict_mismatch"])
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_controller_rejects_terminal_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            model = Path(temporary)
            (model / "config.json").write_text("{}\n", encoding="utf-8")
            args = SimpleNamespace(
                model=str(model),
                batch_size=2,
                max_tokens=2,
                timeout_seconds=1.0,
            )
            observation = {"event": "batch_observation", **supported_observation()}
            terminal = {"event": "request_terminal", **request_row("axi-sb-000", 0)}
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="\n".join(
                    [
                        json.dumps(observation),
                        json.dumps(terminal),
                        json.dumps(
                            {
                                "event": "probe_outcome",
                                "verdict": "supported",
                                "reason": None,
                                "stage": "complete",
                            }
                        ),
                    ]
                )
                + "\n",
                stderr="",
            )
            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
            stream = io.StringIO()
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(spike.subprocess, "run", return_value=completed):
                self.assertEqual(spike.controller(args, spike.Emitter(stream)), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        self.assertTrue(rows[-1]["evidence_verdict_mismatch"])
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_controller_rejects_evidence_for_different_requested_batch_size(self) -> None:
        rows = controller_rows(supported_evidence_rows(), requested_batch_size=4)
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "evidence_verdict_mismatch")
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_controller_rejects_duplicate_terminal_runtime_uids(self) -> None:
        worker_rows = supported_evidence_rows()
        terminals = [row for row in worker_rows if row["event"] == "request_terminal"]
        terminals[1]["runtime_uid"] = terminals[0]["runtime_uid"]
        rows = controller_rows(worker_rows, requested_batch_size=2)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_controller_rejects_terminals_without_lifecycle_rows(self) -> None:
        worker_rows = [
            row
            for row in supported_evidence_rows()
            if row["event"] not in {"request_submitted", "request_admitted"}
        ]
        rows = controller_rows(worker_rows, requested_batch_size=2)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_true_batch_with_response_missing_uid_is_event_observability(self) -> None:
        class FakeTokenizer:
            eos_token_id = 0

            def encode(self, _prompt: str, **_kwargs: object) -> list[int]:
                return [1]

        def fake_model(_inputs: object, *_args: object, **_kwargs: object) -> None:
            return None

        class FakeBatchGenerator:
            def __init__(self, model: object, **_kwargs: object) -> None:
                self.model = model

            def insert(self, _prompts: object, _limits: object) -> list[int]:
                return [0, 1]

            def next(self) -> tuple[list[object], list[object]]:
                self.model(SimpleNamespace(shape=(2, 1)))
                return [SimpleNamespace(progress=(1, 1), end_of_prompt=True)], []

        mlx = ModuleType("mlx")
        mlx.__path__ = []  # type: ignore[attr-defined]
        mlx_core = ModuleType("mlx.core")
        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
        mlx_core.get_peak_memory = lambda: 1  # type: ignore[attr-defined]
        mlx.core = mlx_core  # type: ignore[attr-defined]
        mlx_lm = ModuleType("mlx_lm")
        mlx_lm.__path__ = []  # type: ignore[attr-defined]
        mlx_lm.load = lambda _model: (fake_model, FakeTokenizer())  # type: ignore[attr-defined]
        mlx_lm_generate = ModuleType("mlx_lm.generate")
        mlx_lm_generate.BatchGenerator = FakeBatchGenerator  # type: ignore[attr-defined]
        mlx_lm.generate = mlx_lm_generate  # type: ignore[attr-defined]

        stream = io.StringIO()
        modules = {
            "mlx": mlx,
            "mlx.core": mlx_core,
            "mlx_lm": mlx_lm,
            "mlx_lm.generate": mlx_lm_generate,
        }
        args = SimpleNamespace(model="/fake/model", batch_size=2, max_tokens=2)
        with patch.dict(sys.modules, modules), patch.object(sys, "stdout", stream):
            self.assertEqual(spike.runtime_worker(args), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        batch = next(row for row in rows if row["event"] == "batch_observation")
        self.assertEqual(batch["model_calls"][0]["batch_dimension"], 2)

    def test_worker_protocol_failure_degrades_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            model = Path(temporary)
            (model / "config.json").write_text("{}\n", encoding="utf-8")
            args = SimpleNamespace(
                model=str(model),
                batch_size=2,
                max_tokens=2,
                timeout_seconds=1.0,
            )
            completed = subprocess.CompletedProcess(
                args=[], returncode=1, stdout="traceback", stderr="boom"
            )
            versions = {"mlx-lm": spike.EXPECTED_MLX_LM, "mlx": spike.EXPECTED_MLX}
            stream = io.StringIO()
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(spike.subprocess, "run", return_value=completed):
                self.assertEqual(spike.controller(args, spike.Emitter(stream)), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "worker_protocol_failure")

    def test_invalid_probe_configuration_is_json(self) -> None:
        stream = io.StringIO()
        with patch.object(sys, "stdout", stream):
            self.assertEqual(spike.main(["--batch-size", "1"]), 2)
        row = json.loads(stream.getvalue())
        self.assertEqual(row["event"], "probe_outcome")
        self.assertEqual(row["reason"], "invalid_probe_configuration")


if __name__ == "__main__":
    unittest.main()
