# RECEIPT-HISTSEM-01 — Opus seat, debate response to terra

Read `rh-terra-design.md` in full. My design (`rh-opus-design.md`) stands
except where marked CONCEDED below. Every contested citation was
re-executed in `wtNEXT` at `bea0648`.

**Headline:** terra wins the placement argument outright, and the evidence it
sent me to led me to the mechanism that makes its placement free — a
precedent I had missed and that dissolves the only objection I had to it. I
hold on the anti-drift self-test, the `freeze` gate, refusal granularity, and
the control half of the regression. Two seats converged on the primitive and
diverged almost perfectly complementarily elsewhere; the union is materially
better than either.

---

## D1 — Historical hash primitive · **AGREED (independent convergence)**

Both seats derived the same function from the same two blockers: `HEAD`
hardcoded at `joulewise/arm_readiness.py:2563`, worktree-byte comparison at
`:2658-2667`. Both prescribe `ls-tree -rz --full-tree <commit>` +
`cat-file blob <oid>` + unchanged D-134 framing, and both keep the same
admissibility gates. Independent convergence on a load-bearing mechanic is
worth recording.

**Sub-divergence — where the primitive lives · CONCEDED to terra.** I put it
in a new `joulewise/receipt_histsem.py`; terra puts it in
`joulewise/arm_readiness.py` beside `committed_pack_tree_sha256` (`:2553`).
Terra is right: it shares `_run_git` (`:2520`) and
`_repository_and_pack_relative` (`:2540`), it is the literal sibling of the
function it mirrors, and once the gate itself moves in-library (D11) a
separate module buys nothing but an import edge. It also puts the differential
self-test (D7) on two functions ten lines apart, where drift is visible in
review.

**Only evidence terra lacks that I hold:** terra asserts the primitive works;
I executed it. 9/9 exact matches against the recorded `pack_sha256`
(`rh-opus-design.md:§1c`). Terra's V1 verifies only that the five commits are
*present*. Recommend the ruling record the executed table, since it is what
converts "closure shape" into "closable today."

---

## D2 — Check inventory: my K5+K7 vs terra's pinned-current-digest · **CONCEDED IN PART, and I withdraw my own headline**

My design's §8.1 asserted "K7 (delta envelope), not K5, is the check that
actually closes C1." **That claim is wrong and I withdraw it.** Terra's item 1
— authenticate the current pack against its *pinned* final-tree digest —
closes my own T2 attack (edit a config file at HEAD, coherently repair the
chain) more simply and more completely than a delta envelope does, because
`committed_pack_tree_sha256` covers every file in the pack. I had the same
value in my own pinset (`current_pack_sha256`, §4) and under-weighted it while
promoting K7. Self-inflicted; conceded.

Terra's pinset is also cleverer than mine in one respect I want on the record:
by pinning all **99 receipt SHAs**, it transitively pins every receipt's
`head_commit` and `pack_sha256` without listing them, so a history rewrite is
caught by K5 recompute against an immovable expected value.

**What survives, demoted and re-argued.** K7 is no longer "the check that
closes C1." It survives as the **pinsetless-mode structural invariant**, with
a failure mode no pinned value can cover:

1. **Bootstrap.** When a *new* pinset row is minted (the `_v4` row — D18),
   `current_pack_sha256` is whatever is in the tree at that moment. A pin
   records the tamper as faithfully as the truth. K7 is a statement about
   *process shape* — "the delta from `head_commit` to HEAD is custody
   authoring and nothing else" — verifiable with no prior trusted value. It is
   the only check in either design that can validate a pinset row rather than
   consume one.
2. **Interpretability.** A pinned-digest mismatch says "digest differs." K7
   says "`producer_contract.json` was modified after the freeze." At 3am
   before a window that difference is the whole value.

**Refinement conceded to terra's shape:** split K7. The *code-level* rule
(zero deletions; additions confined to `arm_readiness.evidence/`,
`arm_readiness.freeze.receipts/`, `arm_readiness.sources/`,
`identity_pin_projection.receipts/`; modifications drawn only from the closed
set `{plan_tree.json, plan_tree.sha256, producer_contract.json,
generate_configs.py}`) lives in code and is not editable as data. The pinset
narrows it per pack. Measured basis: 37 adds / 0 deletes / ≤4 modified paths,
identical shape across all 9 packs.

