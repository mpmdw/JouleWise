# R11 delta7 — Sol confirmation

2026-11-08. Verdict: **HOLD** for one reproduced functional failure.
Reviewed `c742e5722..e36b096fe` on `align/2026-11-08-r11-delta7-sol`;
also compared the three measurement-core files against armed R1 `20e9edbc4`.

## F1 — effective_desk admits a mismatched desk containing a real exclusion

`scripts/align_v4_next_arm_packet.py:407-435` checks only the harvest's
`members_excluded`. If those codes are contention-only, it changes false
`no_member_exclusions` and `chain_eligibility` checks to true and recomputes
the full-desk gate. It never inspects the desk's own `members_excluded`.
Both `last_desk_state` and `full_desk` consume this rewritten verdict.

**Ordinary failure scenario:** a stale desk and a later harvest for the same
plan are assembled into one window record. The committed desk still records
`member.runtime_failure`; the committed harvest lists only contention. The
reader silently upgrades that failed desk to passing instead of requiring a
consistent, passing desk. A stale desk naming a different member also passes.
This is an operator/source-selection mistake under D-161, without a forger,
race, inaccessible hardware or edits to committed evidence.

Executed four synthetic committed-Git probes using the existing `Scenario`
and the arm's `evaluate` helper (which rebuilds and compares the packet):

| Desk exclusion | Harvest exclusion | Full desk | Preflight ready / arm admitted |
| --- | --- | --- | --- |
| contention, same member | contention | pass | true / true (control) |
| runtime failure, same member | runtime failure | fail | false / false (control) |
| **runtime failure, same member** | **contention** | **pass** | **true / true (defect)** |
| **contention, different member** | **contention** | **pass** | **true / true (defect)** |

Every probe passed `member_eligibility`; the real-exclusion control correctly
retained its excluded thermal member. The mismatched cases prove that a real
exclusion recorded in the desk can be bypassed, **not** that a real exclusion
present in the authoritative harvest is numerically counted as eligible.

Minimal reproduction (synthetic only; the final desired-behavior assertion
fails at the reviewed head):

```sh
env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_NO_LAZY_FETCH=1 python3.13 -B - <<'PY'
import tempfile
from tests.align.test_v4_next_arm_packet import Scenario, evaluate
with tempfile.TemporaryDirectory(prefix='jw-delta7-synthetic-') as tmp:
    s = Scenario(tmp)
    run_id = s.members[0]['run_id']
    s.sources['exclusions']['members_excluded'] = [
        {'run_id': run_id, 'codes': ['contention.request_overlap']}]
    s.sources['desk'].update(
        pilot_status='instrument_incomplete', harvest_status='members_excluded',
        members_excluded=[{'run_id': run_id, 'codes': ['member.runtime_failure']}],
        checks={'synthetic_check': True, 'chain_eligibility': False,
                'no_member_exclusions': False, 'v4_B_bar': True},
        full_desk_gate={'pass': False})
    s.finish()
    packet = s.build()
    result = evaluate(s, packet)
    print(packet['checks']['full_desk_gate']['status'],
          packet['packet_preflight']['ready'], result['admitted'])
    assert not result['admitted'], 'desk/harvest mismatch must refuse'
PY
```

Required repair: reconcile the desk's own member IDs and effective codes
before upgrading its verdict; preserve real/unknown exclusions and independent
chain-eligibility failures. Alternatively require a fresh native passing desk.
Matching contention-only evidence must remain admissible. No production repair
is made by this confirmation seat.

## Delta6 closure and pin checks

- S1 F1 / S2 F1: the native common desk now applies `split_codes` before
  exclusions, eligibility, analysis and harvest status; v3 retains its default.
  Both original witnesses pass. Closure is qualified by F1 above in the new
  compatibility reader. Mixed real/contention codes still exclude normally.
- S1 F2 / S2 F4: balance includes disclosed contention and coverage flags,
  using a union to count duplicates once. Both witnesses and the duplicate
  control pass.
