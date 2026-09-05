# Custody-read seam for paper suppliers — Opus seat (contract lens)

2026-09-04, `/Users/edr/code/JouleWise-wt-custody-consult`. Read: paper-I 01–10;
d123-supplier 02/04/05/06/07; d165-renderer 02/04/05/06–10; both lane modules via
`git show`; `authentication_io`, `whole_window`, `identity_pins`,
`dominance_closeout`, `floor_extraction`, `analysis_engine/{artifact,inputs}`,
`arm_readiness`, `tests/test_authentication_io.py`.

## 0. Three findings that reframe the question

**(a) The seam largely exists, twice, and no ruling names it.**
`authentication_io.py:319` `V2AuthenticationReadSession`: registration-at-read
(`read` :401, `read_nofollow` :426 with `O_NOFOLLOW`+containment via `:278`,
`ingest` :454 for `git:` identities), first-digest enforcing (`_register` :365 →
`v2_authentication_input_changed`), strict-parsing at read, enforced by AST lint
`direct_read_violations` (`:623`) over `AUTHENTICATION_SURFACE`
(`tests/test_authentication_io.py:26-40`) via
`test_marked_v2_surface_has_no_direct_readable_io` (`:361`). Neither supplier
imports it or is in that list. `arm_readiness._read_identity_projection_receipt`
(`:5568`) is the richest existing custody read: containment, symlink/regular
refusal, digest + GNU `.sha256` sidecar, canonical parse, owning validator.

**(b) The lanes are on opposite sides, contrary to the brief's premise.** d165 is
already path-and-digest bound and is the better reference: `_read_bound_regular`
(`results_fill_outcome.py:281` — absolute path, rejects `bytes`, per-component
`S_ISLNK` walk, `resolve(strict=True)` containment, `O_NOFOLLOW|O_CLOEXEC`,
`S_ISREG` on the fd, digest compare), `_authenticated_closeout_path` :337,
`_validated_before_comparison_path` :612, and — worth promoting verbatim —
**every path re-opened and re-verified after validator replay** (`:414-418`,
`:772-779`); dict/bytes channels gone, kept gone by signature-census tests
(`:707-714`, `:976-978`, `:982-983`). d123 is the total defect:
`_wrapped_document` (`reported_phase_energy.py:308`) takes
`{path, file_sha256, document}`, checks `path` only lexically (`:317-319`) —
**never opens it** — and compares `file_sha256` to
`canonical_json_sha256(document)` (`:323-326`): the caller's object against the
caller's digest. All five entry points take `bytes`/`dict`;
`build_reported_phase_energy_source` seals its own output under a fabricated path
(`:702-706`).

**(c) The residual bug both share is *who names the expected digest*.** A
caller-supplied expected digest is caller-authored; so is a receipt whose digest
the caller supplies — delta-10 V3: resealed sources plus a test-minted
`status: PASS` receipt (`tests/test_results_fill_outcome.py:270-319`) rendered
`41x-fabricated` through a validator-clean `OutcomeFillResult`. Adjacent holes:
`inputs.py:953` `load_floor_artifact` degrades `AuthenticatedFloorArtifact`
(`:352`) to `(dict, str)`; `_load_authenticated_floor_artifact` (`:943`)
authenticates with **neither** binding; `authenticate_floor_artifact_bytes`'s
`expected_sha256` is optional (`:868`); and
`campaign_provenance.load_campaign_log_rows(..., raw_bytes=)` (`:453`) lets a
caller substitute the whole campaign log — the before-comparison lane's own
evidence.

## 1. Module and public API

New `joulewise/paper_custody.py`; ONE home `docs/contracts/paper_supply_custody.md`.
`Custodied` generalizes `AuthenticatedFloorArtifact`; `CustodyRefusal` follows the
`.reason_code`-against-a-frozenset shape of `ArmReadinessError` (`:1047`) and
`IdentityPinProjectionError` (`identity_pins.py:168`, codes `:39`).

