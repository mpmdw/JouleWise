Fix round 1 corrections and verification: [BY-H2-fix1.md](BY-H2-fix1.md).

# BY-H2 — remainder implementation handoff (2026-10-22)

## PROGRESS
- SLICE 4 DONE: R1 remainder measurements now read staged pack tree/collection plan; C5 receives that subset plan. Named sizing.c5_remainder_checks_absent flag is retained and printed because C5 requires H's missing check runs. R2 docstring now states integer ended-started stage time, with no added endpoint second.
- SLICE 4 DONE: extended real-writer remainder prepare/harvest/desk regression passes for both soak choices (1 test, 108.448 s); full session module passes (35 tests, 198.707 s). Gates: 7 pass; refusal census: 23 pass, 1 existing skip. No generated kit, disk/span arithmetic, physical refusal or arm changes. All launched commands completed.
- DIRECTOR EVIDENCE (supplied at slice-4 intake): both real dry prepares at 16bc5d8f9 were STAGED, ledger SHA-256 unchanged, spans 16817.33/13804.91 s, P 63878576237/56122258559 B, ordered stages and battery thresholds verified. Director independently re-derived all span terms from H journals. R1/R2 executing-review disposition and final CI remain pending.
- DONE: implementation and local focused verification complete. Slice 3 began clean at f2f9bc72e; added assertions for prepare's printed stage order/counts and completed this report. Director owns commits/pushes because .git is read-only here.
- DONE: both remainder modes prepare STAGED through the real writer in production-shaped synthetic tests; source ledger hash and full-kit bytes stay unchanged. Full session module: 35 tests pass; strengthened printed-order test rerun passes.
- DONE: kit tests 4 pass; gates 7 pass; refusal census 23 pass (1 skip); generator --check passes. Import graph: 5 pass, 1 known sandbox process-group environmental failure (NULL rather than GO); no bypass attempted.
- DONE: read-only H journals yield full span 15635.331989693057 s / maximum 33360 s and r12 span 12622.910209347223 s / maximum 30360 s (corrected in fix round 1). P is 63878576237 B full, 56122258559 B r12. No live validation claimed.
- NEXT: director commits/pushes this slice, dispositions R1/R2, runs final executing review and CI, and prepares the real arm notice. Do not install/arm until Ed lifts the pause and lead clears the quiet-Mac gates.
- OPEN: executing ACCEPT review, CI and PR are director-owned. Standalone probe B/N require quiet-Mac memory observations and rehearsal; procedure below. No agent measurement, install, launchd action or arm was performed. No launched process remains running.

## SUMMARY
- Added prepare --remainder --soak-70b full|r12 --measured-session H_ROOT.
- Full is the default; r12 selects only the original 70B r12 config bytes.
- Distinct bytes-h2- identity and private runs/custody/backup roots separate the new session from H.
- All ten check stages are omitted; fresh test7 starts accompany all three ends.
- Fixed work and midpoint references remain, with ordered stage/count output before STAGED/INPUTS_ONLY.
- Span comes from H journals, one measured cohort spread, registered settles and a named B6 closing envelope.
- Subset P uses the unchanged H-DISK-RULING formula, native arm budget and non-purgeable free-byte line.
- Desk preserves native per-run flag_codes, including battery.assist, in MEASUREMENTS.json.
- Slice 4 fixes the executing review's remainder desk source-path defect and span docstring; C5's absent-check limitation is a printed flag.
- Director reports both real dry prepares STAGED with unchanged ledger, matching span/P and retained battery thresholds; final executing review and CI remain director-owned.

## DESIGN
Slice-4 R1 disposition: only for state['remainder'], measurements reads plan_tree.json and collection_plan.json from state['inputs']['pack_root']; desk sends that same staged collection plan to C5. The underscore-path full kit remains a source symlink and the full-session code paths remain unchanged. C5 requires five checks per model before sizing; those checks live in H, so the remainder prints and retains sizing.c5_remainder_checks_absent. This is a flag, with no new refusal or cross-session merge. R2 disposition: the docstring now describes ended_epoch_s-started_epoch_s per shell stage row, matching the existing arithmetic and derive_sizing's stage-time convention. No extra second or padding is added; the director's verified spans stay unchanged.

