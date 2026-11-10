#!/bin/bash
# hostlink_setup.sh: one-time setup so the M4 Air and the MBP can reach each other
# without anyone at either machine. Run once on EACH Mac, as the logged-in user, with sudo:
#
#   sudo bash hostlink_setup.sh air  [--nopasswd-sudo] [--wired] [--key-only]
#   sudo bash hostlink_setup.sh mbp  [--nopasswd-sudo] [--wired] [--key-only]
#
# What it does. Each step is idempotent, prints OK/WARN/FAIL, and later steps still run:
#   1. Firewall: stays on with stealth mode, but stops blocking ALL incoming
#      connections. Apple-signed built-in services are allowed, and sshd and
#      screensharing are allowed explicitly.
#   2. sshd: no root login, keepalives; --key-only disables password authentication
#      ONLY after the operator has verified peer key access in both directions
#      (/etc/ssh/sshd_config.d/010-jw-hostlink.conf, checked with `sshd -t`).
#   3. Adds the peer's public key to the user's ~/.ssh/authorized_keys. The Air's key
#      is built in; the MBP's key is pulled by the Air over SSH once step 4 is live.
#   4. Turns Remote Login (sshd) on and checks that port 22 is listening.
#   5. Creates an ed25519 key for the user if there is none, and prints the public half.
#   6. Power, on AC only: never system-sleep (displays may still sleep), wake for
#      network access, restart after a power loss.
#   7. --wired: static IPs on Thunderbolt Bridge (air 10.77.0.1, mbp 10.77.0.2), so a
#      USB-C/Thunderbolt cable between the Macs is a path that does not depend on Wi-Fi.
#   8. --nopasswd-sudo: /etc/sudoers.d/jw-hostlink-<user> (NOPASSWD: ALL for this
#      user, checked with visudo). This lets the agent fix things that need root without you.
#   9. Reports whether Screen Sharing is listening. Turning it ON is a System Settings
#      click; macOS does not allow it from a script.
set -u
export LC_ALL=C
# Keep root's executable search path independent of the invoking user's PATH.
PATH=/usr/bin:/bin:/usr/sbin:/sbin
umask 077
ROLE=${1:-}; shift || true
NOPASSWD=0; WIRED=0; KEY_ONLY=0
for a in "$@"; do case $a in --nopasswd-sudo) NOPASSWD=1;; --wired) WIRED=1;; --key-only) KEY_ONLY=1;; *) echo "unknown option $a"; exit 2;; esac; done
[[ $ROLE == air || $ROLE == mbp ]] || { echo "usage: sudo bash $0 air|mbp [--nopasswd-sudo] [--wired] [--key-only]"; exit 2; }
[[ $(id -u) == 0 ]] || { echo "run with sudo"; exit 2; }
U=${SUDO_USER:-}; [[ -n $U && $U != root ]] || { echo "run via sudo from the normal user account"; exit 2; }
[[ $U =~ ^[a-zA-Z_][a-zA-Z0-9_-]*$ ]] || { echo "unsafe account name"; exit 2; }
UH=$(/usr/bin/dscl . -read "/Users/$U" NFSHomeDirectory | /usr/bin/sed -n 's/^NFSHomeDirectory: //p')
[[ $UH == /* && $UH != / && -d $UH ]] || { echo "cannot resolve a safe home directory for $U"; exit 2; }
WORK=$(/usr/bin/mktemp -d /private/tmp/jw-hostlink.XXXXXX) || exit 1
trap '/bin/rm -rf "$WORK"' EXIT
trap 'exit 1' HUP INT TERM
AIR_KEY='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFYGhQ31kwQtg1BfCqRz4hk1laHwCPz46cu1Qzn7Soz1 edr@Edrs-MacBook-Air.local'
FAILS=0
ok()   { echo "OK    $*"; }
warn() { echo "WARN  $*"; }
fail() { echo "FAIL  $*"; FAILS=$((FAILS+1)); }
listening() { /usr/sbin/lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }

echo "== hostlink setup: role=$ROLE user=$U home=$UH host=$(/usr/sbin/scutil --get LocalHostName) $(/bin/date)"

# 1. Firewall
F=/usr/libexec/ApplicationFirewall/socketfilterfw
$F --setglobalstate on >/dev/null
$F --setblockall off >/dev/null
$F --setstealthmode on >/dev/null
$F --setallowsigned on >/dev/null
for app in /usr/sbin/sshd /usr/libexec/sshd-keygen-wrapper \
  /System/Library/CoreServices/RemoteManagement/screensharingd.bundle/Contents/MacOS/screensharingd; do
  [[ -e $app ]] && { $F --add "$app" >/dev/null 2>&1; $F --unblockapp "$app" >/dev/null 2>&1; }
done
if $F --getblockall | /usr/bin/grep -q 'blocking all'; then fail "firewall still blocks all incoming"; else ok "firewall: on, stealth, block-all off, sshd/screensharing allowed"; fi

# 2. sshd. 010 sorts before Apple's 100-macos.conf and the offload Match.
# Stage OUTSIDE the Include wildcard (which also matches *.new and *.bak).
# Check the effective values too: an earlier drop-in can win even when -t passes.
D=/etc/ssh/sshd_config.d; C=$D/010-jw-hostlink.conf
install_sshd() {
  /usr/bin/grep -Eq '^Include[[:space:]]+/etc/ssh/sshd_config.d/\*[[:space:]]*$' /etc/ssh/sshd_config || {
    fail "sshd Include is nonstandard; leaving configuration unchanged"; return;
  }
  /bin/mkdir -p "$D" "$WORK/sshd" || { fail "sshd staging directory"; return; }
  for entry in "$D"/*; do
    [[ -e $entry && $entry != "$C" ]] || continue
    /bin/ln -s "$entry" "$WORK/sshd/${entry##*/}" || { fail "sshd staging link"; return; }
  done
  /bin/cat > "$WORK/sshd/010-jw-hostlink.conf" <<'EOF'
# jw hostlink: retain existing password policy unless --key-only was requested.
PermitRootLogin no
PubkeyAuthentication yes
ClientAliveInterval 30
ClientAliveCountMax 4
EOF
  if [[ $KEY_ONLY == 1 ]]; then
    printf '%s\n' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' >> "$WORK/sshd/010-jw-hostlink.conf"
  else
    warn "password policy preserved; use --key-only only AFTER verified key logins both ways"
  fi
  /usr/bin/sed "s|^Include[[:space:]]*/etc/ssh/sshd_config.d/\\*[[:space:]]*$|Include $WORK/sshd/*|" \
    /etc/ssh/sshd_config > "$WORK/sshd_config" || { fail "sshd staging config"; return; }
  if ! /usr/sbin/sshd -t -f "$WORK/sshd_config" 2> "$WORK/sshd.err"; then
    fail "sshd candidate invalid: $(/bin/cat "$WORK/sshd.err"); old config retained"; return
  fi
  if ! /usr/sbin/sshd -T -f "$WORK/sshd_config" -C "user=$U,host=hostlink,addr=127.0.0.1" > "$WORK/effective" 2> "$WORK/sshd.err"; then
    fail "cannot inspect sshd candidate; old config retained"; return
  fi
  for setting in 'permitrootlogin no' 'pubkeyauthentication yes' 'clientaliveinterval 30' 'clientalivecountmax 4'; do
    /usr/bin/grep -qxF "$setting" "$WORK/effective" || { fail "sshd policy shadowed: $setting; old config retained"; return; }
  done
  if [[ $KEY_ONLY == 1 ]]; then
    for setting in 'passwordauthentication no' 'kbdinteractiveauthentication no'; do
      /usr/bin/grep -qxF "$setting" "$WORK/effective" || { fail "sshd policy shadowed: $setting; old config retained"; return; }
    done
  fi
  # Preserve the old file for post-install validation failures, including reruns.
  HAD_CONFIG=0
  if [[ -e $C ]]; then
    /bin/cp -p "$C" "$WORK/previous-sshd" || { fail "sshd backup"; return; }
    HAD_CONFIG=1
  fi
  /bin/chmod 0644 "$WORK/sshd/010-jw-hostlink.conf" &&
    /usr/sbin/chown root:wheel "$WORK/sshd/010-jw-hostlink.conf" &&
    /bin/mv -f "$WORK/sshd/010-jw-hostlink.conf" "$C" || { fail "sshd install"; return; }
  if /usr/sbin/sshd -t 2> "$WORK/sshd.err"; then
    ok "sshd config valid; effective hostlink settings checked ($C)"
  else
    if [[ $HAD_CONFIG == 1 ]]; then /bin/mv -f "$WORK/previous-sshd" "$C"; else /bin/rm -f "$C"; fi
    fail "sshd validation failed; restored prior config: $(/bin/cat "$WORK/sshd.err")"
  fi
}
install_sshd

