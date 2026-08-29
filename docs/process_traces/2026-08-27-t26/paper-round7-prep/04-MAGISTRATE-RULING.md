# Round-7 retensing plan — magistrate ruling (Fable, 2026-08-29)

Scope: the five NEEDS-RULING items in `00-director-record.md`, raised after
the standing escalation trigger fired (two consecutive pedagogy rounds
failing with the same signature) and the director correctly stopped. The
frozen draft was not edited by anything ruled here; the plan stays HELD
until the rewrite round below runs.

## R-1. Structural cure ADOPTED — built-terms lexicon + first-use lint

The director's proposed cure is adopted as built:
`scripts/paper_terms_lint.py` (lexicon extraction + A/B/C/D variant lint),
`docs/paper/round7/built-terms-lexicon.md` (430 terms), and
`tests/test_paper_terms_lint.py` (unittest, 4 tests).

Magistrate bench verification (2026-08-29, this checkout):

- Lexicon regeneration is byte-identical to the checked-in file
  (deterministic extractor).
- The lint run against the HELD plan returns **74 findings across 88
  sentences** — it mechanically reproduces the two pedagogy seats' failure
  signature (unbuilt or later-built vocabulary inside replacement prose),
  including the exact terms both seats flagged (`phase-dominance`,
  `model-ranking`, `exact conservative outcome`, `floor window`).
- The suite passes; the module is unittest-style and shard-registered.

Acceptance gate for any future edit of the plan's A/B/C/D prose: the lint
exits 0 (every remaining use either first-built earlier in the draft than
the insertion line, or glossed inline at the use site). The lint is a
necessary gate, not a sufficient one — one fresh pedagogy seat still
adjudicates the rewritten plan (single round; a second failure escalates
to a cold instance, not to round three).

## R-2. The rewrite round is DEFERRED until `_v5` pins the vocabulary

The plan's outcome definitions, TERM token table, and model names were
written against `_v4`: Qwen2.5 1.5B/7B, and the item-34 code predicate as
the falsifier. Three rulings landed after the plan was written and change
its content, not just its tense:

- **D-164**: the production pair is Qwen3-1.7B-4bit / Qwen3-8B-4bit and
  the pack is generation `_v5`; every `[TERM_*_1p5B_*]`/`[TERM_*_7B_*]`
  token name and each in-prose "1.5B"/"7B" is superseded.
- **D-165**: the headline falsifier is the pre-registered dominance ratio
  **R ≥ 2** per component per cell, with mandatory common-mode R_cm
  disclosure and the R_cm < 2 withdrawal rule; the coded predicate
  survives only as the cell label. Outcome A/B definitions keyed to "the
  item-34 code predicate is true" are superseded.
- **D-166**: the decode arm is real pinned prompts (Qwen3 chat template,
  thinking off) and the prefill length is fixed from the G2 shakedown
  record; workload prose in the substitution table changes accordingly.

Running the constrained rewrite now would key it to a token namespace
that does not exist yet and force a second rewrite within days. RULING:
the blind writer seat (Sol, lexicon-constrained, lint exit 0 required
before hand-back) runs once, after the `_v5` analysis manifest and fill
registry pin the token names — the same desk block that regenerates
`docs/paper/results-fill-registry.md` for `_v5`. Its brief carries
Ed's writing standard verbatim, the lexicon, and D-164/165/166.

## R-3. Outcome D is a combinable prefix, not a fourth exclusive outcome

The delta seat is right: outcome D states that the identical-condition
null block was not collected (`characterization.run` false). That is
orthogonal to how the contrast itself resolved — the demonstration can
still yield A, B, or C without the characterization campaign. D therefore
composes as a prefix (null-row-absent framing) with the A/B/C contrast
wording, and the composition propagates to H02 and U02. Item 10's current
"D" text survives as the D-prefix's opening sentence. The precedent stands
(item 64's rule): no placeholder prints without a supplier.

## R-4. Item 60 — the duplicated tamper-evidence sentence

The director kept the frozen paragraph's opening scope sentence AND the
ruled replacement sentence; the delta seat correctly observes the
paragraph now states tamper evidence twice. RULING: the paragraph opens
with the D-161 ruled sentence (verbatim, unchanged), followed by one
short scope clause retaining the only idea the ruled sentence lacks:
"It provides internal consistency, not third-party provenance." The
frozen paragraph's original first sentence is dropped. The rest of the
replacement paragraph stands as drafted.

## R-5. U01–U06 APPROVED; census additions included

The six U blocks (future-tense sentences on hazard lines beyond the ruled
29) are approved as round-7 scope — they do not renumber or enlarge the
ruled H set, and leaving them untouched would mix tenses inside otherwise
retensed paragraphs. The two additional future-tense sentences the census
found (draft line 11 transfer sentence; line 264 Holm-family sentence)
join the same scope. All of them are rewritten by the R-2 seat under the
lexicon constraint and D-164/165/166 vocabulary. Draft line 262's
standing-rule sentence stays unchanged, as the plan proposes.

## R-6. Fill-checklist open gaps 1–10

Deferred to the `_v5` registry regeneration (R-2's desk block): the
gaps are keyed to `_v4` cell shapes and supplier names that the `_v5`
manifest replaces. The checklist itself remains valid as the fence/batch
structure; its row table regenerates with the registry.

## Disposition

- #236 merges with the cure landed and the plan still HELD; the HELD
  banner now points at this ruling.
- Kernel bookkeeping: the round-7 prep row (WAVE-ROWS, kernel wave 3)
  gains this ruling as authority; the R-2 rewrite is part of the `_v5`
  desk block, not a separate row.
