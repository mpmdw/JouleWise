# Pin inventory for the release-day prune

Prepared for `ops/2026-11-08-prune-plan`; repository snapshot
`4e7e878a151d919faf56bb9131af1fcca4b7be75` (`HEAD` = locally recorded `origin/main`).
This is a source/Git-object inventory, not a release authorization. No tags were
created, branches removed, measurements opened, or external storage inspected.

Authority: [freeze-by-commit, F1–F7](../process/freeze_by_commit.md),
[decision log, D-188–D-191](../decision_log.md#d-188-block-5-analysis-rewrite-under-result-equivalence-engineering-window-fresh-analysis-start-ed-2026-11-02),
[previous prune](../run_reports/2026-11-06-repo-prune.md), and the present PI brief.
SHA recorded by a registration remains the authority; a tag supplies retention
and discovery. Never move an existing tag to make a check pass.

## How to use the tables

The table below records the scientific anchors. The companion tables provide the
long tail without duplicating the 27,160-row digest registry:

- [PIN-COMMITS.tsv](PIN-COMMITS.tsv): 1,131 distinct, locally resolvable commit
  references, with every collected source location and a proposed retaining tag.
  Includes all 900 distinct commits resolved from `RUN_STATE.md`, historical
  registry targets, real Git commit references in current code/config/tests,
  and two seal-record commits derived with Git log as its line 42 instructs.
  These references are conservatively retained; a citation is not automatically
  a scientific pin or a current execution dependency.
- [TAGS-TO-CREATE.tsv](TAGS-TO-CREATE.tsv): 203 proposed annotated tags, including
  supplementary `pin/<family>-cited-<12hex>` tags for commits outside the named
  anchor histories. Those supplementary names are storage labels, not new
  registrations. All targets resolve locally. No fetch is needed for this snapshot.
- [PIN-UNRESOLVED.tsv](PIN-UNRESOLVED.tsv): textual hex candidates that did not
  resolve to local objects. This is a review aid, not a list of proven missing
  commits: it includes activation identifiers, dates, digest abbreviations,
  synthetic test values and external model revisions. It records the first
  source location and total location count. Do not invent tags for them.
- [SOURCE-DIGESTS.tsv](SOURCE-DIGESTS.tsv): all 107 SHA-256 literal occurrences
  in 27 tracked Python/shell/JavaScript source files under `joulewise/` and
  `scripts/`, beyond the registry's tests/configs scope. Each has a file:line
  and the containing commit/tag. These include test/sentinel constants as well
  as real pins; source preservation does not authorize changing a pinned target.
- [BRANCH-TRIAGE.tsv](BRANCH-TRIAGE.tsv): all 1,482 locally recorded remote refs,
  their exact tips and disposition. It does not establish current server state.

Locations without a ref prefix refer to the snapshot above. A location such as
`origin/lane/...:path:line` refers to that branch's recorded tip. Tree/blob IDs
are not commits. Model revisions and artifact digests are content identities;
they do not require downloading weights or creating a Git tag in this repository.

## Scientific and operational anchors

“Live” below means retain after Block-5 release for reproduction, provenance or
ongoing work; it does not mean keep executing that code on main. Full commit
names for abbreviated entries are in the companion TSVs.

| Pin | Source file:line | Required commit(s) | Protects | Live after B5 release? | Tag to create |
|---|---|---|---|---|---|
| First B5 claim/seal | `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:40`–41 | `a64000884ef5bb4b76415835f02f39803f6eb620`; `ab7b21e576a2d74f0b25d9a26b463d6934588368` | First seal and its original inputs; retained superseded history | Yes, historical provenance | `pin/b5-seal1-claim`; `pin/b5-seal1-record` |
| Second B5 claim/seal | `SEAL_RECORD.md:397`–412; `configs/campaigns/v5_claim_25g83/sealed_inventory.json` `/head` | `c27485347c9629b857df81665b5b1b8d10dcd36a`; `be6525e5a6511adf882282e404e163e14dbb738b` | Collection code, 682-file inventory, registration, analysis plan, flag catalog, sizing, identity pins | Yes | `pin/b5-collection`; `pin/b5-seal2-record` |
| Seal record itself (R and final recorded text) | `SEAL_RECORD.md:42`; `git log --diff-filter=A` and `git log -1` for that path | R `3ac9623da2fb9e3bd400750856dc010456db13ce`; last change `4c34132bcbacfb2c18ba78478e1e39bbd23fec06` | Record distinct from either seal commit, including appended harvest/erratum history | Yes | `archive/process-traces-before-release-prune-2026-11-08` |
| Harvest 1 | `configs/analysis/b5/seal_pins.json:17`; `SEAL_RECORD.md:436` | `7e6158d669cbb6fb35761aee18abf363f07c5d36` | First-seal harvest and three file digests | Yes, historical replay | `pin/b5-harvest-1` |
| Harvest 2 | `seal_pins.json:25`; `SEAL_RECORD.md:448` | `224a264c5faaae90cdf56118df37e773a932700b` | Second-seal harvest through Erratum-2 cutoff | Yes | `pin/b5-harvest-2` |
| Harvest 3 | `seal_pins.json:33`; `SEAL_RECORD.md:510` | `0699abbb0881ce64b39c46ba07de568cc3848260` | Prospective Erratum 2, epoch `1791649800`; reference-source correction | Yes | `pin/b5-harvest-3` |
| Harvest 4 | `seal_pins.json:41`; `SEAL_RECORD.md:590` | `b039c0257d1b1d407ee9598222db3f78f6ad7beb` | Prospective Erratum 3, epoch `1791738000`; harvest, bracket, whole-window and wrapper digests | Yes | `pin/b5-harvest-4` |
| Sealed digest set | `seal_pins.json:5`–14; `tests/b5_analysis/test_frozen_files.py:36`–49 | Second seal plus harvest-4 and accepted analysis commits above/below | Eight SHA-256 values, including both errata, plus per-harvest file tables; all digest literals remain authoritative | Yes, commit-scoped after migration | Same B5 seal/harvest tags; no replacement digest |
| Accepted analysis freeze | `tests/b5_analysis/test_frozen_files.py:18`; `:27`–30; `:52`–56 | `b13a510dc15b5e280309f7dd6b280426bf44afc6`; rebind `13af1baa8` | Evolved harvest/bracket bytes read with `git show`; working bracket digest `40fd34bb…fe2a1f2` is separately rebound under DLE-3 | Yes; migrate assertions before deleting main files | `pin/b5-accepted-analysis`; cited-commit tag for rebind in TSV |
| Analysis generations/reference | Existing `b5/analysis*` tags; `RUN_STATE.md` items 83, 88, 93, 160, 165; D-188; `docs/analysis/b5/DEVIATION-LOG.md` | `2fdc0929…`, `081875292…`, `e7eb872d…`, `929fc65c…`, `68e47e1f…`, `ab1e0098…` | Original analysis, r1 oracle, separate 9b-fixed oracle, r2/r3/r4; ruled rebind history | Yes; r1 oracle remains historical even after release | `pin/b5-analysis`, `pin/b5-analysis-r1`, `pin/b5-analysis-r1-9bfix-ref`, `pin/b5-analysis-r2`, `-r3`, `-r4` |
| Actual release binding | `scripts/release_b5.py:270`–285; future release receipt | **Not established by this task** | Record `analysis_commit` must equal explicit pinned commit; seal bytes are loaded at that commit | Yes; release-day blocker until receipt is supplied by lead | Future `pin/b5-release-<receipt-id>` at actual commit, never assumed to be r4 |
| Driver/Git ancestry | `joulewise/b5_analysis/dry_run.py:40`; `joulewise/identity_pins.py:834`–861; `scripts/mint_floor_artifact_generalized.py:1587`–1663 | Every executed analysis and head-pin commit named by its receipt | Clean checkout binding; generalized mint's optional main containment and historical head-pin containment; other receipt publishers also use main ancestry | Yes, on the frozen replay line | Analysis tags above; retain `origin/main` history and receipt commit tags |
| B6 registration | `docs/registrations/block6_freeze_by_commit_addendum.md:3`–6; `block6_replication_DRAFT.md:1194` | `2a4e5149c960af411f3c2fe59debcf168c5a70e8`; machine-test `6849cb7e37ec4a26c237d923efef55d196f5d47d` | REGISTERED document, despite filename DRAFT; SHA-256 `c6a6581e…084034` and S-table | Yes, independent of B5 release | `pin/b6-registration`; `pin/b6-machine-test` |
| B6 collection | `block6_freeze_by_commit_addendum.md:29`; `block6_replication_DRAFT.md:519`, `:1194` | `f31aca19f90473231c41cb31643afb0d6c85d355` | Actual collection code; not contained in main | Yes | `pin/b6-collection` |
| B6 acceptance/estimator/environment | `block6_freeze_by_commit_addendum.md:63`–109 | `5ffbe15c410d0314b18cf5861a5657c35366f156`; `3bb305d7…`; kit `1c1bc320…`; estimator `34bfea7c…`; reference `a434e363…` | Acceptance digest `ea130c87…39ce2a8`, estimator quartet, identity/runtime/model pins, lock and pyproject | Yes; lock is constraints-only, not a fully hashed resolved environment | `pin/b6-acceptance`; `pin/b6-cited-1c1bc3204c8b`; archive tag covers main ancestors |
| B6 executed ledger heads | `block6_freeze_by_commit_addendum.md:132`–142 | `f31aca19f → 6da53f73b → 0a6ab8dc2 → c66bb1ba9 → eab9b45ac → ed22b3d3b → 2a68e0831 → f56d5416b → e7b2875e0 → 20c881075be7530bedea7cca68efdec915388bc3` | Nine executed session identities and final ledger pin; not just code state | Yes | `pin/b6-ledger-final` retains whole chain |
| BYTES registration | `docs/registrations/bytes_freeze_by_commit_addendum.md:3`–7; branch `lane/2026-10-28-bytes-pass2-open:docs/registrations/bytes_pack_v1.md:384`, `:513` | `7b622eb957b3b49a34ca9405ea1384939ed1f0fe`; lane tip `ee4ce93fc7a1e4d77bc54d2085337b122448c334` | Registration absent from main; SHA-256 `1dc6105a…909a5`; dated amendments on main remain separate | Yes | `pin/bytes-registration`; `pin/bytes-pass2-lane` |
| BYTES registered analysis digest | Same branch, `bytes_pack_v1.md:384`, `:444`, `:513`; addendum `:149`–151 | `ee4ce93fc` tree (digest checked here) | `joulewise/bytes_analysis.py` SHA-256 `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`; no inference that a later main version has these bytes | Yes | `pin/bytes-pass2-lane` |
| BYTES frozen manifest | Same branch, `bytes_pack_v1.md:73`–83 | `ee4ce93fc` tree (digest checked here) | `configs/bytes/bytes_manifest.json` SHA-256 `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264` | Yes; preserve as identity, never regenerate from newer weights | `pin/bytes-pass2-lane` |
| BYTES collection states | `bytes_freeze_by_commit_addendum.md:31`–120, `:190`–239 | n1 `6731d524907a9c9f77eb51a5380410a705ffc657`; n2 `8e097d020879c95df9a87f4376cff36abea22ac6`; n3 `e624d67c7ca154c67df77f105b6aa8adcad047a4`; n4 `2649fad54a90aba185368f6035e4acf9e68519b8` | Four actual measurement code states and acceptance/estimator/environment identities | Yes | `pin/bytes-collection-n1` through `-n4` |
| BYTES ledger heads | Addendum `:35`, `:58`–64, `:190`–197, `:236`–239 | Includes `786ecd968`, `30c5dedd7`, all n2 pins, `69bc0c93a`, `f0300a579`, `ba26f0757`, `c7d7cfee6`, `da20a8324`, `f1a55bb40`, final `1aca17e27479946c093bbe20c8cc2faa483a6396` | Actual per-session identities and installs, including ledger-only changes | Yes | `pin/bytes-ledger-final`; every cited intermediate is also in PIN-COMMITS |
| ALIGN v4 identity pins | `lane/2026-11-05-align-pilot10-benign:configs/campaigns/align_v4/registration/identity_pins.json:4`–6, `:22` | anchor `83e2dac59d347f34052f5713280d62ef60bb01d8`; snapshot `9c40e4e5d9fa453cce3c70984e11fa382b7d4591` | Model/runtime identity, tree digest `ba503966…74f4a`; file digest `77600018…33517` | Yes, ongoing; **PROVISIONAL_PENDING_LIVE_GATES** | `pin/align-v4-measurement-snapshot` |
| ALIGN v4 plan/registration inputs | Same branch, `configs/campaigns/align_v4/plan_tree.json:16`–24, `:65`–82; `registration/inputs.json:1`; README `:4`; main `docs/align/council-2026-11-05/FINAL-DESIGN.md:5` | Same measurement snapshot; R1 integration `e901eb2a480d51377a494be9d797733dfcd0220b` | Issued acceptance/ledger, plan/config/order/seed/generator digests and pending inputs | Yes; **PROVISIONAL_SKELETON**, non-claim; design explicitly is not registration/arm authority | Measurement tag plus `pin/align-v4-r1-integration-snapshot` |
| Old process traces | `docs/ARCHIVE.md:10`–15; present snapshot and RUN_STATE citations in TSV | Prior archive `eeea6d5cfac225bfa3609a9ca443eca66918ca2a`; present snapshot | Old trace documents, rulings and main ancestors; off-main cited commits need their own TSV tags | Yes, archive only where no live reader needs working-tree path | `archive/process-traces-before-release-prune-2026-11-08`; retain existing archive refs |

Only `tests/b5_analysis/test_frozen_files.py` matches `tests/**/test_frozen_files.py`
on main. The inspected B6, BYTES pass-2, ALIGN measurement and R1 integration tips
have none under that name. Other freeze assertions still exist under other names
and are covered by the registry, not declared retired by this filename census.
The exact historical error spelling `ref_not_in_origin_main` was not found in
the current driver or inspected `b5/analysis*` driver sources; the concrete
ancestry checks above must still be respected. Do not rewrite frozen B5 code.

The addenda's early “UNRECORDED” sections are followed by appended records. The
B6 ledger line, BYTES n4 and final BYTES line, and B6 kit commit now resolve in
this clone. The appended records, not the earlier pending-tag tables, determine
what can be retained. Neither B6 nor BYTES has an analysis tag established by
these addenda. B5 release does not complete their later gates.

Five RUN_STATE citations explicitly describe commits that are **unavailable in
the local object store**. These are real gaps, distinct from unresolved UUIDs
and external model revisions. Keep their owning records/copies on hold; the lead
must identify their full SHA and recover their Git objects through an authorized
handoff before claiming complete historical retention. This task did not access
the external checkouts or measurement roots mentioned by those records.

| Unavailable citation | File:line | Protects / retention consequence | Live after release? | Eventual tag (only after resolution) |
|---|---|---|---|---|
| `4cb222a19` | `RUN_STATE.md:54` | B5 final pin-only ledger head; collection tag alone does not establish this descendant | Provenance remains live | `pin/b5-ledger-final` at recovered full SHA |
| `050aaad13` | `RUN_STATE.md:949` | Historical pre-merge rehearsal code | Historical; recover or explicitly disposition | `pin/b5-rehearsal-050aaad13` |
| `498ad1d0` | `RUN_STATE.md:2861` | Historical lane-232 stage-A branch head | Historical; owner disposition needed | `pin/b5-history-498ad1d0` |
| `6bcd90a3` | `RUN_STATE.md:2873` | Historical quiet-gate lead commit | Historical; owner disposition needed | `pin/b5-history-6bcd90a3` |
| `9a6f8880` | `RUN_STATE.md:3278` | Historical clone mint head | Historical; owner disposition needed | `pin/b5-history-9a6f8880` |

These pending tags are deliberately absent from TAGS-TO-CREATE.tsv: abbreviated
unavailable names are not executable tag targets. The 1,131-row manifest covers
the resolvable set, not these gaps. Do not equate its passing checks with a proof
that every historical pin has been recovered.

## Digest inventory (retain each existing literal)

[`configs/pins/registry.json`](../../configs/pins/registry.json) is the exhaustive
existing census of SHA-256 literals in `tests/` and `configs/`: 2,635 pinning files,
27,160 literals, 23,594 Kind-P rows and 3,566 Kind-B rows. Its `files[].rows`
give source path + JSON pointer, family and target; `targets` includes
commit-scoped `method@commit:path` identities. This census does not claim to
cover every off-main branch or every hash in narrative docs. The named branch
pins above supplement it. Source locations for resolved commit references are
expanded in PIN-COMMITS.tsv; no target path is followed outside this repository.

| Family / count | File:location | Required commit(s) / protection | Live after release? | Retaining tag |
|---|---|---|---|---|
| `pack_config_bytes` / 19,238 | Registry `files[].rows`, family selector | Plan trees, configs, orders and registrations at snapshot; historical target commit where specified | Keep or retire with entire owning pack and tests | Archive snapshot + each historical target's TSV tag |
| `calibration_issued` / 1,064; `estimator_code` / 78 | Same | Issued acceptance, ledger, battery verdicts and estimator bytes | Yes where any live block consumes them | Archive + B5/B6/BYTES anchors |
| `floor_artifact` / 1,989; `issued_code` / 41 | Same | Floor carriers, old manifest and grammar/module identities | Yes as readers/provenance; old computation can move to tags after migration | Archive + historical-target tags |
| `issued_config` / 795; `pinned_config_copy` / 66 | Same | Current config and test-held copies | Per consumer; no blanket retirement | Archive + applicable block tags |
| `sealed_registration` / 133; `historical_pin` / 47; `recorded_evidence` / 143 | Same | Seals, historical artifacts and recorded evidence identities | Preserve originals; do not repin from a changed HEAD | Archive + applicable commit tags |
| Kind B: `fixture_content` / 3,301; `placeholder` / 157; `source_digest` / 3; `synthetic_literal` / 105 | Same | Synthetic/content-addressed fixtures and non-issued literal checks | Keep with relevant tests; not scientific release pins | Archive snapshot |

The remaining 649 process-trace files survived the earlier prune for reasons
including live readers and authority citations. A release does not itself sever
those dependencies. See [PRUNE-PLAN](PRUNE-PLAN.md) for the migration gates.

## Existing tags — retain unchanged

These are peeled commit targets, not annotated tag-object IDs. They are local
observations, not proof of server protection or backup.

| Existing tag | Peeled commit |
|---|---|
| `archive/pre-prune-2026-11-06` | `eeea6d5cfac225bfa3609a9ca443eca66918ca2a` |
| `b5/analysis` | `2fdc0929d5c214505617145893df2e71ab8a83b5` |
| `b5/analysis-r1` | `081875292a7e1b6592105a612280d8ac4783e2e0` |
| `b5/analysis-r1-9bfix-ref` | `e7eb872d232ab58efe3ff861ae2c33dbfd8c0a33` |
| `b5/analysis-r2` | `929fc65c9ce3ff82f0311d28acf76a682edd466f` |
| `b5/analysis-r3` | `68e47e1f29986cf7cf9df747df37b0fd27043b0a` |
| `b5/analysis-r4` | `ab1e0098dbd0ab839c8f278088221aa8aa4de8d2` |
| `b5/collection` | `c27485347c9629b857df81665b5b1b8d10dcd36a` |
| `b6/collection` | `f31aca19f90473231c41cb31643afb0d6c85d355` |
| `bytes/collection-n1` | `6731d524907a9c9f77eb51a5380410a705ffc657` |
| `bytes/collection-n2` | `8e097d020879c95df9a87f4376cff36abea22ac6` |
| `bytes/collection-n3` | `e624d67c7ca154c67df77f105b6aa8adcad047a4` |
| `bytes/collection-n4` | `2649fad54a90aba185368f6035e4acf9e68519b8` |
| `fixture-d117-v2-production-v1` | `5c781678651ec6d5c46442d1dd6847f03c530583` |


## Limits and release-day refresh

This inventory resolves source references and checks retention topology. It
does not authenticate external copies, current server branches, live hardware,
measurement outputs, a release receipt or a fully reproducible environment.
Before deletion, the lead must disposition any unresolved candidate that is
actually a repository commit pin, refresh references added since this snapshot,
and add the actual release commit. Unknown off-main work remains on hold.

Tags in an alternate-backed clone do not keep the shared object store's GC from
removing objects. Preserve a self-contained Git bundle and install retention refs
in the repository that owns the objects before relying on branch deletion for
retention. Tagging here alone is insufficient.
