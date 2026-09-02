```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The three transaction artifacts are absent; the family-publication marker should own the arm census, a pre-commit guard should enforce fixation-first, and three ruled-shape ambiguities require magistrate rulings.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "3b0e23f0345fc630dbed497cf611758281020ed2",
    "head_end": "3b0e23f0345fc630dbed497cf611758281020ed2",
    "upstream_end": "3b0e23f0345fc630dbed497cf611758281020ed2",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "D-155 orders freeze-off before fixation, while its runbook keeps COMMIT_FREEZE_OPEN until after the fixation push; treating one as logical and the other as physical would reinterpret the ruling."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "The semantic artifacts transfer to v5, but the exact successor-pinset path, canonical pack IDs, family marker, and new clone proof are not settled and HEAD remains v4-only."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "text": "The NR-13 shell guard blocks Git publication but checks the sentinel only after writing WINDOW_STATUS.md, contrary to the literal refuse-before-write ruling unless write is redefined."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "text": "campaign-close.json and its validator/transcript are absent."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "text": "The successor fixation literal, content guard, and first-post-freeze commit guard are absent."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "text": "A6's open head exists, but no authoritative v5 arm census, close computation, or post-close arm refusal exists."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "text": "The kernel row has stale v4 wording, empty dependencies, and an obsolete claim that window_runbook section 11 is absent."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "! rg -n 'campaign[_-]close|campaign-close' joulewise scripts tests docs/contracts",
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
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n 'COMMIT_FREEZE' joulewise scripts --glob '*.py' --glob '*.sh'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/window_status.sh:34:COMMIT_FREEZE_SENTINEL=\"${JOULEWISE_COMMIT_FREEZE_SENTINEL:-/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN}\"",
          "scripts/window_status.sh:95:if [ -e \"$COMMIT_FREEZE_SENTINEL\" ]; then"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scripts/window_status\\.sh:95:"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "3b0e23f0345fc630dbed497cf611758281020ed2",
          "3b0e23f0345fc630dbed497cf611758281020ed2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "3b0e23f0345fc630dbed497cf611758281020ed2$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Resolve logical freeze close versus physical COMMIT_FREEZE_OPEN removal.",
      "needs": "Magistrate ruling on the exact meaning of D-155's freeze-off step."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Approve a repository-managed pre-commit guard as the A1 refusal host.",
      "needs": "Magistrate ruling (b); CI alone only detects an already-made bad commit."
    },
    {
      "id": "G3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Set the v5 successor-pinset path and canonical underscore/hyphen pack IDs.",
      "needs": "Magistrate ruling before v5 registry or fixation implementation."
    },
    {
      "id": "G4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NR-13 currently writes WINDOW_STATUS.md before checking the sentinel.",
      "needs": "Rule whether refuse-before-write means before any repository write or only before Git publication."
    },
    {
      "id": "G5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite was run in this read-only design review.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1–F3, blockers:** freeze semantics, the v5 identity instantiation, and NR-13’s meaning of “write” require rulings.
- **F4–F6, should fix:** all three requested artifacts remain absent.
- **F7, should fix:** the kernel row has drifted behind D-164/D-167 and the current runbook.

### Q1 — `campaign-close.json` [F1, F4]

Recommendation: write `$CUSTODY_ROOT/campaign-close.json` at real-transaction runbook §H5, after H4 and before H6. The convention is `CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"` with run evidence below it (`real-transaction-runbook.md:393-411`); §H1 explicitly leaves transaction custody open for this record and transcript (`:1229-1235`), and §H5 owns the trigger and order (`:1253-1318`).

Proposed exact schema ID: `joulewise.campaign_close.v1`. Exact top-level fields:

- `schema_version: Literal["joulewise.campaign_close.v1"]`; `transaction_id: string`; `authority: ["D-155/NR-8","D-153/A6"]`; `declared_by: string`; `declared_at_utc: RFC3339 string`; `declared_at_monotonic_ns: integer`; `declared_head: 40-hex string`.
- `family_marker` and `step6_table`: `ArtifactRef`; `slot_ledger: ArmSlot[]` in published marker order.
- `arm_sets: {planned: ArmKey[], executed: ArmKey[], planned_sha256: hex64, executed_sha256: hex64, equal: Literal[true]}`.
- `changed_set_window: {open_derivation_head: hex40, close_last_consuming_arm_id: string, close_completion: ArtifactRef, close_at_utc: string, close_at_monotonic_ns: integer}`.
- `predicates: {published_plan_equal, every_arm_consumed, every_arm_completed, every_whole_window_eligible, commit_freeze_close_authorized}` with every value literally `true`.
- `artifact_ledger: ArtifactRef[]`; `required_record_order: ["declaration","freeze_off","notification","fixation","bookkeeping"]`.
- `ArmKey = {profile, pack_id, plan_id, window_id}`. `ArmSlot` adds `ordinal`, `status:"completed"`, and authenticated `arm_receipt`, `launch_consumption`, `launch_completion`, `whole_window_verdict`, and `campaign_log` references.
- `ArtifactRef = {role, path, schema_version, sha256}`; `path` is custody-root-relative and `sha256` hashes that artifact’s exact raw bytes. Set hashes cover compact sorted-key UTF-8 JSON plus LF, normalized into marker order. `campaign-close.json.sha256` hashes the final close file’s exact bytes.

This key schema is an instantiation of the ruled Sol-seat ledger/digest/predicate shape, not a replacement: the adopted source requires slot ledger, artifact digests, predicates, times, and transcript SHA (`nr-seat-sol.md:37-42`).

The published arm set comes from the authenticated family-publication marker’s `members[]`, built from the registry at `arm_readiness.py:11374-11382` and required to have one common derivation head at `:11384-11386`. The executed arm set comes from one authenticated arm receipt plus launch-consumption and launch-lifecycle-completion chain per member (`arm_readiness.py:9700-9732`, `:9888-10020`, `:10272-10338`).

Neither `order_manifest.json` nor analysis `arms[]` is the transaction arm census: the v5 root order manifest contains the 80 internal run entries (`generate_configs.py:3074-3173`), while analysis-manifest arms are scientific A/B conditions (`analysis_manifest_v3.py:834-878`). The whole-window verdict and authoritative campaign-log row prove each pack’s internal execution, including `bundle_ids` (`run_campaign.py:6117-6170`, `:6310-6373`), but do not define the three-arm transaction roster.

Validator refusals: unknown/missing keys; noncanonical JSON; non-hex digests; absolute, symlinked, or custody-escaping paths; artifact digest/schema mismatch; unauthenticated marker/table; duplicate, absent, or extra arm keys; any planned/executed inequality; missing consumption/completion; identity or lineage mismatch; noneligible whole-window verdict; verdict not matching its authoritative log row; more than one open derivation head; ambiguous final member; changed-set close not bound to the final completion; existing output/sidecar; or any false predicate. Equality failure must return the Ed escape without writing either output.

Make order mechanical with `$CUSTODY_ROOT/campaign-close.transcript.jsonl`, a create/append-only hash chain permitted by §H1. Rows hold `sequence`, `event_type`, prior-row hash, exact evidence reference, UTC/monotonic time, and actor: declaration references the close digest; freeze-off references an immutable freeze-close receipt; notification references a durable provider message/delivery ID; fixation records commit, parent, literal, pinset digest, and exact changed paths; bookkeeping records later commit IDs. Final validation also checks the fixation commit’s parent equals `declared_head` and no intervening commit exists.

Required regression: transcript permutation `declaration → freeze_off → notification → bookkeeping → fixation` must fail `campaign_close_record_order_invalid`.

**NEEDS-RULING:** D-155 says freeze-off before notification/fixation (`decision_log.md:182`; `nr-synthesis-ruling.md:72-79`), but the runbook removes `COMMIT_FREEZE_OPEN` only after the fixation is pushed (`real-transaction-runbook.md:1297-1318`). Calling the former “logical close” and the latter “physical latch removal” is reasonable but is a reinterpretation, not an implementation detail.

### Q2 — A1 fixation commit [F1, F5]

