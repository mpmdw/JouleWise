# 06 — REFUTER (CONTRACT lens, Opus, read-only): PR #308 @ 20f95848d5975947dbc5bb1c295e56cb58bb534f

Head reviewed: `20f95848d5975947dbc5bb1c295e56cb58bb534f` (detached worktree `/Users/edr/code/JouleWise-wt-ref-308-astra`), diff scope
`git diff --stat main...HEAD` = 30 files, docs and byte artifacts only, no code.

**Head warning (read first).** The live PR #308 head on GitHub is `1f4c4492f6956886979c06b9e2a627de5296eb87` — a CHILD of the head I was
briefed on ("PR #308 fix round 1 (fidelity refuter 05): force-add the three ignored `*.log` harvest copies (17/17 SHA256SUMS verify);
arm census wording; acceptance item 3 → PARTIAL; NIGHT_HANDBACK dated reconciliation"). This review is written against 20f95848 as
briefed; each finding below carries a `Status at 1f4c4492:` line so no fix round is spent twice.

Governing texts read at this head: `docs/process/NIGHT_HANDBACK.md` (whole file, 153 lines); `docs/process/MAGISTRATE_WATCHDOG.md`
(§Safety model, §Plan fence and stand-down ladder, line 102 relaunched-session limits, lines 316–325 rehearsal-checkout and
arming rules); `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` (all 23 lines, esp. 7, 8, 11–13, 19, 20, 22, 23);
`docs/process/state_kernel.json` `/tasks/NIGHT-REHEARSAL-01` (goal, acceptance, dependencies, fences, status_note);
`docs/decision_log.md:11138–11162` (D-175) and its synthesis of record
`docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md` (eight conditions,
lines 35–52); `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md` (relaunch-prompt rules and the four new sections);
`docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md` (arm-email timeline, blocks A/B, conditions map).
Artifacts read byte-for-byte: every file under `21b-rehearsal-20260909-bench/arm-*` and `.../night-harvest/`. Executed this session
(read-only, in the review worktree): `shasum -a 256 -c SHA256SUMS`; `git check-ignore -v`; `git ls-remote origin 'refs/heads/night-results/*'`;
`git fetch --no-write-fetch-head origin refs/heads/night-results/20260909` + `git ls-tree -r a84e0f7f`; `sed -n` reads of
`joulewise/night_gate.py`, `scripts/run_night.py`, `tests/test_night_gate.py`; `gh pr view 308`.

---

## BLOCKER

### B1 — Three artifacts that 21i cites are not in the commit, and at this head exist nowhere in the repository

(a) PR quote — `21i-rehearsal-20260909-harvest-record.md:4-5`:
> "Every fact below is read from a captured artifact under `21b-rehearsal-20260909-bench/night-harvest/` (byte copies of the custody
> root, `SHA256SUMS` alongside); nothing is restated from memory."

and `21i:10-12` ("`night.log`: driver started 02:56:00.988; … courier attempt 1 heartbeat+sent 02:57:33; second push 02:57:35.") and
`21i:14-15` ("`night-chain.stdout.log` `REHEARSAL`").

Executed evidence: `SHA256SUMS` lists 17 files; `git ls-files .../night-harvest/` returns 14 of them plus `uninstall-output.txt` and
`removal-output.txt`. `shasum -a 256 -c SHA256SUMS` in the review worktree: 14 OK, and
`night.log`, `night-chain.stdout.log`, `night-chain.stderr.log` = "No such file or directory / FAILED open or read".
Root cause: `git check-ignore -v` returns `.gitignore:45: docs/process_traces/**/*.log` for all three. The custody root was removed at
`removal-output.txt:12-13` ("plan root removed rc=0", 03:37:38 PDT), and the pushed record does not carry them either:
`git ls-tree -r a84e0f7f | grep night-results/20260909` yields nine files — `censuses.jsonl`, `chain.exited`, `chain.started`,
`courier.attempts.jsonl`, `courier.heartbeat`, `courier.json`, `courier.sent`, `receipt.json`, `result.json` — and no `*.log`.

(b) Governing text — `docs/process/NIGHT_HANDBACK.md:83-85` (§Where the results are):
> "- Driver log: `/Users/edr/night-custody/rehearsal-20260909/night.log` (and the dead-man stand-down line if the 2026-09-08 07:00
>   firing preceded the night)."

