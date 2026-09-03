ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["joulewise/arm_readiness.py", "tests/test_arm_readiness.py", "tests/test_arm_readiness_evidence_t0.py", "tests/test_t0_rehearsal.py", "tests/test_arm_readiness_integration.py", "docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md", "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 1 — T26 item 3, 600 s liveness conjunct (branch feat/2026-09-02-t26-liveness @ e40e7502)

LINKED WORKTREE `/Users/edr/code/JouleWise-wt-t26-b`. Do NOT commit/rebase;
never canonical `unittest discover`; the magistrate commits. Never run a nap,
arm, night-custody or `[QUIET-MAC]` action. `docs/process/state_kernel.json`,
`docs/decision_log.md`, and
`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md` are
OUT of scope — read them; where a closure below needs text in one of them,
write the exact proposed text to `$TMPDIR/bench-<name>.md` and name it in the
report; the magistrate applies it at the bench.
Tests: `python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration`
(166 + 9 today, ~4 min).

AUTHORITY: the T26 cold-gate ruling
`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
(item 3: the 5 s bound is STRUCK, the 600 s liveness bound is RULED — the
NUMBER 600 s and the inclusive `<=` are ruled values; this round moves
neither). Three refuters on the landing at e40e7502 (luna 211 contract lens, terra
212 execution lens, Sol 213 physics lens; envelopes at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/21{1,2,3}-*.md`,
read-only — the operative findings are dictated below; open the envelopes
only if a closure needs a detail not given here).

## Dictated closures

F-1 (terra F1/F2 — the exact boundary is untested; M2 `cap−1 ns` and M9
`<=`→`<` SURVIVED). At EACH of the three sites (arm `test_arm_readiness`,
issuance `test_arm_readiness_evidence_t0`, rehearsal `test_t0_rehearsal`) add
the PASS case at exactly `600_000_000_000` ns elapsed (R1 finish →
validity origin), mirroring the existing `+1 ns` refuse and `−1 ns` pass
tests. Name them `..._passes_at_exactly_600s`. Re-run M2 and M9 yourself and
report KILLED with the test names.

F-2 (terra F3 — integration census blind to the T-0 author reason code;
M8 survived `tests.test_arm_readiness_integration` 9/9). Extend the census
in `tests/test_arm_readiness_integration.py` (`:585-…`) so the
`evidence_author_t0_*` vocabulary (Vocabulary B in
`reason-code-coverage-delta.md §1.2`) is checked the same way `readiness_*`
is: every `"evidence_author_t0_[a-z0-9_]+"` literal produced in
`joulewise/arm_readiness_evidence.py` (and `arm_readiness_evidence_t0.py` if
it produces any) must be a member of the registered vocabulary, and a
mutant string (terra M8: `evidence_author_t0_predicate_refused_mutant`) must
fail THIS test file, not only the direct issuance test. Say where the
Vocabulary-B registry lives (the same `refusal_vocabulary` list or another)
and cite it.

F-3 (luna F5 / G2 — constants coupled by comment only). Add one test
asserting `arm_readiness._T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS ==
arm_readiness_evidence_t0._MIN_IDLE_NS`, with the provenance sentence
(11 × 45 s + 105 s) in its docstring. Do not merge the two constants (the
modules import in one direction only — say which — and the ruling names the
liveness constant by its own name).

F-4 (luna F1 — live struck text in the prior T-0 ruling). In
`MAGISTRATE-RULING-T0-UNATTENDED.md` insert, immediately after the sentence
at `:78-79` ("R1-completion→validity-origin ≤5 s (oldest participating R1
result ≤35 s old at issuance)"), one bracketed marker line:
`[STRUCK 2026-09-02 — T26 cold gate item 3 (COLD-GATE-RULING.md) replaces the ≤5 s / ≤35 s relation with the ordinary-clock 600 s liveness bound; see the dated addendum at the end of this file.]`
and append a dated `## Addendum 2026-09-02 — item 3 liveness bound (T26 cold gate)`
section stating: what was struck (quote it), what replaces it (the exact
conjunct: `0 <= validity_origin_monotonic_ns − r1_batch_finished_monotonic_ns <= 600_000_000_000`,
ordinary `CLOCK_MONOTONIC`, production site `joulewise/arm_readiness.py:6485`
at e40e7502), and that the 6 h horizon, the [600 s, 3600 s] R0 span, the
30 s R1 batch bound and the standing fence are UNCHANGED. Nothing else in the
ruling file is edited (rulings are amended by addendum, never in place).

