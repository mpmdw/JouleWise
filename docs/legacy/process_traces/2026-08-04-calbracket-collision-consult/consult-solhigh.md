```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Approve a reviewed signature amendment, rename the guard as an interface pin, and distinguish integration-tree core/wrapper parity from D-110's governed re-mint.",
  "workspace": {
    "base_requested": "156ea20",
    "base_mode": "exact",
    "head_start": "156ea20e1c5c89bfbd7f8a6e222b50bf61b00216",
    "head_end": "156ea20e1c5c89bfbd7f8a6e222b50bf61b00216",
    "upstream_end": "c2f81d48e55d7c19709cc740640001b351237aa1",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-08-04-calbracket-collision-consult/"
  ],
  "verdict": {
    "recommendation": "Update _CORE_SIGNATURES to the D-109 signature as an explicit reviewed interface revision; do not add an adapter shim, multi-version layer, or core-file digest pin.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The proposed byte-compare oracle is ambiguous and can conflict with D-110",
        "location": "docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md:73"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The guard is an interface pin, not an honest byte freeze",
        "location": "scripts/mint_floor_artifact_generalized.py:4"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Output parity does not prove D-109's one-snapshot identity invariant",
        "location": "scripts/mint_floor_artifact.py:1959"
      }
    ],
    "questions": {
      "Q1": "Reviewed signature amendment.",
      "Q2": "Rename the contract to review-pinned mint-core interface and document the D-109 revision.",
      "Q3": "Not sufficient as stated; compare integration-tree core and generalized outputs and add one-load/object-identity coverage.",
      "Q4": "Update source, explicit signature and snapshot regressions, decision/process record, MINT and CAL kernel rows, and generated queue/run-state projections."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "sed -n '1,260p' docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Finding read first; diagnosis and proposed amendment inspected."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Recommended shape"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --no-ext-diff --unified=80 a14d1fe..impl/cal-bracket-d079 -- scripts/mint_floor_artifact.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Confirmed calibration_ledger_snapshot is loaded once at mint entry and threaded through both authentication calls and evidence rebinding."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_ledger_snapshot"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse impl/cal-bracket-d079",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "main at 156ea20e1c5c89bfbd7f8a6e222b50bf61b00216",
          "review branch at c2f81d48e55d7c19709cc740640001b351237aa1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c2f81d48e55d7c19709cc740640001b351237aa1"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": [
          "Not run by explicit user instruction."
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
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The lead must define byte identity as integration-tree core-versus-generalized parity, not require D-110's corrected governed re-mint to match the tainted historical artifact.",
      "needs": "Rule and record the reviewed interface amendment before merge."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No integration tree or tests were executed in this read-only consult.",
      "needs": "Run the amended focused module, parity replay, snapshot-identity regression, canonical suite, and merge-ref CI."
    }
  ]
}
```

## Findings

Committed recommendation — Q1: adopt the finding’s basic shape: update `_CORE_SIGNATURES["mint_floor_artifact"]` to include:

```text
calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None
```

Treat this as a deliberate D-109 R1.4 interface revision.

No alternative is structurally better:

- An adapter shim preserving the old core signature would conceal a claim-relevant dependency and weaken explicit snapshot injection. The core’s new boundary correctly loads once when absent and threads the same object through both components and rebinding (`impl/cal-bracket-d079:scripts/mint_floor_artifact.py:1959-2025`).
- A multi-version interface pin adds negotiation machinery when the generalized tool loads exactly one local core file (`scripts/mint_floor_artifact_generalized.py:478-492`). Introduce versions only if simultaneous compatibility with multiple core revisions becomes a real requirement.
- A core-file digest pin is too broad. It would reject comments, diagnostics, and legitimate security repairs while providing no behavioral proof. The existing exact signatures, required globals, pinset checks, parity tests, and reviewed diffs are the appropriate layered controls.

**F1 — blocker — Q3: the byte-identity oracle must be corrected.**

The 2026-08-03 procedure proves historical re-derivability at `3de370ec`; its record explicitly says current-head extraction refuses and generalized real-report parity was untested (`docs/process_traces/2026-08-03-q1-remint-bytecompare/RESULT.md:31-47`). Merely transplanting that replay to the integration tree is therefore not decisive.

Run two integration-tree mint paths from the same frozen reports, pinset, project metadata, and ledger state:

1. The reviewed mint-1 core directly.
2. The generalized wrapper loading that same integration-tree core.

Compare artifact and statement bytes between those two outputs. That answers whether the amendment preserves wrapper/core parity.

