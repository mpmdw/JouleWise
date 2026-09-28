REFUTER: DISSENT

# Contract refuter (Opus 5.5): D-138 issuing transaction, epoch 25G83

- Candidate: `feat/2026-09-27-d138-25g83-issuance` at `325d9f77`, read-only worktree `/Users/edr/code/JouleWise-wt-d138-final-d528efb2`. No repository file was modified and no git write was made. Mutation runs used a `git archive 325d9f77` export at `/tmp/d138-contract-refuter/tree`.
- Spec: D138-25G83-DESIGN-01 §9 step 6 "Contract" charge, plus §4 (loader repair), §5 (promotion tool), §6 (pin swap), the issued file, D-185 and the issuing record.
- Probes, all run with `/opt/homebrew/bin/python3 -B`, with output saved beside each script: `probe_auth.py/.out`, `probe_table.py/.out`, `probe_promote.py/.out`, `probe_default.py/.out`, `mutate.py/.out`.
- Targeted suites on the export: `test_calibration_dispositions`, `test_promote_calibration_candidate`, `test_floor_mint_pinsets_schema`, `test_epoch_equivalence_check`, `test_acc_25g83_rev5` and `test_calibration_bracketing` ran 150 tests: OK, 1 skip. H-T1, H-T2 and H-T3 ran 3 tests: OK.
- Limit: the shell tool stopped answering (the classifier gave no verdict) before I could run the combined M3+M6 mutation and the path count against main. Both are marked "not executed" where they are used.

## Verdict in one paragraph

The authentication is sound. No file other than the committed bytes loads under the new identifier. The table and the disposition file cannot drift apart without test D1 failing. The promotion tool reproduces the pinned bytes. The three named R7 freezes hold under mutation.

I dissent on one point, the hold. The issued file is used by every consumer that reads the default. That includes consumers acting for packs that declare R7 or r6. H1, however, is enforced only against packs that *declare* the new identifier. Before this change, the thing that stopped claim-bearing windows at 25G83 was the default's epoch mismatch. The merge removes that barrier for every pack, and H1 replaces it for only some of them. Under ruling §9 step 6, a route of this kind stops the transaction until it is closed. The Hold refuter should confirm the route end to end (B1).

## BLOCKER

### B1. H1 is checked against the pack's declared calibration, but windows are judged by the default. At 25G83 the held file judges windows run from packs that declare R7 or r6.

**Code.**
- `joulewise/arm_readiness.py:6191-6224`: `_issued_d079` admits a pack by the acceptance id the pack *declares*, and refuses only the held id.
- At run time the file that judges a window is the global default, not the declared one:
  - The capture preflight is `scripts/validate_powermetrics_fiducial.py:381-385`. `DEFAULT_ACCEPTANCE_BOUND_PATH` is used when no path is given, and the ordinary capture call at `:2133-2136` gives none.
  - The bracket evaluation is `joulewise/calibration_bracketing.py:2072-2076`: `load_calibration_acceptance_bound()` when `acceptance_bound is None`. A grep for `acceptance_bound=` over `joulewise/` and `scripts/` finds **zero** production callers that pass one.
- A window run from a pack that declares R7 is therefore an "R7 consumer still reading the default". This is the third clause of the contract charge.

