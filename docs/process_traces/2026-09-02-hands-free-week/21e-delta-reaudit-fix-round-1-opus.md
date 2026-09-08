# Delta re-audit — PR #295 `bookkeeping/2026-09-08-activation-evidence`, head 82622e70

Range audited: `a6bff232..82622e70` (fix round 1 `0f3390c9` + magistrate review `82622e70`).
Read-only; nothing written outside `/private/tmp`; no git write commands; `~/night-custody` read only via a
FAKE `$HOME` in the census bench. Worktree `/Users/edr/code/JouleWise-wt-magistrate-1ef89702`.
Diff content files: `docs/process/NIGHT_HANDBACK.md`, `21-first-launchd-activation-1ef89702.md`,
`21b-rehearsal-20260909-arm-plan.md` (+ three added trace files 21c/21d).

## F1–F15 against the 21c dispositions

| # | disposition | status | evidence (file:line) |
|---|---|---|---|
| F1 | ruled B (consolidated notice; H stays ae8f074f) | **PARTIAL** | ruling recorded `21b:32-40`; timeline `21b:7-30`; NO-ARM-pending-notice `21b:38-40`. But `21b:155` still reads "(1) DISPUTED — see Timeline of record" and re-ties the *notice* to cond. **4**, contradicting ruling B, which judges cond. **1** on that notice (D-175 cond. 1/4 at `13-magistrate-synthesis.md:37,44`). See N7. |
| F2 | re-derive every time from primaries | **PARTIAL** | 9 of 10 stated times now carry a primary source and check out (`21b:3,17,60,134,139,152,271,289`; Gmail internalDate verified live, see Executed evidence). Two of the class survive: `21b:26` (`~01:58` vs real 02:01:16, source column says "git") and the NEW `21b:255` (`~02:20` in a commit dated 02:11:53). See N1, N2. |
| F3 | census pid from the lock | **CURED** | `21b:227` `me = json.load(open(os.path.expanduser("~/night-custody/magistrate/magistrate.lock")))["pid"]`; benched both ways (Executed evidence). |
| F4 | fatal guards | **CURED** | every `test`/`cat-file`/`mkdir`/`cd`/python step now ends `|| { print "ABORT: …"; exit 1; }` — `21b:163,165,168,170-172,174,176-178,181-182,207-210,224,243-244,246-247`; benched that `exit 1` inside `{ … }` terminates a pasted zsh block. (New, distinct gap: the arm *window* is still comment-only — N5.) |
| F5 | twin validation under $TMPDIR; real custody created only by the pre-move mkdir | **CURED** | `21b:175-180,196-202,204-210,242-243`; installer reads `custody_root` from the plan file (`scripts/install_night_agent.sh:40`) and `mkdir -p "$custody_root/night"` at `:119-121`, so `--render-only` touches only `$SCRATCH`. Benched: author+twin+diff rc 0, fake real-custody path absent afterwards. |
| F6 | no allowlist; fail-closed on a reparented own process | **CURED as ruled** | `21b:220-222`, `21b:293-295`; bench case A (reparented `claude daemon run`) → `rc=1`. Unreconciled consequence: N8. |
| F7 | quote the artifact | **CURED** | `21:19` and `21:47` now read `clock_sane_samples: 36`; `state.json` = 36, `last_clock.epoch_s` 1788854247.49973 = 00:57:27. |
| F8 | strike `notice.ack` from the copied list | **CURED** | `21:4-7` lists nine artifacts and states `notice.ack` "had already been consumed … no copy exists"; the dir holds exactly nine files. |
| F9 | one authoritative handback text | **CURED** | `21b:130` replaces the stale draft with `git show ae8f074f:docs/process/NIGHT_HANDBACK.md`; no second copy remains in 21b. |
| F10 | record the order (PD-1) | **CURED** | `21b:58` — arm email 01:05:21 preceded the cold-gate AMEND (a8cc6e68, 01:20:08); nothing was armed. |
| F11 | restore four sentences verbatim | **CURED** | `NIGHT_HANDBACK.md:87-100`; all four match `git show main:docs/process/NIGHT_HANDBACK.md` word for word (whitespace-normalized containment test, 4/4 True). Only additions are the bold label "**Standing rules**" and the prefix "Installer note:"; no new normative sentence — no rule smuggled in. Duplication defect: N6. |
| F12 | tie the nonempty census to the clause it fails | **CURED** | `21:32` — cites `MAGISTRATE_WATCHDOG.md:256` and states the handoff is not clean under that clause. |
| F13 | heartbeat claim / schema drift | **CURED** | `21:36-39` — "Nothing reads the heartbeat"; `epoch_s` vs `ts` recorded, not resolved. |
| F14 | rewrite the unparseable sentence | **CURED** | `21b:283` — "Step 4 derives `me` from the lock the live activation holds; never a constant." |
| F15 | don't claim what the census does not show | **CURED** | `21:70` — attribution now "identified … by joulewise-53, not from this census"; the census line does show python3.14 and the 09-04 04:53 start. |

