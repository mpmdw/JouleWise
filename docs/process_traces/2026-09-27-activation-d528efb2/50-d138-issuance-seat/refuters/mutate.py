import subprocess, sys
from pathlib import Path
T = Path("/tmp/d138-contract-refuter/tree")
PY = "/opt/homebrew/bin/python3"
M = [
 ("M1 drop rule (d)", "joulewise/calibration_bracketing.py",
  "        if any(\n            prior_row_by_content_id[content_id].get(\"session_id\") in registration_session_ids\n            or content_id in member_content_ids\n            for content_id in disposed\n        ):\n            return False\n", "",
  ["tests.test_calibration_dispositions.DispositionTests.test_l6_disposed_inside_registration_refuses", "tests.test_calibration_dispositions.DispositionTests.test_l7_member_in_disposition_table_refuses"]),
 ("M2 drop rule (c)", "joulewise/calibration_bracketing.py",
  "        if not disposed.issubset(set(prior_ids)):\n            return False\n", "",
  ["tests.test_calibration_dispositions.DispositionTests.test_l5_missing_disposed_row_refuses"]),
 ("M3 drop rule (b)", "joulewise/calibration_bracketing.py",
  "        if decisions_disposing(set(prior_ids)) != (declared if declared is not None else []):\n            return False\n", "",
  ["tests.test_calibration_dispositions.DispositionTests.test_l3_l4_declaration_refuses"]),
 ("M4 skip by session name not id", "joulewise/calibration_bracketing.py",
  "            if observation[\"content_id\"] in disposed:\n", "            if observation.get(\"session_id\", \"\").endswith(\"20260919\"):\n",
  ["tests.test_calibration_dispositions.DispositionTests.test_l2_unlisted_foreign_valid_refuses"]),
 ("M5 drop rule (f)", "joulewise/calibration_bracketing.py",
  "        if disposed & excluded_content_ids:\n            return False\n", "",
  ["tests.test_calibration_dispositions"]),
 ("M6 use whole table ignoring declaration", "joulewise/calibration_dispositions.py",
  "    return frozenset().union(*(DISPOSITION_DECISIONS[item][\"content_ids\"] for item in declared))",
  "    return frozenset().union(*(row[\"content_ids\"] for row in DISPOSITION_DECISIONS.values()))",
  ["tests.test_calibration_dispositions.DispositionTests.test_l3_l4_declaration_refuses"]),
 ("M7 promote: drop INPUT seal stop", "scripts/promote_calibration_candidate.py",
  "    if issued[\"derivation_input_sha256\"] != INPUT_SHA256:\n        raise ValueError(\"STOP: derivation input seal differs from ruled digest\")\n", "",
  ["tests.test_promote_calibration_candidate"]),
 ("M8 promote: drop candidate own-seal check", "scripts/promote_calibration_candidate.py",
  "        or candidate.get(\"derivation_input_sha256\") != derivation_input_sha256(candidate)\n        or candidate.get(\"derivation_sha256\") != derivation_sha256(candidate)\n", "\n",
  ["tests.test_promote_calibration_candidate.PromotionTests.test_p3_changed_member_refuses_both_seals"]),
 ("M9 unfreeze epoch_equivalence default", "scripts/epoch_equivalence_check.py",
  "\"--acceptance\", type=Path, default=ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH,", "\"--acceptance\", type=Path, default=__import__('joulewise.calibration_bracketing',fromlist=['x']).DEFAULT_ACCEPTANCE_BOUND_PATH,",
  ["tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_default_acceptance_remains_r7"]),
 ("M10 unfreeze sim_acc", "scripts/sim_acc_25g83_rev5.py",
  "load_calibration_acceptance_bound(ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)", "load_calibration_acceptance_bound()",
  ["tests.test_acc_25g83_rev5.RevisionFiveTests.test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7"]),
 ("M11 unfreeze issuer predecessor check", "scripts/issue_calibration_acceptance_generation.py",
  "        if predecessor[\"acceptance_id\"] != ANCHOR_V3_R7_ACCEPTANCE_ID:", "        if predecessor[\"acceptance_id\"] != ACTIVE_ACCEPTANCE_ID:",
  ["tests.test_acc_25g83_rev5"]),
 ("M12 unfreeze issuer predecessor default", "scripts/issue_calibration_acceptance_generation.py",
  "\"--predecessor-acceptance\", type=Path, default=ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH,", "\"--predecessor-acceptance\", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,",
  ["tests.test_acc_25g83_rev5", "tests.test_issuer_corpus_root"]),
 ("M13 drop H1 hold", "joulewise/arm_readiness.py",
  "    return issued in _ISSUED_D079_IDS and issued not in _CLAIM_HELD_ACCEPTANCE_IDS", "    return issued in _ISSUED_D079_IDS",
  ["tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t1_new_issuance_is_held_at_arm"]),
 ("M14 schema: loosen 25G83 screen const", "scripts/floor_mint_pinsets/schema_v2.json",
  "\"bracket_screen_s\": {\"const\": \"0.013701\"}", "\"bracket_screen_s\": {\"const\": \"0.009724\"}",
  ["tests.test_floor_mint_pinsets_schema"]),
]
for name, rel, old, new, tests in M:
    p = T/rel; src = p.read_text(encoding="utf-8"); n = src.count(old)
    if n < 1: print(name, "PATTERN NOT FOUND"); continue
    p.write_text(src.replace(old, new), encoding="utf-8")
    try:
        r = subprocess.run([PY, "-B", "-m", "unittest", *tests], cwd=T, capture_output=True, text=True, timeout=900)
        tail = [l for l in r.stderr.splitlines() if l.startswith(("FAILED","OK","Ran","ERROR:","FAIL:"))]
        print(f"{name} (occurrences {n}): rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {' | '.join(tail)[:300]}")
    finally:
        p.write_text(src, encoding="utf-8")
