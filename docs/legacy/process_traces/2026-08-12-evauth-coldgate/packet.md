# COLD-GATE PACKET — WO-EVIDENCE-AUTHOR-01 second fix round on defect B1 (injection surface)

Mechanically assembled by the T6 magistrate; the sitting rules BEFORE round 2 executes. Mandatory trigger: second fix round on the same defect (rule 11).

## The defect's history
1. Original implementation exposed `_suite_runner` as a PUBLIC kwarg on the authoring API — lens A executed a probe minting PASS facts with tests_run=777 without executing anything (lens report: evauth-lensA-out.md, finding B1).
2. Fix round 1 removed the kwarg and moved execution to an isolated subprocess (B2 fix, delta-verified sound). BUT the delta re-audit (evauth-delta-out.md, finding B1) executed a NEW probe: `DERIVERS` is a module-level MUTABLE exported dict controlling both authoring paths; replacing `DERIVERS["THREE_WINDOW_REGRESSION"]` mints forged PASS evidence through the untouched public API. The fix round's own sentinel tests mutate this same public mapping (normalizing the surface).
3. The delta's prescribed remedy: private immutable dispatch (`_DERIVERS` behind MappingProxyType or equivalent), removed from `__all__`, any replaceable seam strictly private to tests; plus N1 (deterministic child env) and N2 (process-group descendant cleanup).

## The question before the sitting
Q1: Is the prescribed remedy the TERMINATING design for the injection class — or is the class structural (i.e., in Python, ANY module attribute is patchable, so "private immutable dispatch" only raises the bar; the real question is what the enforcement boundary should be)? Rule on: (a) adopt the prescribed remedy as sufficient, with the explicit boundary statement that in-process Python attribute substitution is OUTSIDE the threat model (the tool authors evidence on the magistrate's own machine; the adversary class is accidental/操作 misuse and drift, not a hostile in-process attacker), and the mandated shape is: no PUBLIC seam, tests patch a name-mangled/underscore-private seam, a regression asserting DERIVERS is absent from the public namespace; or (b) mandate a stronger shape (e.g. subprocess-boundary authoring where the CLI is the only entry and the module is not importable-with-mutation for authoring purposes), with its cost; or (c) a different terminating design.
Q2: Are N1/N2 (env determinism, process-group cleanup) mandatory in the same round or separable?
Q3: Any condition the round must additionally satisfy for the freeze receipts authored TONIGHT to be trustworthy?

## Primary artifacts (read directly)
- Lens A: /private/tmp/claude-501/-Users-edr-code-JouleWise/2cc5ce62-9e44-4ab2-a470-a38d9caf2826/scratchpad/evauth-lensA-out.md
- Lens B: same dir, evauth-lensB-out.md
- Fix-round report: evauth-fix-out.md
- Delta re-audit: evauth-delta-out.md
- The code (uncommitted worktree): /private/tmp/claude-501/-Users-edr-code-JouleWise/2cc5ce62-9e44-4ab2-a470-a38d9caf2826/scratchpad/wtEVAUTH/joulewise/arm_readiness_evidence.py (+ scripts/author_arm_readiness_evidence.py, tests/test_arm_readiness_evidence_author.py)
- Authority: D-134 (decision log, ten clauses — cl.6 derive-never-enter); D-118 invariants by reference.

## Context the sitting needs
The tool authors the twelve FREEZE-row evidence receipts (X-1 gap). The pack freeze tonight gates on it. The receipts' consumers re-validate everything (validate_evidence_receipt + predicate derivation at freeze AND arm; boot-session fence; sha bindings) — the author is one layer of a defense-in-depth stack, not the sole gate.
