```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Read-only escalation consult: the repeated defects call for a single decision specification and an independent exhaustive acceptance gate.",
  "workspace": {
    "base_requested": "d2f9a273d5be0bad155c1e8cbfd4ff4197d28159",
    "base_mode": "exact",
    "head_start": "d2f9a273d5be0bad155c1e8cbfd4ff4197d28159",
    "head_end": "d2f9a273d5be0bad155c1e8cbfd4ff4197d28159",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_reduce tests.test_energy_per_correct",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 30 tests in 1.136s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 30 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The proposed crossover and terminal-ceiling rules need adoption in one authoritative acceptance brief before another implementation round.",
      "needs": "Magistrate and claim-policy owners approve or amend the Q2 and Q5 rules."
    }
  ]
}
```

## Q1 — Diagnosis

The magistrate’s diagnosis is substantially right. [Packet C §3](/Users/edr/code/JouleWise/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md) defines L* and non-monotone wording; [synthesis §1](/Users/edr/code/JouleWise/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md) adds Holm and block-aware inference; [ruling 08](/Users/edr/code/wt-d8cc9c0a-bk/docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md) adds pooled-boundary restrictions. Fix clauses X1–X14 then describe selected examples rather than a complete decision function. The current tests encode two wrong readings: pooled constituents are asserted `not estimable`, and an all-1.7B-cheaper pattern with a merged group is asserted to have `boundary_in_merged_group`.

There are two additional causes. First, the modules have separate, permissive input contracts: required registration facts can be supplied inconsistently, skipped on sparse paths, or invented by defaults. Second, example tests and operand-collapse mutation tests establish useful local behavior but cannot establish a five-level policy over all patterns. The balance search illustrates this distinction: it minimizes drift, yet has no acceptance threshold. These are contract and acceptance-design failures, not merely missed branches.

## Q2 — Complete decision specification

**Proposed closed vocabularies.** A group status is `1.7B cheaper` (`1`), `8B cheaper` (`8`), `not resolved` (`n`), or `not estimable` (`e`). A constituent level of an **estimable merged group** has per-level status `pooled` (`p`) and a required group pointer; it never inherits the group’s direction. Constituents of a merged **not-estimable** group have status `not estimable` and the group pointer. Singleton levels take their group status.

Apply the registered count-only merge order before looking at energy, intervals, or p-values. For each arm, begin with five singleton groups. Merge 5 with 4 if either is below three correct in either model; if 4–5 remains sparse, merge it with 3. Then apply the analogous 1→2→3 steps. An isolated sparse Level 3 has no prescribed merge and is `not estimable`; choosing a neighbor for it would require an amended rule. A group remains `not estimable` if either pooled model count is below three after these steps.

For each estimable group, run its paired inference. Its status is `8` only when Holm rejects within the fixed **m = 5** family, the widened interval lies wholly below 1, and the below-side direction wins. Use the mirror conditions for `1`. All other estimable outcomes are `n`. An untested sparse group occupies a non-rejecting hypothesis slot; merging never reduces m. A raw Holm rejection without a compatible interval direction remains `n`.

For L*, scan **groups in level order**, using their statuses. Define “monotone” on the resolved directional subsequence: it must match `1*8*`. Gaps marked `n` or count-based `e` do not themselves constitute reversals. Thus `1n888`, `1nn8n`, and `n1n8n` are monotone for this decision rule. L* means the *first level with a supported 8B-cheaper decision*, not an inferred physical change point inside an unresolved gap.

```text
if a resolved 8 precedes any later resolved 1:
    absent("non_monotone")
elif every group is e:
    absent("all_not_estimable")
elif there is no 8 group:
    absent("no_8b_cheaper_group")
else:
    B = first 8 group
    licenses = earlier 1 groups
    if licenses is empty:
        absent("no_lower_1p7b_cheaper_group")
    elif B is merged:
        absent("boundary_in_merged_group")
    elif no license is a singleton:
        absent("boundary_in_merged_group")
    else:
        L* = B's sole level
```

This retains ruling 08’s restriction on a **merged licensing group**. That restriction is justified: a pooled R above 1 does not establish that either constituent R is above 1; different correct-count weights can produce a pooled reversal. One *singleton* lower license is enough, even if another lower license is merged. A merged group elsewhere does not cause a boundary reason. Patterns with no `8` group cannot have a merged-boundary reason.

Worked patterns use `|` for group boundaries and brackets for merged groups. The “levels” column is the per-level output.

| Group outcomes, Levels 1→5 | Per-level statuses | L* / absent reason |
|---|---|---|
| `1|1|1|1|1` | `11111` | `no_8b_cheaper_group` |
| `8|8|8|8|8` | `88888` | `no_lower_1p7b_cheaper_group` |
| `n|n|n|n|n` | `nnnnn` | `no_8b_cheaper_group` |
| `8|8|1|1|1` | `88111` | `non_monotone` |
| `1|n|8|8|8` | `1n888` | **3** |
| `1|n|n|8|n` | `1nn8n` | **4** |
| `n|1|n|8|n` | `n1n8n` | **4** |
| `8|1|8|8|8` | `81888` | `non_monotone` |
| `1|8|1|8|8` | `18188` | `non_monotone` |
| `1|1|n|8|8` | `11n88` | **4** |
| `1|n|8|n|1` | `1n8n1` | `non_monotone` |
| `[1–2]1|3:8|4:n|5:n` | `pp8nn` | `boundary_in_merged_group` |
| `[1–2]1|3:1|4:8|5:n` | `pp18n` | **4** |
| `1:1|2:n|[3–5]8` | `1nppp` | `boundary_in_merged_group` |
| `1:1|2:n|3:8|[4–5]8` | `1n8pp` | **3** |
| `[1–3]e|4:1|5:8` | `eee18` | **5** |
| `[1–5]e` | `eeeee` | `all_not_estimable` |

