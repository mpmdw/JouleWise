#!/bin/bash
# One-time Air setup for the MBP -> Air offload (docs/ops/AIR-OFFLOAD.md section 3).
# Run by Ed on the Air, from a checkout pinned at the REVIEWED sha of this branch:
#
#   sudo bash scripts/offload_setup_air.sh --mbp-pubkey /path/jw_offload_ed25519.pub --mbp-from 192.168.1.23
#
# Idempotent: every step checks first and changes only what differs. Re-run it after a reviewed
# update of scripts/offload_window.py to reinstall the root-owned copy.
# It never reads window data, never touches /Volumes/JW-EXT/backups contents (only its owner, and only
# if enabling ownership left it owned by _unknown), and installs nothing on the MBP.
set -euo pipefail

OWNER="${SUDO_USER:-}"
ACCOUNT=jw-offload
VOLUME=/Volumes/JW-EXT
STORE="$VOLUME/jw-offload"
ETC=/usr/local/etc/jw-offload
LIBEXEC=/usr/local/libexec/jw-offload
PY=/opt/homebrew/bin/python3.13
SSHD_SNIPPET=/etc/ssh/sshd_config.d/050-jw-offload.conf
CHECKOUT="$(cd "$(dirname "$0")/.." && pwd)"
MIN_FREE_GIB=100
PUBKEY=""
FROM=""

die() { echo "offload_setup_air: $*" >&2; exit 1; }
say() { echo "== $*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mbp-pubkey) PUBKEY="$2"; shift 2 ;;
    --mbp-from) FROM="$2"; shift 2 ;;      # MBP LAN address or CIDR; "any" omits from=
    --min-free-gib) MIN_FREE_GIB="$2"; shift 2 ;;
    *) die "unknown argument $1" ;;
  esac
done

[[ $EUID -eq 0 ]] || die "run with sudo"
[[ -n "$OWNER" && "$OWNER" != root ]] || die "run with sudo from Ed's own account (SUDO_USER is the iCloud user)"
[[ -f "$PUBKEY" ]] || die "--mbp-pubkey FILE is required (the MBP's jw_offload_ed25519.pub)"
[[ -n "$FROM" ]] || die "--mbp-from ADDRESS|CIDR|any is required"
grep -Eq '^ssh-ed25519 [A-Za-z0-9+/=]+( .*)?$' "$PUBKEY" || die "not a single ed25519 public key: $PUBKEY"
[[ $(wc -l < "$PUBKEY") -le 1 ]] || die "public key file has more than one line"
[[ -x "$PY" ]] || die "missing $PY"
[[ -x /opt/homebrew/bin/zstd ]] || die "missing /opt/homebrew/bin/zstd (brew install zstd)"
[[ -f "$CHECKOUT/scripts/offload_window.py" ]] || die "run from a JouleWise checkout"
grep -q '^Include /etc/ssh/sshd_config.d/\*' /etc/ssh/sshd_config || die "sshd_config lacks the sshd_config.d Include"
/sbin/mount | grep -q " on $VOLUME " || die "$VOLUME is not mounted"
# git as Ed: root would refuse a checkout it does not own (safe.directory).
CHECKOUT_SHA="$(/usr/bin/sudo -u "$OWNER" /usr/bin/git -C "$CHECKOUT" rev-parse HEAD)"
/usr/bin/sudo -u "$OWNER" /usr/bin/git -C "$CHECKOUT" diff --quiet HEAD -- scripts/offload_window.py \
  || die "scripts/offload_window.py differs from the checkout's HEAD; use the reviewed, clean checkout"
say "checkout $CHECKOUT at $CHECKOUT_SHA"

# 1. The volume honours ownership (otherwise every user sees every file as its own and the
#    account confinement is void), and Spotlight stays off.
info="$(/usr/sbin/diskutil info "$VOLUME")"
if grep -Eq 'Owners: +Disabled' <<<"$info"; then
  say "enabling ownership on $VOLUME"
  /usr/sbin/diskutil enableOwnership "$VOLUME"
