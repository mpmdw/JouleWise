# Registration-at-read escalation consult — response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge. Charge:
ESCALATION.md beside this file (regression-fidelity + strict-parse-
scoping classes at count 2 on the trust branch).

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL.** The
strict-read SESSION becomes the single byte-read of the active v2
authentication path — every reached document (JSON strict-parsed with
duplicate-key/non-finite refusal; non-JSON registered raw) enters the
registry AT THE READ CALL, so the strict set is definitionally the
authentication-reached set. The parallel traversal is DELETED as
unrepairable (the consult's own words: repair merely starts delta
count three). An AST-level direct-I/O build guard prevents unrouted
reads from compiling into the reachable path. The decisive memo-§8
regression is REPLACED WHOLESALE: real issued-ledger/committed-pin
fixture (tests/fixtures/d117_v2_production/), the unpatched production
CLI, every quoted attack leg with per-leg refusal-stage assertions,
genuine-source SHAs verified unchanged, no-output proof — the
_fresh_original_core substitution is not adapted, it is retired. The
future-delta checklist (16 questions) binds the next delta. v1 golden
byte-parity is a hard constraint throughout. Note: the consult ran
against the branch worktree and could not see the escalation record on
main (baseline preceded it); its independent coverage of both classes
was verified by the magistrate against the delta-4 findings — all five
covered.

---

# Positions

## 1. Registration-at-read

**Ruling:** replace `_strict_v2_recursive_json_inputs` with one v2-scoped read service. Every application-level byte read used to authenticate, hash, validate, rederive, or bind a v2 input must pass through that service. Discovery must come from the authentication call graph, never from a second filesystem traversal.

### Mechanism

Introduce a context-scoped `V2AuthenticationReadSession` with one underlying operation:

`read_authentication_input(path, *, grammar, label)`

The operation must, atomically before returning bytes:

1. Read the file.
2. Compute SHA-256 and stable path identity.
3. For `json`, reject duplicate keys and non-finite numbers.
4. For `jsonl`, apply the same parser to every nonempty row.
5. Register `{normalized_path, sha256, grammar, read_count}`.
6. On every subsequent read of that path, compare the new SHA to the first SHA and refuse immediately if they differ.

The registry has one record type:

- `json` / `jsonl`: registered and strict-parsed.
- `raw`: registered-unparsed, including plan sidecars, CSV, plist, source-code pins, and other binary artifacts.

A caller may not downgrade a `.json` or `.jsonl` path to `raw`; suffix or known wire type forces strict parsing even when the immediate purpose is only hashing. Thus:

- `authentication-reached JSON documents == strict-parsed documents` by construction.
- All other authentication-reached files remain visible in the same registry as `raw`.
- Missing optional files are attempted paths, not byte reads, and therefore have no path+SHA record.

Large raw files may use a streaming implementation, but it must end in the same registration primitive.

### TOCTOU ruling

Register every read, including re-reads. The map retains the first SHA plus `read_count`; each later read must match the first SHA before its bytes are returned. This replaces the bespoke comparisons at:

- acceptance re-read: `scripts/mint_floor_artifact_generalized.py:3432-3448`;
- ledger/head re-read: `:3462-3480`;
- report/spec/order/campaign preflight-versus-core comparison: `:3602-3647` and `:3700-3710`;
- recursive before/after traversal: `:3650-3654` and `:3752-3761`;
- repeated campaign-log, attempt-ledger, bundle, and post-bind reads deeper in the stack.

The reader must perform a real re-read rather than return cached bytes. Same SHA succeeds; changed bytes refuse with one stable `v2_authentication_input_changed` reason.

### Non-filesystem byte sources

`git show HEAD:<head-pin>` at `joulewise/calibration_ledger.py:777-792` is the one special case: Git’s packfile internals are not authentication documents, but the consumed blob on stdout is. Feed those stdout bytes through the same service under a virtual identity such as `git:HEAD:<relative-path>`, strict-parsed as JSON, and compare them with the registered physical head-pin bytes.

Interpreter module loading and directory/stat probes are not evidence-document reads. The deliberate estimator-code hashing at `joulewise/calibration_bracketing.py:166-173` is authentication input and must be registered as raw.

### V1 ruling

The active read session exists only around the v2 route, beginning before the first authoritative v2 pinset/input-manifest read and ending after post-bind validation. Shared helpers may call the wrapper, but with no active v2 session it must preserve their present parsing, exceptions, and output behavior exactly. Existing v1 golden artifacts and statements must remain byte-identical.

The actual `_fresh_original_core()` remains production code; it runs unpatched. Registration is inherited through the active context when that core calls shared readers.

### Replace the parallel traversal