```python
@dataclass(frozen=True)
class SupplyAnchor: commit: str; map_sha256: str    # trust root, not caller data
def load_supply_anchor(repo_root: Path) -> SupplyAnchor
    # tracked docs/contracts/paper_supply_map.json via
    # ingest_git_authentication_input -> git:HEAD:<path>; clean-tree gate
    # reuses identity_pins._mint_git_anchor (:819)

@dataclass(frozen=True)
class Custodied(Generic[T]):
    role: str; value: T                 # validated typed object
    source_path: str; sha256: str       # the bytes actually read, this run
    parents: Mapping[str, str]          # role -> sha256, transitively verified
    validator: str                      # dotted name replayed in-process
    validator_result: tuple[str, ...]   # () == clean
    anchor: SupplyAnchor
    def digests(self) -> Mapping[str, str]

class CustodyRefusal(Exception):        # out-of-band, R4-S3
    reason_code: str; detail: str
    scope: Literal["artifact", "cell", "token"]     # Q-R1-3 levels
    verified: Mapping[str, str]
    def refusal(self) -> dict[str, Any]

@contextmanager
def custody_read_session(*, anchor: SupplyAnchor, runs_root: Path)
        -> Iterator[CustodyReader]      # opens V2AuthenticationReadSession

class CustodyReader:
    def artifact(self, role) -> Custodied[Mapping[str, Any]]
    def rows(self, role, *, key: Mapping[str, str]) -> Custodied[tuple[...]]
    def member(self, role, bundle_id: str) -> Custodied[Mapping[str, Any]]
    def derive(self, role, *, parents: Sequence[Custodied]) -> Custodied[...]
    records: Mapping[str, AuthenticationInputRecord]    # property; the census
```

Invariants, each mechanically checkable:

1. **Caller passes a role name and a runs root — never a path, bytes, dict, or
   expected digest.** Anchored roles take path + digest from the git-anchored map;
   run-generated evidence takes its digest by *traversal* from the manifest bound
   to that campaign — the `whole_window_refusal_reasons` pattern
   (`whole_window.py:5525`: runs root and identity set, never bytes).
2. Reads use `session.read_nofollow` with `_read_bound_regular`'s checks. No
   session ⇒ `custody_session_not_active`: `authentication_io`'s module helpers
   (`:511-605`) silently degrade to `pathlib` when none is active — a live trap.
3. **The owning validator is replayed in-process over the bytes just read, and
   every path is re-opened after replay.** A receipt is never authority; if
   present it is re-read and compared only.
4. Re-read every time; first-digest recording turns any mid-run change into
   `v2_authentication_input_changed`.
5. `derive()` takes only `Custodied` parents from *this* reader (identity, not
   equality) → `custody_parent_not_custodied`.