The `[1–3]e` example deliberately shows the recommended treatment of a **count-based** unestimable group: it remains visible, while later independent directional evidence can still define L*. A terminal measurement failure is different; see Q5(c).

## Q3 — Acceptance shape

Yes, provided the reference is frozen in the brief and maintained independently of the implementation. Exhaustive group-status enumeration is finite and small. The count rule reaches exactly **nine partitions**:

`1|2|3|4|5`, `12|3|4|5`, `1|2|3|45`, `123|4|5`, `1|2|345`, `12|3|45`, `123|45`, `12|345`, `12345`.

Enumerating `{1,8,n,e}` for every group in each partition gives **1,764** cases. This is an intentional superset: some `e` placements cannot arise from the counts that produce that partition. For each case, compare every per-group status, every per-level status and group pointer, L*, and its exact absent reason against the brief’s reference function.

Test the *upstream transformations* separately. Counts saturated at 3 preserve every `< 3` threshold, so all two-model count vectors in `{0,1,2,3}¹⁰` give 1,048,576 finite merge/estimability cases. Independently test Holm rank, stop-after-first-failure, exact equality, and interval/direction disagreement; group-status enumeration alone cannot catch those. Run defect-shaped replays for the known examples alongside the exhaustive tests. Do not generate the oracle from production helpers or ask the implementer to write it.

## Q4 — Structural cure for silent defaults

Use one versioned, immutable, hash-bound **registration plus sizing receipt**. Pass its validated object to pack, reduce, and decide. Reject missing, unknown, duplicate, or conflicting fields before any sparse or terminal branch; bind its digest into rosters, item rows, block windows, and decision output.

It must carry:

- **Identity and scope:** plan/registration IDs and hashes; sizing-receipt hash; frozen problem-set manifest and item IDs by level; required levels `1…5`; n and block size by arm; exact role→model ID and arm→family maps; primary-arm/headline eligibility; prompt, scorer, extractor, decoding, weights, tokenizer, and metric/window-class identities.
- **Decision rule:** correct-count minimum 3; the exact merge order above; five-block/five-distinct-envelope minima; Holm α and fixed m = 5; bootstrap draw count and seed; floor identity and operative `floor_j` by window class; `anchor_j`; gross-energy rail and strict-valid inclusion rule.
- **Capture and packing:** cap tokens by arm; envelope, offset, interior, guard, and pitch seconds with `0 ≤ offset`, `0 < interior − guard ≤ envelope − offset`, and a coherent pitch; prefill and upper seconds/token used to derive each cap-bounded worst-case duration; the post-pilot `max_drift_lever_slots` with its sizing provenance.
- **Recovery and accounting:** permitted whole-block and single-item attempts; parent/child block and digest-chain rules; terminal `ceiling_violation` policy; required `retry_stage` vocabulary; the registered retry sensitivity and balanced-recapture trigger.

The receipt may be *incomplete before the sizing pilot*, but an incomplete object cannot issue a claim-ready roster. Validation should also compare each supplied worst-case duration with its registered derivation and the observed failed prediction; an arbitrary caller number cannot silently replace the cap bound. Reduce must require retry provenance on every row, and decide must validate the registration even when every group is sparse.

## Q5 — Remaining mechanisms

**(a) Bootstrap bounds.** For each bootstrap replicate, count the physical windows attached to **each drawn parent occurrence**, separately by model. A drawn split parent contributes one `floor_j + anchor_j` allowance for *each of its drawn child windows*. If that parent is drawn five times and has two windows, it contributes ten allowances. Reusing the original dataset’s fixed window count narrows both tails.

**(b) Balance.** After the sizing pilot supplies a registered maximum, the packer should **refuse a prospective claim roster** whose worst per-cell measured-block mean-index gap exceeds it, while reporting each accepted gap. Before that receipt, it may produce clearly provisional sizing candidates, not claim-ready rosters. Append-only retries can change the gap after capture; recompute it then and mark the affected claim unresolved or schedule balanced recapture if the registered bound is exceeded. Merely reporting a known exceedance does not satisfy an acceptance bound.

**(c) Ceiling violation.** Distinguish a completed cap-hit attempt, which M2 counts incorrect with its valid gross energy, from a terminal overrun with no valid full attempt/window. Preserve the latter in the item and capture ledger as a typed `ceiling_violation`; never make it disappear through pairing or a count-based merge. Its affected level is **not estimable for the registered full-set estimand**, and that family cannot issue a headline L* until a valid registered recapture resolves the item. Other levels may still be reported descriptively, with Holm’s family size kept at five. Pairwise exclusion of the failed item from both models belongs only in the pre-registered, selection-confounded sensitivity output, never in the primary estimate.

## Q6 — Scope

Split the landing gates. Finalize the shared registration and Q2/Q5 specification first. Then gate **packer plus reducer** on timing coherence, drift acceptance, provenance, and terminal accounting; they can land as pure infrastructure without granting claim authority. Gate the **estimator** afterward against the frozen independent reference and the 1,764-case enumeration, followed by an integration replay across all three modules. This narrows each review without presenting a passing packer/reducer suite as a passing headline decision.

## Findings

No new code defect beyond the two re-audit records is asserted here. The specification choices above are recommendations for the next ruling, not a claim that the present head passes the headline gate.

## Residual risk

This was a pure-module, read-only consult. The passing 30-test command does not validate a scored-night caller, live block windows, or a post-pilot drift threshold. AP-5M and its claim policy also remain draft pending their stated cold gate and owner decision.