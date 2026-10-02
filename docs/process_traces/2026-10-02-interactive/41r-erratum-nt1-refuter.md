REFUTER E-NT1: AGREE

# Refuter, cold erratum E-NT1 (Opus 5.5)

## Contamination disclosure

- **Loaded by the harness before I read anything (not by my choice).** My session started with
  the user's global `~/.claude/CLAUDE.md`, the worktree's `CLAUDE.md` and the user's memory
  index `MEMORY.md` already in context. The charge forbids reading these. I did not open any
  of them, and I did not open any memory file the index points to. From the index I already
  knew, before starting: the project's general history, that block 1 closed
  CLOSE_AND_DERIVE, and that the owner wants refusals cured and re-armed. Nothing in the index
  states a fact about E-NT1 or the two refused attempts that I used.
- **Read under the charge:** the charge (`40-erratum-nt1-charge.md`); the three receipts; d01
  `events.jsonl`, `instrument_evidence.json` and `manifest.json` for both windows; both
  windows' `night/start_conditions.json` and `night/receipt.json` (boot fields only);
  `joulewise/network_time_off.py`; `git show 2431dcaa` (code and tests); the registration's §5
  "Network time", the §5 preamble, §6.2 (d) to (g), the §7 JSON `start_state_conditions` and
  `null_session`, clause [0] with its prose, the STOP-NULL-REPEAT row and A-R5b "Admission";
  the issuer's start-condition check (`scripts/issue_calibration_acceptance_generation.py`,
  lines 1400 to 1510) and grep hits in `scripts/run_night.py`; RULING-judge §6 and
  REFUTER-on-ruling lines 40 to 100; the 0137Z custody (`night/result.json`,
  `night/refusal.json`, `night.log`, `night/courier.sent`, `night/censuses.jsonl`,
  `night/start_conditions.json`); the 0555Z files the charge names; three ledgers.
- **Outside the charge's list:** of `docs/decision_log.md` D-182 I read the whole section
  (Status, "Why now", "What this does not change") as well as the rule and Terms, because my
  `awk` printed all of it. My findings rest on the rule and the Terms only. I also ran
  `git log` and `git show` on the registration path to check its seal commit, and listed the
  judge worktree's directory once at 16:37 PDT (it held no ruling then). I read no
  RUN_STATE.md, TASK_QUEUE.md or AGENTS.md, and no skill files.

## Phase 1: independent findings

Provisional answers, in the form the charge prescribes:

ERRATUM E-NT1: ADOPT In Revision 6 §5 "Network time", "its standard output is exactly `setUsingNetworkTime: Off`" reads "its standard output states the OFF end state: after every run of whitespace is reduced to one space, surrounding whitespace and any trailing periods are removed and letter case is ignored, it equals `setUsingNetworkTime: Off` (was ON, now OFF) or `Network Time is already off` (was already OFF)"; §7 `stdout_exact` reads the same; this changes how one OFF statement is recognised, not the §5 operating condition (OFF, same boot, ≥600 s on both clocks, one receipt), so §5's voiding sentence is not engaged; the code does not compare standard error, which is wider than §5's Error:-99 parenthetical; both admitted receipts have empty standard error; no number, member, statistic or operative changes.
CHAIN: WITHIN TERMS

### Executed checks

