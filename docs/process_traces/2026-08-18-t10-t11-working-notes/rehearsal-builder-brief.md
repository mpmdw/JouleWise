# WO-REHEARSAL-ENV — scratch dress-rehearsal builder + operator card

You are Sol, working in a fresh worktree of JouleWise main (branch
`impl/rehearsal-env-builder`). Tonight the human operator (Ed) performs the
operator-qualification DRESS REHEARSAL: the full T-0 E-step sequence
(E-4 → E-9b) plus author → ARM → verify → consume, against SCRATCH custody —
never the real packs, never production roots. Your job is to make that
rehearsal executable with zero improvisation.

WRITE_SCOPE: ["scripts/ed_session/build_rehearsal_env.sh", "docs/process/rehearsal-operator-card.md"]
You may also write freely under $TMPDIR for smoke testing. Nothing else.

## Authorities (read these; they are the ONE homes)

- `docs/phase_2/window_runbook.md` — §4 (plan directory + window.env example,
  ~lines 150–245), the D-134 rehearsal section (~lines 260–360), §5C and the
  E-step sequence (~lines 741–1010), and the window-chain.zsh literal
  (~lines 1178–1390).
- `scripts/capture_t0_step.py` — the T-0 producer CLI (context loading,
  per-step contracts, refusal conditions). Note `_load_context`: the
  window-plan root MUST be inside the custody root.
- `scripts/author_arm_evidence_t0.py` — E-9b authoring.
- `scripts/generate_arm_readiness.py` — freeze / dry-run / ARM lifecycle.
- `scripts/launch_window.py` — consumption interface (what E-10 invokes).
- Pack with the RULED storage shape (`plan.path: "calibration_plan.json"`):
  `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1`. The two floor packs
  carry the superseded repo-relative spelling and the shared R2 resolver
  REFUSES them — do not use them as the rehearsal source. Confirm this
  refusal claim in code before relying on it; if the contrast pack is
  refused for a different reason, report NEEDS_RULING with the evidence
  rather than guessing.

## Deliverable 1 — `scripts/ed_session/build_rehearsal_env.sh`

A bash script (must run on macOS bash 3.2 under `set -euo pipefail`; guard
every possibly-empty array expansion) taking exactly one argument
SCRATCH_ROOT (an absolute path outside the repository). It constructs a
complete, self-consistent rehearsal environment under SCRATCH_ROOT:

- A scratch PACK_ROOT: a byte-faithful copy of the contrast pack directory
  (this is a COPY under SCRATCH_ROOT; the committed pack is untouched, which
  satisfies "never the real packs").
- The custody topology the runbook requires: ARM_READINESS_CUSTODY_ROOT,
  WINDOW_CUSTODY_ROOT (fresh-empty), QUARANTINE_ROOT as a SIBLING outside
  both custody roots, scratch RUNS_ROOT and BOUND_RUNS_ROOT, scratch backup
  dests (plain dirs under SCRATCH_ROOT — no iCloud).
- WINDOW_PLAN_ROOT at ARM_READINESS_CUSTODY_ROOT/window-plan containing:
  - `window.env` with EXACTLY the key set the runbook §4 example defines,
    every path absolute into SCRATCH_ROOT or the current checkout, no `$`
    or expansions in values. MEASUREMENT_REPO = the CURRENT repo checkout
    (/Users/edr/code/JouleWise) — verify from code whether any consumer
    additionally requires .venv there and note the finding. Also bind the
    E-10 keys the chain section requires (ARM_RECEIPT, LAUNCH_MANIFEST)
    if and as capture/author/launch code requires them; derive their exact
    expected paths from code, not guesswork.
  - `before_midpoint_stages.txt` / `after_midpoint_stages.txt` with valid
    stage lines for the contrast pack (derive from the pack's own config
    directories; exclude reference dirs per §4).
  - `waivers.json` containing `[]`.
  - `window-chain.zsh` extracted from the runbook literal, with the REPO=
    line set to MEASUREMENT_REPO and no other semantic change; emit its
    SHA-256 to a sidecar file.
  - `extraction_spec.json` if the plan-directory contract requires it —
    determine from code/runbook what shape satisfies the rehearsal.
