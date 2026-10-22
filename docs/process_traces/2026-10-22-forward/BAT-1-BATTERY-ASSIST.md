# BAT-1: battery assist when the workload outruns the MagSafe adapter (2026-10-21, 19:25 PDT)

Item BAT-1 of the forward-work workflow (interactive session 2dc9c377), answering Ed's request of 2026-10-21:
"also iirc, there was a problem when the workload exceeded the consumption the magsafe power supply is providing
and you operate off battery, make sure that's remidied, if it was indeed even a problem".

Seat: one Opus 5.5 agent, local (the block-6 flag files are blinded data). Analysis only; no code changed.
Scripts and outputs: `/Users/edr/night-archive/forward-20261021/BAT-1/` (untracked). Non-claim per-run tables:
JouleWise-data branch `analysis/battery-assist-20261022` (0cb3eb6), directory `battery-assist-20261022/`.

## For Ed

Yes, it was real, it is small, and one piece still needs a fix. The adapter is labelled 140 W, but the battery
started helping before the Mac reached that: the Mac's own input sensor never read more than 130.8 W and the cable
meter's highest one-second average was 134.9 W, yet whenever the Mac drew more than the adapter delivered, the
battery made up the difference for a few seconds at a time. In the five-hour BYTES check session on 2026-10-21 this
happened only on Llama-3.3-70B and Qwen3.5-122B, plus 0.14 J once on Qwen3-Next-80B; no model up to 32B took
anything from the battery, and the battery stayed at 100 % and never started charging. On 70B the battery supplied
49 to 73 J per run, nearly all of it during a warm-up run before measurement (28 to 51 J) and while the measured run
processed its 2,048-token prompt (9 to 27 J); writing the 512 answer tokens, the stretch BYTES measures, took
nothing from the battery in 17 of 18 runs and 0.4 J in the other. On 122B it supplied 1.2 to 2.5 J per run, 0.7 to
1.2 J of it while writing tokens, at most 0.14 % of that stretch's energy at the cable. Whether this matters depends
on which energy number you read. The processor's own energy counters (CPU, GPU and neural engine), which are the
main measurements, do not depend on where the power came from, and in the seconds the battery helped the processor
ran no slower and at no lower power or clock speed. The whole-machine number used in blocks 5 and 6 already adds the
battery's share back in, and no block-6 run had any battery help in any of its nine sessions. BYTES' whole-machine
number and its "everything but the processor" number read only the cable meter, so they undercount by about 1 J per
122B run and by essentially nothing on 70B; adding the battery term there has been decided but not built, so that is
the one part not yet remedied.

## What was measured, and how

Sources, all read-only, from the non-claim session `bytes-h-20261021T185555335572Z` (root
`/Users/edr/night-bytes/h-20261021T185555Z`):

- Spans: the harvest's `archive/withheld/spans.json` (member and request, `time.monotonic_ns`). Prefill and decode
  spans come from each bundle's `events.jsonl`, mapped exactly as `bytes_analysis._event_span` maps them.
- 1 s path: every SMC read in `custody/hazards/monitor/battery.jsonl`. There are 18,708 one-second `source: smc`
  lines plus the SMC read attached to each of the 313 ioreg lines, 19,021 in all, each stamped by its own
  `finished` time.
- 0.2 s path: the B0AC/B0AV block embedded in each of the 93,533 KM003C polls in
  `custody/hazards/meter/stream-001.jsonl`. These are stamped by the poll's receive time and mapped to the monotonic
  clock by the stream's own offset (−500 ns).
- DC input: the meter's own samples, `km003c_parse.integrate`, over the decode and request spans.
- Harvest records: `archive/withheld/battery-assist.json`, `archive/withheld/meter.json` and
  `archive/derived/flags.jsonl`.

The integral uses the harvest's rule, re-implemented here rather than imported. Each read holds until the next read
on the same path, for at most 5 s (`SMC_MAX_GAP_S`), and the hold is clipped to the window. The discharged energy
is the sum of −B0AC [mA] × B0AV [mV] / 10⁶ [W] × the clipped hold [s], over reads with B0AC < 0.

Bars, both set by the brief:

- (a) Two programs integrating the same reads must agree within 1e-6 J. This is the doctrine default for an
  agreement bar in the column's unit.
- (b) The 0.2 s and 1 s paths must agree within 1 s × the span's largest discharge power. B0AC refreshes about once a
  second, so either path can place a value up to one refresh early or late. On 70B that is 5.0 to 6.4 W, so the bar
  is 5.0 to 6.4 J.

