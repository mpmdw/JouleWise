"""Synthetic checks for the RL-38 reader; never opens study custody."""
import hashlib
import importlib.util
import csv
from contextlib import redirect_stdout
from decimal import localcontext
import io
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).absolute().parents[2] / 'docs/analysis/b5/hand_check_phase2.py'
spec = importlib.util.spec_from_file_location('phase2_reader', SCRIPT)
reader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader_module)
ext_spec = importlib.util.spec_from_file_location('rl52_reader', SCRIPT.with_name('hand_check_rl52.py'))
extension = importlib.util.module_from_spec(ext_spec)
ext_spec.loader.exec_module(extension)
r2_spec = importlib.util.spec_from_file_location('rl52_round2_reader', SCRIPT.with_name('hand_check_rl52_round2.py'))
round2 = importlib.util.module_from_spec(r2_spec)
r2_spec.loader.exec_module(round2)


class AccessBoundaryTests(unittest.TestCase):
    def test_other_root_is_rejected_before_stat(self):
        with patch.object(Path, 'lstat', side_effect=AssertionError('filesystem touched')):
            with self.assertRaisesRegex(ValueError, 'outside unseal'):
                reader_module.CustodyReader.checked_path(Path('/unapproved'), 'file.json')

    def test_absolute_and_parent_paths_are_rejected_before_stat(self):
        for relative in ('/outside.json', '../outside.json', 'sub/../../outside.json'):
            with self.subTest(relative=relative):
                with patch.object(Path, 'lstat', side_effect=AssertionError('filesystem touched')):
                    with self.assertRaisesRegex(ValueError, 'outside unseal'):
                        reader_module.CustodyReader.checked_path(reader_module.ROOT_A, relative)

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'link').symlink_to(root/'absent-target')
            with patch.object(reader_module, 'ROOT_A', root):
                with self.assertRaisesRegex(ValueError, 'symlink refused'):
                    reader_module.CustodyReader.checked_path(root, 'link')

    def test_wrong_hash_refuses_before_json_parse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'bad.json').write_bytes(b'not JSON')
            source = {'TEST': (root, 'bad.json', '0'*64)}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                with patch.object(reader_module.json, 'loads', side_effect=AssertionError('parsed unverified bytes')):
                    with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                        reader_module.CustodyReader().read('TEST')

    def test_changed_file_refuses_end_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b'{"count": 2}'
            p = root/'sample.json'
            p.write_bytes(payload)
            source = {'TEST': (root, p.name, hashlib.sha256(payload).hexdigest())}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                reader = reader_module.CustodyReader()
                self.assertEqual(reader.read('TEST'), {'count': 2})
                p.write_bytes(b'{"count": 3}')
                with self.assertRaisesRegex(ValueError, 'changed during read'):
                    reader.finish()

    def test_projection_prefix_needs_content_name_and_full_record_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b'{}'
            digest = hashlib.sha256(payload).hexdigest()
            p = root/(digest+'-projection.json')
            p.write_bytes(payload)
            source = {'TEST': (root, p.name, digest[:12])}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                reader = reader_module.CustodyReader()
                with self.assertRaisesRegex(ValueError, 'read REC first'):
                    reader.read('TEST')
                reader.projection_pins.add(digest)
                self.assertEqual(reader.read('TEST'), {})
                self.assertEqual(reader.finish()['TEST']['sha256_after'], digest)


class IndependentArithmeticTests(unittest.TestCase):
    def test_student_tail_has_closed_form_witnesses(self):
        self.assertAlmostEqual(reader_module.student_tail(1, 1), .5, places=14)
        self.assertAlmostEqual(reader_module.student_tail(1, 2), 1-1/math.sqrt(3), places=14)
        self.assertAlmostEqual(reader_module.t975(5), 2.570581835636314, places=12)

    def test_fixed_stratum_weights_survive_unequal_unit_counts(self):
        result = reader_module.stratified([0, 2, 4], [9, 11])
        self.assertAlmostEqual(result['mean'], 8.4)
        self.assertNotAlmostEqual(result['mean'], (0+2+4+9+11)/5)
        self.assertEqual((result['n_r'], result['n_b'], result['df']), (3, 2, 1))

    def test_quad_orientation(self):
        members = [{'E_j': {'decode': x}} for x in (2, 10, 14, 6)]
        self.assertEqual(reader_module.quad_difference(members, 'decode'), 8)

    def test_common_sign_is_distinct_from_independent_corners(self):
        values = [0]*5
        shared = reader_module.widened_floor(values, [0]*5, False, common=[1]*5)
        independent = reader_module.widened_floor(values, [1]*5, False)
        self.assertEqual(shared, 1)
        self.assertGreater(independent, shared)

    def test_absolute_floor_recenters_comparative_does_not(self):
        self.assertEqual(reader_module.point_floor([10]*5, True), 0)
        self.assertEqual(reader_module.point_floor([10]*5, False), 10)

    def test_printed_precision_does_not_accept_a_real_disagreement(self):
        self.assertEqual(reader_module.printed_compare('1.23', 1.234)[2], 'within-rounding')
        self.assertEqual(reader_module.printed_compare('1.23', 1.236)[2], 'MISMATCH')
        self.assertEqual(reader_module.printed_compare('36%', .3606)[0], '36%')
        self.assertEqual(reader_module.printed_compare('78,389', 78389)[2], 'exact')