**Executed (`probe_default.out`).**
- All nine committed packs declare an older generation (n19, n19_r2 or r6), and `_issued_d079` returns True for each.
- A synthetic policy naming R7 returns True in all three policy shapes. The same policy naming the new identifier returns False.
- Capture preflight for a 25G83 identity:
  - At the head it returns the level screen `0.038078579302948`, taken from the held file.
  - With the default patched back to R7 (main's behaviour) it refuses: `acceptance_artifact_epoch_mismatch ['os_build']`.
  - That refusal was the barrier to every 25G83 capture window before the merge.
- `acceptance_judged_epochs`: the new file judges only `25G83`, and R7 judges only `25F84`.
- Evaluation freshness compares the window's identity with the epochs of the default (`:2150-2167`). A 25G83 window run from an R7 pack is therefore evaluated "fresh" by the held file, with `claim_eligible: True` (`:2170-2178`).

**What I did not trace.** I did not check whether another gate independently refuses such a window at arm, capture or mint. Candidates are:
- the stack-identity receipts of `identity_pins.py`;
- the pinset constant `max(observed_drift_s,0.009724)` of R7/r6 packs against the evaluated screen `0.013701`;
- the mint-time `issued_calibration_allowance_projection`.

The ruling left exactly this trace to the Hold refuter (§7.3 "Not verified by me"). If that trace finds a gate that refuses, B1 falls to SHOULD-FIX: the records overstate the hold. If it finds none, B1 stands as a stop.

**The records claim the opposite.**
- `docs/decision_log.md:12245` says "so no pack naming it can arm". That is true, but it is the wrong property.
- `docs/decision_log.md:12263` says "while H1 keeps any claim off this file". That is false as built.
- Issuing record §4.4 (line 93) has the same framing.

**Cure options, for the lead (not prescribed).**
1. Enforce the hold where the file is consumed: `evaluate_calibration_bracket` and the capture preflight refuse, or set `claim_eligible` False, when the loaded artifact's id is held. This needs the held set in a module both can import.
2. At arm, refuse a claim-bearing pack whose declared acceptance id is not `ACTIVE_ACCEPTANCE_ID`. The file a pack declares must be the file that will judge it.

Either cure needs a counterfactual test: a pack or window declaring R7 at a 25G83 identity must be refused, and it must be admitted when the hold set is emptied.

## SHOULD-FIX

### S1. "Windows that run without a pack are not affected" is false. At 25G83 the no-pack derivation-night class is closed, and no-claim captures are now screened by the held file.

**Where the claim is made.**
- `docs/decision_log.md:12261`.
- Issuing record §4.4 "Known cost".
- Ruling §7.3, which says the class W1 and W2 ran under "is not affected".

**Why it is false after the move.**
- `scripts/write_derivation_night_inputs.py:181-187` refuses a 25G83 machine: "this is an ORDINARY night, not a derivation night". It does this with its default `--acceptance`, `:279-290`.
- The writer's `--derivation-only` refuses `DERIVATION_ONLY_EPOCH_UNCHANGED` (`validate_powermetrics_fiducial.py:2094`).
- The branch's own re-point of `tests/test_validate_powermetrics_fiducial_derivation_only.py` asserts both refusals. It moves the "matching" epoch to 25G83 and the "differing" epoch to 25F84.

**Consequence.** Any no-claim 25G83 capture window must now take the ordinary path. That includes H2's route-R evidence captures and H7's first network-time-OFF comparison. On that path every capture is level-screened by the held file (`0.038078579302948`, `probe_default.out` PF head). The file under test judges the captures meant to test it.

**Cure.** This may well be acceptable. The records should state it, and the H2/H7 lanes should be designed knowing it.

**Also not in the §6.4 census of consumers that "move with the default".** Each moves with the default, and none means R7:
- `scripts/generate_g2a_probe_inputs.py:660,667,844-847`;
- `scripts/reissue_calibration_acceptance.py:309,557`;
- `scripts/validate_powermetrics_fiducial.py:541-545,941-945`, and the module constant `PREFLIGHT_SYSTEMATIC_SCREEN_S`, now `0.038078579302948`.

### S2. The promotion tool checks the cited digests and the network-time block only for form. The file and the rulings it cites could disagree without detection.

`scripts/promote_calibration_candidate.py:73-84` checks only that each ruling digest is well-formed hex and that `network_time_provenance.disclosure_id == "D8"`.

**Executed (`probe_promote.out`).** Each of the following issuance texts was **ACCEPTED**:

| Probe | Change to the issuance text |
|---|---|
| P4a | a wrong but well-formed ruling digest (`f`×64) |
| P4b | a ruling path to a file that does not exist |
| P4c | the D8 text replaced by `"x"` |
| P4d | `network_time_provenance.text` different from D8 |
| P4e | `claim_eligible_meaning` and `hold_enforcement` removed |
| P4f | a wrong `source_candidate.relative_path` |

**The committed bytes are correct.** Executed:
- all four ruling digests equal the files at their `relative_path`;
- `source_candidate` equals `dbad7cc7…` / `fac6e6f8…`;
- `network_time_provenance.text == D8`;
- the preserved `timed` log's plain-text sha256 equals `2f9bf739…0b5c`.

Nothing in the code or tests would catch drift on a regeneration. The tool is designed to be re-run for a D9 or a re-issue, and a regenerated file with drifted citations would carry them into the pinned bytes.

**Cure.** Have the tool hash `ROOT/relative_path` for `rulings`, `network_time_provenance.source_rulings` and `preserved_log` (decompressing the log). Require `ntp.text` to equal D8's text, and require `claim_eligible_meaning` to equal the ruling's §7.4 sentence. Add a test P6.

### S3. The issued bytes assert a gate that is still open, and omit A3.

`configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json:856` has `backfill_candidate.required_verification` = "complete: … addenda A1 and A2; design ruling D138-25G83-DESIGN-01 and the gate of its section 9".

- The §9 gate is not complete. This refutation, the Hold refuter, the pedagogy pass, the cold final pass, and the §10 item 2 disposition are all still open.
- The sentence names A1 and A2 only, while `issuance.reason` names A3.

A claim-bearing file should not state a gate as passed before it passes. Because the text can change before merge, the cure costs nothing: re-word it to what was complete when the bytes were written, and name A3. This changes digest X, which is expected before merge.

## NIT

- **N1. Rules (b) and (f) cannot currently be observed** (`calibration_bracketing.py:1023-1024,1081-1082`). Executed mutations (`mutate.out`):
  - M3 drops (b): survives L3/L4.
  - M5 drops (f): survives the whole dispositions suite.
  - M6 uses the whole table instead of the declared decisions: survives, because (b) masks it.

  With one decision in the table, (b) is implied by (a), (c) and the refusal at `:1044`. (f) is implied by the completeness equality. The ruling's L4, "catches ignoring the declaration", holds only for the *combined* mutation M3+M6. My reasoning, not executed: declaration `[]` then skips all eleven rows, the file validates, and L4 fails. The §9 step 5 mutation record should say this.

  Cure: a test that patches a second decision into the table makes (b) observable. (f) can be kept as defence in depth or deleted.
- **N2. The ruled STOP on the input seal is never reached by a test.** Removing it (M7) passes the whole promotion suite. Probe P3c shows why. The candidate digest pin, the candidate's own seals, and the issuance text's `source_candidate.derivation_sha256` always refuse first. The stop guards only a future transform bug, and the PROTECTED comparison also covers that.
- **N3. The loader does not notice some table drift.** Executed: adding a 25F84 valid prior-row id to the code table leaves the issued file loading (V3 True); only test D1 catches it. A later decision disposing *any* row of this 86-row prior set makes the issued file stop loading (V5 False). That failure is closed, as it should be, but D-185's revisit trigger names only "a new disposition decision touching 25G83 rows".
- **N4. The table-equality check can be skipped.** `parse_disposition_registry` checks equality with the table only when `expected_sha256` equals the module constant. A caller-supplied digest, or a patched `issuer.DISPOSITION_REGISTRY_SHA256`, parses a 10-row edited file without the table check (T3/T3b). This is intended for tests; worth a comment.
- **N5. L9 guards less than the ruling asks.** It guards only `Path.read_bytes`, and only for the seven old files. My probe A11 guarded `open`, `os.open` and `Path.read_bytes`, loaded the **new** file, and saw zero reads of the disposition file. That closes it; the test could say so.
- **N6. The block shape differs from the ruling's sketch.** The keys of `network_time_provenance` differ from ruling §7.2's sketch: there is no `state` key, and `source_rulings` is plural, among others. This is presumably by addendum A3, but the issuing record does not note the deviation.
- **N7. The tool's self-check is circular.** Its protected-path check compares objects that are the same references. The real guard is `_parse(raw) == issued` plus test P2 run on the committed file.

## Executed evidence confirming the contract (no finding)

- **Authentication (`probe_auth.out`).**
  - The file digest equals the pin, `80c23036…351b`. The default loads the new id, and R7 loads by path.
  - A byte-identical copy at another path loads, as designed.
  - Each of these is refused:
    - a trailing space;
    - re-serialization;
    - a member value altered and both seals recomputed;
    - D8 and the holds dropped and resealed;
    - R7's content relabelled as the new id;
    - the candidate `dbad7cc7`;
    - the new content relabelled as R7;
    - an in-memory dict with one extra note.
  - With the pin swapped to the tampered digest, the validator alone still refuses the altered member. It accepts the dropped disclosures (A6b), so the pin is the only guard on disclosure text, as ruling V6 says.
- **Disposition file (`probe_table.out`).**
  - The file digest equals the pin `ba1ba3fc…`, and its parse equals the table.
  - If the file is edited and the pin left, it refuses. If the file and module pin are edited but the table is not, it refuses ("table mismatch"). An edited mechanism sentence is refused.
  - Loader against the table: dropping an id refuses; adding an id absent from the prior set refuses; adding an invalid W1 row refuses.
  - Counts: 86 rows / 53 valid = 30 earlier + 12 members + 11 disposed, and `excluded_members` is empty. This matches the issuing record and D-185. Ruling §4.1's "1 named exclusion" was wrong, and the record correctly says so.
- **Tool (`probe_promote.out`).**
  - `--check` gives rc 0 on the committed file and rc 1 on a one-byte change. `--out` will not overwrite different bytes.
  - Each of these is refused: an altered member (digest); the same with the digest patched (seal); a non-candidate role.
  - The line diff removes exactly 10 lines, all on the §5.5 list. The file has no byte above 127.
  - The whole-file seal is `8477d8ce…`, and the candidate's `fac6e6f8…` is carried in `source_candidate`.
- **Mutations killed.**
  - Dropping (d) is caught by L6 and L7, and dropping (c) by L5.
  - Skipping by session name instead of identifier is caught by L2.
  - Dropping the candidate's own seal check is caught by P3.
  - Un-freezing R7 is caught at all three sites (equivalence default, sim, issuer check and default).
  - Dropping the H1 set is caught by H-T1, and loosening the schema's 25G83 screen by the schema test.
