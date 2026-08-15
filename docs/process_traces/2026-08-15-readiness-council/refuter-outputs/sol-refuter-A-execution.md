```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 and F2 survive as one launch-blocking expiry/lifecycle defect; F3 is refuted as a wrong-path artifact.",
  "workspace": {
    "base_requested": "ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b",
    "base_mode": "descendant",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "severity_correct": true,
        "remedy_sound": "partial",
        "summary": "All 33 frozen generic receipts are expired; the inherited arm expiry is already past, so verify and consume cannot succeed."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "severity_correct": true,
        "remedy_sound": "partial",
        "summary": "A generic evidence producer exists, but no operative expiry-refresh lifecycle exists for an already frozen pack."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "REFUTED",
        "severity_correct": false,
        "remedy_sound": "no",
        "summary": "The freeze identity matches at its canonical path; the mismatch occurs only when the canonical-path-bound receipt is evaluated in the audit scratch path."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor ac3fe1d HEAD; echo ancestor_exit=$?; git diff --quiet ac3fe1d -- joulewise configs docs/phase_2/window_runbook.md scripts tests; echo audited_paths_diff_exit=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ancestor_exit=0", "audited_paths_diff_exit=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ancestor_exit=0.*audited_paths_diff_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json,time; from pathlib import Path; import joulewise.arm_readiness as a; now=time.monotonic_ns(); total=expired=other=passed=0; print(\"probe_now_monotonic_ns\",now); exec(\"for root in sorted(Path(\\\"configs/campaigns\\\").glob(\\\"d117_*_v1\\\")):\\n fr=json.loads((root/\\\"arm_readiness.freeze.receipts/freeze-0001.json\\\").read_text()); counts={}; vals=[]\\n for item in fr[\\\"evidence\\\"]:\\n  if item[\\\"schema_version\\\"]!=a.EVIDENCE_RECEIPT_SCHEMA: continue\\n  total+=1; raw=json.loads((root/item[\\\"path\\\"]).read_text()); vals.append(raw[\\\"valid_until_monotonic_ns\\\"])\\n  try: a._authenticate_generic_evidence_item(item,root,root,expected_boot_session_id=raw[\\\"boot_session_id\\\"],now_monotonic_ns=now); passed+=1\\n  except a.ArmReadinessError as e: expired+=e.reason_code==\\\"readiness_record_expired\\\"; other+=e.reason_code!=\\\"readiness_record_expired\\\"\\n print(root.name,len(vals),min(vals))\"); print(\"totals\",json.dumps({\"total\":total,\"record_expired\":expired,\"other_refusal\":other,\"pass\":passed},sort_keys=True))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["totals {\"other_refusal\": 0, \"pass\": 0, \"record_expired\": 33, \"total\": 33}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"record_expired\": 33.*\"total\": 33"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_arm_readiness.py arm --pack-root /Users/edr/JouleWise-measurement-20260813/configs/campaigns/d117_floor_qwen25_1p5b_v1 --arm-context '{\"bracket_session_id\":\"refuter-session\",\"pre_attempt_id\":\"refuter-pre\",\"post_attempt_id\":\"refuter-post\",\"clock_route\":\"MANUAL\",\"claim_runs_root\":\"/tmp/jw-refuter/runs_d117_floor_qwen25_1p5b_v1\",\"bound_runs_root\":\"/tmp/jw-refuter/runs_d117_floor_qwen25_1p5b_v1_bound\",\"custody_root\":\"/tmp/jw-refuter/window\",\"quarantine_root\":\"/tmp/jw-refuter/quarantine\",\"claim_backup_destination\":\"/tmp/jw-refuter/backup-claim\",\"bound_backup_destination\":\"/tmp/jw-refuter/backup-bound\",\"waiver_path\":\"/tmp/jw-refuter/waivers.json\"}' --window-custody-root /tmp/jw-refuter/readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": ["\"reason_codes\": [", "\"readiness_io_error\"", "\"status\": \"REFUSE\""]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "readiness_io_error"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path; import joulewise.arm_readiness as a; root=Path(\"/Users/edr/JouleWise-measurement-20260813/configs/campaigns/d117_floor_qwen25_1p5b_v1\").resolve(strict=True); tree=json.loads((root/\"plan_tree.json\").read_text()); fr=json.loads((root/\"arm_readiness.freeze.receipts/freeze-0001.json\").read_text()); print(\"identity_equal\",fr[\"pack_identity\"]==a._pack_identity(root,tree)); print(\"committed_pack_sha256\",a.committed_pack_tree_sha256(root))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["identity_equal True", "committed_pack_sha256 6246b61858820da7f9349459cce194bf994edd70b24fc0ab44509d6d821523f1"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "identity_equal True"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 12 tests in 0.008s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox denied both kern.bootsessionuuid and creation under $TMPDIR.",
      "needs": "Lead may replay V3 outside the sandbox; no repository or custody bytes were written."
    },
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical measurement checkout remains at 49dcc49 with pack digest 6246b618…, while the audited ac3fe1d pack digest is f4c02c8a…; therefore exact-baseline canonical end-to-end ARM was not executable read-only.",
      "needs": "Before ARM, lead must sync the canonical checkout through the governed reviewed-head procedure and rerun the literal probe."
    }
  ]
}
```