# 3. authorized_keys
S=$UH/.ssh; AK=$S/authorized_keys
# Do not follow a user's symlink as root when changing ownership/permissions.
if [[ -L $S || -L $AK ]]; then
  fail "symlink at $S or $AK; leaving keys unchanged"
elif /usr/bin/sudo -u "$U" /bin/mkdir -p "$S" && /bin/chmod 700 "$S" &&
     /usr/bin/sudo -u "$U" /usr/bin/touch "$AK" && /bin/chmod 600 "$AK" &&
     /usr/sbin/chown "$U" "$S" "$AK"; then
  if [[ $ROLE == mbp ]]; then
    if /usr/bin/grep -qF "${AIR_KEY% *}" "$AK"; then
      ok "Air key already present (verify an actual login)"
    elif printf '\n%s\n' "$AIR_KEY" >> "$AK"; then
      ok "Air key added to $AK"
    else fail "could not authorize Air key"; fi
  else
    warn "Air still needs the MBP public key in $AK; setup alone is not bidirectional"
  fi
else fail "could not prepare $AK"; fi

# 4. Remote Login
if ! listening 22; then
  /usr/sbin/systemsetup -setremotelogin on >/dev/null 2>&1 || true
  if ! listening 22; then /bin/launchctl enable system/com.openssh.sshd 2>/dev/null; /bin/launchctl bootstrap system /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || /bin/launchctl kickstart -k system/com.openssh.sshd 2>/dev/null; fi
  /bin/sleep 2
