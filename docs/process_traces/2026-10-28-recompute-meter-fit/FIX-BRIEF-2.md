BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "RC-CMP-5: structural fix round for the comparator's second-round delta reviews (Sol REJECT, Opus ACCEPT_WITH_FIXES)",
 "OBJECTIVE": "Replace case-by-case coverage, binding and union logic with three structural rules, so that the false-agreement class found in two review rounds cannot recur, and close the five round-2 findings as instances.",
 "AUTHORITY": [
   "RUN_STATE.md items 86, 87, 91 (lead ruling: a defect class seen twice gets a structural rule, contingency plan section 4 item 1)",
   "review/2026-10-28-rc-cmp-sol-rev-2 .codex-report/RC-CMP-SOL-REV-2.md (e1dfdb32f) and .codex-report/rc-cmp-sol-rev-2/probe_new_paths.py",
   "review/2026-10-28-rc-cmp-opus-rev-2 .codex-report/RC-CMP-OPUS-REV-2.md (f8e3b1f00) and .codex-report/rc-cmp-opus-rev-2/probe_delta.py",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "scripts/compare_b5_recompute.py",
   "tests/independent_recompute/**",
   ".codex-report/RC-CMP-5.md"],
 "BASE_HEAD": "tip of lane/2026-10-27-recompute-comparator (e5ccf720b at writing)",
 "ACCEPTANCE": [
   "S1 (default deny for numbers) a step-11 leaf is numeric-class if its L9 value is a number, null, or was read from a nonfinite token (the nonfinite flag records the leaf path); only a leaf whose L9 value is a string or bool may match an uncovered: rule; a numeric-class leaf must bind to a compared AGREE row or be named by an uncovered-by-name rule and listed; any nonfinite value from a step-11 source refuses (exit 2) with a structure code; closes Sol 1 and Opus N1",
   "S2 (independent binding) a leaf's comparison key is built only from its structural position (path components and enclosing container ids), never from a value the same leaf or line asserts about itself; every id that routes a binding (condition_family_id, model, pack, contrast_id, cell_id, central band pack) is itself compared exact against the recompute's value for that row; the arm-gate floor binds to the condition the recompute assigns to that arm; closes Sol 2 and Opus N3 (the central band pack is compared, and a band on one side only is DISAGREE)",
   "S3 (one union, one key space) every family compares two keyed collections through one shared helper that takes the union of keys and records one-sided keys as DISAGREE missing_or_null; row keys are globally unique: building two rows with the same (family, key) is a structure refusal; ratio rows get their own key prefix; an AST test asserts no family function iterates over one side's collection outside the helper; closes Sol 3 and Opus N2",
   "S4 every probe in both round-2 reviews and in both round-1 reviews is a regression test that fails at e5ccf720b where it found a defect (record the counterfactual) and passes after; tests/independent_recompute passes; no file outside WRITE_SCOPE changed; no import of joulewise.b5_analysis or joulewise.external"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .",
   "both reviews' probe scripts (extract with git archive origin/review/<branch> .codex-report/<dir> | tar x) print the failing outcome at the fixed head"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# RC-CMP-5 brief

**Why structural.** Two review rounds have each found new ways for the comparator to report agreement while L9 and
the recompute differ: value-only coverage, one-sided keys, then nonfinite-to-null, self-routing ids, duplicate keys
and one more one-sided loop. Each round fixed instances. This round fixes the class: numbers are denied by default
(S1), bindings never trust the leaf they check (S2), and there is one union helper and one key space (S3).

**Not in this round.** Over-refusal on real shapes (equal member sets, multi-source floor cells) waits for RC-CMP-4,
the full-size synthetic rerun now running on `e5ccf720b` (branch `report/2026-10-28-rc-cmp-4`). Do not loosen any
check for it here. Do not touch `scripts/independent_recompute_b5.py` or the bars.

**Rules.** Synthetic data only; never open real block-5/6/BYTES data. No bar is widened. Push only to
`lane/2026-10-27-recompute-comparator`; no force push, no merge to main, no PR. Push the report after each
milestone. After this job the lead sends the fixed head to both reviewers for one more delta check.

**Report.** `.codex-report/RC-CMP-5.md`: SUMMARY, the S1-S4 table with evidence and counterfactuals, FILES CHANGED,
DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
