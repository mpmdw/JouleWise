# Opus counter-review — PR #272 @ 73f7fcc2

Seat: D-118 gate item 6, Opus counter-review on the near-final head.
Read-only. Worktree `/Users/edr/code/JouleWise-wt-dx` @ 73f7fcc2; main
`/Users/edr/code/JouleWise` @ 403998e1. All file:line citations below are at
73f7fcc2 unless the path says otherwise, and every claim marked *verified* was
executed this session (commands and tails in `## Executed evidence`).

This is not a re-run of the refuters' lenses. Where I reach the same place as a
prior seat (Q4) I say what is additive and what is agreement.

---

## 1. Custody chain — DX-013 traced end to end, and the link I would attack

**Row chosen: DX-013, "49 of 59"** (negative-offset count). Nine links:

| # | Link | Where | By check or by convention |
| --- | --- | --- | --- |
| 1 | Registry row declares site, marker, two field paths, render rule | `docs/paper/results-fill-registry.md:770` | check — `parse_registry_text` :183-296 |
| 2 | Row parse is fail-closed: 7 cells, exactly one `R7F_RENDER`, fixed fill rule, exact freeze label, no `[PENDING`, closed row set/order | :234-296 | check |
| 3 | Artifact pinned by path + sha256 + byte size | registry `:735`; `SOURCE_RE` :97-102 | check |
| 4 | Committed file matches the pin | `check_file_pins` :317-337 (`digest XD`, `size XD`) | check |
| 5 | Load with `parse_float=Decimal` — no `float` ever reaches a renderer | `load_json_artifacts` :339-352 | check |
| 6 | Field paths navigate; values typed | `resolve_field` :354-360; `render_row` :417-421 → `_exact_int` :414 → `_typed` :392-406 | check |
| 7 | Rendered string vs registry marker, type-strict | `check_rendered_rows` :524-540; `_comparison` :161-163 | check |
| 8 | Marker vs the literal in `draft-v2-skeleton.md` | `check_skeleton_literals` :653-700 | **check only where a `[FILL:DX-013]` marker exists** |
| 9 | Artifact bytes re-derived from the retained corpus by the pinned producer | `replay_half` :862-925; `F4_REPLAY_COMMAND` :80-84; `_byte_comparison` :312-315 | check |

Links 1–7 and 9 are genuinely by check. Three links are by convention:

**(a) Link 8 — the last one. The marker→prose binding does not exist yet.**
`check_skeleton_literals` iterates `FILL_RE.finditer(text)` (:658) and nothing
else; `check_placement` (:712-740) counts markers. A number that appears in the
skeleton without a marker is invisible in both directions. Verified: appending
`The onset median is +99.9 ms.` to a scratch copy of the skeleton leaves the
fence at `rc=0, R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0` (probe P-B). The
PR states this honestly at `docs/paper/round7/fill-checklist.md:30` and defers it
to `R7F-DX-PROSE-SCAN-01`.

**(b) Producer identity → reviewed commit.** `- XS = …, sha256 8733ff… (49b258d2, #240)`
and `- AS = …, sha256 e3e435… (b36d1e85, #272)` (registry `:736`, `:739`).
`parse_registry_text:222-223` requires only that the parenthesised metadata be
*non-empty*; the commit id and PR number are never parsed, never compared to
git. The sha binds the registry to the bytes on disk. Nothing binds those bytes
to a reviewed change.

**(c) Identity rows' declared supplier fields are resolve-only.** DX-003
(registry `:766`) declares the F4 digest "bound to parent DX-001 and
`XD#replay_command`". `check_supplier_fields:368-390` emits `"resolves"` and no
kind; identity rows are skipped by the renderer at :528-529. Verified in Q2.

**Which link would I attack: (a).** It is the cheapest by a wide margin — one
edit to one file the fence already reads, no pin to recompute, no producer to
touch, no marker to forge, and the fence returns 0. Every other route requires a
*self-consistent forged set* (artifact bytes + artifact pin + producer bytes +
producer pin + marker + literal), and link 9 only tolerates that set if the
producer itself is changed, which puts the whole attack inside a reviewable code
diff where a human is the detector. (b) is the second choice for exactly that
reason: it relocates the attack into the producer, whose only tie to a reviewed
change is unparsed prose.

