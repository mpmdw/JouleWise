# Cold-gate ruling — gate-ledger cell splitter (branch `feat/2026-09-02-t26-gateledger` @ `2983cdd4`)

## Disclosure

- **Charter digest verified:** `shasum -a 256 docs/process/coldgate_charter.md` in `/Users/edr/code/JouleWise-wt-t26-c2` (HEAD `2983cdd4e2c9d9ad81ba5d66707911e90c6312fe`, `git status --short` empty before and after my work) = `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` — matches the packet. Read §3–§5 and §8 as instructed.
- **Read set:** `PACKET.md`; `207b-opus-counter-review.md` (same directory); `scripts/check_gate_ledger.py` and `tests/test_check_gate_ledger.py` in the worktree (read-only); the charter sections above; the GFM spec at https://github.github.com/gfm/ §4.10 "Tables (extension)" — **fetched live via WebFetch**, dispositive sentences quoted verbatim under L1. Nothing else in the repo was opened.
- **Contamination:** the harness injected into my context, before the packet, the contents of `~/.claude/CLAUDE.md`, `JouleWise/CLAUDE.md`, `JouleWise/CLAUDE.local.md`, and the auto-memory index `MEMORY.md` (with one-line summaries of memory files). I saw them; I relied on none of it. Every conclusion below cites the packet, the spec, or the code lines I ran. I did not open any memory file, README, RUN_STATE, TASK_QUEUE, orchestration, or playbook.
- **Probes:** copies of the script and tests under `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/coldfable-ledger/repo/`, `TMPDIR` exported there, run with `python -m unittest tests.test_check_gate_ledger` (never `discover`). No codex/claude launched. Nothing written in the worktree.
- **Packet hygiene (§6):** no defect found. The packet presents Opus's claim as a claim, names the pinning test, and asks the counter-question (truncate vs refuse) rather than assuming Opus's cure. One note: the packet's History labels the Opus proposal "S2 + prune section"; the Opus file also contains B1/S1/S3–S5/N1–N9, which are outside the three enumerated questions and I do not rule on them.

---

## L1 — Does GitHub split a cell on an unescaped `|` inside a backtick code span?

**Verdict: AFFIRM Opus's reading → ADOPT.** Severity of the shipped behavior: **MATERIAL** (permissive divergence: the checker passes off a cell the rendered table does not show as Evidence).

**Spec citations (fetched, verbatim, GFM §4.10 Tables (extension)):**

1. Definition: *"Each row consists of cells containing arbitrary text, in which inlines are parsed, separated by pipes (`|`)."* — cells are the unit; inlines are parsed **inside** cells, i.e. after the cell boundaries exist.
2. The dispositive sentence: *"Include a pipe in a cell's content by escaping it, including inside other inline spans:"* followed by the example

   ```
   | f\|oo  |
   | ------ |
   | b `\|` az |
   | b **\|** im |
   ```
   whose output is `<th>f|oo</th>`, `<td>b <code>|</code> az</td>`, `<td>b <strong>|</strong> im</td>`.

**Why the example is dispositive (not merely suggestive):** CommonMark does not process backslash escapes inside code spans — `` `\|` `` in a paragraph renders as `<code>\|</code>`. The spec output shows `<code>|</code>`. The only way the backslash disappears is that the table's cell-splitting pass consumed the `\|` escape *before* inline parsing. Therefore cell splitting is a pre-pass that sees pipes inside code spans; if it sees escaped pipes there, it sees raw pipes there too, and a raw pipe splits. The spec had to write `` `\|` `` precisely because `` `|` `` would not have stayed in one cell. (The implementation behind GitHub, cmark-gfm's table extension, scans a cell as `(escaped_char | [^|\r\n])+` — no backtick tracking; my ruling rests on the spec text, the implementation is corroboration from memory.)

