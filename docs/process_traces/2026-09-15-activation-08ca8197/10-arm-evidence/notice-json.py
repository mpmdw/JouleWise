#!/usr/bin/env python3
"""Write notice.json + notice-evidence.txt for the attempt from the ACTUAL Gmail acceptance. Usage: notice-json.py MESSAGE_ID THREAD_ID SENT_EPOCH_S [note]"""
import hashlib, json, os, sys, time
from pathlib import Path
msg, thr, sent = sys.argv[1], sys.argv[2], float(sys.argv[3])
note = sys.argv[4] if len(sys.argv) > 4 else ''
attempt_dir = Path(os.environ['ATTEMPT_DIR']); staged = Path(os.environ['STAGED_PLAN'])
raw = staged.read_bytes(); plan = json.loads(raw)
assert (attempt_dir / 'plan.json').read_bytes() == raw
digest = hashlib.sha256(raw).hexdigest()
notice = {
  'accepted': True, 'message_id': msg, 'thread_id': thr, 'sent_epoch_s': sent,
  'attempt': int(os.environ['ARM_ATTEMPT']), 'plan_id': plan['plan_id'],
  'receipt_class': plan['receipt_class'], 'measurement_head': plan['measurement_head'],
  'plan_sha256': digest,
  'prerequisites_clear': True, 'veto_clear': True, 'blocking_causes': [],
  'latest_no_epoch_s': None, 'latest_abort_epoch_s': None,
}
(attempt_dir / 'notice.json').write_text(json.dumps(notice, indent=2) + '\n')
(attempt_dir / 'notice-evidence.txt').write_text(
  f"Gmail send accepted at {sent} ({time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(sent))}); message_id={msg} thread_id={thr}; "
  f"plan_sha256={digest}; H={plan['measurement_head']}; attempt={notice['attempt']}; class={plan['receipt_class']}. "
  f"NO relay: this activation reads the thread via the Gmail MCP before publication; a reply after exit is read by the next activation. {note}\n")
print(json.dumps(notice, indent=2))