fi
if listening 22; then ok "Remote Login on (port 22 listening)"; else fail "Remote Login not listening: turn it on in System Settings > General > Sharing > Remote Login"; fi

# 5. own key
if [[ -L $S ]]; then fail "refusing key generation through symlink $S"; elif [[ ! -f $S/id_ed25519 ]]; then /usr/bin/sudo -u "$U" /usr/bin/ssh-keygen -q -t ed25519 -N '' -C "$U@$(/usr/sbin/scutil --get LocalHostName).local" -f "$S/id_ed25519" && ok "generated $S/id_ed25519" || fail "own SSH key generation"; fi
[[ -f $S/id_ed25519.pub ]] && echo "      this Mac's public key: $(/bin/cat "$S/id_ed25519.pub")"

# 6. power on AC
/usr/bin/pmset -c sleep 0 womp 1 tcpkeepalive 1 >/dev/null && /usr/bin/pmset -a autorestart 1 >/dev/null && ok "power (AC): no system sleep, wake-on-network, autorestart after power loss" || fail "pmset"

# 7. wired fallback
if [[ $WIRED == 1 ]]; then
  IP=10.77.0.1; [[ $ROLE == mbp ]] && IP=10.77.0.2
  if /usr/sbin/networksetup -setmanual "Thunderbolt Bridge" $IP 255.255.255.0 2>/dev/null; then ok "Thunderbolt Bridge static $IP/24 (cable path)"; else fail "Thunderbolt Bridge service not found"; fi
fi

# 8. passwordless sudo
if [[ $NOPASSWD == 1 ]]; then
  SF=/etc/sudoers.d/jw-hostlink-$U
  printf '%s ALL=(ALL) NOPASSWD: ALL\n' "$U" > $SF.new; /bin/chmod 0440 $SF.new
  if /usr/sbin/visudo -cf $SF.new >/dev/null; then /bin/mv $SF.new $SF; ok "passwordless sudo for $U ($SF)"; else /bin/rm -f $SF.new; fail "sudoers drop-in failed visudo"; fi
fi

# 9. screen sharing
if listening 5900; then ok "Screen Sharing listening on 5900"; else warn "Screen Sharing OFF: System Settings > General > Sharing > Screen Sharing (on)"; fi

echo "== done: $FAILS failure(s). Hostname: $(/usr/sbin/scutil --get LocalHostName).local  Wi-Fi IP: $(/usr/sbin/ipconfig getifaddr en0 2>/dev/null)"
exit $((FAILS>0))
