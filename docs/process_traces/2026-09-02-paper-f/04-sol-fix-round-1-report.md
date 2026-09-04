# Paper F fix round 1 — Sol implementation report

## 1. Head and scope

Work started and ended at `a4fcc7acd257e93cbdd95a3f21edb658064c195b` on
`feat/2026-09-02-paper-f`; no commit was made. The implementation touched only:

- `docs/paper/draft-v2-skeleton.md`
- `docs/paper/round7/built-terms-lexicon.md`
- `tests/fixtures/paper_first_use_pre_cure.md`
- `tests/test_paper_first_use_ledger.py`
- this report

`docs/paper/results-fill-registry.md` was inspected but not changed. Its DS-02,
DS-03, DS-05, and DS-06 `_v5` rows already name the frozen characterization
result specification as supplier, and restoring their exact Markdown anchors
removed the only re-anchoring need.

The draft diff is 153 lines: 88 insertions and 65 deletions. The four reserved
regions were selected by heading text, ending at the next peer heading, and
compared as raw bytes with this command:

```sh
python3 - <<'PY'
import hashlib, subprocess
from pathlib import Path
old = subprocess.check_output(['git','show','a4fcc7ac:docs/paper/draft-v2-skeleton.md'])
new = Path('docs/paper/draft-v2-skeleton.md').read_bytes()
bounds = [
 ('Abstract', b'## Abstract\n', b'## 1. Introduction\n'),
 ('Section 6 printed negative result', b'### Printed negative result: short prompt processing has too few overlapping records\n', b'### Demonstration fixed before collection\n'),
 ('Section 7 What the finding changes', b'### What the finding changes\n', b'### Further limitations\n'),
 ('Section 10', b'## 10. Conclusion\n', b'## 11. References\n'),
]
for name, start, end in bounds:
    def cut(data):
        i=data.index(start); j=data.index(end,i); return data[i:j]
    a,b=cut(old),cut(new)
    print(f'{name}: {"BYTE_IDENTICAL" if a == b else "DIFFERS"} bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}')
PY
```

```text
Abstract: BYTE_IDENTICAL bytes=3294 sha256=377ed4cb407324059599dd4d7debcf5e4b5d19de87ad95e1895e5663b3fe7233
Section 6 printed negative result: BYTE_IDENTICAL bytes=1546 sha256=f1bc638319f8fff94f586d536527a658b7152902a73af97451b5d5070863ba2f
Section 7 What the finding changes: BYTE_IDENTICAL bytes=346 sha256=d90804d636b7a6759c9a0601907f1bc9676ffb0994add82d5576d14888c1305d
Section 10: BYTE_IDENTICAL bytes=398 sha256=7eb623ff2ef086e67b4940d90492fe41e39786e71c3d43d4fff52a0ae475ae4a
```

## 2. Finding -> cure table

Line numbers below are the cured files' current lines. “Test” means the hardened
ledger suite, not a new empirical claim.

