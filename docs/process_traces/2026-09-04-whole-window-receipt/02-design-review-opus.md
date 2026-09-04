# Opus contract-lens review — WHOLE-WINDOW-STOP-RECEIPT-01 design spec

Reviewing `01-design-spec-sol.md` at worktree head `f946f621` (base `913bf3f7`).
All anchors below were opened this session; sibling-commit anchors carry `@<sha>`.

## VERDICT: AMEND

The root-cause diagnosis is correct and independently verified, and the producer
call site is the right one. Three defects block an implementation seat: the
receipt wire drops a key the registered contract requires exactly; the mission's
own purpose (rendering a before-comparison stop) is not reachable from the
artifact this design produces, and the spec does not register that residual; and
the production authority chain terminates in an unnamed supply-map minting step.

### What is sound (do not re-litigate)

- **F1 is real.** `joulewise/whole_window.py:4172-4174` adds
  `whole_window_verdict_provenance_invalid` for *any* nonempty `core.conditions`,
  while `scripts/run_campaign.py:6324-6338` derives `status == "failed"` from
  exactly that nonempty-conditions condition. Every genuine admission failure is
  therefore reported as a provenance failure. `joulewise/whole_window.py:5290-5293`
  independently couples the NEG-8 refusal to `row.get("status") != "passed"`, and
  `:5475` returns only `(bool, tuple[str, ...])`. Split accumulation is the right
  cure; post-hoc whitelisting would be unsound.
- **The typed result is already registered normatively.** The in-flight contract
  at `docs/contracts/paper_supply_custody.md@3c27234e:219-221` names
  `WholeWindowRowValidation` and its `authentic` field as the thing that
  "distinguishes provenance validity from admission outcome". The spec is
  implementing a registered type, not proposing a new one. Keep the field name
  `authentic` verbatim.
- **Call site.** `scripts/run_campaign.py:6407` (`append_log`) then `:6408-6416`
  (byte-identical standalone publish) then `:6417`. Issuing under the lock after
  `:6416` and before `:6417` is correct: it is the only point where the exact
  published bytes and the lock token coexist.
- **Semantic identity.** `joulewise/whole_window.py:163-172` is six keys and the
  spec leaves it alone. Correct — exact-byte binding must not become a seventh key.
- **Acceptance test shape.** Three subtests (raw mutation, full reseal,
  replay-to-reopen replacement) match ruling 15's mandated census
  (`15-magistrate-ruling-custody-seam.md:9`) exactly, and the nominated required
  counterfactual — full reseal of every input, the inventory, and a
  caller-authored receipt with the supply-map pin held fixed — is the only arm
  that tests D-173's actual authority claim
  (`docs/decision_log.md@2e3349e1:10914-10922`: the map, not the caller, names
  digests). Keep it.

## Amendments (numbered, all required before an implementation seat)

**A1 — the receipt wire violates the registered exact-key list (blocker).**
`paper_supply_custody.md@3c27234e:178-182` requires the receipt to have
*exactly* `family`, `inputs`, `replay_codes`, `schema_version`, `status`,
`validator`, `validator_source_sha256`, and step 6 (`:193-195`) requires
`replay_codes` to equal the fresh replay result exactly. The spec's subtype
(01-design-spec-sol.md:62-78) **omits `replay_codes` entirely** and adds `result`.
As written the artifact fails the generic step-4 key check before the subtype is
ever consulted, and the design's own F3 item 3 only flags the *missing result*,
not the *dropped key*. AMEND: the subtype is the seven registered keys **plus**
`result`; `replay_codes` retains its step-6 meaning (`()` for a clean typed
replay), and `result` carries the structured admission finding. State in the
D-173 amendment that subtypes may add keys but may never drop one.

