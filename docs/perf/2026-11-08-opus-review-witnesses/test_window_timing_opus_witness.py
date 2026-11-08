"""Failing-first witnesses from the Opus cold review (2026-11-08).

Synthetic records only. Each test states the behaviour the reader SHOULD have;
on perf/2026-11-08-eng-timing 44fb124cc they fail.
"""
import json
import unittest

from tests.align.window_timing_synthetic import EPOCH, NS, fixture, options
from joulewise.align.window_timing import read_window

EP = "runs/m1/outputs/align_episode.json"


def _read(docs, **overrides):
    opts = options()
    opts.update(overrides)
    return read_window(docs.__getitem__, **opts)


class OpusWitnessTest(unittest.TestCase):
    def test_h1_ordinary_wall_monotonic_drift_keeps_mapped_episode_placed(self):
        """Native episodes always carry start/end paired stamps
        (joulewise/align/apple/workload.py:728). Wall time is NTP-disciplined
        and monotonic is not, so they drift a few ppm (9.2 ppm measured on the
        Air: 1 ms after ~110 s). The native mapping (sampler.py:96-121) absorbs
        that drift into uncertainty_ns. Here: a 28 s episode whose stamps
        disagree by 2 ms, with a mapping whose uncertainty covers it. The
        member's decode/gate/hold time must still be placed."""
        docs = fixture()
        ep = json.loads(docs[EP])
        ep["clock_mappings"][0]["uncertainty_ns"] = 5_000_000
        ep["hardware"]["paired_clock_stamps_ns"] = [
            dict(epoch_ns=(EPOCH + 30) * NS, monotonic_before_ns=130 * NS, monotonic_after_ns=130 * NS),
            dict(epoch_ns=(EPOCH + 58) * NS + 2_000_000, monotonic_before_ns=158 * NS,
                 monotonic_after_ns=158 * NS)]
        docs[EP] = json.dumps(ep).encode()
        member = _read(docs)["members"]["m1"]
        self.assertNotIn("episode_clock", member["unavailable"])
        self.assertEqual(member["phase_ns"]["decode"], 13 * NS)
        self.assertEqual(member["phase_ns"]["gates"], 5 * NS)

    def test_m1_member_without_run_finalized_cannot_expand_window_by_bad_mapping(self):
        """test_episode_with_wrong_clock_mapping_cannot_expand_window covers a
        member WITH run bounds. A member whose bundle lacks run_finalized (a
        crashed or torn member) skips the bounds check, so a wrong mapping
        moves the episode 1,000 s away and inflates the observed envelope."""
        docs = fixture()
        rows = [r for r in map(json.loads, docs["runs/m1/events.jsonl"].splitlines())
                if r["event_type"] != "run_finalized"]
        docs["runs/m1/events.jsonl"] = "".join(json.dumps(r) + "\n" for r in rows).encode()
        ep = json.loads(docs[EP])
        ep["clock_mappings"][0]["offset_ns"] -= 1000 * NS
        docs[EP] = json.dumps(ep).encode()
        report = _read(docs)
        self.assertEqual(report["wall_ns"], 100 * NS)


if __name__ == "__main__":
    unittest.main()
