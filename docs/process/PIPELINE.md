# Pipeline: from idea to merged code

Lands as `docs/process/PIPELINE.md`. Authority: Ed approved formalizing the pipeline on 2026-11-17 and asked that it stay
small ("don't overbuild the meta-process"). Most changes need little checking; only tier 2 gets rounds.

## 1. Tiers

Each tier is a different amount of work, not a different degree of the same work.

| Tier | What | Steps | Merge when |
|---|---|---|---|
| **0** | Docs, records, RUN_STATE, briefs, tests, tooling, small fixes | build → CI → merge | CI green |
| **1** | Normal code, including code that cannot change a claim number | build → CI → **one cross-family review** → merge | CI green and no VERIFIED HIGH |
| **2** | Code that **arms, measures, offloads or deletes on the MBP**; anything touching **blinding, custody or prereg**; code that computes, selects or excludes a claim number | spec → **spec freeze** → build → CI + contract tests → review (**≤ 3 rounds**, §3) → integration owner accepts → lead accepts → merge | all of §3 and §4 hold |

**Tier assignment:** a change gets the highest tier that any path or behavior it touches qualifies for (the table
above), and the PR body states that tier on line 1. The lead may raise a tier at any time, and may lower one only with a
one-line reason in the PR body.

**Always on, at every tier** (carried over from `gate_policy.md` rule 7): CI; blinding; file hashes and custody
manifests; physical-hazard refusals and the agent census during collection; registration before data; the independent
recompute and its agreement bars; the #416 three-family audit, once per freeze of claim-collection code.

**Cross-family** means the reviewer's model family (OpenAI or Anthropic) differs from the builder's.

## 2. Findings (tiers 1 and 2)

Before a reviewer's finding can drive any work, it is labeled:
- **VERIFIED**: reproduced by a probe or test. The builder commits the failing test with the fix.
- **REFUTED**: shown wrong, with the evidence cited.
- **UNVERIFIED**: neither yet. It drives no work and is parked in the PR body.

Severity is HIGH, MED or LOW, set by whoever verifies the finding (not by the reviewer who raised it). Only a VERIFIED
HIGH blocks a merge. The labels go on the seat's ledger line (§6).

## 3. Tier 2 only: spec, freeze and convergence

- **Spec** = invariants, interface contracts, and acceptance scenarios written as failing tests. It is committed before
  the build starts, and the freeze is the commit sha of that spec.
- **Freeze:** a ruling that lands mid-build goes into spec v(n+1), not into the running build, unless it concerns
  safety or blinding. (#807 against RL-174 is the case this prevents.)
- **Round cap: 3.** In each round, record the VERIFIED counts by severity and each finding's root cause (one of:
  `spec-gap`, `contract-conflict`, `integration-seam`, `impl-bug`, `test-gap`, `fix-regression`) in one table in the PR
  body.
- **Decaying**, numerically: let *H_k* be the number of VERIFIED HIGH plus MED findings in round *k*. Round *k* is
  decaying when *H_k* ≤ ⌊*H_(k−1)*/2⌋ and none of its VERIFIED HIGHs has a root cause absent from earlier rounds.
