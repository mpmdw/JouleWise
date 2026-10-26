# BYTES pass 1: lead rulings before slot filling (magistrate 786c0858, 2026-10-23)

Source: the inventory of what stands between today and the first pass-1 t0 (`~/night-archive/seats-786c/by-inventory/`, copy `.scratch-INV/INVENTORY.md` in worktree jw-wt/by-inv), slot by slot. These rulings decide what each unfilled slot is filled with. None changes registered arithmetic; where a registered fallback exists, the ruling applies it.

1. **8B-8bit: kept.** The H desk found five identifiable, bounded 512-output runs (decode 12.02-12.04 s). This is the registered resolvability check (R8 item 6). Its missing F_min diagnostic is a separate slot.
2. **P_limit per regime and contention measurability: the registered fallback applies.** No session-bound non-claim phase-floor or census-power receipt exists for any BYTES regime (H and BY-H2 record those fields as unavailable), and the registration forbids borrowing ALPHA's floor. Under `scripts/bytes_gates.py:326-340` an absent registered phase line gives flag-only contention, with missing operands printed as unavailable. The slot says so and cites the receipts' absence. The hazard monitor's directly measured 5 % CPU limit remains the physical refusal during collection.
3. **Test 7 per long regime: computed at the desk from BY-H2.** BY-H2 has start and end alternating workload/reference stages for llama-70b, qwen35-122b and qwen3-next-80b. The desk compares each regime's start/end drift with the reference drift and records the outcome. A regime with no established pass keeps the registered scale `max(1, E/E_ref, T/T_ref)`. No rerun, and no invented pass threshold.
4. **Clock-gate values: the six measured T_stream_max holds in the sizing rows.** The hold uses the measured rate r (S-7); the frequency word is a diagnostic. The stale §5 wording "wait for the frequency word" is corrected to match.
5. **Per-session disk footprint: the H-DISK form, P = 2(B+WAIT)+fixed, with no added reserve.** The stale §5 "150 GiB before arm" is replaced. Each arm measures physical free space against P (plus the smoke share when a smoke is due). Freeing space is operator work between sessions, not a registration change.
6. **C5 sizing per sub-pack: the six rows of 82cc9462c** (H + BY-H2; complete soaks). The largest P is s4 at 116,400,948,249 B (118,843,585,614 B with smoke); the peak rate comes from a run with two idle-admission retries, a real production behaviour, so it is kept.
7. **B4 slots:** group keys `<pack_records_root>/bytes/blinding`; withheld store `<pack_records_root>/bytes/withheld/<pack_id>/<session_id>.runs.csv`; flag `bytes.withheld_missing`. The runtime config is `configs/b6/loop_bytes.json` (root `/Users/edr/night-b6/loop-bytes`). **`--stage1-commit`** registers the interface and its validation now (`scripts/b6_release_subset.py` requires the full commit of the stage-1 predictions at held-out release); the actual hash is supplied at release. Requiring it before the first t0 would be circular.
8. **B2 estimator SHA and coverage counts:** filled only at the agreeing pin, after #573 and #574 land in the pass-1 lane and the agreement suite passes on the integrated tree (today the defects campaign is 387 fields above the bar on 1c458d71d). Coverage is reproduced at that pin and printed as counts of 400 and fractions.
9. **Known-bytes stream test (§1), amended 16:10 PDT.** It is a required Mac measurement of about one hour (protocol `configs/campaigns/bytes_mac_check/README.md:28-40`). The native chain cannot run it today: `joulewise/b5/chain.py` has a closed tool and stage-kind set and requires a campaign collection (seat BY-KB, `~/night-archive/seats-786c/by-kb/`). Extending the frozen chain on the pass-1 measurement head would add risk and audit work to every pass-1 session for a non-claim companion probe. The test validates the boundaries' response to known streamed bytes. It changes no number collected in a pass-1 session, and blinding protects the analysis until the stage-1 release. So it runs **after pass-1 collection and before stage-1 unblinding**, from its own non-claim checkout with the chain extension, and the slot is filled then. §19's order is amended to say so; the registration cold gate sees this change explicitly. If the test shows a boundary does not respond as registered, the boundary's claim lines are printed with that outcome beside them, as §1 provides.

10. **Launch declarations (`arm_attachments.launch`, fourteen bindings) and identity projections for the six pass-1 trees** are assigned to a build seat (BY-PIN). It follows the non-claim H pattern (`scripts/bytes_h_session.py:139-155, 225`) through the plan-tree generator, then regenerates all tree, config and projection pins.
11. **Release line.** BYTES collects from the reviewed pass-1 lane pin. It does not wait for block 5's release or for a merge to main (block-6 registration: pinned-lane collection is allowed). The laptop whole-suite run of §19 is done on the final integrated pass-1 tree before the registration gate.
12. **BY-VALIDITY and BURN-TRIAGE source findings** are risk lists, not confirmed defects (0 executed). Only findings on the BYTES claim path that an executing review confirms are fixed before the registration gate. The rest are named as deferred in the gate charge.

## Executed evidence

Ruling 2's fallback is the code path at scripts/bytes_gates.py:327 (an absent regime receipt gives an "unavailable" contention line; an absent registered phase line gives "flag_only"). Ruling 6's largest P was re-derived by hand from the s4 row's terms (B, WAIT, fixed in configs/b6/registration/sizing_b5.json), and the pin fence was run on this tree:

```text
$ /opt/homebrew/bin/python3.13 -c "print(2*(38166208818+18010999755)+4046531103)"
116400948249
exit 0
$ /opt/homebrew/bin/python3.13 -B scripts/repin.py --check
PASS 16 pin families current
exit 0
```

The test-7 computation of ruling 3 is in docs/process_traces/2026-10-23-magistrate-786c0858/TEST7.md and TEST7.json; the runtime observation behind ruling 10 is RUNTIME-OBSERVE.txt beside this file.
