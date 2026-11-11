"""Synthetic differential witness for the exporter lane's ARM terminal refactor.

The reference is the complete nested terminal() from r11 at
52f36f1d8d718f90d3e0d390c53275bce5f3e9c1, amended only for the admitted
454d78142 (RL-35 F-09) git delivery receipt branch. The candidate is extracted from
the installed build_packet AST, so this exercises its actual helper calls and
the restored `started` lookup. No historical Git objects are needed at test time.
Only GitEvidence.git is replaced: source decoding, digest authentication,
WindowRecord.source/captures and terminal_window_release remain production code.
No evidence files, Git subprocesses, measurement data, model runtimes or network are used.
"""
import ast
import copy
import inspect
import itertools
import json
import textwrap
import unittest
from unittest.mock import patch

from scripts import align_v4_next_arm_packet as builder


REFERENCE_COMMIT = '52f36f1d8d718f90d3e0d390c53275bce5f3e9c1'
COMMIT = 'a' * 40


def reference_terminal():
    plan, result = previous.source('plan'), previous.source('result')
    require(result.get('schema') == 'joulewise.unattended_night_result.v1', 'terminal result schema missing')
    names = previous.record['sources']
    started, exited = names.get('chain_started') is not None, names.get('chain_exited') is not None
    courier = previous.source('courier')
    previous.source('courier_sent', json_value=False)  # native courier creates an empty marker with touch
    # RL-35 F-09 (454d78142): authenticated git delivery also closes the courier.
    if courier.get('sent') is not True:
        receipt = previous.source('courier_delivery')
        require(receipt.get('transport') == 'git-push' and receipt.get('plan_id') == plan['plan_id']
                and receipt.get('ref') == 'refs/heads/night-results/' + plan['plan_id']
                and receipt.get('result_sha256') == digest(previous.source('result', json_value=False))
                and isinstance(receipt.get('commit'), str)
                and re.fullmatch(r'[0-9a-f]{40,64}', receipt['commit']) is not None,
                'courier delivery missing or for another result')
    decision = terminal_window_release(result, plan_id=plan['plan_id'], receipt_class=plan['receipt_class'],
                now_epoch_s=prepared, chain_started=started, chain_exited=exited, courier_sent=True)
    require(decision.allowed, decision.reason)
    if exited:
        require(previous.source('chain_exited').get('exit_code') == result.get('chain_exit_code'),
                'chain closure and terminal result disagree')
    key = f"{plan['plan_id']}:{plan['custody_root']}:{digest(evidence.source(previous.commit, names['result'], json_value=False))}"
    latch = previous.source('watchdog_state').get('released_terminal_windows', [])
    require(isinstance(latch, list) and key in latch,
            'watchdog empty-process terminal latch missing or for another result')
    captured = previous.captures()
    require(started or not captured, 'null window carries captured members')
    return {'basis': 'B1 authenticated terminal result, chain closure, delivery and watchdog latch',
            'release_kind': decision.reason}


def function_node(function, nested=None):
    node = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]
    if nested is not None:
        return next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == nested)
    return node


REFERENCE = function_node(reference_terminal)
CANDIDATE = function_node(builder.build_packet, 'terminal')


class MemoryEvidence(builder.GitEvidence):
    def __init__(self, blobs):
        super().__init__('.')
        self.blobs = blobs
        self.operations = []

    def git(self, *args):
        self.operations.append(('git', args))
        if args[0] == 'ls-tree':
            path = args[-1]
            if path not in self.blobs:
                return b''
            return b'100644 blob ' + b'b' * 40 + b'\t' + path.encode() + b'\0'
        if args[0] == 'show':
            return self.blobs[args[1].split(':', 1)[1]]
        raise AssertionError(('unexpected Git command', args))

    def source(self, commit, descriptor, *, json_value=True):
        self.operations.append(('source', commit, copy.deepcopy(descriptor), json_value))
        return super().source(commit, descriptor, json_value=json_value)


