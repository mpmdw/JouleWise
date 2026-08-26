# The real `_v4` freeze transaction — operator runbook

**Status: DRAFT for magistrate ruling. Do not execute until §7 is empty.**

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

**The commit freeze, and what "window close" means.** From Ed's terminal-review
step onward, **no ordinary commit lands on `main`** — not from this machine, not
from any other session, not from a status script. The freeze runs through the
*last consuming measurement window* of the campaign, which may be a week away.
D-153 A1 fixes the vocabulary: **"window close" means the close of that commit
freeze**, not the mint and not the end of any single night's measurement. The
mint-side event has its own name, **allowlist-contract closure**, at the commit
called `PINSET_MINT_HEAD`.

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
  `docs/phase_2/window_runbook.md` §1. **Which directory this is for `_v4` is
  UNRESOLVED — see §7 NR-1.** Two candidates exist on disk today:
  `/Users/edr/JouleWise-measurement-20260813` (on `main` at `49dcc49`, clean)
  and `/Users/edr/JouleWise-measurement-20260818` (on branch
  `impl/r2-s0-mint-resolver` at `94dc3b34`, the `_v3` transaction's home, and
  explicitly forbidden to S-0 by runsheet §5).
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
  `env/mac-measurement-lock.txt`.** As of 2026-08-25 the `-20260813` checkout's
  `.venv` reports `transformers 5.15.0` against a lock of `5.12.1` — **out of
  lock**. Reconciling it is a `pip` operation in a measurement environment,
  which is Ed's hands and must be settled before the session, not during it.
- [ ] **`WINDOW-STATUS-FREEZE-GUARD-01` has landed.** `scripts/window_status.sh`
  currently commits *and pushes* `WINDOW_STATUS.md`, a path outside the 112. A
  single status publication inside the freeze span both breaks the commit freeze
  and adds changed-set residue that will refuse every subsequent arm. The kernel
  row is registered (D-153 work order W4) and its status is **`queued`, not
  done**. This is a hard blocker for the freeze span, which begins in this
  session.
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
  reviewed head (runsheet §1.3) and its digest recorded.
- [ ] The custody tools materialised and hashed (runsheet §2.1's allowlist
  contract checker, §2.2's census checker).
- [ ] The anchor map re-checked 15/15 against the reviewed head (runsheet §1.1's
  anchor block). A drifted anchor is a precondition defect: stop, re-derive on
  `main` through the review lane.
- [ ] The registry-v1 literal sweep run and every hit classified (runsheet §1.3).
- [ ] **The full-suite wall clock measured on a scratch checkout.** See §3 — it
  is plausibly the longest single step in the session and nothing in custody
  records it.
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
session — see §7 NR-9; the step-6 contract's own prose has not yet been updated
to record the delegation.)

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
own `.venv/bin/python`**, not a stdlib-only interpreter. The rehearsal's
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

This is runsheet §§3.1–3.7 executed against the real checkout. It is the part
Ed's presence is actually required for, because the six permission prompts fire
inside it.

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
python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
```

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

### C5b — The terminal-review attestation (MAGISTRATE under D-150b)

r4-3 places a terminal-review attestation here, at the common derivation head,
and calls it "tree-preserving". Under D-150b it is delegated to the magistrate
and executed mechanically. The mechanism is worth stating exactly, because it is
not an artifact in custody — **it is three trailers on a Git commit message**:

```
JouleWise-Terminal-Review: PASS
JouleWise-Terminal-Review-Tree-Oid: <the commit's own tree object id>
JouleWise-Terminal-Review-Pack-Sha256: <that pack's committed pack-tree digest>
```

`_derive_terminal_review` in `joulewise/arm_readiness_evidence_t0.py` reads
`HEAD`'s commit message, requires **exactly one** occurrence of each trailer, and
requires the tree and pack values to equal the arming context's. That is what
"tree-preserving" means: the attestation rides on a commit that already exists
and binds that commit's tree, so signing it adds no commit and moves no tree.

The producer step is documented — `docs/phase_2/window_runbook.md` §5C, "Lead-owned
terminal-review attestation": at the reviewed tree, with a clean status, compute
`TREE_OID` and the committed pack digest and make **one empty commit** carrying
the three trailers, then land it as reviewed `main` so the measurement checkout,
local `main`, and `origin/main` all name it. An empty commit preserves the tree,
which is what makes the attestation "tree-preserving". Trailers on an ancestor do
not transfer: a later tree or pack change requires a new attestation commit.

Three consequences bind this transaction, and two of them are unresolved:

- The evidence row is `desk.terminal_review`, applicability **`ALWAYS`**,
  evaluation phase **`ARM_ONLY`** (row registry `d117_row_registry_v2.json`). It
  is therefore *not* one of the eleven generic freeze-time kinds, and it is
  checked at **arm** time — every window, every pack, for the whole campaign.
  The rehearsal never derived it: its arms ran in a clone with no live machine
  window.
- The documented producer is **single-pack** — it reads one `$PACK_ROOT` from a
  single campaign's `window.env` — and the trailer parser admits **exactly one**
  `Pack-Sha256` value. The `_v4` family is three packs sharing one frozen head.
  **See §7 NR-11.**
- The producer's placement ("after all repair/freeze review is complete and
  before the dry run or T-0") puts the attestation commit *after* the mint,
  while r4-3 places it *at the common derivation head*, before evidence
  authoring. Those are different commits, and which one is published depends on
  the answer. **See §7 NR-13.**

The marker's own `terminal_review` block does **not** depend on any of this: the
builder synthesises it from the reviewed head's tree object id
(`joulewise/arm_readiness.py`, marker construction), so the Phase E build does
not refuse for want of an attestation commit.

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
python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4 --predecessor-pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
```

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

