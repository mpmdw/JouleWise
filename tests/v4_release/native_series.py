"""A native-layout synthetic v4 series for the exporter end-to-end test. SYNTHETIC ONLY; no real data.

Real producers:
- W1: the WP22 synthetic world through the real controller, kit and thermal desk
  (``scripts/align_v4_w1_synthetic.py``, ``--inject none``);
- C windows: member configs from the real series kit (``scripts/align_v4_series.build_files`` under the WP22
  synthetic inputs), run through the same WP22 world and controller (``align_v4_w1_synthetic.run_member``), and
  the real thermal desk CLI (``scripts/align_v4_thermal_desk.py``) as WP22's ``run_desk`` drives it;
- session trees in the production layout (``scripts/bytes_h_session.py``: custody/ and runs-parent/ inside the
  session), finalized, packed and restored by the real harvest-off CLI (``scripts/align_v4_harvest_off.py``);
- window records in the Scenario shape (``tests/align/test_v4_next_arm_packet.py``), committed to a git repository
  and read by the real ``WindowRecord``.

NOT real producers (disclosed, RELEASE-RUNBOOK-v4.md section 6a):
- ``raw/powermetrics.plist``: the WP22 synthetic GPU rail writes none. This module writes one frame per row of the
  bundle's own ``power_trace.csv`` (the controller's recorded samples) with the pinned recompute's FrameTemplate.
  Real custody without a plist refuses ``member_file_missing``;
- the KM003C stream (the pinned recompute's ``synth.write_meter``), the U3 bar (WP22's synthetic signed bar),
  and the R1 references file.
"""
from __future__ import annotations

import contextlib
import csv
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

NS = 1_000_000_000
RESULT_SCHEMA = 'joulewise.unattended_night_result.v1'
MANIFEST = REPO / 'configs/campaigns/align_v4/series/series_manifest.json'


def default_plan():
    """W1; C1 captured (GO); C2 a zero-capture refusal and its captured retry (GO)."""
    return [dict(attempt='W1#1', slot='W1', captured=True),
            dict(attempt='C1#1', slot='C1', captured=True),
            dict(attempt='C2#1', slot='C2', captured=False),
            dict(attempt='C2#2', slot='C2', captured=True)]


