#!/bin/zsh
# D-176 decision 4: real pack launch, zero model/sampler members.
set -euo pipefail
: "${MEASUREMENT_ROOT:?required}"
: "${NIGHT_DIR:?required}"
: "${PY:?required}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$MEASUREMENT_ROOT"
# The driver retains the exact pinned input plan path, before consumption.
IFS= read -r rehearsal_plan < "$NIGHT_DIR/rehearsal-plan-path.txt"
exec "$PY" -B "$MEASUREMENT_ROOT/scripts/produce_t0_rehearsal_bundle.py" lifecycle --plan "$rehearsal_plan"
