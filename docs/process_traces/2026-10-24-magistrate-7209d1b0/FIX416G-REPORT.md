```json
{
 "schema": "claude-codex-report/v1",
 "genre": "implementation",
 "status": "findings",
 "completion": "complete",
 "summary": "Implemented FIX-416-G; 25 identical real exports, 13 BYTES smoke exports clear, 24 unchanged arms; only reproduced sandbox census failures remain.",
 "workspace": {
  "base_requested": "bc588a964",
  "base_mode": "exact",
  "head_start": "bc588a964fb292b6dec6cfee1e1d8685b81d9b77",
  "head_end": "bc588a964fb292b6dec6cfee1e1d8685b81d9b77",
  "upstream_end": null,
  "branch": "integrate/2026-10-24-416"
 },
 "pathspec": [
  "configs/b6/flag_catalog_b6.json",
  "configs/b6/packs/bytes-s1-p1/registration.json",
  "configs/b6/packs/bytes-s1-p2/registration.json",
  "configs/b6/packs/bytes-s2-p1/registration.json",
  "configs/b6/packs/bytes-s2-p2/registration.json",
  "configs/b6/packs/bytes-s3-p1/registration.json",
  "configs/b6/packs/bytes-s3-p2/registration.json",
  "configs/b6/packs/bytes-s4-p1/registration.json",
  "configs/b6/packs/bytes-s4-p2/registration.json",
  "configs/b6/packs/bytes-s5-p1/registration.json",
  "configs/b6/packs/bytes-s5-p2/registration.json",
  "configs/b6/packs/bytes-s6-p1/registration.json",
  "configs/b6/packs/bytes-s6-p2/registration.json",
  "configs/gates/hazard_refusals.json",
  "joulewise/b6/export_runs.py",
  "joulewise/hazards/clock.py",
  "scripts/build_b6_flag_catalog.py",
  "tests/b6/test_export_runs.py",
  "tests/hazards/test_clock.py",
  ".scratch-416G/REPORT.md",
  ".scratch-416G/final-shas.json"
 ],
 "unowned_dirty": [
  ".scratch-416C/",
  ".scratch-416E/",
  ".scratch-416F/"
 ],
 "verdict": {
  "implementation": "implemented",
  "acceptance": "ready"
 },
 "verification": [
  {
   "id": "V1",
   "kind": "suite",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_export_runs tests.b6.test_fix416_gates tests.b6.test_blinding tests.b6.test_model_files tests/b6/test_smoke*.py tests.b6.test_catalog tests.test_bytes_plan_trees",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "OK"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?m)^OK"
   }
  },
  {
   "id": "V2",
   "kind": "suite",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates tests.test_bytes_h_session tests.test_fix573i_restore",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "OK"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?m)^OK"
   }
  },
  {
   "id": "V3",
   "kind": "suite",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/hazards -t .",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "FAILED (failures=28, skipped=9)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?m)^OK"
   }
  },
  {
   "id": "V4",
   "kind": "test",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist tests.hazards.test_clock",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "OK (skipped=1)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "(?m)^OK"
   }
  },
  {
   "id": "V5",
   "kind": "other",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/agreement_pair_bound.py withheld",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "withheld: 0 differences"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "withheld: 0 differences"
   }
  },
  {
   "id": "V6",
   "kind": "other",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/agreement_pair_bound.py compressed",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "compressed: 0 differences"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "compressed: 0 differences"
   }
  },
  {
   "id": "V7",
   "kind": "inspection",
   "cmd": "TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/final_audit.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "PASS final audit: 25 identical exports; 13/13 BYTES smoke exports clear; 24 unchanged arm records; probes, agreements, source hashes and scope verified"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "PASS final audit: 25 identical exports"
   }
  }
 ],
 "flags": [
  {
   "id": "F1",
   "kind": "environment",
   "level": "nonblocking",
   "text": "Full hazards: 28 failed assertions in 22 methods, identical on untouched bc588a964; sandbox process enumeration is unavailable. Clock and refusal allowlist pass. All cases are listed in the report.",
   "needs": "Lead may rerun the 22 census-limited methods in an environment with process enumeration."
  }
 ]
}
```

## Change

