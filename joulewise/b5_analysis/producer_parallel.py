"""Authenticated step-5 producer preparation; no pinset construction or writes."""
import hashlib
import json

from joulewise.authentication_io import (V2AuthenticationReadSession, active_v2_authentication_session,
                                         read_authentication_input)


def consume_prepared(outcome, compute, pack_path):
    """Restore the worker's governed declaration before its first read row."""
    from . import pack_parallel as pp

    if outcome is not None and outcome.ok:
        from scripts import mint_floor_artifact_generalized as mint
        mint._allow_governed_extraction_spec(pack_path / 'extraction_spec.json')
    return pp.consume(outcome, compute)


def prepare_producer(entry, report, out_dir, bindings, pack):
    from scripts import emit_floor_mint_pinset as emit, mint_floor_artifact_generalized as mint
    from .archive import ArchiveHandle

    if active_v2_authentication_session() is None:
        with V2AuthenticationReadSession():
            return prepare_producer(entry, report, out_dir, bindings, pack)
    from .steps import require_primary_context
    require_primary_context(entry.archive_context)
    # Registry state is process-local. A spawned preparation has exactly the
    # producer authority the serial author installed before this operation.
    key = str(entry.window.claim_runs_root.resolve())
    present, previous = key in mint.BLOCK5_PRODUCERS, mint.BLOCK5_PRODUCERS.get(key)
    mint.BLOCK5_PRODUCERS[key] = entry
    try:
        acceptance_path = entry.window.archive_root / 'sources/inputs/acceptance.json'
        raw = mint._read_block5_archive_input(entry, 'sources/inputs/acceptance.json', 'block5 acceptance')
        acceptance_hash = hashlib.sha256(raw).hexdigest()
        mint._read_block5_archive_input(entry, 'derived/bracket-binding.json', 'block5 bracket binding')
        core = mint._fresh_original_core()
        acceptance = core.load_calibration_acceptance_bound(acceptance_path)
        if acceptance is None:
            raise mint.MintError('issued calibration acceptance failed authentication')
        contract, producer, row = emit._bootstrap_producer(entry.pack_path, entry.window.claim_runs_root,
            report, entry.window.archive_root / 'derived/bracket-binding.json', bindings,
            acceptance, acceptance_hash, entry.ledger_snapshot, f'{pack}/calibration_plan.json',
            'prefill_p2048', kept_units=entry.kept_units)
        try:
            relative = report.resolve().relative_to(out_dir.resolve()).as_posix()
        except ValueError:
            raise mint.MintError('floor_mint_input_path_not_relative') from None
        manifest_row = {'plan_id': entry.producer_plan_id, 'pack': pack,
            'exclusions_sha256': entry.kept_units.exclusions_sha256, 'report': relative,
            'cells': [{'role': cell['role'], 'allowed_consumer_condition_families': cell['allowed_consumer_condition_families']}
                      for cell in row['cells']]}
        plan = read_authentication_input(entry.pack_path / 'calibration_plan.json',
                                        grammar='json', label='sealed producer plan copy')
        if json.loads(plan).get('order_manifest') != 'order_manifest.json':
            raise mint.MintError('producer order manifest must sit beside its plan')
        order = read_authentication_input(entry.pack_path / 'order_manifest.json',
                                         grammar='json', label='sealed producer order manifest copy')
        census = entry.archive.census() if isinstance(entry.archive, ArchiveHandle) else None
        return contract, producer, manifest_row, plan, order, census
    finally:
        if present:
            mint.BLOCK5_PRODUCERS[key] = previous
        else:
            mint.BLOCK5_PRODUCERS.pop(key, None)