| # | Command (abridged) | Result |
|---|---|---|
| 1a | `cat .../{c1-0617Z,c2-2252Z,c1-0137Z}/night/network_time_off.json` | All three: argv `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`, `exit_code` 0, `stdout` `"Network Time is already off.\n"`, `stderr` `""`, `error` null, `boot_id` `cd5b815a-df9b-4fc7-921a-8e97d8aba867`. Receipt epoch/mono: 0617Z 1790835422.2803 / 1056984.2667; 2252Z 1790895121.2183 / 1116683.3937; 0137Z 1790818622.3883 / 1040184.3215. |
| 1b | `shasum -a 256` on the receipts | 0617Z `243d3796…`, 2252Z `09e0a209…`, 0137Z `1f877794…`. Each equals the `f_network_time_off_receipt.sha256` in its own `start_conditions.json`. |
| 1c | `/tmp/cg-ent1-refuter-d138/age.py` (d01 `events.jsonl` plus `instrument_evidence.json` `clock_anchor.clock_stamps.first_parse`) | Earliest d01 stamp minus receipt. 0617Z: wall 1244.374 s, mono 1244.378 s; `sampling_started` +1244.92 s wall. 2252Z: wall 1246.968 s, mono 1246.972 s; `sampling_started` +1247.97 s wall. Both are far above 600 s. |
| 1d | Same boot | d01 evidence carries no boot UUID. `start_conditions.json` `boot_id` and `receipt.json` `boot_session_uuid` both equal the receipt's `cd5b815a…`. Across receipt → d01 the monotonic and wall deltas agree within 4 ms. The monotonic clock was about 1.06×10⁶ s and still rising, so no reboot fell in between. |
| 1e | `start_conditions.json` `settled_seconds` | 633.13 s and 633.45 s at chain-start admission. My recomputation from the clocks is 633.13 and 633.44. |
| 2a | `sha256` of `joulewise/network_time_off.py` here, in clones r6-c1 0617Z and r6-c2, and in both windows' `results-clone` | All `64001994…`, identical. The admitted windows ran the post-`2431dcaa` recognizer. |
| 2b | `/tmp/cg-ent1-refuter-d138/cmp.py`: `off_stdout_admitted` and `admit` | All three receipts are admitted (`True`, `admit` passes). `setUsingNetworkTime: On`[\n] False; `""` False; `Network Time: Off`[\n] False; `You need administrator access to run this tool... exiting!`[\n] False; `None` and bytes False; a two-line Off-then-On output False; `setUsingNetworkTime:Off` (no space) False; `...off,` False. |
| 2c | Same script, probes of the normalisation | **Admitted, beyond "surrounding whitespace, one trailing period":** `"Network   Time is\talready\noff."` True (internal runs, tabs and newlines collapse); `"...already off..."` True (all trailing periods); `"setUsingNetworkTime: Off."` True; `" …off. "` True (Unicode whitespace). `"off. ."` False. |
| 2d | `admit` with `stderr` = `"anything at all\n"` | **ADMIT.** The code checks only that stderr is a `str`; it does not test the content. |
| 2e | `git show 2431dcaa` | One comparator, used at four sites (`arm_readiness`, `t0_rehearsal` ×2, `capture_t0_step`). Tests admit the C1 bytes and refuse On, empty, getter, admin-access and Off+On. Two inputs the old test refused, `setUsingNetworkTime: off\n` and the form with no newline, are now admitted on purpose. A guard test bans literal comparisons. |
| 3a | `sed -n 966,1012p` of the registration | §5 opens: "Each item below is part of the registered experiment. A change to any of them voids this revision." Network time "stays OFF on the measurement Mac (D-186)". The ON→OFF resync "is allowed only in the window's arm step". Stdout must be "exactly `setUsingNetworkTime: Off` (the known `Error:-99` diagnostic line on standard error is tolerated)". |
| 3b | `sed -n 1318,1328p` | §7 `network_time_off_receipt`: `"stdout_exact": "setUsingNetworkTime: Off"`, `same_boot_as_first_capture` true, `min_age_before_first_capture_s` 600, both clocks, `receipts_per_window` 1. |
| 3c | Hash and seal history of the registration (`git log` / `git show … \| shasum`) | HEAD and `bf017893` (2026-09-30 16:47 PDT, "Seal Revision 6") both hash to `d0034003…`. At `46643f1d` (15:09 PDT) the file has no Revision 6 text (`grep -c "Revision 6"` = 0), but `46643f1d` is an ancestor of `bf017893`. The text says "sealed 2026-09-30 at 46643f1d", naming its code base. Either way the seal precedes `2431dcaa` (21:13). |
| 4a | `grep` in the issuer | Lines 1496–1505: exactly one start-condition entry naming `night/network_time_off.json`. It calls `network_time_off.seconds_since_receipt(off, admitted)`, which first calls `admit()` and so `off_stdout_admitted()`. **Issuance does read stdout, through the same recognizer.** It also checks same boot against chain-start admission, ≥600 s on both clocks and plan binding. |
| 4b | R9 record (`harvest/r9_window.json`, 0617Z) | Mentions network time nowhere. R9 does not check the receipt. |
| 4c | `grep` in `scripts/run_night.py` | `_admit_network_time_off` (line 2994) uses `set_network_time_off` / `read_receipt` / `seconds_since_receipt`, all through `admit()`. |
| Q2a | `grep -c "0137Z\|0555Z"` on the r6-c2 ledger; enumerated `bracket-session-open` rows | 0 hits. 376 rows, 6 session opens: n1, n2, w1, w2, then `…r6-derivation-c1-20261001T0617Z` (row 278) and `…c2-20261001T2252Z` (row 328). Nothing after the w2 head (row 276) except those two sessions. |
| Q2a′ | The 0137Z clone's own ledger | 276 rows, no hit for either plan. Its first 276 rows hash `23f72c37…`, the same as the c2 ledger's first 276 rows. 0137Z added nothing. Its clone has no `runs/instrument_validation` directory. |
| Q2a″ | 0137Z custody | `result.json`: REFUSED, `night_probe_error`, `chain_exit_code` null, `chain_sha256` null, `census_count` 0. There is no `runs/` and no `chain.started*`. The window lasted 65 ms (started 1790818622.327, ended .393). `courier.sent` exists (epoch 1790818713). `start_conditions.json` has `chain_start_admitted` null but **does carry a `session_id` string `d079-epoch-25g83-r6-20261001T0137Z`**. That string is a name only; no ledger session was opened under it. |
| Q2a‴ | 0555Z | Session record items 2–3 and `battery-refused-0555Z-attempt.txt`: InstantAmperage −447 mA at step 0, 04:24:54Z; "Nothing was published for that t0". There is no custody directory, no ledger row and no notice. The successor plan 0617Z was armed 21:48:48 PDT with a fresh notice (`1a0f5cab…`). |

