# Hostlink review — Sol — 2026-11-10

Verdict: **original revision HOLD; patched revision ready for an attended local
setup, with live acceptance still required before either Mac is left unattended.**
This is a static/non-root review, not proof of two-way hardware reachability.
Use the local review commits, not the unmodified remote branch download.

Reviewed baseline `f40cd519e` on the already-existing requested branch
`ops/2026-11-10-hostlink` (clean intake). Offload source read from local Git:
`origin/ops/2026-11-08-air-offload-merged` at
`b5af05e12a0407b11ace28a53431537a8341f882`, setup-script blob
`4a1f6276bc4dc24adc6d9a953b0957410f1eb432`. No fetch or other network request.

## Findings and disposition

1. **High — password hardening before proven access. Fixed.** The MBP peer key
   was added after password authentication was disabled; Air never receives the
   MBP key in this script. Default setup now retains the existing password policy;
   explicit `--key-only` is an operator step after fresh, password-disabled key
   logins both ways and verification of every other required SSH user. A rerun
   without the flag retains prior hostlink `PasswordAuthentication no` and
   `KbdInteractiveAuthentication no`. Offload remains independently key-only.
   Disabling these two methods does not disable ed25519/publickey authentication,
   including the Air's own key or offload's dedicated key. PAM/account access
   controls and Remote Login's allowed-users list still apply.

