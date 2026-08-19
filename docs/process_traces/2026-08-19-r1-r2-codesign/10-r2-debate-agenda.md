# R2 DEBATE — ROUND 1 AGENDA (magistrate-set, bounded)

Both seats' designs are in and CONVERGED on the composite shape. Respond ONLY
to the numbered conflicts below (plus at most one explicitly-flagged
OFF-AGENDA blocker in the other design). Verdict per item: CONCEDE / MAINTAIN
(with evidence, executed where possible) / AMEND (with amended text).
Executed evidence beats argued plausibility.

## Agreed (no debate; recorded for the ruling)
- COMPOSITE design: generation-indexed screen/rule resolution (code layer,
  extending _D102_GENERATION_DERIVATIONS) PLUS a new _v3 pack family
  (artifact layer). Neither alone suffices. Flat migration stays refuted.
- _v2 packs and freeze-0002 receipts are immutable history; never regenerated
  or re-minted. Parked step 6 is AMENDED: freeze-0003 mints on the _v3 roots
  at the measurement checkout (ordinal = predecessor+1 per arm_readiness.py
  lifecycle), not "freeze-0002 re-mints".
- _ACCEPTANCE_SELECTION does not move.
- One atomic transaction; kernel + schema + generators + goldens + evidence
  re-author + freezes + doc pins together; canonical FULL GREEN exit gate.
- The evidence-author acceptance copy-list gains r3+r4 INSIDE the transaction
  (necessity, not incidental).
- "R1" naming collision (capture ruling vs arm_readiness R1 row registry) is
  disambiguated in the ruling text.

## Conflicts to resolve

1. RESOLVER SOURCING. terra F2: derive mint policy from the supplied
   acceptance's own authenticated ratified_operatives (artifact-sourced,
   registry-authenticated). opus G5 (EXECUTED): artifact-sourcing breaks the
   historical replay fixtures, which pass stub acceptance mappings with no
   decimal_derivation (tests/test_floor_mint_estimator.py:38-42) — registry
   sourcing keeps 37/37, is more fail-closed on unregistered ids, and cannot
   diverge from an authenticated artifact (calibration_bracketing.py:550-559).
   terra: verify and concede, or refute with executed evidence.

2. TOOLING. terra F4: new bespoke mint-policy derivation command + new
   deterministic v3-family builder + new family verifier. opus (EXECUTED): the
   committed _v2 generators already emit a complete _v3 tree + extraction spec
   via --pack-id/--family-suffix (run to a temp root, 100 science configs,
   write-boundary guards intact); --check / --check
   --preserve-current-frozen-bytes are the verifiers; the only new code is the
   ~15-line resolver + a no-copied-scalar guard test; a tracked golden
   regenerator is explicitly barred by the goldens block's own comment.
   Decide what NEW tooling (if any) survives.

3. DEFAULT_ACCEPTANCE_BOUND_SHA256. terra F3 row 1: "fix … to r4's digest or
   an r4 alias". opus H2 (EXECUTED): the digest is the genesis-fixture
   authentication value with two live call sites (calibration_bracketing.py
   :629,:722) and a live test pin; changing its VALUE breaks genesis-fixture
   authentication; correct fix is RENAME-ONLY (e.g.
   GENESIS_FIXTURE_ACCEPTANCE_SHA256). terra: verify and rule yourself.

4. ACCEPTANCE BINDING UNDER THE R1 OUTCOME (cross-ruling seam; both seats
   designed blind to it). The R1 debate has converged on: the production
   capture flip moves an r4-pinned estimator source and REQUIRES a
   science-neutral D-079 r5 reissue in the same commit as the flip, inside
   this same parked transaction. Both R2 designs bind the _v3 family to r4.
   State precisely: (a) what in your design must rebind to r5 (generator
   SUCCESSOR_ACCEPTANCE constants, registry rows, resolver entries, copy-list,
   goldens, spec enums) and what is untouched; (b) the cheapest safe
   sequencing of R1-flip+r5 vs R2 kernel/goldens vs _v3 emission so no step
   is done twice; (c) whether anything in your design makes the r5 reissue
   harder (it must not).

Do NOT redesign agreed ground. Do NOT re-open R1 substance beyond item 4's
sequencing facts.
