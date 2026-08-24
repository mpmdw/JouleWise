# Instrument v2 — design lessons

**Status: a lessons memo, not a commitment.** Nothing here is scheduled, funded,
or promised. It records what the instrument's governance code taught us during
the `_v4` transaction week of 2026-08-22/23, and what a second instrument would
have to do differently to not re-learn it. Filed against H2/H3. If v2 never
happens, this memo is still the honest post-mortem of v1's governance layer.

**Audience:** Ed, and whoever sits the first v2 design session. It is written to
be startable-from — a reader with no memory of this week should be able to open
a design session with only this file and the contracts it cites.

---

## 0. The words this memo uses

Every term below is used later in a load-bearing way, so each is built here
before first use rather than glossed in passing.

- **The instrument** — the JouleWise software that measures energy and then
  *governs its own outputs*: it decides whether a measurement is allowed to
  become a claim. Two very different jobs share one Python codebase today.
- **Artifact** — a file of bytes the instrument produced or consumes: a
  measurement pack, a receipt, a registry, a marker.
- **Receipt** — a machine-readable record stating which checks ran, on which
  exact bytes, and what each concluded. A receipt is the instrument's testimony
  about itself; everything downstream trusts receipts, so a receipt that records
  a check which did not actually execute is worse than no receipt.
- **Gate** — code whose only job is to refuse. A gate reads artifacts, applies a
  rule, and either lets execution continue or raises a *refusal*.
- **Refusal code** — the machine-readable name of why a gate refused, e.g.
  `readiness_r1_dependency_changed_set`. Downstream tooling switches on these
  names, so a refusal that arrives as an unnamed crash is a governance failure
  even when it stops the run.
- **Authenticator** — the thing that proves a set of bytes is the set of bytes a
  human approved. A checksum computed *from* the bytes is not an authenticator;
  it is a transport check. The week's sharpest formulation, and the sentence a
  v2 session should keep on the wall:

  > A byte pin authenticates **only** if changing the pinned bytes requires an
  > act the same actor cannot perform in the same breath. Its value comes
  > entirely from (i) the pin being older than the bytes' next change, and (ii)
  > updating it being a separate, separately-reviewed act.
  > (`o1-coldgate/opus-contract-refutation.md:279-283`)

  This distinction is the single most expensive lesson of the week, and §2.3
  defect class D is where it was violated twice.
- **Arm** (verb) — to authorize a measurement run to produce claim-bearing
  output. Arming is the moment the governance layer says yes; everything in this
  memo is about what must be true before it can.
- **Allowlist / changed-set gate** — before the instrument arms a claim, it
  computes which repository files changed between the commit that produced the
  evidence and the commit under review, then subtracts a reviewed list of paths
  known not to affect the science. What survives the subtraction blocks the arm.
  The reviewed list is the allowlist (112 entries at `_v4`).
- **Marker / pinset / freeze receipt** — three artifacts this memo cites by
  name. A *marker* records that a family of measurement packs was published; a
  *pinset* records the expected digests of a set of receipts, so later bytes can
  be checked against reviewed ones; a *freeze receipt* records that a pack's
  evidence was fixed at a given commit with a PASS or REFUSE conclusion.
- **Registry** — a reviewed JSON configuration file holding values that gates
  read at runtime (the allowlist, the refusal-code vocabulary and its typing,
  generation thresholds). Registry values are reviewed artifacts; code literals
  are not.
- **The gauntlet** — the review process that produced this week's defect corpus:
  an implementing agent builds a candidate, an independent seat that did not
  write the code audits it, adversarial refuters attack specific lenses, a
  magistrate adjudicates, and every fix round is re-audited. Sources cited in
  this memo are its output.

---

## 1. Why v2, and when

### 1.1 The forcing problem

The week of 2026-08-22 produced the densest defect corpus in the project's
history:

- a ten-item gap list (G-1…G-10) against the first candidate, four of them
  blockers (`MANIFEST.md:378-530`);
- an eleventh finding, **G-11, larger than all ten** — the candidate was red on
  **149 tests** (36 failures + 113 errors) across the arm-readiness blast radius,
  because the earlier "87 green" was green only for the four modules that had
  been run (`MANIFEST.md:606-613`, `:175-178`);
- an independent seat verdict of **REFUTED** — 3 blockers, 12 should-fix, 4 nits
  (`.../s1-seat-verdict.md`);
- an independent security refuter verdict of **REFUTED** — 1 blocker, 3
  should-fix, 1 nit (`.../s1-refuter-g2.md`);
- and a fix round that **found four defects of its own by running the code**
  (`MANIFEST.md:1277-1360`) and **introduced three more that remain open**
  (`:1145-1165`) — both recorded by the round itself rather than left for the
  delta reviewer to discover.

The corpus is worth studying because almost none of it is carelessness. Two
closing observations are the reason this memo exists. The first is about
*method*:

> Both blockers share a signature: the implementer reasoned carefully to a
> conclusion and never tested the cheapest falsifier.
> (`s1-seat-verdict.md:276-280`; the MANIFEST concurs at `:961-970` and made the
> fix round measurement-first in response)

The second is about *shape*, and it is the one this memo is built around. Of the
four defects the fix round found by running the code, the MANIFEST records:

> All four share a single signature: **a surface the round moved on ONE SIDE
> ONLY.** (`MANIFEST.md:1281-1283`)

The first is a process diagnosis, and process fixes are language-independent.
The second is not. "A surface moved on one side only" is the canonical failure
mode of a language in which the two sides of an invariant are two independent
pieces of text that nothing compares. A substantial fraction of the
*implementation* findings — §2.3 is scrupulous about which, and §2.4 is
scrupulous about which not — are defects that **could not exist in a language
whose type system carried the invariant**. When a refusal code is a string, "is
this code registered?" is a question a human must remember to ask, at every raise
site, forever; both independent design seats failed to ask it, and the marker
ruling records the registry-load closure check as what "genuinely cures the
`_receipt_refusal` → `readiness_internal_error` explosion hole both blind seats
shared" (`MANIFEST.md:368`). The Sol seat traced the exact shape: a typo'd or
divergent spelling passes the regex check, installs cleanly, and **"fails open at
install, closed at the worst possible time"** (`marker-design-opus.md:575-581`).
When a code is a closed enum, none of that is sayable, because the failure cannot
be spelled.

v2's thesis is narrow and testable: **move the invariants that gates depend on
from convention into the compiler**, and leave everything else alone.

### 1.2 Why post-paper only, and what the freeze makes safe

Today the instrument's governance code and its claim-bearing measurement corpus
are entangled: touching the governance code changes which measurements are
admissible, which is why the changed-set gate exists at all. That entanglement
is exactly why v2 cannot start now.

Once the paper's claims are **frozen** — the measurement corpus fixed, the
receipts issued, the numbers published — the entanglement inverts and becomes
protective. A frozen corpus is a **differential test bed**: any v2 kernel can be
run against every frozen artifact and required to reach the *same verdict* as
v1, artifact by artifact. That is a stronger acceptance test than v2 could ever
write for itself, and it does not exist until the freeze. §6.2 makes it the
gate.

