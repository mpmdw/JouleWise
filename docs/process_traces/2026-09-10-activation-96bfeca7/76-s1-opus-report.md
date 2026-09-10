# 76 — Seat S1 (Opus) report: the derivation-only writer mode

Worktree `/Users/edr/code/JouleWise-wt-s1-writer-derivation`, branch
`feat/2026-09-10-epoch-s1-writer-derivation-only`, base `1e43d1cc` (S2's
derivation-kind ledger sessions). No git state was changed; the lead commits.
No `[QUIET-MAC]` measurement, no live `powermetrics` capture: every capture in
this seat's tests is driven by the fixture sampler
(`tests.test_calibration_exits._install_fake_writer_dependencies`).

**Status: COMPLETE with two named exceptions**, both reported below rather than
worked around silently:

1. **NEEDS_SCOPE** on `docs/contracts/calibration_ledger_append.md` (the
   generated refusal-registry table). Two new `RefusalCode` members means the
   generated block is stale, and `tests/test_calibration_exits.py::
   RefusalInventoryTests::
   test_generated_contract_projection_and_runbook_anchors_are_fresh` compares
   it byte-for-byte against `REFUSAL_INVENTORY`. The two rows to insert are
   given verbatim at the end of this report.
2. **One uncovered clause**: the TRUE branch of `exceeds_prior_level_screen`.
   The test exists and is `@unittest.skip`-ed with the blocker and two
   candidate cures written into the skip reason, so the gap is visible in the
   suite and not only here. Full analysis below.

---

## 1. What landed

### `joulewise/calibration_exits.py`

| Site | Change |
|---|---|
| `:96-98` | `RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED = "calibration_derivation_only_epoch_unchanged"` and `DERIVATION_ONLY_SESSION_KIND_REQUIRED = "calibration_derivation_only_session_kind_required"`, placed in the existing "Public writer/reservation CLI protocol refusals" block after `POWER_POLICY_REQUIRED` |
| `:258-259` | `_DESCRIPTIONS` entries |
| `:301-302` | `_PREFLIGHT` membership — routes both to `phase="preflight"`, `exit_kind="fix-preflight"`, `retry_class="after-correction"`, `night_loss=False`, `terminal_result=READY_TO_ARM` |
| `:359-360` | `_WRITER_COMPONENT` membership — routes both to `component="writer"`, `correction_surface="scripts/validate_powermetrics_fiducial.py"`, `corrected_success="writer_capture_valid_slot_finalized"` |

No new routing branch was needed: both codes fall through the existing
`_PREFLIGHT`/`_WRITER_COMPONENT` `else` arms, which is the convention the
sibling writer refusals already use.

### `scripts/validate_powermetrics_fiducial.py`

| Site | Change |
|---|---|
| `:439-482` new `_derivation_only_screen_basis()` | Calls `_derive_preflight_systematic_screen_s(None, acceptance_path=...)` — so the artifact's bytes, `artifact_role == "issued"`, protocol digest and estimator-code digests are all still authenticated, and only the epoch equality is skipped — then returns `(level_screen_s, {acceptance_id, artifact_sha256, preflight_level_screen_s, epoch})`. Exactly the four keys ruling 46 A1 names. |
| `:1683-1694` parser | `--derivation-only` (`store_true`) |
| `:1700-1709` | clause (e): `--derivation-only` with `--rederive-from` or `--output` refuses `WRITER_BRACKET_REDERIVE_CONFLICT`. Placed **before** the `if args.rederive_from is not None:` branch, which returns 0 on its own. |
| `:1804-1873` | clauses (b)(c)(d): the derivation branch, with the ordinary derivation of `preflight_systematic_screen_s` moved into the `else` arm unchanged |
| `:2330-2347` | `derivation_only`, `screen_basis`, `exceeds_prior_level_screen` written into `evidence_payload` **before** `instrument_evidence.json` is written, so all three are inside the hashed bytes |
| `:2366-2371` | the same three fields into `manifest.json` before it is written |
| `:2389-2395` | disposition guard `preflight_systematic_screen_s is not None and ...`, so a `None` screen yields `valid` or `ordinary-invalid` only |

