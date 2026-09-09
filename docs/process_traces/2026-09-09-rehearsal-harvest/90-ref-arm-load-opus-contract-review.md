# 90 — Refuter (Opus 5, CONTRACT lens): PR #311 / ARM-INTEGRATION-LOAD-01

**Head reviewed:** `6881709d092f0198a52c36d48b1332385a6a1bcf` (verified by `git rev-parse HEAD` in the detached
worktree `/Users/edr/code/JouleWise-wt-ref-stub-astra`). Diff base `0fda6d95`. Canonical `/Users/edr/code/JouleWise`
was not touched.

**Lens:** CONTRACT. Does the change stay inside 99gn option (a) and the kernel row's acceptance summary
(`/tasks/ARM-INTEGRATION-LOAD-01/acceptance` in `docs/process/state_kernel.json`), which rejects "relaxed
thresholds, retries-until-PASS, skipped rows and PASS-returning predicate mocks", plus cold gate 56
§ADDENDUM-2 and Opus refuter 57 §Race-test analysis. Author role: none — I am a fresh non-author reader.
No seat report exists (seat 85/89 timed out before reporting), so every fact below is bench-verified in this
session rather than relayed.

---

## Independent execution performed

All runs in `/Users/edr/code/JouleWise-wt-ref-stub-astra`, env
`PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS=`.

**E0 — brief's command as written returns nothing.** The test named in my charge does not live in the module
named in my charge:

```
$ python3 -m unittest tests.test_arm_readiness_integration -k test_subprocess_clock_observations_keep_refusal_predicates_real
Ran 0 tests in 0.000s
NO TESTS RAN
```

`test_subprocess_clock_observations_keep_refusal_predicates_real` is defined at
`tests/test_launch_window.py:884` (class `ProductionArmRelocationLaunchTests`). Re-run against the right module:

**E1 — the named test (timer probe first).**

```
timer_slack_ratio 2.57
test_subprocess_clock_observations_keep_refusal_predicates_real
  (tests.test_launch_window.ProductionArmRelocationLaunchTests....) ... ok
----------------------------------------------------------------------
Ran 1 test in 213.605s
OK
python3  115.80s user 81.59s system 92% cpu 3:33.89 total
```

**E2 — the two new integration tests.**

```
test_specified_clock_boundaries_reach_real_arm_predicates ... ok
test_specified_census_observations_refuse_before_publication ... ok
----------------------------------------------------------------------
Ran 2 tests in 44.719s
OK
python3  21.05s user 19.76s system 90% cpu 45.007 total
```

**E3 — race test at head `6881709d`.**

```
test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses ... ok
Ran 1 test in 22.842s
OK
python3  26.80s user 32.27s system 255% cpu 23.123 total      -> 59.07 s CPU
```

**E4 — race test at base `0fda6d95`** (checked out, measured, then restored to `6881709d`; `git rev-parse HEAD`
re-verified as `6881709d09…`, `git status --porcelain` empty).

```
Ran 1 test in 24.260s
OK
python3  41.35s user 54.76s system 391% cpu 24.526 total      -> 96.11 s CPU
```

**E5 — assertion and test-method census (no deletions).**

```
$ git diff 0fda6d95..6881709d -- tests/ | grep -E "^-.*(assert|self\.fail|mock\.patch)"
-        self.assertFalse(
-                    mock.patch.object(
-        self.assertEqual(armed.returncode, 0, f"{armed.stdout}{armed.stderr}")
-        self.assertEqual(arm_result["status"], "PASS", arm_result)

test methods  0fda6d95 -> 6881709d
  evidence_t0   68 -> 68
  integration   10 -> 12
  lifecycle     69 -> 69
  launch_window 37 -> 38          (net +3, none removed)

$ git diff 0fda6d95..6881709d | grep -E "^\+.*(while |retry|for _ in range|sleep)"
(none)
```

**E6 — production-knob grep (Q5).**

```
$ grep -rn "arm_clock\|coherent_clock_anchor\|REALTIME_OFFSET" joulewise/ scripts/ .github/ docs/contracts/
(no matches)
$ grep -rn "^import tests\|^from tests\|import tests\." joulewise/*.py scripts/*.py
(no matches)
```

