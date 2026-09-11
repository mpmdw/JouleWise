```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HOLD: the ledger dry-run reproduces the exact 08456d50...@76 head and the 30/2/6 inventory conforms to R2, but the planned issued artifact is incompatible with the landed validator and cannot preserve derivation_sha256 3cece3b2....",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "e6db69aa4547341fd3a667cd98e1c9ff66681bc5",
    "head_end": "e6db69aa4547341fd3a667cd98e1c9ff66681bc5",
    "upstream_end": "e6db69aa4547341fd3a667cd98e1c9ff66681bc5",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "HOLD",
    "reproduced_head": {
      "sequence": 76,
      "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
      "matches_packet": true,
      "executed": false
    },
    "inventory": {
      "content_distinct": 38,
      "unique_attempts": 38,
      "valid": 30,
      "systematic_invalid": 2,
      "ordinary_invalid": 6,
      "unresolved": 0,
      "content_ids_recomputed_from_primary_hashes": true,
      "custody_manifest_set_exact": true
    },
    "corpus_doubling": {
      "threshold_valid_same_epoch": 38,
      "current_valid_same_epoch": 30,
      "additional_valid_required": 8,
      "issuance_triggers_rederivation": false,
      "six_further_applies_only_to_rejected_32_valid_candidate": true
    },
    "derivation": {
      "corpus_n": 19,
      "corpus_preserved": true,
      "current_derivation_sha256": "3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d",
      "can_preserve_digest_across_issuance_under_landed_semantics": false
    },
    "clauses": [
      {
        "clause": "D-109 R1.4",
        "status": "fail",
        "detail": "The proposed sequence/head pair and independent head pin are mechanically correct, but the landed acceptance loader cannot authenticate an issued artifact carrying that baseline."
      },
      {
        "clause": "D-109 R2.1",
        "status": "pass",
        "detail": "The intended cutoff is the exact non-genesis pair 76/08456d50..., not fixture genesis."
      },
      {
        "clause": "D-109 R2.2",
        "status": "pass_corpus_only",
        "detail": "The threshold-producing derivation_corpus remains exactly n=19; the separate demand to retain the old whole-core derivation_sha256 fails."
      },
      {
        "clause": "D-109 R2.3",
        "status": "source_conforms_final_artifact_missing",
        "detail": "The ruled table supplies all 38 distinct observations with separate attempt, epoch and disposition data, but the packet contains no exact final 38-row acceptance JSON to audit."
      },
      {
        "clause": "D-109 R2.4",
        "status": "pass",
        "detail": "Every content_id recomputes from canonical manifest.json and instrument_evidence.json byte hashes; paths and copies do not affect identity."
      },
      {
        "clause": "D-109 R2.5",
        "status": "pass",
        "detail": "Import-marked observations seed the prior set and are excluded from post-cutoff/new populations."
      },
      {
        "clause": "D-109 R2.6",
        "status": "pass",
        "detail": "All 38 are classified; the import table contains no pending, abandoned, unresolved or unclassifiable member."
      },
      {
        "clause": "D-109 R2.7",
        "status": "pass",
        "detail": "Raw-physics/hash verification is complete; the two high-bound members are ruled systematic-invalid, yielding 30/2/6."
      },
      {
        "clause": "D-109 R2.8",
        "status": "pass",
        "detail": "Thirty valid same-epoch observations are below 38; eight more valid observations are required and issuance does not itself trigger re-derivation."
      },
      {
        "clause": "D-110(a)",
        "status": "pass",
        "detail": "CAL-BRACKET-D079-01 is merged and gauntlet-clean."
      },
      {
        "clause": "D-110(b)",
        "status": "fail",
        "detail": "The ledger and head-pin plan is ready, but the acceptance artifact would remain invalid/unloadable; condition (b) would therefore not be fully satisfied."
      },
      {
        "clause": "D-110(c)",
        "status": "pending",
        "detail": "The evidence_root_id validator widening is not on current main; this does not independently bar issuance but continues to bar re-mint."
      }
    ],
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The planned issued artifact has no valid landed loader state",
        "detail": "calibration_bracketing.py byte-pins the current fixture, requires artifact_role=schema_fixture_unissued, unratified_fixture status, claim_eligible=false, cutoff sequence 0/all-zero digest, and production_issuance_blocked=true. Production evaluation then unconditionally refuses the artifact as an unissued fixture. The packet proposes only ledger execution, head-pin update, artifact edit and D-116; it omits the required reviewed loader/schema/pin transition and supplies no exact final artifact bytes."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Preserving derivation_sha256 3cece3b2... is incompatible with its current definition",
        "detail": "The validator defines derivation_sha256 as canonical SHA-256 of the complete artifact core excluding only derivation_sha256. Changing artifact_role alone changes the computed digest from 3cece3b2... to a0b98acf...; changing cutoff, issuance, prior_observation_set and backfill state changes it further. Keeping 3cece3b2... makes the issued artifact invalid even though n=19 remains unchanged."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The packet names the wrong physical ledger target",
        "detail": "The CLI default and all production writers use runs/calibration_observation_ledger.jsonl, while the packet says configs/calibration/calibration_observation_ledger. The exact --execute command would write the former."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The custody-locator count in the packet is inaccurate",
        "detail": "All 38 manifest values point into the iCloud JouleWise-backup tree, not 22. This is not an R1.4/R2 violation: all five governed hashes are reauthenticated, content identities are path-independent, and primary-checkout residency is not required."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"custody_manifest_sha256\":\"99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078\",\"disposition_table_sha256\":\"5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a\",\"executed\":false,\"final_sequence\":76,\"head_digest\":\"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\"outcome\":\"planned\",\"receipt_count\":76,\"record\":\"bootstrap-summary\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"final_sequence\":76.*\"head_digest\":\"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\""
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import hashlib,json; v=json.load(open(\"configs/calibration/calibration_acceptance_d079_v2.json\")); core={k:x for k,x in v.items() if k!=\"derivation_sha256\"}; digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(\",\",\":\"),ensure_ascii=False,allow_nan=False).encode()).hexdigest(); print(digest(core)); core[\"artifact_role\"]=\"issued\"; print(digest(core)); print(digest(core)==v[\"derivation_sha256\"])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d",
          "a0b98acf317cc750fb7b31fcd8630d22bad306839b73d380dc16f7b57a8ef1c5",
          "False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "False"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_import_marker_is_excluded_by_discovery_and_trigger_paths tests.test_calibration_bracketing.CalibrationBracketingTests.test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.002s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "VG1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The irreversible --execute path was intentionally not run; the physical ledger remains absent and the working tree remains clean.",
      "needs": "After F1/F2 are repaired, stage the exact issued artifact and loader/pin delta and repeat cold review before executing the bootstrap."
    }
  ]
}
```

