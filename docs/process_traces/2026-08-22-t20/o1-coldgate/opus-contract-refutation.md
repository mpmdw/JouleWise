# O-1 — OPUS CONTRACT-LENS REFUTATION

Seat: Opus 5, contract lens, cold (no session context). Paired with a cold
Fable adjudicator ruling independently. Repo read-only @ `main` `1ba04a8`.

## 0. Bottom line

The packet's O-1 is **half right and wrongly scoped**.

- The conflict is REAL, but the packet **understates it by a factor of six**:
  appending `_v4` rows to the governed pinset breaks **five assertions across
  three tests plus a test-method name**, not "the literal SHA at
  `tests/test_receipt_histsem.py:30-31,53-60`."
- The packet's **option 1 is REFUTED**, and not on cost. Allowlisting
  `tests/test_receipt_histsem.py` mechanically trips the **V-1(vi) tamper-probe
  tripwire** and voids **V-1(iii)**, the recorded condition on which the static
  allowlist mechanism exists at all. Its consequence is not "111 → 113"; it is
  "reopen the mechanism to the V-1(vii) derived manifest and rerun all of S-0."
- The packet's **option 2 SURVIVES only in a form it does not state**. Its two
  natural instantiations (recompute-and-accept; dual SHA pin) are refuted on
  contract text and on fact respectively.
- The packet **missed the load-bearing sentence in its own annex**:
  HISTSEM-CONTRACT `docs/contracts/receipt_histsem_verifier.md:33-34` —
  *"There is no update, regenerate, repair, or auto-reseal lane; **a new
  governed value requires an explicit versioned change**."* The contract states
  the lane. The runsheet's claim at `s0-runsheet.md:450` that *"the current
  sources provide no operation satisfying both"* is **false as a reading of the
  contract**.
- The packet also missed that the changed-set window is **bounded on both
  sides**. It noticed the pre-derivation boundary (and relies on it for U11);
  it never noticed the post-arm boundary, which is where the byte-pin update
  belongs.

**Superior option missed: O-1-D — VERSIONED-SUCCESSOR PINSET WITH POST-WINDOW
FIXATION.** It keeps 112 exactly, amends no ruled value, trips no tripwire,
weakens no existing pin, and is authorised by the histsem contract's own words.
Full construction in §5.

Ranking: **O-1-D ≻ O-1-E ≻ packet-option-2(amended) ≻ packet-option-1 ≈
packet-option-3.**

---

## 1. The mechanism of record (what the gate actually is)

Before adjudicating, the object under dispute must be named correctly. The
packet never states it, and the two things it conflates have different
semantics.

### 1.1 The runtime gate is SUBTRACTION over a bounded window

`joulewise/arm_readiness.py:3916-3964` (`_r1_changed_paths`) enumerates the
window:

```python
raw = _run_git(repository, "diff", "--name-only", "-z",
               f"{derivation_commit}..{current_head}", "--")
```

and `:4041-4049` applies it:

```python
allowlist = set(governed["irrelevant_path_allowlist"])
relevant = sorted(set(changed_paths) - allowlist)
if relevant:
    raise EvidenceLifecycleError(governed, "DEPENDENCY_CHANGED_SET", ...)
```

Three properties follow, all of them dispositive and none of them in the
packet:

- **(P1) The gate is set subtraction, not exact match.** An *unused* allowlist
  entry does not refuse. Exactness ("missing/extra/unused") is enforced only by
  the custody-only S-0 checker (`s0-runsheet.md:172-253`, §4(d) at `:621-645`),
  which is a transaction proof artifact, not the runtime control.
- **(P2) `derivation_commit` is read from the receipt** (`:4038`,
  `str(validated_receipt["derivation_commit"])`) and `current_head` is the head
  at which the arm runs. The window is therefore
  `EVIDENCE_DERIVATION_HEAD .. (head at arm time)`. Confirmed by the runsheet's
  own final check, `s0-runsheet.md:497`:
  `--derivation "$EVIDENCE_DERIVATION_HEAD" --head "$FINAL_HEAD"`.
- **(P3) The registry that carries the allowlist does not exist at HEAD.**
  `configs/arm_readiness/d117_row_registry_v1.json` at `1ba04a8` has top-level
  keys `['plan_profiles','registry_id','rows','schema_version']` — no
  `freeze_evidence_lifecycle`, no `irrelevant_path_allowlist`. The value the
  runsheet reads at `s0-runsheet.md:628` is a **forward reference to an
  unauthored key**. The 112 list is therefore authored **pre-derivation, inside
  the reviewed candidate**. Registry validation
  (`arm_readiness.py:1567-1583`) checks only sorted-unique-canonical paths — it
  never checks that entries are used.

### 1.2 The window is bounded on BOTH sides

The runsheet already exploits the *lower* boundary and says so, `s0-runsheet.md:329`:

> "Those paths are before `EVIDENCE_DERIVATION_HEAD`, so they are correctly
> absent from the 112."

By (P2) the *upper* boundary is equally hard: a commit made after the final arm
appears in no window that any gate in this transaction evaluates. The 112
contract is **a property of one derivation→arm window, not a standing
repository invariant**. The runsheet's O-1 statement treats "creates path 113"
as if any commit ever touching a non-allowlisted path breaks the contract. It
does not. This is the single largest analytic gap in the packet.

(The only downstream cost of a post-window commit is that a *future re-arm from
the same receipt* would see it. That is true of every subsequent commit to the
repository — a README edit has the identical effect — so it is the ordinary,
intended expiry of R1 evidence, not a new cost.)

---

## 2. Is the conflict REAL? — four findings

### F1 — REAL, but the packet understates the breakage sixfold. (Correction, not refutation.)

The runsheet cites `tests/test_receipt_histsem.py:30-31,53-60` and speaks of "a
one-time reviewed literal update." Appending three `_v4` rows to
`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json` breaks **all** of:

| Line | Assertion | Why it breaks |
|---|---|---|
| `:31`,`:55` | `PINSET_SHA256 = "d81515…"` / `assertEqual(sha256(PINSET.read_bytes()), PINSET_SHA256)` | bytes change |
| `:59` | `assertEqual(len(value["packs"]), 9)` | 9 → 12 |
| `:60` | `assertEqual(sum(row["receipt_count"] …), 99)` | 99 → 99 + n |
| `:82` | `def test_differential_self_test_all_nine_packs` | method **name** is false at 12 packs; body iterates the new rows |
| `:95` | `assertEqual(result["pack_count"], 9)` | 9 → 12 |
| `:96` | `assertEqual(result["receipt_count"], 99)` | grows |
| `:103` | `assertEqual(fact_count, 108)` | grows |

Additionally `:93` runs `verify_all_receipt_histsem(ROOT, require_published=True)`.
Under option 1 the new rows' `head_commit` must be an ancestor of
`origin/main` **inside the window** — and the runsheet forges that ref at
`s0-runsheet.md:325`:

```
git update-ref refs/remotes/origin/main "$EVIDENCE_DERIVATION_HEAD"
```

So option 1 makes the normative corpus test pass in-window *only because the
runsheet locally forged `origin/main`*. That is an ugly dependency to introduce
into the one transaction whose whole purpose is contemporaneous custody of
expected values. It is a consequence the packet does not disclose.