Three further conditions the freeze supplies:

1. **No open window.** The changed-set contract is a *window property, not a
   standing repository invariant* — this was the unstated fact that generated
   the O-1 cold gate in the first place (D-151 condition 8, `MAGISTRATE-RULING-O1.md:75-80`).
   With no window open, a governance rewrite cannot void an in-flight arm.
2. **Ruled semantics are settled.** v2 inherits rulings rather than re-opening
   them (§5.2).
3. **P1/P2 are done.** The Rust idea was adjudicated on 2026-08-08 as *"genuine
   H2/H3 architecture idea; HARD NO for the MVP paper — textbook P3 work that
   sacrifices P1. Zero measurement-soundness benefit; would blow the paper
   window. Filed, not funded."* That ruling is not superseded by this memo; this
   memo is what "filed" looks like.

---

## 2. The architecture

### 2.1 The shape

```
  ┌──────────────────────── PYTHON SHELL (execution + analysis) ─────────────────┐
  │                                                                              │
  │   adapters/          harness/            analysis/                           │
  │   powermetrics,      run scheduling,     reduction, brackets,                │
  │   MLX runtime,       workload drive,     statistics, plots                   │
  │   model loading      sampling            paper figures                       │
  │        │                  │                    │                             │
  │        └──────────────────┴────────────────────┘                             │
  │                           │                                                  │
  │                    produces ARTIFACTS (packs, evidence, tables, registries)   │
  └───────────────────────────┼──────────────────────────────────────────────────┘
                              │
        ═══════════════ THE RECEIPT BOUNDARY ═══════════════
        Python hands over bytes + an out-of-band authenticator.
        It never hands over a verdict, and it cannot mint one.
                              │
  ┌───────────────────────────┼──────────────────────────────────────────────────┐
  │                           ▼                                                  │
  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌────────────────┐   │
  │   │  VOCABULARY │   │   GATES     │   │AUTHENTICATOR│   │ RECEIPT MINTER │   │
  │   │ refusal-code│   │ changed-set,│   │  digest-    │   │ executed-checks│   │
  │   │ enums,      │──▶│ head-equality│──▶│ before-parse│──▶│ only; private  │   │
  │   │ check-id    │   │ family-publ.,│   │ out-of-band │   │ constructor    │   │
  │   │ enums       │   │ freeze/replay│   │  hC input   │   │                │   │
  │   └─────────────┘   └─────────────┘   └─────────────┘   └────────────────┘   │
  │                                                                              │
  │            RUST GOVERNANCE KERNEL — small enough to read line by line         │
  └──────────────────────────────────────────────────────────────────────────────┘
                              │  PyO3
                              ▼
                   Python callers receive a receipt
                   or a *named* refusal — never a raw crash
```

Every element named:

- **Python shell** — everything that touches hardware, models, timing, or
  numbers. Adapters (`powermetrics`, MLX runtime, model loading), the harness
  that drives workloads and sampling, and the analysis code that reduces samples
  to energies and figures. This is where the science lives and it does **not**
  move. Rewriting a `powermetrics` adapter in Rust buys nothing and risks the
  one thing the project cannot risk.
- **The receipt boundary** — the horizontal double line. Python produces
  *artifacts*; Rust decides whether those artifacts authorize anything. The
  boundary is drawn at the receipt because the receipt is precisely the point
  where "we measured something" becomes "we are entitled to claim something."
  Everything above the line is fallible in ways measurement is always fallible.
  Everything below the line is where a defect silently converts a bad
  measurement into a published number.
- **Vocabulary** — the closed sets: refusal codes, `check_id`s, gate ids, role
  typings. In v1 these are strings validated by convention. In v2 they are
  enums, and the compiler is the closure check.
- **Gates** — the refusal logic: the changed-set subtraction, strict four-way
  head equality, family-publication, freeze/replay idempotence.
- **Authenticator** — the digest-before-parse channel described in §4.2/§4.10.
  It takes the expected digest as a *required* input; it cannot derive one.
- **Receipt minter** — the only code in the process able to construct a receipt
  value, via a constructor private to its module. Nothing outside can fabricate
  one, and this is compiler-enforced rather than convention-enforced.
- **PyO3** — the Rust↔Python foreign-function bridge. Python calls the kernel;
  the kernel returns either a receipt object or a *named* refusal. The kernel
  never returns an unnamed exception, because in Rust "unnamed exception" is not
  a thing a function signature can express.

### 2.2 Why the boundary is at the receipt and not elsewhere

Two rejected alternatives, so v2 does not re-argue them:

- **Boundary at the process edge (rewrite everything).** This is the
  second-system trap (§5.3). It puts the measurement path — the only part with
  frozen, published, hard-won correctness — at risk to buy governance
  guarantees, and it is what the 2026-08-08 adjudication refused.
- **Boundary at the CLI (Rust wraps Python).** Useless: the invariants that
  broke this week are *inside* the gates, not at the invocation surface. A Rust
  argument parser in front of a Python gate retires zero defect classes.

The receipt boundary is the smallest cut that puts every gate on the compiled
side while leaving every sampler, adapter and reducer on the Python side.

### 2.3 The defect-class table

Every class below is drawn from this week's record. The verdict column is
deliberately honest — five classes are marked **untouched**, and those five are
the reason §3's Python-only row is a real option rather than a straw man.

Four Rust mechanisms do nearly all the work in the verdict column, so they are
built here rather than assumed:

- **Sum type (`enum`)** — a type whose value is exactly one of a fixed, named
  list of alternatives. A refusal code declared as a sum type has no spelling to
  mistype and no registration step to forget: the list *is* the vocabulary.
- **Exhaustive `match`** — when you branch on a sum type, the compiler requires
  a branch for every alternative. Adding a new alternative breaks compilation at
  every place that branches on it, so a new case cannot be silently absorbed.
- **Newtype** — a distinct type wrapping one value, e.g. `PackDigest(String)`
  and `MarkerDigest(String)`. Both hold 64 hex characters; neither can be passed
  or compared where the other is expected.
- **Private constructor** — a type whose only construction site lives inside one
  module, enforced by the compiler (`pub(crate)`), not by a naming convention.
  Code outside that module cannot fabricate a value of the type at all.

