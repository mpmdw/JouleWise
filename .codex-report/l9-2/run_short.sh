#!/usr/bin/env bash
# Short modules plus the cache test, sequential, one process each, fresh TMPDIR each.
run=$1
for m in tests.test_authentication_io tests.test_docs_freshness tests.b5_analysis.test_sensitivity_guard \
         tests.b5_analysis.test_mint_kept_units tests.b5_analysis.test_s10_chain_defects tests.test_r4_acceptance_oracle \
         tests.b5_analysis.test_shared_physics_cache tests.b5_analysis.test_deadline_tripwire tests.b5_analysis.test_deadline_observer; do
  "$(dirname "$0")/run_module.sh" "$run" "$m"
done
touch "$run/ALL_DONE"