- **Return to spec** (stop patching and write spec v(n+1)) when any of these holds:
  - round 2 is not decaying;
  - round 3 has any VERIFIED HIGH;
  - any round has a VERIFIED HIGH whose root cause is `spec-gap` or `contract-conflict`.

  There is no round 4. (#800 reached round 10 under the old rule.)

## 4. Tier 2 only: integration owner

A **cluster** is a set of open PRs that share a contract, a file, or a runtime path on the MBP (for example #800, #804
and #807). The lead names one **integration owner** per cluster in the first PR's body. The owner:
- keeps `tests/contracts/<cluster>/`, the shared contract suite, which every member PR must run green;
- sets the cluster's merge order;
- triages every `integration-seam` finding.

A member PR merges only after the owner's acceptance line.

## 5. Escalation

- **Ed:** only decisions that are his: science-design forks, changes to what a registration computes, excludes or counts
  that Fable cannot settle, money, and physical steps. Send a plain email: the outcome in the subject, at most 8 lines,
  no jargon (`MAGISTRATE_RELAUNCH_PROMPT.md` rule).
- **Fable 5.2 (research lead):** anything paper-bound, prereg, or blinding, and the retirement of a protected rule
  (§7). Fable has the final say there.
- **Lead:** everything else, including tier assignment, integration owners, return-to-spec calls, and routing. Ed is
  told afterwards.

Cold gates are convened only for registrations, claim-bearing results, irreversible actions, and owner-reserved choices
(moved here from the registry's "Convening triggers"). The judge follows `coldgate_charter.md`, whose bytes and digest
are unchanged.

## 6. Model routing: a measured hypothesis

The current defaults are hypotheses, not rules:

| Role | Default |
|---|---|
| Design and spec | Opus 5.5 or Mythos 5.2 |
| Paper-bound design | Fable 5.2 |
| Build | Sol 6.2 xhigh |
| Tier 1 review | one cross-family seat (Astra 6.2 high for a Claude build; Opus 5.5 or Mythos 5.2 for a Sol build) |
| Tier 2 review | one executing seat from each family |
| Mechanical work | Sonnet or Haiku |

Every seat gets **one line** in `model_allocation_ledger.md` §7. The lead may draw no routing conclusion
from fewer than **10 seats per (model, role) cell**. Sol 6.2 and Astra 6.2 are new, so every cell they are in is below
that bar today. Routing is revisited at each retirement pass (§7), with two numbers per cell: the verified rate
V/(V+R) and the count of escaped defects.

## 7. Rule lifecycle

Every standing rule or gate has a row in the rule register: id, one-line rule, source (file:line), owner, protects
(one of `blinding`, `prereg`, `physical-safety`, `science`, `custody`, `ops`), review_by date, and status.
- The register lands as `docs/process/RULES.md`, imported from the drift audit's `REGISTER.md`
  (`/Volumes/JW-EXT/scratch/astra-drift-audit/`) when that exists. Its statuses map as follows:
  - `LIVE` → live;
  - `STALE` → retire;
  - `DUPLICATE` → merge;
  - `SUPERSEDED-BUT-STILL-CITED` → retire and fix the citers;
  - `CONTRADICTED` → the lead rules.
- A new standing RUN_STATE item or gate gets its row the same day.
- **Retirement pass** every 14 days or at each block close, whichever comes first. The lead retires or renews every
  row past review_by. A row protecting `blinding`, `prereg` or `physical-safety` is retired only by the research lead.

## 8. What this supersedes (deleted or edited in the landing PR, no parallel copies)

- `docs/process/gate_policy.md`: **superseded in full and deleted**. Rules 1–2 become tier 0; rule 3 becomes tiers 1
  and 2; rule 4 (fix rounds until nothing above LOW) becomes §3; rule 5 becomes tier 1 plus §5; rule 6 (councils) stays
  as is, being one seat per family for one round on a genuine science fork only; rule 7 becomes "Always on"; rule 8 is
  unchanged (release); rule 9 (pruning tally) becomes §7. The "who decides" part of the 10-27 amendment becomes §5.
- `coldgate_charter_registry.md`: the sections "Convening triggers" and "Minimal validator (queued)" are replaced by §5
  and a one-line pointer.
- `docs/process/coldgate_charter_v3_candidate.md`: retired and deleted. The registry records its historical digest.
- `coldgate_charter.md`: bytes unchanged (it is hashed and ratified); it stays the judge's procedure.
- `model_allocation_ledger.md` §2 "Current standing allocation dictate" (Ed, 2026-07-26): superseded by §6. Sections
  3–6 stay as the historical record, and §7 is new.
- `CANONICAL.md`: one new row, "Process: how work moves → `docs/process/PIPELINE.md`".
