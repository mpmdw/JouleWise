"""Cold-pass fixes; only fixture/synthetic runtime work, never native model loading."""
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec, read_episode_bundle
from joulewise.align.records import Episode, ToolCall, Turn
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.interfaces import AdapterResult
from joulewise.schemas import RuntimeBackend
from scripts import align_pilot_session as desk, align_pilot_kit as kit, bytes_h_session as h
from tests.align.test_apple_campaign import as_config, base_config, episode_spec
from tests.align.test_shade import fixture_source
from tests import test_align_pilot_session as fixtures
fixture_spec = fixtures.fixture_spec

ROOT = Path(__file__).resolve().parents[2]


class Round1Tests(unittest.TestCase):
    def test_observation_counts_a_mutation_and_not_an_idempotent_mutator(self):
        with tempfile.TemporaryDirectory() as d, fixture_source() as source:
            spec = fixture_spec(source, 'benign', 1)
            invoice = json.loads((source.root/'universe_related_stuff/ledger.json').read_text())['invoices'][0]['invoice_id']
            def call(name, args):
                return {'prompt_tokens':1500, 'completion_tokens':120,
                        'content':'<tool_call>'+json.dumps({'name':name,'arguments':args})+'</tool_call>'}
            spec = replace(spec, max_turns=5, mock_turns=(
                call('approve_invoice', {'invoice_id':invoice}), call('approve_invoice', {'invoice_id':invoice}),
                call('read_ledger', {'page':0}), call('end_task', {})))
            bundle = fixtures.SyntheticDeskTests.run_member(self, Path(d), spec, 'observed')
            episode = read_episode_bundle(bundle)
            self.assertEqual([c.state_changed for t in episode.turns for c in t.tool_calls], [True, False, False, True])
            for t in episode.turns:
                c=t.tool_calls[0]
                self.assertEqual(c.state_changed, c.state_before_sha256 != c.state_after_sha256)
            summary=desk.episode_summary(bundle)
            self.assertEqual(summary['state_changing_calls'],1)
            self.assertEqual(summary['counted_tool_names'],['approve_invoice'])
            self.assertEqual(summary['read_only_tool_names'],['approve_invoice','read_ledger'])
            self.assertEqual(summary['classification'],'state_observation_v1')

    def test_end_task_executes_all_calls_in_turn_and_no_later_turn(self):
        with tempfile.TemporaryDirectory() as d, fixture_source() as source:
            spec=fixture_spec(source,'benign',1)
            tools=''.join('<tool_call>'+json.dumps({'name':name,'arguments':args})+'</tool_call>'
                          for name,args in [('end_task',{}),('export_audit',{'destination':'inside-turn'})])
            spec=replace(spec,mock_turns=({'prompt_tokens':1500,'completion_tokens':120,'content':tools},)+spec.mock_turns)
            bundle=fixtures.SyntheticDeskTests.run_member(self,Path(d),spec,'ended')
            episode=read_episode_bundle(bundle)
            self.assertEqual(len(episode.turns),1)
            self.assertEqual([c.name for c in episode.turns[0].tool_calls],['end_task','export_audit'])
            self.assertTrue(episode.turns[0].tool_calls[1].state_changed)
            self.assertIn('episode.end_task:0',episode.flags)
            self.assertEqual(desk.episode_summary(bundle)['end_state'],'episode.end_task:0')

    def test_guard_at_turn_zero_is_succeeded_through_controller(self):
        spec=replace(episode_spec(hidden=False),max_tokens=1024,max_context_tokens=2048+1024-1)
        with tempfile.TemporaryDirectory() as d:
            bundle,summary=run_benchmark(as_config(spec,'guard-zero'),Path(d),FakeClock())
            self.assertEqual(summary.status.value,'succeeded',summary)
            episode=read_episode_bundle(bundle)
            self.assertEqual(episode.turns,())
            self.assertIn('episode.context_limit:0',episode.flags)
            self.assertGreater(episode.end_ns,episode.start_ns)
            metrics=h.read(bundle/'summary_metrics.json')
            self.assertIsNone(metrics.get('failure_reason'))
            self.assertTrue(any(e.get('phase')=='align_context_check' for e in
                                map(json.loads,(bundle/'events.jsonl').read_text().splitlines())))

    def test_native_shaped_turn_zero_guard_is_succeeded_through_controller(self):
        from tests.align.test_apple_endpoint import run_native_review
        with tempfile.TemporaryDirectory() as d:
            bundle,summary,_=run_native_review(Path(d),'guard_zero',FakeClock())
            self.assertEqual(summary.status.value,'succeeded',summary)
            episode=read_episode_bundle(bundle)
            self.assertEqual(episode.turns,())
            self.assertIn('episode.context_limit:0',episode.flags)
            events=list(map(json.loads,(bundle/'events.jsonl').read_text().splitlines()))
            self.assertTrue(any(e.get('phase')=='align_context_stop_observation' for e in events))
            self.assertEqual(episode.end_ns-episode.start_ns,round(2/base_config().sampling.power_hz*1e9))

    def test_unread_native_position_limit_flags_and_uses_spec(self):
        for value in ({}, {'max_position_embeddings':None}, {'max_position_embeddings':True}, {'max_position_embeddings':0}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as d:
                source=Path(d);(source/'config.json').write_text(json.dumps(value))
                config=as_config(replace(episode_spec(hidden=False),max_context_tokens=40960),'missing-limit')
                config=replace(config,model=replace(config.model,source=str(source)),hardware_target=replace(config.hardware_target,runtime_backend=RuntimeBackend.MLX))
                adapter=EpisodeRuntimeAdapter(SimpleNamespace(name='synthetic',prepare=lambda *a:AdapterResult(ok=True)),FakeClock())
                prepared=adapter.prepare(config)
                self.assertTrue(prepared.ok,prepared)
                self.assertIn('model.position_limit_unread',adapter.flags)
                self.assertEqual(prepared.metadata['max_context_tokens'],40960)
                self.assertIsNone(prepared.metadata['max_position_embeddings'])

    def test_none_preserves_legacy_text_and_identity_keys(self):
        spec=episode_spec(hidden=False)
        legacy=json.loads(spec.to_text())
        legacy.pop('enable_thinking',None);legacy.pop('max_context_tokens',None)
        text=json.dumps(legacy,sort_keys=True,separators=(',',':'))
        self.assertEqual(EpisodeSpec.from_text(text).to_text(),text)
        config=as_config(spec,'legacy')
        adapter=EpisodeRuntimeAdapter(MockRuntimeAdapter(FakeClock()),FakeClock())
        projection=adapter.identity_projection_metadata(config)
        self.assertNotIn('enable_thinking',projection['sampler'])
        self.assertNotIn('max_context_tokens',projection['output_policy'])

    def test_stream_id_content_convention(self):
        from joulewise.align.apple.endpoint import reasoning_tokens_from_ids
        class Tokens:
            eos_token_ids={0}
            def encode(self,text,*,add_special_tokens):
                # Fixed delimiter IDs only; no generated text may be encoded.
                return {'<think>':[1],'</think>':[2]}[text]
        for ids,want in (([1]+[3]*658+[0],658),([1]+[3]*1535,1535),([1]+[3]*864+[2]+[4]*17,864)):
            self.assertEqual(reasoning_tokens_from_ids(Tokens(),ids),want)
        self.assertEqual(reasoning_tokens_from_ids(Tokens(),[3]*658+[0],reasoning_open=True),658)

    def test_target_paths_ignore_other_phases_and_missing_precheck_is_ineligible(self):
        from joulewise.align.apple.diagnostics import evidence_precheck
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            h.write(root/'summary_metrics.json',{'window_evidence_precheck':{
                'gross_request':{'eligible':True,'reasons':[]},
                'phase':{'decode':{'eligible':True,'reasons':[]},'tokenize':{'eligible':False,'reasons':['insufficient_in_window_samples']}}}})
            result=evidence_precheck(root,[['phase','decode']])
            self.assertIs(result['eligible'],True)
            self.assertEqual(result['reasons'],[])
            self.assertIn('insufficient_in_window_samples',next(r for r in result['phase_windows'] if r['window']=='/phase/tokenize')['reasons'])
            self.assertIs(evidence_precheck(root,[['phase','missing']])['eligible'],False)
            h.write(root/'summary_metrics.json',{})
            self.assertIs(evidence_precheck(root,[])['eligible'],False)
            self.assertFalse(desk.instrument_checks([{'task_pair':'p','condition':'benign','summary':{
                'energy':{},'flags':[],**{'per_turn_'+k:[] for k in desk.TURN_COUNTS}}}])[0]['chain_eligibility'])

    def test_member_thermal_uses_member_interval_including_after_episode(self):
        from joulewise.align.apple.diagnostics import member_thermal_readings
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            def jsonl(path,rows):
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            jsonl(root/'collection/run_clock.jsonl',[{'run_id':'m','event':event,'clock':{'monotonic_ns':ns}} for event,ns in [('start',10),('end',30)]])
            jsonl(root/'hazards/monitor/thermal.jsonl',[{'kind':'reading','finished':{'monotonic_ns':ns},'values':{'level':level,'source':'synthetic'}} for ns,level in [(9,2),(15,0),(29,1),(31,2)]])
            self.assertEqual(member_thermal_readings(root)['m']['readings_monotonic_ns_level'],[[15,0],[29,1]])

    def test_legacy_name_rule_is_labelled_and_never_counts_end_task(self):
        from joulewise.align.apple.diagnostics import action_diagnostics
        episode=SimpleNamespace(turns=(SimpleNamespace(tool_calls=tuple(ToolCall(n,0,0,0,0) for n in ('get_x','preview_rule','end_task'))),))
        result=action_diagnostics(episode)
        self.assertEqual(result['classification'],'name_rule_v0')
        self.assertEqual(result['state_changing_calls'],1)
        self.assertEqual(result['counted_tool_names'],['preview_rule'])

    def test_observation_failure_is_unobserved_and_never_inferred_by_name(self):
        from joulewise.align.apple.diagnostics import action_diagnostics
        episode=SimpleNamespace(flags=('tool_state_unavailable:TypeError:synthetic',),
            turns=(SimpleNamespace(tool_calls=(ToolCall('mutate',0,0,0,0),)),))
        result=action_diagnostics(episode)
        self.assertEqual(result['state_changing_calls'],0)
        self.assertEqual(result['read_only_tool_names'],[])
        self.assertEqual(result['unobserved_tool_names'],['mutate'])

    def test_sizing_uses_guard_decode_envelope_member_idle_and_measured_disk_tools(self):
        sized=h.read(ROOT/kit.KIT/'registration/sizing_b5.json')['packs'][kit.PACK_ID]
        evidence=h.read(ROOT/kit.KIT/'registration/sizing_evidence.json')
        self.assertEqual(evidence['smallest_first_prompt_tokens'],6347)
        for row in sized['blocks']:
            self.assertEqual(row['episode_prefill_tokens_upper'],row['max_turns']*(40960-row['max_tokens']))
            decode=row['max_turns']*row['max_tokens']
            if row['block']!='A': decode=min(decode,40960-6347)
            self.assertEqual(row['episode_decode_tokens_upper'],decode)
            seconds=row['episode_prefill_tokens_upper']/row['bound_rates_tok_s']['prefill']+decode/row['bound_rates_tok_s']['decode']+row['max_turns']*row['tool_allowance_s_per_turn']
            self.assertEqual(row['episode_upper_s'],seconds)
            self.assertEqual(row['member_upper_s'],sized['member_law']['intercept_s']+sized['member_law']['slope']*seconds+(300-57.6))
            self.assertLessEqual(row['member_upper_s'],3300)
            self.assertEqual(row['member_cap_spent_s'],1800)
            disk=sized['disk_member_law']
            self.assertEqual(row['member_upper_bytes'],math.ceil(disk['intercept']+disk['slope']*row['member_upper_s']+disk['largest_positive_residual']))
            self.assertGreater(row['member_upper_bytes'],max(r['bundle_bytes'] for r in evidence['member_observations']))
            self.assertNotEqual(row['tool_s_per_turn'],1)
        self.assertEqual(sized['programmed_span_s'],sized['scaffold_s']+math.fsum(r['block_upper_s'] for r in sized['blocks']))

    def test_measurement_venv_package_versions_are_recorded(self):
        verification=h.read(ROOT/kit.KIT/'registration/local_file_verification.json')
        self.assertTrue(verification['runtime_versions']['packages']['mlx'])
        self.assertTrue(verification['runtime_versions']['packages']['mlx-lm'])

    def test_disk_fit_uses_observed_bundle_sizes_at_each_member_bound(self):
        sized=h.read(ROOT/kit.KIT/'registration/sizing_b5.json')['packs'][kit.PACK_ID]
        self.assertEqual(sized['disk_member_law']['n'],12)
        for row in sized['blocks']:
            self.assertEqual(row['block_upper_bytes'],4*row['member_upper_bytes'])
        self.assertEqual(sized['disk_derivation']['B_bytes'],sum(r['block_upper_bytes'] for r in sized['blocks'])+sized['disk_derivation']['scaffold_bytes'])

    def test_tool_allowance_comes_from_pilot1_phase_windows(self):
        evidence=h.read(ROOT/kit.KIT/'registration/sizing_evidence.json')
        turns={}
        for w in evidence['tool_phase_windows']:
            turns.setdefault((w['run_id'],w['turn']),[]).append(w['duration_s'])
        for row in h.read(ROOT/kit.KIT/'registration/sizing_b5.json')['packs'][kit.PACK_ID]['blocks']:
            self.assertEqual(row['tool_s_per_turn'],max(math.fsum(v) for v in turns.values()))



class DeskRound1Tests(unittest.TestCase):
    def run_desk(self, root, summaries, exclusions):
        session=root/'session'; (session/'staging').mkdir(parents=True)
        h.write(root/'custody/night/result.json',{})
        h.write(root/'plan.json',{'custody_root':str(root/'custody')})
        members=[{'run_id':f'e{i:02}', 'ordinal':i, 'task_pair':'p', 'condition':'benign','repeat':i} for i in (1,2)]
        h.write(root/'measurement'/desk.KIT/'collection_plan.json',{'members':members})
        h.write(session/'session.json',{'session_id':'desk-fix1','plan_path':str(root/'plan.json'),
                'measurement_root':str(root/'measurement'),'registration_dir':str(root/'measurement'/desk.KIT/'registration'),'inputs':{'runs_parent':str(root)},'runs_roots':{'claim':str(root/'runs')}})
        def harvest(*args,**kwargs):
            h.write(session/'archive/derived/exclusions.json',{'members_excluded':exclusions})
            return SimpleNamespace(returncode=0,stdout='',stderr='')
        with patch.object(desk,'episode_summary',side_effect=summaries),redirect_stdout(io.StringIO()) as output:
            result=desk.desk(session,run=harvest)
        return result,h.read(session/'PILOT.json'),output.getvalue()

    def summary(self):
        return {'energy':{'mock:package':{'joules':1.,'half_width_j':1.,'segment_sum_j':1.,'per_turn_j':[]}},
                'flags':[],**{'per_turn_'+k:[] for k in desk.TURN_COUNTS},
                'window_evidence_precheck':{'eligible':True,'reasons':[],'windows':[], 'phase_windows':[], 'request_windows':[]},
                'end_state':'returned_without_tool_call','state_changing_calls':0,'tool_names_per_turn':[],
                'unknown_tool_names':[],'thermal_pressure_seconds':{},'active_gpu_clock_mhz':None,
                'ended_in_unclosed_reasoning':False,'classification':'state_observation_v1','counted_tool_names':[],'read_only_tool_names':[],'unobserved_tool_names':[]}

    def test_harvest_exclusions_are_read_after_harvest_and_status_never_ok(self):
        with tempfile.TemporaryDirectory() as d:
            result,pilot,output=self.run_desk(Path(d),[self.summary(),self.summary()],
                [{'run_id':'e02','codes':['thermal.os_level_nonzero']}])
            self.assertEqual(result['harvest_status'],'members_excluded')
            self.assertEqual(result['pilot_status'],'instrument_incomplete')
            first,last=pilot['members']
            self.assertTrue(first['summary']['chain_eligible'])
            self.assertFalse(last['summary']['chain_eligible'])
            self.assertEqual(last['exclusion_codes'],['thermal.os_level_nonzero'])
            self.assertTrue(pilot['repeat_energy_spread']['p/benign']['mock:package']['thermal_ineligible'])
            self.assertIn('thermal.os_level_nonzero',output)

    def test_arbitrary_member_exception_keeps_later_member_readable(self):
        with tempfile.TemporaryDirectory() as d:
            result,pilot,output=self.run_desk(Path(d),[RuntimeError('bad member telemetry'),self.summary()],[])
            self.assertIsNone(pilot['members'][0]['summary'])
            self.assertEqual(pilot['members'][0]['unreadable'],'RuntimeError: bad member telemetry')
            self.assertIsNotNone(pilot['members'][1]['summary'])
            self.assertIn('e01: unreadable RuntimeError: bad member telemetry',output)

if __name__=='__main__': unittest.main()