Delete `_strict_v2_recursive_json_inputs` (`scripts/mint_floor_artifact_generalized.py:3132-3381`). Do not retain it as an equality oracle: it is a second path-discovery algorithm and therefore recreates the approximation defect.

The replacement final invariant is local to the reader:

- every registered JSON/JSONL record has `strict_parse_succeeded`;
- every repeated path has one SHA;
- every application read observed by the build guard has a registry record.

The build guard should have two layers:

1. An AST check rejects direct `read_bytes`, `read_text`, readable `open`, and `os.open` in the marked v2 authentication function surface, except inside the central reader.
2. The no-mock production regression uses a test-only low-level open auditor under the fixture/evidence roots and asserts that every actually opened input path appears in the registry. The auditor observes reads; it does not discover or select authentication inputs.

Consequently, constructing “authentication read this document but it is absent from the map” requires bypassing the central service, which breaks the build.

### Actual ad16fb2 read sites that must convert

- **Generalized entry:** `load_pinset` at `1279-1314`; `_load_v2_input_manifest` at `3053-3086`; `_authenticate_v2_inputs` at `3384-3768`, including acceptance, ledger/head, plans, sidecars, bindings, reports, specs, order manifests, campaign log, and bundle pre-reads.
- **Mint core:** `_load_json_object`, `_load_json_lines`, `_sha256_file` at `scripts/mint_floor_artifact.py:189-219,272-276`; `_strict_bundle` at `428-512`; `_authenticated_consumption_summaries` at `515-581`; `_authenticate_component` at `1027-1260`; `bind_floor_artifact_evidence` at `1689-1865`.
- **Acceptance/bracketing:** acceptance loader and default reread at `joulewise/calibration_bracketing.py:446-455,548-556`; estimator code pins at `166-173`; `load_calibration_candidate` at `812-930`.
- **Ledger:** committed pin bytes at `joulewise/calibration_ledger.py:777-792`; append journal at `842-856`; physical head/ledger at `1249-1314`; custody artifacts at `1227-1246`.
- **Ledger custody specifically missed today:** `_custody_reasons` reads every receipt-named `instrument_validation` artifact—`manifest.json`, `instrument_evidence.json`, `events.jsonl`, `power_trace.csv`, and `raw/powermetrics.plist`. `load_calibration_candidate` then re-reads the manifest and members. None is derived from the current report/verdict traversal.
- **Verdict and campaign provenance:** `AuthenticatedConsumptionSession._prepare` at `joulewise/whole_window.py:465-728`; `whole_window_refusal_reasons` at `4589-4776`; `whole_window_drift_allowances` at `4779-4825`; campaign log/manifest readers at `joulewise/campaign_provenance.py:452-465,595-678`.
- **Supersession/salvage:** occurrence descriptors and quarantine bytes at `joulewise/whole_window.py:2079-2271`; salvage descriptors/closure at `joulewise/salvage_dangler.py:207-224,1310-1364`.
- **Attempt custody:** `_evidence_map`, `validated_attempt_selection`, and `_manifest_members` at `joulewise/whole_window.py:2337-2558`; `validate_attempt_ledger` at `joulewise/analysis_engine/registry.py:720-875`.
- **Attempt metadata specifically missed today:** `validate_attempt_ledger` reads `metadata.json` for every ledger-referenced finalized attempt at `registry.py:837-864`, including ineligible/quarantined attempts. The traversal at `mint_floor_artifact_generalized.py:3336-3342` follows only `selected_bundles`.
- **Bundle/verdict rederivation:** `_read_json_object`, custody identity, registered policy, scientific identity, idle records, and evaluation-basis reads at `joulewise/whole_window.py:791-870,2612-2617,2927-2994,3243-3264,3836-3912`.
- **Bundle reader/strict validator:** `joulewise/bundle_read.py:246-410,720-828`, plus AXI/suite validation readers; `joulewise/cli.py:371-450` and its strict evidence helpers.
- **Primary calibration and reducer evidence:** `joulewise/reduce.py:1171-1500,2695-2726`; environment telemetry/policy reads at `joulewise/environment_admission.py:68-330`.
- **Complete bundle hashing and validator pinset rereads:** `joulewise/detection_floor.py:294-345,2009-2054`.

Conditional AXI, suite, salvage, supersession, and environment branches must convert too; “not exercised by this fixture” is not an exemption.

## 2. Decisive regression substitution contract

**Ruling:** adopt candidate **(a)** for production behavior: no mocks or substitutions in extraction, authentication, binding, validation, or Git checks. Temporary filesystem/Git construction is fixture scaffolding, not a substitute, provided it invokes real Git and real production functions.

Candidate (b) is acceptable only in that narrow sense. It must not mean patching `_actual_v2_git_state`, containment results, committed-pin checks, or repository state. Candidate (c) is rejected.