Worth stating plainly since it bounds everything above: the registry, the
producers and the fence all live in the same mutable tree, so the chain's root
of trust is *review of a three-file diff*, not a cryptographic anchor. Under
D-161 (operator-only adversary is not the threat model) that is the right place
to stop — the threat is honest producer drift, and links 4/5/6/9 catch drift.
But the deferred (a) is not an operator-adversary hole; it is the ordinary-error
hole (an author types a number into prose), and it is the one that will actually
happen.

## 2. Typed-scalar refusal (ruling P3) — is the type model complete?

`_typed(value, kind, field)` at :392-406 offers `int | number | bool | str`.
For every scalar that is *rendered or gated* the model is complete and correct:
the resolver is the only path used by all 16 renderer call sites, `check_gates`
(:547), `check_figure`'s per-pulse read (:632), the control-count failure id
(:510) and the XD schema read (:356). Control probe confirms it bites:
`XD…median_ms` set to the string `"13.0"` (pin recomputed) → `rc=2`, three
MISMATCH rows, message `expected number, found str: '13.0'`.

Not in the model: **list, dict, null**. Composite leaves are validated by
hand-written `isinstance` at six sites (:463, :474, :485, :502, :592, :606) —
a consequence of the ruling rejecting Sol's declarative kind map, not an
oversight.

**Row kind that passes with no type check at all: the three identity rows'
declared supplier fields.** DX-003 declares `XD#replay_command`; it is resolved
at :380 and never typed, never rendered, never compared to anything (not even to
`F4_REPLAY_COMMAND` at :80, which is checked against the *registry prose* at
:246-250, not against the artifact's own recorded command).
**Verified (M1):** `XD.replay_command = 12345`, XD pin and size recomputed →
`rc=0, R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`.

Second, weaker instance: **refusal-bucket list elements.** :474-476 checks
`isinstance(refusal_ids, list)` and its length against `v3_refused_count`; the
elements themselves are never typed.
**Verified (M2):** `AQ…v3_refusals_by_token.anchor_unresolved[0] = 999` →
`rc=0, 181/0`. Materially benign — DX-021's rendered claim "all
anchor_unresolved" rests on the key-set check at :459-462, which is sound — but
it is the one place a rendered claim rests on a container the resolver never
sees.

Related registry-completeness gap: `derived_refused_counts` **discards** DX-021's
third declared field ref (`derived, refused, _ = values`, :456) and then reads
`AQ#summary.population_size` from code (:466) — a path DX-021's row (registry
`:776`) does not declare. So the docstring's claim at :3-5 that the registry is
"the single source of digest, field-path, rendering, and row-value truth" is not
literally true for that row, in both directions.

## 3. `--literals-only` — what it skips, and is the skipped set visible?

**Exactly `replay_half` and nothing else** (:990-991). Concretely the skipped
set is:

1. the three byte-identity comparisons `replay XD bytes` / `replay F4 bytes` /
   `replay AQ bytes` (measured: 181 vs 184 comparisons);
2. the corpus-presence precondition `_required_corpus_paths` (:838-861) and
   therefore the **entire exit-3 path** — a literals-only green carries no
   information about whether the retained corpus exists;
3. both producer executions, and with them any producer-side failure
   (`_producer_failure` :824-827) and the pinned-argv validation
   `_f4_replay_argv` :843-861.

The digest half is byte-identical between the two modes.

**Documented adequately — this one is by check, not convention.** Three
surfaces a future operator plausibly reads: the module docstring :12-21, which
argparse prints as the `--help` description (:955); the flag's own help string
:972-974; and `docs/paper/round7/fill-checklist.md:26-28`, which says in words
that the literals-only tail "is not sufficient before a fill batch". Crucially
the tail *token itself* differs (`R7F LITERALS-ONLY COMPARED` vs `R7F COMPARED`,
:984 and :998), so a literals-only green cannot be pasted into a trace as a full
green — that is a mechanism, not a note. I have no finding here.

