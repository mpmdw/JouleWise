# Block 5, second seal, BETA attempt 4: window record (unfinished: the harvest was cut short)

Magistrate activation 817d49e2 (Opus 5.5, headless), 2026-10-10, launched 22:40 PDT, stood down at 22:50 PDT
on the watchdog's request (`wall and monotonic deltas disagree; conservative resident drain`, 90 s).

- Plan `v5-b5-beta-a4-20261010T2237Z`. From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`,
  no refusal, no fault reason; chain exit code 0; 125 planned, 125 bundles present, 6 failed by the driver's
  count. Driver start 15:37:03 PDT, chain exit 22:34 PDT. Courier email Gmail `1a1297693ad10028`.
- 4.2: no open session. 4.3: pin `ADVANCED` 458 to 468, operator identity `magistrate-20261011T0541Z`, clone
  commit `81da8a6ffd8d0caf655b35c03c1021c02efc8111`. 4.4: uninstall rc=0, no night label or job file left;
  the dead-man calendar was hour 23, minute 59 (removed before it fired).
- 4.5: pin test `HARVEST_PINNED`, desk root `0699abbb0881ce64b39c46ba07de568cc3848260`. The harvest into
  `/Users/edr/night-archive/harvest-v5-b5-beta-a4-20261010T2237Z` started 22:45 PDT and was ended by this
  activation at 22:50 on the stand-down request. **That directory is a cut-short harvest and does not count.**
- Departure from the reading list: this activation printed `night/result.json`, `night/chain.exited`,
  `night/courier.sent` and `night.log` (five driver lines, no value) before reading brief 4.1.
- The watchdog queued six notices (five `clock_uncertain`, one `hold_census`, 16:43 to 22:35 PDT). They were
  NOT emailed and NOT acknowledged by this activation unless a line below says so.
- Owner mail: Gmail message `1a128ebb107987ab` (2026-10-10 20:04 PDT, on the ALPHA attempt 1 notice thread)
  is unread and not yet transcribed. It asks four things: revisit the term "window"; explore network time
  during windows against clock drift; check that the physical boundaries are in proportion; power traces
  with prefill and decode marked. Three read-only seats were started on them and died with this activation;
  partial reports are under `/Users/edr/night-archive/b5-consults/ed-1010-asks/`.

Next activation: brief section 3 case 2 for this plan. `pgrep -fl 'run_campaign.py --whole-window-verdict'`
must print nothing first; then harvest into `harvest-v5-b5-beta-a4-20261010T2237Z-r2` (variant A; steps 4.2
to 4.4 are done). Then transcribe the owner mail, relaunch the three seats if their reports are incomplete,
record, decide by section 6. If the watchdog's `clock_uncertain` drain keeps ending activations inside a
45-minute harvest, that is a watchdog fault to fix before anything else (it fired five times in this window).

Stand-down email sent, Gmail `1a12991360887373`; it carried all six watchdog notices, and `notice.ack` was written.

## Added 23:1x PDT, before exit: the Mac slept during this window (seat finding, not yet checked by the lead)

The network-time seat's report (`/Users/edr/night-archive/b5-consults/ed-1010-asks/network-time-options.md`)
finished after the stand-down email. Its side finding corrects that email: the five `clock_uncertain`
notices were not a watchdog fault and not clock drift. The watchdog compares the wall clock's advance with
Python's monotonic clock, which stops while a Mac sleeps (tolerance 60 s,
`scripts/magistrate_watchdog.py:122, 1714-1735`), and the Mac slept during the window:

- `pmset -g log`: "Using Batt (Charge: 79)" at 17:02:01 PDT, idle sleep at 17:02:07 (the battery profile has
  `sleep 1`), AC back at 17:02:27; then a cycle of dark wake and maintenance sleep to the window's end, with
  sleeps of about 929 s (17:04), 916 s (18:25), 402 s (19:42), 266 s (20:50) and 945 s (22:06). Why AC
  dropped is not established (the wake reason names `USB-C_plug`).
- `night/hazard_result.json`: Python monotonic and `CLOCK_MONOTONIC_RAW` agree within 416 ns at the window's
  start and are 3,500.003 s apart at its end: about 14 % of the 25,049 s window asleep.
- The window code holds no sleep-prevention assertion. Which members overlapped a sleep, and whether a member
  run in dark wake is usable, is open. The stand-down of this activation at 22:49 follows the same pattern
  (the Mac may still be cycling).

Next activation, before deciding anything from the re-harvest: (1) verify the three facts above from
`pmset -g log` and `night/hazard_result.json`; (2) check the charger and battery state now and whether the
Mac is still in the sleep cycle; (3) a structure-only listing of which members overlapped the six sleep
intervals (a seat; integers and member ids only); (4) tell Ed, correcting the stand-down email's "watchdog
fault" sentence; (5) a sleep during a chain is a physical hazard no arm check or flag covers: two-seat
consult on the window's status and on the cure (a sleep assertion held by the driver is window code and
needs a new seal; `pmset -b sleep 0` is a machine setting) BEFORE any further arm, even if the harvest says
claim-usable. Do not arm GAMMA or BETA attempt 5 until that consult has ruled.
