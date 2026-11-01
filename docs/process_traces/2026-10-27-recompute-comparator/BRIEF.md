BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "RC-CMP-1: recompute-versus-L9 comparator, recompute output hygiene, and a full-size synthetic agreement run",
 "OBJECTIVE": "Build a comparator between L9's block-5 dry-run outputs and the independent recompute's, make the recompute's public output structure-only, and run both on a full-size synthetic block-5 window before any release, so implementation disagreements are found before anyone sees a real number.",
 "AUTHORITY": [
   "Ed, 2026-10-27, session 015ASG1T: 'yes, queue option 1' (run the recompute and comparator on full-size synthetic data before the release; the sealed §8 blinding clause is not changed)",
   "configs/campaigns/v5_claim_25g83/registration_block5.md (sealed; §8 Blinding and its custody map are NOT amended by this work)",
   "RUN_STATE.md item 37 (independent recompute decisions, rounds 1-3 definitions)",
   "docs/process_traces/2026-10-27-pipeline-audit/SYNTHESIS.md items N6, N7 and CRITIQUE.md items 1, 12",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "scripts/independent_recompute_b5.py",
   "scripts/compare_b5_recompute.py",
   "tests/independent_recompute/**",
   ".codex-report/RC-CMP-1.md"],
 "BASE_HEAD": "tip of lane/2026-10-14-independent-recompute (9ca87bcee at writing)",
 "ACCEPTANCE": [
   "A1 comparator: reads L9 dry-run restricted outputs and recompute outputs; numeric families compared against a bar table read from a config argument (no hard-coded bars), shipped with two bar sets: the recompute's coded bars (commit 7e322b76) and block 6's S-13 bars (1 mJ per run phase energy; every printed quantity, unrounded, within half a unit of its last printed digit); exact match for outcome words, dominance branch, p42 status and Holm order",
   "A2 comparator: a value missing or null on either side is DISAGREE; it refuses unless every step-11 fill or placement is mapped to a comparison or listed as uncovered",
   "A3 comparator: planted-fault tests per family (one per numeric family, one per categorical family, one missing-value, one unmapped-fill), each failing without the check (counterfactual)",
   "A4 comparator public output: pass/fail counts per family only; observed differences go to the restricted folder",
   "A5 recompute hygiene: stdout and stderr carry STRUCTURE codes only (today it prints science-derived pass/fail flag codes, scripts/independent_recompute_b5.py:58-63, 2638-2655); a stdlib re-derivation of member exclusions from flags.jsonl through the registered flag catalog, compared to exclusions.json; the interpreter version recorded",
   "A6 full-size synthetic agreement run: generate L9's full-size synthetic block-5 window with L9's own fixture (read-only checkout of lane/2026-10-27-l9-2 at its tip; never import L9 code into the recompute or comparator), run L9's dry run on it and the recompute on the same bytes, then the comparator; report per-family pass/fail counts and every disagreement with its classification (recompute defect, L9 defect, definition difference, fixture artefact)",
   "A7 no file outside WRITE_SCOPE changed; the recompute and comparator import nothing from joulewise/b5_analysis/ (independence)"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .",
   "grep shows no import of joulewise.b5_analysis in scripts/independent_recompute_b5.py or scripts/compare_b5_recompute.py"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# RC-CMP-1 brief

**Why.** Block 5's sealed registration does not allow the independent recompute to read real restricted data before
the release (§8, completed attempts). So the real comparison happens at the release. A disagreement found then is
fixed with the numbers in view, which is the hazard blinding exists to prevent. This job front-loads almost all of
that risk: most real disagreements are implementation differences, and synthetic data with known structure exposes
them now.

**Rules.**
- Synthetic data only. Never open a real block-5 or block-6 archive, export or key directory.
- No change to registered arithmetic, tolerances or the sealed §8. Which bar set binds block 5's release is NOT
  decided here: list it in NEEDS_RULING (critique item 12 found the two sets conflict). The lead and Ed rule it before
  the release.
- Push only to `lane/2026-10-27-recompute-comparator`. No force push, no merge to main, no PR.
- Long runs start detached with durable logs, one heavy run at a time. Push the report after each milestone.
- After this job: two executing reviews launched together, per the gate policy (rule 3: Sol 6.1 xhigh fast and
  Opus 5.5).

**Report.** `.codex-report/RC-CMP-1.md`: SUMMARY, the A1-A7 table with evidence, the disagreement list, FILES
CHANGED, DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
