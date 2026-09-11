# COLD-GATE ADJUDICATION PACKET — WO-MINT-ESTIMATOR-VOCAB F1 seam question

**Assembled mechanically 2026-08-11. No analysis, no recommendation, no verdict appears in this
document.** Every excerpt below is a verbatim quote with a `file:line` citation, verified against
the file bytes at assembly time.

**Repository states cited:**

- Main checkout: `/Users/edr/code/JouleWise` @ `b670c8fe2fb6eec27b378ff077843ff34ac3463b`
- Branch worktree: `/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad/wtE-mintvocab`
  on branch `impl/mint-estimator-vocab` @ `cbf609fdfcc419a4e9c014eef4f0d5c2c14ff737`
  (`cbf609f Merge post-D-133 main into FCM-01; integrate the fallback spec state`),
  with uncommitted working-tree changes (inventory in §8)
- Sol worker report: `/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad/mintvocab-out.md`

---

## 1. The adopted contract — relevant sections

Source: `/Users/edr/code/JouleWise/docs/process_traces/2026-08-11-staged-contracts/mintvocab-impl-contract.md`

### 1a. Goal statement and WRITE_SCOPE header (`mintvocab-impl-contract.md:1-8`)

```
# WO-MINT-ESTIMATOR-VOCAB implementation — three-site spec-authoritative estimator dispatch (CONSULT DESIGN ADOPTED)

WRITE_SCOPE: ["joulewise/floor_mint_estimator.py", "scripts/mint_floor_artifact_generalized.py", "tests/test_floor_mint_estimator.py", "tests/test_mint_floor_artifact_generalized.py", "docs/decision_log.md"]

Branch impl/floor-commonmode-01 at HEAD (this worktree; stacked on the
landed FCM rounds). Implement the adopted consult design EXACTLY (the
full consult text is appended below the divider — it is the contract;
NEEDS_RULING for anything it does not settle).
```

### 1b. Non-negotiables 1–6, complete (`mintvocab-impl-contract.md:10-41`)

Non-negotiable 4 (pinned core unchanged) is item 4 of this list and is reproduced in place; the
whole enumerated section is quoted so no item is truncated.

```
Non-negotiables restated:
1. NEW shared module joulewise/floor_mint_estimator.py: per-cell
   estimator dispatch whose SOLE authority is the committed pre-registered
   extraction spec (never report/artifact data — ALT-D120 invariant);
   selects between the worst-case default core computation and the
   governed two-shared-edge extraction-path computation.
2. The generalized mint consumes the dispatch at ALL THREE sites:
   postcollection equality (steps 8-9), artifact construction, and final
   evidence binding. NO site may retain an unconditional default-core
   recomputation. The consult's named failure mode (steps 8-9-only patch)
   is the thing your tests must prove absent.
3. The mint still RECOMPUTES the floor itself from authenticated members
   under the dispatched estimator and refuses on any mismatch with the
   report's cached value — never trust the report's number.
4. UNCHANGED: scripts/mint_floor_artifact.py (pinned core),
   scripts/floor_mint_pinsets/schema_v2.json, report/artifact schemas,
   production extraction specs (the pack re-spec is a separate D-133
   consumption step).
5. Committed regressions for every consult attack class: spec-swap,
   estimator-mismatch between spec and report, default/registered
   cross-wiring at EACH of the three sites (three distinct regressions —
   one per site, each demonstrated failing against a deliberately
   site-limited implementation variant or the pre-WO code), equality-check
   bypass, and a full mint run on a synthetic common-mode cell producing
   a bound artifact whose floor equals the extraction path's exact value.
6. Proofs: focused matrices (test_floor_mint_estimator,
   test_mint_floor_artifact_generalized, test_floor_extraction,
   test_detection_floor) AND the full canonical suite
   (python3 -m unittest discover -s tests) on python3 AND python3.11,
   exact counts pasted. Append the WO note to docs/decision_log.md's
   D-124/D-133 chain. Leave uncommitted; claude-codex-report/v1, genre
   implementation.
```

### 1c. The three-site MAP — §1 "MAP — current recomputation and pinning path", complete (`mintvocab-impl-contract.md:160-222`)

