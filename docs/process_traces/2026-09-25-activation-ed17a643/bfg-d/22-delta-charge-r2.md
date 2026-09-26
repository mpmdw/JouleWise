# BFG-D fix round 2 delta re-audit charge: `faf0ea01` → `e02350ff` (rounds 6 and 6b)

**Rulings and contracts.**
- The ruling is BFG-D-PARSER-ESC-01, `15-parser-esc-ruling-source.md`: §4 is the grammar, §6 is R2-1..R2-7.
- The contracts are `18-fix-contract-r6.md` (R2-1..R2-11) and `20-fix-contract-r6b.md` (C-1..C-3).
- The seat reports are `19-fix-seat-report-r6.md` and `21-seat-report-r6b.md`. Verify their claims; do not trust them.

**Lead evidence at `e02350ff`.** The issuer, validate_powermetrics_fiducial, write_derivation_night_inputs, revision_five_b_readers, battery_float and battery_float_sweep modules ran 221 tests, all OK. That run includes the live identity test.

**R2-6 (binding on you).** Run the ruling §4 corpus. Also write at least **ten fresh structural mutations of your own**: malformed or structurally wrong ioreg outputs that are not in `tests/battery_float_corpus.py`. Drive each one through all four sites: `parse`/`observe`, `night_gate.evaluate_night`, `evaluate_dynamic_hard`, and `validate_window`. Any structural false GO or pass is a BLOCKER. Under the stop rule it goes to council, not to another round.

**Also check, with executed evidence:**
1. Each of R2-1..R2-11 and C-1..C-3 is closed as dictated, and its test fails when the fix is reverted. Mutate in /tmp copies only, covering at least R2-1, R2-2, R2-3, R2-9, R2-10, R2-11 and C-2.
2. The seat's F1 moved the tool-mechanics tests to a hypothetical epoch 25G99. Confirm the assertions are unchanged and that this is the right domain.
3. Does any fix introduce a new defect, bypass or regression? **Run every test module that imports a changed fixture builder or a changed production file.** List them with `git diff --name-only faf0ea01 e02350ff` plus grep. The last round missed a regression because it skipped this step.
4. Same-signature: any remaining reader of B, or any verdict consumer, without its gate. Re-grep, and do not rely on the seat's sweep table.
5. The pin proof must be empty.

**Constraints.**
- Read-only in the repository; /tmp is fine.
- No full discovery.
- No launchctl, powermetrics, sudo, installer or model inference. ioreg is allowed, read-only.
- One foreground session, with no subagents.

**Verdict.** MERGE or FIX-FIRST, with every finding tiered BLOCKER / MATERIAL / NIT.
