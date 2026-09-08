```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"Round 2 closes the receipt wire and authority chain while keeping unregistered paper prose fail-closed.","workspace":{"base_requested":"44abb2f1","base_mode":"exact","head_start":"44abb2f1d95fc0f835dea4b3646e2c0147c9aad1","head_end":"44abb2f1d95fc0f835dea4b3646e2c0147c9aad1","upstream_end":"44abb2f1d95fc0f835dea4b3646e2c0147c9aad1","branch":"feat/2026-09-04-whole-window-receipt-design"},"pathspec":["docs/process_traces/2026-09-04-whole-window-receipt/03-design-spec-round-2-sol.md"],"unowned_dirty":[],"verdict":{"findings":[]},"verification":[{"id":"V1","kind":"inspection","cmd":"f=docs/process_traces/2026-09-04-whole-window-receipt/03-design-spec-round-2-sol.md; test $(wc -c < $f) -lt 12288 && echo DESIGN_SPEC_OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DESIGN_SPEC_OK"]},"expected":{"exit_code":0,"tail_regex":"^DESIGN_SPEC_OK$"}},{"id":"V2","kind":"inspection","cmd":"! rg -n '[[:blank:]]+$' docs/process_traces/2026-09-04-whole-window-receipt/03-design-spec-round-2-sol.md && echo DIFF_CHECK_OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIFF_CHECK_OK"]},"expected":{"exit_code":0,"tail_regex":"^DIFF_CHECK_OK$"}}],"flags":[{"id":"F1","kind":"environment","level":"nonblocking","text":"The worktree denied FETCH_HEAD writes and DNS; cached seam head 002353a9 and contract blob 2e3349e1 were inspected.","needs":"Lead re-fetches before implementation and rechecks the invariants if head advanced."},{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"No tests run: design-only seat; preflight permits tests only to confirm a claim.","needs":"Implementation runs focused tests and the canonical suite."}]}
```

# WHOLE-WINDOW-STOP-RECEIPT-01 — round-2 implementation specification

## Decision and authority

Implement on `origin/feat/2026-09-04-paper-custody-seam@002353a9` or its
lead-confirmed latest descendant. The inspected normative contract blob is
`docs/contracts/paper_supply_custody.md@2e3349e1`. Its whole-window input order
is fixed: `campaign_log`, `standalone_verdict`, `prospective_manifest`, `plan`;
inventory also has `validator_receipt` (lines 150-159, 170-174). Never subtype,
sort, add, or omit a role.

This mission authenticates an admission-failed production row; it does not
license professor-facing reason prose. Choose Opus A2(b): OR-01 and the
DS-32/PG-08 `stopped before comparison` branches remain `STOP_FILL` until
`WHOLE-WINDOW-REASON-SENTENCE-MAP-01` supplies a closed code enumeration,
exact sentence map, bidirectional census test, and supplier integration.
Amend those registry rows with this residual. The separate `required ...
verdict absent` branches remain owned by `CLAIM-NONISSUANCE-RECEIPT-01`; bare
absence cannot render.

## 1. Typed source/admission split

Replace the seam head's post-hoc `_WHOLE_WINDOW_ADMISSION_OUTCOME_REASONS`
heuristic and current four-field result with:

```python
@dataclass(frozen=True, slots=True)
class WholeWindowAdmissionReason:
    member_id: str | None
    reason_code: str

@dataclass(frozen=True, slots=True)
class WholeWindowRowValidation:
    authentic: bool
    admission: Literal["passed", "failed"] | None
    status: Literal["invalid", "passed", "flagged", "failed"] | None
    row_sha256: str | None
    source_refusal_codes: tuple[str, ...]
    admission_reasons: tuple[WholeWindowAdmissionReason, ...]
```

`validate_whole_window_verdict_row(raw_row: bytes, runs_root: Path,
referenced_bundle_ids: set[str], *, consumption_session=...)` requires
canonical UTF-8 JSON plus LF and replays the existing membership, policy,
provenance, source-manifest, bundle, calibration, bracket, CPU, environment,
adapter, and consumption checks. Split at each check; never classify a final
flat reason tuple by allowlist.

