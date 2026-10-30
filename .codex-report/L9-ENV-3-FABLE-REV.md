VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-3-FABLE-REV: blocking review of lane L9-ENV-3 (analysis-side inverted-corner clamp)

Reviewed: `origin/main` (`7ebb7db2a`) ... `3e4d359c2` on `lane/2026-10-30-l9-env-analysis-clamp`
(`joulewise/whole_window.py`, `tests/oracle_l9_env_2_reduce_clamp.py`,
`tests/test_whole_window_inverted_corner_clamp.py`; `.codex-report/L9-ENV-3.md` read as claims).
Oracle: `e1b3a0510` (`lane/2026-10-30-l9-env-clamp`, L9-ENV-2's patched `reduce.py`).
Review branch `review/2026-10-30-l9-env3-fable-rev`, this report and `.codex-report/l9-env3-fable-rev/`
(probe scripts, probe logs, mutant logs, suite tails) are the only writes. Synthetic data only
(`JW_B5_SYNTHETIC_ONLY=1`); no real block-5/6/BYTES data was opened or searched. Full history was
fetched (`git fetch --unshallow`), so the `git show <sha>` history tests that errored for the seat ran here.

## Summary

The lane does what Ed's ruling asks, and nothing more, on every check I could execute:

- **R1 oracle.** My own 34,064-case sweep (`probes/r1_oracle_sweep.py`): the analysis function equals
  e1b3a0510's function bit for bit (dict equality plus float sign plus `json.dumps` bytes) in every case,
  and equals origin/main's reduce wherever reduce defines an envelope. 14,469 inverting-defined cases,
  16,123 non-inverting, 3,472 `None` (guards, coverage, no overlap, invalid bounds), 9,614 cases with
  `point_j == lower_j == upper_j`, 1,482 with `point_j == lower_j`. Covered: interval and point traces,
  flat/random/zero/bump power, epochs 0, 1.7e9 and 1.78e9, durations 0 to 10x `2*edge`, `2*edge` at
  +-k ulp at epoch scale (both the duration and the endpoint rounded), multi-window contributions in
  both orders, two contributions, every `None` guard incl. reversed unshifted windows, zero-length
  unshifted windows and negative power. Zero mismatches.
- **R2 mirror.** On the real 0.5.2 fixture (`_build_v052_bundle`: powermetrics raw + suite shape) and on a
  real 0.6.2 fixture (`_install_axi_shape`: the committed AXI event-v2 fixture bound to the same
  powermetrics bytes), at 9 and 6 operative bounds respectively (`probes/r2_r4_fixture_probe.py`,
  495 checks): every pointer reduce records is produced by the mirror in reduce's order, and reduce's
  own function on the mirror's `(curve, windows)` reproduces the recorded envelope byte for byte; every
  pointer reduce omits is also `None` through reduce's function on the mirror's windows; the clamp adds
  a pointer exactly when the clamped function defines one, with that envelope; the whole re-derived
  summary is dict-equal to e1b3a0510's re-derivation at every bound on both wires (JSON-byte-equal
  except the case in F2). A second probe (`probes/r2_v062_structural_probe.py`) compares the mirror to a
  literal copy of `_reduce_v060`'s grouping and of `_reduce`'s `_energy_anchor_envelopes_v05`
  arguments on 300 random multi-source / multi-request / overlapping-window 0.6.2 shapes and 300
  random multi-interval / multi-item / block / level 0.5.2 shapes: zero mismatches. No pointer whose
  window set differs from reduce's mint was found. Frozen 0.5.1/0.6.1 bundles: the clamp
  short-circuits on `reducer_version` (probed by relabelling a summary); I did not locate a frozen
  powermetrics bundle fixture, and none is needed for that path.
- **R3 scope.** `reduce.py` and the other three `ESTIMATOR_CODE_PATHS` hash to the pinned origin/main
  digests (`7b9c0d28...`, `bcdfeec0...`, `b583f35a...`, `70f47086...`). On both fixtures the branch's
  `reduce_bundle` output is JSON-byte-identical to a fresh execution of origin/main's `reduce.py` bytes
  and to the stored mint. Static callers of the new functions: only `AuthenticatedConsumptionSession._prepare`
  (`whole_window.py:1829`). No module-level mutable state (two constants). `reduce.py`,
  `controller.py`, `calibration_bracketing.py`, `bundle_read.py` do not import `whole_window`;
  `b5/harvest.py` imports it for verdict validation only and never constructs a session. See F3 for the
  full reach of the session.
