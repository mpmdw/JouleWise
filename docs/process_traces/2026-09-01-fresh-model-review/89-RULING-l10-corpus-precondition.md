# 89 — Ruling: the L10 rehearsal corpus, and the phase's real shape (PR #259)

Date: 2026-09-01. Two seats on the OPEN RULING box in
`docs/process/v5-l10-rehearsal-phase.md` §C1: Sol xhigh
(`85-sol-l10-corpus-consult.md`) and an Opus 5 contract-lens refuter
(`88-opus-l10-corpus-lens.md`). Magistrate synthesis; no seat saw the other.

## Where the seats converged (installed)

1. The precondition "real, strict-valid, **claim-eligible** evidence **bound to
   the authenticated production pack**" is UNSOURCED. The kernel fence says
   only "Same head, production pack: a synthetic or smoke-scoped replay does
   not discharge this row" (`state_kernel.json` L10 row, fences[0]); D-160
   R-1 forbids a synthetic clean leg; neither text qualifies the corpus by
   claim eligibility. The doc invented the sentence that it then declared
   unsatisfiable.
2. No candidate corpus can run all seven steps positively before the window:
   steps 5–7 in positive form need a finalized manifest, which needs the
   full 80-member cover, which only the campaign produces. The phase is
   over-scoped, not merely mis-parameterized.
3. `RUNS_ROOT` (the contrast corpus) and `PRODUCER_RUNS_ROOT` (the floor-producer
   corpus for `d117_floor_qwen3_{1p7b,8b}_v5`) are different roles; §C1
   treats them as one. The floor-producer corpus is collected by the ALPHA and
   BETA arms of the transaction itself (registry roster ALPHA/BETA = floor
   packs, GAMMA = contrast), so it does not exist pre-window either.
4. D-160 R-2's "live tiny quarantined generation" was superseded by D-162 R-1
   (diagnostic family NOT built pre-campaign; re-homed to
   PIPELINE-SMOKE-TIER2-01). The OPEN RULING box's candidate (i) is stale.
5. ED-L10-1 never executed: `ready-packet/rows/ROW-L10.md:501` ("NO CLOSURE
   EVIDENCE LOCATED — still Ed-owed"), `30-ED-QUALIFICATION-rows.md:609-626`.
   The box's description of it as having "used" a9/a10 is false (Sol F3).
6. The G2-b shakedown root (`V5-G2B-SHAKEDOWN-01`) is the only real,
   same-head, production-`_v5`-pack corpus that exists before the window;
   it already carries the whole-window verdict and the pre-verdict bracket
   binding (NR-14) and needs to emit nothing new.

## Rulings

**R-1 (corpus).** The pre-window rehearsal reads the G2-b shakedown runs root
as `RUNS_ROOT`. Three-part ladder replaces the seven-step-before-window
contract:
- **L10-A (pre-window, gates V5-TRANSACTION-01):** step 1 strict validation
  and step 2 reduction on the G2-b block, outputs under `$L10_CUSTODY_ROOT`
  only; step 5 finalization on a SCRATCH custody copy with PASS defined as
  the singleton reason `analysis_finalization_member_cover_mismatch`
  (`joulewise/analysis_manifest_v3.py:2590,2598`) and nothing else — a
  refusal that reaches the member-cover gate has passed every custody,
  frozen-semantics, verdict-basis, bracket-byte and ledger-head check
  before it (D-162, `proof-consult/04-MAGISTRATE-RULING.md:46-47`).
- **L10-B (after the ALPHA/BETA floor arms, before the real mint):** steps
  3–4 on a scratch copy of the real floor-producer corpus, immediately
  before the production extraction/mint.
- **L10-C (after the last consuming arm, before any claim is published):**
  steps 5–7 in positive form on a scratch copy of the campaign corpus.
The L10 row is NOT closed by L10-A alone; its acceptance becomes the ladder
(kernel edit, bench). D-160's obligation — the full edge executed before
publication, never a synthetic clean leg — is preserved in full, so this is
a re-sequencing within the ruling, not a reversal; recorded as such.

**R-2 (no fence amendment).** `V5-G2B-SHAKEDOWN-01` fences[2] ("never
consumed by a floor, mint, or claim") stays VERBATIM. L10-A's reads are
strict validation, reduction, and a refusing finalizer on a scratch copy —
none is a floor, a mint, or a claim; the G2-b runsheet itself already runs
the exact-refusal finalizer against a scratch copy (`:1124-1149`). The record
carries the root's tree hash before and after (byte-unchanged proof). Any
future proposal to run extraction, mint, or `analyze-claims` on the G2-b
root IS a reinterpretation of that fence and goes to a cold gate.

**R-3 ("spent window").** The doc's gloss "a `[QUIET-MAC]` collection for the
claim-bearing night" is the correct reading of "before any window is spent",
sourced to D-167(1) (Ed 08-28: "diagnostic windows at lead discretion; the
transaction on Ed's go"). Cite it; do not present it as a definition.

**R-4 (lane).** Every L10 step is a desk command: no `sudo`, no `[QUIET-MAC]`,
writes only under `$L10_CUSTODY_ROOT`. Under Ed's 08-14 rule (Ed's hands are
for hardware/sudo only) the lane is BENCH — executed by the magistrate at the
bench, agent lane per the kernel row — not ED-FIRST. "ED-FIRST" is struck
throughout; the ed-batch-packet entry shrinks to the review of the record.

**R-5 (writing-standard defects — fix round).** Every sentence in the Opus
seat's Q5 list (items 1–10) is either sourced to a cited ruling line or
deleted: the self-contradiction between the quoted item 2 ("synthetic
exact-80-member corpus") and §C1 must be reconciled in one sentence (D-160
F-1 proves item 2 unexecutable on merged code, hence R-1); §D must stop
attributing an L10 clause to `V5-TRANSACTION-01`, which carries none until
the magistrate installs it; "BLOCKED until every FIRST CHECK passes" and the
per-step HEAD re-check are kept but labelled as this phase's own
refusals (and §E's "adds no refusal" claim corrected); the
`QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE` literal is labelled NEW, not
inherited; the PASS/FAIL rules follow the sentence that licenses them.

**R-6 (open item, not this lane's).** The G2-b runsheet's B-SUPPLY demands a
"real v5 aggregate-floor artifact" before G2-b, but the `_v5` floor-producer
corpus is collected by the transaction's ALPHA/BETA arms. One of the two is
wrong; routed to `V5-G2B-SHAKEDOWN-01` as a NEEDS-RULING note (bench).

## Dissent recorded

Opus recommended amending the G2-b immutability fence with a qualification-
only carve-out; declined per R-2 (a literal reading suffices once the roots
are separated and steps 3/4/6 leave the G2-b root). Sol held that closing the
full-edge row on G2-b alone would be a reversal needing a cold gate; agreed —
R-1 does not close the row on L10-A, so no cold gate is triggered.

## Erratum (2026-09-01, from the trace-90 delta re-audit)

R-1's citation `joulewise/analysis_manifest_v3.py:2590,2598` for
`analysis_finalization_member_cover_mismatch` is WRONG: those lines belong to
`analysis_prospective_member_cover_mismatch` (a different reason code,
raised while validating the prospective manifest). The finalization reason
is raised at `analysis_manifest_v3.py:2986,3008,3027,3034,3048,3093` (verified
at `6a6e340d`). The ruled PASS criterion — the singleton reason
`analysis_finalization_member_cover_mismatch` — is unchanged; only the
citation is corrected. The inherited citation came from the Opus consult
seat (`88-opus-l10-corpus-lens.md`) and was not opened before ruling; the
next ruling that cites a code line opens it first.
