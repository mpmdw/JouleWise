# 132 — Post-merge cross-unit integration review (gate ledger row 11, second half)

- Lane: ACCEPTANCE-EPOCH-25G83-01 (PR #315)
- Merge commit reviewed: `8cbcaf081746c393ae924d6ef43287efb3c661fb`
  (parents `a0fb1505` = main pre-merge bookkeeping, `7107657d` = PR head)
- Reviewer: Opus 5 subagent, strictly read-only
- Method: `git -C /Users/edr/code/JouleWise-wt-kernel-lanes fetch origin` (no
  checkout, no branch change, canonical `/Users/edr/code/JouleWise` untouched);
  `git archive origin/main | tar -x -C /tmp/postmerge-main`; all executions below
  ran inside `/tmp/postmerge-main`.

## VERDICT: CLEAN — with one should_fix (low) and two nits

Every cross-unit contract named in the brief holds on the merged tree with
executed evidence. One latent one-home split survives the merge at the
S3/S4 seam (two names for the same ruled number, in two units, with no test
tying them); its failure direction is a refusal, not a bad admission, so it is
should_fix, not a blocker. Nothing here blocks the lane's next step.

---

## 1. Import graph — PASS

```
$ python3 -c "import joulewise.calibration_ledger, joulewise.calibration_bracketing, joulewise.calibration_exits; print('IMPORTS_OK')"
IMPORTS_OK
rc=0

$ python3 -m compileall -q joulewise scripts
compileall rc=0
```

No circular import. `calibration_bracketing` imports from `calibration_ledger`
at lines 21 and 29; the reverse grep is empty:

```
$ grep -n "calibration_bracketing" joulewise/calibration_ledger.py
(no matches)
```

`calibration_exits` imports only stdlib (`json`, `dataclasses`, `enum`,
`types`, `typing`), so it is a leaf and cannot participate in a cycle.
Exit registry is collision-free after the merge: `RefusalCode` has 74 canonical
members, `__members__` also 74 (zero silent enum aliases), zero duplicate
values; `TerminalResult` 4, `WitnessClass` 3, no duplicates.

## 2. Registries and one-homes — PASS (one nit, one should_fix)

| symbol | definitions under `joulewise/` | consumers in `scripts/` |
|---|---|---|
| `SESSION_KIND_BRACKET` / `SESSION_KIND_DERIVATION` | 1 each, `calibration_ledger.py:72-73` (+ `SESSION_KINDS` tuple :74) | imported, never restated: `issue_calibration_acceptance_generation.py:103`, `recover_calibration_ledger.py:25`, `reserve_calibration_window_bracket.py:35-36`, `validate_powermetrics_fiducial.py:72` |
| `D125_SCREEN_FLOOR_S` | 1, `calibration_bracketing.py:240` | imported at `issue_calibration_acceptance_generation.py:88` |
| `SCREEN_RULE_RANGE_EQUALS_SCREEN` / `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` | 1 each, `calibration_bracketing.py:225,232` | imported at `issue_calibration_acceptance_generation.py:94` |
| `ENVELOPE_MINIMUM_CORPUS_N` | 1, `calibration_bracketing.py:256` | none (validator-side only; see should_fix S1) |
| `IDENTITY_EPOCH_FIELDS` | 1, `calibration_ledger.py:110` | imported at `calibration_ledger_backfill.py:23`, `gen_derivation_night.py:44` |
| `MAX_DECLARED_SESSION_SLOTS` | 1, `calibration_ledger.py:76` | imported at `gen_derivation_night.py:45` |

No script restates a registry literal. The only `0.010818` outside its one home
is `calibration_bracketing.py:302`, which is the genesis generation's *data*
row (`_D102_N19_DERIVATION["operatives"]["bracket_screen_s"]`), not a second
definition of the constant.

**should_fix S1 (low) — one ruled number, two homes, no test across the seam.**
D-126 cl.2 / CG46 addendum A-2's corpus-size rule is expressed twice:

- validator (S3, library): `joulewise/calibration_bracketing.py:256`
  `ENVELOPE_MINIMUM_CORPUS_N = 17` — the hard bound a generation row may not go
  under, enforced at `:485`.
- issuer (S4, script): `scripts/issue_calibration_acceptance_generation.py:375`
  `RULED_ALTERNATIVE_CORPUS_SIZE = 17` — the one alternative floor `--ed-ruling`
  licenses (`:1152-1165`), alongside `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19` at
  `:369`.

Same ruled 17, two names, two units, no import and no test pinning them:

```
$ grep -rn "ENVELOPE_MINIMUM_CORPUS_N" tests
tests/test_calibration_bracketing.py:27:    ENVELOPE_MINIMUM_CORPUS_N,
$ grep -rn "RULED_ALTERNATIVE_CORPUS_SIZE" tests
(no matches)
```

Neither seat could see this: S3 owned the validator, S4 owned the issuer, and
each is internally consistent. The issuer already imports `D125_SCREEN_FLOOR_S`
and the `SCREEN_RULE_*` names from `calibration_bracketing` for exactly this
reason — the module's own comment at `:238` says "ONE home: the issuer imports
this constant rather than restating the digits" — so the omission is
inconsistent with the lane's own stated convention rather than with an outside
standard. Failure direction is safe: if the two ever diverge, the issuer emits
and the validator refuses at load (a stranded artifact, not an admitted bad
one). Cure is small: import `ENVELOPE_MINIMUM_CORPUS_N` as the alternative
floor, or add one assertion tying the two names. Not a gate item for this
merge.

**Nit N1 — `SESSION_KIND_*` family is split across two modules.** A strict
grep-for-one-home reviewer will trip on
`calibration_bracketing.py:205 SESSION_KIND_UNRESOLVED = "unresolved-session"`
sitting apart from the ledger's `SESSION_KIND_BRACKET` / `SESSION_KIND_DERIVATION`.
It is defensible as written — the comment at `:199-205` states that the ledger
"owns the vocabulary", and `SESSION_KIND_UNRESOLVED` is deliberately *not* in
the ledger's `SESSION_KINDS` tuple because it is a classification sentinel for
a row whose session cannot be resolved, not a kind a session may declare. No
action required; flagged only so the next sweep does not re-litigate it.

## 3. Generated regions, census, and the named tests — PASS (all rc 0)

```
$ python3 scripts/gen_g2_phase_d.py --check
PASS generated Phase D matches pinned runbook bytes
rc=0
$ python3 scripts/gen_derivation_night.py --check
PASS generated derivation-night wrapper region matches
rc=0
$ python3 scripts/gen_state.py --check
rc=0

$ python3 -m unittest tests.test_custody_mode_inventory tests.test_authentication_io \
    tests.test_mint_policy_resolver_guard tests.test_git_fixture_maintenance tests.test_docs_freshness
Ran 66 tests in 38.254s
OK
KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer
rc=0
```

Extra check, because it is the only place the two merge parents actually
touched the same file: main-side `tests/test_gen_state.py` added three
EXPECTED_IDS (`ISOLATION-RULE-DOCTRINE-01`, `V2-SURFACE-GUARD-REKEY-01`,
`RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01`) and moved the row count 165 → 168
with a matching `docs/process/state_kernel.json` (+87). The merged tree agrees:

```
$ python3 -m unittest tests.test_gen_state
Ran 44 tests in 1.532s
OK
rc=0
```

No conflict markers anywhere in `joulewise/ scripts/ tests/ docs/contracts/ configs/`.

## 4. Desk tools from a fresh extraction — PASS, with a clone caveat

```
$ python3 scripts/issue_calibration_acceptance_generation.py check
Desk epoch watch (identity comparison only; no capture authorization)
ACTIVE acceptance: d079_calibration_acceptance_v2_n17_r6
field                  expected      observed                                                         status
os_build               25F84         25G83                                                            MISMATCH
hardware_model         Mac15,9       Mac15,9                                                          match
powermetrics_sha256    unavailable   b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5 MISMATCH
mlx_version            unavailable   unavailable                                                      MISMATCH
ledger: calibration_ledger_head_uncommitted, calibration_ledger_missing, calibration_ledger_rollback
mismatched fields: os_build, powermetrics_sha256, mlx_version
rc=3

$ python3 scripts/gen_derivation_night.py --help   # full usage + rationale printed
rc=0
```

rc 3 and the printed table are exactly as the brief predicted, and the tool
degrades gracefully rather than crashing when `runs/` is absent: it names the
three ledger refusal reasons on their own line and still prints the identity
comparison, because `check` deliberately loads the snapshot with
`verify_custody=False` (`:271-278`) so the watch works in CI and in a freshly
cut clone.

**Answer to the runbook question: the desk step needs the measurement clone,
not an archive — and not a plain `git clone` either.** `runs/` is gitignored
(`.gitignore:8`), so it is absent from `git archive` *and* from any ordinary
clone; the ledger only arrives via the clone recipe that copies the ignored
ledger file, which the activation checklist already rules in
(`13-activation-checklist-2026-09-11.md:69`, "the supply read in the clone
recipe is the ignored ledger file, as ruled"). So the existing recipe is
correct as written; what the runbook must not do is let an operator run this
step from a bare checkout and read the result as a machine verdict.

**Nit N2 — the rc-3 reading is ambiguous to a 03:00 operator.** `check` returns
3 for "the machine drifted" and for "there is no ledger in this tree", and the
table prints `mlx_version unavailable | unavailable | MISMATCH`, which reads
like a contradiction. It is correct and deliberate — `mismatched_fields`
(`:149-158`) documents "Unknown on either side is a mismatch, including
unknown == unknown", i.e. fail-closed — and the distinct code
`DRY_RUN_INADMISSIBLE_EXIT = 5` already exists for the registration answer.
Optional cure: have the runbook step tell the operator to read the `ledger:`
line first, or give the ledger-absent case its own code. No code defect.

## 5. Contracts vs code on main — PASS

Every backticked identifier introduced by the lane's doc changes
(`docs/contracts/calibration_ledger.md`, `calibration_ledger_append.md`,
`powermetrics_fiducial.md`, `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`)
was extracted (83 distinct tokens) and grepped against `joulewise/**.py` and
`scripts/**.py`: **zero missing**. Every file path cited by those four docs
exists on main: **zero missing**.

Spot-check of the six statements S6 rewrote from "NOT YET LANDED" to "landed"
(trace 112, item 1), each of which names its code site by symbol:

| symbol named by the contract | hits in `joulewise/` + `scripts/` |
|---|---|
| `SESSION_KIND_DERIVATION` | 17 |
| `_prior_set_matches_import_cutoff_prefix` | 2 |
| `prior_prefix_mode` | 9 |
| `import_plus_live` | 5 |
| `bracket_session_id` | 66 |
| `_is_derivation_kind_observation` | 4 |
| `--derivation-only` (registered writer arg) | `scripts/validate_powermetrics_fiducial.py:1772` |

Residual grep for `not yet landed` / `NOT YET LANDED` / `No shipped writer`
across `docs/contracts/` and `configs/calibration/*.md`: empty.

The six issued acceptance artifacts still validate byte-identically through the
production loader:

```
$ python3 -m unittest tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.\
test_every_issued_generation_and_genesis_fixture_load_byte_identically -v
... ok
Ran 1 test in 0.008s
OK
rc=0
```

(The test sweeps every `configs/calibration/calibration_acceptance_*.json` —
six files present: `_v2`, `_v2_r2`, `_v2_n17_r3`, `_r4`, `_r5`, `_r6` — and
asserts the count equals `ISSUED_ACCEPTANCE_REGISTRY`.)

Extra cross-unit check the brief did not ask for but the S7/S1 seam needed:
all 26 long flags the tracked chain
`scripts/night_chains/calibration_derivation_only.zsh` passes are registered
argparse options of the scripts it calls — zero unknown flags.

## 6. What the merge itself contributed — no production code

`git diff 7107657d origin/main` is 120 files / +20444 / −3, and it is
main's own bookkeeping only. **Zero changes under `joulewise/` or `scripts/`.**
`git diff a0fb1505 origin/main` (the other direction) is exactly the PR's
33 files / +12985 / −172, i.e. the merge is a clean union.

Main contributed:

1. `README.md` — the activity blurb rewritten for this lane (1 line, replaced).
2. `TASK_QUEUE.md` (+6) and `docs/process/state_kernel.json` (+87) — the three
   final-wave follow-up rows (`ISOLATION-RULE-DOCTRINE-01`,
   `V2-SURFACE-GUARD-REKEY-01`,
   `RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01`).
3. `tests/test_gen_state.py` (6 ±) — the matching EXPECTED_IDS additions and the
   165 → 168 count (verified green above; this is the only file both parents
   could have contended for, and they did not).
4. `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md` (±75) —
   the durable pointer.
5. ~114 trace records under
   `docs/process_traces/2026-09-10-activation-96bfeca7/` — briefs 43–56, seat
   reports 58–61 and their b-revisions, refuters 62–65 / 71 / 74 / 81 / 87 / 89
   / 93 / 104 / 105, deltas 66–68 / 70 / 73 / 77 / 83 / 91 / 96 / 106, the three
   cold-gate packet directories (42, 46, 69) with rulings and Opus pairing
   refuters, replays 94 / 98 / 100 / 107 / 111 / 114 / 119 / 121 / 125 / 128 /
   130, row-10 passes 117 / 120 / 122 / 126 / 129 / 131, terminal reviews 109 /
   113 / 118, the runbook drafts 99 / 108 / 115, and the activation checklist 13.

## Open obligation (not a merge defect, recorded so it is not lost)

The derivation-night **operator runbook** still exists only as trace drafts
(`99-derivation-night-runbook-draft.md`, revised by 108 and 115). Tracked,
operator-reachable homes today are: the generated wrapper region inside
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (the
`gen_derivation_night.py --check` target, green above) and
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. Outside those,
`issue_calibration_acceptance_generation.py` is named only in
`docs/contracts/calibration_ledger.md`, `docs/decision_log.md` and traces — no
checklist or runbook step invokes the desk `check`. This is already fenced:
activation checklist record 57 makes "the corpus-night runbook is written" a
precondition of arming any night. It is a queued obligation, not a defect this
merge introduced.

## Addendum — main advanced during this review (no effect on the verdict)

While this review ran, the resident magistrate committed post-merge bookkeeping
in `/Users/edr/code/JouleWise-wt-kernel-lanes` and pushed it, so `origin/main`
moved from `8cbcaf08` to `d18bc2b3`:

```
$ git log --oneline 8cbcaf08..origin/main
d18bc2b3 CHECKPOINT T38k (2026-09-10 ~19:55 PDT) ...
c1487ffb Post-merge bookkeeping: ACCEPTANCE-EPOCH-25G83-01 implementation merged ...
$ git diff --shortstat 8cbcaf08 d18bc2b3
 5 files changed, 16 insertions(+), 5 deletions(-)
   README.md, RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json, + one trace
```

Docs and kernel bookkeeping only — no `joulewise/`, `scripts/` or `tests/`
change. This review's evidence is pinned to the `git archive` of the merge
commit `8cbcaf08` under review and is unaffected. (The worktree HEAD move was
the magistrate's own commit, not this read-only review: this session ran only
`fetch`, `log`, `show`, `diff`, `ls-tree` and `git archive` there; the worktree
was and is clean, and `/Users/edr/code/JouleWise` was never touched.)
