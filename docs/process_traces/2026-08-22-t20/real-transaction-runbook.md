# The real `_v4` freeze transaction — operator runbook

**Status: RULED, with two items still open — see §7.** D-155 (magistrate
synthesis, 2026-08-26,
`docs/process_traces/2026-08-22-t20/nr-synthesis-ruling.md`) rules eleven of
the thirteen §7 questions and this document now carries those rulings inline.
Still open: **NR-5** (whether the real lane re-runs the runsheet §4 probe
battery), and the **notification cadence** half of NR-9, which is Ed's
one-word question. Do not execute until both are closed **and** D-155 work
order W-2 — the two ruled code cures — is on the reviewed head.

This is the procedure for the one session where Ed is at the machine and the
`_v4` freeze transaction actually happens. It is the operator-facing companion
to `s0-runsheet-r4.md`, which is the *rehearsal* instrument. The rehearsal ran
end to end with zero failures at estate 10 (`S0-COMPLETION-RECORD.md`); this
document is what that rehearsal was a rehearsal *of*.

Two rules govern how to read it.

1. **The runsheet owns the commands; this document owns the sequence, the
   people, and the clock.** Where a step exists in the runsheet, this document
   names the runsheet section and states only what changes in the real lane. It
   does not restate command text that has already been proven, because a second
   copy of a command is a second thing that can drift.
2. **Every difference from the runsheet is stated inline, at the step it
   affects.** The rehearsal ran inside a throwaway clone with a forged remote
   reference; the real transaction runs on the real repository with real
   published references. Those differences are not cosmetic — three of them
   change what a step can even do — so each one is called out where it bites.

Section 7 lists the questions the sources do not answer. **Those are blockers.**
Finding them before the session, rather than at the machine with a person
waiting, is the main reason this document exists.

---

# 0. The vocabulary, built before it is used

Everything below is used in the procedure. Read this section once; the
procedure assumes it.

**A pack.** A *campaign pack* is one directory under `configs/campaigns/`
holding everything needed to run one measurement campaign: the plan
(`plan_tree.json`), the generated science configurations, and the evidence
directories the readiness machinery writes into. There are three `_v4` packs,
and the transaction handles all three together:

| Profile | Pack root | Predecessor (`_v3`) |
|---|---|---|
| ALPHA | `configs/campaigns/d117_floor_qwen25_1p5b_v4` | `…_1p5b_v3` |
| BETA | `configs/campaigns/d117_floor_qwen25_7b_v4` | `…_7b_v3` |
| GAMMA | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4` | `…_vs_7b_v3` |

The profile names ALPHA/BETA/GAMMA come from the row registry
(`configs/arm_readiness/d117_row_registry_v2.json`,
`freeze_evidence_lifecycle.successor_policy.successor_pack_ids`). The three
packs together are the **`_v4` family**; `_v3` is the previous **generation** of
the same family.

**A freeze.** Two different operations in this transaction are called
"freezing", and confusing them has already cost one estate.

- **The identity-pin projection ("U11").**
  `scripts/project_identity_pins.py freeze <pack root>` reads the model weight
  files the pack declares, hashes every one of them, and writes
  `identity_pin_projection.receipts/projection-0001.json` inside the pack. Its
  purpose is to record *exactly which bytes of model weights* this campaign will
  run against. It has to load the MLX runtime to resolve the backend, so it is
  the one step that needs the measurement environment and the one step whose
  wall clock is measured in minutes rather than seconds.
- **The readiness freeze ("freeze-0004").**
  `scripts/generate_arm_readiness.py freeze --pack-root … --predecessor-pack-root …`
  writes `arm_readiness.freeze.receipts/freeze-0004.json`, the receipt that says
  this pack's plan and evidence are sealed. `0004` is the ordinal: `_v3` carried
  `freeze-0003`. The receipt path is **create-only** — the code will not
  overwrite one — and the receipt is **plan-pinned**, meaning the plan tree
  records the receipt's digest, so a receipt that was written cannot be quietly
  replaced by a better one later.

**Evidence stamping.** `scripts/author_arm_readiness_evidence.py --pack-root <pack>`
writes eleven *generic receipts* per pack — one per readiness question the
registry declares applicable (`ACCEPTANCE_OWNER`, `DOCTRINE_PIN`,
`ESTIMATOR_IDENTITY`, `MINT_TRUST`, `MULTICELL_MINT`, `PACK_AUTHENTICATION`,
`PACK_FAMILY`, `REASON_CODE_COVERAGE`, `RECEIPT_ORACLE`,
`RECOVERY_LEDGER_TEST`, `THREE_WINDOW_REGRESSION`). Three packs × eleven kinds =
**33 receipts**. Each receipt records the *boot session identifier* of the Mac
that produced it, derived by the code from `sysctl -n kern.bootsessionuuid` —
callers cannot supply it. **A reboot after this step voids all 33 receipts**
(`joulewise/arm_readiness_evidence.py` compares `receipt["boot_session_id"]`
against the current boot on every subsequent read), and the only cure is to
author them all again. This is why the reboot in §2 Phase B happens where it
does and never later.

**The changed-set gate (also "R1").** Before the readiness machinery will let a
pack be armed, it lists every repository path that changed between the commit
where the evidence was derived and the commit currently checked out, and it
refuses if anything on that list is not accounted for. The accounted-for list is
the registry's `irrelevant_path_allowlist`, and for this transaction it holds
**exactly 112 paths**: 37 per pack (11 evidence sources + 11 evidence receipts +
11 receipt sidecars + `freeze-0004.json` + its sidecar + `plan_tree.json` + its
sidecar) × 3 packs = 111, plus one more described next. The arithmetic is
`3 × 37 + 1 = 112` and it is generated, never typed
(runsheet §2.1).

**The successor pinset, and the digest-conditional 112th path.** The historical
semantics verifier reads a *pinset*: a JSON file listing, for each governed
pack, the digests that pack's frozen receipts must have. The `_v1` pinset covers
the nine older packs and is immutable. `_v4` mints a **successor**,
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json`, holding three
rows (one per `_v4` pack, 33 receipts total). That successor path is the 112th
allowlist entry — and it is the only entry the gate subtracts *on a condition*
rather than on membership alone. The condition is described next.

**The marker `M`, the table `C`, and the two digests `hM` and `hC`.** Two small
files outside the repository authenticate the publication:

- the **family-publication marker** `d117_family_publication_v4.json` — the
  family's birth certificate, built at the freeze boundary. Its SHA-256 is
  `hM`.
- the **step-6 confirmation table** `d117_step6_confirmation_table_v4.json` —
  one file naming `hM` in its `family_publication` section and the successor
  pinset's SHA-256 (`hS`) in its `successor_pinset` section. Its SHA-256 is
  `hC`.

The only digest edges are `C → M` and `C → S`; neither the marker nor the pinset
names the table, so the graph has no cycle. **This ordering is forced, not
stylistic:** `C` contains `hM`, so `C` cannot be rendered until `M` exists. That
is why the marker is built first and the table second, and why the marker
*build* is structurally unable to check the `C → S` edge — it discloses that it
deferred the check instead (`conditional_paths_deferred` in the marker's own
bytes). Authority: `docs/contracts/d117_step6_confirmation_table.md`, the ONE
home for this artifact.

**`hC` is supplied out of band.** "Out of band" means: every consumer that
enforces the `C → S` edge is handed `hC` through its own explicit
`--expected-confirmation-digest` argument, from transaction custody, *never*
read out of the table it is checking and never stored at any repository path. A
consumer not given `hC` refuses; it performs no subtraction and authorises no
publication. The successor pinset path is subtracted from the changed set only
when `hC` matches the table's bytes **and** the table's `successor_pinset.sha256`
matches the bytes committed at the head under test.

**Transaction custody.** A directory *outside* the repository holding the
marker, the table, `hC`, and every command transcript. It is outside the
repository on purpose: an authenticator stored inside the set it authenticates
could be replaced together with its subject (D-151's fixed-point rule — no
authenticator path ever enters any allowlist, in any transaction).

**The commit freeze, and what "window close" means.** From the terminal-review
attestation onward — step C11, executed by the magistrate under D-150b — **no
ordinary commit lands on `main`** — not from this machine, not from any other
session, not from a status script. A sentinel file created in transaction
custody at C11.1 is what makes the status publisher honour that rule
mechanically rather than by memory. The freeze runs through the
*last consuming measurement window* of the campaign, which may be a week away.
D-153 A1 fixes the vocabulary: **"window close" means the close of that commit
freeze**, not the mint and not the end of any single night's measurement. The
mint-side event has its own name, **allowlist-contract closure**, at the commit
called `PINSET_MINT_HEAD`.

**Two heads, and they are different commits.** `PINSET_MINT_HEAD` is the
allowlist-contract closure head and the commit whose bytes `hS` is computed
from. `ATTESTATION_HEAD` is the terminal-review attestation commit made
immediately after it — empty, tree-preserving, and **the head that gets
published**. Every step below that names "the head" says which of the two it
means. Both names are used from §2 Phase C11 onward.

**Fixation.** The first commit *after* the commit freeze closes. It carries
exactly one change: the successor pinset's SHA-256 (`hS`) as a literal in
`tests/test_receipt_histsem.py`, plus its loud-fail guard. Nothing else. It
therefore **does not happen in this session** — see §6.

**Four-way equality.** Several steps call `reviewed_main()`
(`joulewise/arm_readiness.py`), which passes only when, in the checkout being
consulted, `HEAD == refs/heads/main == refs/remotes/origin/main` *and* the
working tree is clean. This single predicate is the reason several of the
real-lane orderings differ from the rehearsal, and it is called out each time.

**A permission prompt.** The Claude Code harness refuses to run certain command
classes without an interactive approval. Under D-150(1) Ed granted the mint
license in its most literal form: **live prompts at Ed's hands, approved at
execution time**, rather than a standing `settings.local.json` allow-rule. Each
prompt names the exact command line and waits. **Declining a prompt is always
safe** — the command has not run and nothing has mutated.

---

# 1. Preconditions

Every box must be checked *before* Ed sits down. Anything unchecked here becomes
a stop at the machine.

## 1.1 The machine and the checkout

- [ ] **The declared measurement checkout is named and recorded.** The
  measurement checkout is the working copy the transaction commits into; every
  repository-relative path resolves from it. Its name is `MEASUREMENT_REPO` in
  `docs/phase_2/window_runbook.md` §1. **RULED (D-155, NR-1): it is
  `/Users/edr/JouleWise-measurement-20260813`**, fast-forwarded to the reviewed
  head. It is already the literal in the window runbook §1, in the `window.env`
  template, and in the §5C producer, so choosing it edits nothing.

  Its head `49dcc49` was verified to be an **ancestor** of the reviewed head —
  meaning the reviewed head can be reached from `49dcc49` by following commits
  forward, so the checkout's history is a prefix of the reviewed history and
  contains nothing the reviewed head does not (`git merge-base --is-ancestor`
  exits 0). That is what makes a **fast-forward** available: moving the branch
  pointer forward to the reviewed head, with no new commit created and no
  content combined, so the resulting tree is byte-identical to the reviewed one.
  `git fetch origin && git merge --ff-only origin/main` on a clean tree is
  therefore sufficient, and `--ff-only` makes it refuse rather than silently
  create a merge commit if the ancestry claim were ever false.

  `/Users/edr/JouleWise-measurement-20260818` is **rejected** on three grounds,
  the third of which is mechanical and decisive: it is not on `main`; its
  virtual environment is twenty lines out of lock; and
  `.claude/settings.local.json` carries a blanket
  `Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)` allow rule, which
  would *suppress* the live permission prompts that D-150(1) chose as the
  operational form of the mint license. Running the transaction there would
  silently remove Ed's approval step.

  **Named fallback:** a fresh `-2026MMDD` checkout, if and only if the venv
  relock below cannot reach the lock (see the next box). That discovery belongs
  to the pre-window worklist, never to the bench.
- [ ] **That checkout is on `main`, at the reviewed green head, with a clean
  tree, and `origin/main` fetched to the same commit.** All three references
  must agree — this is the four-way equality predicate, and several later steps
  refuse without it.
