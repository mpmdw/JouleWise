**NOT CLEAN** — 1 blocker (three shipped files cite a decision ID, D-170, that does not exist anywhere in the repo), 5 should_fix, 9 nits. No fail-open soundness hole: every refusal path I probed is fail-closed; the damage is false refusals on natural markdown, one GFM-spec divergence in the permissive direction, and zero regression coverage of the workflow itself.

---

## Test tail (clean tree, `HEAD = 2983cdd4e2c9d9ad81ba5d66707911e90c6312fe`)

```
$ TMPDIR=…/scratchpad/opus-c2/ python -m unittest tests.test_check_gate_ledger tests.test_docs_freshness
.....................
----------------------------------------------------------------------
Ran 21 tests in 0.831s

OK
--- final git status --short ---
[[end status: empty above]]
```

---

## BLOCKER

**B1 — `D-170` is a dangling forward reference in three shipped files.**
`.github/pull_request_template.md:5`, `.github/workflows/gate-ledger.yml:4`, `docs/orchestration.md:82`.

```
$ grep -c "D-170" docs/decision_log.md      → 0
$ grep -rn "D-170" . --exclude-dir=.git     → only the three files above
$ highest ID in docs/decision_log.md        → D-169
```

The branch does not touch `docs/decision_log.md` (5-file diff). So the PR template tells every future author *"the authoritative gate text is D-118 / D-121 in docs/decision_log.md (and D-170 for this ledger)"* and a reader following that pointer finds nothing; the workflow header claims an authority that was never written down. This is the repo's own `decided ≠ done` pattern inverted — installed-in-CI, never ruled — and doctrine rule 5 requires the decision-log entry so the convention binds future sessions.
**Cheapest fix:** add the D-170 entry to `docs/decision_log.md` in this same commit (advisory-not-required, the mistake-class threat model, the ED-BRANCH-PROTECTION-E1-01 promotion condition — all already drafted in the workflow header, so this is a copy-down).
**Cheapest regression test:** extend `tests/test_docs_freshness.py` with a scan of `docs/**.md` + `.github/**` for `D-\d{3}` tokens absent from `docs/decision_log.md`. `test_decision_index_matches_decision_bodies` currently checks index↔body only and does not cover `.github/`, which is why this shipped.

---

## SHOULD FIX

**S2 — the splitter contradicts GFM, and reads evidence from a cell the reader never sees.** `scripts/check_gate_ledger.py:19-60`, test pinned at `tests/test_check_gate_ledger.py:121`.
GFM spec, Tables extension: *"Include a pipe in a cell's content by escaping it, **including inside other inline spans**"* — spec example `` | b `\|` az | `` escapes the pipe *inside* the code span. Cell splitting is a pre-pass; a **raw** `|` inside backticks **does** split. The checker's `code_ticks` state machine suppresses that split.
Failing input (probe P7), accepted by the checker as `12/12 RUN`:

```
| 1 | gate `a | b` | RUN evidence.txt |
```

