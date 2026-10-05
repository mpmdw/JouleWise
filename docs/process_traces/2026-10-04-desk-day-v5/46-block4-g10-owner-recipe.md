# Recipe 46: the clock-anchor positive control (G10), before measurement block 4

2026-10-05, desk-day seat 2 (Opus 5.5). For Ed. The software is ready; **the control has not been performed.**
Registration V5-QUAL-25G83-B4 §5 is the rule this recipe carries out.

## What this proves, and why it is needed

Every power sample JouleWise records is timestamped by the Mac's wall clock. Before each window, the T-0 author
compares the wall clock with the hardware's raw monotonic counter. The difference between them is the *clock
anchor*. With network time off, the anchor drifts slowly and predictably at the rate the kernel has stored
(about −3.2 ppm today). The author removes that predicted drift, and refuses to certify the window if what is left
exceeds 5 ms, or if the kernel's stored rate itself changed, either of which means the clock was reset. Gate G4
passes when neither happened.

This control shows that the refusal really fires. With automatic network time off for days, the wall clock drifts
from true time. Turning network time on lets macOS resync, which steps the wall clock and moves the anchor. The
control passes only if the clock is really reset (after removing steady drift, the anchor moved by more than 5 ms)
**and** the real author then refuses with
`evidence_author_t0_clock_attestation_underivable`. Running the resync without that movement proves nothing.

## When

Once, before the block's first arm-only control (`a1`) starts its T-0. Nothing may be armed, no capture may be
running, and no Claude or Codex agent session may be open. Close every agent session first.

## What the lead hands you beforehand

Four paths, filled in when the block is prepared:

1. a clean, reviewed execution checkout of JouleWise containing the helper;
2. a committed control pack inside that checkout;
3. an unused directory of **real** T-0 author inputs, captured through the normal
   `scripts/capture_t0_step.py` workflow (never fixture bytes, never a production window's inputs);
4. a new, empty control custody directory.

Preparing those inputs finishes with network time OFF and no agent running.

## What to type

In an ordinary terminal:

```zsh
(cd '<execution checkout>' && .venv/bin/python scripts/ed_session/capture_t0_anchor_positive_control.py run \
  --pack-root '<control pack>' \
  --author-inputs '<real T-0 author inputs directory>' \
  --custody-root '<new control custody directory>')
```

The helper asks you to confirm that no agent, armed window or capture is running. Type `OUTSIDE` only if that is
true. It then:

1. copies the author inputs into the custody directory and stamps both clocks;
2. turns network time ON with the same command every window's arm step already uses,
   `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on` (no password; existing sudoers entry);
3. prints the anchor movement every 5 seconds, stopping as soon as it exceeds 5,000,000 ns or after 120 seconds;
4. if the anchor moved more than 5 ms, runs the real T-0 author once on the copied inputs;
5. always finishes with `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` and records the OFF
   receipt, even after an error.

## What success looks like

Exit code 0 and `status=DISCHARGED`, with the path to `positive-control.json`. That file has exactly eight keys:
`schema_version`, `performed_by` ("Ed"), `outside_t0_sequence`, `network_time_reenabled`, `forced_resync`,
`anchor_before_ns`, `anchor_after_ns`, `author_refusal_reason_code`. Everything else (raw command output, clock
stamps, every poll, the author's response, the OFF receipt, a SHA-256 manifest) sits beside it in the custody
directory. The lead authenticates it and combines it with the software boundary checks.

## If it does not work

- **The anchor moved 5 ms or less** (exit 2, `NOT-DISCHARGED`): stop and tell the lead, with the custody path.
  **Do not run it again**, and do not change the time any other way. The lead decides the next step.
- **Any other non-zero exit:** the same. Keep the whole custody directory unchanged.
- **The helper was killed or the OFF step could not be confirmed:** run
  `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` yourself, keep its output, and tell the lead.
  The block must not start without an authenticated OFF receipt.

## Afterwards

Network time stays OFF. Each later occurrence makes its own OFF receipt and waits at least 600 seconds before its
first capture. The control's OFF receipt is never reused for a window.