| Finding | Ruling applied | What changed | New lines | Disposition |
|---|---|---|---:|---|
| B1 | R1 | Restored the cadence-ratio predicate in plain words; printed both code design constants and both production refusal codes. | draft 330–336; test 99–103 | cured |
| B2 | R2 | Replaced the nonexistent “plan calibration entry” with the three mechanisms actually implemented: capture-manifest and member hashes, frozen-plan hash/id against ledger pins, and acceptance digest from the in-code registry. | draft 177; test 70–76 | cured |
| S1 | R4 | Embedded the existing Figure 3 SVG, supplied a complete caption, and removed the stale build instruction. | draft 863–876, 901 | cured |
| S2 | R3 | Restored all four qualifying characterization rows and their exact registry anchors; added the explicit method-only campaign sentence and plain glosses for workload level, magnitude, and per-token conversion. | draft 250–352, 1228–1232 | cured |
| S3 | R5 | Limited `U_corner/U_point` to independent movement and stated the distinct shared/local numerator `U_cmp,shared/U_cmp,point` exactly as Section 4 constructs it. | draft 118–134, 634–655 | cured |
| S4 | R6 | Matcher now joins paragraphs with a source-line map, recognizes selected derivations/dashes/modifiers, binds required gloss words at or before first use, authenticates the real fixture, and includes bite mutations. | test 21, 37–127, 141–160, 303–365, 464–475, 519–594 | cured |
| N1 | scope ruling | Verified this round's diff is wholly inside its exhaustive write scope; the two lead-custody trace files noted by the refuter are baseline history, not this round's writes. | report §1; final `git diff --name-only` | cured/no action required |
| N2 | R7 | Qualified midpoint reference runs with “when present” in the definition and ledger. | draft 187–190, 1648–1649 | cured |
| N3 | fact refuter | Narrowed the four-item list to recorded **claim-bearing** energy terms, so derived aliases are not excluded. | draft 754–756, 1738 | cured |
| N4 | R6 | Declared the successor lexicon hand-maintained and bound its required rows in a regression test so regeneration cannot silently discard them. | lexicon 1–43; test 129–138, 471–475 | cured |
| P-B1 | R4 | Added the Figure 3 embed and exhaustive source-matched caption. | draft 863–876 | cured |
| P-B2 | R3 | Reconciled four questions with four qualifying table rows; bounded the two uncollected methods with the required explicit sentence. | draft 238–352 | cured |
| P-B3 | R7 | Replaced the forward “admission gate” pointer with the ruled plain-language entry-check definition and built “admitted” immediately afterward. | draft 187–190 | cured |
| P-B4 | R7 | Replaced appendix-only check names with physical pass/fail explanations, including both shared work limits; corrected the ledger disposition. | draft 179; ledger 1645 | cured |
| P-B5 | R7 | Built an interpolation edge from samples, straight-line power, allowed gaps, and retained largest energy change before naming the bound kind. | draft 819–828 | cured |
| P-B6 | R6 | Replaced per-line matching with paragraph/table-row joined search and a per-character line map; added the real wrapped-compound case. | test 141–160, 244–339, 519–549 | cured |
| P-S1 (row 1) | R7 | Defined the A/B/B/A block before using “member of that block”; both naming sentences remain physically compact. | draft 129–134 | cured |
| P-S2 (row 16) | R7 | Replaced “widening factor” with its operand and physical purpose: the point-only value is multiplied by a fixed factor to allow limited repetition. | draft 413–419 | cured |
| P-S3 (row 22) | R7 | Split the nested resolution-bound appositive into two sentences while preserving the resolution/detection/cell-floor relation. | draft 118–120 | cured |
| P-S4 (matcher forms) | R6 | Added admission/admitted, freeze/frozen, resolvable/not-resolvable, U+2010–U+2013 dash, line-wrap, and inserted-modifier cases without a general stemmer. | test 37–47, 178–205, 208–225, 519–549 | cured |
| P-N1 (plan) | R2 | Built “reservation plan” as the file naming reserved collection slots at first use. | draft 177 | cured |
| P-N2 (mean idle power, rows 10/18) | refuter disposition | Retained the phrase: the refuter adjudicated it as audience vocabulary, and the sentence already states the exact multiplication and subtraction. | draft 198–200 | left-with-reason |
| P-N3 (power counter) | writing standard | Replaced the loose “power counter” with “power sampler,” already physically defined. | draft 102–106; first definition 87–90 | cured |
| P-N4 (headings skipped) | R6 | Kept heading exclusion: the test inventories technical prose/table uses, while exact section homes are separately validated; treating a section title as a prose definition would create false passes. | test 303–315, 444–462 | left-with-reason |
| P-N5 (`$` math form) | R6 | Did not add a special matcher for a notation form absent from the draft; LaTeX terms used here are covered by their ledger alternatives. | test 178–225 | left-with-reason |

### Clause map delta (R1–R7)

| Clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| R1 cadence eligibility | draft 330–336 | `GLOSS_REQUIREMENTS["sampling flags / cadence ratio"]`, test 99–103 and `test_required_gloss...` 464–469 | Removing either fixed-multiple definition or either constant fails the gloss test. |
| R2 capture-manifest custody | draft 177 | custody fragments at test 70–76 | Replacing the artifact/fingerprint list or capture-record comparison loses a required fragment. |
| R2 reservation-plan custody | draft 177 | custody fragments at test 70–76 | Restoring an invented plan calibration entry loses the reserved-slot and ledger-pin fragments. |
| R2 acceptance digest | draft 177 | custody fragment at test 75 | Removing the in-code registry source loses a required fragment. |
| R3 four qualifying questions | draft 347–352; registry 822–833 | anchor and named-supplier comparison in §4 below; term/gloss assertions at test 93–103 | The registry-to-table supplier relation is inspection-pinned, not directly unit-pinned; a future registry row change requires re-running that inspection. |
| R4 Figure 3 | draft 863–876; SVG 1–92 | Figure/custody/measured-contrast gloss assertions at test 121–126; source census in §3 | Removing the explanatory paragraph fails; embed presence and the visual census remain inspection-pinned. |
| R5 shared numerator | draft 122–134, 634–655 | U-row fragments at test 63–66 | Reusing `U_corner` for shared movement removes the distinct-numerator fragment. |
| R6 search and gloss binding | test 37–127, 141–365 | regression methods at test 519–594 | Wrapped, derivational, en-dash, modifier, real-pre-cure, and deleted-gloss counterexamples each exercise the matcher. |
| R7 first-use repairs | draft 118–120, 129–134, 179, 187–190, 413–419, 486–491, 819–828 | required fragments at test 52–127 and mutation test 568–594 | Deleting the package-power or retired-calculation gloss is caught; all listed rows must remain in the declared first-use home. |

