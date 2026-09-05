```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the D-174 methods/diagnostic draft; verified historical suppliers, retired empirical fills, and passed all 26 targeted tests.",
  "workspace": {
    "base_requested": "449825bf",
    "base_mode": "exact",
    "head_start": "449825bfd6b584cfff685598ce57b121feb54bc1",
    "head_end": "449825bfd6b584cfff685598ce57b121feb54bc1",
    "upstream_end": null,
    "branch": "feat/2026-09-05-paper-m"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/fill-rehearsal/select_outcome_branches.py",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_first_use_ledger.py",
    "tests/test_paper_terms_lint.py",
    "tests/test_select_outcome_branches.py",
    "docs/process_traces/2026-09-05-paper-m/01-seat-M-landing-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 11 tests in 1.761s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 10 tests in 1.031s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 5 tests in 0.228s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out /tmp/paper-m-excursion.json --svg /tmp/paper-m-excursion.svg",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   b_fiducial_s: draft=0.030067931757111657 derived=0.030067931757111657",
          "ok   projection_evaluated_cell_count: draft=122859 derived=122859",
          "wrote /tmp/paper-m-excursion.json",
          "wrote /tmp/paper-m-excursion.svg"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "projection_evaluated_cell_count: draft=122859 derived=122859"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nfor local, registered in [('/tmp/paper-m-excursion.json','docs/paper/round7/excursion-decomposition.json'),('/tmp/paper-m-excursion.svg','docs/paper/figures/fig4_edge_excursions.svg')]:\n assert Path(local).read_bytes()==Path(registered).read_bytes()\nprint('RAW REPLAY: JSON and SVG byte-identical to registered suppliers')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RAW REPLAY: JSON and SVG byte-identical to registered suppliers"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "JSON and SVG byte-identical"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "METHODS_DIAGNOSTIC validated; abstract_words=225, limit=250"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "METHODS_DIAGNOSTIC validated; abstract_words=225, limit=250"
      }
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Historical raw bytes remain in project custody, not a public release; inference transfer and generic floor-width reproduction remain unproved and are explicitly limited in the draft. No new model/floor result is reported.",
      "needs": ""
    }
  ]
}
```

## Change

Selected the single METHODS/DIAGNOSTIC submission under the 2026-09-05 magistrate fallback ruling and D-174. The exact Abstract/Conclusion headline is grounded in DX-001/003/012/013 and a primary-byte replay, not inferred from a fitted-bound magnitude. Figure 2 uses the registered fig4 SVG unchanged. Its caption distinguishes signed fitted lags, allowed-region excursions and the clock-anchor allowance, and disclaims independence, coverage and inference transfer. The former timeline is Appendix Figure A2; the overlap schematic is Figure 4. All figure bytes, raw evidence and registered parent JSON remain unchanged.

The retained empirical results are the historical calibration (including the formal worked capture and 17-capture corpus) and historical record support: 37/50 failed and 13/50 passed, verified against DG-067–075 suppliers, per-bundle counts and issued statistics. P1 remains SYNTHETIC Figure A1; SYN-01 adds the exact field/hash map for the labelled two-block arithmetic. Tests independently recompute both illustrations. Allocation measurand, shared-energy-sign/local-corner R_cm, both mandatory floor/interval roles, non-gating F+B planning, prompt-0 scope and untested transfer remain explicit. Prospective characterization/workload text is method only. No inference-energy means, v5 floors, clearances, directional verdicts or empirical dominance result remain.

228 registry rows now carry dated RETIRED_FALLBACK dispositions; no original row is deleted. PG-03 gains an explicit tombstone for its earlier PG-02 consolidation. Historical suppliers, anchors, values and prior statuses remain in those rows. DS-34 honestly retains the unavailable release locators; TR-01 is a limitation; PE-01 and SYN-01 retain illustration placements. The current placement census is separate from the preserved frozen-v1 census.

Selector disposition: **adapted, not removed**. Its legacy filename accepts only `--outcome METHODS_DIAGNOSTIC`, validates the one draft, and copies its bytes unchanged into a new file. A/B/REFUSAL are rejected with no output; overwrite is refused. The rendered check enforces the 250-word Abstract limit, exact historical headline, transfer limitation, Figure 2 and absence of retired result fills. Current Abstract: 225 words.

References: 21 existing citations resolved from draft-v1 and the repository bibliography audit/verification; renumbered once using the existing 31-to-21 map. The verified HotCarbon PDF locators were carried into entries 12 and 15. No invented or new citation; **[REF NEEDED]: none**. Availability names what the project checkout contains, the unreleased raw files, missing public release revision/archive/manifest and the limits of D-173 custody and 02-F4 width binding. It claims neither a public release nor independent end-to-end raw reproduction.

