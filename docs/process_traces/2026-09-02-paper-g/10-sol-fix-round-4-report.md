# Paper G fix round 4 — implementation report

Role: paper-writer seat G, implementation only. The session started at
`6f9ca6e0e69a5e822a72995a5c60485a4be37ade` on
`feat/2026-09-02-paper-g`; the upstream head was identical and the worktree was
clean. No commit, push, branch operation, result inference, hardware work, or
quiet-machine work was performed. Per the launch preflight, neither the
repository-wide suite nor the broader `test_paper*` suite was run.

## Change

1. Recast the Section 7 and Section 10 Refusal carriers in the conditional
   mood of the governed Section-4 form. Each now says the result stopped at one
   of two points, states what would cause each point using “if,” and leaves
   `[FILL:OR-01]` to identify the actual point and issued reason. The governed
   Section-4 form itself remains byte-unchanged.
2. Added the same plain-language method sentence carried by Abstract A and B
   to the Abstract Refusal branch. The selected branch remains under 250 words.
3. Made the Section-7 A practice change conditional on the post-campaign
   inserted-gap check supporting application of the pulse-derived timing bound
   to inference. The later `[FILL:TR-01]` placement still supplies that result.
4. Bound the surviving REFUSAL Table 3 verdict cells. DS-32 owns the retained
   token-generation `Verdict` cell and PG-08 owns the retained
   prompt-processing `Verdict` cell. Each row now specifies the rendering when
   the verdict exists, when that verdict's absence is the issued stop reason,
   and when an earlier before-comparison stop prevented evaluation.
5. Added the registry provenance note for the in-place DS-32/PG-08 amendments:
   their Table 3 cells remain frozen-census sites, while only their repeated
   A/B paragraph placements are successor-slot sites.
6. Added a 250-word selected-Abstract guard to the selector and a
   `--check-rendered` mode that reuses the guard after all fill markers have
   expanded. The procedure makes this post-fill check a release condition.
7. Made all global fill-slot counts operate on reader-facing text with HTML
   comments removed. The selector guard test exercises the real selection CLI
   with one comment containing every globally counted marker.

The skeleton's first-use ledger required no row or count change: the added
Abstract method sentence is already present in the other two Abstract branches
and introduces no new term, home, or emphasized phrase. The mechanical ledger
passed against all three selected drafts.

## Branch table and Abstract length

Word counting is whitespace-delimited after branch selection and HTML-comment
removal. A fill marker counts as one current word; the mandatory post-fill guard
recounts its final professor-facing rendering.

| Section | A | B | Refusal |
|---|---:|---:|---:|
| Abstract | lines 27–29; **200 words** | lines 33–35; **209 words** | lines 39–41; **222 words** |
| Section 7 | lines 967–971 | lines 975–979 | lines 983–987 |
| Section 10 | lines 1211–1213 | lines 1217–1219 | lines 1223–1225 |

## FILL-to-registry map

| Marker | Placement and supplier rule | Registry state |
|---|---|---|
| `[FILL:DS-32]` | A/B paragraphs plus retained Table 3 token-generation verdict cell; authenticated decode claim evaluation, with explicit REFUSAL table renderings | `STOP_FILL`; token missing |
| `[FILL:PG-08]` | A/B paragraphs plus retained Table 3 prompt-processing verdict cell; authenticated selected-prefill claim evaluation, with explicit REFUSAL table renderings | `STOP_FILL`; G2-a/token family unresolved |
| `[FILL:OR-01]` | Exactly one stopped point plus its issued reason, supplied by governing window admission, claim evaluation, or authenticated D-165 close-out evidence | `STOP_FILL`; suppliers named/value unissued |
| `[FILL:OB-01]` | Outcome-B list of every authenticated close-out component whose `passes` value is false | `STOP_FILL`; renderer token missing |
| `[FILL:TR-01]` | Branch-independent post-campaign inserted-gap result | `STOP_FILL`; supplier named/value unissued |
| `[FILL:DG-067]`–`[FILL:DG-069]` | Existing short-input diagnostic counts in Abstract and Section 10 | Existing rows unchanged |
| `[FILL:DG-099]`–`[FILL:DG-101]` | Existing Section-7 historical diagnostic ratios | Existing rows unchanged |

