```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"Round 5 F1/F2/F3/F5 and F4 dispatch implemented; fixture landing ready, production registration and F6 remain pending.","workspace":{"base_requested":"55d3bbbe","base_mode":"exact","head_start":"55d3bbbe0904dc7acfd286b725b113eb16e9be5d","head_end":"55d3bbbe0904dc7acfd286b725b113eb16e9be5d","upstream_end":"55d3bbbe0904dc7acfd286b725b113eb16e9be5d","branch":"feat/2026-09-04-paper-custody-seam"},"pathspec":["joulewise/paper_custody.py","joulewise/paper_rendering.py","joulewise/analysis_engine/claim_side_bound.py","docs/contracts/paper_supply_custody.md","configs/paper_supply/supply_map.json","tests/test_paper_custody.py","tests/test_authentication_io.py","tests/test_paper_rendering.py","tests/fixtures/paper_custody/extraction_spec.json","tests/fixtures/paper_custody/repin.py","tests/fixtures/paper_custody/run_kills.py","docs/process_traces/2026-09-04-paper-custody/12-round-5-implementation-report.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"B1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["...............","----------------------------------------------------------------------","Ran 15 tests in 18.751s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 15 tests in [0-9.]+s\\n\\nOK$"}},{"id":"B2","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".....................","----------------------------------------------------------------------","Ran 21 tests in 1.285s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 21 tests in [0-9.]+s\\n\\nOK$"}},{"id":"B3","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["...................................................","----------------------------------------------------------------------","Ran 51 tests in 10.824s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 51 tests in [0-9.]+s\\n\\nOK$"}},{"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["............................","----------------------------------------------------------------------","Ran 28 tests in 30.604s","","OK","KILLED 109 owner-source mutations and 5 grant-policy mutations: stale receipts refused","PENDING production Git-blob role: fixture coverage is not production coverage","KILLED 4 refusal AST mutations: dead literal, undeclared call, variable argument, declared-only code"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 28 tests in [0-9.]+s\\n\\nOK$"}},{"id":"V2","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["......................","----------------------------------------------------------------------","Ran 22 tests in 1.341s","","OK","KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 22 tests in [0-9.]+s\\n\\nOK$"}},{"id":"V3","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_rendering","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["...","----------------------------------------------------------------------","Ran 3 tests in 0.946s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 3 tests in [0-9.]+s\\n\\nOK$"}},{"id":"V4","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["...................................................","----------------------------------------------------------------------","Ran 51 tests in 10.893s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?m)^Ran 51 tests in [0-9.]+s\\n\\nOK$"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["KILL SUMMARY: 35/35 killed; scoped files restored."]},"expected":{"exit_code":0,"tail_regex":"^KILL SUMMARY: 35/35 killed; scoped files restored\\.$"}},{"id":"V6","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"R1","kind":"residual_risk","level":"nonblocking","text":"Ready means non-issuing fixture landing. No production role or actual submission-floor acceptance was issued; the extraction-spec role is explicitly pending desk day.","needs":"Lead registers the reviewed real production blob and complete source census on desk day, then pins actual floor acceptance."},{"id":"R2","kind":"residual_risk","level":"nonblocking","text":"Claim-side-bound validation is an unregistered candidate until its contract/producer exists. Energy joins, transfer acceptance and F6 also remain absent; no empirical non-admission renderer exists.","needs":"Lead owns the 6 September F6 readiness cut and final diff/production verification."}]}
```
## Change

Implemented the authorized Round-5 seam under spec 11, magistrate synthesis 23,
and the adopted D-173 addendum. Intake selected the existing `[AGENT]`
PAPER-CUSTODY-SEAM-01 lane; ACTIVE_STOP_CARD was NONE. The requested branch and
exact base matched, and the initial worktree was clean. No repository commit,
agent launcher, discovery suite, measurement checkout or live capture was used.
The lead-owned running state, queue and decision log were not edited.

| Spec item | Implementation map | Acceptance tests / behavior |
|---|---|---|
| F1 result types | `joulewise/paper_custody.py:247` (`_CustodyResult`); `joulewise/paper_custody.py:162` (`_make_custody_capability_mint`); `joulewise/paper_custody.py:357` (`_FamilySpec`); `joulewise/paper_custody.py:1306` (`open_paper_input`) | Ten frozen/slotted sibling types; all five fixture families now return their `Fixture*` type, including whole window. Constructor checks bind family/type/mode/grants. `test_issuing_fixture_type_matrix` covers constructors, tokenless access, cross-family reconstruction, freezing and deliberate private issuing controls. |
| F1 renderer boundary | `joulewise/paper_rendering.py:14` (`_issued_renderer`); `joulewise/paper_rendering.py:50` (`render_d165`); `tests/test_authentication_io.py:628` (`test_registered_renderers_require_issuing_boundary`) | Five exact issuing-family annotations and runtime wrappers. `test_fixture_results_never_enter_any_renderer` covers all 25 fixture/renderer pairs and untouched spy bodies; runtime rendering tests cover missing and mixed-subject grants. No public boolean check authorizes fixture rendering. |
| F2 exact contract narrowing | `docs/contracts/paper_supply_custody.md`, Terms / Closed public wire / algorithm step 8 | Both spec blockquotes installed verbatim, plus the exact closure-cell disclosure. `test_contract_threat_model_matches_capability_wire` compares against spec 11 and proves ordinary token access and closure recovery. The old boolean rendering obligation and unqualified token claims are removed. |
| F3 registry/replay | `joulewise/paper_custody.py:473` (`_FamilyReplay`); `joulewise/paper_custody.py:481` (`_GateContext`); `joulewise/paper_custody.py:660` (`_run_issuance_gate`); `joulewise/paper_custody.py:1336` (`_open_paper_input_impl`) | Map v2 pins mode, gate ID, subjects and source census. Fixtures require null gate / empty subjects and never dispatch. The closed registry contains only `d165-closeout.v1`. Replay precedes receipt validation; every consumed input is reopened before mint. `test_closed_gate_registry` kills empty replay, receipt promotion, unknown fallback and fixture dispatch. |
| F3 D-165 / acceptance | `joulewise/paper_custody.py:556` (`_d165_issuance_gate`); `joulewise/paper_custody.py:526` (`_validate_floor_acceptance`) | D-165 invokes the existing four-owner adapter / v5 census and recomputes global fields. A/B both grant outcome; only A grants dominance/subtitle; null grants no empirical refusal. The appended production FLOOR_ACCEPTANCE pin checks schema/status/floor/source/binder/anchor. `test_d165_gate_branches_and_floor_acceptance` exercises branches and missing/wrong/stale acceptance controls. |
| F3 claim candidate | `joulewise/paper_custody.py:590` (`_claim_issuance_gate`); `joulewise/analysis_engine/claim_side_bound.py:27` (`validate_claim_side_bound`) | Unregistered candidate: disk finalized validator, verdict validator, actual `evaluate_claim`, embedded-floor equality, reader digest and side-bound joins. Supported/unsupported/demoted/mixed subjects retain separate outcome/L2 grants. Missing explicit source-cell registration refuses. `test_claim_gate_per_contrast` includes wrong digest/cell/lineage/bound and lying ready-flag controls. |
| F3 source pins | `joulewise/paper_custody.py:715` (`_validator_source_census`); `joulewise/paper_custody.py:810` (`_validator_source_sha256`) | Gate/grant/dispatch/mint/mode-census code, policy constants and whole owner modules are pinned. `test_gate_sources_change_receipt_digest` demonstrates 109 owner-source changes and five grant-policy changes refusing old receipts. Current synthetic envelopes were repinned; historical traces and evidence were preserved. |
| F4 dispatch / census | `joulewise/paper_custody.py:1066` (`_read_once`); `configs/paper_supply/supply_map.json`; `tests/fixtures/paper_custody/extraction_spec.json` | Repository Git blobs are read at the anchor, map-hashed before parse, ingested under Git identity, and compared with pinned no-follow worktree reads/reopens. Every fixture has a transitive source; the extraction fixture additionally has a repository Git blob. `test_every_family_actual_read_census_refuses_all_three_attack_arms` exercises raw flips, coherent inventory reseals and replay-to-reopen changes across the actual mixed-root census. |
| F4 production boundary | `tests/test_paper_custody.py:930` (`test_production_git_blob_coverage`) | `production.reported_energy_parents.qwen3-1p7b.v5` remains only in `pending_roles`, with the exact real prospective extraction-spec path. Pending metadata grants no lookup/issuance. The test requires real production mode/path/blob/census when registration exists and explicitly prints PENDING today. Fixture substitution is killed. |
| F5 refusal census | `joulewise/paper_custody.py:890` (`_raise`); `tests/test_paper_custody.py:975` (`test_refusal_constructor_ast_census`); `tests/test_paper_custody.py:981` (`test_refusal_ast_census_kills_dead_literal`) | `_raise` attaches records to an already constructed exception. All 18 registry codes have literal constructor call sites matching the contract. Variable read-error branches are split; dynamic condition tests complement AST equality. Removed both old blanket-stop codes; installed the four specified replacements. |
| F6 | Deferred by explicit instruction | No carrier, failed-finalization path, empirical non-admission renderer or seven-case CLI suite was implemented. `test_non_admission_carrier_is_deferred` protects that boundary. |

