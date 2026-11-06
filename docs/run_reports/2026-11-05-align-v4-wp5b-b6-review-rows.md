# ALIGN v4 WP5b: b6 retroactive review rows — 2026-11-05

WP5b continues `lane/2026-11-05-align-v4-wp5-b6` from
`4344a117488b4f2d8ad8f3d1e9da69e4edb488b3`. The tree was initially clean.
The supplied brief and `/private/tmp/jwsol/v4-plan-synth.md` rulings 2–4 / WP5
own scope and acceptance. Plan SHA-256:
`e46bf4cdbf8af3258db36b0b2f14164db0046f3bac3cb7e50fbfccdfc7d5cd8e`.
Mission M0 found no active stop card or global gate. The explicit brief
supersedes kernel/task registration, coordination-state updates and full-suite
requirements for this run. No peer agent, consult, external integration,
network access, measurement capture or analysis pipeline was used.

## Changes and admission

Copied the three supplied Opus papers verbatim into the requested
`docs/align/reviews/2026-11-05-retro-executing-review-<sha>.md` paths. Appended
exactly three records to `configs/b6/executing_reviews.json`, deriving each from
the paper's section 5. All 53 prior records and both levels of schema keys are
preserved. Each new review uses a repository-relative paper path and records
`paper sha256 <digest>` in its existing `covered` field. No schema key was added.
All three are explicitly retroactive.

| Commit | Verdict recorded | Paper SHA-256 |
| --- | --- | --- |
| `dc2204dba1e0512e17ff264be4f2498b04d0cbb0` | ADMIT | `2a48c3036b997fb0f92383b9a6e5c0a0bede7aec3aa248c1313045b6cfd8e924` |
| `b29c25c59ad57787faae4e939578dea01c5682a6` | ADMIT | `3fe4cba22070c2be54d7e96059ced00069f53f6ac403412ba465a900a187b75f` |
| `0ba413d40fbadeac03d619cda7c030a11eb24394` | ADMIT_WITH_FIXES; admitted for limit None/0 only; F2 required before any limit > 0 cell | `759eb902a5932c3233ed2b1c7fd33bc18d171f0d1b70d87b867f6e98928d7ffd` |

The audit previously accepted only archive-absolute paper paths. Updated
`tests/b6/test_audit_record_fixes.py` to retain that historical text-only case
and also accept repository papers directly in `docs/align/reviews/`. The latter
must be Markdown files, have no traversal or symlink escape, exist, and match
the SHA-256 citation. Append-only identity, unique commits, the independent
history walk through HEAD, and the production `code_check.check` assertions
are retained. No history range was shortened or excluded. This is the only
test-code change; runtime and measurement code are untouched.

`git merge-base --is-ancestor 0ba413d40 HEAD` succeeded. The starting HEAD
contains integration `c8ef6b2f6`; its second parent is `8f8023277b`, the #657
head. Thus the checkpoint commit belongs in this branch's coverage. The named
WP14 commit `a17ed96c8` is unavailable in local objects; no fetch was attempted.
The requested destination paths were taken directly from the brief and the
papers were checked against the supplied `/private/tmp` originals.

## Verification

The two attempted modules used this exact prefix, sequentially in the table's
order:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v <module>
```

| Module | Passed | Failed | Skipped | Interrupted | Not started | Result / elapsed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tests.b6.test_audit_record_fixes` | 8 | 0 | 0 | 0 | 0 | exit 0; wrapper 76.413 s; unittest 75.842 s |
| `tests.b6.test_cold_pass_fixes` | 11 | 0 | 0 | 1 | 2 | exit -2; budget timeout; wrapper 1114.800 s; no final unittest timer |
| `tests.b6.test_loop_round_desk` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_desk_resume_finalize` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_capture_screen_reachability` | 0 | 0 | 0 | 0 | 9 | not started; not run |

Totals: 19 passed, 0 failed, 0 skipped, 1 interrupted, 23 not started.
Sequential wrapper wall time: **1191.213 s**. The 1,190 s cap interrupted its own test process group. A partially completed test or subtest is not counted as passed. The five-module acceptance is incomplete.

The full five-module acceptance is still open because the standing test-time
cap was reached. The gamma test was interrupted;
these two cold-pass tests never started:

