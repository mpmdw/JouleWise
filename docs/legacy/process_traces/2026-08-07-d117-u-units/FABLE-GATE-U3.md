# APEX DIFF GATE — U3 (PR #112, merge d6683bf): pinset v2 + authenticated four-cell generalized floor mint

Gate instance: cold Fable, no loop context. Evidence base: full read of the merged
code (`scripts/mint_floor_artifact_generalized.py` 3400 lines, `scripts/floor_mint_pinsets/schema_v2.json`,
the `joulewise/detection_floor.py` diff, the ledger/acceptance authentication chain in
`joulewise/calibration_ledger.py` and `joulewise/calibration_bracketing.py`), plus the final
reports of U3-AUDIT-CONTRACT, U3-AUDIT-EXEC, U3-DELTA-VERDICT, U3-DELTA2-VERDICT
(transcripts in `docs/process_traces/2026-08-07-d117-u-units/`). U4 (cdb7896) did not touch
these files; working-tree state equals the U3 merge state.

## VERDICT: SOUND-WITH-DEBT

The charged security class — fabricated custody pins minting silently — is genuinely
closed: every one of the nine postcollection fields is equality-compared against
independently constrained evidence, and the delta-2 refuter reproduced the original
fabrication scenario to a named per-field refusal. Composition invariants (max-never-sum,
armwise, allowance-once, retired-literal refusal, v1 byte parity) hold on my own reading.
What remains is structural debt of three kinds: a trust-model claim that must not be
overstated (Finding 1), a two-stage freeze whose second half is convention (Finding 2),
and a three-way hand-synchronized encoding of the pinset shape that has already drifted
once (Finding 3). None of these makes the merge wrong; all of them bound what the
artifact may honestly be said to prove.

---

## Question 3 first, because it decides what the artifact means

**What authenticates the evidence?** The chain, traced to its root:

- The pinset file is authenticated against a SHA-256 **supplied by the operator** on the
  command line (`--pinset-sha256`, `load_pinset` at mint script :1118-1153).
- Component evidence (reports, specs, manifests, bundles) is authenticated by the v1
  core's rederivation checks against source bundles — internal consistency, strong.
- The calibration-acceptance artifact is pinned by an **exact byte hash committed in
  code** (`joulewise/calibration_bracketing.py:431-464`).
- The ledger head pin must byte-match `git show HEAD:<pin-path>` **of the local
  checkout** (`calibration_ledger.py:761-776`, enforced at :1281-1290 and :2454), and
  the receipt chain must hash-link to that head.
- `project_commit` and `project_tree_state` in the artifact's provenance are **operator-
  supplied CLI strings**, checked only for shape (mint script :2430-2433, :3304-3307;
  inherited unchanged from the v1 tool, `mint_floor_artifact.py:1511-1512`). The mint
  never runs git to learn its own commit.

**Plain answer: the root is NOT outside the operator's reach.** The git pin is the local
HEAD; an operator who can run the mint can also commit a forged ledger, forged head pin,
and edited acceptance-hash constant to their local checkout, and every check passes.
The structure therefore does not reduce to *nothing*, but it reduces to exactly this:

1. **Against honest-operator error** (wrong file, stale drift value, transposed hash,
   retro-fitted literal) the mint is now a hard, named-reason gate. This is the failure
   mode that actually occurs in this project, and it is well covered.
2. **Against a dishonest operator** the mint alone proves nothing. What it buys is
   *tamper evidence conditional on external audit*: fabrication now requires forging a
   self-consistent committed history (ledger chain + head pin + acceptance constant +
   the pinset), and that forgery must survive review of what is pushed to authoritative
   main. The pre-fix state let fabricated hashes mint with **no** committed trace; the
   post-fix state forces the forgery into the audited history. That is a real, material
   elevation — and it is the correct design for a single-operator research instrument.

**Consequence for claims language:** the artifact is *operator-attested with
machine-checked internal consistency and git-anchored tamper evidence*. It must never be
described as machine-verified provenance or operator-independent custody. Two cheap
hardenings would close most of the residual gap: (a) derive `project_commit`/
`project_tree_state` inside the mint via git instead of trusting arguments (~15 lines);
(b) record in the artifact whether the ledger head pin's commit is contained in
`origin/main` at mint time, so post-hoc audit is one field-check instead of an
archaeology session. The trust boundary is stated once, in a comment at
`calibration_ledger.py:~640-647` — it belongs in the artifact and the claims doc, not
in a comment.

---

## Ranked findings

**F1 — HIGH (trust model, see above).** Not a code defect; a meaning boundary. Remediation:
the two hardenings above plus a `trust_model` statement in whatever claims surface cites
this artifact. Professor-facing surfaces (advisor plain-language rule) must carry it.