**Verdict: CONCEDED on priority; K7 RETAINED at reduced rank as
defense-in-depth + pinset-row bootstrap.**

---

## D3 — `facts[].source_sha256` · **CONCEDED**

I made it opt-in (`--recheck-facts`) on the grounds it is already enforced at
replay (`arm_readiness.py:4284-4321`, refusal `:4304`). Terra makes it
mandatory (its item 4). Terra is right and my reasoning was misaimed: replay
coverage is a property of the *arm path*, and this verifier's primary lane is
**CI, where no replay runs**. A verifier whose CI mode is weaker than its
pre-arm mode is the wrong shape. Cost is nil — 108 fact→source refs across the
corpus, measured 108/108 green. **Promote to mandatory.**

---

## D4 — Pre-authoring invariant · **DISPUTED (terra lacks it; I hold)**

Measured: at every receipt's `head_commit` the pack tree contains **zero**
files under the four custody directories (`evfiles 0`, all 9 packs). The
recorded `pack_sha256` is by construction the pre-authoring digest. Terra has
no equivalent check.

It is not redundant with K5. K5 asks "does the historical tree hash to the
claimed value"; this asks "is the claimed coordinate the *kind* of coordinate
a freeze receipt may name." A receipt naming a post-authoring commit is
self-inconsistent even if its digest recomputes. **Add as
`histsem_historical_tree_not_pre_authoring`.**

---

## D5 — Ancestry · **DISPUTED (terra lacks it; I hold, with reduced weight)**

Terra requires only that the commit be *readable* (`git cat-file -e
<oid>^{commit}`). A fabricated side commit is readable. My K3 adds
`git merge-base --is-ancestor <head_commit> HEAD` (hard) — measured: all five
distinct commits are ancestors of both `HEAD` and `origin/main`.

I concede the weight is lower than I first argued: with terra's 99 pinned
receipt SHAs, `head_commit` cannot move without a pinset edit. So this too is
pinsetless-mode depth. It costs one `git` call per pack; keep it.

**Retain the origin/main split from my design** — ancestor-of-`origin/main`
**hard in CI, advisory pre-arm** (`histsem_commit_unpublished`). Without the
split, the `_v4` mint cannot be gated on the night it is minted, because its
`head_commit` is legitimately unpushed for minutes. Terra's design has no
mechanism for this and would either refuse the mint or not check publication
at all.

---

## D6 — Predecessor binding · **DISPUTED (terra lacks it; I hold)**

Measured green on all three families: successor `freeze-0003`'s
`predecessor.pack_sha256` equals `committed_pack_tree_sha256(predecessor)` at
HEAD — `95f7c51ca4f2833a…`, `e5ec0f74df3a61da…`, `2fe51b037ad063f9…`, all
MATCH. This chains `_v3 → _v2 → _v1` and is corroborated by the S5 table's
published `freeze-0002` digests (`docs/process/ed-s5-mint-decision-2026-08-19.md:78-80`).
Two `git` calls per family. Terra checks each pack in isolation. **Add.**

---

## D7 — Differential self-test · **DISPUTED (terra lacks it; I hold — MAJOR)**

Terra's spec says "retain the exact D-134 domain and framing" and enumerates
it in prose. Prose is not a pin. The failure this invites is silent and total:
a re-implementation that drifts from `arm_readiness.py:2653-2676` produces
digests that are internally consistent, reproducible, and **wrong**, and every
receipt fails for a reason nobody can diagnose — or worse, a future edit to
`committed_pack_tree_sha256` silently desynchronises the pair and the verifier
starts attesting to a framing the rest of the system no longer uses.

The mechanical pin:
`historical_pack_tree_sha256(repo, "HEAD", rel) == committed_pack_tree_sha256(root)`.
Executed, equal on `d117_floor_qwen25_1p5b_v3` (`1e3f1fa31027e570…`),
`d117_floor_qwen25_1p5b_v1` (`5def6e514116184d…`), `metrology_v1`
(`b2462b3d56048388…`).

