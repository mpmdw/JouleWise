import contextlib
import io
import json
import math
import multiprocessing
import secrets
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.b6 import blinding


def factor_child(directory, gate, queue):
    gate.wait(10)
    queue.put(blinding.factor(directory, "synthetic-key"))


class BlindingTests(unittest.TestCase):
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
        # No printed half-width: COMMON 1e-6 relative / absolute J2 or W2
        # near zero, above 1e6 x double noise (2.2e-16 -> 2.2e-10 relative).
        self.assertTrue(math.isclose(applied["variance_j2"], row["variance_j2"] * scale * scale,
                                     rel_tol=1e-6, abs_tol=1e-6))
        self.assertTrue(math.isclose(applied["idle_variance_of_mean_w2"], row["idle_variance_of_mean_w2"] * scale * scale,
                                     rel_tol=1e-6, abs_tol=1e-6))
        recovered = blinding.unblind(applied, scale)
        # Roundtrip has no printed half-width: 1e-6 relative / absolute in the
        # field's unit near zero, above 1e6 x 2.2e-16 = 2.2e-10 relative noise.
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
