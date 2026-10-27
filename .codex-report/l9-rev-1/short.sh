#!/usr/bin/env bash
cd /home/user/JouleWise
for m in tests.test_authentication_io tests.test_docs_freshness tests.b5_analysis.test_sensitivity_guard \
         tests.b5_analysis.test_s10_chain_defects tests.test_r4_acceptance_oracle tests.b5_analysis.test_mint_kept_units; do
  d=$(mktemp -d /tmp/jwtmp/short-XXXX); s=$(date +%s.%N)
  JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$d python3.13 -m unittest -v $m > $1/$m.log 2>&1; rc=$?
  echo "$m rc=$rc wall=$(echo "$(date +%s.%N) - $s" | bc) $(tail -1 $1/$m.log) sha=$(sha256sum $1/$m.log|cut -c1-16)" >> $1/summary.txt
done
