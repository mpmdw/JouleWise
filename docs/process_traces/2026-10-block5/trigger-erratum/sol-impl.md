```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Erratum 3 desk changes and targeted tests are complete; exact item-6 behavior when no authenticated doubling count exists needs a ruling.",
  "workspace": {
    "base_requested": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "base_mode": "exact",
    "head_start": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "head_end": "0699abbb0881ce64b39c46ba07de568cc3848260",
    "upstream_end": null,
    "branch": "lane/2026-10-11-harvest-trigger-scope"
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "joulewise/b5/harvest.py",
    "tests/test_harvest_b5_window.py",
    "tests/test_harvest_b5_trigger_scope.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Item 6 requires a numeric corpus_doubling record but does not specify unavailable-input refusals. The implementation returns null when an authenticated count cannot be computed; all available counts follow the admitted formula.",
      "needs": "Confirm the required item-6 representation for unavailable-input refusals before declaring exact implementation."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The GAMMA gate uses the closest executed synthetic harvest fixture and a G3 runner seam; the full provenance-checker subprocess and live hardware were not exercised.",
      "needs": "Lead owns the complete GAMMA gate and final verification."
    }
  ]
}
```

## Change

The ruling and draft were read before implementation. The ruling’s SHA-256 matched `becbf587bb84a61954060a19dc54f78517c088c8710e514d73bb31af0cdea260`.

All independent authorized implementation work is finished. Changes remain uncommitted, HEAD is unchanged, and `.scratch-fix/` has been deleted. No network, measurement, subprocess agent, claim-window inspection, or out-of-scope write occurred.

The new tests are in [test_harvest_b5_trigger_scope.py](/Users/edr/code/JouleWise-wt-harvest-trigger/tests/test_harvest_b5_trigger_scope.py:1). Test names below refer to that module unless otherwise stated.

| Section D item | Implementation and verification |
|---|---|
| **0 — governance** | Constant at [harvest.py:89](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:89); non-bool numeric, finite, strictly-later test at [harvest.py:4012](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4012). `test_item0_admission_is_finite_numeric_nonbool_and_strict` covers missing/invalid values, equality, later int/float, and BETA attempts 4/5. |
| **1 — scope argument and sealed identity** | Evaluator argument/validation at [calibration_bracketing.py:2118](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2118); wrapper at [calibration_bracketing.py:2855](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2855), forwarding through all five calls. Harvest’s sole call supplies the governed scope at [harvest.py:4610](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4610). `test_every_existing_bracket_fixture_equals_the_pinned_functions` loads the pinned source with `git show`, compares omitted and explicit sealed results on every intercepted existing bracket fixture, compares canonical JSON, and checks absence of new keys. It covers passed and failed/stale results. `test_item1_wrapper_passes_scope_at_every_call_site` and `test_item1_invalid_scope_raises_at_both_entry_points` cover forwarding and rejection. No other caller changed. |
| **2 — own session and unbound fallback** | Validated binding supplies the own session at [calibration_bracketing.py:2497](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2497); fallback at [calibration_bracketing.py:2515](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2515). `test_item2_other_session_and_no_session_are_recorded_at_both_sites` covers another session and no session. `test_item2_unbound_uses_sealed_decisions_whatever_scope` checks systematic, range, and doubling decisions against sealed behavior when unbound. |
| **3 — event-based demotion** | Doubling/range records begin at [calibration_bracketing.py:2594](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2594); systematic observations/session classification at [calibration_bracketing.py:2631](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2631); own-systematic early return at [calibration_bracketing.py:2661](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2661); second-site failing set at [calibration_bracketing.py:2780](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2780). Tests assert another-session systematic passes, proving both failure sites are handled; own-systematic retains the early return; counts 48 and 49 record and pass; byte change still fails. The active second-site set is exactly `{"protocol_or_estimator_byte_change"}`. |
| **4 — remaining failures/order** | Existing checks retain their decision order; return packaging is centralized at [calibration_bracketing.py:2137](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2137). `test_item4_unchanged_refusals_and_order` covers missing/refused/baseline-invalid snapshot, missing/invalid binding, missing/unissued acceptance, incomplete candidates, abandoned observation, unresolved set-aside, stale endpoints, and invalid numeric bound. Separate tests cover identity change, byte change, own-pre screen failure, post binding rejection, and drift. Wrapper tests exercise custody-loading refusal. |
| **5 — complete own-capture cases** | Own-pre screen check remains at [calibration_bracketing.py:2768](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2768); drift ceiling at [calibration_bracketing.py:2818](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2818). Each case is covered below. |
| **6 — return metadata/freshness** | Four scoped keys at [calibration_bracketing.py:2131](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2131); count and ordered event accumulation at [calibration_bracketing.py:2594](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/calibration_bracketing.py:2594). `test_item6_keys_fixed_order_and_ascending_sequences` asserts `(c), (b), (a)` and ascending sequences. Demoted-only successful cases assert `fresh`; item-4 failures assert `stale`. **Unavailable-count refusal representation remains the ruling issue described below.** |
| **7 — flag condition** | Condition remains unchanged at [harvest.py:4626](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4626): status other than passed, or any reason. Governed worked example has no bracket-failure flag; ungoverned stale fixture retains it. No flag code was added, removed, or reclassified. |
| **8 — harvest output/checkouts** | Initialized summary at [harvest.py:4016](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4016), evaluated summary at [harvest.py:4613](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4613), evaluation-file digest at [harvest.py:4624](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:4624), final top-level object at [harvest.py:8140](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:8140), checkout file list at [harvest.py:3888](/Users/edr/code/JouleWise-wt-harvest-trigger/joulewise/b5/harvest.py:3888). Harvest tests assert governed, ungoverned, and not-evaluated objects; null/empty rules; actual file SHA-256; and checkout digest. |

