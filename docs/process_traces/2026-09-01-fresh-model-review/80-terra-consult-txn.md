```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The NR-13 sentinel is already landed, but `_v5` transfer, an authoritative consuming-arm census, and a universal first-post-freeze guard require magistrate rulings before this row can be installed.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "informational",
    "head_start": "3b0e23f0345fc630dbed497cf611758281020ed2",
    "head_end": "3b0e23f0345fc630dbed497cf611758281020ed2",
    "upstream_end": null,
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "summary": "The queued row remains explicitly `_v4`, while D-164/D-167 make `_v5` the live campaign; the existing publication-marker validator is hard-coded to `d117-v4` and its `_v4` roster."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "summary": "HEAD has no authenticated census connecting planned consuming arms to arm-receipt and completion records, so neither last-arm closure nor exact executed-set equality is computable."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "summary": "The only landed freeze guard protects `window_status.sh`; no repository-wide pre-commit/CI guard can refuse a bookkeeping commit as the first post-freeze commit."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "3b0e23f0345fc630dbed497cf611758281020ed2",
          "main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "main"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n -C 3 'COMMIT_FREEZE|commit.freeze|commit-freeze' joulewise scripts --glob '*.py' --glob '*.sh' --glob '*.zsh'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/window_status.sh:95:if [ -e \"$COMMIT_FREEZE_SENTINEL\" ]; then"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMMIT_FREEZE_SENTINEL"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The exact campaign-close schema, census authority, `_v5` parameter mapping, and generic commit-time enforcement host are not specified by D-153/D-155; choosing them would reinterpret the fenced shapes.",
      "needs": "Ratify the two recommended rulings below, including whether this row is formally re-homed from `_v4` to `_v5`."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The lieutenant's NR-13 absence claim is stale: the custody-external sentinel is implemented in scripts/window_status.sh and covered by tests/test_window_status_guard.py.",
      "needs": ""
    }
  ]
}
```

## Findings

- **B1 — `_v4` versus `_v5` is a real authority conflict.** D-164 says `_v4` is never collected and `_v5` is the same frozen-design regeneration (`docs/decision_log.md:10365-10374`); D-167 makes `_v5` live (`:10407-10418`). Yet the row still demands `_v4` artifacts (`docs/process/state_kernel.json:4517-4561`), and the marker validator requires `family_id == "d117-v4"` (`joulewise/arm_readiness.py:10773-10778`) plus the old three-pack roster (`:10850-10856`).

- **B2 — no arm census exists.** The changed-set code only diffs `derivation_commit..current_head` (`joulewise/arm_readiness.py:4534-4582`) and validates path allowlisting (`:4726-4768`). It has no close endpoint or campaign ledger. Existing order manifests enumerate planned runs (`configs/campaigns/d117_contrast_v5/generate_configs.py:3097-3173`), not readiness-arm receipts.

- **S1 — NR-13 is landed but narrow.** `scripts/window_status.sh:34,95-107` checks the external sentinel before `git add`; `tests/test_window_status_guard.py:49-86` exercises guarded and normal branches. It cannot stop a direct `git commit` of bookkeeping.

## Q1

Recommendation: ratify a canonical external-custody schema, then write it at real-transaction runbook H5 step 1 (`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1297-1306`).

Proposed schema — **NEEDS-RULING** because D-155 adopts the artifact but does not prescribe its keys or schema id:

```json
{
  "schema_version": "joulewise.campaign_close.v1",
  "campaign_id": "string",
  "published_marker": {"path": "string", "schema_version": "string", "sha256": "64-lower-hex", "publication_head": "git-oid"},
  "published_campaign_arm_plan": {"path": "string", "schema_version": "string", "sha256": "64-lower-hex"},
  "expected_arms": [{"campaign_arm_id": "string", "ordinal": "positive-int", "pack_id": "string"}],
  "executed_arms": [{
    "campaign_arm_id": "string",
    "arm_receipt": {"receipt_id": "string", "path": "string", "sha256": "64-lower-hex"},
    "consumption": {"consumption_id": "string", "path": "string", "sha256": "64-lower-hex", "consumed_at_utc": "RFC3339"},
    "completion": {"path": "string", "sha256": "64-lower-hex", "completed_at_utc": "RFC3339"}
  }],
  "last_consuming_arm": {"campaign_arm_id": "string", "arm_receipt_id": "string", "ordinal": "positive-int"},
  "supporting_artifacts": {
    "slot_ledger": {"path": "string", "sha256": "64-lower-hex"},
    "whole_window_verdict": {"path": "string", "sha256": "64-lower-hex"},
    "bracket_binding": {"path": "string", "sha256": "64-lower-hex"}
  },
  "predicate": {"expected_ids": ["string"], "executed_ids": ["string"], "missing_ids": ["string"], "unexpected_ids": ["string"], "equal": true},
  "recorded_at_utc": "RFC3339"
}
```

