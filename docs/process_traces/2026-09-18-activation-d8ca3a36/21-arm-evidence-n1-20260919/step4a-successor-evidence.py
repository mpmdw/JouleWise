#!/usr/bin/env python3
"""Bench-only, read-only predecessor inspection; writes only attempt evidence.

Called by step4 after arm-env.zsh is sourced. RETIRED_0917_ROOT is the exact
step0 output, never the original discoverable root. Missing evidence refuses.
The count is a separate magistrate-observed record, never inferred from an
absent file or silently defaulted to zero. See README-sequence.md.
"""
import copy
import hashlib
import json
import os
import re
from pathlib import Path


def main():
    observations = []
    sources = {}

    def check(ok, source, assertion):
        message = f'{source}: {assertion}'
        print(('PASS: ' if ok else 'REFUSED: ') + message, flush=True)
        if not ok:
            raise ValueError(message)
        observations.append(message)

    def read(path):
        check(path.is_file() and not path.is_symlink(), path, 'regular evidence file')
        raw = path.read_bytes()
        sources[str(path)] = hashlib.sha256(raw).hexdigest()
        print(f'READ: {path} sha256={sources[str(path)]}', flush=True)
        return raw

    def absent(path):
        check(not os.path.lexists(path), path, 'lstat confirms absent, including dangling symlinks')
        return True

    ident = 'd079-epoch-25g83-derivation-n1-20260917'
    root = Path(os.environ['RETIRED_0917_ROOT'])
    check(root.parent == Path('/Users/edr/night-archive') and
          re.fullmatch(re.escape(ident) + r'-plan-root-retired-\d+', root.name) is not None,
          root, 'exact retired 09-17 root naming and archive parent')
    check(root.is_dir() and not root.is_symlink(), root, 'retired root is a real directory')
    repo = Path(os.environ['MEASUREMENT_ROOT'])
    harvest_dir = repo / 'docs/process_traces/2026-09-17-activation-8789ee70'
    record_path = harvest_dir / '01-n1-20260917-harvest-record.md'
    record = read(record_path).decode()
    check('No ledger session opened, nothing captured; `runs/` never created.' in record,
          record_path, 'harvest records no ledger session, capture, or runs directory')
    sums_path = harvest_dir / '01-harvest-evidence' / (ident + '-harvest-20260917.SHA256SUMS')
    sums = read(sums_path).decode()
    for line in sums.splitlines():
        digest, rel = line.split(maxsplit=1)
        rel = rel.removeprefix('*').removeprefix('./')
        check(not Path(rel).is_absolute() and '..' not in Path(rel).parts,
              sums_path, f'safe relative checksum entry {rel}')
        path = root / rel
        check(hashlib.sha256(read(path)).hexdigest() == digest,
              path, f'bytes match tracked harvest SHA256SUMS {sums_path}')
    result_path = root / 'night/result.json'
    refusal_path = root / 'night/refusal.json'
    result = json.loads(read(result_path))
    receipt = json.loads(read(refusal_path))
    plan_path = root / 'night_plan.json'
    old_plan_raw = read(plan_path)
    old_plan = json.loads(old_plan_raw)
    check(result['plan_id'] == receipt['plan_id'] == old_plan['plan_id'] == ident,
          f'{result_path}, {refusal_path}, {plan_path}', 'same predecessor plan id')
    check(result['verdict'] == receipt['verdict'] == 'REFUSED' and
          result['aborted_reason'] == receipt['refusal']['reason'] == 'night_refused_not_quiet',
          f'{result_path}, {refusal_path}', 'terminal load refusal')
    check(result['chain_exit_code'] is None and result['chain_sha256'] is None,
          result_path, 'chain exit code and chain hash are explicitly null')
    chain_absent = absent(root / 'night/chain.started')
    absent(root / 'operator_logs/derivation-chain.log')
    # The harvest says runs/ never existed. Check that stronger observation;
    # an absent directory has an empty inventory, not unknown missing contents.
    runs_absent = absent(root / 'runs')
    validation_empty = absent(root / 'runs/instrument_validation')

    # Use the freshly byte-copied ledger, without visiting the old clone. Its
    # bytes must still equal those read by the predecessor's recorded probe.
    probe_path = root / 'night_probe_receipt.json'
    probe = json.loads(read(probe_path))
    ledger_path = Path(os.environ['CALIBRATION_LEDGER'])
    ledger_raw = read(ledger_path)
    check(hashlib.sha256(ledger_raw).hexdigest() == probe['ledger_sha256'],
          f'{ledger_path}, {probe_path}', 'ledger bytes unchanged since predecessor probe')
    rows = [json.loads(line) for line in ledger_raw.splitlines() if line.strip()]

    def mentions_predecessor(value):
        if isinstance(value, dict):
            return any(mentions_predecessor(v) for v in value.values())
        if isinstance(value, list):
            return any(mentions_predecessor(v) for v in value)
        return isinstance(value, str) and ident in value

    matching = [row for row in rows if mentions_predecessor(row)]
    check(len(rows) == 76 and matching == [], ledger_path,
          '76 parsed rows; zero predecessor session/reservation/attempt references')
    check_path = harvest_dir / '01-harvest-evidence/22-check.txt'
    dry_run = read(check_path).decode()
    check(f'{ident}: absent' in dry_run and
          f'blocker: session {ident} is not in the ledger' in dry_run,
          check_path, 'harvest ledger dry run independently records absent session')
    zero = dict(chain_started_absent=chain_absent, reservation_absent=not matching,
                session_id=None, capture_writer_ran=False,
                instrument_validation_empty=runs_absent and validation_empty)
    print('DERIVED from the printed file observations: reservation_absent=True; '
          'session_id=null (no ledger session); capture_writer_ran=False '
          '(no chain claim/log/hash/exit, no session/reservation, no runs directory).', flush=True)
    c5 = [row for row in receipt['conditions'] if row['condition_id'] == 'C5']
    check(len(c5) == 1 and isinstance(c5[0]['measured'], dict), refusal_path,
          'exactly one C5 measured mapping')
    harvested = copy.deepcopy(receipt)
    measured = next(row['measured'] for row in harvested['conditions'] if row['condition_id'] == 'C5')
    if 'zero_capture_evidence' in measured:
        check(measured['zero_capture_evidence'] == zero, refusal_path,
              'existing zero_capture_evidence equals observed files')
    else:
        print(f'SUPPLEMENT: {refusal_path} lacks zero_capture_evidence; '
              'putting the measured file observations in a separate harvested_receipt copy; '
              'raw receipt remains unchanged.', flush=True)
        measured['zero_capture_evidence'] = zero
    sent_path = root / 'night/courier.sent'
    sent_raw = read(sent_path).decode()
    try:
        sent = json.loads(sent_raw)
    except ValueError:
        # BENCH 2026-09-18 (magistrate): the 09-17 courier wrote courier.sent as
        # key=value lines (sent_epoch_s, message_id, thread_id, to, verdict, reason,
        # courier_pid), not JSON. Parse those lines; every check below is unchanged.
        sent = dict(line.split('=', 1) for line in sent_raw.splitlines() if '=' in line)
        print('PARSED: courier.sent as key=value lines: ' + ', '.join(sorted(sent)), flush=True)
    check(isinstance(sent['message_id'], str) and bool(sent['message_id']) and
          sent['message_id'] in record, f'{sent_path}, {record_path}',
          'courier message id present and corroborated by harvest record')
    courier_path = root / 'night/courier.json'
    courier = json.loads(read(courier_path))
    check(courier['sent'] is True, courier_path, 'courier completed delivery')

    count_path = Path(os.environ['SUCCESSOR_COUNT_EVIDENCE'])
    count = json.loads(read(count_path))
    check(count['plan_id'] == ident and type(count['successors_used']) is int
          and count['successors_used'] == 0, count_path,
          'magistrate-observed predecessor successor count is explicitly integer zero')
    count_source = Path(count['evidence_path'])
    count_text = read(count_source).decode()
    check(ident in count_text and len(count_text.strip()) > len(ident)
          and '__' not in count_text, count_source,
          'underlying count review is present, names predecessor, and has no placeholders')
    delivery = {'plan_id': old_plan['plan_id'], 'courier.sent': courier['sent'],
                'message_id': sent['message_id'], 'successors_used': count['successors_used'],
                'plan_sha256': hashlib.sha256(old_plan_raw).hexdigest()}
    evidence = dict(predecessor_result=result, harvested_receipt=harvested,
                    delivery=delivery, source_sha256=sources, observations=observations)
    target = Path(os.environ['ATTEMPT_DIR']) / 'successor-evidence.json'
    check(not os.path.lexists(target), target, 'new evidence destination; no overwrite')
    with target.open('x') as stream:
        json.dump(evidence, stream, indent=2, sort_keys=True); stream.write('\n')
    print(f'WROTE: {target}; predecessor root and receipt unchanged', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f'REFUSED: {exc}; staged plan untouched', flush=True)
        raise SystemExit(3)