**Therefore the mint head must already be published before the marker can be
built.** r4-3's written order is "marker candidate + Ed's exact-byte step-6 →
atomic publication", which places publication *after* the marker. That order
cannot execute. **See §7 NR-3** — this inversion needs a ruling before the
session, not a decision at the bench.

Assuming the ruling resolves in favour of push-then-build, the phase is:

| Step | Who | What |
|---|---|---|
| D1 | MAGISTRATE | From a **development** worktree, `git pull --ff-only file:///<measurement checkout> main`, then push that to `origin`. The `_v3` doctrine is that nothing is ever pushed *from* the measurement checkout; whether `_v4` keeps it is **§7 NR-2**. |
| D2 | MAGISTRATE | In the measurement checkout: `git fetch origin`, confirm `HEAD == refs/heads/main == refs/remotes/origin/main == PINSET_MINT_HEAD`, tree clean. |
| D3 | MAGISTRATE | Send the D-150a state-change notification: published, freeze span open. |

**`PINSET_MINT_HEAD` is now the published head, and it is also the window-close
head.** Those are the same commit, and the reason is worth stating because it
resolves an apparent contradiction: the commit freeze means `main` does not move
between publication and the close of the last window, so the head that was
published *is* the head at which the freeze closes. Runsheet §3.10's argument —
"the published head is the WINDOW-CLOSE head, and fixation follows publication"
— is exactly this, and it is corroborated inside the tool: publication-lane
marker replay refuses `head_unpublished` unless the marker's own publication head
equals live `origin/main`, so a later fixation commit could never be the
published head the marker admits.

**From D1 onward, an ordinary commit to `main` breaks the transaction.** Arm
receipts bind the reviewed main they were produced against
(`_verify_arm_receipt` requires equality), so any commit — including one line of
`WINDOW_STATUS.md` — invalidates every armed pack for the rest of the campaign.

---

## Phase E — Marker, step-6 table, and the delegated confirmation (MAGISTRATE)

### E1 — Build the marker (runsheet §3.8)

`scripts/build_family_marker.py --repository <measurement checkout> --head
PINSET_MINT_HEAD --pack-root ×3 --output <custody>/marker-candidate/…`.

**Which `--phase` the real transaction uses is unresolved — see §7 NR-4.** The
rehearsal used `--phase candidate` with `--candidate-manifest`, because the
custody tools did not exist at the pinned head of a clone. In the real lane they
do exist as committed blobs, and MARKER-RULING split S-5 makes committed-blob
equality "the PRODUCTION rule" with candidate mode the S-0 accommodation. The
CLI offers `candidate | publication | pre-arm | t0`.

Assert, whichever phase: the marker sidecar was written; the
`conditional_paths_deferred` disclosure names gate `R1_DIGEST_CONDITIONAL`,
`deferred_paths` exactly `[the successor pinset path]`, and the four enforcing
entry points `["arm", "freeze", "verification", "marker-replay"]`. That
disclosure is the visible form of a structural fact: the marker build cannot
check the `C → S` edge, because `C` carries the marker's own digest and so cannot
exist yet. An **empty** `deferred_paths` would be the positive statement that
nothing was deferred, which is why the key is required rather than optional.

### E2 — Verify the marker (runsheet §3.8)

`scripts/verify_family_marker.py` at the same phase. Assert `status: PASS` and
that the reported `origin_main_commit` is the **real** published head.