Uncommitted implementation on `integrate/2026-10-24-416` at `bc588a964fb292b6dec6cfee1e1d8685b81d9b77`. Evidence, campaign archives and APFS clones are under `/private/tmp/fix416g/main`; real data were read only. Recorded disk checks were 70–73 GiB free. No live arm, collection, model load or prohibited system command was run.

1. **BYTES smoke and success evidence.** `joulewise/b6/export_runs.py:129` reads smoke keep prefixes from the checksum-verified archived tree. A reference with neither archived directory nor inventory entry qualifies only through acceptance exclusion or the verified smoke prefix; success in either roster or assessments denies both exceptions. Omitted smoke references are inserted into the exported stage order as `uncollected`, with blank request columns. `tests/b6/test_export_runs.py:379` uses the actual s1-p1 tree with keep 1 in each reference stage: 25 printed references, 4 populated, 21 uncollected. An inline tree without archived digest proof cannot grant the smoke exception; acceptance-excluded uncollected references are also retained if projection omits them. Both success-witness sources and an unverified smoke edit are tested. The exact r4-alpha Opus smoke probe changed from membership STOP to NO STOP. All 13 block-6 smokes changed from STOP to clear through the BYTES branch; the separate 25-archive real-plan replay is byte-identical.

2. **Clock absorption correction.** `joulewise/hazards/clock.py:345` and `joulewise/hazards/clock.py:388` replace the 150-anchor cutoff with exact Fraction arithmetic for every adjacent pair at N ≥ 3: `a_j = (x_(j+1)-x_j) * sum_(i>j)(x_i-xbar) / sum_i(x_i-xbar)^2`, bar `step_ns * (1-a_j)`. N = 2 discloses `clock.step_unmeasured`; the rate, skew and boot-session checks act. N < 2 remains UNMEASURED. Tests cover signed steps, rejected-anchor gaps, exact equality at 1 ms, 1 ns above it, and N = 2 checks. All 24 real arm records (48 judgments) are identical before/after. The allowlist guards and protection text match the new physical test.

3. **Partial reference.** `joulewise/b6/export_runs.py:214` recognizes a missing, unlisted summary only with the harvest's digest-verified `member.bytes_missing` flag whose `observed.files_missing` list contains `summary_metrics.json`. It verifies the rest of the listed bundle, prints `status=member.bytes_missing` and the code, and leaves request columns blank. This physical outcome overrides stale success summaries in assessments/status; a lost listed summary still stops. The Opus partial probe with the required verified harvest flag changed from STOP to 73 rows / 23 populated references / printed missing-summary reason / no stop. Its original acceptance-only version remains a stop before and after.

4. **Gap bar.** `joulewise/b6/export_runs.py:428` uses the lead's 10 µs ceiling: 1% × printed 1 ms duration precision. Its comment derives the impossible simultaneous epoch floor (`10^6 × 2.2e-16 × 1.79e9 s ≈ 0.39 s > 10 µs`) and cites BundleReader's 1e-6 s overlap tolerance in kind. The replayed epoch fixture stopped on 5 and 9 µs gaps before, clears both now, and still stops on 11 µs and 1 ms gaps.

5. **Finder metadata.** `joulewise/b6/export_runs.py:260` ignores exactly files named `.DS_Store`, in both listed and present inputs. The real BY-H2 clone changed from an unlisted-file stop to 73 rows / 24 populated references. Tests retain stops for `.DS_Store.zst`, `.ds_store`, `.DS_Store.backup`, ordinary unlisted files, and the existing raw/instrument input cases.

6. **Catalog and lead text.** `scripts/build_b6_flag_catalog.py:51` and the generated catalog remove the false 150-anchor claim. Only the 12 BYTES registrations' catalog digest fields changed among generated files. Code effects stay 41 EXCLUDE_MEMBER / 19 EXCLUDE_WINDOW / 209 DISCLOSE; BYTES stays 41 / 18 / 210. Plan trees, identity pins, estimator bindings and the pin registry are unchanged; all 16 pin families check current.

**Decisions I made**