**E7 — fixture-repo contents built at head** (`make_go_fixture()` in-process, temp dir, then cleaned up):

```
repo top level:        ['.git', 'configs', 'joulewise', 'tests']
tests/ contents:       ['tests/fixtures', 'tests/fixtures/arm_clock.py']
files mentioning arm_clock inside the repo: (none)
tracked files under tests/: ['tests/fixtures/arm_clock.py']
```

---

## Contract answers

### 1. Inside 99gn option (a) and the kernel's refusal criteria? — YES.

`coherent_clock_anchor` returns a `ClockAnchor` of three integers and nothing else
(`tests/fixtures/arm_clock.py:12-16`):

```python
    return ClockAnchor(
        realtime_ns=REALTIME_OFFSET_NS + raw_ns + drift_ns,
        monotonic_raw_ns=raw_ns,
        read_skew_ns=skew_ns,
    )
```

It returns **observations, not verdicts**. Everything that adjudicates them is untouched production code:
`_sample_live_clock_anchor` still runs `_current_boot_session_id()` and builds the mapping
(`joulewise/arm_readiness.py:6723-6736`); `_clock_probe_predicate_passes` still applies every ruled gate,
including

```python
        or not 0 <= live_clock_anchor["read_skew_ns"] <= 1_000_000
```
(`joulewise/arm_readiness.py:6825`) and

```python
    return live_delta <= 5_000_000
```
(`joulewise/arm_readiness.py:6835`). `_predicate_passes` (`:6838`) and `_evaluate_rows` are not patched anywhere
in the diff.

**Is patching `sample_anchor` at the module boundary a seam or a mock?** A seam, and the diff proves it with a
counterfactual a mock could not survive. `tests/test_arm_readiness_integration.py:333-336` drives the same
custody through three subtests differing by **one nanosecond** in a single observed field:

```python
        for skew, drift, expected in (
            (1_000_000, 5_000_000, "PASS"),
            (1_000_001, 0, "REFUSE"),
            (1_000, 5_000_001, "REFUSE"),
        ):
```

and asserts both the receipt-level reason code and the row verdict
(`tests/test_arm_readiness_integration.py:359-372`). A PASS-returning mock of `_predicate_passes` or
`_clock_probe_predicate_passes` cannot produce PASS at 1 000 000 ns and REFUSE at 1 000 001 ns; only the real
predicate reading the real numbers can. E1/E2 confirm both boundary families execute and hold, in-process and
through the real ARM subprocess.

The four named-forbidden shapes are all absent: no relaxed thresholds (every constant in
`arm_readiness.py:6793-6810` and `:6823-6835` is untouched — production files are not in the diff at all,
diffstat is 5 test files), no retries (E5), no skipped rows (`tests/test_arm_readiness_integration.py:363`
asserts `len(clock_rows) == 1`; `:388` asserts `len(authored["authored_rows"]) == 15`), no test deletions (E5).

99gn's explicit preservation instruction is satisfied: the authored-side boundary tests it named
(`tests/test_arm_readiness_schemas.py:1269`, `tests/test_arm_readiness_evidence_t0.py:1593`, `:1767`) are
untouched — `test_arm_readiness_schemas.py` is not in the diff, and evidence_t0's method count is unchanged
at 68 (E5).

**One scope note for the ledger, not a finding:** the acceptance summary names
`author_environment(probe=…, sample_anchor=…)` and "the fixture bootstrap hook". The PR also installs
class-wide patches in two `setUp`s (`tests/test_arm_readiness_integration.py:314-318`,
`tests/test_arm_readiness_lifecycle.py:579-585`), so those two classes no longer exercise the real
`clock_reference.sample_anchor` at all. This is still "supply coherent anchors through
`_sample_live_clock_anchor`" in 99gn's own words, and the displaced coverage is retained verbatim by
`tests/test_clock_reference.py:267-284`, which asserts the midpoint, the skew, the exact `CLOCK_MONOTONIC_RAW /
CLOCK_REALTIME / CLOCK_MONOTONIC_RAW` read order and the not-`CLOCK_UPTIME_RAW` fence. No coverage is lost.