- `FullRoundTests.test_lost_start_reference_without_spare_counts`
- `FullRoundTests.test_physical_and_opening_no_bound_stops_rotate`

The interrupted case was
`FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim`.
The other three modules have 21 tests not started. Earlier part-1 results are
historical evidence and are not counted as fresh WP5b passes.

Next exact step: the lead reviews the implementation commit, then runs the
four incomplete/unrun modules sequentially in a sufficiently long authorized
test window before claiming the WP5 acceptance gate is green:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_cold_pass_fixes
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_loop_round_desk
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_desk_resume_finalize
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_capture_screen_reachability
```

`env PYTHONPYCACHEPREFIX=/private/tmp/jwsol/v4-wp5b/tmp/pycache python3.13 -m compileall -q joulewise tests`
passed (exit 0). A separate static check confirmed all prior review rows are
unchanged, commits remain unique, all three copies equal their source bytes,
and all three SHA-256 citations match. Final `git diff --check` and a protected-
file diff check passed. The full suite and quick-suite expansion were not run,
per the explicit sequential targeted-test and machine-load restrictions.

## Limits and lead follow-up

The recorded Opus native results are supplied upstream evidence. They were not
reproduced in this sandbox. No native test was attempted or counted as skipped.
The lead's WP3/WP6 native gates remain, including:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
```

The lead must preserve `hybrid_checkpoint_limit` None/0 for this admission.
F2 puts the opt-in boundary prefill outside the deadman guard; before any
positive-limit cell, fix it and rerun the paper's E4 probe (and affected native
gates). `code_check.check` consumes commit coverage, so a passing b6 audit is
not an automatic runtime enforcement of the paper's conditional admission.
No runtime fix or WP3 ruling is made here.

The original archive paths in the copied papers and historical rows were
handled only as text. The 0ba paper retains its author's process note about an
upstream top-level archive listing; this session did not access that archive.
Any disposition of that upstream note remains with the lead. No new Ed ruling
is requested for these records.

Prior WP5 work remains in `649af40ea` / `4344a1174`; the prior detailed handoff
is recoverable as `git show 4344a1174:answer.md`. The dated part-1 run report is
unchanged. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` were not edited or regenerated.

## Process evidence and next step

One pinned-spec implementation stream, no subdelegation. The supplied Opus
papers are consumed as review evidence with the verdicts/conditions above;
lead adjudication and final integration verification remain lead-owned.
Source-to-destination paths and hashes are recorded above and in the new rows.
Synthetic test logs and the sequential wrapper are under
`/private/tmp/jwsol/v4-wp5b/tmp/`; final per-log hashes are recorded below.
The local test gates checked records and synthetic processing, without
establishing a new live measurement number. No mechanism is proposed for
removal from this single run.

Implementation commit: `3bf81ba5312482c9bd64aa14937ad065175ee8a1`. The report-only commit follows on the
same branch. Nothing was pushed. The next exact verification commands are
listed above; integration, native gates and any push remain lead-owned.

## Ephemeral verification artifacts

| Artifact | SHA-256 |
| --- | --- |
| `/private/tmp/jwsol/v4-wp5b/tmp/run_targeted.py` | `656b62183527794d73de43a43995bbda13b6aa28989671e690dfdb5f1fc3831c` |
| `/private/tmp/jwsol/v4-wp5b/tmp/test-results.json` | `51e0f102834bd704a3a09e12f54a194dbb25cc9fecf2f2040769d3d413d47c0f` |
| `/private/tmp/jwsol/v4-wp5b/tmp/test_audit_record_fixes.log` | `c4673aba8de2d8468a141d48b2bba44852e10fdcdb495478583c909a05e60d0d` |
| `/private/tmp/jwsol/v4-wp5b/tmp/test_cold_pass_fixes.log` | `0f9645433425c42f0a262414be72a41a8aabd9fc867ddc9613dfbb1ab6759ffe` |

Source papers: `/private/tmp/jwsol/v4-retro-review-<sha>.md`, with the
same hashes as their committed copies in the table above. The remaining-test
list is `/private/tmp/jwsol/v4-wp5b/tmp/remaining-tests.json`.
