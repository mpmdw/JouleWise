```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Read-only execution checks pass; filesystem-backed audit is blocked by unavailable writable temporary storage.",
  "workspace": {
    "base_requested": "0a7c5858",
    "base_mode": "descendant",
    "head_start": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "head_end": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 48 tests in 0.593s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_rehearse_t0_unattended",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 5 tests in 0.004s", "", "FAILED (errors=5)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import ast,os,re,subprocess as s\nfrom pathlib import Path as P\nfrom unittest.mock import patch\nfrom joulewise import arm_readiness as a\nfrom scripts import rehearse_t0_unattended as l\ndef part(t,k):\n return next(ast.get_source_segment(t,n) for n in ast.parse(t).body if getattr(n,'name',None)==k or isinstance(n,ast.Assign) and any(getattr(x,'id',None)==k for x in n.targets))\nfor p,ks in [('joulewise/night_gate.py',['_RECEIPT_KEYS','validate_receipt']),('scripts/run_night.py',['_claim_chain_start','_complete_chain_start','_complete_chain_launch_failure'])]:\n old=s.check_output(['git','show','0a7c5858:'+p],stderr=s.DEVNULL).decode()\n for k in ks: assert part(old,k)==part(P(p).read_text(),k)\ntree=ast.parse(part(P('scripts/run_night.py').read_text(),'_produce_pack_go'))\nd=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(getattr(x,'id',None)=='go' for x in n.targets))\nkeys=[k.value for k in d.keys]\nt=P('docs/contracts/pack_night_go_receipt.md').read_text().split('| Key | Type | Bound-to | Checked-where |')[1].split('Nested key lists')[0]\nexpected=[line.split(chr(96))[1] for line in t.splitlines() if line.startswith('| '+chr(96))]\nassert len(keys)==len(expected)==26 and set(keys)==set(expected)\ninv=[dict(deployment_id='synthetic',measurement_root='/synthetic/production',custody_root=None,ledger_path=None,notes='fixture')]\nhome=P('/synthetic/home')\nroots=a.production_custody_roots(home=home,inventory=inv)\nassert len(roots)==6\nfor v in ['','/override/only']:\n with patch.dict(os.environ,JOULEWISE_BACKUP_ROOTS=v): assert a.production_custody_roots(home=home,inventory=inv)==roots\nrows=[dict(role=r.role,path=str(r.path)) for r in roots]\nfor items in [rows[:-1],[dict(r,path='/wrong') if r['role']=='backup_icloud' else r for r in rows]]:\n raw=a.render_json(dict(schema_version=l.MANIFEST_SCHEMA,t0_namespace='tests',records={n:'tests/'+n+'.json' for n in l.RECORD_NAMES},production_roots=items))\n with patch.object(l,'_regular_bytes',return_value=raw):\n  try: l.load_evidence_bundle(P.cwd(),home=home,inventory=inv)\n  except l.BundleLoadError as e: assert str(e)=='production-root census incomplete'\n  else: raise AssertionError('G6 accepted mismatch')\nprint('GO_KEYS '+','.join(keys))\nprint('PASS: byte identity; 26 keys; census overrides; G6 mismatches')\n\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "GO_KEYS schema_version,receipt_id,receipt_class,purpose,plan_id,plan_sha256,pack_id,pack_sha256,arm_receipt,boot_session_id,t0_evidence,t0_evidence_set_sha256,launch_manifest_sha256,window_environment_sha256,window_chain_sha256,repo_head,measurement_root,measurement_head,confirmation_record,authorization,census,issued_epoch_s,issued_monotonic_ns,valid_until_monotonic_ns,conditions,verdict",
          "PASS: byte identity; 26 keys; census overrides; G6 mismatches"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^PASS: byte identity; 26 keys; census overrides; G6 mismatches$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "V2 fails during TemporaryDirectory setup: no usable temporary directory exists under the enforced read-only sandbox. Root-placement cases and driver checks 3(a)-(g) were not executed. Marker byte identity was checked, but atomic filesystem behavior was not exercised. No clean verdict is established.",
      "needs": "Resume at the same head with writable disposable fixture storage while keeping repository paths read-only; execute the remaining root and driver cases."
    }
  ]
}
```

## Residual risk

No new defect was established within completed coverage. G6’s omitted-role and changed-path refusals were executed using injected manifest bytes and real existing directories. The census used synthetic, nonexistent production paths, confirming that missing roots remain counted.

The 26 keys are enumerated in V3. `_RECEIPT_KEYS`, `validate_receipt`, and the three marker functions are byte-identical to the base. Remaining filesystem and driver behavior requires the blocked fixture execution; source inspection does not establish those outcomes.