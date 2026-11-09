# Merge c84 review — Sol, 2026-11-08

**Verdict: HOLD.** One reproduced functional merge interaction remains: R17
finality rejects the native R22 disclosure-only desk output. No production fix
is included.

Reviewed only `c84df94bfd38e7c29b083fe6629217eddaab94b3`, parents
`94d3dcb3e` (v4) and `d5dc1198c` (harvest-off), using `git show --cc`,
both parent diffs, and `git show --remerge-diff`. Authority: the review brief,
`origin/main:RUN_STATE.md` items 241/242 and R17, the v4 protocol,
HARVEST-OFF-AGREEMENT, and the speed toolbox. No delegation or consultation.

## F1 — completed contention-only desks cannot become final

The v4 common desk deliberately writes `members_excluded: []` and
`members_disclosure_only: {member: ["contention.unmeasured"]}` to both
PILOT.json and desk.json; the raw harvest exclusion remains in exclusions.json
(`scripts/align_pilot_session.py:408–424`). This is valid R22-1 output.

The lane's `light_triage.final_adjudication_error` compares each filtered
`members_excluded` list directly with the raw list (`light_triage.py:148–150`),
ignoring the disclosure map. Thus a completed native desk fails `cmd_final`
with `final eligibility refused: desk, PILOT.json and exclusions disagree`.
The packet's new `last_desk_state` finality requirement runs before
`effective_desk` (`align_v4_next_arm_packet.py:745–747`), so an otherwise ready
W1 cannot release C1 either. Later windows cannot satisfy R17's finality bound.
This needs no malformed input or adversarial action.

New executable witnesses in `tests/align/test_merge_c84_sol.py` reproduce both
routes. The native route runs the actual common/v4 desk and final consumer on
the existing synthetic endpoint fixture, replacing only the harvest child
with a synthetic archive writer. The committed route has a passing clean
control. Real and mixed real/contention exclusions still block C1.

**Required repair:** reconcile finality against the desk/PILOT exclusion and
disclosure records together, preserving member/code agreement with the raw
harvest and all real exclusions. Keep completed-harvest, plan binding and k+2
checks. Add coverage for a separate contention-only member alongside a real
excluded member and for successor `previous_final`/`final_record` sources.

## Preservation and the provisional-window adjustment

All 96 v4-only and 31 harvest-only changed paths are byte-identical to their
owning parent, relative to merge base `356c41c82`. Reviewed the 14 jointly
changed paths; no unrelated feature loss found. The five conflict resolutions:

| File | Preserved resolution |
| --- | --- |
| pilot_protocol_v4.md | R17 eligibility plus current U4-only and R22/R24 fixed-eight rules |
| align_pilot_session.py | R22 exclusion policy plus lane `harvest_workers` API/CLI forwarding |
| align_v4_next_arm_packet.py | R17 provisional/successor/final_record binding plus structural bars and strict effective_desk |
| align_v4_series.py | C9–C14 reserves and frozen allocation plus withdrawal of the C6 fence |
| align_v4_session.py | R22 split before shared harvest-code application; pre-dwell Git/series/powermode/disk checks and writes; installer_end_ns; timing wrappers |

The specific `has_final_sources()` adjustment is sound within its scope:
`effective_desk(desk, None)` returns the desk unchanged; it grants no passing
verdict. Complete own/successor sources still read exclusions. `effective_desk`
and `structural_bar` are AST-identical to the v4 parent. Existing tests retain
strict member/code mismatch refusal, real-exclusion failure, W1/code-change
barriers, and k+2 finality. F1 is a separate integration failure before that
normalization can run.

## Verification and handoff

Ran at supplied checkout `0b2d4d9b2`. The five production files on F1's path
are byte-identical to c84. Among the requested witness modules, only the
pre-existing D8 `expectedFailure` annotation differs from c84; it was added by
the lead at `0b2d4d9b2` and is not a new finding.

Each table row ran in its own sequential process with
`python3.13 -B -m unittest -v tests.align.<module>`:

| Module | Tests | Result |
| --- | ---: | --- |
| test_harvest_off | 45 | OK |
| test_harvest_off_review_sol1 | 17 | OK |
| test_harvest_off_review_sol2 | 22 | OK |
| test_hoff_delta_sol1 | 17 | OK, one ruled D8 expected failure |
| test_hoff_delta_sol2 | 13 | OK |
| test_hoff_delta2_sol1 | 9 | OK |
| test_hoff_delta2_sol2 | 11 | OK |
| test_hoff_confirm_sol | 3 | OK |
| test_v4_next_arm_packet | 45 | OK |
| test_r11_delta6_sol1 | 11 | OK |
| test_r11_delta6_sol2 | 11 | OK |
| test_v4_disclosure_only_desk | 13 | OK |
| test_merge_c84_sol (new) | 3 | one pass, one failure, one error: F1 |

Requested modules: 217 tests, 338.6 s of process wall time. New witnesses:
6.461 s unittest time; intentionally red, without expected-failure markers.
Synthetic custody fences reported zero forbidden accesses. Archive equality
and worker/dedupe witnesses passed. New witness syntax and final diff whitespace
checks passed. Logs: `/private/tmp/merge-c84-sol-review/`.

Changed only this report and the new witness module. Coordination state is
untouched. No full suite, network, model download, analysis pipeline, real
measurement/custody access or native collection ran. Native finalize/restore,
cross-host equality, RSS and dwell/installer gates remain the lead's outside-
sandbox work; synthetic endpoint results do not discharge them.

**Next exact step:** fix F1, make the new module green, then rerun the affected
finality/disclosure witnesses one module per process. No ruling question is
needed for the reproduced failure; native readiness remains unverified.
