#!/usr/bin/env python3
"""Guarded v4 session skeleton; full thermal/desk integration remains WP15/21."""
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


def install(session_root, **kwargs):
    state = pilot.h.read(Path(session_root) / 'session.json')
    kit.require_ready(kit.read_inputs(state['measurement_root']))
    return pilot.install(session_root, **kwargs)


def main(argv=None):
    return pilot.main(argv, kit=kit.KIT, pack_id=kit.PACK_ID, desk_schema=kit.DESK_SCHEMA,
                      session_prefix='align-v4-', prepare_fn=prepare, install_fn=install)


if __name__ == '__main__':
    raise SystemExit(main())
