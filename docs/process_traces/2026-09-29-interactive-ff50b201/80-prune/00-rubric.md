# Overengineering prune sweep — shared rubric (session ff50b201, 2026-09-29)

Owner's question (Ed, verbatim): "if its as easy as turning off the network clock how much else have you overengineered?" Context: network-time enforcement absorbed 4+ fix rounds on an automatic restore-ON and its capture-absence proof, when the owner's answer was one command (turn it off on the dedicated Mac and leave it off). The owner's standing statements: gates exist "solely to prevent death loops of useless investigation or reasoning and infinite token burn"; "all rules are in service of the science"; the orchestration exists for "preventing bad science".

For each mechanism, record:
1. **What it is**, in one plain sentence (file:line or doc path).
2. **Which number it protects**: name the measured or published quantity (joules per request, calibration S/C, a paper table value …) and the concrete way that number would be wrong without it. "None / process hygiene only" is a valid answer.
3. **What it has actually caught**: cite record items / commits where it caught a real defect in a number or its custody. Count separately the catches that were defects in the enforcement mechanism itself.
4. **What it has cost**: fix rounds, cold gates, seats, PR delays attributable to it (cite records), and ongoing cost (every window, every PR).
5. **A cheaper equivalent**, if one exists (e.g. "turn the setting off" vs "prove nothing runs before turning it on"), and what would be lost.
6. **Verdict**: KEEP (load-bearing for a number), THIN (keep the core, cut named parts), DELETE (protects no number, or a cheaper control covers it), with one deciding reason.
Rank the THIN/DELETE items by (cost saved) × (confidence it protects no number). Flag any DELETE that would touch a claim path as needing a cold Fable check before it lands. Read-only: modify nothing.