## Findings

### F1 — CONFIRMED (blocker)

The independent receipt probe authenticated all 33 frozen generic evidence bindings while forcing the matching recorded boot ID; every one refused `readiness_record_expired`. At live monotonic `2027632609051666`, the three expiries were `1986799611717708`, `1986908495124625`, and `1986948975714208`—roughly 11.3 hours past.

The implementation authors a fixed 24-hour horizon at [arm_readiness_evidence.py:35](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness_evidence.py:35) and [arm_readiness_evidence.py:1645](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness_evidence.py:1645). ARM then takes the minimum of its five-minute horizon and every evidence expiry at [arm_readiness.py:3710](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness.py:3710). Verification rejects a past result at [arm_readiness.py:3948](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness.py:3948), and consumption calls verification before writing anything at [arm_readiness.py:4025](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness.py:4025).

Severity is correct: safety remains fail-closed, but no verified or consumable GO receipt can exist from these bytes. The proposed re-freeze direction is broadly sound, but same-pack “reissue” is under-specified; the runbook requires changed freeze evidence to receive a new pack ID and new pack/custody roots.

### F2 — CONFIRMED (blocker; same root cause as F1)

Independent script/module inventory found these shipped routes: the generic author, T‑0 author, and freeze/arm generator. Thus “no producer exists” would be false: [author_arm_readiness_evidence.py:43](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/scripts/author_arm_readiness_evidence.py:43) authors generic receipts and prints commit→freeze guidance at [lines 47–56](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/scripts/author_arm_readiness_evidence.py:47).

What survives is the missing lifecycle:

- Existing expired receipts cause `evidence_author_existing_stale`; they are not refreshed idempotently ([arm_readiness_evidence.py:1469](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness_evidence.py:1469)).
- The generator exposes `freeze`, `dry-run`, `arm`, `verify`, and `consume`, but no refresh/successor-freeze operation ([generate_arm_readiness.py:29](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/scripts/generate_arm_readiness.py:29)).
- §4 documents initial freeze, not 24-hour generic-evidence renewal ([window_runbook.md:239](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/docs/phase_2/window_runbook.md:239)).
- §5C’s deletion/re-authoring sequence applies only to T‑0 custody namespaces ([window_runbook.md:802](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/docs/phase_2/window_runbook.md:802)).
- The recovery rule says changed freeze evidence requires a new pack ID and roots ([window_runbook.md:1355](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/docs/phase_2/window_runbook.md:1355)).
- Independent search of the operative arm packet found reboot recovery and T‑0 authoring, but no generic-expiry refresh lane.

Severity is correct for the current window. The remedy must include a successor pack identity/root, regenerated U11 binding as applicable, 11 new generic receipts, new freeze receipt and plan pin, commit/review/dry-run, canonical-checkout synchronization, and audit-baseline re-pin. A durable follow-up should either provide this lifecycle mechanically or redesign which stable freeze evidence genuinely needs a 24-hour horizon.

### F3 — REFUTED

The scratch-path invocation reproduced `readiness_freeze_receipt_mismatch`, but the same command against the receipt’s canonical path advanced past identity checking and failed only at sandboxed `kern.bootsessionuuid` lookup with `readiness_io_error`. Direct comparison returned `identity_equal True`. This ordering is decisive: freeze identity is compared at [arm_readiness.py:2804](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness.py:2804), before the boot lookup at [arm_readiness.py:2820](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/joulewise/arm_readiness.py:2820).

The “unfrozen draft/not armable” subclaim is also obsolete. The runbook explicitly makes the committed freeze receipt authoritative over legacy text at [window_runbook.md:273](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/docs/phase_2/window_runbook.md:273), implementing the M‑2 ruling at [decision_log.md:8881](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree/docs/decision_log.md:8881).

The blocker severity and proposed re-freeze remedy are therefore incorrect for F3. The canonical checkout still needs governed synchronization to the audited head, but that is deployment state—not stale freeze identity—and F1/F2 will still block afterward.

Synthesis: F1 and F2 survive and collapse to one expiry/lifecycle defect; F3 dies. The minimal true work-order set is: (1) an immediate successor-pack refreeze/review/rebaseline operation close enough to ARM for the 24-hour receipts, including canonical-checkout synchronization; and (2) a durable, tested pre-arm expiry preflight plus documented successor-pack refresh lifecycle—or an explicit contract change removing inappropriate 24-hour expiry from stable freeze evidence. No F3-specific re-freeze work order is warranted.

## Residual risk

The sandbox prevented exact live boot-UUID comparison and all `$TMPDIR` writes, so it could not create and verify a complete external arm receipt. The direct same-boot authentication probe nevertheless exercised the shipped receipt validator over all 33 bytes and confirmed the monotonic-expiry path. The canonical checkout is also still at `49dcc49`, with one differing pack file and digest `6246b618…`, rather than audited `ac3fe1d`/`f4c02c8a…`; a lead-controlled sync and unsandboxed literal replay remain necessary before any physical ARM. The focused pure schema suite passed 12/12; the full suite was not run because its temporary-file tests are incompatible with this read-only environment.