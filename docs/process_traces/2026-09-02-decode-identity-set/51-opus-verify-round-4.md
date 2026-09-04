# Opus different-model verification — decode-identity lineage paragraph, fix round 4

Verifier: Opus (different-model seat), 2026-09-03.
Checkout: `/Users/edr/code/JouleWise-wt-decode-id`, branch `fix/2026-09-02-decode-identity-set`.
Landing under review: `90689048`, diff of `docs/contracts/identity_pin_projection.md`
from `086d306f`.
Writer's landing record: file `50-sol-round-4-landing-record.md`.
Scratch (all probe scripts, no writes under the checkout):
`<scratchpad>/decode-r4-verify/`.

## 0. Bottom line

The **landed contract text is substantively sound**. I re-executed all 18 claims
independently against a real settled lineage and every reason code the paragraph
names is the code the production path actually emits — 25 probe rows, 0 FAIL, plus
3 rows for C15 under a corrected method. All seven of the gate's §2 corrections are
applied. Tests pass.

The **landing record's headline evidence artifact is weaker than it claims to be**.
The first-use table is described as "built mechanically ... covers every matching
phrase in the added or moved lines"; in fact its noun-phrase rows and their
definition markers are 32 hand-typed dictionary constants. The table therefore
cannot fail on an omitted term, and my independent extraction (93 diff-scoped terms)
found one omitted term that is genuinely undefined in the landed text, plus two
terms that pass only because a bold mark is matched against itself.

Finding counts: **1 blocker (against the record, not the text), 4 should-fix, 4 nits.**

---

## 1. Charge (1) — independent first-use derivation, then diff against the writer's table

I built my own extractor from the grammar in brief file 49 §4.1 and ran it **before**
reading file 50's table.

Scripts: `firstuse.py` (raw pass, all sub-runs), `firstuse2.py` (refined: maximal
noun phrases, definition credit for a bold mark or parenthetical gloss on the term
or its head). Added-line scope: `added_lines.txt`, 84 lines, derived from the diff.

My extraction: **93 diff-scoped terms (20 backticked literals, 73 noun phrases)**,
32 needing hand adjudication.
Writer's table: **54 rows (32 hand-listed noun phrases, 22 mechanically extracted
literals)**, all PASS.

### 1.1 Disagreements

**D1 — the noun-phrase half is not mechanical (BLOCKER, against the record).**
The writer's script contains:

```python
noun_rows={
"launch-lineage authenticator":["launch-lineage authenticator"],
...
"ordinary launch step":["ordinary launch step"],
}
def_markers={
"launch-lineage authenticator":"(the launch-lineage authenticator)",
...
}
```