This is the single highest-value item either seat produced that the other
lacks, and terra's decision to co-locate the primitive (D1) makes it cheaper
still. **Mandatory acceptance item; run over all 9 packs.**

---

## D8 — Plan-binding coordinate · **DISPUTED (terra ambiguous; I hold)**

Terra's item 2 says "verify plan-tree raw bytes and sidecar" and names no
coordinate. Measured: `plan_tree.json` and `plan_tree.sha256` **differ between
`head_commit` and HEAD in 9/9 packs** — freeze minting writes the
`freeze-0003` reference into `arm_attachments.arm_readiness.freeze_receipt`.
An implementer who reads terra's spec and checks the plan binding at the
historical coordinate refuses the entire corpus on day one.

Not a defect in terra's design, but a genuine ambiguity in a spec that will be
handed to an implementer. **The ruling must state the two-coordinate rule
explicitly: `pack_sha256` + pre-authoring invariant are HISTORICAL; sidecar →
freeze → plan binding is CURRENT (HEAD).**

---

## D9 — History-unavailability refusals · **DISPUTED (I hold)**

Terra collapses shallow-repo, unreadable commit, unreadable tree, unreadable
blob, and generic git failure into one `histsem_history_unavailable`. I split
into `histsem_history_shallow`, `histsem_commit_unresolvable`,
`histsem_pack_absent_at_commit`, `histsem_historical_tree_anomalous`,
`histsem_git_unavailable` (+ `histsem_commit_off_lineage`,
`histsem_commit_unpublished` from D5).

Terra's own residual-risk paragraph is my argument: *"shallow, pruned, or
otherwise incomplete history prevents CI/pre-arm authorization until a full
governed checkout is supplied."* Those are two categorically different
situations wearing one code. A shallow clone is a **fixable environment
problem** (`git fetch --unshallow`, thirty seconds, no integrity implication).
A commit unresolvable *in a non-shallow clone* is **evidence the history was
rewritten or pruned** and must stop the operator cold. Emitting the same
string for both trains the operator to treat the second as the first — which
is exactly how C1 came to exist.

The repo's own doctrine is on my side: `READINESS_REASON_CODES` carries 47
discriminated codes (`tests/test_arm_readiness_schemas.py:1003`) rather than a
handful of buckets, and D-134's whole posture is a closed, discriminating
vocabulary. **Hold.**

---

## D10 — "Do not fetch or repair history during CI or arming" · **CONCEDED**

Terra states this; I did not. It is a real rule and I should have written it.
A verifier that self-heals by fetching imports network trust and a mutable
remote into the arm path, and converts an integrity signal into a silent
retry. **Adopt verbatim, as an explicit non-goal in the contract doc.**

---

## D11 — Placement · **CONCEDED to terra, and refined with evidence terra pointed me to**

I proposed a 3-line seam in `scripts/generate_arm_readiness.py:92-96`. Terra
calls a CLI-only hook **bypassable** and puts the gate directly in
`generate_arm_receipt` (`joulewise/arm_readiness.py:6099-6122`), noting the
CLI `arm` branch is "merely a wrapper" (`scripts/generate_arm_readiness.py:108-113`).

**Terra is right and I concede fully.** My defence was that the CLI is the only
production caller and that touching `arm_readiness.py` is costly. The first
half is an argument about *convention*, and this entire kernel row exists
because a check that should have happened wasn't wired. A gate that a future
caller can route around is not a gate. Verified: `generate_arm_receipt` and
`generate_freeze_receipt` have exactly one production caller today
(`scripts/generate_arm_readiness.py:97`, `:109`) — which is precisely why the
next caller is the dangerous one.

The second half — my §3d cost argument — **dissolves on evidence I found while
checking terra's citation.** I had claimed an in-library gate would force a new
`READINESS_REASON_CODES` member and pay a four-way pin (`:192-201`, `:202-211`,
the 47-cardinality assert, and `_derive_reason_code_coverage`,
`joulewise/arm_readiness_evidence.py:1394-1440`). Wrong: `arm_readiness.py`
**already hosts two second vocabularies** that are deliberately outside
`READINESS_REASON_CODES` —

- `EvidenceLifecycleError` (`joulewise/arm_readiness.py:962-988`) — registry-
  sourced code/type plus a `.refusal()` method;
