FINAL PASS: FAIL

# Second cold final pass on PR #483 (`6796b8e0`, feat/2026-10-05-v5-qualification-code)

Seat: Fable 5.1, cold, one session, foreground, read-only on the checkout. Read first: the earlier ruling
(`fable-int.md`, at `898c49a7`). Then the whole `joulewise/` + `scripts/` diff `898c49a7..6796b8e0` (3,402 diff
lines), and the surrounding code wherever the delta touches it. Scratch only under `/tmp/dd5-fable-int2/`. The
checkout is unmodified (`git status` empty at the end).

## Ruling in one paragraph

Nothing in the delta admits a window or a member that should be refused, and no energy, power or per-member
duration reaches a public output. The change still fails, on the same side as last time and for the same reason.
Three defects, each fixed by the code and independent of how the machine behaves, each confirmed by execution:
(B1) gate G1 fails every real `s1` after the launch is consumed; (B2) the G10 clock control can no longer be
discharged at all, and a real attempt would spend its one network-time ON finding that out; (B3) every re-armed
attempt (a fresh `s1` after a NULL or an admission abort, or an `s2`) has its harvest refused after its launch.
The delta's own focused suite is green while all three hold (183 passed, 139 subtests, 392 s), because at each of
these seams the tests replace the real producer with a mock or a hand-written record. Do not run G10 and do not
arm `s1` on this head. `a1` and `a2` are not touched by B1-B3.

## Status of the earlier findings

| Earlier | Status at `6796b8e0` |
|---|---|
| B1 (G9 two-root layout) | Cured. G9 now authenticates the ARM context through the chain pin and uses one shared four-copy source table (`joulewise/t0_rehearsal.py:669-679, 1329-1348`). The native close-out -> real G9 test passes (`tests/test_v5_block4_composed.py`). |
| B2 (G1 absence probes) | The four author absence censuses and the group census are cured. The cure is too broad: see new B1. |
| M1 (public locators) | Cured. Public `replay-locators.json` carries SHA-256 only; size and mtime stay under `withheld/` (`joulewise/v5_qualification.py:743-748`). |
| M2 (G2-b depended on G10 custody) | Cured. The G2-b harvest no longer resolves or replays G10 custody. |
| M3 (frequency gate by pack name) | Cured as written (selected by plan profile, `joulewise/arm_readiness.py:5887`). That cure is the cause of new B2. |
| Required item 2 (one composed test, real journal -> assemble -> evaluate) | Not done. `tests/test_v5_block4_composed.py:1-7` says so itself. G3, G5 and G8 remain unproven on native producer output. |

## Findings

### B1. BLOCKER (priority 6). G1 fails every real `s1`: the maintenance census is registered as an absence probe

Terms. G1 is the qualification gate that checks every process the `s1` driver spawned (recorded in a process
journal) against a *registered outcome*: the exit code, and for some commands the standard output, that a clean run
must show.

- The cure for the earlier B2 registers every command whose executable is `/usr/bin/pgrep` as an absence probe:
  it must exit 1 and print nothing (`joulewise/t0_rehearsal.py:658-667`, applied at `:720-727`; the assembler uses
  the same table, `scripts/produce_t0_rehearsal_bundle.py:505-506`).
- The T-0 author runs one `pgrep` that is not an absence probe. Its maintenance census,
  `/usr/bin/pgrep -lf 'XProtect|mds_stores|mdworker|...|Spotlight|mediaanalysisd'`, lists the background daemons
  that exist, and the author accepts exit 0 or exit 1; the CPU samples that follow decide
  (`joulewise/arm_readiness_evidence_t0.py:1390-1402`). On macOS `mds_stores`, `Spotlight` and the XProtect
  services are always running, so this probe exits 0 with a non-empty list.
- The probe is mandatory for this pack: row `t0.background_quiet` is in the GAMMA profile
  (`configs/arm_readiness/d117_row_registry_v2.json`), and the pack declares GAMMA. The author runs in-process
  under the journal (`scripts/run_night.py:2289`, journal opened at `:4986`).