The first-use ledger now has **260 terms, FAILS: 0**. Obsolete branch alternatives were removed even from the compound request-total row; diagnostic-era and prospective-demonstration homes were separated. New GPU/fitted-edge, best-fit-lag, allowed-region, median, source-map and custody-interface entries carry first-use glosses. The frozen legacy lexicon and pre-cure fixture are unchanged. The appendix also states input checks, event pairing, fit-grid clipping/ties, diagnostic bisection and work limits directly, from the existing artifact guide/code, so a reader does not need to infer these replication rules.

**Section inventory.** Ranges are inclusive source lines, before = requested HEAD `449825bf`, after = this uncommitted draft. Each table lists all added/removed headings and all surviving sections whose immediate content changed; each section ends before the next heading. The title text is unchanged. The draft's opening control note changed from before 1–15 to after 1–5.

**docs/paper/draft-v2-skeleton.md**

| Section | Disposition | Before lines | After lines |
|---|---|---:|---:|
| Abstract | Rewritten / updated | 23–44 | 9–31 |
| 1. Introduction | Rewritten / updated | 45–206 | 32–198 |
| Bracketed pulse-train algorithm | Rewritten / updated | 217–255 | 209–243 |
| One diagnostic reconstruction | Rewritten / updated | 256–276 | 244–264 |
| 3. Instrument characterization | Rewritten / updated | 277–458 | 326–498 |
| Pilot observations under the retired calculation | Removed | 459–492 | — |
| 4. How the method quantifies assigned-energy sensitivity | Rewritten / updated | 493–508 | 499–509 |
| Comparing the moved-edge limit and point-only value | Rewritten / updated | 509–747 | 510–742 |
| Adding publication safeguards after the ratio | Rewritten / updated | 748–892 | 743–888 |
| Outcome sentence forms | Removed | 893–953 | — |
| 5. Collection stops when required evidence fails | Rewritten / updated | 954–957 | 909–912 |
| Every input and every refusal remains visible | Rewritten / updated | 973–985 | 928–940 |
| 6. Demonstration results | Removed | 986–990 | — |
| Results | Removed | 991–1025 | — |
| Printed negative result: short prompt processing has too few overlapping records | Rewritten / updated | 1026–1114 | 943–1042 |
| Demonstration fixed before collection | Removed | 1115–1129 | — |
| Why the selected prompt length is not yet stated | Removed | 1130–1161 | — |
| 7. Discussion and limitations | Rewritten / updated | 1162–1194 | 1043–1058 |
| Further limitations | Rewritten / updated | 1195–1324 | 1059–1188 |
| From counter gain to counter time | Rewritten / updated | 1376–1381 | 1240–1245 |
| LLM energy measurement | Removed | 1382–1387 | — |
| Benchmark and metrology lineage | Rewritten / updated | 1388–1399 | 1255–1266 |
| 9. Evidence and code availability | Rewritten / updated | 1400–1412 | 1267–1300 |
| 10. Conclusion | Rewritten / updated | 1413–1434 | 1301–1316 |
| 11. References | Rewritten / updated | 1435–1439 | 1317–1345 |
| Appendix A. Reproducing this work | Rewritten / updated | 1440–1445 | 1346–1357 |
| A.2 Scientific artifacts and their bindings | Rewritten / updated | 1452–1462 | 1364–1375 |
| A.3 Formal calibration algorithms | Rewritten / updated | 1463–1468 | 1376–1381 |
| A.3.3 The clock-anchor estimator | Rewritten / updated | 1515–1604 | 1428–1528 |
| A.3.4 Placing the trace on the wall clock, trimming warm-ups, and authenticating the schedule | Rewritten / updated | 1605–1614 | 1529–1543 |
| A.3.5 The pulse-fit algorithm | Rewritten / updated | 1615–1687 | 1544–1616 |
| A.3.7 The work budget and the 120 s work clock | Rewritten / updated | 1700–1705 | 1629–1643 |
| A.6 Release locators | Removed | 1744–1753 | — |
| First-use audit ledger | Rewritten / updated | 1789–2069 | 1731–2013 |
| Historical current-method edge result | Added | — | 265–325 |
| Evidence refusal and claim gates | Added | — | 889–908 |
| 6. Historical record-support result | Added | — | 941–942 |
| Large-language-model energy measurement | Added | — | 1246–1254 |
| A.6 Release status | Added | — | 1682–1689 |
| A.8 Measurement-window schematic | Added | — | 1725–1730 |

**docs/paper/results-fill-registry.md**

