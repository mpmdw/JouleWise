# Delta re-audit 2 — PR #295 `bookkeeping/2026-09-08-activation-evidence`, head 277d719f

Range audited: `82622e70..277d719f` (docs only; 8 files, +345/-18). Read-only: nothing written outside
`/private/tmp`, no git write commands, `~/night-custody` untouched (not even read this pass).
Worktree `/Users/edr/code/JouleWise-wt-magistrate-1ef89702`. Content files: `docs/process/NIGHT_HANDBACK.md`,
`21b-rehearsal-20260909-arm-plan.md`, `21e-delta-reaudit-fix-round-1-opus.md` (+5 pass2 artifacts).

## N1–N11 against the 21e delta re-audit

| # | claim | status | evidence (file:line) |
|---|---|---|---|
| N1 | timeline row with an approximate time | **CURED** | `21b:26` now `01:48:16 / 01:48:47 / 02:01:16`; rows added `21b:27-29`. All 14 git-sourced rows recomputed from `git log --format='%ci'` — exact, zero drift (Executed evidence). Gmail rows `21b:12,17,20` recompute from 1788854108/1788854721/1788855059 to 00:55:08 / 01:05:21 / 01:10:59 PDT. |
| N2 | bench pass 2 self-timed, artifact-less | **CURED** | `21b:282` re-times the first run to its commit (82622e70 = 02:11:53, verified) and points at the re-run artifacts; `pass2-bench-output.txt:1,16` start 02:23:36 (epoch 1788859416 → 02:23:36 PDT) / finish 02:23:38, both before 277d719f (02:25:28) — consistent. `pass2-real-staged-night_plan.json:2` `authored_epoch_s` 1788859417.475615 → 02:23:37, inside the transcript window: the stated time is now tied to an artifact the tool wrote. Re-ran the field diff on the two copied JSONs: differing fields exactly `{chain_path, chain_sha256_path, custody_root}`, `authored_epoch_s` identical. Both copied plists `plutil -lint` OK; bench parent `/private/tmp/jw-bench-arm.AZAwVU` absent. |
| N3 | `$STUB_CHECKOUT` had no abort cleanup | **CURED** | `21b:185` (in-block) and `21b:279-280` (rule) both add `git -C "$DRIVER_SOURCE" worktree remove --force "$STUB_CHECKOUT"`. |
| N4 | no un-publish after a post-move install failure | **NOT CURED** | The cure landed at `21b:116` — inside the block headed "Original arm-time sequence (historical; superseded in full…)" (`21b:75`) whose first executable line is `print "ABORT: superseded sequence…"; exit 1` (`21b:79`). The OPERATIVE amended step 7 (`21b:274`) is byte-identical to 82622e70: `|| { print "ABORT: agent install failed"; exit 1; }`. See D1. |
| N5 | arm window comment-only | **PARTIAL** | `21b:172` adds `test "$now" -ge 1788944160 -a "$now" -lt 1788945300`; recomputed 1788944160 = 2026-09-09 01:56:00 PDT = t0−3600 and 1788945300 = 02:15:00 PDT = t0−2460 against t0 = 1788947760 — both labels correct. Benched in/out (rc 0 at 1788944160/1788945299, rc 1 at 1788944159/1788945300). But the guard, and the `assert now < t0 - 25*60` at `21b:196`, sit in block A only; block B (census→move→install, i.e. the arm) has no time check. See D2. |
| N6 | `write_night_plan` rule stated twice in NIGHT_HANDBACK | **CURED** | `NIGHT_HANDBACK.md:77-83` no longer restates it; whitespace-normalized counts on the branch file: `"Author every new v2 plan with"` = 1, `"writer emits both"` = 1, `"schema_version: 2"` = 1 (main = 1/1/1). All four restored sentences (`:87-91`, `:92-95`, `:96-98`) are still verbatim-contained in `git show main:docs/process/NIGHT_HANDBACK.md` (4/4 True); the only deltas remain the `**Standing rules**` label, the `Installer note:` prefix, and one `)`→`.` where the installer sentence was lifted out of main's parenthetical. No normative text added. |
| N7 | "(1) DISPUTED" contradicted ruling B | **CURED** | `21b:158` — "(1) satisfied when the consolidated post-fix notice is sent … (4) satisfied by that same notice, which precedes the move", matching D-175 cond. 1/4 (`13-magistrate-synthesis.md:37,44-45`). |
| N8 | arming activation aborts its own arm | **CURED** | `21b:232-238` names the keepalive Monitor as a direct child that must be stopped with TaskStop, and `21b:316-317` reconciles the succession note. Introduces D3. |
| N9 | twin-validation deviation unstated | **CURED** | `21b:209-211` states the deviation from D-175 cond. 2's literal `--plan <staged>` and cites ruling B requirement 3. |
| N10 | manual steps as comments inside a pasted block | **CURED** | Three ```zsh blocks now: historical `21b:77-121`, block A `21b:161-227`, block B `21b:242-278`; the manual steps are markdown bullets between them (`21b:229-240`) with an explicit "the whole-block paste must stop here". Block A ends at the twin-diff `PY` heredoc; block B opens with `21b:244-246` re-exporting `H, DRIVER_SOURCE, STUB_CHECKOUT, NIGHT_CUSTODY, STAGE, SCRATCH` — every variable block B or its heredocs read (`$STAGE`, `$SCRATCH` via `os.environ` at `21b:220-221`; `$NIGHT_CUSTODY`, `$STUB_CHECKOUT`, `$H` in the block) is re-derived; `DRIVER_SOURCE` is re-exported but unused inside B (harmless). `$SCRATCH` was converted from `mktemp -d` to a fixed path (`21b:183`) with an existence guard, which is what makes the re-derivation sound. |
| N11 | `ps -p 48645` comment-only | **CURED** | `21b:173` `if ps -p 48645 >/dev/null 2>&1; then print "ABORT…"; exit 1; fi`. Benched: `ps -p <live>` rc 0, `ps -p 48645` rc 1, `ps -p 999999` rc 1 — alive ⇒ abort, absent ⇒ proceed. No false PASS while that pid lives; PID reuse gives a false abort (acceptable). Residual, unchanged from N11's framing: a leaked python-hosted stub under a DIFFERENT pid is still invisible to both this guard and the `codex|claude|t3` census regex. |

9 CURED, 1 PARTIAL, 1 NOT CURED.

## Same-signature

**SURVIVES: (a) a self-reported wall-clock time not tied to an artifact, and (b) an unsupported claim** — both at
`21b:234`: "INCLUDING its own keepalive Monitor (a direct child of the session pid — verified at 02:00 PDT: pid
16456 ppid 83086 — stopped with TaskStop)". `grep -rn 16456 docs/` returns that line and nothing else: no census,
`ps` capture, or events record was copied, and "02:00 PDT" is a rounded self-report inside the very class the
delta was convened to remove (the 21d brief's "replace EVERY self-reported '~HH:MM PDT' time with the table
value"). A second instance of (b) is the commit message's "un-publish on install failure after the move", which is
false of the operative sequence (D1). `21b:35` "Option B at 02:03 PDT" is fine (dbd49c1d = 02:03:37).

Classes checked and NOT surviving: hard-coded operative pids (census still derives `me` from the lock,
`21b:254`; the one new pid literal, 48645, is a named leaked-process check, not an operative identity);
non-fatal guards (every new statement — `21b:172,173,183,184,247,248,249` — is fatal; both new blocks pass
`zsh -n`); writes under the real custody root before the move (block A writes only to `/private/tmp`
staging/scratch; the first touch of `$NIGHT_CUSTODY` is still the `mkdir -p` at `21b:270`, and the manual NO
re-check at `21b:239-240` is explicitly "before any write under `~/night-custody`"); duplicated authoritative text
(N6 cured, 1/1 counts).

Grep sweep `~[0-9]` over the three content files: only `21b:314` ("~10 min" relaunch cadence, a derived rate) and
`21b:326` ("~1–2 h", a stated expectation, not a record) — neither is a time-of-record; the `~HH:MM` hits in
`21e` are quotations of the defects it raised. `PDT` sweep: all remaining wall-clock claims in `21b` carry a
commit, a Gmail internalDate, an events.jsonl epoch, or a bench artifact — except `21b:234`.

## New defects

**D1 — blocker — `21b:116` vs `21b:274`: the N4 cure was installed into dead text.**
`21b:75` heads the block "Original arm-time sequence (historical; superseded in full by the amended sequence
below)" and `21b:79` aborts it unconditionally on line 1 of execution — so the un-publish clause at `21b:116` can
never run, by construction. The sequence that will actually be pasted (`21b:242-278`, "AMENDED … supersedes the
entire earlier sequence") still fails a post-move install with a bare `exit 1`, leaving exactly the state N4
described: a discoverable `~/night-custody/rehearsal-20260909/night_plan.json` with no agents, the watchdog
fencing on `plan_span_active`, and `21b:249`'s `test ! -e "$NIGHT_CUSTODY"` blocking every retry. The clause's
authority is sound — D-175 line 19 (a), `13-magistrate-synthesis.md:29-31`, lets this session remove "a plan this
session authored" — it is simply attached to the wrong block. Cure: move the identical clause onto `21b:274`
(and delete or leave it out of the historical block).

**D2 — should-fix — `21b:172,196` guard block A; block B (`21b:242-278`) has no time bound at all.**
N5's floor/ceiling and the `assert now < t0 - 25*60` both live in the half that authors and validates. Between the
blocks sit unbounded manual steps (stop every Codex child and the keepalive Monitor; a Gmail `get_thread`
round-trip). A block B pasted at, say, 02:40 would run the census, publish the plan and install the agents past
the 02:31 request boundary (cond. 7) and inside the watchdog's TERM 02:40 / KILL 02:41 ladder; `21b:277` states
that boundary as a comment only. Cure: repeat the `date +%s` guard (ceiling 1788945300, or t0−25 min) as block
B's first statement.

**D3 — should-fix — `21b:234`: new unsourced time-and-pid observation.** See Same-signature. Cure: drop
"verified at 02:00 PDT: pid 16456 ppid 83086", or copy the `ps` line into the trace dir as the pass2 output was.

**D4 — should-fix — block B re-checks pins but not stop signals.**
`21b:247-249` re-derive and re-verify the staged plan, the checkout pin and the absence of the real custody root,
but not `~/night-custody/magistrate/standdown.request` (checked once at `21b:166`) nor the
`~/night-custody/*/night_plan.json` glob (`21b:167-168`). Both checks are now separated from the move by the
unbounded manual interval of D2; a stand-down request arriving in that gap is missed and the plan is armed anyway.
Cure: repeat both guards in block B's re-derivation preamble.

**D5 — nit — the un-publish clause (`21b:116`, and wherever D1 relocates it) does not clear the rendered plists.**
It removes the plan file and plan root and then only `launchctl list | grep … || true`. `install_night_agent.sh`
renders both plists into `~/Library/LaunchAgents` at `:187-188` BEFORE bootstrapping, and its failure paths
(`:196-210`) boot out the agents but never `rm` the files; only `--uninstall` does (`:173`). A failed install
therefore leaves two plists on disk pointing at a plan that the clause has just deleted — loadable at the next
login. Cure: call `scripts/install_night_agent.sh … --uninstall` in the clause, or `rm -f` the two plists.

**D6 — nit — `NIGHT_HANDBACK.md:79-80` left unwrapped** after the deletion ("never install the two night agents
from the development checkout. Once" / "authored, every armed plan's…"). Cosmetic; content is correct.

No other regression: `21e` as custodied is byte-identical to the report delivered at `/private/tmp/ref-295-delta-opus.keep.md`
(`diff` clean), and the diff adds no code, no test, and nothing outside `docs/`.

## Executed evidence

```
$ git -C <wt> log -1 --format='%ci' for 67cbf5fe 4a7a768c 4ac5d981 f9679fb4 ae8f074f b0c88632 a8cc6e68 2987a626
  9a15338e a6bff232 83b3ec5e dbd49c1d 0f3390c9 82622e70 277d719f
  00:57:32 01:02:02 01:05:11 01:05:39 01:10:44 01:11:22 01:20:08 01:20:19 01:48:16 01:48:47 02:01:16 02:03:37
  02:10:06 02:11:53 02:25:28   -> every "Timeline of record" git row at 21b:12-29 matches exactly      # N1 CURED

$ python3 zoneinfo America/Los_Angeles:
  1788854108 -> 2026-09-08 00:55:08 PDT ; 1788854721 -> 01:05:21 ; 1788855059 -> 01:10:59   # 21b:12,17,20 TRUE
  1788944160 -> 2026-09-09 01:56:00 = t0-3600 ; 1788945300 -> 02:15:00 = t0-2460 (t0 1788947760 = 02:56:00)  # N5
  1788859416 -> 2026-09-08 02:23:36 ; 1788859417.475615 -> 02:23:37     # pass2 transcript vs plan artifact  # N2

$ python3 field-diff of the two copied pass2 plans
  differing: ['chain_path', 'chain_sha256_path', 'custody_root']   EXACT MATCH to allowed set: True
  authored_epoch_s identical: True (1788859417.475615)
$ plutil -lint pass2-render-*.plist -> OK, OK ; ls -d /private/tmp/jw-bench-arm.AZAwVU -> No such file or directory
$ ls 21b-rehearsal-20260909-bench/ -> 3 pass-1 files (Sep 8 01:05) + 5 pass2-* files (Sep 8 02:23)          # N2

$ extract ```zsh blocks -> block0 21b:77-121 (historical), block1 161-227 (A), block2 242-278 (B)
  zsh -n block0/1/2 -> OK OK OK ; compile py0..py3 (4 heredocs) -> all "compiles OK"                       # N10

$ FAKE_NOW=<n> zsh guard.zsh   (block A step-0 window guard, verbatim, under mktemp -d)
  1788944159 ABORT rc=1 | 1788944160 PROCEED rc=0 | 1788944161 PROCEED rc=0 | 1788945000 PROCEED rc=0
  1788945299 PROCEED rc=0 | 1788945300 ABORT rc=1 | 1788945301 ABORT rc=1 | 1788947760 ABORT rc=1

$ ps -p <live pid> rc=0 ; ps -p 48645 rc=1 ; ps -p 999999 rc=1        # N11 guard: no false PASS

$ whitespace-normalized containment vs `git show main:docs/process/NIGHT_HANDBACK.md`
  4/4 sentences True on main and True on branch (installer sentence modulo its trailing ")"->".")
  branch counts: "Author every new v2 plan with"=1  "writer emits both"=1  "schema_version: 2"=1            # N6

$ sed -n '75,79p;114,117p;272,275p' 21b -> historical header + `exit 1` at :79, cure at :116;
  operative step 7 at :274 = `|| { print "ABORT: agent install failed"; exit 1; }` (unchanged)              # D1
$ grep -rn 16456 docs/ -> only 21b:234 (plus unrelated numeric hits)                                        # D3
$ diff /private/tmp/ref-295-delta-opus.keep.md 21e-delta-reaudit-fix-round-1-opus.md -> identical
```

VERDICT: **NOT LANDABLE** — blocker D1 (`21b:116` vs `21b:274`): the N4 un-publish cure was written into the
superseded historical block, which aborts on its own first line, while the operative amended step 7 still leaves a
published plan with no agents on an install failure — and the commit message asserts the cure. It is a
copy-of-one-line fix. N1, N2, N3, N6–N11 are cured and bench clean; N5 is enforced only on the non-arming half
(D2). D2–D4 should land with it.
