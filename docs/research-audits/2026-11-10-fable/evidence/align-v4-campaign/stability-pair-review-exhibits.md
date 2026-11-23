# Stability pair cold-pass exhibits

**Supporting evidence for Opus and Fable.** Submit the final `lm-stab-01` and
`lm-stab-02` manifests together, with both exact SHA-256s and the owner fills
below. The cold pass can precede effective freeze 2. Stage 1 and reservation
each check that freeze 2 is in effect. [RL-190 §3.5][cold] · [Paired review][pair]

## Exhibit A · Kit identity, positional comparison and schedule

### Committed kit index

Paths in the table are relative to this document's directory. The [index][index]
at audit `04d8aa778` and target snapshot `d6016f406` has SHA-256
`9fd3d49c0a51ab75a1c4e20fb784f9f656fb70e9cfca8e2b9ff304c0eba70dae`.
The first 14 rows are the base set. All 16 digests match the public
[filler registry][registry] and the exact kit file bytes. The public
[look commitments][commitments] entry for `lm-stab-01` contains exactly the
14 base pairs, as does the [main draft][draft]. Rows 15 and 16 are absent from
that look entry and belong in the indexed population for `lm-stab-02`.
The full runner pins are `2d347f721552fe03bdd19f113e7bad7a7c24908e`
and `6e9d42f1dd3d308bc9239143d0d634ab965e50e1`.

| Kit ID | Runner pin | Path | SHA-256 | Master seed |
| --- | --- | --- | --- | ---: |
| `f2-stab-01` | `2d347f721` | `f2-stab/f2-stab-01.v1.1.json` | `dbad9c7b79088bb6f06aac1c1148c3631a0c616fd2ece596bab0f56657ce70fe` | 2026112460 |
| `f2-stab-02` | `2d347f721` | `f2-stab/f2-stab-02.v1.1.json` | `1fe8dd1d0fb60fe1d481ecb0d4358fda595668c1e889a35a75695e290fcad505` | 2026112341 |
| `f2-stab-03` | `2d347f721` | `f2-stab/f2-stab-03.v1.1.json` | `ac4b303e228233765efda120b2d63f2f6e59d7f8565c4b913880c4a1aa1dc404` | 2026112481 |
| `f2-stab-04` | `2d347f721` | `f2-stab/f2-stab-04.v1.1.json` | `494739dedbc07f2ee3a02b1e5f9561bb4812d765c7630e6931c24ea138525bff` | 2026111676 |
| `f2-stab-05` | `2d347f721` | `f2-stab/f2-stab-05.v1.1.json` | `023febe9afc8532b8f06bb40dfe32dd64a933c99e8e080a51e2686e888246b11` | 2026111508 |
| `f2-stab-06` | `2d347f721` | `f2-stab/f2-stab-06.v1.1.json` | `a02d18bafca780c580ae7dfe970e3a81e3e12b4051b269699db329f02c33172c` | 2026114403 |
| `f2-stab-07` | `2d347f721` | `f2-stab/f2-stab-07.v1.1.json` | `fb22cadce8be3c7d7642c9b55802aa0bd4ea90e41c7c0e9a5038e7a8dc88746d` | 2026111733 |
| `f2-stab-08` | `2d347f721` | `f2-stab/f2-stab-08.v1.1.json` | `aaba2ad04cbc88e9872c292699dfa9f98dfb15ad9f7e0af23a1faf0091bebf00` | 2026112349 |
| `f2-stab-09` | `2d347f721` | `f2-stab/f2-stab-09.v1.1.json` | `9a2b863f7abbffdc2d33a3af6bee7d8381d0c54883dbb4a7cac41378572c5ce8` | 2026112216 |
| `f2-stab-10` | `2d347f721` | `f2-stab/f2-stab-10.v1.1.json` | `bb54fdaff1292ab24f53204698649d0925fa00beedca70604f760a340c9ee926` | 2026111733 |
| `f2-stab-11` | `2d347f721` | `f2-stab/f2-stab-11.v1.1.json` | `e8cb23471f556d21514fb5ba37ffa409b9b697cfbd2519d3c2ab0c6922ed36fe` | 2026112450 |
| `f2-stab-12` | `2d347f721` | `f2-stab/f2-stab-12.v1.1.json` | `7a0440d3f15823760179782f85cad560e8ca917bf66201c02b1b911d79af35f9` | 2026111711 |
| `f2-stab-13` | `2d347f721` | `f2-stab/f2-stab-13.v1.1.json` | `47c3d2f5f6133112e7a209c9522e48bb3388c7fa27f56e5ffdf86962d95f7de3` | 2026115694 |
| `f2-stab-14` | `2d347f721` | `f2-stab/f2-stab-14.v1.1.json` | `73fe743e013cddd6d5294e95e076c64933a81eb95933fb4aa5dfb85471b9402d` | 2026114612 |
| `f2-stab-15` | `6e9d42f1d` | `f2-stab/qual-pin/f2-stab-15.v1.1.json` | `8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1` | 2026112669 |
| `f2-stab-16` | `6e9d42f1d` | `f2-stab/qual-pin/f2-stab-16.v1.1.json` | `0fc1139dfb4b92ab18e5fb4c0b66e0d211a02e218e841a4cf94fde1fb19f2b96` | 2026113603 |

