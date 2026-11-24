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

A follow-up bounded replay of the first Delta 5 fixture repair found
the derivation descriptor still carried its source template's SHA-256.
The fixture now also binds stage input descriptors to the invented files
and their manifest IDs. The bounded W1-to-C1 builder replay returns a
passing `sentinel_roster` with a ready packet and a complete inventory.
The validator still refuses mismatched committed input descriptors.

## K6 · canonical stage argument paths

Audit 7 assessed `55878150dba2302ec41fe9b7faaee6553b93bce7`, tree
`ac3c2c4c98cf86e6cb03344b285b3c9562adbf9d`. It verified one HIGH
`integration-seam` and zero MED or LOW findings. It refuted the eight
earlier findings. Two invented derivation commands resolved to the same
file. The `repo_path` spelling recorded its digest and the
`binding_path` spelling relative to `repo_root` omitted it. Both
packets built and both synthetic arms admitted.

Freeze `4b04484ef2b631687561f12424095e62b3a6b0a2` (tree
`6f3bd4c24a911661db8549c5f0c172fe7b621fb8`) precedes implementation.
On `55878150d`, the frozen three methods exited 1 with 11 failing
assertions and subtests. The alternative derivation spelling lost its
pin, three equivalent spellings could not resolve the collection
directory, and the standalone builder accepted unrecognized binding
names or invalid path operands. Earlier freezes and regression methods
are ancestors of this change.

`f89fd2247b4c240a7134624f03d7a098516da37d` (tree
`6a792dc17b5cca588d15870909d506af50231b37`) uses the runner's argument
binder in the stage resolver. It projects the repository as the command's
working directory. `repo_path`, `binding_path` rooted at `repo_root`,
relative literals, and tree-pointer values all yield the same logical
repository-relative key. The staging renderer and the packet closure
both use this resolver. Collection directories expand through the
resolved order, and explicit stage descriptors share the same path
normalization. The prepared `repo_root` must name the staging view.
Existing confinement still resolves staging links within the allowed
roots before reading bytes.

The current bare `binding` names supply the repository directory or
runtime controls. They supply no portable frozen file. The resolver
accepts documented runtime controls in their stage roles and refuses an
unknown kind or name, a scalar used as a path base, a root supplied as a
file, or an escaping path. It classifies literal and tree-pointer
operands using the stage option roles. This preserves files named by a
bare relative filename, such as the invented campaign policy in the
sweep. The raw committed packet remains separately pinned.

The sweep covers four portable file forms, 15 input classes, and three
pin states, for 180 comparisons. The exit, checkpoint count and
diagnostic bytes are identical across forms for each class and pin state.
The 120 missing or wrong pins must exit 2 with zero host calls. The
healthy control reaches the mocked checkpoint. The existing K4 byte
sweep, K5 deletion sweeps, C1 roster cases, and preceding gate cases
continue to run. The unknown-form method also checks the prepared root.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests -k test_k6
PYTHONPATH=tests:. python3.13 -B -m unittest -v align.test_v4_next_arm_packet.C1PacketRebuildTests
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest -v \
  test_b5_plan.StageDispatchTests test_bytes_h_session \
  align.test_v4_series_e2e align.test_v4_next_arm_packet.ArmOrderWitness \
  hazards.test_refusal_allowlist.RefusalAllowlistTests.test_every_refusal_site_is_listed_with_its_exact_count \
  align.test_r11_delta5_sol1 align.test_r11_delta5_sol2