*Real-lane difference:* the rehearsal recorded a `FORGED_ORIGIN_MAIN_OID` and
classified the result "forged-`origin/main`-conditional". **There is no forged
OID in the real lane and no such classification.** Any transcript carrying that
phrase in this session is a defect.

### E3 — Render the step-6 confirmation table (MAGISTRATE)

Render `C` exactly per `docs/contracts/d117_step6_confirmation_table.md`: strict
canonical JSON (UTF-8, sorted keys, two-space indent, one trailing newline, no
timestamp, no self-digest), plus its GNU-form `.sha256` sidecar. Its fields bind
the marker digest `hM`, the successor digest `hS`, the registry digest, the
published head and its tree, and the three member rows in ALPHA/BETA/GAMMA
order. `confirmation.authority` is `"ED"`, `confirmation.decision` is `"YES"`,
and `confirmation.statement` is free text.

### E4 — Execute the delegated confirmation (MAGISTRATE, D-150b)

This is what replaces "Ed types YES". It has three parts and the independence
requirement is the whole point of it:

1. **Recompute `hM` from the marker file on disk**, and `hS` from the bytes
   committed at `PINSET_MINT_HEAD` for the successor pinset path — read from the
   artifacts, never taken from the producing session's report.
2. **Evaluate equality** against what the rendered table asserts, and against
   the mint-time `hS` record from C10 step 3. Any mismatch is a refusal and a
   ping to Ed, never a re-render.
3. **Write the delegation into `confirmation.statement`**: that this
   confirmation was executed under D-150b's standing delegation, and what was
   independently recomputed. Then compute `hC` over the final bytes and record
   it **in transaction custody only**. `hC` never enters a repository path, in
   this transaction or any other.

Then notify Ed. **The notification cadence — immediate ping versus batched — is
Ed's item 10 from the D-150a packet and his preference is recorded as PENDING.
See §7 NR-9.**

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

- `PUBLISHED_HEAD` = `PINSET_MINT_HEAD` — **the published window-close head, not
  a fixation commit.** The runsheet's guard refuses an unsubstituted block
  rather than running against the literal placeholder.
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

## Phase G — Arm, or the dry-run ceremony (MAGISTRATE)

**Which of these the real transaction performs is unresolved — see §7 NR-6.**

The rehearsal's §3.9 armed and verified all three packs at `PINSET_MINT_HEAD`,
with the confirmation pair supplied on every call, and asserted three things:
the residue at the mint head is empty; neither R1 refusal code appears; and the
arm receipt carries all eleven generic kinds. r4-3's written order instead puts
a *dry-run ceremony* here — "dry-run + file-09-probe P1/P2/P3; NO real arm" —
with real arms deferred to each window's T-0.

If the ruling is "arm here", one further real-lane obligation attaches that S-0
explicitly could not discharge: under the measurement environment the arm-side
U11 re-verification leg **must pass**, where in the rehearsal it refused by
design under a stdlib interpreter (runsheet §7 O-5). That passing leg is the
real transaction's own evidence, and it is the last open caution in the
rehearsal record.

---

## Phase H — Close the session (MAGISTRATE)

| Step | What |
|---|---|
| H1 | Seal transaction custody read-only. Every command's stdout, stderr and exit code is a preserved triplet; the magistrate reads all of them. |
| H2 | Record the state in `RUN_STATE.md`'s header line: transaction published, push freeze ON, span open. |
| H3 | Send the D-150a notification: campaign span open; per-window notices to follow. |
| H4 | Record the registered limitation (D-153 W5): a mid-campaign non-configuration cure forces a new family generation. There is no patching a published `_v4`. |

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
| C5b | Terminal-review attestation commit | MAGISTRATE | 5 min, **if it belongs here at all** | Placement disputed (NR-12); three-pack form unresolved (NR-11). |
| C6 | Evidence stamping ×3 | SCRIPTED | 3–6 min | Starts the 168 h clock and the boot binding. |
| C7 | Sacrificial pre-mint check | SCRIPTED | 4–8 min | Clone (~650 MB) plus three readiness freezes. |
| C8 | **Freeze ×3 + prompts 4–6** | SCRIPTED + **ED** | 3–6 min | |
| C9 | Tool authentication | SCRIPTED | <1 min | |
| C10 | Mint + close contract + chain verify | SCRIPTED | 3–6 min | |
| | **Phase C subtotal** | | **35–70 min** | Ed present throughout. |
| D | Publication | MAGISTRATE | 5–10 min | |
| E1–E2 | Marker build + verify | MAGISTRATE | 3–6 min | |
| E3–E5 | Table render, delegated confirmation, promote | MAGISTRATE | 20–40 min | Careful desk work; the independent recomputation is the point. |
| F1–F2 | Four-way + publication replay | SCRIPTED | 2–5 min | |
| F3 | **Full suite at the published head** | SCRIPTED | **45–180 min** | See below. |
| G | Arm ×3, or the dry-run ceremony | MAGISTRATE | 10–30 min | Depends on NR-6. |
| H | Close-out | MAGISTRATE | 15 min | |
| | **TOTAL, machine time** | | **≈ 3.5 – 7 hours** | |
| | **TOTAL, Ed's presence** | | **≈ 1 hour** (Phases B + C) | |

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
| Phase D3 | Published at `<head>`; freeze span open; machine is normal use minus pushes and reboots until the campaign closes. |
| Phase E4 | Step-6 confirmation executed under the D-150b delegation, with what was recomputed. *(Cadence pending — NR-9.)* |
| Each window | "T-0 at ~HH:MM, machine untouchable until morning." |
| Each window end | Window closed. |
| Campaign end | Campaign done; freeze **OFF**. |

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
**a reboot in this range ends the attempt**: the 33 generic receipts carry the
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
   own nights, under `docs/phase_2/window_runbook.md`.
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
5. **No arm that consumes a measurement.** Whatever Phase G resolves to, no
   claim-bearing measurement is consumed in this session; the packs are armed or
   dry-run only.
