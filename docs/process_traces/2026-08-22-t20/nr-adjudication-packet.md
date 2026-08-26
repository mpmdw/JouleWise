# NR adjudication packet — the 13 needs-ruling items, mechanically assembled

Companion to `real-transaction-runbook.md` §7. This file carries **no
recommendation** and no preferred answer. It exists so an adjudication seat can
rule from primary evidence instead of from a runbook's paraphrase.

## What this document is

For each of the thirteen items the runbook could not answer, this packet
supplies four things and nothing else:

- **(a) Question** — one neutral sentence.
- **(b) Primary evidence** — the exact bytes of the contract, ruling, or code
  that decide it, quoted with path and line numbers. Every quotation below was
  read from the source file at the branch head, not copied from the runbook.
- **(c) Answer space** — the candidate answers, each with its *mechanical*
  consequence: what executes, what refuses with which code, and what file has to
  be edited at which line.
- **(d) Class** — `RULING` (a seat must decide), `OPERATOR-FIX` (a fact was
  established; someone performs an action), or `ALREADY-ANSWERED-BY` (an
  existing ruling disposes of it, cited).

Where the runbook's paraphrase differs from the source, this packet says so in a
**Paraphrase check** note. Those notes are findings of assembly, not rulings.

**Terms used below, defined once at first use:**

- **four-way equality** — the predicate `reviewed_main()` computes: the working
  tree is clean *and* `HEAD` == `refs/heads/main` == `refs/remotes/origin/main`.
  "Four-way" counts the tree, `HEAD`, local `main`, and `origin/main`. Quoted in
  full under NR-2.
- **trailer** — a `Name: value` line inside a Git commit *message* (not a Git
  note, not a header). The terminal-review attestation is carried this way.
- **the 112** — the changed-set allowlist: 112 repository paths that may change
  between an evidence receipt's derivation commit and the reviewed `HEAD`
  without refusing an arm. Any path outside it that changes is "changed-set
  residue".
- **freeze span / commit freeze** — r4-3's rule that the measurement checkout's
  `main` takes no commits from the terminal-review attestation through window
  close. Quoted in full under NR-13.
- **T-0** — the moment a measurement window arms: the point at which the
  per-window evidence is derived and the readiness rows are evaluated.

Ordering below is by blocking severity as the runbook ranks it, then by when the
item first fires in the operator sequence.

---

# NR-11 — One commit message and three packs

**Class: RULING** (unexercised code path; the reading below was verified against
the source, and the source says what the runbook says it says).

## (a) Question

Under the r4-3 commit freeze all three packs arm against the same `HEAD`, but
the terminal-review attestation is derived from commit-message trailers that
must equal a **per-pack** value — so which of (code change / new producer /
per-pack head / other) governs, and is it landed before the freeze span opens?

## (b) Primary evidence

### The collector

`joulewise/arm_readiness_evidence_t0.py:919-944`, verbatim:

```python
def _git_message(context: _Context) -> str:
    value = _readiness._git_text(context.repository, "show", "-s", "--format=%B", "HEAD")
    if value is None:
        raise _underivable("TERMINAL_REVIEW", "HEAD commit message is unreadable")
    return value


def _derive_terminal_review(context: _Context) -> _DerivedRow:
    kind = "TERMINAL_REVIEW"
    message = _git_message(context)
    trailers: dict[str, list[str]] = {}
    for line in message.splitlines():
        match = _re.fullmatch(r"(JouleWise-Terminal-Review(?:-Tree-Oid|-Pack-Sha256)?):\s*(\S+)", line)
        if match:
            trailers.setdefault(match.group(1), []).append(match.group(2))
    expected = {
        "JouleWise-Terminal-Review": "PASS",
        "JouleWise-Terminal-Review-Tree-Oid": context.head_tree_oid,
        "JouleWise-Terminal-Review-Pack-Sha256": context.pack_sha256,
    }
    if any(trailers.get(name) != [value] for name, value in expected.items()):
        raise _refuse(
            kind,
            "evidence_author_t0_terminal_review_record_missing",
            "HEAD commit lacks the exact PASS/tree/pack terminal-review trailers",
        )
```

Three mechanical facts follow from those exact bytes:

1. `trailers` maps each trailer name to a **list**, appending one entry per
   matching line (`setdefault(...).append(...)`, `:932`).
2. The test at `:939` is `trailers.get(name) != [value]` — a list of **exactly
   one** element equal to the expected value. Two or three `Pack-Sha256` lines
   produce a two- or three-element list, which is `!=` a one-element list.
3. `_re.fullmatch` on the whole line means a trailer with a trailing comment, a
   leading space, or an internal space in the value does not match at all.

### The value is per pack

`context.pack_sha256` is set once per authoring invocation, from the pack being
authored — `joulewise/arm_readiness_evidence_t0.py:1944-1950`:

```python
    context = _DerivationContext(
        pack_root=root,
        repository=repository,
        ...
        pack_sha256=pack_sha,
```

where `pack_sha` comes from `_readiness.committed_pack_tree_sha256(root)`
(`:1940`) — the digest of **that** pack's committed tree. Three packs with
different committed trees therefore have three different `pack_sha256` values.
`context.head_tree_oid`, by contrast, is the same for all three under one head
(`:1929`, `head_tree = reviewed["head_tree_oid"]`).

### The documented producer is single-pack

`docs/phase_2/window_runbook.md:815-846`, verbatim (excerpted):

```
**Lead-owned terminal-review attestation — required producer step.** After
all repair/freeze review is complete and before the dry run or T-0, the lead
operates at the reviewed tree, computes the committed pack digest, and creates
one empty attestation commit. This is not delegated and is not an Ed hardware
step:
```

```sh
cd /Users/edr/JouleWise-measurement-20260813
. /Users/edr/JouleWise-window-custody/d117-alpha-YYYYMMDD/readiness/window-plan/window.env
test -z "$(git status --porcelain=v1 --untracked-files=all)"
TREE_OID="$(git rev-parse HEAD^{tree})"
PACK_SHA256="$(.venv/bin/python - "$PACK_ROOT" <<'PY'
import sys
from joulewise.arm_readiness import committed_pack_tree_sha256
print(committed_pack_tree_sha256(sys.argv[1]))
PY
)"
git commit --allow-empty --cleanup=verbatim \
  -m 'JouleWise terminal review attestation' \
  -m 'JouleWise-Terminal-Review: PASS' \
  -m "JouleWise-Terminal-Review-Tree-Oid: $TREE_OID" \
  -m "JouleWise-Terminal-Review-Pack-Sha256: $PACK_SHA256"
```

It sources **one** `window.env` (hence one `$PACK_ROOT`), computes **one**
`$PACK_SHA256`, and makes **one** commit. `window_runbook.md:843-846` adds:

```
A later tree or pack change requires a new reviewed attestation
commit; trailers from an ancestor do not transfer.
```

### The row fires at every window

`configs/arm_readiness/d117_row_registry_v2.json:806-815`, verbatim:

```json
    {
      "applicability_rule": "ALWAYS",
      "evaluation_phase": "ARM_ONLY",
      "predicate_id": "desk.terminal_review.v1",
      "required_evidence_kinds": [
        "TERMINAL_REVIEW"
      ],
      "row_id": "desk.terminal_review"
    },
```

and its freshness binding at `:434-437`:

```json
      {
        "freshness_policy_id": "r1.execution_bound.t0_procedural_6h.v1",
        "row_id": "desk.terminal_review"
      },
```

`ALWAYS` + `ARM_ONLY` + a 6-hour freshness policy means: evaluated at every
window's T-0, for every pack, for the whole campaign — and re-derived each time,
never reused from an earlier window.

### Why S-0 could not have caught it

`docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md:30-33`, verbatim:

```
REMAINING FOR THE REAL TRANSACTION (not S-0's scope): Ed's D-150(1) live
permission prompts and D-150a reboot; a quiet machine window; the real
commit-freeze window close; the published-green half (§3.10's deferred
block) at the real published head; post-window fixation ordering per D-153.
```

and `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2298-2299`:

```
so it is never read as a finding. Live arm-side U11 re-verification is proven by
the real transaction in the measurement environment, not by S-0.
```

S-0's arms ran in a clone under the stdlib interpreter with a forged
`origin/main`; no T-0 evidence authoring against a live window occurred, so
`_derive_terminal_review` was never exercised in the three-pack shape.

## (c) Answer space

**A. One commit carrying three `Pack-Sha256` trailers.**
Executes: nothing new to write; one commit, three trailer lines.
Refuses: all three packs, at `:939`, with
`evidence_author_t0_terminal_review_record_missing` — the list has three
elements, `!= [value]` for every pack.

**B. One commit carrying one `Pack-Sha256` trailer.**
Executes: the one pack whose digest is named.
Refuses: the other two, same code, same line.

**C. Three heads, one attestation each.**
Executes: each pack arms against its own head.
Forbidden by r4-3's commit freeze
(`docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md:57-60`,
quoted under NR-13) and by the marker's single published head — see NR-3.

**D. Code change: accept a per-pack trailer set.**
Edits: `joulewise/arm_readiness_evidence_t0.py:928-944` — the parse loop and the
`expected`/`any(...)` comparison. The narrowest shape that satisfies all three
packs from one message is to require `PASS` and `Tree-Oid` exactly once, and
`context.pack_sha256` to be **a member of** the `Pack-Sha256` list rather than
its sole element.
Consequence: the pre-derivation candidate is already landed and reviewed; this
is a code delta inside the freeze span unless it lands before the attestation
commit. Also touches `docs/phase_2/window_runbook.md:815-846` (the producer must
emit three `Pack-Sha256` lines) and any regression asserting the current
one-element semantics.
Downstream: a `Pack-Sha256` list weakens the binding from "this commit reviewed
this pack" to "this commit reviewed a set containing this pack" — a
seat-visible semantic change, stated here without a position on it.

**E. A three-pack producer whose trailers the *current* parser accepts.**
No such message exists: any message satisfying pack 1 fails packs 2 and 3 under
the exactly-one rule (see A and B). This branch is mechanically empty unless the
parser changes, i.e. it collapses into D.

**F. Do not derive the row.**
Requires editing `configs/arm_readiness/d117_row_registry_v2.json:806-815`
(`applicability_rule` or `evaluation_phase`) — dropping a mechanism, which the
lieutenant is forbidden to decide alone (CLAUDE.local.md rule 11).

