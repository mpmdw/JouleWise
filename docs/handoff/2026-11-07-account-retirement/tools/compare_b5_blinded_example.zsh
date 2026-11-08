#!/bin/zsh
# Blinded comparator dry-k (reference rerun) vs dry-j (r2 candidate). Reads ONLY stdout fixed grammar + BLINDED-VERDICT.txt.
cd /Users/edr/code/CapstoneProject/jw-wt/cmp-dryij || exit 9
REF_CUSTODY=/Users/edr/jw-b5-custody/dry-k; CAND_CUSTODY=/Users/edr/jw-b5-custody/dry-j
LOG=/private/tmp/jwd188-plan/compare_dryk_j.$(date -u +%Y%m%dT%H%M%SZ).log
echo "comparator HEAD $(git rev-parse HEAD)" > $LOG
nice -n 0 python3.13 -I -B tools/b5_equivalence/compare_b5_results.py --mode blinded --run blind-dry-run "$REF_CUSTODY" "$CAND_CUSTODY" >> $LOG 2> $LOG.stderr-UNREAD
rc=$?
echo "comparator_exit=$rc" >> $LOG
echo "--- BLINDED-VERDICT.txt" >> $LOG
cat "$CAND_CUSTODY/equivalence/BLINDED-VERDICT.txt" >> $LOG 2>/dev/null || echo "(verdict file absent)" >> $LOG
cat $LOG; exit $rc
