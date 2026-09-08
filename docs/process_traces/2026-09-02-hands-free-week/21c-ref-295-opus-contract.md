# Refutation — PR #295 `bookkeeping/2026-09-08-activation-evidence`, head a6bff232c9269990d913c59bdfec459369fb4aff

Read-only contract-lens pass over the 17-file docs diff (`git diff main...HEAD --stat`: 957 insertions,
63 deletions). Worktree `/Users/edr/code/JouleWise-wt-magistrate-1ef89702`. Nothing was written outside
`/private/tmp`. Gmail ids taken as existing per the brief; their *timestamps* are not taken as given and are
the subject of F1.

## Findings

### F1 — BLOCKER — the arm email cannot have been sent at the time the trace states, and the D-175 cond. 1 ordering is refuted
`21b-rehearsal-20260909-arm-plan.md:107-112` ("## Arm email (precondition (a)) — SENT / Gmail id
`1a0800cdb282c3f1`, 2026-09-08 ~01:27 PDT") was itself committed at **01:05:39 -0700** (commit `f9679fb4`,
`Trace 21b: arm email id recorded`). A message sent at 01:27 cannot be recorded in a commit made at 01:05.
So either the stated time is false or the "SENT" label was.
The consequence is contract-bearing: `ae8f074f` (the handback rewrite, H) has committer date **01:10:44
-0700**, i.e. *after* the email was recorded as sent. D-175 condition 1 reads "NIGHT_HANDBACK.md re-dated with
the real pins and committed before the arm email (satisfied at ae8f074f)"
(`docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md`).
`21b:132` asserts "(1) satisfied at `ae8f074f`". On the commit timestamps in this very PR, it is not.
Cure: read `internalDate` of `1a0800cdb282c3f1`; if it precedes `ae8f074f`, either re-send the arm email
citing H and correct 21b, or record the cond.-1 miss and return it to the cold gate before any arm.

### F2 — BLOCKER — every self-reported wall-clock time in 21b is 15–30 min ahead of the artifacts
- `21b:3` "Written … at ~01:25 PDT" — the file was created by `4ac5d981`, committer date 01:05:11.
- `21b:23` "Bench pass (2026-09-08 ~01:24 PDT)" — `21b-rehearsal-20260909-bench/bench-night_plan.json`
  carries `authored_epoch_s: 1788854641.569302` = **01:04:01 PDT**; all three bench artifacts have mtime 01:05.
- `21b:114` "Handback committed as H; pins on Ed's thread (2026-09-08 ~01:40 PDT)" — `b0c88632` is 01:11:22.
- `21b:128` "cold gate AMEND … relayed by joulewise-53 ~01:50 PDT" — `a8cc6e68` is 01:20:08.
(The 21b:197 succession section, "~01:50", is the only accurate one: `9a15338e` 01:48:16.)
This is a trace whose timestamps are the evidence for a ruling's ordering conditions, written on a machine whose
watchdog had just been in `CLOCK_UNCERTAIN`. Cure: re-derive every stated time from commit/artifact timestamps
and add one line stating the source of each.

### F3 — BLOCKER — the amended step-4 census block still hardcodes a dead pid; as written the arm can never proceed
`21b:170-184` contains `me = 84232`. Pid 84232 died at 01:33:28 (`attempts/1ef89702-…/attempt-1.stderr.log`);
the live session is 83086 (`~/night-custody/magistrate/magistrate.lock`). Bench-executed against a fake process
table: with `me` set to a pid absent from the table the classifier returns the arming session's OWN `claude -p`
and its codex child as foreign (see Executed evidence), so the block exits 1 and the arm never happens.
The correction exists only as prose 26 lines later (`21b:209-212`) and is not applied to the code block.
D-175 cond. 5 requires the census to be re-run immediately before the move; the block as committed does not
satisfy it. Cure: edit the block in place to
`import json, os; me = json.load(open(os.path.expanduser("~/night-custody/magistrate/magistrate.lock")))["pid"]`.

### F4 — should-fix — the sequence's preconditions are non-enforcing
`21b:144, 146, 148, 149` (`test ! -e …`, `test "$(git … rev-parse HEAD)" = "$H"`) and `21b:142`
(`git … cat-file -e "$H^{commit}"`, cond. 6) carry no `|| exit 1`, and neither zsh block sets `-e`.
Bench-demonstrated: a failing `test` and a failing `cat-file -e` both fall through to the next line.
Only `21b:138-139` abort. So conditions 2, 3 and 6 are decorative in the pasted block.
Cure: `set -euo pipefail` at the top of the block, or `|| exit 1` on each guard.