and `NIGHT_HANDBACK.md:91-98` (§Next lane): the magistrate "harvests `result.json`, the receipt or refusal, the courier message id and
the results-branch evidence, records them under `NIGHT-REHEARSAL-01`, then runs … `--uninstall` …, removes the stub checkout … and the
plan root". Harvest precedes removal; at this head the harvest is incomplete and the removal is irreversible.

(c) Correction: `git add -f` the three `*.log` copies (or relocate them to a non-`.log` name), re-verify 17/17, and amend `21i:4-5` to
record that the ignore rule required a forced add.

Status at `1f4c4492`: CURED — the three files are force-added and `21i:4-5` now names the ignore rule (verified by `git show --stat 1f4c4492`).

---

## SHOULD-FIX

### S1 — The night is recorded in trace prose only; `/tasks/NIGHT-REHEARSAL-01` is untouched and the cure lane is unregistered

(a) PR quote — `21i:59-63` ("## Next exact actions (this activation, in order) 1. NIGHT-GATE-STUB-CHAIN-01: seat in a linked worktree
off main … 2. Complete PR #308's twelve-row gate ledger … 3. CLONE-READINESS-01 …"). Nothing in the 30-file diff touches
`docs/process/state_kernel.json`. At this head that row still reads: `status_note` = "Remains blocked pending the fresh post-watchdog
REHEARSAL_STUB night; rehearsal-20260909 is prepared for 2026-09-09 02:56 PDT on activation branch 1ae91b4d, trace 21b", and
`dependencies[0]` = `{target: POST-WATCHDOG-REHEARSAL-20260909, state: "pending", evidence: null}`. `grep -c NIGHT-GATE-STUB-CHAIN-01
docs/process/state_kernel.json TASK_QUEUE.md` = 0 and 0.

(b) Governing text — `NIGHT_HANDBACK.md:94-95`: "records them under `NIGHT-REHEARSAL-01`"; and the kernel's own acceptance pointer
`/tasks/NIGHT-REHEARSAL-01/acceptance/pointer` naming `docs/process/state_kernel.json` as the home of that acceptance.

(c) Correction: in the ledger commit, set the row's `dependencies[0].evidence` to `21i` (state `satisfied_with_finding` or equivalent),
replace the "prepared for 2026-09-09 … activation branch 1ae91b4d" status_note with the executed facts, register
NIGHT-GATE-STUB-CHAIN-01, and state in `21i:59-63` that acceptance items 4 and 5 cannot be met by this night, so the row cannot close.

Status at `1f4c4492`: OPEN (`git show --stat 1f4c4492` touches no kernel file).

### S2 — D-175 condition 8 governs removal of this plan and is neither satisfied nor addressed

(a) PR quote — `21i:39-45`, heading and body:
> "## Documented post-completion uninstall (this session; allowed by the relaunch prompt)"
> "- `removal-output.txt`: … `git worktree remove --force` of the stub checkout rc 0, `worktree prune`; plan root
>   `/Users/edr/night-custody/rehearsal-20260909` removed after the byte harvest."

The only authority cited is "the relaunch prompt". No pre-removal agent census and no pre-removal notice to Ed is recorded in `21i`,
`pre-uninstall-observations.txt` (which captures launchctl, plists, HEAD, `ls-remote` and `state.json` — no census), or `removal-output.txt`.

(b) Governing text — D-175's synthesis of record, `13-magistrate-synthesis.md:51-52`:
> "8. Re-arm or **removal** of THIS plan by a later headless session follows (2)-(5) again; every other plan, record, lock, request,
>    event and `state.json` stays barred."

Conditions (2)–(5) include the arm email naming the pins before the action and a census re-run immediately before it
(`13-magistrate-synthesis.md:38-47`). Relaunch-prompt line 19 clause (b) ("the documented uninstall after a plan's completion") plausibly
governs instead, but the record never says which text it acted under, and choosing between them is an interpretation of a cold-gate
ruling's scope — reserved by rule 11 / relaunch prompt line 20.

(c) Correction: add one line to `21i:39` naming the authority actually relied on (relaunch prompt line 19(b) + `NIGHT_HANDBACK.md:96-98`)
and stating that D-175 cond. 8's arm-shaped (2)–(5) were not re-run because the plan had completed — or refer the scope question to the cold gate.

Status at `1f4c4492`: OPEN.

### S3 — The two PR documents give two different courier PIDs

(a) PR quote — `21i:20-21`: "Courier: `night-courier.sent` message id `1a08599a4ff4d005` … courier pid 82210" versus
`00-DURABLE-STATE.md:654-655`: "`notice_pending` carried `transition-20-hold_census` (the night courier, **pid 82106**, counted by the
production census inside the plan span; FENCED→HOLD_CENSUS→FENCED)."