```
## 1. MAP — current recomputation and pinning path

### Authentication and spec binding

1. `scripts/mint_floor_artifact_generalized.py:1289-1326` authenticates the exact pinset bytes against the supplied SHA-256, rejects duplicate/nonfinite JSON, and selects the closed v2 schema.

2. The v2 schema pins the producer extraction-spec SHA/member count at `:731-740`. Each component repeats those pins, and `:842-852` requires exact agreement with its producer. There is currently no estimator field in the pinset schema.

3. `_authenticate_v2_inputs` loads each input spec and invokes the configured pinned core at `:3438-3476`.

4. The pinned core loads report and spec bytes independently at `scripts/mint_floor_artifact.py:1078-1080`, validates the spec and selects the corresponding spec/report cells at `:1096-1105`, authenticates report membership against the spec, verifies bundles at `:1139-1158`, and rederives the whole-window allowance at `:1164-1252`.

5. The resulting `AuthenticatedComponent` records the exact report and spec byte hashes at `:1255-1275`. The v2 component gate then checks the spec SHA, order-manifest SHA, counts, semantics, and exact member/config sequence at `scripts/mint_floor_artifact_generalized.py:1810-1862`.

Current ordering is slightly wrong for the new authority boundary: `_build_v2_artifacts` calls postcollection recomputation before `_v2_gate_component` at `:2717-2742`. The estimator design should reverse that order so no estimator executes before its spec and member pins pass.

### Every default comparative computation

There are three separate default-only surfaces:

- The pinned core’s normal construction computes ABBA blocks and calls `comparative_false_effect_floor` at `scripts/mint_floor_artifact.py:1474-1513` and `:1575-1585`.

- V2 steps 8–9 independently repeat that default computation at `scripts/mint_floor_artifact_generalized.py:2282-2307`.

- V2 construction repeats it again at `:2569-2579`.

There is also a fourth default assumption during evidence binding: `scripts/mint_floor_artifact.py:1917-1940` reconstructs comparative widths exclusively as `(wA1+wB1+wB2+wA2)/2`. The generalized mint invokes that binder at `scripts/mint_floor_artifact_generalized.py:3672-3684`. A common-mode artifact would therefore remain unmintable even after fixing steps 8–9 and construction.

### Equality and U10

The report-cache equality is exact in decimal text space:

- Recomputed absolute/comparative values are obtained at `scripts/mint_floor_artifact_generalized.py:2308-2318`.
- Both `cell.floor.drift_widened_guarded_floor_j` and `cell.operative_floor_j` must exactly equal the recomputation at `:2319-2344`.

The domain-owned U10 projection is built at `:2346-2396`. Its exact comparison covers:

- pre/post receipt and content digests;
- bracket-binding and terminal-ledger-head hashes;
- observed drift, allowance rule/screen/value, and embedding count;
- absolute/comparative evaluation-basis SHA/count;
- extraction-report SHA;
- absolute, comparative, and operative full-precision values;
- all three six-decimal renderings.

Every field is compared at `:2398-2431`; there is no fill/default route.

`extraction_report_sha256` is the SHA of the exact report bytes captured by the core. Both components must identify one report at `:2276-2280`, and that hash enters the U10 projection at `:2374`. It pins the whole closed-profile report byte stream, including members and cached numbers. It does not make the report an arithmetic authority: steps 8–9 still have to reproduce the numbers from authenticated evidence.

The extraction spec is separately authenticated by `spec_sha256`; that is the existing commitment capable of governing estimator selection.

### FCM branch arithmetic and vocabulary boundary

At `impl/floor-commonmode-01@4f04100`:

- `joulewise/floor_extraction.py:1093-1173` validates the spec-only estimator declaration, registration, and calibration basis.
- `extract_cells` passes those spec fields to `extract_comparative_cell` at `:2696-2717`.
- `extract_comparative_cell` chooses default versus common mode at `:2391-2442`, derives common-mode block inputs from bundle evidence at `:2540-2558`, and never falls back after a registered-path refusal.
- Raw trace curves, windows, residuals, and sweep candidates are independently derived by `_common_mode_block_inputs_from_evidence` at `:2152-2344`.
- `_common_mode_floor_from_extracted_inputs` owns the registered arithmetic at `:485-623`.
- `CellReport.as_row` emits no estimator identity at `:1291-1396`.
- The admitted report profile contains no estimator vocabulary at `:1410-1476` and recursively refuses `estimator_registration` at `:1539-1552`.
- `joulewise/detection_floor.py:4088-4115` similarly refuses registration vocabulary anywhere in an artifact.
```

### 1d. Contract restatement of the pinned-core invariant inside §2 (`mintvocab-impl-contract.md:286`)

```
The pinned `scripts/mint_floor_artifact.py` remains byte-unchanged. V1 behavior and its interface pins remain untouched.
```

### 1e. Contract restatement of the pinned-core invariant inside §4 COST (`mintvocab-impl-contract.md:330-337`)

```
Expected total: roughly 360–540 production LOC and 550–850 test LOC. No changes should be needed in:

- `scripts/mint_floor_artifact.py`;
- `scripts/floor_mint_pinsets/schema_v2.json`;
- report or artifact schemas;
- production extraction specs during this WO.

The later pack re-spec is a separate D-133 consumption step.
```

---

