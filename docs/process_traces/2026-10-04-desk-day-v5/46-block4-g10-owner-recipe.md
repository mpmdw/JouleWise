# Recipe 46: the clock-anchor positive control (G10), inside measurement block 4

2026-10-05, desk-day seat 2 (Opus 5.5); revised the same day by seat 3 for ruling 76 addendum D (G10 moves from
before `a1` to between `a2` and `s1`, and waits for a measured clock offset). For Ed. The software is ready; **the
control has not been performed.** Registration V5-QUAL-25G83-B4 §5 is the rule this recipe carries out.

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

Once, after the block's two arm-only controls (`a1`, then `a2`) have finished and before the consuming night `s1`
starts its T-0, on the same boot (do not restart the Mac between `a1` and `s1`). Nothing may be armed, no capture
may be running, and no Claude or Codex agent session may be open. Close every agent session first.

**Why not first.** The control only proves something if turning network time on actually moves the clock. How far
it moves is the *offset*: how far the Mac's clock has drifted from true time since it last synchronized. Today the
clock is about 1.15 s off. Every T-0 preparation checks the clock against internet time servers and, if it is more
than 0.5 s off, synchronizes it first. So the first T-0 preparation of the block (`a1`'s) will synchronize the
clock and bring the offset near zero. If G10 ran first, that synchronization would happen inside G10's own
preparation, and G10's switch-on would then find almost nothing to correct. Run after `a1`, G10 instead finds the
drift that has built up since `a1`'s synchronization, about 11 ms per hour at today's drift rate.

**How long to wait.** G10 needs an offset of at least 20 ms, so that the switch-on moves the clock well past the
5 ms threshold. It also needs the offset to stay under 0.4 s, so that its own preparation does not synchronize.
Twenty milliseconds accrues about two hours after `a1`'s synchronization. The lead checks this before handing you
anything (next section), so you are only called when the clock is ready.

## What the lead hands you beforehand

First the lead runs a read-only offset check. It queries the time servers with the same fixed command T-0 uses,
and changes nothing:

```zsh
(cd '<execution checkout>' && .venv/bin/python scripts/ed_session/capture_t0_anchor_positive_control.py preflight)
```

Exit 0 (`PASS`) means the offset is in the band. Exit 3 means it is still under 20 ms: wait and check again later.
Exit 4 means it is over 0.4 s, which should not happen after `a1`: the lead decides. Only after a PASS does the lead
prepare the inputs below, because they expire within an hour.

Then four paths:

1. a clean, reviewed execution checkout of JouleWise containing the helper;
2. a committed control pack inside that checkout;
3. an unused directory of **real** T-0 author inputs, captured through the normal
   `scripts/capture_t0_step.py` workflow (never fixture bytes, never a production window's inputs);
4. a new, empty control custody directory.

Preparing those inputs finishes with network time OFF and no agent running.

## What to type

Run this within an hour of the inputs being prepared.

In an ordinary terminal:

```zsh
(cd '<execution checkout>' && .venv/bin/python scripts/ed_session/capture_t0_anchor_positive_control.py run \
  --pack-root '<control pack>' \
  --author-inputs '<real T-0 author inputs directory>' \
  --custody-root '<new control custody directory>')
```

The helper asks you to confirm that no agent, armed window or capture is running. Type `OUTSIDE` only if that is
true. It then:

0. measures the offset again, exactly as the lead's check did, and stops at once, without touching the clock, if it
   is outside the band;
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

- **`g10_preflight_offset_too_small` or `g10_preflight_offset_too_large`** (exit 2, with `"g10_attempt": false`):
  nothing was spent and the clock was not touched. Tell the lead. A later try needs a new, empty custody directory
  and, if the inputs have expired, fresh inputs.

- **The anchor moved 5 ms or less** (exit 2, `NOT-DISCHARGED`): stop and tell the lead, with the custody path.
  **Do not run it again**, and do not change the time any other way. The lead decides the next step.
- **Any other non-zero exit:** the same. Keep the whole custody directory unchanged.
- **The helper was killed or the OFF step could not be confirmed:** run
  `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` yourself, keep its output, and tell the lead.
  The block must not start without an authenticated OFF receipt.

## Afterwards

Network time stays OFF. Each later occurrence makes its own OFF receipt and waits at least 600 seconds before its
first capture. The control's OFF receipt is never reused for a window.