| # | Defect class (this week's instance) | What made it possible | Rust verdict |
|---|---|---|---|
| **A** | **`-O`-strippable assert on a refusal path.** `assert table is not None and table_raw is not None` is load-bearing control flow in the published lane; under `python -O` it is stripped and `table["git"]` raises a bare `TypeError` — an ungoverned escape of exactly the class two other findings were written to cure. (`MANIFEST.md:1149-1154`) | The language has a runtime check that a compiler flag deletes, and it reads like a guarantee. | **RETIRED, conditionally.** `Option<T>` cannot be dereferenced without handling `None`; the check *is* the match, and no flag removes it. Conditional because `.unwrap()` reintroduces it — v2 must `#![deny(clippy::unwrap_used, clippy::expect_used)]` in the kernel crate. That deny-list is a one-line policy; the Python equivalent (ban `-O`, audit every assert) is a standing discipline nobody can prove holds. |
| **B** | **Exception-widening that swallows diagnostics.** The fix round made `_family_member` convert *every* residual `ArmReadinessError` into `FamilyPublicationError("evidence_set_mismatch")`. Fail-closed and governed — but registry, schema and structural faults are now all *diagnosed* as an evidence-set mismatch, widening what that `check_id` means inside a closed enumeration. (`MANIFEST.md:1155-1159`) | `except SomeBaseError` catches an open subtree the author never enumerated, and adding a new error subclass silently joins it. | **RETIRED for the silent half, REDUCED for the deliberate half.** An exhaustive `match` over an error enum forces every variant to be named, and adding a variant breaks compilation at *every* match site — the "silently subsumed a new kind" failure cannot occur. Deliberately collapsing variants is still writable (`.map_err(|_| …)`), but it becomes a visible line of code a reviewer can grep for, not an invisible property of a catch clause. |
| **C** | **Refusal codes exploding as internal errors because registration was conventional.** `_receipt_refusal` raises `readiness_internal_error` on any unregistered code, while the registry validator only shape-checks spellings — so a genuine, correct refusal surfaces as an internal error. **Both blind design seats independently shipped this hole**, and the marker ruling cured it with a registry-load closure check. (marker ruling ¶4, `MAGISTRATE-RULING-MARKER.md:38-49`) | A refusal code is a *string*. "Is this string registered?" is a question a human must remember to ask, at every raise site, forever. | **RETIRED.** Make the code a sum type. An unregistered refusal code is then not expressible — there is no string to mistype and no registration step to forget. This is the flagship case for the whole architecture: the cure v1 hand-built (a runtime closure check at registry load) is what a compiler does for free. |
| **C2** | **Dead entries locked into a closed enumeration.** Eight of the 32 `FAMILY_PUBLICATION_CHECK_IDS` were never raised anywhere; one scheduler mapping pointed at an unreachable code. Because the exactness test pins the set as exact, **"it LOCKS IN the dead entries"** — the test that enforces closure also protects the corpses. The fix round cut 32 → 29 and found **a ninth dead id the audit had missed**, via a new mechanical raise-site test. (`MANIFEST.md:427-437`, `:559`) | Closure is enforced against the *declared* set; nothing checks the declared set against the *reachable* one. | **REDUCED, honestly.** Rust's dead-code lint flags never-constructed enum variants, which is most of this for free. But a variant constructed only in a test, or only on a path no caller reaches, still passes — and the rule the project actually wants ("every diagnostic has a live raise site") stays a reachability question. The v1 cure — a mechanical raise-site test — remains necessary in v2. |
| **D** | **Self-authenticating artifacts — the sidecar tautology, twice.** (i) The confirmation table's `.sha256` sidecar is computed from the same bytes it accompanies, so a producer who forges the table trivially produces a matching sidecar (`docs/contracts/d117_step6_confirmation_table.md:44-47`). (ii) The tool self-hash: candidate mode computed a digest from the tool's *own current bytes* and compared it against a sidecar generated from those same bytes — i.e. "does this sidecar match this file" — so a modified tool passed by regenerating its own sidecar (`MANIFEST.md:375`). **Both design seats had rejected this anti-pattern by name** — "a self-produced digest proves nothing about the producer" (`marker-design-opus.md:848`; also `marker-design-sol.md:632`) — **and the implementation shipped both halves of it anyway.** | Nothing in any language stops you from checking bytes against a function of themselves. It is a *protocol* error, and it reads as security. | **UNTOUCHED for the absence, REDUCED for the confusion.** No type system can tell you your digest graph is missing an out-of-band edge; that is design work, and the cure (§4.2) is language-independent. What Rust *can* do is make `TransportChecksum` and `Authenticator` distinct newtypes, so passing a sidecar where an authenticator was required is a compile error rather than a review finding. That is the confusion, not the absence — and note that naming the absence in a design document demonstrably did not prevent it. |
| **E** | **One-sided surfaces — the fix round's own signature.** All four defects the fix round found by *running* the code were one class: **"a surface the round moved on ONE SIDE ONLY"** (`MANIFEST.md:1277-1360`). (i) A new CLI parameter was threaded into the parser and one hand-built `argparse.Namespace` in tests, but not its sibling → `AttributeError`. (ii) A signature fence pinned on one side while the library had re-founded it on the other. (iii) A synthetic test registry predating a new closure check. (iv) **A test double whose signature no longer matched production**, so `TypeError` was raised *from inside the mock* and 18 tests + 6 subtests across 6 modules failed for reasons unrelated to what they assert. Also here: the confirmation-table defaulting asymmetry, still **PARTIAL** — arm/verification/scheduler default to campaign custody while freeze, `_verify_arm_receipt`, `verify_consumed_launch` and the authoring path pass a bare `None` (`:1141`). | Two sides of one invariant are two independent pieces of text and nothing compares them. An optional parameter defaulting to `None` makes "not threaded here" and "deliberately absent here" identical. | **RETIRED for three of the four — the strongest row in the table.** A signature change in Rust breaks compilation at *every* call site, including test doubles, which must implement a trait rather than duck-type a `side_effect=`; there is no hand-built argument namespace to drift; and an authenticator typed as a required parameter of a type constructible only by supplying a real expected digest makes "one side passes nothing" a compile error. What stays: (iii) — a fixture whose *data* predates a rule is a value problem, not a signature problem. Note the cure's own limit: the round's systematic AST sweep over 22 changed signatures **did not cover mock doubles, which is exactly where the defect was hiding** (`:1352-1354`). |
| **E2** | **Scope derived from the review, not from the code graph.** The test-double defect was invisible to a twelve-module joint verification because the module that *defines* the shared mixin was not in the set — the set having been derived from the reviews' scope. "Only the repository-radius run found it" (`MANIFEST.md:1328-1334`). The same lesson at larger scale is **G-11**: an "87 green" that was green only for the four modules it ran, against 149 actually-failing tests — *"a green run is not evidence of the coverage the ruling ordered"* (`:175-178`). | A human picks which modules to verify, and dynamic dispatch hides the blast radius of a change. | **REDUCED, substantially.** The compiler's blast radius is the whole crate, not a chosen module set: a changed signature cannot fail to be checked at every use. Untouched is the runtime half — "which tests actually exercise this path" is a coverage question, and choosing too narrow a *test* radius stays possible. |
| **F** | **One-sided surfaces — prose that describes the wrong mechanism.** (i) In-test comments asserted as fact the exact claim the seat verdict refuted, so future readers would trust them (blocker B-3). (ii) A test whose name became false as the code moved beneath it, requiring a scheduled rename in the fixation commit (D-151 condition 3). (iii) Twenty-one tests labelled with one cause — "requires minted `_v4` packs" — when the measured dominant cause was something else entirely, and the measured partition turned out to be **0 S0-blocked / 17 structural / 4 crash** (blocker B-2; `s1-fixround-packet.md:31-46`). | Names, labels, comments and docstrings are prose. Nothing checks them. | **UNTOUCHED.** No compiler reads English. The only cure is the process one: labels must be *measured*, not reasoned — run the thing and record what it actually said (§4.11). |
| **G** | **Fixture debt — fixtures authoring legacy schemas.** `make_go_fixture` authors legacy generic freeze evidence while the R1 lifecycle requires content/execution receipt schemas, so 14 tests stop dead at `arm_readiness.py:5330` regardless of what bytes get minted. Tracked as A84 FIXTURE-MODERNIZATION-01. (`s1-fixround-packet.md:42-50`) | The fixture and the production authoring path share no structure — a dict is a dict. | **REDUCED.** If evidence schemas are types rather than dicts, a fixture authoring the legacy shape fails to compile against the R1 constructor, and schema drift becomes a build error instead of a 14-test mystery. What stays: a fixture with the *right shape and wrong semantics* still compiles. Fixture realism is not a type property. |
| **H** | **Grep-tests standing in for behavioural tests.** `getsource` source greps grew 9 → 13 across `tests/` against a MANIFEST claim that four had been rewritten as behavioural tests; `test_every_check_id_has_a_raise_site` was satisfied by commented-out and docstring text, and even after being rebuilt as an AST walk it still proves *presence*, not reachability. (seat findings 11, 12; `MANIFEST.md:1142-1143`) | Python cannot ask the compiler "is every variant handled?" or "is this branch reachable?", so tests approximate those questions by reading source text. | **REDUCED, by making the questions askable.** Exhaustive `match` plus `unreachable_patterns` and dead-code lints answer at compile time most of what these greps approximate. What stays untouched: "does this check actually execute in production?" is a coverage and mutation question, and no type system answers it. |
| **H2** | **Fixture digest collision blinding cross-field comparisons.** Every digest field in the schema fixtures was the same literal — `SHA = "0"*64` — so **"any cross-field comparison bug (comparing `pack_sha256` where `freeze_receipt.sha256` was meant) is invisible to the whole schema test class."** (`MANIFEST.md:518-521`) | Every digest has the same type (`str`), so nothing distinguishes one 64-hex value from another, in the code *or* in the fixture. | **RETIRED.** Distinct newtypes — `PackDigest`, `FreezeReceiptDigest`, `MarkerDigest`, `TableDigest` — make a cross-field comparison a type error, at which point the fixture's values stop mattering. This is the cheapest large win in the table and it generalises: every one of the week's digest-confusion hazards is a case of one primitive type standing for many distinct meanings. |
| **I** | **Unenumerated override lanes.** Supplying `pinset_path` replaced the closed enumerated tuple with an arbitrary file, and both public verifiers plus the CLI exposed it — a probe copied a valid pinset to a rogue path and got `PASS`, contradicting the unqualified closed-enumeration contract (refuter G2-3). The cure round then **introduced** a private `_pinset_rows` keyword that bypasses the loader entirely; it is underscore-private and not CLI-exposed, "but nothing asserts it is unreachable from an external caller." (`MANIFEST.md:1160-1165`) | (i) A `PathBuf` can stand in for a member of a closed set. (ii) Python privacy is a leading underscore — a convention, unenforced. | **RETIRED for both halves.** A closed enumeration typed as an enum cannot accept an arbitrary path. And `pub(crate)` is checked by the compiler, so "nothing asserts it is unreachable from an external caller" becomes a compile-time fact rather than an open residual. |
| **J** | **Fail-open by empty intersection.** No runtime check bound the code constant `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` to the registry allowlist. A spelling drift on either side makes the intersection empty — and the path is then subtracted **unconditionally**, i.e. it fails *open*. Caught only by a hardcoded literal in a test until the fix round added a real closure check. (seat finding 7; cure at `arm_readiness.py:2025-2032`) | Two sides of one invariant were expressed as independent strings. | **RETIRED.** One enum, referenced by both sides: spelling drift does not exist. This is the archetype of "the type would have *been* the check" — and note that v1's cure was to hand-write the check the compiler would have supplied. |
| **K** | **Hand-mirrored sets.** The `dynamic` refusal-code set in the library and the `dynamic_or_defensive` set in a test were hand-maintained mirrors with no mechanical link, despite a comment requiring they stay in step. Cured by deriving one from the other via AST parse. (seat nit 17; `MANIFEST.md:1130`) | Same as J: one invariant, two independent literals. | **RETIRED.** One enum; both sides iterate it. The AST-parse cure is an impressive workaround for a problem that should not be expressible. |
| **L** | **Time-of-check/time-of-use on verified bytes.** G7 verified the marker at one point, then *re-read* the marker and table paths to record digests — so a path swap between the two could make a PASS block bind bytes that were never verified. Cured by binding the digests computed inside the verifier and deleting both re-reads. (refuter G2-5; `MANIFEST.md:1137`) | The verifier returned *permission to look again* rather than the verified value. | **REDUCED.** Return the verified bytes (or a digest newtype) and give the caller no path to re-read; ownership makes "you still hold a handle to the mutable thing" visible at the type level. Honest limit: this is a design discipline that Rust makes *checkable*, not one it imposes. |
| **M** | **Evidence-token forgery vs test selection.** The 2026-08-08 adjudication: a Rust private-constructor evidence type, mintable only inside the runner module, is compile-time unforgeable and closes the "fabricate the evidence object" axis — but it does **not** close the deeper threat, because an adversarial in-repo test author can still skip the runner or write a non-verifying test. Test *selection* is a repository-trust question, not a type-system one. | Forgery is a construction problem (typeable). Selection is a trust problem (not typeable). | **SPLIT: forgery RETIRED, selection UNTOUCHED.** The cure for selection is the **mutation-kill harness** — an out-of-process tool that deliberately corrupts the production code, re-runs the suite, and requires that some test *fail*; a test corpus that stays green against a broken gate is thereby proven not to test it. That works identically in any language, needs no rewrite, and remains the correct answer in v1 *and* v2. v2 does not get to claim selection as a win. |
| **N** | **The operator boundary.** After the G2-1 cure, the expected confirmation digest `hC` is an **unauthenticated operator-supplied string**. The trust root moved from repository bytes (forgeable by whoever writes the table) to an out-of-band input, which is what the refuter demanded — "but nothing in code binds that string to Ed." The contract says the post-fixation standing source is a literal pinned in the fixation commit; **no code pins that literal**, so that half of the contract is prose. (`MANIFEST.md:1205-1214`) | The chain of custody ends at a human, and humans are not typeable. | **UNTOUCHED, and permanently so.** Every authentication scheme terminates in something outside the machine. v2's honest goal is to make the termination point *explicit and singular* — one operator input, named, required, and impossible to derive from the artifact — not to eliminate it. |
| **O** | **Environment and adapter faults.** A process-level `SIGABRT` in the MLX adapter aborts the interpreter at ~9% of a full pytest run, making four tests *uncollectable* rather than merely red (an xfail marker cannot contain a process abort); plus a non-deterministic flake that captures an ambient process command line and fails with a different byte diff each run. Both reproduce at merge-base — not branch regressions. (seat finding 15, observation O-1; A85) | Native-library and environment behaviour, entirely outside the governance layer. | **UNTOUCHED.** These live above the receipt boundary by construction. v2 inherits them unchanged; that is the correct outcome, not a gap. |

