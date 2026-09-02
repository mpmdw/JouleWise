# SEALED — cold-gate contract-lens refuter (Opus 5), R7F `CORPUS UNAVAILABLE`, 2026-09-02

Packet: `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/00-PACKET.md`
(committed `4c88b941`); code under review read as committed bytes at
`74fb5206` via `git show 74fb5206:<path>`.

## Disclosure

**Charter digest.** Expected (supplied to me independently of the packet, in my
launching brief): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.
Observed, by `shasum -a 256 /Users/edr/code/JouleWise-wt-dx/docs/process/coldgate_charter.md`:
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. **MATCH.**
Computed before reading the packet or any merits material. The packet's F7
asserts the same value; I did not rely on the packet for the expected value.

**Everything I read** (nothing else):

1. `docs/process/coldgate_charter.md` (whole).
2. `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/00-PACKET.md` (whole).
3. All ten excerpt files in that packet directory (whole; each is short).
4. `docs/process_traces/2026-09-02-dx-registry/19-opus-counter-review.md`
   lines 140–200 and 260–300 (the §4 discussion and SHOULD-FIX 2; the NIT 1 /
   NIT 2 headings fell inside the 260–300 window and were read incidentally —
   they concern registry typing, not this question, and I do not rely on them).
5. `docs/process_traces/2026-09-02-dx-registry/20-terra-239-delta-3.md`
   lines 18–35 and 115–130 (SF2-CONTRACT finding and its narrative).
6. `docs/process_traces/2026-09-02-dx-registry/21-sol-240-fresh-pass.md`
   lines 15–40 and 95–120 (SF1-DOC-FALLBACK finding and its narrative).
7. Primary code at `74fb5206`: `scripts/check_paper_round7_artifacts.py`
   lines 1–40 and 735–1024; `tests/test_paper_round7_artifacts.py`
   lines 395–435, 803–870, plus a `grep -n` class/method index and a
   `grep -n "CORPUS UNAVAILABLE"` index of the whole file.
8. The two producer exit-3 sites and their raise sites at `74fb5206`:
   `scripts/paper_excursion_decomposition.py` lines 128–175 and 780–810;
   `scripts/paper_anchor_correction_quantified.py` lines 700–730; plus
   `grep -n` for the two unavailability exception classes in each.
9. `docs/decision_log.md` line 188 (the D-161 index row, reached by
   `grep -rn "D-161" docs/decision_log.md`) and lines 10332–10400 (the D-161
   section, plus D-162…D-166 headings caught in the same window; I do not rely
   on D-162–D-166).
10. Two targeted greps whose *hits* I read as single lines, for the
    Q1-consumer census only: `docs/paper/round7/fill-checklist.md:24-36` and
    `docs/paper/results-fill-registry.md:729,740,743,764-772` matched by
    `grep -rn "exit 3\|exits 3\|R7F"`. These are paper-fill documents, not
    process/state narrative; I read only the matched lines, and only to test
    whether a non-test consumer of the fence's tail exists.

**Contamination: none of the prohibited set.** I did not read README.md,
RUN\_STATE.md, TASK\_QUEUE.md, docs/orchestration.md, docs/agent\_playbook.md,
MAGISTRATE-NOTES.md, any `*-disposition-*.md`, any CLAUDE\*.md, or any memory
file. I hold no prior context on this project, this PR, or these reviewers.
One unavoidable disclosure: my harness preamble carries standing user/project
instruction text of the kind the charter excludes. I did not consult it for
any proposition in this ruling; every conclusion below rests on bytes I read
at `74fb5206` or on the packet and its named exhibits. If the gate regards
that preamble as disqualifying contamination, that is a fact about my seat,
not about the merits.

**Execution.** Read-only throughout. I wrote nothing under
`/Users/edr/code/JouleWise-wt-dx` (`git status --short` was empty before and
the only git commands I ran were `rev-parse`, `show`, `status --short`, and
`grep`). I ran exactly the two test classes the packet names, once, with
`TMPDIR` pointed at a directory I created under my own scratchpad. I did **not**
run `unittest discover`, did **not** run the retained-corpus replay class, did
**not** launch any codex/claude process, and did **not** execute `--help` or any
other fence invocation (my brief licensed only the two classes); statements
below about `--help` are static reasoning over `argparse` semantics and are
labelled as such.

**Packet hygiene (charter §6).** Three defects, none disqualifying:

- **H1 (NIT).** The Question says the last line's consumers are "the two tests
  at `tests/test_paper_round7_artifacts.py:619` and `:859`". The packet's own
  F3 census lists a third test consumer, `:424`, which asserts the token is
  *absent* on the producer-exit-1 path. No effect on the merits — every
  candidate preserves it — but the Q1-consumer question is asked in narrower
  terms than the packet's own facts support.
- **H2 (NIT).** Option (a) is stated in wording that is itself false on a
  reachable input (see *Refutation of (a)*, R-A1): "the resolved path of the
  first required corpus **file**". Option (b) is stated with two concrete,
  self-consistent variants. The asymmetry is curable inside the question,
  which expressly asks me to "state the operative sentence(s)", so I cure it
  rather than refuse.
