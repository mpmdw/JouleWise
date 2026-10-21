claude-opus-5-5

RULING: ADMIT-WITH-CORRECTIONS

Cold gate on registration B6-REPL (draft `docs/registrations/block6_replication_DRAFT.md` at `3ef265345`), the pack
commit `f31aca19f` and the pin candidate `6849cb7e3`. Judge: Opus 5.5, blind, single foreground session, 2026-10-17.
I found no defect that makes round 1's data unusable for a registered claim. Twelve text corrections follow (C1 to
C12). Each one either brings the text in line with the code that will run, or moves a deadline that protects no
number. None of them changes a collected byte.

---

## Item 1. The §15 decisions marked [cold gate] and not yet ruled

D25, D26 and D31 to D38 are already ruled, and D27 is superseded, so they are not re-ruled here. That leaves D2, D3,
D5, D8, D9, D10, D12, D13, D14, D15 and D23.

- **D2 (the between-session summary includes block 5's session): ADOPT.** Design §5 counts block 5's session among
  the "three/four independent sessions", and the summary decides nothing (§10). Block 5 used a different s_bracket
  (14.531 ms against 10.818 ms), so its attribution floors sit up to 3.713 ms × 0.047 J/ms = 0.175 J higher. §11.1
  already prints that each block has its own acceptance, so no text change is needed.
- **D3 (Δ = block-6 mean − block-5 value, plus each session's own difference): ADOPT.** It is the plain reading of
  "the difference between them", and it removes nothing.
- **D5 (the close): ADOPT-WITH-CHANGE (C1).** The rule is right and the code implements it, but the time zone in the
  text is wrong. US daylight time ends at 02:00 on Sunday 2026-11-01, so 23:59:59 that evening is PST (UTC−8), not
  PDT. "23:59:59 PDT" would be 06:59:59 UTC on 2026-11-02, one hour earlier than the pack files'
  `end_t0_before: 2026-11-02T00:00:00-08:00` (08:00 UTC). The loop refuses any t0 ≥ that instant
  (`joulewise/b6/queue.py` `done_reason`), so the code is right and the text must follow it.
- **D8 (the 5 ms run clock bound kept; the start held only above 5 ms / T_stream_max − 0.25 ppm): ADOPT.** The four
  estimator files are byte-identical to `a434e363d` (same git blobs at `6849cb7e3` and `f31aca19f`, below). The
  measured r = −4.67 × 10⁻⁷ ppm is 14.7 ppm below the hold. The machine test's runs had request spans of at most
  2.97 s and streams of about 80 s, nothing above 335 s, so D33's T_stream_max = 335 s stands.
- **D9 (F_min = 1.9 J from non-claim data): ADOPT.** See item 2. Add the derivation sentence of item 2 to §8.5.
- **D10 (E_add = w × max(0, C − k × c_q), worst placement): ADOPT as the form of the labelled alternative.**
  The exclusion itself is not adopted for round 1 (D34, already ruled), so for round 1 this decision fixes only the
  arithmetic of the printed alternative. The replay counts (14 of 53, 38 of 77) were reproduced by both judges of
  2026-10-17; I did not re-execute them.
- **D12 (the b_op stop is the 25% attribution point of the pack's smallest target phase): ADOPT, with C9 on the
  slot's deadline.** At `f31aca19f` the code holds `REGISTERED_T10_STOP_S = {alpha: 0.139, gamma: 0.139, beta: None}`
  (`joulewise/b6/capture_screen.py:14`). For BETA it emits `calibration.stop_line_unsized` (DISCLOSE) and lets each
  run's phase check decide. That is safe: above the line, every run of the smallest phase fails its phase check, so
  the session could not count anyway (N3). The stop only saves machine hours. A missing BETA line therefore loses no
  data; it can only cost a session's six hours. The 8B prefill is longer than the 1.7B's 0.62 s, so its line lies
  above 139 ms.
- **D13 (M2 read by its point estimate): ADOPT.** d = +0.1803 J against F_min / 4 = 0.475 J (registered with D32).
  The decision flips only if F_min ≤ 4 × 0.1803 = 0.721 J. No floor the non-claim data support comes near that
  (item 2).
- **D14 (GAMMA pairing step 3; one floor session may serve several GAMMA sessions): ADOPT-WITH-CHANGE.** See item 3.
- **D15 (composition of the flagged-inclusive line): ADOPT.** It never replaces a registered value. It excludes W
  and S sessions, so every session it adds ran the registered experiment, and it keeps run exclusions.
- **D23 (graphics and ANE contender line P* = F_min / (4 T_phase), idle-baseline rails, no quiet level subtracted):
  ADOPT-WITH-CHANGE (C6).**
  - *Replay executed:* mean GPU + ANE rail power over each of the 35 idle baselines of the 2026-10-09 session
    `corpus18-20261009T1949Z` (576 records each). Largest mean 1.35 mW; largest single record 206.5 mW. The line is
    0.24 W at decode and 0.77 W at prefill, so 0 of 35 runs are removed, and 1.35 mW is 1/176 of the lower line.
  - *Size:* 0.475 J by construction.
  - *What the code does:* at the pin, no code computes the exclusion. The acceptance emits `power.pstar_unsized`
    (DISCLOSE, `joulewise/b6/acceptance.py` near line 258). The rail readings it needs are preserved in every bundle
    (`raw/powermetrics_idle.plist`), so the exclusion can be applied at the desk before the blind dry run.
  - *Why that suffices:* it needs no step before round 1. The number it protects is the 0.475 J per run, and that is
    applied at analysis either way.

## Item 2. S-10, F_min: REGISTER 1.9 J

F_min is "the smallest floor the paper prints, estimated from non-claim data". I re-derived the candidates from the
non-claim rehearsal of 2026-10-09 (`corpus18-20261009T1949Z`). For each run I summed rail power × overlap on the raw
record stamps (§1.3), and took a first-kind bound g × (P_start-edge record + P_end-edge record) at g = 45.7 ms. That
leaves out the m term and the clock-anchor correction, so these are indicative values, not the reducer's.

- **Decode attribution floor** (largest bound over the 6 decode-target runs): **2.139 J.**
- **Prefill-p2048 attribution floor** (largest bound over the 22 prefill runs): **2.613 J.** Their mean is 26.176 J
  with standard deviation 0.379 J, which reproduces the threshold note's 26.1 J and 0.38 J.
- **Comparative prefill floor** from the five null quads b06 to b10:
  - d_k = −0.787, +0.580, −0.050, +0.905, −0.662 J;
  - point floor max(0.905, 2.776 × 0.7441 × √1.2 + 0.0027) = **2.266 J** (n = 5, unguarded);
  - corner-widened with the shared-edge half-widths w_k = 0.34 to 1.18 J: 5.66 J.
- **Absolute floors** are at least the corner-widened value, whose half-widths are the runs' own first-kind bounds
  (1.2 to 2.6 J here), so they lie above the attribution floors.

The proposed **1.9 J** (45.7 ms × 0.041 J/ms) lies at or below every candidate, so it is the conservative choice:
a smaller F_min gives stricter lines.

**Sensitivity.** Block 6's own b_op over the rehearsals is 41.3 to 51.0 ms, which gives a decode attribution floor
of 1.69 to 2.09 J. Anywhere in that range, F_min / 4 is 0.42 to 0.52 J:

- d = 0.180 J stays disclosed;
- P* moves by at most 11%, and against the 1.35 mW largest baseline no count changes;
- the outside-processor rule is not adopted.

No decision depends on the choice inside [0.73, 2.6] J.

**Text to add to §8.5 after "With the proposed value, F_min / 4 = 0.475 J":**

> "Cold gate 2026-10-17 (registration gate): registered at 1.9 J. On the 2026-10-09 rehearsal the decode attribution
> floor is about 2.1 J, the prefill-p2048 attribution floor about 2.6 J and the comparative prefill point floor
> 2.27 J (5 null quads), all at or above 1.9 J; no registered decision changes for any F_min between 0.73 J and
> 2.6 J."

## Item 3. S-17, GAMMA pairing when no later counting floor session exists: REGISTER step 3, with a change

- **Adopted:** the last counting session of P from an earlier round; failing that, block 5's analysed session of P.
- **Why step 3 is sound:** pairing reads only which sessions count (no energy). One floor session may serve several
  GAMMA sessions.
- **Why the block-5 fallback is not a blinding breach:** block-6 release already waits for block 5's release
  (§12.3 item 2), so that floor is read only after release.
- **What the block-5 floor costs:** it carries block 5's s_bracket, so its gate is up to 0.175 J larger. That errs
  toward `not_resolvable`, never toward a false `direction_supported`.

**Text change to §6.2 step 3** (replace "`OPEN[S-17]`: … marked for the cold gate"):

> "(registered by the cold gate of 2026-10-17). A contrast whose floor gate uses a block-5 floor prints 'floor from
> block 5' in its outcome line and in the replication sentence of §11.2. The pack files' dependency field
> `same_round_else_next_counting` names steps 1 and 2; this text governs step 3."

## Item 4. The fills of S-2, S-3, S-18: CONFIRMED, with C4 on the capture list

- **S-3.** `scripts/build_b6_flag_catalog.py --check` exits 0 at `f31aca19f`.
  `configs/b6/flag_catalog_b6.json` hashes to SHA-256 `b5bce6c6…a389a42b` both at `f31aca19f` and in the
  measurement checkout at `6849cb7e3`, and `git diff 6849cb7e3 f31aca19f -- configs/b6/flag_catalog_b6.json` is
  empty.
- **S-18.** `configs/b6/registration/identity_pins.json` and `configs/campaigns/v5_claim_25g83/identity_pins.json`
  both hash to `513d7d4a…24b4841d`. The four estimator files have identical blobs at `a434e363d`, `6849cb7e3` and
  `f31aca19f`:
  - `reduce.py` 82449d58;
  - `uncertainty_evidence.py` 202acfcb;
  - `powermetrics_fiducial.py` d1bd5d4b;
  - `adapters/powermetrics.py` 8fa6db3c.
- **S-4 file.** `acceptance.json` hashes to `ea130c87…539ce2a8`, as registered.
- **S-2.** `configs/b6/loop.json` sets `loop_root` to `/Users/edr/night-b6/loop`. `session_paths.for_session` builds
  `<loop_root>/../sessions/<id>/{custody, runs-parent, backup-claim, backup-bound, archive, export}`, uses
  `<loop_root>/staging/<id>` for staging, and raises if any destination lies inside the measurement checkout
  (lines 43 to 58). These match the fill.
- **What the S-2 fill leaves out (C4).** The capture list is not empty at the start. `build-checkout.zsh` seeds
  `runs/calibration_observation_ledger.jsonl` with a 402-row terminal ledger from before block 5
  (`harvest-d117-g2a-prefill-probe-20261004T1305Z-r2`, SHA-256 `6ee89e5a…`). The current checkout's ledger has 402
  rows. §3.3's "holds only quiet-machine and block-6 captures" is therefore false.

## Item 5. The pack registrations at `f31aca19f`: CONSISTENT, with C7

- **Validator.** `validate(reg, catalog, root=<checkout of f31aca19f>)` returns `[]` for alpha, beta and gamma.
- **open_packs.** `open_packs(<checkout>, run=subprocess.run)` opens all three (commit time 1792283007) and rejects
  none.
- **Flag effects.** Each file lists 259 codes with effects. The catalog has 259 codes. For every code the file's
  effect equals the catalog's (0 differ, 0 missing). The pack seat's report of 192 listed and 67 omitted codes
  describes its uncommitted state; the commit has all 259.
- **Session counts and close.** Target 3 (`stopping.count` 3), minimum 2, pause after 5 attempts, corpus 18,
  `end_t0_before` 2026-11-02T00:00:00−08:00. All match §5 (the date as corrected by C1).
- **Dependencies.** GAMMA depends on alpha and beta (`floors`, `same_round_else_next_counting`, §6.2 steps 1 and 2).
  ALPHA and BETA have none.
- **Round rotation.** `interleave: none` concerns quads within a session; the §6.1 rotation is the loop's
  (`queue.rotation` over `base_order` alpha, beta, gamma).
- **Fields no program reads.** `flag_effects` and `estimators` are read only by the validator (grep: no other reader
  in `joulewise/` or `scripts/`). Counting comes from the acceptance verdict, which reads the catalog.
- **Mismatch 1, estimator 1 (C7).** It is registered as `paper_reported_energy:_project_cell`, and that function
  refuses any cell with other than exactly 50 rows (`paper_reported_energy.py:392`): fixed n = 10, 9 degrees of
  freedom. It is not §9.1's kept-unit estimator. B5-PLAN §11 names the kept-unit issuer (`REPORTED-ENERGY-ISSUER`)
  as absent.
- **Mismatch 2, hidden offset.** `blinding.hidden_offset: true` is forced by the validator (`pack_registration.py`,
  `check("blinding", …)`). §12.1 already says such factors are divided out before printing. That they divide out
  exactly is owed with S-14: NOT EXECUTED here.
- **Test modules.** `tests.test_b6_registration`, `tests.test_b6_loop` and `tests.test_b5_plan` at `f31aca19f`:
  91 tests, OK.

## Item 6. S-1, the pin: the machine test on `6849cb7e3` STANDS for `f31aca19f`. Pin `f31aca19f`.

`git diff --stat 6849cb7e3 f31aca19f` touches only the three pack files and `tests/test_b6_loop.py` and
`tests/test_b6_registration.py`. Inside the pack files only `status`, `estimators`, `draft_notes` and the values of
`flag_effects` changed. `plan_tree_ref`, `pack_id`, `corpus`, `stopping` and `dependencies` are byte-equal (field
diff executed).

The brief's claim that the pack files are read only by the loop's opener and validator is **not exactly true**.
There are two more readers:

- `joulewise/b6/precheck_lane.py:64` reads `plan_tree_ref`;
- `joulewise/b6/desk_lane.py:216` passes the file to `session_structure.check`, which reads `structure` (absent in
  both versions) and `pack_id`.

Neither reads a field that changed, and none of the changed files is in the number-bearing list. The code check at
`f31aca19f` against `registered_commit` `3bb305d7a` with `configs/b6/executing_reviews.json`:

- `number_bearing_changed`: the same 7 files as at `6849cb7e3`;
- `unreviewed`: [];
- only `code.changed_since_registration` (DISCLOSE) is flagged.

So W3 does not fire. Collection, harvest and the machine test execute identical code on identical inputs, and the
machine test is not re-run.

Two conditions for S-1 (C8):

1. Every session must run from a measurement checkout at `f31aca19f`. The existing clone
   `JouleWise-measurement-20261017T2213Z-b6` is at `6849cb7e3`, where the packs are `draft`, so `open_packs` would
   open none and the loop would sit idle (`no_open_packs`). `build-checkout.zsh` already targets `f31aca19f`.
2. The S-1 record states that the machine test's meter-unplugged item was "not exercised". The meter excludes
   nothing (S-12), and the harvest records a missing or unreadable meter as `meter.absent`, never a fault
   (`b5/harvest.py` near line 6201). Its untested path can therefore cost at most a session, through the §4
   structure check, and never a number.

The pin changes the fingerprint, so a fresh smoke runs before ALPHA_1, as §3.2 item 6 requires.

## Item 7. §7 item 2's session deadline: BUILT. Not a stop.

Commit `ff0d63f04` (2026-10-14, "Session kill deadline covers the agent-pause limit and the wait budget") is an
ancestor of `6849cb7e3`. The formula is:

- `joulewise/b5/plan.py:917`: window_max_s = 60 × ceil((programmed_span + 3,300 + 7,200 + 7,200) / 60);
- `joulewise/b6/plan_inputs.py:55`: the same formula;
- `tests.test_b5_plan` checks the two literals against `agent_pause.PAUSE_LIMIT_S` and
  `idle_wait.SESSION_WAIT_BUDGET_S`.

From `sizing_b5.json`:

| Pack | Programmed span (s) | window_max_s (s) |
|---|---|---|
| ALPHA | 106,890 | 124,620 |
| BETA | 109,290 | 127,020 |
| GAMMA | 95,754 | 113,460 |

The machine test's plan carries `window_max_s` 124,620 (`machine-test.json`).

Correction **C3** to §7 item 2: replace "(…; the driver lane's report names this change as blocking its merge, and no
lane has built it yet)" with "(built at `ff0d63f04`: 124,620 s for ALPHA, 127,020 s for BETA, 113,460 s for GAMMA)".

The pause limit in code is **cumulative**: `AgentPause.total_pause_s` ≥ 7,200 s (`agent_pause.py:77`; design 6.2,
"two paused hours total"). The text says "a pause longer than 7,200 s". Correction **C2** follows.

## Item 8. Anything else that would make round 1's data unusable: NONE FOUND by execution

What I executed, and what it showed:

- **The real acceptance file loads through the harvest's acceptance path.** I re-judged a clonefile copy of the
  machine-test archive with `joulewise.b6.session.accept_archive` and the registered
  `configs/b6/registration/acceptance.json`. The machine test itself had used a stand-in non-claim acceptance with
  block 5's constants (allowance 14.531 ms). With the registered file:
  - `allowance_s` = 0.010818;
  - b_op = 26.647 + 10.818 = 37.465 ms;
  - `pack_id` "b6-replication" is accepted.
- **Real sessions take the "archive" branch, and it behaves as registered.** In "smoke" mode the acceptance sets
  `physics_stop` true whenever any PHYSICS-class run exclusion exists, which is right for a smoke. With the archive's
  smoke flag forced off:
  - `physics_stop` false, no structural failure;
  - the agent-overlapped unit and the cap-skipped run are excluded at run level only;
  - the session's only exclusions are `cell.below_minimum` and `neg8.survivor_screen_undefined`, which a 4-run smoke
    must carry.

  So a short agent pause or a cap skip does not remove a real session, as §3.2 and §8.3 require.
- **The two programs D36 names are gone.** pid 43816 and Spotify are not running (`ps`, `pgrep` at about 17:50 PDT).

Owed before the analysis release (S-14), not before round 1, because the data are preserved:

- the kept-unit estimator-1 issuer (C7);
- the graphics exclusion computation (C6);
- the hidden-offset division check.

## Corrections (exact text)

- **C1.** In §5.3, replace "No session arms with a t0 after 2026-11-01 23:59:59 PDT" with:

  > "No session arms with a t0 at or after 2026-11-02T00:00:00−08:00 (the end of 2026-11-01, Pacific time;
  > daylight time ends at 02:00 that day, so this is 23:59:59 PST, 08:00 UTC on 2026-11-02; the pack files'
  > `end_t0_before`)".

  In the §2 table, "(PDT)" becomes "(Pacific time)". In D5, "PDT" becomes "PST (−08:00)".
- **C2.** In §3.2 item 2, replace "A pause longer than 7,200 s stops the session" with "Agent pauses totalling
  7,200 s in a session stop it (cumulative, `joulewise/b6/agent_pause.py`)". In §8.2 P4, replace "an agent pause
  longer than 7,200 s" with "agent pauses totalling 7,200 s".
- **C3.** §7 item 2: the text given under item 7.
- **C4.** At the end of §3.3's capture-list paragraph, add:

  > "At the pin the list is seeded with 402 rows from before block 5 (the terminal ledger of
  > `harvest-d117-g2a-prefill-probe-20261004T1305Z-r2`, SHA-256 `6ee89e5a…`, installed by the checkout script); no
  > quiet-machine capture is in it (the acceptance carries its own 13). The other-session flags read those rows, and
  > `calibration.corpus_doubling_reached` fires from the first session (83 counted against 26 on the machine test);
  > it discloses only and enters no number."

  Replace "holds only quiet-machine and block-6 captures" with "holds no block-5 capture".
