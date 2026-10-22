# BAT-3: BYTES battery term

## PROGRESS

- **Done:** resumed from accepted checkpoint 71414e1e5; the director approved /usr/bin/python3.13 (3.13.5). No root/sudo is available; missing /opt fixture paths will be listed as environmental.
- **Done:** catalog generated with --write and verified with --check; SHA-256 33e1c6110d98474465109062cfcdff480679ba8b2c9854fc754fa26fa07bccb6, 263 codes, 203 DISCLOSE, 41 EXCLUDE_MEMBER, 19 EXCLUDE_WINDOW. Registration SHA/counts filled.
- **Done:** all 39 plan-generator outputs reproduce byte for byte. Only twelve BYTES registration.json files changed; twelve plan trees are identical. No alpha/beta/gamma or other pack changed.
- **Running:** all eight required modules, each with a fresh TMPDIR and JW_B5_SYNTHETIC_ONLY=1. Initial timing-wrapper attempt did not start tests (/usr/bin/time absent); rerun uses the approved interpreter directly.
- **Next:** fix in-scope failures, execute exact no-assist comparison, record actual fault/CLI evidence and named twin differences, finalize report, push both authorized branches and update PR #544.
- **Open:** director's real-H re-reduction is on the Mac; no science ruling is pending.

The sections below still contain checkpoint-era pending text and will be replaced with completed evidence before final push.

## SUMMARY

Implemented BAT-2's signed decode battery term and own-idle subtraction in meter_decode.
The filtered stream retains all SMC polls in receive order and derives tau from the global maximum gap.
DC input/rest carry u + v; NR1 adds the larger battery edge; the sensitivity remains meter-only.
The decode-scoped marker selects the description; the harvest flag supplies a separate stratum count.
Per-run meter/battery/sum and per-cell battery columns are added, with the ruled boundary sentence.
Added an assisted synthetic mode and 15 worked-example, fault, reference and CLI-chain tests.
Updated every BAT-2 §8 registration placement and the contract; the flag builder has the new disclose-only code.
The implementation is pushed, but generators, local tests and bit-identity evidence remain blocked by the interpreter path.
CI PR #544 is draft; the last observed implementation-head build, installed-wheel and fences passed, quick was running.
BAT-3 is incomplete; no acceptance, twin parity, real-H re-reduction or green final-head CI is claimed.

## WHAT CHANGED

- `joulewise/bytes_analysis.py` — BAT-2 §2–§5 and §12: retain every poll's rx/SMC, including n=0 polls; sort by rx before clock unwrapping and selected meter decoding. Use Stream.battery_watts and integrate for signed gross/secondary energy; retain separate meter/battery/sum and v_start/v_end/tau/counts. Use u + v in the existing phase-edge path, which feeds B and floors; add max(v_start, v_end) to offset_bound_j. NEG-8's existing whole-request meter_decode join receives the correction. Prepare immutable battery input arrays once per archive reduction, without caching mutable direct-call streams. Select without-assisted descriptions on the decode marker and print both counts. Add per-run/per-cell battery disclosures and the ruled boundary sentence.
- `tests/test_bytes_analysis.py` — §9 and §12: add the two nonzero worked examples, signed charging/idle arithmetic, missing-current/voltage cases, all-missing decode, a surviving single incomplete poll in both spans, a current-only marker with missing voltage, out-of-order batches, an outside-span n=0 poll setting global tau, a battery-bearing NEG-8 reference, and the assisted real CLI chain. Adapt old hand-built streams/records to complete zero-assist SMC readings and the new marker. Static count: 69 existing test methods plus 15 new ones; none has been executed locally.
- `tests/fixtures/bytes/campaign.py` — §2 and §12: B0AV=12774 mV accompanies every baseline poll. Optional battery_assist=True supplies 5 Hz polls, four large-model placements and request-scoped harvest flags. Default no-assist batching, random draws, schedule and meter inputs are preserved for the exact comparison.
- `tests/fixtures/bytes/campaign_design.json` — §12: name the large models, placements, -1000 mA current and 12774 mV voltage, with the attribution-scale derivation.
- `docs/contracts/bytes_tables.md` — §2–§5: replace the old harvest-only/meter-only rule; document the signed term, global delay, bounds, marker, counts, column fields and boundary wording; amend NR1's per-run support.
- `docs/registrations/bytes_pack_v1.md` — §8: install all specified placements, verbatim for the three quoted replacements; amend NR1 and printed/dependency/mapping text; update intended catalog counts to 263/203 and list the fourth BYTES disclose-only code. Catalog SHA remains the old SHA until generation runs.
- `scripts/build_b6_flag_catalog.py` — §7/§12: add bytes.decode_battery_assist as RECORDS / REPRESENTATION / DISCLOSE.
- `tests/b6/test_catalog.py` and `tests/flags/test_flags_catalog.py` — assert that B6's generated code has the ruled classification.
- `.codex-report/BAT-3.md` — persistent progress and incomplete-build evidence.

