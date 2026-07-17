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
SCRIPT = ROOT / "scripts" / "axi_sc_spec_decode_spike.py"
SPEC = importlib.util.spec_from_file_location("axi_sc_spec_decode_spike", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
spike = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = spike
SPEC.loader.exec_module(spike)


def source_surface() -> dict[str, object]:
    return {
        "available": True,
        "reason": None,
        "generate_path": "/fake/mlx_lm/generate.py",
        "generate_sha256": spike.EXPECTED_GENERATE_SHA256,
        "generate_sha256_expected": spike.EXPECTED_GENERATE_SHA256,
        "qwen3_5_path": "/fake/mlx_lm/models/qwen3_5.py",
        "qwen3_5_sha256": spike.EXPECTED_QWEN35_SHA256,
        "qwen3_5_sha256_expected": spike.EXPECTED_QWEN35_SHA256,
        "external_draft_generation_surface": True,
        "accepted_token_marker_surface": True,
        "tokens_proposed_callback_surface": False,
        "decode_emission_callback_surface": False,
        "native_mtp_generation_surface": False,
        "qwen35_mtp_weights_discarded": True,
    }


def requested(
    mode: str = "draft_model",
    target: str = "/models/target",
    draft: str | None = "/models/draft",
    max_proposed_tokens: int = 3,
) -> dict[str, object]:
    args = SimpleNamespace(
        mode=mode,
        target_model=target,
        draft_model=draft,
        max_proposed_tokens=max_proposed_tokens,
        max_tokens=4,
        prompt=spike.DEFAULT_PROMPT,
    )
    return spike._requested_parameters(args)


def draft_identity(req: dict[str, object], artifact_sha: str) -> dict[str, object]:
    return {
        "model_name": Path(str(req["draft_model_path"])).name,
        "model_revision": f"local-artifact-sha256:{artifact_sha}",
        "model_artifact_sha256": artifact_sha,
        "weight_format": "safetensors",
        "quantization": '{"bits":4,"group_size":64}',
        "runtime_backend": "mlx-lm",
        "runtime_version": spike.EXPECTED_MLX_LM,
        "tokenizer": {
            "name": "test-tokenizer",
            "revision": "local-config-sha256:" + "c" * 64,
            "class": "FakeTokenizer",
            "vocabulary_size": 100,
        },
    }


def draft_evidence_rows(
    req: dict[str, object],
    artifact_sha: str,
    *,
    child_verdict: str = "unsupported_for_joulewise",
    child_reason: str | None = "event_observability",
) -> list[dict[str, object]]:
    token_ids = [10, 11]
    output_hash = spike.output_ids_sha256(token_ids)
    common = dict(req)
    rows: list[dict[str, object]] = [
        {
            "event": "model_loaded",
            **common,
            "role": "target",
            "resolved_path": req["target_model_path"],
        },
        {
            "event": "model_loaded",
            **common,
            "role": "draft",
            "resolved_path": req["draft_model_path"],
        },
        {"event": "request_submitted", **common, "timestamp_s": 1.0},
        {"event": "request_admitted", **common, "timestamp_s": 1.1},
        {
            "event": "generation_response",
            **common,
            "output_token_ordinal": 0,
            "token_id": 10,
            "from_draft": True,
            "finish_reason": None,
            "timestamp_s": 2.0,
        },
        {
            "event": "generation_response",
            **common,
            "output_token_ordinal": 1,
            "token_id": 11,
            "from_draft": False,
            "finish_reason": "length",
            "timestamp_s": 3.0,
        },
        {
            "event": "request_terminal",
            **common,
            "output_token_ids": token_ids,
            "output_token_count": 2,
            "output_token_ids_sha256": output_hash,
            "stop_reason": "length",
            "terminal_timestamp_s": 3.0,
        },
        {
            "event": "capability_observation",
            **common,
            "runtime_available": True,
            "runtime_generation_supported": True,
            "generation_completed": True,
            "loaded_target_model_path": req["target_model_path"],
            "loaded_draft_model_path": req["draft_model_path"],
            "target_model_call_count": 3,
            "draft_model_call_count": 4,
            "draft_model_identity": draft_identity(req, artifact_sha),
            "native_mtp_identity": None,
            "output_token_ids": token_ids,
            "output_token_count": 2,
            "output_token_ids_sha256": output_hash,
            "tokens_proposed": None,
            "tokens_proposed_observation_source": None,
            "tokens_accepted": 1,
            "tokens_accepted_observation_source": "GenerationResponse.from_draft",
            "acceptance_rate": None,
            "acceptance_rate_reason": "tokens_proposed_unavailable",
            "decode_emission_event_count": 0,
            "decode_emission_observation_source": None,
        },
        {
            "event": "probe_outcome",
            "verdict": child_verdict,
            "reason": child_reason,
            "stage": "complete",
        },
    ]
    return rows


def native_evidence_rows(req: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "event": "capability_observation",
            **req,
            "runtime_available": True,
            "runtime_generation_supported": False,
            "native_mtp_execution_observed": False,
            "generation_completed": False,
            "loaded_target_model_path": None,
            "loaded_draft_model_path": None,
            "target_model_call_count": 0,
            "draft_model_call_count": 0,
            "draft_model_identity": None,
            "native_mtp_identity": None,
            "tokens_proposed": None,
            "tokens_accepted": None,
            "acceptance_rate": None,
            "decode_emission_event_count": 0,
        },
        {
            "event": "probe_outcome",
            "verdict": "unsupported_for_joulewise",
            "reason": "native_mtp_generation",
            "stage": "runtime_surface",
        },
    ]


