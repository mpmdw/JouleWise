"""Explicit raw-export adapter using Sol columns and fresh production attribution.

The lead owns the exporter. No directory discovery or path from a config is
followed; every byte source is relative and digest-bound in its manifest.
"""
from dataclasses import asdict, replace
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from joulewise.clock import ClockStamp
from joulewise.align.records import Episode, from_json
from joulewise.align.apple import reduce_sol as sol, thermal_desk as td
from joulewise.align.apple.sampler import stamp_mapping
from . import residual, dc
from .io import input_path, local_path, read_blob, strict_json


def member(root, slot, source, *, cache_dir=None):
    if type(source.get('captured')) is not bool:
        raise ValueError('captured must be explicit bool in raw export')
    if source.get('captured') is not True:
        return dict(slot=slot, captured=False, thermal=dict(id=slot['run_id'], model=slot['model_id'],
            gated=slot['model_id']=='qwen3.8-27b', status='incomplete', flags=[], intervals=[],
            turn_observation=[], releases=[], coverage=[]), summary=None,
            source_flags=source.get('exclusion_codes', []))
    root = input_path(root)
    episode = from_json(Episode, read_blob(root, source['episode']).decode())
    if episode.episode_id != slot['run_id']:
        _, sep, local = slot['run_id'].partition(':')
        if sep and slot.get('series_role') == 'anchor' and episode.episode_id == local:
            # The export's window-bound alias need not rewrite the captured
            # Episode JSON. Bind its derived rows to the series-unique ID.
            episode = replace(episode, episode_id=slot['run_id'])
        else:
            raise ValueError('raw episode identity differs from roster')
    ref = source['powermetrics']
    samples = sol.reduce_file(local_path(root, ref['path']), cache_dir=cache_dir)
    if samples.raw_sha256 != ref['sha256']:
        raise ValueError('raw source digest differs')
    evidence = source.get('clock_evidence')
    mapping, flags = stamp_mapping([ClockStamp(**s) for s in source['stamps']],
                                  episode_domain=episode.clock_domain, evidence=evidence)
    if 'offset_ns' in source and source['offset_ns'] != mapping.offset_ns:
        raise ValueError('exported production clock offset differs')
    episode = replace(episode, clock_mappings=(mapping,), flags=tuple(dict.fromkeys([*episode.flags, *flags])))
    endpoint, period = source['first_record_endpoint_s'], source['nominal_interval_ns']
    try:
        table = sol.turn_energy_table(samples, episode, first_record_endpoint_s=endpoint,
                                     nominal_interval_ns=period, evidence=evidence)['gpu_power']
    except ValueError:
        # Match the thermal desk's exclusion route: diagnostic attribution
        # without corrupt custody intervals, never a scored substitute.
        thermal_hw = episode.hardware.get('thermal', {})
        fallback = replace(episode, hardware={**episode.hardware,
            'thermal': {**thermal_hw, 'intervals': []}})
        table = sol.turn_energy_table(samples, fallback, first_record_endpoint_s=endpoint,
                                     nominal_interval_ns=period, evidence=evidence)['gpu_power']
    traces, trace_flags = samples.power_traces(endpoint, nominal_interval_ns=period, evidence=evidence)
    episode = replace(episode, power_traces=traces, flags=tuple(dict.fromkeys([*episode.flags, *trace_flags])))
    energies = {r['turn']: (r['owned_j'], r['owned_half_width_j']) for r in table['turns']}
    rows = {str(logged): [asdict(r) for r in residual.er.turn_rows_from_episode(episode, energies,
                    hidden_token_counts_logged=logged, uncertainty_kind='additive_bound')] for logged in (True,False)}
    journal = source.get('journal', [])
    if isinstance(journal, dict):
        journal = strict_json(read_blob(root, journal))
    span = source['registered_span_ns']
    registered = [r for r in source.get('registered_os_readings', []) if span[0] <= r[0] <= span[1]]
    thermal = td.member_record(episode, journal, os_readings=source.get('os_readings', []),
        pm_samples=samples.native_pm_samples(endpoint, mapping.offset_ns), pm_period_s=period/1e9,
        turn_rows=source.get('turn_rows', []), registered_os_readings=registered,
        gate_journal=source.get('gate_journal'))
    thermal.update(status=source.get('status', 'completed'), ordinal=slot['ordinal'], captured=True,
        identity_sha256=source.get('identity_sha256'),
        turn_counts=[[r[k] for k in ('context_tokens','prefill_tokens','decode_tokens')] for r in rows['True']],
        battery=source.get('battery'), cohort_identity=source.get('cohort_identity'),
        configuration=source.get('configuration'), identical_work_group=source.get('identical_work_group'))
    thermal.update({k: source[k] for k in ('template','arm','stage','pilot7_token_identical','window') if k in source})
    attributed = table['attribution']['total']
    result = dict(slot=slot, captured=True, thermal=thermal,
        summary=dict(residual_rows=rows, seed=episode.seed,
            energy={'powermetrics:gpu_power': dict(joules=attributed['joules'], half_width_j=attributed['half_width_j'])},
            flags=[], offset_ns=mapping.offset_ns, raw_sha256=samples.raw_sha256,
            cache_statistics=source.get('cache_statistics', {})), source_flags=source.get('exclusion_codes', []))
    if slot['condition'] == 'benign' and source.get('dc_streams'):
        from joulewise.external import km003c_parse as kp
        streams = [(r['path'], kp.parse_bytes(read_blob(root,r))) for r in source['dc_streams']]
        # Capture runs in analyze(), never in a persisted decision/energy cache.
        result['dc_evidence'] = dict(streams=streams, episode=episode, member_span_ns=source['member_span_ns'])
    return result


def _job(args):
    root, slot, source, cache = args
    return member(root, slot, source, cache_dir=cache)


def window(root, document, slots, *, window_id, cache_dir=None, workers=1):
    from .engine import allocation_run_id, slot_run_id
    # Validate before opening any member's raw references. A prefix is a
    # window binding, not merely a way to make repeated anchor IDs unique.
    for record in [*slots, *document['members']]:
        allocation_run_id(record['run_id'], window_id)
    for slot in slots:
        slot_run_id(slot, window_id, strict=True)
    sources = {m['run_id']: m for m in document['members']}
    if len(sources) != len(document['members']) or set(sources) != {s['run_id'] for s in slots}:
        raise ValueError('raw export roster differs')
    jobs = [(root, slot, sources[slot['run_id']], cache_dir) for slot in slots]
    workers = sol.worker_count(workers)
    if workers == 1:
        return [_job(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        return list(pool.map(_job, jobs, chunksize=1))
