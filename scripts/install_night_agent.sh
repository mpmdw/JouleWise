#!/bin/zsh
set -euo pipefail

usage() {
  print "usage: $0 --plan PLAN.json --hour H --minute M [--uninstall] [--render-only DIR] [--launchctl-bin PATH]" >&2
  exit 2
}

plan=""
hour=""
minute=""
uninstall=0
render_only=""
launchctl_bin="launchctl"
while (( $# )); do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --hour) hour="${2:-}"; shift 2 ;;
    --minute) minute="${2:-}"; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
    --render-only) render_only="${2:-}"; shift 2 ;;
    --launchctl-bin) launchctl_bin="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done
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
custody_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])' "$plan")"
courier_bin=""
courier_path=""
if (( ! uninstall )); then
  plan_head="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repo_head"])' "$plan")"
  if ! actual_head="$(/usr/bin/git -C "$repo" rev-parse HEAD)"; then
    print "unable to read repo_head from driver checkout" >&2
    exit 3
  fi
  [[ "$plan_head" == "$actual_head" ]] || {
    print "plan repo_head does not match driver checkout HEAD" >&2
    exit 3
  }
  measurement_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["measurement_root"])' "$plan")"
  plan_measurement_head="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["measurement_head"])' "$plan")"
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
fi
read -r deadman_hour deadman_minute < <(
  cd "$repo"
  /usr/bin/python3 -c 'from scripts.run_night import DEADMAN_HOUR, DEADMAN_MINUTE; print(DEADMAN_HOUR, DEADMAN_MINUTE)'
)
if (( ! uninstall && hour == deadman_hour )); then
  print "refusing --hour $hour: it is the dead-man hour (DEADMAN_HOUR=$deadman_hour); arm the night in another hour" >&2
  exit 2
fi

if [[ -n "$render_only" ]]; then
  launch_dir="${render_only:A}"
else
  launch_dir="$HOME/Library/LaunchAgents"
fi
mkdir -p "$launch_dir" "$custody_root/night"
uid="$(id -u)"

render() {
  local label="$1"
  local mode="$2"
  local out="$3"
  local entry_hour="$4"
  local entry_minute="$5"
  local log_stem="$6"
  /usr/bin/python3 - "$template" "$out" "$label" "$mode" "$repo" "$plan" "$custody_root" "$entry_hour" "$entry_minute" "$courier_bin" "$courier_path" "$log_stem" <<'PY'
from pathlib import Path
import sys

template, output, label, mode, repo, plan, custody, hour, minute, courier, path, log_stem = sys.argv[1:]
replacements = {
    "com.joulewise.night": label,
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
