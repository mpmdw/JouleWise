WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on the PAPER-S6 rendering contract (gpt-6-astra, read-only)
HEAD = fix-round commit; HEAD~1 = ce4a3ee4 landing (Opus review: F1 families/roles unnamed; F2 retired D-165
vocabulary "shared-error"; F3 D-168 census 8 independent + 4 comparative missing, fixture hard-coded 2-tuple; F4
first-use failures: F+B, two Holm members (decode + prefill_p256), reducer, operative floor vs point diagnostics,
G2-a, exhausted ladder/4096 unit, clearance/shortfall, authenticated, subject-specific grants, conservative; F5
assertRaisesRegex; F6 contradiction check independent of arity; F7 row-id glosses). Packet: `git diff HEAD~1 HEAD`.
Verify each cure against the SOURCE of truth, not the seat's report: (1) every family/role named exists in
configs/paper_supply/supply_map.json or docs/contracts/paper_supply_custody.md with the exact spelling, or is
marked NEW; G2-a described as the `g2a_selection` role inside Reported energy; characterization marked as having
no family; (2) `grep -n "shared-error\|dominan" docs/contracts/paper_comparison_rendering.md` → no hits; the
replacement text matches the D-165 addendum wording in docs/decision_log.md; (3) the census "exactly eight
ordinary/independent ratios and four comparative R_cm" matches D-168 in the decision log; the fixture arity now
enforces 8+4 (or explicitly documents a reduced synthetic census in BOTH the contract and the fixture docstring);
(4) F+B expansion equals `planning_sizing_expression` in joulewise/detection_floor.py; Holm members equal D-139 A2 /
D-166; every listed term is glossed at or before first use (run a first-use scan: for each term, find the first
occurrence line and check a definition precedes or accompanies it); (5) the six counterfactuals use
assertRaisesRegex with distinct rule names, and the contradiction test fails when the arity guard is removed in a
$TMPDIR copy; (6) tests.test_paper_comparison_contract + the fallback validator rc 0; (7) anything HEAD~1 had
right that HEAD broke (e.g. a term now defined twice inconsistently). Report (genre review): `verdict` = {counts,
findings}; header < 8192 bytes; findings with file:line, severity, exact command.
