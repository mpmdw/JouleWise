# 18 — Closing-round DELTA re-audit (contract lens), fresh non-author Opus

Scope: `62d8c58b..7a7c5b56` (6 files, +338 −29), read-only in
`/Users/edr/code/JouleWise-wt-d165-relabel` @ `7a7c5b56`. Driver: report 16
(S1/S2/S3) and report 17 + magistrate addendum (F1 ruled, F2 deferred, F3 queued).

## VERDICT: CLEAN — 0 blockers, 0 should-fix, 3 nits

Both cured should-fixes close on their merits; S3 is registered, not silently
dropped; the ruling was applied exactly and nothing beyond it was widened.

---

## 1. CLOSURE

### S1 — module docstring: CLOSED, and the blind spot is closed with it

**Docstring is the ruled v2 semantics in plain words, and it matches the code.**
`joulewise/dominance_closeout.py:1-11` now says the replay "tries both signs of
an additive energy change shared across all A/B/B/A blocks and every combination
of independent local signs. It does not replay the same timing shift in every
block or prove that its limit covers the effect of such a shift." I checked this
against the implementation, not against the old docstring: `:970-987` is
literally `for shared_sign in (-1.0, 1.0): for local_mask in range(1 << len(blocks)):`
with `delta + shared_sign * shared + (±local)` per block — two shared signs ×
all 2^n local corners, over *energy* widths from `split_common_mode_block_width`.
No time coordinate is perturbed anywhere in the function. The withdrawn claim
("keeps one shared timing-error sign") is gone; the surviving sentences agree
with `replay_common_mode_dominance`'s own docstring (`:876-879`).

**Normalisation covers every RETIRED phrase.** `occurrences` now tokenises on
`[^\s-]+` (hyphens folded to spaces alongside whitespace, `.lower()` as before)
and folds each phrase the same way (`normalized_phrase`), so hyphen/space/case
variants of *all twelve* RETIRED phrases are matched — not the previous
`RETIRED[5:-1]` slice. `test_all_retired_variants_survive_wrapping_and_python_literals`
crosses every phrase with five separators (`" "`, `"-"`, `"\n"`, `"-\n"`, `" - "`)
in both Markdown and adjacent-Python-literal form.

**The counterfactual regression really fails on the old scanner — executed.** I
reconstructed the pre-diff scanner by reverting exactly the two changed lines
(`[^\s-]+`→`\S+`, `normalized_phrase`→`phrase`) in an in-memory copy of the test
module and ran the new test against it:
`FAILED (failures=1) … AssertionError: Lists differ: [] != [(1, 'shared timing error', False)]`.
The regression is genuinely defect-shaped, not a tautology.

**New hits were cured, not allowlisted — measured both sides.** I ran the new
scanner over the *parent* tree (`git ls-tree 62d8c58b`, contents via
`git cat-file`) beside a faithful old scanner:

```
BASE 62d8c58b : old-scanner 38 hits, new-scanner 39 hits
revealed only by folding: ('joulewise/dominance_closeout.py', 1, 'shared timing error', False)
HEAD 7a7c5b56 : old-scanner 40 hits, new-scanner 40 hits (identical sets)
```

Exactly one occurrence was hiding behind the hyphen — the module docstring — and
it was rewritten, not exempted. The allowlist diff is consistent with that:
38 → 40 entries = the two ruled registry entries (273, 289) plus pure re-anchors
(registry 262/277/293 → 264/281/297 from the prose reflow; `dominance_closeout.py`
167/176/182/874 → 169/178/184/876 from the +2-line docstring). No new phrase, no
new file, no path-wide entry, no weakened reason string.

### S2 — prefill rows: CLOSED, byte-identical

The four absolute R_cm cells (registry lines 273, 281, 289, 297) are now
byte-identical: `sha256` of each cell's text after `` `not_applicable` `` =
`095fceb37d7a299f…` for all four; pairwise string equality `273==281==289==297`
is `True`. Stronger than asked: each row's tail equals the production constant
`ABSOLUTE_COMMON_MODE_REASON` (`:183-188`) *exactly* (`row tail == constant: True`),
and the reflowed prose paragraph (`:262-266`) equals it modulo the sentence
period. One home, four faithful reproductions, no paraphrase drift.

---

## 2. CONSEQUENCES

