# Refuter review — PR #312 T0 clock refusal tests (contract lens)

**Head reviewed:** `6e0bbf67737ab54872fb69cd4a5f60dc346e9d10` (verified by `git rev-parse HEAD`
in the detached worktree `/Users/edr/code/JouleWise-wt-ref-stub-astra`). Seat head
`4203ff599b0e7dfafda73ea7d10fb86ee2efbe71` confirmed an ancestor of the review head; the only
other commit in range is the merge of `origin/main`. Diff scope, from
`git diff afaeffef..6e0bbf67 --numstat`: `37  0  tests/test_arm_readiness_evidence_t0.py` — one
file, 37 insertions, **0 deletions**, no production file touched.

**Lens:** contract — fidelity to the governing text (root-cause consult 99 §Regression proposals)
and to the kernel's reviewer refusal criteria for ARM-INTEGRATION-LOAD-01.

**Independent execution performed:** yes. Three runs in the detached worktree, none relying on
seat report 108's evidence:

1. The requested targeted run (below), 10.7 s, `OK`.
2. A mechanical byte-faithfulness diff of the consult's fenced proposal against the added lines.
3. A guard-identity probe (my own, not in report 108): `mock.patch.object(t0, "_underivable", spy)`
   recording `inspect.currentframe().f_back.f_lineno` at each raise, then running each test.

Requested run, tail:

```
test_capture_finish_ahead_of_ordinary_now_refuses (...ArmReadinessEvidenceT0Tests...) ... ok
test_insufficient_positive_capture_history_refuses (...ArmReadinessEvidenceT0Tests...) ... ok
test_r0_raw_anchor_ahead_of_author_raw_refuses (...ArmReadinessEvidenceT0Tests...) ... ok

----------------------------------------------------------------------
Ran 3 tests in 10.674s

OK
```

Guard-identity probe output (exactly one raise per test, no earlier guard fired):

```
test_insufficient_positive_capture_history_refuses: pass=True raises=[(556, 'clock-reference command capture fields are invalid or stale')]
test_r0_raw_anchor_ahead_of_author_raw_refuses:     pass=True raises=[(1163, 'T-0 RAW anchor span is below 600000000000 ns')]
test_capture_finish_ahead_of_ordinary_now_refuses:  pass=True raises=[(562, 'clock-reference command capture is not a live T-0 artifact')]
```

I did **not** re-run report 108's full-module suite (V1, 71 tests / 467.5 s); that claim is
uncorroborated by me and rests on the seat plus the lead's bench run recorded in commit 77702eab.

## Q1 — byte-faithfulness and non-vacuity

Byte-identical to consult 99 §Regression proposals after the required class-body re-indent. My
mechanical `difflib` comparison of the consult's fenced block (re-indented by four spaces) against
the added lines reports two differences, both blank-line count between methods (the consult writes
module-level `def`s separated by two blank lines; the file separates class methods by one, which is
PEP 8 and matches the surrounding file). No token, literal or identifier differs.

Non-vacuity rests on the pre-existing helper, quoted from
`/Users/edr/code/JouleWise-wt-ref-stub-astra/tests/test_arm_readiness_evidence_t0.py:1189-1196`:

```python
            self.assertRaises(T0EvidenceAuthoringError) as caught,
        ):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, kind)
        self.assertEqual(caught.exception.reason_code, reason_code)
        self.assertEqual(str(caught.exception), detail)
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())
```

Four independent ways to fail: authoring succeeding at all (`assertRaises`), the wrong exception
`kind`, the wrong `reason_code`, and — the biting one — exact string equality on `detail`. The two
trailing `assertFalse` calls additionally require that no source or evidence directory was left
behind, so a refusal that half-wrote the pack still fails. Nothing here can pass vacuously.

## Q2 — pinned strings, and three distinct guards

Each pinned detail is produced by production, at `joulewise/arm_readiness_evidence_t0.py`:

- `:556` — `raise _underivable(kind, f"{step_id} command capture fields are invalid or stale")`,
  reached from `:552` `or value["started_monotonic_ns"] < 1`. With `step_id="clock-reference"` the
  f-string renders exactly the test's literal.
- `:1163` — `raise _underivable(kind, "T-0 RAW anchor span is below 600000000000 ns")`, a literal,
  reached from `:1162` `if span < _MIN_IDLE_NS:`.
- `:562` — `raise _underivable(kind, f"{step_id} command capture is not a live T-0 artifact")`,
  reached from `:559` `value["finished_monotonic_ns"] > now`.

**Three different guards, established by execution, not by reading:** the probe above records
lines 556, 1163 and 562 respectively, one raise each. Field validation, RAW anchor span, and
live-artifact age — not the same guard three times.

## Q3 — the two "ahead" tests stay inside their own clock families

Consult 99: *"The two 'ahead' refusals correctly compare timestamps within their respective clock
families. A RAW anchor ahead of ordinary `now` alone should not refuse."*

`test_r0_raw_anchor_ahead_of_author_raw_refuses` lands on `:1162` `if span < _MIN_IDLE_NS:`, where
`span = author_anchor.monotonic_raw_ns - r0["anchor_monotonic_raw_ns"]`
(`arm_readiness_evidence_t0.py:1161`) — RAW minus RAW. The mutation sets R0's anchor one nanosecond
above the author RAW, giving `span = -1`. No ordinary-clock value enters the comparison.

`test_capture_finish_ahead_of_ordinary_now_refuses` lands on `:559`
`value["finished_monotonic_ns"] > now`, where `now = context.clock.monotonic_ns()` (`:557`) —
ordinary minus ordinary.

Neither encodes the cross-family rule the consult warned against. See Nit 2 for the one place a
future reader could misread this.

## Q4 — thresholds, mocks, deletions, production edits, overstatement

Governing text, `docs/process/state_kernel.json` → `/tasks/ARM-INTEGRATION-LOAD-01/acceptance`:
*"no test deletions or production-gate relaxation. Reject relaxed thresholds, retries-until-PASS,
skipped rows and PASS-returning predicate mocks."*

- **No threshold change.** `600000000000` in the pinned string is production's own
  `_MIN_IDLE_NS`-derived literal at `:1163`; the test asserts it, it does not set it. `--numstat`
  shows the production module is not in the diff at all.
- **No PASS-returning mock.** The only patching is the pre-existing `author_environment` seam
  (`tests/test_arm_readiness_evidence_t0.py:833-841`), which installs a synthetic
  `_DerivationClock`. Every added test drives that seam toward a **refusal**; none converts a
  refusal into a pass. The two `mutate` callbacks write real JSON to the real fixture inputs.
- **No deletions, no skipped rows, no retries.** 37 insertions, 0 deletions; the probe shows
  `skipped=[]` for all three; no loop or retry construct.
- **No name shadowing.** A duplicate-method scan over all `test_*` methods in the module returns
  an empty list, so none of the three silently overrides an existing case.
- **Scope is honest.** The consult's regression package had three parts; the `setUp` cure
  (`tests/test_arm_readiness_integration.py:302`
  `fixed_monotonic_ns = coherent_clock_anchor().monotonic_raw_ns`) and
  `ArmReadinessIntegrationClockPortabilityTests` (`:871`) are already at `afaeffef`. PR #312 lands
  the remaining third, and its commit message calls itself a "coverage follow-up" rather than the
  cure. It does **not** on its own satisfy the kernel acceptance clause "focused and four-worker
  replays pass under controlled concurrent agent load"; that remains open and this PR should not be
  recorded against it.
- **Report 108 line citations spot-checked and correct:** 552, 556, 559, 562, 1162, 1163 in
  production, and "test-module line 1194" for the biting assertion, all verified at the review head.
  Its `F1` baseline-drift flag is accurate. One imprecision only, in Nit 3.

## Blockers

None.

