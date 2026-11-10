# Hostlink: Air and MBP reachable from each other without Ed at either machine

Do these steps once, at the machines. Afterwards the agent on the Air can reach the MBP itself:
- **SSH**, the primary path: over the Thunderbolt cable, by Bonjour name or by fixed IP, whichever answers first.
- **Screen Sharing**, the GUI fallback.
- **Claude desktop computer use**, for GUI work.

With passwordless sudo it can also fix root-level problems without Ed.

## At the MBP (about 5 min)

1. Get the script without moving the canonical root:
   ```
   gh api 'repos/mpmdw/JouleWise/contents/scripts/hostlink/hostlink_setup.sh?ref=ops/2026-11-10-hostlink' -H 'Accept: application/vnd.github.raw' > /private/tmp/hostlink_setup.sh
   sudo bash /private/tmp/hostlink_setup.sh mbp --nopasswd-sudo --wired
   ```
   Drop `--nopasswd-sudo` if you don't want the agent to have root without a password. Drop `--wired` if no cable will join the Macs.
2. Check that every line reads `OK`. If Remote Login says FAIL, go to System Settings > General > Sharing, turn on Remote Login, and run the script again.
3. GUI steps that macOS only allows by hand. All of them are in System Settings > Privacy & Security:
   - **Accessibility:** add Terminal and Claude.
   - **Screen & System Audio Recording:** add Terminal and Claude.
   - **Full Disk Access:** add Terminal, and `sshd-keygen-wrapper` if it is listed. Optional: General > Sharing > Remote Login > (i) > "Allow full disk access for remote users".
   - **Claude desktop app:** Settings > Computer use > on.
4. In the Google Home app on your phone, reserve the MBP's and the Air's current IPs (Wi-Fi > Devices > the Mac > Reserve IP).

## At the Air (about 3 min)

```
sudo bash /Users/edr/code/CapstoneProject/jw-wt/hostlink/scripts/hostlink/hostlink_setup.sh air --nopasswd-sudo --wired
```
Then do the same GUI steps as MBP step 3, and Screen Sharing on (System Settings > General > Sharing).
Also still pending from 11-08: `sudo bash scripts/offload_setup_air.sh` (on the `ops/2026-11-08-air-offload-merged` branch).

## The agent does the rest over SSH once the MBP setup is done

- Pulls the MBP's public key into the Air's `authorized_keys`, which makes access both ways.
- Writes the MBP's `~/.ssh/config` entries for `air`, `air-lan`, `air-ip` and `air-wired`, and installs `jwssh` on both Macs.
- Runs the R1 unstrand: it checks the night markers by existence only, uninstalls the two night agents, then watches the watchdog relaunch a magistrate.
- Installs a link-health watcher on the Air that alarms if every path to the MBP fails. It does not probe during an armed span.

## Rules after setup

- No interactive SSH session on the MBP during an armed measurement span, except an emergency stop. The agent census treats it like any other agent.
- The firewall stays on with stealth mode. Only built-in signed services, sshd and Screen Sharing accept incoming connections.
- Password SSH is off on both Macs. Key-only.
