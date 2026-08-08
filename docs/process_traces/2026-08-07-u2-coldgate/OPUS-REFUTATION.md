# U2 cold-gate adverse refutation — Opus contract lens (2026-08-07)

Convened by the magistrate per README.md: Opus subagent, isolated git
worktree, adverse contract lens, sealed from the cold Fable judge
pre-synthesis. Recorded from the refuter's final report.

**Exhibit:** `impl/d117-u2-successor` @ `399ffebd`. **Actual main:**
`e1a8fc86` — 17 commits ahead of the packet's baseline (undisclosed
staleness), including the fired U1 append-recovery escalation, D-118,
D-119.

**Credit first:** the refuter independently replayed all five D-102
ratified operatives through the exhibit's pinned constants — all five
reproduce exactly (budget cap, 95% prediction, bracket screen, preflight
level screen, max budgetable excess). Nobody in the assembly had checked
this; it holds.

## Verdicts

| Q | Severity | Core |
|---|---|---|
| Q1 | **CONTRACT-BREAK** | Selector absorbs the two valid Window-B fiducials D-116 says "do not influence the bound" (Window-A-only basis); D-109 R2.2 ("derivation_corpus remains exactly the n=19 threshold-producing observations") and R2.6 (absorption only after trigger disposition) omitted from the packet; ~11 of 30 valid members were in prior_observation_set at cutoff, never trigger-disposed, yet absorbed into the threshold basis |
| Q2 | **UNSOUND** | `max(level_maximum, two_draw_prediction)` mixes incommensurable quantities (ratio 3.80x); a no-op at n=19; binds only when the corpus is tightest and then RAISES the systematic screen — anti-conservative in RT-1's direction |
| Q3 | **UNSOUND** | Algorithm short-circuited at the only verified df; the "algorithm" test asserts a dictionary lookup; 63 unratified digits hashed into derivation_sha256; continued fraction raises ArithmeticError at 10k iterations with no governed refusal; bisection tolerance asserted, never bounded |
| Q4 | **UNSOUND** | Batch-dependent schedule (crossing at n=40 yields 80, not D-102's 76); UNDISCLOSED ONE-WAY DOOR: loader recomputes expected_boundary for every chain entry and returns None for the WHOLE registry on any ancestor disagreement — overruling Q4 later retroactively bricks every issued artifact including the active one |
| Q5 | **UNSOUND** | D-102's MANDATORY re-derivation trigger converted to a closure-less deadlock (no definition of when an observation stops being "new"); science keeps running under a challenged screen while all subsequent triggers are unreachable; engine second-guesses the production writer's valid classifications |
| Q6 | **CONTRACT-BREAK** | D-109 R1.2 (omitted from packet) designs `abandoned` as one of four TERMINAL finalization states; `_noncontent_rows` raises unconditionally on it; R1.2's reservation-first pending receipt means any capture dying pre-bytes produces an abandoned row — the FIRST such row permanently bricks automatic successor issuance for the life of the immutable ledger. Fires on the designed-for overnight failure path. Also: unguarded KeyError on receipt-shape variation |
| Q7 | STRAIN | 14 failure modes collapse to bare None; no partial-chain degraded mode; carried as Q4 amplifier |
| Q8 | STRAIN | Strongest adverse reading (R1.4 second-store) tested and REJECTED; residual: self-asserted authority string; no cross-check against the head-pin file |
| Q9 | **CONTRACT-BREAK** | D-109 R1.4 (omitted): "NO claim evaluation may occur between ledger advancement and pin commit." Exhibit writes no head pin and creates a second, longer, unbarriered window (registry replaced → git commit); every consumer refuses indistinguishably from "no registry exists"; concrete one-night strand scenario; mirror image of the sequencing class D-116's cold gate HELD on |
| Q10 | STRAIN | The exception's narrowness is outsourced to U1's `is_governed_open_bracket_extension` — different unit, unexamined by the packet, currently under a fired escalation; a false-positive predicate admits WITHHELD observations (finalized_slots) into the trigger population feeding Q1 |
| Q11 | **CONTRACT-BREAK** | The "self-fit guard" comment sits on a MANDATORY-INCLUSION check (build refuses unless every trigger observation is carried into the successor corpus); D-102 pin 2's second conjunct ("never incorporated into a threshold that judges itself") implemented as its negation; artifact stamps `judge_under_prior_artifact_never_self_fit` — attesting a property the code does not enforce. AGGRAVATING: `successor_probe` is a HARDCODED LITERAL (`accepted_under_active_artifact`, empty triggers) never computed — fabricated attestation, the class this project has escalated on three occurrences |
| Q12 | NO-CASE | Honest: the register's own (packet-truncated) Disposition assigns U2 exactly this scope; residuals honestly labelled |

## Composition hazards no single question exposes

- **Night-killer (Q5 x Q12):** successor issues with a screen below the
  writer's stale hardcoded literal → overnight post-calibration lands
  between the two → writer finalizes it valid, appends immutably →
  morning probe re-judges it systematic → persistent refusal; the night
  is spent AND no successor can ever issue automatically again.
- **Coupling:** the packet instructs per-question rulings but Q1's
  corpus choice feeds the allowance rule: the exhibit generalizes D-117
  cl.1's binding literal `0.010818` to corpus-dependent
  `max(observed_drift_s, bracket_screen_s)`; NO question covers the
  allowance rule at all; n=2 corpora are accepted where t(0.995,1)≈63.66.

## Packet-quotation audit

D-102 and D-116 blocks byte-identical (difflib, zero differences). L4
bullet verbatim but TRUNCATED at the register's Disposition paragraph
("U2 covers L4's trigger probe") — the single most Q12-relevant sentence
— with adjacent L5 dropped. Line citations accurate (minor drift only).
**Structural defect:** the exhibit's own
`SUCCESSOR_DECISION_IDS = ("D-102","D-109","D-117","COLD-GATE-U2-PENDING")`
names its binding authorities; the packet quoted D-102/D-116 and
consigned D-109 and D-117 to unswept — D-109 self-describes as supplying
"the authority/universe rulings D-102 left silent" and its
R1.2/R1.4/R2.2/R2.5/R2.6/R2.8 are operative for seven of twelve
questions.

## Unswept-evidence attack (highest risk)

"U1's complete contract record was not substantively reviewed": Q10's
entire safety argument rests on a U1 predicate on a branch under a fired
escalation (foreign-replay class open; introduced zero-payload
auto-replay). Runner-up: NO TESTS WERE RUN by the assembly — the D-102
operative replay that legitimizes the exhibit was established by this
refutation, not by the assembly.

## Contamination disclosure (verbatim substance)

Environment contained: global + project CLAUDE.md, CLAUDE.local.md
(full rule-11 topology), auto-memory index; deliberate reads of D-109,
D-110..D-113, D-117, parts of D-118/D-103 (the D-109 omission is itself
a finding, but contamination relative to strict packet-only);
night-hardening FINDINGS-REGISTER.md (L4 source incl. L5 + Disposition);
git log on current main (exposed the U1 escalation — directly informed
Q10). Wrote no repository files (three scratch files outside the repo
for the quotation diff).