- **H3 (MATERIAL).** The packet scopes Q1 to the `<detail>` grammar and does
  not surface that the *same docstring paragraph* contains a second sentence
  ("Exit codes: … 2 for any mismatch, 3 for an absent corpus", `:21`) that is
  false on two reachable inputs, of exactly the defect class that has now
  failed three rounds. Since Q1 expressly asks "where could a fourth patch
  STILL be wrong", this omission bears directly on the answer. I supply it
  below (R-A3, R-A4); it is the single most consequential thing in this
  ruling.

## Refutation of (a)

Option (a) — document the code as it is, three enumerated detail shapes — is
the only candidate that survives, but **not in the packet's wording**. Four
refutations; the first two bite (a)'s own sentences, the second two bite the
sentences (a) would leave standing beside them.

**R-A1 (BLOCKER against the wording; concrete falsifying input).**
(a)(i) says the detail is "the resolved path of the first required corpus
**file** the preflight finds absent". The preflight's required list is built at
`scripts/check_paper_round7_artifacts.py:781-795`, and its **third element is a
directory**, not a file:

```
794	        corpus_root / "runs" / "instrument_validation",
```

Falsifying input: a corpus root that holds
`runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json`
and `…/raw/powermetrics.plist` but no `runs/instrument_validation` directory —
i.e. the XS capture copied over and the AS population tree not. That is an
ordinary partial corpus, not an adversarial construction. `replay_half:881-883`
then raises `ArtifactsUnavailable(str(path))` for the directory, and the last
line is `R7F CORPUS UNAVAILABLE: <root>/runs/instrument_validation`. (a)(i)'s
operative sentence is false on that input. **Cure: say "path" or "corpus
entry", and name the directory case explicitly so the reader is not surprised.**

**R-A2 (MATERIAL; concrete falsifying input).** The docstring sentence added by
round 1's cure and retained at `74fb5206:28-30` — "The path is printed after
``Path.resolve()``" — is false as stated for the preflight branch. Only the
*corpus root* passes through `Path.resolve()` (`main:998`,
`(args.corpus_root or repository_root).resolve()`); the remainder is literal
`/` joins (`:781-795`, `:815-821`), never resolved. Falsifying input:
`--corpus-root /R` where `/R` is already canonical but `/R/runs_window_a_20260722`
is a symlink to `/E/w`, and `/E/w/instrument_validation/20260722T145535-e941c821/instrument_evidence.json`
is absent. The printed detail is `/R/runs_window_a_20260722/…/instrument_evidence.json`;
a consumer that resolves both sides and compares gets a mismatch, which is the
*same* `/var → /private/var` class of bite that the round-1 cure was written to
prevent, merely displaced one directory level down. **Cure: "the root is
resolved, the joined remainder is not."** (Under D-161 the deliberately planted
symlink is out of the threat model, but an incidentally symlinked capture
directory is not deliberate; I hold this at MATERIAL, not BLOCKER.)

**R-A3 (MATERIAL; the fourth-round predictor).** `:21` promises "2 for any
mismatch". Falsifying input: a corpus in which XS's replay of XD or F4 drifts
by one byte **and** AS's population root holds no capture directories
(`paper_anchor_correction_quantified.py:653` → `PopulationUnavailable` →
`:721-723` → exit 3). Trace it: `replay_half` appends the XD and F4 byte
comparisons to its **local** list at `:910-916`, then AS exits 3 and `:931-935`
raises. The raise propagates out of `replay_half`, so `main:1010`'s
`comparisons.extend(replay_half(...))` never executes and the XD/F4
comparisons — including the mismatching one — are discarded. `main:1011-1014`
prints only the digest-half comparisons (all matching, else `:1002-1006` would
already have returned 2), then the UNAVAILABLE line, and returns 3. A mismatch
exists; the exit code is 3; no `MISMATCH` line is printed. **"2 for any
mismatch" is false, and the drift is invisible in the log.** This is honest
producer drift — the exact thing D-161 names as staying fail-closed — so it is
not pruned by the threat model. It is not a *soundness* hole (3 is never a
pass), which is why I tier it MATERIAL and not BLOCKER; it is a
diagnostic-destruction hole, and it lives one sentence away from the sentence
three reviewers have already failed.

**R-A4 (MATERIAL).** `:21` also promises "3 for an absent corpus". Falsifying
input: a corpus root where every required file is **present** but
`events.jsonl` does not match its retained sha256. `paper_excursion_decomposition.py:169-170`
raises `ArtifactsUnavailable("events.jsonl does not match its retained sha256")`,
`:800-802` prints it to stderr and returns 3, and the fence's `:903-905` turns
that into `R7F CORPUS UNAVAILABLE: events.jsonl does not match its retained
sha256` — a detail containing **no path at all**, for a corpus that is entirely
present. The same holds for `:135-138` (no candidate `raw/powermetrics.plist`
matches the expected sha256; the detail there embeds a Python list repr). A
re-issued corpus artifact is precisely D-161's in-scope threat, and it is
reported to the reader under the word "UNAVAILABLE". **Cure: say that exit 3
means "the replay could not be completed", not "a file was absent".**

**What does NOT refute (a).** I tried and failed on these, and record them so
the record shows the search was symmetric:

- *Is the three-shape enumeration exhaustive?* Yes, and this is the fact that
  makes (a) closable where rounds 1–3 were not.
  `grep -n "ArtifactsUnavailable" ` over the committed fence returns exactly
  three raise sites — `:883`, `:904`, `:933` — one class definition (`:127`),
  and one catch (`:1011`). `digest_half` is called at `:1001`, *outside* the
  `try`, so nothing else can reach the handler; and the producers run as
  subprocesses (`_run_producer:825-832`), so their own `ArtifactsUnavailable` /
  `PopulationUnavailable` classes cannot propagate in-process. Rounds 1–3 each
  described a subset derived from the previous reviewer's counterexample;
  (a) is the first cure derived from the closed site census.
- *Can the flattened detail (ii) break the "last line" contract?*
  No. `(stdout + stderr).strip().splitlines()` (`:844`) splits on every
  line-break character Python recognises (`\n`, `\r`, `\r\n`, `\v`, `\f`,
  `\x1c`-`\x1e`, `\x85`, and the two Unicode separators U+2028 and U+2029),
  and `" | ".join` reintroduces none, so form (ii) is single-line by
  construction.
- *Can the preflight detail (i) break it?* Only via a path containing a
  newline. For the three fixed entries that needs an operator to create such a
  directory name; for the AQ-derived entries (`:803-821`) it needs a
  `validation_id` carrying a newline inside the AQ artifact — and AQ's sha256
  is digest-pinned, so `digest_half` returns 2 at `:1002-1006` before
  `replay_half` ever runs. D-161 prunes the first; the digest gate closes the
  second. **NIT, no cure required.**
- *Is (ii)'s "stdout+stderr" wording right?* Yes, and deliberately so: the code
  concatenates *then* splits, so a producer whose stdout lacks a trailing
  newline yields one element gluing its last stdout line to its first stderr
  line. Writing "stdout and stderr concatenated, stripped, split into lines"
  keeps that true; writing "stdout lines then stderr lines" would not.
- *Is F4 right that shape (iii) is unreachable today?* Yes.
  `paper_excursion_decomposition.py:801` and
  `paper_anchor_correction_quantified.py:722` each print exactly one stderr
  line before `return 3`, so `_producer_unavailable_message` cannot see empty
  output from either. It stays reachable through any future producer and
  through the mocked path, so it must still be documented.

## Refutation of (b)

Both variants the packet offers are refuted; (b) is REJECTED.

**(b) variant 1** — the helper always returns
`f"{corpus_root}: {flattened output or 'no output'}"`, giving "two branches:
preflight path, or corpus root + producer text".

- **It does not reduce the branch count, so it does not cure the defect.** The
  preflight raise at `:883` is `ArtifactsUnavailable(str(path))` and is not
  touched by any change to `_producer_unavailable_message`. `<detail>` still
  has two incompatible shapes, and the operative docstring sentence still needs
  a disjunction. The three failed rounds failed at *disjunction fidelity*, not
  at branch count.
