# Round-5 refuter — CONTRACT lens (Opus)

Branch `feat/2026-09-04-paper-custody-seam`, HEAD **01d00591** ("custody seam round 5"),
base `origin/main`. Independent of the astra refuter (file 13 not read). "contract" =
`docs/contracts/paper_supply_custody.md`; bare `:N` = `joulewise/paper_custody.py`.

**Executed** (repo venv, `PYTHONDONTWRITEBYTECODE=1`, one at a time): `test_paper_custody.py`
**28 passed / 266 subtests**; `test_paper_rendering.py` **3 passed**;
`test_authentication_io.py` **22 passed / 6 subtests**.

**Verdict: NOT REFUTED with AMENDs.** No blocker. Gaps: D-173's SCOPE clause is
declarative-only and undisclosed, plus three wording mismatches. Fixture-only, non-issuing
landing stands.

## 1. Contract ↔ code exactness — NOT REFUTED (2 AMENDs)

**Narrowing text (23 Q-PS-2 as corrected by 22): verbatim.** `contract:55` is
byte-identical to spec 11 F2's block; `:59` carries the added closure-cell sentence.
`test_paper_custody.py:961-972` extracts both ratified lines from spec 11, `assertIn`s them
against the contract, asserts `"held only inside"` is absent, and proves the disclosure true
at runtime (`opened._custody_token` by plain attribute access, same value in the guard's
closure).

**Per-family issuance-gate sentence: verbatim at `contract:253`**, word-for-word with the
D-173 addendum (`decision_log.md:11085-11091`).

**Refusal-code table: exact.** `:42-61` declares 18 codes;
`blocked_pending_receipt`/`receipt_unissued` gone; the four new codes are in registry and
table (`contract:344-361`). Repo-wide grep for the deleted pair: **zero hits outside
`docs/process_traces/`**. `test_paper_custody.py:975-979` binds contract ↔ registry ↔ AST
call sites by set equality; `:981-1000` kills dead literal, undeclared call, variable arg,
declared-only.

