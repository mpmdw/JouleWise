"""Synthetic shard tests. Native parity uses the pinned public canonical port when supplied."""
import hashlib
import io
import json
import math
import os
import re
import struct
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import align_stream_qwen4_exp as stream


MODULE = b"# synthetic model module\n"
STEM = "language_model.model.layers.0"
WEIGHTS = {
    f"{STEM}.conv1d.weight": (2, 3, 1),
    f"{STEM}.mlp.switch_mlp.gate_up_proj.weight": (2, 2, 64),
    f"{STEM}.mlp.switch_mlp.down_proj.weight": (2, 1, 64),
    "language_model.lm_head.weight": (2, 2),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def shard(path, tensors):
    records, payload = {}, bytearray()
    for key, (shape, dtype, data) in tensors.items():
        records[key] = {"dtype": dtype, "shape": list(shape), "data_offsets": [len(payload), len(payload) + len(data)]}
        payload.extend(data)
    raw = json.dumps(records).encode()
    raw += b" " * (-len(raw) % 8)
    path.write_bytes(struct.pack("<Q", len(raw)) + raw + payload)


class FixtureSource:
    identity = {"repo": "synthetic", "revision": "fixture"}

    def __init__(self, checkpoint, root):
        self.checkpoint = checkpoint
        self.root = root
        self.small = {p.name: p.read_bytes() for p in checkpoint.iterdir() if p.suffix != ".safetensors"}
        self.inputs = [stream.Input(p.name, p.stat().st_size, digest(p.read_bytes()))
                       for p in sorted(checkpoint.glob("*.safetensors"))]
        self.downloads = []
        self.observations = []
        self.interrupt = None

    def header(self, item):
        with (self.checkpoint / item.name).open("rb") as file:
            raw = file.read(8)
            return raw + file.read(struct.unpack("<Q", raw)[0])

    def download(self, item, start):
        self.downloads.append((item.name, start))
        self.observations.append((len(list(self.root.glob("source-*.part"))), self.allocated()))
        data = (self.checkpoint / item.name).read_bytes()[start:]
        if item.name == self.interrupt:
            data = data[:len(data) // 2]
        return io.BytesIO(data)

    def allocated(self):
        return sum(p.stat().st_blocks * 512 for p in self.root.rglob("*") if p.is_file())


def checkpoint(root, config, by_shard):
    root.mkdir()
    index = {}
    for number, tensors in enumerate(by_shard):
        name = f"model-{number:05d}.safetensors"
        shard(root / name, tensors)
        index.update({key: name for key in tensors})
    (root / "config.json").write_bytes(stream.json_bytes(config))
    (root / stream.INDEX).write_bytes(stream.json_bytes({"weight_map": index}))
    (root / "tokenizer.json").write_text("{}\n")
    return root


class FixtureCanonical:
    FORMAT = "joulewise-qwen4-exp-canonical-v2"
    PINS = {"mlx": "fixture"}
    SHARD_RE = re.compile(r"\.ngram_embedding\.shard_(\d+)\.weight$")
    EXPERT_RE = re.compile(r"^(?P<head>.+)\.mlp\.experts\.(?P<e>\d+)\.(?P<proj>gate|up|down)_proj\.weight$")

    @staticmethod
    def target_shape(entries):
        _, _, key, shape, kind = entries[0]
        if kind == "conv":
            return shape[0], shape[2], shape[1]
        if kind == "expert":
            return (2, 2 if key.endswith("gate_proj.weight") else 1, 64)
        return shape

    @staticmethod
    def digest_scheme():
        return {"algorithm": "sha256"}

    @staticmethod
    def tensor_bytes(shape, dtype):
        return math.prod(shape) * {"BF16": 2, "U32": 4}[dtype]

    @staticmethod
    def _text_config(config):
        return config

    @staticmethod
    def expected_parameters(rules, config):
        return WEIGHTS, SimpleNamespace(tie_word_embeddings=False, ple_layer_ids=[1])

    @staticmethod
    def sha256(path):
        return digest(path.read_bytes())

    @classmethod
    def hash_files(cls, paths, nofollow=False):
        return {p: cls.sha256(p) for p in paths}


class FixtureRules:
    @staticmethod
    def ple_storage_for(profile, storage, group):
        return "bf16"

    @staticmethod
    def hf_to_mlx_key(key):
        return None if key.startswith("mtp.") else key

    @staticmethod
    def is_ngram_buffer_key(name):
        return False

    @staticmethod
    def quantization_for(key, shape, profile, group):
        return {"group_size": group, "bits": 6, "mode": "affine"} if ".switch_mlp." in key else None

    @staticmethod
    def NgramHashSpec(args, layer):
        return SimpleNamespace(padded_vocab_size=3, head_dim=2)

    @staticmethod
    def ngram_record_layout(fmt, dim, group):
        return {"record_bytes": 2 * dim}


def fixture_encode(canonical, rules, write, source):
    # Deterministic fixture encoder for bare Python CI exercising all three packed ranges.
    raw = source.read_bytes()
    size, = struct.unpack("<Q", raw[:8])
    start, stop = json.loads(raw[8:8 + size])[write.piece.key]["data_offsets"]
    data = raw[8 + size + start:8 + size + stop]
    if write.bits:
        yield (data[:48], data[48:50], data[50:52])
    else:
        yield (data,)


class StreamTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.root = self.base / "job"
        source = []
        self.expert_bytes = []
        for i in range(2):
            tensors = {}
            for projection in ("gate", "up", "down"):
                data = hashlib.shake_256(f"{i}:{projection}".encode()).digest(128)
                tensors[f"{STEM}.mlp.experts.{i}.{projection}_proj.weight"] = ((1, 64), "BF16", data)
                self.expert_bytes.append(data)
            tensors[f"{STEM}.ple.ple_embedding.ngram_embedding.shard_{i}.weight"] = (
                (2 - i, 2), "BF16", bytes([10 + i]) * (8 - 4 * i))
            source.append(tensors)
        source[0][f"{STEM}.conv1d.weight"] = ((2, 1, 3), "BF16", bytes(range(12)))
        source[1]["language_model.lm_head.weight"] = ((2, 2), "BF16", bytes(range(8)))
        source.append({"mtp.extra": ((2,), "BF16", b"\x01\x02\x03\x04")})
        self.source = FixtureSource(checkpoint(self.base / "hf", {}, source), self.root)
        self.plan = self.make_plan()

    def make_plan(self):
        return stream.Plan(self.source, FixtureCanonical(), FixtureRules(), MODULE, "maxfit", 160)

    def convert(self):
        return stream.stream(self.root, self.plan, reserve=0, encode=fixture_encode)

    def test_budget_one_source_and_allocation_bound(self):
        budget = stream.Budget(self.base, self.plan, 0)
        real_encode = fixture_encode

        def observe(*args):
            self.assertEqual(len(list(self.root.glob("source-*.part"))), 1)
            self.assertLessEqual(self.source.allocated(), budget.peak)
            yield from real_encode(*args)

        with patch.object(stream, "range_sha", wraps=stream.range_sha) as verify:
            stream.stream(self.root, self.plan, reserve=0, encode=observe)
        self.assertTrue(any(call.args[0].parent.name == "artifact" for call in verify.call_args_list))
        self.assertEqual(len(self.source.downloads), 3)
        self.assertEqual([number for number, _ in self.source.observations], [0, 0, 0])
        self.assertTrue(all(size <= budget.peak for _, size in self.source.observations))
        self.assertFalse(list(self.root.glob("source-*.part")))

    def test_short_disk_refuses_before_creating_job_or_downloading(self):
        with patch.object(stream.os, "statvfs", return_value=SimpleNamespace(f_frsize=1)):
            budget = stream.Budget(self.base, self.plan, 123)
        with patch.object(stream.os, "statvfs", return_value=SimpleNamespace(
                f_frsize=1, f_bavail=budget.peak + budget.reserve - 1)), patch("builtins.print") as reported:
            with self.assertRaisesRegex(ValueError, "short disk"):
                stream.stream(self.root, self.plan, reserve=123, encode=fixture_encode)
        self.assertFalse(self.root.exists())
        self.assertEqual(self.source.downloads, [])
        report = json.loads(reported.call_args.args[0])
        self.assertEqual(report["reserve_bytes"], 123)
        self.assertEqual(report["one_source_allocation_bytes"], max(item.size for item in self.source.inputs))
        self.assertEqual(report["peak_extra_disk_bytes"], budget.peak)

    def test_disk_loss_after_a_shard_refuses_the_next_transfer(self):
        unit = os.statvfs(self.base).f_frsize
        budget = stream.Budget(self.base, self.plan, 0)

        def disk(path):
            free = budget.peak // unit if not self.source.downloads else 1
            return SimpleNamespace(f_frsize=unit, f_bavail=free)

        with patch.object(stream.os, "statvfs", disk), self.assertRaisesRegex(ValueError, "short disk"):
            self.convert()
        self.assertEqual(self.source.downloads, [(self.source.inputs[0].name, 0)])
        self.assertFalse(list(self.root.glob("source-*.part")))
        self.convert()
        self.assertEqual(self.source.downloads, [(item.name, 0) for item in self.source.inputs])

    def test_resume_reuses_committed_shard_and_partial_download(self):
        second = self.source.inputs[1].name
        self.source.interrupt = second
        with self.assertRaisesRegex(ValueError, "short download"):
            self.convert()
        staged, = self.root.glob("source-*.part")
        self.assertGreater(staged.stat().st_size, 0)
        offset = staged.stat().st_size
        self.assertFalse((self.root / "artifact/manifest.json").exists())
        self.source.interrupt = None
        first_result = self.convert()
        self.assertEqual(self.source.downloads, [(self.source.inputs[0].name, 0), (second, 0),
                                                (second, offset), (self.source.inputs[2].name, 0)])
        self.assertEqual(self.convert(), first_result)
        self.assertEqual(len(self.source.downloads), 4)

    def test_resume_after_journal_commit_before_source_unlink(self):
        original = Path.unlink

        def interrupt(path, *args, **kwargs):
            if path.name == "source-000.part":
                raise InterruptedError("synthetic interruption")
            return original(path, *args, **kwargs)

        with patch.object(Path, "unlink", interrupt), self.assertRaises(InterruptedError):
            self.convert()
        self.assertTrue((self.root / "source-000.part").exists())
        self.convert()
        self.assertEqual(self.source.downloads, [(item.name, 0) for item in self.source.inputs])
        self.assertFalse(list(self.root.glob("source-*.part")))

    def test_output_hash_failure_retains_source_and_refuses_resume_on_committed_corruption(self):
        original = stream.range_sha

        def mismatch(path, start, size):
            return "0" * 64 if path.parent.name == "artifact" else original(path, start, size)

        with patch.object(stream, "range_sha", mismatch), self.assertRaisesRegex(ValueError, "output span sha256"):
            self.convert()
        self.assertTrue((self.root / "source-000.part").exists())
        self.convert()
        manifest = json.loads((self.root / "artifact/manifest.json").read_bytes())
        tensor = manifest["tensors"][f"{STEM}.conv1d.weight"]
        with (self.root / "artifact" / tensor["file"]).open("r+b") as payload:
            payload.seek(tensor["byte_offset"])
            payload.write(b"\x99")
        with self.assertRaisesRegex(ValueError, "output span sha256"):
            self.convert()

    def test_manifest_matches_nonstreamed_fixture_tensor_hashes(self):
        manifest_sha = self.convert()
        raw = (self.root / "artifact/manifest.json").read_bytes()
        self.assertEqual(manifest_sha, digest(raw))
        manifest = json.loads(raw)
        grouped = [([0, 1, 3, 4], "gate_up", (2, 2)), ([2, 5], "down", (2, 1))]
        reference = {
            f"{STEM}.conv1d.weight": ((2, 3, 1), "BF16", bytes(range(12))),
            "language_model.lm_head.weight": ((2, 2), "BF16", bytes(range(8))),
            f"{STEM}.ple.ple_embedding.ngram_embedding.weight": ((3, 2), "BF16", b"\x0a" * 8 + b"\x0b" * 4),
        }
        for indices, projection, shape in grouped:
            packed = [self.expert_bytes[i] for i in indices]
            key = f"{STEM}.mlp.switch_mlp.{projection}_proj"
            reference[key + ".weight"] = ((*shape, 12), "U32", b"".join(p[:48] for p in packed))
            reference[key + ".scales"] = ((*shape, 1), "BF16", b"".join(p[48:50] for p in packed))
            reference[key + ".biases"] = ((*shape, 1), "BF16", b"".join(p[50:52] for p in packed))
        self.assertEqual(set(reference), set(manifest["tensors"]))
        for key, (shape, dtype, data) in reference.items():
            entry = manifest["tensors"][key]
            self.assertEqual((entry["name"], entry["shape"], entry["dtype"], entry["sha256"]),
                             (key, list(shape), dtype, digest(data)))
        self.assertEqual(manifest["source"]["sha256"], {item.name: item.checksum for item in self.source.inputs})

    def test_source_hash_is_checked_before_conversion(self):
        item = self.source.inputs[0]
        path = self.source.checkpoint / item.name
        with path.open("r+b") as payload:
            payload.seek(-1, os.SEEK_END)
            payload.write(b"\xff")
        with self.assertRaisesRegex(ValueError, "source sha256 mismatch"):
            self.convert()
        self.assertFalse(list(self.root.glob("source-*.part")))
        self.assertEqual(json.loads((self.root / "journal.json").read_text())["committed"], [])


class HubRangeTests(unittest.TestCase):
    def test_plan_and_partial_download_require_exact_http_ranges(self):
        name = "model-00001-of-00131.safetensors"
        header = struct.pack("<Q", 2) + b"{}"
        source = object.__new__(stream.HubSource)
        item = stream.Input(name, 16, "0" * 64)

        class Reply(io.BytesIO):
            status = 206

            def __init__(self, raw, content_range):
                super().__init__(raw)
                self.headers = {"Content-Range": content_range}

        replies = [Reply(header[:8], "bytes 0-7/16"), Reply(header[8:], "bytes 8-9/16"),
                   Reply(b"xyz", "bytes 13-15/16"), Reply(b"xyz", "bytes 12-15/16")]
        with patch.object(stream.urllib.request, "urlopen", side_effect=replies) as open_http:
            self.assertEqual(source.header(item), header)
            with source.download(item, 13) as payload:
                self.assertEqual(payload.read(), b"xyz")
            with self.assertRaisesRegex(ValueError, "exact byte range"):
                source.download(item, 13)
        self.assertEqual([call.args[0].get_header("Range") for call in open_http.call_args_list],
                         ["bytes=0-7", "bytes=8-9", "bytes=13-15", "bytes=13-15"])
        self.assertTrue(all(stream.REVISION in call.args[0].full_url for call in open_http.call_args_list))


NATIVE_PORT = os.environ.get("JW_SYNTHETIC_QWEN4_PORT")


@unittest.skipUnless(NATIVE_PORT, "set JW_SYNTHETIC_QWEN4_PORT to run with the pinned MLX port")
class NativeParityTests(unittest.TestCase):
    def test_maxfit_matches_pinned_whole_checkpoint_converter(self):
        import numpy as np

        canonical, rules, module = stream.load_port(Path(NATIVE_PORT))
        text = {
            "vocab_size": 96, "hidden_size": 64, "num_hidden_layers": 4,
            "num_attention_heads": 2, "num_key_value_heads": 1, "head_dim": 32,
            "linear_num_key_heads": 1, "linear_num_value_heads": 2,
            "linear_key_head_dim": 16, "linear_value_head_dim": 16, "linear_conv_kernel_dim": 4,
            "moe_intermediate_size": 64, "shared_expert_intermediate_size": 64,
            "num_experts": 2, "num_experts_per_tok": 1,
            "hc_count": 2, "hc_lowrank": 16,
            "ple_layer_ids": [2], "ple_embed_dim": 32, "ple_conv_kernel_size": 4,
            "ngram_size": 3, "heads_per_ngram": 2, "ngram_vocab_size_base": 11,
            "make_ngram_vocab_size_divisible_by": 8, "split_ngram_parts": 2,
            "indexer_n_heads": 2, "indexer_kv_heads": 1, "indexer_head_dim": 16,
            "indexer_budget": 8, "indexer_compress_ratio": 4,
            "output_gate_type": "sigmoid", "eos_token_id": 1, "tie_word_embeddings": False,
            "layer_types": ["linear_attention"] * 3 + ["full_attention"],
            "rope_parameters": {"partial_rotary_factor": 0.25, "rope_theta": 10_000_000,
                                "rope_type": "default", "mrope_section": [2, 1, 1]},
        }
        expected, args = canonical.expected_parameters(rules, text)
        rng = np.random.default_rng(182)
        shards = [{}, {}, {}]

        def put(i, key, array, dtype="BF16"):
            if dtype == "BF16":
                data = rules._f32_to_bf16_bits(array)
            else:
                data = array.astype({"F32": "<f4", "F16": "<f2", "I64": "<i8"}[dtype])
            shards[i][key] = (array.shape, dtype, data.tobytes())

        for i, (key, shape) in enumerate(expected.items()):
            hf_key = key.replace("language_model.model.", "model.language_model.", 1).removeprefix("language_model.")
            values = rng.standard_normal(shape).astype("<f4")
            if hf_key.endswith(".switch_mlp.gate_up_proj.weight"):
                for e, parts in enumerate(values):
                    gate, up = np.split(parts, 2)
                    put(e, hf_key.replace("switch_mlp.gate_up_proj.weight", f"experts.{e}.gate_proj.weight"), gate)
                    put((e + 1) % 2, hf_key.replace("switch_mlp.gate_up_proj.weight", f"experts.{e}.up_proj.weight"), up)
            elif hf_key.endswith(".switch_mlp.down_proj.weight"):
                for e, part in enumerate(values):
                    put(e, hf_key.replace("switch_mlp.down_proj.weight", f"experts.{e}.down_proj.weight"), part)
            else:
                if hf_key.endswith("conv1d.weight"):
                    values = values.transpose(0, 2, 1)
                put(i % 2, hf_key, values, dtype="F16" if i % 5 == 0 else "BF16")
        spec = rules.NgramHashSpec(args, 0)
        prefix = "model.language_model.layers.1.ple.ple_embedding"
        table = rng.standard_normal((spec.padded_vocab_size, spec.head_dim)).astype("<f4")
        for i, values in enumerate(np.array_split(table, 2)):
            put(1 - i, f"{prefix}.ngram_embedding.shard_{i}.weight", values, ("BF16", "F32")[i])
        for (suffix, values) in zip(("layer_multipliers", "ngram_heads_vocab_sizes", "ngram_heads_offsets"),
                                    (spec.multipliers, spec.head_vocab_sizes, spec.head_offsets)):
            put(2, f"{prefix}.{suffix}", np.array(values, dtype="<i8"), "I64")
        put(2, "mtp.extra", np.zeros((2, 2), dtype="<f4"))
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = checkpoint(base / "hf", {"text_config": text}, shards)
            root = base / "streamed"
            ref = base / "reference"
            limit = 45_000
            original = canonical.convert(source, ref, module_file=canonical.MODULE_FILE, shard_bytes=limit)
            plan = stream.Plan(FixtureSource(source, root), canonical, rules, module, "maxfit", limit)
            pin = stream.stream(root, plan, reserve=0)
            artifact = root / "artifact"
            manifest = canonical.verify_manifest(artifact, pin)
            self.assertEqual(manifest["files"], original["files"])
            self.assertEqual(manifest["inputs"], original["inputs"])
            self.assertEqual(manifest["ngram_tables"], original["ngram_tables"])
            self.assertEqual(manifest["omitted_keys"], original["omitted_keys"])
            model, config = canonical.load_verified_model(artifact, pin)
            self.assertEqual(config["model_type"], "qwen4_exp")
            self.assertEqual(set(model.ngram_tables()), {1})
            reference = {}
            for file in sorted(ref.glob("*.safetensors")):
                header, base_offset = canonical.tensor_header(file)
                for key, record in header.items():
                    if key == "__metadata__":
                        continue
                    start, stop = record["data_offsets"]
                    with file.open("rb") as payload:
                        payload.seek(base_offset + start)
                        reference[key] = (record["shape"], record["dtype"], digest(payload.read(stop - start)))
            reference["language_model.model.layers.1.ple.ple_embedding.ngram_embedding.weight"] = (
                list(table.shape), "BF16", digest(next(ref.glob("ngram-*.bin")).read_bytes()))
            self.assertEqual(set(reference), set(manifest["tensors"]))
            for key, entry in manifest["tensors"].items():
                self.assertEqual((entry["shape"], entry["dtype"], entry["sha256"]), reference[key], key)
