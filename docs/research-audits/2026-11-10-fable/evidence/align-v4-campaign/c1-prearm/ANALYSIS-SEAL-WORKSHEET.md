# Pre-C1 analysis seal worksheet

**DRAFT / INELIGIBLE · Row 14 · Tier 0.** This worksheet tracks evidence owed
before C1. Even when filled, it has no signing, arm, or release authority. The
lead and analysis owner privately verify the actual single committed
analysis-seal file before the first C1. Use only owner-approved public-safe
references in this handoff. Round 2 and the seal gate C1. W1 has its own
registration conditions. [Round-2 spec §11][spec] · [RL-21 item 10][seal] · [RL-149 §3(c)][desk-rule]

## Eight component pins

The owner column names the supplying roles. The accountable signer and each
accepted identity remain UNFILLED. A digest includes its algorithm and what
bytes it covers. For a program with multiple files, include the owner's
approved entry points, complete source closure and digest method at the
immutable source commit. Historical pins in the last column are provenance
only. Acceptance evidence must identify the reviewed bytes and the applicable
run, review or ruling, including dispositions of changes since review.

| Component | Final path or owner-approved closure | Immutable source commit | Digest and method | Acceptance evidence identity / digest | Supplying owner (role) | Outstanding input | Historical provenance only |
|---|---|---|---|---|---|---|---|
| Protocol | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Lead / protocol owner | Final admitted text and amendment identities. Supply review and admission for RL-176–178, RL-182/182a and RL-185 E18/E19 as carried to the signing bytes. [RL-21 item 10][seal] · [RL-28][option-b] · [E18/E19][amendments] | `b2e01464d:docs/align/pilot_protocol_v4.md`, W1 baseline. [P4][p4] |
| Series manifest | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Series owner | Final receipt-bound option-B allocation bytes with both independently text-derived seed-check references on those bytes. Cover B5/B6 placements, reserves, retry identity and U3 N = 24. [RL-15/16][allocation] · [RL-21 items 1 and 10][builds] · [P4 B5][seed-checks] | `b2e01464d:configs/campaigns/align_v4/series/series_manifest.json`, path as cited by P4. [P4 roster][roster] |
| Primary engine | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Sol-family analysis owner / integration owner | Amended option-B entry point and approved closure. Supply text-only build provenance, final wire descriptor, exact paired run and Opus cold verdict with corrective-delta dispositions. Attach the metadata-baseline blob and stage-(a) evidence below. [RL-21][builds] · [RL-187 §2.3][auc] · [Row 13 INT/REVIEW][row13-owners] | `de4a54db9:joulewise/align/v4_analysis/engine.py` (`analyze`) retains the old allocation and unresolved claim codes. [Historical engine][old-engine] |
| Independent recompute | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Opus-family recompute owner / integration owner | Amended option-B program and approved closure. Supply text-only build provenance, final wire descriptor and accepted independent run paired with the exact primary. Show both builds used the ruled text without cross-reading source or sharing new outcome arithmetic. [RL-21][builds] · [Round-2 spec §11][spec] · [Row 13 INT/REVIEW][row13-owners] | `7b9d215ff:scripts/independent_recompute_v4.py` retains the old allocation. [Historical recompute][old-recompute] |
| Blinded comparator | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Comparator / integration owners, with both adapter owners | Approved closure and pins for the exporter, release driver and comparator. Supply both approved producer descriptors for exact pointers, side/branch, row and list identities, mirrors, sentence templates and ruled classes, including B7 items 1/4/5/6 and RL-149 §4 prints. Bind the independent census and truth cards and the full/prefix run index to these schemas and builds. Show intact and restored agreement, missing/extra-row refusal, removal of the old claim exemption and detection at every new compared occurrence, including withholding. Record each mutation's plan, mode, logical key, pointer, rule, expected exit/family and run reference. [RL-21 items 8–10][coverage] · [Round-2 spec §11][spec] · [Adapter and integration requests][owner-inputs] | `4c4b76e3a:scripts/export_v4_series.py`, `b2c0681cd:scripts/release_v4.py` and `scripts/compare_v4_recompute.py`. Earlier comparison exempted the claim block. [Historical driver][stage-a] · [Historical comparator][old-comparator] |
| Numeric bars | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Comparator / bars owner | Final bars and selector evidence on both maps. Name each RL-187 family and governed leaf, with exact decision and withholding comparisons, the single metadata AUC exemption and refusal for `unbound_numeric`. [RL-21 items 8 and 10][coverage] · [RL-187 classes][bars] · [RL-187 §2.3][auc] | `b2c0681cd:configs/analysis/v4/recompute_bars.json` carried `claim_contract_open`. [Historical bars][old-bars] |
| Task evaluator | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Evaluator / exporter owners and signatory | Frozen wrapper, upstream/cache and exporter normalization identities. Supply judge-free qualification, both-pair conversation-invariance and unavailable-outcome results, and the signer's E17 frozen numeric field or ruled null. [RL-17][evaluator] · [RL-185 row 5][release-gate] · [P4 B3][p4-b3] | `b2e01464d:joulewise/align/shade/task.py` (`ShadeTask.score_side` / `score_main`). [Historical wrapper][old-evaluator] |
| Desk | UNFILLED | UNFILLED | UNFILLED | UNFILLED | Desk owner / integration owner | Final guard, reader, projections and entry-point closure. Supply the integrated cold disposition, W1 registered exceptions by output and authority, prefix withholding and pooled-output checks, and release/no-release witnesses including the forbidden-open trap. Account for the desk follow-up on the signing candidate. [RL-149 §3][desk-rule] · [RL-183 §2.5][desk-follow] · [Row 13 DESK][row13-owners] | `b2e01464d:joulewise/align/apple/v4_desk_seal.py`, earlier guard and release-event reader. [Historical desk][old-desk] |