### F5 — should-fix — `--render-only` writes into the real custody root, defeating the staging invariant
`scripts/install_night_agent.sh:119-122` runs `mkdir -p "$custody_root/night"` for **every** non-uninstall
invocation, including `--render-only`. The staged plan's `custody_root` is
`/Users/edr/night-custody/rehearsal-20260909` (`21b:162`), so step 3 (`21b:167`) creates that directory before
the `os.replace` of step 6. The glob `~/night-custody/*/night_plan.json` still does not match (cond. 2 survives),
but step 2's guard `test ! -e "$NIGHT_CUSTODY"` labelled "cond. 3: no prior record" (`21b:148`) will fail on any
retry after a step-4/5 abort, and the plan says nothing about it.
Cure: note the side effect and make the retry guard "no night records under `$NIGHT_CUSTODY/night`", not `! -e`.

### F6 — should-fix — the census classifier cannot see reparented Claude daemon children, including the arming session's own
`mine()` walks `ppid` to 1. In the copied primary census, `71596` (`--bg-pty-host`) and `71666`
(`claude daemon run --origin transient`) both have **ppid 1** (`21-activation-1ef89702/process-census-0055.txt:2-3`)
though they were spawned by a session. `21b:216` states that activation 784a764e "keeps itself alive with a
bounded background poll" — Claude Code background work runs under exactly such a reparented daemon. The arming
session's own daemon will therefore be classified foreign and abort the arm, while `21b:220-223`'s claim that
"the step-4 regex already matches every one of those command lines … so no census change is needed" reasons only
about the regex, never about the parent chain.
Cure: pin the session's own daemon/bg-pty-host pids into an allowlist derived from `claude daemon` state, or
match `--spawned-by`'s cwd, before relying on ancestry.

### F7 — should-fix — 21's state.json numbers do not match the copied artifact
- `21-first-launchd-activation-1ef89702.md:18`: "state.json shows `clock_sane_samples: 4`" —
  `21-activation-1ef89702/state.json:8` reads **36**; no copied artifact shows 4.
- `:42`: "(`clock_sane_samples: 33` at copy time)" — the copied file reads **36**
  (`last_clock.epoch_s` 1788854247.49973 = 00:57:27, matching its 00:57 mtime).
Cure: quote the artifact or delete the numbers.

### F8 — should-fix — 21 claims an artifact it did not copy
`21-first-launchd-activation-1ef89702.md:5` lists `notice.ack` among the files "copied verbatim into
`21-activation-1ef89702/`". The directory holds nine files and no `notice.ack`; `:40` says the file was already
consumed and gone. Cure: strike `notice.ack` from the list at :5.

### F9 — should-fix — "wording fixed here" is false
`21b:83` heads the handback text with "(committed as H at arm time; wording fixed here)". `21b` was written at
`4ac5d981` (01:05:11) and the text actually committed at `ae8f074f` (01:10:44) differs materially: the committed
version adds the thread id `1a0800cdb282c3f1`, the courier deadline `t0 + 900 + 300 = 03:16 PDT`, "Both night
agents are installed FROM that checkout", and a pointer back to 21b. 21b was never reconciled.
Cure: replace the block with the committed text or a `git show ae8f074f:docs/process/NIGHT_HANDBACK.md` pointer.

### F10 — should-fix (AUTHORITY) — self-issued ruling acted on externally before the cold gate existed
`21b:15-21` is a headless magistrate issuing a "RULING" that changes documented stub practice
(`docs/process/MAGISTRATE_WATCHDOG.md:258` calls the stubs' `/private/tmp/...` measurement roots "deliberately
fake"), and the arm-request email to Ed went out under it (F1: at or before 01:05:39) — before the cold-gate
AMEND was relayed at `a8cc6e68` (01:20:08). Relaunch prompt line 20 (`21-activation-1ef89702/prompt.md:20`)
bars ratifying or amending process rules. Nothing was armed and D-175 later ratified the substance, so this is
recoverable, but the trace presents the order as clean.
Cure: one sentence in 21b recording that the arm email preceded the ruling of record, per PD-1.

### F11 — should-fix (AUTHORITY) — the handback rewrite prunes standing rules, not just the night
`docs/process/NIGHT_HANDBACK.md:64-88` ("Next lane") drops, without replacement in that file: "invalid-plan tests
begin with that writer's bytes and apply a named mutation"; "either field missing or inconsistent makes the plan
malformed"; the installer pin note ("`--uninstall` checks neither pin and no longer needs `claude` on PATH"); and
"Ordinary daytime work in the dev checkout no longer invalidates an armed night; only moving the pinned
measurement checkout does." The file's own charter (`:4-9`) authorises rewriting the three sections *for the
night*; these four are standing operational rules. (No evidence is lost — the named-mutation rule survives at
`docs/decision_log.md:10894`, and the 09-02/09-03 night outcomes at `00-DURABLE-STATE.md:12` — so this is
doctrine tidiness, not data loss.)
Cure: restore the four sentences verbatim in the rewritten "Next lane".

### F12 — nit — step-6 framing overstates what was verified
`21:21` heads three checks as "MAGISTRATE_WATCHDOG.md §Install handoff step 6 checks (verified from this
activation)". Step 6 (`docs/process/MAGISTRATE_WATCHDOG.md:256`) also states "a nonempty census before that tick
… is a failed handoff"; the census was manifestly nonempty (joulewise-53 plus daemons). The trace discloses the
coexistence at `:46` but never ties it to the clause it fails.