- **Falsifying input for its operative sentence** ("the detail is always
  `<corpus root>: <flattened producer output or `no output`>`"): any corpus
  root that exists but is missing
  `runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json`.
  The preflight raises before either producer is launched, and the detail is a
  bare path with no `": "` and no producer text. False.
- **It makes machine-consumability strictly worse.** Today a consumer can stat
  the detail on the preflight branch. After variant 1, forms (ii) and (iii)
  both become `"<root>: …"` — never stat-able — while form (i) stays a bare
  path, so a consumer must still discriminate, and now cannot do it by
  "does this stat?" either.

**(b) variant 2** — the detail is ALWAYS the resolved corpus root; producer text
moves to its own preceding stdout line.

- **It destroys the line's most valuable diagnostic, on the most common input.**
  Falsifying counterfactual for its own promise of usefulness: `--corpus-root
  /R` where `/R` exists but `/R/runs_window_a_20260722/…/instrument_evidence.json`
  is absent. The line becomes `R7F CORPUS UNAVAILABLE: /R` — a path that
  **exists**. The night-log reader stats `/R`, finds it, and concludes the
  fence is lying to them. Today that same input names the exact missing file,
  and `tests/test_paper_round7_artifacts.py:857-860` pins precisely that
  behaviour with an exact-equality assertion on
  `…/20260722T145535-e941c821/instrument_evidence.json`.
- **Which assertions change.** `:857-860` must be rewritten from the missing
  file path to the corpus root, deleting the only regression that proves the
  fence tells you *which* entry is missing; `:856` (`assertIn(str(missing_root),
  completed.stdout)`) survives vacuously. `:619-622` must change: `:622`'s
  `assertIn("producer line one | producer line two", lines[-1])` becomes false —
  the flattened text is no longer on the last line — so the test must be split
  into a last-line assertion plus a preceding-line assertion. `:623`
  (`assertFalse(any("COMPARED" …))`) and `:424` survive unchanged.
- **A structural cost the packet does not price.** The producer text can only
  be printed from inside `replay_half` at raise time, i.e. *before*
  `main:1012`'s `_print_comparisons(comparisons)`. So the new line lands above
  the ok/MISMATCH block rather than adjacent to the UNAVAILABLE line it
  explains, and the "no `COMPARED` line" shape now has an unrelated producer
  line floating at the top of the report.
- **Evidence cost.** (b) in either variant is a code change to the fence at the
  head of a PR whose whole point is byte-identity replay. It invalidates the
  executed evidence the packet relies on (F6: Sol 240's `Ran 45 tests` / `OK`
  at `9be7a229`), forcing a full-module re-run that the packet itself prices at
  ~8 minutes because of the retained-corpus replay class, plus new regressions
  for the moved line. That is a fourth round with the same signature on a
  defect that truthful documentation closes at zero behavioural risk —
  precisely what charter §9's second paragraph counsels against.

## Refutation of (c)/other

I considered three "something better" shapes and refute all three.

**(c1) Make `<detail>` machine-parseable — prefix each form with a tag, e.g.
`R7F CORPUS UNAVAILABLE: preflight-path=/…` / `producer=…`.** Genuinely
better *if* a machine consumer existed. **Refuted on the census:** the token
appears at five sites in the entire repository outside process traces —
`scripts/check_paper_round7_artifacts.py:24`, `:1013`, and
`tests/test_paper_round7_artifacts.py:424`, `:619`, `:859` — and nothing under
`docs/` or `.github/` (re-verified below). There is no machine consumer to
serve, and inventing a wire format for a hypothetical one, in a fence PR,
breaks `:859`'s exact-equality assertion for no present benefit. Under D-161 an
exit-3 line is a human diagnostic, not a claim-bearing number; a tag format is
over-engineering of exactly the kind D-161 prunes.

**(c2) Make the preflight raise the fully-resolved path** (`str(path.resolve())`
at `:883`), so the round-1 sentence becomes literally true. **Refuted:** it
would print a path the operator cannot map back to what they passed whenever a
capture directory is symlinked, replacing R-A2's small falsity with a larger
diagnostic one — and it is a behavioural change that breaks `:859` (whose
expectation is built from unresolved joins onto a resolved root) for a
statement that a two-word docstring edit makes true for free.

**(c3) Fix R-A3 in code — collect the replay's comparisons into `main`'s list
before the exception can discard them** (e.g. have `replay_half` attach them to
the exception, or accept the list as an out-parameter). This is the one change
I think is *substantively* right, and I still refuse to attach it to this PR:
it alters what the fence prints and what it exits on a mixed
drift-plus-unavailability input, it needs its own regression, and it re-opens
the byte-identity evidence. **It belongs in a registered follow-up, and this
PR's docstring must tell the truth about the current behaviour in the
meantime** — which is exactly what my recommended text does. Refuting my own
preferred fix on scope grounds is the point: the packet's question is which
*cure shape*, and the cure shape that makes every consumer's assertion true
under every reachable branch today is documentation.

**UNRULED: nothing.** The packet supplies enough primary evidence to decide Q1,
Q1-consumer and Q1-scope; I refuse no question.

## Recommendation

**ADOPT (a), with corrected operative text, extended by two sentences to cover
the exit-code mapping. REJECT (b) in both variants. Docstring-only in this PR.**

(a) survives because — and only because — its enumeration is derived from the
closed set of three raise sites (`:883`, `:904`, `:933`), verified by grep over
the committed file rather than from the last reviewer's counterexample. That is
what makes it structurally different from rounds 1–3 and what stops the
same-signature clock. It does not survive in the packet's wording (R-A1, R-A2),
and it must not be landed while the adjacent exit-code sentence stays false
(R-A3, R-A4), or a fourth reviewer will find that sentence with the same
"true for one branch, false for another" report and the gate will have bought
nothing.

### Operative text, verbatim

Replace `scripts/check_paper_round7_artifacts.py:14-19` (first paragraph) and
`:21-30` (second paragraph) with the following. No code changes.

```
The default invocation additionally re-runs both producers into a directory
under TMPDIR and requires byte identity for XD, AQ, and the XS-produced F4.
Three things end that replay half with exit 3: this script's own preflight
finds a required corpus entry absent, or either producer exits 3 from its own
preflight.  None is ever a pass.  ``--literals-only`` runs only the always-on
digest/field/literal half.
```

```
Exit codes: 0 when every comparison agrees, 2 when any comparison mismatches
(including a producer that fails with a code other than 3), and 3 when the
replay half ends as above.  Exit 3 preempts 2: the comparisons a stopped
replay had already collected are discarded, so an AS exit 3 discards the XD
and F4 byte comparisons and a mismatch coexisting with a stop is reported as 3
with no ``MISMATCH`` line.  Exit 3 also does not mean "a file was absent": a
producer exits 3 when a required file is present but its bytes do not match
the retained sha256.
Successful full replay ends with ``R7F COMPARED n / MISMATCHES m``;
``--literals-only`` uses the distinct ``R7F LITERALS-ONLY COMPARED`` token.  A
stopped replay instead ends with ``R7F CORPUS UNAVAILABLE: <detail>`` and
prints no ``COMPARED`` line.  ``<detail>`` is written at exactly three sites
and is therefore exactly one of three things: (i) the first required corpus
path the preflight finds absent -- name components joined onto the corpus root
after ``Path.resolve()``, so the root is resolved but the joined remainder is
not, and the path may name a directory (``<root>/runs/instrument_validation``)
rather than a file; (ii) a producer's stdout and stderr concatenated,
stripped, split into lines and rejoined with `` | `` on one line, when that
producer exits 3 having written something; (iii) the resolved corpus root,
when a producer exits 3 having written nothing.  A consumer must therefore
compare paths against the resolved form of the corpus root it passed, never
the as-given argument -- and must never stat ``<detail>`` unconditionally,
because in forms (ii) and (iii) it is not a path.
```

I checked each sentence against each of the three reachable branches and
against the exit-0/exit-2 paths:

- "0 when every comparison agrees" — `main:1017-1020`.
- "2 when any comparison mismatches" is exhaustive for exit 2: `:1002` returns
  2 on `any(not match)` **or** `spec is None`, and the `spec is None` path
  always carries a mismatching `"registry"` comparison (`digest_half:757-758`),
  so there is no exit-2 without a mismatch.
- The three `<detail>` forms are the three raise sites, verified by grep.
- The `Path.resolve()` clause now states exactly what `:998` + `:781-795` do.
- The "may name a directory" clause is R-A1's input, named in the text.

### What changes in the tests

**Nothing.** No assertion at `tests/test_paper_round7_artifacts.py:424`,
`:619-623`, or `:855-863` is affected, because no behaviour changes. F6's
executed evidence at `9be7a229` remains valid for the code; only the docstring
bytes move, and no test reads the docstring. I verified the two named classes
still pass at the reviewed code (see *Facts re-verified*, F5).

*Optional, not required by this ruling:* if the gate wants shape (iii) covered
by a regression rather than by a probe, a four-line addition to
`TypedArtifactCliTests` mirroring `:600-623` with
`subprocess.CompletedProcess(["stub-producer"], 3, "", "")` and asserting the
last line equals the prefix plus the resolved corpus root would pin it. I do
not make it a condition: F4 establishes no producer reaches it today, and
adding a test is a change to the PR under review.

### The biting counterfactual

For the ruling as a whole: **a corpus root holding the two
`runs_window_a_20260722` files but no `runs/instrument_validation` directory.**
On that single input the packet's (a)(i) is false (the detail is a directory,
not a file), (b) variant 2 is at its worst (the line names a path that exists),
and — if AS's tree is instead present-but-empty while XS's XD replay has
drifted — R-A3 fires and "2 for any mismatch" is false too. One ordinary
partial corpus falsifies the packet's own (a), refutes (b), and exposes the
sentence the packet did not put in scope. That is why the cure must be an
enumeration derived from the raise sites, and why it must extend one sentence
past `<detail>`.