One caveat that belongs to Finding F1, not here: the checklist expresses the
sufficient tails as the literal constants `184` and `181`, and those constants
stop being true the moment the fill batch the checklist governs lands.

## 4. Should the fence resolve the corpus root before printing it?

The line serves two consumers with opposed needs. As a **gate token** (night
launcher) only the prefix and the exit code matter; either spelling works. As a
**diagnostic** the two consumers ask different questions: "did my flag arrive?"
(answered by the path as given) and "where did it actually look?" (answered by
the resolved path). The current line answers only the second.

**I come down on: resolving is the right contract** — and for a reason beyond
luna 232's. The fence is asserting a *filesystem attempt*; the only path it can
honestly claim to have stat-ed is the resolved one. The stronger argument is
about the log's second reader: a night-launcher log is read hours later, often
from a different cwd and possibly a different shell, and `--corpus-root .` or
`~/code/JouleWise` echoed verbatim is a string nobody can re-stat. Resolution is
what makes the line *actionable* rather than merely faithful to the invocation.
The cost — losing the operator's spelling when a symlink is in play — is the
smaller loss, and the invocation is recoverable from the launcher's own command
record, whereas the resolved path is recoverable from nothing else.

So I would not change the behaviour. I would change the contract in two places,
because as written it does not say what the code does:

1. **"Resolved" appears only in the test's comment.** `tests/…:806-808`
   (commit c8ea9e95) says it. The fence's own contract does not: :14-15 says
   "names the missing path", :20 says `R7F CORPUS UNAVAILABLE: <path>`. The next
   consumer is the night-launcher gate, which does not exist yet and will be
   written against the docstring (it is what `--help` prints). It will compare an
   as-given path and take the identical macOS `/var → /private/var` bite at a new
   call site. That is the same defect class recurring — the standing escalation
   trigger's signature — and the cure is one clause at :20. c8ea9e95 cured the
   symptom in the assertion rather than the contract that produced it.

2. **The line has a second, untested grammar.** :888 and :915 raise
   `ArtifactsUnavailable((stdout + stderr).strip() or str(corpus_root))` when a
   producer exits 3, so the payload becomes a *message*, not a path:
   `artifacts unavailable: /…/instrument_evidence.json is not present`
   (`scripts/paper_excursion_decomposition.py:800-802`) or
   `population unavailable: …` (`scripts/paper_anchor_correction_quantified.py:717-719`,
   added by this PR). A consumer doing
   `line.removeprefix("R7F CORPUS UNAVAILABLE: ")` and stat-ing the result gets
   garbage. It is single-line *today* only because both producers happen to print
   exactly one line — nothing enforces it, and `_producer_failure:824-827` shows
   the author already knew to flatten producer output with `" | "` on the
   sibling code path. `test_absent_corpus_exits_three_and_names_path`
   (`tests/…:804-838`) covers only the first branch;
   `test_as_population_unavailable_exits_three` (`tests/…:423-439`) asserts AS's
   own stderr and never the R7F line.

## 5. Does this PR pre-empt or constrain `R7F-DX-PROSE-SCAN-01`?

**Nothing blocks it.** The PR touches neither `docs/paper/draft-v2-skeleton.md`
nor `scripts/render_results_fills.py` (`git diff --stat main...HEAD`), and D-168's
frozen 109-key renderer is unaffected — verified by running its suite at HEAD
with the 19 new registry rows present: `tests.test_render_results_fills`, 27
tests, OK. Three real constraints the row's brief must inherit:

1. **The region anchor is already fixed and shared — and this is helpful.**
   `DX_STANDING_SENTENCE_HEAD` (:108) is pinned to registry `:747` and
   test-bound at `tests/…:260-261`. The census opens the region on it (:722); the
   ruled prose scan's region ("standing sentence to the next `^#`") must key on
   the *same* constant or the two mechanisms can disagree about whether a region
   exists at all. Reusing it is free; re-deriving it is a second source of truth.