### F13 — nit — unsupported heartbeat-interface claim and silent schema drift
`21:33` asserts "the heartbeat interface wants the session pid the lock names". Nothing reads the heartbeat:
`scripts/magistrate_watchdog.py` has zero occurrences of "heartbeat"; the only mention is
`docs/process/MAGISTRATE_WATCHDOG.md:81`, which specifies no fields. The two activations also disagree on the
key name (`epoch_s` in the copied `heartbeat.json`, `ts` in the live `~/night-custody/magistrate/heartbeat`).

### F14 — nit — 21b:209-212 correction sentence is not English
"…and assert `me == os.getppid()`-chain membership is unnecessary — the lock pid is the session." Unparseable;
the operative instruction has to be inferred. Cure: rewrite as one imperative sentence.

### F15 — nit — census-derived identification unsupported by the copied artifact
`21:65` calls pid 48645 "`python3 …/T/watchdog`". `process-census-0055.txt:1` truncates at the command column and
shows only `…/Python.`; the `/T/watchdog` path appears nowhere in the copied evidence.

## Conditions checked clean (no finding)
- Cond. 2 staging path `/private/tmp/joulewise-rehearsal-20260909-staging/night_plan.json` is outside the
  watchdog glob; `Storage.glob_plans` is `root.parent.glob("*/night_plan.json")`
  (`scripts/magistrate_watchdog.py:258-259`), and the retired plans sit one level deeper, so step 0's guard is
  not spuriously tripped.
- `--render-only DIR` exists (`scripts/install_night_agent.sh:5,21,113-118,189-191`) — D-175's citation holds.
- All twelve `NightPlan` constructor arguments in both python blocks match the dataclass
  (`joulewise/night_gate.py:184-196`); `write_night_plan(path, plan)` matches
  (`joulewise/night_plan_writer.py:37`); `registration_path` is mandatory for `REHEARSAL_STUB`
  (`night_gate.py:282-287`) and the named file exists at `ae8f074f`.
- `--hour 2 --minute 56` == t0 local; `t0 = 1788947760.0`; `custody_root` equals the post-move plan directory;
  courier deadline `t0+900+300` = 03:16 PDT matches `COURIER_DEADLINE_S = 300` and
  `scripts/run_night.py:939`; exit boundary 02:31 = t0−25 min.
- Missing `chain.zsh`/`chain.zsh.sha256` is not a defect: `scripts/run_night.py:1169,1197-1198` forces
  `/dev/null` and the built-in stub for `REHEARSAL_STUB`.
- Cond. 6: `ae8f074f` is reachable and pushed (`origin/bookkeeping/2026-09-08-activation-evidence`).
- Morning-after uninstall path exists and is documented twice (`21b:79`, `NIGHT_HANDBACK.md:70-73`).
- 21's event table, the 00:55:36 ack, the 01:33:28 termination, backoff 300 s, lock pids 84232/84229 and
  83086/83075, `attempt: 2`, the `caffeinate -i -w 84232`, the 00:39:32 pmset line, `4a7a768c`, `ae8f074f`, and
  the `16777233` device claim all match the artifacts.
- 21b's ruling premises hold: `install_night_agent.sh:88` does gate on a real checkout;
  `/Users/edr/JouleWise-measurement-20260813` is at `eeb4e133815d0c…` and has no `joulewise/night_plan_writer.py`.