### Checks

| Check | Result | Bar | Pass |
|---|---|---|---|
| A. 1 s integral here vs harvest `discharged_energy_j`, 78 phase values (pre-request, request, post-request) | max \|diff\| 0.0 J | 1e-6 J | yes |
| B. 0.2 s vs 1 s whole-member integral, 95 runs | max \|diff\| 1.03 J (soak-70b-r02) | 1 s × span max discharge power (≤ 6.4 J) | yes, every run |
| C. `withheld/meter.json` battery and meter terms re-derived with `km003c_parse.delta_machine_energy` on the stored windows, 95 runs | max \|diff\| 0.0 J and 0.0 J | 1e-6 J | yes |
| D. Runs with `battery.assist` vs runs with any negative 1 s read held in the request | 26 = 26, identical sets (70B 18, 122B 7, Next-80B 1) | sets equal | yes |
| Lead's `batt_by_stage.py`, re-run from the item dir | 18,708 SMC lines; 204 below −200 mA; min −497 mA; PDTR max 130.8 W; check-70b 59 reads / 307.1 J; soak-70b 128 / 651.9 J; test7-70b 17 / 98.4 J; 122B min −76 mA; Next-80B min −11 mA | reproduce the brief's totals | yes |

Session facts:

- No SMC read was positive (never charging).
- All 313 registry reads show ExternalConnected Yes, IsCharging No, FullyCharged Yes and CurrentCapacity 100 %.
- The adapter reports 140 W. The SMC DC input (PDTR) peaked at 130.8 W and the meter's 1 s mean at 134.9 W.
- Total discharge over the session, summed per stage: 8.9 + 98.4 + 2.4 + 0.1 + 307.1 + 10.0 + 651.9 = 1,078.8 J
  (0.31 % of the full-charge energy below).

All 70B pre-request discharge falls in the warm-up generation, 777 J over 18 runs. The prepare tail, the idle baseline
and the gap from warm-up to request read 0 J (`out/pre_request_split.txt`). The 122B warm-up adds 0.37 to 1.03 J per run.

The pre-calibration stage discharged 8.9 J, never below −20 mA. H's harvest wrote no capture entries (`captures: {}`;
H had no calibration bracket, `calibration.no_bracket`), so those joules are recorded only here.

### Per-run table (BYTES H, full-length runs of the three models that saw any discharge)

These are the full-length runs: a 2,048-token prompt and 512 decoded tokens. The short test-7 runs and every other
model read 0 J on both paths. The short runs are test-7 r02 and r04 of each model; they decode a few tokens.

"Member" is the whole member, from preparation to the post-request sentinel. "Request" is the measured run. DC-in is
the meter's gross energy over the span. Shares are battery J over DC-in J for the same span.

