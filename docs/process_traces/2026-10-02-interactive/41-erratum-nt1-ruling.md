ERRATUM E-NT1: ADOPT E-NT1. In Revision 6 §5 "Network time", the condition "its standard output is exactly `setUsingNetworkTime: Off`" reads: "its standard output states the OFF end state: after collapsing every run of whitespace to one space, trimming surrounding whitespace, removing any trailing periods and ignoring letter case, it equals either `setUsingNetworkTime: Off` (the setting was ON and is now OFF) or `Network Time is already off` (the setting was already OFF); any other output, including an ON statement, empty output, the getter form `Network Time: Off`, a multi-line output, and the exit-0 `You need administrator access to run this tool... exiting!` text, is refused". The §7 JSON key `stdout_exact` is read the same way; the §7 JSON block itself is not edited (its sealed policy digest `dfa1ec73…` is unchanged). Every other receipt condition (exit status 0, the tolerated stderr diagnostic, same boot, at least 600 s before the first capture on both clocks, one receipt per window) is unchanged. The registered operating condition, network time OFF and settled on the same boot, is unchanged, so the §5 sentence "a change to any of them voids this revision" is not reached: only the recognition of macOS's second statement of that same state changed. No number, member, statistic or operative changes.
CHAIN: WITHIN TERMS

# Cold erratum gate E-NT1: the OFF receipt wording, and the two attempts before C1

Judge: one non-interactive Claude Fable 5.1 session, worktree `/Users/edr/code/JouleWise-ent1-judge`
at HEAD `35515f83ef82f1201b5100b133511d1429ac11f2`, 2026-10-02 16:33 to 16:41 PDT. Foreground
commands only; no background task, no subagent, no sudo, no systemsetup, no launchctl, no
powermetrics, no git write. Read-only except this file and `/tmp/cg-ent1-d138/` (created, unused).

## Contamination disclosure

What was in my context before any ruling, without my asking for it: the harness injected
`/Users/edr/.claude/CLAUDE.md` (global rules, a writing standard), this worktree's `CLAUDE.md`
(Codex bridge notes) and the one-line index `MEMORY.md` of the JouleWise memory directory. That
index contains pointer lines such as "C1+C2 24/24 CLOSE_AND_DERIVE; nothing armed; #454 issuer
fix + #455 records merged" and "PR 449 (handback fix + halt record) UNMERGED". I opened no memory
file, no skill file, and did not read `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md` or
`CLAUDE.local.md` at HEAD. None of those index lines bears on either question here.

What I read by choice outside the charge's list, and why:

- `git show 835aaba3` and `git show 835aaba3:RUN_STATE.md` lines 28 to 38 (plus one stray grep hit
  at lines 1500 to 1503 about an unrelated `_v4` transaction), and
  `docs/process_traces/2026-09-29-interactive-ff50b201/171-magistrate-block-brief.md` at that
  commit, lines 16 to 26: to verify that the refusal route the charge quotes (R1 to R5) is the
  owner's text at that commit. It is, verbatim.
- `git log`/`git show` of the registration file's history, commits `46643f1d`, `bf017893`,
  `2431dcaa`, and `tests/fixtures/epoch_bootstrap/revision6_declaration.json` (grep for
  `stdout_exact` only), to settle the seal provenance (see check 3a).
- `scripts/issue_calibration_acceptance_generation.py` lines 98, 1125 to 1180, 1446 to 1520,
  1540 to 1560, 1690 to 1705, and a one-off import of it to recompute the sealed policy digest.
- `joulewise/arm_readiness.py`, `joulewise/t0_rehearsal.py`, `scripts/capture_t0_step.py`,
  `joulewise/quiet_predicate_campaign.py`, `scripts/bench_replay_systemsetup_stub.py` (grep hits
  only), and `tests/test_network_time_off.py` (run, not edited).
- `RULING-judge.md` header and §6; `REFUTER-on-ruling.md` lines 1 to 6 and 40 to 100.
- `sysctl kern.bootsessionuuid kern.boottime` on this Mac (read-only).
- Custody files beyond the three receipts: `night/start_conditions.json`,
  `start_conditions_manifest.json`, `night_plan.json`, `night.log`, `night/censuses.jsonl`,
  `night/courier.sent`, `night/receipt.json` (boot lines only) of the three plans, and the `d01`
  `instrument_evidence.json`, `events.jsonl`, `power_trace.csv` head and `manifest.json` of
  both admitted windows. I read no member value and no B.