## Executed evidence

### Mechanical changed-sentence first-use table

The changed reader-facing sentences were inspected in document order, then the
ledger was executed against each selected draft so that a later unselected
branch could not satisfy an early use. `S` means the sentence supplies plain
physical wording; `B` means the term is built earlier in that selected draft.

| Changed sentence group | First-use check | Result |
|---|---|:---:|
| Abstract Refusal method sentence | Deliberately started graphics-processor work, dividing-time error, allowed movement, and largest false difference are physical descriptions already used in Abstract A/B; no later definition is required. | PASS (S) |
| Section-7 A ratio sentence | Independent-edge and shared-error ratios are built in Section 1 and calculated in Section 4. | PASS (B) |
| Section-7 A transfer condition | Boundary placement, point-only variation, inserted-gap check, pulse-derived timing bound, and inference are built before Section 7. The sentence preserves “only if.” | PASS (B) |
| Section-7 A conditional practice sentence | “If that check supports the transfer” refers to the immediately preceding built condition; boundary, cell, and comparison sizing are already built. | PASS (B) |
| Section-7 Refusal stop sentence | “One of two points” is plain ordering language and asserts only one actual stop. | PASS (S) |
| Section-7 Refusal before-comparison condition | Measurement window, authenticated verdict, token generation, and prompt processing are built before Section 7. | PASS (B) |
| Section-7 Refusal close-out condition | Required ratio, authentication, and zero denominator are governed in Section 4. | PASS (B) |
| Section-10 Refusal stop sentence | Same plain one-stop wording as Section 7; it does not assert both stages occurred. | PASS (S) |
| Section-10 Refusal two conditions | Both ordered conditions and the OR-01 issued-reason rule are governed in Section 4. | PASS (B) |
| Registry, selector, procedure | Process-facing additions define each retained slot, rendering, word guard, or comment exclusion where introduced. | PASS (S) |

### Selector guard test

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/test_select_outcome_branches.py
```

Tail:

```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.217s

OK
```

The tests accept exactly 250 rendered Abstract words, reject 251, remove every
globally counted marker from HTML comments, and run an A selection successfully
when a source comment contains all five marker kinds.

### Selector and selected-draft first-use replays

Fresh directory: `/tmp/paper-g-fix-round-4-final.ISNDGB`. For each outcome, the exact
command shape was:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output /tmp/paper-g-fix-round-4-final.ISNDGB/selected-<OUTCOME>.md --outcome <OUTCOME>
PAPER_FIRST_USE_DRAFT=/tmp/paper-g-fix-round-4-final.ISNDGB/selected-<OUTCOME>.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered /tmp/paper-g-fix-round-4-final.ISNDGB/selected-<OUTCOME>.md
```

Stable tails and the three requested counts:

```text
selected A: transfer_slots=3, failed_component_slots=0, verdict_slots=4, refusal_reason_slots=1, abstract_words=200
...
----------------------------------------------------------------------
Ran 3 tests in 0.642s

OK
rendered abstract_words=200, limit=250

selected B: transfer_slots=3, failed_component_slots=3, verdict_slots=4, refusal_reason_slots=1, abstract_words=209
...
----------------------------------------------------------------------
Ran 3 tests in 0.636s

OK
rendered abstract_words=209, limit=250

selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4, abstract_words=222
...
----------------------------------------------------------------------
Ran 3 tests in 0.631s

OK
rendered abstract_words=222, limit=250
```

### Terms lint

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint
```

Tail:

```text
...
----------------------------------------------------------------------
Ran 3 tests in 1.816s

OK
```

`git diff --check` also exited 0 with no output.

## Scope and residual risk

All writes are inside the exhaustive write scope. Within the skeleton, the
diff is confined to the Abstract Refusal paragraph, Section-7 A and Refusal
paragraphs, and the Section-10 Refusal paragraph. The final Abstract budget
cannot be known until the STOP_FILL markers receive their authorized text, so
the fill operator must run `--check-rendered`; release now fails if the filled
Abstract exceeds 250 words. No result value, verdict, or refusal reason was
invented.
