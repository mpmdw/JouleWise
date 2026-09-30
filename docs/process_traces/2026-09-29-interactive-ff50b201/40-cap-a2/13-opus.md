CONSULT ANSWER: opus

# CAP-COUNCIL-25G83-01-A2 — Opus 5.5 seat

Seat conduct: one foreground session, read-only. I read the charge, the Sonnet report in full, A1 (`20-cap-council/31-addendum-ruling.md`) in full, the cap ruling's §4.3 R5–§9, the owner brief in full, HOLD-BY-CONSTRUCTION-01 §2, §3.1–3.3, §5–§9, and code at `origin/main` 9eab16f8 and `b953f4b0`. I did not read 11-sol.md or 12-astra.md. I ran nothing but `git show`, `grep` and a small Python reader over R7's JSON. Deviation: I wrote one scratch copy of R7's JSON to my session scratchpad (not `/tmp/cap-a2-ff50b201/opus/`), since deleted. I read no B value beyond numbers already printed in the records (R7's operatives, r1's statistics as the Sonnet report prints them).

## Words used

- **Calibration file**: the issued JSON that sets how large the timing uncertainty B may be. **R7** = `d079_calibration_acceptance_v2_n17_r7`, 17 members, judges build 25F84. **r1** = the 25G83 file from W1/W2 (candidate bytes `dbad7cc7…`).
- **Registered**: listed in `ISSUED_ACCEPTANCE_REGISTRY` in `joulewise/calibration_bracketing.py`. Only registered files can be loaded as authority. **Default**: the registered file production loads when none is named (`ACTIVE_ACCEPTANCE_ID`).
- **Pins**: the sha256 digests of the four estimator files that a calibration file records (`calibration_bracketing.py:208-213` on main). **Pin-only re-issue**: a new file identical to its predecessor except for the pins and its identity and notes.
- **Derivation night**: a non-claim window whose captures are written "derivation-only". It needs a default whose pins equal the running code and that does NOT judge the machine's build.
- **H1**: no claim-bearing window at 25G83 until the cap is closed by ruling. **Route**: a call sequence into unmodified production code that yields held content or a claim at a held build (hold ruling §6.1).

## Q1 — Default during the cap windows

**Answer: yes. A pin-only re-issue of R7 at 25F84 ("R8") is the right default, and it is the only one that works.** It is scientifically neutral provided three checks pass (below). Alternatives are worse: registering any 25G83 file as default makes every derivation night refuse; keeping R7 makes every derivation night refuse on stale pins; relaxing the pin check in the writer weakens a guard for no scientific gain.

**The deciding reason.** The derivation writer demands two things of the default. First, its pins must equal the running code, or it refuses `acceptance_artifact_stale` (`scripts/validate_powermetrics_fiducial.py:397-402`, reached from `_derivation_only_screen_basis` at `:524-567`). Second, it must not judge the machine's build, or it refuses `DERIVATION_ONLY_EPOCH_UNCHANGED` (`:2081-2100`). After the cap change, R7 fails the first test. Any 25G83 file fails the second. R8 passes both. D-138 already requires a pinned-file change to land together with a re-issue. R8 is that re-issue, and the r6→r7 re-issue is the precedent (R7 `derivation_notes.reissue_delta.kind = "estimator_pin_rotation_only"`).

**Why it is neutral, and where it is not.** R8 keeps the same 17 members, the same B values, the same statistics and the same operatives (screen 0.009724 s, level screen 0.032898… s, ceiling 0.010164834757777545 s). The only behaviour change in the code it names is the cap. The cap bound none of R7's members: their largest need was 137,535 cells against 165,000 (R7 `derivation_notes.derivation_method.corpus_survivor_cell_demand`, max 137,535). **Two parts of R7 are not neutral, and R8 must not copy them silently:**
- R7's `derivation_method.governed_projection_cell_budget = 165000` and its `budget_ruling` text (the August "Option B") describe the cap. A1 §3 B2 overrules Option B "for epoch 25G83". The cap, however, is one code constant used at every build, so R8 at 25F84 runs under the new cap too.
- R7's `budget_probe_status` says probe `a7e8b412` "returns detection_nonconvergent at the governed 165,000-cell budget". Under the new cap that statement is false: the probe completes and trips the tripwire at 0.5 (A1 §3 B2).

