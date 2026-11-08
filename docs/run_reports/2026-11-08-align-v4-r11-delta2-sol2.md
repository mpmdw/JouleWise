# ALIGN v4 R11 delta2 — Sol2 review

Branch: `align/2026-11-08-v4-r11-delta2-sol2` (provisioned, initially clean).
Reviewed candidate: `f993b784f`; range `353446ad6..f993b784f`, all 33 changed
paths and targeted execution dependencies. **Verdict: HOLD.** Detailed
findings/dispositions: [r11-delta2-review-sol2.md](../align/squeeze/fanout/r11-delta2-review-sol2.md).

## Result

The two Sol delta modules and the Opus dry-run witness pass. Full WP22 now
passes with the documented collector-death expected failure. New witnesses
find two HIGH exact-candidate problems: the actual `-m joulewise` entry
point and configured R1 wrapper remain unbound, and three launched
calibration scripts are incorrectly amendment-tier. Three MED findings
cover the 22-capture ceiling versus two extra sentinels, ignored untimed
battery-error rows, and the continuity rule being applied to recent
completion evidence. The current DC session-output sealing control passes.

The five-column contrast agrees with independently implemented OLS for
both its coefficient and interval. The full-window oracle remains a legacy
four-column model, so its 0.1 J test tolerance is weaker evidence; no product
estimator defect was established and the exact cited 0.057 J was not
independently reproduced. Pending U3 correctly stays inconclusive and
cannot authorize arming. See the detailed report for limits and repairs.

## Verification

Every module was run in its own process, **sequentially**. Common command:

```sh
python3.13 -B -m unittest tests.align.<module>
```

Synthetic environment: `JW_B5_SYNTHETIC_ONLY=1 JW_REAL_METER_SMOKE=0
JW_WP22_FULL=0 PYTHONDONTWRITEBYTECODE=1
JOULEWISE_HOST_STATE_DIR=/private/tmp/jw-r11-delta2-sol2-review/host`.
The full-window row alone sets `JW_WP22_FULL=1`.

| Module | Tests | Result | Process wall seconds |
|---|---:|---|---:|
| test_r11_delta_sol1 | 8 | OK | 5.071 |
| test_r11_delta_sol2 | 6 | OK | 6.969 |
| test_r1_rehearsal | 74 | OK | 14.138 |
| test_r1_turn_counts_export | 11 | OK | 4.055 |
| test_v4_cadence | 26 | OK | 1.433 |
| test_v4_dc_sealing | 2 | OK | 2.001 |
| test_v4_estimands | 15 | OK | 0.283 |
| test_v4_executed_closure | 4 | OK; completeness limitations in H1 | 9.043 |
| test_v4_kit | 116 | OK | 30.078 |
| test_v4_opus_cold_witnesses | 1 | OK | 19.654 |
| test_v4_receipt_tiers | 7 | OK; misclassification in H2 | 10.770 |
| test_v4_registration | 21 | OK | 59.258 |
| test_v4_topup | 6 | OK; additional cases in M2/M3 | 0.466 |
| test_v4_w1_synthetic | 20 | OK, 14 skips | 33.883 |
| test_r11_review_sol1_witnesses | 5 | OK | 1.452 |
| test_r11_review_sol2 | 4 | OK | 2.299 |
| test_thermal_desk | 25 | OK | 4.140 |
| test_km003c | 16 | OK | 5.136 |
| test_v4_r11 | 27 | OK | 3.399 |
| test_protocol_v4_doc | 6 | OK | 1.102 |
| test_v4_w1_synthetic, JW_WP22_FULL=1 | 20 | OK, 1 expected failure (WP22 F3) | 162.628 |
| **test_r11_delta2_sol2** | **10** | **4 controls pass; 7 failures + 1 error across 6 methods** | **4.847 unittest seconds** |

The last row is intentionally failing-first: H1 has two failing methods,
H2 three failing subtests in one method, M1 raises on the permitted
24-member roster, and M2/M3 each fail one method. The four controls cover
an actually strict path refusing amendments, the 1800 s/old-float boundary,
independent stage-adjusted arithmetic, and nested DC sealing. They pass.
The new witness command exited 1; every baseline command exited 0.

Baseline total: **420 test selections**, comprising 400 ordinary tests
(14 skipped) and 20 full-window tests (one expected failure). Total test
time, including the new module, approximately **382 s / 6.4 min**, below
the twenty-minute limit. No full suite or pytest was used. Baseline
per-process logs and a machine-readable summary remain in the synthetic
temporary directory `/private/tmp/jw-r11-delta2-sol2-review/`; they are not
custodied live evidence or required durable handoff artifacts.

Additional checks passed:

```sh
env PYTHONPYCACHEPREFIX=/private/tmp/jw-r11-delta2-sol2-review/pycache \
  python3.13 -B -m compileall -q joulewise tests
git diff --check
```

The new witness file also parsed with `ast.parse`. No optional MLX import
or native execution was needed for the new tests. No software optimization
was made, so no throughput or byte-identity improvement is claimed.

## Files and commits

* `tests/align/test_r11_delta2_sol2.py` — new synthetic review witnesses.
  Commit **`6cbc76bf2`**, `test(align): add Sol2 delta2 admission witnesses`.
* `docs/align/squeeze/fanout/r11-delta2-review-sol2.md` — detailed review,
  authority/disposition map, bounded uncertainty and next step.
* This run report — command/results record and handoff. The two reports
  are committed together after the witness commit.

No product code, coordination state, kernel tasks or pre-existing files
were changed. No push, merge or deployment.

## Authority, safety and next step

Read local AGENTS/CLAUDE, M0, stop card (NONE), workspace/queue and
Do-Not-Do-Yet sections, orchestration, targeted D-050/D-064/D-161/D-170,
the owning protocol/rulings/dispositions, both original delta reports and
Opus cold review from local Git objects, and origin/main's authority
including fixed-eight item 217. The explicit review brief selected this
task and prohibited full-suite/coordination writes. No additional agent,
external integration, network or weights were used. Forbidden paths and
real restricted directories were not read, listed or probed; absolute
data locators in repo text were not followed. No Block-5 pipeline, real
measurement, host-setting operation, native MLX, quiet-window capture,
or inspection/interference with the running blinded job occurred.

Lead: adjudicate the five findings with Sol1, repair the accepted items,
then run the new witnesses and affected modules at the integrated head,
one process at a time. Resolve the continuous-float evidence plan before
back-to-back windows rely on it. Preserve pending U3, final-roster U6 OC,
B/charge-hold, C/F/T/scorer/dependence, native identity/cache, and live
custody gates. The lead must run the offline tiny-model native modules
outside this sandbox on authorized Metal hardware:

```sh
python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
python3.13 -B -m unittest tests.align.test_r0_mlx_native
```

The native R1 termination/census checks also remain the lead's authorized
host-lane work. No test here closes a live or scientific gate. The review
contains no claim about any sealed outcome and grants no arm authority.
