#!/bin/zsh
# PROPOSED BENCH RECIPE ONLY. NOT EXECUTED BY THIS CONSULT.
# All instrument runs here are [QUIET-MAC], agent-free, controlled synthetic
# load included. Lead must review, choose the window, and own live verification.
# These are diagnostic captures, never derivation members or paper power data.
set -eu
PY=/Users/edr/code/JouleWise/.venv/bin/python
P=/tmp/jw_cadence_probe.py
PROBE_ROOT=$(mktemp -d /tmp/jw-cadence-bench.XXXXXX)
/usr/bin/sw_vers > "$PROBE_ROOT/os.txt"
/usr/bin/shasum -a 256 /usr/bin/powermetrics > "$PROBE_ROOT/binary.sha256"
/usr/bin/pmset -g custom > "$PROBE_ROOT/power-policy.txt"
# Lead adds boot id, machine/AC/thermal state, agent census, interpreter/MLX
# identities and optional library provenance. Keep display/power policy fixed.
run() {
  local label=$1 state=$2
  shift 2
  "$PY" -B "$P" --seconds 90 --out "$PROBE_ROOT/$label-$state" --load "$state" "$@"
  sleep 30
}
# Reversed order separates configuration from monotonic time drift. Each
# block has a matched production baseline at its beginning and end.
run base0 idle
run min100 idle --samplers cpu_power,gpu_power
run prod50 idle --interval-ms 50
run prod200 idle --interval-ms 200
run hide100 idle --hide-cpu-duty-cycle
run base1 idle
run base0 busy
run hide100 busy --hide-cpu-duty-cycle
run prod200 busy --interval-ms 200
run prod50 busy --interval-ms 50
run min100 busy --samplers cpu_power,gpu_power
run base1 busy
# Single-instrument sequential path controls. Same production argv except -o.
run file-hooks idle --adapter-hooks
run stdout-direct idle --mode stdout
run stdout-hooks idle --mode stdout --adapter-hooks
# 15 * 90 s + 15 * 30 s + 6 * 5 s busy warmup = 30.5 min nominal,
# plus interpreter/startup/teardown; budget 35 min. Stop on cleanup failure.
# ADAPTIVE ONLY, after analysis: if minimal helps, isolate ANE versus thermal:
# run ane100 idle --samplers cpu_power,gpu_power,ane_power
# run thermal100 idle --samplers cpu_power,gpu_power,thermal
# Repeat each helpful candidate and baseline in reverse order in both states.
# Old signed binary counterfactual, only if a compatible retained copy exists:
# "$PY" -B "$P" --seconds 90 --out "$PROBE_ROOT/old-on-new" --binary "$OLD_PM"
# Never replace /usr/bin/powermetrics. Repeat matched binary on an approved
# alternate OS boot only if binary-vs-OS causation is still worth resolving.
