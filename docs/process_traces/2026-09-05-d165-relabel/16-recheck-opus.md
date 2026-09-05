# 16 — Fresh non-author counter-review (contract + pedagogy), Opus

Scope: `feat/2026-09-05-d165-relabel` @ `aaa5dc8e`, read-only in
`/Users/edr/code/JouleWise-wt-d165-relabel`. Base `origin/main` = `df657492`.
Authority: ruling 17 §B, D-165 paragraph
(`docs/process_traces/2026-09-04-peer-audit/17-magistrate-final-ruling.md:86-95`).

## VERDICT: LANDABLE — 0 blockers, 3 should-fix, 5 nits

The ruled semantics are implemented, the registry is consistent, the census is
green, and the merge consequences are bounded. Every should-fix is a residue or
a scope gap, not a wrong number or a false claim.

---

## 1. CONTRACT

**v2 active; v1 accepted only for historical bytes — CORRECT.**
`joulewise/dominance_closeout.py:167-171` splits the constant into
`LEGACY_COMMON_MODE_REPLAY_RULE_ID` (.v1), `COMMON_MODE_REPLAY_RULE_ID` (.v2),
and the accepted pair. Era selection is by *producer declaration*, never by
result labels: `:1165` `sidecar_rule_id = value.get("rule_id",
LEGACY_...)`, with the comment at `:1162-1163` recording the rationale (the
original three-field shape declares v1). The absolute rationale is bound to the
declared era at `:1172-1176`, so a v2 body cannot be read with v1 wording.

**No re-issue path, no silent acceptance.** `build_d165_replay_sidecar:858` and
`replay_common_mode_dominance:989` both write v2 unconditionally, so no producer
can emit v1; a v1 artifact is only ever *read*, never re-minted (its bytes are
digest-sealed in the manifest, so a rebuild is a new artifact, not a re-label).
The four hostile directions are all closed and tested: v2 body with the top-level
declaration stripped → 4 × `d165_replay_rule_era_mismatch`
(`tests/test_d165_dominance_closeout.py:519-524`); all results downgraded to v1 →
4 errors (`:508-517`); mixed eras per cell, both directions → exact single error
per cell (`:474-506`); v2 sidecar carrying the legacy absolute reason → refused
(`:541-548`); v1 sidecar round-trips byte-identically (`:459-472`).

Executed: `R7F_CORPUS_ROOT=... python3 -B -m unittest
tests.test_d165_dominance_closeout` → `Ran 59 tests in 9.700s / OK`.

**Refusal enumeration intact — verified verbatim.** The diff touches zero lines
of `D165_CLOSEOUT_REFUSAL_ENUMERATION` (`:46-88`): `git diff origin/main...aaa5dc8e
-- joulewise/dominance_closeout.py | grep -c '^[+-].*REFUSAL_ENUMERATION\|^[+-] *"[A-Z_]*":'`
→ `0`. See nit N1 on the new refusal's code.

**Registry consistent — counted both sides.**

```
                              origin/main   aaa5dc8e
table rows (^| `[…)              126          126
row-token multiset md5     17e2b126…4da5b  17e2b126…4da5b   (identical)
SUPPLIER_PENDING                  5            0
```
No row dropped, added, or reactivated. All four comparative R_cm rows name
`d165_shared_sign_local_corner_replay.v2` as supplier and lost the
`SUPPLIER_PENDING` clause; all four absolute R_cm rows carry
`not_applicable` + the registered comparative-only rationale (see S2 on how two
of them carry it). `grep -rn SUPPLIER_PENDING` outside `process_traces` → no
hits repo-wide.

**Registration pin verified by hand.** `sha256` of
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`
= `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265`, exactly
`joulewise/night_gate.py:31`; the superseded digest is recorded in the comment at
`:29-30` and appears nowhere else in tracked non-trace files.
`tests.test_night_gate` → `Ran 47 tests / OK`. The generator now imports
`ABSOLUTE_COMMON_MODE_REASON` instead of duplicating the literal
(`generate_configs.py:39,551`) — one home, good.

### S1 (should-fix) — the production module's own docstring still states the withdrawn reading, and the census cannot see it

`joulewise/dominance_closeout.py:1-6`:

> "The comparative common-mode replay keeps one **shared timing-error sign**
> across all A/B/B/A blocks…"

