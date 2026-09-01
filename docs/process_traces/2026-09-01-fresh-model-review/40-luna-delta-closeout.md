```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "REFUTE: a forged replay-sidecar object can differ from the authenticated bytes while still licensing Branch A.",
  "workspace": {
    "base_requested": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "base_mode": "exact",
    "head_start": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "head_end": "88e96f60f253f60c665e223780ce651594913b29",
    "upstream_end": "832a5ce30f46c61c7f5c0817b15eccbc924c4abf",
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "Manifest and sidecar mappings are not bound to the raw bytes supplied for authentication.",
        "location": "joulewise/dominance_closeout.py:1159; scripts/build_d165_dominance_closeout.py:184"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "Malformed unhashable census and block-id inputs raise TypeError instead of a named neither-branch refusal.",
        "location": "joulewise/dominance_closeout.py:333,1046,1216"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "The top-level replay-sidecar digest guard lacks an isolated regression test, and partial/schema refusal cases are incompletely asserted.",
        "location": "joulewise/dominance_closeout.py:1346; tests/test_d165_dominance_closeout.py:393,431"
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "summary": "Contract prose fails first-use definitions and gives no runnable builder invocation.",
        "location": "docs/contracts/d165_dominance_closeout.md:31,63,69,237; scripts/build_d165_dominance_closeout.py:208"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.017s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import hashlib; from configs.campaigns.d117_contrast_v5 import generate_configs as g; from joulewise.analysis_manifest_v3 import canonical_json_bytes; print(hashlib.sha256(canonical_json_bytes(g.dominance_criterion_registration())).hexdigest())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check baec098f d53e09fb",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 76dc0c08 50fba9ee",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --quiet baec098f d53e09fb -- joulewise/analysis_manifest_v3.py joulewise/floor_extraction.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --quiet 76dc0c08 50fba9ee -- joulewise/analysis_manifest_v3.py joulewise/floor_extraction.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "blocking",
      "text": "No usable writable temporary directory was available; the focused D-165 suite and canonical suite could not reach normal completion.",
      "needs": "Magistrate rerun the focused, canonical, and mutation suites in a clean writable-temp runner."
    }
  ]
}
```

## Findings

### A. CONTRACT

| Ruled item | Cure and regression | Assessment |
|---|---|---|
| T-F1 / L-F2 | Exact floor-cell/component and common-cell census in `joulewise/dominance_closeout.py:1033-1078`; relabel and unknown-ID tests in `tests/test_d165_dominance_closeout.py:319-367`. | Correct for typed inputs. |
| L-F1 as re-ruled by 31c | Manifest attachment fields, digest checks, identity checks, block-set membership, and cell census in `joulewise/dominance_closeout.py:1130-1230`; builder regressions in `tests/test_d165_dominance_closeout.py:762-843`. | The ruling is implemented in the CLI/file path, but F1 leaves the object/bytes boundary unauthenticated. Per-block operand equality was correctly not reintroduced. |
| T-F2 | `d165_replay_blocks_from_mint_inputs` accepts block IDs, deltas, and `_CommonModeBlockInputs`, with `1e-12` tolerance and cap 16 in `joulewise/dominance_closeout.py:309-375`; adapter test at `tests/test_d165_dominance_closeout.py:1024-1031`. | Correct for valid inputs. |
| L-F3 | Exclusive output creation and exact `output_already_exists` refusal in `scripts/build_d165_dominance_closeout.py:251-259`; CLI test at `tests/test_d165_dominance_closeout.py:949-983`. | Correct. |
| L-F4 / L-F5 | Production finalizer fixture and validator guard matrices in `tests/test_d165_dominance_closeout.py:88-105,476-877`. | Coverage improved; producer E2E remains a separate stream. |
| L-F6 | Both fix-round deltas pass `git diff --check`. | Correct. |

The named contract refusals are present with exact spelling: `dominance_ratio_zero_denominator`, `manifest_lacks_replay_sidecar`, `replay_sidecar_digest_mismatch`, `replay_sidecar_identity_mismatch`, and `manifest_block_membership_mismatch`. Source-precondition failures route through the expected neither state: `branch=null`, `dominance_sentence_licensed=false`, `subtitle_licensed=false`, and `refusal_reason` set.

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| F1 | blocker | `joulewise/dominance_closeout.py:1159`; `scripts/build_d165_dominance_closeout.py:184` | The validator hashes `replay_sidecar_bytes` but validates the separately supplied `replay_sidecar` mapping. A self-consistent forged mapping with recomputed split/result fields, paired with the original authenticated bytes, was accepted as Branch A with both licenses true. | Make raw manifest/sidecar bytes authoritative by decoding them inside the consumer, or compare decoded objects before validation. Retain the named digest refusal and assert neither-branch fields. |
| F2 | should-fix | `joulewise/dominance_closeout.py:333,1046,1216` | Unhashable JSON values such as `component: []`, `block_ids: [[]]`, or an unhashable adapter ID raise `TypeError` before a named refusal is produced. | Type-check every set/map element before hashing and return the applicable named refusal with neither-branch fields. |

