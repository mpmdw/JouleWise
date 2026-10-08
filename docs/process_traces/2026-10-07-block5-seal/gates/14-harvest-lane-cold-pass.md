# Harvest lane: the cold Fable 5.1 pass (2026-10-07)

## What this record is

This is the second of the two gate records for the **harvest lane**; the first, with the terms this record uses
(window, harvest, H_claim, harvest lane, reference, drift screen, lost reference), is
`13-harvest-lane-executing-review.md` beside this file.

A **cold pass** is a last reading of code by a session that took no part in writing or reviewing it and that starts
with no knowledge of the work. The project requires one, by a Fable 5.1 session, for any code on the path from a
measurement to a claim. The harvest is on that path: it decides which measurements are kept.

The pass below was made on 2026-10-07 at the lane's head `c10257418a9d7d2173bec306c0b1deb38e144343`, as one step
of the workflow `wf_38c5e204-c67`. Its verdict is **PASS WITH NOTES**: seven findings, two graded MINOR and five
graded NOTE. It ran the drift screen with the registration's own numbers and found the ruled outcome in every
case; the two MINOR findings are both about how a damaged record line is treated and worded, and neither can print
a wrong number. The pass returned its result as structured data to the workflow and wrote no file, so this record
was made from the workflow's journal on 2026-10-08 by the seat that assembled the seal's record commit.

In the findings, `klass` is the pass's class for a finding: `NUMBER_INTEGRITY` (it bears on whether a number is
right), `REPRESENTATION` (it bears only on how something is recorded or worded) or `FENCE` (it bears on whether the
lane stayed inside the files it was allowed to change). The **allowance** is the amount of drift between
references that the screen tolerates; it is computed from how many references survived, and the pass writes it as
`bound(n_start, n_end)`. "Base" means commit `9395cecfb`, the commit the lane was cut from.

## The reviewer's result, field by field

Source: row 5 (counting from 0) of the workflow journal `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/subagents/workflows/wf_38c5e204-c67/journal.jsonl`, the result of agent `a72a99ea4ec84d456`; SHA-256 of the journal file when this record was written: `b238a7b9e6ef51d8f287e875c9dca66bccc39f60e06771f63859876d06906c5c`. The text under each heading below is the reviewer's own, whole and unchanged. Only the headings and the bold labels were added.

