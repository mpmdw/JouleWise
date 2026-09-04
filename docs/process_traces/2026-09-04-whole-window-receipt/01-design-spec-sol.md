```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Bind source authenticity separately from failed admission.","workspace":{"base_requested":"913bf3f7","base_mode":"exact","head_start":"913bf3f76025f654e5b910670c5a00bfd82c34d4","head_end":"913bf3f76025f654e5b910670c5a00bfd82c34d4","upstream_end":"913bf3f76025f654e5b910670c5a00bfd82c34d4","branch":"feat/2026-09-04-whole-window-receipt-design"},"pathspec":["docs/process_traces/2026-09-04-whole-window-receipt/01-design-spec-sol.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1-VALIDATOR-COLLAPSE","severity":"blocker","text":"Current validation classifies genuine admission conditions as bad provenance."},{"id":"F2-RECEIPT-RESULT-BINDING","severity":"should_fix","text":"Generic custody receipts do not bind the structured result."},{"id":"F3-SUPERSEDED-WIRES","severity":"nit","text":"Superseded artifact and caller-digest wires must not return."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"f=docs/process_traces/2026-09-04-whole-window-receipt/01-design-spec-sol.md; test $(wc -c < $f) -lt 12288 && echo DESIGN_SPEC_OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DESIGN_SPEC_OK"]},"expected":{"exit_code":0,"tail_regex":"^DESIGN_SPEC_OK$"}},{"id":"V2","kind":"inspection","cmd":"git diff --check -- docs/process_traces/2026-09-04-whole-window-receipt/01-design-spec-sol.md && echo DIFF_CHECK_OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIFF_CHECK_OK"]},"expected":{"exit_code":0,"tail_regex":"^DIFF_CHECK_OK$"}}],"flags":[{"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"D-165 trace absent at base; read on its branch. Custody contract read at 3c27234e.","needs":"Compose owning branches before implementation."},{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"No tests: design-only seat and preflight rule.","needs":"Run acceptance test in implementation."}]}
```

## Findings

### F1-VALIDATOR-COLLAPSE — blocker

The source is the newline-terminated row returned by `append_log`: schema at
`joulewise/whole_window.py:74`, status at `scripts/run_campaign.py:6324-6338`,
body at `:6353-6406`, append at `:6407`, and byte-identical standalone publish
at `:6408-6416`. Authenticate `status == "failed"`; do not invent `excluded`.

Current validation cannot do that. It calls every nonempty `core.conditions`
provenance-invalid (`joulewise/whole_window.py:4172-4175`) despite the registered
admission vocabulary (`docs/decision_log.md:4257-4271`), couples row status to
the NEG-8 refusal (`joulewise/whole_window.py:5290-5293`), and returns only a
Boolean/reasons tuple (`:5475,:5666-5713`). Post-hoc whitelisting is unsound.

Implement these frozen types in `joulewise/whole_window.py`:

```python
@dataclass(frozen=True, slots=True)
class WholeWindowAdmissionReason:
    member_id: str | None          # None means idle_admission_core.conditions
    reason_code: str               # closed D-078/member-failure spelling

@dataclass(frozen=True, slots=True)
class WholeWindowRowValidation:
    authentic: bool
    admission: Literal["passed", "failed"] | None
    status: Literal["invalid", "passed", "flagged", "failed"] | None
    row_sha256: str | None
    source_refusal_codes: tuple[str, ...]
    admission_reasons: tuple[WholeWindowAdmissionReason, ...]
```

`validate_whole_window_verdict_row(raw_row, runs_root, referenced_bundle_ids,
consumption_session=...)` accepts canonical UTF-8 JSON bytes, strict-validates
the full row/status/Boolean `claim_licensing`, and replays existing membership,
policy, provenance, source, bundle, calibration, bracket, CPU, environment,
adapter, and consumption checks. Malformation, missing evidence, ambiguity,
unknown codes, or stored/derived disagreement enters `source_refusal_codes`.
Freshly derived gate failures enter `admission_reasons` and must exactly match
the sorted projection of `core.conditions` and
`member_failures[].{member_id,reason_code}`. `authentic` means no source code;
`admission` is `passed` only when derived gates and stored status pass, `failed`
only when a derived gate and production status fail. A mismatch is provenance,
while authentic `invalid`/`flagged` rows have `admission is None`.