No twin, external parser, CLI, hazard-refusal registry, graph list or battery-float lexeme reader changed.
No new import dependency requires a graph-list amendment; no new battery-float lexeme reader exists.
The generated catalog/pack files remain pending rather than hand-edited. No alpha, beta or gamma pack changed.

## WORKED EXAMPLE

Tests written: BatteryRulingWorkedExamples.test_bat2_qwen_check_r01_seven_nonzero_polls and
test_bat2_soak_r11_middle_of_decode. These call meter_decode; their meter power is an explicitly synthetic constant,
and their battery timestamps/current/voltage and span lengths are copied from the packet with a source comment.
They do not pretend to reconstruct H's unavailable full raw meter interior.

Read-only packet preparation, evaluated in JavaScript before local setup became available, gives:

| Run | T (s) | n | E_b (J) | v_start (J) | v_end (J) | Marker |
|---|---:|---:|---:|---:|---:|---|
| check-llama-70b-r01 | 56.018812894 | 280 | 0 | 0 | 0 | no |
| check-qwen35-122b-r01 | 11.017812967 | 56 | 0.7765771682061066 | 0.7765771682061066 | 0 | no |
| soak-llama-70b-r11 | 57.436307192 | 287 | 0.3961203994441993 | 0 | 0 | yes |

The global maximum poll gap is 0.302440875 s over 93,533 polls, so tau=2.302440875 s.
Qwen's added C_j per-run term is 0.7765771682061066 J; soak's is 0 J.

The tests use BAT-2's 1e-5 J printed-value bar: above 1e6 times float64 noise at 6,424 J
(1.4e-6 J) and six-decimal rounding (5e-7 J), below 1% of the smallest printed bound (1.1e-3 J).
Same-input program comparisons use 1e-6 J. Counts, flags and integer-clock identity use equality.
The tests are unexecuted: this table is packet arithmetic, not meter_decode acceptance evidence.

Source: JouleWise-data@c17fdca:bat-council-20261022/data/h_decode_extract.json,
blob 867bd81054eb35e6c91528d7580e32676133da1f. No data-repository file was copied into this repository.

## FAULT INJECTIONS

Written, not executed:

- Missing B0AC throughout decode: existing bytes.meter_decode_unavailable, reason battery reading missing; rails survive.
- Missing B0AV throughout decode: same.
- Missing B0AC throughout idle: same.
- Missing B0AV throughout idle: same.
- Whole decode with no battery readings: same.
- One incomplete poll among complete readings, in decode and idle, with either key absent: ignore that poll, reduce the complete-read count, keep the value.
- Positive B0AC charging poll: signed negative battery energy; no decode-assist marker from that positive current.
- Signed idle battery power: subtract its own mean times decode length.
- Reverse batch-line order: compare term, DC energies, v, C_j bound and exact flags/counts with ordered data, at the ruled 1e-6 J same-input bar.
- An n=0 poll outside selected spans introduces a three-poll (3 × 0.2 s) gap: global tau must retain that gap.
- A negative current with missing voltage: the integral becomes unavailable if no complete pair remains, but §4's current-defined marker still discloses assistance on rails.

The tests assert boundary-only removal and successful rails records. No new refusal site was added.
Refusal census has not been run, so empty census arrays are not claimed.

## BIT-IDENTITY

Not run. No fields-compared count or successful comparison is claimed.

The exact original tree is preserved in /tmp/bat3-base. Run the old fixture and old analysis there; then run the
new analysis on the same synthetic campaign after adding B0AV only, with battery_assist=False. Preserve the
same paths/manifest and compare every common numerical/data field by equality. List new fields separately.

Code-provenance and commitment hashes necessarily change when the module and commitment schema change.
Record those explicitly; do not silently omit them or claim literal file identity. The brief's literal
“every field” cannot include an unchanged hash of changed source/commitment bytes. This is a provenance
disclosure, not a choice of which runs count or a changed numerical comparison bar.

New source fields that need disclosure/comparison coverage:

- Per run: meter_gross_j, meter_secondary_j, meter_idle_power_w, meter_phase_edge_j;
  battery_gross_j, battery_secondary_j, battery_idle_power_w, battery_phase_edge_j,
  battery_v_start_j, battery_v_end_j, battery_tau_s, battery_poll_interval_max_s,
  battery_n, battery_n_idle, decode_battery_assist.
