# 41: Opus 5.5 CONTRACT lens on the TIER-01 installation (TIER01-GATE-01)

- Seat: fresh non-author contract lens (gate rows 6/8/10). Read-only, working in the detached checkout `/Users/edr/code/JouleWise-wt-817355d2-t1lens` at `7c9dadc4d591b6aa5d6e8e77acd5a36b74ed7a51`. I changed no files there; `git status --short | wc -l` gives `0` after the review.
- Authority read: `docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md` §G5 (lines 38–48) and §G8 item 7. I also read Ed's issue #415 live (`gh issue view 415`) and the branch-protection record `docs/process_traces/2026-09-24-interactive-02a24110/01-ed-rulings-harvest-and-reply-miss.md` §7. Live branch protection was queried read-only through `gh api`.
- Not executed: full test discovery (forbidden by the charge). CI on the PR was not checked because no PR exists for the branch yet (`gh pr list --head feat/2026-09-24-tier01-install` returns `[]`).

## Verdict: FIX-FIRST (text-only; no checker change required)

| # | Severity | Finding |
|---|---|---|
| M1 | MATERIAL | Decision log not reconciled. D-118 is the text the template calls "authoritative gate text". It still says every NOT-RUN item blocks merge and "A PR without a complete gate ledger is not merge-eligible". Nothing in `docs/decision_log.md` mentions TIER-01. After merge, the authoritative record contradicts the light tier. |
| M2 | MATERIAL | Status wording is stale and misdated. orchestration.md has "(proposed; cold-gated here; Ed sees the result and may veto)", which #415 overtook: Ed has "exercised [his veto] in favour". "cold-gated here" is also a copy artefact, because the gate was not held in orchestration.md. Both files say "Installed 2026-09-24", but nothing is installed until the merge (still unmerged at 2026-09-25 14:07 PDT). The day-30 date of 2026-10-24 therefore closes the G5 item-5 revert window at least one day early. |
| N1 | NIT | `main()` works out the success message with a different parse from `check()`. A body with ` Tier: light` (leading space) and 12 RUN rows is checked as full but prints `4/4 RUN; 8/8 N/A (light tier)` (case 21). The exit code is correct and only the message is wrong. |
| N2 | NIT | Fences and HTML comments are not modelled for `Tier:`. A `Tier: light` that appears only inside a fenced block or `<!-- -->` counts as the declaration (cases 06, 14), and in a comment it is invisible to reviewers. This is a deliberate-only path, so it falls outside the D-161 mistake-class threat model. Recording it is enough. |
| N3 | NIT | Workflow header "REQUIRED ... on main" is accurate for PR merges, but `enforce_admins` is `false` (live), so direct owner or bookkeeping pushes bypass the check. One clause would make this exact. |
| N4 | NIT (observation for the magistrate, not a diff defect) | #415's light gate ("one fresh non-author review plus green CI; the 12-row full ledger does not apply") is lighter than the G5 text that was installed, which still requires rows 9 and 12. The diff correctly installs G5 verbatim, and #415 is titled "TIER-01 endorsed". Any further lightening needs a new ruling. This lens does not rule on that. |

No BLOCKER. The checker is correct and fail-closed on every branch the ruling names (T2).

## T1. Conformance with COUNCIL-407-01 §G5

Executed:
```
$ git diff --stat origin/main...7c9dadc4
 .github/pull_request_template.md  | 12 ++++-
 .github/workflows/gate-ledger.yml | 24 +++++-----
 docs/orchestration.md             | 15 ++++++-
 docs/process/tier01_defect_log.md | 17 +++++++
 scripts/check_gate_ledger.py      | 21 ++++++++-
 tests/test_check_gate_ledger.py   | 93 ++++++++++++++++++++++++++++++++++-----
 6 files changed, 157 insertions(+), 25 deletions(-)
$ git diff origin/main 7c9dadc4 --stat | tail -1     # two-dot also = 6 files; the main merge added nothing
 6 files changed, 157 insertions(+), 25 deletions(-)
```