**Supply-map v2: `roles` matches; `pending_roles` unvalidated. AMEND (should-fix).**
`:988-1046` enforces the exact per-role key set `{family, inputs, inventory, receipt,
validator, mode, issuance_gate_id, subjects, source_census}`, the `mode` enum, the fixture
invariant (fixture ⇒ gate id null **and** subjects empty), mode-specific ordered input roles
and base/path uniqueness; the live map conforms. But
`:975-978` checks only the top-level key set and never inspects `pending_roles`, so
`contract:104` (its exact shape) and `contract:137` ("Every object has exactly the keys
shown") are false for it — `"pending_roles": 7`, or junk keys, still resolves every fixture
role. No authority leaks (lookup reads `roles` only), so not a blocker. Fix, after `:978`:
require `pending_roles` to be a dict with `_SUPPLY_ROLE_RE` keys whose values are dicts
keyed exactly `{"status", "family", "input_role", "base", "authority", "path"}` with
`status == "pending_desk_day"`, else `paper_custody_supply_map_invalid`.

**Closed public wire: AMEND (nit, two mismatches).**

1. `contract:55` says **five** types; `contract:83` says "The **ten** types share private
   frozen/slotted `_CustodyResult`". `:55` is ratified verbatim — reconcile in prose: after
   `:59` insert `The five names above are the issuing types. Each has a non-issuing
   \`Fixture*\` sibling built on the same private base; no fixture role is ever issuing,
   and no renderer accepts one.` That also restores "every fixture role is explicitly
   non-issuing", which the diff deleted from Definitions.
2. `contract:78` — "exports no path/digest binding class" — is literally false: `__all__`
   exports `VerifiedDigest` (`:125-131`), a diagnostic read-census record, not a lookup
   binding (`_BoundFile` is private), conferring nothing (`CustodyEvidence` construction is
   token-guarded) — but say so. Replace with: `The module exports no path/digest
   **binding** class usable for lookup and no receipt reference class; the exported
   \`VerifiedDigest\` is a read-census record with no lookup or issuance authority.`

## 2. D-173's four appended clauses

**SCOPE — not satisfied, not disclosed.** See §3.

**NON-ISSUING RESULTS — SATISFIED.** `:1438` mints `spec.issuing_type` only when
`mode == "production"`, else `spec.fixture_type`; `:198-202` refuses the wrong pairing;
`paper_rendering.py:19-20` refuses on wrong type *before* the body. Tests
`test_paper_custody.py:733`, `:745`.

**COVERAGE — PENDING, correctly disclosed.** No production role exists; it sits only in
`pending_roles` (`status: pending_desk_day`) of `configs/paper_supply/supply_map.json`;
`contract:174-180` states "Production Git-blob coverage remains unfulfilled until that
registration", no fixture or old pack substituting. `test_paper_custody.py:930-946` asserts
the exact pending row and flips to a real blob-digest assertion once the role registers; `configs/campaigns/d117_floor_qwen3-1p7b_v5/` is absent at HEAD. So **yes**: the
pending role is stated in both map and contract.

**WHOLE WINDOW — SATISFIED.** Registered binding target (`contract:74`) with no producer:
production dispatch reaches `_run_issuance_gate` (`:660-666`); `_ISSUANCE_GATES` holds only
`("d165_closeout", "d165-closeout.v1")`, so the ref returns
`paper_custody_issuance_gate_unregistered`. The unconditional `:1291-1296` stop is gone.

## 3. Results-fill-registry binding — REFUTED (gap stands; not a round-5 defect)

`docs/paper/results-fill-registry.md` (999 lines) has **zero** occurrences of
`paper_custody`, `D-173`, or `open_paper_input` — no row names a family/role.
Symmetrically the contract enumerates **no** custody-bound rows; its only registry
reference is the TR-01 link at `contract:75`. D-173's SCOPE clause is therefore declarative
only: nothing stops a claim-bearing row rendering from a non-custody supplier.

Round 5 was not chartered to close this (23's dispositions are the non-issuing type,
narrowing text, issuance gate, git_blob role, AST census), so it is pending work, not a delivered
defect. Before any claim-bearing row renders, (1) add contract section
`## Custody-bound registry rows` —

> A `results-fill-registry.md` row is **custody-bound** when its supplier column names a
> `paper_custody` family and role as `<family>/<supply role>`. Every claim-bearing row must
> be custody-bound before its value renders; a row naming no family and role is
> `STOP_FILL`. The table below enumerates every custody-bound row and is the only such
> enumeration. (Today it is empty: all five roles are fixtures.)

(2) add that token to the affected rows' supplier column; (3) add a test asserting contract
table and registry agree, shaped like `test_refusal_constructor_ast_census`.

**22's packet-hygiene MATERIAL is uncured:** `contract:75` still cites
`../paper/results-fill-registry.md#L920`. Line 920 is TR-01 today (verified this session),
but a raw line anchor breaks on any insertion above; use a row-ID anchor (`#tr-01`).

## 4. FLOOR_ACCEPTANCE pin — NOT REFUTED (1 AMEND)

Schema matches 23 Q-PS-4 / spec F3 exactly. `:526-554` requires exactly `{schema_version,
floor_sha256, sources, binder_source_sha256, anchor_head, status}` with schema
`joulewise.paper_floor_acceptance.v1`, `status == "PASS"`, `floor_sha256` = read floor bytes,
`sources` = the map census sorted/unique with `repository/`|`runs_root/` prefixes,
`binder_source_sha256` = a fresh `inspect.getsource` hash of
`bind_v2_floor_artifact_evidence`, and `anchor_head` a 40-hex **ancestor** of head
(`git merge-base --is-ancestor`) — the right fix for self-reference. Refusal is `issuance_prerequisite_missing`; the role joins the D-165/claims
censuses only when `mode == "production"` (`:363-366`). `contract:293-305` restates it, and
`contract:306-308` states the one-time desk check verbatim from 23 ("Before submission the
lead runs `bind_v2_floor_artifact_evidence`
once on each actual submission floor and its authenticated sources, then pins the pass
beside the finalized manifest. Fixtures do not satisfy this gate."), then 23's restricted
floor wording verbatim and `:311` "Acceptance is a pinned prerequisite, not a new receipt
family or an execution callback that unlocks a gate."

**AMEND (nit).** The seam verifies the *pin*, not that the census is the floor's true
member set (`_validate_floor_acceptance` compares `sources` to `ctx.source_census`). After
`contract:308` insert: `The seam checks only the pin — mapped source census, floor bytes,
binder source, anchor ancestry; that the census is the floor's true authenticated member set
is established by the desk run, not re-derived here.`

## 5. Supersession / re-pin — NOT REFUTED

`git log -- configs/paper_supply/supply_map.json` gives `2df32d5c` (v1) → `01d00591` (v2),
and the seam reads the map via `git show <head>:…` (`:964`), so any past anchor still
resolves its own v1 bytes. **No test or doc pins an old map digest** — the only literal is
the `"3" * 64` negative control at `test_paper_custody.py:464`, and `:493` compares the
live `evidence.supply_map_sha256`.

## 6. Overbuild vs "five typed refs, no receipt families" — NOT REFUTED (1 AMEND)

Still exactly five refs (`_FAMILY_SPECS`), no receipt family, no receipt reference class;
the gate registry holds one entry. Everything else new is named in spec 11, so inside 23's
single round: `joulewise/paper_rendering.py` (F1, boundary enforced by
`test_authentication_io.py:598-636`) and `joulewise/analysis_engine/claim_side_bound.py`
(F3, 67 lines, one public function).

* `_claim_issuance_gate` is deliberately **unregistered** — dead code in the trusted seam,
  yet hashed into `_validator_source_census` (`:723-724`), so every edit to it forces a
  fixture-receipt repin. Accepted: `contract:277-285` discloses it.
* **AMEND (hygiene).** `tests/fixtures/paper_custody/repin.py` and `run_kills.py` are dev
  scripts under a *fixtures* directory, on no test path — move to `scripts/paper_custody/`.

## Residual risk

F6 / REFUSAL-CARRIER-01 is deferred (`test_paper_rendering.py:46`), within spec 11's 6 Sep
readiness cut; until it lands OR-01/DS-32/PG-08 must stay `STOP_FILL`. Largest exposure is
§3: a ratified SCOPE clause with no mechanism behind it — fixture landing does not touch it,
the first claim-bearing supplier does.