### Question 1 reasoning

The literal reading cannot be satisfied together with the rest of §5. Network time "stays OFF" (D-186), and the ON-then-OFF resync is only *allowed*. If the Mac is OFF and the window skips the resync, the setter prints `Network Time is already off.`. So a literal "exactly `setUsingNetworkTime: Off`" would make every window turn network time ON at arm. That converts an optional step into a mandatory one and contradicts "stays OFF" as policy. The sealed text's purpose is a receipt proving the OFF end state on the same boot, settled at least 600 s on both clocks. Both receipts meet that purpose: exit 0, empty stderr, same boot, and about 1244 s / 1247 s before the first stamp on both clocks. In fact the "already off" form is the stronger statement, because it shows no ON interval preceded the window.

**The proposed text does not describe the code in three places**, so I amend it:

1. The code reduces every internal whitespace run, including newlines and Unicode spaces, to one space. The proposal says only "surrounding whitespace".
2. The code strips any number of trailing periods. The proposal says "one".
3. The code tolerates **any** standard error. It checks only that stderr is a string. Sealed §5 tolerates "the known `Error:-99` diagnostic line". The proposal calls the stderr condition "unchanged", which is true of the text but not of the code.

None of the three touches these windows: both stdouts are byte-identical to the canonical "already off" string, and both stderrs are empty. All three are refused-case widenings, and none can admit an ON statement. A two-line Off+On output is refused, because the normalised string is not in the set.

**Voiding sentence.** The proposal also leaves unaddressed the prior refuter's point (REFUTER-on-ruling, defect 3): §5's "a change to any of them voids this revision". My adopted text says why that sentence is not engaged. The operating condition is unchanged and evidenced; only the recognition of an equivalent macOS statement of it changed.

**Neither question bears on a number.** The issuer's settle and boot checks run against chain-start admission, which precedes the first capture on the same monotonic clock, so they are conservative against §5's first-capture wording. The R9 record does not read the receipt.

### Question 2 reasoning

(a) **No ledger session.** Neither attempt opened a ledger session. The ledger is clean after the pinned head (row 276): exactly the two admitted sessions follow it. So neither attempt is a session or a null session under §7; clause [0] and STOP-NULL-REPEAT do not reach them. The 0137Z `start_conditions.json` carries a `session_id` string. §7 has the issuer decide sessions "from the ledger; never from the operator's naming", so that string is a pre-allocated name, not an opened session. It is a finding, not a defect.

(b) **No selection on a measured value.** 0137Z refused 4 ms after the setter returned, before chain start, with census 0 and no capture writer. 0555Z refused at the arm battery read, before publication. Neither saw a B value or any slot; nothing existed to select on. The only thing the refusals moved is *when* C1 ran, which is not an outcome of the experiment.