**Census: 10/10 green.** `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m
unittest tests.test_d165_rationale_census -v` → `Ran 10 tests in 7.670s / OK`.
This retires report 17's own V1-red caveat: V1 failed only on registry 273/289
pending the two ruled entries, and those are now present.

**Over-match: bounded, and the named example is clean.** Probing the new scanner:
`"a common timestamp for all blocks"` → `[]` (the `(?!\w)` boundary stops it),
`"the common timeline of the run"` → `[]`, `"common-timescale drift"` → `[]`,
`"corner-widened attribution bound"` → `[]`, `"point-only repeatability floor"` → `[]`.
Three constructions do newly match: `"we use a common time base"` and
`"blocks share a common time reference"` (`common-time`), and
`"shared timing error-free windows"` (`shared timing error`). Two of those three
are the retired term of art written with a space, which is the point of the
change; only the `-free` compound is a true false positive. Repo-wide the cost is
zero today (old and new scanners return the identical 40-hit set at HEAD), and
the failure mode is a fail-closed test demanding a reasoned allowlist entry — a
reviewed refresh lane, not a soundness hazard. Nit N2 below.

**Docstring change alters no behaviour.** It is a module `__doc__` only; no
tracked code or test reads `dominance_closeout.__doc__`. `tests.test_d165_dominance_closeout`
→ `Ran 59 tests in 9.482s / OK`.

**TASK_QUEUE entry is substantively accurate.** Verified independently, not
copied: `validate_d165_paper_sources` (`:443-473`) calls
`validate_d165_replay_sidecar(sidecar)` with no era assertion, and
`_CLOSEOUT_TOP_KEYS` (`:257-270`) has no era/rule_id field — era-blind, as S3
says. `grep -c '^| \`\[R_cm_'` = 8 rows, all 8 carrying `RETIRED_FALLBACK` and
"no submission placement", so the "eight rows" mitigation is exact. The probe
result is attributed as *recorded* by the recheck, not re-asserted as fresh — correct
framing. One pointer defect: nit N1.

---

## 3. NITS

- **N1 — stale file:line in the new queue entry.** `TASK_QUEUE.md` cites
  `joulewise/dominance_closeout.py:464-465`. That anchor is correct at `62d8c58b`
  (and at `aaa5dc8e`, where report 16 measured it) but the same commit's +2-line
  docstring moved those statements to `:466-467`; at `7a7c5b56` lines 464-465 are
  the floor-artifact `except`/`codes.append`, a wrong-cause location. Only a nit
  because the entry names the function and the word "reviewed" points at the
  reviewed state — but the same commit re-anchored the allowlist and did not
  re-anchor this. Cure: `:466-467`, or drop the line numbers.
- **N2 — hyphen folding widens the match surface.** `X-free`/`X-based` compounds
  built on a retired phrase now hit (`"shared timing error-free"`). Cheap future
  cure if it ever bites: require the character after the phrase not to be `-`.
- **N3 — the withdrawn v1 sentence now lives unmarked in `tests/`.**
  `test_hyphenated_module_docstring_evaded_old_scanner` embeds the old docstring
  verbatim with no `LEGACY v1`/`SUPERSEDED` marker. Harmless today (`tests/` is
  outside `ROOTS` by design, and the test name is self-documenting), but it is the
  one unlabelled copy of the retired physical claim in the tree.

## Evidence appendix (all read-only, one target at a time)

```
git diff --stat 62d8c58b..7a7c5b56                      6 files, +338 −29
unittest tests.test_d165_rationale_census -v            Ran 10 / OK
unittest tests.test_d165_dominance_closeout             Ran 59 / OK
reverted-scanner counterfactual probe                   FAILED (failures=1), [] != [(1,'shared timing error',False)]
old-vs-new scanner over base 62d8c58b tree              38 vs 39; delta = dominance_closeout.py:1
old-vs-new scanner over HEAD tree                       40 vs 40; identical sets
registry cells 273/281/289/297 sha256 (post-marker)     095fceb37d7a299f… ×4, pairwise ==
row tail == ABSOLUTE_COMMON_MODE_REASON                 True
allowlist entries                                       38 → 40 (2 ruled + re-anchors only)
R_cm rows / RETIRED_FALLBACK / no submission placement   8 / 8 / 8
over-match probes (13 strings)                          "common timestamp" → []; 3 new matches, 1 genuine FP
```
