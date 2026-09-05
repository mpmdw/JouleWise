```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Round-5 code-level design; carrier conditional on readiness.","workspace":{"base_requested":"677bd504","base_mode":"exact","head_start":"677bd5047ca8928ab1f05fa87e6b12db2fa51c82","head_end":"677bd5047ca8928ab1f05fa87e6b12db2fa51c82","upstream_end":"84b24686d4e11b36d2f6fe64e08616ff3ab1c050","branch":"feat/2026-09-05-seam-round5-spec"},"pathspec":["docs/process_traces/2026-09-04-paper-custody/11-round-5-design-spec-astra.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F3","severity":"blocker"},{"id":"F6","severity":"blocker"},{"id":"F2","severity":"should_fix"},{"id":"F4","severity":"should_fix"},{"id":"F5","severity":"should_fix"}]},"verification":[{"id":"V2","kind":"inspection","cmd":"git rev-parse HEAD origin/feat/2026-09-04-paper-custody-seam 84b24686","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["677bd5047ca8928ab1f05fa87e6b12db2fa51c82","84b24686d4e11b36d2f6fe64e08616ff3ab1c050","84b24686d4e11b36d2f6fe64e08616ff3ab1c050"]},"expected":{"exit_code":0,"tail_regex":"84b24686d4e11b36d2f6fe64e08616ff3ab1c050$"}}],"flags":[{"id":"FL1","kind":"environment","level":"nonblocking","text":"Fetch failed: external FETCH_HEAD write denied (exit 255); cached seam matches. Proposed tests unrun; no suite/launcher.","needs":"Lead verification."}]}
```
## Findings

ROUND-5 SPEC. S=84b24686, H=677bd504; Python paths under joulewise. Whole_window ranges use S. Reads complete; 09 corrects 01/02. Tests proposed.

**F1 — types; landing blocker.** In joulewise/paper_custody.py keep five refs. Reserve VerifiedReportedEnergyParents/VerifiedD165Closeout/VerifiedWholeWindowVerdict/VerifiedClaimEvidence/VerifiedTransferProjection for production; add Fixture siblings by prefix replacement, never inheriting Verified. Private frozen/slotted `_CustodyResult` shares fields/guards and one mint/freezer/replay/reopen pipeline. `_FamilySpec` selects issuing_type/fixture_type; constructor checks family/type/map-bound mode/grant. Each overload returns its pair, e.g. `open_paper_input(ref: D165CloseoutRef) -> VerifiedD165Closeout | FixtureD165Closeout`, including whole-window fixture.

New joulewise/paper_rendering.py: `render_d165(value: VerifiedD165Closeout) -> str`; each renderer accepts its exact issuing family. Mandatory `_issued_renderer(expected_type, required_grant)` checks exact type/token/grant before body/payload. No base/Protocol/Any/Fixture union. Public suppliers accept Ref/open seam. Registry/AST guard requires wrappers everywhere; annotations alone are insufficient. Delete :1309 fixture Verified mint/contract :303–304 boolean obligation; keep token guards. Risk: unguarded renderer.

In tests/test_paper_custody.py: `test_fixture_results_never_enter_any_renderer` (5×renderers, no boolean, body untouched/output empty); `test_issuing_fixture_type_matrix` (ten frozen non-containers, sibling/constructor/tokenless checks, issuing control). In tests/test_authentication_io.py: `test_registered_renderers_require_issuing_boundary`. Kill wrong class, Fixture inheritance, wrapper deletion, widened annotation, unregistered renderer.