**F2 — HIGH: the two-stage freeze has no stage linkage.** The desk-stage
`pin_requirements.v2` exists **only** as `$defs.pinRequirements` in `schema_v2.json`.
No Python anywhere parses, validates, or even opens a desk-stage file — the sole code
touchpoints are the constant at mint script :44 and the refusal at :1149-1150. Nothing
ever compares a final pinset against the desk file it supposedly resolves. The entire
commitment value of a two-stage freeze — pins declared *before* collection cannot be
retro-fitted *after* — is enforced by nobody in code; it is a git-history diff a human
must remember to perform. Worse, the desk stage's structural incapability holds only
for files that honestly self-declare the desk `schema_version`; since no tool validates
desk files at desk time, a "desk freeze" written with the final schema_version is simply
a final pinset and nothing would notice until audit. Remediation: a `verify-desk-freeze`
entry point (~120 lines: closed desk-schema check + field-by-field comparison of every
desk-frozen pin against the final pinset), run as a mandatory pre-mint step — or an
explicit written ruling that stage linkage is a review obligation, so it lands on a
checklist instead of in the gap.

**F3 — HIGH (structural): three hand-synchronized encodings of one shape, one of which
is dead.** The v2 pinset shape is encoded in (1) `schema_v2.json`, 919 lines; (2) the
mint parser `_parse_v2_pinset` + helpers, ~375 lines (:594-968); (3) the consumer
projection `_project_floor_mint_pinset_v2`, ~440 lines (`detection_floor.py:1640-2010`).
The JSON schema is **never executed**: jsonschema is not a project dependency (D-009,
`tests/test_schemas.py:34-37`), no test validates any instance against it, its only
runtime appearance is being *skipped by filename* (`detection_floor.py:2038`), and its
only test appearance asserts that two `const` strings differ
(`test_mint_floor_artifact_generalized.py:1528-1537`). The exec audit's finding 3
(mint and shared validator disagreeing on closure) was this drift plane realized once
already; it was fixed by hand-resynchronization, which is not a fix of the plane.

**Answer to gate question 2:** as merged, the schema's discriminating power is **zero in
practice** — every actual refusal comes from the Python parsers. If it were executed it
would refuse most shape errors (22 closed objects, 24 consts, 23 required lists — it is
a competently written schema), but it cannot express the load-bearing invariants: the
producer self-hash arithmetic, custody-record uniqueness across cells, the allowance
rule `max(observed, 0.010818)`, six-decimal↔full-precision consistency, or any
cross-field equality. Those live only in Python. So it is well-made ceremony: a
five-decade-honored way to look rigorous while enforcing nothing. Either arm it (an
optional-jsonschema test validating the synthetic final fixture and a desk fixture,
~40 test lines — recommended, since AUDIT-MINT names a field inventory as ground truth)
or delete it and let the field inventory be the reference.

**F4 — MEDIUM (new ground): consumer plan-attribution loosening.** `_validate_comparative`
changed from exact equality against the artifact's plan sha to *set membership* across
all producer plans (`detection_floor.py` diff, `block["calibration_plan_sha256"] not in
calibration_plan_sha256s`). For a v2 multi-plan artifact, a cell minted under plan A
validates with comparative blocks attributed to plan B. The mint itself cannot produce
such an artifact (order-manifest plan sha is checked per cell at mint script
:2236-2245), but `joulewise.detection_floor.validate_floor_artifact` is the shared
claim-ingestion gate, and it now accepts cross-producer attribution in hand-supplied or
corrupted artifacts. Bounded (both plans are legitimately pinned) but it is precisely
the class of attribution slack this project refuses elsewhere. Remediation: bind each
cell to its producer's plan sha in the validator (the cell's provenance already binds
evidence_root_id; ~20 lines).

**F5 — MEDIUM (known finding; extent verified): cardinality is hardcoded at ~12 sites
across all three encodings.** Exactly two producer plans (mint :609; consumer
`len(producers) != 2`; schema min/maxItems), exactly decode+prefill with fixed metric
strings and precheck paths (mint :753-768; consumer role→metric map), exactly four
cells/groups (mint :867-870), aggregate exactly two component artifacts and four
allowlists (mint :909, :934), and the ABBA block size 4 baked into the comparative
member-count multiplier in **both** mint (:1632-1636) and consumer
(`expected_n * (1 if absolute else 4)`). A third model, a third phase, a single-plan
mint, or any MoE/spec-decode cell (the P3 research axes) requires a v3 schema plus
coordinated edits in three files. Under the paper-first ruling P3 is sacrificable, so
this is *acceptable* debt — but it contradicts the standing modularity preference and
must be recorded as a deliberate casualty, not discovered later as a surprise.

**F6 — LOW: fix-round accretions.** (a) `_consumer_family_pins` called twice on the same
value with one result discarded (mint :953-963). (b) `first_cell_artifact =
cell_artifact` (:2508) binds the **last** cell; correct only because every copied field
is producer-invariant — the name asserts something false. (c) Dead check at :2138:
`records[0] != records[1]` compares records parsed from byte-identical report files
(both hashes must equal the same pin at :2123-2129) — cannot fire. (d) Hardcoded
`Path("pinset.json")` at :2604 in an expected-value dict whose `relative_path` member is
then explicitly excluded from comparison — the aggregate provenance `relative_path` is
effectively unvalidated and the literal is misleading. (e) `_fresh_original_core()`
re-executes the 876-line v1 module from disk ~15 times per mint.

