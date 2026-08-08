# Fable pre-execution examination — U5–U7 pack plan (DRAFT-U5U7.md)

Examiner: fresh Fable instance, D-118 gate. Repo examined at main `7778260`.
Plan block: `docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md` lines 23739–24647
(the block after the final `tokens used` marker).

## VERDICT: ACCEPT-WITH-AMENDMENTS

The plan's re-derivation discipline is genuinely excellent — every oracle I
sampled reproduced against landed bytes, including hashes of files that do not
exist yet. Its defects are all in what it is SILENT about: the mint bar, U2's
absence, the U8 interlock, and the arm-time identity pins. None require
redesign; all are paste-ready amendments. Executing the plan as written would
produce packs that are byte-sound but embedded in an execution order that
quietly assumes two barred/unbuilt dependencies resolve themselves.

---

## 1. Would the packs actually arm? (§5A walk)

Mostly yes, for alpha/beta — with named gaps. The pack supplies plan bytes,
IDs, hashes, stage graph, policy pins, and attachment SLOTS; U1's reserve
script (`scripts/reserve_calibration_window_bracket.py`, exists) supplies
session/attempt identity at arm; the readiness record schema
(`joulewise.frozen_plan_readiness.v1`) is chartered in the separate
PLAN-U8-extracted.md, not here — consistent, but see A6.

Fields the operator or validator needs that NOTHING in this plan (or any
chartered unit) produces:

1. **Per-stage launch-command representation.** PLAN-U8-extracted.md §2
   dependency 3 requires U5–U7 to freeze "a common plan-tree and
   launch-command representation" and instructs U8 to stop with NEEDS_SCOPE
   if absent. The plan's `plan_tree.json` contract (§3) has `stage_graph`
   with kind/ordinal/counts/links but NO runner invocation fields (entrypoint,
   args, absolute-runs-root placeholder, policy path). As written, U8 is
   contractually obligated to refuse these trees. This is the one hard
   inter-plan contradiction.
2. **Projected `runtime_identity_sha256`.** The mint derives it from members
   post-hoc (`_source_regime` → stack-identity hash,
   mint_floor_artifact_generalized.py:2049 refuses on mismatch). The readiness
   record must carry the projection at arm, but no unit charters the tool that
   computes it desk-side from pack configs + installed environment. A wrong
   projection is discovered only at morning mint, when re-declaring pins would
   violate declared-before-collection — good night data, unmintable floors.
3. **`model_artifact_sha256` computation procedure** — operator-supplied in
   the readiness record; the runbook step ("hash these files with this
   command") is nowhere specified.
4. **U2 registry proof** — required by §7 pre-arm; U2 does not exist on main
   (`scripts/build_calibration_acceptance_successor.py`,
   `configs/calibration/calibration_acceptance_registry.json`,
   `tests/test_calibration_acceptance_successor.py`: all absent).
5. **Reason-code mapping** — PLAN-U8 dependency 4 requires it resolved before
   U8 lands; the findings register calls it URGENT; this plan's §9 never
   mentions it.

Everything else checks out: run_campaign takes `--runs-dir` from CLI (configs
do not embed roots — R6 mitigation holds), `load_order_entries`
(run_campaign.py:2475) consumes `executed_order` as claimed and tolerates the
added `config_sha256`, NEG8/reference stages are runnable against their own
pinned external manifests, and the bound/reference/calibration counts
(12/7/2) match the memo.

## 2. Memo-literal staleness — independent re-derivation of the sample

All sampled claims verified against landed code; the plan corrected the memo
where the memo was stale:

| Oracle | Memo said | Plan says | Landed truth |
|---|---|---|---|
| Receipts per session | 3 | **5** | `_PRODUCTION_RECEIPTS_PER_SESSION = 5` (test_calibration_live_three_window.py:66); three receipt kinds in calibration_ledger.py:47–49, claim+finalization ×2 slots |
| Terminal sequence | 85 | **91**, derived not literal | `_EXPECTED_TERMINAL_SEQUENCE = 76 + 3×5 = 91` (test:64–69) — plan right, and right to forbid the literal in pack bytes |
| Extraction relationship | 100 refs / 50 unique | same, PLUS the landed `_validate_order` defect | Verified: `_spec_member_ids` (mint_floor_artifact.py:578) extends across cells → 100 ids; `_order_manifest_ids` (:795) rejects duplicate run_ids; `_validate_order` (:807) compares `len(ordered) != len(spec_ids)` → the four-cell shared-bundle spec CANNOT pass today. Repair location correct (v1 core; the generalized script loads it via `_ORIGINAL_MINT_PATH` and calls `core.mint_floor_artifact`). The generalized script's core pin is SIGNATURE-only (lines 100–131), so the internal repair does not break the pin. |
| Identifier scheme | memo table | identical | matches |
| Binding fields (§1.3) | — | 12 keys + 3 endpoint keys | exact match to `_BRACKET_BINDING_KEYS` / `_BRACKET_ENDPOINT_KEYS` (calibration_bracketing.py:511–529) |
| Producer/role pairing (§1.4) | — | 2 producers, roles exactly {decode,prefill} | verified (generalized:609, :854–855, :3081–3083) |

External pins recomputed byte-for-byte, ALL MATCH: policy `b0d7b228…`, NEG8
manifest `0ec9d68a…`, start/mid/end reference manifests, issued acceptance
`31611396…`, ledger head file `6bbe2625…` (sequence 76, head `08456d50…`),
all four template condition-family byte SHAs, and — computed via
`canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, …)` — all four claimed
domain SHAs.

**Strongest determinism evidence:** I reconstructed both prefill rider
families from the plan's field sketch (decode family JSON with only
`condition_family_id` and `measurement_target.metric` changed, two-space
indent + trailing newline) and got the plan's expected byte SHAs AND domain
SHAs exactly (`985a4e53…`/`974014e0…` and `e896aeae…`/`b9568867…`). The
plan-factory really computed its oracles.