- S2 F2: R25 prospectively installs C9–C14 U3 scopes; roster sum is **22**.
  Healthy synthetic reserve U3 checks pass. Protocol, deviation and fixtures
  agree; this does not attest to any real bar's signing or inputs.
- S2 F3: pool admission now calls `WindowRecord.structural_bar`, as history
  and calibration do. The terminal-bar/nonempty-pool witness refuses; its
  empty-pool control continues; barred calibration counts stay zero.
- Drift prose now says C14 raises gate-admitted FPR by +0.03–0.17 pp at
  b=.05 with T after the stop. No simulation was rerun.

The complete `git diff 20e9edbc4..e36b096fe -- joulewise/b5/driver.py
joulewise/controller.py joulewise/bundle.py` contains only timing-receipts
changes: driver import/decorators/worker context; controller receipt sink,
context binding, buffered timing events and finalize span; one writer `timing`
attribute. Path history names only `3c9c47a4e` and `ed9fd3ca1`. All three
current files are byte-identical to final timing fix `ed9fd3ca1`:

| File | SHA-256 |
| --- | --- |
| `joulewise/b5/driver.py` | `d8780edb8e5806535291b32ace77cdf9a7acd7c8546a36fffebd119c311c0d5e` |
| `joulewise/controller.py` | `3f0535c976463da1ae99718cfcde2b0ef92241cda36973baaf4b1a6ebe1b12db` |
| `joulewise/bundle.py` | `db2d7626d1b4e07148947ba5cbe7508630f9c8184caa72ba96cd04806a245dd6` |

Frozen manifest SHA-256 remains
`21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.
Its bytes equal `series.raw_json(series.candidate())`; the delta6 tests also
verify preserved old windows and contiguous reserve indices 100–147.

## Verification and handoff

Each listed command is `python3.13 -B -m unittest tests.align.<module>` in a
separate process, with Git global/system configuration disabled and lazy
fetch disabled; synthetic temporary files were placed under
`/private/tmp/jw-delta7-sol`.

| Module | Result |
| --- | --- |
| `test_r11_delta6_sol1` | 11 OK, no expected failures |
| `test_r11_delta6_sol2` | 11 OK |
| `test_v4_disclosure_only_desk` | 7 OK |
| `test_measurement_core_boundary` | 5 OK |
| `test_r1_round6_lows` | 18 OK; failed duty bars refuse lead fallback |
| `test_r1_round7_install` | 6 OK, including TERM/HUP child restoration |
| `test_thermal_sidecar` | 9 OK |
| `test_v4_contention` | 7 OK |
| `test_v4_balance` | 4 OK |
| `test_v4_w1_blockers` | 16 OK |
| `test_w1bm_sol1` | 12 OK |
| `test_w1bm_sol2` | 12 OK |
| `test_v4_next_arm_packet` | 32 OK |

All **150 targeted tests** pass. Aggregate unittest-reported time, including
the two repeat modules below, was 152.303 s (well under the 20-minute budget).
The report's exact reproducer printed `pass True True` and exited 1 at the
intended refusal assertion, without fixture errors. A separate pure-code
sweep preserved all 59 non-contention exclusion codes in the catalog's draft
vocabulary through `apply_exclusion_policy` and the matching-harvest reader;
this is a vocabulary check, not an adopted-catalog or measurement claim.

Two initial short module processes (`round6_lows`, `round7_install`)
overlapped because the tool yielded before exit; both passed and were then
rerun serially with the results above. Remaining module launches were
serialized. The four extra committed-source probes reproduced F1 with both
controls intact. No full suite, network, weights, analysis pipeline, real
measurement/restricted/custody paths, native MLX or hardware probes were used.
Python 3.11 and native hardware behavior remain unverified; no new MLX code or
native test requirement is introduced. Coordination files are untouched;
only this report is added. No agents or external consults were used.

Next exact step: lead repairs F1, reruns its reproduction expecting refusal
and the focused desk/packet modules, then adjudicates admission. No science
ruling is needed to report the mismatch; whether compatibility rewriting is
retained is the lead's implementation choice.