### 2. Thresholds relaxed / rows skipped / tests deleted / retries added? — NO. Complete list of the four changed assertions:

1. `tests/test_arm_readiness_lifecycle.py` — `self.assertFalse(` (bare) replaced by the evidence-bearing
   `assertFalse` at `:923-930`. Strictly more information, same predicate.
2. `tests/test_launch_window.py` — the module patch
   `mock.patch.object(clock_reference, "sample_anchor", return_value=anchor)` replaced by threading the same
   object through `self._mint_v4_arm(sample_anchor=lambda: anchor)` (`:530`). Every numeric expectation of
   `test_mint_keeps_raw_anchors_separate_from_sequence_clock` survives unchanged, including
   `"anchor_delta_ns": 0` and `"anchor_realtime_ns": anchor.realtime_ns` (`:500-502`).
3. `tests/test_launch_window.py:870-873` — `assertEqual(armed.returncode, 0, …)` became
   `0 if expected_arm_status == "PASS" else 1`. `expected_arm_status` defaults to `"PASS"` (`:538`), so every
   pre-existing caller asserts exactly what it asserted before.
4. `tests/test_launch_window.py:875` — `assertEqual(arm_result["status"], "PASS")` became
   `expected_arm_status`, **plus** a new assertion that was not there before (`:876-880`):
   `reason_codes == []` on PASS and `["readiness_clock_preflight_refused"]` on REFUSE.

Net effect is a strengthening. Separately, the deleted block at old `tests/test_launch_window.py:831-855`
removed a post-hoc rewrite of the captured R0 evidence bytes (`r0_reference["anchor_realtime_ns"] =
live_clock_offset_ns + …`) — the test used to mutate captured evidence after capture so the delta would come
out; it now specifies R0, author and subprocess coherently up front and lets the predicate adjudicate. That is
a soundness improvement, and the non-zero-delta coverage the old live sample provided is replaced by a
*boundary* case (`drift 5_000_000` PASS / `5_000_001` REFUSE, `tests/test_launch_window.py:885-888`), which is
stronger than an arbitrary live value.

### 3. The race test — the single `_assemble_launch_inputs` patch removes nothing the property depends on.

`launch()` reads exactly one field out of the shared dict —
`argv = list(launch_inputs["exec_argv"])` (`scripts/launch_window.py:263`) — and then hands the whole dict to
`_consume_launch_capability(**launch_inputs, …)` (`:266-271`). That callee is docstringed
"Reauthenticate complete launch inputs, then atomically claim one GO"
(`joulewise/arm_readiness.py:10328`) and independently re-runs, **per consumer**:

| step | site |
|---|---|
| GO admission | `arm_readiness.py:10357` `_admit_pack_launch_go(...)` |
| full ARM verification | `:10397` `_verify_arm_receipt(...)` |
| receipt re-read + digest/binding comparison | `:10407-10423` |
| volatile root/backup/lock predicates | `:10426` `_root_policy_refusals(...)` |
| manifest / window.env / window-chain re-read and re-hash | `:10448-10467` `_load_launch_manifest_for_consumption`, `validate_launch_manifest` |
| binding reconciliation | `:10468` `_reconcile_launch_binding(...)` |
| GO authentication with a live monotonic instant | `:10486-10496` `_authenticate_pack_launch_go(..., at_monotonic_ns=consumed_at, ...)` |
| **the real deadline** | `:10533-10535` `if not go_bounds[0] <= consumed_at < go_bounds[1]: raise _go_invalid("monotonic_ns")` |
| **the linearization point** | `:10539` `_exclusive_write(consumption_path, raw)` → `readiness_record_consumed` on collision (`:10541-10544`) |

