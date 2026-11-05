# ALIGN token admission budget and deadman — 2026-11-05

Branch: `lane/2026-11-05-align-token-budget`, based on pilot-9 `c9a0a3943`.
Implementation commit: `8944d9ed3` (`ALIGN: add whole-turn token admission budget and deadman`).
This report began as a separate documentation commit. The supplied executing
review confirms that the original branch was subsequently pushed and PR #660
exists. The fix-round branch and commits below remain local; this fix round
used no network and did not push or update the remote PR body.

## Intake and authority

Read the council FINAL-DESIGN first through `git show`, then repository intake,
M0, orchestration, relevant decision-log entries and implementation/test seams.
The council ref resolves to `219fb151515383cbbcde887d096837a829c67396`;
§2.2 and B3 govern this work. `ACTIVE_STOP_CARD` was NONE. The explicit user
brief selected this bounded implementation over historical queue pointers.
The tree started clean at the requested base. No kernel task was registered.

The user's standing rules override the ordinary full-suite and coordination
close-out requirements: RUN_STATE, TASK_QUEUE, state_kernel and test_gen_state
were not edited. No restricted directory, real measurement data, external
model/cache path or analysis pipeline was opened or run. No network or hardware
collection was used. The Git alternate was used only through ordinary Git object
reads. No independent agent or external integration was invoked.

## Implemented behavior

- Optional `max_episode_decode_tokens` and `deadman_s` survive spec/config
  round trips, campaign counterbalancing and projected/measured policy identity.
- Decode admission checks cumulative emitted tokens before the next turn.
  An admitted turn keeps its entire per-turn cap, including when it overshoots
  the episode threshold. Reasoning counts toward decode. A budget stop records
  `episode.decode_budget:<k>` and is normal, without exclusion.
- The existing context reservation protects the rendered prefill plus full
  per-turn decode cap. New controls enforce a 40960 context ceiling even if the
  native limit is unread. No separate cumulative prefill budget was invented:
  the binding design specifies a decode admission threshold and context cap.
- The monotonic deadman checks admissions and stream boundaries. A POSIX timer
  also interrupts blocked stream reads, prompt rendering and tool calls on the
  production main thread. Internal cancellation inherits BaseException so a
  generic tool/model Exception handler cannot silently consume it. Returned
  tokens are retained; no subsequent tools are dispatched after expiry.
- `episode.deadman:<k>` marks an incomplete, failed member. The existing
  controller salvage seam preserves episode, transcript, turn rows, runtime
  events and failure evidence. Scoring is skipped for incomplete episodes.
  No pinned controller, monitor, SMC reader or MLX runtime changed; no rebind.
- Opt-in member evidence in `hardware.token_budget`, episode outcome and runtime
  metadata includes decode/prefill/cache counts, configured/effective limits,
  indexed stop reason and incompleteness. The existing desk exposes the fields,
  groups new controls separately, and excludes deadmen from registered residual
  fits and episode-scope alternatives. All-member diagnostics remain visible.
- Unset fields leave legacy serialization, identities and member records alone.
  The four actual anchor configs and their 120-second guard are unchanged.

## Files touched

| Files | Purpose |
|---|---|
| `joulewise/align/apple/budget.py` | Deadline cancellation and additive member budget record |
| `joulewise/align/apple/workload.py` | Spec validation, identity, turn admission, context ceiling, custody |
| `joulewise/align/apple/endpoint.py` | Opt-in stream cap/deadman, partial-token retention, cache abandonment |
| `joulewise/align/apple/campaign.py` | Keep unlike budgets/deadmen in separate counterbalance cells |
| `joulewise/align/apple/diagnostics.py` | Distinct end states and null-precheck compatibility for failed bundles |
| `joulewise/align/apple/pilot_analysis.py` | Additive desk fields/grouping and deadman exclusion |
| `tests/align/test_decode_budget.py` | 15 synthetic tests, including frozen anchor/config/artifact regressions |
| `tests/align/test_pilot3_cache.py` | Explicit legacy-contract oracle and new policy-identity checks |
| `docs/align/token_admission_budget.md` | Configuration, admission semantics and operational limits |
| This report | Handoff without coordination-state edits |

## Verification

