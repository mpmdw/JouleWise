# Paper supply custody

Status: normative for `PAPER-CUSTODY-SEAM-01`. **D-173** is the provisional
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
untracked change refuses the anchor. Whether `origin/main` contains `HEAD` is
recorded by the mint implementation but is not an anchor gate.

The custody inventory and receipt are corroborating structures, not independent
authority: changing evidence and minting replacements cannot change the
Git-anchored supply map.

A **fresh replay** runs the current owning validator code in-process over the
bytes read in the current call. A **reopen** reads every selected input again
after replay. A **verified result** is one of the five frozen, non-container
types that only the seam can construct. **Issuance** means releasing a result
that may authorize paper text; every fixture role is explicitly non-issuing.

## Closed public wire

`open_paper_input(ref)` accepts exactly one of these frozen reference types.
Every reference has exactly two fields, in this order: `role: str` and
`runs_root: pathlib.Path`.

| Reference | Verified result | Meaning |
|---|---|---|
| `ReportedEnergyParentsRef` | `VerifiedReportedEnergyParents` | **D-123**, the ratified decision to preregister and report phase-energy mean cells, together with its governed parents ([decision log](../decision_log.md#d-123-ruling-2-yes--the-signal-size-doctrine--the-overnight-license-ed-2026-08-08)) |
| `D165CloseoutRef` | `VerifiedD165Closeout` | **D-165**, the adopted falsifier requiring every attribution-dominance ratio to reach the fixed twofold threshold before licensing the headline ([decision log](../decision_log.md#d-165-the-falsifier-magistrate--cold-gate-2026-08-28)) |
| `WholeWindowVerdictRef` | `VerifiedWholeWindowVerdict` | One authenticated whole-window admission verdict row and its provenance |
| `ClaimEvidenceRef` | `VerifiedClaimEvidence` | `claim_verdicts.v1`, `claim_side_bound.v1`, and their authenticated parents |
| `TransferProjectionRef` | `VerifiedTransferProjection` | The diagnostic inserted-gap transfer projection used by **TR-01**, the branch-independent paper fill that states whether the measured transfer supports applying the pulse-derived timing bound ([registry row](../paper/results-fill-registry.md#L920)) |

The module exports no path/digest binding class and no receipt reference class.
It exposes no public reader, parser, replay dispatcher, payload constructor, or
verified-result constructor. Calling any `Verified*` class directly refuses
with `paper_custody_request_invalid`; only the private seam factory can create a
populated instance. A dictionary, mapping, bytes object, arbitrary sequence,
prevalidated object, or object made with `object.__new__` is never a valid ref.

## Supply-map schema and lookup

The supply map is strict JSON with this exact shape:

```text
{
  "schema_version": "joulewise.paper_supply_map.v1",
  "roles": {
    "<role>": {
      "family": "<closed family>",
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
within an entry. The `inputs` array order must exactly equal the family order
below; sorting or accepting an extra input is nonconforming.

Lookup is exact and mechanical:

1. Validate the concrete ref type, role grammar, and `Path`-typed runs root;
   resolve the runs root strictly and require a directory.
2. Call `_mint_git_anchor()` with no arguments. Do not accept a repository,
   commit, map path, map bytes, or anchor from the caller.
3. Start a new `V2AuthenticationReadSession`. Run
   `git -C <repository> show <head>:configs/paper_supply/supply_map.json`, then
   pass those exact bytes to the active session as the identity
   `git:<head>:configs/paper_supply/supply_map.json` with strict JSON grammar.
4. Look up `roles[ref.role]`; absence is
   `paper_custody_role_unregistered`. Require the entry's `family` to equal the
   family fixed by the concrete ref class, its validator to equal
   `joulewise.paper_custody.<family>.v1`, and its ordered input roles to equal
   the family census below.
5. Convert the entry to private bindings. `base: repository` resolves under the
   fixed anchor repository; `base: runs_root` resolves under the caller's runs
   root. No public binding, inventory, receipt, path, digest, validator, or
   source-digest parameter exists.

The fixed map currently registers five synthetic roles only. Their bytes carry
the marker `synthetic-no-measurement-value`, inventories use
`mode: test_fixture_non_issuing`, and returned evidence sets
`issuance_authorized` to false. Producer missions add production roles
prospectively; fixture consistency never creates production authority.

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
3. Read every input and the receipt once through `read_nofollow_pinned` using
   the map's base, path, and expected digest. Require each read digest to equal
   the matching inventory row.
4. Parse the receipt as canonical JSON terminated by one newline. It has exactly
   `family`, `inputs`, `replay_codes`, `schema_version`, `status`, `validator`,
   and `validator_source_sha256`. Require schema
   `joulewise.paper_custody_receipt.v1`, `status: PASS`, the map validator, and
   an input row `{path, role, sha256}` for every family input sorted by role.
5. Compute `validator_source_sha256` over the dispatcher and every owning
   validator. Initialize SHA-256 with `family + NUL`; for each member in the
   family's closed census, append `member_id + NUL`, then UTF-8
   `inspect.getsource(member) + NUL`. The common census is `_replay_family`,
   `_validate_fixture_documents`, and `_validate_production_documents`.
   Reported energy adds both floor-extraction validators; D-165 adds its paper
   adapter, manifest, floor, replay-sidecar, and close-out validators; whole
   window adds its typed row validator; claims add `validate_claim_verdicts`;
   transfer currently adds no unavailable producer. The receipt digest must
   equal this result.
6. Replay the owning validators over the bytes read in step 3. Receipt
   `replay_codes` must equal the replay result exactly. Nested validator details
   stay non-renderable.
7. Call the replay/reopen boundary, then read inventory, every family input, and
   receipt again through the same session and pins. Removal, replacement,
   digest change, grammar change, or inode/path substitution refuses as
   `paper_custody_input_changed`.
8. Build a frozen read census and privately construct the matching verified
   result. Production mode still refuses until that family's governed producer
   is registered. Whole-window positive issuance additionally remains blocked
   on `WHOLE-WINDOW-STOP-RECEIPT-01`.

## Family replay requirements

Reported energy replays `validate_extraction_spec` and
`validate_d117_mint_consumption_report`. A future production entry must also
inventory the full ordered `reported_energy_cells[].members` universe and every
strict-bundle input consumed by the projection.

D-165 replays the finalized-manifest validator, floor authentication,
`validate_d165_replay_sidecar`, and `validate_d165_closeout`. The adapter and
the exhaustive professor-facing refusal vocabulary live in the real producer
module `joulewise/dominance_closeout.py`. Its
`D165_CLOSEOUT_REFUSAL_CODES` set and `D165_OR01_REASON_SENTENCES` map have
exactly equal keys, and the test mutation-probes additions on both sides.

Whole-window replay uses `WholeWindowRowValidation`, whose `authentic` field
distinguishes provenance validity from admission outcome. That typed result is
not itself issuance; the governed receipt producer remains mandatory.

Claims replay `validate_claim_verdicts` against the finalized manifest. The
floor file's expected digest comes from the supply map, never from
`claim_verdicts.inputs.floor_artifact.file_sha256`; any embedded copy is only a
corroborating byte-for-byte comparison with the map-pinned floor.

Transfer must eventually recompute the projection from authenticated reviewed
capture and replay the adopted v1 validator. Until both capture and result
receipt producers pass their gates, production returns
`paper_custody_receipt_unissued`; no fixture may issue TR-01 prose.

## Lower-boundary closures

`joulewise.campaign_provenance.load_campaign_log_rows` accepts only `log_path`
and reads its bytes through the authentication input API; it has no
`raw_bytes` substitution channel. The floor loader's normative wire is
`joulewise.inputs.load_floor_artifact(path) -> AuthenticatedFloorArtifact`.
The returned object is the authenticated capability itself; no public
`(Mapping, digest)` projection is part of this wire.

The authentication AST guard includes `joulewise/paper_custody.py`, and its
public-wire test parses all five ref class bodies rather than trusting only the
outer `open_paper_input(ref)` signature. It requires exactly `role` and
`runs_root` and rejects reintroduction of public binding or receipt types.

## Closed refusals and exception translation

Every public-entry failure is `PaperCustodyRefusal` with a code from the closed
`paper_custody_*` set and empty `rendered_output`. This includes malformed
primitive types before regex/path operations, Git/subprocess failures, supply
map failures, JSON/UTF-8 failures, missing files, nested or already-active
authentication sessions, validator exceptions, replay changes, and private
construction attempts. `KeyboardInterrupt`, `SystemExit`, and other
`BaseException` control flow are not converted.

The read census and nested validator codes are diagnostic metadata only. They
cannot be interpolated into paper prose. A supplier may render only a verified
result with `issuance_authorized == true`; all other outcomes stop filling.
