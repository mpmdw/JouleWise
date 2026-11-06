"""Producer preparation preserves authentication, primary authority and refusal order."""
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from joulewise import analysis_run_cache as arc
from joulewise.authentication_io import V2AuthenticationReadSession, V2AuthenticationInputError, read_authentication_input
from joulewise.b5_analysis import pack_parallel as pp
from joulewise.b5_analysis.archive import ArchiveHandle
from joulewise.b5_analysis.deadline_observer import DeadlineObserver
from joulewise.b5_analysis.producer_parallel import prepare_producer, consume_prepared
from joulewise.b5_analysis.windows import AnalysisRefusal
from joulewise.whole_window import ArchiveContext
from scripts import mint_floor_artifact_generalized as mint


def entries(root):
    result = {}
    for pack in ('alpha', 'beta'):
        archive_root = root / pack
        source = archive_root / 'sources/inputs/acceptance.json'
        bracket = archive_root / 'derived/bracket-binding.json'
        source.parent.mkdir(parents=True, exist_ok=True)
        bracket.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b'{}')
        bracket.write_bytes(b'{}')
        expected = hashlib.sha256(b'{}').hexdigest()
        (archive_root / 'sources/SHA256SUMS').write_text(expected + '  inputs/acceptance.json\n')
        window = SimpleNamespace(claim_runs_root=root / (pack + '-runs'), archive_root=archive_root,
                                 record=SimpleNamespace(record_shape='pin4'))
        archive = ArchiveHandle(window, {'outputs': {'derived/bracket-binding.json': expected}}, {})
        result[pack] = SimpleNamespace(window=window, archive=archive, archive_context=ArchiveContext(archive_root))
        # Different authentication failures. Alpha must precede beta even if
        # the beta bracket refusal finishes earlier in a spawned process.
        (source if pack == 'alpha' else bracket).write_bytes(b'{"changed":true}')
    return result


def governed_spec(path):
    mint._allow_governed_extraction_spec(path)
    return read_authentication_input(path, grammar='json', label='synthetic governed producer spec')


class ProducerParallelTests(unittest.TestCase):
    def test_success_restores_governed_authority_before_replaying_first_read(self):
        with tempfile.TemporaryDirectory(prefix='producer-vocabulary-') as tmp:
            paths = [Path(tmp) / pack / 'extraction_spec.json' for pack in ('alpha', 'beta')]
            for path in paths:
                path.parent.mkdir()
                path.write_bytes(b'{}')
            results = []
            for workers in (1, 3):
                with arc.analysis_run_caches({}, workers=workers) as caches, V2AuthenticationReadSession() as session:
                    caches.deadline = DeadlineObserver()
                    calls = [((path,), {}) for path in paths]
                    outcomes = pp.pack_map(governed_spec, calls)
                    if workers == 3:
                        self.assertTrue(all(outcome.ok for outcome in outcomes))
                    values = []
                    for path, outcome in zip(paths, outcomes or [None, None]):
                        values.append(consume_prepared(outcome, lambda: governed_spec(path), path.parent))
                        # This is also required by the later pinset reader. It
                        # refuses if the first row was replayed without authority.
                        mint._allow_governed_extraction_spec(path)
                        self.assertTrue(session.vocabulary_flag(str(path.resolve())))
                    results.append((values, tuple(vars(r) for r in session.records.values())))
            self.assertEqual(*results)

    def test_composition_first_pack_authentication_failure_matches_serial(self):
        with tempfile.TemporaryDirectory(prefix='producer-compose-order-') as tmp:
            root = Path(tmp)
            calls = []
            for pack in ('alpha', 'beta'):
                window = SimpleNamespace(pack_id=pack, archive_root=root / pack)
                path = window.archive_root / ('sources/repo/configs/campaigns/' + pack + '/plan_tree.json')
                if pack == 'alpha':
                    path.parent.mkdir(parents=True)
                    path.write_bytes(b'{invalid-json')
                calls.append(((window, None, None, True, root), {}))
            results = []
            for workers in (1, 3):
                with arc.analysis_run_caches({}, workers=workers) as caches, V2AuthenticationReadSession() as session:
                    caches.deadline = DeadlineObserver()
                    outcomes = pp.pack_map(mint._compose_indexed_producer, calls)
                    try:
                        for (args, kwargs), outcome in zip(calls, outcomes or [None, None]):
                            pp.consume(outcome, lambda: mint._compose_indexed_producer(*args, **kwargs))
                    except V2AuthenticationInputError as exc:
                        results.append((type(exc), str(exc), tuple(vars(r) for r in session.records.values())))
            self.assertEqual(len(results), 2)
            self.assertEqual(*results)
            self.assertTrue(results[0][1].startswith('v2_authentication_invalid_json:'))

    def test_first_authenticated_producer_refusal_and_partial_census_match_serial(self):
        with tempfile.TemporaryDirectory(prefix='producer-order-') as tmp:
            root = Path(tmp)
            results = []
            before = dict(mint.BLOCK5_PRODUCERS)
            for workers in (1, 3):
                producers = entries(root)
                calls = [((entry, root / (pack + '-report.json'), root, {}, pack), {})
                         for pack, entry in producers.items()]
                with arc.analysis_run_caches({}, workers=workers) as caches, V2AuthenticationReadSession() as session:
                    caches.deadline = DeadlineObserver()
                    outcomes = pp.pack_map(prepare_producer, calls)
                    try:
                        for (args, kwargs), outcome in zip(calls, outcomes or [None, None]):
                            pp.consume(outcome, lambda: prepare_producer(*args, **kwargs))
                    except mint.MintError as exc:
                        results.append((str(exc), tuple(vars(r) for r in session.records.values()),
                                        {p: e.archive.census() for p, e in producers.items()}))
                self.assertEqual(mint.BLOCK5_PRODUCERS, before)
            self.assertEqual(*results)
            self.assertIn('sources/inputs/acceptance.json', results[0][0])

    def test_sensitivity_context_never_enters_registered_producer_preparation(self):
        entry = SimpleNamespace(archive_context=ArchiveContext(Path('/synthetic-only'), sensitivity_bound_s=.1))
        with self.assertRaisesRegex(AnalysisRefusal, '^sensitivity_context_on_registered_path$'):
            prepare_producer(entry, None, None, {}, 'alpha')


if __name__ == '__main__':
    unittest.main()
