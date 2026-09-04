# Paper supply custody

Status: normative for `PAPER-CUSTODY-SEAM-01`; D-173 remains provisional
until the paper-supply cold gate. This is the single normative home for the
paper custody-read boundary.

## Terms

A **paper supplier** is code that turns analysis evidence into a paper fill,
table row, token, or professor-facing sentence. The **custody seam** is the
single function that admits evidence to such a supplier:
`joulewise.paper_custody.open_paper_input(ref)`.

A **governed file** is a repository file whose authority is the byte-exact
blob at clean `git:HEAD`. A **generated file** is an output outside that
governed set. It has authority only through a custody inventory that is itself
a governed Git blob. An inventory names each file's closed role, relative
path, SHA-256 digest, and authority class.

An **anchor** is that independent Git blob or inventory entry. A **pin** is a
path or expected digest carried by a caller. A pin makes substitution loud but
does not authorize content. A **receipt** is a producer record corroborating
the anchored inputs and one validator replay. A receipt never acts as a
capability by itself.

A **fresh replay** runs the owning validator in the current process over the
bytes just read. A **reopen** reads every input again after replay. A **family
ref** is one of the five closed locator types below. A **verified type** is the
matching frozen, non-container result. **Issuance** means releasing a result
that may authorize paper text; test fixtures are always non-issuing.

## Only public read operation

`open_paper_input(ref)` accepts exactly one of these concrete types and returns
the matching concrete type:

| Family ref | Verified result | Paper use |
|---|---|---|
| `ReportedEnergyParentsRef` | `VerifiedReportedEnergyParents` | D-123 reported-energy parents |
| `D165CloseoutRef` | `VerifiedD165Closeout` | D-165 dominance close-out |
| `WholeWindowVerdictRef` | `VerifiedWholeWindowVerdict` | whole-window verdict row |
| `ClaimEvidenceRef` | `VerifiedClaimEvidence` | `claim_verdicts.v1` plus `claim_side_bound.v1` |
| `TransferProjectionRef` | `VerifiedTransferProjection` | transfer-fiducial projection |

Raw readers, parsers, replay dispatch, payloads, and verified-object
construction are private. No supplier entry accepts bytes, a dictionary or
mapping, an arbitrary sequence, a role string, a receipt, a validation result,
or a pre-validated object. The verified types are distinct frozen dataclasses
with private payloads and a frozen custody-evidence census.

`BoundFile(path, expected_sha256, role)` is a locator and pin.
`ReceiptRef(file, schema, validator, validator_source_sha256)` locates the
corroborating receipt. Neither is authority.

## Closed family wires

Every ref carries one root directory, one governed custody inventory, its
closed named inputs, and one `ReceiptRef`.

| Family | Required named inputs |
|---|---|
| Reported energy | extraction spec; extraction report; whole-window basis; G2-a selection; prompt pin; validator receipt |
| D-165 close-out | close-out; finalized manifest; on-disk floor artifact; replay sidecar; validator receipt |
| Whole window | canonical campaign log; standalone verdict; prospective manifest; plan; validator receipt |
| Claims | `claim_verdicts.v1`; `claim_side_bound.v1`; finalized manifest; authoritative on-disk floor artifact; validator receipt |
| Transfer | result projection; reviewed capture; plan; pre-data receipt; pulse-bound source; bundle inventory; result-validation receipt |

Paths are root-relative POSIX paths. Absolute paths, empty components,
traversal components, backslash aliases, duplicate paths, duplicate roles,
symlinks, and non-regular files refuse. Each JSON or JSONL input is decoded as
strict UTF-8 with duplicate keys and non-finite numbers refused.

## Authority and read algorithm

For every call, the seam performs these steps in order:

1. Require the ref's root to be exactly the Git worktree root.
2. Start a new `V2AuthenticationReadSession`; no prior cache can satisfy the
   call.
3. Read the custody inventory as a contained regular file without following
   symlinks. Check the caller pin, then require byte equality to its `git:HEAD`
   blob.
4. Read every named file the same way and check its caller pin. For a governed
   file, also require equality to its Git blob. For a generated file, require
   equality to the digest reached through the anchored inventory.
5. Require a canonical, closed receipt with `status: PASS`. It must name the
   family validator and current validator-source digest and bind every input's
   role, path, and exact digest.
6. Replay the owning validators over the bytes read in this call. Validator
   errors remain nested diagnostics and can never become rendered prose.
7. Require byte-exact agreement between the receipt and fresh replay.
8. Reopen every input with the same no-follow read. Any replacement, removal,
   parse change, or digest change refuses.
9. Construct the matching verified type privately. Production inventories are
   registered only by the owning producer mission. A fixture inventory has
   mode `test_fixture_non_issuing` and sets `issuance_authorized` false.

