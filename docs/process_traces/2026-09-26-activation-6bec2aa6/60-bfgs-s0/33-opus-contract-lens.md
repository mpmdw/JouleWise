# BFG-S S0 — CONTRACT lens (Opus 5.5), candidate `26ab7234`

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), fresh session, read-only on the repository (WRITE_SCOPE `[]`). Worktree `JouleWise-wt-s0-opus-6bec2aa6` at `26ab7234`, working tree clean. Reviewed `git diff 64e39bb9 26ab7234` (8 files, all inside the ruled S0 WRITE_SCOPE).

Authority: cold gate BFGS-DESIGN-01 addendum, Final texts v1.1 §4, texts 1–4, 15 and 17, and T1–T4. Also the magistrate gap-fill `20-ruling-bundle-span.md`, the seat briefs `00` and `21`, and the seat reports `10` and `22`.

Contamination: the harness loaded the global and project `CLAUDE.md` and the memory index. I opened no `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE.local.md`, decision log or memory file. The pin *values* are out of scope, as the charge says; the pin *mechanism* is in scope.

## Verdict

**One BLOCKER, four SHOULD-FIX, six NIT.**

- **The blocker.** The quiet wrapper's measured span was never ruled; the seat chose it itself and did not disclose the choice. With that choice, every network-time-refusal envelope comes out `battery_float_evidence_missing`. Once S2 lands, text 6 turns that into a whole QPE-01 summary blanked by one clock refusal. That is exactly addendum blocker 1, which v1.1 exists to cure.
- **Where it must be fixed.** S2 cannot fix it, because S2's WRITE_SCOPE excludes `joulewise/battery_float.py`, and the next PR that may touch that file is S4. It has to be resolved in S0.
- **Everything else in the diff matches the ruled text line by line**:
  - `PHASES`;
  - the `PairVerdict` field order and status set;
  - the rung order of `authenticate_pair`, including custody raising first;
  - the bundle span, exactly per the gap-fill;
  - the seven-row guard and its self-tests;
  - the fence placement, its polarity and the exemption tuple;
  - the staleness pin.
- **Nothing outside S0 moved.**

## Executed evidence (this session)

| # | Probe | Result |
|---|---|---|
| E1 | `python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep` | `Ran 95 tests in 184.495s` / `OK` |
| E2 | `python3 -m unittest tests.test_evidence_night tests.test_night_kinds` | See the addendum at the end: it was still running when this report was first written. |
| E3 | `git archive 64e39bb9` into `/tmp/s0base-opus`, then the candidate's `tests/test_battery_float.py` dropped over the **base** source; ran `S0FreezeTests` + `ParserTests.test_future_update_time_is_currently_a_pass` | `Ran 3 tests` / `OK`. The frozen-function pins and the `observe` golden are truly base bytes, and the frozen functions are byte-unchanged at the candidate (E1 passes the same pins). |
| E4 | `git diff --stat 64e39bb9 26ab7234` | 8 files, all in S0 scope; no `controller.py`, `bundle_read.py`, collector or pack path. |
| E5 | Grep of `configs/`, `joulewise/`, `scripts/` and `tests/` for pins of the three S0 production files | `night_kinds.py` appears only in `quiet_predicate_campaign.MANIFEST_PATHS`, a per-plan digest taken at `measurement_head`, not a committed pin. `battery_float.py`'s whole-file digest is recorded by `issue_calibration_acceptance_generation.py:1614` as `battery_float_module_sha256` and is never compared. No `arm_readiness.sources` or `configs/**` pin names any of the three. **No frozen-source pin moved.** |
| E6 | `/tmp/s0opus_probe.py` P1: a quiet envelope shaped as the collector writes it on the network-time refusal path (`sample_quiet_predicate_evidence.py:1072-1083`), with `start_stamp` present, no `end_stamp` and an empty `rounds.jsonl`, plus a valid passing pair | `battery_float_evidence_missing ('pre evidence missing: quiet_pre outside measured span', 'post evidence missing: quiet_post outside measured span')` |
| E7 | P2: `violations("scripts/x.py", …)` for four `PairVerdict` forgeries | alias assignment `PV = bf.PairVerdict; PV(...)` → `[]`; `dataclasses.replace(verdict, status='pass')` → `[]`; `type(x)(...)` → `[]`; `getattr(bf,'PairVerdict')(...)` → `[]` |
| E8 | P3: `authenticate_pair(record, d, phases=("bundle_pre","bundle_post"), identity="run-1")`, with no span | `pass`; the guard reports `[]` for such a call from `joulewise/x.py` |
| E9 | P4: `exit_code` `False` (pre) and `0.0` (post) | `pass` |
| E10 | P5: capture pair with pre `slot="s01", attempt_id="a1"` and post `slot="s07", attempt_id="a9"`, same `session_id` | `pass` |
| E11 | P6: a row object without `battery_brackets` through the fence's predicate | `AttributeError`, which is not in `inspect`'s caught set `(Refused, OSError, ValueError, KeyError, TypeError)` |
| E12 | Controller event vocabulary: `controller.py:2373/2376` (`_buffer_event("stage_started"/"stage_completed", name, …, metadata)`) and `salvage_dangler.py:145-149` | These match `authenticate_bundle`'s `event_type` / `phase` keys, so the gap-fill's events are addressed by the names the controller actually writes. |
| E13 | Production `observe(` callers under `joulewise/` and `scripts/` | Six sites, all written as `battery_float.observe` or `_battery_float.observe`; the sweep sees all six today. |

