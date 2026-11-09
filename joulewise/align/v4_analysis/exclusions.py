"""R21 A9 frozen prefix table; raw flags remain evidence, classes govern entry."""
FLAG_TO_CLASS = (
    ('thermal.os_level_nonzero', 'X1'), ('thermal.start_gate_timeout', 'X2'),
    ('thermal.gate_timeout:', 'X2'), ('thermal.hold_timeout:', 'X2'),
    ('thermal.powermetrics_non_nominal', 'X3'), ('thermal.state_unobserved', 'X4'),
    ('thermal.collector_thread_dead', 'X4'), ('thermal.collector_failed', 'X4'),
    ('collector_error:', 'X4'), ('runtime.oom', 'X6'), ('runtime.metal', 'X6'),
    ('episode.deadman', 'X7'), ('episode.malformed_tool_call:', 'F1'),
    ('battery.member_span', 'B'), ('battery.accumulator_excursion', 'B'),
    ('member_incomplete', 'incomplete'), ('member.runtime_failure', 'incomplete'),
    ('endpoint_error:', 'incomplete'), ('episode_error:', 'incomplete'),
    ('residual_rows_unavailable', 'energy_unavailable'), ('turn_energy_unavailable', 'energy_unavailable'),
    ('energy_unavailable', 'energy_unavailable'), ('energy.', 'energy_unavailable'),
    ('trace.', 'energy_unavailable'), ('clock.', 'energy_unavailable'),
    ('clock_anchor_unresolved', 'energy_unavailable'), ('duty.uncovered', 'energy_unavailable'),
    ('thermal.custody_invalid', 'custody_invalid'), ('cohort_incomplete', 'cohort_changed'),
    ('final_adjudication_excluded', 'adjudicated'),
    # R23l: bundle config bound to its roster slot; malformed config excludes the member.
    ('config_identity_differs', 'config_identity_differs'), ('config_invalid', 'config_invalid'),
    # R23n: a planned G0 absent from a captured member (start state unobserved).
    ('g0_missing', 'g0_missing'),
)
CLASSES = frozenset((*('X'+str(i) for i in range(1, 9)), 'F1', 'B', 'not_captured',
    'incomplete', 'energy_unavailable', 'custody_invalid', 'seed_identity_differs',
    'cohort_changed', 'adjudicated', 'config_identity_differs', 'config_invalid', 'g0_missing'))


def classes(flags):
    out = set()
    for flag in flags:
        if flag in ('energy.uncertainty_unavailable', 'energy.nonfinite_half_width'):
            continue  # A3: attribution bounds are diagnostic only in v4.
        if flag in CLASSES:
            out.add(flag)
        elif len(flag) >= 2 and flag[:2] in CLASSES and flag[2:3] in (':', '.'):
            out.add(flag[:2])
        else:
            out.update(cls for prefix, cls in FLAG_TO_CLASS if flag.startswith(prefix))
    return sorted(out)
