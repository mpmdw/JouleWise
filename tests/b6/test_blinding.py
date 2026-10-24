import contextlib
import io
import json
import math
import multiprocessing
import secrets
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import blinding


def factor_child(directory, gate, queue):
    gate.wait(10)
    queue.put(blinding.factor(directory, "synthetic-key"))


class BlindingTests(unittest.TestCase):
    def test_first_key_publication_never_exposes_incomplete_bytes(self):
        for failure in ("dump", "link"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp) / "blinding"
                target = directory / "pack.json"
                module = blinding.json if failure == "dump" else blinding.os
                def fail(*args, **kwargs):
                    self.assertFalse(target.exists())
                    raise OSError("interrupted key publication")
                with patch.object(module, failure, side_effect=fail):
                    with self.assertRaisesRegex(OSError, "interrupted key publication"):
                        blinding.pack_factor(directory)
                self.assertFalse(target.exists())
                self.assertEqual(list(directory.iterdir()), [])
                value = blinding.pack_factor(directory)
                self.assertEqual(json.loads(target.read_bytes())["factor"], value)
                self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_twelve_bytes_drafts_share_custody_replication_paths_unchanged(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            records = Path(tmp)
            paths = {blinding.key_directory(records, doc["pack_id"], doc)
                     for path in sorted((root / "configs/b6/packs").glob("bytes-*/registration.json"))
                     for doc in [json.loads(path.read_text())]}
            self.assertEqual(paths, {records / "bytes/blinding"})
            for pack in ("alpha", "beta", "gamma"):
                self.assertEqual(blinding.key_directory(records, pack, {}), records / pack / "blinding")
            for group in ("../escape", "/outside", ".", ".."):
                with self.assertRaises(ValueError):
                    blinding.key_directory(records, "pack", {"blinding_group": group})

    def test_binding_merges_names_and_preserves_old_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "blinding"
            blinding.factor(directory, "first")
            first = blinding._config_filename("first")
            one = blinding.bind_session_keys(directory, "s", {"pack.json", first})
            blinding.factor(directory, "second")
            second = blinding._config_filename("second")
            merged = blinding.bind_session_keys(directory, "s", {"pack.json", second})
            self.assertEqual(merged, {**one, second: __import__("hashlib").sha256((directory / second).read_bytes()).hexdigest()})
            self.assertEqual(blinding.bind_session_keys(directory, "s", {first}), merged)
            (directory / first).write_text("changed bytes")
            with self.assertRaisesRegex(ValueError, "key bytes changed"):
                blinding.bind_session_keys(directory, "s", {first})

    def test_concurrent_session_merges_keep_both_name_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "blinding"
            names = []
            for key in ("first", "second"):
                blinding.factor(directory, key)
                names.append({"pack.json", blinding._config_filename(key)})
            # CI runs its shard program on stdin, which spawn cannot reopen.
            # Import production directly so children need no test-module/main import.
            gate = Path(tmp) / "go"
            program = """
import json
from pathlib import Path
import sys
import time
from joulewise.b6 import blinding
directory, names, gate, ready = sys.argv[1:]
Path(ready).touch()
deadline = time.monotonic() + 10
while not Path(gate).exists():
    if time.monotonic() >= deadline:
        raise TimeoutError("binding barrier was not released")
    time.sleep(.01)
blinding.bind_session_keys(Path(directory), "same-session", set(json.loads(names)))
"""
            workers = []
            try:
                ready = [Path(tmp) / f"ready-{index}" for index in range(len(names))]
                for group, marker in zip(names, ready):
                    workers.append(subprocess.Popen(
                        [sys.executable, "-B", "-c", program, str(directory), json.dumps(sorted(group)),
                         str(gate), str(marker)], cwd=Path(__file__).resolve().parents[2],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
                deadline = time.monotonic() + 10
                while not all(marker.exists() for marker in ready):
                    if time.monotonic() >= deadline or any(worker.poll() is not None for worker in workers):
                        self.fail("binding children failed to reach barrier: " + repr([
                            worker.communicate(timeout=1) for worker in workers if worker.poll() is not None]))
                    time.sleep(.01)
                gate.touch()
                for worker in workers:
                    stdout, stderr = worker.communicate(timeout=15)
                    self.assertEqual(worker.returncode, 0, stdout + stderr)
            finally:
                for worker in workers:
                    if worker.poll() is None:
                        worker.kill()
                    worker.communicate()
            doc = json.loads((directory.parent / "blinding-sessions/same-session.json").read_bytes())
            self.assertEqual(set(doc["key_sha256"]), set.union(*names))

    def test_interrupted_binding_publication_leaves_no_partial_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "blinding"
            blinding.factor(directory, "first")
            names = {"pack.json", blinding._config_filename("first")}
            target = directory.parent / "blinding-sessions/s.json"
            with patch.object(blinding.os, "link", side_effect=OSError("interrupted publish")):
                with self.assertRaisesRegex(OSError, "interrupted publish"):
                    blinding.bind_session_keys(directory, "s", names)
            self.assertFalse(target.exists())
            self.assertFalse(list(target.parent.glob(".s.json.*")))
            initial = blinding.bind_session_keys(directory, "s", names)
            raw = target.read_bytes()
            blinding.factor(directory, "second")
            with patch.object(blinding.os, "replace", side_effect=OSError("interrupted merge")):
                with self.assertRaises(OSError):
                    blinding.bind_session_keys(directory, "s", names | {blinding._config_filename("second")})
            self.assertEqual(target.read_bytes(), raw)
            self.assertEqual(blinding.bind_session_keys(directory, "s", names), initial)

    def test_ranges_over_ten_thousand_draws(self):
        # Distribution support is the registered blinding range, not an agreement tolerance.
        for bounds in (blinding.PACK_RANGE, blinding.CONFIG_RANGE):
            self.assertTrue(all(bounds[0] <= blinding._draw(bounds) <= bounds[1] for _ in range(10000)),
                            "a synthetic draw was outside its distribution")

    def test_stored_draw_and_no_stdout(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as output:
            directory = Path(tmp) / "pack" / "blinding"
            first = blinding.factor(directory, "synthetic-key", session_id="desk")
            # Exact: identical stored key bytes must reproduce the identical factor.
            self.assertTrue(first == blinding.factor(directory, "synthetic-key"), "stored draw changed")
            self.assertEqual(output.getvalue(), "")
            stored = json.loads((directory / "pack.json").read_text())
            self.assertEqual(stored["pack_id"], "pack")
            self.assertEqual(stored["drawn_by_session"], "desk")
            # Registered support bounds, rather than an agreement tolerance.
            self.assertTrue(blinding.PACK_RANGE[0] <= stored["factor"] <= blinding.PACK_RANGE[1])
            configs = list(directory.glob("config-*.json"))
            self.assertEqual(len(configs), 1)
            config = json.loads(configs[0].read_text())
            # Registered support bounds, rather than an agreement tolerance.
            self.assertTrue(blinding.CONFIG_RANGE[0] <= config["factor"] <= blinding.CONFIG_RANGE[1])

    def test_stored_factor_reads_only_and_names_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "keys"
            with self.assertRaisesRegex(ValueError, str(directory / "pack.json")):
                blinding.stored_factor(directory, "key")
            self.assertFalse(directory.exists())
            value = blinding.factor(directory, "key")
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            with patch.object(blinding, "_draw", side_effect=AssertionError("release drew a key")):
                self.assertEqual(blinding.stored_factor(directory, "key"), value)
                with self.assertRaisesRegex(ValueError, "config-.*json"):
                    blinding.stored_factor(directory, "wrong-key")
            self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
            config = next(directory.glob("config-*.json"))
            config.write_text('{"factor":"SECRET_VALUE"}')
            with self.assertRaises(ValueError) as raised:
                blinding.stored_factor(directory, "key")
            self.assertIn(str(config), str(raised.exception))
            self.assertNotIn("SECRET_VALUE", str(raised.exception))

    def test_corrupt_key_decode_retry_is_bounded_and_names_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pack.json"
            for content in ("", "{broken"):
                path.write_text(content)
                # Exact policy boundary on a controlled clock: one retry before
                # the configured deadline, then stop at that deadline. No wall-time bar.
                with patch.object(blinding, "time") as clock:
                    clock.monotonic.side_effect = [0, 0, blinding.DECODE_RETRY_TIMEOUT_S]
                    with self.assertRaises(ValueError) as raised:
                        blinding.pack_factor(tmp)
                    self.assertEqual(clock.monotonic.call_count, 3)
                    clock.sleep.assert_called_once()
                self.assertIn(str(path), str(raised.exception))
                self.assertEqual(path.read_text(), content)

    def test_racing_first_draw_one_file_one_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "pack" / "blinding"
            # "spawn" re-imports __main__ from its file; the shard runner (CI and the
            # local method) feeds the test program on stdin (main path "<stdin>"), which
            # kills spawn children at startup (precedent: tests/test_agent_census_concurrency.py,
            # PR #371). These children only draw or append, so a forked child is safe.
            ctx = multiprocessing.get_context("fork" if "fork" in multiprocessing.get_all_start_methods() else "spawn")
            gate, queue = ctx.Event(), ctx.Queue()
            processes = [ctx.Process(target=factor_child, args=(directory, gate, queue)) for _ in range(2)]
            try:
                for process in processes:
                    process.start()
                gate.set()
                for process in processes:
                    process.join(15)
                    self.assertEqual(process.exitcode, 0)
                first, second = queue.get(timeout=2), queue.get(timeout=2)
                # Exact: both processes must use the single persisted key.
                self.assertTrue(first == second, "racing draws did not converge")
                self.assertEqual(len(list(directory.glob("pack.json"))), 1)
                self.assertEqual(len(list(directory.glob("config-*.json"))), 1)
            finally:
                for process in processes:
                    if process.is_alive():
                        process.kill()
                    process.join()
                queue.close()
                queue.join_thread()

    def test_apply_unblind_roundtrip_squared_and_unchanged_fields(self):
        row = {"gross_energy_j": 1.234, "idle_power_w": .4, "variance_j2": .25, "idle_variance_of_mean_w2": .125,
               "dur_decode_s": 2, "emitted_tokens": 7, "failed_energy_j": "", "absent_energy_j": None}
        scale = 1.117
        applied = blinding.apply(row, scale)
        # Variance has no printed J^2 or W^2 half-width. COMMON uses
        # 1e-6 relative, floor 1e-6 J^2 for energy variance (noise x 1e6
        # at .25 J^2 is 5.5e-11 J^2), and floor 1e-6 W^2 for idle
        # variance (noise x 1e6 at .125 W^2 is 2.75e-11 W^2).
        self.assertTrue(math.isclose(applied["variance_j2"], row["variance_j2"] * scale * scale,
                                     rel_tol=1e-6, abs_tol=1e-6))
        self.assertTrue(math.isclose(applied["idle_variance_of_mean_w2"], row["idle_variance_of_mean_w2"] * scale * scale,
                                     rel_tol=1e-6, abs_tol=1e-6))
        recovered = blinding.unblind(applied, scale)
        # Energy's 1.234e-6 J bar is above noise x 1e6 (2.7e-10 J) and
        # below 1% of the printed 0.013 J half-width (1.3e-4 J). For the
        # fields without half-widths, COMMON gives 1e-6 relative with floors
        # 1e-6 W, 1e-6 J^2 and 1e-6 W^2 respectively; each exceeds noise x
        # 1e6 at these .125-.4 unit fixture scales (at most 8.8e-11 units).
        self.assertTrue(all(math.isclose(recovered[k], v, rel_tol=1e-6, abs_tol=1e-6)
                            for k, v in row.items() if isinstance(v, float)),
                        "synthetic offset roundtrip failed")
        for key in ("dur_decode_s", "emitted_tokens", "failed_energy_j", "absent_energy_j"):
            self.assertEqual(applied[key], row[key])

    def test_configuration_keys_null_quads_and_gamma_models(self):
        config = {"run_metadata": {"tags": ["df-condition=null-family"]}}
        self.assertEqual(blinding.configuration_key(config), "null-family")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(blinding.factor(tmp, blinding.configuration_key(config)) ==
                            blinding.factor(tmp, blinding.configuration_key(config)), "null quad factors differ")
            small = {"model": {"name": "small"}, "workload_profile": {"name": "query", "output_tokens": 256}}
            large = {**small, "model": {"name": "large"}}
            self.assertNotEqual(blinding.configuration_key(small), blinding.configuration_key(large))
            self.assertTrue(blinding.factor(tmp, blinding.configuration_key(small)) !=
                            blinding.factor(tmp, blinding.configuration_key(large)), "configuration draws coincide")
