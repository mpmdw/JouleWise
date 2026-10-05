from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

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

    def pending_marker(self, **overrides):
        record = {"schema": "joulewise.launch_pending.v1", "plan_id": "pending-plan",
                  "attempt_id": "fixture-attempt", "pid": 7272, "pgid": 7272,
                  "epoch_s": 1.0, "start_time": START}
        record.update(overrides)
        path = self.night / "launch.pending"
        path.write_text(json.dumps(record) + "\n")
        return path

    def test_v8_live_pending_launcher_is_measurement_owner_without_chain_started(self):
        path = self.pending_marker()
        original = path.read_bytes()
        self.observer = Mock(return_value=live.Identity("LIVE", START))
        (self.night / "courier.sent").touch()
        with patch.object(live.os, "killpg") as group:
            result = self.census()
        self.assertFalse(result.clear)
        self.assertEqual(result.refusals, [f"live measurement owner: {path}"])
        self.assertEqual(result.warnings, [])
        group.assert_called_once_with(7272, 0)
        self.observer.assert_called_once_with(7272)
        self.assertFalse((self.night / "chain.started").exists())
        self.assertEqual(path.read_bytes(), original)

    def test_pending_group_gone_warns_and_permits_without_identity_or_custody_write(self):
        path = self.pending_marker(start_time=None)
        original = path.read_bytes()
        self.observer = lambda pid: self.fail("absent group probed leader")
        with patch.object(live.os, "killpg", side_effect=ProcessLookupError()):
            result = self.census()
        self.assertTrue(result.clear)
        self.assertIn("dead pending process group", result.warnings[0])
        self.assertEqual(path.read_bytes(), original)

    def test_live_pending_group_with_dead_or_reused_leader_still_refuses(self):
        path = self.pending_marker()
        for identity in (live.Identity("DEAD"), live.Identity("LIVE", OTHER)):
            with self.subTest(identity=identity), patch.object(live.os, "killpg"):
                self.observer = lambda pid: identity
                result = self.census()
            self.assertFalse(result.clear)
            self.assertEqual(result.refusals, [f"live measurement owner process group: {path}"])
            self.assertEqual(len(result.warnings), 1)

    def test_pending_group_unknown_or_identity_unavailable_refuses(self):
        path = self.pending_marker()
        for error in (PermissionError("fixture denied"), OSError("fixture unavailable")):
            with self.subTest(error=error), patch.object(live.os, "killpg", side_effect=error):
                self.assertIn("indeterminate", self.census().refusals[0])
        for identity in (live.Identity("UNKNOWN"), live.Identity("LIVE")):
            with self.subTest(identity=identity), patch.object(live.os, "killpg"):
                self.observer = lambda pid: identity
                self.assertIn("indeterminate", self.census().refusals[0])
        self.observer = lambda pid: live.Identity("LIVE", START)
        for start in (None, "bad"):
            self.pending_marker(start_time=start)
            with self.subTest(start=start), patch.object(live.os, "killpg"):
                self.assertIn("indeterminate", self.census().refusals[0])
        self.assertTrue(path.exists())

    def test_malformed_or_unreadable_pending_marker_refuses_before_group_probe(self):
        path = self.pending_marker()
        for raw in ("", "{", "[]", "{}", '{"pid":7272,"pgid":true}',
                    '{"pid":true,"pgid":7272}', '{"pid":7272,"pgid":1}'):
            path.write_text(raw)
            with self.subTest(raw=raw), patch.object(live.os, "killpg") as group:
                self.assertIn("indeterminate", self.census().refusals[0])
                group.assert_not_called()
            self.assertEqual(path.read_text(), raw)
        self.pending_marker()
        with patch.object(live, "_read_marker", side_effect=PermissionError("fixture unreadable")):
            self.assertIn("indeterminate", self.census().refusals[0])

    def test_pending_symlinks_refuse_including_dangling_links(self):
        path = self.night / "launch.pending"
        target = self.root / "pending-target"
        for exists in (False, True):
            if exists:
                target.write_text(json.dumps({"pid": 7272, "pgid": 7272, "start_time": START}))
            path.symlink_to(target)
            with self.subTest(exists=exists), patch.object(live.os, "killpg") as group:
                self.assertIn("indeterminate", self.census().refusals[0])
                group.assert_not_called()
            path.unlink()

    def test_closed_chain_does_not_hide_live_pending_group(self):
        self.pending_marker()
        self.marker()
        (self.night / "chain.exited").write_text(json.dumps(
            {"exit_code": 0, "epoch_s": 1, "monotonic_ns": 2}))
        with patch.object(live.os, "killpg"):
            result = self.census()
        self.assertFalse(result.clear)
        self.assertIn("launch.pending", result.refusals[0])

    def test_pending_disappearance_reconciles_once_and_instability_refuses(self):
        path = self.pending_marker()
        record = live._read_marker(path)
        with patch.object(live.os, "killpg"), patch.object(
                live, "_read_marker", side_effect=[FileNotFoundError(), record]) as read:
            self.assertFalse(self.census().clear)
            self.assertEqual(read.call_count, 2)
        with patch.object(live, "_read_marker", side_effect=FileNotFoundError()) as read:
            self.assertIn("indeterminate", self.census().refusals[0])
            self.assertEqual(read.call_count, 2)
        def disappear(marker):
            marker.unlink()
            raise FileNotFoundError()
        with patch.object(live, "_read_marker", side_effect=disappear):
            self.assertTrue(self.census().clear)

    def test_pending_diagnostics_are_not_duplicated_when_chain_read_retries(self):
        self.pending_marker()
        self.marker()
        reader = live._read_marker
        failed = False
        def race(path):
            nonlocal failed
            if path.name == "chain.started" and not failed:
                failed = True
                raise FileNotFoundError("fixture chain race")
            return reader(path)
        with patch.object(live.os, "killpg"), patch.object(live, "_read_marker", side_effect=race):
            result = self.census()
        self.assertFalse(result.clear)
        self.assertEqual(len(result.refusals), 2)
        self.assertEqual(len(set(result.refusals)), 2)

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

    def test_dead_owner_with_start_time_warns_and_permits(self):
        self.observer = lambda pid: live.Identity("DEAD")
        self.marker({"pid": 41, "start_time": START})
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

    def test_successful_empty_probe_is_unknown_for_live_pid(self):
        with patch.dict(os.environ, {live.IDENTITY_PROBE_ENV: "/usr/bin/true"}):
            self.assertEqual(live.observe_identity(os.getpid()), live.Identity("UNKNOWN"))

    def test_chain_without_start_time_refuses_even_if_pid_is_dead(self):
        self.marker({"pid": 41, "pgid": 41, "epoch_s": 1})
        self.observer = lambda pid: live.Identity("DEAD")
        result = self.census()
        self.assertFalse(result.clear)
        self.assertIn("indeterminate", result.refusals[0])
        self.assertEqual(result.warnings, [])

    def test_registry_retry_does_not_duplicate_diagnostics(self):
        entries = [self.entry(), self.entry(), self.entry()]
        registry = entries[0].path.parent
        original = live._inspect_campaign
        reads = 0
        def inspect(path, result, observer):
            nonlocal reads
            if path == entries[2].path:
                reads += 1
                if reads <= 2:
                    raise FileNotFoundError("fixture registry race")
            original(path, result, observer)
        def observe(pid):
            # Both warning and refusal from the prefix must survive exactly once.
            return live.Identity("LIVE", START)
        def classify(path, result, observer):
            inspect(path, result, (lambda pid: live.Identity("DEAD"))
                    if path == entries[0].path else observer)
        iterdir = Path.iterdir
        def ordered(path):
            return iter([entry.path for entry in entries]) if path == registry else iterdir(path)
        with patch.object(live, "_inspect_campaign", side_effect=classify), patch.object(Path, "iterdir", ordered):
            result = live.census(observer=observe)
        self.assertEqual(reads, 3)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(len(result.refusals), 2)
        self.assertEqual(len(set(result.refusals)), 2)

    def test_probe_is_specific_pid_fixed_locale_no_commands(self):
        for code, stdout, stderr, expected in (
            (0, 'Tue Sep  8 01:02:03 2026 S+\n', '', live.Identity('LIVE', START)),
            (0, 'Tue Sep  8 01:02:03 2026 Z\n', '', live.Identity('DEAD')),
            (1, '', '', live.Identity('DEAD')),
            (0, '', '', live.Identity('UNKNOWN')),
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