2. **The marker-adjacency grammar is now fixed by `check_skeleton_literals`
   (:653-700), and the prose scan must be its exact complement.** A placed
   literal is legal in exactly two spellings: backticked immediately after the
   marker (:673-676), or bare and followed by a character that is neither
   alphanumeric nor `.`/`%` (:677-694). "Not immediately preceded by its own
   marker" has to negate *that* predicate. If the scan invents its own notion of
   adjacency, a literal can be simultaneously legal to one mechanism and illegal
   to the other — a contradiction that would surface as an unfixable MISMATCH.

3. **Count coupling.** Any always-on comparison the scan adds moves the pinned
   tail numbers again — numbers that are *already* scheduled to move (F1). The
   prose-scan row should land after, or together with, the F1 cure; otherwise it
   is the second change in a row to re-pin the same constants.

No pre-emption: the scan's decision space (region bounds, per-row literal set,
MISMATCH message shape) is untouched, and `render_row` already gives it the 16
rendered literals it needs.

## Findings

### SHOULD-FIX 1 — the pinned tail counts are placement-dependent, so a *correct* DX fill batch turns four assertions red and makes the checklist's stated gate false

`docs/paper/round7/fill-checklist.md:24-28` states R7F's "exact successful
full-replay tail" as the constant `R7F COMPARED 184 / MISMATCHES 0`, in the same
bullet-list idiom as the RF bullet immediately above it (`:22-23`, "require the
exact successful tail … before and after every batch"). But R7F's comparison
count is a *function of how many DX literals are placed*: `check_skeleton_literals`
(:658) emits one comparison per `[FILL:DX-nnn]` marker found, and `digest_half`
counts them all (:757-763). RF's 43 is stable because RF's census does not grow
with placements; R7F imported RF's exact-tail idiom onto a count that does.

Verified counterfactual (probe P-C / probe3): place the mandatory standing
sentence plus all 16 non-identity markers each followed by its exact registry
marker — i.e. execute the fill batch this registry authorizes, correctly —
and the fence reports `rc=0, R7F PLACED 16/16, R7F LITERALS-ONLY COMPARED 197 /
MISMATCHES 0`. Full replay would read `R7F COMPARED 200 / MISMATCHES 0`.

Consequences, all four verified by reading the assertions:
- `tests/test_paper_round7_artifacts.py:797-801` — `assertEqual(lines[-1],
  "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0")` against the **real**
  skeleton (only `--registry` is overridden) → red.
- `tests/…:850` — `assertEqual(len(digest_comparisons), 181)` → red.
- `tests/…:861` — `assertEqual(len(digest_comparisons) + len(comparisons), 184)` → red.
- `tests/…:263-269` `test_current_skeleton_passes_zero_placement_census` —
  `assertEqual(len(comparisons), 1)` and `_placed_row_count == 0` → red.
- `fill-checklist.md:25` and `:27` state tails that no longer exist, so the
  operator following the checklist after the batch either blocks a correct fill
  or learns to ignore the tail number — and "ignore the tail number" is how an
  exact-tail gate dies.

Fail-loud, not fail-silent, and the cure is small — which is why this is not a
blocker. But it schedules a CI break on the very next correct action in this
lane, and it is precisely the "decided ≠ done / ruled-not-installed" shape: a
gate stated as a constant that the governed work invalidates. Cure shape (not
prescriptive): make the tests derive the expected count (`181 + placed literal
comparisons`, or assert on `MISMATCHES 0` plus the `R7F PLACED n/16` line), and
have the checklist state the count as placement-dependent rather than as a
literal.

### SHOULD-FIX 2 — the `R7F CORPUS UNAVAILABLE:` contract is under-specified in the one place its future consumer will read, and its second grammar is untested

Detail and argument in §4. Two concrete defects:

(a) The fence's own contract (:14-15, :20) says "names the missing path" /
`<path>` and never says *resolved*; only the test comment (`tests/…:806-808`)
does. Counterfactual: the night-launcher gate is written from `--help` (which
prints the docstring, :955), asserts the as-given `--corpus-root`, and fails
intermittently on macOS the moment the operator's path crosses `/var` or any
other symlink — the identical c8ea9e95 defect at a new call site. Cure: one
clause at :20.

(b) The producer-exit-3 branches (:888, :915) put a producer *message* after the
`R7F CORPUS UNAVAILABLE: ` prefix, not a path, and no test asserts the resulting
R7F line at all. Counterfactual: a consumer that strips the prefix and stats the
remainder receives `artifacts unavailable: /…/instrument_evidence.json is not
present`. Single-line today only by the producers' good manners
(`paper_excursion_decomposition.py:800-802`,
`paper_anchor_correction_quantified.py:717-719`); if either ever emits a warning
line first, `R7F CORPUS UNAVAILABLE:` stops being the last line and the exact
last-line contract at `tests/…:831-837` silently stops describing reality.
`_producer_failure:824-827` already shows the flattening idiom for exactly this.

### NIT 1 — identity rows' declared supplier fields get no type check

DX-003 (registry `:766`) declares `XD#replay_command` as a binding token;
`check_supplier_fields:368-390` asserts navigability only, and identity rows
skip the renderer (:528-529). **Verified (M1):** setting `XD.replay_command` to
the integer `12345` and recomputing the XD pin yields `rc=0, 181/0`. The
registry's "bound to … `XD#replay_command`" is decorative. Low materiality (a
provenance string, not a paper number) and arguably inside the D-161 prune —
recorded so the registry's wording and the fence's behaviour can be made to
agree in either direction.

