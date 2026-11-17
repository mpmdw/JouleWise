# Qualification and STANDING-F0 r2 drafts — 2026-11-16 PST

**DRAFT / HOLD_FOR_FIT_FREEZE. Nothing issued.** Builder works only in `item-drafts-1118/`; no MBP/SSH, main/RUN_STATE edit, real measurement/energy/power/meter/transcript/custody read, or full suite. Inputs: prior 1115 then f2 drafts, RL-149/155/165/167/169/171/172/172a/173, fetched main `8fd5c8cc5` items 346/367/372/374/375, #794 source `6010985a3`. All execution evidence is synthetic or read-only source/config validation.

| Item | t0-date window, PST (00:00:00–23:59:59) | Forecast t0: freeze Thu19 12:00 / slip Fri20 12:00 | Expected / work-worst close at those forecast starts | Exactly missing before issue; owner |
|---|---|---|---|---|
| qual01-s01 | Thu19; slip requires Fri20 re-date | Thu19 12:00 / Fri20 12:00 | Thu15:24:22 / Thu18:52:30; slip Fri same times | Lead: freeze2 commit/coefficient path/hash, per-kit admission pointers and exact line2 equality, pre-freeze host event/state, queue commit/staging, prior dev-05-s02 confirmation, lines6/7/9 and issue fills. Research lead: Q2 below (Q1 only if sharing dates). Magistrate: live arm observations. Builder: no remaining prerequisite after verification. |
| qual01-s02 | Thu19; slip Fri20 | Thu19 15:29:22 / Fri20 15:29:22 | Thu18:54:32 / Thu22:21:52; slip Fri same times | Same shared prerequisites; lead also records qual01-s01 soak/reference-schema hand comparison SAME against dev-05 (RL-172a F1), then issues inside three-ahead/24 h limits. Magistrate checks predecessor clean at arm. |
| qual02-s01 | Fri20; slip Sat21 | Fri20 00:00 / Sat21 00:00 | Fri03:24:22 / Fri06:52:30; slip Sat same times | Shared prerequisites, qual01 soak hand record, qual-02 cold seat pointer, dated queue/staging and own issue/watch fills (lead). Predecessor qual01-s02 clean at arm (magistrate); actual k−2 desk + typed Q1 debt paid (lead). |
| qual02-s02 | Fri20; slip Sat21 | Fri20 03:29:22 / Sat21 03:29:22 | Fri06:54:32 / Fri10:21:52; slip Sat same times | Same, with predecessor qual02-s01; own issue/watch fills and actual cross-block debt (lead); all fresh operational checks (magistrate). |
| qual03-s01 | Sat21; slip Sun22 | Sat21 00:00 / Sun22 00:00 | Sat03:25:10 / Sat06:52:30; slip Sun same times | Shared prerequisites, qual01 soak hand record, qual-03 cold seat pointer, dated queue/staging and own issue/watch fills (lead); predecessor qual02-s02 and fresh checks (magistrate); actual k−2 desk/Q1 debt (lead). |
| qual03-s02 | Sat21; slip Sun22 | Sat21 03:30:10 / Sun22 03:30:10 | Sat06:54:32 / Sat10:22:40; slip Sun same times | Same, with predecessor qual03-s01; own issue/watch fills and actual cross-block debt (lead); fresh checks (magistrate). |
| STANDING-F0-r2 | Valid Sun22 11:51:24 through before Sun29 11:51:24; daily launch 02:35–22:40 | ≥Sun22 11:51:24 in either case, subject to live ladder/ledger | At that start: ~13:51:24 / 15:14:24; shared desk deadline 15:51:24 | Lead issues at planned start (later issue needs re-dating), rechecks current W1 head/hash qualification and any hold; magistrate checks all standing triggers/spacing/day/restore/copy/READY gates. Optional hold is inactive until lead issues it. |

