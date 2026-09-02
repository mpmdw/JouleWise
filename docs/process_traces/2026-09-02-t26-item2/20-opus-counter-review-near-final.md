# Opus counter-review — PR #275 @ 5f04e147

Seat: D-118 gate item 6, Opus counter-review on the near-final head. Read-only;
no writes outside this scratchpad. Scope: `git diff main...HEAD` (main
`403998e1`), the trace directory `docs/process_traces/2026-09-02-t26-item2/`,
and the live bodies of PRs 272 / 273 / 275. Three code commits post-date the
earlier Opus pass (13b): `5ed6f1e9`, `55bf9f73`, `c01c39bb`, `8207364c`
(`d14a818d` and `5f04e147` are trace-only).

---

## 1. The ledger as a mechanism: what a filled row proves vs. asserts

A filled ledger row proves exactly four things and asserts everything else.
The checker parses the twelve-row table under the literal heading `## Gate
ledger (D-118 / D-121)` (`scripts/check_gate_ledger.py:16`, `:65`), keys rows by
the integer in the FIRST cell (`:98`, `KEYS = tuple(range(1, 13))` at `:14`),
and validates only the THIRD cell (`:109`, `:153-187`). So it proves: (a) all
twelve keys are present exactly once and none is `NOT-RUN`/empty
(`:147-162`) — i.e. the author was forced to say something about every gate
item, which is the whole point against the MISTAKE class; (b) the evidence
string is machine-shaped, `RUN <token>` with an uppercase `RUN` and no
backticks (`:154-169`); (c) for items 1–11 the token resolves at the PR head —
either a regular file under the repo root, reachable without `/`, `~`, `..`,
`://` (`:113-120`, copied verbatim from `scripts/gen_state.py:131-140`), or a
commit object the checkout knows (`:123-133`); (d) for item 12 the token is a
prefix of the PR head sha (`:179-183`), which binds the ledger to one exact
merge candidate and is the only row whose evidence cannot be satisfied by a
stale artifact. What it merely ASSERTS is the entire semantic content: that the
cited file is *about* the gate item, that the gate item was actually performed,
that the reviewer was independent, and — because the LABEL cell is never read —
that the key still means what D-118 says it means. That cut is deliberate and
correct: validating label prose would put a second copy of D-118 doctrine inside
a CI script, where it would drift from `docs/decision_log.md` silently (luna
199's labels-as-doctrine finding; the template states the rule at
`.github/pull_request_template.md:5`, "Row labels are keys"). The residual hole
is real and known: `RUN README.md` satisfies any of items 1–11, and a `RUN
<sha>` proves only that the object exists in the checkout, not that it belongs
to this PR's work — both are out of the threat model by D-161 (the operator is
not the adversary). This PR's own body demonstrates the hole concretely and
honestly: item 6 cites `13b-opus-207b-counter-review.md`, which resolves as a
path and therefore passes, while the row's text says "near-final head" and 13b
reviewed the cold-gate head three code commits earlier (finding F1). Replication
rule for a D-118 reader: **the ledger is an existence-and-binding check over
twelve mandatory keys, plus a human-read pointer; it converts "I forgot item 5"
into a red check, and it converts nothing else.**

## 2. Is `_split_table_row` exactly the ruled L2 rule, and is the table-boundary
rule GitHub's?

**The splitter is exactly the ruled rule and nothing more.** Ruling L2
(`16-MAGISTRATE-RULING-gateledger-splitter.md:57-63`) specifies: split on every
`|`; a `|` preceded by an odd run of backslashes is literal and its escaping
backslash is consumed; leading/trailing empty cells dropped; cells stripped; no
inline syntax modelled. `_split_table_row` (`scripts/check_gate_ledger.py:19-45`)
is a single character loop with one state variable, `backslashes` (`:39`); the
odd-parity branch pops the escaping backslash and emits a literal pipe
(`:30-32`); cells are stripped at `:34` and `:40`; the leading and trailing empty
cells are dropped at `:41-44`. There is no backtick, asterisk, bracket, or fence
state anywhere in the function — the code-span scanner from round 1 is gone. The
arity refusal is the ruled one, verbatim in message text, recorded in a
`malformed: set[int]` returned alongside the rows (`:103-110`), and `check()`
skips missing/duplicate/evidence logic for a malformed key (`:143-144`) — i.e.
Sol's "silent `continue`" dissent stayed rejected. The spec's own examples plus
the two backslash-parity cases are pinned as a table-driven test
(`tests/test_check_gate_ledger.py:209-224`), including `| a `b | c` |` →
`["a `b", "c`"]`, so any future "helpful" inline-aware splitter fails.

