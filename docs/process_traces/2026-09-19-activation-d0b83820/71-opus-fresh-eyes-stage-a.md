# Record 71 — fresh-eyes review (gate-ledger row 10) of the Stage A post-review commits (Opus, fresh seat, 2026-09-19 ~15:0x–15:3x PDT)

Scope: `git diff 087bf3af 12dcc3f5` on `feat/2026-09-19-stage-a-evidence-executor`
(fix round 1 `6cbd84e4`, round 2a `0b36fba6`, round 2b `12dcc3f5` = HEAD), read
in a detached worktree at HEAD. Independent of record 61 (different seat); its
findings were read only to know what the fix rounds claimed to close.

## Verdict

**NO BLOCKERS. Mergeable.** 2 should_fix, 4 nits — none of them blocks the PR;
all are cheap and can land in this branch or as queue rows.

The three items the fix rounds were accepted to close are executed and hold:
the courier ALWAYS runs on every path I could construct (8 of 9 below, the 9th
pre-existing), the chain continues on the frozen cadence after a failed
envelope, and both generated ARM-RETRY-POLICY fences are byte-exact.

## What I executed

**1. Courier-always-runs.** Nine end-states driven through the REAL
`run_night.run_courier` with a real fake-transport binary (an executable zsh
script that writes `courier.heartbeat`/`courier.sent`; `Popen` NOT mocked), each
on a fresh `EvidenceFixture` with a gate-authenticated receipt
(`/tmp/magistrate-d0b83820/opus-fresh-stagea/courier_paths.py`):

| end-state | attempted | sent | cleanup record | prompt names the record |
|---|---|---|---|---|
| success, executor record present | 1 | yes | read, not rewritten | yes |
| pre-execute refusal (no journal) | 1 | yes | written, proven | yes |
| cleanup unproven | 1 | yes | unproven, preserved | yes |
| non-evidence receipt + wrapper missing | 1 | yes | none (correct) | no |
| corrupt `receipt.json` | 1 | yes | none | no |
| malformed process journal | 1 | yes | `cleanup_proven:false` + error | yes |
| `chain.started` absent | 1 | yes | none | no |
| own pgid journaled | 1 | yes | refused by identity guard | yes |
| night dir not writable | RAISES | — | — | — |

The last one raises `PermissionError` in `_acquire_courier_lock`
(`night/courier.lock`), NOT in any code this diff touched — the same raise
exists at `087bf3af`. Out of scope, noted for the queue.

**2. Continue-on-envelope-failure (B1).** Read at
`quiet_predicate_campaign.execute()`: `scheduled = first + (index - 1) *
protocol["envelope_s"]` is absolute, and the collector's own deadline is
`scheduled + duration_s` (`sample_quiet_predicate_evidence.py:757-758`), so a
late-launched collector still ends at its scheduled boundary — no cadence drift
propagates past the envelope that absorbed the delay. Worst case (a collector
that hangs to the `envelope_s + 30` wait timeout, rc 124, plus ≤ 30 s cleanup)
costs its own envelope and start-drifts the next one only; 10 of 12 remain,
above the minimum 8. `consecutive_cleanup_failures = 0 if proven else +1;
>= 2 -> raise` is exact: one isolated failure continues, the second consecutive
one aborts. No off-by-one. `tests.test_quiet_predicate_campaign` (incl.
`test_envelope_three_collect_error_continues_frozen_cadence_retains_eleven`,
`test_isolated_cleanup_unproven_continues_but_two_consecutive_refuse`) OK.

**3. Frozen protocol.** `validate_protocol` now compares the candidate for
EQUALITY against `frozen_protocol()`, which itself refuses unless the file's
sha256 equals `night_gate.QPE01_PILOT_REGISTRATION_SHA256` — a missing key is a
mismatch, so it refuses; there is no `.get(key, default)` anywhere on the
protocol object (all reads are bracket access). Tracked-file digest
`f59804a9…6da6f6` equals the constant at `night_gate.py:47` (`shasum -a 256`,
executed). Serialized-table pin exists:
`test_ruled_registration_serialization_requires_dated_ruling_amendment`.

**4. Generated blocks (round 2b).** Executed `arm_retry.render_policy()` and
searched both documents for the rendered bytes: `NIGHT_HANDBACK.md` True,
`derivation_night_runbook.md` True; exactly one fence per document. The two
moved probe-diagnostic rows are byte-identical to `git show
087bf3af:docs/process/NIGHT_HANDBACK.md:125-126` (grep of both). The
"or, for an evidence payload, the sealed manifest, harness and registration
digests" sentence was already outside the fence at the base (line 572 → 590,
unedited). The ruled-registration clause moved verbatim, with two NEW sentences
appended about the serialization pin — an addition, not an edit to the moved
text; accurate, see nit N3.

**5. Regression honesty (three mutants on a `/tmp` copy, `.git` excluded).**

| mutant | regression | result |
|---|---|---|
| restore `run_courier`'s early `return {"attempted": 0, …}` | `test_cleanup_residue_is_reported_and_does_not_suppress_courier` | FAILED ✓ |
| restore `process_groups` raising on a missing journal | `test_preexecute_manifest_mismatch_writes_typed_refusal_and_courier_runs` | FAILED ✓ |
| re-anchor the interior to the collector's actual start | `tests.test_sample_quiet_predicate_evidence` (1 failure of 57) | FAILED ✓ |

