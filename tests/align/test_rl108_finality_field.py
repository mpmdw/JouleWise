"""RL-108 condition 5 (RL-53 W-7, last sentence): one finality field with one writer.

``WindowRecord.finality()`` is the only place a window record's finality is decided. It returns
``final``, ``provisional`` or ``desk_failed``; every other reader derives from it. ``desk_failed`` is a
value only: no release, no new refusal, no new admission (RL-53). Synthetic Git records only; the
fixtures are the packet builder's own (tests/align/test_v4_next_arm_packet.py).
"""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import align_v4_next_arm_packet as builder
from scripts import align_v4_session as session
from joulewise.align.apple import v4_cadence as cad
from tests.align.test_v4_next_arm_packet import Scenario

REPO = Path(__file__).resolve().parents[2]
BASE = 'a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe'   # the W1 night commit this side branch is based on
LEGACY_CHAIN_KEYS = {'window', 'commit', 'path', 'sha256', 'previous_sha256'}


def _root(case):
    temp = tempfile.TemporaryDirectory(prefix='jw-rl108-finality-')
    case.addCleanup(temp.cleanup)
    return temp.name


def provisional_then_unbound(case):
    """C1 provisional (desk running off the MBP, no final sources); C2 committed without previous_final."""
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1, provisional=True).finish()
    return Scenario(root, 'C2', previous=c1).finish()


def provisional_then_bound(case, change=None):
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1, provisional=True).finish()
    if change is not None:
        change(c1)
    return Scenario(root, 'C2', previous=c1, previous_final=True).finish()


def stale_sources_running_desk(case):
    """Final sources bound in the record itself, but the desk is still running off the MBP."""
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1)
    light = copy.deepcopy(c1.thermal)
    for m in light['members']:
        m['excluded'] = bool(m['calibration_exclusions'])
    c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C1', 'thermal': light,
        'checks': {'v4_B_bar': True}, 'km003c': c1.sources['pilot']['extra_checks']['km003c'],
        'series_desk_row': c1.sources['pilot']['extra_checks']['series_desk_row']}
    c1.sources['desk'] = {'plan_id': c1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
    c1.finish()
    c1.series['last_passed_record'] = dict(w1.passed_ref)
    c1.passed_ref = dict(w1.passed_ref)
    c1.write(c1.series_path, c1.series)
    c1.series_commit = c1.commit()
    return Scenario(root, 'C2', previous=c1).finish()


def own_sources(case, change):
    """C1 carries its own final sources; ``change`` edits them before commit; C2 follows."""
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1)
    change(c1)
    c1.finish()
    c1.series['last_passed_record'] = dict(w1.passed_ref)
    c1.write(c1.series_path, c1.series)
    c1.series_commit = c1.commit()
    return Scenario(root, 'C2', previous=c1).finish()


def non_passing(c):
    c.sources['pilot']['status'] = 'instrument_incomplete'
    c.sources['desk'].update(pilot_status='instrument_incomplete', checks={'synthetic_check': False})


def zero_capture(case):
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1, captured=False)
    c1.sources['desk']['harvest_status'] = 'not_run'
    c1.finish()
    c1.series['last_passed_record'] = dict(w1.passed_ref)
    c1.write(c1.series_path, c1.series)
    c1.series_commit = c1.commit()
    return Scenario(root, 'C1#2', previous=c1).finish()


def unreadable_light(case):
    """No capture, no final sources, a light triage for another window: the predicate refuses."""
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1, captured=False)
    c1.omit_sources.update(builder.FINAL_SOURCES)
    c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C9'}
    c1.finish()
    return c1


def unreadable_final_sources(case):
    """Final sources bound by name; the record binds no plan source, so the sources cannot be read."""
    root = _root(case)
    w1 = Scenario(root, 'W1').finish()
    c1 = Scenario(root, 'C1', previous=w1)
    c1.omit_sources.add('plan')
    c1.finish()
    return c1