- Per DC/rest cell/point: boundary_description, battery_term_mean_j, battery_term_max_j,
  battery_nonzero_run_count, battery_phase_edge_max_j; per cell meter_run_terms.
- Per cell: decode_assisted_member_counts and harvest_assisted_member_counts.
- Existing gross_j, secondary_j and idle_power_w become corrected DC values; phase_edge_j becomes u+v;
  offset_bound_j includes the ruled maximum battery edge. On zero-battery inputs their original arithmetic is retained plus zero.

## SYNTHETIC ASSIST

Written as an optional assisted campaign mode, not executed. Models: Llama-3.3-70B,
Qwen3-Next-80B and Qwen3.5-122B, both passes. Repeat ordinals 0–3 receive these placements:

| Placement | Planted received-reading span | Power and nominal burst energy | Intended term/v/marker check |
|---|---|---|---|
| inside decode | centered at decode midpoint, 1 s | 12.774 W, 12.774 J | positive term, zero edge term, marker yes |
| across decode start | start −0.5 to start +0.5 s | 12.774 W, 12.774 J | term covered by v_start, marker no |
| across decode end | end −0.5 to end +0.5 s | 12.774 W, 12.774 J | term plus post-end v_end, marker yes |
| prefill only | decode start −0.9 to −0.1 s | 12.774 W, 10.2192 J | term 0, v 0, marker no |

These are fixture inputs and expected checks, not measured outputs. Actual terms and v depend on poll membership
and T/n and must be recorded after execution. Each burst exceeds the ruled approximately 1 J attribution limit.
The test additionally checks it against the actual cell's 1% of (h+B) agreement bar.

The new class runs export → blinded CLI → fit-key release → fit CLI → held-out release → heldout CLI,
then load_records and the real table outputs. It checks intended per-stratum decode/request counts
repeat 2/4 and quad 0/0, and without-assisted n_r=8/n_b=10, at every boundary and basis.
The real CLI path is implemented in the test but has not run; none of those counts is execution evidence.

## REGISTRATION

BAT-2 §8 placements installed:

| Placement | Destination |
|---|---|
| DC-input bullet | §1 |
| Battery assist replacement, delay marker, description/counts and H expectations | §6 |
| DC/rest phase-edge table cells | §7 |
| Battery term and its edge term v, copied verbatim after meter u | §7 |
| Per-run C_j max-edge battery addition and one-signed-delay sentence | §9 |
| Battery column and largest v | §15 |
| Native battery-reading dependency, request flag counted only | §16 |
| BAT-2 ruling mapping row | §20 |

The old meter-u paragraph is adjusted to describe meter energy and the combined u+v floor consistently.
The §6 flags sentence names the fourth BYTES disclose-only code and intended totals 263 codes / 203 disclosures.
The actual generated catalog still has 262 codes / 202 disclosures until the generator runs.

Catalog SHA before: 4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f.
Catalog SHA after: still the same; generation and the registration SHA-line update are outstanding.
Only the twelve BYTES registrations and twelve BYTES plan trees may acquire the new map, through the
real bytes_plan_trees generator. Generate to scratch and copy only authorized changed paths if the generator
also emits unchanged out-of-scope files; verify all its outputs byte for byte and leave other packs untouched.

## TESTS RUN

- git diff --check: exit 0 before both source checkpoints; no whitespace errors.
- No local Python test, generator, Python CLI campaign or refusal census ran. No test counts, skips or failures are claimed.
- Static source test-method count: 69 before, 84 after; this is not a test-run count.

Executed setup command (after workspace recovery):

```bash
git -C /workspace/JouleWise fetch origin '+refs/heads/*:refs/remotes/origin/*'
git -C /workspace/JouleWise checkout -B lane/2026-10-22-bytes-battery-term origin/lane/2026-10-22-bytes-battery-term
git -C /workspace/JouleWise rev-parse origin/lane/2026-10-22-bytes-pass1
bash /workspace/JouleWise-data/tools/cloud/seat_setup.sh /workspace/JouleWise
source /tmp/jw-seat.env
git -C /workspace/JouleWise-data fetch origin '+refs/heads/analysis/bat-council-20261022:refs/remotes/origin/analysis/bat-council-20261022'
```

The combined shell command exited 0. BY-INT printed bda481d5af510b29dde4976f172a20170a42c955.
Seat setup printed “mkdir: cannot create directory ‘/opt/homebrew’: Permission denied” but continued to
“SETUP: ok”; it exported JW_B5_SYNTHETIC_ONLY=1 and PYTHONDONTWRITEBYTECODE=1 and created /tmp/jwtmp.
Its Python target was /usr/bin/python3.13, reporting Python 3.13.5. /opt is owned by nobody, is not writable
by uid 1000, and sudo is absent. No auto-review rejection occurred; this is an operating-system permission failure.

