"""Commitment comparison on dispatch doubles and the joined real programs."""
from copy import deepcopy
import hashlib
import unittest
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import AnalysisRefusal


class JoinedReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The primary joined run (shared with JoinedRunTests and the probes)
        # is the first dry run; one more dry run and the release follow in the
        # same scratch repository, so the three share one anchor commit.
        from tests.b5_analysis.joined_s10 import cached_primary
        cls.fixture, cls.harness, cls.first = cached_primary()
        cls.addClassCleanup(cls.harness.remove_repository)
        cls.second = cls.harness.execute('second')
        cls.release = cls.harness.execute(mode='release', custody=cls.first.custody)

    def test_J6_two_custody_roots_have_identical_output_digests(self):
        from tests.b5_analysis.joined_s10 import output_digests
        self.assertEqual((self.first.code, self.second.code), (0, 0),
                         self.first.stderr + self.second.stderr)
        self.assertNotEqual(self.first.custody, self.second.custody)
        self.assertEqual(self.first.record, self.second.record)
        self.assertEqual(output_digests(self.first), output_digests(self.second))
        d.require_release_equality(self.first.record, self.second.record)

    def test_J6_release_after_dry_run_passes(self):
        self.assertEqual(self.release.code, 0, self.release.stderr)
        self.assertIs(self.release.record['completed_without_tooling_refusal'], True)
        self.assertEqual(self.release.record['mode'], 'release')
        self.assertEqual(self.first.record['steps'], self.release.record['steps'])
        d.require_release_equality(self.first.record, self.release.record)


def record():
    return {'input_census':[{'window':'alpha','path':'derived/exclusions.json','sha256':'a'*64,'check':'harvest_outputs'}],
            'steps':[{'step':'11','outputs':[
                {'name':name,'sha256':hashlib.sha256((name+' 12.3457331').encode()).hexdigest()}
                for name in ('disclosures/record.json','disclosures/unreleased.txt','disclosures/released.txt')]}]}


class ReleaseComparisonPrimitiveTests(unittest.TestCase):
    def test_R2_equal_commitments(self):
        before=record()
        self.assertIsNone(d.release_difference(before,deepcopy(before)))
        d.require_release_equality(before,deepcopy(before))

    def test_R3_all_outputs_including_both_rendered_texts_are_compared(self):
        before=record()
        for index in range(3):
            after=deepcopy(before);after['steps'][0]['outputs'][index]['sha256']='b'*64
            with self.subTest(index=index),self.assertRaisesRegex(AnalysisRefusal,'^release_digest_differs_from_dry_run$') as refusal:
                d.require_release_equality(before,after)
            self.assertEqual(refusal.exception.difference,{'step':'11','output':before['steps'][0]['outputs'][index]['name']})

    def test_R4_census_difference_precedes_output_difference(self):
        before=record();after=deepcopy(before)
        after['input_census'][0]['sha256']='b'*64
        after['steps'][0]['outputs'][0]['sha256']='b'*64
        with self.assertRaisesRegex(AnalysisRefusal,'^release_digest_differs_from_dry_run$') as refusal:
            d.require_release_equality(before,after)
        self.assertEqual(refusal.exception.difference,{'path':'derived/exclusions.json'})

    def test_R4_census_only_difference_is_not_exempt(self):
        before=record();after=deepcopy(before)
        after['input_census'][0]['sha256']='b'*64
        with self.assertRaisesRegex(AnalysisRefusal,'^release_digest_differs_from_dry_run$') as refusal:
            d.require_release_equality(before,after)
        self.assertEqual(refusal.exception.difference,{'path':'derived/exclusions.json'})

    def test_census_and_output_additions_or_removals(self):
        before=record()
        for field in ('input_census','outputs'):
            after=deepcopy(before)
            if field=='input_census':after[field]=[]
            else:after['steps'][0][field]=[]
            with self.subTest(field=field):
                self.assertIsNotNone(d.release_difference(before,after))
                self.assertIsNotNone(d.release_difference(after,before))

from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
from tests.b5_analysis import test_dry_run as fixture
DriverDouble=fixture.DriverDouble


class ReleaseAcceptanceTests(unittest.TestCase):
    setUpClass=classmethod(fixture.DriverAcceptanceTests.setUpClass.__func__)
    setUp=fixture.DriverAcceptanceTests.setUp
    execute=fixture.DriverAcceptanceTests.execute

    def test_R1_two_custody_roots_have_identical_records_and_every_digest(self):
        first=self.execute();second=self.execute()
        self.assertEqual((first.code,second.code),(0,0))
        self.assertEqual(first.record,second.record)
        self.assertEqual(first.path.read_bytes(),second.path.read_bytes())
        self.assertNotEqual(first.path,second.path)

    def test_R2_unchanged_release_is_complete_exit0(self):
        before=self.execute();after=self.execute(mode='release',custody=before.custody)
        self.assertEqual((before.code,after.code),(0,0),after.stderr)
        self.assertTrue(after.record['completed_without_tooling_refusal'])
        self.assertEqual(after.record['mode'],'release')
        self.assertEqual(before.record['input_census'],after.record['input_census'])
        self.assertEqual(before.record['steps'],after.record['steps'])

    def test_R3_changed_output_byte_including_each_rendered_view_refuses(self):
        for name in ('closeout.ratio-table.json','view.unreleased.txt','view.released.txt','results-fill-input.json'):
            with self.subTest(output=name):
                DriverDouble.release_change=None;before=self.execute()
                DriverDouble.release_change=name;after=self.execute(mode='release',custody=before.custody)
                self.assertEqual(after.code,2,after.stderr)
                self.assertFalse(after.record['completed_without_tooling_refusal'])
                self.assertEqual(after.record['steps'][-1]['refusal'],'release_digest_differs_from_dry_run')
                self.assertEqual(after.record['release_difference']['step'],'6' if name.startswith('closeout') else '11')
                self.assertTrue(after.record['release_difference']['output'].endswith(name),after.record['release_difference'])

    def test_R4_changed_restricted_input_names_first_census_path(self):
        before=self.execute();path=self.root/'alpha/archive/derived/exclusions.json';original=path.read_bytes()
        try:
            path.write_bytes(original+b' ')
            after=self.execute(mode='release',custody=before.custody)
        finally:path.write_bytes(original)
        self.assertEqual(after.code,2,after.stderr)
        self.assertEqual(after.record['release_difference'],{'path':'derived/exclusions.json'})
        self.assertEqual(after.record['steps'][0]['refusal'],'release_digest_differs_from_dry_run')

    def test_R5_no_completed_dry_run_refuses_before_any_step(self):
        with self.assertRaisesRegex(AnalysisRefusal,'^dry_run_record_missing_or_incomplete$'):
            d.custody_preflight('release',self.root/'no-dry-record',self.repo)
        DriverDouble.refusal=('5','window_index_required');before=self.execute()
        with self.assertRaisesRegex(AnalysisRefusal,'^dry_run_record_missing_or_incomplete$'):
            d.custody_preflight('release',before.custody,self.repo)
        self.assertFalse((before.custody/'release').exists())