# (label, scenario factory, window whose finality is examined, expected value, expected reason prefix)
CASES = (
    ('own final sources, completed passing desk', lambda t: Scenario(_root(t), 'W1').finish(), 'W1', 'final', None),
    ('completed non-passing desk is final', lambda t: own_sources(t, non_passing), 'C1', 'final', None),
    ('zero capture needs no harvest', zero_capture, 'C1', 'final', None),
    ('successor previous_final binds a completed desk', provisional_then_bound, 'C1', 'final', None),
    ('no final sources yet', provisional_then_unbound, 'C1', 'provisional', 'no final sources'),
    ('light triage unreadable, nothing captured', unreadable_light, 'C1', 'provisional',
     'light triage unreadable: '),
    ('own sources, desk still running off the MBP', stale_sources_running_desk, 'C1', 'provisional',
     'the desk recorded no completed harvest (still running off the MBP)'),
    ('previous_final desk still running', lambda t: provisional_then_bound(t, lambda c: c.final_sources.__setitem__(
        'desk', {'plan_id': c.sources['plan']['plan_id'], 'status': 'running_off_mbp'})), 'C1', 'provisional',
     'the desk recorded no completed harvest (still running off the MBP)'),
    ('final sources unreadable', unreadable_final_sources, 'C1', 'desk_failed', 'final sources unreadable: '),
    ('harvest program fault', lambda t: provisional_then_bound(
        t, lambda c: c.final_sources['desk'].update(harvest_status='program_fault')), 'C1', 'desk_failed',
     'the desk recorded no completed harvest (harvest_status program_fault)'),
    ('desk not a mapping', lambda t: provisional_then_bound(
        t, lambda c: c.final_sources.__setitem__('desk', ['not', 'a', 'desk'])), 'C1', 'desk_failed',
     'the desk recorded no completed harvest (still running off the MBP)'),
    ('desk bound to another plan', lambda t: provisional_then_bound(
        t, lambda c: c.final_sources['desk'].update(plan_id='synthetic-other')), 'C1', 'desk_failed',
     "the desk and PILOT.json are not bound to this window's plan"),
    ('no completed adjudication', lambda t: provisional_then_bound(
        t, lambda c: c.final_sources['pilot'].update(status='running')), 'C1', 'desk_failed',
     'PILOT.json carries no completed desk adjudication (status running)'),
    ('final exclusions missing', lambda t: provisional_then_bound(
        t, lambda c: c.final_sources.__setitem__('exclusions', {'reasons': []})), 'C1', 'desk_failed',
     'final exclusions missing'),
    ('desk and exclusions disagree', lambda t: provisional_then_bound(t, lambda c: (
        c.final_sources['desk'].__setitem__('members_excluded', [{'run_id': c.members[0]['run_id'],
                                                                  'codes': ['clock.step']}]))),
     'C1', 'desk_failed', 'desk, PILOT.json and exclusions disagree'),
)


def chain_of(scenario):
    """The authenticated chain with successor bindings, as the builder and held_window_check bind it."""
    evidence = builder.GitEvidence(scenario.root)
    records, s = [], scenario
    while s is not None:
        records.append(builder.WindowRecord(evidence, s.record_commit, s.record_path))
        s = s.previous
    records.reverse()
    for older, newer in zip(records, records[1:]):
        older.bind_final(newer)
    return {r.window: r for r in records}