Caller updates to a path, digest, content ID, sidecar, or receipt cannot update
the independent Git or inventory anchor. A caller-authored `PASS` receipt is
therefore corroboration of nothing and cannot issue a value.

## Family replay rules

Reported-energy replay validates the governed extraction spec and D-117 mint
consumption report. A production registration must additionally inventory the
exact ordered `reported_energy_cells[].members` universe and every artifact
strict bundle validation reads. The reported-energy projection is derived by
the trusted consumer; it is never accepted as source material.

D-165 replay validates the finalized manifest, on-disk floor artifact, replay
sidecar, and close-out. Its adapter returns only four closed nested codes, one
per owner; validator exception text is not part of the paper refusal
vocabulary. The full governed stack identity, including
`tokenizer_json_sha256`, is checked by the owning identity validator.

Whole-window replay uses the typed `WholeWindowRowValidation` result, which
separates authenticity from an admission failure. That type is not issuance:
until `WHOLE-WINDOW-STOP-RECEIPT-01` installs its governed producer, this
family always returns `paper_custody_blocked_pending_receipt` after completing
the read, anchor, replay, receipt, and reopen checks.

Claims replay the canonical claim-verdict validator against the finalized
manifest. Before a production registration can issue, the embedded floor copy
must be byte-identical to the anchored on-disk floor, the sidecar must join to
the reader-computed verdict digest, and each floor resolution must bind the
full selected arm identity beginning with `condition_family_id`.

Transfer replay must recompute the projection from authenticated reviewed
capture. A production registration remains unavailable until the reviewed
capture and result-receipt producers pass their separate gates. Fixture
self-consistency never authorizes TR-01 prose.

## Closed refusal namespace

`PaperCustodyRefusal` carries a code, an optional input role, the
artifact/cell/token scope, non-renderable nested validator codes, and a
non-renderable read census. Its rendered output is always empty.

| Code | Meaning |
|---|---|
| `paper_custody_request_invalid` | ref, role, pin, or closed wire is invalid |
| `paper_custody_anchor_unavailable` | independent Git or inventory authority cannot be reached |
| `paper_custody_anchor_mismatch` | caller-consistent bytes disagree with independent authority |
| `paper_custody_path_refused` | path containment, symlink, or file-kind check failed |
| `paper_custody_input_unreadable` | a required file cannot be read |
| `paper_custody_digest_mismatch` | disk bytes disagree with the caller pin |
| `paper_custody_parse_invalid` | strict JSON or JSONL parsing failed |
| `paper_custody_receipt_unissued` | the owning production inventory or receipt producer does not exist |
| `paper_custody_blocked_pending_receipt` | whole-window issuance is still gated |
| `paper_custody_receipt_invalid` | receipt or inventory schema is invalid |
| `paper_custody_receipt_binding_mismatch` | receipt differs from anchored inputs or fresh replay |
| `paper_custody_validator_refused` | an owning validator returned a refusal |
| `paper_custody_derivation_mismatch` | a producer-only relation does not recompute |
| `paper_custody_evidence_ambiguous` | roles, paths, rows, or evidence are not unique |
| `paper_custody_identity_not_v5` | the full registered v5 identity does not match |
| `paper_custody_input_changed` | any file changed between first read and reopen |

Unknown codes collapse to `paper_custody_request_invalid`. Nested validator
codes and details are diagnostics only and must never enter a fill, row, token,
sentence, or exception string shown to a renderer.

## Bypass closure and guards

Floor-extraction summary and strict JSON helpers must read through the active
authentication session. Paper modules belong to the authentication-surface
AST census, which rejects direct readable I/O. A second AST census rejects
public supplier signatures containing bytes, dictionaries, mappings,
arbitrary sequences, variadic arguments, receipt parameters, or validation
result parameters.

The lower compatibility APIs
`analysis_engine.inputs.load_floor_artifact(path)` and
`campaign_provenance.load_campaign_log_rows(..., raw_bytes=...)` may not be
used by a paper supplier. Their legacy raw/degrading forms must be removed or
made to require a seam-issued capability before any supplier rebase merges.

## Class-ending test

The single census test opens each family, obtains the session's actual read
census, and attacks every record three ways:

1. Raw mutation keeps the frozen caller pin and must return exactly
   `paper_custody_digest_mismatch`.
2. Full caller resealing changes the semantic value and every caller pin while
   leaving the independent anchor fixed; it must return exactly
   `paper_custody_anchor_mismatch` for the fixture wire.
3. Replay-to-reopen replacement changes the file only after validator replay;
   it must return exactly `paper_custody_input_changed`.

Every arm asserts zero rendered output. The fixture catalog lives only under
`tests/fixtures/paper_custody/`, declares that it contains no measurement
value, and cannot yield an issuance-authorized result.