6. **No declaration that the campaign is over.** The "last consuming arm" that
   closes the changed-set window (D-153 A6) happens at the end of the campaign,
   by an act that **is not currently defined anywhere** — §7 NR-8.
7. **No `T0-UNATTENDED-01`.** D-150(4) makes `_v4` windows gate on that work
   order's landing; its kernel status today is `queued`. That gates the windows,
   not this session, but it must land before the first T-0.

---

# 7. NEEDS MAGISTRATE RULING BEFORE THE WINDOW

Each item below is a question this runbook could not answer from the sources.
None of them should be decided at the bench with Ed waiting.

| # | Question | Bites at | Severity |
|---|---|---|---|
| NR-1 | Which checkout is the declared measurement checkout, and how is its venv brought into lock? | Before Phase A | blocks the session |
| NR-2 | Push topology: pull-into-dev → push → fetch-back, or push from the measurement checkout? | Phase D1 | blocks the session |
| NR-3 | Publication must precede the marker build; r4-3's written order says the opposite | Phase D/E | blocks the session |
| NR-4 | Which `--phase` does the real boundary marker build use? | Phase E1 | blocks the session |
| NR-5 | Does the real transaction re-run the §4 probe battery? | Phase G | scope + clock |
| NR-6 | Real arm ×3, or r4-3's dry-run ceremony? And where is file-09-probe P1/P2/P3? | Phase G | blocks the session |
| NR-7 | D-151 condition 5 ("no claim-bearing arm in the interval") versus D-153 A4's re-priced interval | Campaign | doctrine coherence |
| NR-8 | Who declares "the last consuming arm", and by what artifact? | Campaign end | fixation has no trigger |
| NR-9 | Step-6 is delegated (D-150b) but the contract still says Ed confirms; cadence pending | Phase E4 | wrong-person risk |
| NR-10 | Scope of the D-150(1) live-prompt licence beyond the six commands | Phase C | surprise prompts |
| NR-11 | One commit message cannot carry the terminal review for three packs | **First T-0, after publication** | **highest — possible blocker** |
| NR-12 | Where does the attestation commit sit, and is it the published head? | Phase C5b / D | head ambiguity |
| NR-13 | Is `WINDOW-STATUS-FREEZE-GUARD-01` a hard gate on opening the freeze span? | Freeze span | breaks every arm |

---

### NR-1 — Which checkout is the `_v4` declared measurement checkout?

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

Runsheet §3.9 arms and verifies all three packs at the mint head. r4-3 puts a
"dry-run ceremony (B-4 form: dry-run + file-09-probe P1/P2/P3; **NO real arm**)"
at the same point, with real arms at each window's T-0.

**Decide:** which. And if the dry-run ceremony: **the file-09-probe P1/P2/P3
procedure exists in no source read for this runbook** — it needs a home with
executable steps before the session.

---

### NR-7 — D-151 condition 5 versus D-153 A4

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

D-153 A6 closes the changed-set window at the last consuming arm; D-153 A1 hangs
the fixation commit off the commit-freeze close that follows. Neither names the
declaring act, its transcript, or who signs it. Without that, the fixation commit
has no defined trigger and the freeze has no defined end.

**Decide:** the declaration's form, its owner, and where it is recorded.

---

### NR-9 — Step-6 is delegated; the contract still says Ed confirms; the cadence is pending

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