The current adapter at `tests/test_mint_floor_artifact_generalized.py:2251-2336` is disqualifying because it:

- replaces strict bundle validation with a no-op;
- replaces production consumption authentication with a manually `_prepared` session and injected summaries;
- mocks registered policy and NEG-8 decisions;
- substitutes `_synthetic_allowances`;
- replaces stack and scientific-config derivation;
- loads the ledger with `require_committed_pin=False` and `verify_custody=False`, while also dropping the issued acceptance cutoff;
- replaces `bind_floor_artifact_evidence` with a no-op.

The fixture also mocks extractor cooldown, whole-window refusal, allowance derivation, and strict validation at `:1874-1902`. The decisive test patches Git state and `_fresh_original_core` at `:3407-3427`. Those replacements remove exactly the independent authorities the regression claims to exercise.

No narrowed core substitution is admissible in the memo-§8 regression. Such adapters may remain in explicitly synthetic unit tests, but they cannot supply the “class dead” evidence.

### Minimal missing fixture machinery

Add a builder that:

1. Creates a temporary clean Git worktree or clone containing the real source.
2. Places mutable evidence outside that repository so attack mutations do not trip the clean-tree gate first.
3. Uses the exact code-pinned issued D-079 acceptance artifact.
4. Supplies the exact authenticated ledger prefix through the issued cutoff, its required custody artifacts, and new finalized pre/post sessions.
5. Places the terminal head pin inside the temporary repository, commits it with real `git add`/`git commit`, and verifies `git show HEAD:<pin>` equality.
6. Builds real strict-valid bundles, campaign policy/manifests, attempt evidence where applicable, verdict/evaluation basis, extraction spec, and order manifest.
7. Runs the production extractor without patches.
8. Runs the production v2 CLI without patches and proves one authentic mint succeeds.

If the issued ledger prefix and custody archive are not currently available as a fixture, that checked-in fixture is the prerequisite. Do not replace it with `verify_custody=False`, a genesis ledger, or a test-specific unissued acceptance authority.

### Exact coordinated-attack inventory and assertions

Memo §8 requires these exact legs:

> “change pinset postcollection values;”

With repaired self-hashes and genuine sources unchanged, a shadow-free variant must reach step 10 and refuse the first changed field with `postcollection_evidence_mismatch: <field> mismatch against domain-owned verification projection`.

> “repair all pinset self-hashes;”

This is a positive attack precondition: assert `_validate_v2_pin_hashes` succeeds and the eventual refusal is not a pinset self-hash error.

> “change the report SHA pin;”

Assert the modified pin exactly equals the attacked report’s actual SHA, proving raw report identity has been repinned. In a shadow-free variant, refusal must instead come from the report’s domain-owned content check at step 9 or the independent projection at step 10.

> “insert or modify `floor_mint_postcollection`;”

In the full coordinated attack, this is the first independent mismatch: step 8 must refuse the unknown top-level key through the closed D-117 report profile, before report-cache recomputation or U10 pin comparison. Neither output file may exist.

> “change observed drift, applied allowance, and floor strings;”

Exercise this both in the full attack and in masking-removal variants:

- attacked report allowance versus unchanged verdict/ledger/acceptance: refuse during authenticated allowance rederivation;
- attacked report floor values versus unchanged bundles: refuse at step 9 with `report cell floor differs from authenticated ... member evidence`;
- attacked postcollection `observed_drift_s` / `applied_allowance_s` versus unchanged sources: refuse at step 10, with `observed_drift_s` first under the fixed comparison order;
- attacked floor precision/rendering pins: refuse at the first corresponding step-10 floor field.

> “leave the ledger, acceptance artifact, verdict basis, and primary bundle evidence unchanged.”

Record their exact pre-attack SHA inventories and assert equality after attack construction and after refusal. This is part of the test contract, not explanatory prose.

For the combined attack, the asserted order is: clean Git and strict grammar pass; acceptance, ledger, binding, and verdict authentication pass; step 8 rejects `floor_mint_postcollection`; construction and both output writes remain unreached. Removing only the shadow key must expose the step-9 source mismatch, and removing report mutations as well must expose the step-10 pin mismatch. This prevents one early refusal from masking dead legs.

Separately mutate acceptance, physical ledger, committed head pin, binding, verdict basis, campaign manifest, attempt ledger/receipt/strict evidence/all-attempt metadata, primary bundle files, and report cache. Each must produce its owning domain’s refusal and no output.

## 3. File-by-file rework

