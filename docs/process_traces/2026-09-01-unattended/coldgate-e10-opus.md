# OPUS CONTRACT-LENS REFUTER — R-10 (E-10 scope), D-169 stage 1

Read-only pass; every cite re-opened at the stated lines. I looked for text that
BINDS a pack-less diagnostic night to E-10/Ed-presence, and text that RELEASES it.

## (a) Does E-10 bind a pack-less diagnostic night? — **NOT REFUTED** (with one carve-out)

Binding candidates, all defeated by their own scope words:
- `window_runbook.md:7` — "**Applies to:** claim-bearing Mac measurement windows
  after PR #85"; `:14` "the practical procedure for collecting one claim window."
  The document E-10 lives in scopes itself to claim windows.
- `:22-24` "Do not run this procedure while any agent session is active. The
  operator owns the quiet machine…" — binds *this procedure*, inheriting :7.
- `:782-790` E-10's section is "**5C. D-117 manual arming** …"; "Arming happens
  only when the plan-bound GO record is green … and **Ed performs the physical
  steps himself**." Every operand is pack-family (D-117) arming.
- `:1340-1342` E-10's own text: "this E-10 command is a documented target
  procedure, **not current authority to launch**: every **D-117 physical launch**
  remains NO-GO…" — E-10 self-describes as governing D-117 pack launches.
- Position: E-10 is item 3 after `generate_arm_readiness.py verify --pack-root`
  (`:1227-1229`) and consumes `$STEP6_CONFIRMATION_TABLE` + `hC` (`:1246-1278`).
  None of those objects exists on a pack-less night; the step is not merely
  inapplicable in spirit, it is unexecutable in fact.

Releases I found that R-10 did not cite and that strengthen it:
- `SHAKEDOWN-G2-RUNSHEET.md:22-27` — G2's **Authority** imports
  `window_runbook.md:1372-1848` (the chain/display/bound/verdict sections). It
  does **not** import §5C (`:782-1371`), where E-1…E-10 live. The reviewed G2
  runsheet never adopted E-10.
- The runsheet marks each Ed-executed step "(ED PROMPT)": B1 `:625`, B2 `:646`,
  C1 `:685`, C2 `:702`, D1 `:730`. **Zero ED PROMPT markers in the G2-a section
  (`:225-486`).** The reviewed document already assigns G2-a no Ed act.
- `state_kernel.json` `/tasks/UNATTENDED-LAUNCH-01/goal` — "so **campaign
  windows** run without Ed's physical launch", and the runsheet `:227-228` says
  G2-a's runs root and log are "**neither a campaign input**, a mint input, nor
  reusable in G2-b." G2-a falls outside the fence row's own stated object.
- D-127 §1 (Ed, 08-08): "Claude Code drives the full experiment loop … → launch
  the supervisor → EXIT for the capture … **Ed's involvement reduces to
  optionally remote, or zero**." Ed's own charter contemplates agent launch.

**CARVE-OUT — R-10 is REFUTED as to G2-b, and so is R-4's class table.** R-10
says "G2-a **and G2-b** are diagnostic, pack-less windows"; the R-4 table row
reads "`DIAGNOSTIC_NO_PACK` (G2-a, G2-b)". The runsheet says the opposite:
`:529` "**The pack-existence gate begins here, and nowhere in G2-a. G2-b uses
the real** [pack]"; G2-b's Phase D1 (`:728-744`) is "**one physical launch**",
`launch_window.py --pack-root … --launch-manifest`, marked **(ED PROMPT)**,
after a `--pack-root` arm verify (C2, `:702`). G2-b is exactly the shape E-10
binds. Non-claim ≠ pack-less. Stage-plan row 2 ("G2-b on the same machinery",
ruling `:202`) would therefore run an E-10-bound launch unattended under a class
whose C2 is `NOT_APPLICABLE, basis no_pack_by_design`. That basis is false for
G2-b, which is the precise sin R-4 invokes against the Fable seat (`:229-231`).

## (b) Permissible narrowing, or an Ed-only reversal? — **NOT REFUTED** (narrowing), for the pack-less case only