Recommendation: use a tracked test pin, not a passive sidecar. The live fixation commit should add exactly `tests/test_receipt_histsem_fixation.py`, containing `SUCCESSOR_PINSET_PATH`, `PINSET_SHA256 = "<hS>"`, and a test that hashes the pinset’s exact bytes and asserts equality. The existing `PINSET_SHA256` at `tests/test_receipt_histsem.py:45` authenticates the base v1 pinset; its successor section has only v4 identity/prose (`:56-69`, `:231-249`), so repurposing it would conflate two authorities.

`scripts/refresh_receipt_histsem_pinset.py:37-39` recognizes exactly one `PINSET_SHA256` literal, while `--print-pinset-sha256` and `--write-test-pin` are exposed at `:55-68`. However, no-row operation permits print-only and forbids writing a test pin (`:547-561`); therefore use print-only to obtain hS and a dedicated fixation writer to create the new live-only test. Do not mutate the successor pinset during fixation.

“Loud fail” needs two layers:

- Content guard: the test and verifier fail on any literal/pinset digest inequality; a one-nibble literal mutation must fail `test_fixation_literal_one_nibble_flip_fails`.
- History guard: pre-land `.githooks/pre-commit` backed by a shared validator. During C8, require `core.hooksPath=.githooks` and bind the external transaction root in local Git config. Once canonical campaign-close and its pre-fixation transcript rows exist, require `HEAD == declared_head` and the staged diff to contain only the fixation test; after fixation, require its validated transcript event before allowing bookkeeping.

A wrapper or CI-only check cannot truthfully satisfy “refuses the first post-freeze commit”: a wrapper can be bypassed, and CI observes the bad commit after creation. CI should replay the history validator as a backstop. An arm-readiness gate is the wrong lifecycle boundary because the commit occurs after the last arm.

Counterfactuals: flip one hS nibble → content test/verifier fails; stage `RUN_STATE.md` as the first commit → pre-commit fails `fixation_required_as_first_post_freeze_commit` without creating a commit.

**NEEDS-RULING (b):** approve the repository-managed pre-commit hook plus shared validator; no commit-time host exists at HEAD.

### Q3 — A6 LAST CONSUMING ARM [F6]

Candidate census sources at HEAD:

- Registered family roster: authoritative in shape, but currently only the v4 Qwen2.5 roster exists (`d117_row_registry_v2.json:517-536`); marker construction consumes it at `arm_readiness.py:11374-11382`, and several live paths still hardcode `d117-v4` (`:10850-10911`, `:11412-11443`).
- v5 order manifests/plan tree: internal run and stage order for one pack, not the three transaction arms (`generate_configs.py:1722-1755`, `:2139-2381`, `:3074-3173`).
- Analysis Manifest v3 `arms[]`: A/B scientific condition identities and finalized only after collection (`analysis_manifest_v3.py:834-878`, `:3618-3628`, `:3743`).
- Campaign policy: environmental/idle criteria only, with no arm roster (`quiet_mac_p2_production.json:1-52`).

Recommendation: the published family marker is authoritative. Before issuing an arm, load its marker-ordered roster and authenticated completion lineages. The current arm is `is_last_consuming_arm=true` exactly when every other member is complete, the current member is the sole missing member, and no other receipt is open. After its launch lifecycle completes, the §H5 writer requires all members complete and records that receipt ID as `close_last_consuming_arm_id`. This implements NR-8’s “last consuming arm ID; window-consume completion permits commit-freeze close” (`nr-synthesis-ruling.md:72-79`) without treating internal pack counts as arms.

The gate first checks canonical `campaign-close.json`; present-valid and present-invalid must both refuse before creating an arm receipt. A newly required `transaction_custody_root` binding in arm context lets every arm locate the same close record; current arm generation has only `window_custody_root` and no campaign close (`arm_readiness.py:8182-8191`), and arm-context validation is exact-key (`:2392-2411`).

The OPEN side is the marker’s exactly-one common derivation head (`arm_readiness.py:11265-11270`, `:11384-11386`). `readiness_r1_dependency_changed_set` is only a closed-vocabulary reason code (`arm_readiness.py:202`; `arm_readiness_evidence.py:2356`), not the close computation.

