# Magistrate ruling — gate-ledger cell splitter (cold gate, rule 11)

Date 2026-09-02, session 540125d5. Trigger: a THIRD round on
`_split_table_row` and a reversal of the round-1 decision (the code-span
scanner) — mandatory cold gate. Packet: `13-cold-packet.md` (questions L1,
L2, L3) with Opus 207b's counter-review (`13b-opus-207b-counter-review.md`).
Two sealed seats: cold Fable (`14-seat-cold-fable-222.md`; fetched the GFM
spec live) and Sol xhigh read-only (`15-seat-sol-221.md`; ruled from memory of
the spec). Charter sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` verified by
both. Contamination disclosed (harness-injected doctrine / bridge prose; relied
on by neither). No packet defect found by either seat.

## Executed evidence

The dispositive premise (GitHub splits a cell on a raw `|` inside a code span)
was verified against GitHub's own renderer, not a spec reading, using the
Markdown API in `gfm` mode:

```text
$ gh api -X POST /markdown -f mode=gfm -f context=mpmdw/JouleWise -f "text=$(cat gfm-probe.md)" | <extract <tr>/<td> text>
['#', 'Gate item', 'Evidence']
['1', 'gate `a', 'b`']                       # row `| 1 | gate `a | b` | RUN evidence.txt |` — RUN evidence.txt is GONE
['2', 'gate a | b', 'RUN evidence.txt']      # row `| 2 | gate `a \| b` | RUN evidence.txt |` — escaped form renders as intended
['3', 'gate 3', 'RUN evidence.txt']          # row with a 4th cell `extra` — silently truncated
['4', 'gate `tick', 'RUN evidence.txt']      # row `| 4 | gate \`tick | RUN evidence.txt |` — escaped backtick literal
exit 0
```

The shipped checker at `2983cdd4` returns `['1', 'gate `a | b`', 'RUN evidence.txt']`
for row 1 and passes it (`scripts/check_gate_ledger.py:35-47`, pinned wrong by
`tests/test_check_gate_ledger.py:121-128`).

## L1 — ADOPT

Both seats AFFIRM Opus's reading. Spec (GFM §4.10 Tables, fetched by the
cold Fable seat): "Include a pipe in a cell's content by escaping it,
including inside other inline spans:" with the example `| b \`\|\` az |` →
`<td>b <code>|</code> az</td>`. The backslash disappears only because cell
splitting is a pre-pass that consumed it before inline parsing; a pre-pass
that sees escaped pipes inside code spans sees raw ones too. Confirmed live
above. Round 1's code-span suppression contradicted the spec; round 2 patched
a defect internal to that invention; luna 215's "CLEAN / NEW" classification
was wrong at the class level (new relative to the invented state only).

## L2 — option (c): Opus's splitter, REFUSE on arity, never mirror-truncate

Both seats reject `len(cells) < 3` / take-`cells[2]`. Reasons adopted: (1) on
the biting row both shapes refuse, but truncation misnames the cause
("evidence must be RUN …" while `RUN evidence.txt` is visibly there); (2) a
row with a valid third cell plus `extra` is something GitHub silently
discards — the checker refuses mistakes, it does not reproduce GitHub's
tolerance of them; (3) "excess is ignored" is relative to the HEADER row's
cell count, which the checker never parses — mirroring it adds a second
GitHub-modelling dependency. Model less of GitHub, not more.

Operative shape (cold Fable's, verified 18/18 in its scratch copy):

- `_split_table_row`: split on every `|`; a `|` preceded by an odd run of
  backslashes is literal and its escaping backslash is consumed; leading /
  trailing empty cells dropped; cells stripped. Docstring states the
  invariant: "no inline syntax is modelled, on purpose". Backslash parity:
  `\\|` splits (escaped backslash, then pipe); `\\\|` does not.
- `_ledger_rows`: a row whose first cell is a ledger key and whose cell count
  is ≠ 3 is a NAMED defect — `gate-ledger: item {key}: row has {n} cells,
  expected 3 (an unescaped | splits a cell even inside backticks; write \|)`
  — recorded in a `malformed: set[int]` returned alongside `rows`; `check()`
  skips the missing/duplicate/evidence logic for a key in `malformed`. Sol's
  "keep the silent `continue`" is REJECTED: it reports a present row as
  `missing`, which is false on its face (dissent recorded).
- Tests: invert `:121` (raw pipe → rc 1, exactly the one `row has 4 cells`
  line); companion escaped form `| 4 | gate \`a \| b\` | RUN evidence.txt |`
  → rc 0 `12/12 RUN`; `| 4 | gate 4 | RUN evidence.txt | extra |` → `row has
  4 cells`; `| 4 | gate 4 |` → `row has 2 cells`; keep `:130` (escaped tick)
  unchanged — a valid-GFM input that must pass under any splitter.
- Evidence cell (Opus S1, ruled here in the same spirit): the Evidence cell
  is PLAIN TEXT `RUN <path-or-sha>`; a cell containing a backtick is refused
  with `evidence cell must be plain text (no backticks)`; the template says
  so. Refuse, don't model.

## L3 — same class; structural cure

Both seats AFFIRM: rounds 0, 1, 2 and this one are one class — a hand-rolled
cell model instead of the one rule GFM states. Structural cure so that no
round 4 exists on this component: (1) the splitter implements exactly the GFM
cell rule and nothing else (above); (2) everything downstream of splitting is
REFUSED rather than modelled (arity, backticked evidence); (3) a table-driven
test over the spec's own examples plus the parity cases, asserting the
splitter's cells equal the spec's cell text before inline parsing:

```text
| f\|oo  |            -> ["f|oo"]
| b `\|` az |         -> ["b `|` az"]
| b **\|** im |       -> ["b **|** im"]
| abc | def |         -> ["abc", "def"]
| bar |               -> ["bar"]
| bar | baz | boo |   -> ["bar", "baz", "boo"]
abc | def             -> ["abc", "def"]
| a `b | c` |         -> ["a `b", "c`"]        # raw pipe in code span SPLITS
| a \\| b |           -> ["a \\", "b"]         # escaped backslash then pipe: splits
| a \\\| b |          -> ["a \\| b"]           # only the pipe-escape is consumed
```

Any future "helpful" inline-aware splitting fails the `` a `b | c` `` row;
any regression to `split("|")` fails `f\|oo`.

Flagged, not ruled (a different class, not evidence of a round 4 here):
table-CONTEXT divergence — the checker treats every pipe line after the
heading as a candidate row regardless of GFM's "table is broken at the first
empty line" and of a quoted ledger inside a fenced block (Opus N2). Shape if
closed later: a numbered row not in the first contiguous pipe-block after the
heading is refused, not parsed. Goes to the fix-round-3 brief as a should-fix
with that shape.

## Disposition

Fix round 3 (a model other than luna, who holds the delta) carries L2/L3
verbatim plus Opus 207b's S1–S5 and N1–N9; delta re-audit by luna; the
same-signature statement in the delta must classify against THIS ruling's
class definition, not the round-2 "NEW" label.
