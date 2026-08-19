# MAGISTRATE RULING — R2: Mint-lane fan-out shape (pack identity)

Fable magistrate, 2026-08-19. Co-design protocol (D-144-pending). Seats:
terra (gpt-5.6-terra, xhigh) and Opus 5, independent designs + one bounded
debate round. Documents: R2-brief.md, R2-terra.md, R2-opus.md,
R2-debate-agenda.md, R2-debate-terra.md, R2-debate-opus.md (this custody
directory). Both seats INDEPENDENTLY converged on the composite shape —
recorded as protocol evidence.

Classification: BIG design (pack-family supersession; schema conditional).
Consequences: implementation gauntlet + Fable final review + one more
seat-pass over the implemented artifact pre-merge.

## Ratified spec

**S1 — Composite, two axes.** (i) CODE LAYER: mint policy (bracket screen +
allowance rule) is generation-resolved, never copied — no literal screen
scalar or screen-substituted rule string anywhere in the mint lane. (ii)
ARTIFACT LAYER: a new immutable `_v3` pack family
(`d117_floor_qwen25_1p5b_v3`, `d117_floor_qwen25_7b_v3`,
`d117_contrast_qwen25_1p5b_vs_7b_v3`). Flat migration stays REFUTED
(executed both seats: 8F/49E and 14F/49E variants). Neither axis alone
suffices (executed refutations in both design docs).

