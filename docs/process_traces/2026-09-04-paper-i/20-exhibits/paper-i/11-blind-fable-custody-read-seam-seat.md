# Blind Fable design seat — the custody-read seam for paper suppliers (2026-09-04)

Disclosure: auto-loaded `~/.claude/CLAUDE.md`, project `CLAUDE.md`, memory `MEMORY.md`. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md. `$OUT` was empty at launch; this file is the output. Read: rulings 06–10; d123 traces 02-*, 05, 07; d165 traces 05, 10 (earlier rounds via re-audit tables); branch code `reported_phase_energy.py` (b72bbc35), `results_fill_outcome.py` (d79d2883); this checkout's authentication_io, whole_window, analysis_engine, analysis_manifest_v3, dominance_closeout, identity_pins.

## Diagnosis
Both lanes fail because the caller still holds an authority: an embedded document beside its own hash (d123 `_wrapped_document`, `reported_phase_energy.py:308-330`, never opens `path`); a caller-written PASS receipt (d165 `_authenticated_closeout_path`, `results_fill_outcome.py:337-420`, only producer `tests/test_results_fill_outcome.py:270-319`); or an expected digest checked only against the same caller's bytes. A digest, receipt, or content address supplied by the party that supplies the bytes is a consistency check, not authentication. Authority must be something the caller cannot write: a validator replayed in-process over bytes re-read from disk, joined to an independent anchor (git-tracked blob, runs-root bundle bytes, a content ID recomputed by the owning validator).

## 1. Module and public API — `joulewise/custody_read.py`
```python
class Binding(NamedTuple):            # the ONLY input shape a supplier may accept
    path: Path; sha256: str           # sha256 is a PIN (refuse on mismatch), never authority

class CustodyRefusal(Exception):      # never a fill value; frozen renderer maps it to stderr + rc 2
    code: str; where: str             # code ∈ REFUSAL_CODES below; where = label, never prose

@dataclass(frozen=True)
class Verified(Generic[T]):
    value: T                          # typed object built ONLY from re-read bytes
    digests: Mapping[str, str]        # label -> sha256 of the bytes actually validated
    validator: str                    # dotted name of the replayed validator
    validator_source_sha256: str      # sha256 of the validator module file (impl identity)

REFUSAL_CODES = frozenset({
  "custody_path_unsafe",              # outside root, symlink component, non-regular
  "custody_bytes_unreadable",
  "custody_digest_mismatch",          # bytes != Binding.sha256 (pin failed)
  "custody_grammar_invalid",          # strict JSON/JSONL: dup keys, non-finite, BOM
  "custody_schema_mismatch",
  "custody_governed_source_mismatch", # bytes != git:HEAD blob of a governed file
  "custody_validator_refused",        # replayed validator errors (codes in .where)
  "custody_join_mismatch",            # cross-artifact digest/ID join failed
  "custody_row_not_unique",           # row bytes occur != 1 times in the log
  "custody_identity_not_v5",          # D-166 identity-pin gate failed
  "custody_reread_changed",           # bytes changed between validation and re-read
})

def read_bound(b: Binding, *, grammar: Literal["json","jsonl","raw"], label: str,
               within: Path | None = None) -> bytes
def read_governed(relative_repo_path: str, *, label: str) -> tuple[bytes, str]
def open_reported_energy_parents(*, runs_root: Path, extraction_spec_repo_path: str,
    extraction_report: Binding, evaluation_basis: Binding, g2a_selection: Binding,
    prompt_pin: Binding, campaign_role: str) -> Verified[ReportedEnergyParents]
def open_closeout(*, closeout: Binding, finalized_manifest: Binding,
    floor_artifact: Binding, replay_sidecar: Binding) -> Verified[Closeout]
def open_whole_window_row(*, runs_root: Path, campaign_log: Binding, row: Binding,
    prospective_manifest: Binding, plan_tree: Binding) -> Verified[WholeWindowRow]
def open_claim_verdicts(*, claim_verdicts: Binding, finalized_manifest: Binding,
    claim_side_bound: Binding | None) -> Verified[ClaimVerdicts]
def open_transfer_projection(*, projection: Binding, reviewed_capture: Binding
    ) -> Verified[TransferProjection]
```
Every opener, in order: (a) `read_bound` = d165's `_read_bound_regular` (`results_fill_outcome.py:281-335`: O_NOFOLLOW, regular file, containment) moved here, then strict-parsed via `V2AuthenticationReadSession.read`/`read_nofollow` (`authentication_io.py:401-453`) in a fresh session the opener owns; (b) the owning validator replayed in-process; (c) every bound file re-read and compared to (a) → `custody_reread_changed`; (d) `Verified.digests` = the digests from (a). No opener takes a `Mapping`, `bytes`, a receipt, or a pre-validated object; there is no `receipt_path` parameter anywhere. `read_governed` reads `git show HEAD:<path>` via `ingest_git_authentication_input` (`authentication_io.py:590-603`) and refuses if the working tree differs; it gives the frozen extraction spec an authority the caller does not hold.