### NIT 2 — refusal-bucket list elements are counted but never typed; DX-021 reads an undeclared field path

**Verified (M2):** `AQ…v3_refusals_by_token.anchor_unresolved[0] = 999` with the
AQ pin recomputed → `rc=0, 181/0` (:474-476 checks list-ness and length only).
Benign — the "all anchor_unresolved" claim is carried by the key-set check at
:459-462. Separately, :456 discards DX-021's third declared field ref and :466
reads `AQ#summary.population_size`, which the row does not declare
(registry `:776`).

### NIT 3 — `CORPUS_ROOT` is a hardcoded machine path with no env escape, and the module is not in the timing map

`tests/test_paper_round7_artifacts.py:39` `CORPUS_ROOT = Path("/Users/edr/code/JouleWise")`.
The module's docstring (`tests/…:9`) says the replay test is "corpus-gated, like
the Section 2 fence test", but the gating differs materially: the Section 2
precedent uses a repo-relative root (`tests/test_paper_replay_fence.py:36-39`,
`ROOT / FENCE.SOURCE_DIRECTORY`) and therefore *skips* inside a linked worktree,
whereas R7F's absolute path resolves everywhere on Ed's machine and *fires*.
Pointing at the canonical checkout is the only way the replay can run from a
worktree at all, so the behaviour is right; the cost is that every full local
suite run in every worktree now pays the replay. Measured this session: 476 s
CPU / 7 m 57 s wall for the equivalent CLI. The module is absent from
`scripts/test_timings.json` (verified), so `shard_tests` assigns it the unknown
weight. CI is unaffected (the path does not exist on the runner, so it skips).
Counterfactual: `python3 -m unittest tests.test_paper_round7_artifacts` on Ed's
machine costs ~8 minutes with no opt-out, while `REGISTRY_PATH` two lines above
(`tests/…:36-38`) already honours an `R7F_REGISTRY` env override — the
convention exists in the same file and was not extended to the corpus root.

### NIT 4 — docstring overclaims the registry as the single field-path source

