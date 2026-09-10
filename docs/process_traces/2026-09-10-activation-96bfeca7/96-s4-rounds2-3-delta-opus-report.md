# 96 — S4 fix rounds 2 & 3, DELTA RE-AUDIT (execution lens)

Refuter: Opus 5 (1M), execution lens. Date: 2026-09-10.
Tree: `/Users/edr/code/JouleWise-wt-s4-issuer-prepare` @ `410229f1` (rounds `a3ae7bf8` -> `6e9d2a63` -> `410229f1`).
Scope: `git diff a3ae7bf8 410229f1` — `scripts/issue_calibration_acceptance_generation.py`,
`tests/test_issue_calibration_acceptance_generation.py`, `tests/fixtures/epoch_bootstrap/build.py`.
Authority text: `git -C /Users/edr/code/JouleWise-wt-s6-docs-prereg show HEAD:configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
(sha256 `9a5bfcd6770e0da9e8bd9e93645aa496becc135ec50e0f8bf96044c4613745c7`, 222 lines).

## VERDICT: should_fix (no blocker)

Every substantive claim in the seat's unverified "Fix round 2"/"Fix round 3" sections that I
tested is TRUE: the blindness gate exists, is isolated, precedes the ledger refusal, and leaks
nothing; SF-2's n=17-only departure is exact; SF-4 refuses rather than drops; SF-3 stores a
repo-relative `source_directory` and refuses outside-root custody; DF-1's two pure envelope
functions are used at both call sites with no duplicate inline arithmetic; the `check` output is
byte-identical to `a3ae7bf8` when no registration is named; SF-8's licence sentence is inside
`derivation_sha256` and outside `derivation_input_sha256`.

Two cuts SURVIVED and there are four disagreements with the binding pre-registration text.
None of them can put a wrong number into an issued artifact; all of them are cheap.

## Cut table (isolation rule; every cut restored byte-for-byte, `PYTHONDONTWRITEBYTECODE=1`)

| # | Cut | Test run | Result |
|---|-----|----------|--------|
| C1 | delete the `refuse_open_registration(snapshot, session_ids)` call | `test_an_open_registration_session_refuses_before_anything_is_computed` | KILLED (failures=1) |
| C2 | `TERMINAL_SESSION_STATES = frozenset({"finalized"})` (drop `"aborted"`) | full module (172 tests) | **SURVIVED — rc=0 OK** |
| C3 | `TERMINAL_SESSION_STATES = frozenset({"aborted"})` (drop `"finalized"`) | full module | KILLED (22 failures, 13 errors) |
| C4 | move the blindness call AFTER `if snapshot.refusal_reasons:` (the masking) | `test_an_open_registration_session_refuses...` | KILLED (failures=1) |
| C5 | SF-2: `if minimum != RULED_ALTERNATIVE_CORPUS_SIZE:` -> `if False:` | `test_only_seventeen_is_a_ruled_alternative_floor` | KILLED |
| C6 | SF-4: `if unresolved:` (prepare path) -> `if False:` | `test_an_unresolved_prefix_row_refuses` | KILLED |
| C7 | SF-3: `_repo_relative_custody` returns `custody_locator` unchanged | `test_member_source_directory_is_repo_relative_and_re_resolves`, `test_custody_outside_the_repository_refuses` | KILLED (both) |
| C8 | `envelope_screen` -> `quantized_range` | `test_the_ceiling_takes_whichever_operand_is_larger` | KILLED |
| C9 | `envelope_screen` -> `floor` | same | KILLED |
| C10 | `envelope_ceiling` -> `predecessor_ceiling` | same | KILLED (subTest `own Q99 wins`) |
| C11 | `envelope_ceiling` -> `own_q99` | same | KILLED (subTest `predecessor wins`) |
| C12 | dry run: `if terminal:` -> `if True:` (bundle read outside the terminal gate) | the 3 dry-run tests + the blindness test | **SURVIVED — rc=0 OK** |
| C13 | SF-8: delete `"licence": CANDIDATE_LICENCE,` | `test_the_candidate_states_its_licence_in_words`, `test_only_the_candidate_label_stops_the_candidate_authenticating` | KILLED (1 error + 1 failure) |

11 of 13 killed. Restore verified: `scripts/issue_calibration_acceptance_generation.py` sha256
`e4e0260d30ac459efe5f2d72c3dbbe56431cdd724d82671040a0497bb2acd602` before and after every cut;
`git status --porcelain` empty at the end.

## 1. BLINDNESS — the actual CLI output

`prepare-candidate` on the 6-of-20 open-session fixture (`fill_slots=6`), stdout+stderr verbatim:

```
rc=3
--- STDOUT ---
REFUSED: registration: session derivation-night-1 is 'open', not terminal; nothing is computed or reported before every session of the registration is terminal (pre-registration, Blindness)
--- STDERR ---
(empty)
--- outfile ---
ls: /tmp/s4delta/open6_candidate.json: No such file or directory
```

Grep for any decimal lexeme / `screen` / `ceiling` / `n=` / any count over that output: the ONLY
match is the substring `1` inside the session name `derivation-night-1`. No value, no statistic,
no count, no `screen`, no `ceiling`. Nothing written.

Dry run on the SAME open fixture (`check --session-ids derivation-night-1`), verbatim tail:

```
Registration dry run (no measured value is reported)
derivation-night-1: kind=derivation state=open terminal=NO declared_slots=20 rows=0 valid=0 excluded=none
prefix pending or unresolved rows: none
registration would be admissible for prepare-candidate: NO
  blocker: session derivation-night-1 is 'open', not terminal
