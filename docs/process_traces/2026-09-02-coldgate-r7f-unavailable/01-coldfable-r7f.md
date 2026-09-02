# SEALED cold-Fable ruling — R7F `CORPUS UNAVAILABLE` docstring grammar

Packet: `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/00-PACKET.md`
(worktree `/Users/edr/code/JouleWise-wt-dx` @ `4c88b941`; code under review at
`74fb5206`, confirmed byte-identical to `4c88b941` for all four primary files).
Seat: cold Fable, fresh session, no loop context. Ruling date 2026-09-02.

## Disclosure

**Charter digest computed:**
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` for
`docs/process/coldgate_charter.md` — matches the expected value. Charter §3–§5
and §8 read before anything else.

**Files read (complete list):**

- `docs/process/coldgate_charter.md` (§3, §4, §5, §8 only)
- `docs/process_traces/2026-09-02-coldgate-r7f-unavailable/00-PACKET.md`
- all ten excerpt files in that directory: `docstring-73f7fcc2.txt`,
  `docstring-7fc87a7f.txt`, `docstring-74fb5206.txt`, `helper-74fb5206.txt`,
  `preflight-74fb5206.txt`, `xs-site-74fb5206.txt`, `as-site-74fb5206.txt`,
  `main-handler-74fb5206.txt`, `test-multiline-74fb5206.txt`,
  `test-absent-corpus-74fb5206.txt`
- `docs/process_traces/2026-09-02-dx-registry/19-opus-counter-review.md`
  (§4 lines 140–190 and SHOULD-FIX 2 lines 262–283 only; the grep for the
  section also surfaced the first two lines of NIT 1, which I did not use)
- `docs/process_traces/2026-09-02-dx-registry/20-terra-239-delta-3.md`
  (SF2-CONTRACT JSON block lines 18–30 and prose lines 115–126 only)
- `docs/process_traces/2026-09-02-dx-registry/21-sol-240-fresh-pass.md`
  (SF1-DOC-FALLBACK JSON block lines 18–30, verification V3 lines 66–75,
  prose lines 99–106 only)
- `scripts/check_paper_round7_artifacts.py` @ `74fb5206` (lines 1–40,
  125–130, 781–850, 870–890, 895–940, 945–1020 via `git show`)
- `tests/test_paper_round7_artifacts.py` @ `74fb5206` (lines 35–57 grep,
  405–440, 595–599, 830–866 via `git show`; class/def index via grep)
- `scripts/paper_excursion_decomposition.py:790-805` @ `74fb5206`
- `scripts/paper_anchor_correction_quantified.py:710-726` @ `74fb5206`
- `docs/decision_log.md`: index row for D-161 (line 188) and the D-161
  section (lines 10332–10344); the first 80 lines of the file scrolled past
  when my first `grep '^### D-161'` matched nothing (the heading is `##`,
  not `###` — packet nit, harmless), and I did not use them.
- `docs/paper/round7/fill-checklist.md:20-34` and
  `docs/paper/results-fill-registry.md:736-744` @ `74fb5206` — opened ONLY
  because the Q1-consumer census (`git grep check_paper_round7_artifacts`)
  hit them; I read only the lines around the hit to confirm neither
  mentions the UNAVAILABLE line. These are paper-fill reference docs, not
  narrative state docs; disclosed anyway.

**Contamination:** none. I read no README/RUN_STATE/TASK_QUEUE/orchestration/
playbook/MAGISTRATE-NOTES/disposition/CLAUDE*/memory file, no other seat's
output, and carried no prior context on this PR. The system context
delivered to this session contained a generic project memory index; I did
not open any memory file and none of that index concerns R7F, this PR, or
the sentence under review. Nothing under the worktree was written;
`git status --short` was empty before and after every execution.

**Executed:** only `TypedArtifactCliTests` and `InvocationTests` (10 tests,
OK) plus two in-process probes of the fence module, all with
`TMPDIR=<scratchpad>/coldseat-fable/tmp`
and `PYTHONDONTWRITEBYTECODE=1`. No codex/claude process launched; no
canonical discover.

