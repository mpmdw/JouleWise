# Paper F fix round 2 — Sol implementation report

## Scope and disposition

Work began at `9448bac5881d93af14a3245303e857381fa9d4e2` on
`feat/2026-09-02-paper-f`. No commit was made. The draft, successor lexicon,
and this report are the only modified paths. The results-fill registry was
read but not changed because it is outside `WRITE_SCOPE`.

The Abstract, Section 6 printed-negative-result region, Section 7 “What the
finding changes,” and Section 10 remain byte-identical to `HEAD`. This preserves
the line-78 `named-counter boundary` text even though the wording instruction
also asks to change it: line 78 lies inside the explicitly excluded Abstract
range owned by another seat. The lead must rule whether that one phrase should
be changed by the Abstract owner or returned in an expanded subregion scope.

## Finding → cure

Line numbers are from the completed files.

| Finding | Cure | Lines | Disposition |
|---|---|---:|---|
| R3-final: the characterization table included two methods not collected by the `_v5` transaction. | Removed the workload-response and identical-condition rows from the table. The table now contains only phase accounting and drift/recovery. | draft 373–376 | cured |
| R3-final: moving the two rows must not discard their method or orphan registry anchors DS-02/DS-03. | Moved every method, basis, and refusal sentence into the existing paragraph beginning “This campaign does not collect.” Preserved the exact anchors `**Workload response:**` and `**Identical-condition null:**` once each. Added plain-word definitions for the interval and mean interval at their new earlier first uses. | draft 250–276 | cured |
| B2: the capture field was named `manifest_sha256`, which is not the strict-physics calibration field. | Replaced it with `validation_manifest_sha256`, matching `joulewise/reduce.py`'s strict-physics read. | draft 177; `joulewise/reduce.py` 1219 inspected | cured |
| B2: professor-facing prose carried maintenance-fragile `file:line` citations. | Kept file/function attribution but removed line locators from the custody, cadence, and Student-*t* sentences. The only remaining `.py:line` strings are in HTML source comments, not reader-facing prose. | draft 177, 362, 691–696 | cured |
| Wording: “power-counter boundary” and “counter cell” conflicted with the built term. | Standardized the editable prose and ledger definitions on **power-measurement boundary** and recorded the term in the successor lexicon. | draft 119, 719–720, 1706, 1758; lexicon 17 | cured in authorized regions |
| Wording: the same requested change at line 78 conflicts with the Abstract exclusion. | Preserved the Abstract bytes; no out-of-region edit was made. | draft 78 | needs lead ruling |
| Moving bold anchors into prose exposed them to the ledger's bold-introduction closure check. | Added ledger rows for both anchors and increased the mechanical inventory from 248 to 250 terms. | draft 1710–1711, 1898 | cured |

## Executed evidence

### Mechanical first-use audit of every changed reader-facing sentence

The shipped ledger matcher was run over the completed draft. For each changed
sentence group below, every technical word doing work is either built earlier
or glossed in the same paragraph. Literal field/reason names and file/function
citations are code identifiers, not newly coined paper terms. Ledger and
lexicon table edits are audit metadata; their definitions are nevertheless
listed in the final two rows.

| Changed sentence(s) | Technical words doing work | Mechanical first use | Built/glossed | Result |
|---:|---|---:|---:|---|
| draft 177, three custody sentences | declared machine state; instrument-validation manifest; reservation plan; calibration ledger; calibration-acceptance file; frozen | 177 | 177 | same paragraph |
| draft 250–254 | workload response; token generation; workload level | 250; 95; 254 | 250–254; 95–97; 254 | earlier/same |
| draft 255–263 | admitted bundle; timing half-width; cell floor; per-token conversion | 247; 258; 120; 261 | 247–248; 258; 118–120; 261–262 | earlier/same |
| draft 263–268 | identical-condition null; A/B/B/A block; workload magnitude; interval of allowed differences | 263; 129; 265; 267 | 263–265; 129–131; 265–266; 267–268 | earlier/same |
| draft 268–276 | mean interval; comparator; frozen ladder; disjoint evidence | 269; 241; 271; 273–274 | 269–270; 241; 177; plain words at use | earlier/same |
| draft 360–362 | sampling flags; cadence ratio; fixed multiples; refusal names | 356 | 356–362 | same paragraph |
| draft 691–696 | two-block fixture; Student-*t* critical; fixed-table value | 649; 183; 693 | 649–655; 183; 693–696 | earlier/same |
| draft 719–720 | same-cell floor; power-measurement boundary | 719; 119 | 719–720; 118–120 | earlier/same |
| draft ledger 1706, 1710–1711, 1758 | cell; workload response; identical-condition null; same-cell floor | 118; 250; 263; 719 | matching reader-facing rows above | metadata agrees |
| lexicon 17 | cell; power-measurement boundary | 118; 119 | draft 118–120; lexicon row itself | earlier/same |

The matcher also reported these relevant exact first-use locations:

| Term | First line | Ledger status |
|---|---:|---|
| workload level | 254 | glossed-at-first-use |
| per-token conversion | 261 | glossed-at-first-use |
| workload magnitude | 265 | glossed-at-first-use |
| interval of allowed differences | 267 | glossed-at-first-use |
| mean interval | 269 | glossed-at-first-use |
| sampling flags / cadence ratio | 356 | glossed-at-first-use |
| same-cell floor | 719 | glossed-at-first-use |
| cell | 118 | glossed-at-first-use |

### Requested test command

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
```

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 2.544s

OK
```

`git diff --check` returned no output and exit 0.

### Protected-region byte check

```text
Abstract: BYTE_IDENTICAL bytes=3294 sha256=377ed4cb407324059599dd4d7debcf5e4b5d19de87ad95e1895e5663b3fe7233
Section 6 printed negative result: BYTE_IDENTICAL bytes=1546 sha256=f1bc638319f8fff94f586d536527a658b7152902a73af97451b5d5070863ba2f
Section 7 What the finding changes: BYTE_IDENTICAL bytes=346 sha256=d90804d636b7a6759c9a0601907f1bc9676ffb0994add82d5576d14888c1305d
Section 10: BYTE_IDENTICAL bytes=398 sha256=7eb623ff2ef086e67b4940d90492fe41e39786e71c3d43d4fff52a0ae475ae4a
```

## NEEDS_RULING

- **Question:** Does the explicit request to change draft line 78 override the
  same prompt's exclusion of Abstract lines 23–80?
- **Options considered:** leave the protected Abstract byte-identical; or let
  the Abstract owner change `named-counter boundary` to
  `named power-measurement boundary`.
- **Recommendation:** keep this seat out of the Abstract and have its owner make
  the one-phrase change, or resume this seat with that exact subregion added.
- **Blocked work:** only the line-78 wording unification; all authorized fixes
  and requested tests are complete.
