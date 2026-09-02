WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (contract lens) — T26 item 2 install: the tracked gate ledger

Worktree `/Users/edr/code/JouleWise-wt-t26-c2` (detached @ b36d6c2d = branch
`feat/2026-09-02-t26-gateledger`, one commit over main 6075389a). Read-only:
write NOTHING in the tree; `TMPDIR` is preset under the scratchpad for any
scratch files. Never run `unittest discover`; named modules only. Do not
launch codex/claude processes.

## Your lens: RULED TEXT vs LANDED TEXT

The ruling: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 2 (`:113-160`; operative text `:128-143`, sentences (a)/(b)/(c)). The
implementer's brief is the packet you are refuting against — it is quoted
below in full so you do not need to read scratchpad files.

Check, clause by clause, and cite file:line for each verdict:
1. (a) template seeds twelve rows keyed 1–12 whose labels are faithful
   one-line paraphrases of D-118 items 1–11 (`docs/decision_log.md:7770-7805`)
   and D-121 item 12 (`docs/decision_log.md:146`). A label that drops or
   inverts a D-118 obligation is a MATERIAL finding (quote both texts).
2. (b) the job fails on each of the ruled defect classes: missing key, `NOT-RUN`,
   empty, `RUN <path>` not resolving at the PR head, item-12 sha ≠ PR head.
   Does `scripts/check_gate_ledger.py` `_valid_path` reproduce
   `scripts/gen_state.py` `_check_pointer`'s path rules (`:131-140`) EXACTLY —
   same four conditions, no fifth, none dropped? Diff them by hand.
3. (b) the ruled trigger set `[opened, synchronize, edited, ready_for_review]`
   is honoured; the job is labelled ADVISORY in its own header; nothing about
   an existing job's trigger, name, or `needs:` changed (diff
   `.github/workflows/ci.yml` against main: it must be byte-identical).
   The magistrate ruled a SECOND workflow file rather than widening ci.yml's
   untyped `pull_request` trigger — is that consistent with the ruled text,
   or does the ruling's "(b) CI job `gate-ledger` (`pull_request: [...]`)"
   require the job to live in ci.yml? Say which and why.
4. (c) the checker refuses the MISTAKE class only and does not try to
   adjudicate evidence content (D-161 boundary).
5. `docs/orchestration.md` pointer line: does it restate doctrine (forbidden:
   the ONE home is the ruling/D-170) or only point?
6. Tests: does `tests/test_check_gate_ledger.py` have one defect-shaped test per
   refusal branch of `check()`? List branches vs tests; an uncovered branch is
   a SHOULD-FIX.
7. Volatile literals: `python3 -m unittest tests.test_docs_freshness` — run it.

Verdict shape: FINAL message = `claude-codex-report/v1` review envelope with
`findings` (id, severity BLOCKER/MATERIAL/NIT, file:line, ruled text quoted,
landed text quoted, why they differ), `verification` per command run, and a
one-line `same_signature` field: "n/a (first round)".