**Timing constant across every branch:** the row is `ARM_ONLY`, so nothing fires
until the first T-0. By then, under r4-3, the freeze span is open, the family is
published, and the head cannot move.

## Paraphrase check

The runbook's §7 NR-11 text matches the source in every load-bearing particular:
the exactly-one list semantics, the per-pack `context.pack_sha256`, the
single-pack producer, and the `ALWAYS` / `ARM_ONLY` registry row all verify
verbatim. One addition of assembly: the `_re.fullmatch` anchoring at `:930` also
makes any trailer line with a trailing token or comment invisible to the
collector, which is not mentioned in §7 and is a second way a hand-written
three-pack message can refuse.

---

# NR-3 — Publication before the marker build

**Class: RULING** on the r4-3 order text; the substance is
**ALREADY-ANSWERED-BY** `s0-runsheet-r4.md` §3.10 and D-153 A1 + A3 (below), but
no ruling states the inversion of r4-3's written sequence.

## (a) Question

r4-3's written order puts the marker candidate before publication, while the
marker code requires `origin/main` to already equal the head being marked — so
is the r4-3 order amended to push-then-build, or is there a reading under which
the written order executes?

## (b) Primary evidence

### The written order

`docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md:46-60`,
verbatim and complete:

```
## r4-3 (ORDER — supersedes r1 R-4.5's kernel-last)

The converged 10-step order (Sol's F3 formulation): S-0 → all
registry/code/marker-consumer/scheduler/reference commits → U11 ×3
committed → kernel/runbook/custody + canonical at the final
pre-evidence tree → Ed's tree-preserving terminal-review attestation
(THE common derivation head) → evidence ×3 at that head, one commit
→ freeze-0004 ×3 → dry-run ceremony (B-4 form: dry-run +
file-09-probe P1/P2/P3; NO real arm) + marker candidate + Ed's
exact-byte step-6 → atomic publication → published-head suite with
zero further ordinary commits, then shakedown → windows with the
checkout pinned. Docs-only commits to main DISARM T-0
(exact_match=false — executed, sitting §6.2): the runsheet carries a
commit-freeze on the measurement checkout's main from attestation
through window close.
```

### What the build actually requires

`joulewise/arm_readiness.py:10664-10667`, verbatim:

```python
    reviewed = reviewed_main(roots[0])
    if reviewed["head_commit"] != head or reviewed["exact_match"] is not True:
        diagnostic = "worktree_dirty" if reviewed["clean"] is not True else "head_mismatch"
        raise FamilyPublicationError(diagnostic, "marker build requires strict four-way reviewed main")
```

`exact_match` is defined at `joulewise/arm_readiness.py:4912` (full function
quoted under NR-2) as `clean and head == local_main == origin_main and head !=
"unavailable"`. So the build refuses `head_mismatch` unless `origin/main`
already **is** the head being marked.

**This check is not phase-gated.** It sits above every `phase` branch in
`build_family_publication_marker`, so a *candidate* build needs it too. That is
why S-0 forged the ref: `s0-runsheet-r4.md:2148-2149`:

```zsh
FORGED_ORIGIN_MAIN_OID=$(git -C "$CLONE" rev-parse refs/remotes/origin/main)
record_env FORGED_ORIGIN_MAIN_OID "$FORGED_ORIGIN_MAIN_OID"
```

### The independent argument already on record

`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2622-2644`, verbatim
(excerpted):

```
**The published head is the WINDOW-CLOSE head, and fixation follows
publication.** r4 said acceptance waits until "the lead actually publishes the
accepted fixation head." That names the wrong commit and rebuilds the exact
collision D-153 A6 was written to break. Two ruled facts settle it. Under
**D-153 A1**, fixation is the FIRST COMMIT AFTER the r4-3 commit-freeze window
close — so the fixation commit does not exist yet when the window closes, and
the head that closes the window is the head that gets published.
```

```
There is a mechanical corroboration inside the tool: publication-lane marker
replay refuses `head_unpublished` unless the marker's own
`publication_git.head_commit` equals live `origin/main`
(`arm_readiness.py:10913-10919`). The marker is built BEFORE fixation, at the
head whose bytes it binds. So the tool itself will only admit a published head
that the pre-fixation marker names — which is the window-close head, never a
later fixation commit.
```

The refusal it cites, at `joulewise/arm_readiness.py:10917-10922`, verbatim:

```python
    if marker["publication_git"]["head_commit"] != live["origin_main_commit"]:
        raise FamilyPublicationError(
            "head_unpublished",
            "marker publication head is not the current origin/main -- an old "
            "published head or an unpushed head cannot gate",
        )
```

### The ruled anchors

`docs/decision_log.md:180` (D-153), verbatim excerpt:

```
(A1) D-151 condition 3: "window close" = the r4-3 COMMIT-FREEZE CLOSE (after the
LAST consuming window); the mint-side event is ALLOWLIST-CONTRACT CLOSURE at
`PINSET_MINT_HEAD`; the fixation commit is the first commit after window close
```

```
(A3, clarification) condition 4: published-head green required and achievable
without the byte pin.
```

## (c) Answer space

**A. Amend r4-3's order to push-then-build.**
Executes: the atomic publication (push) moves ahead of "marker candidate + Ed's
exact-byte step-6" in the ten-step sequence. Every gate then finds four-way
equality and passes.
Edits: `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md:51-54`
(the order sentence), and any operator text keyed to it.
Interaction: the step-6 table carries the marker digest `hM`
(`docs/contracts/d117_step6_confirmation_table.md:21-25`), so under this branch
the confirmation event necessarily follows publication. Whether the confirmation
can follow publication is itself NR-9's subject.

**B. Keep the written order and find a satisfying reading.**
The only reading in which "marker candidate" precedes publication and executes
is the S-0 shape: a candidate build against a *forged* `origin/main`. In the real
lane there is no forged ref and the build refuses `head_mismatch` at
`arm_readiness.py:10667`. This branch requires a stated mechanism for satisfying
four-way equality pre-push, and no source read for this packet supplies one.