## Verification notes

The four permitted final modules ran sequentially, one module at a time: 104
tests passed. The envelope contains their exact observed tails and the three
pre-existing-module baseline tails. `tests.test_paper_rendering` did not exist
at intake; it was run after creation. Discovery was explicitly prohibited by
the user, so the repository's normal discovery instruction was not applied.

The existing real-anchor test wrote a temporary probe in the lead-owned process
trace directory. Before running it, its probe was moved into the authorized
fixture directory; the same actual dirty-anchor refusal remains tested.

One intermediate custody run exposed a test-harness error when a dispatch spy
was itself inspected for source hashing. The test now holds the authentic
baseline source digest while isolating dispatch, with source-hash mutation
behavior independently tested. This was a harness correction, not a production
hash bypass. Captured pilot tail:

```text
AttributeError: __name__
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_request_invalid
Ran 27 tests in 29.559s
FAILED (errors=1)
```

Spec/current-code differences were resolved in favor of the spec: fixture
Verified mints and both unconditional production stops were replaced; whole-
window fixtures can now be inspected without receiving issuing authority;
production IDs remain closed rather than interpreting an empty code tuple as
admission; and refusal reachability checks use AST constructors rather than
literal counts. The revised algorithm retains no whole-window typed-result
erasure or transfer empty-replay issuance path.

Where the spec left wire details open, the implementation chooses explicit,
non-issuing defaults:

- Map v2 uses `source_census` for prospectively pinned transitive inputs and
  `subjects` for selected rendering subjects; `pending_roles` is separate from
  dispatchable roles. Unknown owner reads and duplicate paths across aliased
  roots refuse. The fixtures remain null-gated with no subjects or grants.
- FLOOR_ACCEPTANCE source paths use `repository/` or `runs_root/` prefixes to
  distinguish roots. Its recorded anchor must be an ancestor of the consuming
  map anchor, since the map commit pins an acceptance produced earlier and
  cannot contain its own future commit hash.
- The side-bound scaffold requires explicit registered `source_cell_ids` and
  uses the owner's `lower`/`upper` interval vocabulary. There is no inference
  of a production source-cell join and no claim gate registration. Its shape
  remains a candidate for the missing producer/contract.

Gate-policy A/B/null and claim controls isolate owner authentication with mocks;
claim outcome reevaluation and side-bound arithmetic run the real code. Private
token-bearing reconstruction appears only in labeled synthetic renderer
controls. These controls are not live hardware or production issuance evidence.
The unchanged D-165 module's 51 tests also ran independently.

The mutation runner repins current fixture receipts under each code mutation,
so a stale fixture digest cannot masquerade as a targeted kill. Each child
executes one named test from a permitted module; every child below exited 1
with a unittest FAILED result. The runner exited 0, with:

```text
KILL SUMMARY: 35/35 killed; scoped files restored.
```

Exact kill tails follow. Each replay command reinstalls only the named mutation,
runs the indicated test, and restores the original scoped bytes. A child failure
is expected; the replay wrapper succeeds only when the mutation is killed.

**F1-wrong-class** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_issuing_fixture_type_matrix`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-wrong-class`

```text
    return _construct_verified(_custody_token, output_type, evidence, payload)
  File "/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py", line 199, in construct_verified
    raise PaperCustodyRefusal("paper_custody_not_issuable")
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_not_issuable

----------------------------------------------------------------------
Ran 1 test in 0.682s

FAILED (errors=1)
```

**F1-fixture-inherits-verified** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_issuing_fixture_type_matrix`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-fixture-inherits-verified`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 754, in test_issuing_fixture_type_matrix
    self.assertFalse(issubclass(spec.fixture_type, spec.issuing_type))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.890s

FAILED (failures=1)
```

**F1-wrapper-deleted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io.PaperRendererBoundaryTests.test_registered_renderers_require_issuing_boundary`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-wrapper-deleted`

```text
'render_d165: missing exact issuing wrapper'

- ('render_d165: missing exact issuing wrapper',)
+ ()

----------------------------------------------------------------------
Ran 1 test in 0.043s

FAILED (failures=1)
```

**F1-annotation-widened** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io.PaperRendererBoundaryTests.test_registered_renderers_require_issuing_boundary`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-annotation-widened`

```text
'render_d165: widened issuing annotation'

- ('render_d165: widened issuing annotation',)
+ ()

----------------------------------------------------------------------
Ran 1 test in 0.043s

FAILED (failures=1)
```

**F1-unregistered-renderer** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io.PaperRendererBoundaryTests.test_registered_renderers_require_issuing_boundary`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-unregistered-renderer`

```text
'unregistered or missing public renderer'

- ('unregistered or missing public renderer',)
+ ()

----------------------------------------------------------------------
Ran 1 test in 0.043s

FAILED (failures=1)
```

**F1-grant-check-deleted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_rendering.PaperRenderingTests.test_d165_issued_control_and_subject_grants`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F1-grant-check-deleted`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_rendering.py", line 23, in test_d165_issued_control_and_subject_grants
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.647s

FAILED (failures=1)
```

