```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Audit found one blocker and four lesser fidelity defects; bibliography logic is sound and the frozen draft remained byte-identical.",
  "workspace": {
    "base_requested": "origin/paper/t26-round7-prep",
    "base_mode": "exact",
    "head_start": "c578e57d36f925346a440871bde9958f66b5ad59",
    "head_end": "c578e57d36f925346a440871bde9958f66b5ad59",
    "upstream_end": "c578e57d36f925346a440871bde9958f66b5ad59",
    "branch": "paper/t26-round7-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/paper/round7/retensing-plan.md",
        "location": "101, 115, 143, 517",
        "check": "A4",
        "summary": "Outcome sentences introduce numeric literals before the frozen draft builds them."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/paper/round7/retensing-plan.md",
        "location": "101, 115, 129, 143, 423",
        "check": "A7",
        "summary": "Abstract/early-Introduction replacements use vocabulary first built later."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/paper/round7/retensing-plan.md",
        "location": "41, 289",
        "check": "A3",
        "summary": "H01 and H20 omit the hazard file's explicit failing-outcome scopes."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "docs/paper/round7/fill-checklist.md",
        "location": "305-306",
        "check": "B2",
        "summary": "Two leaf-field citations point only to parent-object construction; the leaf definitions are far outside the ±10-line tolerance."
      },
      {
        "id": "F5",
        "severity": "nit",
        "file": "docs/paper/round7/fill-checklist.md",
        "location": "187-202",
        "check": "B5",
        "summary": "TERM formulas are semantically equivalent but not copied exactly from all sixteen registry rows."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab  docs/paper/draft-v1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 scripts/paper_renumber_refs.py docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  31 -> 21",
          "RESULT: no changes written"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RESULT: no changes written"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 scripts/paper_renumber_refs.py docs/paper/draft-v1.md --apply",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "REFUSED: --apply on docs/paper/draft-v1.md requires --i-am-round-7"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "^REFUSED: --apply .* requires --i-am-round-7$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code -- docs/paper/round7/retensing-plan.md docs/paper/round7/fill-checklist.md docs/paper/round7/bibliography-renumber-plan.md scripts/paper_renumber_refs.py tests/test_paper_renumber_refs.py docs/paper/draft-v1.md",
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
      "text": "WRITE_SCOPE [] prohibited creating the requested temporary copy, so first/second apply was verified in memory and by source-path inspection rather than filesystem mutation; pytest was likewise not run because its tmp_path fixtures create files.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — blocker — unlicensed early numeric literals

[retensing-plan.md](/Users/edr/code/JouleWise-wt-r7prep/docs/paper/round7/retensing-plan.md:101) introduces numbers that do not satisfy A4:

- H05 C at plan line 101 / draft line 11: `1.5B`, `7B`.
- H06 C at plan line 115 / draft line 11: `§3`.
- H08 C at plan line 143 / draft line 31: `1.5B`, `7B`.
- Item 10 C at plan line 517 / draft line 243: `1.5B`, `7B`.

Evidence:

```text
$ rg -n -m 3 '1\.5B|7B' docs/paper/draft-v1.md
247:...Qwen2.5 1.5B...
260:The prospective demonstration will compare 4-bit Qwen2.5 7B with 1.5B...
268:...7B-minus-1.5B...

$ rg -n -m 1 '§3' docs/paper/draft-v1.md
30:2. The second contribution ... §3 characterizes the instrument...
```

Thus the model literals first occur after draft lines 11, 31, and 243, and `§3` first occurs after line 11. They are neither registry-token-contained nor among the ruled constants.

Complete A4 numeric classification:

- Class (i), registry tokens: digits embedded in Item 10’s `[REFUSAL_REASON_1p5B_floor_window]` token.
- Class (ii), already present on/before the source line: H01 `1.5B/7B`; H02/H03/H08/H09/H29 section numbers; H12 `4-bit`, `Qwen2.5`, `7B`, `1.5B`, `M3`; H13 formula indices/divisor; H17/H28 `_v4`; H27/H28 `1.5B/7B`.
- Class (iii), ruled constants: H14 `128`, H15 `256`, H19 `0.025/0.05`; the ten-block design is also ruled.
- Violations: the seven occurrences listed above.
- H10’s “Item 10” is a non-published routing instruction, not replacement prose.

Fix: remove the early model numerals and forward section reference, using already-built physical wording such as “required evidence” or “an excluded cell.” Item 10 C can say “required evidence was then refused” without naming model sizes.

### F2 — should-fix — later-built vocabulary at first-use sites

The first-use audit fails beyond the numeric literals:

- H05 C, draft line 11: “claim calculations” is not established there.
- H06 C, draft line 11: “floor window” has no occurrence in the frozen draft; “claim-anchored limit” and “artifact’s outcome” first occur at line 88.
- H07 C, draft line 21: “required records were excluded” and the model-ranking concept are first physically explained at line 23.
- H08 C, draft line 31: “floor window” is unbuilt and “artifact’s outcome” first occurs at line 88.
- U01 C, draft line 11: the physical two-gate rule is built at line 23 and the exact “claim gate” term first occurs at line 202.

Evidence:

```text
$ rg -n -m 1 'claim-anchored limit|claim gate' docs/paper/draft-v1.md
88:...an unavailable claim-anchored limit...
202:Figure 3 separates evidence refusal from the two claim gates.