## 2. How each input is obtained
- **D-123 reported-energy parents.** Spec: `read_governed(<tracked spec path>)` with `session.allow_governed_extraction_spec` (`authentication_io.py:349`); kills d123 R2-B1 (self-resealed universe, 202.55→52.55 J). Report: `read_bound` → `validate_d117_mint_consumption_report` (`floor_extraction.py:1599`). Basis: recompute `basis.sha256`; join report drift-allowance basis digests and `consumption_semantics_id` (today's checks at `reported_phase_energy.py:380-412`, moved here). Members: for every ordered `spec.reported_energy_cells[].members[].bundle_id`, `validate_bundle(runs_root/bundle_path, strict=True)` (`joulewise/cli.py:392`) must return `[]`, then `load_reported_phase_energy_member` (branch floor_extraction) under the same session, three digests joined to the basis `member_occurrences` row. Output `ReportedEnergyParents(spec, report, basis, g2a, prompt_pin, members)`; `_derive_reported_energy_projection` (`reported_phase_energy.py:473`) becomes a pure function of it; `source_material` shrinks to Bindings plus `campaign_role`.
- **D-165 close-out.** Four Bindings; replay `validate_d165_closeout(closeout, finalized_manifest_bytes=…, floor_artifact_bytes=…, replay_sidecar_bytes=…)` (`dominance_closeout.py:1713`), `validate_finalized_analysis_manifest_v3` (`analysis_manifest_v3.py:4403`), `authenticate_floor_artifact_bytes` (`analysis_engine/inputs.py:868`) against the manifest-declared digest. OB-01 cell labels come from the registry row keyed by the cell ID in the authenticated finalized manifest, never from close-out text (kills d165 S-2 `41x-fabricated`).
- **Whole-window verdict row.** Read `campaign_log` (jsonl) and `row`; require `_exactly_once_in_log` (`results_fill_outcome.py:440`, moved here) and `schema_version == WHOLE_WINDOW_SCHEMA` (`whole_window.py:74`); replay `validate_prospective_analysis_manifest_v3` (`analysis_manifest_v3.py:2932`); gate identity via `identity_pins.stack_identity_sha256` (`identity_pins.py:205`) over manifest bytes; then call a NEW public `whole_window.validate_verdict_row(row, runs_root, referenced_bundle_ids, *, consumption_session=None) -> RowValidation(authentic, reasons, status)`, a rename-and-export of `_validate_row` (`whole_window.py:4981`) with `row["status"]` attached. `authentic and status != "passed"` is the whole-window stop; `not authentic` → `custody_validator_refused`. This replaces the queued receipt producer with an API export.
- **claim_verdicts.v1 + claim_side_bound sidecar.** Replay `validate_claim_verdicts(value, frozen_manifest=…)` (`analysis_engine/artifact.py:945`, recomputes `calculate_claim_verdicts_id` at `:403`), decode `inputs.floor_artifact.embedded_bytes_base64` and run `authenticate_floor_artifact_bytes(raw, expected_sha256=file_sha256, expected_artifact_id=artifact_id)` (R2-FL-1); require `sidecar.claim_verdicts_sha256 == sha256(v1 bytes)` else `custody_join_mismatch`. Sidecar absent → `claim_side_bound=None`; the gamma renderer refuses.
- **Transfer projection.** Read projection + reviewed capture; require the projection's declared capture digest to equal the capture bytes' sha256; replay the R3 projection validator. The capture producer stays unadopted (R3 fence).

## 3. The ONE test pattern — `tests/custody_census.py::assert_custody(opener, bindings, supplier_entry)`
Control run: `Verified` with `digests[label] == sha256(disk bytes)` for every label. Then for every bound file and every mutation in {flip one byte at 8 offsets, truncate, append, **reseal**}: reseal = one semantic edit (member point, member-list swap, reason string, cell label) followed by recomputing *every* caller-controllable seal (`file_sha256`, `basis.sha256`, `claim_verdicts_id`, `source_id`, the Binding pin, any receipt the test could author). Assert: (i) the opener raises `CustodyRefusal` with `code ∈ REFUSAL_CODES`, and for reseal the **exact** owning code (`custody_governed_source_mismatch` spec; `custody_join_mismatch` basis/sidecar; `custody_validator_refused` report/closeout/claim_verdicts; `custody_row_not_unique` log); (ii) the supplier's public entry returns its structured refusal and no string in it contains any token of the mutated value; (iii) the control re-run reproduces identical bytes. Two static guards: `direct_read_violations` (`authentication_io.py:623`) asserted empty over `results_fill_outcome.py`, `reported_phase_energy.py` and every future supplier module; a signature test refusing any public supplier parameter annotated `Mapping`, `dict`, `bytes`, or named `*receipt*`. This generalizes the d123 S2 cure: assert at the owning relation, and make "caller-consistent" the adversary.

## 4. Delete vs keep in the two landings
- **d123 delete:** `_wrapped_document`/`_optional_wrapped_document` and the `document` field of `source_material` (`reported_phase_energy.py:308-338`); `_validated_parent_wrappers` body (moves into the opener); the fixture's invented member points (`tests/test_reported_phase_energy.py:152-246`). **Keep:** projection arithmetic, `validate_reported_energy_projection_derivation`, three refusal scopes, composition-rule gate, duplicate-role/mixed-source cures, registry rows DS-09..24, `load_reported_phase_energy_member`.
- **d165 delete:** the receipt Binding pair, `CLOSEOUT_VALIDATION_RECEIPT_SCHEMA`, `_CLOSEOUT_RECEIPT_KEYS`, `_CLOSEOUT_SOURCE_RECEIPT_KEYS` (`results_fill_outcome.py:40-47,173-188`); the test receipt writer (`tests/test_results_fill_outcome.py:270-319`); `_PUBLIC_CELL_ID_RE` as authority (keep as prose lint); the three-string gate in `_v5_manifest_model_names` (`:783`). **Move to custody_read:** `_read_bound_regular`, `_exactly_once_in_log`, reopen-after-replay. **Keep:** `OutcomeFillRefusal`/`OutcomeFillResult`, stage order (restore F2: before-comparison wins even over an invalid close-out, trace 10 V5), the OR-01 reason map, `_FORBIDDEN_PUBLIC_MARKERS`.

## 5. Decision-log entry — YES, D-173
One seam for every claim-bearing value (path+pin in, validator-replayed typed object out, receipts are outputs); retires the "receipt in" clause of 07 §(2) and 09 R4-S2; reclassifies `WHOLE-WINDOW-STOP-RECEIPT-01` as an API export. No new wire, no value issued.

## Where I disagree with the earlier rulings
1. **Receipts as inputs (07 §(2), 09 R4-S2, d165 consult Q2).** A receipt supplied by path+digest is a caller document; trace 10 proved the test authored its own PASS receipt. Receipts are what the seam *returns* (`Verified.digests`), never what it accepts. `WHOLE-WINDOW-STOP-RECEIPT-01` as a receipt producer is the same defect one level up.
2. **08's Q-R1-5 replacement names no authority for the spec bytes.** "Validate the frozen extraction spec" from a caller path is the R2-B1 signature. Authority for a governed file is the git-tracked blob (`read_governed`).
3. **07 §(2) "STOP_FILL until a receipt producer exists" is over-cautious.** `_validate_row` (`whole_window.py:4981`) already returns `(ok, reasons)` and the row carries `status`; the distinction exists and needs an export, not an artifact.
4. **Expected digests are a pin, not authentication.** They make substitution loud; the returned digests are computed by the seam from validated bytes.
5. **Byte-exact registry strings (06 R3, R4-B1) constrain the template, not the value.** Only the seam constrains the value.