(b) Governing text — the harvested bytes are decisive: `night-courier.heartbeat` = `pid=82210`, `night-courier.sent` = `courier_pid=82210`,
`night-courier.finding.md:1` = "written by the night courier, pid 82210". `NIGHT_HANDBACK.md:16-17`: "If this file and the result record
disagree, the result record is right and the courier says so." No artifact in the PR mentions 82106.

(c) Correction: change `00-DURABLE-STATE.md:655` to 82210, or name what 82106 is and cite the artifact that shows it.

Status at `1f4c4492`: OPEN.

### S4 — Watchdog transition/sequence claims have no captured source in the PR

(a) PR quote — `21i:3-4` ("pid 82637, watchdog attempt 5, spawned 03:33:01 PDT, **events.jsonl seq 22–23**"), `21i:23-25`
("transition seq 20 FENCED→HOLD_CENSUS (1788947872) → seq 21 back to FENCED (1788948174)"), and the same shape at
`00-DURABLE-STATE.md:627, 644, 646` (seq 12, 16, and 8844a3d0's "clean exit at 1788945287 (seq 13)"), all under `21i:5` "nothing is
restated from memory". The only watchdog artifacts committed are two `state.json` copies (`arm-launchctl-and-state.txt`,
`transition_seq` 8; `pre-uninstall-observations.txt`, `transition_seq` 23). No `events.jsonl` excerpt is in the PR.

(b) Governing text — relaunch prompt line 19 bars only writing, moving or deleting `events.jsonl`; reading and copying it is permitted,
so the evidence was available. `NIGHT_HANDBACK.md:16-17` (records over prose) and `21i:5`'s own standard apply.

(c) Correction: commit a read-only excerpt of the relevant `events.jsonl` lines, or mark those sentences as "read at the time, not captured".

Status at `1f4c4492`: OPEN.

### S5 — At this head `NIGHT_HANDBACK.md` still presents rehearsal-20260909 as an upcoming armed night and names a different measurement root

(a) PR quote — `21i:44-45`: "`/Users/edr/night-custody` now holds `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1`
only. Nothing is armed." and `21h:14`: "Frozen triple for the next relaunch prompt: (`rehearsal-20260909`,
`/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`)."

(b) Governing text — `NIGHT_HANDBACK.md:59-62` at this head: "`measurement_root` is a disposable detached checkout of this commit at
`/private/tmp/JouleWise-rehearsal-20260909-<sha>`"; `:44-47`: "Cut rehearsal checkouts as `JouleWise-rehearsal-<date>-<sha>`; the
reviewed `JouleWise-rehearsal-` prefix is exact and case-sensitive" (same rule at `MAGISTRATE_WATCHDOG.md:316-320`); `:78-82`
(§Where the results are) still points at the custody root deleted at 03:37:38; and `:6-8`: "Between nights the sections hold the
standing template text, so a courier that reads this file on a night nobody armed reports exactly that."
Note for the record: the armed lowercase path is the one D-175's synthesis names verbatim (`13-magistrate-synthesis.md:40-41`,
"run FROM `/private/tmp/joulewise-rehearsal-20260909-checkout` at ae8f074f"), and it is what `ae8f074f` itself wrote into the handback;
the `JouleWise-…-<sha>` text was introduced later by `c16a2ac4` (D-176 census cure) over the night-specific paragraph. The arm is
authorised; the governing file on main is what disagrees with it, and neither 21h nor 21i reconciles that.

(c) Correction: a dated reconciliation section in `NIGHT_HANDBACK.md` recording the executed triple, the harvest/uninstall/removal, and
"nothing armed", leaving the standing rules untouched.

Status at `1f4c4492`: CURED — `1f4c4492` adds "## Executed — reconciliation dated 2026-09-09 (activation 628c2eed; harvest record 21i)",
which explicitly notes "the checkout name differs from the `JouleWise-rehearsal-20260909-<sha>` example above".

