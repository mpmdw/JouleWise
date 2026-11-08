"""D0 reads only explicitly staged synthetic pilot records in these tests."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from scripts import align_v5_capability_d0 as d0
from joulewise.align.records import to_json
from tests.align.test_capability import episode


class D0Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/private/tmp", prefix="jw-cap-d0-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def manifest(self, entries):
        path = self.root / "manifest.json"
        path.write_text(json.dumps({"schema": d0.MANIFEST_SCHEMA,
                                   "purpose": "unblinded_30b_pilot_d0", "entries": entries}))
        return path

    def entry(self, ep=None, name="episode.json"):
        ep = ep or episode()
        (self.root / name).write_text(to_json(ep))
        return {"pilot": 4, "unblinded": True, "record_format": "episode",
                "record_path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest(),
                "configuration_id": "synthetic-frozen-settings"}

    def test_counts_and_no_transcript_text_or_energy_output(self):
        entries = [self.entry(episode(0, True), "a.json"),
                   self.entry(episode(1, False), "b.json"),
                   self.entry(episode(2, None), "c.json")]
        manifest = self.manifest(entries)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = d0.main(["--input-root", str(self.root), "--manifest", manifest.name])
        self.assertEqual(status, 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["gate_status"], "NOT_EVALUATED_PILOT_ONLY")
        summary = result["groups"][0]["summary"]
        self.assertEqual((summary["attempts"], summary["successes"], summary["unscored"]), (3, 1, 1))
        self.assertNotIn("energy", stdout.getvalue())
        self.assertNotIn("transcript", stdout.getvalue())

    def test_pilot_member_adapter_ignores_embedded_absolute_paths_and_exclusions(self):
        summary = {"episode_id": "synthetic-p4", "task_pair": "shade/bank_transfer_2",
                   "seed": 1, "condition": "sabotage", "main_task_score": 1,
                   "side_task_success": True, "per_turn_decode_tokens": [90],
                   "per_turn_hidden_tokens": [20], "configuration": {"model": "synthetic-30B"},
                   "flags": [], "excluded": True}
        path = self.root / "PILOT.json"
        path.write_text(json.dumps({"runs_root": "/NEVER_FOLLOW", "non_claim": True,
                                   "members": [{"run_id": "explicit-id", "excluded": True,
                                                "summary": summary}]}))
        entry = {"pilot": 4, "unblinded": True, "record_format": "pilot_member",
                 "record_path": path.name, "member_run_id": "explicit-id", "give_hint": True,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "configuration_id": "cfg"}
        result = d0.analyze(self.root, self.manifest([entry]).name)
        self.assertEqual(result["groups"][0]["summary"]["successes"], 1)
        self.assertEqual(result["groups"][0]["summary"]["withheld_unknown"], 1)

    def test_optional_apple_transcript_is_hash_checked_and_not_printed(self):
        entry = self.entry(episode(runner=False))
        raw = json.dumps({"role": "assistant", "content": "PRIVATE-ANSWER",
                          "reasoning_content": "<thinking>NATIVE-PRIVATE</thinking>"}).encode()
        (self.root / "messages.jsonl").write_bytes(raw + b"\n")
        entry.update(transcript_path="messages.jsonl",
                     transcript_sha256=hashlib.sha256(raw + b"\n").hexdigest())
        result = d0.analyze(self.root, self.manifest([entry]).name)
        self.assertEqual(result["groups"][0]["summary"]["withheld_tokens_total_known"], 0)
        self.assertNotIn("PRIVATE", json.dumps(result))
        entry["transcript_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry]).name)

    def test_refuses_missing_summary_instead_of_silently_dropping_attempt(self):
        path = self.root / "PILOT.json"
        path.write_text(json.dumps({"non_claim": True, "members": [{"run_id": "lost", "summary": None}]}))
        entry = {"pilot": 4, "unblinded": True, "record_format": "pilot_member",
                 "record_path": path.name, "member_run_id": "lost", "give_hint": True,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "configuration_id": "cfg"}
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry]).name)

    def test_refuses_unattested_v4_and_non_30b_inputs(self):
        for change in ({"unblinded": False}, {"pilot": "W1"}, {"pilot": 11}):
            entry = self.entry()
            entry.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                d0.analyze(self.root, self.manifest([entry]).name)
        entry = self.entry(replace(episode(), agent_model="Qwen3.8-27B"))
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry]).name)

    def test_path_guards_refuse_before_stat_or_open(self):
        # Forbidden strings are tested with all filesystem access mocked out.
        # No real protected path, including its metadata, is accessed.
        for root, rel in (("/Users/edr/jw-b5-do-not-open", "x"),
                          ("/Users/edr/night-do-not-open", "x"),
                          (str(self.root), "restricted/x"),
                          (str(self.root), "night-custody/x"),
                          (str(self.root), "../escape.json"),
                          (str(self.root), "/absolute.json")):
            with self.subTest(root=root, rel=rel), patch.object(Path, "lstat", side_effect=AssertionError("stat")), \
                    patch.object(Path, "open", side_effect=AssertionError("open")):
                with self.assertRaises(ValueError):
                    d0.read_staged(Path(root), rel)

    def test_symlink_and_digest_mismatch_refused(self):
        entry = self.entry()
        (self.root / "link.json").symlink_to(self.root / "episode.json")
        entry["record_path"] = "link.json"
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry]).name)
        entry["record_path"] = "episode.json"
        entry["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry]).name)

    def test_duplicate_exports_are_refused_across_pilot_labels(self):
        entry = self.entry()
        second = dict(entry, pilot=5)
        with self.assertRaises(ValueError):
            d0.analyze(self.root, self.manifest([entry, second]).name)


if __name__ == "__main__":
    unittest.main()