## 3. Figure 3 element census

The SVG itself was read as source because it is outside this round's write
scope. Every drawn element is named by the paragraph and caption at draft
863–876; no drawn element was omitted.

| SVG element | SVG lines | Caption/legend coverage |
|---|---:|---|
| accessible title and description | 2–3 | title, subtitle, two gates, four outcomes, refusal inlet, no measured data |
| reusable arrowhead | 5–9 | each arrow is named with direction and label |
| white background; visible title and subtitle | 11–14 | “white background,” “title and subtitle,” no data/numeric threshold |
| dashed refusal-input rectangle | 17–20 | dashed box; admission/custody failure; all six defects: missing, stale, contaminated, duplicated, inconsistent, unauthenticated |
| refusal arrow and its side-entry label | 22–23 | right-pointing arrow; reaches no gate |
| bordered refused outcome and its two-line consequence | 25–28 | bordered “refused” box; evidence produces no result |
| pale horizontal separator | 30–31 | pale horizontal rule separates lanes |
| gray measured-contrast input box | 34–38 | gray box; point estimate plus composed uncertainty interval |
| input-to-Gate-1 arrow | 40 | right-pointing arrow to first box |
| white rounded Gate 1 box and question | 43–47 | first white rounded box; magnitude versus cell detection floor |
| Gate-1 yes arrow | 49–50 | “yes” arrow to Gate 2 |
| white rounded Gate 2 box and question | 53–56 | second white rounded box; whole interval points one way |
| Gate-2 yes arrow | 58–59 | next “yes” arrow |
| blue directional-claim outcome | 61–65 | blue box; both gates pass in registered direction |
| Gate-1 downward no arrow | 67–69 | downward “no” arrow |
| not-resolvable outcome and explanation | 71–75 | effect smaller than instrument resolves; not zero/equality/no difference |
| Gate-2 downward no arrow | 77–79 | downward “no” arrow |
| direction-unresolved outcome and explanation | 81–85 | floor clears; interval does not settle direction; no claim |
| three bottom annotation lines | 87–92 | physical floor definition; two separate gates; sum is planning disclosure, not acceptance threshold |

## 4. §3 relocation record for R3

The registry contains four `_v5` characterization rows whose status text names
the frozen characterization result specification as supplier. Therefore all
four questions qualify to stay in the table:

| Question kept | Registry row and named supplier | Restored draft anchor |
|---|---|---:|
| workload response | DS-02, frozen characterization result specification | 349 `**Workload response:**` |
| identical-condition null | DS-03, frozen characterization result specification | 350 `**Identical-condition null:**` |
| phase accounting | DS-05, frozen characterization result specification | 351 `**Phase accounting:**` |
| drift and recovery | DS-06, frozen characterization result specification | 352 `**Drift and recovery:**` |

No current member of the stated four-question set was moved, because none lacks
a qualifying named supplier. DS-04 (deliberate small-difference challenge) and
DS-07 (between-session stability) are not members of that four-question table
and were not reintroduced. The exact bounding sentence at draft 250 is:

> This campaign does not collect workload-response or identical-condition characterization; the method for them is stated so a later campaign can apply the already frozen calculations.

That sentence implements Outcome D's method-only status while leaving the
registered calculations available to a later campaign. Because the exact
DS-02/03/05/06 anchors are restored, no DS-02..DS-06 registry edit was needed.

## 5. Executed evidence

### Mechanical first-use audit over every changed reader-facing sentence

Every changed reader-facing sentence belongs to one range below. Rows marked
“earlier” use a term only after its already adequate definition; rows marked
“same” introduce the defining words before or at the technical name. The
end-of-draft ledger was then brought into agreement with these homes.

