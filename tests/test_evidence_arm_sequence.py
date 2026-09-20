"""Offline staged arm composition; no launchd installation or collection."""
import contextlib
from dataclasses import replace
import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import gen_evidence_night
from tests.test_gen_evidence_night import EvidenceFixture, ROOT


class EvidenceArmSequenceTests(unittest.TestCase):
    @unittest.skipUnless(Path('/bin/zsh').is_file(), 'zsh required for real verify-only chain')
    def test_staged_arm_reaches_install_render(self):
        """PR #365 sealed staging: bindings refuse 'evidence plan path mismatch'
        (the render literal guard now catches it earlier). Round 0 executed the
        chain during render: the subprocess spies fail before it can execute.
        The real supervisor supplies PIDs and cleanup_proven; only its process
        census is stubbed, as in EvidenceProbeTests, without claiming host proof.
        """
        f = EvidenceFixture()
        self.addCleanup(f.close)
        f.prepare_installer()
        # Run the actual installer module located in the measurement clone,
        # just as the arm procedure does; its repo_head is that clone's HEAD.
        f.plan = replace(f.plan, repo_head=f.head)
        f.write_plan()
        template = Path('configs/launchd/com.joulewise.night.plist.template')
        (f.repo / template).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / template, f.repo / template)
        probe_template = template.with_name('com.joulewise.night-probe.plist.template')
        shutil.copyfile(ROOT / probe_template, f.repo / probe_template)
        name = 'evidence_arm_fixture_installer'
        spec = importlib.util.spec_from_file_location(name, f.repo / 'joulewise/night_agent_install.py')
        installer = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {name: installer}):
            spec.loader.exec_module(installer)

        staged = f.root / 'staged.json'
        os.replace(f.plan_path, staged)
        wrapper = gen_evidence_night.generate(staged)
        artifacts = (wrapper, Path(f.plan.chain_sha256_path),
                     wrapper.with_name('evidence_manifest.json'),
                     Path(str(wrapper) + '.chain-source.sha256'))
        sealed = {path: path.read_bytes() for path in artifacts}
        plan_bytes = staged.read_bytes()
        python = str(f.repo / '.venv/bin/python')
        rendered = f.root / 'rendered'
        calls = []

        def spy(operation):
            def recorded(argv, *args, **kwargs):
                argv_strings = list(map(str, argv))
                calls.append(argv_strings)
                self.assertNotIn(str(wrapper), argv_strings, 'render-only executed the chain')
                self.assertFalse(any(Path(arg).name in ('launchctl', 'claude')
                                     for arg in argv_strings), argv_strings)
                return operation(argv, *args, **kwargs)
            return recorded

        def render(path):
            output, errors = io.StringIO(), io.StringIO()
            with f.installer_environment(), \
                    patch.object(subprocess, 'run', side_effect=spy(subprocess.run)), \
                    patch.object(subprocess, 'Popen', side_effect=spy(subprocess.Popen)), \
                    contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                rc = installer.main(['--plan', str(path), '--python', python,
                                     '--render-only', str(rendered)])
            self.assertEqual(rc, 0, errors.getvalue())
            # Transaction enforces the concrete NullAdapter type for rendering.
            self.assertEqual({p: p.read_bytes() for p in artifacts}, sealed)
            self.assertEqual(path.read_bytes(), plan_bytes)
            records = [json.loads(line) for line in output.getvalue().splitlines() if line.startswith('{')]
            return next(record for record in records if 'input_digests' in record)

        self.assertFalse(f.plan_path.exists())
        staged_digests = render(staged)
        self.assertTrue(calls)
        self.assertFalse(f.plan_path.exists())
        self.assertEqual(len(list(rendered.glob('*.plist'))), 3)
        self.assertEqual(list((f.custody / 'night').iterdir()), [])
        os.replace(staged, f.plan_path)
        bindings = installer.evidence_probe_bindings(f.plan, f.plan_path, python)
        expected = dict(staged_digests['input_digests'])
        expected[str(f.plan_path.absolute())] = expected.pop(str(staged.absolute()))
        self.assertEqual(expected, bindings['input_digests'])
        self.assertEqual(staged_digests['chain_sha256'], bindings['chain_sha256'])

        receipt_path = f.custody / 'night_probe_receipt.json'
        # Narrow the existing EvidenceProbeTests cleanup seam to census only:
        # _stop_probe_group still kills/reaps and derives cleanup_proven itself.
        probe_code = """from pathlib import Path
import sys
from unittest.mock import patch
from scripts import run_night
with patch.object(run_night, '_probe_group_absent', return_value=True):
    raise SystemExit(run_night.probe_night(Path(sys.argv[1]), Path(sys.argv[2]), timeout_s=30))
"""
        env = dict(os.environ, JOULEWISE_LAUNCHD_LABEL=installer.probe_label(f.plan.plan_id))
        # Enter through the fixture venv so the real worker's interpreter
        # identity matches the interpreter pinned by the rendered plists.
        with subprocess.Popen([python, '-B', '-c', probe_code, str(f.plan_path), str(receipt_path)],
                              cwd=f.repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as supervisor:
            stdout, stderr = supervisor.communicate(timeout=40)
        self.assertEqual(supervisor.returncode, 0, (stdout, stderr, receipt_path.read_text()))
        receipt = json.loads(receipt_path.read_text())
        self.assertTrue(receipt['cleanup_proven'])
        self.assertEqual(receipt['driver_pid'], supervisor.pid)
        self.assertGreater(receipt['chain_pgid'], 0)
        self.assertNotEqual(receipt['chain_pgid'], receipt['driver_pid'])
        identity = json.loads(receipt_path.with_name(receipt_path.name + '.process.json').read_text())
        self.assertEqual(identity['chain_pgid'], receipt['chain_pgid'])
        self.assertTrue(receipt['verify_only'])
        self.assertFalse(receipt['collect_started'])
        self.assertFalse(receipt['load_started'])
        prepared = SimpleNamespace(plan=f.plan, plan_path=f.plan_path, python=python)
        self.assertEqual(installer.validate_probe_receipt(prepared), receipt)
        published_digests = render(f.plan_path)
        self.assertEqual(published_digests['input_digests'], bindings['input_digests'])
        self.assertEqual(published_digests['chain_sha256'], staged_digests['chain_sha256'])
        with f.installer_environment():
            prepared = installer.validate_install(SimpleNamespace(
                plan=f.plan_path, python=python, render_only=None, launchd_probe=False), f.repo)
        self.assertEqual({p: p.read_bytes() for p in artifacts}, sealed)
        self.assertEqual(f.plan_path.read_bytes(), plan_bytes)
        for label, calendar_key in (('com.joulewise.night', 'night_calendar'),
                                    ('com.joulewise.night.deadman', 'deadman_calendar')):
            plist = plistlib.loads((rendered / (label + '.plist')).read_bytes())
            self.assertEqual(plist['WorkingDirectory'], str(f.repo))
            self.assertIs(plist['RunAtLoad'], False)
            argv = plist['ProgramArguments']
            self.assertEqual(argv[0], python)
            self.assertEqual(argv[argv.index('--plan') + 1], str(f.plan_path.resolve()))
            self.assertEqual(plist['StartCalendarInterval'], prepared.schedule[calendar_key])
