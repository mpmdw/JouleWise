```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Amend V2/V3/V4/V6: defer to _v4, close refusal issuance and the freeze-error escape, use a real R1 re-use comparator, and carry an explicit UNBUILT marker limitation.",
  "workspace": {
    "base_requested": "afb7d57",
    "base_mode": "descendant",
    "head_start": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "head_end": "60ddb03a903d1e005190c966960fb091ed4f0e53",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "R1 refusal codes are not issuable or load-closed",
        "detail": "All eight prior Terra r1_* codes fail receipt validation; the lifecycle validator nevertheless accepts them."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "title": "A lifecycle refusal escapes generate_arm_receipt",
        "detail": "_freeze_evidence_for_arm propagates EvidenceLifecycleError outside the receipt-refusal path."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "title": "_v3 is independently refused by V1_GRANDFATHERING",
        "detail": "Each _v3 freeze-0003 binds eleven legacy generic PACK receipts, which R1 rejects."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "The proposed V2 comparator is in the wrong re-use branch",
        "detail": "R1 selects _authenticate_existing_r1, not the legacy branch at 2090-2126."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "title": "Twenty-minute generic freeze evidence is unsuitable",
        "detail": "Ten newly ruled kinds use the generic R1 authoring path and should retain the existing 24-hour behaviour."
      },
      {
        "id": "N1",
        "severity": "nit",
        "title": "Fifteen is an install-gate checklist, not a literal reserved-leaf count",
        "detail": "The placeholder contains 23 ED_RESERVED leaf occurrences (16 unique); empty arrays and code closure are separate gates."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor afb7d5705add3475cd016177a8f8fa1dd02a814e HEAD && git diff --quiet afb7d5705add3475cd016177a8f8fa1dd02a814e..HEAD -- joulewise/ configs/arm_readiness/ tests/test_arm_readiness_evidence.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ancestor_exit=0", "target_diff_exit=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ancestor_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'from joulewise import arm_readiness as a\\nc={\"r1_class_mismatch\",\"r1_dependency_changed_set\",\"r1_dependency_manifest\",\"r1_family_publication\",\"r1_successor_chain\",\"r1_temporal_budget\",\"r1_unknown_policy\",\"r1_v1_grandfathering\"}\\nprint(sorted(c & a.READINESS_REASON_CODES), sorted(c-a.READINESS_REASON_CODES))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["V4 receipt probe: all 8 codes refused as not closed", "R1 lifecycle validator accepted the same unregistered vocabulary"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "r1_class_mismatch"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'from joulewise import arm_readiness as a\\nfrom joulewise import arm_readiness_evidence as e\\nfrom joulewise import arm_readiness_evidence_t0 as t\\nx={k for k,v in a.R1_EVIDENCE_FRESHNESS_CLASSES.items() if v==\"EXECUTION_BOUND\"}\\nprint(sorted(x & set(e._GENERIC_DERIVER_KINDS)),sorted(x & set(t._ROW_KIND.values())),sorted(x-set(e._GENERIC_DERIVER_KINDS)-set(t._ROW_KIND.values())))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["generic=10", "t0=2", "no_generic_or_t0=4", "_v3 remaining_seconds=19355.5 at 2026-08-20T11:27Z"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "generic=10"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<read-only in-memory lifecycle probe against freeze-0003 and _freeze_evidence_for_arm>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["V1_GRANDFATHERING_EXECUTED role=V1_GRANDFATHERING", "FAIL_UGLY_EXECUTED escaped_role=V1_GRANDFATHERING return=none"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "escaped_role=V1_GRANDFATHERING"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No writable end-to-end _v4 author→freeze→arm rehearsal was possible in this read-only worktree.",
      "needs": "Run the corrected transaction and canonical suite in a writable isolated clone."
    }
  ]
}
```

## Findings

### B1 — blocker — refusal-code closure

CONCEDED. The opposing probe is right. I independently invoked `_validate_refusal` for all eight prior `r1_*` values: every one refuses as “code is not closed.” `READINESS_REASON_CODES` and `REASON_TYPE_BY_CODE` are closed at [arm_readiness.py:192](./joulewise/arm_readiness.py:192) and enforced at [1434](./joulewise/arm_readiness.py:1434).

Worse, the registry validator accepts the same unregistered entries: its refusal loop checks syntax/type-enum only, not code-map membership ([1746](./joulewise/arm_readiness.py:1746)-[1805](./joulewise/arm_readiness.py:1805)). Install must include distinct `readiness_r1_*` code/map entries and a registry-side closure check. The opposing type allocation is viable; the pre-existing `SUCCESSOR_CHAIN` reason type is not registry-expressible.

### B2 — blocker — fail-ugly path

CONFIRM. An executed in-memory R1 probe made `_freeze_evidence_for_arm` propagate `EvidenceLifecycleError`; AST inspection finds its call at [6139](./joulewise/arm_readiness.py:6139) has no enclosing `try`. `_discover_evidence` catches the same exception at [4613](./joulewise/arm_readiness.py:4613), so arm generation must do likewise and append `exc.refusal()`.

