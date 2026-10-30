BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "RC-CMP-3: fix round for the two executing reviews of the recompute comparator (Sol REJECT, Opus ACCEPT_WITH_FIXES)",
 "OBJECTIVE": "Close every false-agreement path and the meter-fit difference the reviews found, so the comparator can bind block 5's release.",
 "AUTHORITY": [
   "RUN_STATE.md items 83, 84, 86, 87 (lead dispositions below)",
   "review/2026-10-28-rc-cmp-sol-rev .codex-report/RC-CMP-SOL-REV.md (bb62782d0) and probes .codex-report/rc-cmp-sol-rev/",
   "review/2026-10-28-rc-cmp-opus-rev .codex-report/RC-CMP-OPUS-REV.md (9df560b7b) and probes .codex-report/rc-cmp-opus-rev/",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "scripts/independent_recompute_b5.py",
   "scripts/compare_b5_recompute.py",
   "tests/independent_recompute/**",
   "configs/analysis/b5/recompute_bars.json",
   ".codex-report/RC-CMP-3.md"],
 "BASE_HEAD": "tip of lane/2026-10-27-recompute-comparator (3bf93b25e at writing)",
 "ACCEPTANCE": [
   "X1 (Sol 1, Opus F1) step-11 coverage is key-bound: each mapped fill or disclosure leaf names the comparison row it copies (pack, contrast or cell id, field) and is covered only if that row exists, its L9 value equals the leaf exactly (type and value), and the row is AGREE; the reviewers' probes P1b, P2, P3 and Sol's wrong_fill_estimate now fail",
   "X2 (Sol 2) the machine-line order statistics and band (median, minimum, maximum, q25, q75, spread, central band) are compared: the comparator derives them from the recompute's member values with the registered definition and compares each under the rho or machine bar; Sol's wrong_machine_median now fails",
   "X3 (Sol 3, Opus F2) every family compares the union of L9 keys and recompute keys; a key on one side only is DISAGREE missing_or_null; for the meter line, the members of L9's disclosure, of the recompute's whole_machine.windows and of the supplied harvest record must be equal sets, and a member without its machine object is DISAGREE; probes P4-P7 and Sol's missing_l9_run, extra_recompute_run, missing_harvest_member, missing_harvest_machine now fail",
   "X4 (Sol 4, Opus F3) meter_clock_fit computes residuals, envelope and max-above-envelope in coordinates relative to the first fit point exactly as km003c_parse.clock_fit; tests extend the property test to host origins 1e12, 1e15, 4e15 and 1e16 ns and add the planted near-tie streams of the Opus probe and Sol's synthetic-meter-stream.jsonl: per-sample host times equal the parser's within 1 ns and the selected envelope points are identical, on every stream",
   "X5 (Sol 6, Opus F4) load_bars validates every per-key override like a family bar (finite, non-negative, printed_decimals a non-negative int); P8, P8b and Sol's infinite_override refuse",
   "X6 (Opus F5) catch-all uncovered rules match non-numeric leaves only; a numeric leaf under them refuses unless an explicit uncovered rule names that leaf with a reason; any leaf that becomes uncovered-by-name is listed in the report",
   "X7 (Opus F6) non-finite values in L9's restricted JSON become null with a STRUCTURE flag in the restricted output, which is always written; the comparison then shows DISAGREE for that row",
   "X8 (Opus F7) window edges follow the 7e322b76 rule (exact for window_basis controller_stamps, 1e-6 s for a legacy wall placement); (Opus F8) exact() compares type and value; (Opus F9) MeterStream follows the parser on header status and on batch decoding",
   "X9 every reviewer probe listed above is turned into a regression test that fails at 3bf93b25e (record the counterfactual) and passes after; tests/independent_recompute passes; no file outside WRITE_SCOPE changed; no import of joulewise.b5_analysis or joulewise.external in either script"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .",
   "the reviewers' probe scripts, run against the fixed head, each print the failing outcome"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# RC-CMP-3 fix brief

**Lead dispositions (RUN_STATE item 87).** Every finding of both reviews is fixed (X1-X9), except:
- **Sol 5 (public per-family pass/fail counts):** kept as designed. Block 5's release condition is agreement within
  fixed bars (item 37 (ii)), so whether each family agrees has to be known to release. A count says nothing about the
  size or sign of any value or difference; values and differences stay in the restricted folder.
- **BETA extra sessions (`--extra-beta`):** not compared. That labelled line is computed only by the recompute after
  release (item 37 (i)), so there is no L9 side.
- **Compressed `.zst` inputs:** block 5's archives hold plain `powermetrics.plist` and plain meter streams (checked
  from the manifests, item 86), so no restore step is needed for block 5.

**Rules.** Synthetic data only; never open real block-5/6/BYTES data. No bar is widened. No change to the sealed
registration, registered arithmetic, L9 or the parser. Push only to `lane/2026-10-27-recompute-comparator`; no force
push, no merge to main, no PR. Push the report after each milestone. After this job the lead sends the fixed head
back to both reviewers for a delta check.

**Report.** `.codex-report/RC-CMP-3.md`: SUMMARY, the X1-X9 table with evidence and counterfactuals, FILES CHANGED,
DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