Forecast assumptions: dev-05-s02 closes Wed18 ~07:00; all operational/desk/admission records ready at the assumed freeze; no intervening F0/F2/v4 occupation. Expected successors use expected close +300 s. Worst-close cells are **each span's work bound from its forecast start**, not a promise all six start at those times under worst cases. qual01-s02 after both first spans' work-worst durations would instead start Thu18:57:30 and close Fri01:50:00; qual02-s01 then waits for the actual fence/copy/close interval. F0/F2/non-campaign close adds 1,200 s. Actual fence disappearance and every gate govern.

Planner expected sums: 24,572 s per block, 73,716 s (20:28:36) over six spans, plus three internal 300 s gaps and date waits. Each work bound is 24,750 s (6:52:30); **launcher minimum 27,260 s** adds 1,950 s retry +560 s reserves; items allow +900 s start slack (28,160 s desk deadline). A shared desk fence remains; "no fence" means no clock-based launch fence. `evidence/plan-*.json` contains the six actual pinned plans.

## Frozen facts and admission

| Block | Exact kit SHA-256 | Law spans / short leg | Expected s, s01 / s02 |
|---|---|---|---|
| qual-01 | d125491feec1fc95ca962c6e7ea5d50d8d93634639c5a55417c93cb2c710c5be | L001–L006 / L007–L012; L004=3151, L010=3724 | 12262 / 12310 |
| qual-02 | d7dadff85b1bde79053b9e89a6533fe9b64a098250144f4f2578494db03d36bb | L001–L006 / L007–L012; L003=3151, L011=3724 | 12262 / 12310 |
| qual-03 | 94f20d749faee96e461431b3d420784ebb975498fbd3abb367401b4819b48bc8 | L001–L006 / L007–L012; L003=3724, L010=3151 | 12310 / 12262 |

Kit source `6010985a3312c77bb8e4bb4bf5c920c4d49b8512`; frozen checkout **`e1b85a59c53bfbeaa3477df46bcbe9dd8fdfc427`**, runner `cadence-legs-v1.1`; W1-line commit actually merged **`c3f4bacd8013ca98c19cf8d41f830c701930cd41`**. Seeds 2026111422/23/28. Every span captures at its first own-shaped leg (L001/L007), five span-shaped consumers; one A cell at 2k, one at 10k, two at 19458 plus an adjacent 19458 L pair. No class A smoke (RL-165 §8.1; RL-172a). No `--batch-window` argument, no clock exclusion/fence at this pin; plan/launcher-plan probes include the retired midday and night boundaries. Kits never re-pin on a later W1 merge.

No qualification span queues are on #794's source branch; `BLOCK-QUEUE.json` is a block ledger, not a span queue. Three finite queues are drafted **only here** and validated against the pinned law. Their expiry is Nov23 00:00 PST, ≤7 days after a Nov16 commit, checked against the authenticated queue commit at arm (RL-149 §2.8 line3). They grant no authority. No builder writes a READY/cold-seat/CI admission stamp; those record pointers remain lead fills. Full placeholder and observation shapes: [record-shapes.md](evidence/record-shapes.md).

F0 renewal: item346 ISSUED Nov15 11:51:24 +7 days = **Nov22 11:51:24 PST, epoch1795377084**. Planned renewal ends Nov29 11:51:24, epoch1795981884. Fetched W1 head remains **`b2e01464d6d4fbf2901ff4d4154df9455104a12a`**; main's item346 still names it. Pin/hash table/launch/Check rules carry unchanged; four-hour spacing, three per date, 02:35–22:40 latest-launch rule and 1,200 s after F0 persist. Existing ledger continues across renewal. Diff: [standing-f0-r2.diff](evidence/standing-f0-r2.diff). The optional item374-form hold uses lead fills; item374's Mon16-only hold is not carried forward.

## OPEN QUESTIONS for the research lead