- **C5.** In §8.2, after "One more code stays session-excluding…", add:

  > "`precheck.certain_exclusion` is EXCLUDE_WINDOW in the catalog; only the pre-session check emits it, and that
  > check then does not start the session (§3.2 item 6), so no harvested session carries it."
- **C6.** In §8.3 item 3, second bullet, replace "(a new code, not yet built)" with:

  > "(not computed at the pin: the harvest emits `power.pstar_unsized`, DISCLOSE; the exclusion is computed at the
  > desk from each bundle's preserved idle-baseline rails before the blind dry run, owed with S-14; replay on the 35
  > runs of 2026-10-09 session 1949Z: 0 removed, largest baseline mean 1.35 mW)".

  In §8.1, after "every condition listed here has a code", add "(except this one, as stated in §8.3)".
- **C7.** At the end of §9's opening paragraph, add:

  > "The pack files' `estimators` entries name the library kernels and are read by no program; this section governs.
  > Estimator 1's kernel `paper_reported_energy._project_cell` takes exactly 50 rows; the kept-unit issuer of §9.1
  > (B5-PLAN §11, `REPORTED-ENERGY-ISSUER`) is part of S-14 and must equal `_project_cell` exactly on a complete
  > cell."
- **C8.** Fill S-1 with: "`f31aca19f` (pack registrations on `6849cb7e3`; no collection, harvest or number-bearing
  byte differs); machine test `MT-20261017T2215Z` on `6849cb7e3`, 2026-10-17, stands for it (cold gate); every item
  observed except the meter unplugged (not exercised; the meter excludes nothing); sessions run from a measurement
  checkout built at `f31aca19f`".