- Any auxiliary inputs the E-steps actually load (identity-epoch.json,
  t1-bindings.json, ledger head pin, calibration ledger path...): determine
  from code which must PRE-EXIST vs which the steps create. For must-pre-exist
  scratch inputs, synthesize minimal valid scratch content and clearly mark
  provenance `rehearsal-scratch` inside the artifacts where schemas permit.
  If any input CANNOT be validly synthesized without privileged/live data,
  say so explicitly in the card at the exact step where it bites.
- Idempotence: refuse if SCRATCH_ROOT already exists (operator reruns get a
  clean slate by choosing a new dir or deleting the old one; print the exact
  rm command on refusal).
- End by printing a short manifest: every root created, the window.env path,
  and the next command (the operator card).

## Deliverable 2 — `docs/process/rehearsal-operator-card.md`

The literal command card Ed executes. HARD REQUIREMENTS: zero placeholders —
every command copy-pasteable byte-for-byte assuming
SCRATCH_ROOT=/Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal
(write that literal into every command); state expected output and the
likely refusal mode per step; sequence:

1. Build step (one command invoking deliverable 1).
2. E-4 clock-prior-state — including the interactive prior-state read Ed
   performs first and what the wrapper prompts for.
3. E-5 clock-disable (D-127 vector; sudo -n now works passwordless on this
   machine). Immediately after the rehearsal's final step the card must
   restore network time ON and verify (Network Time: On) — the card owns
   leaving the machine restored.
4. E-7a quiet-mac-prep, E-7b prewindow-check (state the 600 s dwell
   requirement and that ALL agent fleets must be stopped first; the card is
   executed in the post-21:30 quiet slot).
5. E-8 ledger-readiness, E-9a ledger-reservation.
6. E-9b author_arm_evidence_t0 with the 20-MINUTE volatile horizon warning
   in bold: after E-9b, no new processes; proceed immediately.
7. ARM + verify (generate_arm_readiness.py — derive the exact arm/verify
   subcommands and arguments from code).
8. Consume against scratch (the launcher route or the verify_consumed path —
   derive from code what a scratch-safe consumption invocation looks like;
   if true consumption requires the foreground chain, card the smallest
   honest consume the code supports and say what it proves).
9. Reset-for-retry block: the exact three-namespace rm -r from the runbook,
   adapted to the scratch roots, plus clock-restore.

## Deliverable 3 — smoke test (in $TMPDIR)

Run the builder against a $TMPDIR scratch root and execute the sequence as
far as possible WITHOUT privileges and WITHOUT toggling network time:
- E-4 CAN be smoke-tested: feed its interactive prompts via stdin with
  honest scratch values (fabricating scratch rehearsal inputs in your own
  $TMPDIR env is in-contract; you are testing wiring, not producing
  evidence).
- E-5 and anything sudo-bearing: DO NOT run sudo, DO NOT toggle the clock.
  Stop there and verify instead that the step's context loading and
  derivation reach the privileged boundary (e.g., by code reading or a
  refusal you can trigger unprivileged).
- Independently verify the scratch pack passes the R2 resolver and E-8's
  binding derivation (run whatever non-privileged step or helper proves it).
- Record in the final report exactly which steps were proven live in smoke,
  which were proven only to the privileged boundary, and which are
  unproven-until-Ed. The card must carry the same three-way marking per
  step (SMOKE-PROVEN / BOUNDARY-PROVEN / ED-FIRST).

## Report contract (claude-codex-report/v1 envelope, final message)

- What you built, the smoke results table (step → proven level → evidence
  file under $TMPDIR), every synthesized scratch input and why it is valid,
  any NEEDS_RULING items, and the exact commit SHA on the branch.