So a window the author admits is a window G1 fails, exactly as before, through a different probe.

Evidence (`/tmp/dd5-fable-int2/test_g1_maintenance.py`: the real `_execute_probe` under a real journal, mapped with
the assembler's rule, judged by the real `evaluate_g1`; run on this Mac):

```
maintenance pgrep: exit 0 | matched lines: 17 | author accepts: True
registered outcome: {'exit_code': 1, 'stdout': ''}
G1: FAIL | governed process 1 did not complete successfully | sequence_completed: False
```

Consequence: `g1_not_passed`, `verdict=FAIL`, `end_state=true`, after the launch. Why the suite is green:
`tests/test_v5_s1_qualification.py:48-62` and the composed test list five `pgrep` commands and omit this one.

Cure direction: register outcomes per exact argv, not per executable (the maintenance census needs
"exit 0 or 1"). The comment at `t0_rehearsal.py:656` ("all governed pgrep argv are absence probes") states ruling
76 addendum C and is false for this argv, so the addendum needs correcting too. Two related cases I did not
execute: an R1 time-server query that fails is tolerated by the author as a missing leg
(`arm_readiness_evidence_t0.py:1164-1168`) but fails G1 (registered exit 0); and the driver's group-census polls
(`scripts/run_night.py:4501-4533`) return exit 0 while a group is still exiting. Neither occurs on the normal path
of a clean window.

### B2. BLOCKER (priority 3). G10 cannot be discharged: the author refuses on the sizing binding before it reaches the anchor check

Terms. G10 passes only if, after network time is switched on and the clock really moves, the real T-0 author
refuses with one exact detail string, `R0-to-author RAW anchor delta exceeds 5000000 ns`. The *sizing binding* is
the new file `kernel-frequency-binding.json`, which ties the stream maximum used by the frequency gate to one
occurrence's plan, chain and sizing source.

- The author now replays that binding whenever the pack's profile requires a clock attestation, or a binding file
  is present (`joulewise/arm_readiness_evidence_t0.py:783-791`). Every registered profile requires it (row
  `clock.correct_and_prior_state`), so this applies to any pack G10 could use. The replay runs when the author
  loads R0 (`:1189`), before the anchor comparison (`:1237-1238`).
- The replay requires the inputs directory to be exactly `<plan custody>/<pack>/arm_readiness.t0.inputs`
  (`joulewise/v5_qualification.py:474-477`).
- The G10 helper always runs the author on a *copy* of the inputs, under its own new custody directory
  (`scripts/ed_session/capture_t0_anchor_positive_control.py:206`), and refuses if that directory overlaps the
  source (`:201-203`). The copy can therefore never be at the path the binding names.

So the author refuses with `clock_sizing_plan_mismatch` (or `clock_sizing_binding_invalid`, or a missing-file
error), the helper compares the detail with the anchor string (`:308-312`), and the control ends
`NOT-DISCHARGED / author_exact_anchor_refusal_missing`. By then the ON command has been sent and the clock has
been synchronized.

Evidence (`/tmp/dd5-fable-int2/test_g10_real_budget.py`: the PR's own passing G10 happy-path fixture, with one
change: the production `authenticated_clock_budget` is left in place instead of the mock):

```
Drift-corrected anchor movement: 500000000.010 ns (must exceed 5000000 ns).
helper outcome: {'status': 'NOT-DISCHARGED', 'reason': 'author_exact_anchor_refusal_missing'}
ON sent: True | author detail: 'clock_sizing_binding_invalid'
required detail: 'R0-to-author RAW anchor delta exceeds 5000000 ns'
```

The fixture's binding file is a placeholder, so the refusal string here is `..._binding_invalid`; with a real
binding the path test at `v5_qualification.py:474-477` gives `..._plan_mismatch`. Either way it is not the anchor
string. Why the suite is green: both G10 test files write a placeholder binding and mock the replay
(`tests/test_t0_anchor_positive_control.py:66-69, 142`; `tests/test_capture_t0_anchor_positive_control.py:27-35`),
with the comment that the seam "is independent of this anchor test". In production it sits in front of it.

Consequence: `s1` cannot be planned (G10 is a prerequisite), Ed's one attempt is spent, and the clock offset is
back near zero, so the 20 ms preflight band will not be met again for about two hours at today's drift. This
does not consume the `s1` launch. The same new obligation also means the G10 input capture itself needs a
writer-staged occurrence custody (`scripts/capture_t0_step.py:815-820`), which recipe 46 does not provide for.

On the question asked: where G10 can run, it still proves what it should. The preflight is read-only and only
gates the attempt; discharge still requires a drift-corrected anchor movement above 5 ms between stamped samples
and the real author's refusal, and the replay now also checks the preflight record, every poll, and the order
`a2` expiry < preflight < ON < OFF < first `s1` capture on one boot
(`capture_t0_anchor_positive_control.py:380-383, 446-456`; `joulewise/v5_qualification.py:593-615`). I found no
way for the preflight or the placement to pass it without a real resync.

### B3. BLOCKER for every re-armed attempt (priority 6, priority 2). The harvest and the close-out read the network-time receipt with the wrong plan id

Terms. Two different identifiers are both called `plan_id`. The *pack plan id* is in the committed pack's
`calibration_plan.json`. The *night plan id* is in the night plan the writer stages for one attempt.

- Until this delta the writer required them to be equal. It now requires that only for `a1`/`a2`
  (`scripts/write_v5_qualification_plan.py:545-546`), and the attempt history requires every attempt to have its
  own night plan id (`joulewise/v5_qualification.py:257-258`; archive layout `attempts/<plan_id>/`). A re-armed
  attempt on the same pack therefore always has a night plan id different from the pack plan id.
- The T-0 capture writes the network-time OFF receipt with the pack plan id
  (`scripts/capture_t0_step.py:302, 772`), and the author reads it back with the pack plan id
  (`joulewise/arm_readiness_evidence_t0.py:1297-1299`). The window is admitted.
- After the window, the G2-b harvest reads the same receipt with the night plan id
  (`scripts/harvest_v5_g2b_window.py:641-642`), and so does the desk close-out
  (`scripts/v5_s1_desk_closeout.py:172`). `read_receipt` raises `OFF receipt window/plan mismatch`
  (`joulewise/network_time_off.py:81-83`).

Consequence: the structural harvest of any such attempt is `REFUSED / archive_authentication_or_tool_fault`
(`harvest_v5_g2b_window.py:713-715`), and the close-out raises before the backups, so G9 cannot pass either. The
launch has been consumed. The X7 lane adapted the GO and ARM checks to the two ids
(`joulewise/arm_readiness.py:10215`, `joulewise/night_gate.py:1341`, `scripts/run_night.py:2427`) and missed
these two readers. Evidence for the reader (`/tmp/dd5-fable-int2/test_history.py::test_off_receipt_plan_id`):

```
night plan_id == frozen id: harvest/closeout read OK
night plan_id of a re-armed attempt: OFF receipt window/plan mismatch
```

The first `s1` is unaffected only if the lead gives its night plan the pack plan id, which nothing requires any
more. No test runs a harvest with the two ids different.

### M1. MEDIUM (priority 2). A never-started `s2` lets the block take a launch the allowances do not grant

The rule in `attempt_history` for a fresh `s1` is "the previous attempt is NULL, or an admission abort, or a
no-science tooling recover" (`joulewise/v5_qualification.py:305-316`). It looks only one record back. After an
`s1` that ended RECOVER with a tooling cause (the state from which only one lead-authorized `s2` is allowed), an
`s2` that never starts is recorded NULL, and:

```
control: fresh s1 straight after s1 RECOVER(tooling):        REFUSED fresh_s1_predecessor_not_rearmable
second s2 after s2 NULL:                                     REFUSED s2_not_after_named_tooling_recover
fresh s1 after s1 RECOVER(tooling) -> s2 NULL:               ALLOWED s2_count=0 aborts=0
s2 after that launched s1 (third launch of the block):       ALLOWED s2_count=1 aborts=0
```

(`/tmp/dd5-fable-int2/test_history.py::test_s2_null_launders_end_state`, on the PR's own X7 helpers.) Two defects
in one: the correct next step (re-arm the authorized `s2`, since a NULL spends nothing) is refused because
`tooling_s2_predecessor` requires the immediately preceding record to be an `s1` (`:201, :300`); and the only step
the code allows is a fresh `s1` that carries no `s2` authority, after which a further `s2` is allowed because NULL
`s2` records are not counted (`:295`). Cure direction: evaluate both rules against the nearest non-NULL
predecessor. The admission-abort allowance is counted across the whole chain (`:301-304`) and is not affected.

### M2. MEDIUM (priority 2, fail-closed). The first harvest of an attempt is its counted record for ever

`checked_history(..., replay=True)` reads the original `attempts/<plan_id>/harvest.json` and ignores the
re-harvest's verdict (`joulewise/v5_qualification.py:427-435`), and a predecessor pointer must name that original
file (`:269`). If the first harvest is REFUSED for a tooling reason (B3 produces exactly that), the standard cure
"fix, then re-harvest the identical bytes" yields a correct verdict under `reharvest-N/`, but every later plan is
judged against the REFUSED original:

```
fresh s1 after REFUSED original harvest: REFUSED fresh_s1_predecessor_not_rearmable
s2 after REFUSED original harvest:       REFUSED s2_not_after_named_tooling_recover
```

Nothing bad is admitted; the block simply cannot continue without a ruling. Decide which record counts when a
re-harvest supersedes a REFUSED original, and encode it.

### L1. LOW. Notes that do not change the ruling

- An attempt exists for the history only once it is harvested. Two plans can name the same predecessor until the
  first of them is harvested (then `attempt_history_fork` refuses both). The physical interlock is the ledger: a
  T-0 that reached reservation leaves rows that block the next T-0 until the NULL restore, which itself demands
  the NULL harvest.
- NULL restore, read and not executed beyond the PR's tests: it removes exactly two lines, only when the live
  ledger is `seed + append-intent + session-open`, the seed head equals the unchanged pin, the row equals the
  receipt in this attempt's own T-0 capture, the capture's argv matches the frozen ARM identity, and
  `chain.started` is absent, all under the native writer lease, with the attempted bytes saved first
  (`scripts/restore_v5_null_reservation.py:34-62, 84-111, 135-172`). I found no path that removes another row.
  Latent: its replay re-hashes the live pin file (`:197-200` of the same file), so once the measurement checkout itself moves to
  the advanced pin, history replays of a restore-bearing attempt will refuse.
- The latest-chain-start instant is `t0 + cap` (`joulewise/night_gate.py:1269`), but the chain starts after the
  T-0 stage (up to the 3300 s cap) plus the post-stage authoring, which is charged to the span as
  `pack_t0` = 360 s. A stage that uses nearly the whole cap is therefore refused at GO (before the launch), and
  the in-chain `test "$(date +%s)" -le ...` line runs after consumption, a few seconds later. Realistic stages
  (dwell at most 2700 s) fit.
- `size_window` does not assert that the cooldown allowance is at most the stream maximum; it is true by today's
  numbers only (next section).
- The stage list is now hashed at authoring, at launch-input assembly, and inside capability reconciliation
  before the claim (`joulewise/arm_readiness.py:9576-9595, 9756-9764`; `scripts/launch_window.py:183-187`). Read;
  consistent with the chain line the writer emits (`scripts/write_v5_qualification_plan.py:407`).
- Sealed `scripts/prewindow_check.sh`: the delta restores the pre-PR lines; I did not byte-compare with `main`.
  The new T-0 dwell output is accepted by the author's parser (executed: real `t0_wait` on a fake clock ->
  `final_clean_dwell` True).

## The six questions

1. **Admit what should be refused, or let a non-claim byte reach a claim path?** Nothing found. The new sizing
   binding, stage-list attestation, history keys in the authorization record and the `s1`/`s2` marker checks all
   add refusals. `s1`/`s2` stay behind `claim_eligible=false`, `permitted_blocks=1`, purpose `G2B_SHAKEDOWN`
   (`v5_qualification.py:336-347`). The controller's G2-b attachment route arrived by merge from `main` (#481,
   #482) and was read once only.
2. **Attempt history and NULL restore.** History: M1 (an unauthorized launch through a NULL `s2`), M2 (REFUSED
   original is permanent), B3 (re-armed attempts cannot be harvested). No double counting found: re-harvest and
   qualification records sit below `attempts/<id>/` and are outside the census glob. NULL restore: sound as read.
3. **G10.** Still a real proof where it can run; it cannot run to discharge on this head (B2).
4. **Frequency gate and sizing.** Consistent: the writer pins the sizing hash and the computed maximum in the
   chain; R0 capture, author, ARM (`arm_readiness.py:6419-6433, 6913-6918`) and G4 (`t0_rehearsal.py:927-938`) all
   recompute it through one function and compare it with the gate file and the chain literal. Cooldown exclusion
   is sound today: the cooldown runs under its own run id and sampler after the member's sampler stops
   (`joulewise/controller.py:3413-3416`), its cap is 300 s (`controller.py:165`, `schemas.py:524`), and the stream
   maximum is 335 s (members: 292 s and 313 s sampled against 314 s and 335 s streams). So no stream is longer
   than the gated maximum.
5. **Energy, power or per-member duration in a public output?** No. New public fields are hashes, paths,
   verdicts, cause codes, attempt counts, and the G10 preflight's clock offset.
6. **Refuse a good window only after the launch is consumed?** Yes: B1 for every `s1`, B3 for every re-armed
   attempt.

## Required before G10 or `s1`

1. Cure B1, B2 and B3. B1 needs ruling 76 addendum C corrected (it calls every `pgrep` an absence probe).
2. Decide M1 and M2 and encode them, since B3's cure makes re-armed attempts reachable.
3. Write the composed test the first pass required, with no mock at the seams. Three further seams now need the
   same treatment: the real author inside the real G10 helper with the production `authenticated_clock_budget`;
   a G2-b harvest and a desk close-out with the night plan id different from the pack plan id; and the full
   author probe roster (not a hand-picked list) through the journal into G1.

## What I did not verify

- Nothing live: no clock change, sudo, launchctl, sampler or model. One read-only `pgrep` was run on this Mac
  for B1.
- Focused suite at `6796b8e0`: `test_v5_block4_{x6,x7,x9,x10,composed,clock}`, `test_v5_s1_qualification`,
  `test_harvest_v5_qualification`, `test_v5_s1_desk_closeout`, both `test_capture_t0_anchor_positive_control*`,
  `test_t0_anchor_positive_control`, `test_prewindow_check`: 183 passed, 139 subtests passed, 392 s. The whole
  suite was not run. `test_harvest_v5_g2b_window`, `test_v5_qualification_plan`, `test_run_night` were not run.
- The battery-boundary lifecycle binding (`v5_qualification.py:854-919`) was compared field by field with the
  native producer (`joulewise/evidence_night.py:1334-1431, 1758-1842`) by reading; the names match, the
  composition was not executed.
- G3, G5 and G8 on native producer output; the admission-abort replay (`v5_qualification.py:83-184`) against a
  real aborted bundle; the installer and the controller changes merged from `main`.
- B3 was established by reading both sides and executing only the reader; no full harvest was run with differing
  ids.