12 CURED, 3 PARTIAL/qualified, 0 REGRESSED among F1–F15 themselves.

## Same-signature

**SURVIVES: self-reported wall-clock times not tied to an artifact (F2 class), plus a claim unsupported by any
copied artifact (F7/F8 class)** — `21b:255` states bench pass 2 ran "~02:20 PDT" but the commit recording it
(82622e70) is dated 02:11:53, and no pass-2 artifact was copied (`21b-rehearsal-20260909-bench/` still holds only
the three 01:05 pass-1 files); `21b:26` puts 83b3ec5e at "~01:58" under source "git" when its committer date is
02:01:16. The fix-round brief itself dictated "replace EVERY self-reported '~HH:MM PDT' time with the table value"
(`21d-fix-round-1-brief.md:33`); the review commit reintroduced the class it was convened to remove.
Classes checked and NOT surviving: hard-coded operative pids (census derives `me` from the lock; remaining pid
mentions are prose, none signals or gates — but see N11); non-fatal guards inside the sequence (all fatal);
writes under the real custody root before the move (none; benched); duplicated authoritative handback text in 21b
(removed — but re-appears inside NIGHT_HANDBACK.md itself, N6); process-rule amendment inside a per-night handback
(none — the restored block is verbatim main text).

## New defects

**N1 — blocker — `21b:26`: the "Timeline of record" carries a wrong git-sourced time.**
Row `commits 9a15338e / a6bff232 / 83b3ec5e | 01:48:16 / 01:48:47 / ~01:58 | git`; `git log` gives 83b3ec5e =
2026-09-08 02:01:16 -0700. A table whose whole purpose is primary-source times, and which ruling B requires to be
restated to Ed in the consolidated arm notice ("include the corrected timeline … with primary-source times",
`21c:215-216`), still ships an approximate, wrong, "git"-labelled value.
Cure: `83b3ec5e | 02:01:16`, and add the three later commits (dbd49c1d 02:03:37, 0f3390c9 02:10:06, 82622e70 02:11:53).

**N2 — blocker — `21b:255`: bench pass 2 is self-timed ahead of its own commit and has no artifact.**
"Bench pass 2 (activation 784a764e, ~02:20 PDT 2026-09-08 …)" is recorded by 82622e70, committer date 02:11:53 —
the identical impossibility F2 was raised for. Its five observations (`21b:257-266`) are also uncorroborated: no
pass-2 plan, plist, or transcript was copied into the trace (`git diff --name-status a6bff232..82622e70` adds no
artifact files). I independently reproduced the *substance* (author + twin + json diff, Executed evidence), so the
claim appears true — but as landed it is an unsourced self-report in the file whose credibility this PR is about.
Cure: restate the time as the commit's (02:11:53, or the real bench clock from a copied artifact) and copy at least
the twin/staged plan pair under `21b-rehearsal-20260909-bench/pass2/`.