git diff --check b2e01464d HEAD
```

The authorized lead's command and input checklist above applies. The
lead or magistrate owns the final post-close packet. Integration-owner
and Opus acceptance, the cold final pass, and W1 signing remain open.
Audit 8 is the last handoff for this builder lane. A new binding-form
finding returns to the lead for a closed binding-form spec.
`NEEDS_SPEC: none`.

Both invented cases used W1 record
`50d6b1d301a073eca64e9a396d0c17e4b13b0ba1:w-W1/record.json`
and `refs/remotes/synthetic/records` at clock 111. They each
recorded 71 staged pins. The canonical derivation key was
`configs/campaigns/fixture-derivation/settled_corpus.json`, SHA-256
`ad319d72e1b24345b8f6fa95f9adc75c59a301a86e9c3e863a9ddb64fcddf9e2`.

| Form | Invented series and packet transport commits | Builder / present install / omitted pin |
| --- | --- | --- |
| `repo_path` | `455c1bd0a91c4ed8b6b6a77a79b42a5d792315b6` and `256d9f9f8d94e54d19ed2cd7fdaf6dae3d957819` | 0 / 1 with one mocked checkpoint / 2 with zero checkpoints |
| `binding_path` relative to `repo_root` | `52339747f3bbfaf33144d72f05d79c0c63897c0e` and `b621d4eba49600d10b35e873c7dacea4b2fa66dc` | 0 / 1 with one mocked checkpoint / 2 with zero checkpoints |

## Round 9 · full staged closure

The lead returned the lane to spec after audit 8. The supplied manifest
`20b8dbc75c2fa496ec5d68888be3168cddf81194c83ce65fe68999771f398279`
and all nine listed files were verified and frozen before implementation at
`d7701aa716c18eff1b78c85bdb06b38dc34b4715`, tree
`e2c920521c6ebd574e7e8726e6efd1d23de8dcb8`. The freeze check constructed
37 filesystem vectors and verified the offline R1/W1 history and 57 named
integration vectors. The baseline had no full tree/walk entry point. The
preceding audit reproduced the bare ledger and omitted policy false
admissions and the explicit bracket false refusal. The earlier freezes
remain in the branch history.

Implementation `3ae356e818e1b8bd9cec88597f9ba36d62bddd1a`, tree
`b909d7001805f864a3bd0f48d5a2dd46732ab6ff`, replaces operand-derived
inventory with two disjoint walks. The repository export is compared to the
execution commit's Git modes, blob IDs and tree ID. The staging walk verifies
the exact file set and hashes it against prepare's declared outputs and the
fixed packet blob supplied by the named attempt ref. Both install and direct
arm validate the closure and selections before host access. The same
preflight resolves the kit and stage/spare dispatch, the W1 predecessor and
desk evidence, its own canonical packet, latest record and expiry.

The declared-file C2a case introduces a stray before finalization. The
declaration omits it and the arm gate refuses the actual stage. The O2a case
uses a complete pin for a separate same-byte ledger. Path identity refuses it
even with a valid hash. The reservation verifies the starting SHA-256 under
the existing lease. Later snapshots use the same file after append. The
installed frequency helper's observed path and SHA-256 are recorded in the arm
record. This lane used synthetic helper, ledger and command evidence.

The registration artifact catalogue and receipt files retain their prior
membership and bytes. The closure implementation lives in the already
registered validation module. The retired K4–K6 pin-map tests were replaced by
the full-walk tape and addendum checks. The cadence and replay witnesses keep
their synthetic authority seams, and separate tests exercise the real C1
commit and consumers. Metadata-only `git ls-tree` checks matched all ten
condition-13 Git blobs against `b2e01464d`, with zero inherited absences.

### Executable checks

```sh
(cd tests/align/c1_closure_lite && shasum -a 256 -c SUITE.sha256 && python3.13 -B suite/run.py --fixture-check)
PYTHONPATH=tests:. python3.13 -B tests/align/c1_closure_lite/suite/run.py --adapter "$PWD/tests/align/c1_closure_lite/adapter.py" > .row23-seat/r9-observed.jsonl
cmp tests/align/c1_closure_lite/suite/expected.jsonl .row23-seat/r9-observed.jsonl
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_c1_closure
JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_series_e2e align.test_r11_delta5_sol1 align.test_r11_delta5_sol2 align.test_v4_executed_closure test_b5_plan.StageDispatchTests test_b5_plan.WindowPlanTests test_b5_chain.StagePlanTests
git diff --check b2e01464d HEAD
```

The original and supplemental C1 cases, including the kit and order sweeps,
passed 25/25 in the local focused run. The new gate checks, frozen tape and
canonical sharded result govern the published tree. The final PR-head
status and assessment links are recorded in the PR evidence ledger and seat
handoff.

### Authorized attempt checklist

1. Complete W1 signing, the same-state full desk and the predecessor/series
   commits under the existing ownership rules. Prepare C1 on the chosen
   execution commit. The attempt needs disjoint repository and stage roots.
   Keep the starting ledger on the same filesystem for the single live inode.
   The prepare command emits `c1-prepared.json` and declares the exact stage
   outputs. Use the approved supplemental-input declaration only for source
   bytes authorized for this attempt. Entries map stage-relative names to a
   source path relative to the declaration and an expected SHA-256. Carry an
   authorized offline cache under the staged cache root if the workload selects
   it. Preserve the authorized model/runtime and host evidence procedures.
2. With the prepared paths visible, run the original packet builder command
   above with `--c1-prepared "$prepared_handoff"`. Require exit 0 and a ready
   preflight. The finalizer owns committing the resulting packet at
   `series/c1-next-arm.json` on a named attempt ref in the authorized verifier
   repository and placing those exact bytes at the same relative path in S.
   Add `delivery_ref` and `delivery_commit` to the handoff. The real delivery
   and launch evidence stay in the authorized environment.
3. The authorized install command takes `--c1-handoff "$attempt_handoff"` and
   `--next-arm-triage "$stage/series/c1-next-arm.json"` in addition to the
   ordinary install controls. Confirm the packet's committed predecessor,
   roster, clock and live-ledger path. Existing live admission checks and all
   signer decisions remain open until their owners complete them.

Integration-owner and Opus acceptance, W1 signing, the real C1 preparation
and final post-close packet, and all live checks remain with their authorized
owners. The lead or magistrate owns the final packet. Opus owns merging.
`NEEDS_SPEC: none`.

The first adapter replay reached the relabelled-sentinel case and found
that a diagnostic packet omitted the closure when the roster check
refused. The builder now carries the verified transport closure on
diagnostic packets as well. Both consumers can authenticate the attempt
and report the sentinel failure before they consider host access.

The first final-head CI run caught the WP14-C whole-file pin on the
campaign runner, a forwarded optional argument on the W1 CLI route, and
line offsets in the authentication I/O census. The runner was restored
byte for byte to the W1 baseline. C1 now prepares each main and spare
dispatch at a depth that keeps the runner's existing six-level ancestor
scan inside the staged root. Preflight verifies that depth and evaluates
the original parser with the staged defaults. The W1 CLI keeps its
existing argument shape. The authentication census records the same
eight permitted I/O sites at their moved source lines.

Shard 4 exposed two remaining fixture integrations. The dwell-order
witness now uses the explicit projection seam used by the other
preflight-only witnesses and retains its Git, meter and write-order
assertions. The Git-fixture census recognizes the frozen test package's
two named initialization calls only at their exact supplied file digest.
All six targeted checks passed. The frozen files and production code are
identical to the preceding tested head.

Shard 12 reported a refusal-census mismatch and an outstanding
executing-review gate. The census now identifies the four C1 refusal
keys and the prepare-only series dependency. Both focused census
contracts passed. The existing guards and their classifications retain
their prior rows.

The B6 executing-review check names `3ae356e818e1b8bd9cec88597f9ba36d62bddd1a`
and `949298c7c1eb52f10223b6d7fe2237e30bf2d590`. An authorized reviewer
owes an executing-review record for those exact commits. No review row,
issued registration or signer decision was entered by the builder. The
draft remains held on this gate even though the frozen local tape and
the focused regression checks passed.

## Round 9 · audit 1 rebuild

The independent audit of `dc83b3483630350049b69181d3799abbee881958`
verified two HIGH integration defects. It reported zero MED and zero LOW
findings. The executable acceptance freeze is
`23098de753308f97698ab984449428bc319aab34`. Before the validator change,
the three frozen tests produced four expected failing subtests and one
passing control on the audit baseline (`unittest` exit 1).

| Finding | Baseline on invented inputs | Fix and regression |
| --- | --- | --- |
| Supplemental config in the campaign directory | Main and spare both produced builder exit 0, install exit 0, direct arm admit, and one synthetic host checkpoint per route. The campaign's order selection rejected `old-config.json`. | `e6da6a0be` uses the pinned campaign runner's discovery, manifest loading and exact order selection for the logical dispatch directory. `test_declared_extra_json_refuses_in_main_and_spare_dispatch` verifies a digest-bound extra on both routes. Each now produces builder exit 2, install exit 2, direct arm refusal and zero host entries on both routes. `test_dispatch_ignores_declared_file_outside_runner_config_glob` passes with a declared text file. |
| Retired head pin exported despite a later option | Both the split and attached last-option variants passed preflight and entered each synthetic checkpoint, but parsing the campaign with the chain export chose the missing retired pin. | `e6da6a0be` uses one reservation parser for preflight and the chain renderer, including the reservation values exported downstream. `test_reservation_head_pin_export_matches_last_parsed_option` checks that the actual campaign parser selects the validated current pin in both variants. Each produces builder exit 0, install exit 0, direct arm admission and one synthetic checkpoint per route. |

The assessed code tree is `dd07176ec8427ba64d947840c6986fa549a9a2e5`
at `e6da6a0be00aec2fc7ad44948e8d925252defd26`. The protected campaign
runner Git blob remains `2181546feaf0d0db659142533029918c5e9b747c`.
The adapter's wrong-order diagnostic now names the runner's earlier
refusal. The frozen suite at `d7701aa716c18eff1b78c85bdb06b38dc34b4715`
and its SHA-256 manifest are byte identical to the freeze. The renderer's
parse refusal has a census row. Two host command inventory locators now
name the parser function containing the existing command strings.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_c1_closure.C1ClosureTests.test_declared_extra_json_refuses_in_main_and_spare_dispatch \
  align.test_c1_closure.C1ClosureTests.test_dispatch_ignores_declared_file_outside_runner_config_glob \
  align.test_c1_closure.C1ClosureTests.test_reservation_head_pin_export_matches_last_parsed_option \
  tests.test_host_command_sites.HostCommandSiteTests
(cd tests/align/c1_closure_lite && shasum -a 256 -c SUITE.sha256)
PYTHONPATH=tests:. python3.13 -B tests/align/c1_closure_lite/suite/run.py \
  --adapter "$PWD/tests/align/c1_closure_lite/adapter.py" > .row23-seat/r9-audit1-observed.jsonl
cmp tests/align/c1_closure_lite/suite/expected.jsonl .row23-seat/r9-audit1-observed.jsonl
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
git diff --check b2e01464d HEAD
```