This is the superseded physical-common-time reading, unmarked, in the file the
contract names the sole production home — and it directly contradicts
`replay_common_mode_dominance`'s own cured docstring 860 lines below
(`:874-878`, "shared energy signs … no proven conservatism for common-time
motion"). It survives because `RETIRED` in
`tests/test_d165_rationale_census.py:35-47` lists `"shared timing error"`
(spaced) while the docstring writes `timing-error` (hyphenated). Executed probe
replicating the census normalisation over lines 3-6: **`no hits`**. The same
blind spot would pass any future `common-time` → `common time`, or
`shared timing-error` anywhere. Fix: cure the docstring, and add the hyphen
variants to `RETIRED` (or fold `-` to space before matching).

### S2 (should-fix) — two of the four absolute R_cm registry rows point at the rationale instead of stating it

`docs/paper/results-fill-registry.md`: the two decode rows print the rationale in
full ("a uniform additive energy offset cancels from absolute residuals; no
absolute common-time replay is implemented; …"), while the two prefill rows say
only "Literal `not_applicable` **plus the registered comparative-only
rationale**". A filler reading a prefill row cannot rebuild the denial from the
row; and the asymmetry inside one table reads as an oversight. The likely cause
is census economy (each spelled-out row needs an allowlist entry; entries 10-12
cover exactly the prose line plus the two decode rows). Under the binding writing
standard this is the "no word does unpaid work" failure — the phrase "the
registered comparative-only rationale" carries the whole denial. Fix: spell out
all four, and allowlist the two added lines.

### S3 (should-fix) — the paper-facing and close-out validators are era-blind

`validate_d165_paper_sources:464-465` and `validate_d165_closeout` (via
`_source_precondition_errors:1980-1982`) accept *any* registered era. Executed
probe: a fully v1-shaped sidecar (no top-level `rule_id`, legacy absolute reason,
v1 result ids) returns `validate_d165_replay_sidecar(...) == []` → `True`. The
close-out object has no era field (`_CLOSEOUT_TOP_KEYS:252-266`), so a close-out
licensed under the *withdrawn* v1 semantics is indistinguishable at close-out
level from a v2 one; the era is recoverable only by opening the sealed sidecar
bytes. Meanwhile the registry now asserts v2 as the supplier of every comparative
R_cm fill. Ruling 17 §B licenses v1 only to "preserve v1 meanings/bytes", i.e. to
*validate* historical artifacts — not to license new sentences.
Mitigations that hold this below blocker: rebuild is stopped for this submission;
all eight R_cm registry rows are `RETIRED_FALLBACK` with "no submission
placement", so no R_cm value can reach the paper; the sidecar bytes are
digest-sealed by the manifest, so the era is not lost, only not surfaced.
Fix (cheap): assert v2 in `validate_d165_paper_sources`, or record the sidecar's
declared era in the close-out.

---

## 2. PEDAGOGY

The eleven cured occurrences span eight lines (draft 4, ledger 2, generator 1,
SVG 1) and I read every one. **They pass the first-use test.** Every cure
replaces a term of art with a physical operation a reader can rebuild: "It does
not replay the same timing shift in every block or prove that its limit covers
the effect of such a shift" (`draft-v2-skeleton.md:156-157`);
"This within-block construction does not replay the same timing shift in every
block" (`:396`); "no proof that its limit covers the effect of the same timing
shift in every block" (`:810`); the two ledger glosses (`first-use-audit-ledger.md:137-138`).
No retired term is used, and no new term of art is introduced: "limit" is already
built in the draft ("pulse-derived limit" `:97`, "moved-edge limit" `:140`) and
`U_cmp,shared` is defined as "its largest limit" two sentences before the §1 cure
(`:151-152`), so "its limit" has a proximate antecedent.
`tests.test_paper_first_use_ledger` → `Ran 11 tests / OK`.

**Figure A4 text matches its generator, exactly.** Extracted the `y="392"` text
from `figA4_shared_signs.svg`, XML-unescaped it, and compared against the
`ast.literal_eval` of the `t(s,30,392,…)` argument in
`build_mechanism_figures.py:80`: **MATCH: True** (118 chars; the SVG's only
difference is `&#x27;` for the apostrophe). **Legible:** Helvetica AFM width sum
at 15 px puts the right edge at **771.5 px** on a 1000 px canvas (x=30), i.e.
*narrower* than the line it replaced (807.0 px) and than the y=60 line (768.7 px);
baseline y=392 on height 425 leaves room for descenders. No overflow, no
re-layout needed.

---

## 3. CENSUS

`R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest
tests.test_d165_rationale_census -v` → **`Ran 8 tests in 7.612s / OK`** (8/8).

Allowlist `tests/fixtures/d165_rationale_allowlist.json`: **38 entries**, every
one with a nonempty reason. I read all 38. Classification:
- 15 = corrected *denial* sentences (the new rationale itself contains
  "common-time" because it denies an absolute common-time replay) — contract 42/46,
  campaign pack 127/141, registry 262/277/293, fill-checklist 63/207/215/223/231,
  the registration JSON, and `dominance_closeout.py:182,874`;
- 9 = explicit historical v1 rule-token citations, each paired in-line with the
  active v2 authority (contract 115/210, fill-checklist 143, structural-edits
  86/88, `dominance_closeout.py:167`);
- 3 = the `# LEGACY v1 BEGIN/END` block bytes (`dominance_closeout.py:176`);
- 9 = paragraphs under a dated `**SUPERSEDED 2026-09-05**` banner that says in
  terms "retained for custody and must not be inserted as active paper text"
  (retensing-plan ×7, structural-edits ×2);
- 2 = the unrelated Figure-2/A2 drift-schematic captions (draft-v1:61,
  draft-v2:1459), where "common-time line" names a line in an ABBA drift diagram.

**No entry reads as a wording escape hatch.** The two caption entries are the only
ones whose reason is "unrelated" rather than "superseded/denial"; I verified both
captions and the reason is accurate (see N2). The marker mechanics are themselves
tested — `test_markers_are_bounded_and_do_not_hide_following_active_text`,
`test_bare_v1_authority_is_active_even_beside_v2`,
`test_exact_allowlist_does_not_exempt_other_lines_phrases_or_files` — so a banner
cannot silently swallow live text. The one real gap is the phrase list, not the
allowlist: see S1.

---

## 4. CONSEQUENCES OF THE TWO MAIN MERGES

**supply_map re-anchors are confined to the `d165_closeout` role.**
`git diff origin/main -- configs/paper_supply/supply_map.json` = exactly four
lines: `d165_closeout/inventory.json` `c6db071e…` → `57f28f30…` and
`d165_closeout/inputs/validator_receipt.json` `00b1bb95…` → `b9949937…`. No other
role, gate, or census entry moves. Re-anchor verified live:
`tests.test_paper_custody` → `Ran 29 tests in 38.804s / OK`, with
"KILLED 109 owner-source mutations and 5 grant-policy mutations: stale receipts
refused".

**paper-M draft unchanged except the cured lines.** `git diff origin/main --
docs/paper/draft-v2-skeleton.md` = three hunks, four content lines, all three
D-165 denial sentences (`:156-157`, `:396`, `:810`). Nothing else in the draft
moved.

---

## 5. NITS

- **N1** — `d165_replay_rule_era_mismatch` has no entry in
  `D165_CLOSEOUT_REFUSAL_ENUMERATION`; inside a close-out it is wrapped as
  `d165_replay_sidecar_invalid: …` (`:1982`), which matches no registered code, so
  `_closed_refusal_code:368-385` collapses it to the fallback
  `closeout_input_malformed: source.census_or_block_membership` — a wrong-cause,
  professor-facing code. Pre-existing for *all* sidecar-invalid errors, not
  introduced here, so: nit.
- **N2** — Figure A2's caption (`draft-v2-skeleton.md:1459`) uses "common-time
  line" for a drift-schematic element two appendices from the D-165 text that
  retires "common-time" as a term of art. Correctly allowlisted and genuinely a
  different object, but same word / two meanings in one document is a reader trap;
  renaming it "equal-midpoint line" would end the collision permanently.
- **N3** — `docs/paper/round7/fill-checklist.md:58` still labels the item "the
  common-mode sensitivity disclosure" — retired vocabulary, unglossed, in a live
  instruction a filler follows. (The paper draft itself contains zero occurrences
  of "common-mode": `grep -n` → none. Internal doc only.)
- **N4** — Both `fill-checklist.md:61` and `docs/campaign_packs/d117_contrast_v5.md:139`
  name the Python constant `ABSOLUTE_COMMON_MODE_REASON` inline in prose. Harmless
  because the text follows immediately, but it is code identity leaking into
  reader-facing wording.
- **N5** — The cures introduced two very long unwrapped lines
  (`draft-v2-skeleton.md:810`, `results-fill-registry.md:262`) in files otherwise
  wrapped near 80 columns. Cosmetic; noted only so the next diff is readable.

## Evidence appendix — commands run (all read-only, one target at a time)

```
git rev-parse HEAD                                        aaa5dc8e…
git diff --stat origin/main...aaa5dc8e                    40 files, +2755 −94
unittest tests.test_d165_rationale_census                 Ran 8 / OK
unittest tests.test_d165_dominance_closeout               Ran 59 / OK
unittest tests.test_night_gate                            Ran 47 / OK
unittest tests.test_paper_first_use_ledger                Ran 11 / OK
unittest tests.test_paper_custody                         Ran 29 / OK
sha256(d166_dominance_criterion_registration.json)        dfe55f8d… == night_gate.py:31
registry row count / token md5 / SUPPLIER_PENDING         126=126 / equal / 5→0
v1-sidecar validate probe                                 [] (accepted)
census-normalisation probe over dominance_closeout.py:3-6 no hits
figA4 SVG text vs generator literal                       MATCH: True; right edge 771.5 px < 1000
```