**What R8 must carry** (id `d079_calibration_acceptance_v2_n17_r8`):
1. The predecessor block citing R7 by id, file sha256 `9c3a29f6…` and derivation sha256. Every protected field is byte-identical to R7's except `acceptance_id`, `prospective_rederivation.estimator_code_sha256`, `derivation_sha256`, and the notes listed here.
2. `reissue_delta` with kind `estimator_pin_rotation_only`. It lists each rotated pin with its old and new digest (only `powermetrics_fiducial.py` if the cap rides alone, A1 step 3).
3. A new note `cap_change`: 165,000 → the value R3 yields; the members' need maximum of 137,535 sits under both values; the historical `derivation_method` fields are left byte-identical and are marked as describing how the members were derived, not the cap in force. It also says that A1's overruling of Option B applies to the constant R8 names, and it restates the probe's status under the new cap.
4. `science_neutrality_evidence`, built from the checks below.
5. `issuance.claim_eligible: true`, as R7 has. This is inert: R8 judges 25F84 only, and the machine is at 25G83.

**What must be checked before it is admissible:**
- **C-R8-1, B identity by replay.** Replay all 17 members from raw bytes under the frozen shipped bytes. Each B must equal its stored value to the last digit. The raw directories exist on disk: I checked all 17 have `raw/`. The re-issue tool does NOT replay: it copies each member's stored `b_fiducial_s` from `instrument_evidence.json` (`scripts/reissue_calibration_acceptance.py:196-206`, `:249-266`). A PROCEED verdict from that tool therefore proves bytes unchanged, not that B is unchanged. The replay is a separate required check, as it was for r7.
- **C-R8-2, dispositions.** Replay the 38-record on-disk 25F84 corpus that the r7 re-issue replayed (35 bounded, 3 unknown). Every anchor record and every disposition must be identical. If any record that stopped on the 165,000 cap now completes, R8 is not neutral: STOP and return to council.
- **C-R8-3, diff.** Outside `derivation_notes`, the recursive field difference between R7 and R8 must be exactly `acceptance_id`, `derivation_sha256` and the rotated pin(s). The re-issue tool's delta report must say PROCEED (`:411-510`).
- **C-R8-4, behaviour on the real ledger with R8 as default.** A derivation-only preflight at a 25G83 identity must return a basis naming R8, with level screen 0.032898… s (R7's value). Ordinary preflight at 25G83 must refuse `acceptance_artifact_epoch_mismatch` (`:425-436`). Bracket evaluation at 25G83 must return stale.
- **C-R8-5, wiring.** Add R8 in the same change to: the registry; `_issued_d079` in `joulewise/arm_readiness.py:6215-6224`; the `n17AcceptanceIds` enum in `scripts/floor_mint_pinsets/schema_v2.json:186-192`; and the default. Moving the default engages A335 (OLD-EPOCH-EXPLICIT-R7-ROUTE-01) and the R7-freeze tests of hold ruling §5.2. The Sonnet report said A335 does not apply under (a). That holds only until R8 moves the default. The tools pinned to R7 by id (`scripts/epoch_equivalence_check.py:146-151`, `REQUIRED_ACCEPTANCE_ID = ANCHOR_V3_R7_ACCEPTANCE_ID`) may stay on R7 because the operatives are identical. The ruling should say so, so that no one "fixes" them.

## Q2 — Amended text for A1 §5 step 1, step 9 and row S6

> **§5 step 1 (replaces).** **The D-138 transaction under owner choice (a), 2026-09-29.** Land the disposition-registry loader repair and the promotion tool, with their tests. The 25G83 candidate `dbad7cc7` (`d079_calibration_acceptance_v2_n12_25g83_r1`) is not registered in code. Its promoted bytes stay in the record as a reviewed, unregistered file. Its identifier is retired: no other bytes may ever carry it. Its statistics remain disclosed design inputs (ruling §5 item 5) and the H7 reference. No build-keyed hold code is merged. Until the closing transaction of step 16, H1 is enforced on main by absence: no registered calibration and no continuation judges 25G83, so every 25G83 measurement evaluates stale. The cap transaction does not wait on any 25G83 issuance.
>
> **§5 step 7 (adds).** The same B-identity replay is run on R7's 17 members and on the 38-record 25F84 on-disk corpus (conditions C-R8-1 and C-R8-2 of this addendum).
>
> **§5 step 9 (replaces).** **Merge the cap transaction with R8**: a re-issue of R7 at build 25F84 that changes only the recorded estimator digests, its identity and its notes, and becomes the default in the same change. It must meet C-R8-1 to C-R8-5. No file that judges 25G83 is registered by this step or by any step before 16.
>
> **Row S6 (replaces).** *Superseded by owner choice (a).* A calibration of another epoch is re-pinned: R8, at 25F84, becomes the default. Reason: the derivation writer refuses a default whose pins differ from the running code (`validate_powermetrics_fiducial.py:397-402`), and it refuses a default that judges the machine's build (`:2081-2100`). R8 judges 25F84 only. It licenses no measurement at 25G83 and changes no number anywhere. Its only role at 25G83 is to be named as provenance and as the prior-epoch diagnostic screen in derivation-only captures, and its values there equal R7's.
>
> **§10 item 2 (replaces).** Identity of two calibration files: R8 (the default for the cap windows) and the successor.

## Q3 — The interim re-issue

**Answer: drop it. Use R8 for the windows, then the successor alone.**

**The deciding reason.** The one job the ruling gave the interim was to be "a calibration in force whose pins name the code that runs" for the new windows (cap ruling §5 item 2, citing registration lines 149–150). A 25G83 file cannot do that job: a default that judges 25G83 makes the derivation writer refuse (F12). R8 does it.

**What else the interim did, and where each part goes instead:**
- **"The 12 values reproduce under the new bytes."** A1 step 7's B-identity check shows this as a recorded check. No issued file is needed.
- **"The member list was fixed under the 165,000 cap"** (ruling §5 item 2(b)). This disclosure moves into the successor registration, beside S5's naming of the 12 rows.
- **A fallback file.** It was never claim-eligible (§5 item 2(c)), so as a fallback it would yield no claims.
- **It could not be the successor's predecessor.** The issuer requires a predecessor of a different epoch (`scripts/issue_calibration_acceptance_generation.py:1981-1984`). For the 25G83 Revision-5 branch it also requires the predecessor to equal the active default (`:1797-1801`), which under this plan is R8.

**What is lost: nothing measured.** One thing gained: the step at which a 25G83 file first becomes registered moves from step 9 to step 16, which is what Q4 needs.

## Q4 — The hold

**Answer: re-sequence. No 25G83 file is registered until the closing transaction, and that transaction registers the successor, makes it the default and lifts H1 in one merge. Do not open a build-keyed hold lane.**

**The deciding reason.** The three failed rounds were not bad luck. The hold ruling's own stop rule says three rounds that each end in a new route "would show that the hold cannot be confined by the present structure of the code" (hold ruling §6.2, "Why stop"). A fourth design keyed to the same registered file is, in its words, "round 4 under another name". Every route the refuters found needed a registered file that judges a held build. Remove the file and there is nothing to hold.

**The sequence that makes it work** (replaces A1 §5 steps 12–16; steps 10–11 unchanged):

> 12. **Derive the successor candidate; cold science gate.** The candidate is not registered. An unregistered file cannot be loaded as authority (`calibration_bracketing.py:196-197` comment and the registry-indexed loader).
> 13. **Build the closing branch** from main. It holds: the successor's promoted bytes; its registry row; the default moved to it (A335 applies); its id added to `_issued_d079`; and the frozen headline pipeline. Send "CLAIM-RUN WORK COMPLETE" with that branch head's commit.
> 14. **#416 audit** at that head. No window of any kind is armed from the closing branch.
> 15. **Fixes** go on the closing branch, each followed by a re-audit of the difference. A fix that moves a pinned byte restarts at step 4 (R12). The restart also makes both R8 and the successor candidate stale, so both are re-issued, and the successor is re-derived before registration.
> 16. **Closing ruling** citing C1–C9 against the audited head. Then merge that head **by fast-forward**, so main's commit equals the audited commit (C6). This merge is the lifting of H1. No hold entry exists to remove. If main moved meanwhile, the closing branch is rebased, the difference is re-audited, and the ruling names the new head.

**C4 (replaces).** The successor calibration, derived from the fresh captures, cold-gated, and present with its registry row and default move on the audited head. It is not registered on main before the closing merge.

**What enforces H1 until then.** Absence on main, plus the admission list, which names no 25G83 id. There is one weak point: absence depends on the capture recording the machine's true build. On main, `--identity-epoch-json-for-test` still replaces the recorded `os_build` without requiring the fake sampler (`validate_powermetrics_fiducial.py:2046-2060`, compared with the budget seam at `:2029-2036`, which does require it). This is F17 of the hold ruling, and I confirmed it on main. It is a pre-existing gap, not caused by this plan, and bundle bindings may block it further (the earlier Opus refuter's reading, which I did not verify). I recommend a small lane before the first claim window: make that option an argument error without `--sampler-direct-for-test`. It edits no pinned file.

