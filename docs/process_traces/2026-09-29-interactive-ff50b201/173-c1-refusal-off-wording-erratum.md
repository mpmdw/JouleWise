# 173. C1 refusal at t0 and the OFF-wording erratum (2026-09-30)

**What happened.** Window C1, plan `d079-epoch-25g83-r6-derivation-c1-20261001T0137Z`, t0 18:37:00 PDT. The driver ran `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`, which exited 0 and printed `Network Time is already off.`. `network_time_off.admit` accepted only `setUsingNetworkTime: Off\n`, so the driver refused 2 s after t0 with `night_probe_error: network time OFF receipt not admitted`. The chain never started, no session opened and nothing was captured. Under Revision 6 section 7 the window takes no label, so C1 is armed again.

**Why it got through.** Recipe 170 GAP 8 said the setter could not be tested at arm. It can be: the setter is passwordless and idempotent. `arm_readiness.py` carried the note "Ed must bench-verify these exact sudo bytes before this value gates a window"; that was never done. Every test fed the one wording the code expected.

**Fix.** PR #448: one comparator that admits either setter statement ending Off and refuses everything else; a guard test against literal comparisons; recipe section 5.1 runs the real setter through the admission at arm time.

**Erratum to the sealed Revision 6 text.** Its `network_time_off_receipt` declaration says `"stdout_exact": "setUsingNetworkTime: Off"`. Read as: the stdout must state that network time ends Off, in either of the two wordings macOS prints. The requirement the clause protects is unchanged: network time Off, a receipt on the same boot as the first capture, at least 600 s old on both clocks. No code reads the declared string, and the sealed file is not edited.

**Ed's words.** "fix the reason for that idiotic refusal i just got emailed about and make silly semantic stuff like that less likely to waste our time"; "also make sure the window doesnt stop after a fail, that it fixes it and then rearms automatically". The magistrate brief gained refusal route R1-R5 (835aaba3).