**Reading the table.** The retirements cluster tightly in one place:
**invariants currently expressed as two independent pieces of text that
something must spell identically** — a refusal code and its registration, a
constant and its registry twin, a signature and its test double, a digest and
the field it was meant to be compared against. Where the invariant is one enum
or one newtype, the defect stops being expressible. The reductions cluster
somewhere else: places where the compiler can *ask* a question that Python could
only approximate by reading its own source text. And the untouched rows are not
residue — §2.4 is about them, and they are the reason this memo does not end in
a recommendation.

### 2.4 The limit of the thesis — what none of this would have caught

**The corpus splits at the receipt boundary, and the split is inconvenient.**

Every defect in §2.3 comes from *implementation* — the candidate, its fix round,
the seat and refuter audits. The week also produced a large body of defects from
*design*: the O-1 cold gate and the marker co-design, three documents totalling
some 3,400 lines of adjudicated argument. **Not one of those is a type error,
and none of the three documents ever suggests otherwise.** Specifically, no
compiler in any language would have caught:

- **The embedded-confirmation hash cycle.** A marker whose digested body
  contained the confirmation digest requires the order: build marker → Ed
  confirms bytes → write confirmation → *rebuild the marker* to embed it — at
  which point **"the bytes Ed confirmed no longer exist"**
  (`marker-design-opus.md:941-956`). That is a graph-shape defect, caught by one
  model reasoning about another's design.