```

No leak. But see finding E-1: `rows=0 valid=0` is wrong-by-omission — six slots ARE finalized.

Dry run on the terminal (20-of-20) fixture:

```
derivation-night-1: kind=derivation state=finalized terminal=yes declared_slots=20 rows=20 valid=20 excluded=none
prefix pending or unresolved rows: none
registration would be admissible for prepare-candidate: YES
  retained valid rows in the registration: 20
```

## Findings

### E-1 (should_fix) — the dry run reports `rows=0 valid=0` mid-campaign, which is the only time it is useful

`registration_dry_run` derives its filled/valid counts from `snapshot.observations`. For an OPEN
session the ledger loader publishes NO observations at all — verified directly:

```
refusals: ('calibration_ledger_bracket_session_open',)
n observations: 0
state: open  declared: 20
session.finalized_slots -> 6 entries (d01..d06), next_slot = 'd07'
```

So the mid-campaign dry run prints `rows=0 valid=0` after six captured nights' slots. The binding
pre-registration says the dry run reports "how many slots are declared and **how many are filled**"
and concludes "A mid-campaign look **can answer whether the campaign is on schedule**". It cannot:
the number it prints is 0 whether one slot or eleven are in the ledger, and a reader who does not
know the loader's open-session behaviour will read `rows=0` as "nothing captured".
Fix is one line: take the filled count from `len(session.finalized_slots)` (print the COUNT only —
those objects carry `exact_bound_lexeme_s`, so nothing but `len()` may be touched), and keep
`rows`/`valid` for the terminal case. Pin it with the existing `fill_slots=6` fixture asserting
`filled=6` plus `assert_no_measured_value_leaked`.

### E-2 (should_fix) — the `"aborted"` arm of `TERMINAL_SESSION_STATES` is unpinned (C2 survived)

Collapsing the terminal set to `{"finalized"}` breaks no test in the module. The pre-registration
defines terminal as "its last declared slot is final **or the session was aborted**", and the
Sample clause plans for exactly that: "A slot the window cannot reach is recorded unused by the
session abort (reason `window_exhausted`)". Under the cut, a night that legitimately ran short
would refuse issuance forever, and nothing would catch it. Add a fixture with an aborted session
(or reuse `build_derivation_ledger` with an abort) asserting `prepare-candidate` ADMITS it, and a
direct `refuse_open_registration` case with `state="aborted"` that must not raise. (Note
`test_the_blindness_gate_is_isolated_from_the_ledger_refusal` iterates
`for state in issuer.TERMINAL_SESSION_STATES`, so it can never detect a member being removed —
iterating the constant under test is exactly the tautology the isolation rule forbids.)

### E-3 (should_fix) — `bounds_origin` states something the binding pre-registration contradicts, and the test pins the false wording

Emitted, inside `derivation_input_sha256`:

> "issuer-declared bounds, recorded here in the candidate: the pre-registration requires a proof
> for the realized df and **states no numeric bound**, so these two are the issuer's..."

The S6 round-5 text states both numbers explicitly ("with absolute residual at most 1e-30",
"must agree to at least 30 significant decimal digits") and then says: "Those two bounds — residual
at most 1e-30, agreement at least 30 significant digits — are the ISSUER'S DECLARED bounds, not a
ratified constant, and they are stated here so the authority-side record carries them". The claim
"states no numeric bound" is therefore false against the text that will bind, and it is sealed into
the candidate's `derivation_input_sha256`. `test_the_quantile_proof_records_where_its_bounds_came_from`
asserts `assertIn("states no numeric bound", ...)`, so the defect is pinned in place.
Fix: reword to "the pre-registration records these same two bounds AS the issuer's declared bounds
(Quantile proof, final paragraph), not as a ratified constant" and re-point the assertion.

### E-4 (should_fix, low cost) — the dry run's exit code is permanently masked

`check` ends `return 3 if errors or mismatches else dry_run_code`. On the machine this tool exists
for, the epoch watch ALWAYS mismatches (the active r6 artifact binds `25F84`; the machine is
`25G83` — that is the whole reason for the registration). Measured: on the fully admissible
20-of-20 fixture, `check --session-ids ...` exits **3**, not 0. So the dry run's verdict is
readable only by parsing stdout; an operator or runbook branching on the exit code can never see
"admissible". Either give the dry run its own exit code channel, or state in `--help` that the
exit code reports the epoch watch only. The existing test asserts the code from
`registration_dry_run` directly, never through `check`, so this is untested at the CLI boundary.

### E-5 (nit) — the `if terminal:` gate on the bundle read is unfalsifiable (C12 survived)

Turning the gate into `if True:` kills nothing, and cannot: for an open session
`snapshot.observations` is empty (E-1), so `valid` is empty and the loop body is unreachable. The
gate is honest defence-in-depth but no test can distinguish it. Either note that in the comment
(the current comment claims a property no test holds) or drop the gate as dead code once E-1's
`finalized_slots` route lands — at which point the gate becomes reachable and MUST be pinned.

### E-6 (nit) — help text: missing flag help, and first-use failures

`prepare-candidate --help` gives NO help string for `--ledger`, `--head-pin`, `--repo-root`,
`--d125-ruling`, `--ed-ruling`, `--minimum-corpus-size`, `--epoch-catalog-id`, `--acceptance-id`,
`--out`. `--ed-ruling` and `--d125-ruling` are the two flags that carry written rulings, and
`--out` is the one the module docstring calls out as safety-bearing; an operator reading the
subcommand help learns nothing about any of them (notably that `--ed-ruling` licenses n = 17 and
no other number).

First-use test over the module docstring (which `--help` prints in full) — each is a term of art
or a verb doing technical work, used before being built or glossed: "epoch" / "identity epoch";
"trigger observation"; "D-102 prior-artifact rule"; "prior-set prefix"; "rows are `valid`"
(ledger disposition); "D-138 transaction"; "cold science gate"; "Decimal statistics";
"D-125 envelope **operatives**"; "bracket screen"; "budget ceiling"; "level screen";
"quantile proof"; "degrees of freedom". A reader cannot replicate the refusal list from this text.
One sentence each for epoch / bracket screen / budget ceiling / level screen / operatives, plus a
pointer to the pre-registration's glossary for the rest, clears it.

### E-7 (nit) — the dry run prints beyond the pre-registration's enumerated list

The text says the dry run "reports **only** the named sessions' kinds and states, how many slots
are declared and how many are filled, and how many observations are excluded under each named
mechanism". The code additionally prints a `valid=` count, the attempt IDs of pending/unresolved
prefix rows, and (when admissible) `retained valid rows in the registration: N`. None is a measured
value and none violates blindness in substance, but "reports only" is exhaustive as written. Either
widen the pre-registration clause to name counts of dispositions and unresolved attempt ids, or
trim the output. Flagging it because the same sentence is what an authority-side reader will use to
audit the tool.

## Pre-registration vs code — disagreement list

| Prereg clause | Code | Disagreement |
|---|---|---|
| Blindness: "prepare-candidate refuses ... and names the session it found open" | `refuse_open_registration`, before any row read | AGREES (C1/C4 killed; output pasted above) |
| Blindness: terminal = last slot final **or aborted** | `frozenset({"finalized","aborted"})` | agrees in code; the `aborted` arm is UNPINNED (E-2) |
| Blindness: dry run reports declared and **filled** slots | prints `declared_slots` and `rows`/`valid` from `snapshot.observations` | **E-1** — filled is always 0 mid-campaign |
| Blindness: "reports only ..." (exhaustive) | also prints `valid=`, unresolved attempt ids, `retained` | **E-7** |
| Stopping: n >= 19; Ed may rule n = 17; nothing below 19 without it | 19 default, 17 only with `--ed-ruling`, all else refused | AGREES exactly (matrix below) |
| Quantile proof: bounds 1e-30 / 30 digits are the ISSUER'S DECLARED bounds, stated in the text | `bounds_origin` says the prereg "states no numeric bound" | **E-3** |
| Quantile proof: record quantiles at 20 dp, per-probability residuals, agreement digits, both bounds, method string, precision | all seven present (`quantiles`, `forward_residuals`, `closed_form_agreement_digits`, `forward_residual_bound`, `closed_form_agreement_bound`, `closed_form_method`, `precision`) | AGREES |
| Membership: valid disposition + stored anchor-v3 resolves from authenticated bytes, no re-derivation | `derivation_corpus.selection` now states exactly that | AGREES (round-2 wording fix stands) |
| Prospective use: pending/unresolved attempt in the prefix REFUSES | refusal, not drop | AGREES (C6 killed) |
| D-125: S = max(quantized range, 0.010818); C = max(predecessor ceiling, Q99); refuse when S >= C | `envelope_screen` / `envelope_ceiling`, `if not screen < ceiling` | AGREES (C8–C11 killed) |
| — | `check` exit code | **E-4**, not a prereg clause but a CLI-contract defect |

## 2. SF-2 corpus-size floor matrix (CLI, 20-member fixture)

| `--minimum-corpus-size` | with `--ed-ruling` | without |
|---|---|---|
| 16 | rc=3 "is not a ruled floor" | rc=3 "is not a ruled floor" |
| 17 | **rc=0, candidate emitted** | rc=3 "requires --ed-ruling" |
| 18 | rc=3 "is not a ruled floor" | rc=3 "is not a ruled floor" |
| 20 | rc=3 "is not a ruled floor" | rc=3 "is not a ruled floor" |
| default (19) | — | rc=0, candidate emitted |

## 3–5. SF-4 / SF-3 / DF-1

SF-4: `test_an_unresolved_prefix_row_refuses` kills C6; the refusal names the mechanism
("prior set holds pending or unresolved attempts: ...").
SF-3: C7 kills two tests; every emitted `source_directory` is relative, `repo_root / it` resolves to
the member's directory, and r6's own stored form is likewise relative (asserted in-test).
DF-1: all four operand collapses are killed (C8–C11); `main`'s only screen/ceiling arithmetic is the
two calls at `:1116` and `:1122` — `grep -n "envelope_screen\|envelope_ceiling"` shows the two
definitions and exactly two call sites, no duplicate inline `max(...)`.

## 6. Dry-run byte identity

`check` WITHOUT `--session-ids`, same fixture, run in both trees (`git archive a3ae7bf8` to
`/tmp/s4delta/base`):

```
new rc=3 / old rc=3 / BYTE-IDENTICAL
6d2541e4fb59edb0d5075f4fd2bb6e7968bc91512cba7d191c6db87c038825a6  check_new.out
6d2541e4fb59edb0d5075f4fd2bb6e7968bc91512cba7d191c6db87c038825a6  check_old.out
```

With `--session-ids`: kinds/states/counts present (pastes above). Exit 0 when admissible is NOT
observable through `check` on this machine — see E-4. C12 (bundle read outside the terminal gate)
survived — see E-5.

## 7. SF-8 licence

`issuance.licence` is emitted verbatim as `CANDIDATE_LICENCE`; C13 kills both
`test_the_candidate_states_its_licence_in_words` (error) and
`test_only_the_candidate_label_stops_the_candidate_authenticating` (failure), i.e. the label-only
authentication test still ADMITS with the key present and notices its removal. In-test:
mutating `issuance.licence` changes `derivation_sha256` and does NOT change
`derivation_input_sha256`; `load_calibration_acceptance_bound(out)` returns `None`.

## 9. Full module + key-set delta

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_issue_calibration_acceptance_generation tests.test_calibration_bracketing
Ran 172 tests in 65.996s
OK (skipped=1)
```

