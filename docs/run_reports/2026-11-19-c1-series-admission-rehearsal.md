# 2026-11-19 · Row 20 C1 series admission rehearsal

Tier 2 · pipeline · high · three-round cap. Branch `align/2026-11-19-c1-series-admission-rehearsal` targets `ops/2026-11-11-w1-presign` as a separate draft.

The rehearsal exercises the validator used at series prepare and rechecked before arm. The manifest comes from `series.candidate()`. Each test starts with its own temporary root and writes invented W1 collection bytes, the manifest and five distinct evidence files. The descriptors bind exact bytes and point to `/verdict/accepted`, whose value is lower-case `pass`. The receipt carries the real schema and a `SYNTHETIC-ONLY` signature string. The fixture exercises registration behavior only. Series clearance remains open. [Admission validator](../../scripts/align_v4_series.py#L247-L284) · [Session prepare](../../scripts/align_v4_session.py#L60-L69) · [Session recheck](../../scripts/align_v4_session.py#L1165-L1181)

## Freeze and results

| Stage | Commit | Tree | Result |
| --- | --- | --- | --- |
| W1 baseline | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` | `c904864e46879a4adfbdf0b467d4da1ee5928285` | Condition-13 synthetic contract 2/2. Hosted baseline CI 21/21 jobs, including all 12 ordinary shards and three exclusive jobs. |
| Executable spec freeze | `1c2eff89af809b51a062bfb760afd21396f5bb81` | `5b07c687877f602e3af0cfd803a66542663c9873` | 10 expected `synthetic admission fixture pending` setup failures, exit 1. The new class had no fixture yet. |
| Fixture build | `3df94d41cf8e1182996f1283b54379665d1ed500` | `61ca33894a65c6dde464fcf98dcde6940d66c86d` | 10/10 methods, 21 outcomes. The freeze-to-build diff is confined to fixture setup. |

| Frozen scenarios | Result |
| --- | --- |
| Intact C1 receipt | Admitted. |
| One descriptor omitted for each of `scorer_fit_contract`, `seed_allocation`, `r13_r14_gate`, `paired_build_agreement` and `w1_clearance` | Five refusals at missing descriptor validation. |
| One evidence file changed for each of those five descriptors | Five refusals at the named file's byte digest. The bytes still decode to the original values. |
| Existing `fail` leaf and broken pointer | `r13_r14_gate` stays pending for the `fail` leaf. The broken pointer fails at its missing leaf, where the resolver currently raises a lookup error. |
| W1 collection bytes drift and manifest bytes drift | Separate refusals at the W1 configuration and exact-byte admission checks. Both retain the original receipt and its digests. The in-memory manifest stays fixed. |
| Signature removed | Exact-byte lead admission refused. |
| One choice changed for each of `d_mapping`, `test_windows`, `test_shape` and `sentinel` | Four refusals at the explicit choice check. |
| Same receipt with only `w1_clearance` omitted | W1 admits with `post_w1=False`. C1 refuses with `post_w1=True`. The C1 refusal counts in the five omission cases above. |

### Local checks and hosted baseline query

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_registration.R1ExecutedSourceTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_series.PostW1SeriesAdmissionTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_registration.R1ExecutedSourceTests align.test_v4_series_delta5.SlotTests
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_series.PacketTests.test_w1_arm_requires_a_series_bound_packet align.test_v4_series.PacketTests.test_bound_evidence_cannot_change_or_be_forged_in_packet
git diff --check
git diff 1c2eff89a 3df94d41c -- tests/align/test_v4_series.py
gh run view 43712204542 -R mpmdw/JouleWise --json headSha,status,conclusion,jobs
```

The class ran at both freeze and build. The focused neighboring contracts passed 3/3 and 2/2. GitHub's canonical `ci` workflow provides the full sharded suite for this PR. Local test selection was limited to synthetic fixtures to keep operational inputs closed. [W1 baseline CI](https://github.com/mpmdw/JouleWise/actions/runs/43712204542) · [Pipeline at the cited main pin](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L36-L68)

## Review and handoff

| Round | Seat | Assessed commit and tree | VERIFIED HIGH | VERIFIED MED | VERIFIED LOW | Findings and root causes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Astra 6.2, high, `/root/astra_audit` | `3df94d41cf8e1182996f1283b54379665d1ed500` / `61ca33894a65c6dde464fcf98dcde6940d66c86d` | 0 | 0 | 0 | None. |

The read-only Astra seat ran the focused class (10/10) and checked the freeze-to-build diff. Its second synthetic run (`PYTHONPATH=tests:. python3.13 -B -`) observed 21 calls through the real validator: two admissions and 19 refusals. It confirmed the same receipt bytes for the W1/C1 comparison and distinct evidence files inside the temporary root. The lead retains the final-tree and integration decisions. No §3 return-to-spec criterion was met in round 1. NEEDS_SPEC is empty. The draft ledger and seat handoff carry final-head CI and the outstanding integration-owner and Opus acceptances. [Pipeline review and integration gates](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L36-L62)

## Unsigned fill map for the series owner

The code accepts four source descriptors for W1 and also requires `w1_clearance` for C1. A staged input can support a pre-W1 rehearsal. The lead records all five **real** passing descriptors, the exact commitments and the signature on the effective C1 receipt after W1 desk. Each descriptor carries an explicit source locator, SHA-256 of the byte-exact JSON source, and a JSON pointer to its `pass` leaf. An embedded `content_utf8` source carries those same bytes. The paths, hashes, pointers, decisions and signature for actual admission are all owed. [Receipt contract](../../scripts/align_v4_series.py#L247-L284) · [Series agreement A6](../align/v4/DCT-SERIES-AGREEMENT.md#L58)

| Required field | Producer | Immutable binding | Earliest fill |
| --- | --- | --- | --- |
| `schema` | Series owner using the pinned validator's schema constant | Literal `joulewise.align_v4.series_admission.v1` in the receipt | Unsigned drafting. |
| `manifest_sha256` | Series builder supplies the canonical manifest and the series owner verifies it | SHA-256 of the exact serialized manifest bytes, including the allocation and all four choice values | After canonical bytes are frozen. The paired checks must cover these bytes before signing. |
| `w1_collection_sha256` | W1 kit owner supplies the collection plan and the operator verifies the effective binding | SHA-256 of the exact W1 `collection_plan.json` bytes seen by admission | Once the staged collection bytes are fixed. The operator confirms the exact binding before C1 signature. |
| `choices.d_mapping` | Series owner records lead acceptance of P4 R15 | Exact manifest value `alias_calibration` | Draft from the frozen manifest. Lead confirms before signature. |
| `choices.test_windows` | Series owner records lead acceptance of P4 R15 and option B | Exact manifest value `3`. The manifest separately binds the blind reserves T4 and T5. | Draft from the frozen manifest. Lead confirms before signature. |
| `choices.test_shape` | Series owner records lead acceptance of P4 R15 and option B | Exact manifest string `v4: 14 benign + 2 sabotage; no v5 attacks or physical controls` | Draft from the frozen manifest. Lead confirms before signature. |
| `choices.sentinel` | Series owner records lead acceptance of P4 R15/R20 | Entire exact manifest object, including `source` (`W1:5`), `late_replay_of` (`5`), `extra_on_inconclusive` (`2`) and `escalated_ceiling_s` (`62400`) | Draft from the frozen manifest. Lead confirms the source and exact commitment at W1 desk before C1 signature. |
| `evidence.scorer_fit_contract` | Scorer/fit owner supplies the qualified contract and the research lead rules on scientific meaning | Exact passing source bytes and pointer for the frozen scorer, fit and release commitments relevant to the series. RL-182 §1.5 binds the additional C1 dependencies separately. | Once the exact applicable contract is accepted. Confirm the C1 binding before C1. |
| `evidence.seed_allocation` | Series owner and paired seed checkers | Exact passing allocation record and pointer covering the same manifest bytes, seed law, reserve pools and seeded placements | After the paired seed recomputation agrees on the final manifest. |
| `evidence.r13_r14_gate` | Research lead and scoring/statistics owner supply the prospective gate decision | Exact passing decision bytes and pointer for the frozen scorer, eligibility, exchangeability and window-dependence obligations | After the R13/R14 ruling covers the applicable frozen design. A yield count by itself cannot fill this field. |
| `evidence.paired_build_agreement` | Independent build/review seats supply agreement and the series owner records it | Exact passing agreement bytes and pointer for the reviewed manifest and applicable kit commitments | After the independent builds agree on the bytes for the effective tree. |
| `evidence.w1_clearance` | W1 desk and close owners (lead and magistrate) supply the adjudicated decision | Exact passing clearance bytes and pointer tied to the W1 collection commitment and its desk and close decision | After W1 desk and close, with any held reason or required ruling resolved. |
| `lead_signature` | Authorized series lead | Signature in the existing trusted-lead format on the receipt that records the exact bindings, choices and evidence | For C1, after W1 desk and closure of the evidence and rebind requirements. |

The gate record should preserve the distinction between the prospective scorer's validity conditions and the fixed-eight calibration count stop. The draft choices follow the frozen R15 series and option B. [P4 R13/R14](../align/pilot_protocol_v4.md#L581-L599) · [P4 fixed eight and R15](../align/pilot_protocol_v4.md#L984-L1008)

The lead and magistrate own recording the cohort identity and thermal policy, including the R1 sensor keys and heavy class and the pre-W1 commitments for quantization, `B_D`, `T_dead`, `max_tokens=4096` and `max_turns=12`. They own any evidence-bound D-17a selection between W1 and C1 within the permitted scope (D G0 cap, direction-conditional `δ_slow`, `G_turn`, `N_chunk`) and any resulting prospective rebind. A W1 D G1 timeout rate over 10% sends `G_turn` to the research lead before C1. Bind the selected effective policy and regenerated commitments through the authorized receipts and session preparation, preserving historical W1 bytes. From C1 onward, replacements use the frozen identity and policy. A later ladder step requires a new cohort, restarted calibration, disclosure without pooling and a re-derived U3 roster. No policy alternative is exercised or approved by the fixtures. [P4 RL-20](../align/pilot_protocol_v4.md#L501-L515) · [P4 D-17a](../align/pilot_protocol_v4.md#L715-L722) · [P4 series and U3 freeze](../align/pilot_protocol_v4.md#L1375-L1381) · [RLD timeout tripwire at `00a28dcf2`](https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L12359-L12364)

RL-182 §1.5 allows W1 signature on its own required scorer checks. C1 still needs the accepted reference-row builder, one named release script, the synthetic release test at 102 and 101 of 154, the authorized receipt binding `s_rows.py`, the script and both `rl176` modules, and the post-W1 first-token coverage count in §1.4(f). The lead owns that binding and disposition. The W1 desk, close and permitted policy selection remain owed by the lead and magistrate. Fable owns the named returns and any change in scientific meaning or protected rule. [RLD §1.4(f)–1.5 at `00a28dcf2`](https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19768-L19787) · [RLD ownership at `00a28dcf2`](https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20894-L20903)

## Condition-13 Git metadata

Ten of ten blob identities match the W1 baseline, with zero inherited absences. The lists come from `git ls-tree -r b2e01464d -- "${paths[@]}"` and `git ls-tree -r HEAD -- "${paths[@]}"`, where `paths` contains the ten paths below. `diff -u <(git ls-tree -r b2e01464d -- "${paths[@]}") <(git ls-tree -r HEAD -- "${paths[@]}")` exited 0. The check uses only tree metadata. [Ruled path set](../../joulewise/align/apple/v4_registration.py#L489-L496)

| Condition-13 path | Blob at W1 baseline and assessed build |
| --- | --- |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