$ rg -n 'floor window' docs/paper/draft-v1.md
# no output
```

Fix: use plain physical consequences already established at the insertion point, or add an inline gloss that genuinely defines the term. Do not claim these phrases are already built.

### F3 — should-fix — H01/H20 failure scopes are not reproduced

The source hazard scopes are explicit, but the plan makes both unscoped:

```text
$ <mechanical extraction of the two **Fails** fields>
H01 hazard= A, B, and partial C: plan= (unscoped)
H20 hazard= C and currently A/B: plan= (unscoped)
```

H02–H19 and H21–H29 retain matching outcome scopes. H20’s prose implies the same branches, but A3 requires the stated outcomes to match.

Fix:

- H01: begin `**Fails:** A, B, and partial C: ...`
- H20: begin `**Fails:** C and currently A/B: ...`

### F4 — should-fix — two B2 leaf-field citations miss ±10 lines

[fill-checklist.md](/Users/edr/code/JouleWise-wt-r7prep/docs/paper/round7/fill-checklist.md:305) cites `joulewise/analysis_engine/__init__.py:1575-1607` for `estimator.estimate`. That range constructs the parent `"estimator"` object at line 1605, but the leaf is authored at line 192.

Line 306 cites `:1566-1574` for `deterministic_bounds.decision_interval.lower/.upper`. The parent is constructed at 1573, but `lower` and `upper` are authored by `_interval_dict` at line 163.

```text
$ rg -n 'def _interval_dict|def _estimator_dict|"estimate": result.estimate|"lower": value.lower' joulewise/analysis_engine/__init__.py
160:def _interval_dict(value: Interval | None) -> dict[str, float] | None:
163:    return {"lower": value.lower, "upper": value.upper}
185:def _estimator_dict(result: PairedEstimate | None, name: str, n: int) -> dict[str, Any]:
192:        "estimate": result.estimate,
```

All other named artifact fields were found at their cited locations within tolerance.

Fix: retain the parent-object citations and add `joulewise/analysis_engine/__init__.py:185-203` for `estimator.estimate` and `:160-163` for interval endpoints.

### F5 — nit — TERM formulas are not exact textual copies

The formulas are mathematically equivalent, but B5 asked for exact copies:

- Registry absolute TERM B defines `W = math.fsum(w_i)` and prints  
  `max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)`.
- Checklist line 188 prints  
  `max_i(abs(r_i)+w_i*(n-1)/n+(math.fsum(w)-w_i)/n)`.
- Checklist line 190 similarly removes the registry spacing.
- Twelve later rows say “formula above” instead of reproducing their registry row’s formula.

The executable Batch-2 derivation at lines 248–258 implements the correct formulas, so this is not an arithmetic defect.

Fix: copy the registry formula text verbatim into all sixteen table rows.

## Verification

| Check | Result | Mechanical evidence |
|---|---|---|
| A1 | Pass | `A1 quotes 35 failures []`; H01–H29 and U01–U06 all matched their named draft line byte-for-byte. |
| A2 | Pass | `A2 tokens 24 unknown []`; `A2 ids 20 unknown []`. |
| A3 | Fail | H01 and H20 unscoped; all other hazard outcome scopes match. |
| A4 | Fail | Seven unlicensed early numeric occurrences; full classification above. |
| A5 | Pass | `item60 plan bytes: 261 ruling bytes: 261 equal: True`; null-token outcome counts `A=1 B=1 C=1 D=0` (`5` total including two explanatory mentions). |
| A6 | Pass | No claim-side-bound/`deterministic_bounds.total` equation; TERM B matches the predicate at `detection_floor.py:806-841`; published corner-widened component at `:763-784`, full corner computation at `:932-947`; drift-added `floor_gate_j` at `:1620-1640` and validated at `:3866-3874`; Holm families remain distinct; no C sentence asserts equality/no difference. |
| A7 | Fail | Later-built terms listed in F2. |
| B1 | Pass | `sites=34 slots=36`; `sites=37 slots=39`; registry count `38`; `ROWS 38/38 PLACED`; both NEEDS-VALUE sites found at draft lines 272 and 276/checklist lines 325–326. |
| B2 | Fail | All fields exist, but two leaf citations miss ±10 lines; see F4. |
| B3 | Pass | Both scripts’ `--help` accept every documented flag; all three named tests exist; censuses reproduced exactly. |
| B4 | Pass | DS-29 omission forbids `deterministic_bounds.total`; DS-28 states both missing B and the one-cell/two-quantity shape mismatch; consistent with items 33 and 64. |
| B5 | Fail | Semantically correct but not exact textual copies; see F5. |
| C1 | Pass | Cited set and orphan set exactly match the plan; map is correct. |
| C2 | Pass | No draft bracket would be wrongly rewritten; guard exits 2; in-memory first rewrite yields 21 references, no orphans, identity map, so the second-apply branch exits 3. |
| C3 | Pass | Dry-run output matches the plan; SHA-256 stayed `939dfa…39ab` before and after. |

Census output:

```text
$ grep -oE '\[PENDING[^]]*\]' docs/paper/draft-v1.md |
  awk '{ sites += 1; slots += (index($0, ",") ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
