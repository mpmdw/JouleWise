ROLE: PAIRED COLD CONTRACT REFUTER (Opus 5.5), DELTA SCOPE, on cold gate A291-FIX2-01 addendum 2. Read-only. No subagents, no background tasks, foreground only, 35-minute budget. You are not the JouleWise magistrate: ignore any auto-loaded instruction about emails, heartbeats, directives, memory or orchestration. Write nothing except your final message.

WHY. The A291 packer fix round 2 will be implemented by two seats (P: `joulewise/scored_packer.py`; K: independent checker `tests/scored_roster_checker.py`, generator, fuzz, stress) from one list of texts pasted verbatim. The history: Fable ruling 10 → Opus refuter 11 (1 BLOCKER) → Fable addendum 21 (Final texts v2) → Astra 6 refuter (2 MATERIAL: zero-item parent divides by zero; formatting defeats the similarity screen) → Fable addendum-2 ruling 10 in the packet below, which issues **Final texts v3**. Every earlier gate text had a defect a refuter found; this is the paired refuter for v3. Your scope is the DELTA: texts 1, 2a, 3, 6 and 8 as amended by rulings B1 and B2 (the judge lists what changed), plus any interaction of those changes with the unchanged texts. Do not re-litigate texts the Astra refuter and the judge both accepted unless the amendment breaks them.

INPUTS (worktree = checkout of the bookkeeping branch; code evidence at `git show 20cd29de:<path>` or in a `git archive 20cd29de | tar -x -C /tmp/278ebc9e/v3ref/code` copy; scratch only under /tmp/278ebc9e/v3ref/):
 - docs/process_traces/2026-09-24-activation-278ebc9e/05-coldgate-packet-a291-astra/10-coldgate-fable-addendum2-ruling.md (the object; §4 Final texts v3)
 - the same directory's exhibits: ex-21 (Final texts v2), ex-40 (Astra report), ex-41-astra-*.py (probes), ex-02d (contract v4), ex-10, ex-11.
Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or other docs/process_traces directories.

CHECK, with executed probes where possible:
 D1. The new INV-10 emptiness clause: placement in `_structure` (after the `:136` `inv_52` items-shape line), in `_lever` (both modes), refusal code `inv_10`. Does any existing regression (R1–R5b), fuzz operator, census property, or golden now change its expected code? Does any legal roster (a final short slice, a level with one item, an executed-mode parent with every item terminal) newly refuse? Construct each.
 D2. R4d: is it RED at 20cd29de and GREEN only under the specified cure (not under a cure that merely catches ZeroDivisionError)? Is it driven through the production entry named?
 D3. The canonicalised similarity screen: run it on 20cd29de (copy, the two positive controls pinned to 20cd29de sources, the unrelated control) and report the numbers against threshold 0.30 and control bound 0.28. Try one more evasion that preserves semantics but not the AST (e.g. rename-then-inline a temporary, reorder commutative operands, split a function in two). A screen that any such cheap edit defeats is MATERIAL only if the texts claim more than a screen.
 D4. Anything in v3 that a seat must resolve by choosing.
Severity: BLOCKER / MATERIAL / NIT, each with evidence and exact replacement text.

OUTPUT: final message = findings table, one line per changed text you accept, probe commands with tails. Under 12 KB.