Clause by clause:
- **Item 1 (tier definition):** the text is verbatim in orchestration.md §5. I checked it line by line against ruling line 43, and it sits under `5. **Merge gate**` at orchestration.md:159. Conformant.
- **Item 2 (`Tier: full|light` plus six-line impact statement; reviewer confirms; disagreement resolves to full):** the template seeds `Tier: full|light` and the lines (i)–(vi) with `TODO`. The instruction paragraph carries the reviewer-confirms and disagreement-to-full wording. Conformant. The impact lines are not machine-checked, and the ruling does not ask for that.
- **Item 3 (full unchanged; light requires 1/9/11/12 with evidence; 2–8 and 10 read `N/A (light tier)`, accepted only under `Tier: light`):** implemented as `LIGHT_REQUIRED = {1,9,11,12}` and `LIGHT_NA = KEYS − LIGHT_REQUIRED`. Under light, the N/A rows must read exactly `N/A (light tier)`. Elsewhere that text is refused. Required rows fall through to the unchanged RUN, path, sha and item-12 logic. Conformant (T2 below). The checker refuses RUN evidence in rows 2–8 and 10 under light. That is a literal reading of "read `N/A (light tier)`", so it is conformant, just strict.
- **Item 4 (one full-tier PR editing orchestration §5, template, checker plus tests, gate-ledger.yml header; reconcile docs to branch protection):** all present. Branch protection is reconciled correctly (T4). The PR does not exist yet, so its `Tier: full` body cannot be checked. **Omission (M1):** "reconciling the docs" leaves D-118 standing, even though the template names it as the authoritative gate text.
- **Item 5 (tracked defect log, tier column, suspension rule):** `docs/process/tier01_defect_log.md` has the columns the brief specifies and quotes the suspension sentence verbatim. Conformant, apart from the installation date (M2).
- **Item 6 (day-30 review):** stated in both files. The date is wrong (M2).
- **G8 item 7 (advisory wording at orchestration.md:163 and in the gate-ledger.yml header):** fixed.
- **Overbuild:** none. The six files match items 4 and 5 exactly. There is no path validation, no impact-line parsing and no new workflow step. The only extra is the light-tier success message, which is harmless apart from N1.

## T2. Checker correctness (executed)

```
$ python3 -m unittest tests.test_check_gate_ledger
Ran 38 tests in 4.293s
OK
```

Adversarial bodies went through `check_gate_ledger.main()` with the real checkout as repo root, `README.md` as path evidence and the true head sha. The harness is `/tmp/817355d2/41-adv.py`:
```
01 control light                                               rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
02 control full                                                rc=0 | gate-ledger: 12/12 RUN
03 leading-space ' Tier: light' + light rows                   rc=1 | gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 (+7 more)
04 'Tier: Light' + light rows                                  rc=1 | gate-ledger: Tier must be full or light
05 CRLF light                                                  rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
06 Tier only in fenced block + light rows                      rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
07 fenced Tier: light + real Tier: full                        rc=1 | gate-ledger: duplicate Tier declaration
08 Tier in table cell '| Tier: light |' + light rows           rc=1 | gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 (+7 more)
09 blockquote '> Tier: light' + light rows                     rc=1 | gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 (+7 more)
10 'Tier:light' no space                                       rc=1 | gate-ledger: Tier must be full or light
11 'Tier:\tlight' tab                                          rc=1 | gate-ledger: Tier must be full or light
12 trailing space 'Tier: light  '                              rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
13 Tier after ledger (in Summary)                              rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
14 Tier in HTML comment only                                   rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
15 template placeholder + all 12 RUN                           rc=1 | gate-ledger: Tier must be full or light
16 light, lowercase n/a in row 3                               rc=1 | gate-ledger: item 3: light tier requires N/A (light tier)
17 light, wrong head sha row 12                                rc=1 | gate-ledger: item 12: sha is not the PR head
18 missing Tier + light rows                                   rc=1 | gate-ledger: item 2: N/A (light tier) is allowed only in light-tier rows 2-8 and 10 (+7 more)
19 light, row 12 = path not sha                                rc=1 | gate-ledger: item 12: final-head evidence must be a commit sha
20 'Tier: light' + 'Tier: light' duplicate                     rc=1 | gate-ledger: duplicate Tier declaration
21 ' Tier: light' leading space + all 12 RUN (main() message)  rc=0 | gate-ledger: 4/4 RUN; 8/8 N/A (light tier)
22 'Tier: FULL'                                                rc=1 | gate-ledger: Tier must be full or light
23 light, N/A with backticks row 2                             rc=1 | gate-ledger: item 2: evidence cell must be plain text (no backticks)
```