**N3 — should-fix — `21b:170-172` vs `21b:180,252`: `$STUB_CHECKOUT` has no abort cleanup (F5's retry-blocking class, one step earlier).**
Step 1 creates a detached worktree at `/private/tmp/joulewise-rehearsal-20260909-checkout`; the abort rule cleans
only `$STAGE` and `$SCRATCH`. Any abort in steps 2–7 leaves that checkout (and its `worktree` metadata in
`$DRIVER_SOURCE/.git`), so the retry aborts at the `test ! -e "$STUB_CHECKOUT"` guard — exactly the F5 complaint
("the retry guard will fail after an abort and the plan says nothing about it"), relocated.
Cure: add "on abort after step 1: `git -C "$DRIVER_SOURCE" worktree remove --force "$STUB_CHECKOUT"`".

**N4 — should-fix — `21b:243-247`: no procedure for a failure AFTER the atomic move.**
If `install_night_agent.sh` (step 7) fails once `os.replace` has published the plan, a discoverable
`~/night-custody/rehearsal-20260909/night_plan.json` exists with no night agents installed; the watchdog will
fence on the plan span (`plan_span_active`, `magistrate_watchdog.py:721`) and drive the stand-down sequence at
t0−25/−16/−15 for a night that can never run, while step 2's `test ! -e "$NIGHT_CUSTODY"` blocks any retry.
Cure: one line — on a step-7 failure remove the plan file and the plan root (authorized for the authoring session
by D-175 cond. 8 / line 19 (a)), then abort.

**N5 — should-fix — `21b:160-162`: the arm window is a comment; the only enforced bound is 02:31.**
"01:56 PDT <= now < 02:15 PDT" is prose. The sole executable time check is `assert now < t0 - 25*60` in the
authoring block (`21b:191`) = 02:31 — 16 min past the stated ceiling — and there is NO floor check at all, though
ruling B says "do not arm earlier than t0 − 60 min" (`21c:222`). A paste at 02:25, or at 01:30, proceeds.
Cure: add a zsh guard on `date +%s` against 1788944160/1788945300 before step 1.

**N6 — should-fix — `NIGHT_HANDBACK.md:80-82` duplicates `:89-93`.**
"Author every new v2 plan with `write_night_plan`; the writer emits both `schema:…v2` and integer
`schema_version: 2`." now appears twice — once truncated in "Next lane", once complete in the restored Standing
rules — two authoritative statements of one rule, one missing the malformed-plan clause. The F11 cure appended
without pruning what it superseded.
Cure: delete the `:80-82` restatement.

**N7 — should-fix — `21b:155`: "(1) DISPUTED" contradicts the ruling recorded 120 lines above.**
Ruling B (`21b:32-40`, `21c:209-213`) resolves cond. 1: it is judged on the consolidated notice. The conditions
line still calls (1) DISPUTED and instead attaches the notice to cond. 4.
Cure: "(1) satisfied when the consolidated notice is sent (ruling B); (4) satisfied by that notice, which precedes the move".

**N8 — should-fix — `21b:286-288` vs `21b:220-222,293-295`: as written, the arming activation aborts its own arm.**
The trace states activation 784a764e "keeps itself alive with a bounded background poll" — Claude Code background
work runs under a `claude daemon`/`bg-pty-host` reparented to pid 1 — and the census rules every reparented
`codex|claude|t3` process a fatal foreign match with no allowlist. Nothing in 21b reconciles the two; the arm can
be structurally unreachable at 01:56.
Cure: state that the arming activation must stop its own background poll and confirm `claude daemon stop --any`
before step 4 (step 3b says "stop every Codex child and background task" but never names the keep-alive poll).

**N9 — nit — `21b:207`: the plan that is actually armed is never passed through `--render-only`.**
D-175 cond. 2 literally requires validation "with `--plan <staged>`" (`13-magistrate-synthesis.md:39-41`); the
sequence validates the twin. Ruling B requirement 3 authorizes this, and the field diff closes the gap, but the
deviation is not stated as one.

**N10 — nit — `21b:220,240`: manual steps sit as comments inside a block the file says is pasted.**
Step 3b (stop own children) and step 5 (re-check the thread for NO, cond. 4) execute as nothing; a whole-block
paste runs 3 → 4 → 6 without them. Split the block at 3b and at step 5, or make step 5 a `read -q` gate.

**N11 — nit — `21b:149-150`: `ps -p 48645` is comment-only and the census regex would not catch it.**
The pid is described as already retired, and its command line (`process-census-0055.txt:1`, python3.14 framework
path) matches neither `codex|claude|t3`, so if a leaked python-hosted stub magistrate did survive, step 4 passes
while D-175 cond. 5 ("no agent session OTHER than the arming session") is false.

Arithmetic and fence claims check out: t0 = 1788947760 = 2026-09-09 02:56:00 PDT; t0−60 = 01:56; t0−25 = 02:31
(`REQUEST_LEAD_S = 25*60`, `magistrate_watchdog.py:68`); TERM 02:40 (`TERM_LEAD_S = 16*60`, `:69`), KILL 02:41
(`KILL_LEAD_S = 15*60`, `:70`); belt `[02:45, 03:30)` (`:711`); courier 03:16. `21b:117,250` and the 02:15 ceiling
("leaves >= 16 min") are correct, and no statement in 21b contradicts `MAGISTRATE_WATCHDOG.md:14-15,36,304`.

## Executed evidence

```
$ git -C <wt> log --format='%h %ci' -4
82622e70 2026-09-08 02:11:53 -0700 | 0f3390c9 02:10:06 | dbd49c1d 02:03:37 | 83b3ec5e 02:01:16   # N1, N2

$ Gmail get_message METADATA_ONLY (primary source, read-only)
1a0800cdb282c3f1 internalDate 1788854721000 -> 2026-09-08 01:05:21 PDT, thread 1a0800cdb282c3f1, SENT
1a08012045894ef7 internalDate 1788855059000 -> 2026-09-08 01:10:59 PDT, same thread            # 21b:17,20 TRUE

$ python3 zoneinfo: 1788854641.569302 -> 01:04:01 ; 1788854247.49973 -> 00:57:27 ; t0 1788947760 -> 2026-09-09 02:56
  t0-25m 02:31:00 ; t0-60m 01:56:00 ; courier(t0+900+300) 03:16:00

$ extract 2 ```zsh blocks + 4 heredoc PY blocks;  zsh -n block0.zsh; zsh -n block1.zsh      -> rc 0, rc 0
  compile(py0..py3)                                                                        -> all "compiles OK"

$ HOME=<tmp fakehome> zsh globtest.zsh          # plans=(~/night-custody/*/night_plan.json(N)) + guard
count=0 / proceeded / rc=0        (empty)
count=1 / ABORT: existing plan / rc=1   (one fake plan)   # (N) qualifier valid; exit 1 in { } aborts the paste

$ PS_TABLE=tableA HOME=<fakehome> PATH=<fake ps> python3 py3.py      # lock pid 5000 roots a 3-proc tree; 6000 = reparented `claude daemon run`
foreign census matches: [(6000, '/Users/edr/.local/bin/claude daemon run --origin transient')]   rc=1
$ PS_TABLE=tableB … python3 py3.py                                   # own tree only
foreign census matches: []   rc=0

$ cd <wt>; NIGHT_CUSTODY=<tmp>/fakecustody/rehearsal-20260909 STAGE=<tmp>/stage SCRATCH=$(mktemp -d) \
  STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout H=ae8f074f… python3 -B - < py1.py ; python3 - < py2.py
<tmp>/stage/night_plan.json
<tmp>/scratch.Ex2OFK/night_plan.json          author rc=0
plan differing fields: ['chain_path', 'chain_sha256_path', 'custody_root']   diff rc=0   # allowed set exact
fake real custody absent (correct)                                                        # F5 cure holds

$ python3: NightPlan is @dataclass(frozen=True) (night_gate.py:183-196) -> dataclasses.replace valid;
  from_mapping (night_gate.py:200-300) imposes NO restriction on custody_root/chain paths (only absolute
  measurement_root, 40-hex heads, registration_path required for REHEARSAL_STUB) -> a $TMPDIR twin is accepted;
  write_night_plan (night_plan_writer.py:37-68) mkdirs only target.parent.
$ install_night_agent.sh:40 reads custody_root FROM the plan; :119-121 mkdir -p "$custody_root/night"; :189-191
  --render-only exits 0 after the pins line -> twin validation cannot touch the real custody root.

$ whitespace-normalized containment of the 4 F11 sentences: main True/True/True/True, branch True/True/True/True
  branch count("Author every new v2 plan with `…write_night_plan`") = 2 ; count("writer emits both") = 2   # N6

$ python3 -c json state.json -> clock_sane_samples 36, backoff_index 0, attempt 1, notice_pending []   # F7
$ ls 21-activation-1ef89702/ -> 9 files, no notice.ack                                                  # F8
$ ls 21b-rehearsal-20260909-bench/ -> 3 files, all mtime Sep 8 01:05 (pass 1 only)                      # N2
```

VERDICT: **NOT LANDABLE** — blockers N1 (`21b:26`, wrong git-sourced time inside the corrected Timeline of record
that ruling B pushes into Ed's arm notice) and N2 (`21b:255`, bench pass 2 self-timed 8 min after the commit that
records it, with no copied artifact). Both are one-line edits; F1–F15 are otherwise cured or ruled, and the
executable core of the arm sequence (staging, twin validation, fatal guards, lock-derived census) benches clean.