Side effect: running the unittest file may have written `__pycache__` directories inside the
worktree; `git status` after the run reports the tree clean apart from this file.

## Table of executed checks

| # | Command (abridged) | Result |
|---|---|---|
| 1a | `cat` + `shasum -a 256` of the three `night/network_time_off.json` | c1-0617Z sha `243d3796…`, c2-2252Z sha `09e0a209…`, c1-0137Z sha `1f877794…`. All three: `argv` = `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`, `exit_code` 0, `stdout` `"Network Time is already off.\n"`, `stderr` `""`, `error` null, `boot_id` `cd5b815a-df9b-4fc7-921a-8e97d8aba867`, schema `joulewise.network_time_off.v1`, plan and window ids equal to the directory's plan id. |
| 1b | `sysctl kern.bootsessionuuid kern.boottime` | `CD5B815A-DF9B-4FC7-921A-8E97D8ABA867`, boot 2026-09-18 17:40:47 PDT. Same boot as all three receipts and both windows' `night/start_conditions.json` (`boot_id` equal). The capture evidence carries no `boot_id`; see 1d for the same-boot arithmetic. |
| 1c | python: age of receipt before the first capture, `d01/instrument_evidence.json` `clock_anchor.clock_stamps` | c1-0617Z: receipt epoch 1790835422.280 / monotonic 1056984.267; `pre_spawn` of d01 at +1243.408 s wall, +1243.412 s monotonic; `sampling_started` +1244.920 / +1244.924. c2-2252Z: receipt 1790895121.218 / 1116683.394; `pre_spawn` +1245.940 / +1245.944; `sampling_started` +1247.972 / +1247.976. Both ≥ 600 s on both clocks. The issuer's own figure (`settled_seconds` in `start_conditions.json`, taken at chain-start admission) is 633.13 s and 633.45 s, consistent (chain start precedes the first capture by about 610 s). |
| 1d | python: wall minus monotonic, receipt vs capture | c1: receipt 1790835422.280 − 1056984.267 = 1789778438.014; d01 `clock_anchor.wall_minus_monotonic` = 1789778438.0091 to 1789778438.0097. c2: 1790895121.218 − 1116683.394 = 1789778437.825; d01 = 1789778437.8200 to 1789778437.8207. Same monotonic origin to within 5 ms in each window: receipt and first capture share one boot. |
| 2a | `cat -n joulewise/network_time_off.py` | Comparator `off_stdout_admitted`: non-`str` → False; else `" ".join(stdout.split()).casefold().rstrip(".").rstrip()` ∈ {`setusingnetworktime: off`, `network time is already off`}. `admit()` additionally requires schema, exact argv, `exit_code` is `int` and 0, `stderr` is `str`, non-empty `boot_id`/`plan_id`/`window_id`, finite clocks. `seconds_since_receipt` requires the same boot id (case-insensitive) and ≥ 600 s on both clocks. `EXPECTED_STDOUT` still exists (used only by a bench stub and an import). |
| 2b | `git show 2431dcaa` (code + tests) | Author Ed R, 2026-09-30 21:13:24 PDT. Replaces `!= EXPECTED_STDOUT` at four sites (`network_time_off.admit`, `arm_readiness` export, `t0_rehearsal.evaluate_g4` ×2, `capture_t0_step._validate_result`) with the comparator. Tests: the C1 receipt bytes admitted; refused: exit 1 with either wording, `On`, `already on`, empty, admin-access text, two-line `Off\nOn`, getter `Network Time: Off`, `not setUsingNetworkTime: Off`. A guard test fails if any module compares stdout to the literal again. |
| 2c | python: comparator on receipt bytes and probes | All three receipts → True (and `admit()` OK). `setUsingNetworkTime: Off\n` True; `setUsingNetworkTime: On\n` False; `""` False; `Network Time: Off\n` False; `You need administrator access to run this tool... exiting!\n` False; `NETWORK TIME IS ALREADY OFF.` True; `  setUsingNetworkTime:   Off  \n` True (internal whitespace run collapsed); `Network Time is already off..` True (all trailing periods stripped); `setUsingNetworkTime: Off.` True; `None` False; `b"setUsingNetworkTime: Off\n"` False (bytes refused; receipts store `str`). |
| 2d | `python3 -m unittest tests.test_network_time_off` at HEAD | 15 tests, OK. |
| 3a | `shasum` of the registration at HEAD and `git show 46643f1d:…`, `bf017893:…` | HEAD file sha `d0034003…` (the charge's value). At `46643f1d` (merge of PR #445, 15:09 PDT) the markdown file is still the Revision 5 + A-R5b text (sha `81b65f08…`); the Revision 6 text, including §5 "exactly `setUsingNetworkTime: Off`" and the §7 JSON, entered the markdown at `bf017893` ("Seal Revision 6", 16:47 PDT), which is not an ancestor of `46643f1d` but is an ancestor of HEAD. At `46643f1d` the same `stdout_exact` value already sat in `tests/fixtures/epoch_bootstrap/revision6_declaration.json` line 88. Either way the sealed wording predates `2431dcaa` (21:13 PDT) and the first C1 attempt (18:37 PDT). |
| 3b | `sed -n 967,1025p` (§5) | §5 "Network time" quoted in full below. The header says "A change to any of them voids this revision." |
| 3c | `sed -n` §0 line 731, §6 line 1009, §7 lines 1118–1126, 1145–1196, 1293–1312, 1322–1350, 1364–1368, 1394; §11 1705–1706 | Null-session definition, clause [0], STOP-NULL-REPEAT, `max_consecutive: 1`, "sessions_of_this_registration = every derivation-kind session opened after `pins.ledger_head_pin_at_first_window`", the `network_time_off_receipt` entry (`stdout_exact: "setUsingNetworkTime: Off"`, `same_boot_as_first_capture: true`, `min_age_before_first_capture_s: 600`, `clocks: [wall, monotonic]`, `receipts_per_window: 1`). |
| 4a | `grep -n` issuer for `network_time`, `stdout_exact`, `start_condition` | Issuer imports `network_time_off`; `revision_six_start_conditions` (lines 1446–1520) requires exactly one evidence entry at `night/network_time_off.json`, parses it, calls `network_time_off.seconds_since_receipt(off, chain_start_admitted)` (which calls `admit()`, hence the comparator), and requires `plan_id` match and `600 ≤ settled_seconds ≤ settled`. The string `stdout_exact` occurs nowhere in the issuer or `joulewise/`. |
| 4b | issuer lines 1125–1180 + recomputation with the measurement clone's interpreter | The issuer parses the §7 JSON from the markdown and hashes the policy keys (`sessions`, `start_state_conditions`, `start_condition_evidence`, `definitions`, `count_rule`, `stop_lines`, `sampling_dependence`): file gives `dfa1ec736de6a9a8cab71a7d2e0bd0732df3ad733af8a2908fa58e4ceb0bfeff` = `REVISION_SIX_POLICY_SHA256`. Editing `stdout_exact` in place changes the digest and the issuer would refuse ("unsupported Revision 6 policy or sealed amendment"). So the issuer reads the receipt's stdout only through the comparator, and reads the JSON key only as bytes under a digest. |
| 4c | `r9_campaign.json` in the packet | Two sessions, `0617Z` and `2252Z`, both `null: false`, 12 slots, counted 12, valid 12; `clock_movement_or_empty_fit_refusals: []`; no mention of `0137Z`, `0555Z` or `network_time`. The R9 record does not read the receipt. |
| 5a | `RULING-judge.md` §6 items 1 and 3; `REFUTER-on-ruling.md` F1 and defect 3 | Both ask for an erratum or written ruling before the successor issues; the refuter asks that the ruling say why §5's voiding sentence is not reached. |
| 6a | 0137Z custody: `night/result.json`, `night/refusal.json`, `ls night/chain.started`, `ls runs`, `night.log`, `censuses.jsonl`, `courier.sent` | `verdict` REFUSED, `aborted_reason` `night_probe_error`, `chain_exit_code` null, `chain_sha256` null, `receipt_class` DIAGNOSTIC_NO_PACK; refusal detail "network time OFF receipt not admitted"; no `night/chain.started`; no `runs/` directory at all; one census row with zero hits (`pgrep` exit 1); `courier.sent` present (105 B). `night.log` has four lines: driver started 18:37:02.33 PDT, record pushed, courier sent, record pushed. Receipt epoch 1790818622.388, terminal write 1790818622.393: refused 5 ms after the receipt, at t0. `start_conditions.json` `result` refused, `settled_seconds` 0.004. |
| 6b | 0555Z: `00-session-record.md` items 2–3; `c1-rearm/battery-refused-0555Z-attempt.txt` | Battery gate observed 2026-10-01T04:24:54Z (21:24:54 PDT); ExternalConnected Yes, IsCharging No, InstantAmperage raw 18446744073709551169 = 2^64 − 447 → −447 mA (my arithmetic agrees), 82 %; failed `abs ≤ 200 mA`. Record says nothing was published for that t0; no custody directory for 0555Z exists under `/Users/edr/night-custody/`. |
| 6c | ledger scan, `calibration_observation_ledger.jsonl` (376 rows, sha `3c9b6844…`) | Row 276 `receipt_digest` = `476e2ae8…` = `pins.ledger_head_pin_at_first_window.digest`. Rows 277–376 are contiguous and contain exactly two sessions: `bracket-session-open` at seq 278 for `d079-epoch-25g83-r6-20261001T0617Z` and at seq 328 for `…20261001T2252Z`, each with 12 slot claims and 12 finalizations plus paired `append-intent` rows. No row anywhere in the ledger mentions `0137Z` or `0555Z`. |
| 6d | `## D-182` in `docs/decision_log.md` (rule + Terms); A-R5b "Admission" (registration line 654) | Quoted and applied below. |
| 6e | timing arithmetic | 0137Z terminal write 18:37:02 PDT → 0555Z battery observation 21:24:54 PDT: 10 072 s. 0555Z observation → 0617Z plan authored 21:46:37 PDT: 1 303 s. 0617Z t0 23:17:00 PDT; receipt t0 + 2.3 s; chain start admitted t0 + 635 s; first capture t0 + 1 246 s. |

## Question 1: does the OFF receipt condition admit `Network Time is already off.`?

**What the sealed text requires, and why it is worded as it is.** §5 defines the receipt as a
record of one run of the OFF setter that meets four conditions: exit 0; stdout exactly
`setUsingNetworkTime: Off`; same boot as the first capture; at least 600 s before that capture on
both clocks. The surrounding text fixes the purpose: network time "stays OFF on the measurement Mac
(D-186)", the receipt is what "admits" a window, and "a brief clock resync is allowed only in the
window's arm step: network time ON, then OFF, then the receipt". The §7 JSON restates the same four
conditions with `stdout_exact`.

**What macOS prints.** The three receipts show, on this Mac, that `systemsetup -setusingnetworktime
off` prints `Network Time is already off.` with exit 0 when the setting is already OFF. The widening
commit, the recognizer's comment and the owner's route record all state that
`setUsingNetworkTime: Off` is what the setter prints when it switches ON to OFF. I could not run
the setter myself (it needs root and the charge forbids it); I take the receipts as the evidence
of the first wording and the code comment and commit as the evidence of the second. Nothing in
this ruling depends on the second wording being exact, because the erratum keeps it as one of two
admitted strings and the comparator is tested against it.

**Is a literal reading consistent with the rest of §5?** No. Under a literal reading a window can
be admitted only when the setter actually switched the setting from ON to OFF at t0. But §5 also
requires that the setting "stays OFF" between windows (D-186) and makes the ON-then-OFF resync
optional ("allowed only in the arm step"). A window that obeys "stays OFF" and does not take the
optional resync can never produce the literal wording. The literal reading therefore makes the
optional resync mandatory and makes every window that follows the standing policy inadmissible,
which is the opposite of what §5 says the receipt is for. The first C1 attempt showed this
concretely: it was refused at t0 while network time was OFF, which is the condition the receipt
exists to prove. The sealed wording was a transcription of one of two macOS strings, not a
requirement that the setting be toggled.

**Is the purpose met by the two receipts?** Yes, on my own arithmetic (checks 1a to 1d): exit 0,
empty stderr, the OFF end state stated, the same boot as the first capture (boot id equal to the
window's start-condition record and to the current boot session; wall minus monotonic offset of
the receipt equals the first capture's clock-anchor offset to within 5 ms), and 1 243 s and
1 246 s before the first capture on both clocks. The OFF state is further corroborated by R9:
zero clock-movement or empty-fit refusals across 24 captures.

**Does the recognizer do what the erratum says?** Check 2c shows the comparator admits exactly the
two statements after normalisation and refuses ON, empty, the getter form, the admin-access
text, two-line output and bytes. Three details of the proposed erratum text do not match the
code, so I amended the text rather than adopt it as proposed:

1. The code collapses every internal run of whitespace to one space, not only "surrounding"
   whitespace. The adopted text says so.
2. The code removes any number of trailing periods (`rstrip(".")`), not "one trailing period".
   `Network Time is already off..` is admitted. The adopted text says "any trailing periods".
   This is harmless: no OFF statement with extra periods is a different end state.
3. The proposal writes the second admitted string with its period, `Network Time is already
   off.`; since periods are stripped before comparison the adopted text writes it without.

The adopted text also lists what is refused, so that a reader can replicate the comparator from
the registration alone. With those amendments the text describes what the code does, and I found
no remaining difference.

**Where the erratum lives, and the §7 JSON.** The issuer hashes the §7 policy block (check 4b).
If the `stdout_exact` value were edited in place, the digest would change and the issuer would
refuse every issuance until its constant were changed too. The adopted erratum therefore reads
the key rather than edits it: the JSON block stays byte-identical and the erratum text is
appended to the registration (as A-R5b was). This is also the only honest form: the sealed bytes
stay sealed, and the correction is visible as a correction.

**The voiding sentence (refuter's defect 3).** §5 says a change to any listed item voids the
revision. The item is the operating condition: network time OFF, evidenced by a settled same-boot
receipt. That condition did not change; the Mac was OFF before, during and after both windows,
and the receipts say so. What changed on 2026-09-30 21:13 PDT was which of macOS's two statements
of that one state the code recognises. Recognising a second true statement of the registered
state is not a change to the state. The erratum text says this explicitly so the D-138 gate does
not inherit the question.

**Issuance.** The issuer reads the stdout only through `admit()` (check 4a); its registered
checks (one receipt, plan binding, settle ≥ 600 s, same boot) pass on both windows. The R9 record
does not read the receipt (check 4c). Under the adopted erratum the two receipts meet the
registration. Under a literal reading, and only under it, they would not; that reading is
rejected above because it contradicts §5's own "stays OFF" and "allowed only" clauses.

**Process note, not a defect in the numbers.** The owner's route R3 says: write the erratum and
convene one cold gate, "then proceed on its ruling". The proceed came first (re-arm 21:46 PDT,
window 23:17 PDT) and this gate is being convened after both windows ran. That ordering is a
process deviation to record, not a reason to refuse the windows: the condition the erratum
describes was physically met, nothing in the fix touches a captured byte or an estimator file,
and this ruling is the ruling the route required.

## Question 2: is a chain of two zero-capture attempts before C1 within D-182 and A-R5b?

**The rules, read together.** D-182: a night that refuses on machine state with zero capture
licenses ONE new-plan successor, where "zero capture" means no reservation opened a ledger
session, no capture writer ran and `runs/instrument_validation` is empty, the successor is armed
at least 60 s after the refused plan's terminal write with its own id, and the refused plan is
never re-armed. A-R5b "Admission": a t0 or arm refusal with zero capture is a machine-state
refusal under D-182, licensing one new-plan successor on D-182's terms, never a same-plan retry.
Revision 6 §7 clause [0] and `null_session`: a null session is a session of this registration
that opened and ended before any capture was attempted; `max_consecutive: 1`; STOP-NULL-REPEAT
fires on a null session whose preceding session was also null, in ledger order; sessions of this
registration are the derivation-kind sessions opened after the pinned ledger head. The owner's
route R1 defines a pre-start refusal (REFUSED, null chain exit and digest, no `chain.started`, no
session id opened) and says the same label is armed again; R5 bounds it: the same refusal
signature twice in a row goes to Ed, never a third arm on one signature, and the registration's
two-null-session stop also halts.

**(a) Did either attempt open a ledger session?** No. The ledger after the pinned head (seq 276,
digest matching the pin) holds exactly two session opens, 0617Z and 2252Z, and no row names
0137Z or 0555Z (check 6c). So neither attempt is a session of this registration, and neither is a
null session. The null-session count in ledger order is zero; STOP-NULL-REPEAT could not fire.
The issuer's session enumeration (R9 record, check 4c) names only the two windows, as §7 requires
("every session of this registration must be named at issuance"). The string
`d079-epoch-25g83-r6-20261001T0137Z` in 0137Z's `start_conditions.json` is the id the plan would
have used; it was never opened in the ledger.

**(b) Could either attempt have selected on a measured value?** No. 0137Z: no `runs/` directory
exists, `chain.started` is absent, `chain_exit_code` and `chain_sha256` are null, the census had
zero hits, and the refusal was written 5 ms after the receipt at t0 (check 6a). The only thing
decided was a string comparison on the setter's stdout. 0555Z: refused at the bench's step 0 at
21:24:54 PDT, before any plan was published; the only observed quantities are battery telemetry
(−447 mA, 82 %), which is a registered start condition, not an experimental value, and no capture
of any kind existed to select (check 6b). Neither attempt produced a cell count, a frame, a
ratio or a B. The two refusals also have different causes on different checks (a code defect in
the wording check at t0; battery not floating at arm), so neither could be a retry chosen on the
other's outcome.

**(c) Is the number of successive zero-capture refusals bounded, and was the bound respected?**
D-182 bounds the successor of each refusal to one new plan; it does not bound how many refusals
may occur in sequence, and says so by design ("no frequency bound is added; every bound must be
scientific"). Its one-successor licence was used once: 0617Z is the one new-plan successor of
0137Z. 0555Z never became a "night" in D-182's sense (an armed unattended plan): it was stopped
by the recipe's own pre-publication battery gate, which is R3's "wait for physics" branch, and the
next arm after the float was reached is 0617Z. Even read most strictly, as two refusals each
licensing one successor, the chain is 0137Z → 0555Z → 0617Z, each link a new plan id, each armed
well over 60 s after the previous terminal write (10 072 s and 1 303 s, check 6e), no plan
re-armed, `courier.sent` present for the one plan that was armed and refused. The registration's
only sequence bound, two consecutive null sessions, counts sessions in ledger order and never
engaged. The owner's R5 bound, the same signature twice in a row, never engaged: the signatures
differ (`night_probe_error` / "network time OFF receipt not admitted" versus the arm-step battery
refusal), so there was no third arm on one signature. The C1 that ran passed every gate anew at
its own t0 (night gate GO at 23:27:35 PDT, check 6e), as D-182 requires of a successor.

**Conclusion.** Both attempts were zero-capture pre-start refusals within D-182's terms as
extended by A-R5b and the owner's route; neither is a session, a null session or a window of
this registration; the C1 that ran (`…-c1-20261001T0617Z`) is an admissible window of Revision 6.

## Bearing on members, statistics, operatives and admission

- Question 1 changes no member, statistic or operative. It changes the registration's
  description of which stdout proves the OFF state; both windows' receipts satisfy the adopted
  text and satisfied its purpose before the text was corrected. The admission of
  `…-c1-20261001T0617Z` and `…-c2-20261001T2252Z` is unchanged.
- Question 2 changes nothing: no session, null session, window label, count, stop or member is
  added or removed. STOP-NULL-REPEAT and the three-window count are untouched.
- One consequence for the successor record: the erratum must be appended as text, not applied
  inside the §7 JSON block, or the issuer's sealed policy digest check will refuse.

## Plain summary

The sealed registration named one of the two sentences macOS prints when network time ends OFF; the Mac was already OFF, printed the other sentence, and the receipts prove the required state on the same boot more than 20 minutes before the first capture, so the erratum is adopted with wording that matches the code exactly and leaves the sealed JSON and its digest untouched.
Neither attempt before C1 opened a ledger session or captured anything; the ledger after the pinned head holds only the two admitted windows, no stop could fire, and each re-arm was a new plan spaced far beyond 60 s, so the chain is within D-182, A-R5b and the owner's route.
Nothing here changes a member, a statistic, an operative or the admission of either window; the one process deviation is that this gate was convened after the windows ran rather than before, which is recorded and does not alter the numbers.
