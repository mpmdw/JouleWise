"""Fixture-only Saturday workflow checks. Never opens study or model data."""
import contextlib
from dataclasses import asdict
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch, Mock

from scripts import qwen4exp_mbp_live as live
from scripts import qwen4exp_bf16_benchmark as reference
from scripts import qwen4exp_mbp_report as reporting


def system_sample(**changes):
    sample = dict(swapouts=17, swap_used_bytes=0, compressor_bytes=10**9,
                  pressure_level=1, free_percent=30, rss_bytes=1234)
    sample.update(changes)
    return sample


class DryRunTests(unittest.TestCase):
    def test_all_commands_are_side_effect_free(self):
        for command in ("download", "convert", *live.NATIVE):
            with self.subTest(command=command), contextlib.redirect_stdout(io.StringIO()) as output:
                with patch.object(live, "volume_info", side_effect=AssertionError("disk read")), \
                     patch.object(live, "download", side_effect=AssertionError("network")), \
                     patch.object(live, "native_worker", side_effect=AssertionError("MLX")), \
                     patch.object(Path, "open", side_effect=AssertionError("file open")):
                    self.assertEqual(live.main([command, "--dry-run"]), 0)
                self.assertTrue(json.loads(output.getvalue())["dry_run"])

    def test_reference_dry_run_never_calls_network(self):
        with patch.object(reference, "urlopen", side_effect=AssertionError("network")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(reference.main(["--dry-run"]), 0)
        self.assertEqual(json.loads(out.getvalue())["requests_sent"], 0)

    def test_native_refused_without_operator_assertion(self):
        with self.assertRaisesRegex(ValueError, "validation-only"):
            live.main(["memory"])

    def test_stages_are_ordered_and_caps_cannot_be_raised(self):
        for options in (["--contexts", "40960", "4096"], ["--metal-cap-gb", "128"],
                        ["--poll-seconds", "60"], ["--decode-tokens", "0"]):
            with self.subTest(options=options), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    live.parse_args(["memory", "--dry-run", *options])


class SourceTests(unittest.TestCase):
    def make_snapshot(self, directory):
        directory = Path(directory)
        content = {name: b"{}" for name in ("config.json", "tokenizer.json", "tokenizer_config.json",
                                            "chat_template.jinja")}
        content["model.safetensors.index.json"] = json.dumps({"weight_map": {"x": "model-00001.safetensors"}}).encode()
        content["model-00001.safetensors"] = b"tiny pretend weights"
        metadata = {}
        for name, data in content.items():
            (directory / name).write_bytes(data)
            metadata[name] = {"size": len(data), "blob_id": hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()}
            if name.endswith(".safetensors"):
                metadata[name]["sha256"] = hashlib.sha256(data).hexdigest()
        return metadata

    def test_verifies_upstream_lfs_and_git_blob_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = self.make_snapshot(tmp)
            result = live.verify_source(tmp, metadata, expected_shards=1)
            self.assertEqual(len(result), 6)
            for value in result.values():
                self.assertEqual(len(value), 64)
            (Path(tmp) / "model-00001.safetensors").write_bytes(b"bad pretend weights!")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                live.verify_source(tmp, metadata, expected_shards=1)

    def test_rejects_wrong_shard_inventory_and_small_file_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata = self.make_snapshot(tmp)
            with self.assertRaisesRegex(ValueError, "inventory"):
                live.verify_source(tmp, metadata)
            (Path(tmp) / "config.json").write_bytes(b"[]")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                live.verify_source(tmp, metadata, expected_shards=1)

    def test_conversion_preserves_recipe_and_writes_external_raw_sums(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            snapshot = base / "source"
            snapshot.mkdir()
            metadata = self.make_snapshot(snapshot)
            receipt = base / "source.json"
            receipt.write_text(json.dumps(dict(revision=live.REVISION, repo=live.REPO_ID,
                                               snapshot=str(snapshot), metadata=metadata, sha256={"a": "b"})))
            artifact = base / "maxfit"
            def convert(source, output, **kwargs):
                output.mkdir()
                (output / "manifest.json").write_text('{"tiny":true}')
            converter = types.SimpleNamespace(convert=Mock(side_effect=convert), MODULE_SHA256="a" * 64)
            args = live.parse_args(["convert", "--source-receipt", str(receipt), "--artifact", str(artifact),
                                    "--out", str(base / "convert.json")])
            with patch.dict(sys.modules, {"align_convert_qwen4_exp": converter}), \
                 patch.object(live, "external", side_effect=Path), \
                 patch.object(live, "verify_source", return_value={"a": "b"}), \
                 patch.object(os, "statvfs", return_value=types.SimpleNamespace(f_bavail=10**12, f_frsize=1)):
                result = live.convert(args)
            converter.convert.assert_called_once_with(snapshot, artifact, profile="maxfit", group_size=64, ple_storage="bf16")
            self.assertEqual(result["manifest_sha256"], live.raw_sha256(artifact / "manifest.json"))
            self.assertEqual(list(artifact.iterdir()), [artifact / "manifest.json"])
            self.assertTrue(Path(result["plain_sha256s"]).read_text().endswith("  manifest.json\n"))

    def test_live_external_boundary_rejects_before_following_restricted(self):
        with patch.object(Path, "resolve", side_effect=AssertionError("followed forbidden path")):
            with self.assertRaisesRegex(ValueError, "restricted"):
                live.external("/Volumes/JW-EXT/restricted/file")
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(live, "VOLUME", Path(tmp)):
                self.assertEqual(live.external(Path(tmp) / "future"), Path(tmp) / "future")
            with self.assertRaisesRegex(ValueError, "inside"):
                live.external(tmp)


class MemoryTests(unittest.TestCase):
    def test_physical_disk_is_bound_to_apfs_volume(self):
        apfs = {"Containers": [{"Volumes": [{"DeviceIdentifier": "disk5s1"}],
                                 "PhysicalStores": [{"DeviceIdentifier": "disk4s2"}]}]}
        self.assertEqual(live.physical_stores(apfs, "disk5s1"), {"disk4"})
        with self.assertRaisesRegex(ValueError, "absent"):
            live.physical_stores(apfs, "disk8s1")
        apfs["Containers"][0]["PhysicalStores"] = []
        with self.assertRaisesRegex(ValueError, "ancestry"):
            live.physical_stores(apfs, "disk5s1")

    def test_vmstat_real_macos_punctuation(self):
        raw = ('Mach Virtual Memory Statistics: (page size of 16384 bytes)\n'
               'Pages free:                                 123.\n'
               'Pages occupied by compressor:                  5.\n'
               'File-backed pages:                           11.\nSwapouts: 2.\n')
        result = live.parse_vm_stat(raw)
        self.assertEqual(result["swapouts"], 2)
        self.assertEqual(result["compressor_bytes"], 5 * 16384)
        with self.assertRaisesRegex(ValueError, "counters"):
            live.parse_vm_stat("(page size of 4096 bytes)\n")

    def test_aborts_on_swap_pressure_compression_and_free_memory(self):
        before = system_sample()
        self.assertIsNone(live.unsafe_memory(before, before))
        for changes in (dict(swapouts=18), dict(swapouts=16), dict(swap_used_bytes=1),
                        dict(pressure_level=2), dict(free_percent=9), dict(compressor_bytes=4e9)):
            with self.subTest(changes=changes):
                self.assertIsNotNone(live.unsafe_memory(before, system_sample(**changes)))

    def test_supervisor_terminates_worker_and_preserves_abort_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = live.parse_args(["memory", "--out", str(Path(tmp) / "memory.json")])
            child = Mock()
            child.poll.return_value = None
            child.pid = 123
            child.returncode = -15
            with patch.object(live, "sample_system", side_effect=[system_sample(), system_sample(swapouts=18),
                                                                  system_sample(swapouts=18)]), \
                 patch.object(subprocess, "Popen", return_value=child):
                result = live.supervise(args)
            child.terminate.assert_called_once()
            self.assertEqual(result["verdict"], "aborted")
            self.assertEqual(result["swapouts_delta"], 1)
            self.assertEqual(len(Path(result["monitor"]).read_text().splitlines()), 3)

    def test_supervisor_failure_to_monitor_kills_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = live.parse_args(["memory", "--out", str(Path(tmp) / "m.json")])
            child = Mock(pid=1)
            child.poll.return_value = None
            with patch.object(live, "sample_system", side_effect=[system_sample(), ValueError("monitor unavailable")]), \
                 patch.object(subprocess, "Popen", return_value=child):
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    live.supervise(args)
            child.terminate.assert_called_once()

    def test_preexisting_swap_refuses_before_launch(self):
        args = live.parse_args(["memory", "--out", "/tmp/unused.json"])
        with patch.object(live, "sample_system", return_value=system_sample(swap_used_bytes=1)), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("launched")):
            with self.assertRaisesRegex(ValueError, "preflight"):
                live.supervise(args)

    def test_mmap_page_cap_is_separate_from_metal(self):
        live.check_tables({"1": {"resident_bytes": 1}})
        with self.assertRaisesRegex(ValueError, "21.5"):
            live.check_tables({"1": {"resident_bytes": 22e9}})

    def test_terminate_escalates_if_child_ignores_sigterm(self):
        child = Mock()
        child.wait.side_effect = [subprocess.TimeoutExpired("worker", 5), 0]
        live.terminate(child)
        child.kill.assert_called_once()


def identity_receipt():
    return dict(repo=live.REPO_ID, revision=live.REVISION, dtype="bfloat16", quantization=None,
                kv_cache_dtype="auto", mtp=False, transformers="5.22.1",
                template_sha256=reference.e2e.TEMPLATE_SHA256, server_command="fixture",
                server_version="fixture", checkpoint_sha256_manifest="sha256:fixture-only")


class HostedFixtureTests(unittest.TestCase):
    def test_supplied_reference_requires_exact_items_template_profile_and_coverage(self):
        items = reference.e2e.load_items()
        valid = dict(items_sha256=items["_file_sha256"], quant_profile="bf16",
                     harness=reference.e2e.HARNESS_VERSION,
                     template={"sha256": reference.e2e.TEMPLATE_SHA256}, hosted_identity=identity_receipt(),
                     config=asdict(reference.e2e.RunConfig()),
                     stages={"math": {"items": [{"id": i["id"]} for i in items["math"]]}})
        live.validate_reference(valid, ["math"])
        for changes in (dict(items_sha256="wrong"), dict(template={"sha256": "wrong"}),
                        dict(quant_profile="maxfit"), dict(stages={}), dict(hosted_identity={}),
                        dict(config={**valid["config"], "math_thinking": True})):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                live.validate_reference({**valid, **changes}, ["math"])

    def test_rejects_fp8_or_unidentified_reference(self):
        reference.validate_identity(identity_receipt())
        for changes in (dict(dtype="fp8"), dict(revision="main"), dict(mtp=True), dict(quantization="awq")):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "identity"):
                reference.validate_identity({**identity_receipt(), **changes})

    def test_raw_ids_neutral_penalties_and_no_keys_in_report(self):
        tok = types.SimpleNamespace(encode=lambda text, **kw: [ord(c) for c in text],
                                    decode=lambda ids, **kw: ''.join(chr(c) for c in ids))
        poster = Mock(return_value={"usage": {"prompt_tokens": 2},
                                   "choices": [{"text": "4", "finish_reason": "stop"}]})
        adapter = reference.HostedAdapter(tok, "https://fixture.invalid/v1", identity_receipt(), poster=poster)
        generation = adapter.generate([65, 66], max_tokens=10)
        body = poster.call_args.args[0]
        self.assertEqual(body["prompt"], [65, 66])
        self.assertEqual(body["presence_penalty"], 0)
        self.assertEqual(body["repetition_penalty"], 1)
        self.assertEqual(generation.text, "4")
        poster.return_value["usage"]["prompt_tokens"] = 3
        with self.assertRaisesRegex(ValueError, "count mismatch"):
            adapter.generate([65, 66], max_tokens=10)

    def test_context_builder_exact_length_preserves_template_ends(self):
        tok = types.SimpleNamespace(encode=lambda s: list(s.encode()))
        template = types.SimpleNamespace(render=lambda *a, **kw: "HEADJW_CONTEXT_INSERTTAIL")
        ids = live.context_ids(tok, template, 4096, "low")
        self.assertEqual(len(ids), 4096)
        self.assertEqual(bytes(ids[:4]), b"HEAD")
        self.assertEqual(bytes(ids[-4:]), b"TAIL")


