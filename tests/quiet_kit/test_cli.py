from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.quiet_kit.cli import arm, main, render_plist
from joulewise.quiet_kit.paths import fence, atomic_json
from joulewise.quiet_kit.schedule import PLANS, TOTAL_SECONDS

REPO = Path(__file__).resolve().parents[2]


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-cli-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_plan_creates_nothing_and_runs_no_subprocess(self):
        before = list(self.root.rglob('*'))
        output = []
        with (patch('subprocess.run', side_effect=AssertionError('plan subprocess')),
              patch('subprocess.Popen', side_effect=AssertionError('plan subprocess'))):
            self.assertEqual(main(['--plan','--archive',str(self.root/'absent')], emit=output.append), 0)
        self.assertEqual(list(self.root.rglob('*')), before)
        self.assertIn(f'Total estimated wall hours: {TOTAL_SECONDS/3600:.3f}', output[0])
        self.assertLess(output[0].index('m4-contention-watts'), output[0].index('m5-gpu-rail'))

    def test_plumbing_capture_scale_default_and_override_reach_runner(self):
        from .fakes import FakeHardware
        for extra, expected in (([], 1.), (['--capture-scale', '.25'], .25)):
            with self.subTest(extra=extra), patch('joulewise.quiet_kit.runner.Runner.plumbing', return_value=1) as plumbing:
                self.assertEqual(main(['--plumbing-check', '--test', 'm13-meter-edges',
                    '--scale', '.01', '--archive', str(self.root), *extra],
                    seams=FakeHardware().seams(), emit=lambda _: None), 1)
                plumbing.assert_called_once_with('m13-meter-edges', .01, capture_scale=expected)

    def test_script_plan_suppresses_import_bytecode_even_if_caller_enabled_it(self):
        import sys
        checkout=self.root/'minimal-checkout'
        (checkout/'scripts').mkdir(parents=True)
        (checkout/'joulewise').mkdir()
        (checkout/'joulewise/__init__.py').write_text('')
        shutil.copytree(REPO/'joulewise/quiet_kit',checkout/'joulewise/quiet_kit',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy(REPO/'scripts/quiet_kit.py',checkout/'scripts/quiet_kit.py')
        before=sorted(str(p.relative_to(checkout)) for p in checkout.rglob('*'))
        bootstrap=('import runpy,sys; sys.dont_write_bytecode=False; '
                   'sys.argv=[sys.argv[1],"--plan","--archive",sys.argv[2]]; '
                   'runpy.run_path(sys.argv[0],run_name="__main__")')
        result=subprocess.run([sys.executable,'-c',bootstrap,str(checkout/'scripts/quiet_kit.py'),
                               str(checkout/'nonexistent')],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(sorted(str(p.relative_to(checkout)) for p in checkout.rglob('*')),before)

    def test_plan_and_status_read_completion_and_attempts(self):
        (self.root/'m4-contention-watts/attempts/1').mkdir(parents=True)
        output = []
        main(['--plan','--archive',str(self.root)], emit=output.append)
        self.assertIn('1 attempts so far', output[0])
        atomic_json(self.root/'m4-contention-watts/result.json', {'complete':True})
        output.clear()
        main(['--status','--archive',str(self.root)], emit=output.append)
        self.assertIn('1 attempts so far', output[1])  # JSON alone is not completion
        (self.root/'m4-contention-watts/summary.md').write_text('saved\n')
        output.clear()
        main(['--status','--archive',str(self.root)], emit=output.append)
        self.assertEqual(output[1], 'm4-contention-watts: complete')

    def test_fence_rejects_all_blinded_roots_lexical_parent_and_symlink(self):
        paths = ['/Users/edr/night-custody', '/Users/edr/night-custody/x', '/Users/edr/night-b5/x',
                 '/Users/edr/night-g2a/x', '/Users/edr/night-archive/harvest-v5-b5-any/x',
                 '/users/EDR/NIGHT-CUSTODY/x', '/System/Volumes/Data/Users/edr/night-b5/x',
                 '/System/Volumes/Data/Users/edr/NIGHT-ARCHIVE/HARVEST-V5-B5-any/x',
                 '/Users/edr/night-archive/threshold-validation/../../night-b5/x', '/tmp/calibration-ledger.json']
        for path in paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                fence(path)
        link = self.root/'link'
        link.symlink_to('/Users/edr/night-custody')
        with self.assertRaises(ValueError):
            fence(link/'x')
        self.assertEqual(fence(self.root/'allowed'), self.root/'allowed')

    def test_template_has_exact_launchd_context_and_two_pythons(self):
        raw = render_plist(REPO, self.root, '/fake/model-python')
        value = plistlib.loads(raw)
        self.assertEqual(value['ProcessType'], 'Interactive')
        self.assertTrue(value['RunAtLoad'])
        self.assertFalse(value['KeepAlive'])
        self.assertTrue(value['AbandonProcessGroup'])
        self.assertEqual(value['ProgramArguments'], ['/opt/homebrew/bin/python3.13',
            str(REPO/'scripts/quiet_kit.py'), '--run', '--model-python', '/fake/model-python'])
        self.assertEqual(value['EnvironmentVariables']['TMPDIR'], '/private/tmp/jw-quiet-kit')
        self.assertNotIn('codex', value['EnvironmentVariables']['TMPDIR'])
        self.assertNotIn('claude', value['EnvironmentVariables']['TMPDIR'])
        self.assertTrue(value['StandardOutPath'].startswith(str(self.root)))

    def test_model_python_symlink_is_fenced_without_losing_virtual_environment(self):
        import sys
        from joulewise.quiet_kit.hardware import Hardware
        from joulewise.quiet_kit.runner import Runner
        from .fakes import FakeHardware
        venv_python=self.root/'venv/bin/python'
        venv_python.parent.mkdir(parents=True)
        venv_python.symlink_to(sys.executable)
        self.assertNotEqual(str(fence(venv_python)),str(venv_python))
        value=plistlib.loads(render_plist(REPO,self.root,str(venv_python)))
        self.assertEqual(value['ProgramArguments'][-1],str(venv_python))
        self.assertEqual(Hardware(REPO,str(venv_python)).model_python,str(venv_python))
        self.assertEqual(Runner(REPO,self.root,str(venv_python),FakeHardware().seams()).model_python,str(venv_python))

    def test_rendered_plist_lints(self):
        plutil = shutil.which('plutil')
        if not plutil:
            self.skipTest('plutil is unavailable on this desk host')
        path = self.root/'test.plist'
        path.write_bytes(render_plist(REPO, self.root, '/fake/model-python'))
        result = subprocess.run([plutil, '-lint', '--', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_arm_only_fake_actions_lint_bootout_bootstrap(self):
        calls = []
        def command(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 3 if argv[1] == 'bootout' else 0, '', 'not loaded' if argv[1] == 'bootout' else '')
        from joulewise.quiet_kit.paths import mkdir as real_mkdir
        def mkdir(path):
            if str(path) == '/private/tmp/jw-quiet-kit':
                return self.root/'fake-launchd-tmp'
            return real_mkdir(path)
        with patch('joulewise.quiet_kit.cli.mkdir', side_effect=mkdir):
            self.assertEqual(arm(REPO, self.root, '/fake/model-python', command=command, emit=lambda _:None), 0)
        self.assertEqual([a[1] for a in calls], ['-lint','bootout','bootstrap'])
        self.assertTrue((self.root/'launchd/com.joulewise.quiet-kit.plist').is_file())

    def test_estimates_share_real_segment_plan(self):
        m2 = next(p for p in PLANS if p.test_id == 'm2-long-wait')
        self.assertEqual(m2.estimate_s, 10*1200+20*150+300)
        self.assertEqual([s['arm'] for s in m2.segments if s['kind']=='model'], list('NLLN'*5))
        m1 = next(p for p in PLANS if p.test_id == 'm1-capture-stop-line')
        counts = {name:sum(s['condition']==name for s in m1.segments) for name in ('quiet','load','utility')}
        self.assertEqual(counts, {'quiet':10,'load':4,'utility':4})
