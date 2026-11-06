# Ed physical checklist (FINAL-DESIGN §3.1), reported 2026-11-06
- Stand: elevated (Ed: "it is elevated"). Clearance not separately confirmed.
- Room: thermostat 72 °F (22.2 °C), "pretty much 24/7" (Ed).
- Ambient logger/thermometer: none valid ("the thermometer isn't valid"). Ambient = thermostat setpoint only; no independent reading. Ambient is recorded, never gated, so R1/W1 record "setpoint 72 °F, unmeasured".
- Pending from Ed: sudoers step-4 output; battery >= 95 % + Optimized Battery Charging off + 140 W MagSafe direct; cooler status; agent apps quit.
- Sudoers (2026-11-06, Ed on the MacBook Pro): /etc/sudoers.d/joulewise-powermode installed root:wheel 0440, visudo -c all parsed OK.
  `sudo -n -l | grep powermode` -> `(root) NOPASSWD: /usr/bin/pmset -c powermode 0, /usr/bin/pmset -c powermode 2`
  `sudo -n pmset -c powermode 2` -> powermode 2 (no prompt); `... 0` -> powermode 0 (no prompt); `... 1` -> "a password is required" (refused). Left at powermode 0 (Automatic).
- 2026-11-06 Ed: no laptop cooler; Mac propped up; Claude and Codex apps quit; battery 100 %; Optimized Battery Charging OFF; Ed reported "high power mode is on" -> asked to return to Automatic (powermode 0) before R0. 140 W MagSafe direct: to confirm.
- 140 W MagSafe connected directly (Ed, 2026-11-06). Power mode back to Automatic via System Settings (Ed).
