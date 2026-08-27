# Draft registry row — `RQ-ATTRIBUTION-DOMINANCE`

**Status of this file: a DRAFT FOR THE MAGISTRATE TO LAND. It is not the registry.**
The paper director does not edit `docs/research_question_registry.md`; this file
carries the proposed row, the promotion-rule analysis the registry's own preamble
demands, and the one blocking prerequisite the director cannot satisfy alone.

Authority: `docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md`
items 8 and 9. Item 8 orders registration; item 9 fixes the capstone at one primary
research question, one demonstration contrast, and one printed negative result.

## 1. The question, as ruled

Item 8 states the question verbatim:

> Under the corrected clock model, does phase-boundary attribution rather than
> run-to-run scatter dominate the resolution bound for prefill and decode on the
> named M3 Max / MLX / `powermetrics` configuration?

## 2. The falsifier, as ruled

Item 8 adopts Sol turn 2 §1 in substance:

- For each claim-bearing phase cell, the point-only repeatability floor and the
  timing-widened floor are produced independently.
- The claim HOLDS where the timing term exceeds the repeatability term.
- The claim FALLS where it does not.
- A one-phase failure NARROWS the claim to the other phase.
- A total failure turns the capstone into "a calibration that corrected its own
  clock-model error, followed by a prospective null" — still defensible, with the
  Qwen contrast promoted to the principal demonstration.

This falsifier is what makes the row a research question rather than a methodology
artifact, which is the whole basis of item 8's ruling that `RQ-METHOD-FLOOR` cannot
carry the capstone's falsifiable claim.

## 3. Proposed row

Column order and vocabulary follow the registry's own column legend exactly. Two
variants are offered because of the blocking prerequisite in §4; the magistrate
picks one.

### Variant A — `candidate` (lands today, no other file changes)

| canonical_id | aliases | question_type | status | claim_ceiling | forbidden_upgrade | AP owner | campaign owner | gate_class | pre_hardware_preparable | one-line note |
|---|---|---|---|---|---|---|---|---|---|---|
| RQ-ATTRIBUTION-DOMINANCE | Attribution dominance; timing-vs-scatter dominance; the T26 capstone primary question | research question | candidate | L2 stack-conditioned, single unit, named boundary | no instrument-class or software-counter-class generalization from one unit and one stack; no transport of the dominance finding across load regimes while the pulse-to-inference transfer assumption is untested; no universal or probabilistic "detection" reading of a cell-specific resolution bound; no dominance claim for a cell whose two floor terms were not produced independently | none-yet | frozen `_v4` transaction; T26 paper sprint | floor | analysis-plan-only | Capstone's primary falsifiable question (T26 paper-goal magistrate ruling, 2026-08-27, item 8); falsifier is per-cell comparison of the point-only repeatability floor against the timing-widened floor; `RQ-METHOD-FLOOR` remains the methodology artifact this row consumes, not a substitute for it. |

### Variant B — `promoted` (requires the §4 prerequisite to land first)

Identical to Variant A except `status` becomes `promoted`. Do not land Variant B
until §4 is satisfied.

## 4. Promotion-rule analysis (the registry's own rules, checked one by one)

The registry preamble states: "Promotion rules are unchanged from
`docs/research_question_bank.md`: promotion still requires a named RQ slot in
`PROJECT_STATUS.md`, a data plan that does not displace queue ranks above it, and
scope fit."

| # | Rule | Met? | Evidence |
|---|---|---|---|
| 1 | A named RQ slot in `PROJECT_STATUS.md` | **NO — this is the blocker** | `PROJECT_STATUS.md` "Research questions:" (line 441) names Q1–Q6 only. There is no slot for an attribution-dominance question. Creating one is an edit to `PROJECT_STATUS.md`, which is outside the paper director's write scope and is a magistrate action. |
| 2 | A data plan that does not displace queue ranks above it | **YES** | The row consumes the ALREADY-FROZEN `_v4` pack's outputs. Ruling item 11 is explicit: "No pack change." The row therefore adds no measurement night and displaces no queue rank. |
| 3 | Scope fit | **YES** | Ruling items 1 and 9 make attribution dominance the capstone's science and cap the capstone at one primary RQ. The claim ceiling above holds the row inside D-078 cl.11's attribution-limited, stack-specific boundary. |

**Director's recommendation:** land Variant A (`candidate`) now so the row exists and
the paper can cite it, and let the magistrate decide whether to add the
`PROJECT_STATUS.md` RQ slot — the one act that unblocks `promoted`. Landing Variant B
without that slot would break the registry's own promotion rule, which is exactly the
defect item 8 corrected in the first place.

## 5. Dependency on the item-11 verification

The falsifier in §2 presumes that both floor terms — the point-only repeatability
floor and the timing-widened floor — are ISSUED per claim-bearing cell by the frozen
`_v4` pack's existing outputs. Ruling item 11 orders the paper director to verify that
and to report NEEDS-RULING if either term is not derivable at the desk. That
verification is reported separately. **If either term is not issued per cell, this
row's falsifier is not executable as written**, and the row should not be promoted
until the magistrate rules on the substitute.

## 6. What this row does NOT do

- It does not retire or re-scope `RQ-METHOD-FLOOR`, which stays a banked methodology
  artifact and remains the prerequisite for the comparative claims that consume floors.
- It does not touch `C5-1.1`, which remains the demonstration contrast in its permitted
  pairwise form (fixed 7B vs fixed 1.5B, never an active-parameter scaling law) per
  ruling item 9.
- It does not touch `RQ-SHORT-PREFILL-RESOLVABILITY`, which ruling item 9 designates
  the capstone's one printed negative result and which is already `answered-L1`.
- It does not re-adjudicate D-078 cl.11; the claim ceiling above restates that scope.