Item 5 case coverage:

- **Pre above screen:** `test_item5_pre_systematic_abort_has_no_bracket_and_no_evaluation` executes the harvest over a synthetic aborted session/exit-12 record and asserts `calibration.no_bracket`, no evaluator call, and `evaluated: false`. It does not execute the measurement chain.
- **Post above screen:** `test_item5_own_post_systematic_emits_both_codes_and_is_not_evaluated` asserts `calibration.capture_invalid`, `calibration.binding_failed`, and no bracket evaluation. `test_item5_post_above_screen_binding_rejected` separately checks binding construction.
- **Either slot below range:** `test_item5_own_low_capture_records_and_passes_in_both_slots` covers both slots and an operative bound below the sealed minimum.
- **Drift still applies:** `test_item5_low_capture_drift_ceiling_still_fails` checks 20.5/36.4 ms and the 15.9 ms drift refusal.
- **Tiny upper rounding gap:** `test_item5_rounding_gap_is_valid_recorded_and_passed` uses exact Decimal values in the specified gap.
- **Both inside range:** `test_item5_inside_range_has_no_own_event`.
- **Own captures count toward doubling:** `test_item3_doubling_at_and_above_48_records_and_passes` includes the bound pair in counts 48 and 49.

The worked-example evaluator test asserts **passed**, **45.031 ms operative bound**, **14.531 ms allowance**, and **2.5 ms drift**. The harvest test asserts the ruling’s complete summary object: governed/window-evidence/evaluated, passed, empty reasons, fresh, the systematic trigger in both trigger lists, count 43/threshold 48, and sequence `[456]`.

Only one existing test was edited: [HarvestCheckoutTests.test_both_records_name_the_commit_the_program_files_and_whether_the_checkout_was_clean](/Users/edr/code/JouleWise-wt-harvest-trigger/tests/test_harvest_b5_window.py:2627).

- Its expected file list now includes `joulewise/calibration_bracketing.py`, as D8 requires.
- It compares checkout cleanliness/status against an independently captured snapshot at checkout-record creation. Required in-tree scratch files otherwise changed during the harvest, making an after-harvest status comparison time-dependent.

