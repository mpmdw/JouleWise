# DRAFT AMENDMENT: an always-attached external log volume for the ALIGN v4 series

Status: **DRAFT. Not in force.** Proposed 2026-11-06 by the laptop lead's delegate (Opus 5.5).

Adoption needs all three of:
1. the hardware qualification (`SSD-ALWAYS-ATTACHED-STUDY.md` §6) passing at the level the chosen option requires;
2. the window design council (Opus 5.5 xhigh, Sol 6.1 xhigh, Fable 5.1; Opus has the final say);
3. Ed's go, including his confirmation that the borrowed drive can stay for the whole series.

Until then, today's rule binds: no external volume is mounted during R0, R1, W1 or the calibration windows
(RUN_STATE item 181).

What this amends:
- FINAL-DESIGN §3.1 (physical setup, "then untouched for the whole series");
- the measurement-window rules in RUN_STATE item 181 ("no external volume mounted");
- the R1 lever rule in FINAL-DESIGN §2.2 ("once adopted, never changed within the series"), which applies here by
  analogy.

It does not change any registered constant, the estimand, the exclusions X1-X8, U1-U6, or the contrast rule.

## A1. Scope

The ALIGN v4 series only: R1, W1, N1-N4 and D1-D3, whose estimand is the `powermetrics:gpu_power` rail. Any
measurement whose channel is the DC or whole-machine boundary keeps the old rule without exception:
- BYTES-type windows;
- PDTR or KM003C energy;
- the PSTR/PDTR-based claims.

The drive's 1-8 W is in those channels.

## A2. The rule

The arm refuses while any external volume is mounted, with one exception. The exception applies when all of these
hold:
1. `configs/align/v4/external_log_volume.json` has `status: "active"` and names this amendment.
2. Its `allowlist` holds exactly one volume UUID.
3. That volume is mounted at the configured mount point (`/Volumes/JW-EXT`).
4. The volume is APFS, on an external physical device, writable, and has ownership enabled.
5. `mdutil -s` reports "Indexing disabled."
6. `tmutil isexcluded` reports "[Excluded]".
7. `.fseventsd/no_log` exists on the volume.

Unchanged refusals:
- any other external, network or disk-image mount;
- a census that cannot be read;
- a second instance of the allowlisted volume.

With `status: "active"`, the allowlisted volume being **absent** also refuses (A3).

Mechanism: `scripts/align_external_volume.py arm-check --config configs/align/v4/external_log_volume.json` (exit 0
PASS, 3 REFUSE). It runs at the arm and its JSON verdict is kept in custody. Wiring points:
- the magistrate's arm sequence;
- `scripts/launch_align_r0.py preflight` (main);
- the v4 session `prepare`.

## A3. Attachment is a series lever

- The drive is attached from a series boundary: before R1, so that R1's soak and step tests (slots S1-S9) are measured
  in the series configuration.
- It stays attached, on the same port, cable and placement (at least 30 cm from the intake and exhaust), through the
  last window of the series.
- Removing it within the series (for example, to return the borrowed drive) is a **configuration break**:
  - it is recorded;
  - U4 and the K-session anchor read are printed separately on each side of the break;
  - no model-window spans the break.

## A4. Write routing

`log_mode` options:
- **`internal` (adopted with this amendment; Option B).** Every window path stays on the internal disk: runs parent,
  claim and bound backups, custody root, `TMPDIR` (where the powermetrics capture streams). Nothing is written to the
  external volume between the quiet-period start (A5) and the window's end.
- **`backup` (Option A-lite).** Not adopted here. It needs Q2 and Q3 to PASS and a separate lead ruling. Per-member
  backups go to the volume between members. `RouteGuard` reroutes them internal for the rest of the window if the
  volume is lost.
- **`direct` (Option A).** Not adopted.

The custody root and `TMPDIR` are never routed to the external volume in any mode.

## A5. Quiet period

- No access to the external volume starts within Q minutes before t0, where Q = max(30 min, 2 × the
  last-access-to-low-power time measured in the qualification). "Access" includes offload, Flash-Next work and copies.
- Access is not allowed again until the window's terminal record. This keeps the drive in one power state for the
  whole window.
- The offload runbook (PR #665) runs only between windows and addresses the volume by UUID.

## A6. Events inside a window

An unmount, disconnect, remount or UUID change of the allowlisted volume is journaled as `external_volume.event`, from
the presence check (`stat` only) and the kernel log. Then:
- Every member whose request overlaps the event, or the 600 s after a remount (trim, `fsck_apfs`, diskarbitration),
  is flagged `external_volume.event`. It is excluded from calibration and the U checks, as X4 is.
- The window continues. Under `internal`, nothing written is affected.
- The next arm refuses until the volume is back and passes A2.

The flag, its catalog entry and the hazard census row are to be added when this amendment is wired. They are not on
this branch.

## A7. Disclosure

Every report from a series run under this amendment states:
- the attachment;
- the arm verdict;
- the measured presence offsets (GPU rail, Q1; PSTR and PDTR, print only).

The "unassigned power residual" print (PSTR − GPU − CPU − ANE) is labelled as including the external drive's bus
power.

## A8. Qualification gate

Q1-Q3 and Q5 are as in the study, §6 (there is no Q4). The mechanical option mapping (`ssd_qualification.evaluate`):
- **B** requires Q1 PASS and Q5 PASS.
- **A-lite** requires Q1, Q2, Q3 and Q5 PASS.
- **A** is not adopted.

A FAIL anywhere leaves Option C. An INCONCLUSIVE may be re-run with more pairs; a margin is never loosened.

## A9. Rollback

Setting `status: "off"` restores today's rule mechanically. If the qualification or any later window shows the drive
inside a member's flags more than once, the lead returns the series to C at the next series boundary (A3).

## A10. Software (branch `lane/2026-11-06-ssd-always-attached`)

- `joulewise/align/apple/external_volume.py`: config, census, `arm_check`, `route`, `RouteGuard`, `prepare_plan`.
- `scripts/align_external_volume.py`: the CLI.
- `configs/align/v4/external_log_volume.json` (`off`) and a qualification example.
- `joulewise/align/apple/ssd_qualification.py`, `scripts/align_ssd_qualification.py` and
  `scripts/align_ssd_fixed_decode.py`.
- Tests: `tests/align/test_external_volume.py` and `tests/align/test_ssd_qualification.py`.

Not yet wired into any arm path. Wiring goes through the usual gates: a Sol build or review, an Opus executing
review, and a Fable cold pass on A2 and A6.
