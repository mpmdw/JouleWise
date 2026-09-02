# Delta re-audit 2 (luna xhigh, 238, file 17) — magistrate disposition 2026-09-02

`VERDICT: SHOULD-FIX 2` (+1 nit). Contract lens: SF1–SF5, NIT1/3/9 installed
as dictated; the three D-170 ruling spans re-measured correct. Execution
lens: clean — luna's own in-memory mutants (census `NOT-FOUND.md`, `cells[0]`,
four-column rows with empty required cells, `NOT PINNED:` in the quote
column) produced the named failures. Kernel lens: the S9-04/S9-12 mapping
verified against SHORTLIST.md by mechanism; no invented cite in the five new
rows; all seven D-170 dependencies well-formed and `blocked`.

| Finding | Disposition | Where |
|---|---|---|
| C1 (should-fix) — the NIT2 date gloss in `bridge_protocol.md` says the date is "in the report's filename or first heading", but the selector (`tests/test_docs_freshness.py:108-118`, `DATED_DIRECTORY` at `:48`) reads dated DIRECTORY components of the path, as the proposal itself says | ACCEPTED, bench: the gloss now reads "the `YYYY-MM-DD` prefix of a dated directory component of the report's path under `docs/process_traces/`". The magistrate dictated the wrong gloss in the fix-round brief (`16-fix-round-2-brief.md` NIT2); terra installed what was dictated. | bench commit |
| K1 (should-fix) — the addendum's `## Executed evidence` block used `$S` inside a quoted heredoc, so the displayed command cannot reproduce the displayed output (PD-1: evidence must be what was executed) | ACCEPTED, bench: the census was RE-EXECUTED in a replayable form (`git show … \| python3 -c "…"`, no shell variable), same 120-task / 8-row output, and the block replaced with the command actually run. In-place edit of the branch's own uncommitted-then-committed addendum text under review, not of a custodied verdict; recorded here. | bench commit |
| K2 (nit) — the addendum cited `WAVE-ROWS.md` as the provenance of the two rows while `WAVE-ROWS.md:18` lists S9-04/S9-12 as "not yet owned" | ACCEPTED, bench: provenance restated as commit `d01fd4c5` (PR #220, the wave that registered the rows; the rows' `status_note` cites WAVE-ROWS through it), with the `:18` line named as stale. The kernel rows' own `status_note` text is left as is — it is true (the wave did register them) and editing reviewed kernel prose for a stale pointer is not worth a kernel diff. | bench commit |

Rule-11 check: C1 is a defect introduced by fix round 2 (a wrong dictated
gloss), cured once; K1/K2 are defects in the magistrate's own addendum,
first surfaced here. No second fix on any defect class from earlier rounds;
no same-signature trigger. A fresh pass by a different model reads the final
head (gate item 10).