Items 10/14, claim consumers, estimator files, `whole_window.py`, scripts, and configuration were untouched.

Tracked `git diff --stat`:

```text
 joulewise/b5/harvest.py             |  40 ++++++++-
 joulewise/calibration_bracketing.py | 159 +++++++++++++++++++++++++++---------
 tests/test_harvest_b5_window.py     |  18 +++-
 3 files changed, 170 insertions(+), 47 deletions(-)
```

The new untracked test is additionally:

```text
 .../null => tests/test_harvest_b5_trigger_scope.py | 748 +++++++++++++++++++++
 1 file changed, 748 insertions(+)
```

## Verification notes

The final targeted run passed **497 tests, with 29 skipped**. The immediately preceding full targeted run also passed. Skips include synthetic-only exclusions of real archive/Git fixtures, unavailable optional fixtures, and opt-in rehearsal work.

The sealed-identity test executes the existing calibration test module internally against both implementations. Its pinned functions use the same fixture helper globals so existing mocks apply consistently; the helper implementation was unchanged.

**Required stale-state gates**

- **Source-less stored verdict / Erratum 2 recovery:** `RecoveryStaleGateTests.test_gate_governed_stale_bracket_and_source_less_recovery` asserts the full window-removing list is **`[]`**. It constructs a stale stored bracket with no endpoints and no launch lineage, validates its evaluation basis, and executes calibration, stored-verdict handling, and survivor recovery/rescreen stages. The stored failure remains disclosure; the governed desk bracket passes. This is a stage-composed synthetic fixture using existing in-memory source helpers.
- **Closest GAMMA-shaped harvest:** `HarvestScopeTests.test_gate_gamma_shaped_stale_window_removing_codes` asserts the full removal list is **`["calibration.capture_battery_unmeasured", "neg8.bound_not_derived", "neg8.screen_failed"]`**. A fresh control produces the same list. These arise from independent fixture gaps: capture/monitor coverage and absent NEG8 bound/reference-screen inputs. The stale state adds `g3.recompute_failed` and `whole_window.not_passed`, both disclosure; it adds no window-removing code and no bracket-failure flag.

The existing helpers lack a complete GAMMA authenticated science/reference campaign catalog, full family identity/launch lineage, and real calibration-capture fixtures. The closest executed fixture uses six science members, GAMMA hazard-pack/full-window G3 arguments, and real harvest handlers. Its G3 runner seam executes a sealed bracket evaluation and supplies the failing F5-2 result; it does **not** execute the complete provenance-checker subprocess. No stale-state removal defect was observed within these executed fixtures.

**Exact test invocations**

All scratch output was captured inside the allowed `.scratch-fix/` directory. The substantive commands were:

```sh
TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_calibration_bracketing tests.test_harvest_b5_window tests.test_harvest_b5_sources tests.test_harvest_b5_p2harv tests.test_harvest_b5_p3harv tests.test_harvest_b5_rehearsal_compare tests.test_bracket_binding_cli > .scratch-fix/baseline.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.WindowEvidenceTests > .scratch-fix/trigger-unit.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.WindowEvidenceTests > .scratch-fix/trigger-unit-r2.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.WindowEvidenceTests > .scratch-fix/trigger-unit-r3.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope > .scratch-fix/trigger-all-r1.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope > .scratch-fix/trigger-all-r2.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope > .scratch-fix/trigger-all-r3.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope > .scratch-fix/trigger-all-r4.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.RecoveryStaleGateTests > .scratch-fix/recovery-r1.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_trigger_scope.RecoveryStaleGateTests > .scratch-fix/recovery-r2.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_calibration_bracketing tests.test_harvest_b5_window tests.test_harvest_b5_sources tests.test_harvest_b5_p2harv tests.test_harvest_b5_p3harv tests.test_harvest_b5_rehearsal_compare tests.test_bracket_binding_cli tests.test_harvest_b5_trigger_scope > .scratch-fix/final-targeted.log 2>&1

TMPDIR="$PWD/.scratch-fix" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_calibration_bracketing tests.test_harvest_b5_window tests.test_harvest_b5_sources tests.test_harvest_b5_p2harv tests.test_harvest_b5_p3harv tests.test_harvest_b5_rehearsal_compare tests.test_bracket_binding_cli tests.test_harvest_b5_trigger_scope > .scratch-fix/final-targeted-r2.log 2>&1
```