CLI: `prepare --measurement-root FRESH --session-root SCRATCH --remainder --soak-70b full|r12 --measured-session H_ROOT`. Existing full prepare/install/desk CLI and generator are unchanged. Selection occurs only inside measurement_view's disposable tree; ordinals, predecessor/successor links, science, collection plan/hash, manifests and identity inventory are rebuilt there. All selected config bytes are copied unchanged. No new committed kit file or member config is generated.

`chain.stage_plan` and real `plan.write_window_plan` accept both trees. Reference-midpoint stays because acceptance._stage_roles uses the midpoint_reference input ID and harvest._neg8_disclose requires the NEG-8 (3,1,3) roles. The selected expected counts below are stage counts, with collection counts denoting members. Prefix every stage ID with `bytes-mac-check-`.

| Stage | Kind | full / r12 |
|---|---|---|
| bracket-reservation | bracket_reservation | 1 / 1 |
| pre-calibration | calibration_capture | 1 / 1 |
| bound-collection | campaign_collection | 18 / 18 |
| bound-derivation | bound_derivation | 1 / 1 |
| reference-start | campaign_collection | 3 / 3 |
| test7-llama-70b-start | campaign_collection | 4 / 4 |
| test7-qwen35-122b-start | campaign_collection | 4 / 4 |
| test7-qwen3-next-80b-start | campaign_collection | 4 / 4 |
| reference-midpoint | campaign_collection | 1 / 1 |
| soak-llama-70b | campaign_collection | 12 / 1 |
| soak-qwen35-122b | campaign_collection | 12 / 12 |
| test7-llama-70b-end | campaign_collection | 4 / 4 |
| test7-qwen35-122b-end | campaign_collection | 4 / 4 |
| test7-qwen3-next-80b-end | campaign_collection | 4 / 4 |
| reference-end | campaign_collection | 3 / 3 |
| post-calibration | calibration_capture | 1 / 1 |
| whole-window-verdict | whole_window_verdict | 1 / 1 |
| backup | backup | 2 / 2 |

Totals: 73 or 62 members. Model counts (70B,122B,Next80B,reference): (16,16,4,37) or (5,16,4,37). Calibration screen/verdict and corpus derivation remain chain-owned nested work. Missing H journals produce sizing.h_journal_unavailable and INPUTS_ONLY with null span/window; no pilot substitution. Record/writer conditions remain printed flags. Existing physical model/disk hazard refusal sites are unchanged; no new refusal or import-registry entry is needed.

## SPAN
Read-only arithmetic on H's real files, not a measurement or real prepare:
- chain-stages SHA-256: b49589884f71de69838732b3a2543721a8d7e3f6bf2049bfa1eaf147a85a5635.
- run_clock SHA-256: 2c3168abc635462a6170e6ec94e1de38f15a3bc93062f45df7e7d20e5a5dbfed.
- Shared margin m = max(max/min-1) within identical model/quantization/workload/sampling/hardware cohorts, across H's observed members. Winning cohort: Next80B large, 160.82098579406738 / 154.66629195213318 - 1 = 0.039793375558773825 (3.9793375558773825%). Apply once to member seconds; fixed work and residuals receive no extra margin.
- Maximum measured collection residual O = bound collection 2442 - sum(18 member walls 2271.1831274032593) = 170.81687259674072 s. Applied once per unobserved soak. Shell durations use their integer endpoint differences, as derive_sizing does; no extra padding constant.

The table gives each base b and member component M; each row contributes b + m*M. Values shown to six decimals for readability; receipt JSON retains full precision. Prefix stage IDs with bytes-mac-check-. Same rows apply to both modes except the 70B soak.

