"""Stage R: the targeted extractor equals plistlib, the stream reduction is bound to its raw bytes,
and the cache never serves a reduction for other bytes. Synthetic frames only."""
import hashlib
import math
import plistlib
import random
import unittest

from .support import rc, synth, temp_dir


def random_frame(k):
    rng = random.Random(k)
    return synth.frame_bytes(
        elapsed_ns=rng.randrange(1, 10**9), timestamp_s=synth.EPOCH0_S + rng.randrange(10**7),
        gpu_mw=rng.choice([rng.random() * 3e4, rng.randrange(30000), 0.0]), cpu_mw=rng.randrange(5000),
        ane_mw=rng.random(), pressure=rng.choice(["Nominal", "Moderate", "Heavy", "Trapping", "Sleeping", "Other"]),
        dvfm=[(rng.choice([rng.randrange(300, 1500), rng.random() * 1500]), rng.random())
              for _ in range(rng.randrange(0, 6))], n_tasks=rng.randrange(0, 40), seed=k)


class ExtractorEqualityTests(unittest.TestCase):
    def test_fast_equals_plistlib_on_randomized_frames(self):
        for k in range(150):
            frame = random_frame(k)
            fast, slow = rc.fast_frame(frame), rc.slow_frame(frame)
            self.assertIsNotNone(fast, k)
            # repr equality: identical floats bit for bit, NaN clocks included.
            self.assertEqual(repr(fast), repr(slow), k)

    def test_hand_values(self):
        frame = synth.frame_bytes(elapsed_ns=100_000_000, timestamp_s=synth.EPOCH0_S, gpu_mw=12000.0,
                                  cpu_mw=1500.0, ane_mw=3.0, pressure="Heavy", dvfm=((400, 0.25), (1200, 0.5)))
        # active = 25 ms + 50 ms; clock = (400*25e6 + 1200*50e6) / 75e6 = 2800/3 MHz.
        self.assertEqual(rc.fast_frame(frame), (100_000_000, 1500.0, 12000.0, 3.0, 2, 75_000_000,
                                                math.fsum([400 * 25e6, 1200 * 50e6]) / 75e6, synth.EPOCH0_S))

    def test_decoy_keys_at_other_paths_are_ignored(self):
        doc = synth.frame_dict(elapsed_ns=5, timestamp_s=synth.EPOCH0_S, gpu_mw=7.0, n_tasks=3)
        doc["tasks"][0]["processor"] = {"gpu_power": 999.0}
        doc["zzz"] = {"elapsed_ns": 1, "gpu": {"dvfm_states": []}}
        frame = plistlib.dumps(doc, fmt=plistlib.FMT_XML)
        self.assertEqual(rc.fast_frame(frame)[2], 7.0)
        self.assertEqual(repr(rc.fast_frame(frame)), repr(rc.slow_frame(frame)))

    def test_duplicate_key_takes_the_last_value_like_plistlib(self):
        frame = synth.frame_bytes(elapsed_ns=5, timestamp_s=synth.EPOCH0_S, gpu_mw=7.0, n_tasks=0)
        dup = frame.replace(b"<key>thermal_pressure</key>",
                            b"<key>elapsed_ns</key><integer>9</integer><key>thermal_pressure</key>", 1)
        self.assertEqual(rc.fast_frame(dup)[0], 9)
        self.assertEqual(repr(rc.fast_frame(dup)), repr(rc.slow_frame(dup)))

    def test_unhandled_constructs_go_to_plistlib(self):
        frame = synth.frame_bytes(elapsed_ns=5, timestamp_s=synth.EPOCH0_S, gpu_mw=7.0, n_tasks=2)
        cases = [frame.replace(b"<key>tasks</key>", b"<!-- note --><key>tasks</key>"),
                 frame.replace(b"<string>Nominal</string>", b"<string>Nominal &amp; ok</string>"),
                 frame.replace(b"<key>gpu</key>", b"<key>g&#112;u</key>"),
                 frame.replace(b"<integer>5</integer>", b"<real>5</real>", 1)]
        for case in cases:
            self.assertIsNone(rc.fast_frame(case), case[:0])
        # The entity-named key IS the gpu dict to plistlib; the fast path must not have guessed.
        self.assertEqual(rc.slow_frame(cases[2])[5], rc.slow_frame(frame)[5])

    def test_unusable_frames_raise_in_the_reference(self):
        frame = synth.frame_bytes(elapsed_ns=5, timestamp_s=synth.EPOCH0_S, gpu_mw=7.0, n_tasks=0)
        for bad in (frame[:-40], frame.replace(b"<key>gpu_power</key>", b"<key>gpu_powr</key>"),
                    frame.replace(b"<integer>5</integer>", b"<integer>-5</integer>", 1)):
            self.assertIsNone(rc.fast_frame(bad))
            with self.assertRaises(ValueError):
                rc.slow_frame(bad)


