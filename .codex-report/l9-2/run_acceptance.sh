#!/usr/bin/env bash
# Short modules, then the full-size cached test_dry_run alone (observed), at one head.
here=$(dirname "$0")
"$here/run_short.sh" "$1/short"
"$here/host_sampler.sh" "$1/host.log" 30 & sampler=$!
"$here/run_module.sh" "$1/dry" tests.b5_analysis.test_dry_run observed
kill $sampler
touch "$1/ALL_DONE"
