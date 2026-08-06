#!/bin/sh
# One-time interactive installer for the deliberately inactive quiet guard.
# This is the only repository artifact permitted to invoke interactive sudo.
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
STATE_ROOT="/Library/Application Support/JouleWise/quiet-guard"
INSTALL_ROOT="/Library/Application Support/JouleWise/quiet-guard-install"
CREDENTIAL_ROOT="/Library/Application Support/JouleWise/quiet-guard-credentials"
LIB_ROOT="$INSTALL_ROOT/lib/joulewise"
HELPER="/usr/local/libexec/joulewise-quiet-guard"
SUDOERS_PATH="/etc/sudoers.d/joulewise-quiet-guard"

if [ "$(id -u)" -eq 0 ]; then
  echo "Run this setup as the intended unprivileged operator, not as root." >&2
  exit 2
fi

OPERATOR=$(id -un)
case "$OPERATOR" in
  *[!A-Za-z0-9._-]*|'')
    echo "Unsupported operator account name." >&2
    exit 2
    ;;
esac

# The operator explicitly authenticates once. Every installed runtime route is
# then sudo -n through one fixed helper and the two aliases above.
sudo -v

# Copy every mutable repository input exactly once into a root-owned staging
# directory.  Validation and installation below both consume these same
# operator-nonwritable bytes; no repository path is re-read after validation.
STAGE_ROOT=$(sudo /usr/bin/mktemp -d "/private/tmp/joulewise-quiet-guard-root.XXXXXX")
cleanup() {
  if [ -n "${STAGE_ROOT:-}" ]; then
    sudo /bin/rm -R -- "$STAGE_ROOT"
  fi
}
trap cleanup EXIT HUP INT TERM

sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/joulewise/quiet_guard.py" "$STAGE_ROOT/quiet_guard.py"
sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/joulewise/quiet_guard_process.py" "$STAGE_ROOT/quiet_guard_process.py"
sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/scripts/quiet_guard_privileged.py" "$STAGE_ROOT/quiet_guard_privileged.py"

RECOVERY_ACK="I acknowledge quiet-guard recovery and exact-identity abandonment"
sudo /usr/bin/python3 -I -c '
import os, sys
path, helper, operator, acknowledgment = sys.argv[1:]
escaped = acknowledgment.replace("\\", "\\\\").replace(" ", "\\ ")
payload = (
    f"Cmnd_Alias JOULEWISE_QUIET_GUARD_STATUS = {helper} status\n"
    f"Cmnd_Alias JOULEWISE_QUIET_GUARD_RECOVER = {helper} recover --ack {escaped}\n"
    f"{operator} ALL=(root) NOPASSWD: JOULEWISE_QUIET_GUARD_STATUS, JOULEWISE_QUIET_GUARD_RECOVER\n"
).encode("utf-8")
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "wb") as handle:
    handle.write(payload)
    handle.flush()
    os.fsync(handle.fileno())
' "$STAGE_ROOT/joulewise-quiet-guard.sudoers" "$HELPER" "$OPERATOR" "$RECOVERY_ACK"

# Parse the staged Python bytes without importing or writing bytecode, and
# validate the exact staged sudoers bytes that will be installed.
for staged in \
  "$STAGE_ROOT/quiet_guard.py" \
  "$STAGE_ROOT/quiet_guard_process.py" \
  "$STAGE_ROOT/quiet_guard_privileged.py"
do
  sudo /usr/bin/python3 -I -B -c 'import ast, pathlib, sys; ast.parse(pathlib.Path(sys.argv[1]).read_text())' "$staged"
done
sudo /usr/sbin/visudo -cf "$STAGE_ROOT/joulewise-quiet-guard.sudoers"

sudo /usr/bin/install -d -o root -g wheel -m 0700 \
  "$STATE_ROOT" "$INSTALL_ROOT" "$CREDENTIAL_ROOT" "$INSTALL_ROOT/lib" "$LIB_ROOT"
sudo /usr/bin/install -d -o root -g wheel -m 0755 /usr/local/libexec
sudo /usr/bin/python3 -I -c '
import os, stat, sys
path = sys.argv[1]
row = os.lstat(path)
if not stat.S_ISDIR(row.st_mode) or stat.S_ISLNK(row.st_mode) or row.st_uid != 0 or row.st_mode & 0o022:
    raise SystemExit(f"unsafe root-helper parent: {path}")
' /usr/local/libexec
sudo /usr/bin/install -o root -g wheel -m 0644 /dev/null "$LIB_ROOT/__init__.py"
sudo /usr/bin/install -o root -g wheel -m 0644 \
  "$STAGE_ROOT/quiet_guard.py" "$LIB_ROOT/quiet_guard.py"
sudo /usr/bin/install -o root -g wheel -m 0644 \
  "$STAGE_ROOT/quiet_guard_process.py" "$LIB_ROOT/quiet_guard_process.py"
sudo /usr/bin/install -o root -g wheel -m 0755 \
  "$STAGE_ROOT/quiet_guard_privileged.py" "$HELPER"

sudo /usr/bin/install -o root -g wheel -m 0440 \
  "$STAGE_ROOT/joulewise-quiet-guard.sudoers" "$SUDOERS_PATH"

# install-inactive is intentionally not in sudoers. Setup invokes it directly
# while authenticated; it writes live_promotion=false and no lease.
sudo "$HELPER" install-inactive

echo "Quiet guard installed inactive for $OPERATOR (live_promotion=false)."