def _write_artifact(root: Path, name: str) -> Path:
    path = root / name
    path.mkdir()
    (path / "config.json").write_text(
        json.dumps(
            {
                "model_type": "qwen2",
                "vocab_size": 100,
                "quantization": {"bits": 4, "group_size": 64},
            }
        ),
        encoding="utf-8",
    )
    (path / "model.safetensors").write_bytes(name.encode("utf-8"))
    return path


def controller_rows(
    worker_builder,
    *,
    max_proposed_tokens: int = 3,
) -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        target = _write_artifact(root, "target")
        draft = _write_artifact(root, "draft")
        args = SimpleNamespace(
            mode="draft_model",
            target_model=str(target),
            draft_model=str(draft),
            max_proposed_tokens=max_proposed_tokens,
            max_tokens=4,
            timeout_seconds=1.0,
            prompt=spike.DEFAULT_PROMPT,
        )
        req = spike._requested_parameters(args)
        artifact_sha, _ = spike._folded_model_artifact_sha256(draft)
        assert artifact_sha is not None
        worker_rows = worker_builder(req, artifact_sha)
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
        ), patch.object(
            spike, "_source_surface_record", return_value=source_surface()
        ), patch.object(spike.subprocess, "run", return_value=completed):
            spike.controller(args, spike.Emitter(stream))
    return [json.loads(line) for line in stream.getvalue().splitlines()]


