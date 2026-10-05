# Block 4 terminal-refresh coverage: H → H′

2026-10-05. **DRAFT evidence recipe implementing lead ruling 76's terminal-refresh decision; no refresh, seal or arm performed.** Owning rule: registration V5-QUAL-25G83-B4 §12. Ruling 76 is prospective through that registration's cold Fable/independent Opus seal; Ed may veto. Actual H/H′/path digests are runtime bindings, not supplied by this document.

## Decision and evidence boundary

Ruling 76 settles coverage: **H′ = H + the reviewed terminal ledger-pin advance and re-authored readiness/freeze records is covered by `s1`'s qualification.** Executables, generated workload configs and chain sources remain unchanged. The packs pin acceptance cutoff, not live ledger head (Fable N4 on #477). This does not transfer qualification to a changed launch/measurement implementation.

`s1` runs at H; both structural and qualification PASS are required for downstream handoff. At physical-ahead STOP, preserve finalized session, `calibration_ledger_head_mismatch`, exact non-null terminal candidate and all collected bytes. The chain performs no pin advance, launch completion, binding/verdict or analysis finalization. Outside the quiet span, use the existing guarded `scripts/recover_calibration_ledger.py ... advance-head-pin --session-id ... --expected-sequence ... --expected-digest ... --operator-identity ... --attestation-reason ... --execute` against the authenticated exact candidate. Final integrated refresh/restaging invocation remains `FILL[TERMINAL-REFRESH-CLI]`; no guessed argv/path replaces it.

Preserve seed/terminal ledger bytes and hashes, replay `verify_custody=True`, commit only the reviewed pin and regenerated records at a clean reviewed head, re-author readiness, re-freeze/re-attest, and restage the exact ledger/pin pair. Repeat A2 byte comparisons and readiness/freeze authentication before continuation. No later arm consumes the pre-refresh freeze. Build bracket binding before the one authoritative verdict row; preserve actual desk completion/backups/close-out needed by G9. Harvest replays its required source pins; neither STOP nor a records commit proves PASS.

## Exact allowed changed-path classes

Only these three canonical pack roots may contribute refresh records:

- `configs/campaigns/d117_floor_qwen3-1p7b_v5/`
- `configs/campaigns/d117_floor_qwen3-8b_v5/`
- `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/`

Here `<pack>` means one of those roots. Directory classes must be expanded into the **exact reviewed producer-emitted leaf paths** for this refresh; they are not blanket directory write permissions.

| Allowed class | Content constraint |
|---|---|
| `configs/calibration/calibration_ledger_head.json` | Guarded advance to this block's exact authenticated terminal candidate only; seed/terminal custody retained. No acceptance/cutoff alteration. |
| `<pack>/arm_readiness.sources/**` | Re-authored source records/snapshots for readiness at refreshed head/pin. Registered executable/config snapshots must still equal the pinned unchanged implementation/config bytes; a `.py` copy here cannot hide changed executable semantics. |
| `<pack>/arm_readiness.evidence/**` | Re-authored readiness receipts and corresponding digest sidecars from existing pinned producers; unchanged predicates/registry/identity/acceptance. Preserve prior records in immutable custody before refreshing namespaces. |
| `<pack>/arm_readiness.freeze.receipts/freeze-NNNN.json` and matching `.json.sha256` | New reviewed freeze receipt/sidecar under existing ordinal/schema rules. Old freeze receipts remain immutable; no overwrite/delete/relabel of completed evidence. |
| `<pack>/plan_tree.json` and `<pack>/plan_tree.sha256` | **Only** the existing `/arm_attachments/arm_readiness/freeze_receipt` reference (path/sha256) and its mechanically recomputed sidecar may change. Reviewed freeze issuance writes these bindings (`joulewise/arm_readiness.py::generate_freeze_receipt`); no workload/calibration/roster/order/generator/acceptance/identity field may change. |