---

## NIT

- **N1** `21h:10` records only the NO check ("Step 5: NO check on thread `1a0800cdb282c3f1` immediately before block B — six messages,
  all sent by the magistrate (Gmail ids in 21b)"). D-175 cond. 4 (`13-magistrate-synthesis.md:44-45`) turns on the arm email itself;
  its ids and times are in `21b:136-149` (`1a0800cdb282c3f1` 01:05:21, pins follow-up `1a08012045894ef7`, consolidated notice
  `1a080d1adf46c7b2` 04:40:20 on 09-08). Name them in 21h so the arm record discharges cond. 4 without a second document.
- **N2** `uninstall-output.txt:7-8` is "== custody root untouched?" / "17" — no command and no pre-uninstall baseline count, so
  "untouched" (restated at `21i:42`) is asserted rather than shown.
- **N3** `pre-uninstall-observations.txt:1` shows `-  3  com.joulewise.night`; `21i` never mentions the driver's exit status. It is
  `EXIT_REFUSED` (`scripts/run_night.py:61`), consistent with the receipt — one clause would close it.
- **N4** `SHA256SUMS` gives `night.log` = `28ee7ad6…` while `night-result.json:5-7` records `night.log` = `f894b3a4…`. The difference is
  the courier's post-result appends (02:57:33–02:57:35); `21i` does not say so, and a reader checking digests will stop here.
- **N5** `21h:17-18` and `NIGHT_HANDBACK.md:80` name `refusal.json` among the records to harvest; it does not exist, because
  `scripts/run_night.py:1541-1542` writes it only when `receipt.verdict != "GO" and not rehearsal_effective`. `21i` should say
  "absent by design" rather than silently omit it.
- **N6** `00-DURABLE-STATE.md:644-661`: activations 784a764e (1788944349, seq 9), 8844a3d0 (1788945287, seq 13) and 628c2eed have
  recorded exits or spawn epochs; b1e2fd2f has none, so "stand-down before the 02:31 PDT plan span" (commit subject `3faa9e3f` and the
  section heading) is asserted, not evidenced — even though `night-result.json:33-34` (`census_count` 1, `census_hits` []) independently
  proves no agent was alive at t0.
- **N7** No timestamped transcript exists for the byte-copy step itself (unlike `uninstall-output.txt` 03:36:58 and
  `removal-output.txt` 03:37:38), so "harvest before uninstall" is inferred from the copies' existence after the source was deleted.
- **N8** `21i:60-62` states the cure shape as settled ("skip the chain/sidecar read for `REHEARSAL_STUB`, record `chain_sha256: null`
  with basis `stub_by_design` in C5"). `night-courier.finding.md:23` does leave the choice to the magistrate, but the change alters what
  C5 carries for a receipt class fenced by `/tasks/NIGHT-REHEARSAL-01/fences` ("Receipt classes are honest…"), so the seat brief should
  put that fence in front of its review lenses.

---

## Checks that PASSED

1. **Email-then-arm order.** Arm email `1a0800cdb282c3f1` 2026-09-08 01:05:21 and pins follow-up `1a08012045894ef7` 01:10:59, with the
   consolidated post-fix notice `1a080d1adf46c7b2` 04:40:20 (`21b:136-149`, `21b:42`), all precede the `os.replace` at 01:57:32
   (`arm-blockB-output.txt:1,8`). D-175 cond. 4 satisfied; `NIGHT_HANDBACK.md:64-66` satisfied.
2. **No NO when the move began.** `21h:10` and `arm-blockB-output.txt:2` — thread checked immediately before block B, six messages, all
   magistrate-sent. Fence `/tasks/NIGHT-REHEARSAL-01/fences[0]` honoured.
3. **Cond. 5 census.** `arm-blockB-output.txt:3-7`: "foreign agent sessions (cond. 5, must be empty): []", informational []; the
   session's own codex MCP pair 83123/83143 listed and explicitly non-gating. `arm-step3b-output.txt:10-12` retires the leaked 09-04
   test pid 58633 with its argv preserved (`pass3-pid58633-argv.txt`).
4. **Staging outside the watchdog glob, render-only validation, atomic move** (D-175 cond. 2): `arm-blockA-output.txt:5-10` —
   staged at `/private/tmp/joulewise-rehearsal-20260909-staging/night_plan.json`, twin at `…-validate/`, both plists `plutil` OK,
   differing fields exactly `['chain_path','chain_sha256_path','custody_root']`; `arm-blockB-output.txt:8` "moved …/night_plan.json";
   `:178` staging and scratch gone.
5. **Both agents installed FROM the measurement root at the measurement head** (`NIGHT_HANDBACK.md:102-105`): `arm-blockB-output.txt:19,27`
   and `:96,104` — program argv and working directory both `/private/tmp/joulewise-rehearsal-20260909-checkout`; `:163` validated pins
   `repo_head = measurement_head = ae8f074f`, matching `arm-night_plan.json` byte-for-byte.
6. **Hour/minute equal to t0 local** (D-175 cond. 3): `arm-blockB-output.txt:59-60` Hour 2 / Minute 56 for `com.joulewise.night`, Hour 7 /
   Minute 0 for the dead-man; `t0_epoch_s` 1788947760 = 02:56:00 PDT.
7. **Custody root held no prior record**: `arm-blockB-output.txt:172-177` — `night/` empty, plan file mode `-rw-------`.
8. **Frozen triple** recorded identically in `21h:14`, `00-DURABLE-STATE.md:611`, and the live watchdog state
   (`arm-launchctl-and-state.txt:19-23`), and reduced to the canonical repo alone after completion
   (`pre-uninstall-observations.txt:20-26`). D-175 cond. 7 and `MAGISTRATE_WATCHDOG.md:102` satisfied.
9. **Pin reachability** (D-175 cond. 6): `git merge-base --is-ancestor ae8f074f main` = true in this worktree — ae8f074f was reachable
   from main for the whole armed period and remains so after removal.
10. **Exit by t0 − 25 min** (relaunch prompt line 12; D-175 cond. 7): obligation stated at `21h:26`, and
    `00-DURABLE-STATE.md:645` records 784a764e's clean exit at 1788944349 (01:59:09 PDT), 32 minutes early.
11. **The two pre-window relaunches did no work and decided nothing reserved.** `00-DURABLE-STATE.md:627-642` and `:644-661`: heartbeat,
    launch email, `notice.ack` (the only interfaces relaunch prompt line 19 permits), no Codex child, no new lane, read-only disk
    verification, and the plan-aware-launch-fence question routed to "the cold gate or Ed, not to this activation" (`:656-657`) —
    rule 11 and relaunch prompt line 20 honoured.
12. **Harvest → uninstall → removal order, with removal gated on the pushed branch** (`NIGHT_HANDBACK.md:91-98`): byte copies exist for a
    root deleted later; `pre-uninstall-observations.txt:9-11` `ls-remote` at 03:36:44 shows `night-results/20260909` = `a84e0f7f`;
    `uninstall-output.txt:1-2` at 03:36:58; `removal-output.txt:6-8` "origin=a84e0f7f… local=a84e0f7f… results-clone pushed and clean"
    before `worktree remove` and plan-root removal at 03:37:38.
13. **Uninstall run FROM the stub checkout at the pinned head, rc 0** (`NIGHT_HANDBACK.md:96-98`, `:117-119`): `uninstall-output.txt:1-2`.
14. **Nothing armed afterwards**: `uninstall-output.txt:3-6` (only `com.joulewise.magistrate` loaded, only its plist remains) and
    `removal-output.txt:14-20` (custody parent = `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1`).
15. **No watchdog-owned file touched.** `com.joulewise.magistrate.plist` is byte-identical in timestamp and size before and after
    (`arm-blockB-output.txt:180` and `pre-uninstall-observations.txt:4`: 1157 bytes, Sep 6 03:08); the only watchdog writes claimed are
    heartbeat and `notice.ack`. Relaunch prompt line 19 satisfied.
16. **Finding classified correctly.** `night-receipt.json:76` `night_probe_error` ≠ `night_refused_agent_present`, so
    `NIGHT_HANDBACK.md:99-101` makes it a finding; `21i:36-37` says exactly that and adds "this plan is never re-armed on this signature".
17. **Receipt/result facts match the bytes.** `21i:13-15` versus `night-result.json` (`REHEARSAL_ONLY`, `chain_exit_code` 0,
    `census_count` 1, `census_hits` [], `aborted_reason` null) and `night-receipt.json` (C1/C4 "not evaluated after refusal",
    C2 `NOT_APPLICABLE`/`no_pack_by_design`, C3 clean census but FAIL, C5 three heads all `ae8f074f`) — every clause checks out, and
    the D-169 fence "REHEARSAL_STUB can never carry verdict GO" holds.
18. **Code citations in 21i re-verified at this head** (I ran the reads): `joulewise/night_gate.py:1046-1047` are the unconditional
    `probes.read_text(plan.chain_path)` / `chain_sha256_path` calls; `scripts/run_night.py:1540` is
    `rehearsal_effective = rehearsal or plan.receipt_class == "REHEARSAL_STUB"`; `:1566-1570` is the `/dev/null` + `sleep 2; echo REHEARSAL`
    substitution; `tests/test_night_gate.py:414` is `test_a_fully_green_rehearsal_can_never_yield_go`. 21i correctly re-derived these on
    main at `83ab38ed` instead of copying the courier's ae8f074f line numbers (681 / 1196-1199 / 1169-1170).
19. **Launchd-started, not shell-started** (kernel acceptance item 2): `night-launchd.night.out` is the `com.joulewise.night` stdout path
    configured at `arm-blockB-output.txt:29`, and it carries the courier transcript.
20. **Courier recipient is Ed's documented address**: `night-courier.sent:4` `to=claude.ai.copper531@passmail.net` =
    `docs/process/NIGHT_COURIER_PROMPT.md:14`.
21. **SHA256SUMS verify for every file actually committed**: 14/14 OK (the other three are B1).
22. **Acceptance table is honest and does not usurp the cold gate.** `21i:47-57` marks item 1 out of scope, item 3 send-side only,
    item 4 NOT YET, item 5 NOT EXERCISED/still open, item 6 MET WITH A FINDING and CONDITIONAL, and defers "whether a second stub night
    is required after the cure … to the cold gate or Ed, not this activation (rule 11)". `NIGHT_HANDBACK.md:71-73` confirms the item-5
    reasoning (agents installed 01:57 the same night, so the R-7 case does not repeat).
23. **The dead-man never fired and nothing claims it did**: `21i:12`, corroborated by `night-launchd.night.out` and by the absence of
    `launchd.deadman.*` in the harvest.
24. **No process rule amended anywhere in the diff**: `git diff --stat main...HEAD` touches no file under `docs/process/`,
    `docs/decision_log.md`, or any skill; relaunch prompt line 20 honoured.

---

## Verdict

**Blocked at 20f95848 — mergeable after the listed should-fixes on the current PR head.** The recorded arm is, on the evidence, compliant:
every D-175 condition and every `NIGHT_HANDBACK` §Next lane precondition is discharged by a captured artifact in the recorded order
(email → no-NO → census → staged/validated/`os.replace` → both agents installed from the pinned stub checkout → frozen triple → exit
32 minutes before the deadline), the harvest activation stayed inside its authority (harvest before uninstall, uninstall from the stub
checkout, removal only after `ls-remote` confirmed `night-results/20260909` at `a84e0f7f`, only heartbeat/`notice.ack` written on the
watchdog side, nothing armed at the end), the refusal is classified correctly as a finding rather than the one acceptable stub refusal,
and both the second-stub-night question and the launch-fence question are routed to the cold gate or Ed exactly as rule 11 requires.
What blocks 20f95848 is evidence custody, not conduct: three artifacts the record cites — including the driver log that
`NIGHT_HANDBACK` §Where the results are names as a result — were silently dropped by `.gitignore:45`, and the custody root and the
pushed results branch no longer hold them (B1); that is already cured at the live head `1f4c4492`, together with S5. Remaining before
merge: S1 (the kernel row and the cure lane are the machine-readable record `NIGHT_HANDBACK` §Next lane points at, and the row still
says the night is "prepared", not fired), S2 (name the authority for removing the plan, since D-175 cond. 8 textually covers it), S3
(the 82106/82210 courier-pid contradiction between the two PR documents), and S4 (the `events.jsonl` sequence claims have no captured
source). None of these require re-running anything on the machine; all are document edits landing with the twelve-row gate ledger,
whose row 12 will in any case have to name the final head sha.
