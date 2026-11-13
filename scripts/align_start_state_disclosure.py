#!/usr/bin/env python3
"""Start-state disclosure (RL-122 item 5 as extended by RL-131 item 3.4; RL-135).

One function, used by the R1 slot-session gate desk
(``scripts/align_r1_slot_gate_desk.py``) and owed to the W1 thermal desk
(``scripts/align_v4_thermal_desk.py``) before the first W1 thermal desk.

Blind-safe: temperatures and their derived slopes only. The caller supplies,
per member with a sidecar, the quantities at its start row (the G0 exit
sample, or the measured-run entry row for a member with a sidecar and no G0):

* ``tf08_start_c``: Tf08 at the start row;
* ``tv0h_slope_c_per_min``: the gate module's ``slow_slope`` on TV0h at the start row;
* ``tv0h_minus_r_fast_c``: TV0h at the start row minus the window reference on TV0h.

and the window's Tf08 reference (the 60 s pre-warmup median in the capture
member; for R1, step-D, derived as ``align_r1_thermal_replay.night_desk``
derives it). The disclosure is the per-member values with
``tf08_excess_c = tf08_start_c - window reference``, the median of each
quantity by ``condition``, and the pairwise differences of those medians,
within one window. It fires nothing.
"""
from statistics import median

QUANTITIES = ('tf08_excess_c', 'tv0h_slope_c_per_min', 'tv0h_minus_r_fast_c')
SCHEMA = 'joulewise.align_start_state_disclosure.v1'


def start_state_disclosure(members, window_tf08_reference_c, *, u2_tv0h_c=None, tf08_release_range_c=None,
                           window=None):
    """members: iterable of dicts with member, condition, tf08_start_c, tv0h_slope_c_per_min,
    tv0h_minus_r_fast_c (any may be None) and optional start_definition / start_ns.

    Returns the disclosure dict; deterministic (no wall clock; members sorted by name)."""
    rows = []
    for m in sorted(members, key=lambda r: r['member']):
        start = m.get('tf08_start_c')
        excess = (start - window_tf08_reference_c
                  if start is not None and window_tf08_reference_c is not None else None)
        rows.append({**m, 'tf08_excess_c': excess})
    by_condition = {}
    for r in rows:
        by_condition.setdefault(r.get('condition') or 'unspecified', []).append(r)
    medians = {}
    for condition, group in sorted(by_condition.items()):
        medians[condition] = {}
        for q in QUANTITIES:
            values = [r[q] for r in group if r.get(q) is not None]
            medians[condition][q] = median(values) if values else None
        medians[condition]['n'] = len(group)
    differences = []
    names = sorted(medians)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            row = {'condition_a': a, 'condition_b': b}
            for q in QUANTITIES:
                va, vb = medians[a][q], medians[b][q]
                row[q + '_a_minus_b'] = va - vb if va is not None and vb is not None else None
            differences.append(row)
    return {'schema': SCHEMA, 'window': window, 'window_tf08_reference_c': window_tf08_reference_c,
            'members': rows, 'medians_by_condition': medians, 'differences': differences,
            'u2_tv0h_c': u2_tv0h_c, 'tf08_release_range_c': tf08_release_range_c,
            'effect': 'disclosure only (RL-122 item 5; RL-131 item 3.4)'}