### Positional comparison owed to Fable

Compare each kit with the published `f2-inst-01.v1.1.json`, SHA-256
`651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`.
All 16 preserve the ordered 12 positions `L001` through `L012`. The nominal
prompt sequence is `19458, 256, 2000, 2000, 256, 19458, 256, 2000, 19458, 2000, 19458, 256`.
Every position has decode cap 512, G0 shape `own`, and band `q600`. Every
kit retains the Automatic power-mode guards. [Instrument kit][instrument] ·
[Base comparison and extension provenance][kit-design] · [RL-181 §2.6][rl181]

| Comparison with `f2-inst-01` | Differences in the committed design files |
| --- | --- |
| All 16 kits | `/campaign_id`, `/ruling/id` (`RL-169a` to `RL-179`), `/seed_law/master_seed`, and `/legs/*/seed` at every position. The first different leg-seed index is 0 in every kit. |
| Base kits 01–14 | The four paths above exhaust the differences. The frozen block equals the instrument kit's. |
| Extension kits 15–16 | The same four paths plus `/frozen/commit` and seven digests under `/frozen/paths`. The 38 frozen path names agree, and the two extension kits share the same frozen block. |
| Within either stability pin | Campaign IDs and every derived leg seed differ. Master seeds can coincide, as in kits 07 and 10. `/ruling/id` is the same throughout stability. Between pins, the frozen block also differs as above. |

The design manifest records the first-hit search. Its candidate count is
the recorded master seed minus 2026111444 plus one. This comparison uses the
committed seeds and bytes. At stage 1, the authorized owner still binds the
realised prefill/decode pair and missing-count reason at every position. The
existing wording condition for “same work” requires exactly one realised pair
at each position across contributors. Otherwise the ruled wording is “same
cell of work.” [Kit build manifest][kit-design] · [RL-181 §2.6][rl181] ·
[Draft stage 1][draft-stage]

### Public issue and Check observations

This snapshot is bounded by public RUN_STATE item 483. The issue and Check
entries identify candidate spans. The authorized stage-1 cut determines
qualification and distinct dates from its authenticated inputs.

| Local date | Public operational record | Treatment for the future stage-1 cut |
| --- | --- | --- |
| 2026-11-18 | Kit 15 L001 has a Check entry. | Kit 15 alone cannot supply a base date. A qualified leg can supply a full-roster date. |
| 2026-11-19 | Kit 15 L002 and base kit 01 L001 have Check entries. | The base leg can supply the base date if qualified. For the full roster, multiple qualified legs on that date still contribute one distinct date. |
| 2026-11-20 | Base kit 01 L002 and L003 have Check entries. Item 483 also records the issue of L004. | Check and issue text leave the admissible close and qualification to stage 1. A closed, qualified base leg on that date can supply one base date. |

[Items 444][rs444], [453][rs453], [468][rs468], [478][rs478], [483][rs483] ·
[RL-190 §§1.1–1.2][rl190]

### Schedule and invented hand cases

