ROLE: CROSS-FAMILY CONTRACT REFUTER (Astra 6) for JouleWise lane A291 (the scored-roster packer), fix round 2. Read-only review. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. WHY YOU ARE HERE. Under D-184 (Ed, 2026-09-24) important science gets all four model families. The A291 fix-round-2 plan was ruled by a cold Fable 5.1 gate (ruling 10), refuted by an Opus 5.5 contract refuter (11, one BLOCKER), and settled by a cold Fable addendum (21) whose §4 "Final texts v2" will be pasted VERBATIM into two implementation briefs: seat P (Sol, packer `joulewise/scored_packer.py`) and seat K (Opus, an independently re-derived checker `tests/scored_roster_checker.py`, a generator, a mutation fuzz and a stress test). The Astra seat was dropped from that consult only because it predated D-184. You are that seat. Your job is to find what is WRONG, VACUOUS, CONTRADICTORY, UNIMPLEMENTABLE or UNDER-SPECIFIED in Final texts v2 before any code is written — the same class of defect the Opus refuter found three gates running (a regression that can never fire; two readings of one invariant; a handler list that differs between two texts; a similarity ratio that did not separate copied from independent code).

1. INPUTS (read-only; worktree /Users/edr/code/wt-278ebc9e-astra-ref is a detached checkout of `20cd29de`, the code the texts apply to; probes may run there or under /tmp only):
 - THE OBJECT UNDER REVIEW: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/20-addendum/21-coldgate-fable-addendum-ruling.md, §4 Final texts v2 (read §0–§3 for context).
 - Its history: same directory ../10-coldgate-fable-ruling.md (ruling 10), ../11-opus-contract-refuter.md (refuter 11), ../ (packet exhibits), and ../../06-a291-fix2-synthesis-and-plan.md, ../../02-a291-consult-sol.md, ../../03-a291-consult-opus.md.
 - The contract: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md.
 - Code at 20cd29de: joulewise/scored_packer.py, tests/scored_roster_checker.py and their tests.

2. WHAT TO CHECK (each item: verdict, evidence with file:line or executed probe output, and a proposed replacement text if you object):
 Q1. For every regression Rn and fuzz operator in Final texts v2: construct (or execute against 20cd29de) the input it names and show that the named invariant CAN fire on it after the fix and DOES NOT fire before where the text says it is RED at 20cd29de. A regression that cannot fire is a BLOCKER.
 Q2. Every invariant id (inv_*/INV-*) cited: is there exactly one reading consistent with the contract v4? Two readings = MATERIAL.
 Q3. P/K sequencing and WRITE_SCOPEs: any file both seats must write, any P witness that depends on K's not-yet-written files, any order that deadlocks.
 Q4. Checker independence: will the mechanical AST rule and the pairwise similarity check (with control) actually detect a transcribed `_derived`? Try it: compute the stated metric on the 20cd29de packer vs checker derived code and on one unrelated pair, and report the numbers.
 Q5. Population semantics (ADDENDUM A291-POP-1, "gate ⇒ full indices", the executed spread's five-envelope clause, the relation check "regardless of lever nullness"): does any text allow a derived quantity to mix two parent populations — the same signature that triggered this escalation? That is a BLOCKER.
 Q6. Anything else that would let seat P or K satisfy the letter of the texts and still ship the defect class this round exists to cure (forged roster with two live placements accepted by the seal; trusted-output cache letting a re-finalized roster skip replay; derived values from two populations).
 Severity: BLOCKER (text as written guarantees a wrong implementation or a vacuous gate), MATERIAL (ambiguity a competent implementer could resolve wrongly), NIT. Do not restate agreement at length; one line per text you accept.

3. FENCES: never launchctl, sudo, networksetup, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents; never import or execute from /Users/edr/code/JouleWise. Write nothing in any repository. Scratch only under /tmp/278ebc9e/astra-ref/.

4. OUTPUT: your final message is the report: a table of findings (id, severity, Final-text number, claim, evidence, replacement text), then one line per accepted text, then the probe commands you executed with their tails.