(c) **Bound on successive refusals.**
- D-182's rule licenses ONE new-plan successor *per refused night*. It does not cap a chain of distinct refusals.
- §7's only consecutive bound (`max_consecutive` 1, STOP-NULL-REPEAT) is on ledger null sessions. Neither attempt is one.
- The owner's R5 caps the same signature twice in a row. The two signatures differ: `night_probe_error`/network-time at t0, versus the battery gate at the arm check.

So every bound that exists was respected.

Precision on which rule licensed which step:
- D-182's machine-state code list does not include a recognizer `night_probe_error`, and A-R5b's `night_probe_error` mention concerns battery-float probe failures. So 0137Z's re-arm is licensed by the owner's 09-30 route R1/R3/R4: a pre-start refusal, code cured by PR #448, new plan id. It is **not** licensed by D-182 itself. D-182's own terms were nevertheless met: zero capture positively evidenced, `courier.sent` present, new id, fresh notice, and more than 60 s spacing (18:38 → 21:24/21:48).
- 0555Z was never published, so it is not a D-182 "night". It is an arm refusal with zero capture, which A-R5b "Admission" makes a D-182 machine-state refusal licensing one successor. 0617Z was that one successor.

Within terms.

### Other findings (not defects)

- **Seal citation.** The charge's "sealed at commit `46643f1d` … file sha256 `d0034003…`" pairs the code-base commit with the text's hash. The file with that hash first exists at `bf017893` (16:47 PDT). No consequence: both commits precede `2431dcaa`.
- **Prior ruling's ages.** RULING-judge §6 item 1 gives 1243 s and 1246 s. I get 1244.37 s and 1246.97 s from the earliest d01 clock stamp. The difference is which stamp counts as "the first capture". All are about 2× the 600 s bound.

## Phase 2: on the ruling

The ruling (`/Users/edr/code/JouleWise-ent1-judge/docs/process_traces/2026-10-02-interactive/41-erratum-nt1-ruling.md`,
25 733 bytes, unchanged between 16:41 and 16:42 PDT) was read only after Phase 1 above was written.
It reads `ERRATUM E-NT1: ADOPT <amended text>` / `CHAIN: WITHIN TERMS`, which matches my provisional answers.

### What I confirmed in it

- **Receipts, boot, ages.** Same bytes, hashes and boot id as mine. The ruling dates the first capture
  from d01's `pre_spawn` stamp (+1243.41 s / +1245.94 s). I used `first_parse` (+1244.37 s /
  +1246.97 s). `pre_spawn` is earlier, so the ruling's figure is the more conservative one, and both
  are about 2× the 600 s bound. Its wall-minus-monotonic same-boot argument (within 5 ms) is the
  same as mine (within 4 ms).
- **Amendments to the proposal.** Internal whitespace collapse and "any trailing periods" are the
  same two code mismatches I found. The added sentence on why §5's voiding sentence is not reached
  answers the prior refuter's defect 3.
- **§7 JSON.** Leaving `stdout_exact` byte-identical so the sealed policy digest `dfa1ec73…` still
  verifies is correct, and it is a consequence I did not check. I did not recompute that digest;
  I accept it as the ruling's executed check 4b.
- **Issuance.** The issuer reads stdout only through `admit()` and the R9 record does not read the
  receipt. Same finding as mine.
- **Chain.** Ledger: only 0617Z and 2252Z after the pinned head (row 276). The ruling also matched
  that row's digest to the pin, which I did not do. 0137Z is a pre-start refusal with no `runs/`;
  0555Z was never published; the R5 signatures differ; STOP-NULL-REPEAT was never engaged. I
  verified "night gate GO at 23:27:35 PDT" in the 0617Z `night.log` (line 2).

### Defects found (none changes a number or the admission of either window)