- **The authenticator allowlisted beside its subject.** Allowlisting both the
  pinset and the file that pins it means a coherent substitution of *both
  together* "is refused by **no** gate in the transaction"
  (`opus-contract-refutation.md:284-291`). The precedent it would have set is
  worse than the instance: *"The file holding a pin may be allowlisted alongside
  the file it pins"* generalises to **"any authenticator may be allowlisted next
  to its subject"** (`:309-320`) — which is the reasoning that produced the
  fixed-point rule (§4.5).
- **Path-granular subtraction.** Allowlisting one test file subtracts the
  *entire file* — twelve other normative tests — while the human confirmation
  covers one literal (`:964-973`).
- **Forged-ref green.** The same predicate on two surfaces with different
  truth-values: local green runs against a deliberately forged `origin/main`,
  so **"local green at the amending commit proves nothing about published green,
  and the two cannot be distinguished by anyone reading the transcript"**
  (`:786-787`).
- **A predicate false across adjacent generations.** The freeze-engagement rule
  was literally false at mint time for both `_v4` and `_v5`
  (`marker-design-sol.md:802`) — a co-travel defect between a rule and the
  moment it runs.
- **A forward reference to an unauthored key**, which would have surfaced as a
  `KeyError` rather than a governed refusal
  (`opus-contract-refutation.md:82-90`).
- **The bootstrap deadlock.** Had freeze engaged on the pack being minted rather
  than its predecessor, *"the family can never be created"*
  (`marker-design-opus.md:500-509`).

These are **value, graph-shape, phase, and co-travel defects**. They were caught
by adversarial cross-model design review with an adjudicator, and nothing else
would have caught them. Two further honest limits:

1. **A design that names an anti-pattern does not prevent it.** Both marker
   seats explicitly rejected self-produced-digest authentication by name. The
   implementation then shipped both halves of it (class D). Whatever v2 does, it
   must not treat "the design document says not to" as a control.
2. **The residual is a human.** After the cure, `hC` is an *unauthenticated
   operator-supplied string*: "nothing in code binds that string to Ed," and the
   contract's post-fixation pin "is prose" because no code pins it
   (`MANIFEST.md:1205-1214`). Every authentication chain terminates outside the
   machine (class N).

**The conclusion v2 must carry: types retire implementation defects;
adjudication retires design defects; and the gauntlet retires neither on its
own.** A v2 that ships a Rust kernel and retires the cross-model design review
because "the compiler has it now" would trade the cheap half of the corpus for
the expensive half. §4.13 is in the carry-list for exactly this reason.

---

## 3. Language decision matrix

| | Retires the flagship class (C: stringly refusal codes)? | Unforgeable evidence token? | Compiler-enforced module privacy? | Exhaustiveness? | Cost |
|---|---|---|---|---|---|
| **Rust** | Yes — enums + exhaustive `match` | Yes — private constructor, no reflection escape | Yes — `pub(crate)` | Yes | High: PyO3 boundary, two-language repo, build complexity, learning curve |
| **Go** | **No** — no sum types | Partial — unexported fields give a near-equivalent | Yes — package-private | **No** | Medium |
| **Swift** | Yes — enums with associated values | Yes — `private init` | Yes — `internal`/`private` | Yes | Medium-high, plus ecosystem risk |
| **Python + strict typing** | Partial — `StrEnum` + `assert_never` under `mypy --strict` | No — no construction Python cannot bypass | No — underscore is convention | Yes, at type-check time only | Very low |

**Rust — the choice, if v2 happens.** It is the only row that scores yes on all
four columns, and the four columns were chosen to be exactly the mechanisms the
§2.3 retirements depend on. The cost is real and should not be minimised: a
two-language repository, a PyO3 boundary to keep in sync, and a build that a
future maintainer must be able to run. The mitigation is scope — the kernel is
gates and vocabulary only, small enough that Ed can read every line of it, which
is itself a governance property no amount of Python typing buys.

**Go — no, and the reason is specific.** Go has no sum types, so the flagship
retirement (class C) is unavailable: refusal codes stay strings, registration
stays conventional, and the hole both blind design seats fell into stays open.
Go's `error` interface is stringly in the same way. It scores well on privacy
and would give a decent evidence token, but the single defect class that most
justifies the rewrite is the one Go cannot address. Ruled out.

**Swift — capable, ranked second, not chosen.** Enums with associated values,
exhaustive `switch`, `private init` and real access control give it every
mechanism Rust has. The one genuine argument in its favour is that the hardware
lane is macOS-anchored. Against it: the Python interop story is materially worse
than PyO3, and the Linux-side ecosystem for anything this project might later
need is thin. Choosing Swift would trade a well-trodden boundary for a
lightly-trodden one to buy nothing the boundary does not already provide.

**Python + strict typing — the honest baseline, and the thing to do first.** It
is not a straw man. `enum.StrEnum` for every vocabulary plus `mypy --strict`
with `typing.assert_never` in the default arm of every dispatch gives real
exhaustiveness: adding a refusal code breaks type-checking at every incomplete
handler. Frozen dataclasses plus a linted ban on constructing them outside their
module approximates the evidence token. Banning `-O` in CI closes class A.

What it cannot buy: nothing in Python is *unbypassable* — no private
constructor, no enforced module boundary, and every type guarantee evaporates at
runtime. And `assert_never` only fires where someone wrote a dispatch; it does
not find the raise site that formats a code by hand.