**The table-boundary rule is a simplification, and I verified the divergence
live against GitHub's own renderer.** `_ledger_rows` (`:76-90`) starts the table
at the first line after the heading that contains a `|`, and ends it at the
first line that does not; rows after that are reported as `ledger row outside
the ledger table` (`:80-87`). GitHub does neither. (i) GitHub requires a
delimiter row: a lone paragraph line containing a pipe is a `<p>`, not a table —
`gh api /markdown` returned `<p dir="auto">Filled by the magistrate |
2026-09-02.</p>` for exactly that line, while the checker takes it as the table
start and then emits 25 defect lines (1 unrecognised + 12 outside-table + 12
missing) none of which names the cause. (ii) GitHub does NOT end a table at a
non-pipe line: the same probe rendered `trailing prose without a pipe` as a
one-cell row and CONTINUED the table into the following `| 2 | b | RUN y |`,
where the checker ends the table and calls that row "outside". Both divergences
fail CLOSED (the checker refuses bodies GitHub renders fine; it never accepts a
row GitHub would drop), and the cold ruling flagged this exact class as
"table-CONTEXT divergence… flagged, not ruled" with the shape that was then
implemented (`16-…:107-113`). Does it matter for a body a real author would
write? Only for one shape: a sentence containing a `|` between the ledger
heading and the table. The template's preamble has no pipes and authors rarely
edit it, so the probability is low — but the failure output is 25 unhelpful
lines, and while the check is advisory that is a diagnosis cost, not a merge
block. Graded NIT (F4) with the cure named there; it becomes a SHOULD-FIX the
day ED-BRANCH-PROTECTION-E1-01 makes this a required check.

## 3. The two-layer `:`/`#` arrangement (8207364c)

**Coherent, and the parity function must NOT own the rule.** `_valid_path`
(`scripts/check_gate_ledger.py:113-120`) is byte-for-byte the path half of
`scripts/gen_state.py:131-140` — same guard expression at `:117` vs
`gen_state.py:136`, same `os.path.join(root, *path.split("/"))`, same
`os.path.isfile`. Its entire value is that a reader can diff the two and see
equality; the moment it grows a rule gen_state does not have, that property is
gone and the next divergence in gen_state goes unnoticed. The `:`/`#` refusal
therefore sits one layer up, in `check()` at `:172-178`, operating on the token
the `RUN` regex extracted, before any existence test. That is the right seam
because the two layers answer different questions: layer 2 asks "is this string
a bare path at all, or a path plus a locator?" — a question that exists only
because the ledger squeezes a pointer into one free-text cell — and layer 1 asks
"is this repo-relative pointer valid under gen_state's rules?". The ordering is
load-bearing, not cosmetic: `tests/test_check_gate_ledger.py:104-114` creates
files literally named `evidence.txt:12` and `evidence.txt#anchor` in the fixture
repo, so an existence-only check would return 12/12 RUN (Sol 233 SF1's
counterfactual, now killed).

**Would gen_state's kernel pointers ever legitimately need `:` or `#`? No, by
construction.** gen_state does not put locators in the path: `anchor` and
`json_pointer` are separate keys (`gen_state.py:132`, `:142-155`), and the anchor
validator explicitly rejects a leading `#` (`:146-147`). I checked the live
kernel: 399 pointer paths, zero containing `:` or `#`; 21 anchors, all as the
separate key. And `git ls-files | grep -c '[:#]'` is 0 — no tracked file in the
repo would be shut out by the guard. So the guard costs nothing today and cannot
diverge from gen_state's intent, because gen_state's intent is the same rule
expressed structurally rather than syntactically.

## 4. `.github/workflows/gate-ledger.yml`

- **Event types:** `pull_request` with `types: [opened, synchronize, edited,
  reopened, ready_for_review]` (`:32-34`). Not `pull_request_target` —
  confirmed by grep: the string does not appear in the file, nor does
  `secrets`, `workflow_run`, or any `GITHUB_TOKEN` use.
