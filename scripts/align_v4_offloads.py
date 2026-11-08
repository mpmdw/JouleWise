#!/usr/bin/env python3
"""By-day W1 offload verification; never run during a measurement window."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.align_v4_session import daytime_offload_receipt
from joulewise.align.r0_runner import validate_config


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    config = json.loads(args.config.read_bytes())
    config.pop('offloads_owed', None)
    config.pop('daytime_offload_receipt', None)
    freshness = config.pop('daytime_offload_freshness', None)
    record = daytime_offload_receipt(validate_config(config), freshness_policy=freshness)
    with args.output.open('x') as f:
        f.write(json.dumps(record, indent=2, sort_keys=True, allow_nan=False)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