**Rough call: strict-typed Python retires or reduces most of what Rust would, at
a small fraction of the cost.** The Rust case rests on the residual — the
unbypassable half — and on wanting an audit surface small enough to read.

And §2.4 sets the ceiling on the whole matrix: **no row in it addresses the
design-round defects at all.** The hash cycle, the authenticator inside its own
allowlist, the forged-ref green and the false-across-generations predicate are
untouched by every column. A language choice is a decision about the cheaper
half of the corpus. Whether the residual justifies a rewrite is a judgment for
the v2 session, not a conclusion this memo is entitled to reach.

**What is not in doubt: the strict-typing pass is worth doing regardless, it is
worth doing to v1, and it is the best available evidence about how much of §2.3
is really type-shaped.**

---

## 4. Pattern carry-list — v2 requirements

These are patterns the week *validated*, not proposals. Each is a v2 requirement
with its origin.

**4.1 Registry-first configuration — the registry, not the module, is the
authority.** When the freeze-time engagement predicate turned out to be false
across adjacent generations at mint time, the adjudicated repair was a **tracked
generation-threshold value in the reviewed registry**, explicitly "not code
prose." The general form is stated exactly:

> Seven `readiness_r1_*` codes are resolved BY ROLE from the ruled registry's
> `refusal_vocabulary` at the moment of refusal, so they deliberately never
> appear as literals in the runtime source: **the registry, not the module, is
> the code/type authority**, and the registry-load closure check is what keeps
> them registered. (`MANIFEST.md:782-785`)

Two conditions make it work rather than merely relocate the problem. The value
must be **mandatory, not optional** — an optional threshold was a dormant
fail-*open* edge, since a registry that simply omitted it validated, whereupon
freeze set `None` and skipped publication. And the closure check must run **at
load, not at use**: an unregistered spelling that passes a regex "installs
cleanly and only fails at the moment a refusal is needed."
*Origin: marker ruling split S-2 (`MAGISTRATE-RULING-MARKER.md:80-84`); refuter
finding G2-4; `MANIFEST.md:557`, `:368`, `:782-785`;
`marker-design-opus.md:575-581`.*

**4.2 Out-of-band authenticator channels.** The authenticator of record is
`hC = SHA256(C)`, supplied **out of band** by the operator through an explicit
`expected-confirmation-digest` input — meaning it comes from transaction custody
*independently of the repository path being checked*, never from the artifact or
its sidecar. A consumer not given `hC` refuses: no subtraction, no publication.
The adjacent `.sha256` sidecar is transport integrity only and the contract says
so in as many words.
*Origin: refuter blocker G2-1 (`s1-refuter-g2.md:38-42`); contract
`docs/contracts/d117_step6_confirmation_table.md:44-56`.*

**4.3 The acyclic digest graph.** Exactly two immutable consumers — marker bytes
`M` and successor pinset bytes `S`. The final table bytes `C` contain both
digests; the only edges are `C → M` and `C → S`; neither `M` nor `S` names `C`,
so the graph is acyclic by construction. One human confirmation over `hC`
authenticates both. The competing design's embedded-confirmation field was
conceded by its own author as **a genuine hash cycle** — an artifact whose
digest must be known before the artifact exists.

```
        Ed's single YES
              │  names hC = SHA256(C)
              ▼
        ┌───────────┐
        │  TABLE C  │   contains hM and hS
        └─────┬─────┘
        C→M   │   C→S
      ┌───────┴───────┐
      ▼               ▼
 ┌─────────┐    ┌──────────┐
 │MARKER M │    │ PINSET S │     neither names C — no cycle
 └─────────┘    └──────────┘
```

*Origin: marker ruling ¶1-2 (`MAGISTRATE-RULING-MARKER.md:14-32`); contract
§"Acyclic digest graph".*

**4.4 Closed, code-enumerated vocabularies with a load-time closure check.**
Diagnostic granularity comes from a closed `check_id` frozenset, **not from new
refusal codes**; the registry load asserts every code in the vocabulary is
registered and typed. The refuter measured the closure at 8/8 registry roles and
29/29 marker diagnostics mapping into 6 registered codes.
*Origin: marker ruling ¶4; refuter lens (d) (`s1-refuter-g2.md:56`); the
fail-open this prevents is seat finding 7.*

**4.5 The fixed-point rule — no authenticator ever enters an allowlist.**
Standing rule for all future transactions: adding an authenticator path to any
allowlist is a **tripwire event routing to the derived manifest, not an
amendment lane**. The reason is exact: if the authenticator lives inside the set
it authenticates, repository bytes could replace both the subject and its
alleged authenticator together — a coherent substitution of both "is refused by
**no** gate in the transaction."

The rule is stated as a standing one rather than a case ruling because the
*precedent* was worse than the instance. The proposal's general form —
*"the file holding a pin may be allowlisted alongside the file it pins"* —
"authorises allowlisting any authenticator next to its subject," with `_v5`
citing it at 114 and `_v6` at 115. The rule exists to make that growth path
unavailable. v1 asserts it mechanically: zero paths in the 112-entry allowlist
match the table or family-publication patterns.
*Origin: D-151 condition 7 (`MAGISTRATE-RULING-O1.md:70-74`), minted at
`opus-contract-refutation.md:601-620` and `:1063-1068`; the refutation at
`:284-291`; the precedent argument at `:309-320`; mechanical assertion at
`tests/test_arm_readiness_schemas.py:379-380`.*

**4.6 Phase-explicit lanes — never selected by file presence.** The tool-hash
defect was that the *mode* was chosen by `if sidecar_path.exists():`, so dropping
a `.sha256` beside a production tool skipped committed-blob equality entirely.
The cure: an explicit `--phase` flag defaulting to the strict production rule,
with candidate mode reading a *reviewed input manifest* rather than the tool's
own bytes. Candidate green is recorded as forged-`origin/main`-conditional and
may never be reported as published green.
*Origin: `MANIFEST.md:375` (the defect), `MANIFEST.md:558` §8.6 G-4 (the cure);
D-151 condition 4 two-part green; contract §"Candidate and publication lanes".*

**4.7 Executed-checks-only receipts, with nulls on refusal.** A receipt records
only checks that actually ran, in code order. On refusal the corresponding
fields are null rather than carrying stale or optimistic values — a refusal
"must not copy unverified claims from a malformed marker." The defect this
replaced is the exact reason the rule is needed: the verifier's `checks[]` array
was **a hardcoded literal list, not a record of checks actually executed — it
reported `predecessor_mismatch: PASS` for a check that never runs.** A receipt
that lies in the PASS direction is the worst artifact the instrument can
produce, because it is precisely what a reviewer trusts.
*Origin: the defect at `MANIFEST.md:522-525`; the cure at `:563`;
`LEAD-READ-LEDGER.md:11-12`; `marker-design-sol.md:881`.*

