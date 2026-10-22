# BAT-3: BYTES battery term — environment-blocked intake

## PROGRESS

- **Done:** Read the complete BAT-2 ruling at `fc7548a17` through connected GitHub access. Inspected the BY-INT source, registration, design R1–R8, root agent instructions and preflight, and the packet's worked-example and delay-check scripts at `c17fdca`. Retrieved the packet extract by its Git blob.
- **Done:** Confirmed remotely that `lane/2026-10-22-bytes-pass1` is exactly `bda481d5af510b29dde4976f172a20170a42c955`. BAT-3 did not already exist. Created the authorized BAT-3 lane at that exact base through the connected GitHub API.
- **Next:** Obtain a working execution environment, fetch and check out this lane, run seat setup, preserve the baseline comparison, then implement the ruling and run all requested checks. Follow the original brief's exhaustive scope.
- **Open:** Implementation has not started. No analysis, fixture, registration, catalog, generated pack, or test file has changed. This report is the only change.
- **Blocker:** The selected cloud workspace never became usable during intake. The startup wait yielded repeatedly; a direct shell request failed with “No usable execution environment is available. Wait for an environment to become available before using this tool.” Status then changed from `starting` to `pending`, still `offline`, with `capabilities: []`, current observations and no reported failure cause. Latest recorded observation: 2026-10-22 07:36 UTC.
- **Recovery:** A restart or a ready workspace is needed. No science ruling or scope expansion is requested. Remote reads and this report do not substitute for the required Python executions.

## SUMMARY

BAT-3 is incomplete because the selected cloud execution environment is unavailable.
The authorized lane starts at the exact BY-INT head, which has not moved.
The full ruling and the relevant existing source were read through connected GitHub access.
The filtered stream discards SMC values, and synthetic polls omit B0AV, as the brief reported.
The current without-assisted selection uses the harvest flag and must change to the ruled decode marker.
Packet arithmetic independently reproduces the three worked-example battery terms, but meter_decode was not executed.
Only this resume report is committed; no implementation or acceptance check is claimed.
A working workspace is required for seat setup, baseline preservation, generators, tests, and the real synthetic CLI chain.

## WHAT CHANGED

- `.codex-report/BAT-3.md`: records the blocked intake and the resume instructions. Implements the brief's persistent PROGRESS/report requirement.
- All number-bearing source and all generated outputs remain at BY-INT's base. The BAT-2 §2–§5, §7, §8 and §12 implementation remains outstanding.

Confirmed source locations at the base:

- `joulewise/bytes_analysis.py::_filtered_stream` retains neither `poll_ns` nor `smc`, processes batches in file order, and reconstructs only selected meter samples. Retain all poll receive times and SMC metadata, or enough widened by tau plus the global maximum poll interval; order batches by rx before clock unwrapping and decoding.
- `meter_decode` returns meter-only gross/secondary energy, u and the meter-only offset bound.
- `neg8_inputs` already calls `meter_decode` for whole-request DC/rest reference energy, so correcting that function propagates the boundary once the stream preserves reference battery polls.
- `archive_records` catches `AnalysisError` from the meter join and adds the existing `bytes.meter_decode_unavailable` without discarding rails. The new missing-reading case belongs in that existing path.
- `_phase_cell` consumes `phase_edge_j` for the DC/rest bound and floor; the implementation must carry u + v consistently and retain separate per-run meter/battery disclosures.
- `reduce_models` currently selects `battery.assist` for the without-assisted description. Replace that selection with `bytes.decode_battery_assist` and print both counts per stratum.
- `tests/fixtures/bytes/campaign.py` currently writes `{"B0AC": 0}` only. Add realistic B0AV on every poll before integrating the battery term.

## WORKED EXAMPLE

No unit test has been added or executed. Read-only preparation used the packet's actual poll numbers from
`JouleWise-data@c17fdca:bat-council-20261022/data/h_decode_extract.json`, blob
`867bd81054eb35e6c91528d7580e32676133da1f`. Arithmetic was evaluated in JavaScript in the tool orchestrator;
it was not a Python, km003c_parse or meter_decode execution.