sites=34 slots=36

$ grep -oE '\[(PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]' docs/paper/draft-v1.md |
  awk '{ sites += 1; slots += ($0 ~ /^\[PENDING,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
sites=37 slots=39

$ grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[(PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' docs/paper/results-fill-registry.md
38
```

Bibliography dry run and hash:

```text
$ shasum -a 256 docs/paper/draft-v1.md
939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab  docs/paper/draft-v1.md

$ python3 scripts/paper_renumber_refs.py docs/paper/draft-v1.md
REFERENCES: 31
CITED: 1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 15, 19, 20, 22, 23, 26, 27, 28, 29, 30, 31
ORPHANS: 4, 9, 11, 14, 16, 17, 18, 21, 24, 25
MAP:
  1 -> 1
  2 -> 2
  3 -> 3
  5 -> 4
  6 -> 5
  7 -> 6
  8 -> 7
  10 -> 8
  12 -> 9
  13 -> 10
  15 -> 11
  19 -> 12
  20 -> 13
  22 -> 14
  23 -> 15
  26 -> 16
  27 -> 17
  28 -> 18
  29 -> 19
  30 -> 20
  31 -> 21
RESULT: no changes written

$ shasum -a 256 docs/paper/draft-v1.md
939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab  docs/paper/draft-v1.md
```

C2 bracket classification:

- Citations rewritten: `[5]`, `[6]`, `[29]`, `[23]`, `[20]`, `[7]`, `[19]`, `[8]`, `[22]`, `[13]`, `[3]`, `[15]`, `[1]`, `[2]`, `[30]`, `[31]`, `[26]`, `[27]`, `[12]`, `[10]`, `[28]` on lines 324–344.
- Known-range rejection: `[0,1]` at line 221 contains zero.
- Decimal/symbolic intervals: lines 79, 95, 123, 148, 210, 287, 484, 522, 557, 567, 573, 584, 590, 622, 624–625, 628–629, 638; none matches the integer-citation grammar.
- Placeholders: lines 189, 256, 272, 274, 276, 280–283, 289–290, 348; none matches the numeric grammar.
- Markdown image links: lines 39, 59, 206; nonnumeric and followed by `(`.
- Symbolic/empty brackets: `[]` at line 80 and `[ch]` at lines 434–435.
- Registry-style tokens: none in the frozen draft.
- Wrongly rewritten forms: none.

In-memory post-rewrite result:

```text
after references 21
after cited [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
after orphans []
after map {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}
after bracket multiset {'[1]': 1, '[2]': 1, '[3]': 1, '[4]': 2, '[5]': 2, '[6]': 1, '[7]': 1, '[8]': 1, '[9]': 1, '[10]': 1, '[11]': 1, '[12]': 1, '[13]': 1, '[14]': 1, '[15]': 1, '[16]': 1, '[17]': 1, '[18]': 1, '[19]': 1, '[20]': 1, '[21]': 1}
second_apply_code_path exit 3 because analysis.orphans == ()
```

## Residual risk

No files were created or modified. The final worktree remained clean at `c578e57d36f925346a440871bde9958f66b5ad59`, equal to its upstream. The only unexecuted mutation-based checks were the temp-copy apply and pytest runs, both excluded by `WRITE_SCOPE: []`; their relevant control paths were inspected mechanically.