Codes: `custody_{session_not_active, anchor_unclean, role_unregistered,
path_escapes_root, path_not_regular_file, digest_mismatch, strict_parse_failed,
row_not_unique, parent_not_custodied, input_changed, identity_not_v5,
derivation_mismatch}`, `custody_validator_refused` (+ the validator's own code),
and `custody_validator_indistinct` (validator cannot separate authentic-failure
from provenance-failure ⇒ STOP_FILL — the ruled whole-window state).

## 2. Each input class through the seam

| Input | Call → wraps |
|---|---|
| D-123 parents | `reader.artifact("extraction_spec"/"d117_mint_consumption_report"/"whole_window_evaluation_basis"/"g2a_selection"/"prompt_pin")` → `validate_extraction_spec` (`floor_extraction.py:1007`), `validate_d117_mint_consumption_report` (`:1599`) |
| D-123 members | `reader.member("bundle", id)` → keeps the one custody-correct island `reported_phase_energy.py:523-565` (`load_reported_phase_energy_member` + digest compare → `reported_energy_member_parent_digest_mismatch` :565); **adds** `cli.validate_bundle(..., strict=True)` per R2-B1 |
| D-123 projection | `reader.derive("reported_phase_energy_projection", parents=…)` → producer inside the reader; `custody_derivation_mismatch` carries `reported_energy_projection_derivation_mismatch` |
| D-165 close-out | `reader.artifact("d165_closeout"/"finalized_manifest"/"floor_artifact"/"replay_sidecar")`, then replay `validate_d165_closeout` (`dominance_closeout.py:1713`; bytes-in is correct — the missing layer is who supplies the bytes) |
| Whole-window rows | `reader.rows("idle_admission_whole_window_verdict", key={model, phase})` — log under runs_root, strict JSONL, exact-once, replay `whole_window.py:5525` + `AuthenticatedConsumptionSession` (`:438`). `custody_validator_indistinct` today ⇒ STOP_FILL per addendum 07; `WHOLE-WINDOW-STOP-RECEIPT-01` lifts it |
| `claim_verdicts.v1` + sidecar | `reader.artifact("claim_verdicts")` → `validate_claim_verdicts` (`artifact.py:945`); sidecar joined on `claim_verdicts_sha256 == custodied.sha256` — the digest the **reader** computed, not a field of either document |
| Floor lineage (R2-FL-1) | `reader.artifact("floor_artifact")` → `authenticate_floor_artifact_bytes(raw, expected_sha256=<anchored>, expected_artifact_id=…)` (`inputs.py:868`); cf. `:842` |
| `_v5` identity | `reader.artifact("model_panel")` + `stack_identity_sha256` (`identity_pins.py:205`) vs the anchored pin **including `tokenizer_json_sha256`** (`configs/model_panels/qwen3_4bit.json:17,50`); `:500`, `:577` |
| Transfer projection | `reader.artifact("transfer_fiducial_result")`, fixture-only until the d67ee56c capture passes its own gate (R3 fence intact) |

## 3. The one test pattern

`test_<supplier>_refuses_every_mutation_of_every_custodied_input`, **parameterized
over `reader.records`** — the census the session recorded, not a hand list, so a
new input cannot escape coverage. Per record, in a temp copy of the tree:

- **Arm A, raw flip** → `reason_code == "custody_digest_mismatch"`.
- **Arm B, full reseal** (every self-hash, content address, canonical ID *and
  receipt* recomputed) → the **named** code owning that record's relation
  (`custody_derivation_mismatch`, `custody_validator_refused` + the validator's
  code, `custody_row_not_unique`, `custody_identity_not_v5`).

Asserting the **exact** code kills the masking class: an outer whole-object gate
firing first becomes a failure, not a pass. Not theoretical —
`tests/test_reported_phase_energy.py:520`, `:531`, `:951` *assert that a fully
resealed forged artifact passes* `validate_reported_phase_energy`, and the
500-case sweep at `:993-1023` asserts only the coarse `STOP_FILL` that
`reported_phase_energy_token_values:1672-1677` collapses every failure into. The
in-tree antidote is the derivation-first ordering at
`reported_phase_energy.py:1565-1567` — named refusal raised *before* the
whole-object gate at `:1573`; the seam generalizes exactly that ordering.

Two cheap lints: add both suppliers to `AUTHENTICATION_SURFACE` so the existing
AST lint proves no direct read bypasses the seam; and an `inspect.signature` lint
that no public supplier parameter is annotated `bytes`, `dict`, or `Mapping` —
the API must be *unable* to express the defect.

## 4. Kept vs deleted

**D-123** — DELETE `_wrapped_document` (`:308`) and the whole
`{path, file_sha256, document}` grammar; `reported_energy_projection` as source
material; the `bytes`/`dict` signatures of all five entry points; the fabricated
projection path (`:702-706`). KEEP the round-2 derivation
(`_derive_reported_energy_projection` :473, `build_reported_phase_energy_projection`
:614, `validate_reported_energy_projection_derivation` :629) and its named
mismatch; the member island `:523-565`; ratio-of-sums with mixed denominators;
duplicate-role census; nullable refusal custody;
`issuance_composition_rule_not_current`; DS-09..24. FIX `:1672-1677` to surface
named codes; upgrade `tests/…:740`, `:749`, `:993-1023` from bare
`assertRaises`/`STOP_FILL` to exact codes.

**D-165** — KEEP and promote into `paper_custody`: `_read_bound_regular` :281,
the containment/nofollow discipline, re-open-after-replay :414-418/:772-779,
`CLOSEOUT_REASON_SENTENCES`, the `OutcomeFillResult`/`OutcomeFillRefusal` split,
the registry byte-exact oracles, the before-comparison exact-once +
prospective-manifest chain. DELETE only the *authority claims*: caller-named
expected digests (→ anchor), the receipt as capability (→ corroboration;
delta-10 S-2), the close-out-before-before-comparison order (`:954-973`, F2-R),
the incomplete `_V5_CLOSEOUT_PINS`. Upgrade `tests/…:738-742` and `:770-777` to
assert `reason_code`.

## 5. Decision-log entry: YES

New cross-cutting contract + tracked anchor + enforcement lint — the class
D-165/D-168 got entries for. Propose **D-173, "paper supply custody-read seam"**,
ONE home `docs/contracts/paper_supply_custody.md`, plus a `custody_role` column on
DS-09..24, DS-28..33, PG-01..08, OB-01, OR-01, TR-01.

## 6. Where I disagree with the earlier rulings

1. **R4-S2 (addendum 09) and addendum 07's "paths + expected digests + validator
   receipts" is the proximate cause of the third D-165 failure.** It never says
   *who* names the expected digest, and it lets a receipt confer authority
   (delta-10 V3). Amend: digests come from a git-anchored map or by traversal from
   it, a receipt corroborates, the validator is replayed in-process. Addendum 07
   got the replay half right, then let the caller name paths and digests.
2. **R2-FL-1 (addendum 10) is self-referential as written.** It authorizes the
   floor from `claim_verdicts.inputs.floor_artifact.embedded_bytes_base64` with
   `expected_sha256=file_sha256` — both from `floor_link`, inside the object a
   re-content-addressing attacker controls (`artifact.py:1044` is the repo's only
   site passing both bindings). Amend: the on-disk floor artifact under the anchor
   (or `inputs.py:842`) is the authority, the embedded copy corroborates. Close
   `load_floor_artifact` (`:953`) and `load_campaign_log_rows(..., raw_bytes=)`
   (`campaign_provenance.py:453`) in the same round — the hole one layer down.
3. **R4-B1's "closed" reason map is not closed.** `dominance_closeout` can emit
   `closeout_input_malformed: closeout.comparative_common_mode_ratios`
   (`:1833`→`:1952`), which has no named constant and is absent from
   `CLOSEOUT_REASON_SENTENCES` (`results_fill_outcome.py:103-152`) — the ruled
   enumeration test cannot be passing as specified. Same class:
   `reported_phase_energy.py:559` re-raises `FloorExtractionError` text verbatim
   into the refusal vocabulary.
4. **Addendum 09 R4-S1 repeats the abstraction error it was curing.** "Use the
   existing identity-pin validator" is the altitude of the F4-R4-F1-ABSTRACT it
   followed; delta-10 S-1/V6 shows the seat called `stack_identity_sha256` and
   discarded the return, with no `tokenizer_json_sha256` pin. Rulings must name
   the exact pin field set.
5. **Procedural.** Build the seam once and rebase both lanes — d123 should adopt
   d165's already-correct path machinery rather than re-derive it. Curing custody
   per-lane at each lane's altitude bought six rounds of one signature.

Fixture-only; no measurement value issued; no commit.