**F2-closure-only-overclaim** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_contract_threat_model_matches_capability_wire`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F2-closure-only-overclaim`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 966, in test_contract_threat_model_matches_capability_wire
    self.assertIn(exact, contract)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: "A verified result is one of the five frozen, non-container types minted with a construction token created inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161's threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and tokenless `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability." not found in '# Paper supply custody\n\nStatus: normative for `PAPER-CUSTODY-SEAM-01`. **D-173** is the adopted, amended\nproject decision that every paper supplier must obtain claim-bearing evidence\nthrough one shared custody-read seam; its full decision and veto status are in\nthe [decision log](../decision_log.md#d-173-paper-supply-custody--one-custody-read-seam-for-every-claim-bearing-paper-input-magistrate-provisional-2026-09-04).\nThis document is D-173\'s single normative home.\n\n## Terms\n\nA **paper supplier** is code that converts analysis evidence into a paper fill,\ntable cell, token, or professor-facing sentence. The **custody seam** is\n`joulewise.paper_custody.open_paper_input(ref)`, the only public operation that\nadmits evidence to such code.\n\nA **family** is one of the five closed kinds of paper evidence listed below. A\n**role** is a lowercase supply-map key, such as\n`fixture.reported_energy_parents`, that selects exactly one registered family\nand its complete input set. A caller may supply that role string and a **runs\nroot**, meaning one existing directory under which run-generated evidence is\nstored. The caller may supply nothing else that selects or authenticates input\nbytes.\n\nThe **supply map** is the Git-tracked JSON file\n`configs/paper_supply/supply_map.json`. It maps each role to its family,\nrelative input paths, expected SHA-256 digests, and validator identifier. Each\nentry also names a **custody inventory**, a map-pinned object repeating the\ncomplete input census, and a **receipt**, a map-pinned producer record that\ncorroborates the exact inputs and a fresh validator replay. The map is the\nrepository-owned source of every locator and expected digest; a caller cannot\nreplace or supplement it.\n\nAn **anchor** is the pair `(repository, head)` returned by the fixed-repository,\nclean-tree function `joulewise.identity_pins._mint_git_anchor()`, plus the\nsupply-map blob read from that exact commit. The function calls the generalized\nmint\'s Git-state implementation on its fixed `REPO_ROOT`, requires a 40-digit\n`HEAD`, and runs `git status --porcelain --untracked-files=all`. Any tracked or\nuntracked change refuses the anchor, including an untracked file outside the\nsupply-map paths. This strict rule is intentional: the paper build is a\nrelease operation, and an operator must stage, commit, ignore, or remove all\nuntracked scratch material before it can read. The returned `HEAD` must also be\nprovably contained in local `origin/main`; false or unknown containment\nrefuses. Synthetic tests may replace this private anchor call only while\nexercising a map-pinned `test_fixture_non_issuing` inventory. The public\nproduction path exposes no fixture switch and always executes the real gate.\n\nThe custody inventory and receipt are corroborating structures, not independent\nauthority: changing evidence and minting replacements cannot change the\nGit-anchored supply map.\n\nA **fresh replay** runs the current owning validator code in-process over the\nbytes read in the current call. A **reopen** reads every selected input again\nafter replay.\n\nA verified result is one of the five frozen, non-container types minted with a construction token held only inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161\'s threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and tokenless `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability.\n\nThe token is recoverable from the closure cells of the private guard functions.\nEvidence records the authorizing anchor commit and exact supply-map SHA-256,\ninput digests, selected subjects, and family-specific rendering grants.\n**Issuance** means releasing a result that may authorize paper text.\n\n\n## Closed public wire\n\n`open_paper_input(ref)` accepts exactly one of these frozen reference types.\nEvery reference has exactly two fields, in this order: `role: str` and\n`runs_root: pathlib.Path`.\n\n| Reference | Verified result | Meaning |\n|---|---|---|\n| `ReportedEnergyParentsRef` | `VerifiedReportedEnergyParents` | **D-123**, the ratified decision to preregister and report phase-energy mean cells, together with its governed parents ([decision log](../decision_log.md#d-123-ruling-2-yes--the-signal-size-doctrine--the-overnight-license-ed-2026-08-08)) |\n| `D165CloseoutRef` | `VerifiedD165Closeout` | **D-165**, the adopted falsifier requiring every attribution-dominance ratio to reach the fixed twofold threshold before licensing the headline ([decision log](../decision_log.md#d-165-the-falsifier-magistrate--cold-gate-2026-08-28)) |\n| `WholeWindowVerdictRef` | `VerifiedWholeWindowVerdict` | One authenticated whole-window admission verdict row and its provenance |\n| `ClaimEvidenceRef` | `VerifiedClaimEvidence` | `claim_verdicts.v1`, `claim_side_bound.v1`, and their authenticated parents |\n| `TransferProjectionRef` | `VerifiedTransferProjection` | The diagnostic inserted-gap transfer projection used by **TR-01**, the branch-independent paper fill that states whether the measured transfer supports applying the pulse-derived timing bound ([registry row](../paper/results-fill-registry.md#L920)) |\n\nThe module exports no path/digest binding class and no receipt reference class.\nIt exposes no public reader, parser, replay dispatcher, payload constructor, or\nverified-result constructor. Calling `CustodyEvidence` or any `Verified*` or\n`Fixture*` class directly refuses with `paper_custody_request_invalid`.\nPrivate construction requires the token described above. Each verified family\nhas a distinct `Fixture` sibling by prefix replacement, including\n`FixtureWholeWindowVerdict`. The ten types share private frozen/slotted\n`_CustodyResult`; no fixture inherits a verified class. Each opener overload\nreturns only its issuing/fixture pair.\n\n`joulewise.paper_rendering` registers five renderers: `render_reported_energy`,\n`render_d165`, `render_whole_window`, `render_claim`, and `render_transfer`.\nEach accepts exactly its issuing family and runs `_issued_renderer` before\nits body or payload access. The wrapper checks exact type, token, family,\nproduction mode, selected subjects and the required grant for every subject.\nFixture results never enter any renderer, without a caller boolean check.\nThe registry and AST census reject unwrapped, widened, or unregistered public\nrenderers. Public suppliers accept refs and use the opener.\n\n\n## Supply-map schema and lookup\n\nThe supply map is strict JSON with this exact shape:\n\n```text\n{\n  "schema_version": "joulewise.paper_supply_map.v2",\n  "pending_roles": {"<pending role>": {"status": "pending_desk_day", "family": "<family>", "input_role": "<role>", "base": "repository", "authority": "git_blob", "path": "<prospective path>"}},\n  "roles": {\n    "<role>": {\n      "family": "<closed family>",\n      "mode": "production|test_fixture_non_issuing",\n      "issuance_gate_id": "<registered family/version ID or null>",\n      "subjects": ["<selected subject ID>"],\n      "source_census": [{"authority": "git_blob|generated", "base": "repository|runs_root", "expected_sha256": "<digest>", "path": "<relative path>"}],\n      "inputs": [\n        {\n          "authority": "git_blob|generated",\n          "base": "repository|runs_root",\n          "expected_sha256": "<64 lowercase hex>",\n          "path": "<relative POSIX path>",\n          "role": "<closed input role>"\n        }\n      ],\n      "inventory": {\n        "base": "repository|runs_root",\n        "expected_sha256": "<64 lowercase hex>",\n        "path": "<relative POSIX path>"\n      },\n      "receipt": {\n        "base": "repository|runs_root",\n        "expected_sha256": "<64 lowercase hex>",\n        "path": "<relative POSIX path>"\n      },\n      "validator": "joulewise.paper_custody.<family>.v1"\n    }\n  }\n}\n```\n\nEvery object has exactly the keys shown. A role key matches\n`[a-z0-9][a-z0-9_.-]*`. Each path is a nonempty relative POSIX path with no\nempty, `.`, `..`, absolute, or backslash component. `git_blob` authority is\nvalid only with `base: repository`. Paths and closed input roles are unique\nwithin the fixed family inputs. The additional `source_census` may repeat the\nprivate `authenticated_source` role but must have unique base/path identities\nacross all inputs. The `inputs` array order must exactly equal the family order\nbelow; sorting or accepting an extra input is nonconforming.\n\nLookup is exact and mechanical:\n\n1. Validate the concrete ref type, role grammar, and `Path`-typed runs root;\n   resolve the runs root strictly and require a directory.\n2. Call the private `_mint_git_anchor(require_origin_main=True)` release form.\n   Do not accept a repository, commit, map path, map bytes, containment\n   override, fixture switch, or anchor from the caller.\n3. Start a new `V2AuthenticationReadSession`. Run\n   `git -C <repository> show <head>:configs/paper_supply/supply_map.json`, then\n   pass those exact bytes to the active session as the identity\n   `git:<head>:configs/paper_supply/supply_map.json` with strict JSON grammar.\n4. Look up `roles[ref.role]`; absence is\n   `paper_custody_role_unregistered`. Require the entry\'s `family` to equal the\n   family fixed by the concrete ref class, its validator to equal\n   `joulewise.paper_custody.<family>.v1`, and its ordered input roles to equal\n   the mode-specific family census below.\n5. Convert the entry to private bindings. `base: repository` resolves under the\n   fixed anchor repository; `base: runs_root` resolves under the caller\'s runs\n   root. No public binding, inventory, receipt, path, digest, validator, or\n   source-digest parameter exists.\n\nThe fixed map currently registers five synthetic roles only. Their bytes carry\n`synthetic-no-measurement-value`; map and inventory modes must agree on\n`test_fixture_non_issuing`, gate ID must be null, and subjects must be empty.\nEach returns its distinct `Fixture*` type. The reported-energy fixture exercises\na repository `git_blob` extraction spec, and every fixture has a transitive\nsource read in its census. These are synthetic authentication controls.\n\nThe production role `production.reported_energy_parents.qwen3-1p7b.v5` is\n**pending**, recorded only in `pending_roles`, which grants no lookup or\nissuance authority. Its prospective `EXTRACTION_SPEC` is\n`configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json`. Desk-day\nregistration must use the real reviewed/committed blob and full production\ncensus under D-138/D-166 successor naming; a fixture or old pack cannot replace\nit. Production Git-blob coverage remains unfulfilled until that registration.\n\n\n## Family censuses\n\n**D-117** is the adopted prospective three-window replacement for the retired\nhistorical remint plan; it defines the present floor/mint parent chain\n([decision log](../decision_log.md#d-117-d-110s-historical-re-mint-order-superseded--prospective-three-window-replacement-option-2-adopted-d-113-readiness-rewired)).\n**G2-a** is the first diagnostic machine evening that probes four registered\nprefill lengths and produces the later selected-length record; it is defined by\nthe [live queue row](../../TASK_QUEUE.md#current-queue). These definitions bind\nthe reported-energy input names below.\n\n| Family | Ordered input roles |\n|---|---|\n| Reported energy | `extraction_spec`, `extraction_report` (the D-117 mint-consumption report), `whole_window_basis`, `g2a_selection` (the G2-a selection record), `prompt_pin` |\n| D-165 close-out | `d165_closeout`, `finalized_manifest`, `floor_artifact`, `replay_sidecar` |\n| Whole window | `campaign_log`, `standalone_verdict`, `prospective_manifest`, `plan` |\n| Claims | `claim_verdicts`, `claim_side_bound`, `finalized_manifest`, `floor_artifact` |\n| Transfer | `transfer_result`, `reviewed_capture`, `plan`, `pre_data_receipt`, `pulse_bound_source`, `bundle_inventory` |\n\nProduction D-165 and claim inputs append `floor_acceptance` to their fixed\ncensus. Every map entry also pins its complete transitive `source_census`;\nunmapped owner reads refuse.\n\nEvery family additionally reads its `custody_inventory` and\n`validator_receipt` locators from the same map entry.\n\n## Read, replay, receipt, and reopen algorithm\n\nAfter role resolution, the seam performs these steps in order inside the one\nfresh `V2AuthenticationReadSession`:\n\n1. Read the map-pinned inventory with `read_nofollow_pinned`. The session\n   rejects symlinks, containment escapes, non-regular files, digest mismatch,\n   malformed UTF-8/JSON, duplicate keys, and non-finite numbers before bytes\n   enter seam logic.\n2. Require inventory schema `joulewise.paper_custody_inventory.v1` and exact\n   keys `family`, `files`, `inventory_id`, `mode`, `schema_version`. Each file\n   row has exactly `authority`, `path`, `role`, `sha256` and must equal the\n   corresponding map binding. The rows are exactly the family input roles plus\n   `validator_receipt`; duplicates or omissions refuse.\n3. Read all fixed and transitive inputs and the receipt with the map\'s base,\n   path and expected digest. A `git_blob` input first runs anchored `git show`,\n   checks the map digest **before parsing**, and enters the session under\n   `git:<head>:<path>`. Its no-follow worktree bytes must match that same pin;\n   reopening checks both blob and worktree. Generated inputs retain pinned\n   no-follow reads. The inventory corroborates the entire ordered source set.\n4. Authenticate and replay the family gate. `_FamilyReplay` preserves separate\n   `authentic`, `admitted`, `grants` and `validator_codes` fields. Fixtures only\n   replay synthetic documents and never dispatch an issuance gate. Production\n   requires a closed `(family, issuance_gate_id)` registry hit; null or unknown\n   IDs stop. Empty replay/receipts never authorize issuance.\n5. Validate the canonical newline-terminated receipt: exact fields `family`,\n   `inputs`, `replay_codes`, `schema_version`, `status`, `validator`, and\n   `validator_source_sha256`; schema `joulewise.paper_custody_receipt.v1`,\n   status `PASS`, and sorted `{path, role, sha256}` rows for all consumed\n   sources. Its validator digest hashes family, policy constants, registered\n   gate IDs, gate/dispatch/grant/mint code, mode census and owning validators.\n   The executable census in `_validator_source_census` names each member;\n   source is UTF-8 `inspect.getsource`, with NUL separators. Whole owner\n   modules are also pinned so helper code and policy constants cannot drift\n   behind an unchanged validator entry point. The receipt\'s\n   replay codes must match fresh replay exactly; diagnostics are private.\n6. Check that all actual owner reads belong to the mapped fixed/transitive\n   census. The map is authority; an owner callback or receipt is never an\n   extra source authorization channel.\n7. Call the replay/reopen boundary and reread inventory, every fixed/transitive\n   source and receipt through the same session/pins. Changed inputs refuse.\n8. Build frozen evidence with anchor/map digest, selected subjects and grants,\n   then mint only the mode-specific family type. Production needs authentic,\n   admitted replay and the closed required grant for every selected subject.\n\nWhole-window issuance, admitted or non-admitted, remains stopped until a registered per-family issuance gate lands that requires `WholeWindowRowValidation.authentic` to be true and binds model, window, basis, membership and governing row per ruling 43 Q-17-6; non-admission issuance carries only the fixed Q6 sentence.\n\n\n## Family replay requirements\n\nThe future reported-energy gate must replay `validate_extraction_spec` and\n`validate_d117_mint_consumption_report`. Its production entry must also\ninventory the full ordered `reported_energy_cells[].members` universe and every\nstrict-bundle input consumed by the projection.\n\nD-165 replays the finalized-manifest validator, floor authentication,\n`validate_d165_replay_sidecar`, and `validate_d165_closeout`. The adapter and\nthe exhaustive professor-facing refusal vocabulary live in the real producer\nmodule `joulewise/dominance_closeout.py`. Its\n`D165_CLOSEOUT_REFUSAL_CODES` set and `D165_OR01_REASON_SENTENCES` map have\nexactly equal keys, and the test mutation-probes additions on both sides.\n\nD-165\'s `d165-closeout.v1` gate reuses its paper-source adapter, including\nfinalized-manifest/floor/sidecar/closeout validation and the v5 census. It\nrecomputes global fields from validated ratios. A and B license the outcome;\nonly A with recomputed licensing flags grants dominance sentence/subtitle.\nBranch null does not license an empirical refusal. B is not Q6. The subject is\nthe exact supply role.\n\nClaims have an unregistered candidate gate with disk manifest validation,\n`validate_claim_verdicts`, reevaluation via `evaluate_claim`, embedded-floor\nbyte equality and `validate_claim_side_bound`. The sidecar scaffold checks the\nreader digest, explicit registered contrast/source-cell join, floor identity\nand decision-bound arithmetic; the gate compares those bounds to verdict\nfields. Missing explicit source-cell registration refuses. This candidate\nwire is not an adopted sidecar contract/producer, so `claim-evidence.v1`\nremains absent. Outcome grants require each selected contrast to be current,\nconfirmatory and structurally valid; L2 additionally needs reevaluated\nreadiness/ceiling. Mixed subjects never share licensing.\n\nReported-energy joins, the claim-sidecar contract/producer, whole-window F6\nand transfer acceptance are incomplete, so their gates remain unregistered.\nThe whole-window typed validator remains in the source census; no flattened\nempty-code result can replace its authenticity/admission semantics. F6 and its\nempirical non-admission renderer are not implemented in Round 5.\n\n### Floor acceptance\n\nProduction D-165 and claims require a map-pinned artifact with exact keys\n`schema_version`, `floor_sha256`, `sources`, `binder_source_sha256`,\n`anchor_head`, `status`, schema `joulewise.paper_floor_acceptance.v1`, and\nstatus `PASS`. Sources are sorted unique `{path, sha256}` rows matching the\nmapped authenticated source census; path is prefixed `repository/` or\n`runs_root/` to disambiguate roots. Floor bytes and current binder source hash\nmust match. The acceptance anchor must be an ancestor of the current clean\nanchor: it precedes the commit that pins the acceptance digest, avoiding a\nself-referential commit hash. Missing/stale acceptance stops issuance.\n\nBefore submission the lead runs `bind_v2_floor_artifact_evidence` once on each\nactual submission floor and its authenticated sources, then pins the pass\nbeside the finalized manifest. Fixtures do not satisfy this gate. Floors are\n"reconstructed from authenticated member sources once, at mint (and re-checked\nonce before submission); at analysis consumption validated against the widths\nrecorded in the floor artifact and byte-sealed by the finalized manifest, not\nre-derived". Consumption retains the existing binder; full reconstructed\ncustody joins remain post-submission work. Acceptance is a pinned prerequisite,\nnot a new receipt family or an execution callback that unlocks a gate.\n\n\n## Lower-boundary closures\n\n`joulewise.campaign_provenance.load_campaign_log_rows` accepts only `log_path`\nand reads its bytes through the authentication input API; it has no\n`raw_bytes` substitution channel. The floor loader\'s normative wire is\n`joulewise.analysis_engine.inputs.load_floor_artifact(path) -> AuthenticatedFloorArtifact`.\nThe returned object is the authenticated capability itself; no public\n`(Mapping, digest)` projection is part of this wire.\n\nThe authentication AST guard includes `joulewise/paper_custody.py`, every\nsupplier owner module in the validator census, and both\n`joulewise.analysis_engine.inputs` and `joulewise.analysis_manifest_v3`.\nEvidence reads in those modules route through the active authentication\nsession. The manifest\'s three append-only publisher reads are explicitly\nclassified by the lint as writer-state/idempotence/directory-fsync operations,\nnot evidence admission. The guard does not treat subprocess stdout as a direct\nfilesystem read; the seam\'s `git show` bytes are therefore registered by an\nexplicit `session.ingest` call. The public-wire test parses all five ref class\nbodies rather than trusting only the outer `open_paper_input(ref)` signature.\nIt requires exactly `role` and `runs_root` and rejects reintroduction of public\nbinding or receipt types.\n\n## Closed refusals and exception translation\n\nThis is the exhaustive refusal-code registry. A declared code without the\nlisted reachable condition, or a raise-site code absent from this table, is a\ncontract failure.\n\n| Code | Reachable condition |\n|---|---|\n| `paper_custody_request_invalid` | Invalid ref/value shape, private-capability construction/access, or translated unexpected ordinary exception |\n| `paper_custody_anchor_unavailable` | Dirty/unreadable Git state, HEAD not provably contained in `origin/main`, or failed anchored `git show` |\n| `paper_custody_anchor_mismatch` | A custody-inventory locator, authority, or digest disagrees with the Git-anchored supply-map binding |\n| `paper_custody_supply_map_invalid` | Supply-map schema, family, validator, role ordering, path, digest, or binding grammar is invalid |\n| `paper_custody_role_unregistered` | The requested role is absent from the anchored map |\n| `paper_custody_path_refused` | Runs root or a resolved input path is unsafe, non-directory, symlinked, or non-regular |\n| `paper_custody_input_unreadable` | A required root or input cannot be read |\n| `paper_custody_digest_mismatch` | Input bytes disagree with the map-pinned SHA-256 before parsing |\n| `paper_custody_parse_invalid` | Pinned bytes fail strict UTF-8, JSON/JSONL, duplicate-key, or finite-number admission |\n| `paper_custody_issuance_gate_unregistered` | Null or unknown family/version production gate; pending roles never unlock it |\n| `paper_custody_not_issuable` | Wrong issuing/fixture type, malformed replay, non-admission or missing required grant |\n| `paper_custody_binding_mismatch` | Selected subject/grant or side-bound join mismatch; unmapped owner reads |\n| `paper_custody_issuance_prerequisite_missing` | Missing/stale floor acceptance, floor/source/binder/anchor mismatch or absent required producer input |\n| `paper_custody_receipt_invalid` | Inventory or validator-receipt schema/canonical form/status is invalid |\n| `paper_custody_receipt_binding_mismatch` | Receipt input census, validator source digest, or replay-code binding disagrees |\n| `paper_custody_validator_refused` | Fresh owning-validator replay returns one or more private diagnostic codes |\n| `paper_custody_evidence_ambiguous` | Duplicate paths/roles or a non-exact inventory census prevents unique evidence selection |\n| `paper_custody_input_changed` | Reopen detects replacement, removal, grammar/digest change, or different bytes after replay |\n\nEvery public-entry failure is `PaperCustodyRefusal` with a code from the closed\n`paper_custody_*` set and empty `rendered_output`. This includes malformed\nprimitive types before regex/path operations, Git/subprocess failures, supply\nmap failures, JSON/UTF-8 failures, missing files, nested or already-active\nauthentication sessions, validator exceptions, replay changes, and private\nconstruction attempts. `KeyboardInterrupt`, `SystemExit`, and other\n`BaseException` control flow are not converted.\n\nThe read census and nested validator codes are diagnostic metadata only. They\ncannot be interpolated into paper prose. Registered renderers require their\nexact issuing type, private token and per-subject grants before payload access.\nThe refusal AST census requires literal constructor arguments and exact equality\nbetween executable call sites, the 18-code registry and this table. Dynamic\ncondition tests complement the census; dead strings are not execution evidence.\n'

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