Complete pack-tree hashes may change because these records/reference bindings change; new hashes/freeze identities must be authenticated explicitly. Generated science/auxiliary configs, order manifests, generator inputs, calibration plans, pin/selection/ladder, model/tokenizer/identity projection, policies, acceptance/cutoff, row registry, production inventory, historical/family semantic bindings and executables are **not** refresh classes. Preserve them byte-for-byte. In particular, both Markdown chain sources (`docs/phase_2/window_runbook.md`, the G2 runsheet) are executable pins, never records-only allowances.

A separately permitted §12(iii) records-only `docs/`/`tests/`/RUN_STATE/TASK_QUEUE extension has its own exact reviewed map and must leave all pinned executables/configs/chain sources unchanged. It does not widen the terminal-refresh allowlist above. The maps must account for the entire H→H′ delta before any later arm; no unexplained intermediary commit is hidden by calling the last commit records-only.

## Changed-path check and replay record

Before **any later arm**, the lead records full H/H′ SHAs, proves H′ descends from H, authenticates `s1` qualification/source pins and checks the **whole** delta. Required command shape is **`git diff --name-only H H′` against an allowlist**, with H/H′ replaced by full recorded object IDs. For lossless paths and a pinned inventory, the reproducible form is:

```sh
git merge-base --is-ancestor "$QUALIFIED_H" "$REFRESHED_H"
git diff --name-only -z --no-renames "$QUALIFIED_H" "$REFRESHED_H" --
git diff --name-status -z --no-renames "$QUALIFIED_H" "$REFRESHED_H" --
git diff --no-ext-diff --no-renames "$QUALIFIED_H" "$REFRESHED_H" --
```

Use the NUL-delimited name list to compare exact paths with a reviewed allowlist, rejecting any path outside it. Inspect name-status/full diff for deletions, renames, mode changes or non-record mutations; path membership alone is insufficient. The checker/integration interface is `FILL[TERMINAL-REFRESH-CLI]`, not an invented executable. If separate §12(iii) records are included, classify them explicitly in their own allowlist/map and apply the same pinned-source exclusions.

`FILL[TERMINAL-REFRESH-CHANGED-PATH-MAP]` binds:

- every changed path, class, before/after SHA-256, create/update disposition, producer/command and reason; exact expanded allowlist and its digest;
- seed/terminal ledger/candidate/pin custody and sequence/head-digest replay, acceptance-cutoff equality and restaged A2 comparisons;
- new readiness/freeze paths/digests/attestation, preserved predecessor/history and fresh per-arm bindings; plan-tree semantic comparison excluding **only** the permitted freeze-reference pointer;
- before/after SHA-256 equality for all pinned executable/generated-config/chain-source/identity/acceptance inputs, and replay outcomes at clean H′;
- qualification verdict identity/digest, required harvest source pins and the lead's explicit coverage disposition before the later arm.

Working-tree/index/untracked state must not add execution changes outside the checked committed map. Retain old/new evidence immutably, keep raw metrics restricted under registration §10, and include no measured value in this draft.

## What forces a new seal or prospective coverage ruling

Automatic terminal coverage ends if any executable, generated workload/calibration config, chain source, policy, acceptance/cutoff, roster, identity or operating condition changes; if a plan-tree field beyond the freeze reference changes; or if a claimed record cannot be replayed under unchanged predicates/source pins. A path/hash outside the classified allowlists or an unauthenticated candidate prevents a later arm; first resolve a mapping/authentication fault without altering source bytes. An actual change outside §12's permissions requires **new design/seal**, never a wider after-the-fact allowlist.

A gated code-agrees-with-text R3 fix is the separate §12(ii) route, **not** a terminal refresh. If it changes a launch/measurement path exercised at H, the lead/cold gate must prospectively settle qualification coverage at its head before a fresh `s1`, allowed `s2` or claim arm; do not assert H qualified it. Rule/threshold/purpose/roster/recovery/blindness changes need a prospective cold erratum/new seal. R3 never overrides frozen-pack immutability, one-head requirements or the one-`s2`/`recover_no_science` rules. A code-head conflict needing new design follows §7 END STATE; no additional qualification night is authorized by this record.