| Run | Model | < −200 mA reads, 1 s / 0.2 s | Min mA | Member J, 1 s / 0.2 s | Before request J | Request J (prefill / decode) | DC-in decode J | Battery share of DC-in decode | DC-in request J | Battery share of DC-in request | Harvest request J − this audit | `battery.assist` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| check-llama-70b-r01 | llama-70b | 10 / 50 | -442 | 59.73 / 59.09 | 50.87 | 8.85 (8.85 / 0.00) | 6101 | 0.000 % | 8972 | 0.099 % | 0 | yes |
| check-llama-70b-r02 | llama-70b | 12 / 60 | -479 | 51.83 / 52.38 | 40.99 | 10.84 (10.84 / 0.00) | 5995 | 0.000 % | 8863 | 0.122 % | 0 | yes |
| check-llama-70b-r03 | llama-70b | 14 / 70 | -497 | 73.43 / 73.54 | 48.20 | 25.22 (25.22 / 0.00) | 6260 | 0.000 % | 9243 | 0.273 % | 0 | yes |
| check-llama-70b-r04 | llama-70b | 11 / 55 | -466 | 57.72 / 57.98 | 45.83 | 11.89 (11.89 / 0.00) | 6001 | 0.000 % | 8879 | 0.134 % | 0 | yes |
| check-llama-70b-r05 | llama-70b | 12 / 60 | -449 | 64.03 / 64.23 | 42.95 | 21.08 (21.08 / 0.00) | 6126 | 0.000 % | 9067 | 0.233 % | 0 | yes |
| soak-llama-70b-r01 | llama-70b | 10 / 50 | -395 | 49.70 / 50.00 | 40.77 | 8.93 (8.93 / 0.00) | 6132 | 0.000 % | 9017 | 0.099 % | 0 | yes |
| soak-llama-70b-r02 | llama-70b | 13 / 65 | -461 | 61.13 / 60.10 | 48.76 | 12.37 (12.37 / 0.00) | 6033 | 0.000 % | 8908 | 0.139 % | 0 | yes |
| soak-llama-70b-r03 | llama-70b | 15 / 70 | -473 | 66.36 / 66.22 | 39.88 | 26.48 (26.48 / 0.00) | 6189 | 0.000 % | 9172 | 0.289 % | 0 | yes |
| soak-llama-70b-r04 | llama-70b | 10 / 50 | -474 | 52.15 / 52.37 | 39.94 | 12.21 (12.21 / 0.00) | 5997 | 0.000 % | 8866 | 0.138 % | 0 | yes |
| soak-llama-70b-r05 | llama-70b | 12 / 55 | -432 | 60.29 / 60.76 | 48.59 | 11.69 (11.69 / 0.00) | 6035 | 0.000 % | 8915 | 0.131 % | 0 | yes |
| soak-llama-70b-r06 | llama-70b | 12 / 60 | -495 | 65.54 / 65.20 | 38.50 | 27.05 (27.05 / 0.00) | 6206 | 0.000 % | 9179 | 0.295 % | 0 | yes |
| soak-llama-70b-r07 | llama-70b | 11 / 50 | -443 | 53.15 / 53.67 | 41.28 | 11.88 (11.88 / 0.00) | 6030 | 0.000 % | 8898 | 0.133 % | 0 | yes |
| soak-llama-70b-r08 | llama-70b | 11 / 55 | -477 | 57.94 / 58.34 | 47.18 | 10.76 (10.76 / 0.00) | 5997 | 0.000 % | 8863 | 0.121 % | 0 | yes |
| soak-llama-70b-r09 | llama-70b | 16 / 75 | -496 | 67.13 / 67.96 | 42.56 | 24.58 (24.58 / 0.00) | 6232 | 0.000 % | 9210 | 0.267 % | 0 | yes |
| soak-llama-70b-r10 | llama-70b | 12 / 60 | -466 | 60.11 / 60.85 | 49.05 | 11.06 (11.06 / 0.00) | 6031 | 0.000 % | 8914 | 0.124 % | 0 | yes |
| soak-llama-70b-r11 | llama-70b | 10 / 50 | -448 | 57.34 / 57.18 | 44.94 | 12.40 (12.01 / 0.39) | 6424 | 0.006 % | 9349 | 0.133 % | 0 | yes |
| test7-llama-70b-start-r01 | llama-70b | 8 / 40 | -466 | 49.34 / 48.84 | 28.36 | 20.98 (20.98 / 0.00) | 6305 | 0.000 % | 9265 | 0.226 % | 0 | yes |
| test7-llama-70b-start-r03 | llama-70b | 10 / 45 | -412 | 48.89 / 49.26 | 38.40 | 10.49 (10.49 / 0.00) | 6174 | 0.000 % | 9062 | 0.116 % | 0 | yes |
| check-qwen35-122b-r01 | qwen35-122b | 0 / 0 | -47 | 1.53 / 1.51 | 0.37 | 1.16 (0.09 / 1.07) | 884 | 0.121 % | 1340 | 0.087 % | 0 | yes |
| check-qwen35-122b-r02 | qwen35-122b | 0 / 0 | -61 | 1.92 / 1.86 | 0.62 | 1.30 (0.09 / 1.21) | 890 | 0.136 % | 1347 | 0.096 % | 0 | yes |
| check-qwen35-122b-r03 | qwen35-122b | 0 / 0 | -65 | 2.18 / 2.13 | 0.90 | 1.28 (0.10 / 1.18) | 890 | 0.133 % | 1348 | 0.095 % | 0 | yes |
| check-qwen35-122b-r04 | qwen35-122b | 0 / 0 | -62 | 2.15 / 2.13 | 0.72 | 1.43 (0.21 / 1.22) | 891 | 0.137 % | 1349 | 0.106 % | 0 | yes |
| check-qwen35-122b-r05 | qwen35-122b | 0 / 0 | -76 | 2.46 / 2.45 | 1.03 | 1.42 (0.18 / 1.24) | 893 | 0.139 % | 1351 | 0.105 % | 0 | yes |
| test7-qwen35-122b-start-r01 | qwen35-122b | 0 / 0 | -41 | 1.18 / 1.15 | 0.38 | 0.80 (0.07 / 0.73) | 878 | 0.084 % | 1334 | 0.060 % | 0 | yes |
| test7-qwen35-122b-start-r03 | qwen35-122b | 0 / 0 | -37 | 1.29 / 1.28 | 0.47 | 0.82 (0.00 / 0.82) | 880 | 0.093 % | 1333 | 0.061 % | 0 | yes |
| check-qwen3-next-80b-r03 | qwen3-next-80b | 0 / 0 | -11 | 0.14 / 0.14 | 0.00 | 0.14 (0.00 / 0.14) | 438 | 0.032 % | 627 | 0.022 % | 0 | yes |
| other Next-80B full runs (6) | qwen3-next-80b | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 426 to 429 | 0 | 615 to 619 | 0 | – | no |

