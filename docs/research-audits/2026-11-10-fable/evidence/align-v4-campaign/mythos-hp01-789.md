# Seat: Mythos 5.2, #789 hp-01

`date`: Sat Nov 14 15:16:11 PST 2026 (taken at the start of the seat). Cold seat for RL-149 §2.8 line 1; I did not write this code or kit.

## Verdict

**ADMIT WITH FIXES** for hp-01's §2.8 line 1 (code at `d8ae17db2`, kit `bd7c8711…`).

- I found no path that puts the host into a measurement in High Power unnoticed. The marker is written before the mode changes, the close runs on every exit the process survives, and every measuring entry point reads the mode first.
- Line 1 is met when F1 to F3 are closed and the lead records it. All three can close with procedure text, with no frozen-byte change and no re-pin.
- If the builder fixes any of F1 to F7 in code instead, those bytes must land before H001-H003 arm. Otherwise the smoke runs on different bytes than L004-L012 (RL-150 R5, class A).

## What I checked

Read via git only, at `a95812f14`.

| Check | Result |
|---|---|
| Kit sha256 | `bd7c87115e6f…dcda9`, matches |
| Frozen paths vs dev-01's pin (`b4b6aeb19` → `d8ae17db2`) | Exactly five of the 37 blobs differ: `desk.py`, `kit.py`, `legs.py`, `stops.py`, the runner |
| The five changed hashes, plus `powermode.py` and `align_r1_rehearsal.py` | Re-hashed from the blobs at `d8ae17db2`; all seven match the kit |
| The other 30 hashes | Equal to dev-01's kit and the blobs are unchanged; they rest on dev-01's validated pin |
| Twelve seeds | Recomputed from `sha256("cl-hp-01\|2026111403\|seed\|i")`; all twelve match |
| Kit diff against `cl-dev-01` | Only id, title, `frozen`, `power_mode`, master seed and seeds, rule 6 text, `pilot_counted` → `hp_smoke_counted`, `never_in_the_fit`, stop notes |
| Plan arithmetic | Recomputed by hand; correct (item 4) |

**Not done.**
- No test, mock, `plan`, `validate-kit` or mutant was run. The builder's test and mutant counts are unverified.
- CI on `a95812f14` was pending (`build`, `changes`, `fences`) when I looked. Line 2 is the lead's.
- No measurement, slot, transcript, energy, power, meter or powermetrics file was opened. No SSH. No file was edited.

## Findings

### Close before H001-H003 arm

**F1. An absent proof is not a stop. MEDIUM.**
- `stops.py:45` fires RESTORE_UNPROVEN only on an explicit `restore_proven: false`.
- After SIGKILL, power loss, or a failed receipt write (`cadence_legs_runner.py:717`), there is no `result.json`. Only REFUSAL fires (`stops.py:40`).
- RL-155 §3.1 scopes REFUSAL to campaign spans and lets Part C run; "restore unproven" holds everything. So the path most likely to leave the host at 2 gets the weaker stop.
- An older desk drops the key silently (`desk.py:137`, `:145`), so the Air's desk must carry this PR.
- **Fix now (procedure):** one line in the arm record: "for an hp-01 span, no receipt, no `span/result.json`, or anything but `restore_proven: true` is RESTORE_UNPROVEN and holds everything". Record that the Air desk is at or after `d8ae17db2`.
- **Fix in code (v1.1 or any re-pin):** the desk passes the block's mode to `evaluate_named_stops`, and `restore_proven is not True` fires for a High Power kit.

**F2. SIGKILL recovery is detection plus a human, not automatic. MEDIUM.**
- Detection is real. `read_power` refuses anything but 0 at every campaign and smoke start (`run_align_r1_smoke.py:98-102`), and rule 6 excludes a leg in the wrong mode.
- Nothing in the campaign lane restores:
  - An Automatic span refuses at `read_power` and leaves the marker.
  - A High Power span refuses at `high_power_marker_absent` (runner `:524-529`).
  - The watchdog's restore is scoped to W1 markers and returns `not_owner` for this one (`magistrate_watchdog.py:1155-1157`, `powermode.py:307`).
- Only v4-lane entries restore: the v4 install's `session_start_restore` (`align_v4_session.py:1733`), a W1 night admission, and the R1 driver's guard entry.
- The "arm checklist" judges observations the magistrate supplies by hand (`cadence_queue.py:92-94`). This kit keeps `t0_local 13:20`, so `span_window` (`kit.py:526`) fails at any other t0, and RUN_STATE 317 already says not to run that command.
- The plan's manual restore is a bare `sudo pmset` outside the host lock (`cadence_queue_design.md:533`), and it covers only a failed proof, not a missing receipt.
- **Fix (plan text):**
  - Name the two close lines as hand lines, with the path `/Users/Shared/JouleWise/host-power/high-power.marker`.
  - Do the manual restore through `powermode.restore_owed([host_marker_path()], reason=…)`. It takes the lock, reads back, and removes the marker only on 0.
  - Apply the same step when a span leaves no receipt.

**F3. A leg in which the mode changed stays admitted. LOW to MEDIUM.**
- The leg records its mode once, at G0 release (`workload.py:440`). The runner checks before each attempt (`:482-483`).
- If the check before leg n+1 fails, the span stops, but leg n keeps `admitted: true`.
- The last leg of a span has no later observation: the guard's restore does not read the mode first (`align_r1_rehearsal.py:418`).
- This is the same standard as an Automatic leg, so it is not a ruling breach.
- **Fix now (procedure):** the hand-read rule: "a span that stops at an `-powermode` step puts the preceding leg to the research lead under rule 6".
- **Fix in code:** one `observe()` before the close's restore, recorded in the receipt.