## 2. Architectural conflict evidence (branch worktree bytes)

### 2a. `_authenticate_component` signature and its call into `_verify_report_widths`

`wtE-mintvocab/scripts/mint_floor_artifact.py:1049-1062` (function head):

```python
def _authenticate_component(
    paths: ComponentPaths,
    *,
    expected_cell_id: str,
    expected_basis_sha256: str,
    strict_validator: StrictValidator,
    consumption_authenticator: ConsumptionAuthenticator = (
        _authenticated_consumption_summaries
    ),
    allowance_deriver: AllowanceDeriver = whole_window_drift_allowances,
    expected_consumption_semantics_id: str | None = None,
    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    calibration_bracket_binding: Mapping[str, Any] | None = None,
) -> AuthenticatedComponent:
```

`wtE-mintvocab/scripts/mint_floor_artifact.py:1096-1113` (the call site; `_report_members` then
`_verify_report_widths` execute before membership/semantics/consumption authentication):

```python
    errors = validate_extraction_spec(spec)
    if errors:
        raise MintError(f"invalid extraction spec: {errors[0]}")
    order, order_raw = _load_json_object(
        paths.order_manifest_path, "order manifest"
    )
    spec_cell = _target_spec_cell(spec, expected_cell_id, paths.expected_kind)
    cell = _target_report_cell(report, expected_cell_id, paths.expected_kind)
    report_members, widths = _report_members(cell, spec_cell, paths.expected_kind)
    _verify_report_widths(cell, widths)
    spec_ids = _spec_member_ids(spec)
    referenced_bundle_ids = set(spec_ids)
    target_ids = {
        row.get("bundle_id")
        for row in report_members
        if isinstance(row.get("bundle_id"), str)
    }
    semantics = report.get("consumption_semantics_id")
```

### 2b. `_verify_report_widths` — the len-mismatch / element-for-element refusal branch

`wtE-mintvocab/scripts/mint_floor_artifact.py:755-779` (complete function):

```python
def _verify_report_widths(
    cell: Mapping[str, Any], widths: Sequence[float]
) -> None:
    floor = cell.get("floor")
    report_widths = (
        floor.get("admissible_half_widths_j")
        if isinstance(floor, Mapping)
        else None
    )
    if (
        not isinstance(report_widths, list)
        or len(report_widths) != len(widths)
        or any(
            not math.isclose(
                _finite(value, "reported admissible width", nonnegative=True),
                expected,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            for value, expected in zip(report_widths, widths)
        )
    ):
        raise MintError(
            "extraction-report widths differ element-for-element from member evidence"
        )
```

### 2c. The `widths` the pinned core reconstructs for the comparative kind

`wtE-mintvocab/scripts/mint_floor_artifact.py:713-752` (comparative branch of `_report_members`,
quoted to the end of the function):

```python
    blocks = spec_cell.get("blocks")
    if not isinstance(blocks, list):
        raise MintError("comparative extraction spec blocks must be an array")
    ordered: list[Mapping[str, Any]] = []
    widths: list[float] = []
    for block in blocks:
        if not isinstance(block, Mapping):
            raise MintError("comparative extraction spec block must be an object")
        block_id = block.get("block_id")
        spec_members = block.get("members")
        if not isinstance(spec_members, Mapping):
            raise MintError("comparative block members must be an object")
        block_rows: list[Mapping[str, Any]] = []
        for position in _ABBA_POSITIONS:
            bundle_id = spec_members.get(position)
            row = by_id.get(bundle_id)
            if (
                not isinstance(row, Mapping)
                or row.get("block_id") != block_id
                or row.get("position") != position
            ):
                raise MintError(
                    "comparative report membership/order differs from extraction spec"
                )
            block_rows.append(row)
        ordered.extend(block_rows)
        widths.append(
            math.fsum(
                _finite(
                    row.get("anchor_shift_bound_j"),
                    f"{row.get('bundle_id')} anchor width",
                    nonnegative=True,
                )
                for row in block_rows
            )
            / 2.0
        )
    if ordered != members:
        raise MintError("comparative report member sequence is not flattened A1/B1/B2/A2")
    return ordered, tuple(widths)
```

### 2d. Common-mode path: per-BLOCK `admissible_half_widths_j` emission

`wtE-mintvocab/joulewise/floor_extraction.py:609-623` (tail of
`_common_mode_floor_from_extracted_inputs`; `block_widths` is appended once per block):

```python
        block_widths.append(
            _common_mode_block_half_width(
                deltas[index],
                onset,
                offset,
                zero_point,
                envelope_sum,
                residuals,
            )
        )

    return comparative_false_effect_floor(
        deltas,
        admissible_half_widths_j=block_widths,
    )
```