- `LaunchLineageError` (`joulewise/arm_readiness.py:991-998`) — its own
  `LAUNCH_LINEAGE_REASON_CODES` frozenset with the identical unregistered-code
  guard as `ArmReadinessError:946-947`.

`LaunchLineageError` is a line-for-line template for
`HistoricalSemanticsError`. So terra's placement costs **zero** reason-code
price: no 47→48 bump, no coverage-receipt perturbation. My objection is
withdrawn.

**The refinement terra owes, from the same document it cited.**
`MAGISTRATE-RULING.md:135-137` (item 1, ruled this session) records exactly the
defect terra's placement would otherwise reproduce: *"B2 fail-ugly (terra
EXECUTED the escape): `_freeze_evidence_for_arm` propagates
EvidenceLifecycleError uncaught from generate_arm_receipt (:6139). Add the
catch mirroring :4613."* A bare `HistoricalSemanticsError` escaping
`generate_arm_receipt` is the same fail-ugly, freshly ruled against.

**Therefore:** gate inside the library at `joulewise/arm_readiness.py:6108`
(after `root = Path(pack_root).resolve(strict=True)` at `:6106`, before
`_pack_record(root)` at `:6108`) — terra's ordering, exactly right — and
**catch it at that boundary**, converting to a governed refusal in the
`:4616` idiom. Keep the CLI's own `except` arm (`scripts/generate_arm_readiness.py:120`)
so the operator-facing envelope and exit-2 discipline are preserved.

---

## D12 — Gate `freeze`, not only `arm` · **DISPUTED (terra lacks it; I hold — MAJOR)**

Terra's hook is inside `generate_arm_receipt` only. `generate_freeze_receipt`
(`joulewise/arm_readiness.py:5411`) is ungated — and it is the mint that
passes `pack_sha256=None, head_commit=None` (`:5507-5528`), i.e. **the
function whose omission is C1 itself**.

Consequence: the compelled `_v4` re-freeze (`RUN_STATE.md:41-45`) — the very
next readiness event — runs through the one path terra leaves unchecked. A
verifier that attests the archive but does not gate the next mint has the
priorities backwards.

At freeze time the successor pack has no receipts yet, so the gate must verify
the **predecessor** pack and any already-authored receipts, not demand
receipts that cannot exist. **Gate both entry points, with freeze in
predecessor mode.**

---

## D13 — Vocabulary · **AGREED on namespace; CONCEDED on one name**

Both seats independently chose `histsem_*` and both keep it disjoint from
`READINESS_REASON_CODES`. Agreed, and now cheaply enforceable via the
`LaunchLineageError` pattern (D11).

**Conceded:** my `histsem_pack_digest_mismatch` is a bad name — it collides
conceptually with the existing `readiness_pack_digest_mismatch`
(`arm_readiness.py:131`, raised `:2666`), which means *disk-vs-git at HEAD*,
an entirely different proposition. Terra's `histsem_historical_digest_mismatch`
is unambiguous. **Adopt terra's spelling.**

---

## D14 — Regression shape · **DISPUTED on the control (I hold); terra's two additions CONCEDED**

Terra's defect case rewrites `head_commit` + `pack_sha256`, coherently repairs
the chain, expects `histsem_historical_digest_mismatch`, and adds a second
case expecting pin mismatch — guarding, in its words, against "a test that
passes merely because an inner hash broke."

Terra is reaching for the right worry from the negative side. It is not
sufficient. The C-028 defect-shaped standard requires proving **the gap was
real**, which means asserting the *pre-existing* machinery **accepts** the
tampered state:

```
committed_pack_tree_sha256(pack)                  # succeeds: disk == HEAD
_authenticate_generic_evidence_item(item, pack, pack)   # returns, does NOT raise
    # called exactly as frozen PACK evidence is called — WITHOUT
    # expected_pack_sha256 (arm_readiness.py:5253-5264, :5383-5392)
```

Without that control the test proves a new check fires; it does not reproduce
C1 (`sol-refuter2-report.md:108-110`). **Hold — this is the single most
important regression requirement in either design.**

**Conceded from terra, both adopted:**
- its coherence guard, as an independent positive assertion that the tampered
  chain is internally consistent (complementary to the control, not a
  substitute);
