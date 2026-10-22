# BAT-3: BYTES battery term — completed cloud build

## PROGRESS

- **Done:** implemented BAT-2's arithmetic, bounds, flags, descriptions and disclosures; production-shaped SMC retention; assisted fixtures and all fault injections; every §8 registration placement.
- **Done:** generated and checked the catalog and all 39 BYTES-generator outputs. Only the twelve BYTES registrations changed; twelve pass trees and every other generator output are identical. Alpha/beta/gamma pack bytes are unchanged.
- **Done:** all 84 analysis test methods pass, including all 60 full production-shaped CLI campaigns; all 34 tests in the other six required modules pass. No skips or environmental test failures.
- **Done:** worked examples reproduce through meter_decode; all 24 assisted placements and the NEG-8 battery reference test pass; all five refusal-census arrays are empty.
- **Done:** 470,411 common data fields compare exactly across ten before/after files; new fields and the three changing hash locations are disclosed below.
- **Done:** agreement ran: 7 tests pass, one expected assisted-defect failure awaits BY-TWIN-BAT, with all 81 affected field names recorded below.
- **Done:** coherent checkpoints pushed to the lane and CI branch; draft PR [#544](https://github.com/mpmdw/JouleWise/pull/544) remains the only CI PR. This final report is pushed to both branches with the same head.
- **Open external work:** the director's raw-H Mac re-reduction, BY-TWIN-BAT parity and lead-owned executing/cold reviews. No cloud implementation, generator or required local test remains blocked. NEEDS_RULING: none.

Accepted continuation base: 71414e1e5ef23366633d264b2b8d37a09da47948. Original BY-INT base and observed remote
pass-1 head: bda481d5af510b29dde4976f172a20170a42c955, unchanged. Final code/test checkpoint before this report:
1da4ac56dac8b61bfd52e7ac834b60d745d525ab.

## SUMMARY

Implemented the ruled signed battery term in DC input and rest, on both bases and in NEG-8 references.
The filtered stream preserves ordered SMC polls and computes tau from the global maximum poll interval.
DC/rest B and floors use u+v; NR1 adds max(v_start,v_end), with meter-only sensitivity retained.
The decode marker selects the description; both decode-scoped and harvest-scoped counts are printed.
Per-run meter/battery/sum and per-cell battery columns carry the ruled boundary sentence.
The catalog has 263 codes, including the new disclose-only marker; every registration placement is filled.
All 84 analysis methods and 34 other required tests pass; all 60 synthetic CLI campaigns complete.
The no-assist comparison has 470,411 exactly equal common data fields; only disclosed hashes change.
Agreement has the expected assisted-defect failure pending the twin patch; CI PR #544 is draft and latest CI is pending.
The cloud build is done; the director still owns the real-H Mac check and BY-TWIN-BAT owns parity.

## WHAT CHANGED

- `joulewise/bytes_analysis.py` — BAT-2 §2–§5, §7, §12. Retain all poll rx/SMC metadata, including n=0 polls, and sort batches by rx before clock unwrapping and selected meter decoding. Meter payload power outside authorized spans is never unpacked. Use Stream.battery_watts and integrate for signed decode/request energy and the own-idle correction; record meter/battery/sum, v_start/v_end, tau and poll counts. Use u+v in the existing phase-edge path feeding B and floors, and max(v_start,v_end) in offset_bound_j. NEG-8's whole-request call receives the same correction. Prepare battery arrays once per archive reduction; direct callers see their current stream without a persistent mutable-data cache. Select descriptions on bytes.decode_battery_assist, count the harvest flag separately, and add battery columns, per-run terms and the boundary sentence.
- `tests/test_bytes_analysis.py` — §2–§5, §9, §12. Add 15 methods covering the worked examples, charging/idle arithmetic, missing/incomplete readings, preserved rails and marker, reversed batches, an outside-span n=0 poll setting global tau, a corrected NEG-8 reference, and the real assisted CLI chain. Update old hand-built zero-assist inputs to contain both readings and use the new marker in description examples. Expanded the worked examples to cover quoted DC totals, secondary energy, u+v, NR1 and paired rest. One overly exact inequality was corrected to the ruling's existing 1e-6 J bar.
- `tests/fixtures/bytes/campaign.py` — §2, §12. Add B0AV=12774 mV to every baseline poll. Optional battery_assist=True adds 5 Hz polls, four placements on the three large models, and harvest assistance flags. Default meter batches, random draws, schedule and inputs remain identical for the no-assist comparison.
- `tests/fixtures/bytes/campaign_design.json` — §12. Define the three large models, four placements, -1000 mA and 12774 mV, with burst-energy derivation from the ruled approximately 1 J attribution scale.
- `docs/contracts/bytes_tables.md` — §2–§5, §12. Replace the former meter-only/harvest-only treatment; document the term, forward delay, bounds, marker, two counts, signed column semantics, output names and sentence.
- `docs/registrations/bytes_pack_v1.md` — all §8 placements, listed below; update §6's code counts/list and Appendix A's exact catalog SHA.
- `scripts/build_b6_flag_catalog.py` — §7, §12. Add bytes.decode_battery_assist as RECORDS / REPRESENTATION / DISCLOSE.
- `configs/b6/flag_catalog_b6.json` — generated only with the owning builder. Exactly one code added; exclusions unchanged.
- `configs/b6/packs/bytes-s{1..6}-p{1,2}/registration.json` — all twelve files generated by bytes_plan_trees.py; each full flag_effects map gains the code. The twelve `configs/campaigns/bytes-s*-p*/plan_tree.json` files reproduce without a byte change.
- `tests/b6/test_catalog.py`, `tests/flags/test_flags_catalog.py` — assert the generated marker classification/effect.
- `.codex-report/BAT-3.md` — progress, executed evidence, decisions and director handoff.

The CLI already serializes the changed table structures, so scripts/bytes_analyze.py needed no edit.
No twin/agreement source, external parser, hazard-refusal registry or unrelated pack changed. No new
battery-float lexeme reader or import dependency requires a reader/graph-list edit; their required tests pass.

### meter_decode output key reference for the director

The existing gross_j and secondary_j are now corrected DC energies; do not add the battery term to them again.

| Key | Meaning | Unit |
|---|---|---|
| gross_j | meter gross + battery gross over the supplied span | J |
| secondary_j | meter own-idle-subtracted energy + battery own-idle-subtracted energy | J |
| idle_power_w | meter idle mean + signed battery idle mean | W |
| meter_gross_j | cable-meter energy before adding the battery | J |
| meter_secondary_j | cable-meter energy minus its own idle mean × T | J |
| meter_idle_power_w | cable-meter own-idle mean | W |
| meter_phase_edge_j | meter edge term u | J |
| battery_gross_j | signed E_b = mean complete-poll power × T | J |
| battery_secondary_j | E_b − battery_idle_power_w × T | J |
| battery_idle_power_w | signed battery mean over the own idle span | W |
| battery_v_start_j | (T/n) Σ abs(P_b) in [start,start+tau) | J |
| battery_v_end_j | (T/n) Σ abs(P_b) in [end,end+tau) | J |
| battery_phase_edge_j | v_start + v_end | J |
| battery_tau_s | 2 × 1.0 s + stream-wide largest poll interval | s |
| battery_poll_interval_max_s | largest interval over all received polls | s |
| battery_n | complete B0AC/B0AV polls inside the supplied span | count |
| battery_n_idle | complete pairs inside own idle | count |
| decode_battery_assist | negative B0AC received in [start+tau,end+tau) | boolean |
| phase_edge_j | u+v, used by DC/rest B and the meter floor | J |
| offset_bound_j | max(edge powers) × (r_max+sample interval) + max(v_start,v_end) | J |

Existing offset_sensitivity_w remains meter-only. Science records copy a true marker to the flag
bytes.decode_battery_assist. A current-only negative poll can retain that disclosure on rails even when
missing voltage prevents a DC value.

## WORKED EXAMPLE

Executed tests: BatteryRulingWorkedExamples.test_bat2_qwen_check_r01_seven_nonzero_polls,
test_bat2_soak_r11_middle_of_decode and test_charging_is_signed_and_idle_is_subtracted_on_its_own_basis.
All pass, including the final expanded total/bound assertions (3 tests, exit 0).

Source numbers: JouleWise-data c17fdca, bat-council-20261022/data/h_decode_extract.json, named in the test.
Only needed numbers are copied into the test. The extract contains the old meter integral and edge readings,
not the full interior trace. The unit fixture reconstructs three interior powers with that mean and those
edges, uses the actual span lengths/nonzero battery polls/counts, and keeps B0AV on every poll. This is an
arithmetic fixture; the director checks H's real raw stream separately.

All three cases were also captured through meter_decode using that fixture:

| Run | n | Meter J | Battery J | Corrected DC J | DC secondary J | v_start J | v_end J | u+v J | C_j per-run J | Marker |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| check-llama-70b-r01 | 280 | 6101.072862 | 0.000000 | 6101.072862 | 5967.417892 | 0.000000 | 0.000000 | 8.314169 | 4.292775 | no |
| check-qwen35-122b-r01 | 56 | 884.499550 | 0.776577 | 885.276128 | 857.327851 | 0.776577 | 0.000000 | 7.163877 | 4.068644 | no |
| soak-llama-70b-r11 | 287 | 6423.530864 | 0.396120 | 6423.926985 | 6261.634076 | 0.000000 | 0.000000 | 8.547328 | 4.488722 | yes |

Tau is 2.302440875 s in all three, from H's 0.302440875 s maximum over all 93,533 polls.
Qwen has T=11.017812967 s and 56 battery polls, seven nonzero; its added C_j term is
0.776577168206106 J. Its paired rest is 885.276127618884−308.06612272598744=577.210004892897 J.
Soak has T=57.436307192 s, 287 polls, five nonzero; E_b=0.39612039944419924 J, v=0 and marker yes.
Check-70B has T=56.018812894 s and 280 zero-current polls.

Bar: 1e-5 J against six-decimal printed quantities, exactly BAT-2 executed evidence item 3:
above 1e6 × float64 noise at 6,424 J (1.4e-6 J) and rounding (5e-7 J), below 1% of the smallest
printed bound (1.1e-3 J). The largest difference among the quoted full-total checks is below 5e-7 J.
The separate same-input program comparison bar is 1e-6 J. Counts/flags use equality.

Evidence: /tmp/bat3-worked-full.log and /tmp/bat3-worked-values.json.

## FAULT INJECTIONS

All cases execute as named tests in BatteryCampaignTests (and the signed idle example above), through
the actual archive join where applicable. They pass in the final 69-test bounded group.

| Case | Executed result |
|---|---|
| Missing B0AC throughout decode | bytes.meter_decode_unavailable; exact reason “battery reading missing”; rails succeeded, DC/rest lose that repeat only |
| Missing B0AV throughout decode | same |
| Missing B0AC throughout idle | same |
| Missing B0AV throughout idle | same |
| Entire decode has no battery pair | same |
| One poll lacks either key, in decode and in idle, while other complete polls survive | value retained, complete-read count decreases by one; no unavailable flag |
| B0AC>0 charging poll | negative signed battery energy −12.774×T/n J; no discharge marker or unavailable flag |
| Charging in decode plus discharge in own idle | unit example gross battery −2.5548 J, secondary −5.1096 J |
| Negative current while all decode voltages are missing | DC unavailable flag plus decode marker retained on rails |
| Batch lines reversed in file order | same flags/counts and same term, DC energy, v and NR1 bound within 1e-6 J |
| n=0 poll outside selected spans, three production poll periods before the first sampled batch | retained integer rx; global gap 0.6 s sets tau=2.6 s despite absent payload/SMC |
| One NEG-8 start reference receives discharge | DC and rest reference energies rise by 12.774×T_request/n; rails unchanged, both bases corrected |

Missing cases keep n_r=10/n_b=10 for rails and n_r=9/n_b=10 for DC/rest on the selected module.
These are flags and boundary-only availability changes, never physical refusals.
The refusal census returns unlisted=[], stale=[], miscounted=[], guard_changed=[], scope_gaps=[].

The initial assisted-start inequality compared 5.118409655172414 with 5.118409655172413.
It now allows BAT-2's existing 1e-6 J same-input bar; no new threshold was invented.
The production arithmetic did not change for this test repair.

## BIT-IDENTITY

Commands (each production/harvest process has JW_B5_SYNTHETIC_ONLY=1 and its own fresh TMPDIR):

```bash
source /tmp/jw-seat.env
export TMPDIR=$(mktemp -d /tmp/jwtmp/bat3_bit_before.XXXX)
/usr/bin/python3.13 -B /tmp/bat3_bit_identity.py before /tmp/bat3-base
export TMPDIR=$(mktemp -d /tmp/jwtmp/bat3_bit_after.XXXX)
/usr/bin/python3.13 -B /tmp/bat3_bit_identity.py after /workspace/JouleWise
/usr/bin/python3.13 -B /tmp/bat3_bit_identity.py compare /workspace/JouleWise
```

Before is exactly bda481d5af510b29dde4976f172a20170a42c955 and its original campaign (B0AC=0, no B0AV).
After uses the same 1,000 science runs, paths, manifest, meter bytes and stored inputs; only B0AV=12774 is
added to every poll, with no assist episode. Both versions run the real all-stage CLI and load_records.

Comparison implementation: recurse through every common dictionary key; require equal list lengths,
scalar types and scalar values, and no removed keys. No numerical tolerance. Record new keys separately.
The only exemptions are explicitly recorded source/commitment digests of changed bytes, never data quantities.

Committed output summary:

```json
{
  "common_scalar_fields": 470411,
  "differences": [],
  "files": [
    "analysis_record.json",
    "fit_pass_estimates.json",
    "h1.json",
    "h2.json",
    "heldout_pass_estimates.json",
    "model_estimates.json",
    "moe.json",
    "predictions.json",
    "records.json",
    "unavailable.json"
  ],
  "new_fields": [
    "battery_gross_j",
    "battery_idle_power_w",
    "battery_n",
    "battery_n_idle",
    "battery_nonzero_run_count",
    "battery_phase_edge_j",
    "battery_phase_edge_max_j",
    "battery_poll_interval_max_s",
    "battery_secondary_j",
    "battery_tau_s",
    "battery_term_max_j",
    "battery_term_mean_j",
    "battery_v_end_j",
    "battery_v_start_j",
    "boundary_description",
    "decode_assisted_member_counts",
    "decode_battery_assist",
    "harvest_assisted_member_counts",
    "meter_gross_j",
    "meter_idle_power_w",
    "meter_phase_edge_j",
    "meter_run_terms",
    "meter_secondary_j"
  ]
}
```

Every common data field is exactly equal: energies, component bounds/floors, durations, variances, HC3/OLS
fits and intervals, derived powers/bandwidths, counts, flags, words, labels and reference inputs.

Three changing locations (four digest strings), disclosed rather than called bit-identical:

- predictions.json.bytes_analysis_sha256: ae8c856d6467f8f51fae3c4e966d7948e64fadbbad22ada066d28748d52a1186 → fbf7b91acbe361cd3947f8e3d70fb9bc2941da9164b99ee2101294b161fc12e7.
- analysis_record.json.bytes_analysis_sha256.committed and .evaluating: the same source digest change.
- analysis_record.json.predictions_sha256: ac043d20ce54ba4cd8209d21b3a16eaeb3f93c98d501785f2348ea68006cc2a6 → 959f1c725b107760fa785fd2b02ada4cdca88ce606901f562ccd038395a73a55.

Literal equality of hashes of changed source/schema bytes is impossible; no scientific value is exempted.
The analysis source has not changed since this comparison; subsequent edits strengthen tests/report only.

Evidence: /tmp/bat3-bit-identity/comparison.json and /tmp/bat3-bit-{before,after,compare}.log.
New fields are listed in the committed JSON summary above; their meanings are in WHAT CHANGED and the contract.

## SYNTHETIC ASSIST

BatteryCampaignTests uses archive_campaign(battery_assist=True, release="none") and the real export →
blinded CLI → fit-key release → fit CLI → held-out release → heldout CLI → load_records/model tables chain.
All stage processes exit 0, and the prediction commitment stays byte-identical through held-out evaluation.

Power is −(−1000 mA)×12774 mV/1e6=12.774 W. One-second bursts supply 12.774 J;
the 0.8-second prefill burst supplies 10.2192 J. These exceed the ruled approximately 1 J attribution scale
and every actual tested cell's 1% of (h+B) agreement bar. No new bar is used.
Terms use each span's own T/n, so reported joules need not equal a nominal 0.2 s poll hold.

| Pass | Model | Placement | Burst J | Decode term J | v J | Marker |
|---|---|---|---:|---:|---:|---|
| 1 | Llama-70B | inside_decode | 12.774000 | 12.796024 | 0.000000 | yes |
| 1 | Llama-70B | across_start | 12.774000 | 5.118410 | 5.118410 | no |
| 1 | Llama-70B | across_end | 12.774000 | 7.651231 | 5.100821 | yes |
| 1 | Llama-70B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |
| 1 | Next-80B | inside_decode | 12.774000 | 12.774000 | 0.000000 | yes |
| 1 | Next-80B | across_start | 12.774000 | 7.664400 | 7.664400 | no |
| 1 | Next-80B | across_end | 12.774000 | 7.664400 | 5.109600 | yes |
| 1 | Next-80B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |
| 1 | Qwen3.5-122B | inside_decode | 12.774000 | 12.774000 | 0.000000 | yes |
| 1 | Qwen3.5-122B | across_start | 12.774000 | 5.109600 | 5.109600 | no |
| 1 | Qwen3.5-122B | across_end | 12.774000 | 7.664400 | 5.109600 | yes |
| 1 | Qwen3.5-122B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |
| 2 | Llama-70B | inside_decode | 12.774000 | 12.774000 | 0.000000 | yes |
| 2 | Llama-70B | across_start | 12.774000 | 7.664400 | 7.664400 | no |
| 2 | Llama-70B | across_end | 12.774000 | 5.109600 | 7.664400 | yes |
| 2 | Llama-70B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |
| 2 | Next-80B | inside_decode | 12.774000 | 12.774000 | 0.000000 | yes |
| 2 | Next-80B | across_start | 12.774000 | 5.109600 | 5.109600 | no |
| 2 | Next-80B | across_end | 12.774000 | 7.664400 | 5.109600 | yes |
| 2 | Next-80B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |
| 2 | Qwen3.5-122B | inside_decode | 12.774000 | 12.774000 | 0.000000 | yes |
| 2 | Qwen3.5-122B | across_start | 12.774000 | 5.109600 | 5.109600 | no |
| 2 | Qwen3.5-122B | across_end | 12.774000 | 5.109600 | 7.664400 | yes |
| 2 | Qwen3.5-122B | prefill_only | 10.219200 | 0.000000 | 0.000000 | no |

At every large-model cell, on both bases/selections and every boundary:
decode-assisted counts repeat=2/quad=0; request-flag counts repeat=4/quad=0.
The without-assisted description keeps n_r=8/n_b=10. Primary counts remain 10/10.
There are 3 nonzero decode terms per 50-run module; the prefill-only case moves neither term nor marker (v=0).
The cell battery column and boundary sentence are checked in the actual CLI tables.

Evidence: BAT3_SYNTHETIC in /tmp/bat3-analysis-remaining.log, copied to /tmp/bat3-synthetic-evidence.json.
Separately, all 20 seeds of each bytes/resident/time world complete the default no-assist full CLI chain:
60 campaigns, 60,000 science runs, with their original word/coverage/drift assertions unchanged.

## REGISTRATION

All BAT-2 §8 placements are present:

| Required placement | Destination |
|---|---|
| DC-input bullet | §1 |
| Battery assist: term, delay-aware marker, description, both counts and H expectations | §6 |
| u+v DC cell and rails anchor+u+v rest cell | §7 phase-edge bound row |
| “Battery term and its edge term v” | §7 after meter u |
| max(v_start,v_end) in C_j and one-signed-delay sentence | §9 NR1 |
| Battery mean/largest/nonzero count and largest v | §15 |
| Native battery-reading dependency; harvest flag counted only | §16 |
| BAT-2 ruling → §1, §6, §7, §9, §15, §16 | §20 |

The three quoted replacement blocks match the ruling verbatim modulo line wrapping, checked from fc7548a17.
The surrounding meter-u paragraph describes the cable-meter part and the combined u+v floor consistently.
The sensitivity disclosure remains meter-only. §6 lists all four BYTES disclose-only additions and the
generated counts: 263 total, 203 DISCLOSE, 41 EXCLUDE_MEMBER, 19 EXCLUDE_WINDOW.

Catalog SHA before: 4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f.
Catalog SHA after: 33e1c6110d98474465109062cfcdff480679ba8b2c9854fc754fa26fa07bccb6.
Appendix A carries the new exact digest. Excluding codes are unchanged.

Generator commands, all exit 0:

```bash
/usr/bin/python3.13 -B /workspace/JouleWise/scripts/build_b6_flag_catalog.py --write
/usr/bin/python3.13 -B /workspace/JouleWise/scripts/build_b6_flag_catalog.py --check
/usr/bin/python3.13 -B /workspace/JouleWise/scripts/bytes_plan_trees.py --output-root /tmp/bat3-generated
/usr/bin/python3.13 -B /workspace/JouleWise/scripts/bytes_plan_trees.py --check
```

The plan generator emits 39 files into scratch. Only changed authorized registration/plan-tree paths are copied;
every other generated byte string must already equal the checkout. Twelve registrations change, twelve pass
trees do not, and all 39 outputs reproduce. Every non-BYTES pack registration (alpha/beta/gamma, three files)
was compared byte for byte against bda481d5a; the complete pack/campaign Git diff contains only the twelve BYTES
registrations. No other pack or campaign tree changed.

## TESTS RUN

All test/harvest commands use /usr/bin/python3.13 (3.13.5), JW_B5_SYNTHETIC_ONLY=1,
PYTHONDONTWRITEBYTECODE=1 and a fresh per-process TMPDIR from /tmp/jwtmp. No whole suite ran locally.

Common shell prelude, repeated for every module/process with its own name:

```bash
source /tmp/jw-seat.env
export TMPDIR=$(mktemp -d /tmp/jwtmp/<module>.XXXX)
/usr/bin/python3.13 -B -m unittest <module>
```

| Exact module argument | Tests | Exit | Result |
|---|---:|---:|---|
| tests.b6.test_bytes_packs | 9 | 0 | pass |
| tests.b6.test_catalog | 4 | 0 | pass |
| tests.flags.test_flags_catalog | 7 | 0 | pass |
| tests.hazards.test_import_graph | 6 | 0 | pass |
| tests.flags.test_flags_import_graph | 3 | 0 | pass |
| tests.test_battery_float_sweep | 5 | 0 | pass |
| tests.test_bytes_agreement | 8 | 1 | 7 pass; expected assisted-defect failure pending twin |

The initial /usr/bin/python3.13 -B -m unittest tests.test_bytes_analysis run was stopped with exit 143
before the ten-minute foreground limit, after exposing the new roundoff assertion and entering the
60-campaign test. It has no final test count and is not counted as completed evidence.

Complete bounded coverage of tests.test_bytes_analysis:

```bash
# Same common prelude, fresh TMPDIR for each line.
/usr/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.Addendum4RegressionTests
/usr/bin/python3.13 -B /tmp/bat3_run_analysis.py remaining
/usr/bin/python3.13 -B /tmp/bat3_run_analysis.py bytes
/usr/bin/python3.13 -B /tmp/bat3_run_analysis.py resident
/usr/bin/python3.13 -B /tmp/bat3_run_analysis.py time
/usr/bin/python3.13 -B -m unittest -v tests.test_bytes_analysis.BatteryRulingWorkedExamples
```

- Addendum4 group: 14 tests, 242.005 s, exit 0.
- Remaining group: 69 tests, 347.890 s, exit 0. The scratch runner loads every TestCase except Addendum4 and CampaignWordRates.
- Each world: the original CampaignWordRates method, 20 seeds, all original per-world assertions retained; bytes 241.561 s, resident 241.341 s, time 240.509 s, exit 0 each. The runner restricts only the design's seeds mapping to that world; no seed or assertion is removed.
- Final strengthened worked-example group: 3 tests, 0.001 s, exit 0.
- Unique coverage: all 84 analysis methods pass; the world method executes three times to cover its three worlds. The three worked methods are rerun after expanding their assertions. Together with the six other passing modules, 118 unique methods pass; agreement adds 7 passes and its one expected failure (126 unique methods total).

Additional executed checks: bit-identity before/after/compare commands above, each exit 0;
the actual assisted CLI chain (within BatteryCampaignTests), all exits 0; registration block comparison,
non-BYTES pack equality, generator checks and git diff --check, exit 0;
`/usr/bin/python3.13 -B -m tests.hazards.refusal_census`, all five arrays empty, exit 0.

Initial/diagnostic attempts are retained honestly:

- Seat startup was initially offline/starting; shell access later recovered. The prior checkpoint requested a path clarification; the director approved /usr/bin/python3.13 and said to decide such VM details and continue.
- Seat setup's /opt link failed because uid=1000 has no write permission there and sudo is absent. No test actually failed because of the missing path.
- An initial timing wrapper used unavailable /usr/bin/time: all eight launches exited 127 before Python tests started. Reran without that wrapper, with fresh TMPDIRs.
- The first bare catalog-builder invocation printed its required --write/--check usage; no artifact changed. The corrected commands above pass.
- A 15-test new-path diagnostic initially had 14 passes and the one approximately 9e-16 J inequality failure; corrected with the ruling's 1e-6 J bar, then all 15 pass in the final group.
- No /private/tmp, launchd/launchctl, powermetrics, macOS process-group or fixture git-commit-128 test failure occurred. No skips.

### Agreement fields awaiting BY-TWIN-BAT

The four non-assisted campaign comparisons pass their bars:
bytes 9966 compared / 0 above; resident 9966 / 0; time 9966 / 0; minimum 10091 / 0.
The assisted-defect campaign compares 10012 fields: 5574 equal, 4200 under bar, 238 above.
It plants -3000 mA at 12000 mV while halving the meter, so the ruled battery term changes DC/rest,
their bounds and downstream fits; the untouched twin remains meter-only. Rails' independent energy remains intact.

All 81 above-bar keys, by actual comparer name:

```text
B_j
B_kind:meter_edge
bytes:ln_ratio
bytes:measured_lower
bytes:measured_upper
deviation_w
e
extended:P0:estimate
extended:epsilon:estimate
extended:epsilon:lower[HC3]
extended:epsilon:lower[OLS label]
extended:epsilon:upper[HC3]
extended:epsilon:upper[OLS label]
extended:rho:estimate
extended:rho:lower[HC3]
extended:rho:lower[OLS label]
extended:rho:upper[HC3]
extended:rho:upper[OLS label]
h_j
half_width_j(h+B)
llama-3.3-70b-instruct-4bit
lower
lower_j
lower_w
mean_j
meter_attribution_floor_j
pass_difference_j
pass_values_j[0]
power
power_half_w
predicted_w
prediction_half_w
printed_j_per_output_token
qwen3-1.7b-4bit
qwen3-14b-4bit
qwen3-32b-4bit
qwen3-4b-4bit
qwen3-8b-4bit
qwen3-next-80b-a3b-instruct-4bit
qwen3.5-122b-a10b-4bit
resident:ln_ratio
resident:measured_lower
resident:measured_upper
rest:c:estimate
rest:epsilon_rest:estimate
rest:epsilon_rest:lower[HC3]
rest:epsilon_rest:lower[OLS label]
rest:epsilon_rest:upper[HC3]
rest:epsilon_rest:upper[OLS label]
rest:lambda:estimate
rest:lambda:lower[HC3]
rest:lambda:lower[OLS label]
rest:lambda:upper[HC3]
rest:lambda:upper[OLS label]
simple:P0:estimate
simple:epsilon:estimate
simple:epsilon:lower[HC3]
simple:epsilon:lower[OLS label]
simple:epsilon:upper[HC3]
simple:epsilon:upper[OLS label]
status
tier:P0:estimate
tier:epsilon:estimate
tier:epsilon:lower[HC3]
tier:epsilon:lower[OLS label]
tier:epsilon:upper[HC3]
tier:epsilon:upper[OLS label]
tier:rho:estimate
tier:rho:lower[HC3]
tier:rho:lower[OLS label]
tier:rho:upper[HC3]
tier:rho:upper[OLS label]
time:consistent
time:ln_ratio
time:measured_lower
time:measured_upper
upper
upper_j
upper_w
variance
word
```

The model-name keys are entries in H1/active-or-resident miss maps. The other keys span DC/rest cell bounds,
means/endpoints, combined points, H1 log/consistency/word fields, H2 coefficients/intervals and deviations.
The full 238 records, groups, values and bars are /tmp/bat3-agreement-fields.json.
A targeted read-only replay of the same defects campaign collected this full list (exit 0);
tests.test_bytes_agreement.py and every twin file remain untouched. Its old comparer also lacks new
battery-column coverage; those new fields are listed above for the twin seat.

## CI

Branch: ci/2026-10-22-bytes-battery-term. Existing draft PR:
[#544](https://github.com/mpmdw/JouleWise/pull/544), “CI only: BYTES battery term (BAT-3)”, against main.
The lane and CI branch receive the same final head; no merge or force push.

Last observation, 2026-10-22 08:39 UTC, on code/test checkpoint 1da4ac56dac8b61bfd52e7ac834b60d745d525ab:

- [CI 39749257462](https://github.com/mpmdw/JouleWise/actions/runs/39749257462): pending, no conclusion.
- [Gate-ledger 39749257063](https://github.com/mpmdw/JouleWise/actions/runs/39749257063): completed, failure as expected.

Earlier checkpoint build, installed-wheel and fences passed. The initial catalog checkpoint was incomplete;
its old CI state is not evidence for the regenerated final tree. This final report push triggers fresh CI;
no green final-head claim is made. The known agreement failure remains until BY-TWIN-BAT. No waiting on CI
past completion of other work, as directed.

## DECISIONS I MADE

- BAT-2 governs all arithmetic, markers, printing and §8 placements; the obsolete whole-member 55–60 J number is not the decode correction.
- Use the approved installed /usr/bin/python3.13 in this VM; /opt is the Mac convention. There is no root/sudo here. Record an actual missing-path test failure as environmental, but do not block work on a VM path choice.
- Keep signed charging and sub-1 J terms; add no clipping, rounding-to-zero, refusal or new threshold.
- Retain all poll rx/SMC metadata, including zero-sample/incomplete polls, so global delta-t_p and forward windows survive filtering; sort by rx as the native parser does.
- Preserve default no-assist meter batches, random draws and inputs; use an explicit assisted mode for the large-model stress.
- Use u+v in DC/rest B and floors and max(v_start,v_end) in NR1; leave dβ/dδ meter-only.
- Follow §4's current-defined marker literally: known negative B0AC discloses assistance even if voltage is missing. Missing DC coverage must not suppress the rails description.
- Ignore an incomplete poll when complete readings survive, as §2 specifies; only an entire missing decode/idle reading produces the existing unavailable flag.
- Print the largest signed battery value, consistent with the signed term; count nonzero values without an invented threshold.
- Count the harvest flag without selecting on it; print battery columns and no separate meter-only line.
- Use the ruling's 1e-6 J bar for mathematically equal same-input calculations that differ by float roundoff, and 1e-5 J for its six-decimal examples.
- Split the long test by class/world to respect foreground limits, retaining all 60 campaigns and every assertion. No whole suite, extra collection or new gate.
- Disclose source/commitment hash changes in the exact comparison; exempt no scientific quantity. A hash of changed bytes cannot remain equal.
- Preserve the exhaustive scope: no twin, external parser, agreement-test, unrelated pack, main or ops/stop ref edit.

## OPEN ISSUES

- The director re-reduces H's real raw streams on the Mac at the final head, through _filtered_stream and meter_decode,
  without JW_B5_SYNTHETIC_ONLY and with TMPDIR under /Users/edr/night-archive/forward-20261021/BAT-3/tmp:
  check-llama-70b-r01 adds 0 J, soak-llama-70b-r11 adds 0.396120 J, check-qwen35-122b-r01 adds 0.776577 J,
  with |E_b,true−E_b|≤v. The key reference above prevents double-adding the battery to gross_j.
- BY-TWIN-BAT owns parity and the expected agreement failure; its files are untouched. CI cannot be called fully green while that expected failure remains.
- Executing review, cold passes and integration are lead-owned. CI remains pending at the last observation.
  No whole-suite or live-H acceptance is claimed by this cloud seat.

## NEEDS_RULING

none.
