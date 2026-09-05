```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Centralize typed admission and cohort checks; retain a census even if full routing misses the cut.","workspace":{"base_requested":"adada921","base_mode":"exact","head_start":"adada9216e4f2072e5305d07eeff2705c6753dbc","head_end":"adada9216e4f2072e5305d07eeff2705c6753dbc","upstream_end":null,"branch":"feat/2026-09-04-fb-metadata"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/42-fb-v2-structural-consult-astra.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"S1","severity":"blocker","title":"R4: unhashable IDs escape named refusal"},{"id":"S2","severity":"should_fix","title":"Predicate accepts 1 as true"},{"id":"S3","severity":"should_fix","title":"Structural closure needs enumeration and enforced routing"}]},"verification":[{"id":"V1","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json\nfrom tests.test_mint_floor_artifact import make_artifact\nfrom joulewise.analysis_engine.inputs import authenticate_floor_artifact_bytes\nfrom joulewise.detection_floor import attribution_single_count_discipline as emit, attribution_single_count_discipline_is_canonical as check\na=make_artifact();a['cells'][0]['single_count_discipline']['rule_id']=[]\ntry: authenticate_floor_artifact_bytes(json.dumps(a).encode())\nexcept TypeError: print('R4: TypeError confirmed')\nelse: raise AssertionError('R4 baseline changed')\nd=emit();d['both_terms_required']=1\nassert check(d)\nprint('S2: integer boolean accepted')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R4: TypeError confirmed","S2: integer boolean accepted"]},"expected":{"exit_code":0,"tail_regex":"S2: integer boolean accepted$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_floor_artifact.ConstructionTests.test_frozen_v1_carriers_keep_bytes_and_render_through_v1_branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.001s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}}],"flags":[]}
```

## Findings

**S1 (blocker):** Six probes (cell/component/group x rule_id=[]/{}) raise TypeError at detection_floor.py:4316 instead of AnalysisInputError. V1 replays one; PASS means defect reproduction.

**S2 (should_fix):** detection_floor.py:413 accepts both_terms_required=1 as true. Check JSON types, including false versus 0.

**S3 (should_fix):** End per-site repair. I disagree that all four rounds are one runtime defect: R2 needs HTML parity. R4 breaks refusal behavior; no acceptance bypass was demonstrated.

**Choke point.** In joulewise/detection_floor.py:
`read_single_count_discipline(carrier, *, where, required=False) -> DisciplineV1 | DisciplineV2 | None`.
None means absent optional unlabelled metadata; sentinel distinguishes null. required=True or attribution label/source requires presence. Check Mapping, string ID BEFORE hashing, supported ID, exact keys/types/values using the emitter's table. Return a frozen detached view; copy_wire() preserves version/key order. No serialized changes.

Raise local SingleCountDisciplineError(ValueError); translate at boundaries, avoiding family cross-imports or blanket TypeError catches. Validators append errors; bytes/aggregation raise AnalysisInputError; resolver returns artifact_schema_invalid/null floors; claims return floor_artifact_invalid/not_estimable/false readiness; finalization raises ClaimArtifactError; mint raises MintError. Generalized public mint translates its loaded core's MintError.

Also add profile-based enumeration: floor cells/both components/groups; extraction root/cells. Include malformed values/required absences BEFORE filtering; reject malformed containers. Cohort/parent-child checks use validated IDs. One FloorResolution adapter treats its unlabelled default None as absence; present JSON null already failed admission. No generic recursive discovery.

**Delta-41 readers, checked at HEAD.** df=detection_floor.py; ae=analysis_engine/; otherwise under joulewise/. Semantic routing preserves bytes/schemas.

| Reader | Route |
|---|---|
| df:400 | Compatibility predicate wraps the accessor. |
| df:3396,3886,4164;4316-4333 | Component/cell/group parse; cohort replaces raw-ID census. |
| ae/inputs.py:895;4327-4380;4474-4520 | Bytes delegates validation; exact/transport parse selected metadata and copy views. |
| ae/__init__.py:230,263,287,298,335,1287 | Adapt ALL resolutions before filtering; cohort; copies/claim forwarding. |
| ae/claims.py:303,316 | Parse supplied metadata; preserve refusal and version. |
| ae/artifact.py:490,2281,2513,2612;3584,3599 | Parse metadata, compare aggregate/resolution/evaluation views; retain finalize/write errors. |
| floor_extraction.py:1431,3120;1470,1495,1598 | Canonical emitters; vocabulary-only declarations/checking. Narrow exceptions, not admission. |
| scripts/mint_floor_artifact.py:1914,1950,1957,2016,2118,2198 | Enumerate/parse/cohort; tagged prose; validate before writes. |
| scripts/mint_floor_artifact_generalized.py:1716,2424,3948,4188,4197 | Indirect validators/writers; add report-discipline admission before reconstruction, separate from D117 vocabulary. |
| scripts/build_site.py:2060 -> docs/site/adapter_contracts.html | Markdown consumer: generated-page parity, no accessor. |
| df-ph-decode-floor-mint1.json + four fill-rehearsal carriers | Data: retain five hash pins and v1 prose coverage (V2 passes). |

