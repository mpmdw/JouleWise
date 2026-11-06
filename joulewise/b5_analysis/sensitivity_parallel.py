"""One non-issuing pack derivation; contrasts and pass ordering stay in the caller."""
from copy import deepcopy


def derive_pack(pack, window, kept, context, spec, primary_projection, primary_report,
                equal_bound, strict_validator, consumers):
    from .sensitivity import (_projection_cells, _projection_parents, _reported_values,
                              _at_primary_bound, _same, _get)
    from .windows import AnalysisRefusal
    from .context import _SourcesReplay
    from joulewise.whole_window import MAX_BRACKET_CONSUMPTION_SEMANTICS_ID

    primary, refused, order = _projection_cells(primary_projection, spec)
    parents = _projection_parents(primary_projection)
    projection = consumers.project(deepcopy(spec), kept, context=context,
        runs_root=window.claim_runs_root, strict_validator=strict_validator, **parents)
    computed, sensitivity_refused, _ = _projection_cells(projection, spec)
    rows = []
    for cid in order:
        if cid in refused:
            if cid not in sensitivity_refused or _get(refused[cid], 'code') != _get(sensitivity_refused[cid], 'code'):
                raise AnalysisRefusal('sensitivity_changed_bound_independent_value')
            rows.append({'pack': pack, 'cell_id': cid, 'status': 'refused', 'code': _get(refused[cid], 'code')})
            continue
        if cid not in computed:
            raise AnalysisRefusal('sensitivity_changed_bound_independent_value')
        before, after = _reported_values(primary[cid]), _reported_values(computed[cid])
        _at_primary_bound(equal_bound, before, after)
        if not _same([before['mean_j'], before['h_j']], [after['mean_j'], after['h_j']]):
            raise AnalysisRefusal('sensitivity_changed_bound_independent_value')
        rows.append({'pack': pack, 'cell_id': cid, 'status': 'computed',
            'primary': before, 'sensitivity': after, 'mean_and_half_width_equal_primary': True,
            'equals_primary': _same(before, after),
            'not_below_primary': after['attribution_floor_j'] >= before['attribution_floor_j']})
    report = consumers.extract(window.claim_runs_root, deepcopy(spec), kept_units=kept, archive_context=context,
        evaluation_basis_sha256=parents['evaluation_basis_sha256'],
        consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        manifest_id=_get(primary_report, 'manifest_id'), mode='read_replay', hash_bundles=True,
        strict_validator=strict_validator)
    archive = context.sources_replay.archive if isinstance(context.sources_replay, _SourcesReplay) else None
    return rows, report, archive.census() if archive is not None else None