- **C9.** In §14, the "Before" column becomes:
  - for S-5: "round 1 runs the coded table (ALPHA and GAMMA 139 ms; BETA none, `calibration.stop_line_unsized`
    disclosed); a smoke-derived change is a §17 entry and a new pin";
  - for S-9 and S-11: "the blind dry run".

  The number each protects is applied at harvest or analysis from preserved bytes. A stop line only saves machine
  hours (§8.6), and §7 item 6's "no session arms" rule does not apply to these three.
- **C10.** In §8.5, add the S-10 sentence given under item 2. In §14 S-10, add "registered 1.9 J (cold gate
  2026-10-17)".
- **C11.** In §6.2, the S-17 text given under item 3.
- **C12.** Leave `acceptance.json`'s internal `"status": "draft: not cold-gated …"` string and its
  `registered_commit` `3bb305d7a` unchanged; D30 left that choice to S-1. No program reads the status, and changing
  either would change the digest already registered (S-4). Every session then carries
  `code.changed_since_registration` (DISCLOSE), as the machine-test re-judge shows.

## What the draft, the pack seat and the code got wrong

- **Draft:**
  - the close is labelled PDT where PST is in force (C1);
  - "a pause longer than" where the code limits cumulative pause (C2);
  - the session deadline is described as unbuilt (C3);
  - the capture list is said to hold only quiet-machine and block-6 captures (C4);
  - `precheck.certain_exclusion` is not named (C5);
  - the graphics exclusion is registered with no code at the pin (C6);
  - S-5, S-9 and S-11 block arming without protecting a number (C9).
