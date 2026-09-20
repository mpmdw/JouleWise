#!/usr/bin/env python3
"""Assertion-only bench checks. Never install, probe, publish or run a chain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

sys.path.insert(0, os.environ['MEASUREMENT_ROOT'])
from joulewise import night_gate
from joulewise.night_agent_install import Refused
from joulewise.quiet_predicate_campaign import CHAIN_PATH, PROTOCOL_PATH, manifest_for, tracked_bytes, verify_manifest
from scripts.run_night import install_close_epoch, schedule


def check(ok, message):
    print(('PASS: ' if ok else 'REFUSED: ') + message, flush=True)
    if not ok:
        raise ValueError(message)


def candidate(path, publication_safe=False):
    e=os.environ
    raw=Path(path).read_bytes(); value=json.loads(raw)
    p=night_gate.NightPlan.from_mapping(value)
    check(value['schema']=='joulewise.night_plan.v2' and value['schema_version']==2,
          'v2 plan, no v4 schema')
    check('quiet_admission' not in value and p.quiet_admission is None, 'no quiet_admission')
    check('pack_night' not in value and p.pack_night is None, 'no pack fields')
    check(p.repo_head==p.measurement_head==e['H'], 'plan heads equal H')
    check(p.plan_id==e['PLAN_ID'] and p.measurement_root==e['MEASUREMENT_ROOT'] and
          p.custody_root==e['NIGHT_ROOT'], 'plan id and roots equal environment')
    check(p.t0_epoch_s==int(e['T0_EPOCH_S']), 't0 equals selected epoch')
    check(p.receipt_class=='DIAGNOSTIC_NO_PACK' and p.window_max_s==9000,
          'DIAGNOSTIC_NO_PACK, frozen 9000 s window')
    check(p.registration_path==PROTOCOL_PATH==night_gate.QPE01_PILOT_REGISTRATION_PATH,
          'repo-relative pilot registration')
    check(p.chain_path==e['NIGHT_ROOT']+'/chain.zsh' and
          p.chain_sha256_path==p.chain_path+'.sha256', 'wrapper paths match custody root')
    wrapper=Path(p.chain_path).read_text()
    check(night_gate.probe_payload_kind(wrapper)=='quiet_predicate_evidence', 'single evidence payload literal')
    sha=hashlib.sha256(Path(p.chain_path).read_bytes()).hexdigest()
    check(Path(p.chain_sha256_path).read_text().split()==[sha,'chain.zsh'], 'wrapper SHA-256 equals sidecar')
    manifest_path, manifest, manifest_sha=verify_manifest(p,wrapper)
    check(manifest_path==Path(e['NIGHT_ROOT'])/'evidence_manifest.json' and manifest==manifest_for(p),
          'sealed manifest equals manifest_for(plan)')
    source_sha=hashlib.sha256(tracked_bytes(p.measurement_root,e['H'],CHAIN_PATH)).hexdigest()
    check(night_gate.chain_literal(wrapper,'EVIDENCE_CHAIN_SOURCE_SHA256')==source_sha,
          'wrapper source SHA-256 equals tracked chain at H')
    reg_sha=hashlib.sha256((Path(p.measurement_root)/PROTOCOL_PATH).read_bytes()).hexdigest()
    check(reg_sha in night_gate.RULED_REGISTRATIONS and night_gate.RULED_REGISTRATIONS[reg_sha]['binds_chain'],
          'registration SHA-256 belongs to chain-bound RULED_REGISTRATIONS')
    check(json.loads((Path(p.measurement_root)/PROTOCOL_PATH).read_text())['chain_source_sha256']==source_sha,
          'registration binds source SHA-256')
    check(0<=time.time()-p.authored_epoch_s<=night_gate.PLAN_MAX_AGE_S and
          2400<=p.t0_epoch_s-p.authored_epoch_s<=night_gate.PLAN_MAX_AGE_S,
          'plan age valid; t0 at least 40 min after authoring')
    check(time.time()<install_close_epoch(p), 'before exclusive install close')
    check(Path(e['STAGE']).stat().st_dev==Path(e['NIGHT_ROOT']).stat().st_dev, 'same-device atomic publication')
    s=schedule(p)
    check(s['install_close_epoch_s']==int(e['INSTALL_CLOSE_EPOCH_S']) and
          s['deadman_epoch_s']==int(e['DEADMAN_EPOCH_S']), 'derived boundaries equal driver schedule')
    if publication_safe:
        check(night_gate.chain_literal(wrapper,'EVIDENCE_PLAN_PATH')==e['PLAN'],
              'publication-safe EVIDENCE_PLAN_PATH equals published PLAN (NEEDS_RULING at pinned H)')
    print('candidate checks PASS')
    return p


def receipt(path):
    from joulewise.night_agent_install import validate_evidence_probe_receipt, probe_label
    p=night_gate.NightPlan.from_mapping(json.loads(Path(path).read_text()))
    prepared=SimpleNamespace(plan=p,plan_path=Path(path),python=os.environ['PY'])
    r=validate_evidence_probe_receipt(prepared)
    check(r['schema']=='joulewise.night_evidence_probe_receipt.v1', 'evidence receipt schema')
    check(r['verify_only'] is True and r['collect_started'] is False and r['load_started'] is False,
          'verify-only; collect and load never started')
    check(r['launchd_label']==probe_label(p.plan_id) and r['cleanup_proven'] is True,
          'correct probe label and cleanup proven')
    print('PROBE ADMITS: bindings and freshness validated (< 6 h)')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['candidate','receipt'])
    parser.add_argument('--plan',required=True)
    parser.add_argument('--publication-safe',action='store_true')
    args=parser.parse_args()
    try:
        if args.mode=='candidate':
            candidate(args.plan,args.publication_safe)
        else:
            receipt(args.plan)
    except Refused as exc:
        print('REFUSED: '+str(exc),file=sys.stderr)
        raise SystemExit(exc.code)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('REFUSED: '+str(exc),file=sys.stderr)
        raise SystemExit(3)