Every `sha256` is of the referenced raw canonical artifact bytes; it is not a Git object hash. The writer must reject noncanonical JSON, duplicate IDs, mismatched hashes, unequal sets, a non-final `last_consuming_arm`, absent consumption/completion, or a record outside the transaction custody root.

The custody convention is explicitly external to the repository (`real-transaction-runbook.md:164-168`); the existing sentinel default exemplifies that root convention at `/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN` (`scripts/window_status.sh:32-35`). The actual `_v5` custody root is an Ed machine fact.

At HEAD, the executed set comes from **no single producer**. `order_manifest.json` is a frozen planned `executed_order`, not runtime execution; the `_v5` flow’s `campaign_log.jsonl` and whole-window verdict record collection outcomes (`docs/process/v5-artifact-flow.md:10`), but neither is a declared arm census. Consumption records do carry arm receipt id/path/hash (`joulewise/arm_readiness.py:2592-2599`), so they are the correct execution evidence once joined to a newly frozen census.

Mechanically check order with an append-only close transcript: canonical close-record digest → freeze-off event → notification payload/delivery digest → fixation commit parent-chain proof → bookkeeping. Do not order by wall-clock time alone. A pre-commit check must require `HEAD == close.pre_fixation_head` and staged content equals the fixation delta. Regression counterfactual: stage a `RUN_STATE.md` bookkeeping commit first; it must refuse before Git writes a commit, and an offline validator must reject its history if the hook was bypassed. This transcript and hook mechanism are also **NEEDS-RULING** details, not a change to NR-8’s ruled order.

## Q2

Recommendation: keep the A1 literal as a tracked test pin, not a sidecar. The current test pin pattern is `PINSET_SHA256` (`tests/test_receipt_histsem.py:45,200-201`); the refresh tool recognizes exactly one such literal (`scripts/refresh_receipt_histsem_pinset.py:37-38,426-438`) and prints the computed digest (`:715-718`).

The current pin is for the older `PINSET`, while the successor has only a path and prose declaration (`tests/test_receipt_histsem.py:56-60,231-249`). Therefore the fixation commit should add a dedicated successor-pin test containing exactly one literal and `sha256(SUCCESSOR_PINSET bytes) == literal`; a one-nibble mutation then fails that test. `--write-test-pin` cannot directly author a second differently named literal, so either a dedicated test file using the existing exact name or a pre-window tool extension is required — **NEEDS-RULING** on the former’s file/format.

“Loud-fail” needs two distinct mechanisms:

1. The committed successor-pin test fails on any literal/digest mismatch.
2. A pre-existing transaction-close pre-commit hook refuses a non-fixation staged commit while the close record names the current parent as `pre_fixation_head`.

There is no existing hook or `core.hooksPath` implementation at HEAD. CI or a post-commit test only detects, not refuses, the forbidden first commit. The hook host and activation procedure are **NEEDS-RULING**, while the semantic requirement that fixation is first is already ruled by A1/NR-8 (`real-transaction-runbook.md:1307-1315`).

## Q3

Recommendation: choose a declared, ordered, published **campaign-arm census**, not a pack count. A count cannot identify the terminal receipt or reject an extra arm.

Candidate sources at HEAD are insufficient:

- `_v5` generator plan lists experimental condition arms A/B under decode/prefill (`generate_configs.py:1828-1837`), not readiness-arm receipt IDs.
- Root/stage order manifests list planned run configurations and `executed_order` (`:3097-3173`), not consuming-arm identities.
- The prospective analysis manifest references root/stage manifests and member runs (`:2525-2543`, `:2487-2499`), again not readiness-arm receipts.
- Campaign policy governs runtime conditions; it is not an arm census.

The authoritative source should be a new frozen `campaign_arm_plan` with stable `campaign_arm_id`, ordinal, pack, and bound stage/order-manifest references, whose digest is authenticated by publication. Each consuming arm then records its plan ID into the existing arm/consumption chain. This changes the marker or frozen-pack contract and is therefore **NEEDS-RULING**.