`lm-stab-01` is due at the first proven close that gives stage 1 fourteen
distinct local t0-dates with qualified base-kit legs. Fourteen schedules the
read. `lm-stab-02` is due at the lead's committed `paper1_data_lock`. If
that lock commits before 01 has run, 01 is marked `coalesced` and 02 is
the only read. If 01 has run, 02 is still due at the lock. Each authorized
read uses the closes at its own committed stage-1 cut, on or after the due
event when the preconditions hold. A third read requires a ruling.
[RL-181 §2.6][rl181] · [RL-190 §1.5][early]

All inputs below are invented. D01–D15 are local dates in January 2030 with
the corresponding day numbers. Each member has its own closed single-leg
span. Bᵢ is kit `f2-stab-i` (two digits), position L002, on Dᵢ unless
another date is given. X and Y are kit 01 positions L005 and L007 on D01.
E is kit 15 L002; F is kit 16 L002. They all use the nominal 256-token
cell. A member is qualified unless marked loaded. The cases assume the
other read preconditions have been satisfied when a read is shown.

| Event and invented cut | Base legs / dates | Extension-pin legs / dates | Full legs / dates | Read and expected handling |
| --- | ---: | ---: | ---: | ---: | --- |
| Early lock, zero qualified dates. A loaded B₁ closes on D01. | 0 / 0 | 0 / 0 | 0 / 0 | 01 coalesced. 02 runs once. Both views retain the accounting row and empty tables give null with `no_qualified_leg`. |
| Early lock, one date. B₁, X and E all on D01. | 2 / 1 | 1 / 1 | 3 / 1 | 01 coalesced. 02 runs once. Both views have fewer than two dates for between-date SD. |
| Early lock, thirteen dates. B₁–B₁₃ plus X, Y and E on D01. | 15 / 13 | 1 / 1 | 16 / 13 | 01 coalesced. 02 runs once at the lock. D01 counts once in the full view and once in the base view. |
| Kit-15-only date. B₁–B₁₃ plus E on D14, with no lock. | 13 / 13 | 1 / 1 | 14 / 14 | D14 belongs to the full view. 01 stays below its fourteen-base-date trigger. A lock at this cut would run 02 and coalesce 01. |
| Loaded base leg. Same preceding cut plus a loaded B₁₄ on D14. | 13 / 13 | 1 / 1 | 14 / 14 | B₁₄ stays in accounting as `not_qualified:loaded`, with `loaded` as the missing-pair reason. It supplies zero qualified legs, zero prints and zero base dates. |
| Ordinary base trigger. B₁–B₁₄ all qualified, plus E on D14. No lock. | 14 / 14 | 1 / 1 | 15 / 14 | 01 is due at the close of B₁₄. Its cut, counts and tables use the base view. 02 awaits the lock. |
| Later lock, after 01 ran on the preceding cut. Add F on D15. | 14 / 14 | 2 / 2 | 16 / 15 | 02 runs once at its own cut with both views. Its public counts are 16 and 15. 01 keeps its earlier cut. |

With the one-date cut, between-date SD is null with `fewer_than_two` in
both views. Date counts in the full column are the union of the two pins'
qualified dates. RL-192b makes the flag alone sufficient for exclusion and
retains the loaded row. Where multiple checks fail, use the ruled reason
precedence. The lock row carries no count fields. The exact counts by kit
set and runner pin belong in 02's committed stage-1 output, linked from its
`stage1_committed` row. Nothing in these examples supplies that row.
[RL-190 §§1.3, 1.5][index-rule] · [RL-192b][loaded] · [RL-191 §1.1][precedence]

## Exhibit B · Manifest fields, sources and owner fills

At the pinned target snapshot, `looks/lm-stab-01.manifest.json` is the same
draft as on main `c05bcfc45`. The companion
`looks/lm-stab-02.manifest.json` is absent from the target. Main's dispatcher
already lists both routes. The gap worksheet predates the committed index,
RL-190's receipt-based rule and early-lock correction, and RL-192b's loaded
disposition. The matrix gives the requirements for the eventual pair.
[Draft][draft] · [Audit directory][looks] · [Dispatcher][dispatcher] ·
[RL-190 §1][rl190] · [RL-192b][loaded]