- [ ] **The reviewed green head is CI-verified by the conclusion field.**
  `gh run view <id> --json conclusion` — never `gh run watch` exit codes, never
  absence of failure lines in a partial transcript. This rule is not pedantry:
  errata E-1 in this directory records a false "SUCCESS" entered into the
  permanent record by exactly that mistake.
- [ ] **That head contains none of the `_v4` output.** No `_v4` pack roots, no
  successor pinset. Runsheet §1.1's `$BASE` gate checks this mechanically and
  should be run verbatim against the measurement checkout.
- [ ] **The measurement virtual environment matches
  `env/mac-measurement-lock.txt`, proven by an empty diff.** As of 2026-08-25
  the `-20260813` checkout's `.venv` is out of lock in twenty-two lines, not
  one: thirteen packages are *newer* than their pin (`transformers 5.15.0`
  against the lock's `5.12.1` among them), three the lock names are *absent*,
  and the rest differ otherwise. Reconciling it is a `pip` operation in a
  measurement environment, which is Ed's hands, and it must be settled before
  the session.

  **Why this matters even though nothing refuses on it.** No gate in the
  readiness machinery reads the venv's package versions. What does read them is
  the record: `joulewise/identity_pins.py` stamps `runtime_version` into every
  projection receipt, and `scripts/make_figures.py` hardcodes
  "MLX 0.31.2 / mlx-lm 0.31.3" into the figure metadata. An out-of-lock run
  passes every runsheet guard, hashes byte-identical model weights, and
  publishes receipts whose recorded runtime contradicts the paper's own
  caption. The failure is silent and lands in the paper, which is why the gate
  here is a byte-level diff rather than a version glance.

  **The relock method (RULED, D-155 operator fixes): rebuild the environment,
  do not patch it.** A constraints file (`-c`) neither downgrades an installed
  package nor installs one that nothing requires, so patching the existing
  `.venv` cannot close a twenty-two-line drift. Ed's hands, at
  `/Users/edr/JouleWise-measurement-20260813`:

  1. `mv .venv .venv.pre-v4` — the old environment is preserved, so rollback
     costs one `mv` back.
  2. `python3.13 -m venv .venv` — a fresh, empty environment.
  3. `.venv/bin/python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"`
     — the lock header's own canonical form. Constraints do the job here
     precisely because nothing is installed yet: every dependency the editable
     install pulls is resolved *at* its pinned version rather than being
     downgraded afterwards.

  **The acceptance gate is the empty diff, not the version print** (MAGISTRATE,
  read-only, transcript into transaction custody):

  ```sh
  .venv/bin/python3 -m pip freeze --exclude-editable | sort > /tmp/have.txt
  grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort > /tmp/want.txt
  diff /tmp/want.txt /tmp/have.txt        # MUST be empty; exit 0 is the gate
  ```

  `/tmp/want.txt` must be **37 lines**. A version print
  (`python 3.13.1`, `mlx 0.31.2`, `mlx_lm 0.31.3`, `transformers 5.12.1`) is a
  cheap smoke check and is worth recording, but it is not the acceptance — one
  package can match while twenty-one do not.

  **Fallback rule.** If any pinned wheel cannot be obtained — `mlx-metal==0.31.2`
  is the plausible one — **stop; do not accept a partial lock.** Fall back to
  the fresh-checkout branch named in the checkout box above, which builds its
  environment from the lock by construction. This is the one discovery that
  changes the checkout ruling, which is why the relock runs early in the
  pre-window worklist (D-155 W-1) and not on the night.
- [ ] **`WINDOW-STATUS-FREEZE-GUARD-01` has landed — and it must land before
  Phase C1, not merely before the attestation.** `scripts/window_status.sh`
  currently commits *and pushes* `WINDOW_STATUS.md`, a path outside the 112. A
  single status publication inside the freeze span both breaks the commit freeze
  and adds changed-set residue that will refuse every subsequent arm.

  **RULED (D-155, NR-13): a code guard, and the binding deadline is the
  changed-set window, not the freeze span.** The guard's own files —
  `scripts/window_status.sh` and its regression — are not among the 112
  allowlisted paths, and the changed-set window opens at
  `EVIDENCE_DERIVATION_HEAD` (D-153 A6). Landing the guard after that head makes
  it residue and refuses every arm. So it lands **before Phase C1**.

  The ruled shape is a guard, not a removal: a sentinel file **outside the
  repository** (default `/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN`,
  path overridable by an environment variable for tests). When the sentinel is
  present, the script writes `WINDOW_STATUS.md` locally and exits 0 *before* it
  reaches `git add`, printing that the freeze span is open and the status was
  written locally rather than published. Out-of-span behaviour is byte-identical
  to today's. The sentinel lives in custody rather than at a repository path
  because a repository-path sentinel would itself be changed-set residue — the
  exact hazard being guarded against.

  This withdraws nothing Ed was promised: D-150a's committed visibility channel
  is the push notification to Ed's phone (§4 below), not the git push, and
  `WINDOW_STATUS.md` is still written locally under the guard.

  Landing vehicle: D-155 work order **W-2**, the one code PR, together with the
  NR-11 trailer cure. The kernel row stays open until that PR merges.
- [ ] **Disk headroom.** The transaction writes small artifacts, but runsheet
  §3.5's sacrificial pre-mint check clones the measurement checkout (~650 MB
  today). Confirm several GB free.

## 1.2 Quiet configuration — and what "quiet" does *not* mean here

**This session is not a `[QUIET-MAC]` measurement window.** No power measurement
occurs; no campaign runs; no display-sleep ceremony applies. The rules of
`docs/phase_2/window_runbook.md` §1 govern the *windows that follow*, not this
session. Runsheet §1.2 is explicit that no dry-run, launch, measurement, or
quiet-Mac command may occur here at all.

What *does* bind:

- [ ] **The fleet is quiesced for commits and pushes, not for CPU.** From the
  moment the freeze span opens, no other Claude session, Codex session, cron
  job, status script, or other machine of Ed's may commit or push to
  `origin/main`. D-150a item 7 makes this explicit, Ed's other machines
  included.
- [ ] **No reboot from Phase B onward.** D-150a grants an open-ended no-reboot
  span beginning at the pre-campaign reboot and running through campaign close.
- [ ] **Nothing else is mid-flight in the measurement checkout.** No branch
  checked out other than `main`, no stash, no in-progress rebase.

## 1.3 The D-150a reboot

- [ ] **Ed reboots the Mac immediately before the transaction band, and the boot
  session identifier is recorded.** D-150a's rationale: fresh uptime headroom,
  clearance of accumulated state (a two-core orphan leak survived fourteen days
  and was killed on 2026-08-23), a clean boot identifier to pin, and a Codex
  server restart as a side effect.
- [ ] **The reboot precedes the U11 freezes, not merely the evidence stamping.**
  D-150a says "immediately before the real transaction's evidence stamping". The
  evidence stamping is where the boot binding *bites*, but placing the reboot
  earlier is strictly safer and costs nothing: one boot session then covers the
  entire band. Placing it later is a defect, because the 33 receipts would be
  voided by it.

## 1.4 What Ed needs open

- [ ] One terminal at the measurement checkout.
- [ ] The Claude Code session driving the transaction, in the foreground, so its
  permission prompts are visible the moment they fire.
- [ ] The notification channel for the D-150a visibility protocol (push
  notifications at every state change).
- [ ] Nothing else. Browser automation, the Codex pet, periodic monitors, and
  any other agent session are closed — not for measurement cleanliness, but
  because any of them can commit.

## 1.5 What the magistrate needs prepared, at the desk, before Ed arrives

- [ ] Transaction custody root created outside the repository, empty.
- [ ] The mechanical candidate manifest generated from committed bytes at the
  reviewed head (runsheet §1.3) and its digest recorded. **This step survives
  NR-4's ruling and is still required** — step C9 authenticates each executing
  custody tool against the digest this manifest records for its path. What NR-4
  removes is the *marker's* consumption of it: neither the marker build nor the
  marker verify passes `--candidate-manifest`.
- [ ] The custody tools materialised and hashed (runsheet §2.1's allowlist
  contract checker, §2.2's census checker).
- [ ] The anchor map re-checked 15/15 against the reviewed head (runsheet §1.1's
  anchor block). A drifted anchor is a precondition defect: stop, re-derive on
  `main` through the review lane.
- [ ] The registry-v1 literal sweep run and every hit classified (runsheet §1.3).
- [ ] **The full-suite wall clock measured on a scratch checkout.** See §3 — it
  is plausibly the longest single step in the session and nothing in custody
  records it.
- [ ] **The prompt inventory delivered to Ed** (RULED, D-155, NR-10; work
  order W-6). Enumerate every command this runbook issues in Phases A–H,
  predict prompt / no-prompt against the harness's effective allow rules, and
  hand Ed a table with the exact command strings and the exact expected prompt
  count *before* he sits down. Each command lands in one of three classes:
  **ALLOW** — an allow rule matches, so the command runs with no prompt and Ed
  sees nothing; **ASK** — no allow rule matches, or the harness classifier
  blocks the command class outright, so a prompt fires and waits for Ed's
  approval; **DENY** — the command must not run in this session at all, and is
  listed so that a prompt for it is recognised immediately as a defect. Where a prediction is
  uncertain, run a harmless `--help` variant **of the same spelling in the same
  working directory** and observe the actual behaviour.

  Two mechanical facts make this a real step rather than a formality. First,
  whether a command prompts is a function of its *invocation form*, which the
  magistrate controls: `.claude/settings.local.json` allows
  `Bash(python3 scripts/*)` and `Bash(.venv/bin/python3 scripts/*)` — both
  **relative-form** patterns — and carries no rule at all for
  `-20260813`. A command issued from a working directory already set to the
  measurement checkout, in bare relative form, matches those rules;
  `cd /Users/edr/JouleWise-measurement-20260813 && …` matches nothing and
  prompts. Second, **the spelling trap**: the allow rule names
  `.venv/bin/python3` while older runbook text says `.venv/bin/python`. Same
  interpreter, different literal string, different outcome. This document uses
  `.venv/bin/python3` throughout for that reason.

  The consequence Ed must see: those broad allows could *swallow* a licensed
  freeze command, silently removing the prompt that D-150(1) chose as the
  operational form of the mint license. If the inventory shows that, **Ed
  narrows the rules with his own hands.** No agent modifies permission
  settings, and any tracked permission edit lands before evidence derivation.
  Adding a standing settings rule instead of prompting is *not* available:
  D-150 declined that form in terms.
- [ ] **The venv relock verified** by the empty-diff gate in §1.1, with the
  transcript and the lock file's SHA-256 in transaction custody (work order
  W-1). This runs first of everything, because its failure changes which
  checkout the transaction uses.
- [ ] **Freeze-span sentinel guard ARMED** *(D-155 amendment, 2026-08-26)*: with
  the sentinel file present at its custody path, run `scripts/window_status.sh`
  once and require the literal line `freeze span open: status written locally,
  not published.` on stdout. A mistyped sentinel path or a missing custody
  directory leaves the guard silently off; the assertion is the observed line,
  not the file's existence.
- [ ] The D-150a announcement sent: transaction open, push freeze ON.

---

# 2. The sequence

Each step names **WHO** performs it. Three actors appear:

- **Ed** — physically at the machine; reboots, approves permission prompts, does
  not interfere.
- **MAGISTRATE** — the session driving the transaction: issues commands, reads
  transcripts, executes the delegated step-6 comparison, decides when to stop.
- **SCRIPTED** — a command block from the runsheet, run verbatim against the
  measurement checkout, whose assertions decide pass/fail without judgement.

**Under D-150b, Ed does *not* adjudicate digests.** Ed ruled on 2026-08-23 that
the step-6 exact-byte confirmation and the terminal review are **delegated to
the magistrate**, executed as mechanical comparisons with independence preserved
— every digest independently recomputed from the artifacts, never accepted from
the producing session's report. The confirmation table keeps `authority: "ED"`
and its `statement` field records the standing delegation and the recomputation
evidence; Ed is *notified* after execution rather than blocked on it. **Ed's
remaining hands-on items are exactly three: the pre-campaign reboot,
non-interference during window nights, and the permission prompts.** (This
contradicts the widely-carried assumption that Ed types a YES over `hC` in this
session. The step-6 contract's own prose has now been amended to record the
delegation — see D-155's amendment to
`docs/contracts/d117_step6_confirmation_table.md` — so an operator reading the
ONE home no longer waits for Ed. What is still Ed's on that event is the
notification cadence; see §7 NR-9.)

