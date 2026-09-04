# Opus counter-review — paper-f @ bf5bc686 (gate ledger item 6)

Base `33290b8b`. Read-only; both checkouts clean.

```
python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
.............
Ran 13 tests in 2.301s
OK
```

## Findings

| # | Sev | Site | Evidence |
|---|---|---|---|
| 1 | SHOULD-FIX | draft :122-124 (§1) | Cured \(U_{\rm corner}\) gloss says only "…every allowed lower-or-upper edge choice … is **evaluated jointly**." §4 :549-550 has the missing selection rule: "enumerate every joint choice… **Retain the largest result.**" §1 never says max, so the paper's RQ (\(R=U_{\rm corner}/U_{\rm point}\ge2\)) is stated unreplicably; lexicon :1634/:1722 propagate it. No prior reviewer caught it. Fix: "…evaluated jointly, and the largest result retained." |
| 2 | SHOULD-FIX | draft :355 (§3 cell 1, col 2) | "…their planned prompt workloads **and their fixed-output workload**." In `JouleWise-wt-floorgen/configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py`, `output_tokens: 512` at :579 (decode), :817 (prefill p42), :837 (prefill p512) — *every* family is fixed-output, so the phrase picks out no referent, and it is glossed nowhere (absent from the 251 inventoried terms). Worse: nothing in `_v5` varies output length, so the row's own calculation column ("fit energy against output length… all five levels") has **zero** recorded inputs, undercutting the new preamble (:249-251) that the campaign "records inputs a later campaign can use" for this question. File 10's V2 tail shows `output_tokens: 512` and passed it. |
| 3 | SHOULD-FIX | :122-128 vs §4 :528-557, :659-665 | Macro split introduced by the cure: §1 uses `U_{\rm point/corner/cmp,shared/cmp,point}`; §4 uses `U_{\mathrm{…}}`. Same glyphs, two distinct strings for any literal matcher (renderer pass, fill rehearsal, registry anchor grep); `\rm` in a subscript is deprecated. Unify on `\mathrm`. |
| 4 | SHOULD-FIX | :120 vs :820, :876 | One gate threshold, three names. §1 bridge makes **detection floor** the *pre*-safeguard name ("its final value, after the safeguards of Section 4, is what the artifacts call the **cell floor**"), yet Figure 3 prose (:876) gates on "the detection floor" while §4's same Gate 1 (:820-821) gates on \(F_{\mathrm{cell}}\) = "the cell floor". Bridge assigns the figure's name to the wrong stage. |
| 5 | NIT | :119-120 and :698-701 | Relation stated **twice**, not once: §4 re-bolds **resolution bound** / **cell floor** as if at first use, though lexicon :1739-1740 assign both homes to §1. |
| 6 | NIT | :87 vs :103-104 | `powermetrics` glossed twice. The lexicon row was edited to describe the *second* gloss ("macOS's built-in power sampler") while the test's `GLOSS_REQUIREMENTS["powermetrics"]` still binds the *first* ("power sampler used here") — row and enforcement now name different sentences. |
| 7 | NIT | :356 (§3 cell 2, col 3) | "The frozen ladder requires all three magnitudes," but floor packs schedule null blocks at **one** magnitude per arm (decode 512-out; prefill p512) — `d117_floor_qwen3-8b_v5:590-612`. Pre-existing, but now contradicts the adjacent new cell. |
| 8 | NIT | `joulewise/reduce.py:1218-1256` | §2 states the manifest/artifact hash gate unconditionally; in code it is entirely inside `if strict_physics:`, and frozen 0.5.1/0.6.1 replay arms use distinct reason spellings (:1288-1299). Accurate for the current mint; add "under the current mint". |
| 9 | NIT | registry :822-833 | DS-02/03/05/06 cite "line 94/95/96/97"; rows now at :355-358. Content anchors (`**Workload response:**` etc.) match **exactly** — this diff in fact *repairs* anchors the pre-diff plain `\| Workload response \|` row did not satisfy. Only offsets stale. |

## (d) Defect shape the hardened test still misses

**A present-but-incomplete gloss.** `_gloss_failures` (test :344-366) asserts only that each literal phrase appears *somewhere in the same block* — no positional check against `occurrence.character_index`. §3 rows are single ~1600-char lines, so column 1 may use a term column 4 defines and it passes. It cannot detect a *missing clause* in an otherwise-present gloss: finding 1 is the live instance — the `U_point`/`U_corner` requirement demands two phrases but never the max rule, so an unreplicable definition is green. Coverage is also ~30 of 251 rows; the other ~220 get section-home checking only, so a term used many paragraphs before its definition inside the right section is invisible. Secondary: `_search_blocks` skips heading lines, so a term introduced only in a heading is never a first use.

## Confirmed sound (spot-checks; no repeat of prior gate work)

- `PLAN_HASH_MISMATCH` — `calibration_ledger.py:4644,4646`: digest **or** `plan_id` mismatch, exactly as §2 states.
- `ISSUED_ACCEPTANCE_REGISTRY`/`GENESIS_FIXTURE_ACCEPTANCE_SHA256` — `calibration_bracketing.py:733-742,826-828`: expected digest selected by `artifact_role` before bytes accepted. Exact.
- Cadence — `reduce.py:117-118` (`2.0`/`4.0`), `:985-988` (`cadence_ratio_unrecorded` on `None`; `cadence_ratio_below_threshold` on `< min`). Exact.
- Package power — `RAIL_MANIFEST = ["cpu_power","gpu_power","ane_power"]` (`adapters/powermetrics.py:57,1805`). Exact.
- `_T_CRITICAL_95[1] = 12.706` (`aggregate.py:42`) consumed at `detection_floor.py:696`; dropping the file:line citations was correct.
- Timing flag quarter-window — `reduce.py:997-998`. `U_{\rm edge}` residue: 0. "power-counter boundary"/"counter cell" residue: 0. `figures/fig3_decision_gates.svg` present (8206 B); caption's element inventory complete.
- §3 cells 3 and 4 verified in both generators (contrast `gamma-reference-start/-end` + three interior stages; floor `alpha/beta-reference-start|-midpoint|-end`; `phase_energy_j.prefill|decode` in both).

## Verdict

**MERGE** — no blocker; land findings 1-4 as a follow-up before the draft circulates externally.
