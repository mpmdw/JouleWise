# Fixed values of measurement block 5. Every command block of the magistrate brief sources this file first.
export MEASUREMENT_ROOT='/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5'
export PY='/Users/edr/night-custody/measurement/JouleWise-measurement-20261008T0817Z-b5/.venv/bin/python'
export H_CLAIM='a64000884ef5bb4b76415835f02f39803f6eb620'
export SEAL_HEAD='ab7b21e576a2d74f0b25d9a26b463d6934588368'
export REG_SHA256='4d321fe3756076aed508dbed4284b2103cdc4e9c1adc18f496e9d3a617410841'
export BENCH='/Users/edr/night-plan-staging/b5-bench'
export DESK_ROOT=/Users/edr/night-custody/desk/b5-harvest
export HARVEST_ADDENDUM='/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md'
export RECORDS_BRANCH=records/2026-10-block5
export RECORDS_WT=/Users/edr/code/JouleWise-wt-b5-records
export ANSWERS='/Users/edr/night-plan-staging/b5-bench/owner-answers.txt'
export NOTICE_TO='<not printed in the repository copy: the notice address of the owner is held in the installed file only>'
# A window's own values (written by brief section 5.2): set P to its plan id before sourcing this file.
if [ -n "${P:-}" ]; then source "/Users/edr/night-plan-staging/$P/arm-env.zsh" || echo "no arm-env.zsh for plan id $P"; fi