### What this does NOT decide

- It does not decide whether `replay_half` *should* discard the comparisons it
  collected before an exit-3 raise (R-A3, and the fix sketched as c3). It rules
  only that the docstring must say that it does. Register the behavioural
  question; do not resolve it in this PR.
- It does not decide whether a producer's sha256 mismatch *should* be exit 3
  rather than exit 2 (R-A4). Same disposition.
- It does not decide anything about the DX registry, the placement census, the
  figure checks, or the other findings in the three reviewer files.
- It does not authorise a fourth docstring round. If a fifth reviewer finds a
  fourth false sentence in this paragraph, the site census in my
  "What does NOT refute (a)" section is the artifact to check first: if the
  new finding is at a site outside `{:883, :904, :933}` plus the exit-code
  mapping, the census was wrong and the failure is structural; if it is inside,
  the text above was mis-transcribed.

## Q1-consumer

**Verdict: the consumer set is five, not two, and my Q1 answer preserves every
one of them — trivially, because it changes no behaviour.**

Census re-run below (Facts, F3). Enumerated:

1. **`tests/test_paper_round7_artifacts.py:619-623`** (`TypedArtifactCliTests.
   test_multiline_producer_unavailable_is_flattened_to_last_line`) asserts
   exit 3, `lines[-1].startswith("R7F CORPUS UNAVAILABLE: ")`, `lines[-1]`
   contains `producer line one | producer line two`, and no line contains
   `COMPARED`. It pins form (ii). **Preserved.**
2. **`tests/test_paper_round7_artifacts.py:855-863`** (`InvocationTests.
   test_absent_corpus_exits_three_and_names_path`) asserts exit 3 and
   `stdout.splitlines()[-1] == "R7F CORPUS UNAVAILABLE: " + <missing_root>/…/instrument_evidence.json`,
   with no `COMPARED` line. It pins form (i), and its inline comment at
   `:835-837` is the only place "resolved" was said before round 1.
   **Preserved.**
3. **`tests/test_paper_round7_artifacts.py:424`** — a *negative* consumer:
   `assertNotIn("R7F CORPUS UNAVAILABLE", …)` when AS fails with code 1, which
   must route to `_producer_failure` and exit 2. The packet's Question omits it
   (hygiene H1). **Preserved.** It would also survive (b), so it does not
   discriminate; it is the assertion that would break if anyone "simplified" by
   collapsing the non-3 producer-failure path into the unavailable path.