**What the re-sequence costs.**
- The audit runs on an unmerged head.
- Main must hold still on the pinned files and the headline paths during the audit, or pay a re-audit of the difference.
- Every derivation window, including any R9 third window, must finish before step 16. After the successor becomes the default, derivation-only mode refuses at 25G83 (`:2094-2100`).

## Q5 — The promotion and re-issue tools

**Answer: use two tools for two jobs. Land nothing new in the (a) lane beyond what the owner chose.**

- **R8: `scripts/reissue_calibration_acceptance.py`**, the r6→r7 precedent. It loads the registered R7 through the ordinary loader, which works because R7 is registered. It authenticates the 17 member bundles, rewrites the pins, runs the production validator (`:275-283`), and emits a marked candidate plus a delta report that stops on any non-pin difference (`:411-510`). It then needs the same issuance step r7 had: unmark, new id, and the notes of Q1. It does not replay B, so C-R8-1 and C-R8-2 are separate required evidence.
- **The successor: generalize `scripts/promote_calibration_candidate.py` in the successor lane**, not in the (a) lane. Today it hard-wires the candidate path, `CANDIDATE_SHA256`, `INPUT_SHA256`, `ACCEPTANCE_ID`, `RULING_IDS` and the required hold set `{H1,H5,H6,H7}` (`b953f4b0:scripts/promote_calibration_candidate.py:22-30`, `:113-119`, `:156-201`). Move every one of those into a committed promotion manifest. The cold gate cites the manifest by digest, and the tool has no defaults. The H1 hold entry must state its lifting ruling. The regression test is that the generalized tool, given an r1 manifest, reproduces the r1 bytes byte for byte. This also re-points the r1-bound tests that the (a) lane keeps (Sonnet item 4) without weakening any assertion.
- **Not recommended:** routing the successor through the re-issue tool. That tool re-issues an already-registered file with the same members. The successor has new members and no registered source.

