"""RL-148 desk step 0: truncated-member bundles on the WP22 synthetic world (tests only).

SYNTHETIC ONLY. Drives ``scripts/align_v4_w1_synthetic.py``'s collection and desk
unchanged, adding four injections on D members (matched by run-id suffix):

* ``e14``: the stock WP22 deadman (slow decode; deadline crosses turn 0's decode).
* ``e11``: the deadline is moved to 50 ms ahead during turn 1's decode (after
  token 300), so completed turn 0 + a cut turn 1.
* ``e18``: the deadline falls in the middle of turn 1's native prefill and a
  DeadmanExpired is delivered inside it, as the production SIGALRM would be
  (FakeClock guards do not arm the POSIX timer, so this emulates it).
* ``e17``: 80 W of synthetic external heat during the turn-1 G1 wait, so the
  G1 times out at its cap (``thermal.gate_timeout:1``).

``e05`` runs clean (the synthetic registration needs it). Structure only is
reported: file names, row counts, flags, token counts. No real bundle is read.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.align.apple import budget
from scripts import align_v4_w1_synthetic as dry
from tests.align import w1_synthetic as syn

NS = 1_000_000_000
MEMBERS = '5,11,14,17,18'
ENDINGS = {'e05': 'clean', 'e11': 'deadman_mid_decode_turn1', 'e14': 'deadman_mid_decode_turn0',
           'e17': 'g1_timeout_turn1', 'e18': 'deadman_mid_prefill_turn1'}


def _tag(run_id):
    return next((k for k in ENDINGS if (run_id or '').endswith(k)), None)


def install(world, stack):
    """Wrap the native stream and the thermal factory; record the live deadman."""
    live = {}
    original_init = budget.EpisodeDeadman.__init__

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        live['deadman'] = self
    stack.enter_context(patch.object(budget.EpisodeDeadman, '__init__', init))

    original_native = syn.native_module

    def native_module(w, fake_random):
        native = original_native(w, fake_random)
        inner = native.stream_generate

        def stream_generate(model, tokenizer, prompt, *, max_tokens, **kwargs):
            tag, turn = _tag(w.run_id), w.turn
            if tag == 'e14':
                w.injections.slow_decode[w.run_id] = 0.6   # the stock WP22 deadman injection
            if max_tokens > 8 and tag == 'e18' and turn == 1 and live.get('deadman') is not None:
                profile = syn.PROFILES[w.family]
                prompt = list(prompt)
                prefill_s = len(prompt) * profile.prefill_s
                deadman = live['deadman']
                deadman.deadline_ns = round(w.clock.now() * NS + prefill_s / 2 * NS)
                w.busy_w = profile.watts
                try:
                    step = prefill_s / 20
                    for _ in range(20):
                        w.clock.sleep(step)
                        if deadman.expired():
                            # The production alarm interrupts the native call here.
                            raise budget.DeadmanExpired()
                finally:
                    w.busy_w = None
                return
            for index, response in enumerate(inner(model, tokenizer, prompt, max_tokens=max_tokens, **kwargs)):
                if (max_tokens > 8 and tag == 'e11' and w.turn == 2 and index == 300
                        and live.get('deadman') is not None):
                    live['deadman'].deadline_ns = round(w.clock.now() * NS + 0.05 * NS)
                yield response
        native.stream_generate = stream_generate
        return native
    stack.enter_context(patch.object(syn, 'native_module', native_module))

    original_factory = dry.thermal_factory

    def thermal_factory(w):
        factory = original_factory(w)

        def make(policy, clock, context, status_reader=None):
            session = factory(policy, clock, context, status_reader)
            wait = session.wait

            def hot_wait(kind, **kwargs):
                if kind == 'G1' and kwargs.get('turn') == 1 and _tag(w.run_id) == 'e17':
                    w.extra_heat_w = 80.0
                    try:
                        return wait(kind, **kwargs)
                    finally:
                        w.extra_heat_w = 0.0
                return wait(kind, **kwargs)
            session.wait = hot_wait
            return session
        return make
    stack.enter_context(patch.object(dry, 'thermal_factory', thermal_factory))


def run(out):
    """Collect the five members and run the unchanged desk CLI on them."""
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    from contextlib import ExitStack
    original_patches = syn.patches
    with ExitStack() as stack:
        def patches(world):
            # The native wrapper must be in place before the original builds its module.
            pre = ExitStack()
            install(world, pre)
            inner, fake_random = original_patches(world)
            inner.push(pre)
            return inner, fake_random
        stack.enter_context(patch.object(syn, 'patches', patches))
        args = SimpleNamespace(variant='kit', inject='none', leak=0.004, members=MEMBERS)
        results, world = dry.collect(args, out)
    (out / 'world_power.json').write_text(json.dumps(world.power))
    desk = dry.run_desk(out, world)
    return results, desk


def _jsonl_count(path):
    return sum(1 for line in path.read_text().splitlines() if line.strip()) if path.is_file() else None


def structure(out, results, desk):
    """Per member: files present, row counts, flags, per-turn token counts (synthetic)."""
    from joulewise.align.apple import rl145_prints
    from joulewise.align.apple.thermal_desk import normalize_journal, read_bundle_record
    from joulewise.align.apple.workload import read_episode_bundle
    pilot = desk.get('pilot') or {}
    by_id = {m['id']: m for m in pilot.get('members', [])}
    report = []
    for member in results['members']:
        bundle = Path(member['bundle'])
        files = sorted(str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file())
        events = [json.loads(x) for x in (bundle / 'events.jsonl').read_text().splitlines() if x.strip()]
        runtime_path = bundle / 'outputs/align_runtime_events.jsonl'
        runtime = ([json.loads(x) for x in runtime_path.read_text().splitlines() if x.strip()]
                   if runtime_path.is_file() else [])
        thermal_rows = [json.loads(x) for x in (bundle / 'outputs/align_thermal.jsonl').read_text().splitlines()
                        if x.strip()]
        row = {'ending': ENDINGS[_tag(member['run_id'])], 'run_id': member['run_id'],
               'status': member['status'], 'files': files,
               'events_jsonl': {'rows': len(events), 'token_events': sum(e.get('event_type') == 'token' for e in events)},
               'runtime_events_jsonl': None if not runtime_path.is_file() else {
                   'rows': len(runtime), 'token_events': sum(e.get('event_type') == 'token' for e in runtime)},
               'gate_journal': {'rows': len(thermal_rows),
                                'samples_with_os_level': sum(1 for r in normalize_journal(thermal_rows)
                                                             if (r.get('status') or {}).get('os_level') is not None)},
               'power_trace_rows': max(0, (_jsonl_count(bundle / 'power_trace.csv') or 1) - 1)}
        try:
            ep = read_episode_bundle(bundle)
            stop = ep.hardware.get('token_budget', {}).get('stop_reason')
            row['read_episode_bundle'] = 'accepted'
            row['episode'] = {
                'turns': [{'index': t.index, 'prefill_tokens': t.prefill_tokens, 'context_tokens': t.context_tokens,
                           'decode_tokens': t.decode_tokens, 'first_token_ns_set': t.first_token_ns is not None,
                           'tool_calls': len(t.tool_calls)} for t in ep.turns],
                'stop_reason': stop, 'power_traces': len(ep.power_traces), 'clock_mappings': len(ep.clock_mappings),
                'deadman_or_timeout_flags': [f for f in ep.flags if f.startswith(('episode.deadman', 'thermal.gate_timeout',
                                                                                  'episode.decode_budget'))],
                'gate_intervals': [(i['kind'], i.get('turn'), i['outcome']) for i in
                                   (ep.hardware.get('thermal') or {}).get('intervals', [])]}
            row['turn_tokens_by_events_jsonl'] = [len(rl145_prints.token_stamps_from_events(events, t) or [])
                                                  for t in ep.turns]
            row['turn_tokens_by_runtime_events'] = [len(rl145_prints.token_stamps_from_events(runtime, t) or [])
                                                    for t in ep.turns]
            record = read_bundle_record(bundle)
            row['read_bundle_record'] = {'accepted': True, 'calibration_exclusions': record['calibration_exclusions'],
                                         'turn_observation_rows': len(record['turn_observation'])}
        except Exception as exc:  # noqa: BLE001 - a refusal is the finding
            row['read_episode_bundle'] = f'refused: {type(exc).__name__}: {exc}'
        desk_member = next((m for k, m in by_id.items() if k.lower() == member['run_id'].lower()), None)
        row['desk_cli'] = None if desk_member is None else {
            'present': True, 'excluded': desk_member.get('excluded'),
            'calibration_exclusions': desk_member.get('calibration_exclusions')}
        report.append(row)
    return {'desk_status': desk['status'], 'desk_error': desk.get('error'), 'members': report}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args(argv)
    results, desk = run(args.output)
    summary = structure(args.output.resolve(), results, desk)
    (args.output / 'step0_structure.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