Minimum is from the 1 s path; the 0.2 s path's minimum is the same value in every row. Full-length 70B summary:

- Member: 48.9 to 73.4 J, mean 58.7 J.
- Measured request: 8.9 to 27.0 J, mean 15.5 J, all of it prefill except soak-r11's 0.39 J of decode.
- That is 0.10 to 0.30 % of the request's DC input and 0 to 0.006 % of its decode DC input.

Full-length 122B: decode discharge is 0.73 to 1.24 J per run, which is 0.08 to 0.14 % of DC-in decode and 0.13 to
0.21 % of the decode "rest" (DC input minus rails; about 580 J).

## The 2026-10-06 reopen tests, on H's assisted runs

Method (`scripts/h_reopen.py`, output `out/h_reopen.json`):

- Each full-length 70B and 122B run's prefill and decode spans are cut into whole 1 s bins from the phase start.
- A bin is assisted when any 0.2 s poll in it reads B0AC < 0.
- Per bin the script computes rail power (rich_telemetry `rail_sum_power_w`), GPU frequency (`gpu.freq_hz`, which
  powermetrics reports in MHz), P-cluster frequency, the GPU software P-state deficit (requested minus granted,
  each weighted by `used_ratio`), the meter's DC input and decoded tokens per second.
- Matching: assisted and non-assisted bins at the same bin index of the same model and phase across repeats. The
  differences are averaged with weight min(n assisted, n not assisted). The standard error is the weighted standard
  deviation of the cell differences over √cells.
- Across runs (`out/per_run_speed.json`): the Pearson correlation between a phase's discharged J and that phase's
  speed.

| Test (ruling item 6) | What H shows | Verdict |
|---|---|---|
| Power-limit or power-mode transitions associated with assist | Thermal pressure was "Nominal" in every powermetrics sample of all 25 full-length 70B/122B measured runs. The OS thermal level was 1 at 22 of 3,742 monitor reads: 7 in the post-request sentinels of five 70B runs, 15 outside every recorded member span; none within 5 s of a negative B0AC read (`out/thermal_vs_assist.txt`). The GPU P-state deficit was lower in assisted 70B prefill seconds, −0.32 ± 0.09 states against 1.28 in matched non-assisted seconds. | None found |
| Lower rail power, frequency or tokens/s in assisted seconds against matched seconds | 70B prefill (98 assisted of 463 bins, 5 matched cells): rail +3.4 ± 0.8 W (+7.5 %), GPU +39 ± 10 MHz (+3.3 %), P-cluster +1 ± 7 MHz, DC input +7.7 ± 2.3 W. Assist marks the seconds that ran hardest; it does not mark slower ones. Across the 18 runs, prefill speed rises with prefill discharge (r = +0.96): the six runs at 78.6 to 79.5 tokens/s drew 21.0 to 27.0 J, the twelve at 76.1 to 77.1 tokens/s drew 8.9 to 12.4 J. 122B decode (13 assisted of 72 bins, 1 matched cell): tokens/s +0.17 (+0.4 %), rail −0.02 W; within the five check runs, decode discharge (1.07 to 1.24 J) and speed (46.47 to 46.61 tokens/s) show no order. The one apparent case is 70B decode: its only 2 assisted seconds (soak-r11, −31 mA, 0.39 J) coincide with GPU dips. But r11 shows the same dips at 3 other decode seconds with no discharge, and r11 is excluded for `agent.presence` and `thermal.os_level_nonzero`. Its dips go with the agent and the heat, not the battery. | None found |
| Battery temperature rising in assisted stages | 29.69 to 30.36 °C over the whole session (ioreg `Temperature`, about one read a minute). Change over each 70B stage: check −0.05 °C, test7 +0.19 °C (includes the model load), soak −0.05 °C. Change over qwen3-14b, which had no assist: +0.13 °C. | None found |

