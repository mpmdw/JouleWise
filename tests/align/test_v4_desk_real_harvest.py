"""The guarded v4 desk with the REAL harvest (PR #774 executing re-attack seat, E1, E2, E5 and E6).

Synthetic only, the executing seat's shape: the desk side is the release-guard ``Fixture`` (pilot-4 native
bundles with planted sources), the harvest side is ``tests.test_harvest_b5_window.Window`` (real-shaped B5
bundles) run through the real ``scripts/harvest_b6_session.py`` as a child process, joined by run id.
"""
import contextlib
import io
import json
import os
from contextlib import ExitStack
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter

from tests.align import synthetic_custody  # noqa: I001 (BEFORE the B5 fixture: synthetic custody is the default)
from tests import test_harvest_b5_window as w
from tests.b6 import support
import tests.align.test_v4_desk_release_guard as guard
from scripts import align_v4_session as session_mod

ROOT = Path(__file__).resolve().parents[2]
REAL_TMP = os.path.realpath(tempfile.gettempdir())


def setUpModule():  # noqa: N802 (unittest hook): no test probes a home custody locator
    synthetic_custody.setUpModule()


def tearDownModule():  # noqa: N802 (unittest hook)
    w.tearDownModule()
    synthetic_custody.tearDownModule()


def build(root, scope):
    """A synthetic v4 session for ``scope`` (W1, C3 or T2) whose harvest is the real one (exec seat's build)."""
    start, end = w.member_span_ns('b5t-cmp-b01-b1')
    excursion = ((start + end) // 2, {'instant_amperage_ma': 447, 'amperage_ma': 380})
    window = w.Window(root / 'window', journals={'extra_publications': [excursion]})
    plan = json.loads(window.plan_path.read_bytes())
    plan['hazard_window']['bindings']['capture_screen'] = {}
    support.write_json(window.plan_path, plan)
    ids = [m[0] for m in w.MEMBERS]
    fx = guard.Fixture(root / 'fx')
    joined = root / 'fx' / 'runs-joined'
    remap = {}
    for i, row in enumerate(fx.rows):
        shutil.copytree(fx.runs / row['run_id'], joined / ids[i])
        remap[row['run_id']] = ids[i]
        row['run_id'] = ids[i]
    fx.thermals = {remap[k]: v for k, v in fx.thermals.items()}
    fx.runs = joined
    fx.index = {r['run_id']: i for i, r in enumerate(fx.rows)}
    fx.nonbenign = {r['run_id'] for r in fx.rows if r['condition'] != 'benign'}
    (fx.registration.parent / 'collection_plan.json').write_text(json.dumps({'members': fx.rows}))
    support.registration_dir(fx.registration.parent)
    support.write_json(fx.registration / 'registration.json', {'pack_id': w.PACK_ID})
    venv = fx.measurement / '.venv/bin'
    venv.mkdir(parents=True)
    (venv / 'python').write_text(f'#!/bin/sh\nexec {sys.executable} -B "$@"\n')
    (venv / 'python').chmod(0o755)
    (fx.measurement / 'scripts').mkdir()
    (fx.measurement / 'scripts/harvest_b6_session.py').symlink_to(ROOT / 'scripts/harvest_b6_session.py')
    sroot = root / 'session'
    sroot.mkdir()
    series = {'C3': {'window_id': 'C3', 'role': 'calibration'}, 'T2': {'window_id': 'T2', 'role': 'test'}, 'W1': None}[scope]
    state = {'session_id': 'align-v4-' + scope.lower(), 'plan_path': str(window.plan_path),
             'measurement_root': str(fx.measurement), 'source_measurement_root': str(fx.measurement),
             'registration_dir': str(fx.registration), 'runs_roots': {'claim': str(joined)},
             'inputs': {'custody_root': str(window.custody)}}
    if series:
        state['v4_series'] = series
    (sroot / 'session.json').write_text(json.dumps(state))
    return fx, sroot


def run_desk(fx, sroot, run=subprocess.run):
    with ExitStack() as stack:
        fx.patches(stack)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            status = session_mod.desk(sroot, harvest=True, run=run)
    return status, out.getvalue()


class RealHarvestDeskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-desk-real-harvest-', dir=REAL_TMP)
        cls.runs = {}
        for scope in ('W1', 'C3'):
            fx, sroot = build(Path(cls.tmp.name) / scope, scope)
            status, printed = run_desk(fx, sroot)
            cls.runs[scope] = dict(fx=fx, sroot=sroot, status=status, printed=printed)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_real_harvest_ran_and_its_window_flags_are_present(self):
        for scope, run in self.runs.items():
            self.assertIn(run['status']['harvest_exit'], (0, 6), scope)
            full = json.loads((run['sroot'] / 'archive/withheld/PILOT.full.json').read_text())
            self.assertTrue(full['session_harvest_flags'], scope)          # the control: the full record has them

    def test_e1_w1_prints_window_harvest_flags_as_code_names_only(self):
        run = self.runs['W1']
        pilot = json.loads((run['sroot'] / 'PILOT.json').read_text())
        self.assertEqual(set(pilot['session_harvest_flags']), {'flag_codes', 'withheld'})
        line = next(l for l in run['printed'].splitlines() if l.startswith('session harvest_flags: '))
        self.assertEqual(set(json.loads(line.split(': ', 1)[1])), {'flag_codes', 'withheld'})
        full = json.loads((run['sroot'] / 'archive/withheld/PILOT.full.json').read_text())
        self.assertIn('stream_sizes', json.dumps(full['session_harvest_flags']))     # what would have printed
        for text in (line, json.dumps(pilot['session_harvest_flags'])):
            self.assertNotIn('stream_sizes', text)
            self.assertNotIn('observed', text)
            for run_id in run['fx'].nonbenign:
                self.assertNotIn(run_id, text)

    def test_e2_the_committed_exclusions_source_carries_no_flag_counts(self):
        for scope, run in self.runs.items():
            sroot = run['sroot']
            raw = (sroot / 'archive/derived/exclusions.json').read_bytes()
            full = json.loads(raw)
            committed = json.loads((sroot / 'exclusions.json').read_text())
            self.assertIn('by_code', full['flag_counts'])                      # the harvest's own file has them
            self.assertEqual(committed['flag_counts']['status'], 'withheld_until_series_complete', scope)
            self.assertNotIn('by_code', json.dumps(committed))
            for key in ('members_excluded', 'reasons', 'claim_usable', 'plan_id'):
                self.assertEqual(committed[key], full[key], (scope, key))
            # Mythos final seat F1: the full file is bound by the desk's keyed, nonced digest of its sha256, never by
            # the plain sha256, which would test any guess of flag_counts (m_excl_digest.py). It checks with the key.
            import hashlib
            import hmac as _hmac
            digest = hashlib.sha256(raw).hexdigest()
            committed_text = (sroot / 'exclusions.json').read_text()
            self.assertNotIn(digest, committed_text)
            for name in ('PILOT.json', 'desk.json'):
                self.assertNotIn(digest, (sroot / name).read_text(), (scope, name))
            self.assertNotIn(digest, run['printed'])
            binding = committed['committed_from']
            key = bytes.fromhex(json.loads((sroot / 'archive/withheld/desk_seal_key.json').read_text())['key_hex'])
            canonical = json.dumps({'nonce': binding['nonce'], 'value': digest}, sort_keys=True,
                                   separators=(',', ':')).encode()
            self.assertEqual(binding['hmac_sha256'], _hmac.new(key, canonical, hashlib.sha256).hexdigest(), scope)
            # the guessing attack: rebuild the full file from the committed one plus the TRUE flag_counts, in the
            # harvest's canonical form; its hash matches the full file, and nothing committed can be compared with it
            guess = {k: v for k, v in committed.items() if k != 'committed_from'}
            guess['flag_counts'] = full['flag_counts']
            rebuilt = (json.dumps(guess, indent=2, sort_keys=True) + '\n').encode()
            if rebuilt == raw:
                self.assertNotIn(hashlib.sha256(rebuilt).hexdigest(), committed_text)
        # Attack the committed view and a positive control with the true all-member totals restored.
        run = self.runs['W1']
        committed = json.loads((run['sroot'] / 'exclusions.json').read_text())
        full = json.loads((run['sroot'] / 'archive/derived/exclusions.json').read_text())
        benign, window_codes = Counter(), set()
        for line in run['printed'].splitlines():
            rid, sep, rest = line.partition(' harvest_flags: ')
            if sep and rid == 'session':
                window_codes.update(json.loads(rest)['flag_codes'])
            elif sep:
                benign.update(f['code'] for f in json.loads(rest).get('flags') or [])

        def recover(view):
            # Skip codes with an unknown window component. The remainder is measurable by subtraction.
            totals = {code: n for code, n in view['flag_counts'].get('by_code', {}).items()
                      if code not in window_codes}
            return Counter(totals) - benign

        self.assertTrue(benign)
        recovered = recover({**committed, 'flag_counts': full['flag_counts']})
        original = json.loads((run['sroot'] / 'archive/withheld/PILOT.full.json').read_text())
        hidden = Counter(flag['code'] for member in original['members'] if member['run_id'] in run['fx'].nonbenign
                         for flag in member['harvest_flags'] if flag['code'] not in window_codes)
        self.assertTrue(hidden)
        self.assertEqual(recovered, hidden)
        self.assertEqual(recover(committed), {})

    def test_rl163_synthetic_exclusion_rows_carry_only_roster_and_code_fields(self):
        for scope, run in self.runs.items():
            committed = json.loads((run['sroot'] / 'exclusions.json').read_text())
            rows = committed['members_excluded']
            self.assertTrue(rows, scope)
            for row in rows:
                self.assertEqual(set(row), {'run_id', 'position', 'codes', 'families'}, scope)

    def test_e5_w1_benign_harvest_lines_carry_no_timing(self):
        run = self.runs['W1']
        lines = [l for l in run['printed'].splitlines() if ' harvest_flags: ' in l and not l.startswith('session ')]
        flags = [f for l in lines for f in (json.loads(l.split(': ', 1)[1]).get('flags') or [])]
        self.assertTrue(flags)                                               # benign members carry harvest flags
        self.assertFalse([f for f in flags if set(f) & {'emitted', 'interval'}])
        pilot = json.loads((run['sroot'] / 'PILOT.json').read_text())
        printed_members = [m for m in pilot['members'] if isinstance(m.get('harvest_flags'), list)]
        self.assertTrue(printed_members)
        for m in printed_members:
            self.assertFalse([f for f in m['harvest_flags'] if isinstance(f, dict) and set(f) & {'emitted', 'interval'}])

    def test_e3_sweep_refuses_an_unreleased_v4_session_outside_its_withheld_archive(self):
        # The exec seat's exec_sweep.py shape: sweep the harvested C3 session into an operator --out.
        from scripts import align_v4_harvest_off as runner
        run = self.runs['C3']
        outside = Path(self.tmp.name) / 'sweep-C3'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = runner.main(['sweep', '--session-root', str(run['sroot']), '--out', str(outside), '--workers', '1'])
        self.assertEqual(code, 1)
        self.assertIn('archive/withheld', err.getvalue())
        self.assertFalse(outside.exists())
        # Inside the withheld archive the sweep proceeds (its harvest stubbed here; the refusal is the point).
        inside = run['sroot'] / 'archive/withheld/sweep'
        from unittest import mock
        with mock.patch.object(runner, 'measure_harvest', return_value={'exit': 0, 'peak_child_rss_bytes': 1}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(runner.main(['sweep', '--session-root', str(run['sroot']), '--out', str(inside),
                                          '--workers', '1']), 0)
        self.assertTrue((inside / 'SWEEP.json').is_file())

    def test_e6_a_rerun_refuses_before_any_write(self):
        run = self.runs['C3']
        sroot = run['sroot']
        before = {p.relative_to(sroot).as_posix(): p.read_bytes() for p in sroot.rglob('*')
                  if p.is_file() and not p.relative_to(sroot).as_posix().startswith('archive/sources/')}
        calls = []
        with self.assertRaisesRegex(ValueError, 'rerun refused'):
            run_desk(run['fx'], sroot, run=lambda argv, **kw: calls.append(argv) or subprocess.run(argv, **kw))
        self.assertEqual(calls, [])                                          # the harvest never started
        after = {p.relative_to(sroot).as_posix(): p.read_bytes() for p in sroot.rglob('*')
                 if p.is_file() and not p.relative_to(sroot).as_posix().startswith('archive/sources/')}
        self.assertEqual(after, before)


if __name__ == '__main__':
    unittest.main()