| Stage | b (s) | M (s) | m*M (s) | Source |
|---|---:|---:|---:|---|
| bracket-reservation | 1.000000 | 0.000000 | 0.000000 | bracket-reservation |
| pre-calibration | 227.000000 | 0.000000 | 0.000000 | pre-calibration, pre-calibration.screen, pre-calibration.window-calibration-verdict |
| bound-collection | 2442.000000 | 2271.183127 | 90.378043 | bound-collection, bound-collection.retry-decision |
| bound-derivation | 719.000000 | 0.000000 | 0.000000 | bound-derivation.corpus, bound-derivation |
| reference-start | 397.000000 | 379.363332 | 15.096148 | reference-start |
| test7-llama-70b-start | 807.000000 | 781.371997 | 31.093429 | test7-llama-70b-start |
| test7-qwen35-122b-start | 649.000000 | 623.024698 | 24.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-start | 598.000000 | 571.416020 | 22.738572 | test7-qwen3-next-80b-start |
| reference-midpoint | 128.000000 | 127.715171 | 5.082218 | reference-midpoint |
| soak-llama-70b | 3331.327781 | 3160.510908 | 125.767398 | soak-llama-70b-r01, soak-llama-70b-r02, soak-llama-70b-r03, soak-llama-70b-r04, soak-llama-70b-r05, soak-llama-70b-r06, soak-llama-70b-r07, soak-llama-70b-r08, soak-llama-70b-r09, soak-llama-70b-r10, soak-llama-70b-r11, bound-collection: measured collection residual |
| soak-qwen35-122b | 2372.714790 | 2201.897917 | 87.620951 | check-qwen35-122b-r01, check-qwen35-122b-r02, check-qwen35-122b-r03, check-qwen35-122b-r04, check-qwen35-122b-r05, test7-qwen35-122b-start-r01, test7-qwen35-122b-start-r03, bound-collection: measured collection residual |
| test7-llama-70b-end | 807.000000 | 781.371997 | 31.093429 | test7-llama-70b-start |
| test7-qwen35-122b-end | 649.000000 | 623.024698 | 24.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-end | 598.000000 | 571.416020 | 22.738572 | test7-qwen3-next-80b-start |
| reference-end | 397.000000 | 379.363332 | 15.096148 | reference-start |
| post-calibration | 236.000000 | 0.000000 | 0.000000 | H pre-calibration capture alone 215 + chain post-minus-pre countdown 20 + session-status stamp bound 1 |
| soak-llama-70b (r12 alternative) | 434.192782 | 263.375909 | 10.480616 | same r01-r11 mean plus O |

The identical H stages use their complete stage envelopes: pre = 215 capture + 0 screen + 12 verdict = 227 s; bound derivation = 356 corpus + 363 derivation = 719 s. Test7/reference ends reuse their own starts; post uses only the 215 s pre capture, plus the code-derived 20 s countdown delta and 1 s session-status upper stamp endpoint ([0,1), integer shell stamps as in derive_sizing.py). The director cross-checked six B6 journals (r1-alpha/beta/gamma, r2-beta/gamma, r3-alpha): post capture 236–238 s plus session-status 0–1 s, against pre capture 215–217 s; these are cross-checks, not code inputs. The H 70B soak mean is 263.37590902501887 s from r01-r11; multiply by 12 or 1. The 122B mean is 183.49149308885846 s from check r01-r05 and test7-start r01/r03; multiply by 12. No reference workload is mixed into either large-workload mean.

Additional terms:
- Whole-window-verdict: 0 s; backup: 0 s. Both are desk steps excluded from the chain (`joulewise.b5.chain.DESK_KINDS`). The former 1191 s term was unrelated B6 non-collection work and is removed.
- Settles: (12 collection stages + 1 pre-calibration) * chain.SETTLE_S=60 = 780 s. Post has no added settle.
- Full: sum(b + m*M) + 780 = 15635.331989693057 s, printed ceiling 15636 s (4 h 20 min 36 s).
- r12: 12622.910209347223 s, printed ceiling 12623 s (3 h 30 min 23 s).
- window_max_s = 60*ceil((ceil(span)+3300 T0 +7200 pause +7200 WAIT)/60): 33360 s full, 30360 s r12. Uses plan_inputs.window_max_s unchanged.

## DISK
P = 2*(B+WAIT)+fixed. The source is registration/sizing_b5.json disk_derivation; the helper calls registration.derive_sizing.apply_disk_ruling unchanged with only selected inventory counts. No measured-H alternative changes the refusal line. The table retains exact rational registered allowances; multiply each by its count and sum per basis.

| Model | count full/r12 | stream allowance s | wall allowance s |
|---|---:|---:|---:|
| llama-70b | 16/5 | 9548214357147367/50000000000000 | 4746400816793639/20000000000000 |
| neg8_reference | 37/37 | 2475038689504830954481754541426818773/25000000000000000000000000000000000 | 14122618421581197/100000000000000 |
| qwen3-next-80b | 4/4 | 10830196702074579/100000000000000 | 7752958077403059/50000000000000 |
| qwen35-122b | 16/16 | 11577116221769523/100000000000000 | 17078676005436927/100000000000000 |