## Findings

### B-1 BLOCKER — the quiet span is unruled, and the seat's choice refuses every network-time-refusal envelope

**Where.** `joulewise/battery_float.py` `authenticate_quiet_session`:

```python
span = (floor(start_stamp.monotonic_before_s·1e9), ceil(end_stamp.monotonic_after_s·1e9))
```

On any `KeyError` the span becomes `(None, None)`, and `authenticate_pair` then books both phases as "outside measured span".

**Contract.**
- Text 2(f) applies "when `span` is given".
- The gap-fill `20-ruling-bundle-span.md` rules the **bundle** span only.
- No text or ruling names the quiet span fields, the seconds-to-nanoseconds conversion, or the behaviour when a stamp is absent.
- Seat report 10 raised NEEDS_RULING for the bundle domain only, and neither report lists this as a point where the text could not be applied literally.

The brief's item 6 required every such point to be reported.

**Failure (E6).**
1. The collector's network-time refusal path writes `start_stamp` (`:1072`) and returns at `:1081-1083` without an `end_stamp`, which is set only at `:1163` on the capture path.
2. Text 5 puts both reads on that path, precisely so that the envelope is not a missing battery check.
3. Under this wrapper the envelope is `battery_float_evidence_missing`.
4. Text 6 authenticates every readable envelope "before any exclusion or `continue`" and blanks the whole summary on any non-pass.
5. So one clock refusal voids the QPE-01 night. This is addendum §5 item 1, the refuter's first blocker, re-created in S0.

**Why S0.** S2's scope (text E) excludes `joulewise/battery_float.py`, and S4 comes after the epoch. S2 could only paper over it by inventing an `end_stamp` on the refusal path, which is also unruled.

**Exact fix.** Magistrate gap-fill first, then S0 round 3:
1. Rule the quiet span source and conversion. Recommended:
   - `start = floor(start_stamp.monotonic_before_s × 10⁹)`;
   - `end = ceil(end_stamp.monotonic_after_s × 10⁹)` when `end_stamp` is present;
   - when the session is the network-time refusal shape (`error_class == NETWORK_TIME_REFUSAL`, zero rounds, no `end_stamp`), `end = ceil(start_stamp.monotonic_after_s × 10⁹)`. The envelope measured nothing, so the pair need only bracket the start stamp.
   - Any other absence stays `evidence_missing`, with a distinct reason `quiet span unavailable` that mirrors the bundle wording.
2. Add tests:
   - the refusal-shape envelope passes;
   - a capture-shape envelope without `end_stamp` is `evidence_missing` with `quiet span unavailable`;
   - the quiet span rung sits below the custody, probe, parse and predicate rungs.
3. Also rule the clock-domain statement S2 must honour. Text 5 says "the collector's clock is passed to `observe(monotonic_ns=…)`"; S2 must stamp with the same clock as `Clock.monotonic` and convert by truncation, and T5 should carry a test for that.

### S-1 SHOULD-FIX — the frozen-function pins do not cover what the frozen functions depend on

**Mechanism.** `sha256(inspect.getsource(fn))` covers only each function's own text. The frozen set's behaviour also depends on:
- unpinned module-level helpers: `_unsigned`, `_signed` (sign handling of `InstantAmperage`), `_is_sha256`, `_is_wall_time`, `_session_epoch`, `_git`, `verdict_relative_path`, `render_verdict`, `verdict_record`;
- unpinned constants and regexes: `_REQUIRED`, `_OPTIONAL`, `_UINT`, `_SHA256`, `REFUSAL_TEXT`.

**Failure.** An edit to `_signed`, or to `_is_wall_time` (which `authenticate_pair` also uses), changes what `parse` and `validate_window` decide at every site with no pin RED. The `observe` golden catches only `LIMIT_MA`, `MAX_UPDATE_AGE_S`, `SCHEMA`, `POLICY_ID` and the argv, through the record fields. Text 3's intent is that these functions "do not change before S4". The literal instruction (pin `getsource`) is met, but the pinning does not deliver that intent.

