# Invocation recoverability audit — C-022 / C-024 / C-025 / C-026 (MET-001, MET-5)

Date: 2026-07-10 (regenerated at PER-INVOCATION granularity, superseding
the 2026-07-09 block-granularity version, per the C-027 docs-tranche
review finding that MET-5 step 5 requires one row per claimed
invocation). Scope: AUDIT TABLE ONLY (spec MET-5 steps 1-5). The step-6
marking pass ("reported, independently unverifiable" addenda on
council-log gate claims) is deliberately NOT executed here — it is
deferred to the lead, per the C-027 spec's open question 5 (the audit
runs first and determines whether any markings are needed at all). Based
on the counts below, few or no markings appear necessary for the direct
codex invocations; the 46 Workflow-tool agents remain the open case.

## Method / provenance

- Claims enumerated from the four run reports (sources cited per block).
- Substrate: the codex-run observer index
  `~/.codex/claude-spawned/index.jsonl`, read 2026-07-10 with
  `encoding='utf-8', errors='replace'` (867 lines at read time; 697
  parsed as JSON; 170 malformed/blank lines skipped; 287 FINISHED events
  across all dates). The index is append-only and grows with ongoing
  sessions, so line totals differ from the 2026-07-09 read (854/684/170).
- FINISHED events dated 2026-07-09 were grouped by (a) the Claude
  session-directory UUID embedded in each row's `out` path
  (`/private/tmp/claude-501/-Users-edr-code-JouleWise/<uuid>/...`) and
  (b) run_key date, then attributed to council sessions by run_key
  naming against each run report's named streams/lenses/gates. The
  grouping reproduces the prior block audit's counts exactly (C-022 50,
  C-024 19, C-025-direct 30, C-026 7).
- 129 FINISHED rows are dated 2026-07-09: 124 attributed below
  (C-022/C-024/C-025-direct/C-026/C-027) + 5 attributed to C-023's four
  rigor lenses and discussion round (listed in an out-of-scope note at
  the end). One further FINISHED row dated 2026-07-10
  (`rev-docs-tranche`, the docs-tranche review in this regeneration
  session) postdates the audit scope and is not tabulated.
- "Surviving evidence" = whether the row's `out` and `log` file paths
  still exist on disk at audit time (`os.path.exists`, checked
  2026-07-10). These live under `/private/tmp` and are NOT durable;
  survival counts are a snapshot.
- Labels (spec MET-5 step 4, applied PER ROW): **recovered** = session
  id AND at least one surviving prompt/output artifact;
  **partially-recovered** = session id XOR artifact; **unrecoverable** =
  neither. The C-025 workflow agents get the narrower label
  **unrecoverable-from-observer-index** (this substrate never recorded
  them; a different substrate may exist — see that block). Nothing is
  backfilled: no reconstructed session ids, hashes, or timestamps
  anywhere in this note.

## Headline

Total claimed delegated invocations across the four audited sessions:
**~120-121 = ~75 direct codex sessions + 46 Workflow-tool agents**,
i.e. the C-027 review's B5 arithmetic made explicit
(`docs/reviews/c027/synthesis-draft.md:36-37`, which rounds it to "~100
claimed delegated invocations"): ~35 (C-022,
run_reports/2026-07-09-cp5-resume.md:134) + ~20 (C-024,
2026-07-09-spec-fleshing-wave1.md:88) + ~60 (C-025 = 46 workflow +
~14 direct, 2026-07-09-spec-fleshing-wave2.md:49,97) + ~5-6 (C-026,
2026-07-09-p2034-broad-packs.md:44 says "~5"; the MET-001 spec
enumerates ~6) ≈ 121.

Audit result, per row (tables below):