fi
for path in "$VOLUME" "$VOLUME/backups"; do
  # Files written while ownership was ignored can show up as _unknown (uid 99) once it is enabled.
  if [[ -e "$path" && "$(/usr/bin/stat -f %u "$path")" == 99 ]]; then
    say "returning $path to $OWNER (it shows as _unknown after enableOwnership)"
    if [[ "$path" == "$VOLUME" ]]; then /usr/sbin/chown "$OWNER:staff" "$path"; else /usr/sbin/chown -R "$OWNER:staff" "$path"; fi
  fi
done
/usr/bin/mdutil -i off "$VOLUME" >/dev/null

# 2. The dedicated, non-admin, hidden account. Its shell runs only the forced command; its home is
#    root-owned so it cannot write rc files or keys.
if ! /usr/bin/id "$ACCOUNT" >/dev/null 2>&1; then
  say "creating account $ACCOUNT"
  /usr/sbin/sysadminctl -addUser "$ACCOUNT" -fullName "JouleWise offload" -shell /bin/sh \
    -home "/Users/$ACCOUNT" -password "$(/usr/bin/openssl rand -base64 33)" >/dev/null 2>&1
fi
/usr/bin/id "$ACCOUNT" >/dev/null || die "account $ACCOUNT was not created"
if /usr/sbin/dseditgroup -o checkmember -m "$ACCOUNT" admin >/dev/null 2>&1; then
  /usr/sbin/dseditgroup -o edit -d "$ACCOUNT" -t user admin
fi
/usr/bin/dscl . -create "/Users/$ACCOUNT" IsHidden 1
/usr/bin/dscl . -create "/Users/$ACCOUNT" UserShell /bin/sh
/bin/mkdir -p "/Users/$ACCOUNT"
/usr/sbin/chown root:wheel "/Users/$ACCOUNT"
/bin/chmod 0755 "/Users/$ACCOUNT"
if /usr/bin/dscl . -read /Groups/com.apple.access_ssh >/dev/null 2>&1; then
  /usr/sbin/dseditgroup -o edit -a "$ACCOUNT" -t user com.apple.access_ssh
fi

# 3. The gate script, root-owned and not writable by the account.
/usr/bin/install -d -o root -g wheel -m 0755 "$LIBEXEC" "$ETC"
/usr/bin/install -o root -g wheel -m 0755 "$CHECKOUT/scripts/offload_window.py" "$LIBEXEC/offload_window.py"
say "installed $LIBEXEC/offload_window.py sha256 $(/usr/bin/shasum -a 256 "$LIBEXEC/offload_window.py" | cut -d' ' -f1)"

# 4. The store, bound to the volume's APFS UUID (refuses an internal disk or a volume that ignores
#    ownership), then handed to the account. second/ belongs to the iCloud worker's user.
"$PY" -B "$LIBEXEC/offload_window.py" init-store --store-root "$STORE" --binding "$ETC/store-binding.json" \
  --role primary --min-free-gib "$MIN_FREE_GIB"
/usr/sbin/chown root:wheel "$ETC/store-binding.json" "$STORE/.jw-offload-store.json"
/bin/chmod 0644 "$ETC/store-binding.json" "$STORE/.jw-offload-store.json"
/usr/sbin/chown "$ACCOUNT:staff" "$STORE"
/bin/chmod 0750 "$STORE"
for sub in inbox windows queue locks; do
  /usr/bin/install -d -o "$ACCOUNT" -g staff -m 0750 "$STORE/$sub"
done
/usr/bin/install -d -o "$OWNER" -g staff -m 0755 "$STORE/second"