## Should-fix

None.

## Nits

**Nit 1 — the 500-second test's dependence on fixture arithmetic is unstated.**

(a) `tests/test_arm_readiness_evidence_t0.py:1702-1706`:

```python
    def test_insufficient_positive_capture_history_refuses(self) -> None:
        self._assert_clock_refusal(
            now_monotonic_ns=500_000_000_000,
            detail="clock-reference command capture fields are invalid or stale",
        )
```

Nothing on the page says why 500 s refuses. The refusal exists only because
`make_t0_fixture` at `tests/test_arm_readiness_evidence_t0.py:566` builds
`time_origin = now_monotonic_ns - t0._MIN_IDLE_NS - 1_000`, making the capture start
`-100_000_000_990` and tripping `:552`.

(b) Global writing standard, first-use test: a reader should be able to replicate the mechanism
from the text alone. The consult itself spells the arithmetic out; the landed test does not.

(c) Add one comment line above the call, e.g. `# make_t0_fixture:566 subtracts _MIN_IDLE_NS from`
`# this instant, so 500 s of ordinary history yields a negative capture start.` No behaviour change.

**Nit 2 — in the RAW test, author RAW and ordinary `now` are numerically identical, so only the
pinned string separates the right invariant from the wrong one.**

(a) `tests/test_arm_readiness_evidence_t0.py:1708-1722` passes `now = SYNTHETIC_MONOTONIC_NS` and no
`sample_anchor`, so `author_environment` (`:839`) installs
`lambda: coherent_clock_anchor(raw_ns=now_monotonic_ns)` — author RAW `== now == 1_000_000_000_000`.
The mutation `anchor_raw=now + 1` is therefore simultaneously "one ns ahead of author RAW" and "one
ns ahead of ordinary now".

(b) Consult 99: *"A RAW anchor ahead of ordinary `now` alone should not refuse."*

(c) The test is nonetheless correct and does not encode the wrong invariant: the exact-equality
assert on `"T-0 RAW anchor span is below 600000000000 ns"` pins line 1163, and a hypothetical
cross-family guard would raise a different message and fail the test. My guard-identity probe
confirms line 1163 is what fires. The fix is documentation, not code — add
`# Author RAW == ordinary now here by construction; the pinned detail string is what proves the`
`# refusal comes from the RAW-minus-RAW span guard and not from a cross-clock comparison.`
Do not displace the sampler to separate the two numerically: that would change `span` and depart
from the consult's byte-faithful text for no gain.

**Nit 3 — report 108 overstates by one word.**

(a) `108-seat-t0-refusal-tests-astra-report.md`: *"Added 37 lines, exactly matching the proposal;
no helper adaptations or commits."*

(b) The consult's proposal is a module-level snippet; landing it as class methods requires a
four-space re-indent and collapses the inter-method blank lines from two to one.

(c) Read it as "byte-identical after class-body re-indent, with PEP 8 blank-line normalisation".
Substance is unaffected; no correction to the code is needed.

## Same-signature statement

**No same-signature condition.** The standing escalation trigger fires on two consecutive rounds
failing with the same signature; this is a first-pass review of a test-only addition, no fix round
preceded it, and I raise no blockers, so there is no round to repeat.

On the *substantive* signature — consult 87 → consult 99's "host-calibrated fixture assumption" —
these three tests do not re-introduce it. Every instant they use is synthetic and literal
(`SYNTHETIC_MONOTONIC_NS`, `500_000_000_000`, `now + 1`); none reads `time.monotonic_ns()` or any
other host clock, so none can behave differently on a freshly-booted runner. This is the last of the
consult's three regression proposals to land, and it lands without the defect it documents.

## Verdict

**findings** — three nits, all documentation-only; no blockers, no should-fix. The diff is faithful
to consult 99, refuses through three distinct production guards proven by execution, violates none
of the kernel's ARM-INTEGRATION-LOAD-01 refusal criteria, and is landable as-is.