- Retain omitted smoke reference rows in registered stage order with explicit `uncollected` status; acceptance's kept observation count stays unchanged. Existing full-session and non-BYTES export rows remain byte-identical.
- Treat success witnesses independently, so an assessment cannot mask a succeeded roster and vice versa, for both uncollected exceptions.
- Treat the verified missing-summary collection outcome as stronger than a stale high-level success status. Require physical absence and no summary inventory entry, verify the remaining bundle, and print the reason even without an acceptance exclusion. Acceptance alone supplies no such proof.
- Retain the older acceptance-only exclusion behavior under D-161: Opus's `accexcl` remains 73 rows / 23 populated references with the same printed exclusion before/after. No operator-adversary refusal was added for it.
- Apply the exact design-based clock correction at every N ≥ 3, with no empirical count or extra tolerance. Apply the lead's printed-precision ceiling on epoch gaps, rather than selecting a bar at this seat.
- Refresh the catalog note and the 12 BYTES digest bindings because the old note made a false measurement claim. The note changes no flag effect. No analysis/twin re-binding or 17+2 campaign trigger applies: both source files are unchanged.

**Registration sentences for the lead**

§5: replace both the earlier 1.010 ms largest-passing-step claim and the N ≥ 150 passage with:

> For N ≥ 3 remaining usable anchors at RAW positions x_i, with xbar their mean, the fitted line absorbs the exact fraction a_j = (x_(j+1) − x_j) · Σ_(i>j)(x_i − xbar) / Σ_i(x_i − xbar)² of a step between adjacent anchors j and j+1. The arm compares each adjacent fitted-residual change with step_ns · (1 − a_j), the registered 1 ms step after that same fit absorption, including across rejected-anchor gaps; the absolute fitted-residual check remains. For N ≥ 2 it never refuses because of the anchor count. At N = 2 the rate, skew and boot-session checks act, and clock.step_unmeasured is disclosed without refusal; N < 2 remains UNMEASURED.

§6: replace the uncollected-reference and status sentences, and add the Finder sentence:

> A planned reference with neither an archived directory nor an inventory entry stays a printed row only when acceptance records its exclusion, or when a digest-verified archived tree records smoke_reduction and the reference lies beyond its stage's smoke keep prefix. Both exceptions are denied when archived assessments or the roster report succeeded; smoke-dropped reference rows print uncollected in registered stage order with blank request columns. A listed partial reference whose missing summary has no inventory entry and whose digest-verified harvest flags.jsonl records member.bytes_missing with summary_metrics.json in files_missing is not succeeded: it prints that reason with blank request columns and does not stop export. This verified collection outcome takes precedence over a stale high-level success status; all other harvested/source status disagreements and missing listed inputs still stop desk export. Files named exactly .DS_Store are ignored as Finder metadata, which no reader consumes; every other unlisted file inside a listed bundle still stops export.

Appendix A and any catalog digest sentence should use `3c4b8280495ecf6dc02445f40ae1c0ea45bb4fe6bd8cb925c05151d7c6762138`. Counts and effects are unchanged. Registration prose is lead-owned in this write scope.

**Real-plan replay**

Every archive used its own `custody/night_plan.json`, shared before/after keys and identical export options. Full paths, plan hashes, CSV hashes and all row dictionaries are in `/private/tmp/fix416g/main/replay/` (`before-replay.json`, per-archive `rows.json`); final results and row dictionaries are in `/private/tmp/fix416g/main/bound-replay` (`normal.json`, `forced.json`). Columns compare exactly, not just numerically.