# 5. The MBP's key: one forced-command line, root-owned, outside the account's home.
FORCED="$PY -B $LIBEXEC/offload_window.py air-gate --binding $ETC/store-binding.json"
OPTIONS="restrict"
[[ "$FROM" == any ]] || OPTIONS="restrict,from=\"$FROM\""
LINE="$OPTIONS,command=\"$FORCED\" $(cat "$PUBKEY")"
printf '%s\n' "$LINE" > "$ETC/authorized_keys.new"
/usr/sbin/chown root:wheel "$ETC/authorized_keys.new"
/bin/chmod 0644 "$ETC/authorized_keys.new"
/bin/mv "$ETC/authorized_keys.new" "$ETC/authorized_keys"

# 6. sshd: a Match block for the account only (an included file's Match block ends with the file).
cat > "$SSHD_SNIPPET.new" <<EOF
# JouleWise MBP -> Air offload (docs/ops/AIR-OFFLOAD.md). Managed by scripts/offload_setup_air.sh.
Match User $ACCOUNT
    AuthenticationMethods publickey
    PubkeyAuthentication yes
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    AuthorizedKeysFile $ETC/authorized_keys
    ForceCommand $FORCED
    AllowTcpForwarding no
    AllowAgentForwarding no
    AllowStreamLocalForwarding no
    X11Forwarding no
    PermitTTY no
    PermitTunnel no
    PermitUserRC no
EOF
/usr/sbin/chown root:wheel "$SSHD_SNIPPET.new"
/bin/chmod 0644 "$SSHD_SNIPPET.new"
/bin/mv "$SSHD_SNIPPET.new" "$SSHD_SNIPPET"
if ! /usr/sbin/sshd -t; then
  /bin/rm -f "$SSHD_SNIPPET"
  die "sshd -t rejected the snippet; removed it"
fi
/usr/sbin/sshd -T -C "user=$ACCOUNT,host=mbp,addr=${FROM%/*}" 2>/dev/null | grep -Ei '^(forcecommand|authenticationmethods|permittty) ' || true

# 7. Stay awake on power (the display may sleep), so the MBP never finds the Air asleep in cool-down.
/usr/bin/pmset -c sleep 0 disksleep 0

# 8. The iCloud second-copy worker, as Ed (iCloud is per user), every 5 minutes, background priority.
AGENT="/Users/$OWNER/Library/LaunchAgents/com.joulewise.offload-icloud.plist"
LOGDIR="/Users/$OWNER/Library/Logs/jw-offload"
/usr/bin/install -d -o "$OWNER" -g staff -m 0755 "/Users/$OWNER/Library/LaunchAgents" "$LOGDIR"
cat > "$AGENT.new" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.joulewise.offload-icloud</string>
  <key>ProgramArguments</key><array>
    <string>$PY</string><string>-B</string><string>$LIBEXEC/offload_window.py</string>
    <string>air-icloud</string><string>--binding</string><string>$ETC/store-binding.json</string>
  </array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>LowPriorityIO</key><true/>
  <key>StandardOutPath</key><string>$LOGDIR/icloud.log</string>
  <key>StandardErrorPath</key><string>$LOGDIR/icloud.err</string>
</dict></plist>
EOF
/usr/bin/plutil -lint "$AGENT.new" >/dev/null
/usr/sbin/chown "$OWNER:staff" "$AGENT.new"
/bin/chmod 0644 "$AGENT.new"
/bin/mv "$AGENT.new" "$AGENT"
UID_OWNER="$(/usr/bin/id -u "$OWNER")"
/bin/launchctl bootout "gui/$UID_OWNER/com.joulewise.offload-icloud" 2>/dev/null || true
/bin/launchctl bootstrap "gui/$UID_OWNER" "$AGENT"

say "done. Still manual, once:"
echo "   - System Settings > General > Sharing > Remote Login: on, 'Only these users' includes $ACCOUNT."
echo "   - If 'hello' later fails with 'Operation not permitted' on $VOLUME, tick 'Allow full disk access for remote users' there."
echo "   - Read the host key fingerprint for the MBP pin: ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub"
echo "   - Pinned gate: $LIBEXEC/offload_window.py from $CHECKOUT_SHA"