`wtE-mintvocab/joulewise/floor_extraction.py:626-649` (the adapter seam the extractor and the new
mint adapter both call, quoted through the argument list shown):

```python
def _common_mode_floor_from_block_inputs(
    block_deltas_j: Sequence[float],
    block_inputs: Sequence[_CommonModeBlockInputs],
    *,
    calibration_bracket: object,
    shared_edge_bound_s: float,
) -> FloorEstimate:
    """Adapt extraction-owned block records to the internal arithmetic seam."""

    return _common_mode_floor_from_extracted_inputs(
        block_deltas_j,
        onset_sweeps_j=[item.onset_values_j for item in block_inputs],
        offset_sweeps_j=[item.offset_values_j for item in block_inputs],
        zero_point_contrasts_j=[
            item.zero_point_contrast_j for item in block_inputs
        ],
        bundle_residual_half_widths_j=[
            item.bundle_residual_half_widths_j for item in block_inputs
        ],
        member_window_bounds_s=[
            item.member_window_bounds_s for item in block_inputs
        ],
        member_envelope_integral_sums_j=[
            item.member_envelope_integral_sum_j for item in block_inputs
```

### 2e. `extract_comparative_cell` dispatch — common-mode branch vs default branch

`wtE-mintvocab/joulewise/floor_extraction.py:2620-2648`:

```python
            elif use_common_mode:
                assert common_mode_bound_s is not None
                assert consumption_session is not None
                extracted_inputs: list[_CommonModeBlockInputs] = []
                try:
                    for evaluated in admitted_blocks:
                        extracted_inputs.append(
                            _common_mode_block_inputs_from_evidence(
                                evaluated,
                                runs_root=runs_root,
                                metric=metric,
                                shared_edge_bound_s=common_mode_bound_s,
                            )
                        )
                    floor = _common_mode_floor_from_block_inputs(
                        block_deltas,
                        extracted_inputs,
                        calibration_bracket=(
                            consumption_session.calibration_bracket
                        ),
                        shared_edge_bound_s=common_mode_bound_s,
                    )
                except CommonModeEstimatorRefusal as exc:
                    refusals.append(exc.reason)
            else:
                floor = comparative_false_effect_floor(
                    block_deltas,
                    admissible_half_widths_j=block_half_widths,
                )
```

### 2f. The report field the pinned core reads back