**The 2026-10-06 ruling stands.** Assist is disclosed and not excluded. The processor rails do not depend on the
source, and none of the three reopening signals appears.

Limits: the matched cells are few, because assist sits in the first 0 to 8 s of 70B prefill in most runs. The
one-second bins also cannot resolve sub-second transients. Neither changes the direction of the 70B prefill result.

## Block 6 (energies blinded; structure only)

Codes and members were counted from `archive/derived/flags.jsonl`, `b6-flags.jsonl` and `exclusions.json` of each
session (`scripts/b6_battery_counts.py`; flag records / distinct members). No energy, power, current or duration was
printed.

| Session | `battery.assist` | `battery.assist_outside_request` | `battery.member_span` | `battery.unmeasured` | `battery.accumulator_activity` | `meter.battery_activity` | Members excluded (any code) | Members excluded for a battery code |
|---|---|---|---|---|---|---|---|---|
| r1-alpha | 0 | 0 | 0 | 0 | 1 / 1 | 0 | 3 | 0 |
| r1-beta | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| r1-gamma | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| r2-beta | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| r2-gamma | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| r3-alpha | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| r3-beta | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| r3-gamma | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| r4-alpha | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |

- **Zero charging exclusions are confirmed.** No `battery.member_span`, `battery.unmeasured` or
  `battery.accumulator_excursion` appears in any session. The 19 excluded members carry only
  `member.anchor_not_bounded`, `member.target_phase_precheck_failed` and `member.whole_window_member_failure`.
- No `battery.smc_unavailable` appears, so SMC coverage was complete.
- `meter.battery_activity` fires when any 0.2 s poll inside a request reads B0AC ≠ 0. It is absent everywhere, so
  the second path also saw no discharge in any block-6 request.
- r2-alpha was prepared but never ran: it has an empty `runs-parent` and no archive. The nine sessions above are the
  nine that count.
- All nine battery journals read 100 % and never charging (`scripts/charge_resume_scan.py`).

## Boundary by boundary

| Boundary | Does adapter overload change the number? | By how much (H; block 6) | Remedied? |
|---|---|---|---|
| Rails (powermetrics CPU + GPU + ANE) | No. The rails are regulated downstream of the supply. The reopen tests show no lower power, frequency or speed in assisted seconds. | 0 J | Nothing to fix (2026-10-06 ruling stands) |
| Block-5/6 whole machine (`withheld/meter.json` dE_machine) | Yes, by the battery's joules; the code adds them back | H: battery term 0 to 27 J per request, re-derived exactly. Block 6: 0 J (no assisted member, no nonzero poll in any request) | **Yes.** `km003c_parse.delta_machine_energy` adds dE_battery = −B0AC × B0AV / 10⁶ W over the same window. It is called by `joulewise/b5/harvest.py` `_Harvest.meter_joins` (origin/main line 6220; `lane/2026-10-17-b6-packs-registered` line 6252; `lane/2026-10-20-l9-ruling-build` line 6889). L9's `disclosures.MACHINE_BOUNDARY` reads "whole-machine DC input plus the battery term" |
| BYTES DC input (decode span, `bytes_analysis.meter_decode`) | Yes. It integrates only the meter's samples, and `_filtered_stream` drops the SMC blocks | 70B: 0 J in 17 of 18 runs, 0.39 J in one (≤ 0.006 %). 122B: 0.73 to 1.24 J per run (0.08 to 0.14 %). Next-80B: ≤ 0.14 J. Every other model: 0 | **No.** Backlog item 9 (lead's ruling, 10-21 18:5x): machine input = cable + battery discharge over the same span, with the battery printed as its own column. No branch carries it yet (checked: `lane/2026-10-20-bytes-analysis-a8` 0743a7b90 lines 420 to 460, `lane/2026-10-20-b6-blinding-group`, every other bytes branch) |
| BYTES rest (DC input − rails, decode span, about line 672) | Yes. All of the missing battery joules land in rest | 122B: 0.13 to 0.21 % of rest (about 580 J). 70B: ≤ 0.009 % | **No** (same item 9) |
| BYTES "without assisted runs" line (draft registration `bytes_pack_v1.md` §6, on `docs/2026-10-20-bytes-registration`) | It changes which units the line keeps. `battery.assist` is decided over the whole request, prefill included | In H, all 18 full 70B runs and all 7 full 122B runs carry it, so s5's and s6's lines would print "below the registered minimum of 5 units" | **Partly.** Item 9 scopes the marker to the decode span. In H that keeps 17 of 18 70B runs for s5, but 0 of 7 122B runs for s6, which is assisted in decode every time. With the battery term added, s6's primary line is corrected anyway |
| DIFFICULTY `wall` (`difficulty_pack_v2.md` §2, line 53) | In principle; meter only, flagged `battery_assist` | Models are Qwen3 1.7B, 4B and 8B. H read 0 J for every dense model up to 32B and for 30B-A3B | Not built (no adapter yet). Expected 0 J; can reuse item 9's term |