- **its library-level ordering test** — "histsem refusal occurs before an arm
  receipt/custody artifact is created." My T10 tested the CLI's no-write
  invariant (`scripts/generate_arm_readiness.py:92-95,121-125`); terra's tests
  the *library* ordering, which is the property that actually matters now that
  the gate has moved in-library (D11). Genuine catch.

---

## D15 — Pinset · **CONCEDED on location and content; DISPUTED on enforcement**

**Location — conceded to terra:** `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
over my `scripts/receipt_histsem/pinset_v1.json`. `configs/arm_readiness/`
already holds the governed row registry (`d117_row_registry_v1.json`,
referenced by every freeze receipt's `row_registry` block); a governance pin
belongs beside it, not in `scripts/`.

**Content — merge.** Terra's 99 pinned receipt SHAs (transitively pinning
every `head_commit`/`pack_sha256`) are better than my summary rows; my
`historical_pack_sha256`, `head_commit`, and `post_authoring_delta` remain
useful as *explicit* values so the pinset is readable by a human reviewer
rather than only by the verifier. Take both.

**Enforcement — I hold.** Terra says "pinset changes require a new versioned
governed artifact; no auto-reseal" and supplies no mechanism. A prose rule
about a JSON file is exactly the kind of should-that-nobody-wired this row
exists to fix. **Pin the pinset's own sha256 as a literal in
`tests/test_receipt_histsem.py`**, the idiom already in force at
`tests/test_powermetrics_fiducial.py:1556-1559` for the r6 acceptance artifact
(`0227bca3…`). That makes any pinset edit turn a test red and surface in
review — a data change becomes a code change. Agreed with terra that there
must be **no `--update` flag**.

---

## D16 — Contract doc · **CONCEDED**

Terra's WRITE_SCOPE includes `docs/contracts/receipt_histsem_verifier.md`;
mine had none. Terra is right — `CLAUDE.md` mandates a ONE home for wire
policy, `docs/contracts/` holds the other 18, and a governed verifier with a
refusal vocabulary, two invocation lanes, and a pinset needs one. **Adopt.**

---

## D17 — The archival `_v3` location rule · **CONCEDED (terra caught what I missed)**

Terra's scope boundary cites `MAGISTRATE-RULING.md:138-141`: `_v3` replays
**only** at the pre-install commit checked out at
`/Users/edr/JouleWise-measurement-20260818` (absolute `pack_root` pin), and
**a location refusal is not pack corruption**. Verified, and it explains an
artifact I observed but did not interpret — `freeze-0003.json`'s
`pack_identity.pack_root` is that absolute measurement-checkout path, not the
main repo.

My design missed this entirely, and the omission is dangerous: a verifier run
in the main repo (as CI must) could read the absolute-path pin as a mismatch
and refuse all three `_v3` packs, or worse, an implementer could add a
`pack_root` equality check and turn a ruled non-defect into a red gate.
**The contract doc must state that this verifier is location-agnostic by
design: it never compares `pack_identity.pack_root` to its own cwd, and a
location mismatch is out of its scope.** Good catch by terra.

---

## D18 — `_v4` sequencing · **DISPUTED (terra lacks it; I hold — and it is now stronger)**

Terra's stages end at "lead-owned kernel/queue/run-report closeout," with no
coupling to the `_v4` transaction. My design requires minting the `_v4` pinset
row **inside `_v4`'s S5**, because retrofitting an expected value afterwards
reproduces C1's exact shape — an expected value nobody supplied.

That argument is now sharper than when I wrote it, from the same ruling
document terra cited. `MAGISTRATE-RULING.md` item 3: *"Standing price (Opus):
post-`_v4`, every registry edit forces a `_v5` family — the registry becomes a
frozen artifact; get all sites right in one pass."* So the sequencing is not a
preference:

1. Land this verifier and its vocabulary **before** the `_v4` re-freeze.
2. Mint the `_v4` pinset row inside `_v4`'s S5, checked against `_v4`'s
   confirmation table the way the `_v3` rows check against
   `ed-s5-mint-decision-2026-08-19.md:82-84`.
3. Anything deferred past `_v4` costs a `_v5` family.

**This belongs in the ruling as a scheduling constraint on the `_v4`
transaction, not merely as a stage of this row.**

---

## D19 — CI specificity · **DISPUTED (terra under-specified; I hold)**

Terra: "add one early step to `.github/workflows/ci.yml`, whose test job
already uses `fetch-depth: 0` (`:17-28`)." Correct as far as it goes. Two
things it must say:

- **Name the job.** Job `test` (`.github/workflows/ci.yml:9`), step inserted
  after `gen_state.py --check` (`:25-26`).
- **Name the hazard.** Job `build` (`:157-173`) checks out **shallow** — its
  `actions/checkout@v5` at `:160` has no `with:` block. A verifier added there
  refuses `histsem_history_shallow` on every run. Given D9's split this
  produces a clean, self-explaining failure rather than a mystery, but it
  should simply not be wired there.
- Job `test` is an 8-way matrix (`:12-15`); the verifier is seconds
  (9 packs, ~1000 `cat-file` calls), so full-matrix is acceptable.

---

## D20 — `scripts/test_timings.json` · **AGREED (terra, trivial)**

Verified: `scripts/shard_tests.py:3-6` — discovery is always from the current
`tests/` tree and an unmeasured module gets the median weight. No timings entry
needed for the new test module. Minor, correct, adopted.

---

## Scoreboard

| item | verdict |
|---|---|
| D1 primitive (mechanics) | **AGREED** — independent convergence |
| D1 primitive (location) | **CONCEDED** to terra |
| D2 K7 priority claim | **CONCEDED** — I withdraw my own headline; K7 retained, demoted |
| D3 fact-source hashes mandatory | **CONCEDED** to terra |
| D4 pre-authoring invariant | **DISPUTED** — I hold |
| D5 ancestry + origin/main split | **DISPUTED** — I hold (reduced weight) |
| D6 predecessor binding | **DISPUTED** — I hold |
| D7 differential self-test | **DISPUTED** — I hold (MAJOR) |
| D8 two-coordinate rule | **DISPUTED** — I hold (terra ambiguous) |
| D9 refusal granularity | **DISPUTED** — I hold |
| D10 no fetch/repair | **CONCEDED** to terra |
| D11 placement in-library | **CONCEDED** to terra + fail-ugly refinement |
| D12 gate `freeze` too | **DISPUTED** — I hold (MAJOR) |
| D13 `histsem_*` namespace | **AGREED**; name **CONCEDED** to terra |
| D14 control half of regression | **DISPUTED** — I hold (MAJOR); 2 terra additions **CONCEDED** |
| D15 pinset location/content | **CONCEDED**; byte-pin enforcement **DISPUTED**, I hold |
| D16 contract doc | **CONCEDED** to terra |
| D17 archival location rule | **CONCEDED** — terra caught, I missed |
| D18 `_v4` sequencing | **DISPUTED** — I hold (strengthened) |
| D19 CI job/shallow hazard | **DISPUTED** — I hold |
| D20 test_timings | **AGREED** |

Conceded to terra: 8. Held: 11. Agreed: 3. No item is left unresolved for the
magistrate to break a tie on except by choosing to overrule a held position.

---

## Consolidated magistrate ruling list

**Mechanism**

1. `historical_pack_tree_sha256(repository, pack_path, head_commit)` lands in
   `joulewise/arm_readiness.py` beside `committed_pack_tree_sha256` (`:2553`).
   *(terra)*
2. Mandatory anti-drift pin: `historical(..., "HEAD") == committed_pack_tree_sha256(root)`
   over all 9 packs. *(Opus — no counterpart in terra)*
3. Two coordinates, stated explicitly: `pack_sha256` and the pre-authoring
   invariant are HISTORICAL; sidecar → freeze → plan binding is CURRENT
   (HEAD), because `plan_tree.json` differs between them in 9/9 packs.
   *(Opus)*

**Checks** — terra items 1–5, plus: pre-authoring invariant (D4), ancestry
with the CI-hard / pre-arm-advisory `origin/main` split (D5), predecessor
binding (D6), K7 as a code-level structural rule at reduced rank (D2), and
`facts[].source_sha256` promoted to mandatory (D3).

**Vocabulary**

4. `HistoricalSemanticsError` + `HISTSEM_REASON_CODES`, modelled line-for-line
   on `LaunchLineageError` (`joulewise/arm_readiness.py:991-998`); disjoint
   from `READINESS_REASON_CODES`, asserted by test. Zero reason-code price.
5. Granular unavailability codes, not one bucket (D9). Terra's
   `histsem_historical_digest_mismatch` spelling adopted.
6. No fetch, no history repair, in any lane. *(terra)*

**Placement**

7. Gate **inside the library** at `joulewise/arm_readiness.py:6108` (after
   `:6106`, before `_pack_record` at `:6108`). *(terra)*
8. Gate `generate_freeze_receipt` (`:5411`) as well, in predecessor mode —
   it is the function whose `None`/`None` omission *is* C1. *(Opus)*
9. Catch at both boundaries in the `:4616` idiom; a bare escape reproduces the
   B2 fail-ugly ruled at `MAGISTRATE-RULING.md:135-137`. Retain the CLI
   `except` arm for the operator envelope and exit-2.
10. CI: job `test` only, after `.github/workflows/ci.yml:25-26`; never job
    `build` (shallow at `:160`).

**Governance**

11. Pinset at `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
    *(terra location)*, carrying terra's 99 receipt SHAs **and** the explicit
    `head_commit` / `historical_pack_sha256` / delta rows *(Opus)*.