4. **`--help` readers.** `main:975` is
   `argparse.ArgumentParser(description=__doc__)`, so the whole module
   docstring is the `--help` description. With argparse's default
   `HelpFormatter` the description is re-wrapped: the docstring's line breaks
   are collapsed and the ``…`` RST backquotes are printed literally. (Static
   reasoning; I did not execute `--help`.) Consequence for my operative text:
   every promise must survive reflow, which it does because each is a complete
   sentence and none depends on layout. This is the consumer round 1's Opus
   review identified as decisive — the not-yet-written night-launcher gate will
   be built from what `--help` prints — and it is the reason the cure has to be
   in the docstring rather than in a test comment.
5. **A human reading a night-launcher log.** What they most need is the thing
   the current docstring hides: that `UNAVAILABLE` can mean "present but the
   bytes moved" (R-A4) and that an exit 3 can be concealing a mismatch (R-A3).
   My text is the only candidate that tells them.

**Non-consumers, checked and cleared.** `docs/paper/round7/fill-checklist.md:24-36`
and `docs/paper/results-fill-registry.md:729,740,743` describe the fence — its
successful tails (`R7F COMPARED n / MISMATCHES 0`,
`R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`, `R7F PLACED n/16`) and the
fact that AS "returns exit 3 on `PopulationUnavailable` instead of raising" —
but neither quotes the `CORPUS UNAVAILABLE` line or its detail. Neither needs
an edit under (a). Under (b) variant 2 they would still not need one, since the
success tails are untouched. There is **no CI/`.github` consumer**: the census
returns nothing under `.github/`.

## Q1-scope

**Verdict: the cure belongs in this PR, and it is docstring-only. Do not defer
it; do not attach a code change to it.**

Contract-lens reasoning:

1. **The defect is a false statement in the contract, and the contract is the
   artifact under review.** Deferring it means merging a PR whose `--help` text
   is known-false on three reachable inputs, with three reviewer files on the
   record saying so. A documentation defect whose cure is bytes in the file
   being reviewed has no deferral rationale.
2. **No consumer requires a behavioural change.** All five consumers' assertions
   are true under the current code on every reachable branch; only the
   *description* of that code is wrong. When the contract can be made true by
   describing reality, changing reality instead is the more expensive and
   riskier of two cures.
3. **A code change here costs the executed evidence.** F6 records
   `Ran 45 tests` / `OK` for the full module at `9be7a229`. Any change to
   `replay_half` or `_producer_unavailable_message` voids it and forces a
   re-run whose retained-replay class the packet prices at ~8 minutes, plus
   fresh regressions — for a defect documentation closes at zero behavioural
   risk.
4. **Charter §9's same-signature rule points this way, not the other.** Three
   rounds have failed with the same signature; the next spend is the consult,
   and this gate is it. The consult's product should be the cure derived from
   the exhaustive site census — which is documentation — not a fourth guess
   with code attached. Note the inverse reading is available and I reject it
   explicitly: one could argue that three failed documentation rounds prove
   documentation is the wrong instrument and the code must simplify. That
   argument fails on the evidence, because rounds 1–3 did not fail *as
   documentation*; each failed by describing a subset of branches that the
   author had not enumerated. The census closes that failure mode directly.
5. **Register, do not block, the two behavioural items:** (R-A3) `replay_half`
   discards its collected comparisons when a producer exits 3, so a mismatch
   coexisting with an unavailability is reported as 3 with no `MISMATCH` line;
   (R-A4) a producer's sha256 mismatch on a present file routes to exit 3 under
   the word "UNAVAILABLE". Both are MATERIAL, neither is a false PASS, and both
   are properly scoped to a follow-up with its own regressions.

### Does D-161 change the answer?

**No — and it is worth being precise about which refutations it retires, because
it retires exactly the ones I already tiered as NITs.**

D-161 (`docs/decision_log.md:188`, and the section at `:10332-10344`) removes
the trusted operator from the adversary set, keeps fail-closed where the failure
is **physics/evidence or pre-registration**, and — per the ADDENDUM's operative
test — keeps fail-closed for **mistakes** while retiring **deliberate-only**
guards. Applied here:

- **Retired by D-161:** a corpus directory deliberately named with an embedded
  newline (which would break the "last line" contract); an AQ `validation_id`
  carrying a separator (independently unreachable, since `digest_half` returns 2
  on the AQ digest before `replay_half` runs); a symlink planted specifically to
  defeat path resolution. All were NITs before D-161 and are non-issues after.
- **Not retired by D-161:** R-A1 (a partial corpus missing the AS population
  tree is a mistake, not an attack — the mistake case D-161 expressly keeps
  fail-closed); R-A3 (honest producer drift, which D-161 names as in-scope);
  R-A4 (a re-issued artifact whose bytes moved — the *first* thing D-161's
  index row says the fence exists against). R-A2 is a mistake-shaped bite too:
  the operator who symlinks a capture directory for disk-space reasons is not
  an adversary.
- **What D-161 does supply** is the severity ceiling. Because an exit-3 line is
  a human diagnostic and not a claim-bearing number, and because exit 3 is never
  a pass, none of R-A1–R-A4 is a BLOCKER: no false PASS is reachable through
  any of them. That is why the ruling is "document truthfully now, register the
  behaviour for later" rather than "hold the PR". D-161 changes the *severity*
  and the *urgency*; it does not change *which candidate* survives.

