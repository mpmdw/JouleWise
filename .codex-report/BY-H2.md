# BY-H2 — incomplete cloud checkpoint (2026-10-22)

## SUMMARY
- INCOMPLETE: no implementation or executable validation has been performed.
- The attached cloud environment has not become usable; shell execution reports "No usable execution environment is available."
- Runtime observations have moved from pending to starting and back to pending, with offline connectivity and no reported failure reason.
- Diagnostic metadata has no retained records; no root cause has been established.
- The authorized lane was verified through the GitHub read connection at c10b6895fab0894b23b42ad439cf900c37d07c0b before this report commit.
- Repository code and generated kit files are unchanged by this checkpoint.
- Remote source inspection found that desk drops native per-run flag_codes when constructing MEASUREMENTS.json.
- No model execution, installation, launchd operation, arm, PR, or other branch write was performed.
- Resume this item from the lane head and complete the implementation and all required gates.

## DESIGN
Not implemented. Proposed CLI remains the brief's prepare --remainder --soak-70b full|r12 --measured-session H_ROOT; this is not an available command yet.

The existing measurement_view function in scripts/bytes_h_session.py is the appropriate selection boundary: it already rewrites stage manifests and copies dispatched config bytes. Preserve the generator and committed full tree/configs; select in the disposable view, repair ordinals/predecessor/successor, filter science, and rewrite the one-member r12 manifest there.

Candidate stage order (existing fixed-stage expected_count values retained; collection counts are member counts):
1. bracket-reservation: bracket_reservation, 1
2. pre-calibration: calibration_capture, 1 (chain adds its screen and calibration verdict)
3. bound-collection: campaign_collection, 18
4. bound-derivation: bound_derivation, 1 (include its corpus derivation work)
5. reference-start: campaign_collection, 3
6. test7-llama-70b-start: campaign_collection, 4
7. test7-qwen35-122b-start: campaign_collection, 4
8. test7-qwen3-next-80b-start: campaign_collection, 4
9. reference-midpoint: campaign_collection, 1
10. soak-llama-70b: campaign_collection, 12 for full; 1 for r12
11. soak-qwen35-122b: campaign_collection, 12
12. test7-llama-70b-end: campaign_collection, 4
13. test7-qwen35-122b-end: campaign_collection, 4
14. test7-qwen3-next-80b-end: campaign_collection, 4
15. reference-end: campaign_collection, 3
16. post-calibration: calibration_capture, 1
17. whole-window-verdict: whole_window_verdict, 1
18. backup: backup, 2

These selections total 73 or 62 members: full-kit 123 minus ten five-member checks, with eleven additional members removed for r12-only. Counts by model are llama-70b 16 or 5, qwen35-122b 16, qwen3-next-80b 4, neg8_reference 37.

Keep reference-midpoint: existing acceptance assigns its role through the midpoint_reference external input ID (joulewise/b6/acceptance.py, _stage_roles); joulewise/b5/harvest.py, _neg8_disclose, describes the (3,1,3) reference protocol and discloses a missing midpoint. Inspect whole_window's deciding screen before finalizing the implementation explanation.

The real writer's read_allowance verifies a relative JSON source locator, exact hash, and JSON pointer value. A derived sizing receipt in the disposable measurement view can use that interface without changing b5.plan or committed sizing. This has not been exercised.

## SPAN
Not computed. No H journals have been read from the Mac, and no synthetic fixture or derived sizing receipt has been executed.

Use the brief's appendix for the synthetic fixture and H_ROOT/custody/night/chain-stages.jsonl plus H_ROOT/custody/collection/run_clock.jsonl at real prepare time. Account separately for shell-stamped fixed intervals, members, measured collection overhead, and registered chain.SETTLE_S settles. Apply one disclosed observed-spread margin to member/reference time, as governed. Resolve and name the committed fixed_s fallback for the unobserved verdict/backup without inventing separate durations. Print every source term and use plan_inputs.window_max_s.

The committed sizing evidence names the block-6 r4-alpha clock/stage/compression sources. sizing_b5.json has breakdown.fixed_s = 1191; that is an aggregate fixed-work envelope, not independently measured verdict and backup durations. The eventual implementation/report must disclose that distinction.

## DISK
Not computed. Derive P independently of H journal availability from the existing committed rational allowances/rates and the subset counts above:
P = 2 * (max(ceil(stream_rate * sum(count * own_stream_allowance)), ceil(wall_rate * sum(count * own_member_allowance))) + ceil(stream_rate * 7200)) + fixed.
Keep fixed = 4,046,531,103 B and the registered formula, with no reserve. Preserve the native integer budget encoding so its total equals P exactly. Print all counts, products, bases, WAIT, fixed, c, free and purgeable bytes. No physical disk snapshot was taken in this seat.

## PROBE
Not implemented or run. The current chain permits campaign_collection only through campaign_runner; bytes_stream_test.py is a standalone MLX reduction and has no campaign adapter. The driver supervises KM003C across the chain, while member rails capture belongs to the campaign path. Do not add a nominal stage without proving exact-span rails capture.

Complete the separate quiet-Mac packet by inspecting the supported standalone rails capture interface. Its probe command is:
    MEASUREMENT/.venv/bin/python -B MEASUREMENT/scripts/bytes_stream_test.py --bytes B --repeats N --out RECEIPT

B and N must be explicit positive integers chosen from measured available memory, cache capacity and a timed rehearsal for approximately one hour; no bandwidth-derived defaults. No numerical B/N or unverified capture command is supplied by this checkpoint. Preserve paired clock evidence and map both rails and KM003C onto the receipt's CLOCK_MONOTONIC_RAW start_ns/end_ns, excluding allocation/fill. This remains outstanding work, not an acceptance result.

