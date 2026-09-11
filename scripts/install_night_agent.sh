#!/bin/zsh
set -euo pipefail

usage() {
  print "usage: $0 --plan PLAN.json --hour H --minute M [--python ABS_PATH] [--uninstall] [--render-only DIR] [--launchctl-bin PATH]" >&2
  exit 2
}

plan=""
hour=""
minute=""
python=""
python_given=0
uninstall=0
render_only=""
launchctl_bin="launchctl"
while (( $# )); do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --hour) hour="${2:-}"; shift 2 ;;
    --minute) minute="${2:-}"; shift 2 ;;
    --python) python="${2:-}"; python_given=1; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
    --render-only) render_only="${2:-}"; shift 2 ;;
    --launchctl-bin) launchctl_bin="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done
(( uninstall && python_given )) && usage
[[ -n "$plan" && -n "$hour" && -n "$minute" ]] || usage
[[ "$hour" == <-> && "$minute" == <-> ]] || usage
(( hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59 )) || usage
[[ -f "$plan" ]] || { print "plan not found: $plan" >&2; exit 2; }

script_dir="${0:A:h}"
repo="${script_dir:h}"
template="$repo/configs/launchd/com.joulewise.night.plist.template"
[[ -f "$template" ]] || { print "template not found: $template" >&2; exit 2; }
/usr/bin/grep -q "KeepAlive" "$template" && {
  print "template must not contain KeepAlive" >&2
  exit 3
}
plan="${plan:A}"
custody_root=""
courier_bin=""
courier_path=""
if (( ! uninstall )); then
  if (( ! python_given )); then
    # Bootstrap the candidate without running any Python or project imports.
    measurement_root="$(/usr/bin/plutil -extract measurement_root raw -o - "$plan")" || {
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
  plan_fields=("${(@f)$("$python" -B - "$plan" "$repo" <<'PY'
import base64
import json
import sys
import time

sys.path.insert(0, sys.argv[2])
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S, PlanError

with open(sys.argv[1], encoding="utf-8") as stream:
    data = json.load(stream)
try:
    parsed = NightPlan.from_mapping(data)
    if parsed.measurement_root != parsed.measurement_root.strip():
        raise PlanError(
            "night_plan_malformed",
            "measurement_root must be an absolute path with no surrounding whitespace",
        )
    now_epoch_s = time.time()
    if parsed.authored_epoch_s > now_epoch_s:
        raise PlanError(
            "night_plan_malformed",
            "plan authored_epoch_s is in the future",
        )
    if now_epoch_s - parsed.authored_epoch_s > PLAN_MAX_AGE_S:
        raise PlanError("night_plan_stale", "plan is older than 36 hours")
except PlanError as exc:
    print(f"{exc.reason}: {exc.detail}", file=sys.stderr)
    raise SystemExit(3)
for value in (parsed.repo_head, parsed.measurement_root, parsed.measurement_head, parsed.custody_root):
    print(base64.b64encode(value.encode("utf-8")).decode("ascii"))
PY
  )}") || exit $?
  plan_head="$(print -rn -- "$plan_fields[1]" | /usr/bin/base64 --decode)"
  measurement_root="$(print -rn -- "$plan_fields[2]" | /usr/bin/base64 --decode)"
  plan_measurement_head="$(print -rn -- "$plan_fields[3]" | /usr/bin/base64 --decode)"
  custody_root="$(print -rn -- "$plan_fields[4]" | /usr/bin/base64 --decode)"
  if ! actual_head="$(/usr/bin/git -C "$repo" rev-parse HEAD)"; then
    print "unable to read repo_head from driver checkout" >&2
    exit 3
  fi
  [[ "$plan_head" == "$actual_head" ]] || {
    print "plan repo_head does not match driver checkout HEAD" >&2
    exit 3
  }
  if ! actual_measurement_head="$(/usr/bin/git -C "$measurement_root" rev-parse HEAD)"; then
    print "unable to read measurement_head from measurement checkout" >&2
    exit 3
  fi
  [[ "$plan_measurement_head" == "$actual_measurement_head" ]] || {
    print "plan measurement_head does not match measurement checkout HEAD" >&2
    exit 3
  }
  courier_bin="$(command -v claude || true)"
  [[ -n "$courier_bin" && -x "$courier_bin" ]] || {
    print "courier unavailable: command -v claude found no executable" >&2
    exit 2
  }
  courier_path="${courier_bin:h}:/usr/bin:/bin:/usr/sbin:/sbin"
  courier_bin="${courier_bin:A}"
else
  # Uninstall only removes existing agents; no plan validation is needed to locate what to remove.
  custody_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])' "$plan")"