class FinalityValueTests(unittest.TestCase):
    def test_each_case_maps_to_exactly_one_value_with_the_unchanged_message(self):
        seen = set()
        for label, factory, window, value, prefix in CASES:
            with self.subTest(label):
                record = chain_of(factory(self))[window]
                state = record.finality()
                self.assertEqual(set(state), {'finality', 'reason'})
                self.assertIn(state['finality'], builder.WindowRecord.FINALITY_VALUES)
                self.assertEqual(state['finality'], value, state)
                if prefix is None:
                    self.assertIsNone(state['reason'])
                else:
                    self.assertTrue(state['reason'].startswith(prefix), state['reason'])
                # Every reader derives from the one writer.
                self.assertEqual(record.final_evidence(), state['reason'])
                self.assertEqual(record.is_final(), state['finality'] == 'final')
                seen.add(value)
        self.assertEqual(seen, set(builder.WindowRecord.FINALITY_VALUES))

    def test_every_refusal_message_of_the_predicate_is_covered(self):
        """Each return of final_adjudication_error and of the record's own branches appears in CASES."""
        from joulewise.align.apple import light_triage
        tree = ast.parse(Path(light_triage.__file__).read_text())
        func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    and n.name == 'final_adjudication_error')
        heads = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Return) and node.value is not None:
                value = node.value
                while isinstance(value, ast.BinOp):
                    value = value.left
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    heads.add(value.value)
        heads |= {'no final sources', 'light triage unreadable: ', 'final sources unreadable: '}
        prefixes = [case[4] for case in CASES if case[4] is not None]
        for head in heads:
            self.assertTrue(any(p.startswith(head) for p in prefixes), head)

    def test_finality_is_the_only_writer(self):
        """No reader in the builder or the session re-derives finality from final_evidence() on its own."""
        for path in ('scripts/align_v4_next_arm_packet.py', 'scripts/align_v4_session.py'):
            tree = ast.parse((REPO / path).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name in ('final_evidence', 'is_final', 'finality',
                                                                       '_finality_evidence'):
                    continue
                if isinstance(node, ast.FunctionDef):
                    for call in ast.walk(node):
                        if (isinstance(call, ast.Compare) and isinstance(call.left, ast.Call)
                                and isinstance(call.left.func, ast.Attribute)
                                and call.left.func.attr == 'final_evidence'):
                            self.fail(f'{path}:{call.lineno} compares final_evidence() itself')
        source = (REPO / 'scripts/align_v4_next_arm_packet.py').read_text()
        self.assertEqual(source.count('final_adjudication_error('), 1)

    def test_no_release_or_override_exists_for_desk_failed(self):
        self.assertEqual(cad.RULING_RESETS, ('zero_capture_escalation',))
        self.assertEqual(builder.THERMAL_FAIL_RESET, 'u1_u3_fail_escalation')
        for path in ('scripts/align_v4_next_arm_packet.py', 'scripts/align_v4_session.py',
                     'scripts/align_v4_series.py', 'joulewise/align/apple/v4_cadence.py'):
            for number, line in enumerate((REPO / path).read_text().splitlines(), 1):
                if 'desk_failed' in line and not line.lstrip().startswith('#'):
                    self.assertFalse(any(word in line for word in ('resets', 'lead_ruling', 'release', 'admit')),
                                     f'{path}:{number}')
        source = (REPO / 'scripts/align_v4_next_arm_packet.py').read_text()
        self.assertIn("require(reset in ('zero_capture_escalation', THERMAL_FAIL_RESET)", source)
        session_source = (REPO / 'scripts/align_v4_session.py').read_text()
        self.assertEqual(session_source.count("ruling['resets'] =="), 1)

    def test_desk_failed_refuses_k_plus_2_exactly_as_before(self):
        packet = provisional_then_bound(
            self, lambda c: c.final_sources['desk'].update(harvest_status='program_fault')).build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertFalse(packet['packet_preflight']['ready'])


class CarriedFieldTests(unittest.TestCase):
    def test_window_chain_entries_carry_the_value_and_reason(self):
        s = Scenario(_root(self), 'W1').finish()
        root = s.root
        c1 = Scenario(root, 'C1', previous=s).finish()
        c2 = Scenario(root, 'C2', previous=c1, provisional=True).finish()
        packet = c2.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        for entry in packet['window_chain']:
            self.assertEqual(set(entry), LEGACY_CHAIN_KEYS | {'finality', 'finality_reason'})
        self.assertEqual([(e['window'], e['finality'], e['finality_reason']) for e in packet['window_chain']],
                         [('W1', 'final', None), ('C1', 'final', None), ('C2', 'provisional', 'no final sources')])
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'provisional'])

    def test_held_window_rows_carry_the_value_beside_final(self):
        s = Scenario(_root(self), 'W1').finish()
        c1 = Scenario(s.root, 'C1', previous=s).finish()
        c2 = Scenario(s.root, 'C2', previous=c1, provisional=True).finish()
        row = session.held_window_check(c2.root, c2.build())
        by_window = {r['window']: r for r in row['windows']}
        self.assertEqual(by_window['C1']['finality'], 'final')
        self.assertTrue(by_window['C1']['final'])
        self.assertEqual(by_window['C2']['finality'], 'provisional')
        self.assertFalse(by_window['C2']['final'])
        self.assertEqual(by_window['C2']['finality_reason'], 'no final sources')
        self.assertEqual(row['finality'], 'provisional')       # the previous window's row is lifted, as before


def _load_base_builder():
    """The builder exactly as it was at BASE, imported under another name; None when BASE is absent."""
    try:
        raw = subprocess.run(['git', '-C', str(REPO), 'show', f'{BASE}:scripts/align_v4_next_arm_packet.py'],
                             check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    spec = importlib.util.spec_from_loader('rl108_base_next_arm_packet', loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(REPO / 'scripts/align_v4_next_arm_packet.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def _strip_new_fields(packet):
    packet = copy.deepcopy(packet)
    for entry in packet.get('window_chain', []):
        entry.pop('finality', None)
        entry.pop('finality_reason', None)
    return packet


class BaseEquivalenceTests(unittest.TestCase):
    """Packets built by today's builder and by BASE's agree byte for byte once the two new keys are removed."""

    def test_packets_equal_base_except_the_new_fields(self):
        base = _load_base_builder()
        if base is None:
            self.skipTest(f'{BASE[:9]} not in this clone')
        for label, factory, _window, _value, _prefix in CASES + (
                ('two finals then provisional', lambda t: (lambda s: Scenario(s.root, 'C2', previous=Scenario(
                    s.root, 'C1', previous=s).finish(), provisional=True).finish())(Scenario(_root(t), 'W1').finish()),
                 None, None, None),):
            with self.subTest(label):
                s = factory(self)
                try:
                    new = json.dumps(_strip_new_fields(s.build()), sort_keys=True, default=str)
                except (ValueError, KeyError, TypeError, AttributeError) as exc:
                    new = ('raised', type(exc).__name__, str(exc))
                try:
                    old = json.dumps(base.build_packet(s.root, **s.identities(), now_epoch_s=111.0,
                                                       current_artifact_set_sha256=self._current(s)),
                                     sort_keys=True, default=str)
                except (ValueError, KeyError, TypeError, AttributeError) as exc:
                    old = ('raised', type(exc).__name__, str(exc))
                self.assertEqual(new, old)

    @staticmethod
    def _current(s):
        from joulewise.align.apple import v4_registration as registration
        return registration.artifact_set_digest(s.root)


if __name__ == '__main__':
    unittest.main()