## Evidence tied to both final builds

| Evidence the owner supplies | Fill |
|---|---|
| Row 13 `INT` primary and independent recompute evidence IDs, their separate text-based provenance and the exact paired full/prefix run and mutation index. [Row 13 RL21-01–09][row13-cases] · [Row 13 INT and REVIEW][row13-owners] | UNFILLED |
| Row 13 `REVIEW` Opus cold-verdict ID on the exact Sol closure and run index, reviewed-to-final deltas and dispositions, and lead acceptance reference. [Row 13 RL21-09][row13-cases] · [Row 13 REVIEW][row13-owners] | UNFILLED |
| Primary reader entry point and source lines from authenticated committed history through `record_commit`, shared finality and effective assignment set, with its own replay result. [RL-56][replay] · [RL-185 §3.3][finality] | UNFILLED |
| Independent recompute reader entry point and source lines for the same chain, with its independently derived replay result. [RL-56][replay] · [RL-185 §3.3][finality] | UNFILLED |
| Committed held/barred/released/non-final mapping consumed by each reader: record type and field or path, attempt/window/ordinal join, signed ruling linkage and committed effect. Attach paired replay and fail-closed witness IDs. [RL-65][held] · [RL-79][held-release] · [RL-185 §3.3 and row 9][release-gate] · [Row 13 MEM-HELD through MEM-A9][row13-membership] | UNFILLED |
| Reviewed exceptions and dispositions on both final closures: effective A9 union, disclosure-only and inert code decisions, W1/anchor/sentinel exclusions from S, registered W1 output exceptions, and exact prefix status/reasons. Record the applicable ruling, reviewed source lines and fixture ID for each. [RL-65 A9][a9] · [RL-71][inert] · [RL-149 §3][desk-rule] · [Round-2 spec §11][spec] | UNFILLED |
| Source blob of `joulewise/align/metadata_baseline.py` at the bound engine source and its identity in the single seal file. [RL-187 §2.3][auc] | UNFILLED |
| Release driver stage-(a) verification reference on those pins, showing the engine output bytes verified against the bound run record. Include the AUC path, closed null reasons, independent fold census, exact recompute marker and mutation dispositions. [RL-187 §2.3][auc] · [Historical stage (a)][stage-a] · [Row 13 AUC cases][row13-auc] | UNFILLED |

Both readers replay the committed chain instead of trusting cached pools.
Resolve finality from the window's own record or the successor's
`previous_final` under RL-183b's shared check. Key assignments by window ID
and manifest ordinal. A zero-capture retry is a later attempt of the same
assignment. Held and barred windows contribute zero assignments. An admitted
reserve enters under its own ID. A ruling has only its committed effect.
Missing or duplicate final evidence refuses before any loader opens. Route
conflicting admitted A9 decisions to the research lead. Distinguish excluded,
uncaptured assignments from captured eligible members with zero S rows. The
latter can still contribute to Q. [RL-56][replay] · [RL-185 §§3.1, 3.3 and row 9][release-gate] · [Series owner request][series-inputs]

Verify both readers apply A9's protocol precedence: disclose `contention.*`,
retain effective member exclusions including `agent.*`, and disclose
span/class differences. Account for the nine material window reasons, the
held precheck pending ruling, and the nine inert codes with no gate, estimand
or exclusion effect. The desk review covers the deciding contrast and
registered U3–U6 outputs for W1, and rules out non-benign extremes and
per-member heat-bearing prints before release. [RL-65][a9] · [RL-71][inert] · [RL-149 §3][desk-rule]

For the metadata AUC, require one engine leaf with a
finite value in [0, 1] or a reasoned null, compare fold identities and counts
by condition exactly against the independent census, and require one exact
recompute marker `{"status": "exempt", "reason": "shared_library_print"}`.
Only the AUC value is exempt from comparison. Stage (a) verifies the engine
output bytes. [RL-187 §2.3][auc]

Unconfirmed representation is an open owner input. **Only if the owner
demonstrates that no committed held-window representation exists** does Opus
take the specific missing relation and affected readers back to Fable.
[RL-79][held-release] · [RL-185 row 9][held-return]

## Single-file and dossier handoff