fi
if (( ! uninstall )); then
  # Match the job's PATH and HOME, without inherited Python import overrides.
  /usr/bin/env -i PATH="$courier_path" HOME="$HOME" \
    "$python" -B "$repo/scripts/run_night.py" preflight --plan "$plan" || exit 2
  deadman_fields="$(
    cd "$repo"
    "$python" -B -c 'from scripts.run_night import DEADMAN_HOUR, DEADMAN_MINUTE; print(DEADMAN_HOUR, DEADMAN_MINUTE)'
  )" || exit 2
  read -r deadman_hour deadman_minute <<< "$deadman_fields"
  if (( hour == deadman_hour )); then
    print "refusing --hour $hour: it is the dead-man hour (DEADMAN_HOUR=$deadman_hour); arm the night in another hour" >&2
    exit 2
  fi
fi

if [[ -n "$render_only" ]]; then
  launch_dir="${render_only:A}"
else
  launch_dir="$HOME/Library/LaunchAgents"
fi
mkdir -p "$launch_dir"
if [[ "${uninstall:-0}" != "1" ]]; then
  # Only an install may create custody; uninstall must never touch the plan's custody root.
  mkdir -p "$custody_root/night"
fi
uid="$(id -u)"

render() {
  local label="$1"
  local mode="$2"
  local out="$3"
  local entry_hour="$4"
  local entry_minute="$5"
  local log_stem="$6"
  "$python" -B - "$template" "$out" "$label" "$mode" "$repo" "$plan" "$custody_root" "$entry_hour" "$entry_minute" "$courier_bin" "$courier_path" "$log_stem" "$python" <<'PY'
from pathlib import Path
import sys
from xml.sax.saxutils import escape

template, output, label, mode, repo, plan, custody, hour, minute, courier, path, log_stem, python = sys.argv[1:]
replacements = {
    "com.joulewise.night": label,
    "@@PYTHON@@": escape(python),
    "@@MODE@@": mode,
    "@@REPO@@": repo,
    "@@PLAN@@": plan,
    "@@CUSTODY_ROOT@@": custody,
    "@@HOUR@@": hour,
    "@@MINUTE@@": minute,
    "@@COURIER_BIN@@": courier,
    "@@PATH@@": path,
    "@@LOG_STEM@@": log_stem,
}
text = Path(template).read_text(encoding="utf-8")
for old, new in replacements.items():
    text = text.replace(old, new)
Path(output).write_text(text, encoding="utf-8")
PY
}

night_label="com.joulewise.night"
deadman_label="com.joulewise.night.deadman"
night_plist="$launch_dir/$night_label.plist"
deadman_plist="$launch_dir/$deadman_label.plist"
if [[ -z "$render_only" ]]; then
  if [[ "$launchctl_bin" != */* ]]; then
    launchctl_bin="$(command -v "$launchctl_bin" || true)"
  fi
  [[ -n "$launchctl_bin" && -x "$launchctl_bin" ]] || {
    print "launchctl executable not found" >&2
    exit 2
  }
  launchctl_bin="${launchctl_bin:A}"
fi
if (( uninstall )); then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  "$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  rm -f "$night_plist" "$deadman_plist"
  exit 0
fi

existing_night_records=()
for record in receipt.json result.json refusal.json chain.started chain.exited courier.json courier.sent; do
  # -L too: a dangling symlink is still a record name the run path would trip on.
  [[ -e "$custody_root/night/$record" || -L "$custody_root/night/$record" ]] && existing_night_records+=("$record")
done
if (( ${#existing_night_records[@]} )); then
  print "refusing install: existing night records: ${existing_night_records[*]}" >&2
  exit 3
fi

render "$night_label" run "$night_plist" "$hour" "$minute" "launchd.night"
render "$deadman_label" dead-man "$deadman_plist" "$deadman_hour" "$deadman_minute" "launchd.deadman"
if [[ -n "$render_only" ]]; then
  print "validated pins: repo_head=$plan_head measurement_root=$measurement_root measurement_head=$plan_measurement_head"
  exit 0
fi

"$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
"$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
if ! "$launchctl_bin" bootstrap "gui/$uid" "$night_plist"; then
  print "failed to bootstrap $night_label" >&2
  exit 3
fi
if ! "$launchctl_bin" bootstrap "gui/$uid" "$deadman_plist"; then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  print "failed to bootstrap $deadman_label; rolled back $night_label" >&2
  exit 3
fi
if ! "$launchctl_bin" print "gui/$uid/$night_label" || \
   ! "$launchctl_bin" print "gui/$uid/$deadman_label"; then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  "$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  print "launch agent verification failed; rolled back both agents" >&2
  exit 3
fi
print "validated pins: repo_head=$plan_head measurement_root=$measurement_root measurement_head=$plan_measurement_head"