**S2 — Resolver (hybrid sourcing; supersedes both seats' round-0 clauses).**
Resolution authority is the registered D-102 generation entry keyed by the
supplied acceptance's own `acceptance_id`
(`calibration_bracketing._D102_GENERATION_DERIVATIONS`; new public accessors
adjacent to it, ~15 lines). Unregistered id ⇒ refusal. If the supplied
acceptance also carries `decimal_derivation.ratified_operatives`, its
`bracket_screen_s` MUST equal the registered value or the call refuses
(crosswire guard — terra's requirement, opus's execution: honest inputs can
never trip it because `_valid_acceptance_bound` already forces agreement;
stubs served from registry keep the n=19 replay 37/37).

**S3 — Frozen family is untouchable, generators included.** The three `_v2`
pack roots — INCLUDING their `generate_configs.py` files, whose sha256s are
pinned in `plan_tree.json`, `arm_readiness.sources/pack-authentication.json`,
and `arm_readiness.sources/multicell-mint.json` inside each frozen pack, and
whose pack digests are published in the T10 session record and Ed's morning
packet — are READ-ONLY. (Opus conceded its own C6 here; M-2 class.)
`_v1` untouched. `freeze-0002` receipts stand forever. PARKED STEP 6 IS
AMENDED: freeze-0003 mints on the `_v3` roots at the measurement checkout
(`/Users/edr/JouleWise-measurement-20260818`, path-binding), ordinal =
predecessor+1, `predecessor` binding each pack's `_v2` + its freeze-0002.
No freeze-0002 re-mint anywhere.

**S4 — `_v3` production route (no new tracked tooling).** Emit each `_v3`
tree by running the UNEDITED `_v2` generator with
`--pack-id <family>_v3 --family-suffix _v3`; then edit the emitted,
UNFROZEN `_v3/generate_configs.py` at exactly three sites
(`SUCCESSOR_ACCEPTANCE_{REL,SHA256,DERIVATION_SHA256,ID}` → r5;
`calibration_basis()["allowance_rule"]` derived from `acceptance_pin()`;
`CURRENT_FROZEN_RECEIPT_SHA256` → that pack's own `_v2` freeze-0002 sha —
hygiene: currently inherited as v1's); self-regenerate; `--check` per `_v3`
root; `--check --preserve-current-frozen-bytes` per `_v2` root as the
frozen-family regression assertion. New code in the transaction is ONLY:
the resolver + call-site rewiring, the `schema_v2.json` acceptance-id
conditional, the genesis rename (S6), and a no-copied-scalar guard test
(forbids `0.010818`/`0.009724` literals in kernel sources, mirroring the
preflight guard-test precedent). Tracked golden-regeneration CLI stays
BARRED; goldens move only via the `_fixture_canonical_sha256` review step.

**S5 — Touch points.** Opus C1–C5 and C7–C9 as written, as amended by the
debate; C6 replaced by S4. terra F3's evidence-author row is STRUCK
(off-agenda blocker upheld: same-ordinal sibling derivation would break the
frozen `_v2` evidence replay that `evidence-pack-family.json` byte-pins);
`arm_readiness_evidence.py` is UNEDITED this transaction and the successor
PACK_FAMILY route stays queued to the arm_readiness row-registry install as
a recorded carried limitation. Evidence-author acceptance copy-list gains
r3+r4+r5 INSIDE the transaction (necessity). `_ACCEPTANCE_SELECTION` does
not move (renaming it is noted as a separate independent-axis decision, not
taken here).

**S6 — Genesis digest.** `DEFAULT_ACCEPTANCE_BOUND_SHA256` is RENAMED ONLY
(→ `GENESIS_FIXTURE_ACCEPTANCE_SHA256`), value `9a264c57…` unchanged, both
call sites renamed, comment stating it authenticates the retained
`schema_fixture_unissued` genesis bytes and is NOT the digest of
`DEFAULT_ACCEPTANCE_BOUND_PATH`; plus a regression test closing the
executed-proven silent-coverage gap (value change breaks genesis
authentication with zero test failures today).

**S7 — Acceptance binding: r5 at birth.** Per the R1 ruling (S9 there), the
capture flip mandates the science-neutral D-079 r5. The `_v3` family binds
r5 — never emitted at r4 and retargeted later (the generator pins the
acceptance FILE sha at emission; r4's file is unchanged by an r5 issuance,
so the pin would NOT refuse — silent stale binding, executed-verified
hazard). r5 rebind surface is opus item-4(a) as written (registry row,
D-102 alias row to `_D102_N17_DERIVATION`, `arm_readiness.py:4148` issued
set + reserved successor ids, corpus-verify alias, live-default path
literals, goldens, copy-list). Screen/rule values do NOT change (r5 is
science-neutral to r4); schema value enums unchanged.

**S8 — Sequencing (binding; opus S0–S6 adopted).**
S0 R2 kernel (resolver + rewiring + schema + genesis rename; r5-neutral) →
S1 R1 flip + r5 issuance in one commit (+ the one-line r5 registry/routing
rows; live default → r5) → S2 golden re-derivation ONCE against r5 →
S3 `_v3` emission ×3 → draft retarget to r5 → self-regen → checks →
S4 evidence re-author ×3 at the measurement checkout →
S5 freeze-0003 ×3 (LAST acceptance-bearing step) →
S6 docs/bookkeeping → canonical FULL GREEN.
Hard invariants: freeze-0003 last; bind-at-birth (S7). R2's files do not
intersect r4/r5's four estimator pins ⇒ no r6 (both seats verified).

**S9 — Expected fan-out ownership.** R2 owns the 33 mint-lane reds; R1 owns
the whole-window red + the two `test_authentication_io` reds; docs-freshness
red is bookkeeping. FULL GREEN requires both rulings landed in ONE
integration tree before the merge wave.

## Rejected alternatives (ratified from seats)
Flat migration (twice-refuted); generation-indexing alone; `_v3` family
alone with static constants; in-place `_v2` regeneration (mechanically
refused by the generator; M-2); artifact-sourced resolution (breaks replay
fixtures 14F/49E); set-membership screen check (crosswire); staying at r2
(science defect: screen descends from a corpus containing the refused
member); tracked golden regenerator; editing `_v2` generators (frozen pack
content); evidence-author sibling derivation (frozen replay breakage).

## Open items routed to Ed
(1) Family-marker particulars: `_v3` lands FIRST, machine-readable
supersession marker retrofits via its own co-design pass (both seats
recommend; magistrate concurs). (2) `_v2`-arm parallel question: this
ruling assumes single-arm supersession per Ed's recorded "complete the
cycle" lean; a parallel `_v2` arm would need a design not built here.
(3) R1 row-registry reserved values: R2 supplies three of the five
(`successor_pack_ids` = the three `_v3` ids). (4) The r5 issuance amends
the confirmation-table basis again — the v3 confirmation table Ed is owed
will carry r5, not r4, identities.
