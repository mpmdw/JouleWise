# Round-7 bibliography orphan removal and renumbering plan

This plan is preparation only. Do not run its apply command while the round-6
draft is frozen. Ruling Addendum 9 item 62 keeps all entries until round 7 and
then requires one removal-and-renumbering pass, because a second pass could
cause citation drift.

An **orphan** is a reference entry present in Section 11 but never cited in the
rest of the paper. A **renumbering map** is the complete translation from each
kept old reference number to its new contiguous number. The **guard flag** is
the explicit `--i-am-round-7` acknowledgement required before the tool will
modify `docs/paper/draft-v1.md`.

## Verified frozen input

At preparation time, `docs/paper/draft-v1.md` had SHA-256
`939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`.
Its `## 11. References` section contained exactly 31 one-line entries numbered
contiguously from `1.` through `31.`. The scan domain was the entire document
outside that section, including Appendix A.

This grep enumerated numeric-bracket candidates outside the reference-list
lines:

```sh
rg --pcre2 -n '\[(?:[0-9]+)(?:\s*,\s*[0-9]+)*\](?!\()' docs/paper/draft-v1.md \
  | awk -F: '$1 < 360 || $1 > 392'
```

The raw grep also reports the mathematical interval `[0,1]` on line 221. The
tool rejects that candidate because `0` is outside the known old numbering
range 1–31. After applying the code-span, fenced-code, display-math, link, and
known-range rules, the cited set is exactly
`{1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 15, 19, 20, 22, 23, 26, 27, 28, 29, 30, 31}`.
Its complement in 1–31 is exactly the ten ruled orphans.

## Orphans to remove

Each row is absent from the in-text citation grep above. Author and title are
copied from the frozen Section 11 entry.

| Old | First author | Title | Reason |
|---:|---|---|---|
| 4 | D. Economou | Full-System Power Analysis and Modeling for Server Environments | No in-text citation. |
| 9 | P. Hübner | Apple vs. Oranges: Evaluating the Apple Silicon M-Series SoCs for HPC Performance and Efficiency | No in-text citation. |
| 11 | D. Pham | AgentStop: Terminating Local AI Agents Early to Save Energy in Consumer Devices | No in-text citation. |
| 14 | N. Kocher | Guidelines for the Quality Assessment of Energy-Aware NAS Benchmarks | No in-text citation. |
| 16 | M. Poess | Energy Benchmarks: A Detailed Analysis | No in-text citation. |
| 17 | W. Feng | The Green500 List: Encouraging Sustainable Supercomputing | No in-text citation. |
| 18 | S. Rivoire | A Comparison of High-Level Full-System Power Models | No in-text citation. |
| 21 | A. Javat | Silicon Showdown: Performance, Efficiency, and Ecosystem Barriers in Consumer-Grade LLM Inference | No in-text citation. |
| 24 | Q. Cao | Towards Accurate and Reliable Energy Measurement of NLP Models | No in-text citation. |
| 25 | D. Panigrahy | The Energy Blind Spot: NVIDIA's Flagship Edge AI Hardware Cannot Support Process-Level Energy Attribution | No in-text citation. |

## Complete old-to-new map

| Old | New | Old | New | Old | New |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 2 | 2 | 3 | 3 |
| 5 | 4 | 6 | 5 | 7 | 6 |
| 8 | 7 | 10 | 8 | 12 | 9 |
| 13 | 10 | 15 | 11 | 19 | 12 |
| 20 | 13 | 22 | 14 | 23 | 15 |
| 26 | 16 | 27 | 17 | 28 | 18 |
| 29 | 19 | 30 | 20 | 31 | 21 |

The output list therefore has `N = 21` entries. Original order is unchanged.

## Matcher regression anchors

Only a bracket matching `[(number)(, number)*]`, with every number in 1–31,
is a citation candidate. It must also be outside inline or fenced code, outside
a `\[` … `\]` display, and not immediately followed by `(`. The test fixture
pins every exclusion. These frozen-draft anchors explain why:

- `[PENDING]` occurs on line 256, and `[PENDING, PENDING]` on line 289.
- `[RESULT PENDING ISSUED ARTIFACTS]` occurs on line 189, while
  `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` occurs on line
  348.
- `[[NEEDS-VALUE: ...]]` occurs on line 272.
- Display-math delimiters occur on lines 119–121; image-link Markdown such as
  `![Figure 1...](figures/fig1_boundary_attribution.svg)` occurs on line 39.
- Code spans containing numbers occur on line 272, and the fenced `text` block
  is on lines 179–183. The test uses a synthetic numeric bracket inside each so
  future draft content of that form is protected.
- The current frozen draft contains symbolic bracketed code such as
  ``rail_power_w[ch]`` on line 434, but no literal `[TERM_A_...]` registry token.
  The test therefore supplies synthetic `[TERM_A_FIXTURE]` coverage for the
  named registry-token class.

The last point records a source fact rather than inventing a draft quotation:
`rg -n 'TERM_A' docs/paper/draft-v1.md` returned no match during preparation.

## Round-7 invocation

Run from the repository root only after the round-7 fill authority opens:

```sh
mkdir -p .tmp-r7
cp docs/paper/draft-v1.md .tmp-r7/draft-v1.before-bibliography-renumber.md
python3 scripts/paper_renumber_refs.py docs/paper/draft-v1.md
python3 scripts/paper_renumber_refs.py docs/paper/draft-v1.md --apply --i-am-round-7
```

The first tool command is the default dry run and must print the orphan set and
the table above. The second command removes those ten list lines, copies every
kept entry's text unchanged behind its new number, and rewrites each eligible
body bracket once. A repeated apply must exit 3 with `ALREADY RENUMBERED`.

