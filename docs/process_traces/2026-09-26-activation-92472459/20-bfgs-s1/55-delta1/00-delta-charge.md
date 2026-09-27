# BFG-S S1 delta re-audit of the fix round: `24b79db3..b859317c`

**Candidate.** `feat/2026-09-26-bfgs-s1-bundles` @ `b859317c`. Read-only worktree `/Users/edr/code/JouleWise-wt-s1cg-92472459` (detached @ `b859317c`). Delta: `git diff 24b79db3 b859317c`.

**What the fix round was asked to do:** implement amendments 36, 37, 39, 40, 41, 42, 43 exactly as restated in §4 of `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/40-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md` (brief: `20-bfgs-s1/50-fix1/10-fix-brief.txt`; report: `50-fix1/11-seat-report.md`; verbatim transcript: `50-fix1/bfgs-s1-fix-verbatim-report.md`).

**Questions.**
1. Does each amendment land exactly, no more and no less, pinned by a test that dies under the named counterfactual (run the mutant)?
2. **Did the fix round introduce a defect?** In particular: can the rebuilt 69-entry historical set admit a bundle that no committed artifact names as historical (a prospective bundle masquerading as historical), or admit by a digest a live run could collide with? Is amendment 39's tree-digest fold computed from the bundle's own bytes, and can a modified RPT001 bundle still pass? Does amendment 42's typed refusal ever convert a `CustodyFailure` into a status, or drop a member? Does amendment 43's span stage change any energy, stamp difference or `b_fiducial_s`? Did amendment 36's four rows widen the guard beyond those four exact calls?
3. **Same-signature statement:** is any finding the same defect class as a round-1 finding (custody turned into a status; the reader overreaching a ruled binding; a set enumeration miss)? Yes/no per class.

**Standing constraints:** `joulewise/battery_float.py`, `reduce.py`, `bundle.py`, and FT §E's excluded list byte-identical to base `1417c0c4`; custody is never a status; verdicts only through S0 factories.

**Output.** Findings tiered BLOCKER / SHOULD-FIX / NIT with executed evidence (command + exact tail), the production call site, and a closure shape; the same-signature statement. Edit no repository file; scratch under `/tmp`.