Two nits it missed: (a) the "established top-level shape" of
`order_manifest.json` in p2_015 also carries `unavailable_gap` — state whether
new manifests include it; (b) window_id == plan_id is a plan convention, not
landed enforcement (reserve script takes `--window-id` free-form) — U8 must
enforce the equality, and §7 should say so explicitly.

## 3. Ordering and dependency realism

- **U5 → U6 forced?** Yes as drafted: U5 owns the shared v1-core order repair
  and its regression file; U6's full-suite run needs it landed. Sound.
- **U7** genuinely independent once this plan's vocabulary is ratified —
  could run parallel to U6; the plan's serial ordering is merely conservative.
- **No desk-time deadlock.** Pack generation touches neither U2 nor mint
  issuance. The mint BAR is on issuing artifacts, not editing mint code, so
  U5's order repair is permissible — but the plan NEVER MENTIONS THE BAR,
  and §9 steps 6–7 ("U10 mints… gamma binds") silently assume the bar lifts.
  The bar lifts only after the escalation consult's adopted shape (a real
  producer for `floor_mint_postcollection`) lands plus a fresh delta. That
  chain is not in the execution order, and U5's mint-core edit may need
  rebasing under the consult's adopted shape.
- **U2 absent from §9 entirely** despite being a memo F3 BLOCKER before any
  arm and a PLAN-U8 hard dependency. The order as written reads as if packs →
  U8 → nights, which is false.
- **U1 debt:** the apex gate (commit 0d3fee7) requires F1 (writer-retry-path
  false refusal — literally a strand-a-night defect) and F2 closed before
  night 1. Also absent from §9.

## 4. The prefill rider

**The condition-family definition achieves same-bundles/no-added-members, and
landed U3 accepts it.** Verified mechanically:

- Rider keeps `workload_profile.name = "df_ph_decode"`, 128/512, 1 rep/1
  warmup — identical physical execution; only family ID and metric differ.
- Extraction duplicate rejection is per-cell (`_unique_bundle_ids`, called
  inside per-cell extraction; floor_extraction.py:1256) — cross-cell sharing
  is legal.
- The generalized pinset builds `component_member_universe` as a SET across
  a producer's decode+prefill cells and checks it equals
  `extraction_spec.member_count` (=50) — union semantics, shared members
  expected (generalized:843–862).
- Role pairing requires exactly {decode, prefill} per producer with
  `phase_energy_j.<role>` and `["phase", role]` — the plan's table matches.
- The one landed obstruction is exactly the `_validate_order` 100-vs-50
  defect the plan repairs in U5.

**Residual rider risk the plan dropped:** the memo's lead-check list required
verifying that the fifty bundles actually CONTAIN a prefill phase.
`phase_energy_j` is an open dict keyed by recorded phases (reduce.py:2953);
nothing in this plan proves desk-side that `df_ph_decode` bundles carry
`phase_energy_j.prefill` on the current harness. Cheap to verify against
historical P2-015 bundles before freeze; fatal-after-the-night if wrong
(both nights' prefill floors, half the rider's purpose).

## 5. What would strand a night — ranked

1. **Gamma night scheduled before the mint-bar chain completes** (consult
   closure → postcollection producer lands → delta re-audit → U10 mints →
   gamma readiness binds the SHA). U8 will correctly refuse to arm gamma
   without the artifact SHA. If the three nights are consecutive, night 3 is
   near-certain to slip — or worse, generate pressure to improvise around the
   bar. Highest probability, structural.
2. **Morning-refused floor data from wrong arm-time identity pins.**
   `runtime_identity_sha256` / `model_artifact_sha256` / `config_set_sha256`
   are composed into requirement bytes at arm by U8 from attachments no tool
   is chartered to compute. Mint refuses on mismatch; pins cannot honestly be
   re-declared post-collection. A whole floor night collected clean and
   permanently unmintable. Medium probability, worst consequence-per-defect.
