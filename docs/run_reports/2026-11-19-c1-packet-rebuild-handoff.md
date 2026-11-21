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

## Lead audit round 1 · R20 sentinel positions

The independent lead audit on `d5fd0a5d7` reproduced one inherited VERIFIED HIGH, an
integration seam. Both a 22-member projection with ordinary members 20 and 21 relabelled
and a projection with all four canonical sentinel IDs at 5/20/21/22 returned CLI 0 and
matched the arm rebuild. Cohort, full desk, committed-record and C1 history binding did
not catch the missing supplemental positions. The lead authorized the correction in the
single, still-unsigned W1 candidate. The one W1 signing receipt binds that candidate.
[Protocol R20](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/pilot_protocol_v4.md#L1024-L1035) ·
[RL-182 §1.5](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19777-L19802)

The original executable spec remains at `9fba97178`. Supplemental freeze
`49ac71d4e8ef5b63ef02e30d46dc37a276ec0ee0`, tree
`39c94a488f9d9bbd9d180d1f9143c1b4340847f4`, added both reproductions, the ordinal sweep,
and the W1 digest carry witness before implementation. Its run of 17 methods exited 1
with two incorrect CLI admissions, 231 missing-validator sweep errors, and one missing
desk/receipt-proof assertion. The original assertions stayed in place.

The fix at `e0fc1392fc95adcd31812a781423e8f4452a3db7`, assessed code tree
`03faa3637f463e26018de2764de908bad4dde89d`, reads the same committed series manifest
whose SHA-256 the series binding checks. The series producer's ordinary and R20 allocations
supply the expected ordinal and run-ID pairs. The packet verifies the digest-bound
next-plan projection against those pairs, including roster shape and unique identities.
The ledger list must agree with the derived IDs. The validator also checks later series
windows, and the U4-only trigger still governs when supplemental members are mandatory.
The W1 desk artifact-set digest is derived and compared as before. The packet carries the
committed W1 desk SHA-256 and the SHA-256 of its registration receipt when W1 exports it
or the canonical receipt is committed with its record. Both receipt copies must match
when present. The signing gate and all issued artifacts stay with their owners.

None of RL-182 §1.5's eight protected functions or constants changed. All ten
condition-13 Git blob IDs match the W1 baseline, with zero inherited absences.
The original fixture identities above describe the first published tree. The shared
fixture now uses a full digest-bound next-plan projection for the stricter check.

The finalized focused class passed 18/18. Both audit cases and the swapped-ID control write
CLI exit 2 diagnostics with `sentinel_roster` failed. The sweep passes only the frozen pair
over all 276 pairs of the 24 positions and refuses five additional wrong-cardinality sets.
The genuine roster and the receipt replay are ready. An uncommitted edit to the canonical
receipt does not replace the digest from W1's committed evidence.

| Synthetic case | W1 record commit | Series state commit | CLI |
| --- | --- | --- | --- |
| Genuine 24-member C1 | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `7ee21ffaa9ae590e2cae83fc1b72687299666822` | 0, ready |
| Ordinary 20/21 relabelled | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `7677caebf66af4e4d0e3e92412924b7c0d14c72f` | 2, refused |
| Exact sentinel IDs moved to wrong positions | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `2a99c6e0d59915282ae5e11564b2f976ad61c07a` | 2, refused |
| IDs swapped across positions 23 and 24 | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `a2c57ad37deec57caf4ccc0773cba94c03721bb4` | 2, refused |
| Committed synthetic W1 receipt | `1cf442dd6f717a9244aa0bc362e2466fd57b1973` | `9a3409a9c53deab9a94bc255e685299356b42744` | 0, ready |

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_next_arm_packet.PacketTests align.test_v4_next_arm_packet.SentinelTriggerTests \
  align.test_v4_next_arm_packet.DeskDerivationTests tests.align.test_v4_claim_b_packet \
  tests.align.test_v4_series.PacketTests tests.align.test_v4_series_delta5
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  tests.align.test_r11_delta6_sol1.Delta6Witnesses.test_u5_inconclusive_does_not_trigger_sentinels_but_u4_does
git diff --check b2e01464d HEAD
```

`NEEDS_SPEC: none`. The lead's engineering ruling resolves the prior scope and projection
hold. The exact final-head CI is recorded in the draft PR ledger and the seat handoff.
W1 signing, the final post-close packet, and integration-owner and Opus acceptance
remain with their owners.

### Hosted fixture compatibility

The first hosted run at `a30b0fd3f` found a setup regression in shard 11.
The shared `Scenario` created the synthetic series directory in its constructor,
before W1 prequalification copied its own fixture directory there. That caused six failures and
four errors in `test_w1_prequal`. Default manifest creation now runs at fixture
finalization and preserves caller-supplied series bytes. A disposable R1 fixture
verified the same copy sequence, retained a caller-supplied companion blob, and built
a ready W1 packet. The production sentinel gate and both executable freezes remain
the same. [First hosted shard 11](https://github.com/mpmdw/JouleWise/actions/runs/44702660992/job/136175741092)

### Hosted mutation-inventory compatibility

The second hosted run at `459497d6c` passed the repaired prequalification module 42/42
and the packet module 64/64. Its packet-tamper probe refused all 490 mutations, with zero
admitted. The shard failed because the previous test expected 488. The frozen manifest is
now a source in the sentinel check, yielding one changed-source and one removed-source
probe. The independent mutation assertions now require both new probes and the count of
490. A local synthetic packet also reproduced that count and independently rebuilt both
edited packets with canonical comparison false. The R20 gate code is byte-identical
through this test correction.
[Hosted prequalification](https://github.com/mpmdw/JouleWise/actions/runs/44712187100/job/136208242934) ·
[Hosted packet and mutation probe](https://github.com/mpmdw/JouleWise/actions/runs/44712187100/job/136208242907)


## Lead audit round 2 · v3 freeze and build

Round 2 on `13de6a387` verified one HIGH integration seam and one MED regression.
Its HIGH plus MED count rose from one to two. The lead approved a return to spec and
a build restart on this draft. The original freeze `9fba97178` and R20 supplemental
freeze `49ac71d4e` remain in the published history. The five v3 cases were committed
at `5d04e0dc54a28605b99675a2619eafce5fb390c5`, tree
`40955eff9386aeb379301fb7d7a312ece1fc5fd1`, before editing production.
With the validator still at `13de6a387`, the five-case baseline exited 1 with two
expected failures and three passing controls. W1 borrowed R1's digest, and the
genuine ordinal-free projection refused.

The fix at `c80411e8eaa04d8770b13f41e954d2364c8d8c51`, tree
`e2c53ad9ad8192168dd40443e21dcc8e28d7cfb1`, ties the last desk-passed record
to the authenticated W1 predecessor by commit, path, and record SHA-256. A pass
therefore compares W1's own committed artifact set to the consumer's current
digest. The older-digest refusal keeps its existing diagnostic. The rebuild
retains the W1 desk hash and any committed registration receipt hash, and requires
agreement when both receipt copies exist. The validator leaves receipt issuance
and the protected RL-182 functions with their owners.

The full, ordered roster supplies one-based positions. Any explicit ordinal must
be an integer equal to that position. The sentinel mapping is still derived from
the frozen manifest. The rebuilt ordinal-free C1 packet matches and binds with
all live checks pending. Moved, swapped, and duplicate IDs, missing supplemental
rows, and conflicting explicit ordinals refuse at the sentinel check.

| Invented case at clock 111 | W1 record commit | Series state commit | CLI |
| --- | --- | --- | --- |
| W1 desk on W1 code before changing checkout | `8a3833d8963ecafb7b69f2264a782e681c93a8b2` | `ae0ce6baef6338a3c193cb3571bbfe01f1851f0b` | 0, ready |
| W1 correctly named, checkout on different code | `8a3833d8963ecafb7b69f2264a782e681c93a8b2` | `a983312d39404859e2ec64f50a3ae9407e4018d7` | 2, refused |
| Only last-passed pointer switched to R1 | `8a3833d8963ecafb7b69f2264a782e681c93a8b2` | `9423123c6bbf60a7207e5f84ab605ef2bcfb6288` | 2, refused |
| Complete ordered projection, ordinals omitted | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `95c29cc813d99b192f5c5b9281f13a6166bb6833` | 0, ready |
| Full W1 proof, matching committed receipt copies | `89aa8e843537908fd434d5021581c3cce68caa92` | `2e8afb0e1f43d17f30d7e463ac4fda9bb6f25feb` | 0, ready |
| Different committed canonical receipt copy | `ef34b2f2ab669e55012bdb70426c6d0f69c66820` | `50f7600ae5bf1f46017b3647a81068ad1f076e48` | 2, refused |
| Legacy projection, sentinel IDs moved | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `eebe717e6b1eedb783a0e500301053157f3dbc1a` | 2, refused |
| Legacy projection, sentinel ID duplicated | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `fe0bd9dcd66783be21c482e1b2a7f5f3230d1375` | 2, refused |
| Explicit ordinal contradicts position | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `cd2ba5cc6937e49a3a34ba4372fb36e9a3e8710e` | 2, refused |
| Explicit ordinal is Boolean | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `1cbaa49255081f4addeca75d0109e3f296d11f45` | 2, refused |
| Explicit ordinal is a string | `ae3e2dfce849af3a03565c5e636f4949c384ef6f` | `d451ae994e605c1d91eaf9ca0b720f352bdae48d` | 2, refused |


The v3 regressions pass 5/5 after the fix. For the post-close command above,
the authorized lead supplies a `last_passed_record` reference identical to the
authenticated W1 predecessor's commit, path, and SHA-256. The lead carries one
signed registration receipt and verifies that any committed copies agree.
The complete C1 roster may use only `run_id` and `role` in frozen order. If the
projection includes `ordinal`, it must agree with that order.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v -k test_v3_ align.test_v4_next_arm_packet.C1PacketRebuildTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_next_arm_packet.PacketTests align.test_v4_next_arm_packet.SentinelTriggerTests \
  align.test_v4_next_arm_packet.DeskDerivationTests tests.align.test_v4_claim_b_packet \
  tests.align.test_v4_series.PacketTests tests.align.test_v4_series_delta5 \
  tests.align.test_v4_replacement_windows.BuilderTests \
  tests.align.test_r11_delta6_sol1.Delta6Witnesses.test_u5_inconclusive_does_not_trigger_sentinels_but_u4_does
git diff --check b2e01464d HEAD
```

`NEEDS_SPEC: none`. The lead's v3 ruling resolved the two findings. Exact-head CI is
recorded in the draft ledger and the seat handoff. The integration owner and Opus
still own exact-tree acceptance. W1 signing and the final post-close C1 packet
remain with the lead or magistrate.

## Lead audit round 3 and K1

Round 3 on `21010e9fb3e40d8e773640484dab3cfac005485f` verified one HIGH
integration seam and zero MED or LOW findings. In the disposable audit
reproduction, both the 24-member C1 kit and the ordinary 22-member kit passed
the materializer's own check. A packet built for the 24-member kit also
admitted the ordinary kit. The series binding and artifact-set digest both
passed. The round 3 HIGH triggered a return to spec under Pipeline §3.
The lead's K1 ruling supplied the revised contract. Earlier freezes
`9fba97178`, `49ac71d4e`, and `5d04e0dc5` remain in the history.

The five K1 cases were frozen before changes to the validator at
`b3b8df3a20e8ece337c16953780eb984348b227d`, tree
`9d67246781279a8f727720445680cb43a3c40ec7`. The baseline with the validator
at `21010e9fb` exited 1. The positive control found no kit identity, the CLI
reached the synthetic host trap and returned 1, and all seven direct mismatch
assertions saw admission. The five frozen methods now pass.

The packet incorporates the materialized C1 kit from the exact series commit.
It carries a SHA-256 over the canonical map of kit filenames and file
digests, the raw collection-plan digest, the member count, and sentinel
ordinals. The builder compares the kit's ordered IDs and roles to the bound
projection. The CLI checks the selected kit before host actions.
`arm_checks` independently compares the actual selection to the packet it
rebuilt. It also checks the staged plan and the prepared launch tree's digest
binding. It verifies the copied science configs against the frozen plan.
`packet_kit_mismatch` refuses install with exit 2. Projection-only packets
remain usable for off-host preflight. A C1 install requires the committed
kit binding.

| Finding | Fix | Regression |
| --- | --- | --- |
| Round 3 HIGH, 24-member packet could admit an ordinary 22-member kit | `22461975ee2b6d60e8a0563a7b7a028d0d93c5ad` | True 24-member materialization admits under invented host inputs. True 22-member replacement refuses despite identical packet rebuild and successful series binding. The CLI refuses the replacement with exit 2 before host access. A same-plan kit byte change refuses. Counts 22, 23, 25 and 26 and a moved sentinel each refuse. |
| Staged kit checks | `22461975e`, `7b3557ee6824768fc11e89544c6f8349c66ba30f` | A stale staged launch tree or edited staged config refuses while the source kit still matches. |

The invented replay at clock 111 uses W1 record commit
`46c68cbdc92d66613e3ebdb3e4931e087c98e8cd`, path `w-W1/record.json`,
series commit `e9a24bf05a0322fd0d16747434b510aafa93bf4c`, path
`series/state.json`, and ref `refs/remotes/synthetic/records`.

| Kit consumed | Kit SHA-256 | Plan SHA-256 | Result |
| --- | --- | --- | --- |
| Frozen 24, sentinels 5/22/23/24 | `8e2b1c986990d932458d1e07a59079f6b3c5a993746649bc7dcb2e336511dbba` | `7e99554bcd0cb3fc8ac3ac681a9413ec398f6f81680dba856c6a022138cff968` | Builder exit 0, ready; synthetic arm admitted |
| Ordinary 22, sentinels 5/22 | `b45cb44388b6cccac8a1e6f9dc6d57eaa4ec9a9a9c7f4001f9973dfd6f8cd849` | `3bca149c7d71c21c80e039ef8aa8e75c339876ae2a41102e70835ec247be5b70` | Canonical rebuild still matches; arm refuses with `packet_kit_mismatch`; CLI exit 2 |

The regression fix commits have trees `f23eabdce03d9f252148b6f44bcbfdf4b035581f`
and `aed6f987c6d391ecfe99e2da52a3ece4dc4db07c`. Exact published head,
test-merge tree and hosted CI results are tracked in draft PR #896 and
the seat handoff. All ten condition-13 Git blob IDs match the W1 baseline
`b2e01464d`, with zero inherited absences. RL-182's eight protected
functions and constant remain at their existing bytes.

### K1 commands and lead hold

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests -k test_k1
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_r11_delta5_sol1 align.test_r11_delta5_sol2 align.test_v4_series_e2e
git diff --check b2e01464d HEAD
```

For the authorized lead's post-close packet, run the builder command above
with the materialized C1 kit under `configs/campaigns/align_v4_c1` in
`--series-commit`. Use the exact chosen 24-member plan when W1 U4 is
inconclusive. Check that the packet reports its kit digest, collection-plan
digest, 24 members, and sentinel ordinals `[5, 22, 23, 24]`. Rebuild from
that commit and use the same selection in the consumer. The authenticated
W1 desk and receipt digests carry forward. W1 signing, integration-owner and
Opus acceptance, and the final post-close packet remain with their owners.

`NEEDS_SPEC: none`. Only invented fixtures were used for the audit replay
and software checks.

### Hosted integration repair

The first K1 run reported 20/21 jobs passing on `df4c9b2db`.
Shard 8 exposed two integration issues. Its dwell-order witness needed a
committed C1 kit before the real arm could reach the dwell stamp. Its
production-path replay also showed that the night plan's hazard budget
counts scaffold dispatches along with C1 science rows. The check had
compared that larger number to the collection-plan roster, which stopped
C1 and skipped the subsequent history in the replay.

Commit `2fece9927b615da715f7753f46981c78e6124b99`, tree
`68df4829f2b24c67fd5438a9537660ac9c2c64c5`, retains the exact
collection-plan digest, kit digest, roster and sentinel comparisons,
as well as the staged launch-tree and copied-config checks. It compares
the C1 roster through the staged science rows. The synthetic end-to-end
fixture now uses the real, larger scaffold-inclusive budget. The existing
dwell-order witness now uses a committed kit from the synthetic materializer.
Its disk-usage call is a stand-in. Neither fixture performs host probes.
[First hosted shard 8](https://github.com/mpmdw/JouleWise/actions/runs/44755731193/job/136355110044)

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest -v \
  align.test_v4_next_arm_packet.ArmOrderWitness align.test_v4_series_e2e
```

## K2 and K3 · bind the staged dispatch

The supplied audit assessed `314867f42360a4862ccfc310ef6135db3f0a817e`,
tree `aa4cfc5596b6a9743c166c9fc99e1c13cf60c550`, against W1 `b2e01464d`.
It verified two HIGH integration seams and zero MED or LOW findings. A stale
second-stage order manifest removed members 23 and 24 while K1 still accepted.
The genuine linked staging view refused because the W1 artifact digest treated
its links as missing. The lead supplied K2 and K3 and directed a return to spec.
The existing freezes remain in the history.

Freeze `9a50d8f02d1986a5d09e06b59491e63d0c742074`, tree
`1480d8c4036c4d5743bd3995104bf439b0e9b047`, committed six executable
acceptance methods before the build. The baseline with the validator at
`314867f42` exited 1 with nine expected failed assertions. The edited same-roster
bytes, reordered manifests, ordinary second-stage manifest, changed staged kit
copy, and escaping links escaped their intended refusals. The normal linked
view refused. The byte-identical copy control admitted.

Fix `c6887e3f2dcaa1176175c06b6afb52a48ea27885`, tree
`cc21bbcb6c3e0fcbf002af4e7322132fe30af559`, has two parts.

| Finding | Contract and regression |
| --- | --- |
| K2 staged dispatch | The builder binds ordered science IDs and per-stage manifest and config digests using the committed campaign inputs and the production relocation. At install and arm rebuild, the consumer resolves the actual staged argv with the existing dispatch resolver. It checks every manifest, including auxiliary stages, and validates the ordered C1 IDs and frozen sentinel positions. The real ordinary second-stage substitution, the ordered and byte-only sweeps, and a changed staged kit copy refuse before host access. |
| K3 staged artifact identity | The consumer computes W1's current artifact digest from the actual staged bytes. Source and staging are the allowed roots. Confined links and identical copies admit. A manifest or registered artifact link escaping the roots refuses with exit 2 and `packet_kit_mismatch`. The guarded tests trap any access to an escaping target. |

The production-shaped series witness sweeps every science and scaffold order
manifest. The earlier K1, roster, predecessor and desk tests remain. The
lead's post-close command above uses the selected kit, auxiliary order manifests
and configs in the same committed series tree. Any launch input substitution
after the packet requires rebuilding from the authorized committed selection.
W1's desk and receipt digests still carry forward. The signer, integration
owner and Opus retain their existing acceptance holds.

The invented replay at clock 111 names W1 record
`f08685d0743810a635162d8073062b39695577f9` at `w-W1/record.json` and series
`3f1cec3d6076c90f5404bbeb26c205198e8dbc4d` at `series/state.json`. Its tracking
ref is `refs/remotes/synthetic/records`. The builder exits 0 for this packet.
The plan SHA-256 is `2c92ea12419c0f59d8d50929bd70be8e78fd01ebe4f81d66b1c18ec9a9fab772`.
Its staged science order manifests have these expected digests.

| Synthetic stage | Staged order SHA-256 |
| --- | --- |
| C1 episodes A | `df379a2f9d36fd4b0fd289c8ce45b8796aee103982bf0a976839dca615a9c6aa` |
| C1 episodes B | `29e763ab46835ae566c3a2c3c293f2df4d608aafbee7d94b9c1371bc875f7652` |

The genuine linked view admits with the rebuilt packet. Substituting the
ordinary episodes B manifest resolves 22 members. The same packet still
rebuilds identically and the arm refuses at `packet_kit_mismatch`. Its CLI
exits 2 before the host checkpoint.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests -k test_k2 -k test_k3
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest -v \
  align.test_r11_delta5_sol1 align.test_r11_delta5_sol2 align.test_v4_series_e2e \
  align.test_v4_next_arm_packet.ArmOrderWitness
git diff --check b2e01464d HEAD
```

`NEEDS_SPEC: none`. The ten condition-13 identities remain identical to W1,
with zero inherited absences. Exact-head hosted results and final-tree holds are
in the draft PR ledger and seat handoff.

### Hosted fixture repair after the pause

On `8a57514c`, the saved focused class passed 35/35, the adjacent contracts
passed 33/33, and the six-stage substitution and byte-edit sweep passed.
Hosted CI passed 20/21 jobs. Its failing shard passed the packet module
81/81 and the 490-case mutation probe. The C1 production-path fixture failed
when the new reader correctly refused the scaffold directory links inherited
from the generic synthetic harness. The subsequent series subtests lacked the
C1 predecessor because that fixture stopped before C1.

The fixture repair copies the two scaffold input directories into its own
checkout, replacing inherited links in that disposable checkout. It keeps the
production confinement and dispatch checks. A bounded replay of the repaired
fixture constructed the real measurement view and verified the staged kit,
all six stage manifests, and the 22 ordinary science members. The replay
trapped prepare and install. The focused W1 U4-inconclusive replay continues
to cover the 24-member roster and the supplemental-sentinel refusal.

[First hosted shard](https://github.com/mpmdw/JouleWise/actions/runs/44783036619/job/136450919559)

## K4 · whole staged input inventory

The supplied audit at `7cae941b39c5fe2fadf8e3d87e5ce8012ab207ce`, tree
`0424e86b266093e0ec685e9754ff4fce3e0f2d65`, verified one HIGH with root
cause `integration-seam` and zero MED or LOW findings. All six earlier findings
were refuted. The staged derivation argv read a manifest that had a different
reference member while the packet and staged campaign orders stayed unchanged.

Freeze `7f6bdbbefc1c2cea375f219eeb8b487aea1fc635`, tree
`2578b092c9b715a3c30710b0fa72ef0ffdd7b7b1`, preceded validator edits.
Against `7cae941b`, the three frozen methods exited 1. The derivation
mutation passed the arm, and both the read-set and byte-sweep methods found
no staged inventory. Prior freezes remain in the branch.

Fix `ba5982b1b4d56527b8490ca18435829563bef3d2`, tree
`4cb20394183fe2bc56b583a0dd8edda4c33323f6`, derives the inventory from the
committed selection and the same renderer that creates the relocated files.
It includes the original and relocated kit, launch tree and digest, stage
orders and configs, stage file dependencies, and registered artifacts. The
consumer checks all listed bytes before decoding staged inputs. It reuses
those checked bytes and refuses unlisted reads before opening them. The
instrumented test observes the actual CLI and arm reads. The additional
unlisted-read test injects an input request and traps any attempt to open it.

The transport pin comes from the exact packet blob committed at
`series/c1-next-arm.json` in source HEAD. This detached pin authenticates the
packet's raw bytes before parsing. The independent rebuild still uses its
explicit record and series commits. Normal staging links remain confined to
the view and source roots. The prepared plan and live control files enter
from outside the immutable view.

| Fixture evidence at clock 111 | Identity or result |
| --- | --- |
| W1 predecessor | `f8d6eae8949682d79781ff5e3c7c5db1c295a64f:w-W1/record.json` |
| Series selection | `dd1e03fd1d174deada996d2c0598691780d72881:series/state.json` |
| Pushed proof | `refs/remotes/synthetic/records` |
| Packet transport | `3ebd16ec2b7d2926f16681e6e5d6902ab33f2f46:series/c1-next-arm.json`, SHA-256 `a9422117718f6d09104a11d82f60afa368204d16526ed24d1eaad32f5a394692` |
| Staged launch tree | SHA-256 `3918db0b17201335f0e37a5e5af28937f972fc3f9830bedc998f581b2cdc0c56` |
| Genuine derivation | SHA-256 `ad319d72e1b24345b8f6fa95f9adc75c59a301a86e9c3e863a9ddb64fcddf9e2`. One call to the mocked host checkpoint, which deliberately returns CLI exit 1. |
| Changed derivation member | SHA-256 `d2c7c1501bbc87c729a5ba6c4dbe531774ce5dff504b743c2fa32d592ee05bad`. CLI exit 2, zero checkpoint calls. |

The fixture contains 69 pinned files including the packet, plus 329 explicit
artifact absences. The byte sweep flips the first byte in each pinned file
on a disposable staging view and restores it after each check. The bounded
production fixture also verified its linked staged kit, auxiliary inputs, and
all six relocated order manifests with prepare and install trapped.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests -k test_k4
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_series_e2e align.test_v4_next_arm_packet.ArmOrderWitness
git diff --check b2e01464d HEAD
```

The authorized lead supplies the committed materialized kit and its launch
dependencies at the series commit and builds the post-close packet as above.
The lead commits the exact output locally in the prepared source checkout as
`series/c1-next-arm.json` and uses the corresponding
`measurement/series/c1-next-arm.json` as the arm pointer. The W1 desk and
receipt digests carry forward. No integration-owner, Opus or signer hold was
satisfied by the synthetic checks. `NEEDS_SPEC: none`.

The external-control guard also applies to the daytime receipt named inside
the disk configuration. The adjacent regression confirms that an external
configuration cannot cause an unlisted staged receipt to be opened. The
normal synthetic disk and installer witnesses still exercise their existing
paths.

At published head `f433b13ef97f4ea2f81868880134b8c968199c37`, all 39
focused cases passed. Targeted end-to-end checks passed for the D1 alias,
the transitive daytime receipt and unbound W1 and C1 packets. Hosted shard 12
found that the four existing prepare-time checks moved from
`measurement_view` into `render_measurement_files`. The refusal census
keys entries by function name, so it reported four stale and four unlisted
locations. The follow-up updates those four INTERNAL entries. A structural
comparison confirms identical counts, guard digests, classifications and
explanations. The focused census tests for exact sites, the frozen baseline
and reviewed entries passed 3/3.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v \
  hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count \
  hazards.test_refusal_allowlist.RefusalAllowlistTests.test_the_baseline_is_frozen \
  hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_entry_names_what_it_protects
```

[First K4 hosted shard](https://github.com/mpmdw/JouleWise/actions/runs/44913514476/job/136874281415)

## K5 · required staged dispatch closure

Audit 6 assessed `cdca388237a488a8f3be50a7963499a89e61dad6`, tree
`04b22cc88ecc495f1e8612ccb34a5193446a026f`. It verified one HIGH with
root cause `integration-seam` and zero MED or LOW findings. It refuted all
seven earlier findings. In the invented replay at clock 111, the staged
bound-derivation command still named its corpus manifest after that file
was omitted from the selected series commit. The builder exited 0, the arm
admitted, and install reached the mocked host checkpoint.

Freeze `1c74984a811196578371679d9db07a1d6dc1e430` (tree
`f3c26b767968170d579092fce3c0ece4596cf673`) records the named audit
regression, the independently generated file and pin deletion sweeps, and
the extra inventory entry. On `cdca38823`, deleting files with retained
pins already refused. Removing 44 inventory entries separately reached
the checkpoint. The extra matching entry and the missing committed
derivation file reproduced the gaps. Freeze additions `384aaa6a9` and
`5eaf638c9` cover the missing materialized head pin, a null dispatch
digest, and a registered file falsely recorded as absent. All earlier
frozen cases are retained.

`cc7393857d5ce937cc7bfaf5d7eaae7d2346a140` derives the required files
from the validated staged commands, actual order resolution, spare orders,
mirrored kit, and launch-tree files. The builder requires committed inputs
for explicit repository arguments even without a stage input descriptor.
The install gate checks set equality and verifies all remaining required
bytes before the host checkpoint. It also compares registered artifact
pins and absences to the named series commit. The detached transport pin
still authenticates the packet bytes. The resolved tree and orders are
decoded only from digest-verified bytes. The synthetic production-shaped
control resolved all six order manifests with 22 ordinary science members.
Its disposable checkout supplies an inert identity for the backup tool
named by the desk-stage argv.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests -k test_k5
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_v4_series_e2e align.test_v4_next_arm_packet.ArmOrderWitness
PYTHONPATH=tests:. python3.13 -B -m unittest \
  hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count
git diff --check b2e01464d HEAD
```

The authorized lead's command and input checklist above applies. Commit
the executable C1 kit and all resolved command inputs at the named series
commit, including the derivation manifest and calibration head pin.
Produce and pin the post-close packet before the arm uses it. The full-desk digest
and registration receipt hash are carried from authenticated W1 evidence.
The integration owner and Opus still own their acceptance, and the lead
or magistrate owns the final packet. `NEEDS_SPEC: none`.

| Invented fixture at clock 111 | Identity or observation |
| --- | --- |
| W1 predecessor | `e508999068273bb018c6974b2f65b1fd3d096771:w-W1/record.json` |
| Series selection | `038bcf2091e1d372585f49db5d0642ab08b2a6b1:series/state.json` |
| Pushed proof | `refs/remotes/synthetic/records` |
| Packet transport | `0c872dee2f7bcdd950ee5954982ad5e8e0e8abc1:series/c1-next-arm.json`, SHA-256 `95b33786d7bf2696a201e0117ae7d4e4da1dc1c1b6500d0da391714062735e69` |
| Complete staged input closure | 71 referenced files, one detached packet pin and 326 registered absences. The genuine CLI reached the mocked checkpoint exactly once, which deliberately returned exit 1. |
| Omitted derivation manifest | Series commit `464a52448a9360231c7e86f13f11b42eec0a6b1e`. Builder exit 2, `packet_preflight.ready=false`, failing `sentinel_roster`. |
| Sweeps | 71 staged-file deletions and 71 independent pin deletions. The earlier one-byte sweep includes the detached packet and the three newly required tool program pins. |

The resolver reports the original verified-reader error when an order
cannot be opened. This preserves the existing path-specific SHA-256
diagnostic for the K4 byte sweep through the new closure check.

On `6f158deaa`, hosted shards 5 and 10 exposed three older Delta 5
witnesses that materialized the C1 roster and scaffold run IDs without
the committed launch inputs. Their shared fixture now supplies typed
invented scaffold configs, order descriptors, the head pin, and inert
program and repository-argument identities. The same handoff, retry,
history and target assertions run against the strict closure.

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest -v \
  align.test_r11_delta5_sol1 align.test_r11_delta5_sol2
```

The six targeted K5 and retained K4 methods passed on `6f158deaa`,
including all 142 closure deletions and 72 byte mutations.
[First hosted shard 5](https://github.com/mpmdw/JouleWise/actions/runs/44927145240/job/136915747581) · [First hosted shard 10](https://github.com/mpmdw/JouleWise/actions/runs/44927145240/job/136915747633)
