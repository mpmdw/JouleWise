# Fable final pass (gate-ledger row 7) — TIER-01 installation, merge candidate 7c9dadc4

**Contamination disclosure.** Besides the charge I loaded, automatically at session start: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers only; they include lines about issues #415/#416 and the 09-25 activation checkpoint, which I did not open). I read §G5 of the ruling file `docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md`, and four lines (§7 heading and first paragraph) of `docs/process_traces/2026-09-24-interactive-02a24110/01-ed-rulings-harvest-and-reply-miss.md` to verify the citation the diff adds. One over-broad `git grep -i advisory` incidentally printed unrelated matching lines from `RUN_STATE.md` and `TASK_QUEUE.md`; none concerned the gate ledger and I did not read those files otherwise. I did not open `53-tier01-install-brief.md`, `53b-tier01-report.md`, the activation record, or any memory file. I also queried GitHub read-only (`gh api` branch protection, `gh issue view 415`, `gh pr list`). No loop context.

Judge: Claude Fable 5.1, cold, single foreground session, no subagents or background tasks. Repository read-only. Wall ≈ 20 min.

## Verdict: FIX-FIRST (text only), then MERGE

No BLOCKER. Two MATERIAL text defects in the very rule being installed (it still calls itself "proposed … Ed may veto" after Ed endorsed it, and it dates its own installation to a day before the installing PR exists). Both are exact-text fixes in the same PR, no new review round beyond the final-head rule. Checker is correct and fail-closed on every adversarial body I ran. The #415 path-validation ask is a follow-up, not a merge condition; exact design below.

| # | Severity | Finding |
| --- | --- | --- |
| F1 | MATERIAL | `docs/orchestration.md` rule header "(proposed; cold-gated here; Ed sees the result and may veto)" is stale: Ed exercised the veto in favour in #415 on 2026-09-25. Replacement text under T4. |
| F2 | MATERIAL | "Installed 2026-09-24" and day-30 date 2026-10-24 (in `docs/orchestration.md` and `docs/process/tier01_defect_log.md`) predate installation. `gh pr list --head feat/2026-09-24-tier01-install --state all` returns `[]`: the PR does not exist yet, so nothing was installed on 09-24. The 30-day revert clock (§G5 item 5) runs from merge. Replacement text under T4. |
| F3 | NIT | `scripts/check_gate_ledger.py` `main()` success line uses a different predicate (`line.strip() == "Tier: light"`) from `check()` (`line.startswith("Tier:")`). An indented `  Tier: light` with twelve RUN rows exits 0 (validated as full, correct) but prints `4/4 RUN; 8/8 N/A (light tier)` (wrong). Exit code is right; message is misleading. Case E below. |
| F4 | NIT | Code fences are not modelled: a `Tier: light` line that appears only inside a fence counts as the declaration (case F). Consistent with the existing ledger parser's documented non-modelling of fences and D-161's threat model; a fenced declaration plus a real one refuses as duplicate (case G). Note only. |
| F5 | NIT | `docs/decision_log.md:10884` ("Until E1, `gate-ledger` is advisory") and `:11142` ("Until Ed makes it required, `gate-ledger` stays ADVISORY") are historical, conditionally-true sentences whose condition has since resolved. §G5 item 4 asks the install PR to "reconcile the docs to the actual branch-protection state"; a one-line dated addendum under D-170 completes that. Text under T4. Not a merge condition. |
| F6 | NIT | Workflow header and orchestration text attribute the protection change to "Ed's 2026-09-24 branch-protection update" / "Ed made this a required status check". Record 02a24110 §7 shows the PATCH was executed in Ed's interactive session on Ed's "sensible for science" condition. Close enough; optional wording under T4. |

## T1. Conformance to §G5

**Executed.** `git diff --stat origin/main...7c9dadc4` → exactly the six files the charge names (157 insertions, 25 deletions). §G5 item 4 prescribes editing together `docs/orchestration.md` §5 merge gate, the PR template, the checker with its tests, the `gate-ledger.yml` header, and reconciling docs to the actual branch-protection state; item 5 requires a tracked defect-log file. All present:

- Rule text in `docs/orchestration.md` is the §G5 text verbatim (diffed by eye against the ruling; items 1–6 identical, including the "(proposed; …)" header, which is now the F1 problem, not a conformance problem).
- Template: `Tier: full|light` seed plus the six-line (i)–(vi) impact statement; instruction paragraph states rows 1, 9, 11, 12 required and 2–8, 10 = `N/A (light tier)`; matches §G5 items 2–3.
- Checker + tests: light path as ruled; tests updated (38 tests, all pass, see T2).
- Workflow header: advisory language removed; states required-on-main since 2026-09-24 with a record citation. Verified true (T4).
- `docs/process/tier01_defect_log.md`: table with date / defect / PR / tier / changes-a-number / found-by, suspension rule quoted, day-30 review named. Matches items 5–6.

Nothing missing. Nothing overbuilt: no path validation, no new workflow steps, no new CLI flags. The only reconciliation gap is F5 (historical decision-log sentences), a NIT.

## T2. Checker correctness (executed)

```
$ python3 -m unittest tests.test_check_gate_ledger
......................................
Ran 38 tests in 4.300s
OK
```

Code-path reading of `check()`: tier is resolved before the ledger is parsed; `>1` Tier lines → refuse; a Tier line not exactly `Tier: full` / `Tier: light` (after strip) → refuse; no Tier line → `full`. Under light, rows in `LIGHT_NA` = {2..8, 10} must equal `N/A (light tier)` exactly, else "light tier requires …". In any other row, or under full, `N/A (light tier)` is refused before the NOT-RUN / RUN branches. Rows 1, 9, 11, 12 fall through to the unchanged RUN logic; row 12's sha-resolves-and-is-head rule is untouched (lines 212–218 of the script unchanged by the diff).

Adversarial bodies, all twelve rows otherwise valid (`RUN README.md`, row 12 = `RUN <HEAD>`), run with `--head-sha $(git rev-parse HEAD) --repo-root .`; bodies kept in `/tmp/817355d2/adv/`:

| case | body | rc | first output line |
| --- | --- | --- | --- |
| A | `Tier: light`, 8 N/A rows | 0 | `4/4 RUN; 8/8 N/A (light tier)` |
| B | same, CRLF line endings | 0 | same (fail-open safe: `splitlines()` strips `\r`) |
| C | `Tier: Light` | 1 | `Tier must be full or light` |
| D | `  Tier: light` (leading spaces), 8 N/A rows | 1 | item 2 … allowed only in light-tier rows (falls back to full) |
| E | `  Tier: light`, 12 RUN rows | 0 | **`4/4 RUN; 8/8 N/A (light tier)`** ← F3, message only |
| F | `Tier: light` inside a ``` fence only, 8 N/A | 0 | accepted ← F4 |
| G | real `Tier: full` + fenced `Tier: light` | 1 | `duplicate Tier declaration` |
| H | `\| Tier: light \|` in a table | 1 | falls back to full; N/A rows refused |
| I | `Tier:light` | 1 | `Tier must be full or light` |
| J | `Tier: light (docs only)` | 1 | `Tier must be full or light` |
| K | `Tier: light   ` (trailing spaces) | 0 | accepted (strip) |
| L | light, row 2 = `n/a (light tier)` | 1 | `item 2: light tier requires N/A (light tier)` |
| M | light, row 12 = `N/A (light tier)` | 1 | `item 12: … allowed only in light-tier rows 2-8 and 10` |
| N | light, row 12 = a real non-head sha (`c6814dd8`) | 1 | `item 12: sha is not the PR head` |
| O | `Tier: light` placed after the ledger | 0 | accepted (position-independent, fine) |
| P | UTF-8 BOM before `Tier: light` | 1 | falls back to full; N/A rows refused |
| Q | the verbatim PR template | 1 | `Tier must be full or light` (matches new tests) |
| R | no Tier line, 12 RUN | 0 | `12/12 RUN` |
| S | `Tier: light`, 12 RUN rows | 1 | `item 2: light tier requires N/A (light tier)` |

Every ambiguous or malformed declaration resolves to full or to refusal; no body reached exit 0 with fewer than the required evidence rows for its resolved tier. Case S is a deliberate design consequence (a light PR must mark the eight rows N/A rather than over-fill them); acceptable and tested by the diff. **T2 answer: correct and fail-closed.** One cosmetic defect (F3); fix is one line, for example `if any(line.startswith("Tier:") and line.strip() == "Tier: light" for line in body.splitlines()):`, or better, have `check()` return the resolved tier. Optional in this PR.

## T3. Against #415: path validation is a follow-up, not a merge condition

Reasoning on defensibility, not ceremony:

1. What protects the science today is (a) the default: no or malformed tier → full twelve rows (cases D, H, I, J, P, Q); (b) the independent non-author reviewer confirming the tier, with disagreement resolving to full (§G5 item 2, template text); (c) the 30-day revert trigger that suspends TIER-01 on a single number-changing escape (item 5). A wrongly declared light tier therefore needs a mistaken author *and* a mistaken reviewer to pass, and its first escape ends the rule.
2. §G5's criterion is semantic ((i)–(vi)); the ruling explicitly notes "a file-name boundary would pass `clock.py`, the night driver and adapters" as the reason not to make paths the rule. A path check can only be a *backstop* under that rule, never the rule. Ed's #415 says "for example", which reads as illustrative, and rule 3 ("when unsure, full") is already what the checker's fallback does.
3. The backstop's marginal catch is the mistake class the checker exists for (D-161): an author who types `Tier: light` on a diff that touches `joulewise/`. That is worth having and cheap, but it is not what keeps a number honest at merge time; the reviewer's read of the diff is.

Therefore: **follow-up**, opened before the first light-tier merge is attempted, and landed as a FULL-tier PR (it changes the gate itself; "when unsure, full"). Exact design:

- **Workflow** (`gate-ledger.yml`): the checkout already has `fetch-depth: 0` at the head sha. Add, before the validate step:
  ```yaml
  env:
    PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}
  run: |
    git fetch --no-tags --depth=1 origin "$PR_BASE_SHA"
    git diff --name-only "$(git merge-base "$PR_BASE_SHA" HEAD)" HEAD > "$RUNNER_TEMP/changed-files.txt"
  ```
  and pass `--changed-files "$RUNNER_TEMP/changed-files.txt"` to the checker. No token or API call; `permissions: contents: read` is unchanged.
- **Checker**: new optional `--changed-files <file>`. Under `Tier: light`, a missing file refuses (`gate-ledger: light tier requires the changed-file list`), and any path matching `FULL_TIER_PREFIXES` refuses with `gate-ledger: light tier is illegal: <path> is full-tier`. Under full, the list is ignored. Prefixes, drawn from §G5 item 1 and the repository layout at 7c9dadc4:
  `joulewise/`, `scripts/` (Ed's #415 names it whole; the few CI-only scripts such as `check_gate_ledger.py` pay the full gate, which is the safe direction), `configs/campaigns/`, `configs/model_panels/`, `configs/analysis_registry/`, `configs/calibration/`, `configs/arm_readiness/`, `analysis/`, `docs/paper/`, `docs/report_src/`, `README.md`, `CLAIMS_STATUS.md`, `pyproject.toml`, `.github/workflows/`. Everything else (other `docs/`, `tests/`, `.github/pull_request_template.md`, the status files) is light-eligible; the reviewer still confirms.
- **Tests**: light + touched `joulewise/x.py` refuses; light + only `docs/x.md` passes; light with no list refuses; full with touched `joulewise/x.py` and no list passes.

Wording for Ed's "matching light-tier path": the diff already provides it (declared `Tier: light`, checker-validated ledger shape); only the "against the diff's paths" half is deferred.

## T4. Doc accuracy (executed)

```
$ gh api repos/mpmdw/JouleWise/branches/main/protection --jq '.required_status_checks.contexts'
["gate-ledger","quick","fences","test (3.13, 1)",…,"calibration-writer-crash-matrix-exclusive (3.13, 2)"]
```
`gate-ledger` is a required status check on `main` now. The workflow header and the orchestration sentence are accurate. The cited record exists and §7 ("E8 applied: required status checks on `main` (04:20 PDT 2026-09-24)") says what the diff says it says.

**F1, stale header.** Replace in `docs/orchestration.md`:

> `**Rule TIER-01 (proposed; cold-gated here; Ed sees the result and may veto).**`

with

> `**Rule TIER-01 (cold-gated by COUNCIL-407-01 §G5 on 2026-09-24; endorsed by Ed in GitHub issue #415 on 2026-09-25).**`

**F2, install date.** Replace the closing paragraph in `docs/orchestration.md`:

> Installed 2026-09-24 by cold gate COUNCIL-407-01 §G5, as a D-184 addendum. Ed was informed with veto by Gmail `1a0d364481dec249`. The day-30 review date is 2026-10-24; material defects and the suspension trigger are tracked in `docs/process/tier01_defect_log.md`.

with

> Ruled 2026-09-24 by cold gate COUNCIL-407-01 §G5 as a D-184 addendum; Ed was informed with veto by Gmail `1a0d364481dec249` and endorsed the rule in GitHub issue #415 on 2026-09-25. Installed at the merge of the installation PR on 2026-09-25 (set the PR number here at merge). The 30-day revert window and the day-30 review run from that merge: day-30 review 2026-10-25. Material defects and the suspension trigger are tracked in `docs/process/tier01_defect_log.md`.

and in `docs/process/tier01_defect_log.md` replace the first paragraph and the last paragraph's date:

> Ruled 2026-09-24 under cold gate COUNCIL-407-01 §G5 (D-184 addendum; Ed informed with veto by Gmail `1a0d364481dec249`, endorsed in issue #415 on 2026-09-25) and installed at the merge of the installation PR on 2026-09-25. For 30 days from that merge, record every material defect found after merge, including the tier of the PR that merged it.

> Day-30 review: 2026-10-25. …

(If the PR merges on a later date, both dates move with it; the magistrate's item-12 read is where that gets checked.)

**F5, decision-log reconciliation (optional, NIT).** Append under the D-170 dated addendum (after `docs/decision_log.md:11142`):

> **Dated addendum (2026-09-25):** `ED-BRANCH-PROTECTION-E1-01` was applied on 2026-09-24 (interactive record 02a24110 §7); `gate-ledger` is a required status check on `main`. `ED-D118-NA-TIER-E2-01` is answered by rule TIER-01 (COUNCIL-407-01 §G5, Ed's issue #415), installed in `docs/orchestration.md` §5.

**F6, attribution (optional, NIT).** In `gate-ledger.yml`, "Ed made this a required status check on main on 2026-09-24" → "Made a required status check on main on 2026-09-24 in Ed's interactive session (record 02a24110 §7)". Same substitution for "Ed's 2026-09-24 branch-protection update" in the header's first line and in `docs/orchestration.md`.

## Not executed

- The GitHub Actions run itself (no PR exists; `gh pr list` empty). The local invocation is the same command line the workflow runs.
- Full test discovery (charge forbids); only `tests.test_check_gate_ledger`.
- Merge-order simulation against sibling PRs: `origin/main` is `c6814dd8`, which 7c9dadc4 already merges; no open sibling PR touches these six files as far as `git diff --stat` shows, but I did not enumerate open PRs.

## Merge instruction

Apply F1 and F2 (text only) as one commit on `feat/2026-09-24-tier01-install`; F3, F5, F6 at the magistrate's discretion in the same commit. The final-head rule applies: one fresh read of that commit, then the magistrate's item-12 review. This installation PR is itself FULL tier (§G5 item 4): all twelve rows. Open the T3 follow-up as a tracked row before the first light-tier merge.