So the comment's claim at `tests/test_arm_readiness_lifecycle.py:904-905` — "Each consumer still reauthenticates
ARM/GO, hashes and bindings, checks real deadlines, and races the real O_EXCL claim below" — is **true**, and I
verified each clause at the line numbers above. The exactly-one property (`execve.call_count == 1`,
1× `launch_consumption_invalid`, 7× `readiness_record_consumed`, `:932-935`) is unaffected. I also checked the
new shared-mutable-state hazard: `validate_launch_manifest` (`arm_readiness.py:2712-2726`) and the receipt
comparison at `:10409` are read-only, so eight threads sharing one `launch_inputs` dict is safe.

What the patch *does* remove is the eight-way concurrency of the **caller-side** assembly — the test no longer
races GO/ARM authentication against consumption at `_assemble_launch_inputs`. Nothing in the asserted property
depends on it, and the callee re-does all of it, but the comment does not mention the reduction (see Should-fix
SF-2).

**Timeout branch: yes, it records everything refuter 57 asked for.** 57 §5 asked for "how many threads were
alive, the partial `outcomes` list, or `execve.call_count`". `tests/test_arm_readiness_lifecycle.py:923-930`
now records all three plus which consumers completed:

```python
                    f"alive_count={len(alive)} alive={alive} "
                    f"completed_consumers={list(partial_outcomes)} "
                    f"execve.call_count={execve.call_count} "
                    f"partial_outcomes={partial_outcomes}",
```

with named threads (`name=f"consumer-{index}"`, `:912`) and per-consumer keyed outcomes
(`outcomes: dict[int, str]`, `:873`). 57's separate nit — "the `consume()` closure leaves `outcome` unbound if
`launch()` ever returns normally" — is also cured: `outcome = "launch_returned_without_refusal"` (`:877`) plus a
catch-all `except Exception` (`:885-886`) and a `finally` record (`:887-889`). The 30 s join is preserved
(`:919`) and was not raised, as the brief required.

### 4. `REALTIME_OFFSET_NS` far-future anchors — no predicate reads absolute realtime; nothing silently passes or refuses for the wrong reason.

`2_000_000_000_000_000_000` ns ≈ 2033-05-18, about seven years ahead of true wall clock. It is safe because
**every** production consumer uses only the difference REALTIME − MONOTONIC_RAW, in which the offset cancels
identically:

- `_clock_probe_predicate_passes` authored-side delta, `joulewise/arm_readiness.py:6782-6788`;
- the same predicate's live-vs-authored delta, `:6828-6835`;
- `_derive_clock_attestation`, `joulewise/arm_readiness_evidence_t0.py:1166-1171`;
- `t0_rehearsal`, `joulewise/t0_rehearsal.py:643-644`.

Freshness and deadlines are on different clock families and stay live: `valid_until_monotonic_ns` and the
liveness bound at `arm_readiness.py:6806-6809` use ordinary monotonic; `go_bounds` at `:10534` uses
`time.monotonic_ns()`; `_utc_now` (`arm_readiness.py:5432`, `datetime.now(UTC)`) is the only wall-clock read in
the ARM/T-0/clock modules (E6-adjacent grep) and is never compared with any anchor field. `t0_span_ns` is
RAW-versus-RAW (`:6781`), and the fixture keeps it real: `make_t0_fixture` derives R0 at
`author_anchor − _MIN_IDLE_NS − 980`, so the 600–3600 s span gate at `:6794` still adjudicates a real value.
No schema or contract bounds `anchor_realtime_ns` absolutely (grep over `joulewise/schemas/`,
`docs/contracts/` returned nothing). The constant is also **not new** — it was
`SYNTHETIC_REALTIME_OFFSET_NS` at `tests/test_arm_readiness_evidence_t0.py:53` at the base; this PR only moves
it and widens where it applies. See nit N-2 for the one durability concern.

### 5. What the PR does NOT prove, and hidden knobs.

It does not prove live machine readiness, and **nothing over-claims it**. The fixture leads with the
disclaimer, `tests/fixtures/arm_clock.py:1`:

> `"""Specified clock observations for ARM tests; never machine-readiness evidence."""`