The audit regression and host command inventory tests passed 5/5. The
focused refusal census, legacy writer and stage-plan checks passed 16/16.
The draft PR evidence ledger and seat handoff carry the final replay,
published tree and exact-head canonical CI state. The authorized executing
review, integration-owner and Opus acceptance, W1 signing, and final
post-close packet remain with their assigned owners. `NEEDS_SPEC: none`.

## Round 9 · SPEC-LITE round 3, duplicate consumer options

The independent audit of `e4c8893b6e9afbe01f9a4acf4fa11f68fa1e47b0`
verified two HIGH integration defects and reported zero MED and zero LOW.
It refuted both audit 1 findings on that head. The lead issued A1 and A2
for their shared cause. The executable supplement
`39c5cd8321c86b0201bf103a7a1ff919e9483392` was committed before the
implementation. The named synthetic baseline produced four expected
admissions (`build=0, install=0, direct arm=admit, host=1/1`) and the
generated sweep could not find the new parser interface. The frozen
SPEC-LITE suite and its SHA-256 manifest retain their supplied bytes.

| Finding | Named regression | Required and observed result |
| --- | --- | --- |
| Stale corpus operand remained in the renderer while the parser selected a later attached option | `test_duplicate_derivation_corpus_manifest_refuses` | Builder and install exit 2. Direct arm refuses. Both host counts stay zero. |
| Attached runs root overrode the run-root binding recorded for the stage | `test_duplicate_campaign_runs_root_refuses` | Builder and install exit 2. Direct arm refuses. Both host counts stay zero. |
| The audit 1 head-pin reproduction now has an A2 refusal | `test_duplicate_reservation_head_pin_refuses` | Split and attached repeats both exit 2 at builder and install. Direct arm refuses. Both host counts stay zero. |

The implementation at `88139ebffa4289eb79a87892df585a7accbad4c0`, tree
`95d8f039faebacf6bcbfee760a83795d18edafda`, uses the pinned consumer
parser functions with isolated launch defaults. Argparse resolves
spellings to the same action before the C1 gate checks uniqueness. The
renderer and preflight use the selected namespace and parser-reported
argument positions for campaign limits, the configured run roots, corpus
pruning, and spare dispatch. The real terminal status and calibration
verdict CLI parsers parse their generated arguments. Those two commands'
inputs come from the same selected reservation and capture context and
the generated fixed argv. Inline chain helpers consume positional values
supplied by the renderer. Existing non-C1 render routes retain their
calling convention. The protected campaign runner blob remains
`2181546feaf0d0db659142533029918c5e9b747c`.

The generated sweep uses a genuine synthetic spare-enabled chain and the
consumer parsers that handled its rendered argv. It duplicates the emitted
options in split and attached forms and with every option's applicable
argparse abbreviation representative. A singular attached derivation
control binds the same manifest in preflight and pruning and admits.
The frozen tape continues to cover transport, predecessor, dispatch,
semantic and input-selection behavior.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest \
  align.test_c1_closure.C1ClosureTests.test_duplicate_reservation_head_pin_refuses \
  align.test_c1_closure.C1ClosureTests.test_duplicate_derivation_corpus_manifest_refuses \
  align.test_c1_closure.C1ClosureTests.test_duplicate_campaign_runs_root_refuses \
  align.test_c1_closure.C1ClosureTests.test_duplicate_option_spellings_in_every_launch_stage \
  align.test_c1_closure.C1ClosureTests.test_single_attached_derivation_option_selects_same_manifest_for_pruning \
  align.test_c1_closure.C1ClosureTests.test_c2a_finalizer_cannot_pin_a_stray_present_at_finalization \
  align.test_c1_closure.C1ClosureTests.test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_next_arm_packet.C1PacketRebuildTests
(cd tests/align/c1_closure_lite && shasum -a 256 -c SUITE.sha256)
PYTHONPATH=tests:. python3.13 -B tests/align/c1_closure_lite/suite/run.py \
  --adapter "$PWD/tests/align/c1_closure_lite/adapter.py" > .row23-seat/r9-audit2-observed.jsonl