Counterfactual: after a valid close, requesting another member must fail `arm_after_changed_set_close` before namespace creation; an injected receipt with sequence/time after close must make the close verifier fail `campaign_close_has_post_close_arm`.

**NEEDS-RULING (a):** authorize the published family marker as the arm census and the sole-missing-member rule as the mechanical “last consuming arm” test.

### Q4 — Transfer to `_v5` [F2]

D-164 says `_v4` is never collected and `_v5` is the same frozen design regenerated, with D-153 unchanged in substance (`decision_log.md:10365-10373`); D-167 reconciles the kernel without changing soundness (`:10407-10418`).

- `campaign-close.json`: schema and refusal semantics transfer unchanged; family ID, generation, marker/table digests, arm receipt IDs, heads, times, and custody root are instance parameters.
- A1: literal-plus-guard and fixation-first semantics transfer unchanged. The current exact successor path ends `_v4_v1` (`real-transaction-runbook.md:115-133`; `tests/test_receipt_histsem.py:56-69`); renaming it `_v5_v1` changes an exact allowlisted identity and is **NEEDS-RULING**, not a casual parameter substitution.
- A6: open/close semantics transfer unchanged; the v5 marker roster and transaction-custody binding are parameters once published.
- Pack IDs are parameters only after canonical spelling is ruled: `v5-artifact-flow.md:9` uses hyphens while the generated/runsheet IDs use underscores (`generate_configs.py:1151-1180`; G2 runsheet `:178-180`).
- Custody date/root is a runtime parameter if the `analysis/transaction` convention is preserved.
- The v4 S-0 clone-proof record does not transfer as evidence: V5-DESK-DAY independently requires regenerated v5 packs and clone proof (`state_kernel.json:4753-4818`). Treating the old proof as satisfying v5 would reinterpret acceptance.

### Q5 — Sequencing, scopes, tests, mutations

Run three serialized sessions because Sessions 1 and 2 share the strict-order contract/runbook and Session 3 consumes Session 1’s close reader.

1. **Campaign close WRITE_SCOPE:** `joulewise/campaign_close.py` (new), `scripts/build_campaign_close.py` (new), `scripts/verify_campaign_close.py` (new), `scripts/record_campaign_close_event.py` (new), `tests/test_campaign_close.py` (new), `docs/contracts/campaign_close.md` (new), `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`, `docs/process/window_runbook.md`.
   Acceptance: `test_build_and_verify_from_published_roster_and_completed_lineages`, `test_refuses_executed_set_not_equal_published_plan`, `test_refuses_artifact_digest_mismatch`, `test_record_order_refuses_bookkeeping_before_fixation`, `test_output_is_create_only_and_custody_bounded`.

2. **Fixation WRITE_SCOPE:** `joulewise/fixation.py` (new), `scripts/write_successor_pinset_fixation.py` (new), `scripts/verify_successor_pinset_fixation.py` (new), `.githooks/pre-commit` (new, conditional on ruling b), `tests/test_successor_pinset_fixation.py` (new), `tests/test_receipt_histsem_fixation.py` (reserved live-only output), `docs/contracts/successor_pinset_fixation.md` (new), and the same two runbooks.
   Acceptance: `test_fixation_literal_one_nibble_flip_fails`, `test_guard_accepts_only_exact_fixation_commit`, `test_guard_refuses_bookkeeping_as_first_post_freeze_commit`, `test_guard_refuses_advanced_head`, `test_writer_never_mutates_pinset`.

3. **A6 WRITE_SCOPE:** `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence_t0.py`, `scripts/generate_arm_readiness.py`, `scripts/capture_t0_step.py`, `configs/arm_readiness/d117_row_registry_v2.json` (after v5 identity rulings), `configs/campaigns/d117_contrast_v5/generate_configs.py`, `tests/test_arm_readiness.py`, `tests/test_arm_readiness_lifecycle.py`, `tests/test_arm_readiness_schemas.py`, `tests/test_arm_readiness_registry.py`, `tests/test_arm_readiness_evidence_t0.py`, `tests/test_arm_readiness_integration.py`, `tests/test_d117_contrast_v5_pack.py`, `docs/contracts/changed_set_window.md` (new), `docs/process/v5-artifact-flow.md`, and the same two runbooks.
   Acceptance: `test_last_arm_is_sole_missing_published_member`, `test_census_comes_from_family_marker_not_analysis_arms`, `test_close_records_common_head_and_last_completion`, `test_arm_refuses_before_write_when_close_exists`, `test_invalid_close_fails_closed`, `test_close_verifier_refuses_post_close_arm`.