- **Reviewer:** Fable 5.1 cold pass (claim-path code), no part in authoring; read-only on /Users/edr/code/JouleWise-wt-harvest; scratch /private/tmp/w1007-harvestcold; probes /private/tmp/claude-501/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/scratchpad/probe_harvest_cold.py and probe_harvest_cold2.py
- **Reviewed head:** c10257418a9d7d2173bec306c0b1deb38e144343 (lane/2026-10-07-harvest-lane; diff judged against 9395cecfbc40fb93e87a7657ec0ba5da0ca9ef3a); harvest.py f68e53d4e84292c182772a20edf2e3649c7470a7113ff87ebdec6f91208c9bc2, whole_window.py ee107b1e5f7eab306192c78d43171de828c290158bd3dc6fb5e63c229a1c25a5, scripts/harvest_b5_window.py 88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45 (recomputed here, equal to the author's and to harvest_checkout().files)
- **Verdict:** PASS_WITH_NOTES
- **Fence respected:** true

## Findings (7)

### HC-0 (NOTE, NUMBER_INTEGRITY)

**Summary.** Drift check verified with the registration's numbers: K-4 and K-6 give the ruled outcome at both endpoints, a lost reference's energy enters no deciding bracket, and the allowance the consumer reads is the survivors' one. Survivor logic moved toward L9NEG8 option A (one function, parity-tested against the real writer); no fourth strict-invalid variant was added.

**Executed evidence.** probe_harvest_cold.py A_DriftCheck, corpus patched to RULING_CORPUS: minted bound(3,3)=0.59333, neg8_count_adjusted_bound(2,3)=(3,2)=0.63833. (1) start-3 +0.855 J unseen (contention.unmeasured), ends +0.80 J: stored passed (stat 0.515, allowance 0.5933); lane: lost, survivors (2,1,3) stat 0.795 > 0.6383 -> rescreen failed, neg8.screen_failed in exclusions, allowance source none, consumer problem screen_not_passed. (2) mirror at the end (end-1 lowered by 0.855, battery.unmeasured): stored passed; survivors (3,1,2) stat 0.77 -> failed, excluded. (3) end-3 succeeded, no envelope, gross poisoned to 1000 J, drift bound/2: stored failed (neg8_bracket_reference_invalid, claim_families {}); lane: harvest_reference_losses {end-3: energy_unreadable}, rescreen passed (3,1,2), neg8.screen_failed absent, derived/neg8-allowance.json source survivor_rescreen, withheld bracket allowance 0.63833 = bound(3,2), harvest_neg8_allowance_bracket(archive,row) returns that bracket (allowance 0.63833, counts 3/1/2); end-3 appears in neither pass's _reference_energy_evidence calls. (4) same at start-1 (idle NaN): (2,1,3) pass, allowance 0.63833, consumer 0.63833, start-1 never read. (5) end-3 unreadable with real drift 0.80: survivors fail, excluded. (6) clean window, start-2 env.member_quiet_state_violated: stored allowance 0.5933, survivors (2,1,3) 0.63833, consumer reads 0.63833. (7) all three end refs contention.unmeasured: references_insufficient, excluded (probe2). (8) start-1 battery.capture_pair_failed + end-3 unreadable: (2,1,2), allowance = bound(2,2) = 0.68. (9) clock.unmeasured on an unreadable reference: lost as energy_unreadable. Writer parity: 21 edge summaries (no envelope, point!=gross, lower<=0, bool/NaN/inf/int/string, idle None/bool/inf/negative/zero/missing, non-dict) equal between run_campaign._gross_energy_for/_idle_subtracted_energy_for and _neg8_writer_reference_energy. Lane modules here: tests.test_neg8_survivors + 6 harvest classes + tests.flags.test_flags_collect 188 OK; tests.test_whole_window, _selection, test_hazard_neg8_mint_verdicts, hazards.test_refusal_allowlist 120 OK. Structure: _neg8_writer_reference_energy (whole_window.py 4026) is the single energy test, called by harvest._neg8_reference_losses (5093-5096), the replay's lost branch (5058-5063) and the writer_entry branch (5089-5098); _custody_strict_invalid, harvest_strict_invalid and the stored-list logic untouched. Residual for L9-NEG8 stage 1: _derived_neg8_decision now carries three replay-mode knobs (stored_strict_losses, unlisted_strict_invalid, unreadable_energy in {refuse, writer_entry, lost}) that the design's one predicate and outcome function should absorb; the energy test runs at two harvest sites (loss map via setdefault, and the exclusion pass), consistent but duplicated; the predicate lives in whole_window.py beside _gross_fields because the design's new module is outside the fence.

**Smallest fix.** None in this lane. L9-NEG8 stage 1: fold the three _derived_neg8_decision mode keywords into the single predicate/outcome function and move _neg8_writer_reference_energy to joulewise/neg8_survivors.py.

### HC-1 (MINOR, REPRESENTATION)

**Summary.** K-5 narrows candidates to PRE_HARVEST_CODES for a torn prefix only; a malformed line that still shows a WHOLE harvest-only EXCLUDE_WINDOW code is still excluded, although the ruling (T-29, K-5) draws every candidate, whole or prefix, from the pre-harvest writers' codes and the harvest re-derives that code from the preserved bytes, so the exclusion protects no number (flag, not refuse). Disclosed by the author (note 5).

**Executed evidence.** probe_harvest_cold.py B_TornFlagLines, sealed catalog: line b'{"code":"calibration.capture_invalid","scope":{"level":"window"}}' (absorb fails, exact code salvaged) adds records.malformed_flag_exclusion_possible with candidate_codes ['calibration.capture_invalid'], excluding the window; 'calibration.capture_invalid' in h.PRE_HARVEST_CODES is False. The ruled cases hold: torn 'calibration.capt' adds no reason (disclosed only); torn 'model.identity_m' adds records.malformed_flag_exclusion_possible (candidate model.identity_mismatch); a whole pre-harvest DISCLOSE code in a malformed line adds nothing. Code: harvest.py _candidate_codes 6983: `return {code} if exact else {...}`. Reach: needs a pre-harvest writer to emit a harvest-only code, which PreHarvestCodeTests.test_the_flag_writers_are_the_ones_listed_here holds impossible; fails in the safe direction.

**Smallest fix.** harvest.py _candidate_codes: `return ({code} & PRE_HARVEST_CODES) if exact else {item for item in PRE_HARVEST_CODES if item.startswith(code)}`, plus one case in PreHarvestCodeTests / UnwrittenCoreFlagTests. Dispositionable as 'flag, not refuse' now or deferred to the next harvest lane.

### HC-2 (MINOR, REPRESENTATION)

**Summary.** The registration's worked example (T-30 as ruled, and the draft's line 2135 in the worktree copy) says a line torn inside '"code": "member.tok' with a visible run id removes that member; under K-5 as ruled and as coded, member.token_count_mismatch is a harvest-only code (harvest.py 4266), never a candidate, and such a line is disclosed only. Text contradicts the rule it sits beside; no number is at stake because the harvest re-derives the token-count mismatch from the bytes and removes the member by the real flag.