- **Pack seat:** its estimator 1 names a 50-row kernel, not the kept-unit estimator (it flagged this itself as F3).
  Its report of 67 omitted codes was overtaken by the commit. Its F2 is correct (C5).
- **Brief and launch:** the claim that only the opener and validator read the pack files is false (two more readers,
  harmless here, item 6). The machine test ran with a stand-in acceptance (block-5 constants), so it did not exercise
  the registered `acceptance.json`. I executed that path myself (item 8).
- **Code:** no defect that affects a registered number found.

## What I ran

All under TMPDIR `/Users/edr/night-archive/magistrate-52d50d1f/gate/tmp-opus`, with Python
`/opt/homebrew/bin/python3.13 -B`:

1. `git worktree add --detach tmp-opus/wt-pack f31aca19f` (removed at the end).
2. `git diff --stat 6849cb7e3 f31aca19f`, and a field-by-field JSON diff of the three pack files against
   `6849cb7e3`.
3. For each pack: `pack_registration.load` + `validate(reg, load_catalog(...), root=wt-pack)`, giving [] three
   times. Then each pack's `flag_effects` against `catalog.effect(code)` for all 259 codes, and
   `open_packs(wt-pack, run=subprocess.run)`.
4. `scripts/build_b6_flag_catalog.py --check` (exit 0). `shasum -a 256` of the catalog, `identity_pins.json`
   (block 6's and block 5's) and `acceptance.json`, at `f31aca19f` and in the measurement checkout. `git rev-parse`
   of the four estimator files at `a434e363d`, `6849cb7e3` and `f31aca19f`.