- **Permissions:** `contents: read` only (`:40-41`), pinned by
  `tests/test_check_gate_ledger.py:393`.
- **Does a body edit alone re-run it?** Yes — `edited` fires on title/body/base
  edits with no new commit, which is precisely why this job lives outside
  `ci.yml` (the header comment at `:19-22` is the ONE explanation, and it is
  correct: widening `ci.yml`'s untyped `pull_request` would re-run the ~17-minute
  matrix on every body edit). `concurrency` with `cancel-in-progress`
  (`:36-38`) keeps rapid body edits to one run.
- **Does a branch-only `RUN docs/process_traces/...` resolve?** Yes. The
  checkout is `ref: ${{ github.event.pull_request.head.sha }}` (`:52`), the PR
  head and not the merge ref, so files that exist only on the branch are on
  disk; `--repo-root .` (`:65`) points `_valid_path` at that tree. I reproduced
  this locally: all eight filled rows of #275 cite branch-only trace files and
  all eight resolve against the branch worktree. `fetch-depth: 0` (`:53`) is
  there so a `RUN <sha>` naming an earlier branch commit resolves under `git
  cat-file -e` — note this also means a `RUN <sha>` proves object existence
  only, not membership in this PR (see §1), and that a sha on an unpushed local
  branch passes at the bench and fails in CI, which is the fail-closed
  direction.
- **Fork exploitability:** nothing here is exploitable beyond the ordinary
  `pull_request` model. The body is passed through `env: PR_BODY` and written
  with `printf '%s' "$PR_BODY"` (`:57-61`), never interpolated into the shell
  line, so an attacker-shaped body cannot inject shell. The residual is generic
  to `pull_request`: the job executes `scripts/check_gate_ledger.py` from the
  PR head, i.e. fork-controlled code — but with `contents: read`, no secrets
  exposed to fork PRs, and no write path, so the blast radius is a wasted
  5-minute runner. **Confirmed: it is `pull_request`, not
  `pull_request_target`.**

## 5. Same-signature: was the table an acceptable substitute for the consult?

**Defensible on economics, incomplete as a rule-11 discharge.** The facts:
"regression that does not bite" appeared as luna 227 SF1 (one probe, cured
`55bf9f73`) and Sol 233 SF2 (two probes, cured `8207364c`);
`MAGISTRATE-NOTES.md:27-43` records the magistrate treating Sol 233's
rejection/ignore census (`18-sol-233-fresh-pass.md:228-245`, 22 rows, each
paired with the permissive mutant that would let it through) as the rule-11
consult. Worth noting the magistrate took the STRICTER count: Sol 233 itself
concluded "there is not yet a two-consecutive-round trigger" for this class
(`18-…:250-252`), so the magistrate escalated where the seat said not to. On the
substance, the census is a genuine consult deliverable for the artifact
question — it is exhaustive over the module, it names both inert probes, and it
identifies the single shared cause (the fixture never existed, so
`os.path.isfile` refused before the guard under test could), which is what let
the cure act on the class rather than on two probes: `tests/…:121-126` and
`:300-306` now materialise the absolute-path and URL fixtures at their
join-under-root spellings so the syntax guards are the sole refusers on BOTH
sides of the parity. A separate seat asked "which probes are inert" would have
reproduced that table, and the magistrate is right that spending a seat on it
is waste.

As a contract-lens refuter, here is what a real consult would have added and the
table does not. (a) **Scope.** The census is bounded to
`tests/test_check_gate_ledger.py`. A consult is convened on the *lane*, not the
module, and would have asked whether sibling work landed in the same sessions
carries the same defect — which is not hypothetical: luna 232's cross-lane
sibling census on the dx lane is what caught the `TMPDIR` KeyError that this
module's own 31 green tests hid (`c01c39bb`). Same session, same class of
blindness, found only by looking sideways. (b) **The process half.** Rule 11's
consult exists because a repeated signature is evidence of a STRUCTURAL problem;
the answerable question is not "which probes are inert now" but "why does this
lane keep shipping inert probes, and what changes so there is no round three".
The table answers the first and is silent on the second. The cheap, durable
answer is already implicit in the record and in the standing
mutation-cure-counterfactual rule: **every rejection test must name, in the
fix-round brief, the permissive mutant it kills and the counterfactual input
that makes the fixture reach the guard** — had that been a brief requirement,
neither SF would have shipped, and the census would have been a by-product of
writing the tests rather than an audit finding two rounds later. (c) **The
self-grading edge.** The seat that produced the census is the seat that produced
the finding; the notes discharge that by promising "the delta re-audit of this
bench commit (a different model) verifies the class claim"
(`MAGISTRATE-NOTES.md:39-42`), but at `5f04e147` no such seat exists — the last
sealed report (18) ran over `d14a818d`, and `8207364c` has been verified only by
the magistrate's own bench mutants (F2). So: the disposition is defensible for
what it decided, but it is discharged only in part, and the missing part is a
brief-level rule, not another round.