**Persistent census:** tests/test_single_count_discipline_census.py scans ALL joulewise/ and scripts/ Python via stdlib AST plus grep backstop. Track outer keys/attributes, API aliases, version literals, distinctive inner keys (planning_sizing_expression/formula), and discipline-derived rule_id reads.

Manifest: path, symbol, access kind, normalized AST, multiplicity; display lines. Fail new/stale entries. Classify parser/emitter/vocabulary/output/typed reader/delegate. Exempt exact floor_extraction vocabulary declarations and canonical emitters separately; other schema-key declarations also need exact exceptions, never file-wide exemptions.

Allow raw loads only in accessor/FloorResolution adapter; outputs use copy_wire()/emitter. Check .get/subscript/attribute/alias; unsupported forms require review. An accessor call elsewhere in the function proves nothing. Pin validator/renderer/both-writer delegate edges. In-memory scanner mutations (new raw read, same-function bypass, alias, deleted edge) must fail. No general taint engine.

**Shape MATRIX:** passing schema-valid v1/v2 baselines; ONE corrupt cell/component/group/extraction-root among valid siblings. Test null/[]/{}/string/missing, rule_id=[]/{}, opposite canonical versions in both orders, unknown/non-string IDs, ID/body swaps, extra fields, bool/int confusion.

| Admission path | Expected outcome / applicability |
|---|---|
| Bytes | Floor carriers: AnalysisInputError. Extraction-root wrong-schema refusal is a control, not discipline coverage. |
| Resolver | Selected cell/group: artifact_schema_invalid, refused/null floors. Other carriers use production admission; pure resolver is local. |
| Aggregation | FloorResolution injection: AnalysisInputError; exact/transported/refused, malformed first/last, absent diagnostics. Root/component chains mutate BEFORE projection. |
| Mint prose + original output helper | Floor/extraction profiles: MintError, no writes. |
| Generalized mint | Both writer branches; extraction root/cells before reconstruction. Public generalized.MintError; helper may raise core.MintError. No three outputs. |

Assert named family AND discipline-specific reason where consumed; never TypeError/KeyError/AttributeError or usable output. Optional absence is a positive control. Record N/A combinations. Add direct claims/finalize/write probes: five paths omit these readers.

**Delete:** ten local canonical checks; R1 guard/ID set/copy filter; R3 collect/validate/ID set; R4 comprehension/interim guard; raw relationship comparisons. Retain domain validation, error adapters, validation-before-write, mixed-version invariants, historical tests/R2 parity. Predicate becomes thin wrapper.

**Acceptance/kills.** Zero unclassified/raw readers; every applicable matrix case passes; five v1 hashes/prose unchanged; exact v2 shape; existing 6/5/4, strict-boundary and asymmetric-endpoint witnesses pass. Run modules individually; lead owns final-head/integration checks. Kill mutations: bypass accessor; skip malformed/root/component/refused carriers; hash raw IDs; force v2-only/normalize v1; remove cohort check; restore bool/int equality; write before validation; lose generalized error translation; restore stale HTML. Each must fail its intended assertion, not unrelated fixture checks. No-output tests use write spies and temporary destinations.

**Cost/cut:** full routing across about eight semantic modules plus tests: 10-16 engineering hours + 4-8 review/integration hours. Possible before 6 September only with protected runway; not a dependable readiness prerequisite.

Prefer R4 + type-exact predicate + named-error tests WITH inventory now: 3-6 hours plus verification. Pin existing raw sites/guards; fail new/stale sites; disclose routing unfinished. Timebox coding to six hours, reserve verification, defer broad routing if tight. I disagree with deferring the census: retain this discovery. If deferred, say "v2 emitted; known readers version-aware; R4 fixed; structural closure unproven"; also fix/dispose S2. D-174 protects claim-path fixes; modularity stays parked. Lead owns the cut.

## Residual risk

Design only. Fixture probes/one compatibility test; no discovery, launchers or hardware. AST covers ordinary edits, not dynamic Python. Lead owns integration/page parity.

M0: no stop card; A151 ACTIVE [AGENT], no dependencies; D-174/ruling-43 read. Clean/exact HEAD. Only report written. Next: lead selects code/test scope.

