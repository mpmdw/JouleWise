#!/bin/zsh
set -euo pipefail

usage() {
  print "usage: $0 --plan PLAN.json --hour H --minute M [--uninstall]" >&2
  exit 2
}

plan=""
hour=""
minute=""
uninstall=0
while (( $# )); do
  case "$1" in
    --plan) plan="${2:-}"; shift 2 ;;
    --hour) hour="${2:-}"; shift 2 ;;
    --minute) minute="${2:-}"; shift 2 ;;
    --uninstall) uninstall=1; shift ;;
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
plan="${plan:A}"
plan_head="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["repo_head"])' "$plan")"
actual_head="$(git -C "$repo" rev-parse HEAD)"
[[ "$plan_head" == "$actual_head" ]] || {
  print "plan repo_head does not match checkout HEAD" >&2
  exit 3
}
custody_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])' "$plan")"
launch_dir="$HOME/Library/LaunchAgents"
mkdir -p "$launch_dir" "$custody_root/night"
uid="$(id -u)"

render() {
  local label="$1"
  local mode="$2"
  local out="$3"
  local entry_hour="$4"
  local entry_minute="$5"
  /usr/bin/python3 - "$template" "$out" "$label" "$mode" "$repo" "$plan" "$custody_root" "$entry_hour" "$entry_minute" <<'PY'
from pathlib import Path
import sys

template, output, label, mode, repo, plan, custody, hour, minute = sys.argv[1:]
replacements = {
    "com.joulewise.night": label,
    "@@MODE@@": mode,
    "@@REPO@@": repo,
    "@@PLAN@@": plan,
    "@@CUSTODY_ROOT@@": custody,
    "@@HOUR@@": hour,
    "@@MINUTE@@": minute,
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
if (( uninstall )); then
  launchctl bootout "gui/$uid/$night_label" 2>/dev/null || true
  launchctl bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  rm -f "$night_plist" "$deadman_plist"
  exit 0
fi

render "$night_label" run "$night_plist" "$hour" "$minute"
render "$deadman_label" dead-man "$deadman_plist" 7 0
for plist in "$night_plist" "$deadman_plist"; do
  label="${plist:t:r}"
  launchctl bootout "gui/$uid/$label" 2>/dev/null || true
  launchctl bootstrap "gui/$uid" "$plist"
  launchctl print "gui/$uid/$label"
done