**Verified at the primary source:** the shipped checker at `2983cdd4` on a body whose row 1 is `| 1 | gate \`a | b\` | RUN evidence.txt |` returns `rc=0`, `gate-ledger: 12/12 RUN` (run end-to-end, above). Its splitter (`scripts/check_gate_ledger.py:35-47`, the `code_ticks` state) returns `['1', 'gate `a | b`', 'RUN evidence.txt']`. GFM returns four cells `1`, `` gate `a ``, `` b` ``, `RUN evidence.txt`, and per *"If there are greater, the excess is ignored"* GitHub renders three, with Evidence = `` b` ``. The suite pins the wrong behavior at `tests/test_check_gate_ledger.py:121-128`.

**Counterfactual that bites:** any Gate-item cell whose author writes a raw `|` inside backticks (e.g. quoting a shell pipeline `` `a | b` ``, or the pinned test's own `` `escaped \| and raw |` ``) shifts the row right by one; the reviewer sees garbage in Evidence, the check is green.

**Not decided:** whether GitHub's *current* production renderer differs from the spec on this point. It should not (both cmark-gfm and comrak pass the spec example), and the packet says the magistrate will verify live; L2 gives the exact row to paste.

---

## L2 — The cure

**Verdict: (c) — Opus's splitter, NOT Opus's truncation.** Adopt the deletion of the code-span machinery and the backslash-parity-only split; **REJECT `len(cells) < 3` / take-`cells[2]` mirror-truncation; REJECT option (b)**; rule that a numbered row with cell count ≠ 3 is **REFUSED with an explicit message**. Severity of shipping (a) as proposed: NIT-to-MATERIAL (it is fail-closed on P7 but with a misleading message, and it silently accepts a 4-cell row).

**Why (b) is rejected:** keeping the scanner leaves the L1 divergence intact — the scanner still returns 3 cells for P7, so no truncation ever triggers. (b) cures nothing.

**Why refuse beats mirror-truncate (the fail-closed question):**

1. On the biting input `| 1 | gate \`a | b\` | RUN evidence.txt |`, both refuse, but (a) says *"evidence must be RUN <path-or-sha>"* while the author can see `RUN evidence.txt` right there — a message that misnames the cause and invites another round. Refusal by count names it: *row has 4 cells*.
2. On `| 1 | gate 1 | RUN evidence.txt | extra |`, (a) passes (GitHub also renders it fine). Refusing is strictly more conservative: the author typed something GitHub silently discards, and the checker's charge is to refuse mistakes, not to reproduce GitHub's tolerance of them.
3. Mirror-truncation adds a second GitHub-modelling dependency: *"excess is ignored"* holds only relative to the **header row's** cell count, which the checker never parses (`_ledger_rows:63-81` assumes three columns). A PR whose header has four columns renders four cells and truncates nothing — (a)'s `cells[2]` would then be "Evidence" only by luck. Refusing `≠ 3` keeps the checker's contract independent of that: *the ledger is a three-column table, full stop.* This is the same reasoning as L3 — model less of GitHub, not more.
4. Today's `len(cells) != 3: continue` (`:76`) is already fail-closed but reports it as `item N: missing`, which is wrong on its face (the row is present). The cure converts a silent skip into a named refusal; nothing becomes more permissive.