GitHub splits this into 4 cells (`1`, `` gate `a ``, `` b` ``, `RUN evidence.txt ``) and truncates to the header's 3 columns, so the **rendered** Evidence column reads `` b` `` and `RUN evidence.txt` is not displayed at all. The checker reports it green off the wrong cell. Direction of divergence is permissive.
**Mutation probe M1 (run, reverted):** I replaced `_split_table_row` with a GFM-correct 13-line splitter (split on `|` not preceded by an odd number of backslashes; no code-span tracking). Result: **14/15 pass, only `test_pipe_inside_backticked_gate_item_does_not_lose_row` fails** (`AssertionError: 1 != 0 : gate-ledger: item 4: missing`). The suite actively pins the non-GFM behavior.
**Fix:** delete the code-span machinery (42 lines → 13); *and* change `_ledger_rows:76` from `len(cells) != 3` to `len(cells) < 3` while still taking `cells[2]`, so a >3-cell row is truncated the way GitHub truncates it instead of being silently dropped.
**Regression test:** invert line 121's assertion — `| 4 | gate \`a | b\` | RUN evidence.txt |` must be **refused** (evidence cell is `` b` ``, not a path); keep a companion asserting the *escaped* form `` | 4 | gate `a \| b` | RUN evidence.txt | `` passes. This also retires the round-2 I1 class structurally: with no code-span state, an escaped backtick cannot open anything.

**S1 — a code-spanned evidence path is refused; this is the way people write paths in markdown tables.** `scripts/check_gate_ledger.py:127-141`.
Failing input (probe P1):

```
| 1 | gate 1 | RUN `evidence.txt` |
→ gate-ledger: item 1: neither a commit nor a path: `evidence.txt`
```

Same for a backticked item-12 sha → `gate-ledger: item 12: final-head evidence must be a commit sha` (probe P1b), a message that gives the author no clue the backticks are the problem. The checker spends 42 lines supporting backticks in the *Gate item* cell, so backticks in this table are plainly expected; refusing them one column over is inconsistent.
**Mutation probe M2 (run, reverted):** a 3-line strip of a surrounding code span after `target = match.group(1)` makes both P1 and P1b pass, and the existing suite stays **15/15 OK** — i.e. the behavior is unpinned in *both* directions today.
**Regression test:** `test_code_spanned_evidence_is_accepted` — body with `` RUN `evidence.txt` `` (and `` RUN `<head>` `` at item 12) asserts rc=0, `gate-ledger: 12/12 RUN`.

**S3 — `gate-ledger.yml` declares no `permissions:`.** `.github/workflows/gate-ledger.yml:38-41`.
It inherits the repo/org default token scope. `.github/workflows/d117-production-proof.yml:15-16` already establishes the `permissions: contents: read` pattern, and this is the one workflow that ingests attacker-shaped text (`PR_BODY`).
**Fix:** add `permissions:\n  contents: read` above `jobs:`. Two lines.
(The body handling itself is correct — `env:` + `printf '%s' "$PR_BODY"` with the format string as a literal, never interpolated into the `run:` line; backticks, `$`, quotes and leading `-` in the body are all inert. CRLF bodies are handled: probe P3, `\r\n` throughout → `12/12 RUN`, because `splitlines()` consumes the `\r`.)

**S4 — the workflow has zero regression coverage; the round-1 fix can be silently reverted.** No test in `tests/` reads `.github/workflows` (`grep -rln "workflows" tests/` → empty).
**Mutation probe M3 (run, reverted):** I deleted `ref: ${{ github.event.pull_request.head.sha }}` (reverting commit `1529b09a`'s "merge ref ≠ head" fix) *and* added `continue-on-error: true` (neutering the job to always-green). Result: **21/21 OK**. Both the correctness fix and the advisory-vs-inert distinction are unguarded.
**Cheapest regression test** (in `tests/test_docs_freshness.py`, no new module): read `.github/workflows/gate-ledger.yml` as text and assert (a) it contains `ref: ${{ github.event.pull_request.head.sha }}`, (b) `edited` is in the `types:` list, (c) `continue-on-error` does **not** appear (advisory means "not a required check", not "a check that cannot fail"), (d) `permissions:` is present.

**S5 — the template tells authors `NOT-RUN` is a valid fill; the checker fails the build on it.** `.github/pull_request_template.md:3` (*"Fill every row as `RUN <path>`, `RUN <sha>`, or `NOT-RUN`"*) vs `scripts/check_gate_ledger.py:124-125`.
Probe P10, the shipped template verbatim: `rc=1`, twelve × `gate-ledger: item N: NOT-RUN`.
**Fix:** one clause in line 3 — "…or `NOT-RUN`, which the advisory `gate-ledger` check reports as a defect until the row is filled."
**Regression test:** `test_shipped_template_is_refused_until_filled` — run the checker on `.github/pull_request_template.md` itself, assert rc=1 and exactly the twelve NOT-RUN lines. This also pins template↔KEYS parity (all twelve labels present, exactly once, numbered 1..12) — currently nothing checks that the template and `KEYS` agree, so a row deleted from the template would only surface as a mystery "missing" on the next PR.

---

## Workflow lens — items that checked out clean

- **`edited` does fire for body edits.** `pull_request.edited` is emitted on title/body/base change; that is the whole mechanism (ledger is filled by editing the body after the review rounds) and it is correctly chosen. Splitting it out of `ci.yml` to avoid re-running the ~17-minute matrix on every body edit is the right call and the header explains it.
- **`head.sha` vs merge ref: correct.** `RUN <path>` rows must resolve at the head, not at a synthetic merge commit; `fetch-depth: 0` is genuinely needed for `git cat-file -e <sha>^{commit}` on earlier branch commits.
- **Fork PRs work.** The head commit lives in the base repo under `refs/pull/N/head`, so `actions/checkout` with a bare-SHA `ref` fetches it; nothing here needs a write-scoped token. Two inherent caveats, both out of scope under D-161's operator-only-adversary prune: `pull_request` takes the workflow file from the PR head (a PR that deletes the workflow self-exempts), and first-time contributors need run approval.
- **"Advisory" = non-required check, no `continue-on-error`.** Consistent with the header and with the D-072 self-merge condition ("green on the final head"). Correct — `continue-on-error` would make the job green-on-defect and destroy that condition (see S4c).
- **Empty `--head-sha` fails closed** (probe P15 → `item 12: sha is not the PR head`). A body-less PR yields twelve `missing`, not a pass.

## NITS

- **N1 (contract question for the magistrate)** — `docs/x.md:12` is refused (probe P2), and so is any URL (`://` blocked at `check_gate_ledger.py:88`, probe P2b). That means item 11's natural evidence (a GitHub Actions run URL) and item 9's ("exact tail recorded") cannot be expressed except by committing a file. `gen_state.py:144-151` solves the same problem with a separate `anchor` field. Decide explicitly — accept a `:N`/`#anchor` suffix, or state in the template that evidence must be a committed artifact — rather than leaving it as an accident of the copied path rules.
- **N2** — a ledger table quoted inside a fenced code block *before* the real section produces spurious `duplicate key` (probe P12; fences aren't tracked, and `line.strip() == LEDGER_HEADING` at line 68 re-enters rather than resets). Trigger is plausible: a PR that changes the template will quote it. Fail-closed, so nit.
- **N3** — `| **1** | …` (bolded key) or an unmatched backtick in the item cell silently drops the row → `item N: missing` (probes P14, P9), with nothing pointing at the formatting.
- **N4** — heading drift, e.g. `## Gate ledger (D-118/D-121)`, yields twelve `missing` lines and never says *the ledger section was not found* (probe P13). One `if not rows: return ["gate-ledger: no '## Gate ledger (D-118 / D-121)' section in the PR body"]` would save a confused author a round-trip.
- **N5** — `run evidence.txt` (lowercase) is refused with the generic message (probe P6). Either accept case-insensitively or say so.
- **N6** — `check_gate_ledger.py:71` breaks on the **raw** `line.startswith("## ")` while line 68 matches on `line.strip()`; an indented `## Summary` would not terminate the section. Make both use the stripped line.
- **N7** — `reopened` is absent from `types:`; drafts get a red check at `opened` even though `ready_for_review` is handled.
- **N8** — `_valid_path` (`check_gate_ledger.py:84-91`) is a verbatim copy of `gen_state.py:134-140`, as its own comment admits. Two copies of the "what is an admissible repo pointer" invariant will drift; import it or add a test asserting the two accept the same set.
- **N9** — every freshly-opened PR is red by construction (the template seeds twelve `NOT-RUN`). That is the intended nudge, but it makes red the default state and trains reviewers to discount the check. Worth one sentence in the workflow header saying so deliberately.

## Overbuild prune (gate item 8)

452 lines is proportionate for what this does, with one clear cut:

- **Prune: the code-span state machine in `_split_table_row`** (`check_gate_ledger.py:19-60`, 42 lines) plus the two tests that exist only to defend it (`tests/…:121`, `:130`). It is not merely surplus — per GFM it is *wrong* (S2), and it is the sole source of the round-1 I1 defect and the round-2 patch. Replacing it with the 13-line backslash-only splitter deletes ~29 lines of code, one whole defect class, and the fix-round history attached to it. This is the single change I would require before merge alongside B1.
- **Keep:** the 26-line workflow header. It is nearly half the file, but it carries the "do not promote to a required check here — that is a lead-gated branch-protection change" warning, which is exactly the kind of instruction that must sit at the point of edit.
- **Keep:** `_is_commit` accepted for items 1–11 (up to 11 `git cat-file` subprocesses per run, negligible at this timeout). Defensible — "delta re-audit at sha X" is real evidence.
- Nothing else in the diff is fat.

## Mutation-probe ledger (3 of 3, all reverted)

| # | Finding | Mutation | Suite result | Meaning |
|---|---|---|---|---|
| M1 | S2 | `_split_table_row` → GFM-correct 13-line splitter | 14/15, `test_pipe_inside_backticked_gate_item_does_not_lose_row` FAILS | the suite pins non-GFM behavior |
| M2 | S1 | 3-line strip of a surrounding code span from `target` | 15/15 OK; P1/P1b flip to `12/12 RUN` | the false refusal is unpinned in both directions |
| M3 | S4 | delete `ref: head.sha`; add `continue-on-error: true` | 21/21 OK | the workflow has zero coverage; round-1's fix is silently revertible |

Final tree state after reverts: `git status --short` → empty (pasted above), `HEAD = 2983cdd4e2c9d9ad81ba5d66707911e90c6312fe`. No codex/claude launched; work confined to `/Users/edr/code/JouleWise-wt-t26-c2` and the scratch dir.
