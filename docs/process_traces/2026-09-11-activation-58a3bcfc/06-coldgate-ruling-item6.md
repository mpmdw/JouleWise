# 06 — Cold-gate ruling: does item 6 still require a REHEARSAL_STUB night after the interpreter cure, before the equivalence night?

Judge: cold Fable seat (claude-fable-5-1), single non-interactive session, convened under rule 11 from packet
`05-coldgate-packet-item6-after-interpreter-cure.md`. Written 2026-09-11 14:23–14:35 UTC (07:23–07:35 PDT).
Working directory: linked worktree `/Users/edr/code/JouleWise-wt-coldgate-stub6` at `1dddcfea573d85ee8facebc2b50dac412cb3b69f`
(`git rev-parse HEAD`); `git status --short` showed only the untracked packet directory `docs/process_traces/2026-09-11-activation-58a3bcfc/`.

## 0. Contamination disclosure

**What the convening prompt told me** (before I read anything): that the trigger is "a proposed reinterpretation of a prior verdict";
the two trust-anchor digests; the list of files to read; the three options (a)/(b)/(c) and the packet's question Q; the instruction to
choose one, classify the un-exercised rows under D-161, list required evidence, draft Ed's paragraph, not amend kernel text, and
end with a one-line VERDICT. The prompt also said ending without this file existing is a protocol failure, which is why this ruling is
written with the Write tool. That is the one file this session creates; no other file was modified, no state-changing command ran.

**What the harness injected into my system prompt without my asking**, all of which I did not act on: the global `~/.claude/CLAUDE.md`
(multi-model orchestration pointers, a writing standard); this worktree's project `CLAUDE.md` (Codex bridge notes, a sentence about
`docs/agent_playbook.md` Mission M0); the auto-memory index `MEMORY.md` as one-line hooks. Those hooks are loop context and could bias
me; the ones touching this question say, in substance: a "Checkpoint 2026-09-11 courier" hook stating the 02:56 driver crashed on Python
3.9, the 07:00 dead-man refused on an orphaned Claude daemon pid 83102, and a planned sequence ending "interpreter cure → new stub
date"; hooks on Ed's directives about "no silly gates on accepting numbers", "docs are context, code is truth", a standing run mandate,
paper-first priorities, and issue #316's "night one = equivalence check". I also received a git-status snapshot with five recent commit
subjects (PR #320 review, a kernel lane CONTRACT-TEMPORAL-HEDGE-GUARD-01, traces 202–205). I did not open RUN_STATE.md, TASK_QUEUE.md,
CLAUDE.local.md, any council log, any skill, any memory file, or `docs/decision_log.md` beyond the D-161 entry. The "new stub date" hook
is the strongest potential bias toward option (a); I record that I noticed it and that my ruling below does not rest on it.

**Charter tension noted:** charter §4 says "DO NOT DO: modify any file"; the convening prompt requires writing this ruling file. I read
the charter's §8 ("Your final message is recorded verbatim in the tracked gate record") as making the ruling artifact itself the
permitted output; nothing else was written.

**Packet-forbidden material inside the packet:** F8 quotes "RUN_STATE T38g" ("Ed's standing direction = full autonomous science").
RUN_STATE is a narrative state document the charter forbids, and the quotation is not an enumerated exhibit with path, digest and line
range. I disregard that sentence. Ed's timing direction is on the record independently in record 146 (§"Timing"), which I did read.

## 1. Trust anchors (executed before reading the merits)

```
$ shasum -a 256 docs/process/coldgate_charter.md docs/process_traces/2026-09-11-activation-58a3bcfc/05-coldgate-packet-item6-after-interpreter-cure.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
44e914d7fc52e7ea8e7f6e2ef08bdf826f90728291ff4cd7ce51fe5f25e416b6  docs/process_traces/2026-09-11-activation-58a3bcfc/05-coldgate-packet-item6-after-interpreter-cure.md
```

Expected (from the convening prompt): charter `099de884…c95d81`, packet `44e914d7…5e416b6`. Observed: identical. Method: `shasum -a 256`
in the worktree at 14:18:40 UTC.

## 2. Probes executed (all foreground, read-only; nothing in the background; no subagent; no network; no launchctl; no `~/night-custody`)

P1. `python3` read of `docs/process/state_kernel.json` → `/tasks/NIGHT-REHEARSAL-01`. Item 6 verbatim: "After WATCHDOG-INSTALL-01, one
fresh REHEARSAL_STUB night fires through the night driver's own courier before any real plan is armed". Item 2 verbatim: "A
REHEARSAL_STUB result on a night-results branch produced by a launchd-started driver (not a shell-started one), with verdict
REHEARSAL_ONLY". Item 5 verbatim: "A rehearsal with the agents installed the MORNING BEFORE the armed night, so the pre-night 07:00
dead-man firing is observed standing down without writing anything but a log line (coldgate-d1 R-7 amendment)". The kernel file's last
commit is `524f8e35` (2026-09-11 01:18:57 −0700). The row's `status` is `blocked`; the pending dependency `REHEARSAL-20260911-HARVESTED`
reads "receipt not refused (item 6) … a night_refused_agent_present receipt closes item 5 only".

P2. Read in full: cold gate 61 (`docs/process_traces/2026-09-09-rehearsal-harvest/61-coldgate-ruling-second-stub-night.md`), synthesis 65,
records 01, 02, 03, 04 (seat report + `.status`), 146, 147, the 09-09 harvest record 21i, `docs/process/NIGHT_HANDBACK.md` (190 lines),
the runbook's §"What night one is for", §1.1, §1.3, §2.5 (`docs/phase_2/derivation_night_runbook.md` lines 93–125, 734–764, 1192–1208,
1594–1747), and the D-161 entry of `docs/decision_log.md` only (awk-bounded to the entry).