| Section | Disposition | Before lines | After lines |
|---|---|---:|---:|
| Rules and source index | Rewritten / updated | 28–145 | 53–171 |
| `_v5` identity and workload bindings | Rewritten / updated | 146–158 | 172–184 |
| Exact template-token registry | Rewritten / updated | 159–168 | 185–194 |
| Alpha and beta floor-cell values | Rewritten / updated | 169–185 | 195–211 |
| Cell-label terms and D-165 attribution-dominance ratios | Rewritten / updated | 186–272 | 212–298 |
| Floor-cell branch text and diagnostics | Rewritten / updated | 283–317 | 309–343 |
| D-123 reported phase-energy cells | Rewritten / updated | 338–369 | 364–395 |
| Gamma `_v5` contrasts | Rewritten / updated | 370–392 | 396–418 |
| Swap-block tokens (no landed template counterpart) | Rewritten / updated | 393–408 | 419–434 |
| Characterization campaign | Rewritten / updated | 409–474 | 435–500 |
| Rows | Rewritten / updated | 581–686 | 607–712 |
| Successor-draft desk analyses (round 7) — DX rows | Rewritten / updated | 736–795 | 762–819 |
| Renderer-only metatokens | Rewritten / updated | 796–809 | 820–833 |
| Draft marker-site registry | Rewritten / updated | 810–918 | 834–944 |
| Successor-skeleton outcome-branch slots | Removed | 919–935 | — |
| Submission disposition — 2026-09-05 | Added | — | 3–52 |
| Successor submission placements and retired outcome slots | Added | — | 945–963 |
| Fallback placement census (2026-09-05) | Added | — | 980–991 |

Explicit removal spans within surviving headings: Abstract branch group before 25–43; Discussion group before 1169–1193; Conclusion group before 1415–1433. The v5 floor/ratio table occupied before 1007–1013; the contrast/clearance/verdict table occupied before 1014–1018. Their owning Results subsection is removed, with the single historical record-support result taking Section 6. The retired pilot floor/ratio subsection and Section-4 pilot quotient are removed; no absent production evidence is rendered as an empirical refusal.

**Verification tails (verbatim).**

`V1` — `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_first_use_ledger`

```text
----------------------------------------------------------------------
Ran 11 tests in 1.761s

OK
```

`V2` — `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_paper_terms_lint`

```text
----------------------------------------------------------------------
Ran 10 tests in 1.031s

OK
```

`V3` — `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_select_outcome_branches`

```text
----------------------------------------------------------------------
Ran 5 tests in 0.228s

OK
```

`V4` — `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out /tmp/paper-m-excursion.json --svg /tmp/paper-m-excursion.svg`

```text
ok   b_fiducial_s: draft=0.030067931757111657 derived=0.030067931757111657
ok   projection_evaluated_cell_count: draft=122859 derived=122859
wrote /tmp/paper-m-excursion.json
wrote /tmp/paper-m-excursion.svg
```

`V5` — `python3 -B - <<'PY'`

```text
RAW REPLAY: JSON and SVG byte-identical to registered suppliers
```

`V6` — `python3 -B docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md`

```text
METHODS_DIAGNOSTIC validated; abstract_words=225, limit=250
```

`V7` — `git diff --check`

```text
(no output)
```

## Verification notes

Preflight used only the three named modules, one at a time with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`: 11, 5 and 4 tests passed on the requested baseline. Final sequential runs pass 11, 10 and 5 tests. No discovery suite, new measurement, quiet-machine collection, agent launcher, Claude/Codex invocation, commit, push or publication build ran. Python bytecode is redirected by the runner to its temporary cache; later commands also use `-B`. All repository writes are inside WRITE_SCOPE, and the initial tree had no unowned changes. Lead-owned run state, task queue and generic report paths were not edited.

Intermediate targeted failures were cured before the final tails: the removed legacy-calculation check was retained explicitly for the historical fixture; a wrapped bold term was corrected; PG-03's existing consolidation note received the dated tombstone; and a first-use collision between ordinary “the model's” and the appendix's literal “The model” label was removed in prose. The semantic gloss/mutation tests were retained and extended, not disabled. Existing excerpt headings and prior bytes remain available at the requested HEAD for comparison.

The full paper renderer/publication package and independent lead review remain the lead's final gates. This task verifies the requested Markdown draft, immutable suppliers, source-map arithmetic and the three authorized modules; it does not claim a PDF/HTML layout inspection.

## Residual risk

Public raw-byte reproduction remains unavailable until the release manifest and complete evidence archive issue. Pulse-to-inference transfer remains untested. The generic floor consumer's uncertainty-width gap is disclosed with the stronger mint comparison distinguished; neither a custody interface nor matched point values is claimed to close it. The fallback reports no prospective floor or model comparison that could depend on those unissued gates.

Next exact step: lead reviews this uncommitted diff and the retained Figure 2/appendix captions, then performs its publication rendering and final source/label gate. No scope expansion is requested.