class SpecDecodeSpikeTests(unittest.TestCase):
    def test_import_is_mlx_free(self) -> None:
        self.assertNotIn("mlx", spike.__dict__)
        self.assertNotIn("mlx_lm", spike.__dict__)

    def test_external_draft_generation_without_proposals_fails_observability(self) -> None:
        req = requested()
        artifact_sha = "d" * 64
        result = spike.derive_evidence_verdict(
            draft_evidence_rows(req, artifact_sha), req, artifact_sha
        )
        self.assertEqual(result["verdict"], "unsupported_for_joulewise")
        self.assertEqual(result["reason"], "event_observability")
        self.assertTrue(result["runtime_generation_supported"])
        self.assertFalse(result["claim_instrumentable"])

    def test_configured_cap_cannot_pose_as_observed_proposals(self) -> None:
        req = requested()
        artifact_sha = "d" * 64
        rows = draft_evidence_rows(
            req,
            artifact_sha,
            child_verdict="supported",
            child_reason=None,
        )
        observation = next(
            row for row in rows if row["event"] == "capability_observation"
        )
        observation["tokens_proposed"] = req["max_proposed_tokens"]
        observation["tokens_proposed_observation_source"] = "configured_cap"
        observation["acceptance_rate"] = 1 / int(req["max_proposed_tokens"])
        rows.insert(
            -1,
            {
                "event": "decode_emission",
                **req,
                "decode_step_ordinal": 0,
                "tokens_proposed": req["max_proposed_tokens"],
                "tokens_accepted": 1,
                "target_emitted_count": 1,
                "emitted_count": 2,
                "counter_source": "inferred_from_configured_cap",
                "emission_boundary_source": "grouped_from_token_responses",
            },
        )
        result = spike.derive_evidence_verdict(rows, req, artifact_sha)
        self.assertNotEqual(result["verdict"], "supported")
        self.assertEqual(result["reason"], "event_observability")

    def test_missing_draft_execution_is_generation_failure(self) -> None:
        req = requested()
        artifact_sha = "d" * 64
        rows = draft_evidence_rows(req, artifact_sha)
        observation = next(
            row for row in rows if row["event"] == "capability_observation"
        )
        observation["draft_model_call_count"] = 0
        result = spike.derive_evidence_verdict(rows, req, artifact_sha)
        self.assertEqual(result["reason"], "draft_model_generation")
        self.assertFalse(result["runtime_generation_supported"])

    def test_native_mtp_is_a_separate_generation_failure(self) -> None:
        req = requested(
            mode="native_mtp", target="/models/qwen35", draft=None
        )
        result = spike.derive_evidence_verdict(native_evidence_rows(req), req, None)
        self.assertEqual(result["verdict"], "unsupported_for_joulewise")
        self.assertEqual(result["reason"], "native_mtp_generation")
        observation = native_evidence_rows(req)[0]
        self.assertIsNone(observation["draft_model_identity"])

    def test_requested_pair_mismatch_fails_closed(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            observation = next(
                row for row in rows if row["event"] == "capability_observation"
            )
            observation["target_model_path"] = "/substituted/target"
            return rows

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "evidence_verdict_mismatch")
        self.assertNotIn("supported", [row.get("verdict") for row in rows])

    def test_requested_draft_depth_mismatch_fails_closed(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            observation = next(
                row for row in rows if row["event"] == "capability_observation"
            )
            observation["max_proposed_tokens"] = 2
            return rows

        rows = controller_rows(builder, max_proposed_tokens=3)
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "evidence_verdict_mismatch")

    def test_loaded_draft_substitution_cannot_pose_as_requested_pair(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            loaded = next(
                row
                for row in rows
                if row["event"] == "model_loaded" and row["role"] == "draft"
            )
            loaded["resolved_path"] = "/substituted/draft"
            return rows

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "draft_model_generation")
        self.assertFalse(rows[-1]["runtime_generation_supported"])

    def test_draft_artifact_digest_must_match_controller_observation(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            observation = next(
                row for row in rows if row["event"] == "capability_observation"
            )
            observation["draft_model_identity"]["model_artifact_sha256"] = "f" * 64
            return rows

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "draft_model_generation")
        self.assertFalse(rows[-1]["runtime_generation_supported"])

    def test_missing_lifecycle_row_cannot_upgrade_generation(self) -> None:
        def builder(req, artifact_sha):
            return [
                row
                for row in draft_evidence_rows(req, artifact_sha)
                if row["event"] != "request_admitted"
            ]

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        self.assertTrue(rows[-1]["runtime_generation_supported"])

    def test_terminal_output_must_match_generation_rows(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            terminal = next(row for row in rows if row["event"] == "request_terminal")
            terminal["output_token_ids"] = [999]
            return rows

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["reason"], "event_observability")
        self.assertFalse(rows[-1]["claim_instrumentable"])

    def test_duplicate_terminal_rows_fail_lifecycle_crosscheck(self) -> None:
        def builder(req, artifact_sha):
            rows = draft_evidence_rows(req, artifact_sha)
            terminal = next(row for row in rows if row["event"] == "request_terminal")
            rows.insert(-1, dict(terminal))
            return rows

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["reason"], "event_observability")

    def test_child_supported_without_observation_is_not_trusted(self) -> None:
        def builder(_req, _artifact_sha):
            return [
                {
                    "event": "probe_outcome",
                    "verdict": "supported",
                    "reason": None,
                    "stage": "complete",
                }
            ]

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "draft_model_generation")
        self.assertTrue(rows[-1]["evidence_verdict_mismatch"])

    def test_missing_draft_artifact_is_structured_runtime_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = _write_artifact(root, "target")
            args = SimpleNamespace(
                mode="draft_model",
                target_model=str(target),
                draft_model=str(root / "missing-draft"),
                max_proposed_tokens=3,
                max_tokens=4,
                timeout_seconds=1.0,
                prompt=spike.DEFAULT_PROMPT,
            )
            stream = io.StringIO()
            versions = {
                "mlx-lm": spike.EXPECTED_MLX_LM,
                "mlx": spike.EXPECTED_MLX,
            }
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(
                spike, "_source_surface_record", return_value=source_surface()
            ), patch.object(spike.subprocess, "run") as run:
                spike.controller(args, spike.Emitter(stream))
        run.assert_not_called()
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "draft_model_artifact_missing")

    def test_same_target_and_draft_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact = _write_artifact(Path(temporary), "same")
            args = SimpleNamespace(
                mode="draft_model",
                target_model=str(artifact),
                draft_model=str(artifact),
                max_proposed_tokens=3,
                max_tokens=4,
                timeout_seconds=1.0,
                prompt=spike.DEFAULT_PROMPT,
            )
            stream = io.StringIO()
            versions = {
                "mlx-lm": spike.EXPECTED_MLX_LM,
                "mlx": spike.EXPECTED_MLX,
            }
            with patch.object(
                spike,
                "_distribution_record",
                side_effect=lambda name: {
                    "name": name,
                    "version": versions[name],
                    "package_root": f"/fake/{name}",
                },
            ), patch.object(
                spike, "_source_surface_record", return_value=source_surface()
            ):
                spike.controller(args, spike.Emitter(stream))
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["reason"], "target_draft_identity_collision")

    def test_pin_mismatch_is_jsonl(self) -> None:
        args = SimpleNamespace(
            mode="native_mtp",
            target_model=spike.NATIVE_MTP_CANDIDATE,
            draft_model=None,
            max_proposed_tokens=1,
            max_tokens=4,
            timeout_seconds=1.0,
            prompt=spike.DEFAULT_PROMPT,
        )
        stream = io.StringIO()
        with patch.object(
            spike,
            "_distribution_record",
            side_effect=lambda name: {
                "name": name,
                "version": None,
                "package_root": None,
            },
        ):
            spike.controller(args, spike.Emitter(stream))
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertTrue(all(row["schema"] == spike.SCHEMA for row in rows))
        self.assertEqual(rows[-1]["reason"], "pin_mismatch")

    def test_worker_protocol_failure_degrades_cleanly(self) -> None:
        def builder(_req, _artifact_sha):
            return [{"event": "not_outcome"}]

        rows = controller_rows(builder)
        self.assertEqual(rows[-1]["verdict"], "runtime_unavailable")
        self.assertEqual(rows[-1]["reason"], "worker_protocol_failure")

    def test_fake_worker_records_generation_but_refuses_observability(self) -> None:
        class FakeTokenizer:
            vocab_size = 100
            name_or_path = "fake-tokenizer"

        def target_model(_inputs, *_args, **_kwargs):
            return None

        def draft_model(_inputs, *_args, **_kwargs):
            return None

        def fake_load(path):
            model = target_model if path == "/models/target" else draft_model
            return model, FakeTokenizer()

        def fake_stream_generate(target, _tokenizer, _prompt, **kwargs):
            target(SimpleNamespace(shape=(1, 2)))
            kwargs["draft_model"](SimpleNamespace(shape=(1, 1)))
            yield SimpleNamespace(token=10, from_draft=True, finish_reason=None)
            yield SimpleNamespace(token=11, from_draft=False, finish_reason="length")

        mlx = ModuleType("mlx")
        mlx.__path__ = []  # type: ignore[attr-defined]
        mlx_core = ModuleType("mlx.core")
        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
        mlx.core = mlx_core  # type: ignore[attr-defined]
        mlx_lm = ModuleType("mlx_lm")
        mlx_lm.load = fake_load  # type: ignore[attr-defined]
        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
        args = SimpleNamespace(
            mode="draft_model",
            target_model="/models/target",
            draft_model="/models/draft",
            max_proposed_tokens=3,
            max_tokens=2,
            timeout_seconds=1.0,
            prompt=spike.DEFAULT_PROMPT,
            _draft_artifact_sha256="d" * 64,
            _draft_config_sha256="c" * 64,
            _draft_quantization='{"bits":4}',
            _draft_weight_format="safetensors",
        )
        stream = io.StringIO()
        with patch.dict(sys.modules, modules), patch.object(sys, "stdout", stream):
            self.assertEqual(spike.runtime_worker(args), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "unsupported_for_joulewise")
        self.assertEqual(rows[-1]["reason"], "event_observability")
        observation = next(
            row for row in rows if row["event"] == "capability_observation"
        )
        self.assertTrue(observation["runtime_generation_supported"])
        self.assertEqual(observation["tokens_accepted"], 1)
        self.assertIsNone(observation["tokens_proposed"])
        self.assertEqual(observation["decode_emission_event_count"], 0)

    def test_stub_runtime_with_real_observability_surfaces_is_supported(self) -> None:
        class FakeTokenizer:
            vocab_size = 100
            name_or_path = "fake-tokenizer"

        def target_model(_inputs, *_args, **_kwargs):
            return None

        def draft_model(_inputs, *_args, **_kwargs):
            return None

        def fake_load(path):
            model = target_model if path == "/models/target" else draft_model
            return model, FakeTokenizer()

        def fake_stream_generate(
            target,
            _tokenizer,
            _prompt,
            *,
            speculative_decode_callback,
            **kwargs,
        ):
            target(SimpleNamespace(shape=(1, 2)))
            kwargs["draft_model"](SimpleNamespace(shape=(1, 1)))
            speculative_decode_callback(
                decode_step_ordinal=0,
                tokens_proposed=2,
                tokens_accepted=1,
                aggregate_acceptance_rate=0.5,
                target_emitted_count=1,
                emitted_count=2,
                emitted_token_ids=[10, 11],
            )
            yield SimpleNamespace(token=10, from_draft=True, finish_reason=None)
            yield SimpleNamespace(token=11, from_draft=False, finish_reason=None)
            speculative_decode_callback(
                decode_step_ordinal=1,
                tokens_proposed=3,
                tokens_accepted=2,
                aggregate_acceptance_rate=0.6,
                target_emitted_count=0,
                emitted_count=2,
                emitted_token_ids=[12, 13],
            )
            yield SimpleNamespace(token=12, from_draft=True, finish_reason=None)
            yield SimpleNamespace(token=13, from_draft=True, finish_reason="length")

        mlx = ModuleType("mlx")
        mlx.__path__ = []  # type: ignore[attr-defined]
        mlx_core = ModuleType("mlx.core")
        mlx_core.metal = SimpleNamespace(is_available=lambda: True)  # type: ignore[attr-defined]
        mlx.core = mlx_core  # type: ignore[attr-defined]
        mlx_lm = ModuleType("mlx_lm")
        mlx_lm.load = fake_load  # type: ignore[attr-defined]
        mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
        modules = {"mlx": mlx, "mlx.core": mlx_core, "mlx_lm": mlx_lm}
        args = SimpleNamespace(
            mode="draft_model",
            target_model="/models/target",
            draft_model="/models/draft",
            max_proposed_tokens=3,
            max_tokens=4,
            timeout_seconds=1.0,
            prompt=spike.DEFAULT_PROMPT,
            _draft_artifact_sha256="d" * 64,
            _draft_config_sha256="c" * 64,
            _draft_quantization='{"bits":4}',
            _draft_weight_format="safetensors",
        )
        stream = io.StringIO()
        with patch.dict(sys.modules, modules), patch.object(sys, "stdout", stream):
            self.assertEqual(spike.runtime_worker(args), 0)
        rows = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(rows[-1]["verdict"], "supported")
        self.assertIsNone(rows[-1]["reason"])
        surface = next(
            row for row in rows if row["event"] == "runtime_observability_surface"
        )
        self.assertTrue(surface["callback_parameter_explicit"])
        observation = next(
            row for row in rows if row["event"] == "capability_observation"
        )
        self.assertEqual(observation["tokens_proposed"], 5)
        self.assertEqual(observation["tokens_accepted"], 3)
        self.assertEqual(observation["acceptance_rate"], 0.6)
        self.assertEqual(observation["decode_emission_event_count"], 2)
        derived = spike.derive_evidence_verdict(
            rows, spike._requested_parameters(args), "d" * 64
        )
        self.assertEqual(derived["verdict"], "supported")
        self.assertTrue(derived["claim_instrumentable"])

    def test_invalid_configuration_is_json(self) -> None:
        stream = io.StringIO()
        with patch.object(sys, "stdout", stream):
            self.assertEqual(spike.main(["--mode", "draft_model"]), 2)
        row = json.loads(stream.getvalue())
        self.assertEqual(row["event"], "probe_outcome")
        self.assertEqual(row["reason"], "invalid_probe_configuration")


if __name__ == "__main__":
    unittest.main()