The extract's global maximum poll interval is 0.302440875 s over 93,533 polls, giving tau = 2.302440875 s.

| Run | T (s) | Decode battery polls | E_b (J) | v_start (J) | v_end (J) | Marker |
|---|---:|---:|---:|---:|---:|---|
| check-llama-70b-r01 | 56.018812894 | 280 | 0 | 0 | 0 | no |
| check-qwen35-122b-r01 | 11.017812967 | 56 | 0.7765771682061066 | 0.7765771682061066 | 0 | no |
| soak-llama-70b-r11 | 57.436307192 | 287 | 0.3961203994441993 | 0 | 0 | yes |

Qwen's seven nonzero polls, as nanoseconds after decode start on the raw clock, are:

```text
5151255     -37  12773
205211213   -37  12773
405189838   -47  12774
605216297   -47  12774
805253338   -47  12774
1005212505  -47  12774
1205201088  -47  12774
```

Soak's five nonzero polls are:

```text
45721732798 -31 12770
45921723714 -31 12770
46119268381 -31 12770
46320625006 -31 12770
46521773923 -31 12770
```

Resume by copying only required numbers into the scoped unit test with a source comment, never by adding
JouleWise-data files. Use the ruling's 1e-5 J printed-value bar: above 1e6 times float64 noise at 6,424 J
(1.4e-6 J) and six-decimal rounding (5e-7 J), below 1% of the smallest printed bound (1.1e-3 J).
The same-input program comparison bar is 1e-6 J. These are the ruling's bars, not new thresholds.

## FAULT INJECTIONS

Not implemented or run. Still required, each as a test:

- B0AC without B0AV, in decode and idle.
- B0AV without B0AC, in decode and idle.
- An entire decode with no complete battery reading.
- Charging (B0AC > 0), retaining the negative signed term.
- Batch lines out of rx order, giving the same battery term as ordered lines.

The ruled missing-span result is `bytes.meter_decode_unavailable`, reason `battery reading missing`;
only DC-input and rest values become unavailable. It is never a refusal. Refusal-census arrays have not
been executed or inspected by this seat, and no refusal site has been added.

## BIT-IDENTITY

Not run. There is no before/after output, comparison command result, field count, or new field list yet.

Before editing analysis code, preserve the current campaign and reduce it under the exact base
`bda481d5af510b29dde4976f172a20170a42c955`. Compare with the new code on a no-assist campaign whose only
SMC change is adding B0AV. Every common output field must be exactly equal, except code-provenance hashes
whose underlying file actually changes; disclose such hashes explicitly rather than silently dropping them.
Record the actual comparison scope and result. New fields must be listed separately. Exact equality is
appropriate for the intended bit-identity property; do not replace it with a numerical tolerance.

## SYNTHETIC ASSIST

Not implemented or executed. The four required large-model placements are inside decode, across decode
start, across decode end, and prefill only. Each burst must supply at least 1 J, from the ruled attribution
scale. Record actual burst joules, E_b, v, marker, and without-assisted counts after the real CLI stage chain.
The prefill-only burst must not move the term or marker beyond v. Non-assisted production-shaped polls
must carry both B0AC and B0AV. No new agreement or selection bar is authorized.

## REGISTRATION

No registration text has changed. Every BAT-2 §8 placement remains outstanding, verbatim:

- §1: replace the DC-input bullet.
- §6: replace Battery assist, including the delay-aware marker, description line, both counts and H expectations.
- §7: amend both phase-edge table cells; insert “Battery term and its edge term v” after meter u.
- §9: amend NR1's per-run C_j term and add the one-signed-delay sentence; retain meter-only dβ/dδ.
- §15: add the battery-column quantities and largest v.
- §16: replace the harvest-flag dependency with native meter battery readings and counted-only request flag.
- §20: add the BAT-2 ruling mapping row.
- Also update §6's disclose-code counts/list and Appendix A's catalog digest after generating the new catalog.