## Findings

Verdict: **HOLD**.

F1 — blocker. The proposed issuance cannot create an artifact accepted by the landed selector. [calibration_bracketing.py](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:155) permits only the genesis unissued-fixture shape; the byte pin is the current fixture hash, and production evaluation explicitly refuses it at line 757. Updating only the JSON and head pin therefore fails D-109 R1.4 and leaves D-110(b) unsatisfied.

F2 — blocker. `derivation_corpus` remains correctly fixed at n=19, but `derivation_sha256` cannot remain `3cece3b2…`. Its implemented domain is the entire artifact core, not just the n=19 derivation table. The existing verification report itself records this at [VERIFICATION-REPORT.md](/Users/edr/code/JouleWise/docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:642). The issued artifact must either recompute this digest under the current definition or undergo an explicit reviewed schema/semantic change.

F3 — should_fix. Correct the packet’s physical-ledger path to `runs/calibration_observation_ledger.jsonl`, the actual default used by the bootstrap and production writer.

F4 — should_fix. The reviewed custody manifest contains 38 iCloud-backup locators. This is acceptable authenticated custody under D-109: all primary bytes are rehashed, and content IDs are path-independent. The copies do not need to be moved into the primary checkout first.

The R2.8 count is unambiguous: **30 current valid, threshold 38, eight additional valid required, no re-derivation triggered by issuance**. “Six further” applied only to the rejected 32-valid candidate classification.

D-110(a) is satisfied; D-110(b) is not satisfied by this packet; D-110(c) remains pending and continues to block re-mint independently.

## Residual risk

After fixing F1/F2, the exact final 38-row acceptance JSON, its new canonical digest, its new checked-in byte pin, and a production-path test over the real 76-receipt prefix require cold review before the irreversible ledger write.