cmp tests/align/c1_closure_lite/suite/expected.jsonl .row23-seat/r9-audit2-observed.jsonl
git diff --check b2e01464d HEAD
```

The preceding canonical run finished with only the B6 executing-review
gate failing. It identified `3ae356e818e1b8bd9cec88597f9ba36d62bddd1a`,
`949298c7c1eb52f10223b6d7fe2237e30bf2d590` and
`e6da6a0be00aec2fc7ad44948e8d925252defd26` for authorized review.
The PR evidence ledger and seat handoff record the final published tree
and exact-head checks. Integration-owner and Opus acceptance, W1 signing
and the post-close packet stay with their assigned owners.
`NEEDS_SPEC: none`.

## Round 11 · SPEC-LITE round 4, one validator and a closed environment

Audit 3 of `40b8a66a623cedf72abd4050054c0332280a1662` verified two HIGH
cases. Preflight admitted a reservation plan digest computed without the
plan's trailing newline, and it judged a stale `XDG_CACHE_HOME` instead of
the cache the chain exports. An independent Gemini audit of the same head
added two more of that kind. Gemini 6.1 found the same precedence inversion
and no `unset` when `cache_home` is absent. Gemini 6.2 found that
`JOULEWISE_G2A_PRE_BRACKET_PLAN` was checked only if present at preflight
and then read by `joulewise/controller.py:335` from the launch environment.
The lead issued A3 (one validator), A4 (CI 21/21) and A5 (closed
environment). The GPT Sol builder stopped mid-round; this round continued
from its uncommitted regressions in the original worktree.

| Finding | Regression | Fix |
| --- | --- | --- |
| Audit 3 #1: plan digest of non-exact bytes | `test_reservation_plan_digest_covers_the_trailing_newline` | `765c4a126` calls the reservation's own `verify_frozen_plan` |
| Audit 3 #2: stale `XDG_CACHE_HOME` judged | `test_shade_uses_the_rendered_cache_instead_of_stale_xdg_cache_home` | `765c4a126` runs the SHADE task's resolver under the exported cache |
| Gemini 6.1(1): ambient value outranks `cache_home` | `test_gemini_6_1_shade_check_uses_the_rendered_cache_home` | `765c4a126` |
| Gemini 6.1(2): no `unset` without `cache_home` | `test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses` | `765c4a126` |
| Gemini 6.2: G2-a plan reaches the controller | `test_gemini_6_2_g2a_pre_bracket_plan_never_reaches_a_consumer` | `765c4a126` |

The regressions were committed first in `bf3187d27`, with the adapter
changes below. On that commit's unchanged production code, audit 3 #1 and
#2 admit with one host checkpoint per route where each must refuse.
Gemini 6.1(2) refuses only for the stale chain, not for the missing cache
binding. Gemini 6.1(1), 6.2 and the closed-environment class error because
the functions they observe do not exist yet. One-site mutants of
`765c4a126` therefore show that those tests catch the defect. At
`765c4a126`, tree `cfc1d5cc5a728e49889b1a56c217c5db53b60ea7`, all five pass.

| One-site mutant of `765c4a126` | Tests that fail |
| --- | --- |
| `apply_c1_environment` lets the caller's value outrank the rendered one | Gemini 6.1(1) and audit 3 #2, each admitting with one host checkpoint per route |
| The block omits `unset -m 'JOULEWISE_*' 'PYTHON*'` | Gemini 6.2 and the A5 sweep (a stale `PYTHONHOME` reaches the consumer interpreter) |

### A5 · the closed C1 environment

The renderer emits one block right after the `NIGHT_DIR` requirement,
before any stage. It runs `unset -m 'JOULEWISE_*' 'PYTHON*'` and unsets
the listed names. Then it exports `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN`
as the reservation's parser selected them, along with
`JOULEWISE_C1_INPUTS`, `JOULEWISE_NIGHT_PLAN_ID` (the night plan ID) and
`XDG_CACHE_HOME` from `cache_home`. Without `cache_home`, `XDG_CACHE_HOME`
stays unset. `NIGHT_DIR` is the driver's output directory and the only
launch variable kept. One function, `chain.c1_chain_environment`, produces
the mapping for both the renderer and preflight.

`test_closed_environment_covers_every_consumer_read` derives the reads from
code. It starts from the programs that the rendered chain runs and the
chain's inline helpers, then follows every import, including
function-level ones and `module:callable` factory strings. In that closure
it parses every `os.environ`/`os.getenv` read and resolves constant
names. It found 40 variables read across 252 modules, and each is exported,
unset, or matched by a pattern. The only reads with computed names are
`joulewise/arm_readiness_evidence.py`, an arm-time evidence writer, and an
endpoint credential that no module or config names. The test lists both, so
any new computed read fails CI. The chain's own unassigned shell reads are
`NIGHT_DIR` and the two inspection switches, which it refuses before the block.

`test_ambient_stale_values_never_change_what_is_consumed` sets a stale
launch value for each of 47 variables: the code-derived reads, the
exported names, an unlisted `JOULEWISE_` switch and six interpreter
switches. For each one it runs the exact rendered block under `/bin/zsh -f`.
A fresh interpreter then reports, through the consumers' own code, the
environment, the interpreter flags, the SHADE cache that `PinnedUpstream`
selects, the C1 input context and the controller's G2-a plan. Every report
equals the clean report. The same variable is then set in the preflight
process. The environment that preflight judges and the inputs it selects
stay identical. A stale `CALIBRATION_LEDGER` naming another file refuses
(`outside R/S`, see O2a below).

### A3 · the consumers' own pre-host checks

Preflight now runs each consumer check below by calling the consumer's own
function. It runs them under the rendered environment, with the working
directory set to the launch view as the chain's `cd "$REPO"` does.

| Consumer | Checks called at preflight | Checks after launch |
| --- | --- | --- |
| Reservation | Parser (A1), `--execute` required, `runtime_ledger(..., starting=True)`, `CustodyDeadline`, `verify_frozen_plan` (moved unchanged from `main`), `reservation_inputs` (declared slots and `validate_bracket_session_reservation_inputs`, with a stand-in for each host-measured identity field) | HAZARD measured identity vectors, readiness under the writer lease |
| Capture writer | Parser (A1), `runtime_ledger`, `_capture_fixture_error`, `CustodyDeadline`, `_capture_mode_refusal` (bracket arguments, replay conflicts, frozen protocol), `_live_capture_refusal` (`--allow-live`, power policy, test-only bounds) | Launch-lineage authentication, reserved-session snapshot, `sysctl` identity and acceptance screen |
| Campaign runner (protected, unchanged) | Parser (A1), unsupported modes including `--shakedown-gate`, `_require_external_campaign_log`, `load_campaign_policy`, `load_neg8_drift_bound_artifact` for a non-generated bound, `load_analysis_manifest` and its validity, `resolve_prospective_analysis_manifest_v3`, order loading and selection, `config_warning_gate`, `read_config_infos`, `load_waivers`, `duplicate_run_id_error` | Writer launch authentication and block limit. The failure limit is the renderer's literal. |
| SHADE task | `pilot.offline_shade_task(**task_kwargs).upstream.prepare()`, the R/S fence and export manifest in its C1 branch | None |
| Derivation, verdict and session status | Parsers (A1), derivation manifest descriptors | Same-attempt products only |

The extraction keeps `main`'s refusal order and codes. The census moves
the reservation's two plan rows to `verify_frozen_plan`.
`test_listed_consumer_checks_refuse_digests_of_non_exact_bytes` feeds 14
near-miss digests to the reservation plan gate, the starting-ledger gate,
the SHADE export manifest and the staged config descriptors. The variants
are a stripped or added newline, CRLF and canonical re-serialization. All
14 refuse. The stale-variable half of that sweep is the A5 sweep, because
every listed check runs inside the one closed environment.

Calling the consumers' own gates exposed gaps in the invented adapter
template, which is not part of the frozen suite. Its capture template
carried only `--slot`, so the real writer refuses it with
`calibration_writer_bracket_arguments`. Its placeholder campaign policy
fails the runner's policy loader. Its invented spare config fails the
runner's config gate. The adapter now completes the capture template as
`configs/campaigns/align_v4/plan_tree.json` does. It uses the committed
default policy and derives the spare from a valid dispatched config. The
nine frozen files and their manifest are unchanged.

### O2a and the caller's ledger pointer

Frozen row `outside-env-ledger/normal` requires a refusal when the install
or arm shell carries a `CALIBRATION_LEDGER` that names another file. The
chain never consumes that value. Preflight keeps one refusal-only O2a
check: a caller's ledger pointer must locate inside the view and resolve to
the canonical ledger. It never selects or admits a value. Every other
caller variable is ignored.

### Executing-review fix round

The Opus 5.5 executing review of `765c4a126` found no HIGH and one MED.
Preflight still skipped four consumer refusals that the consumers apply to
their prepared arguments before host work:

- the reservation's session and slot validator, which refuses a custody
  locator outside `<runs_root>/instrument_validation`;
- the reservation's `--execute`, without which it exits 0 without
  reserving and the capture then finds no session;
- the capture writer's custody deadline;
- the runner's `--shakedown-gate`, which needs the `--backup` that C1
  refuses.

`6355ffda5` moves the reservation's slot construction and validation into
`reservation_inputs`, which `main` and preflight share. Identity fields
measured on the host at launch get a stand-in, so the validator judges
every prepared input. Preflight now requires `--execute`, constructs each
writer's `CustodyDeadline` from the rendered arguments and refuses a
shakedown gate. The adapter places the calibration directories under the
claim runs root, as `joulewise/b5/plan.py:913` does, and passes `--execute`
as the committed reservation templates do.
`test_opus_med_1_consumer_input_gates_refuse_before_host` covers each case.
The builder exits 2 with that consumer's own refusal. On `90ee255f9`'s
production code, all four cases build with exit 0. At `6355ffda5`, the
five named regressions, this one, the duplicate-option sweep (now 137
cases across 11 command variants, because the completed templates carry
more options), the spare dispatch case and the four closed-environment
tests pass: 12 tests. The census moves the
two plan refusals from `BASELINE` into `NUMBER_INTEGRITY` (`90ee255f9`),
because the census freezes `BASELINE` rows at their original site.

### Frozen suite

The nine frozen files and `SUITE.sha256` are byte-identical to the
supplied freeze (manifest SHA-256 `20b8dbc7…`). The adapter matched the
tape **94/94** byte for byte at `765c4a126` and again at `6355ffda5`, after
the adapter gained the calibration-directory bindings and `--execute`.

### A4 · executing reviews and the review ledger

Shard 12's `test_review_rows_are_append_only_and_load_in_the_code_check`
requires a row in `configs/b6/executing_reviews.json` for every commit that
touches a registered number-bearing path or the F8 list. Five commits
touch one: `3ae356e81`, `949298c7c`, `e6da6a0be`, `88139ebff`
(`joulewise/b5/chain.py`, and in `3ae356e81` also
`joulewise/calibration_ledger.py` and `scripts/run_campaign.py`), and
`765c4a126` (`joulewise/b5/chain.py`). The later commits `90ee255f9`,
`6355ffda5` and `e005aee26` touch none.

Gate policy rule 3 asks for two executing reviews from different model
families, launched together. The Sol 6.1 seat ran through
`scripts/codex-bridge new` at xhigh. Its command sandbox could not
initialize on this machine (`sandbox_apply: Operation not permitted`,
exit 71), so it ran no command and returned `NEEDS_RULING`. Approval and
sandbox bypasses are forbidden. Under rule 3 a Fable seat replaces an
unavailable one, so both seats were Anthropic models.

| Seat | Commits | Verdict | Paper (SHA-256) |
| --- | --- | --- | --- |
| Opus 5.5, cold session; not the builder session | All five; fix-round delta `765c4a126..6355ffda5` | ADMIT-WITH-FIXES; delta ADMIT-WITH-FIXES | `docs/align/reviews/2026-11-22-c1-r11-opus-executing-review.md` (`f4503b6f…`) |
| Fable 5.2, replacing Sol | All five | ADMIT-WITH-FIXES | `docs/align/reviews/2026-11-22-c1-r11-fable-executing-review.md` (`b8c0620b…`) |

Neither seat found a HIGH. Both found the non-C1 render byte-identical
to the base (90/90 and 60/60 renders). Both found `run_campaign.py` equal
to the base blob from `949298c7c` onward. Their MED-1 and F1 are the same
gap, repaired in `6355ffda5` and confirmed by both. The Opus seat shares a
model with the builder of `765c4a126` but not a session; the papers record
this. The five rows cite both papers. The shard 12 test body passes
against them locally. The full module imports a fixture that reads the
operator archive, so it was not run here.

### Open after this round

- **Structural rule needed (gate policy rule 4).** The Opus delta's
  D-MED-1 and Fable's F2 are a second appearance of one class: preflight
  admits a prepared value that a later consumer refuses before host
  measurement. In D-MED-1, a capture's `--power-policy` or
  `--sampler-binary` disagrees with what the reservation records. In F2,
  a stale `--head-pin` fails the reservation's lease-held readiness. Both
  fail closed (MED). Rule 4 hands this class to the lead.
- **A5 and frozen row `outside-env-ledger/normal`.** Preflight keeps one
  refusal-only check on a caller's `CALIBRATION_LEDGER`, because the frozen
  row requires that refusal. A5 says preflight never validates the caller's
  ambient environment. Both seats flagged this. The lead should reconcile
  the two.
- Follow-ups, all LOW:
  - The non-C1 ledger readers react to a stale `JOULEWISE_C1_INPUTS`.
  - The A2 duplicate guard depends on argparse's private return shape
    (3.11/3.12 untested).
  - Indirect environment reads (`HOME`, `TMPDIR`, `PATH`, `GIT_*`,
    third-party libraries) are outside the code-read inventory.
    `JOULEWISE_CUSTODY_PARENT` is now unset for C1 campaign registry
    publication; no repository code sets it.
  - Three `calibration_ledger.py` C1 hooks and three C1 render branches
    have no killing repository test.
  - Unsupported campaign modes `--max-blocks` and `--dry-run`, and the
    capture's test-only flags, are still admitted.

## Round 12 · consumer agreement and the caller ledger rule

The lead resolved both open items of round 11. Item 1 requires preflight to
refuse every consumer refusal decidable from prepared inputs, including
agreements between consumers, with capture identity and the ledger head pin
named. Item 2 keeps `CALIBRATION_LEDGER` as a refusal-only check at entry.
Under PIPELINE §3, spec v(n+1) was committed first at
`7f2155750528ce6e0469ec226857356a8aa1a22b`. On the unchanged production
code its six negative cases admitted, each with one host checkpoint per
route: policy pre and post, sampler pre and post, the rolled-back pin, and
an empty `CALIBRATION_LEDGER`. Every control passed.

| Ruling clause | Commit | Named regression | Result |
| --- | --- | --- | --- |
| Each capture's `--power-policy` equals the reserved policy (pre and post mutated independently; desk-epoch precedence control) | `3daea0447` | `test_r11_capture_power_policy_must_equal_the_reserved_policy` | PASS |
| `--sampler-binary` selects the reserved sampler; an executable on the host and an absent path both refuse unopened; omitted default and `/usr/bin/../bin/powermetrics` pass | `3daea0447` | `test_r11_capture_sampler_must_be_the_reserved_sampler` | PASS |
| The sole in-tree pin `configs/calibration/retired-head.json` (sequence 7) refuses `calibration_ledger_rollback`; the same tree with the default pin passes | `bc224942e`, `3daea0447` | `test_r11_sole_rollback_head_pin_refuses_before_host` | PASS |
| `CALIBRATION_LEDGER` unset, canonical or launch-view alias passes. Empty, missing and outside refuse; outside refuses unread at mode `000`. The alias passes on both routes. | `3daea0447` | `test_r11_caller_ledger_pointer_is_refusal_only` | PASS |
| Same-byte copy refuses | existing | `test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage` | PASS |

Each negative case asserts builder exit 2. It also asserts install exit 2
with `packet_kit_mismatch`, a direct-arm refusal, zero host-checkpoint
entries on both routes, an unchanged starting ledger, and no file beside
it.

- **Capture identity.** The reservation now exposes `reserved_power_policy`
  (desk epoch, then desk T1, then `POWER_POLICY`) and `reserved_sampler`,
  and its HAZARD identity uses both. Preflight reads the desk files with the
  reservation's own `_hazard_desk_object`. For each capture it calls
  `validate_powermetrics_fiducial.reserved_identity_refusal`, which compares
  the policy and the `realpath` of the sampler without opening either
  file. Host-measured fields keep their live checks.
- **Head pin.** The reservation's pre-reserve decision (readiness, the
  strict refusal and the resumable-session route) moved unchanged from
  `main` into `pre_reserve_readiness`. `main` calls it under its lease.
  Preflight calls it on the parsed `--ledger` and `--head-pin` with the
  HAZARD arguments, `enforcing_under_lease=False` and
  `probe_live_writer=False`. The readiness live-writer probe acquires a
  lease and creates `<ledger>.lock` in S. `bc224942e` therefore adds
  `calibration_readiness(probe_live_writer=True)`, which only that
  read-only call turns off. That one-parameter change is the round's only
  number-bearing commit (F8 list).
- **Caller ledger.** An empty `CALIBRATION_LEDGER` now refuses. A set value
  resolves through the fence and `check_ledger` as before. The fence
  rejects an outside path before reading it, and the path comparison
  rejects a same-byte copy before reading it. Preflight and the chain
  still use the ledger exported from the packet.
- **Census.** The three readiness refusals moved from `main` to
  `pre_reserve_readiness` and were reviewed out of `BASELINE`.

### Round 12 executing reviews and their fix

Two executing reviews ran together on `c5b8b8047..3daea0447`: Opus 5.5
(cold) and Fable 5.2 in the Sol seat, whose sandbox still cannot
initialize here. Both returned ADMIT-WITH-FIXES with no HIGH. Both
confirmed that `bc224942e` leaves the default and every existing caller
unchanged. The read-only pre-reserve decision matched the lease-held one
on every synthetic state (Opus 28 cases, Fable 52). Fable F1 and Opus MED-2
showed that a capture or campaign stage could still pick its own
`--head-pin`, and a capture its own session, attempt or custody locator,
all admitted although the capture refuses them before any hardware
capture. Opus MED-1 showed that on the reservation's resumable-session
route, `calibration_session_status` still probed with a lease. It left
`<ledger>.lock` in S, so install and arm refused.

Each finding became an acceptance case before its fix: `48b50958c` and
`ddd369dc6`. On `3daea0447` the negative cases admitted, the resumable
case was refused at install over the lock file, and the controls passed.

| Finding | Commit | Named regression | Result |
| --- | --- | --- | --- |
| Fable F1 / Opus MED-2: a later consumer's own `--head-pin` | `062698aff` | `test_r11_every_consumer_reads_the_reserved_head_pin` (pre, post, collection; explicit-default control) | PASS |
| Opus MED-2: capture session, attempt, custody locator | `062698aff` | `test_r11_capture_slot_binding_must_match_the_reservation` | PASS |
| Opus MED-1: lease on the resumable-session route | `fcfc0dee4`, `062698aff` | `test_r11_resumable_session_preflight_takes_no_lease` (admits; S unchanged) | PASS |
| Fable M7 / Opus LOW-2: desk policy precedence | test only | `ReservedIdentityTests.test_reserved_power_policy_precedence` | PASS |
| Fable M17: another staged file as `CALIBRATION_LEDGER` | test only | case in `test_r11_caller_ledger_pointer_is_refusal_only` | PASS |

`fcfc0dee4` adds the same `probe_live_writer=True` parameter to
`calibration_session_status`. It is the round's second number-bearing
commit. The capture's slot agreement is one shared function,
`reserved_slot_refusal`, fed with the reservation's own validated slot
from `reservation_inputs`. The capture computes its custody locator with
`bracket_custody_locator`, now also used by its `main`.
Open LOW test gaps: no C1 control for a lagging pin that HAZARD accepts;
strict versus non-strict at preflight is untested; and no ledger test
fixes either probe parameter's default.

Both seats then checked the fix diff `3daea0447..062698aff` (rule 4), and
both returned **ADMIT** with nothing above LOW. Opus reran its 28
comparisons with no directory change. Fable compared the resumable route
6/6 and found the capture locator unchanged for 10/10 spellings. Each
seat's mutants of the fixes were killed, except two LOW test gaps: the
attempt-id comparison is masked by the locator check in every named
case, and `calibration_session_status`'s new default has no pinning test.
The papers are `docs/align/reviews/2026-11-22-c1-r12-opus-executing-review.md`
(`509fbffd…`) and `docs/align/reviews/2026-11-22-c1-r12-fable-executing-review.md`
(`da6a1502…`). The two number-bearing commits, `bc224942e` and `fcfc0dee4`,
each have a row in `configs/b6/executing_reviews.json` that cites both
papers. The shard 12 test body passes against them locally.

Local checks, within the lead's test budget, at `062698aff`:
- 17 tests pass: the nine `test_r11_*` acceptance cases, the same-byte,
  MED-1, precedence and three named round-11 regressions, and the four
  closed-environment tests (40 variables across 252 modules, the
  47-variable sweep, 14/14 near-miss digests).
- The census scan is clean.
- `tests.test_calibration_ledger`, `test_validate_powermetrics_fiducial`,
  `test_capture_t0_step`, `test_epoch_continuation_stale_pin`,
  `test_calibration_live_three_window`, `test_host_command_sites` and
  `test_r1_runtime_e2e` pass.

Under this machine's load, the time-scaled synthetic captures in
`tests.test_reserve_calibration_hazard` and the p2_vpf module reported
`detection_nonconvergent`, and a 3 s custody wall-clock assertion
overran. In those runs the reservation succeeded and the capture claimed
its slot. Hosted CI runs both modules. On `3daea0447` it ran them along
with the 94-case frozen replay (`test_frozen_lite_decisions`) and passed
every shard except shard 12, which lacked the pending row.

Open, all LOW:
- No C1 control for a lagging pin that HAZARD accepts.
- No test pins either `probe_live_writer` default.
- The attempt-id comparison is masked by the locator check in every
  named case.
- The head-pin agreement compares files, so a byte-identical pin copy at
  another path is refused. That fails closed and matches the rule.

## Round 13 · audit 4, the reserved window and the swept arguments

Audit 4 checked head `a624b3533` and found two items admitted before host
entry. In H1, changing only the reservation's `--window-id` to `C2` let build,
install and arm admit, and the writer appended `window_id=C2` beside
`plan_id=align-v4-c1`. In M1, `--max-blocks 0` let both routes admit, and the
campaign then exited 2 before its first member. Under PIPELINE §3 the cases
were committed first, as spec
`1b2eb2c85dae2f42a9166f33637ae833d42b8158`. The production code at
`a624b3533` gave these results:
- The `C2` window was admitted, with one host checkpoint per route, and the
  writer replay exited 0.
- `--max-blocks 0` was admitted.
- Eight of the nine sweep arguments were admitted.
- The other plan ID already refused (`calibration_plan_hash_mismatch`).
- The shifted runs root already refused, but only through custody
  containment.

| Finding | Commit | Named regression | Result |
| --- | --- | --- | --- |
| H1: `--window-id C2` with `plan_id=align-v4-c1` (the audit's reproduction), on both routes and in the writer itself; another plan ID | `5e1bac541` | `test_audit4_h1_reservation_window_is_the_frozen_c1_window` | PASS |
| M1: `--max-blocks 0`, with the campaign's own message | `5e1bac541` | `test_audit4_m1_max_blocks_below_one_refuses_before_host` | PASS |
| Sweep: nine rendered arguments a consumer rejects or that disagree with the plan; a matched-policy control | `5e1bac541` | `test_r13_arguments_a_consumer_rejects_or_that_disagree_with_the_plan` | PASS |
| Sweep: a tree window identity naming another window or evidence root; a matching control | `5e1bac541`, `4f5f1fda6` | `test_r13_reservation_matches_the_frozen_window_identity` (spec `7de9fe499`) | PASS |

Each H1, M1 and identity negative case asserts builder exit 2. It also
asserts install exit 2 with `packet_kit_mismatch`, a direct-arm refusal, zero
host-checkpoint entries on both routes and an unchanged starting ledger. The
sweep cases assert builder exit 2 with the named detail. Both identity
negatives admitted on the `a624b3533` preflight, each with one host
checkpoint per route.

- **H1.** Preflight's reservation branch now requires all of the following:
  - `--window-id C1`;
  - a frozen plan whose `window_id` is `C1`;
  - a tree `window_identity.window_id` that, if present, is `C1`;
  - an `--evidence-root-id` equal to the identity's;
  - a `--runs-root` that is the window's claim runs root.

  `verify_frozen_plan` takes the window. When the plan declares a
  `window_id`, the writer's `main` refuses any other `--window-id` with
  `calibration_reservation_input_invalid` (`plan_window_mismatch`) before it
  appends, and preflight calls the same gate. The writer case replays
  `reservation.main` on the rendered argv in the closed environment, with
  only the host identity measurement stubbed. It exits 2, and the ledger is
  unchanged. `consumer_check` now appends a refusal's context reason to its
  message.
- **M1.** For a value below 1, preflight calls the runner's own
  `campaign_block_limit`, so the message is `--max-blocks must be >= 1`. Any
  other block limit also refuses. A C1 launch authorization has purpose
  HAZARD_PACK, and before the first member the runner refuses any block
  limit that lacks G2B_SHAKEDOWN authorization.
- **Census.** There is one new `verify_frozen_plan` row
  (`NUMBER_INTEGRITY`), and the scan is clean.

The sweep compared every reservation, capture and campaign option that the
rendered C1 chain can carry with the checks in each consumer's `main`.
Preflight now refuses each of these:
- a reservation runs root other than the claim runs root;
- a reservation evidence root or tree window identity that disagrees;
- a capture with `--derivation-only`;
- a capture with any of the seven test-only options;
- a capture `--pulse-count` other than the frozen protocol's 59;
- capture sampler-ready or rollover timeouts that are not finite and
  positive;
- a campaign `--dry-run`;
- any campaign `--max-blocks`;
- a campaign `--instrument-power-policy` other than the reserved policy. On
  HAZARD the controller only flags a policy label mismatch, so without this
  check the campaign would run against a policy the reservation didn't
  record.

Swept and not in the class:
- **Capture `--arm-countdown-s` and `--sleep-display-before-capture`.** The
  renderer owns both. A template that carries either refuses at render, and
  the renderer appends 0 for pre and 20 for post.
- **Campaign `--max-failures`.** The renderer always sets it to the stage's
  `expected_count`. Staging ties that count to the dispatched order, which
  has 11 members for the kit's first collection stage. The runner's `< 1`
  refusal would need an empty frozen order, and install already refuses a
  changed kit as `packet_kit_mismatch`.
- **Campaign `--arm-countdown-s` below 0.** The runner's own `parse_args`
  refuses it, and preflight runs that parse.
- **Campaign `--environment-override`.** On HAZARD an environment-preflight
  error becomes a flag record, override included. Its hashes bind the live
  snapshot.
- **Capture `--display-arm-binary`.** On HAZARD a display-arm failure is a
  flag.
- **Capture `--output-root` basename.** The capture checks it only under
  launch lineage, which the committed acceptance config does not require.
  The custody locator agreement already binds the output root and attempt
  to the reserved slot.
- **Reservation.** Every check in `main` already runs at preflight: frozen
  plan, inputs, pre-reserve readiness, custody deadline and ledger. The
  session kind, the uncommitted-pin and crash-authorization test options,
  and `--verify-only` already refuse.
- **Campaign derivation route.** It reads no other argument.

No commit this round changes a number-bearing path, so the round adds no
review row. Local checks, within the lead's test budget:
- 22 tests pass. These are the four round-13 tests, the round-12 acceptance
  cases, the earlier named regressions, the closed-environment class and the
  137-case duplicate-option sweep.
- At `5e1bac541`, `tests.align.test_v4_next_arm_packet` (69),
  `test_v4_series_e2e` (11), `tests.test_bracket_binding_cli` (19) and
  `tests.test_calibration_ledger` (95, one skipped) pass. The only later
  production change is the refusal message.
- The census scan is clean.
- The nine frozen files match `SUITE.sha256` and are unchanged since
  `a624b3533`.

Hosted CI runs the 94-case frozen replay (`test_frozen_lite_decisions`)
and the full suites.

Open, all LOW:
- Two of the seven test-only capture options and one of the four timeout
  forms are exercised.
- The writer's window assertion needs a plan that declares `window_id`.
  The C1 kit plan declares `C1`.

## Round 14 · audit 5, every stage write bound to this attempt

Audit 5 checked head `3ea3de760` and verified one HIGH and one MED, both
admitted before host entry:
- **HIGH.** Adding `--log <previous-attempt>/campaign_log.jsonl` to the first
  collection stage let build, install and arm admit. The campaign then
  appended two provenance attestations to the previous attempt's log and
  never created the current one.
- **MED.** A stage whose other configs carry `launch_lineage_required`, with
  one config left without it, let both routes admit. The campaign then
  exited 2 with `launch_binding_mismatch` before measurement.

The cases were committed first, as spec
`7c70833b767ec5912745846a262805e2290369e3`. The unchanged preflight
admitted both stale-log spellings, with one host checkpoint per route,
and all six class cases. The control built.

| Finding | Commit | Named regression | Result |
| --- | --- | --- | --- |
| HIGH: a previous attempt's `--log`, given as an absolute path (the audit's reproduction) and relative to the launch view. Both routes refuse, the previous log is unchanged and no current log is created. | `766fadf2c` | `test_audit5_high_stale_campaign_log_refuses_before_host` | PASS |
| Class: the log in the other runs root, under another name, or a previous attempt's on the second stage; the bound written into a previous attempt or the claim runs root; a capture output root below `instrument_validation` with an agreeing reservation. Controls: an explicit current log, and the bound name pinned to the harvest's. | `766fadf2c` | `test_r14_every_stage_writes_only_where_this_attempt_is_read` | PASS |

- **Root cause.** Preflight bound each stage's inputs, its runs root and
  the ledger, but no other write location. The class is every path a C1
  stage writes. I listed these from the three consumers:
  - **Reservation.** The ledger (already canonical) and the runs root,
    which is also its flag root.
  - **Capture.** The ledger (already canonical) and the output root. The
    output root holds the custody directory, and its parent is the flag
    root. `--output` already refuses.
  - **Campaign.** The runs directory, which also holds its lock, its
    provenance and its flag root; the log, with its torn-tail sidecar
    beside it; and the derivation's bound output. `--backup`,
    `--whole-window-verdict-output` and `--quarantine-path` need modes that
    C1 refuses.
- **Fix.** One helper, `this_attempt`, now requires each write location to
  be the current attempt's location that the harvest reads. The harvest
  reads `<runs>/campaign_log.jsonl` and
  `<bound_runs_root>/neg8-drift-bound.json`. Each path is compared as
  spelled from the launch view. The round-13 runs-root check and the
  campaign runs-dir check moved into the helper. With the output root
  fixed, the round-12 slot agreement then puts each capture's custody
  directory at its `<slot>_calibration_dir`.
- **Fixture.** The invented adapter wrote the derivation bound to a literal
  `work/derived.json`. It now writes `<bound_runs_root>/neg8-drift-bound.json`,
  where the harvest reads it. The nine frozen files are unchanged. A frozen
  decision records only outcomes, and every clean build passes the new
  checks.
- **Tests updated.** Round 12's slot-binding subcase for
  `--output-root other_validation` still refuses on both routes, but now at
  the earlier write-location check, so it expects that message. The
  round-13 runs-root sweep case expects the shared message.

**MED, not fixed (NEEDS_SPEC).** Outside `--dry-run`, the runner always
refuses a selection that mixes marker-bearing and legacy configs
(`authenticate_campaign_writer_preflight`). Preflight could call the
runner's own `_config_requires_launch_lineage` on each dispatched config.
The frozen suite's invented history, however, mixes them in its first
collection stage: 7 of 11 configs carry the tag, and the second stage
13 of 13. That check would therefore turn the 94 frozen decisions' clean
admits into refusals. The lead has two options:
- add the tag to the four legacy configs in the invented history, which
  changes a frozen file;
- accept the changed decisions.

Local checks, within the lead's test budget:
- 24 focused tests pass on the final code. They cover the two round-14
  tests, every round-13, round-12 and earlier named regression, the
  closed-environment class and the 137-case duplicate-option sweep.
- `tests.align.test_v4_next_arm_packet` (69) and `tests.align.test_v4_series_e2e` (11),
  the C1 packet modules most exposed to the new checks, pass.
- The census scan is clean.
- The nine frozen files match `SUITE.sha256`.

I started the 94-case frozen replay locally by mistake, alongside the
spec run, and stopped it before it finished. Hosted CI runs it.

Open, LOW: the derivation route reads no `--log`, so preflight does not
bind one on that stage.

## Round 15 · audit 6, the night plan's launch identity and fresh write roots

Audit 6 checked head `690295274` and verified two HIGHs and the open MED.
In both HIGHs, build and install exited 0, direct arm admitted, and each
route entered its host checkpoint once:
1. **Night-plan window.** Changing only the night plan's
   `hazard_window.pack.window_id` to `C2` made the production lineage
   publisher record `C2`, and both runs roots authenticated it.
2. **Linked default log.** A link at `claim_runs_root/campaign_log.jsonl`,
   pointing at a previous attempt's log and placed before finalization, made
   the campaign append two attestations to that log.
3. **MED.** The MED from round 14 (a missing `launch_lineage_required` tag)
   is unchanged.

The cases were committed first, as specs `4bc9e9bfb` and `ad50017c5`. On
the unchanged preflight every negative case was admitted, except one: the
chain comparison already refuses another window plan id. Both controls
passed.

| Finding | Commit | Named regression | Result |
| --- | --- | --- | --- |
| HIGH 1: night-plan pack `window_id` `C2` (the audit's reproduction), refused on both routes | `e1b42912c` | `test_audit6_high1_night_plan_window_is_the_reserved_window` | PASS |
| HIGH 1 class: pack plan id, pack id, evidence root, plan tree digest, bracket session, a previous attempt's claim runs root, attempt, window plan id, custody root, measurement root | `e1b42912c` | `test_r15_night_plan_launch_identity_and_locations_are_this_attempts` | PASS |
| HIGH 2: a link at the default campaign log, refused on both routes with the previous log unchanged | `e1b42912c` | `test_audit6_high2_linked_default_log_refuses_before_host` | PASS |
| HIGH 2 class: a hard-linked log, a linked claim runs root, a stale bound, a linked capture root. Control: both roots exist empty and both routes admit. | `e1b42912c` | `test_r15_runs_roots_are_fresh_before_arm` | PASS |
| HIGH 2 class: a linked custody night directory, a linked custody root, a linked operator log. Control: custody holding ordinary records builds. | `e1b42912c` | `test_r15_custody_and_operator_logs_hold_no_links` | PASS |

- **HIGH 1 root cause.** The driver publishes the window lineage from the
  night plan, and preflight checked only that plan's `pack_root`. A new
  check, `check_launch_records`, now binds every launch field the driver
  reads from the plan to the value `b5.plan` writes from this attempt's
  inputs:
  - the lineage identity, read through the driver's own `lineage_identity`.
    The window and pack plan id must match the rendered reservation, and
    so must the bracket session.
  - the pack's evidence root, pack id and plan tree digest;
  - the runs roots, matching the chain's bindings;
  - the attempt, window plan id and custody root, matching the prepared
    session inputs;
  - the measurement root, matching the launch view.
- **HIGH 2 root cause.** `b5.plan` refuses an existing runs root and
  creates both roots empty, because a window never reuses a runs root.
  Nothing re-checked that before arm, so any entry placed since took this
  attempt's writes. `check_fresh_runs_roots` now requires each runs root to
  be absent, or an empty directory that is not a link. That covers every
  write inside the roots: logs, bounds, capture outputs, flags, locks and
  bundles. The custody root holds the lineage and night records, and the
  operator log root holds the chain's logs. Both may already hold records,
  but `check_no_links` refuses a link at or below either one.
- **Order.** All three checks run after every earlier check, so each
  frozen refusal keeps its own reason. A frozen decision records only
  outcomes.
- **Fixture.** The invented adapter now writes the night-plan fields that
  `b5.plan` writes from the same inputs, and the session's `attempt` and
  `plan_id`. It also gains an `edit_night` hook. The nine frozen files are
  unchanged.
- **Test change.** The Gemini 6.2 test stubs `_check_consumers`, so it
  also stubs the new launch-record check.

**MED, still NEEDS_SPEC**, unchanged from round 14. The frozen suite's
invented first collection stage mixes tagged and untagged configs (7 of
11 carry the tag). A preflight marker check would therefore change the
frozen clean admits.

Local checks, within the lead's test budget:
- 29 focused tests pass on the final code. They cover the five round-15
  tests, every round-11 to round-14 regression, the closed-environment
  class and the 137-case duplicate-option sweep.
- `tests.align.test_v4_next_arm_packet` (69) and `tests.align.test_v4_series_e2e` (11),
  which build packets from production-shaped night plans and runs roots, pass at `e1b42912c`.
- The census scan is clean.
- The nine frozen files match `SUITE.sha256`.
- Hosted CI runs the 94-case replay.

A background module run overlapped a 25-second temporary stash of
`v4_registration.py`. I stopped that run and reran it on the committed
code.

Open, LOW:
- `hazard_window.pack.pack_sha256` is not bound. It is a git digest of the
  committed pack that preflight cannot recompute from the staged view, and
  the harvest recomputes pack identity.
- A link placed after arm is outside preflight's reach.
