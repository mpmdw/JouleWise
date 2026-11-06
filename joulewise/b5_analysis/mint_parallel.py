"""Independent MINT authentication; only ordered consumption admits its effects."""
from dataclasses import fields, replace

from . import pack_parallel as pp


def authentication_calls(pinset, by_plan_id, *, block5, strict_validator, **kwargs):
    """Keep caller seams and producers with shared root IDs on the serial path."""
    from joulewise.cli import validate_bundle
    from scripts import mint_floor_artifact_generalized as mint

    if not block5 or strict_validator is not validate_bundle:
        return None
    calls, seen = [], set()
    try:
        for producer in pinset.value['producer_plans']:
            ids = {cell[name]['evidence_root_id'] for cell in producer['cells']
                   for name in ('absolute', 'comparative')}
            if seen.intersection(ids):
                return None
            seen.update(ids)
            plan_id = producer['plan']['plan_id']
            entry = mint._producer_by_plan_id(plan_id)
            calls.append(((entry, producer, by_plan_id.get(plan_id)),
                          dict(kwargs, strict_validator=strict_validator)))
    except (KeyError, TypeError, mint.MintError):
        # This is only a scheduling probe. The original body owns malformed
        # inputs and missing/ambiguous registry entries at their serial position.
        return None
    return calls


def _portable_component(component):
    """The isolated pinned core's dataclass modules are intentionally unloaded.

    Transport their exact fields using the same core's importable definitions;
    no authenticated value is recomputed or rounded.
    """
    from scripts import mint_floor_artifact as core

    values = {field.name: getattr(component, field.name) for field in fields(component)}
    values['members'] = tuple(core.AuthenticatedMember(
        **{field.name: getattr(member, field.name) for field in fields(member)})
        for member in component.members)
    return core.AuthenticatedComponent(**values)


def authenticate_producer(entry, producer, manifest_row, **kwargs):
    from scripts import mint_floor_artifact_generalized as mint
    from .archive import ArchiveHandle

    # Spawned workers have no registry. Install exactly the serial author's
    # producer, and restore process-local authority even on a failed computation.
    key = str(entry.window.claim_runs_root.resolve())
    present, previous = key in mint.BLOCK5_PRODUCERS, mint.BLOCK5_PRODUCERS.get(key)
    mint.BLOCK5_PRODUCERS[key] = entry
    try:
        inputs, roots = mint._authenticate_v2_producer(
            producer, manifest_row, block5=True, evidence_roots={}, **kwargs)
        cells = {role: replace(cell, absolute=_portable_component(cell.absolute),
                               comparative=_portable_component(cell.comparative))
                 for role, cell in inputs.cells.items()}
        census = entry.archive.census() if isinstance(entry.archive, ArchiveHandle) else None
        specs = tuple(dict.fromkeys(
            manifest_row['cells'][i][name]['spec']
            for i in range(len(manifest_row['cells'])) for name in ('absolute', 'comparative')))
        return replace(inputs, cells=cells), roots, census, specs, entry.producer_plan_id
    finally:
        if present:
            mint.BLOCK5_PRODUCERS[key] = previous
        else:
            mint.BLOCK5_PRODUCERS.pop(key, None)


def consume_authenticated(outcome, compute):
    from scripts import mint_floor_artifact_generalized as mint

    if outcome is None or not outcome.ok:
        return pp.consume(outcome, compute)
    # Restore governed vocabulary before replaying any first read, as producer
    # preparation does. Only successful, reached producers receive authority.
    (_, _, _, specs, _), _, _ = pp.loads(outcome.value)
    for path in specs:
        mint._allow_governed_extraction_spec(path)
    inputs, roots, census, _, plan_id = pp.consume(outcome, compute)
    if census is not None:
        entry = mint._producer_by_plan_id(plan_id)
        pp.merge_census(entry.archive, census)
    return inputs, roots