## Q1 ruling

**Verdict: ADOPT (a).** Document the code as it is, with a sentence whose
clauses map one-to-one onto the three exit-3 string sources in the script.
No code change, no test change, in this PR.

**Why (a) and not (b).** The oscillation is not a code defect; it is three
successive docstrings each describing one `raise`/`return` site and missing
another. The terminal cure for that class is a sentence that is exhaustive
BY CONSTRUCTION — one clause per site — which is verifiable now by reading
the four sites (`:883`, `:904-905`, `:933-934`, `:845`) and needs no
delta re-audit. (b) would be a fourth code fix round on a PR that has
already shown fix rounds re-falsify the sentence, and its only beneficiary
is a machine consumer of `<detail>` that does not exist (Q1-consumer below).
Under D-161 (index row, `docs/decision_log.md:188`: fail-closed and
engineering effort stay where the failure is physics/evidence or
pre-registration; the operator is not the adversary) an exit-3 line is a
diagnostic for a human, and shaping it for a hypothetical parser is the
over-engineering pattern the decision retires. Severity of the round-3
finding (Sol SF1-DOC-FALLBACK): NIT — branch (iii) is unreachable with the
two real producers (F4, re-verified) — but it is a true statement about the
code and the docstring must not be false, so it is cured here.

**Operative docstring text** — replace lines 14–31 of
`scripts/check_paper_round7_artifacts.py` (from `The default invocation` to
the closing `"""`) with the following, verbatim:

```
The default invocation additionally re-runs both producers into a directory
under TMPDIR and requires byte identity for XD, AQ, and the XS-produced F4.
An absent retained corpus exits 3 and names the missing resolved path; a
producer that itself exits 3 (its own corpus preflight) also exits 3, and the
last line carries what that producer printed (grammar below).  Neither is
ever a pass.  ``--literals-only`` runs only the always-on
digest/field/literal half.

Exit codes: 0 for agreement, 2 for any mismatch, 3 for an absent corpus.
Successful full replay ends with ``R7F COMPARED n / MISMATCHES m``;
``--literals-only`` uses the distinct ``R7F LITERALS-ONLY COMPARED`` token.
An unavailable corpus instead ends with ``R7F CORPUS UNAVAILABLE: <detail>``
and prints no ``COMPARED`` line.  ``<detail>`` is exactly one of three
strings, one per exit-3 site in this script: (i) when this script's own
preflight finds a required corpus file absent, the path of the first such
file; (ii) when a producer exits 3 and printed anything, the producer's
stdout followed by its stderr, stripped, with its lines joined by `` | ``;
(iii) when a producer exits 3 and printed nothing, the corpus root.  Only
(i) is a missing path; (iii) is a path that exists.  The corpus root is
passed through ``Path.resolve()`` before any path is built or printed, so a
consumer must compare against the resolved form of the root it passed,
never the as-given argument.
"""
```

Clause-to-code map (each verified at `74fb5206`):

- (i) ↔ `replay_half` `:881-883`, `raise ArtifactsUnavailable(str(path))`
  for the first absent entry of `_required_corpus_paths(corpus_root, …)`
  (`:781-820`; every required path is built under `corpus_root`).
- (ii) ↔ `_producer_unavailable_message` `:841-845`, non-empty branch
  `" | ".join(output)` where
  `output = (completed.stdout + completed.stderr).strip().splitlines()`;
  reached from `:904-905` (XS) and `:933-934` (AS).
- (iii) ↔ the same helper's `else str(fallback)`; both call sites pass
  `corpus_root`, which `main` resolved at `:998`.