Keep `whole_window_refusal_reasons` compatible: source codes for unauthentic,
admission codes for authentic failure, `()` only for authentic pass. Preserve
the six-key semantic identity (`joulewise/whole_window.py:163-172`); the receipt
binds exact bytes, not a new semantic identity.

### F2-RECEIPT-RESULT-BINDING — should_fix

Use this subtype. Keys are exact; arrays have the stated order, hashes are 64
lowercase hex strings, and integers exclude Boolean values.

```json
{"schema_version":"joulewise.paper_custody_whole_window_receipt.v1",
 "family":"whole_window_verdict","status":"PASS",
 "validator":"joulewise.paper_custody.whole_window_verdict.v1",
 "validator_source_sha256":"<D-173 source-census sha256>",
 "inputs":[
  {"path":"<runs relative>","role":"campaign_log","sha256":"<hex>"},
  {"path":"<repo relative>","role":"plan","sha256":"<hex>"},
  {"path":"<repo relative>","role":"prospective_manifest","sha256":"<hex>"},
  {"path":"<runs relative>","role":"standalone_verdict","sha256":"<hex>"}],
 "result":{"row_schema_version":"joulewise.idle_admission_whole_window_verdict.v1",
  "row_sha256":"<standalone sha256>","campaign_log_occurrences":1,
  "source_valid":true,"admission":"failed","row_status":"failed",
  "claim_licensing":true,"bundle_ids":["<ordered id>"],
  "evaluation_basis_sha256":"<hex>","consumption_semantics_id":"<id>",
  "prospective_manifest_id":"<am-id>","plan_id":"<id>",
  "targets":[{"model_id":"<id>","phase":"<measurement arm>"}],
  "admission_reasons":[{"member_id":null,"reason_code":"<code>"}]}}
```

`inputs` sorts by role; bundle IDs preserve row order; targets sort by
`(model_id,phase)`; reasons sort by `(member_id is not None,member_id or
"",reason_code)` and are nonempty. Derive targets by joining every basis member
through authenticated source/order-manifest config to prospective plan model
identity and `measurement_arm`; missing/extra/ambiguous joins refuse. Require a
valid `joulewise.analysis_manifest.v3.prospective` and fixed `_v5` pair. Never
substitute a finalized manifest.

Canonicalize with `json.dumps(ensure_ascii=False,allow_nan=False,sort_keys=True,
separators=(",",":"))`, UTF-8, one newline. The full-file SHA-256 is the content
address pinned by supply map and inventory; store no self-asserted ID. Caller
content has no authority without that independent pin.

Add `issue_whole_window_stop_receipt` in `joulewise/whole_window_receipt.py` and
CLI flags `--whole-window-stop-receipt-output`,
`--whole-window-prospective-manifest`, `--whole-window-plan-tree`. The first is
whole-window-only and requires the latter two and verdict output. Call it under
the lock, after standalone publication (`scripts/run_campaign.py:6408-6416`)
and before `:6417`. Reopen all inputs, require the standalone bytes exactly once
as a complete JSONL line, replay both validators, and issue no-clobber only when
`authentic`, `admission == "failed"`, `status == "failed"`,
`claim_licensing is True`, `_v5` identity is exact, and reasons are nonempty.
Normal failed admission still exits 1. Receipt failure is nonzero without
rollback. No flag or any other row class means no receipt and `STOP_FILL`.

Receipt validation is total and ordered after the D-173 path/digest/grammar
checks. Its closed nested codes are:

| Code | Predicate | Outer custody code |
|---|---|---|
| `whole_window_receipt_schema_invalid` | noncanonical bytes, wrong/excess keys or types | `paper_custody_receipt_invalid` |
| `whole_window_receipt_binding_mismatch` | input rows/digests or row digest disagree | `paper_custody_receipt_binding_mismatch` |
| `whole_window_receipt_validator_identity_mismatch` | validator name/source digest differs | `paper_custody_receipt_binding_mismatch` |
| `whole_window_receipt_row_not_unique` | exact standalone line occurs other than once | `paper_custody_evidence_ambiguous` |
| `whole_window_receipt_source_refused` | fresh typed replay is unauthentic | `paper_custody_validator_refused` |
| `whole_window_receipt_admission_not_failed` | replay is not claim-bearing failed admission | `paper_custody_validator_refused` |
| `whole_window_receipt_identity_not_v5` | prospective validation/join or fixed pair fails | `paper_custody_identity_not_v5` |
| `whole_window_receipt_replay_mismatch` | canonical fresh result differs from `result` | `paper_custody_receipt_binding_mismatch` |