## Facts re-verified

All commands run from `/Users/edr/code/JouleWise-wt-dx` unless the path is
absolute; no shell variables inside any heredoc; every command reproducible
as written. Read-only throughout.

**F7 — charter digest.** Run before any merits reading. Command and verbatim
output:

```
$ shasum -a 256 /Users/edr/code/JouleWise-wt-dx/docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  /Users/edr/code/JouleWise-wt-dx/docs/process/coldgate_charter.md
```

Matches the expected value supplied in my brief and F7. **VERIFIED.**

**Worktree state.** `git status --short` printed nothing (clean);
`git rev-parse HEAD` printed `4c88b94180f7f3c33afc9a024811e8b041c3faee`. All
code below was therefore read as committed bytes at `74fb5206` via `git show`,
per the packet.

**F1 — the helper and its two call sites.** VERIFIED, with one addition.

```
$ git show 74fb5206:scripts/check_paper_round7_artifacts.py | sed -n '841,846p'
def _producer_unavailable_message(
    completed: subprocess.CompletedProcess[str], fallback: Path
) -> str:
    output = (completed.stdout + completed.stderr).strip().splitlines()
    return " | ".join(output) if output else str(fallback)
```

Call sites `:904-906` (XS) and `:933-935` (AS) both pass `corpus_root`;
`main:998` is `corpus_root = (args.corpus_root or repository_root).resolve()`.
**Addition:** the helper concatenates *before* splitting, so an unterminated
final stdout line is glued to the first stderr line rather than separated by
`` | ``. My operative text says "concatenated, stripped, split into lines" to
keep that true.

**F2 — the preflight.** VERIFIED, with two corrections that bear on the ruling.

```
$ git show 74fb5206:scripts/check_paper_round7_artifacts.py | sed -n '878,884p'
def replay_half(
    repository_root: Path, corpus_root: Path, spec: RegistrySpec
) -> list[Comparison]:
    for path in _required_corpus_paths(corpus_root, repository_root, spec):
        if not path.exists():
            raise ArtifactsUnavailable(str(path))
```

```
$ git show 74fb5206:scripts/check_paper_round7_artifacts.py | sed -n '781,795p'
def _required_corpus_paths(corpus_root: Path, repository_root: Path, spec: RegistrySpec) -> list[Path]:
    required = [
        corpus_root
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "instrument_evidence.json",
        corpus_root
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "raw"
        / "powermetrics.plist",
        corpus_root / "runs" / "instrument_validation",
    ]
```

Correction 1: the third required entry is a **directory** (R-A1).
Correction 2: every entry is a plain join onto the resolved root; `.resolve()`
is never applied to the joined path (R-A2). The AQ-derived entries at
`:815-821` are likewise plain joins, with `validation_id` read from the
digest-pinned AQ artifact.

**F3 — the census.** VERIFIED exactly as stated: five sites, nothing under
`docs/` or `.github/`.

```
$ grep -rn "CORPUS UNAVAILABLE" scripts tests docs .github | grep -v "^docs/process_traces/"
scripts/check_paper_round7_artifacts.py:24:An unavailable corpus instead ends with ``R7F CORPUS UNAVAILABLE: <detail>``
scripts/check_paper_round7_artifacts.py:1013:            print(f"R7F CORPUS UNAVAILABLE: {exc}")
tests/test_paper_round7_artifacts.py:424:        self.assertNotIn("R7F CORPUS UNAVAILABLE", output.getvalue())
tests/test_paper_round7_artifacts.py:619:            lines[-1].startswith("R7F CORPUS UNAVAILABLE: "), output.getvalue()
tests/test_paper_round7_artifacts.py:859:            f"R7F CORPUS UNAVAILABLE: {missing_root / 'runs_window_a_20260722' / 'instrument_validation' / '20260722T145535-e941c821' / 'instrument_evidence.json'}",
```

**Additional census the packet does not carry — the raise-site closure**, which
is the load-bearing fact for adopting (a):

```
$ git show 74fb5206:scripts/check_paper_round7_artifacts.py | grep -n "ArtifactsUnavailable"
127:class ArtifactsUnavailable(RuntimeError):
883:            raise ArtifactsUnavailable(str(path))
904:                raise ArtifactsUnavailable(
933:                raise ArtifactsUnavailable(
1011:        except ArtifactsUnavailable as exc:
```

Exactly three raise sites, one catch. `digest_half` is invoked at `:1001`,
outside the guarded block (`:1008-1014`), so no fourth shape can reach the
handler.

**F4 — both producers print before exiting 3.** VERIFIED.

```
$ git show 74fb5206:scripts/paper_excursion_decomposition.py | sed -n '798,802p'
    try:
        derived = rederive(repository_root, corpus_root)
    except ArtifactsUnavailable as exc:
        print(f"artifacts unavailable: {exc}", file=sys.stderr)
        return 3
```

```
$ git show 74fb5206:scripts/paper_anchor_correction_quantified.py | sed -n '717,723p'
    try:
        payload = build_payload(
            args.repository_root.resolve(), args.corpus_root.resolve()
        )
    except PopulationUnavailable as exc:
        print(f"population unavailable: {exc}", file=sys.stderr)
        return 3
```