which is exactly 99gn's "It does not prove live machine readiness". The revised class comment at
`tests/test_launch_window.py:441-442` is likewise accurate and scoped. What remains unproven and must not be
read out of this PR: real quiet-machine clock discipline, real census absence on Ed's machine, and — see SF-1 —
determinism under four-shard load, for which this PR contains no evidence at all.

No hidden production knob: E6 shows `arm_clock`, `coherent_clock_anchor` and `REALTIME_OFFSET` appear nowhere
under `joulewise/`, `scripts/`, `.github/` or `docs/contracts/`; there is no env var, no CLI flag and no
`if TESTING` branch. The diff touches five files, all under `tests/`, all inside the brief's `WRITE_SCOPE`.

---

## Blockers

None.

---

## Should-fix

### SF-1 — "dominated" over-states the measured saving, and the PR does not discharge cold gate 56 §ADDENDUM-2.

**(a) Quote.** `tests/test_arm_readiness_lifecycle.py:902-905`:

```python
            # Assemble these immutable fixture inputs once through production.
            # Eight redundant caller-side ARM replays dominated the race cost.
```

**(b) Governing text.** Brief 84 item 3(b): "if the test's CPU cost is dominated by something incidental …
reduce it WITHOUT weakening the property (**state what you changed and why the property is unchanged**)". Cold
gate 56 §ADDENDUM-2: "On the NEXT full-suite four-shard replay on any integration tree … record whether
`test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses` passed under concurrency, with the
shard count and the timer-probe reading at start. If it fails again under concurrency, ARM-INTEGRATION-LOAD-01
… must be amended to name it and its 30 s join explicitly, and no further waiver is available for it."
Global writing standard: "No word does unpaid work."

**(c) Proposed correction.** Measured this session (E3/E4, same machine, alone, timer slack 1.77–2.57×):

| | base `0fda6d95` | head `6881709d` | delta |
|---|---|---|---|
| CPU (user+sys) | 96.11 s | 59.07 s | **−38.5 %** |
| wall | 24.26 s | 22.84 s | **−5.9 %** |
| CPU% | 391 % | 255 % | −136 pts |

38.5 % is a real and worthwhile cut, but it is not domination, and the quantity the forcing defect actually
blew — per-thread wall time against `join(timeout=30)` — improved by 1.4 s alone. Replace "dominated the race
cost" with the measured figure, e.g. "removed ~37 s of ~96 s CPU (−38 %) of duplicated caller-side
authentication; the callee re-runs all of it per consumer (`arm_readiness.py:10357`, `:10397`, `:10486`)".
Separately, the merge record must state that this PR reduces but does not eliminate the four-shard join-timeout
risk and that ADDENDUM-2's obligation is still **open** — it is discharged only by an actual four-shard replay
recording this test's outcome, the shard count and the start timer-probe reading. Brief 84 item 4 required
exactly that run under CPU burners; the seat timed out before producing it, so no such evidence exists at this
head. This should be an explicit unfinished-obligation line on the PR, not an inference the reader has to make.

### SF-2 — the `make_go_fixture` comment states a mechanism that does not exist; the copied helper is unreachable from the fixture repo.

**(a) Quote.** `tests/test_arm_readiness_lifecycle.py:420-424`:

```python
    # Authoring replays import these test modules in a copied repository.
    # Carry their observation helper with the fixture, not the runner's path.
    clock_fixture = Path("tests/fixtures/arm_clock.py")
    (repo / clock_fixture).parent.mkdir(parents=True)
    (repo / clock_fixture).write_bytes((ROOT / clock_fixture).read_bytes())
```

