# Hostlink: Air and MBP access

Use the **reviewed local revision** of all three files in this directory. Local
review commits are not pushed automatically; downloading the old branch head
will not contain these fixes. Keep a local Terminal open on each Mac until the
peer has successfully logged in. Do setup outside an armed measurement span.

## Run locally on each Mac

From the reviewed checkout, as `edr`:

```bash
# MBP
sudo bash scripts/hostlink/hostlink_setup.sh mbp --nopasswd-sudo --wired
# Air (on the Air, from its copy of the reviewed checkout)
sudo bash scripts/hostlink/hostlink_setup.sh air --nopasswd-sudo --wired
```

`--nopasswd-sudo` intentionally grants **all root commands without a password**
to this user, including over SSH. Omit it if that authority is unnecessary.
`--wired` replaces the existing service named `Thunderbolt Bridge` with
10.77.0.1/24 on Air or 10.77.0.2/24 on MBP, without a router, and enables that
service. It does not create/rename services or change Wi-Fi, DNS or service order.
Use a Thunderbolt-capable cable; an ordinary USB-C charging cable is insufficient.
If the service is absent/renamed, inspect `networksetup -listnetworkserviceorder`
locally and resolve it in System Settings. Existing unrelated bridge use must be
resolved before assigning these addresses.

The script exits nonzero for any `FAIL`. Resolve every failure locally and read
all warnings. `WARN` about incomplete peer keys is expected on first setup.
A listening port is not proof of an authorized login. If Remote Login will not
start, use System Settings > General > Sharing > Remote Login. `systemsetup`
needs Full Disk Access on macOS 15; its launchctl fallback enables/bootstraps the
socket service without killing it, but cannot bypass user access controls.
Under Remote Login > Only these users, include `edr`, and `jw-offload` on Air
once installed. Do not switch to All users just to fix one missing account.

AC idle sleep is disabled. Wake/keepalive options depend on hardware support.
Keep AC connected and the lid open. This does not guarantee wake after lid
closure, battery exhaustion or FileVault preboot, and does not promise automatic
restart after power loss. Reserve Wi-Fi IPs in the router for the IP fallback.

## Complete keys and client aliases before hardening

The script adds the built-in Air public key to MBP. Verify it matches the Air's
actual `~/.ssh/id_ed25519.pub` locally. It creates a local ed25519 key only when
one is absent; it does **not** copy the MBP key into the Air. Copy only the MBP's
public key into Air's `~/.ssh/authorized_keys` as `edr`, keeping existing entries,
with a newline before the added entry. Never transfer a private key. Keep `.ssh`
at mode 700 and `authorized_keys` at 600, owned by `edr`.

Configure these aliases on the Air, substituting the MBP's actual Bonjour name
and reserved Wi-Fi address. Place this group before any existing matching
blocks that set the same options, especially `Host *`. Back up the old config.

```sshconfig
Host mbp mbp-lan mbp-ip mbp-wired
    User edr
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
Host mbp mbp-lan
    HostName REPLACE-MBP-BONJOUR.local
Host mbp-ip
    HostName REPLACE-MBP-WIFI-IP
Host mbp-wired
    HostName 10.77.0.2
```

On MBP, use the analogous `air air-lan air-ip air-wired` group, the Air's Bonjour
name and Wi-Fi address, and `10.77.0.1` for `air-wired`. The shared block may
come first **because it has no HostName**. OpenSSH keeps the first value for
each option across matching blocks; a shared HostName would shadow all later
per-alias addresses. Appending a group after conflicting existing settings also
fails. Inspect effective values locally before any connection:

```bash
ssh -G mbp-wired | awk '$1 ~ /^(hostname|user|identityfile|identitiesonly)$/ '
ssh -G mbp
ssh -G mbp-ip
# On MBP, substitute air aliases.
```

Verify each Mac's host-key fingerprint locally with
`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`. Make an initial interactive
SSH connection to every alias you will use, compare fingerprints with the peer's
local display, and accept only the matching key. Do not disable host-key checking.
Then prove key authentication explicitly, from Air to MBP and MBP to Air:

```bash
ssh -o BatchMode=yes -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no mbp true
ssh -o BatchMode=yes -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no mbp-wired true
# Repeat for mbp-ip, and on MBP for air, air-wired and air-ip.
```

Install `jwssh` in a directory on each user's PATH. It probes cable, Bonjour,
then Wi-Fi, using noninteractive authentication and bounded connect attempts.
A failed command is never retried on another path because it may already have
executed. It requires preinstalled aliases and trusted host keys.

Only after key logins succeed both ways, rerun each local setup command with
`--key-only`. This disables password and keyboard-interactive authentication
**globally for SSH users**. Confirm every other required SSH user has key access
first. Rerunning without this flag preserves any previous hostlink key-only
policy. Keep local recovery Terminals open until fresh peer logins still work.

## Offload and final acceptance

The reviewed offload setup on `ops/2026-11-08-air-offload-merged` requires
`--mbp-pubkey FILE --mbp-from ADDRESS|CIDR|any`; follow its own runbook rather
than running it without arguments. Its `050-jw-offload.conf` remains separate:
publickey only, forced command, root-owned authorized keys, no TTY/forwarding.
The hostlink `010` settings precede it and Apple's `100` defaults. Authentication
settings do not grant a regular shell to `jw-offload`. Keep its dedicated key
separate from `edr`'s key, and retain its source-address restriction.

With local access still available, check new logins both ways on all usable
paths, and `sudo -n true` if passwordless sudo was requested. On Air, inspect
`sudo /usr/sbin/sshd -T -C user=jw-offload,host=mbp,addr=MBP_SOURCE_IP` for its
forced command, authorized key path, authentication method and forwarding/TTY
restrictions. An actual offload handshake belongs to its owner-controlled gate;
this setup/review does not run it or read measurement data.

Screen Sharing is an optional GUI fallback: enable it in General > Sharing
and limit allowed users. Grant Accessibility, screen recording, or remote Full
Disk Access only when required for the intended GUI/data task. The firewall
allows built-in signed services and explicit SSH/Screen Sharing binaries; it
preserves existing downloaded-app and other application rules. It does not
claim those are the only allowed inbound apps.

Do not leave unattended until these live checks pass. No link watcher or night
agent change is installed by these scripts. Do not probe during an armed span.
