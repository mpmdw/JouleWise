The write to `REPORT.md` was refused by the permission mode, so the report is returned here in full.

# Seat: Mythos 5.2, cold kit check

Sat Nov 14 01:07:52 PST 2026 (`date`). Cold seat of RL-149 §2.8 line 1. I did not write the kit or the runner.

**Checked bytes.** Worktree `/Volumes/JW-EXT/jw-wt/campaign-runner`, HEAD `79031dcd8` (PR #775).
- `cl-dev-01.json` sha256 `3b33c52d8405006bd11aad71811b78d2dd25becd5f18341e11ea01a5dd8955cd`
- `cl-dev-02.json` sha256 `052579f06e4d9157290fcea5a81fb5aaf263c0fdaca884bce7d218397b726d2b`
- Both pin `frozen.commit` `efbd0b020` (HEAD~1) and 36 paths.

## Verdict

**ADMIT WITH FIXES** for issuing the counted pilot (dev-01 L001-L003).

The legs, inclusion rules and stops in the kit are RL-149 §2's, and the three pilot legs would run in the shape the ruling names. Nothing I found would spoil them as counted development legs. Four findings must close before the arm (F1-F4). None needs a change to a frozen path: three are procedure and one is kit text. I also recommend one line from the research lead on R1 before the arm, because the three legs count.

Line 1 of §2.8 is therefore **not yet met**: F1-F4 are open findings until the lead closes them.

## What I ran

| Command | Result |
|---|---|
| `validate-kit --repo .` on both kits, default window and `--batch-window 02:00-02:35` | `ok: true`, `frozen_paths_verified: true`, all four runs |
| `gen-legs` for `cl-dev-01` (seed 2026111401, 12 legs, band `q0`) | Identical to the kit's leg list |
| `blocks` | Ledger validates; `DESIGN_QUEUE_LOW`, advance dev-01 |
| `plan` pilot, t0 13:20, both windows | Expected 6,903 s (1.9 h), worst case 16,650 s (ends 17:57) |
| `plan` dev-02, t0 13:20 | Expected 18,162 s (5.0 h), worst case 40,950 s (ends 00:42) |
| `plan` dev-02, t0 22:00, `--batch-window 02:00-02:35` | Refused: worst case meets the blackout |
| `plan` dev-02, t0 22:00, no flag | **Accepted**, `blackout_clear: true` (see F2) |
| `mock` pilot | rc 0, 3 legs, no stop |
| `mock` pilot, `--contaminate L001 --g0-timeout L002` | rc 0, `MEASURED_OK`, "3/3 legs run", no stop (see F8) |

**Not done.**
- I did not run the test suite or read CI. Line 2 of §2.8 is the lead's.
- Read access to `scripts/km003c_monitor.py` was refused, so F4's trailer question is unverified.
- I did not open the v4 episode template `align-v4-episodes-a-e05.json`.
- Blinding held: no slot, transcript, energy, power, meter or powermetrics file was opened. No SSH.

**One thing beyond the brief.** `mock` needs an output directory. Two mock spans are in `/Volumes/JW-EXT/scratch/mythos-kit-check/` (`mock-pilot/`, `mock-pilot-faults/`). They hold fake-clock records only and can be deleted.

## Findings

### Must close before the pilot arms

**F1. The kit that arms will not be the bytes I checked.** Major, procedure.
- Evidence: `frozen.commit` is `efbd0b020`, a PR-branch commit, and the kit with these hashes exists only at `79031dcd8`. The checklist and the runner both demand HEAD equal to `frozen.commit` (`kit.py:454`, `cadence_legs_runner.py:250-254`), so the kit must be supplied from outside the measurement checkout. The ledger note says it will be re-pinned "at the commit the magistrate measures from".
- Fix: this check carries to a re-pinned kit only when the kit diff is `frozen.commit` plus F4's text, with all 36 path hashes unchanged. The lead records that diff beside the queue pin. Any changed hash comes back to a cold seat for that file. Line 2's suite result must be for the commit finally pinned.

**F2. The ruled blackout (02:00-02:35) is not on the frozen bytes.** Major; procedure for the pilot, code before any other t0.
- Evidence: the frozen `scripts/align_r1_rehearsal.py:64` still has `((11, 45), (13, 15))`. The runner's default reads it (`cadence_legs_runner.py:92-95`), and the kit has no blackout field. So §2.9 item 4 holds only when the arm passes `--batch-window 02:00-02:35`. The 22:00 `plan` above shows the unguarded case.
- The soak also keeps refusing 11:45-13:15 on these bytes (`run_align_r1_smoke.py:317-319`, `cadence_legs_runner.py:304`), a wait that `plan_span` does not budget.
- Pilot exposure: none at 13:20. The three spans' bounds end at 17:57, 22:27 and 00:42.
- Fix now: every arm passes the flag, and the arm record shows the plan's `batch_windows`.
- Fix in schema v1.1: the window is a kit field, and the runner refuses to run without it.

**F3. Nothing holds L004-L012 until the lead's hand-read.** Major, procedure.
- Evidence: `next_action` arms the next queued span as soon as the previous one is CLOSED_OK (`queue.py:265-283`). There is no pilot-passed evidence key or check kind (`kit.py:90-108`).
- Fix: the first `QUEUE.json` holds the pilot span only. The lead appends L004-L012 after recording the hand-read. No `QUEUE.json` exists on these bytes yet, so line 3 is also still open.

**F4. The kit's energy-read sentence is not the ruling's, and is untrue of the runner.** Major, kit text plus one confirmation.
- Evidence: the kit says "No desk, watcher, queue, runner or agent opens an energy, power or meter sample file". RL-149 §2.6 says "No desk, watcher, queue or agent opens an energy, power or meter file of a campaign leg". The runner's close does open every KM003C stream file: it hashes it (`cadence_legs_runner.py:506-512`) and reads its first line and last 64 KB, decoding the last line (`legs.py:384-393`).
- Only `present`, `proven_stopped`, `polls`, `bad_polls`, `usb_errors` and `elapsed_s` are projected. INSTRUMENT_FAULT needs them, so the read looks right in purpose.
- Fix: restore the ruling's words and add one clause saying what the runner reads. The lead confirms from `km003c_monitor.py` that the trailer line carries no power or energy aggregate. If it does, R8 applies.

### Must close before chained spans or the interim look

**F5. §2.4's campaign-scope stop and `measurement_mode` are absent.** Major.
- Evidence: `stop_rules.notes` lists four stops and omits "any change to a frozen kit path, or to host state outside `measurement_mode`" (campaign scope, cleared by the research lead). The string `measurement_mode` occurs nowhere in this worktree, and no checklist line covers it.
- A frozen-path change is caught at the arm (`frozen_paths_hash`), but nothing routes it to the research lead.
- Fix: add the stop to the notes. The arm and close records carry the `measurement_mode` verification, with the tool named by the lead.

**F6. Lines 3, 4 and 7 of §2.8 have no machine check.** Major.
- Line 4: `--output` and `--custody-root` are arm arguments. Neither the validator nor the runner refuses a path inside a v4 registration or custody root. The runner reads the v4 registration inputs and a v4 episode template (both frozen paths) and tags bundles `align-v4-r1` (`r1_runtime.py:739`), with run ids `cadence-<kit>-<leg>`.
- Line 3: `validate_queue` requires an expiry, not "within seven days" or append-only (`queue.py:99-100`).
- Line 7: no check kind for the watcher stamp.
- Fix for the pilot: the arm record names the output root and states it is outside those roots; the lead's watcher stamp is in the same record. Code checks follow before phase 5.

**F7. Freeze 1 has no home in kit schema v1.** Major, needs R4.
- Evidence: both kits carry `looks: []`. The closed look schema (`kit.py:370-381`) holds a look id, a leg count and one fit path. It cannot hold the model family, the predictor list, the output schema, or a look that spans blocks ("after dev-04 is DESK_FINAL", reading development legs and hp-01).
- A look's fit code must be a frozen path. Adding one later is "a change to the kit's frozen paths", which by §2.8 ends the authorization until a new kit passes lines 1, 2 and 8.
- Answer to the brief's question: freeze 1 gates the first energy read, not the first leg. The pilot may run with `looks: []`. The inclusion rules, the one part of freeze 1 that §2.4 fixes now, are in the kit.

### Minor

**F8. The desk table hides inclusion.** `admitted` is in the summary but not in `JOURNAL-TABLE.md` (`desk.py:158-170`). In the fault mock, a pilot with a G0 timeout closed `MEASURED_OK` with no stop. The lead's hand table cannot be compared on inclusion. Fix: print the column.

**F9. dev-01 is two spans on two calendar days.** With t0 fixed at 13:20, L004-L012 cannot arm until the next day. The ledger's "its calendar day is its unit of independence" is wrong for dev-01. Fix the sentence.

**F10. A loaded soak refuses the span.** The soak path raises on sustained load or an unsettled slope (`run_align_r1_smoke.py:329-332`), outside the redo quota. That is a REFUSAL stop with no leg run. It is stricter than the ruling and acceptable; the lead should expect it sometimes.

**F11. The kit's `model` string is not bound to the model the leg loads.** The leg takes the `d_spam` template from `r1_runtime.json`. Both files are frozen by hash, so the model is fixed, but nothing compares it with `kit.model`. The lead confirms the two agree.

**F12. `start_band` is a recipe label, not the ruling's band.** Every leg is `q0`, including the cold first leg of each span. Tables by band need span position or the measured start reading.

## Item by item

| RL-149 | Kit and runner | Status |
|---|---|---|
| §2.2 model, host | 27B by frozen template and pins; Automatic refused unless powermode 0 (`run_align_r1_smoke.py:98-102`); per-leg powermode read from the bundle | Met; F11 |
| §2.2 gates | TV0h and TV1h from `r1_runtime.json:16`, with Tf08 and both fans journaled; `chunk_tokens` 256 is inert because `heavy` is false (`endpoint.py:310-312`) | Met |
| §2.2 type A | One turn, 40,000 characters (19,458 tokens), cap 4,096, on the step member (`cadence_leg.py:104-121`) | Met |
| §2.2 bands by history | No designed start state; `q0` only; one soak per span | Met on readings 1-2; R1, R2 |
| §2.2 cells by seed law | Not built: the law draws seeds and band order only | Open for dev-03 on; R3 |
| §2.3 block size | 12 legs, expected 5.0 h | Met |
| §2.3 pilot | L001-L003 by roster, kit order enforced (`legs.py:129-148`) | Met; F3 |
| §2.3 day and night spans | Impossible on a 13:20-only kit | Open; reading 4 |
| §2.4 rules 1, 2, 5, 6 | `leg_admitted` (`legs.py:338-345`) | Met; R7 |
| §2.4 rules 3, 4 | Left to frozen code at a look | Not built; F7 |
| §2.4 no drop by outcome | Kit text; the runner reads no energy | Met |
| §2.4 stops | Four coded; campaign-scope stop missing | F5 |
| §2.4 reserve | Kit text only | Met as text |
| §2.6 energy-read rule | Projections are allowlists with a deny guard; the leg calls no energy reader | Met; F4 |
| §2.6 freezes | Inclusion rules only | F7 |
| §2.8 line 1 | This report | Open until F1-F4 close |
| §2.8 line 2 | Kit validates at `efbd0b020`; suite not checked by me | Lead |
| §2.8 line 3 | No queue yet | Lead; F6 |
| §2.8 line 4 | Label refusal works; write roots unchecked | F6 |
| §2.8 lines 5, 6 | 17 arm checks; close-side checks are procedure | Met at the arm |
| §2.8 lines 7, 8 | No check kinds | F3, F6 |
| §2.8 line 9 | k+2 rule (`queue.py:277-282`) | Met |
| §2.9 item 3 | `pilot_counted` text registers the legs as counted | Met |
| §2.9 item 4 | Start rule and arm rule both coded; window value wrong by default | F2 |
| §2.9 item 6.3 | Fixed t0 | Reading 4 |
| §2.9 item 5 row 3 | `leg-summary-v1` bundle written at close | Met |

## The builder's readings

**(1) Warm band `q0`, turn at the leg's own G0 release. Confirmed.**
- The ruling's own table makes type H "Type A in High Power" on "the existing A-B-A B leg". So type A is the A-B-A leg's shape in Automatic. The leg matches `step_member` (`r1_runtime.py:1895-1909`) with no quiet.
- "Directly after a heavy leg's G0" means after the leg's own G0. Between one turn and the next there is a model load, a reference capture, a full warm-up prefill and the G0.
- Two differences from the A-B-A leg, both consistent with the ruling. A G0 timeout runs no turn, where A-B-A legs run anyway (`r1_runtime.py:110`). No decline time or energy is computed.
- One point for the research lead, R1.

**(2) Cold start is the first leg after the soak. Confirmed, with R2.**
- The soak is the night's idle soak (cap 1,950 s) after a 300 s dwell, so the first leg has at least 30 min idle behind it.
- "First after the soak, and after at least 30 min idle" can also be read as two kinds of cold start. Twelve legs in about 5 h leave no room for a second, so I read it as one. No recipe exists for a mid-block 30-min idle.
- Consequence: dev-01 and dev-02 give 3 cold-history legs of 24.

**(3) Anchor legs only for dev-01 and dev-02. Confirmed on the text, with one correction.**
- §5 item 6 and the §5 table ("the same kit, next seeds") support it.
- Correction: §5's condition was "if prompt size is not yet a parameter". It now is one in the runner (`legs.py:87-89`). What cannot express sizes is the kit's seed law. So the choice rests on schema v1.
- Consequence: 24 of 48 development legs sit in one cell, and prompt size becomes confounded with day. R3.
- `cl-dev-02` is a second kit file. It differs from `cl-dev-01` only in id, title, seeds and the pilot rule.

**(4) Schema v1 fixes `t0_local`. Corrected: this contradicts §2.9 item 6.3.**
- The ruling says there is no fixed 13:20 t0 and a block arms at any hour if its worst case clears the blackout. `span_window` (`kit.py:490-495`) requires 13:20 to the minute.
- It is conservative, so it does not block the pilot. Its costs: one span a day, no night span, dev-01 on two days, and a one-minute launch window, because the launcher starts at load (`launch_align_r0.py:396`).
- Fix in v1.1: replace the equality with the plan's bound test.

**(5) The validator refuses a whole span that overlaps the blackout. Confirmed, and it is not stricter than RL-149.** §2.9 item 6.3's arm condition is exactly "the block's worst-case bound clears the blackout". §2.9 item 4's start rule is the in-span net. The runner has both (`legs.py:269-272`, `legs.py:209-225`). The window value is F2.

**(6) LEG_OVERTIME needs two legs; BAND_UNREACHABLE dropped. Confirmed** (`stops.py:26-27`, `stops.py:69-77`). The two `band_unreachable` keys stay required by schema v1 and no stop reads them. A leg with no recorded wall or budget counts as over, which is stricter. Who clears a second CONTAMINATED_REDOS is procedure.

**(7) `benign` stays inside bundle configs; no projection carries it. Confirmed.** `workload.py:114` accepts only the two labels and `workload.py:171` requires the neutral warm-up. `r1_runtime.py:824-826` sets both. The step task ignores the value. The leg result and every projection are value-scanned (`cadence_leg.py:100-101`, `legs.py:327-335`). The label is in the custody the fit code reads. R6.

## Rulings needed from the research lead

- **R1. The G0 reference of a campaign leg.** Each leg captures its own reference in the 60 s before its warm-up (`thermal_gates.py:441-459`), as A-B-A legs do. A warm leg's G0 therefore releases near the leg's own entry temperature, not near the soak's. §2.7 leaves start TV0h out of the predictors "because the gate pins it". Is per-leg capture the shape wanted for the heat-term fit? Best answered before the pilot.
- **R2.** One cold start per span, or also mid-block idles of 30 min?
- **R3.** dev-02 anchor-only, or held for the cell law, given the size and day confound?
- **R4.** Where freeze 1 lives, and whether adding fit code to a kit's frozen paths triggers line 8.
- **R5.** The smoke for a new kit after a frozen-path change (hp-01's power path, type-T code, schema v1.1, the blackout constant): which legs, and do they count?
- **R6.** The wording of "None carries a condition" (§2.6), given `benign` in every bundle config.
- **R7.** Rule 5's edge: a contaminated attempt left unreplaced because the quota ran out. The runner marks it not admitted; the rule's letter excludes only replaced attempts.
- **R8.** Whether the runner may read the meter stream's header and trailer (F4).
- **R9.** Whether the pilot has passed when one of its legs is excluded under rules 1-6 with no stop open. The text of §2.9 item 3 says yes.

For the lead alone: F1, F2, F3, F5, F6, F8, F9, F11.