**Executed evidence.** probe B: non-canonical line b'{"scope":{"level":"member","run_id":"b5t-abs-r01"},"code":"member.tok' -> records.malformed_flag only, no member exclusion; sorted(c for c in h.PRE_HARVEST_CODES if c.startswith('member.tok')) == []. The lane's own PreHarvestCodeTests asserts candidates('member.tok') == {} (tests/test_harvest_b5_window.py 2430). Registration copy in the worktree: configs/campaigns/v5_claim_25g83/registration_block5.md 2134-2136. Also note the canonical serialisation sorts 'code' before 'scope', so a line torn inside its code never shows a run id at all.

**Smallest fix.** Text erratum to the registration (outside this lane's fence): replace the member.tok sentence with: a line torn inside a code that only the harvest emits (for example member.tok) names no candidate and is disclosed only; the harvest re-derives that code from the preserved bytes.

### HC-3 (NOTE, NUMBER_INTEGRITY)

**Summary.** K-4 deliberately drops the member.bytes_missing loss when the reference's bundle directory is absent (author note 4). That also covers a reference the verdict counted whose directory vanished between the desk verdict and the harvest: with no other new loss the stored screen then stands at harvest (allowance source stored_verdict) over bytes that no longer exist. Pre-existing (the code was no loss code at base), caught at claim time, and reachable only by evidence deletion after the verdict, which is a cold-gated irreversible act.

**Executed evidence.** probe_harvest_cold2.py F_Vanished: references on the roster, verdict (3,1,3) written, end-3's directory removed before harvest: member.bytes_missing on end-3, end-3 absent from harvest_reference_losses (the loss was dropped), and in this harness the other six references' strict failures forced a re-screen whose authenticity pass failed as rederivation_differs_from_stored_bracket (end-3 summary_unreadable, counts differ) -> neg8.screen_failed. The no-other-loss branch is by reading: harvest.py neg8_screen 4918 `if not reasons and not survivors: return "stored_verdict"`; the claim-time replay (row validator, survivors mode) loses the reference as summary_unreadable and the stored bracket no longer replays, so no allowance is read.

**Smallest fix.** harvest.py _neg8_reference_losses 5071-5077: drop the member.bytes_missing loss only for a reference that the verdict's authenticated manifests do not list as invoked (never ran), not for every absent directory; one condition plus one test.

### HC-4 (NOTE, REPRESENTATION)

**Summary.** Precision on 'a lost reference's energy is never read': the loss decision reads no energy (structure only, as RF-1 ruled); the exclusion pass, whose bracket carries the allowance, asks no fresh reduction of any lost reference; a reference lost as energy_unreadable is read by neither pass. The authenticity pass, however, still asks a fresh reduction of a reference lost by a physics code, to reproduce the stored bracket that contained it (pre-existing A5 design, equality check only, no decision rests on the value).

**Executed evidence.** probe A energy_reads: S-unmeasured-hidden reads = 7 ids (authenticity) + 6 ids without start-3 (exclusion); E-unreadable reads = 6 + 6, end-3 in neither; same pattern in cases 2, 4, 6, 7, 8, 9. Code: whole_window.py 5089-5111 (writer_entry branch skips _reference_energy_evidence; lost branch continues at 5077 before it); harvest.py _neg8_rescreen 5274-5294 (rederive(None) then rederive(exclude)).

**Smallest fix.** None required. If the registration's 'the loss test never reads the reference's energy' is to be read as covering the authenticity replay too, L9-NEG8 could enter a code-lost reference as the writer entered it (its stored summary) instead of re-reducing it; a text clarification is cheaper.

### HC-5 (NOTE, REPRESENTATION)

**Summary.** Author notes 1 and 10 confirmed: (a) the claim-time row validator still calls _derived_neg8_decision with unreadable_energy='refuse', so a window with an energy_unreadable reference is claim_usable in exclusions.json but refused by every claim consumer until L9-NEG8 part (c) lands (registered: SG-8 T-43, plan section 11); (b) a reference whose stored summary reads by the writer's test but whose fresh reduction is precheck-ineligible gives rederivation_failed:provenance when a re-screen is needed (window excluded) and leaves the stored screen when none is. Both fail in the safe direction; neither prints a wrong number.

**Executed evidence.** probe A test_10: no re-screen needed -> no neg8 code; re-screen needed (start-1 contention.unmeasured) -> rescreen problems ['rederivation_failed:provenance'], neg8.screen_failed in exclusions. (a) by reading: whole_window.py 4880 default 'refuse'; row validator call site unchanged in the diff; harvest_neg8_allowance_bracket returns the survivor bracket (probe A cases 3, 4, 6) but whole_window_drift_allowances runs the vetoes first.

**Smallest fix.** None in this lane; L9-NEG8 (c).

### HC-6 (NOTE, FENCE)

**Summary.** Fence and ruling conformance of K-5, K-7, H-8 to H-13, executed and read; nothing outside the six permitted files changed, no new flag code, no catalog or allowlist change (energy_unreadable is a loss reason inside brackets and neg8.* observed rows, not a code).

**Executed evidence.** git diff --name-only base..HEAD = joulewise/b5/harvest.py, joulewise/whole_window.py, scripts/harvest_b5_window.py, tests/flags/test_flags_collect.py, tests/test_harvest_b5_window.py, tests/test_neg8_survivors.py; blobs identical at base and head for reduce.py, uncertainty_evidence.py, powermetrics_fiducial.py, adapters/powermetrics.py, prewindow_check.sh, run_campaign.py, flags/collect.py, b5/chain.py, b5/driver.py, the sealed flag_catalog.json; no diff under configs/, tests/hazards, tests/fixtures. whole_window.py: one new private helper and one keyword on _derived_neg8_decision whose default reproduces the prior path (writer_entry None -> elif point_drift; 'refuse' never sets a reason); evaluate_neg8_point_drift and every name run_campaign imports unchanged. K-7: harvest_checkout() -> head c10257418..., status_clean true, three digests equal to sha256 of the files; CliTests prints it; exclusions.json gains harvest_checkout and no reader under joulewise/ or scripts/ parses that file today. H-8 (16 synthetic driver_checkout cases): differing/missing/extra code file -> driver_checkout difference; untracked scripts/x.py, tracked edit to joulewise/x.py or pyproject.toml, rename into joulewise/, quoted path -> differences; doc edit and tmp.txt -> recorded only (2); no files map or no porcelain -> unmeasured; None -> no record. H-9 (31 paths): hashlib.py, env/mac-measurement-lock.txt, pyproject.toml, .gitignore, .gitattributes, analysis/zz_new.py, Makefile, .editorconfig -> window_input; docs/other.md, tests/x, .github/, .claude/, README.md, RUN_STATE.md -> record_only; the runbook and its case variant -> window_input; only the runbook under docs/ is read by a window-time program (chain.py 110). H-12: another claim pack's file -> record_only for a window of a different pack, window_input with own_pack None, own pack and v5_claim_25g83 and the corpus directory stay window_input; the three CLAIM_PACK_DIRECTORIES exist. H-10/H-11/H-13 by the lane's IdentityReplayTests and DocstringFactTests (OK here). PRE_HARVEST_CODES held equal to CORE_FLAG_CODES, collect.py's literals and tables, driver.py's literals plus arm codes, and window_lineage.FINDING_CODES by PreHarvestCodeTests (OK here); its eight EXCLUDE_WINDOW members are the refuter's eight.

**Smallest fix.** None.

## What was done with each finding

Written on 2026-10-08 from the session record (`WAVE.md` of the wave of 2026-10-07, the entry of 23:46 PDT) and
the ruling of the seal gate's second stage, part A (`../RULING_STAGE2.md`, its sections C.5 and F). No fix round
was run on the lane: its head is still `c10257418`.

| Finding | What was done | Where it is recorded |
|---|---|---|
| HC-0 | Nothing to change in this lane. The three replay-mode settings it names are folded into one rule by lane L9-NEG8, the lane that gives every program one rule for which references survive. | session record, 23:46 |
| HC-1 | The lane's code stays as it is; the registration now states what the code does (stage 2, part A, change T-S2A-3). The pass itself classed the finding as "flag, not refuse". | `../RULING_STAGE2.md` sections C.5 and F |
| HC-2 | Fixed in the registration before the seal: stage 2, part A required the worked example to be replaced (its change T-S2A-2), and the change was applied word for word. | `../RULING_STAGE2.md` sections C.5 and F |
| HC-3 | The session record carries no ruling on this note. The pass asked for no change before the lane is pinned: the case existed before the lane, is caught when a claim is made, and can arise only if a window's files are deleted after its verdict, which the project allows only through a cold gate. | this record |
| HC-4 | Nothing required; the pass asked for none. | this record |
| HC-5 | Both parts go to lane L9-NEG8, as the pass says: (a) is that lane's registered part (c); (b) is the executing review's finding R-1. Both lose data and neither can print a wrong number. | session record, 23:46 |
| HC-6 | Nothing to change: the lane stayed inside its permitted files. | this record |
