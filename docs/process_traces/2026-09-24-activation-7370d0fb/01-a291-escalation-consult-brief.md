ROLE: DESIGN CONSULT (read-only) for JouleWise lane A291, the scored-night packer. You are one of two blind seats; you will not see the other seat's answer, and a cold Fable gate rules afterwards on the plan the magistrate synthesises. You have explicit licence to disagree with every candidate below, including the framing. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT AND FENCES.
Linked worktree (yours): detached at `20cd29de` on the A291 branch. Read-only in the repository; scratch files and probe scripts only under /tmp. Never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise.
Code under review: `joulewise/scored_packer.py` (the packer: `pack`, `requeue_overrun`, `_seal`, `_derived`, `_live`, `_TRUSTED_OUTPUTS`), `joulewise/scored_registration.py`, and the independently written oracle `joulewise/scored_roster_checker.py` (committed before the packer existed and fixed once after an Opus lens). Tests: `tests/test_scored_*.py`.
Contract: `docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md` in your worktree (§1.2 derived quantities, §3 normative behaviour, §4 executed values, §5 invariant matrix, §6 checker interface), with residual rulings 25, 29, 31 in the same directory.
Evidence of the problem: records 37 (Opus lens on the checker), 44 (checker delta), 45/46 (fix round 1 brief and report), 50 (delta re-audit of fix round 1) in that same directory.

1. WHY YOU ARE BEING ASKED (the escalation).
The project's standing rule: two consecutive rounds failing with the SAME defect signature means the next spend is a design consult, not a third fix round. That trigger has fired. The signature is: "a derived quantity misreads which placements or parents count." Instances so far:
 (a) lens 37 B1: the checker's planned lever dropped split parents that had some terminal singles, contrary to contract RD-4; the implementer I1 then matched the wrong oracle.
 (b) lens 37 B2: the checker read a voided first placement instead of the live one.
 (c) delta 50 S1: the planned lever decides whether to compute from NON-TERMINAL COUNTS but takes its positions from an independently built `pos` list; on a malformed roster the two populations disagree and the code raises a raw ZeroDivisionError at requeue entry instead of a typed refusal.
 (d) delta 50 B1 (BLOCKER): `_seal(..., finalize=True)` adds ANY roster it seals to `_TRUSTED_OUTPUTS`, and `requeue_overrun` skips the full replay for cached rosters. A caller who mutates a returned roster in place, clears its sha256 and re-seals gets a roster that the checker rejects (INV-11, INV-36: two live placements for one block) past requeue entry. The seal itself does not enforce the invariants the checker enforces.
 (e) delta 50 S2: the stress generator's two seeds give identical counts on 10 of 11 edges; the seed barely drives the shapes.

2. CANDIDATE STRUCTURAL CURES (the magistrate's first guesses; judge them, do not assume them):
 C1. ONE INVARIANT TABLE: a single declarative table of the §5 invariants, which the seal enforces on every roster it emits or accepts, and which the independently written checker mirrors row for row (without importing the packer's implementation of it, so the oracle stays independent).
 C2. ONE POPULATION DEFINITION PER DERIVED QUANTITY: each derived value (planned lever, executed lever, spreads, counts) computed by one function from one named parent-population definition, so the guard and the arithmetic cannot read different populations.
 C3. NO TRUSTED-OUTPUT CACHE: requeue entry always runs the full seal-plus-replay; or, if the replay cost matters, cache trust bound to provenance a caller cannot forge (for example an object identity plus a digest captured at emission, never re-sealable).
 C4. A SEED-DRIVEN STRESS GENERATOR whose seed chooses report shapes, stages, boundary durations and geometry, with per-seed variation asserted.

3. TASKS (execute probes where a claim is checkable; do not just read):
 Q1. Is the signature real and structural, or four unrelated bugs? Name the root cause in one paragraph.
 Q2. For each of C1–C4: ADOPT / ADOPT WITH CHANGES / REJECT, with reasons. If C1 is adopted, say exactly how the checker stays an independent oracle while "mirroring" the table (shared row IDs and texts only? shared code? neither?).
 Q3. What does C3 cost? Measure the replay cost at requeue entry on a realistic roster (the stress test's sizes) with a /tmp probe, and state whether dropping the cache is affordable.
 Q4. Any cure the candidates miss. In particular: should `_seal` stay callable with `finalize=True` by callers at all; should `_live` refuse (typed) rather than silently pick one of two live placements; should every malformed-roster exception inside derived computation be converted to a typed refusal at one boundary?
 Q5. The fix-round-2 PLAN you recommend: an ordered list of changes (files, functions), the defect-shaped regressions each change must carry (name the counterfactual input and the production call site each regression drives), and what the checker role vs the packer role each owns. Keep it implementable by one Sol seat in one round.
 Q6. Risks: what in your plan could reintroduce the signature, and how the plan's own tests would catch it.

4. ACCEPTANCE. Genre triage (design consult). Body under about 250 lines; JSON header under 8 KB. Cite file:line for every claim about the code and paste executed probe output for Q3 and any other checkable claim. End your turn only when Q1–Q6 are answered.