**Bearing:** the packet's option 1 is not "one reviewed literal." It is a
seven-site rewrite of the normative test — inside the transaction window, on
the file that authenticates the file being minted. This materially changes the
review burden and the precedent.

### F2 — The packet conflates the runtime allowlist with the S-0 candidate contract

"112 vs 113" is stated as one number. It is two objects:

1. the **runtime registry value** `irrelevant_path_allowlist` — subtraction
   semantics (P1), authored pre-derivation (P3); and
2. the **S-0 candidate contract** — exact 112, failing on missing/extra/unused
   (`s0-runsheet.md:621-645`, `rh-ruling.md:77-78`: *"the 112-entry candidate
   contract still fails on missing/extra/unused"*).

RH-8's *"the allowlist value goes 111 → 112"* amends (1). The exactness
requirement binds (2). They can be satisfied by different means, and no ruled
sentence requires that a path appear in (1) merely because it changed — only
that every changed path be subtracted by (1) **or not be in the window at all**.
This is the seam the runsheet did not see.

### F3 — The conflict is an ARTIFACT of an unstated premise

The runsheet's O-1 rests on an assumption it never states and never sources:
**that the three `_v4` rows must be appended to
`legacy_receipt_histsem_pinset_v1.json`.**

Check every binding sentence:

- `rh-ruling.md:70-73`: *"the allowlist value goes 111 → 112, adding **the
  pinset's exact path** (pack-and-ordinal-exact per V-1(v); `_v5` gets its own
  entry, never a glob)."* — "the pinset's exact path." It does not say v1.
  "Pack-and-ordinal-exact" per V-1(v) means *name the literal artifact, do not
  glob*; it does not fix which artifact.
- `receipt_histsem_verifier.md:120-123`: *"The pinset path is the
  pack-and-ordinal-exact 112th entry in the whole-repository changed-set
  allowlist… a later family gets its own exact entry, never a glob."* — Same.
  Indeed *"a later family gets its own exact entry"* reads **toward**
  per-family artifacts, not against them.
- `receipt_histsem_verifier.md:33-34`: *"There is no update, regenerate,
  repair, or auto-reseal lane; **a new governed value requires an explicit
  versioned change.**"*

That last sentence is the packet's own annex and it is decisive. Under the
runsheet's implicit reading — "versioned change" = "a reviewed edit to the
literal" — the sentence **contradicts its own first clause**: an edit to the
governed value *is* an update lane, differing from the forbidden one only by
being manual. Under the reading that gives both clauses effect, "versioned
change" means what the filename says it means: the governed artifact is
`…_pinset_**v1**.json`, and a new governed value arrives as a new versioned
artifact. The interpretation that leaves no sentence inoperative wins.

The only text that cuts the other way is
`receipt_histsem_verifier.md:15-17` — *"The governed pinset is
`configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`"* (singular).
That is a real obstacle and I do not paper over it: O-1-D **does** amend that
sentence. But it amends it **pre-derivation**, in the same reviewed candidate
in which RH-8 already requires contract work to land
(`rh-ruling.md:66-67`: *"this verifier LANDS BEFORE the `_v4` re-freeze"*) —
not mid-transaction, where the ruling's own retrofit prohibition lives.

**So: the conflict is real given the append premise, and dissolves without it.
The premise is the runsheet's, not the rulings'.**

### F4 — The ruling already assigns new-row validation to something other than the byte pin

`rh-ruling.md:22-26`, item 2:

> "K7 (the delta-shape envelope…) is LAYERED HARDENING and the `_v4`
> pinset-row **BOOTSTRAP validator (the only check that can validate a new
> pinset rather than consume one)**."

Restated in the contract at `receipt_histsem_verifier.md:50-52`: *"K7 is …the
bootstrap check used when a new pinset row is minted."*

The byte pin's job is therefore **fixation of already-validated bytes**, not
validation of new ones. New rows are validated by K7 bootstrap + the
transaction confirmation table (`receipt_histsem_verifier.md:118-119`) + Ed's
exact-byte step 6 (`rh-ruling.md:67-68`). Nothing in the ruled design requires
the byte pin and the mint to occur in the same commit — and, as §3.1 shows,
requiring it is precisely what destroys the pin.

---

## 3. Option-by-option contract accounting

### Option 1 — explicit 113-path amendment including `tests/test_receipt_histsem.py`

**Verdict: REFUTED.**

**(a) Sentences violated, amended, or silently weakened**

*Amended (disclosed):*
- `rh-ruling.md:70-71` "the allowlist value goes 111 → 112" → 113. A cold-pass
  ruled value, re-amended mid-transaction.
- `receipt_histsem_verifier.md:120` "the pack-and-ordinal-exact **112th** entry".

*Violated (undisclosed by the packet):*
- **V-1(vi)** (`rulings-r5-consolidation.md:101-106`): *"S-0 executes a
  PER-CLASS TAMPER PROBE over every allowlisted path class, proving refusal
  through manifest/authentication/replay for each; **any class with no
  authenticator moves to digest-conditional subtraction**, and any probe
  failure REOPENS the mechanism question to the derived manifest (the
  tripwire)."*
  A test-source path has **no** manifest binding, **no** sidecar digest, and
  **no** semantic-replay authenticator. V-1(iv) already records which classes
  lack R1 binding and names the arm-time replay gate as the load-bearing
  substitute for those four; there is no analogue for a test file. A tampered
  test file *is* the tamper — it can be edited to assert whatever the tamperer
  needs.
  Runsheet §4(e) `s0-runsheet.md:725` states the consequence: *"If any class has
  no such authenticator, apply V-1.vi's digest-conditional subtraction rule: it
  may not remain a static allowlist subtraction; remove that class from the
  candidate allowlist and bind it in the authenticated derived manifest, then
  reopen the mechanism proof."*
  And `s0-runsheet.md:830` classes it as a **mechanism failure**: *"any one of
  the eight allowlisted classes lacks an independent tamper authenticator… The
  response is not 'fix a test expectation': derive an authenticated manifest,
  remove every unauthenticated subtraction, **rerun all of S-0**."*
- **V-1(iii)** (`rulings-r5-consolidation.md:90-93`): *"Sol conceded back to the
  static list **CONDITIONAL on independent authentication of all allowed
  bytes**."* Option 1 adds a path whose bytes have no independent
  authentication. **The condition fails, so the concession that made the static
  111/112 list legitimate is void**, and V-1(vii)'s derived,
  digest-authenticated manifest — the standing dissent — becomes the correct
  mechanism. Option 1 does not cost an amendment; it retroactively removes the
  basis of the mechanism it is amending.
- `receipt_histsem_verifier.md:33` *"There is no update, regenerate, repair, or
  auto-reseal lane."* A "one-time reviewed literal update" is an update lane
  operated by hand. And it renders `:34`'s versioned-change sentence
  inoperative (F3).

**(b) Tamper-evidence consequence — this is the refutation proper**

A byte pin authenticates **only** if changing the pinned bytes requires an act
the same actor cannot perform in the same breath. Its value comes entirely from
(i) the pin being older than the bytes' next change, and (ii) updating it being
a separate, separately-reviewed act.

Option 1 allowlists **both the pinset and the file that pins it, in the same
window, under the same subtraction**. During that window:

> a coherent in-window substitution — alter the committed `_v4` rows **and**
> alter `PINSET_SHA256` to match — is refused by **no** gate in the
> transaction. The changed set is `{pinset, test}`; both are subtracted; the
> test passes because it was rewritten to pass.

That is exactly the coherent-tamper class the whole verifier exists to defeat,
demonstrated by `tests/test_receipt_histsem.py:196-277`
(`test_coherent_legacy_tamper_control_accepts_but_histsem_refuses`). Option 1
opens it, by construction, for the one window in which the governed values are
minted — the window whose contemporaneity RH-8 is specifically protecting.

Whose bytes stop being pinned: **the nine existing rows as well as the three
new ones**, because after the update the literal covers a 12-row file and no
committed artifact any longer attests the 9-row value. The `_v3` custody
history's fixation is silently rolled forward.

**Restated: option 1 is option 3 with better paperwork.** A pin updated in the
same commit as the bytes it pins pins nothing during that commit. It is a
waiver of the byte pin for the mint window, presented as an amendment.

**(c) Precedent cost**

Three licences, each citable:
1. *"A normative byte pin may be updated in-band when the pin becomes
   inconvenient."* Retires "no update lane" as a real constraint.
2. *"The file holding a pin may be allowlisted alongside the file it pins."*
   The general form authorises allowlisting any authenticator next to its
   subject.
3. *"V-1(vi) can be satisfied by declaring a class 'reviewed' rather than
   'authenticated'."* Dissolves the tripwire that is the static list's only
   safety.
Plus the mechanical growth path: `_v5` cites this at 114, `_v6` at 115, each
carrying its own test-file entry — which is precisely the glob-by-accretion
that V-1(v) and `receipt_histsem_verifier.md:122-123` forbid in spirit.

### Option 2 — pre-derivation "stable authentication construction"

**Verdict: SURVIVES only in the amended form of §5. As stated, under-specified;
its two natural instantiations are refuted.**