**A2 — the mission's rendering target is not reachable, and the spec does not
register that (blocker).** The mission exists to let a before-comparison stop be
rendered (`07-magistrate-rulings-addendum.md:7`, clause 2). The renderable
target is OR-01, whose registered form is "before comparison: `<model>` — `<issued
stop reason>`" (`06-magistrate-contract-rulings.md:24`) and whose registry row
requires "the reason issued by that governing evidence"
(`docs/paper/results-fill-registry.md:921`). The receipt supplies `targets[].model_id`
(good — the model name comes from an authenticated join, satisfying the
"no unissued name in prose" test) but supplies the reason only as
`admission_reasons[].reason_code`, i.e. D-078 vocabulary
(`docs/decision_log.md:4257-4271`), which the spec then declares non-renderable
(01-design-spec-sol.md:168) and which ruling 15 also forbids rendering
(`15-magistrate-ruling-custody-seam.md:8`). The result: this receipt lands and
OR-01 is *still* STOP_FILL. AMEND, choose one and say which:
  (a) build the addendum-16 §3 pattern for this vocabulary — a module-level
  constant enumeration of whole-window admission reason codes plus a registered
  code→sentence map, cross-checked by a test that fails when either side gains or
  loses a code (`16-magistrate-rulings-addendum-5.md:7` establishes exactly this
  shape for `D165_CLOSEOUT_REFUSAL_CODES` / `D165_OR01_REASON_SENTENCES`); or
  (b) declare explicitly that OR-01 remains STOP_FILL after this mission, add
  `docs/paper/results-fill-registry.md` to WRITE_SCOPE, and register the residual
  on the OR-01 row naming the follow-on mission.
Silence is not acceptable: a downstream seat reading only this spec will invent a
sentence map, which is the exact failure class D-173 was written against
(`docs/decision_log.md@2e3349e1:10905-10909`).

**A3 — the production authority chain has an unnamed final link (blocker for
production; not for fixtures).** The receipt's authority is the supply-map pin
(`paper_supply_custody.md@3c27234e:175-177`), and addendum 16 requires that map to
be git-tracked and read under a clean-tree anchor
(`16-magistrate-rulings-addendum-5.md:5`). A receipt minted at measurement time has
a digest that is by construction not yet in a clean-tree-anchored git file. The
spec's residual-risk note (01-design-spec-sol.md:172-174) says measurement decides
"receipt/inventory bytes" but never says who writes the map row, under what gate,
or what the read returns until then. AMEND: state that production reads return
`paper_custody_receipt_unissued` until a lead-owned, separately gated map-row
minting step lands, and mark `configs/paper_supply/supply_map.json` in WRITE_SCOPE
as **fixture rows only** — the sibling CLAIM-NONISSUANCE spec already draws this
line correctly (its WRITE_SCOPE note excludes "live production supply-map values");
this spec does not.

**A4 — base-commit incoherence across the two sibling lanes (should-fix).**
This spec anchors D-173 and the contract at `3c27234e`; the sibling
CLAIM-NONISSUANCE spec anchors them at `2e3349e1`. `3c27234e` is an ancestor of
`2e3349e1` (verified), and `2e3349e1` changes the floor-loader wire that the
contract's lower-boundary section describes (`@3c27234e:233-240` still names the
*old* `joulewise.inputs.load_floor_artifact`). Neither anchor exists at this
worktree's base `913bf3f7`. AMEND: pin both lanes to `2e3349e1` or later and
re-verify `@3c27234e:178-195` and `:219-221` against the chosen anchor — flag F1
says "compose owning branches" but names no commit.

**A5 — say what happens to `flagged` (should-fix).**
`scripts/run_campaign.py:6335-6336` produces `flagged` for an exploratory-profile
campaign whose core did **not** pass: an authentic, non-admitted row, i.e. the
"before-comparison stop" population — yet the issuance predicate
(01-design-spec-sol.md:100-104) admits only `status == "failed"`. That may be the
right conservative call, but it is implicit. AMEND: state that exploratory
`flagged` is deliberately excluded and why, so a later seat does not widen it.

**A6 — cross-lane branch precedence is undefined (should-fix).** DS-32
(`docs/paper/results-fill-registry.md:885`) carries two absence branches: "required
token-generation verdict absent" (the sibling CLAIM-NONISSUANCE artifact) and
"stopped before comparison: `<issued reason>`" (this artifact). Both receipts can
in principle exist for one campaign. `06-magistrate-contract-rulings.md:26`
registers the stage order — a before-comparison stop wins over a close-out stop —
but neither design cites it. AMEND: bind the DS-32/PG-08 branch predicate to that
registered stage order by reference, and add one arm to the acceptance test where
both governed artifacts are present and the before-comparison branch is the one
rendered.

**A7 — nit, cited-line drift.** `:4172-4175` is `:4172-4174`; `:5666-5713` does not
resolve to the tuple-returning site — `whole_window.py:5475` and the
`whole_window_refusal_reasons` definition at `:5525` are the real anchors.

## Answers to the five contract questions

1. **Authority chain:** closed for fixtures, open for production (A3). A
   caller-authored receipt cannot pass, because the map pin is computed
   independently and the spec forbids a self-asserted ID (01-design-spec-sol.md:90-92)
   — correct and consistent with `paper_supply_custody.md@3c27234e:175-177`. A
   *replayed old* receipt is caught by step 7's reopen
   (`@3c27234e:196-199`, `paper_custody_input_changed`) plus the row-uniqueness
   code, which is the right pairing.
2. **Registered-contract contradiction:** yes, one — A1 (`@3c27234e:178-182`).
3. **Unissued value reaching prose:** no number and no model name (both join
   through the authenticated prospective manifest); but the *reason* path is
   simply absent, not safe — see A2.
4. **Counterfactual:** correct as nominated (full reseal with the pin held fixed);
   add the A6 dual-artifact arm.
5. **Decision-log:** amend D-173 (`docs/decision_log.md@2e3349e1:10903-10932`), do
   not allocate a new number. Correct call — the mission is already authorized by
   `15-magistrate-ruling-custody-seam.md:7` and
   `07-magistrate-rulings-addendum.md:7`. The amendment must carry A1's
   "subtypes add, never drop" rule and A3's production-gating sentence, and it is
   magistrate-owned: `docs/decision_log.md` stays outside the implementation
   seat's WRITE_SCOPE (this spec currently includes it — remove it).
