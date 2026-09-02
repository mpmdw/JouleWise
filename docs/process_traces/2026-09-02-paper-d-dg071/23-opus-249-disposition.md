# Opus 249 counter-review (gate item 6) — magistrate disposition (2026-09-02)

Seat: Opus 5 (contract lens), fresh `Agent`, read-only in the detached
worktree at `8ab397b5` (PR #276 head); sealed report custodied as
`22-opus-249-counter-review.md`. Verdict: BLOCKER 0 / SHOULD-FIX 5 / NIT 5.
Independent replication of all eight values of record; file 18's replay and
file 21's mutation kills both reproduced.

## Same-signature statement (gate ledger item 5) and escalation

Delta 2 (terra 248, file 20) found two surviving mutants that change a
published value; both were cured at the bench (file 21). The counter-review
found two MORE surviving mutants of the same class (C-1: IQR rendered as the
difference of rendered quartiles → `5.9507`; nonzero-boundary count using the
tolerance → `0`). That is two consecutive rounds failing with the same
signature — "a reported field with no test that pins its value on an input
where the wrong computation differs". Under rule 11's standing escalation
trigger the next spend is a CONSULT, not a third pair of hand-added fixtures:
Sol 250 (xhigh, read-only, brief file 24) is asked for the coverage SHAPE
(magistrate candidate: one hand-derived golden bundle with a full-payload
assertion) before any further fix round. The addendum's own cold-gate clause
("a same-signature re-audit failure") names the population/precision
signature of the physics refutation, which did NOT recur (values of record
replicated three times independently); the coverage signature is a test
adequacy class, so the instrument is a consult, and this reading is recorded
here for the cold gate to overrule if it disagrees.

## Dispositions

- **C-1** (two more value-changing mutants survive) — ESCALATED to the Sol 250
  consult (above); fix round 3 follows the ruling on its shape. The two
  mutants stay open until then.
- **C-2** (addendum item 4's "≤ 2.4e-7 s, exactly that" is the float64
  figure; the literals give max 4e-7 s) — CURED by a dated correction at the
  end of the addendum, with the bench histogram as executed evidence (decimal
  gaps 1e-7 ×4, 2e-7 ×49, 3e-7 ×46, 4e-7 ×1; float64 gaps 2.384e-7 ×100).
- **C-3** (six terms of art used before they are built: literal, contiguous,
  order statistics, round-half-even, values of record, the retained writer's
  endpoint convention) and **C-4** ("tiling" names two fields and is defined
  nowhere in the artifact) — ACCEPTED; producer prose edits, dictated in the
  fix-round-3 brief so the artifact is re-issued once, not twice. Opus's
  glosses in §2 are adopted with the magistrate's wording.
- **C-5** (ledger rows 5 and 8 cite files without the labelled check) —
  ACCEPTED. Row 5 now cites THIS file (the statement above). Row 8 now cites
  `MAGISTRATE-NOTES.md` for this trace, whose overbuild prune adopts Opus §6
  and C-6.
- **C-6** (two write-only dataclass fields) — ACCEPTED into fix round 3
  (drop `_ParsedRow.row_number`, `SamplerRecord.interval_start_literal`).
- **C-7** (addendum writes numeric equality where the code requires literal
  equality) — CURED by the same dated correction as C-2 (one word, and the
  reason relaxing it is not made).
- **C-8** (envelope byte counts 4251/3557 in files 18/21 vs 4166/3387 in the
  stored files) — EXPLAINED, not an error: the counts were measured on the
  seat reports before custody; custody rewrites the session scratchpad path
  to `<scratchpad>`, shortening the envelope (85 and 170 bytes). Recorded
  here; the files are not rewritten.
- **C-9** (unredacted scratchpad path in file 19) — CURED (sed at the bench;
  the same redaction applied to file 22). The out-of-lane occurrences Opus
  lists (`2026-09-02-projection-02/`, `2026-09-02-coldgate-dx-t26a/`,
  `RUN_STATE.md`) are noted for the post-merge batch on main.
- **C-10** (JSON `method.iqr` lacks the last-place caveat that the Markdown
  carries) — ACCEPTED into fix round 3.

## Executed evidence

```
$ cd /Users/edr/code/JouleWise-wt-paper-d
$ grep -c 540125d5 docs/process_traces/2026-09-02-paper-d-dg071/19-delta-2-brief.md docs/process_traces/2026-09-02-paper-d-dg071/22-opus-249-counter-review.md
docs/process_traces/2026-09-02-paper-d-dg071/19-delta-2-brief.md:0
docs/process_traces/2026-09-02-paper-d-dg071/22-opus-249-counter-review.md:0
exit=1
$ python3 -c "import re;[print(f,len(re.search(r'(?m)^\`\`\`json[ \t]*\r?\n(.*?)^\`\`\`[ \t]*$',open('docs/process_traces/2026-09-02-paper-d-dg071/'+f).read(),re.S).group(1).encode())) for f in ['17-sol-247-fix-round-2.md','20-terra-248-delta-2.md']]"
17-sol-247-fix-round-2.md 4166
20-terra-248-delta-2.md 3387
exit=0
```