**4.8 Strict four-way head equality, and the rollback refuter that forced it.**
Publication head == HEAD == local main == origin/main, with a clean tree, at all
three live consult points. Ancestry-only was refuted by a decisive argument:
**a checkout of an OLD published head after origin advances is trivially an
ancestor of both**, so ancestry admits a rollback. Ancestry plus dual-coordinate
byte mode survives only for archival verification.
*Origin: marker ruling split S-1 (`MAGISTRATE-RULING-MARKER.md:66-78`).*

**4.9 Freeze/replay idempotence and the poison question.** The *poison question*
is: "if a gate refuses, does the refusal get written and pinned as the standing
conclusion?" The instrument's answer at pinned HEAD is **YES** — freeze
unconditionally writes and plan-pins the PASS *or REFUSE* receipt, and replay
authenticates and returns that conclusion. The consequence is procedural and
severe: mint into a **sacrificial clone first** and require PASS; after a
primary REFUSE write, abandon the primary clone and restart, never repair the
pinned refusal in place. Any third outcome — partial write, traceback, or replay
not idempotent — reopens the mechanism.
*Origin: S-0 runsheet r2 `:432`, `:1035`; the class this defends is the
"poisoned retry" pattern the project has hit since 2026-07-07.*

**4.9b Digest equality and semantic replay are complements, never rivals.** The
verifier does both, and the reason is exact:

> **Digests catch byte substitution; replay catches a receipt whose bytes are
> intact but whose evidence no longer authenticates. Neither subsumes the
> other.** (`marker-design-opus.md:1033-1049`)

This is why the seat verdict could rule that removing semantic replay would have
voided the allowlist's lawful basis: for the 99 allowlisted source and evidence
paths the listed authenticator is a digest check, "which a coherent rewrite
defeats **by construction**. Semantic replay is the ONLY remaining authenticator
for those paths."
*Origin: `marker ruling ¶3`; `MANIFEST.md:941-943`; seat blocker B-1.*

**4.9c Mechanical enforcement over prose.** Custody-externality is not asserted
in a document; the builder resolves `--output` and refuses any path inside the
repository worktree, and a build must leave `git status --porcelain` empty. The
formulation to carry:

> **Prose would not have bound this; a `realpath` prefix check does.**
> (`marker-design-opus.md:395-396`)

*Origin: marker design §3.4; proof obligation T-O1 at `:786-789`.*

**4.9d Falsifiers must pin the specific code, not "some refusal."** Every
regression is a falsifier — it must fail before the fix and pass after — and
each tamper must produce its *specific* sub-code, because **"a test that only
asserts 'some refusal' would pass against a gate that refuses for the wrong
reason."** v1 has the counter-example on file: a scheduler test whose function
was *total* into the code set via its catch-all, making the loop's input
irrelevant.
*Origin: `marker-design-opus.md:732-735`; the vacuous instance is seat finding 8.*

**4.10 Authenticate before you parse.** The confirmation-table authenticator
runs in a fixed order: a missing expected digest refuses before anything is
read; a malformed digest refuses next; only then are the bytes and sidecar read;
only after `sha256(C) == expected` does full schema validation run. **No table
semantics — not even the literal `authority == "ED"` and `decision == "YES"` —
are parsed or trusted before the digest matches.** The original defect was
exactly the inverse: the validator treated literal `ED`/`YES` inside
caller-supplied bytes as confirmation.
*Origin: `MANIFEST.md:1175-1203` §10.1.1; the defect is refuter blocker G2-1.*

**4.11 Measured labels, not reasoned ones.** Twenty-one tests were labelled with
a cause nobody had run one of them to observe; measurement produced a completely
different partition (0 / 17 / 4) and the acceptance criterion built on the
reasoned label was struck. The requirement: **any label that gates something is
produced by executing the thing and recording what it said**, and the
enumeration is mechanical — v1 now enforces its own partition with
`tests/test_s0_blocked_enumeration.py`.
*Origin: seat blocker B-2 (`s1-seat-verdict.md:63-112`); magistrate ruling R1
(`s1-fixround-packet.md:8-15`); `MANIFEST.md:1216-1238`.*

**4.12 Engagement bound to tracked bytes, never to artifact presence.** Whether
a gate is *engaged* is determined by committed registry bytes, never by whether
a marker file exists — deleting the marker must **refuse**, not disengage. And
freeze-time engagement is predecessor-only, so the artifact being minted is
never gated on its own unbuilt publication (the bootstrap cure).
*Origin: marker ruling ¶5 (`MAGISTRATE-RULING-MARKER.md:50-54`).*

**4.13 Writer ≠ reviewer, and a delta re-audit of every fix round.** Both of the
week's headline verdicts came from seats that did not write the code, and the
fix round introduced three fresh defects that only a delta audit would have
caught — the MANIFEST records them itself, which is the behaviour to preserve.
No language change substitutes for this.
*Origin: `s1-seat-verdict.md:3-6`; `MANIFEST.md:1145-1148`.*

---

## 5. The fence — what v2 must not do

One page. If a v2 session finds itself arguing against any of the following, the
session has gone wrong.

### 5.1 It must not invalidate the paper's frozen claims

v2 is a governance rewrite, not a science change. The measurement path, the
reduction, the brackets, the estimator sources and the published numbers are
**out of scope by construction** — they sit above the receipt boundary (§2.1).
The r6-pinned estimator sources have a standing frozen-surface hazard that every
write authorization already checks; v2 inherits that fence unchanged. If a v2
design produces a different number for any frozen artifact, that is a v2 defect,
never a v1 correction.

### 5.2 It must not re-litigate ruled semantics without new evidence

The following were adjudicated with recorded reasoning and dissents preserved.
v2 inherits them. Reopening any requires *new evidence*, not a fresh opinion —
and the standing structural dissent (the derived, digest-authenticated manifest
under V-1(vii)) is already recorded, so rediscovering it is not new evidence.

- Committed-pinset-deletion absence semantics — a proposed tightening was
  **struck** for inverting a settled test, not being entailed by the obligation
  it claimed, and failing open on shallow history and history rewrite (D-151
  condition 9).
- The allowlist stays at **112**; no ruled number is amended (D-151 condition 1).
- Strict four-way equality over ancestry (marker split S-1).
- The ruled refusal-code spelling; an alternative spelling was withdrawn as
  reopening a ruled vocabulary (marker ruling ¶4).
- The seven-gate scheduler enumeration, as amended by the marker ruling.

### 5.3 It must not become a second system

Named temptations, because unnamed ones win:

- **"While we're here, rewrite the adapters."** No. Class O in §2.3 is untouched
  by design; moving it below the boundary buys nothing and risks everything.
- **"While we're here, improve the schemas."** No. Schemas port as-is (§6.1).
  A schema change makes the differential harness (§6.2) impossible, which
  removes v2's only real acceptance test.
- **"While we're here, add the mechanism-level metrics axis."** That is a
  separate roadmap item behind its own fence. It is not v2.
- **"A Rust analysis pipeline would be faster."** Speed is not a problem this
  project has. Correctness of governance is.
- **Scope test:** if a proposed v2 change does not retire or reduce a numbered
  defect class from §2.3, it is out of scope. That test is the fence.

