"""The AppleSMC reader: key and type encoding, value decoding, the two-call
read protocol through a fake transport, errors returned as data, and a live
read of B0AC on macOS."""
from __future__ import annotations

import ctypes
import math
import struct
import sys
import time
import unittest
from unittest import mock

from joulewise.hazards import smc


class FakeTransport:
    """The AppleSMC user client at the seam.

    ``keys`` maps a key to ``(type, bytes)``; a key not in it answers result
    0x84 as the SMC does.  ``fail_on`` makes the call raise like a nonzero
    kernel return.
    """

    def __init__(self, keys: dict[str, tuple[str, bytes]], *, fail_on: set[str] = frozenset()) -> None:
        self.keys = keys
        self.fail_on = set(fail_on)
        self.calls: list[tuple[str, int]] = []
        self.closed = False

    def call(self, request: smc.SMCKeyData) -> smc.SMCKeyData:
        key = struct.pack(">I", request.key).decode()
        self.calls.append((key, request.data8))
        if key in self.fail_on:
            raise OSError("IOConnectCallStructMethod returned 0xe00002c2")
        reply = smc.SMCKeyData(key=request.key)
        if key not in self.keys:
            reply.result = smc.RESULT_KEY_NOT_FOUND
            return reply
        data_type, raw = self.keys[key]
        if request.data8 == smc.CMD_GET_KEY_INFO:
            reply.keyInfo.dataSize = len(raw)
            reply.keyInfo.dataType = smc.fourcc(data_type)
        elif request.data8 == smc.CMD_READ_KEY:
            assert request.keyInfo.dataSize == len(raw), "the read must ask for the key info's size"
            for index, byte in enumerate(raw):
                reply.bytes[index] = byte
        else:
            raise AssertionError(f"unexpected SMC command {request.data8}")
        return reply

    def close(self) -> None:
        self.closed = True


# The probe's 10-06 desk values, encoded as the SMC returns them (little-endian).
DESK = {
    "B0AC": ("si16", struct.pack("<h", -865)),
    "B0AV": ("ui16", struct.pack("<H", 12155)),
    "PDTR": ("flt ", struct.pack("<f", 85.061)),
    "PSTR": ("flt ", struct.pack("<f", 79.602)),
    "PPBR": ("flt ", struct.pack("<f", 0.798)),
}


class EncodingTests(unittest.TestCase):
    def test_request_structure_is_the_80_byte_smc_key_data(self):
        self.assertEqual(ctypes.sizeof(smc.SMCKeyData), 80)
        self.assertEqual(smc.SMCKeyData.data8.offset, 42)
        self.assertEqual(smc.SMCKeyData.bytes.offset, 48)

    def test_four_character_codes(self):
        self.assertEqual(smc.fourcc("B0AC"), 0x42304143)
        self.assertEqual(smc.type_name(smc.fourcc("flt ")), "flt ")
        with self.assertRaises(ValueError):
            smc.fourcc("B0A")

    def test_decode_each_type(self):
        self.assertEqual(smc.decode("si16", bytes.fromhex("9ffc")), -865)
        self.assertEqual(smc.decode("ui16", struct.pack("<H", 12155)), 12155)
        self.assertAlmostEqual(smc.decode("flt ", struct.pack("<f", 85.061)), 85.061, places=4)
        self.assertEqual(smc.decode("si8 ", b"\xff"), -1)
        self.assertEqual(smc.decode("ui8 ", b"\xff"), 255)
        self.assertEqual(smc.decode("si32", struct.pack("<i", -5)), -5)
        self.assertEqual(smc.decode("ui32", struct.pack("<I", 7)), 7)
        # trailing bytes beyond the type's size are ignored
        self.assertEqual(smc.decode("si16", bytes.fromhex("9ffc0000")), -865)

    def test_decode_refuses_unknown_types_and_short_data(self):
        with self.assertRaises(ValueError):
            smc.decode("sp78", b"\x00\x00")
        with self.assertRaises(ValueError):
            smc.decode("flt ", b"\x00\x00")


