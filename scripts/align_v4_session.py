#!/usr/bin/env python3
"""Guarded v4 session skeleton; full thermal/desk integration remains WP15/21."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_pilot_session as pilot, align_v4_kit as kit


def prepare(measurement_root, session_root, **kwargs):
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('pack_id', kit.PACK_ID)
    kwargs.setdefault('session_prefix', 'align-v4-')
    return pilot.prepare(measurement_root, session_root, **kwargs)


def observe_ac_powermode(runner=None):
    """Read the host's AC-profile powermode (read-only ``pmset -g custom``)."""
    from joulewise.align.apple.powermode import observe_ac_powermode as observe
    return observe(runner)


def bundle_ac_powermode(bundle):
    """The AC powermode a member bundle recorded at episode start, or None."""
    from joulewise.desk_compress import read_bytes
    try:
        episode = json.loads(read_bytes(Path(bundle) / 'outputs/align_episode.json'))
    except (OSError, ValueError):
        return None
    record = (episode.get('hardware') or {}).get('ac_powermode')
    return record.get('value') if isinstance(record, dict) else None


def powermode_desk_check(*, state, members, runs_root, kit_path):
    """Council ruling 7: any member whose bundle-recorded AC powermode differs
    from the frozen series value sets ``instrument_ok`` false."""
    plan = {'members': pilot._member_rows(state, kit=kit_path)}
    observed = {m['run_id']: bundle_ac_powermode(Path(runs_root) / m['run_id']) for m in plan['members']}
    verdict = kit.validate_powermode_members(plan, observed)
    return {'ac_powermode_members': verdict['instrument_ok']}, verdict


def desk(session_root, **kwargs):
    kwargs.setdefault('kit', kit.KIT)
    kwargs.setdefault('desk_schema', kit.DESK_SCHEMA)
    kwargs.setdefault('extra_checks', powermode_desk_check)
    return pilot.desk(session_root, **kwargs)


ARM_RECORD_SCHEMA = 'joulewise.align_v4_arm.v1'


def arm_checks(measurement_root, plan, *, runner=None, volume_runner=None):
    """W1/D arm evidence: ruling 7 AC powermode and ruling 20 volumes.

    Ruling 7: the AC-profile powermode must equal the plan's frozen series
    value; an R1 High Power marker under the measurement root is restored to
    Automatic first (narrow sudo rule) and the mode read again (HIGH-3). The
    observed value and the exact ``pmset -g custom`` text are recorded.
    Ruling 20: no external volume may be mounted; the configuration is pinned
    to status "off" (the SSD amendment is not adopted) and the census is
    recorded either way.
    """
    from joulewise.align.apple import external_volume, powermode
    expected = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    marker = Path(measurement_root) / powermode.R1_HIGH_POWER_MARKER
    power = powermode.admit_ac_powermode(expected, marker=marker, runner=runner)
    reasons = [] if power['admitted'] else ['ac_powermode: ' + str(power['reason'])]
    run = volume_runner or external_volume.run_command
    try:
        taken = external_volume.census(run)
        volumes = external_volume.arm_check(external_volume.validate_config(None), taken, run=run)
        volumes['mounts'] = [{k: row.get(k) for k in ('device', 'mount_point', 'fs_type', 'class')}
                             for row in taken.get('mounts', [])]
    except Exception as exc:  # noqa: BLE001 - an unmeasured census refuses
        volumes = {'verdict': external_volume.REFUSE, 'reasons': [f'census_failed:{type(exc).__name__}:{exc}']}
    if volumes['verdict'] != external_volume.PASS:
        reasons += ['external_volume: ' + reason for reason in volumes['reasons']]
    return {'schema': ARM_RECORD_SCHEMA, 'admitted': not reasons, 'reasons': reasons,
            'ac_powermode': power, 'external_volumes': volumes}


def install(session_root, *, runner=None, volume_runner=None, now=None, **kwargs):
    session = Path(session_root)
    state = pilot.h.read(session / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    kit.require_ready(kit.read_inputs(measurement_root), kit.read_r1_slots(measurement_root))
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    record = arm_checks(measurement_root, plan, runner=runner, volume_runner=volume_runner)
    record['epoch_s'] = (now or time.time)()
    # Every arm records what it saw, admitted or not (ruling 7: "every arm and
    # every bundle records it"), before the shared installer can run.
    attempt = 1
    while (session / f'staging/v4-arm-{attempt:03d}.json').exists():
        attempt += 1
    path = session / f'staging/v4-arm-{attempt:03d}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        handle.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
    state.setdefault('v4_arm_records', []).append({'path': str(path), 'admitted': record['admitted'],
                                                    'ac_powermode': record['ac_powermode'].get('observed'),
                                                    'reasons': record['reasons']})
    pilot.h.write(session / 'session.json', state)
    if not record['admitted']:
        raise ValueError('v4 arm refused: ' + '; '.join(record['reasons']))
    kit.arm_powermode_check(plan, record['ac_powermode']['observed'])
    return pilot.install(session_root, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_extra_checks=powermode_desk_check)


if __name__ == '__main__':
    raise SystemExit(main())
