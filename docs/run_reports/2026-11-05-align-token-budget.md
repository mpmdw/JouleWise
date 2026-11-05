# ALIGN token admission budget and deadman — 2026-11-05

Branch: `lane/2026-11-05-align-token-budget`, based on pilot-9 `c9a0a3943`.
Implementation commit: `8944d9ed3` (`ALIGN: add whole-turn token admission budget and deadman`).
This report is a separate local documentation commit. Nothing was pushed.

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

Modules ran sequentially with unittest, without the full suite. Final results:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_decode_budget` | 15 passed, 11.923 s |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed, 29.511 s |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed, 1.387 s |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed, 77.625 s |
| `python3.13 -B -m compileall -q` on the eight changed Python files explicitly | Passed |
| `git diff --check` | Passed |

The four modules total 48 tests. Test time, including fix iterations, stayed
well below 20 minutes. Python 3.11 and hosted CI were not run.

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

There are no blocking design questions. In areas the ruling did not specify,
the implementation uses additive hardware/outcome metadata rather than changing
the shared record schema, opt-in controls rather than model-name inference, and
POSIX interruption rather than a second model process or runtime rebind.

R0/R1 values remain unfilled. The kit/R1 lane must choose B_N/B_D using the
specified floors, 1024 steps, cap ladders and measured planning-member costs,
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