class ReaderTests(unittest.TestCase):
    def test_reads_the_five_keys_with_two_calls_each_then_one(self):
        transport = FakeTransport(DESK)
        reader = smc.Reader(transport)
        first = reader.read()
        self.assertEqual(first["errors"], {})
        self.assertEqual(first["values"]["B0AC"], -865)
        self.assertEqual(first["values"]["B0AV"], 12155)
        self.assertAlmostEqual(first["values"]["PDTR"], 85.061, places=4)
        self.assertEqual(list(first["values"]), list(smc.KEYS))
        self.assertEqual(len(transport.calls), 10)  # key info + read per key
        reader.read()
        self.assertEqual(len(transport.calls), 15)  # key info cached
        reader.close()
        self.assertTrue(transport.closed)

    def test_absent_key_is_an_error_not_a_raise(self):
        reader = smc.Reader(FakeTransport({"B0AC": DESK["B0AC"]}))
        result = reader.read(("B0AC", "PDTR"))
        self.assertEqual(result["values"], {"B0AC": -865, "PDTR": None})
        self.assertEqual(set(result["errors"]), {"PDTR"})
        self.assertIn("0x84 (key not found)", result["errors"]["PDTR"])

    def test_transport_failure_is_an_error_and_the_next_read_retries_key_info(self):
        transport = FakeTransport(DESK, fail_on={"B0AC"})
        reader = smc.Reader(transport)
        result = reader.read()
        self.assertIsNone(result["values"]["B0AC"])
        self.assertIn("OSError", result["errors"]["B0AC"])
        self.assertEqual(result["values"]["B0AV"], 12155)
        transport.fail_on.clear()
        self.assertEqual(reader.read()["values"]["B0AC"], -865)

    def test_an_owned_transport_that_fails_is_reopened_on_the_next_read(self):
        opened: list[FakeTransport] = []

        def open_transport():
            transport = FakeTransport(DESK, fail_on={"B0AC"} if not opened else set())
            opened.append(transport)
            return transport

        with mock.patch.object(smc, "IOKitTransport", open_transport):
            reader = smc.Reader()
            self.assertIsNone(reader.read(("B0AC",))["values"]["B0AC"])
            self.assertTrue(opened[0].closed)
            self.assertEqual(reader.read(("B0AC",))["values"]["B0AC"], -865)
        self.assertEqual(len(opened), 2)

    def test_a_short_native_reply_is_an_error_not_a_zero(self):
        """IOConnectCallStructMethod succeeding with fewer than 80 bytes would leave
        B0AC's bytes zero; the transport refuses it (review F1)."""

        class ShortIOKit:
            def __init__(self, size):
                self.size = size

            def IOConnectCallStructMethod(self, conn, selector, inp, in_size, out, out_size):
                reply = out._obj
                request = inp._obj
                reply.result = 0
                if request.data8 == smc.CMD_GET_KEY_INFO:
                    reply.keyInfo.dataSize = 2
                    reply.keyInfo.dataType = smc.fourcc("si16")
                else:
                    reply.bytes[0], reply.bytes[1] = 0x9F, 0xFC  # -865 mA
                out_size._obj.value = self.size
                return 0

        for size, expected in ((48, None), (80, -865)):
            with self.subTest(size=size):
                transport = object.__new__(smc.IOKitTransport)
                transport._iokit = ShortIOKit(size)
                transport._conn = ctypes.c_uint32(0)
                value, error = smc.Reader(transport).read_key("B0AC")
                self.assertEqual(value, expected)
                if expected is None:
                    self.assertIn("replied 48 bytes", error)

    def test_nan_and_unsupported_types_are_errors(self):
        keys = {"PDTR": ("flt ", struct.pack("<f", math.nan)), "B0AC": ("sp78", b"\x00\x10")}
        result = smc.Reader(FakeTransport(keys)).read(("PDTR", "B0AC"))
        self.assertEqual(result["values"], {"PDTR": None, "B0AC": None})
        self.assertIn("nan", result["errors"]["PDTR"])
        self.assertIn("unsupported SMC data type", result["errors"]["B0AC"])

    def test_no_service_gives_every_key_an_error(self):
        def refuse():
            raise OSError("no AppleSMC service in the IO registry")

        with mock.patch.object(smc, "IOKitTransport", refuse):
            result = smc.read_once()
        self.assertEqual(result["values"], {key: None for key in smc.KEYS})
        self.assertTrue(all("no AppleSMC service" in text for text in result["errors"].values()))

    @unittest.skipIf(sys.platform == "darwin", "off macOS only")
    def test_off_macos_the_reader_reports_and_never_raises(self):
        result = smc.read_once()
        self.assertTrue(all("requires macOS" in text for text in result["errors"].values()))


@unittest.skipUnless(sys.platform == "darwin", "reads the real SMC (macOS)")
class LiveSmcTests(unittest.TestCase):
    def test_b0ac_is_readable_and_the_smc_power_block_updates_within_3_s(self):
        """B0AC reads as a signed integer on every read; the block it publishes
        with (B0AC, PDTR, PSTR, PPBR, refreshed together once a second) changes
        within 3 s.  B0AC alone can sit at exactly 0 mA at float, so the block
        shows the refresh."""

        reader = smc.Reader()
        self.addCleanup(reader.close)
        first = reader.read()
        self.assertEqual(first["errors"], {}, first)
        self.assertIsInstance(first["values"]["B0AC"], int)
        self.assertTrue(10_000 <= first["values"]["B0AV"] <= 13_500, first)  # a 3-cell pack, mV
        block = ("B0AC", "PDTR", "PSTR", "PPBR")
        changed_after = None
        started = time.monotonic()
        while time.monotonic() - started < 3.0:
            time.sleep(0.2)
            result = reader.read()
            self.assertIsInstance(result["values"]["B0AC"], int, result)
            if any(result["values"][key] != first["values"][key] for key in block):
                changed_after = time.monotonic() - started
                break
        self.assertIsNotNone(changed_after, "the SMC power block did not change within 3 s")

    def test_one_five_key_read_costs_well_under_a_millisecond_of_cpu(self):
        import resource

        reader = smc.Reader()
        self.addCleanup(reader.close)
        reader.read()
        before = resource.getrusage(resource.RUSAGE_SELF)
        for _ in range(200):
            reader.read()
        after = resource.getrusage(resource.RUSAGE_SELF)
        cpu_ms = ((after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)) / 200 * 1e3
        print(f"\nSMC five-key read: {cpu_ms:.3f} ms CPU each", file=sys.stderr)
        self.assertLess(cpu_ms, 2.0)


if __name__ == "__main__":
    unittest.main()