**F2-tokenless-omitted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_contract_threat_model_matches_capability_wire`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F2-tokenless-omitted`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 966, in test_contract_threat_model_matches_capability_wire
    self.assertIn(exact, contract)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: "A verified result is one of the five frozen, non-container types minted with a construction token created inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161's threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and tokenless `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability." not found in '# Paper supply custody\n\nStatus: normative for `PAPER-CUSTODY-SEAM-01`. **D-173** is the adopted, amended\nproject decision that every paper supplier must obtain claim-bearing evidence\nthrough one shared custody-read seam; its full decision and veto status are in\nthe [decision log](../decision_log.md#d-173-paper-supply-custody--one-custody-read-seam-for-every-claim-bearing-paper-input-magistrate-provisional-2026-09-04).\nThis document is D-173\'s single normative home.\n\n## Terms\n\nA **paper supplier** is code that converts analysis evidence into a paper fill,\ntable cell, token, or professor-facing sentence. The **custody seam** is\n`joulewise.paper_custody.open_paper_input(ref)`, the only public operation that\nadmits evidence to such code.\n\nA **family** is one of the five closed kinds of paper evidence listed below. A\n**role** is a lowercase supply-map key, such as\n`fixture.reported_energy_parents`, that selects exactly one registered family\nand its complete input set. A caller may supply that role string and a **runs\nroot**, meaning one existing directory under which run-generated evidence is\nstored. The caller may supply nothing else that selects or authenticates input\nbytes.\n\nThe **supply map** is the Git-tracked JSON file\n`configs/paper_supply/supply_map.json`. It maps each role to its family,\nrelative input paths, expected SHA-256 digests, and validator identifier. Each\nentry also names a **custody inventory**, a map-pinned object repeating the\ncomplete input census, and a **receipt**, a map-pinned producer record that\ncorroborates the exact inputs and a fresh validator replay. The map is the\nrepository-owned source of every locator and expected digest; a caller cannot\nreplace or supplement it.\n\nAn **anchor** is the pair `(repository, head)` returned by the fixed-repository,\nclean-tree function `joulewise.identity_pins._mint_git_anchor()`, plus the\nsupply-map blob read from that exact commit. The function calls the generalized\nmint\'s Git-state implementation on its fixed `REPO_ROOT`, requires a 40-digit\n`HEAD`, and runs `git status --porcelain --untracked-files=all`. Any tracked or\nuntracked change refuses the anchor, including an untracked file outside the\nsupply-map paths. This strict rule is intentional: the paper build is a\nrelease operation, and an operator must stage, commit, ignore, or remove all\nuntracked scratch material before it can read. The returned `HEAD` must also be\nprovably contained in local `origin/main`; false or unknown containment\nrefuses. Synthetic tests may replace this private anchor call only while\nexercising a map-pinned `test_fixture_non_issuing` inventory. The public\nproduction path exposes no fixture switch and always executes the real gate.\n\nThe custody inventory and receipt are corroborating structures, not independent\nauthority: changing evidence and minting replacements cannot change the\nGit-anchored supply map.\n\nA **fresh replay** runs the current owning validator code in-process over the\nbytes read in the current call. A **reopen** reads every selected input again\nafter replay.\n\nA verified result is one of the five frozen, non-container types minted with a construction token created inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161\'s threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability.\n\nThe token is recoverable from the closure cells of the private guard functions.\nEvidence records the authorizing anchor commit and exact supply-map SHA-256,\ninput digests, selected subjects, and family-specific rendering grants.\n**Issuance** means releasing a result that may authorize paper text.\n\n\n## Closed public wire\n\n`open_paper_input(ref)` accepts exactly one of these frozen reference types.\nEvery reference has exactly two fields, in this order: `role: str` and\n`runs_root: pathlib.Path`.\n\n| Reference | Verified result | Meaning |\n|---|---|---|\n| `ReportedEnergyParentsRef` | `VerifiedReportedEnergyParents` | **D-123**, the ratified decision to preregister and report phase-energy mean cells, together with its governed parents ([decision log](../decision_log.md#d-123-ruling-2-yes--the-signal-size-doctrine--the-overnight-license-ed-2026-08-08)) |\n| `D165CloseoutRef` | `VerifiedD165Closeout` | **D-165**, the adopted falsifier requiring every attribution-dominance ratio to reach the fixed twofold threshold before licensing the headline ([decision log](../decision_log.md#d-165-the-falsifier-magistrate--cold-gate-2026-08-28)) |\n| `WholeWindowVerdictRef` | `VerifiedWholeWindowVerdict` | One authenticated whole-window admission verdict row and its provenance |\n| `ClaimEvidenceRef` | `VerifiedClaimEvidence` | `claim_verdicts.v1`, `claim_side_bound.v1`, and their authenticated parents |\n| `TransferProjectionRef` | `VerifiedTransferProjection` | The diagnostic inserted-gap transfer projection used by **TR-01**, the branch-independent paper fill that states whether the measured transfer supports applying the pulse-derived timing bound ([registry row](../paper/results-fill-registry.md#L920)) |\n\nThe module exports no path/digest binding class and no receipt reference class.\nIt exposes no public reader, parser, replay dispatcher, payload constructor, or\nverified-result constructor. Calling `CustodyEvidence` or any `Verified*` or\n`Fixture*` class directly refuses with `paper_custody_request_invalid`.\nPrivate construction requires the token described above. Each verified family\nhas a distinct `Fixture` sibling by prefix replacement, including\n`FixtureWholeWindowVerdict`. The ten types share private frozen/slotted\n`_CustodyResult`; no fixture inherits a verified class. Each opener overload\nreturns only its issuing/fixture pair.\n\n`joulewise.paper_rendering` registers five renderers: `render_reported_energy`,\n`render_d165`, `render_whole_window`, `render_claim`, and `render_transfer`.\nEach accepts exactly its issuing family and runs `_issued_renderer` before\nits body or payload access. The wrapper checks exact type, token, family,\nproduction mode, selected subjects and the required grant for every subject.\nFixture results never enter any renderer, without a caller boolean check.\nThe registry and AST census reject unwrapped, widened, or unregistered public\nrenderers. Public suppliers accept refs and use the opener.\n\n\n## Supply-map schema and lookup\n\nThe supply map is strict JSON with this exact shape:\n\n```text\n{\n  "schema_version": "joulewise.paper_supply_map.v2",\n  "pending_roles": {"<pending role>": {"status": "pending_desk_day", "family": "<family>", "input_role": "<role>", "base": "repository", "authority": "git_blob", "path": "<prospective path>"}},\n  "roles": {\n    "<role>": {\n      "family": "<closed family>",\n      "mode": "production|test_fixture_non_issuing",\n      "issuance_gate_id": "<registered family/version ID or null>",\n      "subjects": ["<selected subject ID>"],\n      "source_census": [{"authority": "git_blob|generated", "base": "repository|runs_root", "expected_sha256": "<digest>", "path": "<relative path>"}],\n      "inputs": [\n        {\n          "authority": "git_blob|generated",\n          "base": "repository|runs_root",\n          "expected_sha256": "<64 lowercase hex>",\n          "path": "<relative POSIX path>",\n          "role": "<closed input role>"\n        }\n      ],\n      "inventory": {\n        "base": "repository|runs_root",\n        "expected_sha256": "<64 lowercase hex>",\n        "path": "<relative POSIX path>"\n      },\n      "receipt": {\n        "base": "repository|runs_root",\n        "expected_sha256": "<64 lowercase hex>",\n        "path": "<relative POSIX path>"\n      },\n      "validator": "joulewise.paper_custody.<family>.v1"\n    }\n  }\n}\n```\n\nEvery object has exactly the keys shown. A role key matches\n`[a-z0-9][a-z0-9_.-]*`. Each path is a nonempty relative POSIX path with no\nempty, `.`, `..`, absolute, or backslash component. `git_blob` authority is\nvalid only with `base: repository`. Paths and closed input roles are unique\nwithin the fixed family inputs. The additional `source_census` may repeat the\nprivate `authenticated_source` role but must have unique base/path identities\nacross all inputs. The `inputs` array order must exactly equal the family order\nbelow; sorting or accepting an extra input is nonconforming.\n\nLookup is exact and mechanical:\n\n1. Validate the concrete ref type, role grammar, and `Path`-typed runs root;\n   resolve the runs root strictly and require a directory.\n2. Call the private `_mint_git_anchor(require_origin_main=True)` release form.\n   Do not accept a repository, commit, map path, map bytes, containment\n   override, fixture switch, or anchor from the caller.\n3. Start a new `V2AuthenticationReadSession`. Run\n   `git -C <repository> show <head>:configs/paper_supply/supply_map.json`, then\n   pass those exact bytes to the active session as the identity\n   `git:<head>:configs/paper_supply/supply_map.json` with strict JSON grammar.\n4. Look up `roles[ref.role]`; absence is\n   `paper_custody_role_unregistered`. Require the entry\'s `family` to equal the\n   family fixed by the concrete ref class, its validator to equal\n   `joulewise.paper_custody.<family>.v1`, and its ordered input roles to equal\n   the mode-specific family census below.\n5. Convert the entry to private bindings. `base: repository` resolves under the\n   fixed anchor repository; `base: runs_root` resolves under the caller\'s runs\n   root. No public binding, inventory, receipt, path, digest, validator, or\n   source-digest parameter exists.\n\nThe fixed map currently registers five synthetic roles only. Their bytes carry\n`synthetic-no-measurement-value`; map and inventory modes must agree on\n`test_fixture_non_issuing`, gate ID must be null, and subjects must be empty.\nEach returns its distinct `Fixture*` type. The reported-energy fixture exercises\na repository `git_blob` extraction spec, and every fixture has a transitive\nsource read in its census. These are synthetic authentication controls.\n\nThe production role `production.reported_energy_parents.qwen3-1p7b.v5` is\n**pending**, recorded only in `pending_roles`, which grants no lookup or\nissuance authority. Its prospective `EXTRACTION_SPEC` is\n`configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json`. Desk-day\nregistration must use the real reviewed/committed blob and full production\ncensus under D-138/D-166 successor naming; a fixture or old pack cannot replace\nit. Production Git-blob coverage remains unfulfilled until that registration.\n\n\n## Family censuses\n\n**D-117** is the adopted prospective three-window replacement for the retired\nhistorical remint plan; it defines the present floor/mint parent chain\n([decision log](../decision_log.md#d-117-d-110s-historical-re-mint-order-superseded--prospective-three-window-replacement-option-2-adopted-d-113-readiness-rewired)).\n**G2-a** is the first diagnostic machine evening that probes four registered\nprefill lengths and produces the later selected-length record; it is defined by\nthe [live queue row](../../TASK_QUEUE.md#current-queue). These definitions bind\nthe reported-energy input names below.\n\n| Family | Ordered input roles |\n|---|---|\n| Reported energy | `extraction_spec`, `extraction_report` (the D-117 mint-consumption report), `whole_window_basis`, `g2a_selection` (the G2-a selection record), `prompt_pin` |\n| D-165 close-out | `d165_closeout`, `finalized_manifest`, `floor_artifact`, `replay_sidecar` |\n| Whole window | `campaign_log`, `standalone_verdict`, `prospective_manifest`, `plan` |\n| Claims | `claim_verdicts`, `claim_side_bound`, `finalized_manifest`, `floor_artifact` |\n| Transfer | `transfer_result`, `reviewed_capture`, `plan`, `pre_data_receipt`, `pulse_bound_source`, `bundle_inventory` |\n\nProduction D-165 and claim inputs append `floor_acceptance` to their fixed\ncensus. Every map entry also pins its complete transitive `source_census`;\nunmapped owner reads refuse.\n\nEvery family additionally reads its `custody_inventory` and\n`validator_receipt` locators from the same map entry.\n\n## Read, replay, receipt, and reopen algorithm\n\nAfter role resolution, the seam performs these steps in order inside the one\nfresh `V2AuthenticationReadSession`:\n\n1. Read the map-pinned inventory with `read_nofollow_pinned`. The session\n   rejects symlinks, containment escapes, non-regular files, digest mismatch,\n   malformed UTF-8/JSON, duplicate keys, and non-finite numbers before bytes\n   enter seam logic.\n2. Require inventory schema `joulewise.paper_custody_inventory.v1` and exact\n   keys `family`, `files`, `inventory_id`, `mode`, `schema_version`. Each file\n   row has exactly `authority`, `path`, `role`, `sha256` and must equal the\n   corresponding map binding. The rows are exactly the family input roles plus\n   `validator_receipt`; duplicates or omissions refuse.\n3. Read all fixed and transitive inputs and the receipt with the map\'s base,\n   path and expected digest. A `git_blob` input first runs anchored `git show`,\n   checks the map digest **before parsing**, and enters the session under\n   `git:<head>:<path>`. Its no-follow worktree bytes must match that same pin;\n   reopening checks both blob and worktree. Generated inputs retain pinned\n   no-follow reads. The inventory corroborates the entire ordered source set.\n4. Authenticate and replay the family gate. `_FamilyReplay` preserves separate\n   `authentic`, `admitted`, `grants` and `validator_codes` fields. Fixtures only\n   replay synthetic documents and never dispatch an issuance gate. Production\n   requires a closed `(family, issuance_gate_id)` registry hit; null or unknown\n   IDs stop. Empty replay/receipts never authorize issuance.\n5. Validate the canonical newline-terminated receipt: exact fields `family`,\n   `inputs`, `replay_codes`, `schema_version`, `status`, `validator`, and\n   `validator_source_sha256`; schema `joulewise.paper_custody_receipt.v1`,\n   status `PASS`, and sorted `{path, role, sha256}` rows for all consumed\n   sources. Its validator digest hashes family, policy constants, registered\n   gate IDs, gate/dispatch/grant/mint code, mode census and owning validators.\n   The executable census in `_validator_source_census` names each member;\n   source is UTF-8 `inspect.getsource`, with NUL separators. Whole owner\n   modules are also pinned so helper code and policy constants cannot drift\n   behind an unchanged validator entry point. The receipt\'s\n   replay codes must match fresh replay exactly; diagnostics are private.\n6. Check that all actual owner reads belong to the mapped fixed/transitive\n   census. The map is authority; an owner callback or receipt is never an\n   extra source authorization channel.\n7. Call the replay/reopen boundary and reread inventory, every fixed/transitive\n   source and receipt through the same session/pins. Changed inputs refuse.\n8. Build frozen evidence with anchor/map digest, selected subjects and grants,\n   then mint only the mode-specific family type. Production needs authentic,\n   admitted replay and the closed required grant for every selected subject.\n\nWhole-window issuance, admitted or non-admitted, remains stopped until a registered per-family issuance gate lands that requires `WholeWindowRowValidation.authentic` to be true and binds model, window, basis, membership and governing row per ruling 43 Q-17-6; non-admission issuance carries only the fixed Q6 sentence.\n\n\n## Family replay requirements\n\nThe future reported-energy gate must replay `validate_extraction_spec` and\n`validate_d117_mint_consumption_report`. Its production entry must also\ninventory the full ordered `reported_energy_cells[].members` universe and every\nstrict-bundle input consumed by the projection.\n\nD-165 replays the finalized-manifest validator, floor authentication,\n`validate_d165_replay_sidecar`, and `validate_d165_closeout`. The adapter and\nthe exhaustive professor-facing refusal vocabulary live in the real producer\nmodule `joulewise/dominance_closeout.py`. Its\n`D165_CLOSEOUT_REFUSAL_CODES` set and `D165_OR01_REASON_SENTENCES` map have\nexactly equal keys, and the test mutation-probes additions on both sides.\n\nD-165\'s `d165-closeout.v1` gate reuses its paper-source adapter, including\nfinalized-manifest/floor/sidecar/closeout validation and the v5 census. It\nrecomputes global fields from validated ratios. A and B license the outcome;\nonly A with recomputed licensing flags grants dominance sentence/subtitle.\nBranch null does not license an empirical refusal. B is not Q6. The subject is\nthe exact supply role.\n\nClaims have an unregistered candidate gate with disk manifest validation,\n`validate_claim_verdicts`, reevaluation via `evaluate_claim`, embedded-floor\nbyte equality and `validate_claim_side_bound`. The sidecar scaffold checks the\nreader digest, explicit registered contrast/source-cell join, floor identity\nand decision-bound arithmetic; the gate compares those bounds to verdict\nfields. Missing explicit source-cell registration refuses. This candidate\nwire is not an adopted sidecar contract/producer, so `claim-evidence.v1`\nremains absent. Outcome grants require each selected contrast to be current,\nconfirmatory and structurally valid; L2 additionally needs reevaluated\nreadiness/ceiling. Mixed subjects never share licensing.\n\nReported-energy joins, the claim-sidecar contract/producer, whole-window F6\nand transfer acceptance are incomplete, so their gates remain unregistered.\nThe whole-window typed validator remains in the source census; no flattened\nempty-code result can replace its authenticity/admission semantics. F6 and its\nempirical non-admission renderer are not implemented in Round 5.\n\n### Floor acceptance\n\nProduction D-165 and claims require a map-pinned artifact with exact keys\n`schema_version`, `floor_sha256`, `sources`, `binder_source_sha256`,\n`anchor_head`, `status`, schema `joulewise.paper_floor_acceptance.v1`, and\nstatus `PASS`. Sources are sorted unique `{path, sha256}` rows matching the\nmapped authenticated source census; path is prefixed `repository/` or\n`runs_root/` to disambiguate roots. Floor bytes and current binder source hash\nmust match. The acceptance anchor must be an ancestor of the current clean\nanchor: it precedes the commit that pins the acceptance digest, avoiding a\nself-referential commit hash. Missing/stale acceptance stops issuance.\n\nBefore submission the lead runs `bind_v2_floor_artifact_evidence` once on each\nactual submission floor and its authenticated sources, then pins the pass\nbeside the finalized manifest. Fixtures do not satisfy this gate. Floors are\n"reconstructed from authenticated member sources once, at mint (and re-checked\nonce before submission); at analysis consumption validated against the widths\nrecorded in the floor artifact and byte-sealed by the finalized manifest, not\nre-derived". Consumption retains the existing binder; full reconstructed\ncustody joins remain post-submission work. Acceptance is a pinned prerequisite,\nnot a new receipt family or an execution callback that unlocks a gate.\n\n\n## Lower-boundary closures\n\n`joulewise.campaign_provenance.load_campaign_log_rows` accepts only `log_path`\nand reads its bytes through the authentication input API; it has no\n`raw_bytes` substitution channel. The floor loader\'s normative wire is\n`joulewise.analysis_engine.inputs.load_floor_artifact(path) -> AuthenticatedFloorArtifact`.\nThe returned object is the authenticated capability itself; no public\n`(Mapping, digest)` projection is part of this wire.\n\nThe authentication AST guard includes `joulewise/paper_custody.py`, every\nsupplier owner module in the validator census, and both\n`joulewise.analysis_engine.inputs` and `joulewise.analysis_manifest_v3`.\nEvidence reads in those modules route through the active authentication\nsession. The manifest\'s three append-only publisher reads are explicitly\nclassified by the lint as writer-state/idempotence/directory-fsync operations,\nnot evidence admission. The guard does not treat subprocess stdout as a direct\nfilesystem read; the seam\'s `git show` bytes are therefore registered by an\nexplicit `session.ingest` call. The public-wire test parses all five ref class\nbodies rather than trusting only the outer `open_paper_input(ref)` signature.\nIt requires exactly `role` and `runs_root` and rejects reintroduction of public\nbinding or receipt types.\n\n## Closed refusals and exception translation\n\nThis is the exhaustive refusal-code registry. A declared code without the\nlisted reachable condition, or a raise-site code absent from this table, is a\ncontract failure.\n\n| Code | Reachable condition |\n|---|---|\n| `paper_custody_request_invalid` | Invalid ref/value shape, private-capability construction/access, or translated unexpected ordinary exception |\n| `paper_custody_anchor_unavailable` | Dirty/unreadable Git state, HEAD not provably contained in `origin/main`, or failed anchored `git show` |\n| `paper_custody_anchor_mismatch` | A custody-inventory locator, authority, or digest disagrees with the Git-anchored supply-map binding |\n| `paper_custody_supply_map_invalid` | Supply-map schema, family, validator, role ordering, path, digest, or binding grammar is invalid |\n| `paper_custody_role_unregistered` | The requested role is absent from the anchored map |\n| `paper_custody_path_refused` | Runs root or a resolved input path is unsafe, non-directory, symlinked, or non-regular |\n| `paper_custody_input_unreadable` | A required root or input cannot be read |\n| `paper_custody_digest_mismatch` | Input bytes disagree with the map-pinned SHA-256 before parsing |\n| `paper_custody_parse_invalid` | Pinned bytes fail strict UTF-8, JSON/JSONL, duplicate-key, or finite-number admission |\n| `paper_custody_issuance_gate_unregistered` | Null or unknown family/version production gate; pending roles never unlock it |\n| `paper_custody_not_issuable` | Wrong issuing/fixture type, malformed replay, non-admission or missing required grant |\n| `paper_custody_binding_mismatch` | Selected subject/grant or side-bound join mismatch; unmapped owner reads |\n| `paper_custody_issuance_prerequisite_missing` | Missing/stale floor acceptance, floor/source/binder/anchor mismatch or absent required producer input |\n| `paper_custody_receipt_invalid` | Inventory or validator-receipt schema/canonical form/status is invalid |\n| `paper_custody_receipt_binding_mismatch` | Receipt input census, validator source digest, or replay-code binding disagrees |\n| `paper_custody_validator_refused` | Fresh owning-validator replay returns one or more private diagnostic codes |\n| `paper_custody_evidence_ambiguous` | Duplicate paths/roles or a non-exact inventory census prevents unique evidence selection |\n| `paper_custody_input_changed` | Reopen detects replacement, removal, grammar/digest change, or different bytes after replay |\n\nEvery public-entry failure is `PaperCustodyRefusal` with a code from the closed\n`paper_custody_*` set and empty `rendered_output`. This includes malformed\nprimitive types before regex/path operations, Git/subprocess failures, supply\nmap failures, JSON/UTF-8 failures, missing files, nested or already-active\nauthentication sessions, validator exceptions, replay changes, and private\nconstruction attempts. `KeyboardInterrupt`, `SystemExit`, and other\n`BaseException` control flow are not converted.\n\nThe read census and nested validator codes are diagnostic metadata only. They\ncannot be interpolated into paper prose. Registered renderers require their\nexact issuing type, private token and per-subject grants before payload access.\nThe refusal AST census requires literal constructor arguments and exact equality\nbetween executable call sites, the 18-code registry and this table. Dynamic\ncondition tests complement the census; dead strings are not execution evidence.\n'

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