## Executed evidence
```
$ git -C …-wt-magistrate-1ef89702 log --format='%h %ci %s' main..HEAD
a6bff232 2026-09-08 01:48:47 -0700 Trace 21b: joulewise-53's census …
9a15338e 2026-09-08 01:48:16 -0700 Trace 21b: activation succession …
2987a626 2026-09-08 01:20:19 -0700 Trace 21b: correct the verified device id (16777233)
a8cc6e68 2026-09-08 01:20:08 -0700 Trace 21b: arm-time sequence amended to the cold-gate conditions …
b0c88632 2026-09-08 01:11:22 -0700 Trace 21b: H pinned explicitly, pins follow-up id, peer ruling note
ae8f074f 2026-09-08 01:10:44 -0700 NIGHT_HANDBACK: rehearsal-20260909 …
f9679fb4 2026-09-08 01:05:39 -0700 Trace 21b: arm email id recorded
4ac5d981 2026-09-08 01:05:11 -0700 Trace 21b: rehearsal-20260909 ruling …
4a7a768c 2026-09-08 01:02:02 -0700 Trace 21a: astra read-only scout …
67cbf5fe 2026-09-08 00:57:32 -0700 Trace 21: first watchdog-owned launchd activation …

$ git cat-file -e ae8f074f^{commit} ; git cat-file -e 4a7a768c^{commit}     # both rc 0
$ git branch -r --contains ae8f074f  ->  origin/bookkeeping/2026-09-08-activation-evidence

$ python3 census_test.py            # 21b:170-184 verbatim, fake ps table
me=84232 (live): [(83953, 'claude'), (71666, '…/claude daemon run --origin transient')]
me=83086 (lock pid, absent from table): [(84232, '…/claude -p You are the top-level magistrate'),
  (84246, 'node …/codex mcp-server'), (83953, 'claude'), (71666, '…/claude daemon run …')]

$ python3 -c '…json.load(open("~/night-custody/magistrate/magistrate.lock"))["pid"]'
lock pid -> 83086

$ zsh -n /tmp/block0.zsh ; zsh -n /tmp/block1.zsh          # both OK (2 zsh blocks extracted)
$ python3 -c compile(...)  on the 3 heredoc PY blocks      # 0,1,2 all "compiles OK"
$ zsh guard.zsh
reached line after failed guard (rc of guard was 1)
reached line after failed cat-file (rc was 128)

$ grep -n -- "--render-only" scripts/install_night_agent.sh
5:  usage: … [--uninstall] [--render-only DIR] [--launchctl-bin PATH]
21:    --render-only) render_only="${2:-}"; shift 2 ;;
$ zsh scripts/install_night_agent.sh          # usage line printed, rc 2 path

$ plutil -lint …/21b-…-bench/bench-render-com.joulewise.night{,.deadman}.plist   -> OK, OK

$ python3 - (zoneinfo)
1788947760.0 True ; t0-25min 2026-09-09 02:31:00-07:00 ; courier 2026-09-09 03:16:00-07:00
1788689333 -> 2026-09-06 03:08:53 ; 1788690995 -> 03:36:35 ; 1788853915 -> 2026-09-08 00:51:55
1788854136.9 -> 00:55:36.9 ; 1788856408.777 -> 01:33:28 ; 1788856918.677 -> 01:41:58
$ stat -f %d /private/tmp /Users/edr/night-custody  -> 16777233 / 16777233

$ cat …/attempts/1ef89702-…/attempt-1.stderr.log
Background tasks still running after 600s; terminating. Set CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 …
$ ls /Users/edr/night-custody/*/night_plan.json  -> no matches (rc 1)
$ cat /Users/edr/JouleWise-measurement-20260813/.git/refs/heads/main -> eeb4e133815d0c12486d597d9434a2c18c83c1c4
```

