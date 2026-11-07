"""Block-4 consumer regressions; archived/synthetic bytes, no live Mac claims."""
from dataclasses import replace
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import receipt_readers as readiness; from joulewise import battery_float; from joulewise import qualification_readers as q
from joulewise import battery_records as assembler; from scripts import qualification_harvest_readers as harvest
from scripts import run_campaign, run_night






class ArchivedBatteryTests(unittest.TestCase):
    pass
    pass
    source = Path(__file__).parent / 'fixtures/v5_qualification_harvest/block3_battery'

    def test_real_block3_glob_skips_attached_copy_and_replays_capture_pairs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / 'custody'
            shutil.copytree(self.source, root)
            # Avoid the repository-wide runs/ ignore rule in the stored fixture.
            (root / 'capture-tree').rename(root / 'runs')
            for relative, digest in q.read(root / 'SOURCE.json')['files'].items():
                self.assertEqual(q.sha(root / relative), digest)
            bound = root.parent / 'bound'; bound.mkdir()
            bundle = root / 'runs/g2a-small-p0512-r01'
            self.assertEqual(battery_float.authenticate_bundle(bundle).status, 'battery_float_evidence_missing')
            with self.assertRaises(battery_float.CustodyFailure):
                battery_float.authenticate_capture(bundle / 'instrument_calibration')
            passed, captures = harvest.battery_attempts(root, bound)
            self.assertFalse(passed)  # Block 3 predates bundle pair production.
            self.assertEqual(len(captures), 3)
            self.assertTrue(all('instrument_calibration' not in path.parts for _, path in captures))
            for _, path in captures:
                if path.parent.name == 'instrument_validation':
                    self.assertEqual(battery_float.authenticate_capture(path).status, 'pass')






if __name__ == '__main__':
    unittest.main()


