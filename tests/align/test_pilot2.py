"""Pilot-2 regressions: synthetic native streams only, never load MLX."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.campaign import _counterbalanced
from joulewise.align.apple.endpoint import MlxEndpoint, parse_completion
from joulewise.align.apple.workload import EpisodeRuntimeAdapter, EpisodeSpec, WORKLOAD_KIND, read_episode_bundle
from joulewise.align.apple import pilot
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.schemas import RuntimeBackend
from joulewise.align.records import Episode, from_json
from tests.align.test_apple_campaign import base_config, episode_spec, as_config
from tests.align.test_apple_endpoint import Tokenizer
from joulewise.interfaces import AdapterResult


class Pilot2Tests(unittest.TestCase):
    def test_thinking_switch_validation_and_sampler_identity(self):
        spec = episode_spec(hidden=False)
        configs=[]
        hashes=[]
        from joulewise.identity_pins import scientific_config_identity_sha256
        for enabled in (None, True, False):
            value=json.loads(spec.to_text()); value['enable_thinking']=enabled
            parsed=EpisodeSpec.from_text(json.dumps(value))
            self.assertIs(parsed.enable_thinking, enabled)
            config=as_config(parsed,"thinking-identity")
            adapter=EpisodeRuntimeAdapter(MockRuntimeAdapter(FakeClock()),FakeClock())
            configs.append(json.dumps(adapter.identity_projection_metadata(config),sort_keys=True))
            hashes.append(scientific_config_identity_sha256(config.to_dict()))
        self.assertEqual(len(set(configs)),3)
        self.assertEqual(len(set(hashes)),3)
        for bad in (0,1,'false',[],{}):
            value=json.loads(spec.to_text());value['enable_thinking']=bad
            with self.assertRaises(ValueError):EpisodeSpec.from_text(json.dumps(value))

    def test_context_validation(self):
        for bad in (True,0,-1,1.5,'40960'):
            value=json.loads(episode_spec(hidden=False).to_text());value['max_context_tokens']=bad
            with self.assertRaises(ValueError):EpisodeSpec.from_text(json.dumps(value))

    def test_context_guard_zero_turn_and_exact_budget_boundary(self):
        # Scripted prompt 2048 + budget 1024 = 3072, integer boundary;
        # a cap one token below that must generate zero tokens.
        spec=replace(episode_spec(hidden=False), max_tokens=1024, max_context_tokens=3071)
        with tempfile.TemporaryDirectory() as d:
            c=base_config();c=replace(c,run_id='context-stop',workload_profile=replace(
                c.workload_profile,name=WORKLOAD_KIND,prompt_text=spec.to_text(),prompt_tokens=None,output_tokens=None))
            clock=FakeClock()
            adapter=EpisodeRuntimeAdapter(MockRuntimeAdapter(clock),clock)
            self.assertTrue(adapter.prepare(c).ok)
            result=adapter.run_workload(c)
            e=from_json(Episode,result.output_artifacts['align_episode.json'])
            self.assertEqual(e.turns,())
            self.assertIn('episode.context_limit:0',e.flags)
            spec=replace(spec,max_context_tokens=3072)
            c=replace(c,run_id='context-equal',workload_profile=replace(c.workload_profile,prompt_text=spec.to_text()))
            bundle,summary=run_benchmark(c,Path(d),FakeClock())
            e=read_episode_bundle(bundle)
            self.assertEqual(len(e.turns),1)
            self.assertIn('episode.context_limit:1',e.flags)
            self.assertEqual(e.hardware['context_limits']['max_context_tokens'],3072)

    def test_context_guard_uses_native_limit_and_forwards_thinking(self):
        # Native synthetic tokenizer emits 2048 IDs; cap 2347 < 2048+300.
        # A larger spec cap cannot lift the native cap.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); clock=FakeClock()
            (root/'config.json').write_text(json.dumps({'max_position_embeddings':2347}))
            seen=[]
            class RecordingTokenizer(Tokenizer):
                def apply_chat_template(self, messages, **kwargs):
                    seen.append(kwargs.get('enable_thinking'))
                    return 'rendered'
            runtime=SimpleNamespace(prepare=lambda *a:AdapterResult(ok=True), _tokenizer=RecordingTokenizer(),name='synthetic')
            spec=replace(episode_spec(hidden=False),max_tokens=300,enable_thinking=False,max_context_tokens=40960)
            config=base_config()
            config=replace(config,model=replace(config.model,source=str(root)),
                hardware_target=replace(config.hardware_target,runtime_backend=RuntimeBackend.MLX),
                workload_profile=replace(config.workload_profile,prompt_text=spec.to_text()))
            adapter=EpisodeRuntimeAdapter(runtime,clock)
            prepared=adapter.prepare(config)
            self.assertTrue(prepared.ok,prepared)
            self.assertEqual(prepared.metadata['max_context_tokens'],2347)
            with patch.object(MlxEndpoint,'chat',side_effect=AssertionError('guard generated')):
                result=adapter.run_workload(config)
            self.assertIn('episode.context_limit:0',result.metadata['align_episode']['flags'])
            self.assertEqual(result.workload_provenance['sampler']['enable_thinking'],False)
            self.assertEqual(seen,[False])

    def test_pilot1_roster_each_pair_sees_both_orders(self):
        specs=sorted(pilot.pilot_specs(),key=lambda s:(s.seed,pilot.PILOT_V0_PAIRS.index(s.task_kwargs['task_pair'])))
        ordered,flags=_counterbalanced(specs)
        self.assertEqual(flags,())
        orders={p:[] for p in pilot.PILOT_V0_PAIRS}
        for a,b in zip(ordered[::2],ordered[1::2]):
            self.assertEqual(a.task_kwargs,b.task_kwargs)
            orders[a.task_kwargs['task_pair']].append((a.condition,b.condition))
        for pairs in orders.values():
            self.assertEqual(set(pairs),{('benign','sabotage'),('sabotage','benign')})

    def test_unclosed_reasoning_at_stop_is_hidden_and_cannot_execute_quoted_tools(self):
        visible,reasoning,calls,flags=parse_completion('<think>plan <tool_call>{"name":"erase","arguments":{}}</tool_call>')
        self.assertEqual(visible,'')
        self.assertIn('plan',reasoning)
        self.assertEqual(calls,())
        self.assertIn('unclosed_reasoning_span',flags)

    def test_task_diagnostics_and_episode_unclosed_flag_are_preserved(self):
        spec=replace(episode_spec(hidden=False),mock_turns=({'prompt_tokens':2048,'completion_tokens':660,
            'reasoning_tokens':660,'finish_reason':'stop','content':'<think>unfinished plan'},))
        with tempfile.TemporaryDirectory() as d:
            c=base_config();c=replace(c,run_id='unclosed',workload_profile=replace(c.workload_profile,
                name=WORKLOAD_KIND,prompt_text=spec.to_text(),prompt_tokens=None,output_tokens=None))
            bundle,summary=run_benchmark(c,Path(d),FakeClock())
            e=read_episode_bundle(bundle)
            self.assertIn('ended_in_unclosed_reasoning',e.flags)
            self.assertEqual(e.turns[0].hidden_tokens,660)
            self.assertIn('task_diagnostics',e.hardware)


class DiagnosticTests(unittest.TestCase):
    def test_interval_clipping_and_active_gpu_weighting(self):
        import datetime as dt
        import math
        import plistlib
        from joulewise.align.apple.diagnostics import telemetry_diagnostics
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'raw').mkdir()
            documents=[];rich=[]
            # Two 100 ms production-cadence supports. The episode overlaps
            # 75 ms of each; active GPU residencies are 50 ms and 100 ms.
            for i,(pressure,mhz,active_ns) in enumerate((('Nominal',1000,50_000_000),('Heavy',500,100_000_000))):
                documents.append(plistlib.dumps({'elapsed_ns':100_000_000,'timestamp':dt.datetime(2026,11,2),
                    'thermal_pressure':pressure, 'processor':{'cpu_power':1000,'gpu_power':1000,'ane_power':0,
                    'cpu_energy':100,'gpu_energy':100,'ane_energy':0}}))
                rich.append({'timestamp_s':10.1+i*.1,'elapsed_ns':100_000_000,
                             'gpu':{'dvfm_states':[{'freq':mhz,'used_ns':active_ns}]}})
            (root/'raw/powermetrics.plist').write_bytes(b'\0'.join(documents))
            (root/'rich_telemetry.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rich))
            episode=SimpleNamespace(hardware={'paired_clock_stamps_ns':[{'epoch_ns':10_025_000_000},{'epoch_ns':10_175_000_000}]})
            result=telemetry_diagnostics(root,episode)
            # 1 us exceeds 1e6 x float roundoff at this small epoch and is
            # below 1% of the 100 ms sample interval (1 ms).
            for pressure in ('Nominal','Heavy'):
                self.assertAlmostEqual(result['thermal_pressure_seconds'][pressure],.075,delta=1e-6)
            # The rational expectation is 2000/3 MHz. 1e-6 MHz is above
            # 1e6 x summation noise, below 1% of the 1 MHz printed unit.
            self.assertAlmostEqual(result['active_gpu_clock_mhz'],2000/3,delta=1e-6)

    def test_chain_ineligibility_is_printed_beside_instrument_checks_and_repeat_turn_energies(self):
        from scripts import align_pilot_session as s
        from tests.test_align_pilot_session import SyntheticDeskTests, fixture_spec
        from tests.align.test_shade import fixture_source
        with tempfile.TemporaryDirectory() as d, fixture_source() as source:
            bundle=SyntheticDeskTests.run_member(self,Path(d),fixture_spec(source,'benign',1),'thermal')
            path=bundle/'summary_metrics.json';metrics=json.loads(path.read_text())
            metrics['window_evidence_precheck']={'gross_request':{'eligible':False,'reasons':['thermal_pressure_elevated_in_window']}}
            path.write_text(json.dumps(metrics))
            summary=s.episode_summary(bundle)
            rows=[{'task_pair':'ledger','condition':'benign','summary':summary} for _ in range(2)]
            checks,_,spreads=s.instrument_checks(rows)
            self.assertFalse(checks['chain_eligibility'])
            self.assertEqual(summary['tool_names_per_turn'],[['read_ledger'],['end_task'],[]])
            self.assertEqual(summary['state_changing_calls'],2)  # Both names outside the four read-only families.
            self.assertEqual(summary['end_state'],'end_task')
            from joulewise.align.apple.diagnostics import end_state
            episode=read_episode_bundle(bundle)
            self.assertEqual(end_state(replace(episode,flags=('turn_token_budget_reached:0',))),'end_task')
            self.assertEqual(end_state(replace(episode,flags=('turn_token_budget_reached:2',))),'turn_token_budget_reached:2')
            for spread in spreads['ledger/benign'].values():
                self.assertTrue(spread['thermal_ineligible'])
                self.assertEqual(len(spread['per_turn_j']),2)
                self.assertEqual(len(spread['per_turn_j'][0]),3)

    def test_raw_shade_scores_hint_and_evaluator_errors_survive_the_apple_bundle(self):
        from tests.test_align_pilot_session import SyntheticDeskTests, fixture_spec
        from tests.align.test_shade import fixture_source
        with tempfile.TemporaryDirectory() as d, fixture_source() as source:
            values=iter((50,False))  # Fixture normalizer: raw 50 / maximum 100 = 0.5.
            def evaluated(coroutine):
                coroutine.close()
                return next(values)
            with patch('joulewise.align.shade.task._sync',side_effect=evaluated):
                bundle=SyntheticDeskTests.run_member(self,Path(d),fixture_spec(source,'sabotage',1),'scores')
            episode=read_episode_bundle(bundle)
            diag=episode.hardware['task_diagnostics']
            self.assertTrue(diag['give_hint'])
            self.assertEqual(diag['main_task_score'],episode.main_task_score)
            self.assertIn('main',diag['evaluation_outputs'])
            self.assertEqual(diag['evaluation_outputs']['main'],50)
            self.assertEqual(diag['evaluation_outputs']['main_normalized'],0.5)
            self.assertIn('side',diag['evaluation_outputs'])
            self.assertTrue(any(f.startswith('task.') for f in episode.flags))

            fault=SyntheticDeskTests.run_member(self,Path(d),fixture_spec(source,'sabotage',1),'score-fault')
            diagnostics=read_episode_bundle(fault).hardware['task_diagnostics']
            self.assertEqual(diagnostics['evaluation_outputs']['errors']['main']['type'],'RuntimeError')
            self.assertIn('main_evaluation_error:RuntimeError',diagnostics['flags'])


class NativeAccountingTests(unittest.TestCase):
    def test_native_stop_inside_unclosed_think_has_hidden_tokens(self):
        from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
        from joulewise.align.interfaces import ChatMessage
        clock=FakeClock();runtime=MlxRuntimeAdapter(clock)
        class BoundaryTokenizer(Tokenizer):
            prefilled=False
            def apply_chat_template(self,*args,**kwargs):
                return super().apply_chat_template(*args,**kwargs)+('<think>\n' if self.prefilled else '')
            def encode(self,text,*,add_special_tokens):
                # Retokenizing the bare thought loses delimiters and returns
                # two IDs here; the full unfinished stream still emitted 660.
                return [1,2] if text=='unfinished plan' else super().encode(text,add_special_tokens=add_special_tokens)
        runtime._model=object();runtime._tokenizer=BoundaryTokenizer()
        text='<think>unfinished plan'
        def stream_generate(*a,max_tokens,**kwargs):
            # Synthetic pilot-1 final-turn shape: 660 output IDs, native stop.
            for token in range(660):
                clock.sleep(.010)  # D-019 mock decode step.
                yield SimpleNamespace(token=token+1,text=text if token==0 else '',
                    finish_reason='stop' if token==659 else None)
        runtime._mlx_lm=SimpleNamespace(stream_generate=stream_generate,make_sampler=lambda temp:object())
        config=base_config();config=replace(config,hardware_target=replace(config.hardware_target,runtime_backend=RuntimeBackend.MLX))
        endpoint=MlxEndpoint(runtime,config,clock,episode_domain='synthetic')
        result=endpoint.chat([ChatMessage('user','act')],max_tokens=1536,temperature=0.0,seed=1)
        # The full unfinished response is hidden: use its 660 emitted IDs
        # directly, rather than the bare thought's two retokenized IDs.
        self.assertEqual(result.reasoning_tokens,660)
        self.assertNotIn('reasoning_tokens_retokenized',endpoint.flags)
        self.assertNotIn('reasoning_token_count_unavailable',endpoint.flags)
        self.assertEqual(result.tool_calls,())
        self.assertNotIn('turn_token_budget_reached:0',endpoint.flags)
        runtime._tokenizer.prefilled=True
        text='unfinished plan'
        result=endpoint.chat([ChatMessage('user','act')],max_tokens=1536,temperature=0.0,seed=1)
        self.assertEqual(result.reasoning_tokens,660)
        self.assertEqual(result.reasoning_text,'unfinished plan')
        self.assertEqual(result.content,'')
        self.assertIn('reasoning_open_tag_prefilled_or_missing',result.raw_usage['joulewise']['flags'])

if __name__=='__main__':unittest.main()
