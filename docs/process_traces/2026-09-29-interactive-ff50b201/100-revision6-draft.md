DRAFT, NOT SEALED. Writer: Opus 5.5 subagent, 2026-09-30. Nothing here is in force.

# Revision 6 draft: back-to-back windows for the cap evidence and the successor calibration (epoch 25G83)

This file has two parts.

- **Part A** is the text proposed for sealing. At the seal it is appended, unchanged, to
  `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, after Revision 5 and its
  amendment A-R5b. This is how Revisions 2, 3 and 5 were added. The cold registration gate
  may choose a separate file instead; see Part B, item O-12.
- **Part B** holds the writer's notes and the list headed "Open for the cold registration
  gate". It is not sealed.

Inputs (all read in full): the sealed Revision 5 text and A-R5b (main `0009b976`, file sha256
`81b65f08…`); cap ruling `20-cap-council/21-coldgate-fable-ruling.md` and its addendum A1
`31-addendum-ruling.md` (records worktree 77b1bee2); addendum A2 `40-cap-a2/21-coldgate-fable-ruling.md`
and erratum E1 `40-cap-a2/31-coldgate-erratum-ruling.md`; `90-critical-path.md` §4;
`80-prune/41-cadence-sol.md`; decision-log D-186; session record item 46.

---

# Part A: text for sealing

# Revision 6 (DRAFT 2026-09-30; sealing pending the cold registration gate and the pins below)

**STATUS:** draft. This revision is prospective. It governs only the windows it declares, and
only once it is sealed. It does not arm or authorize any window, license any measurement, or
lift the claim hold H1. No window under it may be armed until two things are true: every
unfilled slot (a pin to be taken at the seal, or a threshold for the cold gate to size; §13 gives the mechanical test) has been replaced by its value, and the
digest of this whole file has been pinned in the arm material. The seal procedure is in §13.

**Authority.** This revision rests on six sources:

- Erratum CAP-COUNCIL-25G83-01-A2-E1, §4 step 12. That step lists what this registration
  must say.
- Addendum CAP-COUNCIL-25G83-01-A2 §3.6, items 6 and 7, and §3.3.
- Addendum CAP-COUNCIL-25G83-01-A1: rule CAP-RULE-25G83-2 (R0 to R12), and S5.
- Cap ruling CAP-COUNCIL-25G83-01 §5 (membership).
- Decision D-186 (network time, round-limit wording).
- The owner's approvals of 2026-09-29, session ff50b201, record item 46: the name of P8, the
  successor name pattern, and the owner's statement that this answer is the seal approval
  that E1 step 12 requires.

The owner's cadence rules of 2026-09-29 are also authority, and §6 states them. Revision 1,
Revision 2, Revision 3, Revision 5 and amendment A-R5b stay sealed, and not one word of them
is edited here. For the Revision 5 windows W1 and W2 they stand exactly as written. §1 maps
which of their clauses this revision replaces for the new windows.

## 0. Words used

Each term is defined here before any rule uses it.

- **Capture**: one 197-second recording by the power sampler (`/usr/bin/powermetrics`). During
  it the machine runs 59 commanded one-second load pulses (protocol
  `powermetrics_pulse_fiducial_v3`). **Frame**: one power sample. **Median frame**: the middle
  value of one capture's native frame lengths, in milliseconds.
- **B** (stored as `b_fiducial_s`): the single timing-uncertainty number, in seconds, that a
  capture yields.
- **Estimator**: the code in four files that turns a capture's raw bytes into B. **Pins**: the
  sha256 digests of those four files.
- **Cell**: one rectangle of candidate pulse-edge timings that the estimator tests. **The cap**:
  the most cells one capture may test. It is fixed by rule CAP-RULE-25G83-2 as one integer,
  pinned in §5.
- **Calibration**: an issued JSON file of limits on B, computed from its **members**, the
  captures whose B enters the limits.
  - **R7** is `d079_calibration_acceptance_v2_n17_r7`: 17 members, all taken at build
    25F84.
  - **P8** is `d079_calibration_acceptance_v2_n17_r8`. It is R7 re-issued with only its pins,
    identity and notes changed, so its limits ("operatives") are identical to R7's
    (E1 §3.1).
  - **r1** is the unregistered 25G83 candidate `d079_calibration_acceptance_v2_n12_25g83_r1`
    (bytes `dbad7cc7…`). Its identifier is retired and never reused.
  - **The successor** is the calibration this revision's windows will produce.
- **Window**: one agent-free run of one derivation-kind ledger session of 12 declared slots.
  Earlier revisions say "night"; the word meant a window and never a time of day. **Slot**: one
  declared, ordered place for a capture inside a window. **Agent-free**: no model-driven agent
  process runs on the measurement Mac, whether active or dormant. The reason is that agent
  processes draw power, and the sampler measures that power. **Windows of this revision** are
  labelled C1, C2, C3 … in ledger order (§7). They are not W1, W2 or W3, which are the sealed
  Revision 5 windows.
- **Valid**: a capture whose ledger disposition is `valid`. **Resolved**: its stored anchor-v3
  clock outcome resolves (Revision 1, "Anchor-v3 replay").
- **Counted capture** (rule R9 of CAP-RULE-25G83-2): a capture in which the cell search ran
  and whose median frame lies between 100 ms and 150 ms inclusive, in a window whose
  battery-float verdict is not adverse (A-R5b). A capture refused at clock alignment tests no
  cells and is not counted.
- **The harness**: the replay harness of rule R0. It is one committed script, cited by digest
  (§5). In report mode it prints, for each capture, the cells, the median frame, cells ÷ cap,
  the disposition and any stop trigger. It never prints B.
- **Content identifier**: the sha256 that the ledger assigns to a capture from its manifest
  hash and its evidence hash. **Set aside**: named in the disposition registry
  `configs/calibration/observation_dispositions.json` under a reviewed decision. The issuer and
  the validator then recognise the row as neither a member nor a foreign row.
- **Foreign row**: a valid capture of epoch 25G83 that belongs to no session of this
  registration and carries no disposition. The issuer refuses to issue while any foreign row
  exists (Revision 1 addendum A-7).
- **S, C, Q99**: as Revision 5 defines them.
  - S is the bracket screen: the corpus range quantized to 1e-6 s, or 0.010818 s if that is
    larger.
  - C is the budget ceiling, meaning the maximum budgetable drift.
  - Q99 is t(0.995, df) × sample SD × √2.
  - df is the degrees of freedom: n − 1 unless §9 says otherwise.

## 1. Supersession map

"Stands" means the clause applies to these windows exactly as sealed. "Replaced
prospectively" means the clause still governs W1 and W2 as sealed, and does not govern the
windows of this revision. The clause shown in its place governs them instead.

| Sealed clause | For W1/W2 | For the windows of this revision |
|---|---|---|
| Rev 1, epoch tuple, powermetrics and MLX pins, the voiding sentence | stands | stands (§5) |
| Rev 1, "Ledger baseline" (one session per window, opened at head-equals-pin, pin committed at the desk before the next window opens) | stands | stands. "At the desk" is read as "by the between-window harvest" (§6.2 item b). |
| Rev 1, "Sample" (distinct calendar days) | replaced by Rev 5 | replaced prospectively by §6 (no calendar spacing) |
| Rev 1, "Classification" (derivation-only under the active artifact) | read with r7 (Rev 5) | read with P8 (§2) |
| Rev 1, "Membership", "Exclusions" | stand | stand, plus the frame-range and R9-void rules of §8 |
| Rev 1, "Stopping" (n ≥ 19) | replaced by Rev 5 | replaced prospectively by §7 and §8 (n ≥ 12, as Rev 5) |
| Rev 1, "Blindness" | stands as Rev 5 amended it | stands; the dry run may also report the harness figures of §10 |
| Rev 1, "Screen challenge" | dropped by Rev 5 | stays dropped (diagnostic only) |
| Rev 1, "Analysis", quantile proof, D-125 envelope | stand as Rev 5 amended them | stand, plus §9 (a second, blocked Q99 when a dependence diagnostic flags) |
| Rev 1, "Known conditions" (display state not constrained) | stands | stands |
| Rev 2 (equivalence night, PASS/FAIL) | not taken (Rev 5) | not taken |
| Rev 3 chain digest `b5beea46…` | stands | replaced by the chain digest pinned in §5 |
| Rev 5, operating condition (Interactive launch context, template digests) | stands | stands (§5) |
| Rev 5 line 612: "at least 6 h apart"; W1/W2/W3 sequence; W3 only if fewer than 12 valid after W2 | stands | replaced prospectively by §6 and §7 |
| Rev 5 line 612: W1 cadence stop (> 150 ms) and futility stop (< 6 valid of 12) | stand | kept (§11). The cadence stop now applies after every window. |
| Rev 5, issuance arithmetic (n ≥ 12; S; C; zero headroom; over-inset refusal at 0.25 s; `excursion_limited` label) | stands | stands, plus §9 |
| A-R5b predicate, admission, per-slot evidence, window verdict, consequences, disclosure | stand | stand |
| A-R5b "Replacement": "keeps this revision's spacing of at least 6 h to its neighbours" | stands | replaced prospectively: a replacement window meets §6.2 like any other window |
| A-R5b "at most one replacement window per epoch" | stands | stands. W1 and W2 used none, so one remains available for epoch 25G83 (§7). |

## 2. Predecessor, and how to read "R7"

**Predecessor.** P8, `d079_calibration_acceptance_v2_n17_r8`, at
`configs/calibration/calibration_acceptance_d079_v2_n17_r8.json`:

- file sha256: `TO BE PINNED AT SEAL`
- `derivation_sha256`: `TO BE PINNED AT SEAL`

P8 is R7 re-issued with only its pins, identity and notes changed (E1 §3.1). It judges build
25F84, and it is the active default under which each capture of these windows is written
derivation-only. The issuer takes the predecessor ceiling from it: 0.010164834757777545 s, the
same value as R7's.

**Basis-reading sentence** (A2 §3.6 item 6, in E1's naming): "read P8 wherever R7 is named as
a derivation basis; operatives identical".

Why the sentence exists: the W1/W2 captures record R7 as their derivation basis, while the
captures of these windows record P8. The two files carry identical operatives, so this
difference in the recorded name changes no number.

## 3. The 12 W1/W2 rows, set aside; what is never a member

**The 12 valid W1/W2 captures are set aside.** They are not members of the successor or of
any registered calibration. They are not diagnostics. They are valid captures. Each is named
by content identifier under decision `CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29`, with
this mechanism text, byte-identical to the registry: "valid Revision 5 capture of window W1 or
W2; member of the unregistered 25G83 candidate r1, whose member list was fixed under the
165,000-cell cap while 8 of the 24 captures stopped on that cap; set aside from the successor
under CAP-COUNCIL-25G83-01 addendum A1 S5 and erratum E1; a valid capture, not a diagnostic;
not a member of any registered calibration".

The 12 content identifiers, in registry order:

```text
e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f
0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c
79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d
554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d
37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3
c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d
641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e
a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41
4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc
2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9
4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2
372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0
```

The registry file that holds them has sha256
`4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd`. This is the value of
`DISPOSITION_REGISTRY_SHA256` on main `0009b976`. It lists 23 rows: these 12, and the 11 rows
of 2026-09-19 under `D-126-disposition-25G83-v3-2026-09-25`. **The successor declares both
decision identifiers** in `prior_observation_set.disposing_decision_ids`. The validator
refuses an artifact that declares only one of the two decisions while its prior set carries
rows of both (E1 §3.2 item 4).

**Never members, of anything:** the 8 W1/W2 captures that stopped on the 165,000-cell cap, and
the 11 captures of 2026-09-19 (cap ruling §5 item 1). The 8 cap stops are not valid, so they
are neither foreign rows nor set aside.

**r1's identifier is retired.** No bytes other than r1's may ever carry
`d079_calibration_acceptance_v2_n12_25g83_r1`. The successor's identifier follows the pattern
the owner approved, `d079_calibration_acceptance_v2_n<N>_25g83_r2`, where `<N>` is the
successor's realized member count. It is set explicitly at issuance and never left to the
issuer's default name.

**The doubling arithmetic (E1 §3.2).** A calibration goes stale when the ledger holds too many
valid captures of its own build compared with its corpus. "Stale" means the validator reports
the trigger `corpus_doubles_from_<n>_to_<2n>` and a re-derivation is due. The rule is in
`joulewise/calibration_bracketing.py` (the doubling block near line 2370):

- The threshold is 2 × n, where n is the calibration's corpus size.
- The count is every `valid` ledger row whose identity epoch is the judged build and whose
  content identifier is not set aside by a decision the calibration declares.

Because the successor declares both decisions, neither the 12 W1/W2 rows nor the 11 rows of
2026-09-19 enter its count. At birth the successor's count is its own registration's valid
rows: its n members, plus any valid rows of its sessions that are not members (for example, a
valid capture whose anchor did not resolve). It goes stale when the count reaches 2n.

Worked example with invented counts: a successor with n = 30 members and one valid non-member
row starts at a count of 31 and has a threshold of 60. It goes stale after 29 more valid 25G83
captures. If the 12 set-aside rows counted, it would start at 43 and go stale after 17 more.
The choice changes when re-derivation is due. It changes no number. The owner sees this
arithmetic at the seal.

## 4. The two purposes of these windows

Both purposes are declared before the first capture (cap ruling §5 item 4).

1. **Cap evidence.** This is the acceptance test R9 of CAP-RULE-25G83-2, run under the shipped
   estimator bytes. It reads only cells, median frames and dispositions, never B. It passes
   when all of these hold:
   - at least 24 captures are counted;
   - no capture stops on the cell count;
   - no capture stops on the wall deadline;
   - every capture whose cell search ran has cells ÷ cap at or below 0.5;
   - every median frame is reported.

   Its record is committed before any B of these windows is read. That commit is an ancestor
   of every commit that carries such a B.
2. **Successor calibration.** The successor is derived from every valid, resolved,
   in-range capture of these windows (§8). B is not read until the last window is terminal
   and the R9 record has been committed.

The cap test cannot select on B. It reads no B, and a pass means that no capture was removed.
If R9 fails, the campaign is void: its captures are diagnostics and never members under any
cap (cap ruling §5 item 4).

## 5. Operating condition and pins

Each item below is part of the registered experiment. A change to any of them voids this
revision.

- **Identity epoch.** Six fields, unchanged from Revision 5: `os_build` = `25G83`;
  `hardware_model` = `Mac15,9`; `power_policy` = `ac_high_power`; `sampling_interval_ms` =
  `100`; `estimator_revision` = `joint_loss_sublevel_interval_branch_v2`; `pulse_protocol_id` =
  `powermetrics_pulse_fiducial_v3`.
- **Machine pins.** Unchanged from Revision 1: the powermetrics binary digest `b762e5bf…`
  (verified on the machine 2026-09-30) and MLX 0.31.2.
- **Launch context.** Unchanged from Revision 5: a launchd agent with
  `ProcessType=Interactive`, with template digests `e62a461b…` and `1570b745…` (both
  recomputed on main `0009b976` and equal). Each window's rendered-plist digests go into
  that window's arm evidence.
- **Estimator pins.** The four digests P8 records in
  `prospective_rederivation.estimator_code_sha256`: `TO BE PINNED AT SEAL` (four values).
- **Cap.** The integer CAP-RULE-25G83-2 yields, as merged in the cap transaction:
  `TO BE PINNED AT SEAL`.
- **Harness, rule text and roster** (rule R0 and step 6 of E1 §4), by digest:
  `TO BE PINNED AT SEAL` (three values).
- **Chain digest then in force.** The sha256 of `scripts/night_chains/calibration_derivation_only.zsh`
  at the head the windows are armed from: `TO BE PINNED AT SEAL`.
- **Validator digest then in force.** The sha256 of `scripts/validate_powermetrics_fiducial.py`
  at the same head: `TO BE PINNED AT SEAL`. It is taken at or after the identity-seam merge
  (#444).
- **Disposition registry.** The file digest given in §3.
- **Network time.** Network time stays OFF on the measurement Mac (D-186). Each window is
  admitted by exactly one **settled OFF receipt**. The receipt is a write-once record of one
  run of `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` that meets all of
  these conditions:
  - its exit status is 0;
  - its standard output is exactly `setUsingNetworkTime: Off` (the known `Error:-99`
    diagnostic line on standard error is tolerated);
  - it was taken on the same boot as the window's first capture;
  - it was taken at least 600 s before that capture, on both the wall clock and the
    monotonic clock.

  A brief clock resync is allowed only in the window's arm step: network time ON, then OFF,
  then the receipt, all while no capture of the window exists. Nothing turns network time ON
  after a window's first capture.

  Three earlier requirements are withdrawn prospectively: the per-capture system-log
  attestation (H6), the restore-ON machinery, and A1 K3's rule that a slew-attested capture
  does not count. H7, the first comparison of network-time-OFF captures with the network-time-ON
  captures of W1/W2, is report-only science. It never gates issuance and never pools the two
  sets.

  The 5 ms limit on clock movement within one capture is unchanged, because it is part of
  the estimator. A capture refused by it is invalid and is not counted.

## 6. Window shape and when a window may start

**6.1 Shape (unchanged in every respect but spacing).** Each window has:

- one derivation-kind ledger session of 12 declared slots;
- one 600 s settle after the last operator action;
- 12 slots at a 600 s start-to-start pitch, in fixed slot order, with a 480 s capture budget
  for the twelfth slot;
- protocol v3 unmodified, and no parameter tuned between captures;
- the Revision 5 battery-float admission and per-slot evidence;
- no operator and no agent present.

A slot the window cannot reach is recorded unused, with reason `window_exhausted`. It is never
compressed or replaced. The plan's `window_max_s` must clear the programmed span plus the
driver's 600 s OFF settle and the generator's allowances. This is a planning fact, not a
science rule.

**6.2 When window k+1 may start: physics, not the calendar.** The owner's rules of 2026-09-29
set the cadence:

- The measurement Mac is dedicated.
- Windows run back to back at the cadence the science needs.
- "Nights" are metaphorical.
- Only physics waits between windows.
- The six-hour gap of Revision 5 has no measured justification (cadence audit F1) and is
  replaced prospectively.

So this revision sets **no minimum gap, no maximum gap and no time of day**. Window k+1 may
start only when all of the following hold. They are checked in this order, and the evidence
for each is recorded for the window.

a. **Window k is finished.** Its session is terminal: its last declared slot is final, or an
   abort has closed it. Every capture and driver process of the window has exited. Its
   custody is sealed.
b. **The blind checks of window k are done**, with no B read:
   - raw bytes authenticated against the recorded digests;
   - the harness report under rule R8;
   - the cadence check (median of per-capture median frames ≤ 150 ms);
   - the battery-float window verdict (A-R5b);
   - the count-only dry run;
   - the ledger head pin committed;
   - the count rule of §7 evaluated and its decision recorded.
c. **Agent census zero.** The night gate's census finds no agent process on the machine.
   Harvest processes have exited before item (h)'s dwell begins.
d. **Thermal state nominal.** The operating system's thermal-pressure level reads Nominal.
e. **Idle power recovered.** Over a sustained 30 s window with at least 80 % evidence
   coverage, idle power is at or below 110 % of the reference idle power. The check is
   released on recovery and capped at 300 s. These constants are the controller's
   `cooldown-v2` defaults. The reference is `PLACEHOLDER` (Part B, O-5).
f. **Battery float.** The A-R5b predicate passes at arm, before publication and at t0, as
   sealed.
g. **Network time.** A settled OFF receipt (§5) exists for this window.
h. **Clean dwell.** For 600 s continuously, no process other than the allow-listed ones uses
   more than 5 % CPU and the one-minute load average stays at or below 2.0. Polling is every
   30 s, and any contamination restarts the 600 s. These are the constants of
   `scripts/prewindow_check.sh`. The 600 s of (g) and the 600 s of (h) may run at the same
   time; neither is added to the other.

For each window the record states: the start-to-start interval from the previous window, the
gap between them, and the evidence for (a) to (h). An owner block of development work between
two windows ("Mix", record item 46) is permitted. The windows before and after such a block
are ordinary consecutive windows of this registration, and §9 treats any difference between
them as a window effect.

## 7. Count rule, window triggers and stops (machine-readable)

**The rule in words.** The windows of this registration are taken in ledger order, meaning
the order in which their sessions were opened (`capability_sequence`). They are labelled C1,
C2, … in that order. After each window's blind checks, the count rule decides one of five
outcomes. The first clause that applies wins.

1. **STOP_TO_REVIEW** if any stop line of §11 has fired.
2. **CLOSE_AND_DERIVE** if, summed over all counting windows so far, counted ≥ 24 **and**
   valid ≥ 12.
3. **R9_NOT_PASSED_TO_REVIEW** if three counting windows are done and counted < 24. Rule R9
   permits a third window for the count, and no fourth.
4. **MAXIMUM_REACHED_TO_REVIEW** if four counting windows are done.
5. **NEXT_WINDOW** otherwise.

So another window runs while counted < 24 **or** valid < 12. These are the two triggers:

- **T-count** comes from A1 R9 and reads counted captures.
- **T-valid** comes from Revision 5 and A2 §3.6 item 7, and reads valid captures.

Either trigger alone opens the next window; their combination is "any". The count trigger can
open a window only up to the third. The valid trigger can open a fourth, and only when at
least 24 were counted after the third. "Review" means a consult, a cold gate or the owner
(D-186). No outcome is "stop for good", and no clause reads B.

A **counting window** is a window whose battery-float verdict is not adverse. A window with an
adverse verdict (`battery_float_confounded` or `battery_float_evidence_missing`) is kept and
disclosed, but none of its slots counts toward counted, valid or n. It is replaced once
under A-R5b. The replacement takes the replaced window's place in the sequence and faces that
window's stops afresh. That makes at most 4 counting windows and at most 5 windows in all. A
second adverse window is a stop line.

**Worked examples** (the counts are invented):

- C1 counts 11 and has 10 valid. The futility stop (valid < 6 in C1) does not fire. Totals:
  counted 11, valid 10 → NEXT_WINDOW.
- C2 counts 12 and has 12 valid. Totals: counted 23, valid 22 → NEXT_WINDOW. T-count alone
  opens C3 here. Under Revision 5's rule, which had only T-valid, C3 would not have opened.
  A2 row 7 named this gap.
- C3 counts 12 and has 11 valid. Totals: counted 35, valid 33 → CLOSE_AND_DERIVE. Up to 33
  members.
- Other paths: totals of counted 23 after C3 → R9_NOT_PASSED_TO_REVIEW, and the campaign is
  void. Counted 30 but valid 11 after C3 → NEXT_WINDOW (C4, by T-valid). Valid still below 12
  after C4 → MAXIMUM_REACHED_TO_REVIEW, and nothing issues.

**The declaration.** The block below is the machine-readable form that the issuer change
(WI-13) reads. The prose above explains it. If the two disagree, the cold registration gate
reconciles them before the seal.

```json
{
  "schema": "joulewise-registration-windows/v1",
  "registration": "D-079 epoch 25G83 Revision 6",
  "status": "DRAFT",
  "identity_epoch": {
    "os_build": "25G83",
    "hardware_model": "Mac15,9",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3"
  },
  "predecessor": {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r8",
    "path": "configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",
    "file_sha256": "TO BE PINNED AT SEAL",
    "derivation_sha256": "TO BE PINNED AT SEAL",
    "basis_reading": "read P8 wherever R7 is named as a derivation basis; operatives identical"
  },
  "successor_acceptance_id_pattern": "d079_calibration_acceptance_v2_n<N>_25g83_r2",
  "retired_acceptance_ids": ["d079_calibration_acceptance_v2_n12_25g83_r1"],
  "disposing_decision_ids_required": [
    "D-126-disposition-25G83-v3-2026-09-25",
    "CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29"
  ],
  "disposition_registry_sha256": "4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd",
  "set_aside_w1w2_content_ids": [
    "e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f",
    "0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c",
    "79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d",
    "554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d",
    "37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3",
    "c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d",
    "641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e",
    "a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41",
    "4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc",
    "2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9",
    "4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2",
    "372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0"
  ],
  "sessions": {
    "session_kind": "derivation",
    "session_id_pattern": "^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$",
    "session_id_carries_order": false,
    "order": "ledger_capability_sequence",
    "every_matching_session_must_be_named": true,
    "declared_slots_per_session": 12,
    "settle_s": 600,
    "slot_pitch_s": 600,
    "final_slot_capture_budget_s": 480,
    "inter_window_min_gap_s": null,
    "inter_window_max_gap_s": null,
    "time_of_day_constraint": null
  },
  "start_state_conditions": [
    "previous_window_terminal_processes_exited_custody_sealed",
    "previous_window_blind_checks_done_and_count_rule_recorded",
    "agent_census_zero",
    "thermal_pressure_nominal",
    {"idle_power_recovered": {"sustained_window_s": 30, "coverage_fraction_min": 0.8,
      "tolerance_fraction_of_reference_max": 1.10, "cap_s": 300, "reference": "PLACEHOLDER"}},
    "battery_float_predicate_pass_A_R5b",
    {"network_time_off_receipt": {"argv": "/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off",
      "exit_status": 0, "stdout_exact": "setUsingNetworkTime: Off", "same_boot_as_first_capture": true,
      "min_age_before_first_capture_s": 600, "clocks": ["wall", "monotonic"], "receipts_per_window": 1}},
    {"clean_dwell": {"continuous_s": 600, "cpu_percent_per_process_max": 5.0,
      "load_average_1min_max": 2.0, "poll_s": 30, "reset_on_contamination": true,
      "may_overlap_network_time_age": true}}
  ],
  "definitions": {
    "counted_capture": ["cell_search_ran", "median_frame_ms_between_100_and_150_inclusive", "window_battery_verdict_not_adverse"],
    "valid_capture": ["ledger_disposition_valid", "window_battery_verdict_not_adverse"],
    "counting_window": "window_battery_verdict_not_adverse",
    "counted_source": "R9 record committed by digest (harness report mode); the issuer does not recompute cells",
    "valid_source": "ledger"
  },
  "count_rule": {
    "evaluated": "after each window's blind checks, before any B is read",
    "triggers": [
      {"id": "T-count", "next_window_if": "counted_total < 24", "source": "A1 R9", "last_window_it_may_open": 3},
      {"id": "T-valid", "next_window_if": "valid_total < 12", "source": "Rev 5; A2 section 3.6 item 7", "last_window_it_may_open": 4}
    ],
    "combination": "any",
    "decision_order": [
      {"if": "any_stop_line_fired", "then": "STOP_TO_REVIEW"},
      {"if": "counted_total >= 24 and valid_total >= 12", "then": "CLOSE_AND_DERIVE"},
      {"if": "counting_windows_done == 3 and counted_total < 24", "then": "R9_NOT_PASSED_TO_REVIEW"},
      {"if": "counting_windows_done == 4", "then": "MAXIMUM_REACHED_TO_REVIEW"},
      {"else": "NEXT_WINDOW"}
    ],
    "max_counting_windows": 4,
    "max_battery_replacement_windows": 1,
    "max_windows_total": 5,
    "review_means": "consult, cold gate or owner (D-186); never stop for good"
  },
  "stop_lines": [
    {"id": "STOP-CADENCE", "applies": "every window", "fires_if": "median of per-capture median native frame lengths > 150 ms", "source": "Rev 5 (W1 only), extended here"},
    {"id": "STOP-FUTILITY", "applies": "first counting window only (C1 or its replacement)", "fires_if": "valid < 6 of 12", "source": "Rev 5"},
    {"id": "STOP-R9-CELL", "applies": "every window", "fires_if": "any capture stopped on the cell count", "source": "A1 R8(b), R9"},
    {"id": "STOP-R9-DEADLINE", "applies": "every window", "fires_if": "any capture stopped on the wall deadline", "source": "A1 R8(b), R9"},
    {"id": "STOP-R9-RATIO", "applies": "every window", "fires_if": "any capture whose cell search ran has cells / cap > 0.5", "source": "A1 R8(a), R9"},
    {"id": "STOP-BATTERY-SECOND", "applies": "epoch", "fires_if": "a second window with an adverse battery-float verdict", "source": "A-R5b"}
  ],
  "sampling_dependence": {
    "computed": "once, by the issuer, after the last window is terminal and the R9 record is committed",
    "D1_window_effect": {
      "test": "kruskal_wallis_chi_square_tie_corrected_df_K_minus_1",
      "alpha": "PLACEHOLDER",
      "window_median_range_over_S_max": "PLACEHOLDER",
      "flags_if": "p_value < alpha or window_median_range_over_S > window_median_range_over_S_max",
      "not_computable_if": "fewer than 2 windows contribute members"
    },
    "D2_serial_dependence": {
      "statistic": "lag1_spearman_consecutive_members_within_window_pooled",
      "rho_max": "PLACEHOLDER",
      "min_pairs": "PLACEHOLDER",
      "flags_if": "rho1 > rho_max or pairs < min_pairs"
    },
    "blocked_q99_when_flagged": {
      "n_eff": "floor(min(n / (1 + (n0 - 1) * ICC), n * (1 - max(rho1, 0)) / (1 + max(rho1, 0)))), minimum 2",
      "df": "n_eff - 1",
      "formula": "t(0.995, df) * sample_sd_presentation_s * sqrt(2), binary64, shortest round-trip decimal",
      "quantile_proof_required_for_df": true
    },
    "c_rule": "C = max(predecessor_C, Q99_plain, Q99_blocked if D1 or D2 flags, S)",
    "never_changes": ["membership", "S", "the preflight level screen"]
  },
  "pins": {
    "chain_sha256": "TO BE PINNED AT SEAL",
    "validator_sha256": "TO BE PINNED AT SEAL",
    "estimator_code_sha256": "TO BE PINNED AT SEAL",
    "cap_cells": "TO BE PINNED AT SEAL",
    "harness_sha256": "TO BE PINNED AT SEAL",
    "cap_rule_text_sha256": "TO BE PINNED AT SEAL",
    "roster_sha256": "TO BE PINNED AT SEAL",
    "launch_template_sha256": [
      "e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8",
      "1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd"
    ],
    "ledger_head_pin_at_first_window": "TO BE PINNED AT SEAL"
  }
}
```

**What the issuer checks from this block** (WI-13 implements these; each is a refusal):

- the registration contains no unfilled slot (the §13 grep prints 0);
- the sessions named at issuance are exactly the derivation-kind ledger sessions whose ids
  match the pattern. The operator may not omit a window, including an adverse one, which
  A-R5b already requires the operator to name separately;
- every session declared 12 slots;
- when the count rule is replayed over the windows in ledger order, using the committed R9
  record for counted and the ledger for valid, every window after the first was opened on a
  NEXT_WINDOW decision, and no window exists after a CLOSE, STOP or REVIEW decision;
- the first counting window has at least 6 valid;
- the predecessor is P8 by identifier and file digest;
- both decision identifiers are declared;
- the successor's identifier matches the approved pattern and is not the retired r1 id.

The issuer's old refusal text "requires r7 predecessor" is reworded when the issuer is changed
(A2 §3.6).

## 8. Membership, exclusions and issuance

These rules are unchanged from Revisions 1 and 5 except where marked "added".

- **Members.** Every capture of this registration's sessions that meets all of these
  conditions is a member:
  - its disposition is `valid`;
  - its stored anchor-v3 outcome resolves;
  - its median frame lies in 100–150 ms (added: A1 R7);
  - it belongs to a counting window.

  No capture is excluded on the basis of its B. There is no top-up and no retry, and no window
  is opened or withheld because of B.
- **Exclusions**, each recorded with its named mechanism and its ledger row retained:
  - `affine_clock_fit_empty` (Revision 1);
  - a failed protocol gate, which leaves the capture ordinary-invalid;
  - a recorded operator or system event;
  - `frame_out_of_covered_range`: a median frame outside 100–150 ms. The capture is flagged in
    the window report, is not a member and is not counted (added: A1 R7);
  - an adverse battery-float window (A-R5b).
- **R9 void (added: cap ruling §5 item 4).** If the count rule ends in R9_NOT_PASSED_TO_REVIEW,
  or STOP-R9-CELL, STOP-R9-DEADLINE or STOP-R9-RATIO fires, the campaign is void. Its captures
  are diagnostics and are never members under any cap.
- **Issuance** follows Revision 5:
  - retained n ≥ 12 is the floor;
  - S = max(corpus range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818 s);
  - Q99 and the quantile proof as Revision 1 specifies them;
  - C = max(predecessor C, Q99, S), with §9 adding the blocked Q99 to that maximum;
  - `zero_headroom` is recorded when C = S;
  - any member B > 0.25 s (`PLATEAU_INSET_S`) refuses issuance;
  - two or more members with B > 0.075 s mark the candidate `excursion_limited`;
  - the preflight level screen is the corpus maximum quantized to 1e-15 s;
  - the predecessor screen challenge is a diagnostic only.

## 9. Back-to-back windows: sampling dependence

**The forcing problem.** Revision 5 spaced windows at least 6 h apart. One effect of that
spacing is that captures from different windows are closer to independent draws. The t-based
Q99 assumes independent draws: it uses the SD of n values with n − 1 degrees of freedom. Two
things break that assumption:

- **Window effect:** a window-level state, such as a thermal or background condition that
  lasts the whole window, shifts all 12 captures together.
- **Serial dependence:** each capture resembles the one before it.

If either is present, the n values carry less information than n independent ones. The SD's
degrees of freedom are then overstated, and Q99 is too small.

**Why back-to-back is still the right estimand.** Claim windows will take their brackets
exactly this way: 600 s pitch and consecutive windows. The quantity to estimate is the spread
of B under that regime. Consecutive windows therefore add no bias. They can only shrink the
effective sample size, and the treatment below measures that shrinkage. It is declared here
before any capture, so nothing in it is chosen after B is seen.

**What is recorded before any B is read** (physical, blind): each window's start-state
evidence (§6.2) and each capture's median frame. None of this edits membership.

**What is computed once, after the last window is terminal and the R9 record is committed.**
The issuer computes it over the members only.

- **D1, window effect.**
  - (i) The Kruskal–Wallis test of B across the K windows that contribute members. The
    Kruskal–Wallis test is a rank test of whether several groups come from one distribution.
    It uses the chi-square approximation with K − 1 degrees of freedom and the standard tie
    correction, and reports a p-value.
  - (ii) The range of the K window medians of B, divided by S.
  - D1 flags if p < `PLACEHOLDER` (α) or if the range ratio > `PLACEHOLDER`. D1 is not
    computable when K < 2.
- **D2, serial dependence.**
  - ρ1 is the Spearman rank correlation between each member's B and the B of the next member
    in capture order within the same window, with pairs pooled across windows. Spearman
    correlation is the Pearson correlation of the ranks.
  - D2 flags if ρ1 > `PLACEHOLDER`, or if there are fewer than `PLACEHOLDER` pairs. Too few
    pairs is treated as a flag, because the check cannot then clear the data.
- **Blocked Q99, computed only if D1 or D2 flags.**
  - The window share. ICC, the intraclass correlation, is the share of B's variance that lies
    between windows. It comes from the one-way analysis of variance by window:
    - MSB = Σ n_j (m_j − m)² / (K − 1);
    - MSW = Σ_j Σ_i (B_ij − m_j)² / (n − K);
    - n0 = (n − Σ n_j² / n) / (K − 1);
    - ICC = max(0, (MSB − MSW) / (MSB + (n0 − 1) MSW)).

    Here n_j and m_j are window j's member count and mean B, and m is the mean over all
    members.
  - Effective sizes: n_eff,window = n / (1 + (n0 − 1) × ICC) and n_eff,serial =
    n × (1 − ρ1⁺) / (1 + ρ1⁺), where ρ1⁺ = max(ρ1, 0).
  - n_eff = floor(min of the two), at least 2, and df_blocked = n_eff − 1.
  - Q99_blocked = t(0.995, df_blocked) × sample SD × √2. This is the same sealed arithmetic
    string as Revision 1, with the same sample SD, only a smaller df. It is evaluated in
    binary64 and recorded as its shortest round-trip decimal, and its quantile proof is run
    and recorded for df_blocked, as for df.
- **The larger value sets C.** C = max(predecessor C, Q99, Q99_blocked, S). S, membership and
  the level screen never change. No B-based exclusion follows from any flag. The flags,
  statistics and both Q99 values are recorded in the candidate's derivation notes.

**Why this form.** The first effective size is Kish's design effect, a standard correction
for clustered samples. When the windows do not differ (ICC = 0) it gives n. When they differ
completely (ICC = 1) it gives about K, the number of windows. It therefore contains the
outline's "n_eff = windows" as its extreme case, and does not impose that case when the data
do not show it. The second is the usual adjustment for first-order serial correlation. Both
are declared rules, not fitted optima.

**Worked example.** The SD of 0.004 s is invented. The quantiles come from the issuer's own
`student_t_quantile`.

- n = 24 members in K = 2 windows of 12, so n0 = (24 − 288/24)/1 = 12.
- Unblocked: df = 23 and t(0.995, 23) = 2.807336, so Q99 = 2.807336 × 0.004 × 1.414214 =
  0.015881 s.
- With ICC = 0.2: design effect 1 + 11 × 0.2 = 3.2, n_eff = 24/3.2 = 7.5, floored to 7, so
  df 6 and t = 3.707428. Q99_blocked = 0.020972 s, and C takes 0.020972 s if S is smaller.
- With ρ1 = 0.3 and no window effect: n_eff = 24 × 0.7/1.3 = 12.9, floored to 12, so df 11
  and t = 3.105807. Q99_blocked = 0.017569 s.
- At the extreme ICC = 1 with K = 2: n_eff = 2, df 1, t = 63.656741, and Q99_blocked =
  0.360097 s. This is larger than the 0.25 s plateau inset. Part B, O-3 names this case for
  the gate.

## 10. Blindness and sequence

These are unchanged from Revision 5 except for the dry run's allowed contents.

- No B value, screen or statistic of these windows is read by any person or agent before two
  things are true: the last window's session is terminal, and the R9 record has been committed.
- `prepare-candidate` refuses while any session of the registration is open.
- Between windows, the count-only dry run and the harness report may state: session kinds and
  states; declared and filled slots; valid counts; exclusions by mechanism; median frames; and,
  per capture, cells, cells ÷ cap, disposition and stop trigger. They state no B, no screen
  and no comparison with either.
- The R9 record is an ancestor of every commit that carries a B of these windows.
- This registration authorizes no claim window. H1 stands until the closing ruling of E1 §4
  step 18.

## 11. Stop lines kept

These are kept from Revision 5 and the cap rule, with where each question goes when the line
is reached:

- **Cadence:** a window whose median of per-capture median native frame lengths is above
  150 ms stops the sequence. Revision 5 applied this at W1 only; here it applies after every
  window. The window's cadence report is read from raw plists before any B.
- **Futility:** the first counting window with fewer than 6 valid of 12 stops the sequence.
- **Battery:** an adverse window is replaced once (A-R5b). A second adverse window stops the
  sequence.
- **Cap rule R8 and R9:**
  - any capture stopped on the cap or on the wall deadline stops the sequence, and R9 fails;
  - any capture with cells ÷ cap above 0.5 stops the sequence, and R9 fails;
  - a capture outside 100–150 ms is flagged, is not a member and is not counted.
- **Count exhaustion:** see §7 clauses 3 and 4.
- **Issuance floor and refusals:** see §8.

Every stop goes to review: a consult, a cold gate or the owner (D-186). None is "stop for
good". The value of the cap is never adjusted between captures or between windows (A1 R10).
A later change to a pinned estimator file restarts the cap rule (A1 R12). A fix in the
calibration derivation path means these windows are re-run under a new revision (E1 step 17;
directive #416 item 3).

## 12. What this revision does not change

It leaves unchanged:

- the identity epoch, the machine pins and the launch context;
- protocol v3 and the window shape except spacing;
- the membership, exclusion and analysis rules of Revisions 1 and 5, except where §8 and §9
  add to them;
- the TWO_DRAW_PREDICTION_RULE string and the quantile-proof bounds;
- the A-R5b battery-float rule except its spacing clause;
- the Revision 1 known conditions;
- any sealed text concerning W1 and W2.

It publishes no number, licenses no measurement and arms no window.

## 13. Seal procedure

1. Replace every pin slot with its value, taken at the head the first window will be armed
   from. Have the cold registration gate replace every threshold slot with
   its sized value.
2. Run `grep -c -E 'TO BE PINNED AT S[E]AL|PLACEHOLDE[R]'` on this file. It must print 0.
3. Replace the header's parenthetical "(DRAFT 2026-09-30; sealing pending the cold
   registration gate and the pins below)" with "(sealed <YYYY-MM-DD> at <first 8 hex of the
   sealing commit>)".
4. Pin the sha256 of the whole registration file in the first window's arm material.
5. Owner approval: the owner's answer of 2026-09-29 (record item 46, "Approve all four") is the
   approval E1 step 12 requires. The seal needs no second ask unless the cold gate changes a
   rule the owner approved: the P8 name, the successor pattern, or the rule that the 12 rows
   do not count toward doubling.

---

# Part B: writer's notes (not sealed)

## Checks the writer ran (read-only)

- The 12 set-aside identifiers were read from `configs/calibration/observation_dispositions.json`
  on main `0009b976`. The registry holds 23 rows (11 D-126 plus 12 E1). The file's sha256
  `4a3d96da…` equals `DISPOSITION_REGISTRY_SHA256` in `joulewise/calibration_dispositions.py`.
- Main `0009b976`:
  - the chain digest is still `b5beea46…`, unchanged by #441;
  - the validator digest is `3dc75857…`, after #444. This is for orientation only; the seal
    takes the value then in force;
  - the two launch templates hash to Revision 5's values;
  - `/usr/bin/powermetrics` hashes to `b762e5bf…`;
  - `sw_vers` reports 25G83.
- The doubling rule was read at `joulewise/calibration_bracketing.py` (threshold 2 ×
  `corpus_n`; the count excludes rows set aside by declared decisions). The issuer's shape
  rules were read at `scripts/issue_calibration_acceptance_generation.py:1815–1880`: {2, 3}
  sessions for Revision 5, W1/W2/W3 order, W1 futility, and the W3 refusal at ≥ 12 valid. All
  of these must become registration-driven (WI-13).
- The t quantiles in §9 were computed with the issuer's own `student_t_quantile`. No B value
  of any capture was read.
- **The issuer parses this file.** `preregistration_epoch_pins` requires exactly one distinct
  match of `os_build:\s*…` and of the phrase "/usr/bin/powermetrics sha256 in force is <hex>"
  across the whole file. Part A therefore writes the epoch as `` `os_build` = `25G83` `` and the
  JSON key as `"os_build":` (neither matches the regex), and does not restate the powermetrics
  phrase. Any edit before the seal must keep that property. Part B must not be appended.

## Open for the cold registration gate

**Placeholders to size** (they must be numbers before the seal):

- **O-1. D1 thresholds.**
  - α for the Kruskal–Wallis test.
  - The maximum ratio of the range of window medians to S.
  - Also: whether the p-value comes from the chi-square approximation, as drafted, or an exact
    permutation, and which implementation is pinned.
- **O-2. D2 thresholds.** ρ_max for the lag-1 Spearman correlation, and the minimum number of
  pairs. Also confirm the pairing rule: consecutive members, skipping non-member slots, rather
  than adjacent slots only.
- **O-3. Blocked Q99 formula and its extreme case.** The draft uses Kish's design effect and
  the AR(1) adjustment. The critical-path outline said "n_eff = windows". The draft's form
  contains that as its ICC = 1 limit, but it is still a choice. At K = 2 and a strong window
  effect, Q99_blocked reaches about 0.36 s (§9 example), which is above the 0.25 s plateau
  inset. The gate should decide whether such a case issues, with C carrying it, or goes to
  review. Any rule chosen must not read B to decide on a further window.
- **O-4. Direction of "the larger value sets C".** A larger C admits more budgeted drift and
  widens the reported uncertainty budget. The brief and the outline both say "larger". The
  gate should confirm this is the conservative direction for the claims C feeds.
- **O-5. The idle-power reference in §6.2(e).** The derivation chain does not run the
  controller's `cooldown-v2` gate and has no reference baseline. Options:
  - a baseline measured at C1's settle;
  - a fixed calibrated ceiling;
  - striking (e) and relying on (c), (d) and (h).

  (e) cannot be enforced as written until one is chosen and implemented.
- **O-6. The session-id pattern** `^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$` is the writer's
  proposal. It must be compatible with `gen_derivation_night.py`'s census check on session ids.

**Conflicts between rulings, and the reading the draft takes:**

- **O-7. Spacing.**
  - E1 §4 step 12 says "Run two non-claim windows of 12 slots, at least 6 hours apart, no
    agent session active". A1 §5 step 10 and the cap ruling §6 step 7 say the same.
  - The draft replaces the 6 h on the owner's 2026-09-29 cadence rule (cadence audit F1;
    record items 32 and 46) and keeps "agent-free".
  - The gate should record this as an owner-directed supersession of a cold-ruled clause.
    The seal record should quote the owner's own words for "back-to-back / only physics waits",
    as Revision 2 quoted issue 316. The writer had the orchestrator's paraphrase, record
    item 32 ("windows back-to-back") and item 46 ("Mix … ≈3 back-to-back windows"), but no
    verbatim sentence for "only physics waits".
- **O-8. H6 and restore-ON.**
  - A1 R9 ("with H5 and H6 met") and A1 K3 (slew-attested captures do not count) conflict with
    D-186, which withdraws H6.
  - So do E1 step 13 ("the H6 log check per capture") and A1 K2 ("restores ON after the last
    capture").
  - The draft follows D-186, which the owner ratified: one settled OFF receipt per window, no
    per-capture log check, no restore, and "counted" defined without H6.
  - Closing conditions C5 ("an H6 count of zero") and C9 (K2's arming refusal) are not
    registration text, but they need the same re-reading at the closing ruling.
- **O-9. The number of windows.**
  - A1 R9 permits "a third [window] only if fewer than 24 captures counted" and ends the test
    after the third.
  - The brief and the outline say "maximum 4 windows".
  - The draft reconciles them: T-count may open windows up to the third; T-valid alone may
    open a fourth, and only when ≥ 24 were counted after the third. That respects R9's end
    state. The gate should confirm this reading, or cap at 3.
- **O-10. Which count T-valid reads.**
  - A2 row 7 says "valid", which is the ledger disposition. The issuance floor, however, is on
    members: valid, resolved and in range.
  - Using "valid" can close the campaign with valid ≥ 12 and members < 12, in which case
    nothing issues and the campaign goes to review.
  - Member counts are also available blind, since the dry run reports exclusions by mechanism.
    The gate may prefer "members ≥ 12" in the trigger. The draft keeps A2's word.
- **O-11. Scope of the cadence stop.** Revision 5 applies the 150 ms stop at W1 only. The draft
  applies it after every window (§11), as the outline's §4(b) start condition implies. This
  makes the rule stricter; confirm it.
- **O-12. Append or a separate file.**
  - Appending changes the prereg file's digest from `81b65f08…`. The W1/W2 arm material binds
    that digest, which stays recoverable by commit.
  - The issuer's 25G83 path requires "# Revision 5 (" in the file (`:1775`), so appending
    needs no issuer change for that check.
  - A separate file would need one. The draft recommends appending.
- **O-13. Disclosed design inputs.**
  - The cap ruling §5 item 5 says the successor registration lists, as disclosed design
    inputs, the 12 r1 member values, the 8 cap-stop diagnostic values and the seats that
    computed them.
  - The writer did not transcribe B values. Doing so needs a reader of the r1 bytes and the
    cap-council replays, and the brief did not ask for it.
  - The gate decides between citing them by file and digest (r1 bytes `dbad7cc7…`; the
    cap-council seat records) and transcribing them as Revision 5 did for the eleven
    2026-09-19 values.
- **O-14. The "every" in R9's ratio clause.** R8(a) limits the 0.5 ratio to captures inside the
  frame range. R9 says "every cells ÷ Cap at or below 0.5". The draft reads R9 literally:
  every capture whose search ran, including captures out of range. That is stricter; confirm.
- **O-15. The chain settle is redundant.** The driver now settles 600 s after the OFF receipt,
  and the chain settles another 600 s (record item 34; outline §2). Removing the chain's settle
  changes the pinned chain digest. It must be done before the seal or not at all. The draft
  keeps Revision 1's shape.
- **O-16. The control option.** The outline offers "one window pair ≥ 6 h apart as a control".
  The draft does not require it. The owner's "Mix" blocks may produce such a pair naturally,
  and D1 covers it either way. The gate may make it a rule.