## BATTERY
Remote source inspection only:
- joulewise/b5/driver.py, production_seams.monitor_argv, builds the existing hazard monitor configuration; meter_argv supervises scripts/km003c_monitor.py.
- joulewise/hazards/monitor.py declares battery_smc_s = 1.0 and the in-process SMC battery current task.
- joulewise/b5/harvest.py emits per-member battery.assist and retains withheld/battery-assist.json.
- joulewise/b6/export_runs.py preserves per-member flag_codes in the native CSV.
- scripts/bytes_h_session.py, measurements, currently constructs numeric per-run receipts without carrying CSV flag_codes into MEASUREMENTS.json. Fix this within the authorized script and test it through desk.
- H observations in the brief make assistance expected for the 70B and 122B large-workload members (16 and 16 in full, or 5 and 16 in r12-only). These are expectations, not flags to synthesize; keep observed native disclosures for every member.

No battery-energy estimator change belongs to this item.

## TESTS RUN
None. No test or setup process was launched. No test counts, exit codes or skips are available.
The attempted shell availability probe was cmd "pwd"; the execution tool rejected it before execution with "No usable execution environment is available. Wait for an environment to become available before using this tool."

The environment startup wait remains unresolved at checkpoint time. This is an infrastructure blocker, not one of the specified macOS environmental test failures. No /private/tmp, launchd, launchctl, powermetrics, osascript, process-group, or fixture git-commit test failure was observed because no tests ran.

Required on resume: seat_setup.sh and source /tmp/jw-seat.env; JW_B5_SYNTHETIC_ONLY=1 for every invocation; fresh module TMPDIR; tests.test_bytes_h_session, tests.test_bytes_mac_kit, tests.test_bytes_gates if desk changes, tests.hazards.test_refusal_allowlist, tests.hazards.test_import_graph, and scripts/bytes_mac_kit.py --check. Do not run the whole suite.

## END-TO-END
NOT RUN. Neither a synthetic remainder prepare nor a real Mac dry prepare has been performed. No STAGED result or unchanged-ledger proof is claimed.

## ARM PACKET DRAFT
NOT READY FOR USE. The remainder CLI is unimplemented. The director owns the real dry prepare, CI branch, draft PR, executing review and final real numbers.

After implementation and gates, the proposed dry prepare shape is:
    FRESH/.venv/bin/python -B FRESH/scripts/bytes_h_session.py prepare --measurement-root FRESH --session-root SCRATCH --remainder --soak-70b full --measured-session /Users/edr/night-bytes/h-20261021T185555Z

FRESH belongs under /Users/edr/night-custody/measurement/ and SCRATCH under /Users/edr/night-archive/forward-20261021/BY-H2/. Use the fresh commit's 402-row ledger and compare its SHA-256 before/after prepare. The director must verify STAGED, term-by-term sizing and disk >= P.

Existing t0 arithmetic is 60 * ceil((now + launch_lead_s) / 60), using configs/b6/loop.json (fallback 420 s, installer minimum 300 s). window_max_s separately adds the unchanged T0/pause/WAIT budgets to ceil(programmed_span_s), rounding up to a minute. Fill in real epoch/local times after successful prepare.

Existing install command (recorded only; never executed by this seat):
    FRESH/.venv/bin/python -B FRESH/scripts/bytes_h_session.py install --session-root SCRATCH

Do not install or arm during the pause. A later lead-authorized handoff must use a current t0 and the Interactive night-agent context.

Plain notice draft, requiring real numbers and lead approval:
"BY-H2 is a separate non-claim remainder session. It includes fresh reservation/calibration/bound/reference work, all three test7 starts and ends, the selected 70B soak and all twelve 122B soaks, closing references/calibration, verdict and backup. It contains no check stages. Start: [t0]. Programmed duration: [derived span]; maximum window: [derived maximum]. Free disk [bytes] exceeds P [bytes]. Native battery-assist disclosures are expected on 70B and 122B large runs; record and retain them. Missing records and identity observations remain named flags. The standalone known-bytes probe needs its separate quiet-Mac capture packet. Nothing is armed until the pause is lifted and the lead completes the gates."

## DECISIONS I MADE
- Preserve the full generator and committed full kit; implement selection only in the existing disposable view.
- Treat the two soak selections as 73/62 planned members; preserve all reference and test7 pairing work.
- Preserve actual disclosure codes rather than inventing battery flags from H's expectations.
- Do not present remote inspection, synthetic fixtures, or startup status as executable or hardware validation.
- Save this incomplete checkpoint only on the expressly authorized lane, using the connected GitHub tool because no shell is usable.

Other implementation choices remain unimplemented and unverified.

## OPEN ISSUES
- Cloud execution environment is unavailable; complete setup, local instructions/state inspection and branch checkout once it is ready.
- Implement and test the remainder path, journal derivation, subset disk sizing and battery flag preservation.
- Exercise both soak selections through the real writer and chain.stage_plan, including independent arithmetic and unchanged-ledger checks.
- Register any changed refusal sites/census and import lists if needed.
- Complete and verify the standalone probe packet.
- Replace this checkpoint with the complete measured synthetic results and finished report.
- Director: real fresh-checkout dry prepare, executing ACCEPT review, CI except gate-ledger, draft PR and real arm-packet numbers remain outstanding.

## NEEDS_RULING
none. The present blocker is execution infrastructure, not a scientific or numeric ruling.
