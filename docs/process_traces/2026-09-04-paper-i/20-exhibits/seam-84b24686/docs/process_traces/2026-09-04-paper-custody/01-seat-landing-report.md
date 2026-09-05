# PAPER-CUSTODY-SEAM-01 implementation-seat landing report

Date: 2026-09-04. Base: `a51eea69`. Branch:
`feat/2026-09-04-paper-custody-seam`. No commit was created.

## Outcome

The five-family `open_paper_input(ref)` seam is implemented against
non-issuing synthetic fixtures. Governed files authenticate against Git blobs;
generated files authenticate through a Git-anchored custody inventory. A
receipt corroborates independently anchored bytes and must equal fresh replay.
Every file is reopened through the same no-follow session before a frozen
verified type can be constructed.

Whole-window validation now has a typed authenticity/admission result, but the
family remains deliberately blocked with
`paper_custody_blocked_pending_receipt`. The D-165 adapter maps its four owning
validators into closed non-renderable codes. Lower floor-extraction reads now
join the active authentication census. The authentication-surface and public
signature guards cover the seam.

## API → family → refusal-code table

| API | Family | Successful fixture type or terminal code | Attack codes |
|---|---|---|---|
| `open_paper_input(ReportedEnergyParentsRef)` | D-123 parents | `VerifiedReportedEnergyParents` (non-issuing) | raw `paper_custody_digest_mismatch`; reseal `paper_custody_anchor_mismatch`; reopen `paper_custody_input_changed` |
| `open_paper_input(D165CloseoutRef)` | D-165 close-out | `VerifiedD165Closeout` (non-issuing) | raw `paper_custody_digest_mismatch`; reseal `paper_custody_anchor_mismatch`; reopen `paper_custody_input_changed` |
| `open_paper_input(WholeWindowVerdictRef)` | whole-window row | `paper_custody_blocked_pending_receipt` | raw `paper_custody_digest_mismatch`; reseal `paper_custody_anchor_mismatch`; reopen `paper_custody_input_changed` |
| `open_paper_input(ClaimEvidenceRef)` | claims v1 + sidecar | `VerifiedClaimEvidence` (non-issuing) | raw `paper_custody_digest_mismatch`; reseal `paper_custody_anchor_mismatch`; reopen `paper_custody_input_changed` |
| `open_paper_input(TransferProjectionRef)` | transfer projection | `VerifiedTransferProjection` (non-issuing) | raw `paper_custody_digest_mismatch`; reseal `paper_custody_anchor_mismatch`; reopen `paper_custody_input_changed` |

All refusals carry zero rendered output. Nested validator codes remain
diagnostic and do not appear in the exception string.

## Red then green

The census test was run before implementation and failed to import
`joulewise.paper_custody`. After the seam landed, the same command passed all
five family subtests and their dynamically enumerated records.

## Verification

Permitted commands are recorded in the runner envelope. The repository-wide
suite was not run because the mission's preflight rule expressly forbids it.

## Scope boundary

The adjudication packet's two exact lower bypasses remain outside this seat's
write authority: `joulewise/analysis_engine/inputs.py::load_floor_artifact`
degrades authenticated floor evidence to a mapping/digest pair, and
`joulewise/campaign_provenance.py::load_campaign_log_rows(..., raw_bytes=...)`
accepts caller-substituted log bytes. Their existing test modules are likewise
outside the allowlist. No edit was made to those paths; the smallest completion
scope is those two modules plus their existing tests.

## Artifact custody

No existing frozen fixture was edited. The only added fixture is a catalog
under `tests/fixtures/paper_custody/`; it declares synthetic non-measurement
content. The pre/post digest proof is recorded in the runner envelope.