What the cases show:
- **Missing `Tier:` means full (18). A malformed one** (04, 10, 11, 15, 22) **is refused.** Refusing is stricter than falling back to full, so it fails closed. A `Tier:` that does not start at column 0 (03 leading space, 08 table, 09 blockquote) is ignored, so the body is checked as full, which also fails closed.
- **A duplicate declaration is refused** (07, 20), even when both lines are identical.
- **`N/A (light tier)`** is accepted only in rows 2–8 and 10 under a declared light tier (01). It is refused in rows 1/9/11/12 (unit test `test_light_tier_requires_evidence_in_rows_one_nine_eleven_twelve`) and under full or missing tier (18, unit test). Matching is exact (16, 23).
- **Rows 1/9/11/12 still need RUN evidence** (unit test `..._still_refuses_missing_and_invalid_required_evidence`). **The item-12 head-sha rule is unchanged** (17, 19; the diff hunk does not touch lines 187–203).
- **CRLF works** (05).
- **Findings:** N1 (case 21: the message comes from `line.strip() == "Tier: light"` in `main()`, while `check()` uses `line.startswith("Tier:")`), and N2 (cases 06 and 14). Optional N1 cure: have `check()` return the resolved tier, or have `main()` apply `line.startswith("Tier:")` before the strip. This is not required for merge.

## T3. Path validation (#415) — follow-up, not a merge condition

Why it is not a merge condition:
1. G5, the binding ruled text, defines the tier by semantic effect, and it rejects a file-name boundary *as the definition* on the grounds that one "would pass `clock.py`, the night driver and adapters". Reviewer confirmation with a disagreement-to-full rule is the ruled control.
2. #415 is titled "TIER-01 endorsed" and says "the magistrate lands TIER-01 accordingly". The path check is offered with "for example". The part that is mandatory, "a matching light-tier path", is met by the `Tier: light` branch of the checker.
3. A mis-tiered measurement change still gets row 1 (independent non-author audit), row 9 (lead full-suite replay on the integration tree), row 11 (CI green) and row 12 (magistrate terminal review of the exact head). The G5 item-5 suspension trigger backstops escapes. Defensibility does not fall below what the cold gate ratified.

A path check is still worth landing inside the 30-day window, before the day-30 review. It only refuses and can never widen the light tier, so it is a pure backstop. Exact design:
- **Workflow:** the checkout already uses `fetch-depth: 0`. Add `PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}` to `env`, then:
  `git diff --name-only "$PR_BASE_SHA"..."$PR_HEAD_SHA" > "$RUNNER_TEMP/changed.txt"`
  and pass `--changed-files "$RUNNER_TEMP/changed.txt"` to the checker. Three dots means the diff is taken from the merge base.
- **Checker:** under `Tier: light`, refuse with `gate-ledger: light tier illegal: <path> can change a number (TIER-01 item 1)` when any changed path matches:
  - `joulewise/**`, `scripts/**`, `configs/**`, `analysis/**`, `env/**`, `figures/**`, `docs/paper/**`
  - `pyproject.toml`, `package.json`, `package-lock.json`, `.github/workflows/**`
  - `CLAIMS_STATUS.md`

  If `--changed-files` is absent under light tier, refuse (fail closed). `README.md` stays with the reviewer: (vi) covers README *claims*, and routine README blurbs are the docs-only case #415 wants light. `tests/**` stays light, per #415's "test-only".
- **Tests:** one refusal per listed prefix, one acceptance for a `docs/**` plus `tests/**` diff, and one refusal when the changed-files input is missing under light.
- A cheaper complement to consider: under `Tier: light`, require each impact line (i)–(vi) to be present and not `TODO`. The impact statement is the author's evidence for the tier.

## T4. Doc accuracy

Branch protection, live:
```
$ gh api repos/mpmdw/JouleWise/branches/main/protection/required_status_checks
{"strict":false,"contexts":["gate-ledger","quick","fences","test (3.13, 1)", ... ,"calibration-writer-crash-matrix-exclusive (3.13, 2)"], ...}
$ gh api repos/mpmdw/JouleWise/branches/main/protection/enforce_admins --jq .enabled
false
```
The 02a24110 §7 record says the same thing: gate-ledger was made required on 2026-09-24 04:20 PDT, and `enforce_admins` was left off. So "required status check on `main` since 2026-09-24" is **accurate** in both the workflow header and orchestration.md.