Each prints exactly one stderr line, so shape (iii) is unreachable through
either producer today, as F4 says. **Addition bearing on R-A4:** the XS
unavailability is raised for non-absence reasons too —

```
$ git show 74fb5206:scripts/paper_excursion_decomposition.py | grep -n "ArtifactsUnavailable"
93:class ArtifactsUnavailable(RuntimeError):
135:    raise ArtifactsUnavailable(
163:        raise ArtifactsUnavailable(f"{evidence_path} is not present")
170:        raise ArtifactsUnavailable("events.jsonl does not match its retained sha256")
800:    except ArtifactsUnavailable as exc:
```

`:170` is a *present file whose bytes moved*, and `:135` is "no candidate
`raw/powermetrics.plist` matched sha256" — both route to fence exit 3.
Likewise AS `:653` (`population_root holds no capture directories`).

**F5 — the two regressions.** VERIFIED by reading the excerpts against the
committed test file (`tests/test_paper_round7_artifacts.py:600-623` and
`:831-863`) and by execution:

```
$ mkdir -p <scratchpad>/coldseat-opus/tmp
$ cd /Users/edr/code/JouleWise-wt-dx && TMPDIR=<scratchpad>/coldseat-opus/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests
```

Observed tail, verbatim:

```
test_multiline_producer_unavailable_is_flattened_to_last_line (tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_multiline_producer_unavailable_is_flattened_to_last_line) ... ok
test_absent_corpus_exits_three_and_names_path (tests.test_paper_round7_artifacts.InvocationTests.test_absent_corpus_exits_three_and_names_path) ... ok
test_literals_only_cli_passes (tests.test_paper_round7_artifacts.InvocationTests.test_literals_only_cli_passes) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.504s

OK
```

(The full `-v` listing had ten `ok` lines; the three above are the ones this
ruling depends on.) The working tree is identical to `74fb5206` for these
paths per the packet and the clean `git status`, so this exercises the reviewed
code.

**F6 — Sol 240's full-module run at `9be7a229`.** **NOT re-run.** The full
module includes `ReplayAgainstRetainedCorporaTests`, which the packet prices at
~8 minutes and my brief excludes. I rely on F6 only for the scope argument
(that a code change would void already-executed evidence), never for a merits
conclusion. Anyone wishing to check it must run the module where the retained
corpora live.

**Claims I make that are NOT in the packet's facts, and how each was verified:**

- R-A1 (directory in the required list) — `:794`, quoted above.
- R-A2 (join is not resolved) — `:781-795`, `:815-821`, `:998`, quoted above.
- R-A3 (the AS exit-3 raise discards the XD/F4 byte comparisons) — read from
  committed bytes: `replay_half:887` creates a **local** `comparisons` list,
  `:910-916` appends the XD and F4 byte comparisons to it, `:931-935` raises,
  and `main:1010`'s `comparisons.extend(replay_half(...))` therefore never
  executes. Static trace over primary code; **not executed** (executing it
  needs a mocked mixed drift-plus-unavailability input, outside my licence).
  Anyone re-checking should read those four line ranges together.
- R-A4 (sha-mismatch routes to exit 3) — `paper_excursion_decomposition.py:135`,
  `:170`, `:800-802`; `paper_anchor_correction_quantified.py:653`, `:721-723`.
- Exit-2 exhaustiveness (`spec is None` always carries a mismatch) —
  `digest_half:755-758` plus `main:1002-1006`.
- The `--help` reflow claim — static reasoning over `argparse`'s default
  `HelpFormatter` given `main:975` `description=__doc__`; **not executed**, and
  labelled as such wherever used.

### Severity summary (charter §8, assessed independently of the verdict)

| Id | Finding | Severity |
| --- | --- | --- |
| R-A1 | Packet's (a)(i) says "file"; the third required entry is a directory | BLOCKER *against the packet's wording of (a)*; NIT against the code |
| R-A3 | "2 for any mismatch" false — exit 3 discards collected comparisons | MATERIAL |
| R-A4 | "3 for an absent corpus" false — sha mismatch on a present file exits 3 | MATERIAL |
| R-A2 | `Path.resolve()` sentence overclaims; only the root is resolved | MATERIAL |
| H3 | Packet did not scope the adjacent false exit-code sentence | MATERIAL (hygiene) |
| H1 | Question names two test consumers; F3 lists three | NIT (hygiene) |
| H2 | (a) stated in wording that cannot be adopted verbatim; (b) stated in two worked variants | NIT (hygiene) |
| — | Newline-bearing path breaks the last-line contract | NIT (retired by D-161 + the digest gate) |

**Where I expect to disagree with the lead's disposition:** the packet's framing
treats Q1 as a choice between documenting `<detail>` and simplifying the code.
I hold that both framings are too narrow — the `<detail>` grammar is *not* the
only false sentence in that paragraph, and shipping a cure that fixes only
`<detail>` sets up a fourth round with the same signature. Adopting (a) without
R-A1's and R-A3/R-A4's sentences would, in my view, be the error this gate was
convened to prevent.
