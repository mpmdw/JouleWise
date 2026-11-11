# Claim contract B: RL-22 fixes

2026-11-10. Sol seat `claim-b-rl22`, based on `79e85ccd9` on
`align/2026-11-10-claim-contract-opus`. Implementation commit: `41228e3e2`
(`align v4: apply RL-22 claim contract B fixes`). This report is a separate handoff commit.
Local branch: `claim-b-rl22`; no push or merge.

## Authority and intake

Applied the four required fixes and the RL-14 power correction in RL-22 from
`origin/audit/2026-11-10-fable` @ `5de56400f6d49a2a3a83aacc0ad174405391b8f0`,
`docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
Mission M0 intake found no active stop card and a clean workspace. The explicit RL-22
brief selected this bounded [AGENT] task ahead of the generated queue. Per the brief,
RUN_STATE, TASK_QUEUE, the state kernel and `tests/test_gen_state.py` were not edited;
no task was registered. No new research ruling or scope choice was made.

Access note: the initial `git show` read the required research-lead decisions document
in full; subsequent reads were narrowed to RL-14, RL-20 and RL-22. Required repository
intake summaries were also read. No real results artifact, measurement data, restricted
directory, night custody/archive or external data path was opened. No network, model
download, measurement pipeline, hardware probe or MLX runtime was used.

## Changes

| Requirement | Applied change / evidence |
|---|---|
| 1. Zero-capture hold count | `thermal()` skips C/T attempts with zero counted captures before updating either counter. Two new regression methods cover C and T FAIL → refusal → FAIL, signed release, and unchanged counts even when the refusal's thermal report says FAIL. The protocol's series-freeze paragraph and B6 explicitly say `(zero-capture attempts are skipped)`; the deviation summary agrees. |
| 2. Durable old-manifest witness | The authority-citation test always compares the current member/ordinal projection to a pinned old digest. Full old-object/byte comparison remains conditional on commit existence. A mocked-absent-commit regression verifies the test passes without `git show`, and still rejects changes to member rows and sabotage ordinals. The real retained object comparison also passed. |
| 3. B5 wording | The protocol now says `that pair's other seven fresh members are benign`, with fourteen benign and two sabotage-instructed fresh members per window. Manifest and placement law are unchanged. |
| 4. Deviation history / receipts | Restored the entire original `R25-U3-N` row from `cf501f75f` verbatim, followed by a supersession marker naming `RL16-U3-N24`. `B-ordinals` cites both 436-member MATCH receipts: `seedcheck-claim-b-opus/comparison.json` and `seedcheck-claim-b-sol/comparison.json`. |
| RL-14 correction | Protocol, agreement and Opus report now give joint-rule equivalence planning power .68 / .60 / .38 at 22 / 20 / 16 strata, and describe limited planning power. The existing protocol table (.682 / .599 / .382) already agreed with `claim-b-power.json`; it and the simulation receipt were preserved. Historical alternative-margin calculations are explicitly labeled design-interval-only. |

The two optional RL-22 notes were not implementation conditions and were left unchanged.

### Digest provenance

Source: `cf501f75fabf99173f278eccf66ac52b8eee1060`,
`configs/campaigns/align_v4/series/series_manifest.json`, raw sha256
`b5fedb49ee04e0b5388ea43a76b6fbf07cb94b896145476386271e702fb41c64`.
Computed once from that object during this run. The projection is the ordered list of
`{id, members, sabotage_ordinals}` for every window, with an absent `sabotage_ordinals`
represented as JSON null. Encoding: `json.dumps(..., sort_keys=True,
separators=(',', ':'), ensure_ascii=True).encode('utf-8')`, no trailing newline.

The 85,767-byte projection (20 windows, 436 members) has sha256
`437ef3972387b987ed9f9f52d367344b6b3508da80d5390b3fbd26ed880256e8`.
Current full manifest sha256 remains
`70009b6a594835643ef0bb2ff324ed700447cbe7a6237975ebdb209ec2c78dd6`.

## Failing-first evidence

Before changing production code, ran:

```text
python3.13 -B -m unittest tests.align.test_v4_claim_b_packet.ClaimBPacketTests.test_rl22_zero_capture_between_fail_bars_does_not_reset_hold_count tests.align.test_v4_claim_b_packet.ClaimBPacketTests.test_rl22_zero_capture_attempt_neither_increments_nor_resets_fail_count
```

Result: 2 tests in 14.755 s, **FAILED (failures=4)**. The C and T subcases
incorrectly returned thermal `pass` after FAIL → refusal → FAIL, with two total bars
but only one consecutive bar. Both zero-capture report-status subcases returned
counts `(1, 0)` instead of `(1, 1)`. After the skip was applied, the full packet module
passed all 15 tests, including ruling/rebuild/admission checks.

## Verification

Each module below ran separately as `python3.13 -B -m unittest <module>`, sequentially.
All 190 tests passed, with no skips reported. Passing runs took about 413 s; including
the red baseline, total test execution was about 428 s (7.1 min), below the brief's limit.

| Module | Tests | Result |
|---|---:|---|
| `tests.align.test_v4_claim_b_packet` | 15 | OK |
| `tests.align.test_v4_seedcheck_claim_b` | 9 | OK |
| `tests.align.test_protocol_v4_doc` | 6 | OK |
| `tests.align.test_v4_next_arm_packet` | 45 | OK |
| `tests.align.test_v4_next_arm_packet_opus_witnesses` | 5 | OK |
| `tests.align.test_v4_executed_closure` | 4 | OK |
| `tests.align.test_measurement_view_identity` | 3 | OK |
| `tests.align.test_v4_claim_b_u3` | 4 | OK |
| `tests.align.test_v4_w1_blockers` | 17 | OK |
| `tests.align.test_v4_test_reserves` | 2 | OK |
| `tests.align.test_v4_replacement_windows` | 20 | OK |
| `tests.align.test_v4_cadence` | 30 | OK |
| `tests.align.test_v4_receipt_tiers` | 8 | OK |
| `tests.align.test_v4_registration` | 22 | OK |

Also passed:

- `python3.13 -B -m compileall -q scripts/align_v4_next_arm_packet.py tests/align/test_v4_claim_b_packet.py tests/align/test_v4_seedcheck_claim_b.py`.
- `git diff --check`.
- A read-only stdlib audit asserting exact original R25-row preservation after removing
  the appended supersession marker; both receipt digests/member counts; unchanged manifest;
  required B5/freeze wording; receipt/table power agreement; and untouched coordination files.
  Its first draft matched roster row 22 instead of power row 22 and raised a parsing
  `ValueError`; narrowing the audit to the power section passed without a product change.
- Targeted power-text review of the claim-contract documents. No power simulation was
  rerun: the retained receipt already contains the corrected joint-rule calculation.

The full suite was intentionally not run, per the brief and the active blinded job.
All runtime evidence above is synthetic. No hardware validation is claimed.

## Files and handoff

Changed:

- `scripts/align_v4_next_arm_packet.py`
- `tests/align/test_v4_claim_b_packet.py`
- `tests/align/test_v4_seedcheck_claim_b.py`
- `docs/align/pilot_protocol_v4.md`
- `docs/align/v4/DEVIATIONS.md`
- `docs/align/v4/CLAIM-CONTRACT-B-AGREEMENT.md`
- `docs/align/v4/CLAIM-CONTRACT-B-opus-report.md`
- `docs/align/v4/CLAIM-CONTRACT-B-rl22-report.md`

No open implementation question or unresolved test failure. Commit absence was simulated
in the regression; no actual shallow/pruned clone was constructed. The delta changes no
MLX code, so it adds no native MLX test requirement. Existing native and round-2 gates
remain lead-owned and are not satisfied by these fixtures.

Next exact step: give `claim-b-rl22` and implementation commit `41228e3e2` to the research
lead or a Fable reviewer for RL-22's required delta check before merge onto the W1 line.
No W1 registration, U3 signature, C1 admission or independent reviewer approval is claimed.
