```json
{
  "verdict": {"gauntlet": "LANDABLE", "findings": []},
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Selected-A sentence-level pedagogy refutation found every changed term built before use or defined at first use; CR-05, CR-06, and CR-08 are cured.",
  "workspace": {
    "base_requested": "2c9ec573561845453d7268758e049f82b2c1631b",
    "base_mode": "exact",
    "head_start": "2c9ec573561845453d7268758e049f82b2c1631b",
    "head_end": "2c9ec573561845453d7268758e049f82b2c1631b",
    "upstream_end": "cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136",
    "branch": "feat/2026-09-04-paper-j"
  },
  "pathspec": ["docs/process_traces/2026-09-04-paper-j/02-refuter-pedagogy.md"],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /private/tmp/paper-j-refuter-selected-a-2c9ec573.md --outcome A",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"]},
      "expected": {"exit_code": 0, "tail_regex": "selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 1.739s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 1.391s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show HEAD -- docs/paper",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["+a failure. Terms inventoried: 266; FAILS: 0."]},
      "expected": {"exit_code": 0, "tail_regex": "Terms inventoried: 266; FAILS: 0\\."}
    }
  ],
  "flags": []
}
```

## Findings

None.

## Sentence audit

The selected A was read in this order: Sections 1, 2, 3, 4, then 10. The entries below cover every reader-facing sentence changed by the landing; repeated later substitutions are grouped only when they add the same already-built label. “Same sentence” is a first-use construction, not a later cure.

| Changed sentence(s) | Nouns, symbols, and labels added by the landing | Earlier construction |
|---|---|---|
| `draft-v2-skeleton.md:56` | request parts; runtime-recorded time; **phase boundary**; **phase edge**; equivalent name | Lines 52–55 build prompt processing/prefill and token generation/decode as the two parts; line 56 then declares both labels as aliases in the defining sentence. |
| `:61–63`, `:95` | sampling record; average power; time; **phase boundary**; integrated energy; time integral; edge; span; phase energy | Lines 50–56 build the sampling record, request parts, and aliased boundary before these uses. No noun or symbol is first supplied later. |
| `:80–82` | displacement; commanded times; edge position; pulse records; **clock-anchor bound**; uncertainty; power record; wall-clock time; **pulse-derived limit** | Lines 74–79 build command timestamps, GPU pulses, physical onset, the power record, and the measurement window. The changed sentence itself glosses the clock-anchor bound and defines the pulse-derived limit as displacement plus that bound. |
| `:112–116` | research question; permitted edge movement; calibration; mapping; component; false-difference source; \(U_{\mathrm{point}}\); **point-only value**; **recorded-edge limit**; plain-word alias | Lines 74–95 build the calibration, mapping, boundary movement, component, and false-difference bound. This sentence defines the symbol and declares the two names as aliases. |
| `:128`, `:138`, `:143` | \(U_{\mathrm{cmp,point}}\); four-run comparison; point-only value; evaluation; ratio; bound; twofold boundary contribution | Lines 112–116 build the canonical value; lines 101–126 build the comparison, evaluation, ratio, and contribution before these changed uses. |
| `:195`, `:197` | pulse-derived limit; \(B_{\mathrm{fiducial}}\); capture; sustained mixed inference; before/after bracket | Lines 80–82 define the limit. Lines 189–193 build the per-capture displacement-plus-anchor quantity before line 195 names it \(B_{\mathrm{fiducial}}\); the bracket is built at the start of line 195 before line 197 uses it. |
| `:279–280` | \(\delta\); four member energies; recorded value; phase boundary; edge-moved allowance | Lines 56 and 260–278 build the boundary, A/B/B/A block, \(\delta\), member energies, and allowed-difference construction before the changed phrase. |
| `:435–447` | retired calculation; point-only values; false-difference limits; phase boundary; prompt processing; token generation; short prompt processing; moved-edge ratios | Lines 112–116 define the value and alias; line 56 defines the boundary; lines 414–438 build the retired calculation before the affected sentences use those terms. |
| heading `:481` and sentences `:483–487`, `:505`, `:546`, `:556–563`, `:671–673`, `:761–764` | boundary-moved bound; point-only value; component; example; phase boundaries; \(R\); comparative point-only value; zero values | All are repetitions of the phase-boundary and point-only-value labels defined at lines 56 and 112–116. The surrounding Section 4 sentences build component, bound, example, and ratio before each use; the heading introduces no new synonym. |
| `:875` (both changed sentences) | \(R\); \(R_{cm}\); boundary movement; component; point-only value; Apple M3 Max; MLX; *powermetrics* configuration; variation at recorded boundaries; inserted-gap check; pulse-derived limit; inference | Lines 50–54 build the machine/framework/sampler scope; lines 112–126 build the values and ratios; lines 80–82 build the limit; lines 83–116 build variation at recorded boundaries; lines 84–86 and 583–666 build the four-run comparison and shared replay; lines 66–68 build the inserted-gap check. |
| `:1009–1062` | phase boundary/boundaries; sampling record; overlap; diagram labels; middle record; phase | The alias is fixed at line 56. Section 5 builds record width, positive overlap, and record support at lines 999–1008 before the changed boundary uses; no competing “phase edge” label reappears. |
| `:1147` (changed sentences) | variation at recorded boundaries; pulse-derived limit; point-only value; repeats; boundary movement | All are built in Section 1 at lines 80–143, and the Section 4 formulas at lines 505–673 precede this Discussion use. |
| `:1175–1181`, `:1196`, `:1325`, `:1350` | physical edge responses; pulse-derived limit; diagnostic capture; residual; inference; phase boundaries; channels; energy integral; resolution bound | The limit and boundary are built at lines 56 and 80–82; the diagnostic capture is built at lines 227–241; the residual comparison is built within the inserted-gap subsection before line 1325. |
| A/B/Refusal Conclusion branches `:1389`, `:1395`, `:1401` | point-only value; **short-input diagnostic records**; earlier measurements; requests; brief prompt processing; measured phases; minimum overlap rule; `[FILL:DG-067]`, `[FILL:DG-068]`, `[FILL:DG-069]` | Lines 52–56 build requests and prompt processing; lines 170–175 build the brief-prompt question and three-record minimum; lines 999–1077 build record overlap and the retained diagnostic population. Each Conclusion branch then defines the new records label in its first sentence and only afterward uses “They”; the three pre-existing registered markers remain in that following sentence. |

CR-05 is therefore cured: the Conclusion gives the retained evidence a first-use label and immediately identifies it with the earlier short-request measurements. CR-06 is cured: **phase boundary**, **point-only value**, and **pulse-derived limit** are canonical thereafter; **phase edge** and **recorded-edge limit** occur only in their explicit first-use alias declarations. CR-08 is cured: the pulse-derived limit is explicitly the pulse-record displacement plus the clock-anchor bound, and the bound is glossed as uncertainty placing the power record on wall-clock time. The changed first-use-ledger cells are metadata rather than prose sentences; their locations and glosses agree with these constructions.

## Residual risk

The audit is intentionally pedagogy-only and selected-A-only. It does not validate future filled marker prose or the evidentiary truth of unissued campaign results.
