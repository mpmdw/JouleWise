import hashlib, json, re, subprocess
from collections import Counter
from pathlib import Path
from joulewise import battery_float
from joulewise.calibration_ledger import load_calibration_ledger_snapshot, terminal_head_pin_for_session

root = Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1')
sid = 'd079-epoch-25g83-derivation-w1-20260927'
ledger = root / 'runs/calibration_observation_ledger.jsonl'
pin_path = root / 'configs/calibration/calibration_ledger_head.json'
verdict_path = root / f'configs/calibration/battery_float_verdicts/{sid}.json'
prereg = root / 'configs/calibration/preregistration_d079_epoch_25g83_rev1.md'
raw_ledger = ledger.read_bytes()
rows = [json.loads(line) for line in raw_ledger.splitlines()]
assert len(rows) == 226
for i, row in enumerate(rows):
    assert row['sequence'] == i + 1
    assert row['predecessor_digest'] == (rows[i-1]['receipt_digest'] if i else '0'*64)
    core = {k:v for k,v in row.items() if k != 'receipt_digest'}
    digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    assert row['receipt_digest'] == digest, (i+1, digest)
old = rows[175]
tail = rows[176:]
open_rows = [r for r in tail if r['event'] == 'bracket-session-open']
assert len(open_rows) == 1 and open_rows[0]['session_id'] == sid
session_rows = [r for r in tail if r.get('session_id') == sid]
control_rows = [r for r in tail if r.get('schema_version') == 'joulewise.calibration_ledger_control.v1']
assert len(tail) == len(session_rows) + len(control_rows)
assert all(r.get('target_core',{}).get('session_id') == sid for r in control_rows)
finals = [r for r in session_rows if r['event'] == 'bracket-session-slot-finalization']
assert [r['slot'] for r in finals] == [f'd{i:02d}' for i in range(1,13)]
assert finals[-1] is rows[-1]
manual_pin = {'sequence': rows[-1]['sequence'], 'head_digest': rows[-1]['receipt_digest'], 'ledger_schema': rows[-1]['ledger_schema']}
tool_pin = terminal_head_pin_for_session(ledger, session_id=sid)
assert manual_pin == tool_pin
expected_pin_bytes = (json.dumps(tool_pin, indent=2) + '\n').encode()
assert pin_path.read_bytes() == expected_pin_bytes
print('LEDGER_SHA256', hashlib.sha256(raw_ledger).hexdigest())
print('OLD_HEAD', old['sequence'], old['receipt_digest'])
print('TAIL', len(tail), 'session_rows', len(session_rows), 'control_rows', len(control_rows), 'other_rows', len(tail)-len(session_rows)-len(control_rows))
print('TAIL_EVENTS', dict(Counter(r['event'] for r in tail)))
print('FINALIZED', len(finals), 'declared', len(open_rows[0]['declared_slots']), 'last_slot', finals[-1]['slot'])
print('MANUAL_PIN', manual_pin)
print('TOOL_PIN', tool_pin, 'EXACT_FILE_BYTES', True)

snapshot = load_calibration_ledger_snapshot(ledger, pin_path, require_committed_pin=True, verify_custody=False, mode='read_replay', repo_root=root)
assert not snapshot.refusal_reasons, snapshot.refusal_reasons
session = snapshot.bracket_session_by_id[sid]
assert session.state == 'finalized' and len(session.finalized_slots) == 12 and len(session.declared_slots) == 12
window = battery_float.validate_window(session)
record = json.loads(verdict_path.read_bytes())
assert window['status'] == record['status'] == 'pass'
assert window['slots'] == record['slots']
parent = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD^'], text=True).strip()
module_sha = hashlib.sha256((root/'joulewise/battery_float.py').read_bytes()).hexdigest()
prereg_sha = hashlib.sha256(prereg.read_bytes()).hexdigest()
recreated = battery_float.verdict_record(session, snapshot=snapshot, preregistration_sha256=prereg_sha, tool_commit=parent, module_sha256=module_sha, wall_time_s=record['computed_wall_time_s'])
assert recreated == record
assert battery_float.render_verdict(recreated) == verdict_path.read_bytes()
print('SNAPSHOT', 'valid', snapshot.valid, 'state', session.state, 'declared', len(session.declared_slots), 'filled', len(session.finalized_slots))
print('WINDOW', window['status'], 'slot_fields_equal', window['slots'] == record['slots'])
print('VERDICT', 'all_fields_equal', recreated == record, 'exact_file_bytes', True, 'prereg_sha', prereg_sha, 'module_sha', module_sha, 'tool_commit', parent)
print('SLOT PHASE EXT CHG INSTANT_mA AGE_s EXIT TIMEOUT STORED_PASS RAW_SHA_OK EVIDENCE_SHA_OK')
for slot, obs in session.finalized_slots.items():
    custody = Path(obs.custody_locator)
    eraw = (custody/'instrument_evidence.json').read_bytes()
    esha_ok = hashlib.sha256(eraw).hexdigest() == obs.artifact_sha256['instrument_evidence.json']
    assert esha_ok
    evidence = json.loads(eraw)['battery_float']
    for phase in ('pre','post'):
        stored = evidence[phase]
        raw = (custody / f'raw/battery_float.{phase}.ioreg').read_bytes()
        rsha_ok = hashlib.sha256(raw).hexdigest() == stored['raw_stdout_sha256']
        assert rsha_ok
        values = {}
        for key in ('ExternalConnected', 'IsCharging', 'InstantAmperage', 'UpdateTime'):
            matches = re.findall(rb'^      "' + key.encode() + rb'" = ([0-9]+|Yes|No)$', raw, re.M)
            assert len(matches) == 1, (slot, phase, key, matches)
            values[key] = matches[0].decode()
        current = int(values['InstantAmperage'])
        if current >= 2**63: current -= 2**64
        age = stored['wall_time_s'] - int(values['UpdateTime'])
        parsed = battery_float.parse(raw, stored['wall_time_s'])
        assert stored['exit_code'] == 0 and stored['timed_out'] is False
        assert values['ExternalConnected'] == 'Yes' and values['IsCharging'] == 'No' and abs(current) <= 200 and age <= 180
        assert parsed['passed'] and stored['passed'] and not stored['probe_error']
        assert parsed['instant_amperage_ma'] == current and parsed['update_age_s'] == age
        print(slot, phase, values['ExternalConnected'], values['IsCharging'], current, f'{age:.3f}', stored['exit_code'], stored['timed_out'], stored['passed'], rsha_ok, esha_ok)
auth = battery_float.authenticate_committed_verdict(root, session=session, preregistration_sha256=prereg_sha)
print('AUTHENTICATE', auth.status, auth.commit, len(auth.slots), auth.file_sha256)