VERDICT: **NOT LANDABLE** — blockers F1 (arm email recorded as sent 22 min before it was sent, and on the commit
clock it preceded H, refuting D-175 cond. 1), F2 (every self-reported time in 21b is 15–30 min ahead of the
artifacts), F3 (the arm block's census hardcodes the dead pid 84232 and, bench-proved, can never pass).

## Ruling of record on F1 (synthesis author joulewise-53, cross-session message ~02:03 PDT 2026-09-08; Ed may veto on the thread)

Option B. Condition 1 is judged on ONE consolidated arm notice sent on the same thread (`1a0800cdb282c3f1`) AFTER the
fix round lands on the branch; H stays `ae8f074f` and conditions 2 and 6 keep that sha. Reasoning: condition 1 exists so
that the pins Ed can say NO to are durable before he is asked; the 01:10:59 pins follow-up met the substance 15 s after
H, but the 01:05:21 email asked before the pins were committed, so the ordering is ambiguous on the primaries. One
consolidated notice cures that at the cost of one email. Requirements on that notice: (1) restate every pin verbatim
(t0 epoch and local time, measurement_root, measurement_head ae8f074f, receipt class REHEARSAL_STUB, courier deadline,
custody_root) and "launches unless NO"; (2) include the corrected timeline (arm email, H, pins follow-up, this notice)
with primary-source times and state that the earlier 21b self-reported times were 15–30 min ahead of the commit clock;
(3) send it only after the fix round is committed: the census block must not hard-code pid 84232 (derive the foreign
list live), guards must be fatal (a non-zero census or a failed --render-only aborts the arm), and --render-only must
run against a SCRATCH custody root under $TMPDIR so nothing is created under the real custody root before the atomic
move (condition 2's staging rule covers the whole validation, not only the plan file); (4) restore the four dropped
"Next lane" sentences in the handback or record here why each is obsolete. The NO window runs from that notice; do not
arm earlier than t0 − 60 min (01:56 PDT 2026-09-09) and never before joulewise-53's stand-down message.

Magistrate 784a764e disposition of the refutation: F1 → ruled B above; F2, F3, F4, F7, F8, F9, F10, F12, F13, F14, F15
→ dictated cures in fix round 1 (astra seat, brief in the activation's scratch, report custodied as 21d); F5 → the
ruled twin-validation shape (validation twin plan under $TMPDIR, byte-diff against the real staged plan, real custody
root first created by the mkdir immediately before os.replace); F6 → no allowlist: the arming session stops its own
Codex children and background tasks before the census and a reparented own process aborts the arm (fail-closed) [superseded in part by
the condition-5 ruling below: Ed's ChatGPT.app tree and its reparented Electron helpers are excluded];
F11 → restore the four sentences verbatim (requirement 4). Delta re-audit of the fix round follows (21e).

## Ruling of record on condition 5 (synthesis author joulewise-53, its last message before exit, after the stand-down census `pass3-standdown-census.txt` epoch 1788877254)

Condition 5 counts agent SESSIONS — a magistrate, a codex-run-v3 seat, an interactive Claude or Codex session, or their children —
not the idle helper processes of Ed's ChatGPT desktop app (pid 82301 tree: Codex Framework helpers, codex app-server,
SkyComputerUseService, cua_node). Those are Ed's app, never signalled, and they are not an agent session under D-175; the regex
list is informational for the arm. The interactive session's pid 83953 and its codex mcp-server children are treated like any other
session: absent = fine, present = do not arm. The NIGHT is judged by the driver's own first act, `joulewise.night_gate.agent_census`
under D-169's documented semantics, exactly as the handback says; the arming session does not pre-empt it. Consequences: (1) if the
driver's pgrep alternation matches the ChatGPT.app helpers at 02:56 (t0 1788947760), the receipt will be `night_refused_agent_present`, which
NIGHT_HANDBACK.md classes as acceptable for a stub; (2) the arm-notice follow-up asks Ed to quit the ChatGPT desktop app before
02:45 PDT (epoch 1788947100) on 9 Sep for a clean REHEARSAL_ONLY receipt, and both census outputs are recorded in the arm-time trace either way. Do not
hold the arm for the ChatGPT helpers alone.

Delta 5 (21e5) / delta 6 (21e6, D6-1) correction to the factual premise of this ruling, decided per process by the chains in
`21b-rehearsal-20260909-bench/pass3-census-classified.txt`: some ChatGPT-pathed processes present at the stand-down census (7143,
7631–7644, 7901, 16479) were descendants of joulewise-53's codex mcp-server (pid 83953 tree) and are sessions; others (82362
`codex … app-server`, 82551 SkyComputerUseService, the renderer helpers) chained to Ed's ChatGPT.app pid 82301 and are Ed's app;
82303/82305 (Frameworks crashpad helpers) were reparented to launchd and are Ed's app by path. The ruling's rule is unchanged: Ed's
desktop-app tree is excluded; every other foreign match is a session and blocks the arm; pid 83953 must be gone (Ed asked to close
its terminal, Gmail `1a081723350aea55`, thread `1a0800cdb282c3f1`). A working app-host Codex task under 82301 is excluded by this rule
(ruling-covered: it is Ed's app), recorded as a known limit; any further change to the classifier goes to a cold gate, not another patch.
