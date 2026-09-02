# COLD GATE RULING — E-10 vs a pack-less diagnostic night (D-169 stage 1, R-10)

Cold Fable, 2026-09-01. Read-only; every cite re-opened at HEAD (main).

## VERDICT: UPHELD-WITH-AMENDMENT (UPHELD for G2-a; REVERSED as to G2-b)

**(a) Does E-10, as written, bind a pack-less diagnostic night? NO — for G2-a.**
Deciding text, in order of weight:
1. Runbook scope line: "**Applies to:** claim-bearing Mac measurement windows after PR #85"
   (`window_runbook.md:7`). G2-a is "diagnostic and non-claim" (`SHAKEDOWN-G2-RUNSHEET.md:227`).
2. E-10 is defined by reference to things G2-a does not have: "after that inspection, Ed personally
   invokes the sole reviewed launcher exactly once" (`:1243-1244`); "that inspection" is the
   `PASS`/`GO` of `generate_arm_readiness.py verify --pack-root "$PACK_ROOT"` (`:1227-1234`); the
   launcher needs `$STEP6_CONFIRMATION_TABLE` and `hC` (`:1259`, `:1272`); the launcher itself
   binds pack custody (`scripts/launch_window.py:170-186`). "The pack does not exist yet and no
   G2-a gate may test `$PACK_ROOT`" (`RUNSHEET:228-229`). E-10 is not merely inapplicable to
   G2-a; it is unexecutable there — there is no launcher to invoke.
3. The G2-a section carries no `(ED PROMPT)` step; every ED PROMPT in the runsheet is in G2-b
   phases B–D (`:625, :646, :685, :702, :730`).

**But R-10 and R-4 misclassify G2-b.** R-10 says "G2-a and G2-b are diagnostic, pack-less windows"
and R-4's table files `DIAGNOSTIC_NO_PACK (G2-a, G2-b)`. The runsheet says the opposite: "G2-b —
evening before the transaction, real-pack one-block proof. The pack-existence gate begins here"
(`:527-529`); D1 is "launch the frozen chain exactly once (ED PROMPT)" running
`scripts/launch_window.py --pack-root "$PACK_ROOT" --arm-receipt … --step6-confirmation-table …`
(`:730-747`). That IS E-10, verbatim. G2-b is non-claim but pack-bound; E-10 binds it as written.
**REVERSED as to G2-b**: G2-b is a `TRANSACTION_PACK`-shaped night (stage 3 machinery) and stays
under E-10 until Ed amends it. Strike G2-b from the `DIAGNOSTIC_NO_PACK` row of R-4 and from R-10.

**(b) Permissible narrowing or Ed-only reversal? PERMISSIBLE NARROWING (G2-a only).**
- The fence's authoring ruling had only pack windows in view: it is the T-0 census design for the
  15-row arm ceremony; bench fact 5 cites E-10 at the pack launcher; the scope fence names "E-10's
  physical launch, D-127 clause 4's relaunch harness" and says "**production windows** depend on
  BOTH rows" (`MAGISTRATE-RULING-T0-UNATTENDED.md:29-31, :113-118`). A pack-less diagnostic
  evening did not exist as a concept until D-162/D-167 (08-28/09-01). "Any automated launch"
  therefore quantified over the launches that existed: pack launches via `launch_window.py`.
- The reservation's holder has spoken since: D-169 (Ed, adopted) — "why can't you do this? …
  so you can drive the experiments entirely"; "Ed-hands residue is limited to what rulings
  literally require — never per-window presence" (`decision_log.md:196`). D-167 cl.1 (Ed 08-28):
  "diagnostic windows at lead discretion" (`:194`). A magistrate fence cannot outrank Ed's own
  directive on his own reservation; reading the fence to still require his hand on a diagnostic
  night would invert the authority order.