| Archive | Rows | Populated references | Stops before/after | All columns identical | CSV SHA-256 prefix |
|---|---:|---:|---:|---|---|
| H | 123 | 21 | 0/0 | yes | `df05561b166f` |
| BY-H2 | 73 | 24 | 0/0 | yes | `b675bf831827` |
| r1-alpha-smoke-0 | 4 | 0 | 0/0 | yes | `9edea7fd3ba2` |
| r1-beta-smoke-0 | 4 | 0 | 0/0 | yes | `ed48626fc99a` |
| r1-gamma-smoke-0 | 6 | 0 | 0/0 | yes | `0cb09655e43c` |
| r2-alpha-smoke-0 | 4 | 0 | 0/0 | yes | `5dd210f3885b` |
| r2-beta-smoke-0 | 4 | 0 | 0/0 | yes | `558e7ed3f62e` |
| r2-gamma-smoke-0 | 6 | 0 | 0/0 | yes | `b55548ea0854` |
| r3-alpha-smoke-0 | 4 | 0 | 0/0 | yes | `de2300dd8dc1` |
| r3-beta-smoke-0 | 4 | 0 | 0/0 | yes | `a259a885b24e` |
| r3-gamma-smoke-0 | 6 | 0 | 0/0 | yes | `f3ee577ef175` |
| r4-alpha-smoke-0 | 4 | 0 | 0/0 | yes | `01b4917418be` |
| MT-20261016T2114Z smoke | 4 | 0 | 0/0 | yes | `8775c91416d0` |
| MT-20261017T1735Z smoke | 4 | 0 | 0/0 | yes | `2248aa220065` |
| MT-20261017T2215Z smoke | 4 | 0 | 0/0 | yes | `569eff4feb73` |
| r1-alpha | 125 | 0 | 0/0 | yes | `97897825a359` |
| r1-beta | 125 | 0 | 0/0 | yes | `64f03ab23348` |
| r1-gamma | 107 | 0 | 0/0 | yes | `9613cc7784d5` |
| r2-beta | 125 | 0 | 0/0 | yes | `da9be9baf4ba` |
| r2-gamma | 107 | 0 | 0/0 | yes | `e8b9255f7059` |
| r3-alpha | 125 | 0 | 0/0 | yes | `28c1baf6a8ec` |
| r3-beta | 125 | 0 | 0/0 | yes | `e60e3d052579` |
| r3-gamma | 107 | 0 | 0/0 | yes | `18cb2bec91c1` |
| r4-alpha | 125 | 0 | 0/0 | yes | `564c6349bd7e` |
| BY-H2 early (zero-run) | 0 | 0 | 0/0 | yes | `10bf26181ca0` |

Commands: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/replay.py before` and `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/replay_bound_all.py`.

**Every block-6 smoke through the BYTES branch**

| Archive | Stops before/after | After rows | Populated references |
|---|---:|---:|---:|
| r1-alpha-smoke-0 | 1/0 | 8 | 2 |
| r1-beta-smoke-0 | 1/0 | 8 | 2 |
| r1-gamma-smoke-0 | 1/0 | 10 | 2 |
| r2-alpha-smoke-0 | 1/0 | 8 | 1 |
| r2-beta-smoke-0 | 1/0 | 8 | 2 |
| r2-gamma-smoke-0 | 1/0 | 10 | 2 |
| r3-alpha-smoke-0 | 1/0 | 8 | 2 |
| r3-beta-smoke-0 | 1/0 | 8 | 2 |
| r3-gamma-smoke-0 | 1/0 | 10 | 2 |
| r4-alpha-smoke-0 | 1/0 | 8 | 2 |
| MT-20261016T2114Z smoke | 1/0 | 6 | 0 |
| MT-20261017T1735Z smoke | 1/0 | 8 | 0 |
| MT-20261017T2215Z smoke | 1/0 | 8 | 1 |

Commands: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/replay_smoke_before.py --keep-going` (expected exit 1, 13 stops) and `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/replay_bound_all.py` (exit 0). Final export source binding: `/private/tmp/fix416g/main/bound-replay-source.json`.

**Clock replays**

Opus gap-aligned probes (183 original samples, BYTES s1 limits):

| Dropped gap | Remaining N | Step | Before | After |
|---:|---:|---:|---|---|
| 5 | 178 | 1.05 ms | PASS | REFUSE |
| 20 | 163 | 1.05 ms | PASS | REFUSE |
| 20 | 163 | 1.2 ms | PASS | REFUSE |
| 33 | 150 | 1.05 ms | PASS | REFUSE |
| 33 | 150 | 1.2 ms | PASS | REFUSE |

All 18 short-dwell cases (N = 100, 120, 149; spacing 0.5, 1, 2 s; steps 1.2, 1.8 ms) now refuse with a step reason. Before, 17 passed and one refused on rate alone. Uniform N = 3..184 and every step position on each real H spacing/subset match the corrected bar exactly for an injected 1 ms step. Actual H midpoint steps of 1.05 and 1.2 ms refuse in every scenario below; plain dwells pass.