**F3 — gates; production blocker.** Replace S:paper_custody.py:1291–1302 BOTH stops. Frozen `_FamilyReplay(authentic: bool, admitted: bool, grants: tuple[_RenderGrant,...], validator_codes: tuple[str,...])`, `_RenderGrant(kind: str, subject_id: str)` with closed family kinds. `_run_issuance_gate(ctx: _GateContext) -> _FamilyReplay` uses private `_ISSUANCE_GATES: dict[tuple[str,str], Callable[[_GateContext],_FamilyReplay]]` (family/version ID). Context: seam-read bindings/inputs/roots/mode. Map v2 adds mode/issuance_gate_id; null stops production, fixtures require null; inventory mode matches. `_FamilySpec` fixes mode-specific censuses. Registered = gate code + mapped inputs/subjects + owner/source census + tests, never receipt/callback unlock.

Authenticate→replay/gate→receipt→reopen all consumed inputs→mint. Fixtures never dispatch gates. Hash gates/grant derivation/policy constants (:460–541); repin current fixture envelopes, preserve history.

| Family / gate ID | Semantics and reused validators |
|---|---|
| reported_energy_parents / `reported-energy.v1` | S:floor_extraction.py:1008 validate_extraction_spec/:1600 validate_d117_mint_consumption_report plus ordered frozen universe/strict bundles, selection/prompt joins. Admission grants only derived registered cells under composed_member_envelope_mean.v1. Gate absent until supplier completes joins. |
| d165_closeout / `d165-closeout.v1` | S:dominance_closeout.py:427 validate_d165_paper_sources invokes finalized validator S:analysis_manifest_v3.py:4452, floor authentication S:analysis_engine/inputs.py:880, sidecar :1115/closeout :1990 in dominance_closeout. Authentic requires all, v5 census and floor acceptance. Admitted = recomputed A or B with no source/structural refusal; both grant outcome. Only A with recomputed dominance_sentence_licensed/subtitle_licensed grants those surfaces (:1949–1986). Branch-null grants no empirical refusal; B is not Q6. |
| claim_evidence / `claim-evidence.v1` | S:analysis_engine/artifact.py:945 validate_claim_verdicts/:607 reevaluation via H:analysis_engine/claims.py:257 evaluate_claim; disk finalized validator, map-pinned floor/embedded equality. New joulewise/analysis_engine/claim_side_bound.py: validate_claim_side_bound(value, *, claim_verdicts_sha256, finalized_manifest, floor_artifact) -> tuple[str,...] binds reader digest, contrast/source-cell, floor lineage/bound arithmetic. Authentic requires joins/acceptance. Outcome grants: current/confirmatory/structurally valid contrast; L2 also requires reevaluated claim_ready_for_l2_l3/ceiling. Aggregate admitted = all selected subjects, never shared mixed-subject licensing. Absent sidecar contract/producer keeps gate absent. |
| whole_window_verdict / `whole-window.v1` | S:whole_window.py:85/:5050 WholeWindowRowValidation/validate_whole_window_verdict_row: authentic plus F6 binding; admitted grants positive, non-admitted only Q6 after F6 lands. Delete :1090 typed-result erasure. |
| transfer_projection / `transfer-projection.v1` | Authenticate/recompute capture, plan, pulse source and bundles plus capture/result acceptance. Admission means diagnostic projection only. :1091 empty fallthrough grants nothing; parked gate stays absent. |

Append production FLOOR_ACCEPTANCE: map-pinned joulewise.paper_floor_acceptance.v1, keys schema_version/floor_sha256/sources/binder_source_sha256/anchor_head/status; sorted unique source path/digests, PASS. Pin after H:floor_mint_estimator.py:598 bind_v2_floor_artifact_evidence per actual floor/sources (widths :683–717). Match floor/sources/binder; missing/stale stops. Keep consumption binder/restricted wording; no receipt family/reconstruction join.

Codes (prefix paper_custody_): delete blocked_pending_receipt/receipt_unissued; add issuance_gate_unregistered/not_issuable/binding_mismatch/issuance_prerequisite_missing for unknown gate/wrong type-grant/subject mismatch/missing acceptance-producer. Keep other 14: owner errors→validator_refused, conflicts→evidence_ambiguous, bad shape-token→request_invalid. All output empty; diagnostics private.

