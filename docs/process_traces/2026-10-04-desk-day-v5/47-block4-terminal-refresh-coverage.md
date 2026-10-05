# Record 47: which head changes after `s1` stay covered by its qualification (H → H′)

2026-10-05, desk-day seat 2 (Opus 5.5). Implements ruling 76's terminal-refresh decision for registration
V5-QUAL-25G83-B4 §12. Draft until that registration is sealed. No refresh, seal or arm is performed here.

## The decision

`s1` runs at head H and stops at physical-ahead, keeping the exact terminal ledger candidate. After the quiet
window, the governed desk step advances the ledger pin to that candidate and re-authors readiness and freeze
records. That produces a new head H′. H′ is covered by `s1`'s qualification **if and only if** the only things
that changed are the ledger pin and those re-authored records. The reason it can be covered at all: the `_v5`
packs pin the acceptance cutoff (sequence 376), not the live ledger head (Fable N4 on #477), so a ledger advance
does not change a single generated config, executable or chain source.

## How the pin moves

Only through the existing guarded command, against the authenticated candidate in the boundary record:

```sh
"$PY" scripts/recover_calibration_ledger.py --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  advance-head-pin --session-id "$BRACKET_SESSION_ID" \
  --expected-sequence "$CANDIDATE_SEQUENCE" --expected-digest "$CANDIDATE_DIGEST" \
  --operator-identity "$OPERATOR_IDENTITY" --attestation-reason "reviewed exact G2-b terminal candidate" --execute
```

Then: keep the seed and terminal ledger bytes and hashes; replay with `verify_custody=True`; commit only the pin
and the regenerated records at a clean reviewed head; re-author readiness; re-freeze and re-attest; restage the
exact ledger and pin pair; repeat the runsheet's A2 byte comparisons. No later arm uses the pre-refresh freeze.
The integrated wrapper is `FILL[TERMINAL-REFRESH-CLI]`.

## The allowlist

`<pack>` is one of `configs/campaigns/d117_floor_qwen3-1p7b_v5/`, `configs/campaigns/d117_floor_qwen3-8b_v5/`,
`configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/`. Directory classes are expanded to the exact leaf
paths the producers wrote; they are not blanket permissions.

| Path class | What may change |
|---|---|
| `configs/calibration/calibration_ledger_head.json` | The guarded advance to this block's authenticated terminal candidate. Acceptance and cutoff unchanged. |
| `<pack>/arm_readiness.sources/**` | Re-authored source snapshots. Any snapshot of an executable or config must still equal the pinned bytes. |
| `<pack>/arm_readiness.evidence/**` | Re-authored readiness receipts and digest sidecars from the pinned producers; prior records kept in immutable custody. |
| `<pack>/arm_readiness.freeze.receipts/freeze-NNNN.json` and its `.sha256` | A new freeze receipt under the existing ordinal rules; old receipts never overwritten. |
| `<pack>/plan_tree.json`, `<pack>/plan_tree.sha256` | Only the `/arm_attachments/arm_readiness/freeze_receipt` reference and the recomputed sidecar (written by `joulewise/arm_readiness.py::generate_freeze_receipt`). |

Everything else stays byte-identical: generated science and auxiliary configs, order manifests, generator inputs,
calibration plans, the pin bundle, model and identity projections, policies, the acceptance, the row registry,
the production inventory and every executable. The two Markdown chain sources (`docs/phase_2/window_runbook.md`
and the G2 runsheet) are executable pins and are never on this list. A separate records-only extension under
§12(iii) (`docs/`, `tests/`, RUN_STATE, TASK_QUEUE) has its own map and does not widen this one.

## The check, before any later arm

```sh
git merge-base --is-ancestor "$QUALIFIED_H" "$REFRESHED_H"
git diff --name-only -z --no-renames "$QUALIFIED_H" "$REFRESHED_H" --
git diff --name-status -z --no-renames "$QUALIFIED_H" "$REFRESHED_H" --
```

Every path in the first list must be on the expanded allowlist; the name-status list is read for deletions,
renames and mode changes, which are not allowed. `FILL[TERMINAL-REFRESH-CHANGED-PATH-MAP]` records each changed path
with its class, before and after SHA-256, producer and reason; the ledger custody replay and cutoff equality; the
new readiness and freeze digests; byte equality of every pinned executable, generated config, chain source,
identity and acceptance; the plan-tree comparison excluding only the freeze reference; and the qualification
verdict's identity. Uncommitted or untracked files cannot carry execution changes past this map.

## What ends automatic coverage

Any change to an executable, generated config, chain source, policy, acceptance or cutoff, roster, identity or
operating condition; any plan-tree change beyond the freeze reference; any record that does not replay under the
unchanged predicates. Such a change needs a new seal, never a wider allowlist after the fact. An R3 code fix is a
different route (§12(ii)): if it touches a launch or measurement path that `s1` exercised, the lead and a cold gate
decide coverage before a fresh `s1`, the `s2` or any claim arm.