- "passed through `Path.resolve()`" ↔ `:998`
  `corpus_root = (args.corpus_root or repository_root).resolve()`. Note the
  wording is deliberately narrower than the round-1 sentence ("the path is
  printed after `Path.resolve()`"): the fence resolves the ROOT and joins
  literal segments; it does not re-resolve the joined path. The
  narrower wording is exactly what `test_absent_corpus_exits_three_and_names_path`
  (`tests/…:836-839`) relies on and introduces no new claim.
- "prints no `COMPARED` line" ↔ `main` `:1011-1014` prints the comparisons
  and the prefix line and returns 3 without calling `_print_tail`.

**Existing test assertions that change:** none.
`tests/test_paper_round7_artifacts.py:600-623` (branch ii) and `:831-865`
(branch i) remain exactly as they are and pass (executed, see §Facts).
`:424` (`assertNotIn("R7F CORPUS UNAVAILABLE", …)` for a non-3 producer
failure) is untouched. I do NOT require a new test for branch (iii) in this
PR: the branch is unreachable with the repository's producers (F4) and was
probe-verified by Sol 240 (V3) and by me (below). If a later change makes a
silent exit-3 producer possible, that change carries the (iii) regression.

**Biting counterfactual** (executed this session, replayable in §Facts):
stub producer `CompletedProcess(["stub-producer"], 3, "", "")`, preflight
mocked empty, `main(["--corpus-root", "/var/tmp/../tmp"])` →
`rc = 3`, last line `R7F CORPUS UNAVAILABLE: /private/var/tmp`, no
`COMPARED` line. The pre-ruling sentence ("the producer's stdout+stderr
flattened to one line … when a producer exits 3") is FALSE for this input —
the flattened output is the empty string and the line does not carry it.
The ruled clause (iii) is TRUE: the detail is the resolved corpus root,
a path that exists. The same input also falsifies the round-1 sentence
(`<resolved path>` of something MISSING) — `/private/var/tmp` is present.

**What Q1 does NOT decide:**

- whether the `str(fallback)` branch should exist at all, or what a
  simplified helper should return (see Q1-scope for the registered shape);
- whether producers must be required to print on exit 3;
- the grammar of the sibling non-3 failure row `_producer_failure`
  `:834-838` (`"{rc}: {last four lines | 'no output'}"` on a `MISMATCH
  replay XS/AS exit` line) — a different line, not under review;
- any contract for a future night-launcher gate beyond "prefix + exit code";
- whether `argparse`'s reflow of `__doc__` in `--help` (`:975`) matters —
  it preserves the words, which is all that is asserted.

## Q1-consumer ruling

**Verdict: ADOPT — there is no consumer of the last line other than the two
tests (plus one negative assertion) and a human reading the log; (a)
preserves every assertion trivially because it changes no code.**

Census at `74fb5206`, whole tree excluding `docs/process_traces`
(`git grep -n "CORPUS UNAVAILABLE" 74fb5206 -- . ':!docs/process_traces'`):
exactly five sites —
`scripts/check_paper_round7_artifacts.py:24` (docstring), `:1013` (the
print); `tests/test_paper_round7_artifacts.py:424` (negative: a non-3
producer failure must NOT emit the prefix), `:619` (last line startswith the
prefix, and `:621` contains `producer line one | producer line two`), `:859`
(exact last-line equality with the resolved missing
`…/instrument_evidence.json`). Nothing under `docs/`, `.github/`, or any
shell/Makefile/YAML. The only other references to the fence outside its own
files are `docs/paper/round7/fill-checklist.md:24-34` and
`docs/paper/results-fill-registry.md:740`, both of which describe only the
`R7F COMPARED` success tail and never the UNAVAILABLE line. The Opus §4
"night-launcher gate" is hypothetical (its own words: "does not exist yet"),
and a gate needs only the prefix and exit code, which (a) leaves unchanged.

What each consumer asserts and why (a) preserves it: `:424` — no code
change, the prefix is still printed only from `:1013` under
`ArtifactsUnavailable`; `:619/:621` — branch (ii) unchanged; `:859` —
branch (i) unchanged; human — the docstring (and `--help`) now tells them
which of three things they are looking at and that (iii) is not a missing
path.

## Q1-scope ruling

**Verdict: docstring-only in this PR (the text above). No code or test edit
for this defect lands in PR #272.** The registered later item is a NIT, not
a task, with a revisit trigger:

- Shape, if ever taken up: drop the `fallback: Path` parameter and have the
  two call sites pass a label, so the helper returns
  `f"{label} exit 3: {' | '.join(output) or 'no output'}"` (matching the
  `_producer_failure` idiom at `:834-838`). `<detail>` then has two
  self-labelling grammars — a missing path, or `XS exit 3: …` / `AS exit
  3: …` — and the `:619/:621` assertions still pass as written (`startswith`
  prefix, `assertIn` flattened text); `:859` is unaffected.
- Revisit trigger: the first time anything OTHER than a human is written to
  parse text after the prefix. Until then, under D-161 the line is a
  diagnostic and the fallback is harmless.

Reason: every code edit in this PR costs a delta re-audit; (a) is verifiable
by reading; the code has been stable since `9be7a229` and the full module
passed there (F6, not re-run by me by packet instruction).

## Facts re-verified

Executed from `/Users/edr/code/JouleWise-wt-dx` (HEAD `4c88b941`, clean).
All commands read-only or scratch-only; `git status --short | wc -l` printed
`0` after each execution block.

**F7 (charter digest) and worktree state:**

```
shasum -a 256 /Users/edr/code/JouleWise-wt-dx/docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  /Users/edr/code/JouleWise-wt-dx/docs/process/coldgate_charter.md

git -C /Users/edr/code/JouleWise-wt-dx status --short | head        -> (empty)
git -C /Users/edr/code/JouleWise-wt-dx rev-parse HEAD              -> 4c88b94180f7f3c33afc9a024811e8b041c3faee
git -C /Users/edr/code/JouleWise-wt-dx diff --stat 74fb5206 4c88b941 -- scripts/check_paper_round7_artifacts.py tests/test_paper_round7_artifacts.py scripts/paper_excursion_decomposition.py scripts/paper_anchor_correction_quantified.py
                                                                   -> (empty: primary files unchanged since 74fb5206)
```

**F1, F2 (helper, call sites, preflight, resolve at :998) — read, then
probed.** Line numbers:

```
git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/check_paper_round7_artifacts.py | grep -n '_producer_unavailable_message\|raise ArtifactsUnavailable\|corpus_root = (args'
841:def _producer_unavailable_message(
883:            raise ArtifactsUnavailable(str(path))
904:                raise ArtifactsUnavailable(
905:                    _producer_unavailable_message(xs, corpus_root)
933:                raise ArtifactsUnavailable(
934:                    _producer_unavailable_message(anchor, corpus_root)
998:    corpus_root = (args.corpus_root or repository_root).resolve()
```

Helper probe (all four input shapes; run with cwd = the worktree):

```
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python - <<'EOF'
import importlib.util, subprocess, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("fence", "scripts/check_paper_round7_artifacts.py")
m = importlib.util.module_from_spec(spec); sys.modules["fence"] = m; spec.loader.exec_module(m)
fb = Path("/resolved/corpus")
CP = subprocess.CompletedProcess
print("silent   ->", repr(m._producer_unavailable_message(CP(["p"],3,"",""), fb)))
print("ws-only  ->", repr(m._producer_unavailable_message(CP(["p"],3,"  \n\n","\n"), fb)))
print("one-line ->", repr(m._producer_unavailable_message(CP(["p"],3,"","artifacts unavailable: /x/instrument_evidence.json is not present\n"), fb)))
print("two-line ->", repr(m._producer_unavailable_message(CP(["p"],3,"a\nb\n","c\n"), fb)))
EOF
silent   -> '/resolved/corpus'
ws-only  -> '/resolved/corpus'
one-line -> 'artifacts unavailable: /x/instrument_evidence.json is not present'
two-line -> 'a | b | c'
```

**Biting counterfactual end to end through `main`** (cwd = the worktree):

```
PYTHONDONTWRITEBYTECODE=1 TMPDIR=<scratchpad>/coldseat-fable/tmp /Users/edr/code/JouleWise/.venv/bin/python - <<'EOF'
import io, subprocess, sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
sys.path.insert(0, "tests")
import test_paper_round7_artifacts as T
FENCE = T.FENCE
spec = FENCE.parse_registry(T.REGISTRY_PATH)
silent = subprocess.CompletedProcess(["stub-producer"], 3, "", "")
out = io.StringIO()
with mock.patch.object(FENCE, "digest_half", return_value=(spec, [])), \
     mock.patch.object(FENCE, "_required_corpus_paths", return_value=[]), \
     mock.patch.object(FENCE, "_run_producer", return_value=silent), redirect_stdout(out):
    rc = FENCE.main(["--corpus-root", "/var/tmp/../tmp"])
print("rc =", rc)
print("last line =", repr(out.getvalue().splitlines()[-1]))
print("resolved root =", repr(str(Path("/var/tmp/../tmp").resolve())))
print("any COMPARED line =", any("COMPARED" in l for l in out.getvalue().splitlines()))
EOF
rc = 3
last line = 'R7F CORPUS UNAVAILABLE: /private/var/tmp'
resolved root = '/private/var/tmp'
any COMPARED line = False
```

**F3 (census):**

```
git -C /Users/edr/code/JouleWise-wt-dx grep -n "CORPUS UNAVAILABLE" 74fb5206 -- . ':!docs/process_traces'
74fb5206:scripts/check_paper_round7_artifacts.py:24:An unavailable corpus instead ends with ``R7F CORPUS UNAVAILABLE: <detail>``
74fb5206:scripts/check_paper_round7_artifacts.py:1013:            print(f"R7F CORPUS UNAVAILABLE: {exc}")
74fb5206:tests/test_paper_round7_artifacts.py:424:        self.assertNotIn("R7F CORPUS UNAVAILABLE", output.getvalue())
74fb5206:tests/test_paper_round7_artifacts.py:619:            lines[-1].startswith("R7F CORPUS UNAVAILABLE: "), output.getvalue()
74fb5206:tests/test_paper_round7_artifacts.py:859:            f"R7F CORPUS UNAVAILABLE: {missing_root / 'runs_window_a_20260722' / 'instrument_validation' / '20260722T145535-e941c821' / 'instrument_evidence.json'}",
```

Five sites, none under `docs/` or `.github/` — F3 confirmed. Packet nit: F3
lists `:424` as a consumer; it is a NEGATIVE assertion (prefix must be
absent on a non-3 failure), which (a) also preserves.

**F4 (both producers print one stderr line then `return 3`):** read at
`git show 74fb5206:scripts/paper_excursion_decomposition.py` lines 798–802
(`print(f"artifacts unavailable: {exc}", file=sys.stderr)` / `return 3`) and
`git show 74fb5206:scripts/paper_anchor_correction_quantified.py` lines
719–723 (`print(f"population unavailable: {exc}", file=sys.stderr)` /
`return 3`). Confirmed: branch (iii) is reachable today only through a stub.

**F5 (the two tests):**

```
cd /Users/edr/code/JouleWise-wt-dx && PYTHONDONTWRITEBYTECODE=1 TMPDIR=<scratchpad>/coldseat-fable/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests
----------------------------------------------------------------------
Ran 10 tests in 0.501s

OK
```

`test_multiline_producer_unavailable_is_flattened_to_last_line` is in
`TypedArtifactCliTests` (`tests/…:595,600`) and
`test_absent_corpus_exits_three_and_names_path` is in `InvocationTests`
(`tests/…:803,831`), so both ran. Assertions read and match the packet's
paraphrase.

**F6:** NOT re-verified (full-module run forbidden by the packet); relied on
only for the Q1-scope observation that the code has been green since
`9be7a229`, which is not load-bearing for the Q1 verdict.

**`--help` prints the docstring** (relevant to the human consumer):

```
cd /Users/edr/code/JouleWise-wt-dx && PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/check_paper_round7_artifacts.py --help | grep -n 'UNAVAILABLE\|<detail>'
25:unavailable corpus instead ends with ``R7F CORPUS UNAVAILABLE: <detail>`` and
26:prints no ``COMPARED`` line. ``<detail>`` is the missing resolved path when
```

— confirms `argparse.ArgumentParser(description=__doc__)` at `:975`
surfaces the sentence to the operator (reflowed).

— SEALED —