**F3-empty-replay-issues** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-empty-replay-issues`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.612s

FAILED (failures=1)
```

**F3-receipt-issues-fixture** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-receipt-issues-fixture`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.776s

FAILED (failures=1)
```

**F3-unknown-gate-default** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-unknown-gate-default`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.615s

FAILED (failures=1)
```

**F3-fixture-dispatches-gate** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-fixture-dispatches-gate`

```text
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py", line 900, in _raise
    raise refusal
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_validator_refused

----------------------------------------------------------------------
Ran 1 test in 0.766s

FAILED (errors=1)
```

**F3-d165-B-collapsed** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-d165-B-collapsed`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 819, in test_d165_gate_branches_and_floor_acceptance
    self.assertEqual(result.admitted, branch is not None)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False != True

----------------------------------------------------------------------
Ran 1 test in 0.655s

FAILED (failures=1)
```

**F3-d165-null-issues** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-d165-null-issues`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 819, in test_d165_gate_branches_and_floor_acceptance
    self.assertEqual(result.admitted, branch is not None)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True != False

----------------------------------------------------------------------
Ran 1 test in 0.661s

FAILED (failures=1)
```

**F3-d165-A-grants-lost** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-d165-A-grants-lost`

```text
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Items in the second set but not the first:
'dominance_sentence'
'subtitle'

----------------------------------------------------------------------
Ran 1 test in 0.626s

FAILED (failures=1)
```