| Lead and owner verification | Fill |
|---|---|
| Accountable signer / owner confirmation and public-safe analysis-seal reference | UNFILLED |
| Carrying commit, committed file and digest (algorithm and covered bytes) of the actual single file, checked privately against all eight accepted rows and the metadata-baseline blob | UNFILLED |
| Immutable before-first-C1 provenance of that same file and its accepted verification, with the evidence reference marking the first C1 boundary | UNFILLED |
| Clause in that file requiring a post-data fix to run through the blinded comparator and receive exactly one entry in the existing deviation record. Supply the authorized procedure reference, existing destination and the reference to record the run and single entry together. | UNFILLED |
| Dossier cross-reference binding that same carrying commit/file/digest to the R13/R14 gate and accepted evidence | UNFILLED |

The lead supplies the dossier reference at the existing R13/R14 and paired
build gate in the C1 READY handoff. [RL-21 item 10][seal] · [C1 READY fills][ready] · [C1 READY carry rules][ready-carry]

| Separate record | Timing and meaning | Authenticated reference |
|---|---|---|
| Four executable registration bindings on one signed receipt | Before C1: `joulewise/align/apple/s_rows.py`, `scripts/align_v4_series_release.py`, `joulewise/align/apple/rl176.py`, and `joulewise/align/apple/rl176_phases.py`, all non-null. Carry the W1 receipt if all four are bound and verified, otherwise use the re-signed C1 receipt. Attach the stored-record → builder → caller → S-word synthetic witness at 102 and 101 of 154. The receipt covers this executable chain. [RL-182 §1.5][four] · [C1 READY fills][ready] | UNFILLED |
| Threshold freeze | At `calibration_complete`, hash-commit the thresholds in the sealed freeze. Thresholds and T scores print at series release. [RL-149 §3(b)][desk-rule] | UNFILLED |
| Series release receipt | At the later authorized release event, the lead-signed receipt binds the committed completion record with the last admitted test window's final eligibility. Desk release identifiers are defined in the public source. [RL-149 §3(b)][desk-rule] · [Desk release-event source][release-event] | UNFILLED |

[spec]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/CLAIM-CONTRACT-B-ROUND2-SPEC.md#L189-L207
[seal]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L452-L457
[builds]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L428-L457
[coverage]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L444-L457
[replay]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L2763-L2765
[a9]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L3409-L3415
[held]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L3451-L3453
[inert]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L3780-L3788
[held-release]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L4352-L4361
[desk-rule]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L12730-L12756
[four]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19776-L19787
[desk-follow]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20233-L20242
[amendments]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20793-L20842
[finality]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20874-L20883
[release-gate]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20848-L20897
[held-return]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20897
[bars]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21605-L21620
[auc]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21654-L21666
[option-b]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L778-L804
[allocation]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L321-L348
[evaluator]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L354-L363
[p4]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md
[roster]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L1008-L1021
[seed-checks]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L1355-L1363
[p4-b3]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L1270-L1284
[old-engine]: https://github.com/mpmdw/JouleWise/blob/de4a54db9/joulewise/align/v4_analysis/engine.py#L33-L67
[old-recompute]: https://github.com/mpmdw/JouleWise/blob/7b9d215ff/scripts/independent_recompute_v4.py#L1722-L1726
[stage-a]: https://github.com/mpmdw/JouleWise/blob/b2c0681cd/scripts/release_v4.py#L152-L191
[old-comparator]: https://github.com/mpmdw/JouleWise/blob/b2c0681cd/scripts/compare_v4_recompute.py#L1922-L1928
[old-bars]: https://github.com/mpmdw/JouleWise/blob/b2c0681cd/configs/analysis/v4/recompute_bars.json#L107-L110
[old-evaluator]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/shade/task.py#L434-L439
[old-desk]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/apple/v4_desk_seal.py#L49-L60
[release-event]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/apple/v4_desk_seal.py#L357-L367
[owner-inputs]: https://github.com/mpmdw/JouleWise/blob/b3519bf0c/docs/run_reports/2026-11-18-c1-comparator-owner-inputs.md#L12-L45
[series-inputs]: https://github.com/mpmdw/JouleWise/blob/b3519bf0c/docs/run_reports/2026-11-18-c1-comparator-owner-inputs.md#L45-L64
[row13-cases]: https://github.com/mpmdw/JouleWise/blob/74a8a7486959180bc392312b0181ed21473ce3a5/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/ROUND2-REHEARSAL-INDEX.md#L15-L27
[row13-membership]: https://github.com/mpmdw/JouleWise/blob/74a8a7486959180bc392312b0181ed21473ce3a5/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/ROUND2-REHEARSAL-INDEX.md#L102-L108
[row13-auc]: https://github.com/mpmdw/JouleWise/blob/74a8a7486959180bc392312b0181ed21473ce3a5/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/ROUND2-REHEARSAL-INDEX.md#L233-L235
[row13-owners]: https://github.com/mpmdw/JouleWise/blob/74a8a7486959180bc392312b0181ed21473ce3a5/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/ROUND2-REHEARSAL-INDEX.md#L297-L312
[ready]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/C1-READY-DRAFT.md#L10-L28
[ready-carry]: https://github.com/mpmdw/JouleWise/blob/00a28dcf2/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/C1-READY-DRAFT.md#L49-L66