- Commit your two files on the branch with a clear message. Run
  `bash -n` on the builder and execute it at least twice (fresh dir,
  refusal-on-existing) as part of smoke.
- A missing/failed step in smoke that you cannot explain from code is a
  finding, not something to paper over.

## LEAD RULING (round 2 — resume from your NEEDS_RULING)

Your F1 ruling request is answered: **Option A adopted.** The builder
creates a full local clone (`git clone --no-hardlinks file:///Users/edr/code/JouleWise`)
at current main under SCRATCH_ROOT (e.g. SCRATCH_ROOT/measurement-repo),
and MEASUREMENT_REPO in window.env points at that clone. The clone's
committed GAMMA pack is the rehearsal PACK_ROOT. This satisfies "never the
real packs": the production checkout and its packs are untouched; the clone
is disposable. Option B (contract change) is REFUSED — no production
authentication surface changes for a rehearsal. Option C remains refused.

Consequences you must handle:

- F3 venv: the builder must provision SCRATCH_ROOT/measurement-repo/.venv.
  Determine the cheapest correct route from the repo's own setup files
  (requirements*/pyproject); prefer `python3 -m venv` + pip install from
  the local environment/cache. Verify `$CLONE/.venv/bin/python -c "import joulewise"`
  passes before declaring the build good. If provisioning is genuinely
  heavy (>10 min), make the builder print progress so the operator knows.
- Scratch main/origin refs: the clone naturally carries main + origin/main
  at the cloned commit — verify whatever E-4's terminal-review gate needs
  resolves in the clone. If the producer requires HEAD == a reviewed
  commit on main, the builder leaves the clone checked out on main.
- window.env exact key set: follow the CODE contract (the producer's
  enforced exact key set). ARM_RECEIPT / LAUNCH_MANIFEST are derived and
  exported post-ARM per your own residual-risk suggestion; the operator
  card carries the exact derivation commands at the right step. Record in
  the card that the runbook §window-chain wording ("window.env must
  additionally bind...") diverges from the enforced key set — flag only,
  do not edit the runbook (out of scope).
- All other requirements of the original work order stand, including the
  smoke ladder (SMOKE-PROVEN / BOUNDARY-PROVEN / ED-FIRST markings) and
  the operator card with SCRATCH_ROOT=/Users/edr/JouleWise-window-custody/ed-qual-20260817/rehearsal
  written literally into every command.
# LEAD RULING ROUND 3 (appended to wo-rehearsal-env-prompt.md before launch)

## Resolution of your round-2 F1/F2 (root-schema refusal)

**Successor-pack route adopted (your option 1).** No committed v1 pack can
complete the rehearsal (alpha/beta fail R2; gamma fails the enforced
roots.claim_root_leaf/bound_root_leaf schema at E-9b/ARM) and no production
authentication surface will be modified for a rehearsal. The Phase-2
transaction has now committed regenerated `_v2` packs with the enforced
schemas on branch `integration/phase2-transaction`.

Changes to the build contract:

- The scratch clone is taken from the LOCAL repo at that branch:
  `git clone --no-hardlinks -b integration/phase2-transaction file:///Users/edr/code/JouleWise <SCRATCH_ROOT>/measurement-repo`
  (exact commit SHA to pin: 28a0daa — verify the clone HEAD equals it).
- PACK_ROOT = the clone's `configs/campaigns/d117_floor_qwen25_1p5b_v2`
  (the ALPHA successor — rehearsing the exact family the real ALPHA night
  arms). Verify in smoke: R2 resolves its plan.path, the frozen plan
  carries the enforced root keys, and the D-134 freeze receipt
  (freeze-0002) is present and pinned by plan_tree.json.
- The operator card must record, in its header, that the rehearsal pack is
  the pre-publication successor from the transaction branch at the pinned
  SHA (qualification choreography evidence, not claim evidence).
- All round-1/round-2 rulings stand: Option-A full clone as
  MEASUREMENT_REPO; .venv provisioned in the clone and verified importable;
  window.env follows the CODE-enforced exact key set; ARM_RECEIPT /
  LAUNCH_MANIFEST derived and exported post-ARM with card-carried commands;
  runbook wording divergence flagged in the card, not edited.
- WRITE_SCOPE unchanged: ["scripts/ed_session/build_rehearsal_env.sh", "docs/process/rehearsal-operator-card.md"].

## LEAD RULING (round 4 — resume from your round-3 NEEDS_RULING)

Your options are adjudicated as a COMBINATION, honest at every step:

1. TERMINAL-REVIEW GATE: the rehearsal card makes the terminal-review
   commit an OPERATOR STEP — Ed personally reviews the scratch clone state
   and creates the terminal-review commit (with whatever trailers/refs the
   producer contract requires) INSIDE the scratch clone, exactly as he will
   on a real arm night. That is a genuine review of genuine scratch state —
   no fabrication. The "clone HEAD equals 28a0daa" pin is amended to: the
   clone STARTS at 28a0daa (verify), and the card records that Ed's
   in-clone terminal-review commit advances the clone's HEAD (record both
   SHAs in the rehearsal evidence). Scratch main/origin refs may be set to
   that reviewed commit by the CARD'S instructions as part of Ed's step —
   the operator sets them, not the builder.
