WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (execution lens) — T26 item 2 install: gate-ledger checker + workflow

Worktree `/Users/edr/code/JouleWise-wt-t26-c` (branch
`feat/2026-09-02-t26-gateledger` @ b36d6c2d, one commit over main 6075389a).
Write NOTHING in the tree; `TMPDIR` is preset under the scratchpad — build
scratch PR bodies and a scratch git repo THERE. Never run `unittest discover`;
named modules only. Do not launch codex/claude processes. No network.

## Your lens: DOES IT RUN AS CLAIMED, and how does it break

Files: `scripts/check_gate_ledger.py`, `tests/test_check_gate_ledger.py`,
`.github/workflows/gate-ledger.yml`, `.github/pull_request_template.md`.
Purpose (one sentence): an advisory GitHub Actions job that fails when the
twelve-row gate-ledger table in a PR body has a forgotten item.

Attack it. For each attack, RUN it and paste the tail:
1. Parser robustness on real bodies: a body where the table is preceded by
   the template's other sections, where GitHub has normalised line endings
   to CRLF, where a cell contains a pipe inside backticks, where the heading
   has trailing whitespace, where the ledger section is the LAST section
   (no following `## `), where the whole body is empty (PR opened with no
   template — what is the failure message? is it one line per item?).
2. Ambiguity: `RUN abcdef0` where a FILE named `abcdef0` exists at the root;
   `RUN 1234567` (7 hex digits) naming a real short sha AND a real file.
   Which branch wins, and is a path made of hex characters (e.g. a run-id
   directory like `runs/…/deadbeef`) ever misclassified? Construct one.
3. Item 12: `RUN <full 40-hex head>` passes; `RUN <7-char prefix>` passes;
   `RUN <sha of the PARENT>` fails with the ruled message; uppercase hex.
4. Workflow semantics (read `.github/workflows/gate-ledger.yml`, reason,
   no network): on `pull_request` the checkout is `refs/pull/N/merge`; does
   `github.event.pull_request.head.sha` exist in that checkout at
   `fetch-depth: 0`? Does a `RUN <sha>` naming a commit on the PR branch
   resolve? A body with `%` or backslashes through `printf '%s'`? A body
   with a NUL? A fork PR (permissions)? An `edited` event that changed only
   the title — does the job still get the body? Is `concurrency` keyed
   safely when `github.event.pull_request.number` is unset (it never is on
   these four event types — confirm from the events' payload shape)?
5. Exit codes and output contract: exactly `gate-ledger: 12/12 RUN` on
   success; on failure exit 1 with ONE line per defect and nothing else on
   stdout; does any path raise instead of refusing (e.g. `--body-file`
   missing, non-UTF-8 body, `--repo-root` not a git repo → `git cat-file`
   error text leaking)?
6. Test quality: run `python3 -m unittest tests.test_check_gate_ledger`, then
   perform three mutations of `check()` (delete the duplicate-key branch;
   make `_valid_path` accept `..`; make item-12 compare case-sensitively
   with the sha uppercased) and report which tests catch each. Restore
   after each (`git checkout -- scripts/check_gate_ledger.py`; the file is
   COMMITTED, so this is safe here).

Verdict shape: FINAL message = `claude-codex-report/v1` review envelope with
`findings` (id, severity BLOCKER/MATERIAL/NIT, file:line, the reproducing
command and its tail, the fix you would make in one sentence),
`verification` per command run, `mutations` (3 entries: killed_by / SURVIVED),
and `same_signature`: "n/a (first round)".