max_observed_bundle_bytes_per_stream_s = 16271360000000000000000/8813392312498763 B/s.

max_observed_bundle_bytes_per_wall_s = 1162240000000000000000/893951484135219 B/s.

| P term | full | r12 |
|---|---:|---:|
| stream_seconds | 225100807958010352315824918032792294601/25000000000000000000000000000000000 | 172585628993699833815824918032792294601/25000000000000000000000000000000000 |
| wall_seconds | 1237531427648210713/100000000000000 | 122059922840570071/12500000000000 |
| stream_basis_bytes | 16623321204 | 12745162365 |
| wall_basis_bytes | 16089335406 | 12695357835 |
| B_bytes | 16623321204 | 12745162365 |
| extra_wait_raw_bytes | 13292701363 | 13292701363 |
| peak_copies | 2 | 2 |
| fixed_retained_bytes | 4046531103 | 4046531103 |
| estimated_footprint_bytes | 63878576237 | 56122258559 |

B = max(ceil(stream_rate*stream_seconds), ceil(wall_rate*wall_seconds)); WAIT = ceil(stream_rate*7200). Both modes retain c=2, WAIT=13292701363 B and fixed=4046531103 B. Native arm keeps its three-copy calculation, q=floor(c*B/(3*n)), with headroom=(c*B-3*n*q)+c*WAIT+fixed; total is P exactly, without a reserve. Prepare prints allowances, counts, bases, WAIT, c, fixed, P, f_bavail*f_frsize and separately labelled purgeable bytes. Only the former free count decides the physical disk line. Slice-3 df showed 66 GiB available at intake and 65 GiB at completion, above the brief's 10 GiB stop line; this is not a real prepare statvfs acceptance result.

## PROBE
Separate quiet-Mac step. chain campaign_collection dispatches campaign_runner with BenchmarkConfig members; bytes_stream_test.py has no such runtime adapter. Driver-wide KM003C coverage alone does not supply member rails over its span, so a nominal campaign stage would misrepresent capture.

Director's later quiet-Mac procedure (draft only; no command below executed here):
1. In the Interactive night-agent context with agents cleared, measure usable memory and cache capacity C in bytes. Choose an explicit positive integer B>C that the MLX uint8 allocation AND reduction workspace actually fit without memory-pressure intervention. Retain the cache/memory observations and allocation rehearsal. The README supplies no universal numeric B; this session must not guess it from a model size or bandwidth.
2. Rehearse with explicit integer N0 (initially 1), retaining receipt duration d. Select final integer N=ceil(3600*N0/d) for the README's approximately one-hour target, then record literal decimal B and N in the lead packet. The observed d includes dispatch/reduction; no guessed bandwidth default. N0=1 is one actual iteration, 3600 is the requested hour. B/N remain lead-owned pending these measurements.
3. From the quiet Interactive foreground controller, start these two supervised children BEFORE the probe (paths are lead-filled, fresh outputs):

```sh
sudo -n /usr/bin/powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o PROBE/rails.plist
FRESH/.venv/bin/python -B FRESH/scripts/km003c_monitor.py --out PROBE/km003c.jsonl --stop-file PROBE/meter.stop
```

These are concurrent children, not sequential blocking shell lines. The rails argv is the production adapter's command with 100 ms from the member's registered 10 Hz sampling. Start meter at plain QoS (default 200 ms polling), retain stdout/stderr and child identities, and wait for a complete rails plist frame and a streaming KM003C header before the probe. Verify observed rails cadence in that context; a launchd rehearsal at 250 ms is not the member-cadence evidence. Keep periodic paired CLOCK_REALTIME/CLOCK_MONOTONIC_RAW observations during capture, each RAW-before / wall / RAW-after, with read-skew recorded. The controller must guarantee cleanup on probe failure or interruption.

```sh
FRESH/.venv/bin/python -B FRESH/scripts/bytes_stream_test.py --bytes B --repeats N --out PROBE/receipt.json
```

