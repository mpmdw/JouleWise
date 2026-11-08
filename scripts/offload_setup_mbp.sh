#!/bin/bash
# One-time MBP setup for the MBP -> Air offload (docs/ops/AIR-OFFLOAD.md section 3). No sudo.
# Run by the magistrate on the MBP, outside any window:
#
#   bash scripts/offload_setup_mbp.sh --air-host Edrs-MacBook-Air.local --expect-fingerprint SHA256:...
#
# --expect-fingerprint is what Ed reads on the Air with: ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
# Idempotent: an existing key is kept; the known_hosts pin is written only when the fingerprint matches.
set -euo pipefail

KEY="$HOME/.ssh/jw_offload_ed25519"
KNOWN="$HOME/.ssh/jw_offload_known_hosts"
STATE="$HOME/code/CapstoneProject/jw-wt/offload-state"
AIR_HOST=""
EXPECT=""

die() { echo "offload_setup_mbp: $*" >&2; exit 1; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    --air-host) AIR_HOST="$2"; shift 2 ;;
    --expect-fingerprint) EXPECT="$2"; shift 2 ;;
    --state-root) STATE="$2"; shift 2 ;;
    *) die "unknown argument $1" ;;
  esac
done
[[ $EUID -ne 0 ]] || die "do not run as root"
[[ -n "$AIR_HOST" ]] || die "--air-host is required"

/usr/bin/install -d -m 0700 "$HOME/.ssh"
if [[ ! -f "$KEY" ]]; then
  /usr/bin/ssh-keygen -q -t ed25519 -N '' -C jw-offload-mbp -f "$KEY"
fi
/bin/chmod 0600 "$KEY"

if [[ -n "$EXPECT" ]]; then
  scan="$(/usr/bin/mktemp)"
  trap '/bin/rm -f "$scan"' EXIT
  /usr/bin/ssh-keyscan -T 10 -t ed25519 "$AIR_HOST" 2>/dev/null > "$scan"
  got="$(/usr/bin/ssh-keygen -lf "$scan" | /usr/bin/awk '{print $2}')"
  [[ "$got" == "$EXPECT" ]] || die "host key fingerprint $got does not match the expected $EXPECT; nothing pinned"
  /bin/cp "$scan" "$KNOWN.new"
  /bin/chmod 0644 "$KNOWN.new"
  /bin/mv "$KNOWN.new" "$KNOWN"
  echo "pinned $AIR_HOST $got in $KNOWN"
else
  echo "no --expect-fingerprint: host key NOT pinned yet (run again with it)"
fi

/bin/mkdir -p "$STATE"
echo "state root: $STATE"
echo "carry this public key to the Air (offload_setup_air.sh --mbp-pubkey):"
/bin/cat "$KEY.pub"
