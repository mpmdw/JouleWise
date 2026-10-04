#!/usr/bin/env python3
"""Archive and authenticate a completed diagnostic G2-a window; print custody only."""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import shutil, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise import calibration_bracketing as brackets, network_time_off, night_gate
from joulewise.calibration_ledger import load_calibration_ledger_snapshot, terminal_head_pin_for_session
from joulewise.cli import validate_bundle
from joulewise.schemas import AdmissionFailureAction, CampaignPolicy, CampaignPolicyProfile
from scripts import generate_g2a_probe_inputs as inputs, summarize_g2a_prefill_probe as summary
from scripts import select_g2a_prefill_length as selector
from scripts.generate_g2a_probe_inputs import harvest_roster as roster
from scripts.summarize_g2a_prefill_probe import network_time_capture_report as clock_report
from scripts.harvest_window import inventory, copy_matches
from scripts.recover_calibration_ledger import recover_harvest_copy

class HarvestRefusal(ValueError):
    pass

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_bytes())

def write(path, value):
    with Path(path).open('xb') as handle:
        handle.write((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())

def anchor_status(path):
    try:
        evidence = read(path / 'metadata.json').get('uncertainty_evidence')
    except (OSError, ValueError, AttributeError):
        return 'not recorded'
    anchor = evidence.get('clock_anchor') if isinstance(evidence, dict) else None
    status = anchor.get('status') if isinstance(anchor, dict) else None
    return status if isinstance(status, str) else 'not recorded'

def group_clear(night):
    started = night / 'chain.started'
    if started.is_symlink():
        raise HarvestRefusal('chain_group_identity_invalid')
    if not started.exists():
        return True  # An admission refusal never owned a chain group.
    pgid = read(started).get('pgid')
    if type(pgid) is not int or pgid <= 1:
        raise HarvestRefusal('chain_group_identity_invalid')
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False

def archive(sources, destination):
    if destination.exists() or any(destination == source or source in destination.parents
                                   or destination in source.parents for source in sources.values()):
        raise HarvestRefusal('archive_exists_or_overlaps_source')
    original = {name: inventory(source) for name, source in sources.items()}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.g2a-archive-', dir=destination.parent) as temporary:
        stage = Path(temporary) / 'archive'
        stage.mkdir()
        for name, source in sources.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_file():
                shutil.copy2(source, target)
            else:
                shutil.copytree(source, target, symlinks=True)
            if inventory(source) != original[name] or not copy_matches(original[name], inventory(stage / name)):
                raise HarvestRefusal('archive_copy_mismatch')
        sums = ''.join(f"{row['sha256']}  {name if path == '.' else name + '/' + path}\n" for name, rows in original.items()
                       for path, row in rows.items() if 'sha256' in row)
        (stage / 'SHA256SUMS').write_text(sums)
        os.rename(stage, destination)
    return original

def command(runner, root, argv):
    result = runner([str(root / '.venv/bin/python'), '-B', *map(str, argv)], cwd=root,
                    capture_output=True, text=True, check=False, timeout=300)
    if result.returncode:
        raise HarvestRefusal('governed_ledger_procedure_refused')
    return json.loads(result.stdout)

def harvest(args, *, now=time.time, clear=group_clear, runner=subprocess.run):
    args.archive_root = args.archive_root.resolve()
    plan = night_gate.NightPlan.from_mapping(read(args.plan))
    night_root, root = Path(plan.custody_root), Path(plan.measurement_root)
    registration = Path(plan.registration_path)
    if not registration.is_absolute():
        registration = root / registration
    if (args.plan.resolve().parent != night_root.resolve() or plan.receipt_class != 'DIAGNOSTIC_NO_PACK'
            or sha(registration) != night_gate.D166_REGISTRATION_SHA256):
        raise HarvestRefusal('g2a_plan_authentication_failed')
    night = night_root / 'night'
    if now() < plan.t0_epoch_s + plan.window_max_s + 300:
        raise HarvestRefusal('harvest_before_completion_boundary')
    if not (night / 'courier.sent').is_file() or not clear(night):
        raise HarvestRefusal('delivery_missing_or_chain_group_alive')
    chain = Path(plan.chain_path)
    if sha(chain) != Path(plan.chain_sha256_path).read_text().split()[0]:
        raise HarvestRefusal('chain_authentication_failed')
    text = chain.read_text()
    if night_gate.chain_literal(text, 'NIGHT_CHAIN_INTERFACE') != 'g2a-reservation-v1':
        raise HarvestRefusal('unsupported_chain')
    g2a = Path(night_gate.chain_literal(text, 'G2A_ROOT'))
    ledger = Path(night_gate.chain_literal(text, 'CALIBRATION_LEDGER'))
    pin = Path(night_gate.chain_literal(text, 'LEDGER_HEAD_PIN'))
    sources = {'night-custody': night_root, 'g2a-root': g2a,
               'physical-ledger/ledger.jsonl': ledger, 'physical-ledger/head-pin.json': pin}
    original = archive(sources, args.archive_root)
    derived = args.archive_root / 'derived'
    derived.mkdir()
    record = {'schema': 'joulewise.harvest_g2a_window.v1', 'plan_id': plan.plan_id,
              'plan_sha256': sha(args.plan), 'archive_root': str(args.archive_root),
              'verdict': 'REFUSED', 'cause_codes': [], 'members': [], 'pin_advance': None}
    if not (night / 'chain.started').exists():
        # Registration G2A-25G83-B2 section 7: a window refused before its chain
        # started (gate, OFF receipt, clean dwell, start budget) is a null window.
        # It is not a sweep, consumes no recovery allowance and owns no session.
        record.update(verdict='NULL', cause_codes=['chain_never_started'], outputs={})
        write(args.archive_root / 'harvest.json', record)
        return record
    try:
        wp, runs = g2a / 'window-plan', g2a / 'runs'
        frozen = wp / 'calibration_plan.json'
        value = read(wp / 'g2a-input-inventory.json')
        ids = roster(value)
        inputs.check_harvest_inputs(measurement_root=root, root=g2a, ledger=ledger, head_pin=pin)
        policy_path = inputs.harvest_campaign_policy_path(measurement_root=root, inventory=value)
        # The inventory names the policy; only a claim-grade one may judge a bracket
        # (production profile, bracket required, admission enabled and aborting).
        policy = CampaignPolicy.from_mapping(read(policy_path))
        if (policy.profile != CampaignPolicyProfile.PRODUCTION or not policy.calibration_bracketing.require_bracket
                or not policy.idle_admission.enabled or policy.idle_admission.on_fail != AdmissionFailureAction.ABORT):
            raise HarvestRefusal('campaign_policy_not_claim_grade')
        if value['window_id'] != plan.plan_id or value['session_id'] != plan.plan_id + '-calibration':
            raise HarvestRefusal('window_identity_mismatch')
        # Authenticate against the committed seed first. A mid-session receipt
        # is never a head-pin candidate. The governed open extension can be
        # assessed as incomplete before recovery closes it below.
        snap = load_calibration_ledger_snapshot(ledger, pin, require_committed_pin=True,
            mode='read_replay', repo_root=root, baseline_sequence=read(frozen)['calibration_ledger']['head_sequence'],
            baseline_digest=read(frozen)['calibration_ledger']['head_digest'])
        session = snap.bracket_session_by_id.get(value['session_id'])
        if session and session.state == 'open':
            if not snap.is_governed_open_bracket_extension:
                raise HarvestRefusal('ledger_authentication_failed')
        else:
            if set(snap.refusal_reasons) - {'calibration_ledger_head_mismatch'}:
                raise HarvestRefusal('ledger_authentication_failed')
            if session:
                candidate = terminal_head_pin_for_session(ledger, session_id=value['session_id'])
                scratch_pin = derived / 'physical-head-pin.json'
                write(scratch_pin, candidate)
                snap = load_calibration_ledger_snapshot(ledger, scratch_pin, require_committed_pin=False,
                    mode='read_replay', repo_root=root,
                    baseline_sequence=read(frozen)['calibration_ledger']['head_sequence'],
                    baseline_digest=read(frozen)['calibration_ledger']['head_digest'])
            if snap.refusal_reasons:
                raise HarvestRefusal('ledger_authentication_failed')
        valid, captures = set(), []
        for run_id in ids:
            path = runs / run_id
            problems = validate_bundle(path, strict=True) if path.exists() else ['member_missing']
            succeeded = path.exists() and (path / 'summary_metrics.json').is_file() and read(path / 'summary_metrics.json').get('status') == 'succeeded'
            clock_status = anchor_status(path)
            # Registration section 6 (seal T3, condition C1): the within-capture
            # clock admission binds members; only a 'bounded' anchor is valid.
            # The reducer's per-phase eligibility flag is never consulted here.
            if not problems and succeeded and clock_status == 'bounded':
                valid.add(run_id)
            record['members'].append({'run_id': run_id, 'valid': run_id in valid, 'problems': problems,
                                      'clock_anchor_status': clock_status})
            if path.exists():
                captures.append((run_id, path))
        session = snap.bracket_session_by_id.get(value['session_id'])
        binding, bracket, reasons = None, {'status': 'failed'}, ('bracket_incomplete',)
        if session:
            if session.plan_sha256 != sha(frozen) or session.runs_root != str(runs):
                raise HarvestRefusal('bracket_session_binding_mismatch')
            captures.extend((row.attempt_id, Path(row.custody_locator)) for row in session.finalized_slots.values())
            if session.state == 'finalized':
                binding = brackets.build_calibration_bracket_binding(snap, session_id=value['session_id'],
                    window_id=value['window_id'], plan_id=value['calibration_plan']['plan_id'], plan_sha256=sha(frozen),
                    evidence_root_id=value['evidence_root_id'], runs_root=runs)
                bracket, reasons = brackets.calibration_bracket_for_bundles(runs, [runs / x for x in sorted(valid)],
                    policy.calibration_bracketing, mode='read_replay', ledger_snapshot=snap, bracket_binding=binding,
                    bracket_window_id=value['window_id'], bracket_plan_id=value['calibration_plan']['plan_id'],
                    bracket_plan_sha256=sha(frozen), bracket_evidence_root_id=value['evidence_root_id'])
        write(derived / 'bracket.json', {'binding': binding, 'assessment': bracket, 'reasons': reasons})
        counts, out = derived / 'counts.json', derived / 'summary.json'
        if summary.main(['--config-root', str(g2a / 'prefill-probe-configs'), '--input-inventory',
                str(wp / 'g2a-input-inventory.json'), '--runs-root', str(runs), '--counts-output', str(counts),
                '--summary-output', str(out)], valid_run_ids=valid):
            raise HarvestRefusal('summary_regeneration_failed')
        # Registration section 8 (seal T4, condition C2): the harvest's regeneration over
        # valid members is the input; the chain's copy is a check. Equality is required
        # only when every roster member is valid; otherwise the copies differ by
        # construction, the difference is recorded and the verdict follows section 7.
        all_valid = len(valid) == len(ids)
        chain_copy = {}
        for produced, name in ((counts, 'd166-prefill-counts-receipt.json'), (out, 'd166-prefill-resolvability-summary.json')):
            if not (wp / name).exists():
                chain_copy[name] = 'absent'
            elif (wp / name).read_bytes() == produced.read_bytes():
                chain_copy[name] = 'equal'
            elif all_valid:
                raise HarvestRefusal('chain_summary_byte_mismatch')
            else:
                chain_copy[name] = 'differs_invalid_members_excluded'
        record['chain_summary_copy'] = chain_copy
        off_path = night / network_time_off.RECEIPT_BASENAME
        off = read(off_path) if off_path.exists() else None
        if off and (off.get('schema') != network_time_off.SCHEMA
                    or off.get('plan_id') != plan.plan_id or off.get('window_id') != plan.plan_id):
            raise HarvestRefusal('off_receipt_identity_invalid')
        try:
            network_time_off.admit(off)
            off_admitted = True
        except ValueError:
            off_admitted = False
        seen = {path.resolve() for _, path in captures}
        captures.extend((path.name, path) for path in sorted((runs / 'instrument_validation').glob('*'))
                        if path.is_dir() and (path / 'raw/powermetrics.plist').is_file()
                        and path.resolve() not in seen)
        network = clock_report(off if off_admitted else None, captures)
        network.update(off_receipt=off, off_admitted=off_admitted)
        write(derived / 'network-time.json', network)
        causes = list(reasons)
        if bracket.get('status') != 'passed' and not causes:
            causes.append('bracket_not_passed')
        if any(row['small_members'] < 5 for row in read(out)):
            causes.append('rung_valid_small_members_shortfall')
        exit_record = read(night / 'chain.exited') if (night / 'chain.exited').exists() else {}
        if exit_record.get('exit_code') != 0:
            causes.append('chain_nonzero_or_missing_exit')
        if not off_admitted:
            causes.append('network_time_off_not_admitted')
        log = g2a / 'operator-logs/window-chain.log'
        if log.exists() and 'pre_calibration_screen=failed' in log.read_text():
            causes.append('pre_screen_stop')
        record.update(verdict='RECOVER' if causes else 'SELECT', cause_codes=sorted(set(causes)))
        # Registration section 7 (seal T8): a RECOVER window with no capture file in
        # the archive copy counts like a null window for the recovery allowance.
        record['capture_made'] = any((args.archive_root / 'g2a-root' / 'runs').glob('**/raw/powermetrics*.plist'))
        if not causes:
            selection = derived / 'selection.json'
            if selector.main(['--summary', str(out), '--output', str(selection)]):
                raise HarvestRefusal('selector_failed')
            record['selection'] = {'path': str(selection), 'sha256': sha(selection)}
        if any(inventory(source) != original[name] for name, source in sources.items()) or not clear(night):
            raise HarvestRefusal('source_or_process_ownership_changed')
        if session:
            if getattr(args, 'read_only_sources', False):
                terminal = recover_harvest_copy(ledger, pin, repo_root=root,
                    session_id=value['session_id'], plan=frozen, destination=derived,
                    operator_identity=args.operator_identity)
                record['pin_advance'] = {'path': str(derived / 'terminal-pin.json'),
                    'sha256': sha(derived / 'terminal-pin.json'), 'needs_operator_commit': True,
                    'source_pin_unchanged': True, 'source_path': str(pin),
                    'sequence': terminal['sequence'], 'head_digest': terminal['head_digest']}
            else:
                procedure = [root / 'scripts/recover_calibration_ledger.py', '--ledger', ledger, '--head-pin', pin]
                if session.state == 'open':
                    command(runner, root, [*procedure, 'abort-session', '--session-id', value['session_id'],
                            '--plan', frozen, '--reason', 'g2a_harvest_incomplete'])
                terminal = command(runner, root, [*procedure, 'terminal-pin', '--session-id', value['session_id']])
                command(runner, root, [*procedure, 'advance-head-pin', '--session-id', value['session_id'],
                    '--expected-sequence', terminal['sequence'], '--expected-digest', terminal['head_digest'],
                    '--operator-identity', args.operator_identity, '--attestation-reason', 'authenticated G2-a harvest terminal', '--execute'])
                shutil.copy2(ledger, derived / 'terminal-ledger.jsonl')
                shutil.copy2(pin, derived / 'terminal-pin.json')
                record['pin_advance'] = {'path': str(pin), 'sha256': sha(pin), 'needs_operator_commit': True}
        if getattr(args, 'read_only_sources', False) and any(
                inventory(source) != original[name] for name, source in sources.items()):
            raise HarvestRefusal('source_or_process_ownership_changed')
        record['outputs'] = {path.name: sha(path) for path in sorted(derived.iterdir()) if path.is_file()}
    except Exception as error:
        # Parse and replay exceptions can contain measured data. Custody-only
        # stdout never echoes them; the mechanical fault has a separate class.
        record.update(verdict='REFUSED', cause_codes=[str(error) if isinstance(error, HarvestRefusal)
                                                    else 'archive_or_authentication_fault'],
                      fault={'type': type(error).__name__, 'detail': str(error)})
    write(args.archive_root / 'harvest.json', record)
    return record

def main(argv=None, **injected):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--archive-root', type=Path, required=True)
    parser.add_argument('--operator-identity', required=True)
    parser.add_argument('--read-only-sources', action='store_true',
        help='run governed ledger closure and pin advancement on derived copies; preserve all sources')
    args = parser.parse_args(argv)
    try:
        record = harvest(args, **injected)
    except Exception:
        # A bad archive coordinate may itself overlap immutable evidence.
        refusal = Path(tempfile.mkdtemp(prefix='g2a-harvest-refusal-')) / 'harvest.json'
        write(refusal, {'schema': 'joulewise.harvest_g2a_window.v1', 'verdict': 'REFUSED',
                        'cause_codes': ['completion_delivery_ownership_or_archive_fault']})
        print(f'verdict=REFUSED harvest={refusal} sha256={sha(refusal)}')
        return 3
    print(f"verdict={record['verdict']} members={sum(row['valid'] for row in record['members'])}/{len(record['members'])}")
    print(f"harvest={args.archive_root / 'harvest.json'} sha256={sha(args.archive_root / 'harvest.json')}")
    for name, digest in record.get('outputs', {}).items():
        print(f"path={args.archive_root / 'derived' / name} sha256={digest}")
    return 3 if record['verdict'] == 'REFUSED' else 0

if __name__ == '__main__':
    raise SystemExit(main())