- **R4 gate re-stamp.** For every clamped pointer the gate loses exactly `anchor_energy_envelope_unrecorded`,
  gains exactly `anchor_energy_envelope_exceeds_quarter_metric`, keeps every other reason, stays
  `eligible: False` (outer and inner `windows`), and equals the oracle's gate; every other gate (gross
  family, non-clamped members) is byte-identical to reduce's. A genuinely missing pointer (prefill or
  gross popped) still refuses exactly `('anchor_energy_envelope_unrecorded',)` (seat test, re-run).
  Tampering a recorded envelope by one ulp, a recorded group pointer the mirror does not know, a prefill
  gate without the `unrecorded` stamp, a prefill gate with `eligible: True`, an inner window without the
  stamp, a non-mapping envelope map, an unreadable path, a failed or frozen summary: each returns the
  input summary object unchanged. With the real `_classify_precheck_refusals` (the seat neutralised it)
  the clamped prefill path carries `exceeds_quarter_metric` as a *local* refusal where it carried
  `unrecorded` before; global classification is equal old/new/oracle at every bound. Eligibility does
  not loosen: `floor_extraction.py:2255-2297` recomputes the quarter-metric gate from the envelope itself
  (lower 0 => half-width >= point => refuses) and `analysis_engine/claims.py:69-70` treats both reasons
  alike. Exception: F1 below.
- **R5 suite.** Whole `tests/b5_analysis` plus all 79 `tests/**/test_*.py` modules that mention
  `whole_window`, `joulewise.reduce` or `reduce_bundle`, each in its own process. Exact tails below.
  Only `tests.test_b5_chain` (21 errors) and `tests.test_b5_chain_prune2` (10 errors, 1 failure) fail;
  both fail identically on an `origin/main` export in this container (`/bin/zsh` absent; sandbox
  process-tree survivor). The seat's `git show` / `bda1c180` history errors do not occur with full history.
- **Mutation.** 18 mutants of `whole_window.py` (table below).

## Findings (ranked)

### F1 (medium, fix before relying on multi-interval phases): a clamped envelope that passes the quarter-metric gate leaves `{"eligible": false, "reasons": []}`

`joulewise/whole_window.py:1168-1194` (`_restamp_clamped_gate`) and `:1312-1327` (its call). The restamp
removes `anchor_energy_envelope_unrecorded`, merges `_anchor_envelope_gate_reasons(clamped, joint)` and
never touches `eligible`. For a single-window phase the clamped envelope has `lower_j == 0`, so the ratio
is >= 1 and `exceeds_quarter_metric` is always merged; block-5 prefill is this case and is correct. For a
phase with several intervals (0.5.2 suite phases, 0.6.2 per-source unions of several requests) where one
short interval inverts and a long one does not, `lower_j > 0` and the ratio can be below 1/4. Then the
reasons list is empty and the gate is left `eligible: False` with no reason (or only unrelated reasons).
Evidence `logs/r4_multiwindow_gate_probe.log`: flat 10 W, g = 0.02 s, windows [0.005 s, 2.0 s]:
origin/main `None`; clamped == oracle (point 20.05 J, lower 19.6 J, upper 20.85 J, ratio 0.0399); clamped
gate reasons `[]`; analysis gate `{'eligible': False, 'reasons': []}`; e1b3a0510 gate
`{'eligible': True, 'reasons': []}`. Consumers disagree on that gate: `_classify_precheck_refusals`
(`whole_window.py:856`) sees no refusal, `analysis_engine/inputs.py:4074` refuses it as
`window_evidence_precheck_missing`. Eligibility does not loosen, so this is not blocking for the block-5
bridge, but the seat's NEEDS_RULING R2 scopes the case wrongly ("only possible for an all-zero-power
window with no joint bound"): it is reachable with ordinary multi-interval phases.
**Fix:** in `_clamp_inverted_operative_envelopes`, compute `reasons = _anchor_envelope_gate_reasons(envelope, joint_bound_j)`
before restamping and, if `reasons` is empty, drop that pointer from `clamped` (leave reduce's
`unrecorded` refusal and no envelope), or return the summary unchanged; add a regression test with a
`[short, long]` phase. Either keeps the gate self-consistent and keeps the stricter reading.

### F2 (low, report accuracy): JSON key order differs from the oracle when reduce recorded no envelope map