None vacuous.

**6. Modules run at HEAD** (`.venv/bin/python -B -m unittest`): `test_night_gate`,
`test_arm_retry`, `test_gen_evidence_night`, `test_quiet_predicate_campaign`,
`test_git_fixture_maintenance`, `test_sample_quiet_predicate_evidence` — OK;
`test_run_night` — 197 tests, OK (117 s).

## Findings

**S1 (should_fix) — an `ImportError` inside the courier guard still suppresses
the courier.** `scripts/run_night.py:_evidence_cleanup_error` catches
`(OSError, ValueError, KeyError, TypeError)`, but its body does two deferred
imports (`from joulewise.quiet_predicate_campaign import cleanup_record,
write_refusal`, and inside `cleanup_record`, `from
scripts.sample_quiet_predicate_evidence import write_json` plus `from
scripts.run_night import _write_driver_refusal` in `write_refusal`). `ImportError`
is in none of those classes. Executed counterfactual: patch `cleanup_record` to
raise `ImportError` on the SUCCESS path and call the real `run_courier` →
`COURIER SUPPRESSED BY ImportError`, no launch. This is the fourth instance of
the class the round ruled out. Call site: `run_night.py:1244-1270`. Cure: the
function now only produces a diagnostic string, so a bare `except Exception as
exc: return f"evidence outcome/cleanup unavailable: {exc}"` is strictly safer
than the tuple. (Note: the deferred `from scripts.run_night import …` also
re-imports the driver as a second module object when it runs as `__main__` — a
pre-existing pattern, `quiet_predicate_campaign.py:128`, not new here.)

**S2 (should_fix) — a malformed `evidence_outcome.json` no longer triggers a
refusal document.** The base checked `outcome.get("outcome") not in {"complete",
"refused"}`; HEAD checks only `if not isinstance(outcome, dict)`
(`run_night.py:1256`). Counterfactual: the chain writes `{}` or
`{"outcome": "garbled"}` → the file is accepted as an outcome, no
`_write_json` overwrite, no `write_refusal`, and the courier is asked to read a
file that says nothing. Cure: keep the widened membership test —
`outcome.get("outcome") not in {"complete", "partial", "refused"}` — instead of
dropping it.

**N1 (nit) — half of triage S4 is ruled but not installed.** 61a S4 ruled BOTH
the serialization pin AND "each table entry's `ruling` names a record path under
`docs/process_traces/` that exists". Only the pin shipped; the test comment
(`tests/test_night_gate.py`, "Record-path existence awaits the lead-owned
traces") explains the gap away in-place, where no later reader will see it as
debt. Queue it or add the existence assertion.

**N2 (nit) — a test name promises more than it proves.**
`test_ruled_registration_serialization_requires_dated_ruling_amendment` pins a
digest; nothing in it can require a *dated* comment. `…_serialization_is_pinned`
is the honest name.

**N3 (nit) — `busy_cores` and `clean_machine_busy_cores` are the same value
under two keys.** `pilot_summary` sets both to `harness.quantiles(clean_busy)`
(`quiet_predicate_campaign.py:~418-421`) while documenting them differently
(`busy_cores_role: covariate_only; never excluded` vs
`clean_machine_definition: envelopes passing census, AC and thermal hard
probes`). Either drop one key or make `busy_cores` the all-envelope
distribution the README's first paragraph still implies.

**N4 (nit) — constants named in strings that the protocol file can now
change.** `causes.append("sized_pairs_above_24")` and
`"block_two_upper_bound_above_1_J"` hardcode 24 and 1 J while the thresholds are
read from `protocol["sizing"]["maximum_pairs"]` / `["delta_j"]`; likewise
`raise ValueError("window_max_s must equal the frozen protocol's 9000 s")`
after comparing against `protocol["window_max_s"]`. These are exactly the
strings that will lie the day the registration is re-ruled. (Also
`entry.get("collector_exit", 0)` and `entry.get("cleanup", {})` in
`pilot_summary` default a MISSING key to "clean", the only lenient reads left in
a function whose protocol reads are all strict.)

## Merge-ability prune

No dead code, no leftover imports (`re` moved to module scope and is used by
`hard_exclusions`; `subprocess` added to `night_gate` is used by the new
`except`), no duplicated helpers beyond N3, no orphaned parameters
(`size_block_two`'s `delta_j=1` → `protocol=None` is updated at its only
caller). `_courier_argv` re-derives `custody_root / "night/evidence_cleanup.json"`
rather than taking `night_dir`; harmless, one path literal in two places.

## Commands run

`git diff 087bf3af 12dcc3f5` (by path); `shasum -a 256
configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json`;
`arm_retry.render_policy()` byte-containment in both documents; `git show
087bf3af:docs/process/NIGHT_HANDBACK.md` grep of the moved rows;
`/tmp/magistrate-d0b83820/opus-fresh-stagea/courier_paths.py` (nine courier
end-states, real fake-transport binary); the ImportError probe; three mutants
under `/tmp/magistrate-d0b83820/opus-fresh-stagea/mut/`; the seven unittest
modules above. Nothing written outside
`/tmp/magistrate-d0b83820/opus-fresh-stagea/` and this file; read-only git only.