---

## Phase A — Desk preflight (MAGISTRATE, before Ed arrives)

| Step | Runsheet | Real-lane difference |
|---|---|---|
| A1 | §1.1 `$BASE` gate | Runs against the measurement checkout's `HEAD`, not a clone's. There is **no throwaway estate and no clone** — the transaction commits into the real working copy. |
| A2 | §1.1 anchor block | Unchanged. |
| A3 | §1.3 manifest generation | Unchanged in mechanism; the output lives in transaction custody rather than an estate `$INPUT`. |
| A4 | §1.3 registry-v1 sweep | Unchanged. |
| A5 | §2.1 / §2.2 tool materialisation | Unchanged. |

**Removed as S-0 scaffolding:** the proof estate, the `git clone --no-local`, the
stdlib-only estate virtual environment, and every
`git update-ref refs/remotes/origin/main` in the runsheet. In the real lane
`origin/main` is a real remote-tracking reference that moves only when something
is actually pushed.

**Added for the real lane:** everything runs under the **measurement checkout's
own `.venv/bin/python3`**, not a stdlib-only interpreter. Spell it
`python3`, not `python`: the two names are the same interpreter inside a
virtual environment, but the harness's permission rules match on the literal
string, and only the `python3` spelling is named by an allow rule (D-155,
NR-10). The rehearsal's
two-interpreter split existed to prove that no hidden dependency had crept in
and to avoid installing anything; the real transaction has no such need, and
using the measurement environment throughout is what discharges the rehearsal's
one open caution (runsheet §7 O-5: live arm-side U11 re-verification is proven
by the real transaction in the measurement environment, and by nothing S-0 did).

---

## Phase B — Reboot and pin (ED)

| Step | Who | What |
|---|---|---|
| B1 | MAGISTRATE | Send the D-150a state-change notification: transaction open, push freeze ON. |
| B2 | **ED** | Reboot the Mac. |
| B3 | MAGISTRATE | Record `sysctl -n kern.bootsessionuuid` into transaction custody, before any transaction command. |

From B2 until campaign close there is **no reboot**. If one happens after
Phase C step C6, the attempt is over — see §5.

---

## Phase C — The scripted band (MAGISTRATE drives; ED at the machine for prompts)

This is runsheet §§3.1–3.7 executed against the real checkout, plus one step
the runsheet does not have: **C11**, the terminal-review attestation, which
D-155 ruled to the end of this phase. Ed's presence is required through C10,
because the six permission prompts fire inside C3 and C8; C11 needs no prompt,
so Ed may leave once C10 is recorded.

### C1 — Emit the three `_v4` pack roots (SCRIPTED, runsheet §3.1)

Each `_v3` generator is run with `--pack-id <the _v4 id> --family-suffix _v4
--no-preserve-current-frozen-bytes`, then all three roots are committed in one
commit. Expected: 100 science configs per pack, plan hashes printed, no evidence
and no `freeze-0004` yet.

*Real-lane difference:* the commit lands on `main` in the measurement checkout.
It is **not** pushed. Nothing is pushed until Phase D.

### C2 — Gate the runtime environment (SCRIPTED, runsheet §3.2a)

Records interpreter path, Python version, `mlx_lm` and `transformers` versions,
and asserts that `import joulewise` resolves inside the measurement checkout and
nowhere else. Then checks that every model weight file the `_v3` projection
receipts declare is present at its recorded size.

*Real-lane difference:* the "clone-first import assertion" becomes a
**checkout-first** assertion. The property is the same — the code under test must
be the code in this working copy — but there is no clone to be first.

`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` are set for every U11 command.
Reading `/Users/edr/jw_models` read-only to hash weights is permitted.

### C3 — U11 identity-pin projection ×3 (SCRIPTED + **ED PROMPTS 1–3**, runsheet §3.2b)

**Run one pack at a time, in its own shell, and do not begin the next until the
previous one's commit exists.** The per-pack `freeze → assert → commit`
interleave is not a style choice: the readiness code mints a whole-tree Git
anchor on every projection, and a tree left dirty by the previous projection
makes the next one refuse `readiness_identity_environment_dirty`. This was found
by real execution at estate 1, after the first-ever live U11 freeze passed and
the second refused.

**PROMPT 1** — Ed will be asked to approve, verbatim:

```
.venv/bin/python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
```

Issued with the shell's working directory **already at** the measurement
checkout, in exactly this bare relative form — not as
`cd /Users/edr/JouleWise-measurement-20260813 && …`. The interpreter must be
the measurement environment's, because this command loads the MLX runtime to
resolve the backend; and the spelling must be `python3`, because that is the
literal the harness's allow rule names (D-155, NR-10). The exact strings Ed
will see are the ones in the W-6 prompt inventory, produced before the
session.

**PROMPT 2** — the same command for
`configs/campaigns/d117_floor_qwen25_1p5b_v4`.

**PROMPT 3** — the same command for `configs/campaigns/d117_floor_qwen25_7b_v4`.

Authority for the prompt form: D-150(1) (live prompts at execution time, no
settings rule); the exact blocked command classes are recorded in
`docs/process/ed-s5-mint-decision-2026-08-19.md`, which is the `_v3` precedent
where the same classifier fired. **Whether commands beyond these two classes
also prompt is unresolved — see §7 NR-10.**

After each pack: assert `status: PASS`, `mutated: true`, empty `reason_codes`,
that `projection-0001.json` and `projection-0001.sha256` exist (that sidecar
drops the `.json`, unlike every other sidecar in this transaction), and that the
tree is clean after a pack-scoped `git add`. A dirty tree after the commit means
the projection wrote outside its own pack — stop there, where the cause is
named.

**Exit code 134 is not a retryable failure.** It is the MLX abort firing outside
pytest. Stop and escalate; never retry.

### C4 — Post-conditions and the derivation head (SCRIPTED, runsheet §3.2c)

Asserts exactly three per-pack commits exist; re-asserts checkout-first import
*after* the mutation; compares every `_v4` weight digest against the committed
`_v3` receipt's digest for the same resolved path (this is the real proof that
the same weight bytes were hashed, deferred from a pre-condition to a
post-condition so several gigabytes are not hashed twice). Records
`EVIDENCE_DERIVATION_HEAD` = the head after the third commit.

### C5 — Terminal common-head gate (SCRIPTED, runsheet §3.3)

Asserts `HEAD == EVIDENCE_DERIVATION_HEAD`, a clean tree, and that the manifest
declares exactly the two test modules the step then runs
(`tests.test_arm_readiness_schemas`, `tests.test_receipt_histsem`). Both must
pass before any evidence is authored.

### C5b — (MOVED) the terminal-review attestation is now step C11

**RULED (D-155, NR-12): nothing happens here.** The terminal-review
attestation used to be scheduled at the common derivation head, on r4-3's
written order. It is now the **last commit before publication**, step **C11**
below, after the mint. The mechanism, the mechanical reason for the move, and
the two head names it introduces are all stated at C11; this heading survives
only so that transcripts, the time budget, and the earlier drafts of this
runbook agree on which step is which.

### C6 — Evidence stamping (SCRIPTED, runsheet §3.4)

Three author commands at the common head, no commit between them, then one
evidence commit. The census check asserts exactly the eleven kinds per pack.

**This is the boot-binding boundary.** From here on, a reboot voids all 33
receipts and the only cure is a full re-author.

**It is also T+0 on the campaign's freshness clock, and that clock bounds the
entire measurement campaign.** Of the eleven authored kinds, **nine** are
`EXECUTION_BOUND` under `r1.execution_bound.freeze_generic_168h.v1` — a
**168-hour** horizon (`604_800_000_000_000` ns), ruled by Ed under D-150(2). The
other two (`DOCTRINE_PIN`, `PACK_FAMILY`) are `RE_DERIVABLE` and carry no
horizon. So: **every consuming window must complete within seven days of this
commit.** The arithmetic Ed ruled on: a clean nightly campaign finishes around
T+74 h; a full-weather campaign with refused nights finishes around T+146 h;
both fit inside 168 h, the worst case with about a day of margin. There is no
re-author after publication — the freeze slots are spent — so an expiry means a
new family generation.

### C7 — Sacrificial pre-mint refusal check (SCRIPTED, runsheet §3.5)

Before touching the real packs' unbuilt freeze slots, all three are frozen in a
throwaway clone and required to return a clean PASS. The reason is a property of
the code that was verified rather than assumed: `generate_freeze_receipt`
evaluates its refusals and then writes and plan-pins the receipt **whether it
passed or refused**. A refused mint therefore permanently occupies the
`freeze-0004` slot. Any REFUSE here is a stop *before* the real mint.

*Real-lane difference:* the throwaway is a clone of the measurement checkout,
made in transaction custody, and is deleted afterwards. It is the one clone that
survives the removal of S-0 scaffolding, because its purpose is not rehearsal —
it is a screen that protects a create-only slot.

### C8 — Primary freeze ×3 (SCRIPTED + **ED PROMPTS 4–6**, runsheet §3.6)

**PROMPT 4** — Ed will be asked to approve, verbatim:

```
.venv/bin/python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --predecessor-pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
```

Same invocation discipline as C3: working directory already at the
measurement checkout, bare relative form, `python3` spelling.

**PROMPT 5** — the same, ALPHA: `…_floor_qwen25_1p5b_v4` against
`…_floor_qwen25_1p5b_v3`.

**PROMPT 6** — the same, BETA: `…_floor_qwen25_7b_v4` against
`…_floor_qwen25_7b_v3`.

Per pack, assert `status: PASS`, `mutated: true`, empty `reason_codes`, and a
`receipt_path` ending `freeze-0004.json`. Then one freeze commit for all three.

**A REFUSE here cannot be retried.** The receipt is plan-pinned; the slot is
spent. See §5.

### C9 — Authenticate the executing custody tools (SCRIPTED, runsheet §3.6.1)

Before any custody tool runs, each executing file's SHA-256 is compared against
the digest the manifest records for its repository-relative path. A mismatch
stops here, at a named step, instead of surfacing later as a `tool_mismatch`
refusal in the middle of the marker build.

### C10 — Mint the successor pinset and close the allowlist contract (SCRIPTED, runsheet §3.7)

Three ordered steps:

1. Build `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` with
   `scripts/build_v4_histsem_pinset.py`, passing `--historical-head` =
   `EVIDENCE_DERIVATION_HEAD` (**not** the evidence commit — the receipts record
   the derivation head as their coordinate, and the builder accepts no other
   value) and `--current-head` = the freeze commit. The output path is
   create-only.
2. Assert the minted shape (3 packs, 33 receipts, the three exact pack ids),
   assert the `_v1` pinset member is byte-unchanged, commit. The resulting head
   is **`PINSET_MINT_HEAD`** — the allowlist-contract closure. **It is not
   "window close" and no transcript may call it that** (D-153 A6 reserves that
   phrase).
3. Close the contract at exactly 112 by diffing
   `EVIDENCE_DERIVATION_HEAD..PINSET_MINT_HEAD` against the registry allowlist;
   verify the present chain with `scripts/verify_receipt_histsem.py
   --require-published`; and record the successor pinset's digest `hS` computed
   from the bytes **committed at the mint head**, at the moment that digest
   first exists.

**Fixation does NOT happen here.** In the rehearsal, fixation was made the last
commit of the clone (runsheet §4.10) so that everything else could run at the
mint head; the runsheet says in terms that this placement is clone-proof-only
and is not a claim about transaction sequencing. In the real transaction
fixation is post-campaign — see §6.

---

### C11 — The terminal-review attestation, and the opening of the freeze span (MAGISTRATE under D-150b)

**RULED (D-155, NR-12).** The attestation is the **last commit before
publication**. It is made here, at the mint tree, and the head it produces is
the head that gets published.

**What the attestation physically is.** Not a file in custody: **three
trailers on a Git commit message.**

