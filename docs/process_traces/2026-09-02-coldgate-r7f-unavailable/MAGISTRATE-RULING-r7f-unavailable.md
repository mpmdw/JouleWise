# Magistrate ruling — R7F `CORPUS UNAVAILABLE` docstring grammar (cold gate 2026-09-02)

Packet: `00-PACKET.md` (committed `4c88b941`). Seats, run blind and in
parallel from the same packet: cold Fable instance (`01-coldfable-r7f.md`,
sealed; committed sha256 `c5638dfd38b4c096654f59d8548075af1f1a92d4a6f276c7c6736f6584f0ca7c`; sealed-at-scratchpad sha256
`c39120fbcb9a42a9c2c855ecb7b42fbe078ab266b610a4c158e94d6d185e3409` before the
`<scratchpad>/` path redaction) and Opus 5 contract-lens refuter
(`02-opus-refute-r7f.md`, sealed; committed sha256 `2d1e0d50871d7db63ec34639e4137bbe69d3fe1d8b09d44d439ec969c99e1212`; sealed-at-scratchpad
sha256 `35b0674b2d31324a06486df524c10322dab390615cb65981608e5542ddb89dda`). Both
verified the charter digest `099de884…` before the merits; both disclosed
contamination: the cold Fable seat none; the Opus seat only the harness
preamble (standing doctrine text), unused for any conclusion.

## Q1 — ADOPT (a), with the Opus seat's operative text

Both seats independently rule ADOPT (a): document the code as it is, with an
enumeration derived from the CLOSED site census — `grep -n ArtifactsUnavailable
scripts/check_paper_round7_artifacts.py` at `74fb5206` returns exactly three
raise sites (`:883` preflight, `:904` XS exit 3, `:933` AS exit 3), one class
(`:127`), one catch (`:1011`); `digest_half` is called at `:1001` outside the
`try`, and the producers run as subprocesses. Rounds 1–3 each described the
subset the previous reviewer's counterexample suggested; this is the first
sentence derived from the census, which is what ends the same-signature clock.
No code change, no test change in PR #272.

The two seats differ only in wording, and the Opus refuter's text is adopted
because it survives four concrete refutations the cold Fable text does not
(each re-verified at the bench, below):

- R-A1 — the packet's and the cold seat's "(i) … corpus **file**" is false:
  the third required entry (`:794`) is the DIRECTORY `runs/instrument_validation`.
  An ordinary partial corpus (XS capture copied, AS tree not) prints a
  directory. Adopted text says "path … may name a directory".
- R-A2 — "printed after `Path.resolve()`" is false for the joined remainder:
  only the root resolves (`:998`); `:781-795` joins literal components. The
  cold seat had already narrowed this; the adopted text states it outright.
- R-A3 — the adjacent sentence "2 for any mismatch" is false: an AS exit 3 at
  `:933` propagates out of `replay_half` AFTER the XD/F4 byte comparisons were
  appended to its local list (`:910-916`), so `main:1010`'s `extend` never
  runs and a real drift is reported as 3 with no `MISMATCH` line. Not a
  soundness hole (3 is never a pass); a diagnostic-destruction hole, and
  exactly the honest-drift case D-161 keeps fail-closed. Documented now;
  behaviour registered below, NOT changed in this PR.
- R-A4 — "3 for an absent corpus" is false: `paper_excursion_decomposition.py:169-170`
  exits 3 on a PRESENT `events.jsonl` whose sha256 moved (the re-issued
  artifact case), and the fence prints that sentence as `<detail>` with no
  path in it. Documented now.

One magistrate amendment to the Opus text: "Exit 3 preempts 2" is qualified to
the replay half, because the digest half runs first (`:1001-1006`) and returns
2 on its own mismatches before any replay. The cold seat's clause "Only (i) is
a missing path; (iii) is a path that exists" is kept — it is the one sentence a
log reader needs.

Operative text: the module docstring paragraphs 2–3 of
`scripts/check_paper_round7_artifacts.py` as committed with this ruling (from
"The default invocation additionally" to the closing `"""`).

