# Paper 1 seat 10: Opus review of the outline restructure and working title

Reviewer: Opus 5.5 (cold seat; did not build seat 10 and did not serve seats 4, 6 or 9).
Written: 2026-11-11 00:38 PST (from `date`).
Branch under review: `docs/2026-11-11-paper1-outline` @ `f7b1b27fc` (implementation commit `e38ff5b32`), cut from
`origin/main` @ `62a87aaad`. Old `paper1.md` SHA-256 `21976909…079551b`, which matches the map's header.
Rulings read with `git show origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/…` (ref
`cb2f1e938`): RL-8, RL-9, RL-24 (seat 10 row), RL-39, RL-40, RL-43, RL-46 (seat 9's verdict), and
`paper-audit.md` §8.1 and §9 E4.
Seat 9's head was read only to test the fence by merging: `docs/2026-11-11-paper1-automation` @ `7932b73e4`.
The research lead reviews after this seat.

Boundaries: no custody, `night-*`, archive or restricted path was opened, and nothing outside the review worktree
except git objects. No Block 6, BYTES held-out or v4 content was read. No number was checked against
`RESULTS.md`, because this seat adds none and none was added.

## Verdict: ADMIT-WITH-FIXES

The restructure does what RL-8 asks. Boundaries come before the method, Block 5 is presented as validation,
BYTES comes second, the title names only released parts, and the method section is at about half its old length.
Apart from headings, section cross-references and the three listed subtitle cuts, every moved paragraph is
byte-identical. The appendix holds the moved material and no material was lost. The fill index regenerates
byte-stably. Three fixes are required before merge, all small and all structural:

- **F-1**: the §7 fence.
- **F-2**: a sentence the move left dangling in §4.8.
- **F-3**: Tier E's keep and replace pointers.

None of them needs new prose.

## (1) Moves and listed cuts only: paragraph identity

I scripted the check independently of the seat's own verifier; the script is reproduced at the end of this
report. It splits both manuscripts into blank-line-delimited units. Then it checks every row of the map's
303-row table against the actual old and new line spans, ignoring digits and whitespace so that section numbers
and split points can move. It confirms that split character spans are contiguous, and it counts FILL, FACT,
BRANCH and HTML-comment multisets.

| Check | Result |
|---|---|
| Old units / new units | 303 / 323 |
| Old units byte-identical somewhere in the new file | 211, with no multiplicity mismatch |
| Map rows verified against both files | 303 of 303. Split rows: 7 units into 17 pieces, contiguous spans, only separating whitespace at each split |
| Rows that differ apart from digits and whitespace | 13 headings, 1 cut (C1), and 3 text rows: P016 (`(Section 3)` became `(Sections 3 and 4; Appendix D)`, a cross-reference), P074 (cut C2) and P075 (cut C3) |
| New body lines outside every map destination | 0. No added prose |
| Cross-reference number changes | 87 single-number changes, plus one range ("Sections 5.2-5.5" → "6.2-6.5") and one expansion (P016), all following the section map (3.2→4.1 … 3.9→3.2, 5.7→6.8, 5.8→6.7, 6.6→3.3, 7.x→8.x, 8→9, 9→11). No paper-internal "Section N" reference outside FACT comments was left stale. Every reference resolves to a heading |
| FILL occurrences | 215 → 214; only `CP-X02-headline` is gone (C1) |
| FACT comments | 25 / 25, byte-identical multiset |
| BRANCH markers | 70 / 70, identical multiset. No branch was selected or deleted |
| HTML comments / images | 34 / 34 and 6 / 6 |
| Cuts C1–C3 | Exactly as listed. C1 is the whole subtitle FILL slot. C2 is ` and the paper's contingent subtitle`. C3 is ` or license the contingent subtitle`. Each is ruled under RL-8 ("No 'attribution-limited' subtitle prints") |

**New headings.** Every new or reworded heading is taken from the `paper-audit.md` §8.1 outline: §3, §3.4, §4, §5,
§6, §7, §8, §10, and the D.1–D.7 appendix headings and pointers. The exception is §8, covered under F-1. The §4.7
heading drops "and the scaled sensitivity line" because that paragraph moved to D.6. That is consistent.

**Cuts C1–C3 are outcome-informed but authorised.** RL-8's blind status says the subtitle rule "follows the
released branch". So the cut of a dominance-conditional slot is a post-release edit made with knowledge of
Block 5. It is ruled, so it is not a seat selection. A–1 below covers what it means for §1.2.

## (2) The RL-43 fence

| Item | Result |
|---|---|
| §7 moved as one contiguous block | Yes. Old lines 1289–1398 became new lines 1172–1281, 110 lines each, in place between BYTES and Limitations |
| Anything cut inside §7 | Nothing |
| Anything edited inside §7 | **14 lines differ**. Three are heading-number-only (`### 7.1/7.2/7.3` → `8.x`). One is a **retitle** of the section heading. Ten carry 11 cross-reference renumberings (block lines 30, 31, 43, 46, 47, 57, 58, 63, 97, 103) |
| FACT comments in §7 | 3 / 3, unchanged |
| RL-40 single full statement | Kept. §1.2 line 94 holds the one full statement ("After the primary release, on 10 November 2026, …"). §8.2 item 7 and §9 keep the short pointer "Corrections made after release are stated in Section 1.2." |
| `build_fill_index.py` | Untouched, so seat 9's §7 source strings are not contended |

**Merge test.** `git merge-file` of seat 9's `paper1.md` (`7932b73e4`) onto this head, with `62a87aaad` as base,
gives **3 conflict hunks**:

- the `### 8.2` heading, beside seat 9's inserted "What armed each collection" text;
- §8.2 item 2's renumbered cross-references;
- §8.3's "rate-aware mapping of Section 4.2" bullet.

I made a variant with the §7 body and title restored byte-identical and only the four heading numbers changed. That
variant leaves **1 hunk**: the `### 8.2` heading. That hunk is unavoidable, because seat 9 inserts text on the line
above a heading whose number must change.

### F-1 (required): leave the inside of §7 to seat 9

RL-43 says seat 10 "moves §7 as one block and cuts nothing inside it", and the brief makes any change inside §7 a
defect. Two kinds of change break that.

- **The retitle**: `## 7. Research automation: an agent-driven pipeline and its controls` became
  `## 8. Research automation: controls, and where they failed`. The move does not require it. The §8.1 outline
  pairs that title with the rewrite "from the half-A ledger", which is seat 9's work, and seat 9 kept the old
  title. Restore the old wording under the new number: `## 8. Research automation: an agent-driven pipeline and its
  controls`. Retitling is seat 9's or the final read's call.
- **The 11 renumbered cross-references inside the block.** These are correct on their own terms. But seat 9
  rewrites those very lines, which causes two of the three conflicts. Seat 9 must renumber its own new text after
  the rebase anyway: RL-46's F-1 wording uses old numbers, "(Section 4.6)" and "(Section 7.3)". Revert the
  block's body to byte-identical. List the 11 references in the map as **handed to seat 9**, with the old→new
  table below, so that seat 9 renumbers all of §8 in one pass during its rebase.

Changing `## 7.` → `## 8.` and `### 7.x` → `### 8.x` stays. That is the move itself.

Old→new section numbers for seat 9's rebase: 3.1→3.1, 3.2→4.1, 3.3→4.2, 3.4→4.3, 3.5→4.4, 3.6→4.5, 3.7→4.6,
3.8→4.7, 3.9→3.2, 3.10→4.8, 4.x→5.x, 5.1–5.6→6.1–6.6, 5.7→6.8, 5.8→6.7, 6.1–6.5→7.1–7.5, 6.6→3.3, 7.x→8.x, 8→9,
9→11. FACT locators are not renumbered.

RL-46 notes that §7's length is "seat 10's and the final read's business". RL-43 bars seat 10 from cutting inside
§7, so any shortening waits until after seat 9 merges. I flag this but it is not a fix.

## (3) The title

The H1 is **"What a Laptop's Power Counters Can Resolve: A Pre-registered, Blinded Measurement of LLM Inference Energy
on Apple Silicon"**. It is word-for-word the `paper-audit.md` §8.1 working title that Ed approved under E4 / RL-24.

| Check | Result |
|---|---|
| Names only released parts (RL-8) | Pass. It names the instrument and a pre-registered, blinded measurement, which is Block 5 (released). It does not name the replication, BYTES or energy per byte, all of which the old title named |
| "Attribution Limits" | Gone, and the contingent "attribution-limited" subtitle slot is cut (C1). No other subtitle prints |
| Tripwire phrase (RL-9, E4) | Absent. No "sabotage", "tripwire" or "energy signature" appears anywhere in `paper1.md`. §10 is an empty heading, "Outlook: physical auditing of agents", reserved for seat 13 |
| Final wording | Correctly left to Ed and the 5 December scope freeze |

## (4) The appendix: a move, not a cut

Every sentence is accounted for. With HTML comments, FILLs and headings removed:

| Section | Words |
|---|---|
| Old phase method (old §3 minus §3.1 and §3.9) | 3,630 |
| New §4 | 1,870 |
| Appendix D | 1,750 |
| New §4 plus Appendix D | 3,620 |

The 10-word difference is exactly C2 (5 words) plus C3 (5 words). The seat's 53.4% (1,974 / 3,699) counts headings
and reproduces exactly. Without headings the figure is 51.5%. Either way it is "about half" as RL-24 asks. All 17
split pieces are verbatim spans of their source units, as described under (1).

Some of the moved material is defining text rather than derivation: the reported-cell estimator steps (D.3), the
two floor forms (D.4), the dominance branch rules (D.5) and the contrast estimator (D.7). §4 keeps the definitions
that the results cite, and the subsection headings point to the appendix. I accept this under "derivations to an
appendix". The research lead may want the D.4 form definitions back in §4.5.

### F-2 (required): a dangling lead-in in §4.8

§4.8 still ends its first paragraph with "Over n kept quads (at least five of ten):". The numbered list that the
colon introduced now opens D.7 with no lead-in. The next thing in §4.8 is "The outcome is one of four registered
words". Fix it by a move only. Either split that clause from P088 (old L477–478) and move it to the head of D.7, or move
P089 (the D.7 list) back into §4.8. Record whichever is done in the map.

## (5) The fill index and tests

| Check | Result |
|---|---|
| `python3 -I docs/paper/paper1/build_fill_index.py` (repo root) | Prints `234 213 217 173`. The tree stays clean afterwards, so the committed index is reproduced byte for byte |
| Fill index against `origin/main`, with digits ignored | Only three differences: the `CP-X02-headline` row is gone (C1); the new-ids list is reordered (`P1-BY-KB` and `P1-B5-METER` move earlier with their sections); two FILL descriptions have renumbered section pointers (P1-B6-SIDEBYSIDE 5.2-5.5→6.2-6.5, CP-X08-decode-a-conclusion 5.5/5.7→6.5/6.8). Everything else is line numbers. All of this is expected |
| `python3 -B -m unittest tests.test_paper_build` (3.14.6 and 3.13) | 5 tests, OK, 2 skipped (`markdown-it-py` absent) |
| `python3 -I -m unittest tests.test_paper_build` | Fails with `No module named 'tests'`. This is a harness artefact, not a defect: `-I` drops the working directory from `sys.path` |
| `docs/paper/build/check_markdown.py paper1.md` | 0 hard defects |
| `git diff --check` | Clean |
| `RUN_STATE.md`, `TASK_QUEUE.md`, state kernel | Untouched |

## Variants

All variant edits are section-pointer and heading renumbering, which I checked by diff.

### F-3 (required): Tier E's keep and replace lists no longer cover §3

Old Tier E kept "§3 (method)". That section included the measurement boundary (old §3.1) and the DC-input
boundary (old §3.9), which are now §3.1–§3.2. The new header keeps only "§4 (method)". Old Tier E also replaced
"§5", which included the whole-machine cross-check paragraph that is now §3.4 with an unfillable `P1-B5-METER`.
New Tier E does not replace §3.4.

Fix, as pointer changes only:

- the header keeps "§2 …, §3.1 to §3.2, §4 (method), §5 (design) …" and replaces "… §3.4, §6, §7.5 and §11";
- the README row for Tier E changes to match.

Optionally, Tier E's §1.3 item 1 can read "(Sections 3 and 4)" to agree with the main text. §3.3 (old §6.6) was
neither kept nor replaced before, and that is unchanged.

## Advisory, not required for this seat

- **A-1, for the research lead: does §1.2's provenance statement cover this seat?** RL-40's statement says that
  statements of fact and branch glosses were corrected after release and lists them in `CORRECTIONS-2026-11-10.md`.
  This restructure is also a post-release change by Block-5-aware seats, and C1–C3 follow the released dominance
  branch. Seat 10 rightly did not touch §1.2 (RL-43). Whether §1.2 gains a clause pointing to
  `OUTLINE-MAP-2026-11-11.md` is the research lead's wording to give.
- **A-2.** The abstract still names the replication, as a collected-and-blinded status, and BYTES Part 2, as a
  FILL. RL-8's rule for the abstract applies at the 5 December scope freeze. Changing the abstract is not a move,
  so it is not seat 10's work.
- **A-3. Prose for later seats.**
  - §3.3, the known-bytes text, now sits before BYTES defines "pass-1" and "stage-1", which makes those forward
    references.
  - The §3.4 heading repeats its own bold run-in label "**Whole-machine cross-check.**".
  - D.2 and D.5 begin with leftover hard line breaks at split points ("If the displacements of the 59⏎pulses",
    "In the⏎synthetic examples above"). These render correctly.
- **A-4.** The empty §10 renders as an empty section until seat 13 fills it. That is acceptable for a working
  draft.
- **A-5.** `docs/paper/paper1/DRAFT_NOTES.md` item 1 still discusses the "attribution-limited" subtitle. It is
  stale under RL-8, and pruning it is the lead's call.

## Paragraph-identity script (reproducible)

Run from the repository root, after `git show 62a87aaad:docs/paper/paper1/paper1.md > /tmp/old.md`:
`python3 -I p1o_identity.py /tmp/old.md docs/paper/paper1/paper1.md docs/paper/paper1/OUTLINE-MAP-2026-11-11.md`

```python
import re, sys, collections
O = open(sys.argv[1]).read(); N = open(sys.argv[2]).read(); MAP = open(sys.argv[3]).read()
ol, nl = O.split('\n'), N.split('\n')
units = lambda t: re.split(r'\n\s*\n', t.strip('\n'))
mask = lambda t: re.sub(r'\s+', ' ', re.sub(r'\d+(\.\d+)?', '#', t)).strip()
ou, nu = units(O), units(N)
oc, nc = collections.Counter(ou), collections.Counter(nu)
print('1 units old/new', len(ou), len(nu), '| old units byte-identical in new', sum(1 for u in ou if nc[u]),
      '| multiplicity mismatches', sum(1 for u in oc if nc[u] and nc[u] != oc[u]))
bad, pieces, cov = [], 0, set()
for r in re.findall(r'^\| P\d{3}, L.*$', MAP, re.M):
    pid, a, b, dest = re.match(r'\| P(\d+), L(\d+)–(\d+) \| .*? \| (.*) \|$', r).groups()
    src = '\n'.join(ol[int(a)-1:int(b)])
    if dest.startswith('cut'): bad.append((pid, 'CUT')); continue
    spans = []
    for s, e, c, f in re.findall(r'(?:`\[(\d+):(\d+)\]`\s+)?(?:[A-Za-z0-9.]+,?\s*)?L(\d+)–(\d+)', dest):
        cov.update(range(int(c), int(f)+1)); dst = '\n'.join(nl[int(c)-1:int(f)])
        part = src[int(s):int(e)] if s else src
        if s: pieces += 1; spans.append((int(s), int(e)))
        if mask(part) != mask(dst): bad.append((pid, 'HEADING' if src.startswith('#') else 'TEXT', dst[:90]))
    spans.sort()
    if spans and not (spans[0][0] == 0 and spans[-1][1] == len(src) and all(x[1] == y[0] for x, y in zip(spans, spans[1:]))):
        bad.append((pid, 'SPAN-GAP'))
unmapped = [i+1 for i, l in enumerate(nl) if l.strip() and not l.startswith('#') and i+1 not in cov]
print('2 split pieces', pieces, '| non-identical rows:', collections.Counter(k[1] for k in bad),
      '| new body lines outside any map destination', len(unmapped))
for k in bad:
    if k[1] == 'TEXT': print('   TEXT', k)
for name, p in [('FILL', r'\{\{FILL:\s*([^|}\s]+)'), ('FACT', r'<!--\s*FACT[\s\S]*?-->'),
                ('BRANCH', r'\*\*\[(?:END )?BRANCH [^\]]*\]\*\*'), ('COMMENT', r'<!--[\s\S]*?-->')]:
    a, b = collections.Counter(re.findall(p, O)), collections.Counter(re.findall(p, N))
    print('3', name, sum(a.values()), sum(b.values()), 'only-old', dict(a - b), 'only-new', dict(b - a))
blk = lambda L, s, e: L[next(i for i, l in enumerate(L) if l.startswith(s)):next(i for i, l in enumerate(L) if l.startswith(e))]
o7, n7 = blk(ol, '## 7.', '## 8.'), blk(nl, '## 8.', '## 9.')
d = [(i+1, x, y) for i, (x, y) in enumerate(zip(o7, n7)) if x != y]
print('4 sec7 lines old/new', len(o7), len(n7), '| differing lines', len(d))
for i, x, y in d: print('   L%d' % i, repr(x[:100]), '->', repr(y[:100]))
def wc(s):
    s = re.sub(r'\{\{FILL:[\s\S]*?\}\}', '', re.sub(r'<!--[\s\S]*?-->', '', s))
    return len(' '.join(l for l in s.split('\n') if not l.startswith('#')).split())
sec = lambda t, s, e: t[t.index(s):(t.index(e, t.index(s)+1) if e else len(t))]
old_pm = wc(sec(O, '\n## 3. Method', '\n## 4. ')) - wc(sec(O, '\n### 3.1 ', '\n### 3.2 ')) - wc(sec(O, '\n### 3.9 ', '\n### 3.10 '))
n4, nD = wc(sec(N, '\n## 4. ', '\n## 5. ')), wc(sec(N, '\n## Appendix D.', None))
print('5 old phase-method words', old_pm, '| new sec4', n4, '| App D', nD, '| sum', n4 + nD, '| delta', old_pm - n4 - nD)
```

Output on `f7b1b27fc`:

- `1 units old/new 303 323 | old units byte-identical in new 211 | multiplicity mismatches 0`
- `2 split pieces 17 | non-identical rows: HEADING 13, TEXT 3, CUT 1 | new body lines outside any map destination 0`.
  The three TEXT rows are P016, P074 and P075.
- `3 FILL 215 214 only-old {'CP-X02-headline': 1}`. FACT 25/25, BRANCH 70/70 and COMMENT 34/34 are identical.
- `4 sec7 lines old/new 110 110 | differing lines 14`
- `5 old phase-method words 3630 | new sec4 1870 | App D 1750 | sum 3620 | delta 10`

After F-1 to F-3, rerun it. Section 4 should show only the four heading lines differing, and the map should list
F-2's split. The delta check can be done by the research lead or the lead; it does not need another Opus seat.
