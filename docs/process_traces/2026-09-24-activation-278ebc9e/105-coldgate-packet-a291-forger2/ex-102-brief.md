ROLE: FORGER SEAT (read-only adversary). Your first output line must list every file your harness auto-loaded into this session (or "none"). Do not call any other agent or model. Wall budget: 30 minutes. Write files only inside your current directory (scratch), never elsewhere.

WRITE_SCOPE: []

YOUR DIRECTORY holds a source snapshot of a Python project (package `joulewise/`), the contract `CONTRACT-v4.1.md`, and a runnable Python (`python3`, run from this directory so `import joulewise` works). Test files have been removed.

THE TARGET: `joulewise/scored_packer.py`. Its function `_seal(registration, roster, finalize=True)` is supposed to refuse any roster that violates the contract's ownership and formation rules — in particular INV-10 (block formation: parents are exactly the registered slices), INV-11 (item conservation, closed form in CONTRACT-v4.1.md), and INV-12 (parent relation). The contract's glossary defines parent, single, placement, live, voided, terminal.

CHARGE (verbatim): "compose a roster with forged ownership or formation that `_seal(registration, roster, finalize=True)` accepts".

Build legal starting rosters with the module's public entry points (`pack`, `requeue_overrun`, `verify_executed_roster`, `executed_status`) and whatever registration objects the code requires (read the code to construct them). Then mutate rosters by hand — any combination of edits (copy/revive/void/move blocks and placements, add/remove/retarget terminal refusals, flip flags, reorder lists, split/merge items) — refresh any derived or digest fields the seal checks if you can, and submit to `_seal(registration, roster, finalize=True)`. A candidate counts only if `_seal` ACCEPTS it and you can state, citing CONTRACT-v4.1.md clauses, which rule it violates.

OUTPUT: your final message: the auto-load line; then for each candidate you submitted (accepted or refused): (a) the complete Python constructor code (self-contained, runnable from this directory), (b) the `_seal` result (accepted, or the exception text), (c) your stated forgery rationale citing contract clauses. Include refused attempts too (briefly). If you find no accepted forgery in 30 minutes, say so plainly and list what you tried.
