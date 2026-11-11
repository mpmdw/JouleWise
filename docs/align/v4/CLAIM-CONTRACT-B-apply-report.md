# Claim contract B — Sol application report

2026-11-10. Local seat `claim-b-apply`, branch `align/2026-11-10-claim-b-apply`.
Ruled base `8aac5f25ead796fb267087231946eb2f44c6484c` (RL-12); implementation head before this report `b731cad38f64b76bbedc68b814083c530863a833`.
Applied agreement §7 items 1–28 in numbered commits, with final consistency corrections.
Nothing was pushed, merged, registered, armed or signed.

Authority read first: `CLAIM-CONTRACT-B-AGREEMENT.md`, RL-12..RL-21 at
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`,
and the Opus builder report. Sol sources read at `origin/align/2026-11-10-claim-contract-sol`
@ `6174ed082`, particularly its round-2 seal/coverage spec and build report. M0 intake found no active
stop card; this direct bounded brief selected the agent-compatible work over historical queue pointers.
Lead-owned coordination state was preserved, as instructed. No new decision or kernel task was registered.

Blind: synthetic text/arithmetic/fixtures only. No measurement bundles, v4 outcomes, real restricted
folders, night custody, /Users/edr data paths, model weights or network were accessed. Git object reads
used local refs/the allowed shared object store. No analysis job or quiet-machine collection was touched.
No MLX code changed or ran. The manifest generator's only behavioral-byte change is the three citation
strings. K scorer/threshold/dose/seed laws, placement tag/draw and other U constants are unchanged.
The only exporter code edit is the U3 roster/docstring explicitly required by item 16; round-2 exporter,
engine, recompute and comparator implementation remains out of scope.

## Per item

“Protocol/spec review” is review of registered text against the numbered clause and ruling, not a claim
that the future engine behavior has been implemented or tested. Test module names are expanded below.

| Item | Status | How | Verification |
|---:|---|---|---|
| 1 | Done | Option-B citations/anchors/links and three generator strings corrected to item 252. Manifest regenerated; test loads the original cf501f75f bytes, pins b5fedb49…1c64, compares every member and placement and proves byte replacement only. Historical builder record kept. | seedcheck (8) |
| 2 | Done | Opus checker rerun on final bytes; comparison.json replaced. Only its authority comment changed. | Opus MATCH; seedcheck |
| 3 | Done | Stdlib-only Sol checker authored from W1/R15/R24/B5/B6 text before opening Opus checker; 436 identities, 19 placements, four exact pairwise-disjoint ranges. Final source is the exact pre-Opus draft. | Sol MATCH; seedcheck mutation witnesses |
| 4 | Done | B1 and round-2 spec require 14 eligible benign T members in each pair for K HELD; X ≥ c* refutation takes precedence; short reason is test_cohort_short. | Protocol/spec review; protocol doc (6) |
| 5 | Done | Registered independent-window CP sentence directly follows FPR sentence; w/W and 63.2% at 0/3 stated. | Protocol/spec review; protocol doc |
| 6 | Done | K HELD prints each undefined H50/H90/interval as “not defined on the registered grid”; A8 unchanged. | Protocol/spec review |
| 7 | Done | K HELD and REFUTED sentences disclose no physical positive control. | Protocol/spec review |
| 8 | Done | RL-14 joint design/window intervals, W, k_w, T_w, SE_w and Student t quantile defined; W ≥ 8. | Protocol/spec review; synthetic power receipt |
| 9 | Done | 100,000 synthetic normal-model replicates, seed 20261110; only equivalence column replaced. Powers .68184/.59880/.38190/0/0. Superiority columns preserved. | claim_b_power.py → claim-b-power.json |
| 10 | Done | Rank scale first, normal 0.75-SD gloss and nominal 2.5%→about 11% sentence. | Protocol/spec review |
| 11 | Done | Registered secondary S, confirmatory K and exact ruled no-correction sentence. | Protocol/spec review |
| 12 | Done | Assigned sabotage-member stratum status/reason and eligible/assigned rates by condition/pair; eligibility conditioning explicit. | Protocol/spec review; round-2 implementation owed |
| 13 | Done | Side-success repeat descriptive: theta and both intervals, no outcome word. | Protocol/spec review |
| 14 | Done | Evaluator input exclusions, no engine/recompute transcript read, and absent/empty/altered-conversation checks for both evaluators. | Protocol/spec review; pinned-cache qualification owed before C1 |
| 15 | Done | Three placement reasons in two added sentences; law/tag/draw and all seed bytes unchanged. | Both seed checks; original-byte witness |
| 16 | Done | T4/T5 added to U3 roster; N=24 inputs, ruling 5, U table, B6, transfer note and deviation rows updated; complete synthetic OC regenerated. | U3 scope script; blockers/w1bm/R11 modules |
| 17 | Done | policy_checks enforces registered beta=.05, transfer=1.5 and manifest-derived roster/counts. Canonical JSON object order is immaterial; exporter order is asserted against manifest order. | U3 module: red 15 subcase failures, green 4 tests |
| 18 | Done | B6, instrument paragraph and thermal_escalation table now freeze C/T policy and define repeated-FAIL hold/restart. | Protocol review; packet/cadence regressions |
| 19 | Done | Both packet guards now compare status == fail; INCONCLUSIVE enters pool and consumes its slot. | Packet red/green; existing packet 45 |
| 20 | Done | W1 ladder preserved; C/T next thermal_policy must equal prior plan (series_thermal_policy_changed). Authenticated C/T FAIL bars counted; signed reset u1_u3_fail_escalation names triggering attempt. | Packet 12 full + new T4 selector; rebuild witnesses |
| 21 | Done | Failing-first C/T/reserve inconclusive, unchanged/changed policy, consecutive/third bars and ruling release cases. Added explicit T4 third-bar red baseline witness and green selector; T4 inconclusive exhausts admitted slots. | 13 distinct packet tests pass; details below |
| 22 | Done | B7 print 8 excludes listed INCONCLUSIVE windows for a print-only recomputation. | Protocol/spec review |
| 23 | Done | B8/B9/council row 2 retain unmet gate and positive_control_not_run always-print disclosure. | Protocol/spec review |
| 24 | Done | RL-18 interpretation copied into protocol and unified spec. | Literal wording review |
| 25 | Done | U5 table/pending paragraph/council row 6 closed; descriptive FAIL limitation, no obligatory change, optional one pre-C1 tightening. | Protocol doc; blockers/kit/cadence |
| 26 | Done | Opus spec renamed ROUND2; ruled K/S/prints/outcomes plus Sol seal, exhaustive row sets, prefix comparison and each-leaf perturbation coverage. | Spec review; no round-2 code implemented |
| 27 | Done | Four PRE-SIGNATURE, blind deviation rows: V4-04 freeze, V4-05 A23, U5 closure, RL16 U3 N24. | Deviation/authority review |
| 28 | Done | Opus builder report and agreement remain byte-unchanged. This apply report, check receipt and dated handoff pointer added beside/pointing to them. | git diff --exit-code on both original records |

## Final manifest and paired receipts

Manifest SHA-256: **`70009b6a594835643ef0bb2ff324ed700447cbe7a6237975ebdb209ec2c78dd6`**.

- Opus: `seedcheck-claim-b-opus/comparison.json`, **MATCH, 436 members**, same SHA.
- Sol: `seedcheck-claim-b-sol/comparison.json`, **MATCH, 436 members, 19 placement windows**, same SHA.
- Per pair: C1–C8 2–65 (64), T1–T3 66–89 (24), C9–C14 100–147 (48), T4–T5 148–163 (16),
  all four ranges exact and pairwise disjoint. No seed/placement was redrawn.
- Sol checker SHA-256: `0baca4cf52aee191662307b99e86d00f7c5dbe86e2db8176e931b800a31561af`.
  Final source is byte-identical (`cmp`) to `/private/tmp/claim_b_sol_seedcheck.py`, authored before the
  Opus checker was opened. A later W1 role-label annotation was discarded to retain that exact source.
  Sol independently compares eight identity/seed fields of every member (ordinal, pool, pair, condition,
  index, model, episode seed, first turn seed); W1 presentation-only `role` labels are not its input.
  Opus and the original-byte witness also cover those labels.

The item-1 test obtains the original manifest from `cf501f75f`, verifies its full
`b5fedb49ee04e0b5388ea43a76b6fbf07cb94b896145476386271e702fb41c64` SHA, compares every member row
and every sabotage_ordinals entry and asserts that replacing only `RUN_STATE 251`/`RUN_STATE_251`
with 252 reproduces the entire new byte stream. It passes on the final tree.

Commands (all exit 0):

```text
python3.13 -B scripts/align_v4_series.py candidate --out configs/campaigns/align_v4/series/series_manifest.json
python3.13 -B docs/align/v4/seedcheck-claim-b-opus/derive_and_check.py --write-receipt
python3.13 -B docs/align/v4/seedcheck-claim-b-sol/derive_and_check.py --manifest configs/campaigns/align_v4/series/series_manifest.json --out docs/align/v4/seedcheck-claim-b-sol/comparison.json
python3.13 -B docs/align/v4/claim_b_power.py --out docs/align/v4/claim-b-power.json
python3.13 -B scripts/align_v4_u3_scope_comparison.py --output docs/align/v4/U3-scope-n24.json
```

The new synthetic U3 evidence gives n=7, beta=.05, N=24: q=4.3305463646 (rounded 4.3305),
D multiplier 6.4958195469 (rounded 6.4958). Historical N=22 evidence is preserved.

## Tests and checks

**402 distinct tests passed across 23 targeted modules**, counting the original 12-case new packet module
plus its later explicit T4-third-bar selector as 13 distinct cases. No full suite or pytest ran.
Recorded unit-test time, including red runs and repeats, is about 12 minutes, below the requested budget.
[Machine-readable checks](CLAIM-CONTRACT-B-apply-checks.json) records commands, counts, timing,
output hashes and the saved packet red-run outputs.

Each table row is `python3.13 -B -m unittest <module>`; the 21 rows were run serially.

| Module | Result | Seconds |
|---|---:|---:|
| `tests.align.test_v4_cadence` | 30 OK | 0.367 |
| `tests.align.test_v4_test_reserves` | 2 OK | 13.373 |
| `tests.align.test_v4_next_arm_packet_opus_witnesses` | 5 OK | 8.097 |
| `tests.align.test_v4_series` | 16 OK | 39.325 |
| `tests.align.test_v4_replacement_windows` | 20 OK | 10.027 |
| `tests.align.test_v4_series_r20` | 10 OK | 1.632 |
| `tests.align.test_v4_series_delta5` | 3 OK | 2.733 |
| `tests.align.test_r11_delta5_sol1` | 8 OK | 18.808 |
| `tests.align.test_r11_delta5_sol2` | 13 OK | 18.446 |
| `tests.align.test_r11_delta6_sol1` | 11 OK | 9.220 |
| `tests.align.test_r11_delta6_sol2` | 11 OK | 7.113 |
| `tests.align.test_w1bm_sol1` | 12 OK | 6.836 |
| `tests.align.test_w1bm_sol2` | 12 OK | 9.263 |
| `tests.align.test_v4_registration` | 22 OK | 19.001 |
| `tests.align.test_v4_receipt_tiers` | 8 OK | 4.070 |
| `tests.align.test_protocol_v4_doc` | 6 OK | 0.333 |
| `tests.align.test_v4_kit` | 116 OK | 6.734 |
| `tests.align.test_v4_seedcheck_claim_b` | 8 OK | 1.496 |
| `tests.align.test_v4_claim_b_u3` | 4 OK | 0.078 |
| `tests.align.test_v4_w1_blockers` | 17 OK | 13.353 |
| `tests.align.test_v4_series_e2e` | 10 OK | 26.724 |
| `tests.align.test_v4_next_arm_packet` | 45 OK | 131.929 |
| `tests.align.test_v4_claim_b_packet` (original full run) | 12 OK | 114.215 |

Final serial selectors/checks after consistency review:

| Command suffix after `python3.13 -B -m unittest` | Result |
|---|---|
| `tests.align.test_v4_claim_b_packet.ClaimBPacketTests.test_item21_third_nonconsecutive_bar_in_test_reserve_requires_ruling` | 1 OK |
| `tests.align.test_v4_claim_b_packet.ClaimBPacketTests.test_item19_t_and_reserve_inconclusive_use_slots_without_ladder_or_bar` | 1 OK |
| `tests.align.test_v4_seedcheck_claim_b` | 8 OK |
| `tests.align.test_protocol_v4_doc` | 6 OK |

Failing-first evidence: item 17's new U3 module had 15 failing subcases across four tests; the initial
12-case packet module had 11 failures, exposing non-PASS escalation, rejection of unchanged plans and
absence of the named repeated-FAIL hold. The extra T4 third-bar case failed against the isolated
pre-items-19–21 builder (`71c4341e8`) before passing against the applied builder. The old source was
loaded in memory into the fixture, with no checkout or production-file mutation.

Other checks: all 25 changed Python sources compiled using Python 3.13 `compile`; `git diff --check
8aac5f25e` passed. `git diff --exit-code` confirmed the coordination files, original Opus report and
agreement are unchanged. Final diff review found no engine/recompute/comparator/scorer/threshold/dose
implementation change.

Two process mistakes are disclosed, not counted as valid baseline evidence: an initial six-test seed run
overlapped citation edits and saw mixed versions (one failure, one error); it was discarded and replaced
by clean passing runs. A 0.293-second cadence run briefly overlapped the existing packet module; cadence
was rerun in the serial table above. Subsequent runs were serial. These mistakes did not read data or
trigger a full suite.

## Interpretation details, exceptions and remaining work

- Item 1 says **“both spec files”** and **“Update the sha wherever it is written.”** Only the Opus spec
  exists on the ruled base. The Sol source-branch spec was read, and its seal/coverage contribution is
  incorporated in the renamed unified spec; no duplicate stale Sol spec was imported. Historical
  Opus report/agreement citations and old SHA are intentionally preserved under item 28, which says
  **“Keep CLAIM-CONTRACT-B-opus-report.md as the builder's record.”** Active pins and receipt pointers
  use the new SHA/item 252. This is the only file-preservation qualification to literal application.
- Item 9 says **“computed by synthetic simulation under the table's own model (normal location shift,
  independent pairs).”** The joint rule additionally needs a window layout. The receipt states the
  planning convention explicitly: first K_S strata of eleven two-pair windows. Thus 11 strata have W=6
  and cannot pass W>=8. This convention describes the power calculation only; eligibility/inference
  still uses every realized stratum. Other attrition layouts can have different power.
  The simulated full-roster power is .68184 (MC SE .00147), rather than RL-14's rough .72 known-SE
  planning approximation. The registered rule was applied unchanged; the lead should review the
  planning convention and computed column, not treat the approximation as an acceptance target.
- Item 20's new `resets: u1_u3_fail_escalation` uses the existing committed `series.lead_rulings` input,
  with digest-authenticated nonempty text, valid lead signature and exact triggering attempt. The
  rebuilt thermal check retains applied rulings/counts. They reset only thermal counts, not the legacy
  zero-capture count/ledger; legacy rows without `resets` retain their existing meaning. A ruling never
  bypasses the in-series thermal-policy equality check. A restart/new cohort remains lead-controlled.
- Existing B5 wording says **“the other fifteen fresh members are benign”**, although the roster is
  fourteen benign plus two sabotage-instructed members. This pre-existing sentence was not among the
  requested changes and the seed law/draw was expressly frozen. The generator, both checks and all
  member rows retain the registered 14+2 shape; lead may clarify that sentence in review.
- No native MLX validation is required for changed MLX code (none changed). The pinned SHADE side/main
  conversation-invariance qualification has only been specified, not run here: the allowed offline
  cache was not accessed. It remains a pre-C1 round-2 prerequisite, as does the full/prefix synthetic
  producer→engine→recompute→comparator rehearsal and analysis seal.
- The required **Opus cold review of Sol-applied code (17, 19–21)** and the research lead's final review
  have not occurred in this seat. No review, merge, U3 signature, W1 registration or C1 admission is
  claimed. Existing engine/recompute remain incompatible with these manifest bytes until round 2.

Next exact step: provide this branch and report to the lead for the Opus cold review and research-lead
final review of RL-12..RL-21. Nothing merges and W1 does not register before that review. The lead then
handles v4-line admission/signatures; round 2 and the analysis seal gate C1.

## Changed files and commits

Changes before this report commit (the report, checks JSON and dated handoff pointer are additional):

```text
M	configs/campaigns/align_v4/series/README.md
M	configs/campaigns/align_v4/series/series_manifest.json
M	docs/align/pilot_protocol_v4.md
R054	docs/align/v4/CLAIM-CONTRACT-B-opus-engine-spec.md	docs/align/v4/CLAIM-CONTRACT-B-ROUND2-SPEC.md
M	docs/align/v4/DEVIATIONS.md
A	docs/align/v4/U3-scope-n24.json
M	docs/align/v4/U3-transfer.md
A	docs/align/v4/claim-b-power.json
A	docs/align/v4/claim_b_power.py
M	docs/align/v4/seedcheck-claim-b-opus/comparison.json
M	docs/align/v4/seedcheck-claim-b-opus/derive_and_check.py
A	docs/align/v4/seedcheck-claim-b-sol/comparison.json
A	docs/align/v4/seedcheck-claim-b-sol/derive_and_check.py
M	joulewise/align/apple/v4_cadence.py
M	joulewise/align/apple/v4_u3.py
M	scripts/align_v4_next_arm_packet.py
M	scripts/align_v4_series.py
M	scripts/align_v4_u3_export.py
M	scripts/align_v4_u3_scope_comparison.py
M	tests/align/test_protocol_v4_doc.py
M	tests/align/test_r11_delta5_sol1.py
M	tests/align/test_r11_delta5_sol2.py
M	tests/align/test_r11_delta6_sol1.py
M	tests/align/test_r11_delta6_sol2.py
A	tests/align/test_v4_claim_b_packet.py
A	tests/align/test_v4_claim_b_u3.py
M	tests/align/test_v4_replacement_windows.py
M	tests/align/test_v4_seedcheck_claim_b.py
M	tests/align/test_v4_series.py
M	tests/align/test_v4_test_reserves.py
M	tests/align/test_v4_w1_blockers.py
M	tests/align/test_w1bm_sol1.py
M	tests/align/test_w1bm_sol2.py
M	tests/align/v4_option_b.py
M	tests/align/v4_registration_fixtures.py
```

Numbered implementation/correction commits:

```text
e1b757d3a align v4 item 1: correct option-B authority and preserve manifest rows
045825d6e align v4 item 2: renew Opus seed-check receipt for corrected bytes
d382a2b9e align v4 item 3: add independent text-derived Sol seed check
3c3d00d10 align v4 items 4-7: register K floor, window bound and complete outcome words
ef5b86798 align v4 item 8: register joint design and window equivalence intervals
0a30ddf0b align v4 item 9: simulate joint equivalence planning power
05e837c2b align v4 items 10-13: state rank margin, alpha and eligibility disclosures
038791fd7 align v4 items 14-15: qualify evaluator inputs and explain placement design
a0a61ea4e align v4 item 16: install N=24 U3 roster and regenerate synthetic evidence
7ab62e3ee align v4 item 17: refuse unregistered U3 constants and roster after red tests
71c4341e8 align v4 item 18: register frozen series and structural thermal hold
cc67ac11e align v4 items 19-21: bar only FAIL and enforce frozen thermal series after red tests
1d90fdfaf align v4 items 22-24: add print 8 and preserve unmet positive-control gate
d00dc1f61 align v4 item 25: close descriptive U5 admission ruling
c61d6a595 align v4 item 26: unify round-2 spec with ruled statistics, seal and coverage
f42bf448c align v4 item 27: record blind pre-signature RL-16 and RL-20 changes
9448b5cc8 align v4 items 1, 3, 16: reconcile final receipt pointers and N=24 witnesses
b731cad38 align v4 items 3, 5, 21, 26: close final provenance, wording and reserve witnesses
```

The following item-28 commit adds this report, its machine-readable check receipt and the dated handoff
pointer; its hash is available from `git log -1`. No commit was pushed.