## 6. The checker against the three live PR bodies

All defect lines are `item N: NOT-RUN` with N ∈ {6, 9, 10, 11, 12}. **No
finding under the stated criterion.** Exact outputs in §Executed evidence:
#272 → items 6, 11, 12; #273 → items 6, 9, 11, 12; #275 → items 9, 10, 11, 12.
All three exit 1, which is the by-construction red the workflow header documents
(`gate-ledger.yml:6-8`). Every filled row in all three bodies resolved, so the
path-form acceptance works against three real branch checkouts, not just
fixtures.

## 7. What I would not merge as-is

Nothing in the code. `scripts/check_gate_ledger.py`, `tests/`, the template, the
workflow and the one-line `docs/orchestration.md` pointer are merge-ready as far
as this lens reaches: the splitter is the ruled rule, the two-layer path
arrangement is coherent, the workflow targets the right object with minimum
permissions, and 31 tests pass both with and without `TMPDIR`. Two things I
would fix in the ledger and the trace before the merge commit (F1, F2), and one
brief-level rule I would adopt before the next lane (F3).

---

## Findings

### SHOULD-FIX 1 — item 6 of #275's ledger cites a review of the wrong head
`.github/pull_request_template.md:14` (row text "on the near-final head") vs.
the live body's evidence `RUN
docs/process_traces/2026-09-02-t26-item2/13b-opus-207b-counter-review.md`. 13b
reviewed the cold-gate head; `5ed6f1e9`, `55bf9f73`, `c01c39bb` and `8207364c`
all post-date it — including the entire ruled cure the row exists to cover. The
body discloses this in plain text, so it is not a concealed claim, and the
checker passes it because it validates resolution, not aboutness (§1).
**Counterfactual:** merging as-is leaves a permanent record in which gate item 6
is marked RUN against a review that could not have seen the code it certifies —
the exact defect the ledger is supposed to make impossible to leave implicit.
**Cure:** commit this report into `docs/process_traces/2026-09-02-t26-item2/`
and repoint row 6 at it.

### SHOULD-FIX 2 — the same-signature section states a cross-model verification that does not exist at 5f04e147
`docs/process_traces/2026-09-02-t26-item2/MAGISTRATE-NOTES.md:39-42`: "the delta
re-audit of this bench commit (a different model) verifies the class claim, not
just the two edits." Written in the present indicative among completed-work
rows. No seat file post-dates `18-sol-233-fresh-pass.md`, whose `head_start` /
`head_end` are `d14a818d` (`18-…:9-11`); `8207364c`'s only verification is the
magistrate's own bench mutant run recorded in the same table row
(`MAGISTRATE-NOTES.md:24`). The ledger itself is honest — item 10 is `NOT-RUN` —
but the trace prose is ahead of the record. **Counterfactual:** a later reader
reconstructing why the rule-11 substitution was acceptable reads this sentence
as a discharged condition and does not notice that the condition is still open.
**Cure:** tense it as a requirement ("…is discharged by gate item 10, which is
open") or cite the seat once it exists.

### SHOULD-FIX 3 — the rule-11 substitution discharges the artifact half of the class and not the process half
`MAGISTRATE-NOTES.md:27-43` against `18-sol-233-fresh-pass.md:228-245`. The
census is exhaustive over this module and correctly identifies the shared cause,
but it is module-scoped and backward-looking; nothing in the record changes how
the NEXT fix-round brief specifies a regression. **Counterfactual:** a third
inert probe surfaces on a later lane, because the only thing standing between
the lane and that outcome is a per-round audit that has now caught it twice
after the fact — and `c01c39bb` already shows that this module's own green suite
does not see its own blind spots (a sibling-lane census did). **Cure (one line
in the fix-round brief template, no seat spend):** every dictated rejection test
names the permissive mutant it must kill AND the counterfactual input that makes
the fixture reach the guard under test; the fix-round report pastes the mutant
run. That is the standing mutation-cure-counterfactual rule applied one level
earlier, at brief time instead of audit time.

### NIT 1 — the "first contiguous pipe block" table boundary diverges from GitHub in two verified ways
`scripts/check_gate_ledger.py:76-90`. Verified live via `gh api -X POST
/markdown -f mode=gfm`: (i) a pipe-containing paragraph line with no delimiter
row is a `<p>` on GitHub but is taken as the table start here — a body whose
ledger preamble contains one `|` produces 25 defect lines, none naming the
cause; (ii) a non-pipe line inside a table is a one-cell row on GitHub and the
table continues, while here it ends the table and the following rows are
reported "outside". Both fail closed, and the cold ruling deferred this class
deliberately (`16-…:107-113`). **Counterfactual:** an author adds a sentence with
a pipe under the ledger heading, gets 25 lines of unrelated defects, and burns a
round diagnosing it. **Cure:** anchor `table_started` on the delimiter row
(`| --- | --- | --- |`, already recognised at `:96`) rather than on the first
pipe line, and refuse a ledger section with no delimiter row with one named
message. This models LESS of GitHub, not more — GFM requires the delimiter row.
Re-grade to SHOULD-FIX if the job is ever promoted to a required check
(ED-BRANCH-PROTECTION-E1-01), since then a false refusal blocks merges.

### NIT 2 — the apex-gate answer understates the workflow's trigger list
`MAGISTRATE-NOTES.md:83` says "Fires on `opened, synchronize, edited,
ready_for_review`"; the workflow has five types, including `reopened`
(`gate-ledger.yml:34`, pinned by `tests/test_check_gate_ledger.py:391`).
**Counterfactual:** trivial — a reader trusting the notes over the file thinks a
reopened PR is unchecked. **Cure:** add `reopened` to the sentence.

---

## Executed evidence

All commands run with `TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp-opus-c`.

```text
$ cd /Users/edr/code/JouleWise-wt-t26-c && git log --oneline main...HEAD
5f04e147 t26-item2 trace: name the SF1/SF2 bench commit
8207364c gate ledger (Sol 233 SF1/SF2/SF3): ':N'/'#anchor' refused as syntax before the existence check ...
c01c39bb gate-ledger tests: TMPDIR optional ...
d14a818d t26-item2 trace: cold gate + round 3 + delta 3 recorded ...
55bf9f73 gate ledger: F-9 regression bites (luna 227 SF1) ...
5ed6f1e9 T26 item 2 gate ledger: fix round 3 (ledger cold ruling L2/L3 + Opus 207b S1-S5/N1-N9)
exit 0   (31 files changed, 3892 insertions(+), 1 deletion(-))
```

```text
$ python3 -m unittest tests.test_check_gate_ledger
...............................
Ran 31 tests in 1.594s
OK
exit 0
```

```text
$ env -u TMPDIR python3 -m unittest tests.test_check_gate_ledger
Ran 31 tests in 1.647s
OK
exit 0        # c01c39bb's CI condition reproduced
```

```text
$ gh pr view 272 --json headRefOid -q .headRefOid  -> 73f7fcc22511ff6d2e6aaddbd66fabf81edd1328
$ gh pr view 273 --json headRefOid -q .headRefOid  -> 10845c14e7ef77c6f46013b18acc8d8569900d8a
$ gh pr view 275 --json headRefOid -q .headRefOid  -> 5f04e147eee440dc6e386e412da8601ba8aa32d3
exit 0
```

```text
$ gh pr view 272 --json body -q .body > $TMPDIR/body-272.md
$ python3 scripts/check_gate_ledger.py --body-file $TMPDIR/body-272.md \
    --head-sha 73f7fcc22511ff6d2e6aaddbd66fabf81edd1328 --repo-root /Users/edr/code/JouleWise-wt-dx