4. After receipt completion, retain at least one complete rails interval and meter poll beyond end_ns, then stop rails using the owned process identity with SIGTERM (the production adapter uses terminate, waits up to 10 s, then kill and reap if necessary), create meter.stop and wait for its trailer; reap both children and verify none remain. Keep every raw frame, clock pair, stderr and termination receipt. Lead owns the bounded controller invocation; no install/launchd/arm is needed for this separate probe.
5. The probe already reports RAW [start_ns,end_ns], excluding allocation/fill. Map rails' UTC interval endpoints to RAW using the contemporaneous paired clock fit (retain fit/skew/residual); derive interval support from native elapsed_ns, never from presumed 100 ms timing. KM003C tx/rx are already RAW; decode queued samples with the existing meter harvest timing logic and retain their polling/timing uncertainty. Integrate interval overlaps with the exact receipt span, including boundary partial intervals and their uncertainty; never use the entire streams. Disclose gaps, clock steps, absent meter or unsupported boundary mapping. B*N is logical uint8 payload bytes, not a hardware-controller count. Preserve the receipt with harvest. This is a packet draft, not a tested standalone capture controller.

## BATTERY
The staged plan retains its native hazard_window/thresholds and uses driver.production_seams.monitor_argv -> hazard_monitor.build_config. DEFAULT_CADENCE battery_smc_s=1.0 remains active; harvest's deciding-phase battery.assist disclosure and withheld/battery-assist.json retention are unchanged. Desk now splits native CSV flag_codes on semicolons into each MEASUREMENTS.json run and excludes this textual list from numeric-field checks. Real harvest/export/desk tests compare every output run's codes and exercise empty/populated lists.

H's supplied observations predict assistance on the large 70B members (soak r01-r12 plus test7 starts/ends r01/r03 =16 full; soak r12 plus four test7 large members =5 r12) and 122B (twelve soaks plus four test7 large members =16 either mode). No expected flag is synthesized on these or reference members. This retains disclosure; it does not remedy hardware delivery limits or implement the separate BYTES battery-energy estimator.

## TESTS RUN
### Slice 4
All commands use the repository root and independent TMPDIRs. No whole suite, live capture, install or arm command ran.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates`

7 tests in 0.364s; exit 0, OK.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist`

23 tests in 13.299s; exit 0, OK (skipped=1: existing block-5 design branch absent).

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.SessionTests.test_remainder_prepare_real_writer_both_soaks_and_journal_math`

1 test, both full/r12 subtests, in 108.448s; exit 0, OK. Both invoke the real writer, harvest, acceptance, export, measurements and C5 CLI. Remainder overhead is finite and matches the independently derived fixture residual (5*member_count/12 seconds, using 15 s member walls within 20 s slots). Both C5 argv paths name the staged subset; the named missing-check flag is printed/retained and source ledger hash remains unchanged. Before R1 this regression would encounter null overhead (22 full collections expected versus 12 observed) and the full-kit C5 argv. Existing C5 remains unavailable on the intentionally incomplete synthetic calibration/floor evidence.

The first extended remainder regression run exited 1 (1 test, 2 subtest failures in 0.201s) because its new assertion counted 123 collection-plan members. Corrected that fixture assertion to the actual 98 science members; the full tree dispatches 25 additional scaffold members, 123 total. Implementation was unaffected.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session`

35 tests in 198.707s; exit 0, OK. Includes both remainder desk subtests and unchanged full-kit prepare/real harvest/export/desk/C5 coverage. No skips or environmental failures in this module. `git diff --check` passed after all code/test/report edits. Slice-4 intake/completion disk checks remain above the 10 GiB stop line (65/62 GiB available). No import or generator change: prior kit/import checks stand; the director requested session/gates/refusal reruns for this slice. All launched test commands completed; no local process left running.

### Slice 3
Slice 3 exact commands below ran from repository root, each module with a fresh TMPDIR. All test runs set JW_B5_SYNTHETIC_ONLY=1; no whole-suite invocation. No live campaign was run. Unit install/arm checks use synthetic/hardware seams, not a real install or arm.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session`

35 tests in 90.135s; exit 0, OK.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_mac_kit`

4 tests in 0.149s; exit 0, OK.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates`

7 tests in 0.361s; exit 0, OK.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist`

23 tests in 13.000s; exit 0, OK (skipped=1: block-5 design branch absent in this clone).

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph`

6 tests in 2.696s; exit 1, FAILED (failures=1); 5 pass. test_a_complete_arm_and_monitor_run_load_no_retired_module expected GO, got NULL. Prior slice diagnostic proves sysmond/pgrep process-group census unavailable in sandbox; do not chase or bypass..

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.SessionTests.test_remainder_prepare_real_writer_both_soaks_and_journal_math`

