# OPEN-ITEMS — unresolvable from the record at `4597ad4`

Each item states the question, what the record does say, why it does not
settle it, and who must resolve it. Nothing here is guessed at in the value
files.

---

## OPEN-ITEM 1 — "The five" is two incompatible lists (BLOCKS the ruling's framing)

**Question.** Does `successor_pack_ids` belong to the five reserved values or
not?

**What the record says.**
- *Enumeration A* (mechanical, from the executed refusal): the five are
  environment comparisons, the 14 EXECUTION_BOUND horizons, the
  refusal-vocabulary spellings, the arm-to-consume budget, and the
  family-publication marker schema — and it says in the same sentence that
  D-139 A3 **had already approved** the successor IDs.
  `git show 35badb4` (commit body); restated
  `docs/run_reports/2026-08-18-t10-session.md:740-754`;
  `docs/process/ed-morning-packet-2026-08-18.md:18`;
  `docs/process/phase2-transaction-runsheet.md:12-14`.
- *Enumeration B*: "R2 supplies three of the five (`successor_pack_ids` = the
  three `_v3` ids)" —
  `docs/process_traces/2026-08-19-r1-r2-codesign/14-r2-ruling.md:125-127`,
  sourced from `06-r2-design-opus.md:727-730`, carried into
  `RUN_STATE.md:34-38`, `:94-96`, `:184-186`, `:330-332` and
  `docs/process/ed-s5-mint-decision-2026-08-19.md` ("three of five are now
  supplied").

**Why the record does not settle it.** The R2 design document states both
readings in adjacent sentences — "That is **one** of the 'R1 registry
reserved values (five items)'… R2 supplies **three** of the five" — and the
ruling copied the second. No document reconciles them. D-139 A3 approved the
IDs as `_v2`; D-147 superseded the family to `_v3` without saying whether
that reopens an approved item or adds a new one.

**Who resolves.** The magistrate, in the ruling's first clause. The packet's
disposition (A is authoritative; `successor_pack_ids` is a reopened sixth)
is a recommendation, not a finding.

---

## OPEN-ITEM 2 — Does installing the registry break the frozen `_v3` family? (BLOCKER)

**Question.** The three `_v3` packs byte-pin
`row_registry.sha256 = d248fdc5…` (the current v1 registry file) in both
their frozen plan trees and their `freeze-0003` receipts. Installing v2 bytes
at that path changes the sha256. Does that make all three packs refuse?

**What the record says.** Nothing. This interaction appears in no consult, no
ruling, no runsheet, and no session report. The R2 design's §(e) analysed the
`_plan_profile`/`successor_pack_ids` interaction and concluded *"Not needed:
an R1 row-registry install"* for the `_v3` transaction
(`06-r2-design-opus.md:464-475`) — it did not analyse the reverse direction,
i.e. what a later install does to the by-then-frozen packs.

**Why the record does not settle it.** The install was scheduled (runsheet
step 4) when the family was `_v2` and unfrozen; the freeze then happened
first, under D-147, changing the ordering. Nobody re-examined step 4 against
the new ordering.

**Assembly's reading of the code** (`07-council-brief.md` §4): equality is
required at `arm_readiness.py:2798`, `:5181-5185`, `:6301-6305`, against a
reference built from live bytes at `:2764-2782`. On that reading the install
breaks the family. **This is a code reading, not an executed experiment**;
the packet did not run the scenario (read-only mandate).

**Who resolves.** An execution seat must run it. Then the magistrate rules,
with a cold-instance pass — it is contract-bearing and adjacent to
irreversible (rule 11).

---

## OPEN-ITEM 3 — `capability_horizon_ns` is reserved but is not on the five-item list

**Question.** Is `arm_policy.capability_horizon_ns` a sixth/seventh reserved
value the council must rule, or was it approved by D-139 A3's "existing
operational horizons"?

**What the record says.**
- It carries an `ED_RESERVED:` placeholder (`arm_readiness.py:534`), so the
  registry cannot load without it.
- R1 clause 7 lists it explicitly among what must be resolved: *"generic
  execution horizons, **ARM capability horizon**, arm-to-consume budget…"*
  (`docs/decision_log.md:9306-9308`).
- The install refusal's five-item list names only the arm-to-consume budget
  (`git show 35badb4`).
- D-139 A3 approved *"the existing operational horizons — 20-minute volatile
  / six-hour procedural"* (`docs/decision_log.md:10078-10083`), which are T-0
  evidence horizons (`arm_readiness_evidence_t0.py:47-50`), not an ARM
  capability horizon. `ARM_CAPABILITY` is a distinct class,
  `TEMPORAL_CAPABILITY` (`arm_readiness.py:706`), and is explicitly *"not an
  evidence-policy row"* (`:673-675`).

**Why the record does not settle it.** The five-item list omits it without
saying why. Either the omission is an oversight, or the author considered it
covered by D-139 — no document says which.

**Who resolves.** The council must rule the value regardless (the registry
will not load otherwise); the magistrate should record whether it counts as a
reserved value or an approved default, so the "five" is stated truthfully.

---

## OPEN-ITEM 4 — The consumption-edge re-probe set is unspecified

**Question.** Which volatile predicates must be re-probed at consumption?

**What the record says.** The consult reserves it in the same breath as the
budget: *"Rule the short horizons, arm-to-consume safety margin, **and which
volatile predicates must be re-probed at consumption**"*
(`docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/consult.md:248`);
the plan consult repeats it as approval item 2
(`2026-08-16-phase2-plan-consult/consult.md:373`).

**Why the record does not settle it.** It has no registry field. It is not in
`_R1_REGISTRY_KEYS` (`arm_readiness.py:479-489`), so the council cannot
install it even if it rules it. Yet `05-arm-to-consume-budget.md`
alternative 4 depends on it: a longer budget is only defensible with
re-probing.

**Who resolves.** The magistrate must decide whether this is (a) out of scope
for the registry install and carried, (b) satisfied by existing consumption
volatile checks (`volatile_checks` is a consumption-receipt key at
`arm_readiness.py:563` and `:586`, validated sorted-unique at `:2444-2447`
and populated at `:7412` — a seat should trace what actually goes in it), or
(c) a schema gap requiring its own design pass.

---

## OPEN-ITEM 5 — `cross_chain_numbering` and `freeze_receipt_v2_predecessor_bindings`: ruled in substance, unspecified in bytes

**Question.** What exact string / list does the registry carry?

**What the record says.** D-139 A3 approved the **semantics**:
*"chain-monotonic `freeze-0002` with explicit predecessor bindings"*
(`docs/decision_log.md:10078-10082`). D-147 S3 moved the chain forward:
*"freeze-0003 mints on the `_v3` roots … ordinal = predecessor+1,
`predecessor` binding each pack's `_v2` + its freeze-0002"*
(`14-r2-ruling.md:42-47`). The cold gate flagged that the numbering semantics
*"must be specified in the freeze-receipt v2 schema, not left to tool
behavior; on Ed's reserved list"*
(`2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:61`).

**Why the record does not settle it.** Approved semantics are not installable
bytes. The validator demands a **string** for `cross_chain_numbering` and a
**sorted, non-empty, unique list of strings** for
`freeze_receipt_v2_predecessor_bindings` (`arm_readiness.py:1720-1736`), and
imposes no vocabulary on either. Neither field has any consumer in
`joulewise/` (verified by grep) — like the marker schema, they are inert
today. And the approved semantics named `freeze-0002`, while the live chain
is `freeze-0003`.

**Available shape hints, not proposals.** The fixture uses
`"test.freeze-0002.v1"` and
`["evidence_set_root", "freeze_receipt", "identity_receipt", "pack_digest", "pack_id"]`
(`tests/test_arm_readiness_evidence.py:68-75`). The actual predecessor object
the code derives has keys `pack_id`, `pack_path`, `pack_digest_algorithm`,
`pack_sha256`, `plan_id`, `plan_sha256`, `freeze_receipt`,
`identity_receipt`, `evidence_set_sha256`
(`FREEZE_PREDECESSOR_KEYS`, `arm_readiness.py:382-392`;
`_derive_freeze_predecessor`, `:5113-5148`) — nine, not five. Whether the
registry's binding list is meant to mirror that key set, or to name a subset
that must be present, is undefined.

**Who resolves.** The council, as part of §1c. It should also say whether the
strings are meant to become live gates or remain declarative.

---

## OPEN-ITEM 6 — The outer v2 `registry_id` and the file path/name

**Question.** What is the v2 row registry's `registry_id`, and does the file
stay at `configs/arm_readiness/d117_row_registry_v1.json`?

**What the record says.** Under v1 the id is pinned:
`registry["registry_id"] != ROW_REGISTRY_ID` refuses
(`arm_readiness.py:1853-1858`), `ROW_REGISTRY_ID = "d117-row-registry-v1"`
(`:46`). Under **v2** that check does not apply — only `_require_string`
(`:1859-1861`). The path constant is unconditional:
`ROW_REGISTRY_RELATIVE_PATH = Path("configs/arm_readiness/d117_row_registry_v1.json")`
(`:80`). The test fixture uses `"test-r1-row-registry-v2"`
(`tests/test_arm_readiness_evidence.py:93`).

**Why the record does not settle it.** No document names the production v2
id. And a v2-schema registry living in a file called `…_v1.json` is a
standing legibility trap — but the filename is byte-pinned inside the frozen
`_v3` artifacts (OPEN-ITEM 2), so renaming it is not free.

**Who resolves.** The council, jointly with OPEN-ITEM 2's disposition.

---

## OPEN-ITEM 7 — Retroactivity: `_v3` evidence was authored under the v1 registry

**Question.** Does installing lifecycle policies require re-authoring the
`_v3` packs' evidence?

**What the record says.** The `_v3` evidence was authored at S4 on 2026-08-19
(`docs/process/ed-s5-mint-decision-2026-08-19.md`, S4 rollups
`0e353456…` / `1421ea4e…` / `653f22c0…`) with the **v1** registry live —
therefore no R1 lifecycle policy applied to it. The R1 lane's own position is
that successor evidence must be *"FRESHLY RE-AUTHORED at the new reviewed
head under the new schema — re-derivation, not re-blessing"*
(`2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:57`),
and R1 forbids grandfathering (`V1_GRANDFATHERING` role,
`arm_readiness.py:497`).

**Why the record does not settle it.** That language addresses v1→v2 pack
succession, not "evidence authored before the lifecycle registry existed."
No document asks whether installing the registry retroactively obliges a
re-author of already-frozen `_v3` evidence — and a re-author would require a
new freeze, which the packs' immutability forbids.

**Who resolves.** The magistrate. If the answer is "yes, re-author", this
converges with OPEN-ITEM 2 on the same conclusion: the install cannot follow
the freeze.

---

## OPEN-ITEM 8 — Successor PACK_FAMILY route: build or carry? (D-147 S5)

**Question.** D-147 S5 queued *"the successor PACK_FAMILY route … to the
arm_readiness row-registry install as a recorded carried limitation"*
(`14-r2-ruling.md:69-71`). Does this council build it or carry it again?

**What the record says.** The route does not exist:
*"a registry-driven successor route for PACK_FAMILY derivation is NOT yet
built (reported to the magistrate with the R1 registry install)"*
(`joulewise/arm_readiness_evidence.py:52-55`). `_derive_pack_family` iterates
the hardcoded `_v1` map (`:1348-1355`). D-147 left
`arm_readiness_evidence.py` UNEDITED by design.

**Why the record does not settle it.** "Queued to the install as a carried
limitation" is ambiguous between *the install discharges it* and *the install
inherits it*. No decision picks one.

**Who resolves.** The council, with a cost statement either way
(`07-council-brief.md` §3). If carried, it needs a registration site — note
that D-148.6/.7 limitations were registered in `CLAIMS_STATUS.md`
(`docs/decision_log.md:171`), which is the precedent.

---

## OPEN-ITEM 9 — Was the whole install premised on ordering that no longer holds?

**Question.** Runsheet step 4 sits inside the Phase-2 atomic re-freeze
transaction, before the freeze. That transaction's steps 1–3 and 5 executed;
step 4 refused; then D-147 re-executed the family as `_v3` with a new
freeze. Is "step 4" still a meaningful instruction?

**What the record says.**
`docs/process/phase2-transaction-runsheet.md:10-15` records the 2026-08-18
status (steps 1-3 and 5 executed, step 4 NEEDS_RULING, steps 6-7 pending).
The document is explicitly *"a living operational document, so the steps
below are edited in place"* (`:16-18`), but it has **not** been amended for
D-147's `_v3`/`freeze-0003` supersession — it still describes a `_v2` /
`freeze-0002` transaction throughout.

**Why the record does not settle it.** The runsheet is stale relative to
D-147 and nobody has re-derived what step 4 means now. Steps 6 (exact-byte
table) and 7 (publication) are also still pending against `_v2` identities.

**Who resolves.** The lead, as bookkeeping, before the ruling lands — a
stale runsheet is what produced the ordering surprise in OPEN-ITEM 2. This is
also a consistency-sweep item for the close-out commit.
