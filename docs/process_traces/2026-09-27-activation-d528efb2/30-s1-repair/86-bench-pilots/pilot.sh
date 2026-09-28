#!/bin/zsh
# pilot.sh <tag> <test-id> <modes...>: modes green | charging | offsecond
cd /Users/edr/code/JouleWise-wt-s1bench-d528efb2 || exit 2
G=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard
O=/tmp/s1bench-d528efb2; export TMPDIR=$O/; TAG=$1; T=$2; shift 2
for MODE in "$@"; do
  case $MODE in
    green) PYTHONPATH=$G /opt/homebrew/bin/python3 -B -m unittest $T < /dev/null > $O/$TAG-$MODE.log 2>&1 ;;
    charging) PYTHONPATH=$G /opt/homebrew/bin/python3 -B $O/plant_charging.py $T < /dev/null > $O/$TAG-$MODE.log 2>&1 ;;
    offsecond) PYTHONPATH=$G /opt/homebrew/bin/python3 -B $O/plant_offsecond.py $T < /dev/null > $O/$TAG-$MODE.log 2>&1 ;;
  esac
  echo "$TAG $MODE rc=$? $(tail -1 $O/$TAG-$MODE.log) | $(grep -oE 'battery_float_[a-z_]*|adapter_continuity_failed|cpu_admission_core_failed|environment_admission_failed|environment_admission_missing|whole_window_verdict_conflict|whole_window_verdict_provenance_invalid' $O/$TAG-$MODE.log | sort | uniq -c | tr '\n' ' ')"
done