class PrintAuthorityTests(unittest.TestCase):
    def test_residual_precision_cannot_recover_full_input(self):
        cases = {'0.006543219876543': '0.0065', '-0.000076543219876': '-0.000077',
                 '0.00999': '0.010', '1.99999999999999999e-24': '2.0e-24',
                 '-0.000000': '0', '-1 distinct cause': '-1 distinct cause', '': ''}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(reader_module.difference_text(value), expected)
        self.assertEqual(reader_module.printed_compare('36%', .36064268123456)[1], '0.064')
        # Classification happens before rounding the difference.
        self.assertEqual(reader_module.printed_compare('1.23', 1.23501)[2], 'MISMATCH')
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            reader_module.difference_text('Infinity')

    def test_source_residual_in_note_is_also_rounded(self):
        rows = [{'difference': '0.00025888888888888',
                 'note': 'SOURCED: example; source difference=-0.000987654321; HAND: synthetic'}]
        reader_module.round_differences(rows)
        self.assertEqual(rows[0]['difference'], '0.00026')
        self.assertIn('source difference=-0.00099;', rows[0]['note'])

    def test_normalized_paths_collapse_lists_and_contrasts(self):
        contrast = {'floor': {'point_floor_diagnostics': {'value': 1, 'valid': True},
                              'resolutions': [{'point_floor_diagnostics': {'value': 2}}]},
                    'claim_evaluation': {'floor_limit': {'entries': [{'bound': 2}, {'bound': 3}],
                                                       'status': 'synthetic'}}}
        self.assertEqual(reader_module.dle5_leaf_counts([contrast, contrast]), (5, 12))

    def test_repository_mode_never_constructs_custody_reader(self):
        with patch.object(reader_module.CustodyReader, '__init__', side_effect=AssertionError('custody reader constructed')):
            with patch('sys.argv', [str(SCRIPT), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                reader_module.main()
        self.assertIn('"byte_identical": true', output.getvalue())

    def test_opus_repository_mode_never_computes_from_custody(self):
        opus_path = SCRIPT.with_name('opus_coldreview_check.py')
        spec = importlib.util.spec_from_file_location('opus_reader', opus_path)
        opus = importlib.util.module_from_spec(spec)
        with localcontext():
            spec.loader.exec_module(opus)
            with patch.object(opus, 'compute', side_effect=AssertionError('custody compute called')):
                with patch.object(opus, 'load', side_effect=AssertionError('custody load called')):
                    with patch('sys.argv', [str(opus_path), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                        opus.main()
        self.assertIn('"rounded_hand_table_byte_identical": true', output.getvalue())

    def test_rulings_are_idempotent_and_count_drift_stops(self):
        with SCRIPT.with_name('rederivation.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        original = reader_module.table_text(rows)
        reader_module.apply_print_rulings(rows)
        self.assertEqual(reader_module.table_text(rows), original)
        rows[0]['match'] = 'MISMATCH'
        with self.assertRaisesRegex(ValueError, 'STOP: RL-42 counts differ'):
            reader_module.apply_print_rulings(rows)


class Round3RepositoryGateTests(unittest.TestCase):
    @staticmethod
    def load_script(name):
        path = SCRIPT.with_name(name) if name != 'fill_check_b5.py' else SCRIPT.parents[2]/'paper/paper1'/name
        spec = importlib.util.spec_from_file_location('round3_' + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_round1_repository_mode_never_constructs_custody_reader(self):
        with patch.object(extension.ReleasedReader, '__init__', side_effect=AssertionError('custody reader constructed')):
            with patch('sys.argv', [str(extension.__file__), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                extension.main()
        self.assertIn('"round1_byte_identical": true', output.getvalue())

    def test_round2_repository_mode_never_constructs_custody_reader(self):
        with patch.object(round2.ReleasedReader, '__init__', side_effect=AssertionError('custody reader constructed')):
            with patch('sys.argv', [str(round2.__file__), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                round2.main()
        self.assertIn('"full_ledger_byte_identical": true', output.getvalue())

    def test_opus_extension_repository_mode_never_reads_custody(self):
        opus = self.load_script('opus_coldreview_rl52_check.py')
        with patch.object(opus, 'sha', side_effect=AssertionError('custody hash called')):
            with patch.object(opus, 'load', side_effect=AssertionError('custody load called')):
                with patch.object(opus, 'compute', side_effect=AssertionError('custody compute called')):
                    with patch('sys.argv', [str(opus.__file__), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                        opus.main()
        self.assertIn('"reviewed_bytes_identical": true', output.getvalue())

    def test_round1_native_replay_accepts_later_rows_without_changing_its_scope(self):
        # Replay serialization using frozen repo rows as stand-ins for custody
        # arithmetic. This tests the F3 comparison, not real recomputation.
        rows = list(csv.DictReader(io.StringIO(extension.round1_bytes().decode()), delimiter='\t'))[538:]
        with patch.object(extension, 'ReleasedReader') as reader:
            reader.return_value.read.return_value = {}
            reader.return_value.finish.return_value = {}
            with patch.object(extension, 'append_rows', return_value=rows):
                with patch('sys.argv', [str(extension.__file__)]), redirect_stdout(io.StringIO()):
                    extension.main()

    def test_round1_rejects_changed_original_or_round1_rows(self):
        raw = SCRIPT.with_name('rederivation.tsv').read_bytes()
        for index in (1, 539, 801):
            lines = raw.splitlines(keepends=True)
            cells = lines[index].split(b'\t')
            cells[0] += b'X'
            lines[index] = b'\t'.join(cells)
            with self.subTest(physical_row=index+1), self.assertRaisesRegex(ValueError, 'differ'):
                extension.check_round1_bytes(b''.join(lines))
        self.assertEqual(extension.check_round1_bytes(raw + b'later append\n'), extension.round1_bytes())

    def test_full_ledger_repository_modes_reject_changed_round2_row(self):
        raw = SCRIPT.with_name('rederivation.tsv').read_bytes()
        lines = raw.splitlines(keepends=True)
        lines[900] = lines[900].replace(b'\t', b'X\t', 1)
        changed = b''.join(lines)
        opus = self.load_script('opus_coldreview_rl52_check.py')
        for module in (round2, opus):
            with self.subTest(checker=module.__name__), patch.object(Path, 'read_bytes', return_value=changed):
                with self.assertRaisesRegex(ValueError, 'differ'):
                    module.repository_check()

    def test_repo_only_write_combination_is_rejected_before_custody(self):
        for module in (extension, round2):
            with self.subTest(checker=module.__name__):
                with patch.object(module.ReleasedReader, '__init__', side_effect=AssertionError('custody reader constructed')):
                    with patch('sys.argv', [str(module.__file__), '--repo-only', '--write']), redirect_stdout(io.StringIO()):
                        with patch('sys.stderr', io.StringIO()), self.assertRaises(SystemExit) as stopped:
                            module.main()
                        self.assertEqual(stopped.exception.code, 2)

    def test_fill_gate_checks_full_ledger_and_original_prefix(self):
        fill = self.load_script('fill_check_b5.py')
        rows = fill.load_ledger()
        self.assertEqual(len(rows), 1845)
        self.assertEqual(fill.FAILURES, [])
        raw = fill.LEDGER.read_bytes()
        original = extension.base_bytes()
        # Bypass the full hash pin to prove the original byte check is a
        # separate gate, not an incidental consequence of the whole-file hash.
        changed = raw.replace(b'\n', b' \n', 1)
        with patch.object(fill, 'AUTHORITY_SHA256', hashlib.sha256(changed).hexdigest()):
            fill.check_ledger_bytes(changed, original)
        self.assertTrue(any('original 538 rows' in f for f in fill.FAILURES))

    def test_fill_gate_rejects_perturbation_of_every_printed_value(self):
        fill = self.load_script('fill_check_b5.py')
        raw = fill.LEDGER.read_bytes()
        original = extension.base_bytes()
        lines = raw.splitlines(keepends=True)
        column = lines[0].decode().rstrip('\n').split('\t').index('printed_value')
        for number in range(1, len(lines)):
            cells = lines[number].split(b'\t')
            cells[column] += b'X'
            changed = b''.join(lines[:number]) + b'\t'.join(cells) + b''.join(lines[number+1:])
            fill.FAILURES.clear()
            fill.check_ledger_bytes(changed, original)
            with self.subTest(physical_row=number+1):
                self.assertTrue(any('extended print authority' in f for f in fill.FAILURES))

    @staticmethod
    def first_fill_text():
        # The admitted first fill, as immutable Git text; never replace the working-tree paper.
        return subprocess.run(['git', 'show',
                               'e5fd296715f21c7c3792e4f9743b7494b07813ec:docs/paper/paper1/paper1.md'],
                              cwd=SCRIPT.parents[3], check=True, capture_output=True, text=True).stdout

    def test_fill_gate_refuses_first_fill_ledger_precision_under_rl52(self):
        # The first fill printed ledger precision; RL-52's print-precision rule now refuses that text.
        fill = self.load_script('fill_check_b5.py')
        with patch.object(fill, 'PAPER') as paper, redirect_stdout(io.StringIO()) as output:
            paper.read_text.return_value = self.first_fill_text()
            self.assertEqual(fill.main(), 1)
        self.assertIn('ledger-rendered text', output.getvalue())

    def test_fill_gate_rejects_each_cited_paper_value_perturbation(self):
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        paper = fill.norm(fill.PAPER.read_text())
        cited = {int(m.group(1)) for _, _, template, _, _ in fill.SITES for m in fill.PH.finditer(template)}
        for number in sorted(cited):
            template = next(t for _, _, t, _, _ in fill.SITES
                            if any(int(m.group(1)) == number for m in fill.PH.finditer(t)))
            rendered = fill.rendered(template)
            changed = fill.rendered(fill.PH.sub(lambda m: m.group(0) + ('X' if int(m.group(1)) == number else ''),
                                                template))
            self.assertIn(fill.norm(rendered), paper)
            fill.FAILURES.clear()
            fill.check_sites(paper.replace(fill.norm(rendered), fill.norm(changed), 1))
            with self.subTest(physical_row=number):
                self.assertTrue(any('ledger-rendered text' in f for f in fill.FAILURES))

    def test_fill_gate_rejects_a_value_rounded_against_the_rule(self):
        # 146.63 J is row 15 rounded to nearest; one unit in the last place is refused.
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        paper = fill.PAPER.read_text()
        self.assertIn('by 146.63 J', paper)
        fill.FAILURES.clear()
        fill.check_sites(paper.replace('by 146.63 J', 'by 146.64 J', 1))
        self.assertTrue(any('ledger-rendered text' in f for f in fill.FAILURES))

    def test_fill_gate_requires_a_reason_for_ledger_precision(self):
        # RL-60/RL-52: the 1.7B prefill R_cm terms print at ledger precision only because rounding would flip a
        # comparison; with that reason removed the check refuses them, and rounding them is refused as a flip.
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        with patch.object(fill, 'FORCED_LEDGER', {}):
            fill.FAILURES.clear()
            fill.check_formats()
        self.assertTrue(any('ledger precision without a recorded comparison flip' in f for f in fill.FAILURES))
        sites = [(n, i, t.replace('{r849:ledger}', '{r849:e}').replace('{r850:ledger}', '{r850:e}'), c, lab)
                 for n, i, t, c, lab in fill.SITES]
        with patch.object(fill, 'SITES', sites):
            fill.FAILURES.clear()
            fill.check_comparisons()
        self.assertTrue(any('flips on the printed (rounded) values' in f and 'failed R_cm row 1846' in f
                            for f in fill.FAILURES))

    def test_fill_gate_appendix_c_is_the_producer_text(self):
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        paper = fill.PAPER.read_text()
        fill.FAILURES.clear()
        fill.check_appendix_c(paper)
        self.assertEqual(fill.FAILURES, [])
        i = paper.index('## Appendix C')
        fill.check_appendix_c(paper[:i] + paper[i:].replace('as part of B; X itself', 'X itself', 1))
        self.assertTrue(any('Appendix C differs' in f for f in fill.FAILURES))

    def test_fill_gate_rejects_a_format_outside_the_row_class(self):
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        site = next(i for i, s in enumerate(fill.SITES) if s[0] == 'Table 2, 1.7B decode')
        name, ids, template, count, labels = fill.SITES[site]
        with patch.object(fill, 'SITES', list(fill.SITES)) as sites:
            sites[site] = (name, ids, template.replace('{r133:e}', '{r133:mr}'), count, labels)
            fill.FAILURES.clear()
            fill.check_formats()
        self.assertTrue(any("is class 'J' but printed with format 'mr'" in f for f in fill.FAILURES))

    def test_fill_gate_rejects_a_rounding_that_flips_a_stated_comparison(self):
        # Synthetic: move d-bar to just above the decode gate; on the ledger it exceeds the gate, but rounded to
        # nearest beside a gate rounded up it does not. The check must refuse the rounding.
        fill = self.load_script('fill_check_b5.py')
        fill.L = fill.load_ledger()
        rows = {n: dict(r) for n, r in fill.L.items()}
        rows[15]['printed_value'] = '10.17900'
        for n in (48, 36, 63, 64):
            rows[n]['printed_value'] = '10.17850'
        rows[37]['printed_value'] = rows[49]['printed_value'] = '10.17950'
        with patch.object(fill, 'L', rows):
            fill.FAILURES.clear()
            fill.check_comparisons()
        self.assertTrue(any('flips on the printed (rounded) values' in f and 'decode: d̄ exceeds the floor gate' in f
                            for f in fill.FAILURES))
        self.assertFalse(any('false on the ledger values: decode: d̄ exceeds' in f for f in fill.FAILURES))


class LedgerExtensionTests(unittest.TestCase):
    def test_partial_reader_refuses_dry_m_before_filesystem_access(self):
        with patch.object(Path, 'lstat', side_effect=AssertionError('filesystem touched')):
            for alias in ('DISC', 'FILL', 'PROJ-A', 'REC', 'VER'):
                with self.subTest(alias=alias), self.assertRaisesRegex(ValueError, 'only RC'):
                    extension.ReleasedReader().read(alias)
            for root, rel in ((extension.h.ROOT_A, 'file.json'),
                              (extension.h.ROOT_B, 'restricted/file.json'),
                              (extension.h.ROOT_B, '../recompute.json')):
                with self.subTest(relative=rel), self.assertRaisesRegex(ValueError, 'only RC'):
                    extension.ReleasedReader.checked_path(root, rel)

    def test_original_ledger_prefix_is_immutable(self):
        self.assertTrue(SCRIPT.with_name('rederivation.tsv').read_bytes().startswith(extension.base_bytes()))
        original = list(csv.DictReader(io.StringIO(extension.base_bytes().decode()), delimiter='\t'))
        self.assertEqual(len(original), 538)

    def test_recompute_pin_cannot_silently_drift(self):
        source = {'RC':(extension.h.ROOT_B,'recompute.json','0'*64)}
        with patch.object(extension.h,'SOURCES',source):
            with patch.object(Path,'lstat',side_effect=AssertionError('filesystem touched')):
                with self.assertRaisesRegex(ValueError,'pin configuration changed'):
                    extension.ReleasedReader().read('RC')

    def test_extension_serializes_only_printed_precision_and_rounded_residual(self):
        fields = next(csv.reader(io.StringIO(extension.base_bytes().decode()), delimiter='\t'))
        ledger = extension.Ledger(fields)
        ledger.add('synthetic.aggregate', 1.234567891, 1.234567892, 'synthetic arithmetic')
        row = ledger.rows[0]
        self.assertEqual(row['printed_value'], '1.23457')
        self.assertEqual(row['rederived_value'], '1.23457')
        self.assertEqual(row['source_value'], '1.23457')
        self.assertEqual(row['difference'], '-0.0000021')
        self.assertEqual(row['match'], 'within-rounding')
        self.assertNotIn('1.23456789', reader_module.table_text(ledger.rows))
        ledger.add('synthetic.mismatch', 1.0, 2.0, 'bad stored leaf', kind='recorded-judgment')
        self.assertEqual(ledger.rows[-1]['match'], 'MISMATCH')

    def test_mixed_load_and_nonload_codes_are_never_restored(self):
        units = [{'unit_id': 'load', 'codes': ['contention.request_overlap']},
                 {'unit_id': 'mixed', 'codes': ['contention.request_overlap', 'member.failed']},
                 {'unit_id': 'empty', 'codes': []}]
        self.assertEqual([x['unit_id'] for x in extension.restored_load_units(units)], ['load'])

    @staticmethod
    def synthetic_cell():
        members = {}
        def put(key, energy, bound):
            members[key] = {'E_j': {'decode':energy}, 'a_bop_j':{'decode':bound}}
        put('repeat1',0,1)
        put('repeat2',2,3)
        for i, energy in enumerate((3,5),1):
            for position in ('a1','b1','b2','a2'):
                put(f'floor-decode-b{i:02}-{position}',energy,5)
        cell = {'model':'Qwen3-1.7B-4bit', 'phase':'decode',
                'kept_units':{'repeat':['repeat1','repeat2'], 'quad':['floor-b01','floor-b02']}}
        rc = {'members':{'ALPHA':members}, 'windows':{'ALPHA':{'neg8':{'allowance_j':2}}}}
        return rc, cell

    def test_kind_averages_are_stratified_and_attribution_uses_kept_members(self):
        rc, cell = self.synthetic_cell()
        rc['members']['ALPHA']['removed'] = {'E_j':{'decode':100},'a_bop_j':{'decode':99}}
        value = extension.cell_arithmetic(rc,cell)
        self.assertAlmostEqual(value['mean'],3.4)
        self.assertEqual(value['kind_averages_j'],[4.4,0,1])
        self.assertAlmostEqual(value['B_j'],5.4)
        self.assertNotEqual(value['attained_by'],'removed')
        self.assertEqual(value['minimum_j'],1)

    def test_cross_session_uses_quad_arm_means_for_scatter(self):
        rc, cell = self.synthetic_cell()
        gamma = {}
        for i, mean in enumerate((3,5,7),1):
            for position, energy in [('a1',mean-1),('a2',mean+1),('b1',1000),('b2',1000)]:
                gamma[f'gamma-decode-b{i:02}-{position}'] = {'E_j':{'decode':energy}}
        rc['members']['GAMMA'] = gamma
        rc['contrasts'] = {'contrast-decode-primary':{'kept_quads':['gamma-b01','gamma-b02','gamma-b03']}}
        value = extension.cross_arithmetic(rc,cell)
        self.assertAlmostEqual(value['delta_j'],1.6)
        self.assertAlmostEqual(value['h_G_j'],4.302652729749464*2/math.sqrt(3))
        self.assertTrue(value['agree'])
        for key, member in gamma.items():
            if key.endswith(('a1','a2')):
                member['E_j']['decode'] += 100
        self.assertFalse(extension.cross_arithmetic(rc,cell)['agree'])

    def test_quad_identity_ambiguity_refuses(self):
        rc, _ = self.synthetic_cell()
        members = rc['members']['ALPHA']
        members['duplicate-decode-b01-a1'] = members['floor-decode-b01-a1']
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            extension.quad_ids(members,'decode','floor-b01')

    def test_quantiles_interpolate_and_keep_endpoints(self):
        self.assertEqual(extension.percentile([1,5,9,13],.25),4)
        self.assertEqual(extension.percentile([1,5,9,13],.75),10)
        self.assertEqual(extension.percentile([7],.75),7)


class LedgerRound2Tests(unittest.TestCase):
    def test_only_exact_pinned_aliases_are_authorized(self):
        reader = round2.ReleasedReader()
        self.assertEqual(set(reader.sources), {'RC','FILL','DISC','EXC','PROJ-A','PROJ-B'})
        with patch.object(Path,'lstat',side_effect=AssertionError('filesystem touched')):
            for alias in ('REC','VER','STEP','night','unlisted'):
                with self.subTest(alias=alias), self.assertRaisesRegex(ValueError,'not an authorized pinned'):
                    reader.read(alias)
        self.assertTrue(all(len(pin)==64 for _,_,pin in reader.sources.values()))

    def test_full_projection_pin_drift_is_rejected(self):
        with SCRIPT.with_name('phase2_sources.tsv').open() as stream:
            manifest = list(csv.DictReader(stream,delimiter='\t'))
        next(x for x in manifest if x['alias']=='PROJ-A')['sha256_after'] = '0'*64
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer,manifest[0].keys(),delimiter='\t')
        writer.writeheader(); writer.writerows(manifest)
        with patch.object(Path,'open',return_value=io.StringIO(buffer.getvalue())):
            with self.assertRaisesRegex(ValueError,'pin configuration changed'):
                round2.ReleasedReader()

    def test_hash_failure_is_not_parsed_and_is_rehashed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'restricted').mkdir()
            p = root/'restricted/test.json'
            p.write_bytes(b'not JSON')
            reader = round2.ReleasedReader()
            reader.sources = {'DISC':(root,'restricted/test.json','0'*64)}
            with patch.object(round2.h,'ROOT_A',root):
                with patch.object(round2.json,'loads',side_effect=AssertionError('parsed unverified bytes')):
                    with self.assertRaisesRegex(ValueError,'hash mismatch before reading/parsing'):
                        reader.read('DISC')
                result = reader.finish()['DISC']
            self.assertEqual(result['sha256_before'],result['sha256_after'])
            self.assertNotEqual(result['sha256_before'],result['expected_sha256'])

    def test_pinned_reader_detects_post_parse_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            p=root/'test.json'; payload=b'{"count":1}'; p.write_bytes(payload)
            reader=round2.ReleasedReader()
            reader.sources={'RC':(root,p.name,hashlib.sha256(payload).hexdigest())}
            with patch.object(round2.h,'ROOT_A',root):
                self.assertEqual(reader.read('RC'),{'count':1})
                p.write_bytes(b'{"count":2}')
                with self.assertRaisesRegex(ValueError,'custody changed'):
                    reader.finish()

    def test_every_committed_row_is_an_immutable_prefix(self):
        prefix=round2.frozen_bytes()
        self.assertEqual(len(list(csv.DictReader(io.StringIO(prefix.decode()),delimiter='\t'))),801)
        self.assertTrue(SCRIPT.with_name('rederivation.tsv').read_bytes().startswith(prefix))
        fields=['key','value']; rows=[{'key':'new','value':'1'}]
        result=round2.append_only(b'prefix\n',b'prefix\n',rows,fields)
        self.assertEqual(result,b'prefix\nnew\t1\n')
        self.assertEqual(round2.append_only(result,b'prefix\n',rows,fields),result)
        for current in (b'changed\n',b'prefix\nold\t1\n'):
            with self.subTest(current=current), self.assertRaisesRegex(ValueError,'refuse'):
                round2.append_only(current,b'prefix\n',rows,fields)

    def test_neg8_uses_unequal_endpoint_sizes_and_corpus_variance(self):
        energies={f'c{i}':x for i,x in enumerate((-4,-2,0,2,4))}
        refs={'ref-start-1':1,'ref-start-2':2,'ref-start-3':3,
              'ref-end-1':5,'ref-end-2':7,'ref-midpoint':-10}
        result=round2.neg8_arithmetic(energies|refs,list(energies),list(refs))
        self.assertEqual(result['bound_envelope_j'],5)
        self.assertAlmostEqual(result['bound_prediction_j'],2.776*math.sqrt(10)*math.sqrt(5/6))
        self.assertEqual(result['screen_statistic_j'],4)
        self.assertEqual(result['trajectory_excursion_max_j'],16)
        self.assertEqual(result['drift_allowance_j'],16)
        self.assertEqual(result['decision'],'passed')

    def test_neg8_midpoint_changes_allowance_but_not_endpoint_screen(self):
        energies={f'c{i}':2 for i in range(12)}
        refs={'ref-start-1':2,'ref-start-2':2,'ref-end-1':2,'ref-end-2':2}
        plain=round2.neg8_arithmetic(energies|refs,list(energies),list(refs))
        refs['ref-midpoint']=9
        excursion=round2.neg8_arithmetic(energies|refs,list(energies),list(refs))
        self.assertEqual(plain['decision'],excursion['decision'])
        self.assertEqual(plain['drift_allowance_j'],0)
        self.assertEqual(excursion['drift_allowance_j'],7)
        refs['ref-end-1']=refs['ref-end-2']=3
        self.assertEqual(round2.neg8_arithmetic(energies|refs,list(energies),list(refs))['decision'],'failed')
        del refs['ref-end-2']
        with self.assertRaisesRegex(ValueError,'reference roster'):
            round2.neg8_arithmetic(energies|refs,list(energies),list(refs))

    def test_temperature_readability_and_strict_thresholds(self):
        self.assertEqual(round2.temperature_arithmetic([None])['temperature_unmeasured'],True)
        self.assertFalse(round2.temperature_arithmetic([3000,3300])['producer_flag'])
        self.assertTrue(round2.temperature_arithmetic([3000,None,3301])['producer_flag'])
        self.assertTrue(round2.temperature_arithmetic([3000,3400,3450,3450])['plateau'])
        self.assertFalse(round2.temperature_arithmetic([3000,3400,3451])['plateau'])

    def test_rho_uses_battery_and_excludes_impossible_negative_energies_from_spread(self):
        def member(rail,meter,battery):
            return {'model':'m','phases':{'request':{'rail_delta_J':rail,'meter':{'delta_J':meter},'battery':{'delta_J':battery}}}}
        members={'a':member(2,3,1),'b':member(3,4,0),'bad':member(-1,-2,0)}
        result=round2.rho_arithmetic(members,'m')
        self.assertEqual(result['median'],.5)
        self.assertEqual(result['q75'],.625)
        self.assertEqual(result['spread'],.4)

    def test_single_source_label_does_not_mask_disagreement(self):
        fields=next(csv.reader(io.StringIO(round2.frozen_bytes().decode()),delimiter='\t'))
        ledger=round2.Ledger(fields,{'DISC':(None,None,'a'*64)})
        ledger.add('synthetic',1.0,2.0,'deliberate counterexample',kind='single-source')
        self.assertEqual(ledger.rows[0]['match'],'MISMATCH')
        self.assertEqual(ledger.rows[0]['difference'],'1.0')
        self.assertEqual(ledger.rows[0]['paper1'],'print-labelled')


class Round4CoverageAndReplayTests(unittest.TestCase):
    @staticmethod
    def module(name):
        return Round3RepositoryGateTests.load_script(name)

    def test_round4_refuses_wrong_hash_before_loading_file(self):
        r4 = self.module('hand_check_rl55_round4.py')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'fake.json').write_bytes(b'{}')
            reader = r4.ReleasedReader()
            reader.sources = {'RC': (root, 'fake.json', '0'*64)}
            with patch.object(r4.r2.h, 'ROOT_A', root):
                with patch.object(Path, 'read_bytes', side_effect=AssertionError('loaded before prehash matched')):
                    with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                        reader.read('RC')

    def test_round4_append_preserves_existing_partial_append(self):
        r4 = self.module('hand_check_rl55_round4.py')
        rows = [{'value':'a'}, {'value':'b'}]
        self.assertEqual(r4.serialize(b'prefix\na\n', b'prefix\n', rows, ['value']), b'prefix\na\nb\n')
        for current in (b'changed\n', b'prefix\nchanged\n', b'prefix\na\nb\nextra\n'):
            with self.subTest(current=current), self.assertRaisesRegex(ValueError, 'differs'):
                r4.serialize(current, b'prefix\n', rows, ['value'])

    def test_round2_native_replay_accepts_round4_append(self):
        frozen = subprocess.run(['git','show',round2.ROUND2+':docs/analysis/b5/rederivation.tsv'],
                                cwd=SCRIPT.parents[3],check=True,capture_output=True).stdout
        rows = list(csv.DictReader(io.StringIO(frozen.decode()),delimiter='\t'))[801:]
        with patch.object(round2, 'ReleasedReader') as reader:
            reader.return_value.read.return_value = {}
            reader.return_value.finish.return_value = {}
            with patch.object(round2, 'append_rows', return_value=rows):
                with patch('sys.argv',[str(round2.__file__)]), redirect_stdout(io.StringIO()):
                    round2.main()

    def test_round4_repository_mode_never_constructs_custody_reader(self):
        r4 = self.module('hand_check_rl55_round4.py')
        with patch.object(r4, 'ReleasedReader', side_effect=AssertionError('custody opened')):
            with patch('sys.argv',[str(r4.__file__),'--repo-only']), redirect_stdout(io.StringIO()):
                r4.main()

    def test_coverage_has_all_pending_ids_and_exact_machine_bytes(self):
        coverage = self.module('fill_coverage_b5.py')
        fill = self.module('fill_check_b5.py')
        rows = coverage.build(coverage.paper_text(), fill.load_ledger())
        self.assertTrue(set(fill.PENDING) - coverage.NEW_AFTER_SNAPSHOT <= {r['placeholder'] for r in rows})
        self.assertEqual(len({r['placeholder'] for r in rows}),65)
        # Compare digests so a failure cannot dump the study's coverage table.
        self.assertEqual(hashlib.sha256(coverage.encoded(rows)).digest(),
                         hashlib.sha256(SCRIPT.with_name('fill_coverage.tsv').read_bytes()).digest())

    def test_coverage_refuses_an_uninventoried_block5_placeholder(self):
        coverage = self.module('fill_coverage_b5.py')
        fill = self.module('fill_check_b5.py')
        paper = coverage.paper_text()+'\n{{FILL: P1-B5-NEW-GAP | required registered leaf}}'
        with self.assertRaisesRegex(ValueError,'unaccounted Block 5'):
            coverage.build(paper,fill.load_ledger())

    def test_coverage_keeps_contrast_members_in_their_phase(self):
        coverage = self.module('fill_coverage_b5.py')
        fill = self.module('fill_check_b5.py')
        rows = coverage.build(coverage.paper_text(),fill.load_ledger())
        for phase, expected in [('decode',set(range(198,202))),('prefill',set(range(202,209)))]:
            actual = {int(n) for r in rows if r['placeholder']=='P1-B5-RM-ctr-'+phase
                      for n in r['ledger_rows'].split(',') if n and 198<=int(n)<=208}
            self.assertEqual(actual,expected)

    def test_coverage_cites_all_window_battery_codes_and_gamma_temperatures(self):
        fill = self.module('fill_check_b5.py'); ledger = fill.load_ledger()
        for pack in ('alpha','beta','gamma'):
            keys = [r['key/leaf'] for r in ledger.values() if r['key/leaf'].startswith(
                f'DISC.window_lines.{pack}[label=battery_counts].counts.')]
            self.assertEqual(len(keys),6)
        self.assertEqual(sum(r['key/leaf'].startswith('DISC.window_lines.gamma[') and
                             r['key/leaf'].endswith('.rise_k') for r in ledger.values()),10)

    def test_fill_paper_ref_is_explicit_and_uses_local_git_only(self):
        # The first-fill commit prints ledger precision, which the RL-52 rule refuses.
        fill = self.module('fill_check_b5.py')
        with patch.object(fill, 'PAPER') as paper, redirect_stdout(io.StringIO()) as output:
            paper.read_text.side_effect=AssertionError('working-tree paper read with explicit ref')
            self.assertEqual(fill.main(['--paper-ref','e5fd296715f21c7c3792e4f9743b7494b07813ec']),1)
        self.assertIn('Paper input: local Git commit',output.getvalue())

    def test_fill_repo_only_never_reads_paper(self):
        fill = self.module('fill_check_b5.py')
        with patch.object(fill, 'PAPER') as paper, redirect_stdout(io.StringIO()) as output:
            paper.read_text.side_effect=AssertionError('paper read in repo-only mode')
            self.assertEqual(fill.main(['--repo-only']),0)
        self.assertIn('paper not checked',output.getvalue())


class Round5DeltaTests(unittest.TestCase):
    module = staticmethod(Round3RepositoryGateTests.load_script)

    def test_independent_replay_matches_uniform_shared_shift_and_refuses_bad_terms(self):
        r5 = self.module('hand_check_rl55_round5.py')
        members = {}
        units = [f'synthetic-b{i:02}' for i in range(8)]
        for i, unit in enumerate(units, 1):
            for position in ('a1', 'b1', 'b2', 'a2'):
                members[f'synthetic-prefill-{unit[-3:]}-{position}'] = {
                    'E_j': {'prefill': 2.0*i if position == 'b1' else 0.0},
                    'r_j': {'prefill': 0.0}}
        # A uniform shift preserves sample SD, so the comparative prediction
        # increases by exactly the shared width. No repository helper used.
        denominator = 4.5 + 2.365*math.sqrt(6)*math.sqrt(9/8)
        numerator = denominator + 0.25
        rc = {'members': {'ALPHA': members},
              'floors': {r5.CELL+'/comparative': {
                  'kept_units': units, 'local_j': [0.0]*8, 'shared_j': [0.25]*8}},
              'dominance': {'common_mode': {r5.CELL: {
                  'n': 8, 'numerator_j': numerator, 'denominator_j': denominator,
                  'R_cm': numerator/denominator}}}}
        self.assertAlmostEqual(r5.rederive(rc)[0], numerator/denominator)
        rc['dominance']['common_mode'][r5.CELL]['numerator_j'] += 0.01
        with self.assertRaisesRegex(ValueError, 'real mismatch'):
            r5.rederive(rc)

    def test_round5_refuses_bad_hash_before_loading(self):
        r5 = self.module('hand_check_rl55_round5.py')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'synthetic.json'
            path.write_bytes(b'{}')
            with patch.object(r5, 'SOURCE', path), patch.object(r5, 'PIN', '0'*64):
                with patch.object(Path, 'read_bytes', side_effect=AssertionError('loaded before hash matched')):
                    with self.assertRaisesRegex(ValueError, 'hash mismatch before loading'):
                        r5.read_source({})

    def test_round5_authenticates_loaded_bytes_before_parsing(self):
        r5 = self.module('hand_check_rl55_round5.py')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'synthetic.json'
            path.write_bytes(b'{}')
            with patch.object(r5, 'SOURCE', path), patch.object(r5, 'PIN', hashlib.sha256(b'{}').hexdigest()):
                with patch.object(Path, 'read_bytes', return_value=b'changed'):
                    with patch.object(r5.json, 'loads', side_effect=AssertionError('parsed unauthenticated bytes')):
                        with self.assertRaisesRegex(ValueError, 'loaded bytes differ'):
                            r5.read_source({})

    def test_coverage_uses_five_decimal_row_and_names_sealed_bytes(self):
        coverage = self.module('fill_coverage_b5.py')
        fill = self.module('fill_check_b5.py')
        ledger = fill.load_ledger()
        rows = coverage.build(coverage.paper_text(), ledger)
        for fid in ('CP-X02-conclusion', 'P1-B5-DOM-FAILED'):
            precision = [r for r in rows if r['placeholder'] == fid and
                         r['element'].startswith('fullest-precision 1.7B prefill R_cm')]
            self.assertEqual(len(precision), 1)
            self.assertEqual(precision[0]['ledger_rows'], '1846')
            self.assertEqual(ledger[1846]['printed_value'], '1.99975')
        sealed = [r for r in rows if r['reason'] == 'outside Block 5 (BYTES; sealed)']
        self.assertEqual({r['placeholder'] for r in sealed},
                         {'P1-M-ACCEPT', 'P1-LEDGER', 'P1-DEV-LIST', 'P1-RELEASE', 'P1-AVAIL'})
        self.assertFalse(any(r['element'].startswith('BYTES') and
                             r['reason'] != 'outside Block 5 (BYTES; sealed)' for r in rows))

    def test_coverage_map_reads_the_pinned_snapshot_not_the_working_paper(self):
        coverage = self.module('fill_coverage_b5.py')
        with patch.object(Path, 'read_text', side_effect=AssertionError('working-tree paper read')):
            self.assertIn('{{FILL: P1-B5-METER', coverage.paper_text())

    def test_coverage_checks_the_filled_working_paper_against_the_map(self):
        coverage = self.module('fill_coverage_b5.py')
        fill = self.module('fill_check_b5.py')
        rows = coverage.build(coverage.paper_text(), fill.load_ledger())
        current = (SCRIPT.parents[3]/'docs/paper/paper1/paper1.md').read_text()
        self.assertEqual(coverage.check_working_paper(current, rows, fill), (55, 10))
        with self.assertRaisesRegex(ValueError, 'unaccounted Block 5 placeholder'):
            coverage.check_working_paper(current + '\n{{FILL: P1-B5-NEW-GAP | x}}', rows, fill)
        with patch.object(fill, 'FILLED', [f for f in fill.FILLED if f != 'P1-B5-XWIN']):
            with self.assertRaisesRegex(ValueError, 'gone without a fill'):
                coverage.check_working_paper(current, rows, fill)

    def test_default_fill_checks_merged_working_paper(self):
        fill = self.module('fill_check_b5.py')
        with redirect_stdout(io.StringIO()):
            self.assertEqual(fill.main(), 0)

    def test_round4_native_replay_preserves_later_append_and_write_refuses(self):
        r4 = self.module('hand_check_rl55_round4.py')
        frozen = subprocess.run(['git', 'show',
                                 'ffe8137be:docs/analysis/b5/rederivation.tsv'],
                                cwd=SCRIPT.parents[3], check=True, capture_output=True).stdout
        rows = list(csv.DictReader(io.StringIO(frozen.decode()), delimiter='\t'))[1419:]
        with patch.object(r4, 'ReleasedReader') as reader:
            reader.return_value.read.return_value = {}
            reader.return_value.finish.return_value = {}
            with patch.object(r4, 'append_rows', return_value=rows), redirect_stdout(io.StringIO()):
                with patch('sys.argv', [str(r4.__file__)]):
                    r4.main()
                with patch('sys.argv', [str(r4.__file__), '--write']):
                    with self.assertRaisesRegex(ValueError, 'later append exists'):
                        r4.main()

    def test_round5_repository_mode_never_opens_custody(self):
        r5 = self.module('hand_check_rl55_round5.py')
        with patch.object(r5, 'read_source', side_effect=AssertionError('custody opened')):
            with patch('sys.argv', [str(r5.__file__), '--repo-only']), redirect_stdout(io.StringIO()):
                r5.main()


if __name__ == '__main__':
    unittest.main()