class G10CustodyTests(unittest.TestCase):
    """Stored G10 support is synthetic; no control command is executed."""

    def _stored_control(self):
        from joulewise import clock_reference, receipt_readers as records
        from joulewise.hazards import network_time
        from tests.git_fixture import init_git_fixture
        import os

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name).resolve()
        repository, root = base / 'repository', base / 'control'
        repository.mkdir()
        root.mkdir()
        boot = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        raw_origin, realtime_offset = 10**12, 2 * 10**18

        def write(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(records.render_json(value))

        def stamp(tick, movement=0):
            return {'realtime_ns': realtime_offset + raw_origin + tick + movement,
                    'monotonic_raw_ns': raw_origin + tick, 'read_skew_ns': 1000,
                    'monotonic_ns': tick, 'boot_id': boot}

        def reference_value():
            samples = []
            for index, server in enumerate(clock_reference.SERVER_ROSTER):
                stdout = f'+0.020000 +/- 0.001000 {server} 192.0.2.{index + 1}\n'
                parsed = clock_reference.parse_sntp_stdout(stdout, server=server)
                self.assertIsNotNone(parsed)
                samples.append({'server': server, 'argv': clock_reference.build_sntp_argv(server),
                    'exit_code': 0, 'started_monotonic_raw_ns': raw_origin + 112 + index * 2,
                    'finished_monotonic_raw_ns': raw_origin + 113 + index * 2,
                    'stdout': stdout, 'stderr': '', 'parsed': True,
                    'offset_s': float(parsed.offset_s), 'uncertainty_s': float(parsed.uncertainty_s),
                    'peer_address': parsed.peer_address, 'raw_line': parsed.raw_line})
            return {'schema_version': clock_reference.SCHEMA_VERSION,
                    'sample_policy_id': clock_reference.SAMPLE_POLICY_ID,
                    'boot_session_id': boot, 'anchor_realtime_ns': realtime_offset + raw_origin + 100,
                    'anchor_monotonic_raw_ns': raw_origin + 100, 'anchor_read_skew_ns': 1000,
                    'batch_started_monotonic_raw_ns': raw_origin + 110,
                    'batch_finished_monotonic_raw_ns': raw_origin + 130, 'samples': samples}

        expected_code = {'scripts/author_arm_evidence_t0.py',
                         'joulewise/arm_readiness_evidence_t0.py', 'scripts/capture_t0_step.py',
                         'scripts/collect_clock_reference.py', 'joulewise/clock_reference.py'}
        for relative in sorted(expected_code):
            path = repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'# inert synthetic code-pin fixture; never executed\n')
        init_git_fixture(repository, '-q')
        environment = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repository), *args], env=environment,
                                           stderr=subprocess.PIPE)
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'synthetic G10 code pins')
        head = git('rev-parse', 'HEAD').decode().strip()
        before, after = stamp(300), stamp(600, 6_000_000)
        write(root / 'before.json', before)
        write(root / 'after.json', after)
        write(root / 'polls/0001.json', after)
        raw_reference = records.render_json(reference_value()).decode()
        preflight = {'argv': list(q.preflight_argv(repository)), 'exit_code': 0,
                     'stdout': raw_reference, 'stderr': '', 'started': stamp(0), 'finished': stamp(200)}
        on = {'argv': list(q.ON_ARGV), 'exit_code': 0, 'stdout': 'setUsingNetworkTime: On\n',
              'stderr': '', 'started': stamp(400), 'finished': stamp(500)}
        for label, command in [('preflight', preflight), ('on', on)]:
            write(root / f'commands/{label}.json', command)
            for endpoint in ('started', 'finished'):
                write(root / f'commands/{label}/{endpoint}.json', command[endpoint])
            for stream in ('stdout', 'stderr'):
                (root / f'commands/{label}/{stream}.txt').write_bytes(command[stream].encode())
        write(root / 'preflight.json', {'midpoint_s': '0.020000', 'bound_s': '0.021000', 'status': 'PASS'})
        write(root / 'anchor-movement.json', {'absolute_movement_ns': 6_000_000})
        positive = {'schema_version': 'joulewise.t0_unattended_anchor_positive_control.v1',
                    'performed_by': 'Ed', 'outside_t0_sequence': True,
                    'network_time_reenabled': True, 'forced_resync': True,
                    'anchor_before_ns': realtime_offset, 'anchor_after_ns': realtime_offset + 6_000_000,
                    'author_refusal_reason_code': q.REFUSAL}
        positive_path = root / 'positive-control.json'
        write(positive_path, positive)
        pack = repository / 'pack'
        pack.mkdir()
        write(root / 'author-input-lineage.json', {'pack_root': str(pack),
            'r0_anchor_ns': realtime_offset, 'boot_id': boot,
            'author_code_sha256': {relative: q.sha(repository / relative) for relative in expected_code}})
        write(root / 'author-custody/pack/arm_readiness.t0.inputs/clock-reference.json',
              {'schema_version': 'joulewise.arm_readiness_t0_command_capture.v1',
               'step_id': 'clock-reference', 'argv': list(q.preflight_argv(repository)),
               'cwd': str(repository), 'exit_code': 0, 'stdout': raw_reference, 'stderr': '',
               'started_monotonic_ns': 0, 'finished_monotonic_ns': 200, 'boot_session_id': boot})
        write(root / 'author-execution.json', {'argv': [str(repository / '.venv/bin/python'),
            str(repository / 'scripts/author_arm_evidence_t0.py'), '--pack-root', str(pack),
            '--custody-root', str(root / 'author-custody')], 'exit_code': 2,
            'present_namespaces': [], 'started': stamp(700, 6_000_000), 'finished': stamp(800, 6_000_000)})
        write(root / 'author.stdout.json', {'status': 'REFUSE', 'kind': 'CLOCK_ATTESTATION',
            'reason_codes': [q.REFUSAL], 'detail': q.ANCHOR_DETAIL})
        off = {'schema': network_time.SCHEMA, 'argv': list(network_time.OFF_ARGV),
               'exit_code': 0, 'stdout': network_time.EXPECTED_STDOUT, 'stderr': '', 'error': None,
               'epoch_s': 1000., 'monotonic_s': 900 / 10**9, 'boot_id': boot,
               'plan_id': root.name, 'window_id': root.name}
        write(root / network_time.RECEIPT_BASENAME, off)
        write(root / 'commands/off.json', off)
        (root / 'commands/off').mkdir()
        (root / 'commands/off/stdout.txt').write_bytes(off['stdout'].encode())
        (root / 'commands/off/stderr.txt').write_bytes(b'')
        write(root / 'outcome.json', {'status': 'DISCHARGED', 'positive_control_path': str(positive_path)})
        manifest = root / 'custody-manifest.json'
        def seal():
            write(manifest, {'files': {path.relative_to(root).as_posix(): q.sha(path)
                for path in sorted(root.rglob('*')) if path.is_file() and path != manifest}})
        seal()
        return root, positive, positive_path, manifest, repository, head, boot, write, seal

    def test_real_g10_verifier_replays_retained_tree_and_refuses_support_mutation(self):
        root, positive, path, manifest, repository, head, boot, write, seal = self._stored_control()
        def verify():
            return q.verify_g10_custody(path, manifest, code_root=repository, head=head,
                                       before_monotonic_ns=1000, boot_id=boot)
        self.assertEqual(verify(), positive)
        before = root / 'before.json'
        original = before.read_bytes()
        before.write_bytes(original + b' ')
        with self.assertRaisesRegex(q.NotDischarged, 'g10_custody_hash_or_census'):
            verify()
        before.write_bytes(original)
        changed = q.read(before)
        changed['realtime_ns'] += 1
        write(before, changed)
        seal()
        with self.assertRaisesRegex(q.NotDischarged, 'g10_anchor_or_record'):
            verify()
