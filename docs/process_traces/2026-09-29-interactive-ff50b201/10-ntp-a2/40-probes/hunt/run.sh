#!/bin/bash
S=/private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3
for pair in "new:/Users/edr/code/JouleWise-wt-n1d3-new-ff50b201" "old:$S/oldov"; do
  h=${pair%%:*}; d=${pair#*:}
  cp $S/hunt/delta_hunt_cases.py $d/tests/zz_delta3_hunt.py
  (cd $d && /opt/homebrew/bin/python3 -B -m unittest tests.zz_delta3_hunt.DeltaHunt.test_DM1_deadman_null_claim_without_launch_error tests.zz_delta3_hunt.DeltaHunt.test_DM2a_deadman_failed_recovery_proof_no_census_refusal tests.zz_delta3_hunt.DeltaHunt.test_DM2b_deadman_census_doc_then_hung_driver_result_step tests.zz_delta3_hunt.DeltaHunt.test_SF_watchdog_supersede_failure_fallback tests.zz_delta3_hunt.DeltaHunt.test_SS_watchdog_supersede_normal_prior_documents tests.zz_delta3_hunt.DeltaHunt.test_DM3_watchdog_doc_then_driver_never_resumes_deadman_proof_fails > $S/hunt/$h.log 2>&1; echo "$h exit=$?")
  rm -f $d/tests/zz_delta3_hunt.py
done