Exact replacement texts (I rule on the wording only; no files were edited):

**(a) orchestration.md, rule heading (M2).** Replace
`**Rule TIER-01 (proposed; cold-gated here; Ed sees the result and may veto).**`
with
`**Rule TIER-01 (cold gate COUNCIL-407-01 §G5, 2026-09-24; endorsed by Ed 2026-09-25, issue #415: "gates are only meant to keep science defendable, not to overly red-tape dumb stuff like docs changes").**`

**(b) orchestration.md, trailing paragraph (M2).** Replace
```
   Installed 2026-09-24 by cold gate COUNCIL-407-01 §G5, as a D-184
   addendum. Ed was informed with veto by Gmail `1a0d364481dec249`.
   The day-30 review date is 2026-10-24; material defects and the
   suspension trigger are tracked in `docs/process/tier01_defect_log.md`.
```
with
```
   Ruled 2026-09-24 by cold gate COUNCIL-407-01 §G5, as a D-184
   addendum; Ed was informed with veto by Gmail `1a0d364481dec249` and
   endorsed the rule on 2026-09-25 (issue #415). TIER-01 is installed on
   the date its installation PR merges; the 30-day defect window and the
   day-30 review run from that merge date, which the post-merge
   bookkeeping commit records in `docs/process/tier01_defect_log.md`
   together with the review date. Material defects and the suspension
   trigger are tracked there.
```

**(c) tier01_defect_log.md, header and footer (M2).** Replace `Installed 2026-09-24 under cold gate COUNCIL-407-01 §G5 (D-184 addendum;` with `Ruled 2026-09-24 by cold gate COUNCIL-407-01 §G5 (D-184 addendum; endorsed by Ed 2026-09-25, issue #415;`. Add a line after the opening paragraph: `Installed (PR merge): <merge date, filled by the post-merge bookkeeping commit>.` Replace `Day-30 review: 2026-10-24.` with `Day-30 review: 30 days after the installation merge date above.`
(Alternative if the magistrate prefers a fixed date: set it to the merge date + 30 days in the same PR, provided the PR merges on that date.)

**(d) decision log (M1).** Directly under the existing `**AMENDED by D-170 (T26 cold gate item 2, 2026-09-02):** ...` line in the D-118 section (docs/decision_log.md:8133), add:
`**AMENDED by TIER-01 (cold gate COUNCIL-407-01 §G5, 2026-09-24; endorsed by Ed 2026-09-25, issue #415):** a PR declaring \`Tier: light\` under the TIER-01 definition completes the ledger with rows 1, 9, 11 and 12 as RUN evidence and rows 2–8 and 10 as \`N/A (light tier)\`; FULL-TIER is unchanged. See \`docs/orchestration.md\` §5.`
Add a matching index row `| D-185 | TIER-01 RISK-TIERED MERGE GATE — ... amends D-118/D-121 ... | ratified (cold gate COUNCIL-407-01 §G5; Ed endorsed 2026-09-25, #415) |`, using the next free number (the current top is D-184).
In the template, change `Row labels are keys; the authoritative gate text is D-118 / D-121 in docs/decision_log.md (and D-170 for this ledger).` to `Row labels are keys; the authoritative gate text is D-118 / D-121 in docs/decision_log.md (D-170 for this ledger; D-185 / TIER-01 for the light tier).`
This can land in this PR, which I prefer, or in the landing bookkeeping commit. Either way it must be on `main` before the first light-tier PR merges.

**(e) gate-ledger.yml header (N3, optional).** Replace
`# Ed made this a required status check on main on 2026-09-24; the`
`# D-072 self-merge condition also requires it green on the final head.`
with
`# Ed made this a required status check on main on 2026-09-24 (PR merges;`
`# enforce_admins is off, so direct owner pushes are not gated). The`
`# D-072 self-merge condition also requires it green on the final head.`

The header line "Every fresh PR is red by construction because the template seeds an unresolved Tier choice and twelve NOT-RUN rows" is accurate. The fresh template refuses on `Tier must be full or light` first (case 15; unit test `test_template_...` now asserts exactly that line).

## Merge condition summary

Apply (a)–(d) as text-only edits. The checker and tests need no change. A final-head fresh review of the text delta is enough (row 10). T3 path validation is a tracked follow-up to land before the day-30 review.