| Artifact | Mutation | Counterfactual | Required failing test |
|---|---|---|---|
| Close | Delete GAMMA execution | Published set has three, executed has two | `test_refuses_executed_set_not_equal_published_plan` |
| Close | Flip verdict digest | Referenced raw bytes no longer hash-match | `test_refuses_artifact_digest_mismatch` |
| Close | Move bookkeeping before fixation | `declaration,freeze_off,notification,bookkeeping,fixation` | `test_record_order_refuses_bookkeeping_before_fixation` |
| Fixation | Flip one hS nibble | Literal differs from exact pinset bytes | `test_fixation_literal_one_nibble_flip_fails` |
| Fixation | Stage bookkeeping first | Staged path is not the fixation test | `test_guard_refuses_bookkeeping_as_first_post_freeze_commit` |
| A6 | Request an arm after close | Valid close already exists | `test_arm_refuses_before_write_when_close_exists` |
| A6 | Inject later receipt | Receipt sequence/time follows recorded close | `test_close_verifier_refuses_post_close_arm` |
| A6 | Mutate analysis A/B arms | Family marker remains unchanged | `test_census_comes_from_family_marker_not_analysis_arms` |

Collision handling: do not edit in-flight `joulewise/dominance_closeout.py`, `joulewise/analysis_manifest_v3.py`, `joulewise/bundle_read.py`, `scripts/dependence_sensitivity.py`, or `scripts/gen_g2*`; consume their published outputs by digest. The new arm-context field may require a later `gen_g2*` reconciliation, so serialize after that lane or request a separate exact scope. Keep `docs/process/state_kernel.json` lead-owned and reconcile it only after all three sessions.

### Q6 — Triage corrections and Ed-only facts [F3, F7]

The lieutenant is correct that the three row artifacts are absent: campaign-close has zero code/test/contract matches, fixation is prose-only, and A6 has no CLOSE computation.

The NR-13 answer is more exact: a shell publication guard is landed, and it is the only `COMMIT_FREEZE` implementation (`window_status.sh:34,95`); there is no Python guard. However, it writes `WINDOW_STATUS.md` at `:59-93` before checking the sentinel, and its regression explicitly expects that untracked write (`test_window_status_guard.py:49-64`). Thus it satisfies “no Git add/commit/push” but not literal “refuse-before-write” (`nr-synthesis-ruling.md:49-55`) unless the latter is reinterpreted; return that to the magistrate.

The row is stale: dependencies remain empty (`state_kernel.json:4536`), its goal still speaks in v4 terms (`:4555`), and its status note says `window_runbook.md` §11 is missing (`:4561`) even though §11 now begins at `window_runbook.md:2155` and §12 at `:2222`.

Ed need only supply external facts: the exact real v5 `$CAMPAIGN_ROOT`, `$CUSTODY_ROOT`, `$ARM_READINESS_CUSTODY_ROOT`, and sentinel override, plus confirmation that one transaction custody root persists across every arm/night. No hardware measurement or quiet-window assertion was attempted. Notification receipt format and freeze semantics are magistrate design decisions, not facts to delegate to Ed.

## Recommended rulings

1. **(a)** Rule that the authenticated family-publication marker is the sole arm census, and that an arm is LAST exactly when it is the sole marker member lacking a completed authenticated launch lineage.
2. **(b)** Rule that a pre-landed repository-managed pre-commit hook using the canonical campaign-close record is the refusal host for fixation-first, with CI/history validation only as a backstop.

## Residual risk

This was static inspection at a clean, read-only HEAD; no live external custody directory, Git-hook installation, notification provider receipt, or v5-generated artifact was available for verification.