P3. Refuter 62's load-bearing probe reproduced on the 09-09 receipt byte copy
`docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/night-receipt.json`:

```
REFUSED reason=night_probe_error detail="FileNotFoundError: … '/Users/edr/night-custody/rehearsal-20260909/chain.zsh'"
C1 FAIL measured keys ['detail']
C2 NOT_APPLICABLE []
C3 FAIL ['agent_census_exit_code', 'agent_census_stdout']
C4 FAIL ['detail']
C5 FAIL ['authored_epoch_s', 'driver_checkout_head', 'measurement_checkout_head', 'measurement_root', 'observed_epoch_s', 'plan_measurement_head', 'plan_repo_head', 't0_epoch_s', 'window_max_s']
```

So on 09-09 the gate stopped at the C5 chain read; C3 holds only the census pair; C4 and C1 were never evaluated. 62's ground is verified
on primary evidence.

P4. Gate row order, `joulewise/night_gate.py` (read at lines 1030–1125 and 1255–1330): census → C5 chain/sidecar read (stub class skips
it since PR #309: `"chain_stub": "built_in_stub_by_design"`, line ~1050) → C3 tail (`hid_idle_raw` 1143, `ac_power_raw` 1161,
`pmset_g_raw` 1177, `load_average_raw` 1197, `thermal_raw`/`cpu_speed_limit` 1221–1234, then `rows["C3"].status = "PASS"` 1252) → C4
(`boot_session_uuid_raw`, `clock:epoch+monotonic`, 1255–1298) → C1 registration hash, gated by
`if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:` (line 1300). The rows are class-independent between the stub and the
equivalence class exactly as 62 said. `class_table()` (lines 437–448) requires C1/C3/C4/C5 PASS and C2 `NOT_APPLICABLE`/`no_pack_by_design`
for both classes.

P5. The 09-11 failure reproduced from the packet directory's byte copies (12/12 `SHA256SUMS` OK by `shasum -a 256 -c`):
`01-harvest-evidence/night/launchd.night.err` ends
`from datetime import UTC, datetime` / `ImportError: cannot import name 'UTC' from 'datetime' (/Library/Developer/CommandLineTools/…/3.9/lib/python3.9/datetime.py)`.
`01-harvest-evidence/night.log` is five lines: `2026-09-10T07:00:02.092553-07:00 dead-man fired before the night's completion epoch
1789121760; standing down`, then the 09-11 07:00 `dead-man starting courier`, two `durable record pushed branch=night-results/20260911`,
and `courier attempt=1 heartbeat=True sent=True`. No `night driver started` line, no `night gate verdict=` line: the run path never began.

P6. The defect itself, live on this host: `env -i PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/env python3 --version`
→ `Python 3.9.6`. `configs/launchd/com.joulewise.night.plist.template` line 10 is `<string>python3</string>` (still the old template).
`pyproject.toml:9` `requires-python = ">=3.11"`. `joulewise/arm_readiness.py:26` `from datetime import UTC, datetime`.
`scripts/run_night.py:1416` `from joulewise import arm_readiness as readiness` is the first line of `run_night()`, before the census at 1418.