gate-ledger: item 6: NOT-RUN
gate-ledger: item 11: NOT-RUN
gate-ledger: item 12: NOT-RUN
exit 1
```

```text
$ gh pr view 273 --json body -q .body > $TMPDIR/body-273.md
$ python3 scripts/check_gate_ledger.py --body-file $TMPDIR/body-273.md \
    --head-sha 10845c14e7ef77c6f46013b18acc8d8569900d8a --repo-root /Users/edr/code/JouleWise-wt-t26-a
gate-ledger: item 6: NOT-RUN
gate-ledger: item 9: NOT-RUN
gate-ledger: item 11: NOT-RUN
gate-ledger: item 12: NOT-RUN
exit 1
```

```text
$ gh pr view 275 --json body -q .body > $TMPDIR/body-275.md
$ python3 scripts/check_gate_ledger.py --body-file $TMPDIR/body-275.md \
    --head-sha 5f04e147eee440dc6e386e412da8601ba8aa32d3 --repo-root /Users/edr/code/JouleWise-wt-t26-c
gate-ledger: item 9: NOT-RUN
gate-ledger: item 10: NOT-RUN
gate-ledger: item 11: NOT-RUN
gate-ledger: item 12: NOT-RUN
exit 1
```

```text
# fenced template before the real (filled) section — fail-closed shape asserted at
# tests/test_check_gate_ledger.py:250-255; exact output confirms the :66-67 comment
$ { echo '```markdown'; cat .github/pull_request_template.md; echo '```'; echo; cat $TMPDIR/body-275.md; } > $TMPDIR/fenced.md
$ python3 scripts/check_gate_ledger.py --body-file $TMPDIR/fenced.md --head-sha 5f04e147... --repo-root .
gate-ledger: item 1: NOT-RUN
... (twelve lines, items 1-12)
gate-ledger: item 12: NOT-RUN
exit 1
```

```text
# NIT 1 (i): a pipe in the ledger preamble
$ python3 scripts/check_gate_ledger.py --body-file $TMPDIR/prosepipe.md --head-sha 5f04e147... --repo-root .
gate-ledger: unrecognised ledger row: 'Filled by the magistrate'
gate-ledger: item 1: ledger row outside the ledger table
... (items 1-12 "outside the ledger table")
gate-ledger: item 1: missing
... (items 1-12 "missing")
exit 1        # 25 defect lines, none naming the cause
```

```text
# NIT 1: GitHub's own renderer on the same shapes
$ gh api -X POST /markdown -f mode=gfm -f context=mpmdw/JouleWise -f "text=$(cat probe2.md)"
<p dir="auto">Filled by the magistrate | 2026-09-02.</p>       # NOT a table (no delimiter row)
<table ...><thead>...#/Gate item/Evidence...</thead><tbody>
<tr><td>1</td><td>a</td><td>RUN x</td></tr>
<tr><td>trailing prose without a pipe</td><td></td><td></td></tr>   # one-cell ROW, table continues
<tr><td>2</td><td>b</td><td>RUN y</td></tr>
</tbody></table>
exit 0
```

```text
# §3: gen_state parity surface and whether ':'/'#' are ever legitimate
$ git ls-files | grep -c '[:#]'
0
$ python3 -c "...json/regex over docs/process/state_kernel.json..."
pointer paths: 399
with : or #: []
anchor keys: 21
sample anchors: ['d-070-architectural-axes-...', '4-work-program-post-audit-clearance-streams', ...]
exit 0
$ sed -n '136,140p' scripts/gen_state.py
    if path.startswith("/") or path.startswith("~") or ".." in path.split("/") or "://" in path:
        fail(...)
    target = os.path.join(ROOT, *path.split("/"))
    if not os.path.isfile(target):
        fail(...)
# identical to scripts/check_gate_ledger.py:117-120 modulo the fail/return shape
```

```text
# §4: fork-safety surface
$ grep -n "pull_request_target\|permissions\|secrets\|workflow_run\|GITHUB_TOKEN" .github/workflows/gate-ledger.yml
40:permissions:
exit 0        # only 'permissions' matches; no pull_request_target, no secrets, no token use
$ grep -rln "gate.ledger\|check_gate_ledger" .github/workflows/
.github/workflows/gate-ledger.yml        # no other workflow invokes the checker
```

```text
$ git diff main...HEAD -- docs/orchestration.md
+   green. Gate ledger: twelve-row PR-body table (`.github/pull_request_template.md`), checked by
+   `scripts/check_gate_ledger.py` in the advisory `gate-ledger` workflow — see D-170. **Final-head rule:** ...
exit 0        # pointer only, no doctrine copy
```

VERDICT: SHOULD-FIX 3