def encoded(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


def fixture(*, started='present', exited='present', verdict='GO', sent=True,
            latch='valid', captured=True):
    values = {
        'plan': {'plan_id': 'synthetic', 'receipt_class': 'HAZARD_PACK',
                 'custody_root': '/DO-NOT-FOLLOW/synthetic'},
        'result': {'schema': 'joulewise.unattended_night_result.v1', 'plan_id': 'synthetic',
                   'receipt_class': 'HAZARD_PACK', 'verdict': verdict, 'ended_epoch_s': 100,
                   'chain_exit_code': 0 if started == 'present' else None,
                   'chain_sha256': 'c' * 64 if started == 'present' else None},
        'chain_started': {'pgid': 123},
        'chain_exited': {'exit_code': 0},
        'courier': {'sent': sent}, 'courier_sent': b'',
        'collection_plan': {'members': [{'run_id': 'tiny'}]},
    }
    key = 'synthetic:/DO-NOT-FOLLOW/synthetic:' + builder.digest(encoded(values['result']))
    values['watchdog_state'] = {
        'valid': {'released_terminal_windows': [key]},
        'missing': {},
        'foreign': {'released_terminal_windows': ['another-result']},
        'non-list': {'released_terminal_windows': key},
    }[latch]
    blobs, sources = {}, {}
    for name, value in values.items():
        path = 'synthetic/' + name
        raw = value if isinstance(value, bytes) else encoded(value)
        blobs[path] = raw
        sources[name] = {'path': path, 'sha256': builder.digest(raw)}
    for name, state in (('chain_started', started), ('chain_exited', exited)):
        if state == 'missing':
            sources.pop(name)
        elif state == 'null':
            sources[name] = None
    blobs['synthetic/capture'] = b'{"synthetic":true}\n'
    capture = {'path': 'synthetic/capture', 'sha256': builder.digest(blobs['synthetic/capture'])}
    return {'sources': sources, 'captures': {'tiny': capture if captured else None}}, blobs


def run_terminal(node, record, blobs, now):
    evidence = MemoryEvidence(copy.deepcopy(blobs))
    previous = object.__new__(builder.WindowRecord)
    previous.evidence, previous.commit, previous.path = evidence, COMMIT, 'synthetic/record'
    previous.record, previous.final_from = copy.deepcopy(record), None
    release = builder.terminal_window_release

    def traced_release(result, **kwargs):
        evidence.operations.append(('release', copy.deepcopy(result), kwargs))
        return release(result, **kwargs)

    namespace = dict(builder.__dict__, previous=previous, evidence=evidence, prepared=now,
                     terminal_window_release=traced_release)
    module = ast.Module(body=[copy.deepcopy(node)], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), '<synthetic-terminal>', 'exec'), namespace)
    with patch.object(builder, 'terminal_window_release', traced_release):
        try:
            outcome = ('return', namespace[node.name]())
        except Exception as exc:
            outcome = ('raise', type(exc).__name__, str(exc))
    # Byte comparison includes the result/refusal text, operation order (even failed
    # source attempts), exact source inventory and accesses, and any input mutation.
    return encoded([outcome, evidence.operations, evidence.accessed, evidence.inventory,
                    previous.record]), evidence.blobs