2. **High — unsafe SSH replacement and false assurance. Fixed.** Original code
   replaced the drop-in before validation and deleted it on failure, losing a
   previous working version. Its `.new` file was itself inside Apple's `Include
   /etc/ssh/sshd_config.d/*` wildcard. Candidates now live in private staging;
   a shadow include directory preserves filenames/order, `sshd -t` checks syntax,
   and `sshd -T -C` checks effective hostlink values before installation. Missing
   standard Include or shadowed policy fails without replacement. Post-install
   failure restores the prior bytes. The predictable shared `/tmp` error file
   was replaced with a private temporary directory. Interrupted/power-loss
   recovery was not exercised; this is not a transactional system installer.

3. **Ordering — baseline 010/050/100 order is correct, not a defect.** Includes
   expand lexically; 010 precedes offload's 050 and Apple's 100 defaults. Global
   first-value-wins means earlier custom settings can still defeat 010; syntax
   validation alone cannot detect that. Matching per-user settings can override
   global defaults. Native synthetic parser checks retained offload's publickey
   method, forced command, separate authorized-key path and all seven inspected
   TTY/forwarding/RC restrictions. No change to offload's script or Match block.

4. **Medium — firewall errors could be reported as success. Fixed.** The old
   grep only looked for `blocking all`; empty/error/unknown output fell through
   to OK even when setters failed or the firewall stayed off. On local macOS
   **15.7.9 (24G830)**, actual read-only output included:
   `Firewall has block all state set to disabled.` and
   `Firewall stealth mode is off`. Installed binary format strings/help confirm
   `Firewall is enabled. (State = 1)` and `Firewall stealth mode is on`.
   Setters and expected readbacks are now checked. `--setallowsigned on` covers
   built-in signed software; downloaded signed software uses the distinct
   `--setallowsignedapp` flag. Its existing value is preserved. Existing app
   exceptions are preserved too; the old runbook's claim that only the named
   services can receive connections was too strong. Earlier progress wording
   about a possible “not blocking all” match was hypothetical; that is not the
   actual disabled-state string observed here.

5. **Medium — Remote Login fallback and access checks. Fixed/documented.**
   Local systemsetup(8) explicitly requires Full Disk Access; sudo alone cannot
   guarantee success. `launchctl enable` plus bootstrap of an unloaded
   `system/com.openssh.sshd` socket service is consistent with launchctl(1) and
   Apple's installed ssh.plist. Removed `kickstart -k`, which kills a running
   instance and is inappropriate for this inetd-style socket service. Existing
   loaded services are left running. Port 22 is only a listener check; runbook
   requires `edr` and, on Air, `jw-offload` in the allowed-users list and real
   peer logins. FDA/TCC/MDM can still require local GUI intervention.

6. **Medium — AC power claims and wired arguments. Fixed.** `sleep`, `womp`,
   `tcpkeepalive`, `autorestart` are recognized pmset settings, but hardware
   capability matters. Local `pmset -g cap` advertises womp/tcpkeepalive and no
   autorestart; no M4 Air capability check was performed. Removed the unconditional
   `-a autorestart` (also contradicted AC-only scope), queried capabilities and
   applied supported options with `-c`. No guarantee against lid sleep or FileVault
   preboot. networksetup(8) requires the router argument to `-setmanual`; now
   supplies an empty router for the point-to-point subnet, enables an existing
   disabled bridge, and fails clearly for an absent/renamed service. The quoted
   English service name is valid only when that exact service exists. No automatic
   service creation, renaming, Wi-Fi/DNS changes or ordering changes. Empty-router
   behavior, actual link establishment and route effects still need the native
   attended setup; no network settings were mutated in review.

7. **Medium — sudoers install reliability. Fixed.** Original visudo-before-mv
   ordering was correct, but directory existence/include, root ownership, command
   failures and complete-policy validation were missing. Candidate `.new` stays
   outside includedir, is root:wheel/0440, and passes `visudo -cf` before moving.
   Existing and resulting full policy are checked; failure restores a prior rule.
   `NOPASSWD: ALL` is deliberately broad, explicitly requested by the flag, and
   documented as full remote root authority. Parser success alone does not prove
   a later rule cannot override it: operator must verify `sudo -n true`.

8. **Medium — shell/key/client pitfalls. Fixed.** Failed/space-containing home
   lookup no longer becomes a write to `/.ssh` or a truncated home; inputs are
   checked, paths quoted, root PATH fixed, failures counted, and existing SSH
   directory/key-list symlinks refused. Peer-key detection no longer accepts a
   commented key as an active bare-key entry; insertion starts with a newline.
   `jwssh` validates air/mbp, applies noninteractive/time-limited options to the
   final connection too, and never retries an already-started remote command.

9. **Client ordering — conditional, not automatically broken.** The Air's
   shared Host group may precede per-alias HostName blocks if it sets only common
   options. A shared or earlier wildcard HostName wins and shadows later aliases.
   Native `ssh -G -F` fixtures confirm separate wired/Bonjour/IP resolution with
   the described safe ordering. Actual user config was not accessed (outside
   permitted paths). Runbook supplies both-Mac instructions and effective-value
   checks; merely appending to an unknown config is insufficient.

## Changed files and local commits

- `scripts/hostlink/hostlink_setup.sh`: SSH/access preservation, validation,
  firewall/service/power/wired/sudoers/error-handling fixes.
- `scripts/hostlink/jwssh`: peer validation and bounded final connection.
- `scripts/hostlink/RUNBOOK.md`: attended setup, key exchange, alias/host-key
  checks, explicit hardening, accurate privilege/firewall/power limits.
- `tests/test_hostlink.py`: focused offline regression tests.
- This report.

Commits before the report/runbook commit:
`696c7bd06` SSH staging/access; `3281749ee` firewall/macOS flags;
`967aa46bc` sudoers validation; `24e75c527` SSH fallback;
`22aa2acc3` key-only rerun preservation; `a10f837f4` active-key/cable checks.
The final documentation commit contains this report and the revised runbook.

## Verification and boundaries

- `bash -n scripts/hostlink/hostlink_setup.sh scripts/hostlink/jwssh`: PASS.
- `python3.13 -B -m unittest tests.test_hostlink`: **12 tests PASS**, about
  1.4 s in the final code run. Native macOS OpenSSH 9.9p2 parses synthetic
  configs/keys; setters/ownership and failure branches use fixtures. Tests cover
  first-value-wins, confinement, retained key-only policy, unchanged prior bytes,
  rollback, exact firewall strings, alias ordering, no command retry, and cable
  arguments. Native sshd tests skip off macOS; no MLX code/tests involved.
- Additional native replay extracted the **entire exact offload Match heredoc**
  from the pinned Git script, substituted only synthetic paths/forced command,
  and checked both users with `sshd -T -h SYNTHETIC_KEY -f SYNTHETIC_CONFIG -C`:
  PASS, including all seven no-TTY/forwarding/RC settings.
- `/usr/sbin/visudo -cf SYNTHETIC/sudoers.new` with the intended edr rule:
  parsed OK, exit 0. Full real sudoers mutation was not exercised.
- `git diff --check`: PASS before final documentation commit.
- No full/sharded/quick suite, pipeline, sudo invocation, actual SSH connection,
  measurements, model downloads, real restricted/custody path access, agent-job
  changes, push or coordination-state edits. User's targeted-only/time/load rules
  override repository suite/coordination-update defaults. No delegates used.
  Intake stop card was NONE; urgent operator-access safety review selected by
  explicit user direction. No kernel row registered.

## Next exact step / remaining uncertainty

Lead must transfer/select these local commits on **both Macs** before Ed runs
setup; a download from the unchanged remote branch is stale. Follow RUNBOOK with
local Terminals open, resolve FAIL lines, confirm peer public keys and host-key
fingerprints, inspect `ssh -G` for each alias, prove fresh key-only logins both
ways over each usable path, verify `sudo -n true` and Air's effective offload
confinement, then optionally apply `--key-only` and retest. Do not leave either
Mac unattended before that passes. The setup does not itself complete the
missing MBP-key installation on Air or install client aliases. Live firewall
setter persistence, FDA/launchd access, service naming, cable/routes, M4 Air
power capabilities and authenticated offload operation remain owner-side checks.
No assertion that the two physical machines are currently reachable is made.