Key-set diff of the emitted candidate, `a3ae7bf8` tree vs `410229f1` tree, same 20-member fixture:

```
ADDED:   /decimal_derivation/quantile_proof/bounds_origin
         /derivation_notes/predecessor/derivation_sha256
         /derivation_notes/predecessor/file_sha256
         /issuance/licence
REMOVED: (none)
```

Additions only, and exactly the four rounds 2/3 promised. (Value-level changes, not key-level:
`derivation_corpus.selection` wording and every member's `source_directory` becoming relative.)

## Hashes

| file | sha256 (unchanged before/after every cut) |
|---|---|
| `scripts/issue_calibration_acceptance_generation.py` | `e4e0260d30ac459efe5f2d72c3dbbe56431cdd724d82671040a0497bb2acd602` |
| `tests/test_issue_calibration_acceptance_generation.py` | `966ebfe78ca23ecd03837115d130c603702c9d2ff2296db91c6019960fc5b2be` |
| `tests/fixtures/epoch_bootstrap/build.py` | `c483361285e1348f3ab5344d87bd71f63aa3fe7b90866eff3c7bbaa07ada4427` |
| S6 pre-registration text | `9a5bfcd6770e0da9e8bd9e93645aa496becc135ec50e0f8bf96044c4613745c7` |

`git status --porcelain` empty; no git state changed; no live capture; nothing written to
`configs/calibration/`; canonical `/Users/edr/code/JouleWise` untouched.

## Reproducing commands

```bash
W=/Users/edr/code/JouleWise-wt-s4-issuer-prepare
# fixtures (persistent, /tmp only)
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/mkfix.py /tmp/s4delta/fx   # open6 (fill_slots=6), wide (20)
# cut batteries (apply -> targeted test -> restore -> sha assert)
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cut.py     # C1,C4..C13
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cut2.py    # C2,C3 (full module)
# blindness CLI
PYTHONDONTWRITEBYTECODE=1 python3 $W/scripts/issue_calibration_acceptance_generation.py prepare-candidate \
  --ledger /tmp/s4delta/fx/open6/runs/calibration_observation_ledger.jsonl \
  --head-pin /tmp/s4delta/fx/open6/runs/calibration_ledger_head_pin.json \
  --repo-root /tmp/s4delta/fx/open6 \
  --preregistration $W/configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --predecessor-acceptance $W/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json \
  --registration-session-id derivation-night-1 --out /tmp/s4delta/open6_candidate.json \
  --d125-ruling "D-125 cl.2 as ruled at cold gate 46 R-b V7"
# byte identity of the epoch watch
git -C $W archive a3ae7bf8 | tar -x -C /tmp/s4delta/base
# (run `check` without --session-ids in both trees, cmp stdout)
```