31c itself remains sound for its stated artifact model; the soundness defect is that the implementation does not enforce that model when callers provide parsed objects and raw bytes through separate channels.

### B. EXECUTION

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| F1 | blocker | `joulewise/dominance_closeout.py:1322-1350` | Authentication covers the raw bytes, but the branch decision consumes independently supplied mappings. The public builder/validator API can therefore license a forged object not represented by the authenticated file. | Eliminate split-channel authority or reject any mapping/byte mismatch before branch evaluation. |
| F2 | should-fix | `joulewise/dominance_closeout.py:1046,1216` | Malformed mutation inputs do not produce a refusal record at all. | Add fail-closed type guards and exact-reason assertions. |
| F3 | should-fix | `joulewise/dominance_closeout.py:1346-1350`; `tests/test_d165_dominance_closeout.py:431-445` | The requested sidecar-edit mutation with recomputed `closeout.replay_sidecar_sha256` is caught by `replay_sidecar_digest_mismatch` from the manifest attachment; the finalized manifest digest does not catch the sidecar edit. No test isolates the top-level replay digest guard, so deleting that guard would not be noticed. | Add a test that mutates only `closeout.replay_sidecar_sha256` while leaving sidecar bytes and manifest attachment unchanged, asserting its exact source-byte-hash reason and neither state. Add dedicated partial-attachment and schema-mismatch tests. |

### C. REGRESSION + PEDAGOGY

No fix-round production hunk was untraceable: census/adapter/output changes map to T-F1/T-F2/L-F3; fixture and matrices map to L-F4/L-F5; attachment and membership changes map to 31c. The D-117 generator registration is unchanged, and neither `joulewise/analysis_manifest_v3.py` nor `joulewise/floor_extraction.py` was touched by either fix round.

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| F4 | should-fix | `docs/contracts/d165_dominance_closeout.md:31,63,69,237`; `scripts/build_d165_dominance_closeout.py:208-217` | `sidecar` is used before it is defined; `close-out builder` precedes the close-out definition; `lineage` is not defined; `census` and the neither-branch are not glossed at first use. The contract contains no runnable CLI invocation and omits the parser’s exact flags and `output_already_exists` behavior. | Define each term at first use and add the exact `--finalized-manifest`, `--floor-artifact`, `--replay-sidecar`, and optional `--output` invocation, including refusal/output semantics. |

## Mutation table

| Mutation | Guard and result | Named reason | Existing exact assertion? |
|---|---|---|---|
| Manifest edited after close-out | Source digest guard; NEITHER | `closeout.finalized_manifest_sha256: source-byte-hash mismatch` | Yes, `tests/test_d165_dominance_closeout.py:431-445`. |
| Self-consistent forged sidecar mapping paired with original bytes | No guard; incorrectly accepted as Branch A with both licenses true | None; `refusal_reason=null` | No. This is F1. |
| Sidecar file edited after manifest attachment | Attachment digest guard; NEITHER | `replay_sidecar_digest_mismatch` | Yes, the forged-sidecar builder regression asserts the exact reason. |
| Sidecar from another campaign with different per-contrast block sets | Membership guard; NEITHER | `manifest_block_membership_mismatch` | Yes, `tests/test_d165_dominance_closeout.py:797-827`. |
| Absent attachment | Attachment-presence guard; NEITHER | `manifest_lacks_replay_sidecar` | Yes, `tests/test_d165_dominance_closeout.py:762-771`. |
| Partial attachment | Missing required fields map to `manifest_lacks_replay_sidecar`; malformed digest maps to `replay_sidecar_digest_mismatch`; NEITHER | As stated | No dedicated partial-entry test. |
| Identity mismatch | Identity guard; NEITHER | `replay_sidecar_identity_mismatch` | Sidecar-ID mismatch: yes. Schema mismatch: no dedicated exact test. |
| Correct `finalized_manifest_sha256`, but recomputed `replay_sidecar_sha256` after sidecar edit | Top-level close-out digest passes; manifest attachment digest fires; finalized manifest digest does not catch the sidecar edit | `replay_sidecar_digest_mismatch` | Attachment reason: yes; isolated top-level replay-digest guard: no. |
| Unhashable component/block-ID mutation | Unhandled `TypeError`; no close-out record | None | No. This is F2. |

The D-117 golden readback still computes `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b` and remains bound to `configs/campaigns/d117_contrast_v5/generate_configs.py`.

## Residual risk

The producer-side `D165-SIDECAR-EMIT-01` stream is not present; tests inject the manifest attachment after production finalization, as permitted by ruling 31c. Therefore producer-to-finalizer custody remains unproven until that separate stream is completed.

VERDICT: REFUTE — the fix rounds implement the ruled census, attachment, adapter, and CLI cures, but a forged replay-sidecar object that is not the authenticated sidecar bytes can still license Branch A.