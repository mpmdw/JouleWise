```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All 28 operative texts are byte-present after whitespace normalization, but v4 contains three policy conflicts, one placement error, and two summary defects.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "5e090987a3e360fddc3562f3ada7e8510865e4ca",
    "head_end": "5e090987a3e360fddc3562f3ada7e8510865e4ca",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","summary":"Categorical no-drop and guaranteed-recapture wording conflicts with T-14 and T-15."},
      {"id":"F2","severity":"blocker","summary":"The sizing-pilot description specifies one shakedown night; T-3 and T-10 require one per arm."},
      {"id":"F3","severity":"blocker","summary":"The plain-language summary overstates permission to claim a direction at each level."},
      {"id":"F4","severity":"should_fix","summary":"The E3 question omits Ed's thinking-off-primary option."},
      {"id":"F5","severity":"nit","summary":"T-13 is byte-exact but placed after the drift term instead of after the Night term."},
      {"id":"F6","severity":"nit","summary":"The plain-language summary retains internal question and record identifiers."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 /tmp/a282_install_audit.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["T-28: PRESENT-EXACT","superseded_full_bodies_present: []"]},
      "expected": {"exit_code":0,"tail_regex":"T-28: PRESENT-EXACT\\nsuperseded_full_bodies_present: \\[\\]"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 /tmp/a282_arithmetic.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["§2.5 ratios: 1.922129, 1.917272, 1.927004; §2.6 lever 2.5, max_gap 23.55, bound 25 J: PASS"]},
      "expected": {"exit_code":0,"tail_regex":"§2\\.5 ratios: .*§2\\.6 lever 2\\.5, max_gap 23\\.55, bound 25 J: PASS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},
      "expected": {"exit_code":0,"tail_regex":"## HEAD \\(no branch\\)"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — BLOCKER.** [V4’s summary](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:8), retry definition (line 184), S7 carry (line 975), and proposed D-166 addendum (lines 1079–1080) say long-running problems are never dropped or imply one recapture settles them. [30/21 §3 T-14](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md) instead excludes a problem from **both** models’ sums and counts when it lacks a counted attempt, with NE/NR status pending recapture. T-15 allows the recapture to fail terminally. The S7 sentence limiting pairwise exclusion to sensitivity directly conflicts with T-14. Revise all four locations before Ed reviews the proposed addendum.

**F2 — BLOCKER.** [V4 §2.1](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:164) describes “one short measured shakedown night.” [30/21 §3 T-3 and T-10](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md) require **one night per arm**, with each arm’s own pass and drift derivation. The K21 text is correct; fix the conflicting introductory description.

**F3 — BLOCKER.** [V4’s summary](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:5) says adoption permits a claim “at each level, which model used less energy per correct answer.” [30/21 §3 T-8, T-11 and T-28](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md) allow unresolved, unestimable and pooled outcomes. The summary should say that directions are claimed only where the tests license them; other levels receive their ruled status.

**F4 — MATERIAL.** [V4’s E3 question](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:13) offers seeded sampling versus greedy decoding. V4’s reserved-item specification at line 1295 also offers **thinking-off as primary**. Both rulings leave E3 to Ed ([30/21 §3 closing sentence](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md)). As written, a yes/no answer to the summary’s E3 does not settle that third choice. E1, E2 and O-21 accept yes/no; E4 accepts a number.

**F5 — NIT.** [V4’s T-13](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:214) is byte-exact, but [30/21 §3 T-13](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md) says to insert it after the Night term. V4 puts it after the drift term and discloses the move in §8. The Night term points forward, so this is a placement defect rather than missing policy.

**F6 — NIT.** The “plain words” section still uses `E1`–`E4` and `O-21` ([V4 lines 11–15](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:11)); its following provenance paragraph uses `A282`, `07c`, `30/10` and `30/21` (lines 17–20). These are internal shorthand. The substantive questions can be named without it.

**C1 — operative installation inventory.** The comparison collapsed whitespace only. `10` means [30/10 §3](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/10-coldgate-fable-ruling.md); `21` means [30/21 §3](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/21-coldgate-fable-addendum-ruling.md). Locations refer to [V4](/Users/edr/code/wt-a65fb4fa-lens5/docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md). Multipart instructions were checked by their dictated fragments at each target; T-4 was checked with its amendment applied. There are **no PRESENT-DIFFERS or MISSING texts**, hence no text diff to show.

| Text | Source | Ruled target → V4 location | Result |
|---|---|---|---|
| T-1 | 10 | Denominator term → §2.1:233 | PRESENT-EXACT |
| T-2 | 10 | Denominator row → §2.8:493 | PRESENT-EXACT |
| T-3 | 21 | K21, row pointer, D-166 → §2.9:790, row:489, §4:1083 | PRESENT-EXACT |
| T-4 | 10 amended by 21 | Floor term and amended formula → §2.1:137 | PRESENT-EXACT |
| T-5 | 21 | Steps 2/7/8, K11, examples → §2.2:265/278/281, §2.9:639, §2.3:307, §2.5:347 | PRESENT-EXACT |
| T-6 | 21 | Floor-gate row → §2.8:491 | PRESENT-EXACT |
| T-7 | 21 | Interval term/step 11, K10 → §2.1:223, §2.2:284, §2.9:626 | PRESENT-EXACT |
| T-8 | 21 | Step 10 → §2.2:283 | PRESENT-EXACT |
| T-9 | 21 | Flag term, K22, step-4 pointer → §2.1:255, §2.9:795, §2.2:270 | PRESENT-EXACT |
| T-10 | 21 | Drift threshold, K12, O-7 closure → §2.1:213, §2.9:653, §7:1259 | PRESENT-EXACT |
| T-11 | 21 | Step 12, K16 → §2.2:285, §2.9:739 | PRESENT-EXACT |
| T-12 | 21 | Drift model → §2.1:212 | PRESENT-EXACT |
| T-13 | 21 | After Night term; K23, step-5 pointer → §2.1:214, §2.9:800, §2.2:273 | **MISPLACED**; bytes exact |
| T-14 | 21 | Counted attempt/K24 → §2.1:194 | PRESENT-EXACT |
| T-15 | 21 | S8 → §3:986 | PRESENT-EXACT |
| T-16 | 10 | O-8 → §7:1261 | PRESENT-EXACT |
| T-17 | 10 | S7 → §3:977 | PRESENT-EXACT |
| T-18 | 10 | S6 sentence → §3:968 | PRESENT-EXACT |
| T-19 | 10 | Covariates row and K4 → §2.8:490, §2.9:565 | PRESENT-EXACT |
| T-20 | 21 | K2 budget, O-14/O-18 → §2.9:534, §7:1268/1294 | PRESENT-EXACT |
| T-21 | 21 | K1 eligibility predicate → §2.9:509 | PRESENT-EXACT |
| T-22 | 10 | Scorer term → §2.1:95 | PRESENT-EXACT |
| T-23 | 10 | Power term → §2.1:107 | PRESENT-EXACT |
| T-24 | 21 | After K2 carry → §2.9:539 | PRESENT-EXACT |
| T-25 | 21 | K9, step 6, K19, change log → §2.9:602/756, §2.2:275, §2.10:828 | PRESENT-EXACT |
| T-26 | 21 | K25 → §2.9:809 | PRESENT-EXACT |
| T-27 | 21 | After K10 M9 carry → §2.9:630 | PRESENT-EXACT |
| T-28 | 21 | S9 and K16 → §3:992, §2.9:741 | PRESENT-EXACT |

**C2.** None of the superseded 30/10 T-3, T-5, T-7–T-15, T-20 or T-21 bodies survives as operative text. The old AP-5 guard and gate-21 floor bracket appear only as marked historical quotations, with their replacements stated beside them. F1 concerns an older S7 carry that conflicts with the new T-14, not survival of a superseded 30/10 final text.

**C3.** V4 §7 marks O-1–O-16 closed and lists the reserved decisions as O-17/E2, O-18/E4, O-19/E3, O-20/E1 and O-21/Ed. The reservation is complete; F4 concerns how E3 is presented to Ed at the top.

**C5.** The §2.5 replicate recomputes to `R* = 1.922129`, low `1.917272`, high `1.927004`; its displayed rounding is sound. In §2.6, P3’s position is `21.5`, the revised 1.7B mean is `11.5`, the lever is `2.5`, `max_gap = 23.55`, and the drift bound is `25 J` (about `0.106%` of `23,552 J`). The displayed arithmetic is sound.

## Residual risk

This was a document installation review. It did not validate the packer, estimator or live measurement path.