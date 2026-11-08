"""Synthetic raw adapter, DC desk and incremental CLI witnesses."""
from dataclasses import replace
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis.io import canonical, digest, load
from joulewise.align.v4_analysis.synthetic import series
from joulewise.align.v4_analysis import analyze, engine as e
from tests.align.test_reduce_sol import synthetic_episode, ENDPOINT, OFFSET, EVIDENCE
from tests.align.v4_synthetic import synthetic_frames
from joulewise.align.records import to_json


class RawTests(unittest.TestCase):
    def test_contract_export_with_series_unique_anchor_ids_and_sensor_keys(self):
        p = series(turns=4)
        planned = []
        for name in e.ORDER:
            slots = e.roster(name)
            for slot in slots[:4]:
                slot['run_id'] = name+':'+slot['run_id']
            planned.append(dict(window=name, members=slots))
        slots = planned[0]['members']
        ep = replace(synthetic_episode(), episode_id=slots[0]['run_id'],
                     agent_model=slots[0]['model_id'], seed=slots[0]['expected_episode_seed'],
                     task_pair=slots[0]['task_pair'], condition=slots[0]['condition'],
                     hardware={'thermal': {'policy': {'sensors': {'s_fast': 'F', 's_slow': 'S', 'fan_keys': []}},
                                           'intervals': []}})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def write(name, data):
                (root/name).write_bytes(data)
                return dict(path=name, sha256=digest(data))
            sources = [dict(run_id=s['run_id'], captured=False) for s in slots]
            sources[0].update(captured=True, episode=write('episode.json', to_json(ep).encode()),
                powermetrics=write('raw.plist', b''.join(synthetic_frames(40))),
                first_record_endpoint_s=ENDPOINT, nominal_interval_ns=100_000_000,
                stamps=[dict(epoch_s=ENDPOINT, monotonic_before_s=100., monotonic_after_s=100.,
                             wall_resolution_s=0., monotonic_resolution_s=0.)],
                registered_span_ns=[ep.start_ns, ep.end_ns],
                journal=[dict(kind='sample', monotonic_ns=ep.start_ns,
                              finished=dict(monotonic_after_ns=ep.start_ns), sensors={'F': 50., 'S': 45.})])
            p['synthetic'] = False
            p['windows'] = [dict(window='C1', attempt_id='C1#1', status='final', roster=slots,
                                 raw_source=write('raw.json', canonical(dict(members=sources))))]
            p['series_source'] = write('series.json', canonical(dict(windows=planned)))
            path = root/'input.json'
            path.write_bytes(canonical(p))
            payload = load(path)
            fill, _ = analyze(payload)
            self.assertEqual(payload['windows'][0]['members'][0]['thermal']['id'], slots[0]['run_id'])
            self.assertTrue(payload['windows'][0]['members'][0]['thermal']['sidecar_present'])
            self.assertEqual(fill['windows'][0]['eligibility'][0]['run_id'], slots[0]['run_id'])
            self.assertNotIn('seed_identity_differs', fill['windows'][0]['eligibility'][0]['reasons'])
            # A series-unique alias also binds an immutable Episode that still
            # carries its original window-local capture ID.
            local_sources = copy.deepcopy(sources)
            local_ep = replace(ep, episode_id=e.roster('C1')[0]['run_id'])
            local_sources[0]['episode'] = write('local-episode.json', to_json(local_ep).encode())
            local_input = copy.deepcopy(p)
            local_input['windows'][0]['raw_source'] = write('local-raw.json', canonical(dict(members=local_sources)))
            local_payload = load(path, document=local_input)
            local_fill, _ = analyze(local_payload)
            self.assertEqual(local_fill['windows'][0]['eligibility'], fill['windows'][0]['eligibility'])
            self.assertEqual(canonical(local_payload['windows'][0]['members']), canonical(payload['windows'][0]['members']))
            for target in ('roster', 'raw'):
                with self.subTest(target=target):
                    bad = copy.deepcopy(p)
                    if target == 'roster':
                        bad['windows'][0]['roster'][0]['run_id'] = 'C2:'+e.roster('C1')[0]['run_id']
                    else:
                        bad_sources = copy.deepcopy(sources)
                        bad_sources[0]['run_id'] = 'C2:'+e.roster('C1')[0]['run_id']
                        bad['windows'][0]['raw_source'] = write('bad-raw.json', canonical(dict(members=bad_sources)))
                    # Prefix validation must happen before opening the episode.
                    with patch('joulewise.align.v4_analysis.raw.member',
                               side_effect=AssertionError('must refuse before raw reads')):
                        with self.assertRaisesRegex(ValueError, 'window prefix'):
                            load(path, document=bad)
            bad_sources = copy.deepcopy(sources)
            wrong_ep = replace(ep, episode_id='C2:'+e.roster('C1')[0]['run_id'])
            bad_sources[0]['episode'] = write('wrong-episode.json', to_json(wrong_ep).encode())
            bad = copy.deepcopy(p)
            bad['windows'][0]['raw_source'] = write('wrong-episode-raw.json', canonical(dict(members=bad_sources)))
            with self.assertRaisesRegex(ValueError, 'episode identity'):
                load(path, document=bad)

    def test_raw_capture_presence_is_explicit_not_inferred(self):
        from joulewise.align.v4_analysis.raw import member
        for source in ({}, {'captured': 1}, {'captured': 'true'}):
            with self.assertRaisesRegex(ValueError,'captured'):
                member(Path.cwd(),{},source)

    def test_raw_observations_to_fresh_rows_and_exact_clock(self):
        from joulewise.align.v4_analysis.raw import member
        from joulewise.align.v4_analysis.engine import roster
        ep = replace(synthetic_episode(), episode_id=roster('C1')[5]['run_id'], seed=roster('C1')[5]['expected_episode_seed'])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def write(name, data):
                (root/name).write_bytes(data)
                return dict(path=name, sha256=digest(data))
            raw = b''.join(synthetic_frames(40)).replace(b'<string>Moderate</string>', b'<string>Nominal</string>')
            source = dict(captured=True, episode=write('episode.json', to_json(ep).encode()),
                powermetrics=write('raw.plist', raw), first_record_endpoint_s=ENDPOINT,
                nominal_interval_ns=100_000_000, stamps=[dict(epoch_s=ENDPOINT, monotonic_before_s=100.,
                    monotonic_after_s=100., wall_resolution_s=0., monotonic_resolution_s=0.)],
                clock_evidence=None, os_readings=[[ep.start_ns, 0], [ep.end_ns, 0]],
                registered_os_readings=[[ep.start_ns, 0]], registered_span_ns=[ep.start_ns, ep.end_ns],
                journal=[], turn_rows=[], identity_sha256='a'*64)
            a = member(root, roster('C1')[5], source, cache_dir=root/'cache')
            b = member(root, roster('C1')[5], source, cache_dir=root/'cache')
            self.assertEqual(canonical(a), canonical(b))
            self.assertEqual(a['summary']['offset_ns'], OFFSET)
            self.assertEqual(len(a['summary']['residual_rows']['True']), 2)
            self.assertAlmostEqual(a['thermal']['turn_owned_j'], sum(r['energy_j'] for r in a['summary']['residual_rows']['True']))
            source['powermetrics']['sha256'] = '0'*64
            with self.assertRaisesRegex(ValueError, 'digest'):
                member(root, roster('C1')[5], source, cache_dir=root/'cache')

    def test_dc_owned_integral_removes_hold_and_refits_own_model(self):
        from joulewise.align.v4_analysis import dc
        from joulewise.external import km003c_parse as kp
        ep = synthetic_episode()
        ep = replace(ep, hardware={'thermal': {'intervals': [dict(kind='H', turn=0,
                      start_ns=ep.start_ns+200_000_000, end_ns=ep.start_ns+250_000_000)]}})
        # An intact synthetic Stream with an exact raw/monotonic offset.
        n = 301
        stream = kp.Stream(dict(status='streaming', start_raw_ns=1, start_mono_ns=1),
            dict(end_raw_ns=2, end_mono_ns=2), [], [],
            kp.Samples([i*10 for i in range(n)], [28.]*n, [10/28]*n, [0]*n, 0, 10),
            kp.Fit(ep.start_ns, 1e6, dict(excess_latency_ms_max=0.)),
            [ep.start_ns+i*10_000_000 for i in range(n)], [10.]*n, [], [])
        r = dc.capture([('synthetic', stream)], ep, [ep.start_ns, ep.end_ns])
        self.assertEqual(r['status'], 'available')
        self.assertEqual(r['whole_member_j'], 30.)
        self.assertAlmostEqual(r['turn_owned_j'], 29.)  # 0.05s hold + 0.05s gap
        self.assertEqual(r['battery_assist']['status'], 'unavailable')

    def test_window_prefix_never_opens_future_sources(self):
        from scripts.benchmark_v4_engine import write_fixture
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_fixture(root/'fixture', full_ids=False)
            (path.parent/'T1.json').unlink()
            (path.parent/'C3.json').unlink()
            payload = load(path, through_window='C2')
            self.assertEqual([w['window'] for w in payload['windows']], ['C1','C2'])
            self.assertEqual(len(payload['input_census']), 2)
            a, _ = analyze(payload)
            self.assertEqual(a['thresholds']['counts_logged/spam']['threshold'], None)

    def test_w1_window_record_feeds_fixed_pairs_and_acceptance(self):
        p = series(turns=4); p['windows'] = p['windows'][:1]
        sentinels = []
        for ordinal in (5,17):
            m = copy.deepcopy(p['windows'][0]['members'][4])
            m['slot']['ordinal'] = ordinal
            m['slot']['run_id'] = 'W1-'+str(ordinal)
            m['thermal']['id'] = m['slot']['run_id']
            sentinels.append(m)
        p['windows'].insert(0,dict(window='W1',attempt_id='W1#1',status='final',members=sentinels))
        fill,_ = analyze(p)
        self.assertEqual(fill['acceptance']['W1']['qwen3.8-27b']['U3']['pairs'][0]['ordinals'],[5,17])
        self.assertEqual(fill['acceptance']['W1']['qwen3.8-27b']['U3']['status'],'pass')
        self.assertEqual(len(fill['ledger']),1)

    def test_dc_loto_fits_dc_coefficients_with_no_gpu_transfer(self):
        from joulewise.align.v4_analysis import dc, residual
        from joulewise.external import km003c_parse as kp
        from joulewise.align.records import Episode,Turn
        import random
        beta = [1.,.003,.15,.000002,.0000003]
        members=[]
        for i in range(7):
            rng=random.Random(i)
            turns=tuple(Turn(index=k,start_ns=k*10**9,end_ns=(k+1)*10**9,first_token_ns=k*10**9+200_000_000,
                context_tokens=rng.randint(100,2000),prefill_tokens=rng.randint(10,100),decode_tokens=rng.randint(100,500)) for k in range(3))
            ep=Episode(episode_id=str(i),task_pair='p',condition='benign',agent_model='D',endpoint='mock',seed=i,
                       clock_domain='host',start_ns=0,end_ns=3*10**9,turns=turns)
            energy=[sum(a*b for a,b in zip(residual.design_row(vars(t)),beta)) for t in turns]
            times=[j*10_000_000 for j in range(301)]
            watts=[energy[min(j//100,2)] for j in range(301)]
            stream=kp.Stream(dict(status='streaming',start_raw_ns=0,start_mono_ns=0),dict(end_raw_ns=1,end_mono_ns=1),[],[],
                kp.Samples([j*10 for j in range(301)],[28.]*301,[w/28 for w in watts],[0]*301,0,10),
                kp.Fit(0.,1e6,dict(excess_latency_ms_max=0.)),times,watts,[],[])
            members.append(dict(captured=True,eligible=True,slot=dict(run_id=str(i),model_id='D',task_pair='p',condition='benign',held_out=True),
                dc_evidence=dict(streams=[('synthetic',stream)],episode=ep,member_span_ns=[0,3*10**9])))
        gpu_fits = [dict(window='C1',pair='p',convention='counts_logged',scores=[dict(
            run_id=str(i), condition='benign', training_trajectories=[str(j) for j in range(7) if j != i])
            for i in range(7)])]
        out=dc.analyze_windows([dict(window='C1',pool_entry=True,members=members)],gpu_fits=gpu_fits)
        for i,r in enumerate(out):
            self.assertEqual(r['residual_status'],'available')
            self.assertEqual(len(r['training_run_ids']),6)
            self.assertNotIn(str(i),r['training_run_ids'])
            for a,b in zip(r['model']['coef'],beta):
                self.assertAlmostEqual(a,b,places=7)


if __name__ == '__main__':
    unittest.main()
