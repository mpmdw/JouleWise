# Independent Sol seat 2 — v4 registration desk handoff

Date: 2026-11-07. Branch: `align/2026-11-07-sol-v4-registration-seat2`.
Starting HEAD: `be3cc8b680cde290299aeb8d198de73993fe38b2`.
The requested branch was already checked out and the worktree was clean.

## Delivered

- `docs/align/squeeze/sol/v4-registration-seat2.md`: executive recommendation;
  prioritized owner/lane/cost/R1–W1–D action table; proposed exact protocol and
  deviation text; implementation and test obligations; immutable commit/line
  citations; confidence per item; blind Fable + Opus gate checklist; claim limits.
- This dated report. No runtime, config, test, registered protocol, coordination
  state or other source file changed.

The recommendation is **do not arm W1 at the audited head**. The draft covers
chair 4/5/6/9/11/15/17/18/20, WP19, battery 4(a), contrast fit, applied duty
fallback, classifier drift, R0 digest binding, seed law, member-5 loss, schedule
and timing differences, and the remaining pre-arm audit debts. It also maps
other chair clauses required for registration and the separate D/squeeze gates.

Additional findings from code/text comparison:

- The installed replay is W1 5/17; chair U4/E_ref and cross-day comparisons still
  name 5/18. The alternate bank seed cannot be mixed into the spam reference.
- R10 at `d600baba0` supplies completion/fit checks only under its receipt;
  no-receipt admission intentionally preserves the older contrast gap.
- A synthetic probe reproduces `>=` threshold detection and the carrier helper's
  calibration from H-shifted carriers. Uniformly shifting their scores leaves
  its reported detection fraction unchanged.
- The rank-general formula selects rank 38 at m=39 (5% marginal bound under
  exchangeability), while the helper/public sample-max language yields 2.5%.
  This needs an explicit rank policy and consistent wording.
- v4 GPU/log-edit evidence cannot establish the requested external-DC,
  adaptive monitor–energy squeeze. A prospective addendum and physical controls
  remain necessary; complementarity is a testable hypothesis, not a guarantee.

## Authority and safety

Read clone-local AGENTS/CLAUDE guidance, Mission M0, the relevant restart/queue
and do-not-do-yet text, the source-of-truth map, orchestration and targeted
decision-log index. The active stop-card projection says NONE. The explicit
brief selected this desk task and forbade coordination updates; no kernel task
was registered and RUN_STATE/TASK_QUEUE/state kernel/test_gen_state were untouched.

Read the requested agenda, energy-tripwire explanation, integrated v4 protocol
and residual contract, and the named literature/program/pre-arm audit snapshots.
Also inspected the already-present R10 and OC refs to avoid proposing obsolete
fixes. The deliverable records their complete immutable hashes. No other current
squeeze seat's branch was read. The historical OC branch and prior Fable/Opus
pre-arm papers are pre-existing design/audit sources, not the independent seats
working this brief.

No network or fetch: the brief's no-network rule overrides its fetch request;
the needed refs were already available. No model downloads, MLX imports, native
measurements, long test suites, B5 pipeline, real restricted data, process/job
inspection, or reads/listings of user paths outside the clone occurred. Git
objects from the permitted alternate store were accessed only through Git.

## Verification actually performed

1. `git status --short --branch` / `git branch --show-current`: correct requested
   branch, clean initial tree.
2. Selected `git show <commit>:<path>` and `nl`/`rg` reads: checked authority,
   protocol/implementation gaps, R10 scope and estimator code. A guessed
   `scripts/align_pilot_desk.py` path at the old desk commit did not exist; no
   conclusions depend on that failed read. The energy-boundary wording was kept
   to the supported on-host GPU versus external DC distinction.
3. `python3.13 -B - <<'PY' ... PY`: tiny synthetic probe executed only the
   frozen, standard-library-only `v4_estimands.py` source from Git. Confirmed
   H*=128 at exact score==threshold and unchanged 1/21 detection fractions for
   scores shifted by +100 at H=128. No measurements or model libraries.
4. `nice -n 19 python3.13 -B /private/tmp/jwsol/squeeze/sol-v4-registration-seat2/check_registration_seat2.py`:
   **3 tests passed in 1.486 s**. Checked citation line existence, required item
   coverage/document hygiene and the reported synthetic helper behaviors,
   including m=39 rank arithmetic. The first pass verified **88 unique anchors
   in 25 immutable source files**. `nice` printed `setpriority: Operation not
   permitted`; Python nevertheless ran and passed. No background job was touched.
5. `python3.13 -B /private/tmp/jwsol/squeeze/sol-v4-registration-seat2/check_registration_seat2.py`:
   **3 tests passed in 1.553 s**, with 88 citation anchors across 25 source files.
   Staged `git diff --cached --check` passed and the staged diff was reviewed
   before commit. These checks validate this report and reproduce defects,
   **not** proposed repairs or W1 readiness.

Full suite/compileall were unnecessary for two documentation files and the full
suite was expressly prohibited. No existing application test modules were run
against this starting checkout; the relevant ALIGN implementation lives in the
pinned lane objects. All proposed code tests in the deliverable remain future
obligations on the lead's implementation candidate. This session's total test
time is seconds, well below the brief's ~20 minute limit.

Native follow-up outside this sandbox, on a qualified Metal host with no
downloads, includes the existing tiny/random-model tests:

```sh
python3.13 -B -m unittest tests.align.test_r0_mlx_native
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
```

Those tests do not replace actual X/Y production token/cache identity, R0/R1
sensor/duty/U5 qualification, battery receipts, power restoration or the future
physical adaptive controls. All live work is lead-owned and agent-free.

## Open questions, uncertainties and next step

The draft deliberately leaves numerical U3 calibration unavailable: public maxima
do not determine a defensible bar or its false-fail rate. The lead must provide
an authorized unrestricted summary and admit the estimator. Final D5 authority,
native R0/R1 evidence, the duty-bar ruling, native Y ordering and exact Q6 split
are also absent from this seat's evidence. No sealed outcomes were inferred.

The report proposes, rather than installs, U6 diagnostic status, label-only seed
tag treatment, a one-member battery window bar, exact 30-minute/24-hour freshness
rules, timing margins and universal contrast checks. These are science/authority
choices for the lead; native overhead, eventual fallback success and adaptive
joint-evasion rates remain unknown. Claim weakening is tabulated explicitly.

Next exact step: lead adjudicates items 0–20, supplies U3 and final D5 authority,
assigns bounded REG/KIT/DESK repairs, and assembles the final candidate for the
independent blind gate. Nothing was registered or armed by this seat.

## Local commit

The commit containing this report carries both documentation files on the
requested branch. Its message is `docs(align): draft independent v4 registration seat 2 gate plan`.
The exact commit ID is supplied in the final handoff. No push or remote mutation.
