# Pin census for editing `docs/paper/draft-v2-skeleton.md`

Read-only audit from `/Users/edr/code/JouleWise-wt-paper-n-ref` (detached at
`dbe6c675`, tree of `origin/main`). Every line number below is from that
checkout. Draft length at audit time: **1459 lines**. Baseline state verified
this session:

```
scripts/check_paper_replay_fence.py --literals-only     -> rc 0, LITERALS 22, INTERNAL MISMATCHES 0
scripts/check_paper_round7_artifacts.py --literals-only  -> rc 0, R7F PLACED 0/4,
                                                            R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0
select_outcome_branches.py --check-rendered <draft>      -> rc 0, abstract_words=246, limit=250
python -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
  tests.test_paper_successor_migration tests.test_paper_comparison_placements
  tests.test_paper_build                                 -> 63 tests, OK (15.9 s)
docs/paper/build/check_markdown.py <draft>               -> rc 0, Hard defects: 0, Images checked: 9
```

**Headroom warning up front: the Abstract has 4 words of slack (246/250).**

---

## 1. Constraint table

Format: constraint -> enforcer (file:line / function) -> what it literally pins
-> how to update it legitimately.

### 1.1 Abstract / Conclusion / Discussion fixed sentences (`select_outcome_branches.py`)

| # | Constraint | Enforced by | What it pins (literal) | Legitimate update |
|---|---|---|---|---|
| A1 | Abstract headline sentence, verbatim, **exactly once in the whole visible draft** | `docs/paper/fill-rehearsal/select_outcome_branches.py:15-19` `ABSTRACT_HEADLINE`; checked at `:67-76` in `validate_methods_draft`; driven by `tests/test_select_outcome_branches.py:56`, `tests/test_paper_successor_migration.py:105,116-122`, `tests/test_paper_terms_lint.py:301-302` | `"In a current-method re-analysis of one historical GPU (graphics-processor) pulse capture, all 59 fitted onsets occur after their commands and 49 of 59 fitted offsets occur before them; transfer of its timing allowance to inference remains untested."` — compared after `" ".join(section.split())`, so **line wrapping is free, every other character is not**. Must live between `## Abstract\n` and `## 1. Introduction`, and its normalized count over the whole visible text must be exactly 1 | Edit the constant in `select_outcome_branches.py:15-19` **and** the copy in the draft in the same commit. `tests/test_paper_terms_lint.py:301` reads the constant, so both move together. Nothing else needs changing. |
| A2 | Conclusion headline sentence, verbatim, exactly once | same file `:20-25` `CONCLUSION_HEADLINE`; `:67-76` | `"The current-method re-analysis places all 59 fitted onsets after their commands and 49 of 59 fitted offsets before them in the historical GPU pulse capture. Transfer of its timing allowance to inference remains untested."` Must sit between `## 8. Conclusion\n` and `## 9. References` (draft lines 923-926) | as A1 |
| A3 | Discussion transfer limitation, **exactly once inside §5** | `select_outcome_branches.py:26-28,77-80`; also `tests/test_paper_terms_lint.py:214-219` asserts `draft.count(...) == 1` over the **whole file** | `"Transfer of the pulse-derived timing allowance to inference was not tested."` — this one is matched **without whitespace normalization**, so it must be on one physical line inside §5 | Edit `TRANSFER_LIMITATION_SENTENCE` and the draft together; keep exactly one occurrence file-wide |
| A4 | Abstract word budget ≤ 250 | `select_outcome_branches.py:13` `ABSTRACT_WORD_LIMIT = 250`, `:36-48` `_abstract_word_count` / `_check_abstract_word_budget`; tests `tests/test_select_outcome_branches.py:25-28`, `tests/test_paper_successor_migration.py:105,120-122` | Whitespace-split token count of the text between `## Abstract\n` and `\n## 1. Introduction` **after HTML comments are stripped** (`_reader_facing_text`, `:29-33`). Current value **246**. Both delimiters must occur exactly once in the visible text | Raising the cap is a doctrine change (edit `:13` + the two tests' literals). **Do not.** Rewrite within 250. HTML comments are free — they do not count. |
| A5 | Forbidden "moved" prospective material | `select_outcome_branches.py:59-62`; mirrored in `tests/test_paper_terms_lint.py:558-562` | The visible draft must **not** contain: `"## 3. Instrument characterization"`, `"Two directional comparisons—"`, `"### Measured admission rules"`, `"Under D-173,"`, `"revision\n`3b1b1768"`, `"The registered minimum basis is forty"`, `"The prospective design"` | Never reintroduce. These live in `docs/paper/protocol/prospective-comparison-protocol.md`. |
| A6 | Protocol citation count | `select_outcome_branches.py:57-58`; `tests/test_paper_terms_lint.py:556` | `"(protocol/prospective-comparison-protocol.md)"` — exactly once in visible text | If you move the citation, move it; never duplicate |
| A7 | Figure 2 locator count | `select_outcome_branches.py:81-82` | `"(figures/fig4_edge_excursions.svg)"` — exactly once | as A6 |
| A8 | No reader-facing FILL and no retired FILL anywhere | `select_outcome_branches.py:63-66`; `tests/test_paper_terms_lint.py:332-343` | `"[FILL:"` must not appear in **visible** text (comments are exempt); `re.search(r"\[FILL:(?:DS-\|PG-\|OB-\|OR-\|R_\|V5-)")` must not match **even inside HTML comments** | The only FILL in the draft is `<!-- [FILL:PE-01] SYNTHETIC appendix placement; no measured value is issued. -->` at draft line 1415. **It must stay inside an HTML comment.** |
| A9 | Editorial ledger stays out of the article | `select_outcome_branches.py:55-56`; `tests/test_paper_terms_lint.py:557` | `"## First-use audit ledger"` must not appear in visible text | The ledger lives in `docs/paper/protocol/first-use-audit-ledger.md` |
| A10 | No outcome branches | `select_outcome_branches.py:52-53`; `tests/test_paper_terms_lint.py:344` | `"OUTCOME-BRANCH"` absent from the **raw** text | never reintroduce |

### 1.2 §4 replay fence — IEEE-754-exact numerals (`scripts/check_paper_replay_fence.py`)

Everything here is anchored by a **regex that must match exactly once** in the
whole draft (`_search`, `scripts/check_paper_replay_fence.py:120-124`). A moved,
split, or reworded sentence fails closed with `FenceError`.

| # | Constraint | Enforced by | Literal pin | Legitimate update |
|---|---|---|---|---|
| R1 | The worked-arithmetic paragraph is **one physical line** | `check_paper_replay_fence.py:148-153` (`_paragraph` reads to the next `\n`) | Heading regex `^([*]{1,2}Worked (?:historical\|current)-capture arithmetic\.[*]{1,2}) ` — one match across both spellings. Draft line **588** is the whole paragraph on a single line | Never wrap it. Never duplicate the heading (`tests/test_paper_replay_fence.py:99-102` proves a duplicate raises) |
| R2 | Pulse count | `:155-158` | `reports all \(59\) pulses detected` — `\(122{,}859\)`-style LaTeX thousands separators are stripped by `_number` (`:135-138`) | Re-derived from primary bytes; not editable |
| R3 | Evaluated-rectangle count | `:159-163` | `\(122{,}859\) evaluated rectangles` | as R2 |
| R4 | Clock-anchor bound | `:164-168` | `a local clock-anchor bound of \(0.0011349971959968978\) s` — compared with `float(literal) == value`, **full 17 digits, no rounding** (`:544-547,556-571`) | as R2 |
| R5 | Capture bound | `:169-171` | `a final capture bound of \(0.030067931757111657\) s` | as R2 |
| R6 | The subtraction and its two operands | `:173-181` + `check_draft_internal_identities` `:282-312` | `largest pulse residual before the anchor term is \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s`. The minuend must be **character-identical** to R5, the subtrahend **character-identical** to R4, and the printed result must be the exact `decimal.Decimal` difference | as R2. Rounding any of these three breaks the identity check even with no corpus present |
| R7 | Maximal-pulse ordinal word | `:183-187` + `:579-585` | `the pulse attaining the maximum: the tenth commanded pulse` (`ORDINAL_WORDS[PULSE_INDEX+1]`, `:91-104`) | as R2 |
| R8 | Planned offsets | `:189-195` | `scheduled to switch on \(26.625\) s and off \(27.625\) s` | as R2 |
| R9 | Command epochs | `:197-203` | `commands were stamped at \(1784757381.2856488\) s and \(1784757382.293089\) s of wall time` | as R2 |
| R10 | Onset residual interval | `:205-211` | `onset lag anywhere in \([0.02544938965763524,\,0.02893293456111476]\) s` | as R2 |
| R11 | Offset residual interval | `:213-219` | `offset lag anywhere in \([-0.008607394549133255,\,-0.005308621075866744]\) s` | as R2 |
| R12 | Best-fit pair (**the one rounded pair**) | `:221-227` + `:573-577` | `about a best-fit pair of \(+0.027\) s and \(-0.007\) s` — compared as `f"{value:+.3f}" == literal`, i.e. **exactly three decimals with an explicit sign** | Only this pair may be rounded, and only to `+.3f` |
| R13 | Retained residual bound | `:229-233` | `those four endpoints allow — \(0.02893293456111476\) s, the upper end of the onset interval` — note the **em dash with surrounding spaces** is part of the anchor | as R2 |
| R14 | The five-row clock-stamp table | `_extract_stamp_table` `:249-279` | Header **verbatim**: `\| Stamp \(s\) \| \(W_s\) (s) \| \(M_s^-\) (s) \| \(M_s^+\) (s) \| \(R_s\) (s) \|` (draft line 576). Exactly **5** data rows, each with **5** cells, each row label a backticked code span. Order must equal `joulewise.uncertainty_evidence.STAMP_ORDER`: `` `pre_spawn` ``, `` `first_parse` ``, `` `sampling_started` ``, `` `sampling_stopped` ``, `` `post_parse` `` (draft lines 578-582), asserted by `tests/test_paper_replay_fence.py:104-109` | These five identifiers **cannot** be moved out of §4. Dropping a row raises `FenceError` (`tests/test_paper_replay_fence.py:120-127`) |
| R15 | Stamp-resolution caption | `:237-244` | `the wall clock's \(1.0\times10^{-6}\) s against the monotonic clock's \(...\times10^{...}\) s` — scientific-notation form is parsed into `Xe±N` and float-compared | as R2 |
| R16 | Exactly 22 extracted literal keys | `tests/test_paper_replay_fence.py:67-92` | the named set; an added or removed anchor changes the set and fails | Adding a fenced value means adding an extractor in the script, a key to the test set, and a derivation |

### 1.3 Round-7 DX fence (`scripts/check_paper_round7_artifacts.py`)

| # | Constraint | Enforced by | Literal pin | Legitimate update |
|---|---|---|---|---|
| D1 | **228 retired identifiers must be absent from the entire draft, HTML comments included** | `check_retired_placement` `scripts/check_paper_round7_artifacts.py:958-971`; `tests/test_paper_round7_artifacts.py:404-413` (`assertEqual(len(checks), 228)`); CLI regression `:474-484` proves `<!-- DS-32 -->` fails | Identifier-shaped sites match with `(?<![\w-])…(?![\w-])`; bracketed sites (`[VALUE]`, `[PREFILL_LENGTH]`, `[R_cm_8B_decode_cmp]`, `[TERMINAL_REFUSAL_REASON_*]`, …) match literally with `*` -> `[^\]\s]*`. The retired set includes **`DX-002`, `DX-014`–`DX-017`, `DX-020`–`DX-027`**, `DG-001`, `DG-043`–`DG-056`, `DG-060`–`DG-064`, `DG-078`–`DG-101`, all `DS-01`–`DS-33`/`DS-08a`, `PG-01`–`PG-08`, `OB-01`, `OR-01`, `V5-G2A-001`, `V5-WL-005` | Never cite a retired locator. Only `DX-001`, `DX-003`, `DX-010`–`DX-013` are live (draft lines 639-640). Beware en-dash ranges: writing `DG-043–050` **does** match `DG-043` |
| D2 | `[FILL:PE-01]` appears **exactly once in the file and exactly once inside `### A.6 …`** | `check_appendix_placement` `:974-990`; `tests/test_paper_round7_artifacts.py:217-230`; also `tests/test_paper_terms_lint.py:23-45,156-173` | Heading regex `^(#{2,6}) A\.6(?=\s\|$)` must match exactly once (draft line 1413 `### A.6 Synthetic partial-record enclosure`), and the section runs until the next `^#{1,3} ` heading (draft line 1455 `### A.7 …`). Marker at draft line **1415**, inside an HTML comment | Keep the marker in A.6, inside a comment, once. To retire or re-home it you must edit the `| PE-01 — Appendix A.6 …` registry row in `docs/paper/results-fill-registry.md` and the two tests |
| D3 | **Zero** `[FILL:DX-nnn]` markers in the draft | `check_placement` `:1000-1028`; `tests/test_paper_round7_artifacts.py:418-423` (`assertEqual(len(comparisons),1)` and `_placed_row_count == 0`) | While the DX standing sentence head is absent, the census collapses to a single "0 `[FILL:DX-` markers" comparison. **The head is the curly-quoted string** `“The following are diagnostic-era instrument statistics` (`:126` `DX_STANDING_SENTENCE_HEAD`, U+201C leading). Draft line 595 deliberately starts `The following are diagnostic-era instrument statistics` **without** the curly quote, so the bounded DX prose region is inert | **Do not add the opening curly quote to draft line 595.** Doing so activates `check_placement` for DX-010/011/012/013 and `check_prose_literals`, immediately failing four comparisons. If a future seat really wants DX prose custody, it must add all four `[FILL:DX-0nn]` markers and update the pinned census counts |
| D4 | Comparison census is pinned at **412 / PLACED 0/4** | `tests/test_paper_round7_artifacts.py:1444-1448` (`"R7F PLACED 0/4"`, `"R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"`) and `:1504` (`len(digest_comparisons) == 412`) | Draft-derived share verified this session: retired placement 228 + appendix placement 1 = **229**; skeleton literals 0; prose literals 0; placement non-matches 0. Registry/artifact/figure share = 183 | Adding **any** `[FILL:DX-nnn]` to the draft adds a `check_skeleton_literals` comparison and breaks the `412` literal in two tests. Adding a registry retirement changes 228. Any such change is a paired test edit |
| D5 | If a `[FILL:DX-nnn]` ever is placed, the rendered value must follow it | `check_skeleton_literals` `:830-869`, `_has_immediately_preceding_marker` `:899-904` | Exact literals: DX-010 `+13.0 ms`, DX-011 `−5.5 ms` (U+2212 minus), DX-012 `59 of 59`, DX-013 `49 of 59` | n/a while D3 holds |
| D6 | `### One diagnostic reconstruction` heading and its second paragraph | `tests/test_paper_round7_artifacts.py:1334-1336,1357-1363` (fixture `_real_shaped_dx_region` splits on the heading, then takes the **second** `\n\n`-separated block and asserts it contains a phrase) | Heading `### One diagnostic reconstruction` (draft line 572) must exist; the paragraph immediately after it (draft line 574) must contain `"The following table and arithmetic reconstruct one retained diagnostic capture"` | Keep the heading text and keep that phrase as the opening paragraph of the section |
| D7 | Appendix section used by the same fixture | `tests/test_paper_round7_artifacts.py:1354` | `skeleton.split("### A.6 ", 1)` must succeed — i.e. the heading is spelled with a trailing space and matches the registry's `Appendix A.6` | as D2 |

### 1.4 First-use ledger (`tests/test_paper_first_use_ledger.py`)

The ledger itself is `docs/paper/protocol/first-use-audit-ledger.md` (265 rows).
The audited body is the draft + protocol, with HTML comments blanked
line-for-line (`_strip_comments_preserving_lines`, `:213-214`).

| # | Constraint | Enforced by | Literal pin | Legitimate update |
|---|---|---|---|---|
| L1 | **Every ledger term's FIRST occurrence must fall inside its declared home section** | `test_first_occurrence_is_in_exact_home_section` `:543-563`, via `_first_occurrence` `:386-390` and `_section_for_line` `:477-482` | `home` is the **heading text** of a `##`/`###` heading (regex `^(#{2,3})\s+(.+?)\s*$`, `:37`), e.g. `Abstract`, `1. Introduction`, `Bracketed pulse-train algorithm`, `A.3 Formal calibration algorithms`. Matching folds case, plurals, possessives, hyphen/space/en-dash joins (`_alternative_pattern` `:259-295`) and **joins wrapped paragraph lines** (`_search_blocks` `:315-351`) | Move the text, then edit that row's `First reader-facing home` cell in `docs/paper/protocol/first-use-audit-ledger.md`. Home counts at audit time: `A.3 Formal calibration algorithms` 67, `Bracketed pulse-train algorithm` 39 (all of §2), `1. Introduction` 34, `Abstract` 13, §4 subsections 15 total (`Evidence validity` 2, `One diagnostic reconstruction` 4, `Historical current-method edge result` 3, `Record support in two historical model stacks` 6) |
| L2 | 55 terms must carry a **verbatim defining phrase** in the first-use paragraph (9 of them in the first-use **sentence**) | `GLOSS_REQUIREMENTS` `:54-156`, `SENTENCE_GLOSS_TERMS` `:167-177`, `_gloss_failures` `:397-438`, test `:565-570`; re-run over the assembled article at `tests/test_paper_successor_migration.py:124-128` | e.g. `"detection floor"` needs all three of `registered operational resolution guard for assigned-energy differences`, `the detection floor in the advisor's terminology`, `the artifacts call the final gate value after those safeguards the cell floor`; `"powermetrics"`/`"sampler"` need `macOS powermetrics is the power sampler used here` **in the same sentence**; `"package power"` needs `summed CPU, GPU, and neural-engine power` | Move the term and its gloss together. If you want to change the wording, edit the tuple at `tests/test_paper_first_use_ledger.py:54-156` and the draft in the same commit |
| L3 | Three cure paragraphs are pinned **byte-for-byte including line breaks** | `test_gloss_checks_bite_when_cures_are_removed` `:682-709` | Must be present verbatim in draft+protocol: `"its duration times its largest recorded **package power**—the summed CPU, GPU,\nand neural-engine power—bounds what may be missing."`; `"A **best-fit lag** is fitted edge time minus its matching command time."`; `"lower-or-upper edge choice for that component is evaluated jointly and the\nlargest result retained."` — **the embedded newline positions are part of the pin** | Rewrapping any of these three lines fails the test. To rewrap, edit the mutation literal at `:684-699` too |
| L4 | Ledger row count sentence | `test_ledger_shape_statuses_and_count` `:494-521` | The ledger must contain exactly one `Terms inventoried: N; FAILS: M.` (currently `Terms inventoried: 265; FAILS: 0.`, ledger line 289) and `N` must equal the parsed row count, `M` the count of `FAILS` rows. ≥ 60 rows; no duplicate Term cells; no duplicate alternatives; statuses ∈ `{built-before, glossed-at-first-use, audience-vocabulary, forward-pointer-next-paragraph, FAILS}` | Adding or deleting a ledger row means updating that sentence in the same commit |
| L5 | **Every bold phrase of ≥2 lexical words in the draft must be a ledger term** | `test_bold_multiword_introductions_are_in_ledger` `:591-611` | Any `**…**` outside headings and table rows whose display text has ≥2 alphabetic tokens must casefold-match a ledger term alternative (`" / "`-split) | **New emphasised prose is the easiest way to break this.** Either avoid `**bold**` in new sentences, or add a ledger row (and bump L4's count) |
| L6 | Seven ledger rows have pinned homes and pinned disposition substrings | `:523-541` | `not resolvable` -> home `Record support in two historical model stacks`, disposition contains `insufficient record support`; `measurement interval` -> `Benchmark and metrology lineage`; `statistical measurement interval`, `decision interval` -> `Directional comparison`; `deterministic bound` -> `Adding publication safeguards after the ratio`; `model/stack` -> `Record support in two historical model stacks`; `The clock model` -> `A.3 Formal calibration algorithms`. Plus `local half-width / shared sign` disposition contains `Section 3 constructs`, and the body must contain `prompt processing and token generation are this paper's two phases` (casefolded, whitespace-joined) | These specific homes are structural; moving them is a doctrine change |
| L7 | Successor lexicon rows | `test_successor_lexicon_is_regeneration_protected` `:585-589` against `docs/paper/round7/built-terms-lexicon.md` | Nine rows including `\| powermetrics \| §1 \|`, `\| mint \| §2 \|`, `\| entry check \| §2 \|`, `\| admitted \| §2 \|`, `\| workload level / workload magnitude / per-token conversion \| §3 \|`, `\| interpolation edge / deterministic-bound kinds \| §4 \|`, `\| measured contrast / custody / Figure 3 \| §4 \|`; plus the string `binds this hand-maintained successor table` | If a §-home genuinely changes, edit the lexicon row and this tuple |
| L8 | Pre-cure regression fixture is byte-frozen | `:20-21,665-667` | `tests/fixtures/paper_first_use_pre_cure.md` sha256 `04e78ec457bb4005ad4e135bad8894f29b4f6c0b45325b7c38874d5c1745ce89` | Do not touch the fixture |

### 1.5 Draft-body pins in `tests/test_paper_terms_lint.py`

This is the densest single file of draft literals. All paths relative to the
repo root; `SUCCESSOR_DRAFT` = the draft (`:18`).

| # | Constraint | Enforced by | Literal pin | Legitimate update |
|---|---|---|---|---|
| T1 | Title line | `:208-211` | `# JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon` (draft line 7) | also pinned in `docs/paper/results-fill-registry.md` (`:265-269`) |
| T2 | Eleven **forbidden** strings | `:220-234` | `largest false`, `same timing error moved together`, `uniform shared shift cancels`, `straight line joining those samples`, `claim-bearing **energy terms**`, `2.776445`, `4.808944`, `95/95`, `BUILD AFTER CAMPAIGN AND TRANSFER FIDUCIAL`, `the headline remains conditional on it`, `the floor packs set A = B` | never reintroduce |
| T3 | Twelve **required** constructions in draft+protocol, several with **pinned line breaks** | `:236-262` | e.g. `"A\nshared sign is one choice applied across all blocks"`, `"The measurand is energy assigned to each phase by\n**interval-overlap allocation**: each sampling record's energy is divided"`, the five-line `"Its \\(\\pm10\\)-ms two-edge timing\nenvelope is [8.8, 9.2] J, …"` block, `"For native interval-average records, the reducer integrates constant reported power\nover the overlap duration; …"`, `"Using the\ncode's fixed three-decimal lookup-table convention, \\(t_{.975,4}=2.776\\)"`, `"We apply Holm at nominal family-wise level 0.05 to two\nmodel-based tests; …"` | **Rewrapping these paragraphs fails.** If you must rewrap, update the literal at `:236-260` |
| T4 | `registered timing domain—the edge movements fixed before collection` occurs **exactly twice** in the draft | `:270-275` | count == 2 | preserve both |
| T5 | `[FILL:` count ≥ 1; `[FILL:TR-01]` absent | `:212-213` | the PE-01 comment is the only one | keep it |
| T6 | DG-071/DG-075 statistics echoed in the draft | `:319-330` | `120.9186 ms`, `5.9508 ms`, `120.9224 ms`, `5.8949 ms` must each appear in the draft; they are re-read from `docs/paper/round7/dg071-dg075-statistics.json` (sha256 `9a4fdd…c3a7`) | **These four-decimal millisecond numerals may NOT be rounded in the main text** |
| T7 | Four forbidden strings | `:344-347` | `OUTCOME-BRANCH`, `A — every required ratio passes`, `outcome A / outcome B`, `\| Contrast \| Point estimate \|` | never reintroduce |
| T8 | Record-support phrases, whitespace-normalized over the whole draft | `:398-403` | `all 50 prompt-processing phases were identifiable`, `33 overlapped three records and 17 overlapped four`, `does not isolate a causal effect of model size`; and `1.7B` must be **absent** | preserve |
| T9 | **Section-scoped** model names and counts | `:404-418` | In each of `## Abstract`→`## 1. Introduction`, `### Record support in two historical model stacks`→`## 5. Discussion`, `## 5. Discussion`→`## 6. Related work`, `## 8. Conclusion`→`## 9. References`: both `Qwen2.5-1.5B-Instruct-4bit` and `Qwen2.5-7B-Instruct-4bit` must appear. In the Abstract **and** Conclusion additionally: `37 of 50`, `13 crossed three and passed`, `33 crossed three records and 17 crossed four`. Each of the four start markers must occur exactly once | **This is the tightest single constraint on an Abstract rewrite**: two full model identifiers plus three count phrases must survive inside 250 words |
| T10 | Conclusion-scoped phrases | `:420-424` | `Record identifiability depended on the model/stack`, `Phases with only two overlapping records failed the three-record minimum`, `37 of the 50 1.5B phases and none of the 50 7B phases`, `which overlapped three or four records each` — all inside `## 8. Conclusion`→`## 9. References` | **A §8 de-duplication pass must not delete any of these four.** Draft lines 936-938 carry three of them |
| T11 | Whole-draft phrases | `:421,425-426` | `count discipline` must be **absent**; `Accordingly, in this 1.5B population, 37 failed` and `In the 1.5B run r03` must be present | preserve |
| T12 | Median prefill durations | `:428-437` | `0.2815 s` (7B) and `0.1365 s` (1.5B) must appear in the draft, re-derived from `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`; plus `120.9-ms median record width` (`:438`) | **`0.2815 s` / `0.1365 s` may not be rounded**; `120.9-ms` is the already-rounded form and is itself pinned |
| T13 | Synthetic arithmetic markers | `:469-470` | `SYNTHETIC ARITHMETIC` present; `registry\nSYN-01` present **with that exact newline** | preserve the wrap |
| T14 | The A.3 local-records table rows are byte-formatted | `:546-551` | Every row of `worked-examples.json`'s `historical.local_records` must appear in the draft as `\| {index} \| {native_end_label:.0f} \| {start-1784757381:.9f} \| {end-1784757381:.9f} \| {gpu_w:.8f} \| {predicted_w:.8f} \| {loss:.6f} \|` | **9-, 8- and 6-decimal table numerals; no rounding** |
| T15 | Cure phrases that must be present | `:563-566` | `constant clock rate between stamps remains an unverified assumption`, `without assuming independence`, `Linear growth reduces a large discrepancy`, `three is a chosen cutoff, not proof of adequate`, `unrounded standard deviation` | preserve |
| T16 | References block shape | `:577-586` | `## 6. Related work\n` and `## 9. References\n` and `## Appendix A.` split points; references numbered `1.`…`21.` consecutively at line start; **the set of `[n]` citations in §6 must equal exactly `{1..21}`**; `[REF NEEDED]` absent; two hotcarbon URLs present | If you move a citation into §7, §6 must still cite all 21. Adding a reference means renumbering and keeping §6 exhaustive |
| T17 | §7 availability phrases, and phrases that must **not** be in §7 | `:587-597` | Present in `## 7. Evidence and code availability`→`## 8.`: `No public submission`, `not been released as a complete public reproduction`, `cannot\nreplace unavailable primary bytes` (pinned newline), `10 named members`, `40 of `runs_window_c_20260726/``. **Absent from §7**: `open_paper_input(ref)` and `Correct points with coherently wrong widths cannot count as` | **Relevant to the "move identifiers into §7" plan: `open_paper_input(ref)` must not land in §7** |
| T18 | Section and appendix numbering | `:601-608` | `^## (\d+)\.` over the draft must be exactly `["1".."9"]`; `^### A\.(\d+) ` exactly `["1".."7"]`; first-mention order of `Figure N` must be `1, 2, 3` then `A1..A6` | **Do not renumber or add a top-level section or appendix subsection.** Do not mention a figure out of first-use order |
| T19 | Figure caption/locator agreement | `:609-617` | Every `![Figure X …](locator)` needs a matching `(?m)^\*?Figure X\. ` caption line and the SVG's embedded `Figure N.` labels must agree | preserve |
| T20 | Structure assertions | `:624-641` | Absent from draft: `**close-out artifact**`, `### Adding publication safeguards`, `The artwork's P1 label`, `historical sources in Section 4`, `synthetic P1` (lower-case p), `**Gross energy**`, `**Idle-subtracted energy**`, `**same-cell floor**`. Present: `### Moving edges and enumerating endpoints`, `### Combining shared movements and local widths`, `Section 1 record definition`, `![Figure A4 …](figures/figA4_shared_signs.svg)`, `![Figure A5 …](figures/figA5_clock_polygon.svg)`. `SYNTHETIC P1` occurs **exactly once**, in `The artwork label "SYNTHETIC P1" is the desk script's name for this fixture` | Do not delete those two §3 headings; do not bold those three phrases |
| T21 | Replay pin commit + one-liner | `:643-660` | `` `2d96783857741f03ad9d634328efaf8bc6d676bc` `` present; `Any later explicitly issued replay pin supersedes it` present; the draft must contain a line matching `(?m)^python3 -B -c '(import json, runpy; .+)'$` and **that command is executed** and must reproduce `worked-examples.json`'s `synthetic` payload | Do not reflow or comment out that command line |
| T22 | Appendix A.6 enclosure block | `:23-45,156-173` | In the section starting `### A.6 Synthetic partial-record enclosure\n` (before any `## First-use audit ledger`): exactly one `(figures/figA_partial_record_enclosure.svg)` and the caption `Figure A1. Synthetic; no hardware observation.`; and §1 must contain `Appendix Figure A1 shows the records, window, and three energy results for this synthetic example.` | preserve verbatim |

### 1.6 D-165 retired-rationale census — **the line-number pin**

| # | Constraint | Enforced by | Literal pin | Legitimate update |
|---|---|---|---|---|
| X1 | **`docs/paper/draft-v2-skeleton.md` line 1459 must still contain the phrase `common-time`** | `tests/test_d165_rationale_census.py`: `RETIRED` `:35-48`, `occurrences` `:88-132`, `allowlist_keys` `:154-177` (stale-entry rejection at `:172-173`), tests `:191-200`. Allowlist: `tests/fixtures/d165_rationale_allowlist.json` | Exact tuple `{"path": "docs/paper/draft-v2-skeleton.md", "line": 1459, "phrase": "common-time"}`. Line 1459 is the last line of the draft — the Figure A2 caption containing `common-time line`. **Any net insertion or deletion above it shifts the line and both fails "stale allowlist entry" and (if the marker rule does not exempt it) "active retired rationale"** | Recompute the new line number and edit the `"line"` value in `tests/fixtures/d165_rationale_allowlist.json` in the same commit |
| X2 | No **new** retired rationale phrases anywhere in `docs/paper/` | same | Folded (case-insensitive, hyphens→spaces, **across line breaks**): `cancels exactly`, `uniform shared fiducial shift cancels`, `deviations-from-mean cancellation`, `shared fiducial shift`, `common-time robustness`, `moved together`, `timing error common to`, `common-time`, `common time shift`, `physical common-time`, `shared timing error`, `d165_shared_sign_local_corner_replay.v1` | New derived sentences must avoid these. If one is unavoidable, add an exact `{path,line,phrase,reason}` allowlist row |

### 1.7 Not constraints on the draft (checked, for completeness)

- `tests/test_paper_build.py` and `docs/paper/build/check_markdown.py` default to
  **`docs/paper/draft-v1.md`** (`check_markdown.py:17` `DEFAULT_DRAFT`;
  `test_paper_build.py:25`). They pin `Hard defects: 0` and `Images checked: 3`
  for **v1 only**. Running `check_markdown.py` on the v2 draft is optional and
  currently reports `Hard defects: 0`, `Images checked: 9`.
- `tests/test_paper_rendering.py` exercises `joulewise.paper_rendering` /
  `paper_custody` token objects. **It never reads the draft.**
- `tests/test_paper_comparison_placements.py` pins
  `docs/contracts/paper_comparison_placements.md`,
  `docs/paper/results-fill-registry.md`, `docs/contracts/paper_supply_custody.md`.
  **It never reads the draft.**
- `tests/test_check_paper_replay_fence.py` (6 lines) only re-runs the shared
  backup-probe regressions against `check_paper_replay_fence.py`.
- `tests/test_paper_renumber_refs.py` pins `draft-v1.md` by sha256
  (`939dfa23…f39b`) — not the v2 draft.
- The **167** `", line NNN"` locators inside `docs/paper/results-fill-registry.md`
  (e.g. `DG-102 — Appendix A.3.3 lower anchor endpoint, line 549`) are **not**
  mechanically checked. Line-shifting edits make them stale documentation but
  break no test. Fixing them is good hygiene, not a gate.

---

## 2. Per-edit-class impact and safe procedure

### 2.1 Rewrite the Abstract

**Pins hit:** A1 (headline verbatim, once), A4 (≤250 words, currently 246),
T9 (both `Qwen2.5-*-Instruct-4bit` identifiers + `37 of 50` + `13 crossed three
and passed` + `33 crossed three records and 17 crossed four` must all remain
inside the Abstract), L1 (13 ledger rows are homed to `Abstract`), L2/L3 (the
Abstract carries the sentence-scoped glosses for `powermetrics`, `sampler`,
`sampling record`, `token`, `commanded graphics-processor pulses`,
`prompt processing / prefill`, `token generation / decode`, `phase boundary`,
`interval-overlap allocation`, `held-average reconstruction`, `timing envelope`),
L5 (bold phrases), X1 (line shift).

**Procedure:**
1. Before touching anything, dump the Abstract's ledger obligations:
   `python -c` over `tests.test_paper_first_use_ledger` filtering
   `row.home == "Abstract"` — 13 rows. Every one of those terms must still have
   its **first** draft occurrence inside the Abstract afterwards, with its
   `GLOSS_REQUIREMENTS` phrase in the same sentence for the nine
   `SENTENCE_GLOSS_TERMS`.
2. Keep `ABSTRACT_HEADLINE` byte-identical. Re-wrap freely (whitespace is
   normalized) but change no word or punctuation mark.
3. Keep T9's five phrases literally.
4. Count words with `select_outcome_branches.py --check-rendered` after each
   draft. You have **4 words** of slack; if you need more, park prose in an
   HTML comment (comments are stripped before counting) or cut elsewhere in the
   Abstract — never raise the constant.
5. Avoid new `**bold**` phrases (L5). If one is essential, add a ledger row and
   bump `Terms inventoried: 265` -> 266.
6. After the edit, fix the D-165 allowlist line number (X1).

### 2.2 Move code identifiers and registry locators out of §2/§4 into §7 or Appendix A

**Pins hit:** L1 (**41 ledger rows homed in §2** — 2 in `2. In-window
calibration method`, 39 in `Bracketed pulse-train algorithm`; **15 homed in §4**
subsections), L2 (the glosses travel with the terms), R14 (the five clock-stamp
code spans `pre_spawn`/`first_parse`/`sampling_started`/`sampling_stopped`/
`post_parse` at draft lines 578-582 **cannot leave §4**), D1 (do not introduce
a retired `DX-`/`DG-`/`DS-`/`PG-` locator at the new site), T17
(`open_paper_input(ref)` must not appear in §7), T18 (do not create a new
`### A.n` subsection — the set is pinned to A.1–A.7), X1.

**The §2 identifiers at risk** (draft line 191): `validation_manifest_sha256`,
`instrument_calibration_invalid`, `joulewise/reduce.py`, `PLAN_HASH_MISMATCH`,
`joulewise/calibration_ledger.py`, `ISSUED_ACCEPTANCE_REGISTRY`,
`GENESIS_FIXTURE_ACCEPTANCE_SHA256`, `joulewise/calibration_bracketing.py`;
draft line 208: `ROUND_HALF_EVEN`,
`configs/calibration/calibration_acceptance_d079_v2_n17_r3.json`.

Note `ISSUED_ACCEPTANCE_REGISTRY` is **not free to move**: it is a required
gloss phrase — `expected digest from the in-code ISSUED_ACCEPTANCE_REGISTRY`
appears in `GLOSS_REQUIREMENTS["declared machine state / …"]`
(`tests/test_paper_first_use_ledger.py:107`), and that row's home is
`Bracketed pulse-train algorithm`. Same for `ROUND_HALF_EVEN`, which is its own
ledger row homed in `Bracketed pulse-train algorithm`.

**The §4 identifiers at risk**: `powermetrics_native_second_rate_aware_set_membership_v1`
(line 601), `not_resolvable_sample_count` (line 677 — also a ledger term with a
pinned disposition, L6), `identifiable` (686), the corpus roots
`runs_window_a10_20260725` / `runs_window_c_20260726` / `runs_window_7bfloor_20260729`,
`docs/process_traces/2026-08-09-prefill-phase-proof/results.json` (782), the
field paths `stack_summaries[stack="1.5B"].bundle_count`, `.resolvability`,
`prefill_overlap_sample_count`, `per_pulse`, `summary.offset_best_fit_lag`, and
the live locators `DX-001`, `DX-003`, `DX-010`, `DX-012`, `DG-024`, `DG-135`,
`DG-140`, `DG-143`, `DG-071`, `DG-131`, `DG-067`, `DG-070`, `DG-072`.

**Procedure:**
1. For each identifier you move, check whether it is a ledger Term or an
   alternative: `_alternatives(row.term)` splits on `" / "`. If yes, its ledger
   `home` cell must be changed to the **new** section's heading text (e.g.
   `7. Evidence and code availability`, `A.2 Scientific artifacts and their
   bindings`, `A.4 Executable verification order`).
2. Beware **partial** moves. The ledger checks the FIRST occurrence only. Moving
   the second mention is free; moving the first is a home change.
3. Do not move any phrase listed in `GLOSS_REQUIREMENTS` away from its gloss.
   `tests/test_paper_successor_migration.py:172-193` exists precisely to prove
   that relocating a term while leaving its construction behind fails.
4. Leave the clock-stamp table (draft lines 576-583) untouched.
5. Re-run `tests.test_paper_first_use_ledger` — its failure message names the
   term, the line, the actual home and the expected home, which is the fastest
   way to enumerate the ledger rows you still owe.

### 2.3 Delete unexercised campaign machinery from §1–§3

**Pins hit:** L1/L4 (a deleted term's ledger row becomes an "orphan ledger term"
— `test_first_occurrence_is_in_exact_home_section:554` asserts the first
occurrence is not `None`), L2 (deleting a gloss fails `_gloss_failures`), L5,
T3 (twelve required constructions with pinned line breaks, several in §1–§3),
T15 (five cure phrases), T20 (`### Moving edges and enumerating endpoints` and
`### Combining shared movements and local widths` must survive; `Section 1
record definition` must survive), T22 (§1 must keep `Appendix Figure A1 shows
the records, window, and three energy results for this synthetic example.`),
T18 (§1, §2, §3 headings themselves must remain, `^## (\d+)\.` == 1..9), A5,
T2/T7 (do not accidentally *add* a forbidden string while summarising), X1.

**Procedure:**
1. Delete prose, never a `##`/`###` heading in the 1..9 / A.1..A.7 sets.
2. For every deleted sentence, grep the deleted text against the ledger's Term
   column **and** against `GLOSS_REQUIREMENTS`. A term whose last occurrence you
   delete needs its ledger row deleted too — and then
   `Terms inventoried: 265; FAILS: 0.` must be decremented (L4).
3. Deleting a term whose home was §1–§3 but which still occurs later re-homes
   it: update the `home` cell to the new first-occurrence section.
4. Re-check T3's twelve constructions and T15's five cures by literal grep
   before running tests — the test's failure message quotes the missing literal.

### 2.4 Round timing numerals in the main text (full digits kept in the appendix)

**This is the most dangerous class.** Three separate mechanisms compare draft
numerals against re-derived doubles, and one compares formatted table rows.

| Numeral family | Where | May it be rounded? |
|---|---|---|
| §4 worked-arithmetic paragraph (draft line 588): `0.0011349971959968978`, `0.030067931757111657`, `0.0289329345611147592`, `26.625`, `27.625`, `1784757381.2856488`, `1784757382.293089`, `0.02544938965763524`, `0.02893293456111476`, `-0.008607394549133255`, `-0.005308621075866744` | R4–R13 | **NO.** `float(literal) == derived` exactly, plus the Decimal subtraction identity (R6). `--literals-only` catches R6 even without the corpus |
| §4 best-fit pair `+0.027` / `-0.007` | R12 | Already the rounded form; must stay exactly `f"{v:+.3f}"` |
| §4 clock-stamp table cells (draft lines 578-582) | R14 | **NO.** `float(printed) == computed` per cell |
| §4 stamp-resolution caption | R15 | **NO** |
| §4 prose `28.93293456111476 ms`, `1.1349971959968978-ms`, `30.067931757111657 ms` (draft lines 629-631) | not fence-extracted, but they are the **millisecond restatements** of R13/R4/R5 | Not mechanically pinned — but rounding them makes the draft internally inconsistent with line 588. If you round these, say so explicitly; no test will stop you |
| `120.9186 ms`, `5.9508 ms`, `120.9224 ms`, `5.8949 ms` | T6 | **NO** — asserted `assertIn(median + " ms", draft)` |
| `0.2815 s`, `0.1365 s` | T12 | **NO** — asserted `assertIn(f"{median:.4f} s", draft)` |
| `120.9-ms median record width` | T12 | Already rounded; the **rounded** form is what is pinned |
| `+13.0 ms`, `−5.5 ms`, `59 of 59`, `49 of 59` | D5 (registry markers), and `49 of 59` also inside A1/A2 headlines | Already rounded; these exact strings are the registry-rendered values |
| Appendix A.3 local-records table rows | T14 | **NO** — 9/8/6-decimal format strings are re-derived and asserted present |
| Appendix A.3.3 anchor numerals `1784757336.5519202`, `1784757336.5532944`, `1784757336.5526073`, `0.0006869160344978743`, `0.00044608116149902344` | registry rows DG-102–106 (documentation only) | Not test-enforced, but they are the appendix full-digit home — keep them |
| §3 synthetic arithmetic `2.4305766103`, `8.8304376431`, `3.6330628732` | `tests/test_paper_terms_lint.py:465-467` recomputes them to 9 places but only asserts the **computation**, not the draft string; `2.776445` and `4.808944` are outright forbidden (T2) | Check by grep before rounding |

**Procedure:** treat every numeral you want to round as guilty until proven
innocent. For each candidate, run
`grep -n "<numeral>" tests/ scripts/ docs/paper/results-fill-registry.md`.
If it appears in any test or in `check_paper_replay_fence.py`'s anchors, it is
pinned. The two `--literals-only` CLIs are a 2-second smoke test that catches
every R-class and D-class break without the 8-minute corpus replay.

### 2.5 Add a few derived sentences

**Pins hit:** L5 (no new `**bold**` multi-word phrase unless ledgered), L1 (a
new sentence can accidentally become the **first** occurrence of an existing
ledger term and move its home — this is the classic silent break), X2 (no
retired D-165 rationale phrase), D1 (no retired `DX-`/`DG-`/`DS-`/`PG-`/`OB-`/
`OR-` locator), D3 (do not open a new sentence with `“The following are
diagnostic-era instrument statistics`), A4 (if the sentence is in the Abstract),
A8 (no `[FILL:` in visible text), T2/T7/T20 (forbidden strings), T18 (no new
`Figure N` mention out of first-use order).

**Procedure:**
1. Write the sentence.
2. Run `tests.test_paper_first_use_ledger` — `test_first_occurrence_is_in_exact_home_section`
   names any term whose home you just moved. Fix by either rewording or
   re-homing the ledger row.
3. Run `tests.test_d165_rationale_census`.
4. Prefer plain prose over emphasis; every `**two word**` phrase costs a ledger
   row.

### 2.6 Remove duplicated sentences from §8

**Pins hit:** A2 (the Conclusion headline must remain, exactly once, at draft
lines 923-926), T10 (**four** Conclusion-scoped phrases at draft lines 936-938
must all survive), T9 (both `Qwen2.5-*` identifiers plus `37 of 50`,
`13 crossed three and passed`, `33 crossed three records and 17 crossed four`
must remain inside §8), L1 (any ledger term homed in §8 — none at audit time,
but a deletion can re-home a term from §8 into a later section or vice versa),
X1.

**Note the real duplication in §8:** draft lines 932-935 say
`37 of 50 phases crossed two records and failed the three-record minimum; 13
crossed three and passed` and lines 936-938 say `Phases with only two
overlapping records failed the three-record minimum: 37 of the 50 1.5B phases
and none of the 50 7B phases`. **Both are independently pinned** — the first by
T9 (`37 of 50`, `13 crossed three and passed`), the second by T10. You cannot
collapse them into one sentence without editing
`tests/test_paper_terms_lint.py:416-424`. If the duplication is genuinely a
defect, the legitimate fix is: rewrite both, then update the four/five asserted
substrings in `:413-424` in the same commit, with the rationale recorded.

Also: the HTML comment at draft line 943
(`<!-- Headline: DX-001/003/012/013; record support: DG-067/068/069/072/073/135–142. -->`)
is a source map. `DG-135–142` uses an **en dash**; `DG-078`–`DG-101` are retired
(D1), so do not widen that range downward. `DX-001/003/012/013` are all live.

---

## 3. Exact local replay command list

All commands from the **worktree root**. `PY=/Users/edr/code/JouleWise/.venv/bin/python`.
The replay-fence and round-7 corpora live at **`/Users/edr/code/JouleWise`**
(the canonical checkout), not in the worktree.

```bash
cd /Users/edr/code/JouleWise-wt-paper-n          # <-- the editing worktree
PY=/Users/edr/code/JouleWise/.venv/bin/python
CORPUS=/Users/edr/code/JouleWise
```

### 3.1 Fast gate (≈20 s) — run after every edit

```bash
# 1. Abstract budget + every fixed-sentence / forbidden-string guard.
$PY docs/paper/fill-rehearsal/select_outcome_branches.py \
    --check-rendered docs/paper/draft-v2-skeleton.md
# expect: rc 0, "METHODS_DIAGNOSTIC validated; abstract_words=<=250, limit=250"

# 2. Section-4 numeric anchors + the draft-internal subtraction identity.
#    JOULEWISE_BACKUP_ROOTS= disables the iCloud probe (otherwise up to 2 s/root).
JOULEWISE_BACKUP_ROOTS= $PY scripts/check_paper_replay_fence.py --literals-only
# expect: rc 0, "LITERALS 22 extracted", "INTERNAL MISMATCHES 0"

# 3. DX registry / retired-locator / appendix-placement census.
JOULEWISE_BACKUP_ROOTS= $PY scripts/check_paper_round7_artifacts.py --literals-only
# expect: rc 0, penultimate line "R7F PLACED 0/4",
#         last line "R7F LITERALS-ONLY COMPARED 412 / MISMATCHES 0"

# 4. Optional structural Markdown lint on the v2 draft (its default is v1).
$PY docs/paper/build/check_markdown.py docs/paper/draft-v2-skeleton.md
# expect: rc 0, "Hard defects: 0", "Images checked: 9"
```

### 3.2 Draft-bearing unit tests, no corpus needed (≈20 s)

```bash
$PY -m unittest -v \
    tests.test_paper_first_use_ledger \
    tests.test_paper_successor_migration \
    tests.test_select_outcome_branches \
    tests.test_d165_rationale_census \
    tests.test_paper_comparison_placements \
    tests.test_paper_build
```

`tests.test_d165_rationale_census` shells out to `git ls-files`, so run it
inside the worktree (it works in a linked worktree).

### 3.3 `tests.test_paper_terms_lint` — needs `R7F_CORPUS_ROOT`

`tests/test_paper_terms_lint.py:353` reads
`$R7F_CORPUS_ROOT/docs/process_traces/2026-08-09-prefill-phase-proof/results.json`
and asserts it is byte-identical to the worktree copy. Its default is the
**repo root**, so plain invocation works; pointing `R7F_CORPUS_ROOT` at a
scratch directory (a common trick to skip the round-7 replay) makes this test
raise `FileNotFoundError`.

```bash
$PY -m unittest -v tests.test_paper_terms_lint                  # default: REPO root — OK
# or, explicitly:
R7F_CORPUS_ROOT="$CORPUS" $PY -m unittest -v tests.test_paper_terms_lint
```

### 3.4 Replay fence against the primary bytes (≈1 min)

`tests/test_paper_replay_fence.py:52` reads `R7F_CORPUS_ROOT`, defaulting to the
**worktree root** — which does NOT hold `runs_window_a_20260722/`, so the replay
class silently skips there. To actually replay:

```bash
R7F_CORPUS_ROOT="$CORPUS" $PY -m unittest -v \
    tests.test_paper_replay_fence tests.test_check_paper_replay_fence

# equivalent direct CLI (full re-derivation, exit 0/2/3):
JOULEWISE_BACKUP_ROOTS= $PY scripts/check_paper_replay_fence.py \
    --repository-root . --corpus-root "$CORPUS"
# expect: rc 0, "MISMATCHES 0"; rc 3 == corpus absent (never read as a pass)
```

### 3.5 Round-7 full replay (≈8 min; re-runs both producers)

`tests/test_paper_round7_artifacts.py:42-44` defaults `R7F_CORPUS_ROOT` to
`/Users/edr/code/JouleWise` already, so the replay class runs by default on this
machine.

```bash
R7F_CORPUS_ROOT="$CORPUS" $PY -m unittest -v tests.test_paper_round7_artifacts

# direct CLI, full replay:
JOULEWISE_BACKUP_ROOTS= $PY scripts/check_paper_round7_artifacts.py \
    --repository-root . --corpus-root "$CORPUS"
# expect: rc 0, last line "R7F COMPARED 415 / MISMATCHES 0"

# to skip the ~8-minute replay locally, point the corpus root at an empty dir;
# the replay CLASS then skips, but tests.test_paper_terms_lint must NOT be run
# with that override (see 3.3):
R7F_CORPUS_ROOT=/tmp/no-corpus $PY -m unittest tests.test_paper_round7_artifacts
```

### 3.6 One-shot everything (what CI effectively runs)

CI (`.github/workflows/ci.yml`) discovers every `tests.*` module through
`scripts/shard_tests.py` (`test` job, `:44-103`, 4 shards × Python 3.11/3.14)
and sets **none** of `R7F_CORPUS_ROOT`, `R7F_REGISTRY`, `PAPER_FIRST_USE_DRAFT`,
or `JOULEWISE_BACKUP_ROOTS`. On the hosted ubuntu runner the corpus is absent,
so both replay classes skip and only the always-on halves gate. The `pr-fast`
job (`:254-360`) is explicitly **not a gate**. So:

- CI enforces: every pin in §1.1, §1.3 (digest half), §1.4, §1.5, §1.6, and the
  §1.2 *extraction* half — but **not** the numeric re-derivation.
- Only a local run with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` proves the
  §4 numerals still re-derive. Rule 1 (lead owns final verification) applies:
  run 3.4 and 3.5 before landing any numeral change.

```bash
R7F_CORPUS_ROOT="$CORPUS" $PY -m unittest -v \
    tests.test_paper_first_use_ledger \
    tests.test_paper_terms_lint \
    tests.test_paper_replay_fence \
    tests.test_check_paper_replay_fence \
    tests.test_paper_round7_artifacts \
    tests.test_paper_successor_migration \
    tests.test_select_outcome_branches \
    tests.test_d165_rationale_census \
    tests.test_paper_comparison_placements \
    tests.test_paper_rendering \
    tests.test_paper_build
```

---

## 4. Files a legitimate pin update touches

| To change | Edit |
|---|---|
| Abstract / Conclusion headline wording | `docs/paper/fill-rehearsal/select_outcome_branches.py:15-25` + the draft |
| Abstract word cap | `select_outcome_branches.py:13` + `tests/test_select_outcome_branches.py:25-28` + `tests/test_paper_successor_migration.py:105,120` (**doctrine change — do not**) |
| A ledger term's section home | `docs/paper/protocol/first-use-audit-ledger.md` (the `First reader-facing home` cell) |
| A required gloss phrase | `tests/test_paper_first_use_ledger.py:54-156` + the draft |
| A pinned line-wrap in a cure paragraph | `tests/test_paper_first_use_ledger.py:684-699` and/or `tests/test_paper_terms_lint.py:236-260` + the draft |
| Ledger row count | `docs/paper/protocol/first-use-audit-ledger.md:289` (`Terms inventoried: 265; FAILS: 0.`) |
| Successor lexicon `§` homes | `docs/paper/round7/built-terms-lexicon.md` + `tests/test_paper_first_use_ledger.py:179-189` |
| A new numeral that must be re-derived | add a registry row in `docs/paper/results-fill-registry.md` (`MEASURED`/`DERIVE`/`EXTRACT`, with supplier locator + sha256 + `NON_CLAIM_BEARING` freeze status) **and** an extractor+comparison in the relevant fence script; a bare new numeral in the draft with no row is a fill without custody |
| An appendix-only derived value | an `AppendixDeriveRow`: `\| XX-01 — Appendix A.n … \| `[FILL:XX-01]` \| `scripts/….py`, SHA-256 `…`, N B … \| … \| DERIVE \| … VALUE_UNISSUED … APPENDIX_ONLY_REGISTRY_BOUND … \|` (parser at `scripts/check_paper_round7_artifacts.py:420-457`), with the marker placed **once**, inside an HTML comment, under that exact `###` heading |
| D-165 allowlist line number | `tests/fixtures/d165_rationale_allowlist.json` |
| Comparison census numbers | `tests/test_paper_round7_artifacts.py:1444-1448,1504` (`412`, `0/4`, `415`) and `:406` (`228`) |
