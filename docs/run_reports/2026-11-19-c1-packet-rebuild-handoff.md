# Row 23 · W1 to C1 packet rebuild handoff

**DRAFT · Tier 2 · synthetic preflight.** Branch `align/2026-11-19-c1-packet-rebuild-handoff` starts at
`b2e01464d6d4fbf2901ff4d4154df9455104a12a`, the verified remote head of
`ops/2026-11-11-w1-presign`. The assigned branch had no remote head or pull request at intake.
Mission M0 found no active stop card. Row 23 is user-directed [AGENT] work. Scope is the existing
packet test module and this report. The published protocol and research decisions fix the existing
behavior. PR #844 supplied the synthetic rehearsal sequence and fixed clock for this check.
[Pipeline §1 and §3–4](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L10-L68) ·
[P4 packet and frozen series](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/pilot_protocol_v4.md#L860-L924) ·
[P4 series roster](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/pilot_protocol_v4.md#L1006-L1022) ·
[RLD C1 sentinels](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L15504-L15514) ·
[RLD completion record mapping](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20874-L20883) ·
[PR #844](https://github.com/mpmdw/JouleWise/pull/844)

## Freeze and verification

- Freeze `9fba97178bb08218b8f5689f5af4b9e1eb9d667e` and tree
  `b440f92ca54aa0935e7ee714cda72cfb76dc88a9`. The class ran 13 methods, exit 1, with 16
  expected assertion failures at the missing fixture seam. This is the test-only red baseline.
  The existing packet, desk, series and delta5 contract baseline passed 28 tests, exit 0.
- Build `710afd2d5b9d82912fd1ee5bd12ad97f8ca9e700` and assessed test tree
  `d0c1225fa3f85e984cbd814b7b8514195daf40dd`. The 13 frozen methods pass, exit 0.
  The expanded focused contracts pass 57 tests, exit 0. Each mutation uses a fresh fixture.
  The C1 roster comes from the producer's `candidate`, `selected` and `escalation_allocations`
  with the producer's run-ID rules. All fixture
  repositories have invented closure, desk and record bytes. The case traps I/O to the
  invented custody locators, non-fixture subprocesses, and arm, prepare and physical probe entry
  points. The scratch driver is absent from the runtime dependency chain.
- Delta `fbf9b68695392904fa99d39691f332ea9dda2654` and tested code tree
  `f5ec972400198a868ff8db4312c85c57cacc5459`. All 13 frozen methods pass again, exit 0.
  The omission case tests the U4 minimum with the plan and series roster in agreement.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_next_arm_packet.PacketTests align.test_v4_next_arm_packet.DeskDerivationTests \
  tests.align.test_v4_series.PacketTests tests.align.test_v4_series_delta5
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_next_arm_packet.PacketTests align.test_v4_next_arm_packet.DeskDerivationTests \
  tests.align.test_v4_cadence.TriageListTests tests.align.test_v4_cadence.CalibrationStopTests \
  tests.align.test_v4_series.PacketTests tests.align.test_v4_series_delta5 \
  tests.align.test_v4_series_r20.DeskTests
git diff --check b2e01464d HEAD
```

The named full-desk, edited-status and stale/expiry regressions supplied the expected behavior.
The local check takes the CLI, rebuild, record binding, cadence and series paths directly. Hosted
CI runs the canonical Python 3.13 sharded suite on the draft PR. The final head and check URLs
are recorded in the PR ledger and the seat's `FINAL-MESSAGE.md`. There is no cluster contract
directory at the baseline. The focused command above exercises the existing owned contracts
while integration owner acceptance remains open.

## Invented fixture results

The CLI uses `NOW=111.0` and `refs/remotes/synthetic/records`. The successful rebuild uses the
same clock and current fixture artifact digest. It binds the frozen C1 roster with the exact
W1 record, the R1 hash link, four sentinels at 5/22/23/24, and a W1 desk pass on the current
artifacts. The cohort check uses populated W1 pool membership. Fixed-eight reports
`continue`, zero attempted, zero eligible in both pairs, and zero replacement windows used.
W1 is the previous window and the counted calibration history is empty. Power mode, external
volume, charging battery and live meter remain pending. A refused CLI preflight can write
a diagnostic file.

### Fixture identities and exits

All paths and commits below belong to throwaway repositories. The W1 record path is
`w-W1/record.json`, the R1 record path is `w-R1/record.json`, and the series path is
`series/state.json`. The success ref tip is the W1 record commit. The stale case advances it
to the recommitted W1. The Git fixture fixes author and committer dates so these identities
are repeatable.

| Baseline fixture input | SHA-256 |
| --- | --- |
| W1 record | `78356af2485909beb7a7856c2bb04c7dcd1919f24fa873705542ea421dcb9e33` |
| R1 record | `11dbfa0706bcba58177e0e1443fde5d60cf0278f99b82713aecfcbdab117a566` |
| W1 series state | `13706aa0439f47b77bccbc89fc5bad3f638d49ff0bbf0d6c3f8a9e1cda0ced07` |
| R1 series state | `4c0bfd4e3ada74c68b6441a4a4fc3a9048097489b98215d416a88012d0e6e32a` |
| C1 series manifest | `70009b6a594835643ef0bb2ff324ed700447cbe7a6237975ebdb209ec2c78dd6` |
| Current artifact set and passing W1 desk | `9260111999969f9bb53b2bd58afbcb6e60a713c338dcbb7ae3f0245718f1c123` |
| Valid older desk artifact set (older-desk control) | `234dad331424ee2fe88b816715c260610afe85155fdf02d6cc57c425a5f7325e` |

| Case | Record commit | Series commit | CLI exit and gate outcome |
| --- | --- | --- | --- |
| W1 positive | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 0, ready. Canonical match, latest record and C1 binding pass. |
| R1 paired with its own ledger | `5478a82ffd4f35c6857c5faa32bdf3ca706a7b65` | `1703724252985a652f36f774e134bed8596a0b5a` | 0, ready. Canonical match, then C1 order binding refuses. |
| R1 substituted into the W1 pointer | `5478a82ffd4f35c6857c5faa32bdf3ca706a7b65` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 2, no packet. W1 previous-record binding mismatch, also on rebuild. |
| Forged W1 digest in series state | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `0b24317e1cb81fbee8280617a436efacf2e64691` | 2, no packet. W1 previous-record binding mismatch. |
| Corrupt committed R1 history link | `f5549407eca676ef7303438104fcda7ab802b3fc` | `5c55476adf1908fb0d1b9149272c142957a90762` | 2, diagnostic. History link digest mismatch. |
| Supplied record hash, evidence, or history (three cases) | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 0, ready for each original. Each edited pointer fails canonical comparison. |
| Valid old desk selected | `4c4024f223fc9dfdac0816fd4e85f92cca16ada8` | `d13073c5bf6e1af7af3a6fbe09b00ba89ca6ee68` | 0 before the ledger change, 2 with diagnostic after. Full desk digest differs from current artifacts. |
| W1 full desk omitted | `e560c94b1271457415db0a64ef0e8518cf7049a1` | `68bc6bc6ffcf30e152b53d0bbbd760008f18aa05` | 2, diagnostic. No final sources. |
| W1 full desk pending | `8c32fdaa76352d8c0e9dd84a6ad90b1aa7603e4e` | `444dcb4663c0040cf8568e35f11b23638cc08c1e` | 2, diagnostic. W1 full desk must complete and pass. |
| Supplemental 23 and 24 omitted | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `886512795e300ce73c0128d45f690fcb8648b17a` | 2, diagnostic. U4 requires four even though the two-sentinel plan and ledger agree. |
| Next-plan cohort changed | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `b7f6e2a7e5346338099026fdfc8084f35135dee2` | 2, diagnostic. W1 pool cannot cross a changed cohort. |
| Working record, series state and desk edited | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 0 before and after, same packet and canonical rebuild. Latest committed record still binds. |
| Stale W1 pointer | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 0 on the original. Old pointer still rebuilds canonically after the recommit, then fails current-record triage. |
| Recommitted W1 pointer | `55ff555eb41324d44563c78629228395c3a9ddd0` | `ab98004e01d2b600ed7e4f23377da8a77de04115` | 0, ready and current-record binding passes. |
| Expired W1 pointer at 141.0 | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 2, diagnostic. Original expiry 140, old pointer expires and the late rebuild reports stale quiet evidence. |
| Missing supplied expiry | `e9c43ad82c150d84c6d087aef1cd3589384d29d7` | `837ab69eea34aeaf4ccbee5c912b6bf3ac1934e8` | 0 on original. Removing expiry fails canonical comparison. |

The passing W1 output before selecting the older desk bound record `4c4024f223fc9dfdac0816fd4e85f92cca16ada8`
and series state `dc05dbdfa8eadf7ef632bddc576788829068801c`. The only subsequent input
change was the committed `last_passed_record` link.

## Independent review

| Round | Assessed commit | VERIFIED HIGH / MED / LOW | Root cause and disposition |
| --- | --- | --- | --- |
| Astra 1 | `710afd2d5` | 0 / 1 / 0 | `test-gap`. The old plan-only omission could refuse for ledger disagreement even when W1 U4 incorrectly passed. An in-process W1-only U4-to-pass counterfactual let the regression pass, exit 0. Fixed at `fbf9b6869`. The same counterfactual now fails the frozen sentinel test with unexpected CLI exit 0, unittest exit 1. The real focused class passes 13/13. |
| Astra 2 | `fbf9b6869` | 0 / 0 / 0 | No residual findings. Independently reran 13/13 and observed exit 2 with only `sentinel_roster` failing on the two-sentinel input. Changing only the minimum to two produced exit 0 and failed the frozen case. |

Both Astra 6.2 high seats executed the focused test class read-only. The local build used one
Sol 6.2 seat. HIGH plus MED fell from one to zero, satisfying Pipeline §3. Opus and the
integration owner still owe acceptance on the final tree. All public evidence here is synthetic
or Git metadata.

## Condition 13 metadata comparison

The ten paths come from `R1_EXECUTED_SOURCES`. The command reads tree entries and compares
only blob identities. All ten were present at the W1 baseline and matched the assessed build.
There was no inherited absence.

```python
import subprocess
from joulewise.align.apple.v4_registration import R1_EXECUTED_SOURCES

for ref in ('b2e01464d', 'HEAD'):
    subprocess.run(['git', 'ls-tree', '-r', ref, '--', *R1_EXECUTED_SOURCES], check=True)
```

| Path | Blob at baseline and assessed head |
| --- | --- |
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |

## Authorized lead checklist after W1 close

1. Resolve the signer's W1 completion, full desk, Check and clearance. Identify the exact
   operational code/config state, the Part C carry and the canonical C1 manifest and kit with
   supplemental ordinals 23 and 24. Require the accepted series admission and receipt bindings.
   The W1 desk-passed code/config artifact digest must equal the current one. Release and
   signer evidence remain with their owners. [RLD pre-sign and C1 release gates](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19784-L19787) ·
   [RLD held-window ruling](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L4352-L4361)
2. Resolve the W1 commit/path and its record SHA-256, the canonical `series/state.json`
   commit/path and digest, and an explicit local remote-tracking ref that reaches the W1 commit.
   Confirm the current ledger names that same latest committed W1. Use the committed,
   digest-bound quiet observation and next-plan evidence, including pool/cohort and four
   sentinels. Choose a new output filename in the authorized environment.
3. Run the read-only packet CLI on the authorized checkout. Require exit 0,
   `packet_preflight.ready=true` and a valid expiry. An exit 2 diagnostic is a refusal.

   ```sh
   python3.13 -B scripts/align_v4_next_arm_packet.py --repo "$authorized_repo" \
     --record-commit "$w1_record_commit" --record-path "$w1_record_path" \
     --series-commit "$series_commit" --series-path series/state.json \
     --pushed-ref "$local_tracking_ref" --output "$new_packet_file"
   ```

4. Check that the arm consumer's own `rebuild_and_compare` uses its current bound artifact digest
   and clock, matches the supplied canonical packet, still proves the latest record and passes
   its rebuilt packet to `bind_packet(root, 'C1', rebuilt, authenticated_by_rebuild=True)`.
   Require previous W1 and zero counted C windows. Expiry, current record binding and live
   checks belong to the eventual consumer. This report provides no authority to arm.
5. Leave READY and all signer decisions open until the exact-final-tree integration owner
   and Opus accept. The signed release, four receipt bindings, accepted operational pin,
   W1 completion and restore, notice and veto, fresh host admission, real t0, final packet
   and arm outcome remain with their authorized owners. Fable owns changes to protected rules or
   scientific meaning. Opus owns merges. [PR #836](https://github.com/mpmdw/JouleWise/pull/836) ·
   [PR #844](https://github.com/mpmdw/JouleWise/pull/844)

**NEEDS_SPEC** · None identified by the builder.