**F7 — LOW: rendering-rule ambiguity.** `_verify_six_decimal_rendering` (:356-376)
checks Decimal `quantize(ROUND_HALF_EVEN)` of the full-precision *string* (a float
repr), which is not identically float `.6f` formatting of the underlying binary64 at
exact-half boundaries (shortest-repr vs full binary expansion). The v1 core's own
literal check is the operative end-to-end guarantee, so this is a nit — but the repo
should state once which rendering rule is normative.

---

## Question 1: is 2614 lines proportionate? Prune list

Judgment: the invariant set is genuinely large (custody chain, two-stage refusal, four
cells × two components, v1 byte parity, no-derive, exclusive write), and the house style
is deliberately closed-fisted — most individual functions are fine. The module as a
whole is at the outer edge of holdable; the **three-encoding structure is past it**.
Roughly 400-450 Python lines plus the 919-line schema carry no distinct catch surface.
The overbuild-prune gate was owed and would have caught items 1-2 below.

| # | Prune | Est. effect |
|---|---|---|
| 1 | Extract ONE closed-shape v2 validator into `joulewise/` (package can't import scripts/, but scripts can import the package); mint parser and `_project_floor_mint_pinset_v2` both consume it | −~350 net lines; kills the drift plane that already bit once |
| 2 | `schema_v2.json`: arm it (optional-jsonschema fixture test, +~40 lines) **or** delete it (−919) | drift plane armed or removed |
| 3 | Hoist `_v2_authenticate_bracket_binding` from per-cell (4×) to per-producer (2×); postcollection gate compares pins to the cached result | −~30 lines, half the ledger walks |
| 4 | Collapse triple allowlist equality (parse-time :957-967 + construction + binding-validation :2700-2724) to two layers | −~40 lines |
| 5 | F6 items a-d | −~15 lines, one falsehood removed |
| 6 | Cache the configured core per pin-tuple instead of re-executing the v1 file from disk | runtime only |

Net: mint script 3400 → ~2900; `detection_floor`'s v2 addition ~440 → ~80 (thin
projection over the shared validator); schema either armed or gone.

## Question 4: two-stage freeze

"Structurally incapable of minting" is **genuinely enforced for self-declared desk
files**: `load_pinset` refuses the desk schema_version by name (:1149-1150), and I
could not construct a desk-shaped file that mints — the final parser's closed 22-key
postcollection object means completing a desk file into mintability *is* writing a full
final pinset. The desk `postcollection` is `{"status": "unresolved"}` by schema, which
cannot satisfy the final shape. But the *freeze* — final must match desk — is enforced
by convention only (F2), and the self-declaration is itself unpoliced at desk time.

## Question 5: consumer (detection_floor.py +542)

- **Max-not-sum preserved**: cell `floor_gate = max(floor_abs, floor_cmp)`
  (`detection_floor.py:1056`, untouched); v2 projection independently requires
  `operative_full == max(absolute_full, comparative_full)` and
  `applied == max(observed, 0.010818)`; mint enforces the same at :588-591, :560-563.
- **Armwise rule preserved**: cross-stack combination remains `max(...)` in
  `joulewise/analysis_engine/__init__.py:221-233` (`_combined_floor`), untouched by
  this diff. No new path sums floors.
- **Cardinality hardcoded**: yes, and in the consumer too — extent in F5. The projection
  requires exactly 2 producers, 2 cells each, decode+prefill, 4 unique cell/group ids,
  ABBA ×4 multiplier.
- **Regression found**: F4 (plan-attribution set-membership loosening) is the one place
  the consumer change *weakened* an existing check.

## Question 6: what the contract+execution lenses structurally missed

Both prior lenses worked the charge sheet (can a desk file mint; are pins compared;
does anything derive a literal) and worked it well — the delta-2 CLEAN on the
authentication class is corroborated by my own reading of `_v2_gate_postcollection`
(:2055-2187) and `_v2_authenticate_bracket_binding` (:1779-1984). New ground found here
that neither lens reported: **F2** (no desk→final linkage — they only tested whether a
desk file can mint), **F3 stated plainly** (the schema is dead code — the contract lens
treated it as an enforcement surface; the exec lens observed drift without naming the
cause), **F4** (consumer attribution loosening), **F6a-e**, and the operator-attested
`project_commit`/`tree_state` component of F1 (delta-2 acknowledged the git-boundary
limitation but not that the provenance commit itself is a trusted CLI argument).

## Recommended disposition

Merge stands. Debt items to queue, in order: F1 hardenings (git-derived provenance
fields + upstream-containment record + trust-model language on every claims surface),
F2 desk-freeze verifier or explicit ruling, F3/prune-1-2 as one consolidation unit
before the next pinset schema change (doing it after a v3 fork doubles the cost), F4
one-line-class validator fix, F5 recorded as a deliberate P3 sacrifice in the decision
log. F6/F7 fold into the consolidation unit.