| Manifest field or linked evidence | `lm-stab-01` | `lm-stab-02` | Source and owner |
| --- | --- | --- | --- |
| `schema`, `look_kind`, `look_id`, `title`, `status` | v2 description, independent ID, existing first-read title, draft at source. | v2 description, independent later-read ID and title. | Integration owner with Opus finalizes both with `status=committed` under the accepted validator. [RL-181 §2.1][shape] · [Draft][draft] |
| `rulings`, `when` | Fourteen qualified base t0-dates. Coalesced if lock precedes the run. | Due on the committed lock, including if 01 has already run or zero dates qualify. | Opus carries forward the governing references in the existing fields. Fable adjudicates any new scientific choice. [RL-181 §2.6][rl181] · [RL-190 §1.5][early] · [RL-192b][loaded] |
| `kits`, `kit_index_path` | Name the exact 14 base ID/digest pairs. | Name the same base pairs and pin the path `f2-stab/KITS.json` under the campaign directory. The index supplies the full roster. | Opus binds the base pairs and index path. `#868` owns validation and loading. [Draft pairs][draft] · [Index rule][index-rule] |
| `stage1` population proof | Authenticate the base member receipts and decide which closed legs and dates qualify at the cut. | Commit the index hash. Require all 14 base rows and census every span receipt under the stability output roots. Each receipt must name an indexed ID and match that row's kit digest and runner pin. Future mint PRs add their row before first issue. | Opus supplies the approved source bindings and counts. `#868` owns the refusal behavior. The superseded worksheet's row-before-first-receipt test is replaced by this census and receipt binding. [RL-190 §1.3][index-rule] · [RL-190 §3.4][ancestry] |
| `stage1` disposition and token table | One leg per span. Bind receipt, span, position and attempt, kit ID, digest and runner pin. Keep failed leg rows, exact counts and the operational token table. | Same accounting with the runner pin on every leg row, and counts by kit set and pin. | Opus binds the hand table, Q1 and desk-final (row 7) and the authorized operational inputs. Disposition comes from `leg_record.json` and `runner_receipt.json` only. Use leg status, G0 outcome, quiet span of at least 600 s, decode against cap, cap reached, mode and loaded flag. Carry the as-run span index and boolean overtime flag. [Draft stage 1][draft-stage] · [RL-179 row 7][row7] · [RL-190 §3.2][asrun] · [RL-192b][loaded] |
| `channels`, `rail_sum_columns`, `stage2` | `gpu_rail`, `rail_sum`, `dc_in`. Ordered rail columns `cpu_power`, `gpu_power`, `ane_power`. Use the fixed stage-1 cut. | Same channels, ordered columns and admission checks for both views. | `#868` provides accepted implementation and synthetic verification. Coverage, U1 and clean DC-in precede interval values. A veto gives the affected print null with its reason and preserves counts. Compare the ordered rail metadata before reading interval values. A mismatch nulls the rail-sum prints and goes to Fable. [Draft stage 2][draft-stage] · [RL-185 §4][rails] |
| `prints`, `outputs` | Base view of `hold.json`, `turn.json`, `date_spreads.json` and `context.json` plus the process-tree `stdout` and `stderr`. | Print each of those four tables over the full indexed roster and again over the 14 base kits on the same closes. Leg rows retain the runner pin. The same six output names cover the private inventory. | Opus binds both inventories. `#868` owns the schemas and checks. Preserve the existing print definitions and names. [Draft inventory][draft-output] · [RL-181 §2.2][shape] · [RL-190 §1.3][index-rule] |
| `PUBLIC.json` | Exact six fields `look_id`, `manifest_sha256`, `commit`, `stage1_sha256`, `n_legs`, `n_local_dates`. Qualified counts from the base cut. | Same six fields. Qualified counts from the full cut. Base-view and per-pin counts stay in stage 1. | Opus supplies expected bytes from committed stage 1, with `commit` binding its ledger row. The six fields are hashes, identifiers and integers. [RL-181 §2.2][shape] · [RL-190 §1.3][index-rule] · [Draft inventory][draft-output] |
| `code_pins` | Eight SHA-256 values remain `PENDING:CODE` in the draft. | Bind the accepted common roles and the applicable stage-1, output and private schema bytes. | `#868` supplies accepted executor and schema artifacts and dependency provenance. Opus independently hashes the exact accepted files and records final validation on each exact manifest. [Draft pins][draft-output] · [Description schema][schema] |
| `freeze2` and ledger sequence | Authenticate the incoming `lm-interim-01/freeze2_sha256`. Both final manifests precede the first stability reservation. | Same freeze-2 reference. The lead's committed lock governs due time and any coalescence. | Opus verifies effective freeze 2 on main under RL-180 row 3. Each manifest commit is an ancestor of its stage-1 commit, which precedes reservation. Keep close, projection and manifest registration provenance distinct. [Draft freeze2][draft-output] · [RL-180 rows 3–7][reservation] · [RL-190 §3.4][ancestry] |