3. **Pre-bookend acceptance trigger with U2 unbuilt.** A range-expanding pre
   observation forces abort before member one (correct per policy), and
   without U2 there is no successor path to save the night — plus L4's
   copied-scalar screen means the trigger might not even be detected until
   the morning verdict, which is the true stranded case: science ran all
   night, verdict refuses. Medium-low probability per night, three draws.
4. (Named for completeness) missing prefill phase in bundles — loses the
   prefill half of both floor nights, decode floors survive; U1 F1 false
   refusal at the writer's retry path; R7 operator killing a >2-min verdict.

## Numbered paste-ready amendments

1. **§9 (execution order) — insert the barred-mint precondition.** Add after
   step 5: "U10 may not run while the v2 mint is BARRED
   (ESCALATION-U3-AUTHENTICATION.md). Precondition for step 6: the
   postcollection-producer consult's adopted shape has landed, a fresh delta
   re-audit accepted it, and the bar is explicitly lifted on main. Gamma's
   night must not be scheduled until this chain plus U10 has completed."
2. **§9 — insert U2 and U1-debt rows.** Add: "No window arms until (a) U1
   findings F1/F2 (apex gate, commit 0d3fee7) are closed; (b) U2 lands and
   passes its cold gate (memo F3 blocker; PLAN-U8 dependency 2); (c) the
   reason-code unit is resolved (PLAN-U8 dependency 4). Pack GENERATION
   (U5–U7) is independent of all three and proceeds first."
3. **§3 (`plan_tree.json`) — add a launch representation.** Extend
   `stage_graph` rows with an exact invocation record: runner entrypoint,
   frozen argument list with named placeholders for the absolute runs root
   and policy path, and the config-dir the stage manifest governs. Without
   this U8 must refuse the trees per its own plan (NEEDS_SCOPE).
4. **§7 (pre-arm) — charter the identity-projection procedure.** Specify that
   the readiness flow computes projected `runtime_identity_sha256` by running
   the SAME stack-identity derivation the mint uses
   (`joulewise.detection_floor` stack identity + `canonical_domain_sha256`)
   over the pack configs and installed environment, and `config_set_sha256`
   via `scientific_config_identity()` on any one member config (all 50 share
   one identity by construction); name the command the operator runs for
   `model_artifact_sha256`. Assign the ~30 lines to U8 (or a named helper in
   U5's generator) so it is in SOMEONE's WRITE_SCOPE.
5. **§4/§5 (U5/U6 test obligations) — add the prefill-phase desk proof.**
   "Verify against at least one historical P2-015 bundle (and one 7B floor
   bundle) that `phase_energy_j.prefill` is present and nonzero for
   `df_ph_decode`-workload bundles on the current harness; a missing phase is
   a freeze blocker, not a night discovery."
6. **§7 — subordinate to PLAN-U8.** Add one line: "PLAN-U8-extracted.md is
   the authoritative U8 contract; this section is a consumer summary. On any
   divergence, PLAN-U8 governs." (Prevents the two documents drifting into
   contradictory validator expectations.) Also state U8 enforces
   `window_id == plan_id` — the landed reserve script does not.
7. **§1.5/U5 — record bar-compatibility of the mint edit.** "The
   `_validate_order` repair changes no pinned signature (the generalized
   script pins signatures only) and does not enable issuance; the mint
   remains BARRED. If the postcollection consult's adopted shape lands after
   U5, a delta re-audit of the combined mint surface is mandatory."
8. **§3 (`order_manifest.json`) — state the `unavailable_gap` disposition**
   (p2_015's root manifest carries it; new manifests should either omit it
   deliberately or include it empty — pick one so U8's exact-shape check has
   an oracle).

## Before or after the U2 cold gate and mint un-barring?

**Generate the packs BEFORE both — deliberately.** The pack bytes depend on
neither: the acceptance policy is correctly frozen at the semantic level
(issued artifact + "authenticated D-102 descendant selected before member
one") without pinning U2 registry paths or schemas, and gamma's artifact SHA
is an arm attachment, not a plan literal — the plan got both firewalls right.
Desk generation is the parallelizable, night-independent work; serializing it
behind U2/consult closure buys nothing and costs calendar.

Two conditions on that judgment: (i) amendments 1–2 must land so nobody reads
frozen packs as armable packs — arming waits on U1-debt closure, U2's cold
gate, the reason-code unit, and (gamma only) the mint un-bar + U10; (ii) keep
U2's eventual registry semantics OUT of pack bytes (as drafted) so a U2
cold-gate surprise cannot force pack regeneration. If the postcollection
consult's adopted shape ends up restructuring extraction-spec or
producer-contract fields (possible but unlikely — its question is who WRITES
the postcollection block, not the desk shape), U5/U6 regeneration is cheap by
construction: the packs are generator-emitted, and that is precisely why the
generator-first design deserves the ACCEPT.