| Label | Rows | Where |
|---|---|---|
| recovered | **121** | C-022 50, C-024 19, C-025-direct 27, C-026 7, C-027 18 |
| partially-recovered | **3** | C-025-direct (the three `-C` malformed-run_key rows: session ids survive, out/log files do not) |
| unrecoverable | **1** | C-024 claimed-but-unmatched (the report's ~20 vs 19 index rows; the literal "4 final-head" sub-claim maps to 3 FH-named rows) |
| unrecoverable-from-observer-index | **46** | C-025 Workflow-tool agents WF-C025-01..46 |

The index over-covers the direct claims (124 matched rows vs ~75 claimed
direct + C-027's own runs) because run reports rounded down and omitted
auxiliary runs. Every matched row carries a session id; 121 of 124 also
have surviving out+log artifacts.

## Per-invocation tables

Run_key prefix `20260709ThhmmssZ-<pid>-` encodes the invocation start
time (UTC). "out+log" means both files exist at audit time under the
block's stated path pattern.

### C-022 — CP-5 resume (claim: ~35 codex sessions, run_reports/2026-07-09-cp5-resume.md:134)

50 matched rows ≥ ~35 claimed → every claim covered; all 50 recovered.
C-022 spans TWO Claude session directories (the session was
stopped/resumed): part (a) 16 rows, part (b) 34 rows.

#### C-022(a) — 00:36-03:03, evidence `/private/tmp/claude-501/-Users-edr-code-JouleWise/ae807c57-7163-4f10-8532-42e8cfacdaff/scratchpad/codex/<name>.{md,log}`

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T003607Z-24175-ra-project` | `019f444d-a895-7d41-999a-e1bc0e90f345` | out+log | recovered |
| `20260709T003607Z-24174-ra-calibration` | `019f444d-a896-7b62-a5bd-41dc53f6ddaa` | out+log | recovered |
| `20260709T003607Z-24173-ra-direction` | `019f4365-22ff-7fd0-9a46-ff797c9c1428` | out+log | recovered |
| `20260709T003607Z-24176-ra-closure` | `019f444d-a898-76e3-8fc0-5c3ac682291e` | out+log | recovered |
| `20260709T004053Z-26634-ra-critic` | `019f4452-03cc-77b3-ad76-7d2f508897ed` | out+log | recovered |
| `20260709T012538Z-36136-debate-r1` | `019f447a-fe0f-7802-8c9f-9853d9039d68` | out+log | recovered |
| `20260709T012921Z-37216-review-doc` | `019f447e-621a-72f2-af87-89f2faa8b5c7` | out+log | recovered |
| `20260709T020140Z-39097-bundlepack` | `019f449b-f985-7f00-b85e-0e5e4287f744` | out+log | recovered |
| `20260709T020140Z-39096-strictfix` | `019f449b-f982-79a0-ae2e-a7f52234bcdc` | out+log | recovered |
| `20260709T020140Z-39095-hashcheck` | `019f449b-f987-7323-b4f6-95d26b36d40d` | out+log | recovered |
| `20260709T020140Z-39094-envgate` | `019f449b-f981-7852-9778-744b54343ae1` | out+log | recovered |
| `20260709T021154Z-44995-strictfix-r2` | `019f44a5-56bd-7ec2-99b6-d780ccec3767` | out+log | recovered |
| `20260709T025457Z-54189-methodology-synthesis` | `019f44cc-c358-77d2-87f4-6f1d416228df` | out+log | recovered |
| `20260709T025457Z-54186-envgate-fix` | `019f44cc-c35a-7dd3-ac2c-57cd089d179e` | out+log | recovered |
| `20260709T025457Z-54187-hashcheck-fix` | `019f44cc-c358-7832-bb4b-595e25914baf` | out+log | recovered |
| `20260709T025457Z-54188-bundlepack-fix` | `019f44cc-c35c-7620-bcfd-d92ab3474d67` | out+log | recovered |

#### C-022(b) — 05:24-06:54, evidence `/private/tmp/claude-501/-Users-edr-code-JouleWise/2dd2fc75-1ff8-4985-8da1-f7f354a568bf/scratchpad/codex/<name>.{md,log}`

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T052429Z-97874-pr22-finalhead` | `019f4555-a84b-7790-ae7c-04f93c39915f` | out+log | recovered |
| `20260709T053104Z-99317-pr25-finalhead` | `019f455b-ae4a-7003-bea7-6d0605758d6d` | out+log | recovered |
| `20260709T053104Z-99316-pr24-finalhead` | `019f455b-ae4b-7593-a14c-a3fbf3e54899` | out+log | recovered |
| `20260709T053104Z-99315-pr23-finalhead` | `019f455b-ae49-7c90-bd1b-e4c39a698dd1` | out+log | recovered |
| `20260709T053342Z-1566-advisor-site-review` | `019f455e-18d2-7dc2-8e22-e960c8301288` | out+log | recovered |
| `20260709T053620Z-2622-pr23-fix` | `019f4560-81ef-79c2-953d-3e8143c9ba94` | out+log | recovered |
| `20260709T053620Z-2623-pr24-fix` | `019f4560-81f3-77d0-b504-e6fd0739dbdd` | out+log | recovered |
| `20260709T053620Z-2624-pr25-fix` | `019f4560-81ef-7550-94ce-01a65d966279` | out+log | recovered |
| `20260709T054222Z-10068-pr24-fixreview` | `019f4566-091b-7703-b6b9-0c7b71acf202` | out+log | recovered |
| `20260709T054222Z-10067-pr23-fixreview` | `019f4566-091e-75b2-ba40-7930863983c3` | out+log | recovered |
| `20260709T054222Z-10069-pr25-fixreview` | `019f4566-091e-7973-a029-86e5ab2e10a0` | out+log | recovered |
| `20260709T054604Z-13961-pr25-fix3` | `019f4569-6c57-7a73-a1b5-326d225b7d06` | out+log | recovered |
| `20260709T054604Z-13960-pr24-fix3` | `019f4569-6c57-7982-bb53-b1d255b30eeb` | out+log | recovered |
| `20260709T055301Z-18346-pr24-fix3review` | `019f456f-ca33-7151-8f90-deaf174f2e9c` | out+log | recovered |
| `20260709T055301Z-18347-pr25-fix3review` | `019f456f-ca35-7120-a98c-64f18e582961` | out+log | recovered |
| `20260709T055606Z-21633-pr25-fix4` | `019f4572-992c-7233-b875-3c881b8d93f6` | out+log | recovered |
| `20260709T055606Z-21632-pr24-fix4` | `019f4572-992c-7cd2-b73c-a6c9499ba483` | out+log | recovered |
| `20260709T055301Z-18349-genwide-impl` | `019f456f-ca34-7020-9983-22b54b9357c2` | out+log | recovered |
| `20260709T060009Z-25162-pr2425-finalpass` | `019f4576-518d-7432-b32b-3d45dd54bc89` | out+log | recovered |
| `20260709T055301Z-18350-advisor-impl` | `019f456f-ca36-7762-b072-80d199fbbe2a` | out+log | recovered |
| `20260709T060316Z-28731-integration-review` | `019f4579-2a87-77d1-a004-7447f1bb531d` | out+log | recovered |
| `20260709T055301Z-18348-capture-impl` | `019f456f-ca36-7ee1-a288-5cc163591c47` | out+log | recovered |
| `20260709T061319Z-32594-advisor-lens` | `019f4582-5f02-7cd3-a344-f26b5d5fceaa` | out+log | recovered |
| `20260709T061319Z-32593-genwide-lens` | `019f4582-5f02-7551-a493-39cb67fd3214` | out+log | recovered |
| `20260709T061319Z-32592-capture-lens-tests` | `019f4582-5f05-7ac2-93ee-bb844726119f` | out+log | recovered |
| `20260709T061319Z-32591-capture-lens-bugs` | `019f4582-5f02-7053-bb98-be50b38a0ef0` | out+log | recovered |
| `20260709T061938Z-35402-advisor-fix` | `019f4588-28a0-7770-b50b-50ced99635a9` | out+log | recovered |
| `20260709T061938Z-35401-capture-fix` | `019f4588-28a0-7601-812e-89f6b1110ab6` | out+log | recovered |
| `20260709T063026Z-39327-pr28-finalhead` | `019f4592-0849-70a2-9863-be18143542e7` | out+log | recovered |
| `20260709T063026Z-39326-pr27-finalhead` | `019f4592-0849-7172-911c-84040f5ea933` | out+log | recovered |
| `20260709T063647Z-40978-capture-mergefix` | `019f4597-da1f-7520-b20d-d1394ffd1467` | out+log | recovered |
| `20260709T064048Z-42723-pr27-tailpass` | `019f459b-86b3-7730-8215-5ddab09a63ab` | out+log | recovered |
| `20260709T064515Z-44361-integration-review2` | `019f459f-993c-74b0-9e03-5a0df8eee192` | out+log | recovered |
| `20260709T065146Z-47442-sweep` | `019f45a5-9220-7b70-b558-4058321adf33` | out+log | recovered |

### C-024 — spec-fleshing wave 1 (claim: ~20 codex sessions = 4 impl + 4 lenses + 6 fix rounds + 4 final-head + 1 tail verification + 1 integration review, run_reports/2026-07-09-spec-fleshing-wave1.md:88)

19 matched rows, 07:29-08:16, evidence
`/private/tmp/claude-501/-Users-edr-code-JouleWise/76b483dd-64da-4113-bb7e-9f847179fcbc/scratchpad/<name>.{md,log}`.
The literal sub-breakdown "4 final-head" maps to only 3 FH-named rows
(FH-scope, FH-p2015, FH2-tails), hence one claim-reconciliation row
below.

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T072956Z-55311-S1-scope` | `019f45c8-8324-72b3-8f5a-71ee3e1b0c87` | out+log | recovered |
| `20260709T073033Z-56108-S3-stats` | `019f45c9-1351-7ea3-a7f4-cb10eb34d129` | out+log | recovered |
| `20260709T073017Z-55704-S2-p2015` | `019f45c8-d4c4-7a52-826f-75dc584f0e84` | out+log | recovered |
| `20260709T073050Z-56523-S4-rqreg` | `019f45c9-55b2-7a72-b211-9f2ad2f2e707` | out+log | recovered |
| `20260709T073400Z-57999-R1-scope-review` | `019f45cc-3a76-7662-8a45-0988f4365bef` | out+log | recovered |
| `20260709T073444Z-59244-R3-stats-review` | `019f45cc-e72a-7562-b880-1547ea00fd58` | out+log | recovered |
| `20260709T073521Z-60177-R2-p2015-review` | `019f45cd-79d6-7700-8d4a-154f6779a193` | out+log | recovered |
| `20260709T073715Z-61396-F1-scope-fixes` | `019f45cf-3773-7172-9bf3-a9cd605688cb` | out+log | recovered |
| `20260709T073643Z-60876-R4-rqreg-review` | `019f45ce-bb0c-7be2-9f44-13596a893b29` | out+log | recovered |
| `20260709T073754Z-61836-F3-stats-fixes` | `019f45cf-cf7f-7b20-8787-3ebae0fb78c6` | out+log | recovered |
| `20260709T074103Z-63324-F4-rqreg-fixes` | `019f45d2-b0a5-7c63-af7b-54a01531a539` | out+log | recovered |
| `20260709T074022Z-62916-F2-p2015-fixes` | `019f45d2-11ec-77c1-8b3d-d113125b5c73` | out+log | recovered |
| `20260709T074628Z-66270-FH-scope` | `019f45d7-a710-7a82-8c83-541c20cec300` | out+log | recovered |
| `20260709T074635Z-67216-FH-p2015` | `019f45d7-c18a-7de2-88e5-12b7d3e18b35` | out+log | recovered |
| `20260709T074957Z-75196-F5-p2015-tail` | `019f45da-d832-7a91-afbf-81aecab8efc2` | out+log | recovered |
| `20260709T075257Z-75846-FH2-tails` | `019f45dd-9635-7891-a8ea-861d866bda84` | out+log | recovered |
| `20260709T080333Z-77628-INT-review` | `019f45e7-48ea-7dc3-91c8-b2161d5c7219` | out+log | recovered |
| `20260709T080705Z-79575-F6-integration-fixes` | `019f45ea-87f7-70c1-be49-7f7558ab54ab` | out+log | recovered |
| `20260709T081221Z-80427-SWEEP` | `019f45ef-5a56-7bf3-b00d-a062cc8fce1f` | out+log | recovered |

Claim reconciliation (claimed > matched):

| Placeholder | Claimed as (source) | Session id | Surviving evidence | Label |
|---|---|---|---|---|
| `C024-claimed-unmatched-01` | 4th final-head of "4 final-head" in the ~20 breakdown (wave1.md:88) | none in index | none | **unrecoverable** |

### C-025 (direct) — spec-fleshing wave 2 (claim: ~14 direct codex sessions, run_reports/2026-07-09-spec-fleshing-wave2.md:97)

30 matched rows ≥ ~14 claimed → every direct claim covered; 27
recovered, 3 partially-recovered. Window 08:35-10:05. Evidence pattern
as C-024, EXCEPT the three `-C` rows, whose out/log paths were mangled
CLI arguments (`/Users/edr/code/JouleWise/-C`, `-C.log`) and no longer
exist (nor does any content under those names).

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T083507Z-84081--C` | `019f4604-2f2c-7c41-98f1-313974702ec4` | none (session id only) | **partially-recovered** |
| `20260709T083641Z-85625--C` | `019f4605-a028-7203-8f7f-d5c4a6ebea18` | none (session id only) | **partially-recovered** |
| `20260709T083619Z-85054-p2031-redteam` | `019f4605-49e8-7d91-86ca-3bb17fbe1571` | out+log | recovered |
| `20260709T083729Z-86861-codex-p2031-review` | `019f4606-5968-7f02-ae9b-97e7643f5a00` | out+log | recovered |
| `20260709T084358Z-89363-codex-ap-review` | `019f460c-4b26-7170-bec2-9732ca87f0cd` | out+log | recovered |
| `20260709T084728Z-91286--C` | `019f460f-7df4-7e10-a9cf-4ff69c75f8f6` | none (session id only) | **partially-recovered** |
| `20260709T084704Z-90757-S10-rqvar` | `019f460f-206d-7ed3-b4b8-d92be29c3357` | out+log | recovered |
| `20260709T084824Z-92141-p2032-exec-audit` | `019f4610-59de-7f22-a237-f16d4faf7519` | out+log | recovered |
| `20260709T084639Z-90223-S9-linter` | `019f460e-bf41-7240-9a01-19efc0722542` | out+log | recovered |
| `20260709T085351Z-97379-R9b-linter-tests` | `019f4615-57e2-7af1-84ea-87748f13bfaa` | out+log | recovered |
| `20260709T085341Z-96980-R9a-linter-correctness` | `019f4615-2eac-7a02-b137-3efaf55bbc08` | out+log | recovered |
| `20260709T085652Z-99748-F9-linter-fixes` | `019f4618-1b2f-7e71-b078-b56c4f454b95` | out+log | recovered |
| `20260709T092514Z-25835-W2F-p2031` | `019f4632-12b4-7772-89cb-a80567850e34` | out+log | recovered |
| `20260709T092456Z-25070-W2F-p2029` | `019f4631-ccd2-7e83-bb08-da90159acff6` | out+log | recovered |
| `20260709T092525Z-26234-W2F-p2032` | `019f4632-3d83-7d40-bc37-d29646cc1886` | out+log | recovered |
| `20260709T092504Z-25449-W2F-p2030` | `019f4631-ec93-7b43-a7cb-c0abd3e33092` | out+log | recovered |
| `20260709T093404Z-32310-FH2-p2032` | `019f463a-2778-7e82-9a6c-0597977697b5` | out+log | recovered |
| `20260709T093347Z-31169-FH2-p2029` | `019f4639-e60e-71e2-8c56-a48234d0fb93` | out+log | recovered |
| `20260709T093358Z-31924-FH2-p2031` | `019f463a-11d4-78b3-9c00-f6900a4b2718` | out+log | recovered |
| `20260709T093417Z-33094-FH2-rqvar` | `019f463a-5bc8-7a11-8497-7c7fa672e7dd` | out+log | recovered |
| `20260709T093352Z-31546-FH2-p2030` | `019f4639-fbed-7e43-bdce-0f3b624be1a6` | out+log | recovered |
| `20260709T093413Z-32696-FH2-p2033` | `019f463a-4cd7-7f11-b6e7-41261a7a05b0` | out+log | recovered |
| `20260709T093717Z-34911-W2T-rqvar` | `019f463d-1c4a-7502-a95f-9da493d79b7d` | out+log | recovered |
| `20260709T093631Z-34194-W2T-p2029` | `019f463c-65e7-7a91-a6b0-e4e1e27b7a57` | out+log | recovered |
| `20260709T093752Z-35537-W2T-p2030` | `019f463d-a562-76e3-b0a7-2d69489d0faf` | out+log | recovered |
| `20260709T093839Z-36551-W2T-p2033` | `019f463e-5ae0-7313-a577-4f1688c3b67f` | out+log | recovered |
| `20260709T094324Z-41830-W2-TAILVERIFY` | `019f4642-b2be-7871-b898-bb30ba5da8f8` | out+log | recovered |
| `20260709T095046Z-44523-INT2-review` | `019f4649-7453-7170-ab1d-9620ba5bd391` | out+log | recovered |
| `20260709T095551Z-45902-INT2-fixes` | `019f464e-19a6-7871-bbf9-9a16f6a66604` | out+log | recovered |
| `20260709T100157Z-48206-SWEEP2` | `019f4653-ae7c-79a0-bccb-c9c4ed1bcadb` | out+log | recovered |

### C-025 (workflow) — 46 Workflow-tool agents (claim: 46 agents, ~1.87M tokens, run_reports/2026-07-09-spec-fleshing-wave2.md:49)

The observer index records codex-run invocations only; it was never
designed to record Workflow-tool subagents, and no index rows are
attributable to them. Each agent is therefore enumerated as a
placeholder row (spec MET-5 step 1: count-only claims become
`<session>-unnamed-NN`), labeled **unrecoverable-from-observer-index**
— narrower than plain "unrecoverable" because a potential substrate WAS
found and NOT verified: the Workflow task-output directory
`/private/tmp/claude-501/-Users-edr-code-JouleWise/76b483dd-64da-4113-bb7e-9f847179fcbc/tasks/`
(the C-025 session directory) held 86 `*.output` files at audit time
(ls-level probe only). A journal for these agents may exist at that
path, unverified; matching those files to the 46 claimed agents is
follow-up work, not asserted here.

| Placeholder | Session id | Surviving evidence | Label |
|---|---|---|---|
| `WF-C025-01` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-02` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-03` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-04` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-05` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-06` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-07` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-08` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-09` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-10` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-11` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-12` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-13` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-14` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-15` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-16` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-17` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-18` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-19` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-20` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-21` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-22` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-23` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-24` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-25` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-26` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-27` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-28` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-29` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-30` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-31` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-32` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-33` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-34` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-35` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-36` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-37` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-38` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-39` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-40` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-41` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-42` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-43` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-44` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-45` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |
| `WF-C025-46` | none in observer index | unverified (see note above) | unrecoverable-from-observer-index |

### C-026 — P2-034 broad packs (claim: ~5 codex sessions = design, implement, 2 lenses, fix, final-head, run_reports/2026-07-09-p2034-broad-packs.md:44; spec enumerates ~6)

7 matched rows ≥ ~5-6 claimed → every claim covered (one-to-one run_key
match plus WRAP-meeting beyond the listed breakdown); all recovered.
Window 16:35-17:22, evidence pattern as C-024.

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T163543Z-51903-P34-design` | `019f47bc-32c9-77d3-9ccb-e457120fdcc4` | out+log | recovered |
| `20260709T163833Z-52636-P34-impl` | `019f47be-c815-79a3-a6e2-15858574fe5e` | out+log | recovered |
| `20260709T165138Z-54259-R34a-exec` | `019f47ca-c415-7992-b294-ee927db7c559` | out+log | recovered |
| `20260709T165146Z-54641-R34b-compliance` | `019f47ca-e386-7343-ab4a-c58050638ee6` | out+log | recovered |
| `20260709T165554Z-55453-F34-fixes` | `019f47ce-aa13-7902-93cc-e989f800795d` | out+log | recovered |
| `20260709T170023Z-56131-FH34` | `019f47d2-c778-7970-abe7-32dcc278aec3` | out+log | recovered |
| `20260709T171853Z-59201-WRAP-meeting` | `019f47e3-b681-7883-83de-496c4f64694b` | out+log | recovered |

### C-027 — this review session's own invocations (final block; not part of the ~121 audited claims)

18 FINISHED rows dated 2026-07-09T20:32-21:46 in the C-027 session
directory, evidence
`/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/<name>.{md,log}`.
These are already mirrored in the tracked manifest; listed here so the
audit's substrate coverage is complete. All recovered (`sol-smoke`'s out
file was never written — the smoke run failed and was rerun as
`sol-smoke2` — but its log survives, which satisfies the recovered
definition; noted rather than hidden).

| Run key | Session id | Surviving evidence | Label |
|---|---|---|---|
| `20260709T203201Z-61735-sol-smoke` | `019f4894-8785-7ab2-bf8a-22e92e41126f` | log only (out absent) | recovered |
| `20260709T203316Z-63120-sol-smoke2` | `019f4895-aec2-7562-89a4-41f69b35b1db` | out+log | recovered |
| `20260709T203549Z-67775-lens-negspace` | `019f4898-00da-7ed0-ad7c-8ab9b305e186` | out+log | recovered |
| `20260709T203430Z-64485-lens-topdocs` | `019f4896-cdfd-7120-b959-4c851cb68099` | out+log | recovered |
| `20260709T203457Z-65741-lens-stats` | `019f4897-368b-7433-ab5f-f61c284e81ad` | out+log | recovered |
| `20260709T203510Z-66146-lens-meta` | `019f4897-693c-7553-b107-f3df655e313a` | out+log | recovered |
| `20260709T203524Z-66829-lens-reverse` | `019f4897-9ff6-7632-9de7-9e1f7d64eaf0` | out+log | recovered |
| `20260709T203537Z-67330-lens-arch` | `019f4897-d398-7f40-b73a-a155fd229fc5` | out+log | recovered |
| `20260709T203447Z-65313-lens-rigor` | `019f4897-0f75-7bf0-8e3d-480442e392a4` | out+log | recovered |
| `20260709T205039Z-76953-counterreview` | `019f48a5-9592-77e0-b5a2-f2b2939f7dac` | out+log | recovered |
| `20260709T211457Z-87034-sweep` | `019f48bb-d755-7420-a80e-de7215fa4bcf` | out+log | recovered |
| `20260709T212750Z-89542-finalhead` | `019f48c7-a231-7781-b45e-8afe00a22a41` | out+log | recovered |
| `20260709T212854Z-90360-spec-p2038` | `019f48c8-9c6b-7870-b115-cbe5ee6afbf8` | out+log | recovered |
| `20260709T212944Z-91701-spec-rpt001` | `019f48c9-6157-75f0-875a-a5096622f6b5` | out+log | recovered |
| `20260709T212908Z-90763-spec-p2039` | `019f48c8-d340-7e22-bfed-09fc1889ebee` | out+log | recovered |
| `20260709T212840Z-89964-spec-p2040` | `019f48c8-650e-70e2-8e41-f67f5c232294` | out+log | recovered |
| `20260709T212928Z-91246-spec-engine` | `019f48c9-21cf-73f0-a1dc-6a37771747c7` | out+log | recovered |
| `20260709T213002Z-92188-spec-doc008` | `019f48c9-a7a1-7b80-b666-0125e8a25541` | out+log | recovered |

## Out-of-scope note — C-023 rows in the same session directory

Five FINISHED rows dated 2026-07-09T07:09-07:13 share the 76b483dd
session directory but precede C-024's window and match C-023's recorded
shape (4 rigor lenses + 1 discussion round, council_log.md C-023 entry):
`L1-metrology`, `L2-benchmark-stats`, `L3-question-bank`,
`L4-advisor-sim`, `D1-discussion` — all with session ids and surviving
out+log. C-023 is not in this audit's claimed-invocation scope; they are
noted so the 129 dated-2026-07-09 FINISHED rows are fully accounted for
(124 tabulated above + these 5).

## Cross-links

- D-031 breach addendum (MET-1): `docs/decision_log.md`, end of the
  D-031 entry.
- D-050 stop-card override addendum (MET-3): `docs/decision_log.md`,
  end of the D-050 entry.
