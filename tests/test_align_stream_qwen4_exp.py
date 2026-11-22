"""Synthetic shard tests. Native parity uses the pinned public canonical port when supplied."""
import hashlib
import http.client
import io
import json
import math
import os
import re
import struct
import subprocess
import tempfile
import unittest
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

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
    SHARD_BYTES = 160
    HASH_CHUNK_BYTES = 256 * 2**20
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

    def digest_scheme(self):
        return {"algorithm": "sha256", "chunk_bytes": self.HASH_CHUNK_BYTES,
                "large_files": "sha256 of the concatenated sha256 digests of consecutive chunk_bytes ranges"}

    @staticmethod
    def tensor_bytes(shape, dtype):
        return math.prod(shape) * {"BF16": 2, "U32": 4}[dtype]

    @staticmethod
    def _text_config(config):
        return config

    @staticmethod
    def expected_parameters(rules, config):
        return WEIGHTS, SimpleNamespace(tie_word_embeddings=False, ple_layer_ids=[1])

    def sha256(self, path):
        raw = path.read_bytes()
        chunk_bytes = self.HASH_CHUNK_BYTES
        if len(raw) <= chunk_bytes:
            return digest(raw)
        return digest(b"".join(hashlib.sha256(raw[start:start + chunk_bytes]).digest()
                               for start in range(0, len(raw), chunk_bytes)))

    def hash_files(self, paths, nofollow=False):
        return {p: self.sha256(p) for p in paths}


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
        self.canonical = FixtureCanonical()
        self.plan = self.make_plan()

    def make_plan(self):
        return stream.Plan(self.source, self.canonical, FixtureRules(), MODULE,
                           "maxfit", self.canonical.SHARD_BYTES)

    def convert(self):
        return stream._run_conversion(self.root, self.plan, reserve=0, encode=fixture_encode)

    def cli_args(self, root, execution, action):
        return [str(root), "--port-checkout", str(self.base / "port"), "--execution", execution, action]

    def test_off_mbp_cli_reaches_worker_for_plan_conversion_and_resume(self):
        actual_worker = stream._run_conversion

        def synthetic_worker(root, plan, *, plan_only):
            return actual_worker(root, plan, reserve=0, plan_only=plan_only, encode=fixture_encode)

        air = subprocess.CompletedProcess(stream.HARDWARE_MODEL_ARGV, 0, stdout=b"Mac16,13\n")
        with (patch.object(stream.sys, "platform", "darwin"),
              patch.object(stream.subprocess, "run", return_value=air) as probe,
              patch.object(stream, "load_port", return_value=(FixtureCanonical(), FixtureRules(), MODULE)),
              patch.object(stream, "HubSource", return_value=self.source) as source,
              patch.object(stream, "_run_conversion", side_effect=synthetic_worker) as worker):
            self.assertEqual(stream.main(self.cli_args(self.root, "off-mbp", "--plan-only")), 0)
            self.assertFalse(self.root.exists())
            self.assertEqual(self.source.downloads, [])
            arguments = self.cli_args(self.root, "off-mbp", "--allow-official-download")
            self.source.interrupt = self.source.inputs[1].name
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as interrupted:
                stream.main(arguments)
            self.assertEqual(interrupted.exception.code, 1)
            staged, = self.root.glob("source-*.part")
            offset = staged.stat().st_size
            self.source.interrupt = None
            self.assertEqual(stream.main(arguments), 0)
        self.assertTrue((self.root / "artifact/manifest.json").is_file())
        self.assertEqual(self.source.downloads[2:4], [(self.source.inputs[0].name, 0),
                                                      (self.source.inputs[1].name, offset)])
        self.assertEqual([call.kwargs["plan_only"] for call in worker.call_args_list], [True, False, False])
        self.assertEqual(source.call_count, 3)
        probe.assert_called_with(("/usr/sbin/sysctl", "-n", "hw.model"), check=True, capture_output=True)
        self.assertEqual(probe.call_count, 3)

    def test_cli_refuses_unadmitted_hosts_before_source_or_job_access(self):
        self.source.interrupt = self.source.inputs[1].name
        with self.assertRaisesRegex(ValueError, "short download"):
            self.convert()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        downloads = list(self.source.downloads)
        fresh = self.base / "fresh"
        cases = [
            ("engineering", "darwin", b"Mac16,13\n", None, "queue launcher", False),
            ("off-mbp", "darwin", b"Mac15,9\n", None, "recognized off-MBP", True),
            ("off-mbp", "darwin", b"VirtualMac2,1\n", None, "recognized off-MBP", True),
            ("off-mbp", "darwin", b"", None, "recognized off-MBP", True),
            ("off-mbp", "darwin", b"", OSError("synthetic failure"), "read the local hardware", True),
            ("off-mbp", "darwin", b"", subprocess.CalledProcessError(1, "sysctl"), "read the local hardware", True),
            ("off-mbp", "linux", b"", None, "verified macOS hardware", False),
        ]
        for execution, platform, model, error, reason, probed in cases:
            for root in (fresh, self.root):
                for action in ("--plan-only", "--allow-official-download"):
                    with self.subTest(execution=execution, platform=platform, model=model,
                                      error=error, root=root.name, action=action):
                        reply = subprocess.CompletedProcess(stream.HARDWARE_MODEL_ARGV, 0, stdout=model)
                        stderr = io.StringIO()
                        with (patch.object(stream.sys, "platform", platform),
                              patch.object(stream.subprocess, "run", return_value=reply, side_effect=error) as probe,
                              patch.object(stream, "load_port") as port,
                              patch.object(stream, "HubSource", return_value=self.source) as source,
                              patch.object(stream, "_run_conversion") as worker,
                              patch.object(Path, "stat") as stat,
                              patch.object(Path, "resolve") as resolve,
                              patch.object(Path, "open") as open_path,
                              patch.object(os, "statvfs") as disk,
                              redirect_stderr(stderr),
                              self.assertRaises(SystemExit) as refused):
                            stream.main(self.cli_args(root, execution, action))
                        self.assertNotEqual(refused.exception.code, 0)
                        self.assertIn(reason, stderr.getvalue())
                        self.assertEqual(probe.call_count, int(probed))
                        for unexpected in (port, source, worker, stat, resolve, open_path, disk):
                            unexpected.assert_not_called()
        self.assertEqual(downloads, self.source.downloads)
        self.assertFalse(fresh.exists())
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_budget_one_source_and_allocation_bound(self):
        budget = stream.Budget(self.base, self.plan, 0)
        real_encode = fixture_encode

        def observe(*args):
            self.assertEqual(len(list(self.root.glob("source-*.part"))), 1)
            self.assertLessEqual(self.source.allocated(), budget.peak)
            yield from real_encode(*args)

        with patch.object(stream, "range_sha", wraps=stream.range_sha) as verify:
            stream._run_conversion(self.root, self.plan, reserve=0, encode=observe)
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
                stream._run_conversion(self.root, self.plan, reserve=123, encode=fixture_encode)
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
        self.assertEqual(self.source.downloads[1:], [(item.name, 0) for item in self.source.inputs])

    def standalone_convert(self, root, source):
        worker = partial(stream._run_conversion, reserve=0, encode=fixture_encode)
        air = subprocess.CompletedProcess(stream.HARDWARE_MODEL_ARGV, 0, stdout=b"Mac16,13\n")
        with (patch.object(stream.sys, "platform", "darwin"),
              patch.object(stream.subprocess, "run", return_value=air),
              patch.object(stream, "load_port", return_value=(self.canonical, FixtureRules(), MODULE)),
              patch.object(stream, "HubSource", return_value=source),
              patch.object(stream, "_run_conversion", worker)):
            return stream.main(self.cli_args(root, "off-mbp", "--allow-official-download"))

    def assert_standalone_refused(self, reason):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as refused:
            self.standalone_convert(self.root, self.source)
        self.assertEqual(refused.exception.code, 1)
        self.assertIn(reason, stderr.getvalue())

    def assert_resume_refused_without_side_effects(self, reason, *replayed):
        downloads = list(self.source.downloads)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(Path, "unlink", autospec=True, side_effect=Path.unlink) as unlink:
            self.assert_standalone_refused(reason)
        unlink.assert_not_called()
        self.assertEqual(self.source.downloads, downloads + [(item.name, 0) for item in replayed])
        self.assertFalse((self.root / "artifact/manifest.json").exists())
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def assert_manifest_matches_uninterrupted(self):
        clean_root = self.base / "clean"
        clean_source = FixtureSource(self.source.checkpoint, clean_root)
        self.assertEqual(self.standalone_convert(clean_root, clean_source), 0)
        raw = (self.root / "artifact/manifest.json").read_bytes()
        self.assertEqual(raw, (clean_root / "artifact/manifest.json").read_bytes())
        self.assertEqual(json.loads(raw)["inputs"], {
            name: self.canonical.sha256(self.source.checkpoint / name)
            for name in ("config.json", *(item.name for item in self.source.inputs))
        })

    def interrupt_during_transfer(self, index):
        self.source.interrupt = self.source.inputs[index].name
        self.assert_standalone_refused("short download")
        self.source.interrupt = None
        staged, = self.root.glob("source-*.part")
        self.assertEqual(staged.name, f"source-{index:03d}.part")
        self.assertGreater(staged.stat().st_size, 0)
        self.assertFalse((self.root / "artifact/manifest.json").exists())
        return staged.stat().st_size

    def test_resume_reuses_committed_shard_and_partial_download(self):
        first, second, third = self.source.inputs
        self.canonical.HASH_CHUNK_BYTES = first.size
        offset = self.interrupt_during_transfer(1)
        journal = json.loads((self.root / "journal.json").read_bytes())
        self.assertEqual(journal.keys(), {"schema", "plan_sha256", "committed"})
        self.assertEqual(journal["schema"], 1)
        row, = journal["committed"]
        self.assertEqual(row[0], first.checksum)
        self.assertEqual(self.standalone_convert(self.root, self.source), 0)
        self.assertEqual(self.source.downloads, [(first.name, 0), (second.name, 0), (first.name, 0),
                                                (second.name, offset), (third.name, 0)])
        self.assert_manifest_matches_uninterrupted()

    def test_resume_refuses_one_bit_tamper_of_committed_input_digest(self):
        first = self.source.inputs[0]
        for chunk_bytes in (first.size, 257):
            with self.subTest(chunk_bytes=chunk_bytes):
                self.root = self.source.root = self.base / f"job-{chunk_bytes}"
                self.canonical.HASH_CHUNK_BYTES = chunk_bytes
                self.interrupt_during_transfer(1)
                path = self.root / "journal.json"
                journal = json.loads(path.read_bytes())
                checksum = journal["committed"][0][0]
                journal["committed"][0][0] = f"{int(checksum[0], 16) ^ 1:x}" + checksum[1:]
                path.write_bytes(stream.json_bytes(journal))
                self.assert_resume_refused_without_side_effects("committed input digest mismatch", first)

    def interrupt_after_journal_commit(self):
        original = Path.unlink

        def interrupt(path, *args, **kwargs):
            if path.name == "source-000.part":
                raise InterruptedError("synthetic interruption before source unlink")
            return original(path, *args, **kwargs)

        with patch.object(Path, "unlink", interrupt):
            self.assert_standalone_refused("synthetic interruption before source unlink")
        staged, = self.root.glob("source-*.part")
        self.assertEqual(staged.name, "source-000.part")
        self.assertEqual(staged.read_bytes(), (self.source.checkpoint / self.source.inputs[0].name).read_bytes())
        return staged

    def test_resume_after_journal_commit_before_source_unlink(self):
        self.canonical.HASH_CHUNK_BYTES = self.source.inputs[0].size - 1
        self.interrupt_after_journal_commit()
        path = self.root / "journal.json"
        original = path.read_bytes()
        journal = json.loads(original)
        row, = journal["committed"]
        first = self.source.inputs[0]
        self.assertNotEqual(row[0], first.checksum)
        self.assertEqual(row[0], self.canonical.sha256(self.source.checkpoint / first.name))
        row[0] = first.checksum
        path.write_bytes(stream.json_bytes(journal))
        self.assert_resume_refused_without_side_effects("committed input digest mismatch")
        path.write_bytes(original)
        self.assertEqual(self.standalone_convert(self.root, self.source), 0)
        self.assertEqual(self.source.downloads, [(item.name, 0) for item in self.source.inputs])
        self.assertEqual([count for count, _ in self.source.observations], [0, 0, 0])
        self.assertFalse(list(self.root.glob("source-*.part")))
        self.assert_manifest_matches_uninterrupted()

    def test_resume_after_two_released_chunked_shards_matches_uninterrupted(self):
        first, second, third = self.source.inputs
        self.canonical.HASH_CHUNK_BYTES = 257
        self.assertGreater(min(first.size, second.size), self.canonical.HASH_CHUNK_BYTES)
        offset = self.interrupt_during_transfer(2)
        artifact = self.root / "artifact"
        payloads = {path: path.read_bytes() for path in artifact.iterdir()}
        download = self.source.download

        def fragmented_download(item, start):
            response = download(item, start)
            read = response.read

            def read_fragment(size=-1):
                self.assertTrue(0 < size <= stream.BLOCK)
                self.assertEqual(list(self.root.glob("source-*.part")), [self.root / "source-002.part"])
                return read(min(size, 71))

            if item != third:
                response.read = read_fragment
            return response

        stdout = io.StringIO()
        with (patch.object(stream, "BLOCK", 113),
              patch.object(self.source, "download", side_effect=fragmented_download),
              patch.object(stream.Conversion, "convert_shard", autospec=True,
                           side_effect=stream.Conversion.convert_shard) as convert_shard,
              redirect_stdout(stdout)):
            self.assertEqual(self.standalone_convert(self.root, self.source), 0)
        convert_shard.assert_called_once()
        self.assertEqual(convert_shard.call_args.args[1], third)
        self.assertEqual(self.source.downloads[3:], [(first.name, 0), (second.name, 0), (third.name, offset)])
        self.assertEqual([count for count, _ in self.source.observations[3:]], [1, 1, 1])
        self.assertEqual([line for line in stdout.getvalue().splitlines() if line.startswith("Re-authenticat")], [
            f"Re-authenticated released source shard 1/2: {first.name} ({first.size} bytes streamed)",
            f"Re-authenticated released source shard 2/2: {second.name} ({second.size} bytes streamed)",
            f"Re-authentication total: {first.size + second.size} bytes streamed",
        ])
        self.assertEqual(payloads, {path: path.read_bytes() for path in payloads})
        self.assert_manifest_matches_uninterrupted()

    def test_resume_refuses_released_source_with_wrong_lfs_checksum(self):
        self.canonical.HASH_CHUNK_BYTES = 257
        first = self.source.inputs[0]
        self.interrupt_during_transfer(1)
        upstream = self.source.checkpoint / first.name
        raw = upstream.read_bytes()
        upstream.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        path = self.root / "journal.json"
        journal = json.loads(path.read_bytes())
        journal["committed"][0][0] = self.canonical.sha256(upstream)
        path.write_bytes(stream.json_bytes(journal))
        self.assert_resume_refused_without_side_effects("re-authenticated source sha256 mismatch", first)

    def test_resume_refuses_truncated_released_source(self):
        self.canonical.HASH_CHUNK_BYTES = 257
        first = self.source.inputs[0]
        self.interrupt_during_transfer(1)
        self.source.interrupt = first.name
        self.assert_resume_refused_without_side_effects("short re-authentication download", first)

    def test_resume_refuses_released_source_on_network_failure(self):
        self.canonical.HASH_CHUNK_BYTES = 257
        first = self.source.inputs[0]
        self.interrupt_during_transfer(1)
        download = self.source.download

        def failing_download(item, start):
            response = download(item, start)
            response.read = Mock(side_effect=http.client.IncompleteRead(b"partial"))
            return response

        with patch.object(self.source, "download", side_effect=failing_download):
            self.assert_resume_refused_without_side_effects("re-authentication download failed", first)

    def test_resume_refuses_incomplete_retained_chunked_source(self):
        self.canonical.HASH_CHUNK_BYTES = self.source.inputs[0].size - 1
        staged = self.interrupt_after_journal_commit()
        staged.write_bytes(staged.read_bytes()[:-1])
        self.assert_resume_refused_without_side_effects("cannot authenticate committed input digest without a complete source")

    def test_resume_refuses_chunked_digest_from_changed_retained_source(self):
        self.canonical.HASH_CHUNK_BYTES = self.source.inputs[0].size - 1
        staged = self.interrupt_after_journal_commit()
        raw = staged.read_bytes()
        staged.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        path = self.root / "journal.json"
        journal = json.loads(path.read_bytes())
        journal["committed"][0][0] = self.canonical.sha256(staged)
        path.write_bytes(stream.json_bytes(journal))
        self.assert_resume_refused_without_side_effects("retained source sha256 mismatch")

    def test_completed_resume_reuses_verified_payload_and_manifest(self):
        self.assertEqual(self.standalone_convert(self.root, self.source), 0)
        path = self.root / "artifact/manifest.json"
        before = path.read_bytes()
        self.assertEqual(self.standalone_convert(self.root, self.source), 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.source.downloads, [(item.name, 0) for item in self.source.inputs] * 2)

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
                   Reply(b"xyz", "bytes 13-15/16"), Reply(b"xyz", "bytes 12-15/16"),
                   io.BytesIO(header + b"abcxyz")]
        with patch.object(stream.urllib.request, "urlopen", side_effect=replies) as open_http:
            self.assertEqual(source.header(item), header)
            with source.download(item, 13) as payload:
                self.assertEqual(payload.read(), b"xyz")
            with self.assertRaisesRegex(ValueError, "exact byte range"):
                source.download(item, 13)
            with source.download(item, 0) as payload:
                self.assertEqual(payload.read(), header + b"abcxyz")
        self.assertEqual([call.args[0].get_header("Range") for call in open_http.call_args_list],
                         ["bytes=0-7", "bytes=8-9", "bytes=13-15", "bytes=13-15", None])
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
            pin = stream._run_conversion(root, plan, reserve=0)
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