These are literal constants. Nothing in the script derives a noun phrase from the
text. The only mechanical half is the literal extraction
(`code_literals=sorted(set(re.findall(r"`([^`]+)`",added_text)))`) guarded by
`assert not missing_gloss` — that half genuinely fails closed. The `assert any(
normalize(t) in normalize(added_text) ...)` on each noun row only checks that a
hand-listed term is *present*; a term the author never listed is invisible.

The record states the grammar "covers every matching phrase in the added or moved
lines". That is not verifiable from the script and is not true of a hand-enumerated
list. This is the same defect class — a prose property asserted rather than
mechanically established — that rounds 1–3 failed on, which is why the brief made
the mechanical build a gate.

**D2 — "bundle loading" / "input loading": undeclared alias, one glossed, one not
(SHOULD-FIX).** Exactly the miss D1 predicts. `:656–657` reads:

> Before a lineage-checked bundle is admitted as analysis
> input, bundle loading authenticates its launch lineage through the recorded
> paths and refuses at input loading (the bundle-to-analysis admission step), so

"bundle loading" is the operative actor at `:656`, `:660` and `:676`; only "input
loading" carries a gloss. The brief's grammar requires "aliases listed as rows
naming both spellings". The writer's table has the row
`"input loading / bundle-to-analysis admission step"` and **no row for "bundle
loading"**. Either the two are aliases (undeclared) or two distinct terms (one
unbuilt); the sentence does not say which, which is itself the defect.

**D3 — a bold mark counted as its own definition (SHOULD-FIX).** The writer's
`def_markers` maps `"pack digest" -> "**pack digest**"` and
`"ordinary launch step" -> "**ordinary launch step**"`, so `definition_line` finds
the bold mark and scores first-use == definition == PASS. Neither term is glossed
anywhere in the contract:

- `**pack digest**` `:588` — only other uses are `:699`, `:704`, which use it, not build it.
- `**ordinary launch step**` `:732` — sole occurrence in the file.

Under the standard in force ("built from physical reality before first use, glossed
in plain words AT first use, or deleted") a bold mark alone is emphasis, not a
definition. Note the irony: correction §2(f) demoted `**launch manifest**` and
`**one-use consumption record**` at the old `:671-672` "so each definition has one
home", and the same edit **promoted** "ordinary launch step" to bold.

**D4 — "consumer identity set" (SHOULD-FIX).** `:628-629` glosses the refusal code as
"(the analysis gate could not authenticate the consumer identity set)". The contract
builds "**distinct member identity set**" at `:109` — a different object. "consumer
identity set" is built nowhere; the gloss restates the code name in English rather
than explaining it. The writer's table scores it PASS with the marker
`"authenticate the consumer identity set)"`, i.e. the gloss matched against itself.

**D5 — first-use is not diff-scoped (NIT).** The writer's `first_line()` scans the
whole document from line 1, not the added lines. Visible in the row
`pack root | 496 | 496 | PASS`: `:496` is pre-existing text. Harmless here (`:496`
does gloss "campaign-pack directory (the pack root)"), but the reported line numbers
are not the diff-scoped ones the brief asked for.

**D6 — `.sha256` gloss stutter (NIT).** `:673-674`: "A receipt whose `.sha256`
(sidecar suffix) sidecar is gone…". The gloss defines the *suffix*; the noun
"sidecar" is then used and is built only at `:176`.

### 1.2 Agreements

Every one of the writer's 54 rows that I also extracted, I agree with. The 22
literal rows are mechanically sound and correctly glossed. My residue beyond D2–D4
is ordinary English or parser artifact ("absolute path", "reviewed command",
"later artifact", "listed code", …), which I adjudicated PASS by hand.

### 1.3 Reproducibility of the writer's table (NIT)

The recorded command runs `git diff --unified=0 -- PATH` with **no base commit**.
At HEAD the diff is empty and the script aborts on its first row. Supplying
`086d306f` reproduces the recorded table **byte-identically** (54 rows, 54 pass).
So the table is faithfully recorded — the recorded command just cannot re-run it.

---

## 2. Charge (2) — re-execution of C1–C18

I did not rely on the writer's runner (`probe_claims.py` is not pasted in file 50 —
only its SHA-256 and self-reported JSON verdicts). I built an independent harness.

**Method.** Every hop probe deletes a **real artifact** from a **real settled
lineage** produced by the production writers `_consume_launch_capability` →
`record_launch_lifecycle_event("start")` → `("settle")`, reusing
`tests.test_arm_readiness.LaunchConsumptionV2Tests` as the fixture factory. This is
stronger than the cold seat's `46a-coldF-*` scripts, which stub leaf readers rather
than deleting files. Each probe is paired with a counterfactual: the unmutated
fixture, which must authenticate. For C1 I built a real git-committed pack so
`_pack_record` runs **unmocked**.

Scripts: `probes_c1_c18.py`, `probes_c5_c15.py`, `probes_c15_fixed.py`.

| Claim | Expected (brief §3, fixed in advance) | Observed | Verdict |
|---|---|---|---|
| CF | unmutated lineage authenticates | authenticated, `consumption_id='arm-0001-launch'` | PASS |
| C1 | `pack_root` == `str(pack_root.resolve())` | equal (unmocked `_pack_record`) | PASS |
| C1b | `generate_arm_receipt` stores the record | `pack = _pack_record(root)` + `"pack": pack,` | PASS |
| C2 | no `pack_root` key in consumption receipt | absent from `CONSUMPTION_RECEIPT_KEYS` and a real receipt | PASS |
| C3 | untagged admitted, lineage `None`, no error | `None`, on a genuinely broken lineage | PASS |
| C4a | tagged + gone artifact → `LaunchLineageError` | `launch_lifecycle_incomplete` | PASS |
| C4b | `_read_bundle` raises before any evidence row | `AnalysisInputError: launch_lifecycle_incomplete: bundle-1` | PASS |
| C5 | locator gone → `launch_consumption_missing` | `launch_consumption_missing` | PASS |
| C5b | locator **sidecar** gone → same | `launch_consumption_missing` | PASS |
| C6 | consumption receipt → `launch_consumption_missing` | `launch_consumption_missing` | PASS |
| C7 | arm receipt → `launch_consumption_invalid` | `launch_consumption_invalid` | PASS |
| C8 | pack root → `launch_binding_mismatch` | `launch_binding_mismatch` | PASS |
| C9 | launch manifest → `launch_consumption_invalid` | `launch_consumption_invalid` | PASS |
| C10 | window plan root → `launch_binding_mismatch` | `launch_binding_mismatch` | PASS |
| C11a | `window.env` → `launch_consumption_invalid` | `launch_consumption_invalid` | PASS |
| C11b | `window-chain.zsh` → `launch_consumption_invalid` | `launch_consumption_invalid` | PASS |
| C12a | start receipt → `launch_lifecycle_incomplete` | `launch_lifecycle_incomplete` | PASS |
| C12b | settle receipt → `launch_lifecycle_incomplete` | `launch_lifecycle_incomplete` | PASS |
| C13 | earliest gone hop's code, for each k | all 7 ladder steps match | PASS |
| C14a | consumption sidecar → same as C6 | `launch_consumption_missing` | PASS |
| C14b | start sidecar → same as C12 | `launch_lifecycle_incomplete` | PASS |
| C15-L1 | unresolvable pack root short-circuits | present: reached 1×; gone: reached 0×, `frozenset()` | PASS |
| C15-L2 | empty declared set → the refusal code | empty → `('consumer_identity_set_unauthenticated',)`; nonempty → `()` | PASS |
| C16 | second consume refused | `readiness_record_consumed` | PASS |
| C17 | `window.env` moved out → `launch_consumption_invalid` | `launch_consumption_invalid` | PASS |
| C18a | completion absent, `require_completion=False` → admitted | NO ERROR | PASS |
| C18b | `require_completion=True` → refuses | `launch_lifecycle_incomplete` | PASS |
| C18c | kinds + predecessor chain | `launch_start`/`launch_settle`, chain True | PASS |

C19 carries no probe (statement of limitation, S3 ruling (d)) — correctly so.

**28 rows, 0 FAIL.** Every reason code the paragraph names is the code the code emits.

### 2.1 A defect in my own first C15 attempt, and its correction

My first C15 probe was invalid and I record it rather than discard it. I called
`_frozen_consumer_identity_set` with the pack root present and then absent, and got
`frozenset()` **both times** — the fixture's pack is not git-committed, so
`committed_pack_tree_sha256` fails in either arm. The counterfactual did not
discriminate, so it proved nothing about the pack root. (This is the
mutation-cure counterfactual failure mode.)

Corrected method (`probes_c15_fixed.py`) splits the claim into the two links it
actually asserts, each with a counterfactual that changes the observed value:
L1 proves the pack-root resolve short-circuits (spy on `committed_pack_tree_sha256`:
reached once when the root is present, never when gone); L2 proves the mapping
(patch the declared set empty vs nonempty; only empty yields the code). Both pass.

The writer's C15 control is *stronger* than mine — `{"result_type":"FloorRequest"}`
means the writer built a full happy path returning a real request. I could not
reconstruct that (it needs a frozen identity-pin projection and a matching U8 freeze
receipt) and, because `probe_claims.py` is not pasted, I cannot verify it. Recorded
as consistent-but-unverified rather than confirmed.

---

## 3. Charge (3) — the gate's §2 corrections

| # | Correction | Applied? | Evidence |
|---|---|---|---|
| a | "recorded paths", never "recorded files" | YES | `:620` "**recorded paths**"; zero matches for "recorded file" |
| b | tag qualifier kept; untagged never lineage-checked | YES | `:653`; proved by C3 |
| c | no "created outside the runs roots" claim | YES | no such sentence; `:620` makes only a locator-location claim, which C5 proves |
| d | sibling custody directory, not "beside" | YES | `:601` "the sibling custody directory (a separate custody directory with the same parent)". Confirmed in code: `arm_path = consumption_path.parent.parent / arm_reference["path"]` |
| e | must not claim the hop list is exhaustive | YES | `:659` "is not exhaustive of every launch-lineage check" |
| f | demote the bold marks at old `:671-672` | YES, but | `:731-733` both demoted with a back-reference to §Analysis-gate definitions — **and a new `**ordinary launch step**` promoted to bold with no gloss** (D3) |
| g | extend the status clause | YES | `:13-16` names `arm_readiness.py` and `analysis_engine/inputs.py` as authoritative for the launch-lineage sentences |

Cross-references resolve: `### Analysis-gate definitions` `:581`, `### Analysis
consumption` `:640`.

**7/7 applied**, with the (f) caveat.

### 3.1 Collateral edits outside the two scoped blocks (SHOULD-FIX)

The diff also touches `:164`, `:468` and `:572` — pre-existing text in other
sections. All three exist to stop a term preceding its new definition at `:589`
(after the edits, "arm receipt" appears nowhere before `:589`). Two carry a cost:

- **`:572` — two code citations deleted.** Was: "…but may have no arm receipt to
  bind (`joulewise/identity_pins.py:2100-2234`; `joulewise/arm_readiness.py:5681-5729`)."
  Now: "…but Arm may have issued nothing to bind." Traceability lost from a section
  the brief did not scope, to satisfy a documentation check on a different section.
- **`:468` — a normative requirement reworded.** Was "whose resolved path stays
  **below the pack root**"; now "stays **within the campaign pack**". Same
  containment in substance (`:496` glosses campaign-pack directory = the pack root),
  but the original mirrored the implementation's own language —
  `_declared_manifest_path`'s docstring reads "Resolve one declared suite manifest
  as a regular file *below its pack*" (`joulewise/identity_pins.py:1541`).
- **`:164` (NIT)** — "holds arm receipts" → "holds the launchable receipts issued by
  Arm". Defensible ("launchable receipt" already appears at `:153`) but the
  vocabulary entry for window custody no longer names the artifact it holds.

WRITE_SCOPE was respected: the landing commit touches exactly the two permitted
files and the working tree is clean.

---

## 4. Charge (4) — tests

The brief's `tests.test_analysis_engine_inputs` **does not exist**; the writer
correctly substituted `tests.test_analysis_inputs` and said so. I ran the same pair
and reproduce the writer's result exactly (84 tests, OK, skipped=4).

---

## 5. Charge (5) — severity tiering

### BLOCKER (1) — against the landing record, not the contract text

**B1.** The first-use table's noun-phrase half is 32 hand-typed constants, not a
mechanical extraction, while the record claims it "covers every matching phrase in
the added or moved lines". The gate cannot fail on an omitted term — and one omitted
term (S1) is genuinely undefined in the landed text. The brief made the mechanical
build a required deliverable precisely because three prior rounds failed on
asserted-rather-than-established prose properties.
*Cure:* extract noun phrases from the added lines programmatically (my
`firstuse2.py` is a working starting point), rerun, fix whatever it surfaces; and
correct the record's description of what the script does.

### SHOULD-FIX (4)

**S1.** "bundle loading" (`:656`, `:660`, `:676`) vs "input loading" (`:657`) —
undeclared alias; only one spelling glossed.
**S2.** `**pack digest**` (`:588`) and `**ordinary launch step**` (`:732`) are bold
with no gloss anywhere; the table scores them PASS by matching the bold mark to
itself. "ordinary launch step" was newly bolded by the correction that demoted two
other bold marks to give each definition one home.
**S3.** "consumer identity set" (`:629`) is used inside the gloss for
`consumer_identity_set_unauthenticated` and is never built; the contract builds
"distinct member identity set" (`:109`), a different object.
**S4.** Collateral edits at `:572` (two code citations deleted) and `:468` (a
normative containment requirement reworded away from the implementation's own
phrasing), both in sections the brief did not scope.

### NIT (4)

**N1.** The recorded first-use command omits the base commit and aborts at HEAD;
with `086d306f` it reproduces byte-identically.
**N2.** `probe_claims.py` is not pasted (only its SHA-256 and self-reported
`VERDICT=PASS` lines), unlike the first-use script. Mitigated: I re-executed
independently and every code agrees.
**N3.** `:164` "the launchable receipts issued by Arm" is vaguer than "arm receipts".
**N4.** `:673-674` "`.sha256` (sidecar suffix) sidecar" reads as a stutter.

---

## 6. Executed evidence

### 6.1 Landing under review

```
$ git log --oneline -3
90689048 DECODE-IDENTITY fix round 4 (Sol 269 xhigh, formulation 4): lineage vocabulary built in the defined-terms block, paragraph rewritten from the claim list with executed per-hop reason codes; landing record (50) carries the mechanical first-use table and C1-C18 probes with counterfactuals
086d306f DECODE-ID: cold-gate synthesis (48) + fix round 4 brief with the claim list and expected probe outputs (49)
d39b1019 DECODE-ID: custody Opus refutation on packet 45 (file 47): Q2/Q3/Q7 stand, Q4/Q5/Q6/Q8 falsified with executed blockers, Q1 refused; seal notice (shared scratch dir)

$ git show --stat --oneline 90689048 | head -4
90689048 DECODE-IDENTITY fix round 4 ...
 docs/contracts/identity_pin_projection.md          | 107 ++++-
 .../50-sol-round-4-landing-record.md               | 490 +++++++++++++++++++++
 2 files changed, 574 insertions(+), 23 deletions(-)

$ git status --short
(empty)
```

### 6.2 My independent first-use extraction

```
$ PYTHONDONTWRITEBYTECODE=1 python3 firstuse2.py fails
terms extracted: 93 (literals 20, NPs 73) | residue needing hand adjudication: 32

TERM                                     KIND     USE   DEF   DEFINED-BY
...
bundle loading                           NP       656   657   parenthetical gloss (the bundle-to-analysis
...
```

Adjudication of the residue is in §1.1; the substantive misses are D2–D4.

### 6.3 Cross-checks behind D2–D4

```
$ grep -n "input loading\|bundle loading\|Bundle loading" docs/contracts/identity_pin_projection.md
656:input, bundle loading authenticates its launch lineage through the recorded
657:paths and refuses at input loading (the bundle-to-analysis admission step), so
660:launch-lineage check. In execution order (the order bundle loading checks
676:Bundle loading uses `require_completion=False` (the **completion policy**):

$ grep -n "pack digest" docs/contracts/identity_pin_projection.md
588:  back to the consumed arm authorization and its exact **pack digest**.
699:name the same pack root and the same 64-hex pack digest; (2) the pack root
704:from its committed bytes) equals that pack digest, which is the same digest the

$ grep -n "ordinary launch step" docs/contracts/identity_pin_projection.md
732:The **ordinary launch step** authenticates and replays the arm receipt, pack

$ grep -n "identity set" docs/contracts/identity_pin_projection.md | head -5
109:  configuration. The **distinct member identity set** is the mathematical set
361:   Let `H` be the lexically sorted distinct member identity set. `H` must be
394:the sorted distinct member identity set. The projection also derives the model
484:   cardinality one. The distinct member identity set for the unit must have
629:  authenticate the consumer identity set).
```

### 6.4 Reproducing the writer's first-use script

```
$ python3 -c "extract the single ```python block from file 50"
python blocks found: 1
sha256 of extracted block: 1b3b47beacee99711417dd177214539d97738d6091133deb0674bd7bd046107f
recorded sha256:          1b3b47beacee99711417dd177214539d97738d6091133deb0674bd7bd046107f

$ PYTHONDONTWRITEBYTECODE=1 python3 -B writer_first_use.py
TERM | FIRST_USE | DEFINITION | VERDICT
Traceback (most recent call last):
  File ".../writer_first_use.py", line 129, in <module>
    assert any(normalize(t) in normalize(added_text) for t in terms), f"noun grammar row absent: {display}"
AssertionError: noun grammar row absent: launch-lineage authenticator

$ sed 's|["git","diff","--unified=0","--",PATH]|["git","diff","--unified=0","086d306f","--",PATH]|' ... && python3 -B writer_first_use_based.py
exit=0
SUMMARY rows=54 pass=54 fail=0

$ diff <(grep '|' writer_rerun.txt) <(grep '|' recorded_table.txt)
IDENTICAL to the recorded table
```

### 6.5 Probe re-execution — C1, C2, C13, and the hop ladder

```
$ PYTHONDONTWRITEBYTECODE=1 python3 probes_c1_c18.py
==============================================================================
PART A - C1, C1b, C2 (no fixture needed)
==============================================================================

C1 _pack_record(pack)['pack_root'] = '/private/var/folders/.../opus-r4-pack-3rudrd60/repo/pack-real'
C1 str(pack_root.resolve())        = '/private/var/folders/.../opus-r4-pack-3rudrd60/repo/pack-real'
[PASS] C1    expected=pack_root == str(resolve())        observed=equal unmocked _pack_record on a git-committed pack
[PASS] C1b   expected=generate_arm_receipt stores _pack_record observed=True structural read of the generator body

C2 CONSUMPTION_RECEIPT_KEYS = ['arm_context_sha256', 'arm_receipt', 'assurance', 'boot_session_id', 'consumed_at_monotonic_ns', 'consumed_at_utc', 'consumption_id', 'exec_argv', 'handoff_token_sha256', 'head_commit', 'launch_manifest', 'pack_id', 'pack_sha256', 'plan_id', 'receipt_kind', 'schema_version', 'volatile_checks', 'window_chain', 'window_environment', 'window_id']
[PASS] C2    expected=no pack_root key                   observed=absent

==============================================================================
PART B - C3-C18 on a REAL settled lineage
==============================================================================

COUNTERFACTUAL (nothing deleted): authenticated, consumption_id='arm-0001-launch'
[PASS] CF    expected=unmutated lineage authenticates    observed=authenticated control for C5-C14, C17, C18

--- C5-C12: delete ONE artifact on a settled lineage, one run per hop ---
[PASS] C6    expected=launch_consumption_missing         observed=launch_consumption_missing consumption receipt
[PASS] C7    expected=launch_consumption_invalid         observed=launch_consumption_invalid arm receipt
[PASS] C8    expected=launch_binding_mismatch            observed=launch_binding_mismatch pack root
[PASS] C9    expected=launch_consumption_invalid         observed=launch_consumption_invalid launch manifest
[PASS] C10   expected=launch_binding_mismatch            observed=launch_binding_mismatch window plan root
[PASS] C11a  expected=launch_consumption_invalid         observed=launch_consumption_invalid window.env
[PASS] C11b  expected=launch_consumption_invalid         observed=launch_consumption_invalid window-chain.zsh
[PASS] C12a  expected=launch_lifecycle_incomplete        observed=launch_lifecycle_incomplete start receipt
[PASS] C12b  expected=launch_lifecycle_incomplete        observed=launch_lifecycle_incomplete settle receipt

--- C13: delete hop k and ALL later artifacts; earliest gone hop's code wins ---
  k=0 earliest gone = consumption receipt    expected=launch_consumption_missing   observed=launch_consumption_missing  PASS
  k=1 earliest gone = arm receipt            expected=launch_consumption_invalid   observed=launch_consumption_invalid  PASS
  k=2 earliest gone = pack root              expected=launch_binding_mismatch      observed=launch_binding_mismatch  PASS
  k=3 earliest gone = launch manifest        expected=launch_consumption_invalid   observed=launch_consumption_invalid  PASS
  k=4 earliest gone = window plan root       expected=launch_binding_mismatch      observed=launch_binding_mismatch  PASS
  k=5 earliest gone = start receipt          expected=launch_lifecycle_incomplete  observed=launch_lifecycle_incomplete  PASS
  k=6 earliest gone = settle receipt         expected=launch_lifecycle_incomplete  observed=launch_lifecycle_incomplete  PASS
[PASS] C13   expected=earliest gone hop's code, each k   observed=all 7 match cascade over the 7 orderable hops

--- C14: delete only the .sha256 sidecar ---
[PASS] C14a  expected=launch_consumption_missing (same as C6) observed=launch_consumption_missing consumption receipt sidecar gone
[PASS] C14b  expected=launch_lifecycle_incomplete (same as C12) observed=launch_lifecycle_incomplete start lifecycle receipt sidecar gone

--- C17: move window.env out of the window plan root ---
[PASS] C17   expected=launch_consumption_invalid         observed=launch_consumption_invalid window.env relocated outside the plan root

--- C18: lifecycle receipts and require_completion=False ---
  completion receipt present on disk? False
[PASS] C18a  expected=NO ERROR (completion absent, require_completion=False) observed=NO ERROR
[PASS] C18b  expected=launch_lifecycle_incomplete when completion required observed=launch_lifecycle_incomplete
  start.receipt_kind='launch_start' settle.receipt_kind='launch_settle'
  start.predecessor == consumption ref ? True
  settle.predecessor == start ref      ? True
[PASS] C18c  observed=launch_start/launch_settle chain=True

--- C16: consume the same arm twice ---
  first consume  -> status='CONSUMED'
[PASS] C16   expected=second consume refused             observed=ArmReadinessError:readiness_record_consumed

--- C3/C4: the launch_lineage_required tag decides whether lineage is read ---
  locator published at .../context/claim/.joulewise-launch-lineage.json (exists=True)
[PASS] C3    expected=admitted, lineage None, no LaunchLineageError observed=None untagged bundle whose lineage is broken (start receipt deleted)
[PASS] C4a   expected=LaunchLineageError from the bundle gate observed=launch_lifecycle_incomplete tagged bundle, gone artifact
[PASS] C4b   expected=_read_bundle raises before any evidence row observed=AnalysisInputError: launch_lifecycle_incomplete: bundle-1: launch-lineage receipt is absent

25 probes, 0 FAIL
```

### 6.6 The locator hop (C5), which the first harness omitted

```
$ PYTHONDONTWRITEBYTECODE=1 python3 probes_c5_c15.py
--- C5: the lineage locator, the FIRST hop in the contract's list ---
  locator path: /var/folders/.../context/claim/.joulewise-launch-lineage.json
  locator lives in the runs root, beside the bundle dir? True
[PASS] C5-CF expected=locator present -> authenticated         observed=authenticated counterfactual
[PASS] C5    expected=launch_consumption_missing               observed=launch_consumption_missing locator deleted, everything else intact
  locator sidecar: .joulewise-launch-lineage.json.sha256 (exists=True)
[PASS] C5b   expected=launch_consumption_missing               observed=launch_consumption_missing locator SIDECAR deleted
```

### 6.7 C15 under the corrected method

```
$ PYTHONDONTWRITEBYTECODE=1 python3 probes_c15_fixed.py
scientific_config_identity(cfg) is not None: True

LINK 1 -- is committed_pack_tree_sha256 reached?
  pack root PRESENT -> committed_pack_tree_sha256 called 1 time(s)
  pack root GONE    -> committed_pack_tree_sha256 called 0 time(s)
  return with the pack root gone: frozenset()
[PASS] C15-L1 expected=present: reached; gone: NOT reached, frozenset() observed=present=1 gone=0 ret=frozenset()

LINK 2 -- what an empty declared set produces at the analysis gate
  declared set EMPTY    -> ('consumer_identity_set_unauthenticated',)
  declared set NONEMPTY -> ()
[PASS] C15-L2 expected=empty -> the code; nonempty -> NOT the code
[PASS] C15    observed=both links executed composed from L1 + L2

3 probes, 0 FAIL
```

The superseded first attempt, recorded for the counterfactual lesson:

```
  _frozen_consumer_identity_set with the pack root PRESENT -> frozenset()
  _frozen_consumer_identity_set with the pack root GONE    -> frozenset()
[FAIL] C15b  expected=('consumer_identity_set_unauthenticated',) observed=()
```

### 6.8 The §2 corrections

```
$ grep -n "recorded path\|recorded file" docs/contracts/identity_pin_projection.md
620:  a runs root beside the bundles it governs. The **recorded paths** are the

$ grep -n "launch_lineage_required" docs/contracts/identity_pin_projection.md
653:Only a bundle whose configuration carries `launch_lineage_required` (the

$ grep -n "sibling" docs/contracts/identity_pin_projection.md | sed -n '3p'
601:  the sibling custody directory (a separate custody directory with the same

$ grep -n "exhaustiv" docs/contracts/identity_pin_projection.md
659:following hop list (the named artifact sequence) is not exhaustive of every

$ sed -n '731,734p' docs/contracts/identity_pin_projection.md
The **ordinary launch step** authenticates and replays the arm receipt, pack
digest, launch manifest, and one-use consumption record, as defined in
§Analysis-gate definitions. It does not call

$ sed -n '10,16p' docs/contracts/identity_pin_projection.md
Status: executable contract for
`joulewise.identity_pin_projection_receipt.v1`. The implementation in
`joulewise/identity_pins.py` is authoritative when this text and code differ.
For the launch-lineage sentences in §Analysis consumption,
`joulewise/arm_readiness.py` (the launch-lineage authenticator) and
`joulewise/analysis_engine/inputs.py` (the analysis input loader) are
authoritative when this text and code differ.

$ grep -n '^#\{1,4\} ' docs/contracts/identity_pin_projection.md | sed -n '11,13p'
581:### Analysis-gate definitions
640:### Analysis consumption
730:### What happens after arm
```

### 6.9 Tests

```
$ ls tests/ | grep -i analysis
test_analysis_claims.py
test_analysis_engine.py
test_analysis_finalizer.py
test_analysis_inputs.py
...
(tests/test_analysis_engine_inputs.py does not exist)

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs tests.test_arm_readiness_lifecycle
...........................................................................ss...s.s.
----------------------------------------------------------------------
Ran 84 tests in 127.943s

OK (skipped=4)
```

---

## 7. Recommendation

The contract paragraph is behaviourally correct and I would land it on the evidence.
The blocker is against the landing record's account of its own evidence, and the four
should-fix items are text defects the hand-enumerated table could not have caught.
Suggested disposition: one bounded fix round that (i) rebuilds the first-use table
with a real extractor and corrects the record's description of it, (ii) fixes S1–S3
in the prose, (iii) rules on whether the `:468` and `:572` collateral edits stand,
followed by a delta re-audit of that round only.