**F3-d165-owner-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-d165-owner-skipped`

```text
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/unittest/mock.py", line 965, in assert_called_once
    raise AssertionError(msg)
AssertionError: Expected 'validate_d165_paper_sources' to have been called once. Called 0 times.

----------------------------------------------------------------------
Ran 1 test in 0.634s

FAILED (failures=1)
```

**F3-acceptance-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-acceptance-skipped`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.634s

FAILED (failures=1)
```

**F3-wrong-floor-accepted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-wrong-floor-accepted`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.691s

FAILED (failures=1)
```

**F3-claim-ready-flag-trusted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-claim-ready-flag-trusted`

```text
    self.assertEqual({(grant.kind, grant.subject_id) for grant in result.grants}, kinds)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Items in the first set but not the second:
('l2', 'unsupported')

----------------------------------------------------------------------
Ran 1 test in 0.668s

FAILED (failures=1)
```

**F3-claim-owner-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-claim-owner-skipped`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 887, in test_claim_gate_per_contrast
    self.assertEqual(owner.call_count, 5); self.assertEqual(disk.call_count, 5); self.assertEqual(side.call_count, 5)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 5

----------------------------------------------------------------------
Ran 1 test in 0.793s

FAILED (failures=1)
```

**F3-sidecar-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-sidecar-skipped`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 887, in test_claim_gate_per_contrast
    self.assertEqual(owner.call_count, 5); self.assertEqual(disk.call_count, 5); self.assertEqual(side.call_count, 5)
                                                                                 ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 5

----------------------------------------------------------------------
Ran 1 test in 0.717s

FAILED (failures=1)
```

