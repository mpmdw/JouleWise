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
QUIET_GUARD_SHA256="b27f6d4438cfd7b4e564b2620f92500c6677138b5e2481103266e253bf472120"
QUIET_GUARD_PROCESS_SHA256="5ac34ec9f1873858957d4d26fee87332053749576006b3c6e4d1db43e865b4ef"
QUIET_GUARD_PRIVILEGED_SHA256="94c6d10d39fabe5d5b70ff9df18ee3cc2ce89d66231d2fa485cbb88873f45116"

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

# A cached timestamp may never authorize repository bytes for root execution.
# Invalidate it first, then require a fresh interactive operator grant.
/usr/bin/sudo -k
/usr/bin/sudo -v

# Copy every mutable repository input exactly once into a root-owned staging
# directory.  Validation and installation below both consume these same
# operator-nonwritable bytes; no repository path is re-read after validation.
STAGE_ROOT=$(/usr/bin/sudo /usr/bin/mktemp -d "/private/tmp/joulewise-quiet-guard-root.XXXXXX")
cleanup() {
  if [ -n "${STAGE_ROOT:-}" ]; then
    /usr/bin/sudo /bin/rm -R -- "$STAGE_ROOT"
  fi
}
trap cleanup EXIT HUP INT TERM

/usr/bin/sudo /usr/bin/install -d -o root -g wheel -m 0700 "$STAGE_ROOT/joulewise"
/usr/bin/sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/joulewise/quiet_guard.py" "$STAGE_ROOT/joulewise/quiet_guard.py"
/usr/bin/sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/joulewise/quiet_guard_process.py" "$STAGE_ROOT/joulewise/quiet_guard_process.py"
/usr/bin/sudo /usr/bin/install -o root -g wheel -m 0600 \
  "$REPO_ROOT/scripts/quiet_guard_privileged.py" "$STAGE_ROOT/quiet_guard_privileged.py"

RECOVERY_ACK="I acknowledge quiet-guard recovery and exact-identity abandonment"
/usr/bin/sudo /usr/bin/python3 -I -S -c '
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

# Authenticate the exact root-staged bytes against review-pinned SHA-256
# digests, then parse those same bytes without import or bytecode writes.
/usr/bin/sudo /usr/bin/python3 -I -S -B -c '
import ast, hashlib, hmac, pathlib, sys
arguments = sys.argv[1:]
if len(arguments) % 2:
    raise SystemExit("path/digest pairs required")
for offset in range(0, len(arguments), 2):
    path = pathlib.Path(arguments[offset])
    expected = arguments[offset + 1]
    payload = path.read_bytes()
    observed = hashlib.sha256(payload).hexdigest()
    if not hmac.compare_digest(observed, expected):
        raise SystemExit(f"reviewed-artifact digest mismatch: {path.name}")
    ast.parse(payload, filename=str(path))
' \
  "$STAGE_ROOT/joulewise/quiet_guard.py" "$QUIET_GUARD_SHA256" \
  "$STAGE_ROOT/joulewise/quiet_guard_process.py" "$QUIET_GUARD_PROCESS_SHA256" \
  "$STAGE_ROOT/quiet_guard_privileged.py" "$QUIET_GUARD_PRIVILEGED_SHA256"
/usr/bin/sudo /usr/sbin/visudo -cf "$STAGE_ROOT/joulewise-quiet-guard.sudoers"

# Refuse incompatible existing state using the authenticated staged engine.
# On a pristine host this validation-only pass does not create the state root
# or control.lock.  Installation revalidates below while holding that lock.
/usr/bin/sudo /usr/bin/python3 -I -S -B -c '
import sys
sys.path.insert(0, sys.argv[1])
from joulewise.quiet_guard import GuardEngine, PRODUCTION_STATE_ROOT
GuardEngine(PRODUCTION_STATE_ROOT).validate_inactive_installation(privileged_setup=True)
' "$STAGE_ROOT"

/usr/bin/sudo /usr/bin/install -d -o root -g wheel -m 0700 \
  "$STATE_ROOT" "$INSTALL_ROOT" "$CREDENTIAL_ROOT" "$INSTALL_ROOT/lib" "$LIB_ROOT"
/usr/bin/sudo /usr/bin/install -d -o root -g wheel -m 0755 /usr/local/libexec
/usr/bin/sudo /usr/bin/python3 -I -S -c '
import os, stat, sys
path = sys.argv[1]
row = os.lstat(path)
if not stat.S_ISDIR(row.st_mode) or stat.S_ISLNK(row.st_mode) or row.st_uid != 0 or row.st_mode & 0o022:
    raise SystemExit(f"unsafe root-helper parent: {path}")
' /usr/local/libexec

# No installed artifact is written unless the fresh inactive-state validation
# and every replacement occur beneath this same continuously held control.lock.
/usr/bin/sudo /usr/bin/python3 -I -S -B -c '
import subprocess, sys
sys.path.insert(0, sys.argv[1])
from joulewise.quiet_guard import GuardEngine, PRODUCTION_STATE_ROOT
stage_root, lib_root, helper, sudoers_path = sys.argv[1:5]
engine = GuardEngine(PRODUCTION_STATE_ROOT)
commands = (
    ("/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0644", "/dev/null", f"{lib_root}/__init__.py"),
    ("/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0644", f"{stage_root}/joulewise/quiet_guard.py", f"{lib_root}/quiet_guard.py"),
    ("/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0644", f"{stage_root}/joulewise/quiet_guard_process.py", f"{lib_root}/quiet_guard_process.py"),
    ("/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0755", f"{stage_root}/quiet_guard_privileged.py", helper),
    ("/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0440", f"{stage_root}/joulewise-quiet-guard.sudoers", sudoers_path),
)
with engine.inactive_installation_lock(privileged_setup=True):
    for command in commands:
        subprocess.run(command, check=True)
' "$STAGE_ROOT" "$LIB_ROOT" "$HELPER" "$SUDOERS_PATH"

# install-inactive is intentionally not in sudoers. Setup invokes it directly
# while authenticated; it writes live_promotion=false and no lease.
/usr/bin/sudo "$HELPER" install-inactive

echo "Quiet guard installed inactive for $OPERATOR (live_promotion=false)."