## Post-apply fence

First run the paper build test in the round-7-authorized checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \
  -m pytest -p no:cacheprovider tests/test_paper_build.py -q
```

Then enumerate every positive-integer citation bracket with `rg`:

```sh
rg --pcre2 -n -o '\[(?:[1-9][0-9]*)(?:\s*,\s*[1-9][0-9]*)*\](?!\()' \
  docs/paper/draft-v1.md
rg --pcre2 -o '\[(?:[1-9][0-9]*)(?:\s*,\s*[1-9][0-9]*)*\](?!\()' \
  docs/paper/draft-v1.md | sort | uniq -c
```

Inspect the first output against the old-to-new table; every changed source
context must carry its new number. The second output must contain `[1]` through
`[21]` once each except `[4]` and `[5]`, which occur twice each. That exact
post-map multiset proves that no old-numbered citation occurrence survived.
This bound grep must return no matches (exit 1), proving that no candidate
contains a number greater than `N = 21`:

```sh
rg --pcre2 -n '\[(?:[1-9][0-9]*\s*,\s*)*(?:2[2-9]|[3-9][0-9]+)(?:\s*,\s*[1-9][0-9]*)*\](?!\()' \
  docs/paper/draft-v1.md
```

Finally, run the tool in dry-run mode again. It must report 21 references, no
orphans, and the identity map 1→1 through 21→21. This is the semantic
idempotence check.

## Kept-entry text cross-check

`docs/paper/bibliography-audit-2026-08-27.md` inventories the kept old keys as
the exact domain of the map above. Renumbering must not change their entry
text—only the numeric prefix. Compare the pre-apply copy with the result:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path('scripts').resolve()))
import paper_renumber_refs as module
before_text = Path('.tmp-r7/draft-v1.before-bibliography-renumber.md').read_text()
after_text = Path('docs/paper/draft-v1.md').read_text()
audit_text = Path('docs/paper/bibliography-audit-2026-08-27.md').read_text()
before = module.analyze_document(before_text)
after = module.analyze_document(after_text)
kept_payloads = [
    entry.text for entry in before.references if entry.number in before.renumbering
]
assert kept_payloads == [entry.text for entry in after.references]
audit_kept = {
    int(match.group(1))
    for match in re.finditer(
        r'^\| (\d+) \| \d+ \| \d+ \| yes \| yes \|$', audit_text, re.MULTILINE
    )
}
assert set(before.renumbering) == audit_kept
print('KEPT ENTRY TEXT: unchanged for all 21 audit keys')
PY
```

Delete `.tmp-r7/` after the round-7 operator has retained any required run
evidence elsewhere.

## Successor-skeleton close (2026-09-02)

The round-7 close was applied to `docs/paper/draft-v2-skeleton.md`, never to the
byte-frozen round-6 draft. The registered command above is specific to the
round-6 file and preserves reference-list order; it does not reorder an already
different successor by first citation. The successor was therefore renumbered
by hand in one bounded edit, and `scripts/paper_renumber_refs.py` was not run.

The final successor list has 24 cited entries and no orphans. Its first-citation
order is:

| New | Source | Former key or lineage source | First citation site |
|---:|---|---|---|
| 1 | Khan et al. | 5 | §8, counter gain |
| 2 | Jay et al. | 6 | §8, counter gain |
| 3 | Hähnel et al. | 29 | §8, counter time |
| 4 | Burtscher, Zecena, and Zong | RECOMMEND lineage | §8, counter time |
| 5 | Dauner et al. | 23 | §8, counter time |
| 6 | Ma et al. | 20 | §8, LLM energy measurement |
| 7 | Niu et al. | 7 | §8, LLM energy measurement |
| 8 | Ruf and Detyniecki | 19 | §8, LLM energy measurement |
| 9 | Chung et al. | 8 | §8, LLM energy measurement |
| 10 | Saad-Falcon et al. | 22 | §8, LLM energy measurement |
| 11 | Benazir and Lin | 13 | §8, LLM energy measurement |
| 12 | Rivoire et al. | 3 | §8, benchmark lineage |
| 13 | Lange | 15 | §8, benchmark lineage |
| 14 | Tschand et al. | 1 | §8, benchmark lineage |
| 15 | Standard Performance Evaluation Corporation | 2 | §8, benchmark lineage |
| 16 | Georges, Buytaert, and Eeckhout | 30 | §8, metrology lineage |
| 17 | Mytkowicz et al. | 31 | §8, metrology lineage |
| 18 | Zhuang, Li, and Fan | 26 | §8, prospective threshold discipline |
| 19 | Milanese and Vicino | RECOMMEND lineage | §8, bounded systematic uncertainty |
| 20 | Li et al. | 27 | §8, disaggregated inference |
| 21 | Basit et al. | 12 | §8, disaggregated inference |
| 22 | Li et al. | 10 | §8, disaggregated inference |
| 23 | Guo and Joshi | 28 | §8, disaggregated inference |
| 24 | Marzullo and Owicki | RECOMMEND lineage | Appendix A.3, clock-anchor feasible set |

The round-7 verification resolved the entries formerly numbered 13, 19, and
23 and all three added lineage sources against online records. Its HotCarbon
PDF locators replace the former locator-free entries. The other retained
entries keep the locators audited in `docs/paper/bibliography-audit-2026-08-27.md`;
they are not relabeled as online-verified by this close. The SPEC methodology
remains `n.d.` because the audited locator does not supply a verified year; no
year was invented.