12. Pinset sha256 pinned as a literal in `tests/test_receipt_histsem.py`
    (`tests/test_powermetrics_fiducial.py:1556-1559` idiom). No `--update`.
    *(Opus enforcement, terra intent)*
13. `_v3` values checked by the lead against the published S5 table
    (`docs/process/ed-s5-mint-decision-2026-08-19.md:78-84`) — rule 1, not
    delegated.
14. `docs/contracts/receipt_histsem_verifier.md` is the ONE home. *(terra)*
15. It records the verifier as **location-agnostic**: never compares
    `pack_identity.pack_root` to cwd; a location refusal is not pack
    corruption (`MAGISTRATE-RULING.md:138-141`). *(terra)*

**Regression**

16. The defect-shaped test carries **both halves**: the control (frozen PACK
    authentication, called without `expected_pack_sha256`, **accepts** the
    coherently rewritten chain) and the new refusal. *(Opus — non-negotiable)*
17. Plus terra's coherence guard and its library-level ordering test (refusal
    before any custody artifact). *(terra)*
18. Plus off-lineage re-anchor, evidence add/remove, and the granular
    unavailable-history fixtures. *(Opus)*

**Sequencing — the item with a deadline**

19. Land the verifier and its vocabulary **before** the `_v4` re-freeze, and
    mint the `_v4` pinset row **inside `_v4`'s S5**. Basis:
    `MAGISTRATE-RULING.md` item 3 — post-`_v4`, every registry edit forces a
    `_v5` family. Retrofitting the `_v4` row afterwards reproduces C1's exact
    shape. *(Opus)*

**Scope prohibitions (both seats agree, verbatim in every stage brief):** the
four r6-pinned files — `joulewise/powermetrics_fiducial.py`,
`joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`,
`joulewise/reduce.py` (`RUN_STATE.md:95-105`) — and `configs/campaigns/**` are
out of scope in every stage.

---

## One residual disagreement worth the magistrate's attention

Terra frames the row as *integrity*; I frame it as *detectability*. Terra's
scope boundary correctly says the verifier "does not reverse D-139 A1"
(`docs/decision_log.md:10047-10058`), but its finding title — "historical
receipt semantics are not yet **mandatory** at the arm boundary" — invites the
reading that making them mandatory makes them *sound*. It does not. Under
D-139 A1 an actor with repo write access can rewrite history, re-mint the
pinset, and revise the published table. What changes is the **cost and
visibility** of forgery: C1's attack was a coherent edit of ~6 files in one
commit; afterwards it additionally requires a history rewrite that breaks
`merge-base --is-ancestor` against `origin/main` and contradicts a
hand-published digest table.

That is a detectability claim, and the paper must state it in those words. If
the ruling adopts only one sentence from this seat, adopt that one.