- It is not silent absorption (the fence's actual prohibition, kernel `acceptance.summary`): the
  narrowing is written, cold-gated, and put to Ed by email with his NO overriding. That is the
  T0 ruling's own required shape ("amended by ratified runbook change, not silently absorbed").
- Amendment condition: the stage-1 email naming the first armed date must be SENT (Gmail, Ed's
  address) before the LaunchAgent is armed, and it must say in one sentence that the night launches
  without his hand under this carve-out unless he replies NO. D-149 cond. (2) (pack arm ceremony)
  is honestly `NOT_APPLICABLE`, not PASS — R-4's shape is correct and required.

**(c) Minimal kernel-row rewording** (`/tasks/UNATTENDED-LAUNCH-01/fences/0/rule`):
"Separate row by ruling: T0-UNATTENDED-01 owns evidence semantics only; this row owns process
lifecycle. Production (pack-bound) windows depend on BOTH. E-10 amendment is Ed-ratified before
any automated launch of a pack-bound window, G2-b included. A `DIAGNOSTIC_NO_PACK` night (G2-a) is
outside E-10's scope (runbook 'Applies to: claim-bearing', :7; RUNSHEET :227-229) and launches
under the night gate without Ed ratification; Ed's standing NO overrides. Authority: this fence's
ruling + MAGISTRATE-RULING-UNATTENDED-STAGE1 R-10 + cold gate coldgate-e10 (2026-09-01)."
Companion: `dependencies[0]` (T0-UNATTENDED-01, hard/start) gets `"scope": "start"` qualified
"pack-bound nights only; no T-0 producer runs in a DIAGNOSTIC_NO_PACK night" — same authority.

## (d) What I REFUSE to let run a live night until cured — with cites

1. **G2-b under `DIAGNOSTIC_NO_PACK` (R-4 table, R-10).** Refused outright: G2-b runs
   `launch_window.py` with a real pack and an arm receipt (`RUNSHEET:730-747`); an automated G2-b
   is exactly the launch the fence guards. Stage 2's "G2-b on the same machinery" (§3 row 2) is
   struck; G2-b moves to stage 3 or runs attended.
2. **Driver topology contradiction (R-2 item 2).** The driver "`execve`s the generated chain
   exactly once" AND afterwards "writes the result record, pushes the results branch, and launches
   the courier." After `execve` no driver code exists to do the latter. Before a live night the
   ruling must name the process that survives capture (a forking supervisor, a second launchd
   job on exit, or a chain-tail step), and that process must be shown NOT to trip the chain's own
   quiet predicates. Undefined topology = undefined census = no live night.
3. **Dead-man can breach the zero-agent fence (R-7).** The 07:00 entry "re-runs the courier step
   alone if `courier.sent` is absent." If the chain is still capturing at 07:00 (no ruled bound ties
   `window_max_s` to the dead-man hour), it starts `claude -p` DURING capture — the one fence the
   ruling declares unchanged (§0; D-127 §2). Cure: dead-man refuses while the chain pid/`chain.exited`
   marker shows the chain alive, and `t0 + window_max_s + courier deadline < 07:00` is a gate predicate.
4. **No launchd-path rehearsal is required (R-4 `REHEARSAL_STUB`, §3 row 1).** The stub rehearsal
   is ruled but not ruled to fire FROM the installed LaunchAgent. A `gui/501` job carries a minimal
   environment (PATH, python/venv, HF cache, git credentials for the results push, MLX). A live
   night whose first real launchd invocation is the live night is a rehearsal, not a night. Cure:
   at least one `REHEARSAL_STUB` fire via the installed plist, with the results-branch push and a
   delivered courier email as its acceptance evidence (R-7 promises email "before he wakes" and
   nothing yet proves a headless `claude -p` can reach Gmail from launchd).
5. **AC-power predicate missing (R-6, §7 item 5).** The definition requires "on AC power" (§0) but
   the listed gate predicates are load, HID idle, display, sleep settings; `pmset -g` reports the
   ACTIVE profile only, so a battery night both sleeps mid-window and measures the wrong thing.
   Cure: `pmset -g batt` "AC Power" is a night-gate refusal code.
6. **Results-branch push from the development checkout (R-7 durable record).** Committing to
   `night-results/<date>` by checking out a branch in `/Users/edr/code/JouleWise` moves HEAD, which
   R-6's `repo_head` check and any live worktree both depend on. Cure: plumbing (`commit-tree` /
   `update-ref`) or a dedicated worktree; never `git checkout` in the driver.

Not refused (noted): R-3, R-5, R-8, R-9, R-11, R-12 are sound as written; R-10's stage-3 request
for "that one sentence" from Ed is the right shape and the honesty clause's Ed-overrides rule stands.

Confidence: high on (a)-(c) and on d.1-d.3 (text-decided); medium on d.4-d.6 (implementation gaps
the stage-1 ruling leaves to WO-2 — refusals stand until the rehearsal evidence exists).
