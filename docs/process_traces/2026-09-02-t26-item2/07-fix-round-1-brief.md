ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: [".github/pull_request_template.md", ".github/workflows/gate-ledger.yml", "scripts/check_gate_ledger.py", "tests/test_check_gate_ledger.py", "docs/orchestration.md"]
GENRE: implementation
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 1 — T26 item 2 gate-ledger checker (branch feat/2026-09-02-t26-gateledger @ b36d6c2d)

You are in a LINKED WORKTREE. Do NOT commit, do NOT rebase, do NOT run
canonical `python3 -m unittest discover`. The magistrate commits. Run only
the suites named in ACCEPTANCE.

AUTHORITY: cold gate T26 item 2 as installed by commit b36d6c2d (read its
message and `docs/decision_log.md` D-170 body for the ruled text; D-118 /
D-121 gate items are the twelve keys). Two refuter reports found the
defects below (luna contract lens, sol execution lens). Each finding has a
dictated closure shape. Apply exactly these; report anything that does not
fit as NEEDS_RULING rather than improvising.

## Dictated closures

F-A (luna F1 blocker = sol F1). `.github/workflows/gate-ledger.yml`
checkout step: on `pull_request` events actions/checkout defaults to the
synthetic merge ref, so a path present only in the base tree passes the
"resolves at the PR head" check. Add `ref: ${{ github.event.pull_request.head.sha }}`
under the existing `with:` (keep `fetch-depth: 0`). Extend the header
comment with one sentence saying why the head sha is checked out
explicitly (merge ref ≠ PR head).

F-B (luna F2–F6, label fidelity). The twelve `Gate item` cells are KEYS,
not doctrine. Two edits: (1) directly under the table's intro sentence add
the line: `Row labels are keys; the authoritative gate text is D-118 / D-121
in docs/decision_log.md (and D-170 for this ledger).` (2) Make the five
labels faithful without becoming paragraphs — one clause each, no more than
~90 characters:
- row 3: `Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied`
- row 5: `Same-signature statement from every delta; a surviving class escalates to a consult, not round three`
- row 7: `Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded`
- row 9: `Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded`
- row 12: `Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable`
Keep the `| # | Gate item | Evidence |` shape and the pre-filled `NOT-RUN`
cells. The checker must still parse every row (it keys on the first cell).

F-C (luna F7, `_check_pointer` parity). `_valid_path` in
`scripts/check_gate_ledger.py` must reproduce ALL of
`scripts/gen_state.py` `_check_pointer`'s path predicates, including the
leading `not isinstance(path, str) or not path` refusal (read gen_state.py
around :134 and copy the conditions verbatim; keep the "Copied verbatim
from …" comment accurate).

F-D (sol F2, GFM cells). `_ledger_rows` splits on every `|`, so a
backticked cell containing an escaped pipe (`\|`) or a pipe inside a code
span loses the row. Split on unescaped pipes outside backtick code spans
(a small stdlib scanner; no new dependency). Add a test: a row whose
GATE-ITEM cell contains a code span with `\|` inside and a valid
`RUN <existing path>` evidence cell must still be counted (test asserts
zero defects for that key).

F-E (sol F3, hex-looking paths / short refs). For items 1–11 a target
matching `SHA_RE` is currently forced down the commit branch and refused
if it is not a commit, even when it is a valid repo-relative path. Rule:
for items 1–11, accept if `_is_commit(target)` OR `_valid_path(target)`;
refuse with a single message `gate-ledger: item <k>: neither a commit nor a
path: <target>` when neither holds. Item 12 stays SHA-only and must equal
the PR head (unchanged). Test both directions: a hex-only filename that
exists passes; a 7-hex string that is neither passes nowhere.

F-F (sol F4/M2, vacuous traversal test). The path-escape test at
`tests/test_check_gate_ledger.py:87` refuses `../x` because the file does
not exist, so a mutant that accepts `..` survives. Rewrite the test so the
outside target EXISTS (write a file in the temp parent directory and
reference it as `../<name>`), so only the traversal guard can refuse it.
Same for a `~`-prefixed and an absolute path to an existing file.

F-G (luna F8, pointer only). `docs/orchestration.md:81` restates doctrine.
Replace the line with a pure pointer: `Gate ledger: twelve-row PR-body
table (`.github/pull_request_template.md`), checked by
`scripts/check_gate_ledger.py` in the advisory `gate-ledger` workflow — see
D-170.` No operative words ("fill all twelve rows before self-merge") in
this file.

F-H (luna F9/F10, missing defect-shaped tests). Add tests: (a) evidence
cell `ran it, trust me` → exactly one line
`gate-ledger: item <k>: evidence must be RUN <path-or-sha>`; (b) item 12
evidence `RUN docs/README.md` (existing path) → exactly
`gate-ledger: item 12: final-head evidence must be a commit sha`.

F-I (sol F5 nit). `main()` must not traceback on an unreadable
`--body-file` or a missing `--repo-root`: catch `OSError`/`UnicodeError`,
print one line `gate-ledger: input error: <message>` and return 1. Test
the missing-repo-root case.

## Mutation check (report each)

M1 remove the `ref:` line → describe why no local test can catch this
(CI-only) and say so explicitly rather than claiming a kill.
M2 `_valid_path` accepts `..` → must be KILLED by the F-F test.
M3 drop the code-span awareness in the cell splitter → KILLED by the F-D test.
M4 for items 1–11 refuse on `not _is_commit` alone → KILLED by the F-E path test.

## ACCEPTANCE

- `python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness` green (paste the exact tail).
- `python3 scripts/check_gate_ledger.py --body-file <a temp body with 12 RUN rows, item 12 = HEAD sha> --head-sha $(git rev-parse HEAD) --repo-root .` prints `gate-ledger: 12/12 RUN`.
- `ruby -ryaml -e 'YAML.load_file(".github/workflows/gate-ledger.yml")'` exits 0 (YAML parses).
- Same-signature statement: say whether any defect class from luna 199 / sol 200 survives this round.
- Report under `## Clause map` the rows you touched: production site `file:line`, biting test `file:line`, counterfactual.

## VERIFICATION
`git diff --stat` in the report; no files outside WRITE_SCOPE touched.
