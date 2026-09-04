# Paper G fix round 3 — implementation report

Role: paper-writer seat G, implementation only. The session started and ended
at `b868b965092f3024e0cda87135337180370d3d5a` on
`feat/2026-09-02-paper-g`; the upstream head was identical. The starting
worktree was clean. No commit, push, branch operation, result inference,
hardware work, or quiet-machine work was performed. Per the launch preflight,
the repository-wide suite and the broader `test_paper*` suite were not run.

## Change

- Treated the existing Section-4 Refusal form as the governed OR-01 contract.
  Its three sentences now appear verbatim in exactly four places: the Section-4
  form and retensing-plan Outcome C, H04-C, and H27-C. H04-C now contains the
  sentence block beneath its heading rather than relying on the heading alone.
- Updated the retensing-plan Outcome-C summary to name both ordered stop points
  and the OR-01 issued-reason rendering. Under the magistrate's exact-location
  fence, the governed literal was not propagated into any other retensing
  variant.
- Kept the Abstract, Section 7, and Section 10 Refusal carriers in plain
  language. Each now separately names a stop before comparison and a stop at
  close-out, then uses `[FILL:OR-01]` for the applicable stop and its issued
  reason.
- Made the branch-selection procedure say that Refusal has exactly those two
  ordered stop points and that OR-01 prints the stop and reason issued by the
  governing evidence. The selector's governed label continues to name both
  points; its adjacent comment records that contract.
- Tightened the OR-01 registry row so every placement renders exactly one of
  the two stop labels plus the reason issued by the corresponding authenticated
  supplier. The row remains `STOP_FILL`; no value or verdict was invented.
- Updated the skeleton ledger's Abstract entry for `issued reason` and the two
  named stops. No Section-1 definition change was needed.

## Literal contract census

The three fixed strings were searched separately after the edit. Each search
returned the same four locations:

| Governed location | Current line |
|---|---:|
| Section-4 outcome form | `draft-v2-skeleton.md:771` |
| Retensing Outcome C | `round7/retensing-plan.md:26` |
| Retensing H04-C sentence | `round7/retensing-plan.md:103` |
| Retensing H27-C sentence | `round7/retensing-plan.md:395` |

No Abstract, Section-7 branch, Section-10 branch, selector, procedure, registry,
or other retensing entry contains the governed literal.

## Mechanical changed-sentence first-use table

The selected-draft ledger test reads the title, one selected Abstract, and then
the body in reader order. `S` means the sentence uses plain words or supplies
the physical meaning in place; `B` means the referent was built earlier in the
selected draft.

| Changed sentence group | First-use check | Result |
|---|---|:---:|
| Abstract Refusal: two stop points | “Before comparison” and “at close-out” are ordinary ordering words; the measurement period, input-reading result, output-token result, missing value, source match, and division by zero are stated physically. | PASS (S) |
| Abstract Refusal: OR-01 carrier | “Applicable stop” and “issued reason” are plain descriptions; OR-01 is a registered replacement slot rather than unexplained result prose. | PASS (S) |
| Section-7 Refusal: before-comparison condition | Section 1 and Section 4 already built measurement windows, authentication, token generation, prompt processing, and verdict use. | PASS (B) |
| Section-7 Refusal: close-out and OR-01 | Section 4 already built required ratios, authentication, evaluation, zero denominator, both stop points, and the issued-reason slot. | PASS (B) |
| Section-10 Refusal: before-comparison condition | The same terms are built in Sections 1 and 4 before the Conclusion. | PASS (B) |
| Section-10 Refusal: close-out and OR-01 | The same close-out predicate and slot are governed in Section 4 before the Conclusion. | PASS (B) |
| Retensing Outcome-C summary | Both stop points and the OR-01 rendering are described in ordinary words; the detailed governed form follows in the plan. | PASS (S) |
| Retensing Outcome C / H04-C / H27-C | `tests.test_paper_terms_lint` mechanically checked the insertions against their draft insertion points and returned zero findings. | PASS |
| Selector comment, procedure, registry, ledger | Process-only text defines its own label, stop-point, supplier, or ledger meaning in place. | PASS (S) |

The first final replay found one useful collision before delivery: the singular
word `stage` in the Refusal Abstract matched the older ledger alternative
`stage / block member`, whose approved home is later in the paper. The prose
was changed to the plain `stop`/`point` wording above, and every requested check
was rerun from fresh copies.

## Executed evidence

Fresh output directory:
`/tmp/paper-g-fix-round-3-final.0eWqjJ`.

For each of `A`, `B`, and `REFUSAL`, the exact replay shape was:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-3-final.0eWqjJ/selected-<OUTCOME>.md --outcome <OUTCOME>
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-3-final.0eWqjJ/selected-<OUTCOME>.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
```

Stable tails:

```text
selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1
...
----------------------------------------------------------------------
Ran 3 tests in 0.799s

OK

selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1
...
----------------------------------------------------------------------
Ran 3 tests in 0.644s

OK

selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4
...
----------------------------------------------------------------------
Ran 3 tests in 0.653s

OK
```

Terms-lint command and tail:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint
```

```text
...
----------------------------------------------------------------------
Ran 3 tests in 1.819s

OK
```

`git diff --check` also exited 0 with no output. Final `HEAD` and upstream both
remained `b868b965092f3024e0cda87135337180370d3d5a`.

## Scope and residual risk

All writes are inside the exhaustive write scope. Within the skeleton, changes
are confined to the Abstract Refusal paragraph, Section 7 “What the finding
changes” Refusal paragraph, Section 10 Refusal paragraph, and the first-use
ledger. OR-01, DS-32, PG-08, OB-01, and TR-01 remain unfilled registry-governed
slots; final prose still depends on their authenticated suppliers and renderers.
