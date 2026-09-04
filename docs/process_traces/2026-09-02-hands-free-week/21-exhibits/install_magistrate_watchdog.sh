#!/bin/zsh
set -euo pipefail

usage() {
  print "usage: $0 (--install | --uninstall | --render-only DIR) [--launchctl-bin PATH]" >&2
  exit 2
}

mode=""
render_dir=""
launchctl_bin="launchctl"
while (( $# )); do
  case "$1" in
    --install|--uninstall)
      [[ -z "$mode" ]] || usage
      mode="$1"
      shift
      ;;
    --render-only)
      [[ -z "$mode" && -n "${2:-}" ]] || usage
      mode="--render-only"
      render_dir="$2"
      shift 2
      ;;
    --launchctl-bin)
      [[ -n "${2:-}" ]] || usage
      launchctl_bin="$2"
      shift 2
      ;;
    *) usage ;;
  esac
done
[[ -n "$mode" ]] || usage

script_dir="${0:A:h}"
repo="${script_dir:h}"
canonical_repo="/Users/edr/code/JouleWise"
template="$repo/configs/launchd/com.joulewise.magistrate.plist.template"
[[ -f "$template" ]] || { print "template not found: $template" >&2; exit 2; }
/usr/bin/grep -q "KeepAlive" "$template" && {
  print "template must not contain KeepAlive" >&2
  exit 3
}

label="com.joulewise.magistrate"
custody_root="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-$HOME/night-custody/magistrate}"
session_bin="${MAGISTRATE_SESSION_BIN:-/Users/edr/.local/bin/claude}"
path_value="$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
python_bin=""
if [[ "$mode" != "--uninstall" ]]; then
  python_command="$(command -v python3 || true)"
  [[ -n "$python_command" && -x "$python_command" ]] || {
    print "python3 executable not found" >&2
    exit 2
  }
  if [[ "$python_command" == "/usr/bin/python3" ]]; then
    print "unacceptable_system_python: /usr/bin/python3 does not carry the repository dependencies" >&2
    exit 3
  fi
  python_bin="$("$python_command" -c 'import sys; print(sys.executable)')"
  [[ "$python_bin" == /* && -x "$python_bin" ]] || {
    print "python3 did not report an executable absolute sys.executable: $python_bin" >&2
    exit 2
  }
fi

if [[ "$mode" == "--install" ]]; then
  canonical_repo="${canonical_repo:A}"
  resolved_repo="${repo:A}"
  git_root="$(/usr/bin/git -C "$resolved_repo" rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$git_root" ]] && git_root="${git_root:A}"
  if [[ "$resolved_repo" != "$canonical_repo" || "$git_root" != "$canonical_repo" ]]; then
    print "noncanonical_checkout: --install requires $canonical_repo (script repo=$resolved_repo git root=${git_root:-unavailable})" >&2
    exit 3
  fi
fi

if [[ "$mode" != "--uninstall" ]]; then
  [[ -L "$session_bin" && -x "$session_bin" ]] || {
    print "session binary must be an executable symlink: $session_bin" >&2
    exit 2
  }
fi

adopt_pid=""
adopt_start=""
adopt_activation=""
adopt_version=""
if [[ "$mode" == "--install" ]]; then
  # File 15 row 10: the installing, Terminal-hosted magistrate is the one
  # exceptional pre-watchdog tree that the first supervisor must adopt.
  read -r adopt_pid adopt_start adopt_activation adopt_version < <(
    "$python_bin" - "$session_bin" <<'PY'
import os
import re
import subprocess
import sys
import time
import uuid

binary = sys.argv[1]
cursor = os.getppid()
candidates = []
while cursor > 1:
    def field(name):
        result = subprocess.run(
            ("/bin/ps", "-p", str(cursor), "-o", f"{name}="),
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    command = field("command")
    claude = re.search(r"(?:^|[/\s])claude(?:\s|$)", command, re.IGNORECASE)
    suffix = command[claude.end():] if claude is not None else ""
    headless = re.search(r"(?:^|\s)(?:-p|--print(?:\s|=|$))", suffix)
    if claude is not None and headless is None:
        candidates.append((cursor, " ".join(field("lstart").split())))
    parent = field("ppid")
    try:
        cursor = int(parent)
    except ValueError:
        break
if not candidates:
    raise SystemExit(
        "--install must be run by the current magistrate session so its tree can be adopted"
    )
pid, start = candidates[-1]
version = subprocess.run(
    (binary, "--version"),
    check=True,
    capture_output=True,
    text=True,
    timeout=30,
).stdout.strip().replace(" ", "_")
activation = f"first-install-{int(time.time())}-{uuid.uuid4().hex[:12]}"
print(pid, start.replace(" ", "_"), activation, version)
PY
  )
  adopt_start="${adopt_start//_/ }"
  adopt_version="${adopt_version//_/ }"
  [[ -n "$adopt_pid" && -n "$adopt_start" && -n "$adopt_activation" ]] || {
    print "could not identify the installing magistrate process tree" >&2
    exit 3
  }
fi

if [[ "$mode" == "--render-only" ]]; then
  launch_dir="${render_dir:A}"
else
  launch_dir="$HOME/Library/LaunchAgents"
fi
plist="$launch_dir/$label.plist"
uid="$(id -u)"
plist_transaction_started=false
plist_existed=false
plist_backup=""
lock_seeded=false
lock_seed_snapshot=""

cleanup_failed_install() {
  local exit_code=$?
  trap - EXIT
  if (( exit_code != 0 )) && [[ "$mode" == "--install" && "$plist_transaction_started" == true ]]; then
    if [[ "$lock_seeded" == true && -n "$lock_seed_snapshot" && -f "$lock_seed_snapshot" && -f "$custody_root/magistrate.lock" ]] && \
        /usr/bin/cmp -s "$lock_seed_snapshot" "$custody_root/magistrate.lock"; then
      rm -f "$custody_root/magistrate.lock"
    fi
    if [[ "$plist_existed" == true && -n "$plist_backup" && -f "$plist_backup" ]]; then
      if ! /bin/mv -f "$plist_backup" "$plist"; then
        print "failed to restore pre-install plist: $plist" >&2
      fi
    else
      rm -f "$plist"
    fi
  fi
  [[ -z "$plist_backup" || ! -e "$plist_backup" ]] || rm -f "$plist_backup"
  [[ -z "$lock_seed_snapshot" || ! -e "$lock_seed_snapshot" ]] || rm -f "$lock_seed_snapshot"
  exit "$exit_code"
}
trap cleanup_failed_install EXIT

if [[ "$mode" == "--uninstall" ]]; then
  if [[ "$launchctl_bin" != */* ]]; then
    launchctl_bin="$(command -v "$launchctl_bin" || true)"
  fi
  [[ -n "$launchctl_bin" && -x "$launchctl_bin" ]] || {
    print "launchctl executable not found" >&2
    exit 2
  }
  "$launchctl_bin" bootout "gui/$uid/$label" 2>/dev/null || true
  rm -f "$plist"
  print "uninstalled $label"
  exit 0
