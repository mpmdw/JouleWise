```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt one non-bypassable paper-input custody reader; both current landings remain unfit because caller-supplied digests and PASS receipts can seal caller-authored values.",
  "workspace": {"base_requested":"5827379c0c927ac4bad2a8c460f138b2a462d331","base_mode":"exact","head_start":"5827379c0c927ac4bad2a8c460f138b2a462d331","head_end":"5827379c0c927ac4bad2a8c460f138b2a462d331","upstream_end":"5827379c0c927ac4bad2a8c460f138b2a462d331","branch":null},
  "pathspec": ["docs/process_traces/2026-09-04-paper-i/11-custody-seam-consult-sol.md"],
  "unowned_dirty": ["docs/process_traces/2026-09-04-paper-i/11-blind-fable-custody-read-seam-seat.md","docs/process_traces/2026-09-04-paper-i/12-custody-seam-consult-opus.md"],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","text":"D-123 and D-165 still let the caller choose both evidence bytes and their seals; neither branch may be a paper-value ingress."},
      {"id":"F2","severity":"should_fix","text":"All paper suppliers need one path/digest/receipt reader that replays existing validators and returns sealed typed objects."},
      {"id":"F3","severity":"should_fix","text":"The cross-supplier custody rule changes the claim-to-prose trust boundary and requires a decision-log entry."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git rev-parse HEAD origin/feat/2026-09-04-paper-i-scout feat/2026-09-04-d123-reported-mean origin/feat/2026-09-04-d123-reported-mean feat/2026-09-04-d165-outcome-renderer origin/feat/2026-09-04-d165-outcome-renderer | uniq","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["5827379c0c927ac4bad2a8c460f138b2a462d331","b72bbc359bc66fb69000aedfad363dbce1c583ad","d79d2883fdfce45597e53eb3bbc9072efc573370"]},"expected":{"exit_code":0,"tail_regex":"5827379c[0-9a-f]+\\nb72bbc35[0-9a-f]+\\nd79d2883[0-9a-f]+"}},
    {"id":"V2","kind":"inspection","cmd":"awk '/[ \\t]+$/ {bad=1} END {exit bad}' docs/process_traces/2026-09-04-paper-i/11-custody-seam-consult-sol.md && test $(wc -c < docs/process_traces/2026-09-04-paper-i/11-custody-seam-consult-sol.md) -lt 12288 && echo REPORT_FORMAT_OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REPORT_FORMAT_OK"]},"expected":{"exit_code":0,"tail_regex":"^REPORT_FORMAT_OK$"}}
  ],
  "flags": [
    {"id":"FL1","kind":"environment","level":"nonblocking","text":"git fetch could not write this linked worktree's FETCH_HEAD under the sandbox; the pre-existing local and origin refs are byte-identical at the heads inspected.","needs":"Lead may refresh refs outside the sandbox if remote movement is suspected."},
    {"id":"FL2","kind":"verification_gap","level":"nonblocking","text":"No tests ran; the preflight permits tests only to confirm a claim, and this was an inspection/design consult.","needs":"Implement the single mutation pattern below with the seam."}
  ]
}
```

## Findings

### F1 — blocker — the seal is still owned by the claimant

Both failures have the same shape. D-123's `_wrapped_document` accepts an embedded document and its adjacent digest without opening `path` (`feat/2026-09-04-d123-reported-mean`, `joulewise/reported_phase_energy.py:308-329`); its member loader reads selected artifacts but never calls the strict bundle validator (`joulewise/floor_extraction.py:1846-1995`). D-165 opens files, but `_authenticated_closeout_path` trusts a receipt whose only producer is the test helper that hashes the same caller files and writes `status: PASS` (`feat/2026-09-04-d165-outcome-renderer`, `joulewise/results_fill_outcome.py:337-419`; `tests/test_results_fill_outcome.py:270-319`). A path and digest supplied by the same caller prove stability, not issuance.

