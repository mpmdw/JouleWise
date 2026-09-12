```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HOLD: the bytes omit the packet-required 3cece3b2 corpus sub-digest, and the described execute operation does not actually update or commit the required current-head pin.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "71bf5ceec25c16982a33f398b4a4b9f21d549662",
    "head_end": "71bf5ceec25c16982a33f398b4a4b9f21d549662",
    "upstream_end": "71bf5ceec25c16982a33f398b4a4b9f21d549662",
    "branch": "impl/issuance-consumer"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "HOLD",
    "artifact_file_sha256": "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
    "whole_artifact_derivation_sha256": "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02",
    "reproduced_cutoff": {
      "sequence": 76,
      "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
    },
    "inventory": {
      "observations": 38,
      "unique_content_ids": 38,
      "unique_attempt_ids": 38,
      "epoch": "d079_epoch",
      "valid": 30,
      "systematic_invalid": 2,
      "ordinary_invalid": 6,
      "rows_match_ruled_table": true
    },
    "clause_conformance": {
      "D-109 R1.4": "HOLD: cutoff and consumer authentication logic conform, but the packet incorrectly says --execute commits the head pin; the CLI only prints candidate head-pin content.",
      "D-109 R2.1": "PASS: both cutoff fields contain the exact 76/08456d50 pair reproduced from the authenticated import.",
      "D-109 R2.2": "PASS for the binding decision: derivation_corpus is exactly the unchanged n=19 table. FAIL for the packet's additional 3cece3b2 sub-field requirement.",
      "D-109 R2.3": "PASS: all 38 content-distinct observations carry separate attempt_id, epoch_id and disposition; counts are 30/2/6.",
      "D-109 R2.4": "PASS: all content IDs recompute solely from canonical manifest.json and instrument_evidence.json byte hashes; no prior-set row contains a path.",
      "D-109 R2.5": "PASS: the exact prior set is cutoff-bound and import-marked observations are excluded from later new-observation discovery.",
      "D-109 R2.6": "PASS: no unresolved, pending, abandoned or unclassifiable observation appears.",
      "D-109 R2.7": "PASS: raw-physics verification supports systematic-invalid for 491995f3 and c76f5d1c.",
      "D-109 R2.8": "PASS: 30 valid same-epoch observations are below 38; eight additional valid observations are required, and issuance does not trigger re-derivation.",
      "artifact_role_and_claim_eligible": "PASS in the bytes: role/status/claim_eligible are issued/issued/true. Effective claim eligibility remains correctly conditional on ledger, cutoff and committed-pin authentication.",
      "D-110(a)": "PASS: the D-109 implementation merge is an ancestor of the reviewed branch.",
      "D-110(b)": "FAIL/HOLD: issuance is incomplete until conforming artifact bytes, ledger and the separately updated repository-committed head pin all land.",
      "D-110(c)": "PASS: PR #105's evidence_root_id validator widening is an ancestor of the reviewed branch.",
      "D-113": "PASS semantically: neither Window-B calibration endpoint is in the n=19 derivation or replacement claim basis. Both remain only in prior-history inventory as R2.3 requires."
    },
    "systematic_screen": {
      "screen_s": "0.033558756679900",
      "491995f3_bound_s": "0.035435840879704805",
      "491995f3_excess_s": "0.001877084199804805",
      "c76f5d1c_bound_s": "0.0350400833260715",
      "c76f5d1c_excess_s": "0.0014813266461715"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The required 3cece3b2 corpus sub-digest is absent and mischaracterized",
        "detail": "The exact file contains zero occurrences of 3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d and derivation_corpus has no digest field. Its canonical subobject digest is 9a19b81d94880cd34d8321ce75d06a9222888cd574b00943bdb3d36a38d64e55. The 3cece3b2 value was the unissued artifact's old whole-core digest, not a corpus sub-digest. D-109 R2.2 requires the n=19 membership, which is preserved, but the packet's explicit additional requirement is not satisfied."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The execute operation does not perform the claimed head-pin update or commit",
        "detail": "scripts/calibration_ledger_bootstrap.py explicitly states that --execute writes the ledger while the head pin is never written. It prints head_pin_content for a separate lead-controlled update. Without that explicit update and Git commit after ledger advancement, the physical head differs from the committed genesis pin, D-109 R1.4 refuses consumption, and D-110(b) remains incomplete."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 /private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/d079-issued-artifact.REVIEW.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985  /private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/d079-issued-artifact.REVIEW.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr --prepare-issued-artifact",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/issuance",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "executed=false; final_sequence=76; head_digest=08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7; issued_artifact_file_sha256=316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985; issued_artifact_derivation_sha256=4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "final_sequence.?76.*08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7.*316113960c.*4f6633d5"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'recompute file, whole-core and derivation_corpus canonical SHA-256 values; count literal 3cece3b2 occurrences'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "file_sha256=316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
          "whole_core_sha256=4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02",
          "corpus_canonical_sha256=9a19b81d94880cd34d8321ce75d06a9222888cd574b00943bdb3d36a38d64e55",
          "stored_3ce_count=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "stored_3ce_count=0"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger.CalibrationLedgerTests.test_d079_issued_artifact_mode_is_deterministic_and_write_explicit tests.test_calibration_bracketing.CalibrationBracketingTests.test_production_path_authenticates_real_76_receipt_import_prefix",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/issuance",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2 tests in 0.002s",
          "FAILED (errors=2)",
          "FileNotFoundError: No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The packet requires a 3cece3b2 corpus sub-digest, but that value is historically a whole-core digest and no such field exists.",
      "needs": "Correct or withdraw the requirement, or define a reviewed new digest field and hash domain; changed bytes require a new whole-core digest, byte pin, and cold review."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox prevented focused tests from creating temporary directories.",
      "needs": "No action for this verdict; the exact dry-run and pure inspections completed. Rerun focused tests in a writable environment before execution if fresh test evidence is required."
    }
  ]
}
```

## Findings

F1 — blocker. The reviewed bytes do not contain the packet-required `3cece3b2…` sub-digest. More importantly, that value was never a digest of `derivation_corpus`; it was the old unissued artifact’s whole-core digest. The n=19 corpus itself is preserved exactly, but check 6 is false as written. This needs a lead ruling, not a blind insertion.

F2 — blocker. The bootstrap command does not update or commit `configs/calibration/calibration_ledger_head.json`; it only prints the proposed pin. The execution procedure must explicitly apply and Git-commit the exact `76/08456d50…` pin before D-116 or any claim evaluation.

All remaining requested checks pass: exact cutoff, 38-row 30/2/6 inventory, path-independent identities, systematic-screen comparisons, 30-valid counting, whole-core `4f6633d5…` digest, issued-role semantics, D-110(a)/(c), and D-113 exclusion from the derivation/claim basis.

## Residual risk

The two focused tests could not allocate temporary directories under the read-only sandbox. No files were modified, and the deterministic read-only emission reproduced the reviewed bytes exactly.