The fence text is literally broad ("E-10 amendment is Ed-ratified before **any
automated launch**", `/tasks/UNATTENDED-LAUNCH-01/fences/0/rule`), but its
authoring ruling is narrower on the operative sentence:
`MAGISTRATE-RULING-T0-UNATTENDED.md:113-118` — "The *launch* blocker … is a
SEPARATE row, UNATTENDED-LAUNCH-01 … and **production windows depend on BOTH
rows**." The kernel row's authority pointer is that file, so the ruling governs
its own transcription. (The same ruling's work-order line `:146-148` says
"windows depend on it" unqualified — an internal ambiguity, which is why this
is a narrowing of an ambiguity rather than a reversal of a holding.)
Decisively: **a pack-less window was not in view on 08-23** — that ruling never
uses "diagnostic", "pack-less", "G2", or "shakedown"; the G2 runsheet is dated
08-28, D-167 09-01. Its fact 5 grounds E-10 in the runbook (`:29-31`), so the
fence inherits the runbook's claim-window scope. Narrowing a term to a case the
author never considered, on the author's own scope word, is interpretation.
It still had to come here: doctrine rule 11 makes "reinterpreting a prior
verdict" a mandatory cold-gate item, and the honesty clause routed it correctly.

## (c) Minimal kernel-row rewording — R-10's implied wording is INSUFFICIENT

`/tasks/UNATTENDED-LAUNCH-01/fences/0/rule`, replace the last sentence with:
"The E-10 amendment is Ed-ratified before any automated launch that consumes a
frozen pack — i.e. any launch preceded by `generate_arm_readiness.py verify
--pack-root` or invoking `scripts/launch_window.py` (runbook `:1227-1244`).
Pack-less diagnostic nights (no `$PACK_ROOT`, no arm receipt, no step-6 table)
are outside E-10 per runbook `:7` and `:1340-1342`; authority: 2026-09-01
stage-1 ruling R-10 + cold gate." Note the test must be **pack/launcher
consumption, not the word "diagnostic"** — G2-b is diagnostic AND pack-bound.
Leave `/acceptance/evidence/1` unchanged (acceptance, not a stage-1 gate) and
mark `/dependencies/0` (`T0-UNATTENDED-01`, hard/start) scope-limited to nights
that run a T-0 producer.

## (d) What I would REFUSE to let run a live night

1. **R-4 + stage plan, G2-b class (blocker).** As (a)'s carve-out: G2-b in
   `DIAGNOSTIC_NO_PACK` with basis `no_pack_by_design` is a false basis against
   runsheet `:529` and `:728-744`. Refuse any unattended G2-b until it has its
   own pack-bound class and the E-10 amendment. G2-a alone may proceed.
2. **C4 has no producer (blocker).** R-4 requires C4 (D-149's "boot-session and
   clock-discipline checks pass at T-0") **PASS** for `DIAGNOSTIC_NO_PACK`, but
   R-1 removes every T-0 producer from stage 1 (`:44-46`) and R-6 names only
   missed-fire/plan-staleness/HID guards. WO-1's contract (`:207-212`) cites
   R-3/R-4/R-6/R-8/R-11 and specifies no boot/clock probe. A PASS written for a
   condition nothing evaluated is the exact false record R-4 forbids. Either
   name the producer (boot-session UUID + a monotonic/realtime anchor recorded
   in the receipt) or mark C4 `NOT_APPLICABLE` with a registered basis.
3. **No once-only latch for D-078 (blocker).** C5 is "PASS required", and D-167
   cl.1 keeps "D-149 T-0 mechanical conditions (2)–(5)" as unchanged soundness
   fences. R-2 gives "`execve`s the generated chain exactly once" *within one
   driver process*; R-6's guard only refuses **outside** `[t0, t0+window_max_s]`.
   A driver crash or a launchd restart inside the window re-runs the chain and
   passes every stated guard — a silent re-arm-and-hope. Require a durable
   once-only marker (plan-id-keyed, `O_EXCL` in the night custody root) that
   refuses a second chain start, and pin the plist to no `KeepAlive` restart.
4. **D-167 cl.1's fence half is unaddressed (should-fix).** R-10 leans on cl.1's
   authorization half ("diagnostic windows at lead discretion") while R-4 sets
   C2 `NOT_APPLICABLE`; cl.1's closing sentence keeps D-149 (2)–(5) "unchanged"
   and cl.2 lists "G2-a probe evening" as a `_v5` row. Condition (2) is vacuous
   for a pack-less night, but the ruling should say so explicitly rather than
   leave a live decision-log sentence contradicting its own class table.
5. **§6 is an empty placeholder (should-fix).** "Sol seat (landed after this
   draft) — concurrence / dissent … _(filled in on harvest)_" (`:240-242`).
   Three-seat rule: a ruling whose third seat's concurrence is unrecorded is not
   a finished synthesis. Fill before stage 2, not before stage-1 code.
6. **Index-vs-body divergence on D-127, flagged and cleared.** The D-127 index
   row says the charter is "INSTALLED only at a deliberate Ed-present moment",
   which read literally would bind R-5's `install_night_agent.sh`. The body
   scopes presence to the privileged path only (§3, "Ed personally runs the
   single sudo install command"); the body governs, and R-5's install is
   `launchctl bootstrap gui/501`, no sudo. **Not** a blocker — but the index row
   should be corrected so it stops reading as a broader fence.
7. **R-3's predicate is substring-loose (nit).** `pgrep -lf "codex|claude|t3"`
   matches any command line containing "t3" (paths, `gpt3`, …). Fail-closed, so
   it costs a night not data; worth anchoring the alternation anyway.

**Verdict:** R-10 **stands for a pack-less G2-a night** and **fails for G2-b**;
the fence rewording must key on pack/launcher consumption, not on "diagnostic".
Items 1–3 must close before any live unattended night; stage-1 code is not
blocked. Confidence: high on (a)/(b)/(d)1–3 (each rests on quoted scope text),
medium on (c)'s exact wording.