Modules ran sequentially with unittest, without the full suite. The original
TMPDIR was not recorded. These historical pass counts are environment-specific:
the supplied review reproduced an anchor-hash failure with default macOS
symlinked TMPDIR, and a pass with a physical temporary root. See the fix round
for the portable regression and fresh results with an explicit TMPDIR.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_decode_budget` | 15 passed, 11.923 s |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed, 29.511 s |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed, 1.387 s |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed, 77.625 s |
| `python3.13 -B -m compileall -q` on the eight changed Python files explicitly | Passed |
| `git diff --check` | Passed |

The four modules total 48 tests in that original environment. Original test
time, including fix iterations, stayed well below 20 minutes. Python 3.11 and
hosted CI were not run by the implementation session; the review-reported CI
failure is recorded below.

An additional inline synthetic comparison loaded the endpoint, workload,
diagnostics and pilot_analysis sources directly from Git at `c9a0a3943`, ran the
old and new 120-second paths, and compared bytes. The episode, turn and transcript
artifacts, v3 desk JSON, and sampler/output-policy/outcome JSON all matched.
Only the temporary model-root string was normalized. The resulting five hashes
are frozen in the regression test, alongside hashes of the four actual anchor
configs. This is synthetic behavior evidence, not live hardware validation.

Checks caught two substantive compatibility issues during development: failed
members can have a null precheck object, which the desk previously crashed on;
and the old cache serialization test derived its legacy oracle from all current
dataclass fields, so adding optional fields changed its expected bytes. The desk
now handles null as absent, and the test uses an explicit pre-controls contract.
An incorrect metadata-key assertion and a test launcher using SIGALRM were also
corrected; the latter conflicted with the intentionally exclusive deadman timer.

## Assumptions, limits and next exact step

This is the original implementation handoff; the fix-round handoff below
supersedes its review status and next step.

There are no blocking design questions. In areas the ruling did not specify,
the implementation uses additive hardware/outcome metadata rather than changing
the shared record schema, opt-in controls rather than model-name inference, and
POSIX interruption rather than a second model process or runtime rebind.

R0/R1 values remain unfilled. Under the user's Amendment-1 direction, window 1
uses Qwen3.8-27B only, Qwen3-Next is dropped, and Flash-Next is later. The kit/R1
lane must choose B_D using the specified floors, 1024 steps, cap ladders and
measured planning-member costs,
and set `deadman_s = (1750 - I_m) / 1.13544`. Example values in the usage note
are illustrative. This lane did not rewrite production cell configs or claim
that a particular model fits a chosen budget/deadman.

Real timer coverage requires SystemClock, the main thread, POSIX setitimer and
no existing active real timer; other production environments fail closed. Python
signals cannot guarantee interruption of an uninterruptible native/device call.
The runner's outer member cap remains necessary. Whether the selected deadman
leaves enough room for normal model work and future holds/gates is an R1 check.

Next: the lead reviews `8944d9ed3` against council B3, incorporates this lane
with the other Stage-1 work, and carries the selected values into the new-model
configs during the authorized R0/R1/kit workflow. Independent executing review,
hardware qualification and the remaining council gates are still outstanding;
this report does not claim those gates passed.

## Fix round

Scope: PR #660 executing-review verdict `ADMIT_WITH_FIXES`, supplied as
`/private/tmp/jwsol/rev-660.json` (SHA-256
`b1888c6f869127f74fb683ec3d158547ffa8b45f97797d4ce6010cdae90aec4a`).
There are two MEDIUM and three LOW findings, no BLOCKER/HIGH findings, and no
refuted notes. All five findings are addressed below; the remote PR/CI actions
are handed to the lead because this run is offline.

The clean clone started at `01b6cd2d8`. Fixes are on the new local branch
`lane/2026-11-05-align-token-budget-fix-660`. No lead-owned coordination files
or kernel registrations were changed. No real study data, real restricted
directory, external model path, measurement pipeline, network, or hardware
collection was accessed. Tests used synthetic model files inside the explicit
temporary root. No peer agent or external integration was invoked.

Authority: read `FINAL-DESIGN.md` through the supplied council ref at
`219fb151515383cbbcde887d096837a829c67396`, especially V2, §2.2 and B3.
`git show` for `FINAL-DESIGN-AMENDMENT-1.md` at that ref failed because the file
is absent; a local `git log --all -- <exact amendment path>` also found no
commit. The user was asked for a local ref. This round applies the user's
explicit Amendment-1 model direction above and changes no model roster or
production config; the amendment's remaining contents were unavailable for
independent verification. `ACTIVE_STOP_CARD` was NONE; the explicit fix brief
selected this work and superseded ordinary state-file/full-suite duties.

### Finding-to-commit map

| Finding (review order) | Commit / disposition | Regression and result |
|---|---|---|
| M1: budget stop hides endpoint fault (`workload.py`, `diagnostics.py`) | `3e44dfcee` | Late reasoning-accounting fault after returned text/tool calls plus exhausted budget reproduced success before the fix. Runtime now fails, preserves fault custody, and desk reports `runner.error`. Diagnostic tests cover endpoint/episode/runner faults with budget and deadman flags. |
| M2: anchor hash normalization assumes a physical TMPDIR | `728fdcce8` | A forced symlink root failed the frozen episode hash before the fix. Resolve and normalize the physical root before the original spelling; original five hashes and four config hashes remain unchanged. Both physical and symlink roots pass. |
| L1: SIGALRM during guard disarm drops returned work and leaks handler | `1924abc8c` | Deterministic alarm on disarm reproduced loss of token 101; a separate disarm exception reproduced missed handler restoration. Clear the armed flag before disarm and restore in a nested `finally`. Both regressions pass; a matching optional MLX-evaluation regression is provided for the lead. |
| L2: unpaired controls and deadman beyond member cap accepted | `03c1e919e` | Both unpaired forms and deadlines equal to, above, or far above `1800 / 1.13544` were accepted before the fix (five failing subtests). They now raise `ValueError`; a value immediately below the ceiling and legacy specs still round-trip. Identity tests now compare valid paired policies and vary each field independently. Usage documentation updated. |
| L3: report/PR claims omit pushed state, TMPDIR caveat and red CI | This documentation commit; remote PR update and CI remain lead actions | Corrected local report, recorded exact fresh test environment and review-supplied CI status. A bounded report-content assertion failed against the old local-only claim and passes after correction. No persistent self-referential documentation test was added. |

Fix-round files touched: `joulewise/align/apple/{budget,workload,diagnostics}.py`,
`tests/align/{test_decode_budget,test_pilot3_cache}.py`,
`docs/align/token_admission_budget.md`, and this report. The endpoint, pinned
runtime/controller/monitor/SMC files, and production configs are unchanged.

### Verification and limits

All commands used Python 3.13.18. Every test module was run one at a time with
`TMPDIR=/private/tmp/jwsol/fix-660/tmp`; no full suite was run. Each code/test
finding's new regression was executed against the unfixed code and failed for
the reviewed behavior before the fix. M1/M2/L1/L2 module reruns passed after
their fixes. During L1 verification, an assertion initially addressed the
provenance token IDs at the wrong nesting level; corrected to `generation`
before the final verified L1 commit.

The L2 ceiling is deliberately permissive: it uses zero intercept and only
rejects deadlines that cannot beat the 1800 s cap even then. It is not an R1
measurement or a guarantee for a real model. The kit must still enforce
`deadman_s = (1750 - I_m) / 1.13544` using its measured intercept.

Fresh final results (same explicit TMPDIR for each test command):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_decode_budget` | 20 passed, 1 MLX skip (21 total), 10.710 s |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed, 0.792 s |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed, 30.726 s |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed, 105.022 s |
| `python3.13 -B -m compileall -q joulewise tests` | Passed |
| Bounded report-content assertions: obsolete local-only claim absent; original TMPDIR omission and CI run `42013285621` present | Passed (failed before report correction) |
| `git diff --check` | Passed |
| `git diff --exit-code 01b6cd2d8 -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | Passed; all four untouched |

The four final modules total 53 passes and one MLX skip. Reported test time,
including baseline, failing probes and fix iterations, was about 3.5 minutes,
below the 20-minute cap. Python 3.11 and hosted CI were not run in this round.

MLX is absent in this interpreter (`find_spec('mlx')` returned `None`); no
native MLX computation ran. Outside this sandbox, the lead must run:

```sh
python3.13 -B -m unittest tests.align.test_decode_budget.DeadmanTests.test_mlx_evaluated_token_survives_alarm_during_disarm
```

That importability-gated test evaluates real MLX arrays inside the otherwise
synthetic stream and injects the cleanup race. It does not load a model or
replace R0/R1 real-model, Metal-stall, hold, or sizing qualification. Python
signal delivery can still be deferred by uninterruptible native calls.

CI status is supplied by the executing review, not refreshed in this offline
run: run `42013285621` is red on shards 2, 4, 6, 10 and 12, in b6 modules
`test_cold_pass_fixes`, `test_desk_resume_finalize`, `test_loop_round_desk`,
`test_audit_record_fixes`, and `test_capture_screen_reachability`. The review
reports the same failures on sibling lanes' runs `42012582057` (smc-thermal)
and `42013328460` (r0-desk), supporting its pre-existing-failure classification.
This round did not independently reproduce those unrelated failures and makes
no green-CI or merge-ready claim.

Next exact step: the lead reviews these local commits, supplies or verifies
the missing amendment text, runs the named MLX test on a usable Metal host,
updates the PR body from this report, and reruns or repairs CI to satisfy the
green-CI merge rule. No push, merge or live-run authorization is implied.
