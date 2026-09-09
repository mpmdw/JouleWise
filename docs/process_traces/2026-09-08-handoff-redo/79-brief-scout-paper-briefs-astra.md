WRITE_SCOPE: []

# Scout brief — turn the paper crosswalk's start_now rows into seat-ready briefs (gpt-6-astra, medium, read-only)
Input: the crosswalk report at the ABSOLUTE path /private/tmp/claude-501/-Users-edr-code-JouleWise/1d65b6ea-5518-4207-8f65-31f8bf376204/scratchpad/runs/paper-crosswalk.md (outside this checkout; read it with cat — it is not tracked in this worktree) (a read-only crosswalk of
the prospective comparison protocol → artifacts → producers → windows). Its verdict rows S1, S2, S4, S5, S6, S7 are
start_now; S3 and "Characterization inclusion" are needs_ruling. For EACH start_now row produce a seat-ready
implementation brief in the house shape (mission; forcing problem with file:line; exact WRITE_SCOPE as a JSON list
of existing or new repo-relative paths — no globs beyond `dir/**`; deliverables with defect-shaped regressions and
their counterfactuals; acceptance = named test modules only; constraints: D-173 custody seam via `open_paper_input`,
no touching frozen measurement inputs, no repository-wide suite, no git commit, envelope < 8192 bytes, genre
implementation verdict keys). Also: (a) a collision matrix — which briefs touch the same files (supply_map.json,
results-fill-registry.md, paper_custody.py) and therefore must run sequentially; (b) for S3 and the characterization
question, a one-page ruling packet skeleton (the question, the options with the failure each avoids, the evidence
file:lines) so the magistrate can cold-gate them; (c) the recommended order. Verify every path you name exists
(`ls`) or mark it NEW. Output (genre scout): envelope header < 8192 bytes; body = the briefs verbatim under headings
`## BRIEF S1` … so the lead can copy each into a file unchanged.