def git(repo, *args):
    return subprocess.run(['git', '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                           '-C', str(repo), *args], check=True, capture_output=True,
                          env={**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}
                          ).stdout.decode().strip()


def dumps(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


# ------------------------------------------------------------------------------------- member producers

def c_window_plan(slot):
    """The real series kit's C window (collection plan + member configs) under the WP22 synthetic inputs."""
    from scripts import align_v4_w1_synthetic as dry, align_v4_kit as kit, align_v4_series as series
    inputs, slots = deepcopy(dry.SYN_INPUTS), deepcopy(dry.SYN_R1_SLOTS)
    manifest = json.loads(MANIFEST.read_bytes())
    with patch.object(kit, 'read_inputs', lambda root=kit.ROOT: deepcopy(inputs)), \
            patch.object(kit, 'read_r1_slots', lambda root=kit.ROOT: deepcopy(slots)):
        files = series.build_files(kit.ROOT, manifest, slot)
    plan = json.loads(files[series.kit_path(slot) / 'collection_plan.json'])
    configs = {m['ordinal']: json.loads(files[Path(m['config_path'])]) for m in plan['members']}
    return plan, configs


def window_kit(slot, models_root):
    """The window's kit as WP22 synthesizes it (model mirror, task factory, rebound window reference). A retry
    runs the same kit, so a zero-capture attempt binds the same bytes as its retry."""
    from scripts import align_v4_w1_synthetic as dry
    plan, raw = c_window_plan(slot)
    configs = {o: dry.synthesize(c, models_root) for o, c in raw.items()}
    dry.rebind(configs)
    return plan, configs


def run_c_members(out, slot, models_root):
    from scripts import align_v4_w1_synthetic as dry
    from tests.align import w1_synthetic as syn
    plan, configs = window_kit(slot, models_root)
    world = syn.World(injections=syn.Injections(), leak_per_c=0.004)
    stack, _ = syn.patches(world)
    results = []
    with stack, contextlib.redirect_stdout(io.StringIO()):
        world.clock.sleep(1)
        for o in sorted(configs):
            results.append(dry.run_member(world, configs[o], out / 'runs', label=str(o)))
    assert all(r['status'] == 'succeeded' for r in results), [r['status'] for r in results]
    (out / 'world_power.json').write_text(json.dumps(world.power))
    return plan, world, configs


def write_plist(bundle, template):
    """NOT a real producer: one NUL-framed powermetrics frame per recorded power_trace.csv row (section 6a)."""
    config = json.loads((bundle / 'config.json').read_bytes())
    period = round(NS / config['sampling']['power_hz'])
    raw = bundle / 'raw' / 'powermetrics.plist'
    raw.parent.mkdir(parents=True, exist_ok=True)
    with (bundle / 'power_trace.csv').open() as rows, raw.open('wb') as fh:
        for row in csv.DictReader(rows):
            fh.write(template.fill(elapsed_ns=period, timestamp_s=int(float(row['timestamp_s'])),
                                   gpu_mw=float(row['power_w']) * 1000.0))
            fh.write(b'\x00')


def desk_items(out, plan, window, *, groups):
    """WP22's roster bridge (align_v4_w1_synthetic.roster_manifest) for any window: no hand tags."""
    items = []
    for m in plan['members']:
        bundle = out / 'runs' / m['run_id']
        ep = json.loads((bundle / 'outputs/align_episode.json').read_text())
        g0 = [i for i in (ep['hardware'].get('thermal') or {}).get('intervals', []) if i['kind'] == 'G0']
        item = {'bundle': f'runs/{m["run_id"]}', 'window': window, 'ordinal': m['ordinal'], 'role': m['role'],
                'stage': m.get('stage_id'), 'registered_span_ns': [g0[0]['start_ns'] if g0 else ep['start_ns'], ep['end_ns']]}
        if m['ordinal'] in groups:
            item['identical_work_group'] = groups[m['ordinal']]
        items.append(item)
    return items


def run_c_desk(out, plan, window, world, w1_inputs):
    """The unmodified thermal desk CLI, driven exactly as WP22's run_desk drives it."""
    from scripts import align_v4_w1_synthetic as dry
    from scripts import align_v4_thermal_desk as cli
    from joulewise.align.apple import thermal_desk
    from tests.align import w1_synthetic as syn
    items = desk_items(out, plan, window, groups={5: 'D-5-22', 22: 'D-5-22'})
    manifest = out / 'desk_manifest.json'
    manifest.write_text(json.dumps({'schema': 'wp22.synthetic_w1_manifest', 'members': items,
                                    'battery_journal': 'synthetic_battery.jsonl',
                                    'delta_slow_c': w1_inputs['R1']['thermal_policy']['delta_slow_c']}))
    (out / 'run_results.json').write_text(json.dumps({'inputs': w1_inputs}))
    registration = dry.synthetic_registration(out, manifest)
    original = thermal_desk.member_record

    def member_record(episode, journal, *, os_readings, pm_samples, pm_period_s, **kwargs):
        if not pm_samples:
            intervals = (episode.hardware.get('thermal') or {}).get('intervals', [])
            start = min([episode.start_ns, *(i['start_ns'] for i in intervals)]) - NS
            pm_samples = syn.pm_samples(world, start, episode.end_ns + NS)
            pm_period_s = 1.0
        return original(episode, journal, os_readings=os_readings, pm_samples=pm_samples,
                        pm_period_s=pm_period_s, **kwargs)
    with patch.object(thermal_desk, 'member_record', member_record):
        cli.main(['--manifest', str(manifest), '--output', str(out / 'desk'), '--registration-dir', str(registration)])
    return json.loads((out / 'desk/PILOT.json').read_text())


def bind_kit(checkout, collection, configs):
    """The kit configs the members ran, at their plan rows' config_path in the measurement checkout, serialized as
    the kit writes them (scripts/align_pilot_kit.raw_json); each plan row's config_sha256 binds those bytes
    (scripts/align_v4_series.py:302). WP22 synthesis changes the model mirror and task factory of every kit
    config, so the committed plan binds the synthesized bytes, as a real kit binds its own."""
    from scripts.align_pilot_kit import raw_json
    for m in collection['members']:
        raw = raw_json(configs[m['ordinal']])
        target = checkout / m['config_path']
        if target.exists():
            assert target.read_bytes() == raw, 'two kit configs at one path: ' + m['config_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        m['config_sha256'] = hashlib.sha256(raw).hexdigest()


# ------------------------------------------------------------------------------------ session + custody

def fake_run(head='a' * 40):
    def run(argv, **_):
        out = {'rev-parse': head + '\n', 'status': ''}.get(argv[3], 'Python 3.13.x\nabc\n')
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr='')
    return run


def harvest_cli(*argv):
    from scripts import align_v4_harvest_off as runner
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        code = runner.main([str(a) for a in argv], run=fake_run())
    assert code == 0, err.getvalue()[-2000:]
    return json.loads(out.getvalue().strip().splitlines()[-1])


def build_session(session, *, slot, role, plan_id, members_src, plan_members, battery, terminal, synth, checkout):
    """A session tree in the production layout; the bundles go to runs-parent/claim/<run_id>."""
    custody, claim = session / 'custody', session / 'runs-parent' / 'claim'
    (custody / 'night').mkdir(parents=True)
    night_plan = dumps({'plan_id': plan_id, 'receipt_class': 'HAZARD_PACK', 'custody_root': str(custody)})
    (custody / 'night_plan.json').write_bytes(night_plan)
    (session / 'session.json').write_text(json.dumps({
        'session_id': plan_id, 'session_root': str(session), 'source_measurement_root': str(checkout),
        'measurement_root': str(checkout), 'registration_dir': str(checkout / 'registration'),
        'plan_path': str(custody / 'night_plan.json'), 'inputs': {'custody_root': str(custody)},
        'runs_roots': {'claim': str(claim)},
        'v4_series': {'window_id': slot, 'role': role,
                      'manifest_sha256': hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}}, sort_keys=True))
    sources = {}
    if terminal is not None:
        sources['result'] = dumps(terminal['result'])
        (custody / 'night/result.json').write_bytes(sources['result'])
        if terminal.get('chain'):
            (custody / 'night/chain.started').write_bytes(dumps({'pgid': 123}))
            (custody / 'night/chain.exited').write_bytes(dumps({'exit_code': terminal['result']['chain_exit_code']}))
            (custody / 'night/courier.sent').write_bytes(b'')
    if members_src is not None:
        claim.mkdir(parents=True)
        starts, ends = [], []
        for m in plan_members:
            shutil.copytree(members_src / m['run_id'], claim / m['run_id'])
            ep = json.loads((claim / m['run_id'] / 'outputs/align_episode.json').read_text())
            starts.append(ep['start_ns'])
            ends.append(ep['end_ns'])
        (custody / 'hazards/monitor').mkdir(parents=True)
        shutil.copyfile(battery, custody / 'hazards/monitor/battery.jsonl')
        stream = custody / 'hazards/meter/stream-000.jsonl'
        synth.write_meter(stream, (min(starts) - 20 * NS, max(ends) + 20 * NS))
        digest = hashlib.sha256(stream.read_bytes()).hexdigest()
        (custody / 'night/hazard_result.json').write_bytes(dumps({'meter': {'streams': [
            {'path': 'hazards/meter/stream-000.jsonl', 'sha256': digest}]}}))
    return night_plan


def finalize_pack_unpack(session, work, *, transfer=True):
    """harvest-off finalize-manifest, then (captured windows) pack and an Air restore at the same path."""
    manifest_path = work / 'M.json'
    printed = harvest_cli('finalize-manifest', '--session-root', session, '--out', manifest_path)
    timings = {}
    if transfer:
        t = time.monotonic()
        harvest_cli('pack', '--session-root', session, '--out', work / 'offload', '--finalized-manifest', manifest_path)
        timings['pack_s'] = time.monotonic() - t
        shutil.move(session, work / 'session.mbp')               # the Air has only the offload
        t = time.monotonic()
        harvest_cli('unpack', '--offload', work / 'offload', '--finalized-manifest', manifest_path,
                    '--finalized-sha256', printed['sha256'])
        timings['unpack_s'] = time.monotonic() - t
        shutil.rmtree(work / 'session.mbp')
        shutil.rmtree(work / 'offload')
    return manifest_path.read_bytes(), printed['sha256'], timings


# --------------------------------------------------------------------------------------------- records

class Records:
    """Committed window records in the Scenario shape (tests/align/test_v4_next_arm_packet.py)."""

    def __init__(self, repo):
        self.repo = Path(repo)
        self.repo.mkdir(parents=True)
        git(self.repo, 'init', '-q')
        self.previous = None

    def write(self, path, raw):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}

    def commit(self, window, role, sources, captures, finalized_raw, raw_evidence):
        d = 'records/' + window.replace('#', '_')
        record = {'schema': 'joulewise.align_v4.window_record.v1', 'window': window, 'role': role,
                  'finalized_at_epoch_s': 101, 'previous_record': self.previous}
        record['sources'] = {k: self.write(f'{d}/evidence/{k}.json', v) for k, v in sources.items()}
        record['finalized_manifest'] = self.write(f'{d}/evidence/finalized_manifest.json', finalized_raw)
        record['captures'] = captures
        record['raw_evidence'] = raw_evidence or [record['finalized_manifest']]
        index = self.write(f'{d}/record.json', dumps(record))
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-qm', 'record ' + window)
        commit = git(self.repo, 'rev-parse', 'HEAD')
        self.previous = {'commit': commit, 'path': f'{d}/record.json', 'sha256': index['sha256']}
        return commit, f'{d}/record.json'


def pilot_source(plan_id, thermal, window, *, captured):
    pilot = {'plan_id': plan_id, 'status': 'instrument_ok' if captured else 'instrument_incomplete',
             'checks': {}, 'extra_checks': {'thermal': thermal, 'km003c': {'members': {}}}}
    if window != 'W1':
        pilot['extra_checks']['series_desk_row'] = {'window_id': window.split('#')[0], 'status': 'provisional',
                                                    'flags': [], 'captured_members': 0,
                                                    'desk_eligible_benign': {'spam': 7, 'bank': 7}}
    return pilot


def zero_capture_thermal(plan, window):
    members = [{'id': m['run_id'], 'model': m['model_id'], 'gated': m['ordinal'] >= 5, 'window': window,
                'excluded': True, 'calibration_exclusions': ['member.runtime_failure'], 'flags': [],
                'tokens': None} for m in plan['members']]
    return {'schema': 'joulewise.align.thermal_desk.v1', 'members': members,
            'model_windows': {f'qwen3.8-27b/{window}': {f'U{k}': {'status': 'inconclusive'} for k in range(1, 6)}}}


# ------------------------------------------------------------------------------------------------ series

def build(root, synth, template, plan=None):
    """Write the series under ``root``; returns (exporter config path, build timings)."""
    from scripts import align_v4_w1_synthetic as dry
    root = Path(root)
    plan = plan or default_plan()
    timings = {}
    checkout = root / 'checkout'
    (checkout / '.venv/bin').mkdir(parents=True)
    (checkout / '.venv/bin/python').write_text('')
    models = root / 'models'
    records = Records(root / 'records')
    t = time.monotonic()
    w1 = root / 'gen' / 'w1'
    with contextlib.redirect_stdout(io.StringIO()):
        assert dry.main([str(w1), '--inject', 'none']) == 0
    w1_results = json.loads((w1 / 'run_results.json').read_text())
    timings['generate_W1_s'] = time.monotonic() - t
    windows, generated = [], {}
    for step in plan:
        attempt, slot, captured = step['attempt'], step['slot'], step['captured']
        record_window = slot if attempt.endswith('#1') else attempt
        role = 'development' if slot == 'W1' else 'calibration' if slot[0] == 'C' else 'test'
        plan_id = 'synthetic-' + attempt.replace('#', '-').lower()
        t = time.monotonic()
        if slot == 'W1':
            # The W1 kit plan as WP22's collect() built it (deterministic from its recorded inputs).
            collection = dry.build_kit(w1_results['inputs'], w1_results['r1_slots'])[0]
            assert collection['members'] == w1_results['plan_members']
            out = w1
            pilot_thermal = json.loads((w1 / 'desk/PILOT.json').read_text())
            # WP22's dry-run desk also carries the two pilot-7 reference runs; the v4 session desk
            # (scripts/align_v4_session.py:310-340) covers only the planned roster, which WindowRecord requires.
            planned = {m['run_id'] for m in collection['members']}
            pilot_thermal['members'] = [m for m in pilot_thermal['members'] if m['id'] in planned]
            pilot_thermal['model_windows'] = {k: v for k, v in pilot_thermal['model_windows'].items()
                                              if k.endswith('/W1')}
        elif captured:
            out = root / 'gen' / attempt.replace('#', '-')
            out.mkdir(parents=True)
            collection, world, ran = run_c_members(out, slot, w1.resolve())   # = dry.main(), which resolves its output
            for m in collection['members']:
                write_plist(out / 'runs' / m['run_id'], template)
        else:
            out, (collection, ran) = None, window_kit(slot, w1.resolve())
        if slot == 'W1':
            for m in collection['members']:
                write_plist(out / 'runs' / m['run_id'], template)
            # WP22's collect() does not expose its synthesized member configs: the kit config is recovered from
            # the bundle's config.json (the writer's normalization is the identity on kit configs).
            ran = {m['ordinal']: json.loads((out / 'runs' / m['run_id'] / 'config.json').read_bytes())
                   for m in collection['members']}
        bind_kit(checkout, collection, ran)
        if slot != 'W1' and captured:
            pilot_thermal = run_c_desk(out, collection, record_window, world, w1_results['inputs'])
        timings[f'generate_{attempt}_s'] = time.monotonic() - t
        session = root / 'sessions' / attempt.replace('#', '-')
        session.mkdir(parents=True)
        result = ({'schema': RESULT_SCHEMA, 'plan_id': plan_id, 'receipt_class': 'HAZARD_PACK', 'verdict': 'GO',
                   'chain_exit_code': 0, 'chain_sha256': 'c' * 64, 'ended_epoch_s': 100} if captured else
                  {'schema': RESULT_SCHEMA, 'plan_id': plan_id, 'receipt_class': 'HAZARD_PACK', 'verdict': 'REFUSED',
                   'chain_exit_code': None, 'chain_sha256': None, 'ended_epoch_s': 100})
        night_plan = build_session(session, slot=slot, role=role, plan_id=plan_id,
                                   members_src=(out / 'runs') if captured else None,
                                   plan_members=collection['members'],
                                   battery=(out / 'synthetic_battery.jsonl') if captured else None,
                                   terminal={'result': result, 'chain': captured}, synth=synth, checkout=checkout)
        work = root / 'work' / attempt.replace('#', '-')
        work.mkdir(parents=True)
        t = time.monotonic()
        finalized_raw, finalized_sha, moved = finalize_pack_unpack(session, work, transfer=captured)
        timings[f'harvest_off_{attempt}_s'] = time.monotonic() - t
        timings.update({f'{k}_{attempt}': v for k, v in moved.items()})
        claim = session / 'runs-parent' / 'claim'
        captures = {}
        for m in collection['members']:
            raw = claim / m['run_id'] / 'raw/powermetrics.plist'
            captures[m['run_id']] = ({'locator': str(raw), 'sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
                                      'bytes': raw.stat().st_size} if captured else None)
        from scripts.align_pilot_kit import raw_json
        # The producer plan verbatim (align_v4_series.build_files / the W1 kit), header included; only each row's
        # config_sha256 binds the WP22-synthesized kit bytes (bind_kit).
        sources = {'plan': night_plan, 'collection_plan': raw_json(collection),
                   'result': dumps(result), 'watchdog_state': dumps({}), 'courier': dumps({'sent': captured})}
        if captured:
            sources.update(chain_started=dumps({'pgid': 123}), chain_exited=dumps({'exit_code': 0}), courier_sent=b'',
                           pilot=dumps(pilot_source(plan_id, pilot_thermal, record_window, captured=True)),
                           desk=dumps({'plan_id': plan_id, 'pilot_status': 'instrument_ok',
                                       'checks': {'v4_B_bar': True}, 'harvest_status': 'ok'}),
                           exclusions=dumps({'members_excluded': []}))
        else:
            sources.update(pilot=dumps(pilot_source(plan_id, zero_capture_thermal(collection, record_window),
                                                    record_window, captured=False)),
                           desk=dumps({'plan_id': plan_id, 'pilot_status': 'instrument_incomplete',
                                       'checks': {'v4_B_bar': True}, 'harvest_status': 'not_run'}),
                           exclusions=dumps({'members_excluded': [
                               {'run_id': m['run_id'], 'codes': ['member.runtime_failure']} for m in collection['members']]}))
        raw_evidence = [c for c in captures.values() if c] or None
        commit, path = records.commit(record_window, role, sources, captures, finalized_raw, raw_evidence)
        windows.append({'attempt_id': attempt, 'record_commit': commit, 'record_path': path,
                        'session_root': str(session) if captured else None})
        generated[attempt] = out
    refs = root / 'inputs' / 'r1_references.json'
    refs.parent.mkdir(parents=True)
    refs.write_bytes(dumps({'schema': 'joulewise.v4_export.r1_references.v1', 'qualified': True,
                            'r1_replay_pair_j': [1500.0, 1510.0], 'delta_slow_c': 1.0,
                            'designed_start_states': [
                                {'designed_slow_c': d, 'g0_release_slow_c': d, 'turn_owned_j': e, 'token_identical': True}
                                for d, e in ((38.0, 1500.0), (40.0, 1501.0), (42.0, 1502.5))]}))

    def ref(path):
        return {'path': str(path), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}
    config = {'schema': 'joulewise.v4_export.config.v1', 'export_root': str(root / 'export'),
              'records_repo': str(root / 'records'), 'kit_root': str(checkout), 'allocation': ref(MANIFEST),
              'u3_bar': ref(w1 / 'registration/u3_bar.json'), 'r1_references': ref(refs),
              'registration_inputs': ref(w1 / 'registration/inputs.json'), 'engine_route': 'raw_source',
              'windows': windows}
    path = root / 'export-config.json'
    path.write_text(json.dumps(config, indent=1, sort_keys=True))
    for out in generated.values():
        if out is not None:
            shutil.rmtree(out / 'runs', ignore_errors=True)     # the restored sessions hold the bundles
    return path, timings


def cached(synth, template, plan_name='default'):
    """A finished native series (read-mostly; refusal tests restore anything they touch), keyed by this module's
    bytes and the producers it drives, under the system temporary folder."""
    import tempfile
    h = hashlib.sha256()
    for path in (Path(__file__), REPO / 'scripts/align_v4_w1_synthetic.py', REPO / 'scripts/align_v4_series.py',
                 REPO / 'scripts/align_v4_harvest_off.py', REPO / 'tests/align/w1_synthetic.py'):
        h.update(path.read_bytes())
    h.update(plan_name.encode())
    root = Path(tempfile.gettempdir()) / f'jw-v4-native-{plan_name}-{h.hexdigest()[:16]}'
    if (root / 'DONE').exists():
        return root / 'export-config.json', json.loads((root / 'timings.json').read_text())
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
    config, timings = build(root, synth, template)
    (root / 'timings.json').write_text(json.dumps(timings))
    (root / 'DONE').write_text('')
    return config, timings
