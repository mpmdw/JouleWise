"""Indexed block-5 reported energy; arithmetic is owned by the pure kernel."""
from __future__ import annotations

import contextvars
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

from joulewise import paper_reported_energy as energy
from joulewise.analysis_engine import inputs
from joulewise.authentication_io import read_authentication_input
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins, load_window_index, select_analysed_attempts, sealed_pack_table
from joulewise.b5_analysis.archive import open_attempt_record, open_archive
from joulewise.b5_analysis.kept_units import KeptUnits, _strict_json, load_kept_units
from joulewise.b5_analysis.bracket import evaluate_window_bracket
from joulewise.b5_analysis.context import build_context
from joulewise.bundle_read import BundleReader, _phase_prompt_counts
from joulewise.whole_window import (
    ArchiveContext, AuthenticatedConsumptionSession, MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    NEG8_HARVEST_ALLOWANCE_RECORD, canonical_sha256, custody_telemetry_identity,
    whole_window_drift_allowances, archive_context_operative_bound_s,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = energy.SCHEMA


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _tokens(reader, summary, metadata, identity):
    provenance = inputs.token_provenance_from_artifacts(summary, metadata)
    workload = metadata.get('workload_provenance', {}) if isinstance(metadata, Mapping) else {}
    observed = metadata.get('workload_observed', {}) if isinstance(metadata, Mapping) else {}
    prompt = workload.get('prompt', {})
    events = reader.events()
    policy = provenance['output_policy']
    frozen_policy = ({k: policy.get(k) for k in ('name', 'requested_tokens', 'sampler')}
                     if isinstance(policy, Mapping) else None)
    tokenizer = provenance['tokenizer_identity']
    return {'source': 'runtime_observed', 'output': observed.get('output_token_count'),
            'total': observed.get('token_count'), 'prompt_realized': prompt.get('realized_token_count'),
            'tokenize_end': _phase_prompt_counts(events, event_type='phase_end', phase='tokenize'),
            'prefill_start': _phase_prompt_counts(events, event_type='phase_start', phase='prefill'),
            'tokenizer_sha256': energy._digest(tokenizer) if tokenizer is not None else None,
            'output_policy_sha256': energy._digest(frozen_policy) if frozen_policy is not None else None}


def normalized_rows(cell, kept, *, session, runs_root, context, binding, kept_units,
                    strict_validator, allowances, b_override_s=None) -> list[dict]:
    if b_override_s is not None:
        raise AnalysisRefusal('b_override_s_unsupported')
    all_units = [unit for units in kept.cell.kept.values() for unit in units] + list(kept.cell.dropped)
    kept_ids = {(u.stratum, u.unit_id) for units in kept.cell.kept.values() for u in units}
    dropped_ids = {(u.stratum, u.unit_id) for u in kept.cell.dropped}
    expected_bundles = {}
    for stratum, size, start in (('repeat', 1, 1), ('quad', 4, 11)):
        units = sorted((u for u in all_units if u.stratum == stratum), key=lambda u: u.positions)
        for i, unit in enumerate(units):
            if len(unit.run_ids) != size:
                raise AnalysisRefusal('exclusions_plan_mismatch')
            owner_kept = ((stratum, unit.unit_id) in kept_ids and (stratum, unit.unit_id) not in dropped_ids)
            for slot, run_id in enumerate(unit.run_ids):
                expected_bundles[start + size*i + slot] = (owner_kept, run_id)
    for ordinal in energy._kept_ordinals(kept):
        try:
            owner_kept, run_id = expected_bundles[ordinal]
            if not owner_kept or cell['members'][ordinal - 1]['bundle_id'] != run_id:
                raise AnalysisRefusal('exclusions_plan_mismatch')
        except (KeyError, IndexError, TypeError):
            raise AnalysisRefusal('exclusions_plan_mismatch') from None
    rows = []
    metric = {'name': cell['metric'], 'window_class': 'phase',
              'metric_tag': cell['cell_id'], 'target_precheck_path': cell['target_precheck_path']}
    cooldowns = inputs.campaign_cooldown_evidence(Path(runs_root), None)
    for ordinal in energy._kept_ordinals(kept):
        member = cell['members'][ordinal - 1]
        bundle_id = member['bundle_id']
        summary = session.summary_for(bundle_id)
        if not isinstance(summary, Mapping):
            raise AnalysisRefusal('whole_window_verdict_provenance_invalid')
        provenance = session.provenance_for(bundle_id)
        actual = provenance.get('operative_fiducial_bound_s') if isinstance(provenance, Mapping) else None
        expected = archive_context_operative_bound_s(context)
        if not _finite(actual) or not _finite(expected) or actual != expected:
            raise AnalysisRefusal('operative_bound_not_the_window_bracket')
        path = Path(runs_root) / bundle_id
        reader = BundleReader(path)
        config, metadata = reader.raw_config(), reader.raw_metadata()
        identity = inputs.realized_scientific_identity(config, metadata)
        identifier = identity.get('model', {}).get('name') if isinstance(identity, Mapping) else None
        model = {'Qwen3-1.7B-4bit': 'qwen3-1p7b', 'Qwen3-8B-4bit': 'qwen3-8b'}.get(identifier, identifier)
        try:
            problems = tuple(strict_validator(path, True))
        except Exception:
            problems = ('bundle_strict_invalid',)
        triangle = custody_telemetry_identity(path, summary=summary, metadata=metadata)
        if triangle.custody_bound_config and not triangle.triangle_agrees:
            problems += ('telemetry_triangle_disagrees',)
        evidence = inputs.BundleEvidence(entry=member, bundle_id=bundle_id, relative_path=bundle_id,
            path=path, summary=summary, metadata=metadata, raw_config=config, strict_problems=problems,
            base_reason_codes=(), config_sha256=member['config_sha256'], summary_sha256=None,
            replacement_classification='registered', inclusion_status='included',
            campaign_cooldown=cooldowns.get(bundle_id), whole_window_drift_allowance_required=True,
            whole_window_drift_allowances=allowances)
        precheck = inputs.window_evidence_precheck(evidence, metric)
        if problems:
            kept_units.stop_if_member_code_on_kept_unit(kept.cell.cell_id, bundle_id, 'bundle_strict_invalid')
        for reason in precheck['reasons']:
            kept_units.stop_if_member_code_on_kept_unit(kept.cell.cell_id, bundle_id, reason,
                                                       p42_precheck=True)
        bounds, reasons = inputs.deterministic_bounds(evidence, metric)
        if 'whole_window_drift_allowance_unrecorded' in reasons:
            raise energy.PaperReportedEnergyRefusal('paper_reported_energy_whole_window_allowance_unrecorded')
        # Missing or malformed kinds remain absent; the kernel owns that refusal.
        bounds = {k: v for k, v in bounds.items() if k in energy.BOUND_KINDS and _finite(v) and v >= 0}
        index = ordinal - 1
        unit = ({'kind':'repeat', 'index':ordinal, 'position':None} if ordinal <= 10 else
                {'kind':'abba', 'index':(index-10)//4+1, 'position':('A1','B1','B2','A2')[(index-10)%4]})
        rows.append({'member': dict(member), 'model': model, 'phase': cell['projection_registration']['phase'],
            **{k:binding[k] for k in ('selection_sha256','prompt_pin_sha256','whole_window_basis_sha256')},
            'strict_valid': not problems and not precheck['reasons'], 'unit':unit,
            'energy_j': inputs.metric_value(summary, metric), 'bounds_j':bounds,
            'tokens': _tokens(reader, summary, metadata, identity)})
    return rows


def project_pack(spec, kept_units: KeptUnits, *, context: ArchiveContext | None, runs_root: Path,
                 evaluation_basis_sha256, selection_sha256, prompt_pin_sha256, strict_validator,
                 b_override_s=None, minimum=5) -> dict:
    if b_override_s is not None:
        raise AnalysisRefusal('b_override_s_unsupported')
    window = kept_units.window
    result = {'schema_version':SCHEMA, 'mode':'production',
              'window':{k:getattr(window,k) for k in ('pack','plan_id','attempt','harvest_pin')},
              'exclusions_sha256':kept_units.exclusions_sha256, 'sensitivity_label':kept_units.sensitivity_label,
              'b_override_s':b_override_s, 'cells':[], 'refused_cells':[]}
    session = None
    allowances = {}
    if context is not None:
        ids = {run for i in range(3) for units in kept_units.for_reported_cell(spec,i).cell.kept.values()
               for unit in units for run in unit.run_ids}
        session = AuthenticatedConsumptionSession(Path(runs_root), ids, mode='issuing',
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, archive_context=context)
        allowance_result = whole_window_drift_allowances(Path(runs_root), ids, consumption_session=session,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            neg8_harvest_archive=context.neg8_harvest_archive)
        # The allowance reader prepares/authenticates the session. Stop before
        # normalized_rows opens a member, preserving the session's own reason.
        if session.refusal_reasons:
            raise AnalysisRefusal(sorted(session.refusal_reasons)[0])
        if not session.ready:
            raise AnalysisRefusal('whole_window_verdict_provenance_invalid')
        allowances = allowance_result.allowances if allowance_result.status == 'allowances' else {}
    for i, cell in enumerate(spec['reported_energy_cells']):
        kept = None
        try:
            if context is None:
                raise energy.PaperReportedEnergyRefusal('paper_reported_energy_whole_window_allowance_unrecorded')
            kept = kept_units.for_reported_cell(spec,i)
            model, _ = energy._cell_identity(cell['cell_id'])
            binding = {'model':model, 'cell_id':cell['cell_id'], 'extraction_spec_sha256':energy._digest(spec),
                'selection_sha256':selection_sha256,'prompt_pin_sha256':prompt_pin_sha256,
                'whole_window_basis_sha256':evaluation_basis_sha256,'attribution_floor_j':0.0}
            rows = normalized_rows(cell, kept, session=session, runs_root=runs_root, context=context,
                binding=binding, kept_units=kept_units, strict_validator=strict_validator,
                allowances=allowances, b_override_s=b_override_s)
            binding['attribution_floor_j'] = max((row['bounds_j'][energy.BOUND_KINDS[0]] for row in rows
                if energy.BOUND_KINDS[0] in row['bounds_j']), default=0.0)
            result['cells'].append(energy._project_cell(cell,rows,binding,kept=kept,
                exclusions_sha256=kept_units.exclusions_sha256,minimum=minimum))
        except energy.PaperReportedEnergyRefusal as exc:
            if kept is None:
                try:
                    kept = kept_units.for_reported_cell(spec,i)
                except (AnalysisRefusal, energy.PaperReportedEnergyRefusal):
                    pass
            result['refused_cells'].append({'cell_id':cell['cell_id'],'code':exc.code,
                'target':kept.cell.target if kept is not None else True,
                'plan_code':'whole_window_drift_allowance_unrecorded' if exc.code ==
                'paper_reported_energy_whole_window_allowance_unrecorded' else None})
    return result


def issue_pack(window_index: Path, pack: str, *, repo_root=REPO_ROOT, strict_validator=None,
               seal_pins=None, pack_table=None, test_only_allow_synthetic_binding=False) -> dict:
    if pack not in ('alpha','beta'):
        raise AnalysisRefusal('floor_pack_required')
    pins = seal_pins or SealPins.load()
    table = sealed_pack_table(seal_pins=pins) if pack_table is None else pack_table
    index = load_window_index(window_index,seal_pins=pins,pack_table=table)
    records = tuple(open_attempt_record(e,seal_pins=pins,pack_table=table) for e in index.entries)
    window = select_analysed_attempts(index,records,seal_pins=pins)[pack]
    prefix = f'sources/repo/configs/campaigns/{window.pack_id}/'
    synthetic = None
    if test_only_allow_synthetic_binding is True:
        synthetic = hashlib.sha256(read_authentication_input(window.archive_root / (prefix+'plan_tree.json'),
            grammar='json',label='synthetic reported-energy plan tree')).hexdigest()
    archive = open_archive(window,seal_pins=pins,pack_table=table,synthetic_plan_tree_sha256=synthetic)
    local_pack = Path(repo_root)/'configs/campaigns'/window.pack_id
    raw = read_authentication_input(local_pack/'extraction_spec.json',grammar='json',label='reported-energy extraction spec')
    if raw != archive.source_bytes(prefix+'extraction_spec.json'):
        raise AnalysisRefusal('extraction_spec_differs_from_archive')
    spec = _strict_json(raw,'extraction_spec_invalid')
    planned = {}
    for cell in spec['cells']:
        strata = planned.setdefault(cell['condition_family_id'],{})
        stratum = 'repeat' if cell['kind']=='absolute' else 'quad'
        strata[stratum] = ({m['bundle_id']:(m['bundle_id'],) for m in cell['members']} if stratum=='repeat' else
            {b['block_id']:tuple(b['members'][p] for p in ('A1','B1','B2','A2')) for b in cell['blocks']})
    kept = load_kept_units(archive,sealed_catalog_sha256=pins.sealed['catalog_sha256'],planned_units=planned)
    bracket = evaluate_window_bracket(archive,repo_root=Path(repo_root))
    allowance = _strict_json(archive.output_bytes(NEG8_HARVEST_ALLOWANCE_RECORD),'neg8_allowance_record_invalid')
    claim_prefix = ('night-custody/'+window.claim_runs_root.relative_to(window.custody_root).as_posix()+'/'
                    if window.claim_runs_root.is_relative_to(window.custody_root) else 'claim-runs/')
    row = _strict_json(archive.source_bytes('sources/'+claim_prefix+allowance['verdict']['path']),
                       'whole_window_verdict_provenance_invalid')
    if (canonical_sha256(row)!=allowance['verdict']['row_sha256'] or
        row['evaluation_basis']['sha256']!=allowance['verdict']['evaluation_basis_sha256']):
        raise AnalysisRefusal('whole_window_verdict_provenance_invalid')
    context = build_context(archive,kept,bracket,row,test_only_allow_synthetic_binding=test_only_allow_synthetic_binding)
    from joulewise.b5_analysis.steps import require_primary_context
    require_primary_context(context)
    parents = []
    for name in ('selection.json','prefill_prompt_pin.json'):
        archived = archive.source_bytes(prefix+'prefill_pin/'+name)
        local = read_authentication_input(local_pack/'prefill_pin'/name,grammar='json',label='reported-energy sealed parent')
        if archived != local:
            raise AnalysisRefusal('reported_energy_parent_differs_from_archive')
        parents.append(hashlib.sha256(archived).hexdigest())
    energy._validate_registered_spec(spec)
    if strict_validator is None:
        from joulewise.cli import validate_bundle
        strict_validator = validate_bundle
    return project_pack(spec,kept,context=context,runs_root=window.claim_runs_root,
        evaluation_basis_sha256=row['evaluation_basis']['sha256'],selection_sha256=parents[0],
        prompt_pin_sha256=parents[1],strict_validator=strict_validator)



def reported_energy_issuance_gate(ctx):
    """Authenticate registered parents and replay one sealed indexed pack."""
    from joulewise import paper_custody as custody
    from joulewise.floor_extraction import validate_extraction_spec, validate_d117_mint_consumption_report
    role = custody.InputRole
    try:
        spec = custody._json_object(ctx.raws[role.EXTRACTION_SPEC])
        report = custody._json_object(ctx.raws[role.EXTRACTION_REPORT])
        codes = list(validate_extraction_spec(spec))
        energy._validate_registered_spec(spec)
        codes.extend(validate_d117_mint_consumption_report(report))
    except energy.PaperReportedEnergyRefusal as exc:
        codes = [exc.code]
    except (ValueError, TypeError, KeyError):
        codes = ['paper_reported_energy_schema_invalid']
    if codes:
        return custody._FamilyReplay(False, False, (), tuple(codes))
    pack = None
    for candidate, model in (('alpha','qwen3-1p7b'),('beta','qwen3-8b')):
        relative = f'configs/campaigns/d117_floor_{model}_v5/extraction_spec.json'
        if custody._git_blob(ctx.repository,ctx.head,relative) == ctx.raws[role.EXTRACTION_SPEC]:
            pack = candidate
            break
    if pack is None:
        return custody._FamilyReplay(False,False,(),('reported_energy_spec_not_a_sealed_pack',))
    def replay():
        index = custody._tracked_window_index(ctx)
        return issue_pack(index,pack,repo_root=ctx.repository)
    try:
        projection = contextvars.Context().run(replay)
    except Exception:
        return custody._FamilyReplay(False,False,(),('reported_energy_replay_refused',))
    try:
        basis = custody._json_object(ctx.raws[role.WHOLE_WINDOW_BASIS])
        selection = hashlib.sha256(ctx.raws[role.G2A_SELECTION]).hexdigest()
        prompt = hashlib.sha256(ctx.raws[role.PROMPT_PIN]).hexdigest()
        if not projection['cells'] or any(
            c['binding']['selection_sha256'] != selection or c['binding']['prompt_pin_sha256'] != prompt
            or c['binding']['whole_window_basis_sha256'] != basis.get('sha256') for c in projection['cells']):
            return custody._FamilyReplay(False,False,(),('reported_energy_parent_mismatch',))
    except (ValueError, TypeError, KeyError):
        return custody._FamilyReplay(False,False,(),('reported_energy_parent_mismatch',))
    issued = {c['cell_id'] for c in projection['cells']}
    grants = tuple(custody._RenderGrant('cell',s) for s in ctx.subjects if s in issued)
    admitted = bool(ctx.subjects) and all(s in issued for s in ctx.subjects)
    return custody._FamilyReplay(True,admitted,grants,(),custody._freeze_json(projection))