Acceptance in tests/test_paper_custody.py: `test_closed_gate_registry` kills empty-replay/receipt=>issue, unknown default, fixture dispatch; `test_d165_gate_branches_and_floor_acceptance` kills A/B/null collapse, skipped owner/acceptance (missing/wrong-floor controls); `test_claim_gate_per_contrast` kills trusted ready flag/skipped sidecar/embedded floor (supported/unsupported/demoted/mixed and wrong digest/cell/lineage); `test_gate_sources_change_receipt_digest` mutates every owner. Risk: authenticity mistaken for permission.

**F6 — REFUSAL-CARRIER-01: IMPLEMENT ONLY IF READINESS CUT MET.** Lead records CLI/fixture/source-map/acquisition-budget readiness by **6 September** (17/23); otherwise null gate/methods fallback, no empirical Refusal.

joulewise/analysis_manifest_v3.py: frozen `WholeWindowPaperCarrier`, canonical `joulewise.whole_window_paper_carrier.v1`, exact fields:

* schema_version; evidence_class=production; status=passed|failed; claim_licensing=false (never claim authority).
* models: ordered {arm_id,model_tag,realized_stack_identity,identity_sha256}, authenticated config/metadata matched to prospective identities.
* window: {plan_id,plan_sha256,source_campaign_manifests}; authenticated descriptors form window identity.
* evaluation_basis: full authenticated basis/SHA/consumption semantics.
* membership: {planned,observed,failed}: planned run ID/arm/block/position, ordered basis occurrences/digests, authenticated member_failures. Exact one-per-slot cover; missing bytes alone are not failure evidence.
* governing_row: {campaign_log_sha256,row_index,row_sha256,standalone_sha256,prospective_manifest_sha256}; zero-based JSONL ordinal, whole_window.canonical_sha256 for row, byte SHA for files. Exactly one selected row agrees with standalone/all bindings; duplicate/conflicting matches refuse.

Closed wrapper keysets; nested owner schemas. Status pairs only passed/admitted or failed/non-admitted. No numeric claim/reason-derived prose.

`_authenticate_whole_window_paper_carrier(*, prospective_manifest_path: Path, whole_window_verdict_path: Path, campaign_log_path: Path, plan_path: Path, custody_root: Path, runs_root: Path) -> WholeWindowPaperCarrier` takes seam-resolved paths. Reuse S:analysis_manifest_v3.py:1452 _read_strict_object/:1550 _path_under_root/:2951 prospective validator; S:whole_window.py:5050 row validator; S:campaign_provenance.py:410 parse_campaign_log_bytes after strict admission. Delete custody :1016 blanket JSON-object parsing. New `_verify_non_admission_members` checks that exact cover; preserve H:analysis_manifest_v3.py:3015 _verify_basis_members's completed-summary requirement.

Separate carrier path preserves H:analysis_manifest_v3.py:3511–3515 analysis_finalization_verdict_not_passed and :3814–3820 attachment. Add map-pinned generated WHOLE_WINDOW_CARRIER input compared to fresh derivation. Referenced IDs come from prospective plan, not custody :1083 row IDs. Transitive inputs require authenticated descriptors/census/reopen. Keep historical verdicts; amend prospective contract/registry OR-01/DS-32/PG-08. Claim rows name family+role/subject or STOP_FILL.

`render_non_admission(value: VerifiedWholeWindowVerdict) -> str | None` uses F1 wrapper allowing only {positive,non_admission}; non_admission returns exactly “The registered window was not admitted for this submission's claim-bearing comparison”; positive grant returns None. No reasons/exceptions/fallback interpolation.

In tests/test_paper_rendering.py, `test_non_admission_cli_seven_cases` runs real role+runs_root CLI, no mocked opener/validator; synthetic controls stay labelled.

