# Paper 1 seat 9 — Sol source review

Date: 2026-11-11. Reviewer: local Sol seat `p1-seat9-review`.
Candidate: `docs/2026-11-11-paper1-automation` at `4d2a9050ff5ce52cacfcdafadde5baa5c21edef0` (draft PR #715).
Comparison base: local `origin/main`, `62a87aaad3e3b2bf0d7f61e534a5b87b0c51a642`, also the merge base.

**Overall: ADMIT-WITH-FIXES.** The per-collection arming account and the Block-5 stop / Block-6-and-BYTES pause correction are supported. The section still contains an incorrect exclusion summary, an overbroad replay chronology, and an unsubstantiated clock-history disposition. Two claims that no source was found need correction. This is a review recommendation; the research lead retains admission authority. No manuscript, generator, coordination-state or evidence file was edited.

## Required fixes

1. **§7.2 item 3 omits registered exclusions.** At `paper1.md:1400-1404`, “Only a directly measured physical hazard can ... remove data” omits the registration's additional N/W/D/S grounds: undefined number, wrong data, drift screen and structural failure. `docs/registrations/block6_replication_DRAFT.md:551-567` explicitly enumerates them immediately after its physics slogan. Restore those qualifications and describe constrained discretion rather than claiming all discretion is removed. This is an inherited defect, still within this review's every-claim remit.
2. **§7.3 replay chronology needs a collection qualifier.** `paper1.md:1459-1464` says both rules changed “before any claim data existed.” The cited replication revision is dated 15 October (`block6_replication_DRAFT.md:32-43`); Block 5 had closed on 12 October (RS item 31). The replication's §9.5 item 7 (`:1046-1054`) specifically retains the earlier policy bytes and changes their treatment for later packs. Say before replication claim collection, and distinguish its disclosed inherited bracket decision from the operative D1 drift screen. Do not imply that the earlier primary-block rule was retrospectively changed.
3. **S9-04 does not establish its full historical claim.** The paragraph is indeed inherited verbatim, but D-099 (`decision_log.md:6222-6230`) records a rate problem and a *queued* rate-aware design. It proves neither that the replacement landed nor that energies reduced under that mapping were voided for claim use. D-078 (`:4207-4228`) bars claim use under a different, earlier defective timestamp anchor; it does not supply the missing causal bridge. Supply the actual implementation and disposition records or narrow/remove the unsupported clauses. “No number in it” is not an exemption from sourcing.
4. **Correct the two absence judgments.** RS `:295` explicitly says Ed installs a `~/.zshrc` guard, with the snippet in issue #589; pipeline-audit `CRITIQUE.md:27-35` describes its `collection.active` condition. The historical synthesis also says each census hit was a real contaminant (`SYNTHESIS.md:15`). Thus “no source found” is too broad for both the shell guard and the first half of the removed catch guarantee. Neither source proves universal installed enforcement or that no kept number was affected. Keeping those guarantees out is defensible; explain the evidentiary limit accurately. Do not open the actual home-directory shell file to resolve this review.
5. **Qualify universal claims and distinguish requirements from demonstrated coverage.** In particular: “decided every question” in H17, each activation necessarily writing a record in S9-01, all consequential defects being found by execution in S9-03, and the whole-study critical-path assertion in S9-11 exceed the cited governance or historical sample. H18 item 6 also needs a direct implementation/printing source for its universal no-default/no-zero claim. State the supported policy or the documented examples. Preserve the pending BLINDCHECK as a requirement, not a completed audit.

Recommended additional precision: S9-07's runtime comparison should carry the retrospective's load/niceness caveat and its limited terminal-step coverage. The times and fixed-comparator finding are supported, but this was not a controlled attribution of the entire speed gain to the rewrite.

**RL-5 conflict requiring the research lead's recorded disposition:** RL-5 item 3 (`:125-126`) says the census “refuses and pauses collection while any agent process is alive.” That is inaccurate for the primary claim head: a positive census returns a refusal and stops its chain. The candidate's per-collection correction is historically confirmed; it should not be flattened back to “pauses.” The research lead should enter the distinction in the binding log. Likewise, item 181 is the 6 November v4 scheduling delegation, not the origin of the already documented October agent arms. This report does not itself amend either ruling.

## Sources and method

I opened the sources myself using local Git objects; this is not acceptance of the builder's table as evidence. Unless another commit is named below, a source locator means `git show 4d2a9050f:<path>` and its numbered lines. `RS` means `RUN_STATE.md` at that commit. Process-path strings inside documents were treated as text, not followed.

Other pinned sources opened:

- `e7ca6d3425824f4cb29e61334c277b38ff67d380:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`: RL-5, RL-7(g), RL-24 seats 9/11, RL-40 H19/R-5 and RL-43's fence (`:125-130`, `:192-194`, `:617-619`, `:1512-1519`, `:1730-1741`).
- `79d8e2dbb5137ccf4e95ac1d0aa32013072252d0:docs/research-audits/2026-11-07/b5-release-to-paper.md:464-475`: adopted P1-P12.
- `24b549f25:docs/research-audits/2026-11-10-fable/paper-audit.md:142`: C-7; adjacent audit material appeared in the same excerpt (exposure note below).
- `c27485347:joulewise/b5/driver.py:1272-1282,1312-1347`; `f31aca19f:joulewise/b6/loop.py:285-312,471-510` and launchd template `:7`; `6731d5249` and `2649fad54:joulewise/b6/loop.py:301-326,526`; BYTES configuration at `6731d5249`.
- `joulewise/b6/agent_pause.py` at all three later pins: `f31aca19f`, `6731d5249`, `2649fad54`. The entire files are byte-identical (216 lines; SHA-256 `d52137d8b5b55ab49a23f5a190d90cf8a3b7ae8688f9ac02db516d6f10d2ef3a`). Constants are `:12-13`; cumulative-limit and clean-resume logic is `:55-88`; wrapper behavior is `:91-106`. Introduction commit `495569dfc` is dated 2026-10-14.
- The inherited paragraph at `a1a5029fb:docs/paper/paper1/paper1.md:1290-1293`; the blind-draft tag resolves to `a1a5029fb2cc0f9b0541f154d0d9d23f56e8aebb`.

**Exposure limitation:** Some source/intake excerpts were broader than necessary. They displayed Block-5 result prose in RL-39 and adjacent paper-audit C rows, and v4 clock-refusal diagnostics in RS items 250-251. I do not claim blanket value-naivety after those excerpts. Those quantities are not reproduced here or used to adjudicate a scientific result. No real measurement, custody, night, archive, model-weight or restricted directory was opened; no path under `/Users/edr` was accessed by a command, apart from Git's permitted shared-object-store access. The lead should retain this limitation when judging the review's blinding compliance. Repository text alone is not a guarantee of value-free exposure.

## Per-claim verdicts

Verdicts concern the wording at the candidate. “Confirmed” for a policy means the cited record states that policy; it does not certify every historical execution. Mixed claims are split below. S9-12 is in the generator, not in the manuscript.

| Claim / FACT locator | Verdict | Source opened and finding |
|---|---|---|
| H17: agents designed, implemented, collected, reviewed and drafted under one human; human set requirements; workers implemented/reviewed/tested | confirmed | `docs/orchestration.md:13-41`; gate policy `:3-6,28-34`; RS session headers and the eleven arm records. Model versions remain a fill. |
| H17: researcher “decided every question” changing measurements or claims | overclaim | Gate policy `:54-60` reserves escalation categories; RS items 256b/257 delegate research design and establish an agent ruling log. Human final authority is supported, an exhaustive personal decision history is not. |
| H17: successive interactive leads, sometimes two concurrently; lead decomposes, adjudicates and chooses gates | confirmed | RS items 102 (`:433`), 108 (`:465`); retrospective `:3` identifies the block-5 lead on the Air; gate policy `:49-60`. |
| H17: 27 October refuter rule; cold judges where registration requires them | confirmed | Gate policy `:37-39,58-60`; RS item 42 (`:105`), item 69's historical pointer (`:2992`) and item 85 (`:350`). The FACT comment's “a judge only where a registration requires one” is **wrong** as an exhaustive policy gloss: `:38-39` also names executing-refuter contradiction on counting/exclusion. |
| H17: binding research-lead log from 10 November; other rulings proposals; this seat assigned | confirmed | RS items 252, 256b and 257 (`:1137-1142`); RL-24 row 9 (`:617`), RL-43. |
| S9-01: launchd watchdog tick every 300 s; safe tick starts a fresh headless session | confirmed | `docs/process/MAGISTRATE_WATCHDOG.md:3`; block-5 magistrate brief `:10-14`; RS activation headers 41-76 opened. |
| S9-01: each activation always records its work and exits | overclaim | Supported as the normal work pattern, not an invariant. `docs/orchestration.md` Records explicitly exempts quiet relaunches; RS items 52/59 explicitly have no record file. Use “working activations” or “normally.” |
| S9-01 / H18.3: census refuses at arm; primary-block positive census stops the chain | confirmed | `driver.py:1272-1282,1322-1328` at `c27485347`; no `PausingCensus` there. RS item 16 corroborates a real stop. Strict arm census also at `2649fad54:driver.py:2194-2201`. |
| S9-01 / H18.3: replication/BYTES pause, resume after 600 clean s, stop at 7,200 cumulative paused s | confirmed | Identical `agent_pause.py` at all three pins, especially `:55-88,97-106`; `2649fad54:driver.py:2593-2599` wires it in. The time limit is cumulative, not a fresh two-hour allowance per episode. |
| S9-01: interactive agents ran on measurement Mac; analysis agents used real custody under its user account; custody by rule; local/cloud development and review | confirmed | RS items 16, 78, 108; `registration_block5.md:4850-4855`; R2P P4; orchestration and review/session records. No claim of machine-enforced data separation remains in §7 prose. |
| Figure 5 caption: permitted activities, no agent remaining during collection, blind L9 production and release verification, separate uncovered checks | confirmed | This is a policy schematic, not a claim that no agent was ever detected. R2P P2/P3/P4; DLE-1 `:71-85`; `LEAN-COVERAGE-AUDIT.md:70-96,107-121`. Figure/caption unchanged from base. |
| S9-02 R-5: primary collection 8-12 October; eleven recorded arms by headless activations | confirmed | All eleven files opened individually (inventory below); first arm header `:3`, RS item 31 (`:54`) closes collection on 12 October. The last arm record is dated 11 October; the table gives collection dates, not eleven arm dates ending on the 12th. |
| S9-02 R-5: agent pre-arm checks, notice, night and dead-man launchd jobs, calendar session command, release-line gating | confirmed | Each arm record records checks, notice and job installation; representative command/calendar at `seal2-alpha-a1-arm.md:64-68`. Magistrate brief and `seal2-gamma-a1-arm.md:14,78` support brief/release-line authority. This is contemporaneous bounded arming, not item 181's later standing grant. |
| S9-02 R-5: replication loop loaded 17 October, reloaded that evening, nine counting sessions, closed 21 October | confirmed | RS items 44/45/47/59 (`:128,131,141,203-205`). Item 44 is a refused first attempt, not evidence that the researcher completed the later successful bootstrap. Item 45 records success by an activation. |
| S9-02 R-5: loop prechecks, sends notice, waits 1,800 s for veto, rechecks and starts | confirmed | `f31aca19f:loop.py:285-312,471-510`; later pins `:301-326,526`. The interval is a minimum wait (`notice_sent + 1800`); ticks/prechecks can make it longer. |
| S9-02 R-5: BYTES pass-1 load 25 October, pass-2 resume 28 October, twelve sub-packs and closure 30 October | confirmed | RS item 70 plus its historical armed pointer `:2984`; item 85 `:348-350`; item 151 `:896-899`; BYTES config at `6731d5249`. Counts here are collection structure, not energy results. |
| S9-02: loop every 300 s, headless wakes at desk points, activation holds/resumes | confirmed | `f31aca19f:configs/launchd/com.joulewise.b6loop.plist.template:7`; RS items 52, 59, 85 and 261. A loaded loop program performed the later session arms. |
| S9-02 / S9-10: standing scheduling/arming authority transferred 6 November, after all three collections; later-study scope | confirmed | RS item 181 `:2659-2669`, dated about 09:10 PST, explicitly names R0/R1/W1/D1-D3 under the approved v4 design and withdraws earlier lead rerun holds. It is not a grant retroactively originating the October arms or an unrestricted grant over all future studies. |
| H18.1: committed registrations/sealed primary inventory, OS/model check, harvest code-difference exclusion, disclosed amendments | confirmed | Seal record `:8-22`; registration `:1543-1548,2602-2604,3948-3950`; R2P P6/P7 and the deviation log. The prose correctly distinguishes arm identity from harvest file checks. |
| H18.2: custody and structure-only release; blind analysis repair; BYTES hidden factors and held-out commitment requirement | confirmed | Registration custody map; magistrate brief `:76-81`; R2P P4/P8; `2649fad54:docs/registrations/bytes_pack_v1.md:340-348`. This confirms prescribed blinding, not a completed BLINDCHECK or a forensic audit of every author. |
| H18.3: only physical hazards can remove data; all other flags eliminate selection discretion | wrong | Replication registration `:551-567` adds N/W/D/S grounds. A registered effect constrains decisions but does not eliminate all stored judgments (coverage audit `:107-119`). Fix 1. |
| H18.4: two-family parallel executing review, regression and counterfactual from 27 October | confirmed | Gate policy `:1,28-34`. This is the adopted rule, not evidence of complete per-PR compliance. |
| H18.5: independent core arithmetic using recorded judgments; uncovered quantities need checks; BYTES twin/tolerance requirement | confirmed | R2P P1/P3; coverage audit `:70-96,107-121`; DLE-0 `:38-49`; BYTES registration §12 at `2649fad54`. It properly says “requires” for the twin. |
| H18.6: every missing fingerprint/malformed record/undefined input refuses, never defaults; refused cell always printed unavailable, never zero | unsourced | Analysis plan `:174-192` establishes refusal handling, but H18's cross-references do not demonstrate this universal set of implementation and display behaviors. Add direct producers/printing sources or state the required contract. |
| H18.7: registered fixed sentences versus later blind-draft branch prose; immutable draft commit/tag and post-collection chronology | confirmed | R2P P5; draft at `a1a5029fb`; tag resolved locally; RS item 31. No post-release provenance statement was added outside §7. |
| H19: primary keyboard session stopped chain 2 h 32 min after t0; attempt did not count | confirmed | RS item 16 (`:34`); this is a structural stop/eligibility record, not a measured scientific outcome. |
| H19: software update left daemon; BYTES paused two hours then ended, noncounting; other t0 refusals captured nothing | confirmed | RS item 78 (`:286`), 67 (`:259`) and 158 (`:964`). These do not establish the removed universal guarantee about all kept numbers. |
| H19: supervisory activation must immediately exit during precheck/arm/collection | confirmed | RS `:295` and item 78/85 next-activation rules; loop-state rule explicitly covers PRECHECK, ARM_WAIT, SMOKE_* and SESSION_RUN. |
| H19 / report: no source found for shell guard | wrong | RS `:295` and pipeline-audit `CRITIQUE.md:27-35` are textual sources. Neither verifies installed shell behavior, and no forbidden home-directory file was inspected. Deletion can stand for that narrower reason under RL-40. |
| S9-03: listed executing catches, late-round fix defects, councils/docs/serial reviews adding little protection; adopted pruning | confirmed | Gate policy `:13-34`; RS item 69; synthesis's historical segment map. Meter-path correction is RS item 210 (`:2040`) and talk H12 (`:344`), without a v4 outcome. |
| S9-03: all number-changing defects over the whole study were found by execution/pipeline runs; reading/process review “added days and caught little” | overclaim | Examples and the adopted policy are supported; an exhaustive whole-period classification is not supplied, and `P1-AUTO-CATCHES` remains unfilled. The historical synthesis is explicitly proposals and has a critique; do not treat its estimates as audited totals. |
| Unnumbered replay bullet: widened bracket bar fails by construction; outside-CPU rule removes quiet rehearsals; later disclosed alternatives | confirmed | Replication registration `:1046-1054` gives the bracket derivation; `:765-774` gives the CPU replay and flag-only alternative. These are non-claim rehearsal derivations, not replication outcomes. |
| Unnumbered replay bullet: both changed “before any claim data existed” | overclaim | Revision `:32-43` is 15 October, after primary closure; `:1046-1054` distinguishes retained primary bytes and later packs. Fix 2. |
| S9-04: early equal-rate assumption can displace edges | confirmed | D-099 `:6222-6230` records unmodeled wall/monotonic rate and anchor margins. |
| S9-04: this was replaced and affected energies were voided for claim use | unsourced | Inheritance at `a1a5029fb:1290-1293` is confirmed. D-099 queues a design; D-078 addresses a different earlier anchor defect. Neither proves these two later events. Fix 3. |
| S9-05: leaked monitor before replication; background constant measured after removal; watchdog now counts fixture orphans | confirmed | RS item 42 (`:109-111`) and item 198 (`:2208`). No threshold value is needed in §7. |
| S9-06: wrong-owner directory caused zero-capture refusal; top-level GO/courier masked it; watchdog key parsing delayed discovery 2.5 days | confirmed | RS item 249 `:1283-1287` states each causal step. Items 250-251 concern a distinct subsequent refusal/diagnosis and should not be folded into the wrong-owner cause. GO is an operational hazard verdict, not a scientific result. |
| S9-07: ENOSPC at 18.5 h / about 110 GB; 27.1 h and 1 h 46 min; fixed comparator equivalence | confirmed | RS item 165 (`:1002,1009`); retrospective `:9-15,19-28,53`; D-188. Equivalence is result/decision equivalence, not universal byte identity. The retrospective says final-step coverage was still pending for that pair. |
| S9-07: implied attribution of the elapsed-time gain entirely to rewrite | overclaim | Retrospective `:13,71`: different load and niceness; no controlled split of code versus load. Add the caveat. Do not change the reported times or infer a benchmark result. |
| S9-08: 1,001 rows, eleven families, six attributed defects from structure-only trace; last defect later repaired | confirmed | Blind-trace report `:3-14,145-159`; DLE-0/1/3; talk H7 `:339` identifies the r4 repair. This is not a claim that six families or all defects belonged to L9; several were recompute/comparator defects. |
| S9-09: classifier refused loop bootstrap and stray-process kill; researcher sent commands | confirmed | RS items 44 (`:128`) and 42 (`:111`). Does not prove the researcher executed either command; manuscript correctly says sent. |
| S9-10: two authority conflicts and their dated resolutions | confirmed | RS item 181 `:2659-2669`; item 257 `:1137-1142`. The latter concerns research-design authority, not scheduling. |
| S9-11: 27 October gate policy predates viewed study results and fits review depth to number impact | confirmed | Gate policy `:1-11,25-39`. This is contemporaneous stated policy provenance, not an independent global access-log audit. |
| S9-11: collection rarely limited the whole project's progress; serial gating was the critical path | overclaim | Historical synthesis supports specific October review bottlenecks, not a measured whole-study comparison through 10 November. S9-07 itself supplies an analysis-runtime bottleneck. Qualify the period and evidence. |
| Pending BLINDCHECK and closing lesson | overclaim | RL-7(g) and RL-24 seat 11 require an actual check; no result is filled. The final claim that controls “held whatever an individual agent believed” is an inference/design lesson, not a demonstrated universal guarantee. Label it as such. |

### S9-12 source mappings

| Mapping | Verdict | Source opened / limit |
|---|---|---|
| `P1-AUTO-MODELS` | confirmed | RS session headers, items 252/257/256b E3; gate policy rule 3; `model_allocation_ledger.md:3-10,33-41`. Ledger entries are historical; use dated headers for actual versions, not the ledger's old introductory model name. |
| `P1-AUTO-LOST` | confirmed | Arm records and cited RS stop/pause/refusal/closure items exist. A source route, not a computed hours total. No subtraction/aggregation was performed. |
| `P1-AUTO-CATCHES` | confirmed | `segments.json` exists as the seven-segment audit evidence; synthesis and gate policy rule 9 provide historical evidence and the required later tally shape. A complete November tally is still owed; the mapping does not prove it exists. |
| `P1-AUTO-REPLAY` | confirmed | Replication registration `:765-774,1046-1054` supplies the actual two replay derivations. Add §9.5 item 7 explicitly: the drift-bar derivation is not the S-8 derivation. |
| `P1-AUTO-BLINDCHECK` | confirmed | RL-7(g) `:192-194` and RL-24 seat 11 `:619` identify required producer and timing. “Made ... and recorded” must be read prospectively as the supplying artifact requirement; do not assert completed evidence until the seat delivers it. |

### Eleven-arm inventory independently opened

All paths below are under `docs/process_traces/2026-10-block5/` at `4d2a9050f`. The directory's Git tree also contains exactly eleven `*-arm.md` entries. Each file names a headless magistrate activation at line 3.

| File | Activation | Notice / installed-job evidence |
|---|---|---|
| `alpha-a1-arm.md` | `d5291af4` | `:59-64` |
| `alpha-a2-arm.md` | `d2ddcd8e` | `:52-63` |
| `alpha-a3-arm.md` | `0705bcd5` | `:51-59` |
| `seal2-alpha-a1-arm.md` | `1aed44f9` | `:59-68` |
| `seal2-beta-a1-arm.md` | `e33d5695` | `:69-78` |
| `seal2-beta-a2-arm.md` | `cbe4230e` | `:69-80` |
| `seal2-beta-a3-arm.md` | `4c4ed4b2` | `:24-28` |
| `seal2-beta-a4-arm.md` | `20773813` | `:22-26` |
| `seal2-beta-a5-arm.md` | `21c2e498` | `:16-18` |
| `seal2-beta-a6-arm.md` | `bab1c330` | `:28-30` |
| `seal2-gamma-a1-arm.md` | `d7a980d2` | `:33-35`; release-line explanation `:14,78` |

### Crosswalk to every row of the builder's “Sourced claims” table

Rows are counted from the first data row of `2026-11-11-p1-seat9.md:56`.

| Rows | Verdict | Corresponding review above |
|---|---|---|
| 1 | overclaim | S9-01: tick confirmed; unconditional record-writing needs qualification. |
| 2-3 | confirmed | Pinned stop versus cumulative pause implementation. |
| 4-9 | confirmed | Eleven-arm inventory; loop loads/closures; veto minimum; interval; item 181's date and scope. |
| 10-13 | confirmed | Research-lead log; dated review/refuter rules; two leads. FACT H17's exhaustive judge-only gloss needs correction. |
| 14-15 | confirmed | Specific primary stop and BYTES pause/termination records. |
| 16 | confirmed | Structure-only release trace counts and attribution. |
| 17 | confirmed | Recorded runtimes/equivalence; retain coverage/load caveats. |
| 18 | confirmed | Wrong-owner zero-capture refusal and delayed discovery, distinct from later clock refusal. |
| 19-21 | confirmed | Classifier refusals; orphan/census records; gate-policy provenance. |

The builder's three-false-claims table is accurate about the resulting §7 prose: the no-agent assertion and unused-account assertion are gone, and recomputation is scoped to core arithmetic. Its “not re-derived” admission is accurate, but does not discharge S9-04. Its complete-run catch guarantee remains unsupported even though a historical source exists for “real contaminant.”

## RL-43 fence, fills and sealed-result check

**Substantive fence: PASS. Literal two-file description: incomplete.** `git diff --name-status origin/main HEAD` lists four files: the manuscript, generator, generated `fill_index.md`, and builder report. No production code or unrelated paper section changed. The report and generated index are additional paths, so “nothing outside those two files changed” is literally false. RL-43 `:1731-1733` explicitly anticipates index regeneration at merge; this generated delta is consistent with that dependency, not an additional scientific edit.

Static checks against the exact local base established:

- Manuscript bytes before §7 and from §8 onward are identical. All nine manuscript diff hunks lie within §7. Figure 5 and its caption are unchanged.
- Generator AST is identical after removing the five new exact-id §7 `source()` branches. Existing generic fallback and non-§7 mappings are unchanged. S9-12 adds only its comment and those mappings.
- All FILL id occurrence counts are identical. Only three placeholder descriptions change: `P1-AUTO-MODELS`, `P1-AUTO-LOST`, `P1-AUTO-CATCHES`. No value was filled and no outcome branch selected.
- An in-memory generator run, with `Path.write_text` intercepted, emits `235 214 218 173` and reproduces committed `fill_index.md` exactly. Beyond line-number movement, exactly the five §7 rows differ. The generator was not allowed to write the file during this review.
- The added section contains operational counts, elapsed analysis times, census timings and process status words. I found no inserted study energy, floor, ratio, held-out prediction or scientific outcome selection. Operational GO/refused/noncounting and comparator status are present; a literal ban on *all* verdict words would fail, but these are explicitly process accounts, not scientific outcome words. No inference of sealed study outcomes is licensed by this finding.
- The candidate is still based on `62a87aaad`, not on seat 10's later restructure. RL-43 requires seat 10 to merge first and seat 9 to rebase. Admission here is not permission to skip that order; recheck the fence/index after the rebase.

## Verification and handoff

- `git diff --check origin/main HEAD`: passed.
- In-memory Python audit described above: prefix/suffix identity, placeholder preservation, generator-only source changes and exact index reproduction passed. No repository file was written by those checks.
- `PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest tests.test_paper_build.PaperBuildTests.test_check_markdown_accepts_current_draft tests.test_paper_build.PaperBuildTests.test_check_markdown_rejects_missing_image tests.test_paper_build.PaperBuildTests.test_check_markdown_rejects_unterminated_inline_math`: **3 tests passed**, 0.174 s. These are lint-harness checks, not claim verification; the “current draft” test targets draft-v1.
- `PYTHONDONTWRITEBYTECODE=1 python3.13 -B docs/paper/build/check_markdown.py docs/paper/paper1/paper1.md`: exit 0; **0 hard defects**, six images present, no broken table rows. It reports one pre-existing abstract emphasis warning outside §7.
- No full suite, build-output generation, study pipeline, hardware/MLX task, performance run, network access, model download, process intervention, push or merge was performed. No native test is needed for this report-only change. The three lint tests were the only tests run.

Changed file: this report only. Commit: the local commit adding this path, message `docs(paper1): record Sol source review of seat 9` (its hash is reported in the handoff rather than embedded recursively here).

Next exact step: the research lead adjudicates the required wording/source fixes and the exposure limitation; the builder applies admitted fixes, then rebases after seat 10 and regenerates the index. The lead rechecks the final diff and sources. The reviewer has left all substantive files untouched and has not installed a ruling or updated coordination state.