```
JouleWise-Terminal-Review: PASS
JouleWise-Terminal-Review-Tree-Oid: <the commit's own tree object id>
JouleWise-Terminal-Review-Pack-Sha256: <a pack's committed pack-tree digest>
```

At arm time the readiness code reads `HEAD`'s commit message, parses those
lines, and compares them against the arming context. "Tree-preserving" means
the commit adds no content: an empty commit reuses its parent's tree, so the
`Tree-Oid` it records is the tree that was reviewed.

**Why it moved here from the derivation head.** Under r4-3's written
placement the tree moves three more times after the attestation — evidence,
freeze, mint — so at arm time the recorded `Tree-Oid` names a tree that is no
longer `HEAD`'s, and the attestation is dead. The window runbook already
states the governing rule: "trailers from an ancestor do not transfer."
Placing the attestation last makes the recorded tree the tree that is
actually armed against.

**Three packs, three digest lines.** Each pack has its own committed
pack-tree digest, and all three arm against this single frozen head, so the
message carries **three** `Pack-Sha256` lines — one per pack, ALPHA/BETA/GAMMA
— with exactly one `PASS` line and exactly one `Tree-Oid` line. The parsers
accept that shape only once the D-155 NR-11 cure is on the head: `PASS` and
`Tree-Oid` stay exactly-once, while `Pack-Sha256` becomes **non-empty,
duplicate-free, and containing the arming pack's digest**. That cure lands in
both parsers — `_derive_terminal_review` in
`joulewise/arm_readiness_evidence_t0.py` **and** its twin
`_verify_terminal_review` in `scripts/capture_t0_step.py`, which runs on every
one of the six `capture_t0_step.py` invocations per window — as work order
W-2, before Phase C1. The producer command block is the ONE home:
`docs/phase_2/window_runbook.md` §5C.

> **DO NOT ALLOWLIST THE CURE.** If the NR-11 parser cure is somehow *not* on
> the head when this step is reached, the tempting repair is to add
> `joulewise/arm_readiness_evidence_t0.py`, `scripts/capture_t0_step.py`, or
> their test modules to the changed-set allowlist so the cure can land
> mid-transaction. **That is a D-151 condition-7 tripwire event, not an
> amendment lane.** D-151 condition 7 reads: "FIXED-POINT PRINCIPLE (standing
> rule, all future transactions): **no authenticator path ever enters any
> allowlist, in any transaction.** A proposal to add one is a V-1(vi) tripwire
> event routing to the V-1(vii) derived manifest, not an amendment." It also
> dies on the same impossibility that killed O-1's Option 1: a test-source
> path's final bytes exist only *after* derivation, so no digest condition
> over them can be pre-committed. The correct response is to stop the
> transaction and land the cure through the ordinary review lane at a new
> head.

**The steps.**

| Step | Who | What |
|---|---|---|
| C11.1 | MAGISTRATE | **Create the commit-freeze sentinel** at `/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN` (outside the repository). From this file's existence onward `scripts/window_status.sh` writes `WINDOW_STATUS.md` locally and refuses to commit or push it. Create it *before* the attestation commit, so the span is guarded from its first instant. |
| C11.2 | MAGISTRATE | Assert the preconditions: `HEAD == PINSET_MINT_HEAD`, working tree clean under `git status --porcelain=v1 --untracked-files=all`. |
| C11.3 | MAGISTRATE | Run the §5C producer block: compute `TREE_OID` and the three pack digests, then one `git commit --allow-empty --cleanup=verbatim` carrying `PASS`, `Tree-Oid`, and the three `Pack-Sha256` lines. `--cleanup=verbatim` matters — the default cleanup would strip lines the parser needs. |
| C11.4 | MAGISTRATE | Record the resulting head as **`ATTESTATION_HEAD`**. Re-run the closure diff with its endpoint moved: `EVIDENCE_DERIVATION_HEAD..ATTESTATION_HEAD` must still be exactly the 112 allowlisted paths. An empty commit adds no paths, so the number is unchanged — but the assertion is re-run rather than reasoned about. |

**Two heads, and every later step says which.**

- **`PINSET_MINT_HEAD`** is the **allowlist-contract closure head** (D-153 A6)
  and the coordinate `hS` — the successor pinset's digest — is computed from.
  An empty commit changes no bytes, so `hS` is unaffected by C11.
- **`ATTESTATION_HEAD`** is the **published head**. The marker is built at
  `--head ATTESTATION_HEAD`; Phase F's `PUBLISHED_HEAD` is
  `ATTESTATION_HEAD`; the dry-run ceremony's head binding is
  `ATTESTATION_HEAD`.

Closure head and published head are now two different commits. That gap is not
a defect introduced here — the changed-set gate is *defined* over
`derivation commit .. reviewed HEAD`, so the machinery already expects two
coordinates. `validate_r1_evidence_lifecycle`'s ancestry check still holds,
because the derivation head is an ancestor of both.

**The freeze span opens at C11.** From this commit onward, an ordinary commit
to `main` — from this machine, another session, a cron job, a status script,
or another of Ed's machines — breaks the transaction. This is also the point
at which r4-3's own sentence "the runsheet carries a commit-freeze on the
measurement checkout's main from attestation through window close" becomes
exactly true, which under r4-3's original placement it was not.

---

## Phase D — Publication (MAGISTRATE)

**This phase has no counterpart in the rehearsal at all, and it contains the
transaction's single largest real-lane difference.**

The rehearsal simulated publication by forging `refs/remotes/origin/main` to
whatever head it had just made. That forge is what let it build the marker.
Remove the forge and a hard constraint appears:

> `build_family_publication_marker` calls `reviewed_main()` on the pack root's
> repository and refuses unless `HEAD == refs/heads/main ==
> refs/remotes/origin/main` with a clean tree (`joulewise/arm_readiness.py`,
> the `head_mismatch` / `worktree_dirty` raise immediately after the
> `reviewed_main` call).

**RULED (D-155, NR-3): push-then-build.** The head must already be published
before the marker can be built, so r4-3's written order ("marker candidate +
Ed's exact-byte step-6 → atomic publication") is amended — see the dated
amendment in
`docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`. The
authority to gate is conferred by the marker receipt's `gate_admissible` and
`publication_authorized` fields and by the verify gate, not by the push: a
pushed head carrying no admissible marker authorizes nothing. Push-then-build
reorders a git operation, not the authority.

**RULED (D-155, NR-2): pull-into-dev → push → fetch-back.** The `_v3` doctrine
— the measurement checkout consumes references and never publishes — is
preserved verbatim. The transaction is licensed to pull, push (from the
development worktree) and fetch (at the measurement checkout), and to do
nothing else that moves a reference.

| Step | Who | What |
|---|---|---|
| D1 | MAGISTRATE | From a **development** worktree: `git fetch /Users/edr/JouleWise-measurement-20260813 main`, then `git push origin FETCH_HEAD:main`. Use the **plain local path**, not a `file://` URL — the `file://` form appears in no source and was an invention of an earlier draft. |
| D2 | MAGISTRATE | In the measurement checkout: `git fetch origin`, then assert four-way equality **by running the predicate**, never by eye (see below). |
| D3 | MAGISTRATE | Send the D-150a state-change notification: published at `ATTESTATION_HEAD`; freeze span open. |

**Assert the four-way equality by running `reviewed_main`, not by comparing
strings.** The predicate is the same code every downstream gate consults, so
running it cannot disagree with them, while a hand comparison can:

```sh
.venv/bin/python3 -c "import json,sys;from joulewise.arm_readiness import reviewed_main;print(json.dumps(reviewed_main(sys.argv[1]),indent=2))" <pack_root>
```

Require `exact_match: true`, `clean: true`, and `head_commit ==
ATTESTATION_HEAD`. Pass a **pack root**, not a repository path:
`_repo_for_pack` derives the repository from the pack root, which is the
non-guessable form and cannot diverge from what the gates themselves resolve.

**What is licensed inside the freeze span, and what is not.** A `git fetch` at
the measurement checkout **is** permitted: it moves only
`refs/remotes/origin/main`, creates no commit, and is *required* for four-way
equality. A commit, a push, or any move of `refs/heads/main` at the
measurement checkout is **not**. Later windows need no further fetch; and if
`origin/main` ever does move during the campaign, a fetch *reveals* the break
rather than causing it.

**`ATTESTATION_HEAD` is the published head, and it is also the window-close
head.** `PINSET_MINT_HEAD` remains the allowlist-contract closure head — two
different commits, and every step below names which one it means. The reason
published head and window-close head coincide is worth stating: the commit
freeze means `main` does not move between publication and the close of the
last window, so the head that was published *is* the head at which the freeze
closes. This is corroborated inside the tool — publication-lane marker replay
refuses `head_unpublished` unless the marker's own publication head equals
live `origin/main`, so a later fixation commit could never be the published
head the marker admits.

**From D1 onward, an ordinary commit to `main` breaks the transaction.** Arm
receipts bind the reviewed main they were produced against
(`_verify_arm_receipt` requires equality), so any commit — including one line
of `WINDOW_STATUS.md` — invalidates every armed pack for the rest of the
campaign. The C11.1 sentinel is what stops the status publisher from being
that commit.

---

## Phase E — Marker, step-6 table, and the delegated confirmation (MAGISTRATE)

**Execution order is E1 → E3 → E4 → E2 → E5** (RULED, D-155, NR-3). The step
names keep their original numbers so that this document, the runsheet, r4-3,
and every transcript agree on which step is which; only the order in which
they run has changed. The forcing reason is mechanical: a marker **verify** at
`--phase publication` calls `_authenticate_confirmation_table`, which raises
`confirmation_missing` when no expected confirmation digest is supplied. The
confirmation digest `hC` does not exist until E4 has executed. So the verify
(E2) cannot run before the confirmation (E4), and the confirmation cannot run
before the table (E3), and the table cannot be rendered before the marker (E1)
because the table's bytes contain the marker's digest.

**RULED (D-155, NR-4): both the build and the verify run `--phase
publication`.** Not `candidate`. In the real lane the custody tools exist at
the head as committed blobs with committed `.sha256` sidecars, so the marker
can authenticate them by committed-blob equality — the rule the marker ruling
calls "the strict production rule". The candidate lane was the S-0
accommodation for a condition that does not obtain here (tools absent at the
pinned head), it authenticates tools against a manifest instead of committed
blobs (strictly weaker), and its receipt is `gate_admissible: false` and
`publication_authorized: false` by construction, so it can gate nothing and a
publication verify would be required anyway. Neither invocation passes
`--candidate-manifest`.

**This does not delete the §1.3 manifest.** It is still produced at preflight,
because **C9 consumes it** — each executing custody tool's SHA-256 is compared
against the digest the manifest records for its repository-relative path. Only
the marker stops consuming it. A cheap dry pass remains available if wanted:
build `--phase publication` to a scratch output path and discard it.

### E1 — Build the marker (runsheet §3.8)

`scripts/build_family_marker.py --repository <measurement checkout> --head
ATTESTATION_HEAD --pack-root ×3 --phase publication --output
<custody>/marker-candidate/…`.

The head is `ATTESTATION_HEAD` — the published head — not `PINSET_MINT_HEAD`.
`_authenticate_custody_tool` reads each tool with `git show <head>:<path>`, and
the attestation commit is empty, so it returns the same blobs either way; the
head is named explicitly so no step is ambiguous about which commit it means.

Assert: the marker sidecar was written; the `conditional_paths_deferred`
disclosure names gate `R1_DIGEST_CONDITIONAL`, `deferred_paths` exactly
`[the successor pinset path]`, and the four enforcing entry points
`["arm", "freeze", "verification", "marker-replay"]`. That disclosure is the
visible form of a structural fact: the marker build cannot check the `C → S`
edge, because `C` carries the marker's own digest and so cannot exist yet. An
**empty** `deferred_paths` would be the positive statement that nothing was
deferred, which is why the key is required rather than optional.

### E3 — Render the DRAFT step-6 confirmation table (MAGISTRATE)