**(b) Governing text.** Global writing standard: a term or claim is "either (a) built from physical reality
before first use, (b) glossed in plain words AT first use, or (c) deleted"; and the C-028 rule that a fix-round
change must name its counterfactual and production call site. This comment names a mechanism ("authoring
replays import these test modules in a copied repository") that I could not reach from any call site.

**(c) Proposed correction.** Bench evidence (E7, built at this head): the fixture repository's entire `tests/`
tree is the single copied file; its only tracked `tests/` entry is `tests/fixtures/arm_clock.py`; and no file
inside the repo references it. The only processes ever run against that repo execute `scripts/*.py`
(`tests/test_arm_readiness_evidence_t0.py:416-427` with `PYTHONPATH=str(repository)`,
`tests/test_launch_window.py:852-869`), and **no production module imports `tests.*` at all** (E6 grep over
`joulewise/*.py scripts/*.py` is empty), so nothing on those paths can import the helper. Either name the exact
replay and its import line in the comment, or drop the two lines — the author must re-verify by deletion, since
I am read-only and cannot run the counterfactual. Two smaller defects in the same hunk regardless of which way
it goes: `mkdir(parents=True)` lacks `exist_ok=True`, so it will raise `FileExistsError` the first time any
other fixture creates `repo/tests/` before this line; and the file is committed into every `make_go_fixture`
repository by the `git add .` at `tests/test_arm_readiness_lifecycle.py:507`, which moves `HEAD^{tree}` for
every ARM fixture in the suite for no stated reason.

---

## Nits

### N-1 — the fixture does not match the signature of the seam it replaces, and the mismatch would fail closed silently.

**(a) Quote.** `tests/fixtures/arm_clock.py:9-11`:

```python
def coherent_clock_anchor(
    *, raw_ns: int = 1_000_000_000_000, skew_ns: int = 1_000, drift_ns: int = 0
) -> ClockAnchor:
```

versus the real seam, `joulewise/clock_reference.py:110-112`:

```python
def sample_anchor(
    clock_gettime_ns: ClockGettimeNs = time.clock_gettime_ns,
) -> ClockAnchor:
```

**(b) Governing text.** Kernel acceptance: "Reject … PASS-returning predicate mocks"; the spirit is that a seam
must behave like the thing it stands in for. Mutation-cure counterfactual rule: a substitute must be exercised
at its real production call site.

**(c) Proposed correction.** `coherent_clock_anchor` is keyword-only, but `sample_anchor` is called
**positionally** in production at `joulewise/clock_reference.py:178` (`anchor = sample_anchor(clock_gettime_ns)`
inside `build_clock_reference`). The two class-wide `side_effect=coherent_clock_anchor` patches
(`tests/test_arm_readiness_integration.py:314-318`, `tests/test_arm_readiness_lifecycle.py:579-585`) would
therefore raise `TypeError` for any covered test that ever reaches `build_clock_reference` — and that
`TypeError` is swallowed twice over, by `_sample_live_clock_anchor`'s `except Exception: return None`
(`joulewise/arm_readiness.py:6726-6728`, which then fails closed to
`readiness_clock_preflight_refused`) and by `_sample_anchor`'s `except Exception` in the author
(`joulewise/arm_readiness_evidence_t0.py:1071-1072`). The result would be a refusal indistinguishable from a
real clock refusal — precisely the "refusing for the wrong reason" failure this lane exists to remove. It is
currently unreachable (`build_clock_reference` is called only from `scripts/collect_clock_reference.py:61` and
`tests/test_clock_reference.py`), so this is prophylactic: give the fixture the seam's real shape,
`def coherent_clock_anchor(clock_gettime_ns=None, *, raw_ns=…, skew_ns=…, drift_ns=…)`.

### N-2 — the far-future REALTIME offset is safe only under an unstated invariant.

**(a) Quote.** `tests/fixtures/arm_clock.py:1-6`:

```python
"""Specified clock observations for ARM tests; never machine-readiness evidence."""
...
REALTIME_OFFSET_NS = 2_000_000_000_000_000_000
```

and the only rationale given, at `:12`: `"""Keep RAW independent of ordinary monotonic capability deadlines."""`
— which explains the RAW choice, not the REALTIME one.

**(b) Governing text.** Writing standard first-use test: a value doing technical work is built before first use
or glossed at it. Also 99gn: "Preserve clock boundary tests."

**(c) Proposed correction.** Add one sentence recording *why* ≈2033 is admissible: every production consumer
compares only REALTIME − MONOTONIC_RAW (`joulewise/arm_readiness.py:6782-6788`, `:6828-6835`;
`joulewise/arm_readiness_evidence_t0.py:1166-1171`; `joulewise/t0_rehearsal.py:643-644`), so the offset cancels;
no predicate compares an anchor's realtime against `_utc_now()` (`arm_readiness.py:5432`) or wall-clock now.
Stating the invariant means that if anyone later adds an absolute realtime plausibility bound, the reason these
fixtures start failing is legible instead of mysterious — and it prevents the opposite failure, a new absolute
bound being silently defeated across four test modules.

### N-3 — "Identical custody" is not what the test builds.

**(a) Quote.** `tests/test_arm_readiness_integration.py:332`:
`"""Identical custody passes at the limits and refuses one ns beyond."""`

**(b) Governing text.** "Packet facts bench-verified" / no unearned words: each subTest calls
`self.prepare_profile("ALPHA")` (`:337-339`), which builds a **fresh** `make_go_fixture` temporary repository
per iteration; nothing asserts the custody bytes are equal across the three subtests.

**(c) Proposed correction.** Either say "equivalently-built custody", or make the claim true by asserting the
pack/receipt digests match across subtests. The test's *argument* is sound either way — the discriminating
evidence is the 1 ns boundary, not byte-identity — so this is wording only.

### N-4 — the guard assertion still unwinds the `execve` patch with a consumer possibly running.

**(a) Quote.** `tests/test_arm_readiness_lifecycle.py:923-930`, `self.assertFalse(alive, …)`, now inside
`with mock.patch.object(launch_window.os, "execve") as execve:` (`:901`).

**(b) Governing text.** Brief 84 item 3: keep the property and the 30 s join; refuter 57 §2: a hung consumer is
"stuck in work, not in waiting".

**(c) Proposed correction.** None required — this is **not a regression**; at the base the same assertion sat
*outside* the `with`, so the patch was already released before the check. In both versions a still-alive
consumer that later wins the race would call the **real** `os.execve` in the test process after the mock
unwinds. Moving the assert inside the `with` is a small improvement. If the author wants to close it properly,
record `alive` and defer the failure until after a bounded second join, or mark the threads `daemon=True`.

### N-5 — seam scope is wider than the acceptance summary names (recorded, no action).

`tests/test_arm_readiness_integration.py:314-318` and `tests/test_arm_readiness_lifecycle.py:579-585` patch
`readiness._clock_reference.sample_anchor` for two entire test classes, not only through
`author_environment(sample_anchor=…)` as the acceptance summary spells it. Substantively inside 99gn option (a)
("Supply coherent numeric fixture anchors through `_sample_live_clock_anchor`"), and the displaced coverage of
`sample_anchor`'s own arithmetic is fully retained by `tests/test_clock_reference.py:267-284`. Logged so the
kernel row's acceptance can be closed against what was actually built.

---

## Same-signature statement

**No same-signature repetition.** This is the first review round against `6881709d`; the implementing seat
(85/89) produced no report, so there is no prior verdict on this head to repeat and no fix round has yet been
attempted on any of these findings. The standing escalation trigger — "two consecutive rounds failing with the
SAME SIGNATURE" — is not met. One adjacent signature is worth naming for the magistrate: the *lane's* forcing
defect (`readiness_clock_preflight_refused` and the race-test join timeout under four-shard load) has now been
observed four-plus times and remains **unreproduced under load at this head** (SF-1); if the next four-shard
replay fails again on this test, cold gate 56 §ADDENDUM-2 makes the next spend a lane amendment naming the test
and its 30 s join, not another replay.

---

## Verdict

**findings** — 0 blockers, 2 should-fix (SF-1 over-stated saving + undischarged ADDENDUM-2 obligation; SF-2
unsupported comment and unreachable copied helper), 5 nits. The contract holds: the seams supply observations,
not verdicts; predicates, bindings, thresholds and deadlines are untouched production code; refusals still
refuse at 1 ns past both boundaries in-process and through the real ARM subprocess; no rows skipped, no retries,
no test deletions, no production knob. Both should-fix items are about the accuracy of what the change *claims*,
not about what it *does*.
