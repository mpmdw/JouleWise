# ED-QUALIFICATION SESSION — one scripted visit (~20 min), prepared 2026-08-14

Purpose: close every stable hardware/privilege row the readiness council
needs in ONE session (interaction contract, decision log 2026-08-14:
magistrate rules everything else; Ed appears only for hardware/sudo,
batched). When the council is READY, ALPHA's arm chains onto the end of
this same visit — one trip, qualification through collection.

Run each step exactly; the session's terminal transcript is custody
evidence. All agent fleets will already be stopped before you sit down
(the loop prepares the machine and pings you).

## Step 1 — privilege grant (~1 min)
`sudo -v` (keeps sudo warm for the session). The loop cannot and will not
do this.

## Step 2 — production sampler live checklist (~5 min)
The #127 production sampler's reliance checklist: run the committed
script `scripts/ed_session/sampler-checklist.sh` when pinged — it
exercises a short sudo powermetrics sample under the production
supervisor, verifies child reaping (no orphaned sampler processes after
teardown: `pgrep -f powermetrics` empty), and records cadence
observations. The script tees its output to `/tmp/ed-session/` for the
audit's capture lens.

## Step 3 — JW-MET-3 rail probe (~7 min, ABBA)
The keyboard-backlight rail-inclusion probe (design custodied in the T6
record): four arms max-1 / off-1 / off-2 / max-2, 30 s sudo powermetrics
each with `--samplers battery,cpu_power,gpu_power,ane_power,thermal`; you
set the backlight level between arms when the script prompts. The loop's
staged script `/tmp/ed-session/rail-probe.sh` runs it end-to-end and the
analysis prints the differential per consumed rail. Documentation-grade
only — the boundary verdict (LED outside cpu+gpu+ane) already stands on
code evidence.

## Step 4 — keyboard backlight conservative control (~2 min, one-time)
System Settings → Keyboard: "Adjust keyboard brightness in low light"
OFF; brightness slider to ZERO; "Turn keyboard backlight off after
inactivity" NEVER. (Apple's supported pathway; removes an independent
timer transition. These become census literals:
keyboard_backlight.level=0 / automatic_adjust=false / inactivity=never /
verification=operator_visual.)

## Step 5 — §5A tap walkthrough (~3 min, familiarization)
Dry read of the two-tap sequence from the FINAL arm packet §3.4 (E-15
confirm → E-18 hand back → gap → E-16 restore → E-17 record) against the
actual screen. No live window; just the muscle memory.

## Step 6 — IF the council is READY: chain into ALPHA arm
The loop will have pre-staged the arm sequence; your part is the §5A
taps and the single foreground launch per the packet. If the council is
not yet READY, the session ends here — everything above stays valid
(stable capabilities; only T0 rows are perishable).