Render `C` exactly per `docs/contracts/d117_step6_confirmation_table.md`: strict
canonical JSON (UTF-8, sorted keys, two-space indent, one trailing newline, no
timestamp, no self-digest). Its fields bind the marker digest `hM`, the
successor digest `hS`, the registry digest, the published head and its tree,
and the three member rows in ALPHA/BETA/GAMMA order.
`confirmation.authority` is `"ED"` and `confirmation.decision` is `"YES"`.

**What E3 produces is a DRAFT, and it gets no sidecar.**
`confirmation.statement` is not yet filled — E4 writes it, because only E4
knows what was independently recomputed — so these are not the final bytes.
**Write no `.sha256` sidecar here.** The contract defines the sidecar as
"computed from the same bytes it accompanies"; a sidecar over draft bytes
would accompany bytes that are about to change, and the mismatch would surface
at E2's verify as a refusal. The sidecar is written once, at E4, over the
final bytes. That there is no sidecar on disk between E3 and E4 is **by
design**, not an omission — do not "repair" it.

### E4 — Execute the delegated confirmation (MAGISTRATE, D-150b)

This is what replaces "Ed types YES". It has six parts, and the independence
requirement in the first two is the whole point of it:

1. **Recompute `hM` from the marker file on disk**, and `hS` from the bytes
   committed at `PINSET_MINT_HEAD` for the successor pinset path — read from
   the artifacts, never taken from the producing session's report. Note the
   head: `hS` is a coordinate of the **closure** head, not of the published
   head.
2. **Evaluate equality** against what the rendered table asserts, and against
   the mint-time `hS` record from C10 step 3. Any mismatch is a refusal and a
   ping to Ed, never a re-render.
3. **Write the delegation into `confirmation.statement`**: that this
   confirmation was executed under D-150b's standing delegation, and what was
   independently recomputed.
4. **Render the FINAL canonical bytes** — the same strict D-134 canonical form
   E3 used, now with `statement` filled. These bytes, and only these, are `C`.
5. **Compute `hC` over those final bytes**, and record it **in transaction
   custody only**. `hC` never enters a repository path, in this transaction or
   any other.
6. **Only now write the adjacent `.sha256` sidecar**, in exact GNU form, over
   the bytes just rendered.

**Render final, then sidecar — in that order, and not before.** No sidecar
exists on disk before this point, by design: the contract defines the sidecar
as computed from the same bytes it accompanies, so a sidecar written at E3
would have accompanied draft bytes that step 3 then changed, and E2's
publication-phase verify would refuse on the mismatch. The sidecar is
transport integrity only and never authentication — the authenticator of
record is `hC`, supplied to every consumer out of band from custody.

The contract's own prose now records this delegation — it was amended under
D-155 and no longer tells a bench operator to wait for Ed.

Then notify Ed. **The notification cadence — immediate ping versus batched to
the phase boundary — is Ed's item 10 from the D-150a packet and remains
PENDING his one word.** Both seats' recommendations are on the table: immediate
(only two desk events exist, and one of them follows the irreversible
publication step, where delayed visibility undercuts the D-150a bargain) versus
batched with immediate mismatch pings (fewer interruptions). The D-155
synthesis recommends **immediate**; the saving from batching is literally one
ping. Nothing in code consumes the notification either way.

### E2 — Verify the marker (runsheet §3.8)

`scripts/verify_family_marker.py --phase publication`, with
`--confirmation <table>` and `--expected-confirmation-digest <hC>` — the
confirmation pair E4 has just produced. Assert `status: PASS` and that the
reported `origin_main_commit` is the **real** published head
(`ATTESTATION_HEAD`).

*Real-lane difference:* the rehearsal recorded a `FORGED_ORIGIN_MAIN_OID` and
classified the result "forged-`origin/main`-conditional". **There is no forged
OID in the real lane and no such classification.** Any transcript carrying that
phrase in this session is a defect.

### E5 — Promote (runsheet §3.8)

Copy the marker, its sidecar, the table, and its sidecar byte-exactly into
`<custody>/windows/family_publication/`. Promotion copies; it never edits.

---

## Phase F — The published-green half (MAGISTRATE)

This is runsheet §3.10's deferred block — the one thing the rehearsal recorded
as an obligation of the real transaction rather than discharging itself
(`095-*`, and the completion record says so in terms). **It runs here, for
real.**

The block takes exactly two operator substitutions, and they are the two the
runsheet names:

- `PUBLISHED_HEAD` = **`ATTESTATION_HEAD`** — the published window-close head,
  not `PINSET_MINT_HEAD` and not a fixation commit (RULED, D-155, NR-12: the
  attestation commit made at C11 is the last commit before publication, so it
  is the head that was pushed). The runsheet's guard refuses an unsubstituted
  block rather than running against the literal placeholder.
- `PUBLISHED_CHECKOUT` = the absolute path of a **clean, separate checkout** at
  that head, with `origin` fetched. Not the measurement checkout: the suite is
  long and heavy and the measurement checkout should be left alone, and the
  block only needs a tree where the four-way equality holds.

It also takes `hC`, supplied explicitly, as every enforcing consumer does.

Three results are required:

1. **Four-way reference equality** at the published head → transcript `150-*`.
2. **Publication-lane marker replay** — `--phase publication`, no
   `--candidate-manifest`, with `--confirmation <table>` and
   `--expected-confirmation-digest <hC>`. Required in the result:
   `lane: "published"`, `gate_admissible: true`, `publication_authorized: true`,
   the reported `origin_main_commit` equal to the published head, and both
   `confirmation_missing` and `confirmation_mismatch` present in the executed-
   checks list. That last requirement is what proves the confirmation pair was
   actually authenticated rather than skipped → transcript `151-*`.
3. **The complete suite, green, against the real reference** → transcripts
   `152-*` / `153-*`, classified `PUBLISHED GREEN`.

A red published-head suite is a mechanism failure, never a carried state
(D-153 A3). D-153 A2 is what makes green achievable here: every
digest-independent consequence of the pinset chain read was moved into the
pre-derivation candidate that already merged, so the only thing still missing at
this head is the `hS` byte pin — and the pin's value cannot exist before the
mint that produces it, so requiring it here would require the head to contain a
value derived from itself.

---

## Phase G — The dry-run ceremony (MAGISTRATE)

**RULED (D-155, NR-6): the dry-run ceremony, and no real arm.** The rehearsal's
§3.9 armed and verified all three packs at the mint head; r4-3 instead put a
dry-run ceremony here. r4-3 governs, on B-4's ruling plus B-3's cost
accounting: a ceremony arm is not free — it burns attempt and session
identifiers under D-131 cl. 4, it requires the ED-FIRST T-0 lane, and it
prepends a supersession link to the claim family's arm chain. The ED-FIRST
requirement alone breaks this night's "Ed present for Phases B and C only"
budget.

**The first real arm of the `_v4` family is the shakedown window's own**, under
its D-149 GO receipt. B-3 makes the shakedown a **non-claim** window whose GO
receipt *is* the V5 measurement and which halts the campaign before any claim
window on a bounds violation — so deferring the first live arm there costs no
claim-bearing exposure.

**`file-09-probe P1/P2/P3` is struck as specified** (D-155, NR-6). Its three
properties were P1 the live registry reference loads, P2 the freeze reference
authenticates, and P3 arm semantics cross the registry gate. P1 and P2 are
already executed *inside* the dry run. P3 requires an arm: the dry-run receipt
records `arm_disposition: NOT_APPLICABLE` and `evidence: []`, so nothing
crosses the registry gate. P3 is therefore **unsatisfiable inside the ceremony
B-4 defines**, and it is struck rather than rewritten — the Sol seat's
read-only reformulation was declined on the ground that renaming an
unsatisfiable ruled property to a satisfiable weaker one is exactly the
quiet-weakening this process exists to refuse.

**What the ceremony is, executably.** One
`scripts/generate_arm_readiness.py dry-run` per pack, against the measurement
checkout, at `ATTESTATION_HEAD`, with the confirmation pair supplied as every
enforcing consumer requires. Assert, per pack:

| Assertion | What it proves |
|---|---|
| `status: PASS` and `refusals: []` | Entails the old P1 and P2 — a failure of either surfaces as a refusal on the same code path, so an empty refusal list is the stronger statement. |
| the same-head pack-binding check PASS, `head_binding == ATTESTATION_HEAD` | The dry run was evaluated against the published head, not a stale one. |
| `receipt_kind: dry_run`, `mode: dry_run`, `arm_disposition: NOT_APPLICABLE`, `evidence: []` | The positive statement that **no arm occurred** — not merely the absence of arm evidence. |

**P3 is recorded as discharged at the shakedown GO receipt**, which B-4 already
names as the V4-delta proof point.

**Arm-side U11 goes with it.** The identity-pin re-verification leg runs only
on the arm path, never on the dry-run path. The rehearsal's one open caution —
runsheet §7 O-5, "live arm-side U11 re-verification is proven by the real
transaction in the measurement environment" — is therefore discharged at the
**shakedown arm**, and this runbook names it there rather than leaving it
floating. That is a recorded trade, not an oversight: B-4 priced it when it
struck the ceremony arm.

Phase G runs against the measurement checkout and can proceed while Phase F3's
long suite runs on the separate published checkout.

---

## Phase H — Close the session (MAGISTRATE)

| Step | What |
|---|---|
| H1 | **Seal the transaction phases' transcripts read-only** — Phases A through G. Every command's stdout, stderr and exit code is a preserved triplet; the magistrate reads all of them. The seal is append-only-with-one-named-exception, not final closure: see the continuation clause below. |
| H2 | **STRUCK.** No `RUN_STATE.md` header update on transaction night — see below. |
| H3 | Send the D-150a notification: campaign span open; per-window notices to follow. |
| H4 | Record the registered limitation (D-153 W5): a mid-campaign non-configuration cure forces a new family generation. There is no patching a published `_v4`. |

**H1's continuation clause — what "sealed" means here.** Sealing exists to make
the record non-repudiable: **nothing already written is ever mutated, reworded,
or removed, at any later point.** That property is what H1 establishes and it
never lapses. But custody cannot be *finally* closed on transaction night,
because one ruled artifact does not exist yet: `campaign-close.json`, written at
campaign close (H5), days later. So H1 seals the transaction phases' transcripts
read-only and leaves custody open for **exactly one appended record** — the
campaign-close record and its transcript, the named exception. Custody closes
fully once that record is written and its digest recorded. Appending the ruled
record is not a breach of the seal; editing anything already sealed is, and
nothing in H5 does that.

**H2 is struck, and the reason is mechanical, not stylistic.** D-150a asks that
the current state be carried in `RUN_STATE.md`'s header line. Writing that line
on transaction night would require a commit to `main`, and two ruled things
forbid it. First, the commit freeze is open from C11: any ordinary commit
invalidates every armed pack for the rest of the campaign, and a `RUN_STATE`
header edit is an ordinary commit. Second, D-153 A1 reserves the **first commit
after the freeze closes** for the fixation commit; a `RUN_STATE` update written
into that slot takes it. So the header update moves to **H5's post-fixation
tail**, at its ruled position in the record order.

Ed's visibility on the night is not reduced by this. D-150a's committed
visibility channel is the **push notification** (§4), not a repository file, and
the window status publisher still writes `WINDOW_STATUS.md` **locally** under
the C11.1 sentinel guard. What is withheld until fixation is only the *published*
copy.

### H5 — Declaring the campaign closed (RULED, D-155, NR-8)

**This does not happen on transaction night.** It happens days later, at the
end of the campaign, and it is written here because it is the act that gives
the fixation commit a trigger and the freeze span an end. Until D-155 no
source named it, which meant the first commit after the last window would have
been whatever a stray script wrote.

**The triggering fact is determinable, not judged.** The campaign's member set
is fixed at publication — the marker names three members and their plans — so
"the last consuming arm" can be *read off the published plan* rather than
decided.

**The predicate is an equality, and nothing else.** The magistrate declares the
campaign closed when, and only when:

> the **executed arm set equals the published campaign plan** — every arm the
> published plan names was executed and consumed, and no arm outside it was.