**F3-embedded-floor-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-embedded-floor-skipped`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py", line 545, in _validate_floor_acceptance
    raise PaperCustodyRefusal("paper_custody_issuance_prerequisite_missing",
                              input_role=InputRole.FLOOR_ACCEPTANCE)
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_issuance_prerequisite_missing:floor_acceptance

----------------------------------------------------------------------
Ran 1 test in 0.715s

FAILED (errors=1)
```

**F3-sidecar-wrong-digest** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-sidecar-wrong-digest`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 895, in test_claim_gate_per_contrast
    self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.718s

FAILED (failures=1)
```

**F3-sidecar-wrong-cell** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-sidecar-wrong-cell`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 892, in test_claim_gate_per_contrast
    self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.727s

FAILED (failures=1)
```

**F3-sidecar-wrong-lineage** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-sidecar-wrong-lineage`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 892, in test_claim_gate_per_contrast
    self.assertFalse(custody._claim_issuance_gate(dataclasses.replace(ctx, subjects=("supported",))).authentic)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.716s

FAILED (failures=1)
```

**F3-sidecar-wrong-bound** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-sidecar-wrong-bound`

```text
                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py", line 629, in _claim_issuance_gate
    raise PaperCustodyRefusal("paper_custody_binding_mismatch")
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_binding_mismatch