P7. State of the cure lane at my probe: `git branch --list fix/2026-09-11-night-interpreter-pin` exists; `git log -1` on it is
`1dddcfea` = main. **No commit exists on the cure branch.** Record 04's envelope: `"status": "blocked"`, `"completion": "none"`,
flag F1 "The runner configured sandbox_mode=read-only … commits cannot be performed"; `.status`: `semantic_status=blocked completion=none`.
The packet's condition ("conditional on NIGHT-INTERPRETER-PIN-01 merging with its defect-shaped tests green") is therefore doing all the
work: as of 14:22 UTC nothing has been built.

P8. Installer constraints, `scripts/install_night_agent.sh`: `--hour` accepts 0–23 (line 28) and refuses only the dead-man hour
(lines 112–113: `refusing --hour $hour: it is the dead-man hour (DEADMAN_HOUR=$deadman_hour)`). Plan parsing, the DEADMAN lookup and
rendering all run `/usr/bin/python3` today (lines 44, 106, 110, 136) — the same 3.9 interpreter; record 03 §2 moves them.

P9. Driver timing guards, `scripts/run_night.py`: `_next_deadman_epoch` (945), `_completion_epoch_s = t0 + window_max_s + COURIER_DEADLINE_S`
(958–959), refusal `plan_overruns_deadman` if completion ≥ next dead-man (1463–1490); gate C5 refuses `night_window_expired` when now is
outside `[t0, t0 + window_max_s]` (`night_gate.py:977–984`). No guard names an hour of day. `_night_date` (538) names the results branch
from the plan's t0 in LOCAL time; `_durable_record` (541–598) clones origin depth-1, `checkout -B night-results/<date>` from that clone's
default branch, commits, and `push origin HEAD:<branch>` with `check=True`; failure is caught and logged `durable record failed: …`,
never fatal. Consequence (code-derived, NOT EXECUTED against the remote): a second plan whose t0 falls on local date 2026-09-11 would push
to `night-results/20260911`, which already holds this morning's dead-man commits (record 01: tip `37876416`), so that push would be a
non-fast-forward rejection and the log would carry a `durable record failed` line.