Biting counterfactual (Opus, executed there; re-derived here from the code):
a corpus root holding the two `runs_window_a_20260722` files but no
`runs/instrument_validation` directory → last line
`R7F CORPUS UNAVAILABLE: <root>/runs/instrument_validation`, a directory. The
pre-ruling sentence ("required corpus file absent … missing resolved path") is
false for it; the ruled clause (i) is true. The cold seat's silent-exit-3 stub
(`--corpus-root /var/tmp/../tmp` → `/private/var/tmp`) falsifies both the
round-1 and round-2 sentences and is true under clause (iii).

What Q1 does NOT decide: whether `replay_half` should keep the comparisons it
collected before an exit-3 raise (R-A3); whether a producer sha256 mismatch
should be exit 2 rather than 3 (R-A4); whether the `str(fallback)` branch
should exist (the cold seat's registered shape
`f"{label} exit 3: {flattened or 'no output'}"`); producer exit-3 manners.
Each is registered as a follow-up (kernel row `R7F-EXIT3-SEMANTICS-01`, to be
added in the post-merge kernel batch), with the revisit trigger both seats
name: the first non-human parser of `<detail>`, or the first real drift
report lost to R-A3.

## Q1-consumer — ADOPT: no consumer beyond tests, `--help`, and a human

Census at `74fb5206`, whole tree excluding process traces: five sites —
`scripts/check_paper_round7_artifacts.py:24` (docstring), `:1013` (print);
`tests/test_paper_round7_artifacts.py:424` (negative: non-3 producer failure
must NOT print the prefix), `:619`/`:621` (branch ii), `:859` (branch i).
`--help` re-renders the docstring (`:975`, `description=__doc__`). Nothing
under `docs/` or `.github/`; the paper docs describe only the `COMPARED`
tail. (a) changes no code, so every assertion is preserved.

## Q1-scope — docstring-only in PR #272

Both seats: cure in this PR, docstring only; no code or test edit for this
defect. The behavioural questions above are registered, not resolved. D-161
does not change the answer: it prunes the operator-deliberate NITs (newline
paths, planted symlinks) and caps severity at MATERIAL (no false PASS is
reachable), while R-A1/R-A3/R-A4 are mistake- and drift-shaped.

This ruling does not authorise a fourth docstring round. If a later reviewer
finds a false sentence in these paragraphs, check the site census first: a
finding at a site outside `{:883, :904, :933}` plus the exit-code mapping means
the census was wrong and the failure is structural (consult); a finding inside
it means the text was mis-transcribed (bench fix, one delta pass).

## Executed evidence

Bench, `/Users/edr/code/JouleWise-wt-dx`, after the docstring edit:

```
$ git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/check_paper_round7_artifacts.py | grep -n "ArtifactsUnavailable"
127:class ArtifactsUnavailable(RuntimeError):
883:            raise ArtifactsUnavailable(str(path))
904:                raise ArtifactsUnavailable(
933:                raise ArtifactsUnavailable(
1011:        except ArtifactsUnavailable as exc:
$ git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/check_paper_round7_artifacts.py | sed -n 794p
        corpus_root / "runs" / "instrument_validation",
$ git -C /Users/edr/code/JouleWise-wt-dx show 74fb5206:scripts/paper_excursion_decomposition.py | sed -n 169,170p
    if _sha256(events_raw) != hashes["events.jsonl"]:
        raise ArtifactsUnavailable("events.jsonl does not match its retained sha256")
$ cd /Users/edr/code/JouleWise-wt-dx && python3 -c "import ast; ast.parse(open('scripts/check_paper_round7_artifacts.py').read())"
$ mkdir -p /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmpcg
$ cd /Users/edr/code/JouleWise-wt-dx && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmpcg python3 -m unittest tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests 2>&1 | tail -3
Ran 10 tests in 0.531s

OK
$ cd /Users/edr/code/JouleWise-wt-dx && python3 scripts/check_paper_round7_artifacts.py --literals-only | tail -1
R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0
$ cd /Users/edr/code/JouleWise-wt-dx && python3 scripts/check_paper_round7_artifacts.py --help | grep -c "exactly three sites"
1
$ cd /Users/edr/code/JouleWise-wt-dx && git diff --stat
 scripts/check_paper_round7_artifacts.py | 44 ++++++++++++++++++++++-----------
 1 file changed, 30 insertions(+), 14 deletions(-)
```

The full module (`tests.test_paper_round7_artifacts`, ~8 min retained-corpus
replay) is executed by the fresh pass over this commit and by the rebuilt
integration tree before merge; no test reads the docstring.
