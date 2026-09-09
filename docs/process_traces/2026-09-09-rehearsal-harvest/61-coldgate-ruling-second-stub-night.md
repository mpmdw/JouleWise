# Cold-gate ruling — SECOND-STUB-NIGHT-RULING (does the merged night-gate cure require a second REHEARSAL_STUB night before any DIAGNOSTIC_NO_PACK plan?)

Judge: cold Fable seat (claude-fable-5-1), single non-interactive session, convened under rule 11 from the packet
`60-coldgate-packet-second-stub-night.md`. Written 2026-09-09 ~09:05 PDT. Working directory: detached worktree
`/Users/edr/code/JouleWise-wt-kernel-fold` at main `7ca2908f` (working tree carried one uncommitted modification, `RUN_STATE.md`,
which I did not open).

## Contamination disclosure

Before I read anything, the harness injected into my system prompt: the global `~/.claude/CLAUDE.md` (multi-model orchestration
pointers and a writing standard), the project `CLAUDE.md` of this worktree (Codex bridge notes), the auto-memory index
`MEMORY.md` (one-line hooks only; the hooks mention PR #308/#309, the rehearsal, cold gate 44 and a "Low Power Mode attribution
WITHDRAWN" note), and a git-status snapshot with the eight most recent commit subjects. I did not open RUN_STATE.md,
TASK_QUEUE.md, docs/decision_log.md beyond the P1 excerpt, AGENTS.md, any skill, or any memory file, and I did not act on the
injected text; the ruling below is derived from the packet (P1–P9, the charge, 31 and its two addenda, 44 §Q3) and the probes
listed next. Nothing ran in the background; no subagent, watcher, or cron was created.

## Probes executed (all foreground, read-only)

- `shasum -a 256 -c 60-coldgate-packet.sha256` in the packet directory: 11/11 OK (packet index, eight excerpts, the charge, 44, 31).
- `git rev-parse HEAD` → `7ca2908f66819d534ebc53e3786f32106f6de5ba`; `git log --oneline -8` shows PR #309 merged at `a52810c9`
  and the bookkeeping commit `7ca2908f` on top, as the packet states.
- `git diff --stat 83ab38ed a52810c9` over the six cure files reproduces P7's diffstat exactly (6 files, +229/−101).
- `git diff 83ab38ed a52810c9 -- joulewise/night_gate.py scripts/run_night.py` read in full: the gate gains one predicate
  (`plan.receipt_class == "REHEARSAL_STUB"` → C5 measured `chain_sha256: null`, `expected_chain_sha256: null`,
  `chain_stub: built_in_stub_by_design`, no `read_text` of chain or sidecar); the non-stub ladder is the old code under `else:`;
  the driver's gate log line gains `reason=… detail=…` (single line, 200 chars) on REFUSED only.
- `git diff 83ab38ed a52810c9 -- tests/…` test names added: `test_rehearsal_stub_does_not_read_missing_chain_or_sidecar`,
  `test_rehearsal_stub_does_not_read_present_mismatched_chain_or_sidecar`, `test_diagnostic_still_refuses_missing_chain_or_sidecar`
  (gate); `test_gate_refusal_log_includes_reason_and_bounded_single_line_detail`, `test_non_refused_gate_log_keeps_exact_verdict_form`,
  `test_stub_without_chain_files_logs_rehearsal_only` (driver, in-process).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night` once: `Ran 136 tests in 9.229s / OK`.
- `launchctl list | grep -i joulewise` → only `com.joulewise.magistrate` (last exit 0). `ls -la /Users/edr/night-custody` →
  `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1` only. Nothing is armed; matches 21i.
- Read in `scripts/run_night.py`: the post-gate flow (lines 1480–1712), `_finish_reporting` (994–1024), `dead_man` (1727–1760),
  `_next_deadman_epoch` (945–955), constants `DEADMAN_HOUR = 7`, `COURIER_DEADLINE_S = 300` with the R-7 comment
  `min(600, max(3 * (5303 ms / 1000), 300)) from cold_start.json` (lines 50–51), exit codes (60–64).
- Read `scripts/install_night_agent.sh` label/dead-man lines (108–113, 160–212) and `scripts/measure_claude_cold_start.sh` in full.
- `grep -rln cold_start.json docs/process_traces` → six files; the wo2 driver brief (Deliverable E) specifies the script; no file
  under `docs/process_traces` or `runs` was found that IS a recorded `cold_start.json` (NOT EXECUTED: an exhaustive search of the
  home directory; I searched only the repository).
- NOT EXECUTED: what the driver does when the daily `com.joulewise.night` calendar trigger fires on a day BEFORE the plan's t0
  (relevant to the item-5 install timing in Q3); I found no explicit early-firing guard on the stub path in the lines I read and
  did not have time to trace `_completion_epoch_s`/window handling for that case.

## Q1 — Is a second REHEARSAL_STUB night required before any DIAGNOSTIC_NO_PACK plan is armed?

**Ruling: (c) — REQUIRED, and it must be the combined night that also closes item 5.** The requirement rests on the kernel's
unmet acceptance item 5, not on the cure; on the cure alone the answer would be (b). Both halves are stated so the record is
honest about the ground.

**Why the cure alone does not force a second stub night (the (b) half).**
1. The cured code path is the STUB branch of `evaluate_night`. A DIAGNOSTIC_NO_PACK night never takes it: it takes the `else:`
   branch, which delta re-audit 23b found byte-identical to the pre-cure ladder and which the regression
   `test_diagnostic_still_refuses_missing_chain_or_sidecar` pins. The charge's premise that "the first real night is also the
   first end-to-end exercise of the cured receipt path" is therefore not true for a real night; the only cure lines a real
   night executes are the driver's refusal log line and the conditional C5 detail sentence. A second stub night would exercise
   the stub branch, which no real night uses.
2. The driver→gate→receipt→courier chain under launchd WAS exercised end to end on 2026-09-09: for the stub class the driver
   proceeds identically whether the gate refuses or not (`rehearsal_effective`, run_night.py 1544–1568), and 21i records the
   receipt written, the stub chain run (rc 0), `result.json` REHEARSAL_ONLY, the durable record pushed twice, and the courier
   sent (`1a08599a4ff4d005`). The only artifact whose CONTENT was wrong was `receipt.json`, and terminal review 31 §4 plus my
   read of `_finish_reporting` show that nothing downstream branches on a stub receipt's verdict or C5 fields.
3. The defect shape is covered at two levels: gate-level with a probe source that raises on the chain path, and driver-level
   (`test_stub_without_chain_files_logs_rehearsal_only`, in-process, no chain files on disk). What the tests do not reach —
   launchd start, the real `Probes` adapter, a real checkout for the measurement-HEAD check — the first night already reached,
   and the cure removes reads from that surface rather than adding any.

**Why a second stub night is nevertheless required (the (c) half).**
4. Kernel acceptance item 5 ("a rehearsal with the agents installed the MORNING BEFORE the armed night, so the pre-night 07:00
   dead-man firing is observed standing down without writing anything but a log line") is OPEN, says "a rehearsal" in terms,
   and cannot be met by any night installed the same night. `dead_man()` (run_night.py 1727–1745) is class-independent, so the
   observation could technically be made on a real night — but the failure mode it guards is a pre-night dead-man writing
   `refusal.json`/`courier.sent` into `night/`, after which the real t0 run would refuse as a rerun via `_existing_record`.
   Observing that for the first time on a DIAGNOSTIC_NO_PACK night risks a wasted real night that costs an Ed sudo session and
   a powermode-0 window; observing it on a stub costs one headless arm ceremony. Soundness says spend the stub.
5. Once a stub night is being armed anyway, the receipt of that night must not refuse (only `night_refused_agent_present` is
   acceptable, per NIGHT_HANDBACK §Next lane), which live-proves the cured stub receipt as a free rider and lets item 6 be
   recorded MET without a finding. That is the combination (c) names.

**Consequences.** Item 6 stays "MET WITH A FINDING, cure merged" until the combined night's receipt is harvested non-refused;
NIGHT-REHEARSAL-01 remains BLOCKED on that night, not on any further ruling. If Ed waives item 5 (his call, not the magistrate's),
the (b) half governs and the next night may be the DIAGNOSTIC_NO_PACK plan once item 4's stage-1 email, powermode 0 (44 §Q3), and
G2-a inputs are in place; 99ey's clone-cut condition does not bind a DIAGNOSTIC_NO_PACK plan because it is not pack-bound, but
the plan's `measurement_root` must still not be a retained production clone (99ey Q1.1) — that constraint is the same for every
class.

## Q2 — May the headless magistrate arm it under D-175, and does anything change the conditions?

**Yes.** The combined stub night is a REHEARSAL_STUB plan and falls squarely inside D-175's authority ("authoring a plan with
`write_night_plan` and installing its two night agents is arming, not alteration"). The eight conditions apply unchanged; the
NIGHT_HANDBACK email-then-arm procedure and the disposable `/private/tmp` detached-checkout `measurement_root` pattern of
rehearsal-20260909 are valid (D-175: a `/private/tmp` detached checkout is a valid REHEARSAL_STUB root and must never be reused by
a real plan). 99ey does not touch a stub night. P8 (44 §Q3) expressly allows stub nights under powermode 1.

Conditions I add or make explicit for THIS night (none conflicts with the eight):
- **N1 — head pins.** `repo_head` and `measurement_head` are the cured merged head or a descendant of it (`a52810c9` or later on
  main); the disposable checkout is cut at that head; both `com.joulewise.night` and `com.joulewise.night.deadman` are installed
  from that checkout via `install_night_agent.sh` (never from the development checkout). Record the head in the arm record.
- **N2 — install timing for item 5.** The agents are installed on the calendar day BEFORE t0, at a wall-clock time strictly
  after that day's t0 hour:minute has passed and strictly before 07:00, so that the dead-man's first daily firing precedes t0 and
  the night agent's first daily firing IS t0. Record the install epoch and both firings' expected epochs in the arm record. (See
  Q3 on why the earlier bound matters and what I could not verify.)
- **N3 — no re-arm on the old signature.** New plan_id (not `rehearsal-20260909`), fresh non-symlink custody root under
  `~/night-custody`, fresh checkout path; 21i's plan is never re-armed.
- **N4 — powermode recorded, not gated.** Record `pmset -g batt` source and `pmset -g custom` powermode in the arm record and,
  if the courier prompt allows, in the courier body; state explicitly that a green stub says nothing about the capture-timeout
  seam (44 §Q3 wording). Not a gate for a stub.
- **N5 — receipt acceptance.** Harvest acceptance requires `receipt.json` verdict NOT `REFUSED` (or exactly
  `night_refused_agent_present`), C5 measured `chain_stub: built_in_stub_by_design` with null digests, and `night.log` carrying
  the dead-man stand-down line before the `night gate verdict=` line. Any other refusal is a finding to cure before any plan.
- **N6 — D-175 condition 8 scope.** Post-completion uninstall and removal follow 21i's documented practice; the scope question
  21i referred (whether condition 8's arm-shaped steps govern removal) is not decided here and does not block arming.

Nothing in D-175, 99ey, or P8 forbids the headless arm. The magistrate must still exit by t0 − 25 min and must confirm no other
agent session is alive at install time; with the longer lead of N2, the census must be re-run immediately before the install,
as condition 8 already requires.

## Q3 — What closes item 1 and item 5?

**Item 1 (cold_start.json / COURIER_DEADLINE_S).** Evidence that closes it: a `cold_start.json` produced by
`scripts/measure_claude_cold_start.sh` on the night-driver machine (five `claude -p` READY round-trips, `median_ms`, Gmail tool
names), stored under a custody or trace path named in the kernel row, plus a pointer showing `COURIER_DEADLINE_S` in
`scripts/run_night.py` equals `min(600, max(3 * median_s, 300))` computed from that file's median. Today the constant is 300 with a
comment citing a 5303 ms median, but I found no committed `cold_start.json` in the repository (search limited to the repo — see
Probes). Closing item 1 is desk work: locate or re-run the script (it invokes `claude -p`, so it is itself an agent session and
must NOT run while a night is armed or a quiet window is open), commit or trace the JSON, and cite it. A stub night neither
closes nor needs item 1; the 300 s deadline was observed adequate on 2026-09-09 (courier sent 93 s after t0).

**Item 5 (agents installed the morning before; 07:00 dead-man observed standing down).** Evidence that closes it: in the
harvested `night.log` of a night whose agents were installed before 07:00 on the day before t0, the line
`dead-man fired before the night's completion epoch <epoch>; standing down` timestamped at ~07:00 that day, with `night/`
containing nothing from that firing (no `refusal.json`, no `courier.sent`, no `courier.json` before t0), and the night's own
run then proceeding normally at t0. Yes — a stub night closes item 5 ONLY if installed before 07:00 the morning before; an
install after 07:00 yields no pre-night firing (the dead-man's next firing is after completion and takes the "courier already
sent" branch), which is exactly the 2026-09-09 case. Lower bound (NOT EXECUTED, flagged for the arming magistrate): because
both agents are daily calendar triggers, installing before the previous day's t0 hour:minute would let the night agent fire a
day early; I did not trace how the driver treats a firing before t0 for the stub class, and the stub proceeds past gate
refusals, so the arming magistrate must either verify that guard at the bench or respect N2's lower bound.

## Q4 — Over-stated or unsupported lines in the packet

1. Charge, Q1 consideration: "the cost of NOT running it is that the first real night is also the first end-to-end exercise of
   the cured receipt path." Over-stated: a real night does not execute the cured stub branch; it executes the unchanged `else:`
   ladder (23b: byte-identical) plus the new log line. The first real night IS the first live run of the sidecar/digest ladder,
   but that was equally true before the cure and no stub night can change it.
2. Charge, Q1: "the unit tests cover the gate function but not the driver→gate→receipt→courier chain under launchd." Half
   supported: `test_stub_without_chain_files_logs_rehearsal_only` in `tests/test_run_night.py` covers driver→gate→receipt in
   process; only launchd and the courier are outside the tests, and both were live-exercised on 2026-09-09.
3. 21i line 59: "`launchctl list` before the uninstall showed `com.joulewise.night` last exit status 3 = `EXIT_REFUSED`,
   consistent with the refused receipt (06 N3)." Unsupported as an inference: run_night.py 1680–1683 sets `base_exit_code =
   EXIT_REFUSED` for EVERY `rehearsal_effective` night regardless of the receipt, so exit 3 is the stub's unconditional exit
   status and says nothing about the receipt. A second stub night with a clean receipt will also exit 3; harvest acceptance
   must not read exit 3 as a refusal signal.
4. P2/21i item 6: "MET, WITH A FINDING." Defensible only with the conditional it carries; as of this ruling the item is not
   MET until the combined night's receipt is harvested non-refused (Q1 consequences).
5. P3 status_note: "Item 5 … CANNOT be met by this night: installed 01:57 the same night." Supported.
6. P6 NIGHT_HANDBACK: "the cure is committed on branch … at `5db38b58` (PR #309) under review, not yet merged." Stale at
   7ca2908f (merged at a52810c9); P3's status_note is current. Not a defect of the packet, but the handback text should be
   reconciled before the next arm since D-175's procedure cites it.

## Verdict summary

- **Q1: (c).** A second REHEARSAL_STUB night is REQUIRED before any DIAGNOSTIC_NO_PACK plan, on the ground of the kernel's open
  acceptance item 5 (a rehearsal installed the morning before, pre-night dead-man observed standing down); the cure by itself
  would not have required one (its stub branch is off every real night's path, and the launchd→courier chain was live-proven on
  2026-09-09). The night must close items 5 and 6 together: receipt not refused (only `night_refused_agent_present` acceptable),
  dead-man stand-down line present.
- **Q2: yes**, the headless magistrate may arm it under D-175's eight conditions, email-then-arm, disposable `/private/tmp`
  checkout; added conditions N1–N6 (cured head pinned; install after the previous day's t0 hour:minute and before 07:00; fresh
  plan_id/root; powermode recorded not gated; explicit receipt/log acceptance; removal scope unchanged).
- **Q3:** item 1 closes by a located or re-measured `cold_start.json` with the deadline formula cited (desk work, never while
  armed); item 5 closes only by a night installed before 07:00 the morning before, with the stand-down log line and an empty
  pre-t0 `night/`.
- **Q4:** three over-statements (real night "exercises the cured path"; tests "do not cover the driver chain"; exit 3
  "consistent with the refused receipt") and one stale handback sentence, none of which changes the verdict.
- **NOT EXECUTED:** driver behaviour on a pre-t0 daily firing for the stub class; exhaustive search for an existing
  `cold_start.json` outside the repository.