**Operative code shape (verified: 18/18 on the copied suite; P7 body → the one refusal shown; the escaped form passes; `\` literal-tick test at `:130` still passes unchanged):**

```python
def _split_table_row(line: str) -> list[str]:
    """Split a GFM table row exactly as the Tables extension does: on every
    pipe, BEFORE inline parsing; the only exception is a backslash-escaped
    pipe, literal "including inside other inline spans". Nothing else
    (backticks, emphasis) is modelled, on purpose."""
    cells: list[str] = []
    cell: list[str] = []
    backslashes = 0
    for char in line:
        if char == "|":
            if backslashes % 2 == 1:
                cell.pop()          # the pre-pass consumes the escaping backslash
                cell.append("|")
            else:
                cells.append("".join(cell).strip())
                cell = []
            backslashes = 0
            continue
        cell.append(char)
        backslashes = backslashes + 1 if char == "\\" else 0
    cells.append("".join(cell).strip())
    if cells and not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return cells
```

In `_ledger_rows`, replace `:76-77` with: if `cells[0].isdigit()` and `int(cells[0]) in KEYS` and `len(cells) != 3`, record a defect
`gate-ledger: item {key}: row has {n} cells, expected 3 (an unescaped | splits a cell even inside backticks; write \|)` and do not record evidence for that row; `_ledger_rows` returns `(rows, defects)` and `check()` skips the missing/duplicate/evidence logic for any key that already has a row-shape defect (I probed this with a substring match; the clean shape is a `malformed: set[int]` alongside `rows`). Parity note: `\\|` (escaped backslash, then pipe) **splits**; `\\\|` does not; only the pipe-escaping backslash is removed, an escaped backslash stays in the raw cell text — this matches the spec grammar and is pinned in the table test below.

**Tests:**
- Invert `:121`: `| 4 | gate \`a | b\` |` → rc 1, stdout exactly the one `row has 4 cells` line.
- Companion: `| 4 | gate \`a \| b\` |` → rc 0, `12/12 RUN`.
- Count test: `| 4 | gate 4 | RUN evidence.txt | extra |` → `row has 4 cells`; `| 4 | gate 4 |` → `row has 2 cells`.
- Keep `:130` (`\`` literal tick) unchanged — it is a valid-GFM input that must pass under any splitter; it no longer defends a state machine.
- Table-driven spec test (see L3).

**Live-verification recipe for the magistrate (GitHub rendering).** Paste this as a PR body (or any issue comment) and view it rendered:

```
| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | gate `a | b` | RUN evidence.txt |
| 2 | gate `a \| b` | RUN evidence.txt |
| 3 | gate 3 | RUN evidence.txt | extra |
```

What must appear for L1/L2 to stand: row 1 renders **three** cells reading `1` · `` gate `a `` (a backtick and the letter a, no code formatting since the span is unterminated) · `` b` `` — the text `RUN evidence.txt` is **not visible anywhere** in row 1. Row 2 renders `2` · `a | b` in code formatting · `RUN evidence.txt`. Row 3 renders three cells with `extra` **absent**. If row 1 instead shows `a | b` as code with `RUN evidence.txt` in the third column, GitHub has diverged from its published spec and L1 must be re-ruled; do not adopt the cure in that case.

**Counterfactual that bites:** the P7 row (refused by count, with the cause named), and the 4-cell-with-valid-third-cell row (refused under this ruling, accepted under (a)).

**Not decided:** (i) whether `\|` inside an Evidence path should be unescaped before `_valid_path` (the splitter now does unescape it, matching the spec's `<th>f|oo</th>`; no repo path contains `|`, moot); (ii) Opus S1 (code-spanned evidence path refused) — a different column and a different question, not before me; (iii) whether the row-count message text is final; (iv) table-context rules (blank line ends a table, delimiter row must match header) — see L3.

---

## L3 — Same-signature classification and the structural cure

**Verdict: AFFIRM — rounds 0, 1, 2 and this one are one class: the checker's cell model is a hand-rolled guess at what GitHub does instead of the one rule GFM states.** Severity of the pattern: MATERIAL (three fix rounds and a pinned wrong test are the cost so far).

- Round 0: `line.split("|")` — wrong on `\|` (over-splits). Model ≠ GFM.
- Round 1: added `\|` handling **and** invented code-span suppression (`:35-47`). The first half is GFM; the second half is not in the spec and contradicts it. Model ≠ GFM, and the test at `:121` pinned the invention.
- Round 2: patched a defect *internal to the invention* (escaped backtick opening `code_ticks`, `:28-34`). A fix to a rule that should not exist. Same class — and the luna "CLEAN / classified NEW" verdict on it was wrong at the class level: it was new only relative to the invented state, not relative to GFM.
- This round: the invention itself is the defect.

**Structural cure such that no round 4 exists on this component:**

1. The splitter implements exactly GFM §4.10's cell rule and nothing else: split on every `|`; a `|` preceded by an odd run of backslashes is literal and its escaping backslash is consumed; leading/trailing pipe optional; cells whitespace-trimmed. **No inline syntax is modelled** — the code's docstring says so, so that the next reviewer who "fixes" backtick handling is contradicting a stated invariant, not filling a gap. (Code shape in L2; 30 lines including docstring.)
2. The checker refuses rather than models everything downstream of splitting: cell count ≠ 3 → refuse (L2). It never reproduces "excess ignored" or "empty cells inserted".
3. A table-driven test over the spec's own examples, asserting the splitter's cells equal the spec's `<td>`/`<th>` text before inline parsing, plus the parity cases the spec grammar implies (all verified passing in my scratch copy):

   ```
   | f\|oo  |            -> ["f|oo"]
   | b `\|` az |         -> ["b `|` az"]
   | b **\|** im |       -> ["b **|** im"]
   | abc | def |         -> ["abc", "def"]
   | bar |               -> ["bar"]
   | bar | baz | boo |   -> ["bar", "baz", "boo"]
   abc | def             -> ["abc", "def"]
   | a `b | c` |         -> ["a `b", "c`"]        # raw pipe in code span SPLITS
   | a \\| b |           -> ["a \\\\", "b"]       # escaped backslash then pipe: splits
   | a \\\| b |          -> ["a \\\\| b"]         # only the pipe-escape is consumed
   ```
   With this table in place, any future "improvement" to the splitter that models inline syntax fails the `` a `b | c` `` row; any regression on escapes fails the spec rows. That is what closes the class.

**Counterfactual that bites:** a future author adds bold-aware or link-aware splitting "to be helpful" — the table test refuses it. A future author reverts to `split("|")` — the `f\|oo` row refuses it.

**Not decided (and explicitly a *different* class, so not evidence of a round 4 on this one):** table-structure divergence — the checker treats every `|` line after the heading as a candidate row regardless of GFM's *"The table is broken at the first empty line, or beginning of another block-level structure"* and regardless of whether a header/delimiter row exists; Opus N2 (quoted ledger inside a fenced block) lives here too. Those are section/table-context rules, not the cell model, and the packet did not put them to me. If the magistrate wants them closed with the same philosophy, the shape is again *refuse, don't model*: a numbered row that is not in the first contiguous pipe-block after the heading is refused, not parsed. I flag it; I do not rule it.

---

**Disagreement with the labelled disposition (charter §8):** the packet carries no lead disposition on the merits, only Opus's proposal; I disagree with Opus on the `< 3` truncation (L2) and with the round-2 "CLEAN / NEW" classification (L3). I concur with Opus on L1 and on deleting the code-span machinery.