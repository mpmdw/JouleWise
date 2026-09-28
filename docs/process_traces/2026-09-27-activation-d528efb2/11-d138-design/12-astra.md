```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "SEAT: GPT-6 Astra — D138-25G83-DESIGN-01. Defect reproduced; recommend authenticated disposition filtering, a sealed issuance transform, atomic pin migration, and a separate claim-window hold.",
  "workspace": {
    "base_requested": "e7c8bcc6",
    "base_mode": "descendant",
    "head_start": "81c229c0530e34998857e2db04e75baed30db1ae",
    "head_end": "81c229c0530e34998857e2db04e75baed30db1ae",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Production completeness check rejects the eleven disposed observations"},
      {"id": "F2", "severity": "should_fix", "title": "Historical R7 consumers inherit the moving default"},
      {"id": "F3", "severity": "should_fix", "title": "Issuance authority and claim-window permission need separate representation"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/d138-design-d528efb2/astra/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "production_return_line=989",
          "issued_in_memory_valid=False",
          "foreign_valid_rows=11",
          "foreign_exactly_disposed=True",
          "skip_authenticated_disposed_valid=True",
          "one_disposition_removed_valid=False",
          "r7_still_valid=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "r7_still_valid=True"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Design consult only; no full suite, primary-corpus replay, issuance, or hardware validation performed.",
      "needs": "Execute the proposed verification at the implementation gate."
    }
  ]
}
```

## Findings

SEAT: GPT-6 Astra — D138-25G83-DESIGN-01

All recommendations below are **design inferences for the judge**, not installed rulings.