The arm refusal at idle stands: ExternalConnected No, IsCharging Yes, or |B0AC| > 200 mA on an idle machine
(`joulewise/hazards/battery.py`, module docstring line 48). The discharged energy goes to `withheld/` as ruled.

## Charging risk inside a pass session

- **State of charge over H:** 100 % at all 313 registry reads. IsCharging was never Yes, and no SMC read was
  positive. AppleRawCurrentCapacity read 7,457 mAh at the start, 7,465 at its highest and 7,440 at the end. That fall
  of 17 to 25 mAh (0.22 to 0.33 % of AppleRawMaxCapacity, about 0.8 to 1.2 kJ at 12.78 V) is consistent with the
  1.08 kJ integrated from the SMC reads.
- **Full-charge energy:** median AppleRawMaxCapacity 7,662 mAh × median ioreg Voltage 12.781 V = 352.5 kJ
  (97.9 Wh; DesignCapacity 8,579 mAh, 313 cycles).
- **Projection:** the pass-1 module run counts (`configs/b6/packs/bytes-s*-p1/registration.json` on
  `lane/2026-10-22-bytes-c4-pins`) × H's whole-member discharge per full-length run of that model. The run shape
  is the same as H's: a 2,048-token prompt, 512 decoded tokens, 1 warm-up run and 57.6 s of idle. H's reference runs
  and every small model read 0 J.

| Sub-pack (pass 1) | Modules (runs) | H member J per run, mean / max | Session discharge, mean / max | Share of full charge, mean / max |
|---|---|---|---|---|
| s1 | qwen3-1p7b (50), qwen3-4b (50) | 0 / 0 | 0 J | 0 % |
| s2 | qwen3-8b (50), qwen3-30b-a3b (50) | 0 / 0 | 0 J | 0 % |
| s3 | qwen3-14b (50), qwen3-next-80b (50) | 0 and 0.02 / 0.14 | 1 J / 7 J | 0.000 % / 0.002 % |
| s4 | qwen3-32b (50), qwen3-8b-8bit (50) | 0 / 0 | 0 J | 0 % |
| s5 | llama-70b (50) | 58.7 / 73.4 | 2,933 J / 3,671 J | 0.83 % / 1.04 % |
| s6 | qwen35-122b (50) | 1.81 / 2.46 | 91 J / 123 J | 0.026 % / 0.035 % |

Pass 2 runs the sub-packs in reverse order, so s5-p1, s6-p1, s6-p2 and s5-p2 would run back to back. Without a
top-off between them, the battery would fall by about 6.0 kJ in all (1.7 %), or 7.6 kJ (2.2 %) at H's per-run maxima.

**The state-of-charge drop at which this Mac resumes charging: unmeasured.**

- Across 56 distinct hazard-monitor battery journals on disk (blocks 5 and 6, BYTES H, rehearsals; 8,334 registry
  reads), IsCharging is never Yes, so no record shows a charging onset (`out/charge_resume_scan.json`, local only).
- Two recorded drops did not start a charge. In H, 1.08 kJ (0.31 % of full charge) went out at the 100 % setting.
  In block 5, under the then-80 % limit, the battery sat at 79 or 80 % through whole sessions.
- The larger of the two, about one point of charge below the limit, is about one s5 session's projected drop
  (0.83 to 1.04 %). Neither rules a mid-session top-off in or out.

Consequence:

- A charging read inside a member is `battery.member_span` (EXCLUDE_MEMBER). If a top-off began during an s5 or
  s6 session, every member whose span it overlaps would be excluded; an s5 member lasts about 270 s. How long a
  top-off lasts depends on the charge it restores and the charge current, and neither is on record.
- The arm refuses while charging, so a session cannot start during a top-off.

Whether a pass session loses members this way depends on the unmeasured threshold. The monitor already polls
IsCharging every 5 s (writing a line on any change) and reads B0AC every second, so the first s5 session will show
it directly. No new enforcement is
proposed: the hazard is already measured and already excludes the right members (doctrine gate 5).

## The ops:battery branch

`lane/2026-10-21-battery-inrun` is absent on origin and locally (checked 19:24 PDT). The ops:battery brief made the
branch conditional on the battery not being sampled during runs. It is sampled: the hazard monitor reads B0AC/B0AV
about once a second, and every 0.2 s KM003C poll carries them. The seat reported that the remedy exists (STATE.md,
"Results in hand"). There is nothing to disposition.

## For the lead

1. **BYTES battery term (backlog item 9) is the only unremedied boundary.** It is worth about 1.1 J per 122B decode
   (0.13 % of DC input, 0.2 % of rest) and nothing measurable on 70B decode. It is claim-path, so it needs a build,
   a twin and both cold passes. The synthetic worlds need a burst inside and outside decode above the 1 J bar.
2. **The without-assisted line will be empty for s6** even after the marker is scoped to decode (7 of 7 122B runs).
   This is a description line, not an exclusion.
3. **Aside, not battery:** 5 of the 18 full-length 70B runs in H carry `thermal.os_level_nonzero` (EXCLUDE_MEMBER).
   Those are check-r02 and soak r02, r05, r08 and r11; r11 also carries `agent.presence`. All the level-1 reads fall in
   post-request idle sentinels or between runs, never in a request. That is an s5 yield question for BY-0 and C5,
   not this item.

## Reproduce

These commands run from any directory. `KP` is `joulewise/external/km003c_parse.py` at origin/main ef520743c,
byte-identical to H's checkout c10b6895f. The registrations come from `lane/2026-10-22-bytes-c4-pins`.

```
H=/Users/edr/night-bytes/h-20261021T185555Z; B=/Users/edr/night-archive/forward-20261021/BAT-1; export TMPDIR=$B/tmp
R=/Users/edr/code/JouleWise; KP=$B/tmp/km003c_parse.py
git -C $R show origin/main:joulewise/external/km003c_parse.py > $KP
for s in 1 2 3 4 5 6; do mkdir -p $B/tmp/regs/bytes-s$s-p1; git -C $R show origin/lane/2026-10-22-bytes-c4-pins:configs/b6/packs/bytes-s$s-p1/registration.json > $B/tmp/regs/bytes-s$s-p1/registration.json; done
/opt/homebrew/bin/python3.13 -I $B/scripts/batt_by_stage.py $H/custody/hazards/monitor/battery.jsonl $H/custody/night/chain-stages.jsonl
/opt/homebrew/bin/python3.13 -I -B $B/scripts/h_battery_runs.py $H $KP $B/out/h_battery_runs.json $B/out/h_battery_runs.csv
/opt/homebrew/bin/python3.13 -I -B $B/scripts/h_reopen.py $H $KP $B/out/h_reopen.json
/opt/homebrew/bin/python3.13 -I $B/scripts/h_battery_state.py $H $B/out/h_battery_state.json
/opt/homebrew/bin/python3.13 -I $B/scripts/summarise.py $B/out/h_battery_runs.json $B/out/h_battery_state.json $B/tmp/regs $B/out/summary.json
/opt/homebrew/bin/python3.13 -I -B $B/scripts/pre_request_split.py $H
/opt/homebrew/bin/python3.13 -I $B/scripts/per_run_speed.py $B/out/h_battery_runs.json
/opt/homebrew/bin/python3.13 -I $B/scripts/thermal_vs_assist.py $H $B/out/h_battery_runs.json
/opt/homebrew/bin/python3.13 -I $B/scripts/b6_battery_counts.py /Users/edr/night-b6/sessions/r*
/opt/homebrew/bin/python3.13 -I $B/scripts/charge_resume_scan.py /Users/edr/night-b6 /Users/edr/night-bytes /Users/edr/night-archive /Users/edr/night-custody
```
