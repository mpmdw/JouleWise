# Reading-copy renderer implementation

## Outcome

The renderer now produces a deterministic Markdown reading copy, meaning the
same inputs produce the same file bytes. The copy removes HTML build notes,
turns every visible fill marker into a plain not-yet-measured statement drawn
from its registry row, installs the settled 21-entry bibliography, renumbers
citations without changing code or mathematics, and rewrites local figure
paths for the output directory. The check mode stops with an error if the
output is stale or retains a fill marker, a registry identifier, a task name
from the project state file, or an HTML build note.

The generated artifact is
`docs/paper/build/out/draft-v2-reading-copy.md`. Its SHA-256 fingerprint—a
fixed-length identifier calculated from the exact file bytes—is
`e1029e1bc016cbf1100c2a9f0e4cb1b2366d75f9623cc6b2a75b67447699c0a3`.
Pandoc, the document converter used for the optional Portable Document Format
(PDF) output, is not installed in this worktree environment, so no PDF was
created.

## Findings and decisions

| Finding | Evidence | Decision |
|---|---|---|
| The established citation helper protected display mathematics but not inline mathematics. A numeric interval in inline mathematics was initially read as a citation. | The first real-draft render stopped on a reference number that the settled bibliography removes; inspection located that number inside an inline mathematical interval. | Preserve every inline mathematical span before calling the existing citation helper, restore it afterward, and pin the case in the small fixture. |
| The source uses `-->` as a diagram arrow inside a fenced text block. | The first real-draft render reported an unmatched comment delimiter at the arrow lines. | Treat only `<!--` as an unmatched opening after complete comments are removed; a bare right-pointing arrow is not an HTML comment. |
| One inline equation crosses a physical line boundary in the skeleton. | The Markdown checker initially reported one unterminated inline mathematical span. | Collapse whitespace inside multiline inline mathematics to one space. The equation is unchanged and the checker now reports zero hard defects. |
| The current worktree predates the already-authored Figure 5 paper change and contains no Figure 4 insertion point. | Current output resolves Figures 1–3. Repository history contains the later Figure 5 asset and prose, while no current source paragraph references Figure 4. | Resolve every local Markdown image generically and stop on a missing referenced asset. Do not invent Figure 4 placement. Re-run check mode after the paper branches are integrated; later Figure 4 or Figure 5 references will be rebased by the same path rule. |
| The Markdown checker retains four advisory emphasis warnings in inherited Appendix and audit-ledger text. | The checker exits zero with `Hard defects: 0`; images, headings, tables, links, and mathematics all pass. | Leave source wording unchanged. These warnings are not introduced scientific claims and do not block this renderer. |

## First-use audit

The existing first-use audit mechanically checked the entire rendered paper:
224 inventoried terms and zero failures. The table below is the requested
change-class view of every new reader-facing form.

| Reader-facing change class | Changed instances | Mechanical first-use result |
|---|---:|---|
| Registry-described not-yet-measured rendering | 52 | PASS: whole rendered-document ledger test |
| Figure 3 directive converted to a reading-copy sentence | 1 | PASS: ledger home updated and checked |
| Bibliography entries assembled after citation renumbering | 21 | PASS: no new paper term introduced |

## Executed verification evidence

Only focused checks were run. The repository-wide test suite was not run, as
required by the brief.

### Focused renderer fixture

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_reading_copy -v
```

Tail:

```text
test_validation_rejects_registry_and_kernel_names (tests.test_paper_reading_copy.ReadingCopyTests.test_validation_rejects_registry_and_kernel_names) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.013s

OK
```

### Real-output check mode

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/render_reading_copy.py --check
```

Tail:

```text
checked /Users/edr/code/JouleWise-wt-fan-reading-copy/docs/paper/build/out/draft-v2-reading-copy.md
fills=52 unique_fills=49 figures=3 references=21
pdf=not requested in check mode
```

### Mechanical first-use audit

```sh
PAPER_FIRST_USE_DRAFT=docs/paper/build/out/draft-v2-reading-copy.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger -v
```

Tail:

```text
test_ledger_shape_statuses_and_count (tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_ledger_shape_statuses_and_count) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.645s

OK
```

### Markdown structure

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/build/check_markdown.py docs/paper/build/out/draft-v2-reading-copy.md
```

Tail:

```text
Undefined footnote references: 0
Non-ASCII quote/dash inventory: 240
  U+2013 EN DASH (–): 17
  U+2014 EM DASH (—): 107
  U+201C LEFT DOUBLE QUOTATION MARK (“): 27
  U+201D RIGHT DOUBLE QUOTATION MARK (”): 27
  U+2212 MINUS SIGN (−): 62
Hard defects: 0
Exit: 0
```

### Deterministic regeneration

```sh
cp docs/paper/build/out/draft-v2-reading-copy.md /tmp/joulewise-reading-copy-determinism.md && PYTHONDONTWRITEBYTECODE=1 python3 scripts/render_reading_copy.py --no-pdf && cmp /tmp/joulewise-reading-copy-determinism.md docs/paper/build/out/draft-v2-reading-copy.md && shasum -a 256 /tmp/joulewise-reading-copy-determinism.md docs/paper/build/out/draft-v2-reading-copy.md
```

Tail:

```text
pdf=disabled
e1029e1bc016cbf1100c2a9f0e4cb1b2366d75f9623cc6b2a75b67447699c0a3  /tmp/joulewise-reading-copy-determinism.md
e1029e1bc016cbf1100c2a9f0e4cb1b2366d75f9623cc6b2a75b67447699c0a3  docs/paper/build/out/draft-v2-reading-copy.md
```

### Optional PDF environment

```sh
if command -v pandoc >/dev/null 2>&1; then command -v pandoc; else echo PANDOC_NOT_INSTALLED; fi
```

Tail:

```text
PANDOC_NOT_INSTALLED
```

## Changed files

- `scripts/render_reading_copy.py` implements rendering, checking, atomic
  Markdown writes, and optional PDF conversion.
- `tests/test_paper_reading_copy.py` supplies the small deterministic fixture
  and fail-closed cases.
- `docs/paper/build/README.md` documents the extension to the existing paper
  pipeline.
- `docs/paper/build/out/.gitignore` admits the generated reading-copy outputs.
- `docs/paper/build/out/draft-v2-reading-copy.md` is the generated professor
  reading copy.
- This report records the implementation and verification evidence.

## Next exact step

After the paper branches that add later figure prose and assets are harvested,
run `PYTHONDONTWRITEBYTECODE=1 python3 scripts/render_reading_copy.py --no-pdf`
and then `PYTHONDONTWRITEBYTECODE=1 python3 scripts/render_reading_copy.py
--check`. If Pandoc is installed in that integration environment, omit
`--no-pdf` to create the PDF as well.