`whole_window.py:1281` sets `operative["energy_anchor_shift_envelopes"] = ordered`. `SummaryMetrics.to_dict`
omits the key when the map is `None` (`schemas.py:1818-1819`), so when the unchanged reducer records no
envelope at all (every window fails coverage at a very wide bound) but a short phase still clamps, the key
is appended last and `json.dumps(new) != json.dumps(oracle)` although `new == oracle`. Evidence:
`logs/r2_r4_fixture_probe.log`, `0.5.2 bound=0.199261` (only `/phase_energy_j/decode` clamps; gross
missing). The session refuses such a member anyway (`unrecorded` from the coverage loop), so no
behaviour changes; but L9-ENV-3.md's "equal ... JSON bytes including key order" holds only when reduce
recorded at least one envelope. **Fix:** qualify the claim in the report, or insert the key at its
schema position when absent.

### F3 (low, report accuracy / R3 reach): the clamp is reachable from every session consumer, including `scripts/run_campaign.py whole-window-verdict`

L9-ENV-3.md says the only caller is "the consumption session". True at function level, but
`AuthenticatedConsumptionSession._prepare` is constructed by `scripts/run_campaign.py:8425`
(`_run_whole_window_verdict_locked`, the `whole-window-verdict` subcommand, `MAX_BRACKET` semantics),
`scripts/mint_floor_artifact.py:547,1250`, `scripts/check_window_provenance.py:1048`,
`scripts/produce_b5_disclosures.py:115`, `joulewise/b5_analysis/dry_run.py:1078`,
`joulewise/paper_reported_energy_issuer.py:146` (issuing mode), `joulewise/floor_extraction.py:3171`,
`joulewise/analysis_engine/inputs.py:2029,2125,3799`, `joulewise/window_duration_margins.py:796`,
`joulewise/floor_mint_estimator.py:480`, `joulewise/analysis_manifest_v3.py:3771`. All are consumption
(analysis/verdict/issuing) paths and all run post-mint; none of controller, reduce,
calibration_bracketing, harvest, run_campaign's collection verbs or the mint precheck reaches it, and
minted summaries are unchanged. **Fix:** list this reach in the report so the release checklist knows which
artefacts (verdicts, floor mints, disclosures) will now see clamped operative envelopes.

### F4 (informational): cost and a second anchor derivation per dominated member

`whole_window.py:1221-1231` re-runs `_derive_anchor_context` (raw plist parse) after reduce already did it
inside `_rederive_summary_for_authenticated_fiducial_bound`. Seat O2 notes it; sessions only. No fix needed.

### F5 (informational): seat test gaps that my probes close

The seat's tests exercise 0.5.2 only, neutralise `_classify_precheck_refusals`, and do not cover the
`eligible`-check or inner-window fail-closed branches of `_restamp_clamped_gate`; mutants M09 and the
0.6.2 mutants M11/M17 survive the seat's module and are killed only by the probes here. Suggest adding
the 0.6.2 fixture (`_install_axi_shape`) and the `[short, long]` case to
`tests/test_whole_window_inverted_corner_clamp.py`.

## Mutation results

Mutants are applied to a `git archive` export of `3e4d359c2` (never to the checkout) and run with
K1 = `tests.test_whole_window_inverted_corner_clamp` (seat), K2 = `probes/r1_oracle_sweep.py`
(function-level mutants), K3 = `probes/r2_r4_fixture_probe.py`, K4 = `probes/r2_v062_structural_probe.py`
(mirror mutants). Logs: `.codex-report/l9-env3-fable-rev/mutants/<name>/`.

{{MUTANTS}}

## R5 verification (exact tails)

Commit `3e4d359c2`. `TMPDIR=/tmp/lnine-fable-rev/tmp` (outside the checkout, no float-like token),
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, python3.13.17, Linux container, 4 cores; modules run
two at a time alongside `python3.13 -m unittest discover -s tests/b5_analysis -t .`. Format
`module | Ran line | last line`. Per-module logs: `.codex-report/l9-env3-fable-rev/suite/`.

```
{{TAILS}}
```

Baseline (origin/main export, same container): `tests.test_b5_chain | Ran 25 tests in 8.725s | FAILED (errors=21)`,
`tests.test_b5_chain_prune2 | Ran 44 tests in 23.809s | FAILED (failures=1, errors=10)`; identical causes
(`FileNotFoundError: /bin/zsh` x21 / x10; `'survivors none' not found` process-tree check). Logs under `logs/`.

## Probe logs

- `logs/r1_oracle_sweep.log`: `{{R1}}`
- `logs/r2_r4_fixture_probe.log`: 495 checks ok, 0 FAIL, 1 NOTE (F2).
- `logs/r2_structural_probe.log`: 0.6.2 300 shapes / 0.5.2 300 shapes, 0 mismatches.
- `logs/r4_multiwindow_gate_probe.log`: F1 reproduction.
