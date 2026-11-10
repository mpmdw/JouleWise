#!/bin/bash
# hostlink_setup.sh: one-time setup so the M4 Air and the MBP can reach each other
# without anyone at either machine. Run once on EACH Mac, as the logged-in user, with sudo:
#
#   sudo bash hostlink_setup.sh air  [--nopasswd-sudo] [--wired]
#   sudo bash hostlink_setup.sh mbp  [--nopasswd-sudo] [--wired]
#
# What it does. Each step is idempotent, prints OK/WARN/FAIL, and later steps still run:
#   1. Firewall: stays on with stealth mode, but stops blocking ALL incoming
#      connections. Apple-signed built-in services are allowed, and sshd and
#      screensharing are allowed explicitly.
#   2. sshd: key-only authentication, no root login, keepalives
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
ROLE=${1:-}; shift || true
NOPASSWD=0; WIRED=0
for a in "$@"; do case $a in --nopasswd-sudo) NOPASSWD=1;; --wired) WIRED=1;; *) echo "unknown option $a"; exit 2;; esac; done
[[ $ROLE == air || $ROLE == mbp ]] || { echo "usage: sudo bash $0 air|mbp [--nopasswd-sudo] [--wired]"; exit 2; }
[[ $(id -u) == 0 ]] || { echo "run with sudo"; exit 2; }
U=${SUDO_USER:-}; [[ -n $U && $U != root ]] || { echo "run via sudo from the normal user account"; exit 2; }
UH=$(/usr/bin/dscl . -read "/Users/$U" NFSHomeDirectory | /usr/bin/awk '{print $2}')
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

# 2. sshd: key-only. The file name sorts before 050-jw-offload.conf (Match block), so these stay global.
D=/etc/ssh/sshd_config.d; C=$D/010-jw-hostlink.conf
/usr/bin/grep -q '^Include /etc/ssh/sshd_config.d/\*' /etc/ssh/sshd_config || warn "sshd_config has no sshd_config.d Include; drop-in will be ignored"
/bin/mkdir -p $D
/bin/cat > $C.new <<'EOF'
# jw hostlink (hostlink_setup.sh): key-only access between the JouleWise Macs
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
ClientAliveInterval 30
ClientAliveCountMax 4
EOF
/bin/chmod 0644 $C.new
/bin/mv $C.new $C
if /usr/sbin/sshd -t 2>/tmp/jw-sshd-t.err; then ok "sshd config valid ($C)"; else fail "sshd -t: $(/bin/cat /tmp/jw-sshd-t.err)"; /bin/rm -f $C; warn "removed $C to keep sshd startable"; fi

# 3. authorized_keys
S=$UH/.ssh; AK=$S/authorized_keys
/usr/bin/sudo -u "$U" /bin/mkdir -p "$S"; /bin/chmod 700 "$S"; /usr/bin/sudo -u "$U" /usr/bin/touch "$AK"; /bin/chmod 600 "$AK"; /usr/sbin/chown "$U" "$S" "$AK"
if [[ $ROLE == mbp ]]; then
  if /usr/bin/grep -qF "${AIR_KEY% *}" "$AK"; then ok "Air key already authorized"; else printf '%s\n' "$AIR_KEY" >> "$AK" && ok "Air key added to $AK"; fi
else
  ok "air role: MBP key will be added by the Air agent over SSH (no step needed here)"
fi

# 4. Remote Login
if ! listening 22; then
  /usr/sbin/systemsetup -setremotelogin on >/dev/null 2>&1 || true
  if ! listening 22; then /bin/launchctl enable system/com.openssh.sshd 2>/dev/null; /bin/launchctl bootstrap system /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || /bin/launchctl kickstart -k system/com.openssh.sshd 2>/dev/null; fi
  /bin/sleep 2
fi
if listening 22; then ok "Remote Login on (port 22 listening)"; else fail "Remote Login not listening: turn it on in System Settings > General > Sharing > Remote Login"; fi

# 5. own key
if [[ ! -f $S/id_ed25519 ]]; then /usr/bin/sudo -u "$U" /usr/bin/ssh-keygen -q -t ed25519 -N '' -C "$U@$(/usr/sbin/scutil --get LocalHostName).local" -f "$S/id_ed25519" && ok "generated $S/id_ed25519"; fi
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