| Changed sentence range | Technical words doing work | First use | Built/glossed | Result |
|---:|---|---:|---:|---|
| 102–106 | Apple M3 Max / 128 GB; `powermetrics`; power sampler | 102; 87 | 102–104; 87–90 | earlier/same |
| 118–120 | cell; resolution bound; detection floor; cell floor | 118; 119; 120; 120 | 118–120 | same |
| 121–134 | `U_point`, `U_corner`; independent quotient; shared numerator; A/B/B/A block; member; timing-error/shared/local sign | 122–134 | 122–134 | same |
| 177 | declared machine state; instrument-validation manifest; reservation plan; calibration ledger; calibration-acceptance file; frozen | 177 | 177 | same |
| 179 | signal/fit/range/trace-coverage/completeness checks; shared search-work limits | 179 | 179 | same |
| 187–190 | entry check; reference runs; admitted | 187; 189; 190 | 187–190 | same |
| 250–257 | workload-response characterization; independent unit; slope; fitted residual; timing half-width | 250–256 | 247–257 | earlier/same |
| 330–336 | sampling flags; cadence ratio; phase rate; fixed minima; refusal codes | 330–336 | 330–336 | same |
| 349 | workload level; timing half-width; per-token conversion | 349 | 349 | same |
| 350 | workload magnitude; interval of allowed differences; comparator | 350 | 259–277, 350 | earlier/same |
| 351 | phase accounting; resolution/floor bands; shared/member-local timing; flags | 351 | 317–336 | earlier |
| 352 | drift allowance; held-out probes; cooldown exit; settling convention | 352 | 238–248, 338–345 | earlier |
| 413–419 | retired calculation; equal-rate anchor; corner maximum; point-only value; fixed limited-repetition factor | 414–418 | 414–419 | same |
| 486–491 | point-only unguarded bound; admitted energy; small-sample multiplier; independent units | 486–490 | 486–491 | same |
| 754–756 | claim-bearing energy terms and four members | 754–756 | 754–756 | same |
| 819–828 | deterministic bound; interpolation edge; deterministic-bound kinds | 819–825 | 819–828 | same |
| 863–876 | Figure 3; admission failure; custody; measured contrast; magnitude/direction gates; four outcomes; visual marks | 863–876 | 863–876 | same |
| 1228–1232 | workload level | 349 | 349; local reminder 1229 | earlier |

The removed “Build Figure 3” sentence is an editorial deletion and introduces
no term. The ledger changes are audit metadata rather than reader-facing
method sentences. The automated gloss table at test 52–127 binds the defining
words for every first-use cure above, including the two factual cures.

### Cured draft: required ledger test

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
```

```text
..........
----------------------------------------------------------------------
Ran 10 tests in 1.315s

OK
```

### Real pre-cure fixture: expected red direction

The fixture is the exact byte stream from
`git show 33290b8b:docs/paper/draft-v2-skeleton.md`, not constructed prose:

```sh
shasum -a 256 tests/fixtures/paper_first_use_pre_cure.md
```

```text
04e78ec457bb4005ad4e135bad8894f29b4f6c0b45325b7c38874d5c1745ce89  tests/fixtures/paper_first_use_pre_cure.md
```

```sh
PAPER_FIRST_USE_DRAFT=tests/fixtures/paper_first_use_pre_cure.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_required_gloss_is_present_by_first_use_paragraph
```

```text
First list contains 29 additional elements.
First extra element 0:
'Apple M3 Max / 128 GB unified memory: required ledger row is missing'

----------------------------------------------------------------------
Ran 1 test in 0.021s

FAILED (failures=1)
```

That nonzero exit is the required red result. In addition,
`test_real_pre_cure_fixture_violates_hardened_ledger` authenticates this fixture
and requires failures for package power, retired calculation, and entry check,
with at least eight total failures. `test_gloss_checks_bite_when_cures_are_removed`
deletes the package-power and retired-calculation definitions from copies of
the cured draft and requires the hardened checker to name each deletion.

### Paper test family

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'
```

```text
............
----------------------------------------------------------------------
Ran 75 tests in 614.010s

OK (skipped=3)
```

`git diff --check` also returned no output and exit 0.

## 6. Lexicon updates

The successor lexicon now records the cured first-use homes and definitions for
the machine and sampler; the independent and shared numerators; the five
custody objects; the five pulse checks and shared work limits; entry/admission;
workload level, magnitude, and per-token conversion; cadence ratio; retired
calculation; small-sample multiplier; claim-bearing energy terms; interpolation
edge; measured contrast; custody; and Figure 3. The split measured-contrast and
first-order-balance rows prevent the figure prose from falsely re-homing the
latter. The generic word “manifest” was removed from the appendix release-row
alternative so the earlier instrument-validation manifest is not hidden.

The file's header identifies the additions as hand-maintained, and
`test_successor_lexicon_is_regeneration_protected` requires both that marker and
the critical rows.

## 7. Open items / anything not cured

There are no blocking or should-fix items left. Three pedagogy nits remain by
design and are recorded in §2: “mean idle power” is already plain language with
its operation stated; headings remain excluded from prose matching; and the
draft has no `$...$` math syntax requiring another matcher variant. Figure 3's
embed and exact visual census, and the registry-to-table supplier relation, are
inspection-pinned rather than directly unit-pinned; both inspections passed in
this round.