P10. `run_night.py` subcommands (1844–1865): `run`, `dead-man`, `rehearse`, `g7-control`; `rehearse` = `run_night(plan, rehearsal=True)`,
and line 1525–1531 refuses `rehearse` unless the plan's class is REHEARSAL_STUB; `rehearsal_effective = rehearsal or plan.receipt_class ==
"REHEARSAL_STUB"` (1545); the stub command is `["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]` (1575).

NOT EXECUTED: any `launchctl` call; `git ls-remote`; a read of the watchdog's code to confirm that its exit boundary and relaunch belt are
derived from the plan's `t0_epoch_s` rather than fixed at 02:56 (the handback states them per plan — "02:31:00 PDT on 09-11 … t0 − 25
minutes" — but I did not verify the derivation in code); the equivalence night's other gates (powermode, sudo) which are outside this
packet; the unit suite (the cure does not exist to test).

## 3. What 65's verdict was, and what stands of its grounds

Synthesis 65, lines 3–6: "Both seats rule (c): a second REHEARSAL_STUB night is REQUIRED, combined so that it also closes 21i acceptance
item 5 … The ground is item 5 and the un-exercised class-independent gate rows (refuter 62: the 09-09 gate returned at the C5 chain read,
so C1/C4 and the tail of C3 never ran live), not the cure's own branch". Cold gate 61 line 48–49: "The requirement rests on the kernel's
unmet acceptance item 5, not on the cure; on the cure alone the answer would be (b)." Line 81: "Item 6 stays 'MET WITH A FINDING, cure
merged' until the combined night's receipt is harvested non-refused".

Ground G1 (item 5). Record 01 §"Acceptance disposition" rules item 5 MET under cold gate 31's predicate P1–P4 with addendum A4, and the
byte copy of `night.log` (P5) carries the stand-down line `2026-09-10T07:00:02.092553-07:00 dead-man fired before the night's completion
epoch 1789121760; standing down` as the first line, preceding everything the 09-11 dead-man wrote. I do not re-litigate cold gate 31.
G1 is DISCHARGED by evidence that exists on disk today. It no longer requires any night.

Ground G2 (un-exercised C1/C4/C3-tail rows). Verified live on the 09-09 receipt (P3) and in the gate's row order (P4). Since PR #309 no
launchd-started driver has reached those rows: the 09-11 driver died at its first import (P5, P6). G2 STANDS, exactly as issued.

Charter §9 binds me: "A prior governed verdict remains as issued and must not be converted into its opposite by reinterpretation." What
changed since 65 is a fact (item 5 became MET), not an interpretation; a ruling that G1 is discharged is not a reversal. A ruling that G2
is discharged by desk evidence would be a reversal, because 62 (line 33–38, 76–85, 113) located G2 precisely in what "the cure did not"
and tests cannot reach: the real `Probes` adapter under launchd for HID/AC/display/load/thermal, `sysctl kern.bootsessionuuid`, and the
registration read.

## 4. The three options against the two grounds

### (a) Another REHEARSAL_STUB night, day-before install span, t0 09-13 02:56 — discharges G1 (already) and G2

Discharges G2 by executing C3-tail, C4 and C1 under the launchd-started driver on the cured head with the real probe adapter, producing
a receipt whose rows carry the measured keys P4 names. It additionally exercises the ONE thing no option can otherwise exercise live: the
cured plist's own executable line under launchd (record 03 §1 replaces `/usr/bin/env` + `python3` with an absolute `@@PYTHON@@`; the 09-09
firing ran the old template). No reading of any text is needed. Cost: the equivalence night moves to 09-14 (packet F7 arithmetic, which I
checked against §1.3's "Install BOTH agents on the calendar day BEFORE t0, between 03:00 and 06:30 local").

### (b) The equivalence night itself at t0 09-13 02:56 on desk evidence — discharges G1; does NOT discharge G2; REJECT

Desk `preflight` (record 03 §3) "imports … every project module that the run, dead-man and rehearse paths import lazily … parses the plan"
and "must NOT touch the custody root, the census, launchctl, or the network". It runs no gate row. `--render-only` renders two plists. Neither
evaluates C3-tail/C4/C1 with the real adapter. So (b) leaves G2 undischarged and is a waiver of 62's ground, which charter §9 forbids me to
grant by reinterpretation. Two further defects in (b) as the packet frames it:

1. Its premise "the launchd-started 09-09 firing (F2) as sufficient proof that the launchd path works" is false after the cure: the cure
   changes the very ProgramArguments launchd executes (record 03 §1) and the installer's own interpreter (§2). Under (b) the first plan ever
   started by the cured job file would be the real one. The 09-11 crash is the worked example of a desk check that did not reproduce the
   launchd runtime (`/usr/bin/env python3` under the plist's PATH, P6); (b) proposes to trust a new desk check of the same kind.
2. Its calendar case is weak on its own terms: (b) gains one day only if the never-fired path works; if it does not, the equivalence night is
   lost at t0 (as on 09-11), the stage-1 email and arm ceremony are spent, and the equivalence night lands no earlier than under (a).

Classification: the guard (b) would drop is a MISTAKE guard (§5). D-161 keeps mistake guards fail-closed; it retires "deliberate-only
guards". (b) is therefore not licensed by D-161 either.

### (c) A REHEARSAL_STUB night at an off-convention t0, harvested before the 09-12 install span — discharges G1 (already) and G2 — CHOSEN, with (a) as the automatic fallback

The packet's F7 assumes every stub night must use the day-before 03:00–06:30 install span. That span exists for two purposes: item 5's
pre-night dead-man observation (61 N2's upper bound "strictly before 07:00") and the day-early-firing guard (61 N2's lower bound "after that
day's t0 hour:minute has passed"). With item 5 MET, only the lower bound still serves a purpose for a stub. Runbook §1.3 is written for "The
equivalence night's arm" (§1 heading), not for stubs. The kernel's item 6 names no install span and no hour. The installer accepts any hour but 7
(P8); the driver's only timing guards are the dead-man arithmetic and the C5 window check (P9). So a stub night can be installed today and
fire in the first hour of 2026-09-12 local, be harvested and retired, and still precede the equivalence night's install at 03:00–06:30 on 09-12.

**Why not a daytime t0 today, as the packet's (c) example suggests:** `_night_date` names the results branch from t0's local date (P9);
a t0 on 09-11 collides with the existing `night-results/20260911` and the push would fail non-fast-forward, leaving a `durable record failed`
log line that the harvest could not distinguish from a real push defect without network probes. A t0 after 00:00 PDT on 09-12 yields
`night-results/20260912`, which does not exist. It also removes any argument about the word "night".

**(c) as ruled — a reading, not an amendment; Ed may veto it with one word:**

Reading R1: kernel item 6's "one fresh REHEARSAL_STUB night" is satisfied by any REHEARSAL_STUB plan executed by the launchd-started driver
through its own courier on a head at or after the cure merge, whatever its `t0_epoch_s`; the day-before 03:00–06:30 install span is 61 N2's
pin for the item-5 night and runbook §1.3's rule for the real plan, and neither binds a stub once item 5 is MET. The lower bound of 61 N2
(install only after the chosen hour:minute of the install day has already passed, so the first daily firing IS t0) is retained.

Conditions (each is evidence the arm record or harvest record must carry; a missing one falls back to (a) with no further gate):

C-1. Cure merged: NIGHT-INTERPRETER-PIN-01 on main at a named head H′, PR number recorded, CI green, and the defect-shaped tests of record 03
§5 (a)–(h) present and passing: `python3 -m unittest tests.test_install_night_agent tests.test_run_night` rc 0 on H′ pasted. (Today the branch
holds no commit — P7.)
C-2. Stub clone at H′ with a `.venv` whose `bin/python` reports ≥ 3.11; `install_night_agent.sh --render-only` from that clone: rendered
`ProgramArguments[0]` is that absolute path, no element equals `/usr/bin/env` or `python3`, and the preflight JSON line `{"preflight": "ok",
"python": …, "version": …, "modules": […]}` produced under `env -i PATH=<the plist's exact PATH> HOME=$HOME` is pasted in the arm record.
C-3. Orphan cleared before install: the census `/usr/bin/pgrep -lf 'codex|claude|t3'` exits 1 with empty stdout immediately before the
install (D-175 condition 8), and pid 83102's tree is absent. This is Ed-external (record 01 F2) and bounds every option.
C-4. Plan: fresh `plan_id` (never `rehearsal-20260911`), fresh custody root under `~/night-custody`, fresh disposable checkout path (61 N3);
class REHEARSAL_STUB; `t0_epoch_s` in [1789196400, 1789200000] = 2026-09-12 00:00–01:00 PDT; `window_max_s` 900 (completion ≤ 01:20 PDT,
well before the 07:00 dead-man — `plan_overruns_deadman` cannot fire); `authored_epoch_s` within 36 h of t0. Email-then-arm per D-175 condition 1
and the NIGHT_HANDBACK notice, rewritten for this plan (handback §Purpose currently describes `rehearsal-20260911`, which is retired — record 02).
C-5. Install from the stub clone on 2026-09-11 local, at a wall-clock time after 07:00 PDT and after the chosen hour:minute has passed
(trivially true for hour 0), with `--hour 0 --minute M`; install epoch recorded; `night/` baseline recorded (it must be empty).
C-6. The arming activation exits by t0 − 25 min and the watchdog's fence for THIS t0 is verified from the watchdog's code to be derived from
the plan's `t0_epoch_s` (NOT EXECUTED by me). If the watchdog's exit boundary or relaunch belt is fixed at the 02:56 convention, (c) is not
available and (a) applies.
C-7. Harvest (checklist 13) shows ALL of: `night/receipt.json` verdict `REHEARSAL_ONLY`; C1 PASS with `registration_sha256` measured; C2
`NOT_APPLICABLE` basis `no_pack_by_design`; C3 PASS with measured `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`, `load_average_raw`,
`thermal_raw` (and `cpu_speed_limit` when present); C4 PASS with the boot-UUID/clock measured pair; C5 PASS with `chain_stub:
built_in_stub_by_design`, `chain_sha256: null`, `expected_chain_sha256: null`; `night/result.json` verdict `REHEARSAL_ONLY`, `chain_exit_code` 0;
`launchd.night.err` EMPTY (the 09-11 traceback signature absent); `night.log` carrying `night driver started`, a `night gate verdict=` line
whose verdict is not REFUSED, `durable record pushed branch=night-results/20260912`, and `courier attempt=1 … sent=True`; `courier.sent`
message id, read back in the inbox; launchd last-exit 3 is the stub's unconditional status and not a refusal (61 Q4.3).
C-8. Uninstall from the stub clone, clone removal and plan-root removal complete, `launchctl list` free of `com.joulewise.night*`, and
`find ~/night-custody -maxdepth 2 -name night_plan.json` empty — all BEFORE the equivalence night's install begins at 03:00 PDT 09-12.
C-9. Fallback: if any of C-1…C-8 is not on disk by 02:30 PDT 09-12, or Ed vetoes R1, route (a) applies without another gate: install
09-12 03:00–06:30, stub t0 09-13 02:56, equivalence night earliest 09-14 02:56. A receipt refusing `night_refused_not_quiet`,
`night_refused_hid_idle` or `night_refused_agent_present` on the (c) attempt is a CORRECT refusal (the rows ran live and refused), not a
finding — it discharges nothing for item 6 and (a) follows. Any `night_probe_error`, crash, non-empty `launchd.night.err`, or refusal of any
other kind IS a finding to cure before any plan, under (a) or (c).

What (c) discharges and how: G1 — already discharged by record 01; (c) adds nothing and needs nothing (its 07:00 dead-man never fires
because the agents are gone by C-8; if C-8 slips past 07:00 the dead-man takes the `courier already sent` branch, `run_night.py:1738`,
harmless). G2 — discharged by C-7's rows PASS with measured keys under the launchd-started driver on the cured head, plus the cured plist's
executable line fired by launchd for the first time. The equivalence night is then armed 09-12 03:00–06:30 for t0 09-13 02:56.

## 5. Classification of the un-exercised rows under D-161

D-161's operative text (`docs/decision_log.md`, entry D-161): "the operative test is MISTAKE vs DELIBERATE (fail-closed for physics/evidence,
pre-registration and operator mistakes; deliberate-only guards retire)".

- C3 tail (HID idle, AC power, display sleep, load average, thermal limit), C4 (boot-session UUID + epoch/monotonic pair) and C1 (registration
  hash) ARE, on the real night, physics/evidence fences: C3 establishes the quiet-machine state the acceptance's envelope assumes, C4 that the
  clock and boot session are coherent for the samples' anchors, C1 that the night runs against the committed pre-registration. They stay
  fail-closed and none of the three options touches them.
- The REQUIREMENT that those rows be exercised live on a stub before the first real plan is a PROCESS fence of the MISTAKE class: an
  un-exercised row can fail only closed (a probe error or crash refuses the night; `night_gate.py` lines 1143–1330 return `_probe_refusal` or
  a named refusal), so its failure mode is a lost night, not a wrong number. A green stub on a quiet machine cannot detect a false PASS in
  those rows; only defect-shaped tests can. D-161 keeps mistake guards ("operator mistakes" are in its fail-closed list) and retires only
  guards against a deliberate adversary; so this guard is not retired, but D-161 says nothing about its SHAPE, and the cheapest shape that
  exercises the rows live suffices. That is why (c) is admissible and (b) is not.
- Item 5 is likewise a process/mistake fence (a pre-night dead-man writing into `night/` would make the real t0 refuse as a rerun via
  `_existing_record`, `run_night.py:1432`); it is MET.

## 6. Packet hygiene (charter §6)

H1. F8's RUN_STATE quotation is forbidden narrative material (disclosed in §0). Effect on Q: none; Ed's timing direction is in record 146.
H2. F4 says "the seat is running"; the branch holds no commit and record 04 returned `blocked`/`none` (P7). The packet should have said the
first seat attempt produced nothing. Effect: the conditional on which every option rests is heavier than the packet presents; C-1 makes it explicit.
H3. F7 treats the day-before 03:00–06:30 install span as intrinsic to any stub night (asymmetric treatment of alternatives). It is not (§4(c)).
This is the defect that makes (a) look like the only stub-shaped route.
H4. Option (b)'s framing embeds an unlabeled false premise: the 09-09 firing "proof that the launchd path works" is proof about a job file
the cure deletes. Effect: (b) is weaker than presented; it is rejected on G2 regardless.
H5. F6's "It IS a real plan in the sense of item 6" is a conclusion labeled as fact; I concur on the merits (DIAGNOSTIC_NO_PACK takes real
`powermetrics` samples; kernel item 4 treats it as the first plan needing the stage-1 email), so no effect.
H6. F3's "No gate row C1–C5 was exercised on this night either" — verified (P5).

## 7. Exact evidence required before the equivalence night may be armed (chosen route)

Under (c): C-1 through C-8 above, each on disk and cited by path in the arm record and harvest record, plus Ed's non-veto of R1 on the notice
thread. Under the fallback (a): C-1, C-2, C-3, then 61's N1–N6 and 65's pins re-issued for a fresh plan id at t0 09-13 02:56 (install 09-12
03:00–06:30), harvested to the same C-7 receipt criteria and retired per C-8 before the equivalence night's install on 09-13. Under either
route, kernel items 4 (stage-1 email before arming a DIAGNOSTIC_NO_PACK plan) and the runbook's §0 desk checks remain owed and are not this
packet's question.

## 8. Paragraph for the magistrate to send Ed

> Ed — one decision, one word if you like. Last night's dry run of the measurement machinery never started: macOS's job scheduler
> (launchd) started our night driver with the wrong Python (an old 3.9 build the scheduler finds first on its path), and the driver crashed on
> its first import. We are fixing that so the job file names the exact Python it must use and the installer test-imports everything under
> that Python before it installs. Before the real "equivalence night" (the one measurement night that checks whether the OS update moved
> the instrument), the rules on file still require one more dry run through the scheduler: the driver's machine checks (idle, power, load,
> thermal, boot clock, pre-registration hash) have never run live from the scheduler since the last fix, and last night they never ran at
> all. The fastest honest way to do that is a dry run tonight at about 00:30 Saturday morning (Sept 12), installed this evening, harvested
> and removed before 03:00, so the real night can be installed Saturday morning and fire at 02:56 on Sunday Sept 13. The only thing you
> must do for any of this: kill the orphaned Claude background process (pid 83102 and its children) — every night check refuses while it is
> alive. If you prefer the usual timetable (dry run Sunday 02:56, real night Monday 02:56), reply NO and we do that instead. Silence means
> tonight's plan goes ahead.

