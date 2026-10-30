#!/usr/bin/env bash
set -eu
review_root=$(git rev-parse --show-toplevel)
review_python=${REVIEW_PYTHON:-python3.13}
export JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 JW="$review_root"
review_dir=.codex-report/by-therm-lines-rev-sol-5
env -C "$review_root" "$review_python" -m unittest tests.test_bytes_thermal_lines > "$review_dir/unit.log" 2>&1
env -C "$review_root" "$review_python" -m unittest tests.b6.test_bytes_p2_thermal_window > "$review_dir/thermal-window.log" 2>&1
env -C "$review_root" "$review_python" "$review_dir/probes.py" > "$review_dir/probes.log" 2>&1
env -C "$review_root" "$review_python" "$review_dir/census.py" > "$review_dir/census.log" 2>&1
env -C "$review_root" "$review_python" "$review_dir/large_level.py" > "$review_dir/large-level.log" 2>&1
env -C "$review_root" "$review_python" "$review_dir/session_path.py" > "$review_dir/session-path.log" 2>&1