That is a set comparison against bytes fixed at publication, which is exactly
the mechanical class D-150b delegates. **Any other outcome is Ed's ruling, not
the magistrate's** — an arm that refused, an arm superseded by a re-run, a
window cancelled, a slot abandoned, or a decision to stop early. Each of those
makes the executed set differ from the planned set, and deciding whether a
campaign that did *not* run its plan is nonetheless complete is judgment-bearing
by construction. The magistrate's move in that case is to stop and put the
question to Ed with the two sets side by side, never to declare.

**The declaration names both coordinates at once**, because two different
windows close at two different events and the vocabulary has been confused
before:

1. the **arm receipt id of the last consuming arm** — this closes the
   **changed-set window** (D-153 A6, whose normative text governs the unit:
   *arm*, not *window*);
2. the **completion of that window's consume** — this permits the
   **commit-freeze close** (D-153 A1).

**Owner: the magistrate**, under D-150b's own boundary — the equality above is
a comparison against bytes fixed at publication, which is exactly the mechanical
class D-150b delegates. **The boundary is where that mechanism ends:**
everything on the non-equality side of the predicate is judgment-bearing by
construction and is Ed's ruling, not the magistrate's.

**The record, and its order is strict.** Getting this order wrong takes the
fixation commit's ruled slot, which is the trap:

1. **Declaration transcript** into transaction custody — no commit. The
   canonical artifact is `campaign-close.json`, carrying the slot ledger, the
   artifact digests, the predicate results and the times; its SHA-256 goes into
   the transcript. This is the one appended record H1's continuation clause
   reserves; it adds to custody and mutates nothing already sealed there.
2. **Freeze close declared.**
3. **D-150a notification:** campaign done, freeze OFF.
4. **THE FIXATION COMMIT — first, before anything else.** It carries exactly
   the successor pinset's `hS` literal plus its loud-fail guard (D-153 A1), and
   an independent reviewer recomputes that SHA against the step-6 table.
5. **Only then** the bookkeeping: `RUN_STATE.md`, `WINDOW_STATUS.md`, the
   decision-log row, and everything else.
6. **Only after the fixation commit is pushed** does the C11.1 commit-freeze
   sentinel come off.
7. **Custody seals fully** — the appended record is written and its digest is
   recorded, so the exception H1 reserved is now spent and nothing further is
   ever added.

A `RUN_STATE` header update written before fixation would occupy the slot
D-153 A1 reserves for the fixation commit. That is why step 5 is numbered
after step 4 rather than left to judgement.

---

# 3. Time budget

Two numbers matter and they are different: **machine time** (how long the
session runs) and **Ed time** (how long Ed must be present). Ed's presence is
required only for Phase B and Phase C.

The floor is estate 10's observed shape: the scripted band ran in roughly **ten
minutes plus the three MLX freezes**. That figure is carried from the session
record rather than from a timing transcript — **no per-step wall clock was
captured in estate custody**, which is itself worth curing on the next
instrument cut. The real lane is slower than the floor: a larger repository, no
warm caches, and six pauses for permission prompts. Everything below is a walk-up
estimate against that floor, not a measurement.

| Phase | Step | Who | Estimate | Notes |
|---|---|---|---:|---|
| A | Desk preflight | MAGISTRATE | 60–90 min | Can run the day before. Includes the suite baseline measurement (F3 below), which can run in the background. |
| B | Reboot + pin | **ED** | 10 min | ~3 min of Ed's attention. |
| C1 | Emit three pack roots | SCRIPTED | 2–4 min | |
| C2 | Runtime gate | SCRIPTED | 2–5 min | Presence and size only; no hashing. |
| C3 | **U11 ×3 + prompts 1–3** | SCRIPTED + **ED** | **15–25 min** | The dominant scripted cost. Each freeze loads the MLX runtime and hashes the pack's full weight set: ~3 GB for ALPHA, ~15 GB for BETA, both for GAMMA. |
| C4 | Post-conditions | SCRIPTED | 1–2 min | |
| C5 | Common-head gate + two modules | SCRIPTED | 2–5 min | |
| C5b | — | — | 0 | Ruled to C11 (D-155, NR-12). Nothing happens here. |
| C6 | Evidence stamping ×3 | SCRIPTED | 3–6 min | Starts the 168 h clock and the boot binding. |
| C7 | Sacrificial pre-mint check | SCRIPTED | 4–8 min | Clone (~650 MB) plus three readiness freezes. |
| C8 | **Freeze ×3 + prompts 4–6** | SCRIPTED + **ED** | 3–6 min | |
| C9 | Tool authentication | SCRIPTED | <1 min | |
| C10 | Mint + close contract + chain verify | SCRIPTED | 3–6 min | |
| C11 | Freeze sentinel + three-pack attestation commit | MAGISTRATE | 5 min | Opens the freeze span. Ed may leave after this. |
| | **Phase C subtotal** | | **40–75 min** | Ed present through C10; C11 needs no prompts. |
| D | Publication | MAGISTRATE | 5–10 min | |
| E1 | Marker build (`--phase publication`) | MAGISTRATE | 2–4 min | |
| E3–E4 | Draft table render, then delegated confirmation: final bytes, `hC`, sidecar | MAGISTRATE | 20–40 min | Careful desk work; the independent recomputation is the point. No sidecar exists until E4 writes it over the final bytes. |
| E2 | Marker verify, with the confirmation pair | MAGISTRATE | 1–2 min | Runs **after** E4 — a publication-phase verify needs `hC` (D-155, NR-3). |
| E5 | Promote | MAGISTRATE | 1–2 min | |
| F1–F2 | Four-way + publication replay | SCRIPTED | 2–5 min | |
| F3 | **Full suite at the published head** | SCRIPTED | **45–180 min** | See below. |
| G | Dry-run ceremony ×3 | MAGISTRATE | 10–20 min | Ruled: dry run, no arm (D-155, NR-6). Runs against the measurement checkout while F3's suite runs elsewhere. |
| H | Close-out | MAGISTRATE | 15 min | |
| | **TOTAL, machine time on the night** | | **≈ 2.5 – 6 hours** | Phase A runs the evening before and is excluded; the whole spread is owned by F3's unmeasured suite. |
| | **TOTAL, Ed's presence on the night** | | **≈ 1 hour** (Phase B through C10) | Plus ~10 minutes for the venv relock on any prior day, and one word on the NR-9 cadence. |

**The full suite is the largest and least-known term, and it should be measured
before the session rather than discovered during it.** No custody record in this
repository states its local wall clock. What is known: on GitHub-hosted runners
the ordinary suite totals **4117 seconds** of test time, and the exclusive
crash-matrix job alone runs about **89 minutes**
(`docs/process_traces/2026-08-23-speed/TEST-SPEED-01-evidence.md`). Phase F runs
`python -m unittest discover -s tests`, which is **serial and single-process** —
it does not get CI's shard parallelism. An M3 Max is faster per core than a
hosted runner, but the serialisation works the other way. Measure it once on a
scratch checkout at the reviewed head; if it exceeds ninety minutes, start it as
soon as Phase F1–F2 pass and let Phase G proceed against the measurement
checkout while it runs.

**Do not compress Phase C to save clock.** Every one of the nine estate halts in
the rehearsal came from a step that looked skippable.

---

# 4. Notifications Ed will receive (D-150a visibility protocol)

Ed accepted the origin-main push freeze conditional on visibility. The committed
form is a notification at every state change, plus standing duration estimates,
plus the current state carried in `RUN_STATE.md`'s header line.