**Exact fix.** In `S0FreezeTests`, compute each frozen function's closure by an AST walk over module-level `Name` loads resolving to a function, class or assignment in `battery_float.py`, and pin the source of every member of that closure too. Put them in the same regenerable `FROZEN_FUNCTION_SOURCE_SHA256` table, so the lead's A309 regeneration is still one table.

A cheaper alternative: pin the bytes of `battery_float.py` from line 1 through the end of `authenticate_committed_verdict`, minus the one `PHASES` insertion. S0 only appends after that point.

### S-2 SHOULD-FIX — the `PairVerdict` construction guard is evaded four ways

**What text 4 says.** It names a "`PairVerdict(...)` call"; `visit_Call` implements exactly that.

**Evasions (E7):**
- alias assignment;
- `dataclasses.replace(v, status="pass", reasons=())`;
- `type(v)(...)`;
- `getattr(bf, "PairVerdict")(...)`.

**Why it matters.** `dataclasses.replace` is the realistic one. It is idiomatic, already used in this repo's tests for `NightKind`, and it turns a refused verdict into `pass` in one call inside an S1 consumer.

**Exact fix.** In `_Checker`:
1. Flag any load of `PairVerdict` (bare name from the from-import set, or an attribute resolving to the module) **except** as the second argument of `isinstance`/`issubclass` or inside an annotation.
2. Flag any `replace`/`dataclasses.replace`/`copy.copy`/`copy.replace` call in a production file that imports `joulewise.battery_float`.

Add the four E7 sources to the self-test as expected violations.

### S-3 SHOULD-FIX — two ruled S1 obligations have no WRITE_SCOPE home once S0 merges (needs a ruling before S0 merges)

This is not a defect of S0's diff against its texts. It is a scope gap that only S0 can close cheaply, because S0 is the last PR before S4 with `joulewise/battery_float.py` in scope.

1. **`authenticate_window_members`.** Text 12 requires `battery_float.authenticate_window_members(members)`, a new function in `joulewise/battery_float.py`. S1's scope (text E) omits `joulewise/battery_float.py`, and S4 is the next PR that may touch it.
2. **`bundle_sha256`.** Text 9 requires "a `PairVerdict` of kind `bundle` carrying `bundle_sha256` = `complete_bundle_sha256`". Text 2's field set has no `bundle_sha256`, and text 4 makes any `PairVerdict(...)` call outside `battery_float.py` a violation. So S1 can neither add the field nor build a carrier.

**Exact fix.** The magistrate rules one of:
- (a) S0 round 3 adds `authenticate_window_members`, and a `bundle_sha256: str | None` field filled by `authenticate_bundle`, which would amend text 2's field list. That needs a cold-gate sign-off because it amends ruled text.
- (b) S1's WRITE_SCOPE gains `joulewise/battery_float.py` for exactly those two items, with the frozen pins guarding the rest.

Either way, record it before S1's brief is cut.

### S-4 SHOULD-FIX — a `check.json` written by pre-S0 code bypasses the fence at publish

`require_fresh_check` (`evidence_night.py:1541`) accepts any fresh `check.json` whose `armable` (or `rehearsal_ready`) is `true`. It does not require a `battery_brackets` row.

**Failure.** A QPE candidate checked with the base code within the 60-minute freshness window before the lead's checkout moves to S0 publish-installs under S0 with no fence. The window is narrow, but it is exactly the moment the fence first matters.

**Exact fix.** In `require_fresh_check`, also require `checked["checks"]["battery_brackets"]["verdict"] == "pass"` and refuse otherwise with `"check.json predates the battery_brackets fence"`. Add one test with a hand-written armable `check.json` that lacks the row.

### N-1 NIT — `authenticate_pair` for bundles with `span=None` skips the span rung, and nothing stops a direct call (E8)

This is the ruled signature, so it is not a defect. S1 consumers are meant to call `authenticate_bundle`.

**Fix.** Either raise `ValueError` in `authenticate_pair` when `kind == "bundle" and span is None`, or have the guard flag any `authenticate_pair` reference outside `battery_float.py`. The latter matches text 4's "wrappers call `authenticate_pair` only" spirit.

### N-2 NIT — rung (c) accepts `exit_code` `False` and `0.0` as success (E9)

`stored.get("exit_code") != 0` is false for both. `observe` writes a real int, so no production record is affected.

**Fix.** Use `type(stored.get("exit_code")) is not int or stored["exit_code"] != 0 or stored.get("timed_out") is not False`.

### N-3 NIT — `authenticate_capture` binds identity only to itself (E10)

The identity is `pre.session_id`; slot and `attempt_id` are never compared, so a pre from one slot and a post from another pass. This matches `validate_window` today, and text 1 rules identity only for `quiet_*` and `bundle_*`. Text 10's ledger digest on `instrument_evidence.json` binds the record in the bracketing use.