F-5 (luna F2 — §6.3 still presents the 5 s contract as live). In
`reason-code-coverage-delta.md`: (a) retitle `### 6.3` from
`COLD-GATE-PENDING — …` to `RESOLVED 2026-09-02 (was COLD-GATE-PENDING) — …`;
(b) insert one `> SUPERSEDED …` blockquote banner at the top of the old
options/interim-disposition block (`:990-1148`) naming the resolved paragraph
(`:1150-1160`) as the only live text; (c) at RF-17 and the numeric relation at
`:522`, append a bracketed `[superseded 2026-09-02 → 600 s liveness, §6.3]`
marker to the line (do not delete the old text — it is the historical
record). Verify by `grep -n '5 s\|≤5\|<=5\|35 s' <file>` that every remaining
hit is either inside a superseded/marked block or is a quote in the resolved
paragraph; paste the grep with your classification.

F-6 (Sol PHYS-1 — 600 s is not a proven successful-path bound). Do NOT move
the number. (a) Compute the worst-case successful-path elapsed from the code
as Sol did (11 × 45 s probe timeouts + 11 × 20 s Git timeouts + untimed
work) — re-derive it yourself from `arm_readiness_evidence_t0.py` and
`identity_pins.py`, cite each site, and state the number. (b) Search the
repo (NOT `runs*/` contents beyond listing; never the night custody root)
for any retained T-0 rehearsal receipt or process trace carrying BOTH an R1
batch finish stamp and a validity origin (grep for
`r1_batch_finished_monotonic` / `validity_origin`) and, for each hit,
compute the observed elapsed; report the maximum, or "no retained receipt
carries both stamps" if so. (c) Add a `### 6.3.1 Limitation — worst-case
successful path vs the 600 s bound` subsection after the resolved paragraph
with (a) and (b), and the sentence: "A refusal on this conjunct in a real
night is a fail-closed false refusal, not a hang, whenever (b)'s observed
elapsed approaches 600 s; the bound is a ruled value and moves only by cold
gate." Write to `$TMPDIR/bench-kernel-row.md` a proposed kernel row
`T0-LIVENESS-BOUND-EMPIRICAL-01` (fill the existing row shape from any
`*-01` row in `docs/process/state_kernel.json`) whose acceptance is: N ≥ 3
real rehearsal receipts with measured elapsed, all < 600 s by a stated
margin, or a cold-gate re-ruling of the number.

F-7 (Sol PHYS-2 — the drift arithmetic omits the admitted initial bound).
Write to `$TMPDIR/bench-coldgate-addendum.md` a dated addendum for
`COLD-GATE-RULING.md` (the magistrate appends it): the ruling's 3.68 ppm ×
horizon calculation assumes zero initial error; with the admitted
`reference_bound_seconds ≤ 0.5 s` the guaranteed envelope is 0.5 s +
3.68 ppm × age (Sol's numbers: 0.5057 s at 1830 s; 0.5808 s under the
standalone 6 h + 600 s + 30 s envelope); this does not justify restoring 5 s
and moves no number; it corrects the stated rationale. Also add one
sentence to the §6.3 resolved paragraph pointing to that addendum.

F-8 (production comment). `joulewise/arm_readiness.py:6478-6485`: the
comment must name the ruled provenance in one line and point to §6.3 — no
other production change in this round.

## Mutation check (report each: KILLED by <test> / SURVIVED)

M2 `600_000_000_000 → 599_999_999_999` → KILLED by the three exactly-600 tests.
M9 `<=` → `<` at `:6485` → KILLED by the same.
M8 `evidence_author_t0_predicate_refused` → `…_mutant` in
`arm_readiness_evidence.py` → KILLED by `tests.test_arm_readiness_integration`
(name the test) AND by the direct issuance test.
M10 change `_MIN_IDLE_NS` by 1 → KILLED by F-3.

## ACCEPTANCE

- the five-module test command tail (expect ≥ 180 tests OK, skipped=7).
- `python3 -m unittest tests.test_docs_freshness` tail.
- the F-5 grep with classification.
- `git status --porcelain` shows only in-scope files; `git diff --stat`.
- Same-signature statement: first fix round on this landing; classify each
  closure as test-gap (F-1/F-2/F-3), documentation-consistency (F-4/F-5),
  or registered-limitation (F-6/F-7); state that no ruled number moved.
- `## Clause map`: one row per closure F-1…F-8 — production or doc
  `file:line`, biting test `file:line` (or "doc — verified by grep"),
  counterfactual.