1. **The adopted text says something the code does not do, and the ruling says it found "no
   remaining difference".** The adopted text says "any other output, including … a multi-line
   output … is refused". The code first collapses every whitespace run, newlines included, so a
   statement wrapped across lines is **admitted**. Tested:
   - `setUsingNetworkTime:\nOff\n` → True
   - `Network Time\nis already off.\n` → True
   - `Network Time is already off.\n\n` → True

   What the code actually refuses is an output carrying a second statement, for example
   `…Off\nsetUsingNetworkTime: On` or a repeated `Off\nOff`. Those are refused because the
   collapsed string is not in the set, not because the output spans more than one line.
   The adopted text also contradicts itself: its own first clause ("collapsing every run of
   whitespace") admits exactly these wrapped outputs.

   Cure, when the erratum is appended: replace "a multi-line output" with "an output that states
   anything besides one admitted statement (for example an OFF statement followed by an ON
   statement)".

2. **Standard error: the code is wider than the text, and the ruling does not say so.** The adopted
   text keeps "the tolerated stderr diagnostic" as "unchanged". Sealed §5 tolerates "the known
   `Error:-99` diagnostic line". `admit()` checks only that stderr is a `str`. A receipt with
   stderr `"anything at all\n"` is ADMITTED (my check 2d), and no code under `joulewise/` or
   `scripts/` mentions `Error:-99`.

   This is a second place where the code admits more than the text says. The charge required the
   ruling to say where text and code differ, and it does not. Both admitted receipts have empty
   stderr, so neither window is affected.

   Cure: one sentence in the appended erratum recording the difference, plus either a code
   narrowing or an explicit statement that stderr content is not a receipt condition. This is
   the D-138 seat's or the owner's choice, not mine.

3. **Which rule licensed 0137Z's re-arm.** The ruling's conclusion places both attempts "within
   D-182's terms as extended by A-R5b and the owner's route", and part (c) calls 0617Z "the one
   new-plan successor of 0137Z" under D-182.
   - D-182's licence covers *machine-state* refusal codes (agent, not quiet, bind-window expiry,
     screensaver, boot clock).
   - A-R5b adds battery-float arm/t0 refusals.
   - 0137Z's `night_probe_error` was a recognizer (code) defect, which is neither.

   Its re-arm is licensed by the owner's route R1/R3/R4, not by D-182. D-182's own terms
   (zero capture positively evidenced, `courier.sent`, new id, fresh notice, at least 60 s) were
   nonetheless all met, so the conclusion stands. The attribution should be precise.

4. **Scope of what the ruling read.** Part (c) quotes D-182's "no frequency bound is added; every
   bound must be scientific". That sentence is in D-182's "What this does not change" paragraph,
   outside the charge's "the rule and its Terms paragraph only". The ruling's contamination
   disclosure does not list it. I read the same paragraph by accident and disclosed it; my
   answer to (c) does not rest on it.

   Without that sentence the answer to (c) is unchanged. The rule's "ONE new-plan successor" is
   attached to each refused night, and nothing in the rule, the Terms, A-R5b or Revision 6 caps
   distinct pre-start refusals; the only caps are STOP-NULL-REPEAT on ledger null sessions and
   R5 on a repeated signature.

5. **Nit: a figure with no check behind it.** Part (c) cites "check 6e" for the night-gate GO time,
   but row 6e of the ruling's table does not list it. I verified it independently, as noted above.

### Why AGREE and not DISAGREE

- Defects 1 and 2 are real mismatches between text and code, not wording nits. Both concern
  hypothetical receipts: a statement wrapped across lines, and non-empty unusual stderr.
- Both admitted receipts are single-line, byte-identical to `Network Time is already off.\n`,
  with empty stderr. They are admitted under the sealed purpose, under the ruling's adopted text,
  under my amended text and by the code.
- So neither defect changes a number, a member, a statistic, an operative or the admission of
  either counting window.
- Neither changes what the registration says about the receipts actually admitted. The cure is
  a phrase replacement and a one-sentence disclosure inside the same single erratum when it is
  appended. That respects "Ruling-findings settle in ONE erratum, not a chain".
- Defects 3 to 5 are attribution and disclosure precision.

The D-138 seat should apply cures 1 and 2 to the erratum text it appends.

## Plain summary

The judge and I independently reached the same rulings: the "already off" receipts meet the
registration's purpose (OFF, same boot, about 1245 s settled on both clocks), and the two refused
attempts before C1 opened no ledger session and captured nothing, so C1 is admissible.
The ruling's adopted text gets two edge cases wrong. It says multi-line outputs are refused, but
the code admits a statement wrapped across lines. It calls the stderr condition unchanged, but the
code accepts any stderr. The appended erratum should fix both; neither touches these windows.
No number, member, statistic, operative or window admission changes: AGREE.