- **2a, recompute-and-accept** (test derives acceptable successor bytes from
  repo state): **REFUTED on text and on soundness.** On text, it is verbatim
  the *"regenerate… or auto-reseal lane"* forbidden at
  `receipt_histsem_verifier.md:33`. On soundness, a check that accepts whatever
  it can recompute from HEAD is self-sealing: a coherent in-repo tamperer who
  changes pack and pinset together passes it. That is the C1 shape the ruling
  was written against (`rh-ruling.md:36-38`: *"a gate a future caller can route
  around is not a gate; C1 exists because a check was not wired"*).
- **2b, dual pin (current bytes + declared successor SHA):** **REFUTED on
  fact.** The successor SHA is unknowable pre-derivation. Verified against the
  live artifact: each row carries `current_pack_sha256`, `head_commit`,
  `freeze_receipt`, `plan_tree_sha256`, `published_anchor` — every one of which
  is minted after `EVIDENCE_DERIVATION_HEAD`. The runsheet is correct here
  (`s0-runsheet.md:840`) and the packet's parenthetical hope for a dual-pin
  construction is closed.
- **2c, expected-successor SHAPE pin** (pin v1 bytes exactly; assert successor
  rows conform to a schema): **PARTIAL WAIVER MISLABELLED AS A REDESIGN.** It
  preserves shape but abandons *"Its bytes are SHA-256-pinned"*
  (`receipt_histsem_verifier.md:32-33`) for exactly the rows that matter. If
  anyone proposes it, it must be adjudicated as option 3, not option 2.

What survives of option 2 is its **structural insight** — that the cure belongs
before derivation, where amendments are cheap and reviewable — and that
insight is correct. §5 supplies the construction the packet could not name.

### Option 3 — waive the `_v4` rows or the byte pin

**Verdict: REFUTED, as the packet says. One correction to the record.**

The packet says "each contradicts a binding RH obligation" and stops. For the
cold pair's benefit, the waivers are **not** equally bad, and this matters
because option 1 is covertly one of them:

- Waiving RH-8's contemporaneous mint is the **worst**: it reproduces C1
  directly (`rh-ruling.md:68-69`, *"an expected value nobody supplied"*).
- Waiving the byte pin over the **nine existing rows** is next: it discards
  fixation already achieved over artifacts with live custody history.
- Waiving *in-window CI byte-pin coverage of never-yet-pinned new rows*, where
  those bytes are covered by K7 bootstrap, the transaction confirmation table,
  and Ed's hand-published exact-byte table, is a **bounded, differently-shaped
  residual** — and it is what O-1-D's fixation gap actually is (§5, C1).
  Naming it honestly is better than option 1, which incurs the second kind
  without saying so.

---

## 4. Ranking under the contract lens

| Rank | Option | Verdict | One-line reason |
|---|---|---|---|
| 1 | **O-1-D** (new; §5) | **SURVIVES** | 112 untouched; no ruled value amended; V-1(vi)/(iii) intact; v1's pin never stale; authorised by `receipt_histsem_verifier.md:34`. |
| 2 | **O-1-E** (new; §5.3) | **SURVIVES with a named cost** | Cheapest; no contract or code delta; but leaves one red intermediate commit and makes the *existing* nine rows' pin stale for that commit. |
| 3 | Packet option 2 | **SURVIVES only as amended** | Right instinct (pre-derivation), no stated construction; 2a/2b/2c all refuted. |
| 4 | Packet option 1 | **REFUTED** | Trips V-1(vi), voids V-1(iii), and admits coherent in-window pinset substitution — the exact attack the verifier exists to detect. |
| 5 | Packet option 3 | **REFUTED** | As the packet says; see §3 for the correct ordering among waivers. |

The packet's recommendation — "option 2 if a design exists, otherwise the
narrow explicit 113-path amendment" — has the fallback **backwards**. Option 1
is not the safe default; it is the option whose stated consequence
(`s0-runsheet.md:725`, `:830`) is *rerun all of S-0 under the derived manifest*.

---

## 5. The option the packet missed

### 5.1 O-1-D — VERSIONED-SUCCESSOR PINSET, POST-WINDOW FIXATION (primary)

**Pre-derivation**, inside the reviewed candidate — where RH-8 already places
the verifier (`rh-ruling.md:66-67`) and where the allowlist registry must be
authored anyway (P3):

1. Amend `receipt_histsem_verifier.md:15-17` from a single governed pinset to a
   **closed, ordered, enumerated chain** of versioned pinset artifacts;
   membership is the union of their rows; the chain members are named in code.
2. Land the library's chain-read with regression tests. In-window the successor
   file does not exist, so the union is exactly v1 and **every existing
   normative assertion holds unchanged at every in-window commit**: `d81515…`,
   9 packs, 99 receipts, 108 facts, `pack_count == 9`. `tests/test_receipt_histsem.py`
   never enters the window.
3. Set the allowlist to **112**, the 112th entry being the successor pinset's
   exact path (e.g. `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json`)
   — pack-and-ordinal exact per V-1(v), no glob.

**In-window**, after freeze-0004 ×3 and before Ed's exact-byte step 6: mint the
three rows into the successor artifact, check them against the transaction's
confirmation table (`receipt_histsem_verifier.md:118-119`), commit. Exactly one
changed path, the allowlisted 112th. RH-8 satisfied verbatim: rows minted after
the freezes, before step 6, no retrofit.

**Post-window**, a separate commit and PR after the final arm, when no
changed-set window is open (§1.2): add the successor's SHA literal and its
row/receipt/fact counts to `tests/test_receipt_histsem.py`, asserting the exact
bytes Ed already confirmed at step 6.

**Contract accounting — what it does NOT do:**
- Does not amend the ruled 112 (RH-8's amendment is respected, not re-amended).
- Does not add an unauthenticated allowlist subtraction → V-1(vi) tripwire not
  tripped; V-1(iii)'s condition holds; the static list keeps its basis.
- Does not update, regenerate, repair, or reseal v1 → `:33` survives literally,
  and `:34` is given operative effect.
- Never lets a pin and the bytes it pins change in the same window.
- Never makes the nine existing rows' pin stale, for any interval.
- Preserves V-1(v) exactness and `:122-123`'s per-family entry rule — indeed
  it is the natural implementation of *"a later family gets its own exact
  entry."*

**Costs, stated honestly:**
- **C1 — fixation gap.** Between the transaction commit and the post-window pin
  commit, the successor's bytes are attested by K7 bootstrap, the transaction
  confirmation table, and Ed's hand-published exact-byte table — but not yet by
  a CI byte pin. Bounded to one commit; and covered by the control the contract
  already leans on (`receipt_histsem_verifier.md:130-132`: detection is
  "contradicts the hand-published S5 digest table"). This is a **real residual
  and should be recorded as one**, not glossed.
- **C2 — a genuine pre-derivation contract delta** to `:15-17` and `:115-123`,
  requiring its own cold review. Cheaper than option 1's mid-transaction
  amendment, but not free.
- **C3 — absent-successor hole.** Deleting the successor would disengage `_v4`
  governance under the current absent-at-HEAD rule (`:36`, *"an
  absence-of-governance answer"*). Mitigation: because the chain is **closed
  and enumerated in code**, an absent *enumerated* member must **refuse**, not
  return ordinary readiness. **This is a tightening of a rule the rule-11
  consult specifically settled** (`receipt_histsem_verifier.md:6-11`), so it
  requires the cold pair's explicit blessing rather than an implementer's
  judgement. Flagged, not assumed.

### 5.2 Why O-1-D beats option 1 in one sentence

Option 1 buys a shorter fixation gap by allowlisting the authenticator next to
its subject — which does not shorten the gap at all, it removes the
authenticator for the duration; O-1-D keeps the authenticator outside the
window on both sides and pays a named, bounded, separately-controlled residual.

### 5.3 O-1-E — DEFER-ONLY (fallback, if C2/C3 are judged too heavy)

Append the rows to **v1** in-window (v1's path is already the ruled 112th
entry, so *nothing about the allowlist changes*), and move the entire test
update — all seven sites in F1 — to a post-window commit.

- Keeps 112 exactly. No contract amendment. No library change. No new file.
- Trips no V-1(vi) tripwire: `tests/test_receipt_histsem.py` is never
  allowlisted.
- Cost: the arm commit carries a **failing normative test** for one commit
  (push the pair together so the tested head is never red), and the existing
  nine rows' pin is momentarily stale — i.e. it touches already-pinned bytes,
  which O-1-D does not. Also inherits the forged-`origin/main` dependency noted
  in F1.

Strictly better than option 1 (no unauthenticated subtraction, no coherent
in-window substitution path), strictly worse than O-1-D.

---

## 6. Items the cold pair must rule that the packet does not surface

1. **Does the packet's option 1 trip V-1(vi)?** If yes — and §3 argues it
   plainly does — option 1 is unavailable without first ruling the derived
   manifest question, which is a far larger decision than O-1 as framed. This
   should be answered before any ranking.
2. **Is "explicit versioned change" (`receipt_histsem_verifier.md:34`) a
   versioned artifact or a reviewed edit?** The entire O-1 space turns on it.
   Only the former reading leaves `:33` operative.
3. **May the byte-pin update land after the final arm?** Requires an explicit
   finding that RH-8's retrofit prohibition
   (`rh-ruling.md:68-69`) binds the **rows**, not their CI fixation. My reading:
   it binds the rows — the mischief named is "an expected value nobody
   supplied," and Ed supplies the value at step 6.
4. **Under O-1-D, must an absent enumerated chain member refuse?** (C3.) This
   tightens a rule the rule-11 consult settled and cannot be decided by an
   implementer.
5. **Precondition defect, independent of O-1:** the runsheet reads
   `["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]` from
   `configs/arm_readiness/d117_row_registry_v1.json` (`s0-runsheet.md:628`);
   that key does not exist at `1ba04a8` (P3). Whichever option is ruled, the
   reviewed candidate must author it, and §4(d) will `KeyError` before it
   reaches its intended gate if it does not. Per `s0-runsheet.md:832` that is an
   ordinary precondition defect, but it is unrecorded.
6. **Recommend recording, whichever option wins:** the finding that the
   changed-set contract is a property of one derivation→arm window, not a
   standing invariant (§1.2). Its absence is what generated O-1.

---

# Round 2 — reply to the cold verdict

Read: `cold-fable-verdict.md` (cold Fable seat, Option 1 precisely bounded,
112 → 113, six binding conditions). Re-verified the code sites it relies on
against `1ba04a8` (`arm_readiness.py` is byte-identical at current HEAD
`73764f0`, so every line number below holds).

## 0. Position change, stated up front

**I concede. My round-1 REFUTED verdict on Option 1 does not survive contact
with the gate call sites, and my own O-1-D fails a mechanical test I did not
run in round 1.**

Revised ranking: **Option 1 (as amended in §5) ≻ O-1-E ≻ O-1-D ≻ option 2 ≻
option 3.** O-1-D drops from first to third — below even my own fallback —
for the reason in §3(a): it cannot satisfy three in-window requirements
simultaneously, and the arithmetic is not close.

What survives from round 1 is not the verdict but four specific defects in the
cold seat's *conditions*, one of which (§5.2) would let the transaction be
declared green on a forged ref. Those are in §5, offered as amendments, not as
dissent.

## 1. The impossibility argument: conceded in full — and it does not reach O-1-D's claim, but something else does

**Conceded without reservation.** "Without a key, bytes committed before
derivation cannot authenticate bytes created during derivation" is correct, and
it is the cleanest statement of the constraint anyone in this packet has made.
I verified the premise independently in round 1 (row keys include
`current_pack_sha256`, `head_commit`, `freeze_receipt`, `plan_tree_sha256`,
`published_anchor` — all minted post-derivation) and reached the same
conclusion for options 2a/2b. The seats agree.

**The distinction, stated precisely, then withdrawn as insufficient.**

The impossibility argument targets constructions claiming *in-window
authentication from pre-committed bytes*. O-1-D never claimed that. Its claim
is a sequencing claim:

- **validation** of the new rows happens in-window by the mechanism the ruling
  already assigns to exactly this job — `rh-ruling.md:22-26`, K7 as "the `_v4`
  pinset-row BOOTSTRAP validator (the only check that can validate a new pinset
  rather than consume one)" — plus the transaction confirmation table and Ed's
  step 6;
- **fixation** (the CI byte pin) happens post-window.

So the keyless-repo-trust argument, on its own terms, does not reach O-1-D. It
refutes 2a/2b/2c, which I had also refuted.

**But the cold seat's *other* argument does reach it, and it is right.** Point 1
bullet 1 — *"the freshest, claim-bearing rows get the weakest control"* — I
deployed against the subtree pin in round 1. It applies with equal force to
O-1-D's successor file, and I did not apply it to my own construction. Compare
end-of-window states honestly:

| | new rows validated in-window by | committed pin over the new rows at end of window |
|---|---|---|
| Option 1 | K7 bootstrap + confirmation table + review | **yes** — exact literal, suite green |
| O-1-D | K7 bootstrap + confirmation table + review (**identical**) | **none** |

The in-window validation is *the same set* under both. Option 1 then adds a
committed pin; O-1-D adds nothing. **Option 1 strictly dominates O-1-D on
tamper-evidence for the three new rows.** There is no compensating advantage,
which is the test I failed to run.

The seat's third bullet also lands: deferring the pin is a retrofit of an
expected value. My round-1 answer — that the value is transcribed from Ed's
antecedent step-6 table rather than invented to match — requires that the
step-6 table actually contain the successor pinset's digest. **I cannot
substantiate that.** `s0-runsheet.md` contains no definition of step 6's table
contents (the only "exact bytes" reference is `:144`, about marker scripts),
and r4-3 is not in the packet. So my C1 rebuttal rested on an artifact I never
verified. Withdrawn. See §3(c).

## 2. The precedent argument: it extends — and needs the limiting principle neither seat stated

The seat's point 5 is correct and I had it backwards. 111 → 112 was a cold-pass
repair for an enumeration that missed a path co-travelling *by construction*
(the pinset). O-1 is the same defect one level up: 112 missed that the pinset's
byte pin co-travels with the pinset by construction. Applying the same
cold-ratified repair is conservative; inventing a pre-transaction redesign to
avoid touching a ruled number is the novelty. My F3 (versioned-artifact reading
of `receipt_histsem_verifier.md:34`) does not defeat this, because even under a
versioned successor the pin must still land somewhere — versioning relocates
the co-traveller, it does not remove it.

**Does the precedent extend to allowlisting a file that is itself an
authenticator? Yes — once, and only once, and the ruling should say so.**

The asymmetry I was groping at in round 1 is real but smaller than I claimed:

- 111 → 112 added a path that **retains** an independent authenticator outside
  the allowlist (the pinset is pinned by a test that is not allowlisted).
- 112 → 113 adds the last such authenticator **into** the allowlist. After it,
  nothing outside the allowlist authenticates anything inside it by test.

That does not make 113 wrong — the authenticators of record simply become K7
bootstrap, the confirmation table, and Ed's step 6 (§5.3), which are the same
ones O-1-D would have used. But it does make 113 a **fixed point**, and that
should be ruled explicitly, because the seat's own "recurrence" doubt otherwise
leaves an open series:

> **Limiting principle (proposed for the amendment text):** the allowlist class
> set is closed at {governed-artifact paths} ∪ {the single authenticator path
> `tests/test_receipt_histsem.py`}. A future family repeats this shape with its
> own governed-artifact entries and the *same* single authenticator path — the
> count is re-enumerated per transaction, but **no amendment may ever add a
> second authenticator path**, because there would then be nothing outside the
> allowlist authenticating the authenticator. A proposal to add one is a
> V-1(vi) tripwire event routing to the V-1(vii) derived manifest, not an
> amendment.

This converts "113 is per-transaction, not a constant" (the seat's phrasing)
from a caution into a mechanical bound.

## 3. O-1-D under stress — it fails

### (a) The gate call sites: O-1-D cannot satisfy three in-window requirements at once. **Decisive.**

`_gate_receipt_histsem` (`arm_readiness.py:3449-3508`) has exactly two early
returns and one hardcoded read:

```python
# :3467-3473   ls-tree HEAD -- RECEIPT_HISTSEM_PINSET_RELATIVE_PATH
if not pinset_entry.strip():          # :3479
    return                            # absent at HEAD -> ordinary readiness
...
if not any(row["pack_id"] == pack_root.name
           and row["pack_path"] == pack_relative
           for row in governed_rows): # :3499-3502
    return                            # membership miss -> ordinary readiness
verify_receipt_histsem_pack(pack_root, ..., _pinset_rows=governed_rows)
```

Callers: `:6258` (freeze, gates the **predecessor**) and `:6952` (arm, gates
**the pack being armed**).

Walking the three in-window states:

1. **Freeze ×3.** `:6258` gates the three `_v3` predecessors, which are
   governed by the nine existing rows. Must **PASS**. Under O-1-D the successor
   pinset is enumerated-but-not-minted. If my C3 mitigation is in force —
   *absent enumerated member must refuse* — this refuses and **freeze ×3 cannot
   run. The transaction is dead at its first step.** So refuse-on-absent must
   NOT fire here.
2. **Post-mint pinset commit.** Successor now present. Fine either way.
3. **Arm ×3** (`:6952`, runsheet §3.9). The `_v4` roots are new directories
   (`configs/campaigns/` contains no `*v4*` at HEAD). Under **Option 1** the
   rows are in the one hardcoded pinset, so membership **hits** and the `_v4`
   packs get full K5/K12/binding/inventory verification against their own
   freshly-minted rows, in-window, before Ed's step 6. Under **O-1-D without a
   chain-read**, membership **misses** at `:3499` and the `_v4` arms cross
   **ungated by histsem entirely** — a silent governance hole, and a failure of
   RH-8's "present → arms cross" clone proof for the family that matters.

So O-1-D must pick two of three:

> (i) tolerate the absent successor at freeze ×3; (ii) refuse an absent
> successor thereafter (the C3 hole); (iii) gate the `_v4` arms in-window.

(i) and (ii) together require the absent-member semantics to *change during the
transaction* — a time-dependent gate, which is the defect shape this whole
ruling exists to prevent. Option 1 gets all three free, because there is one
file whose **presence is invariant** and whose **membership grows at exactly
the right moment**. That is not a stylistic preference; it is why the
single-pinset activation model was the right design.

**This alone retires O-1-D.** I did not run it in round 1 and should have.

### (b) The code delta: I understated it. It is a redesign of the activation model, not a reviewed delta.

The cold seat's `:2712`, `:3467-3484` finding is correct and I confirmed its
scope is wider than either of us wrote. `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH`
(`:2712-2714`) is a single module constant; making it a chain touches:

1. the constant → ordered closed tuple;
2. `_gate_receipt_histsem` `:3449-3508` — loop, union, **and a new
   absent-member semantic** (which §3(a) shows cannot be consistently chosen);
3. `verify_all_receipt_histsem` `:3415` — the CI `--require-published` lane and
   `tests/test_receipt_histsem.py:93`;
4. `scripts/verify_receipt_histsem.py`'s single `--pinset` argument, whose
   absent-path refusal is **normatively tested** at `tests/test_receipt_histsem.py:62-80`
   (exit 2, `["histsem_pinset_absent"]`, canonical stdout);
5. cross-file `(pack_id, pack_path)` uniqueness — a new invalidity class;
6. plausibly a **new closed-vocabulary reason code** for an absent enumerated
   member, which means amending the normative refusal table
   (`receipt_histsem_verifier.md:82-99`) and the disjointness/constructibility
   test at `tests/test_receipt_histsem.py:146-152`;
7. the whole "Governed identity and activation" section, written around the
   singular.

And item 6 collides with the rule-11 consult recorded at
`receipt_histsem_verifier.md:6-11`, which *already* superseded the ruling's
original wording for exactly the absent-pinset case. Reopening a
cold-settled semantic days before the transaction is precisely the risk the
seat names.

**Honest answer to the question posed: this is a redesign of the verifier's
activation model, not a pre-derivation reviewed delta.** My round-1 §5 C2
("a genuine contract delta… not free") was too soft. Correction accepted.

### (c) The fixation gap: attack surface is real, and my mitigation is unverified

Interval: from the in-window pinset-mint commit to the post-window fixation
commit. What protects the successor's rows during it?

- Changed-set gate: dead after the final arm (§1.2). **No.**
- `_gate_receipt_histsem`: verifies *packs against rows*; it never verifies rows
  against anything. A coherent edit of a `_v4` row plus the corresponding pack
  bytes passes. **No.**
- Byte pin: not yet written. **No.**
- Ed's step-6 table: **unverifiable from any source in the packet or repo.**

So the attack surface during the gap is: **any actor with commit access can
rewrite `_v4` governance in one commit and nothing mechanical objects.** That is
exactly the "6-file commit" forgery cost the Truth boundary
(`receipt_histsem_verifier.md:127-133`) says the mechanism exists to raise —
i.e. O-1-D reopens, for a bounded interval, the specific threat the design
defeats, in exchange for closing a residual (the in-transaction actor) that is a
**registered limitation under D-139 A1 and was never claimed closed**.

That trade is backwards, and it is the substance of my round-1 overreach (§4).

## 4. Where my round-1 refutation overreached

Recorded plainly, so the magistrate can discount it correctly.

- **§3(b), "option 1 is option 3 with better paperwork."** Too strong. The
  claim "a pin updated in the same commit as its bytes pins nothing during that
  commit" is *true* but not *decisive*, because (i) it is equally true of the
  v1 pin at its own minting, (ii) the actor it admits is the in-transaction
  actor, already outside the threat model by
  `receipt_histsem_verifier.md:127-133` and D-139 A1, and (iii) the pin's real
  product — downstream detectability from the next commit boundary — is
  **delivered** by Option 1 and merely **delayed** by mine. The cold seat's
  "momentary self-attestation" dissent states this correctly and I did not.
- **§3(a), the V-1(vi) tripwire claim.** Half survives (see §5.3): the seat's
  nominated authenticators are circular for the *coherent* tamper. But my
  implied conclusion — that Option 1 therefore has no authenticators for the
  class — is false. K7 bootstrap, the confirmation table, and step 6 are real
  and are the same ones O-1-D relies on. The tripwire is not tripped; the
  *record of which authenticators apply* is what needs fixing.
- **§5 C1.** Rested on an unverified assumption about step 6. Withdrawn.

## 5. Four amendments to the cold seat's binding conditions

These are the round-1 findings that survive. They strengthen the ruling I now
support; none is a dissent.

### 5.1 Condition 2 is incomplete — a seventh site and a false test name

Condition 2 lists SHA literal, 9→12 packs, 99→99+n receipts, corpus fact-count.
It omits `tests/test_receipt_histsem.py:82`,
`def test_differential_self_test_all_nine_packs` — a method whose **name**
becomes false at twelve packs while its body silently iterates the new rows.
Rename it in the same commit. A normative test whose name contradicts its scope
is the prose-drifts-from-mechanism defect class this project has paid for
before.

### 5.2 Condition 2's "the full suite is green at that commit" is satisfiable only against a forged ref — **this is the material gap**

`tests/test_receipt_histsem.py:92-103` calls
`verify_all_receipt_histsem(ROOT, require_published=True)`. After the append,
the three new rows' `head_commit` must be an ancestor of `origin/main`. The
runsheet forges that ref at `s0-runsheet.md:325`:

```
git update-ref refs/remotes/origin/main "$EVIDENCE_DERIVATION_HEAD"
```

and real CI runs the same predicate at `.github/workflows/ci.yml:28`
(`verify_receipt_histsem.py --repository-root . --require-published`).

**So local green at the amending commit proves nothing about published green,
and the two cannot be distinguished by anyone reading the transcript.** Amend
condition 2 to:

> Green is recorded in two parts: (a) local green at the amending commit,
> explicitly annotated as forged-`origin/main`-conditional with the forged OID
> recorded; (b) published green — the same suite plus
> `.github/workflows/ci.yml`'s `--require-published` job — after the
> transaction reaches real `origin/main`. Acceptance closure requires (b). No
> transcript may report (a) as "the suite is green."

### 5.3 Condition 5 names circular authenticators — correct the record before the probe is run

Condition 5's authenticators of record for the new class are "the test run
itself plus the changed-set gate." For the tamper the probe will actually run
(literal alone, in a clone) that is fine. For the **coherent** {pinset, literal}
tamper — the only one that matters, since both paths are now allowlisted —
both are circular: the test run consumes the tampered literal, and the
changed-set gate subtracts both paths by construction.

Amend to the true set, which is not weaker, merely honest:

> Authenticators of record for the `tests/test_receipt_histsem.py` class:
> **K7 bootstrap** (`rh-ruling.md:22-26`, the only check that validates a new
> pinset rather than consumes one), **the transaction confirmation table**
> (`receipt_histsem_verifier.md:118-119`), and **Ed's exact-byte step 6**. The
> residual — a coherent in-transaction {pinset, literal} substitution — is the
> in-process actor already registered under D-139 A1 and disclaimed by the
> Truth boundary. The probe proves single-file tamper detection; it must not be
> recorded as proving coherent-tamper detection.

Without this, a future probe passes vacuously and the V-1(vi) tripwire silently
stops being a tripwire.

### 5.4 An unrelated precondition defect that will stop S-0 under any ruling

`s0-runsheet.md:628` reads
`json.load(open("configs/arm_readiness/d117_row_registry_v1.json"))["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]`.
At `1ba04a8` that file's top-level keys are
`['plan_profiles','registry_id','rows','schema_version']` — **no
`freeze_evidence_lifecycle`, no `irrelevant_path_allowlist`.** §4(d) will
`KeyError` before reaching its intended gate. Condition 1 covers the generator
script but not the registry key. Add the registry authoring to condition 1's
pre-derivation set. (Runtime note for condition 4: the live gate at
`arm_readiness.py:4041-4042` is pure subtraction —
`set(changed_paths) - allowlist` — and never refuses on an *unused* entry;
missing/extra/unused exactness lives only in the S-0 custody checker, which is
what must be updated to expect 113.)

## 6. Final round-2 position

**I move to the cold seat's verdict: Option 1, precisely bounded, 112 → 113,
with its six conditions plus the four amendments in §5.**

Ranking: **Option 1 (amended) ≻ O-1-E ≻ O-1-D ≻ option 2 ≻ option 3.**

I place O-1-E (defer the test update only; no versioning, no code delta) above
O-1-D because it avoids the activation-model redesign and the §3(a) trilemma
entirely, and it remains the natural fallback **if and only if** the magistrate
concludes that a red intermediate commit is cheaper than the in-window
self-attestation Option 1 accepts. I no longer think it is: the intermediate
commit's red state is a *worse* signal than a disclosed, reviewed,
same-commit pin, because a red normative test on the transaction branch is
indistinguishable from a real defect and invites exactly the "fix the test
expectation" response that `s0-runsheet.md:830` forbids.

**On conditions the cold seat may offer onto O-1-D:** I would not accept them.
§3(a) is not a condition-shaped problem — no condition can make the absent
successor simultaneously tolerated at freeze ×3 and refused afterward. If the
cold seat's reply proposes salvaging O-1-D, my position is that it should not
be salvaged, and I would rather the magistrate take Option 1 with §5's
amendments than a conditioned O-1-D.

**What would move me back:** exactly one artifact — Ed's step-6 exact-byte table
definition (r4-3), if it turns out to enumerate the pinset's digest. That would
restore the fixation-gap mitigation withdrawn in §1/§3(c). It would still not
answer §3(a), so it would move O-1-D from third to second, not to first. The
absence of that artifact from a mechanically-assembled cold-gate packet is
itself worth recording: my round-1 construction leaned on a document the packet
does not contain.

---

# Round 3 — final position

Read `cold-fable-verdict.md` §§R2.1-R2.4 (the cold seat concedes Option 1 and
adopts O-1-D with six conditions). Verified independently before replying:
r4-3 (`v4-plan-ruling-r4draft.md:46-61`, verbatim as the seat quotes it) and
`tests/test_receipt_histsem.py:368-390`.

**The seats have crossed. I do not move back by reflex, and the magistrate
should audit the reasoning below rather than count votes.** My round-2
concession rested on two of *my own* arguments against O-1-D — the trilemma
(§3a) and the delta sizing (§3b). Both have now moved: the trilemma is
answered (though not by the seat's rule — §1), and the delta sizing resolves
in the seat's favour once the disputed component is dropped (§3). The ground
for my concession is gone, so I return to O-1-D. The V-1(iii) argument (§2),
which I never addressed in round 2, is independently decisive.

**FINAL: O-1-D, on the merged condition set in §4.**
Ranking: **O-1-D ≻ Option 1 ≻ O-1-E ≻ option 2 ≻ option 3.**

## 1. The trilemma: answered — but the seat's rule is unsound and unnecessary

**My trilemma is answered.** I asserted that horns (i) tolerate-absent-at-freeze
and (ii) refuse-absent-after require time-dependent semantics. That was wrong:
it assumed the only predicate available was "absent at HEAD," which is
two-valued. The seat adds a second predicate (history presence), and a
history-dependent rule is a well-defined function of repository state, not of
wall-clock. Conceded cleanly — my trilemma does not defeat O-1-D.

**But the rule the seat proposes should be struck, on four independent
grounds.** I checked each against the code.

1. **It inverts a normative test.** `tests/test_receipt_histsem.py:368-390`,
   `test_committed_pinset_deletion_gate_returns_normally`, clones, `unlink`s
   the pinset, **commits the removal**, and asserts
   `self.assertIsNone(readiness._gate_receipt_histsem(pack))`. That is exactly
   the committed-then-deleted state, and it is normatively required to
   **return**. The seat's rule requires it to **refuse**.
2. **It is not entailed by RH-8 — the reconciliation already exists.** The seat
   argues the tightening is compelled by RH-8's clone-proof clause
   ("absent → the pinset-absent refusal"). But `s0-runsheet.md:792` already
   records the settled reading: *"the **library's default HEAD pinset absence**
   returns ordinary readiness; **only this explicit CLI/worktree verifier path**
   promises `histsem_pinset_absent`."* RH-8's clause is discharged by the CLI
   path (`tests/test_receipt_histsem.py:62-80`, exit 2), not the library gate.
   The entailment claim fails on a document the runsheet already contains, and
   the semantic is rule-11-settled (`receipt_histsem_verifier.md:6-11`, `:36`).
3. **It fails open on shallow history.** `_gate_receipt_histsem` returns at
   `:3479` *before* anything reaches a shallow guard —
   `histsem_history_shallow` is raised inside `historical_pack_tree_sha256`,
   which runs only *after* membership succeeds. So a `git rev-list HEAD --
   <path>` probe in a shallow clone returns empty for a path introduced before
   the shallow boundary → "never committed" → **ordinary readiness, governance
   silently off.** The seat's assurance that shallow "is already owned" does not
   hold at this call site.
4. **It fails open on history rewrite.** The probe is a bare local-history
   query. The one actor the truth boundary names — the history rewriter —
   converts a refusal into a silent pass by dropping the introducing commit.
   The new predicate's failure mode is fail-open against precisely the
   adversary it would be added to resist.

**And it is unnecessary, which is the cleaner resolution.** Ask what the
tightening buys: refusal on post-window deletion of the successor. But after
fixation the successor is byte-pinned — deleting it makes
`PINSET.read_bytes()` fail and CI goes red. That is the contract's own
assignment, `receipt_histsem_verifier.md:36`: *"Committed pinset mutation or
deletion is owned by the byte-pin and changed-set CI controls."* The successor
gets exactly the protection v1 has today, by the mechanism already ruled for
it.

So the trilemma dissolves without any new semantic: horn (i) holds on unchanged
absence semantics; horn (iii) holds because the successor is present at arm
time; horn (ii) is discharged post-fixation by the byte pin. The only uncovered
interval is mint → fixation, which is the residual condition 4 registers
anyway. **Strike the rule.**

## 2. V-1(iii): Option 1 does not survive it — and my round-2 rejoinder missed the question

The coordinator is right that my round-2 concession never engaged this. Doing
so now changes the answer.

V-1(iii) (`rulings-r5-consolidation.md:91-93`): *"Sol conceded back to the
static list **CONDITIONAL on independent authentication of all allowed
bytes**."* This is not a statement about how much tamper-evidence is
tolerable. It is the **ratified basis** of the static-list mechanism. My
round-2 D-139 A1 rejoinder answered a different question — whether the residual
is acceptable — and left this one untouched.

Can the test-file class satisfy it, or V-1(vi)'s digest-conditional fallback?
No, and the reason is the seat's own round-1 theorem: the test file's
post-derivation bytes contain a SHA of the post-derivation pinset, so **no
pre-committed digest can be supplied**. The fallback is unavailable. The ruled
consequence is `s0-runsheet.md:725`/`:830`: *"remove that class from the
candidate allowlist and bind it in the authenticated derived manifest, then
reopen the mechanism proof"* — the V-1(vii) derived manifest, **not an
amendment**. A cold gate may amend a ruled *value* (111→112). It may not
silently retire the *condition* on which the mechanism was adopted; doing so
voids the concession that produced the static list.

**The sharp form, which neither seat has stated:** the allowlist is
**path-granular, not line-granular**. Allowlisting `tests/test_receipt_histsem.py`
subtracts the *entire file* from the changed-set gate for the window —
including `test_coherent_legacy_tamper_control_accepts_but_histsem_refuses`
(`:196-277`), `test_required_refusal_granularity` (`:114-144`),
`test_vocabulary_is_disjoint_closed_and_each_code_constructs` (`:146-152`), and
nine others. Ed's step-6 digest confirmation covers *one literal*, not the
other twelve normative tests. So Option 1's window admits arbitrary weakening
of the entire histsem normative suite with no mechanical objection. Under
O-1-D, `tests/` is never allowlisted and any touch is refused at `:4041-4049`.

The seat's condition-2 counterpart lands too: under O-1-D the successor class
**can** be digest-conditional (the confirmation-table digest, derived at mint
and confirmed at step 6), so all 112 allowed byte-sets carry an authenticator
and V-1(vi) is *exercised rather than waived*. Contemporaneous authentication
is already accepted by V-1's own scheme — V-1(iv) makes the arm-time semantic
replay gate load-bearing for four classes on exactly that footing.

**Option 1 is refuted on V-1(iii)/(vi).** This is where round 1 started, but
for a better reason than round 1 gave.

## 3. Delta sizing: resolved — the seat is right, once the struck component is struck

My round-2 characterization ("a redesign of the activation model colliding with
the rule-11-settled absence semantic") **assumed the tightening**. Every
expensive item on my list flowed from it: a new closed-vocabulary reason code,
the normative refusal-table amendment (`receipt_histsem_verifier.md:82-99`),
the disjointness test at `:146-152`, and the rule-11 collision. With the
tightening struck (§1), that entire branch disappears. Honest enumeration of
what remains:

| Touch point | Change | Scale |
|---|---|---|
| `arm_readiness.py:2712-2714` | constant → ordered enumerated tuple | trivial |
| `_gate_receipt_histsem` `:3467-3508` | loop ls-tree/show per member; union rows; **absent member → skip (semantics UNCHANGED)** | modest |
| cross-member `(pack_id, pack_path)` uniqueness | → existing `histsem_pinset_invalid`; **no new reason code** | small |
| `verify_all_receipt_histsem` `:3415` | enumerate over the union | modest |
| CLI `--pinset` | single explicit override preserved; `:62-80` untouched | none |
| tests | union / duplicate-identity / absent-member regressions | ordinary |

The **activation model is unchanged** — membership in a committed pinset
engages the gate; only the row *source* becomes a union of code-enumerated
files. I withdraw "redesign." The seat's reading is correct, including its
point that the single-hardcoded-path finding is the *reason* a pre-derivation
delta is required rather than an argument against one.

**Can the reviewed-candidate lane absorb it? Yes.** r4-3 (`:46-61`) puts "all
registry/code/marker-consumer/scheduler/reference commits" in step 2, before
U11 ×3 and before the derivation head — the lane already carries code deltas,
and RH-8 independently requires this verifier to land pre-`_v4`-re-freeze. The
delta above is smaller than the verifier itself, which that lane already
absorbed.

**Two corrections from the seat that I accept against my own text:**
(a) fixation cannot land "the first commit after the final arm" (my §5.1) —
r4-3's commit-freeze runs from attestation **through window close**, so it is
the first commit after *window close*. The gap is longer than I wrote and I own
that. (b) **O-1-E is dead**, and r4-3 kills it: at the published head the
pinset would carry 12 rows against a test asserting 9/99/108, so r4-3's
"published-head suite" step is RED and the transaction cannot complete its own
ruled order. I could not read r4-3 in round 2; the seat's kill is correct.

## 4. Merged condition set for the magistrate

Seat's six, reconciled with my four, plus three new. Deltas from the seat's
text are marked.

1. **Pre-derivation reviewed candidate** carries: the contract amendment
   (governed pinset → closed, ordered, code-enumerated chain); the chain-read
   delta with regression tests; the allowlist at **112** with the successor's
   exact path as the 112th entry (no ruled number amended).
   **[AMENDED — the refuse-if-absent-but-in-history rule is STRUCK, §1.]**
2. **Digest-conditional subtraction for the successor class:** S-0 §4(d)
   verifies the successor's committed bytes against the confirmation-table
   digest in transaction custody. V-1(vi) exercised, not waived. **[ACCEPTED —
   this is what makes O-1-D lawful where Option 1 is not.]** The per-class probe
   list records the confirmation-table digest as the authenticator of record;
   **no probe may record "the test run itself" as an authenticator** (my round-2
   §5.3 — circular for the coherent case).
3. **Fixation:** the first commit **after window close** (r4-3 commit-freeze);
   adds the successor's SHA literal and row/receipt/fact counts as **new**
   assertions touching no v1 assertion; an independent reviewer recomputes the
   SHA and matches it to Ed's step-6 table. **[+ my §5.1, transferred:** the
   same commit renames `test_differential_self_test_all_nine_packs` (`:82`),
   whose name goes false once the corpus is the union.**]**
4. **Two-part green [NEW — my §5.2, transferred and still binding].**
   `tests/test_receipt_histsem.py:92-103` runs
   `verify_all_receipt_histsem(require_published=True)`, and the runsheet forges
   `refs/remotes/origin/main` at `s0-runsheet.md:325` while real CI runs the same
   predicate at `.github/workflows/ci.yml:28`. Local green must be recorded as
   forged-ref-conditional with the forged OID; acceptance closure requires
   published green. No transcript may report local green as "the suite is green."
5. **Residual registration:** mint → fixation recorded as a named residual under
   the truth boundary / D-139 A1, with the seat's phase-by-phase controls
   (R2.2(a)) listed. **[ACCEPTED.]**
6. **Chain integrity [NEW]:** the chain is **closed** — a pinset file present in
   the repository but not code-enumerated governs nothing; cross-member
   duplicate `(pack_id, pack_path)` refuses `histsem_pinset_invalid`; absent
   enumerated member skips, with **no** change to the `:36` absence semantics.
7. **Family precedent [merged with my fixed-point principle]:** `_v5` repeats the
   shape with its own successor artifact, its own exact entry, fixation
   post-window. Stated as a standing rule, stronger under O-1-D than the version
   I proposed in round 2: **no authenticator path ever enters any allowlist, in
   any transaction.** A proposal to add one is a V-1(vi) tripwire event routing
   to the V-1(vii) derived manifest, not an amendment.
8. **Out-of-scope defects endorsed:** the registry precondition
   (`freeze_evidence_lifecycle.irrelevant_path_allowlist` absent at `1ba04a8`;
   `s0-runsheet.md:628` will `KeyError`) and the record that the changed-set
   contract is a **window property, not a standing invariant** — the finding
   whose absence generated O-1.
9. **If the magistrate keeps a tightening anyway [NEW, contingent]:** it must
   (a) carry an explicit shallow-history guard at the `:3479` return, (b) anchor
   the history probe to a published ref rather than bare local HEAD, and
   (c) explicitly amend `receipt_histsem_verifier.md:36` **and** invert
   `tests/test_receipt_histsem.py:368-390` — a rule-11-settled semantic, so
   Ed/magistrate sign-off, never implementer discretion.

## 5. What I still hold against the consensus

One item, recorded so convergence is not mistaken for unanimity: the seat
retains a doubt that my "Option 1 ≈ Option 3" framing overstates at the
detectability layer. **I concede that and adopt its formulation** — Option 1
should enter the record as *"refuted on V-1(iii)/(vi) mechanism grounds"*, not
as a covert waiver of detectability. Detectability does survive Option 1; what
does not survive is the static list's ratified basis.

My round-1 and round-2 sections stand unedited above as the record of positions
taken and conceded.
