"""Lead-only Mac15,9 validation; explicit live opt-in and importability gates."""
import importlib.util
import os
import struct
import tempfile
import unittest
from pathlib import Path

from joulewise.align.apple import smc_enumeration, smc_reader
from tests.live_hw import LiveHardwareTestCase


class NativeSmcTests(LiveHardwareTestCase):
    def test_native_big_endian_count_and_index_inventory(self):
        reader = smc_reader.Reader()
        self.addCleanup(reader.close)
        count, error = reader.read_key("#KEY")
        self.assertIsNone(error)
        raw = bytes.fromhex(reader.raw["#KEY"]["raw_hex"])
        self.assertEqual(count, struct.unpack(">I", raw)[0])
        self.assertTrue(0 < count <= 65536)
        inventory = reader.enumerate_sensors()
        self.assertTrue(inventory["complete"], inventory["errors"])
        self.assertTrue(any(s["unit"] == "degC" for s in inventory["keys"]))


@unittest.skipUnless(importlib.util.find_spec("mlx") is not None, "MLX is not importable")
class NativeGpuTests(LiveHardwareTestCase):
    def test_native_worker_starts_from_other_directory_and_is_reaped(self):
        load = smc_enumeration.GpuLoad(2)
        original = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.chdir(tmp)
                load.start()
                load.check()
                load.stop()
                self.assertIsNotNone(load.process.poll())
        finally:
            os.chdir(original)
            if load.process is not None and load.process.poll() is None:
                load.stop()