### 5.4 It must not start before the freeze, or consume P1/P2 budget

The 2026-08-08 adjudication stands: this is P3 work, and P3 is sacrificed if it
costs P1 or P2. This memo does not fund anything.

---

## 6. Migration sketch

### 6.1 What ports as-is — because it is already language-neutral

This is the pleasant surprise of the exercise. The genuinely hard-won assets of
the governance layer are not code:

- **Contracts.** `docs/contracts/d117_step6_confirmation_table.md` and its
  siblings are normative prose describing byte layouts, digest graphs and
  enforcement conditions. They contain no Python. They port unchanged, and the
  ONE-home discipline ports with them.
- **Schemas.** Canonical JSON encodings — UTF-8, duplicate-key refusal, finite
  values, sorted keys, two-space indent, one trailing newline — plus the exact
  GNU SHA-256 sidecar form. Byte-level specifications, language-neutral.
- **Registries.** `configs/arm_readiness/d117_row_registry_v2.json` and the
  pinsets: the 112-entry allowlist, the generation threshold, the eight-role
  refusal-code typing, the horizons. These are *data*, and v2 must read the same
  files rather than transcribing them.
- **Rulings and their dissents.** D-150, D-151, the marker ruling and its six
  splits. These are the reasoning v2 is not entitled to redo (§5.2).
- **The vocabularies themselves.** The refusal-code names and their role
  typings port verbatim; only their *representation* changes, from strings the
  registry shape-checks to enum variants the compiler closes.

### 6.2 What re-derives — the science-neutral reissue discipline

**v2 must never accept a v1 receipt as evidence.** A kernel that reads v1
receipts as valid imports v1's trust wholesale, including whichever defects the
gauntlet has not yet found. The discipline instead:

1. v2 re-runs its own verification against the same frozen artifacts.
2. v2 issues **its own** receipts, under its own vocabulary.
3. A **differential harness** asserts that v1 and v2 reach the same verdict —
   same PASS/REFUSE, same refusal code — on every frozen artifact and every
   adversarial probe in the corpus (including the six constructed bypasses the
   G-2 cure survived, and the refuter's replayed attack now pinned at
   `tests/test_launch_window.py:511-689`).
4. **Any disagreement is a v2 defect until proven otherwise** — and if it is
   proven to be a v1 defect instead, that is a finding routed through the
   ordinary gauntlet, never a silent v2 "correction."

That harness *is* v2's acceptance test, and it is why §1.2 makes the freeze a
precondition: the corpus must stop moving for the comparison to mean anything.

Acceptances that must be re-earned rather than translated: every arm
authorization, every family publication, every freeze receipt, every changed-set
subtraction.

### 6.3 What retires

Machinery that exists only because Python could not express the invariant:

- The runtime closure checks at registry load (class C, J) — subsumed by enum
  deserialization with unknown-variant refusal.
- The source-grep and `getsource` tests (class H) — subsumed by exhaustive match
  plus unreachable-pattern and dead-code lints.
- The AST-parse test that derives one set from another to keep hand-mirrored
  literals in step (class K) — one enum, both sides iterate it.
- The hand-written "is this refusal code registered" discipline at every raise
  site (class C).
- `@unittest.expectedFailure` — already eliminated in v1 for being wrong twice
  over: it passes on *any* exception, and it takes no argument, so its
  documented reason was a source comment attached to nothing, invisible to every
  report and every tool.

### 6.4 Sequencing

1. **Do the strict-typing pass on v1 first** (§3, Python row). It is cheap, it
   is useful whether or not v2 happens, and it is the best available evidence
   about how much of §2.3 is really type-shaped.
2. **Freeze.** Paper claims fixed; no window open.
3. **Build the differential harness against v1** — before any Rust exists. If
   the harness cannot be built, v2 cannot be accepted, and that is worth
   discovering for free.
4. **Greenfield the kernel** behind the harness. Vocabulary first (the flagship
   retirement), then the authenticator channel, then the gates.
5. **Nothing merges until v1 and v2 agree on every frozen artifact.** Then, and
   only then, cut the Python callers over to the PyO3 boundary.

---

## Appendix — source index

| Source | What it supplies |
|---|---|
| `docs/process_traces/2026-08-22-t20/s1-candidate/s1-seat-verdict.md` | Independent writer≠reviewer verdict: 3 blockers, 12 should-fix, 4 nits; the same-signature meta-observation |
| `docs/process_traces/2026-08-22-t20/s1-candidate/s1-refuter-g2.md` | Security refuter: G2-1 unauthenticated confirmation digest, plus G2-2..G2-5 |
| `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md` | §9/§10: the cure table, the three defects the fix round introduced, §10.1.1 authenticate-before-parse trace, §10.2 measured partition |
| `docs/process_traces/2026-08-22-t20/s1-candidate/s1-fixround-packet.md` | Magistrate rulings R1/R2; the measured 0/17/4 partition; A84/A85 rows |
| `docs/process_traces/2026-08-22-t20/s1-candidate/LEAD-READ-LEDGER.md` | Slice-by-slice lead read; executed-checks-only receipts; nulls-on-refusal |
| `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md` | D-151: fixed-point rule, digest-conditional allowlist, two-part green, struck tightening |
| `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md` | Marker design ruling and six splits: strict four-way equality, generation threshold, library-boundary gate, tool-hash lanes |
| `docs/process_traces/2026-08-22-t20/o1-coldgate/opus-contract-refutation.md` | The authenticator definition (`:279-283`); the allowlisted-authenticator refutation (`:284-291`); the three precedent licences (`:309-320`); path-granularity (`:964-973`); forged-ref green (`:786-793`); the merged nine-condition set (`:1040-1079`) |
| `docs/process_traces/2026-08-22-t20/marker-codesign/marker-design-opus.md` | Blind seat: the hash-cycle concession (`:941-956`), bootstrap deadlock (`:500-509`), engagement-not-by-presence (`:511-519`), digests-and-replay-are-complements (`:1033-1049`), mechanical-not-prose (`:395-396`), falsifier specificity (`:732-735`), closure-at-install (`:575-581`) |
| `docs/process_traces/2026-08-22-t20/marker-codesign/marker-design-sol.md` | Blind seat: the acyclic digest flow (`:972-984`), the rollback refuter (`:739-746`), the cross-generation predicate repair (`:796-802`), no-mutable-lane-field (`:768-769`) |
| `docs/contracts/d117_step6_confirmation_table.md` | The acyclic digest graph, sidecar-is-not-authentication, the eight `C → S` enforcement conditions, candidate vs publication lanes |
| `docs/process_traces/2026-08-22-t20/s0-runsheet-r2.md` | The poison question and its YES answer; the sacrificial-clone consequence |
| `docs/run_reports/2026-08-22-t20-session.md` | Session narrative; §8 CI incident; §9 delegation calibration |
| Memory: `rust-rewrite-witness-integrity` | The 2026-08-08 adjudication: private-constructor token real, test-selection language-independent, hard no for P1 |
