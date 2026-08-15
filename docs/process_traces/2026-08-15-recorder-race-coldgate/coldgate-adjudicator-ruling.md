# COLD-GATE RULING — recorder check-to-grant race (adjudicator seat; verbatim custody)

Provenance: cold Fable instance, fresh session, no loop context; converted the packet's static
traces to EXECUTED evidence (E1-E5) in scratchpad exports of branch head eff85f8; repo untouched.
Relayed verbatim except this header. The paired Opus refuter's findings are custodied separately;
the composed license is recorded after both seats.

---

**Gate identity.** Cold Fable adjudicator, rule-11 mandatory trigger (second fix round, same defect class: aliasing of the governed extraction-spec grant). Packet: docs/process_traces/2026-08-15-recorder-race-coldgate/ (non-author assembly at repo head a2d4d04), reviewed branch impl/wo-margin-recorder-authz at eff85f8. Inputs beyond the packet: the live grant region at eff85f8; the full docs/contracts/calibration_ledger.md; joulewise/authentication_io.py.

**Executed evidence produced by this gate** (race_driver.py + exports head/, mutant/, proposal/, closure/):

- **E1 — the race, executed on the branch head.** Deterministic interposition wrapping allow_governed_extraction_spec so the ALPHA→symlink→BETA swap runs after every pre-grant check and before the grant's internal resolve (the maximal-power schedule; dominates all check-then-grant designs). Result at eff85f8: grant argument was ALPHA's canonical path, but the session's governed-vocabulary set registered BETA's canonical identity; BETA's bytes were read through the symlink and parsed UNDER THE EXEMPTION; refusal arrived only afterward as pack_pin_invalid. The delta re-audit's F1 is confirmed as executed fact; packet anomaly 2 discharged in the confirming direction.
- **E2 — the sandbox-blocked G1 mutation, executed.** Removing only the round-1 guard flips test_symlinked_spec_path_refuses_before_any_grant to a discriminating failure. The round-1 regression is live, not vacuous.
- **E3 — the round-2 proposal's step 2, executed under the race.** With the pre-grant O_NOFOLLOW fd-read + hash-vs-pin refusal installed verbatim, the race evidence is IDENTICAL to the unfixed head: BETA's identity still receives the grant, BETA's bytes still parse under the exemption, refusal still arrives afterward. Additionally the pre-bind BREAKS the existing regression test_tampered_selected_spec_refuses_before_census_processing (tampered-bytes refusal fires pre-grant; grant.assert_called_once_with observes zero calls) — an undeclared observable behavior change on a green attack line.
- **E4 — the redirect shape, executed under the same race.** With the governed spec read routed through the existing read_authentication_input_nofollow (dir_fd component walk O_NOFOLLOW|O_DIRECTORY per step; O_NOFOLLOW + fstat S_ISREG final), the identical schedule refuses authoritative_input_invalid via ELOOP AT THE READ, before any parse — BETA's bytes never read, never parsed, no read registered for BETA's identity. Full focused suite 34/34 OK, zero static-path behavior change.
- **E5 — grant-after-read impossibility, verified against the API.** allow_governed_extraction_spec raises RuntimeError when the identity is already in session records; an ungranted read refuses on the lexical ban. Grant-before-read is API-mandated; adoption clause 2 forbids changing authentication_io.py.

## (i) Threat model and severity — OUT of model; blocker REGRADED to should-fix

The race requires a concurrent local process with repo write access acting mid-execution on Ed's single-operator machine. The contract's own boundary (calibration_ledger.md, opening): the instrument "does not defend against a malicious trusted writer or an authority that rewrites both Git and the complete ledger history." A process that can win a sub-millisecond window holds repo write authority — at least a trusted writer — and a strictly stronger attack by the same adversary is already conceded out of scope by the instrument's own F2 analysis (self-consistent replacement of plan tree, sidecar, and spec = the D-120 single_authority limitation). Every F2 required-result row is a static shape. Blocker grading would also be incoherent with the surrounding code: the plan tree, sidecar, and GAMMA manifest reads carry identical TOCTOU exposure and were flagged by no round.