The family read stays `open_paper_input(WholeWindowVerdictRef(role: str,
runs_root: Path)) -> VerifiedWholeWindowVerdict`: resolve pinned inventory,
inputs and receipt; replay; reopen; privately build a frozen result containing
typed status, model IDs, phases, bundle IDs, basis/semantics IDs and reasons.
No paths, bytes, mappings or nested codes escape. This implements ruling 15
(`15-magistrate-ruling-custody-seam.md:5-11`) and addendum 16 (`16-...:5`).

**ONE acceptance test:** `test_whole_window_receipt_census_and_caller_reseal_refuse`.
Its real producer fixture exits 1 yet opens as typed failed. Subtests census raw
mutation (`paper_custody_digest_mismatch`), full reseal of all inputs/inventory
plus a caller-authored canonical receipt while the supply-map pin stays fixed
(`paper_custody_digest_mismatch`, role `validator_receipt`), and replacement
after replay (`paper_custody_input_changed`). Each has `rendered_output == ""`.
The full-reseal arm is the required counterfactual.

**Decision log:** amend D-173; allocate no new number. Q-C-4 authorized this
mission (`15-magistrate-ruling-custody-seam.md:7`), but generic v1 has exact
`replay_codes` and no result (`paper_supply_custody.md@3c27234e:178-195`). Add
the subtype/mapping and amend `decision_log.md@3c27234e:10903-10932` pre-gate.

Implementation-seat `WRITE_SCOPE` (exhaustive proposal):

```json
["joulewise/whole_window.py","joulewise/whole_window_receipt.py","joulewise/paper_custody.py","scripts/run_campaign.py","configs/paper_supply/supply_map.json","docs/contracts/paper_supply_custody.md","docs/decision_log.md","tests/test_whole_window.py","tests/test_run_campaign.py","tests/test_paper_custody.py","tests/test_authentication_io.py","tests/fixtures/paper_custody/**","docs/process_traces/2026-09-04-whole-window-receipt/02-implementation-sol.md"]
```

### F3-SUPERSEDED-WIRES — nit

All contract conflicts found:

1. The fictitious artifact at
   `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:25`
   was replaced by `07-magistrate-rulings-addendum.md:7`.
2. Caller-supplied path/digest advice at D-165 trace 05
   `@feat/2026-09-04-d165-outcome-renderer:128-150` and
   `07-magistrate-rulings-addendum.md:7` is superseded: addendum 16 requires
   role plus runs root (`16-magistrate-rulings-addendum-5.md:5`). Trace 05's
   `admission=excluded` (`:148-151`) also conflicts with the real `failed` enum;
   paper may derive “excluded,” but the receipt may not mint it.
3. Generic receipt exact keys at
   `docs/contracts/paper_supply_custody.md@3c27234e:178-195`
   lack the structured result; amend D-173.
4. `joulewise/whole_window.py:4172-4175,5290-5293,5475` conflicts with the
   vocabulary (`docs/decision_log.md:4222-4271`), rederivation (`:4436-4448`), and
   Q-C-4 (`15-magistrate-ruling-custody-seam.md:7`); split accumulation fixes it.

Exact-byte binding leaves the six-key identity (`whole_window.py:163-172`)
unchanged. Caller digests, normalized stop objects and rendered nested codes
remain forbidden.

## Residual risk

Measurement decides roles/root, paths/digests, receipt/inventory bytes,
targets, bundles, basis/semantics IDs and reasons; no value is predicted or
retrofitted. Nonissuance, professor prose and D-165 re-landing remain
`STOP_FILL`. D-173 is on sibling `3c27234e`; compose it and recheck anchors.