## 9. Severity-tiered findings

- BLOCKER (independent of the ruling): the orphan daemon tree pid 83102 (record 01 F2, record 02) refuses every census; no option can fire
  until it is gone. Ed-external.
- BLOCKER (conditional): the cure branch holds no commit (P7); every option is conditional on C-1.
- MATERIAL: any stub t0 on local date 2026-09-11 collides with the existing `night-results/20260911` branch and would log `durable record
  failed` (P9, code-derived). (c) is therefore restricted to t0 ≥ 00:00 PDT 09-12.
- MATERIAL: the handback's §Purpose/§Where/§Next lane still describe the retired `rehearsal-20260911` and must be rewritten before any arm
  (R-9, handback lines 4–8), and the handback line 167–169 ("the driver, chain, and preflight always derive `<measurement_root>/.venv/bin/python`")
  is the CHAIN interpreter, not the driver's, as record 03 §"Two facts" says; the cure's doc clause (§6) must not leave that sentence implying
  the driver was already pinned.
- NIT: 61's item-6 phrasing ("MET WITH A FINDING, cure merged") and the kernel status_note's "item 6 MET conditional on the cure landing" are
  both superseded by record 01's "Item 6 — NOT MET"; the kernel status_note should carry the 09-11 disposition once this ruling is synthesized.

## 10. Verdict summary

- Q: **(c)**, as a reading (R1) with conditions C-1…C-9 and automatic fallback to (a); **(b) REJECTED** (does not discharge 62's ground; its
  launchd premise is false after the cure; not licensed by D-161, which keeps mistake guards).
- G1 (item 5): discharged already by record 01; none of the options needs to touch it.
- G2 (un-exercised C1/C4/C3-tail): discharged only by a launchd-started REHEARSAL_STUB run on the cured head whose receipt shows those rows
  PASS with measured values — (a) or (c); never (b).
- Classification: the rows are physics/evidence fences on the real night; the stub-first requirement is a process fence of the mistake
  class, kept by D-161, whose shape is free.
- NOT EXECUTED: launchctl, ls-remote, the watchdog's t0-derivation (C-6), the equivalence night's other gates.

VERDICT: (c) — a REHEARSAL_STUB night with t0 in 2026-09-12 00:00–01:00 PDT (epoch 1789196400–1789200000), harvested green and retired before 02:30 PDT 09-12; earliest equivalence-night t0 it permits = 2026-09-13 02:56:00 PDT (epoch 1789293360); fallback (a) → 2026-09-14 02:56:00 PDT.
