#!/usr/bin/env python3
"""Guarded v4 session skeleton; full thermal/desk integration remains WP15/21."""
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


def install(session_root, *, observe_powermode=observe_ac_powermode, **kwargs):
    state = pilot.h.read(Path(session_root) / 'session.json')
    measurement_root = state['measurement_root']
    # Council ruling 7: the frozen series powermode comes from the measurement
    # checkout's r1_slots, and arm refuses on a mismatch with the host.
    kit.require_ready(kit.read_inputs(measurement_root), kit.read_r1_slots(measurement_root))
    plan = json.loads((Path(measurement_root) / kit.KIT / 'collection_plan.json').read_bytes())
    kit.arm_powermode_check(plan, observe_powermode())
    return pilot.install(session_root, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install,
                      desk_extra_checks=powermode_desk_check)


if __name__ == '__main__':
    raise SystemExit(main())
