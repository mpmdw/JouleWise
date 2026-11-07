#!/usr/bin/env python3
"""Guarded v4 session skeleton; full thermal/desk integration remains WP15/21.

prepare refuses until the kit is W1-ready (inputs, D identity, R1-derived
sizing_b5.json, WP18 fixtures) and writes the frozen series AC powermode into
the night plan. install additionally requires the AC powermode to equal the
frozen series value and the R0 host's w1_disk_gate to pass. Under an adopted
High Power (r1_slots ac_powermode 2, lead ruling R5-6) install sets
powermode 2 through the narrow sudo rule after writing the High Power marker,
and restores Automatic if the arm then refuses; run_night admits 2 only for a
plan that declares 2 and restores Automatic when that night closes.
"""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_pilot_session as pilot, align_v4_kit as kit


def series_ac_powermode(measurement_root):
    """The R1-frozen series AC powermode the generated collection plan carries."""
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    value = (plan.get('runtime_requirements') or {}).get('ac_powermode')
    if type(value) is not int or value not in (0, 2):
        raise ValueError(f'v4 collection plan freezes no series AC powermode (got {value!r})')
    return value


def prepare(measurement_root, session_root, **kwargs):
    kit.generate(measurement_root, check=True, source_root=measurement_root)
    # Lead ruling R5-6: the night plan declares the frozen series powermode, so
    # run_night admits a High Power host only for a W1 that adopted it.
    kwargs.setdefault('ac_powermode', series_ac_powermode(measurement_root))
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


def w1_disk_check(config_path, *, gate=None):
    """The W1 arm's storage gate (CHAIR ruling 20; R0 runbook): r0_host.w1_disk_gate.

    It reads the validated R0 desk config (disk_path and the configured W1 offload
    receipts), requires >= 80 decimal GB free after R0 and re-hashes every
    configured offload. Anything but ``pass`` refuses the arm. Read-only.
    """
    if config_path is None:
        raise ValueError('W1 arm requires --w1-disk-config: the validated R0 desk config whose '
                         'disk_path and offloads the W1 disk gate checks')
    from joulewise.align.r0_host import w1_disk_gate
    from joulewise.align.r0_runner import validate_config
    config = validate_config(json.loads(Path(config_path).read_text()))
    receipt = (gate or w1_disk_gate)(config)
    if not isinstance(receipt, dict) or receipt.get('status') != 'pass':
        rows = [{k: row.get(k) for k in ('label', 'pass', 'error')} for row in (receipt or {}).get('offloads', [])]
        raise ValueError('W1 disk gate refused the arm: '
                         + json.dumps({'status': (receipt or {}).get('status'),
                                       'free_bytes_after_present_weights': (receipt or {}).get(
                                           'free_bytes_after_present_weights'),
                                       'required_free_bytes_after_r0': (receipt or {}).get(
                                           'required_free_bytes_after_r0'),
                                       'offloads': rows}, sort_keys=True))
    return receipt


def install(session_root, *, runner=None, volume_runner=None, now=None, w1_disk_config=None,
            disk_gate=None, **kwargs):
    session = Path(session_root)
    state = pilot.h.read(session / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    kit.require_w1_ready(measurement_root)
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    from joulewise.align.apple import powermode
    high = None
    marker = Path(measurement_root) / powermode.R1_HIGH_POWER_MARKER
    custody_root = (state.get('inputs') or {}).get('custody_root')
    if custody_root and (Path(custody_root) / 'night/result.json').is_file():
        # A terminal session has no night left to restore Automatic (Sol
        # critique of R5-6): never change the power mode for it.
        raise ValueError('v4 install refused: the session is terminal (night/result.json exists)')
    already = (state.get('install') or {}).get('exit_code') == 0
    if (plan.get('runtime_requirements') or {}).get('ac_powermode') == 2 and not already:
        # Lead ruling R5-6: W1 under an adopted High Power. The marker comes
        # first (powermode.enter_high_power), so any later crash leaves the
        # restore owed to the next night that expects Automatic.
        high = powermode.enter_high_power(marker, runner=runner)
    try:
        return _arm_and_install(session, state, measurement_root, plan, high, runner=runner,
                                volume_runner=volume_runner, now=now, w1_disk_config=w1_disk_config,
                                disk_gate=disk_gate, **kwargs)
    except BaseException:
        if high is not None:
            # The arm did not hand off: leave the host Automatic (R5-6), on
            # every failure from the mode change on.
            restore = powermode.restore_automatic(marker, runner=runner)
            try:
                pilot.h.write(session / f'staging/v4-arm-restore-{time.time_ns()}.json', restore)
            except Exception:  # noqa: BLE001 - the restore itself is what matters
                pass
        raise


def _arm_and_install(session, state, measurement_root, plan, high, *, runner, volume_runner, now,
                     w1_disk_config, disk_gate, **kwargs):
    record = arm_checks(measurement_root, plan, runner=runner, volume_runner=volume_runner)
    if high is not None:
        record['high_power_enter'] = high
        if not high['ok']:
            record['admitted'] = False
            record['reasons'] = ['high_power_enter: ' + str(high['reason'])] + record['reasons']
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
    receipt = w1_disk_check(w1_disk_config, gate=disk_gate)
    pilot.h.write(session / 'staging/w1_disk_gate.json', receipt)
    return pilot.install(session, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_extra_checks=powermode_desk_check,
                      install_options=(('--w1-disk-config', dict(
                          type=Path, required=True,
                          help='validated R0 desk config (disk_path, W1 offloads) for the W1 disk gate')),))


if __name__ == '__main__':
    raise SystemExit(main())