### Recommended, not blocking

**F4. The close makes one restore attempt. LOW.** `self.runner(self.AUTO)` is unguarded (`align_r1_rehearsal.py:418`) and `host_run` has a 15 s timeout (`run_align_r1_smoke.py:73-75`). One transient sudo failure leaves the host at 2 until a human acts. It is detected (the proof fails). Fix: up to three attempts when the proof fails and the guard did not defer.

**F5. A second signal can skip the close. LOW, pre-existing pattern.** In `run_span`'s `finally` (`:604-606`), a different signal arriving while the loop sets `SIG_IGN` raises before `_close` runs. The window is microseconds, and the marker survives. Fix: block the three signals with one `pthread_sigmask` call before the loop, or nest `_close` in its own `finally`.

**F6. Two unasserted reads. LOW.**
- `before_high` is recorded but not required to be 0 (`:316`), so a mode change during the soak would pass.
- The per-leg check tests marker presence, not that the marker is this span's (`:542-546`).

**F7. Kit rule 6 overstates. LOW, text.** "On every exit path the close restores…" is untrue of SIGKILL and power loss. Correct it at the next re-pin; it need not change for the smoke.

**F8. Doc arithmetic. NIT.** `cadence_queue_design.md:543`: 16:50 plus 32,850 s ends at 01:57:30, not 02:02:30. The conclusion stands.

**F9. The stop also fires on spans that never touched the mode. NOTE.** A span refused at preflight under someone else's High Power reports `restore_proven: false`. That is conservative and I would keep it.

## The six attack items

**1. Left in High Power, or a stale marker.**

| Path | Outcome |
|---|---|
| Exception or signal between marker and `pmset 2` | Close restores; `touched` is set first (`:315`) |
| Marker write fails (disk full) | `high()` stops before the mode changes |
| Lock held at start | Refused before any feed (`:517-522`) |
| W1 marker race | Only in the retake's release-to-acquire window; the v4 install takes the lock (`align_v4_session.py:1712-1719`). The guard defers and the stop fires |
| Close ordering | Restore runs first, before the feeds stop. After a SIGTERM it starts within about 70 s (child teardown, `run_night.py:536-601`), inside the launcher's 180 s grace |
| Journal fails at the close | Power steps run directly (`:672-677`) |
| Later span or W1 session starting in High Power unnoticed | No: every entry reads the mode |
| SIGKILL or power loss | F1 and F2 |

**2. Guard and kits.**
- A High Power kit cannot run without the guard. The base validator refuses the key, and the runner requires HEAD and the working-tree hashes to equal the kit's (`:341-356`).
- An Automatic kit cannot trip the guard: every High Power step is behind `mode == 2`.
- v1 kits validate unchanged (`kit.py:257`). `cl-dev-01` and `cl-dev-02` pin `b4b6aeb19`, so their runs never touch these bytes.

**3. The kit.** It is a correct §2.3/§2.5 type-H block: 12 legs in dev-01's cell, and the leg-executing bytes are identical to dev-01's. `hp_smoke_counted` matches RL-150 R5, `never_in_the_fit` matches §2.3 and §2.5, and `block_power_mode` matches the code. Seeds and hashes are correct. F7 is the only text defect.

**4. Plans.** All correct against RL-155a's fence.

| Span | Fence | Latest t0 |
|---|---|---|
| L001-L003 | 16,650 + 1,460 = 18,110 s | 20:48:10 |
| L004-L012 | 32,850 + 1,460 = 34,310 s | 16:18:10 |
| L004-L009 | 24,750 + 1,460 = 26,210 s | 18:33:10 |

"No launch 10:50-13:15" is right: these bytes carry 11:45-13:15 (`align_r1_rehearsal.py:64`) and the soak path waits it out (runner `:395`).

**6. Countability and the next Automatic block.**
- Countability: F3, and the rule that any frozen-path fix lands before the smoke.
- A later Automatic block's start state is not at risk once the proof holds. Each span has its own soak, and `read_power` gates the mode.

## 5. The builder's seven questions

None is a safety defect. All are design choices for the research lead.

1. **Soak mode.** Keep it Automatic. The soak bytes and L001's cold start stay comparable with dev-01, and time in High Power is shortest. The hand-read should show L001 separately, since it starts just after the switch.
2. **Restore under an unproven child.** The builder is right to restore. The child holds no lock here, the leg is already out of the data, and leaving the host at 2 is worse. R1's R8-1 clause is dead code in this runner. Record the unproven child in the receipt.
3. **Seeds.** Leave them independent. §2.5 asks for matched blocks, not matched legs, and every leg decodes to the cap. Pairing would be a v1.1 seed-law field, decided before any energy is read.
4. **Reserve.** The rule is vacuous for a one-block phase. As written, an excluded H leg is not replaced. That is acceptable for a descriptive block unless the research lead rules a High Power reserve span.
5. **Budgets.** The fence uses the process cap, so it is unaffected. Whether G0 and decode shift is what the smoke shows; LEG_OVERTIME needs two legs over 1.5 times budget.
6. **Scope of the close proof.** Make it universal in v1.1, never by re-pinning the dev kits. That also closes F1 cleanly, because "absent" would stop meaning "Automatic".
7. **The blackout.** It cannot happen on a valid plan: `plan_span` refuses any span whose worst case meets a blackout (`legs.py:269-272`). Keep that refusal for High Power kits.