RULING: the race is OUTSIDE the documented threat model. The delta's finding is factually correct (E1) and its REJECT was procedurally legitimate, but blocker is REGRADED to should-fix; the closure lands as defense-in-depth. No merge is gated on the race itself.

## (ii) Closure soundness — proposal REJECTED; fd-identity alternative REJECTED; a simpler, stronger shape exists

The proposal's step 2 keeps the check-then-grant shape; the grant re-resolves internally at grant time, so a post-check swap still yields a BETA-identity grant — demonstrated (E3), and its marginal protection is zero (the existing post-read SHA refusal already protects consumption) while adding a second open/read (more TOCTOU surface) and breaking an existing regression. Its race analysis judges residual by consumption, quietly substituting a weaker invariant for the adjudicated one (clause 1: "never granted the other floor pack's spec"). The fd-identity alternative detects after the fact, cannot prevent the wrong-identity grant, and its unique catch (byte-identical content, different inode) is definitionally harmless under a content-pin contract.

The structurally correct closure exists in the contract's audited surface: route the governed spec read through read_authentication_input_nofollow. One call site changes; no authentication_io.py change; grant stays exactly-once/floor-branch/selected-path-only; post-read hash comparison retained. Under any raced schedule the exemption can never attach to the other pack's file AND be consumed: symlink at read time dies ELOOP before parse (E4); a regular-file content swap parses at ALPHA's identity only and is pin-refused — the F2 table's own in-contract row.

Accepted residual (recorded, not chased): a raced schedule can still momentarily register the other pack's resolved identity in the session-local vocabulary set before the read refuses. Inert — never consumed, no read registered, refusal terminal — and not closable without amending authentication_io (E5 + clause 2). Sits inside the trusted-writer exclusion.

## (iii) LICENSE round 2 — REDIRECTED to this exact specification

Code (joulewise/window_duration_margins.py, floor branch of _pack_inventory only):
1. Keep the round-1 resolution-invariance guard unchanged.
2. Do NOT implement the proposal's step 2. No pre-grant content read of any kind.
3. Replace the governed spec's _json_object read with: registry_raw = read_authentication_input_nofollow(repository_root, <pack-relative selected path>, grammar="json", label="pack-pinned extraction spec"); OSError → _refuse("authoritative_input_invalid", f"governed extraction-spec no-follow read failed: {exc}"); re-apply _json_object's decode/parse/Mapping normalization; the existing registry_sha != expected_sha → pack_pin_invalid refusal and everything downstream byte-identical.
4. GAMMA branch, plan-tree read, sidecar read OUT OF SCOPE (same exposure, same out-of-model adversary; widening not licensed).

Regression obligations (all four, same commit):
- R1. test_symlinked_spec_path_refuses_before_any_grant retained unchanged.
- R2 (new, race regression). Deterministic interposition per E1/E4: wrap allow_governed_extraction_spec to perform the swap before delegating. Assert: refusal authoritative_input_invalid with no-follow detail; _floor_cells never invoked; BETA's canonical identity ABSENT from authentication.records (the discriminator). Must NOT assert grant.assert_not_called() — the grant fires once with ALPHA's path; docstring names the inert raced-grant residual as accepted.
- R3 (new). Static parent-directory symlink regression (configs/floor_mint symlinked): authoritative_input_invalid, zero grant calls.
- R4 (bench mutations, EXECUTED before merge, at the FINAL round-2 head): (a) remove round-1 guard → R1 discriminating failure; (b) revert no-follow read to _json_object → R2 discriminating failure. Static prediction is not acceptance evidence. Full focused suite green (34 + 2 new) at the final head.

Bookkeeping bound into the landing: the decision-log round-2 entry records (a) the severity regrade with the threat-model basis, (b) the inert raced-grant residual as an accepted limitation, (c) that the pre-grant content-bind was adjudicated and rejected on executed evidence, so it does not return.

Packet integrity notes: anomalies 1/3/4 disposed (citations resolved against the live branch; G1 executed; full contract read). Anomaly 5: the embedded M-2 amendment played no part. Anomaly 6: SUPPLEMENT S1 was load-bearing for (i); the mechanic addition was proper. The non-author assembly was clean.

Per rule 11, the magistrate may overrule this verdict only with written dissent that Ed sees.