----------------------------------------------------------------------
Ran 1 test in 0.715s

FAILED (errors=1)
```

**F3-source-owner-omitted** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_gate_sources_change_receipt_digest`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F3-source-owner-omitted`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 918, in test_gate_sources_change_receipt_digest
    self.assertIn(required, members)
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
AssertionError: 'analysis_engine.claims.evaluate_claim' not found in {'paper_custody._replay_family': <function _replay_family at 0x1091a5d20>, 'paper_custody._validate_fixture_documents': <function _validate_fixture_documents at 0x1091a5a60>, 'paper_custody._validate_production_documents': <function _validate_production_documents at 0x1091a5bc0>, 'paper_custody._run_issuance_gate': <function _run_issuance_gate at 0x1091a4300>, 'paper_custody._validate_grants': <function _validate_grants at 0x1091b7110>, 'paper_custody._validate_floor_acceptance': <function _validate_floor_acceptance at 0x1091b7e20>, 'paper_custody._floor_binder_source_sha256': <function _floor_binder_source_sha256 at 0x1091b7cc0>, 'paper_custody._d165_issuance_gate': <function _d165_issuance_gate at 0x1091a4040>, 'paper_custody._claim_issuance_gate': <function _claim_issuance_gate at 0x1091a41a0>, 'paper_custody._make_custody_capability_mint': <function _make_custody_capability_mint at 0x1091045c0>, 'paper_custody._FamilySpec': <class 'joulewise.paper_custody._FamilySpec'>, 'paper_custody._load_supply_entry': <function _load_supply_entry at 0x1091a54e0>, 'paper_custody._read_once': <function _read_once at 0x1091a5640>, 'paper_custody._open_paper_input_impl': <function _open_paper_input_impl at 0x1091a6820>, 'analysis_engine.artifact._validate_cross_field_claim_semantics': <function _validate_cross_field_claim_semantics at 0x1096505c0>, 'analysis_engine.claim_side_bound.validate_claim_side_bound': <function validate_claim_side_bound at 0x1096537f0>, 'analysis_engine.claim_side_bound._interval': <function _interval at 0x109653690>, 'analysis_manifest_v3.validate_finalized_analysis_manifest_v3': <function validate_finalized_analysis_manifest_v3 at 0x10997c300>, 'analysis_engine.artifact.validate_claim_verdicts': <function validate_claim_verdicts at 0x109650b40>, 'floor_mint_estimator.bind_v2_floor_artifact_evidence': <function bind_v2_floor_artifact_evidence at 0x109a30a90>, 'module:joulewise.analysis_engine.artifact': <module 'joulewise.analysis_engine.artifact' from '/Users/edr/code/JouleWise-wt-paper-custody/joulewise/analysis_engine/artifact.py'>, 'module:joulewise.analysis_engine.claim_side_bound': <module 'joulewise.analysis_engine.claim_side_bound' from '/Users/edr/code/JouleWise-wt-paper-custody/joulewise/analysis_engine/claim_side_bound.py'>, 'module:joulewise.analysis_manifest_v3': <module 'joulewise.analysis_manifest_v3' from '/Users/edr/code/JouleWise-wt-paper-custody/joulewise/analysis_manifest_v3.py'>, 'module:joulewise.floor_mint_estimator': <module 'joulewise.floor_mint_estimator' from '/Users/edr/code/JouleWise-wt-paper-custody/joulewise/floor_mint_estimator.py'>, 'module:joulewise.paper_custody': <module 'joulewise.paper_custody' from '/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py'>}

----------------------------------------------------------------------
Ran 1 test in 1.423s

FAILED (failures=1)
```

**F4-authority-ignored** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_git_blob_dispatch_checks_blob_before_parse_and_worktree`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F4-authority-ignored`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 705, in assert_code
    with self.assertRaises(custody.PaperCustodyRefusal) as raised:
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: PaperCustodyRefusal not raised

----------------------------------------------------------------------
Ran 1 test in 0.644s

FAILED (failures=1)
```

**F4-wrong-root** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_git_blob_dispatch_checks_blob_before_parse_and_worktree`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F4-wrong-root`

```text
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/joulewise/paper_custody.py", line 900, in _raise
    raise refusal
joulewise.paper_custody.PaperCustodyRefusal: paper_custody_input_unreadable:extraction_spec

----------------------------------------------------------------------
Ran 1 test in 0.663s

FAILED (errors=1)
```

**F4-blob-comparison-skipped** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_git_blob_dispatch_checks_blob_before_parse_and_worktree`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F4-blob-comparison-skipped`

```text
AssertionError: 'paper_custody_parse_invalid' != 'paper_custody_digest_mismatch'
- paper_custody_parse_invalid
+ paper_custody_digest_mismatch


----------------------------------------------------------------------
Ran 1 test in 0.633s

FAILED (failures=1)
```

**F4-fixture-substitute** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_production_git_blob_coverage`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F4-fixture-substitute`

```text
   'input_role': 'extraction_spec',
-  'path': 'tests/fixtures/paper_custody/extraction_spec.json',
+  'path': 'configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json',
   'status': 'pending_desk_day'}

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

**F5-dead-literal** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_refusal_constructor_ast_census`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F5-dead-literal`

```text
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 680, in _assert_refusal_census
    raise AssertionError("refusal constructor/registry/contract census mismatch")
AssertionError: refusal constructor/registry/contract census mismatch

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

**F5-declared-only** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_refusal_constructor_ast_census`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F5-declared-only`

```text
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 978, in test_refusal_constructor_ast_census
    self.assertEqual(codes, custody.PAPER_CUSTODY_REFUSAL_CODES)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: {'paper_custody_evidence_ambiguous', 'pap[587 chars]tch'} != frozenset({'paper_custody_validator_refus[629 chars]ch'})

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

**F5-undeclared-call** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_refusal_constructor_ast_census`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F5-undeclared-call`

```text
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 680, in _assert_refusal_census
    raise AssertionError("refusal constructor/registry/contract census mismatch")
AssertionError: refusal constructor/registry/contract census mismatch

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

**F5-variable-argument** — child `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody.RoundFiveTests.test_refusal_constructor_ast_census`; observed/expected child exit 1.

Replay: `PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/paper_custody/run_kills.py F5-variable-argument`

```text
       ~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_paper_custody.py", line 673, in _refusal_ast_codes
    raise AssertionError("refusal constructor requires a literal first argument")
AssertionError: refusal constructor requires a literal first argument

----------------------------------------------------------------------
Ran 1 test in 0.009s

FAILED (failures=1)
```

## Residual risk

This is ready for the ratified non-issuing fixture landing. Actual production
Git-blob coverage, actual submission FLOOR_ACCEPTANCE binder execution/pinning,
reported-energy joins, the claim-sidecar producer/contract, transfer acceptance
and F6 remain pending. No receipt or fixture proves those gates. The restricted
floor-consumption wording remains in the contract; no reconstruction join was
invented.

Next exact step: lead reviews this diff and report for fixture-only landing,
then handles desk-day production extraction-spec registration with the real full
census. Lead records the F6 readiness decision at the 6 September cut. No commit
was made in the shared repository.