2. LEDGER ROUTE: the clone's own committed calibration ledger + head pin
   (self-consistent committed state from the branch) IS the authorized
   rehearsal ledger — writes land in the clone, canonical state untouched
   (the same isolation-by-clone ruling the D-139 shakedown adopted
   tonight). No new code route; if reservation refuses against the
   clone's committed state for a reason you can demonstrate, capture the
   exact refusal in the card as a BOUNDARY-PROVEN stop with its meaning.
3. The card gains PART A — the D-134 dry-run (generate_arm_readiness.py
   dry-run per the runbook's own rehearsal section) against the frozen
   alpha _v2 pack in the clone with a scratch custody root: sanctioned,
   executes the real reservation CLI and production ledger-writer
   lifecycle. PART B = the E-4→E-9 wrapper walk + author→ARM→verify→
   consume per the original contract, with Ed's terminal-review step from
   ruling 1. Mark every step SMOKE-PROVEN / BOUNDARY-PROVEN / ED-FIRST as
   originally required.
4. Do NOT fabricate any production authentication record in the builder;
   everything the operator must personally do is a card step.

All other rulings stand (rounds 1-3). Deliver the builder + card + smoke
ladder + commit per the original contract.

## LEAD RULING (round 5 — final; resolves your round-4 F1/F2)

Your F1 is CONFIRMED and was general: freeze receipts authenticate their
absolute pack_root. The lead has RE-MINTED all three freeze-0002 receipts in
the durable designated measurement checkout
/Users/edr/JouleWise-measurement-20260818 (branch integration/phase2-
transaction; receipts now committed at head; _load_freeze_reference
VERIFIED to authenticate there end-to-end, predecessor chain included).
Consequences:

1. The rehearsal RUNS AT that measurement checkout — your builder's clone
   step is REPLACED by using /Users/edr/JouleWise-measurement-20260818
   directly (verify at build time: HEAD contains the freeze-0002 receipts
   and `git status` is clean; refuse otherwise). Scratch custody roots stay
   under SCRATCH_ROOT exactly as you built them. The builder still creates
   the venv IF that checkout lacks .venv (check; create it there — the real
   arm night needs it anyway).
2. F2 commit target: commit on the CURRENT branch of the worktree you are
   in (integration/phase2-transaction) — the impl/rehearsal-env-builder
   branch is retired; do not touch it.
3. Your two files exist untracked in this worktree from round 4 — amend
   them in place per ruling 1, re-run the smoke ladder against the
   measurement checkout (read-only + $TMPDIR scratch custody; no sudo, no
   clock, no privileged E-steps — same boundaries as before), update the
   card's SMOKE/BOUNDARY/ED-FIRST markings, and COMMIT.
All prior rulings stand.