| H design / rejection sample | N | Largest absorbed share | Plain before/after | 1.05 / 1.2 ms midpoint |
|---|---:|---:|---|---|
| real full | 183 | 0.827436% | PASS/PASS | REFUSE / REFUSE |
| real first150 | 150 | 1.009287% | PASS/PASS | REFUSE / REFUSE |
| real four rejects trial0 | 179 | 1.649538% | PASS/PASS | REFUSE / REFUSE |
| real four rejects trial1 | 179 | 1.659482% | PASS/PASS | REFUSE / REFUSE |
| real four rejects trial2 | 179 | 1.016055% | PASS/PASS | REFUSE / REFUSE |
| real four rejects trial3 | 179 | 1.584570% | PASS/PASS | REFUSE / REFUSE |
| real four rejects trial4 | 179 | 1.654724% | PASS/PASS | REFUSE / REFUSE |
| real random150 trial0 | 150 | 2.469681% | PASS/PASS | REFUSE / REFUSE |
| real random150 trial1 | 150 | 1.983398% | PASS/PASS | REFUSE / REFUSE |
| real random150 trial2 | 150 | 2.323129% | PASS/PASS | REFUSE / REFUSE |
| real random150 trial3 | 150 | 2.436376% | PASS/PASS | REFUSE / REFUSE |
| real random150 trial4 | 150 | 2.286242% | PASS/PASS | REFUSE / REFUSE |

Real arms: 24/24 unchanged; instant PASS 24/24 and series PASS 24/24 in both versions, all 48 complete verdict objects equal. Evidence: `/private/tmp/fix416g/main/clock-replay.json`, `/private/tmp/fix416g/main/fable-sweep.json`, `logs/clockprobe-before.log`, `logs/clockprobe-after.log`. Commands: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/clockprobe.py`, `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/fable_sweep.py`, `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/replay_clock.py`. The before snapshot is byte-identical to bc588a964.

**Other probe results**

| Probe | Before | After |
|---|---|---|
| Opus r4-alpha smoke_as_bytes | membership stop | no stop |
| Opus uncollect (bundle + inventory removed, acceptance exclusion added, success assessment retained) | no stop; contradictory succeeded/excluded row | membership stop |
| Opus accexcl (acceptance alone) | no stop; 23 populated; printed exclusion | identical row / 23 populated |
| Opus original partial, without harvest witness | no verified source status stop | same stop |
| Partial plus digest-verified harvest missing-summary witness | no verified source status stop | no stop; member.bytes_missing; 23 populated |
| Finder .DS_Store in listed reference | unlisted input stop | no stop; 24 populated |
| Epoch gap 5 / 9 µs | stop / stop | clear / clear |
| Epoch gap 11 µs / 1 ms | stop / stop | stop / stop |

Probe commands use `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/probe.py /Users/edr/night-bytes/h2-20261023T144711Z <name>` with `FIX416G_BEFORE=1` for before and `FIX416G_BEFORE=0` for after. Names/logs: `uncollect` → `uncollect-final`, `accexcl-before`/`accexcl-after`, `partial`/`partial-original-after`, `partial-witness-before`/`partial-witness-after`, `dsstore-before`/`dsstore-after`. Clones are APFS `cp -c` copies under `/private/tmp/fix416g/main/probes`, never originals. Gap command: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/gap_probe.py`. The exact r4-alpha smoke command and all cause text are preserved in `logs/smoke-before.log` and `logs/smoke-after.log`.

**Agreement and checks**

| Campaign | Compared | Equal | Under bar | Above bar | Diagnostics compared / different |
|---|---:|---:|---:|---:|---:|
| withheld | 219549 | 214754 | 4795 | 0 | 68146 / 690 |
| compressed | 262385 | 256732 | 5653 | 0 | 84106 / 566 |

The final campaigns ran after the catalog refresh. The earlier pair also had zero above-bar differences. Small equal/under-bar/diagnostic count variation follows newly drawn blinding keys; those diagnostics are not a new agreement bar.