Do not require the future D-110 governed re-mint to equal the historical tainted artifact. D-110 requires re-derivation with the computed allowance after issuance and validator widening (`docs/decision_log.md:7107-7112`), so changed artifact bytes can be the correct result. If `FINDING.md:73-76` intends historical digest identity, it conflicts with D-110; D-110 wins. The ambiguous kernel acceptance text at `docs/process/state_kernel.json:1287` needs clarification.

Evidence could pass while the amendment remains wrong if:

- The replay imports the pinned old core or normal package import instead of the integration-tree file-loaded core.
- Both compared paths share the same defective core, preserving bytes while silently violating D-109.
- Genesis/fixture ledger state or mocks avoid the real snapshot path.
- Repeated snapshot loads happen to produce equal values; byte comparison cannot prove object identity.

**F2 — should_fix — Q2: “byte-frozen core” is no longer honest.**

The mechanism at `scripts/mint_floor_artifact_generalized.py:82-110` freezes selected signatures, while `_fresh_original_core` loads whatever bytes currently occupy `scripts/mint_floor_artifact.py`. It is an exact, review-controlled compatibility-interface pin—not a byte freeze.

Minimal correction:

- Call it the “review-pinned mint-core interface” in the module docstring, errors, helper docstrings, and test name.
- Add a note adjacent to `_CORE_SIGNATURES` stating that the D-109 R1.4 amendment added the immutable ledger snapshot parameter and that future changes require explicit signature-pin review plus parity evidence.
- Keep the current exact signature comparison. No digest mechanism is needed.
- Reserve “byte-identical” for observed artifact/statement output comparisons.

**F3 — should_fix — Q3: add a snapshot-identity regression.**

In addition to the exact-new-signature test and synthetic-drift test, add a cheap regression through the mint path that:

- makes `load_calibration_ledger_snapshot` return a sentinel;
- asserts it is called exactly once;
- asserts that exact object is supplied to absolute authentication, comparative authentication, and evidence rebinding.

This directly covers D-109 R1.4 (`docs/decision_log.md:7024-7029`). The branch audit covered snapshot identity elsewhere, but no mint-specific executable assertion was found.

Q4 — concrete ripple obligations:

- `scripts/mint_floor_artifact_generalized.py`
  - Amend the expected signature at lines 101-108.
  - Add the D-109 review note.
  - Replace inaccurate “byte-frozen core/interface” wording with “review-pinned mint-core interface.”

- `tests/test_mint_floor_artifact_generalized.py`
  - Add an explicit literal assertion pinning the new signature.
  - Retain `test_core_signature_drift_refuses_loudly`.
  - Rename the “byte-frozen core” parity test without weakening its byte comparison.
  - Add the one-load/same-object snapshot regression, here or in `tests/test_mint_floor_artifact.py`.

- `docs/process_traces/2026-08-04-calbracket-integration-collision/RESOLUTION.md`
  - Record the ruling, exact diff, integration-tree core/wrapper digests, snapshot regression, synthetic-drift result, focused/full-suite results, and CI result.
  - Preserve the existing finding and the historical Q1 result rather than rewriting them.

- `docs/decision_log.md`
  - Record the reviewed interface amendment.
  - Clarify D-110 without changing its three conditions: integration parity is tooling evidence, not the governed re-mint and not evidence that the corrected artifact must match the tainted historical bytes.

- `docs/process/state_kernel.json`
  - Rewrite `MINT-GENERALIZE-01` acceptance evidence at line 1287 to say “generalized path is byte-identical to the reviewed core on the same integration tree and inputs.”
  - Keep D-110 issuance and validator-widening dependencies intact.
  - Update `CAL-BRACKET-D079-01` status/evidence after the amended merge gate completes.

- `RUN_STATE.md` and `TASK_QUEUE.md`
  - Regenerate their marker-owned regions from the kernel.
  - Update the active handoff/collision language and mirrored MINT/CAL rows.

- `docs/run_reports/2026-08-04-<integration-amendment>.md`
  - Record the substantial-run handoff and exact verification.

- `PROJECT_STATUS.md`
  - Update only after the merge changes advisor-visible gate state. `CLAIMS_STATUS.md` should remain unchanged unless claim-bearing status actually changes.

## Residual risk

The branch implementation and records were inspected read-only; no composed integration tree or executable test was run. The unissued genesis ledger fixture can establish plumbing and parity, but cannot substitute for D-110’s later issued-ledger governed re-mint.

Checks performed: finding, D-109 synthesis, D-109/D-110 decision text, generalized guard and tests, branch core diff, historical byte-compare record, state-kernel MINT row, run-state handoff, and workspace status inspected; no files modified and no tests executed.