5. `JW_B5_SYNTHETIC_ONLY=1 python -m unittest tests.test_b6_registration tests.test_b6_loop tests.test_b5_plan`:
   91 tests, OK.
6. `cp -cR` of the machine-test archive. Then `joulewise.b6.session.accept_archive(copy, plan, wt-pack/configs/b6/registration, smoke=True)`, and again with the archive's smoke flag patched off (archive mode).
7. `code_check.check('.', '3bb305d7a', <6849cb7e3 | f31aca19f>, number_bearing_paths, executing_reviews)`.
8. Read: the `window_max_s` and pause code, the machine test's `report.json`, `injections.jsonl`,
   `machine-test.json` and `smoke-result.json`, and the run spans of its bundles.
9. `scripts/phase_e.py`: phase energy by record overlap and the raw-stamp first-kind bound, over the 28 science
   bundles of `rehearsal-real/corpus18-20261009T1949Z`. Then the comparative-floor arithmetic of §9.2 on the 5
   prefill null quads.
10. `scripts/idle_gpu.py`: GPU + ANE idle-baseline rails over 35 bundles of the same session.
11. `ps -p 43816`, `pgrep -fl -i spotify`, `pgrep -fl hazard_monitor.py`.

**NOT EXECUTED:**

- the D10 and D34 outside-processor replay (reproduced by both 2026-10-17 judges);
- the hidden-offset division;
- the 8B packs' floors (no non-claim 8B null quads on disk).

**Protocol disclosure.** One `reduce_bundle` loop over the rehearsal bundles hit the 600 s foreground limit and was
moved to the background by the harness. I stopped it (TaskStop) with no output used, and replaced it with item 9.

**Blinding.** I opened no block-5 claim data, no block-5 restricted path, and no file under `night-custody/v5-*`,
`night-b5`, `night-g2a` or `night-archive/b5-*`. I did not open the capture-list seed's contents. Energies read:
non-claim rehearsal (2026-10-09) and machine-test (2026-10-17) bundles only.