| Check | Result |
|---|---|
| Required B6 modules + all test_smoke* + catalog + plan-tree tests | 122 tests, OK |
| bytes_gates + bytes_h_session + fix573i_restore | 75 tests, OK |
| Final export/order guards + refusal allowlist | 75 tests, OK |
| Clock + refusal allowlist | 75 tests, OK, 1 skip |
| Full tests/hazards | 326 tests; 28 baseline-only failed assertions; 9 skips |
| Same 22 failing methods on untouched bc588a964 | 22 methods; same 28 assertions; 0 errors |
| Catalog generator, BYTES generator, all pin families | current; 16 pin families pass |
| Final evidence/scope/source audit | pass |

Exact commands are in the envelope and the individual replay notes. Generator checks: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/build_b6_flag_catalog.py --check`, `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check`, `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/repin.py --check`. No full `tests.test_bytes_analysis`, `tests.test_bytes_agreement` or `tests.test_bytes_coverage_map` suite was run; only the requested two agreement campaigns used the agreement module's helpers.

**Final SHAs**

HEAD start/end: `bc588a964fb292b6dec6cfee1e1d8685b81d9b77`. No commit or branch operation was made. Full file manifest: `.scratch-416G/final-shas.json`.

| Changed file | SHA-256 |
|---|---|
| `configs/b6/flag_catalog_b6.json` | `3c4b8280495ecf6dc02445f40ae1c0ea45bb4fe6bd8cb925c05151d7c6762138` |
| `configs/b6/packs/bytes-s1-p1/registration.json` | `a674066a642aaceee85f492a1c512c805a913ec68375bf9d043ec9d535f5fb94` |
| `configs/b6/packs/bytes-s1-p2/registration.json` | `60c02e71f3883c0fdf8aa63837aa1c4221fd53fa0e815e65e8844085f993eb93` |
| `configs/b6/packs/bytes-s2-p1/registration.json` | `edb023bd40788cbbc4ef1f8c3a4792306cf1c1708a43e8e175d7e6100d805a2e` |
| `configs/b6/packs/bytes-s2-p2/registration.json` | `616ea51e664d095f95a63604218289d847938dce3728d436d9ff157f0f664993` |
| `configs/b6/packs/bytes-s3-p1/registration.json` | `697dca03b1e5e6e0097f6422a2b1d3a6ee5311ca209d5a88718b8f83de7a8ced` |
| `configs/b6/packs/bytes-s3-p2/registration.json` | `4ebbe4eb48e9792e72773d8a032d18e50583f0b1c56e19411170ad3e781afa5e` |
| `configs/b6/packs/bytes-s4-p1/registration.json` | `6cd842913da1dde15fef3869562e001d4eccebac792ab13e24200455614be65a` |
| `configs/b6/packs/bytes-s4-p2/registration.json` | `8e8b8beb187610bdddf1237f7d7f8039682be81e9d6c0dbf433943a49d4e0ff0` |
| `configs/b6/packs/bytes-s5-p1/registration.json` | `5fd6975f5fad99ff908535ee810b691a72869be15aec851dfdde0b68844807b7` |
| `configs/b6/packs/bytes-s5-p2/registration.json` | `ab67c91fbcf034e72883095d7d8b0ab56c5fc9eb4600fb1343032dab26756542` |
| `configs/b6/packs/bytes-s6-p1/registration.json` | `deb0dd403f46d0cd62e3736f3b1ecaff44c66bfd0900ebf60b28c4dcc8cbd0a7` |
| `configs/b6/packs/bytes-s6-p2/registration.json` | `195130db1d4685f14224d2627312c0de101a35195a5a28bab094a8edc4a49bb9` |
| `configs/gates/hazard_refusals.json` | `e582a35e8210958f5301cbed85dc1c7afce2a8896897d94cb0ca18a22172e382` |
| `joulewise/b6/export_runs.py` | `abe9a6ac21354745b4a10b484f7c97281c8f4b61c9e2fd71ac980eed4e383ebe` |
| `joulewise/hazards/clock.py` | `f15e60cf0d2a203c46d429093088cb3e21de3e5e145b285a07bdfb829dffecc9` |
| `scripts/build_b6_flag_catalog.py` | `57c59ed9f53e900b48ae6df4c070d7e1d935fef18cdc403617aca3a00bd42076` |
| `tests/b6/test_export_runs.py` | `6e31fae9533ea3cff97c4d81fa47da04ce4bf54507ab37d20245845b4a7add0c` |
| `tests/hazards/test_clock.py` | `534a83b3dc0468733eae17e78d57c45675bf2bdb8d715085b357d9cdbc5031b6` |

Unchanged analysis SHA-256: `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`. Unchanged twin SHA-256: `25aa36082c11402cf042103257e83de36eca77c1d70d47876bd58f4c8bd117a9`.

## Verification notes

The 28 full-hazards assertions reproduce exactly on the untouched base. The sandbox cannot enumerate the capture process group: `census_exit_3`, `sysmond service not found`, `pgrep: Cannot get process list`. Arm fixtures therefore stop at instrument cleanup before the later condition each test expects. This is a verification limitation, not live hardware evidence. The following 22 methods are affected (all under `tests.hazards`); `unmeasured_refuses...` has five module subtests and `failed_read...` has three failure-mode subtests, accounting for the 28 assertions:

- `test_arm.ArmTests.test_a_battery_current_that_starts_during_the_dwell_refuses_at_the_final_read`
- `test_arm.ArmTests.test_agent_that_starts_during_the_dwell_gets_no_go`
- `test_arm.ArmTests.test_block6_plan_holds_above_its_registered_rate`
- `test_arm.ArmTests.test_charging_that_starts_during_the_dwell_refuses_at_the_final_read`
- `test_arm.ArmTests.test_clock_step_during_the_dwell_refuses`
- `test_arm.ArmTests.test_contending_daemon_times_the_dwell_out`
- `test_arm.ArmTests.test_frequency_word_change_at_the_end_of_the_dwell_is_diagnostic`
- `test_arm.ArmTests.test_go_records_a_clean_census_taken_after_the_final_reads`
- `test_arm.ArmTests.test_go_records_the_smc_current_beside_the_registry_cross_check`
- `test_arm.ArmTests.test_network_time_off_output_is_recorded_not_judged`
- `test_arm.ArmTests.test_quiet_float_mac_arms_go_in_the_registered_order`
- `test_arm.ArmTests.test_record_only_collectors_never_change_the_decision`
- `test_arm.ArmTests.test_unmeasured_refuses_at_arm_only_for_the_instrument`
- `test_arm.ArmTests.test_without_the_smc_the_arm_judges_the_registry_and_records_the_fallback`
- `test_arm_identity.ArmIdentityTests.test_empty_epoch_list_never_refuses`
- `test_arm_identity.ArmIdentityTests.test_failed_read_is_recorded_and_never_refuses`
- `test_arm_identity.ArmIdentityTests.test_judged_identity_proceeds_to_go`
- `test_arm_identity.ArmIdentityTests.test_no_expected_epochs_reads_no_identity`
- `test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module`
- `test_instrument.CadenceProbeTests.test_block3_interactive_capture_at_130_ms_passes`
- `test_instrument.CadenceProbeTests.test_privilege_prefix_is_prepended_to_the_adapter_command`
- `test_instrument.ProductionCommandTests.test_timeout_kills_the_capture_group`

Comparison command: `TMPDIR=/private/tmp/fix416g/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416g/main/scripts/compare_hazard_baseline.py`. Full artifacts: `/private/tmp/fix416g/main/hazards-baseline-comparison.json`, `baseline-census-result.json`, `logs/hazards-required.log`, `logs/hazards-baseline-census.log`. No sandbox bypass or safety-rule change was made.

The supplied Fable report preserves the §C sweep description but no random seed; its reproduction uses deterministic seed 416. The exact absorption identity is checked at every step position independently of a seed. Initial negative Opus harness runs caught Exception while StorageStop derives from BaseException, so they exited 1 with the expected printed stop; their raw logs are retained. The scratch harness now catches BaseException to record explicit probe outcomes. Production CLI exit-5 behavior remains covered by the passing export/storage tests.

Next exact step: the lead reviews this uncommitted diff, applies the supplied §5/§6 sentences and Appendix A digest, performs its final verification, and commits.