The arm-time gate must consult this plan plus append-only custody before `generate_arm_receipt` reaches its exclusive write (`joulewise/arm_readiness.py:8182-8209,8419-8425`). It refuses an unplanned ID, a non-next ordinal, or any arm after a close record names the final ordinal. Regression: append a valid close record, then attempt ordinal `last+1` (or a later recorded sequence/timestamp); assert refusal before any arm receipt exists. Reusing `readiness_r1_dependency_changed_set` for this would be semantically misleading; the exact reason-code disposition is also unruled.

## Q4

- `campaign-close.json`: the schema shape can transfer, but `_v5` campaign id, marker reference, pack IDs, census, and custody root are parameters. Current hard-coded `_v4` marker validation means this is not a purely data-only parameterization.
- A1 fixation: “first post-freeze commit carries exactly `hS` plus loud failure” transfers semantically. The successor pinset path/name and `hS` do not transfer unchanged: current code names `legacy_receipt_histsem_pinset_v4_v1.json` (`tests/test_receipt_histsem.py:56`). Creating a `_v5` successor chain requires a ruling.
- A6 endpoints transfer unchanged: open at evidence derivation, close at final consuming arm. The actual `_v5` census and IDs are new transaction parameters.
- The `_v4` S-0 clone proof is historical proof only, not an executed claim-bearing arm; it must not enter `_v5` executed-set equality. D-164’s regeneration language (`docs/decision_log.md:10370-10374`) supports no carry-forward of `_v4` custody facts.

## Q5

Use three sequential sessions after the rulings; do not parallelize them.

| Session | Exhaustive WRITE_SCOPE |
|---|---|
| A6 census/gate | `joulewise/arm_readiness.py`; `scripts/generate_arm_readiness.py`; `configs/campaigns/d117_contrast_v5/generate_configs.py`; `tests/test_arm_readiness_integration.py`; `tests/test_d117_contrast_v5_pack.py`; new `docs/contracts/campaign_arm_census.md`; `docs/process/v5-artifact-flow.md`; `docs/phase_2/window_runbook.md`; `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` |
| NR-8 close artifact | new `joulewise/campaign_close.py`; new `scripts/declare_campaign_close.py`; new `tests/test_campaign_close.py`; new `docs/contracts/campaign_close.md`; `docs/process/v5-artifact-flow.md`; `docs/phase_2/window_runbook.md`; `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` |
| A1 fixation | new `scripts/validate_transaction_fixation.py`; new `tests/test_transaction_fixation.py`; `tests/test_receipt_histsem.py`; new `docs/contracts/transaction_fixation.md`; `docs/process/v5-artifact-flow.md`; `docs/phase_2/window_runbook.md`; `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` |

The proposed contract names follow existing lower-snake-case convention, e.g. `docs/contracts/receipt_histsem_verifier.md`.

Demand these regressions:

| Artifact | Mutation | Counterfactual | Failing test |
|---|---|---|---|
| Close | Change an artifact hash or add an unexpected arm | Claimed execution differs from custody/plan | `test_campaign_close_refuses_hash_or_set_mismatch` |
| A1 | Flip one hex nibble; stage bookkeeping first | Literal differs; first post-freeze commit is not fixation | `test_successor_pin_one_nibble_fails`; `test_fixation_hook_refuses_bookkeeping_first` |
| A6 | Add arm ordinal after recorded close | Arm timestamp/sequence follows close | `test_campaign_arm_gate_refuses_after_close_before_write` |

No proposed scope touches the named in-flight lanes `joulewise/dominance_closeout.py`, `joulewise/analysis_manifest_v3.py`, `joulewise/bundle_read.py`, `scripts/dependence_sensitivity.py`, `scripts/gen_g2*`, or `docs/process/state_kernel.json`. Do not add the kernel to any delegated scope.

## Q6

The lieutenant is correct that A6 has only an OPEN-side changed-path check and no last-consuming-arm computation. But “all three absent” is overbroad: NR-13 is implemented and regression-tested at `scripts/window_status.sh:34,95-107` and `tests/test_window_status_guard.py:49-86`.

Send Ed only these machine/custody questions:

1. What exact external `_v5` transaction-custody root and append-only transcript location will exist on the measurement machine?
2. What locally enforceable hook-installation path is acceptable in that measurement checkout, and how will its activation be recorded in custody?

## Recommended rulings

- **(a)** Ratify an explicit ordered `_v5` campaign-arm census, authenticated at publication and joined to real arm/consumption/completion receipts, as the sole source for A6 last-arm closure and NR-8 equality.

- **(b)** Ratify a transaction-close pre-commit hook, activated before evidence derivation, that permits only the exact `hS` fixation delta as the first post-freeze commit while retaining the committed successor-pin test as the durable loud-fail guard.