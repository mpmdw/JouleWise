1. **The block-5 erratum (B5-2, B5-3) breaks the rule it relies on.** The synthesis quotes only the second sentence of `registration_block5.md:5144-5146`. The first sentence reads: "None to §§3–9 for an armed or completed attempt." The custody map, "Who may read" at `:4895-4902`, sits inside §8 Blinding (`:4824`). All three analysed attempts are completed. B5-3 adds a new pre-release reader of restricted paths. B5-2 replaces the "results cold gate" that §8 names as a reader. Both are §8 changes for completed attempts. The erratum also cannot be called "prospective", because the definition at `:566-567` says "before the bytes it governs exist", and the block-5 bytes already exist.
   - Fix: keep the recompute after the release, as RUN_STATE item 37 already decided ("computed after the release by the independent recompute"; "run beside L9 at the release"). Then B5-3 can be dropped.
   - For B5-2, make the step-12 executing seat meet the cold-gate definition at `:562-565` (no prior involvement), so §8's named reader stays the same.
   - Or put the §10 override to Ed explicitly, labelled not prospective.

2. **The s5-p2 science question is decided without the council or Ed.** The a46602ae RECORD (lines 12-13) says s5-p2 "is held until the thermal ruling passes its gate". Round-2 council questions Q2 and Q3 (s5-p1's labelled alternative and s5-p2's options) are still open (RECORD:11). Yet BY-3 ranks s5-p2 second, and BY-4 says "Collection for s5-p2 is unchanged". That answers the council's open questions and lifts the hold silently.
   - Fix: wait for round 2, then put BY-4 and the s5-p2 hold to Ed.

3. **Addendum 10's blinding statement is unverified and probably wrong.** M1 ran the harvest readers on s5-p1, Llama-70B, a held-out model. It read request-relative timing: episodes 10-35 s long, a post-request tail of 22.9-23.9 s over 50 members (RECORD:8). BYTES §11 item 2 bans clocks on rows before stage 1 because timing reveals a held-out module's duration (`bytes_pack_v1.md:347`), and decode time is one of the rival hypotheses.
   - Fix: disclose M1 in the addendum. Check whether any per-request duration of a held-out model was seen. State that BY-4 was motivated by structure seen on a held-out model.

4. **The evidence for transfer condition 2 is contaminated, and the synthesis rewrites the fallback.** `BLOCK5-TRANSFER.md:62-64` and RUN_STATE item 79 require the run "alone". The synthesis admits that load from its own segment agents and the auditor (2.76-5) ran beside it. L9-2 measured that the firing tracks contention: about 5.6 times slower than the reference in isolation (`l9:.codex-report/L9-2.md:11-14`). The file says that if the deadline fires, the dry run stays on the Mac. The synthesis changes this to "rerun alone" without Ed. Its timings also cannot measure N1's saving. The Air is fanless, so throttling under multi-hour load is not tested (INFERRED).
   - Fix: a pass under load counts. A firing triggers the file's fallback unless Ed amends it. Run no agents on the Air during that run. Measure the cache saving on a separate run in Codex Cloud.

5. **The Air is planned as both the quiet analysis host and the agent host.** §4 puts Ed's interactive Claude and Codex, fallback Sol seats, the login relay, the replay harness and N12 on the Air. That contradicts ED2(c) and gate policy 9 ("one heavy job per host"), and contention is what fires the 120 s deadline.
   - Fix: write a quiet-Air protocol for every real run: no agent processes, AC power, `caffeinate`, Spotlight off. Move interactive work to the cloud during those runs.

6. **The custody design on the Air does not hold together.** iCloud tars arrive under `edr`'s `~/Library/Mobile Documents`, which any agent running as `edr` can read. ED2(b) wants "same absolute paths (your user is edr on both)", but ED2(d) wants a folder readable only by a separate account. The synthesis never says who launches the dry run under the non-agent account (INFERRED: Ed by hand).
   - Fix: encrypt the tars with a key only the analysis account holds, or move them by an SSD connected only at a desk. Pick a data root that both requirements allow, and check which absolute roots the S11 index and bindings actually name. Name the launcher.

7. **There is an unexamined contamination path through iCloud on the measurement Mac.** The upload of `JouleWise-transfer` continues on its own after the desk ends, into PRECHECK and SESSION_RUN. The census matches only `[c]odex|[c]laude` (`bytes:joulewise/hazards/arm.py:65-70`). RUN_STATE item 79 also notes that iCloud folders mirror to every signed-in Mac, so files placed there from the Air would download onto the measurement Mac.
   - Fix: confirm the upload has finished before releasing the loop hold, or use the SSD route. Add an iCloud-activity check to PRECHECK (INFERRED tooling).

8. **Nobody checked disk space.** Uncompressed data is about 43 GiB per session (`analysis_cadence_plan.md:15`). Block 5's three windows, plus BETA a1/a4/a5 (which ED2 adds), plus two custody roots for B5-1, plus the tars, plus the iCloud local copies, may not fit in the 198 GiB free. Block 6 (9 sessions) plus block-5 bytes for S-16 cannot fit at all, so "optionally block 6 on the Air" and B6-6 have no basis.
   - Fix: total the sizes from the harvest manifests (structure only) before GO. Drop the Air as the block-6 host unless digest-checked `.zst` streaming is built.