1 test in 0.205s; exit 0, OK, both mode subtests after adding printed-order/count assertions.

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check`: exit 0, `verified non-claim Mac kit`.

`git diff --check`: initial report check found one extra EOF blank line; removed it, then final check exited 0 with no output. Full module loaded before the final assertion-only edit; the focused remainder test then passed on those exact final assertions. No implementation changed in slice 3.

## END-TO-END
Director-supplied executing evidence at slice-4 intake: real fresh-checkout dry prepare at 16bc5d8f9 printed STAGED for full and r12, span 16817.33/13804.91 s, P 63878576237/56122258559 B, ordered stages and unchanged ledger SHA-256. Staged battery thresholds were retained. Director independently re-derived all span terms against H's journals. This is attributed director evidence, not an action run by this slice. Final R1/R2 disposition/ACCEPT and CI remain director-owned.

Production-shaped fixture uses the appendix member durations (rounded milliseconds), integer stage seconds, original member/config identities and real tree. Both modes call prepare -> measurement_view -> real plan.write_window_plan -> chain.stage_plan/render path, not a mocked plan result. Only ledger head-status Git lineage inspection is patched to admit the synthetic checkout; the writer, allowance authentication, manifests, chain and budgets are real. Hardware identity producer and disk snapshots are deterministic synthetic boundaries.

Both print bytes-h2- session identity, every span source/term, programmed ceiling/window, complete subset disk derivation, all 18 ordered stage IDs/kinds/counts, then preparation_status: STAGED. Tests independently hand-compute every base/member/margin/span/window term, exact rational P terms, check 73/62 members, stage order/counts, ledger SHA-256 unchanged and source full-kit byte identity. Missing-journal regression prints INPUTS_ONLY and no fabricated plan. Existing full prepare real-writer and desk chain tests pass. These tests are synthetic execution evidence only; real dry preparation is attributed to the director above.

## ARM PACKET DRAFT
Before prepare, the lead clears seat TMPDIRs and finished worktrees, then runs `df -g /Users/edr` immediately before prepare. Prepare correctly refuses below P. Reviewer measurement on 2026-10-22: prepare takes about 6–13 s with the Mac under load.

Lead fills FRESH and SCRATCH, choosing the 70B option from BY-0 (default full). FRESH must be the director's new measurement clone with the committed 402-row ledger and reproduced .venv. Do not use the h2 ledger with its two extra reservations. No access to the director's checkout occurred here.

```sh
FRESH/.venv/bin/python -B FRESH/scripts/bytes_h_session.py prepare --measurement-root FRESH --session-root SCRATCH --remainder --soak-70b full --measured-session /Users/edr/night-bytes/h-20261021T185555Z
```

The optional `--soak-70b r12` requires the director to re-run `scripts/run_campaign.py <staged-r12-soak-dir> --runs-dir <scratch> --log <scratch>/campaign_log.jsonl --campaign-policy configs/campaign_policies/quiet_mac_p2_b5.json --max-failures 1 --dry-run` and verify one member before arming.

Director records ledger SHA-256 before/after, STAGED output, every P term, real statvfs free>=P, span/stage list and diff review. Fresh scratch root is under /Users/edr/night-archive/forward-20261021/BY-H2/. Source checkout follows the director's specified measurement location; this session never reads/writes that location. Execute within foreground calls under ten minutes and never install during the pause.

Candidate t0 = 60*ceil((now + launch_lead_s)/60). loop.json supplies launch_lead_s (fallback 420 s, minimum 300 s). The candidate is computed at prepare time; reprepare into a new scratch root if expired. Programmed duration uses ceil(span), maximum uses the separate T0/pause/WAIT arithmetic above. Lead records real epoch, UTC and local start, programmed end=t0+ceil(span), latest end=t0+window_max_s; do not substitute current report time.

Recorded install command for AFTER pause lift and completed gates, not executed:

```sh
FRESH/.venv/bin/python -B FRESH/scripts/bytes_h_session.py install --session-root SCRATCH
```

Use the verified Interactive night-agent context for cadence, never the magistrate's launchd rehearsal context as proof. Lead owns executing ACCEPT review, CI (except gate-ledger), arm notice, real t0 and authorization.

Notice draft:
"BY-H2 is a separate non-claim remainder session. It runs fresh reservation/calibration/bound/reference work, all three test7 starts and ends, [full twelve / r12-only] 70B soak and twelve 122B soaks, midpoint/end references, closing calibration, then desk verdict and backup outside the programmed chain span. No check stages. Start [epoch/UTC/PDT]; programmed [15636 s full / 12623 s r12], maximum [33360 s / 30360 s]. Real free disk [bytes] >= P [63878576237 B / 56122258559 B]. Expect native battery.assist disclosures on 70B/122B large workloads; retain all observed flags and withheld receipts. Other record/identity/lineage observations remain named flags. The known-bytes probe is a separate quiet-Mac step. Nothing is armed until Ed lifts the pause and the lead clears gates."

## DECISIONS I MADE
- R1 uses staged subset inputs only for remainder desk; C5's existing check requirement remains unchanged and is disclosed as sizing.c5_remainder_checks_absent. No combining H/remainder data in this item.
- R2 changes wording only: integer stage endpoint difference, no +1 s per row, preserving director-verified arithmetic.
- Preserve all full-kit/generator bytes; subset only in the disposable view, with existing r12 bytes/identity.
- Preserve midpoint because existing acceptance/harvest assigns its protocol role.
- Keep full 70B soak default; only the lead chooses r12 after BY-0.
- Use own-stage H members first, then matching model/workload cohorts; mean member durations plus maximum observed residual for unobserved soaks, one shared observed-spread member margin. No pilot allowances substitute for missing H span evidence.
- Name the single aggregate B6 fixed envelope rather than invent separate closing stage times. Keep fixed disk allocation and rational rates unchanged.
- Keep derived span receipt separate from immutable registration, using the writer's authenticated relative-path/hash/pointer interface.
- Keep preparation record failures as flags, with INPUTS_ONLY when no writer-authenticated plan can be produced.
- Retain native battery flags without inferring flags or adding a battery energy estimator.
- Keep standalone probe out of the campaign path; numerical B/N are explicitly deferred to the quiet-Mac observations the README requires.
- No generated files, hazard registries, smoke_keep or import-graph lists changed because no generator/import/raise-site additions required them. No queue/state/run-report files outside WRITE_SCOPE changed.

## OPEN ISSUES
- Director: commit/push slice 4, final review and R1/R2 disposition, executing ACCEPT, CI branch and draft PR. Real dry prepares/ledger proof were reported by the director at intake; no green CI or final ACCEPT is claimed here.
- Import-graph synthetic arm environmental failure: process-group census unavailable in sandbox. Rerun in the director's supported CI/environment; no bypass or test weakening.
- Standalone probe explicit B/N, quiet-Mac capture controller/clock mapping and resulting receipts remain lead-owned. Packet is a draft, not executed hardware evidence.
- No real measurement, install, arm, launchd load, ops/stop ref change, PR or network push occurred. No local command left running.

## NEEDS_RULING
none. The brief assigns BY-0's soak choice, real prepare and probe measurements to the lead; no implementation authority expansion is requested.

## PRIOR SLICE VERIFICATION HISTORY
The following historical commands/results document fixes and prior testing; final status above supersedes their next-step notes.

## LOCAL SLICE 2 VERIFICATION
All test/kit commands used `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B` from repository root. Commands below append to that exact prefix.
- Initial mixed-module command `-m unittest tests.test_bytes_h_session.SessionTests.test_prepare_uses_real_writer_without_install_or_loop_registration tests.test_bytes_h_session.RealKitStagingTests tests.hazards.test_refusal_allowlist`: exit 1, 26 tests, 1 error, 1 skip. This incorrectly shared one TMPDIR between modules; subsequently reran modules separately. Error was an implementation variable collision: the old disk divmod local named remainder overwrote the new mode boolean. Renamed it rounding_remainder. No added refusal site.
- `-m unittest tests.test_bytes_h_session.SessionTests.test_prepare_uses_real_writer_without_install_or_loop_registration tests.test_bytes_h_session.RealKitStagingTests`: exit 0, 3 tests, 0.657 s, OK after the fix.
- `-m unittest tests.test_bytes_h_session.SessionTests.test_remainder_prepare_real_writer_both_soaks_and_journal_math`: exit 0, 1 test, 0.206 s, OK (both full/r12 subtests).
- `-m unittest tests.test_bytes_h_session.SessionTests.test_prepare_flags_missing_ledger_without_fabricating_a_plan tests.test_bytes_h_session.SessionTests.test_prepare_accepts_exact_p_and_prints_terms_without_reserve tests.test_bytes_h_session.SessionTests.test_prepare_and_native_arm_budget_the_same_peak_disk_bytes`: exit 0, 3 tests, 0.376 s, OK.
- `-m unittest tests.hazards.test_refusal_allowlist`: exit 0, 23 tests, 12.942 s, OK (skipped=1).
- `scripts/bytes_mac_kit.py --check`: exit 0, `verified non-claim Mac kit`.
- Independent read-only inspection called remainder_span with the real H journals for both views (no prepare or measurement); results recorded in PROGRESS. An initial inspection failed because StageDispatch has no kind attribute; resolve_stage_dispatches already returns collections only, so removed that access before executable testing.
- `-m unittest tests.test_bytes_h_session.SessionTests.test_remainder_prepare_real_writer_both_soaks_and_journal_math tests.test_bytes_h_session.SessionTests.test_remainder_missing_journals_flags_inputs_only_without_pilot_span tests.test_bytes_h_session.RealKitStagingTests tests.test_bytes_h_session.DiskRulingTests`: exit 0, 8 tests, 0.814 s, OK. Includes stage-by-stage independent base/member/margin/total assertions for both soak selections, absent-journal flag, integer P, and source-kit byte identity.
- `-m unittest tests.test_bytes_mac_kit`: exit 0, 4 tests, 0.224 s, OK.
- `-m unittest tests.test_bytes_gates`: exit 0, 7 tests, 0.441 s, OK.
- `git diff --check`: exit 0. All launched commands completed. No live hardware work, installation, arm or background measurement was performed.

## LOCAL SLICE 1 VERIFICATION
Every test invocation below ran from the repository with its own fresh TMPDIR, prefixed exactly `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2.XXXXXX) /opt/homebrew/bin/python3.13 -B`.

- `-m unittest tests.test_bytes_h_session.SessionTests.test_fully_observed_native_export_extracts_and_clears_c5 tests.test_bytes_h_session.SessionTests.test_prepare_to_real_nonclaim_harvest_to_measurements_to_gates`: exit 0, 2 tests, 95.810 s, OK. The first injects native CSV flag disclosures at the input boundary; the second uses real harvest/acceptance/export/gates children and compares all per-run flag lists.
- `-m unittest tests.test_bytes_h_session.RegistrationInputTests tests.test_bytes_h_session.DiskRulingTests tests.test_bytes_h_session.MeasurementViewLedgerTests tests.test_bytes_h_session.ReceiptMathTests tests.test_bytes_h_session.RealKitStagingTests`: exit 0, 14 tests, OK (before the added remainder test).
- `-m unittest tests.test_bytes_h_session.RealKitStagingTests`: exit 0, 2 tests, OK (including both remainder modes, source kit byte identity, reference roles, existing r12 config and unchanged full path).
- The same RealKitStagingTests command after adding subset disk sizing first failed in both modes with KeyError for removed model qwen3-14b. Fixed by restricting sized.models to the actual staged inventory before calling the unchanged disk-rule function. Rerun: exit 0, 2 tests, 0.695 s, OK, including all independent P assertions.
- `-m unittest tests.test_bytes_gates`: exit 0, 7 tests, OK.
- `-m unittest tests.hazards.test_refusal_allowlist`: exit 0, 23 tests, OK (skipped=1). No new raise site or import was added.
- `-m unittest tests.hazards.test_import_graph`: exit 1, 6 tests, one failure: test_a_complete_arm_and_monitor_run_load_no_retired_module expected GO, got NULL. Diagnostic synthetic Rig.run returned `instrument REFUSE: the capture's process group was not proven gone: census_exit_3: sysmon request failed with error: sysmond service not found` and `pgrep: Cannot get process list`. This is the brief's environmental process-group lane; no production arm was attempted.
- `-m unittest tests.test_bytes_mac_kit`: exit 0, 4 tests, OK.
- `scripts/bytes_mac_kit.py --check`: exit 0, `verified non-claim Mac kit`.
- Full `-m unittest tests.test_bytes_h_session`: exit 0, 33 tests, 121.691 s, OK. This process loaded before the final disk-helper assertions were added; the subsequent focused RealKitStagingTests run covers those additions.
- `git diff --check`: exit 0 after remainder and disk-helper changes.
