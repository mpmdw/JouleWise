"""Render the receipt-only close census into self-contained, unissued items.

The emitted reader opens only runner_receipt.json and projects ended.epoch_s.
Filesystem mtimes never establish close identity or select a copy marker.
"""
import re

CENSUS_PY = r'''import json, math, os, sys
def fail(e): raise e
found = []
for root in sys.argv[1:]:
    if not os.path.isdir(root): sys.exit('STOP: missing receipt root: ' + root)
    base = root.rstrip('/').count('/')
    for d, dirs, files in os.walk(root, onerror=fail):
        if d.count('/') - base >= 3: dirs[:] = []
        if 'runner_receipt.json' in files:
            p = os.path.join(d, 'runner_receipt.json')
            if '\n' in p: sys.exit('STOP: bad receipt path')
            try:
                with open(p) as handle: ended = json.load(handle)['ended']['epoch_s']
                if (isinstance(ended, bool) or not isinstance(ended, (int, float))
                        or not math.isfinite(ended) or ended <= 0):
                    raise ValueError('invalid ended.epoch_s')
            except (OSError, ValueError, KeyError, TypeError) as e:
                sys.exit('STOP: unreadable receipt close stamp: ' + p + ': ' + str(e))
            found.append((ended, p))
if not found: sys.exit('STOP: empty receipt census')
latest = max(t for t, p in found)
newest = [p for t, p in found if t == latest]
if len(newest) != 1: sys.exit('STOP: ambiguous newest receipt close epoch')
print(math.ceil(latest)); print(newest[0])
'''


def repair_census(text):
    """Replace exactly one close-census heredoc; preserve all surrounding gates."""
    pattern = r'(  CENSUS="\$\("\$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<\'PY\'\n).*?(\nPY\n)'
    text, count = re.subn(pattern, lambda m: m[1] + CENSUS_PY.rstrip() + m[2], text, flags=re.S)
    assert count == 1, count
    text = text.replace('fractional mtimes', 'fractional recorded close epochs')
    text = text.replace('newest mtime', 'latest recorded close epoch')
    return text