The shared code-pin roles are `kit_commitments`, `reader`, `manifest_schema`,
`validator` and `schema_validator`. The draft names the `lm-stab-01` stage-1,
output and private schema paths for the other three roles. For `lm-stab-02`,
record the applicable paths from the accepted integration. The final
validator refuses `PENDING:CODE` and `OPEN-n` anywhere in either file.
[Draft pins][draft-output] · [RL-181 §2.1][shape]

### Future fills for the paired submission

Blank cells are to be supplied on acceptance. Each exact manifest digest is
bound by Fable's named ruling with the executor and schema revisions, both
inventories, synthetic hand tables, row-7 evidence, host rehearsal and
once-only test. Changed manifest bytes require review of the new digest.
[RL-190 §3.5][cold]

| Owner and required evidence | `lm-stab-01` | `lm-stab-02` |
| --- | --- | --- |
| Integration owner / Opus · Final manifest SHA-256, path and main registration commit | | |
| PR #868 owner / Opus · Accepted clean executor revision, eight code-pin byte records and indirect dependency provenance | | |
| PR #868 owner / Opus · Accepted schema revisions and final validation on the exact bytes | | |
| PR #868 owner / independent verifier · Synthetic hand-table, release inventory, host rehearsal and once-per-ID evidence | | |
| Opus / authorized source owner · Authenticated row-7 bindings, effective freeze-2 proof and stage-1 cut, commit and hash | | |
| Lead · Committed `paper1_data_lock` row and resulting look ledger state | | |
| Fable through Opus · Paired exact-hash ruling and signatures / private-read authorization | | |

[shape]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19383-L19405
[rl181]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19436-L19453
[rl190]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22320-L22382
[index-rule]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22340-L22382
[early]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22369-L22382
[asrun]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22434-L22439
[ancestry]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22450-L22457
[cold]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22459-L22466
[pair]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21589-L21593
[loaded]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23022-L23041
[precedence]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22642-L22659
[row7]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18914
[rails]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20909-L20918
[reservation]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19218-L19222
[index]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/KITS.json
[kit-design]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/MANIFEST.md
[instrument]: https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2/f2-inst-01.v1.1.json
[registry]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/process/cadence/looks/filler-kit-registry.json
[commitments]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/process/cadence/looks/look-kit-commitments.v2.json
[looks]: https://github.com/mpmdw/JouleWise/tree/d6016f406/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks
[draft]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-stab-01.manifest.json
[draft-stage]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-stab-01.manifest.json#L84-L86
[draft-output]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-stab-01.manifest.json#L87-L167
[dispatcher]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/joulewise/cadence_looks/manifest_dispatch.py#L40-L42
[schema]: https://github.com/mpmdw/JouleWise/blob/c05bcfc45/docs/process/cadence/looks/look_manifest.v2.schema.json#L462-L556
[rs444]: https://github.com/mpmdw/JouleWise/blob/d6016f406/RUN_STATE.md#L1966
[rs453]: https://github.com/mpmdw/JouleWise/blob/d6016f406/RUN_STATE.md#L1757
[rs468]: https://github.com/mpmdw/JouleWise/blob/d6016f406/RUN_STATE.md#L1436
[rs478]: https://github.com/mpmdw/JouleWise/blob/d6016f406/RUN_STATE.md#L1186
[rs483]: https://github.com/mpmdw/JouleWise/blob/d6016f406/RUN_STATE.md#L1055