Initial startup: wait_for_environment never produced readiness before it was stopped to inspect status;
a shell request was rejected before launch with “No usable execution environment is available.”
Status later became running/connected and shell access recovered. No diagnostic logs or credentials were read.

Still required, one fresh TMPDIR per module and JW_B5_SYNTHETIC_ONLY=1 throughout:

```bash
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_analysis.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_packs.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_agreement.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_agreement
```

Also run tests.b6.test_catalog, tests.flags.test_flags_catalog, tests.hazards.test_import_graph,
tests.flags.test_flags_import_graph and tests.test_battery_float_sweep, with separate TMPDIRs.
Do not run the whole suite locally. List the seat notes' environmental failures rather than chasing them.

tests.test_bytes_agreement has not run. Actual failing field names cannot be listed yet.
The old comparer omits the new battery-column fields, and its harvest-flag-based description is expected
to diverge from the new marker. Record actual named failures after execution; BY-TWIN-BAT owns the twin.

## CI

- Branch: ci/2026-10-22-bytes-battery-term.
- Draft PR: [#544](https://github.com/mpmdw/JouleWise/pull/544), title “CI only: BYTES battery term (BAT-3)”.
- Last observed implementation head: bba4b2695c2af6334f085932a973db55db9913de.
- [CI run 39745041911](https://github.com/mpmdw/JouleWise/actions/runs/39745041911): changes, build,
  installed-wheel and fences passed; quick was in progress. This is not a green whole-suite claim.
- [Gate-ledger run 39745041940](https://github.com/mpmdw/JouleWise/actions/runs/39745041940): failed as expected.
- Catalog assertions and reproducibility checks cannot be considered complete while generated outputs are pending.
- The report update will push the same new head to both authorized branches and start fresh CI.
  No final-head green result is claimed and no waiting on CI beyond other work is intended.

## DECISIONS I MADE

- BAT-2 governs the arithmetic, selection, printing and all §8 placements, ahead of the earlier design text.
- Use the ruled decode-span term, not the corrected brief's obsolete whole-member 55–60 J number.
- Retain signed charging energy and sub-1 J terms; no clipping, rounding-to-zero or new threshold.
- Retain all SMC poll metadata to preserve both the global maximum gap and forward edge windows;
  sort batches by rx before unwrapping, as the native parser does.
- Keep original no-assist meter batching/random inputs; make the large-model assist campaign explicit through a fixture parameter.
- Use u+v in DC/rest B and floors and max(v_start,v_end) in NR1; keep dβ/dδ meter-only.
- Interpret §4's current-defined marker literally: a known negative B0AC can disclose assistance even
  if B0AV is missing. Missing energy coverage still removes only DC/rest, so preserve that marker on rails.
- A partial poll does not trigger the missing-span flag if other complete polls remain, as §2 specifies.
- The largest battery column value is the signed maximum, consistent with the ruled signed term.
- Count the request flag without selecting on it, and print no separate meter-only estimate line.
- Keep the existing flag-only missing-reading path. Add no hazard refusal.
- Do not infer approval to substitute the interpreter while the explicit path question is pending.
- Do not represent written tests, packet arithmetic or CI build checks as executed local acceptance evidence.

## OPEN ISSUES

1. Provide the required interpreter path or authorize its installed /usr/bin/python3.13 target.
2. Run the catalog builder and --check; regenerate only authorized BYTES maps with the real plan generator;
   check byte-for-byte reproduction and unchanged alpha/beta/gamma outputs. Update registration SHA.
3. Run all specified modules and the assisted process-level CLI chain; fix actual defects within scope.
4. Execute the exact zero-assist baseline comparison, list common compared fields/new fields/hash changes,
   and commit the actual output summary.
5. Record actual agreement failures by field for BY-TWIN-BAT. Do not edit the twin or agreement test.
6. The director must re-reduce H on the Mac without JW_B5_SYNTHETIC_ONLY, with TMPDIR under
   /Users/edr/night-archive/forward-20261021/BAT-3/tmp: check-llama-70b-r01 adds 0 J,
   soak-llama-70b-r11 adds 0.396120 J, check-qwen35-122b-r01 adds 0.776577 J, with the ruled bounds.
7. Executing review and cold gates remain lead-owned; no merge to main or physical collection occurred.

## NEEDS_RULING

none. The current blocker is the interpreter-path constraint, not an undecided scientific choice.
