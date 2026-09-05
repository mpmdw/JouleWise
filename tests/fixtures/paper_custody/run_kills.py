"""Run the Round-5 kill mutations sequentially, restoring scoped bytes exactly.

Only the four user-permitted unittest modules may run. These mutations are
synthetic test controls, and fixture receipt repins prevent stale receipts
from masquerading as kills of the intended behavior. No discovery/agent/live
measurement process is launched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CUSTODY = 'joulewise/paper_custody.py'
RENDER = 'joulewise/paper_rendering.py'
BOUND = 'joulewise/analysis_engine/claim_side_bound.py'
CONTRACT = 'docs/contracts/paper_supply_custody.md'
MAP = 'configs/paper_supply/supply_map.json'
C = 'tests.test_paper_custody.RoundFiveTests.'
A = 'tests.test_authentication_io.PaperRendererBoundaryTests.'
R = 'tests.test_paper_rendering.PaperRenderingTests.'

# id, file, exact old/new source, test that must fail
MUTATIONS = [
 ('F1-wrong-class', CUSTODY, 'output_type = spec.issuing_type if mode == "production" else spec.fixture_type',
  'output_type = spec.issuing_type', C+'test_issuing_fixture_type_matrix'),
 ('F1-fixture-inherits-verified', CUSTODY, 'class FixtureD165Closeout(_CustodyResult):',
  'class FixtureD165Closeout(VerifiedD165Closeout):', C+'test_issuing_fixture_type_matrix'),
 ('F1-wrapper-deleted', RENDER, '@_issued_renderer(VerifiedD165Closeout, "outcome")\n', '', A+'test_registered_renderers_require_issuing_boundary'),
 ('F1-annotation-widened', RENDER, 'value: VerifiedD165Closeout) -> str:', 'value: object) -> str:', A+'test_registered_renderers_require_issuing_boundary'),
 ('F1-unregistered-renderer', RENDER, '__all__ = list(_RENDERERS)', '__all__ = list(_RENDERERS)\n\ndef render_rogue(value):\n    return "paper"', A+'test_registered_renderers_require_issuing_boundary'),
 ('F1-grant-check-deleted', RENDER, 'if any(_RenderGrant(required_grant, subject) not in evidence.grants for subject in evidence.subjects):',
  'if False:', R+'test_d165_issued_control_and_subject_grants'),
 ('F2-closure-only-overclaim', CONTRACT, 'construction token created inside private seam closures',
  'construction token held only inside private seam closures', C+'test_contract_threat_model_matches_capability_wire'),
 ('F2-tokenless-omitted', CONTRACT, 'and tokenless `object.__new__` instances',
  'and `object.__new__` instances', C+'test_contract_threat_model_matches_capability_wire'),
 ('F3-empty-replay-issues', CUSTODY, 'raise PaperCustodyRefusal("paper_custody_issuance_gate_unregistered")',
  'return _FamilyReplay(True, True, (), ())', C+'test_closed_gate_registry'),
 ('F3-receipt-issues-fixture', CUSTODY, 'elif replay.admitted or replay.grants:', 'elif False:', C+'test_closed_gate_registry'),
 ('F3-unknown-gate-default', CUSTODY, 'gate = _ISSUANCE_GATES.get((ctx.family, ctx.issuance_gate_id))',
  'gate = _ISSUANCE_GATES.get((ctx.family, ctx.issuance_gate_id), _d165_issuance_gate)', C+'test_closed_gate_registry'),
 ('F3-fixture-dispatches-gate', CUSTODY, 'if ctx.mode == "test_fixture_non_issuing":',
  'if False:', C+'test_closed_gate_registry'),
 ('F3-d165-B-collapsed', CUSTODY, 'return _FamilyReplay(True, True, tuple(grants), ())',
  'return _FamilyReplay(True, expected["branch"] == "A", tuple(grants), ())', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-d165-null-issues', CUSTODY, 'if closeout.get("refusal_reason") is not None or closeout.get("branch") is None:\n        return _FamilyReplay(True, False, (), ())',
  'if closeout.get("refusal_reason") is not None or closeout.get("branch") is None:\n        return _FamilyReplay(True, True, (_RenderGrant("outcome", ctx.supply_role),), ())', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-d165-A-grants-lost', CUSTODY, 'grants.append(_RenderGrant(kind, ctx.supply_role))',
  'pass', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-d165-owner-skipped', CUSTODY, 'codes = validate_d165_paper_sources(',
  'codes = (lambda **kwargs: ())(', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-acceptance-skipped', CUSTODY, '    _validate_floor_acceptance(ctx)\n    if ctx.subjects != (ctx.supply_role,):',
  '    if ctx.subjects != (ctx.supply_role,):', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-wrong-floor-accepted', CUSTODY, 'or value.get("floor_sha256") != _sha256(ctx.raws[InputRole.FLOOR_ARTIFACT])',
  'or False', C+'test_d165_gate_branches_and_floor_acceptance'),
 ('F3-claim-ready-flag-trusted', CUSTODY, 'if evaluated["claim_ready_for_l2_l3"] is True and evaluated["claim_level_ceiling"] in {"L2", "L3"}:',
  'if contrast["claim_evaluation"]["claim_ready_for_l2_l3"] is True:', C+'test_claim_gate_per_contrast'),
 ('F3-claim-owner-skipped', CUSTODY, 'codes.extend(validate_claim_verdicts(artifact, frozen_manifest=manifest))',
  'codes.extend([])', C+'test_claim_gate_per_contrast'),
 ('F3-sidecar-skipped', CUSTODY, 'codes.extend(validate_claim_side_bound(sidecar, claim_verdicts_sha256=_sha256(ctx.raws[InputRole.CLAIM_VERDICTS]),\n                                           finalized_manifest=manifest, floor_artifact=floor))',
  'codes.extend([])', C+'test_claim_gate_per_contrast'),
 ('F3-embedded-floor-skipped', CUSTODY, 'if embedded_floor != ctx.raws[InputRole.FLOOR_ARTIFACT]:',
  'if False:', C+'test_claim_gate_per_contrast'),
 ('F3-sidecar-wrong-digest', BOUND, 'return ("claim_side_bound_reader_digest_mismatch",)',
  'return ()', C+'test_claim_gate_per_contrast'),
 ('F3-sidecar-wrong-cell', BOUND, 'return ("claim_side_bound_cell_mismatch",)',
  'return ()', C+'test_claim_gate_per_contrast'),
 ('F3-sidecar-wrong-lineage', BOUND, 'return ("claim_side_bound_lineage_mismatch",)',
  'return ()', C+'test_claim_gate_per_contrast'),
 ('F3-sidecar-wrong-bound', BOUND, 'return ("claim_side_bound_arithmetic_mismatch",)',
  'return ()', C+'test_claim_gate_per_contrast'),
 ('F3-source-owner-omitted', CUSTODY, '("analysis_engine.claims.evaluate_claim", evaluate_claim),',
  '', C+'test_gate_sources_change_receipt_digest'),
 ('F4-authority-ignored', CUSTODY, 'if binding.authority == "git_blob":',
  'if False:', C+'test_git_blob_dispatch_checks_blob_before_parse_and_worktree'),
 ('F4-wrong-root', CUSTODY, 'return repository if binding.base == "repository" else runs_root',
  'return runs_root', C+'test_git_blob_dispatch_checks_blob_before_parse_and_worktree'),
 ('F4-blob-comparison-skipped', CUSTODY, 'if _sha256(blob) != binding.expected_sha256:',
  'if False:', C+'test_git_blob_dispatch_checks_blob_before_parse_and_worktree'),
 ('F4-fixture-substitute', MAP, 'configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json',
  'tests/fixtures/paper_custody/extraction_spec.json', C+'test_production_git_blob_coverage'),
 ('F5-dead-literal', CUSTODY, 'raise PaperCustodyRefusal("paper_custody_role_unregistered")',
  'raise PaperCustodyRefusal("paper_custody_request_invalid")\n        "paper_custody_role_unregistered"', C+'test_refusal_constructor_ast_census'),
 ('F5-declared-only', CUSTODY, 'PAPER_CUSTODY_REFUSAL_CODES = frozenset(\n    {\n        "paper_custody_request_invalid",',
  'PAPER_CUSTODY_REFUSAL_CODES = frozenset(\n    {\n        "paper_custody_declared_only",\n        "paper_custody_request_invalid",', C+'test_refusal_constructor_ast_census'),
 ('F5-undeclared-call', CUSTODY, '__all__ = [',
  'if False:\n    raise PaperCustodyRefusal("paper_custody_undeclared")\n\n__all__ = [', C+'test_refusal_constructor_ast_census'),
 ('F5-variable-argument', CUSTODY, 'raise PaperCustodyRefusal("paper_custody_role_unregistered")',
  'raise PaperCustodyRefusal(_SUPPLY_MAP_SCHEMA)', C+'test_refusal_constructor_ast_census'),
]


def main():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    records = []
    paths = {ROOT / item[1] for item in MUTATIONS} | {ROOT / MAP}
    originals = {path: path.read_bytes() for path in paths}
    selected = set(sys.argv[1:])
    try:
        for identity, relative, old, new, test in MUTATIONS:
            if selected and identity not in selected:
                continue
            if not test.startswith(('tests.test_paper_custody.', 'tests.test_authentication_io.', 'tests.test_paper_rendering.', 'tests.test_d165_dominance_closeout.')):
                raise ValueError('unpermitted test')
            path = ROOT / relative
            source = originals[path].decode()
            if source.count(old) != 1:
                raise ValueError(f'{identity}: mutation target count {source.count(old)}')
            try:
                path.write_text(source.replace(old, new, 1))
                if relative != MAP:
                    repin = subprocess.run([sys.executable, 'tests/fixtures/paper_custody/repin.py'], cwd=ROOT, env=env,
                                           capture_output=True, text=True)
                    if repin.returncode:
                        raise RuntimeError(f'{identity}: fixture repin failed: {repin.stderr}')
                result = subprocess.run([sys.executable, '-m', 'unittest', test], cwd=ROOT, env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                tail = result.stdout.rstrip().splitlines()[-9:]
                killed = result.returncode == 1 and 'FAILED (' in result.stdout and 'Ran 1 test' in result.stdout
                records.append({'id': identity, 'cmd': f'PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py {identity}',
                                'test': test, 'exit_code': result.returncode, 'killed': killed, 'tail': tail})
                print(f'{identity}: {"KILLED" if killed else "SURVIVED/ERROR"} (exit {result.returncode})', flush=True)
                if not killed:
                    print(result.stdout, flush=True)
            finally:
                path.write_bytes(originals[path])
                (ROOT / MAP).write_bytes(originals[ROOT / MAP])
    finally:
        for path, raw in originals.items():
            path.write_bytes(raw)
        out = Path('/tmp/paper-custody-r5-kills.json')
        out.write_text(json.dumps(records, indent=2) + '\n')
    passed = bool(records) and all(row['killed'] for row in records)
    print(f'KILL SUMMARY: {sum(row["killed"] for row in records)}/{len(records)} killed; scoped files restored.', flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
