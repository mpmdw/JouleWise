# Charge — cold gate A291-FIX2-01: rule the fix-round-2 plan for the scored-night packer

Assembled 2026-09-24 by the resident magistrate (Opus 5.5, activation 7370d0fb). Nothing is armed. This gate is MANDATORY under the standing escalation rule: two consecutive rounds on the A291 packer failed with the same defect signature, so no code is written until a cold judge rules on the cure.

## Terms in plain words

The terms are built in `ex-06-plan.md` §1 and in `ex-02d-contract-v4.md` §0.4.
- A *block* is a group of MATH problems that one model answers inside one fixed-length power capture (an *envelope*).
- A *placement* puts a block in an envelope. It is *live* if the envelope's `blocks` list names that block.
- A *parent* is an original block. A *single* is a one-problem block split from a parent after a time overrun.
- A problem is *terminal* when it is refused for good; the refusal is recorded in `terminal_refusals`.
- The *seal* validates a roster and stamps its digest. *Replay* re-derives the whole event history from the root roster and must reproduce the roster.
- The *checker* is an oracle written separately from the packer (`tests/scored_roster_checker.py`). It reports which invariants of the §5 matrix a roster violates.
- A *gate population* decides whether a lever is null. A *position population* supplies the numbers averaged.

## Background

The code under review is at commit `20cd29de` (branch `feat/2026-09-24-a291-packer-recut`). Delta re-audit `ex-50-fix1-delta.md` found:
- a BLOCKER: a caller-resealed forged roster enters a trusted-output cache and skips replay;
- a repeat of the signature "a derived quantity misreads which placements or parents count".

Two blind consult seats answered `ex-01-consult-brief.md`: Sol 6.0 (`ex-02-consult-sol.md`) and Opus 5.5 (`ex-03-consult-opus.md`). The magistrate's synthesis and proposed plan is `ex-06-plan.md`. The magistrate bench-verified one load-bearing claim: the checker's `_derived` (`tests/scored_roster_checker.py:247-279`) is the packer's `_derived` (`joulewise/scored_packer.py:77-110`) with renamed variables. The judge should re-verify it.

## Questions (for each: AFFIRM the plan's text / write a different text / request a new rule; give the deciding exhibit or executed probe)

- **B1.** Root cause (`ex-06` §2 item 1): affirm or correct. Is the signature structural, as both seats say?
- **B2.** Delete `_TRUSTED_OUTPUTS` and replay at every external requeue entry (§2 item 2, plan step 5). Rule on the measured cost and on the residual "re-measure before any registration plans more than about 60 envelopes".
- **B3.** The population table (`ex-06` §4). Rule its exact text as a dated addendum that restates RD-4, RD-5, FT-10, §4.1 and X-5 without reopening them. Check each row against `ex-02d` and `ex-31`; the planned-spread row in particular is the magistrate's reading of the code, not of the contract. Also rule the gate-⊆-position rule and its refusal code.
- **B4.** Checker independence (D1). Must the checker's `_derived` and `check_executed` be re-derived by a separate seat that never reads the packer? Rule the seat's model family, what its brief may show it, and the similarity check the lens applies (method and threshold).
- **B5.** Seal order and the precondition row set (D2: INV-03, INV-11, INV-12, INV-17, INV-52). Rule the exact order, and whether the set is complete and not stricter than the contract.
- **B6.** The `ArithmeticError` backstop (D3): its code, its detail string, and the never-fires assertion.
- **B7.** `_seal(finalize=True)` stays callable (D5). Affirm or rule otherwise.
- **B8.** The test obligations: R1–R5b, the seed-driven generator's variation threshold (≥ 60% of cases differ between two seeds), and the mutation-fuzz operator list and properties (D4). Every regression must name its counterfactual input and the production call site it drives. Fill any gap.
- **B9.** Seat split, write scopes and sequencing (`ex-06` §5). Should seat P (packer) and seat K (checker) run in parallel? What do they integrate against? What happens when they disagree?
- **B10.** Anything the plan misses that would let the signature recur in round 2.

Finish with a single consolidated list, **"Final texts (paste verbatim into the P and K briefs)"**. Tier findings BLOCKER / MATERIAL / NIT.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody`, any `/Users/edr/JouleWise-measurement-*` directory, or `~/Library/LaunchAgents`.
- Code evidence comes from `git show 20cd29de:<path>`, or from executed probes in a `git archive 20cd29de` copy under `/tmp`.
- Write only the ruling file.
- Do not read any `docs/process_traces` file outside this packet directory, or RUN_STATE.md, TASK_QUEUE.md, council logs, run reports or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
84a3eef03b687a24e089fb050afdd0e843fc6ce4175b99ab04fb02a9dd456b33  ex-01-consult-brief.md
4ca1f8b01af42a6066386cb2d6684bbe850dd0243dbeddbea6bd9118a65e7114  ex-02-consult-sol.md
2e438f596afd54cce1f277f962954d87ae66a17e8554d1127aeb59d683b3a728  ex-02d-contract-v4.md
f1777dbc570f92bb02d808f6fb0c361de6def2271a4238f9a7067571188743bb  ex-03-consult-opus.md
2ecfea12bd15527e8c820272a3b583329692e0eabe97f52cb5d8bb127e5042eb  ex-06-plan.md
37f5064b95cabe5752d4564343b93dfa4c42b66041a1afe84e225dfade7446a6  ex-31-residual-rulings.md
0a4e23ec9c9387a8a91319fd7cb499ddf81b4ca040155c41cf4b2e5345dffdf1  ex-37-checker-opus-lens.md
1ea0a258c3104420e2f26cda5131cbc4fed7d13aebf09ec48a50abb22067f2c6  ex-50-fix1-delta.md
```
