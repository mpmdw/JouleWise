#!/bin/zsh
# Runbook §1.4 recovery after a post-publication failure. Record every rc.
source /tmp/magistrate-b58fb582/exports.zsh
set -uo pipefail
cd "$MEASUREMENT_ROOT"
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" --uninstall; echo "uninstall rc=$?"
cp "$NIGHT_ROOT/night_plan.json" "$STAGE/failed-night_plan.json"; echo "cp rc=$?"
cmp "$STAGE/failed-night_plan.json" "$STAGE/arm-night_plan.json"; echo "cmp rc=$?"
rm "$NIGHT_ROOT/night_plan.json"; echo "rm rc=$?"
launchctl list | grep joulewise
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