### B3 — blocker — grandfathering and fuse

CONFIRM. All three `_v3` `freeze-0003` receipts contain 11 legacy PACK/v1 generic receipts out of 12 items. An actual frozen item raised `V1_GRANDFATHERING` under the candidate lifecycle through [4219](./joulewise/arm_readiness.py:4219)-[4229](./joulewise/arm_readiness.py:4229). This independently bars `_v3` under R1.

The fuse calculation also reproduces: at 11:27Z the `_v3` minimum was `2468742407178458`, with 19,355.5 seconds remaining; that is consistent with the opposing 5.73-hour result at 11:07Z.

### S1 — should fix — V2 comparator

PARTLY CONFIRM, but the proposed line range is wrong. [2090](./joulewise/arm_readiness_evidence.py:2090)-[2126](./joulewise/arm_readiness_evidence.py:2126) is legacy `_authenticate_existing`; an R1 install routes re-use through `_authenticate_existing_r1` at [2216](./joulewise/arm_readiness_evidence.py:2216), selected at [2361](./joulewise/arm_readiness_evidence.py:2361)-[2378](./joulewise/arm_readiness_evidence.py:2378). Neither path compares a fingerprint.

Put the comparator in `_authenticate_existing_r1`. Compare the nested fingerprint facts for interpreter descriptor plus implementation, Python version, system, release, and machine; “six scalar” is slightly inaccurate because interpreter is a descriptor object. A mismatch can refuse re-use with author vocabulary; it needs no new R1 role, but it does not automatically re-author the existing append-only namespace. I withdraw `RECORD_ONLY` in favor of an explicitly re-use-scoped token.

### S2 — should fix — V3 horizons and census

CONCEDED on tiers. The ten newly ruled generic kinds are the only ones whose R1 policy horizon is live at generic issuance; they should retain 24 hours, matching `_EVIDENCE_VALIDITY_NS` at [arm_readiness_evidence.py:42](./joulewise/arm_readiness_evidence.py:42). A 20-minute freeze→arm ceremony is incompatible with the cited 900-second suites and no-retry windows.

The four-kind statement needs correction: `GIT_CHECKOUT` and `PRIVILEGE_INSTALLATION` lack a generic/T-0 lane, but `IDENTITY_PIN_PROJECTION` and `DRY_RUN_REHEARSAL` have specialized producers ([3919](./joulewise/arm_readiness.py:3919), [5775](./joulewise/arm_readiness.py:5775)). Six registry horizon declarations are nevertheless non-authoritative today: two T-0 kinds have their own fixed six-hour source ([arm_readiness_evidence_t0.py:115](./joulewise/arm_readiness_evidence_t0.py:115)-[121](./joulewise/arm_readiness_evidence_t0.py:121)), plus the four non-generic policy rows.

### N1 — nit — marker, outer identity, and enumeration

CONCEDED on V6. D-147 explicitly deferred marker co-design ([14-r2-ruling.md:119](./docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:119)); current code has no marker consumer or `FAMILY_PUBLICATION` raise site. Use an explicit `UNBUILT.v0` token, runsheet publication refusal, canary, and registered limitation. Do not pretend it is runtime fail-closed.

REFUTE “15 reserved sites” as a literal validator count: the placeholder has 23 reserved leaf occurrences, 16 unique. Accept it only as a grouped 15-gate install checklist.

The byte-pin does not force the new `_v4` outer ID after archival replay is adopted; `_v2` schema accepts any nonempty outer ID ([1857](./joulewise/arm_readiness.py:1857)-[1859](./joulewise/arm_readiness.py:1859)). The path remains operationally fixed absent a code delta by `ROW_REGISTRY_RELATIVE_PATH` ([80](./joulewise/arm_readiness.py:80)).

## Residual risk

The corrected transaction still needs a writable `_v4` rehearsal, including V2 re-use mismatch, all issued V4 refusals, and an arm receipt carrying a captured freeze-path refusal.

## Final amended position

- V1 — AGREED: install `_v4` successor IDs; `_v3` is archival replay only.
- V2 — CONCEDED: replace RECORD_ONLY with an exact interpreter/platform comparator in the R1 re-use path.
- V3 — CONCEDED: ten generic kinds 24h; T-0 mirrors 6h; four remaining declarations explicitly non-authoritative.
- V4 — CONCEDED: add closed `readiness_r1_*` code/type deltas and registry-load closure.
- V5 — AGREED: 300s capability and 300s budget, conditional on the real T-0→arm rehearsal.
- V6 — CONCEDED: `UNBUILT.v0` plus canary, runsheet refusal, and registered limitation.
- Outer ID/path — DISPUTED (no byte-pin force): retain the fixed path; use the new outer ID for `_v4` clarity.
- Install timing — AGREED: one corrected code/registry transaction at `_v4`, then author, freeze, arm, and consume there.