`wtE-mintvocab/joulewise/floor_extraction.py:1317-1319` (inside `CellReport.as_row`'s `floor_row`):

```python
                "admissible_half_widths_j": list(
                    self.floor.admissible_half_widths_j
                ),
```

---

## 3. Sol worker's F1 flag — verbatim

Source: `mintvocab-out.md:140-147` (the `flags` array entry `F1`, quoted whole):

```json
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: before any authorized dispatch site, pinned core _authenticate_component calls _report_members and _verify_report_widths, reconstructing default ABBA widths. A registered extraction reproduced report width 0.10000000000071085 versus pinned-auth width 1.0 and refused. Options considered: (A) authorize a generalized-v2 authentication seam that preserves all other pinned-core checks, defers comparative report-width equality, and performs spec-selected exact equality only after component and producer pins pass; (B) amend the pinned core with estimator vocabulary, contradicting the unchanged-core contract; (C) retain default-shaped report widths, contradicting the registered extractor and evidence-bound artifact width. Recommendation: A.",
      "needs": "Rule whether option A is authorized and specify the approved deferral mechanism; blocked work is a genuine common-mode CLI mint, full happy path, and complete attack matrix."
    },
```

The three options as stated inside that `text` field, separated for reading (wording unaltered):

- **(A)** "authorize a generalized-v2 authentication seam that preserves all other pinned-core checks, defers comparative report-width equality, and performs spec-selected exact equality only after component and producer pins pass"
- **(B)** "amend the pinned core with estimator vocabulary, contradicting the unchanged-core contract"
- **(C)** "retain default-shaped report widths, contradicting the registered extractor and evidence-bound artifact width"

Trailing sentence of the same field: "Recommendation: A."

### 3a. Companion flags F2 and F3, verbatim (`mintvocab-out.md:148-161`)

```json
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: tests/test_detection_floor.py hard-pins the complete production caller inventory for _common_mode_floor_from_block_inputs. The new governed adapter is correctly detected as an additional caller, making required proof V1 fail, but the test is outside WRITE_SCOPE.",
      "needs": "Expand WRITE_SCOPE prospectively to include tests/test_detection_floor.py so its expected production inventory can admit joulewise/floor_mint_estimator.py:recompute_comparative_estimate."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Python 3.11 focused verification and both full canonical suites were not run after the blocking contract and scope conflicts were confirmed.",
      "needs": "Resume after the ruling and scope expansion, finish the regressions, then execute all six acceptance proofs."
    }
```

### 3b. The worker's observed evidence for F1 (`mintvocab-out.md:174-184`, prose sections quoted whole)

```
## Change

Partial implementation adds the spec-authoritative selector, frozen recomputation flow, construction consumption, and estimator-aware binding. It also adds 22 passing adapter tests. No out-of-scope file was changed, and the pinned mint core remains byte-identical.

## Verification notes

The focused matrix’s sole failure is the out-of-scope production-caller inventory. Separately, the pinned authentication-width reproduction proves that a genuine common-mode report cannot currently reach the three authorized dispatch sites.

## Residual risk

The working tree is intentionally uncommitted and partial. The decision-log note and remaining attack regressions were not added because the implementation cannot honestly be declared complete before the ruling.
```

---

## 4. Option D — surfaced by the stream director, not by the worker

Stated neutrally, as recorded by the stream director (no source file; it does not appear in
`mintvocab-out.md`):

> **Option D.** The extraction report carries per-member source widths in
> `admissible_half_widths_j` and carries the registered per-block widths in a separate field. This
> is a report-schema change plus a matching FCM extractor change. Both lie outside this work
> order's WRITE_SCOPE and outside non-negotiable 4's "UNCHANGED" list (which names report/artifact
> schemas), and it reopens the D-124/FCM lineage.

Scope facts bearing on option D, quoted from the sources already cited above:

- Contract WRITE_SCOPE (`mintvocab-impl-contract.md:3`) lists five paths; neither
  `joulewise/floor_extraction.py` nor any report schema is among them.
- Contract non-negotiable 4 (`mintvocab-impl-contract.md:24-27`): "UNCHANGED:
  scripts/mint_floor_artifact.py (pinned core), scripts/floor_mint_pinsets/schema_v2.json,
  report/artifact schemas, production extraction specs (the pack re-spec is a separate D-133
  consumption step)."
- Contract §4 COST (`mintvocab-impl-contract.md:330-336`): "No changes should be needed in: …
  report or artifact schemas".

---

## 5. Provisional magistrate ruling ALREADY ISSUED

**STATUS: PROVISIONAL — ISSUED TO UNBLOCK THE IN-FLIGHT RUN, MERGE-GATED ON THIS COLD SITTING.**

Verbatim as issued:

> "OPTION A IS AUTHORIZED with five binding conditions: (1) the pinned core
> scripts/mint_floor_artifact.py remains byte-identical — verify and state its sha; (2) the
> generalized-v2 authentication seam must preserve every non-width pinned-core check unweakened
> (component pins, producer pins, member identity — enumerated); (3) the deferred comparative
> report-width equality is REPLACED, not dropped: an exact spec-selected-estimator width equality
> runs unconditionally after component and producer pins pass — never optional, never advisory;
> (4) a differential regression proving a default-path report authenticates byte-identically to
> current pinned-core behavior on default cells; (5) refusal regressions both ways:
> common-mode-shaped widths under a default-selecting spec REFUSE, default-shaped widths under a
> common-mode-selecting spec REFUSE."

### 5a. Mechanical evidence responsive to condition (1), gathered at assembly time

```
main checkout  b670c8fe2fb6eec27b378ff077843ff34ac3463b
  shasum -a 256 scripts/mint_floor_artifact.py
  bf628eed4386b69589c9498cd644c0b3b70513f991f5bb223c70d35f1ca55f5c

wtE-mintvocab  impl/mint-estimator-vocab @ cbf609f (working tree, uncommitted changes present)
  shasum -a 256 scripts/mint_floor_artifact.py
  bf628eed4386b69589c9498cd644c0b3b70513f991f5bb223c70d35f1ca55f5c

  git diff HEAD -- scripts/mint_floor_artifact.py      -> empty
  git diff origin/main -- scripts/mint_floor_artifact.py -> empty
```

---

## 6. Governing doctrine texts

### 6a. D-133 — full decision body (`/Users/edr/code/JouleWise/docs/decision_log.md:8263-8321`, quoted to the end of the section)

```
## D-133: FCM-01 disposition — hybrid + ALT-D120 (cold gate, revised sitting)

**Ruled 2026-08-11 by the mandated cold gate** (fresh Fable adjudicator +
paired Opus contract-lens refuter; revised sitting after the refuter's
brief; magistrate adopted the revised ruling without dissent). Trigger:
the round-6 fresh delta REJECTED on FCM6-01 (registration dictionary
injectable into admitted JSON; validators and the unbound authenticator
accept it), landing outside both branches of the pre-committed decision
rule, and a round 7 would have been the next round on the
fabricated-record-admission class.

**Bench-verified facts that shaped the ruling** (magistrate-executed):
the pinned mint scripts contain ZERO estimator vocabulary — the tighter
two-shared-edge floor cannot reach a minted artifact this cycle under any
disposition without new D-118-gated mint work; no consumer of
`estimator_registration` exists outside its two owning modules (the
forged field is inert); the production claim path binds
`expected_sha256` + `expected_artifact_id`, which the delta's V3
reproduction omitted. The adjudicator's first ruling (round-7
custody-closure) was withdrawn on these facts with concessions on the
record, including that `exact_understatement_found=false` was a
non-finding (lenses unexecuted).

**The disposition:**
(1) Fallback `respec/d124-withdrawn` (681ab49) merges after its own gate
shape (fresh delta audit + re-verified generator/--check/dual-interpreter
evidence + D-121); the pack-freeze lane unblocks at that merge and FCM-01
may not gate it thereafter.
(2) FCM-01 continues as an unmerged desk thread under ALT-D120: DELETE
the serialized registration vocabulary (CellReport.as_row stops emitting
it; removed from _D117_MINT_FLOOR_OPTIONAL_KEYS and _CMP_OPTIONAL_KEYS;
self-equality branch deleted) so both demonstrated forgeries become
closed-profile unknown-key REFUSALS — the D-120 precedent (delete
vocabulary, don't authenticate it). The false round-6 provenance claim
("registered results exist only as governed extraction artifacts") is
corrected to what the design enforces, with a sixth parameter-sha
rotation.
(3) A FULL fresh delta is owed on the branch head (the +497 lines of
moved arithmetic are unaudited; the round-6 delta was interrupted before
its arithmetic lenses). Any exact understatement found there drops the
estimator to the fallback PERMANENTLY under the original pre-committed
rule — no further revival.
(4) Packs re-spec back to the tighter estimator only if ALT-D120 + the
full delta + the mint-estimator vocabulary workstream (new, D-118-gated,
registered in TASK_QUEUE) all land before the freeze wave.
(5) Debts surfaced, not discharged: the FLOOR-COMMONMODE-01 BANKED
UNGATED 425f75f audit debt and the fallback's previously-unstated gate
status enter the ledger.

**Flagged to Ed (schedule call, not ruled):** if the gamma-arm claim
capability must ship in the MAIN paper this cycle, the mint-estimator
workstream becomes critical path and the freeze wave waits by direction —
reversal condition 5 of the ruling. Default absent Ed's direction: the
freeze does not wait; the tighter number banks for the ICPE version.

D-132 is satisfied, not overridden: work continues; consumption is
deferred. The same-signature escalation trigger is satisfied by
resolution through this consult with a structurally different remedy
(deletion, not a third validator).
```

### 6b. D-133 index row (`docs/decision_log.md:157`, quoted whole)

```
| D-133 | FCM-01 DISPOSITION — HYBRID + ALT-D120 (cold gate revised sitting, 2026-08-11): round-6 delta REJECT (FCM6-01, forged registration admitted by validators) adjudicated by fresh Fable + Opus refuter. Fallback respec/d124-withdrawn merges after its own gates (freeze lane unblocks there, decoupled from FCM); FCM-01 continues unmerged under ALT-D120 — DELETE serialized registration vocabulary so forgeries die as closed-profile unknown-key refusals (D-120 precedent); false round-6 provenance claim corrected + sixth sha rotation; FULL fresh delta owed on moved arithmetic (any exact understatement = permanent drop, no further revival); re-spec back to tighter estimator only if ALT-D120 + full delta + new mint-estimator WO all land pre-freeze-wave. Bench-verified: mint has zero estimator vocabulary (tighter floor unmintable this cycle regardless); forged field inert (no consumer); production authenticate binds expected_sha256. Ed schedule call flagged: gamma-arm-in-main-paper would make mint work critical path and hold the wave | adopted (cold gate; magistrate, no dissent) |
```

### 6c. The ALT-D120 identity principle as stated in the operative documents

TASK_QUEUE.md:209-212 (inside the WO row, quoted in full in §6d below):

```
Scope: add governed estimator vocabulary to the mint so a
spec-declared registered estimator's floor passes recomputation +
equality, with provenance re-derived from authenticated members (never
read from admitted JSON, per D-133/ALT-D120).
```

Contract non-negotiable 1 (`mintvocab-impl-contract.md:11-15`):

```
1. NEW shared module joulewise/floor_mint_estimator.py: per-cell
   estimator dispatch whose SOLE authority is the committed pre-registered
   extraction spec (never report/artifact data — ALT-D120 invariant);
   selects between the worst-case default core computation and the
   governed two-shared-edge extraction-path computation.
```

Contract §2 "Authority rule" (`mintvocab-impl-contract.md:226-249`, quoted to the end of the
subsection):

```
### Authority rule

Do not add estimator fields to the v2 pinset, extraction report, floor artifact, or artifact provenance.

The selector is exactly `AuthenticatedComponent.spec_cell["estimator"]`, whose enclosing spec bytes already have:

- exact input authentication;
- component and producer SHA pins;
- membership/config/order pins;
- U10-era source ownership.

The extraction-spec SHA carried through component provenance is the durable indirect commitment. The declared registration authorizes a code path; it is never copied out as claimed provenance.

Selection must be per comparative cell:

- absent or `d054_false_effect_guard.v1` → pinned default core;
- `d124_two_shared_edge_common_mode.v1` → common-mode path only;
- anything else → refusal;
- pending candidate registration → refusal at mint time;
- malformed full registration or calibration basis → refusal, never default fallback.

For common mode, require the spec registration to equal the canonical branch registration exactly, including parameter SHA. Its `calibration_basis` must match the authenticated producer acceptance identity, artifact SHA, derivation SHA/schema, `max(observed_drift_s,0.010818)`, embedding count `1`, and componentwise-max rule. Numeric provenance is rederived from the acceptance, ledger, bracket binding, members, and traces.
```

### 6d. D-118 gauntlet requirement as stated in the WO row (`/Users/edr/code/JouleWise/TASK_QUEUE.md:201-227`, section quoted to its end)

The requirement line is `TASK_QUEUE.md:212-213`: "Full D-118 gauntlet mandatory. Prerequisites:
FCM-01 ALT-D120 round + full fresh delta land clean." It is quoted in situ below.

```
## WO-MINT-ESTIMATOR-VOCAB (D-133 condition; registered 2026-08-11)

Priority: P2 (rises to P0 critical-path ONLY if Ed rules the gamma-arm
claim capability must ship in the main paper this cycle — D-133 flagged
schedule call). The pinned mint scripts (mint_floor_artifact.py,
mint_floor_artifact_generalized.py) carry ZERO estimator vocabulary: the
v2 mint recomputes comparative floors with the default core under an
exact-equality check, so a common-mode-estimator cell CANNOT be minted
today. Scope: add governed estimator vocabulary to the mint so a
spec-declared registered estimator's floor passes recomputation +
equality, with provenance re-derived from authenticated members (never
read from admitted JSON, per D-133/ALT-D120). Full D-118 gauntlet
mandatory. Prerequisites: FCM-01 ALT-D120 round + full fresh delta land
clean. Consumption: packs re-spec back to the tighter estimator only if
this WO + both FCM items land before the freeze wave (D-133 cl.4).

DESIGN ADOPTED (2026-08-11 Sol xhigh consult, magistrate-adjudicated):
one spec-authoritative per-cell estimator dispatch (new shared
joulewise/floor_mint_estimator.py) consumed at ALL THREE mint sites —
postcollection equality, artifact construction, final evidence binding —
because patching steps 8-9 alone leaves a second default-core
recomputation and a default-only binder (the consult's named likely
failure mode). Pinned core, v2 pinset schema, report/artifact schemas,
and production specs all UNCHANGED this WO. Cost estimate 360-540
production LOC + 550-850 test LOC; three audit waves + D-121. Full
consult: session scratchpad mintvocab-consult-out.md (T4-late).
Implementation stacks on impl/floor-commonmode-01 after round 9 lands.
```

### 6e. The contract's own enumeration of the D-118 gauntlet invariants (`mintvocab-impl-contract.md:288-306`, quoted to the end of the subsection)

```
### D-118 gauntlet invariants

The implementation ledger must prove:

1. Estimator authority comes only from the authenticated target comparative spec cell.
2. Spec SHA, membership, config, order, and producer inventory pass before dispatch.
3. No estimator/registration identity appears anywhere in admitted report or artifact JSON.
4. Pending or malformed common-mode registration refuses; no registered-path failure falls back.
5. Spec acceptance declarations match the authenticated acceptance domain owner exactly.
6. Calibration bracket and once-widened bound are rederived from ledger/binding/acceptance evidence.
7. Raw sweeps, residuals, windows, and widths come from authenticated member bytes.
8. Dispatch is cell-local; mixed default/common cells cannot inherit a producer-global choice.
9. One gated recomputation object feeds construction.
10. Report and all U10 numbers remain exact comparisons.
11. Final evidence binding independently uses the same spec selector and exact common-mode widths.
12. Default-only fixtures remain byte-identical to the current v2 output.
13. Common-mode refusal produces no output files.
14. Final-head tests include a one-ULP downward-width attack and the FCM exact-understatement oracle.
15. Any exact common-mode understatement invokes D-133’s permanent fallback, not another repair round.
```

---

## 7. Questions for the cold instance

**Q1.** Does option A preserve the adopted contract's integrity guarantees, or does relocating the
comparative width check out of the pinned core weaken the mint trust surface in a way options
B/C/D would not?

**Q2.** Are the five provisional conditions sufficient; if not, what conditions are missing?

**Q3.** Should option D be preferred despite its scope/lineage cost?

**Q4.** Is the F2 caller-inventory guard widening (admitting
`joulewise/floor_mint_estimator.py:recompute_comparative_estimate` to the exhaustive
`_common_mode_floor_from_block_inputs` caller list) acceptable?

---

## 8. Branch diff inventory — uncommitted working-tree changes at `cbf609f`

Commands run in `/private/tmp/claude-501/-Users-edr-code-JouleWise/7c344e29-f3e2-455c-9384-1902c950c106/scratchpad/wtE-mintvocab`.

`git status -s`:

```
 A joulewise/floor_mint_estimator.py
 M scripts/mint_floor_artifact_generalized.py
 M tests/test_detection_floor.py
 A tests/test_floor_mint_estimator.py
 M tests/test_mint_floor_artifact_generalized.py
```

`git diff HEAD --stat`:

```
 joulewise/floor_mint_estimator.py             | 603 ++++++++++++++++++++++++++
 scripts/mint_floor_artifact_generalized.py    | 196 +++++++--
 tests/test_detection_floor.py                 |   8 +-
 tests/test_floor_mint_estimator.py            | 462 ++++++++++++++++++++
 tests/test_mint_floor_artifact_generalized.py |   3 +-
 5 files changed, 1231 insertions(+), 41 deletions(-)
```

`git diff HEAD --numstat` (added / deleted / path):

```
603	0	joulewise/floor_mint_estimator.py
157	39	scripts/mint_floor_artifact_generalized.py
7	1	tests/test_detection_floor.py
462	0	tests/test_floor_mint_estimator.py
2	1	tests/test_mint_floor_artifact_generalized.py
```

`git diff HEAD -- scripts/mint_floor_artifact.py` and
`git diff origin/main -- scripts/mint_floor_artifact.py`: both empty (no hunks).

**State-drift note (fact, not judgment):** the Sol report's V5/V6 inspections
(`mintvocab-out.md:103-137`) recorded a smaller tree — `tests/test_detection_floor.py` unmodified,
and `git diff --stat` reporting "2 files changed, 87 insertions(+), 40 deletions(-)". The working
tree has advanced since that report was written; the inventory above is the state read at packet
assembly time.

### 8a. Full text of the F2-relevant diff, `tests/test_detection_floor.py`

`git diff HEAD -- tests/test_detection_floor.py`:

```diff
diff --git a/tests/test_detection_floor.py b/tests/test_detection_floor.py
index d35f4f3..3763422 100644
--- a/tests/test_detection_floor.py
+++ b/tests/test_detection_floor.py
@@ -1103,7 +1103,13 @@ class TestTwoSharedEdgeCommonModeFloor(unittest.TestCase):
         self.assertEqual(calls["two_shared_edge_common_mode_floor"], [])
         self.assertEqual(
             calls["_common_mode_floor_from_block_inputs"],
-            [("joulewise/floor_extraction.py", "extract_comparative_cell")],
+            [
+                (
+                    "joulewise/floor_mint_estimator.py",
+                    "recompute_comparative_estimate",
+                ),
+                ("joulewise/floor_extraction.py", "extract_comparative_cell"),
+            ],
         )
         self.assertEqual(
             calls["_common_mode_floor_from_extracted_inputs"],
```

### 8b. Full text of the diff, `tests/test_mint_floor_artifact_generalized.py`

`git diff HEAD -- tests/test_mint_floor_artifact_generalized.py`:

```diff
diff --git a/tests/test_mint_floor_artifact_generalized.py b/tests/test_mint_floor_artifact_generalized.py
index 9392ecc..43a77ac 100644
--- a/tests/test_mint_floor_artifact_generalized.py
+++ b/tests/test_mint_floor_artifact_generalized.py
@@ -5651,7 +5651,7 @@ class V2PinsetAndMintTests(unittest.TestCase):
                         replace(decode, absolute=basis_component)
                     ),
                     ledger_snapshot,
-                    "absolute_evaluation_basis_sha256 mismatch",
+                    "evaluation basis sha256 mismatch",
                 ),
                 (
                     "member-bytes",
@@ -7051,6 +7051,7 @@ print("AUDIT=" + json.dumps({"observed": sorted(observed), "registered": sorted(
                 MintError=mint1.MintError,
                 ComponentPaths=mint1.ComponentPaths,
                 _authenticate_component=mock.Mock(side_effect=authenticate),
+                _verify_report_widths=mint1._verify_report_widths,
             )
             with (
                 mock.patch.object(
```

---

*End of packet. Assembled mechanically; contains no analysis, recommendation, or verdict.*