I disagree with trace 07's D-165 `LANDABLE` verdict and fix-round 3's claim that path/digest/PASS-receipt closed R4-S2; trace 10 is decisive. Addendum 07's “structured results” are insufficient without a producer-owned receipt anchor. D-123 fix round 2 also under-installs addendum 08, which requires validating the frozen spec and every bundle, not a self-hashed wrapper plus partial reads. The rulings' fail-closed intent, refusal scope, registered prose, stage order, and producer-only derivation stand.

### F2 — should-fix — one shared seam

Create `joulewise/paper_custody.py`. Its only public read operation is an overloaded function:

```python
@overload
def read_paper_input(ref: ReportedEnergyParentsRef) -> Verified[ReportedEnergyParents]: ...
@overload
def read_paper_input(ref: D165CloseoutRef) -> Verified[D165CloseoutEvidence]: ...
@overload
def read_paper_input(ref: WholeWindowVerdictRef) -> Verified[WholeWindowVerdictEvidence]: ...
@overload
def read_paper_input(ref: ClaimEvidenceRef) -> Verified[ClaimEvidence]: ...
@overload
def read_paper_input(ref: TransferProjectionRef) -> Verified[TransferProjectionEvidence]: ...
```

`BoundFile(path: Path, expected_sha256: str, role: InputRole)` and `ReceiptRef(file: BoundFile, schema: str, validator: str, validator_source_sha256: str)` are locator types. Each family ref has closed named files and one receipt—never `Mapping`, `bytes`, `Any`, an arbitrary list, or normalized content. Private-constructor `Verified[T]` contains the frozen family value, verified receipt/validator digests, and `tuple[VerifiedDigest(role, normalized_path, sha256, read_count), ...]`. Public suppliers accept refs and invoke the seam; only private helpers see `Verified[T]`.

Each call starts a fresh `V2AuthenticationReadSession`, uses no cache, rejects escaping/symlink paths, opens regular files with `O_NOFOLLOW`, hashes before strict parse, and checks the supplied digest. The session records first digest/read count (`joulewise/authentication_io.py:319-424`) and provides contained no-follow reads (`:426-452,575-587`). A receipt is corroboration, not a capability: it is producer-owned, independently pinned by the issuance handoff, binds every file and validator-source digest, and must match fresh replay; bare `status: PASS` is ignored. Reopen all files after replay before constructing `Verified[T]`.

Exact codes: `paper_custody_request_invalid`, `paper_custody_path_refused`, `paper_custody_input_unreadable`, `paper_custody_digest_mismatch`, `paper_custody_parse_invalid`, `paper_custody_receipt_unissued`, `paper_custody_receipt_invalid`, `paper_custody_receipt_binding_mismatch`, `paper_custody_validator_refused`, `paper_custody_derivation_mismatch`, `paper_custody_evidence_ambiguous`, `paper_custody_input_changed`. `PaperCustodyRefusal` carries `code`, `input_role`, and non-public `validator_codes`; its detail never renders.

Family routing is closed as follows.