Catalog SHA before: `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`
(as recorded in BY-INT's report; not rehashed locally by this seat).
Catalog SHA after: unchanged, because no catalog change was made.

Add only `bytes.decode_battery_assist` through `scripts/build_b6_flag_catalog.py`, then regenerate only the
twelve BYTES registrations and twelve BYTES plan trees through `scripts/bytes_plan_trees.py`.
Do not regenerate alpha, beta or gamma.

## TESTS RUN

No Python tests or CLI campaign were run. No test pass, failure, count or skip is claimed.

The attempted shell-access command was:

```text
pwd && ls -ld /workspace /workspace/JouleWise /workspace/JouleWise-data
```

The tool rejected it before a process could start: “No usable execution environment is available. Wait for an
environment to become available before using this tool.” There is no process exit code. Git fetch, checkout,
seat_setup.sh and /tmp/jw-seat.env sourcing could not execute. The initial wait for the selected environment
was stopped only to inspect readiness directly; it did not produce readiness or a startup-failure cause.
The diagnostic metadata endpoint returned no retained records. No diagnostic logs or credential values were read.

Required commands after recovery (one fresh TMPDIR per module, no whole suite locally):

```bash
bash /workspace/JouleWise-data/tools/cloud/seat_setup.sh /workspace/JouleWise
source /tmp/jw-seat.env
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_analysis.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_packs.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs
TMPDIR=$(mktemp -d /tmp/jwtmp/test_bytes_agreement.XXXX) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_agreement
```

Also run the scoped catalog, import-graph and battery-reader modules listed in the brief if those files change.
Environmental failures named in seat setup must be listed, not chased. None were observed because no test started.

`tests.test_bytes_agreement` was not run. No actual failing field names are available yet. The twin remains
untouched, as required. Its future divergences must be recorded by their actual names after the implementation,
rather than inferred as executed failures here.

## CI

The requested CI branch and draft PR are to be created from the report head using connected GitHub access.
This is a report-only checkpoint, not a BAT-3 implementation or green-acceptance claim.
The PR body records the startup blocker. Check the PR and its actual head for the current run state.

## DECISIONS I MADE

- The BAT-2 ruling governs all arithmetic, marker selection, printing and registration placements.
- The 55–60 J whole-member number is not the decode correction.
- Preserve signed charging energy; do not clip or suppress sub-1 J terms.
- Use the stream-wide maximum poll gap, not a run-local gap, for tau.
- Use u + v in DC-input B/floor and rails anchor + u + v in rest; add max(v_start, v_end) to NR1's per-run bound.
- Keep dβ/dδ meter-only.
- Select the description with `bytes.decode_battery_assist`; count `battery.assist` without selecting on it.
- Print the battery column and no separate meter-only estimate line.
- Missing battery coverage follows the existing per-boundary flag path, never a refusal.
- Preserve all scope fences, including the twin and external parser.
- Do not claim a source implementation, a test execution or a generated-output check that did not occur.

## OPEN ISSUES

- Provision/restart a usable cloud workspace and complete every implementation and acceptance item in the brief.
- Re-run the original setup against this lane head; the remote report was created without a local checkout.
- Complete the baseline bit-identity comparison before analysis edits.
- Add the worked-example and fault-injection tests, large-model episodes, catalog registration and generated BYTES outputs.
- Run the required production-shaped CLI chain and module checks; list actual twin differences for BY-TWIN-BAT.
- The director must re-reduce H on the Mac without JW_B5_SYNTHETIC_ONLY, with TMPDIR under
  /Users/edr/night-archive/forward-20261021/BAT-3/tmp: check-llama-70b-r01 adds 0 J,
  soak-llama-70b-r11 adds 0.396120 J, and check-qwen35-122b-r01 adds 0.776577 J, each with the ruled bound.
- Executing review and cold gates are not claimed by this seat.

## NEEDS_RULING

none. The current blocker is execution infrastructure, not an undecided scientific choice.