fi

mkdir -p "$launch_dir"
if [[ "$mode" == "--install" ]]; then
  mkdir -p "$custody_root"
  if [[ -e "$plist" ]]; then
    plist_backup="$(mktemp "$launch_dir/.${label}.plist.rollback.XXXXXX")"
    /bin/cp -p "$plist" "$plist_backup"
    plist_existed=true
  fi
  plist_transaction_started=true
fi

"$python_bin" - "$template" "$plist" "$canonical_repo" "$custody_root" "$session_bin" "$path_value" "$python_bin" <<'PY'
from pathlib import Path
import sys
from xml.sax.saxutils import escape

template, output, repo, custody, session_bin, path_value, python_bin = sys.argv[1:]
replacements = {
    "@@REPO@@": repo,
    "@@CUSTODY_ROOT@@": custody,
    "@@SESSION_BIN@@": session_bin,
    "@@PATH@@": path_value,
}
text = Path(template).read_text(encoding="utf-8")
for old, new in replacements.items():
    text = text.replace(old, escape(new))
interpreter_pair = "    <string>/usr/bin/env</string>\n    <string>python3</string>"
if text.count(interpreter_pair) != 1:
    raise SystemExit("template interpreter pair is missing or duplicated")
text = text.replace(interpreter_pair, f"    <string>{escape(python_bin)}</string>")
if "@@" in text:
    raise SystemExit("unresolved template token")
Path(output).write_text(text, encoding="utf-8")
PY
/usr/bin/plutil -lint "$plist"

if [[ "$mode" == "--render-only" ]]; then
  print "rendered $plist"
  exit 0
fi

lock_seed_snapshot="$(mktemp "$custody_root/.magistrate.lock.seed.XXXXXX")"
"$python_bin" - "$custody_root/magistrate.lock" "$lock_seed_snapshot" "$adopt_pid" "$adopt_start" "$adopt_activation" "$session_bin" "$adopt_version" <<'PY'
import json
import os
import sys
import time

path, snapshot, pid, start, activation, binary, version = sys.argv[1:]
record = {
    "schema": "joulewise.magistrate_lock.v1",
    "activation_id": activation,
    "pid": int(pid),
    "start_time": start,
    "supervisor_pid": None,
    "launch_epoch_s": time.time(),
    "binary_symlink": binary,
    "binary_version": version,
    "status": "ACTIVE",
    "first_install_adoption": True,
}
data = (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")
with open(snapshot, "wb") as stream:
    stream.write(data)
    stream.flush()
    os.fsync(stream.fileno())
descriptor = None
try:
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    offset = 0
    while offset < len(data):
        offset += os.write(descriptor, data[offset:])
    os.fsync(descriptor)
except BaseException:
    if descriptor is not None:
        stat = os.fstat(descriptor)
        try:
            current = os.stat(path, follow_symlinks=False)
            if (current.st_dev, current.st_ino) == (stat.st_dev, stat.st_ino):
                os.unlink(path)
        except FileNotFoundError:
            pass
    raise
finally:
    if descriptor is not None:
        os.close(descriptor)
PY
lock_seeded=true

if [[ "$launchctl_bin" != */* ]]; then
  launchctl_bin="$(command -v "$launchctl_bin" || true)"
fi
[[ -n "$launchctl_bin" && -x "$launchctl_bin" ]] || {
  print "launchctl executable not found" >&2
  exit 2
}
launchctl_bin="${launchctl_bin:A}"
"$launchctl_bin" bootout "gui/$uid/$label" 2>/dev/null || true
if ! "$launchctl_bin" bootstrap "gui/$uid" "$plist"; then
  print "failed to bootstrap $label" >&2
  exit 3
fi
if ! "$launchctl_bin" print "gui/$uid/$label"; then
  "$launchctl_bin" bootout "gui/$uid/$label" 2>/dev/null || true
  print "launch agent verification failed; rolled back $label" >&2
  exit 3
fi
trap - EXIT
[[ -z "$plist_backup" || ! -e "$plist_backup" ]] || rm -f "$plist_backup"
[[ -z "$lock_seed_snapshot" || ! -e "$lock_seed_snapshot" ]] || rm -f "$lock_seed_snapshot"
print "installed and verified $label"