- **D-123 parents.** `ReportedEnergyParentsRef` names spec, extraction report, whole-window basis, G2-a selection, prompt pin, and a receipt inventorying every bundle artifact. Replay `validate_extraction_spec` (`joulewise/floor_extraction.py:1007-1035`), `validate_d117_mint_consumption_report` (`:1599-1615`), `BundleReader.problems()` per member (`feat/2026-09-04-d123-reported-mean`, `joulewise/bundle_read.py:785-853`), then `load_reported_phase_energy_member` (`joulewise/floor_extraction.py:1846-1995`). Factor G2-a/prompt-pin checks into public validators. Return the exact ordered universe/digests; keep `_derive_reported_energy_projection` as consumer.
- **D-165 close-out.** `D165CloseoutRef` names close-out, finalized manifest, floor artifact, replay sidecar, and a producer-owned validation receipt. Replay `validate_finalized_analysis_manifest_v3` (`joulewise/analysis_manifest_v3.py:4403-4454`), `authenticate_floor_artifact_bytes` (`joulewise/analysis_engine/inputs.py:868-903`), `validate_d165_replay_sidecar` (`joulewise/dominance_closeout.py:845`), and `validate_d165_closeout` (`:1713-1779`). No positive object issues until a non-test receipt producer binds the registered cell identities; otherwise `paper_custody_receipt_unissued`.
- **Whole-window row.** `WholeWindowVerdictRef` names runs root, log, standalone row, prospective manifest, plan tree, and receipt. Require writer-exact bytes once in the log; replay `validate_prospective_analysis_manifest_v3` (`joulewise/analysis_manifest_v3.py:2932-2975`), `load_authenticated_campaign_manifest` (`joulewise/campaign_provenance.py:649-687`), and `whole_window_refusal_reasons` (`joulewise/whole_window.py:5525-5713`). Until `WHOLE-WINDOW-STOP-RECEIPT-01` distinguishes source-valid/admission-failed, return `paper_custody_receipt_unissued`.
- **Claims.** `ClaimEvidenceRef` names `claim_verdicts.v1`, `claim_side_bound.v1`, the finalized manifest, and receipt. Replay `validate_claim_verdicts(value, frozen_manifest=manifest)` (`feat/2026-09-04-gamma-claim-renderer`, `joulewise/analysis_engine/artifact.py:945-973`); that validator already authenticates the embedded floor bytes at `:1018-1060`. Then replay `validate_claim_side_bound(..., claim_verdicts_bytes=...)` and its exact projection join (`joulewise/claim_side_bound.py:166-269`). Return typed contrasts and bound rows indexed only after exact census/identity checks.
- **Transfer.** `TransferProjectionRef` names result projection, reviewed capture, plan, pre-data receipt, pulse-bound source, bundle inventory, and result-validation receipt. Replay `validate_transfer_fiducial_result` (`feat/2026-09-04-transfer-result-renderer`, `joulewise/results_fill_transfer.py:455-586`) and require exact recomputation from the authenticated capture. That derivation producer/validator does not yet exist—the current renderer accepts result bytes directly at `:638-668`, and the capture remains fenced—so the seam must return `paper_custody_receipt_unissued` until both land; self-consistency of the projection is insufficient.

One pattern closes the class: `test_every_paper_input_byte_is_custody_gated` table-drives all five public entry points and bound files. After a valid baseline, flip each byte while retaining the frozen digest and require `PaperCustodyRefusal(code="paper_custody_digest_mismatch", input_role=<role>)`, with no fills/tokens/prose. Its reseal mode changes each derived child/receipt while parents stay fixed and requires `paper_custody_derivation_mismatch` (or stale-seal `paper_custody_receipt_binding_mismatch`), proving an oracle below the outer digest gate. Replacement between replay and reopen yields `paper_custody_input_changed`.

In D-123, delete public `source_material -> source -> artifact -> issuance` byte/object ingress: wrapper helpers/keys, generic `build_*(bytes)`, `source_bytes_by_role`, and artifact-sequence token input. Keep final v1 schemas/IDs/validators, refusal scopes, math, role cardinality, deterministic projection, and formatting; make the CLI take explicit refs.

In D-165, delete local bound readers/adapters, its receipt schema, and the 20-keyword ingress. Keep structured result/refusal, before-first stage order, reason map, identity pins, OB/OR formatting, and prose hygiene. The renderer takes only `WholeWindowVerdictRef | None` and `D165CloseoutRef | None` and calls the seam.

### F3 — should-fix — decision authority

Yes, this needs a new decision-log entry (lead assigns the D-number). It changes how every claim-bearing or professor-facing value crosses from evidence custody into prose, supersedes the permissive readings of R1-5/R4-F1/R4-S2, makes producer-owned replayable receipts mandatory, and records that path+digest pairs from one caller are not issuance authority. The entry should also gate `RENDERER-V5-SUCCESSOR-01` and the transfer/whole-window receipt missions on this seam.

## Residual risk

The seam cannot manufacture a trust root. D-165 close-out, whole-window stop, and transfer projection lack governed receipt/derivation producers and remain structured refusals. Available matching local/origin refs were inspected after sandboxed fetch failed; no behavior tests ran.
