```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Items 4 and 5 match the binding interface by inspection and execution; F1, F2 and F3 remain unchanged.",
  "workspace": {
    "base_requested": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "base_mode": "exact",
    "head_start": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "head_end": "376dd35f859c69bcd17f2f8c06c6d397e67817a6",
    "upstream_end": "68fa9a9cf89c88e64588f8d3d7eee7508158b45e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/validate_powermetrics_fiducial.py:1634",
        "title": "Ordinary abandonment appends after its custody deadline expires",
        "authority": "docs/process_traces/2026-09-16-interactive-5239df1e/02-reserve-hang-design-consult.md:30",
        "clause": "Recheck expiry before accepting success and immediately before entering the append path.",
        "counterexample": "Previously executed in /tmp/refute-contract-376dd35f: TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_contract_probe.AppendDeadlineContract",
        "input": "Real pending ordinary attempt; real bounded hashing succeeds; a scheduling pause then expires the 0.5-second deadline.",
        "observed": "abandon: deadline_expired=true, refusal=null, ledger_changed=true, appended_events=[append-intent, finalization]. Normal finalize control refused with calibration_ledger_custody_timeout and appended nothing. Two tests, one failure.",
        "cause": "abandon supplies the deadline to hashing but omits it from finalize_attempt_receipt.",
        "recommendation": "Pass the same deadline into finalize_attempt_receipt and check expiry before appending.",
        "disposition": "Carried forward unchanged; not re-derived."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/calibration_ledger.py:5260",
        "title": "Bounded issuing shortcut drops the pinned stderr diagnostic",
        "authority": "docs/contracts/calibration_ledger_append.md:569",
        "clause": "emits exactly one stderr line per probe: `custody_backup_roots_disabled: <path>`",
        "counterexample": "Previously executed in /tmp/refute-contract-376dd35f: TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_shortcut_contract_probe",
        "input": "_custody_state on a lexical backup-root descendant with JOULEWISE_BACKUP_ROOTS='' and a CustodyDeadline; worker invocation forbidden.",
        "observed": "result=absent; stderr=''. One test failed. Analogous new branches at lines 292 and 2125 also omit the diagnostic.",
        "recommendation": "Emit the existing issuing diagnostic once without filesystem access.",
        "disposition": "Carried forward unchanged; not re-derived."
      },
      {
        "id": "F3",
        "severity": "nit",
        "file": "docs/contracts/calibration_ledger_append.md:61",
        "title": "The subsection lacks two first-use glosses",
        "authority": "Seat-A brief, stage 7; review lens item 9",
        "clause": "Gloss every term of art at first use.",
        "command": "nl -ba docs/contracts/calibration_ledger_append.md | sed -n '54,77p'",
        "observed": "Line 61 introduces 'reaps' without explaining collection of process exit status; line 74 introduces '.PID.json' without expanding PID.",
        "recommendation": "Gloss reaping and process ID.",
        "disposition": "Carried forward unchanged; not re-derived."
      }
    ],
    "interface_authority": "68fa9a9c:docs/process_traces/2026-09-16-activation-9853dd2b/01-brief-seat-A-custody-worker.md, Interface contract shared with seat B, lines 24-29",
    "trace": [
      "1: Previously traced: one absolute monotonic deadline covers worker startup, selector IPC, metadata, reads and hashing, clipped by --custody-deadline-epoch-s. Observations do not restart it. Finalization/abandonment starts a separate operation. Append exception remains F1.",
      "2: Previously traced: reservation readiness at reserve_calibration_window_bracket.py:276 and existing-session fallback at :294 receive the same deadline. Checks at :323 and calibration_ledger.py:4681 precede append. Traced, no finding on these reservation paths.",
      "2 continued: Writer preflight snapshot :2005, under-lease snapshot :1517, pre-slot readiness :1561 and slot-validation fallback :1348 receive the preparation deadline. _validate_slot at :1509/:1524 reuses bounded snapshots; :1575 reloads with the deadline via :1553. Slot custody classification forwards it into _custody_state. Hashing at :1640/:1672 is bounded; abandonment's subsequent append remains F1.",
      "3: Previously traced, no finding: worker imports authentication readers, not ledger/lease/append modules; opens are reads; close_fds=True; request contains frozen data, no writer capability; caller process group retained; no descendants created.",
      "4: Traced, no finding against brief lines 26-28. calibration_exits.py:647-658 has exactly these 14 names: schema, code, exit_code, phase, plan_id, session_id, existing_session, ledger, budget_s, elapsed_s, last_observation, written_epoch_s, pid, detail. schema is exactly joulewise.calibration_refusal.v1. ledger contains path/head_sha256; last_observation contains observation_id/locator/artifact or null. Code comes from RefusalCode; plan_id comes from JOULEWISE_NIGHT_PLAN_ID; detail is flattened to one line.",
      "4 continued: Phase literals match exactly: reservation at reserve_calibration_window_bracket.py:210; writer_preflight at writer :1427/:1850; under_lease at :1513. Both CLIs route registry refusal emissions through emit_calibration_refusal. Lines 664/669 use O_WRONLY|O_CREAT|O_EXCL without truncation; collision path at :666 is exactly <path>.<pid>.json and :667 announces it on stderr. Unset destination skips document creation and retains ordinary stderr emission.",
      "4 execution: One real reservation invocation against an open fixture session, with a stalled artifact read and a pre-existing refusal file. Exit 2; exact 14-key document and nested key sets; reservation phase, plan/session/head binding, numeric fields and progress values checked. PID sibling name and announcement matched; original refusal and ledger/pin bytes remained unchanged; structured stderr refusal present. V1 passed.",
      "5: Traced, no finding against brief line 25. The mutually exclusive flags are at reservation :116-121. verify-only shares enforcing preflight, checks expiry, prints one JSON line and returns 0 at :343 before append at :344. Exactly eight fields match: verify_only, ledger_head_sha256, observations, custody_elapsed_s, custody_budget_s, python, python_version, code_digests. verify_only is exactly ok.",
      "5 continued: The three digest keys match literally: scripts/reserve_calibration_window_bracket.py, joulewise/calibration_ledger.py, joulewise/calibration_custody_worker.py. Values are sha256: followed by each file's actual digest. Interpreter fields use sys.executable and platform.python_version(). One successful real verify-only invocation checked all fields, three observations, all digest bytes, one stdout line, exit 0, unchanged ledger/pin and no refusal document. V1 passed. The seat-A receipt contract requires no additional plan/input fields.",
      "6: Previously traced, no finding: operational, arm-blocking, stop-preserved, exit 2, terminal night_stopped_preserved. Registry/projection/runbook checks passed; exact code and description also match brief line 24.",
      "7: Previously traced, no finding: hash mismatch remains calibration_ledger_custody_invalid, including reservation existing-session rejection.",
      "8: Previously traced, no finding on generic probe_custody caller-thread behavior; synchronous authentication callback preserved. The separate bounded issuing diagnostic regression remains F2.",
      "9: First-use review remains F3.",
      "Existing refusal registry records were previously compared against 3015cb39: none changed; only the timeout code was added. No measurement, instrument, gate or claim constant changed. F2 remains an existing pinned-clause violation."
    ],
    "prior_evidence": "81 existing focused tests passed in the preceding review. F1/F2 counterexamples and F3 inspection were not rerun.",
    "scratch": "/tmp/refute-contract-376dd35f/test_shared_interface_contract.py; only disposable-copy files were written.",
    "authority_gap": "G1 resolved by the lead-provided git-object source."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_shared_interface_contract.SharedInterfaceContract",
      "cwd": "/tmp/refute-contract-376dd35f",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "item4: exact 14 fields; nested keys and values; exit=2; PID sibling; original and ledger/pin preserved; stderr refusal present",
          "item5: exact 8 fields; exact 3 code-digest keys and bytes; one stdout JSON line; exit=0; ledger/pin preserved",
          "Ran 2 tests in 4.296s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git show 68fa9a9c:docs/process_traces/2026-09-16-activation-9853dd2b/01-brief-seat-A-custody-worker.md | nl -ba | sed -n '19,36p'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Binding interface read at lines 24-29."]},
      "expected": {"exit_code": 0, "tail_regex": "Interface contract shared with seat B"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 3015cb39..376dd35f",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The preceding supplementary broad invocation's terminal result remains uncollected: write_stdin now reports Unknown process id 84717. No overall result is attributed to that invocation. The requested two interface executions both completed successfully.",
      "needs": ""
    },
    {
      "id": "G3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Verification used disposable fixtures, not live launchd or hardware. All five relevant production source files in the disposable copy were checked byte-identical to 376dd35f. The reviewed worktree remained clean and unchanged.",
      "needs": ""
    }
  ]
}
```