from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise import measurement_liveness as live

START = "Tue Sep 8 01:02:03 2026"
OTHER = "Tue Sep 8 01:02:04 2026"


class MeasurementLivenessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.parent = self.root / "custody"
        self.night = self.parent / "unittest spaced plan" / "night"
        self.night.mkdir(parents=True)
        self.observer = lambda pid: live.Identity("LIVE", START)
        self.env = patch.dict(os.environ, {
            live.CUSTODY_PARENT_ENV: str(self.parent),
            live.ADDITIONAL_PARENTS_ENV: "[]",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def marker(self, value=None):
        (self.night / "chain.started").write_text(json.dumps(
            {"pid": 41, "start_time": START} if value is None else value))

    def census(self):
        return live.census(observer=self.observer)

    def test_open_chain_live_and_sent_never_closes_it(self):
        self.marker()
        (self.night / "courier.sent").touch()
        result = self.census()
        self.assertFalse(result.clear)
        self.assertIn("live measurement", result.refusals[0])

    def test_closed_chain_does_not_probe_identity(self):
        self.marker()
        (self.night / "chain.exited").write_text(json.dumps(
            {"exit_code": 0, "epoch_s": 1, "monotonic_ns": 2}))
        self.observer = lambda pid: self.fail("closed chain probed")
        self.assertTrue(self.census().clear)

    def test_pid_reuse_warns_and_permits(self):
        self.marker()
        self.observer = lambda pid: live.Identity("LIVE", OTHER)
        result = self.census()
        self.assertTrue(result.clear)
        self.assertIn("reused PID", result.warnings[0])

    def test_dead_and_legacy_dead_warn_and_permit(self):
        self.observer = lambda pid: live.Identity("DEAD")
        for value in ({"pid": 41, "start_time": START}, {"pid": 41}):
            with self.subTest(value=value):
                self.marker(value)
                result = self.census()
                self.assertTrue(result.clear)
                self.assertIn("dead owner", result.warnings[0])

    def test_uncertain_open_markers_refuse(self):
        for raw in ('', '{', '[]', '{"pid":41}', '{"pid":true}',
                    '{"pid":41,"start_time":"bad"}'):
            with self.subTest(raw=raw):
                (self.night / "chain.started").write_text(raw)
                self.assertFalse(self.census().clear)
        self.marker()
        self.observer = lambda pid: live.Identity("UNKNOWN")
        self.assertIn("indeterminate", self.census().refusals[0])

    def test_malformed_exit_does_not_close_chain(self):
        self.marker()
        (self.night / "chain.exited").write_text('{}')
        self.assertFalse(self.census().clear)

    def entry(self):
        return live.publish_campaign(self.root / "unrelated runs with spaces", "nonce",
                                     pid=42, parent=self.parent, observer=self.observer)

    def test_campaign_entry_is_live_even_without_lock_and_after_sent(self):
        entry = self.entry()
        (self.night / "courier.sent").touch()
        record = json.loads(entry.path.read_text())
        self.assertEqual(record["runs_root"], str((self.root / "unrelated runs with spaces").resolve()))
        self.assertFalse((Path(record["runs_root"]) / "campaign.lock").exists())
        self.assertFalse(self.census().clear)
        self.marker()
        (self.night / "chain.exited").write_text(json.dumps(
            {"exit_code": 0, "epoch_s": 1, "monotonic_ns": 2}))
        self.assertFalse(self.census().clear)

    def test_dead_registry_owner_is_harmless_without_deleting_entry(self):
        entry = self.entry()
        original = entry.path.read_bytes()
        self.observer = lambda pid: live.Identity("DEAD")
        result = self.census()
        self.assertTrue(result.clear)
        self.assertTrue(result.warnings)
        self.assertEqual(entry.path.read_bytes(), original)

    def test_registry_cleanup_preserves_replacements_and_removes_owned(self):
        entry = self.entry()
        live.remove_campaign(entry)
        self.assertFalse(entry.path.exists())
        live.remove_campaign(entry)
        for same_inode in (False, True):
            with self.subTest(same_inode=same_inode):
                entry = self.entry()
                if not same_inode:
                    replacement = entry.path.with_suffix('.replacement')
                    replacement.write_bytes(entry.payload)
                    replacement.replace(entry.path)
                else:
                    entry.path.write_text('{"replacement":true}')
                content = entry.path.read_bytes()
                live.remove_campaign(entry)
                self.assertTrue(entry.path.exists(), "cleanup removed replacement")
                self.assertEqual(entry.path.read_bytes(), content)

    def test_malformed_and_legacy_registry_markers_refuse(self):
        entry = self.entry()
        record = json.loads(entry.path.read_text())
        for field in ('schema', 'nonce', 'runs_root', 'start_time'):
            with self.subTest(field=field):
                broken = {key: value for key, value in record.items() if key != field}
                entry.path.write_text(json.dumps(broken))
                self.assertIn('indeterminate', self.census().refusals[0])
        entry.path.write_text('')
        self.assertFalse(self.census().clear)

    def test_publication_failure_cleans_partial_entry(self):
        with patch.object(live.os, "fsync", side_effect=OSError("fixture fsync")):
            with self.assertRaisesRegex(OSError, "fixture fsync"):
                self.entry()
        self.assertEqual(list((self.parent / "active-campaigns").iterdir()), [])

    def test_missing_root_clear_but_root_and_read_errors_refuse(self):
        self.assertTrue(live.census(parents=[self.root / "missing"], observer=self.observer).clear)
        bad = self.root / 'file-root'
        bad.touch()
        self.assertFalse(live.census(parents=[bad], observer=self.observer).clear)
        self.marker()
        with patch.object(live, "_read_marker", side_effect=PermissionError("fixture unreadable")):
            self.assertFalse(self.census().clear)
        with patch.object(Path, "iterdir", side_effect=PermissionError("fixture root")):
            self.assertFalse(self.census().clear)

    def test_additional_parents_are_json_data(self):
        extra = self.root / 'extra ; $(echo never)'
        entry = live.publish_campaign(self.root / 'runs', 'n', pid=42,
                                      parent=extra, observer=self.observer)
        with patch.dict(os.environ, {live.ADDITIONAL_PARENTS_ENV: json.dumps([str(extra)])}):
            self.assertFalse(self.census().clear)
        self.assertTrue(entry.path.exists())
        for raw in ('x', '{}', '[42]'):
            with patch.dict(os.environ, {live.ADDITIONAL_PARENTS_ENV: raw}):
                self.assertFalse(self.census().clear)

    def test_disappearance_reconciles_once_and_instability_refuses(self):
        self.marker()
        reader = live._read_marker
        with patch.object(live, "_read_marker", side_effect=[FileNotFoundError(), reader(self.night / 'chain.started')]) as read:
            self.assertFalse(self.census().clear)
            self.assertEqual(read.call_count, 2)
        with patch.object(live, "_read_marker", side_effect=FileNotFoundError()) as read:
            self.assertIn('indeterminate', self.census().refusals[0])
            self.assertEqual(read.call_count, 2)
        def disappear(path):
            path.unlink()
            raise FileNotFoundError()
        with patch.object(live, "_read_marker", side_effect=disappear):
            self.assertTrue(self.census().clear)

    def test_probe_is_specific_pid_fixed_locale_no_commands(self):
        for code, stdout, stderr, expected in (
            (0, 'Tue Sep  8 01:02:03 2026 S+\n', '', live.Identity('LIVE', START)),
            (0, 'Tue Sep  8 01:02:03 2026 Z\n', '', live.Identity('DEAD')),
            (1, '', '', live.Identity('DEAD')),
            (1, '', 'denied', live.Identity('UNKNOWN')),
            (2, '', '', live.Identity('UNKNOWN')),
            (0, 'bad', '', live.Identity('UNKNOWN')),
        ):
            with self.subTest(stdout=stdout, code=code), patch.object(live.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, stdout, stderr)) as probe:
                self.assertEqual(live.observe_identity(42), expected)
                self.assertEqual(probe.call_args.args[0][1:], ['-p', '42', '-o', 'lstart=', '-o', 'stat='])
                self.assertEqual(probe.call_args.kwargs['env']['LC_ALL'], 'C')
        with patch.object(live.subprocess, 'run', side_effect=OSError('probe unavailable')):
            self.assertEqual(live.observe_identity(42).state, 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