| When | Message |
|---|---|
| Phase A end | Transaction open; push freeze **ON**; expected span ~1 week. |
| Phase C11 | Freeze span open (the sentinel is in place and the attestation commit is made). |
| Phase D3 | Published at `ATTESTATION_HEAD`; freeze span open; machine is normal use minus pushes and reboots until the campaign closes. |
| Phase E4 | Step-6 confirmation executed under the D-150b delegation, with what was recomputed. *(Cadence still pending Ed's one word — immediate ping, which D-155 recommends, versus batched to the phase boundary. A mismatch always pings immediately, either way.)* |
| Each window | "T-0 at ~HH:MM, machine untouchable until morning." |
| Each window end | Window closed. |
| Campaign end | Campaign done; freeze **OFF** — sent at step 3 of the H5 record order, *before* the fixation commit and before any bookkeeping. |

---

# 5. Abort semantics

The rehearsal's failure classes (runsheet §6) carry over, but their *recoveries*
change, because the real lane has no estates. Where the runsheet says "restart
from a fresh estate", the real lane says **"a new attempt at a new head"**: cure
the cause on `main` through the ordinary review lane, re-sync the measurement
checkout, and begin the band again at C1.

The one thing that has no real-lane analogue is a *cheap* restart. A fresh
estate cost a clone; a new attempt costs the whole band, and — after C6 — a full
re-author of 33 receipts.

## 5.1 The three lines that matter

**Line 1 — before C6 (evidence stamping).** Everything is recoverable. Nothing
outside the measurement checkout has moved. Reset the checkout hard to the last
recorded good head, preserve the failed transcripts in custody in writing, cure,
and restart the band.

**Line 2 — between C6 and D1 (publication).** Recoverable, but expensive, and
**a reboot in this range ends the attempt**. Note that C11's attestation
commit and its freeze sentinel fall inside this range: the commit is local
until D1 pushes it, so a reset here discards it like any other, and the
sentinel is a file in custody that is simply removed. What is *not* recoverable
here is the boot binding: the 33 generic receipts carry the
boot session identifier and every later read of them compares it against the
current boot. The cure is a full re-author from the derivation head. Also in
this range, the 168-hour freshness clock is running; an attempt that drags past
seven days from C6 expires the evidence.

**Line 3 — after D1 (publication).** **A mechanism failure here abandons the
family, not the attempt.** The mint head is on `origin/main`; the marker binds
it; `freeze-0004` slots are create-only and plan-pinned; the successor pinset
path is create-only. There is no re-mint at this generation. The path is a new
family generation — the registered limitation D-153 W5 records exactly this
("a mid-campaign non-config cure forces a new family generation"), and it is the
reason the pre-publication screens exist at all.

## 5.2 What each refusal class means at the machine

**A declined permission prompt is always safe.** The command has not run. Nothing
has mutated. Decline freely if anything looks wrong; re-issue and approve when it
does not. The dangerous action is approving a command whose preconditions are
false, which is why every prompt is preceded by a scripted precondition block.

**An interrupted U11 freeze is not a refusal.** If a projection is interrupted
mid-write, the tree is dirty and the next projection will refuse
`readiness_identity_environment_dirty`. Do not retry the interrupted command
against the dirty tree. Restore the tree to the last commit, record the
interruption in custody, and re-run that one pack. Never interrupt a freeze
deliberately.

**Exit code 134 in the U11 band** is the MLX abort firing outside pytest. Stop,
escalate, never retry.

**A primary freeze REFUSE at C8 is terminal for the attempt.** The receipt was
written and plan-pinned regardless of its verdict, so the slot is spent. Recovery
is to abandon the transaction commits and restart from the evidence commit —
which, in the real lane, is `git reset --hard <evidence commit>` in the
measurement checkout while nothing has been pushed. C7's sacrificial screen
exists precisely to make this outcome nearly impossible; if it happens anyway,
the screen itself is suspect and the failure is a mechanism failure.

**Mechanism failures** — a path outside the 112 crossing the gate; an unexpected
evidence output accepted; the successor subtracted without the authenticated
`C → S` edge; an authenticator found inside an allowlist; a candidate-lane
receipt claiming `gate_admissible: true`; a local-green transcript presented as
published green. The response is never "adjust a test expectation". It is:
derive an authenticated manifest, remove every unauthenticated subtraction,
restart. Before D1 that is a new attempt; after D1 it is a new family.

**Instrument failures** — a step whose environment precondition is false, a
drifted anchor, a command naming a flag or refusal code that does not exist, a
step sequenced after the step that supplies its input. Stop, cure on `main`
through the review lane, restart at a new head. Nine of the ten rehearsal
estates ended this way, and each cure is now on `main`.

**Execution defects** — a block run without its preamble, two blocks
concatenated into one shell, a transcript written by a step whose assertions did
not all pass. Void the affected transcripts **in writing**, then restart. This is
the class that produced the rehearsal's worst near-miss: a compound script
continued past failed assertions and wrote two transcripts against the wrong
head.

**One command block per shell invocation, always.** Do not concatenate blocks and
do not wrap them in an outer script. Under `zsh`, `set -e` is not trustworthy
inside compound constructs, which is why every assertion in the runsheet ends in
an explicit `|| die`.

## 5.3 Standing escalation trigger

Two consecutive rounds failing with the **same signature** — the same defect
class, another missed call site, another failed formulation — is evidence of a
structural problem. The next spend is a consult, not round three. This applies to
every actor in this session.

---

# 6. What does NOT happen in this session

Naming these explicitly, because several of them look like they belong here and
do not.

1. **No measurement window.** No campaign run, no dry-run, no launch, no
   `[QUIET-MAC]` command of any kind. The windows follow this session, on their
   own nights, under `docs/phase_2/window_runbook.md`. **Hand-off note
   (2026-08-27):** `scripts/launch_window.py` is never invoked in this session
   — deliberately, per item 5 below and Phase G — but the windows that follow
   consume two things this session produces: the published step-6 confirmation
   table `C` and its out-of-band digest `hC`. Every launcher call that replays
   the consumption takes them as `--step6-confirmation-table <C>` and
   `--expected-confirmation-digest <hC>`, and `hC` must be carried from this
   session's custody transcript of Ed's step-6 confirmation, never recomputed
   from `C`'s own bytes. Because §2 Phase E4 keeps `hC` in transaction custody
   only, that transcript is the sole route by which a later window can satisfy
   the check. Ed's own E-10 command can supply both. The frozen
   `window-chain.zsh` currently **cannot** — it needs the pair at its
   `--lifecycle-event start` call, `execve` does not carry E-10's argv into it,
   and `window.env` cannot hold the values because `capture_t0_step.py`
   enforces an exact key allowlist. That gap is registered as an OPEN DEFECT in
   `docs/phase_2/window_runbook.md` and awaits a magistrate ruling; it gates the
   windows, not this session.
2. **No fixation commit.** Fixation is the first commit after the commit freeze
   closes, and the freeze closes after the *last consuming window*, which is
   days away (D-153 A1 and A4 price the mint-to-fixation interval at up to about
   eight days). The rehearsal made fixation its last step for a reason that is
   clone-proof-only — it needed the marker, arm, verify and probes to all run at
   the mint head — and the runsheet says in terms that this placement is not a
   claim about transaction sequencing.
3. **No `hS` byte pin, and no `118-*` byte-pin probe.** Both require the fixation
   commit to exist; the pinned test method does not exist at any head reachable
   in this session.
4. **No probe battery (probably).** Runsheet §4's tamper probes are the
   rehearsal's proof of mechanism, executed against throwaway case clones.
   Whether the real transaction re-runs any of them at the real head is **§7
   NR-5**.
5. **No arm at all.** RULED (D-155, NR-6): Phase G is the dry-run ceremony,
   with no real arm. The family's first real arm is the shakedown window's,
   under its D-149 GO receipt, on a later night.
6. **No declaration that the campaign is over.** The declaring act now exists
   — §2 Phase H5 defines its predicate, its owner, its artifact
   (`campaign-close.json`) and the strict order of its record (D-155, NR-8) —
   but it fires at the end of the campaign, days after this session.
7. **No `T0-UNATTENDED-01`.** D-150(4) makes `_v4` windows gate on that work
   order's landing; its kernel status today is `queued`. That gates the windows,
   not this session, but it must land before the first T-0.

---

# 7. Ruling dispositions — eleven ruled, two still open

D-155 (magistrate synthesis, 2026-08-26,
`docs/process_traces/2026-08-22-t20/nr-synthesis-ruling.md`, on two
independent adjudication seats recorded beside it) rules eleven of the
thirteen questions below. **Every ruling is folded into the body of this
document at the step it affects**; the entries here record the question, the
disposition, and where the mechanics now live, so that a reader who
remembers the open question can see how it closed.

Two remain open, and the session does not start until they are closed:

- **NR-5** — does the real transaction re-run the runsheet §4 probe battery?
  Not ruled by D-155; still a scope-and-clock question for the magistrate.
- **NR-9, cadence half** — immediate ping versus batched notification for the
  delegated step-6 execution. This is Ed's one-word question, presented to him
  with both seats' options and a recommendation of *immediate*.

| # | Question | Disposition | Mechanics now live at |
|---|---|---|---|
| NR-1 | Which checkout is the declared measurement checkout, and how is its venv brought into lock? | **RULED** — `-20260813`, fast-forwarded; fresh checkout is the named fallback if the relock cannot reach the lock | §1.1, both boxes |
| NR-2 | Push topology at the measurement checkout | **RULED** — pull-into-dev → push → fetch-back; plain local path, no `file://`; four-way equality asserted by running `reviewed_main` | Phase D |
| NR-3 | Publication must precede the marker build; r4-3 says the opposite | **RULED** — push-then-build; Phase E runs E1→E3→E4→E2→E5 | Phase D, Phase E; r4-3 amended |
| NR-4 | Which `--phase` does the real boundary marker build use? | **RULED** — `publication` for both build and verify; the §1.3 manifest is still produced, for C9 | Phase E preamble, §1.5 |
| NR-5 | Does the real transaction re-run the §4 probe battery? | **OPEN** | — |
| NR-6 | Real arm ×3, or the dry-run ceremony? Where is `file-09-probe P1/P2/P3`? | **RULED** — dry-run ceremony, no arm; the probe is struck as specified and replaced by named receipt assertions; P3 discharged at the shakedown GO | Phase G; r3 B-4 amended |
| NR-7 | D-151 condition 5 versus D-153 A4 | **RULED** — A4 governs; condition 5 re-scoped into two sub-intervals, not struck | `MAGISTRATE-RULING-O1.md` condition 5 (ONE home); `decision_log.md` D-151 row |
| NR-8 | Who declares "the last consuming arm", and by what artifact? | **RULED** — magistrate declares mechanically, Ed owns early termination; `campaign-close.json`; strict record order with the fixation commit first | Phase H5, §6 item 6 |
| NR-9 | Step-6 delegated but the contract says Ed confirms; cadence pending | **PART-RULED** — the contract prose is amended and the delegation is live; **the cadence is Ed's, still open** | Step-6 contract; Phase E4 |
| NR-10 | Scope of the D-150(1) live-prompt license | **RULED** — the six ruled prompts stand, plus a mandatory pre-window prompt inventory; Ed narrows any allow rule that would swallow a licensed command | §1.5, C3, C8 |
| NR-11 | One commit message cannot carry the terminal review for three packs | **RULED** — code cure at **both** parsers: `PASS`/`Tree-Oid` exactly-once, `Pack-Sha256` non-empty, duplicate-free, membership. Lands as W-2 before Phase C1 | C11; window runbook §5C |
| NR-12 | Where does the attestation commit sit, and is it the published head? | **RULED** — last commit before publication; `ATTESTATION_HEAD` is the published head, `PINSET_MINT_HEAD` stays the closure head; magistrate executes it | C11, Phase D, Phase F; r4-3 amended |
| NR-13 | Is `WINDOW-STATUS-FREEZE-GUARD-01` a hard gate on opening the freeze span? | **RULED** — yes, and earlier than asked: a custody-external sentinel guard landing **before Phase C1**, because the binding gate is the changed-set window | §1.1, C11.1 |

The full question statements are preserved below, unedited, each with its
ruling attached. They are kept because a reader who only sees the answer
cannot check whether it answers the right question.

### NR-1 — Which checkout is the `_v4` declared measurement checkout?

**RULED (D-155): branch A — `/Users/edr/JouleWise-measurement-20260813`**, fast-forwarded to the reviewed head (`49dcc49` verified as an ancestor). `-20260818` is rejected on three grounds, the decisive one being that its blanket allow rule would suppress the D-150(1) prompts. A fresh checkout is the **named fallback** if the venv relock cannot reach the lock. Mechanics: §1.1.

`docs/phase_2/window_runbook.md` §1 names
`/Users/edr/JouleWise-measurement-20260813` as the declared default "for the
current three-pack freeze", and prescribes a `JouleWise-measurement-YYYYMMDD`
convention with the chosen absolute path recorded in `window.env`. But the `_v3`
transaction executed at `/Users/edr/JouleWise-measurement-20260818`, and runsheet
§5's acceptance box forbids S-0 from touching that path at all. Both directories
exist; neither is at the reviewed head; `-20260818` is on a stale branch and
`-20260813`'s virtual environment is out of lock (`transformers 5.15.0` against
`env/mac-measurement-lock.txt`'s `5.12.1`).

**Decide:** which path, or a fresh `-2026MMDD` checkout; and how its virtual
environment is brought back into lock, since that is a `pip` operation in a
measurement environment and therefore Ed's hands.

---

### NR-2 — Push topology at the measurement checkout

**RULED (D-155): branch A — pull-into-dev → push origin → fetch-back at the measurement checkout.** The `_v3` "never push from it" doctrine is preserved verbatim. Four-way equality is asserted by RUNNING `reviewed_main` on a pack root, never by eye. The earlier draft's `file://` command form is dropped — it appears in no source. A `git fetch` is licensed inside the freeze span; a commit, a push, or any move of `refs/heads/main` is not. Mechanics: Phase D.

The marker build's `reviewed_main()` predicate requires `HEAD == refs/heads/main
== refs/remotes/origin/main` **in the repository that owns the pack roots** —
the measurement checkout. The `_v3` doctrine is "land by `git pull --ff-only
file://<measurement checkout>` from a development worktree; **never push from
the measurement checkout**". Satisfying four-way equality then requires the
measurement checkout to fetch and fast-forward its own `main` after the push.

**Decide:** is that the ruled shape (pull-into-dev → push → fetch-back), or does
`_v4` push directly from the measurement checkout? **The rehearsal forged
`origin/main` and therefore exercised none of this.**

---

### NR-3 — Publication must precede the marker build; r4-3 says the opposite

**RULED (D-155): branch A — push-then-build**, with r4-3 amended by a dated marker rather than silently rewritten. Consequence: Phase E executes E1 build → E3 render → E4 confirm → E2 verify → E5 promote, because a publication-phase verify requires the confirmation pair. Mechanics: Phase D and Phase E.

r4-3's ten-step order reads "… dry-run ceremony + marker candidate + Ed's
exact-byte step-6 → atomic publication". But `build_family_publication_marker`
refuses on `head_mismatch` unless `origin/main` already equals the head being
marked. **The written order cannot execute.** Runsheet §3.10 argues
independently that the published head must be the window-close head and cannot be
the fixation head, which is consistent with push-then-build — but no ruling
states the inversion.

**Decide:** amend the r4-3 order to place the push before the marker build, or
identify the reading under which the written order runs.

---

### NR-4 — Which marker phase does the real boundary build use?

**RULED (D-155): branch A — `--phase publication` for both the build and the verify**, with no `--candidate-manifest` on either. The §1.3 candidate manifest is **still produced**, because C9 consumes it to authenticate the executing custody tools; only the marker stops consuming it. Mechanics: Phase E preamble, §1.5.

MARKER-RULING split S-5 makes committed-blob equality "the PRODUCTION rule" and
candidate mode the S-0 accommodation, on the stated ground that "the tools do not
exist at the pinned HEAD". In the real lane they do exist as committed blobs at
the head. The CLI's phases are `candidate | publication | pre-arm | t0`; every
non-candidate phase drives the live four-way consult, which (per NR-3) becomes
available only after the push.

**Decide:** the phase for the real boundary build and the real boundary verify,
and consequently whether the real transaction needs a §1.3-style mechanical
candidate manifest at all.

---

### NR-5 — Does the real transaction re-run the §4 probe battery?

**OPEN.** D-155 does not rule this item. It remains a scope-and-clock decision for the magistrate before the session.

The brief for this runbook describes the real transaction as executing the
runsheet's "§§2–4.10 shape". §4 is thirty-odd tamper probes over throwaway case
clones, whose purpose is to prove the mechanism refuses correctly — and which the
rehearsal executed all-green at estate 10, confirming every code-derived
prediction by execution.

**Decide:** is S-0's battery the proof of record (so the real lane runs §§1–3.10
plus post-campaign fixation), or must some or all probes be re-executed at the
real head? If some: which, and where do their case clones live relative to the
frozen measurement checkout?