class ReportTests(unittest.TestCase):
    def test_missing_evidence_never_becomes_pass(self):
        report = reporting.render(reporting.TEMPLATE.read_text(), {}, "fixture-only")
        self.assertIn("fixture-only", report)
        self.assertIn("memory.json | PENDING", report)
        self.assertIn("GOAL 11: OPEN", report)
        self.assertNotIn("{{", report)

    def test_populates_real_metric_fields_without_closing_goal(self):
        run = dict(context=40960, prompt_tokens=40896, metal={"peak_bytes": 112.7e9},
                   ple_after={"1": {"resident_bytes": 2e9}}, prediction={"relative_error": 0})
        reports = {"memory.json": {"verdict": "completed", "results": {"runs": [run]}}}
        report = reporting.render(reporting.TEMPLATE.read_text(), reports, "tiny")
        self.assertIn("40960 | 40896 | 112.7 | 2.0 | 0", report)
        self.assertIn("GOAL 6: OPEN", report)

    def test_report_dry_run_needs_no_inputs(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(Path, "open", side_effect=AssertionError("read")):
            self.assertEqual(reporting.main(["--dry-run"]), 0)


HAS_MLX = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx_lm") is not None


@unittest.skipUnless(HAS_MLX, "native MLX required; lead runs on Mac outside sandbox")
class NativeMlxTests(unittest.TestCase):
    def test_verified_canonical_maxfit_qsa_and_ple_through_timing_path(self):
        if not (importlib.util.find_spec("torch") and importlib.util.find_spec("transformers")):
            self.skipTest("native canonical smoke requires pinned torch/transformers too")
        from tests.align import test_qwen4_exp_canonical as canonical
        reason = canonical._skip_reason()
        if reason:
            self.skipTest(reason)
        from tests.test_qwen4exp_e2e_eval import _CharTokenizer
        with tempfile.TemporaryDirectory() as tmp, patch.object(canonical, "WORK_ROOT", Path(tmp)):
            fx = canonical.Fixture()  # Tiny random checkpoint; no reference sweep.
            artifact = fx.converted("maxfit")
            args = live.parse_args(["memory", "--artifact", str(artifact),
                                    "--manifest-sha256", live.raw_sha256(artifact / "manifest.json")])
            with patch.object(live, "external", side_effect=Path), \
                 patch("transformers.AutoTokenizer.from_pretrained", return_value=_CharTokenizer(256)):
                adapter = live.load_adapter(args)
            adapter.prefill_step = 8
            prompt = list(range(1, 41))  # Beyond tiny QSA budget 16; both PLE layers.
            expected = adapter.generate(prompt, max_tokens=5, stop_ids=())
            run = live.timed_tokens(adapter, prompt, 4)
            self.assertEqual(run["generated_ids"], expected.token_ids)
            stats = live.table_stats(adapter.model)
            self.assertEqual(len(stats), 2)
            self.assertTrue(all(t["lookups"] > 0 and t["io"] == "mmap" for t in stats.values()))

    def test_timed_prefill_decode_matches_real_generate_step_on_tiny_hybrid(self):
        # Reuse the tiny random GDN + attention + MoE model; never real weights.
        from tests.test_qwen4exp_e2e_eval import MlxAdapterTests
        MlxAdapterTests.setUpClass()
        adapter = MlxAdapterTests.adapter
        prompt = [1, 3, 6, 9, 12, 15, 18, 21, 24, 27]
        expected = adapter.generate(prompt, max_tokens=5, stop_ids=())
        result = live.timed_tokens(adapter, prompt, 4)
        self.assertEqual(result["generated_ids"], expected.token_ids)
        self.assertGreater(result["prefill_tps"], 0)
        self.assertGreater(result["decode_tps"], 0)

    @unittest.skipUnless(sys.platform == "darwin", "Darwin mincore integration")
    def test_mincore_on_tiny_bf16_ple_file(self):
        import numpy as np
        from joulewise.align.models.qwen4_exp import NgramTable
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ple.bin"
            path.write_bytes(b"\0" * (128 * 32 * 2))
            table = NgramTable(path, 128, 32, "bf16", io="mmap")
            try:
                table.gather(np.array([1, 2, 3]))
                stats = live.resident_pages(table)
                self.assertGreater(stats["resident_bytes"], 0)
                self.assertEqual(stats["mapped_bytes"], path.stat().st_size)
            finally:
                table.close()


if __name__ == "__main__":
    unittest.main()
