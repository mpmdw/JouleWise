# DRAFT — Block-5 r2 analysis-program addendum

Written **2026-11-05**, before the release event, in a blind release-readiness
writing session. **DRAFT; not an adopted pin, release event, or GO.** The lead
must review and append the adopted record to
[`SEAL_RECORD.md`](../process_traces/2026-10-07-block5-seal/SEAL_RECORD.md)
before the event. This file does not change that record or any sealed document.
It does not assert that an analysis-program addendum existed earlier.

Writing seat: Codex, local branch `lane/2026-11-05-b5-release-readiness`.
This seat has read no real claim-window energy or study custody. Its execution
evidence uses only repository-generated synthetic S10 windows. Existing
absolute custody paths in source documents were treated as text. The seat's
attributed identity for the adopted seal entry: **LEAD-FILL**.

Authority: registration §8 (release/readers), §11 item 4 (blind authorship,
files and SHA-256s, desk commit, pin before release), §12 (append-only record
and manual verification); analysis plan §3.2 and §11; decision-log
[D-188, D-189 and D-190](../decision_log.md#d-188-block-5-analysis-rewrite-under-result-equivalence-engineering-window-fresh-analysis-start-ed-2026-11-02).
The seal record's §7 convention requires date and writing seat. The proposed
number/title of the adopted addendum: **LEAD-FILL**.

## Proposed analysis pin and oracle

These identities were computed from this clone's Git objects on 2026-11-05;
tag-object identity is included separately from the peeled commit. All four
tags are annotated. No tag was created, moved, or fetched in this session.

| Role / tag | Commit | Tree | Annotated tag object |
|---|---|---|---|
| First analysis tag, `b5/analysis` | `2fdc0929d5c214505617145893df2e71ab8a83b5` | `ea994f30a109123cffe19e1b064e1593928f16b3` | `8b8aa535898142470426050e8b4b2ef64e593e3a` |
| Pre-rewrite revision, `b5/analysis-r1` | `081875292a7e1b6592105a612280d8ac4783e2e0` | `674c2783f8d40c450a7b7afefab5913d17c00e51` | `9ae60f7274e626f65c36b37b3dc97017424c2118` |
| Equivalence oracle only, `b5/analysis-r1-9bfix-ref` | `e7eb872d232ab58efe3ff861ae2c33dbfd8c0a33` | `de2e980edecf9047efd5c86dd4f31488a6d5a739` | `57bd0af630297a9557adcd307d9d8b912195835d` |
| **Proposed release program, `b5/analysis-r2`** | **`929fc65c9ce3ff82f0311d28acf76a682edd466f`** | **`9e89d7ff48999416467129c03ea171fc3a1f3f83`** | `bdaf0c03e74b6fc824e16f607122c0738dab0eb7` |

Proposed pin (draft text, not an installed seal-record pin):
`B5-ANALYSIS-PIN: 929fc65c9ce3ff82f0311d28acf76a682edd466f`.
The reference branch is an oracle and is never merged. Actual release desk
checkout locator and clean/detached identity verification: **LEAD-FILL**.

## Named files and SHA-256s

The companion [draft file inventory](b5_r2_analysis_program_files_DRAFT.json)
names **315 files**, with SHA-256s computed from `git show
b5/analysis-r2:<path>` bytes. Its own SHA-256 is
`fe7268c7012214d23360b50e6ca0fd1b81bacd752fd7377c6659fed7567a7c4e`.
It covers every tracked Python source under `joulewise/` and `scripts/`, every
file under `configs/analysis/b5/`, `pyproject.toml`, and
`env/analysis-lock.txt`. This is an intentionally overinclusive source envelope,
including programs not executed by block 5; it is not an observed import census.
The full tree identity above also binds all other tracked files, including
sealed campaign configurations. The lead's adoption of this inventory and
verification against the actual checkout: **LEAD-FILL**.

Selected entries, copied from that inventory:

| File at r2 | SHA-256 |
|---|---|
| `scripts/run_b5_analysis.py` | `3ae7151a06628405b4f30561bd53e946a68f1ad323b8b67a737103c87f6915e0` |
| `joulewise/b5_analysis/dry_run.py` | `7a184361274f071cb2d33e648043c428bf04cddd282e2e12f2446ab82bf98a4d` |
| `joulewise/b5_analysis/sensitivity.py` | `3197b6bd970a3868b288ebbce967808ba7d1a55d95a47d5eb46a05d60325c4bf` |
| `joulewise/b5_analysis/disclosures.py` | `039f0d20ebb920b09acb77bbfe71c96ee4ef1cbe172f472e66c4fec18258bae5` |
| `env/analysis-lock.txt` | `f1d6073d2815a9e8370d3462cc015e2d747266412a97664388cb1a3fdd31196b` |

Reproduction (read Git objects only):

```sh
git rev-parse 'b5/analysis-r2^{commit}' 'b5/analysis-r2^{tree}'
git rev-parse 'b5/analysis-r1-9bfix-ref^{commit}' 'b5/analysis-r1-9bfix-ref^{tree}'
git cat-file -t b5/analysis-r2
git cat-file -t b5/analysis-r1-9bfix-ref
git show b5/analysis-r2:joulewise/b5_analysis/dry_run.py | shasum -a 256
```

Environment actually used for the study runs (Python minor/patch, dependency
lock verification, OS/toolchain, VDL selection and provenance record):
**LEAD-FILL**. Naming the tracked lock above does not attest that a study run
used it. No installation or upgrade was performed by this writing seat.

## What is being rebound

The sealed plan §11 anticipated post-seal implementation of exclusions-aware
selection, kept-unit floor extraction and issuance, GAMMA manifest binding,
NEG-8 survivor consumption, mint/closeout adapters, disclosures and fill input.
The analysis tags identify implemented programs; the sealed plan itself is not
an executable baseline. The first tag and r1 above give the historical code
anchors. Full disposition of the plan's FILL markers, the intervening L9 fixes
and their review/authority records: **LEAD-FILL**. This draft does not imply
that D-188 alone authorized every earlier L9 change.

The r1-to-r2 changes addressed here are:

1. **D-188 (2026-11-02): result-equivalent rewrite.** Shared authenticated
   input, reduction and physics caches; content-hash verification by independent
   consumers; the verified-data store; worker dispatch and phase timing reduce
   repeated work. The driver, archive/bracket consumers, whole-window
   authentication, floor extraction, mint/closeout paths and input validation
   participate. Scientific numbers must be exactly equal to the oracle and
   admit/refuse/select decisions identical. Audit records may differ. The
   independent *arithmetic* recompute's tolerance bars do not relax this exact
   rewrite-equivalence requirement. D-188 also authorizes a fresh analysis start.
2. **D-189 (2026-11-04): step 9b non-issuance.** The narrow
   `claim_side_bound_not_issuable` outcome has one non-stopping `outcome_class`
   row, no outputs or flags, and permits steps 10/11 to run. Exit 3 is an
   outcome, while tooling refusal still stops. No claim-side-bound sidecar or
   claim-evidence custody is fabricated. A paper fill requiring
   `VerifiedClaimEvidence` still refuses. The same change is backported to the
   oracle, so the comparison does not pit different outcome policies against
   each other.
3. **D-190 (2026-11-04): carry registered null outcomes through step 11.**
   `sensitivity.py` and `disclosures.py` preserve nulls for the engine's
   not-resolvable floor and not-estimable contrast, printing their registered
   state. Shapes previously accepted keep their bytes. Unexpected nulls and
   inconsistent shapes still refuse. Engine arithmetic and the claim-side-bound
   producer are unchanged by this fix. It is backported to the oracle.
4. **D-188 comparator correction (PR #643).** Commit-derived composite
   digests are compared through verified referents at their own leaf tiers;
   they are not accepted as arbitrary differing digests. Strict timing policy
   remains. This is distinct from the independent-recompute comparator.

The existing seal-record deviation of 2026-10-20 remains: step 11 ends at the
validated `results-fill-input.json`; no block-5 Results renderer is delivered
by release. This addendum does not change any collection/harvest pin, sealed
document, estimator, threshold, exclusion, attempted-window selection or input.

## Evidence to complete before adoption and release

Every unresolved field is explicitly **LEAD-FILL**. No study comparator verdict
or run identity is inferred from the task handoff, historical prose, a tag, or
synthetic acceptance.

| Required evidence | Value |
|---|---|
| Final oracle run id, custody record path/digest, terminal status and complete through-11 sequence | **LEAD-FILL** |
| Final r2 dry-run id, custody record path/digest, terminal status and complete through-11 sequence | **LEAD-FILL** |
| Exact window index digest, immutable input/ledger/attempt bindings | **LEAD-FILL** |
| Independent rewrite-comparator checkout commit, code/config hashes and invocation | **LEAD-FILL** |
| Fresh blinded comparator verdict, exit code, verdict-record digest and full-run coverage | **LEAD-FILL** |
| Review evidence and dispositions, including the applicable L9 executing reviews | **LEAD-FILL** |
| Independent arithmetic recompute/comparator versions, block-5 bars, run ids and agreement record | **LEAD-FILL** |
| Lead disposition of recompute-before-event versus results-gate ordering (runbook gap 5) | **LEAD-FILL** |
| Named post-release reader and owner of every printed uncovered leaf | **LEAD-FILL** |
| Applicable seal/errata and final harvest-record digests for each analysed pack | **LEAD-FILL** |
| Actual blind statements of repair authors and reviewers, with attributed seats | **LEAD-FILL** |
| Adoption date/time, adopting lead and final seal-record addendum pointer | **LEAD-FILL** |

The release event remains a separate lead-authored entry under registration §8.
Its time, readers, bindings and subsequent r2 release-run equality evidence are
**LEAD-FILL**, to be recorded at the event and after the release run respectively,
never backdated into this pre-event draft. This writing session establishes no
real-data equivalence, independent-recompute agreement, release or unblinding.