- Grammar/type/schema, missing/ambiguous evidence, unknown codes,
  path/digest/census/provenance, validator exceptions, and stored/derived
  disagreement enter sorted `source_refusal_codes`; `authentic=False` and
  `admission=None`.
- Only source-clean, freshly derived gate failures enter `admission_reasons`.
  They equal the sorted projection of `idle_admission_core.conditions`
  (`member_id=None`) and `member_failures[].{member_id,reason_code}`. Any
  unknown, extra, missing, duplicate, or order mismatch is a source failure.
- Source-clean passed/no-reason gives `passed`; source-clean claim-bearing
  production failed/nonempty-reasons gives `failed`. `invalid` and `flagged`
  give `None`. Exploratory `flagged` is intentionally non-issuing.
- Keep `whole_window_refusal_reasons` compatible and preserve the existing
  six-key semantic identity; exact-byte binding is not a seventh key.

D-161 binds this split: tampered, malformed, missing, or unauthenticated
evidence stays fail-closed and never mints this or any non-issuance receipt.

## 2. Exact receipt subtype

The file is sorted-key compact UTF-8 JSON plus LF, strict duplicate/non-finite
rejection; hashes are lowercase hex and integers exclude Boolean. Its exact
keys are the seven generic keys at contract lines 178-195 plus `result`:

```json
{"family":"whole_window_verdict","inputs":[{"path":"<runs relative>","role":"campaign_log","sha256":"<hex>"},{"path":"<repo relative>","role":"plan","sha256":"<hex>"},{"path":"<repo relative>","role":"prospective_manifest","sha256":"<hex>"},{"path":"<runs relative>","role":"standalone_verdict","sha256":"<hex>"}],"replay_codes":[],"result":{"admission":"failed","admission_reasons":[{"member_id":null,"reason_code":"<closed code>"}],"bundle_ids":["<row order>"],"campaign_log_occurrences":1,"claim_licensing":true,"consumption_semantics_id":"<id>","evaluation_basis_sha256":"<hex>","plan_id":"<id>","prospective_manifest_id":"<id>","row_schema_version":"joulewise.idle_admission_whole_window_verdict.v1","row_sha256":"<standalone sha256>","row_status":"failed","source_valid":true,"targets":[{"model_id":"<id>","phase":"<measurement arm>"}]},"schema_version":"joulewise.paper_custody_whole_window_receipt.v1","status":"PASS","validator":"joulewise.paper_custody.whole_window_verdict.v1","validator_source_sha256":"<D-173 census sha256>"}
```

A subtype may add keys, never drop a base key. `inputs` sorts by role; the map
census does not. Bundle IDs keep row order; targets sort by `(model_id,phase)`;
reasons sort by `(member_id is not None,member_id or "",reason_code)` and are
nonempty. Join each basis member through authenticated source/order-manifest
configuration to prospective-plan model identity and `measurement_arm`.
Missing/extra/duplicate/ambiguous joins refuse. Require valid prospective-v3,
authenticated plan tree, and fixed `_v5` Qwen3 pair; never use a finalized
manifest. The full-file map digest is the sole content address—no receipt ID.

`replay_codes` is the generic fresh-replay result, `[]` here; structured
admission lives in `result`. Amend contract and `_validate_receipt` to exact-
dispatch this subtype; generic whole-window receipts, unknown schemas, dropped
base keys, or extras refuse. The source census adds both row and receipt
validators.

## 3. Producer and consumer

Add `joulewise/whole_window_receipt.py::{issue,validate}_whole_window_stop_receipt`.
Run-campaign adds `--whole-window-stop-receipt-output`,
`--whole-window-prospective-manifest`, `--whole-window-plan-tree`; receipt
output requires the latter two and verdict output. Under the campaign lock,
issue after log append and byte-identical standalone publish, before the current
print/return. Reopen all sources, require the standalone bytes exactly once as
a complete log line, replay plan/manifest and typed validation, and publish
no-clobber only for exact `authentic`, `admission="failed"`, status `failed`,
Boolean `claim_licensing is True`, fixed `_v5`, and nonempty reasons. Ordinary
failed admission remains rc 1. Receipt failure is nonzero without log rollback.
No flag, other row class, `flagged`, or source/evidence failure writes a receipt.

