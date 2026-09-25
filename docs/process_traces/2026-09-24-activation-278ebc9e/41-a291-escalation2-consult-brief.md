ROLE: BLIND CONSULT SEAT on a JouleWise escalation (lane A291, the scored-roster packer). Read-only. You have explicit licence to disagree with every prior ruling. Do not call any other agent or model.

WRITE_SCOPE: []

THE ESCALATION. The packer `joulewise/scored_packer.py` seals a roster (which item blocks run in which measurement envelope, with requeue history). Its seal must refuse any roster that violates the contract. Fix round 1 was escalated because the seal accepted a forged roster with two live placements for one block. Fix round 2 was then built from four cold-gated rounds of texts (Final texts v4). It added a precondition set in `_structure` and a checked-derived boundary, and an independently written, item-centric checker agrees on every legal roster. The delta re-audit of round 2 now finds the SAME SIGNATURE again. A composed forgery with TWO DISTINCT live blocks holding L1I0 and L1I1 passes `_structure`, `_seal(finalize=True)` and verification-mode `_seal`. The reason is that the packer's INV-11 row uses an item-specific, block-id-specific terminal test instead of the contract's all-items-terminal block predicate. The independent checker reports INV-11 on it, and replay later rejects it with `inv_38`. Two consecutive rounds have now failed with the same signature: the seal is still accepting forged ownership. The project's rule says this is evidence of a STRUCTURAL problem. The next spend is this consult, not another patch.

INPUTS (your worktree is a detached checkout of the integration head `0fa4e6e3`; scratch only under /tmp/278ebc9e/esc2-<seat>/; never launchctl, sudo, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise):
 - The re-audit: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/39b-a291-delta-reaudit-report.md (AUD-1 witness and cure).
 - Final texts v4: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/14-a291-final-texts-v4.md (text 3 is the INV-11 row as ruled).
 - The contract v4: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/ex-02d-contract-v4.md (INV-09..12 near :455-476).
 - The round-1 escalation consults: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/02-a291-consult-sol.md and 03-a291-consult-opus.md.
 - Code: joulewise/scored_packer.py (seal, `_structure`, INV-11 row near :234), tests/scored_roster_checker.py (the independent checker's INV-11 row), tests/test_scored_packer_fuzz.py.

ANSWER:
 Q1. Root cause, structurally: why do per-row predicates in the packer keep diverging from the contract's ownership invariants? Is it the texts (Final text 3 as ruled), the implementation, or the architecture (the seal re-states invariants in its own data model)? Verify by reading text 3 against the contract and the code; say whether text 3 itself mis-states INV-11.
 Q2. Candidate structural cures, each with cost and what it guarantees. Include at least these:
   (a) the literal contract predicate in the packer (Astra's cure);
   (b) a single ownership table built once from the roster, with every ownership invariant (INV-10/11/12/17/52) evaluated on it;
   (c) the seal calls the independent checker as a production dependency (moved out of tests/). Weigh the independence cost: the checker stops being an oracle for the packer.
   (d) a differential guard in production: the seal refuses if the packer's facts and a second, item-centric recomputation disagree;
   (e) your own.
 Q3. The regression and fuzz design that would have caught AUD-1. Why didn't the ten-operator fuzz compose two edits? Specify a composed-operator or property-based generator for ownership forgeries.
 Q4. Your recommended plan for fix round 3, as executable text: the seats, the WRITE_SCOPEs, the ordering, and the gate before merge.
OUTPUT: final message under ~10 KB, headed with your seat name, with file:line for every code claim and executed probes where they decide.