:3-5 ("the single source of digest, field-path, rendering, and row-value
truth"). False in both directions for DX-021: a declared ref discarded (:456)
and an undeclared path read (:466). One-clause fix.

---

**What I would not merge as-is:** nothing. Both SHOULD-FIX items are
documentation/assertion shape, not soundness; the full replay is green at
184/0 and the ruled A1/A2/P3 mechanisms are installed and biting (control probe
and M1/M2 above). F1 should be cured before the DX fill batch is executed, not
before merge — but it should be recorded now, because the batch is the next step
in this lane and the failure will present as "the fence broke" rather than
"the pinned constant was placement-dependent".

## Executed evidence

All runs with `TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp-opus-dx`,
cwd `/Users/edr/code/JouleWise-wt-dx` @ 73f7fcc2. No writes to any checkout;
all mutation probes ran against throwaway copies under TMPDIR.

```text
$ git -C /Users/edr/code/JouleWise-wt-dx diff --stat main...HEAD
24 files changed, 4164 insertions(+), 7 deletions(-)
  (scripts/check_paper_round7_artifacts.py 1004+, tests/test_paper_round7_artifacts.py 865+,
   docs/paper/results-fill-registry.md 60+, docs/paper/round7/fill-checklist.md 32 changed,
   scripts/paper_anchor_correction_quantified.py 10 changed, 19 trace files)
exit 0

$ python3 scripts/check_paper_round7_artifacts.py --literals-only
...
R7F PLACED 0/16
R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
exit 0                       # 183 output lines, 0 MISMATCH lines

$ python3 scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise
ok   replay AQ bytes
R7F PLACED 0/16
R7F COMPARED 184 / MISMATCHES 0
exit 0                       # 476.10s user, 7:57.34 wall

$ python3 -m unittest -q tests.test_paper_round7_artifacts.RegistryAndDigestTests \
    tests.test_paper_round7_artifacts.RefusalTests \
    tests.test_paper_round7_artifacts.TypedArtifactCliTests \
    tests.test_paper_round7_artifacts.InvocationTests
Ran 43 tests in 0.795s
OK
exit 0                       # ReplayAgainstRetainedCorporaTests excluded (the 8-minute class)

$ python3 -m unittest -q tests.test_render_results_fills     # D-168 frozen 109-key renderer
Ran 27 tests in 0.439s
OK
exit 0

$ python3 $TMPDIR/probe.py                  # scratch repo-root copies; artifact mutated + pin/size recomputed
--- BASELINE (unmutated copy): rc=0 tail=R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
--- CONTROL: XD median_ms -> str '13.0': rc=2 tail=R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 3
    MISMATCH row DX-010: expected '+13.0 ms', observed "REFUSED: ValueError: XD#summary.onset_best_fit_lag.median_ms: expected number, found str: '13.0'"
    MISMATCH row DX-016: ... same refusal
    MISMATCH row DX-017: ... same refusal
--- M1: XD replay_command -> int 12345: rc=0 tail=R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
--- M2: AQ anchor_unresolved[0] -> int 999: rc=0 tail=R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
exit 0

$ python3 $TMPDIR/probe2.py                 # scratch skeleton copies; prose appended, no registry change
--- P-A: correct literal, NO marker, no standing sentence: rc=0
    tail: R7F PLACED 0/16 | R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
--- P-B: WRONG literal +99.9 ms, NO marker, no standing sentence: rc=0
    tail: R7F PLACED 0/16 | R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
--- P-C: standing sentence + 16 bare markers + one WRONG unmarked literal: rc=2
    tail: R7F PLACED 16/16 | R7F LITERALS-ONLY COMPARED 197 / MISMATCHES 16
    MISMATCH literal DX-010: expected '+13.0 ms', observed ''
exit 0

$ python3 $TMPDIR/probe3.py                 # standing sentence + all 16 markers with their EXACT registry markers
rc= 0
R7F PLACED 16/16
R7F LITERALS-ONLY COMPARED 197 / MISMATCHES 0
exit 0                       # <- F1: the correct post-fill tail is 197 (full replay 200), not 181/184

$ python3 -c "import json; d=json.load(open('scripts/test_timings.json')); \
    print('round7 in map:', 'tests.test_paper_round7_artifacts' in d['seconds_by_module'])"
round7 in map: False
exit 0

$ git -C /Users/edr/code/JouleWise-wt-dx diff main...HEAD --stat -- scripts/test_timings.json
(empty)
exit 0
```

Line-number citations verified by direct read of
`scripts/check_paper_round7_artifacts.py` (full file),
`tests/test_paper_round7_artifacts.py` (:1-150, :151-275, :394-470, :776-865),
`docs/paper/results-fill-registry.md:724-782`,
`docs/paper/round7/fill-checklist.md:18-32` and the branch diff of that file,
`scripts/paper_excursion_decomposition.py:770-836`, the AS diff, and
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
(full, including the 07:25 addendum).

VERDICT: SHOULD-FIX 2