class StreamTests(unittest.TestCase):
    def write(self, frames, tail=b""):
        path = temp_dir(self) / "raw.plist"
        path.write_bytes(b"\x00".join(frames) + b"\x00" + tail)
        return path

    def test_stream_columns_offsets_and_digest(self):
        tpl = synth.FrameTemplate(n_tasks=1)
        frames = [tpl.fill(100_000_000 + i, synth.EPOCH0_S + i, 1000.0 * i) for i in range(30)]
        frames[7] = frames[7].replace(b"<key>tasks</key>", b"<!--x--><key>tasks</key>")
        path = self.write(frames)
        red = rc.reduce_stream(path, chunk_bytes=4096)  # many chunk boundaries inside frames
        self.assertEqual(red["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(red["counts"], {"frames": 30, "fast": 29, "fallback": 1, "bytes": path.stat().st_size})
        self.assertIsNone(red["error"])
        cols = red["columns"]
        self.assertEqual(list(cols["gpu_mw"]), [1000.0 * i for i in range(30)])
        # The first sample ends at the anchor; each later end adds its own elapsed.
        self.assertEqual(cols["end_offset_ns"][0], 0)
        self.assertEqual(cols["end_offset_ns"][3], (100_000_001) + (100_000_002) + (100_000_003))

    def test_truncated_final_frame_is_an_error_not_a_dropped_sample(self):
        tpl = synth.FrameTemplate(n_tasks=0)
        frames = [tpl.fill(100_000_000, synth.EPOCH0_S, 5.0) for _ in range(3)]
        path = self.write(frames, tail=frames[0][:500])
        red = rc.reduce_stream(path)
        self.assertIsNotNone(red["error"])

    def test_cache_round_trip_and_binding(self):
        tpl = synth.FrameTemplate(n_tasks=0)
        path = self.write([tpl.fill(100_000_000, synth.EPOCH0_S + i, 5.0 + i) for i in range(10)])
        cache = temp_dir(self)
        miss = rc.reduce_member_raw(path, cache)
        hit = rc.reduce_member_raw(path, cache)
        self.assertEqual((miss["cache"], hit["cache"]), ("miss", "hit"))
        self.assertEqual(rc.column_stats(miss["columns"]), rc.column_stats(hit["columns"]))
        cached = next(cache.iterdir())
        # A cached file for other raw bytes is never served.
        self.assertIsNone(rc.read_reduced(cached, "0" * 64))
        # A corrupted body is never served; the next run recomputes.
        data = bytearray(cached.read_bytes())
        data[-1] ^= 1
        cached.write_bytes(bytes(data))
        self.assertEqual(rc.reduce_member_raw(path, cache)["cache"], "miss")
        # Changed raw bytes give a different key, hence a miss.
        path.write_bytes(path.read_bytes() + tpl.fill(100_000_000, synth.EPOCH0_S, 1.0) + b"\x00")
        self.assertEqual(rc.reduce_member_raw(path, cache)["cache"], "miss")

    def test_column_stats_hand(self):
        cols = {name: rc.array(code) for name, code in rc.COLUMNS}
        for v in (1.0, 2.0, 4.0):
            cols["gpu_mw"].append(v)
        for name, code in rc.COLUMNS:
            if name != "gpu_mw":
                for _ in range(3):
                    cols[name].append(math.nan if code == "d" else 0)
        stats = rc.column_stats(cols)
        self.assertEqual(stats["gpu_mw"]["fsum"], 7.0)
        self.assertEqual((stats["gpu_mw"]["min"], stats["gpu_mw"]["max"]), (1.0, 4.0))
        self.assertEqual(stats["gpu_clock_mhz"]["n_finite"], 0)
        self.assertEqual(stats["gpu_mw"]["sha256"], hashlib.sha256(rc.array("d", [1.0, 2.0, 4.0]).tobytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
