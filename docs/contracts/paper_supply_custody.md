# Paper supply custody

Status: normative for `PAPER-CUSTODY-SEAM-01`. **D-173** is the adopted, amended
project decision that every paper supplier must obtain claim-bearing evidence
through one shared custody-read seam; its full decision and veto status are in
the [decision log](../decision_log.md#d-173-paper-supply-custody--one-custody-read-seam-for-every-claim-bearing-paper-input-magistrate-provisional-2026-09-04).
This document is D-173's single normative home.

## Terms

A **paper supplier** is code that converts analysis evidence into a paper fill,
table cell, token, or professor-facing sentence. The **custody seam** is
`joulewise.paper_custody.open_paper_input(ref)`, the only public operation that
admits evidence to such code.

A **family** is one of the five closed kinds of paper evidence listed below. A
**role** is a lowercase supply-map key, such as
`fixture.reported_energy_parents`, that selects exactly one registered family
and its complete input set. A caller may supply that role string and a **runs
root**, meaning one existing directory under which run-generated evidence is
stored. The caller may supply nothing else that selects or authenticates input
bytes.

The **supply map** is the Git-tracked JSON file
`configs/paper_supply/supply_map.json`. It maps each role to its family,
relative input paths, expected SHA-256 digests, and validator identifier. Each
entry also names a **custody inventory**, a map-pinned object repeating the
complete input census, and a **receipt**, a map-pinned producer record that
corroborates the exact inputs and a fresh validator replay. The map is the
repository-owned source of every locator and expected digest; a caller cannot
replace or supplement it.

An **anchor** is the pair `(repository, head)` returned by the fixed-repository,
clean-tree function `joulewise.identity_pins._mint_git_anchor()`, plus the
supply-map blob read from that exact commit. The function calls the generalized
mint's Git-state implementation on its fixed `REPO_ROOT`, requires a 40-digit
`HEAD`, and runs `git status --porcelain --untracked-files=all`. Any tracked or
untracked change refuses the anchor, including an untracked file outside the
supply-map paths. This strict rule is intentional: the paper build is a
release operation, and an operator must stage, commit, ignore, or remove all
untracked scratch material before it can read. The returned `HEAD` must also be
provably contained in local `origin/main`; false or unknown containment
refuses. Synthetic tests may replace this private anchor call only while
exercising a map-pinned `test_fixture_non_issuing` inventory. The public
production path exposes no fixture switch and always executes the real gate.

The custody inventory and receipt are corroborating structures, not independent
authority: changing evidence and minting replacements cannot change the
Git-anchored supply map.

A **fresh replay** runs the current owning validator code in-process over the
bytes read in the current call. A **reopen** reads every selected input again
after replay.

A verified result is one of the five frozen, non-container types minted with a construction token created inside private seam closures. The token is also stored on every authentic capability and is readable by ordinary attribute access, because `_custody_token` is not among the guarded `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token recovery. Forging a result additionally requires importing the module-private `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside D-161's threat model. Physics/evidence and pre-registration failures and ordinary operator mistakes remain fail-closed. Direct public construction and tokenless `object.__new__` instances refuse on guarded access. These guards prevent ordinary caller and operator mistakes; they do not prevent deliberate token extraction or token-bearing reconstruction, which D-161 places outside the threat model. A dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or tokenless `object.__new__` object is never a valid ref or verified capability.

The token is recoverable from the closure cells of the private guard functions.
The five names above are the issuing types. Each has a non-issuing
`Fixture*` sibling built on the same private base; no fixture role is ever issuing,
and no renderer accepts one.
Evidence records the authorizing anchor commit and exact supply-map SHA-256,
input digests, selected subjects, and family-specific rendering grants.
**Issuance** means releasing a result that may authorize paper text.


## Closed public wire

`open_paper_input(ref)` accepts exactly one of these frozen reference types.
Every reference has exactly two fields, in this order: `role: str` and
`runs_root: pathlib.Path`.

| Reference | Verified result | Meaning |
|---|---|---|
| `ReportedEnergyParentsRef` | `VerifiedReportedEnergyParents` | **D-123**, the ratified decision to preregister and report phase-energy mean cells, together with its governed parents ([decision log](../decision_log.md#d-123-ruling-2-yes--the-signal-size-doctrine--the-overnight-license-ed-2026-08-08)) |
| `D165CloseoutRef` | `VerifiedD165Closeout` | **D-165**, the adopted falsifier requiring every attribution-dominance ratio to reach the fixed twofold threshold before licensing the headline ([decision log](../decision_log.md#d-165-the-falsifier-magistrate--cold-gate-2026-08-28)) |
| `WholeWindowVerdictRef` | `VerifiedWholeWindowVerdict` | One authenticated whole-window admission verdict row and its provenance |
| `ClaimEvidenceRef` | `VerifiedClaimEvidence` | `claim_verdicts.v1`, `claim_side_bound.v2`, and their authenticated parents |
| `TransferProjectionRef` | `VerifiedTransferProjection` | The diagnostic inserted-gap transfer projection used by **TR-01**, the branch-independent paper fill that states whether the measured transfer supports applying the pulse-derived timing bound ([registry row](../paper/results-fill-registry.md#tr-01)) |

The module exports no path/digest **binding** class usable for lookup and no receipt reference class; the exported
`VerifiedDigest` is a read-census record with no lookup or issuance authority.
It exposes no public reader, parser, replay dispatcher, payload constructor, or
verified-result constructor. Calling `CustodyEvidence` or any `Verified*` or
`Fixture*` class directly refuses with `paper_custody_request_invalid`.
Private construction requires the token described above. Each verified family
has a distinct `Fixture` sibling by prefix replacement, including
`FixtureWholeWindowVerdict`. The ten types share private frozen/slotted
`_CustodyResult`; no fixture inherits a verified class. Each opener overload
returns only its issuing/fixture pair.

`joulewise.paper_rendering` registers five renderers: `render_reported_energy`,
`render_d165`, `render_whole_window`, `render_claim`, and `render_transfer`.
Each accepts exactly its issuing family and runs `_issued_renderer` before
its body or payload access. The wrapper checks exact type, token, family,
production mode, selected subjects and the required grant for every subject.
Fixture results never enter any renderer, without a caller boolean check.
The registry and AST census reject unwrapped, widened, or unregistered public
renderers. Public suppliers accept refs and use the opener.


## Custody-bound registry rows

The [successor specification proposal](paper_comparison_placements.md) is separate
from this live census. It grants no comparison placements and does not satisfy
the pending paper-side acceptance below. Floor-cell, measured-dependence and
characterization routes remain unresolved; related authenticated parents do not
extend a family's rendering grants. Archive completeness and public availability
cannot be established by a partial family census.

A `results-fill-registry.md` row is **custody-bound** when its supplier column names a
`paper_custody` family and role as `<family>/<supply role>`. Every claim-bearing row must
be custody-bound before its value renders; a row naming no family and role is
`STOP_FILL`. The table below enumerates every custody-bound row and is the only such
enumeration. (Today it is empty: all five roles are fixtures.)

| Registry row | Family / supply role |
|---|---|

**Pending paper-side work (D-173 SCOPE):** registry rows naming `paper_custody`
families and roles have not been installed. Before any claim-bearing row renders,
acceptance requires adding `<family>/<supply role>` to every affected row's
supplier column, enumerating every custody-bound row in the table above, and
adding a test asserting that this contract table and the registry agree, shaped
like `test_refusal_constructor_ast_census`. The stable `#tr-01` row-ID anchor
must also be installed in the registry. This fixture-only landing does not
satisfy that pending paper-side acceptance.


## Supply-map schema and lookup

The supply map is strict JSON with this exact shape:

```text
{
  "schema_version": "joulewise.paper_supply_map.v2",
  "pending_roles": {"<pending role>": {"status": "pending_desk_day", "family": "<family>", "input_role": "<role>", "base": "repository", "authority": "git_blob", "path": "<prospective path>"}},
  "roles": {
    "<role>": {
      "family": "<closed family>",
      "mode": "production|test_fixture_non_issuing",
      "issuance_gate_id": "<registered family/version ID or null>",
      "subjects": ["<selected subject ID>"],
      "source_census": [{"authority": "git_blob|generated", "base": "repository|runs_root", "expected_sha256": "<digest>", "path": "<relative path>"}],
      "inputs": [
        {
          "authority": "git_blob|generated",
          "base": "repository|runs_root",
          "expected_sha256": "<64 lowercase hex>",
          "path": "<relative POSIX path>",
          "role": "<closed input role>"
        }
      ],
      "inventory": {
        "base": "repository|runs_root",
        "expected_sha256": "<64 lowercase hex>",
        "path": "<relative POSIX path>"
      },
      "receipt": {
        "base": "repository|runs_root",
        "expected_sha256": "<64 lowercase hex>",
        "path": "<relative POSIX path>"
      },
      "validator": "joulewise.paper_custody.<family>.v1"
    }
  }
}
```

Every object has exactly the keys shown. A role key matches
`[a-z0-9][a-z0-9_.-]*`. Each path is a nonempty relative POSIX path with no
empty, `.`, `..`, absolute, or backslash component. `git_blob` authority is
valid only with `base: repository`. Paths and closed input roles are unique
within the fixed family inputs. The additional `source_census` may repeat the
private `authenticated_source` role but must have unique base/path identities
across all inputs. The `inputs` array order must exactly equal the family order
below; sorting or accepting an extra input is nonconforming.

Lookup is exact and mechanical:

1. Validate the concrete ref type, role grammar, and `Path`-typed runs root;
   resolve the runs root strictly and require a directory.
2. Call the private `_mint_git_anchor(require_origin_main=True)` release form.
   Do not accept a repository, commit, map path, map bytes, containment
   override, fixture switch, or anchor from the caller.
3. Start a new `V2AuthenticationReadSession`. Run
   `git -C <repository> show <head>:configs/paper_supply/supply_map.json`, then
   pass those exact bytes to the active session as the identity
   `git:<head>:configs/paper_supply/supply_map.json` with strict JSON grammar.
4. Look up `roles[ref.role]`; absence is
   `paper_custody_role_unregistered`. Require the entry's `family` to equal the
   family fixed by the concrete ref class, its validator to equal
   `joulewise.paper_custody.<family>.v1`, and its ordered input roles to equal
   the mode-specific family census below.
5. Convert the entry to private bindings. `base: repository` resolves under the
   fixed anchor repository; `base: runs_root` resolves under the caller's runs
   root. No public binding, inventory, receipt, path, digest, validator, or
   source-digest parameter exists.

The fixed map currently registers five synthetic roles only. Their bytes carry
`synthetic-no-measurement-value`; map and inventory modes must agree on
`test_fixture_non_issuing`, gate ID must be null, and subjects must be empty.
Each returns its distinct `Fixture*` type. The reported-energy fixture exercises
a repository `git_blob` extraction spec, and every fixture has a transitive
source read in its census. These are synthetic authentication controls.

Both production roles `production.reported_energy_parents.qwen3-1p7b.v5` and
`production.reported_energy_parents.qwen3-8b.v5` are **pending**, recorded only
in `pending_roles`, which grants no lookup or issuance authority. The 8b role
is included by the S2 fix ruling because both models are cells of the D-179
registration. Their prospective `EXTRACTION_SPEC` blobs are respectively
`configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json` and
`configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json`. Desk-day
registration must use each real reviewed/committed blob and full production
census under D-138/D-166 successor naming; a fixture or old pack cannot replace
it. Production Git-blob coverage remains unfulfilled until that registration.


## Family censuses

**D-117** is the adopted prospective three-window replacement for the retired
historical remint plan; it defines the present floor/mint parent chain
([decision log](../decision_log.md#d-117-d-110s-historical-re-mint-order-superseded--prospective-three-window-replacement-option-2-adopted-d-113-readiness-rewired)).
**G2-a** is the first diagnostic machine evening that probes four registered
prefill lengths and produces the later selected-length record; it is defined by
the [live queue row](../../TASK_QUEUE.md#current-queue). These definitions bind
the reported-energy input names below.

| Family | Ordered input roles |
|---|---|
| Reported energy | `extraction_spec`, `extraction_report` (the D-117 mint-consumption report), `whole_window_basis`, `g2a_selection` (the G2-a selection record), `prompt_pin` |
| D-165 close-out | `d165_closeout`, `finalized_manifest`, `floor_artifact`, `replay_sidecar` |
| Whole window | `campaign_log`, `standalone_verdict`, `prospective_manifest`, `plan` |
| Claims | `claim_verdicts`, `claim_side_bound`, `finalized_manifest`, `floor_artifact` |
| Transfer | `transfer_result`, `reviewed_capture`, `plan`, `pre_data_receipt`, `pulse_bound_source`, `bundle_inventory` |

Production D-165 and claim inputs append `floor_acceptance` to their fixed
census. Every map entry also pins its complete transitive `source_census`;
unmapped owner reads refuse.

Every family additionally reads its `custody_inventory` and
`validator_receipt` locators from the same map entry.

## Read, replay, receipt, and reopen algorithm

After role resolution, the seam performs these steps in order inside the one
fresh `V2AuthenticationReadSession`:

1. Read the map-pinned inventory with `read_nofollow_pinned`. The session
   rejects symlinks, containment escapes, non-regular files, digest mismatch,
   malformed UTF-8/JSON, duplicate keys, and non-finite numbers before bytes
   enter seam logic.
2. Require inventory schema `joulewise.paper_custody_inventory.v1` and exact
   keys `family`, `files`, `inventory_id`, `mode`, `schema_version`. Each file
   row has exactly `authority`, `path`, `role`, `sha256` and must equal the
   corresponding map binding. The rows are exactly the family input roles plus
   `validator_receipt`; duplicates or omissions refuse.
3. Read all fixed and transitive inputs and the receipt with the map's base,
   path and expected digest. A `git_blob` input first runs anchored `git show`,
   checks the map digest **before parsing**, and enters the session under
   `git:<head>:<path>`. Its no-follow worktree bytes must match that same pin;
   reopening checks both blob and worktree. Generated inputs retain pinned
   no-follow reads. The inventory corroborates the entire ordered source set.
4. Authenticate and replay the family gate. `_FamilyReplay` preserves separate
   `authentic`, `admitted`, `grants` and `validator_codes` fields. Fixtures only
   replay synthetic documents and never dispatch an issuance gate. Production
   requires a closed `(family, issuance_gate_id)` registry hit; null or unknown
   IDs stop. Empty replay/receipts never authorize issuance.
5. Validate the canonical newline-terminated receipt: exact fields `family`,
   `inputs`, `replay_codes`, `schema_version`, `status`, `validator`, and
   `validator_source_sha256`; schema `joulewise.paper_custody_receipt.v1`,
   status `PASS`, and sorted `{path, role, sha256}` rows for all consumed
   sources. Its validator digest hashes family, policy constants, registered
   gate IDs, gate/dispatch/grant/mint code, mode census and owning validators.
   The executable census in `_validator_source_census` names each member;
   source is UTF-8 `inspect.getsource`, with NUL separators. Whole owner
   modules are also pinned so helper code and policy constants cannot drift
   behind an unchanged validator entry point. The receipt's
   replay codes must match fresh replay exactly; diagnostics are private.
6. Check that all actual owner reads belong to the mapped fixed/transitive
   census. The map is authority; an owner callback or receipt is never an
   extra source authorization channel.
7. Call the replay/reopen boundary and reread inventory, every fixed/transitive
   source and receipt through the same session/pins. Changed inputs refuse.
8. Build frozen evidence with anchor/map digest, selected subjects and grants,
   then mint only the mode-specific family type. Production needs authentic,
   admitted replay and the closed required grant for every selected subject.

Whole-window issuance, admitted or non-admitted, remains stopped until a registered per-family issuance gate lands that requires `WholeWindowRowValidation.authentic` to be true and binds model, window, basis, membership and governing row per ruling 43 Q-17-6; non-admission issuance carries only the fixed Q6 sentence.


## Family replay requirements

The separate D-179 projection contract is `docs/contracts/paper_reported_energy.md`.
Its executable registrations and non-issuing synthetic kernel are installed;
production joins remain pending. The future reported-energy gate must replay `validate_extraction_spec` and
`validate_d117_mint_consumption_report`. Its production entry must also
inventory the full ordered extraction-spec `reported_energy_cells[].members` universe and every
strict-bundle input consumed by the projection. The closed mint-consumption
report is unchanged; computed results belong to the separate typed frozen field
`reported_energy_projection` on both reported-energy result types, never to an
invented report field. The new owner module, phase-ratio validator, bundle
reader and typed whole-window owner are
in the transitive source census. Optional fixture `projection_input` is
synthetic-only and cannot issue a cell. D-179 fixes the fifty-member mean,
stratified t9 interval and observed ratio of totals, but authentic production
replay and registration-before-spec proof still gate issuance.

D-165 replays the finalized-manifest validator, floor authentication,
`validate_d165_replay_sidecar`, and `validate_d165_closeout`. The adapter and
the exhaustive professor-facing refusal vocabulary live in the real producer
module `joulewise/dominance_closeout.py`. Its
`D165_CLOSEOUT_REFUSAL_CODES` set and `D165_OR01_REASON_SENTENCES` map have
exactly equal keys, and the test mutation-probes additions on both sides.

D-165's `d165-closeout.v1` gate reuses its paper-source adapter, including
finalized-manifest/floor/sidecar/closeout validation and the v5 census. It
recomputes global fields from validated ratios. A and B license the outcome;
only A with recomputed licensing flags grants dominance sentence/subtitle.
Branch null does not license an empirical refusal. B is not Q6. The subject is
the exact supply role.

Claims register `claim-evidence.v1` with disk manifest validation,
`validate_claim_verdicts`, reevaluation via `evaluate_claim`, embedded-floor
byte equality, floor acceptance and `validate_claim_side_bound`. The adopted
[claim-side contract](paper_claim_side_bound.md) owns the copy-only v2 producer,
verdict-resolution ordered join, required anchor kind, typed complete widening
and exact numeral-byte equality for bounds, components and both intervals.
The gate regenerates that projection from authenticated verdict bytes and
reevaluates claims from verdict fields only. Outcome grants require each
selected contrast to be current, confirmatory and structurally valid; L2
additionally needs reevaluated readiness/ceiling. Mixed subjects never share
licensing. This registration adds no production supply-map role or renderer;
X6/X7 remain PROPOSED_STOP_FILL pending the later post-S2 rendering seat.

Reported-energy joins, whole-window F6 and transfer acceptance are incomplete,
so their gates remain unregistered.
The whole-window typed validator remains in the source census; no flattened
empty-code result can replace its authenticity/admission semantics. F6 and its
empirical non-admission renderer are not implemented in Round 5.

### Floor acceptance

Production D-165 and claims require a map-pinned artifact with exact keys
`schema_version`, `floor_sha256`, `sources`, `binder_source_sha256`,
`anchor_head`, `status`, schema `joulewise.paper_floor_acceptance.v1`, and
status `PASS`. Sources are sorted unique `{path, sha256}` rows matching the
mapped authenticated source census; path is prefixed `repository/` or
`runs_root/` to disambiguate roots. Floor bytes and current binder source hash
must match. The acceptance anchor must be an ancestor of the current clean
anchor: it precedes the commit that pins the acceptance digest, avoiding a
self-referential commit hash. Missing/stale acceptance stops issuance.

Before submission the lead runs `bind_v2_floor_artifact_evidence` once on each
actual submission floor and its authenticated sources, then pins the pass
beside the finalized manifest. Fixtures do not satisfy this gate. Floors are
"reconstructed from authenticated member sources once, at mint (and re-checked
once before submission); at analysis consumption validated against the widths
recorded in the floor artifact and byte-sealed by the finalized manifest, not
re-derived". Consumption retains the existing binder; full reconstructed
custody joins remain post-submission work. Acceptance is a pinned prerequisite,
not a new receipt family or an execution callback that unlocks a gate.


## Lower-boundary closures

`joulewise.campaign_provenance.load_campaign_log_rows` accepts only `log_path`
and reads its bytes through the authentication input API; it has no
`raw_bytes` substitution channel. The floor loader's normative wire is
`joulewise.analysis_engine.inputs.load_floor_artifact(path) -> AuthenticatedFloorArtifact`.
The returned object is the authenticated capability itself; no public
`(Mapping, digest)` projection is part of this wire.

The authentication AST guard includes `joulewise/paper_custody.py`, every
supplier owner module in the validator census, and both
`joulewise.analysis_engine.inputs` and `joulewise.analysis_manifest_v3`.
Evidence reads in those modules route through the active authentication
session. The manifest's three append-only publisher reads are explicitly
classified by the lint as writer-state/idempotence/directory-fsync operations,
not evidence admission. The guard does not treat subprocess stdout as a direct
filesystem read; the seam's `git show` bytes are therefore registered by an
explicit `session.ingest` call. The public-wire test parses all five ref class
bodies rather than trusting only the outer `open_paper_input(ref)` signature.
It requires exactly `role` and `runs_root` and rejects reintroduction of public
binding or receipt types.

## Closed refusals and exception translation

This is the exhaustive refusal-code registry. A declared code without the
listed reachable condition, or a raise-site code absent from this table, is a
contract failure.

| Code | Reachable condition |
|---|---|
| `paper_custody_request_invalid` | Invalid ref/value shape, private-capability construction/access, or translated unexpected ordinary exception |
| `paper_custody_anchor_unavailable` | Dirty/unreadable Git state, HEAD not provably contained in `origin/main`, or failed anchored `git show` |
| `paper_custody_anchor_mismatch` | A custody-inventory locator, authority, or digest disagrees with the Git-anchored supply-map binding |
| `paper_custody_supply_map_invalid` | Supply-map schema, family, validator, role ordering, path, digest, or binding grammar is invalid |
| `paper_custody_role_unregistered` | The requested role is absent from the anchored map |
| `paper_custody_path_refused` | Runs root or a resolved input path is unsafe, non-directory, symlinked, or non-regular |
| `paper_custody_input_unreadable` | A required root or input cannot be read |
| `paper_custody_digest_mismatch` | Input bytes disagree with the map-pinned SHA-256 before parsing |
| `paper_custody_parse_invalid` | Pinned bytes fail strict UTF-8, JSON/JSONL, duplicate-key, or finite-number admission |
| `paper_custody_issuance_gate_unregistered` | Null or unknown family/version production gate; pending roles never unlock it |
| `paper_custody_not_issuable` | Wrong issuing/fixture type, malformed replay, non-admission or missing required grant |
| `paper_custody_binding_mismatch` | Selected subject/grant or side-bound join mismatch; unmapped owner reads |
| `paper_custody_issuance_prerequisite_missing` | Missing/stale floor acceptance, floor/source/binder/anchor mismatch or absent required producer input |
| `paper_custody_receipt_invalid` | Inventory or validator-receipt schema/canonical form/status is invalid |
| `paper_custody_receipt_binding_mismatch` | Receipt input census, validator source digest, or replay-code binding disagrees |
| `paper_custody_validator_refused` | Fresh owning-validator replay returns one or more private diagnostic codes |
| `paper_custody_evidence_ambiguous` | Duplicate paths/roles or a non-exact inventory census prevents unique evidence selection |
| `paper_custody_input_changed` | Reopen detects replacement, removal, grammar/digest change, or different bytes after replay |

Every custody-seam and renderer-guard failure is `PaperCustodyRefusal` with a code
from the closed `paper_custody_*` set; a reported-energy renderer body may
additionally raise the closed `paper_reported_energy_*` vocabulary of D-179, also
with empty `rendered_output`. Custody-seam failures include malformed
primitive types before regex/path operations, Git/subprocess failures, supply
map failures, JSON/UTF-8 failures, missing files, nested or already-active
authentication sessions, validator exceptions, replay changes, and private
construction attempts. `KeyboardInterrupt`, `SystemExit`, and other
`BaseException` control flow are not converted.

The read census and nested validator codes are diagnostic metadata only. They
cannot be interpolated into paper prose. Registered renderers require their
exact issuing type, private token and per-subject grants before payload access.
The refusal AST census requires literal constructor arguments and exact equality
between executable call sites, the 18-code registry and this table. Dynamic
condition tests complement the census; dead strings are not execution evidence.


## Proposed comparison supplier bindings — 2026-09-08

This appendix is **outside the live custody-bound registry census**. It mirrors
the proposed placement/registry rows, including explicit non-empirical exclusions.
No family/role pair here grants a fill; every status remains PROPOSED_STOP_FILL.
UNREGISTERED is not a role key. UNRESOLVED grants remain absent, including floor
cells, measured dependence, characterization, archive completeness, public release
and machine applicability. Partial family censuses cannot authorize the latter
claims. Proposed extensions require lead ruling; none installs a sixth family.
Every empirical supplier must call `open_paper_input` after adoption. Synthetic
and schematic suppliers cannot discharge empirical obligations.

<!-- BEGIN COMPARISON BINDINGS -->
| Obligation | Placement | Site | Artifact field | Supplier | Evidence | Family | Role | Required grant | Applicability | Missing evidence | Adoption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| X1 | CP-X01-identity | V5-ID-001/002; V5-WL-001–004 | Reviewed model/runtime/workload identities; frozen panel and workload files | selection_identity_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | UNRESOLVED: candidate route; dedicated identity-text grant | Prospective identity disclosure; no measured result | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X1 | CP-X01-length | V5-WL-005; V5-G2A-001; [PREFILL_LENGTH] | G2-a selection.collection_prefill_tokens; prompt-pin v2 cross-check; prefill count receipt and resolvability summary | selection_identity_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | UNRESOLVED: candidate route; selection-text grant | Only authenticated selected L; never assume a ladder rung | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X2 | CP-X02-ratios | All eight R_*; four comparative R_cm_*; four absolute R_cm_* N/A dispositions | d165-closeout.json: complete independent/comparative diagnostic ratio records and recomputed global flags | d165_ratio_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome(subject=supply role); UNRESOLVED: numeric ratio projection grant | Twelve evaluable ratios; four absolute common-mode ratios explicitly N/A | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X2 | CP-X02-abstract | A all-pass sentence @ abstract | d165-closeout.json: branch=A and recomputed licensing flags | d165_prose_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome + dominance_sentence(subject=supply role) | All twelve ratios >=2 and publication acceptance PASS | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X2 | CP-X02-discussion | A all-pass sentence @ discussion | d165-closeout.json: branch=A and recomputed licensing flags | d165_prose_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome + dominance_sentence(subject=supply role) | All twelve ratios >=2 and publication acceptance PASS | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X2 | CP-X02-conclusion | A all-pass sentence @ conclusion | d165-closeout.json: branch=A and recomputed licensing flags | d165_prose_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome + dominance_sentence(subject=supply role) | All twelve ratios >=2 and publication acceptance PASS | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X2 | CP-X02-headline | contingent dominance subtitle | d165-closeout.json: A and subtitle licensing flag | d165_prose_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome + subtitle(subject=supply role) | A only; never infer from a model verdict | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X3 | CP-X03-section4 | &#91;FILL:OB-01&#93; @ section4 | d165-closeout.json: branch=B; every failed independent/comparative diagnostic record | d165_failed_components_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome(subject=supply role); UNRESOLVED: full failed-list renderer | Complete evaluable ratio census; B never means a failed model contrast | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X3 | CP-X03-abstract | &#91;FILL:OB-01&#93; @ abstract | d165-closeout.json: branch=B; every failed independent/comparative diagnostic record | d165_failed_components_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome(subject=supply role); UNRESOLVED: full failed-list renderer | Complete evaluable ratio census; B never means a failed model contrast | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X3 | CP-X03-discussion | &#91;FILL:OB-01&#93; @ discussion | d165-closeout.json: branch=B; every failed independent/comparative diagnostic record | d165_failed_components_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome(subject=supply role); UNRESOLVED: full failed-list renderer | Complete evaluable ratio census; B never means a failed model contrast | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X3 | CP-X03-conclusion | &#91;FILL:OB-01&#93; @ conclusion | d165-closeout.json: branch=B; every failed independent/comparative diagnostic record | d165_failed_components_projection | EMPIRICAL | d165_closeout | UNREGISTERED | outcome(subject=supply role); UNRESOLVED: full failed-list renderer | Complete evaluable ratio census; B never means a failed model contrast | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-1p7b-prefill | DS-11; d117-qwen3-1p7b-prefill-pL-floor-v5; associated F_* and TERM tokens; TERMINAL_REFUSAL_REASON_*; NO_EXACT_FLOOR_REASON_*; AVAILABLE_DIAGNOSTIC_CLAUSE_*; POINT_DIAGNOSTIC_CLAUSE_* | detection-floor-extraction.json and minted v2 floor: cell components, operative floor and label; exact projection field contract UNRESOLVED | floor_cell_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ALPHA small / BETA large; selected L for prefill; floor acceptance required | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-8b-prefill | DS-15; d117-qwen3-8b-prefill-pL-floor-v5; associated F_* and TERM tokens; TERMINAL_REFUSAL_REASON_*; NO_EXACT_FLOOR_REASON_*; AVAILABLE_DIAGNOSTIC_CLAUSE_*; POINT_DIAGNOSTIC_CLAUSE_* | detection-floor-extraction.json and minted v2 floor: cell components, operative floor and label; exact projection field contract UNRESOLVED | floor_cell_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ALPHA small / BETA large; selected L for prefill; floor acceptance required | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-1p7b-decode | DS-19; d117-qwen3-1p7b-decode-floor-v5; associated F_* and TERM tokens; TERMINAL_REFUSAL_REASON_*; NO_EXACT_FLOOR_REASON_*; AVAILABLE_DIAGNOSTIC_CLAUSE_*; POINT_DIAGNOSTIC_CLAUSE_* | detection-floor-extraction.json and minted v2 floor: cell components, operative floor and label; exact projection field contract UNRESOLVED | floor_cell_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ALPHA small / BETA large; selected L for prefill; floor acceptance required | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-8b-decode | DS-23; d117-qwen3-8b-decode-floor-v5; associated F_* and TERM tokens; TERMINAL_REFUSAL_REASON_*; NO_EXACT_FLOOR_REASON_*; AVAILABLE_DIAGNOSTIC_CLAUSE_*; POINT_DIAGNOSTIC_CLAUSE_* | detection-floor-extraction.json and minted v2 floor: cell components, operative floor and label; exact projection field contract UNRESOLVED | floor_cell_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ALPHA small / BETA large; selected L for prefill; floor acceptance required | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-composition | DS-01; empirical component composition and cell labels | Minted floor component census; exact standalone projection fields UNRESOLVED | floor_cell_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Comparison successor only | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X4 | CP-X04-na | Prefill J/output-token and decode J/input-token companion sites | No artifact field: phase-inapplicable companion cells | fixed_applicability_text | LIMITATION | NONE | NONE | NONE | N/A by column/phase; not a missing measurement | Retain explicit N/A; never opportunistically fill | PROPOSED_STOP_FILL |
<<<<<<< HEAD
<<<<<<< HEAD
| X5 | CP-X05-1p7b-prefill | DS-09/10/12; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/prefill: five fields defined in paper_reported_energy.md; production member replay pending | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | RETIRED_FALLBACK under D-174; no placement restored | RETIRED_FALLBACK |
| X5 | CP-X05-8b-prefill | DS-13/14/16; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/prefill: five fields defined in paper_reported_energy.md; production member replay pending | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | RETIRED_FALLBACK under D-174; no placement restored | RETIRED_FALLBACK |
| X5 | CP-X05-1p7b-decode | DS-17/18/20; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/decode: five fields defined in paper_reported_energy.md; production member replay pending | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | RETIRED_FALLBACK under D-174; no placement restored | RETIRED_FALLBACK |
| X5 | CP-X05-8b-decode | DS-21/22/24; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/decode: five fields defined in paper_reported_energy.md; production member replay pending | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | RETIRED_FALLBACK under D-174; no placement restored | RETIRED_FALLBACK |
| X6 | CP-X06-table | DS-25–32; point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; finalized manifest; claim_side_bound.v1 and source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X7 | CP-X07-table | DS-33; PG-01/02/04–08 (no PG-03); point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; finalized manifest; claim_side_bound.v1 and source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
=======
| X5 | CP-X05-1p7b-prefill | DS-09/10/12; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/prefill: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X5 | CP-X05-8b-prefill | DS-13/14/16; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/prefill: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X5 | CP-X05-1p7b-decode | DS-17/18/20; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/decode: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X5 | CP-X05-8b-decode | DS-21/22/24; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/decode: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X6 | CP-X06-table | DS-25–32; point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; finalized manifest; claim_side_bound.v2 and verdict-resolution source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X7 | CP-X07-table | DS-33; PG-01/02/04–08 (no PG-03); point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; finalized manifest; claim_side_bound.v2 and verdict-resolution source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
>>>>>>> feat/2026-09-08-paper-S3
=======
| X5 | CP-X05-1p7b-prefill | DS-09/10/12; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/prefill: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred; D-177 adjacent phase-energy limitation required | PROPOSED_STOP_FILL |
| X5 | CP-X05-8b-prefill | DS-13/14/16; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/prefill: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred; D-177 adjacent phase-energy limitation required | PROPOSED_STOP_FILL |
| X5 | CP-X05-1p7b-decode | DS-17/18/20; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 1p7b/decode: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred; D-177 adjacent phase-energy limitation required | PROPOSED_STOP_FILL |
| X5 | CP-X05-8b-decode | DS-21/22/24; gross mean + two endpoints + per-token value + count | extraction_spec.json; mint-consumption extraction_report; proposed reported_energy_cells for 8b/decode: five values, exact field names/member joins UNRESOLVED | reported_energy_projection | EMPIRICAL | reported_energy_parents | UNREGISTERED | cell(subject=exact registered model/phase cell) | ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred; D-177 adjacent phase-energy limitation required | PROPOSED_STOP_FILL |
| X6 | CP-X06-table | DS-25–32; point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; finalized manifest; claim_side_bound.v1 and source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X7 | CP-X07-table | DS-33; PG-01/02/04–08 (no PG-03); point, endpoints, floor, signed clearance/shortfall, claim-side bound, floor gate, direction/Holm and verdict | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; finalized manifest; claim_side_bound.v1 and source-cell join; numeric projection fields UNRESOLVED | claim_table_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast); l2 where required; UNRESOLVED: numeric/table projection scope | GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
>>>>>>> feat/2026-09-08-paper-S7-reconciliation
| X7 | CP-X07-split | D-166 split-refusal sentence; guarded prefill token family UNRESOLVED | G2-a selection/prompt-pin and issued affected prefill evidence; split-refusal field/route UNRESOLVED | prefill_split_refusal_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Two distinct exhausted-ladder renderings require adoption; diagnostic failure is not production non-admission | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-a-abstract | &#91;FILL:DS-32&#93; @ A/abstract | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-a-discussion | &#91;FILL:DS-32&#93; @ A/discussion | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-a-conclusion | &#91;FILL:DS-32&#93; @ A/conclusion | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-b-abstract | &#91;FILL:DS-32&#93; @ B/abstract | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-b-discussion | &#91;FILL:DS-32&#93; @ B/discussion | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-decode-b-conclusion | &#91;FILL:DS-32&#93; @ B/conclusion | claim_verdicts.json contrasts[decode].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-a-abstract | &#91;FILL:PG-08&#93; @ A/abstract | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-a-discussion | &#91;FILL:PG-08&#93; @ A/discussion | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-a-conclusion | &#91;FILL:PG-08&#93; @ A/conclusion | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-b-abstract | &#91;FILL:PG-08&#93; @ B/abstract | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-b-discussion | &#91;FILL:PG-08&#93; @ B/discussion | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X8 | CP-X08-prefill-b-conclusion | &#91;FILL:PG-08&#93; @ B/conclusion | claim_verdicts.json contrasts[prefill].claim_evaluation.outcome; identical rendering to Table 3 | claim_verdict_projection | EMPIRICAL | claim_evidence | UNREGISTERED | outcome(subject=exact contrast) | Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X9 | CP-X09-section4 | &#91;FILL:OR-01&#93; @ before-comparison/section4 | campaign_log.jsonl exact governing row; whole-window-verdict.json; prospective manifest, plan, bracket/basis/member/model bindings | whole_window_stop_projection | EMPIRICAL | whole_window_verdict | UNREGISTERED | UNRESOLVED: F6 non-admission grant; positive does not license refusal | Actual affected ALPHA/BETA/GAMMA window | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X9 | CP-X09-abstract | &#91;FILL:OR-01&#93; @ before-comparison/abstract | campaign_log.jsonl exact governing row; whole-window-verdict.json; prospective manifest, plan, bracket/basis/member/model bindings | whole_window_stop_projection | EMPIRICAL | whole_window_verdict | UNREGISTERED | UNRESOLVED: F6 non-admission grant; positive does not license refusal | Actual affected ALPHA/BETA/GAMMA window | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X9 | CP-X09-discussion | &#91;FILL:OR-01&#93; @ before-comparison/discussion | campaign_log.jsonl exact governing row; whole-window-verdict.json; prospective manifest, plan, bracket/basis/member/model bindings | whole_window_stop_projection | EMPIRICAL | whole_window_verdict | UNREGISTERED | UNRESOLVED: F6 non-admission grant; positive does not license refusal | Actual affected ALPHA/BETA/GAMMA window | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X9 | CP-X09-conclusion | &#91;FILL:OR-01&#93; @ before-comparison/conclusion | campaign_log.jsonl exact governing row; whole-window-verdict.json; prospective manifest, plan, bracket/basis/member/model bindings | whole_window_stop_projection | EMPIRICAL | whole_window_verdict | UNREGISTERED | UNRESOLVED: F6 non-admission grant; positive does not license refusal | Actual affected ALPHA/BETA/GAMMA window | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X10 | CP-X10-section4 | &#91;FILL:OR-01&#93; @ at-closeout/section4 | d165-closeout.json: authenticated governing refusal including zero denominator | closeout_refusal_projection | EMPIRICAL | d165_closeout | UNREGISTERED | UNRESOLVED: branch null has no empirical refusal grant | Only if no governing before-comparison stop; retain separately valid model verdicts | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X10 | CP-X10-abstract | &#91;FILL:OR-01&#93; @ at-closeout/abstract | d165-closeout.json: authenticated governing refusal including zero denominator | closeout_refusal_projection | EMPIRICAL | d165_closeout | UNREGISTERED | UNRESOLVED: branch null has no empirical refusal grant | Only if no governing before-comparison stop; retain separately valid model verdicts | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X10 | CP-X10-discussion | &#91;FILL:OR-01&#93; @ at-closeout/discussion | d165-closeout.json: authenticated governing refusal including zero denominator | closeout_refusal_projection | EMPIRICAL | d165_closeout | UNREGISTERED | UNRESOLVED: branch null has no empirical refusal grant | Only if no governing before-comparison stop; retain separately valid model verdicts | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X10 | CP-X10-conclusion | &#91;FILL:OR-01&#93; @ at-closeout/conclusion | d165-closeout.json: authenticated governing refusal including zero denominator | closeout_refusal_projection | EMPIRICAL | d165_closeout | UNREGISTERED | UNRESOLVED: branch null has no empirical refusal grant | Only if no governing before-comparison stop; retain separately valid model verdicts | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X11 | CP-X11-archive | CP-X11-archive: preservation, admission/accounting and archive assertion | Complete census: raw telemetry/runtime/environment/instrument_calibration; campaign log; replacements/quarantine; plans/receipts/policy; calibration/drift/brackets; extraction specs/reports; final manifest/verdicts | archive_census_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | G2-a through final close; include failures, not merely admitted members | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X12 | CP-X12-p1 | docs/paper/figures/fig3_decision_gates.svg; four outcome descriptions | Diagram geometry/method labels: refused; not resolvable; direction unresolved; directional claim | schematic_p1 | SCHEMATIC | NONE | NONE | NONE | No measured annotations or numeric thresholds | Retain schematic label; empirical annotations need separate X6–X10 bindings | PROPOSED_STOP_FILL |
| X13 | CP-X13-response | DS-02; linearity tokens/outcome phrase | Workload-response fields in characterization_result_report.json under frozen characterization_result_schema_v1.json; producer absent | characterization_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ruled omission (D-177); separate Window C; forty admitted bundles / five lengths remain design requirements | STOP_FILL; preserve withdrawal/no-characterization prefix; D is not a fourth global outcome | PROPOSED_STOP_FILL |
| X14 | CP-X14-containment | DS-03; null tokens; D prefix | Per-block intervals, mean interval and maximum endpoint magnitude from separate characterization report | characterization_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ruled omission (D-177); Five disjoint A/B/B/A blocks per magnitude and earlier disjoint comparator; ALPHA/BETA nulls cannot double as test | STOP_FILL; preserve withdrawal/no-characterization prefix; D is not a fourth global outcome | PROPOSED_STOP_FILL |
| X15 | CP-X15-phase | DS-05; phase-accounting tokens | Separate characterization report phase-accounting results; producer absent | characterization_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ruled omission (D-177); 24 admitted bundles / two brackets | STOP_FILL; preserve withdrawal/no-characterization prefix; D is not a fourth global outcome | PROPOSED_STOP_FILL |
| X15 | CP-X15-drift | DS-06; drift/recovery tokens | Separate characterization report drift/recovery results; producer absent | characterization_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ruled omission (D-177); Six designated references, three held-out probes, three sustained-work/cooldown pairs | STOP_FILL; preserve withdrawal/no-characterization prefix; D is not a fourth global outcome | PROPOSED_STOP_FILL |
| X16 | CP-X16-challenge | DS-04 deliberate small-difference challenge | No issued challenge result | characterization_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | ruled omission (D-177); DO_NOT_START; explicit inclusion and design gates required | Remain excluded; no silent restoration | PROPOSED_STOP_FILL |
| X16 | CP-X16-between-session | DS-07 retired between-session stability | No authorized successor field | fixed_limitation_text | LIMITATION | NONE | NONE | NONE | ruled omission (D-177); DO_NOT_START; retired result remains retired | Retain exclusion; historical Window C is no supplier | PROPOSED_STOP_FILL |
| X17 | CP-X17-decode | CP-X17-decode: measured independent / estimated-AR(1) / fixed ESS-halving comparison | dependence_sensitivity.py JSON calculations for same ten ordered GAMMA blocks and authenticated metrology inputs; issuing projection fields UNRESOLVED | measured_dependence_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Ten complete blocks per contrast; preserve collection order/membership; SYN-04 cannot supply | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X17 | CP-X17-prefill | CP-X17-prefill: measured independent / estimated-AR(1) / fixed ESS-halving comparison | dependence_sensitivity.py JSON calculations for same ten ordered GAMMA blocks and authenticated metrology inputs; issuing projection fields UNRESOLVED | measured_dependence_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Ten complete blocks per contrast; preserve collection order/membership; SYN-04 cannot supply | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X18 | CP-X18-acceptance | CP-X18-acceptance: reconstructed-versus-published floor assertion | joulewise.paper_floor_acceptance.v1: status=PASS, floor_sha256, sources, binder_source_sha256, anchor_head; source-member/width and bracket/basis/estimator census | floor_publication_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Every submission floor actually rechecked; binder existence and DC/CE parent acceptance do not grant publication prose | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X19 | CP-X19-null | CP-X19-null: unnumbered null diagram and pass sentence | Stipulated comparator [-3,+3] J, five intervals, mean [-1.2,+1.2] J, M=2 J; connectors schematic | synthetic_null | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X19 | CP-X19-slope | SYN-06 endpoint-weight illustration | x=[1,2,3], L=[0,2,16], U=[2,16,24]; endpoint-weight interval 7–12 J/token | synthetic_slope | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X19 | CP-X19-floor | SYN-02 floor composition and pass/refusal illustration | worked-examples.json synthetic.composition_absolute and synthetic.composition_comparative | synthetic_floor | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X19 | CP-X19-holm | SYN-04 Student-t/Holm pass/refusal sentences | Separate ten-delta dataset; stipulated second p=0.041; Holm thresholds 0.025/0.05 | synthetic_statistics | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X19 | CP-X19-geometry | SYN-04 separate 10-J geometry and sign/Holm qualifications | Stipulated 10 J, bounds and intervals; distinct ten-point dataset for Holm | synthetic_geometry | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X19 | CP-X19-dependence | SYN-04 illustrative dependence scenarios | dependence_sensitivity.py on stipulated deltas; independent/AR(1)/ESS-halving outputs | synthetic_dependence | SYNTHETIC | NONE | NONE | NONE | Illustrative datasets kept separate; never campaign evidence | Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal | PROPOSED_STOP_FILL |
| X20 | CP-X20-limitation | TR-01 fixed limitation; withdrawn result slot | Fixed statement that transfer is untested | fixed_limitation_text | LIMITATION | NONE | NONE | NONE | DO_NOT_START; historical pulse bound is not transfer validation | Retain limitation | PROPOSED_STOP_FILL |
| X20 | CP-X20-result | CP-X20-result: conditional transfer result (not TR-01 reactivation) | Future transfer result + reviewed capture, prospective plan, pre-data receipt, pulse-bound source and bundle inventory | transfer_projection | EMPIRICAL | transfer_projection | UNREGISTERED | diagnostic(subject=registered transfer); acceptance/gate absent | DO_NOT_START; separate prospectively fixed design and explicit inclusion | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
| X21 | CP-X21-external | CP-X21-external: external-meter/replication result exclusion | No issued meter or replication artifact or registered result field | external_replication_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | DO_NOT_START; separate authorization, equipment, load/synchronization/range; not a comparison dependency | Retain limitation; no result inferred from design | PROPOSED_STOP_FILL |
| X22 | CP-X22-availability | DS-34; [REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST] | Actual release checklist: issued repository revision, public archive locator and fingerprint-manifest locator; fields unissued | release_availability_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Public release, not local custody paths | STOP_FILL; retain honest unissued-locators statement | PROPOSED_STOP_FILL |
| X22 | CP-X22-machine | CP-X22-machine: fresh-machine applicability statement | Actual machine instrument/runtime/model/privilege/admission evidence; route/field contract UNRESOLVED | machine_applicability_projection | EMPIRICAL | UNRESOLVED | UNRESOLVED | UNRESOLVED | Every new machine must demonstrate admission; no inherited measured limits | STOP_FILL; methods/diagnostics fallback; no issued refusal inferred | PROPOSED_STOP_FILL |
<!-- END COMPARISON BINDINGS -->