| Output | Last result lines |
|---|---|
| `baseline.log` | `Ran 471 tests in 388.555s` · `FAILED (failures=1, skipped=29)` |
| `trigger-unit.log` | `Ran 16 tests in 8.478s` · `FAILED (errors=21)` |
| `trigger-unit-r2.log` | `Ran 16 tests in 17.498s` · `FAILED (failures=21, errors=1)` |
| `trigger-unit-r3.log` | `Ran 16 tests in 20.400s` · `FAILED (failures=1)` |
| `trigger-all-r1.log` | `Ran 24 tests in 79.213s` · `FAILED (failures=1, errors=2)` |
| `trigger-all-r2.log` | `Ran 25 tests in 84.653s` · `FAILED (failures=1, errors=2)` |
| `trigger-all-r3.log` | `Ran 25 tests in 91.276s` · `FAILED (errors=1)` |
| `trigger-all-r4.log` | `Ran 26 tests in 101.884s` · `FAILED (failures=1)` |
| `recovery-r1.log` | `Ran 1 test in 0.882s` · `FAILED (failures=1)` |
| `recovery-r2.log` | `Ran 1 test in 0.882s` · `OK` |
| `final-targeted.log` | `Ran 497 tests in 478.828s` · `OK (skipped=29)` |
| `final-targeted-r2.log` | `Ran 497 tests in 477.651s` · `OK (skipped=29)` |

The first run’s failure was the existing checkout test’s changing scratch-file count. Development failures were corrected fixture issues: receipt indexing, prefix session data, unbound-fixture session fields, mock-call restoration, terminal-pin shape, in-memory hashing/attributes, complete expected GAMMA removal list, and fake-filesystem `lstat` custody support. No production flag or battery-custody check was weakened.

Final inspections passed:

```sh
git diff --check
git rev-parse HEAD
test ! -e .scratch-fix
git diff --exit-code HEAD -- joulewise/reduce.py joulewise/uncertainty_evidence.py joulewise/powermetrics_fiducial.py joulewise/adapters/powermetrics.py joulewise/whole_window.py scripts configs
git status --short --branch
```

HEAD was the requested hash; protected-path diff and whitespace checks were empty. Status showed only the four reported paths. Scratch cleanup used checked file-by-file deletion after the tool rejected `rm -rf`.

## Residual risk

**NEEDS_RULING — item 6 unavailable-count refusals**

The relevant frozen text says:

> “plus four keys under `acceptance.prospective_rederivation`, present with `"window_evidence"` only”

and specifies:

> `corpus_doubling` (`{"count": <the largest per-epoch count of BRK 2544 to 2552>, "threshold": 48}`)

There is no authenticated per-epoch count when the acceptance or snapshot is unavailable/refused, its baseline is invalid, or the declared set-aside list cannot be resolved. The text does not specify the representation for those refusals.

The nearest implemented behavior is `corpus_doubling: null`, retaining the original refusal and decision order. Where authenticated inputs exist, including early binding/candidate refusals, the implementation computes the specified descriptive count after the refusal decision.

**Question:** What is the required item-6 representation when those inputs do not permit an authenticated count?

**Options considered:** retain `null`; treat the numeric-record requirement as applicable only when its inputs exist; or supply a specifically ruled alternative. Inventing a zero count would misrepresent unavailable evidence.

**Recommendation:** confirm `null` for these refused evaluations. The blocked work is declaring item 6 fully exact and acceptance ready. After that ruling, the lead’s next step is final diff review and the complete GAMMA gate.