#!/usr/bin/env python3
"""Guarded v4 session skeleton; full thermal/desk integration remains WP15/21.

prepare refuses until the kit is W1-ready (inputs, D identity, R1-derived
sizing_b5.json). install additionally requires the AC powermode to equal the
frozen series value and the R0 host's w1_disk_gate to pass.
"""
import json
from pathlib import Path
import sys

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


def install(session_root, *, observe_powermode=observe_ac_powermode, w1_disk_config=None,
            disk_gate=None, **kwargs):
    state = pilot.h.read(Path(session_root) / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    kit.require_w1_ready(measurement_root)
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    kit.arm_powermode_check(plan, observe_powermode())
    receipt = w1_disk_check(w1_disk_config, gate=disk_gate)
    pilot.h.write(Path(session_root) / 'staging/w1_disk_gate.json', receipt)
    return pilot.install(session_root, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_extra_checks=powermode_desk_check,
                      install_options=(('--w1-disk-config', dict(
                          type=Path, required=True,
                          help='validated R0 desk config (disk_path, W1 offloads) for the W1 disk gate')),))


if __name__ == '__main__':
    raise SystemExit(main())