class TerminalEquivalenceTests(unittest.TestCase):
    def assert_equivalent(self, record, blobs, now=111):
        self.assertEqual(run_terminal(REFERENCE, record, blobs, now),
                         run_terminal(CANDIDATE, record, blobs, now))

    def test_git_delivery_receipt_and_field_faults_match_amended_reference(self):
        valid = {'transport': 'git-push', 'plan_id': 'synthetic',
                 'ref': 'refs/heads/night-results/synthetic', 'commit': 'd' * 40}
        for field in (None, *valid, 'result_sha256'):
            with self.subTest(field=field):
                record, blobs = fixture(sent=False)
                receipt = {**valid, 'result_sha256': builder.digest(blobs['synthetic/result'])}
                if field is not None:
                    receipt[field] = 'wrong'
                raw = encoded(receipt)
                blobs['synthetic/courier_delivery'] = raw
                record['sources']['courier_delivery'] = {
                    'path': 'synthetic/courier_delivery', 'sha256': builder.digest(raw)}
                self.assert_equivalent(record, blobs)
                if field is None:
                    self.assertIn(b'collected_window', run_terminal(CANDIDATE, record, blobs, 111)[0])

    def test_expanded_checks_match_reference_ast(self):
        """Check statement identity after only the three reviewed substitutions.

        1. Split the old left-to-right plan/result assignment and inline helpers.
        2. Rewrite the old raw result lookup through WindowRecord.source, which
           delegates to exactly that evidence.source for the non-final 'result'.
           Earlier successful result reads guarantee names['result'] exists.
        3. Elide the repeated started lookup of the same immutable JSON dict.
        These are source-level facts, not assumptions about grid coverage.
        """
        def shape(node):
            return ast.dump(node, include_attributes=False)

        def statement(source):
            return ast.parse(source).body[0]

        old_raw = shape(ast.parse(
            "evidence.source(previous.commit, names['result'], json_value=False)", mode='eval').body)

        class BindHelper(ast.NodeTransformer):
            def visit_Name(self, node):
                replacements = {'record': 'previous', 'now_epoch_s': 'prepared'}
                return ast.copy_location(ast.Name(id=replacements.get(node.id, node.id), ctx=node.ctx), node)

        class RawResultLookup(ast.NodeTransformer):
            def visit_Call(self, node):
                if shape(node) == old_raw:
                    return ast.parse("previous.source('result', json_value=False)", mode='eval').body
                return self.generic_visit(node)

        reference = copy.deepcopy(REFERENCE.body)
        reference[:1] = [statement("plan = previous.source('plan')"),
                         statement("result = previous.source('result')")]
        reference = [RawResultLookup().visit(node) for node in reference]
        release_call = shape(statement('decision = terminal_release_check(previous, plan, prepared)'))
        latch_call = shape(statement('watchdog_latch_check(previous, plan)'))
        repeated_start = shape(statement("started = previous.record['sources'].get('chain_started') is not None"))
        expanded = []
        for node in copy.deepcopy(CANDIDATE.body):
            if shape(node) in (release_call, latch_call):
                helper = (builder.terminal_release_check if shape(node) == release_call
                          else builder.watchdog_latch_check)
                body = copy.deepcopy(function_node(helper).body)
                self.assertIsInstance(body.pop(0).value, ast.Constant)  # docstring
                if helper is builder.terminal_release_check:
                    self.assertEqual(shape(body.pop()), shape(statement('return decision')))
                expanded.extend(BindHelper().visit(n) for n in body)
            elif shape(node) != repeated_start:
                expanded.append(node)
        self.assertEqual([shape(n) for n in reference], [shape(n) for n in expanded])

    def test_cartesian_terminal_variants(self):
        count = 0
        for start, exit_, verdict, sent, latch, captured, now in itertools.product(
                ('missing', 'null', 'present'), ('missing', 'null', 'present'),
                ('GO', 'REFUSED', 'ABORTED', 'CHAIN_STOPPED', 'UNKNOWN', None),
                (True, False, 1, None), ('valid', 'missing', 'foreign', 'non-list'),
                (False, True), (99, 100, 111)):
            with self.subTest(start=start, exit=exit_, verdict=verdict, sent=sent,
                              latch=latch, captured=captured, now=now):
                record, blobs = fixture(started=start, exited=exit_, verdict=verdict, sent=sent,
                                        latch=latch, captured=captured)
                self.assert_equivalent(record, blobs, now)
                count += 1
        self.assertEqual(count, 5184)

    def test_missing_malformed_and_unauthenticated_sources(self):
        names = tuple(fixture()[0]['sources'])
        for name, fault in itertools.product(names, ('missing', 'null', 'descriptor', 'digest',
                                                   'unavailable', 'json', 'non-object')):
            with self.subTest(name=name, fault=fault):
                record, blobs = fixture()
                descriptor = record['sources'][name]
                if fault == 'missing':
                    del record['sources'][name]
                elif fault == 'null':
                    record['sources'][name] = None
                elif fault == 'descriptor':
                    descriptor['extra'] = True
                elif fault == 'digest':
                    descriptor['sha256'] = '0' * 64
                elif fault == 'unavailable':
                    del blobs[descriptor['path']]
                else:
                    raw = b'{' if fault == 'json' else b'null'
                    blobs[descriptor['path']] = raw
                    descriptor['sha256'] = builder.digest(raw)
                self.assert_equivalent(record, blobs)

    def test_field_faults_and_competing_refusal_order(self):
        variants = {
            'plan': ('plan_id', 'receipt_class', 'custody_root'),
            'result': ('schema', 'plan_id', 'receipt_class', 'ended_epoch_s', 'verdict',
                       'chain_exit_code', 'chain_sha256'),
            'courier': ('sent',), 'chain_exited': ('exit_code',),
            'watchdog_state': ('released_terminal_windows',),
        }
        for name, fields in variants.items():
            for field, value in itertools.product(fields, ('absent', None, False, 1, 'wrong', [], {})):
                with self.subTest(name=name, field=field, value=value):
                    record, blobs = fixture()
                    descriptor = record['sources'][name]
                    source = builder.decode(blobs[descriptor['path']])
                    if value == 'absent':
                        source.pop(field, None)
                    else:
                        source[field] = value
                    blobs[descriptor['path']] = encoded(source)
                    descriptor['sha256'] = builder.digest(blobs[descriptor['path']])
                    # Leave the old result latch in place: result mutations that
                    # reach it must refuse there, after any release/closure fault.
                    self.assert_equivalent(record, blobs)
        for now in (None, True, 'invalid', float('inf'), float('nan')):
            with self.subTest(now=now):
                self.assert_equivalent(*fixture(), now=now)

    def test_positive_controls_and_restored_started_guard(self):
        cases = [
            ({}, 'collected_window'),
            ({'verdict': 'CHAIN_STOPPED'}, 'chain_stopped'),
            ({'started': 'missing', 'exited': 'missing', 'verdict': 'REFUSED',
              'captured': False}, 'null_window'),
        ]
        for options, reason in cases:
            record, blobs = fixture(**options)
            self.assert_equivalent(record, blobs)
            actual = json.loads(run_terminal(CANDIDATE, record, blobs, 111)[0])[0]
            self.assertEqual(actual, ['return', {
                'basis': 'B1 authenticated terminal result, chain closure, delivery and watchdog latch',
                'release_kind': reason}])
        record, blobs = fixture(started='missing', exited='missing', verdict='REFUSED', captured=True)
        self.assert_equivalent(record, blobs)
        actual = json.loads(run_terminal(CANDIDATE, record, blobs, 111)[0])[0]
        self.assertEqual(actual, ['raise', 'ValueError', 'null window carries captured members'])


if __name__ == '__main__':
    unittest.main()