---

### NR-6 — Real arm, or r4-3's dry-run ceremony, in Phase G?

**RULED (D-155): branch B — the dry-run ceremony, no real arm.** `file-09-probe P1/P2/P3` is **struck as specified** (P3 is unsatisfiable inside the ceremony B-4 defines) and replaced by named assertions over the dry-run receipts; P3 is discharged at the shakedown GO receipt, and arm-side U11 at the shakedown arm. Mechanics: Phase G; `MAGISTRATE-RULING-r3.md` B-4 amendment.

Runsheet §3.9 arms and verifies all three packs at the mint head. r4-3 puts a
"dry-run ceremony (B-4 form: dry-run + file-09-probe P1/P2/P3; **NO real arm**)"
at the same point, with real arms at each window's T-0.

**Decide:** which. And if the dry-run ceremony: **the file-09-probe P1/P2/P3
procedure exists in no source read for this runbook** — it needs a home with
executable steps before the session.

---

### NR-7 — D-151 condition 5 versus D-153 A4

**RULED (D-155): D-153 A4 governs; condition 5 is re-scoped, not struck.** The parenthetical "no claim-bearing arm occurs in it" is true of the sub-interval mint → the first consuming arm, and false of the re-priced interval as a whole. ONE home for the restated condition: `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`; the D-151 index row in `docs/decision_log.md` carries a pointer.

D-151 condition 5 states that "no claim-bearing arm occurs in" the
mint-to-fixation interval. D-153 A4 re-prices that same interval as mint →
post-window fixation, up to about eight days — which by construction contains
every campaign window's arm, and campaign window arms are claim-bearing. The
terra seat read condition 5 literally and used it as one of the two grounds for
killing option beta; the adopted amendment package does not reconcile the two
texts.

**Decide:** which text governs, and restate the surviving one so a reader at the
bench cannot reach the wrong conclusion.

---

### NR-8 — Who declares "the last consuming arm", and by what artifact?

**RULED (D-155): a mechanical declaration by the magistrate, with an Ed escape.** The predicate, the two coordinates it names, the `campaign-close.json` artifact and the strict record order (declaration → freeze-off → notification → **the fixation commit first** → only then any bookkeeping) are at §2 Phase H5. Early termination, waivers and abandoned slots are Ed's.

D-153 A6 closes the changed-set window at the last consuming arm; D-153 A1 hangs
the fixation commit off the commit-freeze close that follows. Neither names the
declaring act, its transcript, or who signs it. Without that, the fixation commit
has no defined trigger and the freeze has no defined end.

**Decide:** the declaration's form, its owner, and where it is recorded.

---

### NR-9 — Step-6 is delegated; the contract still says Ed confirms; the cadence is pending

**PART-RULED (D-155).** Threads 1 and 2 are closed: the delegation is live for this transaction, and `docs/contracts/d117_step6_confirmation_table.md` has been amended to record it (authority stays `ED`, decision stays `YES`, the statement field records the delegation and what was independently recomputed). **Thread 3, the cadence, remains Ed's one-word question**, with a recommendation of *immediate*. Mechanics: Phase E4, §4.

Three loose threads on one event:

1. **D-150b delegates** the step-6 exact-byte confirmation and the terminal
   review to the magistrate, with Ed notified rather than blocked. The
   `S0-COMPLETION-RECORD.md` list of what remains for the real transaction is
   consistent with this — it names the permission prompts and the reboot, and
   does **not** name a step-6 confirmation by Ed.
2. **The contract has not caught up.** `docs/contracts/d117_step6_confirmation_table.md`
   — the declared ONE home — still reads "Before Ed is asked, the producer
   renders the final bytes… Ed's yes names `hC`." An operator following the
   contract at the bench will wait for Ed. The ONE home should record the
   delegation before execution.
3. **The notification cadence is explicitly pending.** D-150a records item 10
   ("step-6 timing: immediate ping vs batched") as explained to Ed with "his
   preference pending".

**Decide:** confirm the delegation is live for this transaction; amend the
contract's prose; settle the cadence.

---

### NR-10 — Scope of the D-150(1) live-prompt license

**RULED (D-155): branch A — the license stays exactly two command classes, six executions — plus a mandatory pre-window prompt inventory** that makes the count exact. Whether a command prompts turns on its invocation form, which the magistrate controls; the broad `settings.local.json` allows could swallow a licensed command, and if the inventory shows that, **Ed** narrows them. No agent modifies permission settings. Mechanics: §1.5, C3, C8.

D-150(1) grants the mint license as live prompts for "each `_v4`
freeze/projection command"; the r5 packet counts **six**, and the `_v3`
precedent identifies exactly two blocked command classes
(`project_identity_pins.py freeze`, `generate_arm_readiness.py freeze`). The real
transaction also runs repository-mutating commands outside those classes: the
three generator emissions, three `author_arm_readiness_evidence.py` invocations,
`build_v4_histsem_pinset.py` (the mint itself), and `build_family_marker.py`.

**Decide:** whether those are inside the granted license, and whether Ed should
expect more than six prompts. A surprise prompt at 11pm on a command nobody
warned him about is the failure this item exists to prevent.

---

### NR-11 — One commit message cannot carry the terminal review for three packs (possible blocker)

**RULED (D-155): branch D — a code cure at BOTH parsers, landing before Phase C1.** No zero-code path exists; branch E was verified mechanically empty three times. The second call site — `_verify_terminal_review` in `scripts/capture_t0_step.py`, which runs on every one of the six `capture_t0_step.py` invocations per window — was found by both adjudication seats and is absent from the question as originally written; a cure landing only in the evidence collector would still have refused at the first T-0 capture step. Semantics: `PASS` and `Tree-Oid` stay exactly-once; `Pack-Sha256` becomes non-empty, duplicate-free, containing the arming pack's digest. Zero refusal-registry cost. Mechanics: C11; window runbook §5C; code in work order W-2.

The terminal-review attestation is derived from Git commit trailers on `HEAD`
(`_derive_terminal_review`, `joulewise/arm_readiness_evidence_t0.py`). It
requires **exactly one** of each:

```
JouleWise-Terminal-Review: PASS
JouleWise-Terminal-Review-Tree-Oid: <context.head_tree_oid>
JouleWise-Terminal-Review-Pack-Sha256: <context.pack_sha256>
```

The collector builds a list per trailer name and then tests
`trailers.get(name) != [value]` — a list of exactly one element equal to the
arming context's value. The arming context is **per pack**
(`context.pack_sha256`), while under the r4-3 commit freeze all three packs arm
against the **same** `HEAD`. Three packs have three different committed pack-tree
digests. A commit message carrying three `Pack-Sha256` trailers yields a
three-element list and refuses
`evidence_author_t0_terminal_review_record_missing`; a message carrying one
satisfies one pack and refuses the other two.

The documented producer (`docs/phase_2/window_runbook.md` §5C) is written for one
pack: it sources a single campaign's `window.env`, computes one `$PACK_ROOT`
digest, and makes one empty commit. It dates from the single-campaign era and has
never been run against a three-pack family.

The registry row is `desk.terminal_review`, applicability `ALWAYS`, evaluation
phase `ARM_ONLY` — so this fires at every window's T-0, for every pack, for the
whole campaign.

**This path is unexercised.** S-0's arms ran in a clone with no live machine
window and never derived T-0 evidence; the rehearsal cannot have caught it.

**Decide:** verify the reading at the bench, and if it holds, rule the cure
before the freeze span opens — a code change to accept a per-pack trailer set, a
three-pack producer whose trailers the parser accepts, a per-pack head (which the
commit freeze forbids), or something else. This is the highest-severity item in
this list because it does not fire until the first T-0, by which time the freeze
span is open, the family is published, and the head cannot move.

---

### NR-12 — Where does the terminal-review attestation commit sit, and is it the published head?

**RULED (D-155): branch B — the attestation is the LAST commit before publication, and the magistrate executes it (D-150b).** `ATTESTATION_HEAD` is the published head; `PINSET_MINT_HEAD` remains the allowlist-contract closure head and the coordinate `hS` is computed from. Every step naming "the head" now says which. Mechanics: C11, Phase D, Phase F; r4-3 and window runbook §5C amended.

r4-3's ten-step order places the terminal-review attestation at **the common
derivation head** — before evidence authoring, before the freeze, before the
mint. `docs/phase_2/window_runbook.md` §5C's producer places it "after all
repair/freeze review is complete and before the dry run or T-0" — that is, after
the mint. These are different commits.

The choice is load-bearing because the producer makes a **real commit** (empty,
tree-preserving, but a commit). If it lands after the mint, then:

- the published head is the attestation commit, not `PINSET_MINT_HEAD`;
- the marker is built at the attestation commit;
- `PINSET_MINT_HEAD` remains the allowlist-contract closure head (D-153 A6), so
  the closure head and the published head are two different commits, and every
  step that names "the head" must say which;
- the changed-set arithmetic is unaffected — an empty commit adds no paths — so
  the 112 closure still holds.

If instead it lands at the derivation head, its trailers bind that tree, and the
window runbook's own rule ("trailers from an ancestor do not transfer") means the
attestation is dead by arm time, when the tree has moved.

**Decide:** which placement governs for `_v4`, and restate the affected heads
throughout Phase D so no step is ambiguous about which commit it means.

---

### NR-13 — Is `WINDOW-STATUS-FREEZE-GUARD-01` a hard gate on opening the freeze span?

**RULED (D-155): yes — a code guard, and earlier than this question assumed.** The binding deadline is not the freeze span but the **changed-set window, which opens at `EVIDENCE_DERIVATION_HEAD`**, because the guard's own files are not among the 112. It lands **before Phase C1**, as a custody-external sentinel with a refuse-before-write branch and byte-identical out-of-span behaviour. D-150a's visibility promise is unaffected: the committed channel is the push notification, not the git push. Mechanics: §1.1, C11.1; code in work order W-2.

Not strictly a ruling gap — the kernel row exists (D-153 W4) with status
`queued` — but it needs an explicit disposition. The hazard is verified by
inspection and not yet executed: `scripts/window_status.sh` commits and pushes
`WINDOW_STATUS.md`, a path outside the 112, which inside the freeze span both
breaks the commit freeze and adds changed-set residue that refuses every
subsequent arm.

**Decide:** land it before Phase D, or record an explicit operational fence (the
script is not run during the span) with an owner.

---

# 8. Sources

Read in preparing this runbook; cited above at the point each one binds.

- `docs/process_traces/2026-08-22-t20/nr-synthesis-ruling.md` — **D-155**, the
  magistrate synthesis that rules eleven of the thirteen §7 questions, with the
  two independent adjudication seats recorded verbatim beside it in
  `nr-seat-opus.md` and `nr-seat-sol.md`, over the mechanically-assembled
  `nr-adjudication-packet.md`.
- `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md` — the proven instrument.
- `docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md` — what S-0 proved
  and what it deferred here.
- `docs/process_traces/2026-08-22-t20/ERRATA.md` — E-1's CI-verification rule.
- `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md` and
  `opus-contract-refutation.md` §4 — D-151 and the normative nine conditions.
- `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`
  — the marker design and splits S-1 through S-5.
- `docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md` —
  D-153 amendments A1–A6 and work orders W1–W5.
- `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md` — r4-1
  through r4-7, especially r4-3's order and the commit freeze.
- `docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md` — the
  V-7 Ed packet.
- `docs/decision_log.md` — D-148, D-150, D-150a, D-150b, D-151, D-153.
- `docs/contracts/d117_step6_confirmation_table.md` — the ONE home for `C`.
- `docs/phase_2/window_runbook.md` — `MEASUREMENT_REPO` and the window rules that
  govern what follows this session.
- `docs/process/ed-s5-mint-decision-2026-08-19.md` — the `_v3` precedent for the
  blocked command classes and the landing route.
- `docs/process_traces/2026-08-23-speed/TEST-SPEED-01-evidence.md` — suite timing
  figures used in §3.
- `docs/run_reports/2026-08-25-t23-t24-session.md` §§8–9a — estate 10 and the
  ten-estate record.