**F1 — Loader repair.** The in-memory probe authenticated candidate SHA-256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` and both seals. After issuance-field conversion and generation registration, validation returned False at [calibration_bracketing.py:989](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:989). All eleven offending rows exactly matched the authenticated registry. Exempting precisely those rows passed; withholding one exemption failed. This isolates the reported defect without changing repository bytes.

Move the issuer’s registry pin, parser and validation into a small shared package module, proposed `joulewise/calibration_dispositions.py`. Both issuer and loader call it; neither maintains a second interpretation. Retain the existing **raw-file** SHA-256 pin `ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c`, decision id, mechanism and duplicate-row checks. Read through `read_authentication_input`, preserving authentication-session custody. Sources: [issuer:511](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:511), [issuer:1326](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:1326), [authentication_io.py:547](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/authentication_io.py:547).

Bind that policy to this generation in trusted code. Require:

- Every disposed content id remains in the prior set.
- Its decision is represented by the artifact’s exact, duplicate-free `disposing_decision_ids` list.
- No disposed id becomes a member or an ordinary member-exclusion entry.
- Only authenticated dispositions are subtracted from completeness. Every remaining foreign same-epoch `valid` row still refuses.
- Historical generations without this policy retain their existing behavior and no new file dependency.

Preserve the member/exclusion set-equality check after subtraction; do not broaden registered sessions. The existing obligations are at [issuer:2055](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:2055), [bracketing:1024](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:1024), and [decision_log.md:12199](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/decision_log.md:12199). Amend the last citation’s “sole new registry consumer” sentence explicitly when adding the loader.

Defect-shaped tests should pair the real positive case with: one missing disposition; an appended foreign row; wrong/missing/extra decision ids; omitted disposed prior row; disposed member; registry byte mutation, unreadability, duplicate keys/rows, wrong mechanism; missing legitimate member. Recompute artifact seals in semantic mutations so failures reach the intended check. Test exact-byte loading separately. Retain an R7 positive control with the disposition file unavailable. Future registry changes must preserve this generation’s pinned snapshot.

**Issued bytes.** Promote the reviewed candidate through a deterministic transform; do not rerun preparation as issuance. Preserve the candidate file.

The complete permitted mutation list should be:

1. `acceptance_id` only if Ed chooses another name.
2. `candidate_not_issued = false`; `artifact_role = "issued"`.
3. Replace the entire `issuance` block: issued status, `claim_eligible = true`, accurate reason/licence, source-candidate digest, gate provenance, disclosures and hold.
4. Change `backfill_candidate.status` to issued and `production_issuance_blocked` to false; replace its stale “pending” verification sentence with completed evidence references.
5. Recompute seals and register the resulting serialized file digest.

The issuer explicitly requires replacement of the whole issuance block: [issuer:2236](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:2236). The loader’s issued predicates are at [bracketing:749](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:749).

Recompute `derivation_input_sha256` using its existing recipe; demand equality unless Ed changes identity, because that seal includes `acceptance_id`. Then recompute `derivation_sha256` over every field except itself using sorted keys, compact separators, UTF-8, `ensure_ascii=False`, `allow_nan=False`. Finally serialize deterministically and SHA-256 the actual bytes for the registry. These are distinct hashes: [issuer:2329](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:2329), [bracketing:654](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:654).

Require an allowlisted structural diff and byte comparisons of protected blocks: all twelve members and decimal lexemes, all 86 prior observations, disposition ids, cutoff, identity, estimator/protocol pins, statistics, proofs, operatives, generation row and existing derivation notes. An independent preparation replay is verification only. A1 expressly forbids repairing this transaction by re-preparing under changed estimator code: [addendum:190](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:190).

**F2 — Atomic migration and historical consumers.** The production grep inventory identifies these migration surfaces:

- New issued JSON; its path/id/file-hash constants; `ISSUED_ACCEPTANCE_REGISTRY`; its independently registered generation row; `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` in [bracketing:137](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:137) and [bracketing:377](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/calibration_bracketing.py:377).
- Additive issued-id admission in [arm_readiness.py:6191](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/arm_readiness.py:6191) and [schema_v2.json:192](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/floor_mint_pinsets/schema_v2.json:192).
- Shared disposition repair, historical-default repairs, regression tests, issuing record and current state/queue projections.

Convert the generation row’s two array fields to tuples using the established recipe; register the n12 row, not the n17 row: [issuer:1058](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:1058).

Freeze Revision-5 predecessor validation and its preparation default to explicit R7; freeze the equivalence checker’s default path alongside its already-R7 required id. Its Revision-2 comparison remains historical, not a new issuance gate. Sources: [issuer:1798](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:1798), [issuer:2553](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:2553), [epoch_equivalence_check.py:152](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/epoch_equivalence_check.py:152), [checker:699](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/epoch_equivalence_check.py:699).

Audit moving-default fixtures in `test_calibration_bracketing`, `test_epoch_equivalence_check`, `test_epoch_continuation`, `test_issue_calibration_acceptance_generation`, `test_issuer_corpus_root`, and the mint/derivation-input suites. Preserve historical R7 tests explicitly; add separate new-default expectations. One concrete stale assertion is [test_calibration_bracketing.py:615](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/tests/test_calibration_bracketing.py:615).

R7 bytes, pins, derivation, frozen packs and preregistration remain unchanged and must still judge 25F84. Do not alias the n12 corpus to the historical verifier’s n17 bank; its current paths assume repository-local custody: [verify_calibration_acceptance_corpus.py:64](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/tests/verify_calibration_acceptance_corpus.py:64), [same:88](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/tests/verify_calibration_acceptance_corpus.py:88).

**F3 — Disclosures and H1.** Put D1–D7, corrected by A1, in both the issuing record and sealed issuance metadata, with source paths/digests. Include H1 and its release criteria there; render H1 into every 25G83 arm material. That exceeds the minimum placement requirement but makes the restriction portable. Sources: [science gate:180](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:180), [addendum:195](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:195).

Interpret artifact `claim_eligible=true` as **eligible calibration authority subject to separate window authorization**. It cannot mean H1 is discharged. Recommend a shared, fail-closed epoch hold check at arm authorization and execution revalidation, using authenticated window purpose/claim status. Missing classification must not become “nonclaim.” Release requires a pinned written route-R/M ruling, never an operator boolean. Existing window authorization already distinguishes purpose and claim eligibility: [night_gate.py:978](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/joulewise/night_gate.py:978). Procedural text alone is inadequate protection; H1 nevertheless is expressly not an issuance precondition.

**Verification, gates and ordering.** Before issue, independently rehash candidate, both seals, R7, disposition registry, preregistration, protocol, four estimator files, member manifests/evidence, ledger chain through cutoff 276, battery verdicts/raw observations, and referenced gate/custody records. Repeat estimator hashes after merge; my current-tree comparison matched all four. Audit discharge of custody-repair and predecessor-path conditions specifically left to this gate: [science gate:171](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md:171).

Require independent primary-byte membership/statistical/quantile replay, exact transformation comparison, positive 25G83 load/bind, historical R7 load/judgment, cross-epoch refusal, tamper failures and H1 arm refusal/nonclaim passage. Run focused checks and `python3 -m unittest discover -s tests`; investigate default-migration failures rather than broadly rewriting expectations.

Sequence: cold design ruling → Ed’s name decision → implementation and issued-byte proposal → independent contract/execution reviews → fixes and independent test audit → full suite → cold gate with distinct contract reviewer → lead exact-head review and authorized atomic merge → merged-hash confirmation. This follows [orchestration.md:63](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/orchestration.md:63). Mechanical comparisons are delegated; judgment-bearing publication remains Ed’s: [decision_log.md:197](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/decision_log.md:197).

**Name and stops.** Recommend `d079_calibration_acceptance_v2_n12_25g83_r1`: it accurately separates epoch and corpus from R7 and matches the issuer’s naming recipe ([issuer:1055](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/scripts/issue_calibration_acceptance_generation.py:1055)). Ed decides. Stop issuance on any B1/B2 mismatch; do not fold in cap work or waiting estimator branches. Do not delay issuance for route-R/M measurements, and do not interpret issuance as opening claim windows ([addendum:190–200](/Users/edr/code/JouleWise-wt-d138-astra-d528efb2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:190)).

## Residual risk

The probe establishes the completeness defect and a discriminating counterfactual, not a finished repair. Primary-corpus replay, authentication-custody integration and complete arm-entry coverage remain implementation-gate obligations.