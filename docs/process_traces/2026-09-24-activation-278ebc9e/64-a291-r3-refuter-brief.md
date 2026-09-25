ROLE: PAIRED CONTRACT REFUTER (Astra 6, cross-family) on cold gate A291-ESC2-01's "Final texts A291-R3". Read-only, with executed probes. Do not call Claude or any other agent.

WRITE_SCOPE: []

WHY. These texts will be pasted verbatim into two implementation briefs: seat K (independent checker, composed generator, seal-level oracle) and seat P (packer ownership view). Every earlier gate text in this lane had a defect that a refuter found. Your job is to find what is WRONG, VACUOUS, CONTRADICTORY, UNIMPLEMENTABLE or UNDER-SPECIFIED before any code: a regression that cannot fire, two readings of one rule, a coverage row the seal cannot evaluate before arithmetic, an AST rule that forbids something the texts also require, or a forger-seat or stop rule that cannot be operated.
INPUTS (your worktree /Users/edr/code/wt-278ebc9e-r3ref is a detached checkout of the integration head `0fa4e6e3`; scratch only under /tmp/278ebc9e/r3ref/; never launchctl, sudo, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise):
 - THE OBJECT: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/63-a291-final-texts-r3.md (§4 of the ruling), and the whole ruling /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/48-coldgate-packet-a291-esc2/20-coldgate-fable-esc2-ruling.md.
 - The packet it ruled on: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/48-coldgate-packet-a291-esc2/ (the synthesis ex-47, the consults ex-42/43/45/46, the probes ex-42-probe-*.py, the contract ex-02d, Final texts v4 ex-14).
CHECK (each: verdict, executed evidence, replacement text if you object):
 R1. The closed INV-11 text: execute it (as a scratch predicate) against AUD-1, B1, B2, probe-D, the legal contrast, and the legal corpus from `tests/scored_case_generator.py` `generate_case` over at least 4 seeds × 12 cases. Any legal roster refused, or any forgery accepted, is a BLOCKER.
 R2. The row→boundary map: can every row assigned to the seal actually be evaluated from the roster before derived arithmetic, without replay? Is any row missing?
 R3. The AST confinement rule versus the texts' own requirements (type rows, `_parent_facts`, the digest step): is there a contradiction?
 R4. Seats, order and independence: any file both seats must write, any P witness that depends on K's files, any RED-per-target requirement that is unfalsifiable.
 R5. The gate before merge, the forger seat and the stop rule: are they operable exactly as written (who, what they see, what counts as success, what happens next)?
 R6. Anything else.
Severity: BLOCKER / MATERIAL / NIT.
OUTPUT: findings table, one line per accepted text, probe commands with tails.