**Fix.** For kind `capture`, require `pre.slot == post.slot` and `pre.attempt_id == post.attempt_id`, both non-null.

### N-4 NIT — a `NightKind`-like row lacking `battery_brackets` escapes `inspect` as `AttributeError` (E11)

The failure mode is still closed: `check` raises and no armable `check.json` is written. But the fence row is not journaled.

**Fix.** Use `getattr(row, "battery_brackets", None) is not True`.

### N-5 NIT — T4's "no `skipped` exemption" and the unreadable-kind branch have no dedicated test

The "no skipped" obligation is covered only behaviourally: the QPE and unknown-kind tests assert `verdict == "fail"`. Adding `"battery_brackets"` to the exemption tuple at `:1423` would still pass every test, because the fence never writes `skipped`.

**Fix.** Add a test that injects a `skipped` `battery_brackets` row, or asserts from the source that the exemption tuple is exactly `("machine_quiet", "corecaptured")`. Add one test for the `candidate_payload_kind` raise branch showing `battery_brackets` is `fail`.

### N-6 NIT — the `PHASES` sweep resolves only the names `battery_float` / `_battery_float`

A future `from joulewise.battery_float import observe`, or `import … as bf`, is silently skipped (E13 shows none exist today). Also, a positional `phase` makes `[phase] = …` raise an unpacking error rather than a named failure.

**Fix.** Reuse the consumer guard's alias resolution (`module_aliases`, `bound`), and assert that every resolved `observe` call has a `phase=` keyword.

## Line-by-line conformance (no finding)

- **Text 1.** `PHASES` is exact; the schema id and field set are unchanged; `observe` is not edited (E3). Identity:
  - `quiet_*` binds `session_id` to `session.json["session"]`, the collector's `session_id` (`sample_quiet_predicate_evidence.py:1056`);
  - `bundle_*` binds `metadata.run_id`;
  - both require null `slot`/`attempt_id`;
  - `raw_path` is fixed, and custody reads the fixed path, never the stored one, so a traversal or symlinked stored path cannot redirect the read.
- **Text 2.**
  - `PairVerdict` fields and order are exact, and the status set is enforced in `__post_init__`.
  - Rungs (a)→(f) are in order.
  - Custody raises `CustodyFailure`, never a status, and a structure fault in one phase does not hide custody in the other.
  - Confounded ranks above `evidence_missing`, which ranks above `pass`.
  - The stored `passed` is never read, and `delta_q_mah` is reported only.
  - Span bounds are inclusive, per "≤ / ≥".
- **Gap-fill.**
  - Uses the first `idle_baseline` `stage_started` and the last `idle_drift_sentinel` `stage_completed` `metadata.monotonic_ns`.
  - Requires non-negative, non-bool ints with end ≥ start.
  - The reason `bundle span unavailable` is emitted once, at the span rung only, and after every earlier rung; tests cover custody, probe, parse and predicate precedence and repeats.
- **Text 3.** The ten-function pin table, with values matching the base (E3). The seven-phase golden is byte-identical against base output (E3). The table is one named constant for the A309 regeneration.
- **Text 4.** The allowlist has exactly seven rows, the new one being `authenticate_pair → parse`. There is a self-test for a new function's `parse` reference, a wrapper-calls-core test, and a `PairVerdict(...)` call test with `isinstance` allowed. The guard's evasion gap is S-2.
- **Text 15.**
  - `battery_brackets: bool` is required, with calibration `True` and QPE `False`.
  - The check is placed after `inspect("battery_float")` and after `row = NIGHT_KINDS.get(...)`.
  - It fails unless `row is not None and row.battery_brackets is True`, and it has no `skipped` state.
  - The `:1423` exemption tuple is unchanged; the unreadable-kind branch also fails.
  - A side effect consistent with fail-closed: a failed fence downgrades `corecaptured` to read-only, because the live-actuator gate requires every prior row to pass.
  - Existing downstream-gate tests are re-pointed per test to a patched post-S2 table; none is blanket.
- **Text 17.** The pin covers `parse`, `authenticate_pair` and `validate_window`. "Every site" arguably also means `observe`/`require_pass`, which are reached through `parse`; a one-line `require_pass(observe(...future...))` test would make it literal.
- **Out-of-scope movement.** None (E4, E5).

## Addendum: E2 tail

`python3 -m unittest tests.test_evidence_night tests.test_night_kinds`, run this session at `26ab7234`:

```text
----------------------------------------------------------------------
Ran 178 tests in 667.969s

OK
```

E1 and E2 are both green. The findings above are contract gaps that the candidate's tests do not exercise; the green runs do not disconfirm them.
