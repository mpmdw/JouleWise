# LITREAD-VERIFY-01 — verify the related-work sources of record (Opus seat, read-only + web)

Queue row (TASK_QUEUE.md, LITREAD-VERIFY-01): pre-submission verbatim re-verification of the two
load-bearing related-work sources against the PDFs of record: TokenPowerBench (arXiv 2512.03024) and
"The Illusion of Power Capping in LLM Decode" (arXiv 2605.11999). Earlier readings went through an HTML
extraction; this pass must read the PDF of record (or, if the PDF cannot be fetched, the arXiv HTML of the
SAME version, stating the version read).

Work in `/Users/edr/code/JouleWise-wt-paper-n-ref` (detached origin/main dbe6c675). Do not edit files.
Article: `docs/paper/draft-v2-skeleton.md` — §6 "Related work" (lines ~865–893) and §9 "References"
(lines ~945–973); also any in-text citation of [6]/[7]-style numbers elsewhere in the main text (grep for
the bracketed reference numbers used in §6).

## Tasks

1. Fetch https://arxiv.org/pdf/2512.03024 and https://arxiv.org/pdf/2605.11999 (fall back to
   https://arxiv.org/abs/… and the HTML render, and say which). Record title, authors, version and date
   as printed.
2. For EVERY statement the article makes about each of the two works (claims about what they measure,
   report, group by, disclose, or omit; every number attributed to them; every quoted phrase), build a table:
   article sentence (section:line, quoted) → source location (section/page, quoted supporting text) →
   verdict MATCH / PARTIAL / MISMATCH / NOT FOUND → proposed minimal cure if not MATCH.
3. Reference-list check for ALL entries in §9: does each entry's title/authors/year/identifier resolve to a
   real work as listed (arXiv abs page, DOI, or publisher page)? Table: entry → resolved URL → OK / FIX
   (say what is wrong). Do not rewrite the list.
4. Note the queue row's id correction (TokenPowerBench = 2512.03024; Illusion = 2605.11999) and confirm the
   article cites each under the right id.

Report: ONE Markdown file at
`/Users/edr/code/JouleWise-wt-paper-n/docs/process_traces/2026-09-12-paper-n/08-litread-verify-opus.md`
with the three tables, a tiered findings list (blocker / should-fix / nit), and an explicit statement of what
could NOT be verified and why. No prose restyling proposals; sources of record only.