- `joulewise/authentication_io.py` — new v2 read session, strict parser, raw registration, repeated-read SHA enforcement, and Git-blob ingestion.
- `scripts/mint_floor_artifact_generalized.py` — activate the session; route pinset/manifest/direct reads; remove `_strict_v2_recursive_json_inputs`; remove v2 callback substitution seams; finalize the registry after post-bind validation.
- `scripts/mint_floor_artifact.py` — route core object/JSONL/hash reads and post-bind reads through the shared service when v2 context is active.
- `joulewise/calibration_ledger.py` — route ledger, head, append journal, committed Git blob, and every custody artifact.
- `joulewise/calibration_bracketing.py` — route acceptance/default rereads, estimator-code pins, and calibration candidate artifacts.
- `joulewise/whole_window.py` — route campaign/verdict, supersession, attempt, policy, evaluation-basis, and bundle rederivation reads.
- `joulewise/campaign_provenance.py` — route manifest and campaign-log reads.
- `joulewise/analysis_engine/registry.py` — route analysis manifest, receipt/evidence, and every finalized-attempt metadata read.
- `joulewise/bundle_read.py`, `joulewise/cli.py`, `joulewise/reduce.py`, `joulewise/environment_admission.py` — route strict bundle, telemetry, calibration, and reduction reads.
- `joulewise/detection_floor.py` — route complete-bundle streaming hashes and pinset validator rereads.
- `joulewise/salvage_dangler.py` — route conditional salvage closure, membership, and artifact reads.
- `tests/fixtures/d117_v2_production/` — exact issued acceptance/ledger-prefix/custody and strict-valid seed evidence.
- `tests/test_mint_floor_artifact_generalized.py` — replace the decisive test with the unpatched production CLI regression and exact attack matrix.
- A focused authentication-I/O test module — atomic registration, duplicate/non-finite refusal, TOCTOU mutation, raw registration, AST direct-I/O guard, and low-level-open/registry equality.
- `docs/phase_2/floor_mint_contract.md` — state registration-at-read, raw versus strict records, no parallel traversal, and the no-substitution regression contract.

### Future-delta checklist

- Does the v2 session begin before the first authoritative v2 input read and remain active through post-bind validation?
- Can any application-level input read occur without one registry record from the same call?
- Does every reached JSON/JSONL path show successful duplicate-key and non-finite rejection?
- Are repeated reads of one path SHA-identical, with mutation refusing before use?
- Are ledger custody files under every `instrument_validation` locator registered?
- Are attempt ledger, analysis manifest, all receipts/strict evidence, and metadata for every ledger-referenced finalized attempt registered, including unselected attempts?
- Are non-JSON evidence and estimator-code pins registered as raw rather than omitted?
- Is unreferenced runs-root junk absent from the registry, while referenced junk refuses?
- Has the parallel traversal been deleted rather than relocated?
- Does the direct-I/O build guard cover every newly reachable helper?
- Does v1 still reproduce its exact golden bytes?
- Does the decisive regression run the real extractor, Git checks, strict validator, ledger custody, consumption authentication, allowance derivation, binding, and output path without patches?
- Does it execute every quoted attack leg, verify unchanged genuine-source SHAs, assert the first refusal stage, and prove no output?
- Do shadow-free variants expose step 9 and step 10 rather than relying on the unknown-key refusal?
- Does each genuine-source mutation produce its own domain-specific refusal?
- Has any locally authored summary, certificate, fixture adapter, or test-only loader become a replacement authority?

# Disagreements

The current recursive traversal is not repairable into a durable trust boundary; adding more followed path classes merely starts delta count three. It must be deleted.

The current coordinated-attack test is not production-path evidence despite invoking `extract_cells` and `_authenticate_v2_inputs`: its substituted ledger, consumption, allowance, strict-validation, binding, identity, and Git paths remove the independent checks that matter.

# Open questions

The binding trigger record `docs/process_traces/2026-08-08-trust-scoping-escalation/ESCALATION.md` is absent at `ad16fb2`. I therefore could not verify or quote its four P1 and one P2 texts directly; the design above independently covers the two defect classes and the specifically named ledger-custody and attempt-metadata omissions.

# Recommendation

Implement registration-at-read first, including the build guard and deletion of the traversal. Then build the real issued-ledger/committed-pin fixture and replace the decisive regression wholesale; do not adapt the current `_fresh_original_core` substitution. Run the focused suite, v1 byte-parity check, full suite, and a fresh delta only after both shapes land together.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Designed a registration-at-read architecture and no-substitution memo-§8 regression contract, including the full read-site inventory, exact attack legs, file plan, and relocation-resistant delta checklist.","pathspec":[],"verification":["git rev-parse HEAD: ad16fb299b617dfcf2eaed5ff5539942a39dc5e6","git status --short --branch: clean","Read bridge protocol, binding memo §§6/8, v2 authentication stack, decisive regression, ledger/verdict/bundle/attempt readers"],"flags":["no_edits","authority_pointer_missing"]}
