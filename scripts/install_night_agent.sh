#!/bin/zsh
set -euo pipefail

usage() {
  print "usage: $0 --plan PLAN.json [--python ABS_PATH] [--uninstall] [--render-only DIR] [--launchctl-bin PATH]" >&2
  exit 2
}

plan=""
python=""
python_given=0
uninstall=0
render_only=""
launchctl_bin="launchctl"
while (( $# )); do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --python) python="${2:-}"; python_given=1; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
    --render-only) render_only="${2:-}"; shift 2 ;;
    --launchctl-bin) launchctl_bin="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -n "$plan" ]] || usage
[[ -f "$plan" ]] || { print "plan not found: $plan" >&2; exit 2; }
script_dir="${0:A:h}"
repo="${script_dir:h}"
if (( uninstall )); then
  python="/usr/bin/python3"
else
  if (( ! python_given )); then
    # Any Python 3 (including the 3.9 from the 2026-09-11 defect) can read
    # this JSON using only stdlib json and sys, never the project or driver.
    # The plists still name the derived venv Python, checked by MIN_PYTHON below.
    measurement_root="$(/usr/bin/env python3 -B -S -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])' "$plan" 2>/dev/null)" && [[ -n "$measurement_root" ]] || {
      print "cannot derive measurement_root/.venv/bin/python from $plan; pass --python ABS_PATH" >&2
      exit 2
    }
    python="$measurement_root/.venv/bin/python"
    [[ -f "$python" && -x "$python" ]] || {
      print "missing executable interpreter: $python; pass --python ABS_PATH" >&2
      exit 2
    }
  fi
  [[ "$python" == /* && -f "$python" && -x "$python" ]] || {
    print "invalid --python: $python (expected an absolute executable regular file)" >&2
    exit 2
  }
  # Read only the minimum literal: importing the driver before checking the
  # version could itself fail on an old interpreter (the 2026-09-11 defect).
  "$python" -B - "$repo/scripts/run_night.py" "$python" <<'PYTHON_CHECK' || exit 2
import ast
import re
import sys

# Parse ONLY the MIN_PYTHON assignment line, never the whole driver: the driver
# may use syntax the rejected interpreter cannot parse, and a SyntaxError here
# would replace the version message with a parser traceback (refuter 08 F1).
with open(sys.argv[1], encoding="utf-8") as stream:
    match_line = next(
        (line for line in stream if re.match(r"^MIN_PYTHON\s*=\s*\(", line)), None)
if match_line is None:
    print("cannot find the MIN_PYTHON assignment in {}".format(sys.argv[1]), file=sys.stderr)
    raise SystemExit(2)
minimum = ast.literal_eval(match_line.split("=", 1)[1].strip())
if sys.version_info[:2] < minimum:
    print("interpreter {} reports Python {}; minimum is {}".format(
        sys.argv[2], ".".join(map(str, sys.version_info[:2])),
        ".".join(map(str, minimum))), file=sys.stderr)
    raise SystemExit(2)
PYTHON_CHECK
fi
# Resolve caller-relative paths before binding -m to the script's checkout.
if [[ "$launchctl_bin" == */* ]]; then
  launchctl_bin="${launchctl_bin:A}"
fi
set -- --plan "${plan:A}" --launchctl-bin "$launchctl_bin"
if [[ -n "$render_only" ]]; then
  set -- "$@" --render-only "${render_only:A}"
fi
if (( uninstall )); then
  set -- "$@" --uninstall
  if (( python_given )); then
    set -- "$@" --python "$python"
  fi
else
  set -- "$@" --python "$python"
fi
cd "$repo"
PYTHONPATH="$repo" exec "$python" -B -m joulewise.night_agent_install "$@"