Custody validates after map/path/digest/grammar, compares fresh result exactly,
reopens, then privately constructs frozen `VerifiedWholeWindowVerdict` with
only custody evidence, status/admission, targets, bundle/basis/semantics/
manifest/plan IDs, and reason codes. No path, bytes, mapping, free text, or
nested source code escapes; reason codes are not prose.

Nested -> outer translations: schema/canonical/key/type ->
`paper_custody_receipt_invalid`; input/row/result mismatch, validator identity,
or replay mismatch -> `paper_custody_receipt_binding_mismatch`; nonunique log
row -> `paper_custody_evidence_ambiguous`; unauthentic source or not a
claim-bearing failed admission -> `paper_custody_validator_refused`; bad
manifest/plan/join/pair -> `paper_custody_identity_not_v5`. Nested names are
respectively `whole_window_receipt_{schema_invalid,binding_mismatch,
validator_identity_mismatch,row_not_unique,source_refused,
admission_not_failed,identity_not_v5,replay_mismatch}`.

## 4. Production map-row link

Measurement output is not authority until Git pins it. The named final-link
producer is lead-owned, separately gated `PAPER-SUPPLY-MAP-ROW-MINT-01`, entry
point `scripts/mint_paper_supply_map_row.py --family whole_window_verdict`. It
reopens/validates the fixed inputs and receipt, emits the exact inventory,
computes digests, and proposes one production map role; its reviewed commit is
the clean-tree anchor. Until then production consumption is
`paper_custody_receipt_unissued` and no issuing value exists.

This seat may change `supply_map.json` only for synthetic fixture rows/digests:
no live role, locator, digest, inventory, or receipt. Fixtures stay
`issuance_authorized=False`.

## 5. Stage order, residuals, and tests

Per `06-magistrate-contract-rulings.md:26`, before-comparison beats close-out;
with both, it is primary and close-out secondary. No caller precedence input.
Register on OR-01, DS-32, and symmetric PG-08 that this receipt still cannot
license `<issued reason>` (follow-on: `WHOLE-WINDOW-REASON-SENTENCE-MAP-01`),
and that fixed missing-verdict text waits for `CLAIM-NONISSUANCE-RECEIPT-01`.

One auto-census test,
`test_whole_window_receipt_census_and_caller_reseal_refuse`, uses the real
producer fixture (campaign rc 1; typed failed fixture opens non-issuing) and
iterates inventory, four inputs, and receipt:

1. raw mutation -> `paper_custody_digest_mismatch`;
2. full reseal of inputs/inventory/receipt with Git pin fixed -> same code;
3. post-replay replacement -> `paper_custody_input_changed`.

Every refusal has `rendered_output == ()`. Producer regressions prove tampered
input, unauthentic replay, `flagged`, and failed write mint nothing. A two-stage
arm makes before-comparison primary and close-out secondary, then returns
`STOP_FILL` (never the close-out sentence) because the reason map is unissued.

This narrows Opus A6's “rendered” request: A2 permits this residual
(`02-design-review-opus.md:74-82`), while the rule requires selection/secondary
recording, not unsafe prose (`06-magistrate-contract-rulings.md:24-26`).
Rendering would violate D-173 and D-161.

## 6. Sequence and implementation scope

First the magistrate amends D-173—no new number—with subtype-adds-never-drops,
this exact result, unchanged census, map-row gate, and paper residuals.
`docs/decision_log.md` remains outside implementation scope.

```json
["joulewise/whole_window.py","joulewise/whole_window_receipt.py","joulewise/paper_custody.py","scripts/run_campaign.py","configs/paper_supply/supply_map.json","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","tests/test_whole_window.py","tests/test_run_campaign.py","tests/test_paper_custody.py","tests/test_authentication_io.py"]
```

Run focused tests, authentication AST/public-wire guards, and
`python3 -m unittest discover -s tests`. Remaining stops: OR-01 and DS-32/PG-08
before-comparison prose, bare verdict absence, and production reads before the
map-row gate. They remain registered residuals, not fixture-proven claims.