Clause (a) — "requires `--allow-live`" — is enforced by **ordering**, not by a
new gate: `main`'s existing `QUIET_MAC_AUTH_REQUIRED` refusal at `:1749` runs
before every derivation-only clause, so no derivation-only invocation can reach
capture without live authorization. See §4 for why this is a composition test
and not a mutation-killing one.

`_CaptureLedgerLifecycle` (`:1256-1470`) needed **no change**: S2 already routed
`is_terminal_slot` / `is_derivation_session` off the session's declared shape,
including the suppression of the `slot == "pre"` auto-abort for derivation
sessions (addendum A-1's live-writer half).

### Ordinary path

Byte-for-byte unchanged in behaviour. The only edit on the non-derivation path
is the `preflight_systematic_screen_s is not None and` conjunct in the
disposition expression, which is vacuously true whenever the mode is off. No
existing test's ASSERTION was weakened or rewritten. `tests/test_calibration_exits.py`
gained three additive things: two `WitnessCase` rows, one `writer-derivation-*`
observer branch, and two members added to the closed correction-set literal in
`_execute_case` (see §3).

---

## 2. Ambiguities in the ruling I had to decide

**(i) Refusal ORDER between the epoch check and the session-kind check.**
Ruling 46 A1 gives the empty-stale-field refusal and A7 gives the
derivation-kind requirement, but neither orders them. I put the **epoch check
first**: it is a pure computation over the artifact and the planned epoch and
needs no ledger read, so it is both the cheapest gate and the one whose failure
mode is most fundamental (a matching epoch means the mode itself is a bypass,
regardless of what session shape is offered). Consequences, all deliberate:

- `--derivation-only` on a matching epoch refuses `DERIVATION_ONLY_EPOCH_UNCHANGED`
  even when it is also standalone.
- The standalone and bracket-kind tests therefore supply a **differing** epoch
  via `--identity-epoch-json-for-test`, so the clause under test is provably
  the one refusing.
- Both executed witnesses in `test_calibration_exits.py` stay cheap: neither
  needs a ledger, a session, or a sampler.

Both orderings are fail-closed; nothing reaches capture either way.

**(ii) `screen_basis` key set.** I kept it to exactly the four keys A1 names
(`acceptance_id`, `artifact_sha256`, `preflight_level_screen_s`, `epoch`) and
did **not** add the computed stale-field list, even though it is the mode's
whole justification and I had it in hand. Reason: the block is hashed evidence
and its shape will be read by seat S4's issuer and by the cold science gate;
widening a ruled schema is the lead's call, not the seat's. If the magistrate
wants the stale-field list recorded, it is a one-line addition at `:1861`.
`preflight_level_screen_s` is recorded as the **string** of the Decimal, matching
the artifact's own lexeme-preserving convention.

**(iii) `exceeds_prior_level_screen` comparison basis.** Compared against the
recorded `screen_basis["preflight_level_screen_s"]` rather than against a
separately re-derived Decimal, so the recorded diagnostic and the recorded
basis can never disagree in the hashed bytes.

**(iv) "`evaluate_calibration_bracket` on r6 still reports it stale".** I did
not call `evaluate_calibration_bracket` directly. That call needs a candidate
sequence, a `CalibrationBracketingPolicy`, a bracket binding, and an
authenticated snapshot whose baseline matches the artifact's cutoff — a fixture
that belongs to seat S3's generation-row work and could not be built honestly
inside this seat's budget. Instead the valid-capture test asserts the load-bearing
input to that staleness verdict: the finalized ledger row's `identity_epoch`
differs from the artifact's on **exactly** `["os_build"]` when filtered through
the production constant `ACCEPTANCE_IDENTITY_FIELDS` — which is precisely the
`stale_fields` computation at `calibration_bracketing.py:1533-1538`, so
`freshness_status` is `stale`. **Recommendation for the S3 gate:** the
end-to-end "r6 refuses a derivation row for measurement" assertion should be
required of seat S3, where the fixture already exists.

**(v) A converse fence I built and then REMOVED.** I implemented the mirror rule
— the ORDINARY writer refuses a derivation-kind slot, so a 25G83 capture can
never be judged by r6's level screen through the front door — and it broke
`tests/test_powermetrics_fiducial.py::WriterLedgerIntegrationTests::
test_main_preserves_symlinked_custody_spelling_used_by_reservation`, because the
fence reads the ledger before the test's `_CaptureLedgerLifecycle` double is
reached. That is a real ordinary-path behaviour change, which this seat's brief
forbids, so I reverted it rather than edit the existing test.

**This leaves a real hole and I am flagging it as a finding, not a nit:**
nothing today stops `validate_powermetrics_fiducial.py` without
`--derivation-only` from filling a derivation-kind slot, in which case
`preflight_systematic_screen_s` is r6's `0.032898493715362` and a valid 25G83
capture above it is written `systematic-invalid` — exactly the D-102 cl.2
inversion that ruling 46 V2 forbids, and the same defect addendum A-1 cured on
the recovery path. **Recommended cure (not this seat's to choose):** put the
check inside `_CaptureLedgerLifecycle.begin()`, which already resolves
`session_shape` from the ledger on the bracket path, so no new pre-lifecycle
read is introduced and the existing lifecycle double is unaffected. That is
~10 lines and belongs with seat S2's footprint.

---

## 3. Test double / harness extended

No existing test double gained a FIELD. The two new witness rows reuse the
`_state_writer_protocol` state helper unchanged, and the new
`writer-derivation-*` observer branch builds its own identity fixture from the
witness repo's own acceptance artifact, so the witness is independent of the
bench machine's real `sysctl` values.

One closed literal in the harness had to be extended, and it is worth the
lead's attention because it is a genuine registry CONTRACT, not boilerplate.
`PublicGovernedExitWitnessTests._execute_case` (`:5725-5732` before the edit)
asserts that every refusal whose registry row says `terminal_result =
ready_to_arm` belongs to a closed set of codes for which the test then EXECUTES
the correction and proves the corrected command succeeds. Both new codes are
`ready_to_arm` preflight refusals, so both had to be added to that set — and
the addition is only honest because the correction the harness executes is the
correction the registry row names.

- `DERIVATION_ONLY_EPOCH_UNCHANGED`: the epoch matches, so the operator's
  correction is to DROP `--derivation-only` and capture ordinarily. That is
  literally what `_execute_valid_writer` runs.
- `DERIVATION_ONLY_SESSION_KIND_REQUIRED`: the harness executes the ordinary
  bracket slot that was actually reserved in the witness sandbox. This is the
  weaker of the two demonstrations — the *other* valid correction, opening a
  derivation-kind session and filling its declared slot, is not built in this
  harness. It IS exercised end to end in
  `tests/test_validate_powermetrics_fiducial_derivation_only.py`
  (`test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance`).
  I recorded this split in a comment at the edit site so a later reader does
  not mistake the ordinary capture for the derivation correction.

**This was a real caught defect, not bookkeeping.** My first version of the two
witness rows passed nothing: the harness raised
`AssertionError: <RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED> not found in
{WRITER_BRACKET_ARGUMENTS, QUIET_MAC_AUTH_REQUIRED, POWER_POLICY_REQUIRED}`,
which is the registry saying "you declared a correctable preflight refusal and
never showed the correction." Adding a `RefusalCode` member without deciding
its corrected-success path is exactly the omission that assertion exists to
catch.

---

## 4. Per-clause test and mutation table

Mutation protocol: one term changed per cut, single named test, source bytes
restored and the sha256 re-verified after each cut. Baseline
`scripts/validate_powermetrics_fiducial.py` sha256, current file,
`816a14b594c33be6338d5716f64822212838fe2f4212f4f5ce6711ed3d54ac95`.
The seven cuts below were first executed against the file as it stood while the
reverted converse fence (§2 v) was still present, sha256
`7eb390e4039b6cfe4fe6af17acc2f5b5d9d365afe4883775d5d93337e4284dfa`; M1-M3 were
then RE-EXECUTED against the current file and are reported at the current line
numbers. M4-M6 touch clauses the fence removal did not move.

| Clause | Test | Production call site killed | Mutation | Result |
|---|---|---|---|---|
| (c) matching epoch refuses | `DerivationOnlyPreflightRefusalTests::test_matching_identity_epoch_refuses_because_derivation_only_would_bypass_the_screen` | `main` `:1824` `if not stale_fields:` | → `if False:` | `Ran 1 test in 0.112s` / `FAILED (failures=1)` rc 1 (re-executed on the current file) |
| (b) standalone refuses | `…::test_standalone_derivation_only_refuses_without_a_declared_session_slot` | `main` `:1830` `if not bracket_mode:` | → `if False:` | `Ran 1 test in 0.114s` / `FAILED (failures=1)` rc 1 (re-executed on the current file) |
| (e) `--rederive-from` refuses | `…::test_rederive_from_with_derivation_only_refuses_before_any_replay` | `main` `:1700` derivation/rederive conflict | → `if False:` | `Ran 1 test in 0.112s` / `FAILED (failures=1)` rc 1 (re-executed on the current file) |
| (b) bracket-kind session refuses | `DerivationOnlyLiveCaptureTests::test_bracket_kind_session_refuses_a_derivation_only_capture` | `main` `:1851` `declared_shape["session_kind"] != SESSION_KIND_DERIVATION` | → `if False:` | `Ran 1 test in 21.840s` / `FAILED (failures=1)` rc 1 |
| (d) provenance in hashed bytes | `…::test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance` | `main` `:2337` `evidence_payload["screen_basis"] = screen_basis` | key renamed to `screen_basis_absent` | `Ran 1 test in 21.865s` / `FAILED (errors=1)` rc 1 |
| (d) disposition skips the systematic comparison | `…::test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance` | `main` `:2391` `preflight_systematic_screen_s is not None and` | conjunct deleted | `Ran 1 test in 22.061s` / `FAILED (failures=1)` rc 1 |
| (a) requires `--allow-live` | `…::test_derivation_only_without_allow_live_refuses_quiet_machine_authorization` | `main` `:1749` existing `QUIET_MAC_AUTH_REQUIRED` | **none — composition test, no mutation claimed** | asserts the ordering fence only |
| ordinary path unchanged | the 202 existing tests of the four focused modules, unedited | — | — | green |
| **UNCOVERED**: `exceeds_prior_level_screen == True` | `…::test_a_bound_above_the_prior_level_screen_is_recorded_but_still_valid` | `main` `:2340-2345` | — | `@unittest.skip`, reason inline |

The two new witness cases in `tests/test_calibration_exits.py` are additionally
covered by that module's own exact-set gate
(`test_enum_inventory_and_discovered_executed_witnesses_are_exact_sets_per_class`),
which requires every OPERATIONAL code to have an executed public witness.

### Why the TRUE branch of `exceeds_prior_level_screen` is uncovered

Measured, this session: a fixture-sampler capture yields
`b_fiducial_s = 9.298188781738281e-05`, against r6's level screen
`0.032898493715362` — a factor of ~354. The bound tracks
`SAMPLING_INTERVAL_MS × --time-scale-for-test`, so reaching the screen needs a
time scale of ~0.35, i.e. a ~17 minute capture per test.

Lowering the screen instead is blocked by the artifact's own self-consistency
fence: `_valid_acceptance_bound` (`joulewise/calibration_bracketing.py:676-687`)
requires `max(member values)` quantized to `1e-15` to EQUAL
`preflight_level_screen_s`, `max - min` quantized to `1e-6` to equal
`bracket_screen_s`, and `bracket_screen_s + max_budgetable_excess_s ==
maximum_budgetable_drift_s`. Rewriting the screen therefore means rewriting all
17 member values and both t-quantile predictions consistently — which is seat
S4's issuer, not a test fixture.

Two candidate cures, both outside this seat's WRITE_SCOPE:
(a) generate a synthetic **issued** acceptance fixture from seat S4's issuer,
with a small internally-consistent corpus whose maximum sits below the fixture
sampler's bound;
(b) add a fixture-sampler knob that widens the trace interval without widening
wall time.

I explicitly **rejected** a third option — a test-only `--acceptance-path`
override on the writer. It would let a caller point the mode at an artifact of a
*different* epoch and so walk straight through
`DERIVATION_ONLY_EPOCH_UNCHANGED`. A test seam that can disarm the fence it
tests is not worth the coverage.

---

## 5. Executed runs (exact tails, rc captured in a variable, never gated on a pipe)

New module alone:

```
$ python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only \
      > /tmp/newmod.log 2>&1; RC=$?
RC=0
s......
----------------------------------------------------------------------
Ran 7 tests in 22.819s

OK (skipped=1)
```

Focused modules (excluding `tests.test_calibration_exits`, which is reported
separately below):

```
$ python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only \
      tests.test_powermetrics_fiducial tests.test_calibration_ledger \
      tests.test_docs_freshness > /tmp/focused1.log 2>&1; RC=$?
RC=0
Ran 202 tests in 87.609s
OK (skipped=2)
```

Compile gate:

```
$ python3 -m compileall -q scripts joulewise
compileall rc=0
```

`tests.test_calibration_exits`: see §7.

---

## 6. Footprint

```
$ git status --short
 M joulewise/calibration_exits.py
 M scripts/validate_powermetrics_fiducial.py
 M tests/test_calibration_exits.py
?? tests/test_validate_powermetrics_fiducial_derivation_only.py
```

Exactly the WRITE_SCOPE, minus `tests/test_powermetrics_fiducial.py`, which
needed no edit.

CI needs no registration for the new module: `.github/workflows/ci.yml:66` uses
`shard_tests.discover_test_modules()`, and an unmeasured module is scheduled at
`shard_tests.conservative_unknown_weight()`. Adding a real row to
`scripts/test_timings.json` (measured ~23 s) would improve shard balance and is
a one-line follow-up for whoever owns that file; it is outside this WRITE_SCOPE.

---

## 7. NEEDS_SCOPE

**Path:** `docs/contracts/calibration_ledger_append.md`
**Reason:** it carries the generated block
`<!-- BEGIN GENERATED: calibration-refusal-registry -->`, which
`tests/test_calibration_exits.py::RefusalInventoryTests::
test_generated_contract_projection_and_runbook_anchors_are_fresh` compares
byte-for-byte against `REFUSAL_INVENTORY`. Adding two `RefusalCode` members —
which this seat's brief requires — necessarily makes that block stale, and no
generator script exists in the repo (the projection is asserted, not emitted).
Until the doc is updated that one test fails; nothing else in the module
depends on it.

The two rows to insert, generated from the landed inventory this session, go
immediately after the `calibration_power_policy_required` row (enum order):

```
| `calibration_derivation_only_epoch_unchanged` | `operational` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_derivation_only_epoch_unchanged` | `scripts/validate_powermetrics_fiducial.py` | `writer_capture_valid_slot_finalized` |
| `calibration_derivation_only_session_kind_required` | `operational` | writer | preflight | `correct-preflight` | `ready_to_arm` | `false` | `witness.calibration_derivation_only_session_kind_required` | `scripts/validate_powermetrics_fiducial.py` | `writer_capture_valid_slot_finalized` |
```

The runbook (`docs/phase_2/window_runbook.md`) needs **no** change: the test
only asserts code-value presence for `internal-invariant` records, and both new
codes are `operational`.

`tests.test_calibration_exits` rc and tails: **PENDING** at the time this
report was written. The module runs well past the 600 s tool ceiling (its
witness corpus executes ~190 real writer/recovery subprocesses) and was moved
to the background; the seat's own turn is over before it lands.

What IS proven for that module this session, executed directly rather than
inferred:

```
$ python3 -c '<drive PublicGovernedExitWitnessTests._execute_witness_case for
              the two derivation cases>'
CASE PASS calibration_derivation_only_epoch_unchanged
PASS calibration_derivation_only_epoch_unchanged
CASE PASS calibration_derivation_only_session_kind_required
PASS calibration_derivation_only_session_kind_required
```

Both new executed witnesses pass, including their registry-mandated corrected
success. The remaining expected outcome for the full module is **exactly one
failure**, `RefusalInventoryTests::
test_generated_contract_projection_and_runbook_anchors_are_fresh`, cured by the
two registry rows in §7. **If any OTHER test in that module fails, treat this
report as INCOMPLETE for that module** — the lead should re-run
`python3 -m unittest tests.test_calibration_exits` at the gate and confirm the
failure set is that single row-staleness assertion and nothing else.
