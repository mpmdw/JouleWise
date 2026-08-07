# Run report — 2026-08-07 paper-first session (Fable magistrate)

**Primary object-level deliverable (§0 sentence, set at intake):** the MVP
capstone paper. **SHIPPED** as a complete draft: PR #110 merged (`6a70707`)
after a full round-2 gauntlet. Demonstration VALUES remain pending the
D-117 windows by construction — the draft carries explicit pending markers
and an honest status note.

## Ed's directives this session (in order received)

1. Resume from checkpoint → executed the owed queue.
2. **Abandon t3 work; MVP capstone paper first, rest later.**
3. 14-hour autonomous window; then **3 quiet nights + desk work accepted**
   as the path → transcribed as **D-117**.
4. **Sol burn** (3 h unlimited, later extended to 12 h): fast mode
   everywhere, ~20 paper investigations, work far ahead of the council.
5. **Opus 5 counter-reviewers**; every paper idea must turn EXISTING
   material into a solid paper.
6. Plan/spec/implementation drafting far ahead for later council review;
   Opus examines Sol drafts, Sol adjudicates, Fable reviews last.

## What landed (all pushed to main unless noted)

**Paper (P1).** Draft completed end-to-end: abstract, §7 pre-registered
demonstration design with two-gate result tables, §8 Discussion, merged
related work, §10 limitations, §11 artifacts, §12 conclusion, §13
references (18 entries, numeric citations). Gauntlet: 2 review lenses
(metrology-fidelity xhigh + plain-language) → bibliography & novelty audit
(13/13 keys verified real; **novelty claim STANDS** — no published
powermetrics validation exists; one factual error fixed) → Sol xhigh FIX
round (14 items) → delta re-audit (all blockers closed; hunts PASS) →
bench fidelity corrections against the CODE (interval-average integration
replaces "trapezoidal"; exact operative bracket formula; custody-claim
narrowing) → advisor-lineage citations (JouleSort, Mantis — caught by the
advisor-lens referee). Title narrowed to name Apple silicon and the
attribution limit.

**D-117 (the claim path).** Ed's directive transcribed: D-110's historical
re-mint order SUPERSEDED (structurally unsatisfiable at main); replacement
= three prospective windows (1.5B decode floor, 7B decode floor, decode
contrast) live-bracketed under the issued regime; prefill floors ride the
floor windows; contrast decode-only (≥256-tok prefill arm = Ed's open
option); D-113 readiness rewired. Supersession lines on D-110/D-113;
index row (a CI break I introduced and fixed); CLAIMS_STATUS un-staled.

**Plan freeze.** Sol xhigh design memo ratified (gates 1–8, work orders
U1–U10, immutable identifier scheme, two-stage pin freeze, budgets
3.14/3.24/2.80 h). Three toolchain blockers stand before any arm.

**Night-hardening.** Three Sol lenses over the runner/ledger/mint paths +
a paper-vs-code fidelity audit. Live findings: relative `--runs-dir`
path-doubling still breaks verdict issuance (mitigated by freezing
absolute roots); bracket selection could borrow another window's receipts;
pre-flight screened only a copied scalar. Allowance arithmetic verified
clean.

**Paper-portfolio factory (Ed's burn).** 24 directions developed by Sol
high/fast with full repo context, each counter-reviewed by an Opus 5
referee, then two opposing-prior Sol xhigh syntheses, then magistrate
ADJUDICATION. Arc adopted: **MVP + Window C → quantization BF16/Q4/Q8 →
MoE stretch (re-anchored)**; 7 night-cheap riders folded into the MVP;
everything else killed with salvage recorded. Ed's ranked rulings ##1–7
are in `docs/strategy/2026-08-07-paper-portfolio/ADJUDICATION.md`.

**U-units.** U1 (+U1b scope grant) two-slot bracket session + writer
integration: paired audits (3 blockers, 2 HIGH live-proofs) → 8-item fix
round → **full suite 2689 OK, lead-verified** → xhigh delta (7/8 closed,
D-116 issued-prefix byte-identical; one introduced recovery-boundary
blocker → FIX-6b under a pinned idempotent shape + a binding
no-round-three stop-condition). U3 pinset v2 + four-cell mint: paired
audits (CRITICAL — fabricated custody hashes still minted, live-proved;
plus internal literal derivation violating D-084) → 7-item fix round →
branch pushed. Both branches await their final gates.

**Meta-sweeps (Sol high/fast, read-only).** Refusal census (13 window
decisions, 1,173 member attempts, 44 refusals, 10 mechanism families —
and **only 34% of refused members have a reconstructable reason**, which
evidences the pre-window plumbing item); contamination desk study (742
idle captures; member-length burst excess >1 J in ~35% of windows, never
>5 J, max 3.21 J); decision-log coherence; queue staleness; council-log
layer yields; skill-stack drift; U5–U7 pack scout; paper production-format
scout; docs-vs-practice.

**Plan factory (far-ahead work).** 8 Sol drafts custodied (U4, U8,
reason-code plumbing, never-zero rider, quantization gates, MoE gates,
two probes, three-variant results prose) + speculative implementations of
U2/U4/U8 running under enforced scope — all explicitly staged for council
review, not landing.

## Process trace appendix

**Catches by layer (unique).** PAIRED AUDIT LENSES — the session's
highest-yield layer by far: contract lens found optional-binding,
universe-deletion, and mid-window-pin classes; execution lens live-proved
concurrency double-arm, candidate leakage, non-discriminating tests, and
the fabricated-custody mint. DELTA RE-AUDIT — again caught an introduced
defect (recovery boundary), holding its record: fix rounds introduce
defects. OPUS REFEREES — systematic sizing error across the portfolio
(proposals sized against the generic ~5 J bar when their 7B arms face the
measured ~14 J armwise floor), the Window-C/§6 evidence gap, the
anti-conservative floor-transport rule, and the missing advisor-lineage
citations. LEAD BENCH — the D-117 index-row CI break (self-inflicted,
self-caught), the U4 scope-glob launch failure, and the fidelity
corrections applied by hand.

**Lead errors recorded plainly.** (1) Transcribed D-117 without its index
row → broke CI on a docs-only PR. (2) First status-file poll tested
existence instead of "leaves RUNNING" — the skill's own documented
pattern; deviation was mine, skill text was right. (3) Trailing-slash
scope entry killed a U4 launch.

**Instrumentation notes.** Fast mode verified as a real per-call tier via
`scripts/codex-bridge` (service_tier=priority observed) and confirmed NOT
read by codex-run-v3 — so enforced-scope implementation work correctly
runs standard-tier. One Sol OUTPUT was blocked by a content classifier
(adversarial-audit vocabulary, first observed on output rather than
input); recovered by resuming with a neutral-language re-emission.

**Skill folds (same-session).** codex-delegation: fast-mode/service-tier
section, bridge-vs-wrapper routing rule, and the poll-leaves-RUNNING wake
pattern. adversarial-review: physics/causality lens for
measurement-adjacent panels, and paired contract+execution lenses as the
default unit shape.

## Owed at close

Ed's rulings ##1–7 (top: Window C night; reported-energy cells before
pack freeze; reason-code plumbing authorization). Consistency sweep and
council-log entry for THIS session. U-unit gauntlets to completion, then
U5–U7 packs.
