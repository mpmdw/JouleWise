"""B1-B8 desk tests. All service responses are synthetic; no service is used."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stdout, redirect_stderr
import copy
import importlib.util
import json
import io
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import warnings
from unittest.mock import patch

from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/sol_cloud_fixtures'
SPEC = importlib.util.spec_from_file_location('sol_cloud_runner', ROOT / 'tools/cloud/sol_cloud_run.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
REAL_RUN = subprocess.run


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *map(str, args)],
                          check=True, capture_output=True).stdout


def envelope(paths=None, expansion=False):
    obj = {'schema': 'claude-codex-report/v1', 'genre': 'implementation',
           'status': 'clean', 'completion': 'complete', 'summary': 'Applied the requested change.',
           'workspace': dict.fromkeys(('base_requested', 'base_mode', 'head_start', 'head_end',
                                      'upstream_end', 'branch')),
           'pathspec': ['inside.txt'] if paths is None else paths, 'unowned_dirty': [],
           'verdict': {'implementation': 'implemented', 'acceptance': 'ready'},
           'verification': [{'id': 'V1', 'kind': 'test', 'cmd': 'check', 'cwd': '.',
                             'observed': {'result': 'pass', 'exit_code': 0, 'tail': ['OK']},
                             'expected': {'exit_code': 0, 'tail_regex': '^OK$'}}], 'flags': []}
    if expansion:
        obj.update(status='blocked', completion='partial',
                   scope_expansion={'requested_paths': ['outside.txt'], 'reason': 'Needed',
                                    'blocked_work': 'The second edit', 'minimal_change': 'One file'})
        obj['verdict'] = {'implementation': 'partial', 'acceptance': 'needs_ruling'}
        obj['flags'] = [{'id': 'F1', 'kind': 'scope_deviation', 'level': 'blocking',
                         'text': 'Need scope', 'needs': 'Approve'}]
    return obj


def report(obj):
    return ('```json\n' + json.dumps(obj, ensure_ascii=False) + '\n```\n\n## Change\nDone.\n').encode()


def add_patch(path, content, mode='100644'):
    lines = content.decode().splitlines()
    return (f'diff --git a/{path} b/{path}\nnew file mode {mode}\n'
            f'--- /dev/null\n+++ b/{path}\n@@ -0,0 +1,{len(lines)} @@\n' +
            ''.join('+' + line + '\n' for line in lines)).encode()


@contextmanager
def argv_guard():
    def guarded(argv, *args, **kwargs):
        if isinstance(argv, (str, bytes)):
            raise AssertionError('shell commands forbidden in desk tests')
        if str(argv[0]) == str(FIXTURES / 'fake_cx_cli.py') and len(argv) > 2 and argv[2] == 'exec':
            # The mandatory report contract includes census words. Send the
            # prompt as stdin data so the fake process argv remains safe.
            kwargs['input'] = argv[-1].encode()
            argv = [*argv[:-1], '--prompt-stdin']
        if any(re.search('claude|codex', str(arg), re.I) for arg in argv):
            raise AssertionError('agent census word in subprocess argv')
        return REAL_RUN(argv, *args, **kwargs)
    with patch.object(subprocess, 'run', guarded):
        yield


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sol-desk-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.guard = argv_guard()
        self.guard.__enter__()
        self.addCleanup(self.guard.__exit__, None, None, None)

    def B1_contract(self):
        reference = Path('/Users/edr/.local/bin/codex-run-v3')
        if not reference.exists() or os.environ.get('CI'):
            self.skipTest('local reference unavailable or CI')
        text = reference.read_text()  # Never executed.
        block = text[text.index('genre_contract() {'):text.index('\nsha256_text()')]
        template = block.split('  cat <<EOF\n')[1].split('\nEOF')[0].replace('\\`', '`')
        self.assertEqual(runner.GENRE_TEMPLATE, template)
        for genre in runner.VERDICTS:
            section = block.split(f'    {genre})\n')[1].split(' ;;')[0]
            verdict = re.search("verdict_text='(.*?)'", section)[1]
            prose = re.search("prose_text=\\$'(.*?)'", section, re.S)[1].replace('\\n', '\n')
            expected = template.replace('$1', genre).replace('$verdict_text', verdict).replace('$prose_text', prose) + '\n'
            self.assertEqual(runner.genre_contract(genre), expected)

    def B2_reports(self):
        good = envelope()
        cases = [(report(good), 'valid', False), (b'', 'missing', False),
                 (b'prose\n' + report(good), 'invalid', False),
                 (report(good).replace(b'"clean"', b'NaN'), 'invalid', False),
                 (report(good).replace(b'"schema":', b'"schema":"duplicate", "schema":'), 'invalid', False)]
        for mutation in [dict(good, genre='review'), {k:v for k,v in good.items() if k != 'workspace'},
                         dict(good, summary='x' * 8192), dict(good, status=[])]:
            cases.append((report(mutation), 'invalid', False))
        expanded = envelope(expansion=True)
        cases.append((report(expanded), 'valid', True))
        invalid = copy.deepcopy(expanded)
        invalid['flags'] = []
        cases.append((report(invalid), 'valid', False))
        invalid = copy.deepcopy(expanded)
        invalid['scope_expansion']['extra'] = 'bad'
        cases.append((report(invalid), 'invalid', False))
        for raw, expected, expansion_valid in cases:
            with self.subTest(expected=expected, raw=raw[:80]):
                metrics = runner.parse_report(raw, 'implementation')
                self.assertEqual(metrics['report_parse'], expected)
                self.assertEqual(metrics['scope_expansion_valid'], expansion_valid)
                self.assertEqual(metrics['report_bytes'], len(raw))
        metrics = runner.parse_report(report(good), 'implementation')
        self.assertEqual(metrics['reported_changed_paths'], ['inside.txt'])
        self.assertEqual(metrics['semantic_status'], 'clean')
        self.assertEqual(metrics['completion'], 'complete')
        self.assertEqual(metrics['verification_counts'], {'pass': 1, 'fail': 0, 'not_run': 0})
        # Compare every metric against v3's Python body without executing a CLI.
        reference = Path('/Users/edr/.local/bin/codex-run-v3')
        if reference.exists():
            text = reference.read_text().split('parse_report() {', 1)[1]
            source = text.split("python3 - <<'PY'\n", 1)[1].split('\nPY\n}', 1)[0]
            for raw, _, _ in cases[:-1]:
                if b'"status": []' in raw:
                    continue  # v3 throws TypeError here; runner rejects cleanly.
                out, header, result = [self.root / name for name in ('out', 'header', 'metrics')]
                out.write_bytes(raw)
                env = {'OUT':str(out), 'GENRE':'implementation', 'HEADER_TMP':str(header),
                       'METRICS_TMP':str(result), 'VALIDATOR_ENGINE':'python3', 'WRITE_SCOPE':'["inside.txt"]'}
                with patch.dict(os.environ, env), warnings.catch_warnings():
                    warnings.simplefilter('ignore', ResourceWarning)
                    exec(compile(source, '<v3-validator>', 'exec'), {})
                self.assertEqual(runner.parse_report(raw, 'implementation'), json.loads(result.read_text()))

    def B3_scope_grammar(self):
        for value in ['[]', '["x","a/b","dir/**"]', '["é space"]']:
            self.assertEqual(runner.normalize_scope(value), json.loads(value))
        for entry in ['./x', 'a//b', 'a/*', '.git/x', '../x', 'a/../b', 'a/', 'a\\b', '/x', 'a/**/**']:
            with self.subTest(entry=entry), self.assertRaises(runner.Refusal):
                runner.normalize_scope([entry])
        for bad in ['null', '{}', '[1]', '["x","x"]', 'bad']:
            with self.assertRaises(runner.Refusal):
                runner.normalize_scope(bad)
        self.assertTrue(runner.allowed('a/b', ['a/**']))
        self.assertFalse(runner.allowed('a', ['a/**']))

    def B4_patch_parsers(self):
        for path in sorted((FIXTURES / 'scenarios').glob('paths-*.patch')):
            with self.subTest(path=path.name):
                raw = path.read_bytes()
                self.assertEqual(runner.patch_paths_headers(raw), runner.patch_paths_git(path))
        self.assertGreaterEqual(len(list((FIXTURES / 'scenarios').glob('paths-*.patch'))), 10)

    def B5_scope_decisions(self):
        for paths, scope, modes, expected in [
                ({'in/a','out/b'}, ['in/**'], {}, ['out/b']),
                ({'out/a','in/b'}, ['in/**'], {}, ['out/a']),
                ({'out/deleted'}, ['in/**'], {}, ['out/deleted']),
                ({'.codex-report/other.md'}, [], {}, ['.codex-report/other.md']),
                ({'in/link'}, ['in/**'], {'in/link':'120000'}, ['in/link']),
                ({'in/sub'}, ['in/**'], {'in/sub':'160000'}, ['in/sub']),
                ({'.codex-report/job.md'}, [], {}, []),
                ({'../escape'}, ['in/**'], {}, ['../escape'])]:
            self.assertEqual(runner.check_scope(paths, scope, 'job', modes)[0], expected)
        (self.root/'link').symlink_to(self.root/'missing')
        self.assertEqual(runner.check_scope([], ['link/x'], 'job', apply_base=self.root)[0], ['link/x'])
        self.assertEqual(runner.decide(runner.parse_report(b'', 'implementation'))[:2], ('ACCEPTANCE_FAILED',65))
        valid=runner.parse_report(report(envelope(expansion=True)), 'implementation')
        self.assertEqual(runner.decide(valid)[:2], ('NEEDS_SCOPE',79))
        valid['scope_expansion_valid']=False
        self.assertEqual(runner.decide(valid)[:2], ('ACCEPTANCE_FAILED',65))
        self.assertEqual(runner.decide(valid,['out'])[:2], ('SCOPE_VIOLATION',77))

    def setup_repo(self):
        self.repo, self.origin = self.root/'repo', self.root/'remote.git'
        self.repo.mkdir()
        self.origin.mkdir()
        init_git_fixture(self.repo)
        init_git_fixture(self.origin, '--bare')
        git(self.repo, 'config', 'user.name', 'fixture')
        git(self.repo, 'config', 'user.email', 'fixture@invalid')
        (self.repo/'inside.txt').write_text('before\n')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-m', 'base')
        git(self.repo, 'branch', '-M', 'main')
        git(self.repo, 'remote', 'add', 'origin', self.origin)
        git(self.repo, 'push', '-u', 'origin', 'main')
        self.addCleanup(self.remove_worktrees)

    def remove_worktrees(self):
        for directory in self.root.glob('apply-*'):
            git(self.repo, 'worktree', 'remove', '--force', directory)

    def scenario(self, name, patch_bytes=None):
        scenario = json.loads((FIXTURES/'scenarios'/f'{name}.json').read_text())
        folder = self.root / name
        folder.mkdir(exist_ok=True)
        if patch_bytes is not None:
            (folder/'change.patch').write_bytes(patch_bytes)
        (folder/'scenario.json').write_text(json.dumps(scenario))
        return {'SOL_CLOUD_TEST_SCENARIO':str(folder/'scenario.json'),
                'SOL_CLOUD_TEST_CALLS':str(folder/'calls.jsonl'),
                'SOL_CLOUD_TEST_RATE_LIMIT_WAIT':'0', 'SOL_CLOUD_TEST_POLL_FLOOR':'0'}

    def invocation(self, name, scope=None, timeout='5'):
        out = self.root / f'{name}.md'
        args = [str(out), '--env','test-env','--branch','main','-C',str(self.repo),
                '--genre','implementation','--write-scope',json.dumps(scope or ['inside.txt']),
                '--apply-worktree',str(self.root/f'apply-{name}'), '--cx-bin', str(FIXTURES/'fake_cx_cli.py'),
                '--timeout',timeout,'--poll','0.1','--record-dir',str(self.root/f'record-{name}'),
                'WRITE_SCOPE: ["inside.txt"]\nTASK_ID: test\nImplement.']
        return out, args

    def modification(self):
        return b'diff --git a/inside.txt b/inside.txt\n--- a/inside.txt\n+++ b/inside.txt\n@@ -1 +1 @@\n-before\n+after\n'

    def run_main(self, args):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = runner.main(args)
        self.last_stdout, self.last_stderr = output.getvalue(), errors.getvalue()
        return result

    def invoke(self, name, scenario_name='ready', body=None, scope=None, timeout='5'):
        out,args = self.invocation(name, scope, timeout)
        env = self.scenario(scenario_name, body)
        with patch.dict(os.environ, env):
            rc = self.run_main(args)
        state = json.loads(Path(str(out)+'.state.json').read_text())
        rows = [json.loads(x) for x in Path(str(out)+'.manifest.jsonl').read_text().splitlines()]
        return rc,out,state,rows,env

    def B6_pure_copy(self):
        # A pure copy is scope-checked at both ends, but only its new end is staged.
        self.setup_repo()
        body = (b'diff --git a/inside.txt b/copied.txt\nsimilarity index 100%\n'
                b'copy from inside.txt\ncopy to copied.txt\n')
        body += add_patch('.codex-report/copy.md', report(envelope()))
        result, out, state, rows, env = self.invoke('copy', 'ready', body, scope=['inside.txt', 'copied.txt'])
        self.assertEqual(result, 0)
        self.assertEqual(runner.staged_paths(state['apply_worktree']), {'copied.txt'})
        result, out, state, rows, env = self.invoke('copy-out', 'ready',
                                                    body.replace(b'copy.md', b'copy-out.md'),
                                                    scope=['copied.txt'])
        self.assertEqual(result, 77)

    test_B6_pure_copy = B6_pure_copy

    def B6_end_to_end(self):
        self.setup_repo()
        for name, scenario_name, patch_body, rc in [
                ('clean','ready', self.modification(),0),
                ('violation','ready',add_patch('outside.txt',b'new\n'),77),
                ('no-report','ready',self.modification(),65),
                ('expansion','ready',self.modification(),79),
                ('task-error','error',b'',1), ('timeout','pending',b'',143),
                ('retry','rate',self.modification(),0),
                ('begin','ready',b'*** Begin Patch\n',1),
                ('bad-base','ready',self.modification().replace(b'-before',b'-wrong'),74),
                ('lookup','lookup',self.modification(),0),
                ('page','page',self.modification(),0),
                ('poll-rate','poll-rate',self.modification(),0),
                ('list-fail','list-fail',b'',1),
                ('empty','ready',b'',65)]:
            with self.subTest(name=name):
                raw_report = report(envelope(expansion=name=='expansion'))
                if name not in {'no-report','task-error','timeout','begin','list-fail','empty'}:
                    patch_body += add_patch(f'.codex-report/{name}.md',raw_report)
                result,out,state,rows,env = self.invoke(name,scenario_name,patch_body,timeout='2' if name=='timeout' else '5')
                self.assertEqual(result,rc)
                self.assertEqual(len(rows),2)
                self.assertFalse(rows[-1]['model_verified'])
                self.assertEqual(self.last_stdout.splitlines()[-1],
                                 f'codex-run exit: {rows[-1]["transport_status"]} -> {out}')
                calls = [json.loads(line) for line in Path(env['SOL_CLOUD_TEST_CALLS']).read_text().splitlines()]
                self.assertFalse(any(re.search('claude|codex', ' '.join(call['argv']), re.I) for call in calls))
                if name=='page':
                    self.assertIn('--cursor', calls[2]['argv'])
                if name=='list-fail':
                    self.assertEqual(sum(call['argv'][1]=='list' for call in calls),5)
                if rc in {0,65,79}:
                    self.assertEqual(runner.staged_paths(state['apply_worktree']), set() if name=='empty' else {'inside.txt'})
                    self.assertFalse(Path(state['apply_worktree'], '.codex-report').exists())
                else:
                    self.assertFalse(Path(state['apply_worktree']).exists())
                if name=='clean':
                    self.assertEqual(out.read_bytes(),raw_report)
                    self.assertEqual(Path(str(out)+'.status').read_text(),
                                     'OK\nsemantic_status=clean\ncompletion=complete\nrun_status=OK\nscope_action=passed\n')
                    self.assert_manifest_keys(rows)
                if name=='violation':
                    self.assertTrue(Path(state['evidence_bundle'],'metadata.json').exists())
                    self.assertEqual(Path(state['patch_path']).read_bytes(),patch_body)
                if name=='expansion':
                    self.assertEqual(state['pending_scope_expansion']['requested_paths'],['outside.txt'])
                if name=='begin':
                    self.assertEqual(rows[-1]['error_stage'],'report_capture')
                if name=='timeout':
                    self.assertEqual(rows[-1]['transport_status'],'TIMEOUT after 2s')
                records=list((self.root/f'record-{name}').glob('*.json'))
                self.assertGreaterEqual(len(records),1)
                for recording in records:
                    self.assertTrue(recording.with_suffix('.stdout').exists())
                    self.assertTrue(recording.with_suffix('.stderr').exists())

    def assert_manifest_keys(self, rows):
        cloud = {'transport','cloud_env','cloud_branch','cloud_task_id','cloud_task_url','base_sha',
                 'patch_path','apply_worktree','apply_branch','model_verified'}
        started = set('schema_version event run_key task_id attempt parent_run_key genre prompt_contract report_contract prompt_sha256 prompt_bytes base_requested base_mode head_start upstream_start branch_start write_scope verification_profile model reasoning_effort sandbox cwd out role_or_lens parent_report started_at'.split())
        finished = set('schema_version event run_key attempt session_id invocation_state runner_rc error_stage duration_ms head_end upstream_end run_status model reasoning_effort transport_status token_usage finished_at scope_policy_version scope_enforcement actual_changed_paths actual_changed_count attempt_changed_paths attempt_changed_count reported_changed_paths reported_changed_count scope_violation_paths scope_violation_count pathspec_report_mismatch scope_action evidence_bundle'.split()) | set(runner.parse_report(b'', 'implementation'))
        self.assertEqual(set(rows[0]),started|cloud)
        self.assertEqual(set(rows[1]),finished|cloud)

    def B7_approve_resume(self):
        self.setup_repo()
        body = add_patch('outside.txt',b'new\n') + add_patch('.codex-report/approve.md',report(envelope(['outside.txt'])))
        rc,out,state,rows,env = self.invoke('approve',body=body)
        self.assertEqual(rc,77)
        common = [state['run_key'],'--approval-note','Lead approved','--state-file',state['state_file']]
        self.assertEqual(self.run_main(['approve',*common,'--approve-scope-add','["unasked.txt"]']),64)
        self.assertEqual(self.run_main(['approve',*common,'--approve-scope-add','["broad/**"]']),64)
        self.assertEqual(self.run_main(['approve',*common,'--approve-scope-add','["outside.txt"]']),0)
        rows = [json.loads(x) for x in Path(state['manifest']).read_text().splitlines()]
        self.assertEqual([r['event'] for r in rows],['run_started','run_finished','scope_expansion_approved','run_finished'])
        self.assertEqual(set(rows[2]), set('schema_version event run_key session_id old_scope approved_additions new_scope approval_note approved_at'.split()))
        self.assertEqual(runner.staged_paths(state['apply_worktree']),{'outside.txt'})
        body = self.modification() + add_patch('.codex-report/resume.md',report(envelope(expansion=True)))
        rc,out,state,_,env = self.invoke('resume',body=body)
        self.assertEqual(rc,79)
        args=['resume',state['run_key'],'--approval-note','Go','--state-file',state['state_file'],
              '--approve-scope-add','["outside.txt"]']
        self.assertEqual(self.run_main(args),64)
        git(state['apply_worktree'],'commit','-m','partial')
        self.assertEqual(self.run_main(args),64)
        git(state['apply_worktree'],'push','-u','origin',state['apply_branch'])
        second = add_patch('outside.txt',b'new\n') + add_patch('.codex-report/resume.md',report(envelope(['outside.txt'])))
        env=self.scenario('resume-ready',second)
        with patch.dict(os.environ,env):
            self.assertEqual(self.run_main(args),0)
        calls=[json.loads(x) for x in Path(env['SOL_CLOUD_TEST_CALLS']).read_text().splitlines()]
        invocation=calls[0]['argv']
        amended=calls[0]['prompt']
        self.assertEqual(invocation[invocation.index('--branch')+1],state['apply_branch'])
        self.assertIn('WRITE_SCOPE: ["inside.txt","outside.txt"]',amended)
        self.assertIn('SCOPE EXPANSION APPROVED BY LEAD: Go',amended)
        self.assertIn('AMENDED WRITE_SCOPE: ["inside.txt","outside.txt"]',amended)
        final=json.loads(Path(state['state_file']).read_text())
        self.assertEqual(final['attempt'],2)
        self.assertEqual(runner.staged_paths(state['apply_worktree']),{'outside.txt'})

    def B8_guard_and_refusals(self):
        with self.assertRaisesRegex(AssertionError,'agent census'):
            subprocess.run(['not-run', 'CODEX'])
        self.setup_repo()
        out,args=self.invocation('refuse')
        self.assertEqual(self.run_main(args[:-1]+['-s','danger-full-access',args[-1]]),64)
        args[args.index('--write-scope')+1]='["./bad"]'
        self.assertEqual(self.run_main(args),64)
        self.assertFalse(out.exists())

    test_B1 = B1_contract
    test_B2 = B2_reports
    test_B3 = B3_scope_grammar
    test_B4 = B4_patch_parsers
    test_B5 = B5_scope_decisions
    test_B6 = B6_end_to_end
    test_B7 = B7_approve_resume
    test_B8 = B8_guard_and_refusals
