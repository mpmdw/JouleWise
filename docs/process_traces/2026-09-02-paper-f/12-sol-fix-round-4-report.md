# Sol fix round 4 report

Date: 2026-09-03  
Branch: `feat/2026-09-02-paper-f`  
Required start: `225afb0c5744734c7196b30a0b304510d2144fb9`  
Observed start: `225afb0c5744734c7196b30a0b304510d2144fb9`

## Scope and protected regions

Only the draft, successor lexicon, first-use ledger test, and this authorized
process-trace report were changed. The Abstract, Section 6's “Printed negative
result,” Section 7's “What the finding changes,” Section 10, the fill registry,
and the Figure 3 SVG were not edited. `git diff --unified=0` shows draft hunks
only at current lines 103–132, 181, 254–258, 360–361, 703–706, 881, and the
first-use ledger/count at 1634–1655 and 1887.

## Findings 1–9

| Finding | Disposition | Implemented cure |
|---:|---|---|
| 1 | Cured | Section 1 now says every joint lower/upper edge choice is evaluated and the largest result retained. The draft ledger, successor lexicon, and `GLOSS_REQUIREMENTS` carry the same selection rule; the mutation regression removes that clause and proves the test fails. |
| 2 | Cured | The Section 3 preamble now distinguishes workload response from the other three questions. The workload-response status cell deletes the referentless fixed-output phrase and states that all outputs are 512 tokens, so this campaign supplies no output-length-fit inputs; the method remains for a later varying-output campaign. |
| 3 | Cured | The Section 1 `U` symbols and their ledger/lexicon forms now use `\mathrm`, matching Section 4. A section-bounded grep finds no `\rm` in Section 1 or Section 4. |
| 4 | Cured | Section 1 assigns “detection floor” to the pre-safeguard resolution bound and “cell floor” to the safeguarded final gate value. The Section 4 gate and the Figure 3 lead-in both now say “cell floor.” |
| 5 | Cured | The repeated Section 4 mentions of resolution bound and cell floor are no longer bold; their first-use home remains Section 1. |
| 6 | Cured | The first-use sentence, draft ledger, successor lexicon, and test now bind the same gloss: “macOS `powermetrics` is the power sampler used here.” The later duplicate gloss was removed. |
| 7 | Cured | The identical-condition status cell says each floor pack schedules one magnitude: decode at 512 output tokens or prefill at a 512-token prompt. |
| 8 | Cured | The manifest/artifact hash gate now begins “Under the current mint”; “mint” is glossed there as the analysis run that issues the paper's fixed results and is ledgered. |
| 9 | Preserved | No registry line offsets were edited. Its content anchors remain untouched, as required. |

## Executed evidence

### First-use audit of every changed reader-facing sentence

The whole-draft mechanical ledger and terms-lint tests scan these sentences in
their current locations. The table records the term-level first-use decision
for each changed sentence; “earlier” means the term's ledgered construction
precedes this sentence.

| Current line(s) | Changed sentence | Technical terms doing work | Build/gloss location | Mechanical result |
|---:|---|---|---|---|
| 103 | Machine-scope sentence now names one `powermetrics` configuration without repeating its gloss. | `powermetrics` | First gloss at 87: power sampler used here. | PASS |
| 103–106 | MLX sentence and transfer-limit sentence were reflowed after the duplicate sampler gloss was removed. | MLX | Same sentence: Apple's on-device inference framework; ledger home §1. | PASS |
| 118–123 | The resolution-bound naming bridge assigns the advisor and artifact names to their stages. | resolution bound; detection floor; cell floor | Same sentence defines the false-difference bound, advisor term, safeguards, and final artifact value. | PASS |
| 124–129 | The component-bound sentence now includes exhaustive joint evaluation and maximum selection. | \(U_{\mathrm{point}}\); \(U_{\mathrm{corner}}\) | Same sentence: recorded-edge component, every allowed joint edge choice, largest retained result. | PASS |
| 128–132 | Both quotient sentences use the unified TeX macro. | independent-movement quotient; shared numerator | Components are built in the preceding and same sentences; only spelling changed. | PASS |
| 181 | The manifest/artifact hash sentence is qualified by the current mint. | mint; manifest; SHA-256 fingerprint | Same sentence glosses mint; manifest and fingerprint are built in the preceding sentence. | PASS |
| 254–256 | Only three characterization questions are said to record later-campaign inputs. | characterization question; frozen calculation | Existing vocabulary built in the preceding §3 question sequence and §2 frozen gloss. | PASS |
| 256–258 | Workload response is named as the exception and no different-output-length measurements are claimed. | workload response; output length | Workload response is the named question above; output length is plain measured input. | PASS |
| 258 | The method is retained for a later campaign. | method; campaign | Plain audience vocabulary already in use. | PASS |
| 360 | Every output is fixed at 512 tokens; the campaign records no output-length-fit inputs. | output-length fit | Same sentence explains it as comparing energy across different output lengths. | PASS |
| 360 | No workload-response report issues; the varying-output method is deferred. | workload-response characterization report | The question and its straight-line method are defined in the row and immediately preceding prose. | PASS |
| 361 | Each floor pack schedules one magnitude, with decode and prefill sizes stated. | floor pack; workload magnitude; decode; prefill | Floor pack at 259–260; magnitude earlier in the same row; decode/prefill in §1. | PASS |
| 361 | Requirements now apply at that one magnitude. | magnitude; comparator floor | Magnitude is defined earlier in the same row; comparator floor at 259–260. | PASS |
| 703–705 | The existing Section 4 resolution-bound definition is de-bolded. | resolution bound | Built at 118–123; this is a later use. | PASS |
| 705–706 | The existing Section 4 artifact-name sentence is de-bolded. | cell floor; same-cell floor | Cell floor built at 118–123; same-cell floor is defined by the following sentence. | PASS |
| 879–883 | The Figure 3 lead-in now sends values clearing the cell floor to the direction gate. | cell floor; magnitude gate; direction gate | Cell floor built in §1; both gates are defined in §4 before this sentence. | PASS |

### Changed ledger and lexicon definitions

| Artifact entry | First-use check |
|---|---|
| `powermetrics` | Exact same first-use gloss is used in draft ledger and successor lexicon; `GLOSS_REQUIREMENTS` binds its presentation-stripped text. |
| resolution bound / detection floor / cell floor | Stage relation matches §1: pre-safeguard resolution/detection bound, post-safeguard artifact cell floor. |
| \(U_{\mathrm{point}}\) / \(U_{\mathrm{corner}}\) | Uses `\mathrm` and includes exhaustive joint evaluation plus largest-result retention. |
| mint | New same-sentence gloss and §2 lexicon/ledger home added. |
| inventory count | Updated mechanically from 251 to 252 after adding `mint`; FAILS remains 0. |

### Requested verification

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
```

Tail:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 2.853s

OK
```

### Canonical suite

The repository's docs/tooling exception applies: this round changes paper
prose, its hand-maintained lexicon, and only the dedicated first-use test, so
the focused paper suite above is the acceptance check. A broad preflight
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` invocation was
started but intentionally interrupted before completion (exit 130); no
canonical-suite result is claimed.

## Notes

- Finding 4 was resolved without changing the out-of-scope Figure 3 SVG; the
  requested draft prose now uses the artifact's final-gate name.
- No commit was created.
