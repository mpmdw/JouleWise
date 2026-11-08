#!/usr/bin/env python3
"""Compare repeated parsing of the committed synthetic seed; no path discovery."""
import argparse
from contextlib import nullcontext
import cProfile
import json
from pathlib import Path
import pstats
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.adapters import powermetrics as pm


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    seed = ROOT/'tests/fixtures/d117_v2_production/strict_seed_bundle/raw/powermetrics.plist'
    reference = None
    results = {}
    with args.output.open('x', encoding='utf-8') as receipt:
        for name, enabled in (('original', False), ('reuse', True)):
            profile = cProfile.Profile()
            with patch.object(pm.plistlib, 'loads', wraps=pm.plistlib.loads) as loads:
                start = time.monotonic()
                with pm.reuse_parsed_records() if enabled else nullcontext():
                    profile.enable()
                    for _ in range(3):
                        parsed = pm.parse_powermetrics_records(seed.read_bytes())
                        if reference is None:
                            reference = parsed
                        elif parsed != reference:
                            raise AssertionError('parsed records differ')
                    profile.disable()
                elapsed = time.monotonic()-start
            stats = pstats.Stats(profile)
            functions = sorted(stats.stats.items(), key=lambda pair: pair[1][3], reverse=True)[:8]
            results[name] = {'wall_s': elapsed, 'xml_decodes': loads.call_count,
                'top_cumulative': [{'function': key[2], 'calls': val[1], 'cumulative_s': val[3]}
                                   for key, val in functions]}
        record = {'synthetic': True, 'raw_bytes': seed.stat().st_size,
                  'parses_per_case': 3, 'records': len(reference), 'equal': True, 'results': results,
                  'limits': 'one small committed seed, cProfile enabled; not a whole harvest speedup'}
        receipt.write(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    main()