## Q6 — What could make a number false under the amended plan

1. **R8 declared neutral on the re-issue tool's PROCEED alone.** That verdict compares stored values, not a replay. **Required:** C-R8-1 and C-R8-2.
2. **R8 copying R7's cap statements as current fact** ("governed budget 165,000"; "the probe returns nonconvergent"). The published calibration record would then misstate the code that produced its numbers. **Required:** Q1 item 3.
3. **Past 25F84 claim numbers replayed under the new cap.** Any claim-window capture that stopped on the 165,000 cap would now complete. A replay would then differ from a published table. R7 cites 137,535 as the claim-bearing maximum in August. I did not check later 25F84 windows. **Required:** list the dispositions of every capture behind a published 25F84 number under the shipped bytes, and disclose any change.
4. **The r1 identifier reused for other bytes, or r1 called "the calibration" anywhere.** Authentication is indexed by id (`calibration_bracketing.py:144-146` comment). **Required:** retire the id, and label r1's statistics "candidate" wherever H7 or the paper cites them.
5. **The audited commit differing from the claim commit** because of a squash, a rebase or an intervening merge. **Required:** the fast-forward condition of step 16.
6. **A capture recording a false build** (the F17 seam) while H1 rests on absence. **Required:** the lane in Q4.
7. **Mixed provenance in the successor's inputs.** W1/W2 rows name R7 as their derivation basis; the new windows will name R8. The operatives are identical, so no number moves. The S5 lane and the successor registration must accept both and say "read R8 wherever R7 is named; operatives identical", as Revision 5 did for r6→r7 (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:604`). NOT CHECKED: whether the issuer compares a row's recorded basis id. My search of the issuer found no such check (only `:389`, `:1798`).
8. **Cosmetic, not a number.** The issuer's refusal message says "requires r7 predecessor" but tests equality with `ACTIVE_ACCEPTANCE_ID` (`:1798-1800`), which will be R8. Reword it.

## Summary

1. The cap windows need a default whose code fingerprints match the new code and that does not cover build 25G83. A re-issue of R7 at 25F84 with only its fingerprints changed ("R8") is the only file that fits, and it follows the r6→r7 precedent.
2. R8 changes no number, but only if a replay proves it: the re-issue tool copies stored values without recomputing them. R8 must also stop repeating R7's text about the old 165,000 cap as current fact.
3. Drop the interim 25G83 re-issue. Its stated job was to be that default, which a 25G83 file cannot be, and its other jobs become a recorded check and a disclosure.
4. Enforce the claim hold by keeping every 25G83 file unregistered until one closing merge registers the successor, lifts the hold, and is exactly the commit the three-family audit examined. Do not attempt a fourth hold design.
5. Use the existing re-issue tool for R8, and generalize the promotion tool for the successor in its own lane. Before claims, close the test option that lets a capture record a false build, and check that the new cap changes no published 25F84 capture's disposition.