9. **"No agent on the Mac, ever" contradicts the Mac's own task list.** Gate policy 10 says no agent process ever, and the bottom line says this "costs no code". But §4 assigns to the Mac:
   - BYTES stages 1 and 2, including committing `predictions.json` and attributing held-out agreement differences;
   - the known-bytes hour;
   - R3 desk reruns;
   - packaging;
   - block-6 runs.

   The pull-model watchdog that would run scripts from a git ref is not built. It would also be a new remote code-execution path on the measurement Mac.
   - Fix: scope the ban to "while any `collection.active` exists", which is the `~/.zshrc` guard's condition. Name who runs each Mac step, and cost the scripts.

10. **L1 conflicts with a registered retry rule.** `bytes_pack_v1.md:107` says "a lost BYTES attempt retries in the next BYTES slot (R6)". RECORD a46602ae:13 records that the s6-p1 retry arms next.
    - Fix: put the s1-p1-first order into the blind addendum, or keep the registered order. A lead ruling is not enough.

11. **BY-2 skips a registered precondition, and Addendum 10's authority is undefined.**
    - `bytes_pack_v1.md:384` says "Pass-2 versions remain null pending their agreement". BY-2 binds `18582818…` without showing that a pass-2 agreement run exists. Fix: cite one, or rerun it in the cloud.
    - "Addendum 10" clashes with the design ruling's Addenda 1-9, which the Authority paragraph ranks (`:14`). The new addendum has no rank there. Fix: rename it and give its rank.
    - The registration states no procedure for changes after its cold gate. Fix: ask Ed to authorise lead-made items 2-4.

12. **B5-4's tolerance conflicts with the bars already coded in the recompute.** Commit 7e322b76 sets 1e-6 relative for J and W, 1e-6 absolute for rho, exact counts, and a 1.24e-4 J gross-meter bar. B5-4 sets 1 mJ per phase plus half a unit of the last printed digit. The N6 comparator cannot implement both.
    - Fix: settle one set of bars in the amendment itself.

13. **B5-1's replacement check does not exist in code.** The only coded digest comparison is release mode's `release_digest_differs_from_dry_run` (ED-RULING:23-24). No tool compares two blind custody roots, and nothing enforces that "the lead reads only digest-verified outputs".
    - Fix: build and test a root-to-root comparator before the amendment is adopted, or keep the release-mode rerun.

14. **N3's status is misstated.** `ED-RULING.md:65-67` names seat L9-2 and says that if it cannot confirm, "this choice returns to Ed before the dry run". L9-2 reported NEEDS_RULING (`L9-2.md:9`). The condition covers a kept unit, the lost-reference list and a printed number, but N3 asserts only "refusal, never a dropped survivor".
    - Fix: match N3's asserts to all three items, record the condition as pending, and tell Ed.

15. **The estimates have no basis.**
    - The slot count does not subtract the packaging holds, which the transfer file lets run across several desks (`:21-24`).
    - The 10.5 h cycle has not been measured for pass 2, where every session smokes.
    - "Saves one slot" for ED2 is not net of packaging.
    - A 1-2 day L9 review stage assumes much less than #416's 7 rounds.
    - The block-6 dates ignore that BY-1 can keep the Mac collecting until 11-05, and ignore the Air's disk.
    - Fix: give ranges with explicit dependencies.

16. **The timeline breaks the transfer file, and parallel work was missed.**
    - §5 schedules packaging for 10-28/29, before GO on 10-29/30. `BLOCK5-TRANSFER.md:8-9` forbids any action under the file before GO. Fix: ask Ed to permit hash-only packaging before GO, or move it after GO.
    - Missed: run the same cached full-size test in Codex Cloud in parallel. That gives a clean acceptance result and a cache-saving measurement, and its outputs can be used to build and test B5-1's comparison and N6 now.

17. **N12 runs on the wrong machine.** BYTES stages run on the Mac (§4), so headroom measured on the Air against 120 s does not transfer.
    - Fix: time it on the Mac at a quiet desk or after collection.

18. **A bottom-line claim is not backed.** "No lone cold judge caught a W-class defect" sits beside RUN_STATE item 69, where Fable's single-family cold delta pass REFUSED a silently dropped reference. The synthesis's own rejected table also credits single-seat catches (Astra: A3, A4, C18). The claim mixes up "cold" and "executing", and it is used to justify B5-2.
    - Fix: restate it narrowly.

19. **Block-6 branch constraints are left out.** Block-6 registration §7 says "Nothing of block 6 merges into main before block 5's release", and #502 is held the same way (scout:27).
    - Fix: state that the L3/N9 integration and the S-14 pin stay on an integration branch.

20. **Low-priority items:**
    - L14 edits Ed's binding ruling text. Annotate it instead.
    - ED3's dropping of `test_docs_freshness` saves nothing; 6/6 short modules already pass (`L9-2.md:19`).
    - ED4 should cite RUN_STATE item 37(ii), which already ruled "no separate cold gate" on 2026-10-14.
    - N10 may duplicate a block-6 recompute seat that was "left to 015ASG1T" (RECORD a46602ae:13). Check before launching.