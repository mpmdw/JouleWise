WRITE_SCOPE: [".github/pull_request_template.md",".github/workflows/ci.yml","scripts/check_gate_ledger.py","tests/test_check_gate_ledger.py","docs/orchestration.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# INSTALL T26 cold-gate verdict item 2 — the tracked gate ledger

Linked worktree `/Users/edr/code/JouleWise-wt-t26-c`, branch
`feat/2026-09-02-t26-gateledger` @ 6075389a (main). You cannot commit; the
magistrate commits. Never run `python -m unittest discover`; named modules
only. `TMPDIR` is preset under the scratchpad. Never edit
`docs/process/state_kernel.json`, `docs/decision_log.md` (a sibling seat owns
the D-118/D-170 text), or any file outside WRITE_SCOPE. Do NOT change any
required-status-check setting, branch protection, or any existing CI job's
trigger, name, or `needs:` — the new job is ADDED, advisory, and labelled so.

## The ruling (read `:113-160` in full first)

`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 2. Ruled text (`:128-143`, verbatim):

> The gate ledger has a tracked form. (a) `.github/pull_request_template.md`
> seeds twelve rows keyed `1`–`12` (D-118 items 1–11, D-121 item 12), each
> to be filled `RUN <repo-relative-path | commit-sha>` or `NOT-RUN`; item
> 12 names the final head sha. (b) CI job `gate-ledger`
> (`pull_request: [opened, synchronize, edited, ready_for_review]`) fails
> when any of the twelve keys is missing, any row reads `NOT-RUN` or is
> empty, any `RUN` path does not resolve at the PR head (reuse
> `gen_state.py` `_check_pointer` path rules), or item 12's sha is not the
> PR head. The job is labelled ADVISORY in its own header until Ed makes
> it a required status check; the D-072 self-merge condition is that the
> job is green on the final head. (c) The pasted-block risk is DELIBERATE
> operator conduct and is out of the threat model by D-161; the job
> targets the MISTAKE class (a forgotten item), which is what the three
> forcing instances were.

D-118's items 1–11 are at `docs/decision_log.md:7770-7805` (read them; the
template's twelve row labels must be one-line paraphrases of those items,
item 12 = D-121 "magistrate's own terminal review on the final head sha",
`docs/decision_log.md:146`). The forcing instances and the 404 branch-
protection finding are at `COLD-GATE-RULING.md:115-126`.

Existing CI shape: `.github/workflows/ci.yml` jobs `test` (:17),
`calibration-exits-exclusive` (:119), `calibration-writer-crash-matrix-exclusive`
(:153), `pr-fast` (:254 — its header comment :257-275 records the standing
constraint that a job must not be promoted to a required check without a
lead-gated change; copy that constraint's wording style into the new job's
header). The `pr-fast` job shows how a PR-only job is shaped here — mirror it.

## Deliverables

1. `.github/pull_request_template.md`: a `## Gate ledger (D-118 / D-121)`
   section with a twelve-row markdown table `| # | Gate item | Evidence |`
   pre-filled `NOT-RUN` in every Evidence cell, one sentence above it telling
   the author the accepted forms (`RUN <repo-relative-path>` /
   `RUN <commit-sha>` / `NOT-RUN`) and that item 12 must name the final head
   sha; plus the existing conventional PR-body tail the repo uses
   (look at three recent merged PR bodies via `gh pr view N --json body` for
   #269, #270, #268 and keep whatever standing sections they share). Keep it
   under 40 lines.
2. `scripts/check_gate_ledger.py`: stdlib-only; reads the PR body from a
   file path (`--body-file`) or stdin, takes `--head-sha` and `--repo-root`;
   parses the ledger table (tolerate surrounding prose; the twelve keys are
   the `#` column values 1..12); exits 0 only when: all twelve keys present
   exactly once; no Evidence cell is empty or `NOT-RUN`; every `RUN <path>`
   resolves under the repo root with `gen_state.py` `_check_pointer`'s path
   rules (`scripts/gen_state.py:131-140` — import the module via importlib
   and reuse the rule, or copy the four-condition check verbatim with a
   comment naming its source — do not invent a fifth rule); every
   `RUN <sha>` is a 7–40 hex string that `git cat-file -e <sha>^{commit}`
   accepts in the repo root; item 12's sha is a prefix-match of
   `--head-sha`. Every refusal prints ONE line per defect
   `gate-ledger: item <k>: <what>` and exits 1. Print `gate-ledger: 12/12 RUN`
   on success.
3. `tests/test_check_gate_ledger.py`: defect-shaped tests, one per refusal
   branch (missing key, duplicate key, empty cell, NOT-RUN, unresolvable
   path, escaping path `../x`, bad sha, item-12 sha ≠ head, a body with
   prose around the table that PASSES), all against scratch bodies under
   `TMPDIR` and a scratch git repo you init there. No network.
4. `ci.yml` job `gate-ledger`: `on: pull_request` types
   `[opened, synchronize, edited, ready_for_review]` — CHECK the workflow's
   top-level `on:` block (:4 ff.) first: if the workflow's `pull_request`
   trigger does not already include `edited`, adding it at the top level
   would re-run EVERY job on a body edit — in that case, put the job in a
   NEW workflow file… which is outside your scope: STOP and return
   `NEEDS_RULING` naming the two options (top-level `types` widening vs a
   second workflow file `.github/workflows/gate-ledger.yml`) and land items
   1–3 + 5 anyway. The job: ubuntu, checkout, `python3
   scripts/check_gate_ledger.py --body-file <(printf '%s' "$PR_BODY")
   --head-sha ${{ github.event.pull_request.head.sha }}` with the body passed
   via `env: PR_BODY: ${{ github.event.pull_request.body }}` (never
   interpolated into the script line — injection). Header comment: ADVISORY
   until Ed makes it required (E1 = kernel row ED-BRANCH-PROTECTION-E1-01);
   D-072 self-merge is conditioned on it being green on the final head.
5. `docs/orchestration.md` §"The loop, end to end": ONE pointer line at the
   merge step: the gate ledger has a tracked form (template + `gate-ledger`
   job, D-170); fill all twelve rows before self-merge.

## Verify and report (verbatim tails)

- `python3 -m unittest tests.test_check_gate_ledger`
- `python3 scripts/check_gate_ledger.py --body-file <a scratch body you fill
  fully> --head-sha $(git rev-parse HEAD) --repo-root .` → `12/12 RUN`;
  and the same with one cell `NOT-RUN` → exit 1 with the item line
- `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"`
  (if PyYAML is absent, say so and validate with `ruby -ryaml` or report
  NOT VALIDATED — do not pip install)
- `python3 -m unittest tests.test_docs_freshness` (the template and
  orchestration edit must not trip the volatile-literal rules)
- `git status --porcelain` — only WRITE_SCOPE files dirty.

FINAL message = `claude-codex-report/v1` envelope (implementation) with a
`verification` entry per command, `flags` for any NEEDS_RULING, and a "Change"
section: each ruled sentence (a)/(b)/(c) → CONFIRMED (file:line) or NOT DONE
(why).