**C. Rule that "marker candidate" in r4-3 means the mechanical candidate
manifest (S-0's §1.3 artifact), not a marker build.**
Executes: nothing at that step; the real marker is built after the push.
Requires: an explicit statement of what the pre-publication artifact *is* — see
NR-4, which asks the same question from the phase side.

**Constant across A–C:** the marker VERIFY gate at `:10917-10922` refuses
`head_unpublished` for any marker naming a head that is not live `origin/main`,
so no branch admits a marker built at an unpushed head.

## Paraphrase check

Accurate, with one strengthening: §7 attributes the requirement to the build
refusing "unless `origin/main` already equals the head being marked", which is
right, but does not note that the check is **outside** the phase branches — so
the S-0 candidate build needed the forged ref for exactly this reason, which is
the concrete demonstration that the written order cannot run unforged.

---

# NR-2 — Push topology at the measurement checkout

**Class: RULING.**

## (a) Question

To reach four-way equality in the repository that owns the pack roots, is the
ruled shape pull-into-a-development-worktree → push → fetch-back at the
measurement checkout, or does `_v4` push directly from the measurement checkout?

## (b) Primary evidence

### The predicate

`joulewise/arm_readiness.py:4898-4920`, verbatim and complete:

```python
def reviewed_main(pack_root: Path | str) -> dict[str, Any]:
    root = Path(pack_root)
    repository = _repo_for_pack(root)
    head = _git_text(repository, "rev-parse", "HEAD") or "unavailable"
    tree = _git_text(repository, "rev-parse", "HEAD^{tree}") or "unavailable"
    local_main = _git_text(repository, "rev-parse", "refs/heads/main") or "unavailable"
    origin_main = _git_text(repository, "rev-parse", "refs/remotes/origin/main") or "unavailable"
    status_raw = _git_text(
        repository,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    clean = status_raw == ""
    exact = clean and head == local_main == origin_main and head != "unavailable"
    return {
        "head_commit": head,
        "head_tree_oid": tree,
        "local_main_commit": local_main,
        "origin_main_commit": origin_main,
        "clean": clean,
        "exact_match": exact,
    }
```

Two mechanical points a seat needs:

1. `refs/remotes/origin/main` is a **local remote-tracking ref**. It moves only
   when *that* repository runs `fetch`, `pull`, or `push`. A push performed
   elsewhere does not update it.
2. The repository consulted is `_repo_for_pack(root)`
   (`joulewise/arm_readiness.py:3903-3905`) — derived from the **pack root**, so
   for the arm and evidence paths it is the measurement checkout by
   construction. The marker *verify* path instead consults the `--repository`
   argument (`arm_readiness.py:10908`, `live = reviewed_main(repository)`), while
   the marker *build* consults `roots[0]` (`:10664`). A seat choosing a topology
   should note that build and verify can, in principle, be pointed at different
   repositories, and that only the pack-root-derived form is forced.

### Where the predicate gates

`joulewise/arm_readiness_evidence_t0.py:1921-1927`, verbatim:

```python
    reviewed = _readiness.reviewed_main(root)
    if not reviewed["clean"] or not reviewed["exact_match"]:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_reviewed_tree_mismatch",
            "reviewed checkout is dirty or differs from local/origin main",
        )
```

and the scheduler-side code for the same predicate is
`readiness_reviewed_main_mismatch` (`tests/test_scheduler_gates.py:51`, `:545`,
`:616` exercise it).

### The `_v3` precedent

`docs/process/ed-s5-mint-decision-2026-08-19.md:66-69`, verbatim:

```
Landing is a pull FROM the measurement checkout (never a push from it);
Claude performs it plus the full receipt verification (path-binding,
PASS, `freeze-0003`, predecessor triple vs the `_v2` receipts, digests
for the confirmation table).
```

The `_v3` mints ran at a **branch**, not `main`
(`docs/process/ed-s5-mint-decision-2026-08-19.md:51-53`):

```
At `/Users/edr/JouleWise-measurement-20260818`, branch
`impl/r2-s0-mint-resolver` — first `git pull --ff-only origin
impl/r2-s0-mint-resolver` to the current head `246167f`
```

so `_v3` never had to satisfy four-way equality on `main` at the measurement
checkout at all.

### The S-0 rehearsal did not exercise it

`s0-runsheet-r4.md:2148-2149` (forged ref, quoted under NR-3) and
`s0-runsheet-r4.md:2609-2610`:

```zsh
test "$(git -C "$CLONE" rev-parse refs/remotes/origin/main)" = "$FORGED_ORIGIN_MAIN_OID" \
  || die 'the forged origin/main OID moved since the marker was verified'
```

## (c) Answer space

**A. Pull-into-dev → push → fetch-back.**
Executes: (1) a development worktree fetches from the measurement checkout;
(2) the development worktree pushes to `origin`; (3) the measurement checkout
runs `git fetch origin` (or `git pull --ff-only`) so its own
`refs/remotes/origin/main` advances to the pushed commit.
Without step 3, `origin_main` at the measurement checkout is stale, `exact` is
`False`, and evidence authoring refuses
`evidence_author_t0_reviewed_tree_mismatch`
(`arm_readiness_evidence_t0.py:1922-1927`) while marker build refuses
`head_mismatch` (`arm_readiness.py:10667`).
Preserves the `_v3` written rule ("never a push from it") verbatim.
Adds one network operation at the measurement checkout inside the transaction —
a fetch, not a push.

**B. Push directly from the measurement checkout.**
Executes: one `git push`; `origin/main` at that checkout advances as a side
effect of the push, so four-way equality holds immediately with no extra fetch.
Contradicts `ed-s5-mint-decision-2026-08-19.md:66` as written, so that sentence
needs amendment or an explicit `_v4` carve-out.

**C. Some third topology** (e.g. a bare intermediate, or push from dev plus a
`git update-ref` at the measurement checkout).
Any variant is admissible to the code exactly insofar as it leaves the
measurement checkout with `HEAD == refs/heads/main == refs/remotes/origin/main`
and a clean tree; the code inspects refs, not provenance.

**Constant across A–C:** whichever is chosen must also state whether the network
operation is permissible during the freeze span and whether it is one of Ed's
prompted commands (NR-10).

## Paraphrase check

Two notes.

1. §7 renders the `_v3` doctrine as «land by `git pull --ff-only
   file://<measurement checkout>` from a development worktree». The `file://`
   URL form appears in **no** source read for this packet; the actual sentence
   at `ed-s5-mint-decision-2026-08-19.md:66` is "Landing is a pull FROM the
   measurement checkout (never a push from it)" with no command form given. The
   mechanism is faithfully described; the literal command is the runbook's own
   construction.
2. §7 says the predicate applies "in the repository that owns the pack roots".
   True for the evidence and arm paths and for the marker *build* (`roots[0]`),
   but the marker *verify* path consults `--repository` instead
   (`arm_readiness.py:10908`).

---

# NR-9 — Step-6 delegation, contract prose, and cadence

**Class: mixed.**
Part 1 — **ALREADY-ANSWERED-BY D-150b** (`docs/decision_log.md:176`).
Part 2 — **OPERATOR-FIX**: a documented prose edit, target lines identified below.
Part 3 — **RULING** (Ed's, recorded as pending).

## (a) Question

Is the delegated step-6 exact-byte confirmation live for this transaction, does
the ONE-home contract's prose get amended before execution, and what is the
notification cadence?

## (b) Primary evidence

### The delegation

`docs/decision_log.md:176` (D-150b), verbatim:

```
| D-150b | ED RULING 2026-08-23 (packet item 10 + the exact-byte class,
discharged by DELEGATION): "Approve them for me if they match … def want the
campaign moving fast" + "we don't really have to worry about adversarial
situations … don't require me to be somewhere … to compare strings to make sure
they're legit." RULED: the STEP-6 EXACT-BYTE CONFIRMATION and the TERMINAL
REVIEW are DELEGATED to the magistrate, executed as mechanical comparisons with
INDEPENDENCE preserved (every digest independently recomputed from the artifacts
— never accepted from the producing session's report — before the a==b
evaluation; refusal on any mismatch, with Ed pinged on mismatch); the
confirmation table keeps authority ED with the statement field recording this
standing delegation and the recomputation evidence; Ed is NOTIFIED after each
execution rather than blocked on. Grounds: D-139 A1 rules the in-process
adversary out of the threat model, so step-6's protective value is drift/bug
catching, which independence (not humanity) supplies; this supersedes the
Ed-reserved reading of D-139 A3's exact-byte clause for comparisons that are
purely mechanical — judgment-bearing publication decisions remain Ed's.
Remaining Ed-hands items: the pre-campaign reboot, window-night
non-interference, and S-0 permission prompts (or the optional settings rule). |
adopted (Ed) |
```

Note the two operative sub-clauses a seat must carry into any prose edit:
authority in the table **stays** `ED`, and the `statement` field records the
standing delegation plus the recomputation evidence.

### The contract has not caught up

`docs/contracts/d117_step6_confirmation_table.md:37-41`, verbatim:

```
The table contains no self-digest and no timestamp. Event time belongs in the
immutable transaction transcript. Before Ed is asked, the producer renders
the final bytes including the literal proposed `YES`, computes `hC`, and
presents both. Ed's yes names `hC`; publication promotes the same bytes
without mutation.
```

The schema at `:74-80` fixes the fields D-150b speaks to:

```json
{
  "confirmation": {
    "authority": "ED",
    "decision": "YES",
    "statement": "I confirm these exact D-117 v4 step-6 bytes."
  },
```

The file's ONE-home status is asserted at `:1-6`. A D-153 A5 prose repair
**has** already landed in this file at `:52-60` (the `hC` custody sentence), so
the file has been amended once since the transaction rulings began; the
D-150b delegation has not been recorded in it.

### The cadence

`docs/decision_log.md:177` (D-150a), verbatim excerpt:

```
Item 10 (step-6 timing: immediate ping vs batched) explained to Ed in plain
words; his preference pending.
```

### The S-0 record is consistent with the delegation

`S0-COMPLETION-RECORD.md:30-33` (quoted in full under NR-11) lists what remains
for the real transaction and names permission prompts and the reboot — not a
step-6 confirmation by Ed. Estate 10 nevertheless recorded a real Ed YES:
`S0-COMPLETION-RECORD.md:7-9`:

```
build with the S0-O2 deferral disclosed and candidate verify PASS; Ed's
step-6 YES over hC adbd116d7dcaa3dd5b0d6f1e5c9127282232b29ea74b03b9c6b8077ec9da36bc
(recorded in 085-*, table authenticated);
```

## (c) Answer space

### Part 1 — is the delegation live?

**A. Live as ruled.** Nothing executes differently in code: `hC` is supplied to
each consumer through its explicit `--expected-confirmation-digest` input
(`docs/contracts/d117_step6_confirmation_table.md:144-165`, conditions 1–6),
which is indifferent to who typed the YES. What changes is who performs the
byte comparison and what the `statement` field says.

**B. Not live for this transaction / Ed confirms in person.** Executes: the
operator blocks at the step-6 moment until Ed is at the machine. Under NR-3
branch A that moment sits after publication, i.e. late at night in the same
session.

### Part 2 — the contract prose

**A. Amend before execution.** Edit target:
`docs/contracts/d117_step6_confirmation_table.md:37-41` (the "Before Ed is
asked… Ed's yes names `hC`" sentences), plus whatever `statement` literal the
producer will emit at `:79`. D-150b's two constraints bind the edit: authority
stays `ED`; `statement` records the delegation and the recomputation evidence.
Mechanical consequence of *not* editing: an operator reading the declared ONE
home at the bench waits for Ed, since nothing in the file mentions D-150b.
This is a repository commit — under the freeze span it must land **before** the
attestation commit (see NR-13).

**B. Leave the prose; carry the delegation only in the decision log.**
Consequence: the ONE-home claim at `:1-6` and the file's own text disagree with
D-150b, and the operator's authority at the bench is a lookup in
`decision_log.md`.

### Part 3 — cadence

The two named options in D-150a item 10 are **immediate ping** per execution and
**batched** notification. Mechanically identical from the code's side (nothing
consumes the notification); the difference is Ed's interruption profile during
the transaction and the window nights. Recorded as pending Ed's preference.

## Paraphrase check

Accurate. Two additions of assembly: (i) D-150b requires the confirmation
table's `authority` to remain `ED` and the `statement` field to carry the
delegation and the recomputation evidence — a constraint on any prose edit that
§7 does not state; (ii) the contract file has already taken one amendment
(D-153 A5, visible at `:52-60`), so the "has not caught up" gap is specific to
D-150b rather than general staleness.

---

# NR-1 — The declared `_v4` measurement checkout, and the venv

**Class: split.**
"Which checkout" — **RULING**.
"How the venv is brought into lock" — **OPERATOR-FIX**; the facts are
established below and they differ materially from the runbook's account.

## (a) Question

Which absolute path is the `_v4` declared measurement checkout, and what is
done about the state of its Python environment relative to
`env/mac-measurement-lock.txt`?

## (b) Primary evidence

### The declared default

`docs/phase_2/window_runbook.md:26-34`, verbatim:

```
## 1. Rules that do not bend

The measurement checkout is named by `MEASUREMENT_REPO`. For the current
three-pack freeze its declared default is
`/Users/edr/JouleWise-measurement-20260813`; future freezes use the same
`/Users/edr/JouleWise-measurement-YYYYMMDD` convention and record the chosen
absolute path in `window.env`. Every repository-relative launch path and each
window runs root resolves from that checkout, never from a development
checkout.
```

The same path is the literal in the §4 `window.env` template
(`docs/phase_2/window_runbook.md:190-196`) and in the §5C attestation producer
(`:822`).

### The `_v3` checkout is fenced out of S-0

`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:3-5`, verbatim:

```
This is a bench runsheet, not an execution transcript. The magistrate executes
it in the throwaway clone defined in §1.1 and reads every transcript. It never
uses or reads `/Users/edr/JouleWise-measurement-20260818`.
```

and the §5 acceptance box, `:4379-4384`:

```
- [ ] No command touched or read `/Users/edr/JouleWise-measurement-20260818`; no
  quiet-Mac measurement, freeze outside the clone, dry-run, arm launch, consume
  or publication occurred. §3.2's read-only use of
  `/Users/edr/code/JouleWise/.venv` and read-only hashing of
  `/Users/edr/jw_models` are the two permitted host reads and are recorded in
  `029-*`.
```

Read exactly: that box fences S-0's own execution. It is not a statement about
the real transaction's checkout choice.

### Verified state of both directories (read-only, 2026-08-25)

| | `-20260813` | `-20260818` |
|---|---|---|
| branch | `main` | `impl/r2-s0-mint-resolver` |
| head | `49dcc49` "FREEZE 6/6: D-134 freeze receipt — GAMMA PASS…" | `94dc3b34` "D-147 S5: freeze-0003 minted for d117_contrast_qwen25_1p5b_vs_7b_v3…" |
| `git status --porcelain=v1 -uall` | empty (clean) | empty (clean) |

Both are clean; neither is at the reviewed head; `-20260818` is not on `main` at
all, so four-way equality (NR-2) is unreachable there without a branch change.

### Verified venv state — the runbook's account is incomplete

`env/mac-measurement-lock.txt` pins, among 37 requirement lines
(`:25-27`, `:41`):

```
mlx==0.31.2
mlx-lm==0.31.3
mlx-metal==0.31.2
transformers==5.12.1
```

`pip freeze --exclude-editable` from each interpreter, diffed against those 37
lines:

| venv | Python | `transformers` | `mlx` / `mlx-metal` | lines differing from lock |
|---|---|---|---|---|
| `/Users/edr/JouleWise-measurement-20260813/.venv` | 3.13.1 | **5.15.0** | **0.32.0** | 22 |
| `/Users/edr/JouleWise-measurement-20260818/.venv` | 3.13.1 | 5.12.1 ✓ | **0.32.1** | 20 |
| `/Users/edr/code/JouleWise/.venv` (dev checkout) | 3.13.1 | 5.12.1 ✓ | 0.31.2 ✓ | **0** (plus `pytest`, `pluggy`, `iniconfig` — test tooling only) |

Both measurement venvs are also missing three packages the lock names
(`charset-normalizer`, `requests`, `urllib3`) and carry newer
`annotated-doc`, `anyio`, `certifi`, `filelock`, `fsspec`, `hf-xet`,
`huggingface_hub`, `numpy`, `packaging`, `regex`, `sentencepiece`, `tqdm`, and
`typer`.

**The one environment that is exactly at lock is the development checkout's
venv** — which is the interpreter the S-0 runsheet pinned for its single
non-stdlib section. `s0-runsheet-r4.md:1114-1121`, verbatim:

```
§3.2 runs under the **pinned existing host measurement venv**,
`$MEASURE_PY = /Users/edr/code/JouleWise/.venv/bin/python`, read-only — the
locked environment of `env/mac-measurement-lock.txt`, verified on 2026-08-24 to
be Python 3.13.1 with `mlx_lm` 0.31.3 and `transformers` 5.12.1.
```

That claim re-verifies today.

### What the drift does and does not refuse

Nothing in the shipped code compares an installed environment against the lock.
`tests/test_env_locks.py:41-77` checks only that the lockfiles exist, that every
requirement line is pinned, and that the lock's `mlx` / `mlx-lm` pins equal the
canonical bundle's `prepare_metadata` — a check on **files**, not on a venv.

The runsheet's own U11 guards compare **weight bytes only**, not runtime
versions — `s0-runsheet-r4.md:1678-1700`, verbatim (excerpt):

```python
# Weight-digest post-condition: the _v4 projections must have hashed the same
# weight bytes the committed _v3 projection receipts recorded.
...
    for path, digest in new.items():
        assert digest == old[path], (path, digest, old[path])
```

But the runtime version **is** recorded into every projection receipt —
`joulewise/identity_pins.py:291-318`, verbatim (excerpt):

```python
    runtime_version = (
        prepare.get("version")
        or prepare.get("mlx_version")
        or prepare.get("mlx_lm_version")
```

```python
        "runtime_version": {
            ...
            "version": runtime_version,
```

and the paper's figure metadata hardcodes the lock's value —
`scripts/make_figures.py:552`, verbatim:

```python
            "runtime_version": "MLX 0.31.2 / mlx-lm 0.31.3 (from adapter prepare metadata)",
```

So a U11 projection run under `mlx` 0.32.x refuses nothing, hashes identical
weight bytes, passes both runsheet guards — and stamps `0.32.x` into the `_v4`
projection receipts while the figure caption says `0.31.2`.

### The lock-restoring operation is a `pip` operation

`s0-runsheet-r4.md:1102-1104`, verbatim:

```
**No `pip install` anywhere.** Not into the estate venv, not into the host, not
into any environment.
```

That prohibition scopes S-0. Whatever brings a measurement venv to lock is a
`pip install` in a measurement environment, which no source read here authorizes
an agent to perform.

## (c) Answer space

### Which checkout

**A. `/Users/edr/JouleWise-measurement-20260813`.**
Matches the declared default at `window_runbook.md:28-30`, the `window.env`
template literal at `:190`, and the §5C producer's hardcoded `cd` at `:822` — no
document edits needed.
Requires: fast-forward `main` from `49dcc49` to the reviewed head, then the NR-2
topology; venv brought to lock (22 lines differ, including `transformers` and
`mlx`).

**B. `/Users/edr/JouleWise-measurement-20260818`.**
Requires: a branch change off `impl/r2-s0-mint-resolver` onto `main` before
four-way equality is reachable; venv brought to lock (20 lines differ, `mlx`
among them; `transformers` already matches).
Edits: `window_runbook.md:28-30`, `:190-196`, `:822`.
Also collides with the S-0 fence text at `s0-runsheet-r4.md:5` and `:4379`,
which would then read as history rather than a standing rule.

**C. A fresh `/Users/edr/JouleWise-measurement-2026MMDD`.**
Executes: clone at the reviewed head (four-way equality reachable by
construction), build a venv from `env/mac-measurement-lock.txt` (`pip install -c
env/mac-measurement-lock.txt -e ".[mac]"`, the form the lock header names at
`:6-7`), record the path in `window.env`.
Edits: `window_runbook.md:28-30`, `:190-196`, `:822`; every operator literal
naming a dated path.
Costs: a full model-weight-visible venv build and disk for a third checkout.
Leaves both existing checkouts untouched as historical record.

### The venv, under any of A–C

**OPERATOR-FIX, not a ruling.** The established facts:

1. Neither measurement venv is at lock; the drift is 20–22 lines, not one
   package.
2. The dev checkout's venv **is** at lock and is the environment the S-0
   runsheet pinned and re-verified on 2026-08-24.
3. No code refuses on drift. The consequence is provenance: the `_v4`
   projection receipts would record a runtime version that the lock, the
   canonical bundle metadata, and `scripts/make_figures.py:552` all contradict.
4. The restoring action is a `pip` operation in a measurement environment —
   Ed's hands, per the same reasoning that makes the mint commands Ed's
   (NR-10).

## Paraphrase check

**The runbook's NR-1 misstates the scope of the drift.** §7 says
`-20260813`'s venv "is out of lock (`transformers 5.15.0` against
`env/mac-measurement-lock.txt`'s `5.12.1`)". `transformers` is one of
**22** lines that differ there, and `-20260818` — which §7 does not flag as
drifted — differs on **20** lines including `mlx` 0.32.1 against the pinned
0.31.2, even though its `transformers` matches. A seat reading §7 alone could
conclude that `-20260818` is the in-lock option. It is not; nothing under
`/Users/edr/JouleWise-measurement-*` is.

Everything else in §7's NR-1 verifies: the declared default, the
`YYYYMMDD` convention, the `window.env` recording, the §5 fence, both
directories existing, and neither being at the reviewed head.

---

# NR-12 — Where the attestation commit sits

**Class: RULING.**

## (a) Question

Does the terminal-review attestation commit land at the common derivation head
(r4-3) or after the mint (`window_runbook.md` §5C), and is it therefore the
published head?

## (b) Primary evidence

### Placement A — r4-3

`v4-plan-ruling-r4draft.md:50-53`, verbatim:

```
pre-evidence tree → Ed's tree-preserving terminal-review attestation
(THE common derivation head) → evidence ×3 at that head, one commit
→ freeze-0004 ×3 → dry-run ceremony
```

### Placement B — the window runbook's producer

`docs/phase_2/window_runbook.md:815-819`, verbatim:

```
**Lead-owned terminal-review attestation — required producer step.** After
all repair/freeze review is complete and before the dry run or T-0, the lead
operates at the reviewed tree, computes the committed pack digest, and creates
one empty attestation commit. This is not delegated and is not an Ed hardware
step:
```

"After all repair/freeze review is complete" places it after the freeze; r4-3
places it before evidence authoring, which is itself before the freeze. These
are different commits.

### It is a real commit

`window_runbook.md:832-836` (the `git commit --allow-empty --cleanup=verbatim`
block, quoted in full under NR-11) and `:839-843`:

```
The lead then lands that exact commit as reviewed `main`; the measurement
checkout, local `main`, and `origin/main` must all name it. The tree OID is
unchanged by the empty commit.
```

### The trailers are tree-bound and do not survive a tree move

`window_runbook.md:843-846`, verbatim:

```
A later tree or pack change requires a new reviewed attestation
commit; trailers from an ancestor do not transfer.
```

Mechanically this is `context.head_tree_oid`
(`arm_readiness_evidence_t0.py:936`): the expected `Tree-Oid` trailer is the
tree of the head being armed, so an attestation whose trailers name an earlier
tree fails the `:939` comparison.

### The two heads D-153 names

`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:64-66`
and `:83-86`, verbatim:

```
A1 condition 3: "window close" bound to the r4-3 commit-freeze close;
   fixation = first commit after it, containing exactly the hS literal
   + its loud-fail guard; no mint-falsifiable assertion may live there.
```

```
A6 condition 8: the changed-set window opens at the evidence-derivation
   head and closes at the LAST CONSUMING ARM; "window close" is
   reserved for the commit-freeze close; the mint-side head is
   PINSET_MINT_HEAD. Conditions 2, 6, 7, 9 unamended.
```

### Sequencing conflict between the two placements

Under r4-3, the attestation is made **before** the mint, and the mint is a real
commit (`PINSET_MINT_HEAD`). By `window_runbook.md:845`, trailers bound to the
pre-mint tree do not transfer to the post-mint tree — the mint changes
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json`, so the tree
OID moves. Whether the attestation is therefore dead at arm time is exactly what
this item asks a seat to settle.

### The changed-set arithmetic is unaffected either way

An empty commit adds no paths, and the changed-set gate computes the set of
repository paths that changed between derivation commit and reviewed HEAD
(`docs/contracts/d117_step6_confirmation_table.md:145-148`):

```
The R1 changed-set gate (`validate_r1_evidence_lifecycle` in
`joulewise/arm_readiness.py`) computes the set of repository paths that changed
between an evidence receipt's derivation commit and the reviewed HEAD, then
subtracts the registry's `irrelevant_path_allowlist`.
```

## (c) Answer space

**A. At the common derivation head (r4-3 as written).**
Executes: attestation → evidence ×3 → freeze ×3 → mint. Trailers name the
pre-evidence tree.
Refuses at T-0: the tree has moved (evidence commit, freeze commit, mint
commit), so `context.head_tree_oid` at arm time is not the trailer's value, and
`:939` refuses `evidence_author_t0_terminal_review_record_missing`, unless a
further attestation is made after the last tree move — which is placement B.

**B. After the mint (`window_runbook.md` §5C as written).**
Executes: the attestation is the last commit before publication, so its trailers
name the head that gets published.
Consequences a seat must then name explicitly in every Phase D step:
- the published head is the attestation commit, **not** `PINSET_MINT_HEAD`;
- the marker is built at the attestation commit (NR-4 chooses its phase);
- `PINSET_MINT_HEAD` remains the allowlist-contract closure head (D-153 A6), so
  closure head ≠ published head and every step naming "the head" must say which;
- the 112 closure arithmetic is unchanged (empty commit, no paths).

**C. Both** — an attestation at the derivation head for the r4-3 record, and a
second at the post-mint head for the trailers that actually gate.
Consequence: two commits inside a span r4-3 wants frozen; the second is the one
`_derive_terminal_review` reads.

**Who makes it, under every branch:** r4-3 says "**Ed's** tree-preserving
terminal-review attestation" (`:50`); `window_runbook.md:818-819` says it "is
not delegated and is not an Ed hardware step"; D-150b
(`decision_log.md:176`) delegates the terminal review to the magistrate. All
three texts speak to the same act. A seat ruling placement should also rule the
owner, or note which text it is leaving standing.

## Paraphrase check

Accurate on both placements, on the commit's realness, on the head consequences,
and on the 112 arithmetic. One addition of assembly: the three sources disagree
about **who** performs the attestation (Ed / the lead, explicitly not delegated /
the magistrate under D-150b), which §7 does not raise.

---

# NR-4 — The marker phase for the real boundary build

**Class: RULING.**

## (a) Question

Which `--phase` value do the real boundary marker build and verify use, and does
the real transaction need an S-0-style mechanical candidate manifest at all?

## (b) Primary evidence

### The phases

`scripts/build_family_marker.py:24-33`, verbatim:

```python
    # Split S-5: the tool-authentication lane is chosen here and nowhere else.
    # The default is the strict production rule (executing bytes must equal the
    # blob committed at --head); candidate mode is an explicit opt-in that
    # compares against the reviewed $INPUT manifest instead.
    parser.add_argument(
        "--phase",
        choices=("candidate", "publication", "pre-arm", "t0"),
        default="publication",
    )
    parser.add_argument("--candidate-manifest", type=Path)
```

`scripts/verify_family_marker.py:20-33` offers the same four choices with
`default="candidate"`.

### What phase actually selects

`joulewise/arm_readiness.py:10473-10518` (docstring `:10473-10485`, lane branch `:10497-10517`), verbatim:

```python
    """Authenticate the executing custody tool under the lane's own rule.

    PRODUCTION (``phase`` is anything but ``"candidate"``): the executing bytes
    must equal the blob committed at ``head``.  This is the ruled rule and the
    only one that can gate a publication.

    CANDIDATE (``phase == "candidate"``): the tools deliberately do not exist at
    the pinned HEAD of the S-0 clone, so committed-blob equality would refuse
    the clone proof.  The executing bytes are instead compared against the
    digest recorded in the reviewed ``$INPUT`` manifest (marker ruling, split
    S-5).  The lane is chosen by this argument alone -- never by the presence of
    a file on disk, which would let a dropped sidecar silently downgrade a
    production consult.
    """
```

```python
    if phase == "candidate":
        manifest_path = (
            Path(candidate_manifest)
            if candidate_manifest is not None
            else executing_path.resolve(strict=True).with_name(
                S0_CANDIDATE_MANIFEST_NAME
            )
        )
        if _candidate_manifest_tool_digest(manifest_path, relative_path) != digest:
            raise FamilyPublicationError(
                "tool_mismatch",
                f"{relative_path} differs from the digest the reviewed candidate "
                "manifest records for it",
            )
    else:
        code, committed, _stderr = _histsem_git(repository, "show", f"{head}:{relative_path}")
        if code != 0 or committed != raw:
            raise FamilyPublicationError(
                "tool_mismatch",
                f"{relative_path} is not the blob committed at the reviewed head",
            )
```

The other three things `phase` selects, in `verify_family_publication_marker`:

- confirmation-table authentication, `arm_readiness.py:10940-10943`:
  ```python
      if phase != "candidate":
          table, table_raw = _authenticate_confirmation_table(
              confirmation_path, expected_confirmation_digest
          )
  ```
- the C→S conditional deferral, `:10949`:
  ```python
      replay_deferral = R1ConditionalDeferral() if phase == "candidate" else None
  ```
- the receipt's own admissibility fields, `:11094-11098`:
  ```python
      "lane": "candidate" if phase == "candidate" else "published",
      "gate_admissible": phase != "candidate",
  ```
  ```python
      "publication_authorized": phase != "candidate",
  ```

### The S-5 split, verbatim

`docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md:94-99`:

```
- **S-5 Tool self-hash in S-0 (Opus's defect, cured as Sol's
  candidate mode):** committed-blob equality is the PRODUCTION rule;
  S-0 candidate mode verifies against the reviewed `$INPUT` manifest
  sidecars instead (the tools do not exist at the pinned HEAD — the
  literal rule would refuse the clone proof). The dual proof
  (candidate PASS + production-gate refusal) is required in S-0.
```

### The tools exist as committed blobs in the real lane

`scripts/build_family_marker.py` and `scripts/verify_family_marker.py` are
tracked, each with a committed `.sha256` sidecar (`scripts/build_family_marker.py.sha256`,
`scripts/verify_family_marker.py.sha256`), so `git show <head>:scripts/…` at the
reviewed head returns bytes — the production lane's precondition holds.

## (c) Answer space

**A. Build `--phase publication`, verify `--phase publication`.**
Executes: committed-blob tool authentication at the reviewed head; live four-way
consult; confirmation table required at verify (`:10940-10943`) — so `C` and
`hC` must both exist by then; receipt carries `lane: "published"`,
`gate_admissible: true`.
Needs: the push already done (NR-3), and the step-6 confirmation pair already in
hand at verify time.
Consequence for the candidate manifest: none is passed; `--candidate-manifest`
is unused in this lane. The real transaction needs no §1.3-style manifest for
the marker.

**B. Build `--phase candidate` first (as S-0 did), then a publication verify.**
Executes: the build authenticates tools against a manifest instead of the
committed blobs, which in the real lane is strictly weaker than what is
available.
Needs: a real `$INPUT` manifest of tool digests to exist — i.e. the §1.3
mechanical candidate manifest has to be constructed for the real transaction.
Consequence: the candidate receipt is `gate_admissible: false` and
`publication_authorized: false` by construction (`:11095`, `:11098`); it cannot
gate anything, so a publication-lane verify is required regardless.

**C. `pre-arm` / `t0` for the boundary build.**
Mechanically identical to `publication` for tool authentication, table
authentication, deferral, and admissibility — the code branches only on
`== "candidate"` versus everything else. The value is recorded in the marker's
`phase` field and is therefore a labelling choice about which consult this is,
not a behavioural one.

**Constant across A–C:** the build's four-way equality check
(`arm_readiness.py:10664-10667`) is **outside** every phase branch, so no phase
lets a marker be built at an unpushed head.

## Paraphrase check

**One misstatement.** §7 says "every non-candidate phase drives the live
four-way consult". The live four-way consult runs in **every** phase, candidate
included: `live = reviewed_main(repository)` at `arm_readiness.py:10908` and the
`head_unpublished` / `head_mismatch` checks at `:10917-10924` sit above all
phase branching. What `phase` actually selects is the four things enumerated
above (tool lane, table authentication, C→S deferral, admissibility fields).
S-0's candidate run satisfied the live consult by forging `origin/main`
(`s0-runsheet-r4.md:2148-2149`), not by phase-exemption.

The rest of §7's NR-4 verifies: the S-5 "production rule" language, the
four-choice CLI, and the fact that the tools exist as committed blobs in the
real lane.

---

# NR-13 — `WINDOW-STATUS-FREEZE-GUARD-01` as a gate on the freeze span

**Class: mixed.**
The cure is **ALREADY-ANSWERED-BY D-153 W4** (ordered, kernel row exists).
Its **scheduling** relative to Phase D is a **RULING**.

## (a) Question

Must `WINDOW-STATUS-FREEZE-GUARD-01` land before the freeze span opens, or is an
explicit operational fence with a named owner sufficient?

## (b) Primary evidence

### The commit freeze

`v4-plan-ruling-r4draft.md:57-60`, verbatim:

```
checkout pinned. Docs-only commits to main DISARM T-0
(exact_match=false — executed, sitting §6.2): the runsheet carries a
commit-freeze on the measurement checkout's main from attestation
through window close.
```

### The work order

`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:101-104`,
verbatim:

```
W4 scripts/window_status.sh:92-104 commits and pushes WINDOW_STATUS.md
   — inside the freeze span this breaks the commit-freeze AND adds
   changed-set residue (terra's verified bonus hazard). Guard it:
   refuse (or write-without-commit) during the freeze span. Kernel row.
```

### The script

`scripts/window_status.sh:94-105`, verbatim:

```sh
cd "$REPO"
git add WINDOW_STATUS.md
if git diff --cached --quiet; then
  echo "No status change; nothing to publish."
  exit 0
fi
git commit -q -m "status: $STATE — $HEADLINE"
git push -q origin HEAD 2>/dev/null || {
  echo "WARNING: push failed (offline?). Status committed locally only." >&2
  exit 0
}
echo "Published: $STATE — $HEADLINE"
```

and `scripts/window_status.sh:32`, verbatim:

```sh
REPO=/Users/edr/code/JouleWise
```

The script's own push discipline is documented at `:12-19` and is about
measurement contamination, not about the commit freeze:

```
#   PUSH DISCIPLINE -- THIS IS A SAFETY RULE, NOT A STYLE PREFERENCE
#     git push is network and CPU activity. It must NEVER run while a measurement
#     is in flight. Call this ONLY:
```

Its only existing refusal is a live-campaign process check at `:40-45`.

### The kernel row

`docs/process/state_kernel.json`, task `WINDOW-STATUS-FREEZE-GUARD-01`, verbatim
fields:

```json
 "id": "WINDOW-STATUS-FREEZE-GUARD-01",
 "lane": "agent",
 "priority": "p1_phase_gate",
 "rank": 91,
 "status": "queued",
 "status_note": "D-153 work order W4, pending kernel registration since the 2026-08-24 ruling (W1/W2 landed via PR #181 and the errata; W3 had no target). Hazard is verified by inspection, not yet executed.",
```

```json
  "summary": "The status publisher can no longer break the commit-freeze or add changed-set residue.",
  "evidence": [
   "scripts/window_status.sh refuses (or writes without committing) while the commit-freeze span is open, proven by a regression that exercises both the in-span and out-of-span branches",
   "Out-of-span publishing behaviour is unchanged (WINDOW_STATUS.md still written, committed and pushed)"
  ],
```

`TASK_QUEUE.md:647` carries the same row as `A91` with status `READY [AGENT]`.

## (c) Answer space

**A. Land the guard before Phase D.**
Executes: a code change plus a regression covering the in-span and out-of-span
branches, per the kernel acceptance evidence quoted above.
Timing: it is itself a commit to `main`, so it must land before the attestation
commit opens the freeze span — i.e. before the point r4-3 fixes at `:58-60`.

**B. Operational fence with a named owner** (the script is simply not run during
the span).
Executes: nothing; the hazard remains reachable by any operator or automation
that calls `scripts/window_status.sh`.
Requires: the owner named, and the fence recorded somewhere an operator reads at
the bench.
Interaction: D-150a
(`decision_log.md:177`) committed to "push notifications at every state change"
during the transaction — window-status publishing is exactly the visibility
mechanism the no-reboot/push-freeze bargain rests on, so a blanket fence removes
a committed channel unless a non-committing substitute is named.

**C. Neither, before the span opens.**
Consequence chain if the script runs in-span: it commits and pushes
`WINDOW_STATUS.md` in `/Users/edr/code/JouleWise` (the path hardcoded at `:32`),
`origin/main` advances, the measurement checkout's `refs/remotes/origin/main`
diverges from its `HEAD` on the next fetch, `exact` goes `False`
(`arm_readiness.py:4912`), and every subsequent T-0 refuses
`evidence_author_t0_reviewed_tree_mismatch` /
`readiness_reviewed_main_mismatch`. If the measurement checkout does **not**
fetch, its four-way equality survives locally, but `WINDOW_STATUS.md` is now a
path outside the 112 in the published history.

## Paraphrase check

Accurate. Two additions of assembly, both narrowing the mechanism:

1. `REPO` is **hardcoded** to `/Users/edr/code/JouleWise` at `:32`, so the
   commit lands in the development checkout, not the measurement checkout. The
   kill mechanism is therefore primarily the **push** moving `origin/main` out
   from under the measurement checkout's four-way equality — not residue
   appearing in the measurement working tree.
2. Actual line numbers of the commit/push block are `94-105`; both D-153 W4 and
   the kernel row cite `92-104`. The block is the one quoted above either way.
3. Kernel status is `queued`, as §7 says; `TASK_QUEUE.md:647` shows the same row
   as `READY [AGENT]`. The two are not identical strings.

---

# NR-6 — Real arm, or the dry-run ceremony, in Phase G

**Class: RULING**, plus an unresolved **missing-procedure** fact.

## (a) Question

Does Phase G execute runsheet §3.9's arm-and-verify of all three packs, or
r4-3's B-4 dry-run ceremony with no real arm — and if the latter, where is the
`file-09-probe P1/P2/P3` procedure written?

## (b) Primary evidence

### The runsheet arms

`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2282-2290`, verbatim:

```
### 3.9 Arm and verify all three at the allowlist-contract closure head

The exact 112 allowlist contract was closed at `$PINSET_MINT_HEAD` in §3.7, and
this section runs at that same head: under D-153 the fixation commit is made
last, in §4.10, so it is not present here and cannot enlarge anything. This clone proof
may arm only after the exact marker and Ed-confirmed table have been placed in
`$CUSTODY/windows/family_publication`. Any arm or verify result here is
non-claim-bearing and forged-ref-conditional; publication acceptance is the
separate published-green step in §3.10.
```

### r4-3 forbids a real arm at the same point

`v4-plan-ruling-r4draft.md:53-55`, verbatim:

```
→ freeze-0004 ×3 → dry-run ceremony (B-4 form: dry-run +
file-09-probe P1/P2/P3; NO real arm) + marker candidate + Ed's
exact-byte step-6 → atomic publication
```

### B-4, the definition it points to

`docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r3.md:73-83`,
verbatim:

```
## B-4 (ceremony definition — supersedes A-5.4(b); G5 accepted)

"Clean-arm dry run" is REDEFINED as: one
`generate_arm_readiness.py dry-run` (DRY_RUN_REHEARSAL evidence) plus
the file-09 probe P1/P2/P3 OK. No real arm is issued for ceremony —
the first real arm of the `_v4` family is the shakedown window's own,
under its D-149 GO receipt. RECORDED TRADE (cold final check):
striking the ceremony arm removes the empty-refusals arm receipt as
the V4 reason-code-delta proof vehicle; until the shakedown arm, that
proof rests on dry-run + load-closure + gauntlet regressions, and THE
SHAKEDOWN GO RECEIPT IS NAMED AS THE V4-DELTA PROOF POINT.
```

### D-151 condition 5 assumes the same

`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:62-65`,
verbatim:

```
5. The mint→fixation interval is a REGISTERED RESIDUAL under the
   truth boundary / D-139 A1 with the phase-by-phase controls listed;
   no claim-bearing arm occurs in it (r4-3: dry-run only until
   publication).
```

### But something is named as a real-lane obligation

`s0-runsheet-r4.md:2298-2299`, verbatim:

```
so it is never read as a finding. Live arm-side U11 re-verification is proven by
the real transaction in the measurement environment, not by S-0.
```

The refusal that made S-0's arm-side U11 leg inadmissible is pre-declared at
`s0-runsheet-r4.md:2292-2297`:

```
**Pre-declared expected refusal.** Under the stdlib `$PY`, the
`u11-arm-reverification` leg refuses with
`readiness_identity_artifact_unreadable` (`arm_readiness.py:7655` calls
`_run_identity_arm_reverification`, defined at `:5235`, which resolves the
runtime backend the same way §3.2 does).
```

### `file-09-probe P1/P2/P3` — every occurrence in the repository

An exhaustive search (`file-09`, `file_09`) returns eight hits, all prose:

- `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r3.md:77` — the
  B-4 definition above, "the file-09 probe P1/P2/P3 OK".
- `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md:54` — the
  order line above.
- `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:152` — "file-09
  probe P1/P2/P3 OK + one clean-arm dry run".
- `docs/process_traces/2026-08-20-go-session/readiness-sitting/VERDICT-PACKET.md:117` —
  records V-6 and its consequence: "makes ED-QUAL-L6-1 unsatisfiable as written".
- `docs/process_traces/2026-08-20-go-session/v4plan/opus-design.md:348` — "PLUS
  the file-09 probe requiring **P1, P2, P3 all OK**".
- `docs/process_traces/2026-08-20-go-session/v4plan/opus-design.md:510` — "This
  is the file-09 experiment's mirror image and it has not been run."
- `docs/process/state_kernel.json:4041` — "file-09 probe P1/P2/P3 OK at the _v4
  family + one dry-run ceremony (no real arm)".
- `docs/process_traces/2026-08-20-go-session/v4plan/sol-design.md:260` — the only
  text giving P1/P2/P3 any content, verbatim:

  ```
  - Run file-09 P1/P2/P3 against each `_v4` pack: live registry reference loads, freeze reference authenticates, and arm semantics cross the registry gate.
  ```

No file names the probes' commands, expected outputs, or pass criteria. There is
no `file-09` document, script, or test in the repository.

## (c) Answer space

**A. Real arm ×3 at the closure head (runsheet §3.9 shape).**
Executes: three arms and verifies at `PINSET_MINT_HEAD` with the confirmation
pair supplied.
Collides with: r4-3's "NO real arm" (`:54`) and D-151 condition 5's "no
claim-bearing arm occurs in it" (`MAGISTRATE-RULING-O1.md:64`) — unless the
ceremony arm is ruled non-claim-bearing, which is NR-7's subject.
Supplies: the live arm-side U11 re-verification that `s0-runsheet-r4.md:2299`
names as the real transaction's obligation, and the empty-refusals arm receipt
B-4's recorded trade gave up.

**B. Dry-run ceremony (B-4 form).**
Executes: one `generate_arm_readiness.py dry-run` per pack producing
`DRY_RUN_REHEARSAL` evidence — plus the P1/P2/P3 probe, which **has no written
procedure**. Under this branch the probe needs a home with executable steps
before the session, or the ceremony is under-specified at the bench.
Preserves: r4-3, B-4, and D-151 condition 5 as written.
Leaves: the V4 reason-code delta proven only at the shakedown GO receipt, per
B-4's own recorded trade.

**C. Dry-run ceremony now, with the live arm-side U11 re-verification
explicitly deferred to the shakedown window.**
Requires: naming the shakedown as the place `s0-runsheet-r4.md:2299`'s
obligation is discharged, and accepting that the first live exercise of
`_run_identity_arm_reverification` (`arm_readiness.py:5235`, called at `:7655`)
happens at a claim-bearing T-0.

**Under B or C, the P1/P2/P3 question is separable and must be answered
regardless:** either write the procedure from `sol-design.md:260`'s three
properties (registry reference loads; freeze reference authenticates; arm
semantics cross the registry gate), or strike the probe from the ceremony
definition at `MAGISTRATE-RULING-r3.md:77` and the order line at
`v4-plan-ruling-r4draft.md:54`.

## Paraphrase check

Accurate, including the claim that the procedure "exists in no source read for
this runbook" — an exhaustive repository search confirms it exists in no source
at all. One addition of assembly: `s0-runsheet-r4.md:2298-2299` explicitly
assigns live arm-side U11 re-verification to the real transaction, which is
evidence bearing on the choice and which §7 does not cite here.

---

# NR-5 — Does the real transaction re-run the §4 probe battery?

**Class: ALREADY-ANSWERED-BY** `S0-COMPLETION-RECORD.md:30-33` in substance —
that record enumerates what remains for the real transaction and the probe
battery is not among the items. It is a **record**, not a ruling, so a seat may
still want to state it.

## (a) Question

Is S-0's §4 probe battery the proof of record, or must some probes be
re-executed at the real head — and if so, which, and where do their case clones
live?

## (b) Primary evidence

### What the battery is

`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`, section headings —
ten probe sections plus the fixation step:

```
2779:### 4(a). Ordinary changed path refuses
2821:### 4(b). Unexpected output-directory file refuses
2931:### 4(c). Manifest-only plan mutation — the current pack, and the sibling pack replaying itself
3100:### 4(d). Missing, extra, and unused candidate entries all fail
3148:### 4(e). Per-class tamper probes over every allowlisted path class
3460:### 4(e.1). Digest-conditional successor subtraction — actual C→S edge
3620:### 4(f). `DEPENDENCY_MANIFEST` conjunct — both halves
3772:### 4(g). S-6 dual-validator falsifiers
3871:### 4(h). Histsem and pinset probes
3934:### 4(i). Poison question — direct code-path probe
```

### What the battery proved

`docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md:11-16`, verbatim:

```
§3.10 local green (full suite in the clone), published half DEFERRED by
design (095-*); §4 probe battery ALL GREEN including the six r6 re-derived
probes (every code-derived prediction CONFIRMED by execution — the r6
caveat is discharged) and the post-fixation 118 shape-preserving re-mint
byte-pin probe; §4.10 fixation (078-* equals the mint-time 074-* record);
block-level §5 checks green.
```

### What the record says remains

`S0-COMPLETION-RECORD.md:30-33`, verbatim (also quoted under NR-11):

```
REMAINING FOR THE REAL TRANSACTION (not S-0's scope): Ed's D-150(1) live
permission prompts and D-150a reboot; a quiet machine window; the real
commit-freeze window close; the published-green half (§3.10's deferred
block) at the real published head; post-window fixation ordering per D-153.
```

Five items. The probe battery is not one of them.

### The probes' estate

The battery runs over throwaway case clones inside the S-0 proof estate
(`S0-COMPLETION-RECORD.md:21-23`):

```
Estate custody: scratchpad s0-clone-proof-r4 of session
eac3ed1d-1740-4cf1-9ab3-b4c539575666 (173 transcripts). Ten estates were
cut in total;
```

The runsheet's environment contract forbids running these against the
measurement checkout — `s0-runsheet-r4.md:1123-1126`, verbatim:

```
Reading `/Users/edr/jw_models` (read-only hashing of weights) is permitted; it
is not the forbidden measurement checkout. Never run a dry-run, launch,
measurement, or quiet-Mac command in S-0.
```

## (c) Answer space

**A. S-0's battery is the proof of record; the real lane runs §§1–3.10 plus
post-campaign fixation.**
Consistent with `S0-COMPLETION-RECORD.md:30-33` as written.
Executes: no probe blocks in the real transaction; Phase G is whatever NR-6
rules.
Clock: no additional bench time.

**B. Re-execute some probes at the real head.**
Requires naming: which probes, and where their case clones live. The clones must
be **outside** the frozen measurement checkout — a probe mutates a pack tree to
elicit a refusal, and any such mutation inside the measurement checkout dirties
the tree, which fails `clean` in `reviewed_main` (`arm_readiness.py:4912`) and
refuses every arm until reverted.
Clock: each probe class is a clone-cut plus a governed invocation.

**C. Re-execute the whole battery at the real head.**
Same clone-siting requirement as B, ten sections' worth, inside the freeze span.

**Constant across A–C:** the probes prove *refusal* behaviour, which is a
property of the code at a head. If the real head's code is byte-identical to the
head S-0 proved at, a seat may treat the battery as transferable; if the
pre-derivation candidate or any W1–W5 work order changes the gate code between
S-0's BASE (`f125ae70`, per `S0-COMPLETION-RECORD.md:4`) and the real head, the
transferability argument is not automatic. That comparison is a mechanical diff a
seat can order.

## Paraphrase check

Accurate. §7's "thirty-odd tamper probes" is a count of individual probe cases
inside ten sections `4(a)`–`4(i)` plus `4(e.1)`; the section-level enumeration
above is the exact list.

---

# NR-7 — D-151 condition 5 versus D-153 A4

**Class: RULING** (doctrine coherence; two adopted texts, one interval).

## (a) Question

Which text governs the mint→fixation interval — D-151 condition 5's "no
claim-bearing arm occurs in it", or D-153 A4's re-pricing of the same interval as
mint → post-window fixation — and how is the surviving text restated?

## (b) Primary evidence

### D-151 condition 5

`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:62-65`,
verbatim:

```
5. The mint→fixation interval is a REGISTERED RESIDUAL under the
   truth boundary / D-139 A1 with the phase-by-phase controls listed;
   no claim-bearing arm occurs in it (r4-3: dry-run only until
   publication).
```

`docs/decision_log.md:175` (D-151 index row) renders the same clause as:

```
mint→fixation interval a registered residual (no claim-bearing arm occurs in it)
```

### D-153 A4

`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:73-76`,
verbatim:

```
A4 condition 5: residual re-priced mint -> post-window fixation
   (~<=8 days worst case), with the per-phase controls named and the
   ordinary-commit tail charged to the truth boundary / D-139 A1.
```

`docs/decision_log.md:180` (D-153 index row):

```
(A4) condition 5 residual re-priced mint->post-window fixation (<=~8 days worst
case) with per-phase controls named
```

### The arithmetic that makes them collide

D-153 A1 (`04-MAGISTRATE-SYNTHESIS-PACKET5.md:64-66`) puts fixation **after** the
commit-freeze close, which A1 binds to "after the LAST consuming window"
(`decision_log.md:180`). D-153 A6 (`:83-86`) closes the changed-set window "at
the LAST CONSUMING ARM". So the re-priced interval mint → post-window fixation
contains, by construction, every campaign window's arm — and a *consuming* arm
is claim-bearing.

### How condition 5 was used

The runbook reports that the terra seat read condition 5 literally and used it
as one of two grounds for killing option beta. The synthesis records beta's
disposition at `04-MAGISTRATE-SYNTHESIS-PACKET5.md:57-58`:

```
   analysis is recorded as a REGISTERED LIMITATION: any non-config cure
   mid-campaign forces a new family generation under every option.
```

and in the dissents at `:115-117`:

```
- Luna's beta — overruled per finding 4; retained as the operational
  sequence study.
```

The full terra round record lives in the same trace directory
(`docs/process_traces/2026-08-24-packet5/`); this packet does not reproduce it,
and a seat wanting the exact ground beta was killed on should read the seat file
directly rather than rely on either summary.

## (c) Answer space

**A. D-153 A4 governs; condition 5's "no claim-bearing arm" is superseded.**
Executes: the interval is a registered residual spanning the campaign, priced at
≤ ~8 days worst case, with the per-phase controls named in the synthesis.
Edits: `MAGISTRATE-RULING-O1.md:62-65` and the D-151 index row at
`decision_log.md:175` get an amendment marker; the "dry-run only until
publication" parenthetical is either struck or scoped to the pre-publication
phase only.
Consequence for NR-6: removes condition 5 as a ground against a ceremony arm.

**B. Condition 5 governs literally; A4's re-pricing describes a different
interval.**
Requires: naming the two intervals separately — mint → *publication* (no
claim-bearing arm) versus mint → post-window fixation (the ≤ ~8-day residual) —
and restating both texts so a bench reader cannot conflate them.
Consequence: any real arm before publication is forbidden (bears on NR-6
branch A).

**C. Both stand as written.**
Consequence: an operator at the bench reads condition 5 as forbidding what A4
prices as normal. §7 exists because that is the current state.

**Constant across A–C:** whichever survives must be restated at its ONE home,
because the clause is quoted in two places (`MAGISTRATE-RULING-O1.md:62-65` and
`decision_log.md:175`) and paraphrased in a third (`decision_log.md:180`).

## Paraphrase check

Accurate on both texts and on the collision. One caution of assembly: §7's
account of *why* the terra seat killed beta ("one of the two grounds") is not
reproduced here from the seat's own file; a seat relying on that history should
read `docs/process_traces/2026-08-24-packet5/` directly.

---

# NR-8 — Who declares "the last consuming arm"

**Class: RULING** (a named gap; no source supplies the declaring act).

## (a) Question

What act declares the last consuming arm, who performs it, and where is it
recorded — since the fixation commit hangs off the commit-freeze close that
follows it?

## (b) Primary evidence

### The two amendments that create the dependency

`04-MAGISTRATE-SYNTHESIS-PACKET5.md:83-86` (A6), verbatim:

```
A6 condition 8: the changed-set window opens at the evidence-derivation
   head and closes at the LAST CONSUMING ARM; "window close" is
   reserved for the commit-freeze close; the mint-side head is
   PINSET_MINT_HEAD. Conditions 2, 6, 7, 9 unamended.
```

`04-MAGISTRATE-SYNTHESIS-PACKET5.md:64-66` (A1), verbatim:

```
A1 condition 3: "window close" bound to the r4-3 commit-freeze close;
   fixation = first commit after it, containing exactly the hS literal
   + its loud-fail guard; no mint-falsifiable assertion may live there.
```

`decision_log.md:180` renders A1's parenthetical as:

```
(A1) D-151 condition 3: "window close" = the r4-3 COMMIT-FREEZE CLOSE (after the
LAST consuming window)
```

Note the two texts use different units: A6 says the changed-set window closes at
the last consuming **arm**; the D-153 index row says the commit-freeze closes
after the last consuming **window**. A window contains an arm and a consume.

### Every occurrence of the phrase

An exhaustive search for "last consuming arm" / "LAST CONSUMING ARM" over
`docs/` returns exactly two hits, both quoted above:
`04-MAGISTRATE-SYNTHESIS-PACKET5.md:84` and `decision_log.md:180` (which
paraphrases it). No document names a declaring act, a transcript, a signer, or a
form.

### What is downstream of the undeclared event

- the commit-freeze close (r4-3, `v4-plan-ruling-r4draft.md:58-60`);
- the fixation commit, whose content is fixed by A1 (the `hS` literal + its
  loud-fail guard);
- the end of the freeze span, and therefore the point at which ordinary commits
  to `main` resume;
- the changed-set window's close (A6), and therefore the point after which
  changed-set residue stops mattering.

## (c) Answer space

The answer space here is a *design* space with no candidates on record. The
dimensions a ruling must fix:

**1. The triggering fact.** Candidates visible in the machinery: the last
window's consume completing; the last window's whole-window verdict being
emitted; the campaign's own completion record. Each is a different moment and
each has a different artifact.

**2. The declaring act and its owner.** D-150b (`decision_log.md:176`) delegated
mechanical comparisons to the magistrate while reserving "judgment-bearing
publication decisions" to Ed. Whether "the campaign is over" is mechanical or
judgment-bearing is itself the question.

**3. The record.** Candidates: a transaction-custody transcript (the pattern
every other transaction event follows), a `RUN_STATE` header line (D-150a's
committed visibility channel, `decision_log.md:177`), a decision-log row, or the
fixation commit's own message.

**Mechanical consequence of leaving it unnamed:** the fixation commit has no
defined trigger, so the freeze span has no defined end. Nothing refuses — no
code consults "the last consuming arm" — which is precisely why the gap is
invisible to every gate and can only be closed by a ruling.

## Paraphrase check

Accurate. One addition of assembly: A6 says the changed-set window closes at the
last consuming **arm** while the D-153 index row says the commit freeze closes
after the last consuming **window**; a ruling on the declaring act should fix
which unit it declares, since the two are not the same instant.

---

# NR-10 — Scope of the D-150(1) live-prompt license

**Class: RULING.**

## (a) Question

Does the D-150(1) live-prompt mint license cover the repository-mutating
commands outside the two `_v3` blocked classes, and how many prompts should Ed
expect?

## (b) Primary evidence

### The license as granted

`docs/decision_log.md:178` (D-150), verbatim excerpt:

```
(1) MINT LICENSE GRANTED — operationalized as LIVE PROMPTS AT ED'S HANDS, not a
standing settings rule: each `_v4` freeze/projection command surfaces a
permission prompt Ed approves at execution time (the most literal D-148.1
reading; no settings.local.json rule exists and none is required under this
form).
```

### The count of six

`docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md:166-171`,
verbatim:

```
V-7 (Ed packet, reordered and reconciled):
1. MINT LICENSE (blocks S-0; strictly Ed's hands per D-148.1 —
   classifier forbids self-granting; the six `_v4` commands +
   measurement-checkout scoping). FIRST, because everything gates
   on S-0.
```

### The two blocked classes, from the `_v3` precedent

`docs/process/ed-s5-mint-decision-2026-08-19.md:11-17`, verbatim:

```
The freeze mints themselves are BLOCKED by the Claude Code permission
classifier — for both the executing agent and the lead — on exactly these
command classes at the measurement checkout:
```

```
python3 scripts/project_identity_pins.py freeze <pack_root>      # U11, x3 first
python3 scripts/generate_arm_readiness.py freeze --pack-root <v3> --predecessor-pack-root <v2>   # x3
```

and the four settings-rule lines D-148.1 named, `:31-34`:

```
"Bash(python3 scripts/project_identity_pins.py freeze *)",
"Bash(python3 scripts/generate_arm_readiness.py freeze *)",
"Bash(cd /Users/edr/JouleWise-measurement-20260818 && python3 scripts/project_identity_pins.py freeze *)",
"Bash(cd /Users/edr/JouleWise-measurement-20260818 && python3 scripts/generate_arm_readiness.py freeze *)"
```

"Six" is therefore three `project_identity_pins.py freeze` invocations (one per
pack) plus three `generate_arm_readiness.py freeze` invocations — two command
classes, six executions.

### The other repository-mutating commands in the real sequence

Each of these writes to the repository and is not in either blocked class:

- three generator emissions producing the `_v4` pack roots
  (runsheet §3.1, `s0-runsheet-r4.md:1482`);
- three `author_arm_readiness_evidence.py` invocations
  (runsheet §3.4, `:1760`);
- `build_v4_histsem_pinset.py` — the mint itself (runsheet §3.7, `:1916`);
- `scripts/build_family_marker.py` (runsheet §3.8, `:2048`);
- the per-pack commits after each freeze
  (`s0-runsheet-r4.md:1625`: "Commit THIS pack only, so the next freeze starts
  from a clean tree").

### What remains Ed's hands under D-150b

`decision_log.md:176`, verbatim excerpt:

```
Remaining Ed-hands items: the pre-campaign reboot, window-night
non-interference, and S-0 permission prompts (or the optional settings rule).
```

`S0-COMPLETION-RECORD.md:30-31` names the same:

```
REMAINING FOR THE REAL TRANSACTION (not S-0's scope): Ed's D-150(1) live
permission prompts and D-150a reboot;
```

## (c) Answer space

**A. License scoped to the two `_v3` blocked classes — six prompts.**
Executes: Ed approves six prompts; every other repository-mutating command runs
without one, insofar as the classifier does not independently stop it.
Risk named by the item: if the classifier *does* stop one of the others, the
operator hits an unwarned prompt mid-transaction.

**B. License scoped to every repository-mutating command in the transaction.**
Executes: Ed can expect roughly six plus the emissions, the evidence authoring,
the mint, the marker build, and the commits — a materially larger and less
predictable count.
Requires: enumerating them before the session so the count is known in advance.

**C. Convert to a `settings.local.json` allow rule** (the option D-150 declined,
`decision_log.md:178`: "not a standing settings rule").
Executes: no prompts. Requires Ed's hands once to write the rule, since
self-granting is a hard harness boundary (`ed-s5-mint-decision-2026-08-19.md:23-28`).
Reverses the "most literal D-148.1 reading" D-150 adopted.

**Determinable before the session, under any branch:** whether the classifier
blocks each of the non-freeze commands is an empirical fact about the harness
configuration, not a ruling. It can be established by inspecting the effective
permission rules, so the prompt count can be made exact rather than estimated.

## Paraphrase check

Accurate. The "six" is confirmed at `rulings-r5-consolidation.md:168`; the two
blocked classes at `ed-s5-mint-decision-2026-08-19.md:14-15`; the "live prompts,
not a settings rule" form at `decision_log.md:178`. One note: the `_v3` settings
lines at `ed-s5-mint-decision-2026-08-19.md:33-34` are scoped to
`/Users/edr/JouleWise-measurement-20260818` by literal path, so a `_v4` rule
under branch C would need re-scoping to whichever path NR-1 selects.

---

# Assembly notes

## Sources read for this packet

Every quotation above was read from the file named, at the head of
`docs/real-transaction-runbook`, on 2026-08-25.

- `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence_t0.py`,
  `joulewise/identity_pins.py`
- `scripts/build_family_marker.py`, `scripts/verify_family_marker.py`,
  `scripts/window_status.sh`, `scripts/make_figures.py`
- `configs/arm_readiness/d117_row_registry_v2.json`
- `tests/test_env_locks.py`
- `env/mac-measurement-lock.txt`
- `docs/contracts/d117_step6_confirmation_table.md`
- `docs/phase_2/window_runbook.md`
- `docs/decision_log.md` (rows D-150, D-150a, D-150b, D-151, D-153)
- `docs/process/state_kernel.json`, `TASK_QUEUE.md`
- `docs/process/ed-s5-mint-decision-2026-08-19.md`
- `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`,
  `S0-COMPLETION-RECORD.md`,
  `o1-coldgate/MAGISTRATE-RULING-O1.md`,
  `marker-codesign/MAGISTRATE-RULING-MARKER.md`
- `docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md`
- `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`,
  `MAGISTRATE-RULING.md`, `MAGISTRATE-RULING-r3.md`,
  `rulings-r5-consolidation.md`, `readiness-sitting/VERDICT-PACKET.md`,
  `v4plan/opus-design.md`, `v4plan/sol-design.md`
- Read-only inspection of `/Users/edr/JouleWise-measurement-20260813`,
  `/Users/edr/JouleWise-measurement-20260818`, and
  `/Users/edr/code/JouleWise/.venv` (`git rev-parse`, `git status`,
  `pip freeze --exclude-editable`). No writes, no installs, no measurement
  command.

## Classification summary

| # | Class | Note |
|---|---|---|
| NR-11 | RULING | reading verified against source; branch E is mechanically empty |
| NR-3 | RULING (order text) | substance ALREADY-ANSWERED-BY runsheet §3.10 + D-153 A1/A3 |
| NR-2 | RULING | no `_v4` ruling on record; `_v3` precedent ran on a branch, not `main` |
| NR-9 | mixed | (1) ALREADY-ANSWERED-BY D-150b; (2) OPERATOR-FIX, edit target named; (3) RULING pending Ed |
| NR-1 | RULING + OPERATOR-FIX | path is a ruling; venv is fact-found — §7 understates the drift |
| NR-12 | RULING | also unresolved: who performs the attestation (three texts disagree) |
| NR-4 | RULING | §7's phase claim corrected below |
| NR-13 | ALREADY-ANSWERED-BY D-153 W4 + RULING on scheduling | kernel row `queued` |
| NR-6 | RULING | plus a missing procedure: `file-09-probe P1/P2/P3` exists nowhere |
| NR-5 | ALREADY-ANSWERED-BY `S0-COMPLETION-RECORD.md:30-33` (record, not ruling) | |
| NR-7 | RULING | two adopted texts, one interval |
| NR-8 | RULING | no candidates on record; design space enumerated |
| NR-10 | RULING | prompt count is empirically determinable before the session |

## Paraphrase defects found

Three, in descending materiality.

1. **NR-1 understates the venv drift.** §7 flags one package on one checkout.
   Verified: `-20260813` differs from the lock on 22 requirement lines,
   `-20260818` on 20 (including `mlx` 0.32.1 against the pinned 0.31.2), and the
   only environment exactly at lock is the *development* checkout's venv. A seat
   reading §7 alone could pick `-20260818` believing it in-lock.
2. **NR-4 misstates what `--phase` gates.** §7 says "every non-candidate phase
   drives the live four-way consult". The live four-way consult runs in every
   phase including candidate (`arm_readiness.py:10908-10924`); `phase` selects
   the tool-authentication lane, confirmation-table authentication, the C→S
   deferral, and the receipt's admissibility fields. S-0 satisfied the consult by
   forging `origin/main`, not by phase.
3. **NR-2 attributes a command form to the `_v3` doctrine that no source
   contains.** «`git pull --ff-only file://<measurement checkout>`» appears in no
   read source; `ed-s5-mint-decision-2026-08-19.md:66` says only "Landing is a
   pull FROM the measurement checkout (never a push from it)". The mechanism is
   described faithfully; the command is the runbook's own.

Minor, non-material: NR-13's cited line range `92-104` is `94-105` in the
current file (D-153 W4 and the kernel row carry the same off-by-two); the kernel
status is `queued` as §7 says while `TASK_QUEUE.md:647` shows the row as
`READY [AGENT]`.