**Q1 — qualification cap on a shared t0-date.** Exact question: "Does RL-149 §2.3's two-blocks-per-day rule cap qualification at 24 legs and two qualification blocks on one t0-date, with the two block starts at least 10 h apart, or does RL-172 (a) leave qualification without a numeric per-date cap while requiring at least two non-development dates?" Options: (A) explicit 24 legs/two blocks and 10 h separation; (B) the explicit 24-leg cap applies only to development, qualification otherwise only needs two disjoint dates. Recommendation: A until ruled; default one block/date never depends on sharing. Blocked: admitting a less restrictive shared-date plan. Builder drafts the conservative reading and day_gate prints its rule; no ruling is invented.

**Q2 — qualification maintenance flags at freeze 2.** Exact question: "Under RL-171 §5 item3, do maintenance flags join qualification's inclusion rule at freeze 2, or do the pinned six rules remain unchanged with maintenance overlaps print-only?" Options: (A) unchanged six rules, print overlaps and retry counts; (B) a prospectively specified maintenance-flag inclusion rule, with its exact text and any required kit/manifest disposition. Recommendation: A only if the counted evidence justifies it; otherwise the research lead specifies B before any qualification leg. Blocked: issue/arm until that disposition is recorded; these drafts WAIT on an unfilled INCLUSION_RECORD and conservatively do not alter the kit. Lead owns delivering the by-job counts of flagged development legs that passed rule5; research lead owns the decision. This builder opens none of those data.

## Verification and reproduction

Targeted source/config and synthetic checks only; no canonical suite because production runner/kit/frozen paths are unchanged and the request explicitly forbids it. Totals: **1092 gate, 91 pinned, 21 F0, 6 generator, 74 shell syntax and 60 Python compile checks; all pass**. Logs and full totals: `evidence/lint.log`, `pinned-checks.log`, `gates.log`, `standing-f0-tests.log`, `redate-tests.log`; pinned re-check detail in `kit-recheck.json`. Read-only fresh peer review and lead disposition are recorded in `evidence/review.md`; this builder retains final diff/verification responsibility.

```sh
cd docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118
python3 -B build_items.py
bash tests/run_all_gates.sh
```

For the freeze-2 slip, the lead regenerates all six items/queues/plans with one argument, commits the new bytes and re-issues (never silently reuses Thursday's item):

```sh
python3 -B build_items.py --dates qual-01=2026-11-20,qual-02=2026-11-21,qual-03=2026-11-22
```

Fetch the source refs first if absent. The generator extracts only allowlisted Python/shell source and two configs into a disposable directory **inside this folder**, never a worktree or measurement root. Runner tests create labeled synthetic Git coefficients/queues and mock spans there, then remove them. Both bash and zsh are required. Next exact step: lead records Q2 (Q1 is needed only to loosen the conservative shared-date rule), commits freeze2 coefficient file, supplies admission/host/queue/operational pointers, stages on a clean close, and issues only the next ≤3 spans inside their 24 h windows; magistrate alone runs the issued native item.

## Close-census repair — 2026-11-16

All unissued item copies now select the latest close by the receipt's recorded `ended.epoch_s`, never filesystem mtime. Identity is chosen before ceiling to whole seconds; missing/unreadable/invalid stamps and equal latest epochs stop. The exact selected campaign span's marker remains mandatory. The non-campaign Check rule is unchanged. Generators carry the same repair; the 1118 standing-F0 renewal is included. Earlier test captures and source-item evidence are preserved.

New tests execute the embedded functions in bash and zsh, keeping an older receipt's bytes unchanged while giving it a later mtime; its marker cannot authorize a newer uncopied campaign. The actual latest marker passes. New evidence lives under `evidence/fix-2026-11-16/{bash,zsh}/`; the current standing renewal's derivative comparison is `evidence/fix-2026-11-16/standing-f0-r2.diff`. See `docs/run_reports/2026-11-16-f2-item-fixes.md` for results and the issued-item assessment. This repair issues no item and clears no live prerequisite.