| Case | Expected; kill |
|---|---|
| Authentic FAILED, bound | Fixed sentence only; unconditional stop/admitted-only gate |
| Missing row/carrier | STOP_FILL, no sentence; missing-exception=>sentence |
| Corrupt bytes/provenance | Refuse/no sentence; skipped digest/replay |
| Diagnostic-only/fixture | No sentence, both variants; ignored mode/grant/type |
| Conflicting rows | evidence_ambiguous/no sentence; first/latest selection |
| Wrong window/binding | binding_mismatch/no sentence; individually remove model/window/basis/member/governing-row equality |
| Authentic PASSED, bound | Positive only/no refusal; authentic=>non-admission |

`test_non_admission_carrier_cannot_finalize_or_license_claim`: failed rejected, passed control succeeds; kill relaxed passed gate/schema confusion. Risk: absence becomes empirical failure or claim authority.

**F2 — exact narrowing; before landing.** Replace contract :53–56/:75–81 with 21's text as corrected by 22, adopted by 23:

> A verified result is one of the five frozen, non-container types minted with a construction token created inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161's threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and tokenless `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability.

Also: “The token is recoverable from the closure cells of the private guard functions.” Keep no-public-binding/receipt/reader/parser clauses; add fixture siblings. Step 8/:234:

> Whole-window issuance, admitted or non-admitted, remains stopped until a registered per-family issuance gate lands that requires `WholeWindowRowValidation.authentic` to be true and binds model, window, basis, membership and governing row per ruling 43 Q-17-6; non-admission issuance carries only the fixed Q6 sentence.

Keep residency/F1 guards; delete closure-only/unqualified object.__new__ claims. D-173 edit: dictated seat. `test_contract_threat_model_matches_capability_wire` requires ordinary/closure/private-constructor disclosures; kill “held only inside”/missing “tokenless”. Risk: overclaiming Python.

**F4 — Git-blob role.** First production role production.reported_energy_parents.qwen3-1p7b.v5 / EXTRACTION_SPEC = `configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json` (generator :20 SPEC_REL). Absent at H: prospectively generate/review/commit under D-138/D-166 successor naming, register real full census, repository/git_blob/exact blob SHA; no old-pack substitute.

Replace inert S:paper_custody.py:780 authority: _git_blob (:638)→session.ingest (S:authentication_io.py:490), git:head:path identity/map digest before parse; no-follow worktree bytes equal blob/reopen. Keep generated reads. Git/digest/reopen failures→anchor_unavailable/digest_mismatch/input_changed. Sole current blob call: map :699.

Extend `test_every_family_actual_read_census_refuses_all_three_attack_arms`: map-base roots; raw flip/coherent inventory repin/reopen replacement per repository/transitive read. Mixed fixtures now; `test_production_git_blob_coverage` requires real production role/blob at registration. Kill ignored authority/wrong root/skipped blob comparison/fixture substitute. Risk: fixture mistaken for production.

**F5 — AST census.** Replace tests/test_paper_custody.py:655–658 count with `test_refusal_constructor_ast_census`: literal PaperCustodyRefusal first arguments = registry = contract; variables fail. Observed 16 codes/13 direct: digest_mismatch/input_changed/validator_refused use _raise. Refactor :615 to `_raise(refusal: PaperCustodyRefusal,...)`, attach records/raise exact exception; split :801–829 variable branches. Keep diagnostics/dynamic tests; 18 codes need condition tests. `test_refusal_ast_census_kills_dead_literal` kills constructor replacement+dead string, declared-only code, undeclared call, variable argument. Risk: syntax is not execution; no dummy calls.

## Residual risk

Disagree with 23 on sufficiency: AST is not reachability; git_blob needs dispatch. Accept dispositions/seven cases. Fixture landing cannot claim production coverage.

Next: lead adjudicates/grants implementation scope and records F6 readiness. Unimplemented gates stay absent; no live validation.
